# 第十一课 · 第 2 阶段
# 法规知识体系与 Policy Registry：法律层级、辖区、生效时间、版本和冲突
## 怎样保证系统引用的不是“某个看起来相关的法规”，而是真正对当前采购项目具有适用性的规则？

> **中文阅读增强说明（本次修订新增）**：为方便中国政府采购业务人员、合规人员和工程人员共同阅读，本阶段所有关键英文工程字段、状态值、流程节点和 Schema 标识均保留原英文名称，并在同一代码块中增加 `# 中文：...` 的业务释义。英文名称用于后续数据库、JSON/YAML、API 和程序实现保持稳定；中文释义用于说明它在政府采购合规审查中的实际含义。


第 1 阶段我们已经建立：

\[
\boxed{
LatestPolicy
\neq
ApplicablePolicy
}
\]

**中文业务释义：** 最新发布 / 当前最新政策 ≠ 适用政策 / 适用法规。

并且明确：

> **一个政府采购合规 Finding，不能只有采购文件证据，还必须有真正适用于当前项目的法源证据。**

所以第 2 阶段不只是“收集法规 PDF”。

我们真正要建立的是：

# Policy Registry
## 法规政策注册表 / 适用规则注册中心

本阶段最终形成：

# `ProcurementPolicyRegistry_V1`

它不是一个普通知识库。

它必须能够回答：

```text
这是什么文件？
谁发布的？
法律层级是什么？
适用于哪里？
什么时候发布？
什么时候生效？
什么时候失效？
现在是否有效？
项目发生时是否有效？
适用于什么采购对象？
适用于什么采购方式？
适用于哪个业务环节？
是否存在特别规则？
是否存在上位规则？
是否被修改、废止或替代？
当前 Finding 为什么可以引用它？
```

所以本阶段第一条核心边界：

\[
\boxed{
PolicyRegistry
\neq
VectorDatabase
}
\]

**中文业务释义：** 政策法规注册表 ≠ 向量数据库。

向量库解决的是：

> **“哪段文字语义上相关？”**

Policy Registry 解决的是：

> **“哪一条规则在法律状态、时间、辖区和事项上真正适用？”**

---

# 一、先把“法规知识”拆成三层

政府采购 AI 最容易犯的错误，是把所有文件都当成：

```text
一堆可检索文本
```

但实际至少有三层：

## Layer 1：Source Document
### 来源文件

例如：

```text
法律
行政法规
财政部规章
规范性文件
专项整治通知
专项整治工作指引
地方制度文件
行政处罚 / 处理决定
征求意见稿
```

它回答：

> **这段规则来自哪个正式来源？**

---

## Layer 2：Policy Provision
### 政策 / 法规条文

例如：

```text
第22条第2款
第20条第（七）项
第17条
财库〔2025〕14号某一工作重点
附件9某一表现形式
```

它回答：

> **文件里面具体哪一条产生规范意义？**

---

## Layer 3：Executable Rule
### 可执行规则

把条文进一步工程化成：

```text
Trigger    # 中文：触发条件
Scope    # 中文：适用范围
Condition    # 中文：条件
Exception    # 中文：例外条件
Evidence Requirement    # 中文：证据要求
Decision Logic    # 中文：决策逻辑
Human Review Policy    # 中文：人工复核策略
```

它回答：

> **系统真正应该怎样检查采购文件？**

所以：

\[
\boxed{
SourceDocument
\neq
Provision
\neq
ExecutableRule
}
\]

**中文业务释义：** 来源文件 ≠ 具体条文 / 规定 ≠ 可执行规则。

这是整个 `ProcurementPolicyRegistry_V1` 的第一根骨架。

---

# 二、核心心智模型 ①
# `Law Text ≠ Executable Compliance Rule`

法律文本是人类规范语言。

例如其中经常出现：

```text
不合理条件
实际需要
合同履行无关
无正当理由
除特别规定外
```

这些都不是简单 Boolean。

所以：

\[
\boxed{
LawText
\rightarrow
RuleInterpretation
\rightarrow
ExecutableRule
}
\]

**中文业务释义：** 法规文本 → 规则解释 → 可执行规则。

中间必须经过：

```text
适用范围识别
条件拆解
例外拆解
证据要求
裁量边界
人工复核边界
```

---

# 三、Policy Registry 必须先解决 Source Type

我们先建立一个工程分类。

注意：

> **这是为了让系统管理规则来源的工程分类，不等于把所有文件简单机械地排成一个法律效力分数。**

可以先定义：

```text
LAW    # 中文：法律
法律

ADMINISTRATIVE_REGULATION    # 中文：行政法规
行政法规

DEPARTMENTAL_RULE    # 中文：部门规章
部门规章

NORMATIVE_DOCUMENT    # 中文：规范性文件
规范性文件

SPECIAL_INSPECTION_NOTICE    # 中文：专项整治通知
专项整治通知

SPECIAL_INSPECTION_GUIDE    # 中文：专项整治工作指引
专项整治工作指引

LOCAL_RULE    # 中文：地方规则 / 地方政策
地方规则 / 地方政策

ENFORCEMENT_DECISION    # 中文：执法 / 处理处罚决定
处理处罚 / 行政执法结果

OFFICIAL_INTERPRETATION_OR_REPLY    # 中文：官方解释 / 答复
官方解释 / 答复

DRAFT    # 中文：草案 / 征求意见稿
草案 / 征求意见稿
```

不同 Source Type：

