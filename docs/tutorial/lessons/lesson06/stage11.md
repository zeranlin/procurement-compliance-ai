# 第六课 · 第 11 阶段
# 真正搭建 `ProcurementRAG_V0.1`：端到端检索、生成与评测
## 把前 10 个阶段真正接成一个可以运行、可以评测、可以定位错误的政府采购 RAG 系统

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：MEDIUM。** 审计原因：核心心智模型出现偏后，阅读前段缺少认知锚点；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，Fine-tuning 改变模型参数和稳定行为，RAG 改变推理时模型能看到的外部证据；两者是互补关系。**
2. **第二，RAG 的上限首先受知识库质量限制：来源、版本、时间、辖区和有效性如果错，后面的检索越强只会越快找到错误证据。**
3. **第三，Chunking 定义检索单元，Embedding 定义语义空间，Vector Index 定义怎样快速找到候选；三者分别解决不同层的问题。**
4. **第四，Retriever 的目标是高 Recall，Hybrid Retrieval 用 BM25 和 Dense 互补，Reranker 再负责把真正 Gold Evidence 压到前排。**
5. **第五，Query Processing 负责恢复真实检索意图，但不能注入不存在的条件；Metadata Filter 可以显著提升质量，但错误 Hard Filter 会直接杀掉 Gold Evidence。**
6. **第六，Context Assembly 决定哪些证据真正进入 Prompt，Citation 必须形成从 Claim 到 Evidence、Chunk、Document、Source 的可审计映射，证据不足时 Abstention 是正确行为。**
7. **第七，真正的 RAG 不是“LLM + 向量库”四个字，而是一套可以分别评测 Knowledge、Retrieval、Ranking、Context、Generation 和 Citation，并能沿 Trace 定位错误的完整系统。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Query` | Query/Q：当前 Token 表示“我要找什么”的向量 |
| `Rank` | LoRA Rank：低秩增量的容量参数 |
| `Citation` | 引用：把生成结论和具体来源建立可追踪链接 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `Reranker` | 重排器：对初筛候选做更精细相关性排序 |
| `Metadata` | 元数据：项目、来源、时间、地区、版本等辅助信息 |
| `BM25` | BM25：基于词频和逆文档频率的经典词法检索算法 |

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

到第 10 阶段，第六课所有核心零件已经齐了：

```text
Knowledge Base
Chunking
Embedding
Vector Index
Retrieval Benchmark
BM25
Dense Retrieval
Hybrid Retrieval
Reranker
Query Processing
Context Assembly
Citation
Grounded Generation
```

但“零件都有”还不等于：

> **系统已经成立。**

真正的工程问题是：

> **这些模块怎样按固定数据契约接起来，怎样留下可追踪日志，怎样做端到端评测，怎样知道最终提升到底来自哪里？**

所以本阶段不再增加新的核心概念。

我们要做的是：

\[
\boxed{
把第六课前10阶段
组装成
ProcurementRAG\_V0.1
}
\]

这是第六课最终交付物。

---

# 一、先把最终系统边界锁死

`ProcurementRAG_V0.1` 不是一个新的 Base Model。

也不是第六课又训练出一个新的 Adapter。

它是：

\[
\boxed{
ProcurementLM\_V0.1
+
ExternalEvidenceSystem
}
\]

其中：

```text
ProcurementLM_V0.1
负责：
业务判断方式
输出Schema
稳定行为
推理习惯

External Evidence System
负责：
当前知识
证据召回
版本过滤
上下文组装
引用映射
```

因此：

\[
\boxed{
RAGRelease
\neq
ModelWeightsOnly
}
\]

真正发布的是：

> **模型 + 知识资产 + 检索策略 + 上下文策略 + 评测基线 + 版本清单。**

---

# 二、最终端到端链路

现在把整个第六课压成一条完整 Pipeline：

```text
                         Offline Path

Raw Sources
    │
    ▼
Source Verification
    │
    ▼
Knowledge Base
    │
    ▼
Structure-aware Chunking
    │
    ▼
