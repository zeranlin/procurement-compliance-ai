# 第十一课 · 第 6 阶段
# 技术参数合规：品牌、专利、技术路线、检测报告、认证、授权、样品
## 怎样识别“看起来只是技术要求，实际上已经把竞争范围锁定到特定供应商或特定产品”的显性与隐性限制？

第 5 阶段我们已经建立：

\[
\boxed{
CapabilityRequirement
\neq
MarketAccessBarrier
}
\]

**中文业务释义：** 履约能力要求 ≠ 市场准入障碍。

并且把资格条件拆成：

\[
\boxed{
Objective
\rightarrow
Relevance
\rightarrow
Necessity
\rightarrow
Proportionality
\rightarrow
Alternative
}
\]

**中文业务释义：** 目标 → 相关性 → 必要性 → 比例性 → 替代方案。

现在进入政府采购合规检查中另一个非常容易出现隐性限制的区域：

# Technical Requirement
## 技术要求 / 技术参数

技术参数最危险的地方，不是：

> “写得专业”。

而是：

> **采购文件可能没有直接写“只能买某品牌”，但参数组合、专利、接口、组件、证明材料、厂家授权、指定检测机构等条件叠加以后，实际竞争范围已经被压缩到极少数甚至特定供应商、特定产品。**

因此本阶段第一条核心边界正式锁定为：

\[
\boxed{
TechnicalSpecificity
\neq
TechnicalDiscrimination
}
\]

**中文业务释义：** 技术参数具体性 ≠ 技术歧视 / 不合理技术排斥。

技术要求当然可以具体。

真正需要审查的是：

> **这种具体性是否服务于真实采购目标，是否采用了必要且最小充分的约束，是否存在不合理的特定供应商 / 特定产品指向，是否给其他能够实现同一功能目标的竞争方案留下公平进入空间。**

本阶段最终形成：

# `ProcurementTechnicalCompliance_V1`

---

# 一、本阶段与附件 9 哪些规则直接连接？

根据《2025年政府采购领域“四类”违法违规行为专项整治工作指引》及附件 9，本阶段重点连接：

```text
D11    # 中文：技术、服务需求指向特定供应商、特定产品

D12    # 中文：限定或指定特定供应商、专利、商标、品牌、原产地、零部件等

D13    # 中文：资格证书、技术参数、商务条件等与项目具体特点、实际需要不相适应，或与合同履行无关

D15    # 中文：将特定信用证书、协会 / 组织证书、奖项等作为资格条件或评审因素

D16    # 中文：除采购进口货物外，设置厂家授权、承诺、证明、背书等不合理限制

D20    # 中文：除特别规定外，无正当理由限制技术证明材料的出具机构
```

专项整治工作指引正文还特别提示关注：

```text
“知名”    # 中文：以“知名”作为品牌或产品范围限定的风险表达

“一线”    # 中文：以“一线品牌”等模糊等级词限制竞争的风险表达

“参考品牌”    # 中文：表面写“参考”，但仍需检查是否形成事实上的品牌指向
```

所以：

\[
\boxed{
TechnicalCompliance
\neq
BrandKeywordDetection
}
\]

**中文业务释义：** 技术参数合规 ≠ 品牌关键词检测。

---

# 二、先定义“技术要求”到底是什么

一个技术要求，不应该只是：

```text
parameter_name    # 中文：技术参数名称

parameter_value    # 中文：技术参数数值
```

更完整的业务结构应当是：

\[
\boxed{
TechnicalRequirement
=
FunctionalGoal
+
PerformanceIndicator
+
Constraint
+
VerificationMethod
+
BusinessFunction
}
\]

**中文业务释义：** 技术要求 = 功能目标 + 性能指标 + 约束条件 + 验证方式 + 业务功能 / 条款作用。

中文分别是：

```text
FunctionalGoal    # 中文：采购人真正要实现的功能目标

PerformanceIndicator    # 中文：能够量化或验证的性能指标

Constraint    # 中文：为实现功能目标设置的技术约束

VerificationMethod    # 中文：如何证明供应商 / 产品满足该要求

BusinessFunction    # 中文：该技术要求在采购文件里到底是准入门槛、实质性条款、评分因素还是履约义务
```

这套结构非常重要。

因为：

> 如果只看到参数，不知道它想解决什么业务目标，就很难判断参数是否必要。

---

# 三、核心心智模型 ①
# `TechnicalRequirement` 必须能回到 `FunctionalGoal`

例如：

```text
要求A    # 中文：某个具体接口、尺寸、协议或组件要求
```

系统不能只问：

> “这个参数常不常见？”

而要继续问：

```text
functional_goal    # 中文：这个参数要实现什么功能？

failure_risk    # 中文：如果不满足，真实履约风险是什么？

contract_link    # 中文：它是否与最终合同履约目标存在直接联系？
```

因此：

\[
\boxed{
ParameterWithoutGoal
=
NecessityWarningSignal
}
\]

**中文业务释义：** 缺少功能目标解释的参数 = 必要性预警信号。

这里表示：

> **技术参数无法解释其功能目标时，应提高必要性复核优先级，但不是自动认定违规。**

---

# 四、D11：没有品牌名，也可能存在“实质指向”

D11 关注：

> 技术、服务需求是否指向特定供应商、特定产品。

最容易犯的错误是：

\[
\boxed{
NoBrandName
\neq
NoProductDirection
}
\]

**中文业务释义：** 未出现品牌名 ≠ 不存在产品指向。

例如采购文件没有写：

```text
必须采用某品牌    # 中文：显式品牌指定
```

但同时要求：

```text
尺寸A必须等于某值    # 中文：尺寸条件

接口B必须采用某专有形式    # 中文：接口条件

协议C必须支持某私有协议    # 中文：协议条件

组件D必须与某型号完全兼容    # 中文：组件兼容条件

特定功能E必须按某实现方式完成    # 中文：实现路径条件
```

单独看每一项：

> 可能都“像技术参数”。

组合起来以后：

> 可能形成某一产品的“参数指纹”。

---

# 五、Parameter Fingerprint
## 参数指纹

# Parameter Fingerprint
中文：**参数指纹**

指的是：

> **多项参数组合在一起以后，形成高度独特的产品特征集合。**

可以抽象成：

\[
\boxed{
ParameterFingerprint
=
P_1
\land
P_2
\land
P_3
\land
...
\land
P_n
}
\]

**中文业务释义：** 参数指纹 = P_1 且 P_2 且 P_3 且 ... 且 P_n。

其中每个 \(P_i\) 都是一个技术约束。

例如：

```text
parameter_01    # 中文：第一项技术约束

parameter_02    # 中文：第二项技术约束

parameter_03    # 中文：第三项技术约束

parameter_combination    # 中文：多项参数联合后的产品筛选条件
```

所以：

\[
\boxed{
SingleParameterReasonable
\neq
ParameterCombinationNeutral
}
\]

**中文业务释义：** 单项参数合理 ≠ 参数组合保持竞争中立。

---

# 六、核心心智模型 ②
# 技术合规必须看“组合效果”，不能只逐条看

如果 20 项技术参数：

> 每一项单独都能解释，

但只有一家产品：

> 能同时满足全部参数，

那么系统必须继续调查：

