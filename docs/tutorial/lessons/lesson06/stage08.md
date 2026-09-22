# 第六课 · 第 8 阶段
# Reranker：为什么“先召回，再精排”比直接 Top-K 更可靠？
## Retriever 负责“别漏掉”，Reranker 负责“别把错的排太前”

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：MEDIUM。** 审计原因：核心心智模型出现偏后，阅读前段缺少认知锚点；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，Retriever 负责高 Recall 召回，Reranker 负责把最相关的候选重新排到最前面；两者优化目标不同。**
2. **第二，Bi-Encoder 通过独立 Query / Document Vector 实现高效大规模检索，而 Cross-Encoder 让 Query 与候选文本逐 Token 交互，因此更适合细粒度精排，但成本更高。**
3. **第三，Reranker 只能重排已经召回的 Candidate Set，不能救回根本没进入候选集的 Gold Evidence；所以调试必须先区分 Recall Failure 和 Rerank Failure。**
4. **第四，政府采购 Reranker 的关键价值是压制“投标前 vs 中标后”“准入 vs 履约”这类语义很近但业务边界不同的 Hard Negative。**
5. **第五，是否启用 Reranker 必须同时比较 MRR、Gold Rank、Hard Negative 排名改善和新增 Latency / VRAM 成本，而不是只看一个排序分数。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Rank` | LoRA Rank：低秩增量的容量参数 |
| `Reranker` | 重排器：对初筛候选做更精细相关性排序 |
| `BM25` | BM25：基于词频和逆文档频率的经典词法检索算法 |
| `Query` | Query/Q：当前 Token 表示“我要找什么”的向量 |
| `Hard Negative` | 高难负例：表面像风险但正确结论不应判风险 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Recall` | 召回率：真实风险中被系统成功找出的比例 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |

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

第 7 阶段，我们已经把两条召回链接起来：

\[
BM25
+
DenseRetrieval
\rightarrow
CandidateSet
\]

这一步的目标很明确：

> **尽量不要漏掉真正的 Gold Evidence。**

所以召回阶段通常愿意多拿一些候选，例如：

```text
Sparse Top-20
+
Dense Top-20
↓
去重后
得到 25～35 条候选
```

但真正送进 LLM 的 Context 不可能无限大。

于是马上出现第二个问题：

> **这几十条候选里，谁应该排在最前面？**

这就是今天的主题：

# Reranking
## 重排序 / 精排

本阶段最终形成：

# `ProcurementRerankingPolicy_V0.1`

---

# 一、先锁死最重要的职责边界

Retriever 和 Reranker 不应该被当成同一个东西。

Retriever 的第一职责：

\[
\boxed{
High\ Recall
}
\]

也就是：

> **正确证据尽量别漏。**

Reranker 的第一职责：

\[
\boxed{
High\ Precision\ at\ Top
}
\]

也就是：

> **真正最有用的证据尽量排到最前面。**

所以最经典的两阶段结构是：

```text
Query
↓
Retriever
召回较多候选
↓
Candidate Set
↓
Reranker
逐个重新判断 Query-Document 相关性
↓
Final Top-K
```

脑中先记一句：

> **召回阶段怕漏，精排阶段怕错。**

---

# 二、为什么不直接让 Retriever 一次性把 Top-3 排准？

因为 Retriever 的设计目标通常包含：

```text
大规模
低延迟
高吞吐
可索引
可近似搜索
```

Dense Retriever 往往先把 Query 和 Document 分别编码成向量：

\[
\mathbf{q}=f(Q)
\]

\[
\mathbf{d}=g(D)
\]

然后比较：

\[
sim(\mathbf{q},\mathbf{d})
\]

这个方式非常高效，因为 Document Vector 可以：

> **提前离线算好并建立 Index。**

但代价是：

> Query 和 Document 在编码阶段并没有充分逐 Token 交互。

因此一些细粒度差异，例如：

