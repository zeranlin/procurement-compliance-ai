# 第二课 · 第 7 阶段：Initialization、Normalization 与 Residual Connection
## 为什么 2 层网络随便也能训练，几十层、上百层网络却必须建立一整套“信号稳定系统”？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Deep Network 需要 Signal Stability。深度增加以后，激活和梯度的尺度必须被主动控制。**
2. **Initialization 决定训练从什么数值尺度起步；坏初始化可能让信号一开始就爆炸或衰减。**
3. **Normalization ≠ Data Cleaning。它是在网络内部稳定表示尺度，不是对原始采购数据做清洗。**
4. **Residual Connection 提供 Identity Path，让信息和梯度可以跨层直接传播，是深层 Transformer 可训练的重要条件。**
5. **Initialization + Normalization + Residual 是一套协同稳定机制，但它们只能让深网络更容易训练，不保证数据和任务本身正确。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Normalization` | 规范化：稳定中间激活与训练过程 |
| `Initialization` | 初始化：训练开始前设置参数初值 |
| `Residual Connection` | 残差连接：让信息跨层直接传递、改善深层优化 |
| `Gradient` | 梯度：损失对参数变化方向和敏感度的局部信息 |
| `Transformer` | Transformer：以注意力和前馈网络为核心的序列架构 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Batch` | 批次：一次参与计算的一组样本 |
| `Loss` | 损失函数：把预测错误压缩成可优化的数值信号 |
| `Optimizer` | 优化器：依据梯度规则更新参数 |
| `Backpropagation` | 反向传播：把最终损失沿计算图反向分配到参数 |
| `Hidden Layer` | 隐藏层：逐层形成内部表示的中间网络层 |
| `Neuron` | 神经元：加权、偏置和非线性变换的最小计算单元 |

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

到第 6 阶段为止，我们已经完整理解：

\[
\boxed{
Forward
\rightarrow
Loss
\rightarrow
Backward
\rightarrow
Optimizer
\rightarrow
ParameterUpdate
}
\]

乍看之下，训练神经网络似乎已经没什么问题了。

那么我们现在问一个非常关键的问题：

> 既然 Backpropagation 可以给所有参数算梯度，为什么不直接把网络堆到 1000 层？

答案是：

\[
\boxed{
数学上能算梯度
\neq
工程上能稳定训练
}
\]

深层网络真正困难的地方，是：

\[
\boxed{
Signal\ Propagation
}
\]

也就是：

> 前向的数值能不能稳定传下去，反向的梯度能不能稳定传回来。

今天我们要把四件看起来分散的东西放到同一个框架中：

\[
\boxed{
Initialization
+
Normalization
+
Residual
+
GradientFlow
}
\]

它们其实都在解决同一个问题：

\[
\boxed{
让深层网络里的信息和梯度保持在“可训练区域”
}
\]

---

## 1. 先把问题放进一个 100 层网络

假设：

\[
h_1=f(W_1x)
\]

\[
h_2=f(W_2h_1)
\]

一直到：

\[
h_{100}=f(W_{100}h_{99})
\]

Forward 时：

\[
x
\rightarrow
h_1
\rightarrow
h_2
\rightarrow
\cdots
\rightarrow
h_{100}
\]

Backward 时：

\[
L
\rightarrow
h_{100}
\rightarrow
h_{99}
\rightarrow
\cdots
\rightarrow
h_1
\]

问题来了。

每经过一层：

> 数值都会变化。

100 层以后：

> 会变成什么？

---

## 2. 一个极端例子

假设先完全忽略 Activation。

每一层只是乘：

\[
0.5
\]

那么：

\[
h_1=0.5x
\]

\[
h_2=0.5h_1
\]

所以：

\[
h_{100}=0.5^{100}x
\]

而：

\[
0.5^{100}
\]

大约：

\[
7.9\times10^{-31}
\]

也就是说：

\[
\boxed{
信号几乎消失
}
\]

---

## 3. 如果每层乘 2 呢？

那么：

\[
h_{100}=2^{100}x
\]

而：

\[
2^{100}
\approx1.27\times10^{30}
\]

于是：

\[
\boxed{
信号爆炸
}
\]

---

## 4. 这就是深度带来的第一个基本问题

如果每层把信号：

> 稍微缩小一点，

几十层以后：

> 消失。

如果每层：

> 稍微放大一点，

几十层以后：

> 爆炸。

所以深层模型需要尽可能让：

\[
\boxed{
SignalScale
}
\]

在层与层之间保持合理。

---

## 5. 第一个核心心智模型

### 心智模型 ①：深度网络首先是一个“信号传播系统”

学习神经网络不要只看：

\[
LayerCount
\]

而应该问：

\[
\boxed{
前向Signal能走多远？
}
\]

以及：

\[
\boxed{
反向Gradient能走多远？
}
\]

今天所有技术几乎都围绕这两个问题展开。

---

## 6. 为什么随机初始化不能随便随机？

模型训练开始时：

\[
W
\]

还没学到任何知识。

所以通常需要：

# Random Initialization

随机初始化。

但“随机”不等于：

> 随便从 \([-100,100]\) 抽。

关键问题是：

\[
\boxed{
随机数的Scale是多少？
}
\]

---

## 7. 假设一个神经元

\[
z=
\sum_{i=1}^{n}w_ix_i
\]

如果：

\[
n
\]

越来越大，而每个：

\[
w_i
\]

尺度保持不变，

那么总和：

\[
z
\]

通常也会越来越大。

---

## 8. 一个简单概率直觉

假设：

\[
x_i
\]

均值为：

\[
0
\]

方差：

\[
Var(x_i)=\sigma_x^2
\]

权重：

\[
Var(w_i)=\sigma_w^2
\]

并做一些简化独立性假设。

则：

\[
Var(z)
\approx
n\sigma_w^2\sigma_x^2
\]

---

## 9. 这意味着什么？

如果：

\[
\sigma_w^2
\]

不随：

\[
n
\]

变化，

那么：

\[
Var(z)
\propto n
\]

输入维度越高：

> 输出数值越来越大。

所以我们希望：

\[
\sigma_w^2
\]

随着：

