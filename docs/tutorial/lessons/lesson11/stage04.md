# 第十一课 · 第 4 阶段
# “四类”专项整治——采购人设置差别歧视条款：附件 9 的 22 项规则工程化
## 怎样把财政部《2025 年政府采购领域“四类”违法违规行为专项整治工作指引》中 7 类问题、22 项具体表现形式，转成机器可执行、可解释、可审计、可评测的政府采购合规规则体系？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：正文质量已较高，仅增加轻量核心阅读导航。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **22项 ≠ 22个关键词。附件 9 的 22 项是 7 类问题下的 22 种具体表现形式。**
2. **Rule ≠ PromptInstruction。每个 Dxx 必须是可版本化、可执行、可测试、可审计的 Rule Object。**
3. **InspectionRule ≠ LegalProvision。专项检查规则与法律政策依据必须分层，但保持可追踪。**
4. **Trigger → Candidate，不是 Trigger → Violation。触发器负责召回候选，不负责最终宣判。**
5. **All22Rules ≠ SameInferenceMethod。有的规则偏确定性、有的依赖例外、有的依赖政策状态、有的需要强语义与项目必要性判断。**

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

> **中文阅读增强说明（本次修订新增）**：为方便中国政府采购业务人员、合规人员和工程人员共同阅读，本阶段所有关键英文工程字段、状态值、流程节点和 Schema 标识均保留原英文名称，并在同一代码块中增加 `# 中文：...` 的业务释义。英文名称用于后续数据库、JSON/YAML、API 和程序实现保持稳定；中文释义用于说明它在政府采购合规审查中的实际含义。


第 3 阶段我们已经建立：

\[
\boxed{
TextChunk
\neq
BusinessClause
}
\]

**中文业务释义：** 检索文本块 ≠ 政府采购业务条款。

并且把真实采购文件恢复为：

\[
\boxed{
Project
\rightarrow
Document
\rightarrow
Version
\rightarrow
Section
\rightarrow
Clause
\rightarrow
Requirement
\rightarrow
BusinessFunction
\rightarrow
EvidenceSpan
}
\]

**中文业务释义：** 采购项目 → 采购文件 → 文档版本 → 章节 → 业务条款 → 业务要求 → 业务功能 / 条款作用 → 证据片段及原文定位。

现在终于进入第十一课最核心的业务规则阶段之一：

# “采购人设置差别歧视条款”
## 采购文件专项合规检查

本阶段的正式业务来源是：

```text
《2025年政府采购领域“四类”违法违规行为专项整治工作指引》

第二部分 检查规范
一、关于采购人设置差别歧视条款问题

附件9
处理处罚标准
```

该工作指引正文明确要求：

> 对采购文件、采购公告的具体内容进行全面检查，重点包括采购需求、资格要求、实质性条款以及评分标准等。

正文归纳为：

\[
\boxed{
7\ 类违法违规问题
}
\]

附件 9 又进一步展开为：

\[
\boxed{
22\ 项具体表现形式
}
\]

数量结构：

\[
\boxed{
2+2+4+2+2+3+7=22
}
\]

**中文业务释义：** 2+2+4+2+2+3+7=22。

因此本阶段第一条、也是最高优先级边界正式锁定为：

\[
\boxed{
22项
\neq
22个关键词
}
\]

本阶段最终形成：

# `ProcurementDiscrimination22RuleSet_V1`

---

# 一、先把附件 9 的业务层级锁死

正确结构是：

\[
\boxed{
“四类”专项整治
\supset
采购人设置差别歧视条款
\supset
7类问题
\supset
22项具体表现形式
}
\]

这意味着：

> D01～D22 不是 22 个互不相关的标签。

它们有：

```text
上位专项
一级问题类别
具体表现形式
处理依据
处罚依据
处理建议
责任主体
```

等正式来源关系。

因此：

\[
\boxed{
RuleID
必须保留
SourceHierarchy
}
\]

---

# 二、7 类问题与 22 项具体表现形式

下面的 D01～D22，是对附件 9“表现形式”逐项建立的工程 Rule ID。

这里的目的不是改写附件 9，

而是：

> 给每一项具体表现形式建立稳定、可版本化、可测试的机器标识。

---

# 第一类
# 直接或变相对外地企业进入本地市场设置阻碍
## 2 项

## D01
### 注册地、距离、行政区域内分支机构等不合理资格条件或评审因素

附件 9 表现形式：

> 采购文件设置供应商注册地、所在地距离采购人的距离、在某行政区域内设立分支机构等不合理的资格条件、评审因素。

典型结构：

```text
Subject    # 中文：主体
供应商

RestrictionType    # 中文：限制类型
地域 / 本地存在性

BusinessFunction    # 中文：业务功能
ENTRY_GATE / SCORING_FACTOR    # 中文：准入门槛 / 评分因素

Timing    # 中文：适用 / 发生时点
通常发生在投标前或评审阶段
```

重点不是只搜：

```text
“本地”
“分公司”
```

而是判断：

```text
是否要求投标前满足
是否作为资格门槛
是否作为评分因素
是否限制外地企业进入
是否存在明确业务必要性或特别依据
```

---

## D02
### 特定行政区域或特定主体的业绩、奖励作为加分、中标或成交条件

附件 9 表现形式：

> 采购文件将特定行政区域或特定主体的业绩、奖励作为加分条件或中标、成交条件。

需要结构化识别：

```text
ExperienceRegion    # 中文：业绩地域限制

AwardRegion    # 中文：奖项地域限制

SpecificEntity    # 中文：特定主体限制

ScoreBonus    # 中文：评分加分

WinningCondition    # 中文：中标 / 成交条件
```

所以：

\[
\boxed{
ExperienceRequirement
\neq
RegionalExperienceRestriction
}
\]

**中文业务释义：** 业绩要求 ≠ 地域业绩限制。

---

# 第二类
# 限定供应商所在行业或限制其他行业供应商参与竞争
## 2 项

## D03
### 特定行业的业绩、奖励作为资格条件或评审因素

附件 9 表现形式：

> 采购文件将特定行业的业绩、奖励作为资格条件或评审因素。

系统必须区分：

```text
与项目履约能力直接相关的类似经验
```

与：

```text
无充分依据限定只能来自某一行业的业绩 / 奖励
```

所以：

\[
\boxed{
RelevantExperience
\neq
IndustryLockIn
}
\]

**中文业务释义：** 相关履约经验 ≠ 行业锁定。

---

## D04
### 除特别规定外，将营业执照经营范围作为资格条件或评审因素

附件 9 表现形式：

> 除特别规定外，采购文件将营业执照经营范围作为资格条件或评审因素。

这里有一个非常重要的规则组件：

```text
ExceptionCondition    # 中文：例外条件
=
除特别规定外
```

因此不能做成：

```text
出现“营业执照经营范围”
→ 自动违规
```

而必须：

\[
\boxed{
Trigger
+
ExceptionCheck
}
\]

**中文业务释义：** 触发条件 + 例外检查。

---

# 第三类
# 设置对企业规模的不合理限制以排斥中小企业
## 4 项

## D05
### 经营年限、注册资本、资产总额、营业收入、从业人员、利润、纳税额等规模条件作为资格要求或评审因素

附件 9 表现形式：

> 采购文件将经营年限、注册资本、资产总额、营业收入、从业人员、利润、纳税额等规模条件作为资格要求或评审因素。

这是典型：

