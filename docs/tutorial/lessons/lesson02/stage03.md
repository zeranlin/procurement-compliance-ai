# 第二课 · 第 3 阶段：Hidden Layer 与 Representation——为什么多层网络能逐步形成更抽象的“内部表示”

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Hidden Layer ≠ Human Rule Table。隐藏层不是一张可直接阅读的专家规则表。**
2. **Representation 是分布式的：一个业务概念通常由很多维度共同编码，而不是对应某一个神经元。**
3. **Depth 的价值来自多层函数复合，让模型逐步把表面输入转换成更抽象的内部特征。**
4. **更深 ≠ 自动更好；只有在优化稳定、数据足够、架构合理时，深度才可能转化为能力。**
5. **“模型内部形成了某种表示”是需要通过探针、消融和行为实验验证的工程判断，不能只凭直觉解释。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Representation` | 表示：模型内部承载语义或特征的向量结构 |
| `Hidden Layer` | 隐藏层：逐层形成内部表示的中间网络层 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `State` | 状态：保存任务进度、事实和待办 |
| `Input` | 输入：模型在当前任务中允许看到的条件信息 |
| `Transformer` | Transformer：以注意力和前馈网络为核心的序列架构 |
| `Neuron` | 神经元：加权、偏置和非线性变换的最小计算单元 |
| `Loss` | 损失函数：把预测错误压缩成可优化的数值信号 |
| `Embedding` | 嵌入：把离散 Token 映射到连续高维向量 |
| `Attention` | 注意力：根据内容相关性动态聚合信息 |
| `Backpropagation` | 反向传播：把最终损失沿计算图反向分配到参数 |
| `Token` | Token：模型实际处理的离散文本单元 |

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

前两阶段我们已经拿到了两个最核心的零件：

\[
\boxed{
z=WX+b
}
\]

和：

\[
\boxed{
h=f(WX+b)
}
\]

第 1 阶段告诉我们：

> 神经元负责对信息进行加权组合。

第 2 阶段告诉我们：

> Activation 负责打破线性，让网络能够表达复杂关系。

现在第 3 阶段要回答一个更关键的问题：

> **为什么要把很多神经元组成 Hidden Layer？为什么多个 Hidden Layer 叠起来以后，模型会逐渐形成越来越抽象的表示？**

这一阶段的主线是：

\[
\boxed{
Input
\rightarrow
Hidden\ Representation
\rightarrow
Hidden\ Representation
\rightarrow
Output
}
\]

以及五个核心概念：

\[
\boxed{
Hidden\ Layer
+
Width
+
Depth
+
Hidden\ Dimension
+
Representation
}
\]

---

## 1. 先把第二课路线重新定位

我们现在已经走到：

\[
Neuron
\rightarrow
Activation
\rightarrow
\boxed{Hidden\ Layer}
\rightarrow
Deep\ Network
\rightarrow
Backpropagation
\]

前两阶段学的是：

> 单个计算单元。

从今天开始，我们第一次真正搭出：

# Neural Network

神经网络。

---

## 2. 最简单的完整神经网络长什么样？

假设：

\[
X
\]

是输入。

第一层：

\[
z_1=W_1X+b_1
\]

激活：

\[
h_1=f(z_1)
\]

然后输出层：

\[
z_2=W_2h_1+b_2
\]

最后：

\[
\hat Y=g(z_2)
\]

所以：

\[
\boxed{
X
\rightarrow
Hidden
\rightarrow
Output
}
\]

---

## 3. 为什么中间叫 Hidden Layer？

因为训练数据只直接给我们：

\[
X
\]

和：

\[
Y
\]

例如：

```text
输入：
供应商须在项目所在地设立分公司

标签：
风险
```

但是中间：

\[
h
\]

应该是什么，

数据并没有直接告诉我们。

模型自己学习。

所以叫：

# Hidden

隐藏。

---

## 4. 换句话说

我们知道：

\[
X
\]

也知道：

\[
Y
\]

但不知道中间应该经过：

> 哪些概念、哪些特征、哪些表示。

模型自动构造：

\[
H
\]

所以：

\[
\boxed{
Hidden\ Layer
=
模型自己学习出来的中间表示空间
}
\]

这是这一阶段最重要的一句话之一。

---

## 5. 一个政府采购例子

原始输入：

> “供应商必须在项目所在地注册并持续经营三年以上。”

我们最终想判断：

\[
Risk / NoRisk
\]

但真正专家可能隐含地经历：

```text
原始文字
↓
识别“注册地要求”
↓
识别“成立年限要求”
↓
判断是否属于供应商资格门槛
↓
判断是否与履约能力有关
↓
判断是否限制竞争
↓
风险结论
```

传统系统可能要人工写出全部中间规则。

神经网络希望：

> 自己学习有用的中间表示。

---

## 6. 第一个核心心智模型

### 心智模型 ①：Hidden Layer 的作用不是“多算几遍”，而是创造新的表示

第一层看到：

\[
X
\]

然后生成：

\[
H_1
\]

第二层不是继续看原始 X，

而是在处理：

\[
H_1
\]

生成：

\[
H_2
\]

因此：

\[
\boxed{
每一层都在重新描述输入
}
\]

---

## 7. Representation 到底是什么？

这个词以后会不断出现。

# Representation

表示。

简单说：

> **同一个对象，用一组数字表达出来。**

例如一个采购条款：

> “供应商须在本市设立分公司。”

最原始表示可以是：

```text
字符串
```

也可以被人工表示成：

\[
[1,0,1,0]
\]

也可以被深度模型表示成：

\[
[0.27,-1.18,2.04,0.51,\ldots]
\]

这些都是不同：

\[
Representation
\]

---

## 8. 好的 Representation 有什么特点？

它应该把：

> 对任务有用的信息

变得容易利用。

例如风险分类需要：

- 是否限制注册地；
- 是否限制企业成立时间；
- 是否有履约必要性；
- 是否影响竞争。

而可能不太需要：

> 文件页码是 17 还是 18。

一个好表示应该：

\[
\boxed{
保留任务相关信息
+
弱化任务无关信息
}
\]

---

## 9. 这是深度学习真正强大的地方之一

传统机器学习经常：

> 人工设计 Feature。

例如：

```text
x1 = 是否包含“注册资本”
x2 = 是否包含“本市”
x3 = 是否包含“成立年限”
```

这叫：

# Feature Engineering

特征工程。

深度学习则试图：

\[
\boxed{
Learn\ the\ Features
}
\]

自己学习 Feature。

---

## 10. 所以“深度学习”不只是更大的分类器

它真正改变的是：

\[
\boxed{
Feature\ Engineering
\rightarrow
Representation\ Learning
}
\]

过去：

> 人类告诉模型什么特征有意义。

现在：

> 模型自己学习哪些中间表示更有助于降低 Loss。

---

## 11. 一个 Hidden Layer 里面有什么？

假设：

\[
X\in\mathbb{R}^3
\]

意思是输入有：

\[
3
\]

个数字。

Hidden Layer 有：

\[
4
\]

个神经元。

那么：

\[
H\in\mathbb{R}^4
\]

也就是说：

> 原来的 3 维表示，被转换成 4 维新表示。

---

## 12. 图形表示

```text
Input Layer        Hidden Layer

