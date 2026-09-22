# 第二课 · 第 8 阶段：Embedding 与高维向量空间
## “供应商”“注册资本”“本市”这些文字，究竟怎样变成神经网络可以计算的数字？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Token ID ≠ Semantic Meaning。整数 ID 本身没有语义，语义来自对应的 Embedding Vector。**
2. **Embedding 本质是一个可学习查表：离散 Token → 连续高维向量。**
3. **Embedding Space 的几何关系可以承载相似性，但“距离近”不自动等于法律规则或业务等价。**
4. **Embedding 的每一维通常没有稳定的人类命名含义，语义是分布式编码。**
5. **输入 Embedding 只是起点；经过 Attention 和 MLP 后，表示会随上下文不断变化。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Embedding` | 嵌入：把离散 Token 映射到连续高维向量 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Representation` | 表示：模型内部承载语义或特征的向量结构 |
| `Attention` | 注意力：根据内容相关性动态聚合信息 |
| `Transformer` | Transformer：以注意力和前馈网络为核心的序列架构 |
| `Tokenizer` | 分词器：文本与 Token ID 之间的编码/解码组件 |
| `State` | 状态：保存任务进度、事实和待办 |
| `Batch` | 批次：一次参与计算的一组样本 |
| `Optimizer` | 优化器：依据梯度规则更新参数 |
| `Neuron` | 神经元：加权、偏置和非线性变换的最小计算单元 |
| `PyTorch` | PyTorch：张量计算、自动求导和训练/推理框架 |
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

前 7 个阶段，我们其实一直偷偷做了一个假设：

\[
X
\]

已经是数字。

例如：

\[
X=
[0.8,0.3,0.2]
\]

然后神经网络就可以：

\[
WX+b
\]

但真正的 ProcurementLM 输入不是：

\[
[0.8,0.3,0.2]
\]

而是：

> “供应商注册资本不得低于5000万元。”

于是一个无法绕开的基础问题出现了：

\[
\boxed{
文字不能直接和Weight矩阵相乘
}
\]

神经网络真正能处理的是：

\[
Numbers
\]

所以文本模型第一步必须完成：

\[
\boxed{
Text
\rightarrow
DiscreteSymbol
\rightarrow
ID
\rightarrow
Vector
}
\]

今天我们重点研究最后这个关键转换：

\[
\boxed{
TokenID
\rightarrow
EmbeddingVector
}
\]

也就是：

# Embedding

---

## 1. 先把第 8 阶段放进整个 LLM 路线

到目前为止：

\[
Neuron
\rightarrow
Activation
\rightarrow
HiddenLayer
\rightarrow
Forward
\rightarrow
Backward
\rightarrow
Optimizer
\rightarrow
StableDeepNetwork
\]

现在进入：

\[
\boxed{
Text
\rightarrow
Token
\rightarrow
Embedding
\rightarrow
HiddenState
}
\]

然后后面才有：

\[
Attention
\rightarrow
Transformer
\rightarrow
LLM
\]

所以：

> Embedding 是语言进入神经网络世界的入口之一。

---

## 2. 今天先做一个重要约定

真正的文字：

> “供应商不得……”

必须先经过：

# Tokenizer

分成 Token。

Tokenizer 本身很重要，我们下一阶段会专门拆。

今天暂时假设：

> Tokenizer 已经把文字分好了。

例如：

```text
供应商
注册
资本
不得
低于
5000
万元
```

今天只研究：

> 这些离散 Token 怎么进入神经网络。

---

## 3. 神经网络不能处理“供应商”这个字符串

Linear Layer 要做：

\[
WX
\]

Weight：

\[
W
\]

是数字矩阵。

所以：

\[
X
\]

也必须是数字。

不能写：

\[
W\times \text{“供应商”}
\]

数学上根本没有定义。

---

## 4. 最简单方案：给每个 Token 一个编号

假设 Vocabulary：

| Token | ID |
|---|---:|
| 供应商 | 0 |
| 注册 | 1 |
| 资本 | 2 |
| 本市 | 3 |
| 项目 | 4 |

于是：

> “供应商”

变成：

\[
0
\]

> “本市”

变成：

\[
3
\]

---

## 5. 这叫 Token ID

也就是：

\[
\boxed{
Token
\rightarrow
IntegerID
}
\]

例如：

```text
供应商 → 0
注册 → 1
资本 → 2
```

一句：

> “供应商 注册 资本”

可以暂时写成：

\[
[0,1,2]
\]

---

## 6. 那模型直接拿 ID 计算可以吗？

看起来似乎可以。

例如：

\[
供应商=0
\]

\[
注册=1
\]

\[
本市=3
\]

但马上出现严重问题。

---

## 7. ID 的数字大小没有语义

如果：

\[
本市=3
\]

\[
项目=4
\]

并不意味着：

> “项目”比“本市”大 1。

也不意味着：

> 它们特别相似。

ID 只是：

\[
\boxed{
Index
}
\]

索引。

---

## 8. 第一个核心心智模型

### 心智模型 ①：Token ID 是地址，不是语义

记住：

\[
\boxed{
ID\neq Meaning
}
\]

ID：

> 告诉模型去哪里找这个 Token 对应的参数。

它本身：

> 不承载可靠语义距离。

---

## 9. 那怎样表示离散类别？

机器学习里一个经典办法：

# One-Hot Encoding

假设 Vocabulary 有：

\[
5
\]

个 Token。

---

## 10. “供应商”的 One-hot

ID：

\[
0
\]

那么：

\[
供应商
=
[1,0,0,0,0]
\]

---

## 11. “注册”

ID：

\[
1
\]

表示：

\[
[0,1,0,0,0]
\]

---

## 12. “本市”

ID：

\[
3
\]

表示：

\[
[0,0,0,1,0]
\]

