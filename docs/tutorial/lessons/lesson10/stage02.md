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