```text
是否确有业务必要性？    # 中文：参数组合是否确实来自项目实际需要

是否存在等效方案？    # 中文：其他技术路线能否实现相同功能目标

是否存在市场证据？    # 中文：满足条件的竞争产品 / 供应商范围是否有可验证依据

是否存在参数冗余？    # 中文：某些参数是否不是实现采购目标所必需
```

所以：

\[
\boxed{
ClauseByClauseReview
\neq
CombinationReview
}
\]

**中文业务释义：** 逐条款审查 ≠ 参数组合审查。

---

# 七、D12：品牌、专利、商标、原产地、零部件等显性限定

D12 相对更容易产生显性候选触发。

至少要抽：

```text
supplier_reference    # 中文：是否直接出现特定供应商名称

patent_reference    # 中文：是否限定或指定特定专利

trademark_reference    # 中文：是否限定或指定特定商标

brand_reference    # 中文：是否限定或指定特定品牌

origin_reference    # 中文：是否限定产品原产地

component_reference    # 中文：是否限定特定零部件、组件或型号

model_reference    # 中文：是否直接或变相出现特定型号

equivalent_mechanism    # 中文：是否存在真正可执行的等效产品 / 等效技术路线机制
```

但这里仍然必须坚持：

\[
\boxed{
ReferenceDetected
\rightarrow
Candidate
}
\]

**中文业务释义：** 检测到显性引用 → 候选。

而不是：

\[
\boxed{
ReferenceDetected
\rightarrow
AutomaticViolation
}
\]

**中文业务释义：** 检测到显性引用 → 自动违规认定。

因为仍然需要：

```text
Applicable Policy    # 中文：适用法律政策

Project Necessity    # 中文：项目实际必要性

Exception    # 中文：合法例外

Evidence    # 中文：采购文件和市场事实证据
```

共同判断。

---

# 八、“知名”“一线”“参考品牌”为什么危险？

这些表达的问题是：

> 它们看起来没有直接写死某一个品牌，却可能把竞争空间限定到一个模糊但很窄的品牌圈层。

系统至少应抽：

```text
brand_tier_term    # 中文：是否出现“知名”“一线”等品牌层级词

reference_brand_list    # 中文：是否列出参考品牌清单

brand_count    # 中文：参考品牌数量

equivalent_allowed    # 中文：是否允许等效品牌 / 产品

equivalent_standard    # 中文：等效的判断标准是否明确

brand_role    # 中文：品牌在这里是示例、评分条件、实质性条件还是准入条件
```

---

# 九、核心心智模型 ③
# 写了“或相当于”不代表天然中立

例如：

```text
某品牌或相当于    # 中文：表面允许等效产品
```

但如果后面又有：

```text
专有接口    # 中文：只有少数产品支持的接口要求

专有组件    # 中文：只有特定产品生态可满足的组件要求

独特尺寸    # 中文：高度接近特定型号的尺寸要求
```

那么：

> “或相当于”可能只是文字层面的开放。

所以：

\[
\boxed{
EquivalentWording
\neq
EffectiveEquivalence
}
\]

**中文业务释义：** “或相当于”等等效表述 ≠ 真正可执行的等效机制。

真正要看：

# Equivalent Path
## 等效进入路径

是否真的可执行。

---

# 十、Equivalent Mechanism
## 等效机制

一个专业的等效机制至少要回答：

```text
equivalent_goal    # 中文：等效产品必须实现的相同业务目标

equivalent_metrics    # 中文：用哪些功能 / 性能指标判断“等效”

equivalent_evidence    # 中文：供应商用什么材料证明等效

equivalent_review_method    # 中文：评审委员会如何验证等效

equivalent_acceptance    # 中文：合同验收阶段如何确认等效性能
```

因此：

\[
\boxed{
Equivalent
必须可验证
}
\]

而不能只是：

> 一个模糊词。

---

# 十一、Function vs Implementation
## 功能目标与实现路径

采购人真正需要的通常是：

# Functional Goal    # 中文：采购人真正要实现的功能目标
中文：**功能目标**

例如：

```text
高并发处理能力    # 中文：系统在高并发下仍能稳定完成业务

数据兼容    # 中文：能够与现有数据交换

安全隔离    # 中文：满足所需安全边界

低时延    # 中文：满足业务响应时间目标
```

而不是天然需要某一个：

# Implementation Path
中文：**实现路径 / 技术路线**

例如：

```text
必须采用某专有协议    # 中文：指定实现方式

必须采用某独占架构    # 中文：限定技术架构

必须采用某品牌生态组件    # 中文：限定产品生态
```

所以：

\[
\boxed{
FunctionalGoal
\neq
SpecificImplementationPath
}
\]

**中文业务释义：** 功能目标 ≠ 特定技术实现路径。

---

# 十二、核心心智模型 ④
# 优先表达“要实现什么”，谨慎限定“必须怎么实现”

这不意味着：

> 政府采购文件永远不能规定技术路线。

而是：

> **如果要限定技术路线，必须能解释为什么其他实现路径不能满足真实项目需求。**

所以：

\[
\boxed{
SpecificImplementation
\Rightarrow
StrongerNecessityEvidence
}
\]

**中文业务释义：** 限定具体实现方式 ⇒ 更强的必要性证据。

---

# 十三、Minimal Sufficient Constraint
## 最小充分约束

本阶段引入一个非常重要的工程概念：

# Minimal Sufficient Constraint
中文：**最小充分约束**

意思是：

> **只设置实现采购目标所需要的最少且足够的技术限制。**

可以理解为：

\[
\boxed{
GoodTechnicalConstraint
=
EnoughForNeed
+
NoUnnecessaryLockIn
}
\]

**中文业务释义：** 良好技术约束 = 足以满足采购需求 + 不存在不必要技术锁定。

不是：

> 参数越少越好。

也不是：

> 参数越详细越专业。

而是：

> **参数应当“够用”，但不应额外把竞争空间锁死。**

---

# 十四、核心心智模型 ⑤
# `MoreParameters` 不等于 `BetterRequirement`

参数越多：

```text
可能更清楚    # 中文：提高技术描述精度

也可能更锁定    # 中文：叠加后收窄可竞争产品范围
```

因此：

\[
\boxed{
ParameterCount
\neq
RequirementQuality
}
\]

**中文业务释义：** 参数数量 ≠ 需求质量。

真正关注：

\[
\boxed{
NecessityPerConstraint
}
\]

**中文业务释义：** 逐项约束必要性。

中文：

> **每一个约束是否都有项目必要性。**

---

# 十五、Compatibility Requirement
## 兼容性要求

真实政府采购项目经常存在：

```text
现有硬件    # 中文：已有设备

现有软件    # 中文：已有业务系统

现有协议    # 中文：已经投入使用的通信 / 数据协议

现有数据    # 中文：历史数据与现有数据模型

现有运维体系    # 中文：已有维护和保障环境
```

因此：

> 某些兼容性要求可能具有真实业务必要性。

所以：

\[
\boxed{
CompatibilityNeed
\neq
BrandLockIn
}
\]

**中文业务释义：** 兼容性需求 ≠ 品牌锁定。

但系统要继续判断：

```text
existing_system_evidence    # 中文：现有系统确实存在的证据

compatibility_objective    # 中文：为什么必须兼容

open_standard_available    # 中文：是否存在开放标准或中立接口

migration_alternative    # 中文：是否存在合理迁移 / 适配方案

lock_in_effect    # 中文：兼容要求会把供应商范围收窄到什么程度
```

---

# 十六、核心心智模型 ⑥
# “现有系统兼容”不是万能理由