\[
n
\]

减小。

---

## 10. 最简单目标

如果希望：

\[
Var(z)\approx Var(x)
\]

那么大致希望：

\[
n\sigma_w^2\approx1
\]

也就是：

\[
\boxed{
\sigma_w^2
\approx
\frac1n
}
\]

因此标准差：

\[
\boxed{
\sigma_w
\approx
\frac1{\sqrt n}
}
\]

现在你第一次看到了：

> 为什么权重初始化里经常出现 \(1/\sqrt n\)。

---

## 11. 这不是神秘经验值

它来自一个非常基础的目标：

\[
\boxed{
别让一层之后的方差突然变大或变小
}
\]

这就是：

# Variance Preservation

方差保持。

---

## 12. 什么是 fan-in？

如果一个神经元接收：

\[
n
\]

个输入，

那么：

\[
\boxed{
fan_{in}=n
}
\]

例如：

```python
Linear(768,3072)
```

每个输出神经元读取：

\[
768
\]

个输入。

所以：

\[
fan_{in}=768
\]

---

## 13. 什么是 fan-out？

同一个 Linear：

\[
768\rightarrow3072
\]

输出有：

\[
3072
\]

个单元。

所以：

\[
\boxed{
fan_{out}=3072
}
\]

---

## 14. Xavier Initialization

经典的：

# Xavier Initialization

又叫：

# Glorot Initialization

其中一种常见形式希望同时兼顾：

\[
fan_{in}
\]

和：

\[
fan_{out}
\]

例如方差大致：

\[
\boxed{
Var(W)
=
\frac{2}
{fan_{in}+fan_{out}}
}
\]

---

## 15. 为什么同时考虑 fan-in 和 fan-out？

因为我们不仅希望：

> Forward 信号稳定。

还希望：

> Backward Gradient 也不要剧烈改变尺度。

所以 Xavier 是一种：

\[
\boxed{
Forward/Backward\ Scale\ Compromise
}
\]

---

## 16. Xavier 特别适合什么直觉？

对于像：

\[
Tanh
\]

这类相对对称 Activation，

Xavier 是经典选择之一。

但现在不要形成：

> Tanh 必须 Xavier。

真正理解它背后的原则：

> 保持信号尺度。

---

## 17. ReLU 出现以后为什么要修改？

ReLU：

\[
ReLU(x)=\max(0,x)
\]

对于大致对称、均值接近 0 的输入：

> 大约一部分负值会被变成 0。

也就是说：

> 一部分信号能量被删掉。

---

## 18. 如果还用原来的尺度会怎样？

每经过 ReLU：

> 方差可能逐层减小。

于是网络越深：

> Activation 越来越弱。

所以需要：

> 稍微更大的初始化尺度进行补偿。

---

## 19. He Initialization

针对 ReLU 类网络的经典初始化：

# He Initialization

常见方差：

\[
\boxed{
Var(W)
=
\frac{2}{fan_{in}}
}
\]

因此标准差大约：

\[
\boxed{
\sqrt{\frac{2}{fan_{in}}}
}
\]

---

## 20. 为什么有这个 2？

粗略直觉：

> ReLU 大约砍掉了一部分输入，

所以初始化时：

> 适当增加 Weight 方差进行补偿。

严格推导会更细，但现在这个直觉已经够用。

---

## 21. 第二个核心心智模型

### 心智模型 ②：好的初始化不是为了给模型“好答案”，而是为了让模型从一个“好训练的位置”开始

Initialization 并不是：

> 提前塞业务知识。

而是在训练 Step 0 时确保：

\[
\boxed{
Activation不过大不过小
}
\]

\[
\boxed{
Gradient不过大不过小
}
\]

让 Optimizer 有机会真正工作。

---

## 22. 为什么不能全部初始化成 0？

这是经典问题。

假设一个 Hidden Layer 有两个神经元。

所有：

\[
W=0
\]

Bias：

\[
b=0
\]

那么两个神经元：

> Forward 输出完全一样。

---

## 23. Backward 会怎样？

因为：

> 它们输入一样、参数一样、输出一样，

所以得到的：

> Gradient 也完全一样。

更新以后：

> 仍然一样。

于是永远学不出不同 Feature。

---

## 24. 这叫 Symmetry Problem

# 对称性问题

神经元之间必须在初始化阶段：

> 有一点不同。

随机初始化：

> 打破对称。

于是不同 Neuron 可以逐渐学习不同方向。

---

## 25. Bias 可以初始化为 0 吗？

通常很多层：

\[
b=0
\]

完全没问题。

为什么？

因为 Weight 已经随机：

> 神经元之间的对称性已经被打破。

---

## 26. 初始化太大会发生什么？

例如 Sigmoid：

如果：

\[
z=20
\]

那么：

\[
\sigma(z)\approx1
\]

如果：

\[
z=-20
\]

那么：

\[
\sigma(z)\approx0
\]

进入：

# Saturation

---

## 27. Saturation 的后果

Sigmoid 导数：

\[
\sigma(z)(1-\sigma(z))
\]

在两边都：

\[
\approx0
\]

所以模型刚开始：

> 梯度就可能很弱。

也就是：

\[
\boxed{
BadInitialization
\rightarrow
BadGradientFlow
}
\]

---

## 28. ReLU 初始化太大会怎样？

Activation：

> 可能变得非常大。

下一层再乘 Weight：

> 更大。

最终：

- Activation 爆炸；
- Gradient 爆炸；
- Loss 不稳定；
- NaN。

---

## 29. 初始化太小呢？

信号：

\[
0.01
\]

乘：

\[
0.01
\]

再乘：

\[
0.01
\]

深层以后：

> 几乎为 0。

所以：

\[
\boxed{
Initialization
就是在控制深层信号的第一口气
}
\]

---

## 30. 可初始化解决所有深层问题吗？

不能。

假设训练刚开始尺度很好。

训练：

\[
10000
\]

个 Step 后：

\[
W
\]

已经改变。

原来的初始化保证：

> 不再自动成立。

所以需要第二种机制：

\[
\boxed{
Normalization
}
\]

---

## 31. 什么叫 Normalization？