```text
投标前
vs
中标后

必须预先设立
vs
中标后提供服务

本地准入条件
vs
本地履约安排
```

可能无法被单个向量充分表达。

所以：

\[
\boxed{
FastRetriever
擅长快速缩小范围
}
\]

但未必擅长：

> **在非常相似的候选之间做最终精细判断。**

---

# 三、Bi-Encoder 与 Cross-Encoder：这是理解 Reranker 的核心

Dense Retriever 常见的一类结构叫：

# Bi-Encoder
## 双塔 / 双编码器

概念上：

```text
Query
↓
Encoder
↓
Query Vector

Document
↓
Encoder
↓
Document Vector

最后
计算相似度
```

即：

\[
score(Q,D)
=
sim(
f(Q),
g(D)
)
\]

它的优势是：

> Document 可以提前编码。

因此很适合：

> 百万、千万级候选的第一阶段检索。

---

Reranker 常见的一类结构叫：

# Cross-Encoder
## 交叉编码器

它不是先分别压成两个独立向量。

而是把：

```text
Query
+
Document
```

一起送进模型：

\[
score(Q,D)
=
h(Q,D)
\]

于是模型内部可以直接看到：

```text
Query Token
↔
Document Token
```

之间的细粒度交互。

所以它更容易判断：

> “这段法规到底是不是在回答这个具体问题。”

---

# 四、为什么 Cross-Encoder 通常更适合精排？

看一个政府采购 Hard Negative。

Query：

> “采购文件要求供应商在投标前必须设立本地服务机构，是否属于不合理准入条件？”

候选 A：

> “不得要求供应商在参加采购活动前已在采购人所在地设立分支机构。”

候选 B：

> “中标供应商应当在合同履行期间提供本地化售后服务。”

Embedding 可能觉得 A、B 都非常接近 Query。

因为它们都有：

```text
供应商
本地
服务
机构
要求
```

但真正决定相关性的词是：

```text
参加采购活动前
vs
中标后 / 合同履行期间
```

Cross-Encoder 因为 Query 和候选文本一起参与 Attention，

更有机会把这种：

> **局部条件对局部条件**

直接比较。

所以：

\[
\boxed{
CrossEncoder
更擅长细粒度相关性判断
}
\]

---

# 五、为什么不直接拿 Cross-Encoder 搜整个知识库？

因为成本太高。

假设知识库有：

\[
10^7
\]

个 Chunk。

如果每次 Query 都运行：

\[
h(Q,D_i)
\]

一千万次，

几乎不可接受。

Bi-Encoder 可以提前把：

\[
g(D_i)
\]

全部离线计算好，

查询时只需要：

```text
Query Encoding
+
Vector Search
```

而 Cross-Encoder 必须针对每一个 Query-Document Pair 重新 Forward。

因此经典架构就是：

\[
\boxed{
Cheap\ Retrieval
\rightarrow
Expensive\ Reranking
}
\]

也就是：

> **先便宜地缩小候选，再昂贵地精排少量候选。**

---

# 六、Candidate Pool 多大，Final Top-K 多大，是两个不同参数

假设：

```text
Retriever Candidate N = 50
```

并不等于：

```text
最终给 LLM 50 条
```

更常见是：

```text
Retriever
Top-50

↓
Reranker

Final Top-5
```

这里有两个不同目标：

### Candidate N

要足够大，保证：

> Gold Evidence 有机会被召回。

### Final K

要足够小，保证：

> Context 干净、成本可控。

因此：

\[
\boxed{
CandidateN
解决Recall
}
\]

\[
\boxed{
FinalK
解决Precision\ /\ ContextBudget
}
\]

不要把它们混成一个 Top-K 参数。

---

# 七、Reranker 不能救回“根本没召回”的证据

这是本阶段最重要的边界之一。

假设 Gold Evidence：

> 根本不在 Retriever Top-50。

