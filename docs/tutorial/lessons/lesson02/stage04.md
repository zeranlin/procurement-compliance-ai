# 第二课 · 第 4 阶段：Forward Propagation——一条政府采购样本到底如何从输入开始，逐层穿过整个神经网络，最终变成一个风险概率

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Forward Propagation = 在固定参数下把输入逐层变成输出；Forward 本身不等于学习。**
2. **每一层都同时有“数值”和“Shape”，Shape 跟错会直接导致矩阵运算或后续层语义出错。**
3. **Logit 是模型原始打分，Probability 是经过 Sigmoid/Softmax 等变换后的分数，Business Decision 还要再经过 Threshold。**
4. **同一个输入和同一组参数下，Forward 应是可重复的计算过程；训练发生在后续 Loss、Backward 和 Optimizer Step。**
5. **理解 Forward 的关键不是背每个矩阵，而是能追踪：输入表示 → 中间表示 → 输出分数。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Forward Propagation` | 前向传播：输入逐层计算直到得到预测 |
| `Batch` | 批次：一次参与计算的一组样本 |
| `Loss` | 损失函数：把预测错误压缩成可优化的数值信号 |
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `Transformer` | Transformer：以注意力和前馈网络为核心的序列架构 |
| `PyTorch` | PyTorch：张量计算、自动求导和训练/推理框架 |
| `Backpropagation` | 反向传播：把最终损失沿计算图反向分配到参数 |
| `Input` | 输入：模型在当前任务中允许看到的条件信息 |
| `dtype` | 数据类型：FP32/FP16/BF16 等，影响显存、速度和数值稳定性 |
| `BF16` | BF16：保留较大指数范围的 16 位浮点，常用于大模型 |
| `Optimizer` | 优化器：依据梯度规则更新参数 |
| `Inference` | 推理：系统接收请求并产生结果的在线计算过程 |

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

前三阶段，我们已经拿到了：

\[
\boxed{
z=WX+b
}
\]

\[
\boxed{
h=f(z)
}
\]

以及：

\[
\boxed{
X\rightarrow H_1\rightarrow H_2\rightarrow Y
}
\]

但我们还没有把一条样本从头到尾真正“跑一遍”。

这一阶段要解决的，就是：

\[
\boxed{
Forward\ Propagation
}
\]

前向传播。

---

## 1. 什么叫 Forward Propagation？

最直接的定义：

> **把输入送入模型，按照网络结构从第一层一直计算到最后一层，得到模型输出。**

也就是：

\[
\boxed{
Input
\rightarrow
Layer_1
\rightarrow
Layer_2
\rightarrow
\cdots
\rightarrow
Output
}
\]

这个过程就叫：

# Forward Pass

或者：

# Forward Propagation

---

## 2. 为什么叫“Forward”？

因为信息流动方向是：

\[
X
\rightarrow
Prediction
\]

从输入：

> 向输出方向走。

以后 Backpropagation：

\[
Loss
\rightarrow
Parameters
\]

则沿计算关系：

> 从后往前计算梯度。

所以：

\[
\boxed{
Forward
=
算答案
}
\]

\[
\boxed{
Backward
=
算责任
}
\]

这个直觉非常重要。

---

## 3. 先看完整训练链

第一课我们反复看到：

```text
Batch
↓
Forward
↓
Loss
↓
Backward
↓
Optimizer
↓
Update
```

现在第二课开始拆其中的：

\[
\boxed{
Forward
}
\]

到底发生了什么。

---

## 4. 一个最简单的两层网络

假设：

\[
X
\]

进入第一层：

\[
z_1=W_1X+b_1
\]

然后：

\[
h_1=ReLU(z_1)
\]

再进入输出层：

\[
z_2=W_2h_1+b_2
\]

最后二分类：

\[
p=\sigma(z_2)
\]

完整：

\[
\boxed{
p
=
\sigma(
W_2ReLU(W_1X+b_1)+b_2
)
}
\]

---

## 5. Forward 就是在真正执行这个公式

不是一次性“神奇算出”。

而是按照顺序：

```text
X
↓
W1X + b1
↓
z1
↓
ReLU
↓
h1
↓
W2h1 + b2
↓
z2
↓
Sigmoid
↓
p
```

每一步都有：

> 输入。

每一步都有：

> 输出。

---

## 6. 第一个核心心智模型

### 心智模型 ①：Forward 是“模型当前知识的一次执行”

训练好的参数：

\[
W,b
\]

可以理解成：

> 模型已经学到的长期状态。

输入：

\[
X
\]

进入后：

> 参数开始对这个具体案例进行计算。

最后产生：

\[
Prediction
\]

所以：

\[
\boxed{
Forward
=
用当前参数处理当前输入
}
\]

---

## 7. Forward 本身不会修改参数

这是非常重要的一点。

前向计算：

\[
W_1X+b_1
\]

只是：

> 使用 \(W_1\)。

并不会自动改变：

\[
W_1
\]

所以：

\[
\boxed{
Forward\ does\ not\ learn
}
\]

学习发生在：

\[
Backward + OptimizerStep
\]

之后。

---

## 8. 推理时其实主要就是 Forward

模型上线以后：

用户输入：

> 一份采购文件。

系统：

```text
Input
↓
Forward
↓
Prediction
```

通常不会：

```text
Backward
↓
Update Parameters
```

所以：

\[
\boxed{
Inference
主要就是Forward
}
\]

---

## 9. 训练为什么也需要 Forward？

因为你必须先知道：

> 模型当前预测了什么。

才能计算：

\[
Loss
\]

例如：

真实：

\[
y=1
\]

Forward：

\[
p=0.23
\]

然后才知道：

> 错得很厉害。

所以训练一定先：

\[
Forward
\]

再：

\[
Loss
\]

---

## 10. 今天第一次正式引入 Tensor

深度学习代码里最常出现的一个词：

# Tensor

张量。

你以后几乎每天都会看到。

---

## 11. Scalar 是什么？

一个数字：

\[
3.7
\]

叫：

# Scalar

标量。

Shape 可以理解为：

\[
()
\]

---

## 12. Vector 是什么？

一维数组：

\[
X=
[0.2,0.7,0.9]
\]

叫：

# Vector

向量。

Shape：

\[
(3,)
\]

---

## 13. Matrix 是什么？

二维数字表：

\[
W=
\begin{bmatrix}
1&2&3\\
4&5&6
\end{bmatrix}
\]

Shape：

\[
(2,3)
\]

叫：

# Matrix

矩阵。

---

## 14. Tensor 又是什么？

Tensor 可以把它理解为：

> **更一般化的多维数字数组。**

例如：

\[
(32,768)
\]

二维 Tensor。

或者：

\[
(8,2048,4096)
\]

三维 Tensor。

甚至：

\[
(B,H,S,D)
\]

四维 Tensor。

---

## 15. 为什么不用一直说 Matrix？

因为真实深度学习数据经常：

> 不止两维。

例如 Transformer：

\[
Batch
\times
Sequence
\times
Hidden
\]

所以需要更一般的：

\[
\boxed{
Tensor
}
\]

---

## 16. Tensor 有几个核心属性？

以后你看到一个 Tensor，要习惯问：

1. Shape 是什么？
2. Dtype 是什么？
3. Device 在哪里？
4. 数值代表什么？

这四个问题非常重要。

---

## 17. Shape

例如：

\[
X.shape=(32,768)
\]

意味着：

```text
32 个样本
×
每个样本 768 个数字
```

---

## 18. Dtype

例如：

- FP32
- FP16
- BF16
- INT8

代表：

> 数字用什么精度存储。

以后训练大模型：

\[
BF16
\]

会非常常见。

---

## 19. Device

Tensor 可能在：

```text
CPU
```

或者：

```text
GPU
```

例如 PyTorch 里常见：

```python
x.device
```

如果：

> 模型参数在 GPU，输入却在 CPU，

通常不能直接计算。

---

## 20. 第二个核心心智模型

### 心智模型 ②：深度学习程序本质是在让 Tensor 不断改变 Shape 和数值

例如：

```text
(32, 20)
↓ Linear
(32, 64)
↓ ReLU
(32, 64)
↓ Linear
(32, 1)
↓ Sigmoid
(32, 1)
```

Forward 不只是：

> 数学公式。

还可以理解成：

\[
\boxed{
Tensor\ Transformation
}
\]

---

## 21. 现在做一次真正完整的数值 Forward

我们不再只说概念。

假设一个政府采购风险模型输入只有两个 Feature：

\[
x_1=\text{竞争限制程度}
\]

\[
x_2=\text{业务必要性程度}
\]

输入：

\[
X=
\begin{bmatrix}
0.8\\
0.3
\end{bmatrix}
\]

---

## 22. 第一层有三个神经元

网络：

\[
2
\rightarrow
3
\rightarrow
1
\]

也就是：

```text
Input: 2
Hidden: 3
Output: 1
```

---

## 23. 第一层权重

假设：

\[
W_1=
\begin{bmatrix}
1.0&-0.5\\
0.4&0.8\\
-0.7&1.2
\end{bmatrix}
\]

Shape：

\[
(3,2)
\]

为什么？

因为：

\[
2维输入
\rightarrow
3维输出
\]

---

## 24. 第一层 Bias

\[
b_1=
\begin{bmatrix}
0.1\\
-0.2\\
0.3
\end{bmatrix}
\]

Shape：

\[
(3,)
\]

---

## 25. 先计算第一个 Hidden Neuron

第一行：

\[
z_{1,1}
=
1.0(0.8)
+
(-0.5)(0.3)
+
0.1
\]

所以：

\[
0.8-0.15+0.1
\]

得到：

\[
\boxed{
0.75
}
\]

---

## 26. 第二个神经元

\[
z_{1,2}
=
0.4(0.8)
+
0.8(0.3)
-0.2
\]

即：

\[
0.32+0.24-0.2
\]

得到：

\[
\boxed{
0.36
}
\]

---

## 27. 第三个神经元

\[
z_{1,3}
=
-0.7(0.8)
+
1.2(0.3)
+
0.3
\]

即：

\[
-0.56+0.36+0.3
\]

得到：

\[
\boxed{
0.10
}
\]

---

## 28. 所以第一层 Linear 输出

\[
z_1=
\begin{bmatrix}
0.75\\
0.36\\
0.10
\end{bmatrix}
\]

输入：

\[
2维
\]

变成：

\[
3维
\]

---

## 29. 然后经过 ReLU

因为三个数都大于 0：

\[
ReLU(z_1)=z_1
\]

因此：

\[
h_1=
\begin{bmatrix}
0.75\\
0.36\\
0.10
\end{bmatrix}
\]

---

## 30. 如果第三个值原来是 -0.10 呢？

那么：

\[
ReLU(-0.10)=0
\]

于是：

\[
h_1=
[
0.75,
0.36,
0
]
\]

这就是 Activation：

> 真正改变表示。

---

## 31. Hidden State 是什么？

现在这个：

\[
h_1
\]

就是：

# Hidden State

或者：

# Hidden Representation

它不是最终答案。

它是：

> 网络处理完第一层以后，对这个采购案例形成的内部数字表示。

---

## 32. 再进入输出层

假设：

\[
W_2=
\begin{bmatrix}
1.2&-0.8&0.5
\end{bmatrix}
\]

Bias：

\[
b_2=-0.4
\]

---

## 33. 输出 Logit

\[
z_2
=
1.2(0.75)
-0.8(0.36)
+
0.5(0.10)
-0.4
\]

计算：

\[
0.90-0.288+0.05-0.4
\]

得到：

\[
\boxed{
z_2=0.262
}
\]

---

## 34. 这个 0.262 还是 Logit

它还不是：

> 26.2% 风险。

这是第一课已经学过的：

\[
\boxed{
RawScore
}
\]

---

## 35. 经过 Sigmoid

\[
p=\sigma(0.262)
\]

大约：

\[
\boxed{
p\approx0.565
}
\]

于是模型：

> 当前给出约 0.565 的风险分数。

---

## 36. 完整 Forward 链已经出现

```text
X
[0.8, 0.3]