非常粗略地说：

> 对中间表示的尺度进行重新标准化。

例如某层输出：

\[
x=
[100,-70,300,45]
\]

可能非常难训练。

Normalization 希望把它：

> 调回比较稳定的范围。

---

## 32. 为什么尺度稳定有利于训练？

因为下一层：

\[
Wx
\]

的数值尺度直接由：

\[
x
\]

决定。

如果某层输出今天：

\[
10^{-5}
\]

明天：

\[
10^5
\]

Optimizer 要处理的环境：

> 极其不稳定。

---

## 33. 第三个核心心智模型

### 心智模型 ③：Normalization 的核心不是“把数字变漂亮”，而是控制网络内部的运行尺度

可以把它理解成：

\[
\boxed{
Internal\ Numerical\ Stabilizer
}
\]

使各层尽量工作在：

> 合理数值范围。

---

## 34. 先理解均值和方差

一组数：

\[
x_1,x_2,\ldots,x_n
\]

均值：

\[
\mu
=
\frac1n
\sum_i x_i
\]

方差：

\[
\sigma^2
=
\frac1n
\sum_i(x_i-\mu)^2
\]

---

## 35. Standardization

经典标准化：

\[
\boxed{
\hat x_i
=
\frac{x_i-\mu}
{\sqrt{\sigma^2+\epsilon}}
}
\]

结果大致：

\[
Mean\approx0
\]

\[
Variance\approx1
\]

---

## 36. 为什么有 \(\epsilon\)？

避免：

\[
\sigma^2=0
\]

导致除以 0。

同时：

> 增强数值稳定性。

---

## 37. 但如果永远强行均值 0、方差 1，会不会限制模型？

会。

因此 Normalization 后经常加入可训练参数：

\[
\gamma
\]

和：

\[
\beta
\]

得到：

\[
\boxed{
y
=
\gamma\hat x+\beta
}
\]

---

## 38. \(\gamma\) 做什么？

控制：

> Scale。

\[
\gamma
\]

可以让网络重新：

> 放大或缩小。

---

## 39. \(\beta\) 做什么？

控制：

> Shift。

可以重新：

> 平移均值。

---

## 40. 所以 Normalization 不是强制所有层永远标准正态

更准确是：

1. 先把输入变成稳定标准尺度；
2. 再允许模型通过 \(\gamma,\beta\) 学合适变换。

---

## 41. 最经典的 BatchNorm

# Batch Normalization

曾经在 CNN 等模型中非常重要。

它通常沿：

> Batch 统计均值和方差。

---

## 42. 一个简单例子

某个 Feature 在 Batch 中有：

\[
[3,5,7,9]
\]

BatchNorm 会根据：

> 这 4 个样本的统计量

进行标准化。

所以一个样本的结果：

> 会受到其它 Batch 样本影响。

---

## 43. 为什么这对 NLP/Transformer 不理想？

语言模型经常：

- Batch 大小变化；
- Sequence Length 变化；
- 在线推理可能 Batch=1；
- Token 结构复杂。

如果归一化严重依赖 Batch：

> 很不方便。

于是 Transformer 更常使用：

# Layer Normalization

---

## 44. LayerNorm 的关键区别

LayerNorm 对：

> 单个样本当前 Hidden Vector 内部

进行标准化。

例如：

\[
h=
[h_1,h_2,\ldots,h_d]
\]

计算：

\[
\mu_h
\]

和：

\[
\sigma_h^2
\]

沿 Hidden Dimension 归一化。

---

## 45. 假设 Hidden Size = 4

一个 Token：

\[
h=[2,4,6,8]
\]

LayerNorm 只使用：

> 这一个 Token 自己的 4 个 Hidden Dimension。

并不需要其它 Batch 样本。

---

## 46. 这为什么特别适合 Transformer？

因为每个 Token：

> 都有自己的 Hidden State。

LayerNorm 可以：

> 独立稳定每个 Token 的 Hidden Representation。

因此不依赖：

\[
BatchSize
\]

---

## 47. Transformer Shape 下怎么理解？

如果：

\[
H.shape
=
(B,S,D)
\]

例如：

\[
(8,2048,4096)
\]

LayerNorm 通常对最后：

\[
D=4096
\]

维做归一化。

---

## 48. 也就是说

对于：

\[
8\times2048
\]

个 Token 位置，

每一个位置：

> 分别对自己的 4096 维向量归一化。

---

## 49. 这又回到 Shape 思维

看到：

```python
LayerNorm(4096)
```

你应该想到：

\[
\boxed{
Normalize\ last\ hidden\ dimension
}
\]

而不是：

> 把整个 Batch 所有数字混起来。

---

## 50. LayerNorm 公式

设：

\[
x\in\mathbb R^d
\]

均值：

\[
\mu
=
\frac1d\sum_{i=1}^d x_i
\]

方差：

\[
\sigma^2
=
\frac1d\sum_i(x_i-\mu)^2
\]

然后：

\[
\boxed{
LN(x)
=
\gamma
\odot
\frac{x-\mu}
{\sqrt{\sigma^2+\epsilon}}
+
\beta
}
\]


---

## 51. LayerNorm 自己也有参数吗？

有。

通常：

\[
\gamma\in\mathbb R^d
\]

\[
\beta\in\mathbb R^d
\]

所以：

```python
LayerNorm(4096)
```

通常还存在：

> 可训练 Scale 和 Bias。

---

## 52. 那些参数多吗？

Hidden Size：

\[
4096
\]

LayerNorm 参数约：

\[
4096+4096
=
8192
\]

相比一个：

\[
4096\times4096
\]

的大矩阵：

> 非常少。

---

## 53. 什么是 RMSNorm？

现代 LLM 经常看到：

# RMSNorm

例如一些现代 Transformer 架构中很常见。

---

## 54. RMSNorm 与 LayerNorm 的核心差别

LayerNorm：

> 减均值，再除标准差。

RMSNorm：

> 通常不减均值。

主要按 Root Mean Square：

> 调整尺度。

---

## 55. RMS 是什么？

\[
RMS(x)
=
\sqrt{
\frac1d
\sum_i x_i^2
}
\]

于是：

