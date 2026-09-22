# 第二课 · 第 9 阶段：Tokenizer 与 Subword
## “供应商注册资本不得低于5000万元”，模型究竟凭什么决定切成哪些 Token？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Token ≠ Word ≠ Concept。Tokenizer 切出来的是模型计算单位，不是天然语言学词或完整知识概念。**
2. **Subword Tokenization 在词表大小与序列长度之间做折中，使模型能处理未登录词和组合词。**
3. **Tokenizer 是模型协议的一部分；训练、推理和微调必须使用与模型匹配的 Tokenizer。**
4. **Tokenization 直接影响 Context 占用、训练成本、数字/法规文号切分和领域术语效率。**
5. **随意更换或扩展 Tokenizer 可能导致 Embedding/LM Head 尺寸和已学参数失配，需要专门训练与兼容性验证。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Token` | Token：模型实际处理的离散文本单元 |
| `Tokenizer` | 分词器：文本与 Token ID 之间的编码/解码组件 |
| `Embedding` | 嵌入：把离散 Token 映射到连续高维向量 |
| `Tokenization` | Token 化：把文本转换成 Token 序列 |
| `Attention` | 注意力：根据内容相关性动态聚合信息 |
| `Normalization` | 规范化：稳定中间激活与训练过程 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Self-Attention` | 自注意力：同一序列内部各位置计算相关性并聚合 |
| `Gradient` | 梯度：损失对参数变化方向和敏感度的局部信息 |
| `Latency` | 延迟：单个请求从进入到完成的时间 |
| `Memory` | 任务记忆：保存跨步骤需要复用的结构化信息 |
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |

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

第 8 阶段，我们已经建立：

\[
\boxed{
TokenID
\rightarrow
EmbeddingVector
}
\]

但是我们故意跳过了一个问题：

> **Token ID 从哪里来？**

真正输入明明是字符串：

> “供应商注册资本不得低于5000万元。”

模型却最终拿到：

\[
[28731,1152,9034,\ldots]
\]

中间一定发生了某种转换。

这就是今天的主角：

\[
\boxed{
Tokenizer
}
\]

完整链条：

\[
\boxed{
RawText
\rightarrow
Normalization
\rightarrow
Segmentation
\rightarrow
Tokens
\rightarrow
TokenIDs
}
\]

今天最重要的不是记住几个 Tokenizer 名字，而是理解：

\[
\boxed{
Tokenizer
实际上定义了LLM看到语言时的“最小积木”
}
\]

---

## 1. 先明确：Token 不等于“单词”

这是第一个必须拆掉的误区。

很多人第一次听 Token，会理解为：

> 一个 Token = 一个词。

不对。

一个 Token 可能是：

- 一个汉字；
- 一个词；
- 一个词的一部分；
- 数字的一部分；
- 标点；
- 空格；
- 几个字节；
- 一段常见字符串。

所以：

\[
\boxed{
Token
\neq
Word
}
\]

---

## 2. Tokenizer 到底做什么？

给定：

\[
Text
\]

Tokenizer 定义一个映射：

\[
\boxed{
T(Text)
=
[t_1,t_2,\ldots,t_n]
}
\]

然后 Vocabulary 再将 Token 映射为：

\[
[id_1,id_2,\ldots,id_n]
\]

---

## 3. 一个简单例子

输入：

> 供应商必须在本市注册

Tokenizer A 可能产生：

```text
供应商
必须
在
本市
注册
```

Tokenizer B 可能产生：

```text
供应
商
必须
在
本
市
注册
```

Tokenizer C 甚至可能产生：

```text
供
应
商
必
须
在
本
市
注
册
```

三个都合法。

---

## 4. 模型看到的其实不是原始文本

模型真正收到的是：

\[
TokenIDs
\]

例如：

\[
[217,8912,71,355,\ldots]
\]

所以：

\[
\boxed{
模型的语言世界首先经过Tokenizer过滤
}
\]

这句话非常重要。

---

## 5. 第一个核心心智模型

### 心智模型 ①：Tokenizer 是模型与原始语言之间的“接口协议”

人看到：

> “中小企业声明函”

模型可能看到：

```text
中小企业
声明
函
```

也可能：

```text
中
小
企业
声明
函
```

所以模型的基本输入世界：

> 不是字符世界，也不是人类词典世界。

而是：

\[
\boxed{
Tokenizer定义的Token世界
}
\]

---

# 一、为什么不直接 Character-Level？

## 6. 最简单思路：一个字符一个 Token

中文：

> 供应商

可以直接：

```text
供
应
商
```

这叫：

# Character-Level Tokenization

---

## 7. 它有什么优点？

字符集合相对有限。

中文常用字符虽然不少，但远小于：

> 所有可能词语。

因此：

> Vocabulary 可以相对可控。

---

## 8. 还几乎不会出现未知词问题

例如新词：

> “政采贷”

即使 Vocabulary 没有整个词，

仍然可以：

```text
政
采
贷
```

所以模型至少：

> 能表示它。

---

## 9. 那为什么不全部按字符？

最大问题：

\[
\boxed{
SequenceLength
}
\]

会变长。

---

## 10. 假设一句话

> “政府采购框架协议采购方式管理暂行办法”

按词或常见片段：

```text
政府采购
框架协议
采购方式
管理
暂行办法
```

可能只有：

\[
5
\]

个 Token。

---

## 11. 如果按汉字

可能变成：

```text
政 府 采 购 框 架 协 议 采 购 方 式 管 理 暂 行 办 法
```

大约：

\[
18
\]

个 Token。

序列明显更长。

---

## 12. 为什么 Sequence Length 很重要？

标准 Self-Attention 的核心矩阵：

\[
QK^T
\]

如果序列长度：

\[
S
\]

Attention Score Matrix 大约是：

\[
S\times S
\]

---

## 13. 所以基础 Attention 计算量大致有

\[
\boxed{
O(S^2)
}
\]

这一项。

如果：

\[
S
\]

翻倍，

这部分计算：

> 可能接近 4 倍。

---

## 14. 这意味着 Tokenizer 会影响 GPU 成本

同一份政府采购文件：

Tokenizer A：

\[
3000\ Tokens
\]

Tokenizer B：

\[
6000\ Tokens
\]

即使模型完全一样：

> 推理成本也可能明显不同。

---

## 15. 第二个核心心智模型

### 心智模型 ②：Tokenizer 不只是语言问题，它也是计算成本问题

