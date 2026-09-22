# 第二课 · 第 12 阶段：Transformer Block 与完整 Decoder-only LLM
## 把 Embedding、RoPE、Attention、RMSNorm、SwiGLU、Residual、LM Head 全部组装起来——一个现代大语言模型到底是怎样从文字走到下一个 Token 的？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **LLM ≠ One Giant Layer。现代 Decoder-only LLM 是许多 Transformer Block 重复堆叠形成的系统。**
2. **RMSNorm / Residual / Attention / MLP 各自承担不同角色：稳定、信息通路、跨 Token 交互和逐位置非线性变换。**
3. **Decoder-only Transformer 使用 Causal Mask，通过 Next Token Prediction 学习序列分布。**
4. **LM Head 把最终 Hidden State 映射成 Vocabulary Logits；生成则把“选一个 Token”循环成完整文本。**
5. **KV Cache 只是在推理时减少历史 Attention 的重复计算，它不会给模型增加新知识或改变已训练权重。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Token` | Token：模型实际处理的离散文本单元 |
| `Attention` | 注意力：根据内容相关性动态聚合信息 |
| `Block` | 版面块：文档解析后保留布局和位置的基本块 |
| `Transformer` | Transformer：以注意力和前馈网络为核心的序列架构 |
| `Embedding` | 嵌入：把离散 Token 映射到连续高维向量 |
| `RMSNorm` | RMSNorm：基于均方根的轻量归一化 |
| `RoPE` | RoPE：旋转位置编码，把位置信息融入注意力 |
| `MLP` | MLP/前馈网络：对每个位置表示做非线性变换 |
| `State` | 状态：保存任务进度、事实和待办 |
| `Tokenizer` | 分词器：文本与 Token ID 之间的编码/解码组件 |
| `Representation` | 表示：模型内部承载语义或特征的向量结构 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |

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

前 11 个阶段，我们一直在拆零件。

我们拆过：

\[
Neuron
\]

\[
Activation
\]

\[
HiddenRepresentation
\]

\[
Forward
\]

\[
Backward
\]

\[
Optimizer
\]

\[
Initialization
+
Normalization
+
Residual
\]

然后进入语言模型：

\[
Tokenizer
\]

\[
Embedding
\]

\[
RoPE
\]

最后是：

\[
SelfAttention
\]

现在终于可以问：

> **这些东西合起来，到底是不是一个真正的大语言模型？**

还差最后一步：

\[
\boxed{
Assembly
}
\]

今天我们会从：

\[
\boxed{
一个TransformerBlock
}
\]

一直组装到：

\[
\boxed{
完整DecoderOnlyLLM
}
\]

最终得到：

\[
\boxed{
RawText
\rightarrow
Tokenizer
\rightarrow
Embedding
\rightarrow
TransformerBlocks
\rightarrow
FinalNorm
\rightarrow
LMHead
\rightarrow
Logits
\rightarrow
NextToken
}
\]

如果这一阶段真正吃透，第二课就结束了。

因为到那时，你不再只是“听说过 Transformer”。

你已经能从底层回答：

> 一个 LLM 到底在计算什么。

---

## 1. 先把完整模型画出来

一个现代 Decoder-only LLM，可以先抽象成：

```text
Raw Text
   ↓
Tokenizer
   ↓
Token IDs
   ↓
Token Embedding
   ↓
Transformer Block 1
   ↓
Transformer Block 2
   ↓
...
   ↓
Transformer Block L
   ↓
Final Norm
   ↓
LM Head
   ↓
Logits over Vocabulary
   ↓
Next Token
```

数学上：

\[
\boxed{
H_0
=
Embedding(TokenIDs)
}
\]

然后：

\[
H_1
=
Block_1(H_0)
\]

\[
H_2
=
Block_2(H_1)
\]

一直到：

\[
H_L
=
Block_L(H_{L-1})
\]

最后：

\[
\boxed{
Z
=
LMHead(Norm(H_L))
}
\]

其中：

\[
Z
\]

就是 Vocabulary Logits。

---

## 2. 第一个核心心智模型

### 心智模型 ①：LLM 不是一个“巨大函数块”，而是大量结构相同的 Transformer Block 反复改写同一条 Hidden Representation

可以写成：

\[
\boxed{
H_0
\rightarrow
H_1
\rightarrow
H_2
\rightarrow
\cdots
\rightarrow
H_L
}
\]

每一层：

> 都没有重新读取原始文字。

它处理的是：

> 上一层已经形成的 Hidden State。

---

## 3. 什么叫 Hidden State？

假设：

\[
B=2
\]

Batch 中有两个样本。

序列长度：

\[
S=512
\]

Hidden Size：

\[
D=4096
\]

那么：

\[
H_l
\in
\mathbb R^{2\times512\times4096}
\]

---

## 4. 这意味着什么？

每一个 Token：

> 在每一层，都有一个 4096 维向量。

所以第：

\[
l
\]

层里的第：

\[
i
\]

个 Token：

\[
h_i^{(l)}
\in
\mathbb R^{4096}
\]

---

## 5. 从第 0 层到最后一层

同一个 Token 的表示：

\[
h_i^{(0)}
\]

\[
h_i^{(1)}
\]

\[
h_i^{(2)}
\]

……

\[
h_i^{(L)}
\]

会不断变化。

---

## 6. 例如“本市”

最初：

\[
h_{\text{本市}}^{(0)}
\]

主要来自：

> Token Embedding。

经过上下文后：

\[
h_{\text{本市}}^{(10)}
\]

可能已经携带：

> 它出现在什么句子里。

---

## 7. 到更后层

\[
h_{\text{本市}}^{(L)}
\]

可能已经携带：

- 谁被要求；
- 要求的动作是什么；
- 是否存在强制关系；
- 前后是否有否定；
- 上下文是否提供必要性解释；

等等信息。

这里仍然只是：

> 概念化理解。

真实 Representation 是分布式向量。

---

# 一、Transformer Block 到底是什么？

## 8. 一个现代 Pre-Norm Decoder Block

最核心可以写成两行：

\[
\boxed{
U_l
=
H_l
+
Attention(Norm(H_l))
}
\]

然后：

\[
\boxed{
H_{l+1}
=
U_l
+
MLP(Norm(U_l))
}
\]

---

## 9. 就两大模块

第一个：

\[
Attention
\]

第二个：

\[
MLP
\]

---

## 10. 周围再加

\[
Norm
\]

和：

\[
Residual
\]

于是：

\[
\boxed{
Norm
+
Attention
+
Residual
+
Norm
+
MLP
+
Residual
}
\]

就是 Block 骨架。

---

## 11. 这张图非常值得记住

```text
              ┌───────────────┐
H_l ─────────►│               │
 │            │               ▼
 │         RMSNorm        Attention
 │            │               │
 │            └───────────────►│
 │                            │
 └─────────────────────── + ◄─┘
                              │
                              ▼
                              U_l
                              │
              ┌───────────────┤
              │               ▼
              │            RMSNorm
              │               │
              │              MLP
              │               │
              └────────── + ◄─┘
                              │
                              ▼
                           H_{l+1}