\[
\boxed{
RMSNorm(x)
=
\gamma
\odot
\frac{x}
{\sqrt{
\frac1d\sum_i x_i^2+\epsilon
}}
}
\]

一种常见形式就是这样。

---

## 56. 少掉了什么？

相比 LayerNorm：

> 不需要显式减均值。

有些实现也没有：

\[
\beta
\]

所以结构更简单。

---

## 57. 为什么 RMSNorm 能工作？

核心思想是：

> 对很多深层 Transformer 来说，控制表示的整体尺度本身已经非常有价值。

不一定每次都必须：

> 强制中心化到均值 0。

---

## 58. LayerNorm 和 RMSNorm 谁更好？

不能抽象地说：

> 一个绝对更好。

架构设计是整体系统。

现代不同 LLM：

> 可能选择不同 Norm。

真正要掌握的是：

\[
\boxed{
两者都在帮助稳定HiddenState尺度
}
\]

---

## 59. Normalization 能不能改变模型表达能力？

它不仅是：

> 单纯数值预处理。

因为：

\[
\gamma,\beta
\]

可训练，而且 Norm 被放置在网络计算图中。

所以它会参与：

> 网络实际函数。

---

## 60. Normalization 也会影响 Gradient Flow

Backward 会穿过：

\[
LayerNorm
\]

所以它不仅改变 Forward Distribution。

也改变：

> Gradient 的尺度和耦合。

因此：

\[
\boxed{
Normalization
同时影响Forward和Backward
}
\]

---

## 61. 但是现在还有一个问题

即使：

> Initialization 好。

即使：

> 每层都有 Normalization。

如果网络有：

\[
100
\]

层，

信息还是必须：

> 连续穿过 100 个复杂变换。

如果某一层学坏：

> 前面的信息怎么办？

---

## 62. 这就是 Residual Connection 出场的地方

普通网络：

\[
x
\rightarrow
F(x)
\rightarrow
y
\]

Residual：

\[
\boxed{
y=x+F(x)
}
\]

也就是：

> 原输入直接绕过复杂模块，加到输出。

---

## 63. 为什么叫 Residual？

因为：

\[
F(x)
\]

不必学习：

> 完整的新映射。

可以只学习：

> 在原来 \(x\) 上应该增加什么“修正量”。

即：

\[
\boxed{
Residual
=
Correction
}
\]

---

## 64. 一个直觉

不使用 Residual：

> 每层都必须重新构造完整 Representation。

使用 Residual：

> 每层只需要说：

> “基于原来表示，我修改一点什么？”

这通常容易得多。

---

## 65. 政府采购专家类比

假设上一层 Representation 已经表示：

> “这是一个供应商资格条件。”

下一模块不一定需要：

> 把这个事实从零重新建立。

它可以只增加：

> “存在地域性要求。”

下一层再增加：

> “业务必要性证据不足。”

也就是：

\[
\boxed{
ExistingRepresentation
+
Update
}
\]

这只是帮助理解，并不代表网络逐层真的使用这些中文标签。

---

## 66. Residual 最核心的数学价值之一在 Backward

如果：

\[
y=x+F(x)
\]

那么：

\[
\frac{\partial y}{\partial x}
=
1+
\frac{\partial F}{\partial x}
\]

注意这里有一个：

\[
\boxed{
1
}
\]

---

## 67. 这意味着什么？

即使：

\[
\frac{\partial F}{\partial x}
\]

很小，

仍然存在一条：

\[
1
\]

的直接 Gradient Path。

于是：

> 梯度更容易向前层传播。

---

## 68. 第四个核心心智模型

### 心智模型 ④：Residual Connection 给信息和梯度都修了一条“高速公路”

正常路径：

\[
x
\rightarrow
复杂模块
\rightarrow
y
\]

Residual 增加：

\[
x
\longrightarrow
y
\]

因此：

\[
\boxed{
Information\ Highway
+
Gradient\ Highway
}
\]

---

## 69. 如果 \(F(x)=0\) 会怎样？

那么：

\[
y=x
\]

这一层退化成：

# Identity Mapping

恒等映射。

---

## 70. 为什么这很重要？

如果某一层：

> 暂时不知道应该学什么，

它至少可以：

> 接近什么都不做。

而不是：

> 被迫对表示进行巨大破坏。

---

## 71. 所以深层网络可以从“接近浅层网络”开始

这是一种很强的思想。

新增一层：

> 不一定立即改变整个函数。

如果：

\[
F(x)\approx0
\]

那么：

\[
y\approx x
\]

所以增加深度：

> 不再那么危险。

---

## 72. Residual 为什么让几百层网络成为可能？

因为每一层都有：

> Identity Path。

信息可以：

> 跨越很多 Block。

梯度也可以：

> 通过残差路径传播。

这极大改善：

# Trainability

---

## 73. ResNet 是这一思想的经典代表

图像领域中的 ResNet：

\[
x
\rightarrow
F(x)
\]

然后：

\[
x+F(x)
\]

让非常深的 CNN：

> 更容易训练。

后来 Transformer：

> 也大量依赖残差。

---

## 74. Transformer Block 的骨架开始出现了

你以后会看到类似：

\[
x
\rightarrow
Attention
\rightarrow
+
\]

以及：

\[
x
\rightarrow
MLP
\rightarrow
+
\]

也就是：

\[
\boxed{
ResidualAroundAttention
}
\]

和：

\[
\boxed{
ResidualAroundFFN
}
\]

---

## 75. 一个非常简化的 Transformer Block

可以先想成：

\[
x_1
=
x+Attention(x)
\]

再：

\[
x_2
=
x_1+MLP(x_1)
\]

这已经非常接近 Transformer 核心结构。

---

## 76. 但还缺 Norm

现实里经常是：

\[
Norm
\]

与：

\[
Attention/MLP
\]

配合。

于是出现两种重要结构：

# Post-Norm

和：

# Pre-Norm

---

## 77. Post-Norm 直觉

经典原始 Transformer 风格可以抽象成：

\[
\boxed{
y
=
Norm(x+F(x))
}
\]

先：

> Residual Add。

再：

> Normalization。

---