\[
\boxed{
Tokenization
\rightarrow
SequenceLength
\rightarrow
Compute
+
Memory
+
Latency
}
\]

所以 Tokenizer 是：

> 模型架构与系统工程的一部分。

---

# 二、那为什么不一个 Word 一个 Token？

## 16. 另一个极端

把：

> “供应商”

作为一个 Token。

> “注册资本”

一个 Token。

> “框架协议”

一个 Token。

这叫：

# Word-Level

---

## 17. 看起来很自然

因为人类也经常：

> 按词理解语言。

而且序列：

> 比字符级短。

---

## 18. 但 Word-Level 遇到一个巨大问题

语言中的可能词：

> 几乎无限。

例如：

```text
采购
采购人
采购项目
采购需求
采购文件
采购代理机构
采购实施计划
```

每一个都放进 Vocabulary：

> 很快膨胀。

---

## 19. 还有新词

训练 Vocabulary 时没见过：

> “智能政采云审查引擎”

怎么办？

---

## 20. 传统系统会出现

# OOV

Out Of Vocabulary。

即：

> 词表外词。

---

## 21. 一种旧方案是 `[UNK]`

例如：

```text
智能政采云审查引擎
→
[UNK]
```

问题很明显。

大量不同未知词：

> 全部变成一个 Token。

信息损失极大。

---

## 22. 所以我们陷入两难

Character：

> Vocabulary 小，但 Sequence 长。

Word：

> Sequence 短，但 Vocabulary 巨大，而且 OOV 严重。

于是：

\[
\boxed{
Subword
}
\]

出现了。

---

# 三、Subword 的核心思想

## 23. Subword 是什么？

不要强迫：

> 一个 Token 一定是完整词。

也不要强迫：

> 一个 Token 一定只是一个字符。

而是在中间找平衡。

---

## 24. 例如

“中小企业声明函”可能：

```text
中小企业
声明
函
```

这里：

> “中小企业”

是常见片段。

> “声明”

也是常见片段。

---

## 25. 一个罕见词

假设：

> 超智慧政采审查器

词表里没有整个词。

仍可拆成：

```text
超
智慧
政采
审查
器
```

所以：

> 不必 `[UNK]`。

---

## 26. Subword 的核心原则

\[
\boxed{
常见字符串
\rightarrow
较大Token
}
\]

\[
\boxed{
罕见字符串
\rightarrow
拆成较小Token
}
\]

---

## 27. 这是一种压缩式思想

频繁出现：

> “政府采购”

可以值得一个 Token。

很少出现：

> “超量子采购银河审核系统”

没必要为整个字符串浪费 Vocabulary Entry。

---

## 28. 第三个核心心智模型

### 心智模型 ③：Subword 是“词表大小”和“序列长度”之间的压缩折中

可以写成：

\[
\boxed{
VocabularySize
\leftrightarrow
SequenceLength
}
\]

Tokenizer 设计就是在决定：

> 哪些字符串值得成为一块“大积木”。

---

# 四、Vocabulary 到底是什么？

## 29. Vocabulary 就是一张 Token 表

例如：

```text
ID 0    <pad>
ID 1    <bos>
ID 2    <eos>
ID 3    供应
ID 4    商
ID 5    供应商
ID 6    采购
ID 7    政府采购
...
```

---

## 30. Vocabulary Size

如果：

\[
V=100000
\]

说明：

> 一共有 10 万个可用 Token ID。

---

## 31. 它和第 8 阶段 Embedding 直接相连

Embedding Matrix：

\[
E\in\mathbb R^{V\times d}
\]

所以：

\[
V\uparrow
\]

Embedding 参数：

\[
Vd
\]

也随之增加。

---

## 32. Vocabulary 是谁设计的？

早期可以：

> 人工定义。

现代大模型通常：

> 用算法从大规模训练语料里学习 Vocabulary。

这就是：

# Tokenizer Training

---

# 五、Tokenizer 训练和 LLM 训练不是一回事

## 33. 一个非常重要的区别

Tokenizer 的“训练”通常是：

> 根据语料统计，构造 Vocabulary 和切分规则。

LLM 训练：

> 通过 Gradient Descent 学 Weight。

---

## 34. Tokenizer 通常不是每个 Gradient Step 都改变

模型训练过程中：

Vocabulary 通常：

> 已经固定。

Token ID 体系也：

> 固定。

---

## 35. 为什么必须固定？

假设今天：

\[
ID=583
\]

代表：

> “供应商”

明天突然代表：

> “合同”

Embedding Matrix 第 583 行：

> 就全部乱套了。

所以模型与 Tokenizer 必须保持一致。

---

## 36. 这非常像数据库 Schema

Tokenizer 定义：

\[
Token\leftrightarrow ID
\]

Embedding 定义：

\[
ID\leftrightarrow Vector
\]

两者必须：

\[
\boxed{
严格对齐
}
\]

---

## 37. 第四个核心心智模型

### 心智模型 ④：Tokenizer 与模型 Weight 是绑定资产，不能随便替换

不是说：

> 模型中文不好，我随便换一个中文 Tokenizer。

这样 Token ID：

> 完全变了。

模型原来的 Embedding：

> 基本失效。

---

# 六、从最经典的 BPE 开始

## 38. BPE 全称

# Byte Pair Encoding

最初是一种：

> 数据压缩算法。

后来被引入 Subword Tokenization。

---

## 39. 核心思想非常简单

从：

> 很小的基本单位

开始。

然后反复寻找：

> 最常一起出现的相邻 pair。

把它们合并。

---

## 40. 一个玩具例子

语料中经常出现：

```text
采 购
采 购
采 购
采 购
采 用
```

最频繁 pair 可能是：

```text
采 + 购
```

---

## 41. 第一次 merge

创建新 Token：

```text
采购
```

以后：

```text
采 购
```

可以变成：

```text
采购
```

---

## 42. 然后继续统计

可能发现：

```text
政府 + 采购
```

非常频繁。

于是再创建：

```text
政府采购
```

---

## 43. 又发现

```text
框架 + 协议
```

很频繁。

于是：

```text
框架协议
```

成为 Token。

---

## 44. BPE 的训练过程因此可以理解成

\[
\boxed{
SmallUnits
\rightarrow
FrequentPairs
\rightarrow
Merge
\rightarrow
LargerUnits
}
\]

不断重复。

---

## 45. Vocabulary Size 怎么控制？