> **在系统里的使用方式不应该一样。**

---

# 四、核心心智模型 ②
# `SourceType ≠ AuthorityAutomaticallyResolved`

知道一个文件属于：

```text
部门规章
```

不等于系统已经知道：

> 当前项目一定适用它。

还必须继续判断：

```text
Jurisdiction    # 中文：适用辖区
辖区

Effective Time    # 中文：生效时间
有效时间

Subject Matter    # 中文：适用事项
事项范围

Procurement Method    # 中文：采购方式
采购方式

Object Scope    # 中文：适用对象范围
采购对象

Exception    # 中文：例外条件
例外
```

所以：

\[
\boxed{
Authority
只是
Applicability
的一部分
}
\]

---

# 五、发布时间、生效时间、失效时间必须分开

法规知识库不能只有：

```text
publish_date    # 中文：发布日期
```

至少要有：

```text
publication_date    # 中文：发布日期
发布日期

effective_from    # 中文：生效起始
生效日期

effective_to    # 中文：生效截止
失效 / 截止日期

repeal_date    # 中文：废止日期
废止日期
```

因为：

\[
\boxed{
PublicationDate
\neq
EffectiveDate
}
\]

**中文业务释义：** 发布日期 ≠ 施行日期。

例如一个文件：

> 今天发布，三个月后施行。

在这三个月里：

```text
已发布
但尚未生效
```

所以系统状态不能只有：

```text
有效 / 无效
```

---

# 六、建议的 Policy Status 状态机

第一版至少定义：

```text
DRAFT    # 中文：草案 / 征求意见稿
草案

PUBLISHED_NOT_EFFECTIVE    # 中文：已发布但尚未生效
已发布但尚未生效

EFFECTIVE    # 中文：现行有效
现行有效

PARTIALLY_EFFECTIVE    # 中文：部分条款已生效 / 部分有效
部分条款 / 分阶段生效

AMENDED    # 中文：已被修订
已修改

SUPERSEDED    # 中文：已被后续文件替代
已被新规则替代

REPEALED    # 中文：已废止
已废止

EXPIRED    # 中文：已失效 / 到期
期限届满

UNKNOWN    # 中文：状态未知
状态待确认
```

但这里还有一条非常重要的边界：

\[
\boxed{
CurrentStatus
\neq
HistoricalApplicability
}
\]

**中文业务释义：** 当前状态 ≠ 历史时点适用性。

一个现在已经废止的文件：

> 可能对 2023 年发生的采购项目仍然是当时适用的规则。

所以系统不能因为今天状态是：

```text
REPEALED    # 中文：已废止
```

就把它从历史项目里删除。

---

# 七、核心心智模型 ③
# `DeleteOldPolicy` 是合规系统的大忌

真正需要的是：

# Versioned Policy History
## 版本化法规历史

例如：

```text
Policy V1    # 中文：政策 / 法规V1
2022-01-01 → 2024-06-30

Policy V2    # 中文：政策 / 法规V2
2024-07-01 → 2026-01-31

Policy V3    # 中文：政策 / 法规V3
2026-02-01 → Current    # 中文：2026-02-01 → 当前
```

查询 2023 年项目：

> 返回 V1。

查询 2025 年项目：

> 返回 V2。

查询 2026 年 3 月项目：

> 返回 V3。

所以：

\[
\boxed{
PolicyUpdate
\neq
OverwriteOldVersion
}
\]

**中文业务释义：** 政策更新 ≠ 覆盖旧版本。

---

# 八、Temporal Reasoning：适用时间到底看哪个时间？

一个采购项目可能有很多时间点：

```text
需求编制时间
采购文件发布时间
公告发布时间
投标截止时间
评审时间
合同签订时间
履约时间
投诉时间
监督检查时间
```

不同规则：

> 可能绑定不同事件时间。

所以系统不能只有：

```text
project_date    # 中文：项目日期
```

而应该有：

# Event Time
## 业务事件时间

例如：

```text
procurement_document_issue_date    # 中文：采购文件发布 / 发出日期

bid_deadline    # 中文：投标截止时间

evaluation_date    # 中文：评审日期

award_date    # 中文：中标 / 成交日期

contract_date    # 中文：合同日期

performance_date    # 中文：履约日期

complaint_date    # 中文：投诉发生 / 受理日期

inspection_date    # 中文：监督检查日期
```

然后 Rule 声明：

```text
applicable_event = procurement_document_issue_date    # 中文：规则适用所依据的业务事件 = 采购文件发布 / 发出日期
```

或者：

```text
applicable_event = evaluation_date    # 中文：规则适用所依据的业务事件 = 评审日期
```

所以：

\[
\boxed{
PolicyTimeMatch
必须绑定
BusinessEvent
}
\]

---

# 九、核心心智模型 ④
# `ProjectDate` 不是一个足够专业的字段

真正专业的做法是：

\[
\boxed{
Rule
\leftrightarrow
RelevantBusinessEventTime
}
\]

**中文业务释义：** 规则 ↔ 相关业务事件时间。

这样系统才能回答：

> **为什么用这个版本，而不是另一个版本？**

---

# 十、Jurisdiction：法规适用地域不能靠模型猜

至少要保存：

```text
jurisdiction_level    # 中文：辖区层级

jurisdiction_code    # 中文：辖区编码

country    # 中文：国家

province    # 中文：省级

city    # 中文：市级

county    # 中文：县级

central_or_local_budget    # 中文：中央OR地方 / 本地预算
```

