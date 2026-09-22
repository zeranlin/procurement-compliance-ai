# 第三课 · 第 7 阶段：第一次建立完整“显存账本”
## 一张 GPU 到底能不能装下一个模型？为什么 Weight 明明放得下，Context 一长还是会 CUDA OOM？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Serving VRAM ≠ Weight VRAM。完整显存账本至少包括 Weights + KV Cache + Activations/Workspace + Runtime Overhead。**
2. **Context Length 增长会显著扩大 KV Cache；“模型刚加载成功”不代表长上下文时仍不会 OOM。**
3. **Batch / Concurrency 会让多个请求同时占用 KV Cache，因此单请求显存不能直接代表服务显存。**
4. **OOM 可能发生在生成过程中而不是加载阶段，所以显存预算必须覆盖真实 Workload Shape。**
5. **专业显存预算必须留 Headroom，不能把理论可用显存全部吃满。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `CUDA` | CUDA：NVIDIA GPU 通用并行计算平台与软件生态 |
| `KV Cache` | KV 缓存：生成时缓存历史 Key/Value 以减少重复计算 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Batch` | 批次：一次参与计算的一组样本 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `VRAM` | 显存：GPU 上存放权重、激活和 KV Cache 等的高速内存 |
| `BF16` | BF16：保留较大指数范围的 16 位浮点，常用于大模型 |
| `Attention` | 注意力：根据内容相关性动态聚合信息 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |
| `Query` | Query/Q：当前 Token 表示“我要找什么”的向量 |
| `Transformer` | Transformer：以注意力和前馈网络为核心的序列架构 |

### C. 建议阅读层级

```text
一级：核心心智模型    # 中文：先建立判断框架
↓
二级：关键公式 / 流程 / Schema    # 中文：理解系统怎样工作
↓
三级：政府采购案例与反例    # 中文：把抽象边界落到业务
↓
四级：编号细节与工程扩展    # 中文：按需要查阅，不要求一次全部记忆
```
<!-- PEDAGOGY_CN_ENHANCEMENT_V2 END -->

第 6 阶段我们已经学会了第一笔账：

```text
参数量
×
每个参数占多少 Bytes
≈
模型 Weight 大小
```

例如：

```text
7B BF16
≈ 14GB Weight
```

很多人学到这里，就开始产生一个错误直觉：

> “我有 24GB 显存，14GB 模型当然随便跑。”

问题就在这里。

因为 GPU 显存不是只租给：

> **Model Weight。**

它还要住很多别的东西。

今天我们真正要建立的是一张完整账本：

```text
                    24GB VRAM
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
   Model Weight       KV Cache        Activations
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ▼
                 Runtime / Buffers
```

这一阶段真正需要带走 **5 个核心心智模型**：

```text
① VRAM 是一个共享预算，不是“模型专用仓库”

② Weight 是固定房租
   KV Cache 是按 Context 和用户数增长的住宿费

③ Context 越长，KV Cache 越大

④ Batch / 并发越高，KV Cache 基本也跟着放大

⑤ “刚好装下”不是好的部署方案
   必须给运行时留下安全余量
