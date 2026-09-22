# 第十一课 · 第 1 阶段
# 业务目标与系统边界：政府采购合规 AI 到底要做什么？
## 先定义“什么叫完成、什么叫可靠、什么必须交给人”，再决定模型、RAG、规则和 Agent 应该怎么做

> **中文阅读增强说明（本次修订新增）**：为方便中国政府采购业务人员、合规人员和工程人员共同阅读，本阶段所有关键英文工程字段、状态值、流程节点和 Schema 标识均保留原英文名称，并在同一代码块中增加 `# 中文：...` 的业务释义。英文名称用于后续数据库、JSON/YAML、API 和程序实现保持稳定；中文释义用于说明它在政府采购合规审查中的实际含义。


前十课，我们已经分别建立了：

```text
Machine Learning    # 中文：机器学习
机器学习基础

Transformer / LLM    # 中文：Transformer / 大语言模型
大模型基础

Data Engineering    # 中文：数据工程
数据工程

SFT / LoRA / QLoRA    # 中文：监督微调 / LoRA / QLoRA 参数高效微调
监督微调

RAG    # 中文：检索增强生成
检索增强生成

Agent / Tool Calling    # 中文：智能体 / 工具调用
智能体与工具调用

CPT    # 中文：继续预训练（Continued Pretraining）
领域继续预训练

Gold Benchmark    # 中文：金标准评测基准
评测与可靠性

Production Serving    # 中文：生产推理服务
生产部署与MLOps
```

现在进入最后一课。

第十一课不再从：

```text
选哪个模型？
要不要LoRA？
RAG用哪个Embedding？
```

开始。

而是先回答一个更高层的问题：

> **我们到底要交付一个什么样的政府采购合规系统？**

因为如果这个问题没有定义清楚，

后面的：

```text
Dataset    # 中文：数据集
Rule Engine    # 中文：规则引擎
RAG    # 中文：检索增强生成
SFT    # 中文：监督微调
Agent    # 中文：智能体
Benchmark    # 中文：评测基准
Deployment    # 中文：部署
```

都会失去统一目标。

所以本阶段第一条核心边界是：

\[
\boxed{
AIProject
\neq
ModelProject
}
\]

**中文业务释义：** AI业务项目 ≠ 单纯模型项目。

本阶段最终形成：

# `ProcurementComplianceProductSpec_V1`

它是后面 15 个阶段共同遵守的：

# Product Contract
## 产品契约

也就是说：

> **先把政府采购合规 AI 的职责、边界、输入、输出、证据、完成条件、人工边界和质量要求锁死，再开始设计具体技术。**

---

# 一、先定义第十一课真正的最终产品

我们最终不是要交付：

```text
一个会聊天的政府采购模型
```

也不是：

```text
一个能把采购文件总结一下的LLM
```

而是一个：

# Government Procurement Compliance Review System
## 政府采购合规审查系统

它接收：

```text
采购公告
采购文件
采购需求
资格条件
实质性条款
技术要求
商务要求
评分标准
合同条款
相关附件
```

输出：

```text
结构化审查结果
风险发现项
规则命中
法律 / 政策依据
证据原文
文档定位
判断理由
例外条件
修改建议
人工复核状态
最终审查报告
```

所以：

\[
\boxed{
Input
\neq
PromptOnly
}
\]

**中文业务释义：** 系统输入 ≠ 仅有Prompt提示词。

真正输入是：

> **一组政府采购业务文档 + 项目上下文 + 适用政策上下文。**

而：

\[
\boxed{
Output
\neq
FreeTextOnly
}
\]

**中文业务释义：** 系统输出 ≠ 仅自由文本输出。

真正输出必须是：

> **可结构化、可定位、可复核、可审计的 Compliance Findings。**

---

# 二、核心心智模型 ①
# `BusinessClaim` 必须先于 `ModelChoice`

第十一课第一步不是：

> “我们用哪个大模型？”

而是定义：

# Business Claim
## 业务能力声明

第一版可以定义为：

> **系统能够对政府采购采购文件实施合规性预审，识别采购需求、资格条件、实质性条款、技术要求、商务要求、评分标准、政策适用、竞争性要求等环节中的潜在违法违规或高风险问题；能够以“四类专项整治”中“采购人设置差别歧视条款”附件 9 的 7 类问题、22 项具体表现形式作为重要规则主轴；能够定位采购文件原文、匹配适用规则与法源、说明判断理由、检查例外条件、给出修改建议，并将不确定、冲突、高风险或需要裁量的事项升级人工复核。**

这个 Business Claim 一旦确定，

后面的技术选择都要围绕它服务。

所以：

\[
\boxed{
Model
服务于
BusinessClaim
}
\]

而不是：