# Multi-trigger Rule
## 多触发字段规则

触发对象包括：

```text
OperatingYears    # 中文：经营年限
RegisteredCapital    # 中文：注册资本
TotalAssets    # 中文：资产总额
Revenue    # 中文：营业收入
EmployeeCount    # 中文：从业人员数量
Profit    # 中文：利润
TaxAmount    # 中文：纳税额
```

但最终仍然要识别：

```text
它是不是供应商准入 / 评分条件
```

而不是仅仅：

> 文档里是否出现这些财务字段。

---

## D06
### 特定金额的合同业绩作为资格条件或评审因素

附件 9 表现形式：

> 采购文件将特定金额的合同业绩作为资格条件或评审因素。

这里要结构化：

```text
ExperienceType    # 中文：业绩类型
ContractAmountThreshold    # 中文：合同金额门槛
QualificationOrScoring    # 中文：用于资格条件还是评分因素
TimeWindow    # 中文：时间窗口
ProjectSimilarity    # 中文：项目相似性
```

所以：

\[
\boxed{
PastPerformance
\neq
ArbitraryAmountThreshold
}
\]

**中文业务释义：** 历史业绩 ≠ 任意金额门槛。

---

## D07
### 与规模条件存在直接关联的第三方信用评价、认证等不合理限制

附件 9 表现形式：

> 采购文件设置与规模条件存在直接关联的第三方信用评价、认证等不合理的限制条件。

这条说明：

> 风险可以通过“间接代理变量”出现。

即采购文件可能没有直接写：

```text
注册资本必须达到X
```

而是要求：

```text
某信用等级
某认证
```

但该评价体系本身：

> 与企业规模直接关联。

所以：

\[
\boxed{
ProxyRestriction
也可能构成
ScaleRestriction
}
\]

---

## D08
### 场所面积、营业网点数量及分布等与采购需求无关的条件

附件 9 表现形式：

> 采购文件设置场所面积、营业网点数量及分布等与采购需求无关的资格条件或评审因素。

真正判断关键是：

```text
是否与采购需求有关
```

所以：

\[
\boxed{
PhysicalCapacityRequirement
\neq
AutomaticallyUnreasonable
}
\]

**中文业务释义：** 场所 / 网点等实体能力要求 ≠ 自动视为不合理。

必须建立：

# Relevance Test
## 业务相关性测试

---

# 第四类
# 非法限定供应商的企业形式等
## 2 项

## D09
### 限定供应商所有制形式、组织形式等条件

附件 9 表现形式：

> 采购文件限定供应商的所有制形式、组织形式等条件。

典型字段：

```text
OwnershipType    # 中文：所有制形式
OrganizationForm    # 中文：组织形式
```

风险位置可以出现在：

```text
资格条件
评分标准
实质性条款
```

---

## D10
### 企业股权结构、投资者国别、所在地等不合理条件

附件 9 表现形式：

> 采购文件设置企业股权结构、投资者国别、所在地等不合理条件。

这条需要特别识别：

```text
ShareholdingStructure    # 中文：股权结构
InvestorNationality    # 中文：投资者国别
Location    # 中文：所在地 / 地域
```

同时仍需保留：

```text
是否存在明确法定特殊情形
```

的 Exception Slot。

---

# 第五类
# 指向、限定或指定特定供应商、特定产品等
## 2 项

## D11
### 技术、服务需求指向特定供应商、特定产品

附件 9 表现形式：

> 采购文件中的技术、服务需求指向特定供应商、特定产品。

这里最危险的误区是：

```text
没有出现品牌名
→ 就不存在指向性
```

实际可以通过：

```text
参数组合
接口约束
独有功能
尺寸组合
专有协议
服务体系
```

形成：

# De facto Direction
## 实质指向

因此：

\[
\boxed{
NoBrandName
\neq
NoProductDirection
}
\]

**中文业务释义：** 未出现品牌名 ≠ 不存在产品指向。

---

## D12
### 限定或指定供应商、专利、商标、品牌、原产地、零部件等

附件 9 表现形式：

> 采购文件限定或指定特定的供应商或专利、商标、品牌、原产地、零部件等。

正文还特别提示关注：

```text
“知名”
“一线”
“参考品牌”
```

等表述。

这里至少要抽：

```text
SupplierReference    # 中文：特定供应商指向
PatentReference    # 中文：专利指向
TrademarkReference    # 中文：商标指向
BrandReference    # 中文：品牌指向
OriginReference    # 中文：原产地指向
ComponentReference    # 中文：零部件指向
EquivalentMechanism    # 中文：等效替代机制
```

---

# 第六类
# 设置与采购项目实施不必要或无关的评审标准
## 3 项

## D13
### 资格证书、技术参数、商务条件等与项目具体特点和实际需要不相适应或与合同履行无关

附件 9 表现形式：

> 采购文件设定的资格证书、技术参数、商务条件等需求与采购项目的具体特点和实际需要不相适应或与合同履行无关。

这是 D01～D22 中最典型的：

# Context-sensitive Rule
## 强上下文规则

因为没有一个词：

> 能直接决定违规。

必须判断：

\[
\boxed{
Requirement
\leftrightarrow
ProjectNecessity
}
\]

**中文业务释义：** 业务要求 ↔ 项目实际必要性。

以及：

\[
\boxed{
Requirement
\leftrightarrow
ContractPerformance
}
\]

**中文业务释义：** 业务要求 ↔ 合同履约目标。

---

## D14
### 国务院取消的行政审批事项作为资格条件或评审因素

附件 9 表现形式：

> 采购文件将国务院取消的行政审批事项作为资格条件或评审因素。

这类规则依赖：

# External Registry
## 外部政策 / 审批事项状态库

因为模型仅凭采购文件本身：

> 无法可靠判断某审批事项是否已经取消。

所以：

\[
\boxed{
D14
需要
PolicyRegistry / ExternalReference
}
\]

---

## D15
### AAA 级信用证书、守合同重信用证书或其他行业协会、组织颁发的证书、奖项作为资格条件或评审因素

附件 9 表现形式：

> 采购文件将 AAA 级信用证书、守合同重信用证书或其他行业协会、组织颁发的证书、奖项作为资格条件或评审因素。

这条需要：

```text
CertificateType    # 中文：证书类型
IssuerType    # 中文：出具 / 颁发机构类型
AwardType    # 中文：奖项类型
QualificationOrScoring    # 中文：用于资格条件还是评分因素
```

并继续确认：

> 是否属于附件所指的情形。

---

# 第七类
# 以其他不合理的条件限制或排斥潜在供应商
## 7 项

## D16
### 除采购进口货物外，设置厂家授权、承诺、证明、背书等不合理限制

附件 9 表现形式：

> 除采购进口货物外，采购文件设置厂家授权、承诺、证明、背书等不合理的限制。

这里有明确 Exception：

```text
采购进口货物
```

所以：

\[
\boxed{
ManufacturerAuthorization
+
ImportException
}
\]

**中文业务释义：** 厂家授权 + 进口货物例外。

必须同时判断。

---

## D17
### 供应商备选库、名录库、资格库等作为资格条件

附件 9 表现形式：

> 采购文件将供应商备选库、名录库、资格库等作为资格条件。

结构化对象：

```text
LibraryType    # 中文：库 / 名录类型
MembershipRequired    # 中文：是否要求入库 / 入围
BusinessFunction = ENTRY_GATE    # 中文：业务功能 = 准入门槛
```