并区分：

```text
全国适用
中央预算单位
某省
某市
某县区
特定行业主管体系
```

所以：

\[
\boxed{
SimilarRule
\neq
ApplicableJurisdiction
}
\]

**中文业务释义：** 相似规则 ≠ 适用辖区。

一个地方财政部门的规则：

> 即使文本非常相关，也不能自动当成全国项目的直接依据。

---

# 十一、核心心智模型 ⑤
# `SearchHit ≠ LegalBasis`

RAG 搜到：

```text
一篇地方通知
```

并且语义很像，

并不意味着：

> 可以直接作为当前中央项目的适用法源。

因此 Legal RAG 的结果必须经过：

```text
Source Validation    # 中文：来源真实性与权威性校验
↓
Jurisdiction Validation    # 中文：适用辖区校验
↓
Temporal Validation    # 中文：生效时间与项目时点校验
↓
Subject Validation    # 中文：适用事项校验
```

之后才有资格成为：

# Legal Basis Candidate
## 法源候选

---

# 十二、Subject Matter：同一个法规也可能只适用于部分业务

例如需要区分：

```text
货物
服务
工程

招标
非招标

资格条件
采购需求
评分标准
履约验收
投诉处理
监督检查
```

所以每条 Rule 应该有：

```text
procurement_category_scope    # 中文：采购类别范围

procurement_method_scope    # 中文：采购方法范围

business_stage_scope    # 中文：业务阶段范围

document_section_scope    # 中文：文档章节范围
```

这让系统知道：

> **不是“法条存在”就自动适用所有采购环节。**

---

# 十三、核心心智模型 ⑥
# `ProvisionExists ≠ ProvisionAppliesHere`

可以把 Rule Applicability 概念化为：

\[
\boxed{
Applicable(r,p)
=
StatusMatch
\land
TimeMatch
\land
JurisdictionMatch
\land
SubjectMatch
\land
StageMatch
\land
NotExcluded
}
\]

**中文业务释义：** 适用(规则r,项目p) = 状态匹配 且 时间匹配 且 辖区匹配 且 事项匹配 且 业务阶段匹配 且 不存在排除情形。

其中：

- \(r\)：Rule；
- \(p\)：Procurement Project / Event。

这不是法律裁判公式。

它是：

> **系统进行适用性过滤的工程模型。**

---

# 十四、Exception：规则一定要能表达例外

政府采购规则中经常出现：

```text
除……外

法律法规另有规定的

特别规定

涉及国家安全 / 国家秘密

采购进口产品

特定项目情形
```

所以 Rule 不能只有：

```text
if trigger:    # 中文：如果满足触发条件：
    violation = true    # 中文：违规判断状态 = 正确 / 真
```

而必须支持：

```text
trigger    # 中文：触发
↓
exception_check    # 中文：例外检查
↓
applicability    # 中文：适用性判断
↓
decision    # 中文：决策
```

所以：

\[
\boxed{
RuleWithoutException
=
IncompleteRule
}
\]

**中文业务释义：** 缺少例外逻辑的规则 = 不完整规则。

---

# 十五、Special Rule 与 General Rule

系统会遇到：

```text
General Rule    # 中文：一般规则
一般规则

Special Rule    # 中文：特别规则
特别规则
```

但不能把它简单硬编码成：

```text
特别规则永远覆盖一般规则
```

因为还要判断：

```text
发布机关
法律层级
事项范围
时间
是否明确特别规定
是否存在冲突
```

所以：

\[
\boxed{
Specificity
\neq
AutomaticPrecedence
}
\]

**中文业务释义：** 规则具体性 / 特别性 ≠ 自动优先适用。

真正存在冲突时：

> 系统应当生成 Conflict Object，并升级人工 / 专业复核。

---

# 十六、核心心智模型 ⑦
# `PolicyConflict ≠ LLMChooseOne`

如果两个来源产生表面冲突：

LLM 不能：

> 自己挑一个更像答案的。

应该输出：

```text
CONFLICT_DETECTED    # 中文：检测到法规 / 规则冲突

candidate_policy_A    # 中文：候选政策 / 法规A
candidate_policy_B    # 中文：候选政策 / 法规B

conflict_type    # 中文：冲突类型

jurisdiction    # 中文：辖区

effective_time    # 中文：生效时间

authority_metadata    # 中文：效力 / 权威元数据

speciality_metadata    # 中文：特别性 / 特殊规则元数据

human_review_required = true    # 中文：是否需要人工复核 = 正确 / 真
```

所以：

\[
\boxed{
Conflict
\Rightarrow
Evidence
+
Escalation
}
\]

**中文业务释义：** 规则冲突 ⇒ 证据 + 升级处理 / 人工复核。

---

# 十七、Amend / Repeal / Supersede 必须做成关系图

法规不是孤立文件。

它们之间存在：

```text
AMENDS    # 中文：修订关系：本文件修订其他文件
修改

REPEALS    # 中文：废止关系：本文件废止其他文件
废止

SUPERSEDES    # 中文：替代
替代

IMPLEMENTS    # 中文：实施关系：本文件落实上位规则
落实

INTERPRETS    # 中文：解释关系：本文件解释其他规则
解释

CITES    # 中文：引用关系：本文件引用其他来源
引用

DERIVES_RULE_FROM    # 中文：规则派生关系：该工程规则来源于某正式规则
规则来源

LOCALIZES    # 中文：地方化关系：上位规则在本地的细化落实
地方细化
```

