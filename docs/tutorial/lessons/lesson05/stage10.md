# 第五课 · 第 10 阶段
# 训练显存到底花在哪里？
## 为什么 7B 模型已经 QLoRA 4-bit 了，训练时照样可能 OOM？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **能推理，不代表能训练。**
2. **Model Weights + KV Cache + Activations / Runtime Buffers**
3. **Model Weights + Forward中间结果 + Backward所需信息 + Gradients + Optimizer States**
4. **BF16 Base 约16-bit/parameter**
5. **NF4 Base 约4-bit/parameter + metadata**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `LoRA` | LoRA：冻结大部分基座参数，只训练低秩增量矩阵 |
| `QLoRA` | QLoRA：量化基座模型并训练 LoRA，以降低显存成本 |
| `Gradient` | 梯度：损失对参数变化方向和敏感度的局部信息 |
| `Batch` | 批次：一次参与计算的一组样本 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Attention` | 注意力：根据内容相关性动态聚合信息 |

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

第 9 阶段我们解决的是：

> **怎样把 Frozen Base Model 的权重显存压下来。**

现在必须解决一个非常现实的问题：

```text
7B Base
已经4-bit了

LoRA
也只有几千万参数

为什么24GB显卡
还是可能突然 OOM？
```

答案是：

> **训练显存从来不只有 Model Weights。**

真正的训练显存账本更接近：

\[
\boxed{
M_{peak}
\approx
M_{base}
+
M_{trainable}
+
M_{grad}
+
M_{optimizer}
+
M_{activation}
+
M_{temporary}
+
M_{runtime}
}
\]

本阶段最终形成：

# `TrainingMemoryBudget_V0.1`

---

# 一、本阶段只解决一个核心问题

你以后碰到：

```text
CUDA out of memory
```

第一反应不能再是：

> “模型太大。”

而应该问：

> **到底是哪一类显存在涨？它主要跟 Parameter Count、Trainable Parameters、Sequence Length，还是 Micro Batch Size 有关？**

先把总图锁死：

```text
                         GPU VRAM
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
    Model Side          Training Side       Runtime Side
        │                   │                   │
 Base Weights           Gradients          Temp Buffers
 LoRA Weights           Optimizer          CUDA Context
                        Activations        Allocator
                                           Framework
```

一句话：

> **模型有多大，只解释了显存账本的一部分。**

---

# 二、今天只锁死 5 个核心心智模型

## 心智模型 1：Inference Memory ≠ Training Memory

推理时主要关心：

```text
Model Weights
+
KV Cache
+
Activations / Runtime Buffers
```

训练时则需要：

```text
Model Weights
+
Forward中间结果
+
Backward所需信息
+
Gradients
+
Optimizer States
```

所以同一个模型：

> 能推理，不代表能训练。

\[
\boxed{
CanLoadForInference
\neq
CanTrain
}
\]

---

## 心智模型 2：QLoRA 主要砍掉 Base Weight Memory，不会自动砍掉 Activation

第 9 阶段：

```text
BF16 Base
约16-bit/parameter
```

变成：

```text
NF4 Base
约4-bit/parameter + metadata
```

这对：

# Base Weights

非常有效。

但 Forward 过程中每一层产生的：

```text
Hidden States
Attention中间量
MLP中间量
```

并不会因为 Base Weight 是 4-bit：

> 全部自动缩成四分之一。

所以：

\[
\boxed{
4bitWeights
\neq
4bitActivations
}
\]

---

## 心智模型 3：LoRA 让 Gradient / Optimizer 很小，但 Activation 仍经过完整 Base Model

QLoRA 中真正 Trainable 的：

```text
LoRA A/B
```

很少。

因此：

```text
Gradient Memory
Optimizer State Memory
```

相对 Full Fine-Tuning 可以小很多。

但一条 Token 仍然要跑过：

> 整个 Transformer。

所以：

```text
7B Base
虽然Frozen
```

不等于：

```text
Forward只算1%的模型
```

整个模型仍参与计算。

---

## 心智模型 4：Sequence Length 和 Micro Batch Size 是 Activation Memory 的两大旋钮

非常粗略地说：

\[
M_{\text{activation}}
\propto
B_{\text{micro}}
\times
S
\times
L
\times
H
\]

其中：

- \(B_{\text{micro}}\)：单次真正送进 GPU 的样本数；
- \(S\)：Sequence Length；
- \(L\)：Transformer 层数；
- \(H\)：Hidden Size。

真实公式会复杂得多，但这个心智模型非常有用。

也就是说：

> **参数没变，只把 2048 Token 改成 8192 Token，训练显存也可能完全变成另一回事。**

---

## 心智模型 5：OOM 要按“显存来源”诊断，不能随机调参

最差的调试方式：

```text
OOM
↓
rank乱改
↓
batch乱改
↓
alpha乱改
↓
再装几个包
```

正确思路：

```text
OOM
 ↓