每 Merge 一次：

> 新增一个 Token。

所以如果目标 Vocabulary Size：

\[
V
\]

达到指定规模后：

> 停止 Merge。

---

# 七、手算一个小 BPE

## 46. 假设语料

为了理解算法，我们用英文式符号：

```text
AB
AB
AB
AC
```

初始 Token：

```text
A B
A B
A B
A C
```

---

## 47. 统计相邻 Pair

\[
(A,B)
\]

出现：

\[
3
\]

次。

\[
(A,C)
\]

出现：

\[
1
\]

次。

---

## 48. 所以先 merge

\[
A+B\rightarrow AB
\]

语料变成：

```text
AB
AB
AB
A C
```

Vocabulary 新增：

\[
AB
\]

---

## 49. 这就是最基本的 BPE

它没有人工理解：

> “AB 是一个词。”

只是发现：

\[
\boxed{
AB频繁共同出现
}
\]

所以把它作为更大的单位更划算。

---

## 50. 这和信息压缩有什么关系？

如果：

\[
A,B
\]

经常一起出现，

每次都写两个 Symbol：

> 浪费。

合成一个 Symbol：

> 可以缩短表示。

Tokenizer 本质上也在做：

\[
\boxed{
CorpusCompression
}
\]

的一种近似。

---

# 八、BPE 的重要特征

## 51. 高频片段容易成为单独 Token

例如政府采购语料很多时：

> “采购人”

> “供应商”

> “采购文件”

有可能被学成较完整 Token。

---

## 52. 低频长词会拆分

例如非常罕见：

> “超级智能电子化履约辅助平台”

可能被拆成：

```text
超级
智能
电子
化
履约
辅助
平台
```

甚至更细。

---

## 53. 这正是我们想要的平衡

常见内容：

> 更高效。

罕见内容：

> 仍然可表达。

---

# 九、经典 BPE 和 Byte-Level BPE 不是完全一回事

## 54. 名字里有 Byte，容易造成混淆

原始 Byte Pair Encoding：

> 是压缩算法名称。

NLP 里的 BPE：

> 可以从字符等符号开始做 merge。

---

## 55. 现代 GPT 风格经常使用

# Byte-Level BPE

这时基础单位进一步变成：

\[
Byte
\]

---

# 十、为什么从 Byte 开始？

## 56. 计算机里的文本最终都是编码后的字节

例如 UTF-8。

一个汉字通常：

> 会编码为多个 Byte。

---

## 57. Byte 的取值只有

\[
256
\]

种：

\[
0\sim255
\]

所以：

> 任何文件里的字节都可以表示。

---

## 58. 这带来一个巨大优势

\[
\boxed{
几乎不存在真正无法表示的字符
}
\]

因为任何 Unicode 字符最终：

> 都可以分解到 Byte。

---

## 59. 也就是说 Byte-Level 提供极强 Coverage

罕见汉字：

> 能表示。

Emoji：

> 能表示。

奇怪符号：

> 能表示。

代码字符：

> 能表示。

---

## 60. 如果整个字符串很常见

BPE Merge 又可以：

> 把这些 Byte/字符组合成较大的 Token。

所以：

\[
\boxed{
ByteCoverage
+
SubwordCompression
}
\]

两边兼得。

---

## 61. 第五个核心心智模型

### 心智模型 ⑤：Byte-Level Tokenization 的底线是“任何文本都能被表示”，BPE Merge 再负责让常见文本变得高效

这是一种：

\[
\boxed{
CoverageFirst
+
CompressionLater
}
\]

的设计。

---

# 十一、UTF-8 为什么需要一点概念？

## 62. 中文字符不是一个 Byte

例如一个常见汉字在 UTF-8 中：

> 通常使用 3 个 Byte。

Emoji：

> 可能使用更多 Byte。

---

## 63. 所以极端情况下

一个罕见字符如果没有合适 merge：

> 可能变成多个底层 Token 单位。

---

## 64. 这意味着什么？

Tokenizer 对某种语言支持差时：

同样一段人类文字：

> Token 数会很高。

这叫：

# Tokenization Inefficiency

---

# 十二、Token Fertility

## 65. 一个非常实用的指标

可以研究：

\[
\boxed{
TokenFertility
}
\]

粗略说：

> 一个词、字符或文本单位平均被切成多少 Token。

---

## 66. 例如

100 个中文字符：

Tokenizer A：

\[
120\ Tokens
\]

Tokenizer B：

\[
250\ Tokens
\]

显然：

> B 对这段中文更“费 Token”。

---

## 67. 采购领域也可以测

例如建立一个语料集：

- 招标公告；
- 招标文件；
- 采购需求；
- 质疑答复；
- 投诉处理决定；
- 政策法规。

然后统计：

\[
\boxed{
TokensPerChineseCharacter
}
\]

或：

\[
\boxed{
TokensPerDocument
}
\]

---

## 68. 为什么这个指标很重要？

同样：

\[
128K
\]

Context Window，

如果一份文档 Token 化效率低：

> 能装下的中文正文就更少。

---

## 69. 所以 Context Window 不是纯粹字符数

模型说：

\[
128K\ Tokens
\]

不是：

> 128K 个汉字。

能装多少文字：

> 取决于 Tokenizer。

---

# 十三、WordPiece

## 70. 第二个常见名字

# WordPiece

它因 BERT 等模型而广为人知。

---

## 71. WordPiece 和 BPE 很像吗？

高层直觉：

> 都是 Subword。

都希望：

> 高频有意义片段形成较大单元。

---

## 72. 但它选择合并的标准不同

BPE 的经典直觉：

> 找最频繁 pair。

WordPiece 的经典设计更偏向：

> 选择能够较好提升语言建模/词表解释能力的组合。

---

## 73. 所以不要死记成

\[
WordPiece=BPE
\]

更准确：

\[
\boxed{
两者都属于Subword家族，
但Vocabulary学习目标和细节不同
}
\]

---

## 74. WordPiece 常见视觉特征

在一些实现中会看到：

```text
play
##ing
```

`##` 表示：

> 这是词内部续接片段。

---

## 75. 中文中这个现象看起来没那么直观

因为中文天然：

> 不靠空格划词。

但 WordPiece 同样可以：

> 把中文字符或片段作为 Vocabulary Entry。

---

# 十四、SentencePiece

## 76. 第三个经常被误解的名字

# SentencePiece

很多人以为 SentencePiece 是：