那么 Reranker 无论多强：

> 都看不到它。

所以：

\[
\boxed{
Reranker
只能重新排序候选
不能凭空召回不存在于候选集的证据
}
\]

这意味着调试时一定要先问：

```text
Gold 在 Candidate Set 里吗？
```

如果不在：

> 优先修 Retrieval。

如果在，但排得太后：

> 才重点修 Reranking。

这和第 6 阶段的错误分层完全一致。

---

# 八、Reranker Score 不是概率，也不能随便跨模型比较

很多 Reranker 会输出一个：

```text
relevance score
```

但这个 Score 的数值语义取决于：

```text
模型
训练目标
实现
是否经过Sigmoid / Softmax
输入格式
版本
```

因此：

\[
\boxed{
RerankerScore
\neq
UniversalProbability
}
\]

例如：

```text
Model A
score = 8.2

Model B
score = 0.91
```

不能据此说：

> Model A 更确信。

Reranker Score 最可靠的用途通常是：

> **同一 Query 下做候选排序。**

如果要做 Threshold：

> 必须基于自己的 Benchmark 校准。

---

# 九、Reranker 最应该盯住的，是 Hard Negative 排名

第 6、7 阶段我们已经反复强调：

# Hard Negative

对于政府采购，很多真正难的候选不是完全无关，

而是：

> **高度相关，但关键条件错了一点。**

例如：

```text
Gold:
投标前必须设本地机构
属于准入限制

Hard Negative:
中标后提供本地服务
属于履约要求
```

一个好的 Reranker 应该实现：

\[
score(Gold)
>
score(HardNegative)
\]

并最好形成稳定 Margin：

\[
Margin
=
score(Gold)
-
score(HardNegative)
\]

因此 Stage 8 的重点不是只看：

> 平均 MRR 有没有涨。

还要看：

```text
Hard Negative Above Gold Rate
↓
```

有没有明显下降。

---

# 十、Reranking 前后，哪些指标最值得比较？

我们已经有：

# `ProcurementRetrievalBenchmark_V0.1`

所以可以固定同一 Candidate Set，

比较：

```text
Before Rerank
vs
After Rerank
```

重点看：

| 指标 | 关注什么 |
|---|---|
| Hit@K | Gold 是否仍在候选范围内 |
| MRR | 第一条 Gold 是否更靠前 |
| Median Gold Rank | 典型 Query 的 Gold 排名 |
| P95 Gold Rank | 尾部困难 Query |
| Hard Negative Above Gold Rate | 困难负例是否还压在 Gold 上面 |
| NDCG@K | 多级相关性时，整体排序质量 |
| Latency | 精排带来的额外时延 |

这里可以引入：

# NDCG
## Normalized Discounted Cumulative Gain

当相关性不是简单：

```text
Relevant
vs
Irrelevant
```

而是：

```text
3 = 核心证据
2 = 强相关辅助证据
1 = 弱相关背景
0 = 无关
```

时，

NDCG 会比单纯 MRR 更适合评价：

> **整个 Top-K 排序质量。**

本阶段先理解用途，不要求背完整公式。

---

# 十一、Reranker 的成本主要花在哪？

Retriever 可以：

> 一次 Query Encoding + ANN Search。

Reranker 则要对：

\[
N
\]

个候选分别构造：

\[
(Q,D_1), (Q,D_2), \ldots, (Q,D_N)
\]

然后做模型 Forward。

所以粗略上：

\[
RerankCost
\propto
CandidateN
\times
PairSequenceLength
\]

真实成本还与：

```text
模型大小
Batch Size
GPU / CPU
最大Token长度
动态Padding
实现Kernel
```

有关。

因此：

> Candidate Pool 不是越大越好。

如果从：

```text
Top-50
```

扩大到：

```text
Top-500
```

可能 Recall 稍涨，

但 Reranker 延迟和算力成本可能大幅上升。