是哪类Memory？
 ↓
对应哪个Scaling变量？
 ↓
只改最相关的旋钮
 ↓
重新测Peak VRAM
```

这叫：

# Memory Attribution
## 显存归因

---

# 三、训练显存正式拆成 7 个账户

| 显存账户 | 主要由什么决定 | QLoRA 是否明显降低 |
|---|---|---|
| **Base Weights** | Base 参数量、量化位宽 | **是，核心收益** |
| **LoRA / Trainable Weights** | Rank、Target Modules | 数量本来就小 |
| **Gradients** | Trainable 参数量 | **LoRA 大幅降低** |
| **Optimizer States** | Trainable 参数量、优化器 | **LoRA 大幅降低** |
| **Activations** | Batch、Sequence、模型结构 | **不会自动消失** |
| **Temporary Buffers** | Attention/kernel/算子 | 部分受实现影响 |
| **Runtime Overhead** | CUDA、allocator、框架等 | 与4-bit不是一回事 |

以后看到显存：

> 就用这 7 个账户查账。

---

# 四、账户 1：Base Model Weights

这是最好理解的一块。

如果模型有：

\[
N
\]

个参数。

BF16 理论裸权重：

\[
M_{\text{base}}
\approx
2N \text{ bytes}
\]

7B：

\[
7\times10^9\times2
\approx14GB
\]

QLoRA 4-bit 裸编码理论上：

\[
7\times10^9\times0.5
\approx3.5GB
\]

但上一阶段已经强调：

> 实际驻留显存还要加量化 Scale、Metadata、非量化参数、临时工作区等。

因此这里最重要的不是死记：

```text
7B = X GB
```

而是：

\[
\boxed{
BaseWeightMemory
\propto
ParameterCount
\times
StorageBits
}
\]

这块就是 QLoRA 最擅长压缩的地方。

---

# 五、账户 2～4：LoRA Weight、Gradient、Optimizer State

假设 LoRA 真正可训练参数只有：

```text
20M Parameters
```

那么需要 Gradient 的：

> 主要也是这 20M。

Optimizer 需要保存状态的：

> 主要也是这些 Trainable Parameters。

这和 Full Fine-Tuning 完全不同。

Full FT：

```text
7B参数
都可能需要Gradient和Optimizer State
```

LoRA：

```text
7B Base
Frozen

20M LoRA
Trainable
```

所以：

\[
\boxed{
OptimizerMemory
主要跟
TrainableParameterCount
走
}
\]

而不是简单跟：

> Base Model 总参数量走。

---

# 六、为什么 Optimizer State 有时比你想象得更贵？

例如常见 AdamW 会为可训练参数维护：

```text
First Moment
m

