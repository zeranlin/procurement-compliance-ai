# 第六课 · 第 9 阶段
# Query Rewrite、Metadata Filter 与多路检索
## 用户问得不标准、信息藏在上下文里，Retriever 应该怎样先“理解查询”再去搜？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，User Query 不一定适合直接检索；Query Processing 的职责是恢复上下文、显式化检索条件和生成必要的检索变体，但绝不能改变用户真实意图。**
2. **第二，Query Expansion 是“同一意图的多种表达”，Query Decomposition 是“把复杂问题拆成多个子意图”，两者不是一回事。**
3. **第三，时间、辖区、版本、文号、金额、条款号、否定词和“投标前 / 中标后”等高风险字段必须被精确保护；不确定 Metadata 应标记 unknown 或请求澄清，而不是自动猜。**
4. **第四，Metadata Filter 可以大幅缩小错误搜索空间，但只有确定条件才适合 Hard Filter；错误过滤比排序错误更危险，因为它会让 Gold Evidence 根本没有机会进入 Candidate Set。**
5. **第五，Query Rewrite、Multi-query、Routing 和 Metadata Filter 是否值得启用，最终都必须回到 ProcurementRetrievalBenchmark_V0.1 做 A/B，并额外监控 Intent Preservation、Identifier Preservation 和 Metadata Extraction Accuracy。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Query` | Query/Q：当前 Token 表示“我要找什么”的向量 |
| `Metadata` | 元数据：项目、来源、时间、地区、版本等辅助信息 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Rank` | LoRA Rank：低秩增量的容量参数 |
| `Reranker` | 重排器：对初筛候选做更精细相关性排序 |
| `Drift` | 漂移：数据、业务、政策或模型行为分布发生变化 |

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

到第 8 阶段，我们的检索链已经变成：

\[
Query
\rightarrow
HybridRetrieval
\rightarrow
Reranker
\rightarrow
TopK
\]

这条链本身已经很强。

但它隐含了一个前提：

> **用户原始 Query 本身已经足够适合检索。**

现实里经常不是这样。

用户可能只说：

```text
“这个要求合法么？”
```

但真正决定检索结果的信息，可能藏在上文：

```text
2026年
广东省
政府采购
投标前
本地机构
资格条件
```

又或者用户会问：

> “那个 17 号文件里关于资格审查的规定现在还有效吗？”

这里同时包含：

```text
“17号文件”
→ 文号识别

“资格审查”
→ 主题

“现在还有效吗”
→ 时间有效性
```

如果把原句原封不动送给 Retriever：

> 很可能检索目标并不完整。

所以今天正式进入：

# Query Processing
## 查询处理

本阶段最终形成：

# `ProcurementQueryProcessingPolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

用户的：

# User Query

不一定等于系统最终拿去搜索的：

# Retrieval Query

两者职责不同。

User Query 是：

> **用户自然表达出来的问题。**

Retrieval Query 是：

> **为了让检索系统更容易找到正确证据而构造的查询表示。**

因此：

\[
\boxed{
UserQuery
\neq
RetrievalQuery
}
\]

但还有一个更重要的限制：

\[
\boxed{
Rewrite
不能改变用户真实意图
}
\]

所以 Query Processing 的目标不是：

> “把问题改成系统喜欢的答案。”

而是：

> **把隐含的检索条件显式化，同时尽量保持原始语义不变。**

---

# 二、Query Rewrite：先把“依赖上下文的问题”改写成可独立检索的问题

假设对话是：

```text
用户：
某省2026年的采购项目要求供应商投标前必须已有本地办事处。

用户：
这个要求合法么？
```

如果只拿最后一句：

```text
这个要求合法么？
```

去检索，

Retriever 几乎不知道：

```text
“这个”指什么
哪个地区
哪个时间
哪类采购
什么条件
```

所以我们需要把它改写成：

```text
2026年某省政府采购项目中，
将“供应商投标前必须已经设立本地办事处”
作为资格条件是否存在合规风险？
```

这就是：

# Conversational Query Rewrite
## 对话查询改写

它的目标是：

> **把指代、上下文、时间、地区和核心业务对象恢复出来。**

---

# 三、Rewrite 不是回答问题

这是一个非常容易出错的地方。

Query Rewrite 模型不能偷偷把：

```text
“这个要求合法么？”
```

改成：

```text
“为什么这个不合法的要求违反政府采购规定？”
```

因为这已经把：

> **待判断问题**

改写成了：

> **预设结论的问题。**