```

---

## 12. 第二个核心心智模型

### 心智模型 ②：一个 Transformer Block 做两件事——先让 Token 彼此通信，再让每个 Token 自己计算

可以压缩成：

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

然后：

\[
\boxed{
Residual
=
Preserve
+
Update
}
\]

---

# 二、第一半：Attention Sub-layer

## 13. 输入

\[
H_l
\]

先通过：

\[
RMSNorm
\]

得到：

\[
\bar H_l
\]

---

## 14. 为什么先 Norm？

第 7 阶段已经知道：

> 深层网络需要控制内部 Signal Scale。

所以：

\[
\boxed{
\bar H_l
=
RMSNorm(H_l)
}
\]

让 Attention 接收到：

> 更稳定尺度的 Hidden State。

---

## 15. 然后生成 Q/K/V

\[
Q
=
\bar H_lW_Q
\]

\[
K
=
\bar H_lW_K
\]

\[
V
=
\bar H_lW_V
\]

---

## 16. Q/K 再进入 RoPE

\[
\tilde Q
=
RoPE(Q)
\]

\[
\tilde K
=
RoPE(K)
\]

---

## 17. 然后计算 Attention Score

\[
S
=
\frac{\tilde Q\tilde K^T}
{\sqrt{d_h}}
+
M
\]

其中：

\[
M
\]

包含 Causal Mask 等可见性限制。

---

## 18. Softmax

\[
A
=
Softmax(S)
\]

---

## 19. 读取 Value

\[
C
=
AV
\]

---

## 20. 多个 Head 合并

\[
C_{all}
=
Concat(C_1,\ldots,C_H)
\]

---

## 21. 再经过 Output Projection

\[
O
=
C_{all}W_O
\]

---

## 22. 最后 Residual Add

\[
\boxed{
U_l
=
H_l+O
}
\]

---

## 23. 注意这里发生的事情

Attention 并没有：

> 把原表示删掉。

它只计算一个：

\[
\Delta H_{attention}
\]

然后：

\[
U_l
=
H_l
+
\Delta H_{attention}
\]

---

## 24. 这就是 Residual Stream 的第一层理解

可以把：

\[
H_l
\]

看成一条贯穿模型的：

# Residual Stream

---

## 25. Attention 往这条 Stream 里写入

> 上下文信息更新。

MLP 又继续：

> 写入特征变换更新。

---

## 26. 第三个核心心智模型

### 心智模型 ③：Residual Stream 是整个 Transformer 中贯穿几十层的“共享工作内存主干”

每个 Block 不是重新造一份表示。

而是在同一条主干上：

\[
\boxed{
Read
\rightarrow
ComputeUpdate
\rightarrow
AddBack
}
\]

---

# 三、第二半：为什么还必须有 MLP？

## 27. Attention 已经会交流了

为什么不堆：

\[
Attention
\rightarrow
Attention
\rightarrow
Attention
\]

就结束？

---

## 28. 因为 Attention 的核心是

\[
WeightedSum
\]

它非常擅长：

> 把不同位置的信息路由过来。

---

## 29. 但路由以后

Token 还需要：

> 非线性加工这些信息。

---

## 30. 例如一个 Token 已经读到了

- “供应商”；
- “注册资本”；
- “不得低于”；
- “5000万元”。

接下来需要形成：

> 更高阶组合表示。

这就是 MLP 擅长的部分之一。

---

# 四、最基础的 Feed-Forward Network

## 31. 经典 Transformer FFN 可以写成

\[
\boxed{
FFN(x)
=
W_2\phi(W_1x+b_1)+b_2
}
\]

---

## 32. 第一层通常升维

如果：

\[
D=4096
\]

可能变成：

\[
d_{ff}=11008
\]

或者其它更大的维度。

---

## 33. 所以

\[
4096
\rightarrow
11008
\]

---

## 34. 中间经过 Activation

例如经典模型可能使用：

\[
GELU
\]

---

## 35. 然后再降维

\[
11008
\rightarrow
4096
\]

---

## 36. 为什么最后必须回 4096？

因为需要：

\[
U_l+MLP(U_l)
\]

Residual Add。

两边 Shape：

> 必须兼容。

---

## 37. 所以一个普通 FFN

\[
\boxed{
D
\rightarrow
D_{ff}
\rightarrow
D
}
\]

---

# 五、为什么中间要升维？

## 38. 一个直觉

Hidden State：

\[
D
\]

是模型主通信维度。

---

## 39. MLP 中间扩大到

\[
D_{ff}
\]

给每个 Token：

> 更大的非线性特征空间。

---

## 40. 可以理解成

\[
\boxed{
Expand
\rightarrow
NonlinearTransform
\rightarrow
Compress
}
\]

---

## 41. 注意

升维不是为了：

> 永久让模型变宽。

而是给局部计算：

> 一个更大的中间工作空间。

---

# 六、现代 LLM 为什么常见 SwiGLU？

## 42. 很多现代 Decoder LLM

已经不只是：

\[
Linear
\rightarrow
GELU
\rightarrow
Linear
\]

---

## 43. 常见的是

# Gated MLP

例如：

# SwiGLU

---

## 44. 先理解 SiLU

\[
\boxed{
SiLU(x)
=
x\sigma(x)
}
\]

其中：

\[
\sigma(x)
=
\frac1{1+e^{-x}}
\]

---

## 45. SiLU 也常被称为

# Swish

的一种常用形式。

---

## 46. 它不像 ReLU 那样

负数全部：

\[
\rightarrow0
\]

而是：

> 平滑地控制输入。

---

# 七、SwiGLU 的核心结构

## 47. 对输入：

\[
x
\]

产生两个 Projection。

一个叫：

\[
Gate
\]

---

## 48. Gate Projection

\[
g
=
xW_g
\]

---

## 49. 另一个叫 Up Projection

\[
u
=
xW_u
\]

---

## 50. Gate 经过 SiLU

\[
\hat g
=
SiLU(g)
\]

---

## 51. 然后做逐元素乘法

\[
\boxed{
m
=
SiLU(xW_g)
\odot
(xW_u)
}
\]

---

## 52. 最后 Down Projection

\[
\boxed{
MLP(x)
=
mW_d
}
\]

---

## 53. 所以完整公式

\[
\boxed{
MLP(x)
=
\left[
SiLU(xW_g)
\odot
(xW_u)
\right]
W_d
}
\]

这就是一种常见 SwiGLU 结构。

---

# 八、为什么需要 Gate？

## 54. 先看普通 MLP

\[
\phi(xW)
\]

它只是：

> 变换后激活。

---

## 55. Gated MLP 多了一条分支

一条计算：

> “内容”。

另一条计算：

> “门”。

---

## 56. 然后：

\[
Gate
\times
Content
\]

---

## 57. 这意味着模型可以根据当前输入

动态决定：

> 哪些中间特征应该被放大。

> 哪些应该被抑制。

---

## 58. 第四个核心心智模型

### 心智模型 ④：SwiGLU 可以粗略理解成“一个分支产生特征，另一个分支决定这些特征开多大”

即：

\[
\boxed{
Feature
\times
InputDependentGate
}
\]

---

## 59. 为什么乘法很有价值？

加法关系：

\[
a+b
\]

通常是线性组合。

---

## 60. 乘法：

\[
a\odot b
\]

可以表达：

> 两组 Feature 之间更丰富的交互。

---

## 61. 所以 Gating 是另一种

\[
\boxed{
FeatureInteraction
}
\]

机制。

---

# 九、SwiGLU 的 Shape

## 62. 假设：

\[
x\in\mathbb R^D
\]

---

## 63. Gate Matrix：

\[
W_g
\in
\mathbb R^{D\times D_{ff}}
\]

---

## 64. Up Matrix：

\[
W_u
\in
\mathbb R^{D\times D_{ff}}
\]

---

## 65. 得到：

\[
g,u
\in
\mathbb R^{D_{ff}}
\]

---

## 66. Elementwise Product

仍是：

\[
D_{ff}
\]

维。

---

## 67. Down Matrix：

\[
W_d
\in
\mathbb R^{D_{ff}\times D}
\]

---

## 68. 最终：

\[
MLP(x)
\in
\mathbb R^D
\]

---

# 十、为什么现代 MLP 参数很多？

## 69. SwiGLU 有三个大矩阵

\[
W_g
\]

\[
W_u
\]

\[
W_d
\]

---

## 70. 参数量粗略：

\[
\boxed{
3DD_{ff}
}
\]

忽略 Bias。

---

## 71. 如果：

\[
D=4096
\]

\[
D_{ff}=11008
\]

一个矩阵大约：

\[
4096\times11008
\approx45.1M
\]

---

## 72. 三个就是：

\[
\boxed{
\approx135M
}
\]

参数。

---

## 73. 这意味着什么？

一个 Transformer Block：

> MLP 往往占很大一部分参数。

---

## 74. 所以一个重要误区是

> “LLM 的参数基本都在 Attention。”

不对。

---

## 75. 很多常见 Dense Transformer

MLP 参数量：

> 可以比 Attention 更大。

---

# 十一、Attention 参数重新算一次

## 76. 如果是标准 MHA

且：

\[
Q,K,V,O
\]

都是：

\[
D\rightarrow D
\]

---

## 77. 那么参数：

\[
W_Q:
D^2
\]

\[
W_K:
D^2
\]

\[
W_V:
D^2
\]

\[
W_O:
D^2
\]

---

## 78. 合计：

\[
\boxed{
4D^2
}
\]

---

## 79. 如果：

\[
D=4096
\]

大约：

\[
\boxed{
67.1M
}
\]

---

## 80. 与刚才 SwiGLU 比

Attention：

\[
67M
\]

MLP：

\[
135M
\]

---

## 81. 所以一个 Block 粗略：

\[
\boxed{
\approx202M
}
\]

再加：

> 很少量 Norm 参数。

这是一个说明数量级的例子。

---

# 十二、GQA 时 Attention 参数会下降

## 82. 假设：

\[
H_Q=32
\]

Head Dim：

\[
d_h=128
\]

所以：

\[
D=4096
\]

---

## 83. 如果 KV Heads：

\[
H_{KV}=8
\]

---

## 84. 那么 K/V 总宽度：

\[
8\times128=1024
\]

---

## 85. Q Projection 仍然

\[
4096\rightarrow4096
\]

---

## 86. 但 K Projection

变成：

\[
4096\rightarrow1024
\]

---

## 87. V 同样：

\[
4096\rightarrow1024
\]

---

## 88. Output Projection：

\[
4096\rightarrow4096
\]

---

## 89. 所以 GQA Attention 参数约

\[
D^2
+
D(D_{KV})
+
D(D_{KV})
+
D^2
\]

---

## 90. 即：

\[
\boxed{
2D^2
+
2DD_{KV}
}
\]

---

## 91. 在这个例子中

大约：

\[
16.78M
+
4.19M
+
4.19M
+
16.78M
\]

---

## 92. 合计：

\[
\boxed{
\approx41.9M
}
\]

比标准 MHA：

\[
67.1M
\]

更少。

---

## 93. 但 GQA 更大的生产优势仍然是

\[
\boxed{
KVCache
}
\]

显著减少。

---

# 十三、完整 Block 的 Shape 追踪

## 94. 假设输入

\[
H_l.shape
=
(B,S,4096)
\]

---

## 95. RMSNorm 后

\[
(B,S,4096)
\]

Shape：

> 不变。

---

## 96. Q：

\[
(B,32,S,128)
\]

---

## 97. K/V，如果 GQA 8 KV Heads：

\[
(B,8,S,128)
\]

---

## 98. 每 4 个 Query Head

共享：

> 一个 KV Head。

因为：

\[
32/8=4
\]

---

## 99. 逻辑上的 Attention Score

最终仍会对应：

\[
(B,32,S,S)
\]

---

## 100. Attention 输出合并后

回到：

\[
(B,S,4096)
\]

---

## 101. Residual

仍：

\[
(B,S,4096)
\]

---

## 102. 第二个 RMSNorm

还是：

\[
(B,S,4096)
\]

---

## 103. SwiGLU 两个 Up/Gate Projection

变成：

\[
(B,S,11008)
\]

---

## 104. Elementwise Gating

仍：

\[
(B,S,11008)
\]

---

## 105. Down Projection

回：

\[
(B,S,4096)
\]

---

## 106. Residual Add

最终：

\[
\boxed{
H_{l+1}.shape
=
(B,S,4096)
}
\]

---

# 十四、为什么几十层 Shape 一直不变？

## 107. 因为 Residual Stream 的主维度

\[
D
\]

需要保持稳定。

---

## 108. 所以 Block 1：

\[
(B,S,D)
\]

输入。

输出：

\[
(B,S,D)
\]

---

## 109. Block 2：

仍然：

\[
(B,S,D)
\]

---

## 110. 一直：

\[
Block_L
\]

也不变。

---

## 111. 这使 Transformer 可以

> 非常规则地堆叠。

---

# 十五、第五个核心心智模型

### 心智模型 ⑤：Transformer 的深度不是不断改变 Tensor 外形，而是在固定 Shape 的 Residual Stream 上不断改变“内容”

\[
\boxed{
Shape\ Stable
,\quad
Meaning\ Evolves
}
\]

这是读模型架构时非常重要的认知。

---

# 十六、一个 Block 可以写成非常短的伪代码

## 112. 概念版本：

```python
def block(x):
    x = x + attention(norm1(x))
    x = x + mlp(norm2(x))
    return x