\[
\boxed{
Business
迁就
ModelCapability
}
\]

---

# 三、为什么必须明确“预审”而不是“自动最终裁决”？

政府采购合规审查中存在大量：

```text
法律适用
事实认定
项目必要性
业务合理性
例外条件
裁量判断
```

这些问题不适合全部交给模型做最终不可逆决定。

因此产品第一版更专业的定位是：

# Compliance Pre-review
## 合规预审

系统负责：

```text
发现问题
定位证据
匹配规则
组织法源
给出风险解释
生成修改建议
提示不确定性
创建人工复核任务
```

而不是宣称：

> “AI 自动作出最终法律认定。”

所以：

\[
\boxed{
AIRecommendation
\neq
FinalLegalDetermination
}
\]

**中文业务释义：** AI建议 ≠ 最终法律认定。

---

# 四、核心心智模型 ②
# `AutomationBoundary` 必须在产品设计阶段确定

如果不提前规定哪些事情：

```text
AI可以自动完成
AI可以建议
必须人工确认
系统必须拒绝判断
```

后面 Agent 就容易：

> 越权。

所以 Product Spec 必须定义：

# Automation Boundary
## 自动化边界

例如：

| 类型 | 系统行为 |
|---|---|
| 明确文本定位 | 可自动 |
| D01-D22 候选规则匹配 | 可自动 |
| 确定性金额 / 比例 / 日期计算 | 可自动 |
| 法规版本检索 | 可自动，但需来源验证 |
| 是否具有项目实际必要性 | AI分析 + 证据 + 可能人工 |
| 复杂例外判断 | AI建议 + 人工复核 |
| 高风险最终认定 | 默认人工确认 |
| 法源无法确认 | 不得强行下结论 |

因此：

\[
\boxed{
CanAutomate
\neq
ShouldAutomate
}
\]

**中文业务释义：** 技术上能够自动化 ≠ 业务上适合自动化。

---

# 五、系统到底检查什么？

第一版 Product Scope
## 产品检查范围

至少覆盖以下层级：

```text
1. Procurement Requirement    # 中文：采购需求
采购需求

2. Qualification    # 中文：资格条件
资格条件

3. Substantive Requirement    # 中文：实质性要求
实质性条款

4. Technical Requirement    # 中文：技术要求
技术要求

5. Commercial Requirement    # 中文：商务要求
商务要求

6. Scoring Criteria    # 中文：评分标准
评分标准

7. Procurement Policy    # 中文：政府采购政策
政府采购政策

8. Competition / Procurement Method    # 中文：竞争性 / 采购方式
竞争性与采购方式

9. Contract / Performance    # 中文：合同 / 履约
合同与履约要求

10. D01-D22    # 中文：D01D22
附件9差别歧视22项具体表现形式
```

其中：

\[
\boxed{
D01\sim D22
}
\]

**中文业务释义：** D01规则～ D22规则。

不是一个孤立模块。

而应该横跨：

```text
采购需求
资格要求
实质性条款
评分标准
技术条件
商务条件
```

进行检查。

---

# 六、核心心智模型 ③
# `ComplianceScope` 必须是显式的

如果系统只检查：

```text
资格条件
```

却对外说：

> “完成采购文件合规检查。”

这是错误的产品定义。

因此：

\[
\boxed{
CheckedScope
\neq
WholeDocumentClaim
}
\]

**中文业务释义：** 已完成检查的范围 ≠ 整份采购文件合规声明。

每次报告必须明确：

```text
检查了什么
没有检查什么
哪些部分无法解析
哪些规则没有适用
哪些部分需要人工
```

---

# 七、检查对象不是“整份文档”，而是多层 Evaluation Unit

一份采购文件是：

# Document
## 文档

但真正的合规判断通常落在：

# Clause
## 条款

甚至：

# Requirement
## 单个要求

最终形成：

# Finding
## 合规发现项

所以系统至少需要四层对象：

```text
Project    # 中文：采购项目
项目

Document    # 中文：采购文档
文档

Clause    # 中文：条款
条款

Finding    # 中文：合规发现项
发现项
```

可以表示为：

\[
\boxed{
Project
\rightarrow
Document
\rightarrow
Clause
\rightarrow
Finding
}
\]

**中文业务释义：** 采购项目 → 采购文件 → 业务条款 → 合规发现项。

---

# 八、核心心智模型 ④
# `DocumentLevelScore` 不能替代 `ClauseLevelEvidence`

如果最终只输出：

```text
这份文件风险较高
```

用户无法知道：

```text
哪里有问题？
哪一条？
命中了什么规则？
为什么？
怎么改？
```

所以：

\[
\boxed{
ComplianceDecision
必须落到
Clause / Evidence
}
\]

---

# 九、每一个 Finding 必须是什么结构？

