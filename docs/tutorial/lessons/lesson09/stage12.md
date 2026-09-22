# 第九课 · 第 12 阶段
# 真正搭建 `ProcurementBench_V1`：端到端评测与 Release Gate
## 怎样把 Gold、Metrics、RAG、Agent、Slice、Calibration、Firewall、Regression 全部接成一套真正能决定“能不能上线”的质量系统？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Benchmark ≠ DatasetOnly。评测基准是数据、协议、指标和治理的组合。**
2. **ExpertOpinion ≠ GroundTruth。Gold 的权威来自受控流程，不来自单一专家身份。**
3. **CorrectAnswer ≠ CompleteEvaluation。结果、过程、证据和错误严重度都需要评。**
4. **Accuracy ≠ RiskQuality。分类指标必须和真实业务错误成本绑定。**
5. **FluentAnswer ≠ CorrectAnswer。生成质量必须拆事实、证据、引用和拒答。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Regression` | 回归测试：更新后验证旧能力和关键切片没有退化 |
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `Calibration` | 校准：使模型置信度更接近实际正确率 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |

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

前 11 个阶段，我们已经分别建立：

```text
Benchmark Boundary
Gold Set
Evaluation Schema
Classification Metrics
Generation Evaluation
RAG Evaluation
Agent Evaluation
Slice Evaluation
Calibration / Abstention / OOD
Benchmark Firewall
Regression Testing
```

第 12 阶段不再增加孤立概念。

它要把所有东西接成：

# `ProcurementBench_V1`

也就是：

> **政府采购 AI 的长期质量裁判系统。**

本阶段第一条总边界：

\[
\boxed{
BenchmarkRun
\neq
ReleaseDecision
}
\]

跑完一遍 Benchmark，

只代表：

> 得到一组评测证据。

真正是否发布，

还需要：

> Release Gate。

---

# 一、`ProcurementBench_V1` 到底是什么？

它不是：

```text
一个CSV
一个Excel
一个F1脚本
```

而是：

\[
\boxed{
ProcurementBench\_V1
=
GoldData
+
EvaluationSchema
+
Metrics
+
Slices
+
Calibration
+
Firewall
+
Regression
+
Governance
+
ReleaseGate
}
\]

所以：

\[
\boxed{
BenchmarkSystem
\neq
BenchmarkFile
}
\]

---

# 二、核心心智模型 ①
# `Benchmark` 是质量基础设施，不是一次考试

真正成熟以后，

每个模型、RAG、Agent 版本都应该经过：

```text
统一Benchmark
统一Protocol
统一Trace
统一Regression
统一ReleaseGate
```

所以 ProcurementBench 是：

# Quality Infrastructure
## 质量基础设施

---

# 三、完整端到端流程

```text
Define Evaluation Objectives
↓
Build Candidate Pool
↓
Benchmark Firewall
↓
Gold Annotation
↓
Adjudication
↓
Freeze Gold
↓
Evaluation Schema
↓
Task-specific Metrics
↓
Slice Registry
↓
Hidden / OOD Sets
↓
Run Model / RAG / Agent Eval
↓
Calibration & Risk-Coverage
↓
Regression Comparison
↓
Release Gate
↓
Release Report
↓
Versioned Benchmark Maintenance
```

这条链必须：

> 可复现、可审计、可版本化。

---

# 四、Benchmark Artifact Tree

第一版可以组织为：

```text
ProcurementBench_V1/

├── gold/
│   ├── items
│   ├── labels
│   ├── evidence
│   └── adjudication
│
├── schema/
│   ├── annotation_schema
│   ├── evaluation_schema
│   └── error_taxonomy
│
├── metrics/
│   ├── classification
│   ├── generation
│   ├── rag
│   ├── agent
│   └── calibration
│
├── slices/
│   ├── registry
│   ├── critical_slices
│   └── hard_cases
│
├── firewall/
│   ├── contamination_checks
│   ├── hidden_test
│   └── access_policy
│
├── regression/
│   ├── champion
│   ├── challenger
│   └── history
│
├── runs/
│   └── benchmark_run_manifest
│
└── release/
    ├── release_gate
    └── release_report
