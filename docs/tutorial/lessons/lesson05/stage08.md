# 第五课 · 第 8 阶段
# Target Modules：LoRA 到底插在哪里？
## `q_proj`、`k_proj`、`v_proj`、`o_proj` 和 MLP，到底该训练哪些？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **A 容量一定更大，因为 64 > 16。**
2. **“Rank 用多少？”**
3. **Rank 多大，并且 LoRA 装在哪里？**
4. **只训练 Attention 和同时训练 MLP，给模型的适配自由度是不一样的。**
5. **“知识全在 MLP。”**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Target Modules` | 目标模块：指定 LoRA 插入哪些线性层 |
| `LoRA` | LoRA：冻结大部分基座参数，只训练低秩增量矩阵 |
| `MLP` | MLP/前馈网络：对每个位置表示做非线性变换 |
| `Attention` | 注意力：根据内容相关性动态聚合信息 |
| `Rank` | LoRA Rank：低秩增量的容量参数 |
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

到现在，我们已经理解：

\[
\Delta W = BA
\]

也知道了：

```text
Rank
=
每个 LoRA Adapter 有多少容量
```

但还有一个比 Rank 更基础的问题：

> **这个 Adapter 到底装在哪个权重矩阵上？**

因为 Transformer 里不是只有一个 \(W\)。

一层里就可能有：

```text
Attention
├── q_proj
├── k_proj
├── v_proj
└── o_proj

MLP
├── gate_proj
├── up_proj
└── down_proj
```

LoRA 不需要天然装到所有地方。

你必须决定：

> **哪些计算路径允许政府采购数据去修改。**

这就是今天的核心：

# Target Modules
## LoRA 目标模块

本阶段最终形成：

# `LoRATargetModulePolicy_V0.1`

---

# 一、本阶段只解决一个核心问题

假设某个 Transformer 权重：

\[
W_m
\]

被选为 LoRA Target Module。

那么：

\[
W_m'
=
W_m
+
\frac{\alpha}{r}B_mA_m
\]

如果它**没有**被选中：

\[
W_m'=W_m
\]

继续冻结。

所以 Target Modules 本质上是在回答：

> **Transformer 的哪些矩阵拥有“可学习的领域修正通道”？**

整个流程先锁成这一张图：

```text
                    Transformer Layer
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
         Attention                      MLP
             │                           │
     ┌───────┼───────┐           ┌───────┼───────┐
     ▼       ▼       ▼           ▼       ▼       ▼
   q_proj  k_proj  v_proj      gate    up      down
     │       │       │
     └── o_proj ─────┘

             ↓ Target Modules 决策

        哪些 W 保持完全 Frozen？
        哪些 W 旁边增加 LoRA ΔW？
```

一句话压缩：

> **Rank 决定“改多宽”，Target Modules 决定“改哪里”。**

---

# 二、先锁死 5 个核心心智模型

## 心智模型 1：Target Modules 决定“修改路径”，Rank 决定“修改容量”

这两个必须彻底分开。

假设：

```text
配置 A

r = 64
只给 q_proj 装 LoRA
```

另一组：

```text
配置 B

r = 16
给 q/k/v/o + MLP
全部装 LoRA
```

你不能简单说：

> A 容量一定更大，因为 64 > 16。

因为真实可训练空间同时受：

\[
\boxed{
Rank
\times
TargetModules
\times
Layers
}
\]

影响。

所以以后不要只问：

> “Rank 用多少？”

要问：

> **Rank 多大，并且 LoRA 装在哪里？**

---

## 心智模型 2：Attention Modules 和 MLP Modules 改的是不同计算路径

极简理解：

```text
Attention
更直接参与：
当前 Token 如何从上下文读取、组合信息

MLP
更直接参与：
读取后的表示怎样被非线性转换、重编码
```

因此：

> 只训练 Attention 和同时训练 MLP，给模型的适配自由度是不一样的。

注意，这只是工程直觉。

不能简单粗暴地说：

> “知识全在 MLP。”

或者：

> “推理全在 Attention。”

真实能力是整个网络共同产生的。

---

## 心智模型 3：`q/k/v/o` 不是四个同义矩阵

它们都属于 Attention，但角色不同。

非常粗略地记：

```text
q_proj
当前 Token 用什么表示去“寻找”相关信息