如果采购文件只写：

> “为保证兼容性，必须使用某品牌。”

但没有：

```text
现有系统事实    # 中文：现有环境的具体技术事实

接口约束    # 中文：无法替代的兼容条件

迁移成本证据    # 中文：切换方案真实成本

安全 / 稳定性证据    # 中文：为什么替代方案无法满足
```

则系统应进入：

```text
NECESSITY_REVIEW_REQUIRED    # 中文：需要进一步开展必要性复核
```

而不是自动接受。

---

# 十七、Market Satisfiability    # 中文：真实市场可满足性证据
## 市场可满足性

技术条款是否形成产品指向，

最终往往需要知道：

> **市场上到底有多少独立产品 / 供应商能够满足。**

这就是：

# Market Satisfiability    # 中文：真实市场可满足性证据
中文：**市场可满足性**

建议抽：

```text
market_evidence_id    # 中文：市场调研证据标识

evidence_date    # 中文：市场证据采集日期

candidate_products    # 中文：候选可满足产品列表

candidate_suppliers    # 中文：候选可满足供应商列表

independent_brands    # 中文：独立品牌数量

requirements_checked    # 中文：本次市场调研实际核验了哪些技术要求

satisfied_count    # 中文：同时满足关键参数组合的产品数量

uncertain_count    # 中文：证据不足、无法确认的候选数量

source_refs    # 中文：产品资料、官方参数、调研材料等来源引用
```

---

# 十八、核心心智模型 ⑦
# LLM 不能凭“感觉”宣布市场上只有一家

因此：

\[
\boxed{
ModelBelief
\neq
MarketEvidence
}
\]

**中文业务释义：** 模型主观判断 ≠ 市场证据。

如果没有：

```text
产品参数资料    # 中文：产品官方或可核验技术资料

市场调研记录    # 中文：采购需求调查 / 市场调查资料

供应商响应事实    # 中文：真实供应商响应或澄清情况

可靠外部来源    # 中文：可复核的市场证据
```

系统只能输出：

```text
MARKET_EVIDENCE_INSUFFICIENT    # 中文：市场可满足性证据不足
```

而不能：

> 强行说“只有某品牌能满足”。

---

# 十九、只有一家能满足，就一定违规吗？

也不是。

\[
\boxed{
SingleFeasibleProduct
\neq
AutomaticViolation
}
\]

**中文业务释义：** 仅有一个可行产品 ≠ 自动违规认定。

它可能意味着：

```text
需求确实高度特殊    # 中文：项目目标具有真实特殊性

存在不可替代兼容约束    # 中文：现有系统造成真实兼容边界

法律政策存在特殊要求    # 中文：适用规则要求特定技术条件

也可能是参数被人为锁定    # 中文：不必要技术组合造成竞争收窄
```

所以还要回到：

\[
\boxed{
Necessity
+
Proportionality
+
Alternative
+
Evidence
}
\]

**中文业务释义：** 必要性 + 比例性 + 替代方案 + 证据。

---

# 二十、D13：技术参数与项目实际需要是否匹配

D13 是本阶段最核心的强上下文规则之一。

它不能靠：

```text
关键词    # 中文：单个敏感词
```

判断。

而要建立：

# Technical Necessity Test    # 中文：技术必要性检验，包括相关性、最小充分性、替代方案和可验证性
## 技术必要性检验

至少回答六个问题。

---

# 二十一、Technical Necessity Test    # 中文：技术必要性检验，包括相关性、最小充分性、替代方案和可验证性 六问

## 1. Goal
### 功能目标

```text
technical_goal    # 中文：该技术要求解决什么业务目标
```

---

## 2. Relevance
### 相关性

```text
need_relation    # 中文：该参数与采购项目特点、实际需要有什么直接联系
```

---

## 3. Minimum Sufficiency
### 最小充分性

```text
minimum_sufficient    # 中文：是否可以用更少、更宽松但仍足够的技术约束实现目标
```

---

## 4. Verifiability
### 可验证性

```text
verification_method    # 中文：如何客观证明该要求已满足
```

---

## 5. Alternative
### 替代方案

```text
technical_alternatives    # 中文：是否存在其他技术路线能够实现相同目标
```

---

## 6. Competition Impact    # 中文：技术要求对供应商和产品竞争范围的影响
### 竞争影响

```text
competition_impact    # 中文：该要求会把潜在供应商 / 产品范围收窄到什么程度
```

最终形成：

\[
\boxed{
TechnicalNecessity
=
Goal
+
Relevance
+
MinimumSufficiency
+
Verifiability
+
Alternative
+
CompetitionImpact
}
\]

**中文业务释义：** 技术必要性 = 目标 + 相关性 + 最小Sufficiency + Verifiability + 替代方案 + Competition影响。

这是工程审查模型，

不是法律公式。

---

# 二十二、核心心智模型 ⑧
# “与项目有关”仍然不代表“参数可以无限精细”

这和 Stage 5 完全一致：

\[
\boxed{
Relevant
\neq
UnlimitedConstraint
}
\]

**中文业务释义：** 与项目相关 ≠ 无限制细化 / 收紧参数。

例如：

> 精度确实重要。

不代表：

> 精度必须恰好限定到某一产品独有值。

因此：

\[
\boxed{
Need
\rightarrow
MinimumSufficientRequirement
}
\]

**中文业务释义：** Need → 最小充分要求。

比：

\[
\boxed{
Need
\rightarrow
MaximumPossibleSpecification
}
\]

**中文业务释义：** Need → MaximumPossibleSpecification。

更符合合规工程逻辑。

---

# 二十三、Mandatory / Substantive / Scoring
## 必须满足、实质性条款、评分因素

同一个技术参数，

可能是：

```text
MANDATORY_REQUIREMENT    # 中文：必须满足的技术要求

SUBSTANTIVE_REQUIREMENT    # 中文：不满足可能导致响应无效 / 否决的实质性要求

SCORING_FACTOR    # 中文：满足程度影响评分的技术因素

PERFORMANCE_OBLIGATION    # 中文：中标后合同履约阶段需要满足的技术义务
```

因此：

\[
\boxed{
SameTechnicalParameter
+
DifferentBusinessFunction
=
DifferentCompetitionImpact
}
\]

**中文业务释义：** 相同技术参数 + 不同业务功能 = 不同Competition影响。

---

# 二十四、核心心智模型 ⑨
# 技术参数“放在哪里、起什么作用”与参数本身同样重要

例如一个非常严格的技术要求：

> 如果作为高分评分项，

和：

> 作为不满足即废标的实质性条件，

竞争影响完全不同。

所以 Stage 3 的：

\[
\boxed{
WhereItAppears
\neq
WhatItDoes
}
\]

**中文业务释义：** WhereItAppears ≠ WhatItDoes。

在这里再次成为核心。

---

# 二十五、检测报告、认证、证明材料不能混成一类

本阶段需要把：

```text
test_report    # 中文：检测 / 检验报告

certification    # 中文：认证证书

license    # 中文：许可 / 资质

manufacturer_proof    # 中文：生产厂家出具的证明

third_party_proof    # 中文：第三方机构出具的证明

self_declaration    # 中文：供应商自我声明 / 承诺
```

分开。

因为不同证明材料的：

```text
法律属性    # 中文：是否属于法定要求

证明对象    # 中文：到底证明参数、质量、资质还是能力

出具主体    # 中文：谁出具

有效期    # 中文：什么时候有效

适用范围    # 中文：对哪些产品 / 型号 / 项目有效
```