只有对应位置：

\[
1
\]

其它全部：

\[
0
\]

所以叫：

# One-hot

---

## 13. One-hot 解决了什么？

至少不会再出现：

\[
ID=8
\]

比：

\[
ID=2
\]

“更大”的错误暗示。

每个 Token：

> 是平等的离散类别。

---

## 14. 但 One-hot 有第一个巨大问题

假设 Vocabulary：

\[
V=100000
\]

那么每一个 Token：

> 都需要一个 100000 维向量。

例如：

\[
[0,0,0,\ldots,1,\ldots,0]
\]

其中只有一个：

\[
1
\]

---

## 15. 太浪费了

100000 个数字里：

\[
99999
\]

个都是：

\[
0
\]

所以 One-hot 是：

# Sparse Representation

稀疏表示。

---

## 16. 第二个问题更加致命：没有相似性

假设：

\[
v_{\text{供应商}}
\]

和：

\[
v_{\text{投标人}}
\]

都是不同 One-hot。

它们点积：

\[
v_1^Tv_2=0
\]

---

## 17. “供应商”和“天气”呢？

同样：

\[
0
\]

所以在 One-hot 空间：

> “供应商”和“投标人”

与：

> “供应商”和“天气”

几何关系一样。

这显然不符合语言。

---

## 18. 也就是说 One-hot 只表示 Identity

它能告诉模型：

> 这是哪个 Token。

但完全没有告诉：

> Token 之间有什么关系。

所以：

\[
\boxed{
OneHot
=
IdentityRepresentation
}
\]

而不是：

\[
SemanticRepresentation
\]

---

## 19. 这就引出 Embedding

我们真正希望：

> 每个 Token 不再是十万个 0/1。

而是一个较短的稠密向量。

例如：

\[
供应商
\rightarrow
[0.18,-0.72,1.03,0.44,\ldots]
\]

---

## 20. 假设 Embedding Dimension = 4

可以有：

\[
e_{\text{供应商}}
=
[0.2,-0.7,0.4,1.1]
\]

\[
e_{\text{投标人}}
=
[0.18,-0.65,0.5,1.02]
\]

\[
e_{\text{天气}}
=
[-1.3,0.2,-0.9,0.1]
\]

这就是：

# Dense Vector

稠密向量。

---

## 21. 为什么叫 Dense？

因为向量中的大量位置：

> 都可能不是 0。

例如：

\[
[0.2,-0.7,0.4,1.1]
\]

不像 One-hot：

\[
[0,0,0,1,0,\ldots]
\]

那么稀疏。

---

## 22. Embedding 的第一层意义

\[
\boxed{
离散符号
\rightarrow
连续向量空间
}
\]

这是语言模型里非常根本的一次转换。

Token 原本只有：

> 是 / 不是。

现在变成：

> 在很多连续维度上的位置。

---

## 23. 第二个核心心智模型

### 心智模型 ②：Embedding 把“离散身份”转换成“连续几何位置”

原来：

```text
供应商
投标人
采购人
天气
```

只是四个不同 ID。

Embedding 后：

> 它们进入同一个 Vector Space。

于是终于可以讨论：

\[
Distance
\]

\[
Direction
\]

\[
Similarity
\]

---

# 一、Embedding Matrix 到底是什么？

## 24. 假设词表有 5 个 Token

Vocabulary：

\[
V=5
\]

Embedding Dimension：

\[
d=3
\]

那么建立一个矩阵：

\[
E\in\mathbb R^{5\times3}
\]

---

## 25. 例如

\[
E=
\begin{bmatrix}
0.2&-0.5&0.8\\
0.1&0.7&-0.3\\
-0.4&0.2&0.9\\
0.8&-0.1&0.3\\
-0.6&0.4&0.1
\end{bmatrix}
\]

每一行：

> 对应一个 Token。

---

## 26. 如果 Token ID = 0

那么：

\[
Embedding(0)
=
E_{0,:}
\]

得到：

\[
[0.2,-0.5,0.8]
\]

---

## 27. 如果 Token ID = 3

取第 3 行：

\[
E_{3,:}
\]

得到：

\[
[0.8,-0.1,0.3]
\]

所以 Embedding Layer 本质上首先可以理解成：

\[
\boxed{
LookupTable
}
\]

查表。

---

## 28. 这句话非常关键

很多初学者看到：

```python
nn.Embedding(100000,4096)
```

觉得里面一定有：

> 很复杂的神经网络。

其实最基础的 Forward 操作：

> 根据 Token ID 取矩阵中的一行。

---

## 29. PyTorch 形式

例如：

```python
embedding = nn.Embedding(
    num_embeddings=5,
    embedding_dim=3
)
```

意味着：

\[
E.shape=(5,3)
\]

---

## 30. 输入 ID

```python
token_id = 3
```

Forward：

```python
embedding(token_id)
```

结果：

> 取第 3 行。

---

## 31. 如果输入一串 Token ID 呢？

例如：

\[
[0,3,1,2]
\]

那么输出：

\[
[
E_0,
E_3,
E_1,
E_2
]
\]

Shape：

\[
\boxed{
(4,d)
}
\]

---

## 32. 这就是 Sequence Length 维出现了

如果：

\[
SequenceLength=4
\]

\[
EmbeddingDim=3
\]

那么：

\[
EmbeddingOutput.shape=(4,3)
\]

---

## 33. 如果 Batch = 8 呢？

输入：

\[
TokenIDs.shape=(8,4)
\]

Embedding 后：

\[
\boxed{
(8,4,3)
}
\]

即：

\[
Batch
\times
Sequence
\times
EmbeddingDimension
\]

---

## 34. 这已经非常接近 Transformer Shape

未来：

\[
(B,S,D)
\]

就是：

\[
Batch
\times
SequenceLength
\times
HiddenSize
\]

