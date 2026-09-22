# 第二课 · 第 11 阶段：Self-Attention
## Query、Key、Value 到底是什么？一个 Token 究竟怎样“寻找、读取、整合”其它 Token 的信息？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Self-Attention 的核心不是“平均看所有 Token”，而是根据 Query–Key 匹配动态决定从哪里读取信息。**
2. **Query 决定“我要找什么”，Key 决定“我怎样被匹配”，Value 承载“真正被汇聚的内容”。**
3. **Attention Score 经过缩放与 Softmax 后形成权重；除以 √d_k 是为了避免高维点积过大导致 Softmax 饱和。**
4. **Causal Mask 保证 Decoder 当前位置看不到未来 Token，从而维持 Next Token Prediction 的因果训练目标。**
5. **Attention Weight ≠ Human Explanation。高权重说明当前计算中的信息路由强度，不等于法律因果解释或最终决策依据。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Attention` | 注意力：根据内容相关性动态聚合信息 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Query` | Query/Q：当前 Token 表示“我要找什么”的向量 |
| `Value` | Value/V：被注意力权重实际汇聚的内容向量 |
| `Key` | Key/K：其他 Token 表示“我可被怎样匹配”的向量 |
| `Self-Attention` | 自注意力：同一序列内部各位置计算相关性并聚合 |
| `Softmax` | Softmax：把一组分数转换成归一化权重 |
| `Transformer` | Transformer：以注意力和前馈网络为核心的序列架构 |
| `State` | 状态：保存任务进度、事实和待办 |
| `RoPE` | RoPE：旋转位置编码，把位置信息融入注意力 |
| `Representation` | 表示：模型内部承载语义或特征的向量结构 |
| `Routing` | 路由：决定当前任务交给哪个工具/模块 |

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

前面三阶段，我们完成了 LLM 输入世界：

\[
\boxed{
Text
\rightarrow
Tokenizer
\rightarrow
TokenIDs
\rightarrow
Embedding
\rightarrow
Position
}
\]

现在每一个 Token 已经拥有一个向量：

\[
x_i\in\mathbb R^D
\]

它知道：

> “我是谁。”

也拥有位置机制：

> “我在哪里。”

但是现在出现真正关键的问题：

> **Token 之间怎么交流？**

比如一句：

> “供应商注册资本不得低于5000万元。”

当模型处理“5000万元”时，它为什么能够利用：

> “注册资本”

> “不得”

> “低于”

这些前文信息？

答案就是：

\[
\boxed{
SelfAttention
}
\]

Self-Attention 最核心的公式，我们今天最终要真正吃透：

\[
\boxed{
Attention(Q,K,V)
=
Softmax
\left(
\frac{QK^T}{\sqrt{d_k}}
\right)V
}
\]

如果是 Decoder-only LLM，还要加：

\[
\boxed{
CausalMask
}
\]

所以完整一点：

\[
\boxed{
A
=
Softmax
\left(
\frac{QK^T}{\sqrt{d_k}}
+
M
\right)
}
\]

然后：

\[
\boxed{
O=AV
}
\]

今天所有内容，本质都在解释这两行。

---

## 1. 先不要碰 Q、K、V

我们先问一个更朴素的问题。

假设当前 Token 是：

> “5000万元”

它想理解自己在句子里的作用。

它可能需要参考：

> “注册资本”

因为要知道：

> 5000万元是什么数值。

---

## 2. 它还需要参考

> “不得低于”

因为这决定：

> 5000万元与注册资本之间是什么关系。

---

## 3. 所以一个 Token 的最终表示不应该只来自自己

如果只有：

\[
h_i=x_i
\]

那么“5000万元”的表示：

> 永远只是“5000万元”。

它不知道：

> 前面到底是在说预算、注册资本还是合同金额。

---

## 4. 我们希望得到

\[
\boxed{
h_i'
=
\text{自己}
+
\text{从上下文读取的信息}
}
\]

也就是说：

> Token Representation 必须 Contextualize。

---

## 5. 第一个核心心智模型

### 心智模型 ①：Attention 是一个“动态信息路由系统”

当前 Token 不只是处理自己的向量。

它会问：

\[
\boxed{
我现在应该从哪些Token读取信息？
}
\]

再问：

\[
\boxed{
每个Token应该读取多少？
}
\]

最后：

\[
\boxed{
把读取到的信息组合进自己的新表示
}
\]

---

# 一、从最简单的“加权平均”开始

## 6. 假设前面有三个 Token

\[
x_1,x_2,x_3
\]

当前 Token 想从它们读取信息。

---

## 7. 最简单方法是什么？

给每个 Token 一个权重：

\[
a_1,a_2,a_3
\]

满足：

\[
a_i\ge0
\]

以及：

\[
a_1+a_2+a_3=1
\]

---

## 8. 然后做加权求和

\[
\boxed{
o
=
a_1x_1
+
a_2x_2
+
a_3x_3
}
\]

这已经有一点 Attention 的味道了。

---

## 9. 例如

\[
a_1=0.1
\]

\[
a_2=0.8
\]

\[
a_3=0.1
\]

意味着：

> 当前 Token 主要从第二个 Token 读取信息。

---

## 10. 真正困难的问题不是“怎么加权”

真正困难的是：

\[
\boxed{
这些权重从哪里来？
}
\]

不能人工规定：

> “不得永远权重 0.8。”

因为不同句子：

> 关系完全不同。

---

## 11. 所以权重必须动态产生

给定当前输入：

\[
X
\]

模型必须自己计算：

\[
A(X)
\]

所以 Attention Weight 是：

\[
\boxed{
InputDependent
}
\]

而不是固定参数表。

---

## 12. 这就是 Attention 与普通 Linear Layer 的重大区别

Linear：

\[
Y=XW
\]

Weight：

\[
W
\]

训练完成后：

> 对所有输入基本固定。

---

## 13. Attention 的 Routing Weight

却会根据当前文本：

> 动态改变。

同一个“本市”：

在一句：

> “项目地点位于本市”

可能关注：

> “项目地点”。

---

## 14. 另一句

> “供应商必须在本市注册”

“本市”可能与：

> “供应商”

> “注册”

形成另一种关系。

---

## 15. 所以 Attention 可以理解成

\[
\boxed{
DynamicWeighting
}
\]

神经网络不是预先写：

> Token A 永远看 Token B。

而是每个输入：

> 重新计算关系。

---

# 二、怎样动态计算“谁和谁相关”？

## 16. 第 8 阶段已经学过一个工具

两个向量：

\[
a,b
\]

可以通过：

\[
a^Tb
\]

计算 Dot Product。

---

## 17. Dot Product 大

粗略意味着：

> 两个向量在当前表示空间里匹配得比较强。

所以一个自然想法：

\[
\boxed{
Score(i,j)
=
x_i^Tx_j
}
\]

---

## 18. 当前 Token \(i\)

对所有 Token：

\[
j
\]

分别算：

\[
x_i^Tx_j
\]

就得到：

> 一排匹配分数。

---

## 19. 例如

\[
[
2.3,
0.4,
5.1,
-1.2
]
\]

说明当前 Token：

> 与第三个 Token 匹配最强。

---

## 20. 但直接用原始 \(X\) 做匹配有一个限制

同一个向量：

\[
x_i
\]

既要表示：

> “我是什么”。

又要承担：

> “我现在寻找什么”。

还要承担：

> “别人应该如何找到我”。

---

## 21. 这三个角色实际上不同

于是 Transformer 做了一件非常聪明的事：

> 把同一个 Hidden State 投影成三个不同角色。

就是：

\[
\boxed{
Q,K,V
}
\]

---

# 三、Query、Key、Value 第一次出现

## 22. 对输入

\[
X
\]

创建三个 Linear Projection：

\[
\boxed{
Q=XW_Q
}
\]

\[
\boxed{
K=XW_K
}
\]

\[
\boxed{
V=XW_V
}
\]

---

## 23. \(W_Q\)、\(W_K\)、\(W_V\) 是什么？

它们都是：

# Trainable Weight

通过：

\[
Backprop
+
Optimizer
\]

学习出来。

---

## 24. Query 最好怎么理解？

Query：

\[
q_i
\]

可以粗略理解为：

> **当前 Token 正在寻找什么信息？**

即：

\[
\boxed{
What\ am\ I\ looking\ for?
}
\]

---

## 25. Key 呢？

Key：

\[
k_j
\]

可以粗略理解为：

> **这个 Token 用什么特征让别人判断“我是否值得被读取”？**

即：

\[
\boxed{
What\ do\ I\ match\ on?
}
\]

---

## 26. Value 呢？

Value：

\[
v_j
\]

表示：

> **如果别人决定关注我，我真正提供什么信息？**

即：

\[
\boxed{
What\ information\ do\ I\ carry?
}
\]

---

## 27. 一个非常经典的类比

可以把它想成数据库检索。

Query：

> 搜索请求。

Key：

> 索引字段。

Value：

> 真正返回的内容。

---

## 28. 例如

你搜索：

> “采购文件中注册资本限制”

这个需求：

> 类似 Query。

---

## 29. 数据库某条记录的索引

> “供应商资格 / 注册资本”

类似：

> Key。

---

## 30. 真正返回的条款正文

> “供应商注册资本不得低于5000万元”

类似：

> Value。

---

## 31. 第二区分非常重要

模型不是：

\[
Query
\]

和：

\[
Value
\]

直接比较。

它首先：

\[
Query
\leftrightarrow
Key
\]

决定：

> 该不该读。

然后才拿：

\[
Value
\]

回来。

---

## 32. 第二个核心心智模型

### 心智模型 ②：Q/K 决定“从哪里读”，V 决定“读回来什么”

可以压缩成：

