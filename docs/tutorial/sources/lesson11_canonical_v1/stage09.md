# 第十一课 · 第 9 阶段
# 采购方式、竞争充分性与异常低价检查
## 市场竞争是否真实存在？单一来源等采购方式是否成立？确定性低价规则什么时候必须启动审查？怎样把“供应商数量、采购方式、异常低价、履约风险”接成一套可计算、可解释、可审计的政府采购竞争合规系统？

第 8 阶段我们已经建立：

\[
\boxed{
PolicyPreference
\neq
IllegalDiscrimination
}
\]

**中文业务释义：** 有明确制度依据的政府采购政策支持、优惠、预留和特殊程序 ≠ 采购人自行设置的不合理差别歧视待遇。

并且建立：

\[
\boxed{
PolicyApplicability
\rightarrow
Calculator
}
\]

**中文业务释义：** 先由政策引擎确认政策是否适用，再把明确比例、金额、份额和价格调整交给确定性计算器。

现在进入采购活动中另一个决定竞争是否真实、价格是否可靠的核心领域：

# Competition Compliance
## 竞争合规

本阶段第一条核心边界：

\[
\boxed{
LowPrice
\neq
AbnormallyLowPrice
}
\]

**中文业务释义：** 报价低 ≠ 异常低价；只有触发适用规则或评审委员会基于专业判断认为可能影响产品质量、诚信履约时，才进入异常低价审查程序。

第二条核心边界：

\[
\boxed{
ObservedOneSupplier
\neq
OnlyOneSupplierExists
}
\]

**中文业务释义：** 实际只有一家供应商投标 / 响应 ≠ 市场上依法只能从唯一供应商采购；“只有一家来”与“客观上只有一家能供”是完全不同的事实。

本阶段最终形成：

# `ProcurementCompetitionCompliance_V1`

---

# 一、本阶段的当前法规政策基线

截至本阶段校对时点：

```text
《中华人民共和国政府采购法》
# 中文：采购方式、公开招标、邀请招标、竞争性谈判、单一来源、询价以及方式适用条件的基础法律

《中华人民共和国政府采购法实施条例》
# 中文：进一步规定单一来源公示、评审程序等制度要求

财政部令第74号《政府采购非招标采购方式管理办法》
# 中文：竞争性谈判、单一来源采购、询价采购的具体程序规则

财库〔2014〕214号《政府采购竞争性磋商采购方式管理暂行办法》
# 中文：竞争性磋商的适用情形、供应商邀请、磋商、综合评分等程序规则

财库〔2015〕124号
# 中文：竞争性磋商中政府购买服务项目符合要求供应商只有2家时的特定处理规则

财库〔2026〕2号《关于推动解决政府采购异常低价问题的通知》
# 中文：自2026年2月1日起施行，建立全国政府采购异常低价审查触发规则、解释举证、审查、归档和履约跟踪要求

财库〔2026〕12号《紧急采购管理暂行办法》
# 中文：已经发布，但自2026年10月1日起施行；在本阶段校对时点尚未生效
```

因此本阶段必须再次应用 Stage 2 的时间心智模型：

\[
\boxed{
Published
\neq
Effective
}
\]

**中文业务释义：** 文件已经发布 ≠ 当前项目已经可以适用；截至 2026 年 9 月 20 日，财库〔2026〕12号属于“已发布、尚未生效”状态。

---

# 二、先把三个经常混淆的概念彻底分开

政府采购项目里至少有三层：

```text
ProcurementOrganization
# 中文：采购组织形式，例如集中采购、分散采购

ProcurementMethod
# 中文：采购方式，例如公开招标、邀请招标、竞争性谈判、竞争性磋商、单一来源、询价等

EvaluationMethod
# 中文：评审方法，例如最低评标价法、综合评分法等
```

所以：

\[
\boxed{
ProcurementOrganization
\neq
ProcurementMethod
\neq
EvaluationMethod
}
\]

**中文业务释义：** 采购组织形式 ≠ 采购方式 ≠ 评审方法；系统不能把“集中采购”“竞争性磋商”“综合评分法”混成同一维度。

---

# 三、政府采购法中的采购方式框架

政府采购法第二十六条列明：

```text
PUBLIC_TENDER
# 中文：公开招标

INVITED_TENDER
# 中文：邀请招标

COMPETITIVE_NEGOTIATION
# 中文：竞争性谈判

SINGLE_SOURCE
# 中文：单一来源采购

INQUIRY
# 中文：询价

OTHER_RECOGNIZED_METHOD
# 中文：国务院政府采购监督管理部门认定的其他采购方式
```

并明确：

> 公开招标应作为政府采购的主要采购方式。

竞争性磋商则依据政府采购法第二十六条第一款第六项，由财库〔2014〕214号建立具体规则。

---

# 四、核心心智模型 ①
# `MethodChoice` 必须有法定 / 政策依据

\[
\boxed{
ProcurementMethod
=
ProjectFacts
+
ThresholdRule
+
StatutoryCondition
+
ApprovalRequirement
}
\]

**中文业务释义：** 采购方式 = 项目事实 + 数额标准规则 + 法定适用条件 + 必要的审批 / 决策程序。

不能只因为：

```text
“这样比较快”
# 中文：采购便利性

“以前一直这么做”
# 中文：历史习惯

“市场上好像只有几家”
# 中文：未经证据验证的市场印象
```

就决定采购方式。

---

# 五、公开招标数额标准不能全国写死一个值

政府采购法第二十七条明确：

> 中央预算政府采购项目与地方预算政府采购项目的公开招标数额标准，由不同层级依法确定。

因此：

\[
\boxed{
PublicTenderThreshold
\neq
OneNationalConstant
}
\]

**中文业务释义：** 公开招标数额标准 ≠ 全国永远使用一个固定金额。

系统必须解析：

```text
budget_level
# 中文：中央预算还是地方预算

jurisdiction
# 中文：具体省、自治区、直辖市及必要的级次

procurement_object_type
# 中文：货物、服务、工程

effective_date
# 中文：项目时点

threshold_document_id
# 中文：当前适用的集中采购目录 / 数额标准文件

threshold_amount
# 中文：当前适用公开招标数额标准
```

---

# 六、Threshold Resolver
## 数额标准解析器

正式建立：

\[
\boxed{
Threshold
=
f(
BudgetLevel,
Jurisdiction,
ObjectType,
EffectiveDate
)
}
\]

**中文业务释义：** 公开招标数额标准是预算级次、地区、采购对象类型和政策时点共同决定的结果。

所以：

> 生产系统不得在代码里只写一个 `2,000,000` 或 `4,000,000` 当作全国永久标准。

---

# 七、达到公开招标数额标准后怎样处理？

原则上：

```text
public_tender_required
# 中文：达到适用公开招标数额标准，应依法采用公开招标
```

如果符合法定特殊情形、拟改用其他采购方式：

```text
alternative_method_condition
# 中文：是否满足其他采购方式的法定适用条件

approval_required
# 中文：是否需要在采购活动开始前取得相应财政部门批准
```

因此：

\[
\boxed{
AboveThreshold
+
WantAlternativeMethod
\Rightarrow
ConditionCheck
+
ApprovalCheck
}
\]

**中文业务释义：** 达到公开招标数额标准 + 想采用非公开招标方式 ⇒ 必须同时检查法定适用条件和审批要求。

---