例如：

\[
(8,2048,4096)
\]

---

## 35. 第三个核心心智模型

### 心智模型 ③：Embedding Layer 是“参数矩阵 + 按 ID 取行”

核心：

\[
\boxed{
E\in\mathbb R^{V\times d}
}
\]

Token：

\[
i
\]

得到：

\[
\boxed{
e_i=E[i]
}
\]

这一个式子以后会一直用。

---

# 二、Embedding 和 One-hot 有什么数学关系？

## 36. 这里有一个很漂亮的等价关系

假设 Token：

\[
i=2
\]

其 One-hot：

\[
x=
[0,0,1,0,0]
\]

如果：

\[
E\in\mathbb R^{5\times3}
\]

那么：

\[
x^TE
\]

会发生什么？

---

## 37. One-hot 乘矩阵

因为：

\[
x
\]

只有第 3 个位置是：

\[
1
\]

所以：

\[
x^TE
\]

等于：

> 直接选择 \(E\) 的第 3 行。

也就是：

\[
\boxed{
x^TE=E_i
}
\]

---

## 38. 所以 Embedding Lookup 可以看作优化版矩阵乘法

理论上：

\[
OneHot
\rightarrow
MatrixMultiply
\rightarrow
Embedding
\]

实际上没必要真的创建巨大 One-hot。

直接：

\[
\boxed{
IndexLookup
}
\]

即可。

---

## 39. 为什么工程上差别巨大？

假设：

\[
V=150000
\]

如果每个 Token 都先造一个：

\[
150000维
\]

One-hot：

> 极其浪费。

直接 ID Lookup：

> 快得多、节省大量内存。

---

## 40. 但数学理解 One-hot 很有价值

因为它告诉我们：

> Embedding 并不是脱离 Linear Algebra 的特殊魔法。

它本质上仍然可以理解为：

\[
\boxed{
OneHot\times TrainableMatrix
}
\]

---

# 三、Embedding Matrix 是固定的吗？

## 41. 最关键的问题来了

刚开始：

\[
E
\]

里的数字从哪里来？

通常：

> 初始化。

例如随机初始化。

---

## 42. 一开始有没有语义？

通常没有多少。

可能：

\[
供应商
=
[0.01,-0.03,0.02,\ldots]
\]

\[
天气
=
[-0.02,0.01,0.04,\ldots]
\]

只是随机数。

---

## 43. 那语义从哪里来？

训练。

Embedding Matrix：

\[
E
\]

本身就是：

# Trainable Parameter

---

## 44. 这意味着 Embedding 也参与 Backprop

例如：

\[
TokenID
\rightarrow
Embedding
\rightarrow
Transformer
\rightarrow
Logits
\rightarrow
Loss
\]

Backward：

\[
Loss
\rightarrow
\cdots
\rightarrow
EmbeddingMatrix
\]

---

## 45. 第 5 阶段学的 Backprop 终于走到文字入口

Gradient 会计算：

\[
\boxed{
\frac{\partial L}
{\partial E}
}
\]

于是：

\[
E
\]

也会被 Optimizer 更新。

---

## 46. 某个 Token 出现在当前 Batch 中

例如：

> “供应商”

对应：

\[
ID=125
\]

Forward 取：

\[
E_{125}
\]

Backward：

> 对这个 Row 产生 Gradient。

---

## 47. 一个最简单直觉

如果训练数据不断告诉模型：

> “供应商”和“投标人”经常出现在相似上下文和任务关系中，

训练最终可能把二者向量调整成：

> 某些方面更相似。

---

## 48. 这就是 Learned Embedding

不是：

> 人手给“供应商”设计 4096 个 Feature。

而是：

\[
\boxed{
让Loss通过Backprop自己塑造Vector
}
\]

---

## 49. 第四个核心心智模型

### 心智模型 ④：Embedding 的“语义”不是写进数组里的，而是 Loss 长期塑造出来的几何结构

所以：

\[
\boxed{
EmbeddingMeaning
=
TrainingHistory
}
\]

更准确地说：

> 语义来自训练目标、数据分布和模型整体共同塑造的参数结构。

---

# 四、为什么相似上下文会产生相似表示？

## 50. 这里开始进入 Distributional Semantics

语言学和 NLP 里有一个非常重要的直觉：

> 出现在相似上下文中的词，往往具有某些相似语义或功能。

---

## 51. 政府采购例子

下面两句话：

> “供应商应具有独立承担民事责任的能力。”

> “投标人应具有独立承担民事责任的能力。”

“供应商”和“投标人”：

> 周围上下文高度相似。

---

## 52. 再比如

> “采购人依法确定中标供应商。”

> “采购人应当公开采购意向。”

“采购人”：

> 出现的角色和上下文模式与“供应商”不同。

---

## 53. 模型不是先查词典再学向量

大规模预训练更多是：

> 通过预测任务被迫理解什么词在什么上下文中合理。

于是：

> 语义关系逐渐反映到参数和表示空间里。

---

## 54. 这就是 Distributional Hypothesis 的核心直觉

可以粗略概括：

\[
\boxed{
SimilarContexts
\Rightarrow
RelatedRepresentations
}
\]

但注意：

> 不是数学上绝对保证。

它取决于训练目标和模型。

---

# 五、向量“相似”到底是什么意思？

## 55. 假设两个 Embedding

\[
a=
[1,2]
\]

\[
b=
[2,4]
\]

看起来：

> 方向相同。

---

## 56. Dot Product

点积：

\[
a^Tb
\]

即：

\[
1(2)+2(4)
=
10
\]

点积大：

> 常常意味着方向和尺度共同比较匹配。

---

## 57. 但点积同时受长度影响

例如：

\[
a=[1,0]
\]

\[
b=[100,0]
\]