一个成熟的：

# Compliance Finding
## 合规发现项

不能只有：

```text
risk = true    # 中文：风险 = 正确 / 真
```

至少要包含：

```text
finding_id    # 中文：发现项标识
project_id    # 中文：项目标识
document_id    # 中文：文档标识
clause_id    # 中文：条款标识
document_location    # 中文：文档位置 / 地域
clause_text    # 中文：条款文本
review_domain    # 中文：审查业务域
rule_id    # 中文：规则标识
primary_category    # 中文：一级问题类别
manifestation    # 中文：具体表现形式
risk_level    # 中文：风险等级
legal_basis    # 中文：法律 / 政策依据
policy_version    # 中文：政策 / 法规版本
jurisdiction    # 中文：辖区
effective_status    # 中文：生效状态
reasoning_summary    # 中文：判断理由摘要
business_necessity    # 中文：业务必要性
competition_impact    # 中文：竞争影响
exception_status    # 中文：例外状态
evidence_span    # 中文：证据片段及原文定位
recommended_revision    # 中文：建议修改方案
confidence    # 中文：置信度
human_review_required    # 中文：是否需要人工复核
human_review_status    # 中文：人工复核状态
audit_status    # 中文：审计状态
```

因此：

\[
\boxed{
Finding
\neq
Label
}
\]

**中文业务释义：** 合规发现项 ≠ 标签。

更准确的是：

\[
\boxed{
Finding
=
Decision
+
Evidence
+
Basis
+
Reason
+
Remediation
+
ReviewState
}
\]

**中文业务释义：** 合规发现项 = 判断结论 + 证据 + 依据 + 判断理由 + 修改建议 + 复核状态。

---

# 十、D01-D22 在 Product Spec 里的角色

附件 9 的 22 项具体表现形式，

在 V1.0 里必须成为：

# Mandatory Coverage Axis
## 强制覆盖轴

也就是说：

> 每一份属于适用范围的采购文件，都必须形成 D01-D22 的检查状态。

不能只记录：

```text
命中了D07
```

还要知道：

```text
D01 checked    # 中文：D01已检查
D02 checked    # 中文：D02已检查
...
D22 checked    # 中文：D22已检查
```

所以：

\[
\boxed{
NoHit
\neq
NotChecked
}
\]

**中文业务释义：** 未命中风险规则 ≠ 尚未检查。

这是非常重要的一条。

---

# 十一、核心心智模型 ⑤
# `NoFinding` 和 `NoReview` 必须彻底区分

如果报告显示：

```text
D13 = 无风险
```

必须意味着：

> 系统确实检查过 D13。

而不能意味着：

> 系统没看见，所以默认无风险。

因此每个 Rule 至少要有状态：

```text
NOT_STARTED    # 中文：尚未开始检查
CHECKED_NO_FINDING    # 中文：已检查，未发现风险
POTENTIAL_FINDING    # 中文：潜在风险发现项
NEEDS_HUMAN_REVIEW    # 中文：需要人工复核
CONFIRMED_FINDING    # 中文：已确认风险发现项
NOT_APPLICABLE    # 中文：不适用
UNRESOLVED    # 中文：无法确定 / 待解决
```

这样：

\[
\boxed{
ReviewState
\neq
RiskLabel
}
\]

**中文业务释义：** 复核状态 ≠ 风险标签。

---

# 十二、Applicable Policy 必须先于最终判断

同一句采购条款，

在不同：

```text
时间
地区
政策版本
项目类型
采购方式
```

下，

适用规则可能不同。

所以系统在做较高等级结论前，

必须先解决：

# Applicable Policy
## 适用政策

至少需要：

```text
jurisdiction_resolved    # 中文：辖区已解决
project_date_resolved    # 中文：项目日期已解决
policy_version_resolved    # 中文：政策 / 法规版本已解决
policy_status_resolved    # 中文：政策 / 法规状态已解决
```

因此：

\[
\boxed{
RuleMatch
WithoutApplicablePolicy
=
IncompleteDecision
}
\]

**中文业务释义：** 规则匹配 缺少适用政策确认 = 不完整判断。

---

# 十三、核心心智模型 ⑥
# `LatestPolicy ≠ ApplicablePolicy`

系统不能简单：

> 永远检索最新文件。

真正需要的是：

\[
\boxed{
ApplicablePolicy
=
Authority
+
Jurisdiction
+
EffectiveTime
+
SubjectMatter
}
\]

**中文业务释义：** 适用政策 / 适用法规 = 效力层级 / 制定主体 + 适用辖区 + 生效时间 + 适用事项。

如果：

```text
适用地区未知
项目时间未知
法规状态未知
```

系统应该：

> 暂停高置信最终结论。

而不是：

