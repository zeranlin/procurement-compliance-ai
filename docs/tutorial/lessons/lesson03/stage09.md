# 第三课 · 第 9 阶段：从“模型能跑”到“模型服务能用”
## TTFT、TPS、Latency、Throughput、Batching、Continuous Batching、vLLM 与 PagedAttention 到底在解决什么？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Latency ≠ Throughput。单个用户等多久与服务器单位时间处理多少请求是不同指标。**
2. **TTFT ≠ Decode Speed。首 Token 等待时间和后续 Token 流速来自不同阶段瓶颈。**
3. **Batching 可以提高 GPU 利用率和吞吐，但过度 Batch 也可能增加排队与单请求延迟。**
4. **Continuous Batching / PagedAttention 的价值在于动态请求与 KV Cache 管理，不是改变模型能力。**
5. **Serving Benchmark 必须使用真实输入长度、输出长度、并发和 P95/P99，而不是只看一个 tokens/s。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Batch` | 批次：一次参与计算的一组样本 |
| `TTFT` | 首 Token 时间：用户等待第一个输出 Token 的时间 |
| `Throughput` | 吞吐：单位时间内处理请求或生成 Token 的能力 |
| `Latency` | 延迟：单个请求从进入到完成的时间 |
| `Attention` | 注意力：根据内容相关性动态聚合信息 |
| `Continuous Batching` | 连续批处理：动态把不同时间到达的请求加入 GPU 批次 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |
| `KV Cache` | KV 缓存：生成时缓存历史 Key/Value 以减少重复计算 |
| `Serving` | 服务化：把模型包装成可扩展、可观测、可治理的在线服务 |
| `Inference` | 推理：系统接收请求并产生结果的在线计算过程 |

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

到第 8 阶段为止，我们已经解决了一个人的问题：

```text
一个用户
    ↓
一个Prompt
    ↓
模型
    ↓
一个Token一个Token生成
    ↓
得到回答
```

如果我们只是坐在电脑前：

> 自己测试模型，

到这里似乎已经够了。

但政府采购 AI 最终不是：

> 一个人在 Jupyter Notebook 里玩模型。

而是可能变成：

```text
采购人A ─┐
代理机构B ─┤
审查人员C ─┤
专家D     ─┼──→ ProcurementAI
监管人员E ─┤
……       ─┘
```

这时候问题完全变了。

我们不再只问：

> **模型能不能生成答案？**

而是开始问：

> **第一个字多久出来？**

> **后面生成快不快？**

> **10个人一起问会怎样？**

> **50个人一起上传长文件会怎样？**

> **GPU 有没有大量时间其实在浪费？**

> **KV Cache 怎么管理才不会把显存弄得一地碎片？**

这一阶段，就是从：

# Model Inference

第一次真正走向：

# Inference Serving

---

# 一、本阶段先只建立 6 个核心心智模型

先不要背任何框架名字。

这一阶段最重要的是下面六句话：

```text
① TTFT
=
用户等多久看到第一个Token

② TPS
=
第一个Token出来以后，后续Token吐得有多快

③ Latency
=
一个请求从进入系统到完成，总共等多久

④ Throughput
=
整套系统单位时间能处理多少工作

⑤ Batching
=
让很多请求一起使用GPU，
避免GPU只服务一个人

⑥ vLLM / PagedAttention这一类技术
=
主要是在提高“服务效率”和“KV内存利用率”
不是让模型Weight突然变聪明
```

先把这六根柱子立住。

---

# 二、先看一个最生活化的场景：政府办事大厅

想象一个办事大厅。

只有一个窗口。

来了一个人：

```text
用户A
```

窗口人员给他处理业务。

三分钟完成。

你会觉得：

> 挺快。

---

# 三、现在突然来了 50 个人

```text
A
B
C
D
E
...
第50个人
```

窗口工作人员的能力：

> 完全没变。

但系统体验：

> 彻底变了。

为什么？

因为现在除了：

> “一个业务办得有多快”

还多了：

> “大家要排多久队”。

这就是模型服务与单模型测试的区别。

---

# 四、一个 LLM 服务请求实际上有很多时间组成

用户点击：

> “开始审查”

到最终报告完成，

可以粗略想成：

```text
用户提交请求
      │
      ▼
排队
      │
      ▼
Prompt进入GPU
      │
      ▼
Prefill
      │
      ▼
第一个Token出现
      │
      ▼
Decode
Token
Token
Token
...
      │
      ▼
回答完成
```

于是：

> “模型速度”

根本不是一个单一数字。

---

# 五、第一个核心指标：TTFT

# Time To First Token

可以直接翻译：

> **从用户提交请求，到看到第一个生成 Token，需要多久。**

例如：

```text
点击“开始审查”
       │
       │ 2.3 秒
       ▼
“该……”
 ↑