这叫：

# Query Drift
## 查询漂移

所以 Rewrite 必须满足：

\[
\boxed{
PreserveIntent
+
RecoverContext
-
InjectConclusion
}
\]

也就是：

> **补全信息，但不提前替用户下结论。**

---

# 四、哪些信息必须在 Rewrite 时优先保护？

对于政府采购检索，有一些字段属于：

# High-risk Retrieval Tokens
## 高风险检索信息

它们一旦被改错，

整个检索方向就会错。

例如：

```text
数字
金额
日期
文号
条款号
地区
机构名
项目编号
投标前 / 中标后
不得 / 可以
必须 / 建议
```

尤其要保护：

# Negation
## 否定词

例如：

```text
“不得要求”
```

不能改成：

```text
“可以要求”
```

同样：

```text
“投标前”
```

不能被改写成：

```text
“中标后”
```

所以 Query Rewrite 不能只追求：

> “语言更通顺。”

而要追求：

> **检索语义不失真。**

---

# 五、Query Expansion：不只是改写，还可以增加“同义检索表达”

Rewrite 主要解决：

> 原 Query 不完整、不独立。

另一个问题是：

> 同一业务概念有很多表达方式。

例如：

```text
本地办事处
本地分支机构
属地服务机构
当地服务网点
区域性服务机构
```

如果只搜索用户原词：

> 可能漏掉法规里的另一种表达。

所以可以做：

# Query Expansion
## 查询扩展

例如生成多个检索表达：

```text
Q1:
投标前必须设立本地办事处

Q2:
参与采购活动前预先设立本地分支机构

Q3:
将属地服务机构作为供应商准入条件
```

然后分别检索。

这就是：

# Multi-query Retrieval
## 多查询检索

---

# 六、Query Expansion 不能随便扩展精确标识符

假设用户问：

```text
财库〔2026〕17号
```

Query Expansion 绝不能“语义扩展”成：

```text
财库〔2026〕71号
财库〔2025〕17号
```

因为：

> 文号不是近义词。

同样：

```text
100万元
```

也不能自动扩成：

```text
1000万元
```

所以一个非常重要的规则是：

\[
\boxed{
SemanticTerm
可以扩展
}
\]

\[
\boxed{
ExactIdentifier
必须保护
}
\]

Query Processing 必须区分：

```text
可语义扩展的信息
vs
必须精确保留的信息
```

---

# 七、Metadata Extraction：把自然语言里的检索条件抽出来

假设用户问：

> “按照2026年广东省现行政府采购规则，投标前要求供应商设立本地机构是否合适？”

这里其实同时包含：

```text
query_time = 2026
jurisdiction = 广东省
validity = current_at_query_time
domain = 政府采购
topic = 本地机构准入
stage = 投标前
```

这些信息不应该全部只塞在自然语言里。

可以抽成结构化：

```json
{
  "query_time": "2026",
  "jurisdiction": "广东省",
  "domain": "government_procurement",
  "topic": "local_presence_requirement",
  "procurement_stage": "pre_bid",
  "validity_requirement": "valid_at_query_time"
}
```

这就是：

# Metadata Extraction
## 查询元数据抽取

然后把它交给：

# Metadata Filter

---

# 八、Hard Filter 和 Soft Constraint 必须区分

不是所有 Metadata 都应该直接：

> 一刀切过滤。

有些条件非常明确：

```text
query_time = 2024-06-01
```

如果我们知道某文件：

```text
effective_from = 2025-01-01
```

那它显然不应该作为：

> 2024 年问题的有效依据。

这种可以是：

# Hard Filter
## 硬过滤

---

但如果用户只说：

```text
“某省”
```

而系统不确定具体省份，

就不能自己猜：

```text
jurisdiction = 广东省
```

然后把其它地区全部过滤掉。

这种信息不确定时，

应该：

```text
unknown
needs_clarification
or
soft_preference
```

所以：

\[
\boxed{
UncertainMetadata
\neq
HardFilter
}
\]

否则 Query Processing 会在 Retriever 之前：

> **把正确证据提前杀掉。**

---

# 九、Temporal Filter：时间过滤应该怎么理解？

如果用户明确问：

> “2023年当时适用什么规定？”

那么查询目标不是：

\[
LatestDocument
\]

而是：

\[
ValidAt(2023)
\]

假设文档：

```text
V1
effective_from = 2020-01-01
effective_to   = 2024-12-31

V2
effective_from = 2025-01-01
effective_to   = null
```

