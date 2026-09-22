# 第九课 · 第 3 阶段
# Evaluation Schema：到底评什么，不只是 Correct / Wrong
## 一个政府采购 AI 到底应该被拆成哪些能力维度评测？为什么只给最终答案打一个“对 / 错”，无法定位模型、RAG 和 Agent 真正的问题？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **CorrectAnswer ≠ CompleteEvaluation。最终答案正确，不代表过程、证据和系统行为都可靠。**
2. **WhatYouMeasure → WhatYouCanImprove。评测维度决定你能诊断和优化到什么粒度。**
3. **TaskType → EvaluationLogic。分类、检索、生成、Agent 不应该被同一套指标粗暴衡量。**
4. **Outcome ≠ Process。结果对不代表过程可靠，尤其在需要审计的系统里。**
5. **SameErrorRate ≠ SameRiskProfile。错误数量相同，错误结构和严重度可能完全不同。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
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

前两阶段，我们已经解决了两个最底层的问题：

\[
\boxed{
Benchmark
\neq
DatasetOnly
}
\]

以及：

\[
\boxed{
ExpertOpinion
\neq
GroundTruth
}
\]

现在 Gold Set 已经有了相对可信的“标准答案”。

但马上会出现第三个问题：

> **到底拿这些 Gold 样本评什么？**

假设系统最终给出一个结论：

```text
风险类型：地域限制
结论：存在风险
理由：要求供应商在本地设立服务机构
```

如果最终标签和 Gold 一样，我们能不能直接说：

> “这个样本评测通过”？

不一定。

因为系统可能：

```text
结论碰巧对了
但证据引用错了

结论对了
但理由是编的

结论对了
但RAG检索到了错误政策

结论对了
但Agent调用了错误工具

结论对了
但遇到信息不足时本应该拒答
```

所以本阶段最重要的边界是：

\[
\boxed{
CorrectAnswer
\neq
CompleteEvaluation
}
\]

本阶段最终形成：

# `ProcurementEvaluationSchema_V0.1`

---

# 一、Evaluation Schema 到底是什么？

# Evaluation Schema
## 评测结构

它回答的不是：

> “用什么 Metric？”

而是更前一层：

> **一个样本到底要从哪些维度被判定。**

可以把它表示成：

\[
\boxed{
EvaluationSchema
=
EvaluationUnit
+
CapabilityDimensions
+
Outcome
+
Process
+
Evidence
+
ErrorTaxonomy
+
Severity
}
\]

中文就是：

> 先定义评测单元，再定义能力维度、最终结果、过程、证据、错误类型和错误严重度。

所以：

\[
\boxed{
Metric
是Schema的一部分
不是Schema本身
}
\]

---

# 二、核心心智模型 ①
# `WhatYouMeasure` 决定 `WhatYouCanImprove`

如果 Benchmark 只记录：

```text
final_correct = true / false
```

那么系统失败时你只能知道：

> “错了。”

却不知道：

```text
Retriever没找到？
Reranker排错？
LLM理解错？
证据引用错？
Agent工具选错？
格式错？
该拒答却没拒答？
```

所以：

\[
\boxed{
CoarseEvaluation
\Rightarrow
CoarseDiagnosis
}
\]

评测 Schema 越粗，

你能做的工程诊断就越粗。

---

# 三、第一步：定义 Evaluation Unit

# Evaluation Unit
## 评测单元

到底“一条评测样本”是什么？

可以是：

```text
一个分类样本
一个问题
一段采购条款
一份完整文档
一次RAG问答
一次Agent任务
一个完整采购工作流
```

这些不是同一种 Evaluation Unit。

例如：

### Item-level
样本级

评：

> 单条输入输出。

### Document-level
文档级

评：

> 一份完整采购文件的理解。

### Session-level
会话级

评：

> 多轮交互是否保持状态。

### Task-level
任务级

评：

> Agent 是否最终完成真实目标。

所以：

\[
\boxed{
EvaluationUnit
决定
MetricMeaning
}
\]

如果 Unit 定义不清，

不同指标会混在一起。

---

# 四、Task Taxonomy：先把任务类型分清

政府采购 AI 至少可能包含：

```text
Classification
分类

Extraction
信息抽取

Retrieval
检索

Ranking
排序

Question Answering
问答

Summarization
摘要

Risk Analysis
风险分析

Citation
引用

Tool Calling
工具调用

Workflow Completion
工作流完成
```

每类任务的“正确”都不同。

例如：

> Classification 可以有明确标签。

但：

> Generation 往往不是唯一正确文本。

所以：

