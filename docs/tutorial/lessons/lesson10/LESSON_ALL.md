# 第十课：推理部署、性能优化与 MLOps

> **V2 教学增强版。** 共 10 个阶段；主要产物/主线：`ProcurementAI`。  
> 核心心智模型前置、中文释义增强、详细正文完整保留。

---


<!-- LESSON 10 STAGE 01 START -->

# 第十课 · 第 1 阶段
# Inference 到底在优化什么？Latency、Throughput、TTFT、TPOT
## “模型跑得快”到底是什么意思？为什么首 Token 很快、整体生成很慢，或者吞吐很高、单个用户却等很久，都可能同时发生？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Latency ≠ Throughput。一个请求快和整个服务处理得多，是两个不同目标。**
2. **Prefill ≠ Decode。输入处理和逐 Token 生成是两个不同性能阶段，瓶颈也可能不同。**
3. **tokens/s 必须带 Scope。单请求、整机、输入、输出、单卡、多卡不能混为一谈。**
4. **FastStart ≠ FastFinish。TTFT、TPOT / ITL、E2E Latency 必须分开看。**
5. **Requests/s ≠ Tokens/s。吞吐指标必须匹配真实 Workload Shape。**
6. **AverageLatency ≠ TailLatency。生产体验往往由 P95 / P99 决定，而不是平均值。**
7. **FastKernel ≠ FastService。Queue Time 可以让一个很快的模型服务变得很慢。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Token` | Token：模型实际处理的离散文本单元 |
| `Latency` | 延迟：单个请求从进入到完成的时间 |
| `TTFT` | 首 Token 时间：用户等待第一个输出 Token 的时间 |
| `Throughput` | 吞吐：单位时间内处理请求或生成 Token 的能力 |
| `TPOT` | 每输出 Token 时间：首 Token 后平均生成一个 Token 的耗时 |
| `Inference` | 推理：系统接收请求并产生结果的在线计算过程 |
| `tokens/s` | 每秒 Token 数：衡量生成速度或系统吞吐的常见指标 |
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `Input` | 输入：模型在当前任务中允许看到的条件信息 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Batch` | 批次：一次参与计算的一组样本 |

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

第九课结束以后，我们已经有了：

```text
ProcurementLM_V0.2
ProcurementRAG_V0.1
ProcurementAgent_V0.1
ProcurementBench_V1
```

也就是说，我们已经能够回答：

> **这个系统质量够不够好？**

第十课开始解决另一个完全不同的问题：

> **这个已经被证明“质量合格”的系统，能不能真正稳定地跑在生产环境里？**

很多团队进入部署以后第一句话就是：

```text
模型有多少 tokens/s？
```

这个问题太粗。

因为“快”至少可能指：

```text
用户多久看到第一个Token？

后续Token流出来有多快？

一个请求多久完整结束？

服务器一秒能处理多少请求？

服务器一秒能生成多少Token？

高并发时P95 / P99会不会爆炸？

排队时间占了多少？

输入很长时会不会突然变慢？
```

所以本阶段第一条边界必须先锁死：

\[
\boxed{
Latency
\neq
Throughput
}
\]

本阶段最终形成：

# `ProcurementInferenceSLOPolicy_V0.1`

---

# 一、先给 Inference 一个完整工程定义

# Inference
## 推理

在部署语境里，Inference 不只是：

> “模型执行一次 forward。”

而是从请求进入系统，到结果返回用户之间的完整在线计算过程。

可以粗略拆成：

```text
Request Arrival
请求到达
↓
Queue
排队
↓
Preprocessing
预处理
↓
Prefill
处理输入上下文
↓
Decode
逐Token生成
↓
Postprocessing
后处理
↓
Response Complete
响应完成
```

所以端到端延迟可以概念化为：

\[
\boxed{
T_{E2E}
=
T_{queue}
+
T_{preprocess}
+
T_{prefill}
+
T_{decode}
+
T_{postprocess}
}
\]

注意：

> 不同服务框架对时间边界的定义可能略有差异。

因此真正做 Benchmark 时必须同时记录：

# Metric Definition
## 指标口径

否则同一个“Latency”可能根本不是同一个东西。

---

# 二、核心心智模型 ①
# `Latency ≠ Throughput`

# Latency
## 延迟

问的是：

> **一个请求要等多久？**

# Throughput
## 吞吐量

问的是：

> **系统单位时间能处理多少工作？**

例如：

```text
系统A：
单请求 1.2 秒完成
每秒处理 5 个请求

系统B：
单请求 2.0 秒完成
每秒处理 50 个请求
```

那么：

> A 的单请求延迟更低。

但：

> B 的总体吞吐更高。

所以：

\[
\boxed{
LowLatency
\not\Rightarrow
HighThroughput
}
\]

同样：

\[
\boxed{
HighThroughput
\not\Rightarrow
LowLatency
}
\]

生产优化第一步不是问：

> “哪个数最大？”

而是问：

> **我们的业务真正受哪个指标约束？**

---

# 三、用户真正感受到的第一类指标：TTFT

# TTFT
## Time To First Token
## 首 Token 延迟

它表示：

> 从请求进入服务，到用户看到第一个生成 Token，要等多久。

概念上：

\[
\boxed{
TTFT
\approx
Queue
+
Preprocess
+
Prefill
+
FirstDecodeStep
}
\]

为什么 TTFT 很重要？

因为流式输出场景里：

> 用户并不需要等整个回答完成，才开始感受到系统响应。

如果：

```text
总回答需要8秒
```

但：

```text
0.5秒就开始出字
```

用户体验通常会比：

```text
前6秒完全没反应
最后2秒突然全部输出
```

好很多。

所以：

\[
\boxed{
PerceivedResponsiveness
高度受
TTFT
影响
}
\]

---

# 四、TTFT 主要受什么影响？

通常包括：

```text
Queue Time
排队时间

Input Length
输入长度

Prefill Compute
Prefill计算量

Batching State
当前批处理状态

Model Size
模型规模

Hardware
硬件

Prompt Processing
提示词处理

RAG Context Length
RAG上下文长度
```

特别是：

> 输入 Token 越长，Prefill 需要处理的上下文越多。

所以一个政府采购系统如果把：

```text
整份数万Token采购文件
+
多段RAG证据
+
长System Prompt
```

全部直接塞进模型，

TTFT 可能显著上升。

因此：

\[
\boxed{
LongInput
首先强烈影响
Prefill / TTFT
}
\]

---

# 五、Prefill 到底是什么？

# Prefill
## 输入预填充阶段

模型先处理整个输入上下文：

```text
System Prompt
User Query
RAG Context
Conversation History
Tool Results
```

并建立后续生成需要的内部状态。

这个阶段通常：

> 一次处理很多输入 Token。

所以它和后面的 Decode：

> 计算形态不同。

---

# 六、Decode 到底是什么？

# Decode
## 自回归生成阶段

第一步生成：

\[
y_1
\]

然后：

\[
y_2
\]

依赖前面已经生成的 Token。

继续：

\[
y_3,y_4,\ldots
\]

所以：

\[
\boxed{
Decode
=
AutoregressiveSequentialGeneration
}
\]

中文：

> **同一个序列内部，生成过程具有时间上的顺序依赖。**

这也是为什么：

> 单个回答不能简单把所有未来 Token 一次性并行算完。

---

# 七、核心心智模型 ②
# `Prefill ≠ Decode`

Prefill 更关注：

> 输入上下文处理。

Decode 更关注：

> 一个 Token 接一个 Token 地生成。

两者的性能瓶颈也常常不同。

在很多典型部署里：

```text
Prefill
更容易受到大规模矩阵计算能力影响

Decode
更容易受到逐步生成、KV Cache访问、内存带宽和并发调度影响
```

但具体瓶颈仍取决于：

```text
模型结构
硬件
并发
序列长度
推理引擎
量化方式
```

所以：

\[
\boxed{
OneOptimization
不一定同时改善
Prefill
和
Decode
}
\]

---

# 八、第二类关键指标：TPOT

# TPOT
## Time Per Output Token
## 每个输出 Token 的平均时间

在已经生成第一个 Token 以后，

后续 Token 平均多久出来一个。

一种常见定义可以写成：

\[
\boxed{
TPOT
=
\frac{
T_{last}-T_{first}
}{
N_{output}-1
}
}
\]

前提：

\[
N_{output}>1
\]

它越低：

> 后续文字流出来越快。

例如：

```text
TPOT = 50 ms/token
```

大致意味着：

\[
20\ tokens/s
\]

的单序列输出节奏。

---

# 九、TPOT 和 Tokens/s 是什么关系？

对单个序列，

近似可以理解：

\[
\boxed{
OutputTokensPerSecond
\approx
\frac{1}{TPOT}
}
\]

但工程上必须非常小心。

因为“tokens/s”可能指：

```text
单请求输出 tokens/s

整个服务器输出 tokens/s

输入+输出总 tokens/s

每张GPU tokens/s

某个Batch内 tokens/s
```

所以：

\[
\boxed{
TokensPerSecond
必须说明
Scope
}
\]

否则一句：

> “我们现在 2000 tokens/s。”

几乎没有足够信息。

---

# 十、核心心智模型 ③
# `tokens/s` 是一个必须带口径的指标

至少要问：

```text
Per Request 还是 Server Aggregate？

只算 Output 还是 Input + Output？

单GPU还是多GPU？

什么模型？

什么输入长度？

什么输出长度？

什么并发？
```

所以：

\[
\boxed{
MetricWithoutWorkload
=
WeakMetric
}
\]

---

# 十一、第三类指标：End-to-End Latency

# E2E Latency
## 端到端延迟

表示：

> 一个请求从进入系统到完整响应结束，用户总共等多久。

对于流式生成：

\[
\boxed{
E2ELatency
\neq
TTFT
}
\]

一个系统可能：

```text
TTFT = 0.4s
```

但：

```text
E2E = 15s
```

说明：

> 开头反应很快，但生成过程很慢或输出很长。

反过来，

TTFT 慢但 TPOT 很快：

> 用户前面等很久，后面字出得很快。

这两种用户体验完全不同。

---

# 十二、核心心智模型 ④
# `FastStart ≠ FastFinish`

所以生产监控至少应该分开：

```text
TTFT
TPOT / ITL
E2E Latency
```

而不是只记录：

```text
request_time
```

一个总数。

---

# 十三、ITL 是什么？

# ITL
## Inter-Token Latency
## Token 间延迟

表示：

> 相邻两个输出 Token 之间的时间。

TPOT 是平均。

ITL 可以进一步观察：

```text
中间有没有突然卡顿
P95 Token间隔
P99 Token间隔
```

所以：

\[
\boxed{
AverageTPOT
可能掩盖
Jitter
}
\]

# Jitter
## 抖动

指：

> Token 输出节奏忽快忽慢。

流式交互里，

稳定的输出节奏通常也很重要。

---

# 十四、第四类指标：Request Throughput

# Request Throughput
## 请求吞吐

例如：

\[
\boxed{
RequestsPerSecond
}
\]

或者：

\[
\boxed{
RequestsPerMinute
}
\]

它回答：

> 服务单位时间完成多少请求。

但如果请求长度差异巨大：

```text
请求A：
100 input tokens
20 output tokens

请求B：
20000 input tokens
3000 output tokens
```

那么：

> 只比较 Requests/s 也很容易失真。

---

# 十五、第五类指标：Token Throughput

可以记录：

```text
Input Tokens/s

Output Tokens/s

Total Tokens/s
```

它比 Requests/s 更能表达：

> 实际处理了多少 Token 工作量。

但仍然要结合：

```text
输入长度分布
输出长度分布
并发
Batch
```

一起看。

---

# 十六、核心心智模型 ⑤
# `Requests/s` 和 `Tokens/s` 衡量的不是同一件事

一个系统：

> 很擅长处理大量短请求。

另一个系统：

> 更擅长长文档。

如果只看 Requests/s，

可能得到完全错误的比较结论。

所以：

\[
\boxed{
ThroughputMetric
必须匹配
WorkloadShape
}
\]

---

# 十七、P50、P95、P99 为什么比平均值更重要？

假设 100 个请求：

```text
95个请求 = 1秒

5个请求 = 20秒
```

平均值：

> 仍然可能看起来没有特别离谱。

但那 5 个用户体验非常差。

所以生产系统通常看：

# Percentile Latency
## 分位数延迟

### P50
中位用户。

### P95
95% 请求低于这个时间。

### P99
99% 请求低于这个时间。

所以：

\[
\boxed{
AverageLatency
\neq
TailLatency
}
\]

---

# 十八、核心心智模型 ⑥
# 生产事故经常发生在 Tail，不发生在 Average

真正线上用户抱怨的通常是：

```text
为什么有些请求突然20秒？

为什么高峰期偶尔超时？

为什么一到长文档就卡死？
```

所以：

\[
\boxed{
ProductionSLO
通常需要
P95 / P99
}
\]