对于 Query Time：

```text
2023-06-01
```

应该优先保留：

```text
V1
```

而不是 V2。

概念条件可以写成：

\[
effective\_from
\le
query\_time
\]

且：

\[
effective\_to
\text{为空}
\quad
或
\quad
effective\_to
\ge
query\_time
\]

当然真实法律效力判断可能还需要更复杂的业务规则，

但检索层至少要做到：

> **不把明显尚未生效或已经失效的版本当作当前 Gold Candidate。**

---

# 十、Jurisdiction Filter：地区也不能只做字符串匹配

用户可能问：

```text
广东省
```

知识库可能有：

```text
国家级规则
广东省规则
广州市规则
深圳市规则
```

这时：

> 只保留 `jurisdiction = 广东省`

可能又太粗暴。

因为国家级规则：

> 仍然可能适用。

而某市规则是否适用：

> 又要看用户问题具体发生在哪个市。

所以 Jurisdiction 更合理的结构是：

```text
national
province
city
district
special_system
```

并建立：

# Jurisdiction Hierarchy
## 辖区层级

查询时做：

> **适用范围展开，而不是简单字符串等于。**

例如省级 Query 可以考虑：

```text
国家级
+
目标省级
```

是否加入市级：

> 要看 Query 是否明确到了对应城市。

---

# 十一、多路检索不只是“同一个 Query 跑三遍”

真正有价值的 Multi-query Retrieval，

通常是：

> **让不同 Query 负责问题的不同检索面。**

假设用户问：

> “投标前必须有本地办事处，而且要求注册满三年，这两个条件分别有没有风险？”

这其实有两个子问题：

```text
Subquery A
本地机构准入限制

Subquery B
经营年限 / 注册年限准入限制
```

如果把整句话只做一个 Embedding，

可能其中一个主题被另一个主题稀释。

所以可以做：

# Query Decomposition
## 查询分解

形成：

```text
Q1
投标前必须设本地办事处作为资格条件

Q2
要求供应商注册经营满三年作为资格条件
```

分别检索，

再合并证据。

---

# 十二、Query Decomposition 和 Query Expansion 不一样

这两个很容易混。

# Query Expansion

是：

> **一个意图，生成多个表达。**

例如：

```text
本地办事处
≈
本地分支机构
≈
属地服务机构
```

---

# Query Decomposition

是：

> **一个复杂问题，拆成多个子意图。**

例如：

```text
本地机构要求
+
三年经营年限要求
```

所以：

\[
\boxed{
Expansion
=
SameIntent,\ MultipleExpressions
}
\]

\[
\boxed{
Decomposition
=
MultipleSubIntents
}
\]

这两个会产生完全不同的检索结构。

---

# 十三、Query Routing：不是所有 Query 都必须走完全相同的检索路径

如果 Query 是：

```text
“财库〔2026〕17号第十二条”
```

这类精确标识符很强，

BM25 / Exact Match 的价值很大。

如果 Query 是：

```text
“有没有规则禁止把本地办公地点作为投标门槛？”
```

Dense Retrieval 的语义能力非常重要。

如果 Query 同时有：

```text
文号
+
自然语言问题
```

Hybrid 往往更合适。

所以可以引入：

# Query Routing
## 查询路由

概念上：

```text
Identifier-heavy
→ Sparse强权重

Semantic Question
→ Dense强权重

Mixed Query
→ Hybrid

Multi-part Query
→ Decompose + Hybrid
```

但第一版系统不一定要做复杂 Routing。

一个非常稳妥的默认仍然是：

> **Hybrid Retrieval 作为主路径，Routing 只有在 Benchmark 证明有收益时再启用。**

---

# 十四、Multi-query 检索后，结果必须合并并保留“来源查询”

假设我们生成：

```text
Q0
Original Query

Q1
Rewritten Query

Q2
Expanded Query

Q3
Subquery A

Q4
Subquery B
```

每条 Query 都可能召回一批候选。

最终不能只把它们：

> 全部堆在一起。

至少需要：

```text
Dedup
Version Check
Metadata Check
Fusion
Rerank
```

同时应该保留：

# Query Provenance
## 查询来源链

例如：

```json
{
  "chunk_id": "DOC_001_A12_C01",
  "retrieved_by": [
    "original_query",
    "rewrite_1",
    "subquery_A"
  ]
}
```

这样后续分析时我们能知道：

> **到底是哪条查询路径把 Gold Evidence 找回来的。**

