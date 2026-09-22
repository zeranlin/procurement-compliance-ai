# 第九课 · 第 2 阶段
# Gold Set：专家标注、Adjudication 与 Ground Truth
## “标准答案”是谁说了算？多个采购专家意见不一致时，怎样把主观判断变成可审计、可复现的 Gold Label？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **ExpertOpinion ≠ GroundTruth。专家意见只是输入，Gold Truth 来自受控标注与裁决流程。**
2. **Gold = AuthorityByProcess。Gold 的权威性来自 Schema、证据、独立判断、裁决和版本治理，而不是单一专家身份。**
3. **BadSchema + GoodExperts = UnstableGold。标注结构和边界没定义清楚，再好的专家也会产生不稳定标签。**
4. **GoodExpert ≠ GoodAnnotator。领域知识和高一致性标注能力是两种不同能力。**
5. **Agreement Metric ≠ Ground Truth Quality。一致性高不代表一定正确，一致性低也不等于谁必须被淘汰。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `Adjudication` | 专家裁决：对分歧样本形成最终 Gold 结论 |
| `ANN` | ANN/近似最近邻：在大规模向量中快速寻找相似项 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |

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

第 1 阶段我们已经锁定：

\[
\boxed{
Training
\neq
Validation
\neq
Test
\neq
GoldBenchmark
}
\]

并且进一步建立：

\[
\boxed{
Benchmark
=
FrozenData
+
StableProtocol
+
StableMetrics
+
Governance
}
\]

但现在出现了一个更根本的问题：

> **Gold Benchmark 里面的“Gold”，到底是谁定义的？**

假设有一条采购条款：

```text
供应商须在项目所在地设立固定服务机构。
```

专家 A 认为：

> 存在不合理地域限制风险。

专家 B 认为：

> 如果项目确实需要本地即时服务，可能具有合理业务依据。

专家 C 认为：

> 需要结合采购需求、履约时效、服务半径和替代措施后才能判断。

那么真正的问题是：

> **谁对？**

如果我们只是：

```text
找一个资深专家
↓
他说是什么
↓
就记成Gold Label
```

那我们得到的不是严格意义上的 Ground Truth。

更准确地说：

> 我们得到的是一个 Expert Opinion。

所以本阶段最重要的第一条边界是：

\[
\boxed{
ExpertOpinion
\neq
GroundTruth
}
\]

本阶段最终形成：

# `ProcurementGoldSetPolicy_V0.1`

---

# 一、Gold Label 到底是什么？

Gold Label 不是：

> “专家觉得最合理的答案。”

更专业的定义是：

\[
\boxed{
GoldLabel
=
Schema
+
Evidence
+
IndependentJudgment
+
Adjudication
+
VersionedDecision
}
\]

也就是说，一个 Gold Label 至少需要：

```text
明确标注结构
证据依据
独立判断
争议裁决
版本化记录
```

所以：

\[
\boxed{
Gold
不是
AuthorityByPerson
}
\]

而是：

\[
\boxed{
Gold
=
AuthorityByProcess
}
\]

中文：

> **Gold 的可信度来自过程，而不是来自某一个人“资历很高”。**

---

# 二、核心心智模型 ①
# `ExpertOpinion ≠ GoldLabel`

一个专家的判断可以：

```text
专业
有经验
有依据
高质量
```

但它仍然只是：

# Expert Opinion
## 专家意见

只有经过：

```text
Annotation Guideline
标注规范

Independent Annotation
独立标注

Evidence Requirement
证据要求

Conflict Resolution
冲突处理

Adjudication
正式裁决
```

以后，

才有资格升级成：

# Gold Label
## 金标准标签

所以：

\[
\boxed{
GoldLabel
=
ProcessControlledExpertJudgment
}
\]

---

# 三、为什么 Gold Set 最先要定义 Annotation Schema？

# Annotation Schema
## 标注结构

回答的是：

> **每个样本到底要标什么字段？**

例如一个采购风险样本，如果只标：

```text
risk = yes / no
```

信息可能远远不够。

更完整的 Schema 可以是：

```text
sample_id

risk_label

risk_type

risk_severity

evidence_span

reason

applicable_context

ambiguity_flag

confidence

source_reference
```

其中：

### `risk_label`
是否存在目标风险。

### `risk_type`
属于哪一类风险。

### `evidence_span`
文本里哪一段支持这个判断。

### `reason`
为什么这样判。

### `applicable_context`
这个判断成立需要什么上下文。

### `ambiguity_flag`
是不是存在合理争议。