点积：

\[
100
\]

非常大。

因为：

> b 很长。

---

## 58. 如果只关心方向相似性呢？

这就引出：

# Cosine Similarity

余弦相似度。

---

## 59. 公式

\[
\boxed{
cos(a,b)
=
\frac{a^Tb}
{\|a\|\|b\|}
}
\]

---

## 60. 它基本消除了向量长度影响

如果：

\[
a=[1,0]
\]

\[
b=[100,0]
\]

那么：

\[
cos(a,b)=1
\]

说明：

> 方向完全一致。

---

## 61. 如果方向相反

\[
a=[1,0]
\]

\[
b=[-1,0]
\]

那么：

\[
cos(a,b)=-1
\]

---

## 62. 垂直呢？

\[
a=[1,0]
\]

\[
b=[0,1]
\]

则：

\[
cos(a,b)=0
\]

---

## 63. 所以 Cosine 的典型范围

\[
[-1,1]
\]

其中：

\[
1
\]

方向相同。

\[
0
\]

正交。

\[
-1
\]

方向相反。

---

## 64. 这和第一阶段的 Dot Product 再次接上

我们最早学：

\[
W^TX
\]

现在看到：

> 向量之间的语义关系，也经常通过点积结构被利用。

以后 Attention：

\[
QK^T
\]

仍然是：

> Dot Product。

---

## 65. 这不是巧合

现代深度学习里大量“匹配”行为，本质都利用：

\[
\boxed{
VectorGeometry
}
\]

例如：

- 分类；
- Embedding 检索；
- Attention；
- 相似度搜索。

---

# 六、什么叫高维向量空间？

## 66. 二维向量很好画

\[
x=[x_1,x_2]
\]

就是平面上的一个点。

---

## 67. 三维也能想象

\[
x=[x_1,x_2,x_3]
\]

是三维空间中的一个点。

---

## 68. 那 4096 维呢？

\[
x\in\mathbb R^{4096}
\]

无法画出来。

但数学规则：

> 没有变。

依然可以：

- 相加；
- 点积；
- 算距离；
- 投影；
- Linear Transformation。

---

## 69. 所以“高维”没有新魔法

只是：

\[
\boxed{
Dimensions\ 很多
}
\]

所有二维向量的很多数学直觉：

> 可以推广。

---

## 70. 为什么需要高维？

因为语言中可能同时存在非常多因素：

- 对象；
- 角色；
- 时间；
- 地域；
- 数量；
- 语义；
- 语法；
- 条件；
- 语气；
- 否定；
- 法律领域；
- 业务领域。

更高维空间：

> 给模型更多自由度去编码复杂结构。

---

## 71. 但千万不要理解成“一维对应一个概念”

例如：

\[
Dimension\ 37
\]

不一定就是：

> “供应商”。

\[
Dimension\ 82
\]

也不一定就是：

> “风险”。

真实表示通常：

# Distributed

---

## 72. 一个概念更可能是方向或子空间

例如：

\[
v_{qualification}
\]

可能代表：

> 某种资格条件方向。

但它一般不是：

> 某一根坐标轴。

而是：

\[
[0.13,-0.41,\ldots]
\]

横跨很多维度。

---

## 73. 这就和第 3 阶段彻底接上了

当时说：

\[
\boxed{
Concept
\approx
DirectionInRepresentationSpace
}
\]

Embedding 阶段：

> 我们第一次真正给语言创建了这个空间。

---

# 七、Distance 又是什么？

## 74. 最经典 Euclidean Distance

\[
\boxed{
d(a,b)
=
\|a-b\|_2
}
\]

例如：

\[
a=[1,2]
\]

\[
b=[2,4]
\]

差：

\[
[-1,-2]
\]

距离：

\[
\sqrt{1+4}
=
\sqrt5
\]

---

## 75. 距离小意味着什么？

在某个训练出来的 Embedding Space 中：

> 可能意味着表示相近。

但一定注意：

\[
\boxed{
CloseInVectorSpace
\neq
UniversalSemanticEquivalence
}
\]

---

## 76. 为什么？

因为 Vector Space 是：

> 某个训练目标学出来的。

如果模型主要训练：

> 文本主题分类，

它形成的“接近”可能更偏主题。

如果训练：

> 语义检索，

接近关系可能更偏语义相关性。

---

## 77. 所以所有 Embedding 都一样吗？

完全不是。

例如：

- LLM Token Embedding；
- Sentence Embedding；
- RAG Retrieval Embedding；
- Image Embedding；

训练目标不同。

空间含义：

> 也不同。

---

# 八、Token Embedding 和 Sentence Embedding 不要混淆

## 78. Token Embedding

输入：

\[
TokenID
\]

输出：

\[
e_i\in\mathbb R^d
\]

表示：

> 一个 Token 的基础向量。

---

## 79. Sentence Embedding

输入：

> 一整个句子。

输出：

\[
v_{sentence}
\]

用于：

- 检索；
- 相似度；
- 聚类。

---

## 80. 两者不能机械互换

LLM 内部 Token Embedding：

> 不一定适合直接拿去做 RAG 句子检索。

专业 RAG 通常使用：

> 专门训练的 Embedding Model。

---

## 81. 为什么？

因为 Retriever 需要优化：

\[
\boxed{
Query
\leftrightarrow
RelevantDocument
}
\]

这种几何关系。

而 LLM Token Embedding：

> 主要服务于语言模型内部计算。

---

# 九、一个 Token 的 Embedding 是“词义”吗？

## 82. 不能这么简单说

例如：

> “银行”

可能指：

- 金融机构；
- 河岸。

如果 Token Embedding 只有一张静态表：

\[
E[\text{银行}]
\]

那么最初取出来：

> 是同一个基础向量。

---

## 83. 那上下文差异从哪里来？