> 和 BPE 完全并列的单一算法。

其实更准确：

> 它是一套直接从原始文本训练和执行 Subword Tokenization 的框架。

---

## 77. SentencePiece 可以使用不同模型

例如：

- BPE；
- Unigram Language Model。

所以：

\[
\boxed{
SentencePiece
\neq
只有一种Subword算法
}
\]

---

## 78. SentencePiece 一个重要设计

它可以：

> 直接从 raw text 学习。

不强制依赖：

> 语言特定的预分词器。

这对：

- 中文；
- 日文；
- 多语言；

特别有吸引力。

---

# 十五、为什么空格也是信息？

## 79. 英文里

```text
government procurement
```

空格：

> 是很重要的词边界。

---

## 80. 中文里

> 政府采购

通常：

> 没有空格。

所以如果 Tokenizer 设计严重依赖英文空格：

> 跨语言表现会很奇怪。

---

## 81. SentencePiece 常把空格编码成一个可见符号概念

例如常见表示：

```text
▁government
```

前面的：

`▁`

表示：

> 前面存在空格/词边界。

---

## 82. 这让空格本身也进入统一符号系统

所以：

> 不需要依赖外部英文式分词规则。

---

# 十六、Unigram Language Model Tokenizer

## 83. SentencePiece 常见另一种算法

# Unigram

思路和 BPE 很不一样。

---

## 84. BPE 是从小到大

\[
SmallUnits
\rightarrow
Merge
\rightarrow
LargeUnits
\]

---

## 85. Unigram 更接近从一个较大候选集合开始

然后评估：

> 哪些 Token 对解释训练语料最重要。

逐步删除：

> 价值较低的 Token。

---

## 86. 可以把它粗略理解成

BPE：

\[
\boxed{
BottomUp
}
\]

Unigram：

\[
\boxed{
TopDownPruning
}
\]

这只是帮助理解。

---

## 87. Unigram 还有一个有趣能力

同一个字符串：

> 可能有多种合法切法。

训练时可以：

> 对不同切分进行采样。

这可以形成：

# Subword Regularization

---

## 88. 为什么随机切分可能有帮助？

假设某词总是：

> 只以一个固定大 Token 出现。

模型可能过度依赖：

> 单一切法。

偶尔拆成更小单元：

> 可以增强组合鲁棒性。

---

# 十七、Tokenizer 通常包含的不只是 Subword Algorithm

## 89. 一个完整 Tokenizer Pipeline 可能有

\[
\boxed{
Normalization
\rightarrow
PreTokenization
\rightarrow
SubwordModel
\rightarrow
PostProcessing
}
\]

不能只盯着：

> BPE 三个字母。

---

# 十八、Normalization

## 90. 文本看起来一样，底层编码可能不同

Unicode 世界里：

> 某些视觉上类似或等价的字符串

可能存在不同编码形式。

---

## 91. Tokenizer 可以先做 Normalization

例如某些配置可能：

- Unicode Normalization；
- 大小写处理；
- 空格处理；
- 特殊字符标准化。

---

## 92. 但 Normalization 是有损风险的

例如：

> 大小写

对于某些任务：

> 有意义。

全角/半角：

> 有时有意义。

法律文书里的原始符号：

> 有时也可能有意义。

所以：

\[
\boxed{
Normalization
=
DesignDecision
}
\]

---

## 93. 政府采购尤其要注意数字和符号

例如：

```text
7×24
7*24
7x24
```

人可能理解为相近。

Tokenizer：

> 可能完全不同。

---

## 94. 再比如

```text
5000万元
5,000万元
5000 万元
伍仟万元
```

语义可能有关联。

表面字符：

> 非常不同。

---

## 95. Tokenizer 不负责自动证明它们相等

Tokenizer 只是：

> 编码输入。

真正语义归一：

> 可能需要模型能力、数据处理或规则系统。

---

# 十九、Pre-tokenization

## 96. 一些 Tokenizer 在 Subword 前会先粗切

例如按照：

- 空格；
- 标点；
- 数字；
- 字母；

先划分片段。

这叫：

# Pre-tokenization

---

## 97. 然后才在片段内部做 BPE 等算法

所以：

\[
RawText
\]

可能先：

\[
Pretokens
\]

然后：

\[
SubwordTokens
\]

---

## 98. 不同 Pre-tokenizer 会明显改变结果

特别是：

- 数字；
- URL；
- 代码；
- 中文标点；
- 混合中英文。

---

# 二十、数字为什么是 Tokenizer 的硬骨头？

## 99. 看这个采购例子

> 注册资本不得低于5000万元

Tokenizer 可能产生：

```text
注册资本
不得
低于
5000
万元
```

这非常舒服。

---

## 100. 也可能

```text
注册
资本
不得
低于
500
0
万
元
```

---

## 101. 甚至不同数字长度切法不同

```text
50
500
5000
50000
```

可能并不拥有：

> 一致的数字结构。

---

## 102. 这会影响模型算数吗？

Tokenizer 是原因之一，但不是全部。

如果：

> 相似数字被切成非常不同的 Token 序列，

模型学习数值规律：

> 会更困难。

---

## 103. 为什么 LLM 有时对数字很奇怪？

因为模型并不是天然接收：

\[
RealNumber
\]

它接收：

\[
TokenSequence
\]

例如：

\[
5000
\]

首先是一段：

> Token 模式。

---

## 104. 所以“数字理解”不是普通计算器式输入

计算器看到：

\[
5000
\]

可能直接当整数。

LLM 首先看到：

> 若干 Token ID。

这是一条非常重要的差异。

---

# 二十一、政府采购金额尤其值得测试

## 105. 例如

```text
400万元
4000万元
40000万元
```

从业务上：

> 差一个数量级非常重要。

Tokenizer 是否：

> 对这些数字形成稳定可学习结构，

值得专门评测。

---

## 106. 还有百分比

```text
10%
0.1
百分之十
10％
```

表面形式：

> 多种多样。

---

## 107. 日期也是一样

```text
2026-09-11
2026年9月11日
2026/09/11
```

法律和采购文件中：

> 日期信息非常关键。

---

# 二十二、Tokenizer 会不会理解法律术语？

## 108. 不会以业务意义“理解”

它可能把：

> “政府采购法”

作为完整 Token。

但这不表示：

> Tokenizer 知道这是一部法律。

---

## 109. Tokenizer 学的是统计切分价值