不能只看平均延迟。

---

# 十九、Queue Time：为什么模型本身很快，用户仍然很慢？

当请求到达速度超过当前服务能力，

请求会进入：

# Queue
## 队列

于是：

\[
\boxed{
UserLatency
=
QueueLatency
+
ServiceLatency
}
\]

即使模型本身只需：

```text
2秒
```

但排队：

```text
8秒
```

用户实际等待：

```text
10秒
```

所以：

\[
\boxed{
FastKernel
\neq
FastService
}
\]

---

# 二十、Concurrency：并发到底是什么？

# Concurrency
## 并发数

表示：

> 同一时间系统里有多少请求正在等待或执行。

提高 Concurrency 往往可以：

> 更充分利用 GPU。

但 Concurrency 太高：

```text
Queue变长

Batch变大

KV Cache增长

显存压力变大

P95 / P99上升

甚至OOM
```

所以：

\[
\boxed{
MoreConcurrency
\neq
AlwaysBetter
}
\]

---

# 二十一、核心心智模型 ⑦
# Throughput 和 Latency 往往存在 Operating Tradeoff

提高并发：

> 吞吐可能上升。

但：

> 单请求等待时间也可能上升。

所以生产优化真正寻找的是：

# Operating Point
## 运行工作点

即：

> 在目标 SLO、成本和硬件预算下，最合适的并发、Batch 和资源配置。

---

# 二十二、什么时候系统开始 Saturation？

# Saturation
## 饱和

当请求负载继续增加，

系统已经无法等比例增加吞吐，

但：

```text
Queue Time快速增加
P95快速增加
P99快速增加
```

这就是接近饱和。

概念上：

```text
低负载：
请求来了马上跑

中负载：
GPU利用率提升，吞吐提高

高负载：
系统接近满载

过载：
吞吐增加有限，但排队延迟急剧恶化
```

所以：

\[
\boxed{
MaxThroughputPoint
通常不是
BestProductionPoint
}
\]

---

# 二十三、Little's Law：为什么并发、吞吐和延迟会互相约束？

在稳定系统里，常用一个非常重要的排队论关系：

\[
\boxed{
L
=
\lambda W
}
\]

其中：

- \(L\)：系统中的平均请求数；
- \(\lambda\)：平均到达 / 完成速率；
- \(W\)：平均停留时间。

它告诉我们：

> 并发、吞吐和延迟不是三个互不相关的数字。

如果吞吐固定，

系统里积压的请求越多：

> 平均等待时间通常越长。

这就是为什么：

> “把并发无限调大”

不是免费优化。

---

# 二十四、核心心智模型 ⑧
# `Concurrency` 是资源利用工具，不是性能目标本身

并发真正的作用是：

> 让 GPU 尽可能少闲着。

不是：

> 数字越大越高级。

所以：

\[
\boxed{
Concurrency
服务于
SLO
}
\]

而不是：

\[
\boxed{
SLO
服务于
Concurrency
}
\]

---

# 二十五、Workload Shape：为什么 Benchmark 必须模拟真实流量？

如果性能 Benchmark 只测：

```text
Input = 128 tokens
Output = 128 tokens
Concurrency = 1
```

但生产采购系统实际：

```text
短问答
长文档
RAG长Context
Agent多轮工具结果
输出长度差异巨大
并发有高峰
```

那么离线性能数字：

> 参考价值有限。

所以需要：

# Workload Distribution
## 工作负载分布

至少记录：

```text
Input Length Distribution

Output Length Distribution

Concurrency Distribution

Request Arrival Pattern

Task Mix

Streaming / Non-streaming

RAG Context Size

Agent Tool Latency
```

因此：

\[
\boxed{
BenchmarkWorkload
必须接近
ProductionWorkload
}
\]

---

# 二十六、Cold Start 和 Warm Run 要不要分开？

要。

# Cold Start
## 冷启动

可能包含：

```text
模型加载
CUDA初始化
Kernel编译
Cache未命中
```

# Warm Run
## 热运行

系统已经：

> 模型加载完成、缓存建立、服务稳定。

所以：

\[
\boxed{
ColdLatency
\neq
SteadyStateLatency
}
\]

二者都可以有价值，

但不能混着报告。

---

# 二十七、核心心智模型 ⑨
# `Benchmark Environment` 是性能指标的一部分

性能分数必须绑定：

```text
GPU型号
GPU数量
显存
CPU
内存
网络
驱动
CUDA
推理引擎
模型版本
量化版本
并发
输入输出长度
```

否则：

```text
TTFT = 500ms
```

缺少环境信息，

很难复现。

所以：

\[
\boxed{
PerformanceNumber
+
Environment
=
ReproducibleEvidence
}
\]

---

# 二十八、SLO 到底是什么？

# SLO
## Service Level Objective
## 服务级目标

不是：

> “越快越好。”

而是明确：

> 生产系统应该达到什么服务水平。

例如概念上：

```text
P95 TTFT <= 某阈值

P95 E2E <= 某阈值

P99错误率 <= 某阈值

最大并发下不得OOM

吞吐 >= 某目标

关键任务成功率 >= 某阈值
```

具体数值：

> 应由真实业务要求和性能压测确定。

不是本课拍脑袋给一个万能数字。

---

# 二十九、核心心智模型 ⑩
# `SLO` 是部署优化的目标函数

没有 SLO 时：

```text
更快一点
更多吞吐
再省点显存
```

会变成无止境优化。

有 SLO 后：

> 才能知道什么叫“已经足够好”。

所以：

\[
\boxed{
Optimization
需要
Target
}
\]

而：

\[
\boxed{
ProductionTarget
=
SLO
}
\]

---

# 三十、Latency、Throughput、Cost 三者必须一起看

假设方案 A：

```text
TTFT更低
但需要8张GPU
```

方案 B：

```text
TTFT略高
但只需要2张GPU
```

到底选哪个？

不能只看延迟。

还要看：

# Cost Efficiency
## 成本效率

例如：

```text
requests / dollar

output tokens / dollar

GPU hours / 1M tokens
```

概念上：

\[
\boxed{
ProductionOptimization
=
Quality
+
Latency
+
Throughput
+
Cost
}
\]

而且 Quality：

> 不能因为性能优化而掉出第九课 Benchmark 的 Release Gate。

---

# 三十一、性能优化为什么不能脱离质量评测？

后面我们会做：

```text
Quantization
Batching
Long Context Optimization
Parallelism
```

这些可能改变：

```text
数值精度
解码行为
上下文处理
输出稳定性
```

所以：

\[
\boxed{
PerformanceGain
不能自动等于
ProductionGain
}
\]

必须继续通过：

```text
ProcurementBench_V1
```

验证质量没有不可接受回归。

这就把第九课和第十课正式连接起来。

---

# 三十二、本阶段正式工程产物
# `ProcurementInferenceSLOPolicy_V0.1`

第一版至少锁定：

```text
inference_slo_policy_version

model_version

serving_engine_version

hardware_profile

quantization_version

workload_profile_version

request_arrival_pattern

input_length_distribution

output_length_distribution

concurrency_levels

streaming_enabled

ttft_definition

tpot_definition

itl_definition

e2e_latency_definition

request_throughput_definition

input_token_throughput

output_token_throughput

p50_latency

p95_latency

p99_latency

queue_time

prefill_time

decode_time

cold_start_policy

warm_run_policy

saturation_test

oom_boundary

cost_metric

quality_regression_benchmark

slo_targets

release_gate

trace_logging
=
enabled
```

每次性能 Benchmark Run 至少记录：

```text
run_id

model_version

engine_version

hardware

workload_profile

concurrency

input_tokens

output_tokens

ttft

tpot

itl

e2e_latency

queue_time

requests_per_second

input_tokens_per_second

output_tokens_per_second

gpu_memory

gpu_utilization

errors

oom

cost

benchmark_quality_delta

slo_status
```

这样以后才能回答：

> **所谓“更快”，到底快在哪里、在什么负载下快、代价是什么、质量有没有下降？**

---

# 三十三、本阶段最重要的 10 个核心心智模型

> **心智模型 ①：`Latency ≠ Throughput`。一个请求快和整个服务处理得多，是两个不同目标。**

> **心智模型 ②：`Prefill ≠ Decode`。输入处理和逐 Token 生成是两个不同性能阶段，瓶颈也可能不同。**

> **心智模型 ③：`tokens/s` 必须带 Scope。单请求、整机、输入、输出、单卡、多卡不能混为一谈。**

> **心智模型 ④：`FastStart ≠ FastFinish`。TTFT、TPOT / ITL、E2E Latency 必须分开看。**

> **心智模型 ⑤：`Requests/s ≠ Tokens/s`。吞吐指标必须匹配真实 Workload Shape。**

> **心智模型 ⑥：`AverageLatency ≠ TailLatency`。生产体验往往由 P95 / P99 决定，而不是平均值。**

> **心智模型 ⑦：`FastKernel ≠ FastService`。Queue Time 可以让一个很快的模型服务变得很慢。**

> **心智模型 ⑧：`Concurrency` 是资源利用工具，不是性能目标；最大并发不等于最佳生产工作点。**

> **心智模型 ⑨：`PerformanceNumber + Environment = ReproducibleEvidence`。脱离硬件和负载上下文的性能数字没有充分可比性。**

> **心智模型 ⑩：`SLO = Production Optimization Target`。没有 SLO，就没有明确的优化停止条件。**

---

# 三十四、把完整 Inference Performance 模型压成一张专业工程图

```text
                        Incoming Requests
                           请求到达
                               │
                               ▼
                             Queue
                              排队
                               │
                               ▼
                         Preprocessing
                            预处理
                               │
                               ▼
                            Prefill
                          处理输入上下文
                               │
                       ┌───────┴────────┐
                       │                │
                       ▼                ▼
                    TTFT            KV / State
                  首Token时间          缓存状态
                       │                │
                       └───────┬────────┘
                               ▼
                             Decode
                         逐Token生成
                               │
                  ┌────────────┼────────────┐
                  ▼            ▼            ▼
                TPOT          ITL       Output Tokens/s
            每Token时间     Token间延迟      输出吞吐
                  │            │            │
                  └────────────┼────────────┘
                               ▼
                        Response Complete
                           响应完成
                               │
                               ▼
                         E2E Latency
                          端到端延迟
                               │
                               ▼
                  P50 / P95 / P99 + Throughput
                      分位延迟 + 系统吞吐
                               │
                               ▼
                       Cost + Quality Check
                       成本 + 质量回归
                               │
                               ▼
                              SLO
                          服务级目标
```

脑中最后只留一句：

> **Inference 性能优化的本质，不是追求一个最大的 tokens/s，而是在真实 Workload 下，把 Queue、Prefill、Decode 和输出全过程拆开，用 TTFT、TPOT、ITL、E2E、P95/P99、Throughput 和 Cost 建立统一性能模型，再在不突破质量回归门槛的前提下找到满足业务 SLO 的最佳运行工作点。**

---

# 第十课 · 第 1 阶段掌握测试

现在不回看正文，你应该能够解释：Latency 和 Throughput 为什么不是一回事；TTFT、TPOT、ITL、E2E 分别测什么；Prefill 与 Decode 为什么要分开；输入长度为什么主要影响 Prefill 和 TTFT；为什么同一个 “tokens/s” 必须说明 Scope；Requests/s 和 Tokens/s 为什么不能互相替代；为什么平均延迟不能代表 P95 / P99；Queue Time 为什么会让“模型很快但服务很慢”；Concurrency 为什么既能提高利用率又可能拉高 Tail Latency；什么叫 Saturation；Little's Law 为什么能帮助理解并发、吞吐、延迟之间的关系；为什么真实性能 Benchmark 必须定义 Workload Shape；Cold Start 与 Warm Run 为什么要分开；为什么性能数字必须绑定 Hardware / Engine / Model / Workload；SLO 为什么是性能优化真正的目标函数；以及为什么所有性能优化最后还必须重新经过 `ProcurementBench_V1` 的质量回归验证。

如果这些能够完整讲出来：

\[
\boxed{
第十课第1阶段真正掌握
}
\]

---

# 下一阶段：第十课 · 第 2 阶段
# Quantization：FP16、BF16、INT8、INT4 与精度—显存权衡
## 为什么把 Weight 从 16 bit 压到 8 bit / 4 bit 可以显著省显存？为什么 Quantization 不是“免费压缩”，而是一次必须经过 Benchmark 验证的数值近似？

下一阶段会正式进入：

```text
Floating Point
浮点表示

FP16 / BF16
半精度

INT8
8位整数

INT4
4位整数

Weight-only Quantization
只量化权重

Activation Quantization
激活量化

Scale / Zero Point
缩放与零点

Calibration
量化校准

Quantization Error
量化误差

Memory Saving
显存节省

Throughput Impact
吞吐影响

Quality Regression
质量回归
```

并建立：

# `ProcurementQuantizationPolicy_V0.1`

