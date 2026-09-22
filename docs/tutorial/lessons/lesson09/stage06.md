# 第九课 · 第 6 阶段
# RAG Evaluation：Retrieval、Ranking、Context、Generation 分层评测
## RAG 回答错了，到底是没检索到、排错了、上下文组装错了，还是 LLM 没用好证据？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **RAGFailure ≠ LLMFailure。RAG 错误必须分层归因。**
2. **RetrievedContext = LLMVisibleWorld。Retriever 决定模型实际看到的证据世界。**
3. **RetrievalRecall ≠ RankingQuality。找到了和排对了是两个问题。**
4. **RetrievedDocs ≠ FinalContext。Context Builder 还可能丢证据或引入噪声。**
5. **GoodContext ≠ GoodAnswer。上下文正确不代表生成一定正确。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Rank` | LoRA Rank：低秩增量的容量参数 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `Recall` | 召回率：真实风险中被系统成功找出的比例 |
| `Precision` | 精确率：系统报出的风险中真正成立的比例 |
| `Citation` | 引用：把生成结论和具体来源建立可追踪链接 |

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

RAG 系统最终只给用户一个答案。

但内部至少经历：

```text
Query
↓
Retrieval
↓
Ranking
↓
Context Construction
↓
Generation
```

如果最终答错，

不能直接说：

> “LLM 不行。”

所以本阶段第一条边界：

\[
\boxed{
RAGFailure
\neq
LLMFailure
}
\]

本阶段最终形成：

# `ProcurementRAGEvalPolicy_V0.1`

---

# 一、RAG 必须分层评测

完整链路：

\[
\boxed{
Retrieval
\rightarrow
Ranking
\rightarrow
Context
\rightarrow
Generation
}
\]

每一层都可能失败。

所以：

\[
\boxed{
EndToEndFailure
需要
LayerAttribution
}
\]

---

# 二、Retrieval Recall：有没有把正确证据捞上来？

如果 Gold Evidence 已知，

可以看：

# Recall@K
## 前 K 个结果中的召回率

概念上：

\[
Recall@K
=
\frac{
RetrievedRelevant@K
}{
TotalRelevant
}
\]

如果正确证据根本不在 Top-K：

> 后面的 LLM 再强也没用。

所以：

\[
\boxed{
MissingEvidence
是上游硬上限
}
\]

---

# 三、核心心智模型 ①
# `Retriever` 决定 LLM 能看到什么世界

RAG 的 LLM 并不是直接面对整个知识库。

它面对的是：

> Retriever 选出来的一小块世界。

所以：

\[
\boxed{
RetrievedContext
=
LLMVisibleWorld
}
\]

如果可见世界错了，

生成质量上限会直接被限制。

---

# 四、Precision@K：捞上来的东西有多少真的相关？

\[
Precision@K
=
\frac{
RelevantRetrieved@K
}{
K
}
\]

Recall 高但 Precision 很低：

> 大量噪声上下文会挤占 Context。

所以：

\[
\boxed{
MoreRetrieved
\neq
BetterContext
}
\]

---

# 五、MRR：正确答案第一次出现得有多靠前？

# Mean Reciprocal Rank
## 平均倒数排名

如果第一个相关结果排名为：

\[
r
\]

则：

\[
RR=\frac{1}{r}
\]

越靠前越好。

适合：

> 关注第一个关键证据是否足够靠前。

---

# 六、nDCG：多个相关证据有不同价值时怎么办？

# nDCG
## 归一化折损累计增益

适合：

> 相关性有等级、并且排序重要的场景。

例如：

```text
权威法规 = 高相关
地方解读 = 中相关
论坛讨论 = 低相关
```

nDCG 可以同时考虑：

> 相关度和排名位置。

---

# 七、核心心智模型 ②
# `Retrieval` 和 `Ranking` 是两个问题

Retriever 可能：

> 已经把正确文档找到了。

但 Reranker：

> 把它排到很后面。

所以：

\[
\boxed{
RetrievalRecall
\neq
RankingQuality
}
\]

必须分别评。

---

# 八、Context Construction：Top-K 正确也不代表最终 Context 正确

拿到 Top-K 文档后还会发生：

```text
Chunk Merge
Chunk Dedup
Context Truncation
Section Selection
Citation Mapping
```

如果关键段落被：

> 截断、覆盖、重复噪声挤掉，

最终 Context 仍然可能失败。

所以：

\[
\boxed{
RetrievedDocs
\neq
FinalContext
}
\]

---

# 九、Context Recall / Precision

可以定义：

# Context Recall
最终 Context 覆盖了多少 Gold Evidence。

# Context Precision
最终 Context 中有多少内容真正对回答有帮助。

这能区分：

```text
Retriever找到了
但Context Builder丢了
```

和：

```text
Retriever本身没找到
```

---

# 十、核心心智模型 ③
# `ContextBudget` 是有限资源

Context Window 有限。

多塞一个低价值 Chunk，

就可能挤掉一个高价值 Chunk。

所以：

\[
\boxed{
ContextSelection
=
BudgetAllocation
}
\]

这和第八课 Mixture 的思想非常像：

> 有限资源必须优先分配给高价值信息。

---

# 十一、Generation Groundedness：LLM 有没有真正用好 Context？

即使 Context 完全正确，

LLM 仍可能：

```text
忽略关键证据
误读证据
引用错段落
加入外部记忆
过度推断
```

所以要评：

```text
Answer Correctness
Groundedness
Citation Correctness
Evidence Coverage
```

因此：

\[
\boxed{
GoodContext
\neq
GoodAnswer
}
\]

---

# 十二、核心心智模型 ④
# `RAGQuality` 是链路乘积，而不是单点能力

概念上可以理解：

\[
\boxed{
RAGQuality
\approx
Retrieval
\times
Ranking
\times
Context
\times
Generation
}
\]

不是严格数学乘法。

它强调：

> 任一关键环节接近零，整体就会明显受限。

---

# 十三、No-answer 样本为什么必须进 Benchmark？

如果知识库里根本没有答案，

正确行为应该：

> 不回答 / 请求更多证据。

所以 RAG Benchmark 必须包含：

# Unanswerable Items
## 不可回答样本

否则系统可能养成：

> 每题必答。

所以：

\[
\boxed{
CanAnswer
+
CanAbstain
=
ReliableRAG
}
\]

---

# 十四、Gold Evidence 怎么定义？

RAG 评测最好不仅有：

```text
Gold Answer
```

还要有：

```text
Gold Document IDs
Gold Chunk IDs
Gold Evidence Spans
```

这样才能评：

```text
Retrieval
Ranking
Context
Citation
```

所以：

\[
\boxed{
RAGGold
=
AnswerGold
+
EvidenceGold
}
\]

---

# 十五、核心心智模型 ⑤
# `Answer-only Gold` 不足以诊断 RAG

如果只有最终答案，

你无法知道：

> 检索器到底有没有找到正确证据。

因此 RAG Gold 必须更丰富。

---

# 十六、Failure Attribution：一次错误应该归到哪层？

可以定义：

```text
R1 Retrieval Miss
R2 Ranking Failure
R3 Context Drop
R4 Context Noise
R5 Evidence Misuse
R6 Unsupported Generation
R7 Wrong Citation
R8 Failed Abstention
```

然后每个失败样本尽量标：

# Primary Failure
## 主失败原因

以及：

# Secondary Failures
## 次级失败原因

这样才能做真正工程优化。

---

# 十七、Counterfactual Eval：把正确证据给模型，看看它还会不会错

一个非常有价值的诊断方法：

> 直接把 Gold Evidence 放进 Context。

如果此时模型答对：

> 原问题更可能在 Retrieval / Ranking。

如果仍答错：

> 更可能在 Generation / Reasoning。

所以：

\[
\boxed{
OracleContextEval
=
FailureIsolationTool
}
\]

---

# 十八、核心心智模型 ⑥
# `Oracle Context` 可以测 RAG 的“生成上限”

它不是生产配置。

而是诊断实验：

> 如果给模型完美上下文，它最高能做到什么？

这样可以区分：

```text
Retriever瓶颈
vs
Generator瓶颈
```

---

# 十九、RAG 评测还要记录成本和延迟吗？

需要。

因为：

```text
Top-K更大
Reranker更复杂
Context更长
```

可能提升质量，

但也会增加：

```text
Latency
Token Cost
Compute Cost
```

所以 RAG 评测应保留：

```text
quality
latency
cost
```

三个坐标。

---

# 二十、核心心智模型 ⑦
# `BestOfflineQuality` 不一定是 `BestProductionRAG`

生产系统还要考虑：

\[
\boxed{
Quality
+
Latency
+
Cost
}
\]

因此：

\[
\boxed{
RAGSelection
=
MultiObjectiveDecision
}
\]

---

# 二十一、本阶段正式工程产物
# `ProcurementRAGEvalPolicy_V0.1`

至少锁定：

```text
rag_eval_policy_version