```

---

# 五、核心心智模型 ②
# `BenchmarkVersion = Data + Protocol + Schema + Metrics`

如果只改：

```text
Gold Data
```

是版本变化。

如果只改：

```text
Judge Prompt
Metric Definition
Slice Definition
```

同样是版本变化。

所以：

\[
\boxed{
BenchmarkVersion
\neq
DatasetVersionOnly
}
\]

---

# 六、Benchmark Run Manifest

每次 Run 至少记录：

```text
benchmark_run_id

benchmark_version

model_version

rag_version

agent_version

prompt_version

threshold_version

judge_version

metric_version

slice_registry_version

retrieval_index_version

timestamp

environment

results

release_gate_status
```

这样以后看到：

```text
Score = 84.7
```

才能知道：

> 它到底是怎么跑出来的。

---

# 七、核心心智模型 ③
# `ScoreWithoutRunManifest = WeakEvidence`

没有上下文的分数，

不能成为可靠发布证据。

---

# 八、统一 Scorecard 应该长什么样？

可以分：

### Foundation
```text
Domain Understanding
Long Context
Terminology
```

### Classification
```text
Precision
Recall
F1
PR-AUC
Critical FN
```

### Generation
```text
Factuality
Groundedness
Citation
Completeness
```

### RAG
```text
Recall@K
MRR
Context Recall
Groundedness
```

### Agent
```text
Task Completion
Tool Correctness
Recovery
Safety
```

### Reliability
```text
Calibration
Abstention
OOD
Risk-Coverage
```

### Regression
```text
Critical Delta
Worst Slice
Historical Trend
```

---

# 九、核心心智模型 ④
# `OneScore` 只能做导航，不能代替多维证据

可以有一个：

```text
Overall Score
```

用于快速导航。

但真正 Release 决策必须看：

```text
Dimension
Slice
Critical Gate
Regression
```

所以：

\[
\boxed{
OverallScore
=
Dashboard
\neq
Decision
}
\]

---

# 十、Release Gate 怎样设计？

可以概念化：

\[
ReleaseGate
=
G_{gold}
\land
G_{classification}
\land
G_{generation}
\land
G_{rag}
\land
G_{agent}
\land
G_{slice}
\land
G_{calibration}
\land
G_{regression}
\land
G_{firewall}
\]

全部为 True：

\[
\boxed{
ReleaseGate=True
}
\]

才允许：

> 发布候选系统晋级。

---

# 十一、关键门槛必须训练前定义

不能模型跑完后：

> 看哪个指标好就说哪个重要。

所以：

\[
\boxed{
PredefinedGate
>
PostHocNarrative
}
\]

这里的 `>` 表示：

> 决策可信度更高。

---

# 十二、核心心智模型 ⑤
# `Benchmark` 的价值在“阻止错误发布”，不只是证明模型很强

一个好 Benchmark 不只是：

> 给好模型发奖状。

更重要的是：

> 在高风险回归时把 Release 挡住。

所以：

\[
\boxed{
Benchmark
=
PromotionEvidence
+
ReleaseBrake
}
\]

---

# 十三、Champion / Challenger 工作流

```text
Champion
当前稳定系统

↓

Challenger
候选新系统

↓

Same Benchmark
同一基准

↓

Paired Eval
配对评测

↓

Regression Check
回归检查

↓

Release Gate
发布门槛

↓

Promote / Reject
晋级或否决
```

这会成为后面 MLOps 的核心流程。

---

# 十四、Benchmark 自身也需要 Quality Gate

谁来评 Benchmark？

至少要检查：

```text
Gold Agreement
Gold Evidence Completeness
Slice Coverage
Critical Slice Support
Contamination Status
Protocol Completeness
Metric Reproducibility
Access Governance
```

所以：

\[
\boxed{
BenchmarkQuality
也需要BenchmarkGovernance
}
\]

---

# 十五、核心心智模型 ⑥
# `BadBenchmark` 会让好模型看起来坏，也会让坏模型看起来好

所以：

\[
\boxed{
EvaluationError
也是
SystemRisk
}
\]

评测本身不能被当作绝对无误。

---

# 十六、人工评测和自动评测怎样组合？

自动：

```text
快
便宜
可重复
```

人工：

```text
贵
慢
但能处理复杂语义
```

所以推荐：

# Hybrid Evaluation
## 混合评测

例如：

```text
Programmatic Metrics
↓
LLM Judge
↓
Human Audit
↓
Expert Adjudication for Critical Cases
```

不同风险层级：

> 不同评测成本。

---

# 十七、核心心智模型 ⑦
# `EvaluationCost` 也要按风险分配

不要所有样本都人工，

也不要所有样本都自动。

可以：

```text
Low Risk
自动评