例如字符串非常常见：

> 值得作为较大 Token。

至于真正语义：

> 由模型训练负责。

所以：

\[
\boxed{
TokenizationFrequency
\neq
SemanticUnderstanding
}
\]

---

# 二十三、一个专业词被拆开，是不是模型就一定不认识？

## 110. 不是

假设：

> “履约验收”

被切成：

```text
履约
验收
```

模型完全可以：

> 通过组合理解整个概念。

---

## 111. 就算拆成

```text
履
约
验
收
```

理论上仍可以学习。

只是：

> 序列更长、组合负担更重。

---

## 112. 所以“一个专业术语必须等于一个 Token”是错误结论

真正问题应该是：

\[
\boxed{
这种切分是否显著影响效率和任务性能？
}
\]

---

# 二十四、什么时候专业词拆分可能确实值得关注？

## 113. 如果一个高频核心术语

在你的领域语料里：

> 每份文件出现几十次。

却平均被拆成：

\[
6\sim10
\]

个 Token。

---

## 114. 那么累计代价可能很大

例如：

\[
1000
\]

次出现，

每次比理想情况多：

\[
5
\]

个 Token。

就是：

\[
5000
\]

额外 Token。

---

## 115. 所以领域 Tokenizer 分析应该看频率

不是只挑几个词说：

> “这个切得不好看。”

真正要计算：

\[
\boxed{
Frequency
\times
ExtraTokens
}
\]

---

# 二十五、Domain Tokenization Efficiency

## 116. 可以定义一个简单工程指标

例如对采购语料：

\[
\boxed{
CompressionRatio
=
\frac{Characters}
{Tokens}
}
\]

或者反过来：

\[
\boxed{
TokensPer1KChars
}
\]

---

## 117. 再按文档类型切片

公告：

\[
Tokens/1KChars
\]

法规：

\[
Tokens/1KChars
\]

招标文件：

\[
Tokens/1KChars
\]

质疑投诉：

\[
Tokens/1KChars
\]

---

## 118. 为什么要 Slice？

Tokenizer 可能对：

> 普通中文很好。

但对：

- 产品型号；
- 技术参数；
- 数字；
- 表格；
- 法规编号；

特别差。

---

# 二十六、一个采购技术参数例子

## 119. 文本

```text
CPU主频≥3.2GHz，内存≥32GB，支持Wi-Fi 6E。
```

这里混合：

- 中文；
- 英文；
- 数字；
- 单位；
- 符号；
- 连字符。

---

## 120. Tokenizer 可能把它切得很碎

如果每个技术参数：

> 都膨胀很多 Token，

IT 采购文件：

> Context 消耗会异常高。

---

## 121. 所以 ProcurementLM Tokenizer Benchmark 应该专门包含

不只是：

> 普通中文段落。

还应该包括：

- 金额；
- 日期；
- 法规编号；
- 产品型号；
- 技术单位；
- 百分比；
- 数学符号；
- 表格文本；
- 中英文混排。

---

# 二十七、特殊 Token

## 122. Vocabulary 里还有一类特殊成员

# Special Tokens

它们不一定来自普通自然语言。

---

## 123. 常见的有

\[
<BOS>
\]

Beginning Of Sequence。

\[
<EOS>
\]

End Of Sequence。

\[
<PAD>
\]

Padding。

\[
<UNK>
\]

Unknown。

以及：

> Chat Template 特殊 Token。

---

## 124. BOS 是什么？

表示：

> 序列开始。

例如：

```text
<BOS>
用户文本……
```

---

## 125. EOS 呢？

表示：

> 序列结束。

语言模型可以学习：

> 什么时候输出 EOS。

也就是：

> 停止生成。

---

## 126. PAD 为什么需要？

Batch 中不同文本长度不同。

样本 A：

\[
100\ Tokens
\]

样本 B：

\[
300\ Tokens
\]

为了组成规则 Tensor：

> 经常要补齐。

---

## 127. 于是短样本后面加入 PAD

例如：

```text
A A A <PAD> <PAD>
B B B B B
```

这样 Shape：

> 能对齐。

---

## 128. 但模型不应该把 PAD 当正文

所以通常还需要：

# Attention Mask

告诉模型：

> 哪些位置是真的，哪些是 Padding。

这个后面讲 Attention 时正式展开。

---

# 二十八、Chat Model 还有角色 Token

## 129. 例如一段对话

```text
system
user
assistant
```

模型需要知道：

> 谁说了哪一段。

不同模型可能使用：

> 不同特殊 Token 和模板。

---

## 130. 所以 Chat Template 本质上最终也会变成 Token Sequence

用户看到：

```text
用户：请审查这份采购文件
```

内部可能被包装成：

```text
<role_user>
请审查这份采购文件
<end_turn>
<role_assistant>
```

---

## 131. 这就是为什么不能随便换 Chat Template

模型 SFT 时如果一直见：

> 某一套格式，

部署时完全换掉：

> 性能可能下降。

---

# 二十九、Tokenizer 与 Prompt 格式其实相连

## 132. Prompt 最终不是字符串概念

它最终成为：

\[
\boxed{
TokenSequence
}
\]

所以：

- 换换行；
- 加 XML；
- 加 JSON；
- 加 Markdown；

最终都改变：

> Token 序列。

---

## 133. 这也是 Prompt Length 为什么按 Token 算

不是：

> 按 Word。

也不是：

> 按字符。

而是：

\[
\boxed{
NumberOfTokens
}
\]

---

# 三十、Tokenizer 是否可逆？

## 134. Encode

\[
Text
\rightarrow
TokenIDs
\]

---

## 135. Decode

\[
TokenIDs
\rightarrow
Text
\]

理想情况下：

> 尽可能恢复原文。

---

## 136. 但如果 Normalization 做了不可逆处理

例如主动：

> 删除某些字符，

Decode：

> 可能无法恢复原始形式。

所以必须理解具体 Tokenizer 配置。

---

# 三十一、Tokenizer 的确定性

## 137. 推理时大多数常规 Tokenizer

同样输入：

> 通常得到同样 Token IDs。

也就是：

\[
\boxed{
DeterministicEncoding
}
\]

---

## 138. 但训练阶段某些方案可以故意随机

例如前面提到：

# Subword Regularization

同一个字符串：

> 随机选择不同合法切法。

用于：

> 数据增强式训练。

---

# 三十二、为什么模型和 Tokenizer 必须一起发布？