---

## D18
### 要求供应商进行不必要的登记、注册等

附件 9 表现形式：

> 要求供应商进行不必要的登记、注册等。

这里的核心词不是：

```text
登记 / 注册
```

而是：

```text
不必要
```

因此必须评：

# Necessity
## 必要性

---

## D19
### 将营业执照、审计报告、资质证书等资格条件证明材料作为获取采购文件的前置条件

附件 9 表现形式：

> 采购文件将营业执照、审计报告、资质证书等资格条件证明材料作为获取采购文件的前置条件。

这是典型：

# Stage Misplacement
## 条件设置阶段错误

重点字段：

```text
RequiredMaterial    # 中文：要求提交的材料
RequiredAtStage    # 中文：要求提交的程序阶段
Consequence    # 中文：不满足时的后果
```

所以：

\[
\boxed{
QualificationMaterial
\neq
DocumentAccessPrerequisite
}
\]

**中文业务释义：** 资格证明材料 ≠ 获取采购文件前置条件。

---

## D20
### 除特别规定外，无正当理由限制技术证明材料的出具机构

附件 9 表现形式：

> 除特别规定外，采购文件无正当理由限制技术证明材料的出具机构等。

至少要判断：

```text
IssuerRestriction    # 中文：出具机构限制
SpecialProvision    # 中文：特别规定
Justification    # 中文：合理性 / 正当理由说明
```

因此：

\[
\boxed{
IssuerRestriction
需要
Exception
+
Justification
}
\]

---

## D21
### 违规要求投标人为特定范围的定点供应商、入围单位等

附件 9 表现形式：

> 采购文件违规要求投标人为特定范围的定点供应商、入围单位等。

结构化：

```text
DesignatedSupplierPool    # 中文：指定供应商范围 / 供应商池
FrameworkMembership    # 中文：框架 / 入围成员资格
EntryGate    # 中文：准入门槛
```

---

## D22
### 设置没有法律依据的黑名单、不良记录名单、违约名单等资格要求

附件 9 表现形式：

> 采购文件设置没有法律依据的黑名单、不良记录名单、违约名单等资格要求。

最关键的判断不是：

```text
是否出现黑名单
```

而是：

```text
该名单是否有法律依据
```

因此：

\[
\boxed{
BlacklistRequirement
WithoutLegalBasis
=
CandidateRisk
}
\]

**中文业务释义：** 黑名单要求 缺乏法律依据 = 候选风险。

它天然需要：

```text
PolicyRegistry    # 中文：政策 / 法规登记库
```

参与。

---

# 三、22 项规则不是同一种类型

D01～D22 至少可以分成不同 Decision Logic 类型。

## Type A
# Direct Structural Rule
## 直接结构型

例如：

```text
D17    # 中文：D17 规则编号（附件9工程化规则标识）
供应商备选库 / 名录库 / 资格库作为资格条件
```

如果结构事实明确，

规则判断相对直接。

---

## Type B
# Exception-sensitive Rule
## 例外敏感型

例如：

```text
D04    # 中文：D04 规则编号（附件9工程化规则标识）
除特别规定外，营业执照经营范围

D16    # 中文：D16 规则编号（附件9工程化规则标识）
除采购进口货物外，厂家授权

D20    # 中文：D20 规则编号（附件9工程化规则标识）
除特别规定外，限制技术证明材料出具机构
```

这类必须：

\[
\boxed{
Trigger
+
ExceptionCheck
}
\]

**中文业务释义：** 触发条件 + 例外检查。

---

## Type C
# Context / Necessity Rule
## 上下文必要性型

例如：

```text
D08    # 中文：D08 规则编号（附件9工程化规则标识）
场所面积 / 营业网点与采购需求是否相关

D13    # 中文：D13 规则编号（附件9工程化规则标识）
资格证书 / 技术参数 / 商务条件是否与实际需要相适应
```

必须：

```text
Project Context    # 中文：项目业务上下文
+
Requirement    # 中文：业务要求
+
Business Necessity    # 中文：业务必要性
```

共同判断。

---

## Type D
# External-status Rule
## 外部状态依赖型

例如：

```text
D14    # 中文：D14 规则编号（附件9工程化规则标识）
国务院取消的行政审批事项

D22    # 中文：D22 规则编号（附件9工程化规则标识）
没有法律依据的黑名单
```

必须查：

```text
Policy Registry    # 中文：政策法规登记库
External Registry    # 中文：外部权威状态库
Effective Status    # 中文：生效状态
```

---

## Type E
# Semantic Direction Rule
## 语义指向型

例如：

```text
D11    # 中文：D11 规则编号（附件9工程化规则标识）
技术 / 服务需求指向特定供应商、特定产品
```

它可能没有明显关键词，

需要综合：

```text
参数组合
市场可满足性
等效产品
上下文
```

因此：

\[
\boxed{
All22Rules
\neq
SameInferenceMethod
}
\]

**中文业务释义：** D01-D22全部规则 ≠ 同一种推理 / 执行方式。

---

# 四、核心心智模型 ①
# `RuleType` 决定 `ExecutionStrategy`

因此每个 Rule Object 必须声明：

```text
execution_mode    # 中文：执行模式
```

例如：

```text
DETERMINISTIC    # 中文：确定性规则执行
SEMANTIC    # 中文：语义判断型执行
CONTEXTUAL    # 中文：上下文判断型执行
EXTERNAL_LOOKUP    # 中文：需要外部权威查询
HYBRID    # 中文：混合执行模式
```

这样 Hybrid Compliance Engine 才知道：

> 这个规则应该交给谁算。

---

# 五、Rule Object 的正式结构

每个 D01～D22 至少要包含：

```text
rule_id    # 中文：规则标识

rule_set_version    # 中文：规则集版本

source_document    # 中文：来源文件

source_section    # 中文：来源章节

source_attachment    # 中文：来源附件

primary_category_id    # 中文：一级问题类别标识

primary_category_name    # 中文：一级问题类别名称

manifestation_text    # 中文：具体表现形式文本

legal_basis_refs    # 中文：法律 / 政策依据引用标识列表

penalty_basis_refs    # 中文：处罚依据引用标识列表

handling_advice_refs    # 中文：处理建议引用标识列表

responsible_party_refs    # 中文：责任主体引用标识列表

document_scope    # 中文：文档适用范围

business_functions    # 中文：业务功能 / 作用

execution_mode    # 中文：执行模式

trigger_schema    # 中文：触发结构定义

context_requirements    # 中文：上下文要求

necessity_check    # 中文：必要性检查

exception_conditions    # 中文：例外条件

external_registry_dependencies    # 中文：外部登记库依赖项

evidence_requirements    # 中文：证据要求

negative_patterns    # 中文：负例模式

hard_negative_patterns    # 中文：高难负例模式

decision_logic    # 中文：决策逻辑

risk_default    # 中文：风险默认

human_review_policy    # 中文：人工复核政策 / 法规

output_schema    # 中文：输出结构定义

test_cases    # 中文：测试样例

effective_from    # 中文：生效起始

effective_to    # 中文：生效截止

rule_status    # 中文：规则状态
```

因此：

\[
\boxed{
Rule
\neq
PromptInstruction
}
\]

**中文业务释义：** 规则 ≠ Prompt中的规则指令。

Rule 是：

> 一个被版本化管理、可以执行、可以测试、可以审计的工程资产。

