# 第五课 · 第 9 阶段
# QLoRA 与 4-bit / NF4
## 为什么一个几十亿参数的 Base Model 可以用 4-bit 保存，却仍然能训练出有效的 LoRA Adapter？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Base Model 的存储方式。**
2. **Base Model BF16 / FP16 等 Frozen + LoRA Adapter Trainable**
3. **Base Model 4-bit Quantized Frozen + LoRA Adapter Trainable**
4. **Input Attention MLP Loss Gradient**
5. **全部都只有4-bit**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `LoRA` | LoRA：冻结大部分基座参数，只训练低秩增量矩阵 |
| `QLoRA` | QLoRA：量化基座模型并训练 LoRA，以降低显存成本 |
| `NF4` | NF4：适合近似正态权重的 4 位量化格式 |
| `Adapter` | 适配器：附加在基座模型上的轻量可训练参数模块 |
| `Quantization` | 量化：用更低位宽表示权重/激活以降低显存和计算成本 |
| `BF16` | BF16：保留较大指数范围的 16 位浮点，常用于大模型 |

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

前面我们已经把 LoRA 拆得非常清楚了：

\[
W' = W + \Delta W
\]

其中：

\[
\Delta W = BA
\]

并且：

```text
Base Weight W
=
Frozen

LoRA A / B
=
Trainable
```

到这里，还有一个巨大的工程问题没有解决。

即使：

> Base Model 不训练，

它仍然要：

> **驻留在显存里。**

假设 Base Model 有 7B 参数。

BF16 大致需要：

\[
7\times10^9\times2
\approx14GB
\]

仅仅模型权重就已经非常大。

于是 QLoRA 出现了。

今天要彻底搞懂的不是某个配置参数，而是这条链：

```text
Frozen Base Model
        ↓
4-bit Quantization
低位宽保存
        ↓
Forward 时按需恢复到计算精度
        ↓
Base Path 继续参与计算
        +
LoRA A/B 保持可训练
        ↓
Loss
        ↓
Backward
        ↓
只更新 LoRA
```

最终形成：

# `QLoRAMemoryModel_V0.1`

---

# 一、本阶段只解决一个核心问题

> **QLoRA 到底量化了谁？4-bit 存在哪里？Forward 真的是用 4-bit 做所有计算吗？LoRA 参数又是什么精度？**

先把最重要的一句话放在这里：

\[
\boxed{
QLoRA
\neq
EverythingRunsIn4Bit
}
\]

QLoRA 更准确的理解是：

> **把冻结的 Base Model 权重以低位宽量化形式保存，从而显著减少权重显存；计算时按需要恢复到合适的计算精度，同时继续训练正常的 LoRA Adapter。**

这句话掌握，本阶段已经通了一半。

---

# 二、先锁死 5 个核心心智模型

## 心智模型 1：QLoRA = Quantized Base + Trainable LoRA

普通 LoRA：

```text
Base Model
BF16 / FP16 等
Frozen
      +
LoRA Adapter
Trainable
```

QLoRA：

```text
Base Model
4-bit Quantized
Frozen
      +
LoRA Adapter
Trainable
```

所以：

\[
\boxed{
QLoRA
=
QuantizedFrozenBase
+
LoRA
}
\]

关键变化发生在：

> **Base Model 的存储方式。**

LoRA 的低秩学习思想本身：

> 没有变。

---

## 心智模型 2：4-bit 主要是“权重存储精度”，不是“整个训练过程只有 4-bit”

这是最容易犯的错误。

不要想象：

```text
Input
↓
Attention
↓
MLP
↓
Loss
↓
Gradient

全部都只有4-bit
```

这不是 QLoRA 的正确心智模型。

实际更接近：

```text
GPU显存里
Base Weight
以4-bit形式保存
        ↓
需要做矩阵计算时
        ↓
按块反量化 / Dequantize
        ↓
BF16 / FP16 等计算精度
        ↓
Matrix Multiply
```

所以必须区分：

# Storage Dtype
存储精度

和：

# Compute Dtype
计算精度