Chunks + Metadata
    │
    ├──────────────► BM25 / Sparse Index
    │
    ▼
Embedding
    │
    ▼
Vector Index


                         Online Path

User Query
    │
    ▼
Query Processing
    │
    ├── Rewrite
    ├── Metadata Extraction
    ├── Temporal / Jurisdiction Filter
    └── Multi-query
    │
    ▼
Hybrid Retrieval
    │
    ├── BM25
    └── Dense Retrieval
    │
    ▼
Fusion / Dedup
    │
    ▼
Reranker
    │
    ▼
Evidence Top-K
    │
    ▼
Context Assembly
    │
    ├── Version Check
    ├── Parent Expansion
    ├── Evidence Selection
    ├── Token Budget
    ├── Ordering
    └── Citation Mapping
    │
    ▼
ProcurementLM_V0.1
    │
    ▼
Grounded Answer
    │
    ▼
Answer + Citations + Trace
```

这就是：

# `ProcurementRAG_V0.1`

---

# 三、真正让系统可维护的关键：模块之间必须有 Data Contract

如果每个模块都只是：

> “传一段字符串给下一个模块。”

系统很快就会失控。

我们至少需要几类稳定对象。

第一类：

# QueryRequest

```json
{
  "query_id": "Q_20260917_0001",
  "user_query": "投标前要求本地机构是否存在风险？",
  "conversation_context": [],
  "query_time": "2026-09-17",
  "user_metadata": {}
}
```

第二类：

# ProcessedQuery

```json
{
  "query_id": "Q_20260917_0001",
  "original_query": "...",
  "rewritten_queries": ["..."],
  "subqueries": [],
  "extracted_metadata": {
    "query_time": "2026-09-17",
    "jurisdiction": "example",
    "procurement_stage": "pre_bid"
  },
  "applied_filters": []
}
```

第三类：

# EvidenceCandidate

```json
{
  "chunk_id": "DOC_001_A12_C01",
  "document_id": "DOC_001",
  "text": "...",
  "metadata": {},
  "sparse_rank": 3,
  "dense_rank": 1,
  "fusion_score": 0.041,
  "rerank_score": 8.7
}
```

第四类：

# ContextEvidence

```json
{
  "evidence_id": "E1",
  "chunk_id": "DOC_001_A12_C01",
  "source": "...",
  "article": "第十二条",
  "version_id": "V3",
  "validity_status": "current",
  "text": "..."
}
```

第五类：

# RAGResponse

```json
{
  "query_id": "Q_20260917_0001",
  "answer": "...",
  "citations": ["E1", "E3"],
  "needs_review": false,
  "trace_id": "TRACE_0001"
}
```

核心思想是：

\[
\boxed{
每个模块
既传内容
也传身份、版本和来源
}
\]

---

# 四、Offline Build 和 Online Query 必须独立版本化

离线知识链可能一个月更新很多次。

在线检索策略也可能频繁调参。

所以最终系统不能只有：

```text
version = 0.1
```

一个字段。

至少要分别记录：

```text
knowledge_base_version
chunk_policy_version
embedding_version
sparse_index_version
vector_index_version
query_processing_version
hybrid_retrieval_version
reranker_version
context_policy_version
grounded_prompt_version
model_version
benchmark_version
```

最终 Release 再引用它们：

```json
{
  "release": "ProcurementRAG_V0.1",
  "model": "ProcurementLM_V0.1",
  "knowledge_base": "KB_V0.1",
  "chunk_policy": "Chunk_V0.1",
  "embedding": "Embed_V0.1",
  "hybrid_retrieval": "Hybrid_V0.1",
  "reranker": "Rerank_V0.1",
  "context_policy": "Context_V0.1",
  "benchmark": "RAGBench_V0.1"
}
```

这样以后答案变化时，

我们能判断：

> 是模型变了，还是知识库变了，还是 Retriever 变了。

---

# 五、先搭一个最小可运行版本，而不是一次把所有优化全开

工程上最危险的做法是：

```text
第一天
同时打开：
Query Rewrite
Multi-query
BM25
Dense
RRF
Reranker
Parent Expansion
Compression
复杂Threshold
动态Routing
```

最后指标变了，

却不知道：

> 到底是谁造成的。

所以第一版建议分层搭建：

```text
V0
Dense Retrieval
+
简单Context