---

# 六、Source Provenance 必须成为 Rule 的一部分

D01～D22 的 source 不能写成：

```text
“根据政府采购相关规定”
```

而要明确：

```text
source_document    # 中文：来源文件
=
2025年政府采购领域“四类”违法违规行为专项整治工作指引

source_section    # 中文：来源章节
=
第二部分 检查规范
一、关于采购人设置差别歧视条款问题

source_attachment    # 中文：来源附件
=
附件9

source_column    # 中文：来源表格列 / 来源字段
=
表现形式
```

必要时还要链接：

```text
处理依据
处罚依据
处理建议
责任主体
```

所以：

\[
\boxed{
RuleWithoutProvenance
=
WeakComplianceAsset
}
\]

**中文业务释义：** 缺少来源链的规则 = 薄弱的合规资产。

---

# 七、附件 9 中的“处理依据”怎样进入 RuleSet？

附件 9 不只列：

```text
违法违规问题
表现形式
```

还列：

```text
处理依据
处罚依据
处理建议
责任主体
```

因此一个 Rule Finding 最终应该能追踪：

\[
\boxed{
Finding
\rightarrow
Dxx
\rightarrow
Manifestation
\rightarrow
HandlingBasis
}
\]

**中文业务释义：** 合规发现项 → Dxx规则 → 具体表现形式 → 处理依据。

但必须注意：

> RuleSet 不应擅自把所有来源“压缩成一句法律结论”。

应该保存原始引用关系。

例如附件 9 将不同问题关联到：

```text
《中华人民共和国政府采购法》

《中华人民共和国政府采购法实施条例》

《中华人民共和国中小企业促进法》

《中华人民共和国外商投资法》

《中华人民共和国外商投资法实施条例》

《政府采购货物和服务招标投标管理办法》

财库〔2019〕38号

财库〔2020〕46号

财库〔2021〕35号
```

等处理依据。

具体 Finding 时：

> 再由 Policy Registry 解析适用版本和有效状态。

---

# 八、核心心智模型 ②
# `InspectionRule` 和 `LegalBasis` 必须分层

D01～D22 是：

# Inspection Rule
## 专项检查规则

而：

```text
政府采购法
实施条例
部门规章
政策文件
```

是：

# Legal / Policy Basis
## 法律与政策依据

所以：

\[
\boxed{
InspectionRule
\neq
LegalProvision
}
\]

**中文业务释义：** 专项检查规则 ≠ 法律 / 政策条文。

但二者必须可追踪连接。

---

# 九、Trigger 到底是什么？

# Trigger
## 规则触发条件

不是只有 Keyword。

可以包括：

```text
Lexical Trigger    # 中文：词语 / 表述触发器
词语

Structural Trigger    # 中文：结构型触发
业务结构

Numeric Trigger    # 中文：数值触发器
数值条件

Role Trigger    # 中文：业务角色触发
资格 / 评分 / 实质性门槛

Temporal Trigger    # 中文：程序时点 / 时间触发器
投标前 / 中标后

External Trigger    # 中文：外部触发
政策状态

Semantic Trigger    # 中文：语义触发
语义指向
```

例如 D01：

```text
注册地
+
资格门槛
```

比：

```text
只出现“注册地”
```

强得多。

---

# 十、核心心智模型 ③
# `Trigger` 的目标是召回候选，不是直接宣判

所以：

\[
\boxed{
Trigger
\rightarrow
Candidate
}
\]

**中文业务释义：** 触发条件 → 候选。

而不是：

\[
\boxed{
Trigger
\rightarrow
Violation
}
\]

**中文业务释义：** 触发条件 → Violation。

这能显著降低：

> Keyword Matching 带来的误报。

---

# 十一、Context Requirements

每个 Rule 必须声明：

> 做判断时需要哪些上下文。

例如 D13：

```text
采购项目具体特点

实际采购需要

合同履行目标

当前Requirement

SectionRole    # 中文：章节业务角色

BusinessFunction    # 中文：业务功能
```

缺一个关键上下文：

> 可能无法可靠判断。

所以 Rule Object 需要：

```text
required_context_fields    # 中文：必需上下文字段
```

---

# 十二、核心心智模型 ④
# `MissingContext` 必须能让规则 Abstain

如果 D13 缺少：

```text
采购需求
```

却要判断：

> 某技术参数是否与实际需要不相适应，

系统应该：

```text
UNRESOLVED    # 中文：无法确定 / 待解决
```

或者：

```text
NEEDS_HUMAN_REVIEW    # 中文：需要人工复核
```

而不是强行：

```text
COMPLIANT / NON_COMPLIANT    # 中文：合规 / 不合规（二值状态示例；复杂规则不应只依赖二值）
```

所以：

\[
\boxed{
MissingRequiredContext
\Rightarrow
NoForcedDecision
}
\]

**中文业务释义：** MissingRequired上下文 ⇒ 无/未Forced判断。

---

# 十三、Exception 必须是一级字段

D04：

```text
除特别规定外
```

D16：

```text
除采购进口货物外
```

D20：

```text
除特别规定外
```

这些不是备注。

而是：

# Exception Logic
## 例外逻辑

必须进入：

```text
exception_conditions    # 中文：例外条件
exception_evidence    # 中文：例外证据
exception_status    # 中文：例外状态
```

状态可以：

```text
NO_EXCEPTION_FOUND    # 中文：未发现适用例外

POSSIBLE_EXCEPTION    # 中文：可能存在例外

EXCEPTION_CONFIRMED    # 中文：已确认适用例外

EXCEPTION_UNRESOLVED    # 中文：例外情况尚无法确认
```

---

# 十四、核心心智模型 ⑤
# `Exception` 不是模型自由发挥的“但是”

例外必须：

```text
有来源
有条件
有证据
有适用性
```

因此：

\[
\boxed{
Exception
=
RuleCondition
+
Evidence
+
PolicySupport
}
\]

**中文业务释义：** 例外 = 规则条件 + 证据 + 政策支持。

---

# 十五、Business Necessity

附件与正文中大量判断使用：

```text
不合理
不必要
与实际需要不相适应
与合同履行无关
无正当理由
```

这些词说明：

> 很多 Rule 不是简单形式规则。

它们需要：

# Business Necessity Analysis
## 项目必要性分析

可以拆成：

```text
Purpose    # 中文：采购业务目的
为什么需要？

Relation    # 中文：关联
与项目目标有什么关系？

Proportionality    # 中文：比例性 / 限制强度是否相称
限制程度是否与需求相称？

Alternative    # 中文：更少排斥竞争的替代方案
有没有更少排斥的表达方式？

CompetitionImpact    # 中文：竞争影响
会排除多少合理竞争者？

Evidence    # 中文：证据
采购人有没有事实依据？
```

---

# 十六、核心心智模型 ⑥
# `Necessity` 必须被解释，不应该只是一个分数

不能：

```text
necessity_score = 0.62    # 中文：必要性评分 = 062
```

然后结束。

必须至少输出：

```text
necessity_claim    # 中文：必要性说明 / 主张

supporting_evidence    # 中文：支持性证据

counter_evidence    # 中文：反向 / 反证证据

alternative_requirement    # 中文：替代方案要求

uncertainty    # 中文：不确定
```

---

# 十七、Competition Impact

差别歧视条款的核心业务后果之一是：

> 不合理限制或排斥潜在供应商公平参与。

所以每个候选 Finding 可以抽：