k_proj
上下文信息以什么表示被“匹配”

v_proj
匹配到以后真正携带什么内容

o_proj
多头 Attention 的结果怎样重新投回主表示空间
```

这不是四个装饰性的名字。

它们控制的是：

> Attention 计算不同阶段的表示变换。

---

## 心智模型 4：Target Modules 越多，自由度和成本通常都越大，但不保证业务效果越好

更多模块：

```text
Trainable Parameters ↑
Adapter Size ↑
Optimizer State ↑
训练计算 ↑
适配自由度 ↑
```

同时也可能：

```text
过拟合空间 ↑
实验变量 ↑
调试难度 ↑
```

所以：

\[
\boxed{
MoreTargetModules
\neq
AutomaticallyBetter
}
\]

真正要找的是：

> **完成任务所需的足够修改范围。**

---

## 心智模型 5：模块选择最终必须靠 Benchmark，而不是模块名称的“听感”

`q_proj` 看起来重要。

`v_proj` 也看起来重要。

MLP 更看起来重要。

但真正问题不是：

> 哪个名字更高级？

而是：

```text
固定 Dataset
+
固定 Rank / Alpha
+
改变 Target Modules
+
验证 Validation / Hard Case
```

所以：

\[
\boxed{
TargetModuleChoice
=
EmpiricalDesignDecision
}
\]

---

# 三、重新把 Attention 拉回来

第二课我们已经学过：

\[
Q=XW_Q
\]

\[
K=XW_K
\]

\[
V=XW_V
\]

Attention：

\[
Attention(Q,K,V)
=
Softmax
\left(
\frac{QK^T}{\sqrt{d_k}}
\right)V
\]

最后还通常有：

\[
O = Attention(Q,K,V)W_O
\]

对应到代码名称，大致就是：

```text
W_Q → q_proj
W_K → k_proj
W_V → v_proj
W_O → o_proj
```

LoRA 所做的事情就是：

> 对其中选中的某些 \(W\)，允许增加一个低秩 \(\Delta W\)。

---

# 四、`q_proj`：改变“当前表示怎样提出查询”

原本：

\[
Q=XW_Q
\]

加 LoRA 后：

\[
Q
=
X
\left(
W_Q+\Delta W_Q
\right)
\]

其中：

\[
\Delta W_Q=B_QA_Q
\]

直觉上，它会影响：

> 当前 Token 用怎样的内部表示去匹配上下文。

放到政府采购场景里，可以粗略理解：

模型看到：

```text
投标人在投标截止日前
须已在本市设立固定服务机构
```

它到底更重视：

```text
“本市”
```

还是更重视：

```text
“投标截止日前”
+
“须已设立”
+
“参与资格”
```

其中一部分适配可能通过 Query 表示改变而实现。

再次强调：

> 这不是“q_proj 专门存判断规则”。

而是它改变 Attention 中查询表示形成的方式。

---

# 五、`k_proj`：改变“上下文怎样被建立匹配索引”

Key 可以粗略理解成：

> 每个上下文位置拿什么表示参与 Query–Key 匹配。

于是：

\[
K=XW_K
\]

加 LoRA：

\[
K
=
X
\left(
W_K+\Delta W_K
\right)
\]

它会影响：

> 哪些上下文位置与当前 Query 更容易形成高匹配。

例如：

```text
资格条件
投标前
本地机构
中标后
服务响应
```

哪些信息之间应该建立更强的关系，

理论上都可能受到 K 路径适配的影响。

---

# 六、`v_proj`：改变“被读取的信息实际携带什么表示”

Attention 权重最终作用在：

\[
V
\]

上。

所以 V 可以粗略记成：

> **匹配完成以后，被带走的内容表示。**

公式：

\[
V=XW_V
\]

LoRA：

\[
V
=
X
\left(
W_V+\Delta W_V
\right)
\]

因此调整 `v_proj`：

> 会改变上下文信息被 Attention 读取后，以怎样的内部表示传递出去。

这也是为什么 `q_proj` / `v_proj` 经常会作为一个简洁 LoRA Baseline 的候选组合。

---

# 七、`o_proj`：改变 Attention 结果怎样重新写回主表示流

Attention 并不是最终直接结束。

多个 Head 产生的结果还需要重新映射：

\[
H_{\text{attn}}
W_O
\]

也就是：

```text
o_proj
```

可以粗略理解：

> **Attention 已经读到的信息，怎样重新整合进模型的 Residual Stream。**

所以：

```text
q/k/v
```

主要影响：

> Attention 内部怎样构造和读取信息。

而：

```text
o_proj
```

影响：

> 读取结果怎样重新进入后续 Transformer 计算。

---

# 八、现在进入 MLP：`gate_proj / up_proj / down_proj`

现代 LLM 的 MLP 往往不只是一个简单：

\[
Wx
\]

例如常见门控 MLP 可以抽象成：

\[
MLP(x)
=
W_{down}
\left[
\sigma(W_{gate}x)
\odot
(W_{up}x)
\right]
\]

具体不同模型会不同。

但核心结构可以理解成：

```text
hidden state
     │
     ├── gate_proj
     │
     └── up_proj
           │
           ▼
     高维中间表示
           │
           ▼
       down_proj
           │
           ▼