x1 ───────────────→ h1
  \               ↗
   \─────────────→ h2
   /              ↘
x2 ───────────────→ h3
   \              ↗
x3 ───────────────→ h4
```

通常是：

> 每一个 Hidden Neuron 都能读取上一层全部输入。

这叫：

# Fully Connected Layer

全连接层。

---

## 13. 数学上怎么写？

输入：

\[
X=
\begin{bmatrix}
x_1\\
x_2\\
x_3
\end{bmatrix}
\]

第一层：

\[
W_1
\]

需要把：

\[
3维
\]

变成：

\[
4维
\]

所以：

\[
W_1
\]

可以是：

\[
4\times3
\]

矩阵。

---

## 14. 写出来就是

\[
W_1=
\begin{bmatrix}
w_{11}&w_{12}&w_{13}\\
w_{21}&w_{22}&w_{23}\\
w_{31}&w_{32}&w_{33}\\
w_{41}&w_{42}&w_{43}
\end{bmatrix}
\]

Bias：

\[
b_1=
\begin{bmatrix}
b_1\\
b_2\\
b_3\\
b_4
\end{bmatrix}
\]

于是：

\[
\boxed{
H=f(W_1X+b_1)
}
\]

---

## 15. 为什么 \(W\) 有这么多数字？

因为每一个 Hidden Neuron：

> 都需要决定上一层每个输入对自己的影响。

例如：

Neuron 1：

\[
h_1=f(w_{11}x_1+w_{12}x_2+w_{13}x_3+b_1)
\]

Neuron 2：

\[
h_2=f(w_{21}x_1+w_{22}x_2+w_{23}x_3+b_2)
\]

……

每一个神经元都有不同：

\[
W
\]

所以能观察输入的不同方向。

---

## 16. 一个直觉政府采购例子

假设输入：

\[
X=
[
x_1,
x_2,
x_3
]
\]

分别是：

```text
x1 = 地域限制信号
x2 = 资格门槛信号
x3 = 必要性说明信号
```

第一层可能概念上形成：

```text
h1 = 本地资格限制程度
h2 = 履约门槛强度
h3 = 条件合理性
h4 = 潜在竞争影响
```

注意：

> 这只是为了帮助理解。

真实神经网络不会自动给神经元贴这些中文标签。

---

## 17. 一个重要警告

不要认为：

\[
h_1
\]

一定就是：

> “本地限制”。

真实模型内部往往是：

# Distributed Representation

即：

> 一个概念分布在多个维度里。

同时：

> 一个维度也可能参与表示多个概念。

因此：

\[
\boxed{
Neuron\neq HumanConcept
}
\]

---

## 18. 那为什么还用“某个神经元检测某种模式”的比喻？

因为它有助于建立第一层直觉。

但更准确地说：

> 一个概念通常是隐藏向量中的某种方向、模式或组合。

例如：

\[
H=[h_1,h_2,\ldots,h_{768}]
\]

某种“竞争限制”概念，

可能不是单独一个：

\[
h_{37}
\]

而是：

\[
h_3,h_{17},h_{88},h_{201},\ldots
\]

共同编码。

---

## 19. 第二个核心心智模型

### 心智模型 ②：模型内部的“概念”更像向量空间里的方向，而不是一个个独立开关

这对以后理解：

\[
Embedding
\]

\[
Attention
\]

\[
Transformer\ Hidden\ State
\]

非常重要。

模型世界的基本单位往往不是：

> 人类可读标签。

而是：

\[
\boxed{
Vector
}
\]

---

## 20. 什么叫 Hidden Dimension？

假设：

\[
H\in\mathbb{R}^{768}
\]

那么：

\[
768
\]

就可以叫：

# Hidden Dimension

隐藏维度。

也可以看到：

- hidden size
- model dimension
- embedding dimension

这些词在不同架构里含义略有差异，但核心直觉都和：

> 向量有多少个数字

相关。

---

## 21. 举例

如果：

\[
H=
[h_1,h_2,\ldots,h_{768}]
\]

那么一条数据经过这层以后：

> 用 768 个数字表示。

也就是说：

\[
\boxed{
HiddenSize=768
}
\]

---

## 22. 为什么需要这么多维？

因为现实概念非常复杂。

一句采购条款可能同时涉及：

- 资格；
- 行业；
- 时间；
- 金额；
- 地域；
- 技术；
- 条件关系；
- 否定；
- 例外；
- 必要性；
- 因果；
- 风险。

如果表示空间只有：

\[
2维
\]

很难同时编码这么多结构。

---

## 23. 但维度越大越好吗？

不一定。

更大的 Hidden Dimension：

> 提供更大表达空间。

但也会带来：

- 更多参数；
- 更多计算；
- 更多显存；
- 更高过拟合可能；
- 更多数据需求。

所以仍然是：

\[
\boxed{
Capacity\ vs\ Cost
}
\]

---

## 24. 参数数量怎么计算？

假设：

```python
Linear(3, 4)
```

权重：

\[
3\times4=12
\]

Bias：

\[
4
\]

总参数：

\[
\boxed{
16
}
\]

---

## 25. 通用公式

对于：

```python
Linear(d_{in},d_{out})
```

参数：

\[
W\in
\mathbb{R}^{d_{out}\times d_{in}}
\]

所以：

\[
\#W=d_{in}d_{out}
\]

Bias：

\[
\#b=d_{out}
\]

总参数：

\[
\boxed{
d_{in}d_{out}+d_{out}
}
\]

---

## 26. 一个更大的例子

```python
Linear(768,3072)
```

权重：

\[
768\times3072
=
2,359,296
\]

Bias：

\[
3,072
\]

总计：

\[
\boxed{
2,362,368
}
\]

超过：

> 236 万个参数。

---

## 27. 如果再接回来

Transformer FFN 里经常有类似：

\[
768
\rightarrow
3072
\rightarrow
768
\]

那么两个 Linear：

第一层约：

\[
2.36M
\]

第二层约：

\[
2.36M
\]

合起来：

\[
\approx4.72M
\]

仅仅一个这样的模块：

> 就已经有数百万参数。

---

## 28. 这开始解释大模型参数从哪里来

不是因为：

> 模型里有几十亿条 IF 规则。

而是因为：

> 大量高维空间之间存在巨大的权重矩阵。

例如：

\[
4096\times11008
\]

这种矩阵本身就有：

\[
45M+
\]

参数。

---

## 29. 什么叫 Width？

# Width

宽度。

通常指：

> 一层有多少个神经元 / Hidden Dimension 多大。

例如：

```text
Hidden Layer 1：64
Hidden Layer 2：64
```

网络宽度大约：

\[
64
\]

---

## 30. 什么叫 Depth？

# Depth

深度。

通常指：

> 网络有多少层参数化变换。

例如：

```text
Input
↓
Hidden 1
↓
Hidden 2
↓
Hidden 3
↓
Output
```

比只有一个 Hidden Layer：

> 更深。

---

## 31. Width 和 Depth 是两个不同的 Capacity 方向

可以：

### 变宽

\[
64
\rightarrow
1024
\]

一层里面容纳更多表示方向。

也可以：

### 变深

\[
2层
\rightarrow
32层
\]

进行更多层级组合。

---

## 32. 第三个核心心智模型

### 心智模型 ③：Width 决定“这一层能同时表示多少”，Depth 决定“能进行多少级组合”

可以粗略理解：

\[
\boxed{
Width
\approx
Representation\ Capacity
}
\]

\[
\boxed{
Depth
\approx
Composition\ Capacity
}
\]

这不是严格数学等式，

但作为学习直觉很好用。

---

## 33. 政府采购例子：变宽

假设只有：

\[
2
\]

个 Hidden Neurons。

可能很难同时表示：

- 地域要求；
- 成立年限；
- 注册资本；
- 业绩；
- 资质；
- 服务能力；
- 市场竞争；
- 必要性。

如果增加到：

\[
128
\]

维，

模型有更多内部“方向”可以利用。

---

## 34. 政府采购例子：变深

第一层可能识别：

> 基础语言模式。

第二层组合成：

> 条件类型。

第三层：

> 条件与项目需求的关系。

第四层：

> 对竞争的影响。

第五层：

> 合规风险。

这就是：

\[
\boxed{
Hierarchical\ Composition
}
\]

---

## 35. 为什么深度特别适合层级结构？

因为现实很多规律本来就有层级。

例如：

```text
字符
↓
词
↓
短语
↓
句子关系
↓
条款含义
↓
文件结构
↓
法律/业务判断
```

每一级都可以建立在：

> 前一级抽象的基础上。

---

## 36. 这就是 Feature Hierarchy

# 特征层级

图像里可能：

```text
边缘
↓
纹理
↓
形状
↓
物体
```

文本里可能：

```text
Token
↓
局部语义
↓
句法关系
↓
语义关系
↓
高层概念
```

政府采购：

```text
词语
↓
资格条件
↓
条件目的
↓
履约关联性
↓
竞争影响
↓
风险判断
```

---

## 37. 但真实模型内部是不是一定按这个顺序？

不是。

这是一个：

> 概念模型。

真实大型网络中的表示：

- 会重叠；
- 会复用；
- 会跨层；
- 会分布；
- 会出现复杂 superposition。

所以我们用它帮助理解：

> “为什么层级表示有价值”。

而不是宣称：

> 第 17 层一定负责必要性。

---

## 38. 什么是 Feature Reuse？

一个底层模式可能被多个高级任务共享。

例如模型识别：

> “不得低于”

这个比较/约束语义。

它既可能参与：

- 注册资本限制；
- 业绩数量限制；
- 人员数量限制；
- 营收限制。

所以底层 Feature：

> 可以被多个高级概念重复使用。

---

## 39. 这就是神经网络很高效的一点

不用为：

```text
注册资本不得低于5000万
```

学一套完全独立规则。

再为：

```text
年营业额不得低于1亿元
```

学另一套完全独立规则。

可以先学习：

\[
\boxed{
Numerical\ LowerBound\ Restriction
}
\]

类似的抽象模式，

再和不同对象组合。

---

## 40. 这就是 Compositionality

# 组合性

模型可以把简单 Feature：

\[
A,B,C
\]

组合成：

\[
AB
\]

再组合：

\[
ABC
\]

最终形成复杂表示。

这就是深度网络的重要能力来源。

---

## 41. 一个政府采购组合例子

底层：

```text
A = 地域实体
B = 必须
C = 注册
```

组合：

```text
A + B + C
↓
本地注册限制
```

然后：

```text
本地注册限制
+
采购项目需求
+
市场竞争情况
↓
竞争限制风险
```

再：

```text
竞争限制风险
+
法规依据
↓
合规判断
```

---

## 42. Hidden Layer 其实在做“重新编码”

原始：

\[
X
\]

可能不容易分类。

通过：

\[
H=f(WX+b)
\]

我们把输入重新编码成：

\[
H
\]

在新的空间里：

> 某些原本难分的样本可能变得容易分。

---

## 43. 可以把它想成换坐标系

原始空间：

```text
● ○ ● ○
○ ● ○ ●
```

非常交错。

模型通过 Hidden Layers：

> 不断改变坐标表达。

最终新空间：

```text
● ● ●     ○ ○ ○
```

然后输出层：

> 一条简单直线就能分开。

---

## 44. 这是 Representation Learning 的一个核心直觉

最终分类层可能非常简单：

\[
Linear
\]

真正困难的事情：

> 已经由前面几十层把数据变成“容易分类”的表示。

所以：

\[
\boxed{
Deep\ Network
的很多工作
=
让问题在新空间里变简单
}
\]

---

## 45. 第四个核心心智模型

### 心智模型 ④：深度网络不是直接寻找复杂答案，而是在寻找“让答案变简单的表示”

这句话非常值得记住。

例如最终风险分类：

\[
Risk / NoRisk
\]

可能只是：

> 最后一层 Linear。

真正强大的地方是：

\[
H_{final}
\]

已经把：

> 资格、必要性、竞争影响等信息编码好了。

---

## 46. Hidden Layer 的输出叫什么？

经常会看到：

- hidden state
- activation
- feature vector
- latent representation
- embedding

这些词不是永远完全等价，

但很多时候都在讨论：

> 中间数字表示。

---

## 47. 什么叫 Latent？

# Latent

潜在的、隐藏的。

例如我们没有直接标注：

> “竞争限制程度 = 0.83”。

但模型内部可能形成某种方向：

> 对这一概念敏感。

所以：

\[
LatentRepresentation
\]

指：

> 模型自己学出的潜在表示。

---

## 48. 为什么 Latent Representation 很有价值？

因为很多重要概念：

> 数据中根本没有直接标签。

例如：

- 条款强制程度；
- 业务必要性；
- 风格；
- 相似性；
- 语义主题。

模型可能通过其它任务的 Loss：

> 间接形成这些内部结构。

---

## 49. 一个关键问题：没有标注中间概念，模型为什么会学出来？

因为这些中间概念如果：

> 有助于预测最终 Y，

那么形成这种表示：

> 可以降低 Loss。

所以训练会推动参数：

\[
W
\]

形成有利于任务的内部结构。

---

## 50. 但它不一定形成我们想要的概念

这又回到第一课。

模型可能发现：

> 机构名称

比真正的法律逻辑更容易降低 Loss。

于是隐藏表示里可能强烈编码：

> 机构身份。

而不是：

> 业务机制。

所以：

\[
\boxed{
Representation\ Learning
不保证
Representation\ Correctness
}
\]

---

## 51. 怎样让 Representation 更接近我们想要的规律？

依然靠：

- 数据多样性；
- Hard Negative；
- 对比样本；
- 多环境数据；
- 辅助任务；
- 专家标签；
- 评测；
- 反事实测试。

你会发现：

> 第一课的内容没有消失。

它开始指导第二课的内部模型理解。

---

## 52. Multi-task Learning 可以帮助表示学习

假设模型不仅预测：

\[
Risk
\]

还同时预测：

- 风险类型；
- 条件目的；
- 是否有履约关联；
- 是否存在竞争影响。

那么 Hidden Representation 必须同时服务多个任务。

可能更容易学出：

> 更有业务意义的表示。

---

## 53. 这就是 Auxiliary Task

辅助任务。

主任务：

\[
Risk
\]

辅助任务：

\[
RiskType
\]

\[
Relevance
\]

\[
Necessity
\]

等。

它们可以共同塑造：

\[
H
\]

---

## 54. 这和我们第一课第 12 阶段的结构化标签接上了

当时我们设计：

```text
Condition
↓
Business Purpose
↓
Relevance
↓
Necessity
↓
Competitive Effect
↓
Risk
```

现在你可以理解：

> 这些中间监督信号可能帮助网络形成更好的 Hidden Representation。

---

## 55. Hidden Layer 的宽度是不是概念数量？

不是。

如果：

\[
HiddenSize=768
\]

不代表：

> 模型最多只能理解 768 个概念。

真实表示空间远比：

> 一维一个概念

复杂。

不同方向组合可以表示大量模式。

---

## 56. 一个向量空间可以有很多方向

二维平面只有两个坐标轴：

\[
x,y
\]

但可以有无限多个方向：

- 0°
- 30°
- 45°
- 77°
- …

所以：

\[
768维
\]

的表示空间可以拥有极其丰富的方向结构。

---

## 57. 这也是“概念方向”为什么比“概念神经元”更准确

某个概念可以表示为：

\[
v_{concept}
\]

模型 Hidden State：

\[
h
\]

如果：

\[
h
\]

在这个方向投影较大：

> 可能意味着该概念比较明显。

这会在以后 Embedding、Attention 课程非常重要。

---

## 58. 什么叫 Bottleneck？

假设：

\[
X\in\mathbb{R}^{1000}
\]

突然压缩成：

\[
H\in\mathbb{R}^{5}
\]

这个中间层非常窄。

叫：

# Bottleneck

瓶颈。

---

## 59. Bottleneck 有什么作用？

它强迫模型：

> 用很少的数字总结大量信息。

可能有助于：

- 压缩；
- 学习关键特征；
- 去除噪声。

Autoencoder 就大量利用这种思想。

---

## 60. 但 Bottleneck 太窄会怎样？

重要信息可能丢失。

例如：

\[
1000
\]

维复杂采购文件表示，

强行压成：

\[
2维
\]

很可能无法保留：

- 行业；
- 条件；
- 法规；
- 时间；
- 竞争；
- 必要性。

这就：

# Under-capacity

容量不足。

---

## 61. 反过来太宽呢？

例如：

\[
1000
\rightarrow
100000
\]

参数数量巨大。

可能：

- 计算昂贵；
- 显存高；
- 训练慢；
- 更容易记忆训练数据。

但现代深度学习也经常使用：

# Overparameterization

过参数化。

---

## 62. 什么叫 Overparameterization？

参数数量：

> 远远大于直觉上“解决问题最低需要”的数量。

例如训练样本：

\[
10000
\]

模型参数：

\[
10M
\]

甚至：

\[
1B
\]

仍然可能泛化很好。

这是现代深度学习很有意思的现象。

---

## 63. 为什么参数多不一定必然过拟合？

第一课的传统 Bias/Variance 直觉仍然重要，

但深度学习里还有：

- 优化路径；
- 初始化；
- 正则化；
- 数据规模；
- SGD 隐式偏置；
- 架构结构；

共同影响泛化。

所以：

\[
\boxed{
ParameterCount
\neq
EffectiveComplexity
}
\]

不能机械一一对应。

---

## 64. 但参数多仍然不是免费午餐

更大模型需要：

\[
更多显存
\]

\[
更多算力
\]

\[
更多训练数据
\]

\[
更复杂部署
\]

所以工程上必须问：

> 增加 Width / Depth 带来的收益是否值得？

---

## 65. 参数规模和显存怎么粗略联系？

假设：

\[
1B
\]

个参数。

如果仅用：

\[
FP16
\]

存权重，

每参数约：

\[
2Bytes
\]

仅权重：

\[
\approx2GB
\]

但训练还需要：

- gradients；
- optimizer states；
- activations；

所以实际显存：

> 远大于纯权重。

---

## 66. Hidden Activations 也占显存

很多人以为：

> 显存全被参数吃掉。

实际训练中：

\[
H_1,H_2,\ldots,H_L
\]

为了 Backpropagation：

> 往往需要保留。

所以：

\[
\boxed{
ActivationMemory
}
\]

也是重要显存来源。

---

## 67. 为什么训练比推理更吃显存？

推理：

> 主要做 Forward。

训练：

> Forward 后还要 Backward。

反向传播需要知道：

> 前向过程中很多中间结果。

于是必须保留：

\[
HiddenStates
\]

等数据。

---

## 68. 这会连接未来的 Gradient Checkpointing

如果显存不够：

> 不保存所有 Hidden Activations。

反向时：

> 再重新计算一部分。

这叫：

# Gradient Checkpointing

用：

> 更多计算

换：

> 更少显存。

以后训练 LLM 时非常常见。

---

## 69. 现在理解 Shape

深度学习代码里你会不断看到：

# Shape

形状。

例如：

\[
X.shape=(768,)
\]

表示：

> 一个 768 维向量。

---

## 70. 如果一个 Batch 有 32 条呢？

那么：

\[
X.shape=(32,768)
\]

含义：

```text
32 个样本
×
每个样本 768 维
```

这就是 Batch Dimension。

---

## 71. Linear(768,3072) 后 Shape 怎么变？

输入：

\[
(32,768)
\]

Linear：

\[
768\rightarrow3072
\]

输出：

\[
\boxed{
(32,3072)
}
\]

Batch 仍然：

\[
32
\]

Representation Dimension：

\[
768\rightarrow3072
\]

---

## 72. 这个 Shape 思维极其重要

以后你学 Transformer：

\[
(batch,\ sequence,\ hidden)
\]

例如：

\[
(8,2048,4096)
\]

如果没有 Shape 直觉：

> Attention 很快会变成天书。

所以从现在开始看到任何层：

> 都问输入 Shape、输出 Shape。

---

## 73. 第五个核心心智模型

### 心智模型 ⑤：学习神经网络不能只看公式，还要始终追踪“数据的 Shape 怎么变化”

例如：

```text
Input        (32, 10)
↓ Linear
Hidden       (32, 64)
↓ Linear
Hidden       (32, 128)
↓ Output
Prediction   (32, 1)
```

模型结构本质上也可以看成：

\[
\boxed{
Shape\ Transformation
}
\]

---

## 74. 一个完整三层网络

假设：

\[
X\in\mathbb{R}^{10}
\]

第一层：

```python
Linear(10,32)
```

得到：

\[
H_1\in\mathbb{R}^{32}
\]

第二层：

```python
Linear(32,16)
```

得到：

\[
H_2\in\mathbb{R}^{16}
\]

输出：

```python
Linear(16,1)
```

得到：

\[
z\in\mathbb{R}
\]

---

## 75. 再加 Activation

完整：

\[
H_1=ReLU(W_1X+b_1)
\]

\[
H_2=ReLU(W_2H_1+b_2)
\]

\[
z=W_3H_2+b_3
\]

\[
p=\sigma(z)
\]

这就是：

> 一个真正完整的 MLP。

---

## 76. MLP 是什么？

# Multilayer Perceptron

多层感知机。

典型：

```text
Input
↓
Linear
↓
Activation
↓
Linear
↓
Activation
↓
Linear
↓
Output
```

它是神经网络最基础的架构之一。

---

## 77. 为什么叫 Perceptron？

历史原因来自早期：

# Perceptron

感知机。

现在你可以把 MLP 理解为：

> 多层全连接神经网络。

未来 Transformer 的 Feed Forward Network：

> 也可以看作特殊形式的 MLP。

---

## 78. 一个两层 Hidden MLP 参数怎么算？

架构：

\[
10
\rightarrow
32
\rightarrow
16
\rightarrow
1
\]

第一层：

\[
10\times32+32=352
\]

第二层：

\[
32\times16+16=528
\]

第三层：

\[
16\times1+1=17
\]

总参数：

\[
352+528+17
=
\boxed{
897
}
\]

---

## 79. 参数为什么增长这么快？

因为相邻层是：

\[
d_{in}\times d_{out}
\]

如果：

\[
4096\rightarrow16384
\]

单层就是：

\[
67,108,864
\]

约：

\[
67M
\]

参数。

所以 Hidden Size 一扩大：

> 参数增长非常快。

---

## 80. Width 翻倍，参数不一定只翻倍

假设：

\[
d\rightarrow d
\]

矩阵参数：

\[
d^2
\]

如果：

\[
d\rightarrow2d
\]

参数变成：

\[
(2d)^2=4d^2
\]

也就是说：

> 宽度翻倍，某些层参数可能四倍。

这个工程直觉很重要。

---

## 81. Depth 增加则怎样？

如果每一层大小固定：

\[
d
\]

每增加一层大约增加：

\[
d^2
\]

级别参数。

所以：

\[
Width
\]

和：

\[
Depth
\]

对参数成本的影响方式不同。

---

## 82. 更深和更宽哪个更好？

没有统一答案。

更宽：

> 一层可以表达更多并行模式。

更深：

> 可以形成更多级组合。

具体取决于：

- 任务；
- 数据；
- 架构；
- 优化；
- 算力。

---

## 83. 一个很重要的工程认知

模型 Scale 不只是：

\[
ParameterCount
\]

还包括：

\[
Depth
\]

\[
Width
\]

\[
ContextLength
\]

\[
Data
\]

\[
Compute
\]

不同 Scale 方向：

> 会产生不同能力和成本。

---

## 84. 回到 ProcurementLM

假设我们用普通 MLP 做资格风险：

输入手工 Feature：

\[
X\in\mathbb{R}^{25}
\]

第一层：

\[
25\rightarrow128
\]

第二层：

\[
128\rightarrow64
\]

输出：

\[
64\rightarrow1
\]

模型内部已经可以：

> 自动组合 25 个指标。

---

## 85. 但这仍然不是 LLM

因为输入：

\[
25个手工Feature
\]

仍然是：

> 人工定义。

真正 LLM：

> 直接从 Token Embedding 开始。

然后经过大量：

\[
HiddenState
\]

转换。

---

## 86. Transformer 里的每个 Token 都有 Hidden State

例如一句话经过 Tokenizer：

```text
供应商
必须
在
本市
注册
```

每个 Token 都会有：

\[
H
\]

比如：

\[
4096维
\]

表示。

所以可能是：

\[
SequenceLength\times HiddenSize
\]

---

## 87. 一个 Shape 预告

假设：

\[
Batch=8
\]

\[
SequenceLength=2048
\]

\[
HiddenSize=4096
\]

那么 Hidden State：

\[
\boxed{
(8,2048,4096)
}
\]

这个 Tensor：

> 就是未来 Transformer 大量处理的对象。

---

## 88. 每一层 Transformer 都在更新这些表示

Layer 1：

\[
H_0\rightarrow H_1
\]

Layer 2：

\[
H_1\rightarrow H_2
\]

……

Layer 32：

\[
H_{31}\rightarrow H_{32}
\]

所以：

\[
\boxed{
Transformer
本质上也是持续变换Representation
}
\]

---

## 89. Attention 在这个体系里做什么？

先预告：

MLP：

> 主要在每个位置内部转换 Representation。

Attention：

> 让不同 Token 之间交换信息。

以后会形成：

\[
\boxed{
Attention
+
MLP
}
\]

共同更新 Hidden State。

---

## 90. 所以今天这课离 LLM 已经很近了

我们现在已经拥有：

\[
Vector
\]

\[
HiddenState
\]

\[
HiddenSize
\]

\[
Layer
\]

\[
Depth
\]

\[
Width
\]

这些全部是理解 Transformer 的基础语言。

---

## 91. 一个更深的概念：Representation 是“任务相关的信息压缩”

输入可能非常复杂。

模型不断形成：

\[
H
\]

理想情况下：

> 保留对后续任务最重要的信息。

这可以理解为一种：

\[
\boxed{
Information\ Transformation
}
\]

甚至某种：

> 有损压缩。

---

## 92. 但不是维度降低才叫压缩

即使：

\[
768\rightarrow3072
\]

维度变大，

仍然可能在：

> 信息结构上进行重新组织。

所以 Representation Learning：

> 不等于简单的数据压缩。

---

## 93. 一个 Hidden State 可能同时保存很多东西

例如某个 Token：

> “本市”

的向量可能同时编码：

- 它是地理概念；
- 当前位置；
- 与“注册”的关系；
- 与“供应商”的关系；
- 是否处于限制性条件；
- 上下文语义。

所以：

\[
H
\]

可以是高度上下文化的表示。

---

## 94. 这和传统 One-hot 非常不同

One-hot：

```text
本市 = ID 1234
```

无论上下文：

> 表示基本一样。

深层网络 Hidden State：

> 同一个词在不同句子里可以完全不同。

例如：

A：

> “项目地点位于本市。”

B：

> “供应商必须在本市注册。”

虽然都有：

> “本市”。

最终 Representation：

> 应该不同。

---

## 95. 这就是 Contextual Representation

# 上下文化表示

这是未来 Transformer 最重要能力之一。

模型不只知道：

> 这个 Token 是什么。

还知道：

> 它在当前上下文里扮演什么角色。

---

## 96. 第六个关键认知：层越深，不代表语义必然越“高级”

这是一个常见过度简化。

概念上我们说：

```text
浅层 → 基础
深层 → 高级
```

很有帮助。

但真实模型：

> 信息可能跨很多层流动。

不同层可能有不同功能，

但不是严格的：

> 第 1 层词语，第 20 层法律推理。

---

## 97. 为什么不能太机械理解层？

因为神经网络是：

> 共同优化。

没有人工告诉：

```text
Layer 3 负责语法
Layer 8 负责竞争
Layer 12 负责法律
```

这些功能都是：

> Loss 驱动下自组织产生。

---

## 98. 所以解释 Hidden Representation 很难

我们只能通过：

- probing；
- visualization；
- activation analysis；
- causal intervention；
- feature attribution；

等方法研究。

这以后属于：

# Interpretability

可解释性。

---

## 99. 但不能因为难解释就说里面“什么都没有”

如果模型稳定完成：

> 语义、推理、分类任务，

那么内部一定存在：

> 支持这些行为的某种计算结构。

只是：

> 不一定以人类容易理解的方式编码。

---

## 100. 这也是为什么“模型知识存在哪里”不是简单问题

不是：

> 某一个参数 = 某一条法规。

更接近：

\[
\boxed{
大量参数
+
大量激活
+
不同层之间的交互
}
\]

共同形成行为。

---

## 101. Static Parameters 和 Dynamic Activations

这是非常重要的区别。

参数：

\[
W,b
\]

训练完以后：

> 相对固定。

但每次输入产生的：

\[
H
\]

不同。

所以：

\[
\boxed{
Parameters
=
长期学到的计算规则
}
\]

\[
\boxed{
Activations
=
当前输入下产生的临时状态
}
\]

---

## 102. 用政府采购专家类比

Parameters：

> 专家的长期知识、经验、判断习惯。

Activations：

> 专家今天正在阅读这个具体项目时，在脑子里形成的当前判断状态。

这个比喻不是严格等价，

但非常好用。

---

## 103. 为什么 Hidden State 会随着输入变化？

因为：

\[
H=f(WX+b)
\]

虽然：

\[
W,b
\]

固定，

但：

\[
X
\]

不同。

所以：

\[
H
\]

自然不同。

模型因此能针对：

> 每一个具体采购条款

形成不同内部表示。

---

## 104. 参数负责“能力”，Activation 负责“当前思考状态”

这是一个非常有用的高层直觉。

\[
\boxed{
Weights
=
Capability
}
\]

\[
\boxed{
Activations
=
Computation\ on\ Current\ Input
}
\]

以后理解 KV Cache、Attention、Hidden State 都很有帮助。

---

## 105. 第六个核心心智模型

### 心智模型 ⑥：权重是长期状态，Hidden Activation 是当前输入下动态产生的工作状态

模型不是：

> 从参数表里直接查一个答案。

而是：

\[
Input
\]

进入以后，

参数进行大量计算，

产生：

\[
HiddenStates
\]

最后生成答案。

---

## 106. 一个完整前向传播例子

假设：

\[
X=
\begin{bmatrix}
1\\
0\\
1
\end{bmatrix}
\]

第一层：

\[
W_1=
\begin{bmatrix}
1&1&0\\
0&2&-1
\end{bmatrix}
\]

\[
b_1=
\begin{bmatrix}
0\\
0
\end{bmatrix}
\]

---

## 107. 计算第一层

\[
W_1X
=
\begin{bmatrix}
1&1&0\\
0&2&-1
\end{bmatrix}
\begin{bmatrix}
1\\
0\\
1
\end{bmatrix}
\]

第一行：

\[
1(1)+1(0)+0(1)=1
\]

第二行：

\[
0(1)+2(0)-1(1)=-1
\]

所以：

\[
z_1=
\begin{bmatrix}
1\\
-1
\end{bmatrix}
\]

---

## 108. 经过 ReLU

\[
H_1=ReLU(z_1)
\]

得到：

\[
\boxed{
H_1=
\begin{bmatrix}
1\\
0
\end{bmatrix}
}
\]

原来的 3 维输入：

\[
[1,0,1]
\]

已经变成新的 2 维表示：

\[
[1,0]
\]

---

## 109. 再进入第二层

假设：

\[
W_2=
\begin{bmatrix}
2&-1
\end{bmatrix}
\]

\[
b_2=-0.5
\]

那么：

\[
z_2
=
2(1)-1(0)-0.5
\]

\[
\boxed{
z_2=1.5
}
\]

---

## 110. 输出 Sigmoid

\[
p=\sigma(1.5)
\]

大约：

\[
\boxed{
0.818
}
\]

所以：

```text
Input
[1,0,1]