---

# 十二、Batching：Reranker 工程效率的关键

虽然每个 Query-Document Pair 都需要重新计算，

但不代表必须一个一个串行跑。

可以把多个 Pair 组成 Batch：

```text
(Q, D1)
(Q, D2)
(Q, D3)
...
```

一起进入 GPU。

这样可以显著提高：

# Throughput
## 吞吐

但 Batch 过大又可能：

> OOM。

所以要 Benchmark：

```text
rerank_batch_size
p50_latency
p95_latency
pairs_per_second
peak_vram
```

这和第五课训练显存的思想很相似：

> **工程优化必须看真实瓶颈，而不是只改一个参数。**

---

# 十三、Reranker 输入长度也会反过来影响 Chunking

假设某个 Chunk：

```text
4000 Tokens
```

而 Reranker 支持的最大输入长度有限。

那可能发生：

```text
Query + Chunk
↓
Truncation
↓
真正关键证据恰好被截掉
```

于是一个“模型能力问题”，其实是：

# Reranker Input Truncation

所以 Stage 3 的 Chunking Policy 到这里再次回来。

需要记录：

```text
reranker_max_tokens
query_token_budget
document_token_budget
truncation_policy
```

尤其政府采购条文中：

> 例外条件、但书、后半段限制

经常非常关键。

不能总是简单：

> 从末尾硬截。

---

# 十四、Reranker 也不能替代 Metadata / Version Filter

假设候选里同时有：

```text
2022旧版
2026现行版
```

两段文字都和 Query 极其相关。

如果用户问：

> “按照 2026 年现行规定……”

我们不应该把所有责任都丢给 Reranker，

让它自己猜：

> 哪一份当前有效。

更可靠的系统仍然应该先利用：

```text
query_time
effective_from
effective_to
validity_status
jurisdiction
```

做硬约束或强过滤。

因此：

\[
\boxed{
BusinessMetadataConstraint
\neq
SemanticReranking
}
\]

Reranker 负责：

> 在合法候选空间内判断相关性。

Metadata / Version Policy 负责：

> 定义哪些候选本来就不应该参与竞争。

---

# 十五、第一版 Reranking Pipeline 应该怎么设计？

对于 `ProcurementRAG_V0.1`，建议先采用清楚的两阶段结构：

```text
User Query
    │
    ▼
Metadata / Validity Filter
    │
    ▼
BM25 + Dense Retrieval
    │
    ▼
Fusion / RRF
    │
    ▼
Candidate Top-N
    │
    ▼
Cross-Encoder Reranker
    │
    ▼
Reranked Top-K
    │
    ▼
Context Builder
```

第一版不要急着引入太多动态规则。

先固定：

```text
candidate_n
final_k
reranker_model
reranker_revision
max_input_tokens
batch_size
```

然后用同一套 Retrieval Benchmark 做 A/B。

这样我们才能知道：

> 提升到底来自哪里。

---

# 十六、本阶段工程产物：`ProcurementRerankingPolicy_V0.1`

第一版至少记录：

```text
reranker_model_id
reranker_model_revision

reranker_type
=
cross_encoder

candidate_source
=
hybrid_retrieval

candidate_n

final_top_k

query_document_format

max_input_tokens
truncation_policy

batch_size
device
dtype

score_usage
=
ranking_only / thresholded

score_threshold
如果启用

metadata_filter_before_rerank
=
true

version_filter_before_rerank
=
true

benchmark_version
```

同时记录：

```text
before_rerank_mrr
after_rerank_mrr

before_median_gold_rank
after_median_gold_rank

before_hard_negative_above_gold_rate
after_hard_negative_above_gold_rate

p50_rerank_latency
p95_rerank_latency

pairs_per_second
peak_vram
```

这样我们才真正知道：

> **Reranker 带来的排序收益，值不值得它增加的系统成本。**

---

# 十七、把本阶段压成最精准的 5 句话