```text
competition_impact    # 中文：竞争影响

entry_barrier    # 中文：是否形成市场准入障碍

supplier_scope_reduction    # 中文：潜在供应商范围收窄程度

product_scope_reduction    # 中文：可竞争产品范围收窄程度

regional_restriction    # 中文：地域限制情况

industry_restriction    # 中文：行业限制情况

scale_restriction    # 中文：企业规模限制情况
```

但注意：

> 这些字段是分析信息，不代表自动完成法律定性。

---

# 十八、Hard Negative 为什么是 D01-D22 最重要的数据之一？

如果只训练：

```text
明显违规
```

模型会变成：

> 看到敏感词就报风险。

真正困难的是：

# Hard Negative
## 高难负例

例如：

```text
出现“本地”
但只是描述项目履约地点

出现“品牌”
但不是限定供应商品牌

出现“业绩”
但要求与实际履约能力合理相关

出现“授权”
但属于规则明确的例外情形
```

因此：

\[
\boxed{
GoodRuleSystem
需要
Positive
+
HardNegative
+
ExceptionCase
}
\]

---

# 十九、Counterfactual Pair

# Counterfactual
## 反事实样本

例如：

### A

```text
供应商投标前必须在本市设立分公司。
```

### B

```text
中标供应商应根据履约需要，在合同约定期限内建立满足服务响应要求的服务能力。
```

只改变：

```text
Timing    # 中文：适用 / 发生时点
Subject State    # 中文：主体 / 事项状态
Business Necessity    # 中文：业务必要性
```

结论可能改变。

所以：

\[
\boxed{
CounterfactualPair
帮助模型学习
DecisionBoundary
}
\]

---

# 二十、Rule Decision State

建议每个 Dxx 的执行结果不只：

```text
true / false    # 中文：正确 / 真 / 错误 / 假
```

而是：

```text
NOT_CHECKED    # 中文：尚未检查

NOT_APPLICABLE    # 中文：不适用

CHECKED_NO_TRIGGER    # 中文：已检查，未触发规则

CANDIDATE_HIT    # 中文：命中候选规则

CONTEXT_INSUFFICIENT    # 中文：上下文不足

EXCEPTION_POSSIBLE    # 中文：可能存在例外

NEEDS_HUMAN_REVIEW    # 中文：需要人工复核

FINDING_SUPPORTED    # 中文：证据支持形成发现项

FINDING_REJECTED    # 中文：经复核不支持形成发现项
```

这样：

\[
\boxed{
RuleExecutionState
\neq
BinaryLabel
}
\]

**中文业务释义：** 规则执行状态 ≠ Binary标签。

---

# 二十一、核心心智模型 ⑦
# `FindingSupported` 必须经过 Evidence Gate

一个 Rule 最终进入：

```text
FINDING_SUPPORTED    # 中文：证据支持形成发现项
```

至少要有：

```text
matched_clause    # 中文：命中条款

evidence_span    # 中文：证据片段及原文定位

document_version    # 中文：文档版本

business_role    # 中文：业务业务角色

rule_id    # 中文：规则标识

source_manifestation    # 中文：来源具体表现形式

applicable_policy    # 中文：适用政策 / 法规

reason    # 中文：原因 / 说明

exception_status    # 中文：例外状态
```

缺关键字段：

> 不能进入高置信正式 Finding。

---

# 二十二、Decision Logic 的标准流程

每个 Rule 可以共享一个外层状态机：

\[
\boxed{
Applicable?
\rightarrow
Trigger?
\rightarrow
ContextEnough?
\rightarrow
Exception?
\rightarrow
Necessity?
\rightarrow
EvidenceEnough?
\rightarrow
Decision
}
\]

**中文业务释义：** 适用? → 触发条件? → 上下文是否充分? → 例外? → 必要性? → 证据是否充分? → 判断结论。

中文：

```text
1. 这个Rule对当前对象适用吗？
2. 是否出现候选触发？
3. 判断需要的上下文够不够？
4. 有没有例外？
5. 是否有合理项目必要性？
6. 证据是否充分？
7. 形成Finding还是转人工？
```

---

# 二十三、规则不要直接写在 Prompt 里

最危险的实现：

```text
System Prompt:    # 中文：系统提示词：
请记住以下22项规定……
```

问题：

```text
规则无法独立版本化

无法逐项测试

无法记录执行状态

无法单独热更新

难以审计

容易被Prompt变化影响
```

所以：

\[
\boxed{
RuleSet
\neq
LongSystemPrompt
}
\]

**中文业务释义：** 规则集合 ≠ LongSystem提示词。

---

# 二十四、Rule Engine 怎样调用 LLM？

正确方式不是：

```text
LLM负责全部D01-D22
```

而是：

```text
Rule Engine    # 中文：规则引擎
先确定需要检查哪个Rule
↓
准备结构化上下文
↓
必要时调用LLM Judge
↓
要求结构化输出
↓
Evidence Validator验证
↓
Rule Engine更新状态
```

所以：

\[
\boxed{
LLM
是
RuleExecutor的一部分
}
\]

而不是：

\[
\boxed{
LLM
=
RuleSet本身
}
\]

---

# 二十五、D01-D22 规则矩阵

第一版执行策略可以这样规划：

| Rule | 一级问题 | 主要判断类型 | 关键依赖 |
|---|---|---|---|
| D01 | 外地市场障碍 | 结构 + 语义 + 必要性 | Qualification / Scoring / Timing |
| D02 | 外地市场障碍 | 结构 + 地域约束 | Scoring / Award / Experience |
| D03 | 行业限制 | 结构 + 语义 | Industry / Experience / Award |
| D04 | 行业限制 | 结构 + 例外 | Business Scope / Exception |
| D05 | 企业规模 | 确定性字段 + 业务角色 | Financial / Scale Fields |
| D06 | 企业规模 | 数值 + 业绩结构 | Contract Amount / Experience |
| D07 | 企业规模 | 外部规则 + 代理限制 | Credit / Certification |
| D08 | 企业规模 | 必要性 | Premises / Outlets / Project Need |
| D09 | 企业形式 | 结构型 | Ownership / Organization |
| D10 | 企业形式 | 结构 + 例外 | Shareholding / Nationality / Location |
| D11 | 指向供应商产品 | 语义指向 | Technical / Service / Market Context |
| D12 | 指定特定对象 | 结构 + 语义 | Patent / Trademark / Brand / Origin |
| D13 | 无关评审标准 | 强上下文 / 必要性 | Project Need / Contract Performance |
| D14 | 无关评审标准 | 外部状态查询 | Policy Registry |
| D15 | 无关评审标准 | 结构 + 证书来源 | Certificate / Award / Issuer |
| D16 | 其他限制 | 结构 + 例外 | Manufacturer Authorization / Import |
| D17 | 其他限制 | 直接结构型 | Supplier Library Membership |
| D18 | 其他限制 | 必要性 | Registration Requirement |
| D19 | 其他限制 | 阶段逻辑 | Material / Document Access Stage |
| D20 | 其他限制 | 结构 + 例外 + 理由 | Proof Issuer |
| D21 | 其他限制 | 直接结构型 | Designated / Shortlisted Supplier |
| D22 | 其他限制 | 外部法律依据 | Blacklist / Policy Registry |

这张表非常重要。

它说明：

\[
\boxed{
D01-D22
不是一个单一分类任务
}
\]

而是：