Embedding 进入 Transformer 后：

\[
H_0
=
Embedding
\]

经过 Attention 和其它层：

\[
H_1,H_2,\ldots,H_L
\]

不断根据上下文更新。

---

## 84. 最终同一个 Token 的 Hidden State 可以不同

句子 A：

> “银行批准了贷款。”

句子 B：

> “人在河流的岸边。”

如果相应 Token 相同或相关，

Transformer 后的：

\[
H_L
\]

可以根据上下文：

> 完全不同。

---

## 85. 这就是静态 Embedding 与 Contextual Representation 的区别

输入层：

\[
\boxed{
TokenEmbedding
}
\]

更多是：

> 基础身份表示。

深层：

\[
\boxed{
ContextualHiddenState
}
\]

已经融合：

> 当前上下文。

---

## 86. 政府采购例子

词：

> “本地”

A：

> “项目履约地点位于本地。”

B：

> “供应商必须在本地注册。”

最初“本地”的 Token Embedding：

> 可以相同。

但经过上下文计算：

\[
H_A
\neq
H_B
\]

---

## 87. 第五个核心心智模型

### 心智模型 ⑤：Token Embedding 是起点，不是最终语义

这是理解 LLM 的关键。

\[
\boxed{
StaticTokenEmbedding
+
ContextComputation
\rightarrow
ContextualRepresentation
}
\]

所以不能看到 Embedding Vector 就说：

> 这已经包含了整句话的全部含义。

---

# 十、Embedding Dimension 和 Hidden Size 是一回事吗？

## 88. 在很多 Transformer 中

Token Embedding 输出：

\[
d_{model}
\]

正好等于：

\[
HiddenSize
\]

例如：

\[
4096
\]

---

## 89. 为什么方便？

因为 Embedding 后：

\[
H_0.shape=(B,S,4096)
\]

可以直接进入 Transformer Block。

---

## 90. 但概念上要区分

Embedding Dimension：

> Token 初始向量的维度。

Hidden Size：

> 网络内部 Hidden State 的主维度。

很多架构让它们相等。

但并非数学上必须永远相同。

---

# 十一、Embedding Matrix 有多少参数？

## 91. 公式非常简单

Vocabulary Size：

\[
V
\]

Embedding Dimension：

\[
d
\]

那么：

\[
\boxed{
ParameterCount
=
Vd
}
\]

---

## 92. 一个例子

假设：

\[
V=50000
\]

\[
d=4096
\]

则：

\[
50000\times4096
=
204,800,000
\]

也就是：

\[
\boxed{
204.8M
}
\]

参数。

---

## 93. 仅仅“词表入口”就可能有上亿参数

这说明：

> 大模型参数不仅存在 Attention 和 FFN。

Embedding Matrix：

> 也可能非常大。

---

## 94. Vocabulary 越大有什么代价？

Embedding 参数：

\[
Vd
\]

所以：

\[
V\uparrow
\Rightarrow
EmbeddingParameters\uparrow
\]

同时输出 Vocabulary Projection：

> 也可能很大。

---

## 95. 但 Vocabulary 太小也有代价

同一段文字：

> 可能被切成更多 Token。

Sequence Length：

\[
S
\]

变大。

然后：

> Attention 和推理成本增加。

---

## 96. 这已经预告了下一阶段 Tokenizer 的核心权衡

\[
\boxed{
VocabularySize
\leftrightarrow
SequenceLength
}
\]

大词表：

> 单词更完整，但参数大。

小词表：

> 参数小，但序列可能更长。

---

# 十二、Embedding Matrix 怎样参与训练？

## 97. 假设一句话 Token IDs

\[
[12,85,37]
\]

Embedding Lookup：

\[
[E_{12},E_{85},E_{37}]
\]

---

## 98. Forward 后产生 Loss

\[
L
\]

Backprop 会得到：

\[
\frac{\partial L}{\partial E_{12}}
\]

\[
\frac{\partial L}{\partial E_{85}}
\]

\[
\frac{\partial L}{\partial E_{37}}
\]

---

## 99. 没出现的 Row 呢？

在最简单的 Embedding Lookup 情况下：

> 当前样本不会通过这一查表路径直接给未使用 Row 产生梯度。

---

## 100. 所以常见 Token 为什么学得更充分？

因为它们：

> 出现在更多训练样本里。

获得：

> 更多训练信号。

---

## 101. 稀有 Token 呢？

出现次数少：

> 直接训练机会少。

Embedding 可能：

> 学得相对不稳定。

这也是 Tokenization 和数据覆盖很重要的原因。

---

## 102. 政府采购领域会出现大量专业稀有词

例如：

- 框架协议；
- 质疑答复；
- 履约验收；
- 联合体；
- 专门面向中小企业；
- 政府购买服务。

如果基础 Tokenizer 切分极差：

> 模型学习这些领域概念的难度可能增加。

---

## 103. 但不要直接推出“必须把每个专业词加入 Vocabulary”

不一定。

现代 Subword Tokenization：

> 可以由多个 Token 组合表达新词。

是否扩 Vocabulary：

> 是一个工程实验问题。

---

# 十三、Embedding 是不是数据库？

## 104. 不是传统意义上的知识数据库

虽然：

\[
E[token]
\]

像查表。

但每一行并不是：

```text
供应商 = 法律定义 + 解释 + 案例
```

---

## 105. 它只是一个向量

例如：

\[
[0.13,-0.7,\ldots]
\]

这些数字：

> 只有放进整个模型计算体系里才有意义。

---

## 106. 所以不能“打开 Embedding Matrix 直接读知识”

它不是：

> 人类可读词典。

Embedding 的意义：

> 分布在向量几何和后续 Weight 的交互中。

---

## 107. 一个重要认知