第一个Token
```

那么：

```text
TTFT ≈ 2.3秒
```

---

# 六、为什么 TTFT 对用户体验特别重要？

想象两个系统。

### 系统 A

点击以后：

```text
0.8秒
```

就开始：

> “该条款……”

然后慢慢继续生成。

---

### 系统 B

点击以后：

```text
12秒
```

屏幕完全没动静。

然后突然高速生成。

---

多数用户会觉得：

> A 更“灵”。

哪怕最终整篇报告完成时间：

> 未必差很多。

---

# 七、TTFT 主要发生在哪一段？

最重要的一段就是我们第五阶段学过的：

# Prefill

也就是：

> 先处理整个 Prompt。

---

# 八、短 Prompt 和长 Prompt 的区别

用户 A：

```text
请判断以下资格条件是否合理。
```

可能只有：

```text
几十Token
```

---

用户 B：

上传：

```text
180页招标文件
+
法规证据
+
系统Prompt
```

可能变成：

```text
几十K Token
```

---

第二个请求在模型生成第一个 Token 之前：

> 必须先读完整个输入。

所以通常：

```text
Prompt更长
↓
Prefill工作更多
↓
TTFT更长
```

---

# 九、把 Prefill 想成专家“先读材料”

你把一页材料交给专家：

> 很快开始回答。

你把 400 页材料交给专家：

> 他不可能第 0.1 秒就开始给最终结论。

至少要：

> 先阅读。

LLM 也是一样。

---

# 十、所以 ProcurementAI 第一个非常现实的问题出现了

如果用户上传：

> 整本采购文件，

我们不能只问：

```text
模型支持128K吗？
```

还要问：

```text
128K Prefill
用户要等多久？
```

这就是：

> **Context 能塞进去**

和：

> **Context 实际好不好用**

之间的区别。

---

# 十一、第二个指标：TPS

第一个 Token 出来以后，

系统开始：

```text
Token
Token
Token
Token
Token
```

连续生成。

这时我们关注：

# Tokens Per Second

简称：

# TPS

---

# 十二、例如

模型 1 秒钟：

> 生成 50 个 Token。

可以粗略说：

```text
50 token/s
```

---

# 十三、TPS 是“阅读前”还是“写答案”速度？

更直觉地说：

> TPS 主要让你感受模型 **后续写答案有多快**。

而 TTFT：

> 更像模型 **开始说话前要准备多久**。

---

# 十四、用采购专家类比

### TTFT

像：

> 专家看完材料以后，多快开始开口。

### TPS

像：

> 专家开始说以后，说话速度多快。

这两个指标：

> 完全不是一回事。

---

# 十五、来看两个模型

### 模型 A

```text
TTFT = 1秒
TPS  = 20 token/s
```

### 模型 B

```text
TTFT = 5秒
TPS  = 80 token/s
```

哪个更快？

答案：

> **问题问得不完整。**

---

# 十六、如果只回答 20 Token

模型 A：

> 很可能体验更好。

因为 B：

> 光准备就等 5 秒。

---

# 十七、如果要生成 5000 Token 长报告

模型 B：

> 后续生成速度巨大优势可能逐渐体现出来。

所以：

\[
\boxed{
Prompt长度
+
Output长度
}
\]

会影响：

> 用户到底更在意 TTFT 还是 TPS。

---

# 十八、第三个指标：Latency

Latency：

> **一个请求从进入系统，到得到所需结果，要等多久。**

这是一个更完整的概念。

---

# 十九、不要把 Latency 只理解成模型 Forward 时间

真实请求可能经历：

```text
请求进入
  ↓
排队
  ↓
Tokenizer
  ↓
Prefill
  ↓
Decode
  ↓
后处理
  ↓
JSON校验
  ↓
Citation验证
  ↓
最终返回
```

全部加起来：

> 才是用户真正体验到的等待时间。

---

# 二十、所以一个非常重要的心智模型

可以把总等待时间粗略看成：

```text
Total Latency
=
Queue Time
+
Prefill Time
+
Decode Time
+
其它系统开销
```

这不是要你背公式。

只是告诉你：

> “慢”可能慢在不同位置。

---

# 二十一、一个 ProcurementAI 案例

用户说：

> “为什么模型今天这么慢？”

你不能马上回答：

> “GPU 不够快。”

可能实际是：

```text
GPU Forward      很快
但前面排队       18秒
```

真正的问题：

> 并发调度。

---

# 二十二、另一个案例

排队只有：

```text
0.1秒
```

但用户上传：

```text
100K Token
```

Prefill：

> 非常长。

这时真正的问题：

> Context / Prefill。

---

# 二十三、再一个案例

Prompt 很短。

但要求：

> 生成 6000 Token 审查报告。

TTFT：

> 很快。

最后完成：

> 很慢。

问题主要：

# Decode

---

# 二十四、所以以后排查性能第一件事不是问

> “模型快不快？”

而应该拆成：

```text
Queue慢？

Prefill慢？

Decode慢？