不同。

---

# 二十六、D15：证书 / 奖项的技术审查连接

D15 在技术章节中可能表现为：

```text
必须获得某协会技术奖    # 中文：将行业组织奖项作为门槛或评分

必须取得某商业信用认证    # 中文：将非必要信用认证嵌入技术 / 评分要求

必须取得某非强制技术证书    # 中文：将并非法定必需的技术证书设为强条件
```

系统至少要识别：

```text
certificate_type    # 中文：证书类型

issuer_type    # 中文：颁发机构类型

legal_status    # 中文：法律 / 政策状态

mandatory_status    # 中文：是否属于法定或强制要求

project_relation    # 中文：与采购项目技术目标的关联性

business_function    # 中文：它是门槛、实质性要求还是评分因素
```

---

# 二十七、核心心智模型 ⑩
# `ProofNeeded` 不等于 `SpecificCertificateNeeded`

采购人可能确实需要证明：

> 某个产品满足某项性能。

但这不自动推出：

> 必须使用某一个特定证书名称。

所以：

\[
\boxed{
ProofObjective
\neq
SpecificProofForm
}
\]

**中文业务释义：** 证明目标 ≠ 特定证明形式。

需要进一步问：

> 有没有其他能够同等证明技术能力 / 性能的材料？

---

# 二十八、D20：技术证明材料出具机构限制

D20 的核心不是：

> “有没有检测机构”。

而是：

> **是否无正当理由把技术证明材料限定为某一家、某一类、某一地区或某一特定范围机构出具。**

因此要抽：

```text
proof_type    # 中文：要求提供什么技术证明材料

issuer_required    # 中文：是否指定出具机构

issuer_name    # 中文：指定机构名称

issuer_type    # 中文：指定机构类型

issuer_region    # 中文：是否限定机构地域

exclusive_issuer    # 中文：是否只有指定机构出具才被认可

special_provision    # 中文：是否存在特别规定

justification    # 中文：限制出具机构的正当理由 / 依据
```

---

# 二十九、核心心智模型 ⑪
# `ProofContent` 与 `ProofIssuer` 必须分开

真正采购目标通常是：

> 证明某项技术事实。

所以：

\[
\boxed{
NeedProof
\neq
NeedSpecificIssuer
}
\]

**中文业务释义：** 需要证明技术事实 ≠ 需要特定出具机构。

如果有特别规定：

> 则走 Exception / Policy Registry。

如果没有：

> 应进一步审查为什么限定出具主体。

---

# 三十、D16：厂家授权、承诺、证明、背书

技术采购中经常出现：

```text
manufacturer_authorization    # 中文：原厂授权

manufacturer_commitment    # 中文：原厂承诺

manufacturer_certificate    # 中文：原厂证明

manufacturer_endorsement    # 中文：原厂背书
```

它们常被解释为：

```text
保证正品    # 中文：真实性目标

保证售后    # 中文：售后保障目标

保证兼容    # 中文：兼容性目标

保证供货    # 中文：供货能力目标
```

但附件 9 对此有明确的专项检查逻辑，并存在：

```text
imported_goods_exception    # 中文：采购进口货物的例外条件
```

因此：

\[
\boxed{
ManufacturerProof
\rightarrow
Trigger
+
ImportExceptionCheck
+
NecessityCheck
}
\]

**中文业务释义：** 厂家证明 → 触发条件 + 进口例外Check + 必要性Check。

---

# 三十一、核心心智模型 ⑫
# “想证明正品 / 售后”不等于必须要求“原厂授权”

系统应追问：

```text
business_objective    # 中文：采购人真正想保障什么

alternative_evidence    # 中文：是否存在其他真实性 / 售后 / 供货证明方式

pre_bid_gate    # 中文：是否被设置成投标前准入 / 实质性门槛

competition_impact    # 中文：会排除多少经销商 / 供应商
```

因此：

\[
\boxed{
BusinessGoal
\neq
SingleEvidenceForm
}
\]

**中文业务释义：** 业务目标 ≠ 单一证据Form。

---

# 三十二、样品要求怎么处理？

这里必须特别区分“来源规则”和“工程扩展”。

# Sample Requirement
## 样品要求

**样品并不是附件 9 单独列出的一个 Dxx 表现形式。**

所以本课程不会把：

```text
“要求样品”
```

虚构成：

```text
D23    # 中文：不存在的附件9新增规则
```

正确做法是：

> 将样品要求作为技术审查的工程扩展对象，再根据其具体作用连接 D13、其他适用规则和 Policy Registry。

这是非常重要的来源纪律：

\[
\boxed{
EngineeringExtension
\neq
SourceRule
}
\]

**中文业务释义：** 工程扩展审查对象 ≠ 来源文件中的正式规则。

---

# 三十三、Sample Requirement
## 样品要求的工程审查字段

可以抽：

```text
sample_required    # 中文：是否要求提交样品

sample_stage    # 中文：样品在什么阶段提交

sample_quantity    # 中文：样品数量

sample_cost    # 中文：样品制作 / 提交成本

sample_return_policy    # 中文：是否退还及退还规则

sample_damage_policy    # 中文：损坏 / 消耗规则

sample_evaluation_method    # 中文：样品如何评审

sample_score_role    # 中文：样品是符合性门槛还是评分因素

sample_necessity    # 中文：为什么必须通过实物样品验证

alternative_verification    # 中文：是否可通过检测报告、演示、照片、视频、现场测试等替代
```

真正要问：

> **样品是否确实是验证采购目标的必要手段。**

---

# 三十四、检测方法本身也可能影响竞争

即使技术参数本身中立，

如果要求：

```text
只能按某独家方法检测    # 中文：验证路径被限定

必须在某特定机构检测    # 中文：检测出具主体被限定

必须在投标前完成高成本检测    # 中文：验证时点和成本形成门槛
```

也可能产生竞争影响。

所以：

\[
\boxed{
NeutralRequirement
+
RestrictiveVerification
=
PotentialBarrier
}
\]

**中文业务释义：** 中立要求 + 限制性验证 = Potential障碍。

---

# 三十五、标准、规范、版本号

技术参数经常引用：

```text
national_standard    # 中文：国家标准

industry_standard    # 中文：行业标准

local_standard    # 中文：地方标准

group_standard    # 中文：团体标准

enterprise_standard    # 中文：企业标准

international_standard    # 中文：国际标准
```

系统必须保存：

```text
standard_number    # 中文：标准编号

standard_name    # 中文：标准名称

standard_version    # 中文：标准版本

effective_status    # 中文：当前 / 项目时点是否有效

mandatory_status    # 中文：是否强制性

scope    # 中文：标准适用范围
```

---

# 三十六、核心心智模型 ⑬
# `StandardMentioned` 不代表 `StandardApplicable`

这和 Stage 2 的：

\[
\boxed{
LatestPolicy
\neq
ApplicablePolicy
}
\]

**中文业务释义：** 最新发布 / 当前最新政策 ≠ 适用政策 / 适用法规。

是同一种工程思想。

技术标准也需要：

```text
版本    # 中文：使用的是哪个版本

状态    # 中文：是否有效 / 被替代

适用范围    # 中文：是否适用于当前产品 / 项目

强制性    # 中文：是不是必须遵守
```

---

# 三十七、参数范围、精度和容差

