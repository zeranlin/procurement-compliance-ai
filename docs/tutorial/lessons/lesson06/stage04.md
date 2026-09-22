# 第六课 · 第 4 阶段
# Embedding：文本为什么可以变成“语义向量”？
## 为什么文字不同，却能在向量空间里靠得很近？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，Embedding 是把 Query 或 Chunk 映射成固定维度向量，使语义相关的文本在模型学出的向量空间里尽量靠近。**
2. **第二，Dense Retrieval 的核心就是分别得到 Query Vector 和 Document Vector，再用 Cosine、Dot Product 或其它兼容度量做 Top-K 排序。**
3. **第三，Query 和 Document 必须进入兼容的检索表示空间；有些模型是对称编码，有些模型需要不同的 Query / Document Prefix 或任务指令。**
4. **第四，Embedding Similarity 只负责候选召回，不等于最终业务正确性；政府采购里的“投标前 vs 中标后”等 Hard Negative 仍可能让语义向量犯错。**
5. **第五，Embedding Model、Revision、Normalization、Similarity Metric 和编码策略必须版本锁定；换模型通常意味着旧知识向量需要重新计算。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Embedding` | 嵌入：把离散 Token 映射到连续高维向量 |
| `Query` | Query/Q：当前 Token 表示“我要找什么”的向量 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Representation` | 表示：模型内部承载语义或特征的向量结构 |
| `Cosine Similarity` | 余弦相似度：比较两个向量方向相似程度 |
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

第 3 阶段，我们已经把长文档处理成：

\[
Document
\rightarrow
Chunk
\]

也就是说，我们终于拥有了真正可以被检索的知识单元。

但现在还有一个问题：

> **Retriever 怎么知道用户的问题和哪个 Chunk 更相关？**

如果用户问：

> “采购文件能不能要求供应商投标前在本地设立分支机构？”

知识库里的正确证据可能写成：

> “不得以供应商所在地、经营年限、预先设立本地机构等条件限制或者排斥潜在供应商。”

两段文字并不完全一样。

如果系统只做：

```text
字符串相等
关键词完全匹配
```

很可能找不到。

所以我们需要一种表示方法，把：

> **一段文本的语义**

压缩成：

> **一个可以计算相似度的数值向量。**

这就是：

# Embedding
## 语义向量表示

本阶段最终形成：

# `ProcurementEmbeddingPolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

Embedding 的本质不是：

> **把一句话翻译成一串“人类可读的数字含义”。**

而是：

> **把文本映射到一个向量空间，使语义上相近的文本，在这个空间里尽量靠近。**

可以写成：

\[
f_{\theta}(text)
=
\mathbf{e}
\in
\mathbb{R}^{d}
\]

其中：

- \(f_{\theta}\)：Embedding Model；
- `text`：Query 或 Chunk；
- \(\mathbf{e}\)：输出向量；
- \(d\)：Embedding Dimension。

例如：

\[
\mathbf{e}
=
[0.13,-0.72,0.08,\ldots]
\]

这个向量通常有几百到几千个维度。

真正重要的不是某一维“代表什么”，而是：

> **向量之间的几何关系。**

---

# 二、Embedding 不是“词典编码”，而是学习出来的表示

假设有三句话：

```text
A:
投标人必须在本市设立固定办公场所

B:
供应商在参与投标前须已经具有本地分支机构

C:
中标后应提供2小时现场服务响应
```

从字符表面看：

```text
A 和 B
用词并不完全相同

A 和 C
都出现“本地 / 现场”一类空间概念
```

但从业务语义看：

```text
A 和 B
都在讨论
“投标前预设本地机构作为准入条件”

C
讨论的是
“中标后的履约响应要求”
```

一个好的 Embedding Model 应尽量形成：

\[
sim(A,B)
>
sim(A,C)
\]

也就是说：

> **相似度应该更接近业务语义，而不是仅仅接近字面重合。**

这就是 Dense Retrieval 能超过纯关键词匹配的核心原因之一。

---

# 三、为什么 Query 和 Chunk 可以互相比较？

在 RAG 中，我们通常会分别计算：

\[
\mathbf{q}
=
f_{\theta}(Query)
\]

和：

\[
\mathbf{d_i}
=
f_{\theta}(Chunk_i)
\]

然后比较：

\[
sim(\mathbf{q},\mathbf{d_i})
\]

如果 Query 和 Chunk 被映射到：

> **同一个可比较的向量空间**

那么就可以把：

```text
用户问题
```

与：

```text
知识库里的每个Chunk
```

做相似度排序。

最终：