### `confidence`
标注者对判断有多大把握。

所以：

\[
\boxed{
AnnotationSchema
决定
WhatGroundTruthMeans
}
\]

如果 Schema 本身含糊，

后面再专业的专家也很难得到稳定 Gold。

---

# 四、核心心智模型 ②
# `BadSchema + GoodExperts = UnstableGold`

很多团队遇到专家意见不一致，

第一反应是：

> “专家水平不一样。”

但真正问题可能是：

```text
标签定义不清
类别边界重叠
风险类型互相包含
证据要求没写
模糊案例没定义
```

所以：

\[
\boxed{
AnnotatorDisagreement
可能来自
SchemaAmbiguity
}
\]

而不一定来自：

> “某个专家错了”。

因此标注一致性差时，

第一步不应该立刻淘汰标注者，

而要先检查：

# Annotation Guideline
## 标注规范

---

# 五、Annotation Guideline 应该写到什么程度？

至少需要回答：

```text
这个Label的正式定义是什么？

什么情况属于正例？

什么情况属于负例？

有哪些边界案例？

哪些证据是必须的？

什么时候允许标Ambiguous？

什么时候允许Abstain？

多标签能不能同时成立？

冲突时优先看什么证据？
```

例如不要只写：

```text
标签：
地域限制
```

而应该写成更接近：

```text
Label:
地域限制风险

Definition:
对供应商注册地、设立地、经营地、服务机构所在地等提出与项目实际需要缺乏充分关联的限制。

Positive Example:
明确要求供应商必须在某地注册，且没有与履约必要性相对应的合理说明。

Negative Example:
要求供应商具备能够满足明确时效要求的服务能力，但不限定注册地。

Ambiguous Example:
要求在本地设置服务点，但采购需求同时存在高频现场响应要求，需要进一步结合上下文判断。
```

这才叫：

# Operational Definition
## 可操作定义

即：

> 不是“概念解释”，而是能指导不同标注者做出一致判断的定义。

---

# 六、Annotator Qualification：谁有资格做 Gold 标注？

# Annotator Qualification
## 标注者资格

Gold Set 不适合完全依赖：

> 无领域背景的普通众包标注。

但也不是说：

> 只要专家职称高就一定适合。

真正应该看：

```text
领域知识
规则理解
标注规范理解
证据意识
边界案例判断能力
一致性表现
```

所以：

\[
\boxed{
DomainExpertise
\neq
AnnotationSkill
}
\]

一个很懂采购的人，

不一定天然会做：

> 高一致性的 Benchmark 标注。

---

# 七、核心心智模型 ③
# `GoodExpert ≠ GoodAnnotator`

标注者必须经过：

```text
Guideline Training
标注规范培训

Calibration Round
校准轮次

Trial Annotation
试标

Error Review
错误复盘

Qualification Test
资格测试
```

然后才进入正式 Gold 标注。

所以：

\[
\boxed{
AnnotatorQuality
=
Expertise
+
GuidelineMastery
+
Calibration
}
\]

---

# 八、为什么必须 Independent Annotation？

# Independent Annotation
## 独立标注

意思是：

> 多个标注者先独立判断，不能提前互相讨论答案。

例如：

```text
Sample 001

Annotator A
→ risk

Annotator B
→ no_risk

Annotator C
→ ambiguous
```

为什么必须先独立？

因为如果一开始就一起讨论：

```text
资深专家先说答案
↓
其他人跟随
```

你就无法知道：

> 他们是真的独立一致，还是发生了从众。

这会产生：

# Anchoring Bias
## 锚定偏差

和：

# Authority Bias
## 权威偏差

所以：

\[
\boxed{
IndependentFirst
\rightarrow
DiscussLater
}
\]

---

# 九、Inter-Annotator Agreement：专家一致性到底怎么量化？

# Inter-Annotator Agreement
## 标注者间一致性

最简单可以看：

# Percent Agreement
## 简单一致率

例如：

\[
Agreement
=
\frac{NumberOfAgreedItems}
{TotalItems}
\]

如果 100 个样本中：

```text
85个样本两位专家一致
```

那么：

\[
Agreement=85\%
\]

但简单一致率有一个问题：

> 没有扣除“随机碰巧一致”。

---

# 十、Cohen's Kappa：为什么比简单一致率更严格？

如果是两个标注者、类别型标签，

常见指标之一是：

# Cohen's Kappa
## Cohen κ 一致性系数

概念公式：