下一阶段最关键的一条边界：

\[
\boxed{
Quantization
\neq
FreeCompression
}
\]

也就是说：

> **量化节省的是数值表示成本，但它引入的是近似误差；省下多少显存、能不能更快、质量会不会退化，都必须用真实模型、真实硬件和 `ProcurementBench_V1` 实测。**

---

<!-- LESSON 10 STAGE 01 END -->


<!-- LESSON 10 STAGE 02 START -->

# 第十课 · 第 2 阶段
# Quantization：FP16、BF16、INT8、INT4 与精度—显存权衡
## 为什么把 Weight 从 16 bit 压到 8 bit / 4 bit 可以显著省显存？为什么 Quantization 不是“免费压缩”，而是一次必须经过 Benchmark 验证的数值近似？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：MEDIUM。** 审计原因：核心心智模型出现偏后，阅读前段缺少认知锚点；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Quantization ≠ FreeCompression。低 bit 是数值近似，不是无损压缩。**
2. **DataTypeChoice = Memory + Numerical + Kernel Decision。**
3. **StoragePrecision ≠ ComputePrecision。**
4. **WeightQuantization ≠ ActivationQuantization。**
5. **QuantizedModel 是独立 Serving Version。**
6. **SmallerModel ≠ FasterModel。性能收益取决于真实 Kernel。**
7. **WeightMemorySaving ≠ TotalVRAMSaving。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Quantization` | 量化：用更低位宽表示权重/激活以降低显存和计算成本 |
| `FP16` | FP16：16 位浮点，节省显存但数值范围较窄 |
| `BF16` | BF16：保留较大指数范围的 16 位浮点，常用于大模型 |
| `Throughput` | 吞吐：单位时间内处理请求或生成 Token 的能力 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `Latency` | 延迟：单个请求从进入到完成的时间 |
| `Calibration` | 校准：使模型置信度更接近实际正确率 |
| `Memory` | 任务记忆：保存跨步骤需要复用的结构化信息 |

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

第 1 阶段已经建立：

\[
\boxed{Latency \neq Throughput}
\]

现在进入最常见的推理优化之一：

# Quantization
## 量化

本阶段第一条边界：

\[
\boxed{Quantization \neq FreeCompression}
\]

量化的本质不是“无损变小”，而是：

> 用更少 bit 去近似原来的数值。

本阶段最终形成：

# `ProcurementQuantizationPolicy_V0.1`

---

# 一、Weight 显存为什么和 bit 数直接相关？

若模型有 \(P\) 个参数，每个参数使用 \(b\) bit，则仅 Weight 的理论存储量近似：

\[
\boxed{
Memory_{weights}\approx \frac{P\cdot b}{8}
}
\]

因此理论上：

```text
16 bit → 每参数约 2 bytes
8 bit  → 每参数约 1 byte
4 bit  → 每参数约 0.5 byte
```

所以从 16 bit 到 8 bit：

> Weight 存储大约减半。

从 16 bit 到 4 bit：

> Weight 存储大约变成四分之一。

但真实推理显存还包括：

```text
KV Cache
Runtime Buffer
CUDA Context
Workspace
Batch Metadata
```

所以：

\[
\boxed{
WeightMemorySaving
\neq
TotalVRAMSaving
}
\]

---

# 二、FP16 与 BF16

两者都是 16 位浮点。

FP16：

> 尾数精度相对更高，但动态范围较窄。

BF16：

> 动态范围更大，但尾数精度较低。

工程上最终选哪个，需要看：

```text
GPU支持
模型训练精度
Kernel实现
推理引擎
```

所以：

\[
\boxed{
DataTypeChoice
=
MemoryDecision
+
NumericalDecision
+
KernelDecision
}
\]

---

# 三、整数量化怎样映射浮点数？

一种常见抽象：

\[
q=
round\left(\frac{x}{s}\right)+z
\]

其中：

- \(s\)：Scale，缩放因子；
- \(z\)：Zero Point，零点。

反量化：

\[
\hat{x}=s(q-z)
\]

通常：

\[
\hat{x}\neq x
\]

量化误差：

\[
\boxed{
e_q=x-\hat{x}
}
\]

因此低 bit 的核心交换关系是：

\[
\boxed{
LessMemory
\leftrightarrow
MoreApproximation
}
\]

---

# 四、Symmetric、Asymmetric 与 Scale 粒度

## Symmetric Quantization
对称量化

数值范围围绕 0 对称。

## Asymmetric Quantization
非对称量化

允许使用 Zero Point，更适合偏移分布。

Scale 还可以分为：

```text
Per-Tensor
整个Tensor一个Scale

Per-Channel
每个Channel一个Scale

Group-wise
每组Weight一个Scale
```

一般来说：

> 粒度越细，越容易降低量化误差，但元数据和 Kernel 复杂度更高。

所以：

\[
\boxed{
FinerGranularity
\neq
FreeAccuracy
}
\]

---

# 五、Weight-only 与 Activation Quantization

# Weight-only Quantization
只量化权重

例如：

```text
Weight = INT4
Activation = FP16/BF16
```

重点是：

> 减少 Weight 存储和 Weight 读取带宽。

但：

\[
\boxed{
StoragePrecision
\neq
ComputePrecision
}
\]

Weight 存成 INT4，不代表整个算子都在 INT4 中计算。

---

# Activation Quantization
激活量化

Activation 会随输入动态变化，并可能存在：

# Outlier
离群值

所以一般比固定 Weight 更难量化。

因此：

\[
\boxed{
WeightQuantization
\neq
ActivationQuantization
}
\]

---

# 六、Quantization Calibration

这里的 Calibration 是：

> 用代表性样本观察数值分布，为 Scale、Clipping Range 等量化参数提供依据。

它不是第九课的 Confidence Calibration。

所以：

\[
\boxed{
QuantizationCalibration
\neq
ConfidenceCalibration
}
\]

而且校准数据应该尽量接近生产：

```text
中文采购长文
RAG长上下文
结构化输出
真实任务分布
```

---

# 七、PTQ 与 QAT

# PTQ
Post-Training Quantization
训练后量化

优点：

```text
成本低
速度快
不必完整重训
```

# QAT
Quantization-Aware Training
量化感知训练

训练时模拟量化误差，让模型适应低精度表示。

通常：

> 成本更高，但在更激进量化场景下可能更有价值。

---

# 八、为什么量化后不一定更快？

如果：

```text
低bit Kernel不成熟
硬件不擅长该格式
频繁反量化
Batch形态不匹配
```

就可能：

> 显存省了，但速度没有提升。

所以：

\[
\boxed{
SmallerModel
\neq
FasterModel
}
\]

真正性能收益必须经过：

```text
真实硬件
真实Engine
真实Workload
```

实测。

---

# 九、Quantized Model 是新版本

量化以后数值行为已经改变。

所以：

```text
ProcurementLM_V0.2-FP16
ProcurementLM_V0.2-INT8
ProcurementLM_V0.2-INT4
```

必须视为不同 Serving Artifact。

至少版本化：

```text
quantization_method
bit_width
group_size
zero_point
calibration_version
kernel_version
```

因此：

\[
\boxed{
QuantizationConfig
\in
ServingVersion
}
\]

---

# 十、质量回归必须用 `ProcurementBench_V1`

不能只看：

```text
Perplexity
```

而应至少检查：

```text
Classification
Generation
RAG
Agent
Critical Slices
Calibration
Regression
```

因为量化可能只伤：

```text
复杂推理
长上下文
数字
结构化输出
稀有风险
```

所以：

\[
\boxed{
AverageQualityStable
\neq
CriticalSliceStable
}
\]

---

# 十一、受控量化比较

至少比较：

```text
FP16/BF16 Baseline
INT8 Candidate
INT4 Candidate
```

固定：

```text
模型
Benchmark
Prompt
Workload
Hardware
Serving Engine
```

比较：

```text
VRAM
TTFT
TPOT
Throughput
P95/P99
Cost
Quality Delta
```

量化选型是：

# Pareto Decision
## 帕累托决策

即：

\[
\boxed{
Memory
+
Latency
+
Throughput
+
Quality
+
Cost
}
\]

之间做折中。

---

# 十二、什么时候不值得量化？

如果：

```text
FP16已满足SLO
显存足够
并发压力不大
质量要求极高
```

量化带来的工程复杂度和回归风险可能不值得。

所以：

\[
\boxed{
Optimization
必须由
Bottleneck
驱动
}
\]

---

# 十三、本阶段正式工程产物
# `ProcurementQuantizationPolicy_V0.1`

至少锁定：

```text
quantization_policy_version
base_model_version
baseline_dtype
candidate_dtypes
weight_quantization
activation_quantization
kv_quantization_policy
symmetric_asymmetric
scale_granularity
group_size
zero_point_policy
calibration_dataset_version
ptq_qat_mode
quantization_kernel
serving_engine_version
hardware_profile
weight_memory
total_vram
ttft
tpot
throughput
p95_latency
quality_benchmark_version
overall_quality_delta
critical_slice_delta
release_gate
rollback_target
```

---

# 十四、本阶段最重要的 9 个核心心智模型

> **① `Quantization ≠ FreeCompression`。低 bit 是数值近似，不是无损压缩。**

> **② `DataTypeChoice = Memory + Numerical + Kernel Decision`。**

> **③ `StoragePrecision ≠ ComputePrecision`。**

> **④ `WeightQuantization ≠ ActivationQuantization`。**

> **⑤ `QuantizedModel` 是独立 Serving Version。**

> **⑥ `SmallerModel ≠ FasterModel`。性能收益取决于真实 Kernel。**

> **⑦ `WeightMemorySaving ≠ TotalVRAMSaving`。**

> **⑧ `AverageQualityStable ≠ CriticalSliceStable`。**

> **⑨ `Optimization must follow Bottleneck`。**

---

# 下一阶段：第十课 · 第 3 阶段
# KV Cache：为什么推理显存不只是模型 Weight？

下一阶段最关键的边界：

\[
\boxed{
ModelFitsInGPU
\neq
ServingFitsInGPU
}
\]

并建立：

# `ProcurementKVCachePolicy_V0.1`

---

<!-- LESSON 10 STAGE 02 END -->


<!-- LESSON 10 STAGE 03 START -->

# 第十课 · 第 3 阶段
# KV Cache：为什么推理显存不只是模型 Weight？
## 模型明明能装进 GPU，为什么一到长上下文和高并发就 OOM？KV Cache 到底缓存了什么，又为什么会随序列长度和并发增长？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **ModelFitsInGPU ≠ ServingFitsInGPU。**
2. **KVCache = MemoryForComputeTradeoff。**
3. **ParameterCount ≠ ServingMemoryProfile。**
4. **MaxContext ≠ BestServingContext。**
5. **PrefixCache 主要节省重复 Prefill，必须看 Hit Rate。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `KV Cache` | KV 缓存：生成时缓存历史 Key/Value 以减少重复计算 |
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Memory` | 任务记忆：保存跨步骤需要复用的结构化信息 |
| `Serving` | 服务化：把模型包装成可扩展、可观测、可治理的在线服务 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |

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

上一阶段已经锁定：

\[
\boxed{
WeightMemorySaving
\neq
TotalVRAMSaving
}
\]

现在进入推理显存最关键的动态部分之一：

# KV Cache
## Key / Value 缓存

本阶段第一条边界：

\[
\boxed{
ModelFitsInGPU
\neq
ServingFitsInGPU
}
\]

本阶段最终形成：

# `ProcurementKVCachePolicy_V0.1`

---

# 一、为什么自回归生成需要 KV Cache？

Transformer Attention 会为 Token 计算：

```text
Query
Key
Value
```

生成第 \(t\) 个 Token 时，需要关注前面的历史 Token。

如果每一步都重新计算所有历史 Token 的 Key / Value：

> 重复计算会非常大。

所以把历史的 K/V 缓存起来：

```text
历史Token的K/V
→ 保存在显存

新Token
→ 只计算新增K/V
```

因此：

\[
\boxed{
KVCache
=
MemoryForComputeTradeoff
}
\]

也就是：

> 用显存换掉重复计算。

---

# 二、KV Cache 显存怎样增长？

单个 Token 的 KV Cache 大致与：

\[
2
\times
N_{layers}
\times
N_{kvheads}
\times
D_{head}
\times
Bytes
\]

成正比。

前面的 2 表示：

```text
K + V
```

序列长度 \(T\) 增长时：

\[
\boxed{
KVMemory\propto T
}
\]

并发序列 \(B\) 增长时：

\[
\boxed{
KVMemory\propto B\cdot T
}
\]

这不是所有实现的完整公式，

但抓住了最重要的工程关系：

> **Context Length 和活跃并发会直接推高 KV Cache。**

---

# 三、MHA、GQA、MQA 与 KV Head

MHA 通常：

> 每个 Query Head 都对应独立 K/V Head。

GQA：