```

这一阶段公式会有，但只保留**真正能帮你判断显存的两个公式**。

先从直觉开始。

---

# 一、把显存想成一家酒店

假设你买了一张：

# 24GB VRAM

的 GPU。

就像你有一家：

> **24GB 容量的酒店。**

现在有四类客人要入住。

---

## 1. 第一类客人：Model Weights

这是模型本体。

比如：

```text
7B BF16
≈ 14GB
```

它们一旦模型加载好：

> 基本长期住在酒店里。

---

## 2. 第二类客人：KV Cache

这是模型针对：

> **当前正在处理的 Context**

保存的注意力历史。

用户输入越长：

> 它越大。

模型生成越长：

> 它继续变大。

---

## 3. 第三类客人：Activations

Transformer 正在计算时：

> 会产生各种中间结果。

这些结果不能凭空消失。

计算到某些阶段：

> 需要暂时存在显存里。

---

## 4. 第四类客人：Runtime / Temporary Buffers

GPU Kernel、推理框架、矩阵乘法等：

> 还可能需要临时工作区。

于是：

```text
24GB
```

绝对不能简单理解成：

```text
可以装24GB Weight
```

---

# 二、第一个核心心智模型：显存是一张预算表

以后看到一张 GPU，脑子里不要再只有：

```text
VRAM
=
Weights
```

而是：

```text
VRAM
=
┌─────────────────────────┐
│ ① Weights               │
├─────────────────────────┤
│ ② KV Cache              │
├─────────────────────────┤
│ ③ Activations           │
├─────────────────────────┤
│ ④ Runtime / Workspace   │
└─────────────────────────┘
```

这四个账户：

> **抢的是同一块显存。**

---

# 三、先把最容易算的 Weight 算清楚

这个第 6 阶段已经学过。

我们今天直接做一张表。

| 模型参数量 | BF16/FP16 Weight | INT8 粗估 | 4-bit Weight 理论粗估 |
|---|---:|---:|---:|
| 7B | 约 14GB | 约 7GB | 约 3.5GB |
| 14B | 约 28GB | 约 14GB | 约 7GB |
| 32B | 约 64GB | 约 32GB | 约 16GB |

先再次强调：

> 这是 **Weight 数量级**。

不是：

> 最终运行显存。

---

# 四、现在拿一张 24GB GPU 做第一次判断

## 5. 7B BF16

Weight：

```text
约14GB
```

24GB 减去 14GB：

```text
还剩约10GB
```

这些空间可以继续给：

- KV Cache；
- Activations；
- Runtime。

所以：

> **中等 Context、较小 Batch 下，通常是一个比较合理的单卡推理候选。**

---

# 五、14B BF16 呢？

Weight：

```text
约28GB
```

你的 GPU：

```text
24GB
```

甚至还没开始处理 Prompt：

> Weight 自己就放不下。

所以：

```text
14B BF16
→ 单24GB GPU
→ 单看Weight就不成立
```

这个判断甚至：

> 不需要跑代码。

---

# 六、如果 14B 改成 INT8 呢？

Weight：

```text
约14GB
```

这时候突然：

> 又有机会了。

剩下大约：

```text
10GB级别空间
```

给其它账户。

---

# 七、如果 14B 改成 4-bit 呢？

Weight 理论粗估：

```text
约7GB
```

显存空间明显更宽松。

但是千万别马上说：

> “那一定可以跑 128K Context。”

因为：

> **KV Cache 还没算。**

---

# 八、这就是第二个核心心智模型

可以把 Weight 看成：

# 固定房租

模型一旦选定：

```text
7B
14B
32B
```

再选定 Weight Precision：

```text
BF16
INT8
INT4
```

Weight 占用：

> 大致就定下来了。

---

## 8. KV Cache 则完全不同

它像：

# 按入住人数和住宿天数收费

Context 越长：

> 越大。

同时服务用户越多：

> 越大。

这两个变量特别重要。

---

# 九、重新认识 KV Cache

第五阶段我们已经知道：

生成过程分成：

```text
Prefill
↓
建立过去Token的K/V
↓
Decode
↓
复用过去K/V
```

如果不保存 K/V：

> 每生成一个新 Token，都得把过去大量 Attention 信息重新计算。

所以：

# KV Cache 是用显存换速度

---

# 十、一个 ProcurementAI 场景

用户上传一份采购文件。

### 用户 A

文件很短：

```text
2,000 Token
```

---

### 用户 B

文件很长：

```text
32,000 Token
```

---

### 用户 C

一次塞入：

```text
128,000 Token
```

虽然使用的：

> 是同一个模型，

模型 Weight：

> 一模一样，

但三个人的 KV Cache：

> 完全不同。

---

# 十一、用会议秘书继续理解

假设一个专家团队有：

> 32 层 Transformer。

每一层：

> 都有自己的 Attention。

秘书读一个 Token：

> 每一层都要留下部分 K/V 记录。

所以一份文档从：

```text
1,000 Token
```

增长到：

```text
32,000 Token
```

不是只多存：

> 一份笔记。

而是：

> **每一层都在增加自己的 K/V 历史。**

---

# 十二、KV Cache 受哪些东西影响？

先不要看公式。

只看这张图：

```text
KV Cache
│
├── 模型有多少层
│
├── Context有多少Token
│
├── 有多少KV Heads
│
├── 每个Head多宽
│
├── 每个数占多少Bytes
│
└── 同时有多少条Sequence
```

所以：

> KV Cache 不是只由模型 B 数决定。

---

# 十三、为什么 GQA 又回来了？

第二课 Self-Attention 学过：

```text
MHA
Query Heads很多
Key Heads很多
Value Heads很多
```

而：

```text
GQA
Query Heads很多
但多个Query Head共享较少的K/V Heads
```

---

## 9. 当时可能觉得

> “这只是 Attention 架构细节。”

现在终于看到工程意义：

> **K/V Head 越少，需要缓存的 K/V 就越少。**

---

# 十四、一个特别直观的例子

假设：

```text
Query Heads = 32
```

### 普通 MHA

```text
KV Heads = 32
```

---

### GQA

```text
KV Heads = 8
```

那么 KV Cache 中的 Head 数：

> 直接少到四分之一。

这就是为什么：

> GQA 对长 Context 和推理部署特别有价值。

---

# 十五、现在才看第一个真正有用的公式

KV Cache 的粗略容量可以理解为：

\[
\boxed{
KV
\approx
2
\times
L
\times
S
\times
H_{KV}
\times
d_h
\times
B
\times
Bytes
}
\]

别背。

我们逐个翻译。

---

# 十六、公式里的 `2` 是谁？

因为缓存两样东西：

```text
K
+
V
```

所以：

```text
2
```

---

# 十七、`L` 是什么？

```text
L
=
Transformer Layers
```

例如：

```text
32层
```

每一层：

> 都需要自己的 KV Cache。

---

# 十八、`S` 是什么？

```text
S
=
Sequence Length
```

也就是当前 Context 中：

> 大约多少 Token。

---

# 十九、`H_KV` 是什么？

```text
KV Head数量
```

比如：

```text
8
```

---

# 二十、`d_h` 呢？

每一个 Attention Head：

> 有多少维。

例如：

```text
128
```

---

# 二十一、`Bytes` 是什么？

如果 K/V 使用：

```text
BF16
```

每个数字：

```text
2 Bytes
```

---

# 二十二、最后的 `B`

这是：

# Batch / 同时活跃的 Sequence 数

先简单理解：

> 一次同时在为多少条序列保存 KV。

---

# 二十三、现在不要算大模型，先算一个特别整齐的教学模型

假设：

```text
Layers       = 32
KV Heads     = 8
Head Dim     = 128
KV dtype     = BF16 = 2 Bytes
Batch        = 1
```

只改变：

> Context Length。

---

# 二十四、Context = 8K

大约：

```text
8192 Token
```

代入后：

> KV Cache 大约 **1 GiB**。

先别管计算过程。

只记：

```text
8K Context
→ 约1GB KV Cache
```

对于这个教学架构。

---

# 二十五、如果 Context 变成 32K 呢？

32K：

> 是 8K 的 4 倍。

于是 KV Cache：

```text
约4GB
```

---

# 二十六、如果 Context = 128K？

128K：

> 是 8K 的 16 倍。

KV：

```text
约16GB
```

---

# 二十七、停一下，看这张表

仍然是：

> **完全同一个模型。**

| Context | KV Cache 粗估 |
|---|---:|
| 8K | 约 1 GiB |
| 32K | 约 4 GiB |
| 128K | 约 16 GiB |

这就是为什么：

> **Context Length 本身就是显存变量。**

---

# 二十八、现在用 24GB GPU 重做 7B BF16 案例

假设：

```text
Weights
≈ 14GB
```

GPU：

```text
24GB
```

---

## 10. 8K Context

粗略：

```text
Weights       14GB
KV Cache       1GB
------------------
≈15GB
```

还没算：

- Activations；
- Runtime；
- Buffer。

但总体：

> 有较明显余量。

---

# 二十九、换成 32K Context

```text
Weights       14GB
KV Cache       4GB
------------------
≈18GB
```

剩余空间：

> 明显变少。

---

# 三十、换成 128K Context

```text
Weights       14GB
KV Cache      16GB
------------------
≈30GB
```

已经超过：

```text
24GB
```

还没算其它东西。

于是：

# CUDA OOM

完全不奇怪。

---

# 三十一、所以第三个核心心智模型

\[
\boxed{
Context越长
\Rightarrow
KVCache越大
}
\]

而且在其它条件固定时：

> 大体是线性增长。

---

# 三十二、这解释了一个以前很奇怪的现象

用户说：

> “模型昨天明明能跑，今天怎么 OOM 了？”

可能模型：

> 完全没变。

只是昨天输入：

```text
3页采购条款
```

今天输入：

```text
400页采购文件
```

---

# 三十三、所以排查 OOM 时必须问

不要只问：

> “模型多大？”

还要问：

```text
Context多长？
```

这是非常重要的诊断习惯。

---

# 三十四、第四个核心心智模型：并发也要吃 KV

刚才全部是：

```text
Batch = 1
```

也就是：

> 只有一条 Sequence。

---

## 11. 如果同时 4 个请求呢？

还是刚才：

```text
8K Context
```

单条大约：

```text
1GB KV
```

四条类似请求：

> KV 总需求可能接近约 4GB 量级。

---

# 三十五、32K Context × 4 条呢？

一条：

```text
约4GB
```

四条：

```text
约16GB
```

---

# 三十六、这就是为什么“单用户能跑”完全不等于“能生产部署”

本地测试：

```text
1个用户
```

感觉：

> 非常顺。

上线以后：

```text
10个用户
50个用户
100个用户
```

突然：

> 显存完全是另一回事。

---

# 三十七、政府采购系统特别容易遇到这个问题

因为用户输入不是普通一句聊天。

可能是：

```text
采购需求
+
招标文件
+
评分办法
+
供应商材料
+
RAG法规证据
```

单请求本来：

> 就很长。

再加并发：

> KV Cache 压力会非常明显。

---

# 三十八、把生产推理想成酒店

Weight：

> 酒店建筑本身。

只有一份。

---

## 12. 每个用户进来

都会拿一个房间：

> 放自己的 KV Cache。

所以：

```text
更多用户
=
更多KV房间
```

---

# 三十九、Weight 不会因为用户翻倍而简单翻倍

如果同一个模型服务 10 个用户：

> 不需要复制 10 份 Weight。

模型 Weight：

> 可以共享。

---

# 四十、但是 KV Cache 是请求私有的

用户 A：

> 有自己的对话历史。

用户 B：

> 有自己的采购文件。

用户 C：

> 有自己的 Token Sequence。

这些不能：

> 全部混成同一个 KV Cache。

---

# 四十一、所以生产系统显存结构更像这样

```text
                     GPU VRAM
                         │
       ┌─────────────────┴────────────────┐
       │                                  │
       ▼                                  ▼
  Shared Model Weight               Per-request KV
                                      │
                         ┌────────────┼────────────┐
                         ▼            ▼            ▼
                       User A       User B       User C