# 八、化整为零规避公开招标

政府采购法第二十八条明确：

> 不得将应当以公开招标方式采购的货物或者服务化整为零或者以其他任何方式规避公开招标。

工程上需要建立：

```text
same_budget_project
# 中文：是否属于同一预算项目

same_procurement_category
# 中文：是否属于同一采购品目 / 采购对象

time_proximity
# 中文：多个采购发生时间是否高度接近

supplier_overlap
# 中文：供应商范围是否高度重合

business_goal_overlap
# 中文：采购目标是否属于同一业务需求

split_reason
# 中文：拆分采购包是否存在真实专业、交付、区域、进度等合理理由
```

---

# 九、核心心智模型 ②
# `PackageSplit` 不等于 `Evasion`

\[
\boxed{
ReasonablePackageDesign
\neq
TenderEvasion
}
\]

**中文业务释义：** 合理划分采购包 ≠ 化整为零规避公开招标；关键要判断拆包是否基于专业类型、市场供给、履约组织等真实需要，还是为了绕开适用数额标准和程序。

---

# 十、邀请招标的适用条件

政府采购法第二十九条规定，货物或者服务符合下列情形之一，可以采用邀请招标：

```text
limited_supplier_scope_due_to_speciality
# 中文：具有特殊性，只能从有限范围的供应商处采购

public_tender_cost_disproportionate
# 中文：采用公开招标方式的费用占项目总价值比例过大
```

注意：

\[
\boxed{
LimitedSupplierRange
\neq
SingleSupplier
}
\]

**中文业务释义：** 供应商范围有限 ≠ 只有唯一供应商；邀请招标和单一来源不是同一逻辑。

---

# 十一、竞争性谈判的适用条件

政府采购法第三十条及财政部令第74号规定的典型情形包括：

```text
failed_tender
# 中文：招标后没有供应商投标、没有合格标的或重新招标仍未成立

complex_or_special
# 中文：技术复杂或性质特殊，不能确定详细规格 / 具体要求

urgent_need_not_caused_by_purchaser
# 中文：因非采购人可预见、非采购人拖延造成的紧急需要，招标时间无法满足

total_price_not_precalculable
# 中文：因艺术品、专利、专有技术或服务时间数量不确定等原因不能事先计算价格总额
```

---

# 十二、核心心智模型 ③
# `Urgency` 必须区分“真实紧急”和“采购人拖延”

\[
\boxed{
SelfCreatedUrgency
\neq
LawfulUrgency
}
\]

**中文业务释义：** 因采购人自身拖延、计划不足造成的时间紧迫 ≠ 当然满足竞争性谈判等制度中的紧急适用条件。

---

# 十三、竞争性磋商的适用条件

财库〔2014〕214号列明的典型情形包括：

```text
government_purchase_of_services
# 中文：政府购买服务项目

complex_or_special
# 中文：技术复杂或性质特殊，不能确定详细规格 / 具体要求

price_not_precalculable
# 中文：艺术品、专利、专有技术或服务时间数量等原因导致不能事先计算价格总额

research_market_competition_insufficient
# 中文：市场竞争不充分的科研项目，以及需要扶持的科技成果转化项目

non_mandatory_tender_construction
# 中文：依法必须招标的工程建设项目之外的工程建设项目
```

因此：

\[
\boxed{
CompetitiveConsultation
\neq
UniversalFlexibleMethod
}
\]

**中文业务释义：** 竞争性磋商 ≠ “不好选方式时就用”的万能灵活采购方式；仍需满足适用条件。

---

# 十四、询价采购的适用条件

政府采购法第三十二条规定：

> 货物规格、标准统一，现货货源充足且价格变化幅度小的政府采购项目，可以采用询价方式。

因此：

\[
\boxed{
Inquiry
=
StandardizedGoods
+
AdequateSpotSupply
+
LowPriceVolatility
}
\]

**中文业务释义：** 询价适合规格标准统一、现货供应充分、价格波动较小的货物采购，而不是所有“想比最低价”的项目。

---

# 十五、单一来源的三类法定情形

政府采购法第三十一条规定：

```text
ONLY_ONE_SUPPLIER
# 中文：只能从唯一供应商处采购

UNFORESEEABLE_EMERGENCY
# 中文：发生不可预见的紧急情况，不能从其他供应商处采购

CONSISTENCY_OR_SUPPORTING_ADDITIONAL_PURCHASE
# 中文：为保证原项目一致性或服务配套，需要继续从原供应商添购，并满足金额限制
```

这三类情形：

> 不是同一种证据逻辑。

---

# 十六、核心心智模型 ④
# `OneBidderObserved` 不等于 `OnlyOneSupplierExists`

\[
\boxed{
OneBidderObserved
\neq
OnlyOneSupplierExists
}
\]

**中文业务释义：** 招标现场只有一家供应商来投标 ≠ 客观市场上只有这一家供应商能够提供。

出现“一家来投”的原因可能是：

```text
market_truly_unique
# 中文：市场客观唯一

restrictive_requirements
# 中文：资格、技术、评分条件过度限制

insufficient_publicity
# 中文：公告传播不足

short_response_time
# 中文：供应商准备时间不足

package_too_large
# 中文：采购包过大、过杂

high_participation_cost
# 中文：投标成本过高

poor_market_timing
# 中文：采购时点与市场供给不匹配
```

所以必须先做：

# Root Cause Analysis
## 竞争不足根因分析

---

# 十七、公开招标失败不能自动“顺滑变成单一来源”

财政部对第74号令的公开解读明确强调：

> 公开招标只有一家供应商响应，不能因此直接等同于“只能从唯一供应商处采购”。

所以：

\[
\boxed{
FailedTender
+
OneSupplier
\neq
AutomaticSingleSource
}
\]

**中文业务释义：** 招标失败 + 只有一家供应商响应 ≠ 自动满足单一来源“只能从唯一供应商处采购”的法定条件。

---

# 十八、真正的“唯一供应商”需要什么证据？

建议至少建立：

```text
market_research_id
# 中文：市场调研记录标识

alternative_supplier_search
# 中文：替代供应商搜索范围和方法

functional_substitute_analysis
# 中文：是否存在功能可替代方案

technical_exclusivity
# 中文：是否存在客观不可替代的技术独占

ip_exclusivity
# 中文：专利 / 著作权 / 专有技术是否真的造成排他性

compatibility_exclusivity
# 中文：现有系统兼容是否客观只能由原供应商满足

switching_cost_evidence
# 中文：替换供应商的真实迁移成本

reasonable_alternative_absence
# 中文：是否确实不存在合理替代方案
```

因此：

\[
\boxed{
UniqueSupplierClaim
\neq
UniqueSupplierEvidence
}
\]

**中文业务释义：** 声称“只有一家能做” ≠ 已经证明市场客观上只有一家能够满足。

---

# 十九、专利 / 专有技术也不自动等于单一来源

\[
\boxed{
PatentExists
\neq
OnlyOneSupplier
}
\]

**中文业务释义：** 项目涉及专利或专有技术 ≠ 必然只能从一个供应商处采购；还要检查是否存在合法授权、替代技术、等效方案或其他可供应主体。

这与 Stage 6 的：

\[
\boxed{
NoBrandName
\neq
NoProductDirection
}
\]

**中文业务释义：** 未出现品牌名称 ≠ 不存在特定产品指向；技术参数、接口、组件和兼容性组合仍可能形成隐性产品锁定。