> 强行补全。

---

# 十四、Evidence Contract：每一个风险结论都必须能“落地到证据”

第十一课要建立：

# Evidence Contract
## 证据契约

任何高风险 Finding 至少回答：

```text
采购文件哪一段？
在哪一页 / 哪一章 / 哪一个Clause？
匹配哪一个D01-D22 Rule？
对应什么法源？
对应哪个版本？
为什么当前上下文满足触发条件？
有没有例外？
```

所以：

\[
\boxed{
LegalCitation
\neq
LegalSupport
}
\]

**中文业务释义：** 法条引用 ≠ 法条对当前结论的实质支持。

只是贴一个法条链接：

> 不等于这个法条真的支持当前判断。

---

# 十五、核心心智模型 ⑦
# `Evidence` 必须双向连接

至少同时有：

```text
Finding    # 中文：合规发现项
→ Procurement Clause    # 中文： → 采购条款

Finding    # 中文：合规发现项
→ Legal / Policy Basis    # 中文： → 法定政策 / 法规依据
```

也就是：

\[
\boxed{
Finding
\leftrightarrow
BusinessEvidence
}
\]

**中文业务释义：** 合规发现项 ↔ 采购业务证据。

和：

\[
\boxed{
Finding
\leftrightarrow
LegalEvidence
}
\]

**中文业务释义：** 合规发现项 ↔ 法律政策证据。

这样才形成：

# Evidence Chain
## 证据链

---

# 十六、规则命中为什么不能直接等于违法？

例如系统发现：

```text
“供应商须在本市设立服务机构”
```

它可能命中某个地域限制候选模式。

但还需要继续判断：

```text
这是投标前条件还是中标后履约要求？
是否确有项目实际需要？
是否有明确政策 / 法律依据？
是否存在合理例外？
是否真正限制潜在供应商公平参与？
```

所以：

\[
\boxed{
RuleHit
\neq
FinalViolation
}
\]

**中文业务释义：** 规则命中 ≠ 最终违规认定。

必须经过：

\[
\boxed{
RuleHit
\rightarrow
Context
\rightarrow
Necessity
\rightarrow
Exception
\rightarrow
Evidence
\rightarrow
Decision
}
\]

**中文业务释义：** 规则命中 → 业务上下文 → 必要性 → 例外 → 证据 → 判断结论。

---

# 十七、核心心智模型 ⑧
# `Requirement ≠ Restriction`

政府采购文件天然会提出：

```text
资格要求
技术要求
服务要求
履约要求
```

不是所有要求：

> 都是不合理限制。

真正要区分：

\[
\boxed{
NecessaryRequirement
vs
UnreasonableExclusion
}
\]

**中文业务释义：** 必要要求 vs 不合理排斥。

因此模型必须学：

> Decision Boundary。

而不是只学：

> 敏感词。

---

# 十八、为什么 Deterministic Rule 必须优先走 Calculator？

部分合规问题是：

```text
金额
比例
日期
价格差
数量
阈值
```

这类问题应该优先交给：

# Deterministic Rule / Calculator
## 确定性规则 / 计算器

而不是让 LLM 自由生成。

所以：

\[
\boxed{
DeterministicRule
\Rightarrow
CalculatorFirst
}
\]

**中文业务释义：** 确定性规则 ⇒ 优先使用确定性计算器。

LLM 更适合：

```text
语义解释
上下文关联
合理性判断
例外解释
证据组织
```

---

# 十九、核心心智模型 ⑨
# `LLM ≠ ComplianceEngine`

真正的：

# Compliance Engine
## 合规引擎

应该是：

\[
\boxed{
Rules
+
PolicyRegistry
+
LegalRAG
+
Calculator
+
LLM
+
Agent
+
Human
}
\]

**中文业务释义：** 规则集合 + 政策法规注册表 + 法规RAG检索 + 计算器 + 大语言模型 + Agent + 人工专家。

因此第十一课永远不会把架构简化成：

```text
Document    # 中文：采购文档
↓
LLM    # 中文：大语言模型
↓
Answer    # 中文：答案 / 输出
```

---

# 二十、Risk Level 怎么设计？

不能只有：

```text
违规
不违规
```

可以先定义：

```text
R0    # 中文：未发现风险
未发现风险

R1    # 中文：提示性 / 低风险
提示性风险 / 低风险

R2    # 中文：中风险，需要复核
需要复核的中风险

R3    # 中文：高风险候选
高度疑似违规 / 高风险

R4    # 中文：重大高风险，必须人工确认
严重风险 / 必须人工确认
```

但必须注意：

> Risk Level 是产品风险分级，不等于最终行政执法定性。

所以：

\[
\boxed{
RiskLevel
\neq
LegalPenaltyConclusion
}
\]