Second Moment
v
```

这些状态可能使用 FP32 等精度。

某些训练方案还可能存在：

```text
Master Weights
```

等额外副本。

因此不能机械记：

> “一个参数训练永远固定 X bytes。”

因为这取决于：

```text
Optimizer
Parameter Dtype
Gradient Dtype
Mixed Precision实现
8-bit Optimizer与否
Framework
```

长期正确心智模型：

\[
\boxed{
OptimizerState
跟 Trainable Parameters 强相关
}
\]

这正是 LoRA 为什么能省大量训练显存。

---

# 七、真正的大户：Activations

这里就是很多人第一次 QLoRA OOM 的原因。

假设输入经过第 1 层 Transformer：

```text
Hidden State
↓
Attention
↓
MLP
↓
Layer Output
```

然后还有：

```text
第2层
第3层
...
第32层
```

Backward 要计算：

> 每一步参数变化对最终 Loss 的影响。

因此训练期间需要保存或能够重新得到大量中间信息。

这些中间结果统称：

# Activations
## 激活值 / 中间激活

可以把它理解成：

> **Forward 为了让 Backward 以后能够追责，留下的计算现场。**

---

# 八、为什么 Batch Size 会直接推高 Activation？

假设：

```text
micro_batch_size = 1
```

GPU 同时保存：

> 一条 Sequence 的大量中间结果。

改成：

```text
micro_batch_size = 4
```

现在同一时刻要处理：

> 4 条。

因此很多 Activation Memory 会近似跟：

\[
B_{\text{micro}}
\]

一起增加。

注意我这里特意写：

# Micro Batch Size

而不是：

# Effective Batch Size

这两个后面必须分开。

---

# 九、为什么 Sequence Length 更危险？

假设：

```text
Batch = 1
```

但长度：

```text
2048
→
4096
→
8192
```

每层都要处理更多 Token。

大量 Hidden State 相关存储大致会随：

\[
S
\]

增长。

Attention 又更特殊。

经典 Attention 计算里：

\[
QK^T
\]

会形成与：

\[
S\times S
\]

相关的结构。

因此传统实现的某些 Attention 中间内存：

\[
O(S^2)
\]

增长非常快。

这就是为什么：

> 长上下文训练特别容易吃显存。

---

# 十、但这里必须做一个现代实现修正：FlashAttention 会改变“显存复杂度”，不会改变所有计算规律

如果使用传统 Attention，并显式保存完整 Attention Matrix：

> \(S^2\) 中间结果会非常昂贵。

FlashAttention / 高效 SDPA 等实现：

> 不需要把完整 Attention Matrix 长时间写回显存。

因此能显著降低 Attention 的峰值显存。

所以不能简单说：

> “序列长度翻倍，所有训练显存一定四倍。”

这是不精确的。

更准确：

> **Attention 的理论计算量依然随序列长度呈近似二次增长，而高效 Attention Kernel 可以避免完整 \(S^2\) Attention Matrix 的显存驻留，使实际峰值显存增长比朴素实现健康很多。**

这条区别很重要：

\[
\boxed{
ComputeComplexity
\neq
StoredActivationMemory
}
\]

---

# 十一、Gradient Checkpointing 为什么能省显存？

正常做法：

```text
Forward
↓
保存大量Activation
↓
Backward直接使用
```

Gradient Checkpointing：

# 梯度检查点

采用：

```text
Forward
↓
只保留部分Checkpoint
↓
其他Activation不长期保存
↓
Backward需要时
重新Forward计算
```

也就是：

\[
\boxed{
Memory
\downarrow
\quad
\text{换取}
\quad
Compute
\uparrow
}
\]

中文：

> **不存那么多计算现场，等需要的时候再重算。**

---

# 十二、Gradient Checkpointing 省的不是 Model Weight

这一点很容易搞混。

QLoRA：

> 主要压 Base Weight。

Gradient Checkpointing：

> 主要压 Activation。

所以二者非常互补：

```text
QLoRA
        ↓
Base Weight Memory ↓

Gradient Checkpointing
        ↓