↓

Hidden
[1,0]

↓

Logit
1.5

↓

Risk Score
0.818
```

这就是一个完整 Forward Pass。

---

## 111. 这次你应该特别注意什么？

不是：

> 最终 0.818。

而是中间：

\[
\boxed{
[1,0,1]
\rightarrow
[1,0]
}
\]

这个转换。

因为：

> 这就是 Representation Learning 最小版本。

---

## 112. 如果换一个输入

例如：

\[
X=
\begin{bmatrix}
0\\
1\\
1
\end{bmatrix}
\]

第一层产生的：

\[
H_1
\]

会完全不同。

同样参数：

> 为不同输入构造不同表示。

---

## 113. 为什么需要多层 Hidden？

一层：

> 可以学一次非线性转换。

多层：

\[
H_1=f_1(W_1X+b_1)
\]

\[
H_2=f_2(W_2H_1+b_2)
\]

\[
H_3=f_3(W_3H_2+b_3)
\]

意味着：

> 对表示连续加工。

---

## 114. 每层可以把上一层当成“新输入”

第一层：

> 不知道最终答案，只负责构造有用 Feature。

第二层：

> 不再直接面对原始数据，而面对第一层 Feature。

第三层：

> 再组合第二层 Feature。

所以：

\[
\boxed{
Abstraction\ builds\ on\ abstraction
}
\]

---

## 115. 这非常像专家学习

初学者看到：

> “供应商必须有5个同类项目。”

首先只看到：

> 5 个。

有经验以后看到：

> 业绩数量门槛。

更进一步想到：

> 与履约能力是否相关。

更进一步：

> 是否造成不合理竞争限制。

也就是不断：

\[
RawFact
\rightarrow
Concept
\rightarrow
Principle
\rightarrow
Judgment
\]

---

## 116. 神经网络是不是在像人一样思考？

不能直接这么下结论。

这个类比只是帮助理解：

> 层级表示。

神经网络内部计算：

> 是数值向量变换。

不要把人类概念结构直接投射到模型内部。

---

## 117. 模型的表示可能比人类语言更“细”

人类可能只有一个词：

> “限制性”。

但模型内部可能存在很多不同方向：

- 地域型限制；
- 时间型限制；
- 规模型限制；
- 品牌型限制；
- 业绩型限制。

甚至更加细微。

向量空间可以表达：

> 连续程度。

---

## 118. 表示可以是连续的，而不是标签式的

人工规则：

```text
风险 = 0 / 1
```

Hidden Feature：

\[
0.13,\ 0.72,\ -1.4,\ 2.1
\]

可以表达：

> 程度、方向和复杂组合。

这也是神经网络优势之一。

---

## 119. Representation Space 中“相似”是什么意思？

如果两个样本的 Hidden Vector：

\[
h_A
\]

和：

\[
h_B
\]

很接近，

可能说明模型认为：

> 它们在当前任务相关意义上相似。

以后：

\[
CosineSimilarity
\]

就会衡量这种相似性。

---

## 120. 这直接连接 Embedding 和 RAG

为什么 RAG 可以找相似文本？

因为：

```text
文本
↓
Embedding Model
↓
Vector
```

然后比较：

\[
VectorDistance
\]

所以今天学的 Representation：

> 正是以后 Vector Database 的理论根。

---

## 121. 第七个核心心智模型

### 心智模型 ⑦：好的表示会让“语义上相似的东西在向量空间里更容易被一起处理”

例如：

> “须在本地注册”

和：

> “投标人注册地必须位于项目所在地”

表面词不同，

如果模型表示好：

\[
h_A\approx h_B
\]

于是模型能跨措辞泛化。

---

## 122. 但相似表示也取决于训练目标

如果模型训练任务是：

> 风险识别，

它可能认为这两条很相似。

如果任务是：

> 法律文书来源识别，

它可能更关注：

- 地区；
- 写作风格；
- 机构模板。

所以：

\[
\boxed{
Representation
是Task-dependent的
}
\]

---

## 123. 同一个输入可以有不同“好表示”

没有唯一正确向量。

对于：

> 翻译任务，

好的表示需要语言语义。

对于：

> 作者识别，

好的表示需要风格。

对于：

> 政府采购风险，

好的表示应该强化合规相关因素。

---

## 124. 这再次说明 Task Definition 决定模型学习什么

第一课第一阶段：

\[
X\rightarrow Y
\]

现在深入内部：

\[
Y
\]

通过 Loss，

反向决定：

> 什么样的 Hidden Representation 有价值。

所以：

\[
\boxed{
Task
\rightarrow
Loss
\rightarrow
Representation
}
\]

---

## 125. 这也是 Fine-tuning 为什么会改变模型

预训练模型已经有：

\[
H
\]

表示。

做政府采购 SFT：

> Loss 会推动参数变化。

于是部分 Hidden Representation：

> 更适合政府采购任务。

这就是领域适配的一个内部视角。

---

## 126. CPT 又做了什么？

领域继续预训练：

> 让模型大量接触政府采购语言。

于是参数和 Representation：

> 会对法规、公告、采购文件语言更加熟悉。

然后 SFT：

> 再塑造具体工作方式。

---

## 127. 所以 CPT 和 SFT 可以从表示角度理解

CPT：

\[
\boxed{
Learn\ Domain\ Representation
}
\]

SFT：

\[
\boxed{
Learn\ Task\ Behavior
}
\]

这是简化说法，但很有帮助。

---

## 128. RAG 又有什么不同？

RAG：

> 不主要依赖改参数形成新 Representation。

而是在推理时：

\[
Input
+
RetrievedEvidence
\]

一起进入模型。

所以它改变：

> 当前上下文和 Hidden Activation。

---

## 129. 这个区别非常漂亮

训练：

> 改 \(W\)。

RAG：

> 改 \(X\)。

于是：

\[
H=f(WX)
\]

都会变化。

所以：

\[
\boxed{
FineTune
=
ChangeWeights
}
\]

\[
\boxed{
RAG
=
ChangeContext
}
\]

---

## 130. 这是以后模型架构设计的重要视角

知识问题：

> 不一定全靠改 Weight。

可以：

> 给更好的 Context。

行为问题：

> 可能需要训练 Weight。

这正是 ProcurementAI：

\[
LLM+RAG+Rules
\]

架构的理论来源之一。

---

## 131. 第二课 · 第 3 阶段的核心知识压缩

现在把整个阶段压成：

\[
\boxed{
X
\xrightarrow{W_1,f}
H_1
\xrightarrow{W_2,f}
H_2
\xrightarrow{W_3}
Y
}
\]

关键不只是：

\[
Y
\]

而是：

\[
H_1,H_2
\]

这些模型自己学习出来的中间表示。

---

## 132. 本阶段五个最重要的核心心智模型

我们前面实际上讲了更多，但最终建议先牢牢记住这 5 个：

| 心智模型 | 核心认知 |
|---|---|
| **① Hidden Layer 创造新表示** | 它不是单纯增加计算次数 |
| **② 概念是分布式向量表示** | 不要机械理解为“一神经元一个概念” |
| **③ Width 与 Depth 是不同能力维度** | Width 扩展同时表达能力，Depth 扩展层级组合能力 |
| **④ 深度网络让问题在新空间中变简单** | 前面层主要负责学习 Representation |
| **⑤ Shape 是理解网络结构的第二语言** | 每经过一层都要知道输入/输出维度如何变化 |

---

## 133. 如果只记一个公式

请记：

\[
\boxed{
H=f(WX+b)
}
\]

它意味着：

> 输入经过模型参数和非线性，被转换成一个新的表示。

下一层继续对这个：

\[
H
\]

操作。

---

## 134. 如果只记一句话

\[
\boxed{
深度神经网络的核心，不只是“做更多计算”，
而是逐层把原始信息重新表示成越来越适合完成任务的形式。
}
\]

---

## 135. 第二课前三阶段现在串起来了

### 第 1 阶段

\[
z=WX+b
\]

解决：

> 信息怎样被加权组合。

### 第 2 阶段

\[
h=f(z)
\]

解决：

> 怎样引入非线性。

### 第 3 阶段

\[
X\rightarrow H_1\rightarrow H_2
\]

解决：

> 怎样逐层学习 Representation。

于是：

\[
\boxed{
WeightedCombination
+
Nonlinearity
+
RepresentationHierarchy
}
\]

已经构成深度神经网络的骨架。

---

## 136. 第 3 阶段小思维实验

假设一个网络：

```text
Input = 20维