还是后处理慢？
```

这和之前显存阶段：

> 先找 dominant term

是同一种专家思维。

---

# 二十五、第四个指标：Throughput

Throughput 可以翻译成：

> **吞吐量。**

它回答的是：

> 整套系统单位时间能够完成多少工作。

---

# 二十六、例如

系统 A：

```text
每秒总共生成50 Token
```

系统 B：

```text
每秒总共生成500 Token
```

B：

> 整体吞吐更高。

---

# 二十七、也可以用 Request 来衡量

例如：

```text
每分钟完成100个请求
```

或者：

```text
每秒处理20个请求
```

取决于：

> 业务定义。

---

# 二十八、Latency 与 Throughput 不是同一个东西

这是本阶段特别重要的一组区别。

### Latency

关心：

> **一个用户等多久。**

### Throughput

关心：

> **整个系统一小时能服务多少用户。**

---

# 二十九、用高速公路类比

Latency：

> 一辆车从入口到出口要多久。

Throughput：

> 一小时能通过多少辆车。

---

# 三十、一条车道可能单车很快

但只能：

> 一辆一辆过。

所以：

> 单请求 Latency 很漂亮，

系统 Throughput：

> 可能很差。

---

# 三十一、这就是很多“跑分视频”容易误导的地方

有人展示：

```text
一个用户
一个Prompt
一张GPU
```

然后说：

> “模型每秒 70 Token，非常快。”

这只能说明：

> 单请求某种条件下挺快。

并不能说明：

> 100 个用户来时系统仍然很好。

---

# 三十二、现在终于进入 Batching

GPU 有一个特点：

> 它特别擅长做大量并行计算。

如果你每次只给 GPU：

> 一丁点工作，

它很多计算单元：

> 可能吃不饱。

---

# 三十三、想象一个 100 人大厨房

你有：

> 100 个厨师。

但现在每次只进来：

> 1 个三明治订单。

于是：

```text
1个厨师工作
99个厨师发呆
```

很浪费。

---

# 三十四、如果一次来了 32 个订单

可以：

> 同时处理。

GPU 利用率：

> 可能明显提高。

这就是 Batching 的第一层直觉。

---

# 三十五、Batching 不是让模型变聪明

Batching 改变的是：

> **我们怎样把工作交给 GPU。**

不是：

> Weight。

所以：

```text
Batching
=
Serving Efficiency
```

不是：

```text
Model Intelligence
```

---

# 三十六、最简单的 Static Batching

假设系统规定：

> 凑齐 8 个请求，再一起运行。

```text
A ┐
B │
C │
D ├──→ Batch 8 → GPU
E │
F │
G │
H ┘
```

这样可以：

> 提高并行效率。

---

# 三十七、但马上出现一个问题

请求 A：

```text
输出50 Token
```

请求 B：

```text
输出3000 Token
```

请求 C：

```text
输出200 Token
```

---

# 三十八、谁先结束？

A：

> 很快。

但如果是传统固定 Batch 思维，

可能出现：

> A 已经没事干了，但这个 Batch 还被 B 拖着。

这就是一种：

# Waste

---

# 三十九、用旅游大巴理解 Static Batch

8 个人坐一辆大巴。

规则：

> 必须所有人办完事，大巴才能走。

---

### A

办事：

> 5分钟。

### B

办事：

> 2小时。

---

结果 A：

> 等 B 两小时。

整个资源利用：

> 很差。

---

# 四十、而 LLM 请求天然就是“长短不一”

因为每个用户：

- Prompt 长度不同；
- Output 长度不同；
- EOS 出现时间不同。

所以：

> 固定 Batch 非常别扭。

---

# 四十一、这就引出 Continuous Batching

名字看起来复杂。

其实直觉非常简单：

> **谁结束了，谁就退出；有新请求，就尽快补进来。**

---

# 四十二、还是一辆动态公交

开始：

```text
A
B
C
D
```

一起在 GPU 上跑。

---

## 1. A 先结束

A 下车。

马上有：

```text
E
```

进入。

现在：

```text
B
C
D
E
```

继续。

---

## 2. C 又结束

C 下车。

新请求：

```text
F
```

加入。

---

# 四十三、这就是 Continuous 的感觉

不是：

```text
一批开始
↓
必须整批全部结束
↓
下一批才能开始
```

而更像：

```text
GPU始终保持一个动态工作池

完成一个
↓
腾出位置

新请求
↓
及时补进来
```

---

# 四十四、这对 LLM 特别合适

因为 Decode 本来就是：

```text
一步
生成一个Token

下一步
再生成一个Token
```

所以推理引擎有机会在：

> 多个请求之间动态调度。

---

# 四十五、第五个核心心智模型正式出现

\[
\boxed{
ContinuousBatching
=
把GPU当成持续运行的公共服务平台
而不是一批一批死等
}
\]

---

# 四十六、政府采购大厅类比

传统 Static Batch：

> 每 10 个人一组。

只要其中一个：

> 业务特别复杂，

另外 9 个：

> 都跟着等。

---

Continuous Batching：

> 谁办完谁走。

新的人：

> 有窗口就补进来。

所以整个大厅：

> 更高效。

---

# 四十七、为什么 Throughput 会提高？

因为 GPU：

> 更少时间闲着。

同样一小时：

> 可以处理更多 Token / 请求。

所以 Continuous Batching 主要优化：

# System Utilization

---

# 四十八、但 Throughput 提高是不是一定让每个用户都更快？

不一定。

这是一个非常重要的 Trade-off。

---

# 四十九、假设 GPU 同时服务很多用户

优点：

> 总吞吐高。

但每个人：

> 可能要和别人分享 GPU 时间。

于是某些情况下：

> 单用户 TPS 可能下降。

---

# 五十、所以又出现一组经典矛盾

```text
单用户极致速度
vs
整机最大吞吐
```

这两个目标：

> 不总是一致。

---

# 五十一、这就是为什么生产推理需要 Scheduler

Scheduler：

> 调度器。

它决定：

```text
谁先上GPU？

谁继续生成？

谁暂时等待？

一次允许多少Sequence？