Activation Memory ↓
```

这也是为什么这两个技术经常一起出现。

---

# 十三、Gradient Accumulation 又是在解决什么？

假设你希望：

```text
Effective Batch Size = 16
```

但 GPU 一次只能放：

```text
Micro Batch Size = 2
```

可以让 8 个 Micro-batch：

```text
forward
backward

forward
backward

...

累计8次Gradient
```

然后：

```text
optimizer.step()
```

于是：

\[
B_{\text{effective}}
=
B_{\text{micro}}
\times
GradientAccumulationSteps
\]

单卡、单进程的简化情况例如：

\[
2\times8=16
\]

这叫：

# Gradient Accumulation
## 梯度累积

---

# 十四、Gradient Accumulation 最容易被误解的一点

它可以让：

> **有效 Batch 变大，而不要求一次把整个 Batch 放进 GPU。**

但是：

\[
\boxed{
GradientAccumulation
不会让单个MicroBatch本身变小
}
\]

所以如果：

```text
micro_batch = 1
sequence_length = 32K
```

这一条本身已经 OOM，

再把：

```text
gradient_accumulation_steps
```

从 4 调到 32：

> 没用。

因为连第一条 Forward 都进不去。

---

# 十五、Packing 对显存又是什么关系？

第 4 阶段学了 Packing。

Packing 的主要目标是：

# Token Utilization

减少 Padding Waste。

但一定不要误解成：

> `packing=True` 必然降低 Peak VRAM。

如果 Packed Sequence 最终仍是：

```text
4096 Tokens
```

GPU 依然需要处理：

> 一条 4096 长度 Sequence。

Packing 的主要收益更接近：

> **同样的计算长度中，装更多真实训练 Token。**

它是：

# Efficiency Optimization

而不一定是：

# Peak Memory Reduction

这一点很关键。

---

# 十六、为什么 Rank 通常不是 QLoRA OOM 的第一嫌疑人？

假设：

```text
r = 16
```

改成：

```text
r = 8
```

LoRA Trainable Parameters 的确减少。

Gradient 和 Optimizer State：

> 也会减少。

但如果真正显存大头已经变成：

# Activations

那么这个变化：

> 可能救不了多少显存。

所以出现 OOM 时，不要机械：

```text
先砍Rank
```

要看账本。

对于 QLoRA，一个很常见的优先诊断方向反而是：

```text
Micro Batch Size

Sequence Length

Gradient Checkpointing

Attention Implementation
```

---

# 十七、7B QLoRA 为什么“模型才几 GB”仍然会 OOM？

现在可以精准回答了。

假设只是概念例子：

```text
4-bit Base
≈ 几GB级

LoRA
≈ 相对较小
```

但你又设置：

```text
Sequence Length = 8192

Micro Batch = 4

Gradient Checkpointing = OFF

Attention implementation
不够省显存
```

那么：

```text
Base Weight
并不是主犯

Activation
+
Attention Temp
+
Runtime Buffer
```

完全可能把剩余显存吃光。

所以：

\[
\boxed{
SmallWeightFootprint
\neq
SmallTrainingFootprint
}
\]

这是今天最重要的一句话之一。

---

# 十八、还有一个经常混进来的东西：KV Cache

推理阶段我们经常讨论：

# KV Cache

它会随着生成长度和 Batch 增长。

但普通 Causal LM 训练时：

> 通常并不需要像自回归推理那样保留跨生成步骤的 KV Cache。

训练配置里一般会：

```text
use_cache = False
```

尤其和 Gradient Checkpointing 一起时。

所以看到训练 OOM：

> 不要第一时间把所有显存都归因到推理阶段熟悉的 KV Cache。

训练真正的大头通常另有其人。

---

# 十九、OOM 时建立一个精准的处理顺序

对于我们的 `ProcurementLM_V0.1` QLoRA Baseline，可以采用：

```text
OOM
 │
 ▼