> 多种规则执行问题的集合。

---

# 二十六、RuleSet 版本化

建议：

```text
ProcurementDiscrimination22RuleSet_V1.0.0    # 中文：附件9差别歧视22项规则集 V1.0.0
```

后面如果：

```text
只修正描述
→ Patch    # 中文：→ Patch：补丁版本，仅修正不改变规则含义的问题

增加不改变旧语义的检测字段
→ Minor    # 中文：→ Minor：次版本，增加兼容性能力 / 字段

规则来源、逻辑、适用范围重大变化
→ Major    # 中文：→ Major：主版本，规则来源、逻辑或适用范围发生重大变化
```

每个 Finding 必须记录：

```text
rule_set_version    # 中文：规则集版本
rule_version    # 中文：规则版本
```

所以：

\[
\boxed{
RuleUpdate
\neq
SilentChange
}
\]

**中文业务释义：** 规则更新 ≠ 静默变更。

---

# 二十七、Rule Hot Update

后面生产系统需要：

# Rule Hot Update
## 规则热更新

即：

> 不重新训练整个模型，也能更新规则资产。

适合：

```text
法规状态变化
政策新增例外
Rule Trigger更新
处理依据版本变化
```

但：

> 热更新之后必须重新跑受影响 Benchmark Slice。

所以：

\[
\boxed{
HotUpdate
\Rightarrow
TargetedRegression
}
\]

**中文业务释义：** 规则热更新 ⇒ 定向回归测试。

---

# 二十八、D01-D22 与 Policy Registry 的连接

Rule Object 里不要复制一份：

> 永远不变的法规全文。

而应存：

```text
legal_basis_ref_ids    # 中文：法律 / 政策依据REF标识列表
```

连接：

```text
ProcurementPolicyRegistry_V1    # 中文：采购政策 / 法规登记库V1
```

执行时：

\[
\boxed{
Rule
\rightarrow
PolicyResolver
\rightarrow
ApplicableProvision
}
\]

**中文业务释义：** 规则 → 政策Resolver → 适用条文。

这样法规更新：

> 不需要在 22 条规则里手工同步 22 份副本。

---

# 二十九、核心心智模型 ⑧
# `RuleLogic` 和 `PolicyText` 解耦，但不能脱链

理想结构：

\[
\boxed{
ExecutableLogic
\leftrightarrow
SourceManifestation
\leftrightarrow
ApplicableLegalBasis
}
\]

**中文业务释义：** 可执行逻辑 ↔ 来源中的具体表现形式 ↔ 适用法律政策依据。

既能执行，

又能解释来源。

---

# 三十、D01-D22 与 Document Schema 的连接

Stage 3 已经给出：

```text
Clause    # 中文：条款
Requirement    # 中文：业务要求
BusinessFunction    # 中文：业务功能
Timing    # 中文：适用 / 发生时点
EvidenceSpan    # 中文：证据片段及原文定位
```

Stage 4 的 Rule Input 就应该直接读这些结构。

例如 D19：

```text
RequiredMaterial    # 中文：要求提交的材料
=
AuditReport    # 中文：审计报告

BusinessFunction    # 中文：业务功能
=
DOCUMENT_ACCESS_GATE    # 中文：文档获取门槛

Timing    # 中文：适用 / 发生时点
=
BEFORE_DOCUMENT_ACCESS    # 中文：之前文档获取
```

然后才判断：

> 是否属于附件 9 所指的“作为获取采购文件的前置条件”。

所以：

\[
\boxed{
StructuredFact
\rightarrow
RuleDecision
}
\]

**中文业务释义：** 结构化业务事实 → 规则判断。

比：

\[
\boxed{
RawText
\rightarrow
Guess
}
\]

**中文业务释义：** 原始文本 → 模型猜测。

可靠得多。

---

# 三十一、一个完整 D01 Rule Object 示例

概念上：

```text
rule_id    # 中文：规则标识
=
D01    # 中文：D01 规则编号（附件9工程化规则标识）

category    # 中文：类别
=
直接或变相对外地企业进入本地市场设置阻碍

manifestation    # 中文：具体表现形式
=
采购文件设置供应商注册地、所在地距离采购人的距离、
在某行政区域内设立分支机构等不合理的资格条件、评审因素

execution_mode    # 中文：执行模式
=
HYBRID    # 中文：混合执行模式

document_scope    # 中文：文档适用范围
=
QUALIFICATION / SCORING    # 中文：资格条件章节 / 评分标准章节

trigger_fields    # 中文：触发字段
=
supplier_registration_location    # 中文：供应商注册 / 登记位置 / 地域
distance_to_purchaser    # 中文：供应商所在地到采购人的距离
required_local_branch    # 中文：是否需要地方 / 本地分支机构

required_context    # 中文：必需上下文
=
business_function    # 中文：业务功能
timing    # 中文：时点
project_need    # 中文：项目实际需要

exception_policy    # 中文：例外政策 / 法规
=
source-defined / policy-resolved    # 中文：由来源规则定义 / 由 Policy Registry 确认适用状态

decision    # 中文：决策
=
candidate    # 中文：候选
→ context    # 中文： → 上下文
→ necessity    # 中文： → 必要性
→ evidence    # 中文： → 证据
→ human_if_needed    # 中文：→ 必要时转人工复核
```

注意：

> 这是工程表达，不是重新制定法律规则。

---

# 三十二、一个完整 D16 Rule Object 示例

```text
rule_id    # 中文：规则标识
=
D16    # 中文：D16 规则编号（附件9工程化规则标识）

manifestation    # 中文：具体表现形式
=
除采购进口货物外，
采购文件设置厂家授权、承诺、证明、背书等不合理的限制

execution_mode    # 中文：执行模式
=
HYBRID    # 中文：混合执行模式

trigger    # 中文：触发
=
manufacturer_authorization    # 中文：厂家授权
manufacturer_commitment    # 中文：厂家承诺
manufacturer_certificate    # 中文：厂家证书
manufacturer_endorsement    # 中文：厂家背书

exception    # 中文：例外
=
procurement_of_imported_goods    # 中文：是否属于采购进口货物

required_context    # 中文：必需上下文
=
procurement_category    # 中文：采购类别
import_status    # 中文：进口状态
business_function    # 中文：业务功能
```

这里：

\[
\boxed{
Exception
是Rule的一部分
}
\]

不是后处理备注。

---

# 三十三、Rule Test Case 怎样设计？

每条 Dxx 至少应有：

```text
Positive    # 中文：正例

Hard Positive    # 中文：高难正例

Negative    # 中文：普通负例

Hard Negative    # 中文：高难负例

Exception    # 中文：例外条件

Missing Context    # 中文：上下文缺失样本

Cross-section    # 中文：跨章节样本

Table-based    # 中文：表格型样本

OCR Noise    # 中文：OCR 噪声样本

Adversarial Paraphrase    # 中文：对抗性改写样本
```

所以每条规则不是：

> 一两个例句。

而是一组：

# Rule Test Suite
## 规则测试集

---

# 三十四、核心心智模型 ⑨
# `RuleCoverage` 不等于 `RuleReliability`

22 条都有代码：

> 叫 Coverage。

每条在：

```text
正例
负例
边界例
例外
OCR噪声
跨章节
```

都稳定：

> 才叫 Reliability。

因此：

\[
\boxed{
Implemented
\neq
Validated
}
\]

**中文业务释义：** 已实现 ≠ 已验证。