回到 hidden dimension
```

所以 MLP 是：

> Transformer 中另一个非常大的表示变换路径。

---

# 九、三个 MLP Projection 怎么理解？

不需要死抠名字。

### `up_proj`

大致把：

\[
d_{model}
\]

映射到更高的中间维度。

可以记成：

> **展开表示空间。**

---

### `gate_proj`

与门控激活一起：

> 决定哪些中间特征被激活和保留。

可以记成：

> **控制特征通路。**

---

### `down_proj`

最后把高维中间表示：

> 压回模型 Hidden Size。

可以记成：

> **把转换后的特征重新写回主表示流。**

因此：

```text
Attention
=
怎么读取上下文

MLP
=
读完以后怎样转换表示
```

作为长期直觉已经够用了。

---

# 十、所以 LoRA Target Modules 实际上有几种典型“范围”

为了建立清晰心智模型，可以把它分成三档。

### 窄范围

```text
q_proj
v_proj
```

特点：

> 参数少、实验简单、训练成本低。

适合：

> 做一个非常轻量的 Baseline。

---

### Attention 全投影

```text
q_proj
k_proj
v_proj
o_proj
```

意味着：

> 整个 Attention Projection 路径都获得 LoRA 适配能力。

相比 q/v：

> 修改范围更广。

---

### Attention + MLP

```text
q_proj
k_proj
v_proj
o_proj
gate_proj
up_proj
down_proj
```

这通常意味着：

> Transformer Layer 中主要 Linear Projection 都获得低秩适配能力。

适配容量明显更大。

同时：

> 参数量和训练成本也更高。

---

# 十一、为什么不能直接永远选择“全部 Linear”？

因为我们真正追求的是：

\[
\boxed{
MinimumSufficientAdaptation
}
\]

而不是：

\[
MaximumPossibleAdaptation
\]

例如：

```text
q/v 已经能让
Procurement Benchmark
达到目标
```

那么增加：

```text
k/o + MLP
```

如果没有明显业务收益，

就只是在增加：

```text
参数
成本
Checkpoint
实验复杂度
```

没有必要。

---

# 十二、反过来，为什么不能永远只用 `q_proj + v_proj`？

因为任务可能需要：

> 更广泛地调整 Transformer 内部表示。

如果出现：

```text
简单格式学会了

基础分类学会了

但复杂决策边界长期不足

增加 Rank 收益很小