1. 先确认有没有错误配置
   ├─ 是否意外加载BF16完整Base副本？
   ├─ 是否use_cache不合理开启？
   └─ 实际dtype是否符合预期？
 │
 ▼
2. 降低 Micro Batch Size
 │
 ▼
3. 检查 / 降低 Sequence Length
   并优化Context Selection
 │
 ▼
4. 开启 Gradient Checkpointing
 │
 ▼
5. 使用合适的高效Attention实现
 │
 ▼
6. 再检查 Packing / Length Bucketing 等吞吐效率
 │
 ▼
7. 如果仍不足
   再考虑Rank / Target Modules等Trainable Scope
 │
 ▼
8. 更进一步
   Offload / Distributed / 更大显存GPU
```

这里有一个原则：

> **先砍无效显存，再砍业务信息。**

例如不要为了 OOM：

> 第一刀直接把关键上下文从 4096 暴力砍到 512。

先确认有没有其他浪费。

---

# 二十、真正应该监控的是 Peak VRAM，而不是“理论估计”

理论公式可以帮助定位方向。

但真实训练最终要记录：

```text
Peak Allocated VRAM

Peak Reserved VRAM

Sequence Length

Micro Batch Size

Gradient Accumulation

Gradient Checkpointing

Attention Backend

Quantization Config

Trainable Parameters
```

因为 CUDA Allocator 还会涉及：

# Reserved Memory

以及：

# Fragmentation
## 显存碎片

所以有时：

```text
实际Tensor总量
```

没有完全占满显卡，

仍可能因为：

> 当前找不到足够大的连续可用块

而 OOM。

因此：

\[
\boxed{
TheoreticalMemory
\neq
ObservedPeakVRAM
}
\]

---

# 二十一、本阶段工程产物：`TrainingMemoryBudget_V0.1`

第一版至少记录这些字段：

```text
base_model
base_model_revision

quantization
compute_dtype

parameter_count
trainable_parameter_count

max_sequence_length
micro_batch_size
gradient_accumulation_steps

gradient_checkpointing

attention_backend

packing_enabled

optimizer
optimizer_precision

peak_allocated_vram
peak_reserved_vram

tokens_per_step
supervised_tokens_per_step

oom_status
```

同时建立显存归因：

```text
Base Weight
Trainable Weight
Gradient
Optimizer
Activation
Temporary / Attention
Runtime Overhead
```

不是要求你精确算到：

> 每个字节。

而是要求：

> **知道哪一个旋钮主要影响哪一块。**

---

# 二十二、这一阶段最值得保留的一张“变量地图”

| 你修改的变量 | 最直接影响的显存 |
|---|---|
| Base Model 参数量 | Base Weight |
| 4-bit / BF16 | Base Weight |
| Rank | LoRA Weight、Grad、Optimizer |
| Target Modules | LoRA Weight、Grad、Optimizer |
| Micro Batch Size | **Activation** |
| Sequence Length | **Activation + Attention + Compute** |
| Gradient Accumulation | 有效 Batch；对单 Micro-batch Peak VRAM影响较小 |
| Gradient Checkpointing | **Activation ↓，Compute ↑** |
| FlashAttention / 高效 Attention | Attention 中间内存、吞吐 |
| Packing | Token 利用率，未必直接降低 Peak VRAM |

这张表比背 CUDA 参数值重要得多。

---

# 二十三、把本阶段压成最精准的 5 句话

> **第一，训练显存不只是模型权重，而是 Base Weight、Trainable Weight、Gradient、Optimizer State、Activation、Temporary Buffer 和 Runtime Overhead 的总和。**

> **第二，QLoRA 主要降低冻结 Base Model 的 Weight Memory，LoRA 主要降低 Gradient 和 Optimizer 对应的 Trainable Parameter Memory，但完整 Transformer 的 Activation 仍然存在。**

> **第三，Micro Batch Size 和 Sequence Length 是 Activation 显存的核心变量；长上下文尤其昂贵，高效 Attention 可以降低中间显存，但不会让长序列计算免费。**

> **第四，Gradient Checkpointing 用额外计算换 Activation 显存；Gradient Accumulation 用多个小 Micro-batch 组成较大的 Effective Batch，两者解决的是完全不同的问题。**

> **第五，OOM 不是“模型太大”四个字能解释的；必须先定位显存账户，再调对应变量，并用真实 Peak VRAM 验证。**

---

# 二十四、本阶段最核心的一张图

```text
                    Training Peak VRAM
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
     Weights             Training           Runtime
       │                   │                   │
 Quantized Base        Activations         Buffers
 LoRA Params           Gradients           CUDA
                      Optimizer            Allocator
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
        Sequence       Micro Batch     Checkpointing
         Length           Size              │
             │             │                ▼
             └──────┬──────┘           Memory ↓
                    │                  Compute ↑
                    ▼
             Activation Peak
                    │
                    ▼
              OOM or Stable