\[
\boxed{
OneMetric
不能覆盖
AllTaskTypes
}
\]

---

# 五、核心心智模型 ②
# `TaskType` 决定 `EvaluationLogic`

分类任务：

> 更适合 Confusion Matrix、Precision、Recall、F1。

检索任务：

> 更适合 Recall@K、MRR、nDCG。

生成任务：

> 更适合事实性、Groundedness、完整性、引用质量等 Rubric。

Agent：

> 更关心 Task Completion、Tool Correctness、Recovery、Safety。

所以：

\[
\boxed{
MetricChoice
必须由
TaskSemantics
驱动
}
\]

不是哪个 Metric 流行就用哪个。

---

# 六、Capability Dimension：不要把所有能力混成一个分数

# Capability Dimension
## 能力维度

对政府采购系统，可以拆成：

```text
Domain Understanding
领域理解

Factual Correctness
事实正确性

Risk Recognition
风险识别

Evidence Grounding
证据支撑

Citation Correctness
引用正确性

Instruction Following
指令遵循

Structured Output
结构化输出

Abstention
拒答与不确定性

Retrieval Quality
检索质量

Tool Use
工具使用

Task Completion
任务完成

Safety / Policy Compliance
安全与策略遵循
```

于是一个样本可能：

```text
结论正确 = 1
证据正确 = 0
引用正确 = 0
格式正确 = 1
```

这比：

```text
overall = 1
```

信息量高得多。

---

# 七、Outcome Metric 和 Process Metric 必须分开

# Outcome Metric
## 结果指标

回答：

> 最终结果对不对？

例如：

```text
最终风险类型是否正确
最终答案是否正确
任务是否完成
```

# Process Metric
## 过程指标

回答：

> 系统是怎样得到这个结果的？

例如：

```text
是否检索到正确证据
是否调用正确工具
是否使用了正确参数
是否进行了必要复核
```

所以：

\[
\boxed{
Outcome
\neq
Process
}
\]

---

# 八、核心心智模型 ③
# `RightAnswerForWrongReason` 仍然是系统风险

如果系统：

> 通过错误证据碰巧给出正确结论，

今天可能得分。

但换一个样本：

> 很可能崩。

所以：

\[
\boxed{
CorrectOutcome
+
InvalidProcess
\neq
ReliableSystem
}
\]

特别是政府采购这类需要：

```text
可解释
可审计
可追溯
```

的场景，

过程质量不能被忽略。

---

# 九、Evidence Quality：证据本身也要评

对于有 RAG 或引用的系统，

不能只看：

> “有没有引用。”

还要分：

```text
Evidence Relevance
证据是否相关

Evidence Sufficiency
证据是否足够

Evidence Correctness
证据是否支持结论

Evidence Coverage
关键结论是否都有证据
```

所以：

\[
\boxed{
CitationPresent
\neq
EvidenceValid
}
\]

有引用，

不代表引用真的支持答案。

---

# 十、Error Taxonomy：错误分类体系为什么重要？

假设 100 个失败样本。

如果只记：

```text
wrong = 100
```

价值很低。

更专业的做法是：

# Error Taxonomy
## 错误分类体系

例如：

```text
E1 Domain Misunderstanding
领域理解错误

E2 Retrieval Miss
检索漏召回

E3 Ranking Error
排序错误

E4 Unsupported Claim
无证据断言

E5 Wrong Citation
错误引用

E6 Instruction Violation
指令违反

E7 Schema Error
结构输出错误

E8 Overclaim
过度确定

E9 Failed Abstention
该拒答未拒答

E10 Tool Error
工具调用错误

E11 State Error
状态管理错误

E12 Completion Failure
任务未完成
```

这样才能回答：

> 新模型到底把哪类错误减少了？

---

# 十一、核心心智模型 ④
# `ErrorCount` 不如 `ErrorStructure` 有价值

两个系统都错 100 条：

```text
系统A：
90条格式错
10条事实错

系统B：
10条格式错
90条事实错
```

这两个系统风险完全不同。

所以：

\[
\boxed{
SameErrorRate
\neq
SameRiskProfile
}
\]

评测必须理解：

> 错误结构。

---

# 十二、Severity：错误严重度必须进入 Schema

同样是一个错误：

```text
少一个标点
```

和：

```text
把高风险限制条款判断成无风险
```

不能同等对待。

所以需要：

# Severity
## 错误严重度

例如：

```text
S0 Cosmetic
展示问题

S1 Minor
轻微错误

S2 Material
影响业务判断

S3 Critical
可能导致重大决策风险
```

于是：