这对 Debug 非常有价值。

---

# 十五、为什么 Original Query 最好不要丢？

Rewrite 模型可能犯错。

例如原始 Query：

> “中标后建立本地服务网点是否可以？”

错误 Rewrite：

> “投标前要求本地服务网点是否可以？”

这时如果系统只用 Rewrite：

> 检索方向已经完全变了。

所以一个稳妥策略是：

```text
Original Query
+
Rewritten Query
```

都保留一条检索路径，

然后统一 Fusion / Rerank。

这叫：

# Rewrite Fallback
## 改写回退

因此：

\[
\boxed{
Rewrite
最好是增加检索机会
而不是单点替换原始Query
}
\]

至少第一版系统如此更稳。

---

# 十六、Query Processing 最大的风险：Hallucinated Constraint

LLM 做 Query Rewrite 时，

很容易“补得太聪明”。

原问题：

> “这个条件合理吗？”

上下文只明确：

```text
政府采购
本地服务要求
```

但模型可能自动补成：

```text
广东省
2026年
投标前
资格条件
```

如果这些信息原本根本没有，

这就是：

# Hallucinated Constraint
## 幻觉约束

它比普通语言幻觉更危险。

因为它会直接影响：

```text
Metadata Filter
Query Rewrite
Retriever Candidate Space
```

最终正确证据甚至没有机会出现。

因此 Query Processing 必须遵守：

\[
\boxed{
ExtractKnown
\neq
InventUnknown
}
\]

不确定字段应该明确记录：

```text
null
unknown
needs_clarification
```

而不是自动猜值。

---

# 十七、什么时候应该直接向用户 Clarify，而不是继续自动检索？

假设用户问：

> “这个地方政策现在还能用吗？”

但上下文里没有：

```text
政策名称
地区
时间
文号
```

系统可以做宽检索，

但得到的大量候选可能无法可靠区分。

这种情况下，

最合理的行为可能是：

# Clarification
## 澄清

也就是询问：

> “你指的是哪份政策 / 哪个地区？”

因此 RAG 不应该被设计成：

> **无论信息够不够，都必须立刻给一个检索结果。**

正确系统应该允许：

\[
\boxed{
InsufficientQueryInformation
\rightarrow
Clarify
}
\]

这和第五课、第六课一直强调的：

# `needs_review`

是同一种可靠性思想。

---

# 十八、怎样评测 Query Rewrite 有没有帮助？

不能只看 Rewrite 文本：

> “看起来更专业了。”

要做 A/B。

至少比较：

```text
A
Original Query Only

B
Rewrite Only

C
Original + Rewrite

D
Original + Rewrite + Expansion

E
Decomposition + Multi-query
```

固定：

```text
Knowledge Base
Chunk Policy
Embedding
BM25
Metadata Policy
Reranker
Final Top-K
```

然后比较：

```text
Hit@K
Recall@K
MRR
Hard Negative Above Gold Rate
No-answer False Retrieval Rate
Latency
```

同时增加 Query Processing 自己的指标：

```text
Rewrite Intent Preservation Rate
Metadata Extraction Accuracy
Identifier Preservation Rate
Negation Preservation Rate
Temporal Constraint Accuracy
Jurisdiction Extraction Accuracy
Clarification Accuracy
```

这一步非常关键。

否则 Query Rewrite 很容易：

> 让 Retrieval 指标整体上升一点，但在少量高风险问题上改错关键条件。

---

# 十九、本阶段工程产物：`ProcurementQueryProcessingPolicy_V0.1`

第一版至少记录：

```text
rewrite_enabled
=
true / false

conversation_context_used

preserve_original_query
=
true

query_expansion_enabled

query_decomposition_enabled

max_rewrite_queries
max_subqueries

protected_fields:
  number
  amount
  date
  document_number
  article_number
  jurisdiction
  organization
  negation
  procurement_stage

metadata_fields:
  query_time
  jurisdiction
  document_type
  procurement_stage
  validity_requirement

hard_filter_policy
soft_constraint_policy

unknown_metadata_policy
=
unknown / clarify

query_routing_policy

multi_query_fusion
=
rrf / rerank / other

query_provenance_logging
=
enabled

benchmark_version
```

并且每次线上查询最好记录：

```text
original_query
rewritten_queries
subqueries
extracted_metadata
applied_filters
retrieval_route
candidate_sources
final_evidence
```

这样发生错误时，

我们才能从头重放整个检索过程。

---

# 二十、把本阶段压成最精准的 5 句话