Prefill和Decode怎么排？
```

---

# 五十二、Scheduler 像大厅叫号系统

不是模型专家本身。

它负责：

> **谁什么时候得到服务资源。**

所以：

```text
Scheduler
≠
LLM
```

---

# 五十三、一个很重要的问题：Prefill 和 Decode 的计算特征不太一样

不用进入 GPU 微架构。

只先建立直觉。

### Prefill

一次处理：

> 很多输入 Token。

可以形成：

> 较大的矩阵计算。

通常更加：

> Compute-heavy。

---

### Decode

每一步：

> 每个 Sequence 只增加少量新 Token。

却需要不断：

> 读取大量 Weight 和 KV。

很多场景下会更加受：

> Memory Bandwidth

影响。

---

# 五十四、用专家办公室类比

Prefill：

> 一次性读一大摞文件。

Decode：

> 每写一句话，都不断回头查自己的知识和已经读过的笔记。

两者工作模式：

> 不一样。

---

# 五十五、所以 Prefill 和 Decode 会争 GPU

假设正在有 20 个用户：

> 一个 Token 一个 Token Decode。

突然来了用户 X：

```text
100K Token Prompt
```

X 的 Prefill：

> 是一大坨工作。

---

# 五十六、如果系统让 X 一口气霸占 GPU

其他正在聊天的人可能感觉：

> 突然卡住。

这就是服务系统中的：

# Scheduling Problem

---

# 五十七、这有点像高速公路突然来了一辆超长车队

原来：

> 大家平稳通过。

突然：

> 100 辆重型卡车一起占道。

其它小车：

> 延迟暴涨。

---

# 五十八、所以好的推理服务不仅要“Batch”

还要考虑：

> **Batch 谁、什么时候 Batch、Prefill 怎么切、Decode 怎么公平调度。**

这已经开始进入真正的系统工程。

---

# 五十九、现在回到第 7 阶段的 KV Cache

每一个活跃用户都有：

> 自己的 KV Cache。

比如：

```text
User A → KV_A
User B → KV_B
User C → KV_C
User D → KV_D
```

随着：

> 请求不断进入、结束，

这些 Cache：

> 不断申请、增长、释放。

---

# 六十、如果内存管理很笨，会发生什么？

想象一块显存：

```text
[AAAAAA][BBBBBBBB][CCCC][DDDDDD]
```

A 完成了。

释放：

```text
[      ][BBBBBBBB][CCCC][DDDDDD]
```

---

# 六十一、后来 C 又完成

```text
[      ][BBBBBBBB][    ][DDDDDD]
```

现在总空闲：

> 可能不少。

但空位：

> 被切成很多小块。

这就是我们第 7 阶段说过的：

# Fragmentation

---

# 六十二、然后来了一个长请求 E

它想要一大块连续空间。

虽然：

> 总空闲显存够，

但：

> 连续的大块不够。

结果：

> 内存利用很差甚至 OOM。

---

# 六十三、这就是为什么 KV Cache 管理非常关键

它不是：

> 一个小附件。

在长 Context、多并发服务中，

KV Cache 可能就是：

> 显存调度的核心对象之一。

---

# 六十四、现在进入 PagedAttention 的核心直觉

先不要看论文公式。

只看名字：

# Paged

分页。

这个思想和操作系统管理内存：

> 很像。

---

# 六十五、传统思路像给每个用户一整套连续房间

用户 A 预计可能需要：

```text
100个房间
```

于是提前：

> 给他留 100 个连续房间。

但他最后只用了：

```text
20个
```

剩下 80：

> 被浪费。

---

# 六十六、Paged 的思路

不要提前要求：

> 一整块连续大空间。

而是把 KV Cache 切成很多：

# Blocks / Pages

---

# 六十七、像一本活页夹

用户 A：

```text
Block 7
Block 9
Block 31
Block 42
```

虽然这些 Block：

> 在物理显存里不连续，

系统仍然知道：

> 它们逻辑上属于 A 的连续上下文。

---

# 六十八、用户 B 可能占

```text
Block 2
Block 8
Block 15
```

也不需要：

> 挨在一起。

---

# 六十九、所以 PagedAttention 最值得记的不是 Attention 公式

而是：

\[
\boxed{
KV逻辑上连续
不要求物理显存里必须整块连续
}
\]

这是最重要的直觉。

---

# 七十、用政府档案库理解

以前：

> 一个项目必须占一个完整柜子。

项目只有 10 页：

> 也占一整柜。

非常浪费。

---

Paged 思路：

> 每个项目按照文件盒分页存放。

比如项目 A：

```text
盒17
盒21
盒38
```

系统目录知道：

> 这三个盒子都属于项目 A。

所以：

> 不必物理连续。

---

# 七十一、这样有什么好处？

主要直觉上有三个：

```text
① 减少大块连续预留浪费

② 减轻显存碎片问题

③ 更灵活地让KV随着Sequence增长
```

---

# 七十二、注意：PagedAttention 不会让 KV Cache 消失

它做的不是：

```text
原本10GB KV
↓
突然变0GB
```

而是：

> **把显存管理得更聪明。**

---

# 七十三、这和第 6 阶段 Quantization 是完全不同的问题

Quantization：

> 改变一个数字占多大。

PagedAttention：

> 改变这些数据怎么组织和分配内存。

---

# 七十四、两者可以同时存在

例如：

```text
4-bit Weight
+
高效KV管理
```

一个优化：

> Weight。

一个优化：

> Runtime KV Memory。

不是二选一。

---

# 七十五、现在终于可以理解 vLLM 是什么角色

不要先把 vLLM 理解成：

> 一个新模型。

它不是：

```text
Llama
Qwen
Mistral
```

这种 Model Weight。

---

# 七十六、vLLM 更像什么？

可以先理解成：

> **专门负责让 LLM 高效提供推理服务的一套引擎。**

也就是：

```text
用户请求
   ↓