共同构成：

> 技术独占与市场独占必须分别验证。

---

# 二十、原供应商添购的 10% 上限

政府采购法第三十一条第三项要求：

> 为保证原有采购项目一致性或服务配套，需要继续从原供应商添购时，添购资金总额不得超过原合同采购金额的 10%。

工程计算：

\[
\boxed{
AdditionalPurchaseRatio
=
AdditionalPurchaseAmount
/
OriginalContractAmount
}
\]

**中文业务释义：** 添购比例 = 累计添购金额 ÷ 原合同采购金额。

并且：

\[
\boxed{
AdditionalPurchaseRatio
\leq
10\%
}
\]

**中文业务释义：** 按该法定情形采用单一来源继续从原供应商添购时，累计添购金额不得超过原合同采购金额的 10%。

---

# 二十一、核心心智模型 ⑤
# “不超过10%”只是必要条件之一

\[
\boxed{
RatioWithin10Percent
\neq
AutomaticallyValidSingleSource
}
\]

**中文业务释义：** 添购金额不超过 10% ≠ 单一来源当然成立；还必须存在保证原项目一致性或服务配套的真实需要，并且继续从原供应商添购。

---

# 二十二、单一来源的公示要求

政府采购法实施条例第三十八条和财政部令第74号第三十八条要求：

> 达到公开招标数额标准、属于“只能从唯一供应商处采购”的货物服务项目，拟采用单一来源采购的，应按规定进行单一来源公示，公示期不得少于 5 个工作日，并履行相应批准程序。

因此：

```text
single_source_publicity_required
# 中文：是否需要单一来源公示

publicity_start_date
# 中文：公示开始日期

publicity_end_date
# 中文：公示结束日期

publicity_working_days
# 中文：有效公示工作日数量

objection_received
# 中文：是否收到其他供应商 / 专业人员异议

objection_resolution
# 中文：异议是否被充分处理
```

---

# 二十三、核心心智模型 ⑥
# `SingleSourceReason` 和 `SingleSourceProcedure` 必须同时成立

\[
\boxed{
SingleSourceCompliance
=
SubstantiveCondition
+
RequiredProcedure
}
\]

**中文业务释义：** 单一来源合规 = 实体适用条件成立 + 应履行的审批、公示、论证和协商程序正确。

---

# 二十四、供应商数量到底怎么判断“竞争充分”？

不能只看：

```text
supplier_count
# 中文：最终参与供应商数量
```

而要建立：

# Competition Funnel
## 竞争漏斗

\[
\boxed{
PotentialMarket
\rightarrow
AwareSuppliers
\rightarrow
DocumentAccess
\rightarrow
SubmittedResponses
\rightarrow
QualificationPassed
\rightarrow
ConformityPassed
\rightarrow
ValidPrices
\rightarrow
Candidates
}
\]

**中文业务释义：** 潜在市场供应商 → 知悉采购信息 → 获取采购文件 → 实际投标 / 响应 → 通过资格审查 → 通过符合性审查 → 形成有效报价 → 进入成交 / 中标候选。

---

# 二十五、核心心智模型 ⑦
# `CompetitionLoss` 要定位发生在哪一层

例如：

```text
PotentialMarket = 50
# 中文：市场上可能有50家潜在供应商

AwareSuppliers = 20
# 中文：20家实际获得采购信息

DocumentAccess = 12
# 中文：12家获取采购文件

SubmittedResponses = 3
# 中文：只有3家实际提交响应

QualificationPassed = 2
# 中文：2家通过资格

ConformityPassed = 1
# 中文：最终只有1家通过符合性审查
```

这时：

> “竞争不足”的根因可能根本不在市场，而在采购文件条件或程序设计。

---

# 二十六、Competition Sufficiency
## 竞争充分性的多维模型

可以建立：

\[
\boxed{
CompetitionSufficiency
=
MarketBreadth
+
AccessFairness
+
RequirementNeutrality
+
ResponseTime
+
PackageReasonableness
+
ValidSupplierCount
}
\]

**中文业务释义：** 竞争充分性 = 市场供给广度 + 信息获取公平性 + 采购条件中立性 + 合理响应时间 + 采购包合理性 + 有效竞争供应商数量。

这是工程分析框架，不是法律公式。

---

# 二十七、竞争不足时必须回查 D01～D22

如果：

> 大量供应商在资格、技术、评分环节被排除，

系统应自动回查：

```text
D01-D10
# 中文：资格和市场准入限制

D11-D16
# 中文：技术、品牌、证书、授权等限制

D17-D22
# 中文：名录库、登记、文件获取门槛、出具机构、黑名单等其他限制
```

因此：

\[
\boxed{
LowCompetition
\rightarrow
DiscriminationRuleCrossCheck
}
\]

**中文业务释义：** 竞争度异常偏低时，应联动检查差别歧视条款，而不是只把问题归咎于“市场没有供应商”。

---

# 二十八、供应商最低数量不能写成一个全局常量

竞争性谈判、询价一般要求：

```text
minimum_suppliers = 3
# 中文：通常至少需要3家符合条件的供应商参加
```

但存在制度例外。

例如财政部令第74号规定：

> 公开招标过程中提交投标文件或经评审实质性响应的供应商只有2家，符合条件并经批准转为竞争性谈判时，可以由2家继续谈判。

竞争性磋商中：

> 财库〔2014〕214号对“市场竞争不充分的科研项目”等特定情形允许2家提交最后报价；财库〔2015〕124号对政府购买服务项目符合要求供应商只有2家的特定情形允许继续开展。

所以：

\[
\boxed{
MinimumSupplierCount
=
MethodSpecificRule
+
ExceptionRule
}
\]

**中文业务释义：** 最低供应商数量 = 当前采购方式的一般规则 + 当前项目是否命中特定例外，不能全系统统一写死成“永远3家”。

---

# 二十九、核心心智模型 ⑧
# `SupplierCount` 是程序事实，不是市场结论

\[
\boxed{
SupplierCount
\neq
MarketUniqueness
}
\]

**中文业务释义：** 供应商数量是当前采购程序的观察结果 ≠ 对整个市场结构的最终结论。

---

# 三十、现在进入 2026 年最重要的新规则之一：异常低价审查

财库〔2026〕2号：

# 《关于推动解决政府采购异常低价问题的通知》

自：

```text
2026-02-01
# 中文：2026年2月1日
```

起施行。

它把异常低价审查从：

> 模糊的“专家觉得太低”

升级为：

> **确定性数值触发 + 专业判断触发 + 供应商解释举证 + 评审委员会审查 + 全程归档。**

---

# 三十一、核心心智模型 ⑨
# `LowPrice` 不等于 `AbnormallyLowPrice`

\[
\boxed{
LowPrice
\neq
AbnormallyLowPrice
}
\]

**中文业务释义：** 报价比别人低 ≠ 自动属于异常低价；应依据财库〔2026〕2号及采购文件确定的触发规则启动审查。

---

# 三十二、异常低价触发条件 1：低于有效报价平均值的一定比例

财库〔2026〕2号规定基础触发标准：

\[
\boxed{
P_i
<
Average(PassedConformityPrices)
\times
50\%
}
\]

**中文业务释义：** 某供应商报价低于全部通过符合性审查供应商报价平均值的 50% 时，触发异常低价审查。