例如：

```text
parameter_min    # 中文：参数下限

parameter_max    # 中文：参数上限

exact_value    # 中文：是否要求精确等于某值

tolerance    # 中文：允许误差 / 容差范围

unit    # 中文：计量单位
```

“精确等于”往往比：

```text
>=    # 中文：不低于

<=    # 中文：不高于

range    # 中文：合理区间
```

更容易形成产品指纹。

但：

\[
\boxed{
ExactValue
\neq
AutomaticRisk
}
\]

**中文业务释义：** ExactValue ≠ 自动风险。

仍然要看：

> 该精确值是否存在真实功能必要性。

---

# 三十八、核心心智模型 ⑭
# 技术参数合规不是“全部改成越大越好 / 越小越好”

例如：

```text
至少越高越好    # 中文：并非所有性能指标都适合无限提高

最多越低越好    # 中文：并非所有限制指标都适合无限降低
```

真正专业的采购需求应该：

> **定义与业务目标相匹配的性能边界。**

因此：

\[
\boxed{
PerformanceRequirement
\neq
ExtremeSpecification
}
\]

**中文业务释义：** 性能要求 ≠ 极端规格。

---

# 三十九、专有协议、私有接口、生态锁定

技术文件可能通过：

```text
proprietary_protocol    # 中文：专有协议

private_interface    # 中文：私有接口

exclusive_component    # 中文：生态内专属组件

closed_format    # 中文：封闭数据格式

vendor_specific_api    # 中文：特定厂商 API
```

形成：

# Ecosystem Lock-in
## 技术生态锁定

但再次强调：

> 生态锁定的存在，不自动等于违法。

需要：

```text
现有系统事实    # 中文：已有生态是否真实存在

迁移可行性    # 中文：是否可以合理迁移

数据 / 安全风险    # 中文：切换技术路线是否带来重大风险

替代接口    # 中文：是否存在开放或中立替代方案

成本证据    # 中文：迁移或替代成本是否有客观依据
```

---

# 四十、Cross-clause Lock-in
## 跨条款组合锁定

非常隐蔽的一类风险是：

> 每个参数分散在不同章节，看起来都普通，但组合后形成唯一产品指向。

例如：

```text
Clause A    # 中文：技术参数章节中的尺寸要求

Clause B    # 中文：商务章节中的配套耗材要求

Clause C    # 中文：实质性条款中的兼容接口要求

Clause D    # 中文：评分表中的某品牌生态加分
```

单独看：

> 风险不明显。

合起来：

> 可能形成完整产品指纹。

所以：

\[
\boxed{
LocalClauseReview
\neq
CrossClauseTechnicalReview
}
\]

**中文业务释义：** 局部条款审查 ≠ 跨条款技术审查。

---

# 四十一、核心心智模型 ⑮
# 技术指向可能是“分布式”的

因此 Technical Engine 需要：

```text
canonical_technical_requirement_id    # 中文：跨章节归一化后的技术要求标识

related_clause_ids    # 中文：相关条款列表

parameter_bundle_id    # 中文：技术参数组合标识

cross_section_effect    # 中文：跨章节组合后的实际竞争影响
```

这也是为什么 Stage 3 的 CrossReference 很重要。

---

# 四十二、Table / Attachment
## 表格与附件

技术参数经常全部在：

```text
parameter_table    # 中文：技术参数表

configuration_list    # 中文：配置清单

bill_of_materials    # 中文：设备 / 零部件清单

technical_attachment    # 中文：技术附件

drawing    # 中文：图纸

footnote    # 中文：脚注
```

中。

所以：

> 正文里没有品牌、专利，不代表附件里没有。

因此：

\[
\boxed{
MainTextReview
\neq
WholeTechnicalReview
}
\]

**中文业务释义：** 只审正文 ≠ 完整技术审查。

---

# 四十三、Technical Candidate Rule Mapping
## 技术要求到 D01-D22 的候选规则映射

Stage 3 的 Document Schema 先输出：

```text
candidate_rule_ids    # 中文：根据结构事实初步召回的候选规则标识
```

Stage 6 在技术域进一步形成：

```text
D11_candidate    # 中文：可能存在特定供应商 / 产品指向

D12_candidate    # 中文：可能限定专利 / 商标 / 品牌 / 原产地 / 零部件

D13_candidate    # 中文：参数可能与项目实际需要不相适应或与合同履行无关

D15_candidate    # 中文：可能存在不适当证书 / 奖项要求

D16_candidate    # 中文：可能存在厂家授权 / 承诺 / 证明 / 背书限制

D20_candidate    # 中文：可能无正当理由限制技术证明材料出具机构
```

仍然坚持：

\[
\boxed{
Candidate
\neq
Finding
}
\]

**中文业务释义：** 候选 ≠ 合规发现项。

---

# 四十四、Technical Finding
## 技术合规发现项

一个完整技术 Finding 至少需要：

```text
finding_id    # 中文：技术合规发现项标识

review_domain    # 中文：审查域，这里固定为 TECHNICAL 技术要求

document_id    # 中文：采购文件标识

document_version    # 中文：采购文件版本

section_id    # 中文：章节标识

clause_id    # 中文：条款标识

requirement_id    # 中文：结构化技术要求标识

parameter_bundle_id    # 中文：相关参数组合标识

business_function    # 中文：准入 / 实质性 / 评分 / 履约等业务作用

functional_goal    # 中文：采购人真实功能目标

technical_constraints    # 中文：形成当前要求的技术约束集合

explicit_references    # 中文：品牌、专利、商标、原产地、组件等显性引用

combination_fingerprint    # 中文：参数组合是否形成明显产品指纹

market_evidence_id    # 中文：市场可满足性证据标识

equivalent_mechanism    # 中文：是否存在有效等效进入机制

necessity_analysis    # 中文：技术必要性分析

alternative_analysis    # 中文：替代技术路线分析

competition_impact    # 中文：对供应商 / 产品竞争范围的影响

proof_requirements    # 中文：检测报告、认证、证明等要求

issuer_restriction    # 中文：对证明材料出具机构的限制

manufacturer_requirement    # 中文：厂家授权 / 承诺 / 证明 / 背书要求

exception_status    # 中文：例外状态

candidate_rule_ids    # 中文：候选 Dxx 规则

confirmed_rule_ids    # 中文：证据充分后支持的规则标识

legal_basis_refs    # 中文：适用法律 / 政策依据引用

policy_snapshot_id    # 中文：项目时点法规快照标识

evidence_span    # 中文：采购文件原文证据及定位

risk_level    # 中文：产品风险等级，不等于行政处罚定性

confidence    # 中文：系统对当前判断的置信程度

human_review_required    # 中文：是否必须进入人工复核

recommended_revision    # 中文：建议如何保留采购目标并去除不必要技术锁定
```

---

# 四十五、技术合规判断主流程

\[
\boxed{
TechnicalClause
\rightarrow
RequirementParse
\rightarrow
BusinessFunction
\rightarrow
ExplicitReferenceCheck
\rightarrow
ParameterBundle
\rightarrow
FunctionalGoal
\rightarrow
Necessity
\rightarrow
EquivalentPath
\rightarrow
MarketEvidence
\rightarrow
ProofIssuerCheck
\rightarrow
ManufacturerException
\rightarrow
CompetitionImpact
\rightarrow
EvidenceGate
\rightarrow
Finding/HumanReview
}
\]