```

---

## 113. 真实模型当然更复杂

Attention 内部有：

- QKV Projection；
- RoPE；
- Mask；
- GQA；
- FlashAttention；
- Output Projection。

---

## 114. MLP 内部可能有：

- Gate Projection；
- Up Projection；
- SiLU；
- Elementwise Multiply；
- Down Projection。

---

## 115. 但宏观上：

```python
x = x + attention(norm(x))
x = x + mlp(norm(x))
```

仍然抓住了核心。

---

# 十七、为什么一层要两个 Norm？

## 116. 因为 Attention 和 MLP

都是：

> 两个独立的大型变换模块。

---

## 117. Pre-Norm 架构通常分别给它们

一个：

\[
Norm
\]

---

## 118. 第一份：

\[
Norm_{attn}
\]

稳定 Attention 输入。

---

## 119. 第二份：

\[
Norm_{mlp}
\]

稳定 MLP 输入。

---

## 120. 它们的参数

通常：

> 不是同一份。

---

# 十八、RMSNorm 参数有多少？

## 121. 如果：

\[
D=4096
\]

一个典型 RMSNorm 通常有一个：

\[
\gamma
\in
\mathbb R^{4096}
\]

---

## 122. 所以：

\[
4096
\]

个参数。

---

## 123. 两个 Norm：

\[
8192
\]

---

## 124. 和一亿级 MLP 参数相比

几乎：

> 很小。

---

## 125. 但参数少不等于不重要

Norm：

> 对训练稳定性极其关键。

---

# 十九、参数量和功能重要性不是同一个概念

## 126. RMSNorm

参数：

> 极少。

---

## 127. RoPE

甚至可以：

> 几乎没有训练参数。

---

## 128. Causal Mask

没有：

> 模型参数。

---

## 129. 但这些结构

全部对：

> 模型行为极其重要。

所以：

\[
\boxed{
ParameterCount
\neq
ArchitecturalImportance
}
\]

---

# 二十、几十个 Block 怎么叠起来？

## 130. 假设：

\[
L=32
\]

---

## 131. 那么：

\[
H_0=Embedding(ids)
\]

---

## 132. Layer 1：

\[
H_1=Block_1(H_0)
\]

---

## 133. Layer 2：

\[
H_2=Block_2(H_1)
\]

---

## 134. ……

---

## 135. Layer 32：

\[
H_{32}=Block_{32}(H_{31})
\]

---

## 136. 每一个 Block

结构：

> 大致相同。

---

## 137. 但参数：

> 通常不同。

---

## 138. 即：

\[
W_Q^{(1)}
\neq
W_Q^{(2)}
\]

等等。

---

## 139. 所以不是

> 同一个 Block 重复执行 32 次。

而是：

> 32 组独立学习的 Block。

---

# 二十一、不同层到底学什么？

## 140. 不能简单规定

> 第 1 层学词法。

> 第 10 层学法律。

> 第 30 层学推理。

---

## 141. 真实模型：

> 没有这种人工硬分工。

---

## 142. 但一般可以理解

随着深度增加：

\[
H_l
\]

会越来越：

> 上下文化。

---

## 143. 后层处理的输入

已经是：

> 前面多层加工后的表示。

---

## 144. 所以后层有机会建立

> 更复杂组合关系。

---

## 145. 但“越后越高级”

也不是：

> 永远严格成立的定律。

---

# 二十二、不要把 Transformer Layer 当成“思维步骤”

## 146. 这是一个很常见误区

比如：

> 32 层模型是不是思考 32 步？

不是。

---

## 147. 一个 Layer

不是：

> 一句人类可解释推理步骤。

它是：

\[
\boxed{
连续向量变换
}
\]

---

## 148. 人类最终看到的 Chain-of-Thought

与内部 Layer：

> 不是一一对应。

---

# 二十三、32 层以后为什么还要 Final Norm？

## 149. 最后得到：

\[
H_L
\]

---

## 150. 通常再做：

\[
\boxed{
H_{final}
=
Norm(H_L)
}
\]

---

## 151. 为什么？

让送进输出 Head 的 Hidden State：

> 尺度更加稳定。

---

## 152. 这叫：

# Final Norm

---

# 二十四、然后终于进入 LM Head

## 153. LM：

# Language Model

所以：

# LM Head

就是语言模型输出头。

---

## 154. 每个 Token 最后的 Hidden Vector：

\[
h_i
\in
\mathbb R^D
\]

---

## 155. 但我们的目标是预测：

> 下一个 Token 是 Vocabulary 里的哪一个。

Vocabulary Size：

\[
V
\]

---

## 156. 所以需要从：

\[
D
\]

映射到：

\[
V
\]

---

## 157. 创建一个输出矩阵

一种记法：

\[
W_U
\in
\mathbb R^{V\times D}
\]

---

## 158. 那么：

\[
\boxed{
z_i
=
W_Uh_i
}
\]

得到：

\[
z_i
\in
\mathbb R^V
\]

---

## 159. 这就是 Vocabulary Logits

假设：

\[
V=100000
\]

那么一个 Token Position：

> 输出 10 万个 Logit。

---

# 二十五、第六个核心心智模型

### 心智模型 ⑥：LM Head 本质上是在问——当前 Hidden State 与词表中每个候选 Token 的输出方向有多匹配？

\[
\boxed{
HiddenState
\rightarrow
VocabularyScores
}
\]

---

# 二十六、Logit 又出现了

## 160. 例如：

\[
z=
[-2.1,1.4,8.7,\ldots]
\]

---

## 161. 它还不是概率。

和第一课一样：

\[
\boxed{
Logit
\neq
Probability
}
\]

---

## 162. Softmax 后：

\[
p_j
=
\frac{e^{z_j}}
{\sum_k e^{z_k}}
\]

才得到：

\[
P(Token_j\mid Context)
\]

---

# 二十七、一个语言模型真正学的目标出现了

## 163. 假设 Context：

> “供应商必须在本市”

真实下一 Token：

> “注册”

---

## 164. 模型产生：

\[
P(Token\mid Context)
\]

---

## 165. 我们希望：

\[
P(\text{注册}\mid Context)
\]

尽可能高。

---

## 166. 所以 Loss：

\[
\boxed{
L
=
-\log
P(y_{true}\mid Context)
}
\]

---

## 167. 这就是多分类 Cross Entropy

Vocabulary 中：

> 10 万类。

---

# 二十八、语言模型训练不是只预测最后一个 Token

## 168. 给定：

```text
供应商 必须 在 本市 注册
```

---

## 169. 输入可以：

\[
[x_1,x_2,x_3,x_4]
\]

目标：

\[
[x_2,x_3,x_4,x_5]
\]

---

## 170. 也就是整体右移一位。

这常叫：

# Label Shift

---

## 171. 位置 1：

根据：

> “供应商”

预测：

> “必须”。

---

## 172. 位置 2：

根据：

> “供应商 必须”

预测：

> “在”。

---

## 173. 位置 3：

预测：

> “本市”。

---

## 174. 位置 4：

预测：

> “注册”。

---

## 175. 所以一条长文本

可以同时产生：

> 大量训练目标。

---

# 二十九、Causal Mask 的价值现在完全看清了

## 176. 训练 Tensor 里虽然有整个文本

但位置：

\[
i
\]

只能看：

\[
\le i
\]

---

## 177. 然后预测：

\[
i+1
\]

---

## 178. 所以：

\[
\boxed{
CausalMask
+
ShiftedLabels
}
\]

共同形成：

# Causal Language Modeling

---

# 三十、完整训练目标

## 179. 一条序列：

\[
x_1,x_2,\ldots,x_T
\]

---

## 180. 模型希望最大化：

\[
\boxed{
P(x_1,x_2,\ldots,x_T)
=
\prod_{t=1}^{T}
P(x_t\mid x_{<t})
}
\]

---

## 181. 取 Log：

\[
\log P(X)
=
\sum_t
\log P(x_t\mid x_{<t})
\]

---

## 182. 训练最小化负对数似然：

\[
\boxed{
L
=
-\sum_t
\log P(x_t\mid x_{<t})
}
\]

---

## 183. 这就是一个非常深的答案

LLM 预训练表面上：

> 只是预测下一个 Token。

---

## 184. 但为了把下一个 Token 预测好

模型被迫学习：

- 语法；
- 语义；
- 世界规律；
- 文档结构；
- 某些知识；
- 某些推理模式；
- 代码模式；
- 人类表达规律。

---

## 185. 但一定注意

\[
\boxed{
NextTokenPrediction
\neq
GuaranteeOfTruth
}
\]

---

## 186. 它优化的是：

> 哪个 Token 在当前训练分布中更可能出现。

---

## 187. 不直接优化：

> 法律结论必须真实。

> 引用必须准确。

> 业务建议必须合规。

---

## 188. 第一课那句话再次成为底层原则

\[
\boxed{
YouGetWhatYouOptimize
}
\]

---

# 三十一、为什么大模型会“回答问题”？

## 189. 因为问答文本本身

也可以写成：

```text
问题：……
答案：……
```

---

## 190. 预训练模型学会大量：

> 文本延续模式。

---

## 191. Instruction Tuning / SFT

进一步告诉模型：

> 当 Context 是某种用户指令时，应该延续什么样的 Assistant Response。

---

## 192. 所以 Chat Model 本质上仍然：

\[
\boxed{
ConditionalNextTokenPrediction
}
\]

---

# 三十二、SFT 有没有改变 Transformer 结构？

## 193. 通常没有。

仍然是：

\[
Embedding
\rightarrow
Blocks
\rightarrow
LMHead
\]

---

## 194. 改变的是：

\[
\boxed{
Weights
}
\]

---

## 195. 通过新的监督数据

Loss 重新塑造：

- Attention Projection；
- MLP；
- Embedding；
- Norm；

等参数。

---

# 三十三、SFT 数据里 Loss 一定计算所有 Token 吗？

## 196. 不一定。

例如对话：

```text
User: 请审查……
Assistant: 存在以下风险……
```

---

## 197. 有一种做法

User Token：

> 只作为 Context。

不计算它们的预测 Loss。

---

## 198. Assistant Token：

> 才是监督目标。

---

## 199. 即：

\[
LossMask_{prompt}=0
\]

\[
LossMask_{assistant}=1
\]

---

## 200. 这样模型主要学习：

> 给定用户输入，如何生成目标回答。



# 三十四、这就是 SFT 与 Attention Mask 不同

## 201. Attention Mask

控制：

> 能不能看。

---

## 202. Loss Mask

控制：

> 这个 Token 的预测错了以后，要不要算 Loss。

---

## 203. 又是两个完全不同的 Mask。

\[
\boxed{
AttentionMask
\neq
LossMask
}
\]

---

# 三十五、一个 Procurement SFT 样本进入模型发生什么？

## 204. 输入：

> “请审查以下供应商资格要求：供应商注册资本不得低于5000万元。”

---

## 205. Tokenizer：

\[
Text
\rightarrow
TokenIDs
\]

---

## 206. Embedding：

\[
TokenIDs
\rightarrow
H_0
\]

---

## 207. Block 1：

> Attention 建立局部关系。

> MLP 做特征变换。

得到：

\[
H_1
\]

---

## 208. 一直经过：

\[
H_L
\]

---

## 209. LM Head：

> 对下一个回答 Token 产生 Vocabulary Logits。

---

## 210. 如果专家答案第一 Token 是：

> “存在”

模型却更倾向：

> “未”

---

## 211. Cross Entropy：

> 产生 Loss。

---

## 212. Backprop：

> 把责任一路传回几十层。

---

## 213. Optimizer：

> 修改相关参数。

---

## 214. 千千万万个样本以后：

模型逐渐学会：

> 哪类输入应该延续出哪类专业回答。

---

# 三十六、知识到底“存在哪里”？

## 215. 这是一个非常重要的问题。

答案不是：

> “都在 Embedding。”

---

## 216. 也不是：

> “都在 Attention。”

---

## 217. 更准确：

\[
\boxed{
Knowledge
\ is\
DistributedAcrossParameters
}
\]

---

## 218. Token Embedding：

> 存部分基础符号表示。

---

## 219. Attention Projection：

> 存某些关系匹配与路由结构。

---

## 220. MLP：

> 存大量特征变换结构。

---

## 221. Layer 之间：

> 共同构成复杂计算。

---

## 222. 所以不能打开某一个 Weight

说：

> “这里就是《政府采购法》第22条。”

---

# 三十七、MLP 是不是“知识库”？

## 223. 有研究发现

MLP/FFN 与模型某些知识行为：

> 有很强关系。

---

## 224. 但说：

> “全部知识都存储在 MLP”

仍然过度简化。

---

## 225. 因为输出行为还依赖：

- Embedding；
- Attention；
- Residual Stream；
- Layer interaction；
- Context。

---

## 226. 更可靠的说法：

\[
\boxed{
能力和知识是整个网络分布式实现的
}
\]

---

# 三十八、Weight Tying

## 227. 这里有一个很漂亮的设计。

输入 Embedding Matrix：

\[
E
\in
\mathbb R^{V\times D}
\]

---

## 228. 输出 LM Head 也需要：

\[
V\times D
\]

大小的 Weight。

---

## 229. 那能不能：

> 共用同一份参数？

可以。

---

## 230. 这叫：

# Weight Tying

---

## 231. 即可能使用：

\[
\boxed{
W_U=E
}
\]

或等价的转置使用方式，取决于实现约定。

---

## 232. 这意味着

输入时：

> Token ID 从 E 中取 Row。

输出时：

> Hidden State 又和这些 Token 向量计算输出 Score。

---

## 233. 好处之一

显著减少：

> 参数量。

---

## 234. 但不是所有模型

都必须 Weight Tying。

---

## 235. 所以看到模型配置时

应该确认：

> Input Embedding 和 LM Head 是否共享参数。

---

# 三十九、LM Head 参数能有多大？

## 236. 假设：

\[
V=100000
\]

\[
D=4096
\]

---

## 237. 参数：

\[
100000\times4096
\]

---

## 238. 等于：

\[
409,600,000
\]

即：

\[
\boxed{
409.6M
}
\]

---

## 239. 如果 Input Embedding 又独立一份

再来：

\[
409.6M
\]

---

## 240. 所以 Weight Tying

可能省掉：

> 数亿参数。

---

# 四十、Vocabulary Size 的影响再次回来

## 241. 词表变大：

\[
V\uparrow
\]

---

## 242. Input Embedding：

\[
V\times D
\]

变大。

---

## 243. LM Head：

\[
V\times D
\]

也可能变大。

---

## 244. 最后每个 Position 的 Logits：

\[
V
\]

也变大。

---

## 245. 所以 Tokenizer 的 Vocabulary Size

一直影响到：

> 模型最后一层。

---

# 四十一、一个完整 Shape Trace

假设：

\[
B=2
\]

\[
S=512
\]

\[
D=4096
\]

\[
V=100000
\]

---

## 246. Token IDs：

\[
\boxed{
(2,512)
}
\]

---

## 247. Embedding：

\[
\boxed{
(2,512,4096)
}
\]

---

## 248. 32 层 Transformer 后：

\[
\boxed{
(2,512,4096)
}
\]

Shape 不变。

---

## 249. Final Norm：

\[
\boxed{
(2,512,4096)
}
\]

---

## 250. LM Head：

\[
\boxed{
(2,512,100000)
}
\]

---

## 251. 也就是说

一批只有 2 个样本、512 Token，

最后产生：

\[
2\times512\times100000
\]

---

## 252. 即：

\[
102,400,000
\]

个 Logit。

---

## 253. 所以 Vocabulary Logits

本身也可能：

> 非常吃显存。

---

# 四十二、训练时一定要存完整 Softmax Probability 吗？

## 254. 不一定。

高效框架通常会使用：

> Fused Cross Entropy 等实现。

---

## 255. 目标是减少：

> 中间 Tensor 物化和 Memory Traffic。

---

## 256. 这和 FlashAttention 的工程思想类似：

\[
\boxed{
数学目标不变，
重新组织计算方式
}
\]

---

# 四十三、从 Logits 怎么真正生成 Token？

## 257. 推理时我们通常只需要

> 最后一个当前位置的 Logits。

---

## 258. 设：

\[
z\in\mathbb R^V
\]

---

## 259. 最简单：

# Greedy Decoding

选择：

\[
\boxed{
argmax_j z_j
}
\]

---

## 260. 就是：

> 永远选择最高分 Token。

---

# 四十四、Greedy 的问题

## 261. 它是：

> 确定性的。

---

## 262. 但语言生成不一定需要：

> 每次都选择最高概率 Token。

---

## 263. 所以可以：

> 从概率分布 Sampling。

---

# 四十五、Temperature

## 264. Logits 可以除：

\[
T
\]

---

## 265. 概率：

\[
\boxed{
p
=
Softmax(z/T)
}
\]

---

## 266. 如果：

\[
T<1
\]

分布：

> 更尖锐。

---

## 267. 如果：

\[
T>1
\]

分布：

> 更平坦。

---

## 268. 但一定注意

Temperature：

> 不改变模型参数。

---

## 269. 它没有让模型：

> 知道更多知识。

---

## 270. 只是改变：

\[
\boxed{
SamplingDistribution
}
\]

---

# 四十六、Top-k

## 271. 假设 Vocabulary：

\[
100000
\]

---

## 272. Top-k 只保留：

> 最高的 \(k\) 个 Token。

---

## 273. 例如：

\[
k=50
\]

其余候选：

> 删除。

---

# 四十七、Top-p

## 274. 又叫：

# Nucleus Sampling

---

## 275. 按概率排序。

保留最小候选集合，使累计概率：

\[
\ge p
\]

---

## 276. 例如：

\[
p=0.9
\]

---

## 277. 如果分布很尖锐

可能只保留：

> 几个 Token。

---

## 278. 如果分布很平

可能保留：

> 很多 Token。

---

# 四十八、政府采购专业任务为什么通常不希望 Temperature 太高？

## 279. 因为很多任务目标是：

- 稳定；
- 可重复；
- 少幻觉；
- 严谨措辞。

---

## 280. 高随机性

可能：

> 让表达更加多样。

但也可能：

> 增加不稳定。

---

## 281. 所以专业系统

通常需要根据：

> 任务类型调 Decode Policy。

---

## 282. 但：

\[
\boxed{
低Temperature
\neq
自动正确
}
\]

---

## 283. 如果模型最可能答案本身错

Greedy：

> 只会稳定地输出错误。

---

# 四十九、Decoder-only 为什么叫 Decoder-only？

## 284. 原始 Transformer

有：

- Encoder；
- Decoder。

---

## 285. Encoder

通常：

> 双向读取输入。

---

## 286. Decoder

通常：

> Causal 自回归生成。

---

## 287. 现代很多通用 LLM

只使用：

> Decoder 风格 Block。

所以：

# Decoder-only

---

## 288. 例如它没有单独的 Encoder Stack

Prompt：

> 直接进入同一个 Causal Transformer。

---

## 289. 然后在 Prompt 后：

> 继续预测 Token。

---

# 五十、为什么只靠 Decoder 也能“理解”输入？

## 290. 因为 Prompt Token

都在生成位置之前。

---

## 291. 后面的 Token：

> 可以 Attention 到所有前面 Prompt。

---

## 292. 所以虽然模型是 Causal 的

生成阶段仍可以利用：

> 整个 Prompt。

---

## 293. 例如：

```text
[长采购文件]
[用户问题]
[Assistant:]
```

---

## 294. Assistant 后续 Token

可以读取：

> 前面允许 Context 中的全部信息。

---

# 五十一、Encoder-only 又适合什么？

## 295. 例如经典 BERT 风格模型

可以双向 Attention。

---

## 296. 它特别适合：

- 分类；
- 抽取；
- Embedding；
- 理解类任务。

---

## 297. 但原生结构：

> 不以自回归长文本生成为核心。

---

# 五十二、Encoder-Decoder 呢？

## 298. 输入先经过 Encoder。

---

## 299. Decoder：

> 使用 Cross-Attention 读取 Encoder Representation。

---

## 300. 适合很多：

- 翻译；
- 摘要；
- Seq2Seq；

任务。

---

## 301. 所以三个架构不是

> 谁绝对先进。

而是：

\[
\boxed{
不同信息流设计
}
\]

---

# 五十三、现代 LLM 一次推理其实分两阶段

## 302. 第一阶段：

# Prefill

---

## 303. 模型一次处理：

> 整个 Prompt。

---

## 304. 为每一层计算：

\[
K,V
\]

---

## 305. 并建立：

# KV Cache

---

## 306. Prefill 阶段

可以：

> 大量并行处理 Token。

---

# 五十四、第二阶段：Decode

## 307. 然后开始逐 Token 生成。

---

## 308. 每一步只有：

> 一个或少量新 Token。

---

## 309. 使用过去：

\[
KVCache
\]

---

## 310. 所以：

# Decode

与：

# Prefill

的计算特征：

> 很不同。

---

## 311. 第七个核心心智模型

### 心智模型 ⑦：LLM 推理不是一个均匀过程，而是“Prefill 批量读 Prompt + Decode 逐 Token 生成”

这个区别对：

> GPU 性能、延迟、服务架构

极其重要。

---

# 五十五、TTFT 与 TPS

## 312. 用户输入长 Prompt。

等待模型开始吐第一个字的时间：

# Time To First Token

TTFT。

---

## 313. 它很受：

> Prefill 成本

影响。

---

## 314. 开始生成后：

> 每秒输出多少 Token。

可以看：

# Tokens Per Second

---

## 315. 它更受：

> Decode 阶段性能

影响。

---

## 316. 所以一个模型可能：

> TTFT 慢，但 Decode 快。

也可能反过来。

---

# 五十六、为什么长采购文件 TTFT 会变高？

## 317. 输入：

\[
100K
\]

Token。

---

## 318. Prefill 必须：

> 让它们经过几十层 Transformer。

---

## 319. 所以即使最终只回答：

> 200 Token。

前面的阅读成本：

> 仍然巨大。

---

## 320. 这再次说明 RAG 为什么有价值

如果只需：

\[
8K
\]

相关 Token，

可能显著减少：

> Prefill 成本。

---

# 五十七、权重显存只是 LLM 显存的一部分

## 321. 模型运行时可能需要：

1. Weights；
2. Activations；
3. KV Cache；
4. 临时计算 Buffer。

训练时还可能有：

5. Gradients；
6. Optimizer States。

---

## 322. 所以：

\[
\boxed{
GPU Memory
\neq
ModelWeightsOnly
}
\]

---

# 五十八、为什么训练比推理更吃显存？

## 323. 推理：

> 不需要保存 Backprop 所需的大量 Activation。

---

## 324. 训练：

> Forward 后还要 Backward。

---

## 325. 所以需要：

- Activations；
- Gradients；
- Optimizer State。

---

## 326. Adam 类 Optimizer

甚至需要额外：

> Momentum / Variance State。

---

## 327. 因此一个能轻松推理的模型

不代表：

> 可以同样轻松 Full Fine-tune。

---

# 五十九、这就是 LoRA 为什么重要

## 328. Full Fine-tuning：

> 修改大量甚至全部 Weight。

---

## 329. LoRA：

> 冻结原 Weight。

学习一个低秩更新：

\[
\boxed{
\Delta W
=
BA
}
\]

---

## 330. 原矩阵：

\[
W
\]

变成：

\[
W'=W+\Delta W
\]

---

## 331. 如果 Rank：

\[
r\ll D
\]

---

## 332. 新增训练参数：

> 大幅减少。

---

## 333. 为什么 LoRA 经常挂在 Q/K/V/O 或 MLP Matrix？

因为现在我们已经看到：

> Transformer 最主要的 Trainable Parameters 就是这些巨大 Linear Matrix。

---

## 334. 所以 LoRA 并不是神秘插件。

它就是：

> 对这些大矩阵学习一个小型 Low-rank Delta。

---

# 六十、把第 7 阶段的 Residual 思想和 LoRA 再联系一次

## 335. Residual：

\[
ExistingRepresentation
+
Update
\]

---

## 336. LoRA：

\[
ExistingWeight
+
LowRankUpdate
\]

---

## 337. 它们数学上不是同一回事。

但设计哲学非常相似：

\[
\boxed{
PreserveBase
+
LearnDelta
}
\]

---

# 六十一、ProcurementLM 为什么不应该从零训练第一版？

## 338. 现在你已经能从架构层理解原因。

从零训练意味着：

> Embedding 没知识。

---

## 339. Attention：

> Q/K/V 全部没学。

---

## 340. MLP：

> 全部随机。

---

## 341. LM Head：

> 也随机。

---

## 342. 你需要重新让数十亿参数学会：

- 中文；
- 语法；
- 世界知识；
- 推理模式；
- 格式；
- 常识；
- 再到采购专业。

---

## 343. 成本极高。

---

## 344. 如果使用一个已经成熟的基础模型

它已经形成：

\[
\boxed{
GeneralLanguageRepresentation
}
\]

---

## 345. 我们要做的更像：

\[
\boxed{
通用能力
+
采购领域增量
}
\]

---

# 六十二、CPT 在这个架构上做什么？

## 346. Continued Pretraining：

> 仍然使用语言模型目标。

---

## 347. 只是把训练语料：

> 换成大量政府采购领域文本。

---

## 348. Loss 仍然：

\[
NextTokenCrossEntropy
\]

---

## 349. 但 Gradient 会继续改变：

- Embedding；
- Attention；
- MLP；
- Norm；

等 Weight。

---

## 350. 目标是让模型更熟悉：

> 政府采购语言与分布。

---

# 六十三、SFT 又做什么？

## 351. SFT 使用：

> 输入 → 专家输出

样本。

---

## 352. 例如：

> 采购条款 → 风险审查报告。

---

## 353. 它教模型：

> **怎么工作。**

而不是只：

> 熟悉文本分布。

---

## 354. 所以我们的长期框架仍然成立：

\[
\boxed{
CPT
=
DomainLanguageFamiliarity
}
\]

\[
\boxed{
SFT
=
WorkBehavior
}
\]

---

# 六十四、RAG 呢？

## 355. RAG 通常：

> 不修改模型 Weight。

---

## 356. 它在推理前：

> 从外部 Knowledge Base 找证据。

---

## 357. 然后把证据：

> 加到 Prompt。

---

## 358. 所以从 Transformer 视角：

\[
RAG
\]

做的是：

\[
\boxed{
改变Context
}
\]

而：

\[
SFT/CPT
\]

做的是：

\[
\boxed{
改变Weights
}
\]

---

## 359. 第八个核心心智模型

### 心智模型 ⑧：RAG 改“模型现在看什么”，Fine-tuning 改“模型拿什么参数去看”

这句话非常重要。

---

# 六十五、Rules 又在哪里？

## 360. Rule Engine

通常：

> 不属于 Transformer Block。

---

## 361. 它位于：

# Model System

层。

---

## 362. 例如：

```text
采购文件
   ↓
