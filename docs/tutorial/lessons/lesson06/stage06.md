# 第六课 · 第 6 阶段
# Retrieval：Top-K 找到了，真的代表找对了吗？
## 从“向量上接近”走向“业务上找到正确证据”

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，Retriever 的目标不是让“看起来相关”的文本靠前，而是让真正能够支持问题的 Gold Evidence 尽可能进入足够靠前的位置。**
2. **第二，Hit@K 看是否至少命中，Recall@K 看 Gold Set 覆盖率，MRR 看第一条正确证据出现得有多早；三者回答的问题不同。**
3. **第三，政府采购 Retrieval Benchmark 必须包含 Hard Negative、时间版本、辖区和 No-answer Query，否则无法测出真正的业务边界。**
4. **第四，正确证据没进 Top-K 时，要区分 Knowledge、Chunking、Metadata Filter、Embedding、ANN、Ranking、Version 和 Duplicate 等失败类型，不能一律归咎于 Embedding。**
5. **第五，Retrieval Evaluation 必须和 Generation Evaluation 分离：先证明“证据找到了”，再讨论“模型有没有正确使用证据”。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `Query` | Query/Q：当前 Token 表示“我要找什么”的向量 |
| `Rank` | LoRA Rank：低秩增量的容量参数 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `Recall` | 召回率：真实风险中被系统成功找出的比例 |
| `Chunking` | 分块：把长文档切成适合检索和上下文组装的片段 |

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

第 5 阶段，我们已经解决了一个工程问题：

\[
\boxed{
怎样快速找到向量上最接近的候选
}
\]

但今天要解决更重要的问题：

> **最接近的候选，真的是正确证据吗？**

假设用户问：

> “采购文件要求供应商在投标截止前已经在本地设立服务机构，这种条件是否存在风险？”

Retriever 返回：

```text
Top-1:
中标后供应商应保证本地现场服务能力

Top-2:
不得以供应商所在地限制或者排斥供应商

Top-3:
供应商应具备履行合同所必需的设备和专业技术能力
```

从语义相似度看：

> Top-1 可能很像。

但真正能回答“投标前本地机构准入条件”的证据，

可能是：

> Top-2。

所以今天开始，我们第一次正式把：

# Retrieval Evaluation
## 检索评测

从 Generation Evaluation 中拆出来。

本阶段最终形成：

# `ProcurementRetrievalBenchmark_V0.1`

---

# 一、先锁死本阶段最重要的一句话

Retriever 的目标不是：

> **把“看起来相关”的文本排在前面。**

而是：

> **让真正能够支持当前问题的 Gold Evidence 尽可能进入足够靠前的位置。**

所以：

\[
\boxed{
Similarity
\neq
Relevance
}
\]

更进一步：

\[
\boxed{
Relevance
\neq
Sufficiency
}
\]

一段 Chunk 可能：

> 和问题主题相关，

但仍然不足以支持最终判断。

因此我们评测 Retrieval 时，真正关心的是：

> **正确证据有没有被召回、排到了哪里、是否足够完整。**

---

# 二、什么是 Gold Evidence？

要评测 Retrieval，必须先知道：

> “正确答案应该搜到哪一条证据？”

这就是：

# Gold Evidence
## 标准证据

例如：

```text
Query:
“投标前必须设本地机构是否存在风险？”

Gold Evidence:
DOC_001_A12_C01
```

这里的 Gold Evidence 不一定只能有一条。

真实问题可能需要：

```text
Gold Evidence Set
=
{
  A,
  B,
  C
}
```

例如：

```text
A
一般规则

B
地方适用规则

C
例外条款
```

所以：

\[
\boxed{
GoldEvidence
可以是集合
}
\]

而不是永远只有单一 Chunk。

---

# 三、Gold Evidence 必须按“证据粒度”定义

这是一个很容易做错的地方。

假设完整正确证据是：

```text
第十二条
```

但 Chunking 后它被拆成：

```text
A12_C01
A12_C02
A12_C03
```

如果只把：

```text
A12_C02
```

标成 Gold，

可能过于严格。

反过来，

如果整份文档：

```text
DOC_001
```

都算 Gold，

又太宽松。

所以 Gold Label 必须与我们的：

# Retrieval Unit
## 检索粒度