\[
\kappa
=
\frac{p_o-p_e}
{1-p_e}
\]

其中：

\[
p_o
=
ObservedAgreement
\]

即：

> 实际观察到的一致率。

\[
p_e
=
ExpectedAgreementByChance
\]

即：

> 按两位标注者各自标签分布，随机情况下预期会有多少一致。

所以：

\[
\boxed{
Kappa
=
AgreementBeyondChance
}
\]

它回答：

> **两位专家的一致，超过随机巧合多少？**

---

# 十一、核心心智模型 ④
# `Agreement Metric ≠ Ground Truth Quality`

这是非常容易误解的一点。

如果：

\[
\kappa
\]

很高，

只能说明：

> 标注者很一致。

不自动说明：

> 他们判断一定正确。

例如如果：

```text
所有人都误解了Guideline
```

也可能：

> 高度一致地标错。

所以：

\[
\boxed{
Consistency
\neq
Correctness
}
\]

Agreement 是：

> Gold Quality 的一个指标。

不是：

> Gold Quality 的全部。

---

# 十二、那一致性低意味着什么？

低一致性可能意味着：

```text
Schema有问题

Guideline不清楚

案例本身真的有争议

标注者培训不足

上下文缺失

标签类别设计不合理
```

所以低一致性应该触发：

# Root Cause Analysis
## 根因分析

不能简单：

```text
一致性低
→ 把少数意见删掉
```

否则可能正好删掉了：

> 最有价值的边界信息。

---

# 十三、Adjudication 到底是什么？

# Adjudication
## 争议裁决

指：

> 当独立标注不一致时，通过一个受控流程产生最终 Gold 决策。

注意：

\[
\boxed{
Adjudication
\neq
MajorityVoteOnly
}
\]

简单多数投票：

```text
A = risk
B = risk
C = no_risk
```

可能得到：

> risk。

但如果 C 提供了：

> 更强的权威证据或关键上下文，

那多数票不一定更合理。

所以真正 Adjudication 应考虑：

```text
标注规范
证据
上下文
规则定义
争议点
裁决理由
```

---

# 十四、核心心智模型 ⑤
# `Consensus ≠ Truth`

三个人都同意：

> 不代表一定真。

一个人持少数意见：

> 也不代表一定错。

所以：

\[
\boxed{
MajorityVote
是Aggregation
不是TruthGuarantee
}
\]

Gold Set 的关键不是：

> 让所有人看起来一致。

而是：

> **让最终决策有证据、有规则、有记录。**

---

# 十五、Adjudication 推荐流程

英文流程：

```text
Independent Labels
↓
Disagreement Detection
↓
Evidence Comparison
↓
Guideline Check
↓
Context Review
↓
Adjudicator Decision
↓
Decision Rationale
↓
Gold Label
```

中文解释：

```text
先收集独立标注
↓
识别哪些样本存在冲突
↓
比较每个判断引用的证据
↓
检查标注规范
↓
补充必要上下文
↓
由裁决者作最终决定
↓
记录为什么这样裁决
↓
形成Gold Label
```

所以：

\[
\boxed{
Adjudication
=
Decision
+
Rationale
+
Evidence
}
\]

---

# 十六、Ground Truth 真的“绝对真实吗”？

在很多机器学习任务里：

```text
猫
狗
数字
字符
```

Ground Truth 相对明确。

但政府采购很多任务不是纯客观事实识别。

例如：

```text
条款是否构成不合理限制？

理由是否充分？

风险级别是高还是中？

是否需要进一步人工审核？
```

这些可能带有：

> 规范性判断和上下文依赖。

所以更专业的理解是：

\[
\boxed{
GroundTruth
=
BestAvailableOperationalTruth
}
\]

即：

> **在当前任务定义、证据、规范和版本下，经过治理流程得到的最可信可操作答案。**

不是哲学意义上的：

> 永恒绝对真理。

---

# 十七、核心心智模型 ⑥
# `GroundTruth` 在高争议任务中，本质上是“治理后的可操作真值”

这并不会降低 Gold 的价值。

相反，

它要求我们把：

```text
任务定义
证据来源
裁决原则
不确定性
版本
```

全部写清楚。

所以：

\[
\boxed{
GroundTruthWithoutProvenance
=
WeakGroundTruth
}
\]

没有来源和决策记录的 Gold，

可信度是有限的。

---

# 十八、Ambiguous Case：有些样本本来就不应该硬标 Yes / No

假设一个样本：

```text
要求供应商在本地设置服务点
```

但上下文只给了这一句话。