## 78. Pre-Norm 呢？

Pre-Norm：

\[
\boxed{
y
=
x+F(Norm(x))
}
\]

先对模块输入：

> Normalization。

然后：

\[
F
\]

最后加回：

\[
x
\]

---

## 79. 两者看起来只换了顺序

但训练深层网络时：

> Gradient Flow 会明显不同。

现代很多大型语言模型：

> 常见 Pre-Norm 或其变体。

---

## 80. 为什么 Pre-Norm 深层训练通常更稳定？

看：

\[
y=x+F(Norm(x))
\]

从：

\[
x
\]

到：

\[
y
\]

有一条非常直接的：

\[
\boxed{
IdentityPath
}
\]

Norm 没有挡在这条主 Residual Path 后面。

---

## 81. Backward 的直觉

梯度可以直接通过：

\[
y\rightarrow x
\]

沿残差主干传播。

因此：

> 很深的模型更容易训练。

严格理论更复杂，但这个直觉非常重要。

---

## 82. Post-Norm 一定不好吗？

不是。

它有自己的特点，也有优秀模型使用。

但随着模型越来越深：

> Pre-Norm 在训练稳定性方面非常有吸引力。

不要把架构历史演变理解成：

> 老结构错误，新结构真理。

---

## 83. 现在把三个组件组合起来

一个现代深层 Block 可以抽象为：

\[
\boxed{
x
\rightarrow
Norm
\rightarrow
F
\rightarrow
ResidualAdd
}
\]

这三个部分分别在做：

\[
Norm
\]

控制尺度。

\[
F
\]

学习新变换。

\[
Residual
\]

保留主信息路径。

---

## 84. 第五个核心心智模型

### 心智模型 ⑤：现代深层网络不是靠单个技巧稳定，而是靠“初始化 + Norm + Residual + Optimizer”共同形成稳定系统

所以不要问：

> “Residual 和 LayerNorm 到底哪个更重要？”

更准确的问题是：

\[
\boxed{
整个SignalPropagationSystem是否健康？
}
\]

---

## 85. 为什么我们第 6 阶段学 Warmup，现在又有关系了？

即使：

- Initialization 合理；
- Norm 合理；
- Residual 合理；

训练第一步如果：

\[
LR
\]

过大，

仍然可能迅速破坏这些良好尺度。

所以：

\[
Warmup
\]

让训练初期：

> 温和进入稳定区。

---

## 86. 这就是系统思维

深层训练稳定性不是：

\[
Initialization
\]

一个变量决定。

而更像：

\[
\boxed{
Initialization
\times
Normalization
\times
Residual
\times
Activation
\times
Optimizer
\times
LearningRate
}
\]

任何一部分严重异常：

> 都可能训练失败。

---

## 87. 现在看 Gradient Vanishing 的完整来源

它可能来自：

\[
ActivationDerivative<1
\]

也可能来自：

\[
WeightScale<1
\]

也可能来自：

> 深度太大。

还可能来自：

> 不合适的网络结构。

所以：

\[
VanishingGradient
\]

不是 Sigmoid 独有现象。

---

## 88. Gradient Explosion 也一样

可能来自：

- Weight Scale 太大；
- 多层 Jacobian 放大；
- Learning Rate 太高；
- Loss 异常；
- Numerical instability。

因此专家不会：

> 看见梯度爆炸就只调 Gradient Clipping。

---

## 89. Jacobian 是什么？

我们现在第一次轻轻碰一下这个词。

如果一个向量函数：

\[
y=f(x)
\]

那么：

\[
\frac{\partial y}{\partial x}
\]

形成一个矩阵：

# Jacobian

---

## 90. 深层 Backprop 本质在发生什么？

梯度连续乘：

\[
J_LJ_{L-1}\cdots J_1
\]

其中：

\[
J_i
\]

是每层的局部 Jacobian。

---

## 91. 为什么会梯度消失？

如果这些 Jacobian 的典型放大比例：

\[
<1
\]

连续相乘：

\[
\rightarrow0
\]

---

## 92. 为什么会梯度爆炸？

如果典型比例：

\[
>1
\]

连续相乘：

\[
\rightarrow\infty
\]

---

## 93. 所以初始化本质上也在影响 Jacobian

Weight Scale：

> 直接进入局部导数。

Activation：

> 也进入局部导数。

Norm：

> 改变状态尺度和梯度结构。

Residual：

> 引入 Identity Jacobian。

于是四者终于完全统一起来了。

---

## 94. 一个很深的统一公式

残差层：

\[
h_{l+1}
=
h_l+F_l(h_l)
\]

对应 Jacobian：

\[
\boxed{
\frac{\partial h_{l+1}}
{\partial h_l}
=
I+
J_{F_l}
}
\]

这里：

\[
I
\]

是 Identity Matrix。

---

## 95. 这个 \(I\) 为什么这么珍贵？

普通网络只有：

\[
J_F
\]

Residual 网络有：

\[
I+J_F
\]

所以梯度传播时：

> 永远多了一条不经过复杂 \(F\) 的基础路径。

这就是 Residual 在数学上的深层意义。

---

## 96. 这和“模型只是不断做小修正”也一致

如果：

\[
J_F
\]

比较小，

那么：

\[
I+J_F
\]

接近：

\[
I
\]

信息：

> 不会被某一层突然完全扭曲。

---

## 97. 为什么 Residual Branch 也不能无限大？

如果：

\[
F(x)
\]

一层就加：

\[
1000x
\]

那么：

\[
x+F(x)
\]

仍然会爆炸。

所以 Residual 并不意味着：

> 可以完全不管 Scale。

---

## 98. 这就是 Residual Scaling 的思想

某些架构可能使用：

\[
y=x+\alpha F(x)
\]

其中：

\[
\alpha
\]

控制：

> Residual Branch 的更新幅度。

---

## 99. 如果 \(\alpha\) 很小

网络一开始更接近：

\[
y=x
\]

也就是：

> Identity Mapping。

训练再逐渐学：

> 应该添加什么修正。

---

## 100. 这和 Fine-tuning 有一个很漂亮的类比

预训练模型已经有：

\[
x
\]