```

这张图非常重要。

---

# 四十二、为什么 vLLM 以后会重要？

现在先不展开技术细节。

传统 KV Cache 管理可能：

> 出现大量内存碎片、预留浪费。

vLLM 等推理框架会想办法：

> 更高效地管理 KV Cache。

后面第 9 阶段会进一步讲：

# PagedAttention

---

# 四十三、现在进入第三个账户：Activations

Activation 是什么？

第二课已经学过。

例如：

```text
Token Embedding
↓
Attention输出
↓
MLP中间结果
↓
下一层Hidden State
```

这些：

> 都是中间计算结果。

---

# 四十四、用办公室类比

Weights：

> 员工长期知识。

KV Cache：

> 当前项目的会议笔记。

Activations：

> **员工现在桌面上正在计算的草稿纸。**

---

# 四十五、推理时 Activation 为什么不像训练那么夸张？

因为推理：

> 不需要为 Backprop 保存所有中间结果。

算完一部分：

> 很多临时 Activation 可以被释放或复用。

---

# 四十六、训练就完全不同

训练还要：

```text
Forward
↓
保存很多中间结果
↓
Backward
↓
计算Gradient
```

为了 Backward：

> 必须保留更多 Activation。

这就是训练显存远大于纯推理的重要原因之一。

---

# 四十七、所以我们先明确

今天这张显存账本：

> 主要先用于 **Inference**。

训练显存：

> 要额外再加很多账户。

---

# 四十八、Activation 受什么影响？

一个很实用的直觉：

```text
Batch越大
↓
同时算的数据越多
↓
Activation通常越大
```

Context 越长：

> 也会增加中间 Tensor。

---

# 四十九、所以 Batch Size 是双重压力

它可能同时让：

```text
KV Cache ↑
```

和：

```text
Activations ↑
```

---

# 五十、第四个账户：Runtime / Temporary Buffers

这类最容易被初学者忽略。

你可能粗算：

```text
Weights = 14GB
KV      = 4GB
合计     = 18GB
```

然后说：

> “24GB 肯定够，还有 6GB。”

---

## 13. 但 GPU 运行矩阵 Kernel

可能还需要：

- Workspace；
- CUDA Context；
- Kernel 临时 Buffer；
- Framework 内存；
- 内存对齐；
- 已缓存未立即归还的分配。

所以：

> 实际 `nvidia-smi` 看到的显存可能更高。

---

# 五十一、这就是第五个核心心智模型

## 不要把 GPU 用到 100% 才叫“充分利用”

生产环境真正希望的是：

> 有余量。

因为：

- Prompt 长度会波动；
- 并发会波动；
- Kernel 有临时峰值；
- 某些请求输出更长。

---

# 五十二、一个停车场类比

你有：

```text
100个停车位
```

如果日常运营计划就是：

```text
100辆车
```

看起来：

> 利用率 100%。

但第 101 辆临时车来了：

> 整个系统没有任何余地。

---

## 14. 更健康的方案

应该给：

- 临时车辆；
- 救援车辆；
- 施工车辆；

留下空间。

显存也是一样。

---

# 五十三、所以工程上不要问

> “理论上能不能塞进 24GB？”

而应该问：

> **“在我的 Context、Batch、并发和生成长度下，是否能稳定运行？”**

这句话比：

> “能跑”

专业很多。

---

# 五十四、现在建立正式“显存账本”

以后看到一个推理任务，先写：

```text
┌───────────────────────────────────┐
│       Inference VRAM Ledger       │
├───────────────────────────────────┤
│ Model Weights                     │
│ + Quantization Metadata           │
├───────────────────────────────────┤
│ KV Cache                          │
├───────────────────────────────────┤
│ Activations                       │
├───────────────────────────────────┤
│ Runtime / Kernel Workspace        │
├───────────────────────────────────┤
│ Safety Headroom                   │
└───────────────────────────────────┘
```

这就是本阶段的核心工具。

---

# 五十五、ProcurementLM 案例一：7B BF16 + 24GB

假设：

```text
Model      = 7B
Weight     = BF16
GPU        = 24GB
Context    = 8K
Batch      = 1
```

---

## 15. Weight

粗略：

```text
14GB
```

---

## 16. KV

假设模型架构接近我们刚才教学例子：

```text
约1GB
```

---

## 17. 于是基础账面

```text
14GB
+1GB
≈15GB
```

还剩：

> 一些明显空间。

所以这是：

> 一个看起来比较健康的起点。

---

# 五十六、如果同一个模型 Context 改成 32K？

KV：

```text
约4GB
```

变成：

```text
14GB Weights
+
4GB KV
=
约18GB
```

---

## 18. 还能不能跑？

有可能。

但相比 8K：

> 安全余量明显减少。

此时需要真实测：

- Runtime；
- Actual KV dtype；
- Framework；
- Output Length。

---

# 五十七、如果变成 128K？

刚才的教学架构：

```text
KV约16GB
```

Weight：

```text
14GB
```

合计：

```text
约30GB
```

于是单 24GB：

> 从账本上就已经宣告失败。

不需要等程序 OOM 才知道。

---

# 五十八、ProcurementLM 案例二：14B BF16 + 24GB

只看：

```text
Weights ≈ 28GB
```

所以：

> 直接淘汰单卡 BF16 方案。

---

# 五十九、改成 14B INT8

Weight：

```text
约14GB
```

这时：

> 重新有空间给 KV Cache。

对于适中 Context：

> 可能进入候选区。

---

# 六十、改成 14B 4-bit

Weight 粗略：

```text
约7GB+
```

显存压力大幅下降。

这时：

> Context 和 KV Cache 的预算地位开始明显上升。

---

# 六十一、这个现象非常重要

高精度大模型时：

```text
Weight
```

往往是最大块。

量化以后：

```text
Weight ↓↓↓
```

于是其它账户：

```text
KV Cache
Activations
Buffers
```

占比：

> 开始越来越显眼。

---

# 六十二、所以量化会“移动瓶颈”

这句话非常专业，也非常重要：

\[
\boxed{
Quantization
\neq
消灭显存瓶颈
}
\]

它经常只是：

> **把瓶颈从 Weight 推向 KV Cache / Runtime。**

---

# 六十三、ProcurementLM 案例三：32B 4-bit + 24GB

Weight 理论粗估：

```text
约16GB
```

加上量化 Metadata：

> 会再多一些。

---

## 19. 于是很多人会说

> “24GB 能跑 32B 4-bit！”

更准确的说法应该是：

> **在某些量化格式、推理框架、较小 Context、较低并发和合适配置下，可能有机会。**

---

# 六十四、为什么要说得这么谨慎？

因为剩下的：

```text
约8GB级别
```

不是全给你随便用。

还要分：

```text
KV
+
Activation
+
Runtime
```

---

# 六十五、如果再塞 32K 或更长 Context

显存：

> 很可能迅速吃紧。

---

# 六十六、所以“某张卡能跑某模型”这句话缺了很多参数

完整问题应该是：

```text
什么模型？
什么量化？
什么Context？
什么Batch？
多少并发？
什么推理框架？
生成多长？
```

如果这些都没说：

> “能跑”

的信息量其实很低。

---

# 六十七、现在比较三个模型在 24GB 上的直觉

### 7B BF16

```text
Weight约14GB
```

优势：

> 高精度 Weight，空间尚可。

---

### 14B 4-bit

```text
Weight约7GB+
```

优势：

> 模型参数更多，但经过量化。

---

### 32B 4-bit

```text
Weight约16GB+
```

优势：

> 模型更大。

但：

> Context 和 Runtime 余量更紧。

---

# 六十八、哪个一定最好？

没有答案。

因为：

```text
Model Size
≠
Business Quality
```

而：

```text
Lower Quantization
≠
Free Lunch
```

所以最后还是要：

# Benchmark

---

# 六十九、政府采购业务不能只看“能装最大的模型”

假设方案 A：

```text
32B 4-bit
Context只能勉强8K
```

方案 B：

```text
14B 4-bit
Context可以舒服32K
```

如果你的任务是：

> 审查 200 页招标文件，

方案 B：

> 可能反而更有业务价值。

---

# 七十、这就是系统设计思维

不是：

```text
最大模型
=
最好系统
```

而是：

```text
模型能力
×
Context能力
×
速度
×
并发
×
稳定性
×
业务准确率
```

一起看。

---

# 七十一、一个特别容易忽略的问题：Output Token 也占 Context

假设 Prompt：

```text
30K Token
```

模型最大窗口：

```text
32K
```

你觉得：

> “还有 2K。”

没错。

但如果希望生成：

```text
4K Output
```

那就：

> 不够。

---

# 七十二、而且生成中的 Output 也会增加 KV Cache

模型每生成：

> 一个新 Token，

也需要：

> 把这个 Token 的 K/V 加入 Cache。

所以：

```text
KV Cache
```

不仅由输入长度决定。

更准确：

```text
当前Context
=
Input Tokens
+
Generated Tokens
```

---

# 七十三、一个采购报告案例

输入：

```text
20K Token招标文件
```

RAG：

```text
5K Token法规证据
```

System + Prompt：

```text
1K
```

希望输出：

```text
4K Token风险报告
```

总 Context：

```text
约30K
```

这才是：

> 实际预算。

---

# 七十四、所以 Context Budget 和 VRAM Budget 是连在一起的

```text
更多RAG证据
      ↓