Parser
   ↓
LLM
   ↓
RAG
   ↓
Rule Engine
   ↓
Risk Report
```

真实顺序可以按系统设计变化。

---

## 363. 所以：

\[
\boxed{
LLM
\neq
整个采购AI系统
}
\]

---

# 六十六、Transformer 是 Engine，不是完整产品

## 364. 它负责：

> 通用的语言计算。

---

## 365. 但生产系统还需要：

- 文档解析；
- 法规库；
- 检索；
- 确定性规则；
- 权限；
- 日志；
- 评测；
- 专家复核。

---

## 366. 这连接第一课 Production ML。

---

# 六十七、从一个采购句子完整跑一次

## 367. 输入：

> “供应商注册资本不得低于5000万元。”

---

## 368. 第一步：

# Tokenizer

把字符串转成：

\[
[id_1,id_2,\ldots,id_S]
\]

---

## 369. 第二步：

# Embedding

\[
H_0
=
E[ids]
\]

---

## 370. 第三步：

进入 Block 1。

RMSNorm。

---

## 371. 第四步：

生成：

\[
Q,K,V
\]

---

## 372. 第五步：

Q/K 加 RoPE。

---

## 373. 第六步：

计算：

\[
QK^T/\sqrt d
\]

---

## 374. 第七步：

加入 Causal Mask。

---

## 375. 第八步：

Softmax。

---

## 376. 第九步：

读取 V。

---

## 377. 第十步：

多个 Head 合并。

---

## 378. 第十一步：

Output Projection。

---

## 379. 第十二步：

Residual Add。

---

## 380. 第十三步：

第二个 RMSNorm。

---

## 381. 第十四步：

SwiGLU MLP。

---

## 382. 第十五步：

第二个 Residual Add。

得到：

\[
H_1
\]

---

## 383. 然后重复：

\[
32
\]

层或者模型配置规定的层数。

---

## 384. 最终：

\[
H_L
\]

---

## 385. Final RMSNorm。

---

## 386. LM Head。

---

## 387. 得到：

\[
VocabularyLogits
\]

---

## 388. 从中选择：

> 下一个 Token。

---

## 389. 生成新 Token 后：

> 再把它接回 Context。

---

## 390. 重复：

\[
NextToken
\rightarrow
NextToken
\rightarrow
NextToken
\]

直到：

> EOS 或其它停止条件。

---

# 六十八、这就是一个 ChatGPT 类文本模型最底层的生成循环

## 391. 它不是一次性：

> “想出整段答案”。

---

## 392. 而是：

\[
\boxed{
一步一个Token
}
\]

---

## 393. 例如回答：

> “该条件存在潜在竞争限制风险。”

实际上是不断：

\[
P(Token_{t+1}\mid Context,Token_{\le t})
\]

生成出来。

---

# 六十九、为什么前面的错误会影响后面？

## 394. 因为刚生成的 Token

马上进入：

> 后续 Context。

---

## 395. 如果前面生成了错误表述

后面模型看到的 Context：

> 已经改变。

---

## 396. 于是错误可能：

> 继续传播。

---

## 397. 这叫某种：

# Autoregressive Error Propagation

---

## 398. 所以长回答越长

越需要：

> 稳定任务结构与证据约束。

---

# 七十、为什么 Structured Output 有价值？

## 399. 例如要求模型输出：

```json
{
  "risk": true,
  "risk_type": "...",
  "legal_basis": [],
  "reason": "...",
  "suggestion": "..."
}
```

---

## 400. 这种结构：

> 约束生成空间。



## 401. 同时方便：

- 程序解析；
- Rule Validation；
- 自动评测；
- 专家修改。

---

## 402. 但 JSON 格式正确

不意味着：

> 内容正确。

---

# 七十一、格式正确和事实正确必须分开评测

## 403. 可以有：

\[
FormatAccuracy
\]

---

## 404. 还要有：

\[
RiskAccuracy
\]

---

## 405. 还有：

\[
CitationAccuracy
\]

---

## 406. 还有：

\[
ReasoningQuality
\]

---

## 407. 不要用：

> JSON Parse Success

冒充：

> 专业能力。

---

# 七十二、为什么 LLM 会 Hallucinate？

## 408. 从模型目标看：

它必须：

> 继续生成 Token。

---

## 409. 即使当前 Context：

> 没有足够证据。

---

## 410. 原生 Next Token Objective

没有一个天然按钮说：

> “我不知道，停止回答。”

---

## 411. 除非训练数据、系统策略和解码：

> 教它学会 Abstain。

---

## 412. 所以 Hallucination

不是简单一个 Bug。

它与：

\[
\boxed{
GenerativeObjective
}
\]

本身就有深刻联系。

---

# 七十三、第一课 Stage 11 又回来

## 413. 可靠系统必须教模型：

\[
\boxed{
WhenToAnswer
}
\]

以及：

\[
\boxed{
WhenToAbstain
}
\]

---

## 414. 所以 ProcurementLM 最终不能只有：

> 答案生成。

还需要：

- Evidence；
- Confidence；
- OOD；
- Citation Validation；
- Expert Escalation。

---

# 七十四、参数多等于更聪明吗？

## 415. 不一定。

Parameter Count：

> 提供 Capacity。

---

## 416. 但能力还取决于：

- 数据质量；
- 数据量；
- 架构；
- Training Compute；
- Optimizer；
- Post-training；
- Evaluation。

---

## 417. 所以：

\[
\boxed{
ParameterCount
\neq
IntelligenceScore
}
\]

---

# 七十五、参数少也不一定差

## 418. 一个训练更好的较小模型

在某个采购专项任务上：

> 可能胜过更大的通用模型。

---

## 419. 特别是有：

- 高质量专家数据；
- RAG；
- Rule Engine；
- 专项评测。

---

## 420. 这也是为什么我们的第一版

不应该只追求：

> 最大参数量。

---

# 七十六、模型参数量大概怎么估？

## 421. 一个 Dense Decoder LLM 的主要部分：

\[
Embedding
\]

\[
L\times Attention
\]

\[
L\times MLP
\]

\[
Norm
\]

\[
LMHead
\]

---

## 422. 粗略：

\[
\boxed{
Params
\approx
Embedding
+
L(
AttentionParams
+
MLPParams
)
+
LMHead
}
\]

---

## 423. 如果 Weight Tying：

LM Head 与 Embedding：

> 不重复计算一份。

---

# 七十七、为什么 Layer 数和 Hidden Size 都很重要？

## 424. Hidden Size：

\[
D
\]

变大。

---

## 425. 大矩阵：

\[
D^2
\]

增长。

---

## 426. 所以参数：

> 大致快速增长。

---

## 427. Layer：

\[
L
\]

增加。

参数：

> 大致线性增加。

---

## 428. 因此：

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

都控制 Model Capacity。

---

# 七十八、为什么模型计算量这么大？

## 429. 每个 Token 每层

都要经过：

- QKV Projection；
- Attention；
- Output Projection；
- SwiGLU 大矩阵。

---

## 430. 再乘：

\[
数十层
\]

---

## 431. 再乘：

\[
数十亿/万亿训练Token
\]

---

## 432. 所以预训练需要：

> 巨大 Compute。

---

# 七十九、训练 Token 数和参数数不是一回事

## 433. Parameter Count：

> 模型有多少可学习数字。

---

## 434. Training Tokens：

> 模型看过多少文本单位。

---

## 435. 一个 7B 模型：

> 不是只训练 7B Token。

完全不同。

---

## 436. 模型可以拥有：

\[
7B
\]

参数。

同时训练：

> 数万亿 Token。

---

# 八十、一个参数会只看一个样本吗？

## 437. 不会。

同一参数：

> 在海量不同输入中反复参与计算。

---

## 438. 每个训练 Batch：

> 都可能对它产生 Gradient。

---

## 439. 所以 Parameter：

> 是跨数据共享的。

---

# 八十一、为什么模型能泛化？

## 440. 因为它不只是：

> 把每个句子单独存在数据库里。

---

## 441. 它通过共享 Weight：

> 学习跨样本可复用的表示和规律。

---

## 442. 当然也可能：

> 记忆部分训练内容。

---

## 443. 所以真实模型同时具有：

- Pattern Learning；
- Memorization；
- Generalization；

等行为。

---

# 八十二、Transformer 是不是一个巨大的数据库压缩器？

## 444. 这个类比有一点帮助。

训练：

> 把海量数据规律压进参数。

---

## 445. 但它不只是：

> 压缩数据库。

---

## 446. 因为模型还学习：

> 可组合计算函数。

---

## 447. 所以更准确：

\[
\boxed{
Model
=
LearnedStatisticalComputationSystem
}
\]

而不是：

> Key-Value 数据库。

---

# 八十三、为什么 Prompt 可以改变行为而不改变参数？

## 448. 因为 Prompt 改变：

\[
H_0
\]

---

## 449. 然后每一层 Attention

产生：

> 不同 Routing。

---

## 450. 所以同一套 Weight

在不同 Context 下：

> 执行不同动态计算路径。

---

## 451. 这就是 In-Context Learning 能存在的基础之一。

---

# 八十四、Prompt 不会永久写进 Weight

## 452. 一次普通推理：

> 没有 Backprop。

---

## 453. 所以模型 Parameter：

> 不因为你发一个 Prompt 就更新。

---

## 454. Prompt 只改变：

> 当前 Forward Pass 的 Activation / KV Cache。

---

## 455. 这非常重要：

\[
\boxed{
ContextMemory
\neq
WeightUpdate
}
\]

---

# 八十五、RAG 证据也是临时 Context

## 456. 今天检索到某法规：

> 放进 Prompt。

---

## 457. 模型可以使用它。

---

## 458. 下一次没放：

> 它并没有因此自动永久记住。

---

## 459. 除非：

> 另外做训练或其它持久化系统。

---

# 八十六、模型的“短期工作记忆”在哪里？

## 460. 可以粗略认为：

当前 Context 对应的：

- Hidden States；
- KV Cache；

承担大量短期上下文状态。

---

## 461. 而 Parameter：

> 是长期训练后固化的 Weight。

---

## 462. 可以形成一个很有用的区别：

\[
\boxed{
Weights
=
LongTermLearnedParameters
}
\]

\[
\boxed{
Context/KV
=
TemporaryWorkingState
}
\]

---

# 八十七、但不要把它完全等同人类记忆

这是：

> 工程类比。

模型内部没有证据说明：

> 它以人类心理记忆方式工作。

---

# 八十八、一个现代 Decoder LLM 的完整伪代码

## 463. 现在我们终于可以写：

```python
ids = tokenizer(text)