对齐。

常见做法是定义：

```text
Exact Gold Chunk
Relevant Chunk Set
Parent Article
Document-level Relevance
```

然后分别评估。

因此：

\[
\boxed{
EvaluationGranularity
必须和
ChunkingGranularity
对齐
}
\]

---

# 四、Hit@K：正确证据有没有进入前 K 名？

最简单的指标是：

# Hit@K

如果一个 Query 的 Gold Evidence 进入 Top-K：

\[
Hit@K=1
\]

否则：

\[
Hit@K=0
\]

例如：

```text
Gold = B

Top-5 =
A
C
B
D
E
```

那么：

\[
Hit@5=1
\]

因为 B 在前 5 名里。

如果：

```text
Top-2 =
A
C
```

那么：

\[
Hit@2=0
\]

Hit@K 回答的是：

> **“至少有没有一条正确证据进入候选集？”**

---

# 五、Recall@K：多个 Gold Evidence 找回了多少？

假设：

\[
Gold
=
\{A,B,C,D\}
\]

Retriever Top-5 找到：

\[
\{A,B,X,Y,Z\}
\]

那么：

\[
Recall@5
=
\frac{2}{4}
=
0.5
\]

因为四条 Gold Evidence 中只找回两条。

所以：

# Recall@K

回答：

> **所有应该找到的证据里，前 K 名找回了多少。**

这和 Hit@K 不同。

Hit@K 只关心：

> 有没有至少命中一个。

Recall@K 更关心：

> Gold Set 被覆盖了多少。

---

# 六、MRR：正确证据排得够不够靠前？

假设每个 Query 只关心第一个正确证据出现的位置。

如果：

```text
Gold 第1名出现
```

则：

\[
RR=1
\]

如果：

```text
Gold 第2名出现
```

则：

\[
RR=\frac{1}{2}
\]

如果：

```text
Gold 第5名出现
```

则：

\[
RR=\frac{1}{5}
\]

这叫：

# Reciprocal Rank
## 倒数排名

多个 Query 取平均：

\[
MRR
=
\frac{1}{Q}
\sum_{i=1}^{Q}
\frac{1}{rank_i}
\]

其中：

\[
Q
\]

是 Query 数量。

MRR 关心的是：

> **第一条正确证据出现得有多早。**

这对 RAG 很重要，

因为最终 Context 往往不会塞进几十条证据。

---

# 七、为什么只看 Hit@K 不够？

假设两个 Retriever：

```text
Retriever A
Gold总在第1～2名

Retriever B
Gold总在第9～10名
```

如果只看：

```text
Hit@10
```

它们可能都是：

\[
100\%
\]

但实际体验完全不同。

因为：

```text
A
Reranker压力小
Context更干净

B
需要更大的候选池
无关Chunk更多
后续成本更高
```

所以最好联合看：

```text
Hit@K
Recall@K
MRR
Rank Distribution
```

而不是一个指标包打天下。

---

# 八、Retrieval Benchmark 必须包含 Hard Negative

这和第五课训练 Benchmark 完全呼应。

例如：

```text
Query:
投标前要求本地机构
```

正确证据：

```text
Gold:
不得要求供应商在投标前预先设立本地机构
```

困难负例：

```text
Hard Negative:
中标后应建立本地售后服务体系
```

两者词面和语义都很接近，

真正差别在：

```text
投标前
vs
中标后

准入
vs
履约
```

如果 Retriever 经常把 Hard Negative 排在 Gold 前面，

说明：

> 它抓住了大主题，却没有抓住真正业务边界。

因此我们需要专门记录：

# Hard Negative Rank

以及：

# Gold-vs-Hard-Negative Margin

概念上：

\[
Margin
=
score(Gold)
-
score(HardNegative)
\]

如果 Margin 经常小于 0：

> 说明检索空间没有很好地区分关键边界。

---

# 九、No-answer Query：没有正确证据时怎么办？

真实系统里并不是每个问题：

> 知识库里一定有答案。

例如用户问：

> “某内部未公开规则是否允许这样做？”

知识库可能根本没有该规则。

如果 Benchmark 只包含：

```text
一定存在Gold Evidence
```

Retriever 很容易学成：