更多Token
      ↓
更大KV Cache
      ↓
更大VRAM需求
```

---

# 七十五、这解释了为什么 RAG 不是“文档塞越多越好”

检索 50 段法规全塞进去：

> 不仅可能干扰模型，

还会：

> 直接消耗 Context 和 KV Cache。

---

# 七十六、以后 ProcurementRAG 的目标会是

```text
更相关的证据
而不是
更多的证据
```

这就是：

# Retrieval Quality

为什么重要。

---

# 七十七、现在说 Batch

假设模型每次只处理：

```text
1条采购条款
```

Batch：

```text
1
```

---

## 20. 如果一次处理 8 条

```text
Batch = 8
```

GPU 可以：

> 更并行。

吞吐可能：

> 更高。

---

## 21. 但是代价

同时存在更多：

- Input；
- Activation；
- KV Cache。

所以显存：

> 上升。

---

# 七十八、所以 Batch 是典型的“速度换显存”

较大的 Batch：

> 可能提高 GPU 利用率。

但：

> 吃更多显存。

---

# 七十九、这和并发有什么关系？

概念上很接近，但生产推理里：

> 并发请求和传统固定 Batch 并不完全是同一件事。

推理引擎可能：

> 动态把多个请求组织成 Batch。

---

# 八十、先用简单心智模型

对我们现在而言可以先记：

```text
同时活跃Sequence越多
↓
KV总量越大
↓
显存压力越高
```

已经足够。

---

# 八十一、为什么生成长度不可忽略？

假设两个用户都输入：

```text
4K Prompt
```

---

### 用户 A

要求：

```text
一句话回答
```

输出：

```text
50 Token
```

---

### 用户 B

要求：

```text
生成完整采购风险审查报告
```

输出：

```text
4000 Token
```

---

## 22. B 的 Session

活得更久。

Context：

> 越来越长。

KV Cache：

> 也不断增长。

---

# 八十二、所以生产容量不能只测短回答

如果真实业务：

> 输出长报告，

Benchmark 却只生成：

```text
20 Token
```

得到的显存和 TPS：

> 没太大业务代表性。

---

# 八十三、这就是为什么 Benchmark 必须模拟真实工作负载

例如 ProcurementAI 测试至少应该有：

```text
短条款审查
中型采购文件
长招标文件
法规RAG输入
长报告输出
多人并发
```

---

# 八十四、显存碎片是什么直觉？

假设显存里：

```text
有很多空位
```

但它们：

> 东一块、西一块。

某个 Kernel 需要：

> 一大块连续空间。

却找不到。

---

## 23. 像停车场

空了：

```text
10个车位
```

但全是：

> 零散的单个小位。

现在一辆超长卡车：

> 需要连续 4 个位。

总空位够：

> 但仍然停不进去。

---

# 八十五、这就是为什么 OOM 有时让人觉得奇怪

你看到：

```text
理论上还有显存
```

但某次大型分配：

> 仍然失败。

实际内存分配：

> 比简单加减法复杂。

---

# 八十六、所以账本是“容量规划”，不是逐字节保证

我们今天算：

```text
14GB + 4GB
```

是为了：

> 判断方案方向。

最终是否稳定：

> 必须真实运行测峰值。

---

# 八十七、什么叫 Peak VRAM？

不是：

> 模型空闲时占多少。

而是：

> 整个实际请求过程中显存最高到多少。

---

# 八十八、为什么它更重要？

假设平时：

```text
18GB
```

某个 Attention Kernel 峰值：

```text
24.5GB
```

你的 GPU：

```text
24GB
```

结果：

> 仍然 OOM。

所以部署容量要看：

# Peak

---

# 八十九、怎样做一个简单的容量实验？

以后真正跑模型时，我们可以设计：

```text
固定Model
固定Precision
固定Batch
```

然后改变：

```text
Context
2K
4K
8K
16K
32K
```

记录：

```text
Peak VRAM
TTFT
TPS
```

---

# 九十、得到一张表

例如教学意义上的：

| Context | Peak VRAM | TTFT | TPS |
|---:|---:|---:|---:|
| 2K | ... | ... | ... |
| 8K | ... | ... | ... |
| 16K | ... | ... | ... |
| 32K | ... | ... | ... |

这比：

> “这个模型支持 32K”

有用得多。

---

# 九十一、“支持32K”到底是什么意思？

它更多是在说：

> 模型架构/位置编码允许在某个范围使用。

但它不保证：

> 你的 GPU 能以任何 Batch、任何并发舒服跑 32K。

---

# 九十二、所以要区分

```text
Model Context Capability
```

和：

```text
Hardware Context Capacity
```

前者：

> 模型理论/训练支持。

后者：

> 你机器实际装不装得下。

---

# 九十三、这两个必须同时满足

```text
模型支持128K
+
GPU只够16K
```

实际系统：

> 仍然跑不了 128K。

---

# 九十四、再来看 MHA vs GQA 的 KV 差距

刚才教学模型：

```text
32 Layers
Head Dim 128
BF16
```

---

## 24. GQA

```text
KV Heads = 8
```

8K：

```text
约1GiB
```

32K：

```text
约4GiB
```

128K：

```text
约16GiB
```

---

## 25. 如果是 MHA

```text
KV Heads = 32
```

是四倍。

同样条件：

| Context | GQA：8 KV Heads | MHA：32 KV Heads |
|---|---:|---:|
| 8K | 约 1GiB | 约 4GiB |
| 32K | 约 4GiB | 约 16GiB |
| 128K | 约 16GiB | 约 64GiB |

现在应该能非常直观地感受到：

> 为什么现代推理架构那么在意 GQA/MQA。

---

# 九十五、第二课一个抽象概念，到这里变成钱了

第二课里：

```text
GQA
```

可能只是：

> “多个 Query Head 共享 K/V。”

今天它变成：

```text
更少KV Heads
↓
更小KV Cache
↓
更长Context
↓
更多并发
↓
更低部署成本
```

这就是为什么底层架构最终会影响：

> 商业成本。

---

# 九十六、企业选模型为什么不能只看 Benchmark 分数？

假设：

### 模型 A

效果：

```text
95分
```

但：

```text
KV特别大
需要4张GPU
```

---

### 模型 B

效果：

```text
94.5分
```

但：

```text
一张GPU就能部署
```

---

## 26. 哪个更好？

要看业务。

如果 B：

> 已经达到质量门槛，

部署成本又低很多，

B：

> 可能更合理。

---

# 九十七、这就是工程中的 Pareto Frontier

这个词先认识即可。

意思是：

> 在质量、成本、速度等多个目标之间，寻找没有明显被全面碾压的方案。

---

# 九十八、ProcurementLM 最终不会只优化一个数字

至少会考虑：

```text
Accuracy / Recall
+
Citation Quality
+
VRAM
+
Latency
+
Throughput
+
Cost
```

---

# 九十九、现在讲训练显存，只建立地图

如果以后从推理进入训练：

显存账本会变成：

```text
Training VRAM
│
├── Weights
├── Gradients
├── Optimizer States
├── Activations
├── Temporary Buffers
└── Distributed Training Overhead
```

注意：

> KV Cache 通常不是训练显存的核心故事。

---

# 一百、为什么 Gradient 很大？

如果 Full Fine-tuning：

> 每个可训练 Weight 都需要 Gradient。

模型：

```text
7B Parameter
```

就意味着：

> 数十亿个 Gradient。

---

# 一百零一、Optimizer State 更可怕

例如 Adam 类优化器：

> 通常还要维护额外状态。

所以 Full Fine-tuning：

> 显存需求远大于只放 Weight。

---

# 一百零二、这就是 LoRA 的另一个价值

LoRA：

> 不让全部几十亿参数都产生可训练状态。

只训练：

> 少量 Adapter 参数。

于是：

```text
Gradient ↓
Optimizer States ↓
```

显存：

> 大幅下降。

---

# 一百零三、QLoRA 再进一步

```text
Base Weight
→ 4-bit

