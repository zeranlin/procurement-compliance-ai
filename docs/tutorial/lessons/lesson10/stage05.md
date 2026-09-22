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