这样的成熟 Representation。

LoRA/Adapter 很多时候也是在做：

\[
\boxed{
ExistingFunction
+
SmallLearnedUpdate
}
\]

虽然数学结构不完全等同于 Residual Block，但思维非常相似：

> **保留已有能力，在其上学习增量。**


---

## 101. 为什么这对 ProcurementLM 特别有价值？

我们有一个通用基础模型。

它已经知道：

- 中文；
- 基础推理；
- 文本结构；
- 通用知识。

我们真正希望：

> 增加政府采购专业能力。

而不是：

> 把原有模型重新洗掉。

所以：

\[
\boxed{
PreserveBase
+
LearnDelta
}
\]

是后面领域模型设计很重要的思想。

---

## 102. 现在回到 LayerNorm 的政府采购直觉

假设某个 Token Hidden State：

\[
[0.1,80,-30,0.002,\ldots]
\]

某些维度绝对值异常大。

下一层点积：

\[
W h
\]

可能过度被这些尺度主导。

Norm 会先：

> 把整体向量尺度稳定下来。

---

## 103. 但 Norm 会不会把重要信息洗掉？

这是个很好的问题。

标准化确实会改变：

> 均值和尺度。

但不同维度之间的：

> 相对结构仍然保留很多信息。

同时：

\[
\gamma,\beta
\]

还能学习重新缩放。

---

## 104. 对 RMSNorm 来说

它更专注：

> 控制整体 RMS Scale。

方向信息：

\[
\frac{x}{\|x\|}
\]

大体仍然保留。

所以可以粗略理解成：

> 把向量“长度”调到合理区间，而让“方向”继续携带语义。

---

## 105. 这个“方向”以后会非常重要

因为 Attention 会大量依赖：

> 向量之间的点积关系。

Embedding 相似度也和：

> 向量方向密切相关。

所以：

\[
\boxed{
VectorMagnitude
}
\]

和：

\[
\boxed{
VectorDirection
}
\]

要开始分开理解。

---

## 106. 为什么模型训练中经常监控 Activation Statistics？

因为我们想知道：

某一层：

\[
Mean
\]

\[
Std
\]

\[
Max
\]

\[
Min
\]

有没有逐层异常。

如果某层开始：

> 数值巨大，

后面往往很快出问题。

---

## 107. 还可以监控 Gradient Statistics

例如：

\[
GradientNorm
\]

逐层分布。

如果 Layer 1：

\[
10^{-12}
\]

而 Layer 30：

\[
1
\]

说明：

> 前层梯度可能已经严重衰减。

---

## 108. 这就是为什么只看最终 Loss 不够

Loss：

> 只告诉你最终结果。

但训练系统内部可能已经出现：

- Activation 爆炸；
- Gradient 消失；
- 某些层死亡；
- Norm 异常。

因此：

\[
\boxed{
Observability
}
\]

非常重要。

---

## 109. 一个专业的训练诊断视角

如果 Loss 变 NaN，不是立刻说：

> 数据坏了。

可以沿系统检查：

\[
Input
\rightarrow
Activation
\rightarrow
Norm
\rightarrow
Logits
\rightarrow
Loss
\rightarrow
Gradient
\rightarrow
Optimizer
\]

到底从哪一步：

> 第一次出现 Inf/NaN。

---

## 110. 这就叫找 First Failure

不要只看：

> 最终哪里崩了。

要找：

\[
\boxed{
第一个开始异常的节点
}
\]

这是非常强的工程诊断心智模型。

---

## 111. 初始化也不是“模型参数固定规则”

不同 Activation：

> 需要不同 Scale 思考。

不同残差结构：

> 也会改变初始化要求。

不同深度：

> 也可能需要特殊处理。

因此：

\[
\boxed{
Initialization
必须与Architecture匹配
}
\]

---

## 112. Xavier 与 He 不要死记成表格题

真正应该理解：

Xavier：

> 希望层间方差在前向/反向相对稳定。

He：

> 对 ReLU 丢失部分信号做了额外补偿。

只要掌握这个机制：

> 忘了公式也能重新推理。

---

## 113. BatchNorm 与 LayerNorm 也不要死背名称

真正区别首先问：

\[
\boxed{
到底沿哪个维度算统计量？
}
\]

BatchNorm：

> 借 Batch 信息。

LayerNorm：

> 在单样本/Token 的 Hidden Dimension 内归一化。

---

## 114. 以后遇到任何 Norm 都问四件事

第一：

> 对哪些维度算统计量？

第二：

> 减不减 Mean？

第三：

> 用什么 Scale？

第四：

> 有没有可训练参数？

用这四个问题：

> 很多新 Norm 都能拆懂。

---

## 115. 同理，遇到任何 Residual 结构问什么？

问：

> 主路径是谁？

> Residual Branch 是谁？

> 两边 Shape 是否相同？

> 加法发生在哪里？

> Norm 在加法之前还是之后？

这样读架构图会快很多。

---

## 116. 为什么 Residual 两边 Shape 通常要一致？

因为要：

\[
x+F(x)
\]

逐元素相加。

所以：

\[
Shape(x)
=
Shape(F(x))
\]

必须兼容。

---

## 117. Transformer 为什么常保持 Hidden Size 不变？

例如：

\[
4096
\rightarrow
4096
\]

Attention 输出仍：

\[
4096
\]

这样可以直接：

\[
ResidualAdd
\]

---

## 118. 但 FFN 中间为什么能变成 11008？

因为：

\[
4096
\rightarrow
11008
\rightarrow
4096
\]

FFN 最终：

> 又投影回 4096。

所以最后：

\[
F(x)
\]

Shape 与：

\[
x
\]

一致。

才能：

\[
x+F(x)
\]

---

## 119. 现在你第一次能够理解 FFN 为什么“升维再降维”

中间宽：

\[
d_{ff}
\]

提供：

> 更大的非线性处理空间。

最后回到：

\[
d_{model}
\]

确保：

> Residual Connection 可以相加。

以后 Transformer FFN 会正式展开。

---

## 120. 一个简化 Transformer Pre-Norm Block

先看：

\[
u
=
x+
Attention(RMSNorm(x))
\]