**中文业务释义：** 技术条款 → 要求解析 → 业务功能 / 条款作用 → ExplicitReferenceCheck → 参数Bundle → 功能目标 → 必要性 → 等效进入路径 → 市场证据 → 证明出具机构Check → 厂家例外 → Competition影响 → 证据门槛 → 合规发现项/人工复核。

中文就是：

```text
先恢复技术条款结构    # 中文：知道参数、主体、条件、时点和业务作用

再检查显性指定    # 中文：品牌、专利、商标、原产地、组件、供应商等

再检查参数组合    # 中文：防止“没有品牌名但参数指纹高度唯一”

再问功能目标    # 中文：采购人到底要实现什么

再做必要性检验    # 中文：参数是不是实现目标所必需

再看等效进入路径    # 中文：其他技术路线能否公平参与

再看市场证据    # 中文：真实竞争产品 / 供应商范围

再审证明材料和出具机构    # 中文：防止验证环节制造新的排斥

再审厂家授权例外    # 中文：D16及进口货物例外

最后进入Evidence Gate    # 中文：文件、市场、必要性、政策证据门    # 中文：证据充分才形成正式Finding，否则转人工
```

---

# 四十六、核心心智模型 ⑯
# `TechnicalDirection` 必须由“文件证据 + 市场证据 + 必要性证据”共同支持

所以：

\[
\boxed{
TechnicalFinding
\neq
LLMImpression
}
\]

**中文业务释义：** 技术合规发现项 ≠ LLM印象判断。

高风险 Finding 至少应有：

```text
document_evidence    # 中文：采购文件条款证据

market_evidence    # 中文：竞争产品 / 供应商可满足性证据

necessity_evidence    # 中文：技术要求与项目真实需求的必要性证据

policy_evidence    # 中文：适用规则与法律政策依据
```

---

# 四十七、什么时候必须 Human Review？

至少包括：

```text
市场可满足性证据不足    # 中文：无法确认到底有多少产品可满足

兼容性必要性存在争议    # 中文：现有系统约束是否真的不可替代

参数组合疑似唯一指向    # 中文：单项合理但组合后可能锁定产品

涉及专利 / 私有协议    # 中文：知识产权或独占技术边界复杂

标准版本状态不明确    # 中文：引用标准是否有效 / 强制无法确认

证明材料出具机构依据不明确    # 中文：D20需要进一步核实

厂家授权与进口货物例外不清    # 中文：D16例外状态无法确认

样品必要性无法从文件解释    # 中文：工程扩展对象需要人工判断

高风险但置信度低    # 中文：潜在影响大但证据不充分
```

因此：

\[
\boxed{
HighImpact
+
Uncertainty
\Rightarrow
HumanReview
}
\]

**中文业务释义：** 高影响 + 不确定性 ⇒ 人工复核。

---

# 四十八、技术条款修改建议怎么生成？

核心仍然是：

\[
\boxed{
Remediation
=
PreserveFunctionalGoal
+
RemoveUnnecessaryLockIn
}
\]

**中文业务释义：** 修改建议 = 保留功能目标 + 移除不必要技术锁定。

例如原要求：

```text
必须采用某品牌某型号接口    # 中文：直接限定技术实现
```

如果真实目标只是：

```text
与现有系统实现稳定数据交换    # 中文：真正业务目标
```

更专业的修改思路是：

> 把“品牌 / 型号指定”改成可验证的兼容接口、数据交换能力、性能和安全指标；如果确有不可替代兼容要求，则补充必要性与现有系统证据。

---

# 四十九、核心心智模型 ⑰
# 好的技术合规修改不是“把参数删光”

采购需求仍然必须：

```text
明确    # 中文：供应商知道要交付什么

可验证    # 中文：评审和验收知道怎样证明满足

可履约    # 中文：合同能够真正执行

能保障采购质量    # 中文：不会为了竞争而牺牲真实业务目标
```

所以：

\[
\boxed{
Neutrality
\neq
Vagueness
}
\]

**中文业务释义：** 竞争中立 ≠ 模糊不清。

真正目标是：

\[
\boxed{
Clear
+
Necessary
+
Verifiable
+
CompetitionNeutral
}
\]

**中文业务释义：** 清晰 + 必要 + 可验证 + 竞争中立。

---

# 五十、Hard Negative
## 技术域高难负例

Stage 6 必须重点积累：

```text
HardNegative_Compatibility    # 中文：有真实兼容需要，因此某些接口约束具有合理依据

HardNegative_StatutoryStandard    # 中文：法律 / 强制标准确实要求特定技术条件

HardNegative_SafetyConstraint    # 中文：安全风险要求严格参数，但不构成不合理排斥

HardNegative_PerformanceThreshold    # 中文：严格性能阈值有充分业务必要性

HardNegative_ImportedAuthorizationException    # 中文：符合进口货物等适用例外

HardNegative_ValidIssuerRequirement    # 中文：特别规定明确要求特定类型机构出具证明
```

这些样本非常重要，

因为真正专业的模型必须学会：

> **严格 ≠ 歧视。**

---

# 五十一、Counterfactual Pair
## 技术域反事实样本

### Pair A

```text
必须采用某品牌专有接口    # 中文：直接限定品牌生态和实现路径
```

### Pair B

```text
应支持与现有系统进行双向数据交换，并满足已公开的接口规范X    # 中文：把目标改成可验证的兼容能力
```

比较：

```text
BrandLockIn    # 中文：品牌生态锁定

FunctionalCompatibility    # 中文：功能兼容目标
```

---

### Pair C

```text
检测报告必须由某某机构出具    # 中文：限制单一证明材料出具机构
```

### Pair D

```text
应提供能够证明参数X达到要求的有效检测 / 证明材料；如有特别规定，从其规定    # 中文：围绕证明内容设计较中立的验证要求
```

比较：

```text
IssuerRestriction    # 中文：出具机构限制

ProofObjective    # 中文：证明目标
```

---

# 五十二、技术域 Benchmark 要测什么？

至少：

```text
D11_recall    # 中文：特定供应商 / 产品指向规则召回率

D11_precision    # 中文：D11候选 / Finding精确率

D12_recall    # 中文：品牌、专利、商标、原产地、零部件等限制召回率

D13_context_accuracy    # 中文：技术要求与项目需要 / 合同履行关联判断准确度

D15_certificate_accuracy    # 中文：证书 / 奖项类型与风险识别准确度

D16_exception_accuracy    # 中文：厂家授权及进口货物例外判断准确度

D20_issuer_accuracy    # 中文：证明材料出具机构限制识别准确度

parameter_bundle_recall    # 中文：跨参数组合锁定识别召回率

cross_clause_recall    # 中文：跨章节技术锁定识别召回率

equivalence_accuracy    # 中文：等效机制是否真实有效的判断准确度

market_evidence_groundedness    # 中文：市场可满足性结论是否真正有证据支撑

technical_evidence_localization    # 中文：技术风险原文定位准确度

hard_negative_precision    # 中文：合理严格技术要求不被误报的能力

human_escalation_accuracy    # 中文：需要人工复核的技术边界案例升级准确度
```

所以：

\[
\boxed{
TechnicalBenchmark
\neq
BrandDetectionAccuracy
}
\]

**中文业务释义：** 技术合规评测 ≠ 品牌检测准确率。

---

# 五十三、`ProcurementTechnicalCompliance_V1` 建议目录