没有：

```text
响应时效
履约场景
服务范围
行业特性
```

这时强行标：

```text
risk = yes
```

或者：

```text
risk = no
```

可能都会制造：

# Label Noise
## 标签噪声

所以 Gold Schema 应该允许：

```text
ambiguous

insufficient_context

needs_review
```

---

# 十九、核心心智模型 ⑦
# `ForcedCertainty = LabelNoise`

如果真实世界本来存在不确定性，

而标注系统只允许：

```text
Yes
No
```

那么所有不确定性都会被：

> 强行压成错误确定性。

所以：

\[
\boxed{
Uncertainty
应该被
Represented
}
\]

而不是：

> Erased。

这会直接影响后面第 9 阶段：

# Calibration / Abstention / OOD

---

# 二十、Evidence Requirement：Gold Label 为什么必须绑定证据？

如果专家只给：

```text
label = risk
```

以后别人很难判断：

> 为什么？

所以高价值 Gold Sample 最好包含：

```text
evidence_span

source_document

source_section

reference_rule

decision_reason
```

这样可以支持：

```text
专家复核
错误审计
模型解释评测
Citation评测
未来标签修订
```

所以：

\[
\boxed{
GoldLabel
+
Evidence
>
GoldLabelOnly
}
\]

这里的 `>` 表示：

> 审计与评测价值更高。

---

# 二十一、Label Confidence：专家也应该表达不确定性

可以让标注者记录：

# Label Confidence
## 标签置信度

例如：

```text
high
medium
low
```

或者数值：

```text
0.95
0.70
0.55
```

但必须注意：

\[
\boxed{
AnnotatorConfidence
\neq
ProbabilityOfTruth
}
\]

它只是：

> 标注者主观把握程度。

不能直接当作：

> 客观概率。

---

# 二十二、核心心智模型 ⑧
# `Confidence` 是元数据，不是替代 Adjudication 的捷径

一个专家：

```text
confidence = 0.99
```

不能自动压过：

> 另一个专家提供的更强证据。

所以：

\[
\boxed{
HighConfidence
\neq
AutomaticAuthority
}
\]

Confidence 可以帮助：

```text
筛选复核样本
识别边界案例
设计难度Slice
```

但不能直接替代：

> 证据和裁决。

---

# 二十三、Single-label 和 Multi-label 要不要提前定义？

必须。

例如一个条款可能同时涉及：

```text
地域限制
资格条件
履约能力
中小企业政策
```

如果任务天然允许多个风险同时存在，

却把 Schema 设计成：

# Single-label
## 单标签

那 Gold 会丢失真实结构。

如果任务业务上只允许：

> 一个主风险类型，

那就需要明确：

```text
primary_label
secondary_labels
```

所以：

\[
\boxed{
LabelCardinality
必须由TaskDefinition决定
}
\]

---

# 二十四、Gold Set 不只需要 Label，还需要 Provenance

# Provenance
## 来源血缘

至少记录：

```text
sample_id

source_document_id

source_version

project_id

section_id

annotation_guideline_version

annotator_ids

annotation_timestamp

adjudicator_id

adjudication_reason

gold_version
```

为什么？

因为以后如果：

```text
规则更新
源文件更正
发现标注错误
Guideline变化
```

你必须知道：

> 哪些 Gold 样本受影响。

所以：

\[
\boxed{
GoldSet
=
Labels
+
Lineage
}
\]

---

# 二十五、Gold Label Freeze：什么时候一条样本才算正式 Gold？

可以定义一个：

# Gold Promotion Gate
## Gold 晋级门槛

例如：

```text
Schema完整
AND

独立标注完成
AND

必要证据存在
AND

冲突已裁决
AND

Benchmark Firewall通过
AND

Lineage完整
```

只有全部通过：

\[
\boxed{
GoldEligible=True
}
\]

才进入正式 Gold Set。

所以：

\[
\boxed{
Annotated
\neq
Gold
}
\]

---

# 二十六、Gold Set Versioning：标注修正以后怎么办？

不能直接覆盖旧标签。

例如：

```text
ProcurementGold_V1.0
```

后来发现：

```text
17条标签需要修订
```

应该形成：

```text
ProcurementGold_V1.0.1
```

并记录：

```text
changed_item_ids

old_label

new_label

change_reason

adjudicator

timestamp
```

所以：

\[
\boxed{
GoldCorrection
必须Versioned
}
\]

不能：

> 悄悄改答案。

---