Base Weight
→ Frozen

LoRA
→ Trainable
```

于是：

> Weight 账户和训练状态账户同时得到缓解。

第五课会彻底算一次。

---

# 一百零四、现在把推理和训练放一起看

```text
INFERENCE
────────────
Weights
KV Cache
Activations
Runtime


TRAINING
────────────
Weights
Gradients
Optimizer
Activations
Runtime
```

两边：

> 都吃显存。

但：

> 吃法完全不同。

---

# 一百零五、所以买 GPU 前第一问仍然是

> **你究竟要干什么？**

只是：

```text
Inference
```

还是：

```text
QLoRA
```

还是：

```text
Full Fine-tuning
```

还是：

```text
CPT
```

答案不同：

> 硬件预算会差非常多。

---

# 一百零六、我们现在可以回答：24GB GPU 怎么选模型？

先不要把它理解成一个固定型号推荐。

我们做的是：

# 决策框架

```text
24GB VRAM
   │
   ▼
先预留Runtime / Safety Margin
   │
   ▼
剩余预算
   │
   ├─ Weight
   │
   └─ KV Cache
```

---

# 一百零七、如果目标是舒服学习和实验

更优先：

> 留余量。

例如：

```text
7B BF16
```

或者：

```text
更大模型的合适量化版本
```

通常比：

> 强行把最大模型塞到 23.9GB

更有学习价值。

---

# 一百零八、为什么？

因为你后面还要测试：

```text
Context变化