## 139. 模型 Weight 只认识 ID

假设：

\[
ID=9281
\]

训练时代表：

> “供应商”。

Embedding Row：

\[
E_{9281}
\]

已经为它学了参数。

---

## 140. 换一个 Tokenizer 后

如果：

\[
9281
\]

变成：

> “太阳能”。

那么模型接收到这个 ID：

> 仍然会取原来的 Row。

完全错位。

---

## 141. 所以模型 Artifact 应该包含

至少包括：

\[
\boxed{
Weights
+
Tokenizer
+
Vocabulary
+
TokenizerConfig
}
\]

这也是 Model Reproducibility 的一部分。

---

# 三十三、能不能给现有模型“增加几个 Token”？

## 142. 技术上可以

例如 Vocabulary：

\[
V
\]

增加：

\[
K
\]

个新 Token。

Embedding Matrix：

\[
V\times d
\]

就需要变成：

\[
(V+K)\times d
\]

---

## 143. 新增 Row 从哪里来？

旧模型：

> 没有学过。

所以新 Embedding：

> 必须初始化。

然后：

> 再训练。

---

## 144. 输出层也可能需要同步变化

语言模型最后通常要预测：

\[
V
\]

个 Vocabulary Token。

如果 Vocabulary 变大：

> 输出 Head 也必须支持新大小。

---

## 145. 这就是为什么“加专业词表”不是改 JSON 那么简单

至少涉及：

\[
Tokenizer
\]

\[
InputEmbedding
\]

\[
OutputHead
\]

以及：

\[
Training
\]

---

## 146. 如果直接加 Token 不训练会怎样？

新 Token Embedding：

> 基本没有可靠语义。

模型看到：

> 这个 Token

就像看到一个新随机向量。

所以：

\[
\boxed{
AddToken
\neq
AddKnowledge
}
\]

---

# 三十四、这对 ProcurementLM 极其重要

## 147. 如果我们发现基础 Tokenizer

把：

> “政府采购”

拆成：

\[
政府 + 采购
\]

这不一定需要修改。

模型完全可能：

> 已经很好理解。

---

## 148. 即使“框架协议采购”

拆成：

```text
框架
协议
采购
```

也可能非常合理。

---

## 149. 真正需要证据的问题是

修改 Tokenizer 后：

\[
\boxed{
性能收益
>
兼容性成本+训练成本
?
}
\]

---

## 150. 不要因为“看起来切得碎”就重做 Tokenizer

这是一个很常见的冲动。

但重做 Tokenizer：

> 会破坏与基础模型 Embedding 的天然兼容。

成本非常高。

---

# 三十五、预训练模型为何通常不换 Tokenizer？

## 151. 因为 Tokenizer 已经是其参数系统的一部分

基础模型几十亿参数：

> 已经围绕原 Tokenizer 学了很久。

直接换：

> 相当于把输入字典重新编号。

---

## 152. 所以领域微调一般更稳妥的方法

先保留：

\[
\boxed{
OriginalTokenizer
}
\]

然后用：

- CPT；
- SFT；
- RAG；

提升政府采购能力。

---

## 153. 什么时候才考虑 Vocabulary Extension？

例如大量核心领域字符串：

> 切分效率异常差。

并且：

> 造成明显 Context / Compute / Accuracy 问题。

同时你有：

> 足够领域训练数据重新训练新增 Embedding。

才值得认真实验。

---

# 三十六、Tokenizer 需要 Benchmark，而不是凭感觉

## 154. 我们可以建立 Procurement Tokenizer Benchmark

固定一批真实但合规处理后的文本：

- 法规；
- 采购公告；
- 采购需求；
- 招标文件；
- 投诉处理；
- IT 技术参数；
- 医疗参数；
- 工程条款。

---

## 155. 对每个 Tokenizer 统计

\[
Tokens
\]

\[
Tokens/1KChars
\]

\[
MaxSequence
\]

\[
P95Sequence
\]

\[
RareDomainTermFragmentation
\]

---

## 156. 还应该单独测数字

例如：

```text
1万元
10万元
100万元
1000万元
10000万元
```

观察：

> 切分是否稳定。

---

## 157. 测法规编号

例如：

```text
财库〔2020〕46号
```

这类字符串对政府采购：

> 高频且重要。

---

## 158. 测日期和条款号

```text
第22条
第二十二条
2026年9月11日
```

---

## 159. 测企业名称与型号

例如：

```text
ABC-X5000-Pro
```

技术采购中：

> 型号信息可能非常重要。

---

# 三十七、Tokenization 与信息损失

## 160. 好消息是

现代 Subword / Byte Tokenizer 通常：

> 不会因为没见过新词就直接丢掉整个词。

它会：

> 拆小。

---

## 161. 所以碎并不等于丢失

例如：

```text
政
采
贷
```

仍然包含原始字符信息。

模型理论上：

> 可以组合回来。

---

## 162. 真正问题是效率和学习难度

切得越碎：

\[
SequenceLength\uparrow
\]

模型需要更多层计算：

> 把碎片重新组合成概念。

---

# 三十八、为什么常见词有“大 Token”可能更容易？

## 163. 假设“供应商”是单 Token

一开始就有：

\[
E_{\text{供应商}}
\]

一个直接可训练向量。

---

## 164. 如果是三个 Token

\[
供
\]

\[
应
\]

\[
商
\]

模型需要依靠后续上下文：

> 组合成“供应商”。

---

## 165. 但大 Token 也有代价

如果 Vocabulary 把所有可能词都加入：

> 参数爆炸。

而且：

> 稀有大 Token 训练次数少。

其 Embedding 可能：

> 反而学不好。

---

## 166. 所以又回到统计折中

高频片段：

> 值得独立 Token。

低频片段：

> 组合更划算。

这就是 Subword 的漂亮之处。

---

# 三十九、Tokenizer 与语言公平性

## 167. 如果一种语言平均更费 Token

那么同一个：

\[
ContextWindow
\]

它实际能表达：

> 更少内容。

---

## 168. 同一个 API Token 计费体系下

也可能导致：

> 使用成本不同。

所以 Tokenizer：

> 也会影响多语言系统体验。

---

# 四十、中文 Tokenizer 的特殊点

## 169. 中文没有天然空格分词

例如：

> 政府采购监督管理部门

到底是：

```text
政府采购
监督管理
部门
```

还是：

```text
政府
采购
监督
管理部门
```