两者：

\[
\boxed{
可以不同
}
\]

---

## 心智模型 3：NF4 是一种 4-bit 量化表示，不是“保留四位小数”

NF4：

# NormalFloat 4-bit

它不是：

> “一个浮点数只留 4 位小数。”

4-bit 真正意味着：

> 每个量化值只用大约 4 个二进制位来表示其离散编码。

4 bit 能表示：

\[
2^4=16
\]

种离散状态。

NF4 的设计思路是：

> 针对神经网络权重常见的近似正态分布特性，设计更合适的 16 个表示级别。

所以：

\[
\boxed{
NF4
=
4bit Quantization Format
}
\]

而不是：

\[
4\text{ decimal places}
\]

---

## 心智模型 4：量化一定引入近似误差，QLoRA 的问题不是“有没有误差”，而是“误差是否值得换显存”

原始 Base Weight：

\[
W
\]

量化以后：

\[
Q(W)
\]

再反量化：

\[
\hat W
\]

一般不会满足：

\[
\hat W=W
\]

而更像：

\[
\hat W
=
W+\epsilon_q
\]

其中：

\[
\epsilon_q
\]

就是：

> Quantization Error，量化误差。

所以：

\[
\boxed{
Quantization
=
Compression
+
Approximation
}
\]

真正工程问题是：

> **这点近似误差带来的能力损失，是否远小于我们得到的显存收益？**

答案只能由 Benchmark 判断。

---

## 心智模型 5：QLoRA 大幅减少 Base Weight 显存，但不会把所有训练显存都消灭

训练显存我们已经拆过：

```text
Model Weights
+
Gradients
+
Optimizer States
+
Activations
+
Temporary Buffers
```

QLoRA 非常擅长压缩：

> Frozen Base Model Weights。

LoRA 又大幅减少：

> Trainable Gradient / Optimizer State 对应的参数规模。

但是：

# Activations

仍然存在。

Sequence Length 越长：

> Activation 仍可能很贵。

所以：

\[
\boxed{
QLoRA
\neq
UnlimitedContextForFree
}
\]

这会直接接到下一阶段：

> **训练显存到底花在哪里。**

---

# 三、先精准区分 LoRA 和 QLoRA

| 对象 | LoRA | QLoRA |
|---|---|---|
| Base Model | Frozen | Frozen |
| Base Weight 存储 | 常见 BF16 / FP16 等 | 常见 4-bit |
| LoRA A/B | Trainable | Trainable |
| LoRA 是否低秩 | 是 | 是 |
| Base Weight 是否更新 | 否 | 否 |
| 主要额外目标 | 减少可训练参数 | 再进一步减少 Base Weight 显存 |
| Activation | 仍存在 | 仍存在 |

所以一句话：

> **LoRA 解决“不要训练整个 Base Model”，QLoRA 进一步解决“既然 Base Model 冻结了，能不能连它的显存也省下来”。**

---

# 四、为什么 4-bit 可以省这么多？

假设：

\[
N
\]

个参数。

BF16：

\[
16\text{ bits}
=
2\text{ bytes}
\]

理论权重存储：

\[
Memory_{BF16}
\approx
2N
\]

bytes。

4-bit：

\[
4\text{ bits}
=
0.5\text{ bytes}
\]

理论权重存储：

\[
Memory_{4bit}
\approx
0.5N
\]

所以理想裸权重比例：

\[
\frac{4}{16}
=
\frac14
\]

也就是：

> 4-bit 原始权重编码理论上约为 BF16 的四分之一。

例如 7B：

BF16：

\[
7B\times2
\approx14GB
\]

4-bit 裸编码理论值：

\[
7B\times0.5
\approx3.5GB
\]

但是这里一定要加一句：

> **真实显存不会精确等于 3.5GB。**

因为量化还需要：

```text
Scale
Zero / Quantization Metadata
Block Information
Temporary Buffers
Framework Overhead
其他未量化参数
```

所以：

\[
\boxed{
4bit理论裸权重大小
\neq
实际GPU显存占用
}
\]