Hidden1 = 64维

Hidden2 = 32维

Output = 1维
```

请在脑子里立刻看到：

\[
20
\rightarrow
64
\rightarrow
32
\rightarrow
1
\]

第一层参数：

\[
20\times64+64
=
1344
\]

第二层：

\[
64\times32+32
=
2080
\]

输出：

\[
32\times1+1
=
33
\]

总参数：

\[
\boxed{
3457
}
\]

---

## 137. 再问 Shape

如果：

\[
BatchSize=128
\]

那么输入：

\[
(128,20)
\]

第一层后：

\[
(128,64)
\]

第二层：

\[
(128,32)
\]

输出：

\[
\boxed{
(128,1)
}
\]

这个 Shape 链以后必须逐渐做到：

> 一眼能看出来。

---

## 138. 第 3 阶段掌握标准

完成本阶段以后，你应该能自然回答：

> Hidden Layer 为什么叫 Hidden？

> Representation 是什么？

> Hidden Size 768 到底表示什么？

> Width 和 Depth 有什么区别？

> `Linear(768,3072)` 参数怎么算？

> Batch=32 时 Shape 怎么变化？

> 为什么多层网络可以形成层级抽象？

> 为什么不能简单认为一个 Neuron 就是一个人类概念？

> Parameters 和 Activations 有什么区别？

> Fine-tuning 和 RAG 从 \(H=f(WX)\) 的角度有什么不同？

如果这些已经清楚：

> 第 3 阶段就真正学到了。

---

接下来进入 **第二课 · 第 4 阶段：Forward Propagation——一条政府采购样本到底如何从输入开始，逐层穿过整个神经网络，最终变成一个风险概率。**

那一阶段我们会第一次把：

\[
\boxed{
MatrixShape
+
Linear
+
Activation
+
HiddenState
+
Output
}
\]

完整执行一遍，而且会开始引入 **Tensor、Batch Forward、计算图 Computational Graph**。

这会为后面最重要的 **Backpropagation** 正式铺路。

---
