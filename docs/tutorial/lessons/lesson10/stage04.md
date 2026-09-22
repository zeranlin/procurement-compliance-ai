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