vLLM等Inference Engine
   ↓
调度 / Batching / KV管理
   ↓
真正的Model Weight
   ↓
GPU
```

---

# 七十七、所以如果你用同一个模型

方案 A：

```text
Transformers
单请求简单generate
```

方案 B：

```text
高性能Inference Engine
```

模型 Weight：

> 可以完全一样。

业务质量：

> 理论上核心模型没有因为换 Serving Engine 就突然学会新知识。

但：

> 系统吞吐和资源利用可能差非常多。

---

# 七十八、这就是第六个核心心智模型

\[
\boxed{
ServingEngine
\neq
ModelIntelligence
}
\]

它主要解决：

> **如何更有效率地运行模型。**

---

# 七十九、一个采购大厅总类比

现在我们把整个 Stage 9 都放进一个大厅。

### Model Weight

> 专家团队。

### GPU

> 专家所在的办事大厅。

### KV Cache

> 每个案件的临时工作档案。

### Scheduler

> 叫号系统。

### Continuous Batching

> 有空位就让下一案件进来。

### PagedAttention

> 案件档案不用强制占连续完整柜子，而是分页灵活存储。

### vLLM

> 整套高效率办事大厅管理系统之一。

这张类比，基本可以贯穿本阶段。

---

# 八十、现在区分四个性能指标

把它们放一张图：

```text
用户发请求
    │
    │<------ TTFT ------->
    ▼
第一个Token
    │
    │ Token Token Token...
    │<--- TPS描述这一段 --->
    ▼
回答完成


从请求进入
一直到回答完成
<------ Latency ------>


整个服务器
单位时间处理多少请求/Token
<------ Throughput ------>
```

这张图要记牢。

---

# 八十一、一个具体数字案例

系统 A：

```text
TTFT = 1秒
TPS = 25 token/s
```

输出：

```text
500 Token
```

粗略感觉：

> 先等 1 秒，

然后后面约：

> 20 秒左右生成。

总时间：

> 约 21 秒级别，再加其它开销。

---

# 八十二、系统 B

```text
TTFT = 5秒
TPS = 100 token/s
```

同样 500 Token：

> 先等 5 秒，

后面约：

> 5 秒。

总共：

> 约 10 秒级别。

---

# 八十三、如果只输出 20 Token 呢？

A：

> 可能用户感觉更灵。

B：

> 5 秒第一字等待反而明显。

所以性能指标一定要和：

> **真实工作负载**

一起看。

---

# 八十四、这也是为什么 Benchmark 不能只给一个 TPS

如果别人告诉你：

```text
模型速度 = 100 token/s
```

你至少还应该问：

```text
什么GPU？

什么Model？

什么Precision？

Prompt多长？

Output多长？

Batch是多少？

并发是多少？

是单请求TPS还是系统总吞吐？

TTFT是多少？
```

否则这个数字：

> 很容易失去意义。

---

# 八十五、采购 AI 的 Benchmark 更不能只测“Hello”

真实用户可能输入：

### Case A

```text
200 Token
```

一个资格条件。

### Case B

```text
8K Token
```

一章采购需求。

### Case C

```text
32K Token
```

完整文件片段。

### Case D

```text
长Prompt
+
长RAG证据
+
2000 Token报告
```

性能：

> 会完全不同。

---

# 八十六、所以我们未来至少要建立几类 Workload

```text
短输入 + 短输出

长输入 + 短输出

短输入 + 长输出

长输入 + 长输出
```

这四类：

> 对系统压力完全不同。

---

# 八十七、长输入 + 短输出

例如：

> 审查 100 页文件，只输出 5 个风险点。

特点：

```text
Prefill重
Decode较轻
```

更关注：

> TTFT。

---

# 八十八、短输入 + 长输出

例如：

> 给一个项目概要，生成 3000 Token 审查报告。

特点：

```text
Prefill轻
Decode重
```

更关注：

> TPS 和总 Latency。

---

# 八十九、长输入 + 长输出

这个最狠。

例如：

```text
30K采购文件
+
5K法规证据
+
输出4K审查报告
```

它同时压力：

```text
Prefill
+
KV Cache
+
Decode
```

这才接近很多真实采购 AI 工作负载。

---

# 九十、现在说 Queueing

单用户测试：

> 没有排队。

生产：

> 有排队。

---

# 九十一、假设一张 GPU 每秒最多服务某个负载

突然在 1 秒钟内来了：

```text
100个请求
```

GPU 不可能：

> 同时无限处理。

所以一部分：

> 必须排队。

---

# 九十二、排队会让 TTFT 变差

注意：

用户感受到的“第一字等待”在产品层面可能包括：

```text
Queue Time
+
Prefill Time
```

所以即使模型 Prefill 很快，

队伍太长：

> 用户仍然觉得慢。

---

# 九十三、这就是为什么平均值不够

假设：

```text
平均TTFT = 2秒
```

听起来很好。

但真实可能是：

```text
90%用户：1秒