> 多个 Query Head 共享较少 KV Head。

MQA：

> 更大范围共享 KV Head。

所以：

\[
\boxed{
FewerKVHeads
\Rightarrow
SmallerKVCache
}
\]

因此参数量相近的模型：

> 推理 KV 成本也可能差很多。

---

# 四、核心心智模型 ①
# `ParameterCount ≠ ServingMemoryProfile`

模型选型不能只看：

```text
7B
14B
32B
```

还要看：

```text
num_layers
num_kv_heads
head_dim
context_length
dtype
```

---

# 五、Prefill 之后 Cache 已经开始占显存

输入：

```text
10000 tokens
```

Prefill 会处理这些 Token，并为后续 Decode 建立 KV。

如果再输出：

```text
2000 tokens
```

当前序列的 Cache 还会继续增长。

可以近似理解：

\[
\boxed{
KVLength
=
InputTokens
+
GeneratedTokens
}
\]

---

# 六、为什么长上下文 × 高并发特别危险？

一个请求从：

```text
2K context
→ 32K context
```

KV 显存会显著增加。

再叠加：

```text
Concurrency = 32
```

压力会继续放大。

所以：

\[
\boxed{
LongContext
\times
HighConcurrency
=
KVPressure
}
\]

---

# 七、核心心智模型 ②
# `MaxContext ≠ BestServingContext`

模型架构支持：

```text
128K
```

不代表生产中每个请求都应该给 128K。

还必须考虑：

```text
TTFT
KV显存
并发
吞吐
成本
```

所以：

\[
\boxed{
ContextWindowSupported
\neq
ContextWindowAffordable
}
\]

---

# 八、KV Cache Quantization

KV 也可以低精度保存。

目标：

> 降低动态 Cache 显存。

但这会近似 Attention 历史表示。

因此要测试：

```text
长上下文
关键Slice
不同Context Length
质量回归
真实性能
```

所以：

\[
\boxed{
KVQuantization
\neq
FreeMemory
}
\]

---

# 九、Prefix Caching

如果很多请求共享：

```text
System Prompt
公共政策前缀
相同RAG前缀
```

可以复用已经计算好的前缀 KV。

这叫：

# Prefix Caching
## 前缀缓存

它主要节省：

> 重复 Prefill。

所以：

\[
\boxed{
SharedPrefix
\rightarrow
ReusableCompute
}
\]

---

# 十、核心心智模型 ③
# Prefix Cache 是否有效，必须看 Hit Rate

如果命中率：

```text
5%
```

实际收益可能很小。

如果：

```text
70%
```

可能价值很高。

所以：

\[
\boxed{
FeatureEnabled
\neq
FeatureEffective
}
\]

---

# 十一、KV Cache 和 Batching 相互制约

并发更多：

> GPU 更忙。

但活跃序列也更多：

> KV Cache 更大。

所以：

\[
\boxed{
BatchingGain
受
KVCapacity
约束
}
\]

---

# 十二、Fragmentation

请求长度和结束时间不同，会不断申请、释放 KV 空间。

可能产生：

# Fragmentation
## 内存碎片

即使总 Free VRAM 仍然存在，

也未必能找到合适的连续区域。

所以：

\[
\boxed{
FreeVRAM
\neq
AllocatableKV
}
\]

下一阶段的 Paged Attention 就是为这种动态 KV 管理而生的重要思路。

---

# 十三、Eviction 与 Admission

显存不足时可能：

```text
Evict Cache
驱逐缓存

Recompute
以后重算

Reject Request
拒绝新请求
```

所以系统需要：

# Admission Policy
## 准入策略

决定：

> 当前容量还能不能安全接受更多请求。

---

# 十四、理论估算不够，必须真实压测

真实推理还有：

```text
Allocator Overhead
Workspace
Kernel Buffers
CUDA Graphs
Temporary Tensor
```

因此必须跑：

```text
不同 Context
不同 Concurrency
不同 Output Length
```

找到：

# OOM Boundary
## 显存失效边界

所以：

\[
\boxed{
TheoreticalMemory
\neq
ReleaseEvidence
}
\]

---

# 十五、KV 监控指标

至少：

```text
kv_cache_used_bytes
kv_cache_utilization
active_sequences
average_context_length
p95_context_length
prefix_cache_hit_rate
eviction_count
recompute_count
oom_count
rejected_requests
```

还要和：

```text
TTFT
TPOT
P95
Throughput
```

联动分析。

---

# 十六、本阶段正式工程产物
# `ProcurementKVCachePolicy_V0.1`

至少锁定：

```text
kv_policy_version
model_version
num_layers
num_kv_heads
head_dim
kv_dtype
bytes_per_element
max_context
serving_context_policy
max_output_tokens
concurrency_targets
estimated_kv_bytes_per_token
measured_kv_usage
prefix_cache_enabled
prefix_cache_hit_rate
kv_quantization
eviction_policy
recompute_policy
admission_policy
fragmentation_monitoring
oom_boundary
context_length_slices
quality_regression
release_gate
```

---

# 十七、本阶段最重要的 9 个核心心智模型

> **① `ModelFitsInGPU ≠ ServingFitsInGPU`。**

> **② `KVCache = MemoryForComputeTradeoff`。**

> **③ `ParameterCount ≠ ServingMemoryProfile`。**

> **④ `MaxContext ≠ BestServingContext`。**

> **⑤ `PrefixCache` 主要节省重复 Prefill，必须看 Hit Rate。**

> **⑥ `BatchingGain` 受 KV Capacity 约束。**

> **⑦ `FreeVRAM ≠ AllocatableKV`。**

> **⑧ `TheoreticalMemory ≠ ReleaseEvidence`。**

> **⑨ KV Cache 是容量规划核心变量。**

---

# 下一阶段：第十课 · 第 4 阶段
# Paged Attention 与 vLLM：怎样提高显存利用率？

最关键的边界：

\[
\boxed{
ContiguousKVAllocation
\neq
EfficientDynamicServing
}
\]

并建立：

# `ProcurementPagedServingPolicy_V0.1`

---

<!-- LESSON 10 STAGE 03 END -->


<!-- LESSON 10 STAGE 04 START -->

# 第十课 · 第 4 阶段
# Paged Attention 与 vLLM：怎样提高显存利用率？
## 为什么传统 KV Cache 容易产生碎片和预留浪费？Paged Attention 怎样把“连续大块内存”问题变成“分页式动态分配”问题？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **ContiguousKVAllocation ≠ EfficientDynamicServing。**
2. **LogicalContinuity ≠ PhysicalContinuity。**
3. **Allocation Granularity 越细通常越省预留浪费，但管理开销更高。**
4. **Model ≠ Engine。**
5. **PagedKV + PrefixCache 可以联合优化，但收益取决于真实 Workload。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Attention` | 注意力：根据内容相关性动态聚合信息 |
| `KV Cache` | KV 缓存：生成时缓存历史 Key/Value 以减少重复计算 |
| `Serving` | 服务化：把模型包装成可扩展、可观测、可治理的在线服务 |
| `Block` | 版面块：文档解析后保留布局和位置的基本块 |
| `Memory` | 任务记忆：保存跨步骤需要复用的结构化信息 |
| `Batch` | 批次：一次参与计算的一组样本 |

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

第 3 阶段已经知道：

\[
\boxed{
LongContext\times HighConcurrency=KVPressure
}
\]

真实请求还有：

```text
长度不同
到达时间不同
结束时间不同
输出长度不可提前准确知道
```

如果每个请求都必须提前拿一大块连续 KV 空间，就容易出现：

```text
预留过多
碎片
并发受限
```

因此本阶段第一条边界：

\[
\boxed{
ContiguousKVAllocation
\neq
EfficientDynamicServing
}
\]

本阶段最终形成：

# `ProcurementPagedServingPolicy_V0.1`

---

# 一、为什么连续大块预留容易浪费？

假设请求最大输出：

```text
4096 tokens
```

如果一开始就预留 4096，

但实际只生成：

```text
500
```

剩余就是：

> 预留浪费。

再加上不同请求不断结束和释放，就会形成：

# Fragmentation
## 显存碎片

---

# 二、Paged Attention 的核心思想

把 KV Cache 切成固定大小：

# Blocks / Pages
## 块 / 页

逻辑序列：

```text
Token1 ... TokenN
```

不要求在物理显存中完全连续。

通过：

# Block Table
## 块映射表

记录逻辑位置到物理 Block 的映射。

因此：

\[
\boxed{
LogicalContinuity
\neq
PhysicalContinuity
}
\]

---

# 三、核心心智模型 ①
# Paged Attention 的本质是解耦逻辑序列与物理显存布局

这样可以：

```text
按需申请Block
动态增长
快速回收
降低连续内存要求
减少碎片
```

更适合动态 Serving。

---

# 四、为什么显存利用率通常会提高？

因为不再要求：

> 每个请求提前拿最大空间。

而是：

```text
需要多少
分配多少Block
```

所以：

\[
\boxed{
SmallerAllocationUnit
通常降低
ReservationWaste
}
\]

但 Block 太小也会增加管理开销。

因此：

\[
\boxed{
BlockSize
=
GranularityTradeoff
}
\]

---

# 五、vLLM 在这里是什么？

vLLM 可以理解为：

# Serving Engine
## 大模型推理服务引擎

它的重要职责包括：

```text
KV管理
请求调度
Continuous Batching
Prefix Cache
Kernel执行
```

所以：

\[
\boxed{
ServingEngine
=
Scheduling
+
MemoryManagement
+
KernelExecution
}
\]

不要把它理解成：

> “换一个库就自动变快。”

---

# 六、核心心智模型 ②
# `Model ≠ Serving Engine`

同一个：

```text
ProcurementLM_V0.2
```

换不同 Serving Engine，

可能得到完全不同：

```text
TTFT
TPOT
Throughput
VRAM
MaxConcurrency
```

因此性能由：

\[
\boxed{
Model
+
Engine
+
Hardware
+
Workload
}
\]

共同决定。

---

# 七、Paged KV 与 Prefix Cache

如果多个请求共享相同前缀，

可以复用物理 KV Block。

这与：

# Copy-on-Write
## 写时复制

思想相似：

> 共享直到分歧，再为新增部分分配新的 Block。

因此：

\[
\boxed{
PagedKV
+
PrefixCache
}
\]

可以联合减少：

```text
碎片
重复Prefill
重复KV存储
```

但前提仍然是：

> 真实业务确实存在高前缀复用。

---

# 八、Memory Optimization 不等于 Quality Improvement

Paged Attention 主要优化：

```text
显存管理
并发
吞吐
```

它不训练模型新知识。

所以：

\[
\boxed{
MemoryOptimization
\neq
ModelQualityImprovement
}
\]

但 Serving Engine 发生变化，仍需跑：

```text
ProcurementBench_V1
```

确认没有实现层回归。

---

# 九、Scheduler 同样重要

Block 管得好，

但 Scheduler 如果：

```text
让长Prefill独占GPU
让短请求一直排队
过度接收请求
```

用户体验仍然会差。

所以：

\[
\boxed{
EfficientMemory
\neq
EfficientScheduling
}
\]

---

# 十、怎样 Benchmark Paged Serving？

固定：

```text
模型
量化
硬件
Workload
```

比较不同 Engine / Config：

```text
Peak VRAM
KV Utilization
Max Concurrency
TTFT P50/P95/P99
TPOT
Output Tokens/s
OOM Rate
Queue Time
```

不能只用：

```text
最大并发
```

一个数字判断优劣。

---

# 十一、Engine 配置必须版本化

至少：

```text
engine_version
attention_backend
kv_block_size
scheduler_config
prefix_cache_config
memory_fraction
max_batched_tokens
max_sequences
quantization_kernel
```

所以：

\[
\boxed{
EngineConfig
\in
ServingArtifact
}
\]

---

# 十二、本阶段正式工程产物
# `ProcurementPagedServingPolicy_V0.1`

至少锁定：

```text
paged_serving_policy_version
model_version
engine_name
engine_version
attention_backend
kv_block_size
block_allocator
prefix_cache_enabled
shared_prefix_policy
scheduler_policy
memory_utilization_target
max_sequences
max_batched_tokens
admission_control
kv_fragmentation_metric
kv_utilization
max_concurrency
ttft
tpot
throughput
p95_p99
oom_rate
quality_regression
release_gate
```

---

# 十三、本阶段最重要的 8 个核心心智模型

> **① `ContiguousKVAllocation ≠ EfficientDynamicServing`。**

> **② `LogicalContinuity ≠ PhysicalContinuity`。**

> **③ Allocation Granularity 越细通常越省预留浪费，但管理开销更高。**

> **④ `Model ≠ Engine`。**

> **⑤ `PagedKV + PrefixCache` 可以联合优化，但收益取决于真实 Workload。**

> **⑥ `MemoryOptimization ≠ QualityImprovement`。**

> **⑦ `EfficientMemory ≠ EfficientScheduling`。**

> **⑧ Engine 优化最终仍要回到 SLO 和 `ProcurementBench_V1`。**

---

# 下一阶段：第十课 · 第 5 阶段
# Batching：Static、Dynamic、Continuous Batching

最关键的边界：

\[
\boxed{
MaxBatch
\neq
BestBatch
}
\]

并建立：

# `ProcurementBatchingPolicy_V0.1`

---

<!-- LESSON 10 STAGE 04 END -->


<!-- LESSON 10 STAGE 05 START -->

# 第十课 · 第 5 阶段
# Batching：Static、Dynamic、Continuous Batching
## 为什么一次服务多个请求能提高 GPU 利用率？为什么 Batch 太大又会伤害 TTFT、Queue 和 Tail Latency？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：MEDIUM。** 审计原因：核心心智模型出现偏后，阅读前段缺少认知锚点；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **MaxBatch ≠ BestBatch。**
2. **BatchSize ≠ TokenLoad。**
3. **Continuous Batching 解决请求生命周期不同步。**
4. **Prefill 与 Decode 会争 GPU，长 Prefill 会伤流式体验。**
5. **HigherBatch 用 Queue / Tail Latency 换 Throughput。**
6. **100% Accept ≠ ReliableService，过载时需要准入控制。**
7. **生产配置应该找 Knee Point，不是绝对最大吞吐。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Batch` | 批次：一次参与计算的一组样本 |
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `Continuous Batching` | 连续批处理：动态把不同时间到达的请求加入 GPU 批次 |
| `TTFT` | 首 Token 时间：用户等待第一个输出 Token 的时间 |
| `Latency` | 延迟：单个请求从进入到完成的时间 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Throughput` | 吞吐：单位时间内处理请求或生成 Token 的能力 |
| `Serving` | 服务化：把模型包装成可扩展、可观测、可治理的在线服务 |

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

第 4 阶段已经建立：

\[
\boxed{
EfficientMemory
\neq
EfficientScheduling
}
\]

现在进入吞吐最关键的调度机制之一：

# Batching
## 批处理

本阶段第一条边界：

\[
\boxed{
MaxBatch
\neq
BestBatch
}
\]

本阶段最终形成：

# `ProcurementBatchingPolicy_V0.1`

---

# 一、为什么 GPU 喜欢 Batch？

GPU 擅长并行。

如果每次只给一个小请求：

> 很多计算单元可能没有充分利用。

把多个请求组合：

```text
A
B
C
D
```

可以提高：

# Hardware Utilization
## 硬件利用率

所以：

\[
\boxed{
Batching
可以提高
Throughput
}
\]

---

# 二、Static Batching

固定收集 N 个请求：

```text
凑满Batch
↓
一起执行
↓
等整批结束
↓
开始下一批
```

优点：

> 简单。

问题：

```text
长度不同
输出时间不同
短请求被长请求拖住
新请求只能等下一批
```

所以：

\[
\boxed{
SameBatch
\neq
SameWork
}
\]

---

# 三、Batch Size 不等于计算量

请求：

```text
A：100 input / 20 output
B：20000 input / 2000 output
```

数量都算 1，

但计算量完全不同。

所以：

\[
\boxed{
BatchSize
\neq
TokenLoad
}
\]

更需要关注：

```text
batched tokens
active sequences
prefill tokens
decode tokens
```

---

# 四、Padding Waste

静态 Batch 中不同输入长度常需要补齐。

例如：

```text
100
200
2000
```

如果按 2000 处理，

大量补齐部分没有真实信息。

所以：

\[
\boxed{
Padding
=
PotentialComputeWaste
}
\]

---

# 五、Dynamic Batching

系统短暂等待，

把一小段时间内到达的请求组合起来。

收益：

> 吞吐提高。

代价：

> 等 Batch 本身产生 Queue Delay。

所以：

\[
\boxed{
BatchWindow
=
ThroughputLatencyTradeoff
}
\]

---

# 六、Continuous Batching

LLM 在线 Serving 更适合：

# Continuous Batching
## 连续批处理

每个 Decode Step 之后：

```text
完成请求
→ 退出