Medium Risk
LLM Judge + 抽检

High Risk
专家复核
```

所以：

\[
\boxed{
EvaluationBudget
=
RiskWeightedAllocation
}
\]

---

# 十八、Benchmark 运行以后输出什么？

至少输出：

```text
Executive Summary
总体摘要

Dimension Scorecard
能力维度

Critical Slice Report
关键切片

Regression Matrix
回归矩阵

Calibration / Coverage
校准与覆盖

Contamination Status
污染状态

Critical Failures
严重失败

Release Decision
发布结论
```

这才是完整：

# Evaluation Bundle
## 评测证据包

---

# 十九、Release Report 必须能回答哪些问题？

至少：

```text
新版本为什么更好？

哪里没有变？

哪里变差？

关键场景是否安全？

哪些问题仍然未知？

Benchmark是否干净？

是否有统计不确定性？

成本是否变化？

最终为什么Pass / Fail？
```

---

# 二十、核心心智模型 ⑧
# `Unknown` 必须被写进评测报告

Benchmark 永远不可能覆盖：

> 所有未来场景。

所以专业报告要明确：

```text
Known Strengths
Known Weaknesses
Known Unknowns
Coverage Gaps
```

而不是：

> “通过 Benchmark = 全面安全。”

所以：

\[
\boxed{
BenchmarkPass
\neq
UniversalGuarantee
}
\]

---

# 二十一、`ProcurementBench_V1` 的版本规则

建议：

```text
V1.0.0
首个冻结版

V1.0.1
标签/实现修复，不改变大范围能力定义

V1.1.0
新增Slice / 任务 / 覆盖

V2.0.0
评测体系重大改变
```

具体版本规则可以根据团队调整。

关键是：

> 变化必须显式。

---

# 二十二、本课 12 个阶段的工程产物怎样接起来？

第 1 阶段：

```text
ProcurementBenchmarkBoundaryPolicy_V0.1
```

回答：

> Benchmark 和 Validation / Test 的边界是什么？

第 2 阶段：

```text
ProcurementGoldSetPolicy_V0.1
```

回答：

> Gold Label 怎么产生？

第 3 阶段：

```text
ProcurementEvaluationSchema_V0.1
```

回答：

> 到底评哪些维度？

第 4 阶段：

```text
ProcurementClassificationMetricPolicy_V0.1
```

回答：

> 分类任务怎样量化？

第 5 阶段：

```text
ProcurementGenerationEvalPolicy_V0.1
```

回答：

> 开放式生成怎样评？

第 6 阶段：

```text
ProcurementRAGEvalPolicy_V0.1
```

回答：

> RAG 错在哪一层？

第 7 阶段：

```text
ProcurementAgentEvalPolicy_V0.1
```

回答：

> Agent 是否真正、安全完成任务？

第 8 阶段：

```text
ProcurementSliceEvalPolicy_V0.1
```

回答：

> 哪些关键场景被平均分掩盖？

第 9 阶段：

```text
ProcurementCalibrationAbstentionPolicy_V0.1
```

回答：

> 模型什么时候应该回答、什么时候应该拒答？

第 10 阶段：

```text
ProcurementBenchmarkFirewallPolicy_V0.1
```

回答：

> 如何保护测试独立性？

第 11 阶段：

```text
ProcurementRegressionPolicy_V0.1
```

回答：

> 新版本哪里进步、哪里退化？

第 12 阶段：

```text
ProcurementBench_V1
```

回答：

> 怎样用统一证据决定是否发布？

---

# 二十三、第九课最终 12 条核心心智模型

> **心智模型 ①：`Benchmark ≠ DatasetOnly`。评测基准是数据、协议、指标和治理的组合。**

> **心智模型 ②：`ExpertOpinion ≠ GroundTruth`。Gold 的权威来自受控流程，不来自单一专家身份。**

> **心智模型 ③：`CorrectAnswer ≠ CompleteEvaluation`。结果、过程、证据和错误严重度都需要评。**

> **心智模型 ④：`Accuracy ≠ RiskQuality`。分类指标必须和真实业务错误成本绑定。**

> **心智模型 ⑤：`FluentAnswer ≠ CorrectAnswer`。生成质量必须拆事实、证据、引用和拒答。**

> **心智模型 ⑥：`RAGFailure ≠ LLMFailure`。RAG 必须分层归因到 Retrieval、Ranking、Context、Generation。**

> **心智模型 ⑦：`ToolCallSuccess ≠ TaskCompletion`。Agent 要同时评结果、轨迹、安全和恢复。**

> **心智模型 ⑧：`OverallScore ≠ SliceReliability`。关键场景不能被平均分掩盖。**

> **心智模型 ⑨：`ConfidenceScore ≠ ProbabilityOfBeingCorrect`。可靠系统必须评校准、拒答和 Risk-Coverage。**

> **心智模型 ⑩：`NoExactDuplicate ≠ NoContamination`。测试独立性需要完整 Firewall 和访问治理。**

> **心智模型 ⑪：`HigherOverallScore ≠ NoRegression`。升级必须同时证明收益和关键能力不退化。**

> **心智模型 ⑫：`BenchmarkRun ≠ ReleaseDecision`。评测产生证据，Release Gate 才做最终发布决策。**

---

# 二十四、把整门第九课压成一张最终工程图

```text
                      Evaluation Objective
                         定义评测目标
                               │
                               ▼
                         Benchmark Boundary
                          锁定数据边界
                               │
                               ▼
                         Benchmark Firewall
                           防训练与开发泄漏
                               │
                               ▼
                            Gold Set
                    专家标注 + 证据 + 裁决
                               │
                               ▼
                       Evaluation Schema
                      结果 / 过程 / 证据 / 错误
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
         Classification     Generation      RAG / Agent
             分类              生成           系统链路
                │              │              │
                └──────────────┼──────────────┘
                               ▼
                        Slice Evaluation
                         关键场景切片
                               │
                               ▼
                 Calibration / Abstention / OOD
                    置信度与拒答可靠性
                               │
                               ▼
                       Regression Compare
                         新旧版本回归
                               │
                               ▼
                         Release Gate
                          发布门槛
                    ┌──────────┴──────────┐
                    ▼                     ▼
                  Reject                 Pass
                   否决                   通过
                                           │
                                           ▼
                               ProcurementBench_V1