\[
\boxed{
Embedding
是模型参数的一部分，
不是外部知识库。
}
\]

RAG Vector Database：

> 又是另一回事。

---

# 十四、不要混淆 Embedding Matrix 和 Vector Database

## 108. LLM Token Embedding Matrix

存在模型里：

\[
E\in\mathbb R^{V\times d}
\]

作用：

> Token ID → 输入向量。

---

## 109. RAG Vector Database

保存的是：

> 文档 Chunk 的 Embedding。

例如：

```text
法规条款 A → vector
案例 B → vector
采购文件 C → vector
```

用于：

> 相似度检索。

---

## 110. 两个东西虽然都叫 Embedding

但职责完全不同。

一个：

\[
TokenInputRepresentation
\]

一个：

\[
DocumentRetrievalRepresentation
\]

---

## 111. 第六个核心心智模型

### 心智模型 ⑥：Embedding 是一种表示方式，不是某一个特定组件

你会看到：

- Token Embedding；
- Position Embedding；
- Sentence Embedding；
- Document Embedding；
- Image Embedding。

共同本质：

\[
\boxed{
Object
\rightarrow
Vector
}
\]

但训练目标和使用方式：

> 完全可能不同。

---

# 十五、向量空间里是否真的存在“语义轴”？

## 112. 有时可以发现某些可解释方向

例如某个方向：

> 对某类语义属性敏感。

但不要机械假设：

```text
维度 1 = 性别
维度 2 = 地域
维度 3 = 风险
```

真实表示通常更复杂。

---

## 113. 为什么分布式表示有优势？

因为一个概念可以：

> 复用多个维度。

一个维度也可以：

> 参与多个概念。

这种：

# Superposition

可以提高表示效率。

---

## 114. 但也增加可解释性难度

我们很难直接看：

\[
4096
\]

个数字，

然后说：

> “第 812 个数字表示资格限制。”

所以需要：

> Interpretability Methods。

---

# 十六、Vector Addition 有语义吗？

## 115. 在某些训练出来的空间中

可能出现近似：

\[
v_A-v_B+v_C
\]

对应某种语义关系。

这类现象曾经让 Word Embedding 很出名。

---

## 116. 但不要过度神化

向量算术：

> 不是自然语言的完整逻辑系统。

更不能认为：

> 所有法律推理都可以靠简单 Vector Addition 完成。

---

## 117. 真正现代 LLM 的能力来自

\[
Embedding
+
Attention
+
DeepTransformation
+
Training
\]

共同作用。

不是：

> 一个漂亮词向量空间就自动会推理。

---

# 十七、Embedding 和 Feature Engineering 的关系

## 118. 传统方式

我们可能人工写：

```text
是否包含“本市”
是否包含“注册”
是否包含“资本”
```

然后：

\[
X=[1,1,0,\ldots]
\]

---

## 119. Embedding 方式

不再手工规定：

> “本市”应该对应哪些 Feature。

而是给它：

\[
d
\]

维可训练参数。

---

## 120. Loss 决定这些维度怎样变化

于是：

\[
\boxed{
ManualFeatures
\rightarrow
LearnedRepresentation
}
\]

这正是第 3 阶段 Representation Learning 的具体实例。

---

# 十八、为什么 Dense Embedding 比 One-hot 更容易泛化？

## 121. 假设训练数据里见过

> “投标人必须……”

测试时出现：

> “供应商必须……”

如果两者完全独立 One-hot：

> 模型更难共享统计结构。

---

## 122. Dense Representation 可以共享

如果：

\[
e_{\text{投标人}}
\]

和：

\[
e_{\text{供应商}}
\]

在有用方向上接近，

后续同一个 Linear / Attention：

> 可以对它们做类似处理。

---

## 123. 这叫 Parameter Sharing 的一种效果

不同 Token：

> 不需要每一种组合都独立学习一遍。

共同向量空间让：

> 类似模式可以复用。

---

# 十九、高维空间也有风险：Curse of Dimensionality

## 124. 维度越来越高并非只有好处

高维空间中：

> 几何直觉会发生变化。

例如很多随机向量：

> 可能几乎彼此正交。

---

## 125. 数据也需要更多

如果希望在巨大空间里：

> 学出稳定结构，

通常需要：

> 足够训练数据和合理归纳偏置。

---

## 126. 所以 Hidden Size 不能无限增加

更大：

> Capacity 增加。

但同时：

- 参数增加；
- 显存增加；
- FLOPs 增加；
- 数据要求增加。

再次回到：

\[
\boxed{
Capacity\ vs\ Cost
}
\]

---

# 二十、Norm 和 Embedding 的关系

## 127. 一个向量不仅有方向，还有长度

例如：

\[
e=[1,2,3]
\]

Norm：

\[
\|e\|
=
\sqrt{1^2+2^2+3^2}
\]

即：

\[
\sqrt{14}
\]

---

## 128. 为什么向量长度也可能有意义？

模型训练可以利用：

> Direction。

也可以利用：

> Magnitude。

后续点积：

\[
a^Tb
=
\|a\|\|b\|\cos\theta
\]

同时受：

> 长度和方向影响。

---

## 129. 这就解释为什么第 7 阶段 Norm 很重要

如果 Hidden Vector 长度：

> 无限制增长，

点积可能：

> 变得非常大。

因此深层 Transformer：

> 需要控制尺度。

---

# 二十一、Embedding Initialization

## 130. Embedding Matrix 最开始也需要初始化

因为它本身就是 Weight。

例如：

\[
E_{ij}
\sim
\mathcal N(0,\sigma^2)
\]

或其它初始化。

---

## 131. 为什么不能所有 Token Embedding 都一样？

如果：

\[
E_1=E_2=\cdots=E_V
\]

输入层就无法区分：

> 不同 Token。

虽然后续其它机制可能引入信息，但这显然不是合理起点。