**中文业务释义：** 风险Level ≠ 法律PenaltyConclusion。

---

# 二十一、Confidence 和 Risk Level 是两回事

一个 Finding 可以：

```text
Risk = High    # 中文：风险 = 高
Confidence = Low    # 中文：置信度 = 低
```

意思是：

> 如果成立，风险很高；但当前证据不足。

也可能：

```text
Risk = Medium    # 中文：风险 = 中
Confidence = High    # 中文：置信度 = 高
```

所以：

\[
\boxed{
RiskSeverity
\neq
ModelConfidence
}
\]

**中文业务释义：** 风险严重程度 ≠ 模型置信度。

这两个字段必须分开。

---

# 二十二、核心心智模型 ⑩
# `HighRisk + LowConfidence` 更应该升级人工，而不是自动忽略

因此：

\[
\boxed{
HumanEscalation
=
Function(
Risk,
Confidence,
Evidence,
RuleType
)
}
\]

**中文业务释义：** 升级人工复核 = 功能( 风险, 置信度, 证据, 规则类型 )。

不是只看一个 confidence threshold。

---

# 二十三、Human Review 到底什么时候触发？

至少包括：

```text
高风险Finding

法源冲突

适用辖区不明确

项目时间不明确

需要判断“实际必要性”

存在例外但证据不完整

D01-D22中边界型Hard Case

模型与Rule Engine结论冲突

Legal RAG无法找到充分支持

涉及重大采购决策
```

所以：

\[
\boxed{
HumanReview
不是系统失败
}
\]

而是：

# Risk Control Mechanism
## 风险控制机制

---

# 二十四、核心心智模型 ⑪
# `Abstention` 在合规产品里是一种专业行为

如果：

```text
证据不足
法源不确定
文档解析失败
```

系统应该输出：

```text
UNRESOLVED    # 中文：无法确定 / 待解决
NEEDS_HUMAN_REVIEW    # 中文：需要人工复核
```

而不是：

> 编一个确定答案。

所以：

\[
\boxed{
Unknown
>
FalseCertainty
}
\]

**中文业务释义：** Unknown > FalseCertainty。（这里的 `>` / `<` 若用于心智模型，表示工程优先级或信息价值关系，不一定是数学数值大小。）

这里的 `>` 表示：

> 在高风险合规系统中更安全、更专业。

---

# 二十五、什么叫“合规检查完成”？

这是 Product Spec 最核心的定义之一。

不能因为：

```text
生成了一份报告
```

就说任务完成。

必须定义：

# Completion Criteria
## 完成条件

第一版至少包括：

```text
project_identified    # 中文：项目已识别并建立项目标识

document_ingestion_complete    # 中文：采购文件接收 / 导入完成

document_parse_complete    # 中文：文档解析完成

jurisdiction_resolved    # 中文：辖区已解决

project_date_resolved    # 中文：项目日期已解决

policy_version_resolved    # 中文：政策 / 法规版本已解决

procurement_requirement_review_done    # 中文：采购要求复核已完成

qualification_review_done    # 中文：资格复核已完成

substantive_clause_review_done    # 中文：实质性条款复核已完成

technical_review_done    # 中文：技术复核已完成

commercial_review_done    # 中文：商务复核已完成

scoring_review_done    # 中文：评分复核已完成

policy_review_done    # 中文：政策 / 法规复核已完成

competition_review_done    # 中文：竞争复核已完成

contract_review_done    # 中文：合同复核已完成

D01_D22_review_done    # 中文：D01D22复核已完成

evidence_map_complete    # 中文：证据映射完成

unresolved_items_explicit    # 中文：未解决事项明确

human_review_items_created    # 中文：人工复核事项已创建

final_report_generated    # 中文：最终报告已生成

audit_record_complete    # 中文：审计记录完成
```

只有满足必要条件：

\[
\boxed{
ReviewComplete=True
}
\]

**中文业务释义：** 复核完成=True。

---

# 二十六、核心心智模型 ⑫
# `ReportGenerated ≠ ReviewComplete`

生成 PDF / Word：

> 只是输出动作。

真正完成必须证明：

```text
应该检查的内容都检查了
没检查的内容明确标记
不确定项没有被掩盖
证据链完整
人工任务已经创建
```

---

# 二十七、系统必须有 State Machine

可以把审查任务设计成：

```text
CREATED    # 中文：任务已创建
↓
INGESTING    # 中文：正在接收 / 导入文档
↓
PARSING    # 中文：正在解析文档
↓
POLICY_RESOLUTION    # 中文：正在解析适用法规
↓
REVIEWING    # 中文：正在进行合规审查
↓
EVIDENCE_VALIDATION    # 中文：正在验证证据
↓
HUMAN_REVIEW    # 中文：人工复核阶段
↓
REPORTING    # 中文：正在生成报告
↓
COMPLETED    # 中文：已完成
```