Batch变化

不同Prompt

不同Sampling

RAG证据
```

如果一开始显存：

> 已经顶死，

任何实验：

> 都容易 OOM。

---

# 一百零九、如果目标是极限单卡模型能力

那策略可能变成：

```text
更大的模型
+
更激进的Quantization
+
较小Batch
+
限制Context
```

---

# 一百一十、如果目标是长文档采购审查

策略可能反过来：

```text
不要把Weight塞到极限
↓
给KV Cache留空间
↓
保证更长Context
```

---

# 一百一十一、如果目标是多人生产服务

还要：

```text
给并发KV留空间
```

所以可能宁愿：

> 用稍小模型。

---

# 一百一十二、这就是同一张 GPU 的三种完全不同用法

```text
同一张24GB GPU
      │
      ├── 最大模型优先
      │
      ├── 长Context优先
      │
      └── 高并发优先
```

没有一种配置：

> 同时全部最大。

---

# 一百一十三、这是一个“资源三角形”

```text
                 更大模型
                    ▲
                   / \
                  /   \
                 /     \
                /       \
               /         \
      长Context ───────── 高并发
```

在同一块显存预算里：

> 三个方向通常互相争空间。

这张图建议牢牢记住。

---

# 一百一十四、政府采购系统最可能偏向哪里？

我们的任务特点：

> 经常需要处理较长文档。

所以未来 ProcurementAI 很可能不能只追求：

> 最大 Parameter Count。

还需要非常重视：

```text
Long Context
+
RAG Context
+
Evidence
```

---

# 一百一十五、但长 Context 也不是无限塞文件

因为长 Context 会带来：

- 更高 KV Cache；
- 更长 Prefill；
- 更高 TTFT；
- Lost-in-the-middle 等模型质量问题。

所以未来真正架构：

> 仍然会大量依靠 RAG 和文档分解。

---

# 一百一十六、这解释了 ProcurementAI 的整体结构为什么不是

```text
把1000页文件
全部塞给一个超长Context模型
```

而更可能是：

```text
文件解析
↓
结构化切分
↓
检索 / 定位
↓
选最相关内容
↓
送给LLM
↓
综合判断
```

---

# 一百一十七、显存优化其实和数据工程有关

这点很有意思。

如果你能从 300 页文件里准确找到：

> 真正相关的 20 页，

不仅：

> 检索质量更好，

还会：

> Token 更少、KV 更小、TTFT 更低。

---

# 一百一十八、所以 RAG 也可以理解成一种计算资源优化

好的 Retrieval：

```text
无关Context ↓
```

于是：

```text
KV Cache ↓
TTFT ↓
噪声 ↓
```

这是未来很重要的一条线。

---

# 一百一十九、显存不足时的决策顺序

以后真 OOM，不要乱改。

可以按这个顺序想：

```text
OOM
 │
 ├─ Weight太大？
 │     ↓
 │   Quantization / 小模型 / 多GPU
 │
 ├─ Context太长？
 │     ↓
 │   缩Context / RAG / KV优化
 │
 ├─ Batch太大？
 │     ↓
 │   降Batch
 │
 ├─ 并发太高？
 │     ↓
 │   限并发 / 调度
 │
 └─ Runtime峰值？
       ↓
     优化框架 / Buffer / Kernel