> 无论什么问题都给你找几个“看起来像”的 Chunk。

所以我们还需要：

# No-answer Query
## 无充分证据问题

目标不是让 Retriever：

> 返回空一定最好。

而是让系统能够识别：

> **当前知识库没有足够可信的支持证据。**

这会影响后面的：

```text
score threshold
needs_review
abstention
```

所以：

\[
\boxed{
NoEvidence
也是一种正确结果
}
\]

---

# 十、Score Threshold：Top-K 不代表都该进入 Context

假设 Top-5 分数：

```text
0.91
0.87
0.43
0.39
0.37
```

前两条明显相关，

后面三条可能已经很弱。

如果系统死板地：

```text
永远塞满Top-5
```

就会把噪声一起送给 LLM。

所以可以考虑：

# Score Threshold
## 相似度阈值

例如只保留：

\[
score_i \ge \tau
\]

的候选。

但这里必须非常小心：

> 不同 Embedding Model 的 Score 分布不同。

甚至同一个模型在不同任务上：

> 分数尺度也可能变化。

所以：

\[
\boxed{
Threshold
必须通过Benchmark校准
}
\]

而不能拍脑袋写：

```text
score > 0.8 就一定相关
```

---

# 十一、Retrieval Failure Analysis：找错了以后怎么定位？

以后发现正确证据没进 Top-K，

不能只说：

> “Embedding 不行。”

至少要把失败拆成几类。

```text
1. Knowledge Missing
知识库里根本没有正确证据

2. Chunking Failure
正确文档有，但证据被切碎

3. Metadata Filter Failure
正确证据被错误过滤掉

4. Embedding Failure
语义向量没有把Query和Gold拉近

5. ANN Index Failure
Exact能找到，但ANN漏掉

6. Ranking Failure
Gold被召回，但排名太低

7. Version / Temporal Failure
找到了错误版本

8. Duplicate Domination
Top-K被重复内容占满
```

这张错误地图非常重要。

因为每一类问题的解决方式完全不同。

---

# 十二、怎样构造 `ProcurementRetrievalBenchmark_V0.1`？

每条 Query 至少应该记录：

```json
{
  "query_id": "Q_0001",
  "query": "投标前必须设本地机构是否存在风险？",

  "query_time": "2026-09-17",
  "jurisdiction": "example",

  "gold_chunk_ids": [
    "DOC_001_A12_C01"
  ],

  "acceptable_parent_ids": [
    "DOC_001_A12"
  ],

  "hard_negative_chunk_ids": [
    "DOC_009_A03_C02"
  ],

  "answerability": "answerable",

  "notes": "重点区分投标前准入与中标后履约"
}
```

对于无充分证据问题：

```text
answerability
=
no_evidence
```

这样 Benchmark 才能同时测：

```text
找得到
排得前
分得清
没证据时不乱找
```

---

# 十三、第一版 Retrieval 指标应该记录什么？

我们先不追求几十个指标。

第一版足够实用的是：

```text
Hit@1
Hit@3
Hit@5
Hit@10

Recall@5
Recall@10

MRR

Median Gold Rank
P95 Gold Rank

Hard Negative Above Gold Rate

No-answer False Retrieval Rate
```

再按 Slice 拆：

```text
Normal
Hard Positive
Hard Negative
Boundary
Temporal
Jurisdiction
Version-sensitive
No-answer
```

这样我们就能知道：

> 总体还可以，

到底是哪一类检索在拖后腿。

---

# 十四、Retrieval Evaluation 和 Generation Evaluation 必须彻底分开

这是本阶段最重要的系统工程升级。

如果最终答案错了，

先问：

```text
正确证据进入Top-K了吗？
```

如果：

# 没有

这是：

# Retrieval Failure

LLM 没机会。

如果：

# 有

再问：

```text
正确证据进入最终Context了吗？
```

如果没有：

> 是 Ranking / Context Selection 问题。

如果也有，

但最终答案仍错：

> 才开始重点怀疑 Generation / Reasoning。

所以错误链应该是：

```text
Knowledge
↓
Retrieval
↓
Ranking
↓
Context
↓
Generation
```

每层单独验收。

---

# 十五、本阶段工程产物：`ProcurementRetrievalBenchmark_V0.1`

最终我们要形成：