新请求
→ 加入
```

因此：

\[
\boxed{
BatchMembership
可以动态变化
}
\]

它解决的是：

> LLM 请求输出长度不同、生命周期不同步的问题。

---

# 七、核心心智模型 ①
# Continuous Batching 不是“大 Batch”，而是“动态 Batch”

重点不是：

> 一次装更多。

而是：

> 请求可以动态加入和退出。

---

# 八、长 Prefill 会伤害 Decode

一个：

```text
30000 Token Prefill
```

可能长时间占用 GPU。

已有流式请求：

> 等不到下一 Token。

这叫：

# Decode Stall
## 解码卡顿

所以：

\[
\boxed{
LongPrefill
可能伤害
ITL / TPOT
}
\]

---

# 九、Chunked Prefill

把超长 Prefill：

> 分成多个小块。

在中间穿插 Decode。

所以：

\[
\boxed{
ChunkedPrefill
=
PrefillDecodeSchedulingTool
}
\]

---

# 十、核心心智模型 ②
# Prefill 与 Decode 会争用同一套 GPU 资源

因此 Scheduler 必须决定：

```text
谁先跑
每次跑多少
何时切换
```

这已经超出简单 Batch Size。

---

# 十一、Max Batched Tokens

比：

```text
max_batch_size
```

更接近真实负载的是：

> 一次调度允许的总 Token 数。

因为：

\[
\boxed{
ComputeLoad
更接近
TokenVolume
}
\]

---

# 十二、为什么更大 Batch 会伤 TTFT？

为了凑 Batch：

> 请求要等。

Batch 本身更重：

> 单轮时间也可能更长。

因此：

\[
\boxed{
HigherBatch
可能提高Throughput
同时伤害TTFT
}
\]

---

# 十三、Fairness 与 Priority

可以区分：

```text
交互问答
高优先级

离线批量任务
低优先级
```

还要防止：

```text
长请求饿死短请求
短请求永远抢占长请求
```

所以需要：

# Fair Scheduling
## 公平调度

---

# 十四、Admission Control

系统接近饱和后，

继续无限接请求：

> 只会让 Queue 和 P99 爆炸。

所以可以：

```text
限流
排队
拒绝
降级
```

因此：

\[
\boxed{
100PercentAccept
\neq
ReliableService
}
\]

---

# 十五、Knee Point

性能 Sweep 时会看到：

```text
吞吐上升
↓
某一点之后
吞吐增长很少
但延迟急剧恶化
```

这个位置附近可以看作：

# Knee Point
## 性能拐点

生产通常应该：

> 留在拐点之前，并保留 Headroom。

所以：

\[
\boxed{
KneePoint
比
AbsoluteMaximum
更有生产意义
}
\]

---

# 十六、本阶段正式工程产物
# `ProcurementBatchingPolicy_V0.1`

至少锁定：

```text
batching_policy_version
serving_engine_version
static_batching
dynamic_batching
continuous_batching
batch_wait_window
max_sequences
max_batched_tokens
chunked_prefill
prefill_chunk_size
priority_classes
fairness_policy
admission_control
queue_limit
overload_policy
concurrency_sweep
workload_matrix
ttft_slo
p95_p99_slo
throughput_target
kv_capacity_constraint
oom_boundary
knee_point
release_gate
```

---

# 十七、本阶段最重要的 8 个核心心智模型

> **① `MaxBatch ≠ BestBatch`。**

> **② `BatchSize ≠ TokenLoad`。**

> **③ Continuous Batching 解决请求生命周期不同步。**

> **④ Prefill 与 Decode 会争 GPU，长 Prefill 会伤流式体验。**

> **⑤ `HigherBatch` 用 Queue / Tail Latency 换 Throughput。**

> **⑥ `100% Accept ≠ ReliableService`，过载时需要准入控制。**

> **⑦ 生产配置应该找 `Knee Point`，不是绝对最大吞吐。**

> **⑧ Batching 的目标仍然是满足 SLO。**

---

# 下一阶段：第十课 · 第 6 阶段
# Tensor Parallel、Pipeline Parallel 与多 GPU 推理

最关键的边界：

\[
\boxed{
MoreGPUs
\neq
LinearSpeedup
}
\]

并建立：

# `ProcurementParallelServingPolicy_V0.1`

---

<!-- LESSON 10 STAGE 05 END -->


<!-- LESSON 10 STAGE 06 START -->

# 第十课 · 第 6 阶段
# Tensor Parallel、Pipeline Parallel 与多 GPU 推理
## 单卡放不下模型怎么办？为什么加 GPU 不等于线性加速？模型到底应该按 Tensor、Layer 还是 Replica 拆？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **MoreGPUs ≠ LinearSpeedup。**
2. **ScaleUp ≠ ScaleOut。模型分片和多副本服务是两种不同扩展。**
3. **Tensor Parallel 用高频通信换取单层并行。**
4. **Pipeline Parallel 的关键是 Stage Balance，而不是层数平均。**
5. **单副本放不下才优先考虑 Sharding；放得下但吞吐不够优先考虑 Replica。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `Pipeline Parallel` | 流水线并行：把不同层/阶段分配到不同 GPU |
| `Tensor Parallel` | 张量并行：把同一层矩阵计算拆到多张 GPU |
| `Serving` | 服务化：把模型包装成可扩展、可观测、可治理的在线服务 |
| `Throughput` | 吞吐：单位时间内处理请求或生成 Token 的能力 |
| `Latency` | 延迟：单个请求从进入到完成的时间 |

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

当：

```text
模型Weight
+
KV Cache
+
Runtime
```

超过单卡能力，

或者单卡吞吐不够，

就要进入：

# Multi-GPU Inference
## 多 GPU 推理

本阶段第一条边界：

\[
\boxed{
MoreGPUs
\neq
LinearSpeedup
}
\]

本阶段最终形成：

# `ProcurementParallelServingPolicy_V0.1`

---

# 一、先区分三种常见扩展方式

## Tensor Parallel
### 张量并行

把同一层里的大矩阵运算：

> 横向切到多张 GPU。

## Pipeline Parallel
### 流水线并行

把不同 Layer：

> 纵向分到不同 GPU / Stage。

## Replica Serving
### 多副本服务

每组 GPU：

> 放一份完整模型，由负载均衡器把不同请求分发给不同副本。

所以：

\[
\boxed{
ScaleUp
\neq
ScaleOut
}
\]

前两者是把一个模型拆开，

Replica 更像把完整服务复制多份。

---

# 二、Tensor Parallel

大矩阵 \(W\) 可以被切到：

```text
GPU0
GPU1
GPU2
GPU3
```

各自计算部分结果，再通过：

```text
All-Reduce
All-Gather
Reduce-Scatter
```

等通信组合。

所以：

\[
\boxed{
TPGain
=
ParallelCompute
-
CommunicationCost
}
\]

因此高速互联非常重要。

---

# 三、核心心智模型 ①
# `Interconnect` 属于模型推理性能的一部分

同样四张 GPU，

如果互联带宽不同，

TP 性能可能差很多。

所以：

\[
\boxed{
4GPUs
\neq
4GPUs
}
\]

真正硬件描述要包括：

```text
GPU型号
单机卡数
显存
GPU互联
节点网络
NUMA
```

---

# 四、TP Degree 为什么不是越大越好？

TP Degree 增大：

```text
每卡Weight减少
计算更分散
```

但也会：

```text
通信更多
同步更多
Kernel更碎
```

所以：

\[
\boxed{
TPDegree
存在最优区间
}
\]

---

# 五、Pipeline Parallel

例如：

```text
GPU0：Layer 1-10
GPU1：Layer 11-20
GPU2：Layer 21-30
GPU3：Layer 31-40
```

数据依次穿过 Stage。

因此：

\[
\boxed{
PP
=
LayerPartitioning
}
\]

但如果某个 Stage 特别慢，

其他 Stage 就会等待。

这形成：

# Pipeline Bubble
## 流水线气泡

所以：

\[
\boxed{
PipelineBalance
决定
PPEfficiency
}
\]

---

# 六、核心心智模型 ②
# `EqualLayerCount` 不一定等于 `EqualWork`

不同 Layer 的：

```text
算力
显存
KV
通信
```

可能不同。

所以 Pipeline 切分不能只按层数平均。

---

# 七、Replica Serving

如果模型本身已经能放进一组 GPU，

但总流量太大，

可以：

```text
Replica A
Replica B
Replica C
```

每个副本各自服务请求。

这时扩的是：

> 总吞吐。

所以：

\[
\boxed{
ModelDoesNotFit
\rightarrow
Sharding
}
\]

\[
\boxed{
ModelFitsButTrafficHigh
\rightarrow
Replication
}
\]

---

# 八、核心心智模型 ③
# 先问“放不下”还是“吞吐不够”

Parallelism Choice 必须由 Bottleneck Type 决定。

盲目提高 TP：

> 可能增加通信，却没有解决真正问题。

---

# 九、组合并行

可以：

```text
TP=4
×
3 Replicas
```

也可以：

```text
TP + PP
```

但越复杂：

```text
调度
通信
故障
发布
监控
```

越复杂。

所以：

\[
\boxed{
MoreParallelism
=
MoreCoordination
}
\]

---

# 十、多节点为什么更难？

跨节点：

```text
延迟更高
带宽更低
故障点更多
```

对于通信密集型 TP，

网络可能直接成为瓶颈。

所以：

\[
\boxed{
Topology
必须进入
ParallelPlan
}
\]

---

# 十一、Latency 和 Throughput 要分开评

TP：

> 可能改变单请求延迟。

Replica：

> 主要提升总吞吐。

PP：

> 让更大模型可部署，但可能带来流水线延迟。

所以：

\[
\boxed{
Parallelism
必须分别评
Latency
和
Throughput
}
\]

---

# 十二、Fault Domain

如果一个服务实例由很多 GPU 共同组成，

任意一张卡故障：

> 可能让整个实例不可用。

所以：

\[
\boxed{
LargerShardGroup
可能扩大
FailureImpact
}
\]

性能拓扑：

> 同时也是可靠性拓扑。

---

# 十三、Parallel Benchmark

至少比较：

```text
单卡 / 单组基线