数据与训练配置已确认正常
```

这时候真正的瓶颈可能不是：

> Adapter 不够宽。

而是：

> **允许修改的模型路径太窄。**

也就是：

# Module Coverage Bottleneck

这时候扩大 Target Modules：

> 可能比继续堆 Rank 更合理。

---

# 十三、Rank 和 Target Modules 是两个完全不同的扩容方向

这是今天最重要的工程判断之一。

### 增大 Rank

```text
原来的模块
装更宽的 Adapter
```

回答：

> **同一个地方多给一些修改容量。**

---

### 增加 Target Modules

```text
让更多模型路径
可以被修改
```

回答：

> **扩大可以动手术的位置。**

所以：

\[
\boxed{
IncreaseRank
\neq
IncreaseModuleCoverage
}
\]

一个是：

> 深一点。

一个是：

> 广一点。

---

# 十四、总 LoRA 参数量到底怎么计算？

如果 Target Modules 有多个，

总参数量大致就是：

\[
N_{\text{LoRA,total}}
=
\sum_{m\in M}
r_m
\left(
d_{in,m}+d_{out,m}
\right)
\]

其中：

\[
M
\]

就是：

> 所有 Target Modules。

如果所有模块 Rank 相同：

\[
r_m=r
\]

那么模块越多：

> 总可训练参数自然越多。

所以实际实验必须记录：

```text
Target Modules
+
Rank
+
Trainable Parameter Count
```

而不能只保存：

```text
r = 16
```

---

# 十五、这里还有一个重要现实：不同 Base Model 的模块名称并不完全一样

不要认为所有模型一定叫：

```text
q_proj
k_proj
v_proj
o_proj
```

有些架构：

> 名字不同。

有些：

> QKV 可能采用组合投影。

还有些模型使用：

```text
Grouped Query Attention
Multi-Query Attention
```

此时 Q、K、V 的维度甚至可能不同。

所以真正开始训练以前：

> **必须检查 `model.named_modules()` 或模型架构，而不是照抄别人模型的 `target_modules`。**

这是非常关键的工程习惯。

---

# 十六、最危险的 Bug：你以为装了 LoRA，其实根本没装到目标层

例如配置：

```python
target_modules=["q_proj", "v_proj"]
```

但当前 Base Model：

> 实际模块命名完全不同。

轻则：

> 框架直接报错。

更危险的情况是：

> 部分匹配错误或训练范围和预期不同。

所以训练前必须打印：

```text
Matched Target Modules
```

以及：

```text
Trainable Parameter Count
```

确认：

> LoRA 到底被插进了哪里。

---

# 十七、第一版 ProcurementLM 怎么选更专业？

不要一开始做几十组组合爆炸。

建议建立三档实验。

```text
Experiment A
Narrow Baseline

q_proj
v_proj
```

```text
Experiment B
Attention Coverage

q_proj
k_proj
v_proj
o_proj
```

```text
Experiment C
Broad Linear Coverage

q_proj
k_proj
v_proj
o_proj
gate_proj
up_proj
down_proj
```

然后：

> Rank、Alpha、Learning Rate 等主要变量尽量固定。

比较：

```text
Validation
Hard Negative
Boundary Case
General Capability Regression
Trainable Parameters
Training Cost
```

这才真正回答：

> 扩大修改范围是否值得。

---

# 十八、一个 ProcurementAI 的诊断例子

假设配置 A：

```text
q_proj + v_proj

r = 16
```

结果：

```text
输出格式             很好
简单风险识别         很好
Hard Negative        一般
复杂理由              一般
Boundary Case         较弱
```

第一反应不要立刻：

```text
r = 128
```

而应该建立两个假设：

```text
假设 1
当前模块已经合适
只是容量不够

→ 增大 Rank
```

```text
假设 2
修改路径太窄

