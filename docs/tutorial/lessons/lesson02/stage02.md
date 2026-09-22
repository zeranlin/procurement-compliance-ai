# 第二课 · 第 2 阶段：Activation Function——为什么没有激活函数，再深的神经网络也只是一个线性模型

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **No Activation ⇒ Deep Linear Model。没有非线性激活函数，多层线性层可以合并成一个线性变换。**
2. **Activation Function 的核心作用是引入非线性，使网络能够表示弯曲、分段和更复杂的决策边界。**
3. **ReLU / GELU / SiLU 的差异主要影响数值形状、梯度流和优化行为，不代表某一种激活函数“更懂政府采购”。**
4. **激活函数会影响梯度是否容易传播，因此它既是表达能力问题，也是训练稳定性问题。**
5. **对预训练模型而言，Activation 是架构的一部分，不能因为“另一个函数看起来更好”就随意替换。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Activation Function` | 激活函数：给网络引入非线性表达能力 |
| `Representation` | 表示：模型内部承载语义或特征的向量结构 |
| `Neuron` | 神经元：加权、偏置和非线性变换的最小计算单元 |
| `Gradient` | 梯度：损失对参数变化方向和敏感度的局部信息 |
| `Backpropagation` | 反向传播：把最终损失沿计算图反向分配到参数 |
| `Threshold` | 阈值：把连续分数转成业务动作的决策门槛 |
| `Transformer` | Transformer：以注意力和前馈网络为核心的序列架构 |
| `Initialization` | 初始化：训练开始前设置参数初值 |
| `Softmax` | Softmax：把一组分数转换成归一化权重 |
| `Normalization` | 规范化：稳定中间激活与训练过程 |
| `Hidden Layer` | 隐藏层：逐层形成内部表示的中间网络层 |

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

上一阶段我们把神经网络拆到最小，得到了一个神经元：

\[
\boxed{
z=W^TX+b
}
\]

现在遇到一个根本问题：

> 如果每一层都只是 \(WX+b\)，那把 2 层、20 层、200 层叠起来，真的会变聪明吗？

答案是：

\[
\boxed{
不会
}
\]

真正让神经网络能够表达复杂规律的关键组件之一，就是今天的主角：

\[
\boxed{
Activation\ Function
}
\]

---

## 1. 先把第二阶段放到总路线里

第二课目前走到：

\[
Neuron
\rightarrow
Linear\ Layer
\rightarrow
\boxed{Activation}
\rightarrow
Hidden\ Layer
\rightarrow
Deep\ Network
\rightarrow
Backpropagation
\]

这一阶段我们重点理解：

\[
\boxed{
Sigmoid
\rightarrow
Tanh
\rightarrow
ReLU
\rightarrow
GELU
\rightarrow
SiLU
}
\]

但真正重要的不是背函数名字。

而是回答：

> **为什么神经网络必须有非线性？**

---

## 2. 先复习上一阶段的核心公式

一个神经元：

\[
z=w_1x_1+w_2x_2+\cdots+w_nx_n+b
\]

向量形式：

\[
\boxed{
z=W^TX+b
}
\]

多个神经元组成 Linear Layer：

\[
\boxed{
Z=WX+b
}
\]

这本质上都是：

# Linear / Affine Transformation

线性或仿射变换。

---

## 3. 如果连续放两个 Linear Layer 会怎样？

第一层：

\[
h=W_1X+b_1
\]

第二层：

\[
y=W_2h+b_2
\]

代入第一层：

\[
y
=
W_2(W_1X+b_1)+b_2
\]

展开：

\[
y
=
W_2W_1X
+
W_2b_1
+
b_2
\]

重新定义：

\[
W'=W_2W_1
\]

\[
b'=W_2b_1+b_2
\]

于是：

\[
\boxed{
y=W'X+b'
}
\]

---

## 4. 一个非常重要的结论

两个线性层：

\[
Linear
\rightarrow
Linear
\]

等价于：

\[
Linear
\]

那么：

\[
100
\]

层呢？

仍然可以不断合并。

所以：

\[
\boxed{
Linear
\circ
Linear
\circ
Linear
=
Linear
}
\]

---

## 5. 这意味着什么？

假设你造一个：

> 1000 层神经网络。

但是每一层只有：

\[
WX+b
\]

最终它在数学表达能力上：

> 仍然只是一个大线性模型。

这句话非常重要：

\[
\boxed{
Depth\ alone
\neq
Complexity
}
\]

单纯增加深度，并不会自动产生复杂表达能力。

---

## 6. 那么 Activation 在哪里加入？

真正的神经网络通常这样：

\[
z=W^TX+b
\]

然后：

\[
\boxed{
a=f(z)
}
\]

这里：

\[
f
\]

就是：

# Activation Function

激活函数。

于是一个神经元变成：

\[
\boxed{
a=f(W^TX+b)
}
\]

---

## 7. 为什么叫 Activation？

历史上可以把它理解成：

> 一个神经元接收到足够刺激以后是否“激活”。

但对于我们学习机器学习，最好先把生物学比喻放一边。

它最重要的数学职责是：

\[
\boxed{
引入非线性
}
\]

---

## 8. 第一个核心心智模型

### 心智模型 ①：Activation 的核心不是“激活神经元”，而是“打破线性”

记住：

\[
\boxed{
Linear + Activation
}
\]

才是真正开始产生复杂表达能力的组合。

如果没有 Activation：

\[
Deep\ Network
\]

可以坍缩成：

\[
Single\ Linear\ Layer
\]

---

## 9. 什么叫“非线性”？

简单说：

如果：

\[
f(ax+by)
=
af(x)+bf(y)
\]

总成立，它属于线性关系。

而像：

\[
x^2
\]

\[
\sin x
\]

\[
\max(0,x)
\]

通常都不是线性的。

例如 ReLU：

\[
f(x)=\max(0,x)
\]

就是非常简单的非线性函数。

---

## 10. 一个看起来很简单的函数，为什么这么重要？

ReLU：

\[
\boxed{
ReLU(x)=\max(0,x)
}
\]

如果：

\[
x<0
\]

输出：

\[
0
\]

如果：

\[
x>0
\]

输出：

\[
x
\]

看起来简单得离谱。

但这个“折一下”：

> 就已经打破了纯线性关系。

---

## 11. 用图形直觉看 ReLU

它大概是：

```text
y
↑
│          /
│         /
│        /
│       /
│______/
│
└────────────→ x
       0