```

这是非常实用的一张故障树。

---

# 一百二十、不要第一反应就量化

如果 OOM 原因是：

```text
128K Context造成巨大KV
```

你继续把 Weight：

```text
8-bit → 4-bit
```

可能有帮助。

但如果 KV 已经占大头：

> 效果可能没有想象中那么大。

---

# 一百二十一、也不要第一反应就换更大 GPU

如果输入里：

> 80% 都是不相关文档，

更聪明的办法可能是：

> 做更好的 Retrieval。

而不是：

> 砸钱买显存。

---

# 一百二十二、这就是“Find the dominant term”

虽然这是数学味的词，但意思极简单：

> **到底是谁占得最多？**

---

## 27. 如果最大的是 Weight

优化：

> Weight。

---

## 28. 如果最大的是 KV

优化：

> Context / KV。

---

## 29. 如果最大的是 Activation

优化：

> Batch / Runtime / Training Strategy。

---

# 一百二十三、这是专家真正的显存思维

不是背：

> “7B需要多少显存。”

而是：

\[
\boxed{
先找显存主要花在哪里
}
\]

再优化。

---

# 一百二十四、本阶段 5 个核心心智模型总结

| 核心心智模型 | 真正含义 |
|---|---|
| **① VRAM = 共享预算** | Weight、KV、Activation、Runtime 都抢同一块空间 |
| **② Weight = 固定房租** | 模型和 dtype 定了以后，Weight 基本确定 |
| **③ KV = 随 Context 增长的费用** | 输入越长、输出越长，KV 越大 |
| **④ 并发 = 多份请求状态** | Weight 可以共享，但每个请求需要自己的 KV |
| **⑤ 刚好装下 ≠ 可稳定部署** | 必须考虑 Peak VRAM 和安全余量 |

---

# 一百二十五、再加三个辅助模型

### 辅助模型 A：资源三角形

```text
更大模型
   ↕
更长Context
   ↕