gold_answer_required

gold_document_ids

gold_chunk_ids

gold_evidence_spans

retrieval_recall_at_k

precision_at_k

mrr

ndcg

context_recall

context_precision

context_budget

ranking_eval

oracle_context_eval

answer_correctness

groundedness

citation_correctness

citation_completeness

unanswerable_items

abstention_metric

failure_taxonomy

latency_metric

cost_metric

release_gate
```

---

# 二十二、本阶段最重要的 8 个核心心智模型

> **心智模型 ①：`RAGFailure ≠ LLMFailure`。RAG 错误必须分层归因。**

> **心智模型 ②：`RetrievedContext = LLMVisibleWorld`。Retriever 决定模型实际看到的证据世界。**

> **心智模型 ③：`RetrievalRecall ≠ RankingQuality`。找到了和排对了是两个问题。**

> **心智模型 ④：`RetrievedDocs ≠ FinalContext`。Context Builder 还可能丢证据或引入噪声。**

> **心智模型 ⑤：`GoodContext ≠ GoodAnswer`。上下文正确不代表生成一定正确。**

> **心智模型 ⑥：`RAGGold = AnswerGold + EvidenceGold`。只标答案不足以诊断 RAG。**

> **心智模型 ⑦：`OracleContextEval` 是隔离 Retriever 与 Generator 瓶颈的重要工具。**

> **心智模型 ⑧：`BestOfflineQuality ≠ BestProductionRAG`。生产选择必须同时考虑质量、延迟和成本。**

---

# 二十三、下一阶段：第九课 · 第 7 阶段
# Agent Evaluation：Planning、Tool、State、Recovery、Safety、Completion

最关键的边界：

\[
\boxed{
ToolCallSuccess
\neq
TaskCompletion
}
\]

并建立：

# `ProcurementAgentEvalPolicy_V0.1`

---