还允许：

```text
FAILED    # 中文：执行失败
PARTIAL    # 中文：部分完成 / 部分解析
BLOCKED    # 中文：流程被阻塞
UNRESOLVED    # 中文：无法确定 / 待解决
```

所以：

\[
\boxed{
WorkflowState
\neq
ChatHistory
}
\]

**中文业务释义：** Workflow状态 ≠ ChatHistory。

真正状态必须由系统持久化。

---

# 二十八、用户角色也必须在 Product Spec 中明确

至少考虑：

```text
采购人
采购代理机构
内部合规人员
财政监管 / 审核人员
项目负责人
法律 / 业务专家
系统管理员
模型 / 规则维护人员
```

不同角色：

> 能看到的内容、能确认的 Finding、能修改的 Rule、能否 Override 结论都不同。

所以：

\[
\boxed{
SameFinding
\neq
SamePermission
}
\]

**中文业务释义：** 相同发现项 ≠ 相同Permission。

---

# 二十九、Override 必须可审计

如果人工把：

```text
AI = High Risk    # 中文：AI = 高风险
```

改成：

```text
Human = No Finding    # 中文：人工 = 无 / 否发现项
```

系统应该记录：

```text
who    # 中文：由谁执行 / 操作人
when    # 中文：执行 / 修改时间
before    # 中文：之前
after    # 中文：之后
reason    # 中文：原因 / 说明
evidence    # 中文：证据
policy_version    # 中文：政策 / 法规版本
```

因此：

\[
\boxed{
HumanOverride
\Rightarrow
AuditTrail
}
\]

**中文业务释义：** HumanOverride ⇒ 审计链。

---

# 三十、False Negative 和 False Positive 在这里代价不同

# False Negative
## 漏检

真实存在高风险，

系统没有发现。

# False Positive
## 误报

实际没有问题，

系统报了风险。

在政府采购合规预审里：

> 高风险漏检通常需要非常重视。

但误报过多也会导致：

```text
人工复核负担
业务效率下降
用户失去信任
```

所以 Product Spec 必须定义：

\[
\boxed{
RiskCost
\neq
SimpleAccuracy
}
\]

**中文业务释义：** 风险Cost ≠ Simple准确率。

后面 Benchmark 会对：

```text
Critical Risk Recall    # 中文：关键风险召回率
False Positive Rate    # 中文：错误 / 假正例比例
D01-D22 Per-rule Recall    # 中文：D01D22逐项 / 每规则召回率
```

分别控制。

---

# 三十一、核心心智模型 ⑬
# `OverallAccuracy ≠ ComplianceReliability`

即使总体：

```text
Accuracy = 95%    # 中文：准确率 = 95
```

如果：

```text
D17高风险规则Recall = 40%
```

系统仍然可能不能上线。

因此：

\[
\boxed{
CriticalCoverage
>
AverageScore
}
\]

**中文业务释义：** Critical覆盖 > AverageScore。（这里的 `>` / `<` 若用于心智模型，表示工程优先级或信息价值关系，不一定是数学数值大小。）

这里表示：

> 在发布决策中关键风险覆盖优先级更高。

---

# 三十二、产品必须输出“已知未知”

最终报告不能只分：

```text
有风险
无风险
```

还必须明确：

```text
Known Finding    # 中文：已确认的发现项
已确认发现

Potential Finding    # 中文：潜在发现项
潜在发现

Not Applicable    # 中文：未 / 不适用
不适用

Checked No Finding    # 中文：已检查无 / 否发现项
已检查未发现

Unresolved    # 中文：无法确定 / 待解决
无法解决

Needs Human Review    # 中文：需要人工复核
需人工复核

Parse Failure    # 中文：解析失败 / 不满足
解析失败
```

所以：

\[
\boxed{
UnknownState
必须显式建模
}
\]

---

# 三十三、核心心智模型 ⑭
# `Silence ≠ Compliance`

系统没有输出风险：

> 不等于采购文件就合规。

可能是：

```text
没有检查
解析失败
规则不适用
证据不足
系统漏检
```

因此最终报告必须同时包含：

# Coverage Report
## 覆盖情况

回答：

> **哪些地方确实检查过？**

---

# 三十四、产品验收必须从“演示效果”升级成 Acceptance Criteria

第十一课最终不能用：

```text
看起来挺聪明
```

作为验收标准。

至少要定义：

# Acceptance Criteria
## 验收条件

包括：