> **第一，Retriever 负责高 Recall 召回，Reranker 负责把最相关的候选重新排到最前面；两者优化目标不同。**

> **第二，Bi-Encoder 通过独立 Query / Document Vector 实现高效大规模检索，而 Cross-Encoder 让 Query 与候选文本逐 Token 交互，因此更适合细粒度精排，但成本更高。**

> **第三，Reranker 只能重排已经召回的 Candidate Set，不能救回根本没进入候选集的 Gold Evidence；所以调试必须先区分 Recall Failure 和 Rerank Failure。**

> **第四，政府采购 Reranker 的关键价值是压制“投标前 vs 中标后”“准入 vs 履约”这类语义很近但业务边界不同的 Hard Negative。**

> **第五，是否启用 Reranker 必须同时比较 MRR、Gold Rank、Hard Negative 排名改善和新增 Latency / VRAM 成本，而不是只看一个排序分数。**

---

# 本阶段最核心的一张图

```text
                         User Query
                             │
                             ▼
                  Metadata / Validity Filter
                             │
                             ▼
                BM25 + Dense Retrieval
                             │
                             ▼
                       Fusion / RRF
                             │
                             ▼
                    Candidate Top-N
                             │
                             ▼
                  Cross-Encoder Reranker
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
               Gold                Hard Negative
          score应该更高              score应该更低
                 │                       │
                 └───────────┬───────────┘
                             ▼
                      Reranked Top-K
                             │
                             ▼
                       Context Builder
```

脑中最后只留一句：

> **Retriever 的任务是“把正确答案带进考场”，Reranker 的任务是“让正确答案坐到第一排”。**

---

# 第六课 · 第 8 阶段掌握测试

现在不回看正文，你应该能够解释：Retriever 和 Reranker 的职责为什么不同；为什么 Retriever 优先追求 Recall，而 Reranker 更关注 Top-Rank Precision；Bi-Encoder 和 Cross-Encoder 在计算结构上有什么根本差别；为什么 Cross-Encoder 更擅长处理细粒度 Hard Negative；为什么不能直接用 Cross-Encoder 对千万级知识库全量搜索；Candidate N 和 Final K 为什么是两个不同参数；为什么 Reranker 不能救回没有进入 Candidate Set 的 Gold Evidence；Reranker Score 为什么不能自动当成概率；为什么 Hard Negative Above Gold Rate 是政府采购精排的重要指标；为什么 Reranker 的输入长度会反过来约束 Chunking；为什么 Metadata / Version Filter 不应该完全交给 Reranker；以及为什么最终必须同时比较排序收益与 Latency / VRAM 成本。

如果这些能够完整讲出来：

\[
\boxed{
第六课第8阶段真正掌握
}
\]

---

# 下一阶段：第六课 · 第 9 阶段
# Query Rewrite、Metadata Filter 与多路检索
## 用户问得不标准、信息藏在上下文里，Retriever 应该怎样先“理解查询”再去搜？

到第 8 阶段，我们的链路已经变成：

\[
Query
\rightarrow
HybridRetrieval
\rightarrow
Reranker
\rightarrow
TopK
\]

下一阶段要处理的问题是：

> **如果原始 Query 本身就不适合拿去检索怎么办？**

例如用户只说：

```text
“这个要求合法么？”
```

但真正有用的信息其实在前面对话里：

```text
2026年
广东省
政府采购
投标前
本地机构
资格条件
```

下一阶段会正式进入：

```text
Query Rewrite
Query Expansion
Metadata Extraction
Temporal Filter
Jurisdiction Filter
Multi-query Retrieval
Query Routing
```

并形成：

# `ProcurementQueryProcessingPolicy_V0.1`

也就是把 RAG 从：

> “拿用户原句直接搜”

升级成：

> **先把真正的检索意图结构化，再决定搜什么、在哪搜、怎么搜。**

---