再：

\[
\boxed{
y
=
u+
MLP(RMSNorm(u))
}
\]

你现在已经能认出三个组件：

\[
RMSNorm
\]

\[
Attention/MLP
\]

\[
ResidualAdd
\]

---

## 121. 注意：Attention 我们还没学

但这已经不妨碍你理解：

> Transformer 为什么能堆几十层。

因为：

> 每个 Block 都有 Norm 稳尺度，有 Residual 保主路径。

---

## 122. Transformer 为什么不用纯 MLP 一层接一层？

如果纯粹：

\[
H_{l+1}=MLP(H_l)
\]

几十层以后：

> 优化会困难很多。

Residual：

\[
H_{l+1}
=
H_l+MLP(\cdot)
\]

让深度模型：

> 更像对表示进行连续小更新。

---

## 123. 一个非常有价值的宏观视角

可以把 Transformer 的层级计算理解成：

\[
H_0
\]

是初始表示。

Layer 1：

\[
H_1
=
H_0+\Delta H_1
\]

Layer 2：

\[
H_2
=
H_1+\Delta H_2
\]

……

最终：

\[
H_L
=
H_0+
\sum_{l=1}^{L}\Delta H_l
\]

这只是概念化表达，但非常有帮助。

---

## 124. 模型可以被看成“表示逐步修正器”

不是：

> 每层把前一层全部推翻。

而是：

\[
\boxed{
Representation
\rightarrow
Refinement
\rightarrow
Refinement
\rightarrow
Refinement
}
\]

这和专家逐步阅读上下文的直觉很相似。

---

## 125. 但不要把 Residual 简化成“每层贡献独立知识”

因为：

\[
\Delta H_l
\]

依赖：

\[
H_l
\]

而：

\[
H_l
\]

已经包含前面所有计算结果。

所以这些修正：

> 高度互相依赖。

---

## 126. Gradient 也可以沿很多路径传播

Residual Network 中：

> 从输出回到早期层不只有一条长链。

而存在：

> 多种短路径和长路径组合。

这也是残差网络优化优势的一部分直觉。

---

## 127. 为什么更深仍然不是无限免费？

即使有 Residual：

- 计算量增加；
- Activation Memory 增加；
- 参数增加；
- 通信增加；
- 训练稳定性仍变难。

所以：

\[
Depth\uparrow
\]

不是没有成本。

---

## 128. Norm 也不是免费

每个 Norm：

> 都需要额外计算。

并且架构选择：

> 会影响模型行为。

所以系统设计仍然需要权衡。

---

## 129. 一个常见误区：有 LayerNorm 就不会梯度爆炸

错误。

LayerNorm：

> 有助于稳定。

但如果：

\[
LR
\]

巨大，

或者：

\[
Loss
\]

异常，

或者：

> 数值溢出，

依然可以爆炸。

---

## 130. 另一个误区：Residual 一定保证梯度不消失

也不准确。

Residual：

> 显著改善梯度路径。

但深层训练仍可能受到：

- Scale；
- Norm；
- Optimizer；
- Activation；
- 精度；

等因素影响。

---

## 131. 专家不会寻找“单个救世主”

不是：

> “用了 RMSNorm 就稳定了。”

也不是：

> “用了 Residual 就万事大吉。”

更好的心智模型是：

\[
\boxed{
StableTraining
=
SystemProperty
}
\]

训练稳定：

> 是整个系统涌现出来的属性。

---

## 132. 这和政府采购 AI 架构也非常像

最终质量不是：

> “有 LLM 就行。”

而是：

\[
LLM
+
RAG
+
Rules
+
Parser
+
Evaluation
+
HumanReview
\]

共同决定。

同样：

> 神经网络内部稳定性也依赖多个组件共同工作。

---

## 133. 第六个核心心智模型

### 心智模型 ⑥：强系统通常不是靠某个组件“解决问题”，而是靠多层机制互相兜底

内部训练：

\[
Initialization
\]

保证起点。

\[
Normalization
\]

控制运行尺度。

\[
Residual
\]

保证信息通道。

\[
Optimizer
\]

控制更新。

\[
GradientClipping
\]

提供异常保护。

---

## 134. 这其实就是 Defense in Depth

第一课我们讲生产风险控制时用了：

\[
DefenseInDepth
\]

现在神经网络内部也是类似思想。

没有任何一个机制：

> 绝对可靠。

多个机制组合：

> 提高稳定性。

---

## 135. 回到具体训练：你应该看哪些信号？

以后训练 ProcurementLM 时，至少逐渐形成意识：

\[
TrainLoss
\]

\[
ValidationLoss
\]

\[
LearningRate
\]

\[
GradientNorm
\]

以及必要时：

\[
ActivationStatistics
\]

---

## 136. 如果第一步 Loss 就 NaN

优先怀疑：

> Forward 数值问题。

例如：

- Input 有 NaN；
- Logits 爆炸；
- Loss 数值不稳定；
- FP16 Overflow。

这时还没必要讨论：

> Overfitting。

---

## 137. 如果前几十步正常，突然爆炸

可以看：

> LR 当前位置。

> Gradient Norm 是否提前升高。

> 某个 Batch 是否异常。

> Optimizer State 是否异常。

这就是：

\[
\boxed{
TimelineDiagnosis
}
\]

---

## 138. 如果 Deep Layer 有梯度，Early Layer 没有

强烈提示：

\[
GradientFlowProblem
\]

可能需要检查：

- Activation；
- Initialization；
- Residual；
- Norm；
- 架构。

---

## 139. 如果所有 Gradient 都接近 0

也可能不是网络太深。

还有可能：

> 参数全被冻结。

或者：

> Loss 与模型输出计算图断开。

所以再次：

\[
Diagnosis
>
Guessing
\]

---

## 140. 为什么 `detach()` 会导致梯度突然断掉？

因为：

\[
detach
\]

人为告诉 Autograd：

> 从这里不要再往前追。

所以某个错误的 `.detach()`：

> 可以直接让前面网络不学习。

---

## 141. Residual 也必须在计算图里保持可微

正常：

\[
y=x+F(x)
\]

Autograd 可以沿：