工程字段：

```text
supplier_price
# 中文：当前供应商投标 / 响应报价

passed_conformity_prices
# 中文：全部通过符合性审查供应商的有效报价集合

average_valid_price
# 中文：通过符合性审查供应商报价平均值

average_trigger_rate
# 中文：平均报价触发比例，基础规则为50%，采购文件可依法提高但最高不得超过65%
```

---

# 三十三、异常低价触发条件 2：低于次低报价的一定比例

基础规则：

\[
\boxed{
P_{low}
<
P_{second\_low}
\times
50\%
}
\]

**中文业务释义：** 最低报价低于通过符合性审查的次低报价供应商报价的 50% 时，触发异常低价审查。

这条特别适合识别：

> 某一个报价与其他有效报价之间出现巨大断层。

---

# 三十四、异常低价触发条件 3：低于最高限价的一定比例

基础规则：

\[
\boxed{
P_i
<
PriceCeiling
\times
45\%
}
\]

**中文业务释义：** 某供应商报价低于采购项目最高限价的 45% 时，触发异常低价审查。

如果项目没有设定最高限价：

\[
\boxed{
PriceCeiling
=
ProjectBudget
}
\]

**中文业务释义：** 未设置最高限价的项目，按财库〔2026〕2号以采购预算视为最高限价用于异常低价规则判断。

---

# 三十五、异常低价触发条件 4：专业判断

即使没有命中前三个数值条件：

> 评审委员会基于专业判断，认为报价过低，可能影响产品质量或者不能诚信履约，

仍应启动异常低价审查。

所以：

\[
\boxed{
NoNumericTrigger
\neq
NoLowPriceRisk
}
\]

**中文业务释义：** 没有命中三个确定性数值阈值 ≠ 一定不存在异常低价风险；仍保留评审委员会基于专业经验启动审查的入口。

---

# 三十六、采购文件可以提高数值触发标准

财库〔2026〕2号规定：

> 采购人可以结合项目实际，提高前述第1～第3项的数值标准，但最高不得超过 65%。

因此：

```text
base_average_rate = 0.50
# 中文：平均报价基础触发比例

base_second_low_rate = 0.50
# 中文：次低报价基础触发比例

base_ceiling_rate = 0.45
# 中文：最高限价基础触发比例

configured_rate_max = 0.65
# 中文：采购文件依法提高数值标准时的最高上限
```

---

# 三十七、核心心智模型 ⑩
# `ThresholdConfiguration` 必须来自采购文件

\[
\boxed{
ConfiguredTriggerRate
\neq
ModelChosenRate
}
\]

**中文业务释义：** 项目实际采用的异常低价触发比例 ≠ 模型自己选择的比例；必须读取采购文件和当前有效规则。

---

# 三十八、严格小于还是小于等于？

财库〔2026〕2号的公式明确使用：

```text
<
# 中文：严格小于
```

因此工程实现时：

\[
\boxed{
Price
=
Threshold
\Rightarrow
NoNumericTriggerByThatCondition
}
\]

**中文业务释义：** 如果报价恰好等于该数值触发线，按通知给出的“<”公式，不因这一数值条件本身触发；但仍可能因其他条件或专业判断进入审查。

这是典型：

# Boundary Condition
## 边界条件

必须进入测试集。

---

# 三十九、政策性评审价格和异常低价报价基数不能混

Stage 8 已经存在：

```text
evaluation_price
# 中文：本国产品、小微企业等政策调整后的评审价格
```

而财库〔2026〕2号异常低价规则使用的是：

```text
bid_response_price
# 中文：供应商投标 / 响应报价
```

所以：

\[
\boxed{
PolicyEvaluationPrice
\neq
AbnormalLowPriceTriggerPrice
}
\]

**中文业务释义：** 政策优惠后的评审价格 ≠ 异常低价数值触发所直接使用的供应商投标 / 响应报价，系统不能把两套价格字段混在一起。

---

# 四十、最重要的边界：触发审查 ≠ 无效投标

\[
\boxed{
ThresholdHit
\neq
InvalidBid
}
\]

**中文业务释义：** 命中异常低价触发条件 ≠ 自动把供应商投标 / 响应认定无效。

正确流程是：

\[
\boxed{
Trigger
\rightarrow
SupplierExplanation
\rightarrow
CostEvidence
\rightarrow
CommitteeReview
\rightarrow
Decision
}
\]

**中文业务释义：** 触发规则 → 要求供应商解释 → 提交成本和报价合理性证据 → 评审委员会审查 → 最终判断报价是否合理。

---

# 四十一、供应商解释时间

财库〔2026〕2号规定：

> 启动异常低价审查后，应给予供应商在评审现场合理时间提交书面说明及必要证明材料，合理时间一般不少于 30 分钟。

因此：

```text
explanation_requested_at
# 中文：评审委员会发出解释要求的时间

explanation_deadline
# 中文：供应商提交解释的截止时间

explanation_minutes
# 中文：实际给予供应商的解释时间

minimum_general_guideline_minutes = 30
# 中文：通知规定的一般合理时间原则上不少于30分钟
```

---

# 四十二、供应商需要解释什么？

至少包括：

```text
material_cost
# 中文：原材料成本

labor_cost
# 中文：人工成本

manufacturing_cost
# 中文：制造费用

service_delivery_cost
# 中文：服务项目实际履约成本

logistics_cost
# 中文：运输 / 配送成本

maintenance_cost
# 中文：后续维护成本

consumables_cost
# 中文：专用耗材成本

other_cost_basis
# 中文：其他与报价合理性相关的成本依据

business_reason
# 中文：规模采购、库存、工艺、效率等形成低价的合理商业原因
```

---

# 四十三、核心心智模型 ⑪
# `Cheap` 不等于 `Unsustainable`

\[
\boxed{
Cheap
\neq
Unsustainable
}
\]

**中文业务释义：** 报价很便宜 ≠ 一定无法履约；供应商可能有真实成本优势，但必须通过可验证成本说明和证明材料支持。

---

# 四十四、什么时候会被按无效投标 / 响应处理？

财库〔2026〕2号规定：

> 供应商不能提供书面说明、证明材料，或者提供的说明材料不能证明报价合理性的，评审委员会应当将其作为无效投标（响应）处理。

所以：

\[
\boxed{
TriggerHit
+
InsufficientExplanation
\Rightarrow
InvalidResponse
}
\]

**中文业务释义：** 命中异常低价审查 + 无法通过书面说明和证明材料证明报价合理 ⇒ 评审委员会按无效投标 / 响应处理。

---

# 四十五、异常低价审查不是只看供应商自己提交的材料

评审委员会还可以参考：

```text
similar_project_award_prices
# 中文：同类项目中标 / 成交价格

similar_product_market_prices
# 中文：类似产品市场价格水平

industry_labor_cost_standard
# 中文：行业人工费用标准

industry_average_cost
# 中文：国家有关部门指导行业协会发布的行业平均成本

historical_contract_data
# 中文：采购人 / 同类项目历史合同价格和履约数据
```

因此：

\[
\boxed{
SupplierExplanation
+
ExternalMarketEvidence
\rightarrow
PriceReasonablenessJudgment
}
\]

**中文业务释义：** 供应商解释材料 + 外部市场 / 行业证据 → 评审委员会形成报价合理性判断。

---

# 四十六、互联网查询记录也要归档