x = token_embedding(ids)

for block in blocks:
    x = block(x)

x = final_norm(x)

logits = lm_head(x)
```

---

## 464. Block 内部：

```python
def block(x):
    h = rmsnorm_1(x)
    a = attention(h)
    x = x + a

    h = rmsnorm_2(x)
    m = swiglu_mlp(h)
    x = x + m

    return x
```

---

## 465. Attention 内部：

```python
q = x @ Wq
k = x @ Wk
v = x @ Wv

q, k = rope(q, k)

scores = q @ k.T / sqrt(head_dim)
scores += causal_mask

weights = softmax(scores)

context = weights @ v

out = context @ Wo
```

---

## 466. SwiGLU：

```python
gate = silu(x @ W_gate)
up   = x @ W_up

hidden = gate * up

out = hidden @ W_down
```

---

## 467. 到这里

一个现代 LLM 的主 Forward Path：

> 已经没有黑箱了。

---

# 八十九、当然真实代码还会有更多细节

## 468. 例如：

- Batch；
- Head reshape；
- GQA；
- Cache；
- FlashAttention；
- Tensor Parallel；
- Mixed Precision；
- Fused Kernels；
- Quantization。

---

## 469. 但这些主要是：

> 在核心数学结构之上做工程实现与扩展。

---

# 九十、第九个核心心智模型

### 心智模型 ⑨：看任何新 LLM 架构，先寻找“哪部分是核心 Transformer，哪部分只是实现或架构变体”

核心问题始终是：

\[
Embedding?
\]

\[
Norm?
\]

\[
Attention?
\]

\[
Position?
\]

\[
MLP?
\]

\[
Residual?
\]

\[
OutputHead?
\]

---

# 九十一、以后打开一个模型 config 应该怎么看？

## 470. 假设看到：

```text
vocab_size
hidden_size
intermediate_size
num_hidden_layers
num_attention_heads
num_key_value_heads
max_position_embeddings
rope_theta
```

你已经应该知道：

> 每一个字段大概控制什么。

---

## 471. `vocab_size`

决定：

\[
V
\]

---

## 472. `hidden_size`

决定：

\[
D
\]

---

## 473. `intermediate_size`

通常与：

\[
D_{ff}
\]

有关。

---

## 474. `num_hidden_layers`

就是：

\[
L
\]

---

## 475. `num_attention_heads`

Query Head：

\[
H_Q
\]

---

## 476. `num_key_value_heads`

决定：

> MHA / GQA / MQA 结构。

---

## 477. `rope_theta`

与：

> RoPE 频率基础尺度有关。

---

## 478. `max_position_embeddings`

与：

> 位置/上下文配置有关。

但不应直接等同：

> 可靠 Context 长度。

---

# 九十二、看到模型名“7B”现在应该想到什么？

## 479. 大约表示：

> 数十亿级 Parameter。

---

## 480. 你应该继续问：

> Hidden Size 多大？

---

## 481. Layer 数多少？

---

## 482. MHA 还是 GQA？

---

## 483. Intermediate Size 多大？

---

## 484. Vocabulary 多大？

---

## 485. Context 多长？

---

## 486. 训练了多少 Token？

---

## 487. 训练数据是什么？

---

## 488. Post-training 做了什么？

---

## 489. 因为：

\[
\boxed{
7B
只是一个粗粒度参数量标签
}
\]

---

# 九十三、为什么同样 7B 能力差很多？

## 490. 因为 Parameter 数相同

不代表：

> Weight 学得一样。

---

## 491. 数据：

> 不一样。

---

## 492. Architecture：

> 不一样。

---

## 493. Training Recipe：

> 不一样。

---

## 494. Context：

> 不一样。

---

## 495. Post-training：

> 不一样。

---

## 496. 所以：

> 参数量只是 Capacity 指标之一。

---

# 九十四、ProcurementLM 选底座以后应该先看什么？

## 497. 不只是 Benchmark 总榜。

---

## 498. 还要检查：

- 中文能力；
- 长文档；
- Structured Output；
- RAG compatibility；
- Context；
- GPU cost；
- License；
- Fine-tuning ecosystem。

---

## 499. 然后才进入：

> 自己的采购 Gold Set。

---

# 九十五、基础模型为什么必须用自己的 Gold Set 选？

## 500. 通用 Benchmark：

> 不知道你的业务错误成本。

---

## 501. Procurement Gold Set：

> 才能测资格、评分、技术参数、法规依据等真实任务。

---

## 502. 所以第一课和第二课最终汇合：

\[
\boxed{
Architecture
必须服从Evaluation
}
\]

---

# 九十六、Transformer 强大并不意味着不需要数据治理

## 503. 模型会学习：

> 数据中的规律。

---

## 504. 数据有错误：

> 模型可以学习错误。

---

## 505. 数据有偏差：

> Representation 可以携带偏差。

---

## 506. 数据有泄漏：

> Test 可以虚高。

---

## 507. 所以底层架构再漂亮：

\[
\boxed{
GarbageIn
\rightarrow
GarbageLearned
}
\]

---

# 九十七、模型会自动理解法规效力层级吗？

## 508. 不能默认。

---

## 509. 它可能学到：

> 某些统计模式。

---

## 510. 但政府采购法律判断还需要：

- 法律效力层级；
- 生效时间；
- 地域；
- 条款上下文；
- 监管口径。

---

## 511. 所以这些信息最好：

> 显式进入 RAG Metadata、Rule 或训练数据结构。

---

# 九十八、Transformer 不等于法律专家

## 512. 它是：

\[
\boxed{
非常强大的可学习语言计算架构
}
\]

---

## 513. 专业性来自：

- 基础训练；
- 领域数据；
- 专家 SFT；
- RAG；
- Rules；
- Evaluation；
- Human Review。

---

# 九十九、第二课真正想让你建立的认知

## 514. 以后有人说：

> “我们用一个 32B 模型做政府采购。”

你不应该只问：

> “32B 厉不厉害？”

---

## 515. 你应该能追问：

> Tokenizer 怎么样？

---

## 516. Vocabulary 多大？

---

## 517. Hidden Size？

---

## 518. Layers？

---

## 519. Attention Heads？

---

## 520. KV Heads？

---

## 521. RoPE 怎么配置？

---

## 522. Context 怎么训练？

---

## 523. MLP 是什么结构？

---

## 524. CPT 做过吗？

---

## 525. SFT 数据是什么？

---

## 526. Gold Set 怎么切？

---

## 527. 法规知识怎么更新？

---

## 528. 生产错误怎么反馈？

---

# 一百、现在再看“训练一个模型”这句话

## 529. 第一课时它可能像一句口号。

现在你应该看到完整系统：

\[
RawData
\]

↓

\[
Tokenizer
\]

↓

\[
Batches
\]

↓

\[
Embedding
\]

↓

\[
Blocks
\]

↓

\[
Logits
\]

↓

\[
Loss
\]

↓

\[
Backward
\]

↓

\[
Optimizer
\]

↓

\[
UpdatedWeights
\]

↓

\[
Evaluation
\]

↓

\[
Deployment
\]

---

# 一百零一、整个第二课压缩成一条主线

## 530. Stage 1

\[
\boxed{
Neuron
}
\]

模型从：

> 加权组合开始。

---

## 531. Stage 2

\[
\boxed{
Activation
}
\]

加入：

> 非线性。

---

## 532. Stage 3

\[
\boxed{
RepresentationLearning
}
\]

模型学：

> 中间表示。

---

## 533. Stage 4

\[
\boxed{
Forward
}
\]

数据怎样走过网络。

---

## 534. Stage 5

\[
\boxed{
Backward
}
\]

错误责任怎样传回参数。

---

## 535. Stage 6

\[
\boxed{
Optimizer
}
\]

参数怎样真正更新。

---

## 536. Stage 7

\[
\boxed{
Initialization
+
Norm
+
Residual
}
\]

为什么深网络能稳定训练。

---

## 537. Stage 8

\[
\boxed{
Embedding
}
\]

离散 Token 怎样变成连续向量。

---

## 538. Stage 9

\[
\boxed{
Tokenizer
}
\]

原始文字怎样变成 Token。

---

## 539. Stage 10

\[
\boxed{
Position
+
RoPE
}
\]

Token 怎样知道顺序。

---

## 540. Stage 11

\[
\boxed{
SelfAttention
}
\]

Token 怎样彼此通信。

---

## 541. Stage 12

\[
\boxed{
TransformerAssembly
}
\]

所有组件怎样形成完整 LLM。

---

# 一百零二、第二课的五条总公式

## 542. 神经元：

\[
\boxed{
z=W^Tx+b
}
\]

---

## 543. 参数更新：

\[
\boxed{
\theta_{t+1}
=
\theta_t-\eta\nabla_\theta L
}
\]

---

## 544. Attention：

\[
\boxed{
Attention(Q,K,V)
=
Softmax
\left(
\frac{QK^T}{\sqrt{d_k}}+M
\right)V
}
\]

---

## 545. Transformer Block：

\[
\boxed{
U_l
=
H_l+
Attention(Norm(H_l))
}
\]

\[
\boxed{
H_{l+1}
=
U_l+
MLP(Norm(U_l))
}
\]

---

## 546. Language Modeling：

\[
\boxed{
P(x_1,\ldots,x_T)
=
\prod_t
P(x_t\mid x_{<t})
}
\]

---

# 一百零三、如果只记一个现代 LLM 总公式

没有一个单独封闭公式能准确包含所有组件。

但可以写成：

\[
\boxed{
Text
\xrightarrow{Tokenizer}
IDs
\xrightarrow{Embedding}
H_0
\xrightarrow{Transformer^L}
H_L
\xrightarrow{Norm}
H_f
\xrightarrow{LMHead}
Logits
\xrightarrow{Decode}
NextToken
}
\]

这就是第二课最终图。

---

# 一百零四、第二课十大专家心智模型

| 心智模型 | 核心认知 |
|---|---|
| **① 神经网络本质是可学习的参数化函数** | 学习就是用 Loss 和 Gradient 塑造参数 |
| **② Representation 比手工 Feature 更核心** | 深层模型逐层学习有用表示 |
| **③ 深度网络首先是信号传播系统** | Initialization、Norm、Residual 保证可训练 |
| **④ Tokenizer 定义模型看到语言的离散积木** | Token 数直接影响 Context 与 Compute |
| **⑤ Embedding 把离散符号送进连续可微空间** | Token ID 是地址，向量才参与计算 |
| **⑥ RoPE 把位置变成 Attention Geometry** | 内容关系和相对位置在 Q/K 匹配中结合 |
| **⑦ Attention 是动态信息路由** | Q/K 找信息，V 携带信息 |
| **⑧ MLP 是每个 Token 内部的大型非线性计算器** | Attention 通信，MLP 计算 |
| **⑨ Residual Stream 是贯穿模型的表示主干** | 每层不断写入更新而不是重建全部状态 |
| **⑩ LLM 最终仍是条件 Next-token Predictor** | 强能力从大规模训练中涌现，但不天然保证真实与合规 |

---

# 一百零五、一个非常重要的最终认知

## 547. 大模型内部没有一个小人

在读：

> “供应商注册资本不得低于5000万元”。

---

## 548. 也没有一个显式 IF 程序：

```text
IF 出现注册资本:
    判断违法