\[
TopK
=
\operatorname{arg\,topk}_{i}
\;
sim(\mathbf{q},\mathbf{d_i})
\]

中文就是：

> **找出和 Query 向量最接近的 K 个 Chunk。**

这就是 Dense Retrieval 最核心的计算。

---

# 四、但“同一个模型编码”不等于 Query 和 Document 必须完全同一种写法

这是一个很重要的精度点。

有些 Embedding Model 是：

# Symmetric
## 对称任务

适合比较：

```text
句子 A
vs
句子 B
```

两边形式差不多。

但检索任务经常是：

# Asymmetric Retrieval
## 非对称检索

也就是：

```text
Query:
“投标前必须设本地机构合法吗？”

Document:
一整段法规条文
```

Query 很短，

Document 更长、更正式。

所以很多检索型 Embedding Model 会区分：

```text
query representation
document representation
```

甚至要求不同的：

```text
prefix
instruction
task type
```

因此长期正确心智模型是：

\[
\boxed{
Query
和
Document
必须进入
兼容的检索表示空间
}
\]

而不是死记：

> “两边只要直接调用同一个函数就一定正确。”

---

# 五、一个 Chunk 最后为什么会变成“一个向量”？

Transformer 对一段文本内部通常会产生很多 Token Representation。

例如：

```text
Chunk
↓
Token 1 → h1
Token 2 → h2
Token 3 → h3
...
Token n → hn
```

但向量检索需要的通常是：

> **整个 Chunk 的单个固定长度向量。**

于是需要一个：

# Pooling
## 汇聚

把多个 Token Representation 变成一个 Sentence / Passage Embedding。

概念上可能是：

\[
\mathbf{e}
=
Pool(
\mathbf{h}_1,
\mathbf{h}_2,
\ldots,
\mathbf{h}_n
)
\]

不同模型可能使用：

```text
Mean Pooling
特殊Token表示
加权Pooling
模型专门训练出的Pooling机制
```

所以：

> **Embedding 不是简单把 Token Embedding 平均一下的同义词。**

具体怎样 Pool：

> 是 Embedding Model 架构和训练方式的一部分。

---

# 六、Cosine Similarity 到底在比较什么？

最常见的相似度之一是：

# Cosine Similarity
## 余弦相似度

公式：

\[
\cos(\theta)
=
\frac{
\mathbf{q}\cdot\mathbf{d}
}{
\|\mathbf{q}\|
\|\mathbf{d}\|
}
\]

它比较的是：

> 两个向量方向有多接近。

如果方向非常接近：

\[
\cos(\theta)
\approx 1
\]

如果接近正交：

\[
\cos(\theta)
\approx 0
\]

如果方向相反：

\[
\cos(\theta)
<0
\]

但这里不要形成一个错误理解：

> “Cosine = 人类语义相似度真理。”

不是。

它只是：

> **在这个 Embedding Model 学出的空间里，用一个几何函数比较向量关系。**

效果好不好，最终仍取决于：

> Embedding Model 有没有把我们的业务语义组织好。

---

# 七、Dot Product、Cosine、L2 Distance 不要混

除了 Cosine，还经常见：

# Dot Product
## 点积

\[
\mathbf{q}\cdot\mathbf{d}
\]

以及：

# Euclidean Distance
## 欧氏距离 / L2 Distance

\[
\|\mathbf{q}-\mathbf{d}\|_2
\]

三者不是一回事。

如果向量已经做了：

# L2 Normalization
## L2 归一化

即：

\[
\hat{\mathbf{e}}
=
\frac{\mathbf{e}}{\|\mathbf{e}\|}
\]

那么对于单位向量：

\[
\hat{\mathbf{q}}
\cdot
\hat{\mathbf{d}}
=
\cos(\theta)
\]

这时候：

> Dot Product 和 Cosine 排序会变得等价。

而单位向量之间的 L2 距离也和 Cosine 存在固定关系：

\[
\|\hat{\mathbf{q}}-\hat{\mathbf{d}}\|_2^2
=
2-2\cos(\theta)
\]

所以工程上真正要记录的是：

```text
Embedding Model
是否Normalize
Similarity Metric
Index Metric
```

必须彼此一致。

---

# 八、Embedding Dimension 越大，不代表语义一定越强

假设两个模型：

```text
Model A
768 dimensions

Model B
1536 dimensions
```

不能直接推出：

> Model B 一定更懂政府采购。

Dimension 只是：

> 表示空间的宽度之一。

真正效果还取决于：

```text
训练数据
训练目标
模型架构
多语言能力
检索任务训练
领域分布
Query / Document格式
```

