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