最后10%用户：12秒
```

那一部分用户：

> 体验很差。

---

# 九十四、因此生产性能经常看 Percentile

例如：

```text
P50
P95
P99
```

先只理解直觉。

---

# 九十五、P50

大约：

> 一半用户比它快，一半比它慢。

可以把它理解成：

> 典型用户体验。

---

# 九十六、P95

大约：

> 95% 的请求都不比这个值更慢太多。

更能看：

> 较差用户的体验。

---

# 九十七、P99

关注：

> 尾部极慢请求。

对于生产系统，

这种：

# Tail Latency

很重要。

---

# 九十八、为什么政府采购系统尤其不能只看平均值？

因为某个特别大的采购文件：

> 可能把队列堵住。

普通请求：

> 也被拖慢。

如果只看平均：

> 可能掩盖问题。

---

# 九十九、一个“超长文件堵大厅”的例子

正常请求：

```text
2K Token
```

突然来了一个：

```text
120K Token
```

如果调度器处理不合理，

这个大 Prefill：

> 可能对其它用户产生明显影响。

这类似：

# Head-of-Line Blocking

---

# 一百、直觉是什么？

排队第一位：

> 是一个超级复杂案件。

后面：

> 20 个简单案件。

如果规则是：

> 必须第一个完全办完，后面才能开始，

所有简单案件：

> 都被拖死。

---

# 一百零一、优秀 Scheduler 要尽量避免这种低效

也就是说：

> 不只是追求 GPU 100% 忙，

还要兼顾：

- 公平；
- 响应时间；
- 长短请求；
- Prefill / Decode 混合。

所以：

> Serving 是一个调度问题。

---

# 一百零二、这和操作系统越来越像了

一个 LLM Serving Engine 其实在同时管理：

```text
计算资源
+
显存
+
请求队列
+
KV Cache
+
执行顺序
```

这已经不只是：

> “调用 model.generate()”。

---

# 一百零三、为什么 Hugging Face `generate()` 仍然很重要？

因为学习、实验、单请求验证时：

> 它简单、直观。

我们的课程前面用它：

> 非常合适。

---

# 一百零四、但为什么生产可能需要专门推理引擎？

因为生产目标变成：

```text
多人
+
高吞吐
+
低延迟
+
长Context
+
更高GPU利用率
```

这不是简单：

> 多写一个 for 循环

就能解决。

---

# 一百零五、所以不要形成另一个极端

不是：

> “Transformers 不专业，vLLM 才专业。”

而是：

```text
不同工具
适合不同阶段
```

---

# 一百零六、学习阶段

我们需要：

```text
容易看懂
容易调试
容易观察Tensor
```

简单框架：

> 很有价值。

---

# 一百零七、生产服务阶段

我们开始追求：

```text
Batching
Scheduling
KV管理
并发
吞吐
```

专业 Serving Engine：

> 价值开始变大。

---

# 一百零八、这是“开发环境”和“生产环境”的区别

开发：

> 追求理解和可调试性。

生产：

> 追求可靠、稳定、高利用率。

不要过早：

> 把所有生产优化塞进第一天学习。

---

# 一百零九、现在回到 ProcurementAI

假设我们未来有：

```text
100个采购单位
```

每天提交：

> 采购文件风险审查。

如果每个用户都独占：

> 一套 14B 模型，

成本会非常夸张。

---

# 一百一十、更合理的方向

通常希望：

```text
一套或多套共享Model Weight
        │
        ├─ User A KV
        ├─ User B KV
        ├─ User C KV
        └─ ...
```

然后推理引擎：

> 动态调度。

---

# 一百一十一、这就是为什么 Stage 7 和 Stage 9 是连续的

Stage 7 问：

> 显存里装了什么？

Stage 9 问：

> **这些显存资源怎么在很多请求之间高效使用？**

---

# 一百一十二、一个非常重要的系统公式不需要公式

可以直接记成：

```text
单请求性能
≠
多用户服务能力
```

再重复一遍：

\[
\boxed{
SingleRequestSpeed
\neq
ServingCapacity
}
\]

---

# 一百一十三、为什么一张 GPU TPS 很高，Throughput 仍可能不高？

如果它始终：

> 一次只服务一个请求，

GPU 并行能力：

> 没有被充分利用。

---

# 一百一十四、为什么 Throughput 很高，某用户却觉得慢？

因为系统：

> 同时服务很多请求。

单个请求可能：

> 得不到全部 GPU 资源。

这就是：

```text
Throughput
vs
Latency
```

Trade-off。

---

# 一百一十五、生产系统真正要优化的是“业务 SLA”

SLA 先简单理解成：

> 我们承诺什么体验。

例如未来可以设想：

```text
普通条款审查
第一Token P95 < 某阈值

完整文件审查
总报告完成 < 某阈值

系统
支持至少某并发
```

具体数字：

> 必须靠真实 Benchmark 决定。

现在不先拍脑袋。

---

# 一百一十六、为什么不能先定“100用户并发”？

因为：

> “100 个用户”本身信息不够。

100 个用户如果都只发：

```text
20 Token Prompt
```

与 100 个用户都发：

```text
50K Token文件
```

是两个世界。

---

# 一百一十七、所以并发容量必须带 Workload

更专业的描述是：

```text
在什么输入长度
什么输出长度
什么模型
什么精度
什么硬件