```

脑中最后只留一句：

> **真正的 Benchmark，不是拿一批题跑一个总分，而是把高可信 Gold、任务化 Evaluation Schema、分类/生成/RAG/Agent 指标、关键 Slice、Calibration、Benchmark Firewall 和 Regression 全部接成一条证据链，最后用预先定义的 Release Gate 决定新系统是否真的值得上线。**

---

# 第九课 · 第 12 阶段掌握测试

现在不回看正文，你应该能够解释：ProcurementBench_V1 为什么不是一个数据文件；Benchmark Version 为什么同时包含数据、协议、Schema 和 Metric；为什么每次 Run 必须有 Manifest；为什么 Overall Score 只能做 Dashboard；Release Gate 应该包含哪些子门槛；为什么 Benchmark 的价值不仅是证明“更强”，还要阻止错误发布；Champion / Challenger 工作流怎样运行；为什么 Benchmark 自身也需要 Quality Gate；人工评测、LLM Judge、程序指标怎样分层组合；为什么评测预算也要按风险分配；Release Report 应该说明什么；为什么 Benchmark Pass 不等于 Universal Guarantee；以及为什么评测体系必须长期版本化维护。

如果这些能够完整讲出来：

\[
\boxed{
第九课第12阶段真正掌握
}
\]

---

# 第九课正式完成

到这里：

\[
\boxed{
第九课
=
12/12
}
\]

最终工程交付：

\[
\boxed{
ProcurementBench\_V1
}
\]

课程系统演化到：

\[
\boxed{
ProcurementDataset\_V0.1
\rightarrow
ProcurementLM\_V0.1
\rightarrow
ProcurementRAG\_V0.1
\rightarrow
ProcurementAgent\_V0.1
\rightarrow
ProcurementLM\_V0.2
\rightarrow
ProcurementBench\_V1
}
\]

下一课正式进入：

# 第十课：推理部署、性能优化与 MLOps
## 怎样把已经通过 Benchmark 的系统真正部署成低延迟、高吞吐、可监控、可灰度发布的 `ProcurementAI`？

第九课解决的是：

> **我们怎么知道系统真的更好。**

第十课开始解决：

> **怎样让这个已经被证明更好的系统，在真实生产环境里稳定、快速、可控地运行。**

---