\[
\boxed{
ErrorProbability
\neq
ErrorCost
}
\]

这为后面：

> 风险加权、Release Gate

打基础。

---

# 十三、Partial Credit：生成任务为什么不能只有 0 / 1？

一段回答可能：

```text
结论正确
理由部分正确
证据不完整
格式完全正确
```

如果直接：

```text
score = 0
```

会丢失信息。

如果：

```text
score = 1
```

又过于乐观。

所以可以采用：

# Partial Credit
## 部分得分

例如：

| 维度 | 分数 |
|---|---:|
| 结论正确 | 1.0 |
| 理由完整 | 0.7 |
| 证据充分 | 0.5 |
| 引用正确 | 1.0 |
| 格式遵循 | 1.0 |

但需要注意：

\[
\boxed{
PartialCredit
必须有Rubric
}
\]

不能靠评测者随意感觉。

---

# 十四、核心心智模型 ⑤
# `PartialCredit` 的价值在诊断，不在制造漂亮小数

如果最终只是算：

```text
0.83
```

但不知道 0.83 来自哪里，

意义仍然有限。

更重要的是：

> 每个维度为什么得这个分。

所以：

\[
\boxed{
DecomposedScore
>
OpaqueScore
}
\]

这里的 `>` 表示：

> 工程诊断价值更高。

---

# 十五、Composite Score：能不能把所有东西合成一个总分？

可以，

但必须谨慎。

# Composite Score
## 复合指标

可以概念化：

\[
S
=
\sum_i w_i s_i
\]

其中：

\[
w_i
=
第i个能力维度权重
\]

\[
s_i
=
该维度得分
\]

但风险是：

> 高分维度可以把关键失败“平均掉”。

例如：

```text
格式 100
语言 95
事实 60
安全 40
```

如果直接平均，

总分仍可能看起来不错。

所以：

\[
\boxed{
CompositeScore
不能替代
CriticalGate
}
\]

---

# 十六、核心心智模型 ⑥
# `WeightedAverage` 不能把 Critical Failure 洗掉

对关键能力应该设置：

# Hard Gate
## 硬门槛

例如：

```text
Critical Risk Recall >= threshold

Citation Correctness >= threshold

Failed Abstention <= threshold
```

即使综合分很高，

只要关键门槛没过：

\[
\boxed{
ReleaseGate=False
}
\]

这比单一总分安全得多。

---

# 十七、Evaluation Record：每次评测到底要保存什么？

建议每个样本记录：

```text
benchmark_item_id

task_type

input

gold_output

gold_evidence

model_output

retrieved_context

tool_trace

outcome_score

process_score

evidence_score

error_codes

severity

slice_tags

judge_version

metric_version

evaluation_timestamp
```

这样评测不是一张最终分数表。

而是：

# Evaluation Trace
## 评测追踪记录

---

# 十八、Judge 到底是谁？

不同任务可能使用：

```text
Exact Matcher
精确规则

Programmatic Scorer
程序评分器

Domain Expert
领域专家

LLM-as-a-Judge
大模型裁判

Hybrid Judge
混合裁判
```

所以 Evaluation Schema 还必须明确：

# Judge Type
## 裁判类型

因为：

\[
\boxed{
Score
依赖
Judge
}
\]

如果 Judge 变了，

分数也可能变。

---

# 十九、核心心智模型 ⑦
# `JudgeVersion` 也是 Benchmark Protocol 的一部分

如果使用 LLM-as-a-Judge，

至少要版本化：

```text
judge_model

judge_prompt

judge_temperature

rubric_version
```

否则：

> 同一个模型输出，换了 Judge，分数可能变。

所以：

\[
\boxed{
JudgeChange
=
ProtocolChange
}
\]

---

# 二十、Evaluation Schema 应该支持 Model、RAG、Agent 共用吗？

应该：

> 共用顶层框架，但允许任务专属字段。

可以设计：

```text
Common Layer
通用层

+
Task-specific Layer
任务专属层
```

Common Layer：

```text
correctness
severity
evidence
slice
error_type
```

RAG Layer：

```text
retrieval_recall
ranking
context_quality
```

Agent Layer：

```text
tool_selection
tool_args
state
recovery
completion
```

这样：

\[
\boxed{
SharedSchema
+
TaskSpecificSchema
}
\]

既能统一，

又不会强行一刀切。

---

# 二十一、Evaluation Schema 的版本也必须冻结

例如：

```text
ProcurementEvaluationSchema_V1.0
```

以后发现：

> 需要新增“Abstention Quality”。

应该：

```text
ProcurementEvaluationSchema_V1.1
```