更高并发
```

在固定显存里：

> 三者争预算。

---

### 辅助模型 B：量化移动瓶颈

```text
Weight ↓
↓
KV占比 ↑
```

---

### 辅助模型 C：先找大头

```text
Who is dominating VRAM?
```

找到以后：

> 再优化。

---

# 一百二十六、ProcurementLM 快速判断练习 A

GPU：

```text
24GB
```

模型：

```text
14B BF16
```

只看 Weight：

```text
约28GB
```

结论：

> **单卡直接不成立。**

---

# 一百二十七、练习 B

同一模型：

```text
14B INT8
```

Weight：

```text
约14GB
```

现在：

> 有进入候选方案的可能。

但仍要问：

> Context 和 Batch。

---

# 一百二十八、练习 C

```text
32B 4-bit
```

Weight 粗略：

```text
约16GB+
```

24GB 卡：

> 有些配置下可能可以跑。

是不是可以直接承诺：

> “128K 文档也没问题”？

**绝对不能。**

---

# 一百二十九、练习 D

7B BF16：

```text
14GB Weight
```

为什么 128K Context 可能比：

```text
14B 4-bit + 8K Context
```

还更吃显存？

因为：

> 第一个方案的 KV Cache 可能非常大。

---

# 一百三十、练习 E

模型从 7B 变 14B。

KV Cache 一定刚好翻倍吗？

**不一定。**

因为 KV Cache 更直接取决于：

- Layer Count；
- KV Head Count；
- Head Dim；
- Context；
- dtype。

不同架构：

> 参数量相近也可能 KV 成本不同。

---

# 一百三十一、这个问题很关键

所以不能简单认为：

```text
模型大2倍
→
KV一定大2倍
```

Architecture：

> 很重要。

---

# 一百三十二、练习 F

同一个模型：

```text
Batch 1
→
Batch 8
```

Weight：

> 基本没有乘 8。

但 KV 和 Activation：

> 可能大幅增加。

---

# 一百三十三、练习 G

一个模型“支持128K”。

是不是意味着：

> 8GB GPU 也一定能跑 128K？

不是。

支持：

> 是模型能力范围。

能不能运行：

> 是硬件容量问题。

---

# 一百三十四、本阶段最容易犯的八个错误

### 错误 1

> 显存 = Weight。

错。

---

### 错误 2

> Weight 放得下，就一定能推理。

错。

---

### 错误 3

> Context 只影响速度，不影响显存。

错。

---

### 错误 4

> Weight 已经 4-bit，长 Context 就不再 OOM。

错。

---

### 错误 5

> 10 个用户要复制 10 份 Model Weight。

通常不是这么理解。

---

### 错误 6

> 模型官方支持 128K，我的 GPU 就支持 128K。

错。

---

### 错误 7

> 两张卡总显存加起来够，就一定像一张大卡一样简单。

错。

---

### 错误 8

> 把显存跑到 99.9% 是最专业的部署。

通常不是。

稳定生产：

> 需要余量。

---

# 一百三十五、把第三课第 1～7 阶段串起来

```text
Stage 1
GPU / VRAM是什么？
       ↓
Stage 2
软件怎么调用GPU？
       ↓
Stage 3
模型文件是什么？
       ↓
Stage 4
模型怎么加载进GPU？
       ↓
Stage 5
模型怎么真正生成文字？
       ↓
Stage 6
每个Weight占多大？
       ↓
Stage 7
所有东西加起来到底占多少显存？
```

现在我们终于真正回答了：

> **“能不能跑这个模型？”**

而不再只是凭感觉。

---

# 一百三十六、第 7 阶段掌握标准

如果现在不看前文，你能够自己解释下面这些问题，这一阶段就算真正掌握：

> 为什么 24GB GPU 不能简单装一个 24GB Weight 模型？

> 推理时显存至少有哪些主要账户？

> Weight 为什么可以理解成固定成本？

> KV Cache 为什么与 Context Length 有关？

> 为什么模型生成的 Token 也会继续增加 KV Cache？

> 为什么 GQA 可以显著降低 KV Cache？

> KV Cache 的大小大致受哪些变量控制？

> 为什么 8K → 32K Context，KV 大致会增长约 4 倍？

> 为什么 Batch / 并发会显著增加显存？

> 为什么多个请求可以共享 Weight，却不能共享同一份请求 KV？

> Activation 在推理和训练中的显存意义为什么不同？

> Runtime Buffer 为什么使简单算术低估实际 VRAM？

> Peak VRAM 为什么比空闲显存更重要？

> 为什么 7B BF16 能跑，不代表 128K Context 也能跑？

> 为什么量化之后显存瓶颈可能转向 KV Cache？

> 为什么 32B 4-bit 在 24GB 上“可能跑”与“稳定生产部署”完全不是一回事？

> 为什么支持 128K Context 和硬件能跑 128K 是两个问题？

> 为什么长文档政府采购系统需要 RAG，而不能只靠无限 Context？

> OOM 时为什么应该先判断到底是 Weight、KV、Activation 还是 Runtime 在占大头？

如果这些都能自己讲出来：

\[
\boxed{
第三课第7阶段真正掌握
}
\]

---

# 一百三十七、本阶段最终只记一句话

> **GPU 显存不是只用来装模型 Weight 的仓库，而是一张共享预算：Weight 是固定房租，KV Cache 随 Context 和并发增长，Activation 与 Runtime 还需要额外工作空间；真正的模型部署问题不是“模型文件多大”，而是“在真实工作负载下，显存峰值到底是多少”。**

最后把它压成一张图：

```text
                  GPU VRAM
                     │
      ┌──────────────┼───────────────┐
      │              │               │
      ▼              ▼               ▼
   Weights         KV Cache      Activations
  固定成本         动态增长        计算草稿
      │              │               │
      └──────────────┼───────────────┘
                     ▼
              Runtime / Buffers
                     │
                     ▼
               Safety Headroom


KV Cache 主要随着：

Context ↑
Batch / Concurrency ↑
Layers ↑
KV Heads ↑

而增长
```

---

# 下一阶段：第三课 · 第 8 阶段
## Temperature、Top-k、Top-p 到底在控制什么？为什么同一个模型，同一个问题，两次回答会不一样？

前面第 5 阶段我们留下了一个问题：

```text
Transformer
↓
Logits
↓
？？？
↓
Next Token
```

第 8 阶段就专门拆中间的：

```text
？？？
```

我们会继续坚持“先案例、后必要公式”。

比如模型面对下一 Token 时给出：

```text
A：40%
B：30%
C：15%
D：10%
其它：5%
```

然后分别看：

```text
Greedy
Temperature
Top-k
Top-p
```

究竟是在改变什么。

最后会回答一个对 ProcurementAI 特别重要的问题：

> **为什么创意写作可以接受更高随机性，而法规依据、资格条件审查、风险分类等任务往往应该更强调稳定、可复现和证据约束？**

也就是说，第 8 阶段我们会第一次把：

\[
\boxed{
“模型知道什么”
}
\]

和：

\[
\boxed{
“模型这次决定说什么”
}
\]

彻底分开。

---