V1
+ Metadata Filter

V2
+ BM25 Hybrid

V3
+ Reranker

V4
+ Query Processing

V5
+ Citation / Grounded Prompt

V6
= ProcurementRAG_V0.1 Candidate
```

每加一层：

> 都跑同一套 Benchmark。

这叫：

# Incremental Integration
## 增量集成

---

# 六、一个最小端到端伪代码应该是什么样？

不绑定具体框架，

核心流程可以写成：

```python
def answer_with_rag(request):
    processed = query_processor.process(request)

    sparse_candidates = sparse_retriever.search(
        processed,
        filters=processed.applied_filters
    )

    dense_candidates = dense_retriever.search(
        processed,
        filters=processed.applied_filters
    )

    candidates = fusion.merge(
        sparse_candidates,
        dense_candidates
    )

    candidates = dedup(candidates)

    reranked = reranker.rank(
        processed.original_query,
        candidates
    )

    context = context_builder.build(
        query=processed,
        candidates=reranked
    )

    answer = procurement_lm.generate(
        query=processed.original_query,
        context=context.prompt_context
    )

    return citation_layer.attach_and_validate(
        answer=answer,
        citation_map=context.citation_map
    )
```

这段代码最重要的不是语法。

而是顺序：

\[
\boxed{
Process
\rightarrow
Retrieve
\rightarrow
Fuse
\rightarrow
Rerank
\rightarrow
Assemble
\rightarrow
Generate
\rightarrow
ValidateCitation
}
\]

---

# 七、Baseline 必须保留：没有对照组，就不知道 RAG 到底有没有价值

第六课最终不能只展示：

> “这是 RAG 的输出。”

必须保留：

# Baseline

也就是：

```text
User Query
↓
ProcurementLM_V0.1
↓
Answer
```

然后和：

```text
User Query
↓
ProcurementRAG_V0.1
↓
Answer + Evidence
```

比较。

两边应该尽量固定：

```text
同一个ProcurementLM_V0.1
同一个System Prompt主体
同一个Generation Config
同一个测试集
同一个输出Schema
```

真正改变的是：

> **有没有 External Evidence System。**

所以：

\[
\boxed{
RAGGain
必须相对Baseline测量
}
\]

---

# 八、端到端 Benchmark 不能只测“答案对不对”

RAG 系统至少有四层质量。

第一层：

# Retrieval Quality

```text
Hit@K
Recall@K
MRR
Gold Rank
Hard Negative Above Gold Rate
```

第二层：

# Context Quality

```text
Gold Evidence Inclusion Rate
Context Precision
Duplicate Rate
Version Correctness
Token Efficiency
```

第三层：

# Generation Quality

```text
业务结论正确性
理由质量
Schema Compliance
needs_review正确性
Unsupported Claim Rate
```

第四层：

# Citation Quality

```text
Citation Precision
Citation Recall
Citation Correctness
Citation Entailment
```

所以：

\[
\boxed{
RAGQuality
\neq
AnswerAccuracyOnly
}
\]

---

# 九、端到端测试集必须覆盖哪些 Slice？

第一版 `ProcurementRAGBench_V0.1` 至少要包含：

| Slice | 主要测什么 |
|---|---|
| Normal | 常规可回答问题 |
| Hard Positive | 需要多条证据才能回答 |
| Hard Negative | 高相似但关键条件不同 |
| Temporal | 历史版本 / 生效时间 |
| Jurisdiction | 国家 / 省 / 市适用范围 |
| Version-sensitive | 新旧规则差异 |
| Identifier-heavy | 文号、金额、条款号 |
| Multi-intent | 一个问题多个子问题 |
| No-answer | 知识库没有充分证据 |
| Conflict | 多来源或多版本冲突 |
| Citation | 结论能否准确回指证据 |
| Injection | 检索文档里含恶意指令 |

只有这样，

系统才不是只会：

> “简单 Query + 单条法规”的演示。

---

# 十、端到端错误必须沿 Trace 反向定位

如果最终答案错了，

不要直接说：

> “RAG 不行。”

应该沿 Trace 检查：

```text
1. Knowledge
正确知识存在吗？