条件下
支持多少并发
```

---

# 一百一十八、未来我们的 Procurement Benchmark 不仅测质量

还应该同时记录：

```text
Quality
+
TTFT
+
TPS
+
Latency
+
Throughput
+
Peak VRAM
```

这才接近：

> 真正模型选型。

---

# 一百一十九、为什么“最聪明模型”不一定是最佳生产模型？

假设：

### Model A

业务准确率：

```text
94%
```

但：

```text
只能2并发
TTFT很高
需要4张GPU
```

---

### Model B

业务准确率：

```text
93.5%
```

但：

```text
支持20并发
TTFT低
1张GPU
```

如果 B 已经超过业务质量门槛：

> 它可能更有价值。

---

# 一百二十、这是再次回到 Pareto 思维

系统设计不是只追：

```text
最高Accuracy
```

而是：

```text
Quality
Cost
Latency
Throughput
VRAM
Reliability
```

共同优化。

---

# 一百二十一、现在做一个完整“办事大厅”总图

```text
                    用户请求
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
         Request A           Request B ...
             │                   │
             └─────────┬─────────┘
                       ▼
                    Queue
                       │
                       ▼
                   Scheduler
                       │
                       ▼
             Continuous Batching
                       │
                       ▼
              ┌────────────────┐
              │      GPU       │
              │                │
              │ Shared Weights │
              │                │
              │ KV A           │
              │ KV B           │
              │ KV C           │
              └────────────────┘
                       │
                       ▼
               Token Generation
                       │
                       ▼
                     用户
```

而 PagedAttention 类思路：

> 主要在中间帮助更灵活地管理 KV Cache。

---

# 一百二十二、五个最容易混淆的概念，一次分开

| 概念 | 最直白的问题 |
|---|---|
| TTFT | 用户多久看到第一个字？ |
| TPS | 开始生成后，吐字多快？ |
| Latency | 这个请求总共等多久？ |
| Throughput | 整台服务器单位时间干多少活？ |
| Concurrency | 同时有多少请求处于活跃状态？ |

这五个：

> 不能混成一个“速度”。

---

# 一百二十三、再区分 Batching 和 Concurrency

Concurrency：

> 同时有很多请求。

Batching：

> 系统把多个请求组织起来一起高效计算。

所以：

```text
有并发
≠
一定高效Batching
```

---

# 一百二十四、一个很烂的服务器也可以“有100并发”

只是：

> 99个人都在排队。

所以：

> Concurrency Number 本身不是性能。

---

# 一百二十五、Continuous Batching 的真正价值

不是：

> “让所有人瞬间完成。”

而是：

> **让动态长短不一的 LLM 请求更充分共享 GPU。**

这句话最准确。

---

# 一百二十六、PagedAttention 的真正价值

不是：

> “Attention 更聪明。”

而是：

> **更灵活地组织 KV Cache 的显存块，减少连续大块分配和浪费。**

---

# 一百二十七、vLLM 的真正价值

先记成：

> **一个高性能 LLM Serving Engine。**

核心目标是：

```text
更高GPU利用率
+
更好的KV管理
+
更高吞吐
+
更成熟的服务调度
```

具体版本实现：

> 后面实操时再看。

---

# 一百二十八、所以这三者的关系不要混

```text
Continuous Batching
=
调度思想


PagedAttention
=
KV内存管理/Attention执行思想


vLLM
=
实现高性能推理服务的引擎之一
```

不是：

> 三个同义词。

---

# 一百二十九、思维实验 A

一个模型：

```text
单请求TPS = 100
```

是不是说明：

> 100 个用户一起时每个人还是 100 TPS？

当然不是。

---

# 一百三十、思维实验 B

模型 TTFT 很高。

第一步该调 Temperature 吗？

不是。

Temperature：

> 控制 Sampling。

TTFT：

> 主要是 Serving / Queue / Prefill 问题。

---

# 一百三十一、思维实验 C

模型已经 4-bit。

系统 Throughput 还是低。

是不是继续量化到更低 bit 就一定解决？

不一定。

可能瓶颈在：

- Batching；
- Scheduler；
- KV；
- CPU；
- 网络；
- Prefill。

---

# 一百三十二、思维实验 D

PagedAttention 能不能让一个 8GB GPU 神奇容纳无限 KV Cache？

不能。

它提高：

> 内存管理效率。

不会：

> 创造无限显存。

---

# 一百三十三、思维实验 E

Continuous Batching 以后总 Throughput 提高。

为什么单用户 TPS 可能下降一点？

因为：

> GPU 同时服务更多 Sequence。

资源：

> 被共享。

---

# 一百三十四、思维实验 F

用户说：

> “点击以后 15 秒没反应，之后文字飞快出来。”

更像哪里慢？

优先怀疑：

```text
Queue / Prefill / TTFT
```

而不是：

> Decode TPS。

---

# 一百三十五、思维实验 G

用户说：

> “第一个字马上出来，但完整报告半天写不完。”

更像：

# Decode

或者：

> 输出太长。

---

# 一百三十六、思维实验 H

单用户测试一切完美。

20 用户一起就崩。

说明至少要调查：

```text
并发KV
+
Batching
+
Peak VRAM
+
Scheduler
```

而不是马上：

> 重训模型。

---

# 一百三十七、本阶段最容易犯的九个错误

### 错误 1

> TPS 就是模型所有速度。

错。

### 错误 2

> TTFT 和 TPS 是一回事。

错。

### 错误 3

> 单用户很快，就代表生产系统很快。

错。

### 错误 4

> Throughput 高，就意味着每个用户都最快。

错。

### 错误 5

> Batch 越大永远越好。

错。

### 错误 6

> Continuous Batching 会提高模型智力。

错。

### 错误 7

> PagedAttention 会减少模型参数。

错。

### 错误 8

> vLLM 是一种新的基础模型。

错。

### 错误 9

> 平均 Latency 很低，生产体验就一定好。

错。

还要看：

> P95 / P99。

---

# 一百三十八、把第三课第 1～9 阶段串起来

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
模型怎么加载？
        ↓
Stage 5
一个请求怎么生成文字？
        ↓
Stage 6
Weight怎么压缩？
        ↓
Stage 7
显存怎么做账？
        ↓
Stage 8
Next Token怎么选？
        ↓
Stage 9
很多请求怎么高效共享模型？
```