---

## 132. Token ID 的真正作用现在清楚了

ID：

\[
125
\]

不是拿来参加语义算术。

它只是告诉：

\[
\boxed{
取EmbeddingMatrix第125行
}
\]

---

# 二十二、Embedding 是否会“记住词频”？

## 133. 间接可能

高频 Token：

> 经历更多更新。

它们的向量统计性质：

> 可能受频率影响。

---

## 134. 这未必都是好事

语料中的频率偏差：

> 也可能被模型学进去。

例如某些机构、地区、模板过多：

> 会影响表示空间。

---

## 135. 这再次连接第一课的数据分布

\[
\boxed{
TrainingDistribution
\rightarrow
RepresentationGeometry
}
\]

Embedding Space：

> 不是纯粹客观语义地图。

它是训练数据和目标塑造出来的地图。

---

# 二十三、Embedding 也会学到偏差和捷径

## 136. 如果训练语料中

某个词总和：

> “高风险”

共同出现。

模型可能形成：

> 强相关方向。

---

## 137. 但相关不等于因果

第一课第 12 阶段又回来了：

\[
Correlation
\neq
Causation
\]

向量接近：

> 只表示模型学习到统计关系。

不是：

> 法律因果结论。

---

## 138. 所以 Vector Similarity 不能直接作为合规结论

例如某条采购条件与：

> 历史风险案例

Embedding 很相似。

可以作为：

> 检索线索。

不能自动推出：

> 当前条款违法。

仍需：

- 上下文；
- 法规；
- 事实；
- 必要性；
- 专家判断。

---

# 二十四、这正是 RAG 为什么需要“检索 + 推理”

## 139. Retriever

使用 Embedding：

\[
Query
\rightarrow
Vector
\]

与文档向量比较：

\[
Similarity
\]

找候选材料。

---

## 140. Generator / LLM

再读取：

> 实际文本证据。

进行：

> 上下文推理。

所以：

\[
\boxed{
EmbeddingSimilarity
=
CandidateRetrievalSignal
}
\]

而不是：

\[
FinalLegalJudgment
\]

---

# 二十五、Embedding 与分类头

## 141. 假设已经得到一个向量

\[
h\in\mathbb R^{768}
\]

分类器：

\[
z=Wh+b
\]

其中：

\[
W\in\mathbb R^{5\times768}
\]

可以输出 5 个风险类别 Logits。

---

## 142. 这里发生了什么？

Embedding / Hidden Representation：

> 把复杂输入放进语义空间。

Linear Head：

> 在这个空间上寻找任务相关方向。

---

## 143. 如果某个风险类别有一个 Weight Vector

\[
w_{risk}
\]

那么：

\[
z=w_{risk}^Th
\]

可以粗略理解成：

> 当前表示沿“风险判断方向”的匹配程度。

---

## 144. 又是 Dot Product

你会发现：

\[
\boxed{
DotProduct
}
\]

正在成为一个非常核心的统一语言。

Neuron：

\[
W^TX
\]

Similarity：

\[
a^Tb
\]

Classification：

\[
w^Th
\]

未来 Attention：

\[
QK^T
\]

---

# 二十六、为什么向量空间如此适合神经网络？

## 145. 因为向量可以连续变化

离散 Token：

> “供应商”和“投标人”只能说相同/不同。

向量：

> 可以表达部分相似。

---

## 146. 连续空间意味着可微

Embedding 参数：

\[
E
\]

可以做：

\[
GradientDescent
\]

微调一点点。

例如：

\[
0.512
\rightarrow
0.509
\]

这使学习成为可能。

---

## 147. 所以 Embedding 完成了一个关键桥梁

左边：

# Discrete Symbolic World

\[
TokenID
\]

右边：

# Continuous Differentiable World

\[
Vector
\]

Embedding 就是连接两者的：

\[
\boxed{
Bridge
}
\]

---

## 148. 第七个核心心智模型

### 心智模型 ⑦：Embedding 的深层意义是把离散语言送入一个可微、可学习的连续计算空间

这是为什么：

\[
Token
\]

能够进入：

\[
GradientDescent
\]

系统的根本原因之一。

---

# 二十七、一个完整政府采购输入例子

## 149. 假设文本

> “供应商必须在本市注册。”

Tokenizer 暂时给出：

```text
供应商
必须
在
本市
注册
。
```

---

## 150. Token IDs

假设：

\[
[12,88,5,203,91,2]
\]

注意：

> 这些数字本身没有语义大小关系。

---

## 151. Embedding Lookup

Embedding Matrix：

\[
E\in\mathbb R^{V\times d}
\]

如果：

\[
d=4
\]

那么得到：

\[
H_0=
\begin{bmatrix}
E_{12}\\
E_{88}\\
E_5\\
E_{203}\\
E_{91}\\
E_2
\end{bmatrix}
\]

Shape：

\[
\boxed{
(6,4)
}
\]

---

## 152. 如果 Batch = 32

并统一到：

\[
SequenceLength=128
\]

则输入 ID：

\[
(32,128)
\]

Embedding：

\[
\boxed{
(32,128,d)
}
\]

如果：

\[
d=4096
\]

则：

\[
\boxed{
(32,128,4096)
}
\]

---

## 153. 现在神经网络终于可以工作

因为每一个 Token：

> 已经从字符串变成了 4096 个浮点数。

后续可以做：

\[
Linear
\]

\[
Norm
\]

\[
Attention
\]

\[
MLP
\]

---

# 二十八、但现在有一个致命问题

假设句子：

> “供应商限制采购人。”

和：

> “采购人限制供应商。”

Token 集合可能高度相似。

如果只有 Token Embedding：

> 模型怎么知道顺序？

---

## 154. Embedding Lookup 本身不告诉顺序