而更高维通常还意味着：

```text
向量存储更大
索引更大
计算成本更高
内存占用更高
```

所以：

\[
\boxed{
HigherDimension
\neq
GuaranteedBetterRetrieval
}
\]

---

# 九、Embedding 的每一维通常没有稳定的人类语义

看到：

\[
[0.13,-0.72,0.08,\ldots]
\]

不要问：

> “第 37 维是不是代表地域限制？”

通常不是这样理解。

Embedding 的意义是：

> **分布式表示。**

业务概念往往不是单独存放在某一个维度，而是体现在：

```text
很多维度
共同组成的方向
距离
局部几何结构
```

所以我们使用 Embedding 时，

关注的是：

\[
Geometry
\]

而不是：

> 每一维的人类解释。

这和第二课里“神经网络知识是分布式表示”是一脉相承的。

---

# 十、Embedding 解决的是“候选召回”，不是最终法律判断

这是政府采购场景必须特别小心的边界。

假设 Query：

> “要求投标前设立本地分公司是否存在风险？”

Embedding 找到两个高相似 Chunk：

```text
Chunk A
不得以供应商所在地限制供应商

Chunk B
中标后可要求供应商建立本地服务团队
```

它们都可能和：

```text
本地
供应商
服务机构
```

语义相关。

但哪一条真正回答用户问题，

还需要：

```text
时间条件
投标前 / 中标后

法律关系
资格准入 / 履约要求

适用区域
文件版本
具体上下文
```

所以 Embedding 更接近：

# Candidate Retrieval
## 候选召回

而不是：

# Final Legal Reasoning
## 最终业务判断

因此：

\[
\boxed{
HighSimilarity
\neq
CorrectAnswer
}
\]

---

# 十一、Embedding 也会产生“语义假朋友”

关键词检索会被字面相似骗。

Embedding 也一样会有自己的错误。

例如：

```text
Query:
投标前必须在本地设立机构

Chunk A:
不得要求供应商投标前在采购人所在地设立机构

Chunk B:
供应商中标后应建立本地售后服务机构
```

Embedding 可能认为：

> A、B 都很相关。

因为它们共享大量语义概念：

```text
供应商
本地
机构
要求
```

但真正的业务决策边界在：

```text
投标前
vs
中标后
```

所以我们第五课一直强调的 Hard Negative，

到了 RAG 一样重要。

这里可以把它叫：

# Retrieval Hard Negative
## 检索困难负例

也就是：

> **语义看起来很近，但实际上不是正确证据。**

这也是后面为什么需要：

```text
Hybrid Retrieval
Reranker
Metadata Filter
```

---

# 十二、真正的离线向量化流程

当 Chunking 完成以后，Offline Indexing 可以继续：

```text
Chunk
  │
  ▼
Embedding Model
  │
  ▼
Vector
  │
  ├── chunk_id
  ├── document_id
  ├── metadata
  └── embedding
  │
  ▼
Vector Index
```

概念上：

```text
DOC_001_A12_C01
→
[0.13, -0.72, ..., 0.08]

DOC_002_A07_C03
→
[-0.22, 0.51, ..., 0.19]
```

这一步通常是：

> **离线完成。**

不是用户每问一次，

就重新对整个知识库做 Embedding。

---

# 十三、在线 Query 流程则只编码当前问题

用户发来：

```text
Query
=
“供应商投标前必须有本地分公司合法吗？”
```

在线流程：

```text
Query
  │
  ▼
Embedding Model
  │
  ▼
Query Vector
  │
  ▼
和知识库向量比较
  │
  ▼
Top-K Candidates
```

也就是：

\[
\mathbf{q}
=
f_{\theta}(Query)
\]

然后：

\[
score_i
=
sim(
\mathbf{q},
\mathbf{d_i}
)
\]

最后按：

\[
score_i
\]

排序。

这就是 Dense Retrieval 的最小数学骨架。

---

# 十四、怎样判断一个 Embedding Model 适不适合政府采购？

不能只看：

> 公共榜单排名。

至少要检查五件事：

```text
中文能力
法规 / 政策文本能力
Query-Document非对称检索能力
长Chunk处理能力
领域Hard Negative区分能力
```

最终还必须拿自己的：

# Retrieval Benchmark

来测。

例如设计：

```text
Query 001
Gold Evidence = 第十二条

Query 002
Gold Evidence = 第二十四条第二款

Query 003
Gold Evidence = 某地方文件旧版本

Query 004
Gold Evidence = needs_review / 无充分证据
```

然后看：