> **第一，User Query 不一定适合直接检索；Query Processing 的职责是恢复上下文、显式化检索条件和生成必要的检索变体，但绝不能改变用户真实意图。**

> **第二，Query Expansion 是“同一意图的多种表达”，Query Decomposition 是“把复杂问题拆成多个子意图”，两者不是一回事。**

> **第三，时间、辖区、版本、文号、金额、条款号、否定词和“投标前 / 中标后”等高风险字段必须被精确保护；不确定 Metadata 应标记 unknown 或请求澄清，而不是自动猜。**

> **第四，Metadata Filter 可以大幅缩小错误搜索空间，但只有确定条件才适合 Hard Filter；错误过滤比排序错误更危险，因为它会让 Gold Evidence 根本没有机会进入 Candidate Set。**

> **第五，Query Rewrite、Multi-query、Routing 和 Metadata Filter 是否值得启用，最终都必须回到 `ProcurementRetrievalBenchmark_V0.1` 做 A/B，并额外监控 Intent Preservation、Identifier Preservation 和 Metadata Extraction Accuracy。**

---

# 本阶段最核心的一张图

```text
                      Conversation
                           │
                           ▼
                     Original Query
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           Rewrite      Metadata     Decompose
              │         Extraction       │
              ▼            │             ▼
        Rewritten Q        │          Subqueries
              │            │             │
              └──────┬─────┴─────┬───────┘
                     ▼           ▼
                Hard / Soft    Query Expansion
                   Filter          │
                     │             │
                     └──────┬──────┘
                            ▼
                    Multi-query Retrieval
                            │
                  ┌─────────┴─────────┐
                  ▼                   ▼
                BM25                Dense
                  │                   │
                  └─────────┬─────────┘
                            ▼
                     Fusion / Dedup
                            │
                            ▼
                         Reranker
                            │
                            ▼
                       Final Evidence
```

脑中最后只留一句：

> **不要急着“搜”；先确认系统到底知道用户在问什么、哪些条件是真的、哪些条件还不知道，然后再决定搜什么、在哪个范围搜、用几条查询去搜。**

---

# 第六课 · 第 9 阶段掌握测试

现在不回看正文，你应该能够解释：为什么 User Query 不等于 Retrieval Query；Query Rewrite 为什么不能提前注入结论；哪些数字、时间、否定词、文号、地区和采购阶段属于必须保护的高风险字段；Query Expansion 和 Query Decomposition 有什么根本区别；为什么 Exact Identifier 不能被语义扩展；Metadata Extraction 为什么应该把时间、辖区和有效性条件结构化；Hard Filter 和 Soft Constraint 应该怎样区分；为什么不确定 Metadata 不能直接拿来过滤；Temporal Filter 为什么要找 `ValidAt(QueryTime)` 而不是永远找最新版本；Jurisdiction 为什么需要层级关系而不是字符串等于；Query Routing 在什么情况下有价值；为什么 Multi-query 结果必须保留 Query Provenance；为什么第一版最好保留 Original Query 作为 Rewrite Fallback；什么是 Hallucinated Constraint；什么时候系统应该 Clarify；以及为什么 Query Processing 本身也必须有独立 Benchmark。

如果这些能够完整讲出来：

\[
\boxed{
第六课第9阶段真正掌握
}
\]

---

# 下一阶段：第六课 · 第 10 阶段
# Context Assembly、Citation 与 Grounded Generation
## 找到正确证据以后，怎样把它们真正交给 LLM，而不是把一堆 Chunk 粗暴塞进 Prompt？

到第 9 阶段，我们已经有：

\[
QueryProcessing
\rightarrow
HybridRetrieval
\rightarrow
Reranker
\rightarrow
EvidenceTopK
\]

下一阶段要解决的是：

> **正确证据已经找到了，怎样排序、去重、压缩、组织、引用，并让 LLM 明确区分“证据支持的事实”和“模型自己的推断”？**

我们会正式进入：

```text
Context Budget
Evidence Selection
Context Ordering
Deduplication
Source Labels
Citation Mapping
Grounded Prompt
Conflict Handling
Insufficient Evidence
```

并建立：

# `ProcurementContextAssemblyPolicy_V0.1`

这一步会把前面 9 个阶段真正接到：

# `ProcurementLM_V0.1`

上。

也就是从：

> **“检索系统找到了正确证据”**

真正走向：

> **“模型基于正确证据回答，而且回答能追溯到证据。”**

---