财库〔2026〕2号明确要求：

> 异常低价审查的启动原因、审查意见和结果应记录在评审报告中；供应商说明和证明材料，以及评审委员会有关互联网浏览、查询历史，应当一并归档。

因此：

```text
trigger_reason
# 中文：为什么启动异常低价审查

committee_opinion
# 中文：评审委员会审查意见

review_result
# 中文：报价合理 / 无法证明合理等最终结果

supplier_explanation_refs
# 中文：供应商书面说明及证明材料引用

internet_query_history
# 中文：评审委员会现场互联网查询历史

market_evidence_refs
# 中文：外部市场 / 行业证据引用

archive_status
# 中文：是否已经完整归档
```

---

# 四十七、核心心智模型 ⑫
# `LowPriceDecision` 必须可审计

\[
\boxed{
LowPriceReview
=
TriggerEvidence
+
SupplierEvidence
+
MarketEvidence
+
CommitteeReason
+
Archive
}
\]

**中文业务释义：** 异常低价审查 = 触发依据 + 供应商证据 + 市场证据 + 评审委员会理由 + 完整归档。

---

# 四十八、异常低价中标后还没结束

财库〔2026〕2号进一步要求：

> 对触发异常低价审查后仍中标 / 成交的供应商，采购人应重点关注其履约承诺和实际履约情况。

因此：

\[
\boxed{
LowPriceReviewPassed
\neq
RiskClosed
}
\]

**中文业务释义：** 异常低价审查通过 ≠ 后续履约风险已经关闭；中标后仍需加强履约、验收、分期考核和责任追踪。

---

# 四十九、Lifecycle Cost
## 全生命周期成本

财库〔2026〕2号允许采购人针对相关项目引入全生命周期成本理念，例如：

```text
initial_purchase_price
# 中文：初始采购价格

operation_cost
# 中文：运行费用

maintenance_cost
# 中文：维护费用

upgrade_cost
# 中文：升级费用

special_consumables_cost
# 中文：专用耗材费用

disposal_cost
# 中文：报废处置费用
```

所以：

\[
\boxed{
LowestInitialPrice
\neq
LowestLifecycleCost
}
\]

**中文业务释义：** 最低初始报价 ≠ 全生命周期总成本最低。

这对：

> 信息化建设、打印复印、实验、医疗等后续耗材和服务成本较大的项目，

尤其重要。

---

# 五十、核心心智模型 ⑬
# 异常低价治理不能只在“评标现场”做

正确闭环：

\[
\boxed{
DemandDesign
\rightarrow
PriceCeiling
\rightarrow
Quotation
\rightarrow
LowPriceReview
\rightarrow
Contract
\rightarrow
Acceptance
\rightarrow
PerformanceData
}
\]

**中文业务释义：** 采购需求设计 → 合理最高限价 → 供应商报价 → 异常低价审查 → 合同约束 → 履约验收 → 形成新的履约和成本数据。

---

# 五十一、2026 年 10 月 1 日将出现一个重要规则切换：紧急采购

财库〔2026〕12号《紧急采购管理暂行办法》已经发布：

```text
publication_date = 2026-09-07
# 中文：文件印发日期

effective_date = 2026-10-01
# 中文：正式施行日期

current_stage_date = 2026-09-20
# 中文：本课程当前校对时点
```

因此当前状态应是：

```text
PUBLISHED_NOT_EFFECTIVE
# 中文：已经发布，但尚未生效
```

所以：

\[
\boxed{
FutureEffectiveRule
\neq
CurrentApplicableRule
}
\]

**中文业务释义：** 将来确定生效的规则 ≠ 当前项目已经可以适用的规则。

---

# 五十二、为什么这个未来规则值得现在进入 Policy Registry？

因为从 2026 年 10 月 1 日起，符合该办法定义的紧急采购将有专门规则，例如：

```text
emergency_procurement_trigger
# 中文：严重自然灾害等突发事件、紧急国防外交等不可抗力事件，现有储备和紧急调拨 / 支援仍无法满足应急需要

competitive_methods_preferred
# 中文：原则上以竞争性谈判、竞争性磋商、询价等竞争性采购方式为主

direct_purchase_if_extreme
# 中文：时间极为紧迫、市场供给渠道受限，竞争性方式无法满足需要时，可以直接采购

simplified_supplier_count
# 中文：竞争性紧急采购中，只有两家甚至一家供应商符合要求时，在满足条件下可以继续采购活动

alternative_method_without_finance_approval
# 中文：达到公开招标数额标准的紧急采购项目拟采用其他采购方式时，可由采购人自行确定，无须按普通规则取得相应财政批准

emergency_additional_purchase_ratio
# 中文：符合办法规定的紧急情况下，从原供应商添购 / 追加原则上可达到原合同金额30%
```

注意：

> 上述规则在 2026 年 9 月 20 日尚未生效。

---

# 五十三、核心心智模型 ⑭
# `EmergencyRule` 不能提前适用

\[
\boxed{
EventDate
<
2026\text{-}10\text{-}01
\Rightarrow
DoNotApplyCaiKu2026No12AsEffectiveRule
}
\]

**中文业务释义：** 对 2026 年 10 月 1 日以前发生、需要判断适用规则的项目，不能把财库〔2026〕12号当作已经生效的现行规则。

这就是 Stage 2 的 Temporal Reasoning 在真实业务里的价值。

---

# 五十四、采购方式与竞争分析的统一状态机

建议：

```text
METHOD_NOT_CHECKED
# 中文：尚未检查采购方式

THRESHOLD_RESOLVED
# 中文：已确定当前项目适用数额标准

METHOD_CONDITION_CONFIRMED
# 中文：采购方式适用条件已确认

METHOD_CONDITION_UNCLEAR
# 中文：采购方式理由 / 事实不足

APPROVAL_REQUIRED
# 中文：需要取得审批

APPROVAL_CONFIRMED
# 中文：审批文件已经确认

COMPETITION_SUFFICIENT
# 中文：竞争充分性检查通过

COMPETITION_WEAK
# 中文：竞争偏弱，需要根因分析

SINGLE_SOURCE_CANDIDATE
# 中文：可能符合单一来源，需要进一步验证唯一性及程序

ABNORMAL_LOW_PRICE_TRIGGERED
# 中文：触发异常低价审查

LOW_PRICE_EXPLANATION_PENDING
# 中文：等待供应商解释和证明

LOW_PRICE_REASONABLE
# 中文：供应商已证明报价合理

LOW_PRICE_UNPROVEN
# 中文：无法证明报价合理

HUMAN_REVIEW_REQUIRED
# 中文：高影响 / 边界案件转人工复核
```

---

# 五十五、Competition Finding
## 竞争与采购方式合规发现项

一个完整 Finding 至少：