↓

Linear 1

↓

z1
[0.75, 0.36, 0.10]

↓

ReLU

↓

h1
[0.75, 0.36, 0.10]

↓

Linear 2

↓

z2
0.262

↓

Sigmoid

↓

p
0.565
```

这就是一个完整的：

\[
\boxed{
ForwardPass
}
\]

---

## 37. 第三个核心心智模型

### 心智模型 ③：每一个 Forward 都是在逐层构造“当前案例的内部状态”

不是参数直接：

> 查出一个答案。

而是：

\[
X
\]

经过层层计算，形成：

\[
H_1,H_2,\ldots
\]

最后才得到：

\[
Prediction
\]

---

## 38. 参数和 Activation 再区分一次

权重：

\[
W_1,W_2
\]

Bias：

\[
b_1,b_2
\]

是：

# Parameters

参数。

而：

\[
z_1,h_1,z_2,p
\]

是：

> 当前 Forward 中生成的中间值。

---

## 39. 参数跨样本共享

换另一个采购案例：

\[
X'
\]

仍然使用同一个：

\[
W_1,W_2,b_1,b_2
\]

但会得到不同：

\[
h_1'
\]

所以：

\[
\boxed{
Parameters\ are\ shared
}
\]

\[
\boxed{
Activations\ are\ input-dependent
}
\]

---

## 40. 这也是“模型能力”和“当前状态”的区别

模型能力：

\[
W
\]

比较固定。

当前案例的计算状态：

\[
H
\]

随着输入变化。

这会一直延伸到 LLM。

---

## 41. 一条样本算一次很慢怎么办？

真实训练不会：

> 一条一条手工算。

我们会一次处理：

# Batch

---

## 42. 假设有 4 条采购样本

每条有两个 Feature。

那么：

\[
X=
\begin{bmatrix}
0.8&0.3\\
0.2&0.9\\
0.7&0.1\\
0.4&0.6
\end{bmatrix}
\]

Shape：

\[
\boxed{
(4,2)
}
\]

---

## 43. 这里每一行代表什么？

一行：

> 一个样本。

两列：

> 两个 Feature。

所以：

```text
Batch = 4
Feature Dimension = 2
```

---

## 44. Batch Forward 不需要写四遍公式

我们可以一次：

\[
XW^T+b
\]

完成整个 Batch。

这就是：

# Vectorization

向量化。

---

## 45. 为什么向量化非常重要？

GPU 最擅长：

> 大规模矩阵运算。

它不喜欢：

```python
for sample in samples:
    一个一个慢慢算