```text
D01-D22全部进入规则覆盖矩阵

采购需求 / 资格 / 技术 / 商务 / 评分等域均有明确Review State

高风险Finding必须有文档证据

高风险Finding必须有规则 / 法源依据

法源必须带版本、辖区和适用状态

Unresolved必须显式输出

人工复核可以闭环

Finding可回溯到Clause

报告可回溯到Finding

Finding可回溯到Rule

Rule可回溯到Source

版本变更可追踪

系统能被Benchmark重复评测
```

因此：

\[
\boxed{
DemoSuccess
\neq
ProductAcceptance
}
\]

**中文业务释义：** DemoSuccess ≠ 产品Acceptance。

---

# 三十五、本阶段正式工程产物
# `ProcurementComplianceProductSpec_V1`

第一版至少锁定：

```text
product_spec_version    # 中文：产品规格版本
product_name    # 中文：产品名称
business_claim    # 中文：业务能力声明
product_positioning    # 中文：产品定位
target_users    # 中文：目标用户
user_roles    # 中文：用户角色
review_scope    # 中文：复核范围
out_of_scope    # 中文：不在本产品审查范围内的事项
supported_document_types    # 中文：支持的采购文档类型
project_context_schema    # 中文：项目上下文结构定义
jurisdiction_scope    # 中文：辖区范围
policy_scope    # 中文：政策 / 法规范围
D01_D22_required    # 中文：D01D22是否需要
review_domains    # 中文：合规审查业务域
evaluation_units    # 中文：评审单元
finding_schema    # 中文：发现项结构定义
risk_level_schema    # 中文：风险等级结构定义
confidence_schema    # 中文：置信度结构定义
review_state_schema    # 中文：复核状态结构定义
evidence_contract    # 中文：证据合同
legal_basis_contract    # 中文：法律 / 政策依据合同
applicable_policy_requirement    # 中文：适用政策 / 法规要求
exception_handling    # 中文：例外处理
business_necessity_analysis    # 中文：业务必要性分析
deterministic_rule_boundary    # 中文：确定性规则的适用边界
llm_boundary    # 中文：大语言模型边界
agent_boundary    # 中文：智能体自动执行边界
human_review_policy    # 中文：人工复核政策 / 法规
human_override_policy    # 中文：人工覆盖 / 改判策略
completion_criteria    # 中文：任务完成条件
workflow_state_machine    # 中文：工作流状态机
coverage_report    # 中文：覆盖报告
audit_trail    # 中文：审计轨迹 / 审计链
acceptance_criteria    # 中文：产品验收条件
benchmark_requirements    # 中文：评测基准要求
release_constraints    # 中文：发布限制 / 上线约束
```

这份 Product Spec 是后续所有阶段的根。

后面：

```text
Policy Registry    # 中文：政策法规登记库
Document Schema    # 中文：文档结构定义
D01-D22 RuleSet    # 中文：D01D22规则集
Dataset    # 中文：数据集
Legal RAG    # 中文：法规检索增强生成
SFT    # 中文：监督微调
Agent    # 中文：智能体
Benchmark    # 中文：评测基准
Deployment    # 中文：部署
```

全部必须能回指：

> 它服务的是哪个 Product Requirement。

---

# 三十六、本阶段最重要的 14 个核心心智模型

> **心智模型 ①：`AIProject ≠ ModelProject`。第十一课交付的是业务系统，不是单个模型。**

> **心智模型 ②：`BusinessClaim → ModelChoice`。先定义要证明的业务能力，再选择模型与技术。**

> **心智模型 ③：`AIRecommendation ≠ FinalLegalDetermination`。AI 做合规预审和证据组织，高风险最终认定保留人工边界。**

> **心智模型 ④：`CanAutomate ≠ ShouldAutomate`。能自动做，不代表应该让系统自动做最终决定。**

> **心智模型 ⑤：`CheckedScope ≠ WholeDocumentClaim`。检查范围必须显式，不能局部检查却声称全文件合规。**

> **心智模型 ⑥：`Finding ≠ Label`。完整 Finding 必须包含判断、证据、法源、理由、修改建议和复核状态。**

> **心智模型 ⑦：`NoHit ≠ NotChecked`。没有命中规则和根本没有检查，是完全不同的状态。**

> **心智模型 ⑧：`LatestPolicy ≠ ApplicablePolicy`。真正适用规则由效力层级、辖区、时间和事项共同决定。**

> **心智模型 ⑨：`RuleHit ≠ FinalViolation`。规则命中后还必须检查上下文、必要性、例外和证据。**

> **心智模型 ⑩：`Requirement ≠ Restriction`。系统真正要学习的是合理要求和不合理排斥之间的 Decision Boundary。**

> **心智模型 ⑪：`LLM ≠ ComplianceEngine`。真正合规引擎是 Rules + Policy Registry + RAG + Calculator + LLM + Agent + Human。**