```text
finding_id
# 中文：竞争合规发现项标识

review_domain
# 中文：审查域，这里固定为COMPETITION竞争与采购方式

project_id
# 中文：采购项目标识

document_id
# 中文：采购文件标识

procurement_method
# 中文：实际采用的采购方式

method_reason
# 中文：采购人选择该方式的理由

threshold_rule_id
# 中文：当前适用数额标准规则标识

public_tender_threshold
# 中文：当前适用公开招标数额标准

above_public_tender_threshold
# 中文：项目是否达到公开招标数额标准

method_condition_status
# 中文：采购方式法定适用条件是否成立

approval_status
# 中文：应有审批是否完整

supplier_count_by_stage
# 中文：竞争漏斗各阶段供应商数量

competition_loss_stage
# 中文：供应商大量流失发生在哪个业务阶段

single_source_basis
# 中文：单一来源适用依据

unique_supplier_evidence
# 中文：唯一供应商市场证据

publicity_status
# 中文：需要公示时是否依法公示

discrimination_crosscheck
# 中文：是否联动检查D01-D22对竞争的限制

abnormal_low_price_status
# 中文：异常低价审查状态

legal_basis_refs
# 中文：适用法律政策依据

policy_snapshot_id
# 中文：项目时点法规快照

evidence_span
# 中文：采购文件 / 审批 / 论证等证据定位

risk_level
# 中文：竞争合规风险等级

human_review_required
# 中文：是否需要人工复核

recommended_action
# 中文：建议补充论证、重新选择方式、重新采购、启动低价审查等处理建议
```

---

# 五十六、Abnormal Low Price Review Schema
## 异常低价审查 Schema 第一版

```text
low_price_review_id
# 中文：异常低价审查记录标识

project_id
# 中文：采购项目标识

supplier_id
# 中文：供应商标识

bid_response_price
# 中文：供应商原始投标 / 响应报价

passed_conformity_prices
# 中文：全部通过符合性审查供应商报价集合

average_valid_price
# 中文：有效报价平均值

second_lowest_price
# 中文：次低有效报价

price_ceiling
# 中文：项目最高限价；未设置时按当前规则解析采购预算

average_trigger_rate
# 中文：平均报价触发比例

second_low_trigger_rate
# 中文：次低报价触发比例

ceiling_trigger_rate
# 中文：最高限价触发比例

trigger_1
# 中文：是否命中“低于平均有效报价一定比例”

trigger_2
# 中文：是否命中“低于次低报价一定比例”

trigger_3
# 中文：是否命中“低于最高限价一定比例”

trigger_4_professional_judgment
# 中文：评审委员会是否基于专业判断启动审查

triggered
# 中文：是否最终启动异常低价审查

explanation_requested
# 中文：是否要求供应商解释

explanation_minutes
# 中文：给予供应商解释的实际时间

supplier_explanation_refs
# 中文：供应商书面说明和证明材料

cost_breakdown
# 中文：原材料、人工、制造、服务等成本测算

market_evidence_refs
# 中文：同类项目、类似产品、行业成本等外部证据

committee_reasoning
# 中文：评审委员会报价合理性判断理由

review_result
# 中文：报价合理 / 无法证明合理 / 其他状态

invalid_response
# 中文：是否因无法证明报价合理而作无效响应处理

internet_query_history
# 中文：评审委员会互联网查询历史

report_recorded
# 中文：是否记录进评审报告

archive_complete
# 中文：是否完整归档

post_award_monitoring
# 中文：中标后是否纳入重点履约跟踪
```

---

# 五十七、确定性规则必须交给 Calculator

前三项异常低价数值规则属于：

# Deterministic Rule
## 确定性规则

所以：

\[
\boxed{
NumericLowPriceTrigger
\Rightarrow
CalculatorFirst
}
\]

**中文业务释义：** 明确的异常低价数值触发，应由确定性规则 / 计算器计算，不应让 LLM 凭感觉心算。

而第四项：

```text
professional_judgment_trigger
# 中文：评审委员会认为报价过低、可能影响质量或诚信履约
```

更适合：

```text
Rule    # 中文：确定性规则
+
MarketEvidence    # 中文：市场 / 行业外部证据
+
LLMAssist    # 中文：大语言模型辅助分析
+
HumanCommittee    # 中文：评审委员会最终专业判断
```

协同处理。

---

# 五十八、核心心智模型 ⑮
# `Calculator` 决定“有没有命中数值条件”，不是决定“最终报价是否合理”

\[
\boxed{
TriggerCalculator
\neq
FinalPriceReasonablenessDecision
}
\]

**中文业务释义：** 计算器负责判定数值阈值是否命中 ≠ 它替代评审委员会完成最终报价合理性判断。

---

# 五十九、Hard Negative
## 竞争与低价域高难负例

必须包含：

```text
HardNegative_LowButReasonable
# 中文：报价非常低，但供应商有可验证成本优势并能证明履约可持续

HardNegative_LimitedButCompetitiveMarket
# 中文：供应商数量少，但确属专业细分市场且采购条件中立

HardNegative_LawfulSingleSource
# 中文：唯一供应商证据充分、法定条件和程序均成立

HardNegative_ApprovedTwoSupplierNegotiation
# 中文：公开招标失败后符合法定条件并经批准，两家供应商转竞争性谈判

HardNegative_ConsultationTwoSupplierException
# 中文：竞争性磋商符合法定两家供应商例外

HardNegative_FutureEmergencyRule
# 中文：2026年10月1日后的项目正确适用紧急采购新规；此前项目不得提前套用
```

---

# 六十、Counterfactual Pair
## 竞争域反事实样本

### Pair A：一家响应 vs 唯一供应商

```text
公开招标只有一家供应商提交投标文件，所以转为单一来源
# 中文：仅凭程序中实际参与数量推导市场唯一
```

### Pair B

```text
重新开展市场调查，验证替代供应商、替代技术、兼容性和市场供给；只有唯一供应商条件及程序均成立后，才进入单一来源
# 中文：用市场证据证明唯一性
```

比较：

```text
ObservedCompetition
# 中文：当前采购活动观察到的竞争结果

MarketUniqueness
# 中文：客观市场唯一性
```

---

### Pair C：低价自动废标

```text
报价低于平均价50%，直接作无效投标
# 中文：把触发规则误当最终结论
```

### Pair D

```text
报价触发数值条件后启动异常低价审查，要求供应商提交成本测算和证明材料，再由评审委员会形成结论
# 中文：正确的“触发—解释—证据—审查”流程
```

比较：

```text
TriggerHit
# 中文：触发审查

InvalidBid
# 中文：无效投标 / 响应结论
```

---

### Pair E：人为制造紧急

```text
采购计划延误导致时间不足，因此直接认定紧急采购 / 紧急谈判
# 中文：采购人自身拖延造成的紧迫
```

### Pair F

```text
核查紧急事件来源、发生时点、是否可预见、现有储备和替代资源是否不足，再按项目时点适用当时生效的紧急采购规则
# 中文：基于事实和时点解析紧急采购
```

---

# 六十一、Competition Benchmark
## 竞争合规 Benchmark 应该测什么？

至少：