TP=2

TP=4

Replica x2

TP=2 + Replica x2
```

记录：

```text
TTFT
TPOT
Throughput
P95/P99
GPU Utilization
Interconnect Traffic
Cost
Fault Impact
```

---

# 十四、本阶段正式工程产物
# `ProcurementParallelServingPolicy_V0.1`

至少锁定：

```text
parallel_policy_version
model_version
hardware_topology
gpu_model
gpus_per_node
interconnect
tensor_parallel_degree
pipeline_parallel_degree
replica_count
pipeline_partition
load_balancer_policy
communication_backend
max_context
concurrency
ttft
tpot
throughput
p95_p99
interconnect_utilization
gpu_memory
cost
fault_domain
failure_recovery
quality_regression
release_gate
```

---

# 十五、本阶段最重要的 8 个核心心智模型

> **① `MoreGPUs ≠ LinearSpeedup`。**

> **② `ScaleUp ≠ ScaleOut`。模型分片和多副本服务是两种不同扩展。**

> **③ Tensor Parallel 用高频通信换取单层并行。**

> **④ Pipeline Parallel 的关键是 Stage Balance，而不是层数平均。**

> **⑤ 单副本放不下才优先考虑 Sharding；放得下但吞吐不够优先考虑 Replica。**

> **⑥ Parallelism Choice 必须由 Bottleneck 与 Hardware Topology 共同决定。**

> **⑦ `4GPUs ≠ 4GPUs`，互联拓扑会改变真实性能。**

> **⑧ 性能拓扑同时也是故障拓扑。**

---

# 下一阶段：第十课 · 第 7 阶段
# Serving Architecture：把 Model + RAG + Agent 接成真实 API 服务

最关键的边界：

\[
\boxed{
Deployment
\neq
ModelLoading
}
\]

并建立：

# `ProcurementServingArchitecture_V0.1`

---

<!-- LESSON 10 STAGE 06 END -->


<!-- LESSON 10 STAGE 07 START -->

# 第十课 · 第 7 阶段
# Serving Architecture：把 Model + RAG + Agent 接成真实 API 服务
## 模型能启动，不代表系统能上线。怎样把 Gateway、Model Server、Retriever、Agent、Tool、State、Queue、Auth 和 Trace 真正接成生产服务？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Deployment ≠ ModelLoading。**
2. **ProductionAI = ModelSystem + DistributedSystem。**
3. **Traceability 从统一 Request ID 开始。**
4. **AgentControlPlane ≠ ModelExecutionPlane。**
5. **Decision ≠ Authorization。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `State` | 状态：保存任务进度、事实和待办 |
| `Serving` | 服务化：把模型包装成可扩展、可观测、可治理的在线服务 |
| `Idempotency` | 幂等：重复执行不会产生不可控重复副作用 |
| `Observability` | 可观测性：通过指标、日志、追踪理解系统内部状态 |

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

到第 6 阶段，我们已经解决：

```text
显存
Batch
Inference Engine
多GPU
```

但生产系统不是：

```text
python model.generate()
```

它还必须面对：

```text
鉴权
限流
排队
超时
重试
RAG
Agent
Tool
状态
日志
审计
```

所以本阶段第一条边界：

\[
\boxed{
Deployment
\neq
ModelLoading
}
\]

本阶段最终形成：

# `ProcurementServingArchitecture_V0.1`

---

# 一、完整生产链

```text
Client
↓
API Gateway
↓
Auth / Rate Limit
↓
Request Router
↓
RAG / Agent Orchestrator
↓
Model Server
↓
Tool Services
↓
State / DB / Cache
↓
Response Stream
```

每一层都可能成为：

> 性能瓶颈、故障点或安全边界。

---

# 二、核心心智模型 ①
# `ProductionAI = ModelSystem + DistributedSystem`

模型只是其中一个组件。

真正上线后，

我们面对的是：

> 分布式系统问题。

---

# 三、API Gateway

至少负责：

```text
Authentication
鉴权

Authorization
授权

Rate Limiting
限流

Routing
路由

Quota
配额

TLS
加密传输
```

它是外部流量进入系统的第一层控制面。

---

# 四、Request ID

每个请求创建：

```text
request_id
```

并贯穿：

```text
Gateway
RAG
Model
Agent
Tool
Database
```

所以：

\[
\boxed{
Traceability
从
RequestID
开始
}
\]

---

# 五、核心心智模型 ②
# 没有统一 Request ID，就没有真正端到端追踪

日志再多，

如果无法串成同一个请求：

> 排障仍然很困难。

---

# 六、RAG Service

RAG 可以独立：

```text
Retriever
Reranker
Context Builder
```

好处：

```text
独立扩容
独立版本化
独立回滚
```

因此：

\[
\boxed{
RAGVersion
\neq
ModelVersion
}
\]

---

# 七、Agent Orchestrator

它负责：

```text
Goal
Plan
Tool Routing
State
Retry
Human Escalation
Completion
```

而 Model Server：

> 负责推理执行。

所以：

\[
\boxed{
AgentControlPlane
\neq
ModelExecutionPlane
}
\]

---

# 八、Tool Service

工具可能：

```text
查预算
写数据库
提交审批
发送消息
```

所以必须有：

```text
权限
超时
幂等
审计
重试策略
```

模型可以决定：

> 想调用什么。

但系统策略决定：

> 能不能调用。

所以：

\[
\boxed{
Decision
\neq
Authorization
}
\]

---

# 九、Timeout Budget

整个请求：

> 应有总超时预算。

内部组件：

```text
RAG
Model
Tool
Database
```

也要有分层 Timeout。

否则一个依赖卡住：

> 整条链都会无限等待。

---

# 十、Retry 与 Idempotency

读请求：

> 通常更容易安全重试。

写请求：

> 可能产生重复副作用。

所以：

\[
\boxed{
RetryPolicy
必须感知
Idempotency
}
\]

---

# 十一、Circuit Breaker

如果某个依赖持续失败，

继续调用会放大故障。

所以：

# Circuit Breaker
## 熔断器

在达到阈值时：

> 暂停调用、降级或转人工。

---

# 十二、核心心智模型 ③
# `RetryEverything` 会把局部故障变成雪崩

成熟 Retry 必须考虑：

```text
上限
Backoff
Jitter
Idempotency
Circuit Breaker
```

---

# 十三、Backpressure

下游模型满载时，

上游不能无限灌请求。

需要：

# Backpressure
## 背压

可以通过：

```text
限流
排队
降级
拒绝
```

保护下游。

---

# 十四、业务 State 不能只存在 Prompt 里

真实状态应该存：

```text
Database
Durable Store
State Service
```

模型上下文只是：

# Working Context
## 工作上下文

所以：

\[
\boxed{
BusinessState
\neq
PromptMemory
}
\]

---

# 十五、Streaming 与 Cancellation

流式服务还要处理：

```text
连接保持
客户端取消
断线
中途超时
```

如果用户取消：

> 后端应该尽快停止 Decode。

所以：

\[
\boxed{
ClientCancellation
\rightarrow
ComputeCancellation
}
\]

---

# 十六、Observability 与 Privacy

更多日志：

> 更容易排障。

但也带来：

```text
隐私
敏感数据
留存
访问风险
```

因此：

\[
\boxed{
Observability
必须和
Privacy
一起设计
}
\]

---

# 十七、System Version

生产版本不能只记：

```text
model=v0.2
```

还要记：

```text
rag_index_version
retriever_version
reranker_version
agent_policy_version
tool_registry_version
prompt_version
gateway_version
serving_engine_version
```

所以：

\[
\boxed{
SystemVersion
>
ModelVersion
}
\]

这里表示：

> 系统版本包含更多依赖。

---

# 十八、本阶段正式工程产物
# `ProcurementServingArchitecture_V0.1`

至少锁定：

```text
serving_architecture_version
api_gateway
auth_policy
authorization_policy
rate_limit
request_id_policy
router
model_server_version
rag_service_version
retriever_version
reranker_version
agent_orchestrator_version
tool_registry_version
tool_auth_policy
state_store
cache
timeout_budget
retry_policy
idempotency_policy
circuit_breaker
backpressure
queue_policy
streaming
cancellation
privacy_logging_policy
trace_context
release_gate
```

---

# 十九、本阶段最重要的 9 个核心心智模型

> **① `Deployment ≠ ModelLoading`。**

> **② `ProductionAI = ModelSystem + DistributedSystem`。**

> **③ Traceability 从统一 Request ID 开始。**

> **④ `AgentControlPlane ≠ ModelExecutionPlane`。**

> **⑤ `Decision ≠ Authorization`。**

> **⑥ Retry 必须与 Idempotency、Backoff、Circuit Breaker 联动。**

> **⑦ `BusinessState ≠ PromptMemory`。**

> **⑧ Client Cancellation 应传播到计算层。**

> **⑨ `SystemVersion > ModelVersion`。**

---

# 下一阶段：第十课 · 第 8 阶段
# Observability：Metrics、Logs、Tracing、GPU 与业务监控

最关键的边界：

\[
\boxed{
Monitoring
\neq
GPUUtilizationOnly
}
\]

并建立：

# `ProcurementObservabilityPolicy_V0.1`

---

<!-- LESSON 10 STAGE 07 END -->


<!-- LESSON 10 STAGE 08 START -->

# 第十课 · 第 8 阶段
# Observability：Metrics、Logs、Tracing、GPU 与业务监控
## 线上突然变慢、答错、RAG 漏检、Agent 工具失败，到底怎样知道“发生了什么、发生在哪一层、影响多少用户”？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Monitoring ≠ GPUUtilizationOnly。**
2. **Observability = Metrics + Logs + Traces + Quality + Cost。**
3. **HealthyGPU ≠ HealthyAI。**
4. **Metrics 适合聚合，Logs/Traces 适合高基数细节。**
5. **没有 Trace Span 只能知道慢，不能知道哪里慢。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `Observability` | 可观测性：通过指标、日志、追踪理解系统内部状态 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `Monitoring` | 监控：持续观察系统、模型和业务指标是否健康 |
| `Latency` | 延迟：单个请求从进入到完成的时间 |

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

系统上线以后，

最危险的不只是：

> 出问题。

而是：

> **出了问题却不知道原因。**

所以本阶段第一条边界：

\[
\boxed{
Monitoring
\neq
GPUUtilizationOnly
}
\]

本阶段最终形成：

# `ProcurementObservabilityPolicy_V0.1`

---

# 一、Monitoring 与 Observability

# Monitoring
## 监控

关注：

> 已知指标有没有异常。

# Observability
## 可观测性

关注：

> 能否通过系统产生的信号推断内部发生了什么。

经典三类信号：

```text
Metrics
Logs
Traces
```

对 AI 系统还要补：

```text
Quality Signals
Cost Signals
```

所以：

\[
\boxed{
Observability
=
Metrics
+
Logs
+
Traces
+
Quality
+
Cost
}
\]

---

# 二、Metrics 至少分四层

## Infrastructure

```text
GPU Utilization
GPU Memory
CPU
RAM
Network
Disk
```

## Inference

```text
TTFT
TPOT
E2E
Queue Time
Tokens/s
Batch
KV Utilization
OOM
```

## Application

```text
Request Rate
Error Rate
Timeout
Retry
RAG Latency
Tool Failure
```

## Quality

```text
Abstention Rate
Citation Failure
User Correction
Escalation Rate
Audit Failure
```

---

# 三、核心心智模型 ①
# `HealthyGPU ≠ HealthyAI`

GPU 95% 利用率、

没有 OOM，

但系统仍可能：

```text
引用错误
RAG漏检
Agent重复提交
```

所以：

\[
\boxed{
InfrastructureHealth
\neq
ProductQuality
}
\]

---

# 四、Golden Signals

传统服务常关注：

```text
Latency
Traffic
Errors
Saturation
```

AI 系统还应该显式加入：

```text
Quality
Cost
```

所以：

\[
\boxed{
AIServiceHealth
=
Latency
+
Traffic
+
Errors
+
Saturation
+
Quality
+
Cost
}
\]

---

# 五、Logs

日志可以记录：

```text
request_id
model_version
prompt_version
rag_version
tool_calls
status_code
latency
token_count
error_code
```

但用户原文、采购文件、敏感字段：

> 需要脱敏和留存策略。

所以：

\[
\boxed{
MoreLogs
\neq
BetterObservability
}
\]

日志应该：

> 结构化、分级、采样、可关联。

---

# 六、Tracing

一次请求可能：

```text
Gateway
↓
Retriever
↓
Reranker
↓
LLM
↓
Tool A
↓
LLM
↓
Tool B
```

总延迟 12 秒时，

Trace 可以告诉我们：

> 哪个步骤耗了多少时间。

所以：

\[
\boxed{
Trace
=
LatencyAttribution
+
FailureAttribution
}
\]

---

# 七、Span

Trace 中每个步骤是：

# Span
## 链路片段

例如：

```text
retrieval_span
rerank_span
prefill_span
decode_span
tool_span
```

没有 Span：

> 只能知道“慢”。

有 Span：

> 才能知道“哪里慢”。

---

# 八、核心心智模型 ②
# Metrics 聚合，Logs / Traces 解释细节

像：

```text
request_id
document_id
```

这种高基数字段，

不适合无限作为 Metric Label。

所以：

\[
\boxed{
Metrics
用于Aggregation
}
\]

\[
\boxed{
Logs/Traces
用于HighCardinalityDetail
}
\]

---

# 九、SLO 与 Error Budget

当 SLO 明确以后，

允许的失败空间可以理解为：

# Error Budget
## 错误预算

它可以帮助决定：

> 当前应该继续发布新功能，还是先修稳定性。

所以：

\[
\boxed{
ErrorBudget
=
ReliabilityChangeBudget
}
\]

---

# 十、核心心智模型 ③
# SLO 不是 Dashboard 装饰，而是发布节奏控制器

Error Budget 接近耗尽时：

> 应降低发布频率、优先恢复稳定性。

---

# 十一、Alert

好的告警应该对应：

```text
SLO风险
用户影响
安全异常
资源耗尽
```

例如：

```text
P99 TTFT持续超阈值
OOM上升
Queue持续增长
Tool权限错误
Critical Citation Error
```

告警太多会造成：

# Alert Fatigue
## 告警疲劳

所以：

\[
\boxed{
AlertVolume
\neq
OperationalAwareness
}
\]

---

# 十二、Online Quality Monitoring

线上可以观察：

```text
用户纠错率
人工转交率
拒答率
引用失败率
工具失败率
抽样人工审核
```

它们是：

# Proxy Signals
## 代理质量信号

但：

\[
\boxed{
OnlineSignal
\neq
GroundTruth
}
\]

不能完全替代：

```text
ProcurementBench_V1
```

---

# 十三、Drift Monitoring

线上输入可能变化：

```text
文档更长
行业变化
新格式
OCR质量下降
```

因此要监控：

# Input Drift
## 输入漂移

以及：

# Output Drift
## 输出漂移

例如：

```text
标签分布
拒答率
输出长度
风险类型分布
```

---

# 十四、Cost Monitoring

成本与：

```text
Input Tokens
Output Tokens
GPU Time
Tool Calls
Retrieval
```

相关。

可以记录：

```text
cost_per_request
cost_per_1k_requests
cost_per_successful_task
```

所以：

\[
\boxed{
CostPerSuccessfulOutcome
>
CostPerRequest
}
\]

这里表示：

> 更接近真实效率。

---

# 十五、本阶段正式工程产物
# `ProcurementObservabilityPolicy_V0.1`

至少锁定：

```text
observability_policy_version
metric_catalog
log_schema
trace_schema
request_id
trace_id
span_policy
gpu_metrics
inference_metrics
rag_metrics
agent_metrics
tool_metrics
quality_proxy_metrics
cost_metrics
slo_dashboard
error_budget
alert_rules
alert_severity
sampling_policy
pii_redaction
retention_policy
drift_monitoring
online_audit
incident_linkage
release_gate
```

---

# 十六、本阶段最重要的 9 个核心心智模型

> **① `Monitoring ≠ GPUUtilizationOnly`。**

> **② `Observability = Metrics + Logs + Traces + Quality + Cost`。**

> **③ `HealthyGPU ≠ HealthyAI`。**

> **④ Metrics 适合聚合，Logs/Traces 适合高基数细节。**

> **⑤ 没有 Trace Span 只能知道慢，不能知道哪里慢。**

> **⑥ `SLO + ErrorBudget` 应控制发布节奏。**

> **⑦ `AlertVolume ≠ Awareness`。**

> **⑧ `OnlineSignal ≠ GroundTruth`。**

> **⑨ `CostPerSuccessfulOutcome` 比单纯 Cost per Request 更完整。**

---

# 下一阶段：第十课 · 第 9 阶段
# Model Versioning、Canary、Shadow、A/B 与 Rollback

最关键的边界：

\[
\boxed{
NewVersionReady
\neq
NewVersionShouldReceive100PercentTraffic
}
\]

并建立：

# `ProcurementReleaseRolloutPolicy_V0.1`

---

<!-- LESSON 10 STAGE 08 END -->


<!-- LESSON 10 STAGE 09 START -->

# 第十课 · 第 9 阶段
# Model Versioning、Canary、Shadow、A/B 与 Rollback
## 新模型为什么不能直接全量替换？怎样用 Canary、Shadow、A/B、Feature Flag 和 Rollback 把发布风险限制在可控范围？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **NewVersionReady ≠ 100% Traffic Ready。**
2. **ProductionVersion = ArtifactBundle。**
3. **Canary = LimitBlastRadius。**
4. **Shadow 用真实流量观察，但必须阻断真实副作用。**
5. **A/B 测真实用户因果效果，Shadow 更适合先测技术风险。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Rollback` | 回滚：出现问题时恢复上一稳定系统版本 |
| `Canary` | 灰度发布：让有限真实流量先使用新版本 |
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |

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