# 二十七、核心心智模型 ⑨
# `Gold Set` 是审计资产，不是一次性标注结果

真正 Gold Set 应该能回答：

```text
谁标的？

按哪版Guideline标的？

当时用了什么证据？

谁裁决的？

为什么这样裁决？

后来有没有改过？

哪个Benchmark版本使用了它？
```

所以：

\[
\boxed{
GoldSet
=
AuditableDecisionAsset
}
\]

这也是为什么：

> Benchmark 评测质量的上限，首先受 Gold 质量限制。

---

# 二十八、Gold Quality 的上限决定 Benchmark 的上限

如果 Gold 本身：

```text
标签不稳定
证据缺失
大量争议
版本混乱
```

那么即使模型评测系统再精密，

得到的指标也会很可疑。

所以：

\[
\boxed{
BenchmarkQuality
\leq
GoldQuality
}
\]

这里不是严格数学不等式。

它表达：

> **评测体系不可能长期比自己的标准答案更可信。**

---

# 二十九、完整 Gold Set 生产流程

英文流程：

```text
Task Definition
↓
Annotation Schema
↓
Guideline Design
↓
Annotator Qualification
↓
Calibration Round
↓
Independent Annotation
↓
Agreement Measurement
↓
Disagreement Detection
↓
Evidence Review
↓
Adjudication
↓
Confidence / Ambiguity Tagging
↓
Gold Promotion Gate
↓
Freeze
↓
Versioned Maintenance
```

中文解释：

```text
先定义评测任务
↓
设计标注字段
↓
写清楚标注规范
↓
筛选并培训标注者
↓
先做一轮校准标注
↓
正式独立标注
↓
测量一致性
↓
发现冲突样本
↓
比较证据
↓
做正式争议裁决
↓
记录置信度和模糊状态
↓
通过Gold晋级门槛
↓
冻结成Gold版本
↓
以后所有修改都版本化
```

所以：

\[
\boxed{
GoldCreation
=
ControlledDecisionPipeline
}
\]

---

# 三十、本阶段正式工程产物
# `ProcurementGoldSetPolicy_V0.1`

第一版至少锁定：

```text
gold_policy_version

task_definition

annotation_schema_version

annotation_guideline_version

label_definition

positive_examples

negative_examples

ambiguous_examples

annotator_qualification_policy

calibration_round_required

independent_annotation_required

minimum_annotators

agreement_metric

agreement_threshold

disagreement_policy

adjudication_required

adjudicator_role

evidence_required

evidence_schema

ambiguity_policy

insufficient_context_policy

abstain_policy

label_confidence_policy

single_multi_label_policy

provenance_required

gold_promotion_gate

benchmark_firewall_required

gold_freeze_policy

gold_versioning_policy

audit_log
=
enabled
```

每个 Gold Sample 至少记录：

```text
sample_id

source_id

source_version

annotation_schema_version

guideline_version

annotator_labels

annotator_reasons

annotator_evidence

agreement_status

adjudication_status

adjudicated_label

adjudication_reason

ambiguity_flag

label_confidence

gold_eligible

gold_version
```

这样以后才能回答：

> **这个 Gold Label 为什么是这个答案，而不是另一个答案？**

---

# 三十一、本阶段最重要的 10 个核心心智模型

> **心智模型 ①：`ExpertOpinion ≠ GroundTruth`。专家意见只是输入，Gold Truth 来自受控标注与裁决流程。**

> **心智模型 ②：`Gold = AuthorityByProcess`。Gold 的权威性来自 Schema、证据、独立判断、裁决和版本治理，而不是单一专家身份。**

> **心智模型 ③：`BadSchema + GoodExperts = UnstableGold`。标注结构和边界没定义清楚，再好的专家也会产生不稳定标签。**

> **心智模型 ④：`GoodExpert ≠ GoodAnnotator`。领域知识和高一致性标注能力是两种不同能力。**

> **心智模型 ⑤：`Agreement Metric ≠ Ground Truth Quality`。一致性高不代表一定正确，一致性低也不等于谁必须被淘汰。**

> **心智模型 ⑥：`Consensus ≠ Truth`。多数投票只是聚合方法，不是事实保证；最终 Gold 必须有证据和裁决理由。**

> **心智模型 ⑦：`ForcedCertainty = LabelNoise`。真实存在模糊性时，强制 Yes / No 会制造错误确定性。**

> **心智模型 ⑧：`GoldLabel + Evidence > GoldLabelOnly`。有证据的标签才具备更高的复核、审计和生成评测价值。**