```text
ProcurementTechnicalCompliance_V1/    # 中文：技术参数合规审查工程资产根目录

├── schema/    # 中文：结构化Schema目录
│   ├── technical_requirement.json    # 中文：技术要求数据结构
│   ├── parameter_bundle.json    # 中文：参数组合 / 参数指纹结构
│   ├── market_evidence.json    # 中文：市场可满足性证据结构
│   ├── proof_requirement.json    # 中文：检测报告 / 认证 / 证明材料结构
│   └── technical_finding.json    # 中文：技术合规发现项结构
│
├── rules/    # 中文：技术域规则执行逻辑
│   ├── D11/    # 中文：特定供应商 / 产品指向规则
│   ├── D12/    # 中文：专利 / 商标 / 品牌 / 原产地 / 零部件规则
│   ├── D13/    # 中文：与实际需要 / 合同履行不匹配规则
│   ├── D15/    # 中文：证书 / 奖项规则
│   ├── D16/    # 中文：厂家授权等规则
│   └── D20/    # 中文：技术证明材料出具机构规则
│
├── analysis/    # 中文：技术必要性与竞争影响分析模块
│   ├── functional_goal/    # 中文：功能目标解析
│   ├── necessity/    # 中文：技术必要性检验
│   ├── equivalence/    # 中文：等效进入机制分析
│   ├── compatibility/    # 中文：现有系统兼容性分析
│   └── market_satisfiability/    # 中文：市场可满足性分析
│
├── tests/    # 中文：技术规则测试集
│   ├── positive/    # 中文：正例
│   ├── hard_negative/    # 中文：高难负例
│   ├── counterfactual/    # 中文：反事实对
│   ├── exception/    # 中文：例外案例
│   └── cross_clause/    # 中文：跨条款组合案例
│
└── manifest.json    # 中文：版本、依赖、规则与测试清单
```

---

# 五十四、Technical Requirement Schema 第一版

```text
technical_requirement_id    # 中文：技术要求标识

project_id    # 中文：采购项目标识

document_id    # 中文：采购文件标识

document_version    # 中文：采购文件版本

section_id    # 中文：章节标识

clause_id    # 中文：条款标识

requirement_id    # 中文：业务要求标识

functional_goal    # 中文：功能目标

performance_indicator    # 中文：性能指标

parameter_name    # 中文：参数名称

operator    # 中文：比较关系，例如不低于 / 不高于 / 等于 / 区间

parameter_value    # 中文：参数值

unit    # 中文：计量单位

tolerance    # 中文：允许误差 / 容差

mandatory_status    # 中文：是否必须满足

substantive_status    # 中文：是否属于实质性条款

scoring_status    # 中文：是否作为评分因素

performance_obligation_status    # 中文：是否属于合同履约义务

brand_reference    # 中文：品牌引用

patent_reference    # 中文：专利引用

trademark_reference    # 中文：商标引用

origin_reference    # 中文：原产地引用

component_reference    # 中文：零部件 / 组件引用

model_reference    # 中文：型号引用

protocol_reference    # 中文：协议引用

interface_reference    # 中文：接口引用

compatibility_requirement    # 中文：兼容性要求

verification_method    # 中文：验证方式

proof_type    # 中文：证明材料类型

issuer_restriction    # 中文：证明材料出具机构限制

manufacturer_requirement    # 中文：厂家授权 / 承诺 / 证明 / 背书要求

sample_requirement    # 中文：样品要求；工程扩展字段，不代表附件9新增规则

equivalent_mechanism    # 中文：等效产品 / 等效技术路线机制

candidate_rule_ids    # 中文：候选Dxx规则标识

parse_confidence    # 中文：技术条款结构化解析置信度
```

---

# 五十五、Technical Analysis Schema 第一版

```text
technical_analysis_id    # 中文：技术合规分析记录标识

functional_goal    # 中文：真实采购功能目标

project_need_relation    # 中文：技术要求与项目实际需要的关系

contract_performance_link    # 中文：与合同履约目标的对应关系

minimum_sufficient_analysis    # 中文：是否属于最小充分技术约束

alternative_technical_paths    # 中文：可替代技术路线

equivalent_path_status    # 中文：等效产品 / 技术进入路径是否真实可行

compatibility_evidence    # 中文：兼容性必要性证据

parameter_bundle_id    # 中文：参数组合标识

combination_fingerprint_status    # 中文：参数组合是否形成明显产品指纹

market_evidence_id    # 中文：市场可满足性证据标识

market_satisfiability_status    # 中文：市场可满足性状态

competition_impact    # 中文：竞争影响

exception_status    # 中文：例外状态

supporting_evidence    # 中文：支持技术必要性的证据

counter_evidence    # 中文：反对 / 削弱必要性的证据

uncertainty    # 中文：仍未解决的不确定事项

human_review_required    # 中文：是否需要人工复核
```

---

# 五十六、本阶段最重要的 17 个核心心智模型

> **心智模型 ①：`TechnicalSpecificity ≠ TechnicalDiscrimination`。技术要求可以具体，真正审查的是具体性是否必要、合理并保持公平竞争。**

> **心智模型 ②：`TechnicalRequirement → FunctionalGoal`。每一个技术约束都应该能够解释它服务于什么真实采购目标。**

> **心智模型 ③：`NoBrandName ≠ NoProductDirection`。没有品牌名，也可能通过参数组合、私有接口、独特组件形成特定产品指向。**

> **心智模型 ④：`SingleParameterReasonable ≠ ParameterCombinationNeutral`。单项参数合理，不代表参数组合仍然中立。**

> **心智模型 ⑤：`EquivalentWording ≠ EffectiveEquivalence`。写了“或相当于”不代表其他竞争产品真的有可执行的等效进入路径。**

> **心智模型 ⑥：`FunctionalGoal ≠ SpecificImplementationPath`。采购目标与某一种技术实现方式必须分开。**

> **心智模型 ⑦：`MinimalSufficientConstraint`。好的技术要求应当是实现采购目的所需要的最小充分约束。**

> **心智模型 ⑧：`CompatibilityNeed ≠ BrandLockIn`。真实兼容要求可以合理，但必须有现有系统、接口、迁移与风险证据支撑。**

> **心智模型 ⑨：`ModelBelief ≠ MarketEvidence`。LLM不能凭印象判断“市场只有一家能满足”。**

> **心智模型 ⑩：`SingleFeasibleProduct ≠ AutomaticViolation`。市场上产品很少仍需继续检查项目必要性、替代方案和适用依据。**

> **心智模型 ⑪：`Relevant ≠ UnlimitedConstraint`。参数与项目有关，不等于可以无限精细或锁定到独有值。**

> **心智模型 ⑫：`SameTechnicalParameter + DifferentBusinessFunction = DifferentCompetitionImpact`。作为评分项、实质性条款或履约义务，竞争影响不同。**

> **心智模型 ⑬：`ProofObjective ≠ SpecificProofForm`。需要证明技术事实，不等于必须限定某一种证书、报告形式。**

> **心智模型 ⑭：`NeedProof ≠ NeedSpecificIssuer`。需要检测 / 证明不等于必须由某特定机构出具。**

> **心智模型 ⑮：`EngineeringExtension ≠ SourceRule`。样品等工程扩展审查对象不能被虚构成附件9新增Dxx规则。**

> **心智模型 ⑯：`LocalClauseReview ≠ CrossClauseTechnicalReview`。技术锁定可能分散在技术、商务、实质性条款和评分表中。**