```text
procurement_method_classification_accuracy
# 中文：采购方式识别准确率

threshold_resolution_accuracy
# 中文：公开招标数额标准解析准确率

method_applicability_accuracy
# 中文：采购方式适用条件判断准确率

approval_requirement_accuracy
# 中文：审批要求判断准确率

tender_evasion_detection_recall
# 中文：化整为零规避公开招标风险召回率

competition_funnel_accuracy
# 中文：供应商竞争漏斗各阶段识别准确率

competition_root_cause_accuracy
# 中文：竞争不足根因分析准确率

single_source_uniqueness_precision
# 中文：唯一供应商认定精确率

single_source_publicity_accuracy
# 中文：单一来源公示程序判断准确率

additional_purchase_10_percent_accuracy
# 中文：原供应商添购10%规则计算准确率

minimum_supplier_exception_accuracy
# 中文：不同采购方式供应商数量例外判断准确率

low_price_trigger_1_accuracy
# 中文：平均有效报价触发条件计算准确率

low_price_trigger_2_accuracy
# 中文：次低报价触发条件计算准确率

low_price_trigger_3_accuracy
# 中文：最高限价触发条件计算准确率

low_price_boundary_accuracy
# 中文：等于阈值、不触发等边界条件准确率

low_price_explanation_workflow_accuracy
# 中文：异常低价解释举证流程判断准确率

low_price_invalidity_accuracy
# 中文：无法证明报价合理时无效响应判断准确率

price_field_separation_accuracy
# 中文：原始报价、政策评审价格、合同价格字段区分准确率

future_rule_temporal_accuracy
# 中文：财库〔2026〕12号等未来生效规则时点判断准确率

hard_negative_precision
# 中文：合法单一来源、合理低价、供应商数量例外等不被误报的精确率

human_escalation_accuracy
# 中文：边界型竞争问题转人工准确率
```

---

# 六十二、核心心智模型 ⑯
# `OverallCompetitionAccuracy` 不等于 `MethodAndPriceReliability`

\[
\boxed{
OverallCompetitionAccuracy
\neq
CriticalSliceReliability
}
\]

**中文业务释义：** 竞争合规总体准确率 ≠ 对单一来源、供应商数量例外、异常低价边界、紧急采购时点等关键风险切片都可靠。

---

# 六十三、`ProcurementCompetitionCompliance_V1` 建议目录

```text
ProcurementCompetitionCompliance_V1/
# 中文：采购方式、竞争充分性和异常低价合规工程资产根目录

├── method/
│   # 中文：采购方式适用规则
│   ├── public_tender/    # 中文：公开招标规则
│   ├── invited_tender/    # 中文：邀请招标规则
│   ├── competitive_negotiation/    # 中文：竞争性谈判规则
│   ├── competitive_consultation/    # 中文：竞争性磋商规则
│   ├── single_source/    # 中文：单一来源规则
│   └── inquiry/    # 中文：询价规则
│
├── threshold/
│   # 中文：采购限额、公开招标数额标准、地区和时点解析
│   ├── resolver/    # 中文：数额标准解析器
│   └── snapshots/    # 中文：各地区各时点数额标准快照
│
├── competition/
│   # 中文：竞争充分性分析
│   ├── supplier_funnel/    # 中文：供应商竞争漏斗分析
│   ├── root_cause/    # 中文：竞争不足根因分析
│   ├── discrimination_crosscheck/    # 中文：D01-D22差别歧视交叉检查
│   └── market_uniqueness/    # 中文：市场唯一供应商证据分析
│
├── abnormal_low_price/
│   # 中文：财库〔2026〕2号异常低价审查
│   ├── trigger_calculator/    # 中文：异常低价数值触发计算器
│   ├── explanation/    # 中文：供应商解释与举证模块
│   ├── market_evidence/    # 中文：市场价格与行业成本证据
│   ├── committee_review/    # 中文：评审委员会专业审查
│   └── post_award_monitoring/    # 中文：中标后重点履约跟踪
│
├── temporal/
│   # 中文：未来生效 / 历史规则解析
│   └── emergency_procurement_2026_12/    # 中文：财库〔2026〕12号紧急采购时点规则
│
├── schema/    # 中文：结构化数据契约与发现项Schema
│   ├── procurement_method.json
│   # 中文：采购方式结构
│   ├── competition_funnel.json
│   # 中文：竞争漏斗结构
│   ├── single_source_evidence.json
│   # 中文：单一来源唯一性证据结构
│   ├── abnormal_low_price_review.json
│   # 中文：异常低价审查结构
│   └── competition_finding.json
│       # 中文：竞争合规发现项结构
│
├── tests/
│   ├── positive/    # 中文：明确风险正例
│   # 中文：明确风险正例
│   ├── hard_negative/    # 中文：合法采购方式 / 合理低价高难负例
│   # 中文：合法采购方式 / 合理低价高难负例
│   ├── boundary/    # 中文：50%、45%、65%、10%等边界测试
│   # 中文：50%、45%、65%、10%等边界案例
│   ├── temporal/    # 中文：生效时间 / 历史规则测试
│   # 中文：规则生效时点案例
│   └── cross_domain/    # 中文：资格、技术、政策、竞争、履约跨域测试
│       # 中文：D01-D22、政策优惠、价格、履约跨域案例
│
└── manifest.json
    # 中文：版本、法源、依赖、测试和生效时点清单
```

---

# 六十四、本阶段最重要的 20 个核心心智模型

> **心智模型 ①：`ProcurementOrganization ≠ ProcurementMethod ≠ EvaluationMethod`。集中 / 分散采购、采购方式、评审方法是三套不同维度。**

> **心智模型 ②：`PublicTenderThreshold ≠ OneNationalConstant`。公开招标数额标准必须按预算级次、地区、采购对象和时点解析。**

> **心智模型 ③：`ReasonablePackageDesign ≠ TenderEvasion`。合理拆包和化整为零规避公开招标必须区分。**

> **心智模型 ④：`ObservedOneSupplier ≠ OnlyOneSupplierExists`。只有一家来投不等于市场唯一供应商。**

> **心智模型 ⑤：`FailedTender + OneSupplier ≠ AutomaticSingleSource`。招标失败不能自动转单一来源。**

> **心智模型 ⑥：`PatentExists ≠ OnlyOneSupplier`。专利、专有技术不自动等于市场唯一。**

> **心智模型 ⑦：`SingleSourceCompliance = SubstantiveCondition + RequiredProcedure`。单一来源既要条件成立，也要程序正确。**

> **心智模型 ⑧：`SupplierCount ≠ MarketUniqueness`。供应商数量是程序事实，不是市场结论。**

> **心智模型 ⑨：`MinimumSupplierCount = MethodSpecificRule + ExceptionRule`。最低供应商数量必须按采购方式和例外分别解析。**

> **心智模型 ⑩：`LowPrice ≠ AbnormallyLowPrice`。低价不是异常低价的自动结论。**

> **心智模型 ⑪：`ThresholdHit ≠ InvalidBid`。命中异常低价阈值只是启动审查，不是直接废标。**

> **心智模型 ⑫：`ConfiguredTriggerRate ≠ ModelChosenRate`。项目实际触发比例必须来自采购文件和当前有效规则。**

> **心智模型 ⑬：`PolicyEvaluationPrice ≠ AbnormalLowPriceTriggerPrice`。政策优惠后的评审价格与异常低价触发报价必须分字段。**

> **心智模型 ⑭：`Cheap ≠ Unsustainable`。供应商可能有真实低成本优势，但必须能够解释并举证。**

> **心智模型 ⑮：`LowPriceReviewPassed ≠ RiskClosed`。异常低价审查通过后，中标履约仍需重点跟踪。**

> **心智模型 ⑯：`LowestInitialPrice ≠ LowestLifecycleCost`。低初始价格不等于全生命周期成本最低。**

> **心智模型 ⑰：`TriggerCalculator ≠ FinalPriceReasonablenessDecision`。计算器负责数值触发，不替代评审委员会最终判断。**

> **心智模型 ⑱：`FutureEffectiveRule ≠ CurrentApplicableRule`。已经发布但未来生效的新规不能提前适用。**