2. Query Processing
Query有没有被改坏？

3. Metadata Filter
Gold有没有被过滤掉？

4. Retrieval
Gold有没有进入Candidate Set？

5. Fusion
Gold有没有被融合策略压下去？

6. Reranker
Hard Negative有没有排到Gold前面？

7. Context
Gold有没有真正进入Prompt？

8. Generation
模型有没有正确使用Gold？

9. Citation
结论有没有引用正确Evidence？
```

因此最终日志必须允许：

\[
\boxed{
Answer
\rightarrow
Trace
\rightarrow
EveryStage
}
\]

这才是真正可调试的 RAG。

---

# 十一、什么日志是必须保存的？

一条线上请求至少应该留下：

```text
trace_id
query_id

original_query
rewritten_queries
subqueries

extracted_metadata
applied_filters

sparse_candidates
dense_candidates
fusion_result

reranker_input
reranker_output

selected_evidence
dropped_evidence
drop_reason

context_token_count
citation_map

model_input_version
model_output

final_citations

latency_by_stage
error_flags
```

注意：

> 日志本身也可能包含敏感采购信息。

所以真实部署时还需要：

```text
权限控制
脱敏
保留周期
审计
访问日志
```

但就 RAG 可观测性而言，

最核心的是：

> **每一步可重放。**

---

# 十二、Latency 也必须拆成阶段，而不是只看总耗时

最终用户只看到：

\[
T_{total}
\]

但工程上应该拆成：

\[
T_{total}
=
T_{query}
+
T_{retrieval}
+
T_{rerank}
+
T_{context}
+
T_{generation}
\]

概念上还可以继续细分：

```text
Query Rewrite
BM25 Search
Dense Search
Fusion
Reranking
Context Build
LLM Prefill
LLM Decode
Citation Validation
```

如果总延迟高，

必须知道：

> 是 Reranker 慢，

还是 LLM Decode 慢。

所以：

\[
\boxed{
EndToEndLatency
必须可分解
}
\]

---

# 十三、No-answer 与 Abstention 是最终系统的正式能力

最终 RAG 不应该被设计成：

> 每个 Query 都必须输出一个确定法律判断。

如果：

```text
知识库没有Gold
或
版本状态不明
或
辖区不清楚
或
证据冲突未解决
```

正确结果可能是：

```text
needs_review = true
```

并说明：

> 当前缺少哪些关键信息。

所以：

\[
\boxed{
ReliableRAG
=
CanAnswer
+
CanAbstain
}
\]

这不是失败。

这是系统边界能力。

---

# 十四、发布前必须做 Ablation：每个复杂模块到底贡献了什么？

我们最终用了：

```text
BM25
Dense
RRF
Reranker
Rewrite
Metadata Filter
Parent Expansion
Grounded Prompt
```

但哪一个真正有效？

需要做：

# Ablation Study
## 消融实验

例如：

```text
Full System

- BM25
- Reranker
- Query Rewrite
- Metadata Filter
- Parent Expansion
```

分别跑 Benchmark。

观察：

```text
Retrieval Recall变化
MRR变化
Groundedness变化
Citation变化
Latency变化
```

这样才能发现：

> 某个模块也许增加 200ms 延迟，却几乎没有带来收益。

所以：

\[
\boxed{
MoreComponents
\neq
BetterSystem
}
\]

---

# 十五、`ProcurementRAG_V0.1` 的 Release Gate 应该是什么？

和第五课一样：

> 训练完成不等于可以发布。

RAG 也需要 Release Gate。

第一版 Gate 可以至少包含：

```text
Retrieval Gate
关键Slice的Hit@K / Recall@K不能低于Baseline

Ranking Gate
Hard Negative Above Gold Rate达到目标