> 正确证据是否进入 Top-K。

也就是说：

\[
\boxed{
EmbeddingModelQuality
必须用RetrievalTask验证
}
\]

不能只看向量维度或模型参数量。

---

# 十五、本阶段工程产物：`ProcurementEmbeddingPolicy_V0.1`

第一版至少记录：

```text
embedding_model_id
embedding_model_revision

embedding_dimension

query_encoding_mode
document_encoding_mode

query_prefix
document_prefix

max_input_tokens

pooling_strategy
如果模型需要记录

normalize_embeddings

similarity_metric

batch_size

device
dtype

chunk_policy_version

embedding_created_at

embedding_version
```

这里有一个特别重要的工程规则：

> **Embedding 一旦更换模型或关键编码策略，已有向量通常不能继续和新向量混用。**

例如：

```text
V1 Knowledge Vectors
来自 EmbeddingModel_A

Query Vector
来自 EmbeddingModel_B
```

即使维度碰巧一样，

也不代表：

> 它们处在同一个语义空间。

所以：

\[
\boxed{
SameDimension
\neq
SameVectorSpace
}
\]

更换 Embedding Model 后，

通常需要：

> **重新 Embedding / Re-index。**

---

# 十六、把本阶段压成最精准的 5 句话

> **第一，Embedding 是把 Query 或 Chunk 映射成固定维度向量，使语义相关的文本在模型学出的向量空间里尽量靠近。**

> **第二，Dense Retrieval 的核心就是分别得到 Query Vector 和 Document Vector，再用 Cosine、Dot Product 或其它兼容度量做 Top-K 排序。**

> **第三，Query 和 Document 必须进入兼容的检索表示空间；有些模型是对称编码，有些模型需要不同的 Query / Document Prefix 或任务指令。**

> **第四，Embedding Similarity 只负责候选召回，不等于最终业务正确性；政府采购里的“投标前 vs 中标后”等 Hard Negative 仍可能让语义向量犯错。**

> **第五，Embedding Model、Revision、Normalization、Similarity Metric 和编码策略必须版本锁定；换模型通常意味着旧知识向量需要重新计算。**

---

# 本阶段最核心的一张图

```text
                   Offline Knowledge Path

                       Chunk
                         │
                         ▼
                  Embedding Model
                         │
                         ▼
                  Document Vector
                         │
                         ▼
                    Vector Index


                    Online Query Path

                      User Query
                         │
                         ▼
                  Embedding Model
                         │
                         ▼
                    Query Vector
                         │
                         ▼
              Similarity / Distance
                         │
                         ▼
                      Top-K
                         │
                         ▼
                Candidate Evidence
```

脑中最后只留一句：

> **Embedding 不是答案，它只是把“这个问题可能和哪些知识最相关”变成可以计算的几何问题。**

---

# 第六课 · 第 4 阶段掌握测试

现在不回看正文，你应该能够解释：Embedding 到底是什么；为什么它不是传统词典编码；为什么语义相近但字面不同的文本可以在向量空间里靠近；Query Vector 和 Document Vector 为什么能够比较；什么是对称检索与非对称检索；为什么一个 Chunk 最后需要 Pooling 成一个固定长度向量；Cosine Similarity、Dot Product、L2 Distance 分别在比较什么；为什么 L2 Normalization 后 Dot Product 可以和 Cosine 等价排序；为什么更高的 Embedding Dimension 不保证更好；为什么不能把某一维解释成“地域限制维度”；为什么高相似度不等于正确业务答案；什么是 Retrieval Hard Negative；Offline Embedding 和 Online Query Encoding 分别发生什么；以及为什么换 Embedding Model 后通常需要重新向量化整个知识库。

如果这些能够完整讲出来：

\[
\boxed{
第六课第4阶段真正掌握
}
\]

---

# 下一阶段：第六课 · 第 5 阶段
# Vector Index / Vector Database：向量到底怎样被快速找到？

到这里我们已经有：

\[
Chunk
\rightarrow
EmbeddingVector
\]

下一阶段要解决的是：

> **如果知识库有 1,000 个向量，逐个比较还可以；如果有 1,000 万个向量，难道每次 Query 都和所有向量做一次完整相似度计算吗？**

我们会正式进入：

```text
Exact Search
Approximate Nearest Neighbor
ANN
Vector Index
HNSW
IVF
Vector Database
Top-K Search
Recall / Latency Trade-off
```

并真正理解：

> **Vector Database 最核心的价值不是“保存向量”，而是让大规模近邻搜索、Metadata Filter、持久化和工程管理变得可用。**

---