到这里，

我们已经从：

> “我会运行一个 LLM”

走到了：

> **“我开始理解一个 LLM 服务为什么能或不能真正上线。”**

---

# 一百三十九、本阶段掌握标准

这一阶段结束以后，你应该能够不用背术语，自己解释：

> TTFT 到底在衡量什么？

> 为什么长 Prompt 往往会增加 TTFT？

> TPS 到底是在测哪一段？

> Latency 和 TPS 为什么不是一回事？

> Throughput 和 Latency 为什么可能互相 Trade-off？

> 单用户 TPS 很高为什么不代表多用户服务能力强？

> GPU 为什么适合 Batching？

> Static Batch 在 LLM 上为什么容易浪费？

> Continuous Batching 为什么特别适合长短不一的生成请求？

> Scheduler 在模型服务中到底负责什么？

> Prefill 和 Decode 从工作模式上有什么不同？

> 为什么超长 Prompt 可能影响其它正在 Decode 的请求？

> 什么叫 Head-of-Line Blocking？

> KV Cache 为什么会出现碎片和预留浪费？

> PagedAttention 的“分页”直觉是什么？

> 为什么逻辑连续的 KV 不一定必须物理连续？

> PagedAttention 为什么不是“新的 Attention 智力算法”？

> vLLM 和 Model Weight 是什么关系？

> 为什么换 Serving Engine 不等于重新训练模型？

> 为什么生产系统要看 P95 / P99 而不能只看平均值？

> 为什么 Benchmark 必须包含真实的 Prompt 长度、Output 长度和并发？

> 为什么 ProcurementAI 的质量评测和性能评测最终必须放在同一张选型表里？

如果这些都能自己讲出来：

\[
\boxed{
第三课第9阶段真正掌握
}
\]

---

# 一百四十、本阶段最终只记一句话

> **“模型能生成答案”只是推理的起点；真正的模型服务还必须解决排队、Prefill、Decode、并发、Batching、KV Cache 和调度问题。TTFT 决定用户多久看到第一字，TPS 决定后续生成速度，Latency 描述一个请求整体等待时间，Throughput 描述整套系统能干多少活，而 Continuous Batching、PagedAttention 和 vLLM 这一类技术，本质是在提高 GPU 与 KV Cache 的服务效率，而不是提高模型本身的知识和智力。**

最后把整个阶段压成一张图：

```text
                    多个用户
                       │
                       ▼
                     Queue
                       │
                       ▼
                   Scheduler
                       │
                       ▼
             Continuous Batching
                       │
                       ▼
        ┌─────────────────────────┐
        │          GPU            │
        │                         │
        │     Shared Weights      │
        │                         │
        │  KV_A  KV_B  KV_C ...  │
        │       ↑                 │
        │   Paged KV管理          │
        └─────────────────────────┘
                       │
            ┌──────────┴──────────┐
            ▼                     ▼
         Prefill                Decode
            │                     │
            ▼                     ▼
          TTFT                   TPS
            └──────────┬──────────┘
                       ▼
                    Latency

整个系统单位时间处理多少工作
                       │
                       ▼
                  Throughput
```

# 下一阶段：第三课 · 第 10 阶段
## 第三课最终闭环：怎样真正选择一个政府采购基础模型，并建立第一个 ProcurementAI Baseline？

第 10 阶段会把第三课前 9 个阶段第一次全部变成一张**真实选型表**。

我们不再抽象地问：

> “哪个开源模型最强？”

而是按真正项目的方法比较候选模型：

```text
模型能力
+
中文能力
+
Context
+
Tokenizer
+
License
+
VRAM
+
量化方式
+
TTFT
+
TPS
+
Throughput
+
采购Gold Set
+
法规引用正确率
+
风险漏报率
```

最后形成第三课最重要的成果：

```text
ProcurementAI Base Model Selection Matrix
```

并且第一次定义：

> **ProcurementModel V0.1 的 Baseline 到底应该怎么建立。**

到了第 10 阶段，第三课就会完整闭环：从 **GPU → CUDA → 模型文件 → 加载 → 推理 → 精度 → 显存 → Sampling → Serving → 最终模型选型与 Baseline**。

---