→ 扩大 Target Modules
```

然后：

> 做控制变量实验。

这就是专业调参和“玄学调参”的区别。

---

# 十九、哪些东西第一版通常不要随便动？

例如：

```text
Embedding
LM Head
LayerNorm
```

不是说：

> 永远不能训练。

而是第一版 LoRA Baseline：

> 没有充分证据时，不要为了“多训练一些”随意把所有模块都纳入。

原因非常简单：

> 每增加一类 Trainable Scope，都增加新的实验变量。

第一版最重要的是：

# Attribution
## 可归因性

也就是：

> 模型为什么变好或变坏，我们能够解释。

---

# 二十、Target Modules 和模型能力不是一一对应关系

这是一个必须纠正的直觉。

不要说：

```text
q_proj
=
学习推理

v_proj
=
学习知识

MLP
=
储存知识
```

这种说法太绝对。

正确理解是：

> 不同模块承担不同数学计算角色，但最终语言能力、知识使用、推理行为都是整个 Transformer 联合形成的。

因此 Target Modules 选择：

> 不是把业务需求机械映射成某个单独矩阵。

而是：

> 决定允许哪些计算路径获得任务适配自由度。

---

# 二十一、我们现在可以建立一个非常清楚的调参顺序

不要这样：

```text
模型效果不好
↓
Rank改
Alpha改
Dropout改
Modules改
LR改
全部一起改
```

应该：

```text
Step 1
确认 Dataset / Mask / Training 正确

        ↓

Step 2
建立稳定 Target Module Baseline

        ↓

Step 3
确认 Rank 是否足够

        ↓

Step 4
如果出现 Module Coverage Bottleneck
再扩大 Target Modules

        ↓

Step 5
用 Benchmark 判断收益是否值得成本
```

这样每一次变化：

> 都有解释。

---

# 二十二、这一阶段最重要的“模块地图”

| 模块 | 所处位置 | 最简工程直觉 |
|---|---|---|
| `q_proj` | Attention | 当前表示怎样构造 Query |
| `k_proj` | Attention | 上下文怎样构造 Key 参与匹配 |
| `v_proj` | Attention | 被读取的信息携带什么表示 |
| `o_proj` | Attention | Attention 结果怎样写回主表示 |
| `gate_proj` | MLP | 中间特征怎样被门控 |
| `up_proj` | MLP | 怎样扩展到中间表示空间 |
| `down_proj` | MLP | 怎样压回 Hidden Size |

这张表不是让你背定义。

它是让你看到：

> **选择 Target Modules，其实是在选择允许修改 Transformer 的哪些计算路径。**

---

# 二十三、本阶段工程产物：`LoRATargetModulePolicy_V0.1`

正式记录至少应该包括：

```text
base_model
base_model_revision

architecture_family

available_linear_modules

target_modules

excluded_modules

target_layer_scope

rank
alpha
dropout

matched_module_count

trainable_parameter_count
trainable_parameter_ratio

target_module_policy_version
```

训练启动前必须额外验证：

```text
1. 配置中的模块名称真实存在

2. 匹配数量符合预期

3. Trainable Parameter Count 符合预期

4. Base Parameters 仍正确 Frozen