所以：

# Policy Graph
## 法规关系图

比单纯：

```text
文件列表
```

更专业。

因此：

\[
\boxed{
PolicyRegistry
=
VersionedDocuments
+
ProvisionGraph
+
ExecutableRules
}
\]

**中文业务释义：** 政策法规注册表 = 版本化法规文件 + 条文关系图谱 + 可执行规则集合。

---

# 十八、2025 专项整治工作指引在 Registry 里应该怎么放？

这是一个非常重要的例子。

我们不能把附件 9 简单标成：

```text
LAW    # 中文：法律
```

更合适的工程建模是：

```text
source_type = SPECIAL_INSPECTION_GUIDE    # 中文：来源类型 = 专项整治工作指引

source_title = 2025年政府采购领域“四类”违法违规行为专项整治工作指引

section = 第二部分 检查规范 / 一、关于采购人设置差别歧视条款问题

attachment = 附件9

rule_family = DISCRIMINATION_22    # 中文：规则族 = 附件9差别歧视 D01-D22 规则集

rule_ids = D01-D22    # 中文：规则标识列表 = D01D22
```

同时：

> D01-D22 不能只链接附件 9。

还要继续链接其处理依据 / 法规基础。

例如：

```text
Dxx    # 中文：Dxx 规则编号占位符
↓
附件9表现形式
↓
专项整治检查标准
↓
政府采购法 / 实施条例 / 财政部规章 / 规范性文件等依据
```

所以：

\[
\boxed{
InspectionGuideRule
\neq
StandaloneLegalAuthority
}
\]

**中文业务释义：** 专项检查指引规则 ≠ 独立法律依据。

它更像：

> **监督检查场景中的结构化执法检查规则入口。**

---

# 十九、核心心智模型 ⑧
# `D01-D22` 必须做“规则来源链”而不是一张标签表

每一个 D Rule 至少需要：

```text
rule_id    # 中文：规则标识

manifestation_source    # 中文：具体表现形式来源

inspection_standard_source    # 中文：专项检查标准来源

legal_basis[]    # 中文：法律 / 政策依据

penalty_basis[]    # 中文：处罚依据

exception_sources[]    # 中文：例外来源材料

related_official_cases[]    # 中文：相关官方处理 / 处罚案例列表
```

以后报告才能回答：

> **这个规则为什么存在？**

而不只是：

> “模型说命中了 D07。”

---

# 二十、2026 专项整治为什么必须独立进入 Registry？

到 2026 年，财政部、公安部、市场监管总局继续开展政府采购领域“四类”违法违规行为专项整治。

它继续把：

```text
采购人设置差别歧视条款
```

作为四类重点之一。

并继续关注：

```text
倾斜照顾本地企业
指向特定供应商或产品
注册地
所有制形式
组织形式
股权结构
投资者国别
经营年限
经营规模
财务指标
```

同时明确提出：

> 鼓励在安全可控前提下探索利用人工智能等手段识别采购文件差别歧视条款和围标串标疑点。

因此 Registry 不应该：

> 用 2026 通知覆盖掉 2025 指引。

而应该：

```text
2025 Notice / Guide    # 中文：2025 年专项整治通知 / 工作指引
保留其历史规则版本与附件9来源

2026 Notice    # 中文：2026公告
记录其新的专项整治周期、检查时间、当前工作重点和AI监管方向
```

所以：

\[
\boxed{
NewAnnualCampaign
\neq
DeletePreviousOperationalEvidence
}
\]

**中文业务释义：** 新年度专项整治 ≠ 删除前期业务规则证据。

---

# 二十一、本国产品政策为什么特别适合讲 Policy Version？

`国办发〔2025〕34号`：

```text
publication_date = 2025-09-30    # 中文：发布日期 = 20250930

effective_from = 2026-01-01    # 中文：生效起始 = 20260101
```

这说明：

\[
\boxed{
Published
\neq
Effective
}
\]

**中文业务释义：** 已经发布 ≠ 已经生效。

并且文件本身还规定：

```text
某些分产品组件成本占比要求
某些关键组件 / 关键工序要求
```

会在未来分产品逐步确定，并可能设置过渡期。

这意味着 Registry 还需要支持：

# Partial / Progressive Policy
## 分阶段实施政策

而不是只存：

```text
effective = true    # 中文：生效 = 正确 / 真
```

---

# 二十二、核心心智模型 ⑨
# `PolicyStatus` 有时是 Rule-level，不只是 Document-level

同一个文件里：

> A 条已经生效，B 条可能等待配套规则，C 条可能存在过渡期。

所以：

\[
\boxed{
DocumentEffective
\neq
EveryDerivedRuleFullyOperational
}
\]

**中文业务释义：** 文件整体生效 ≠ 所有派生规则均已完全可执行。

因此 `Policy Registry` 必须允许：

```text
document_status    # 中文：文档状态

provision_status    # 中文：条款 / 规定状态

rule_status    # 中文：规则状态
```

三级状态。

---

# 二十三、异常低价规则为什么必须单独版本化？

`财库〔2026〕2号`：

```text
publication_date = 2026-01-22    # 中文：发布日期 = 20260122

effective_from = 2026-02-01    # 中文：生效起始 = 20260201
```

其中包含明确的异常低价审查触发条件。

这类规则特别适合：

```text
Rule Engine    # 中文：规则引擎
+
Calculator    # 中文：确定性计算器
```

