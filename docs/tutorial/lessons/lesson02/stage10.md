# 第二课 · 第 10 阶段：Position Encoding 与 RoPE
## “采购人限制供应商”和“供应商限制采购人”拥有相同 Token，Transformer 到底怎样知道谁在前、谁在后？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **没有 Position Information 的 Self-Attention 很难区分相同 Token 集合的不同顺序。**
2. **Positional Encoding 的任务是把“谁在前、谁在后、相距多远”注入模型表示。**
3. **RoPE 通过旋转 Query/Key 表示位置关系，使 Attention Score 同时感知内容与相对位置。**
4. **Max Context Length 是架构/训练/推理共同约束，不等于模型在整个最大长度上都同样可靠。**
5. **Long-Context Extension ≠ Free Extrapolation。扩展上下文窗口仍需要位置编码、训练分布和评测共同支持。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Token` | Token：模型实际处理的离散文本单元 |
| `RoPE` | RoPE：旋转位置编码，把位置信息融入注意力 |
| `Transformer` | Transformer：以注意力和前馈网络为核心的序列架构 |
| `Attention` | 注意力：根据内容相关性动态聚合信息 |
| `Embedding` | 嵌入：把离散 Token 映射到连续高维向量 |
| `Self-Attention` | 自注意力：同一序列内部各位置计算相关性并聚合 |
| `Causal Mask` | 因果掩码：阻止当前位置看到未来 Token |
| `Representation` | 表示：模型内部承载语义或特征的向量结构 |
| `Tokenizer` | 分词器：文本与 Token ID 之间的编码/解码组件 |
| `Loss` | 损失函数：把预测错误压缩成可优化的数值信号 |
| `Softmax` | Softmax：把一组分数转换成归一化权重 |
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

第 8、9 阶段，我们已经完成：

\[
\boxed{
RawText
\rightarrow
Tokenizer
\rightarrow
TokenIDs
\rightarrow
Embedding
}
\]

例如：

> “采购人限制供应商”

可能变成：

\[
[e_{\text{采购人}},e_{\text{限制}},e_{\text{供应商}}]
\]

现在把顺序倒过来：

> “供应商限制采购人”

得到：

\[
[e_{\text{供应商}},e_{\text{限制}},e_{\text{采购人}}]
\]

看起来似乎只是矩阵里的行换了位置。

问题来了：

> **Self-Attention 到底凭什么知道某个 Token 是第 1 个、第 2 个还是第 20000 个？**

今天我们要建立：

\[
\boxed{
TokenIdentity
+
PositionInformation
\rightarrow
ContextualRepresentation
}
\]

最后一路走到现代 LLM 中极其重要的：

\[
\boxed{
RoPE
=
Rotary\ Position\ Embedding
}
\]

---

## 1. 为什么语言绝对不能没有顺序？

看两句话：

> 采购人限制供应商。

> 供应商限制采购人。

词几乎完全一样。

但：

> 主体与客体完全反过来了。

因此：

\[
\boxed{
Words
+
Order
=
Meaning
}
\]

---

## 2. 再看一个采购例子

A：

> 注册资本不得低于5000万元。

B：

> 5000万元不得低于注册资本。

虽然 B 很奇怪，但它说明：

> Token 集合本身并不足以表达完整语义。

必须知道：

\[
\boxed{
谁出现在谁之前
}
\]

---

## 3. 第 8 阶段的 Token Embedding 只解决了什么？

它解决：

\[
\boxed{
Who\ am\ I?
}
\]

即：

> 我是“供应商”。

> 我是“采购人”。

> 我是“不得”。

但没有天然解决：

\[
\boxed{
Where\ am\ I?
}
\]

---

## 4. 所以我们至少需要两个信息源

第一个：

\[
\boxed{
Token\ Identity
}
\]

第二个：

\[
\boxed{
Position
}
\]

组合起来：

\[
\boxed{
Identity
+
Position
}
\]

才能形成真正的序列输入。

---

## 5. 第一个核心心智模型

### 心智模型 ①：Embedding 回答“我是谁”，Position 回答“我在哪里”

这两件事必须分开。

例如：

\[
e_{\text{供应商}}
\]

表示 Token 身份。

而：

\[
p_{37}
\]

表示：

> 它当前位于第 37 个位置。

---

# 一、为什么纯 Self-Attention 天然不懂顺序？

## 6. 先暂时忘掉 Position

假设输入：

\[
X=
\begin{bmatrix}
x_1\\
x_2\\
x_3
\end{bmatrix}
\]

Self-Attention 会计算：

\[
Q=XW_Q
\]

\[
K=XW_K
\]

\[
V=XW_V
\]

---

## 7. 然后计算关系

\[
QK^T
\]

再：

\[
Softmax
\]

最后：

\[
Attention(Q,K,V)
\]

---

## 8. 注意这里发生了什么

Attention 会问：

> 每个 Token 与其它 Token 有多匹配？

但如果没有任何 Position 信息：

> 它没有天然的“第几个 Token”概念。

---

## 9. 一个简单思维实验

输入：

\[
[A,B,C]
\]

如果我们把顺序统一置换成：

\[
[C,A,B]
\]

同时 Q、K、V 也跟着完全相同地重新排列，

Self-Attention 的结果：

> 也会按照相同方式重新排列。

---

## 10. 这叫 Permutation Equivariance

在不加位置结构的标准 Self-Attention 中，可以粗略写成：

\[
\boxed{
Attention(PX)
=
P\,Attention(X)
}
\]

其中：

\[
P
\]

是一个置换矩阵。

---

## 11. 这句话到底什么意思？

它意味着：

> Attention 知道“这些 Token 之间有什么关系”。

但单凭这一机制：

> 并不知道“它们原本应该按什么天然顺序排列”。

---

## 12. 注意一个重要技术细节

Decoder-only LLM 还有：

\[
CausalMask
\]

它规定：

> 当前 Token 不能看未来 Token。

Causal Mask 本身已经引入了一定：

> 前后结构。

但：

\[
\boxed{
CausalMask
\neq
PositionEncoding
}
\]

它们解决的问题不同。

---

## 13. Causal Mask 回答什么？

它回答：

\[
\boxed{
Who\ may\ I\ attend\ to?
}
\]

例如第 10 个位置：

> 只能看 1～10。

---

## 14. Position Encoding 回答什么？

它回答：

\[
\boxed{
Where\ are\ these\ tokens?
}
\]

例如：

> Token A 和 Token B 相隔 1 个位置还是 1000 个位置？

这是另一件事。

---

## 15. 第二个核心心智模型

### 心智模型 ②：Mask 管“可见性”，Position 管“位置关系”

这两个东西以后一定不要混淆：

\[
\boxed{
Mask
=
AccessControl
}
\]

\[
\boxed{
Position
=
OrderGeometry
}
\]

---

# 二、最直观的方法：Position ID

## 16. 假设一句话有 5 个 Token

那么可以给它们编号：

\[
[0,1,2,3,4]
\]

这就是：

# Position IDs

---

## 17. 例如

```text
供应商   0
必须     1
在       2
本市     3
注册     4
```

所以现在每个 Token 有两个身份：

```text
Token ID
Position ID
```

---

## 18. Token ID 与 Position ID 完全不是一回事

例如：

\[
TokenID=5832
\]

可能表示：

> “供应商”。

而：

\[
PositionID=37
\]

只表示：

> 它当前位于第 37 个序列位置。

---

## 19. Token ID 会查哪里？

查：

\[
TokenEmbeddingMatrix
\]

得到：

\[
e_i
\]

---

## 20. Position ID 可以怎么用？

最简单方案：

> 也查一张 Position Embedding Matrix。

得到：

\[
p_i
\]

然后：

\[
\boxed{
h_i=e_i+p_i
}
\]

---

# 三、Learned Absolute Position Embedding

## 21. 假设最大长度

\[
L_{max}=4096
\]

Hidden Size：

\[
D=768
\]

那么我们可以创建：

\[
P\in\mathbb R^{4096\times768}
\]

---

## 22. 每个 Position 都有自己的向量

位置 0：

\[
P_0
\]

位置 1：

\[
P_1
\]

……

位置 4095：

\[
P_{4095}
\]

---

## 23. Token Embedding

假设：

\[
e_{\text{供应商}}
\]

是：

\[
768
\]

维。

Position：

\[
p_{37}
\]

也是：

\[
768
\]

维。

---

## 24. 直接相加

\[
\boxed{
h
=
e_{\text{供应商}}
+
p_{37}
}
\]

于是 Hidden State 同时包含：

> Token 身份。

以及：

> 位置身份。

---

## 25. 为什么可以直接相加？

因为二者：

\[
Shape=(768,)
\]

一致。

加法后：

> 仍然是 768 维。

所以无需让 Hidden Size 翻倍。

---

## 26. 第三个核心心智模型

### 心智模型 ③：最简单的 Position Encoding，就是把“内容向量”和“位置向量”放进同一个表示空间

\[
\boxed{
InputRepresentation
=
TokenEmbedding
+
PositionEmbedding
}
\]

这是非常经典的设计。

---

## 27. Position Embedding 是否可训练？

如果是：

# Learned Position Embedding

那么：

\[
P
\]

本身也是 Parameter。

训练：

\[
Loss
\rightarrow
Backward
\rightarrow
P
\]

---

## 28. 这意味着位置 37 的向量也是“学出来的”

不是我们人工告诉模型：

> 第 37 位是什么意思。

模型通过训练：

> 自己调整 \(P_{37}\)。

---

## 29. 经典绝对位置有什么优点？

简单。

直观。

实现容易。

模型可以：

> 直接为每一个位置学一套表示。

---

## 30. 但马上出现第一个问题

如果只训练：

\[
0\sim4095
\]

这些 Position，

突然推理输入：

\[
Position=5000
\]

怎么办？

---

## 31. 原来的 Position Table 根本没有第 5000 行

这就是 Learned Absolute Position Embedding 的一个明显限制：

\[
\boxed{
MaxPosition
}
\]

通常是预先固定的。

---

## 32. 可以把矩阵扩长吗？

技术上可以增加新 Row。

但这些新 Row：

> 没训练过。

所以：

\[
\boxed{
增加PositionTable长度
\neq
模型自动学会更长Context
}
\]

---

## 33. 这和新增 Token 很像

新增 Token：

> 新 Embedding 没学过。

新增 Position：

> 新 Position Embedding 也没学过。

---

# 四、绝对位置还有一个更深的问题

## 34. 假设两个 Token

A 在：

\[
100
\]

B 在：

\[
101
\]

模型真正关心的可能是：

\[
101-100=1
\]

即：

> 它们相邻。

---

## 35. 换一个位置

A：

\[
3000
\]

B：

\[
3001
\]

关系仍然：

\[
1
\]

---

## 36. 但是 Absolute Position Embedding 首先编码的是

\[
100
\]

和：

\[
101
\]

或者：

\[
3000
\]

和：

\[
3001
\]

模型还需要：

> 自己从绝对位置中推导相对距离。

---

## 37. 对语言来说相对位置非常重要

例如：

> “不得”离“低于”只有 1～2 个 Token。

比：

> “不得”距离某个完全无关条款 3000 Token

通常更有直接语义关系。

---

## 38. 所以 Position 有两个层面

\[
\boxed{
AbsolutePosition
}
\]

以及：

\[
\boxed{
RelativePosition
}
\]

---

# 五、Sinusoidal Position Encoding

## 39. 原始 Transformer 提出了一种不需要学习 Position Table 的方法

就是：

# Sinusoidal Position Encoding

正弦位置编码。

---

## 40. 核心思想

对于每一个位置：

\[
pos
\]

构造一组：

\[
sin
\]

和：

\[
cos
\]

值。

---

## 41. 经典公式

对偶数维：

\[
\boxed{
PE(pos,2i)
=
\sin
\left(
\frac{pos}
{10000^{2i/d}}
\right)
}
\]

---

## 42. 奇数维

\[
\boxed{
PE(pos,2i+1)
=
\cos
\left(
\frac{pos}
{10000^{2i/d}}
\right)
}
\]

其中：

\[
d
\]

是 Hidden Dimension。

---

## 43. 看起来为什么这么怪？

关键不是：

> 10000 这个数字本身有神秘意义。

核心是：

> 不同维度使用不同频率。

---

## 44. 某些维度变化很快

位置：

\[
1\rightarrow2
\]

数值：

> 就变化明显。

它们可以帮助表示：

> 精细局部位置。

---

## 45. 某些维度变化很慢

可能位置从：

\[
1\rightarrow100
\]

只发生较缓慢变化。

它们可以表达：

> 较粗尺度的位置变化。

---

## 46. 可以把它理解成很多“钟表”

一个钟：

> 转得很快。

另一个：

> 转得慢一点。

再一个：

> 转得更慢。

多个钟的读数组合起来：

> 表示当前位置。

---

## 47. 第四个核心心智模型

### 心智模型 ④：Sinusoidal Encoding 用“多种频率的周期信号”共同表示位置

这和只给位置一个数字：

\[
37
\]

完全不同。

它把：

\[
37
\]

展开成：

> 很多不同时间尺度上的相位状态。

---

## 48. 为什么要 Sin 和 Cos 配对？

因为：

\[
sin
\]

和：

\[
cos
\]

共同可以表达一个角度。

例如二维圆：

\[
(\cos\theta,\sin\theta)
\]

表示：

> 圆周上的位置。

---

## 49. 所以你可以把每两维看成一个小圆

Position 增长时：

> 向量在这个二维平面里旋转。

不同维度对：

> 旋转速度不同。

---

## 50. 这句话要记住

因为到了 RoPE：

> 我们会直接把“旋转”这件事应用到 Q、K。

---

# 六、为什么 Sinusoidal 能表达相对位移？

## 51. 三角恒等式告诉我们

\[
\sin(a+b)
\]

可以用：

\[
\sin a,\cos a,\sin b,\cos b
\]

表示。

---

## 52. 例如

\[
\sin(a+b)
=
\sin a\cos b+\cos a\sin b
\]

---

## 53. 这意味着

从位置：

\[
pos
\]

移动：

\[
\Delta
\]

到：

\[
pos+\Delta
\]

对应的编码之间：

> 存在结构化线性关系。

---

## 54. 所以它比完全独立的 Learned Position Row

天然多了一点：

\[
\boxed{
RelativeShiftStructure
}
\]

---

## 55. 但是 Sinusoidal Encoding 仍然通常是

把：

\[
PE(pos)
\]

加到：

\[
TokenEmbedding
\]

上。

即：

\[
h_i=e_i+PE(i)
\]

---

# 七、为什么后来越来越强调 Relative Position？

## 56. 对很多语言关系而言

真正重要的不是：

> “这个 Token 是第 1837 个。”

而是：

> “它距离当前 Token 是 -2、+4 还是 +1000。”

---

## 57. 例如

> “不得低于5000万元”

“不得”与“低于”之间的：

\[
RelativeDistance
\]

对理解这一局部结构很重要。

---

## 58. 又例如法律文本

> “符合前款第（三）项规定的供应商……”

“前款”：

> 本身就是一种相对引用概念。

---

## 59. 因此一些模型直接把相对位置放进 Attention

例如 Attention Score：

\[
score_{ij}
\]

除了内容关系：

\[
q_i^Tk_j
\]

还加：

\[
b_{i-j}
\]

---

## 60. 一个抽象形式

\[
\boxed{
score_{ij}
=
\frac{q_i^Tk_j}{\sqrt d}
+
b_{i-j}
}
\]

其中：

\[
b_{i-j}
\]

只依赖：

> 相对距离。

---

## 61. 这样位置 100 与 101

和：

位置 3000 与 3001

都拥有：

\[
i-j=-1
\]

相同的相对位置结构。

---

# 八、Relative Position Bias

## 62. 一个思路是为不同距离学习 Bias

例如：

\[
-1,-2,-3,\ldots
\]

各有参数。

---

## 63. 但距离可能非常大

不可能为：

\[
-100000
\]

到：

\[
+100000
\]

每个距离都无限建参数。

---

## 64. 所以经常做 Bucket

例如：

```text
距离 1
距离 2
距离 3
距离 4–7
距离 8–15
距离 16–31
...
```

近距离：

> 分得细。

远距离：

> 分得粗。

---

## 65. 这符合语言直觉

距离：

\[
1
\]

和：

\[
2
\]

可能差别很大。

但：

\[
10001
\]

和：

\[
10002
\]

通常没必要拥有完全独立 Position Parameter。

---

# 九、ALiBi：另一个重要思路

## 66. 你以后可能看到

# ALiBi

Attention with Linear Biases。

---

## 67. 它不一定给 Token 添加 Position Embedding

而是直接在 Attention Score 中加入：

> 与距离相关的线性 Bias。

---

## 68. 非常简化地想

\[
score_{ij}
=
q_i^Tk_j
-
m|i-j|
\]

不同 Head：

> 可以使用不同斜率。

---

## 69. 核心思想

距离越远：

> Attention Score 获得某种位置惩罚。

这使模型获得：

> 距离感。

---

## 70. 我们今天不会深入 ALiBi

但要建立统一认知：

\[
\boxed{
PositionInformation
不一定非要“加到Embedding上”
}
\]

它也可以进入：

> Attention Score。

甚至：

> Q/K 的几何结构。

而后者就是 RoPE。

---

# 十、终于进入 RoPE

## 71. RoPE 全称

# Rotary Position Embedding

中文通常叫：

# 旋转位置编码

---

## 72. 它最关键的思想不是

> 为位置单独创造一个向量然后加到 Token 上。

而是：

\[
\boxed{
根据Position旋转Q和K
}
\]

---

## 73. 这句话第一次看很奇怪

“供应商”明明是文字。

为什么：

> 位置会变成旋转？

答案在高维向量几何里。

---

# 十一、先从二维旋转开始

## 74. 一个二维向量

\[
x=
\begin{bmatrix}
x_1\\
x_2
\end{bmatrix}
\]

旋转角度：

\[
\theta
\]

---

## 75. 二维旋转矩阵

\[
\boxed{
R(\theta)
=
\begin{bmatrix}
\cos\theta&-\sin\theta\\
\sin\theta&\cos\theta
\end{bmatrix}
}
\]

---

## 76. 旋转以后

\[
x'
=
R(\theta)x
\]

---

## 77. 例如

\[
x=
\begin{bmatrix}
1\\
0
\end{bmatrix}
\]

如果：

\[
\theta=90^\circ
\]

得到：

\[
x'
=
\begin{bmatrix}
0\\
1
\end{bmatrix}
\]

---

## 78. 一个非常重要性质

旋转：

> 不改变向量长度。

即：

\[
\boxed{
\|R(\theta)x\|
=
\|x\|
}
\]

---

## 79. 它改变的是

\[
\boxed{
Direction
}
\]

也就是说：

> 位置可以通过改变方向来编码，而不必改变向量整体尺度。

---

# 十二、Position 怎么变成旋转角度？

## 80. 假设 Token 位于位置

\[
m
\]

我们给它一个基础角速度：

\[
\theta
\]

那么旋转角度：

\[
\boxed{
m\theta
}
\]

---

## 81. Position = 1

旋转：

\[
\theta
\]

---

## 82. Position = 2

旋转：

\[
2\theta
\]

---

## 83. Position = 100

旋转：

\[
100\theta
\]

所以位置：

> 直接变成旋转相位。

---

# 十三、高维向量怎么旋转？

## 84. 假设 Head Dimension

\[
d=8
\]

我们把它两两分组：

\[
(x_0,x_1)
\]

\[
(x_2,x_3)
\]

\[
(x_4,x_5)
\]

\[
(x_6,x_7)
\]

---

## 85. 每一对维度

都可以看成：

> 一个二维平面。

然后：

> 独立做旋转。

---

## 86. 但每个二维平面的旋转速度不同

定义：

\[
\theta_i
\]

不同 \(i\)：

> 使用不同频率。

---

## 87. 一种典型形式

\[
\boxed{
\theta_i
=
B^{-2i/d}
}
\]

其中：

\[
B
\]

是 RoPE Base。

---

## 88. 经典设计中常见

\[
B=10000
\]

但现代模型：

> 可以使用不同 Base 和不同 Scaling 方法。

所以不要把：

\[
10000
\]

理解成 RoPE 的永恒固定常数。

---

## 89. 低编号维度

\[
\theta_i
\]

通常较大。

于是：

> 随位置变化旋转更快。

---

## 90. 高编号维度

频率更低。

于是：

> 旋转更慢。

---

## 91. 这又出现了多尺度位置表示

与 Sinusoidal Encoding 很像：

> 快频率负责精细变化。

> 慢频率负责长尺度变化。

---

# 十四、RoPE 对 Query 做什么？

## 92. 原 Query

位置：

\[
m
\]

内容向量：

\[
q_m
\]

RoPE 后：

\[
\boxed{
\tilde q_m
=
R_m q_m
}
\]

---

## 93. 这里

\[
R_m
\]

就是：

> 根据位置 \(m\) 构造的多频率旋转矩阵。

---

## 94. Key 也一样

位置：

\[
n
\]

原 Key：

\[
k_n
\]

RoPE 后：

\[
\boxed{
\tilde k_n
=
R_n k_n
}
\]

---

## 95. 然后 Attention 看什么？

仍然计算：

\[
\tilde q_m^T\tilde k_n
\]

---

# 十五、RoPE 最漂亮的一步来了

## 96. 代入

\[
\tilde q_m^T\tilde k_n
=
(R_mq_m)^T(R_nk_n)
\]

---

## 97. 转置展开

\[
=
q_m^TR_m^TR_nk_n
\]

---

## 98. 对旋转矩阵

\[
R_m^T
=
R_{-m}
\]

因此：

\[
R_m^TR_n
=
R_{n-m}
\]

---

## 99. 所以

\[
\boxed{
\tilde q_m^T\tilde k_n
=
q_m^T
R_{n-m}
k_n
}
\]

这就是 RoPE 最重要的公式之一。

---

## 100. 看见关键了吗？

Attention Score 中的位置影响最终依赖：

\[
\boxed{
n-m
}
\]

也就是：

# Relative Position

---

## 101. 这非常漂亮

我们使用的是：

> 每个 Token 的绝对位置 \(m,n\)。

但两者做 Dot Product 时：

> 自然出现相对距离 \(n-m\)。

---

## 102. 第五个核心心智模型

### 心智模型 ⑤：RoPE 用“绝对位置旋转”，让 Q·K 的匹配天然呈现“相对位置关系”

一句话：

\[
\boxed{
AbsolutePhase
\rightarrow
RelativeAttentionGeometry
}
\]

---

# 十六、一个简单二维例子

## 103. 假设 Query 位于

\[
m=10
\]

Key 位于：

\[
n=12
\]

那么：

\[
n-m=2
\]

---

## 104. 如果二者一起整体往后移动

Query：

\[
100
\]

Key：

\[
102
\]

依然：

\[
n-m=2
\]

---

## 105. 因此它们的 Position Relationship

仍然表现出：

> 相同相对距离结构。

这非常适合语言。

---

# 十七、为什么 RoPE 特别适合 Attention？

## 106. Attention 的核心本来就是

\[
QK^T
\]

即：

> Query 与 Key 的向量匹配。

---

## 107. RoPE 没有另开一套大型位置网络

而是直接：

> 修改 Q/K 的方向。

于是位置关系：

> 进入 Dot Product 本身。

---

## 108. 所以 Content 与 Position

在 Attention Score 中变成：

\[
\boxed{
ContentMatch
\times/\!+\ PositionGeometry
}
\]

不是简单两条完全独立通道。

---

# 十八、为什么通常旋转 Q 和 K，而不是 V？

## 109. Attention 的权重由

\[
QK^T
\]

决定。

因此：

> Q/K 决定“看谁”。

---

## 110. V 负责什么？

V 是：

\[
\boxed{
What\ information\ to\ retrieve
}
\]

即：

> 真正被聚合的内容。

---

## 111. 所以标准 RoPE 设计通常

对：

\[
Q,K
\]

做位置旋转。

而：

\[
V
\]

通常不做相同旋转。

---

## 112. 可以记成

\[
\boxed{
Q/K
=
Addressing
}
\]

\[
\boxed{
V
=
Payload
}
\]

这是很好的 Attention 直觉。

---

# 十九、RoPE 不改变 Q/K 的长度吗？

## 113. 理想旋转矩阵满足

\[
R^TR=I
\]

因此：

\[
\|Rq\|=\|q\|
\]

---

## 114. 所以 RoPE 核心改变

> 方向。

而不是任意放大或缩小：

> 向量 Norm。

这对数值稳定也很优雅。

---

# 二十、Complex Number 视角

## 115. RoPE 还有一个非常漂亮的理解方式

把两个维度：

\[
(x_{2i},x_{2i+1})
\]

看成一个复数：

\[
z=x_{2i}+jx_{2i+1}
\]

---

## 116. 旋转等于乘

\[
\boxed{
e^{jm\theta_i}
}
\]

所以：

\[
z'
=
z e^{jm\theta_i}
\]

---

## 117. Position 就变成

# Phase

相位。

这也是为什么 RoPE 的本质非常像：

> 多频率相位编码。

---

# 二十一、为什么不同频率很关键？

## 118. 如果所有维度旋转速度都一样

不同位置：

> 容易产生周期性混淆。

---

## 119. 多个频率组合

让一个 Position：

> 同时在很多“钟表”上留下不同相位。

这提高了：

> 位置可区分性。

---

## 120. 你可以粗略想象

第一对维度：

> 秒针。

第二对：

> 分针。

第三对：

> 时针。

更多维度：

> 更慢的长周期钟。

---

# 二十二、RoPE Shape 怎么看？

## 121. 假设 Multi-Head Attention

Hidden Size：

\[
D=4096
\]

Head 数：

\[
32
\]

那么：

\[
HeadDim
=
\frac{4096}{32}
=
128
\]

---

## 122. 每个 Head 的 Q/K

Shape 类似：

\[
(B,H,S,d_h)
\]

即：

\[
(B,32,S,128)
\]

---

## 123. RoPE 通常作用在哪个维度？

作用在：

\[
d_h
\]

里的维度对。

例如：

\[
128
\]

维：

> 两两旋转。

---

## 124. 也有模型只对部分维度使用 RoPE

例如：

\[
RotaryDim<HeadDim
\]

这取决于：

> 具体架构。

所以看到实现时：

> 不要假定永远 100% Head Dimension 都旋转。

---

# 二十三、Position ID 如何生成 RoPE？

## 125. 位置序列

\[
[0,1,2,\ldots,S-1]
\]

---

## 126. 对每个频率

\[
\theta_i
\]

计算：

\[
m\theta_i
\]

---

## 127. 然后生成

\[
\cos(m\theta_i)
\]

和：

\[
\sin(m\theta_i)
\]

---

## 128. 所以实际代码经常缓存

\[
CosCache
\]

\[
SinCache
\]

避免：

> 每次重复计算。

---

# 二十四、一个常见 RoPE 实现直觉

## 129. 对某个向量

\[
x
\]

可以构造一个：

\[
rotate\_half(x)
\]

把：

\[
(x_0,x_1,x_2,x_3)
\]

变成类似：

\[
(-x_1,x_0,-x_3,x_2)
\]

---

## 130. 然后

\[
\boxed{
x_{rope}
=
x\cos\theta
+
rotate\_half(x)\sin\theta
}
\]

本质就是：

> 二维旋转矩阵的向量化实现。

---

# 二十五、RoPE 和 Sinusoidal Position Encoding 有什么关系？

## 131. 两者都使用

\[
sin
\]

与：

\[
cos
\]

以及：

> 多频率结构。

---

## 132. 但应用方式不同

Sinusoidal：

\[
\boxed{
TokenEmbedding
+
PositionVector
}
\]

---

## 133. RoPE

更像：

\[
\boxed{
Rotate(Q,position)
}
\]

\[
\boxed{
Rotate(K,position)
}
\]

---

## 134. 所以它不是简单

> “在 Embedding 上加一串正弦数字”。

这是非常重要的区别。

---

# 二十六、RoPE 与绝对 Position Embedding 的核心差异

## 135. Learned Absolute

位置 100：

> 有一个专属向量。

位置 101：

> 另一个专属向量。

---

## 136. RoPE

位置：

\[
m
\]

首先决定：

> 一组旋转角。

---

## 137. 它把 Position 作用到

\[
Q,K
\]

的几何关系里。

最终 Attention：

> 自然反映相对位移。

---

# 二十七、为什么现代 LLM 很喜欢 RoPE？

## 138. 几个主要优点

它：

- 不需要巨大的位置 Embedding Table；
- 与 Attention Dot Product 深度整合；
- 有漂亮的相对位置性质；
- 实现高效；
- 可以使用各种 Scaling 技术扩展 Context。

---

## 139. 但一定不要得到错误结论

\[
\boxed{
用了RoPE
\neq
无限Context
}
\]

RoPE 也有：

> 长度外推问题。

---

# 二十八、为什么长 Context 会成为问题？

## 140. 假设模型训练时最多看过

\[
4096
\]

Token。

那么训练过程中 Position：

\[
m
\]

主要位于：

\[
0\sim4095
\]

---

## 141. 推理突然给

\[
m=50000
\]

RoPE 仍然可以数学上算：

\[
\sin(50000\theta)
\]

\[
\cos(50000\theta)
\]

---

## 142. 但数学能算不等于模型训练过这种分布

模型参数从未充分学习：

> 这么大的相位组合。

所以：

\[
\boxed{
Computable
\neq
Reliable
}
\]

---

## 143. 这和第一课的 OOD 完全一致

训练 Position Distribution：

\[
P_{train}(position)
\]

与部署：

\[
P_{deploy}(position)
\]

差异太大。

就会形成：

\[
\boxed{
PositionOOD
}
\]

---

# 二十九、RoPE 为什么可能在超长位置变困难？

## 144. 不同频率会不断旋转

位置越来越大时：

> 高频维度已经转过很多圈。

---

## 145. 模型训练只见过某个角度分布范围

直接外推：

> 可能让 Attention 几何关系进入陌生区域。

---

## 146. 所以长 Context 不只是

> “显存够不够”。

还包括：

\[
\boxed{
PositionalGeneralization
}
\]

---

# 三十、Position Interpolation

## 147. 一个重要思想叫

# Position Interpolation

简称：

# PI

---

## 148. 假设模型原来支持

\[
L=4096
\]

现在希望：

\[
L'=16384
\]

扩展：

\[
4\times
\]

---

## 149. 与其直接给位置 16383

不如把新 Position：

> 压缩回原训练范围。

例如：

\[
\boxed{
m_{scaled}
=
\frac{m}{4}
}
\]

---

## 150. 那么新位置

\[
16383
\]

映射到大约：

\[
4095.75
\]

仍位于：

> 原来熟悉的 Position Scale。

---

## 151. 直觉是什么？

把一条：

\[
16K
\]

长的尺子，

压缩到原来的：

\[
4K
\]

位置空间。

---

## 152. 代价是什么？

原本位置：

\[
1
\]

与：

\[
2
\]

现在间距也被压缩。

所以：

> 局部位置分辨率发生变化。

---

# 三十一、为什么不能只粗暴统一压缩？

## 153. RoPE 不同维度使用不同频率

高频维度：

> 更关注局部差异。

低频维度：

> 更适合长尺度结构。

统一缩放：

> 不一定对所有频率都最优。

---

## 154. 所以后来出现更多 Scaling 方法

例如：

- NTK-aware scaling；
- Dynamic NTK scaling；
- YaRN；
- 各类 frequency-aware scaling。

---

## 155. 现在不需要背公式

真正要理解的是：

\[
\boxed{
LongContextScaling
=
调整RoPE频率/位置映射，
让更长位置尽量落入模型可泛化的几何区域
}
\]

---

# 三十二、NTK-aware Scaling 的直觉

## 156. 不简单把所有频率

> 一刀切缩放。

而是考虑：

> 不同 RoPE 频率对短距离和长距离关系的贡献不同。

---

## 157. 目标之一

尽量：

> 保住短距离分辨率。

同时：

> 扩展长距离表示能力。

---

# 三十三、YaRN 的宏观理解

## 158. YaRN 属于

> 长 Context RoPE Scaling 方法家族。

它会更精细地处理：

> 不同频率区间。

并配合：

> Attention Scale 等调整。

---

## 159. 现在不要陷入算法名词竞赛

以后看到任何 Context Extension 方法，

先问三个问题：

\[
\boxed{
Position怎么映射？
}
\]

\[
\boxed{
Frequency怎么改变？
}
\]

\[
\boxed{
有没有LongContext继续训练？
}
\]

---

# 三十四、长上下文最关键的现实问题

## 160. 一个模型配置写着

\[
128K
\]

Context。

这只能说明：

> 系统允许你输入那么多 Token。

---

## 161. 它不自动证明

模型在：

\[
128K
\]

任何位置都：

> 同样可靠。

---

## 162. 例如信息放在

开头：

> 能找到。

结尾：

> 能找到。

中间：

> 可能性能下降。

这类现象经常被称为：

# Lost in the Middle

---

## 163. 所以 Context Length 不是单一数字能力

更应该测：

\[
\boxed{
Performance
\times
Position
\times
Distance
}
\]

---

## 164. 第六个核心心智模型

### 心智模型 ⑥：Context Window 是容量上限，Long-Context Ability 是需要独立评测的能力

就像：

\[
GPU\ Memory
\]

够放一个模型，

不代表：

> 模型质量就好。

同样：

\[
128K\ Context
\]

不代表：

> 128K 范围内理解能力均匀。

---

# 三十五、政府采购长文档为什么尤其需要这个认知？

## 165. 一份采购文件可能有

- 采购需求；
- 资格条件；
- 技术参数；
- 商务要求；
- 评分办法；
- 合同条款；
- 附件。

总长度可能：

\[
数万Token
\]

---

## 166. 一个风险点可能在第 3000 Token

相关解释却在：

\[
25000
\]

Token 后。

---

## 167. 模型需要跨越

\[
22000
\]

Token

建立关系。

这就不是：

> 单纯局部语义问题。

---

## 168. 例如

前文：

> “供应商须在项目所在地设置服务机构。”

后文：

> “现场响应仅适用于重大故障情形，普通服务均可远程完成。”

二者结合后：

> 风险判断可能改变。

---

## 169. 所以政府采购模型必须评测

\[
\boxed{
LongRangeEvidenceIntegration
}
\]

而不是：

> 只测 500 Token 小片段。

---

# 三十六、Position Encoding 能解决所有长文档问题吗？

## 170. 不能

Position Encoding 只是：

> 让模型知道 Token 的位置关系。

它不保证：

> 模型一定会正确找到远距离证据。

---

## 171. 还取决于

- Attention Architecture；
- Training Data；
- Long-context training；
- Model capacity；
- Retrieval strategy；
- Document structure；
- Prompt design。

---

## 172. 所以对于超长采购文件

仍然可能需要：

\[
\boxed{
LongContext
+
RAG
+
StructuredParsing
}
\]

共同工作。

---

# 三十七、Position 与 RAG 是什么关系？

## 173. RAG 的一个作用

不是强迫模型：

> 一次把 300 页文件全部精细记住。

而是先：

> 找到最相关区域。

---

## 174. 然后送入较短 Context

比如：

\[
3000\sim10000\ Tokens
\]

模型处理起来：

> 可能更可靠、更便宜。

---

## 175. 所以即使模型支持

\[
1M\ Tokens
\]

RAG 仍然可能有价值。

因为：

\[
\boxed{
CanFit
\neq
ShouldAlwaysFitEverything
}
\]

---

# 三十八、Causal Mask 再和 RoPE 区分一次

## 176. Decoder-only LLM

位置：

\[
i
\]

通常只能看：

\[
j\leq i
\]

---

## 177. 这是通过

\[
CausalMask
\]

实现。

---

## 178. RoPE 则告诉 Attention

在允许看的这些 Token 里面：

> 彼此相隔多远、相对在哪里。

---

## 179. 所以

\[
\boxed{
CausalMask
=
未来不可见
}
\]

\[
\boxed{
RoPE
=
位置几何
}
\]

---

# 三十九、Attention Mask 和 Position ID 也不要混淆

## 180. Attention Mask

可能表示：

> 这个位置是不是 PAD。

或者：

> 能不能互相 Attention。

---

## 181. Position ID

表示：

> 这个有效 Token 使用哪个位置编号。

两者：

> 可以不同。

---

# 四十、Padding 时 Position 怎么处理？

## 182. 假设两个样本

A 长度：

\[
3
\]

B 长度：

\[
5
\]

右侧 Padding：

```text
A A A PAD PAD
B B B B   B
```

---

## 183. 有效位置可以是

A：

\[
0,1,2
\]

B：

\[
0,1,2,3,4
\]

PAD：

> 由 Mask 排除。

---

## 184. 左侧 Padding 会更有趣

```text
PAD PAD A A A
B   B   B B B
```

如果直接按 Tensor Column 编：

A 会得到：

\[
2,3,4
\]

---

## 185. 但有些实现希望有效 Token 仍然使用

\[
0,1,2
\]

因此：

> Position IDs 往往需要根据 Attention Mask 重新计算。

---

## 186. 具体行为取决于模型实现

所以做推理框架兼容时：

\[
\boxed{
不要自己猜PositionID规则
}
\]

应该遵循：

> 模型原实现。

---

# 四十一、Packed Training

## 187. 训练时为了减少 Padding

可能把多个短文档拼成一条长序列。

例如：

```text
文档A | 文档B | 文档C
```

这叫：

# Sequence Packing

---

## 188. 这样 GPU 利用率更高

因为：

> 少浪费 PAD。

---

## 189. 但马上有问题

文档 A 结尾：

> 不应该偷看文档 B。

---

## 190. 所以光重置 Position ID 不够

必须同时处理：

\[
\boxed{
AttentionBoundary
}
\]

例如使用：

> Block-diagonal Attention Mask。

---

## 191. 这是非常重要的工程点

\[
\boxed{
PositionReset
\neq
DocumentIsolation
}
\]

---

# 四十二、KV Cache 与 Position

## 192. LLM 生成时

第一个 Token：

\[
Position=0
\]

第二个：

\[
1
\]

一路生成：

\[
t
\]

---

## 193. 每次如果把过去所有 Token 重新算一遍

极其浪费。

所以使用：

# KV Cache

缓存以前的 Key、Value。

---

## 194. RoPE 与 KV Cache 紧密相关

过去的 Key：

> 已经对应过去的位置完成了 RoPE 处理。

然后被缓存。

---

## 195. 新 Token 到来

只需计算：

\[
q_t
\]

以及：

\[
k_t,v_t
\]

其中：

\[
q_t,k_t
\]

使用：

\[
Position=t
\]

的旋转。

---

## 196. 然后新 Query

可以与缓存的：

\[
K_{0:t}
\]

计算 Attention。

---

## 197. 所以 Position Counter 绝对不能乱

如果模型生成到：

\[
t=500
\]

你却错误给新 Token：

\[
Position=0
\]

RoPE 几何：

> 会完全错乱。

---

# 四十三、Prefix Cache 为什么要求上下文一致？

## 198. 假设系统 Prompt

完全相同。

可以缓存：

> 它的 KV。

后续不同请求：

> 复用。

---

## 199. 但如果前面突然插入 100 个 Token

原 Prefix 中 Token 的位置：

> 全部发生变化。

对于 RoPE：

> 对应旋转相位也改变。

---

## 200. 所以 Prefix Cache

通常依赖：

\[
\boxed{
相同TokenPrefix
+
相同PositionStructure
}
\]

不是：

> “文字大概一样”就能随便复用。

---

# 四十四、Position 与 Chat Template

## 201. 例如 System Prompt 有

\[
1000\ Tokens
\]

那么用户真正正文的第一个 Token：

> 已经不是 Position 0。

---

## 202. 它可能从

\[
1000+
\]

的位置开始。

所以非常长的系统 Prompt：

> 不只占 Context。

还会把后面所有内容：

> 推向更远 Position。

---

## 203. 这再次说明

Prompt Engineering 不是：

> 纯语言艺术。

它会真正改变：

\[
\boxed{
TokenLayout
}
\]

---

# 四十五、位置越靠后，语义一定越弱吗？

## 204. 不一定

Position Encoding 本身：

> 不是一个简单“越远权重越低”的规则。

特别是 RoPE：

> 主要改变 Attention Geometry。

---

## 205. 最终 Attention 强不强

仍由：

\[
Content
+
Position
+
ModelWeights
+
Context
\]

共同决定。

---

# 四十六、相对距离越远就一定不重要吗？

## 206. 也不一定

法律文件中：

> 前面定义的术语

可能在 10000 Token 后：

> 仍然非常关键。

---

## 207. 所以模型不能只学

\[
Distance\uparrow
\Rightarrow
Importance\downarrow
\]

而必须学：

> 内容和距离共同决定关系。

---

# 四十七、RoPE 不是“距离衰减函数”

## 208. 这是一个重要误区

RoPE 本身不是简单：

\[
score
=
\frac1{|i-j|}
\]

---

## 209. 它是

> 用不同频率旋转 Q/K。

然后：

> 让 Dot Product 对相对位置敏感。

这是更复杂的几何机制。

---

# 四十八、为什么有时会谈 RoPE 的 Long-term Decay？

## 210. 对不同频率和高维组合

随着相对距离变化：

> Dot Product 的统计结构可能表现出某些距离特性。

---

## 211. 但不要简化成

> “RoPE 就是离得越远 Attention 越小。”

这个结论：

> 太粗糙。

真正 Attention 仍受：

\[
Q,K
\]

内容影响。

---

# 四十九、Position 是不是现实世界“页码”？

## 212. 不是

Position：

\[
3000
\]

表示：

> Token Sequence 中第 3000 个位置。

---

## 213. 它不天然表示

> PDF 第 8 页。

> 招标文件第 3 章。

> 评分办法第 4 条。

这些是：

# Document Structure

另一层信息。

---

## 214. 所以 ProcurementAI 还需要结构解析

例如保留：

```text
章节
条款号
表格
页码
字段
```

这些 Metadata。

---

## 215. Position Encoding 不能替代 Document Parser

再次是层级区别：

\[
\boxed{
TokenPosition
\neq
DocumentStructure
}
\]

---

# 五十、表格为什么更麻烦？

## 216. 采购文件大量使用表格

例如：

| 参数项 | 要求 | 分值 |
|---|---|---|
| CPU | ≥3.2GHz | 5 |
| 内存 | ≥32GB | 5 |

---

## 217. 如果把表格简单线性化

模型看到的是一维 Token Sequence。

---

## 218. 但原表格其实有二维关系

“5”到底属于：

> CPU 还是内存？

依赖：

> 行列结构。

---

## 219. 一维 Position 只能表达

> 前后距离。

不能天然完整表达：

> 二维表格 Layout。

---

## 220. 所以复杂采购文档理解可能需要

\[
\boxed{
TextPosition
+
LayoutStructure
+
TableStructure
}
\]

而不是：

> 只靠 RoPE。

---

# 五十一、一个政府采购顺序思维实验

## 221. 文本 A

> “供应商应具备售后服务能力，不要求在采购人所在地设立分支机构。”

---

## 222. 文本 B

> “供应商应在采购人所在地设立分支机构，不要求具备售后服务能力。”

词大量重合。

但：

> 条件完全不同。

---

## 223. 模型必须建模

\[
否定词
\]

和：

\[
被否定对象
\]

之间的位置关系。

---

## 224. 这也是为什么

“不得低于”

“不得高于”

“不得要求”

这些短语：

> 对 Token Order 非常敏感。

---

# 五十二、Position 与否定范围

## 225. 例如

> “不得仅因供应商注册资本较低而拒绝其参与采购活动。”

“不得”修饰：

> 后面一大段行为。

---

## 226. 如果模型不能处理位置和上下文范围

可能错误理解成：

> “注册资本较低 = 不得参与”。

含义完全相反。

---

## 227. 所以 Position 本质上参与

\[
\boxed{
SyntacticScope
}
\]

和：

\[
\boxed{
SemanticScope
}
\]

建模。

---

# 五十三、Position 与法律引用

## 228. 例如

> “前款规定不适用于本条第二项情形。”

这里有：

- 前款；
- 本条；
- 第二项。

---

## 229. Token Position 只能告诉

> 字面顺序。

真正解析：

> “前款”引用哪里，

还需要：

\[
DocumentStructure
\]

---

## 230. 所以未来采购法律 RAG

最好保留：

- Article ID；
- Paragraph ID；
- Section ID；
- Source Document；
- Effective Date。

这样模型不必：

> 纯靠 Token 距离猜法律结构。

---

# 五十四、长 Context 的 Procurement Benchmark 应该怎么做？

## 231. 第一类：Single Needle Retrieval

在：

\[
32K
\]

文档里放一个风险条件。

问模型：

> 条件是什么？

---

## 232. 位置要变化

分别放在：

\[
5\%
\]

\[
25\%
\]

\[
50\%
\]

\[
75\%
\]

\[
95\%
\]

位置。

---

## 233. 这样可以画

\[
\boxed{
Accuracy\ vs\ Position
}
\]

---

## 234. 第二类：Two-Evidence Integration

证据 A：

> 在前 10%。

证据 B：

> 在后 90%。

只有结合：

> 才能做正确判断。

---

## 235. 这比 Needle 更难

因为模型不只是：

> 找一个字符串。

而要：

\[
\boxed{
Retrieve
+
Integrate
+
Reason
}
\]

---

## 236. 第三类：Contradiction Resolution

前文：

> 供应商必须设置本地机构。

后文更正：

> 删除本地机构要求。

问：

> 最终有效要求是什么？

---

## 237. 这特别适合采购文件

因为真实项目经常有：

- 原公告；
- 更正公告；
- 补充通知；
- 澄清文件。

---

## 238. 第四类：Section Boundary

把相似内容放在：

> 不同章节。

看模型能否区分：

- 资格条件；
- 技术参数；
- 评分标准；
- 合同要求。

---

## 239. 第五类：Long-distance Negation

前文：

> 某要求成立。

后文：

> 某特殊情形除外。

测试：

> 模型能否正确处理例外。

---

# 五十五、长 Context 指标不能只有整体 Accuracy

## 240. 应该按 Position Slice

例如：

| 位置 | Accuracy |
|---|---:|
| 0–20% | 95% |
| 20–40% | 93% |
| 40–60% | 76% |
| 60–80% | 91% |
| 80–100% | 94% |

---

## 241. 如果只看平均

可能：

\[
90\%
\]

看起来很好。

但中间区域：

\[
76\%
\]

明显弱。

---

## 242. 第一课的 Slice Evaluation 又回来了

\[
\boxed{
Average
\ hides\
PositionWeakness
}
\]

---

# 五十六、训练长度与推理长度

## 243. 一个很关键的配置

\[
TrainContextLength
\]

---

## 244. 另一个是

\[
InferenceContextLength
\]

两者：

> 不一定相同。

---

## 245. 如果训练主要是

\[
4K
\]

但部署强行扩到：

\[
128K
\]

需要非常谨慎。

---

## 246. 即使 RoPE Scaling 技术上支持

仍需要：

> 长上下文评测。

最好还有：

> Long-context continued training / fine-tuning。

---

# 五十七、长 Context 继续训练教模型什么？

## 247. 不只是让 Position 数字变大

还让模型实际看到：

> 长距离依赖任务。

---

## 248. 例如

证据：

\[
10000
\]

Token 前。

结论：

> 在当前 Token。

模型通过 Loss：

> 学习跨长距离使用信息。

---

## 249. 所以

\[
\boxed{
LongPositionSupport
\neq
LongReasoningTraining
}
\]

这是一个非常重要的区别。

---

# 五十八、Position Scaling 与训练数据必须一起看

## 250. 只改 RoPE Config

让：

\[
MaxPosition=128K
\]

不代表：

> 模型获得真正 128K 专业阅读能力。

---

## 251. 还应该问

> 有没有 32K、64K、128K 训练样本？

> 有没有长距离依赖？

> 有没有长文档 Benchmark？

---

# 五十九、为什么长采购文件可能不应该全部塞进去？

## 252. 假设一个文件

\[
90K\ Tokens
\]

真正与当前问题相关的：

\[
3K
\]

---

## 253. 全塞进去

不仅成本高。

还增加：

> 无关信息干扰。

---

## 254. 所以更加成熟的系统思路

\[
\boxed{
Parser
\rightarrow
Retriever
\rightarrow
RelevantContext
\rightarrow
LongContextLLM
}
\]

---

## 255. Long Context 是能力储备

RAG 是：

> 信息选择机制。

二者：

> 不是替代关系。

---

# 六十、Position Encoding 最终统一到一个问题

## 256. 对任意两个 Token

\[
i,j
\]

模型真正需要知道：

> 它们是什么？

以及：

> 它们在哪里？

---

## 257. Token Embedding 提供

\[
Content
\]

---

## 258. Position Mechanism 提供

\[
PositionRelation
\]

---

## 259. Attention 最终组合

\[
\boxed{
Who
+
Where
+
WhoRelatesToWhom
}
\]

---

# 六十一、第二课第 10 阶段七个核心心智模型

| 心智模型 | 核心认知 |
|---|---|
| **① Token Embedding 管身份，Position 管序列位置** | 没有位置结构，词集合不足以表达语言顺序 |
| **② Mask 与 Position 是两种机制** | Mask 管谁能看谁；Position 管彼此在哪里 |
| **③ Absolute Position 简单但外推有限** | Learned Position Table 对训练外位置没有天然保证 |
| **④ 多频率 Sin/Cos 把位置变成多尺度相位** | 不同频率同时编码局部和长尺度位置变化 |
| **⑤ RoPE 用绝对旋转产生相对 Attention 几何** | \(R_m^TR_n=R_{n-m}\) 是核心 |
| **⑥ Context Window 不等于 Long-context Reliability** | 必须按位置、距离、任务独立评测 |
| **⑦ 长文档能力是系统能力** | Position、Attention、训练数据、RAG、解析、评测必须一起工作 |

---

# 六十二、如果只记四个公式

第一个，经典输入加绝对位置：

\[
\boxed{
h_i=e_i+p_i
}
\]

第二个，二维旋转：

\[
\boxed{
R(\theta)
=
\begin{bmatrix}
\cos\theta&-\sin\theta\\
\sin\theta&\cos\theta
\end{bmatrix}
}
\]

第三个，RoPE：

\[
\boxed{
\tilde q_m=R_mq_m,\qquad
\tilde k_n=R_nk_n
}
\]

第四个，最核心：

\[
\boxed{
\tilde q_m^T\tilde k_n
=
q_m^TR_{n-m}k_n
}
\]

如果这个第四个公式真正理解：

> RoPE 的灵魂就已经抓住了。

---

# 六十三、如果只记一句话

\[
\boxed{
RoPE不是给Token“贴一个位置标签”，
而是根据位置旋转Query和Key，
使Attention在比较内容的同时，
天然感知Token之间的相对位置。
}
\]

---

# 六十四、第二课 8～10 阶段现在组成完整输入层

第 9 阶段：

\[
\boxed{
Text
\rightarrow
TokenIDs
}
\]

第 8 阶段：

\[
\boxed{
TokenIDs
\rightarrow
TokenEmbedding
}
\]

第 10 阶段：

\[
\boxed{
TokenEmbedding
+
PositionStructure
}
\]

于是终于得到：

\[
\boxed{
RawText
\rightarrow
Tokenizer
\rightarrow
IDs
\rightarrow
Embeddings
\rightarrow
PositionAwareRepresentations
}
\]

现在，LLM 已经具备：

> “这些 Token 是什么”

以及：

> “这些 Token 在哪里”

两种基础信息。

但是，还差真正最关键的一步：

> **它怎么决定当前这个 Token 应该去看前面的哪些 Token？**

这就是：

\[
\boxed{
Attention
}
\]

---

# 六十五、第 10 阶段掌握标准

学完这一阶段，你应该能够从机制上解释：

> 为什么纯粹的无位置 Self-Attention 没有天然 Token 顺序概念？

> Causal Mask 与 Position Encoding 有什么根本区别？

> Token ID 与 Position ID 为什么完全不同？

> Learned Absolute Position Embedding 如何工作？

> 为什么直接把 Position Table 从 4K 扩到 128K 并不等于获得 128K 能力？

> Sinusoidal Position Encoding 为什么使用不同频率？

> 为什么 Sin 和 Cos 经常成对出现？

> Absolute Position 与 Relative Position 有什么区别？

> Relative Position Bias 怎样进入 Attention Score？

> RoPE 为什么叫“旋转”位置编码？

> 二维 Rotation Matrix 是怎样工作的？

> 为什么 RoPE 通常作用在 Q 和 K，而不是 V？

> 为什么旋转不会改变向量 Norm？

> 为什么 \(R_m^TR_n=R_{n-m}\) 能让 Dot Product 感知相对位置？

> RoPE 与普通 Sinusoidal Position Encoding 最根本的应用方式差在哪里？

> 什么叫 RoPE Base？

> 为什么不同维度需要不同旋转频率？

> 为什么 RoPE 数学上能算 100K Position，不代表模型可靠支持 100K Context？

> Position Interpolation 的“压缩尺子”直觉是什么？

> 为什么 NTK-aware / YaRN 这类方法本质上都在重新处理位置与频率尺度？

> Context Window 与 Long-context Ability 为什么必须分开评测？

> 为什么要做 Position Slice Benchmark？

> KV Cache 为什么必须保持正确 Position？

> 为什么 Sequence Packing 时重置 Position 不足以隔离不同文档？

> Token Position 为什么不能替代 PDF 页码、章节和表格结构？

> 为什么采购长文档即使能塞进模型，仍然可能需要 RAG？

如果这些问题已经能够自己完整解释：

\[
\boxed{
第二课第10阶段真正建立起来了
}
\]

下一阶段，我们就正式进入整个 Transformer 最核心、也是很多人第一次真正“看懂大语言模型”的地方：