> 两条路径反向。

如果某一条路径被错误截断：

> Gradient Behavior 就会改变。

---

## 142. 现在把第二课 1～7 阶段串成一个完整网络

第 1 阶段：

\[
WX+b
\]

第 2 阶段：

\[
Activation
\]

第 3 阶段：

\[
HiddenRepresentation
\]

第 4 阶段：

\[
Forward
\]

第 5 阶段：

\[
Backward
\]

第 6 阶段：

\[
Optimizer
\]

第 7 阶段：

\[
\boxed{
SignalStability
}
\]

---

## 143. 到这里，“神经网络为什么能够变深”终于补齐

只有：

\[
Backprop
\]

还不够。

真正能训练现代深网络，还需要：

\[
\boxed{
Backprop
+
GoodInitialization
+
Normalization
+
ResidualConnections
+
StableOptimization
}
\]

---

## 144. 本阶段最重要的五个专家心智模型

| 心智模型 | 核心认知 |
|---|---|
| **① 深度网络首先是信号传播系统** | 前向 Activation 和反向 Gradient 都必须能跨很多层稳定传播 |
| **② 初始化的目标是创造“可训练起点”** | Xavier/He 的本质是控制初始方差，而不是给模型先验答案 |
| **③ Normalization 是网络内部尺度稳定器** | LayerNorm/RMSNorm 让 Hidden State 工作在更稳定范围 |
| **④ Residual 是信息与梯度高速公路** | \(y=x+F(x)\) 保留 Identity Path，让深层模型更容易训练 |
| **⑤ 深层稳定性是系统属性** | Initialization、Norm、Residual、Activation、Optimizer、LR 必须协同 |

---

## 145. 如果只记四个公式

初始化的方差直觉：

\[
\boxed{
Var(W)
\propto
\frac1{fan_{in}}
}
\]

He：

\[
\boxed{
Var(W)
\approx
\frac2{fan_{in}}
}
\]

LayerNorm：

\[
\boxed{
LN(x)
=
\gamma
\odot
\frac{x-\mu}
{\sqrt{\sigma^2+\epsilon}}
+
\beta
}
\]

Residual：

\[
\boxed{
y=x+F(x)
}
\]

这四个公式已经覆盖今天绝大多数思想。

---

## 146. 如果只记一句话

\[
\boxed{
深度模型真正困难的不是“层数够不够多”，
而是让信息向前走几百层、梯度向后走几百层以后，
仍然保持在一个可用、可训练的尺度。
}
\]

---

## 147. 一个采购 AI 小思维实验

假设一个 80 层模型处理：

> “供应商须在合同签订前于采购人所在地设立服务机构。”

模型需要保持的信息可能包括：

\[
地域实体
\]

\[
时间条件
\]

\[
约束对象
\]

\[
履约阶段
\]

\[
必要性上下文
\]

这些信息不能：

> 在前 10 层以后就数值衰减到消失。

Residual：

> 帮助已有表示继续存在。

Norm：

> 控制表示尺度。

Attention/MLP：

> 再不断补充、修改表示。

这就是现代 Transformer 的工作底座。

---

## 148. 再做一个架构识别练习

以后看到：

```text
x
│
├───────────────┐
│               │
RMSNorm         │
│               │
Attention       │
│               │
└────── + ──────┘
        │
        h
```

你应该立刻认出：

> Pre-Norm。

> Residual Connection。

> Attention Branch。

> Identity Path。

---

## 149. 再看到

```text
h
│
├───────────────┐
│               │
RMSNorm         │
│               │
MLP             │
│               │
└────── + ──────┘
        │
        y
```

你应该知道：

> 第二个 Residual Sub-layer。

于是完整 Transformer Block 已经几乎出现。

---

## 150. 第二课 · 第 7 阶段掌握标准

学完以后，你应该能够自然回答这些问题：

> 为什么所有 Weight 不能初始化为 0？

> 为什么随机初始化的 Scale 很重要？

> fan-in 与 fan-out 是什么？

> Xavier 与 He 初始化分别在解决什么问题？

> 为什么 ReLU 对初始化尺度有特殊要求？

> Normalization 真正稳定的是什么？

> BatchNorm 与 LayerNorm 最根本区别是什么？

> 为什么 Transformer 更偏好 LayerNorm/RMSNorm？

> RMSNorm 与 LayerNorm 的核心差别是什么？

> 为什么 Norm 后还需要可训练 Scale？

> \(y=x+F(x)\) 为什么对 Gradient Flow 有帮助？

> 什么叫 Identity Path？

> 为什么深层 Residual Network 比纯层叠 MLP 更容易训练？

> Pre-Norm 与 Post-Norm 区别在哪里？

> 为什么现代 LLM 很多使用 Pre-Norm 风格？

> 为什么 `4096 → 11008 → 4096` 最终还要回到 4096？

> 为什么 Transformer 的 Attention 和 FFN 都被 Residual 包围？

> 为什么“训练稳定性”应该看成系统属性，而不是某个单独 Trick？

如果这些问题你已经能够从机制上解释，而不是只背名字：

\[
\boxed{
第二课第7阶段就真正学会了
}
\]

---

接下来第二课会发生一个非常关键的转折。

前 7 个阶段主要在回答：

\[
\boxed{
一个DeepNeuralNetwork
究竟是怎么构造、计算和训练的？
}
\]

下一阶段开始，我们要进入：

# **第二课 · 第 8 阶段：Embedding 与高维向量空间**

也就是正式回答那个迟早必须解决的问题：

> **神经网络只能处理数字，那么“供应商”“注册资本”“本市”“不得低于5000万元”这些文字，究竟怎样变成模型能计算的数字？**

我们将从最原始的：

\[
OneHot
\]

开始，一步步走到：

\[
\boxed{
EmbeddingMatrix
}
\]

再到：

\[
\boxed{
SemanticVectorSpace
}
\]

并真正推导出：

\[
TokenID
\rightarrow
EmbeddingLookup
\rightarrow
HiddenVector
\]

那一阶段开始，我们就会正式从“通用神经网络原理”跨进 **NLP 与 LLM 的核心地带**。

---