而不是只给 LLM 看原文。

因此 Registry 中应该保存：

```text
rule_type = DETERMINISTIC_THRESHOLD    # 中文：规则类型 = 确定性阈值规则

threshold_version    # 中文：阈值版本

effective_from    # 中文：生效起始

calculation_formula    # 中文：确定性计算公式

exception = related_law_overrides    # 中文：例外 = 相关法律法规存在优先 / 特别规定
```

所以：

\[
\boxed{
PolicyRegistry
不仅服务RAG
还服务RuleEngine
}
\]

---

# 二十四、核心心智模型 ⑩
# `Legal RAG` 和 `Policy Registry` 的职责必须分开

Legal RAG 擅长：

```text
找相关条文
找上下文
找解释材料
找相似案例
```

Policy Registry 擅长：

```text
版本
状态
辖区
时间
关系
适用条件
规则ID
来源链
```

因此：

\[
\boxed{
LegalRAG
回答“哪里相关”
}
\]

\[
\boxed{
PolicyRegistry
回答“是否适用”
}
\]

两者结合才是真正的：

# Applicable Legal Retrieval
## 可适用法源检索

---

# 二十五、Source Provenance：一个 URL 远远不够

至少保存：

```text
source_url    # 中文：官方来源地址

publisher    # 中文：发布机关 / 发布主体

document_number    # 中文：文档编号

publication_date    # 中文：发布日期

retrieved_at    # 中文：检索时间点 / 阶段

source_hash    # 中文：来源哈希

file_hash    # 中文：文件哈希

page_number    # 中文：页编号

article_number    # 中文：条文编号

source_type    # 中文：来源类型
```

因为网页可能更新。

所以：

\[
\boxed{
SourceURL
\neq
CompleteProvenance
}
\]

**中文业务释义：** 来源网址 ≠ 完整来源链。

如果规则以后改变，必须能够回答：

> **当时系统到底依据的是哪一版内容？**

---

# 二十六、双时间模型：Valid Time 与 System Time

这是专业法规系统非常值得引入的概念。

## Valid Time
### 规则在现实世界中何时有效

例如：

```text
2026-02-01开始施行
```

## System Time
### 系统何时知道 / 收录这条规则

例如：

```text
registry_ingested_at = 2026-01-23    # 中文：登记库入库时间点 / 阶段 = 20260123
```

这两个时间可能不同。

所以：

\[
\boxed{
LegalValidityTime
\neq
RegistryKnowledgeTime
}
\]

**中文业务释义：** 法规效力时间 ≠ 系统登记 / 知晓时间。

这让系统可以重放：

> **某一天的系统，当时掌握了什么规则？**

---

# 二十七、核心心智模型 ⑪
# `Reproducibility` 需要 Policy Snapshot

每次正式审查 Run 必须锁定：

```text
policy_registry_version    # 中文：政策 / 法规登记库版本

policy_snapshot_time    # 中文：政策法规快照时间

rule_bundle_version    # 中文：规则包版本
```

这样半年后才能复现：

> 当时为什么判成这个结果。

因此：

\[
\boxed{
Finding
必须绑定
PolicySnapshot
}
\]

---

# 二十八、Rule Object 应该长什么样？

第一版可以定义：

```text
rule_id    # 中文：规则标识

rule_family    # 中文：规则族

rule_name    # 中文：规则名称

source_document_id    # 中文：来源文件标识

source_provision_ids[]    # 中文：来源条款 / 规定标识列表

source_type    # 中文：来源类型

issuer    # 中文：出具机构

authority_metadata    # 中文：效力 / 权威元数据

jurisdiction_scope[]    # 中文：辖区范围

procurement_category_scope[]    # 中文：采购类别范围

procurement_method_scope[]    # 中文：采购方法范围

business_stage_scope[]    # 中文：业务阶段范围

document_section_scope[]    # 中文：文档章节范围

trigger_logic    # 中文：触发逻辑

exception_logic    # 中文：例外逻辑

evidence_requirements[]    # 中文：证据要求

business_event_for_time_match    # 中文：用于法规时间匹配的业务事件

effective_from    # 中文：生效起始

effective_to    # 中文：生效截止

rule_status    # 中文：规则状态

supersedes[]    # 中文：替代

amended_by[]    # 中文：修订由

related_rules[]    # 中文：关联规则列表

human_review_policy    # 中文：人工复核政策 / 法规

confidence_policy    # 中文：置信度政策 / 法规

source_hash    # 中文：来源哈希
```

这才是：

# Executable Policy Object
## 可执行政策对象

---

# 二十九、Applicable Policy Resolver：系统真正怎么找适用法规？

正式流程建议：

```text
1. Resolve Project Facts    # 中文：1. 解析并确认采购项目事实
解析项目事实

2. Resolve Business Event    # 中文：2. 确认当前规则对应的业务事件时点
确定当前判断对应的业务事件

3. Retrieve Candidate Sources    # 中文：3. 检索候选法规 / 政策来源
召回候选法规 / 政策

4. Validate Source Status    # 中文：4. 校验来源权威性和现行状态
检查来源状态

5. Time Filter    # 中文：5. 按生效时间和项目时点过滤
按生效区间过滤

6. Jurisdiction Filter    # 中文：6. 按适用辖区过滤
按辖区过滤

7. Subject / Stage Filter    # 中文：7. 按适用事项 / 采购阶段过滤
按采购对象和业务阶段过滤

8. Exception Check    # 中文：例外检查
检查例外

9. Relationship / Conflict Check    # 中文：9. 检查文件关系和规则冲突
检查修改、替代、冲突关系

10. Produce Applicable Policy Set    # 中文：10. 形成当前项目适用的法规政策集合
形成适用政策集合

11. Bind Snapshot    # 中文：11. 绑定政策法规快照
绑定Policy Registry版本

12. If Conflict or Unknown    # 中文：12. 若存在冲突或未知状态则转人工 / 暂缓结论
升级人工复核
```