一个版本通过：

```text
ProcurementBench_V1
```

仍然不代表：

> 可以直接接 100% 真实流量。

因为生产还有：

```text
真实流量
真实并发
真实工具
真实依赖
真实故障
```

所以本阶段第一条边界：

\[
\boxed{
NewVersionReady
\neq
NewVersionShouldReceive100PercentTraffic
}
\]

本阶段最终形成：

# `ProcurementReleaseRolloutPolicy_V0.1`

---

# 一、Production Version 是 Artifact Bundle

至少包含：

```text
Model
Tokenizer
Quantization
Prompt
RAG Index
Retriever
Reranker
Agent Policy
Tool Registry
Thresholds
Serving Engine
Runtime Config
```

因此：

\[
\boxed{
ProductionVersion
=
ArtifactBundle
}
\]

而不是：

> 一个模型文件。

---

# 二、核心心智模型 ①
# `ModelVersion` 只是 `SystemVersion` 的一个节点

Prompt、RAG Index、Threshold：

> 任一个变化都可能改变系统行为。

所以所有生产变更都要进入：

> Release Trace。

---

# 三、Canary

# Canary Release
## 金丝雀发布

先让新版本接：

```text
1%
5%
10%
```

小流量，

观察：

```text
SLO
错误率
质量代理指标
成本
Tool失败
```

稳定后再扩大。

所以：

\[
\boxed{
Canary
=
LimitBlastRadius
}
\]

---

# 四、核心心智模型 ②
# Canary 的核心不是“慢慢上线”，而是限制故障爆炸半径

如果新版本有隐藏问题：

> 只影响少量用户。

---

# 五、Shadow Traffic

真实请求同时复制给：

```text
Champion
Challenger
```

但用户只看到 Champion。

Challenger 结果：

> 只用于评估。

所以：

\[
\boxed{
Shadow
=
ProductionWorkload
WithoutUserImpact
}
\]

---

# 六、Shadow 的副作用安全

如果 Agent 会：

```text
提交
写数据库
发送
审批
```

不能直接 Shadow 执行真实副作用。

需要：

```text
Dry Run
Mock
Sandbox
```

所以：

\[
\boxed{
ShadowSafety
必须感知
SideEffects
}
\]

---

# 七、A/B Test

随机把真实用户分到：

```text
A = Champion
B = Challenger
```

比较：

```text
成功率
完成率
延迟
转人工
成本
```

所以 A/B 更适合：

> 测真实用户因果效果。

Shadow 更适合：

> 先测技术风险。

---

# 八、核心心智模型 ③
# 风险可以逐步增加

一种典型路线：

```text
Offline Benchmark
↓
Shadow
↓
Canary
↓
A/B
↓
Full Rollout
```

不是唯一固定顺序，

但体现：

> 从低风险证据到高风险真实流量。

---

# 九、Feature Flag

可以运行时控制：

```text
新模型
新RAG
新Agent工具
新Prompt
```

是否启用。

所以：

\[
\boxed{
FeatureFlag
=
RuntimeReleaseControl
}
\]

---

# 十、Rollback

必须提前定义：

```text
previous_stable_version
compatibility_matrix
rollback_trigger
rollback_action
rollback_validation
```

所以：

\[
\boxed{
ReleaseReady
\Rightarrow
RollbackReady
}
\]

---

# 十一、核心心智模型 ④
# Rollback 不等于只换回旧 Weight

如果新版本还改了：

```text
Tokenizer
Prompt Schema
RAG Index
Agent State
Tool API
```

只换模型：

> 可能不兼容。

所以必须有：

# Compatibility Matrix
## 兼容矩阵

---

# 十二、State / Schema Migration

新 Agent 如果写入了新状态格式，

旧版本可能无法读取。

因此要区分：

```text
Backward Compatible
Forward Compatible
Breaking Change
```

所以：

\[
\boxed{
Rollbackability
必须在
Schema设计阶段考虑
}
\]

---

# 十三、Rollback Trigger

可以来自：

```text
P99超阈值
OOM
Critical Error
Tool Side Effect
错误率
质量代理指标异常
成本异常
```

这些触发条件应该：

> 预先定义。

所以：

\[
\boxed{
Rollback
=
PolicyDriven
}
\]

---

# 十四、Automatic Rollback

基础设施信号：

```text
OOM
错误率
延迟
```

更适合自动化。

复杂质量问题：

> 可能需要人工确认。

所以：

\[
\boxed{
AutomationLevel
取决于
SignalReliability
}
\]

---

# 十五、核心心智模型 ⑤
# `FastRollback` 比 `PerfectDetection` 更现实

生产不可能提前发现所有问题。

所以成熟系统必须：

> 能快速限制影响。

---

# 十六、Release Manifest

每次发布至少记录：

```text
release_id
system_version
model_version
quantization_version
prompt_version
rag_index_version
agent_policy_version
serving_engine_version
feature_flags
traffic_percentage
benchmark_result
slo_result
rollback_target
```

因此：

\[
\boxed{
WhatIsRunningNow
必须机器可回答
}
\]

---

# 十七、本阶段正式工程产物
# `ProcurementReleaseRolloutPolicy_V0.1`

至少锁定：

```text
rollout_policy_version
release_manifest_schema
champion_version
challenger_version
shadow_policy
canary_stages
traffic_split
ab_test_policy
feature_flags
side_effect_shadow_policy
compatibility_matrix
rollback_target
rollback_trigger
automatic_rollback
manual_approval
rollback_validation
database_migration_policy
state_compatibility
slo_guardrail
quality_guardrail
cost_guardrail
release_audit
```

---

# 十八、本阶段最重要的 9 个核心心智模型

> **① `NewVersionReady ≠ 100% Traffic Ready`。**

> **② `ProductionVersion = ArtifactBundle`。**

> **③ `Canary = LimitBlastRadius`。**

> **④ Shadow 用真实流量观察，但必须阻断真实副作用。**

> **⑤ A/B 测真实用户因果效果，Shadow 更适合先测技术风险。**

> **⑥ `ReleaseReady ⇒ RollbackReady`。**

> **⑦ Rollback 是兼容性问题，不只是旧 Weight 重部署。**

> **⑧ `FastRollback` 是生产安全核心能力。**

> **⑨ `WhatIsRunningNow` 必须机器可查询。**

---

# 下一阶段：第十课 · 第 10 阶段
# 真正部署 `ProcurementAI`：性能压测、SLO、Release Gate 与生产闭环

最关键的总边界：

\[
\boxed{
DeploymentSuccess
\neq
ProductionReadiness
}
\]

最终交付：

# `ProcurementAI`

---