---

# 三十五、D01-D22 的 Benchmark 必须逐项切 Slice

后面第 15 阶段至少要有：

```text
D01 Recall / Precision    # 中文：D01召回率 / 精确率
D02 Recall / Precision    # 中文：D02召回率 / 精确率
...
D22 Recall / Precision    # 中文：D22召回率 / 精确率
```

还要看：

```text
Category1    # 中文：类别1
...
Category7    # 中文：类别7
```

以及：

```text
Qualification    # 中文：资格条件
Technical    # 中文：技术
Scoring    # 中文：评分
Table    # 中文：表格
OCR    # 中文：OCR
HardNegative    # 中文：高难负例
Exception    # 中文：例外条件
```

所以：

\[
\boxed{
Overall22Score
\neq
PerRuleReliability
}
\]

**中文业务释义：** 22项总体得分 ≠ 逐规则可靠性。

---

# 三十六、False Negative 为什么要重点记录？

如果：

> 某一高风险表现形式真实存在，

系统没发现，

就是：

# False Negative
## 漏检

对于合规预审：

> 漏检可能让风险进入后续采购流程。

因此每个 Rule 都要明确：

```text
FN examples    # 中文：漏检（False Negative）样例
FN root cause    # 中文：漏检根因
FN severity    # 中文：FN严重程度
```

---

# 三十七、False Positive 也不能忽视

如果系统：

> 看到“品牌”“业绩”“本地”就报警，

会导致：

```text
大量人工复核
规则系统失去可信度
业务人员不再使用
```

所以：

\[
\boxed{
HighRecall
\neq
UsefulSystem
}
\]

**中文业务释义：** 高召回率 ≠ 真正可用的系统。

必须在：

```text
Recall    # 中文：召回率
Precision    # 中文：精确率
Human Review Load    # 中文：人工复核工作量
```

之间设计业务工作点。

---

# 三十八、Human Review Policy

建议规则层至少有：

```text
AUTO_CLEAR_ALLOWED    # 中文：允许自动判定无风险

AUTO_FINDING_ALLOWED    # 中文：允许自动形成发现项

HUMAN_CONFIRM_REQUIRED    # 中文：必须人工确认

HUMAN_ON_UNCERTAINTY    # 中文：不确定时转人工

HUMAN_ALWAYS    # 中文：始终需要人工复核
```

例如：

> 强上下文、强裁量规则，

可以默认：

```text
HUMAN_CONFIRM_REQUIRED    # 中文：必须人工确认
```

而不是追求：

> 全自动。

---

# 三十九、核心心智模型 ⑩
# `AutomationRate` 不是合规系统第一目标

真正目标：

\[
\boxed{
ReliableRiskControl
}
\]

**中文业务释义：** 可靠风险控制。

而不是：

\[
\boxed{
100\%Automation
}
\]

**中文业务释义：** 100\%自动化。

---

# 四十、最终 Finding 怎样表达？

一个 Dxx Finding 至少：

```text
finding_id    # 中文：发现项标识

rule_id    # 中文：规则标识

rule_version    # 中文：规则版本

rule_set_version    # 中文：规则集版本

primary_category    # 中文：一级问题类别

manifestation    # 中文：具体表现形式

document_id    # 中文：文档标识
document_version    # 中文：文档版本

clause_id    # 中文：条款标识
requirement_id    # 中文：要求标识

matched_text    # 中文：命中文本
evidence_span    # 中文：证据片段及原文定位

trigger_facts    # 中文：触发事实

context_facts    # 中文：上下文事实

business_necessity    # 中文：业务必要性

competition_impact    # 中文：竞争影响

exception_status    # 中文：例外状态

legal_basis_refs    # 中文：法律 / 政策依据引用标识列表

policy_snapshot_id    # 中文：政策法规快照标识

decision_state    # 中文：决策状态

risk_level    # 中文：风险等级

confidence    # 中文：置信度

reasoning_summary    # 中文：判断理由摘要

recommended_revision    # 中文：建议修改方案

human_review_required    # 中文：是否需要人工复核

audit_trace    # 中文：审计追踪
```

---

# 四十一、Recommended Revision 不能脱离原始问题

修改建议应该做到：

```text
保留真实采购目的
删除不合理限制
尽量使用功能 / 性能 / 履约目标表达
避免扩大采购需求
保留必要条件
```

所以：

\[
\boxed{
Remediation
\neq
DeleteRequirement
}
\]

**中文业务释义：** 修改建议 ≠ 删除要求。

更专业的是：

\[
\boxed{
Remediation
=
PreserveNeed
+
RemoveUnreasonableRestriction
}
\]

**中文业务释义：** 修改建议 = 保留真实采购需求 + 移除不合理限制。

---

# 四十二、核心心智模型 ⑪
# 合规 AI 不能只会“找错”，还要能帮助“改对”

但修改建议仍然必须：

> 明确标记为建议。

高风险或复杂场景：

> 需要采购业务人员 / 法务 / 合规人员确认。

---

# 四十三、本阶段正式工程产物
# `ProcurementDiscrimination22RuleSet_V1`

建议目录：

```text
ProcurementDiscrimination22RuleSet_V1/    # 中文：ProcurementDiscrimination22RuleSet_V1：附件9差别歧视22项规则集根目录

├── rules/    # 中文：工程目录：规则
│   ├── D01.yaml    # 中文：工程文件：D01YAML 配置文件
│   ├── D02.yaml    # 中文：工程文件：D02YAML 配置文件
│   ├── ...
│   └── D22.yaml    # 中文：工程文件：D22YAML 配置文件
│
├── taxonomy/    # 中文：工程目录：分类体系
│   ├── category_01.yaml    # 中文：工程文件：类别01YAML 配置文件
│   ├── ...
│   └── category_07.yaml    # 中文：工程文件：类别07YAML 配置文件
│
├── sources/    # 中文：工程目录：来源材料
│   ├── source_document.json    # 中文：工程文件：来源文件JSON 配置文件
│   ├── attachment9_mapping.json    # 中文：工程文件：附件9mappingJSON 配置文件
│   └── legal_basis_refs.json    # 中文：工程文件：法律 / 政策依据引用标识列表JSON 配置文件
│
├── schemas/    # 中文：工程目录：结构定义
│   ├── rule_schema.json    # 中文：工程文件：规则结构定义JSON 配置文件
│   ├── execution_state.json    # 中文：工程文件：执行状态JSON 配置文件
│   └── finding_schema.json    # 中文：工程文件：发现项结构定义JSON 配置文件
│
├── tests/    # 中文：工程目录：测试集
│   ├── positive/    # 中文：工程目录：正例
│   ├── hard_negative/    # 中文：工程目录：高难负例
│   ├── exception/    # 中文：工程目录：例外
│   └── missing_context/    # 中文：工程目录：缺失上下文
│
└── manifest.json    # 中文：工程文件：清单 / 元数据JSON 配置文件
```

---

# 四十四、Rule Schema 第一版