---

# 五、量化究竟怎么发生？

不要把量化想成：

> 整个 70 亿参数只找一个最大值，然后压成 16 档。

实际通常会：

# Block-wise Quantization
## 分块量化

也就是把权重分成很多小块。

例如概念上：

```text
Block 1
[w1 w2 w3 ...]
      ↓
找到这个Block自己的缩放信息
      ↓
映射到16个NF4状态

Block 2
[w...]
      ↓
自己的scale
      ↓
映射到16个状态
```

这样相比整个大矩阵只用一个统一尺度：

> 能更好地保留局部数值结构。

所以一个量化权重实际上不仅有：

```text
4-bit codes
```

还需要：

```text
quantization scales / metadata
```

来恢复近似权重。

---

# 六、Forward 时最精准的流程是什么？

这一段非常关键。

假设原始 Base Weight：

\[
W
\]

加载成：

\[
W_q
\]

即 4-bit 量化存储。

Forward 不是简单：

\[
W_qx
\]

然后整个矩阵乘法都按普通整数 4-bit 思维理解。

概念上更接近：

```text
4-bit Quantized Weight
W_q
      ↓
Dequantization
反量化
      ↓
Compute Dtype
例如 BF16
      ↓
Matrix Multiply
      ↓
Base Output
      +
LoRA Output
```

公式上可以粗略写：

\[
y
=
Dequant(W_q)x
+
\frac{\alpha}{r}BAx
\]

其中：

\[
Dequant(W_q)
\approx
W
\]

这就是 QLoRA 最核心的一张公式。

---

# 七、为什么“反量化”以后还省显存？

你可能马上发现一个问题：

> 既然最后要恢复成 BF16，为什么不一开始直接保存 BF16？

关键在于：

> **不需要把整个 Base Model 永久以 BF16 完整副本驻留在显存中。**

权重主要保持：

```text
4-bit compressed storage
```

计算某一层时：

> 按实际 kernel / 实现需要，把相关量化权重转换到计算表示完成矩阵运算。

所以要区分：

```text
长期驻留的模型权重表示
```

和：

```text
计算瞬间使用的数值表示
```

这就是为什么：

> Storage Dtype 与 Compute Dtype 的区别如此重要。

---

# 八、LoRA Adapter 本身会不会也变成 4-bit？

第一版心智模型：

> **不要这样理解。**

QLoRA 中被低位宽量化的核心对象是：

# Frozen Base Model

而 LoRA：

\[
A,B
\]

是真正需要梯度更新的训练参数。

它们通常保持：

> 更适合训练的浮点精度。

例如常见会使用：

```text
BF16
FP16
或框架适合的训练dtype
```

所以：

```text
4-bit
=
Frozen Base Storage

BF16 / FP16 等
=
主要计算与可训练Adapter相关精度
```

这个边界一定要牢牢记住。

---

# 九、NF4 为什么不是普通 INT4？

这里不需要深入信息论，但必须建立准确直觉。

普通均匀 INT4 可以想象：

> 把一个数值区间相对均匀地划成有限档位。

NF4 的设计思想则更加针对：

> 神经网络权重的统计分布。

它试图让有限的 16 个编码：

> 更有效地覆盖常见权重值所在的区域。

因此在 QLoRA 语境里：

```text
4-bit
```

只说明：

> 位宽。

而：

```text
NF4
```

说明：

> **这 4 个 bit 怎样解释。**

所以：

\[
\boxed{
BitWidth
\neq
QuantizationFormat
}
\]

4-bit 可以有不同量化格式。

NF4 是其中一种。

---

# 十、什么是 Double Quantization？

这是 QLoRA 里另一个值得认识、但不用过度钻数学的技术。

第一次量化：

> 把 Base Weight 压成 4-bit。

但前面说过：

> 每个量化 Block 还需要 Scale 等量化常数。

这些常数本身：

> 也占空间。

于是 Double Quantization 的思路是：

> **连这些量化常数本身也再做进一步量化。**

流程：

