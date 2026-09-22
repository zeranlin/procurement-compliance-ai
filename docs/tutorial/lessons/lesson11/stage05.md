# 第十一课 · 第 5 阶段
# 资格条件与市场准入合规：地域、行业、所有制、规模、年限、财务、资质、业绩
## 怎样区分真正的履约能力要求与不合理市场准入门槛？怎样把“供应商必须具备什么”拆成可解释、可审计、可进入 D01-D22 Rule Engine 的资格审查对象？

> **中文阅读增强说明（本次修订新增）**：为方便中国政府采购业务人员、合规人员和工程人员共同阅读，本阶段所有关键英文工程字段、状态值、流程节点和 Schema 标识均保留原英文名称，并在同一代码块中增加 `# 中文：...` 的业务释义。英文名称用于后续数据库、JSON/YAML、API 和程序实现保持稳定；中文释义用于说明它在政府采购合规审查中的实际含义。


第 4 阶段我们已经把附件 9 的：

\[
\boxed{
7类问题
\rightarrow
D01\sim D22
}
\]

正式工程化为：

# `ProcurementDiscrimination22RuleSet_V1`

并建立：

\[
\boxed{
Trigger
\rightarrow
Candidate
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

**中文业务释义：** 触发条件 → 候选 → 业务上下文 → 必要性 → 例外 → 证据 → 判断结论。

现在进入这些规则最容易集中出现的业务区域之一：

# Qualification
## 供应商资格条件与市场准入

本阶段最重要的第一条边界：

\[
\boxed{
CapabilityRequirement
\neq
MarketAccessBarrier
}
\]

**中文业务释义：** 履约能力要求 ≠ 市场准入障碍。

采购人当然需要判断：

> 供应商有没有履行合同所需要的能力。

但如果把这种能力要求设计成：

```text
不必要的地域门槛
行业门槛
企业规模门槛
所有制门槛
成立年限门槛
财务指标门槛
特定金额业绩门槛
无依据证书门槛
名录库门槛
```

就可能从：

# Capability Check
## 履约能力检查

跨越成：

# Market Access Barrier
## 市场准入障碍

本阶段最终形成：

# `ProcurementQualificationCompliance_V1`

---

# 一、本阶段的正式业务依据是什么？

本阶段以：

```text
《2025年政府采购领域“四类”违法违规行为专项整治工作指引》
第二部分 检查规范
一、关于采购人设置差别歧视条款问题
及附件9
```

作为重要业务基线。

该工作指引要求重点检查：

```text
采购需求
资格要求
实质性条款
评分标准
```

并明确列出：

```text
地域限制
行业限制
企业规模限制
企业形式限制
指向特定供应商 / 产品
与项目无关或不必要的条件
其他不合理限制
```

等问题。

文件同时列示的处理依据包括：

```text
《中华人民共和国政府采购法》

《中华人民共和国政府采购法实施条例》

《中华人民共和国中小企业促进法》

《中华人民共和国外商投资法》

《中华人民共和国外商投资法实施条例》

《政府采购货物和服务招标投标管理办法》
财政部令第87号

《政府采购促进中小企业发展管理办法》
财库〔2020〕46号

《财政部关于促进政府采购公平竞争优化营商环境的通知》
财库〔2019〕38号

《财政部关于在政府采购活动中落实平等对待内外资企业有关政策的通知》
财库〔2021〕35号
```

但是：

> 本课程中的工程 Rule 不能把 2025 工作指引永久当成“当前有效性的唯一判断来源”。

生产系统中仍然必须通过：

# `ProcurementPolicyRegistry_V1`

确认：

```text
当前法规状态
适用时间
适用辖区
适用事项
后续修订 / 废止 / 替代
```

所以：

\[
\boxed{
InspectionBaseline
\neq
ForeverApplicablePolicy
}
\]

**中文业务释义：** 专项检查业务基线 ≠ 永远适用的政策。

---

# 二、先把“资格条件”定义清楚

# Qualification
## 资格条件

它解决的是：

> **供应商是否具备进入当前采购项目后续竞争程序的基本资格。**

所以资格条件是一种：

# Gate
## 准入门

如果供应商不满足：

> 通常不能继续进入后续评审。

因此：

\[
\boxed{
Qualification
=
EntryGate
}
\]

**中文业务释义：** 资格条件 = 准入门槛。

这和：

# Scoring
## 评分

完全不同。

评分解决的是：

> 已经通过资格 / 符合性检查的供应商之间怎样比较。

所以：

\[
\boxed{
QualificationGate
\neq
ScoringPreference
}
\]

**中文业务释义：** 资格准入门槛 ≠ 评分偏好 / 评分加分。

---

# 三、核心心智模型 ①
# “能不能参加”和“参加以后得多少分”必须分开

例如：

```text
具有三项同类项目业绩
```

如果作为：

```text
资格条件
```

表示：

> 没有就不能参加。

如果作为：

```text
评分因素
```

表示：

> 可以参加，但得分可能不同。

竞争影响完全不同。

所以任何 Requirement 都必须记录：

```text
business_function    # 中文：业务功能
=
ENTRY_GATE    # 中文：准入门槛
or    # 中文：或者
SCORING_FACTOR    # 中文：评分因素
or    # 中文：或者
PERFORMANCE_OBLIGATION    # 中文：履约义务
```

而不能只保存文字。

---

# 四、法定 / 通用条件与项目特定条件要分层

可以把资格条件粗分成：

# Baseline Eligibility
## 基础资格条件

与：

# Project-specific Qualification
## 项目特定资格条件

基础资格更像：

> 政府采购制度对供应商参与活动的通用要求。

项目特定条件则是：

> 因具体项目的特殊要求增加的条件。

真正容易出现合规风险的地方通常是：

\[
\boxed{
ProjectSpecificCondition
}
\]

**中文业务释义：** 项目特定条件。

因为它必须回答：

> **为什么这个项目真的需要这项门槛？**

所以：

\[
\boxed{
SpecialRequirement
\Rightarrow
ProjectSpecificJustification
}
\]

**中文业务释义：** 项目特定要求 ⇒ 项目特定理由。

---

# 五、核心心智模型 ②
# `ProjectSpecific` 不等于 `PurchaserPreference`

采购人觉得：

```text
“大企业更稳”
“本地企业服务更方便”
“成立久的公司更靠谱”
“做过大项目的公司更安全”
```

这些偏好：

> 不能直接成为资格门槛。

必须经过：

# Necessity Test
## 必要性检验

也就是：

\[
\boxed{
Preference
\neq
NecessaryQualification
}
\]

**中文业务释义：** 采购人偏好 ≠ 必要资格条件。

---

# 六、资格条件合规判断的“五问模型”

对任何新增的项目特定资格条件，先问五个问题：

## Question 1
# Objective
## 目标是什么？

这项条件到底要防什么风险？

例如：

```text
保证技术能力
保证履约响应
保证安全资质
保证法定许可
```

---

## Question 2
# Relevance
## 与项目是否直接相关？

即：

\[
\boxed{
Condition
\leftrightarrow
ProcurementNeed
}
\]

**中文业务释义：** 条件 ↔ 采购需求。

是否存在直接业务联系。

---

## Question 3
# Necessity
## 是否真的需要把它放到“准入门槛”？

即使某条件与项目有关，

也不一定必须：

> 在投标前全部满足。

---

## Question 4
# Proportionality
## 限制强度是否与风险相称？

例如：

> 为了保证售后响应，

是否真的需要：

```text
投标前已经在本市有分公司
```

还是：

```text
中标后建立满足响应时间的服务能力
```

就足以达到目的？

---

## Question 5
# Alternative
## 有没有更少排斥竞争的实现方式？

所以：

\[
\boxed{
QualificationNecessity
=
Objective
+
Relevance
+
Necessity
+
Proportionality
+
LessRestrictiveAlternative
}
\]

**中文业务释义：** 资格门槛必要性 = 目标 + 相关性 + 必要性 + 比例性 + 更少限制竞争的替代方案。

这不是法律公式。

它是：

> **工程系统必须收集和组织的判断信息。**

---

# 七、核心心智模型 ③
# `Relevant` 还不等于 `Necessary as Entry Gate`

一项条件可能：

> 和项目有关。

但不意味着：

> 必须在供应商报名 / 投标时就作为淘汰条件。

因此：

\[
\boxed{
Relevant
\neq
GateNecessary
}
\]

**中文业务释义：** 与项目相关 ≠ 必须作为准入门槛。

这是资格合规系统非常重要的 Decision Boundary。

---

# 八、地域条件：D01 的资格审查视角

附件 9 第一类重点包括：

```text
供应商注册地
所在地距采购人的距离
在某行政区域内设立分支机构
```

作为不合理资格条件或评审因素的风险。

在资格层真正要抽：

```text
supplier_registration_location    # 中文：供应商注册 / 登记位置 / 地域

required_service_location    # 中文：是否需要服务位置 / 地域

distance_threshold    # 中文：距离阈值

required_local_branch    # 中文：是否需要地方 / 本地分支机构

required_local_office    # 中文：是否需要地方 / 本地办公 / 服务机构

required_before_bid    # 中文：是否需要之前投标

required_after_award    # 中文：是否需要之后中标 / 成交

failure_consequence    # 中文：不满足条件的后果
```

然后判断：

\[
\boxed{
LocationRequirement
+
EntryGate
+
PreBid
}
\]

**中文业务释义：** 地域要求 + 准入门槛 + 投标前。

与：

\[
\boxed{
PerformanceLocation
+
PostAward
}
\]

**中文业务释义：** 履约地点 + 中标后。

是否被混淆。

---

# 九、核心心智模型 ④
# `LocalServiceNeed` 不等于 `LocalEntityPrecondition`

例如采购项目确实需要：

```text
2小时现场响应
```

这是：

# Service Level
## 服务水平要求

系统应优先问：

> 能否直接要求 2 小时响应？

而不是先把它转换成：

```text
投标人必须在本市已有分公司
```

所以：

\[
\boxed{
OutcomeRequirement
优先于
EntityLocationProxy
}
\]

在工程上：

> 如果业务目标可以用履约结果表达，就不要自动用供应商身份 / 地域代理变量表达。

---

# 十、行业条件：D03 / D04 的资格审查视角

风险可能表现为：

```text
必须属于某行业

必须具有某行业业绩

必须获得某行业奖项

营业执照经营范围必须写明某词
```

这里系统需要区分：

# Subject-matter Capability
## 实际业务能力

与：

# Industry Identity
## 行业身份

所以：

\[
\boxed{
CanPerformTheContract
\neq
BelongsToSpecificIndustryLabel
}
\]

**中文业务释义：** 是否能够履行合同 ≠ 属于特定行业标签。

---

# 十一、营业执照经营范围为什么不能简单关键词判断？

D04 本身带有：

```text
除特别规定外
```

所以系统至少要检查：

```text
是否把经营范围作为资格Gate

是否存在特别规定

该经营范围条件是否有明确依据

是否实际上用于限制其他行业供应商
```

因此：

\[
\boxed{
BusinessScopeMention
\neq
AutomaticFinding
}
\]

**中文业务释义：** 提及营业执照经营范围 ≠ 自动形成风险发现。

---

# 十二、企业规模条件：D05 的直接风险字段

附件 9 以及工作指引正文明确关注：

```text
经营年限
注册资本
资产总额
营业收入
从业人员
利润
纳税额
```

这些字段必须在 Document Schema 中被结构化为：

```text
company_age_years    # 中文：企业年限年限

registered_capital    # 中文：注册资本

total_assets    # 中文：总额资产

annual_revenue    # 中文：年度营业收入

employee_count    # 中文：从业人员数量

profit    # 中文：利润

tax_amount    # 中文：纳税金额
```

并记录：

```text
operator    # 中文：运算符 / 运营主体
threshold    # 中文：阈值
time_window    # 中文：适用时间窗口
business_function    # 中文：业务功能
```

例如：

```text
registered_capital >= 5000万元
```

如果它作为：

```text
ENTRY_GATE    # 中文：准入门槛
```

就进入高优先级规则检查。

---

# 十三、核心心智模型 ⑤
# `FinancialData` 和 `FinancialBarrier` 不是一回事

采购文件可能需要：

> 合法的财务会计材料。

这不等于：

> 可以任意设定某个资产、收入、利润或注册资本数值作为准入门槛。

所以：

\[
\boxed{
EvidenceOfFinancialSoundness
\neq
ArbitraryScaleThreshold
}
\]

**中文业务释义：** 财务状况证明材料 ≠ 任意企业规模数值门槛。

工程上必须区分：

```text
要求提供材料
```

和：

```text
要求达到某数值
```

---

# 十四、经营年限为什么特别容易被误用？

例如：

```text
成立满10年
```

表面看起来是：

> “经验丰富”。

但公司成立时间：

> 并不自动等价于当前项目履约能力。

所以系统要问：

```text
成立年限与合同履约风险有什么直接关系？

是否可以改用人员能力、技术能力、项目经验等更直接证据？

是否对新设但具备能力的供应商造成不必要排斥？
```

因此：

\[
\boxed{
CompanyAge
\neq
Capability
}
\]

**中文业务释义：** 企业成立 / 经营年限 ≠ 履约能力。

---

# 十五、企业形式：D09 / D10

附件 9 关注：

```text
所有制形式

组织形式

企业股权结构

投资者国别

所在地
```

因此 Supplier Profile 要结构化：

```text
ownership_type    # 中文：所有制类型

organization_form    # 中文：组织形式

shareholding_structure    # 中文：股权结构

investor_nationality    # 中文：投资者国别

registered_location    # 中文：注册位置 / 地域
```

但这些字段存在的目的不是：

> 让模型更容易筛掉某类企业。

而是：

> 检查采购文件是否把这些身份属性变成不合理门槛。

所以：

\[
\boxed{
SupplierAttribute
\neq
QualificationJustification
}
\]

**中文业务释义：** 供应商身份属性 ≠ 资格条件正当理由。

---

# 十六、核心心智模型 ⑥
# “是谁”与“能不能履约”必须尽量分开

理想资格条件应该更多回答：

```text
能不能完成合同？
有没有必要许可？
有没有所需技术与设备？
能否满足安全 / 质量要求？
```

而不是：

```text
企业属于谁？
成立多久？
注册在哪里？
资本有多大？
```

所以：

\[
\boxed{
CapabilityEvidence
>
IdentityProxy
}
\]

**中文业务释义：** 能力证据 > 身份 / 规模代理变量。（这里的 `>` / `<` 若用于心智模型，表示工程优先级或信息价值关系，不一定是数学数值大小。）

这里的 `>` 表示：

> 对履约能力判断通常更直接。

---

# 十七、业绩要求：最容易出现“合理需求”和“不合理门槛”的混合区

项目经验是现实采购中常见能力证据。

但附件 9 同时关注：

```text
特定行政区域业绩

特定主体业绩

特定行业业绩

特定金额合同业绩
```

所以：

\[
\boxed{
ExperienceRequirement
\neq
AutomaticallyReasonable
}
\]

**中文业务释义：** 业绩要求 ≠ 自动视为合理。

需要进一步拆：

```text
experience_subject    # 中文：业绩主体 / 事项

project_similarity    # 中文：项目相似性

industry_constraint    # 中文：行业限制条件

region_constraint    # 中文：地域限制条件

specific_entity_constraint    # 中文：特定实体 / 主体限制条件

minimum_project_count    # 中文：最低项目数量

minimum_contract_amount    # 中文：最低合同金额

time_window    # 中文：适用时间窗口

completion_status    # 中文：完成状态

proof_material    # 中文：证明材料材料
```

---

# 十八、核心心智模型 ⑦
# `SimilarExperience` 的“相似”必须可解释

不能只是：

```text
与本项目类似
```

然后实际规则暗含：

```text
同地区
同采购人
同一行业
同金额级别
```

系统应该问：

> 相似到底体现在哪些履约能力？

例如：

```text
技术复杂度
服务对象规模
安全级别
并发规模
交付周期
人员能力
```

因此：

\[
\boxed{
Similarity
应该映射到
CapabilityDimension
}
\]

---

# 十九、特定金额业绩：D06 的资格判断

例如：

```text
必须有单项合同金额5000万元以上项目
```

系统不能只问：

> 5000 万是不是很大？

而要问：

```text
当前项目预算 / 规模是多少？

这个金额阈值在证明什么能力？

是否存在更直接的履约能力指标？

是否显著排除具备能力但过去项目金额不同的供应商？
```

所以：

\[
\boxed{
HistoricalContractAmount
\neq
DirectCapabilityProof
}
\]

**中文业务释义：** 历史合同金额 ≠ 直接能力证明。

---

# 二十、证书 / 资质必须先做“类型识别”

不能把所有：

```text
证书
认证
资质
奖项
```

当成一类。

至少分：

```text
LEGAL_LICENSE    # 中文：法定许可
法定许可

MANDATORY_QUALIFICATION    # 中文：法定 / 强制资质
法定 / 强制资质

VOLUNTARY_CERTIFICATION    # 中文：自愿性认证
自愿性认证

INDUSTRY_CERTIFICATE    # 中文：行业协会 / 行业类证书
行业协会证书

AWARD    # 中文：奖项
奖项

CREDIT_RATING    # 中文：信用评级
信用评级

TRAINING_CERTIFICATE    # 中文：培训证书
培训证书

OTHER    # 中文：其他
```

因为不同类型：

> 合规逻辑不同。

---

# 二十一、核心心智模型 ⑧
# `CertificateExists` 不代表 `CertificateCanBeQualificationGate`

真正要问：

```text
谁颁发？

法律 / 行政法规 / 有效政策是否要求？

和项目履约有什么关系？

是否已经取消？

是否只是行业组织 / 协会评价？

是否被用作资格门槛还是评分项？
```

这直接连接：

```text
D14    # 中文：D14 规则编号（附件9工程化规则标识）
D15    # 中文：D15 规则编号（附件9工程化规则标识）
D07    # 中文：D07 规则编号（附件9工程化规则标识）
```

---

# 二十二、D14 为什么必须连接 Policy Registry？

D14 涉及：

> 国务院取消的行政审批事项。

这个判断不能靠模型训练记忆。

因为：

```text
审批事项状态会变化
```

所以：

\[
\boxed{
ApprovalStatus
\Rightarrow
PolicyLookup
}
\]

**中文业务释义：** 审批事项状态 ⇒ 政策法规查询。

执行流程：

```text
检测到许可 / 审批事项
↓
识别事项名称
↓
Policy Registry 查当前 / 项目时点状态
↓
确认是否属于已取消事项
↓
再形成候选Finding
```

---

# 二十三、D15：协会证书 / 奖项为什么需要 Issuer Resolution？

系统必须识别：

# Issuer
## 颁发主体

例如：

```text
行政机关
法定机构
行业协会
社会组织
商业评价机构
未知主体
```

所以：

\[
\boxed{
CertificateName
不够
}
\]

还需要：

\[
\boxed{
Certificate
+
Issuer
+
LegalStatus
+
BusinessFunction
}
\]

**中文业务释义：** 证书 + 出具机构 + 法律状态 + 业务功能 / 条款作用。

---

# 二十四、厂家授权：D16 的资格视角

附件 9 对：

```text
厂家授权
承诺
证明
背书
```

设置了重要检查逻辑，

同时包含：

```text
除采购进口货物外
```

这样的例外表达。

所以系统要抽：

```text
manufacturer_authorization_required    # 中文：是否要求厂家授权

manufacturer_commitment_required    # 中文：厂家承诺是否需要

manufacturer_certificate_required    # 中文：厂家证书是否需要

manufacturer_endorsement_required    # 中文：厂家背书是否需要

import_goods_status    # 中文：进口货物状态

used_as_qualification_gate    # 中文：用于AS资格门槛
```

然后：

\[
\boxed{
AuthorizationTrigger
+
ImportExceptionCheck
}
\]

**中文业务释义：** 授权触发 + 进口例外Check。

---

# 二十五、供应商库 / 名录库 / 资格库：D17

如果采购文件要求：

```text
必须进入某备选库

必须属于某名录库

必须已进入某资格库
```

并把它作为：

```text
ENTRY_GATE    # 中文：准入门槛
```

应进入：

# Supplier Pool Restriction
## 供应商库限制

重点结构：

```text
pool_name    # 中文：供应商库 / 名录名称

pool_operator    # 中文：供应商库 / 名录运算符 / 运营主体

membership_required    # 中文：入库 / 入围资格是否需要

membership_time    # 中文：入库 / 入围资格时间

entry_gate    # 中文：准入门槛

policy_basis    # 中文：政策 / 法规依据
```

---

# 二十六、不必要登记注册：D18

系统要区分：

```text
法定登记
```

和：

```text
为了参加采购活动额外要求的不必要登记 / 注册
```

因此：

\[
\boxed{
Registration
\neq
UnnecessaryRegistration
}
\]

**中文业务释义：** 登记 / 注册 ≠ 不必要登记注册。

仍然需要：

```text
LegalBasis    # 中文：法律 / 政策依据
Necessity    # 中文：必要性
Timing    # 中文：适用 / 发生时点
```

---

# 二十七、获取采购文件前置材料：D19

这一条特别适合用：

# Stage Logic
## 程序阶段逻辑

例如：

```text
营业执照
审计报告
资质证书
```

这些材料可能属于：

> 后续资格审查材料。

但如果要求：

> 在获取采购文件之前就必须提交，

就出现：

# Document Access Gate
## 采购文件获取门槛

因此：

\[
\boxed{
QualificationEvidence
\neq
ProcurementDocumentAccessGate
}
\]

**中文业务释义：** 资格证明材料 ≠ 采购文件获取门槛。

---

# 二十八、核心心智模型 ⑨
# 同一个材料，放在不同程序阶段，合规意义可能完全不同

这和 Stage 3 的：

\[
\boxed{
Meaning
=
Text
+
BusinessPosition
}
\]

**中文业务释义：** 含义 = 文本 + 业务Position。

完全一致。

因此任何资格条件必须带：

```text
required_at_stage    # 中文：要求满足 / 提交的程序阶段
```

---

# 二十九、技术证明材料出具机构：D20

系统不能只检测：

```text
检测报告
认证报告
证明材料
```

还要抽：

```text
issuer_name    # 中文：出具机构名称

issuer_type    # 中文：出具机构类型

issuer_region    # 中文：出具机构地域

issuer_designation    # 中文：出具机构指定

exclusive_issuer_required    # 中文：唯一 / 排他出具机构是否需要

special_provision    # 中文：特别条款 / 规定

justification    # 中文：理由 / 正当性
```

因为真正风险可能来自：

> 无正当理由把“谁能出证明”限定死。

---

# 三十、定点供应商 / 入围单位：D21

如果要求：

```text
投标人必须是某范围内的定点供应商
```

或者：

```text
必须是某入围单位
```

就要判断：

```text
这是不是合法框架 / 定点机制？

当前项目是否允许依赖该范围？

还是额外形成新的市场准入壁垒？
```

因此：

\[
\boxed{
ExistingPoolMembership
\neq
AutomaticallyValidQualification
}
\]

**中文业务释义：** 既有供应商库 / 入围资格 ≠ 当然有效的资格条件。

---

# 三十一、黑名单 / 不良记录 / 违约名单：D22

出现：

```text
黑名单
不良记录名单
违约名单
```

不能自动：

> 判定违规。

真正关键是：

# Legal Basis
## 法律依据

因此：

\[
\boxed{
BlacklistMention
\neq
Finding
}
\]

**中文业务释义：** 提及黑名单 ≠ 合规发现项。

而：

\[
\boxed{
BlacklistGate
+
NoLegalBasis
=
CandidateRisk
}
\]

**中文业务释义：** 黑名单准入门槛 + 没有法律依据 = 候选风险。

必须通过：

```text
Policy Registry    # 中文：政策法规登记库
```

确认依据。

---

# 三十二、资格条件的“身份代理变量”问题

很多不合理门槛不直接写：

```text
只要大企业
```

而是通过：

```text
注册资本
营业收入
人员数量
大型项目金额
高等级信用
大量网点
长期经营年限
```

间接筛选。

这些叫：

# Proxy Variables
## 代理变量

因此：

\[
\boxed{
NoExplicitDiscrimination
\neq
NoDiscriminatoryEffectCandidate
}
\]

**中文业务释义：** 无/未Explicit歧视/不合理排斥 ≠ 无/未歧视性Effect候选。

但是否真正构成 Finding：

> 仍需结合来源规则、项目上下文和证据判断。

---

# 三十三、核心心智模型 ⑩
# `Proxy` 不是自动违规，而是“进一步解释为什么需要”的信号

Rule Engine 应该把它升级成：

```text
NECESSITY_REVIEW_REQUIRED    # 中文：需要进行必要性复核
```

而不是：

```text
VIOLATION=true    # 中文：违规状态 = 正确 / 真
```

---

# 三十四、Qualification Gate 的风险分层

第一版可以先按：

```text
Q0    # 中文：未发现资格门槛风险
未发现资格门槛风险

Q1    # 中文：存在需要说明的资格条件
存在需要说明的资格条件

Q2    # 中文：存在明显限制竞争的候选条件，需要复核
存在明显限制竞争的候选条件，需要复核

Q3    # 中文：与 D01-D22 高度匹配的高风险资格条件候选
高风险资格条件候选，与D01-D22直接高度匹配

Q4    # 中文：重大高风险，证据与法源充分但仍须人工确认
重大高风险，证据和法源充分，必须人工确认
```

但再次强调：

\[
\boxed{
QualificationRiskLevel
\neq
AdministrativePenaltyConclusion
}
\]

**中文业务释义：** 资格风险等级 ≠ 行政处罚结论。

---

# 三十五、Qualification Finding 的完整结构

```text
finding_id    # 中文：发现项标识

review_domain    # 中文：审查业务域
=
QUALIFICATION    # 中文：资格条件章节

clause_id    # 中文：条款标识
requirement_id    # 中文：要求标识

qualification_type    # 中文：资格条件类型

business_function    # 中文：业务功能

required_at_stage    # 中文：要求满足 / 提交的程序阶段

subject    # 中文：主体 / 事项

condition    # 中文：条件

threshold    # 中文：阈值

timing    # 中文：时点

failure_consequence    # 中文：不满足条件的后果

candidate_rule_ids    # 中文：候选规则标识列表

confirmed_rule_id    # 中文：已确认规则标识

capability_objective    # 中文：履约能力目标

relevance_analysis    # 中文：相关性分析

necessity_analysis    # 中文：必要性分析

proportionality_analysis    # 中文：比例性分析

alternative_requirement    # 中文：替代方案要求

competition_impact    # 中文：竞争影响

exception_status    # 中文：例外状态

legal_basis_refs    # 中文：法律 / 政策依据引用标识列表

policy_snapshot_id    # 中文：政策法规快照标识

evidence_span    # 中文：证据片段及原文定位

risk_level    # 中文：风险等级

confidence    # 中文：置信度

human_review_required    # 中文：是否需要人工复核

recommended_revision    # 中文：建议修改方案
```

---

# 三十六、Qualification Rule Engine 的执行流程

\[
\boxed{
QualificationClause
\rightarrow
RequirementParse
\rightarrow
GateDetection
\rightarrow
D01-D22Candidate
\rightarrow
CapabilityObjective
\rightarrow
Relevance
\rightarrow
Necessity
\rightarrow
Proportionality
\rightarrow
Alternative
\rightarrow
Exception
\rightarrow
PolicyCheck
\rightarrow
EvidenceGate
\rightarrow
Finding/HumanReview
}
\]

**中文业务释义：** 资格条款 → 要求解析 → 门槛Detection → D01规则-D22候选 → 能力目标 → 相关性 → 必要性 → 比例性 → 替代方案 → 例外 → 政策Check → 证据门槛 → 合规发现项/人工复核。

中文：

```text
先看它是不是准入门槛

再看命中哪类风险候选

再问它想证明什么能力

再检查是否真的相关

再检查是否必须作为投标前Gate

再检查限制强度是否过大

再找有没有更少排斥的办法

再查例外和政策

最后才形成Finding
```

---

# 三十七、核心心智模型 ⑪
# 合理资格条件应尽量“直接测能力”，而不是“间接测身份”

例如要保证：

```text
响应速度
```

优先测：

```text
响应时间SLA
```

而不是：

```text
本地注册地
```

要保证：

```text
技术能力
```

优先测：

```text
关键人员
设备
方法
实施方案
法定许可
```

而不是：

```text
企业成立年限
```

所以：

\[
\boxed{
DirectCapabilitySignal
>
IdentityProxy
}
\]

**中文业务释义：** 直接履约能力信号 > 身份 / 规模代理变量。（这里的 `>` / `<` 若用于心智模型，表示工程优先级或信息价值关系，不一定是数学数值大小。）

---

# 三十八、修改建议怎样生成？

合规系统不能只说：

```text
删除
```

而是问：

> 采购人原本想解决什么业务风险？

例如：

### 原要求

```text
投标人必须在本市设立分公司
```

如果真实目的只是：

```text
保障现场服务响应
```

则修改建议可能倾向：

```text
改成中标后 / 履约期间满足明确服务响应时间、
人员到场时间或服务能力要求
```

因此：

\[
\boxed{
Remediation
=
PreserveBusinessGoal
+
RemoveUnnecessaryBarrier
}
\]

**中文业务释义：** 修改建议 = 保留业务目标 + 移除不必要准入障碍。

---

# 三十九、核心心智模型 ⑫
# 好的合规修改不是“全部放宽”，而是“把身份门槛改成能力 / 结果要求”

这能同时满足：

```text
采购质量
+
公平竞争
```

而不是二选一。

---

# 四十、Hard Negative 必须重点训练

资格领域最容易产生误报。

例如：

```text
项目需要法定许可
```

不能因为看到：

```text
许可证
```

就报不合理限制。

又例如：

```text
履约地点在本地
```

不能因为看到：

```text
本地
```

就报地域限制。

所以必须建立：

```text
HardNegative_LocalPerformance    # 中文：高难负例地方 / 本地履约

HardNegative_StatutoryLicense    # 中文：高难负例：确有法定许可要求

HardNegative_ReasonableExperience    # 中文：高难负例：与履约能力合理相关的业绩要求

HardNegative_PostAwardService    # 中文：高难负例后中标 / 成交服务

HardNegative_ValidPolicyException    # 中文：高难负例有效政策 / 法规例外
```

---

# 四十一、Counterfactual Pair

### Pair A

```text
投标人必须在投标截止前在本市设立分公司。
```

### Pair B

```text
中标供应商须在合同履约期间满足2小时现场响应要求。
```

比较变量：

```text
Timing    # 中文：适用 / 发生时点
Gate    # 中文：门槛
LocationProxy    # 中文：地域 / 本地身份代理变量
OutcomeRequirement    # 中文：履约结果要求
```

---

### Pair C

```text
投标人注册资本不得低于5000万元。
```

### Pair D

```text
供应商应具有履行合同所需要的设备和专业技术能力，并提供相应证明。
```

比较：

```text
ScaleProxy    # 中文：企业规模代理变量
vs    # 中文：VS
DirectCapability    # 中文：直接履约能力指标
```

这种训练数据帮助系统学习：

\[
\boxed{
MarketAccessDecisionBoundary
}
\]

**中文业务释义：** 市场准入判断边界。

---

# 四十二、Qualification Benchmark 应该测什么？

不能只测：

```text
违规 / 不违规准确率
```

至少需要：

```text
Qualification Gate Detection    # 中文：资格准入门槛识别

D01-D10 Recall / Precision    # 中文：D01D10召回率 / 精确率

D15-D22 Qualification Slice    # 中文：D15-D22 中与资格准入相关的评测切片

PreBid / PostAward Accuracy    # 中文：前投标 / 后中标 / 成交准确率

Capability vs Identity Classification    # 中文：履约能力要求 vs 企业身份代理条件分类

Experience Restriction Accuracy    # 中文：业绩限制准确率

Scale Proxy Detection    # 中文：企业规模代理变量识别

Certificate Type Resolution    # 中文：证书类型消解

Exception Accuracy    # 中文：例外准确率

Legal Basis Accuracy    # 中文：法律 / 政策依据准确率

Human Escalation Accuracy    # 中文：转人工复核决策准确率

Evidence Localization Accuracy    # 中文：证据原文定位准确率
```

---

# 四十三、核心心智模型 ⑬
# `QualificationRecall` 要与 `HumanReviewLoad` 一起看

如果为了不漏检：

> 所有资格条件都转人工，

Recall 可能很高，

但系统没有实际生产价值。

所以：

\[
\boxed{
UsefulQualificationSystem
=
RiskRecall
+
Precision
+
ReasonableHumanLoad
}
\]

**中文业务释义：** 可用的资格合规系统 = 风险召回 + 精确率 + 合理人工复核负荷。

---

# 四十四、资格条件与评分标准之间要做 Cross-check

同一个条件可能：

```text
在资格审查中已经作为Gate
```

同时又：

```text
在评分中再次加分
```

这种跨域关系不能只靠 Stage 5 单独判断。

需要记录：

```text
canonical_requirement_id    # 中文：归一化要求标识
```

后面 Stage 7 做：

# Cross-domain Review
## 跨域检查

因此：

\[
\boxed{
QualificationReview
\neq
IsolatedReview
}
\]

**中文业务释义：** 资格条件审查 ≠ 孤立审查。

---

# 四十五、资格条件与合同履约之间也要 Cross-check

如果采购人声称：

> 某资格门槛是履约所必需，

系统应检查：

```text
它在合同里有没有对应的履约义务？

验收是否检查它？

不满足会不会影响合同目标？
```

如果：

```text
投标时要求非常严格
但合同里根本不要求
```

就会增加：

# Necessity Doubt
## 必要性疑点

所以：

\[
\boxed{
QualificationJustification
应该能回到
ContractPerformance
}
\]

---

# 四十六、核心心智模型 ⑭
# `GateWithoutPerformanceLink` 是重要风险信号

不是自动认定违法，

但应提高：

```text
necessity_review_priority    # 中文：必要性复核优先级
```

---

# 四十七、Human Review 什么时候必须触发？

至少包括：

```text
项目必要性无法从文件判断

采购人有特殊业务说明但证据不足

法定许可状态不确定

Rule和Policy Registry结论冲突

行业 / 地域经验是否合理存在强裁量

特定金额业绩与项目规模关系不明确

本地服务能力存在重大安全 / 时效要求

证书 / 认证法律属性不明确

D22名单依据无法确认

高风险但模型置信度低
```

所以：

\[
\boxed{
Uncertainty
+
HighImpact
\Rightarrow
HumanReview
}
\]

**中文业务释义：** 不确定性 + 高影响 ⇒ 人工复核。

---

# 四十八、本阶段正式工程产物
# `ProcurementQualificationCompliance_V1`

建议核心结构：

```text
ProcurementQualificationCompliance_V1/    # 中文：ProcurementQualificationCompliance_V1：资格与市场准入合规模块根目录

├── schema/    # 中文：工程目录：结构定义
│   ├── qualification_requirement.json    # 中文：工程文件：资格要求JSON 配置文件
│   ├── supplier_attribute.json    # 中文：工程文件：供应商attributeJSON 配置文件
│   ├── capability_objective.json    # 中文：工程文件：履约能力目标JSON 配置文件
│   └── qualification_finding.json    # 中文：工程文件：资格发现项JSON 配置文件
│
├── rules/    # 中文：工程目录：规则
│   ├── location/    # 中文：工程目录：位置 / 地域
│   ├── industry/    # 中文：工程目录：行业
│   ├── scale/    # 中文：工程目录：scale
│   ├── ownership/    # 中文：工程目录：所有制
│   ├── experience/    # 中文：工程目录：业绩
│   ├── certificate/    # 中文：工程目录：证书
│   ├── authorization/    # 中文：工程目录：授权
│   ├── supplier_pool/    # 中文：工程目录：供应商供应商库 / 名录
│   └── blacklist/    # 中文：工程目录：黑名单
│
├── decision/    # 中文：工程目录：决策
│   ├── relevance_test    # 中文：相关性测试
│   ├── necessity_test    # 中文：必要性测试
│   ├── proportionality_test    # 中文：比例性测试
│   ├── alternative_test    # 中文：替代方案测试
│   └── policy_check    # 中文：政策 / 法规检查
│
├── tests/    # 中文：工程目录：测试集
│   ├── positive/    # 中文：工程目录：正例
│   ├── hard_negative/    # 中文：工程目录：高难负例
│   ├── counterfactual/    # 中文：工程目录：counterfactual
│   ├── exception/    # 中文：工程目录：例外
│   └── missing_context/    # 中文：工程目录：缺失上下文
│
└── manifest.json    # 中文：工程文件：清单 / 元数据JSON 配置文件
```

---

# 四十九、Qualification Requirement Schema

```text
qualification_requirement_id    # 中文：资格要求标识

clause_id    # 中文：条款标识
requirement_id    # 中文：要求标识

qualification_type    # 中文：资格条件类型

business_function    # 中文：业务功能
required_at_stage    # 中文：要求满足 / 提交的程序阶段

subject    # 中文：主体 / 事项
action    # 中文：动作
object    # 中文：对象
condition    # 中文：条件

threshold    # 中文：阈值
unit    # 中文：单位

region_constraint    # 中文：地域限制条件
industry_constraint    # 中文：行业限制条件
ownership_constraint    # 中文：所有制限制条件
organization_constraint    # 中文：组织形式限制
shareholding_constraint    # 中文：股权限制条件
investor_nationality_constraint    # 中文：投资者国别限制条件

company_age_constraint    # 中文：企业年限限制条件
registered_capital_constraint    # 中文：注册资本限制条件
asset_constraint    # 中文：资产限制条件
revenue_constraint    # 中文：营业收入限制条件
employee_constraint    # 中文：从业人员限制条件
profit_constraint    # 中文：利润限制条件
tax_constraint    # 中文：纳税限制条件

experience_constraint    # 中文：业绩限制条件
contract_amount_constraint    # 中文：合同金额限制条件

certificate_constraint    # 中文：证书限制条件
license_constraint    # 中文：许可 / 资质限制条件
award_constraint    # 中文：中标 / 成交限制条件
credit_constraint    # 中文：信用限制条件

manufacturer_authorization_constraint    # 中文：厂家授权限制条件

supplier_pool_constraint    # 中文：供应商供应商库 / 名录限制条件
registration_constraint    # 中文：注册 / 登记限制条件
document_access_constraint    # 中文：文档获取限制条件
issuer_constraint    # 中文：出具机构限制条件
blacklist_constraint    # 中文：黑名单限制条件

failure_consequence    # 中文：不满足条件的后果

candidate_rule_ids    # 中文：候选规则标识列表

parse_confidence    # 中文：解析置信度
```

---

# 五十、Capability Analysis Schema

```text
capability_objective    # 中文：履约能力目标

project_need    # 中文：项目实际需要

direct_relation    # 中文：直接关联性

gate_necessity    # 中文：作为准入门槛的必要性

proportionality    # 中文：比例性

less_restrictive_alternative    # 中文：更少限制竞争的替代方案

contract_performance_link    # 中文：与合同履约目标的关联

supporting_evidence    # 中文：支持性证据

counter_evidence    # 中文：反向 / 反证证据

uncertainty    # 中文：不确定

human_review_required    # 中文：是否需要人工复核
```

---

# 五十一、本阶段最重要的 15 个核心心智模型

> **心智模型 ①：`CapabilityRequirement ≠ MarketAccessBarrier`。保障履约能力和设置不合理准入门槛是两回事。**

> **心智模型 ②：`QualificationGate ≠ ScoringPreference`。能不能参加和参加以后得多少分必须分开。**

> **心智模型 ③：`ProjectSpecific ≠ PurchaserPreference`。项目特定条件必须有项目特定理由。**

> **心智模型 ④：`Relevant ≠ GateNecessary`。与项目有关，不等于必须作为投标前淘汰条件。**

> **心智模型 ⑤：`LocalServiceNeed ≠ LocalEntityPrecondition`。履约服务目标不应自动转化为本地注册 / 分支机构门槛。**

> **心智模型 ⑥：`CanPerformContract ≠ BelongsToIndustryLabel`。实际履约能力与行业身份标签必须区分。**

> **心智模型 ⑦：`FinancialEvidence ≠ ArbitraryScaleThreshold`。财务材料与规模数值门槛不是一回事。**

> **心智模型 ⑧：`CompanyAge ≠ Capability`。成立年限只是身份 / 历史代理变量，不是直接履约能力。**

> **心智模型 ⑨：`SupplierAttribute ≠ QualificationJustification`。所有制、组织形式、股权、国别、所在地不能因为“存在”就成为门槛理由。**

> **心智模型 ⑩：`ExperienceRequirement ≠ AutomaticallyReasonable`。业绩需要映射到真实能力维度，而不是地域、行业、主体、金额的任意锁定。**

> **心智模型 ⑪：`CertificateExists ≠ CertificateCanBeQualificationGate`。证书必须看颁发主体、法律状态、项目关系和业务用途。**

> **心智模型 ⑫：`QualificationEvidence ≠ ProcurementDocumentAccessGate`。资格证明材料不能因为属于资格材料，就当然适合作为获取采购文件的前置条件。**

> **心智模型 ⑬：`DirectCapabilitySignal > IdentityProxy`。资格条件应尽量直接测履约能力，而不是用企业身份和规模做代理。**

> **心智模型 ⑭：`Remediation = PreserveBusinessGoal + RemoveUnnecessaryBarrier`。好的修改建议不是简单删条件，而是保留采购目的、去掉不必要排斥。**

> **心智模型 ⑮：`GateWithoutPerformanceLink` 是必要性疑点。资格门槛如果无法回到合同履约目标，应提高人工复核优先级。**

---

# 五十二、把整个资格合规判断压成一张工程图

```text
                     Qualification Clause    # 中文：资格条款
                          资格条款
                              │
                              ▼
                     Requirement Parsing    # 中文：要求结构化解析
                        结构化要求
                              │
                              ▼
                         Is It a Gate?    # 中文：是否属于准入门槛
                         是否准入门槛
                              │
                              ▼
                     D01-D22 Candidate    # 中文：D01-D22 候选规则
                         候选规则
                              │
                              ▼
                     Capability Objective    # 中文：需要证明的履约能力目标
                      想证明什么能力？
                              │
                              ▼
                         Relevance    # 中文：与项目的直接相关性
                     与项目是否直接相关
                              │
                              ▼
                       Gate Necessity    # 中文：是否必须作为准入门槛
                  是否必须作为投标前门槛
                              │
                              ▼
                      Proportionality    # 中文：比例性 / 限制强度是否相称
                       限制是否相称
                              │
                              ▼
                Less Restrictive Alternative    # 中文：更少排斥竞争的替代方案
                     是否有更少排斥方案
                              │
                              ▼
                     Contract Performance    # 中文：合同履约目标
                       能否回到履约目标
                              │
                              ▼
                       Exception Check    # 中文：例外检查
                          例外检查
                              │
                              ▼
                        Policy Check    # 中文：法规政策适用性检查
                       法规状态检查
                              │
                              ▼
                       Evidence Gate    # 中文：证据充分性门槛
                          证据门
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
       Checked No Risk   Candidate Finding   Unresolved    # 中文：已检查无 / 否风险候选发现项未解决
          已检查无风险       候选风险项          无法确定
                              │               │
                              ▼               ▼
                       Human Review      Human Review    # 中文：人工复核人工复核
                          人工确认          人工复核
                              │               │
                              └───────┬───────┘
                                      ▼
                              Remediation    # 中文：修改 / 整改建议
                                修改建议
```

脑中最后只留一句：

> **资格合规的本质，不是“供应商条件越少越好”，而是每一个准入门槛都必须能够证明它直接服务于项目真实履约能力，并且在相关性、必要性、比例性、替代方案、竞争影响、例外和法源上经得起追问；如果采购目标可以用更直接的能力或履约结果表达，就不应轻易用地域、行业身份、企业规模、成立年限、所有制、特定金额业绩等代理变量把供应商挡在竞争入口之外。**

---

# 第十一课 · 第 5 阶段掌握测试

现在不回看正文，你应该能够解释：

```text
为什么 Capability Requirement 不等于 Market Access Barrier？

Qualification Gate 与 Scoring Preference 有什么根本区别？

什么是 Baseline Eligibility，什么是 Project-specific Qualification？

为什么 Project-specific 条件必须有 Project-specific Justification？

资格条件为什么要做 Objective / Relevance / Necessity / Proportionality / Alternative 五问？

为什么 Relevant 仍然不等于 Gate Necessary？

为什么本地服务需求不应自动变成本地企业 / 本地分支机构前置条件？

为什么行业身份与履约能力必须分开？

为什么经营范围规则必须检查特别规定？

为什么财务材料和财务门槛是两回事？

为什么成立年限不是直接履约能力？

为什么所有制、组织形式、股权结构、投资者国别等是 Supplier Attribute，而不是天然 Qualification Justification？

业绩要求为什么需要拆地域、行业、金额、时间和能力维度？

为什么历史合同金额不是直接能力证明？

证书为什么必须识别 Certificate Type 和 Issuer？

为什么 D14 必须查 Policy Registry？

为什么厂家授权必须同时做进口货物 Exception Check？

为什么资格证明材料与获取采购文件前置门槛必须区分？

为什么 D22 的关键不是“有没有黑名单”，而是“有没有法律依据”？

什么叫 Proxy Variable？

为什么好的修改建议应该把身份门槛改成能力 / 结果要求？

为什么资格条件必须与合同履约目标 Cross-check？
```

如果这些能够完整解释：

\[
\boxed{
第十一课第5阶段真正掌握
}
\]

---

# 下一阶段：第十一课 · 第 6 阶段
# 技术参数合规：品牌、专利、技术路线、检测报告、认证、授权、样品
## 怎样识别“看起来只是技术要求、实际上已经把竞争范围锁定到特定供应商或特定产品”的隐性限制？

下一阶段将重点连接：

```text
D11    # 中文：D11 规则编号（附件9工程化规则标识）
D12    # 中文：D12 规则编号（附件9工程化规则标识）
D13    # 中文：D13 规则编号（附件9工程化规则标识）
D15    # 中文：D15 规则编号（附件9工程化规则标识）
D16    # 中文：D16 规则编号（附件9工程化规则标识）
D20    # 中文：D20 规则编号（附件9工程化规则标识）
```

并建立：

# `ProcurementTechnicalCompliance_V1`

最重要的边界：

\[
\boxed{
TechnicalSpecificity
\neq
TechnicalDiscrimination
}
\]

**中文业务释义：** 技术参数具体性 ≠ 技术歧视 / 不合理技术排斥。