```

而喜欢：

\[
\boxed{
Large\ Matrix\ Multiplication
}
\]

---

## 46. 第四个核心心智模型

### 心智模型 ④：GPU 的力量来自“并行执行大量相同的矩阵计算”

Batch：

\[
32
\]

不意味着 GPU：

> 按顺序算 32 次。

而是尽量把它们组合成：

> 大 Tensor 运算。

---

## 47. 这就是为什么 Batch 会提高吞吐量

单样本：

\[
(1,768)
\]

Batch：

\[
(128,768)
\]

同一个 Weight Matrix：

\[
W
\]

一次作用在很多样本上。

GPU 利用率通常会更高。

---

## 48. 但 Batch 越大越好吗？

不是。

因为：

\[
BatchSize\uparrow
\]

会增加：

> Activation Memory。

最终受：

\[
GPU\ Memory
\]

限制。

这就和第一课第 5 阶段接上了。

---

## 49. PyTorch 中 Linear 的 Shape 约定

假设：

```python
nn.Linear(2, 3)
```

PyTorch 参数中的 Weight Shape 通常是：

\[
(3,2)
\]

但用户输入通常：

\[
(Batch,2)
\]

输出：

\[
(Batch,3)
\]

---

## 50. 为什么数学公式有时写 \(WX\)，代码却像 \(XW^T\)？

这是一个非常常见的困惑。

我们前面把单样本写成列向量：

\[
X\in\mathbb R^{d\times1}
\]

于是：

\[
WX
\]

最自然。

代码通常把 Batch 样本放成：

> 每行一个样本。

所以写成：

\[
XW^T
\]

两者只是：

> Shape 约定不同。

---

## 51. 不要被转置吓到

真正应该检查的是：

\[
\boxed{
Dimensions\ must\ match
}
\]

比如：

\[
(32,768)
\times
(768,3072)
\]

得到：

\[
(32,3072)
\]

这才是 Shape 思维。

---

## 52. 矩阵乘法的 Shape 规则

如果：

\[
A:(m,n)
\]

\[
B:(n,p)
\]

那么：

\[
AB:(m,p)
\]

中间的：

\[
n
\]

必须匹配。

---

## 53. 一个必须练成本能的例子

\[
(32,768)
\times
(768,3072)
\]

结果：

\[
\boxed{
(32,3072)
}
\]

记法：

> 外面留下来，中间消掉。

---

## 54. Transformer 以后也一直这样

例如：

\[
(8,2048,4096)
\]

最后一维：

\[
4096
\]

乘：

\[
(4096,4096)
\]

结果仍：

\[
(8,2048,4096)
\]

前面维度：

> 保持。

最后 Hidden Dimension：

> 被 Linear 变换。

---

## 55. 什么叫 Broadcasting？

加入 Bias 时：

输入：

\[
(32,64)
\]

Bias：

\[
(64,)
\]

我们不用复制：

\[
32
\]

份 Bias。

框架会自动：

> 把同一个 Bias 加到每个样本。

这叫：

# Broadcasting

广播。

---

## 56. 例如

\[
Z=XW+b
\]

如果：

\[
Z.shape=(32,64)
\]

而：

\[
b.shape=(64,)
\]

那么相当于：

> 每一行都加同一个 \(b\)。

---

## 57. Broadcasting 很方便，但也会产生 Bug

有时 Shape 不对，

框架却：

> 依然能广播成功。

于是程序不报错，

但是：

> 算错了。

所以专家很重视：

\[
\boxed{
ShapeAssertion
}
\]

---

## 58. Forward 中到底会保存什么？

训练时：

\[
z_1
\]

\[
h_1
\]

\[
z_2
\]

等很多中间值可能需要保留。

为什么？

因为：

> Backward 之后要用。

---

## 59. 举例：ReLU 的梯度需要知道什么？

要知道：

\[
z>0?
\]

因为：

\[
ReLU'(z)
=
\begin{cases}
1&z>0\\
0&z<0
\end{cases}
\]

所以 Backward 时：

> 需要知道前向过程中哪些位置被激活。

---

## 60. 这就是 Activation Memory 的来源之一

深度：

\[
L\uparrow
\]

Sequence：

\[
S\uparrow
\]

Batch：

\[
B\uparrow
\]

Hidden：

\[
H\uparrow
\]

中间 Activation：

> 很快巨大。

---

## 61. 一个 Transformer Hidden Tensor 有多大？

假设：

\[
B=8
\]

\[
S=2048
\]

\[
H=4096
\]

元素数量：

\[
8\times2048\times4096
\]

约：

\[
67M
\]

个数字。

---

## 62. 如果每个数字 BF16 2 Bytes

单个这样规模的 Tensor：

\[
67M\times2
\]

大约：

\[
134MB
\]

而一个 Transformer 有：

> 很多层、很多中间 Tensor。

显存自然快速增加。

---

## 63. 这就是为什么长 Context 很贵

Sequence Length：

\[
2048\rightarrow8192
\]

很多 Activation：

> 直接变成 4 倍。

Attention 里的某些计算甚至增长得更快。

后面专门学。

---

## 64. 现在进入 Computational Graph

这是本阶段特别重要的新概念：

# Computational Graph

计算图。

---

## 65. 什么叫计算图？

假设：

\[
p
=
\sigma(
W_2ReLU(W_1X+b_1)+b_2
)
\]

我们可以拆成节点：

```text
X
↓
MatMul
↓
Add b1
↓
ReLU
↓
MatMul
↓
Add b2
↓
Sigmoid
↓
p
```

每一个运算：

> 都是计算图中的节点。

---

## 66. 图的边表示什么？

表示：

> 一个计算结果被下一步使用。

例如：

\[
z_1
\]

是：

\[
ReLU
\]

的输入。

所以：

```text
z1 → ReLU
```

---

## 67. 为什么计算图重要？

因为 Backpropagation 需要回答：

> 最终 Loss 是怎样通过这些运算依赖每一个参数的？

计算图保存了：

\[
\boxed{
DependencyStructure
}
\]

依赖关系。

---

## 68. 一个最简单计算图

假设：

\[
z=wx+b
\]

\[
p=\sigma(z)
\]

\[
L=L(p,y)
\]

图：

```text
x ─┐
   × w
    ↓
    +
    ↑ b
    ↓
    z
    ↓
 sigmoid
    ↓
    p
    ↓
  loss ← y
    ↓
    L