```text
Base Weights
      ↓
第一次Quantization
      ↓
4-bit weight codes
+
quantization constants
      ↓
再压缩这些constants
      ↓
进一步节省显存
```

所以：

\[
\boxed{
DoubleQuantization
不是把权重“量化两遍”
}
\]

更准确地说：

> 第二层主要进一步压缩第一层量化产生的量化参数。

---

# 十一、把 LoRA、QLoRA、NF4 一次性放对位置

整个结构应该这样看：

```text
                Base Model Weight W
                         │
                         ▼
                 4-bit Quantization
                         │
                         ▼
                        NF4
              低位宽保存Frozen Base
                         │
                  Forward时按需
                   Dequantize
                         │
                         ▼
                      Base Path
                         │
                         ├──────────────┐
                         │              │
输入 x ─────────────────┤              ▼
                         │            相加
                         │              │
                         ▼              ▼
                    LoRA A → B       Output
                    Trainable
                         │
                         ▼
                       Loss
                         │
                         ▼
                     Backward
                         │
                         ▼
                    更新 LoRA
                    Base不更新
```

这就是 QLoRA。

不是：

> “把整个 LoRA 也压成 4-bit 然后训练。”

---

# 十二、政府采购项目为什么特别适合把 QLoRA 作为 Baseline 候选？

因为我们的第一版目标是：

```text
强 Base Model
+
高质量政府采购 SFT 数据
+
有限训练资源
+
频繁实验
+
多个 Adapter Version
```

我们真正想训练的：

> 是领域行为增量。

而不是：

> 整套 Base Model。

于是 QLoRA 可以让：

```text
大模型能力
```

与：

```text
较低训练显存门槛
```

同时存在。

但这里必须防止另一个极端：

> **QLoRA 不是因为省显存，所以永远应该优先于 LoRA。**

如果 GPU 足够，

普通 BF16 LoRA：

> 结构更简单。

有时调试也更直接。

所以最终比较仍然是：

```text
BF16 LoRA
vs
QLoRA
```

在相同 Dataset、Benchmark 和 Target Modules 下：

> 看显存、速度、稳定性和业务指标。

---

# 十三、QLoRA 最容易产生的 7 个错误理解

| 错误理解 | 正确理解 |
|---|---|
| “QLoRA 就是 4-bit LoRA” | 核心是 4-bit Frozen Base + Trainable LoRA |
| “所有训练计算都是 4-bit” | 4-bit 主要用于 Base Weight 存储，计算通常使用更高精度 |
| “NF4 是保留四位小数” | NF4 是 4-bit 量化编码格式 |
| “4-bit 没有误差” | 量化一定是近似表示 |
| “LoRA A/B 也必须是 4-bit” | 可训练 Adapter 通常保持适合训练的浮点精度 |
| “7B 4-bit 一定只占 3.5GB” | 3.5GB 只是裸权重理论值，实际还有元数据和运行开销 |
| “QLoRA 解决所有 OOM” | Activation、Sequence Length、Batch 等仍可能导致 OOM |

这张表建议真正记住。

---

# 十四、本阶段工程产物：`QLoRAMemoryModel_V0.1`

第一版配置记录不要只写：

```text
load_in_4bit = true
```

至少应该把这些信息放在一起：

```text
base_model_revision

quantization_enabled
=
true

base_weight_bit_width
=
4

quantization_format
=
NF4

double_quantization
=
enabled / disabled

compute_dtype
=
BF16 / FP16 / actual setting

base_weights
=
frozen

adapter_method
=
LoRA

adapter_train_dtype
=
actual framework setting

rank
alpha
dropout
target_modules

measured_peak_vram

benchmark_version
```

为什么最后两个特别重要？

因为理论上：

> “应该省很多显存。”

不等于：

> 你的真实训练配置真的省了多少。

最终必须测：

# Peak VRAM

同时测：

# Business Quality

---

# 十五、把本阶段压缩成最精准的 5 句话

如果一周以后只剩五句话，我希望是：