> **心智模型 ⑨：`Annotated ≠ Gold`。完成标注只是中间状态，只有通过 Gold Promotion Gate 才能进入正式 Gold Set。**

> **心智模型 ⑩：`GoldSet = AuditableDecisionAsset`。Gold Set 不是一张标签表，而是一套可以追溯谁、依据什么、如何裁决、何时修改的决策资产。**

---

# 三十二、把完整 Gold Set 流程压成一张专业工程图

```text
                         Task Definition
                           定义评测任务
                                │
                                ▼
                       Annotation Schema
                         设计标注结构
                                │
                                ▼
                      Annotation Guideline
                         编写标注规范
                                │
                                ▼
                    Annotator Qualification
                         标注者资格校准
                                │
                                ▼
                     Independent Annotation
                           独立标注
                                │
                                ▼
                    Agreement Measurement
                          一致性评估
                                │
                  ┌─────────────┴─────────────┐
                  ▼                           ▼
               Agree                      Disagree
                一致                         冲突
                  │                           │
                  │                           ▼
                  │                    Evidence Review
                  │                       证据复核
                  │                           │
                  │                           ▼
                  │                      Adjudication
                  │                       正式裁决
                  │                           │
                  └─────────────┬─────────────┘
                                ▼
                     Ambiguity / Confidence
                       模糊性与置信度记录
                                │
                                ▼
                      Gold Promotion Gate
                         Gold晋级门槛
                                │
                  ┌─────────────┴─────────────┐
                  ▼                           ▼
                Reject                       Pass
                 淘汰                         通过
                                              │
                                              ▼
                                         Gold Freeze
                                          冻结版本
                                              │
                                              ▼
                                    Versioned Maintenance
                                        版本化维护
```

脑中最后只留一句：

> **Gold Set 的本质不是“让专家给每道题一个答案”，而是先定义可操作的标注 Schema，再通过合格标注者的独立判断、一致性测量、证据要求、争议裁决、不确定性表达和版本治理，把专家判断加工成可审计、可复现、可长期比较的 Ground Truth。**

---

# 第九课 · 第 2 阶段掌握测试

现在不回看正文，你应该能够解释：为什么 Expert Opinion 不等于 Ground Truth；Gold Label 的权威为什么来自流程而不是个人；Annotation Schema 为什么决定 Ground Truth 的含义；为什么 Bad Schema 即使配上好专家也会产生不稳定标签；Good Expert 和 Good Annotator 有什么区别；为什么标注者必须先独立判断再讨论；Percent Agreement 和 Cohen's Kappa 分别在测什么；为什么高一致性不自动等于高正确性；低一致性可能暴露哪些系统性问题；Adjudication 和简单多数投票有什么区别；为什么 Consensus 不等于 Truth；高争议任务里的 Ground Truth 应该怎样理解；为什么允许 Ambiguous / Insufficient Context 比强制 Yes / No 更专业；Evidence Requirement 为什么重要；Label Confidence 能说明什么、不能说明什么；Single-label 和 Multi-label 为什么必须在任务定义阶段决定；Gold Set 为什么必须记录 Provenance；为什么 Annotated 不等于 Gold；Gold Promotion Gate 应该检查什么；为什么 Gold 修正必须版本化；以及为什么 Benchmark 质量的上限首先受 Gold 质量限制。

如果这些能够完整讲出来：

\[
\boxed{
第九课第2阶段真正掌握
}
\]

---

# 下一阶段：第九课 · 第 3 阶段
# Evaluation Schema：到底评什么，不只是 Correct / Wrong
## 一个政府采购 AI 到底应该被拆成哪些能力维度评测？为什么只给最终答案打一个“对 / 错”，无法定位模型、RAG 和 Agent 真正的问题？

下一阶段会正式进入：

```text
Evaluation Unit
评测单元

Task Taxonomy
任务分类体系

Capability Dimension
能力维度

Outcome Metric
结果指标

Process Metric
过程指标

Evidence Quality
证据质量

Error Taxonomy
错误分类

Severity
错误严重度

Partial Credit
部分得分

Composite Score
复合指标
```

并建立：

# `ProcurementEvaluationSchema_V0.1`

下一阶段最关键的一条边界会是：

\[
\boxed{
CorrectAnswer
\neq
CompleteEvaluation
}
\]

也就是说：

> **最终答案看起来正确，只能说明“结果可能对了”；它并不能证明证据正确、过程可靠、风险边界正确，更不能告诉我们错的时候到底错在哪一层。**

---
