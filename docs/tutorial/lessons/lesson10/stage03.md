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