<!-- LESSON 10 STAGE 09 END -->


<!-- LESSON 10 STAGE 10 START -->

# 第十课 · 第 10 阶段
# 真正部署 `ProcurementAI`：性能压测、SLO、Release Gate 与生产闭环
## 怎样把 Quantization、KV Cache、Paged Attention、Batching、多 GPU、Serving、Observability、Canary 和 Rollback 全部接成一套真正可上线的生产系统？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **GoodModel ≠ GoodProductionSystem。**
2. **Latency ≠ Throughput。**
3. **Quantization ≠ FreeCompression。**
4. **ModelFitsInGPU ≠ ServingFitsInGPU。**
5. **EfficientMemory ≠ EfficientScheduling。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Serving` | 服务化：把模型包装成可扩展、可观测、可治理的在线服务 |
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `Observability` | 可观测性：通过指标、日志、追踪理解系统内部状态 |
| `Rollback` | 回滚：出现问题时恢复上一稳定系统版本 |
| `Batch` | 批次：一次参与计算的一组样本 |
| `Quantization` | 量化：用更低位宽表示权重/激活以降低显存和计算成本 |

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

前 9 个阶段已经分别解决：

```text
性能指标
量化
KV Cache
Paged Attention
Batching
多GPU
Serving Architecture
Observability
灰度与回滚
```

第 10 阶段不再增加孤立技巧。

它要把全部机制接成：

# `ProcurementAI`

本阶段第一条总边界：

\[
\boxed{
DeploymentSuccess
\neq
ProductionReadiness
}
\]

服务能启动：

> 只是 Deployment Success。

真正 Production Ready：

> 还需要质量、容量、可靠性、监控、成本和回滚全部闭环。

---

# 一、`ProcurementAI` 到底是什么？

它不是单个模型。

而是：

\[
\boxed{
ProcurementAI
=
Model
+
RAG
+
Agent
+
Serving
+
Observability
+
ReleaseControl
+
BenchmarkGovernance
}
\]

更具体：

```text
ProcurementLM_V0.2
+
ProcurementRAG_V0.1
+
ProcurementAgent_V0.1
+
ProcurementBench_V1
+
Production Serving Stack
```

所以：

\[
\boxed{
AIProduct
\neq
LLMFile
}
\]

---

# 二、核心心智模型 ①
# Production Readiness 是“系统状态”，不是“部署动作”

至少同时看：

```text
Quality
Performance
Capacity
Reliability
Security
Observability
Rollback
Cost
```

---

# 三、Serving Plane 与 Control Plane

# Serving Plane
## 服务平面

```text
Client
↓
Gateway
↓
RAG / Agent
↓
Inference Cluster
↓
Tools / State
↓
Response
```

# Control Plane
## 控制平面

```text
Benchmark
Release
Version
Canary
Rollback
Policy
```

所以：

\[
\boxed{
ProductionSystem
=
ServingPlane
+
ControlPlane
}
\]

---

# 四、核心心智模型 ②
# 只会 Serving，不会治理；只会 Benchmark，又不能生产运行

成熟系统需要：

\[
\boxed{
RuntimeExecution
+
LifecycleControl
}
\]

---

# 五、Load Test 要测真实 Workload Matrix

不是只压：

```text
最大QPS
```

而是：

```text
短问答 × 低并发
短问答 × 高并发
长RAG × 中并发
长文档 × 高输出
Agent多Tool × 外部延迟
真实混合Traffic
```

记录：

```text
TTFT
TPOT
P95/P99
Throughput
Queue
OOM
Error
Cost
```

---

# 六、Capacity Planning

不能直接拿峰值压测结果当生产容量。

还要留：

# Headroom
## 容量余量

用于：

```text
突发流量
节点故障
双版本发布
依赖变慢
未来增长
```

所以：

\[
\boxed{
ProductionCapacity
<
TheoreticalMaximum
}
\]

这是有意保守。

---

# 七、核心心智模型 ③
# `PeakBenchmark ≠ CapacityPlan`

容量规划需要：

\[
\boxed{
Workload
+
SLO
+
FailureMargin
}
\]

---

# 八、Autoscaling

可以依据：

```text
Queue Depth
Request Rate
KV Utilization
GPU Utilization
TTFT
```

扩缩容。

但大模型加载和 Warm-up：

> 需要时间。

所以：

\[
\boxed{
ReactiveScaling
可能太晚
}
\]

高峰前预热、预扩容可能更重要。

---

# 九、Failure Injection

上线前要主动模拟：

```text
GPU进程退出
Retriever超时
Tool 500
数据库变慢
节点丢失
网络抖动
RAG Index不可用
```

看系统能否：

```text
降级
熔断
重试
转人工
回滚
恢复
```

所以：

\[
\boxed{
ReliableSystem
必须被
FailureTest
证明
}
\]

---

# 十、Graceful Degradation

组件故障时可以：

```text
RAG失败
→ 明确提示无法获得可靠证据

Tool失败
→ 转人工

高负载
→ 降低输出上限

主模型失败
→ 切备用模型
```

所以：

\[
\boxed{
GracefulDegradation
优于
TotalFailure
}
\]

---

# 十一、最终 Serving Build 必须重新跑质量 Benchmark

最终生产配置已经改变：

```text
Quantization
Engine
Batching
Parallelism
Prompt
RAG
Agent
```

所以必须再次通过：

\[
\boxed{
ProcurementBench_V1
}
\]

因此：

\[
\boxed{
TrainingCheckpointPass
\neq
ServingBuildPass
}
\]

用户真正使用的是：

> Serving Build。

---

# 十二、最终 Release Gate

可以概念化：

\[
ReleaseGate
=
G_{quality}
\land
G_{latency}
\land
G_{throughput}
\land
G_{capacity}
\land
G_{reliability}
\land
G_{observability}
\land
G_{rollback}
\land
G_{security}
\land
G_{cost}
\]

全部通过：

\[
\boxed{
ProductionReady=True
}
\]

---

# 十三、核心心智模型 ④
# Release Gate 必须是多维 AND，而不是平均分

不能：

```text
质量100
安全30
延迟90
```

平均后说：

> 可以上线。

关键失败必须直接 Block。

---

# 十四、Runbook

# Runbook
## 运行手册

必须提前写：

```text
OOM怎么办
P99暴涨怎么办
RAG不可用怎么办
Agent重复提交怎么办
Critical Error怎么办
怎样回滚
怎样扩容
谁负责
```

所以：

\[
\boxed{
OperationalKnowledge
也必须资产化
}
\]

---

# 十五、Production Feedback Loop

上线后持续收集：

```text
失败样本
人工纠错
低置信样本
OOD
Critical Incident
Latency Outlier
RAG Miss
Tool Failure
```

再进入：

```text
Benchmark Candidate Pool
Data Pipeline
Model Improvement
```

形成：

\[
\boxed{
Production
\rightarrow
Evidence
\rightarrow
Benchmark
\rightarrow
Improvement
\rightarrow
Release
}
\]

---

# 十六、核心心智模型 ⑤
# 生产不是终点，而是下一轮学习的真实证据源

真实用户会暴露：

> Benchmark 没覆盖的新失败模式。

所以生产反馈必须回流。

---

# 十七、完整 `ProcurementAI` Artifact Tree

```text
ProcurementAI/

├── model/
│   ├── model_version
│   ├── tokenizer
│   └── quantization
│
├── serving/
│   ├── engine
│   ├── batching
│   ├── kv_policy
│   └── parallelism
│
├── rag/
│   ├── retriever
│   ├── reranker
│   └── index
│
├── agent/
│   ├── policy
│   ├── tools
│   └── state_schema
│
├── observability/
│   ├── metrics
│   ├── logs
│   ├── traces
│   └── alerts
│
├── benchmark/
│   └── ProcurementBench_V1
│
├── release/
│   ├── canary
│   ├── rollback
│   └── release_manifest
│
└── runbook/
    ├── incidents
    ├── capacity
    └── recovery
```

---

# 十八、本课 10 个阶段工程产物怎样接起来？

```text
Stage 1
ProcurementInferenceSLOPolicy_V0.1
→ 定义“快”的统一口径

Stage 2
ProcurementQuantizationPolicy_V0.1
→ 精度 / 显存 / Kernel权衡

Stage 3
ProcurementKVCachePolicy_V0.1
→ 动态显存与长上下文容量

Stage 4
ProcurementPagedServingPolicy_V0.1
→ Paged KV与Serving Engine

Stage 5
ProcurementBatchingPolicy_V0.1
→ 吞吐 / 延迟工作点

Stage 6
ProcurementParallelServingPolicy_V0.1
→ 多GPU拓扑与副本

Stage 7
ProcurementServingArchitecture_V0.1
→ Model + RAG + Agent真实服务

Stage 8
ProcurementObservabilityPolicy_V0.1
→ Metrics / Logs / Traces / Alert

Stage 9
ProcurementReleaseRolloutPolicy_V0.1
→ Shadow / Canary / A-B / Rollback

Stage 10
ProcurementAI
→ 生产闭环
```

---

# 十九、第十课最终 10 条核心心智模型

> **① `GoodModel ≠ GoodProductionSystem`。**

> **② `Latency ≠ Throughput`。**

> **③ `Quantization ≠ FreeCompression`。**

> **④ `ModelFitsInGPU ≠ ServingFitsInGPU`。**

> **⑤ `EfficientMemory ≠ EfficientScheduling`。**

> **⑥ `MoreGPUs ≠ LinearSpeedup`。**

> **⑦ `Deployment ≠ ModelLoading`。**

> **⑧ `Monitoring ≠ GPUUtilizationOnly`。**

> **⑨ `ReleaseReady ⇒ RollbackReady`。**

> **⑩ `DeploymentSuccess ≠ ProductionReadiness`。**

---

# 二十、整门第十课最终工程图

```text
                 ProcurementBench_V1 Pass
                          │
                          ▼
                    Inference SLO
                          │
                          ▼
                    Quantization
                          │
                          ▼
                      KV Cache
                          │
                          ▼
                    Paged Serving
                          │
                          ▼
                       Batching
                          │
                          ▼
                    Multi-GPU Plan
                          │
                          ▼
                Serving Architecture
                          │
                          ▼
                    Observability
                          │
                          ▼
               Shadow / Canary / A-B
                          │
                          ▼
                 Production Load Test
                          │
                          ▼
                     Release Gate
               ┌──────────┴──────────┐
               ▼                     ▼
             Reject                 Pass
                                      │
                                      ▼
                               ProcurementAI
                                      │
                                      ▼
                            Production Feedback
                                      │
                                      └──→ Benchmark / Improvement
```

脑中最后只留一句：

> **真正的 AI 部署，不是把模型启动起来，而是把模型、RAG、Agent、推理引擎、显存管理、Batch、多 GPU、网关、状态、监控、灰度、回滚和 Benchmark 接成一条可测量、可扩容、可故障恢复、可持续发布的生产链，最终形成可运营的 `ProcurementAI`。**

---

# 第十课 · 第 10 阶段掌握测试

现在不回看正文，你应该能够解释：为什么 Deployment Success 不等于 Production Readiness；ProcurementAI 为什么不是一个模型文件；Serving Plane 和 Control Plane 有什么区别；真实 Workload Matrix 应该怎样设计；为什么 Capacity Plan 不能直接等于峰值压测；Headroom 为什么重要；为什么大模型 Autoscaling 要考虑冷启动和预热；Failure Injection 为什么必须在上线前做；Graceful Degradation 怎样限制故障影响；为什么最终质量评测必须针对 Serving Build；Release Gate 为什么必须是多维 AND；Runbook 为什么属于系统资产；以及 Production Feedback 怎样重新进入 Benchmark、数据和下一轮迭代。

如果这些能够完整讲出来：

\[
\boxed{
第十课第10阶段真正掌握
}
\]

---

# 第十课正式完成

到这里：

\[
\boxed{
第十课=10/10
}
\]

最终工程交付：

\[
\boxed{
ProcurementAI
}
\]

课程系统演化到：

\[
\boxed{
ProcurementDataset\_V0.1
\rightarrow
ProcurementLM\_V0.1
\rightarrow
ProcurementRAG\_V0.1
\rightarrow
ProcurementAgent\_V0.1
\rightarrow
ProcurementLM\_V0.2
\rightarrow
ProcurementBench\_V1
\rightarrow
ProcurementAI
}
\]

下一课正式进入：

# 第十一课：ProcurementLM V1.0 全流程实战
## 怎样把需求定义、数据、模型、RAG、SFT、Rules、Benchmark、Agent、部署与反馈闭环全部从零接一遍，最终交付 `ProcurementLM_V1.0`？

第十课解决的是：

> **怎样把已经证明有效的 AI 系统真正运行在生产环境。**

第十一课开始解决：

> **怎样把前十课全部压缩成一个完整、可交付、可审计、可运营的端到端项目。**

<!-- LESSON 10 STAGE 10 END -->