Context Gate
Gold Evidence Inclusion Rate达到目标

Generation Gate
业务判断指标不低于无RAG模型

Citation Gate
关键Claim必须有可验证Citation

Groundedness Gate
Unsupported Claim Rate低于上限

No-answer Gate
无证据问题不能高频强答

Latency Gate
p95端到端延迟在预算内

Regression Gate
通用能力和既有采购能力不能明显退化
```

具体阈值：

> 应由真实 Benchmark 和业务风险共同确定，

而不是在课堂里拍一个固定数字。

---

# 十六、最终 Release Bundle 必须包含什么？

真正的：

# `ProcurementRAG_V0.1`

至少应该包含：

```text
1. ProcurementLM_V0.1
   Adapter / Merged Candidate
   Tokenizer
   Chat Template
   Generation Config

2. Knowledge Base Manifest
   Source List
   Version
   Validity Metadata

3. Chunk Policy
   ProcurementChunkingPolicy_V0.1

4. Embedding Policy
   ProcurementEmbeddingPolicy_V0.1

5. Vector Index Policy
   ProcurementVectorIndexPolicy_V0.1

6. Retrieval Benchmark
   ProcurementRetrievalBenchmark_V0.1

7. Hybrid Retrieval Policy
   ProcurementHybridRetrievalPolicy_V0.1

8. Reranking Policy
   ProcurementRerankingPolicy_V0.1

9. Query Processing Policy
   ProcurementQueryProcessingPolicy_V0.1

10. Context Assembly Policy
    ProcurementContextAssemblyPolicy_V0.1

11. End-to-End Benchmark Report

12. Known Limitations

13. Release Manifest
```

这时我们发布的已经不是：

> “一个模型文件”。

而是：

> **一个完整知识增强系统。**

---

# 十七、最终系统怎样回答一个真实 Query？

假设用户问：

> “按照当前有效规定，采购文件要求供应商投标前已经在本市设立三年以上分支机构，是否存在风险？请给出依据。”

系统内部依次发生：

```text
1.
Query Processing
抽取：
当前时间
本市
投标前
三年以上
分支机构
资格准入

2.
Metadata Filter
限制有效版本和适用范围

3.
BM25
抓取：
“三年以上”
“分支机构”
精确表述

4.
Dense Retrieval
抓取：
本地机构准入限制
经营年限限制
同义表达

5.
Fusion
合并候选

6.
Reranker
把：
投标前准入
排在：
中标后履约
之前

7.
Context Builder
选择：
现行核心规则
经营年限相关规则
必要例外
并分配Evidence ID

8.
ProcurementLM_V0.1
基于Evidence判断

9.
Citation Layer
把结论映射回具体证据
```

最终用户看到的不是：

> “模型觉得有风险。”

而是：

> **判断 + 理由 + 证据 + 来源 + 必要的不确定性说明。**

这就是第六课从第一阶段开始一直追求的目标。

---

# 十八、把第六课 11 个阶段压成一张工程地图

```text
Stage 1
RAG Boundary
Fine-tuning改Weights
RAG改Context

Stage 2
Knowledge Base
知识先可信、可追溯、可版本化

Stage 3
Chunking
定义Retrieval Unit

Stage 4
Embedding
把语义映射到Vector Space

Stage 5
Vector Index
让大规模近邻搜索可扩展

Stage 6
Retrieval Evaluation
用Gold Evidence证明“找没找对”

Stage 7
BM25 + Dense
让Lexical与Semantic互补

Stage 8
Reranker
先高Recall召回，再高Precision精排

Stage 9
Query Processing
先理解检索意图，再决定怎么搜

Stage 10
Context Assembly
把Evidence变成可引用、可控制的Context