> **心智模型 ⑲：`LowCompetition → DiscriminationRuleCrossCheck`。竞争度异常偏低时要回查 D01-D22 是否人为压缩竞争。**

> **心智模型 ⑳：`CompetitionCompliance = MethodLegality + RealCompetition + PriceReasonableness + Auditability`。竞争合规不仅看采购方式名称，还要看真实竞争、价格合理性和完整审计链。**

---

# 六十五、把整个采购方式、竞争与异常低价压成一张工程图

```text
Project Facts
# 中文：预算级次、地区、采购对象、金额、项目时点、需求特征
↓
Threshold Resolver
# 中文：解析采购限额和公开招标数额标准
↓
Method Candidate
# 中文：公开招标 / 邀请招标 / 谈判 / 磋商 / 单一来源 / 询价等候选方式
↓
Statutory Condition + Approval
# 中文：法定适用条件和必要审批
↓
Competition Funnel
# 中文：潜在市场→知悉→获取文件→响应→资格→符合性→有效报价→候选
↓
Competition Root Cause
# 中文：竞争不足时分析市场、资格、技术、评分、公告、时限、采购包等原因
↓
D01-D22 Cross-check
# 中文：检查采购文件是否人为限制公平竞争
↓
Single Source / Supplier Count Exception Resolver
# 中文：如涉及单一来源或两家供应商例外，解析实体条件和程序
↓
Valid Prices
# 中文：进入有效报价集合
↓
Abnormal Low Price Calculator
# 中文：计算平均价50%、次低价50%、最高限价45%及项目配置阈值
↓
Trigger?
# 中文：是否命中数值条件或专业判断条件
↓
Supplier Explanation + Cost Evidence
# 中文：供应商解释和成本证明
↓
Market Evidence + Committee Review
# 中文：外部市场证据和评审委员会专业审查
↓
Price Reasonableness Decision
# 中文：报价合理 / 无法证明合理
↓
Contract + Post-award Monitoring
# 中文：合同履约、验收、分期考核和重点跟踪
↓
Audit Trace + Benchmark
# 中文：采购方式、竞争、低价审查全链路审计与评测
```

---

# 六十六、脑中最后只留一句

> **政府采购竞争合规的本质，不是“供应商越多越好”，也不是“价格越低越好”，更不是“只有一家来就能做单一来源”；它要求先按项目金额、地区、采购对象和时点选对采购方式，再确认竞争不足到底源于真实市场结构还是采购文件人为限制，并对异常低价按照确定性阈值启动审查、要求供应商解释举证、结合市场证据由评审委员会形成可审计结论，最后把高风险低价继续带入合同履约和验收闭环。**

---

# 第十一课 · 第 9 阶段掌握测试

现在不回看正文，你应该能够解释：

```text
Procurement Organization、Procurement Method、Evaluation Method 为什么不能混？
# 中文：采购组织形式、采购方式、评审方法分别解决什么问题？

为什么 Public Tender Threshold 不能写死成全国一个数字？
# 中文：预算级次、地区、货物服务工程、项目时点怎样决定数额标准？

Reasonable Package Design 和 Tender Evasion 有什么区别？
# 中文：合理拆包和化整为零规避公开招标怎样区分？

竞争性谈判、竞争性磋商、询价分别适合什么项目？
# 中文：为什么这些方式不能因为“方便”就随便选？

Observed One Supplier 为什么不等于 Only One Supplier Exists？
# 中文：一家来投和市场客观唯一的区别是什么？

公开招标只有一家响应为什么不能自动转单一来源？
# 中文：为什么必须重新做市场唯一性证据？

Patent Exists 为什么不等于 Only One Supplier？
# 中文：专利、授权、替代技术、等效方案怎样影响唯一性判断？

单一来源第三类“原供应商添购”为什么同时需要一致性 / 配套需要和10%金额上限？
# 中文：为什么满足10%仍然不是自动单一来源？

单一来源为什么既要 Substantive Condition 又要 Required Procedure？
# 中文：公示、审批、论证为什么是独立的一层？

什么是 Competition Funnel？
# 中文：潜在市场到最终有效报价的供应商为什么要分阶段计数？

竞争不足为什么必须 Cross-check D01-D22？
# 中文：如何判断是市场真的小，还是采购文件把供应商挡掉了？

为什么 Minimum Supplier Count 不能全局写成3家？
# 中文：谈判、磋商等方式有哪些不同的法定例外？

财库〔2026〕2号什么时候生效？
# 中文：为什么异常低价规则必须按2026年2月1日这个时点解析？

异常低价三个确定性数值触发条件分别是什么？
# 中文：平均有效报价、次低报价、最高限价三条规则怎样计算？

为什么项目没有最高限价时要看采购预算？
# 中文：最高限价字段怎样解析？

采购人把50% / 45%提高到其他比例时，为什么必须读采购文件？
# 中文：为什么模型不能自己选择阈值？

为什么“等于阈值”与“低于阈值”是重要边界案例？
# 中文：公式里的严格小于号怎样影响自动化判断？

Policy Evaluation Price 为什么不能用于异常低价触发？
# 中文：政策评审价格与供应商原始报价为什么必须分字段？

Threshold Hit 为什么不等于 Invalid Bid？
# 中文：异常低价触发以后为什么还必须解释、举证和委员会审查？

供应商一般至少要获得多少解释时间？
# 中文：财库〔2026〕2号为什么强调合理时间一般不少于30分钟？

供应商不能证明报价合理时怎样处理？
# 中文：什么时候异常低价候选最终进入无效投标 / 响应结论？

为什么互联网查询历史也需要归档？
# 中文：异常低价审查怎样做到可审计？

为什么 Low Price Review Passed 不等于 Risk Closed？
# 中文：异常低价供应商中标后为什么要重点履约跟踪？

什么是 Lifecycle Cost？
# 中文：为什么初始采购价格低不等于项目全生命周期成本低？

截至2026年9月20日，财库〔2026〕12号是什么状态？
# 中文：为什么已经发布的紧急采购新规还不能当成当前生效规则使用？

为什么未来生效规则也应该提前进入 Policy Registry？
# 中文：系统怎样在2026年10月1日自动切换到正确规则版本？

Calculator 和评审委员会在异常低价审查里分别做什么？
# 中文：哪些是确定性计算，哪些仍然需要专业判断？
```

如果这些能够完整解释：

\[
\boxed{
第十一课第9阶段真正掌握
}
\]

**中文业务释义：** 如果能够把采购方式合法性、竞争充分性、单一来源、供应商数量例外、异常低价数值触发、供应商解释举证、评审委员会判断、履约跟踪和法规时点完整串起来，就说明真正掌握了本阶段。

---

# 下一阶段：第十一课 · 第 10 阶段
# 采购文件数据工程：PDF、Word、表格、OCR、章节树、Clause ID 与 Evidence Span
## 怎样把真实采购文件变成可可靠计算、可定位、可追溯的结构化事实？

下一阶段将正式建立：

# `ProcurementComplianceDataset_V1`

最重要的边界：

\[
\boxed{
ParsedText
\neq
ReliableComplianceFact
}
\]

**中文业务释义：** 从 PDF / Word 中成功提取出文本 ≠ 已经得到可以直接用于合规判断的可靠业务事实；还必须恢复版本、章节、表格、条款边界、业务角色、交叉引用和原文证据定位。