并没有唯一正确答案。

---

## 170. Subword 的优势就在这里

不要求：

> 先有人类给出唯一“正确分词”。

模型可以基于：

> 语料统计形成有效单位。

---

# 四十一、政府采购里的复合术语

## 171. 例如

> “竞争性磋商”

可以：

```text
竞争性
磋商
```

也可以整个：

```text
竞争性磋商
```

---

## 172. 两种切法哪个绝对正确？

没有。

要看：

- Vocabulary 预算；
- 语料频率；
- 训练效果；
- 压缩效率。

Tokenizer 优化目标：

> 不等于语言学词典。

---

# 四十二、Tokenizer 与法律条款边界

## 173. Tokenizer 不知道“第十七条”是法律结构

它可能切：

```text
第
十七
条
```

---

## 174. 但后面的模型可以学习

这些 Token 组合：

> 经常表示法律条款编号。

所以：

\[
\boxed{
Tokenizer负责表示
}
\]

\[
\boxed{
Transformer负责上下文化建模
}
\]

---

# 四十三、为什么不能把 Tokenizer 看成“智能理解器”？

## 175. 因为它的主要任务不是判断语义

它不负责回答：

> 这条资格条件是否合理。

它只是把字符串：

> 转换成可处理的离散单元。

---

## 176. 很粗略地说

Tokenizer：

\[
\boxed{
Compression/EncodingLayer
}
\]

Transformer：

\[
\boxed{
ContextualComputationLayer
}
\]

---

# 四十四、Tokenizer 和 RAG Chunking 也不是一回事

## 177. Tokenization

把：

> 字符串拆成模型基本输入单位。

---

## 178. Chunking

把：

> 长文档拆成检索单元。

例如：

```text
采购文件
↓
资格条件 Chunk
评分办法 Chunk
技术参数 Chunk
```

---

## 179. 一个 Chunk 内部仍然需要 Tokenizer

所以：

\[
\boxed{
Document
\rightarrow
Chunks
\rightarrow
Tokens
}
\]

两个层级完全不同。

---

# 四十五、Chunk Size 为什么经常用 Token 表示？

## 180. 因为最终模型 Context 限制：

> 按 Token。

所以 RAG 中常见：

\[
ChunkSize=512\ Tokens
\]

而不是：

> 512 个汉字。

---

# 四十六、Tokenizer 与 Context Window

## 181. 假设模型 Context Length

\[
C=32768
\]

那么所有输入：

- System Prompt；
- User Prompt；
- RAG Evidence；
- Chat History；
- Generated Tokens；

都共同消耗：

\[
TokenBudget
\]

---

## 182. 所以 ProcurementAI 系统必须学会预算 Token

例如：

\[
System=1500
\]

\[
UserDocument=18000
\]

\[
RAG=8000
\]

已经：

\[
27500
\]

还要留：

> 输出空间。

---

## 183. Tokenizer 因此直接影响系统架构

如果同一文件：

\[
18000
\]

变成：

\[
26000
\]

那么 RAG Evidence：

> 就塞不下那么多了。

---

# 四十七、Tokenizer 可以改变模型“看到的距离”

## 184. 人看两个词之间距离

可能是：

> 10 个汉字。

模型看的是：

> 中间隔了多少 Token。

---

## 185. 如果一段字符串切得特别碎

两个业务概念在 Token 序列中的距离：

> 会变大。

这会影响：

- Context 使用；
- Position；
- Attention 距离。

---

# 四十八、Position 编码为什么下一阶段马上就必须出现？

## 186. 现在我们已经有

\[
TokenIDs
\]

再经过 Embedding：

\[
H_0
\]

但 Token Embedding 只告诉：

> “我是谁”。

---

## 187. 它还没有告诉模型

> “我在哪里”。

例如：

```text
采购人 限制 供应商
```

和：

```text
供应商 限制 采购人
```

Token 内容非常相似。

顺序：

> 决定语义。

---

## 188. 所以 LLM 输入至少需要两个维度的信息

\[
\boxed{
TokenIdentity
}
\]

和：

\[
\boxed{
TokenPosition
}
\]

---

# 四十九、Tokenizer 的最终统一视角

## 189. Raw Text 是连续字符串

例如：

```text
供应商注册资本不得低于5000万元
```

---

## 190. Tokenizer 把它变成离散序列

\[
[t_1,t_2,\ldots,t_S]
\]

---

## 191. Vocabulary 把 Token 变成 ID

\[
[id_1,id_2,\ldots,id_S]
\]

---

## 192. Embedding 把 ID 变成向量

\[
[e_1,e_2,\ldots,e_S]
\]

---

## 193. 于是 Shape 变成

单样本：

\[
(S,D)
\]

Batch：

\[
\boxed{
(B,S,D)
}
\]

---

## 194. 到这里才真正进入 Transformer

所以 LLM 的入口不是：

\[
Text\rightarrow Transformer
\]

而更准确是：

\[
\boxed{
Text
\rightarrow
Tokenizer
\rightarrow
IDs
\rightarrow
Embedding
\rightarrow
Transformer
}
\]

---

# 五十、本阶段最重要的 7 个核心心智模型

| 心智模型 | 核心认知 |
|---|---|
| **① Tokenizer 是语言与模型之间的接口协议** | 模型看到的不是原始字符串，而是 Token 序列 |
| **② Tokenizer 同时决定语言效率和计算效率** | Token 数会影响 Context、显存、延迟和 Attention 成本 |
| **③ Subword 是 Vocabulary 与 Sequence Length 的折中** | 高频片段变大 Token，低频内容拆小 |
| **④ Tokenizer 与模型 Weight 强绑定** | Token-ID 映射不能随意替换 |
| **⑤ Byte-Level 的核心价值是覆盖性** | 底层几乎任何文本都能表示，再靠 Merge 提升效率 |
| **⑥ 专业术语被拆开不等于模型无法理解** | 真正应评估效率、训练难度和任务性能 |
| **⑦ Tokenizer 是压缩/编码层，不是业务推理层** | 合规判断仍来自后续模型、证据与规则 |

---

# 五十一、BPE、WordPiece、SentencePiece 一次分清

可以先记这个框架：