```

脑子里只留一句：

> **QLoRA 省权重，Checkpointing 省激活，Accumulation 省一次性 Batch；三件事别混。**

---

# 二十五、本阶段掌握测试

不回看正文，你现在应该能够解释：为什么同一个 7B 模型能够推理却未必能够训练；训练显存有哪些主要组成；QLoRA 主要压缩哪一部分；为什么 LoRA 能显著减少 Gradient 和 Optimizer State；为什么 Base Model Frozen 后 Activation 仍然存在；为什么 Micro Batch Size 和 Effective Batch Size 不是一回事；Gradient Accumulation 为什么不能解决“单条 32K Sequence 已经 OOM”；Gradient Checkpointing 为什么能省显存以及它付出的代价是什么；为什么 Sequence Length 会强烈影响 Activation 和 Attention；FlashAttention 为什么能省显存但不会消除 Attention 的计算成本；为什么 Packing 主要提升 Token Utilization 而不保证降低 Peak VRAM；为什么 QLoRA OOM 时 Rank 往往不是第一刀；为什么训练阶段不应该把所有显存问题都归因于 KV Cache；以及为什么最终必须记录真实的 Peak Allocated / Reserved VRAM，而不能只看理论权重大小。

如果这些能完整讲出来：

\[
\boxed{
第五课第10阶段真正掌握
}
\]

---

# 本阶段最后只记一句话

> **训练显存是一张完整账本：QLoRA 把冻结 Base Weight 压下来，LoRA 把需要 Gradient 和 Optimizer 的参数规模压下来，但真正训练时仍然要为完整 Transformer 的 Activation、Attention 中间量和运行时缓冲付费；所以 OOM 的正确解决方式不是盲目缩模型，而是先判断显存到底花在哪，再针对 Sequence Length、Micro Batch、Checkpointing、Attention 实现和 Trainable Scope 精准下刀。**

---

# 下一阶段：第五课 · 第 11 阶段
# 真正跑一次 SFT 训练
## 前面 10 个阶段，终于要第一次全部接成可执行训练流程

下一阶段不再新增一堆理论概念，而是把目前所有组件真正组装起来：

```text
ProcurementDataset_V0.1
        ↓
Chat Template
        ↓
Assistant-only Loss
        ↓
Length Policy
        ↓
Packing
        ↓
4-bit NF4 Base
        ↓
LoRA Config
        ↓
Target Modules
        ↓
Training Arguments
        ↓
Trainer / Training Loop
        ↓
Forward
        ↓
Loss
        ↓
Backward
        ↓
Optimizer Step
        ↓
ProcurementLM_V0.1 Adapter
```

下一阶段我们会第一次真正回答：

> **从 `from_pretrained()` 到训练启动，一个完整可运行的 ProcurementLM QLoRA SFT 脚本到底由哪些部分组成，每一行为什么存在，以及开跑前必须检查哪几项才不会“代码能跑、训练却是错的”。**

---