```text
rule_id    # 中文：规则标识

name    # 中文：名称

category_id    # 中文：类别标识

category_name    # 中文：类别名称

manifestation_text    # 中文：具体表现形式文本

source_document_id    # 中文：来源文件标识

source_location    # 中文：来源位置

legal_basis_refs    # 中文：法律 / 政策依据引用标识列表

execution_mode    # 中文：执行模式

document_scope    # 中文：文档适用范围

business_functions    # 中文：业务功能 / 作用

trigger_schema    # 中文：触发结构定义

required_context_fields    # 中文：必需上下文字段

necessity_check    # 中文：必要性检查

exception_conditions    # 中文：例外条件

external_dependencies    # 中文：外部依赖项

evidence_requirements    # 中文：证据要求

decision_logic    # 中文：决策逻辑

decision_states    # 中文：规则执行 / 决策状态集合

default_risk_level    # 中文：默认风险等级

human_review_policy    # 中文：人工复核政策 / 法规

remediation_policy    # 中文：修改建议政策 / 法规

test_suite_id    # 中文：测试集标识

rule_version    # 中文：规则版本

effective_from    # 中文：生效起始

effective_to    # 中文：生效截止

status    # 中文：状态
```

---

# 四十五、本阶段最重要的 14 个核心心智模型

> **心智模型 ①：`22项 ≠ 22个关键词`。附件 9 的 22 项是 7 类问题下的 22 种具体表现形式。**

> **心智模型 ②：`Rule ≠ PromptInstruction`。每个 Dxx 必须是可版本化、可执行、可测试、可审计的 Rule Object。**

> **心智模型 ③：`InspectionRule ≠ LegalProvision`。专项检查规则与法律政策依据必须分层，但保持可追踪。**

> **心智模型 ④：`Trigger → Candidate`，不是 `Trigger → Violation`。触发器负责召回候选，不负责最终宣判。**

> **心智模型 ⑤：`All22Rules ≠ SameInferenceMethod`。有的规则偏确定性、有的依赖例外、有的依赖政策状态、有的需要强语义与项目必要性判断。**

> **心智模型 ⑥：`MissingRequiredContext ⇒ NoForcedDecision`。上下文不够时必须允许 Abstain / Human Review。**

> **心智模型 ⑦：`Exception` 是 Rule 的一级逻辑，不是模型自由生成的“但是”。**

> **心智模型 ⑧：`Necessity` 必须有理由和证据，不能只输出一个不可解释分数。**

> **心智模型 ⑨：`RuleHit ≠ FinalViolation`。命中后仍要做 Context、Necessity、Exception、Evidence 检查。**

> **心智模型 ⑩：`Parser ≠ RuleEngine ≠ LLMJudge`。文档事实恢复、规则执行、语义裁量必须分层。**

> **心智模型 ⑪：`RuleUpdate ≠ SilentChange`。规则版本变化必须可追踪，并触发受影响 Slice 的回归测试。**

> **心智模型 ⑫：`Implemented ≠ Validated`。22 条有代码不等于 22 条可靠。**

> **心智模型 ⑬：`Overall22Score ≠ PerRuleReliability`。D01～D22 必须逐项看 Recall、Precision、Hard Negative 和 Exception。**

> **心智模型 ⑭：`AutomationRate ≠ ComplianceQuality`。政府采购合规系统追求的是可靠风险控制，而不是 100% 自动判断。**

---

# 四十六、把 D01-D22 整体工程链压成一张图

```text
                 Attachment 9    # 中文：附件9
                   附件9
                      │
                      ▼
                7 Categories    # 中文：7 类一级问题
                   7类问题
                      │
                      ▼
                   D01-D22    # 中文：D01D22
                22项表现形式
                      │
                      ▼
                  Rule Object    # 中文：规则对象
          来源 / Trigger / Context
          Exception / Evidence / Logic    # 中文：例外条件 / 证据 / 逻辑
                      │
                      ▼
              ProcurementDocumentSchema    # 中文：采购文档结构定义
         Clause / Requirement / Function    # 中文：条款 / 业务要求 / 功能 / 作用
                      │
                      ▼
                Candidate Trigger    # 中文：候选触发
                    候选触发
                      │
                      ▼
                 Context Check    # 中文：上下文检查
                   上下文检查
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
      Necessity    Exception   External Lookup    # 中文：必要性例外外部查询
      必要性分析      例外检查       政策状态查询
          │           │           │
          └───────────┼───────────┘
                      ▼
                Evidence Gate    # 中文：证据充分性门槛
                   证据门
                      │
             ┌────────┴────────┐
             ▼                 ▼
        Evidence Enough     Uncertain    # 中文：证据充分 / 证据或判断仍不确定
          证据充分             不确定
             │                 │
             ▼                 ▼
       Supported Finding   Human Review    # 中文：支持发现项人工复核
          支持发现项          人工复核
             │                 │
             └────────┬────────┘
                      ▼
               Remediation    # 中文：修改 / 整改建议
                 修改建议
                      │
                      ▼
               Audit + Benchmark    # 中文：审计记录 + Benchmark 评测
                审计 + 评测
```

脑中最后只留一句：

> **附件 9 的 22 项不是给模型背诵的 22 句话，而是 22 个来源可追踪、条件可执行、例外可检查、证据可定位、结果可复核、版本可治理的 Compliance Rule Objects；真正的系统流程是“结构化采购事实 → 候选规则 → 上下文 / 必要性 / 例外 → 证据门 → Finding 或人工复核”，而不是“关键词出现 → 违规”。**

---

# 第十一课 · 第 4 阶段掌握测试

现在不回看正文，你应该能够解释：

```text
附件9中的7类问题和22项具体表现形式是什么关系？

为什么D01-D22不能做成22个关键词？

D01-D22中哪些更偏结构规则、哪些更依赖例外、哪些依赖外部政策状态、哪些依赖项目必要性？

为什么Trigger只能产生Candidate？

为什么D04、D16、D20必须把Exception做成一级字段？

为什么D13不能离开Project Context判断？

为什么D14和D22必须依赖Policy Registry？

为什么D11即使没有品牌名，也仍然可能存在特定产品指向？

为什么RuleSet不能只写进一个超长System Prompt？

为什么Rule Object必须保存Source Provenance？

为什么Inspection Rule与Legal Basis必须分层？

为什么Missing Context应该允许Abstention？

为什么Hard Negative比明显负例更重要？

Counterfactual Pair如何帮助学习Decision Boundary？

为什么Implemented不等于Validated？

为什么D01-D22必须逐规则做Benchmark Slice？

为什么Automation Rate不是合规系统的最终目标？

为什么修改建议必须Preserve Need，而不是简单删除要求？
```

如果这些能够完整解释：

\[
\boxed{
第十一课第4阶段真正掌握
}
\]

---

# 下一阶段：第十一课 · 第 5 阶段
# 资格条件与市场准入合规：地域、行业、所有制、规模、年限、财务、资质、业绩
## 怎样区分真正的履约能力要求与不合理市场准入门槛？

下一阶段将把 D01～D10、D15～D22 中大量与资格和市场准入有关的规则进一步展开到：

```text
Qualification Gate    # 中文：资格准入门

Market Access    # 中文：市场准入

Supplier Eligibility    # 中文：供应商准入资格

Experience    # 中文：业绩

Financial Condition    # 中文：财务条件

Enterprise Form    # 中文：企业表单

Local Presence    # 中文：本地设点 / 本地存在性要求

Certificate    # 中文：证书

Pre-bid Requirement    # 中文：前投标要求
```

并建立：

# `ProcurementQualificationCompliance_V1`

下一阶段最重要的边界：

\[
\boxed{
CapabilityRequirement
\neq
MarketAccessBarrier
}
\]

**中文业务释义：** 履约能力要求 ≠ 市场准入障碍。