可以压成：

\[
\boxed{
CandidatePolicy
\rightarrow
ValidatedSource
\rightarrow
ApplicablePolicy
\rightarrow
BoundLegalBasis
}
\]

**中文业务释义：** 候选政策 → 验证来源 → 适用政策 / 适用法规 → Bound法律依据。

---

# 三十、核心心智模型 ⑫
# `Retrieval` 只是 Applicable Policy Resolver 的第一步

RAG Top-1：

> 不等于适用法源 Top-1。

所以：

\[
\boxed{
SemanticSimilarity
\neq
LegalApplicability
}
\]

**中文业务释义：** SemanticSimilarity ≠ 法律适用性。

这是 Legal RAG 和普通企业知识库最大的区别之一。

---

# 三十一、冲突和不确定状态必须显式输出

适用法源解析至少需要：

```text
RESOLVED    # 中文：已解决

MULTIPLE_APPLICABLE    # 中文：存在多项同时适用的规则 / 文件

CONFLICT_DETECTED    # 中文：检测到法规 / 规则冲突

JURISDICTION_UNKNOWN    # 中文：适用辖区未知

TIME_UNKNOWN    # 中文：关键业务时点未知

STATUS_UNKNOWN    # 中文：法规 / 规则状态未知

INSUFFICIENT_SOURCE    # 中文：不足来源

NEEDS_HUMAN_REVIEW    # 中文：需要人工复核
```

所以：

\[
\boxed{
PolicyResolution
不是
SingleString
}
\]

而是：

# Resolution State Machine
## 适用政策解析状态机

---

# 三十二、核心心智模型 ⑬
# `Unknown Policy State` 必须阻止虚假确定性

如果：

```text
项目时间未知
辖区未知
规则状态未知
```

系统不能：

> 直接生成高置信违规结论。

应该：

```text
policy_resolution = UNRESOLVED    # 中文：政策 / 法规消解 = 无法确定 / 待解决

human_review_required = true    # 中文：是否需要人工复核 = 正确 / 真
```

所以：

\[
\boxed{
NoApplicablePolicyProof
\Rightarrow
NoHighConfidenceLegalConclusion
}
\]

**中文业务释义：** 无/未适用政策证明 ⇒ 无/未高置信度法律Conclusion。

---

# 三十三、D01-D22 如何接进 Policy Registry？

每一个 D Rule：

```text
D01    # 中文：D01 规则编号（附件9工程化规则标识）
...
D22    # 中文：D22 规则编号（附件9工程化规则标识）
```

必须链接：

```text
1. 附件9表现形式

2. 正文对应检查标准

3. 处理依据

4. 处罚依据

5. 相关上位法 / 实施条例 / 部门规章 / 规范性文件

6. 适用例外

7. 后续年度专项整治延续信息

8. 相关官方处理处罚案例
```

因此：

\[
\boxed{
D01-D22
=
RuleLayer
而不是
SourceLayer
}
\]

附件 9：

> 是重要 Source。

D01-D22：

> 是我们根据该 Source 结构化出来的 Rule Objects。

---

# 三十四、官方处理处罚案例在 Registry 中是什么角色？

例如财政部公开的专项整治处理处罚信息中，已经存在：

> 因采购文件存在以不合理条件对供应商实行差别待遇或者歧视待遇而受到处理处罚的公开案例。

这些案例不应该替代法规。

它们更适合作为：

# Enforcement Evidence
## 执法实践证据

可以帮助：

```text
训练Hard Case
建立案例RAG
理解规则如何落地
构造Benchmark
```

所以：