```

---

## 549. 真正发生的是：

\[
TokenIDs
\]

↓

\[
Vectors
\]

↓

\[
MatrixMultiplication
\]

↓

\[
AttentionRouting
\]

↓

\[
NonlinearTransformation
\]

↓

\[
LayerAfterLayer
\]

↓

\[
VocabularyLogits
\]

---

## 550. 而所有这些数值行为

是被：

\[
\boxed{
Data
+
Loss
+
GradientDescent
}
\]

塑造出来的。

---

# 一百零六、但这不意味着“它什么都没理解”

## 551. “理解”这个词要谨慎。

如果从功能角度：

模型可以形成：

> 非常复杂的内部表示。

---

## 552. 它可以利用：

- 语义；
- 关系；
- 上下文；
- 结构；
- 模式；

完成复杂任务。

---

## 553. 但不能因为输出流畅

就直接等同：

> 人类式理解。

---

## 554. 在工程上更有价值的问题是：

\[
\boxed{
它在哪些任务、分布、条件下可靠？
}
\]

这又回到了第一课的：

# Generalization

---

# 一百零七、采购领域最危险的误解

## 555. “模型架构很先进，所以输出一定专业。”

错误。

---

## 556. Transformer 只是：

> 强大的学习机器。

---

## 557. 它学成什么：

首先取决于：

\[
\boxed{
TrainingSignal
}
\]

---

## 558. 所以我们的 ProcurementLM 仍必须建立：

- 专家标注；
- Gold Set；
- Hard Negative；
- 法规 RAG；
- Citation Validation；
- Rule Engine；
- Human Review。

---

# 一百零八、为什么现在你能理解 RAG + SFT 的分工？

## 559. RAG 把法规：

> 放进当前 Token Context。

---

## 560. Attention：

> 在这些证据 Token 之间路由信息。

---

## 561. SFT 则改变：

> Attention/MLP 等 Weight。

---

## 562. 让模型更会：

> 使用这些证据完成专业任务。

---

## 563. 所以：

\[
\boxed{
RAG
=
GiveEvidence
}
\]

\[
\boxed{
SFT
=
TeachBehavior
}
\]

---

# 一百零九、为什么 Rules 仍然不能消失？

## 564. 因为一些业务条件：

> 可以确定性验证。

例如：

- 日期范围；
- 金额格式；
- 必填字段；
- 明确禁止条件；
- 文档完整性。

---

## 565. 让概率型生成模型

承担所有确定性判断：

> 没必要。

---

## 566. 更成熟：

\[
\boxed{
LLM
+
RAG
+
Rules
+
Experts
}
\]

---

# 一百一十、到这里你已经具备读开源模型架构图的基础

## 567. 以后看到：

```text
Embedding
32 × DecoderLayer
RMSNorm
LMHead
```

应该已经不陌生。

---

## 568. DecoderLayer 里面：

```text
SelfAttention
MLP
InputLayerNorm
PostAttentionLayerNorm
```

也应该能拆。

---

## 569. Attention 内：

```text
q_proj
k_proj
v_proj
o_proj
rotary_emb
```

你知道：

> 每一个是什么。

---

## 570. MLP 内：

```text
gate_proj
up_proj
down_proj
act_fn
```

你也知道：

> 这是 SwiGLU 类结构。

---

# 一百一十一、以后看到 LoRA Target Modules

例如：

```text
q_proj
k_proj
v_proj
o_proj
gate_proj
up_proj
down_proj
```

你现在也应该知道：

> 它到底在改模型什么地方。

---

## 571. `q_proj`

改变：

> Query Space。

---

## 572. `k_proj`

改变：

> Key Space。

---

## 573. `v_proj`

改变：

> 被传输的 Value Representation。

---

## 574. `o_proj`

改变：

> 多 Head 信息怎样融合回 Residual Stream。

---

## 575. `gate_proj/up_proj/down_proj`

改变：

> MLP Feature Transformation。

---

# 一百一十二、这就是为什么第二课必须先学完再进入实操

如果一开始直接给：

```python
target_modules=[
    "q_proj",
    "v_proj"
]
```

你只能：

> 背配置。

---

现在再看：

> 你知道它真正改变了哪一个数学矩阵。

这就是理论基础的价值。

---

# 一百一十三、第二课毕业思维实验

有人告诉你：

> “我买了 8 张高端 GPU，下载了一个 14B 模型，我准备微调 100 万份政府采购文件。”

你现在应该立即产生这些问题：

## 576. 输入是怎样 Tokenize 的？

---

## 577. 一份采购文件平均多少 Token？

---

## 578. Context Length 能否覆盖？

---

## 579. 是继续预训练还是 SFT？

---

## 580. 如果 SFT，Target Output 是什么？

---

## 581. Loss 计算在哪些 Token？

---

## 582. 训练哪些 Parameter？

---

## 583. Full Fine-tune 还是 LoRA？

---

## 584. LoRA 挂在哪些 Projection？

---

## 585. 为什么选这些 Matrix？

---

## 586. 训练数据有没有 Leakage？

---

## 587. Gold Set 怎么切？

---

## 588. 法规知识为什么不直接用 RAG？

---

## 589. 专业行为为什么需要 SFT？

---

## 590. 训练后怎么判断模型是真的学到机制，而不是学“5000万元→风险”这种 Shortcut？

---

# 一百一十四、如果你会问这些问题

你已经不再是在：

> “使用一个 AI 工具”。

而是在开始：

\[
\boxed{
理解并设计一个机器学习系统
}
\]

这正是第二课的目标。

---

# 一百一十五、第二课最终掌握标准

第二课毕业后，你应该能够从第一性原理解释：

> 一个神经元为什么是 \(W^Tx+b\)。

> 为什么没有 Activation，深层线性层会坍缩成一个线性变换。

> Backprop 为什么是 Credit Assignment。

> Optimizer 和 Gradient 为什么不是同一个东西。

> Xavier / He Initialization 为什么与方差传播有关。

> RMSNorm 为什么稳定 Hidden State Scale。

> Residual 为什么提供 Identity / Gradient Highway。

> Token ID 为什么只是 Index。

> Embedding 为什么是可训练矩阵查表。

> Tokenizer 为什么影响 Context、成本和模型输入世界。

> BPE / WordPiece / SentencePiece / Byte-Level 的核心差别。

> 为什么文字顺序必须进入 Position Mechanism。

> RoPE 为什么通过旋转 Q/K 表达相对位置。

> Q/K/V 为什么代表三个不同计算角色。

> 为什么 Attention 要除以 \(\sqrt{d_k}\)。

> 为什么 Softmax Weight 是 Routing Weight 而不是事实概率。

> Multi-Head 为什么可以在不同子空间建立不同关系。

> GQA 为什么主要优化 KV Cache。

> FlashAttention 为什么改的是计算方法，不是 Attention 数学目标。

> Attention 为什么主要负责跨 Token 通信。

> MLP 为什么主要负责 Position-wise 非线性计算。

> SwiGLU 的 Gate / Up / Down 三个 Projection 在做什么。

> 一个 Transformer Block 为什么是 `Norm → Attention → Residual → Norm → MLP → Residual`。

> 为什么几十层 Block 的 Shape 可以一直保持 \((B,S,D)\)。

> 什么是 Residual Stream。

> Final Norm 为什么存在。

> LM Head 怎样把 \(D\) 维 Hidden State 映射到 \(V\) 个 Vocabulary Logits。

> Next-token Cross Entropy 到底优化什么。

> Causal LM 为什么可以在训练时并行，却在生成时逐 Token Decode。

> Prefill 与 Decode 有什么区别。

> KV Cache 为什么会占大量推理显存。

> Weight Tying 是什么。

> Temperature / Top-k / Top-p 改变的是模型参数还是 Sampling Policy。

> CPT、SFT、RAG 分别改变的是模型的什么部分。

> 为什么 LoRA 本质上是在大 Linear Weight 上学习低秩增量。

如果你能够不靠死记定义，把这些东西从机制上串起来：

\[
\boxed{
第二课正式毕业
}
\]

---

# 第二课最终一句话

如果第一课解决的是：

\[
\boxed{
机器学习到底在学什么？
}
\]

那么第二课最终解决的是：

\[
\boxed{
大语言模型到底是怎样用大量可训练矩阵、
非线性、Attention、Residual和Gradient，
把一串离散文字逐层变成上下文化表示，
再变成下一个Token的概率分布？
}
\]

答案就是我们现在建立起来的完整链条：

\[
\boxed{
Text
\rightarrow
Tokens
\rightarrow
Embeddings
\rightarrow
TransformerBlocks
\rightarrow
ContextualRepresentations
\rightarrow
Logits
\rightarrow
NextToken
}
\]

而模型之所以能不断变强，是因为在训练阶段，这条链条之后还有：

\[
\boxed{
Loss
\rightarrow
Backward
\rightarrow
Optimizer
\rightarrow
UpdatedParameters
}
\]

于是两条链最终闭环：

\[
\boxed{
Forward
\rightarrow
Loss
\rightarrow
Backward
\rightarrow
Update
\rightarrow
BetterForward
}
\]

**到这里，第二课 12 个阶段完整闭环。**

下一课开始，我们就可以不再把 Token、Embedding、Attention、Transformer 当作黑箱术语，而是在这个基础上进入真正的 **LLM 训练、模型选择、GPU 环境与 ProcurementLM 实操体系**。




---