而不是直接改旧字段。

因为：

\[
\boxed{
SchemaChange
可能改变
HistoricalScoreMeaning
}
\]

---

# 二十二、本阶段正式工程产物
# `ProcurementEvaluationSchema_V0.1`

第一版至少锁定：

```text
evaluation_schema_version

evaluation_unit

task_taxonomy

capability_dimensions

outcome_metrics

process_metrics

evidence_metrics

error_taxonomy

severity_levels

partial_credit_policy

composite_score_policy

critical_gate_policy

judge_type

judge_version

task_specific_fields

slice_fields

evaluation_trace_schema

schema_versioning_policy
```

每个 Evaluation Item 至少记录：

```text
item_id

task_type

gold_reference

gold_evidence

system_output

system_trace

dimension_scores

error_codes

severity

slice_tags

judge_metadata

final_status
```

---

# 二十三、本阶段最重要的 9 个核心心智模型

> **心智模型 ①：`CorrectAnswer ≠ CompleteEvaluation`。最终答案正确，不代表过程、证据和系统行为都可靠。**

> **心智模型 ②：`WhatYouMeasure → WhatYouCanImprove`。评测维度决定你能诊断和优化到什么粒度。**

> **心智模型 ③：`TaskType → EvaluationLogic`。分类、检索、生成、Agent 不应该被同一套指标粗暴衡量。**

> **心智模型 ④：`Outcome ≠ Process`。结果对不代表过程可靠，尤其在需要审计的系统里。**

> **心智模型 ⑤：`SameErrorRate ≠ SameRiskProfile`。错误数量相同，错误结构和严重度可能完全不同。**

> **心智模型 ⑥：`PartialCredit` 必须基于 Rubric。部分得分是诊断工具，不是随意打小数。**

> **心智模型 ⑦：`CompositeScore ≠ ReleaseGate`。综合分不能掩盖关键能力失败。**

> **心智模型 ⑧：`JudgeVersion` 属于 Benchmark Protocol。换裁判就等于改变评测协议。**

> **心智模型 ⑨：`SharedSchema + TaskSpecificSchema`。统一评测框架和任务专属维度必须同时存在。**

---

# 二十四、把 Evaluation Schema 压成一张专业工程图

```text
                         Benchmark Item
                           Gold样本
                              │
                              ▼
                       Evaluation Unit
                         定义评测单元
                              │
                              ▼
                         Task Taxonomy
                           识别任务类型
                              │
                              ▼
                    Capability Dimensions
                       拆分能力维度
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
            Outcome         Process        Evidence
             结果            过程            证据
               │              │              │
               └──────────────┼──────────────┘
                              ▼
                        Error Taxonomy
                         错误类型归因
                              │
                              ▼
                           Severity
                          错误严重度
                              │
                              ▼
                     Partial / Exact Score
                         分维度评分
                              │
                              ▼
                        Critical Gates
                         关键能力门槛
                              │
                              ▼
                       Evaluation Trace
                         评测记录
```

脑中最后只留一句：

> **Evaluation Schema 的本质不是“给模型打多少分”，而是把一次系统输出拆成结果、过程、证据、错误类型和严重度，使我们既能公平比较版本，又能知道系统到底为什么成功、为什么失败。**

---

# 第九课 · 第 3 阶段掌握测试

现在不回看正文，你应该能够解释：为什么 Correct Answer 不等于 Complete Evaluation；Evaluation Unit 为什么会改变指标含义；Task Taxonomy 为什么必须先于 Metric；Outcome Metric 和 Process Metric 有什么区别；为什么 Right Answer for Wrong Reason 仍然是系统风险；Evidence Quality 应该拆成哪些维度；Error Taxonomy 为什么比单纯 Error Count 更有价值；Severity 为什么必须进入 Schema；Partial Credit 为什么需要 Rubric；Composite Score 为什么不能替代 Critical Gate；Judge 为什么也要版本化；为什么 RAG、Agent 需要 Task-specific Schema；以及为什么 Evaluation Schema 本身也必须版本化。

如果这些能够完整讲出来：

\[
\boxed{
第九课第3阶段真正掌握
}
\]

---

# 下一阶段：第九课 · 第 4 阶段
# Classification Metrics：Precision、Recall、F1、PR-AUC 与业务代价
## 为什么采购风险识别不能只看 Accuracy？False Negative 和 False Positive 在业务上到底谁更贵？

下一阶段最关键的边界：

\[
\boxed{
Accuracy
\neq
RiskQuality
}
\]

并建立：

# `ProcurementClassificationMetricPolicy_V0.1`

---