```

左边：

\[
y=0
\]

右边：

\[
y=x
\]

在：

\[
x=0
\]

发生折角。

这个折角就是：

> 非线性。

---

## 12. 为什么折角会增加表达能力？

单个线性函数只能画：

> 一条直线。

但多个：

\[
Linear + ReLU
\]

组合以后，可以形成：

> 很多段不同斜率的折线。

二维空间里：

> 可以拼出复杂边界。

高维空间里：

> 可以拼出非常复杂的分区。

---

## 13. 一个政府采购例子

假设：

\[
x=\text{竞争限制程度}
\]

如果风险不是简单：

\[
Risk=2x
\]

而可能是：

> 限制度很小时影响不明显，超过某个阈值后风险迅速上升。

这更像：

\[
Risk
=
ReLU(x-0.5)
\]

也就是说：

当：

\[
x<0.5
\]

输出：

\[
0
\]

当：

\[
x>0.5
\]

风险信号开始增长。

---

## 14. 现实业务中大量存在“阈值效应”

例如项目条件：

> 有一点严格，不一定有问题。

但当多个限制达到某种程度以后：

> 竞争影响显著增强。

这就是：

\[
\boxed{
Threshold\ Effect
}
\]

线性模型很难自然表示这种：

> “超过某个点以后行为发生变化”。

非线性函数则非常适合。

---

## 15. 再看“交互作用”

假设两个变量：

\[
x_1=\text{供应商限制程度}
\]

\[
x_2=\text{业务必要性不足}
\]

现实风险可能是：

> 只有当两者都很高时，风险才明显上升。

也就是说：

\[
Risk
\]

并不是简单：

\[
w_1x_1+w_2x_2
\]

而可能具有：

\[
x_1\times x_2
\]

这样的交互。

---

## 16. 为什么深层非线性网络能表示交互？

第一层可以学习：

> 某个局部模式。

第二层可以组合第一层模式。

第三层继续组合。

例如概念上：

```text
本地限制
+
极短响应
↓
本地履约约束模式
```

再和：

```text
缺少必要性说明
```

组合：

```text
本地履约约束
+
缺乏必要性
↓
高竞争限制风险
```

这就是层级组合。

---

## 17. 这连接到了上一阶段的 Representation

上一阶段说：

\[
RawInput
\rightarrow
Representation
\rightarrow
Prediction
\]

现在再具体一点：

\[
\boxed{
Linear
\rightarrow
Activation
\rightarrow
NewRepresentation
}
\]

每经过一层：

> 输入空间被重新变换一次。

---

## 18. 第二个核心心智模型

### 心智模型 ②：Activation 让网络能够不断“重新切割输入空间”

一个 Linear Layer：

> 画一个超平面。

Activation：

> 把空间折叠、截断或重新映射。

下一层再：

> 重新组合。

于是：

\[
\boxed{
Linear
\rightarrow
Fold
\rightarrow
Linear
\rightarrow
Fold
}
\]

最终可以形成非常复杂的 Decision Boundary。

---

## 19. 先学最经典的 Sigmoid

第一课已经见过：

\[
\boxed{
\sigma(x)=\frac{1}{1+e^{-x}}
}
\]

它把：

\[
(-\infty,+\infty)
\]

压缩到：

\[
(0,1)
\]

---

## 20. Sigmoid 的几个典型值

当：

\[
x=-5
\]

大约：

\[
0.007
\]

当：

\[
x=0
\]

得到：

\[
0.5
\]

当：

\[
x=5
\]

大约：

\[
0.993
\]

它是一个：

> S 型曲线。

---

## 21. Sigmoid 为什么适合二分类输出层？

假设模型最后输出：

\[
z
\]

我们需要：

\[
RiskScore\in(0,1)
\]

那么：

\[
p=\sigma(z)
\]

就非常自然。

所以：

\[
\boxed{
Binary\ Classification
}
\]

中 Sigmoid 经常出现在：

> 最后一层输出。

---

## 22. 但 Sigmoid 作为隐藏层 Activation 有问题

最主要的问题之一：

# Saturation

饱和。

当：

\[
x\gg0
\]

Sigmoid 接近：

\[
1
\]

当：

\[
x\ll0
\]

接近：

\[
0
\]

这两个区域曲线几乎变平。

---

## 23. 为什么“变平”是问题？

因为训练靠：

\[
Gradient
\]

梯度。

如果曲线很平：

\[
\frac{d\sigma}{dx}
\approx0
\]

那么：

> 梯度很小。

反向传播到前面的参数：

> 更新非常弱。

---

## 24. Sigmoid 的导数

一个非常漂亮的公式：

\[
\boxed{
\sigma'(x)
=
\sigma(x)(1-\sigma(x))
}
\]

最大值发生在：

\[
\sigma(x)=0.5
\]

也就是：

\[
x=0
\]

此时最大导数：

\[
0.25
\]

---

## 25. 这意味着什么？

即使最理想位置：

\[
Gradient
\]

最多还要乘：

\[
0.25
\]

如果连续很多层 Sigmoid：

\[
0.25
\times
0.25
\times
0.25
\times\cdots
\]

很快变得非常小。

这就是：

# Vanishing Gradient

梯度消失。

---

## 26. 一个简单数字直觉

假设每层梯度大约乘：

\[
0.2
\]

连续 10 层：

\[
0.2^{10}
\]

约等于：

\[
0.0000001024
\]

也就是说：

> 后层还有明显误差信号，

传到前几层以后：

> 几乎没了。

---

## 27. 这会造成什么？

靠近输出层：

> 学得比较快。

网络早期层：

> 几乎不更新。

深度网络就很难训练。

这也是早期深度神经网络发展中的一个核心难题。

---

## 28. 第三个核心心智模型

### 心智模型 ③：Activation 不只决定表达能力，也决定梯度能不能顺利流动

所以选择 Activation 时要看两件事：

\[
\boxed{
Forward\ Expressiveness
}
\]

以及：

\[
\boxed{
Backward\ GradientFlow
}
\]

一个函数前向表达很好，

但梯度传播极差：

> 训练仍然可能失败。

---

## 29. 第二个经典函数：Tanh

公式：

\[
\boxed{
\tanh(x)
=
\frac{e^x-e^{-x}}
{e^x+e^{-x}}
}
\]

输出范围：

\[
(-1,1)
\]

---

## 30. Tanh 和 Sigmoid 最大区别之一

Sigmoid 输出：

\[
(0,1)
\]

而 Tanh：

\[
(-1,1)
\]

也就是说：

> Tanh 是以 0 为中心的。

这通常比 Sigmoid 作为隐藏层更好一些。

---

## 31. 为什么 Zero-centered 有帮助？

如果激活值全部：

\[
>0
\]

梯度方向有时容易产生不理想的偏移。

而 Tanh 同时有：

> 正值和负值。

优化过程通常更自然。

不过这是优化层面的直觉，不需要现在过度展开。

---

## 32. Tanh 仍然有 Saturation

当：

\[
x\gg0
\]

Tanh：

\[
\to1
\]

当：

\[
x\ll0
\]

Tanh：

\[
\to-1
\]

两端一样：

> 梯度接近 0。

所以它仍然存在：

\[
VanishingGradient
\]

问题。

---

## 33. 然后 ReLU 出现了

ReLU：

\[
\boxed{
ReLU(x)=\max(0,x)
}
\]

导数大致：

\[
ReLU'(x)
=
\begin{cases}
0,&x<0\\
1,&x>0
\end{cases}
\]

在 \(0\) 点严格数学上不可导，但工程中可以选择一个方便的值处理。

---

## 34. ReLU 最大优势是什么？

正区间：

\[
x>0
\]

导数：

\[
1
\]

所以梯度不像 Sigmoid 那样一直被压缩。

这让深层网络：

> 更容易训练。

---

## 35. ReLU 还有计算简单的优点

Sigmoid 需要：

\[
e^{-x}
\]

Tanh 也涉及指数运算。

ReLU：

\[
\max(0,x)
\]

计算非常直接。

在大规模神经网络中：

> 简单操作乘以几十亿次，就很有意义。

---

## 36. ReLU 还会产生稀疏激活

对于：

\[
x<0
\]

输出直接：

\[
0
\]

意味着某些神经元在某些输入上：

> 完全关闭。

这种：

# Sparse Activation

有时会形成有用的表示特性。

---

## 37. 政府采购的直觉例子

假设某个隐藏神经元概念上学习：

> “不合理本地限制信号”。

如果当前条款完全没有这种模式：

\[
z<0
\]

经过 ReLU：

\[
0
\]

这个特征：

> 不向下一层继续贡献。

如果相关信号明显：

\[
z=2.3
\]

则：

\[
ReLU(z)=2.3
\]

继续传递。

---

## 38. 但是 ReLU 也有问题

最经典：

# Dying ReLU

“死亡 ReLU”。

如果某个神经元长期：

\[
z<0
\]

那么：

\[
ReLU(z)=0
\]

而梯度：

\[
0
\]

它可能以后：

> 很难再被训练回来。

---

## 39. 为什么神经元会“死”？

假设一次参数更新太激进：

\[
b
\]

变得非常负。

于是无论输入怎样：

\[
Wx+b<0
\]

那么这个神经元永远：

\[
0
\]

梯度也：

\[
0
\]

所以它基本停止学习。

---

## 40. 这和 Learning Rate 也有关系

如果：

\[
LearningRate
\]

过大，

参数更新幅度太猛，

某些 ReLU 神经元更容易跑入：

> 长期负区间。

这再次说明：

\[
\boxed{
Activation
和
Optimization
不是完全独立的
}
\]

---

## 41. 为了解决 Dying ReLU，出现了 Leaky ReLU

公式：

\[
LeakyReLU(x)
=
\begin{cases}
x,&x>0\\
\alpha x,&x\le0
\end{cases}
\]

例如：

\[
\alpha=0.01
\]

---

## 42. 为什么有用？

负区间不再完全：

\[
0
\]

而是：

\[
0.01x
\]

所以梯度仍然有：

\[
0.01
\]

神经元不容易彻底“死亡”。

---

## 43. 还有 ELU、SELU 等大量变体

你以后会遇到很多 Activation：

\[
ELU
\]

\[
SELU
\]

\[
Softplus
\]

\[
Mish
\]

等等。

现在不要陷入：

> “到底哪个最好？”

真正需要掌握的是：

> 它们都在权衡非线性形状、梯度传播、计算成本和数值稳定性。

---

## 44. 进入现代 Transformer 常见的 GELU

公式的一种定义：

\[
\boxed{
GELU(x)
=
x\Phi(x)
}
\]

其中：

\[
\Phi(x)
\]

是标准正态分布的累积分布函数。

---

## 45. GELU 的直觉是什么？

ReLU 是硬切：

\[
x<0\Rightarrow0
\]

GELU 更像：

> 平滑地决定保留多少输入。

例如略微负的值：

> 不一定完全砍掉。

较大的正值：

> 基本保留。

所以它比 ReLU：

> 更平滑。

---

## 46. GELU 可以粗略理解成“软门”

ReLU：

```text
负值 → 直接关掉
正值 → 直接通过
```

GELU：

```text
负很多 → 大多压掉
接近0 → 部分通过
正很多 → 大多保留
```

它更像：

\[
\boxed{
Soft\ Gating
}
\]

---

## 47. 为什么 Transformer 喜欢 GELU？

早期 Transformer 系列大量采用 GELU，因为它：

> 平滑、可微，并且在深层网络中表现很好。

后来的许多架构也使用其它函数。

所以不要形成：

> “Transformer = GELU”

这种绝对印象。

架构会变化。

---

## 48. 另一个现代常见函数：SiLU

SiLU：

\[
\boxed{
SiLU(x)
=
x\sigma(x)
}
\]

也常叫：

# Swish

---

## 49. SiLU 长什么样？

它和 ReLU 类似：

> 正值大部分保留。

但负值：

> 不会全部变成 0。

而会留下小的负输出。

同时整体：

> 很平滑。

---

## 50. 为什么 LLM 里经常看到 SiLU？

现代很多 Transformer/LLM 架构会使用：

\[
SiLU
\]

尤其配合：

# GLU

或：

# SwiGLU

等门控 Feed Forward 结构。

以后学 Transformer FFN 时，我们会重新碰到它。

---

## 51. 先预告一下 SwiGLU

以后可能看到：

\[
\boxed{
SwiGLU(x)
=
SiLU(xW_1)
\odot
(xW_2)
}
\]

这里：

\[
\odot
\]

代表逐元素乘法。

现在不用记。

只需要知道：

> Activation 后来不仅仅是“一个函数夹在两层 Linear 中间”，还可以参与更复杂的门控机制。

---

## 52. Activation 和“开关”有什么关系？

很多激活函数都可以理解成：

> 根据当前输入，决定某些表示应该被保留多少。

例如 ReLU：

\[
z<0
\]

完全关闭。

GELU / SiLU：

> 更柔和地调节。

所以：

\[
\boxed{
Activation
=
Feature\ Gating\ Mechanism
}
\]

也是一个很有用的直觉。

---

## 53. 但不要误解成“一神经元一个规则”

例如一个神经元高激活：

> 不一定就明确等于“本地限制”。

真实深度网络中：

> 一个概念往往分布在多个神经元和维度之间。

同时一个神经元也可能参与：

> 多个概念。

这叫：

\[
DistributedRepresentation
\]

---

## 54. 为什么多个简单非线性可以产生复杂能力？

这是深度学习最迷人的地方之一。

单个 ReLU：

> 非常简单。

但成千上万个 ReLU：

> 在不同方向、不同阈值上切割空间。

再叠很多层：

> 就可以组合成非常复杂的函数。

---

## 55. 可以把它想成“折纸”

原始输入空间：

> 很难用一条线分开。

第一层：

> 折一次。

第二层：

> 再折。

第三层：

> 再重新组合。

最终：

> 原本复杂交错的数据，在新表示空间里可能变得容易分开。

这只是直觉比喻，但非常有用。

---

## 56. 第四个核心心智模型

### 心智模型 ④：深度网络不是在原始空间硬画一条复杂线，而是在不断改变“表示空间”

我们最终不是简单：

\[
X\rightarrow Y
\]

而是：

\[
X
\rightarrow
H_1
\rightarrow
H_2
\rightarrow
H_3
\rightarrow
Y
\]

每一个：

\[
H_i
\]

都是新的 Representation。

---

## 57. 政府采购例子：第一层可能学什么？

假设原始表示包含大量语言特征。

第一层概念上可能形成：

> 地域词、金额词、资格词、时间词、资质词等局部表示。

第二层可能组合成：

> 注册地约束、规模门槛、成立年限、业绩限制。

更深层再组合：

> 资格限制是否与履约能力存在合理关联。

这是帮助理解的概念模型，不代表真实神经元会严格一一对应这些标签。

---

## 58. 这正是 Deep 的含义

Deep Learning 的“深”不仅仅表示：

> 层数很多。

更重要的是：

\[
\boxed{
Hierarchical\ Function\ Composition
}
\]

即：

> 简单函数不断组合成复杂函数。

---

## 59. 一个形式化表达

假设网络有三层：

\[
h_1=f_1(W_1X+b_1)
\]

\[
h_2=f_2(W_2h_1+b_2)
\]

\[
y=f_3(W_3h_2+b_3)
\]

完整就是：

\[
\boxed{
y
=
f_3(
W_3
f_2(
W_2
f_1(W_1X+b_1)
+b_2)
+b_3)
}
\]

这已经不可能简单合并成一个：

\[
WX+b
\]

因为中间存在非线性：

\[
f_1,f_2
\]

---

## 60. 这就是非线性存在的数学意义

没有：

\[
f
\]

整个式子：

> 可以合并。

有：

\[
f
\]

就不能简单合并。

因此网络真正有机会：

> 表示复杂函数。

---

## 61. 一个容易犯的错误：Activation 越复杂越好吗？

不是。

一个 Activation 的函数式看起来很高级：

> 不代表模型就更强。

实际性能取决于：

\[
Architecture
+
Initialization
+
Normalization
+
Optimizer
+
Data
+
Activation
\]

共同作用。

所以专家不会只因为：

> 某个函数数学更复杂

就认为它更好。

---

## 62. Activation 选择还和任务位置有关

例如：

# Hidden Layer

常用：

\[
ReLU/GELU/SiLU
\]

而：

# Binary Output

可能使用：

\[
Sigmoid
\]

多分类：

> 通常最终处理会涉及 Softmax。

也就是说：

\[
\boxed{
同一个网络不同位置，
Activation 的职责可能不同
}
\]

---

## 63. Hidden Activation 和 Output Activation 不要混淆

Hidden Activation 的主要任务：

> 引入非线性、塑造表示。

Output Activation 的主要任务：

> 把最后的模型分数映射成任务需要的输出形式。

例如二分类：

\[
z
\rightarrow
Sigmoid
\rightarrow
p
\]

---

## 64. Softmax 也是 Activation 吗？

广义上可以把它看作一种输出变换。

公式：

\[
\boxed{
Softmax(z_i)
=
\frac{e^{z_i}}
{\sum_j e^{z_j}}
}
\]

把一组 logits 转成：

\[
0\sim1
\]

并且：

\[
\sum_i p_i=1
\]

---

## 65. 政府采购多分类例子

假设输出风险类型：

\[
z=
[
2.1,
0.4,
-0.2
]
\]

分别对应：

\[
资格风险
\]

\[
技术参数风险
\]

\[
评分标准风险
\]

经过 Softmax 后：

> 可以得到三个类别的相对概率分布。

后面讲分类输出时会深入。

---

## 66. Activation 对数值范围也有影响

Sigmoid：

\[
(0,1)
\]

Tanh：

\[
(-1,1)
\]

ReLU：

\[
[0,\infty)
\]

不同输出范围：

> 会影响下一层接收到的数据分布。

这又与：

# Initialization

和：

# Normalization

紧密相关。

---

## 67. 为什么后面要学 Normalization？

假设网络越深：

> 激活值越来越大或越来越不稳定。

会影响：

- 梯度；
- 数值稳定性；
- 优化速度。

所以现代深度网络里会使用：

\[
LayerNorm
\]

等技术。

Transformer 尤其离不开 LayerNorm / RMSNorm。

---

## 68. Activation 和初始化为什么有关？

假设 ReLU 前的：

\[
z
\]

全部特别负。

那么：

> 大量神经元直接变 0。

如果全部特别正且特别大：

> 激活分布也可能不理想。

所以参数初始值不能乱来。

以后会学：

# Xavier Initialization

和：

# He Initialization

---

## 69. He Initialization 为什么和 ReLU 有关系？

它的设计目标之一就是：

> 在经过 ReLU 的深网络中，更好地保持激活与梯度尺度。

这进一步说明：

\[
\boxed{
Activation
不是孤立组件
}
\]

它和：

> 初始化、归一化、梯度、深度

共同形成一个系统。

---

## 70. 第五个核心心智模型

### 心智模型 ⑤：现代神经网络不是“挑一个最强 Activation”，而是让 Activation 与整个架构匹配

真正的问题不是：

> ReLU、GELU、SiLU 谁天下第一？

而是：

\[
\boxed{
这个Activation
是否适合当前网络结构和优化环境？
}
\]

---

## 71. 回到最核心问题：为什么一个简单 ReLU 能有巨大作用？

因为我们需要的不是：

> 单个 Activation 自己非常聪明。

而是：

> 它让许多线性层之间无法再坍缩。

于是：

\[
Linear
+
ReLU
+
Linear
+
ReLU
+\cdots
\]

拥有越来越丰富的表达空间。

---

## 72. 一个政府采购直觉模型

假设第一层有三个神经元。

Neuron A：

\[
a_1=ReLU(z_1)
\]

概念上响应：

> 地域限制信号。

Neuron B：

\[
a_2=ReLU(z_2)
\]

响应：

> 资格门槛信号。

Neuron C：

\[
a_3=ReLU(z_3)
\]

响应：

> 必要性说明信号。

下一层再学习：

\[
h
=
ReLU(
w_1a_1
+
w_2a_2
-
w_3a_3
+b)
\]

于是：

> 原本几个简单特征开始组合成更复杂概念。

---

## 73. 如果“必要性说明”很强会怎样？

假设：

\[
a_1=2.0
\]

\[
a_2=1.8
\]

但：

\[
a_3=3.0
\]

如果：

\[
w_3
\]

是较大的负权重，

下一层可能：

> 大幅降低风险信号。

这就体现：

\[
\boxed{
Context-dependent\ Interaction
}
\]

上下文组合关系。

---

## 74. 这比关键词模型高级在哪里？

关键词模型：

```text
看到“本地”
→ 风险
```

深度网络希望学：

```text
本地相关语义
+
约束对象
+
履约要求
+
必要性
+
竞争影响
↓
综合表示
```

然后再判断。

这就是：

> 表示学习 + 非线性组合。

---

## 75. 当然，神经网络不保证一定学到正确抽象

第一课第 12 阶段已经学过：

\[
SpuriousCorrelation
\]

神经网络也可能学：

> “本市”关键词捷径。

Activation 提高的是：

\[
ExpressiveCapacity
\]

并不自动保证：

\[
CorrectReasoning
\]

---

## 76. 能力更强，也意味着更容易过拟合

一个线性模型表达能力有限。

深层非线性网络：

> 可以表示极其复杂的规律。

优点：

> 能学真实复杂关系。

风险：

> 也能学训练数据里的噪声和捷径。

这重新连接第一课：

\[
Capacity
\leftrightarrow
Overfitting
\]

---

## 77. 所以“更复杂”不是无条件更好

如果数据：

> 很少、标签很差、覆盖不足，

给一个巨大非线性网络：

> 可能只是让它更容易拟合错误规律。

因此仍然要回到第一课：

\[
Data
+
Generalization
+
Evaluation
\]

---

## 78. 现在理解 Universal Approximation 的直觉

神经网络有一个很著名的理论方向：

# Universal Approximation

粗略来说：

> 在一定条件下，带非线性激活的神经网络可以逼近非常广泛的一类函数。

现在不用学严格定理。

核心直觉是：

\[
\boxed{
Linear + Nonlinear
}
\]

不断组合，

具有非常强的函数表示能力。

---

## 79. 但“能表示”不等于“能学到”

这一点极其重要。

理论上某个网络：

> 可以表达目标函数。

不意味着：

> 梯度下降一定能找到它。

所以有两个问题：

\[
Representation\ Capacity
\]

和：

\[
Optimization
\]

必须分开。

---

## 80. 一个网络可能“有能力但不会学”

例如模型结构足够强，

但：

- Learning Rate 不合适；
- 梯度消失；
- 初始化差；
- 数据不足；
- Loss 不匹配。

结果仍然很差。

所以：

\[
\boxed{
Can\ Represent
\neq
Can\ Train
}
\]

---

## 81. 这就是为什么 Activation 设计同时考虑梯度

如果只关注表达能力：

> 很多非线性函数都可以。

但真正深度学习里，还要问：

> 梯度是否容易传播？

于是 ReLU、GELU、SiLU 等函数的工程价值开始体现。

---

## 82. 第二课 · 第 2 阶段五个核心心智模型

| 心智模型 | 核心认知 |
|---|---|
| **① Activation 打破线性坍缩** | 没有非线性，再多 Linear Layer 仍等价于一个 Linear Layer |
| **② 非线性让网络重新塑造表示空间** | 网络不断切割、折叠、重新组合输入 |
| **③ Activation 同时影响梯度传播** | 表达能力和可训练性必须一起考虑 |
| **④ Deep 的本质是函数的层级组合** | 简单非线性反复组合可以形成复杂表示 |
| **⑤ Activation 必须和整个架构匹配** | 不存在脱离模型结构的“绝对最佳激活函数” |

如果只记一个公式：

\[
\boxed{
h=f(WX+b)
}
\]

---

## 83. 如果只记一个结论

请记住：

\[
\boxed{
没有Activation，
1000层Linear
和
1层Linear
在表达类型上没有本质区别。
}
\]

而加入：

\[
Nonlinearity
\]

之后：

> 网络才真正开始拥有深度带来的表达能力。

---

## 84. Sigmoid、Tanh、ReLU、GELU、SiLU 怎么暂时记？

可以先建立一个简单地图：

| Activation | 直觉 | 当前最重要认知 |
|---|---|---|
| Sigmoid | 压到 0～1 | 二分类输出常见，但隐藏层容易饱和 |
| Tanh | 压到 -1～1 | Zero-centered，但仍有饱和 |
| ReLU | 负数砍 0 | 简单、梯度友好，但可能 Dying ReLU |
| GELU | 平滑筛选 | Transformer 中经典选择 |
| SiLU | \(x\sigma(x)\) | 现代 LLM/门控 FFN 中常见 |

不用死背细节。

真正需要理解：

> 它们是在“非线性表达”和“梯度行为”之间做不同设计。

---

## 85. 一个数值思维实验

假设：

\[
z=-2
\]

那么：

Sigmoid：

\[
\sigma(-2)\approx0.119
\]

Tanh：

\[
\tanh(-2)\approx-0.964
\]

ReLU：

\[
ReLU(-2)=0
\]

三种 Activation：

> 面对完全相同的输入，

产生完全不同的 Representation。

---

## 86. 再看 \(z=2\)

Sigmoid：

\[
0.881
\]

Tanh：

\[
0.964
\]

ReLU：

\[
2
\]

这说明：

> Activation 不只是“加一个开关”。

它直接决定：

\[
下一层看到什么数字
\]

---

## 87. 下一层为什么在乎这些数字？

下一层做：

\[
z_2=W_2h+b_2
\]

其中：

\[
h
\]

就是上一层 Activation 的输出。

所以：

\[
Activation
\]

改变：

\[
h
\]

就会改变整个后续网络。

---

## 88. 现在把一个两层网络完整写出来

输入：

\[
X
\]

第一层：

\[
z_1=W_1X+b_1
\]

激活：

\[
h=ReLU(z_1)
\]

第二层：

\[
z_2=W_2h+b_2
\]

二分类输出：

\[
p=\sigma(z_2)
\]

完整：

\[
\boxed{
p
=
\sigma(
W_2
ReLU(W_1X+b_1)
+b_2
)
}
\]

这已经是一个真正的小型神经网络了。

---

## 89. 这已经比 Logistic Regression 多了什么？

Logistic Regression：

\[
p=\sigma(WX+b)
\]

小型神经网络：

\[
p
=
\sigma(
W_2ReLU(W_1X+b_1)+b_2
)
\]

关键多出来：

\[
\boxed{
Hidden\ Representation
}
\]

也就是：

\[
h
\]

---

## 90. 这就是下一阶段的主角

下一阶段我们要正式进入：

# Hidden Layer

隐藏层。

我们会真正理解：

\[
InputLayer
\rightarrow
HiddenLayer
\rightarrow
OutputLayer
\]

为什么叫“隐藏”，每一层的维度意味着什么，多个神经元如何一起形成新的 Representation，以及：

\[
\boxed{
Width
}
\]

和：

\[
\boxed{
Depth
}
\]

分别意味着什么。

---

## 91. 第二课 · 第 2 阶段掌握标准

学完这一阶段以后，看到：

\[
h=ReLU(WX+b)
\]

你应该马上知道：

\[
WX+b
\]

负责：

> 线性组合。

而：

\[
ReLU
\]

负责：

> 引入非线性。

看到连续：

\[
Linear
\rightarrow
Linear
\]

应该立即警觉：

> 如果中间没有非线性，它们可以合并。

看到：

\[
Sigmoid
\]

应该想到：

> 0～1、饱和、梯度变小、常用于二分类输出。

看到：

\[
ReLU
\]

应该想到：

> 简单、正区梯度好、负区为 0、可能 Dying ReLU。

看到：

\[
GELU/SiLU
\]

应该知道：

> 它们是现代深层模型常见的平滑非线性。

---

## 92. 最后用一句话把前两阶段串起来

第一阶段告诉我们：

\[
\boxed{
Neuron
=
Weighted\ Sum
}
\]

第二阶段告诉我们：

\[
\boxed{
Neural\ Network
真正开始变强
=
Weighted\ Sum
+
Nonlinearity
}
\]

也就是：

\[
\boxed{
h=f(WX+b)
}
\]

这一个公式，从今天开始会一直陪我们走到 Transformer。

---

下一阶段就是 **第二课 · 第 3 阶段：Hidden Layer 与 Representation——为什么一层神经元只能学简单模式，多层网络却能逐层形成“资格限制 → 竞争影响 → 合规风险”这样的抽象概念。**

那一阶段我们会第一次完整搭出：

\[
\boxed{
Input
\rightarrow
Hidden_1
\rightarrow
Hidden_2
\rightarrow
Output
}
\]

并开始真正理解 **Width、Depth、Hidden Dimension、Parameter Count，以及“模型内部表征”究竟是什么。**

---