> **心智模型 ⑰：`Neutrality ≠ Vagueness`。公平竞争不等于把技术需求写模糊；目标是清楚、必要、可验证且不过度锁定。**

---

# 五十七、把整个技术合规判断压成一张工程图

```text
                    Technical Document Units    # 中文：技术参数、表格、附件、脚注等技术业务单元
                    # 中文：技术参数、表格、附件、脚注等技术业务单元
                               │
                               ▼
                     Requirement Parsing    # 中文：恢复参数、条件、时点和业务作用
                     # 中文：恢复参数、条件、时点和业务作用
                               │
                               ▼
                 Explicit Reference Detection    # 中文：检测品牌、专利、商标、原产地、组件、型号等显性引用
                 # 中文：品牌 / 专利 / 商标 / 原产地 / 组件 / 型号显性引用
                               │
                               ▼
                    Parameter Bundle    # 中文：把分散参数组合成完整技术约束集合
                    # 中文：把分散参数组合成完整技术约束集合
                               │
                               ▼
                   Functional Goal    # 中文：采购人真正要实现的功能目标
                   # 中文：采购人真正要实现的功能目标
                               │
                               ▼
                 Technical Necessity Test    # 中文：技术必要性检验，包括相关性、最小充分性、替代方案和可验证性
                 # 中文：相关性、最小充分性、替代方案、验证方式
                               │
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
      Compatibility / Equivalent Path / Proof-Issuer    # 中文：兼容性 / 等效进入路径 / 证明材料与出具机构
      # 中文：兼容性       # 中文：等效路径       # 中文：证明材料与出具机构
             │                 │                 │
             └─────────────────┼─────────────────┘
                               ▼
                     Market Satisfiability    # 中文：真实市场可满足性证据
                     # 中文：真实市场可满足性证据
                               │
                               ▼
                      Competition Impact    # 中文：技术要求对供应商和产品竞争范围的影响
                      # 中文：竞争范围是否被不必要压缩
                               │
                               ▼
                         D11 / D12 / D13    # 中文：产品指向、显性限定、技术必要性相关规则
                         D15 / D16 / D20    # 中文：证书奖项、厂家授权、证明材料出具机构相关规则
                         # 中文：技术域候选专项规则
                               │
                               ▼
                         Evidence Gate    # 中文：文件、市场、必要性、政策证据门
                         # 中文：文件 / 市场 / 必要性 / 政策证据门
                               │
                  ┌────────────┴────────────┐
                  ▼                         ▼
           Supported Finding / Unresolved-Borderline    # 中文：证据支持的发现项 / 未解决或边界案件
           # 中文：证据支持的风险项     # 中文：证据不足或边界案件
                  │                         │
                  ▼                         ▼
             Remediation / Human Review    # 中文：修改建议 / 人工复核
             # 中文：修改建议             # 中文：人工复核
```

脑中最后只留一句：

> **政府采购技术参数合规的本质，不是“技术要求越宽松越好”，而是把采购人的真实功能目标翻译成清楚、可验证、最小充分的技术约束；系统既要识别显性的品牌、专利、商标、原产地和零部件限制，也要识别由参数组合、私有接口、兼容条件、指定证明形式和出具机构等形成的隐性产品指向，同时必须用项目必要性、等效路径、市场可满足性和适用政策证据约束判断，避免把合理的严格技术要求误报成差别歧视。**

---

# 第十一课 · 第 6 阶段掌握测试

现在不回看正文，你应该能够解释：

```text
TechnicalSpecificity 为什么不等于 TechnicalDiscrimination？
# 中文：技术要求具体和技术歧视的边界是什么？

为什么每个技术参数都应该能够回到 Functional Goal    # 中文：采购人真正要实现的功能目标？
# 中文：参数为什么必须能解释真实采购功能目标？

为什么 NoBrandName 不等于 NoProductDirection？
# 中文：没有品牌名为什么仍可能锁定特定产品？

什么是 Parameter Fingerprint？
# 中文：参数指纹如何由多项技术约束组合形成？

为什么 SingleParameterReasonable 不等于 ParameterCombinationNeutral？
# 中文：为什么技术要求必须做组合审查？

D11 和 D12 的区别是什么？
# 中文：技术 / 服务指向与显性品牌、专利等限定分别怎样识别？

为什么写了“或相当于”仍然要检查 Equivalent Mechanism？
# 中文：什么叫真正可执行的等效进入路径？

Functional Goal    # 中文：采购人真正要实现的功能目标 与 Implementation Path 有什么区别？
# 中文：采购目标和技术实现路径为什么要分开？

什么叫 Minimal Sufficient Constraint？
# 中文：为什么不是参数越多越专业？

Compatibility Need 为什么不自动等于 Brand Lock-in？
# 中文：现有系统兼容怎样提供必要性证据？

为什么 LLM 不能自己宣布“市场上只有一家能满足”？
# 中文：Market Evidence 为什么必须独立存在？

Single Feasible Product 为什么不自动等于违规？
# 中文：为什么还要检查特殊需求、兼容性、替代方案和政策依据？

D13 的 Technical Necessity Test    # 中文：技术必要性检验，包括相关性、最小充分性、替代方案和可验证性 六问是什么？
# 中文：功能目标、相关性、最小充分性、可验证性、替代方案、竞争影响分别解决什么？

为什么 Mandatory / Substantive / Scoring / Performance Obligation 必须分开？
# 中文：同一参数在不同业务作用下为什么竞争影响不同？

Proof Objective 与 Specific Proof Form 为什么不是一回事？
# 中文：需要证明性能为什么不一定要指定一种证书？

为什么 Need Proof 不等于 Need Specific Issuer？
# 中文：D20为什么重点检查证明内容和出具机构之间的区别？

D16 为什么必须同时检查 Imported Goods Exception？
# 中文：厂家授权等要求怎样做例外判断？

样品为什么是 Engineering Extension，而不是新的 D23？
# 中文：怎样保持来源规则与工程扩展的边界？

为什么 Cross-clause Review 对技术参数特别重要？
# 中文：技术锁定为什么可能分散在多个章节？

为什么 Neutrality 不等于 Vagueness？
# 中文：公平竞争与采购需求明确性怎样同时成立？
```

如果这些能够完整解释：

\[
\boxed{
第十一课第6阶段真正掌握
}
\]

---

# 下一阶段：第十一课 · 第 7 阶段
# 评审标准合规：量化、分值、业绩、奖项、人员、主观分与资格评分化
## 怎样识别“资格条件换个位置放进评分表”“看似可以打分、实际无法客观量化”“通过分值设计变相排斥供应商”等风险？

下一阶段将重点连接：

```text
ScoringFunction    # 中文：评分函数 / 评分规则结构

QualificationCrossCheck    # 中文：资格条件与评分标准交叉检查

ExperienceScoring    # 中文：业绩评分

AwardScoring    # 中文：奖项评分

PersonnelScoring    # 中文：人员条件评分

SubjectiveScoring    # 中文：主观评分

Quantifiability    # 中文：评分标准可量化程度

CompetitionImpact    # 中文：评分规则对竞争的实际影响
```

并建立：

# `ProcurementScoringCompliance_V1`

下一阶段最重要的边界：

\[
\boxed{
Scorable
\neq
CompliantScoringFactor
}
\]

**中文业务释义：** Scorable ≠ Compliant评分Factor。