\[
\boxed{
Case
\neq
Rule
}

但：

\[
\boxed{
Case
可以帮助解释
RuleApplication
}
\]

---

# 三十五、核心心智模型 ⑭
# `LegalBasis`、`InspectionRule`、`EnforcementCase` 必须三层分离

最终一个 Finding 可以同时拥有：

```text
legal_basis    # 中文：法律 / 政策依据
法律 / 行政法规 / 规章 / 规范性文件依据

inspection_rule    # 中文：专项检查规则
D01-D22专项检查规则

enforcement_reference    # 中文：执法 / 处理处罚参考
相关公开处理处罚案例
```

但不能把它们混成：

> “都是法规”。

---

# 三十六、当前 `ProcurementPolicyRegistry_V1` 的第一批 Source Seed

截至本阶段校验时，第一版至少应纳入：

```text
《中华人民共和国政府采购法》

《中华人民共和国政府采购法实施条例》
国务院令第658号

《政府采购货物和服务招标投标管理办法》
财政部令第87号

《政府采购促进中小企业发展管理办法》
财库〔2020〕46号

《财政部关于促进政府采购公平竞争优化营商环境的通知》
财库〔2019〕38号

《财政部关于在政府采购活动中落实平等对待内外资企业有关政策的通知》
财库〔2021〕35号

《2025年政府采购领域“四类”违法违规行为专项整治工作指引》
以及附件9

《财政部 公安部 市场监管总局关于开展2025年政府采购领域“四类”违法违规行为专项整治工作的通知》
财库〔2025〕14号

《财政部 公安部 市场监管总局关于开展2026年政府采购领域“四类”违法违规行为专项整治工作的通知》
财库〔2026〕9号

《国务院办公厅关于在政府采购中实施本国产品标准及相关政策的通知》
国办发〔2025〕34号

《财政部关于推动解决政府采购异常低价问题的通知》
财库〔2026〕2号
```

这些只是：

# Seed Registry
## 第一批种子法规源

不是最终完整法规库。

---

# 三十七、当前几个非常重要的时间校验点

## 财政部令第 87 号

```text
发布：2017-07-11
施行：2017-10-01
```

## 国办发〔2025〕34号

```text
发布：2025-09-30
施行：2026-01-01
```

## 财库〔2026〕2号

```text
发布：2026-01-22
施行：2026-02-01
```

## 财库〔2026〕9号

```text
发文：2026-06-08
专项整治周期：2026年6月中旬至12月底
```

这些例子共同证明：

\[
\boxed{
PolicyDate
不是一个字段
}
\]

而是一组：

```text
publish    # 中文：发布
issue    # 中文：发布 / 出具
effective    # 中文：生效
expiry    # 中文：到期 / 失效时间
campaign_window    # 中文：专项整治工作周期
business_event    # 中文：业务事件
```

不同时间语义。

---

# 三十八、本阶段正式工程产物
# `ProcurementPolicyRegistry_V1`

第一版至少锁定以下 Schema：

```text
policy_registry_version    # 中文：政策 / 法规登记库版本

policy_document_id    # 中文：政策 / 法规文档标识

title    # 中文：标题

document_number    # 中文：文档编号

issuer    # 中文：出具机构

source_type    # 中文：来源类型

authority_metadata    # 中文：效力 / 权威元数据

publication_date    # 中文：发布日期

issue_date    # 中文：发布 / 出具日期

effective_from    # 中文：生效起始

effective_to    # 中文：生效截止

campaign_start    # 中文：专项整治开始时间

campaign_end    # 中文：专项整治结束时间

current_status    # 中文：当前状态

jurisdiction_level    # 中文：辖区层级

jurisdiction_codes[]    # 中文：适用辖区编码列表

central_local_scope    # 中文：中央地方 / 本地范围

procurement_category_scope[]    # 中文：采购类别范围

procurement_method_scope[]    # 中文：采购方法范围

business_stage_scope[]    # 中文：业务阶段范围

document_section_scope[]    # 中文：文档章节范围

article_id    # 中文：条文标识

provision_id    # 中文：条款 / 规定标识

provision_text    # 中文：条款 / 规定文本

rule_ids[]    # 中文：规则标识列表

rule_status    # 中文：规则状态

exception_ids[]    # 中文：例外标识列表

amends[]    # 中文：本文件修订的文件列表

amended_by[]    # 中文：修订由

repeals[]    # 中文：本文件废止的文件列表

repealed_by[]    # 中文：废止本文件的后续文件列表

supersedes[]    # 中文：替代

implements[]    # 中文：本文件实施 / 落实的上位规则列表

interprets[]    # 中文：本文件解释的规则列表

cites[]    # 中文：本文件引用的来源列表

related_cases[]    # 中文：关联官方案例列表

source_url    # 中文：官方来源地址

source_hash    # 中文：来源哈希

retrieved_at    # 中文：检索时间点 / 阶段

registry_ingested_at    # 中文：登记库入库时间点 / 阶段

valid_time    # 中文：有效时间

system_time    # 中文：系统时间

human_review_required    # 中文：是否需要人工复核
```

并建立：

# `ApplicablePolicyResolver`
## 适用政策解析器

负责：

```text
Candidate Retrieval    # 中文：候选法规 / 规则检索
候选召回

Status Validation    # 中文：法规 / 规则状态校验
状态校验

Temporal Filtering    # 中文：时间适用性过滤
时间过滤

Jurisdiction Filtering    # 中文：辖区适用性过滤
辖区过滤

Scope Filtering    # 中文：事项 / 范围适用性过滤
事项过滤

Exception Check    # 中文：例外检查
例外检查

Conflict Detection    # 中文：冲突检测
冲突检测

Policy Snapshot Binding    # 中文：绑定政策法规快照
版本快照绑定
```

---

# 三十九、本阶段最重要的 14 个核心心智模型

> **心智模型 ①：`PolicyRegistry ≠ VectorDatabase`。向量库找语义相关，Registry 判断规则状态和适用性。**

> **心智模型 ②：`SourceDocument ≠ Provision ≠ ExecutableRule`。来源文件、具体条文和机器可执行规则必须分层。**

> **心智模型 ③：`LawText ≠ ExecutableComplianceRule`。法律文本必须拆成范围、条件、例外、证据与裁量边界。**

> **心智模型 ④：`PublicationDate ≠ EffectiveDate`。发布时间和生效时间是不同语义。**

> **心智模型 ⑤：`CurrentStatus ≠ HistoricalApplicability`。现在废止的规则可能仍然适用于历史项目。**

> **心智模型 ⑥：`PolicyUpdate ≠ OverwriteOldVersion`。法规更新必须保留历史版本链。**

> **心智模型 ⑦：`ProjectDate` 不够，规则必须绑定真正相关的 Business Event Time。**

> **心智模型 ⑧：`SearchHit ≠ LegalBasis`。语义相关不等于辖区、时间和事项上可适用。**

> **心智模型 ⑨：`RuleWithoutException = IncompleteRule`。规则工程化必须显式表达例外。**

> **心智模型 ⑩：`PolicyConflict ≠ LLMChooseOne`。冲突必须形成证据对象并升级人工。**

> **心智模型 ⑪：`InspectionGuideRule ≠ StandaloneLegalAuthority`。D01-D22 要沿规则来源链回到处理依据和法源。**

> **心智模型 ⑫：`LegalRAG` 找相关，`PolicyRegistry` 判适用，两者职责不同。**

> **心智模型 ⑬：`Finding` 必须绑定 `PolicySnapshot`，否则无法复现当时为什么作出这个判断。**

> **心智模型 ⑭：`LegalBasis`、`InspectionRule`、`EnforcementCase` 必须三层分离，不能统称“法规”。**

---

# 四十、把 `ProcurementPolicyRegistry_V1` 压成一张专业工程图

```text
                         Procurement Project    # 中文：采购项目
                           政府采购项目
                                  │
                                  ▼
                          Project Context    # 中文：项目业务上下文
                    时间 / 地区 / 类型 / 方式
                                  │
                                  ▼
                         Business Event Time    # 中文：业务事件时点
                       规则对应的业务事件时间
                                  │
                                  ▼
                         Candidate Retrieval    # 中文：候选法规 / 规则检索
                         候选法规 / 政策召回
                                  │
                                  ▼
                         Source Validation    # 中文：来源真实性与权威性校验
                      来源 / 文号 / 发布机关校验
                                  │
                                  ▼
                         Status Validation    # 中文：法规 / 规则状态校验
                    Draft / Effective / Repealed    # 中文：草案 / 现行有效 / 已废止
                                  │
                                  ▼
                         Temporal Filtering    # 中文：时间适用性过滤
                            生效时间过滤
                                  │
                                  ▼
                       Jurisdiction Filtering    # 中文：辖区适用性过滤
                              辖区过滤
                                  │
                                  ▼
                       Subject / Stage Filter    # 中文：适用事项 / 采购阶段过滤
                         事项与业务阶段过滤
                                  │
                                  ▼
                          Exception Check    # 中文：例外检查
                              例外检查
                                  │
                                  ▼
                      Relationship / Conflict    # 中文：文件关系 / 规则冲突
                     修改 / 替代 / 冲突关系检查
                                  │
                       ┌──────────┴──────────┐
                       ▼                     ▼
                  Conflict / Unknown      Resolved    # 中文：冲突 / 未知状态 → 已解决后继续
                    冲突 / 未知             已解析
                       │                     │
                       ▼                     ▼
                  Human Review        Applicable Policy Set    # 中文：人工复核适用政策 / 法规集合
                   人工复核             适用政策集合
                                             │
                                             ▼
                                      Policy Snapshot    # 中文：政策法规快照
                                        版本快照
                                             │
                                             ▼
                                      Compliance Finding    # 中文：合规发现项
                                       合规发现项法源
```

脑中最后只留一句：

> **政府采购 Legal AI 的核心不是“搜到法规”，而是把法规来源、条文、可执行规则、辖区、生效区间、业务事件时间、例外、修改废止关系和冲突状态全部结构化，再把每一个合规 Finding 绑定到一个可复现的 Policy Snapshot；只有这样，Legal RAG 找到的文本才有资格变成真正的 Applicable Legal Basis。**

---

# 第十一课 · 第 2 阶段掌握测试

现在不回看正文，你应该能够解释：

```text
为什么 Policy Registry 不等于向量数据库？

Source Document、Provision、Executable Rule 有什么区别？

为什么发布时间和生效时间必须分开？

Current Status 和 Historical Applicability 为什么不能混？

为什么法规更新不能直接覆盖旧版本？

为什么 Project Date 不够，要绑定 Business Event Time？

为什么地方文件被 RAG 检索到，不等于它能作为全国项目法源？

Rule Applicability 至少需要哪些维度？

为什么 Exception 必须是 Rule Object 的一部分？

为什么 Policy Conflict 不能让 LLM 自己挑一个答案？

D01-D22 在 Registry 中属于 Source 还是 Rule Layer？

为什么 2025 附件9、2026专项整治通知都应该保留？

为什么国办发〔2025〕34号特别能说明 Publication 与 Effective 的区别？

为什么财库〔2026〕2号既要进入 Legal RAG，也要进入 Rule Engine？

Legal RAG 和 Policy Registry 的职责分别是什么？

为什么每次 Finding 必须绑定 Policy Snapshot？

Legal Basis、Inspection Rule、Enforcement Case 为什么必须三层分离？
```

如果这些能够完整解释：

\[
\boxed{
第十一课第2阶段真正掌握
}
\]

---

# 下一阶段：第十一课 · 第 3 阶段
# 采购文件业务解剖：Qualification、Technical、Commercial、Scoring、Contract
## AI 怎样知道一段文字究竟属于采购需求、资格条件、实质性条款、技术需求、商务要求、评分项还是合同要求？

下一阶段最关键的边界：

\[
\boxed{
TextChunk
\neq
BusinessClause
}
\]

**中文业务释义：** 检索文本块 ≠ 政府采购业务条款。

并建立：

# `ProcurementDocumentSchema_V1`