\[
\boxed{
QK
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

这和上一阶段理解 RoPE 时已经见过一次。

现在正式展开。

---

# 四、为什么同一个 X 要做三个 Projection？

## 33. 假设 Token 是

> “注册资本”

它对不同任务可以扮演不同角色。

别人寻找：

> “金额条件”

时，

它可能是一个很好的 Key。

---

## 34. 但当它自己作为 Query 时

它可能寻找：

> “不得低于”

> “供应商”

> “资格条件”

这些上下文。

---

## 35. 所以

\[
q_i
\]

与：

\[
k_i
\]

没有理由一定相同。

---

## 36. 同理

真正要传给其它 Token 的 Value：

\[
v_i
\]

也不一定应该等于：

\[
k_i
\]

---

## 37. 如果强制

\[
Q=K=V=X
\]

Self-Attention 仍然可以定义。

但表达能力：

> 会受到限制。

---

## 38. 所以标准 Transformer 学习

\[
W_Q
\]

\[
W_K
\]

\[
W_V
\]

三个不同投影。

让模型自己决定：

> 什么特征适合用于搜索。

> 什么特征适合被匹配。

> 什么特征适合被传输。

---

## 39. 技术上它们“必须”完全不同吗？

不是数学上的绝对必须。

这是一个重要修正。

---

## 40. 实际架构里确实存在共享

例如现代模型里的：

# Multi-Query Attention

以及：

# Grouped-Query Attention

会让多个 Query Head：

> 共享部分 K/V。

---

## 41. 所以更精确地说

\[
\boxed{
Q,K,V
代表不同计算角色，
标准Attention通常使用不同投影，
但架构可以共享其中部分参数或表示。
}
\]

---

# 五、Shape 开始进入

## 42. 假设输入有

\[
S
\]

个 Token。

Hidden Size：

\[
D
\]

那么：

\[
X\in\mathbb R^{S\times D}
\]

---

## 43. 假设

\[
W_Q\in\mathbb R^{D\times d_k}
\]

那么：

\[
Q=XW_Q
\]

Shape：

\[
\boxed{
Q\in\mathbb R^{S\times d_k}
}
\]

---

## 44. 同样

\[
K\in\mathbb R^{S\times d_k}
\]

这样：

\[
QK^T
\]

才能做 Dot Product。

---

## 45. 因为

\[
Q:
(S,d_k)
\]

而：

\[
K^T:
(d_k,S)
\]

所以：

\[
\boxed{
QK^T:
(S,S)
}
\]

---

## 46. 这张 \(S\times S\) 矩阵是什么？

它就是：

# Attention Score Matrix

每个：

\[
(i,j)
\]

位置表示：

> 第 \(i\) 个 Token 对第 \(j\) 个 Token 的匹配分数。

---

## 47. 行是什么意思？

第：

\[
i
\]

行：

> Token \(i\) 的 Query 对所有 Key 的 Score。

---

## 48. 列是什么意思？

第：

\[
j
\]

列：

> 所有 Query 对 Token \(j\) 的 Key 匹配情况。

---

## 49. 所以一张 Attention Matrix 本质上是一张关系图

\[
\boxed{
Token
\times
Token
}
\]

这就是为什么 Attention 可以建模：

> 任意位置之间的直接关系。

---

# 六、亲手算完整的 3 Token Self-Attention

## 50. 我们现在用一个最小模型

三个 Token：

```text
供应商
不得
本市
```

为了手算，不使用真实高维 Embedding。

设：

\[
X=
\begin{bmatrix}
1&0\\
0&1\\
1&1
\end{bmatrix}
\]

---

## 51. 也就是

“供应商”：

\[
x_1=[1,0]
\]

“不得”：

\[
x_2=[0,1]
\]

“本市”：

\[
x_3=[1,1]
\]

---

## 52. 为了第一次手算最简单

先设：

\[
W_Q=I
\]

\[
W_K=I
\]

\[
W_V=I
\]

所以：

\[
Q=K=V=X
\]

---

## 53. 注意

真实 Transformer：

> 不会简单使用 Identity。

这里只是：

> 为了把 Attention 数学本身看清楚。

---

## 54. 于是

\[
Q=
\begin{bmatrix}
1&0\\
0&1\\
1&1
\end{bmatrix}
\]

---

## 55. K 一样

\[
K=
\begin{bmatrix}
1&0\\
0&1\\
1&1
\end{bmatrix}
\]

---

## 56. V 也一样

\[
V=
\begin{bmatrix}
1&0\\
0&1\\
1&1
\end{bmatrix}
\]

---

# 七、第一步：算 \(QK^T\)

## 57. \(K^T\)

\[
K^T=
\begin{bmatrix}
1&0&1\\
0&1&1
\end{bmatrix}
\]

---

## 58. 所以

\[
QK^T
=
\begin{bmatrix}
1&0\\
0&1\\
1&1
\end{bmatrix}
\begin{bmatrix}
1&0&1\\
0&1&1
\end{bmatrix}
\]

---

## 59. 得到

\[
\boxed{
QK^T
=
\begin{bmatrix}
1&0&1\\
0&1&1\\
1&1&2
\end{bmatrix}
}
\]

---

## 60. 第一行是什么意思？

第一个 Token：

> “供应商”

Query：

\[
[1,0]
\]

---

## 61. 它和自己 Key 点积

\[
[1,0]\cdot[1,0]=1
\]

---

## 62. 和“不得”

\[
[1,0]\cdot[0,1]=0
\]

---

## 63. 和“本市”

\[
[1,0]\cdot[1,1]=1
\]

所以第一行：

\[
[1,0,1]
\]

---

## 64. 第三行为什么最后一个是 2？

因为：

\[
[1,1]\cdot[1,1]
=
1+1
=
2
\]

---

# 八、为什么不能直接 Softmax？

## 65. 标准公式先要除

\[
\sqrt{d_k}
\]

这里：

\[
d_k=2
\]

所以除：

\[
\sqrt2
\]

---

## 66. 得到

\[
S=
\frac{QK^T}{\sqrt2}
\]

约等于：

\[
\begin{bmatrix}
0.707&0&0.707\\
0&0.707&0.707\\
0.707&0.707&1.414
\end{bmatrix}
\]

---

# 九、为什么偏偏是 \(\sqrt{d_k}\)？

## 67. 这是 Self-Attention 最经典的问题之一

假设 Query 和 Key 每个维度：

- 均值约 0；
- 方差约 1；
- 简化地看相互独立。

---

## 68. 点积是

\[
q^Tk
=
\sum_{r=1}^{d_k}
q_rk_r
\]

---

## 69. 一项

\[
q_rk_r
\]

的方差大约：

\[
1
\]

---

## 70. 加 \(d_k\) 项以后

Dot Product 的方差大致：

\[
\boxed{
Var(q^Tk)\approx d_k
}
\]

---

## 71. 所以标准差大约

\[
\sqrt{d_k}
\]

---

## 72. 如果不缩放

当：

\[
d_k=128
\]

时，

Score 数值可能：

> 比 \(d_k=2\) 大很多。

---

## 73. Score 太大会怎样？

Softmax 会变得：

> 极其尖锐。

例如：

\[
[20,1,0]
\]

Softmax 几乎：

\[
[1,0,0]
\]

---

## 74. 这意味着

Attention 很容易：

> 提前饱和。

梯度：

> 也可能变差。

---

## 75. 除以

\[
\sqrt{d_k}
\]

以后：

\[
Var
\]

大致重新压回：

\[
1
\]

量级。

---

## 76. 第三个核心心智模型

### 心智模型 ③：\(\sqrt{d_k}\) 是 Attention 的“尺度稳定器”

它不是：

> 神秘常数。

而是在控制：

\[
\boxed{
DotProductVariance
}
\]

让不同 Head Dimension 下：

> Softmax 工作在较健康数值区间。

---

# 十、Softmax 到底在做什么？

## 77. 我们已经得到 Score

第一行：

\[
[0.707,0,0.707]
\]

---

## 78. Softmax 定义

\[
\boxed{
Softmax(z_i)
=
\frac{e^{z_i}}
{\sum_j e^{z_j}}
}
\]

---

## 79. 第一行指数

\[
e^{0.707}\approx2.028
\]

\[
e^0=1
\]

\[
e^{0.707}\approx2.028
\]

---

## 80. 总和

\[
2.028+1+2.028
=
5.056
\]

---

## 81. 所以第一行 Attention Weight

约为：

\[
\boxed{
[0.401,0.198,0.401]
}
\]

---

## 82. 第二行同理

\[
[0,0.707,0.707]
\]

得到：

\[
\boxed{
[0.198,0.401,0.401]
}
\]

---

## 83. 第三行

\[
[0.707,0.707,1.414]
\]

---

## 84. 指数约为

\[
[2.028,2.028,4.113]
\]

总和：

\[
8.169
\]

---

## 85. 所以第三行

约：

\[
\boxed{
[0.248,0.248,0.503]
}
\]

---

## 86. 最终 Attention Matrix

\[
A
\approx
\begin{bmatrix}
0.401&0.198&0.401\\
0.198&0.401&0.401\\
0.248&0.248&0.503
\end{bmatrix}
\]

---

## 87. 每一行有什么共同特点？

所有值：

\[
>0
\]

并且：

\[
\boxed{
\sum_j A_{ij}=1
}
\]

---

## 88. 因此每一行可以理解为

当前 Token：

> 如何把自己的“读取预算”分配给所有 Token。

---

## 89. 但注意

Attention Weight：

> 不是“事实为真的概率”。

---

## 90. 0.7 Attention 不代表

> “模型有 70% 把握这个词重要。”

它只是：

\[
\boxed{
当前Head当前Layer当前Query下的归一化RoutingWeight
}
\]

---

# 十一、Softmax 为什么很适合 Attention？

## 91. 第一，它产生正权重

\[
A_{ij}>0
\]

所以加权聚合容易解释。

---

## 92. 第二，每行归一化

\[
\sum_jA_{ij}=1
\]

所以不同 Token：

> 在一个共同预算下竞争。

---

## 93. 第三，它强调相对大小

假设 Score：

\[
[1,2,3]
\]

和：

\[
[101,102,103]
\]

Softmax 结果相同。

---

## 94. 因为 Softmax 对整体平移不敏感

\[
\boxed{
Softmax(z+c)
=
Softmax(z)
}
\]

---

## 95. 所以它关心

> Score 之间的差。

而不是：

> 绝对基线。

---

## 96. 第四，Softmax 可微

所以：

\[
Loss
\]

可以通过它：

> 反向传播到 Q、K。

---

# 十二、数值稳定 Softmax

## 97. 如果 Score 很大

例如：

\[
1000
\]

直接：

\[
e^{1000}
\]

可能溢出。

---

## 98. 所以实际实现通常先减最大值

\[
z'_i
=
z_i-\max(z)
\]

---

## 99. 因为

\[
Softmax(z)
=
Softmax(z-\max z)
\]

结果不变。

---

## 100. 例如

\[
[1000,999,998]
\]

变成：

\[
[0,-1,-2]
\]

数值稳定得多。

---

## 101. 这又是第 7 阶段的 Numerical Stability

现代深度学习：

> 到处都在做这种稳定性设计。

---

# 十三、最后一步：\(AV\)

## 102. Attention Matrix：

\[
A
\]

Value：

\[
V
\]

最终：

\[
\boxed{
O=AV
}
\]

---

## 103. 我们例子里

\[
V=
\begin{bmatrix}
1&0\\
0&1\\
1&1
\end{bmatrix}
\]

---

## 104. 第一行输出

\[
o_1
=
0.401v_1
+
0.198v_2
+
0.401v_3
\]

---

## 105. 展开

\[
=
0.401[1,0]
+
0.198[0,1]
+
0.401[1,1]
\]

---

## 106. 得到

\[
\boxed{
o_1
\approx
[0.802,0.599]
}
\]

---

## 107. 原来第一个 Token 是

\[
[1,0]
\]

现在：

\[
[0.802,0.599]
\]

---

## 108. 看见发生了什么吗？

新的 Representation：

> 已经混入其它 Token 的信息。

---

## 109. 第二行输出

\[
o_2
\approx
[0.599,0.802]
\]

---

## 110. 第三行输出

\[
o_3
\approx
[0.751,0.751]
\]

---

## 111. 所以 Self-Attention 做了一件根本性的事

原来：

\[
x_i
\]

只是：

> 每个 Token 自己。

Attention 后：

\[
o_i
\]

变成：

> 根据当前句子动态整合上下文的信息。

---

## 112. 第四个核心心智模型

### 心智模型 ④：Attention Output 是“根据动态关系权重聚合来的上下文向量”

公式就是：

\[
\boxed{
o_i
=
\sum_j
A_{ij}v_j
}
\]

这是 Self-Attention 最核心的一行。

---

# 十四、为什么叫 Self-Attention？

## 113. 因为 Q、K、V 都来自

同一个输入序列：

\[
X
\]

---

## 114. 即

\[
Q=XW_Q
\]

\[
K=XW_K
\]

\[
V=XW_V
\]

所以：

> 序列“关注自己”。

---

## 115. 如果 Query 来自一个序列

而 Key/Value 来自另一个序列，

那就是：

# Cross-Attention

---

## 116. 例如 Encoder-Decoder Transformer

Decoder 的 Query：

> 来自 Decoder。

K/V：

> 来自 Encoder 输出。

---

## 117. 这时模型在做

> “我当前生成状态应该从输入文本读取什么？”

---

## 118. 但现代 Decoder-only LLM

主要依赖：

\[
\boxed{
MaskedSelfAttention
}
\]

所以本课重点放这里。

---

# 十五、现在把 Causal Mask 加回来

## 119. 我们刚才那个 Attention

第一个 Token：

> 可以看第三个 Token。

---

## 120. 这在 BERT 类双向模型里

可能完全合理。

---

## 121. 但 Decoder-only Language Model 做 Next Token Prediction 时

当前 Token：

> 不能偷看未来答案。

---

## 122. 例如序列

```text
供应商 必须 在 本市 注册
```

训练预测：

> “注册”

时，

模型不能提前看到：

> “注册”。

---

## 123. 所以需要 Causal Mask

对于：

\[
i
\]

只能看：

\[
j\le i
\]

---

## 124. Mask Matrix 可以写成

\[
M_{ij}
=
\begin{cases}
0,&j\le i\\
-\infty,&j>i
\end{cases}
\]

---

## 125. 为什么用 \(-\infty\)？

因为 Softmax：

\[
e^{-\infty}=0
\]

所以未来位置：

> 权重精确趋向 0。

---

## 126. 三 Token Mask

\[
M=
\begin{bmatrix}
0&-\infty&-\infty\\
0&0&-\infty\\
0&0&0
\end{bmatrix}
\]

---

## 127. 第一 Token

只能看：

\[
1
\]

自己。

---

## 128. 第二 Token

可以看：

\[
1,2
\]

---

## 129. 第三 Token

可以看：

\[
1,2,3
\]

---

## 130. 所以 Decoder Self-Attention Score 实际是

\[
\boxed{
S
=
\frac{QK^T}{\sqrt{d_k}}
+
M
}
\]

然后再：

\[
Softmax(S)
\]

---

# 十六、为什么训练时还能并行？

## 131. 这是 Transformer 的巨大优势之一

虽然：

> Token \(i\) 不能看未来。

但所有 Token 的：

\[
Q,K,V
\]

可以一次矩阵乘法：

> 全部计算。

---

## 132. Attention Score Matrix

\[
S\times S
\]

也可以：

> 一次生成。

---

## 133. Causal Mask

只把：

> 未来位置遮掉。

---

## 134. 所以训练不是必须

```text
Token1
等它算完
Token2
等它算完
Token3
...
```

---

## 135. 而是可以

\[
\boxed{
ParallelTraining
}
\]

---

## 136. 这和早期 RNN 很不同

RNN Hidden State：

\[
h_t
\]

依赖：

\[
h_{t-1}
\]

所以计算天然顺序化。

---

## 137. Transformer Attention

训练时可以：

> 并行计算整条序列。

这对 GPU：

> 极其友好。

---

# 十七、Teacher Forcing

## 138. 训练语言模型时

我们已经拥有：

> 完整真实文本。

例如：

```text
供应商 必须 在 本市 注册
```

---

## 139. 输入可以一次给完整 Sequence

然后每个位置：

> 预测下一个 Token。

---

## 140. 例如

位置 1：

> 预测“必须”。

位置 2：

> 预测“在”。

位置 3：

> 预测“本市”。

---

## 141. Causal Mask 保证

即使真实未来 Token 已经存在 Tensor 里：

> 当前位置也不能读取它们。

---

## 142. 所以

\[
\boxed{
完整序列并行训练
+
CausalMask
=
AutoregressiveObjective
}
\]

---

# 十八、推理为什么不能同样完全并行？

## 143. 生成时未来 Token：

> 还不存在。

---

## 144. 第一个新 Token 生成以后

才能知道：

> 第二个新 Token 的输入是什么。

---

## 145. 因此生成阶段依然：

\[
Token_t
\rightarrow
Token_{t+1}
\rightarrow
Token_{t+2}
\]

顺序进行。

---

## 146. 这叫

# Autoregressive Decoding

---

# 十九、KV Cache 再次出现

## 147. 假设已经生成

\[
1000
\]

个 Token。

新的第：

\[
1001
\]

Token 到来。

---

## 148. 过去 1000 个 Token 的 K、V

之前已经算过。

没必要：

> 每次全部重算。

---

## 149. 所以缓存

\[
K_{1:1000}
\]

\[
V_{1:1000}
\]

---

## 150. 新一步只计算

\[
q_{1001}
\]

\[
k_{1001}
\]

\[
v_{1001}
\]

---

## 151. 然后

\[
q_{1001}
\]

与所有缓存 K：

\[
K_{1:1001}
\]

比较。

---

## 152. 这就是为什么 KV Cache

对 LLM 推理：

> 极其重要。

---

# 二十、Attention 是一种 Content-Addressable Memory

## 153. 这是一个非常强的心智模型

传统数组读取：

> 给地址 37，读第 37 个位置。

---

## 154. Attention 不一定先知道地址

它可以说：

> “我要找和我这个 Query 最匹配的信息。”

---

## 155. 然后通过

\[
q^Tk_j
\]

计算：

> 哪个 Key 最匹配。

---

## 156. 这很像

# Content-Addressable Memory

基于内容寻址。

---

## 157. 举个采购例子

当前 Token 表示：

> “5000万元”。

模型内部某个 Query 方向可能希望找：

> “这个数字修饰什么？”

---

## 158. 前文 Token 中

“注册资本”的 Key：

> 可能与这个 Query 匹配较强。

---

## 159. Attention 就把

“注册资本”对应的 Value：

> 更多混进当前 Representation。

---

## 160. 这只是帮助理解的抽象

真实大模型不会显式存在：

> “寻找被修饰对象”这个中文 Query 标签。

这种功能：

> 是训练后参数中的分布式行为。

---

# 二十一、为什么 Attention 不是普通平均池化？

## 161. 普通平均：

\[
o_i
=
\frac1S
\sum_jv_j
\]

每个 Token：

> 权重一样。

---

## 162. Attention：

\[
o_i
=
\sum_jA_{ij}v_j
\]

其中：

\[
A_{ij}
\]

由当前输入动态决定。

---

## 163. 所以同一序列中

不同 Query Token：

> 可以读取完全不同的上下文。

---

## 164. 例如“注册资本”

可能关注：

> 数字金额。

---

## 165. “不得”

可能更关注：

> 后续动作或条件。

---

## 166. “供应商”

可能关注：

> 资格要求、行为或角色。

---

## 167. 这就是

\[
\boxed{
ContextDependentRouting
}
\]

---

# 二十二、Attention Weight 是不是硬选择？

## 168. 通常不是

不是：

```text
只看 Token 17
完全不看其它
```

而通常是：

\[
[0.02,0.15,0.61,0.12,\ldots]
\]

---

## 169. 所以 Attention 是

# Soft Selection

软选择。

---

## 170. 优点是什么？

模型可以：

> 同时融合多个证据。

---

## 171. 例如风险判断可能同时需要

- “供应商”；
- “必须”；
- “本市”；
- “注册”；
- 其它上下文。

不是：

> 一个词就能决定。

---

# 二十三、Attention 可以非常尖锐，也可以很分散

## 172. 尖锐 Attention

例如：

\[
[0.01,0.01,0.96,0.02]
\]

基本只关注：

> 一个位置。

---

## 173. 分散 Attention

例如：

\[
[0.22,0.28,0.25,0.25]
\]

从：

> 多个 Token 综合信息。

---

## 174. 可以用 Entropy 描述分散程度

\[
H(A_i)
=
-\sum_jA_{ij}\log A_{ij}
\]

---

## 175. 高 Entropy

表示：

> 权重比较分散。

---

## 176. 低 Entropy

表示：

> 权重比较集中。

---

## 177. 但集中不一定更好

任务有时需要：

> 精确指代。

有时需要：

> 综合整段信息。

---

# 二十四、Softmax Temperature

## 178. 一般形式可以写

\[
Softmax
\left(
\frac{z}{T}
\right)
\]

---

## 179. \(T\) 小

Score 差异：

> 被放大。

Attention：

> 更尖锐。

---

## 180. \(T\) 大

Score：

> 更平坦。

Attention：

> 更分散。

---

## 181. Scaled Dot-Product 中

\[
\sqrt{d_k}
\]

本质上也具有：

> 控制 Score Temperature 的效果。

---

# 二十五、Value 为什么必须单独投影？

## 182. 假设 Key 只需要表示

> “我适合被什么 Query 找到？”

---

## 183. 但真正传输的信息

可能比 Key：

> 丰富得多。

---

## 184. 例如一个法规条款

Key 可以突出：

> “资格条件 / 注册资本”。

---

## 185. Value 则可以携带

> 更复杂的上下文表示。

---

## 186. 所以分开 K/V

让模型拥有：

\[
\boxed{
SearchFeature
\neq
ReturnedFeature
}
\]

的自由度。

---

# 二十六、QK Score 是对称的吗？

## 187. 很多人会误以为

\[
q_i^Tk_j
\]

和：

\[
q_j^Tk_i
\]

必然相同。

---

## 188. 如果

\[
Q=K
\]

确实可能对称。

---

## 189. 但标准 Attention

\[
Q=XW_Q
\]

\[
K=XW_K
\]

而：

\[
W_Q\neq W_K
\]

---

## 190. 所以通常

\[
\boxed{
q_i^Tk_j
\neq
q_j^Tk_i
}
\]

---

## 191. 这很合理

因为关系可能是有方向的。

例如：

> “代词寻找它指代的名词”

和：

> “名词寻找后面的代词”

不是同一个任务。

---

## 192. 所以 Attention Relation

不必：

> 对称。

这是一个非常重要的几何性质。

---

# 二十七、Attention Matrix 不是普通距离矩阵

## 193. 距离矩阵通常：

\[
d(i,j)=d(j,i)
\]

---

## 194. Attention Score：

> 可以完全不对称。

所以：

\[
\boxed{
Attention
更像有向关系图
}
\]

---

# 二十八、Backprop 怎么训练 Q/K/V？

## 195. 最终 Loss

\[
L
\]

会通过后续层：

> 回到 Attention Output。

---

## 196. 然后回到

\[
V
\]

因为：

\[
O=AV
\]

---

## 197. 同时也会回到

\[
A
\]

---

## 198. A 又来自

\[
Softmax(S)
\]

---

## 199. S 来自

\[
QK^T
\]

---

## 200. 所以 Gradient 最终进入

\[
W_Q,W_K,W_V
\]



## 201. 这意味着模型不是人工指定

> “这个词应该关注那个词”。

而是：

\[
\boxed{
通过最终任务Loss，
反向学出怎样的Attention Routing更有用
}
\]

---

# 二十九、Q/K/V 学到的到底是什么？

## 202. 不一定是人类可命名的规则

某个 Head：

> 可能对局部语法关系敏感。

---

## 203. 另一个 Head

可能对：

> 长距离重复模式。

敏感。

---

## 204. 再一个

可能参与：

> 位置结构、列表、引用或实体关系。

---

## 205. 但不能简单说

> “Head 7 就是注册资本 Head。”

真实网络中的能力：

> 通常分布式存在。

---

# 三十、终于进入 Multi-Head Attention

## 206. 到目前为止

我们只讨论：

# Single-Head Attention

---

## 207. 但如果只有一个 Attention Head

它必须使用一个 Q/K 空间：

> 同时表示所有关系。

这可能限制表达能力。

---

## 208. 所以 Transformer 使用

# Multi-Head Attention

多头注意力。

---

## 209. 基本思想

不是只产生一组：

\[
Q,K,V
\]

而是产生：

\[
Q^{(1)},K^{(1)},V^{(1)}
\]

\[
Q^{(2)},K^{(2)},V^{(2)}
\]

……

---

## 210. 每个 Head

都有自己的：

> Attention Geometry。

于是可以：

> 在不同子空间里寻找不同关系。

---

# 三十一、Multi-Head Shape

## 211. 假设

\[
D=4096
\]

Head 数：

\[
H=32
\]

那么常见：

\[
d_h
=
\frac{4096}{32}
=
128
\]

---

## 212. 原输入

\[
X:
(B,S,4096)
\]

---

## 213. 投影后可以看成

\[
Q:
(B,S,32,128)
\]

---

## 214. 为计算方便常转置为

\[
\boxed{
(B,32,S,128)
}
\]

也就是：

\[
Batch
\times
Head
\times
Sequence
\times
HeadDim
\]

---

## 215. K、V 类似

\[
K:
(B,32,S,128)
\]

\[
V:
(B,32,S,128)
\]

---

## 216. 每个 Head 单独算

\[
Q_hK_h^T
\]

得到：

\[
(B,S,S)
\]

---

## 217. 32 个 Head 合起来

Attention Score：

\[
\boxed{
(B,32,S,S)
}
\]

---

## 218. 这就是为什么 Attention Matrix 很吃显存

当：

\[
S
\]

非常大，

\[
S^2
\]

增长非常快。

---

# 三十二、每个 Head 输出

## 219. 每个 Head：

\[
O_h=A_hV_h
\]

Shape：

\[
(B,S,128)
\]

---

## 220. 32 个 Head 拼接

得到：

\[
(B,S,4096)
\]

---

## 221. 然后还要一个

# Output Projection

\[
W_O
\]

---

## 222. 所以 Multi-Head Attention 完整结构

\[
\boxed{
X
\rightarrow
Q,K,V
\rightarrow
Heads
\rightarrow
Concat
\rightarrow
W_O
}
\]

---

## 223. \(W_O\) 的作用

让不同 Head 的输出：

> 再次混合。

否则：

> 每个 Head 永远各玩各的。

---

# 三十三、Multi-Head 的第五个核心心智模型

## 224. 心智模型 ⑤：Multi-Head 就是在多个不同表示子空间里同时建立关系，再把结果重新融合

不是简单：

> 把同一个 Attention 复制 32 次。

---

## 225. 每个 Head 有不同 Weight

所以可能：

> 学到不同匹配规则。

---

## 226. 但也可能出现 Head 冗余

多个 Head：

> 学到相似行为。

因此：

> Head 数更多并不自动等于能力线性增加。

---

# 三十四、参数量怎么算？

## 227. 假设所有 Projection

输入输出维度都是：

\[
D
\]

那么：

\[
W_Q:
D\times D
\]

---

## 228. 同样

\[
W_K:
D\times D
\]

\[
W_V:
D\times D
\]

---

## 229. Output：

\[
W_O:
D\times D
\]

---

## 230. 所以忽略 Bias

Attention Projection 参数约：

\[
\boxed{
4D^2
}
\]

---

## 231. 如果

\[
D=4096
\]

那么：

\[
4096^2
=
16,777,216
\]

---

## 232. 四份大约

\[
67.1M
\]

参数。

---

## 233. 这只是一个 Transformer Layer 的 Attention 部分

还没有算：

> MLP。

---

## 234. 而现代 Transformer 中

MLP 参数：

> 往往比 Attention 还多。

以后会继续拆。

---

# 三十五、Attention 的计算复杂度

## 235. Q/K/V Projection

大约有：

\[
O(SD^2)
\]

级别计算。

---

## 236. Score：

\[
QK^T
\]

大约：

\[
O(S^2d)
\]

---

## 237. 再算：

\[
AV
\]

又约：

\[
O(S^2d)
\]

---

## 238. 所以长 Context 下

\[
S^2
\]

部分：

> 会成为大问题。

---

## 239. 这就是第 9 阶段为什么说

Tokenizer 切得更碎：

> 会影响 Attention 成本。

现在内部机制完全看见了。

---

# 三十六、为什么 4K 到 128K 如此困难？

## 240. 序列长度从

\[
4096
\]

变：

\[
131072
\]

约增加：

\[
32\times
\]

---

## 241. naive Attention Matrix 面积增加：

\[
32^2
=
1024\times
\]

---

## 242. 所以长上下文问题

不仅是：

> Position Encoding。

还有：

\[
\boxed{
AttentionCompute
+
AttentionMemory
}
\]

---

# 三十七、FlashAttention 是什么？

## 243. 这是现代 LLM 工程中很重要的技术

# FlashAttention

---

## 244. 它是不是一种新 Attention 数学公式？

不是。

核心 Attention：

\[
Softmax
\left(
\frac{QK^T}{\sqrt d}
\right)V
\]

基本不变。

---

## 245. FlashAttention 的主要创新

是：

> 更聪明地安排 GPU 内存读取和分块计算。

---

## 246. naive 实现可能

把巨大的：

\[
S\times S
\]

Attention Matrix：

> 写到显存再读回来。

---

## 247. 但 GPU 很多时候

瓶颈不只是 FLOPs。

而是：

# Memory IO

---

## 248. FlashAttention 使用 Tiling

把 Q/K/V：

> 分块放入更快的片上存储。

---

## 249. 分块计算 Softmax 与输出

避免完整：

\[
S\times S
\]

矩阵在 HBM 中反复物化。

---

## 250. 第六个核心心智模型

### 心智模型 ⑥：FlashAttention 优化的是“怎样算 Attention”，而不是改变 Attention 在数学上是什么

这一区分很重要。

---

# 三十八、为什么 Softmax 分块并不简单？

## 251. 因为 Softmax 分母

\[
\sum_j e^{z_j}
\]

需要：

> 整行信息。

---

## 252. 如果只看一个 Block

还不知道：

> 后面的 Score 会不会更大。

---

## 253. 所以 FlashAttention 使用

# Online Softmax

维护：

- 当前最大值；
- 当前归一化总和；

并逐块更新。

---

## 254. 最终结果

可以与标准 Attention：

> 数学等价或在数值精度范围内一致。

---

# 三十九、为什么 Attention 不是“解释模型”的万能工具？

## 255. 很多人看到 Attention Map

就说：

> “模型因为关注这里，所以做出这个结论。”

这要非常谨慎。

---

## 256. Attention Weight 只是

某一：

- Layer；
- Head；
- Query；

中的：

> 中间 Routing Weight。

---

## 257. 最终输出还经过

- 多个 Head；
- \(W_O\)；
- Residual；
- Norm；
- MLP；
- 后续几十层。

---

## 258. 所以

\[
\boxed{
AttentionWeight
\neq
CausalExplanation
}
\]

---

## 259. 高 Attention 只能说明

在这个特定计算节点：

> 较多 Value 信息从该位置流入。

---

## 260. 不能直接说明

> 这个词就是最终判断的法律原因。

---

## 261. 这又连接第一课 Stage 12

\[
\boxed{
ModelExplanation
\neq
CausalExplanation
}
\]

---

# 四十、为什么 Attention Map 仍然有价值？

## 262. 它可以帮助

- Debug；
- 分析某些模式；
- 发现位置偏好；
- 研究 Head 行为。

---

## 263. 但应该作为

\[
\boxed{
DiagnosticEvidence
}
\]

而不是：

\[
\boxed{
FinalBusinessExplanation
}
\]

---

# 四十一、Self-Attention 与 MLP 的根本分工

## 264. 这是理解 Transformer 极重要的一条线

Attention：

\[
\boxed{
Mix\ information\ across\ positions
}
\]

---

## 265. MLP：

通常对每个 Token Position：

> 独立执行相同非线性变换。

---

## 266. 也就是说

Attention 解决：

> **Token 与 Token 之间通信。**

---

## 267. MLP 解决：

> **每一个 Token 内部的特征变换。**

---

## 268. 一个非常稳定的心智模型

\[
\boxed{
Attention
=
Communication
}
\]

\[
\boxed{
MLP
=
Computation
}
\]

虽然这只是抽象，但非常有用。

---

# 四十二、用政府采购专家团队类比

## 269. 假设每一个 Token

像一个：

> 小专家节点。

---

## 270. Attention 阶段

每个节点问：

> “为了理解我当前的问题，我应该去问谁？”

---

## 271. 然后从其它节点

读取：

> 相关信息。

---

## 272. MLP 阶段

节点拿到这些信息后：

> 自己做内部加工。

---

## 273. 下一层 Attention

又重新：

> 和其它节点交流。

---

## 274. 于是 Transformer Layer

反复：

\[
\boxed{
Communicate
\rightarrow
Compute
\rightarrow
Communicate
\rightarrow
Compute
}
\]

---

# 四十三、Residual 在哪里？

## 275. 第 7 阶段学过

一个典型 Pre-Norm Block：

\[
u
=
x+
Attention(Norm(x))
\]

---

## 276. 这意味着

Attention Output：

> 不是完全替换原表示。

而是：

\[
\boxed{
OldRepresentation
+
ContextUpdate
}
\]

---

## 277. 所以 Attention 可以理解成

给每个 Token：

> 计算一个“上下文修正量”。

---

## 278. 然后 MLP 再：

\[
y
=
u+
MLP(Norm(u))
\]

---

## 279. 所以整层就是

\[
\boxed{
ContextualUpdate
+
FeatureUpdate
}
\]

---

# 四十四、RoPE 在 Attention 的哪个位置？

## 280. 通常先：

\[
X\rightarrow Q,K,V
\]

---

## 281. 再对

\[
Q,K
\]

应用：

\[
RoPE
\]

---

## 282. 得到

\[
\tilde Q,\tilde K
\]

---

## 283. 然后算

\[
\boxed{
\tilde Q\tilde K^T
}
\]

---

## 284. 所以完整链条开始变成

\[
X
\rightarrow
Q,K,V
\rightarrow
RoPE(Q,K)
\rightarrow
Scores
\rightarrow
Mask
\rightarrow
Softmax
\rightarrow
V
\]

---

# 四十五、Attention 和 Position 终于真正合流

## 285. Query-Key Dot Product

决定：

> 内容匹配。

---

## 286. RoPE

让这个匹配：

> 对相对位置敏感。

---

## 287. Causal Mask

决定：

> 是否允许读取。

---

## 288. Softmax

决定：

> 读取比例。

---

## 289. V

提供：

> 被读取的内容。

---

## 290. 所以一个完整 Head 可以压缩成

\[
\boxed{
Content
+
Position
+
Access
\rightarrow
Routing
\rightarrow
Information
}
\]

---

# 四十六、Grouped-Query Attention 为什么出现？

## 291. 标准 Multi-Head Attention

假设：

\[
32
\]

个 Query Heads。

也有：

\[
32
\]

组 K/V Heads。

---

## 292. 推理时 KV Cache

每一层都要缓存：

> 每个过去 Token 的 K 和 V。

---

## 293. Context 很长时

KV Cache：

> 非常吃显存。

---

## 294. 所以 Multi-Query Attention

让所有 Query Heads：

> 共享一组 K/V。

---

## 295. 即

\[
H_Q=32
\]

但：

\[
H_{KV}=1
\]

---

## 296. 这样 KV Cache

可以大幅下降。

---

## 297. 但完全共享 K/V

可能损失：

> 一些表达能力。

---

## 298. 所以又有

# Grouped-Query Attention

---

## 299. 例如

\[
H_Q=32
\]

\[
H_{KV}=8
\]

---

## 300. 每 4 个 Query Head

共享：

> 一组 K/V Head。

---

## 301. 这形成折中

\[
\boxed{
Quality
\leftrightarrow
KVCacheCost
}
\]

---

## 302. 第七个核心心智模型

### 心智模型 ⑦：GQA/MQA 的核心不是改变 Query 的数量，而是减少需要保存的 K/V 头数

这对现代 LLM 推理：

> 极其重要。

---

# 四十七、KV Cache 大小怎么估？

## 303. 粗略看一层

需要缓存：

\[
K
\]

和：

\[
V
\]

---

## 304. 假设

Sequence：

\[
S
\]

KV Heads：

\[
H_{KV}
\]

Head Dim：

\[
d_h
\]

---

## 305. 每个 Token 每层缓存元素数

大致：

\[
\boxed{
2H_{KV}d_h
}
\]

前面的 2：

> K + V。

---

## 306. 整个 Sequence：

\[
2SH_{KV}d_h
\]

---

## 307. 再乘 Layer 数

\[
L
\]

得到：

\[
\boxed{
2LSH_{KV}d_h
}
\]

---

## 308. 再乘每个元素的 Byte

比如 BF16：

\[
2Bytes
\]

就能估 KV Cache Memory。

---

## 309. 所以 Context 越长

KV Cache：

\[
\boxed{
O(S)
}
\]

线性增长。

---

## 310. 注意

训练时 Attention Matrix naive memory：

> 可能涉及 \(S^2\)。

推理 KV Cache：

> 主要随 \(S\) 线性增长。

这是两个不同瓶颈。

---

# 四十八、一个简化 KV Cache 例子

## 311. 假设

\[
L=32
\]

\[
H_{KV}=8
\]

\[
d_h=128
\]

\[
S=32768
\]

BF16：

\[
2Bytes
\]

---

## 312. 元素数

\[
2
\times32
\times32768
\times8
\times128
\]

---

## 313. 大约是

\[
2.15\times10^9
\]

个元素。

---

## 314. ×2 Bytes

约：

\[
4.29GB
\]

仅仅 KV Cache：

> 就已经数 GB。

---

## 315. 如果 Batch 增大

还要：

> 再乘 Batch Size。

所以服务端 LLM：

> KV Cache 管理非常关键。

---

# 四十九、Attention 和 RAG 有什么本质区别？

## 316. RAG Retriever

在模型外：

> 从大量外部文档中选择相关 Chunk。

---

## 317. Attention

在当前 Context 内：

> 决定 Token 之间如何路由信息。

---

## 318. 所以

\[
\boxed{
RAG
=
ExternalSelection
}
\]

\[
\boxed{
Attention
=
InternalSelection
}
\]

---

## 319. 两者可以串起来

\[
Corpus
\rightarrow
RAG
\rightarrow
RelevantChunks
\rightarrow
Tokenizer
\rightarrow
Attention
\]

---

## 320. 这就是为什么好 RAG

可以减少 Attention：

> 在大量无关文本中寻找证据的负担。

---

# 五十、Attention 可以直接“检索法规库”吗？

## 321. 不能超出当前 Context

如果某法规文本：

> 没在参数有效知识里。

也没被 RAG：

> 放入 Context。

---

## 322. Self-Attention 没有魔法通道

去读取：

> 外部数据库。

---

## 323. 它只能处理

\[
\boxed{
当前HiddenStates
}
\]

之间的信息路由。

---

# 五十一、Attention 与模型参数知识

## 324. 那模型为什么没看到法规正文也可能回答？

因为训练过程中：

> 某些规律已经进入 Weight。

---

## 325. 但那属于

\[
\boxed{
ParametricKnowledge
}
\]

---

## 326. Attention 是利用当前 Context

结合这些 Weight：

> 进行动态计算。

---

## 327. 所以不要说

> “Attention 就是模型数据库。”

不准确。

---

# 五十二、Self-Attention 是否理解整个句子？

## 328. 单层 Attention

只做：

> 一次信息聚合。

---

## 329. 真正深层模型

有：

\[
几十层
\]

反复：

\[
Attention
+
MLP
\]

---

## 330. 第一层可能建立

> 局部关系。

---

## 331. 后续层可以在已经上下文化的表示上

继续：

> 建更复杂关系。

---

## 332. 所以模型最终能力来自

\[
\boxed{
IterativeContextualization
}
\]

不是：

> 一次 Attention 就完成全部理解。

---

# 五十三、一层的 Attention 能跨多远？

## 333. 理论上

如果没有 Mask 限制，

一个 Token 一层就可以：

> 直接看任意位置。

---

## 334. 这和 CNN 不同

CNN 需要多层：

> 才扩大 Receptive Field。

---

## 335. Self-Attention 一层

理论 Receptive Field：

> 就可以覆盖整个允许 Context。

---

## 336. 这是 Transformer 的一个强大特性

长距离 Token：

> 不需要通过 100 个局部邻居逐级传递。

---

## 337. 但“能够直接看”

不等于：

> 一定会正确使用。

再次：

\[
\boxed{
Reachability
\neq
Reliability
}
\]

---

# 五十四、采购长距离例子

## 338. 第 500 Token

写：

> “除特别说明外，现场服务不作属地限制。”

---

## 339. 第 15000 Token

某评分标准：

> “本地服务网点得5分。”

---

## 340. 理论上 Attention

可以：

> 建立跨 14500 Token 关系。

---

## 341. 但真实能力还取决于

- Position；
- 训练数据；
- Head 行为；
- 深度；
- 长 Context 泛化。

所以：

> 必须评测。

---

# 五十五、Attention 的 Weighted Sum 有一个数学特点

## 342. Softmax Weight：

\[
A_{ij}\ge0
\]

且：

\[
\sum_jA_{ij}=1
\]

---

## 343. 所以单个 Head 的

\[
o_i
\]

是 Value 向量的：

# Convex Combination

凸组合。

---

## 344. 也就是说单个 Head 输出

位于：

> Value 向量凸包内部。

---

## 345. 但整个 Transformer 并不会因此受严重限制

因为之后还有：

- \(W_O\)；
- Residual；
- MLP；
- 多层。

---

## 346. 所以最终 Representation

当然可以：

> 超出单个 Value 凸包。

---

# 五十六、为什么 Attention 输出还需要 \(W_O\)？

## 347. Multi-Head Concat 后

不同 Head：

> 各有自己的子空间。

---

## 348. \(W_O\)

允许：

> 跨 Head 组合这些信息。

---

## 349. 可以把它理解成

> “把 32 个专家返回的答案重新融合成统一 Hidden State。”

只是类比。

---

# 五十七、Attention Dropout

## 350. 某些 Transformer 训练中

会对 Attention Weight：

> 做 Dropout。

---

## 351. 即随机删除部分 Attention Link

帮助：

> Regularization。

---

## 352. 但不同现代 LLM

可能：

> 不使用或使用很小 Dropout。

所以不要认为：

> Attention 必然有 Dropout。

---

# 五十八、Attention Score 与 Probability 再区分一次

## 353. Raw Score

\[
q_i^Tk_j
\]

是：

# Logit-like Compatibility Score

---

## 354. Softmax 后

\[
A_{ij}
\]

虽然数学上像概率分布，

但它是：

> 路由分布。

---

## 355. 它不是

> 法律风险概率。

---

## 356. 也不是

> 事实真实性概率。

---

# 五十九、为什么 Attention 权重总和为 1 有时也有局限？

## 357. 因为 Token 之间必须竞争

即使：

> 所有位置都不太相关。

Softmax 仍然必须：

\[
\sum_jA_{ij}=1
\]

---

## 358. 所以至少有一些位置

会获得权重。

---

## 359. Residual Connection 很重要

因为模型不需要：

> 完全依赖 Attention 返回的信息。

原 Hidden State：

> 仍然直接保留下来。

---

# 六十、Attention Head 是否可以“不读任何人”？

## 360. 在纯 Softmax 结构里

它总会形成：

> 某种权重分布。

---

## 361. 但通过 Value、Output Projection 和 Residual

最终该 Head 的实际贡献：

> 可以非常小。

---

# 六十一、Attention Sink

## 362. 在长上下文研究里

你可能遇到：

# Attention Sink

---

## 363. 某些 Token

例如序列开头 Token：

> 可能吸收异常多 Attention。

---

## 364. 原因并不简单等于

> “开头内容最重要”。

可能与：

- Softmax；
- Causal structure；
- 训练动力学；

有关。

---

## 365. 这再次提醒我们

Attention Map：

> 不能机械按人类语义解释。

---

# 六十二、Self-Attention 和传统检索的区别

## 366. 传统检索

Query：

> 通常是一段独立文本。

数据库：

> 很大、静态。

---

## 367. Self-Attention

每一个 Token：

> 都同时产生 Query。

---

## 368. 同一个 Token

也同时产生：

> Key 和 Value。

---

## 369. 所以整个 Sequence

在一层里发生：

\[
\boxed{
AllToAllDynamicCommunication
}
\]

在允许的 Mask 范围内。

---

# 六十三、为什么 Self-Attention 如此强大？

## 370. 因为它把“连接结构”本身变成可学习、输入相关

传统固定网络：

> 谁连谁，架构预先决定。

---

## 371. Attention 中

Token \(i\) 到 Token \(j\) 的有效连接强度：

\[
A_{ij}
\]

每次输入：

> 都可以不同。

---

## 372. 所以我们可以把 Attention 看成

\[
\boxed{
DynamicGraph
}
\]

---

## 373. Token：

> 是节点。

Attention Weight：

> 是动态边权。

---

## 374. 每一层

模型根据当前 Hidden State：

> 重新生成一张关系图。

---

## 375. 下一层

Hidden State 已经变化。

于是：

> 关系图又会重新变化。

---

## 376. 这就是一种

\[
\boxed{
IterativeDynamicGraphReasoning
}
\]

的直觉。

注意：

> 这是帮助理解的抽象，不等于模型显式执行符号图推理。

---

# 六十四、ProcurementLM 中可能发生什么？

## 377. 第一层某些 Head

可能主要建立：

> 邻近词关系。

---

## 378. 中层

可能开始关联：

> “注册资本”与“资格条件”。

---

## 379. 更后层

可能把：

- 限制对象；
- 必要性；
- 竞争影响；

整合到更高层 Representation。

---

## 380. 但这些是概念性示意

真实模型：

> 不会严格按照我们命名的阶段运行。

---

# 六十五、Attention 能执行逻辑推理吗？

## 381. Attention 本身只是

\[
WeightedInformationRouting
\]

---

## 382. 逻辑能力来自

\[
\boxed{
Attention
+
MLP
+
Depth
+
Training
}
\]

共同作用。

---

## 383. 不应该把

> “Attention”

等同于：

> “Reasoning”。

---

# 六十六、为什么 MLP 不能被 Attention 完全替代？

## 384. Attention 很擅长

> 从其它位置读取信息。

---

## 385. 但如果没有足够的非线性 Feature Transformation

仅不断加权平均：

> 表达能力有限。

---

## 386. MLP 提供

\[
Linear
\rightarrow
Activation
\rightarrow
Linear
\]

强大的：

> 非线性变换。

---

## 387. 所以 Transformer Block 的两大核心：

\[
\boxed{
Attention
+
MLP
}
\]

一个通信。

一个计算。

---

# 六十七、Attention 和第 3 阶段 Representation Learning 合流

## 388. 原来 Token：

\[
x_i
\]

只是初始 Representation。

---

## 389. Attention 后：

\[
x_i'
\]

已经带有：

> 其它 Token 信息。

---

## 390. MLP 再将：

\[
x_i'
\]

变换成新的：

\[
h_i
\]

---

## 391. 下一层又继续。

所以：

\[
\boxed{
Representation
\rightarrow
Contextualize
\rightarrow
Transform
\rightarrow
Contextualize
\rightarrow
Transform
}
\]

---

# 六十八、Self-Attention 与 Embedding 的区别

## 392. Embedding

给一个 Token：

> 初始向量。

---

## 393. Self-Attention

根据当前上下文：

> 修改这个向量。

---

## 394. 所以同一个“本市”

初始 Embedding：

> 一样。

---

## 395. 经过 Self-Attention

句子 A：

> “项目地点位于本市。”

得到：

\[
h_A
\]

---

## 396. 句子 B：

> “供应商必须在本市注册。”

得到：

\[
h_B
\]

---

## 397. 一般：

\[
\boxed{
h_A\neq h_B
}
\]

这就是：

# Contextual Representation

真正形成的位置。

---

# 六十九、Self-Attention 和第 10 阶段 RoPE 合流

## 398. 没有 Position

Attention 主要根据：

> 内容向量匹配。

---

## 399. 加 RoPE 后

Q/K：

> 同时携带位置相位。

---

## 400. 所以模型可以区分

> “不得”在目标词前面 2 Token。

与：

> “不得”出现在 2000 Token 外无关章节。



# 七十、一个更完整的现代 Attention 公式

## 401. 输入

\[
X
\]

先 Norm：

\[
\bar X=Norm(X)
\]

---

## 402. Projection

\[
Q=\bar XW_Q
\]

\[
K=\bar XW_K
\]

\[
V=\bar XW_V
\]

---

## 403. Position

\[
\tilde Q=RoPE(Q)
\]

\[
\tilde K=RoPE(K)
\]

---

## 404. Scores

\[
S
=
\frac{\tilde Q\tilde K^T}
{\sqrt{d_h}}
+
M
\]

---

## 405. Weights

\[
A=Softmax(S)
\]

---

## 406. Read

\[
H=AV
\]

---

## 407. Multi-Head + Output

\[
O=Concat(H_1,\ldots,H_H)W_O
\]

---

## 408. Residual

\[
\boxed{
X'
=
X+O
}
\]

这已经非常接近真实 Transformer Attention Sub-layer。

---

# 七十一、如果只看一行代码应该看到什么？

## 409. 例如概念代码

```python
scores = q @ k.transpose(-2, -1)
scores = scores / sqrt(head_dim)
scores = scores + mask
weights = softmax(scores, dim=-1)
out = weights @ v
```

---

## 410. 第一行

\[
QK^T
\]

回答：

> 谁与谁匹配？

---

## 411. 第二行

控制：

> 数值尺度。

---

## 412. 第三行

控制：

> 谁可以看谁。

---

## 413. 第四行

变成：

> 归一化路由权重。

---

## 414. 第五行

真正：

> 从 Value 读取信息。

---

# 七十二、Self-Attention 最常见的 Shape Bug

## 415. Q Shape

\[
(B,H,S,d)
\]

K：

\[
(B,H,S,d)
\]

---

## 416. K 转置最后两维

得到：

\[
(B,H,d,S)
\]

---

## 417. Q @ Kᵀ

得到：

\[
\boxed{
(B,H,S,S)
}
\]

---

## 418. 如果你错误转置 Batch 或 Head

整个 Attention：

> 就错了。

所以：

\[
\boxed{
ShapeThinking
}
\]

再次成为核心技能。

---

# 七十三、Attention Mask Shape

## 419. Mask 可能原始是

\[
(B,S)
\]

表示：

> 哪些 Token 有效。

---

## 420. 为与 Score 广播

可能 reshape 成：

\[
(B,1,1,S)
\]

---

## 421. Causal Mask

可能是：

\[
(1,1,S,S)
\]

---

## 422. 两者可以组合

最终广播到：

\[
(B,H,S,S)
\]

---

## 423. 所以 Debug Attention

除了数值：

> 第一件事就是看 Shape。

---

# 七十四、Padding Mask 和 Causal Mask 组合

## 424. Padding Mask

阻止模型：

> 读取 PAD。

---

## 425. Causal Mask

阻止模型：

> 读取未来。

---

## 426. 两种 Mask 同时存在时

只要任一规定：

> 不可见。

这个 Score：

> 就应被 Mask。

---

# 七十五、Sequence Packing 再连接回来

## 427. 一条 Tensor 中有

文档 A：

\[
1\sim100
\]

文档 B：

\[
101\sim200
\]

---

## 428. 如果只使用普通 Causal Mask

文档 B：

> 可以看到文档 A。

---

## 429. 如果两者是完全独立训练样本

这是：

> Data Leakage。

---

## 430. 所以 Packing Mask

需要建立：

> Block-diagonal 可见区域。

---

## 431. 例如

A 只能看 A。

B 只能看 B。

---

## 432. 这就是第 10 阶段为什么说：

\[
\boxed{
PositionReset
\neq
DocumentIsolation
}
\]

现在通过 Attention Matrix：

> 已经看得非常清楚。

---

# 七十六、一个更深的“查询”理解

## 433. Query 不是自然语言搜索框

\[
q_i
\]

只是一个：

> 高维向量。

---

## 434. 它没有显式文字：

```text
请找和注册资本有关的信息
```

---

## 435. 这种“搜索意图”

是通过：

\[
W_Q
\]

把当前 Hidden State：

> 映射进 Query Space。

---

## 436. Key 同理

不存在显式标签：

```text
我是资格限制信息
```

---

## 437. 而是：

\[
W_K
\]

把 Hidden State：

> 映射到 Key Space。

---

## 438. 两者点积变大

意味着模型训练后形成：

> 某种匹配结构。

---

# 七十七、为什么 Q/K 空间可以很有表现力？

## 439. 因为不同 Head

有不同：

\[
W_Q^{(h)},W_K^{(h)}
\]

---

## 440. 一个 Token

可以同时在多个 Head 中：

> 扮演完全不同的搜索角色。

---

## 441. 例如同一个“本市”

某 Head：

> 参与地域关系。

另一个：

> 参与短语结构。

再一个：

> 参与位置或格式模式。

仍然只是概念化理解。

---

# 七十八、Attention Head 是“专家”吗？

## 442. 可以类比

但不要字面化。

---

## 443. Head 并没有：

> 独立完整知识库。

---

## 444. 而是一个：

\[
\boxed{
LowDimensionalAttentionSubspace
}
\]

---

## 445. 最终真正能力

由 Head 之间、Layer 之间：

> 大量交互形成。

---

# 七十九、Heads 能不能被剪掉？

## 446. 研究中常发现

某些 Attention Head：

> 比较冗余。

---

## 447. 剪掉部分 Head

有时：

> 性能下降并不大。

---

## 448. 这说明

模型能力：

> 存在冗余和分布式编码。

---

## 449. 所以再次不能说

> “这一头就是唯一负责法规引用。”

---

# 八十、Attention 是否总关注语义相似词？

## 450. 不一定

它也可以学习：

- 前一个 Token；
- 句首；
- 标点；
- 列表边界；
- 固定距离；
- 格式符号。

---

## 451. 因为训练目标不是

> “找到语义最相似的词”。

而是：

\[
\boxed{
降低Loss
}
\]

---

## 452. 只要某种 Attention Pattern

有助于 Next Token Prediction：

> 就可能被学习。

---

# 八十一、这和 RAG Embedding 再区分一次

## 453. RAG Embedding Similarity

目标通常：

> 找语义相关文档。

---

## 454. Attention Q/K

目标：

> 服务当前 Transformer 计算。

---

## 455. 所以不能把

\[
q_i^Tk_j
\]

理解成：

> 普通语义相似度。

它可能编码：

> 任何对任务有用的关系。

---

# 八十二、Attention 能学习复制吗？

## 456. 可以

例如语言中出现：

> 一个名称。

后面需要：

> 重复这个名称。

---

## 457. Attention 可以让后面位置

强烈读取：

> 前面对应 Token 的 Value。

---

## 458. 这种机制与某些

# Induction Head

研究现象有关。

---

## 459. Induction Pattern 粗略是什么？

序列中出现：

```text
A B ... A
```

模型看到第二个 A 时：

> 去找前一个 A 后面的 B。

---

## 460. 从而预测：

> B。

---

## 461. 这是 Attention 能学习

> 模式复制与上下文学习机制

的经典研究方向之一。

---

# 八十三、为什么 Attention 对 In-Context Learning 重要？

## 462. Prompt 中给示例：

```text
输入A → 输出A
输入B → 输出B
输入C →
```

---

## 463. 模型需要

> 在当前 Context 中寻找相关示例。

---

## 464. Attention 提供

> 动态读取 Prompt 中其它位置的能力。

---

## 465. 但 In-Context Learning

也不只是 Attention。

仍然依赖：

- MLP；
- 多层；
- 预训练形成的算法性能力。

---

# 八十四、Procurement Few-shot 例子

## 466. Prompt：

> 条款A → 风险类型：地域限制

> 条款B → 风险类型：注册资本限制

> 条款C → 风险类型：？

---

## 467. 模型可能通过 Attention

让条款 C：

> 读取与其相似的示例表示。

---

## 468. 然后后续层

完成：

> 任务映射。

---

# 八十五、Attention 与 Copying 也有风险

## 469. 如果 Prompt 中有错误示例

模型可能：

> 高度读取错误模式。

---

## 470. 所以 In-Context Example Quality

同样非常重要。

---

# 八十六、Attention 是不是“模型正在阅读”？

## 471. 可以作为类比

但要知道：

> 人类阅读和矩阵运算完全不是一回事。

---

## 472. 更准确的数学描述始终是

\[
\boxed{
Query-KeyCompatibility
\rightarrow
SoftmaxWeights
\rightarrow
ValueAggregation
}
\]

---

# 八十七、为什么每层都重新算 Attention？

## 473. 因为每经过一层

Hidden State：

\[
H_l
\]

已经改变。

---

## 474. 新层产生新的

\[
Q_l,K_l,V_l
\]

---

## 475. 所以新的关系图：

\[
A_l
\]

也会改变。

---

## 476. 这意味着

模型不是：

> 第 1 层决定一张 Attention Map，然后一直用。

而是：

\[
\boxed{
每一层重新定义Token之间的关系
}
\]

---

# 八十八、这就是“逐层重写关系图”

## 477. Layer 1：

> 看到表面词法关系。

---

## 478. Layer 10：

> 输入已经包含上下文。

它的 Query/Key：

> 是上下文化向量。

---

## 479. 所以 Layer 10 Attention

可以建立：

> 更抽象的关系。

---

## 480. Layer 30：

> 又在更高阶表示上重新路由。

---

# 八十九、为什么 Depth 很重要？

## 481. 一层 Attention

虽然能全局读取。

但一次 Weighted Sum：

> 无法完成所有复杂组合。

---

## 482. 多层允许

\[
\boxed{
Read
\rightarrow
Transform
\rightarrow
ReadAgain
\rightarrow
TransformAgain
}
\]

---

## 483. 例如采购判断可能概念上需要

第一步：

> 找资格条件。

---

## 484. 第二步：

> 找业务必要性说明。

---

## 485. 第三步：

> 比较二者关系。

---

## 486. 第四步：

> 结合风险模式。

真实模型不一定这样整齐，但：

> 多层使组合计算成为可能。

---

# 九十、Attention 能不能精确保存原 Token？

## 487. 有 Residual：

\[
X'=X+Attention(X)
\]

---

## 488. 所以原始 Representation

存在直接通路。

---

## 489. Attention 只需要学习：

> 应该添加什么上下文信息。

---

## 490. 这让模型无需

> 每层重新复制全部 Token Identity。

再次体现 Residual 的价值。

---

# 九十一、Self-Attention 与 LayerNorm

## 491. Pre-Norm 模型中：

\[
\bar X=RMSNorm(X)
\]

---

## 492. 然后：

\[
Q,K,V
\]

来自：

\[
\bar X
\]

---

## 493. 这样 Q/K Dot Product

输入 Scale：

> 更受控制。

---

## 494. 所以第 7 阶段的 Norm

与第 11 阶段 Attention：

> 终于完全连接。

---

# 九十二、为什么 Q/K Scale 尤其重要？

## 495. Dot Product：

\[
q^Tk
\]

直接受：

\[
\|q\|
\]

\[
\|k\|
\]

影响。

---

## 496. 如果向量 Norm 失控

Score：

> 也会失控。

---

## 497. 然后 Softmax：

> 极度饱和。

---

## 498. 所以：

\[
Normalization
+
\sqrt{d_k}\ Scaling
\]

都在帮助：

> Attention Logit 保持可训练。

---

# 九十三、现代模型还可能做 QK-Norm

## 499. 某些架构会直接对

\[
Q,K
\]

进一步：

> Normalize。

---

## 500. 目的之一

就是：

> 控制 Attention Score Scale。

---

## 501. 这说明架构仍然在不断优化

\[
\boxed{
AttentionStability
}
\]

而不是 2017 公式永远一成不变。

---

# 九十四、Attention Output 以后发生什么？

## 502. 单个 Block 中

Attention 只是第一部分。

---

## 503. 通常：

\[
X
\rightarrow
Norm
\rightarrow
Attention
\rightarrow
Residual
\]

---

## 504. 然后：

\[
\rightarrow
Norm
\rightarrow
MLP
\rightarrow
Residual
\]

---

## 505. 所以完整 Transformer Block 已经马上可以写出来：

\[
\boxed{
H'
=
H+
Attention(Norm(H))
}
\]

\[
\boxed{
H_{next}
=
H'
+
MLP(Norm(H'))
}
\]

---

# 九十五、这已经是现代 Decoder Block 的骨架

## 506. 还差一些具体设计差异

例如：

- RMSNorm / LayerNorm；
- GELU / SwiGLU；
- MHA / GQA；
- RoPE 配置；
- Bias 与否；
- Dropout 与否。

---

## 507. 但宏观骨架已经完全出现

\[
\boxed{
Attention
+
MLP
+
Residual
+
Norm
}
\]

---

# 九十六、Self-Attention 最容易出现的三个误解

## 508. 误解一

> Attention = 相似度搜索。

不完全。

它是：

> 任务训练出来的 Q/K 匹配空间。

---

## 509. 误解二

> Attention Weight = 模型解释。

不成立。

---

## 510. 误解三

> Attention 自己就是推理。

也不成立。

---

## 511. 更准确的统一理解

\[
\boxed{
Attention
=
LearnedDynamicInformationRouting
}
\]

---

# 九十七、Attention 与专家检索的类比边界

## 512. 可以类比：

Query：

> 当前问题。

Key：

> 专家标签。

Value：

> 专家知识。

---

## 513. 但真实 Q/K/V

不是：

> 人类可读结构化数据库。

---

## 514. 它们都是

\[
FloatingPointVectors
\]

由：

> Training Loss 塑造。

所以不要把类比：

> 当成真实内部符号结构。

---

# 九十八、一个完整 Procurement Attention 思维实验

## 515. 句子：

> “供应商注册资本不得低于5000万元。”

---

## 516. 假设当前后层正在处理

> “5000万元”

的 Hidden State。

---

## 517. 某个 Head 的 Query

可能在当前训练后表示空间里：

> 对“被什么条件修饰”这类关系敏感。

只是概念化描述。

---

## 518. “注册资本”的 Key

可能与它：

> 高度匹配。

---

## 519. “不得”“低于”的其它 Head

可能提供：

> 约束方向。

---

## 520. Value 被读回后

“5000万元”的新 Hidden State：

> 不再只是裸数字。

而开始携带：

> “注册资本下限条件”

的上下文信息。

---

## 521. 下一层

这个上下文化表示又可以：

> 与“供应商”建立关系。

---

## 522. 更后层

可能与：

> 资格条件、竞争限制等更抽象模式联系。

---

## 523. 最后分类或生成 Head

才能输出：

> 某种风险判断。

---

# 九十九、注意业务判断仍然不能只靠这个例子

## 524. “5000万元注册资本要求”

是否构成不合理条件：

> 必须结合实际任务、法规依据、业务必要性和上下文。

---

## 525. 我们这里只是在解释

> 神经网络如何建立 Token 之间的表示关系。

不是：

> 对具体采购项目作法律结论。

---

# 一百、Attention 与 Shortcut Learning

## 526. Attention 很强

不代表：

> 它一定学到正确机制。

---

## 527. 如果训练数据里

“5000万元”

总是风险样本，

模型可能学：

> 看到金额就提高风险。

---

## 528. 它甚至可以通过 Attention

非常高效地：

> 找到数字。

---

## 529. 但这仍然是

# Shortcut

---

## 530. 所以第一课 Stage 12 依然控制整个训练哲学

\[
\boxed{
StableMechanism
>
SurfaceCorrelation
}
\]

---

# 一百零一、Attention 只会帮助模型更有效利用它学到的规律

## 531. 如果规律错

Attention：

> 也可以高效路由错误规律。

---

## 532. 所以数据设计依然决定

> 模型最终学什么。

---

# 一百零二、为什么 Hard Negative 对 Attention 也重要？

## 533. 例如：

> “项目预算为5000万元。”

这是金额。

但不等于：

> 注册资本限制。

---

## 534. 如果训练数据缺少这种 Hard Negative

模型可能学：

> 5000万元 → 风险。

---

## 535. 加入对比样本

迫使模型真正利用：

> “注册资本”

> “不得低于”

> “供应商”

之间的关系。

---

## 536. 也就是迫使 Attention 和后续层

使用：

> 更完整上下文。

---

# 一百零三、Self-Attention 为什么特别适合语言？

## 537. 因为语言中的依赖距离不固定

主语和谓语：

> 有时相邻。

---

## 538. 有时中间隔几十个 Token

---

## 539. 法律引用

甚至：

> 相隔数千 Token。

---

## 540. 固定局部窗口

很难统一处理。

---

## 541. Self-Attention 允许

任何允许位置：

> 建立直接连接。

所以非常适合：

\[
\boxed{
VariableRangeDependencies
}
\]

---

# 一百零四、但全局 Attention 也有代价

## 542. 每个 Token 对所有 Token

就形成：

\[
S^2
\]

关系。

---

## 543. 所以长文档时代

出现大量：

- Sparse Attention；
- Sliding Window Attention；
- Block Sparse；
- Linear Attention；
- State-space 混合架构；

等研究。

---

## 544. 它们共同试图回答

> 能不能保留长距离能力，同时降低 \(S^2\) 成本？

---

# 一百零五、Sliding Window Attention

## 545. 一个简单办法

每个 Token：

> 只看附近 \(W\) 个 Token。

---

## 546. 这样复杂度大约从

\[
O(S^2)
\]

降到：

\[
O(SW)
\]

---

## 547. 但缺点

远距离 Token：

> 不能一层直接互相通信。

---

## 548. 可以通过多层

逐渐：

> 传递信息。

---

## 549. 某些模型也会混合

> Local + Global Attention。

---

# 一百零六、Procurement 长文档中的局部与全局

## 550. 技术参数表

很多关系：

> 很局部。

---

## 551. 但法规定义与后面条款

可能：

> 很全局。

---

## 552. 所以未来模型架构评估

也要问：

\[
\boxed{
模型的AttentionPattern是否适合长采购文档？
}
\]

---

# 一百零七、Attention Complexity 不只是理论

## 553. 你的采购文档从

\[
20K
\]

Token 增长到：

\[
40K
\]

---

## 554. naive \(S^2\) 部分

不是 2 倍。

而是：

\[
\boxed{
4倍
}
\]

---

## 555. 这就是为什么

Tokenizer Audit、RAG、Chunking、Long Context：

> 最终全部在 Attention 这里汇合。

---

# 一百零八、为什么 FlashAttention 仍不是无限长 Context 答案？

## 556. 它大幅优化

> Memory IO。

---

## 557. 但标准 Attention 的数学计算量

仍然存在：

\[
S^2
\]

核心项。

---

## 558. 所以长度持续增加

计算成本：

> 仍然非常高。

---

# 一百零九、Attention 与 GPU 的关系

## 559. QKV Projection

非常适合：

> Matrix Multiplication。

---

## 560. Score 计算

也是：

> Matrix Multiplication。

---

## 561. AV

又是：

> Matrix Multiplication。

---

## 562. 所以 GPU

能够很好利用：

> 大规模并行矩阵运算。

---

## 563. 这也是 Transformer

与现代 GPU：

> 非常匹配的重要原因之一。

---

# 一百一十、为什么矩阵乘法如此反复出现？

## 564. 第 1 阶段

\[
WX
\]

---

## 565. Embedding 可以理解成

\[
OneHot\times E
\]

---

## 566. Attention

\[
QK^T
\]

---

## 567. Output

\[
AV
\]

---

## 568. MLP

又是：

\[
XW
\]

---

## 569. 所以现代 LLM 极大部分计算

本质都是：

\[
\boxed{
LargeMatrixMultiplication
}
\]

再配合：

- Softmax；
- Activation；
- Norm；
- Elementwise operations。

---

# 一百一十一、第二课从神经元走到 Attention 的统一线

## 570. 神经元

\[
w^Tx
\]

---

## 571. Attention Score

\[
q^Tk
\]

---

## 572. 两者本质都有

\[
\boxed{
DotProduct
}
\]

---

## 573. 神经元中的 Weight

相对固定。

---

## 574. Attention 中被聚合的有效 Weight

\[
A_{ij}
\]

却：

> 根据输入动态产生。

---

## 575. 这是一个巨大飞跃

\[
\boxed{
StaticParameterizedComputation
\rightarrow
DynamicInputDependentRouting
}
\]

---

# 一百一十二、这也是 Transformer 强大的一个核心来源

## 576. 网络连接模式

不再完全固定。

---

## 577. 每个输入

都产生：

> 自己的 Attention Graph。

---

## 578. 所以：

> 不同句子可以走不同信息流。

---

# 一百一十三、本阶段最重要的七个专家心智模型

| 心智模型 | 核心认知 |
|---|---|
| **① Attention 是动态信息路由系统** | 每个 Token 根据当前输入决定从哪些 Token 读取多少信息 |
| **② Q/K 决定地址，V 提供内容** | Query 找什么、Key 如何匹配、Value 返回什么是三种不同角色 |
| **③ \(\sqrt{d_k}\) 是 Score 尺度稳定器** | 防止高维点积把 Softmax 推入过度饱和区 |
| **④ Attention Output 是 Value 的动态加权聚合** | \(o_i=\sum_jA_{ij}v_j\) 是核心计算 |
| **⑤ Multi-Head 在多个子空间并行建立关系** | 不同 Head 可以学习不同 Routing Geometry，再通过 \(W_O\) 融合 |
| **⑥ Attention Map 是计算中间量，不是因果解释** | 高权重不等于最终业务判断理由 |
| **⑦ GQA/MQA 用共享 K/V 换取更低推理成本** | 重点优化 KV Cache，而不是取消 Query 多样性 |

---

# 一百一十四、如果只记一个总公式

\[
\boxed{
Attention(Q,K,V)
=
Softmax
\left(
\frac{QK^T}{\sqrt{d_k}}
+
M
\right)V
}
\]

你应该能够逐字解释：

\[
QK^T
\]

是什么。

---

## 579. \(QK^T\)

回答：

> 谁应该关注谁？

---

## 580. \(\sqrt{d_k}\)

回答：

> 怎样让 Score 尺度稳定？

---

## 581. \(M\)

回答：

> 谁允许看谁？

---

## 582. Softmax

回答：

> 读取预算怎样分配？

---

## 583. \(V\)

回答：

> 真正读取什么信息？

---

# 一百一十五、如果只记 Q/K/V 三句话

\[
\boxed{
Query
=
我在找什么？
}
\]

\[
\boxed{
Key
=
我能被什么查询找到？
}
\]

\[
\boxed{
Value
=
找到我以后，我提供什么？
}
\]

虽然是类比，但对建立第一性理解非常有效。

---

# 一百一十六、如果只记一句话

\[
\boxed{
SelfAttention的本质，
就是让每个Token生成一个Query，
与所有允许访问Token的Key进行匹配，
把匹配结果变成权重，
再按这些权重动态读取它们的Value。
}
\]

---

# 一百一十七、第二课 8～11 阶段已经形成真正的语言计算链

Tokenizer：

\[
\boxed{
Text\rightarrow IDs
}
\]

Embedding：

\[
\boxed{
IDs\rightarrow Vectors
}
\]

Position / RoPE：

\[
\boxed{
Vectors\rightarrow PositionAwareVectors
}
\]

Self-Attention：

\[
\boxed{
PositionAwareVectors
\rightarrow
ContextualInformationMixing
}
\]

于是终于形成：

\[
\boxed{
Text
\rightarrow
Tokens
\rightarrow
Vectors
\rightarrow
Position
\rightarrow
ContextualInteraction
}
\]

这已经是 Transformer 的核心半边发动机。

---

# 一百一十八、第 11 阶段掌握标准

学完以后，你应该能够不靠背公式，自己解释：

> 为什么普通 Token Embedding 不足以形成上下文理解？

> 为什么 Attention 可以看成动态信息路由？

> Query、Key、Value 分别承担什么角色？

> 为什么 Q、K、V 来自同一个 X，却需要不同 Projection？

> 为什么说 Q/K/V 不一定数学上必须完全独立？

> \(QK^T\) 的 Shape 为什么是 \(S\times S\)？

> Attention Matrix 的一行和一列各是什么意思？

> 为什么要除以 \(\sqrt{d_k}\)？

> 为什么高维 Dot Product 不缩放会让 Softmax 饱和？

> Softmax 为什么适合把 Score 变成 Routing Weight？

> 为什么 Attention Weight 不是事实概率？

> 为什么实际 Softmax 要减最大值？

> 为什么最终输出是 \(AV\)？

> 为什么 \(o_i=\sum_jA_{ij}v_j\) 是 Self-Attention 的核心？

> Self-Attention 和 Cross-Attention 有什么区别？

> Causal Mask 是怎样通过 \(-\infty\) 阻止未来 Token 的？

> 为什么 Decoder-only 模型训练可以并行，而生成仍必须 Autoregressive？

> KV Cache 究竟缓存什么？

> 为什么 Multi-Head Attention 不是把同一套 Attention 重复几十次？

> Head Dim 和 Hidden Size 是什么关系？

> Multi-Head 拼接后为什么还要 \(W_O\)？

> 为什么 QK Score 通常不是对称的？

> 为什么 Attention 可以看成 Content-Addressable Memory？

> 为什么 Attention Weight 不能直接当业务因果解释？

> Attention 和 MLP 最核心的分工是什么？

> 为什么可以粗略记成 “Attention = Communication，MLP = Computation”？

> RoPE 在 Attention 公式中的什么位置发挥作用？

> MHA、MQA、GQA 三者为什么主要差在 K/V Head 数量？

> 为什么 GQA 可以显著节省 KV Cache？

> FlashAttention 改变的是 Attention 数学公式，还是计算方法？

> 为什么 FlashAttention 仍没有消除 \(S^2\) 的基本计算压力？

> RAG 与 Attention 为什么一个是外部选择、一个是内部选择？

> 为什么一层 Attention 虽然理论上能看到整个 Context，却不代表模型一定能可靠使用远距离信息？

如果这些问题已经能够从机制上完整解释：

\[
\boxed{
第二课第11阶段真正建立起来了
}
\]

下一阶段就非常自然了：