```text
benchmark_version

query_set_version

gold_evidence_policy

chunk_granularity

query_slices

top_k_values

score_threshold_policy

metrics:
  hit_at_k
  recall_at_k
  mrr
  gold_rank
  hard_negative_rank
  no_answer_behavior

failure_labels:
  knowledge_missing
  chunking_failure
  metadata_filter_failure
  embedding_failure
  ann_failure
  ranking_failure
  version_failure
  duplicate_domination
```

这套 Benchmark 会成为后面：

```text
Embedding Model比较
Vector Index调参
Hybrid Retrieval
Reranker
Query Rewrite
```

的共同裁判。

否则每次优化都只是在：

> “感觉好像搜得更好了。”

---

# 十六、把本阶段压成最精准的 5 句话

> **第一，Retriever 的目标不是让“看起来相关”的文本靠前，而是让真正能够支持问题的 Gold Evidence 尽可能进入足够靠前的位置。**

> **第二，Hit@K 看是否至少命中，Recall@K 看 Gold Set 覆盖率，MRR 看第一条正确证据出现得有多早；三者回答的问题不同。**

> **第三，政府采购 Retrieval Benchmark 必须包含 Hard Negative、时间版本、辖区和 No-answer Query，否则无法测出真正的业务边界。**

> **第四，正确证据没进 Top-K 时，要区分 Knowledge、Chunking、Metadata Filter、Embedding、ANN、Ranking、Version 和 Duplicate 等失败类型，不能一律归咎于 Embedding。**

> **第五，Retrieval Evaluation 必须和 Generation Evaluation 分离：先证明“证据找到了”，再讨论“模型有没有正确使用证据”。**

---

# 本阶段最核心的一张图

```text
                        User Query
                            │
                            ▼
                        Retrieval
                            │
                            ▼
                         Top-K
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
          Hit@K          Recall@K          MRR
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                     Gold Rank Analysis
                            │
                            ▼
                  Hard Negative Analysis
                            │
                            ▼
                    Failure Diagnosis
                            │
          ┌─────────────────┼──────────────────┐
          ▼                 ▼                  ▼
      Knowledge          Retrieval          Ranking
      / Chunking         / Filter           / Version
                            │
                            ▼
                   Retrieval Benchmark
```

脑中最后只留一句：

> **Top-K 只是候选列表；真正的检索质量，要看 Gold Evidence 是否被找回、排得够前、并且能压过那些“很像但不对”的 Hard Negative。**

---

# 第六课 · 第 6 阶段掌握测试

现在不回看正文，你应该能够解释：为什么 Similarity 不等于 Relevance；为什么 Relevance 也不一定等于 Sufficiency；什么是 Gold Evidence；为什么 Gold Evidence 可以是集合；为什么 Gold Label 必须和 Chunking 粒度对齐；Hit@K、Recall@K、MRR 分别测什么；为什么 Hit@10 一样高的两个 Retriever 可能实际表现差很多；什么是 Retrieval Hard Negative；为什么“投标前本地机构”和“中标后本地服务”是典型 Hard Negative；为什么 No-answer Query 必须进入 Benchmark；Score Threshold 为什么不能拍脑袋设；为什么正确证据没进 Top-K 时不能直接怪 Embedding；以及为什么 Retrieval Evaluation 必须先于 Generation Evaluation 独立完成。

如果这些都能够完整讲出来：

\[
\boxed{
第六课第6阶段真正掌握
}
\]

---

# 下一阶段：第六课 · 第 7 阶段
# BM25 + Dense Retrieval：为什么只靠向量检索不够？

到这里我们已经能准确评测：

\[
\boxed{
Retriever到底找没找对
}
\]

下一阶段要解决一个非常现实的问题：

> **Embedding 很擅长语义，但法条编号、金额、机构名称、精确术语、文号这些信息，为什么有时反而是关键词检索更可靠？**

我们会正式把：

```text
Sparse Retrieval
BM25
Dense Retrieval
Score Fusion
Hybrid Retrieval
```

接起来。

并建立下一件工程产物：

# `ProcurementHybridRetrievalPolicy_V0.1`

目标是：

> **让“字面精确匹配”和“语义相似匹配”互补，而不是让两种 Retriever 互相替代。**

---