```

---

## 69. Forward 在计算图上做什么？

从：

\[
x,w,b
\]

开始，

一路向前算：

\[
z
\]

↓

\[
p
\]

↓

\[
L
\]

---

## 70. Backward 将来做什么？

从：

\[
L
\]

开始，

沿计算图反向算：

\[
\frac{\partial L}{\partial p}
\]

\[
\frac{\partial L}{\partial z}
\]

\[
\frac{\partial L}{\partial w}
\]

等等。

所以：

\[
\boxed{
Forward\ creates\ values
}
\]

\[
\boxed{
Backward\ creates\ gradients
}
\]

---

## 71. 第五个核心心智模型

### 心智模型 ⑤：计算图是 Forward 和 Backward 之间的桥梁

Forward 告诉我们：

> 当前每个节点算出了什么。

计算图告诉我们：

> 谁依赖谁。

Backward 才能利用：

> Chain Rule

一路追责。

---

## 72. PyTorch 的 Autograd 本质就在做这个

例如：

```python
y = model(x)
loss = criterion(y, target)
loss.backward()
```

看起来只有三行。

背后却自动构建和遍历：

\[
ComputationalGraph
\]

---

## 73. 什么叫 Autograd？

# Automatic Differentiation

自动微分。

框架会记录：

> Forward 做了哪些可微运算。

然后自动计算：

\[
Gradient
\]

不用我们手推几十亿个参数的导数。

---

## 74. Forward 为什么需要“记录”？

训练模式下，

很多 Tensor 会知道：

> 自己是由什么运算产生的。

例如：

\[
h=ReLU(WX+b)
\]

框架记录：

- MatMul
- Add
- ReLU

等关系。

---

## 75. 推理为什么可以关闭 Gradient Tracking？

因为推理：

> 不需要 Backward。

所以没必要保存：

> 完整梯度计算图。

PyTorch 常见：

```python
with torch.no_grad():
```

或者：

```python
torch.inference_mode()
```

这样能：

> 节省显存和计算。

---

## 76. 训练 Forward 和推理 Forward 完全一样吗？

大部分核心数学：

> 一样。

但有些层会根据模式不同。

例如：

# Dropout

训练：

> 随机关闭部分激活。

推理：

> 通常关闭随机 Dropout。

---

## 77. BatchNorm 也有 Train/Eval 区别

BatchNorm：

训练时：

> 使用 Batch 统计量并更新 running statistics。

推理时：

> 使用累计统计量。

所以：

```python
model.train()
```

和：

```python
model.eval()
```

有真实意义。

---

## 78. Transformer 里常见 LayerNorm

LayerNorm 的 train/eval 行为不像 BatchNorm 那样依赖 running statistics，

但：

> Dropout 等模块仍然有差异。

所以推理时：

\[
model.eval()
\]

依然是标准习惯。

---

## 79. Forward 最后的输出一定是概率吗？

不一定。

模型可以输出：

# Logits

例如：

\[
z=2.3
\]

或者多分类：

\[
[2.3,-0.4,1.1]
\]

---

## 80. 为什么很多训练代码直接输出 Logits？

因为很多 Loss：

> 已经内部组合了 Softmax / Sigmoid 相关的稳定计算。

例如：

```python
BCEWithLogitsLoss
```

直接输入：

\[
logit
\]

通常比：

> 手动 Sigmoid 再 BCE

数值更稳定。

---

## 81. 多分类也类似

常见：

```python
CrossEntropyLoss
```

通常直接接：

\[
Logits
\]

而不是先手动 Softmax。

因为内部会做：

> 更稳定的计算。

---

## 82. 所以网络“输出层”要区分两个概念

### Raw model output

\[
Logit
\]

### 用户想看的结果

\[
Probability
\]

训练代码：

> 经常使用 Logit。

产品界面：

> 可能展示概率或风险等级。

---

## 83. 二分类 Forward

可以写：

\[
X
\rightarrow
Logit
\]

然后训练：

\[
Logit+Y
\rightarrow
BCEWithLogitsLoss
\]

推理：

\[
Logit
\rightarrow
Sigmoid
\rightarrow
Probability
\]

---

## 84. 多分类 Forward

例如风险类型：

```text
资格风险
技术参数风险
评分标准风险
无风险
```

模型输出：

\[
z\in\mathbb R^4
\]

也就是 4 个 Logits。

---

## 85. 然后 Softmax

\[
p_i
=
\frac{e^{z_i}}
{\sum_j e^{z_j}}
\]

得到：

\[
[p_1,p_2,p_3,p_4]
\]

并满足：

\[
\sum_i p_i=1
\]

---

## 86. 但多标签问题不同

一个采购条款可能同时有：

- 资格风险；
- 地域限制；
- 业绩风险。

它们不是：

> 互斥类别。

这叫：

# Multi-label Classification

---

## 87. 多标签通常怎么办？

每一个标签：

> 独立一个 Logit。

例如：

\[
[z_1,z_2,z_3]
\]

然后分别：

\[
\sigma(z_i)
\]

而不是 Softmax 强迫总和为 1。

---

## 88. 这个差别对 ProcurementML 很重要

风险类别往往：

> 可以同时存在。

所以不能机械地：

> 所有问题都用 Softmax。

任务定义必须先明确。

---

## 89. Forward 里面 Loss 算不算一部分？

严格讲：

> 模型的 Forward 通常到模型输出结束。

例如：

\[
X\rightarrow Logits
\]

Loss：

> 属于训练目标计算。

但从一次完整训练步骤来看：

\[
Forward
\rightarrow
Loss
\]

通常连续发生。

---

## 90. 可以把训练前向阶段理解成

\[
\boxed{
ModelForward
+
LossForward
}
\]

先模型产生：

\[
\hat Y
\]

再 Loss Function 产生：

\[
L
\]

然后才进入：

\[
Backward
\]

---

## 91. 一个完整政府采购训练样本

输入：

```text
竞争限制程度 = 0.8
业务必要性 = 0.3
市场竞争充分度 = 0.2
```

标签：

\[
y=1
\]

表示：

> 专家认为存在风险。

---

## 92. 模型 Forward

可能：

\[
X
\rightarrow
H_1
\rightarrow
H_2
\rightarrow
z
\]

得到：

\[
z=-0.7
\]

然后：

\[
p=\sigma(-0.7)\approx0.332
\]

---

## 93. 模型现在错在哪里？

真实：

\[
1
\]

模型：

\[
0.332
\]

也就是说：

> 明显低估风险。

于是 Loss：

> 较高。

---

## 94. Forward 到这里完成使命

Forward 只负责告诉我们：

\[
\boxed{
在当前W下，
这个X会产生什么Prediction
}
\]

它不负责：

> 怎么改 W。

---

## 95. 下一步 Backward 才回答

\[
\boxed{
为了让Prediction更接近Y，
每个参数应该往什么方向改？
}
\]

这就是：

# Credit Assignment

责任分配。

---

## 96. Forward 像什么？

可以把模型想成一个复杂机器。

Forward：

> 把原料放进去，看机器现在产出什么。

Backward：

> 如果成品不对，沿生产线倒查各机器应该调整多少。

这个类比很好用。

---

## 97. 一次 Forward 是确定的吗？

如果：

- 参数固定；
- 输入固定；
- 模型处于确定性推理模式；
- 数值环境固定；

通常结果应该基本确定。

但训练中有：

- Dropout；
- 随机层；
- 某些非确定 GPU 算法；

所以结果可能存在随机性。

---

## 98. LLM 生成为什么看起来随机？

这是另一个层次。

模型 Forward 会计算：

\[
NextTokenProbabilityDistribution
\]

之后 Sampling：

> 可以随机抽 Token。

所以随机性可能发生在：

\[
SamplingPolicy
\]

而不仅是网络 Forward 本身。

---

## 99. Temperature 又在哪里？

LLM 得到 Logits 后：

\[
z_i
\]

可以做：

\[
\frac{z_i}{T}
\]

再 Softmax。

这里：

\[
T
\]

是 Sampling Temperature。

它改变：

> Token 概率分布的尖锐程度。

以后语言模型课程深入。

---

## 100. 第二课 · 第 4 阶段最终压缩

到这里，我们可以把 Forward 压成：

\[
\boxed{
X
\rightarrow
Linear
\rightarrow
Activation
\rightarrow
HiddenState
\rightarrow
\cdots
\rightarrow
Logits
\rightarrow
Prediction
}
\]

训练时继续：

\[
\boxed{
Prediction
\rightarrow
Loss
}
\]

但此时：

> 参数还没有发生任何更新。

本阶段最重要的 5 个心智模型是：

1. **Forward 是当前模型知识的一次执行**：输入在固定参数下逐层变换成预测。
2. **神经网络也是 Tensor Shape Transformation 系统**：每层都必须追踪 Shape、Dtype、Device。
3. **Hidden State 是当前案例动态形成的内部状态**：参数共享，Activation 随输入变化。
4. **Batch + Matrix Multiplication 是 GPU 高吞吐的基础**：现代训练依赖向量化，而不是逐样本循环。
5. **Computational Graph 是 Forward 与 Backward 的桥梁**：Forward 产生数值并建立依赖关系，Backward 才沿图计算梯度。

如果只记一个总流程，请记：

\[
\boxed{
X
\rightarrow
Z_1
\rightarrow
H_1
\rightarrow
Z_2
\rightarrow
H_2
\rightarrow
Logits
\rightarrow
Prediction
}
\]

而下一阶段，我们终于要进入第二课最核心的一块：

# **第二课 · 第 5 阶段：Backpropagation——最终 Loss 到底怎样穿过计算图，把“错误责任”一层层分配给每一个 Weight？**

我们会从一个只有：

\[
w,x,b
\]

的最小计算图开始，真正手算：

\[
\frac{\partial L}{\partial w}
\]

再逐步进入：

\[
Chain\ Rule
\rightarrow
Local\ Gradient
\rightarrow
Gradient\ Flow
\rightarrow
Backpropagation
\]

到那一步，你会第一次真正看清：

> **“模型是怎样从一次犯错中修改自己”的全过程。**

---
