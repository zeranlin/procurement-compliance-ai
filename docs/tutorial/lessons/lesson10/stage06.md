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