例如：

\[
E_{\text{供应商}}
\]

无论放在：

> 第 1 位还是第 10 位，

基础 Token Embedding：

> 一样。

---

## 155. 所以还需要 Position Information

模型必须知道：

\[
Token_i
\]

位于：

\[
Position=i
\]

否则：

> 语言顺序信息无法完整表达。

---

## 156. 这会引出 Position Encoding

以后会学习：

- Absolute Position Embedding；
- Sinusoidal Position Encoding；
- RoPE；
- Relative Position；

等方法。

---

## 157. 但在进入 Position 前，还有一个更基础问题

今天我们假设：

```text
供应商
必须
在
本市
注册
```

已经被切成 Token。

现实问题是：

> **到底谁决定怎么切？**

---

## 158. “供应商”一定是一个 Token 吗？

不一定。

某个 Tokenizer 可能：

```text
供应
商
```

另一个可能：

```text
供应商
```

甚至可以切得：

> 更细。

---

## 159. “5000万元”呢？

可能：

```text
5000
万元
```

也可能：

```text
5
000
万
元
```

具体取决于：

# Vocabulary + Tokenizer Algorithm

---

## 160. 这为什么极其重要？

因为 Tokenization 直接影响：

\[
\boxed{
SequenceLength
}
\]

\[
\boxed{
DomainVocabularyEfficiency
}
\]

\[
\boxed{
Numbers
}
\]

\[
\boxed{
RareTerms
}
\]

\[
\boxed{
TrainingCost
}
\]

---

# 二十九、本阶段核心知识压缩

到这里，完整链条已经成为：

\[
\boxed{
Text
\rightarrow
Token
\rightarrow
TokenID
\rightarrow
EmbeddingLookup
\rightarrow
DenseVector
\rightarrow
NeuralNetwork
}
\]

其中：

\[
\boxed{
E\in\mathbb R^{V\times d}
}
\]

是 Embedding Matrix。

某 Token：

\[
i
\]

映射为：

\[
\boxed{
e_i=E[i]
}
\]

---

# 三十、本阶段最重要的七个核心心智模型

| 心智模型 | 核心认知 |
|---|---|
| **① Token ID 是地址，不是语义** | ID 只负责索引 Vocabulary / Embedding Row |
| **② Embedding 把离散身份变成连续几何位置** | 从符号空间进入 Vector Space |
| **③ Embedding 本质是可训练矩阵查表** | \(E\in\mathbb R^{V\times d},\ e_i=E[i]\) |
| **④ Embedding 的语义是训练塑造出来的** | 数据、Loss、上下文共同决定空间结构 |
| **⑤ Token Embedding 只是语义起点** | 真正上下文化表示由后续 Transformer 逐层形成 |
| **⑥ Embedding 是一类表示，不是单一产品** | Token、Sentence、Document、RAG Embedding 职责不同 |
| **⑦ Embedding 是离散语言与可微神经网络之间的桥梁** | Token 进入连续空间后才能通过梯度学习 |

---

# 三十一、如果只记三个公式

第一：

\[
\boxed{
E\in\mathbb R^{V\times d}
}
\]

第二：

\[
\boxed{
e_i=E[i]
}
\]

第三：

\[
\boxed{
cos(a,b)
=
\frac{a^Tb}
{\|a\|\|b\|}
}
\]

---

# 三十二、如果只记一句话

\[
\boxed{
Embedding不是给词“贴一个数字编号”，
而是让每个离散Token拥有一个可训练的高维坐标，
从而让语言进入神经网络可以计算和学习的连续空间。
}
\]

---

# 三十三、把第二课 1～8 阶段串起来

第 1 阶段：

\[
WX+b
\]

> 神经元如何组合数字。

第 2 阶段：

\[
Activation
\]

> 如何产生非线性。

第 3 阶段：

\[
HiddenRepresentation
\]

> 如何逐层形成表示。

第 4 阶段：

\[
Forward
\]

> 如何执行模型。

第 5 阶段：

\[
Backward
\]

> 如何计算参数责任。

第 6 阶段：

\[
Optimizer
\]

> 如何真正修改参数。

第 7 阶段：

\[
SignalStability
\]

> 为什么深网络能够稳定训练。

第 8 阶段：

\[
\boxed{
Embedding
}
\]

> 文字如何第一次进入数字向量空间。

现在第一次形成了：

\[
\boxed{
Language
\rightarrow
Vector
\rightarrow
DeepNeuralNetwork
}
\]

这一步非常重要。

---

# 三十四、第 8 阶段掌握标准

学完这一阶段，你应该能自然回答：

> 为什么不能直接把 Token ID 当连续数字喂给神经网络？

> One-hot 到底解决什么，又有什么根本问题？

> Dense Embedding 比 One-hot 多了什么能力？

> `nn.Embedding(100000,4096)` 到底保存了什么？

> 为什么它有 \(100000\times4096\) 个参数？

> Embedding Lookup 和 One-hot × Matrix 为什么数学上等价？

> Token Embedding 是固定参数还是可训练参数？

> Gradient 怎样回到 Embedding Matrix？

> 为什么高频 Token 往往获得更多训练信号？

> 为什么两个 Vector “相近”不是绝对客观事实？

> Dot Product 与 Cosine Similarity 有什么差别？

> Vector Direction 与 Magnitude 为什么要区分？

> Token Embedding 与 Contextual Hidden State 有什么区别？

> Token Embedding 和 RAG Document Embedding 为什么不是一回事？

> 为什么 Embedding Similarity 不能直接等价为法律合规结论？

> 为什么说 Embedding 是“离散符号世界”和“连续可微世界”的桥梁？

如果这些问题已经能够从机制上回答：

\[
\boxed{
第二课第8阶段真正建立起来了
}
\]

下一阶段非常自然：