> **第一，QLoRA 不是把整个训练变成 4-bit，而是主要把冻结 Base Model 的权重低位宽保存，再继续训练 LoRA Adapter。**

> **第二，必须区分 Storage Dtype 与 Compute Dtype：权重可以 4-bit 存储，但矩阵计算通常会在 BF16、FP16 等更合适的计算精度下完成。**

> **第三，NF4 是针对神经网络权重设计的 4-bit 量化表示；4-bit 表示位宽，NF4 表示这些 4 个 bit 如何编码数值。**

> **第四，量化一定产生近似误差，QLoRA 的价值是用可接受的量化误差换取巨大的 Base Weight 显存节省，最终是否值得必须由 Benchmark 验证。**

> **第五，QLoRA 主要解决 Base Weight Memory，不会让 Activation、Context Length、Batch Size 和训练临时内存问题自动消失。**

这五句话真正掌握：

> QLoRA 就不会再变成“神秘省显存开关”。

---

# 本阶段最核心的一张图

```text
Original Base Model
BF16 / FP16 Weights
        │
        ▼
4-bit Quantization
        │
        ▼
NF4 Frozen Base
低显存驻留
        │
        │ Forward
        ▼
On-the-fly Dequantization
        │
        ▼
Compute Dtype
BF16 / FP16 等
        │
        ▼
       Wx
        │
        ├────────────────┐
        │                │
        │           LoRA Branch
        │             A → B
        │           Trainable
        │                │
        └───────┬────────┘
                ▼
              Output
                │
                ▼
               Loss
                │
                ▼
             Backward
                │
                ▼
         LoRA A/B Updated
                │
         Quantized Base
             Frozen
```

脑中只记一句：

> **Base 低位宽存，计算高精度做，LoRA 正常训练。**

---

# 本阶段掌握测试

现在不回看正文，你应该能够自己解释：QLoRA 和普通 LoRA 的真正区别是什么；QLoRA 到底量化了谁；为什么 Frozen Base 仍然值得量化；为什么 4-bit 不意味着所有 Forward、Backward 都只有 4-bit；Storage Dtype 和 Compute Dtype 有什么区别；为什么 4-bit 理论上相对 BF16 能把裸权重存储缩到约四分之一；为什么实际显存不会严格等于理论值；什么是 Block-wise Quantization；NF4 的 4-bit 与“四位小数”为什么完全不是一回事；为什么 NF4 和 INT4 不是同一个概念；什么是 Quantization Error；为什么 `Dequant(W_q)` 只能近似原始 \(W\)；为什么 LoRA A/B 通常不跟着 Base 一起量化成训练用 4-bit；Double Quantization 进一步压缩的是什么；以及为什么 QLoRA 之后仍然可能因为长 Context、Activation 或 Batch Size 而 OOM。

如果这些能够完整讲出来：

\[
\boxed{
第五课第9阶段真正掌握
}
\]

---

# 本阶段最后只记一句话

> **QLoRA 的本质，是把“不需要更新但必须驻留”的巨大 Base Model 权重以 NF4 等 4-bit 形式压缩保存，在 Forward 时按需要恢复到合适的计算精度参与完整模型计算，同时保持 LoRA Adapter 为真正可训练参数；它省掉的是 Base Weight 的大头显存，而不是把整个训练系统魔法般变成 4-bit。**

---

# 下一阶段：第五课 · 第 10 阶段
# 训练显存到底花在哪里？
## 为什么明明 7B 4-bit Base Model 只有几 GB，训练时还是可能 OOM？

第 9 阶段解决了：

> **Base Weight 怎样从 BF16 的大体积压到 4-bit。**

第 10 阶段要正式把训练显存账本摊开：

```text
Model Weights
+
LoRA Parameters
+
Gradients
+
Optimizer States
+
Activations
+
Attention / Temporary Buffers
+
CUDA / Framework Overhead
```

然后真正回答：

> **哪个东西跟模型参数量走，哪个东西跟 Sequence Length 走，哪个东西跟 Batch Size 走，以及 OOM 时到底应该先改什么。**

---