Stage 11
End-to-End RAG
把所有模块接成ProcurementRAG_V0.1
```

这 11 个阶段真正构成了一条完整工程闭环。

---

# 十九、把整个第六课压成最精准的 7 句话

> **第一，Fine-tuning 改变模型参数和稳定行为，RAG 改变推理时模型能看到的外部证据；两者是互补关系。**

> **第二，RAG 的上限首先受知识库质量限制：来源、版本、时间、辖区和有效性如果错，后面的检索越强只会越快找到错误证据。**

> **第三，Chunking 定义检索单元，Embedding 定义语义空间，Vector Index 定义怎样快速找到候选；三者分别解决不同层的问题。**

> **第四，Retriever 的目标是高 Recall，Hybrid Retrieval 用 BM25 和 Dense 互补，Reranker 再负责把真正 Gold Evidence 压到前排。**

> **第五，Query Processing 负责恢复真实检索意图，但不能注入不存在的条件；Metadata Filter 可以显著提升质量，但错误 Hard Filter 会直接杀掉 Gold Evidence。**

> **第六，Context Assembly 决定哪些证据真正进入 Prompt，Citation 必须形成从 Claim 到 Evidence、Chunk、Document、Source 的可审计映射，证据不足时 Abstention 是正确行为。**

> **第七，真正的 RAG 不是“LLM + 向量库”四个字，而是一套可以分别评测 Knowledge、Retrieval、Ranking、Context、Generation 和 Citation，并能沿 Trace 定位错误的完整系统。**

---

# 本阶段最核心的一张图

```text
                    ProcurementRAG_V0.1

                           Query
                             │
                             ▼
                    Query Processing
                             │
                             ▼
                     Metadata Filter
                             │
               ┌─────────────┴─────────────┐
               ▼                           ▼
             BM25                    Dense Retrieval
               │                           │
               └─────────────┬─────────────┘
                             ▼
                       Fusion / Dedup
                             │
                             ▼
                          Reranker
                             │
                             ▼
                       Evidence Top-K
                             │
                             ▼
                    Context Assembly
                             │
                     + Citation Map
                             │
                             ▼
                   ProcurementLM_V0.1
                             │
                             ▼
                    Grounded Generation
                             │
                             ▼
                 Answer + Citation + Trace
                             │
                             ▼
                      End-to-End Eval
```

脑中最后只留一句：

> **`ProcurementRAG_V0.1` 不是一个“会搜资料的模型”，而是一套能够把正确知识找到、排好、组织好、交给模型、让结论可追溯，并且能定位每一层错误的完整证据系统。**

---

# 第六课 · 第 11 阶段掌握测试

现在不回看正文，你应该能够解释：为什么 `ProcurementRAG_V0.1` 不是一个新的模型权重文件；为什么 RAG Release 必须包含知识库、检索策略和评测资产；Offline Build 与 Online Query 为什么必须独立版本化；为什么模块之间需要 Data Contract；为什么第一版应该增量集成而不是一次打开全部高级功能；Baseline 为什么必须保留；为什么 RAG Benchmark 不能只看最终答案正确率；为什么 Retrieval、Context、Generation、Citation 必须分别评测；为什么线上请求必须保留 Trace；为什么 Latency 要分阶段统计；为什么 No-answer / Abstention 是正式能力；为什么发布前应该做 Ablation；RAG Release Gate 应该检查哪些层；以及为什么最终交付物必须是一个完整 Release Bundle，而不是一个向量库加一份 Prompt。

如果这些能够完整讲出来：

\[
\boxed{
第六课第11阶段真正掌握
}
\]

---

# 第六课最终交付

到这里，第六课正式完成。

我们已经从：

\[
ProcurementLM\_V0.1
\]

走到了：

\[
\boxed{
ProcurementRAG\_V0.1
}
\]

也就是：

\[
\boxed{
ProcurementLM\_V0.1
+
KnowledgeBase
+
Retrieval
+
Reranking
+
ContextAssembly
+
Citation
}
\]

第五课解决的是：

> **模型怎样稳定地做政府采购任务。**

第六课解决的是：

> **模型怎样拿着当前、可追溯、可更新的外部证据做政府采购任务。**

所以到这里，我们已经拥有了课程中的第二个真正系统级里程碑：

# `ProcurementRAG_V0.1`

第六课：

\[
\boxed{
11/11
\ COMPLETE
}
\]




---