| 名称 | 核心理解 |
|---|---|
| **BPE** | 反复合并高价值/高频相邻单元，形成 Subword Vocabulary |
| **WordPiece** | 同属 Subword，但 Vocabulary 构造准则与经典 BPE 不完全相同 |
| **SentencePiece** | 一套直接处理原始文本的 Tokenization 框架，可使用 BPE、Unigram 等模型 |
| **Byte-Level BPE** | 以 Byte 覆盖为底座，再使用 BPE Merge 提升压缩效率 |
| **Unigram** | 从候选 Token 集合出发，通过概率模型逐步筛选有效 Vocabulary |

不要把它们背成产品名。

要问：

\[
\boxed{
BaseUnit是什么？
}
\]

\[
\boxed{
Vocabulary怎么学习？
}
\]

\[
\boxed{
输入怎么切？
}
\]

\[
\boxed{
未知字符怎么处理？
}
\]

---

# 五十二、如果只记一个核心公式

Tokenizer 最重要的工程关系其实不是复杂数学，而是：

\[
\boxed{
Text
\xrightarrow{Tokenizer}
TokenIDs
\xrightarrow{Embedding}
\mathbb R^{S\times D}
}
\]

其中：

\[
S
\]

就是 Tokenizer 最直接影响的变量。

---

# 五十三、再加一个成本公式

标准 Self-Attention 的一项主要计算随：

\[
S
\]

大致呈：

\[
\boxed{
O(S^2)
}
\]

所以：

\[
\boxed{
TokenizerEfficiency
\rightarrow
ModelEfficiency
}
\]

不是一句漂亮口号，而有直接计算含义。

---

# 五十四、一个 ProcurementLM Tokenizer 实验

假设未来我们真正选一个 7B/14B 基础模型。

不要先修改 Tokenizer。

先建立：

# Procurement Tokenization Audit

拿：

\[
10000
\]

个真实采购文本片段。

---

## 195. 第一组：法规

例如：

> 政府采购法、实施条例、部门规章、规范性文件。

统计：

\[
Tokens/1KChars
\]

---

## 196. 第二组：采购文件

资格条件、商务要求、评分标准、技术参数。

分别统计：

> Token Density。

---

## 197. 第三组：核心领域词

例如：

```text
政府采购
采购人
采购代理机构
供应商
框架协议采购
竞争性磋商
单一来源采购
质疑答复
投诉处理
履约验收
中小企业声明函
```

记录：

> 每个术语被拆成几个 Token。

---

## 198. 第四组：数字和符号

例如：

```text
5000万元
30%
7×24小时
ISO9001
GB/T 19001
财库〔2020〕46号
```

观察：

> 切分稳定性。

---

## 199. 第五组：长文档成本

统计每类完整文件：

\[
P50
\]

\[
P90
\]

\[
P95
\]

\[
P99
\]

Token Length。

---

## 200. 然后才回答是否需要改 Tokenizer

如果原 Tokenizer：

- 中文效率合理；
- 核心术语切分可接受；
- 技术参数没有灾难性膨胀；
- Context 够用；

那么：

\[
\boxed{
不要为了“更专业”而乱换Tokenizer
}
\]

---

# 五十五、为什么这是一个很重要的工程结论？

因为我们做政府采购领域模型的目标是：

> 提升专业能力。

而不是：

> 重新发明基础语言模型全部底层组件。

如果现有 Tokenizer 已经够用：

> 把资源投入到专家数据、RAG、SFT、评测，

往往价值更高。

---

# 五十六、什么时候真的值得考虑扩词表？

至少应该出现类似证据：

\[
\boxed{
高频领域文本
+
严重Token膨胀
+
明显性能/成本问题
+
足够继续训练数据
}
\]

这时才值得做：

> Vocabulary Extension 实验。

---

# 五十七、最危险的做法

拿到一个训练好的 14B 模型。

然后：

> “我自己重新训练一个采购 Tokenizer，中文切得漂亮多了。”

接着直接用新 Tokenizer：

> 喂旧模型。

这基本相当于：

\[
\boxed{
重新给词典编号，
但要求模型继续读懂旧编号
}
\]

当然会出问题。

---

# 五十八、第 9 阶段一句话压缩

\[
\boxed{
Tokenizer决定了模型用哪些离散积木观察文本；
Subword算法则在“完整词太多”和“字符序列太长”之间寻找统计上的高效折中。
}
\]

---

# 五十九、第二课 1～9 阶段现在已经串起来

第 1～7 阶段：

> 神经网络怎么计算和学习。

第 8 阶段：

\[
TokenID\rightarrow Embedding
\]

解决：

> 离散符号怎么进入向量空间。

第 9 阶段：

\[
Text\rightarrow TokenID
\]

解决：

> 原始文本怎么变成离散符号。

所以倒过来组合：

\[
\boxed{
RawText
\rightarrow
Tokenizer
\rightarrow
TokenIDs
\rightarrow
Embedding
\rightarrow
HiddenStates
}
\]

LLM 的输入管线已经只缺一个非常关键的东西：

\[
\boxed{
Position
}
\]

---

# 六十、第 9 阶段掌握标准

完成这一阶段以后，你应该能自然解释：

> Token 为什么不等于 Word？

> 为什么不用纯字符级 Tokenizer？

> 为什么不用纯词级 Tokenizer？

> 什么叫 OOV？

> Subword 为什么能同时缓解词表膨胀和未知词问题？

> BPE 的 Merge 到底在做什么？

> Byte-Level BPE 为什么几乎可以覆盖任意文本？

> WordPiece 与 BPE 为什么不能简单画等号？

> SentencePiece 为什么更准确地说是一套框架？

> Unigram 和 BPE 的高层思路有什么区别？

> Vocabulary Size 为什么会影响 Embedding 参数量？

> Token 数为什么会影响 Attention 成本？

> 为什么“框架协议采购”被拆成三个 Token 不代表模型不理解它？

> 为什么给模型新增一个 Token 并不等于给模型增加一个知识点？

> 为什么不能随意给已经训练好的模型换 Tokenizer？

> 为什么领域模型应该先做 Tokenization Audit，而不是先重做 Vocabulary？

> 为什么数字、金额、日期、法规编号、产品型号需要单独测试？

> Special Token、BOS、EOS、PAD 分别在解决什么问题？

> 为什么 Chat Template 最终也是一种 Token 序列格式？

> Tokenization 和 RAG Chunking 为什么是完全不同层级的概念？

如果这些已经能够从底层机制讲明白：

\[
\boxed{
第二课第9阶段真正建立起来了
}
\]

下一阶段，我们终于要补上 LLM 输入层最后一个大缺口：