> **心智模型 ⑫：`RiskSeverity ≠ Confidence`。风险后果和模型确定程度必须分开建模。**

> **心智模型 ⑬：`ReportGenerated ≠ ReviewComplete`。只有必要检查、D01-D22覆盖、证据、不确定项和人工任务都完成，审查才算完成。**

> **心智模型 ⑭：`Silence ≠ Compliance`。没有发现风险并不自动等于合规，必须同时报告 Coverage、Parse State 和 Unresolved State。**

---

# 三十七、把整个 Product Spec 压成一张专业工程图

```text
                       Business Claim    # 中文：业务能力声明
                       定义业务能力
                              │
                              ▼
                         Review Scope    # 中文：复核范围
                         锁定检查范围
                              │
                              ▼
                      Project / Document    # 中文：采购项目 / 采购文档
                       项目与采购文件
                              │
                              ▼
                        Policy Context    # 中文：政策 / 法规上下文
                   辖区 / 时间 / 法规版本
                              │
                              ▼
                         Clause Units    # 中文：条款单元
                          条款级对象
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
             D01-D22     Domain Review    Deterministic    # 中文：D01-D22 规则覆盖 / 业务域审查 / 确定性规则计算
           差别歧视规则     业务域检查       Rules/Calc
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                          Rule Match    # 中文：规则匹配
                           候选命中
                              │
                              ▼
                     Context / Necessity    # 中文：上下文 / 必要性
                      上下文与实际必要性
                              │
                              ▼
                       Exception Check    # 中文：例外检查
                          例外检查
                              │
                              ▼
                        Evidence Chain    # 中文：证据链
                    采购原文 + 法规依据
                              │
                              ▼
                      Compliance Finding    # 中文：合规发现项
                    风险 + 理由 + 修改建议
                              │
                   ┌──────────┴──────────┐
                   ▼                     ▼
            Auto-resolvable        Human Review    # 中文：可自动闭环的事项 / 需要人工复核的事项
             可自动闭环              人工复核
                   │                     │
                   └──────────┬──────────┘
                              ▼
                       Completion Check    # 中文：完成检查
                         完成条件检查
                              │
                              ▼
                    Coverage + Final Report    # 中文：覆盖最终报告
                      覆盖报告 + 最终报告
                              │
                              ▼
                           Audit Trail    # 中文：审计轨迹 / 审计链
                            审计链
```

脑中最后只留一句：

> **第十一课的第一步不是训练模型，而是把“政府采购合规审查完成”定义成一个可以被机器验证的业务状态：检查范围明确、D01-D22 必须有 Review State、每个 Finding 必须有采购原文和规则/法源证据、不确定事项必须显式、关键判断必须能够升级人工、最终报告必须可追溯到 Clause、Rule、Policy 和 Review State。**

---

# 第十一课 · 第 1 阶段掌握测试

现在不回看正文，你应该能够解释：

```text
为什么 AIProject 不等于 ModelProject？

Business Claim 为什么必须先于 Model Choice？

为什么政府采购合规系统第一版更适合定义为“合规预审”？

Automation Boundary 为什么必须提前定义？

为什么 Checked Scope 不能冒充 Whole Document Compliance？

Project / Document / Clause / Finding 四层对象分别是什么？

为什么 Finding 不能只是一个风险标签？

为什么 D01-D22 必须同时有 Review State，而不是只记录命中的 Rule？

No Finding 与 Not Checked 为什么必须区分？

为什么 Applicable Policy 必须在最终判断之前解决？

Evidence Contract 为什么需要同时连接采购文件证据和法规证据？

为什么 Rule Hit 不等于 Final Violation？

Requirement 与 Restriction 的真正边界是什么？

为什么 Deterministic Rule 应优先走 Calculator？

为什么 LLM 不能等同于 Compliance Engine？

Risk Severity 和 Model Confidence 为什么必须分开？

什么时候必须 Human Review？

为什么 Report Generated 不等于 Review Complete？

为什么 Silence 不等于 Compliance？

Acceptance Criteria 为什么必须取代“Demo看起来不错”？
```

如果这些能够完整解释：

\[
\boxed{
第十一课第1阶段真正掌握
}
\]

---

# 下一阶段：第十一课 · 第 2 阶段
# 法规知识体系与 Policy Registry：法律层级、辖区、生效时间、版本和冲突
## 怎样保证系统引用的不是“某个看起来相关的法规”，而是真正对当前采购项目具有适用性的规则？

下一阶段最关键的边界：

\[
\boxed{
LatestPolicy
\neq
ApplicablePolicy
}
\]

**中文业务释义：** 最新发布 / 当前最新政策 ≠ 适用政策 / 适用法规。

并建立：

# `ProcurementPolicyRegistry_V1`