5. Adapter 确实只出现在目标模块
```

这一步叫：

# Adapter Injection Audit
## Adapter 注入审计

---

# 二十四、本阶段最危险的 6 个反例

**第一，只看 Rank，不看 Target Modules。**  
LoRA 总容量同时取决于“每个 Adapter 多宽”和“装了多少位置”。

**第二，认为 q/k/v/o 都做同一件事。**  
它们处于 Attention 的不同变换阶段。

**第三，认为 MLP 只是附属模块。**  
它是 Transformer 中极大的表示变换路径之一。

**第四，一上来就 `all-linear`，然后发现效果好，却不知道究竟哪些模块带来了收益。**  
失去实验可归因性。

**第五，把别的模型的 `target_modules` 原样复制。**  
不同架构的模块命名和形状可能不同。

**第六，配置写完以后不检查真正 Trainable Parameters。**  
你以为在训练的东西和实际训练的东西可能不是一回事。

---

# 二十五、现在把本阶段压成最精准的 5 句话

> **第一，Rank 决定 LoRA 在一个目标矩阵上“能改多宽”，Target Modules 决定 Transformer “哪些计算路径允许被改”。**

> **第二，`q/k/v/o` 分别参与 Attention 的 Query、Key、Value 和输出投影；MLP 的 `gate/up/down` 则参与后续非线性表示转换。**

> **第三，增加 Rank 和增加 Target Modules 是两种不同扩容方式：一个增加局部容量，一个扩大修改覆盖范围。**

> **第四，更多 Target Modules 会增加可训练参数和适配自由度，但是否带来真实业务收益必须由 Validation、Hard Case 和成本共同判断。**

> **第五，永远不要照抄模块名称；训练前必须检查模型真实架构、实际匹配模块和 Trainable Parameter Count。**

如果这五句能脱口而出：

> Target Modules 就不再是配置文件里一串莫名其妙的字符串。

---

# 二十六、本阶段最核心的一张图

```text
                     Transformer Layer
                            │
            ┌───────────────┴───────────────┐
            │                               │
            ▼                               ▼
        Attention                          MLP
            │                               │
   ┌────────┼────────┐             ┌────────┼────────┐
   ▼        ▼        ▼             ▼        ▼        ▼
 q_proj   k_proj   v_proj       gate      up       down
   │                 │
   └────── o_proj ───┘
            │
            ▼
       Target Modules
            │
      哪些位置加 LoRA？
            │
            ▼
   Frozen W + ΔW=BA
            │
            ▼
       Trainable Scope
            │
     ┌──────┴───────┐
     ▼              ▼
  Rank              Module Coverage
局部容量             修改范围
     │              │
     └──────┬───────┘
            ▼
     Validation / Hard Case
            │
            ▼
   是否值得扩大修改范围？
```

脑中只记：

> **Rank 决定“改多宽”，Target Modules 决定“改哪里”。**

---

# 二十七、本阶段掌握测试

现在不回看正文，你应该能自己解释：Target Modules 到底决定什么；为什么它和 Rank 不是同一个超参数；`q_proj / k_proj / v_proj / o_proj` 在 Attention 中分别处于什么位置；为什么不能简单说“Q 是推理、V 是知识”；MLP 的 `gate/up/down` 大致完成什么计算；为什么 `q+v`、完整 Attention、Attention+MLP 是不同的适配范围；为什么增加 Rank 和增加 Target Modules 是两种不同的扩容方式；为什么模型效果不足不能总靠提高 Rank；什么叫 Module Coverage Bottleneck；为什么不同 Base Model 不能照抄同一组模块名称；为什么训练前必须检查实际匹配模块和 Trainable Parameter Count；为什么第一版不应该没有证据就随便训练 Embedding、LM Head 等更多模块；以及为什么最终模块选择必须回到固定 Benchmark 上验证。

如果这些能够自己讲清楚：

\[
\boxed{
第五课第8阶段真正掌握
}
\]

---

# 本阶段最后只记一句话

> **LoRA 不只是决定“用多大的 Adapter”，还必须决定“把 Adapter 装在哪里”：Rank 控制每个低秩更新的容量，Target Modules 控制哪些 Transformer 计算路径获得领域适配权；专业的模块选择不是把 `q_proj/v_proj` 当口诀，而是先看真实模型架构，再通过可归因的控制实验验证修改范围是否真正改善 Procurement Benchmark。**

---

# 下一阶段：第五课 · 第 9 阶段
# QLoRA 与 4-bit / NF4
## 为什么 Base Model 可以用 4-bit 加载，却仍然能够训练出高质量 LoRA Adapter？

现在我们已经知道：

```text
Base Model
Frozen

+

选定 Target Modules
安装 LoRA

+

A / B
真正训练
```

但还有一个大头：

> **Frozen Base Model 虽然不更新，它依然占显存。**

第 9 阶段会解决：

```text
7B / 14B Base Model
        ↓
4-bit Quantization
        ↓
NF4
        ↓
低显存保存 Frozen Base
        +
BF16 / FP16 等计算路径
        +
LoRA Adapter 继续训练
```

最后真正建立：

> **量化的是谁、谁仍然训练、计算时为什么还能保持足够精度——这三件事必须彻底分开。**

---
