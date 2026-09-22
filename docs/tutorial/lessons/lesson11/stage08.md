# 第十一课 · 第 8 阶段
# 政府采购政策合规：本国产品、中小企业、绿色采购、创新、进口产品
## 怎样区分“国家政策明确允许的支持、优惠、预留、强制采购和特殊程序”与“采购人自行设置的不合理差别待遇”？怎样让 AI 正确计算政策优惠，又不把合法政策误报成歧视？

第 7 阶段我们已经建立：

\[
\boxed{
Scorable
\neq
CompliantScoringFactor
}
\]

**中文业务释义：** 一个条件能够被设计成“打分”，不代表它当然适合作为政府采购合规评分因素。

并且把评分标准恢复成：

\[
\boxed{
ProcurementNeed
\rightarrow
ScoringFactor
\rightarrow
SupplierEvidence
\rightarrow
ContractCommitment
}
\]

**中文业务释义：** 采购需求 → 评分因素 → 供应商证明材料 → 中标后的合同履约承诺。

现在进入一个特别容易被合规模型误判的领域：

# Government Procurement Policy
## 政府采购政策功能

政府采购并不只有：

> “所有供应商完全一样处理”

这一种机制。

在法律政策明确规定的条件下，政府采购可能合法实施：

```text
reserved_procurement    # 中文：专门面向特定政策对象预留采购份额

price_preference    # 中文：依法给予价格评审优惠 / 价格扣除

priority_procurement    # 中文：政府优先采购

mandatory_procurement    # 中文：政府强制采购

special_procurement_method    # 中文：依法采用特定采购方式，例如合作创新采购

import_approval    # 中文：采购进口产品前履行审核管理程序
```

因此，本阶段第一条、也是最重要的边界正式锁定为：

\[
\boxed{
PolicyPreference
\neq
IllegalDiscrimination
}
\]

**中文业务释义：** 有明确法律政策依据的政府采购支持、优惠、预留、强制采购或特殊程序 ≠ 采购人自行设置的违法违规差别歧视待遇。

本阶段最终形成：

# `ProcurementPolicyCompliance_V1`

---

# 一、本阶段为什么特别重要？

前面 D01～D22 训练我们识别：

```text
地域限制    # 中文：不合理限制外地供应商

行业限制    # 中文：不合理限定供应商行业身份

企业规模限制    # 中文：用规模、财务、成立年限等形成门槛

品牌 / 产品指向    # 中文：技术要求不合理锁定特定供应商或产品

证书奖项限制    # 中文：把缺乏依据的证书奖项设置成资格或评分条件
```

但政府采购政策本身又可能：

```text
支持中小企业    # 中文：依法预留份额、价格评审优惠等

支持本国产品    # 中文：依法按本国产品标准给予价格评审优惠

实施绿色采购    # 中文：依法优先或强制采购符合要求的节能环保产品

支持科技创新    # 中文：在符合条件的项目中依法采用合作创新采购

管理进口产品    # 中文：确需采购进口产品时依法履行审核程序
```

如果模型只学会：

> “区别对待 = 违规”，

就会出现严重误报。

所以：

\[
\boxed{
DifferenceInTreatment
\neq
UnlawfulDiscrimination
}
\]

**中文业务释义：** 存在不同处理方式 ≠ 当然构成违法违规差别待遇；关键要判断这种差异是否来自有效、适用且执行正确的政府采购政策。

---

# 二、核心心智模型 ①
# `PolicySupport` 必须回答四件事

任何政府采购政策优惠，至少必须回答：

\[
\boxed{
PolicySupport
=
Authority
+
Applicability
+
Mechanism
+
Evidence
}
\]

**中文业务释义：** 政策支持 = 有效政策依据 + 当前项目是否适用 + 政策具体怎样执行 + 供应商 / 产品如何证明满足条件。

四层分别解决：

```text
Authority    # 中文：政策是谁制定、当前是否有效

Applicability    # 中文：项目类型、金额、采购标的、时点、地区、供应商 / 产品状态是否满足适用条件

Mechanism    # 中文：是预留份额、价格扣除、优先采购、强制采购还是特殊采购程序

Evidence    # 中文：声明函、认证证书、审核文件、合同分包承诺等证据是否完整
```

---

# 三、政策执行不能写死在 Prompt 里

如果把当前政策简单写成：

```text
“中小企业优惠20%”
“本国产品优惠20%”
“节能产品必须采购”
```

直接塞进 System Prompt，

存在几个重大问题：

```text
适用范围可能不同    # 中文：货物、服务、工程的规则可能不同

政策时点可能变化    # 中文：同一比例在不同年份可能变化

项目条件可能不同    # 中文：专门面向中小企业与非预留项目执行方式不同

例外可能不同    # 中文：国际条约、进口产品、特殊项目等存在特别规则

优惠可能叠加    # 中文：不同政策在满足条件时可能同时生效

证明材料可能不同    # 中文：声明函、认证证书、审批文件要求不同
```

所以：

\[
\boxed{
PolicyRule
\neq
PromptMemory
}
\]

**中文业务释义：** 政府采购政策规则 ≠ 让大语言模型“背住”的 Prompt 记忆；它必须进入可版本化、可计算、可追溯的 Policy Registry 和 Policy Engine。

---

# 四、截至 2026 年 9 月的本阶段核心政策快照

本阶段当前至少连接：

```text
国办发〔2025〕34号
# 中文：《国务院办公厅关于在政府采购中实施本国产品标准及相关政策的通知》，自2026年1月1日起施行

财库〔2025〕30号
# 中文：财政部、工业和信息化部贯彻落实本国产品标准及相关政策的实施意见

财库〔2020〕46号
# 中文：《政府采购促进中小企业发展管理办法》

财库〔2022〕19号
# 中文：进一步加大政府采购支持中小企业力度，调整货物服务小微企业价格评审优惠幅度等

财库〔2019〕9号
# 中文：节能产品、环境标志产品政府采购执行机制，实行品目清单 + 有效认证证书管理

财库〔2022〕35号
# 中文：扩大政府采购支持绿色建材促进建筑品质提升政策实施范围

财库〔2024〕13号
# 中文：《政府采购合作创新采购方式管理暂行办法》，自2024年6月1日起施行

财库〔2007〕119号
# 中文：《政府采购进口产品管理办法》，规范确需采购进口产品时的审核管理
```

这里必须再次强调：

\[
\boxed{
PolicySnapshot
\neq
PermanentTruth
}
\]

**中文业务释义：** 2026 年当前政策快照 ≠ 永远不变的政策真理；生产系统必须在每个项目时点重新解析法规状态和适用范围。

---

# 五、本国产品政策：先分清“产品身份”和“企业身份”

2026 年政府采购本国产品政策最容易被误解成：

> “支持中国企业”。

但真正需要先建模的是：

# Product Status
## 产品属性

而不是：

# Supplier Ownership
## 供应商所有制 / 企业身份

所以：

\[
\boxed{
DomesticProduct
\neq
DomesticEnterprise
}
\]

**中文业务释义：** 本国产品 ≠ 内资企业产品；判断对象首先是“产品是否符合本国产品标准”，而不是供应商是不是国企、民企或外资企业。

国办发〔2025〕34号明确要求：

```text
state_owned_enterprise    # 中文：国有企业

private_enterprise    # 中文：民营企业

foreign_invested_enterprise    # 中文：外商投资企业
```

等各类经营主体：

> 平等享受符合条件的本国产品政府采购支持政策。

---

# 六、核心心智模型 ②
# `SupplierNationality` 和 `ProductDomesticStatus` 必须分层

系统至少拆成：

```text
supplier_ownership_type    # 中文：供应商所有制形式

supplier_investor_nationality    # 中文：投资者国别

manufacturer_identity    # 中文：实际生产企业

production_location    # 中文：产品生产地点

domestic_product_status    # 中文：是否符合本国产品标准
```

因此：

\[
\boxed{
ForeignInvestedEnterprise
+
DomesticProduct
\Rightarrow
EqualPolicyTreatment
}
\]

**中文业务释义：** 外商投资企业 + 其产品符合本国产品标准 ⇒ 依法平等享受本国产品支持政策。

这也与前面的 D09 / D10：

> 所有制、组织形式、股权结构、投资者国别不得被不合理用于限制供应商

形成直接连接。

---

# 七、本国产品标准到底怎么判断？

国办发〔2025〕34号建立的核心结构可以抽象为：

\[
\boxed{
DomesticProductStatus
=
DomesticProduction
+
ComponentCostRequirement
+
CriticalComponentProcessRequirement
}
\]

**中文业务释义：** 本国产品状态 = 在中国境内生产 + 中国境内生产组件成本占比达到要求 + 特定产品满足关键组件 / 关键工序要求。

其中：

# Domestic Production
## 在中国境内生产

核心是：

> 在中华人民共和国关境内实现从原材料、组件到产品的属性改变。

简单的：

```text
贴标签    # 中文：仅粘贴品牌 / 标识

简单包装    # 中文：只做包装展示

简单上漆    # 中文：没有形成新产品属性

简单分装    # 中文：只重新分装
```

不属于这种“属性改变”。

---

# 八、过渡期必须进入系统

国办发〔2025〕34号同时建立了渐进式标准体系：

```text
component_cost_ratio    # 中文：中国境内生产组件成本占比

critical_components    # 中文：特定产品的关键组件

critical_processes    # 中文：特定产品的关键工序
```

将分产品逐步制定。

在具体产品的组件成本占比、关键组件、关键工序要求实施前：

> 符合“在中国境内生产”条件的产品，在政府采购活动中视同本国产品。

因此：

\[
\boxed{
DomesticProductRule
=
ProductSpecificVersionedRule
}
\]

**中文业务释义：** 本国产品判断规则是分产品、分阶段、可版本化的规则，不应把未来全部标准提前写死。

---

# 九、核心心智模型 ③
# `CurrentDomesticRule` 必须按“产品 + 时点”解析

不能只问：

```text
项目日期是什么？    # 中文：采购活动发生时间
```

还要问：

```text
product_category    # 中文：产品属于哪个政府采购品目 / 产品类别

specific_component_rule_effective    # 中文：该产品的组件成本占比规则是否已经实施

critical_component_rule_effective    # 中文：关键组件要求是否已经实施

critical_process_rule_effective    # 中文：关键工序要求是否已经实施
```

所以：

\[
\boxed{
SameProduct
+
DifferentPolicyDate
=
PotentiallyDifferentDomesticTest
}
\]

**中文业务释义：** 同一种产品 + 不同政策时点 = 可能需要执行不同版本的本国产品判断标准。

---

# 十、本国产品 20% 价格评审优惠

2026 年起，对适用本国产品标准的政府采购活动：

> 当本国产品和非本国产品共同参与竞争时，依法对本国产品报价给予 20% 的价格扣除，用扣除后的价格参与评审。

工程上：

\[
\boxed{
DomesticEvaluationPrice
=
OriginalPrice
\times
(1-0.20)
}
\]

**中文业务释义：** 在政策适用并满足条件时，本国产品评审价格 = 原始报价 × 80%；注意这是“用于评审的价格调整”，不是让供应商把合同报价真正降价 20%。

因此：

\[
\boxed{
EvaluationPrice
\neq
ContractPrice
}
\]

**中文业务释义：** 政策性评审价格 ≠ 供应商最终合同成交价格。

---

# 十一、多产品采购包的 80% 规则

当一个采购项目 / 采购包含有多种产品时，

若：

> 供应商提供的符合本国产品标准的产品成本之和，占其提供的全部产品成本之和达到 80% 以上，

并满足政策要求，

可依法对其提供的全部产品总报价给予本国产品价格评审优惠。

可以工程化为：

\[
\boxed{
DomesticProductCostRatio
=
DomesticEligibleProductCost
/
AllProductCost
}
\]

**中文业务释义：** 本国产品成本占比 = 符合本国产品标准的产品成本之和 ÷ 供应商提供的全部产品成本之和。

以及：

\[
\boxed{
DomesticProductCostRatio
\geq
80\%
\Rightarrow
PackageLevelDomesticPreferenceCandidate
}
\]

**中文业务释义：** 当本国产品成本占比达到 80% 及以上时，可进入“采购包整体享受本国产品价格评审优惠”的政策适用候选判断；仍需检查声明 / 承诺等政策要求。

---

# 十二、本国产品声明函到底是什么？

系统要保存：

```text
domestic_product_declaration    # 中文：《关于符合本国产品标准的声明函》

manufacturer_name    # 中文：生产厂名称

manufacturer_address    # 中文：生产厂地址

production_location    # 中文：生产地点

component_cost_ratio    # 中文：中国境内生产组件成本占比，如当前产品已实施相应要求

critical_component_evidence    # 中文：关键组件要求证明，如当前产品已实施

critical_process_evidence    # 中文：关键工序要求证明，如当前产品已实施

declaration_integrity    # 中文：声明函是否完整

declaration_consistency    # 中文：声明函与响应文件其他内容是否一致
```

---

# 十三、核心心智模型 ④
# `PolicyEvidence` 不等于 `SupplierQualification`

财政部国库司公开答复明确指出：

> 本国产品声明函是产品享受本国产品支持政策的先决条件，但不应作为对供应商的资格条件。

因此：

\[
\boxed{
DomesticDeclaration
\neq
SupplierQualificationGate
}
\]

**中文业务释义：** 本国产品声明函 ≠ 供应商资格准入门槛；它解决的是“产品能否享受本国产品政策支持”，不是“供应商有没有资格参加采购”。

这条边界非常重要。

---

# 十四、`不接受进口产品` 也不等于 `全部是本国产品`

2026 年财政部国库司公开答复明确说明：

> 进口产品属于非本国产品；但某些“非进口产品”，如果不满足本国产品标准，同样可能属于非本国产品。

因此：

\[
\boxed{
NonImportedProduct
\neq
DomesticProduct
}
\]

**中文业务释义：** 非进口产品 ≠ 一定属于本国产品。

同时：

\[
\boxed{
ImportedProduct
\Rightarrow
NonDomesticProduct
}
\]

**中文业务释义：** 按现行本国产品政策口径，进口产品属于非本国产品。

这会直接影响：

```text
进口产品审核    # 中文：采购进口产品是否已依法履行审核程序

本国产品价格优惠    # 中文：是否符合本国产品支持政策

采购文件表述    # 中文：是否错误地把“非进口”直接等同于“本国产品”
```

---

# 十五、中小企业政策：先分清“支持谁”和“支持什么”

中小企业政策不能简单写成：

> “供应商是小企业就优惠”。

尤其货物项目中，需要继续看：

# Manufacturer
## 制造商

财政部政策问答明确：

> 货物采购项目中，货物由中小企业制造，才能按办法相关规则享受中小企业扶持政策；多采购标的情况下，需要按政策要求逐标的判断。

因此：

\[
\boxed{
SmallSupplier
\neq
AutomaticallySMEEligibleGoods
}
\]

**中文业务释义：** 投标供应商本身是小微企业 ≠ 其提供的所有货物就自动符合中小企业政策支持条件；货物项目需要关注实际制造企业及政策定义。

---

# 十六、中小企业支持机制不是只有“价格扣除”

`ProcurementPolicyCompliance_V1` 至少要识别：

```text
reserved_project    # 中文：项目整体专门面向中小企业

reserved_package    # 中文：设置采购包专门面向中小企业

joint_venture_requirement    # 中文：通过联合体落实中小企业合同份额

subcontract_requirement    # 中文：要求中标供应商向中小企业分包一定比例

price_deduction    # 中文：非预留项目 / 非预留采购包中的小微企业价格评审优惠

payment_support    # 中文：付款期限、预付款等支持措施

credit_guarantee    # 中文：政府采购信用担保

contract_financing    # 中文：政府采购合同融资
```

所以：

\[
\boxed{
SMEPolicy
\neq
PriceDiscountOnly
}
\]

**中文业务释义：** 中小企业政府采购政策 ≠ 只有价格扣除；还包括预留份额、采购包设计、联合体 / 分包、支付和融资支持等多种机制。

---

# 十七、中小企业预留份额

财库〔2020〕46号明确建立：

```text
goods_services_threshold = 200万元    # 中文：达到采购限额标准以上且200万元以下的货物、服务项目，适宜由中小企业提供的，原则上按政策专门面向中小企业采购

works_threshold = 400万元    # 中文：达到采购限额标准以上且400万元以下的工程项目，适宜由中小企业提供的，按政策专门面向中小企业采购

reserved_share_over_threshold >= 30%    # 中文：超过上述金额且适宜由中小企业提供的部分，按管理办法预留30%以上专门面向中小企业

micro_share_within_reserved >= 60%    # 中文：预留给小微企业的比例不低于预留份额的60%
```

但这里必须建立时间意识。

财库〔2022〕19号中：

> 对超过 400 万元工程项目，2022 年下半年曾阶段性把相关预留份额由 30% 提高到 40% 以上。

这个安排有明确阶段性时间。

所以：

\[
\boxed{
HistoricalTemporaryPolicy
\neq
CurrentPermanentRule
}
\]

**中文业务释义：** 历史阶段性政策 ≠ 当前永久适用规则；AI 绝不能因为训练语料里见过“40%”就直接套到 2026 年项目。

---

# 十八、小微企业价格评审优惠

截至当前，财库〔2022〕19号规定：

```text
goods_services_micro_price_deduction = 10% - 20%
# 中文：货物、服务采购项目对符合条件的小微企业价格评审优惠区间

joint_venture_or_subcontract_price_deduction = 4% - 6%
# 中文：符合政策条件的大中型企业与小微企业联合体或向小微企业分包时的评审优惠区间

works_policy
# 中文：政府采购工程价格评审优惠仍按财库〔2020〕46号相关规定执行
```

因此：

\[
\boxed{
SMEPricePreference
=
PolicyRange
+
ProjectSpecificRate
}
\]

**中文业务释义：** 小微企业价格评审优惠 = 政策允许区间 + 当前采购文件依法确定的具体优惠比例。

不能让模型自己“默认选 20%”。

---

# 十九、核心心智模型 ⑤
# `AllowedRange` 不等于 `AutomaticMaximum`

\[
\boxed{
PolicyRange
\neq
AlwaysUseUpperBound
}
\]

**中文业务释义：** 政策给出 10%～20% 的允许区间 ≠ 每个项目自动使用 20%；系统必须读取当前项目采购文件确定的合法具体比例。

---

# 二十、本国产品与小微企业优惠可以叠加吗？

财政部国库司当前公开答复已经给出一个非常重要的 2026 实务口径：

> 对非专门面向中小企业的项目，如果既有本国产品、也有非本国产品参与竞争，且符合本国产品政策的供应商同时满足小微企业政策条件，应分别落实本国产品和小微企业价格评审优惠；相关扣除均以供应商原始报价为基础计算。

因此：

\[
\boxed{
PolicyStacking
\neq
PolicyConflict
}
\]

**中文业务释义：** 多项政府采购政策同时适用 ≠ 政策冲突；有些政策可以依法叠加执行。

例如概念上：

\[
\boxed{
EvaluationPrice
=
OriginalPrice
-
DomesticDeduction
-
SMEDeduction
}
\]

**中文业务释义：** 在两项政策均适用且允许叠加时，评审价格 = 原始报价 − 本国产品政策扣除额 − 小微企业政策扣除额；每项扣除应按适用规则计算。

并且：

\[
\boxed{
DomesticDeduction
=
OriginalPrice
\times
DomesticRate
}
\]

**中文业务释义：** 本国产品扣除额 = 原始报价 × 本国产品适用扣除比例。

\[
\boxed{
SMEDeduction
=
OriginalPrice
\times
SMERate
}
\]

**中文业务释义：** 小微企业扣除额 = 原始报价 × 当前项目适用的小微企业扣除比例。

---

# 二十一、核心心智模型 ⑥
# `PolicyStacking` 必须由 Policy Resolver 计算

不能简单写：

```text
20% + 20% = 40%
# 中文：只看数字相加，而不检查两项政策是否都适用
```

系统必须先判断：

```text
domestic_policy_applicable    # 中文：本国产品政策是否适用

sme_policy_applicable    # 中文：中小企业价格评审优惠是否适用

reserved_project_status    # 中文：是否属于专门面向中小企业采购，避免误用价格扣除

product_status    # 中文：产品是否满足本国产品标准

sme_status    # 中文：供应商 / 制造商是否满足中小企业政策定义

project_specific_rate    # 中文：采购文件选择的合法具体优惠比例
```

所以：

\[
\boxed{
CalculateAfterApplicability
}
\]

**中文业务释义：** 必须先判断政策适用，再计算优惠；不能先做算术、后补政策理由。

---

# 二十二、绿色采购：先分清“强制采购”和“优先采购”

财库〔2019〕9号建立了：

# Category List Management
## 品目清单管理

核心机制：

```text
energy_saving_category_list    # 中文：节能产品政府采购品目清单

environmental_label_category_list    # 中文：环境标志产品政府采购品目清单

mandatory_procurement_flag    # 中文：是否属于强制采购类别

priority_procurement_flag    # 中文：是否属于优先采购类别

valid_certificate    # 中文：由国家确定的认证机构出具、且处于有效期内的认证证书
```

因此：

\[
\boxed{
GreenProcurement
\neq
GreenKeyword
}
\]

**中文业务释义：** 绿色采购 ≠ 看到“节能、环保、绿色”关键词就判断政策适用；需要解析品目清单、认证、标准和当前有效状态。

---

# 二十三、核心心智模型 ⑦
# `Mandatory` 和 `Priority` 必须严格区分

\[
\boxed{
MandatoryProcurement
\neq
PriorityProcurement
}
\]

**中文业务释义：** 强制采购 ≠ 优先采购；前者属于必须执行的采购约束，后者是在符合条件时依法给予优先待遇，两者不能混成一个状态。

系统至少记录：

```text
policy_strength    # 中文：政策强度，强制 / 优先 / 鼓励

category_list_version    # 中文：使用的是哪一版品目清单

certificate_status    # 中文：认证证书是否有效

certificate_issuer    # 中文：认证机构

standard_reference    # 中文：对应标准规范

effective_date    # 中文：政策 / 清单 / 证书适用时间
```

---

# 二十四、绿色政策不等于任意“绿色证书加分”

财库〔2019〕9号允许在政策框架内依法实施绿色采购。

但不能据此推出：

> “采购人可以随便指定一个绿色协会证书，然后加 10 分。”

所以：

\[
\boxed{
GreenPolicy
\neq
ArbitraryGreenCertificateBonus
}
\]

**中文业务释义：** 政府绿色采购政策 ≠ 可以任意指定绿色证书、奖项或认证机构作为加分条件。

这里必须回到：

```text
policy_basis    # 中文：有没有明确政策依据

category_scope    # 中文：采购产品是否属于适用品目

certificate_basis    # 中文：认证证书是否属于政策认可范围

issuer_basis    # 中文：出具机构是否符合政策要求

score_or_gate_role    # 中文：该证书被用作强制要求、优先待遇还是采购人自行加分
```

---

# 二十五、绿色建材政策为什么必须做“地域 + 项目类型”解析？

财库〔2022〕35号扩大了政府采购支持绿色建材促进建筑品质提升政策实施范围，并对纳入政策实施范围的政府采购工程建立了专门需求标准和全流程管理要求。

但系统不能把它误写成：

> “全国所有政府采购项目一律执行同一个绿色建材规则”。

因此：

\[
\boxed{
GreenBuildingPolicy
=
Jurisdiction
+
ProjectType
+
ImplementationScope
+
DemandStandard
}
\]

**中文业务释义：** 绿色建筑 / 绿色建材政策适用 = 地区 + 工程项目类型 + 政策实施范围 + 对应采购需求标准。

---

# 二十六、核心心智模型 ⑧
# `NationalPolicy` 也可能有 `ScopedImplementation`

\[
\boxed{
PolicyPublishedNationally
\neq
EveryProjectSameExecution
}
\]

**中文业务释义：** 政策由中央部门发布 ≠ 全国每一个采购项目执行方式完全相同；某些政策具有明确地区、项目类型或实施范围。

---

# 二十七、创新支持：什么是合作创新采购？

财库〔2024〕13号规定：

# Cooperative Innovation Procurement
## 合作创新采购

核心结构：

```text
purchase_need    # 中文：市场现有产品 / 技术无法满足，需要技术突破或显著创新

research_goal    # 中文：最低研发目标

research_budget    # 中文：最高研发费用

research_supplier    # 中文：合作研发供应商

research_contract    # 中文：研发合同

milestones    # 中文：阶段性标志成果

first_purchase    # 中文：研发成功后的首购
```

其核心不是：

> “给创新企业多加几分”。

而是一个：

# Special Procurement Method
## 特殊采购方式

---

# 二十八、核心心智模型 ⑨
# `InnovationSupport` 不等于 `InnovationLabelBonus`

\[
\boxed{
InnovationSupport
\neq
InnovationAwardBonus
}
\]

**中文业务释义：** 政府采购支持创新 ≠ 采购人可以因为企业有“创新企业”“创新奖项”等标签就自行加分。

合作创新采购要求：

> 项目本身符合制度适用条件，并依法执行专门的需求管理、竞争、谈判、研发合同、阶段成果和首购程序。

---

# 二十九、合作创新采购的适用前提

财库〔2024〕13号规定的典型适用情形包括：

```text
market_solution_insufficient    # 中文：市场现有产品 / 技术不能满足要求，需要技术突破

new_solution_significant_improvement    # 中文：以创新产品形成新范式 / 新解决方案，能够显著改善功能性能或绩效

national_strategy_relation    # 中文：项目符合国家科技和相关产业发展规划，有利于落实国家重大战略目标任务
```

所以：

\[
\boxed{
WantInnovation
\neq
EligibleForCooperativeInnovation
}
\]

**中文业务释义：** 采购人“希望有创新” ≠ 项目当然符合合作创新采购方式适用条件。

---

# 三十、创新采购仍然要公平竞争

财库〔2024〕13号规定：

> 除只能从有限范围或者唯一供应商处采购外，应通过公开竞争确定研发供应商。

并要求：

> 除涉及国家安全和国家秘密的采购项目外，应保障内外资企业平等参与合作创新采购活动。

因此：

\[
\boxed{
InnovationPolicy
\neq
CompetitionExemption
}
\]

**中文业务释义：** 创新支持政策 ≠ 自动免除公平竞争要求。

---

# 三十一、核心心智模型 ⑩
# 合法特殊程序必须有“进入条件”和“程序证据”

系统要保存：

```text
innovation_eligibility_basis    # 中文：为什么项目符合合作创新采购适用条件

market_research_evidence    # 中文：市场现有产品 / 技术不能满足要求的调研证据

expert_review_evidence    # 中文：专家论证材料

procurement_plan    # 中文：合作创新采购方案

competition_mode    # 中文：公开竞争 / 有限范围 / 唯一供应商及其依据

research_contract    # 中文：研发合同

milestone_evidence    # 中文：阶段研发成果与验收证据

first_purchase_basis    # 中文：首购依据
```

否则：

> 不能只因为项目文件写了“创新采购”就默认程序合法。

---

# 三十二、进口产品：这是另一条政策轴

《政府采购进口产品管理办法》把进口产品定义为：

> 通过中国海关报关验放进入中国境内且产自关境外的产品。

并规定：

> 政府采购应当采购本国产品，确需采购进口产品的，实行审核管理。

因此：

\[
\boxed{
ImportStatus
\neq
DomesticProductStatus
}
\]

**中文业务释义：** 进口产品状态和本国产品政策状态是两个相关但不能合并成一个布尔字段的业务轴。

---

# 三十三、进口产品审核

典型判断流程：

```text
need_imported_product    # 中文：采购需求是否确需进口产品

domestic_availability    # 中文：中国境内是否能够获取满足需求的产品

reasonable_commercial_condition    # 中文：是否能以合理商业条件获取

legal_policy_requirement    # 中文：法律法规政策是否另有明确要求

finance_approval    # 中文：是否取得财政部门审核 / 核准

industry_opinion    # 中文：按适用规则是否需要行业主管部门意见

expert_opinion    # 中文：按适用规则是否需要专家论证意见
```

所以：

\[
\boxed{
ImportProcurement
=
Need
+
Approval
+
Evidence
}
\]

**中文业务释义：** 进口产品采购 = 确有采购需要 + 履行法定审核程序 + 具备相应证明材料。

---

# 三十四、核心心智模型 ⑪
# `ImportedProduct` 与 `ForeignInvestedEnterpriseProduct` 完全不是一回事

\[
\boxed{
ForeignInvestedEnterpriseProduct
\neq
ImportedProduct
}
\]

**中文业务释义：** 外商投资企业提供 / 生产的产品 ≠ 进口产品；必须看产品在哪里生产、是否经过关境进口以及是否符合本国产品标准，而不是看企业股东国别。

这条边界直接关系：

```text
内外资平等    # 中文：供应商主体平等

本国产品判断    # 中文：产品属性判断

进口产品审核    # 中文：是否履行进口产品采购程序
```

---

# 三十五、`不接受进口` 是采购文件要求，不是完整政策计算结果

即使项目：

```text
accept_imported_product = false    # 中文：采购文件不接受进口产品
```

系统仍然需要单独计算：

```text
domestic_product_status    # 中文：产品是否符合本国产品标准

domestic_price_preference    # 中文：是否应给予本国产品价格评审优惠

domestic_declaration_status    # 中文：声明函 / 证明文件是否满足要求
```

所以：

\[
\boxed{
NoImportedProduct
\neq
SkipDomesticProductPolicy
}
\]

**中文业务释义：** 不接受进口产品 ≠ 可以跳过本国产品政策判断。

---

# 三十六、政策优惠除了“算比例”，还要判断是否该算

本阶段将 Stage 7 的：

\[
\boxed{
DeterministicScore
\Rightarrow
CalculatorFirst
}
\]

**中文业务释义：** 确定性评分应优先交给规则引擎 / 计算器。

进一步升级为：

\[
\boxed{
PolicyApplicability
\rightarrow
Calculator
}
\]

**中文业务释义：** 先由政策引擎确认哪项政策适用，再把明确比例、金额、份额、价格扣除交给 Calculator 计算。

---

# 三十七、Policy Applicability Matrix
## 政策适用矩阵

每个政策至少要从这些维度判断：

```text
policy_id    # 中文：政策规则标识

policy_version    # 中文：政策版本

effective_time    # 中文：项目时点是否在政策有效期

jurisdiction    # 中文：政策适用地区

procurement_category    # 中文：货物 / 服务 / 工程

procurement_method    # 中文：采购方式

project_amount    # 中文：项目金额

procurement_object    # 中文：采购标的 / 品目

supplier_status    # 中文：供应商主体身份与政策状态

manufacturer_status    # 中文：制造商身份与政策状态

product_status    # 中文：产品属性，例如本国产品 / 节能产品

import_status    # 中文：进口产品状态

certificate_status    # 中文：政策要求的认证证书状态

reserved_status    # 中文：是否专门面向政策对象

exception_status    # 中文：例外条件

treaty_status    # 中文：国际条约 / 协定是否另有规定
```

因此：

\[
\boxed{
PolicyApplicability
=
MultiDimensionalDecision
}
\]

**中文业务释义：** 政策适用性判断是多维决策，不是只看一个标签。

---

# 三十八、核心心智模型 ⑫
# `PolicyNameMatch` 不等于 `PolicyApplicability`

\[
\boxed{
PolicyNameMatch
\neq
PolicyApplicability
}
\]

**中文业务释义：** 文档里出现“中小企业”“节能产品”“本国产品”等政策名称 ≠ 当前政策机制已经正确适用于这个项目。

---

# 三十九、政策之间还可能有“顺序问题”

例如一个价格评审流程可能需要：

```text
original_price    # 中文：供应商原始报价

domestic_product_adjustment    # 中文：本国产品政策调整

sme_adjustment    # 中文：小微企业政策调整

other_applicable_adjustments    # 中文：其他依法适用的政策调整

evaluation_price    # 中文：最终用于评审的政策调整后价格
```

政策引擎必须明确：

```text
calculation_basis    # 中文：每项优惠以什么价格为基数

stacking_allowed    # 中文：是否允许与其他政策叠加

exclusive_policy_ids    # 中文：哪些政策互斥

calculation_order    # 中文：如政策明确规定计算顺序，应按规则执行

rounding_rule    # 中文：金额 / 分值取舍规则
```

---

# 四十、核心心智模型 ⑬
# `PolicyStacking` 不等于 `DoubleCounting`

\[
\boxed{
PolicyStacking
\neq
DoubleCounting
}
\]

**中文业务释义：** 多项独立政策依法同时适用 ≠ 错误重复优惠；关键是每项政策都有独立依据、独立适用条件和正确计算基数。

---

# 四十一、Policy Evidence
## 政策证明材料必须结构化

不同政策需要不同证据：

```text
SME_declaration    # 中文：中小企业声明函等政策证明材料

domestic_product_declaration    # 中文：本国产品声明函或政策规定的其他证明

energy_saving_certificate    # 中文：节能产品有效认证证书

environmental_label_certificate    # 中文：环境标志产品有效认证证书

import_approval_document    # 中文：进口产品财政审核文件

innovation_procurement_plan    # 中文：合作创新采购方案及相关审批 / 论证

green_building_scope_evidence    # 中文：项目是否属于绿色建材政策实施范围的证据
```

因此：

\[
\boxed{
PolicyClaim
\neq
PolicyEvidence
}
\]

**中文业务释义：** 供应商 / 采购文件声称“符合某政策” ≠ 已经提供政策要求的有效证明材料。

---

# 四十二、政策声明函也不是普通附件

声明函可能直接决定：

```text
能否享受价格优惠    # 中文：政策资格

是否计入预留份额    # 中文：中小企业政策执行

是否认定本国产品    # 中文：本国产品支持政策

是否公开随中标结果    # 中文：政策信息公开义务
```

所以需要：

```text
declaration_type    # 中文：声明函类型

signatory    # 中文：声明主体

product_or_service_scope    # 中文：声明覆盖哪些产品 / 服务

consistency_check    # 中文：与投标响应文件是否一致

public_disclosure_required    # 中文：是否需要随中标 / 成交结果公开

false_statement_risk    # 中文：虚假声明风险
```

---

# 四十三、核心心智模型 ⑭
# `Declaration` 是政策执行证据，不是 LLM 自己“推断出来的身份”

\[
\boxed{
ModelInference
\neq
FormalPolicyDeclaration
}
\]

**中文业务释义：** 模型根据企业名称、规模、地址推测“可能是小微企业 / 本国产品” ≠ 法定政策声明和证明材料。

---

# 四十四、政策支持和 D01-D22 如何共存？

例如：

```text
本国产品政策
# 中文：依法给予符合本国产品标准的产品价格支持

D09 / D10
# 中文：禁止以所有制、组织形式、股权结构、投资者国别等不合理条件限制供应商
```

两者并不冲突。

因为：

\[
\boxed{
ProductBasedPolicy
\neq
OwnershipBasedRestriction
}
\]

**中文业务释义：** 依法基于“产品是否符合本国产品标准”的政策支持 ≠ 基于供应商所有制、股权或投资者国别的不合理限制。

---

# 四十五、再例如：中小企业政策 vs 企业规模歧视

看起来两边都涉及：

> 企业规模。

但逻辑完全不同。

D05 禁止的是：

```text
采购人自行把注册资本、营业收入、资产、利润、人员数量等规模指标设置成不合理门槛 / 评审因素
```

中小企业政策则是：

```text
依据法定 / 政策企业划型和声明机制，依法实施预留份额、价格优惠等支持措施
```

所以：

\[
\boxed{
SMEPolicy
\neq
PurchaserDefinedScalePreference
}
\]

**中文业务释义：** 法定中小企业支持政策 ≠ 采购人自行按企业大小设置偏好或歧视条件。

---

# 四十六、核心心智模型 ⑮
# 合法政策扶持最关键的不是“结果有差别”，而是“差别有没有制度授权”

\[
\boxed{
LawfulDifferentiation
=
AuthorizedPolicy
+
CorrectApplicability
+
CorrectExecution
}
\]

**中文业务释义：** 合法差异化处理 = 有效政策授权 + 当前项目正确适用 + 执行方式正确。

只要缺一层：

> 就不能自动认为政策执行正确。

---

# 四十七、国际条约 / 协定也必须进入 Policy Resolver

国办发〔2025〕34号明确：

> 中华人民共和国缔结或者共同参加的国际条约、协定对政府采购中本国产品政策另有规定的，按照有关条约、协定执行。

所以：

\[
\boxed{
DomesticProductPolicy
+
TreatyOverrideCheck
}
\]

**中文业务释义：** 执行本国产品政策时，还要检查当前采购是否存在应优先适用的国际条约 / 协定特别规定。

系统至少预留：

```text
treaty_id    # 中文：国际条约 / 协定标识

coverage_status    # 中文：当前采购主体 / 项目 / 产品是否处于协定覆盖范围

special_rule    # 中文：协定对本国产品政策是否有特别规定

resolver_result    # 中文：最终适用哪一层规则
```

---

# 四十八、Policy Conflict Resolver
## 政策冲突 / 叠加解析器

Stage 2 已经有：

# `ProcurementPolicyRegistry_V1`

Stage 8 在它上面增加：

# `Policy Resolver`
## 政策适用解析器

流程：

\[
\boxed{
ProjectFacts
\rightarrow
PolicyCandidates
\rightarrow
ApplicabilityCheck
\rightarrow
ConflictAndStacking
\rightarrow
Calculation
\rightarrow
EvidenceValidation
\rightarrow
PolicyDecision
}
\]

**中文业务释义：** 项目事实 → 候选政策 → 适用性检查 → 冲突与叠加处理 → 计算优惠 / 份额 → 验证证明材料 → 形成政策执行结论。

---

# 四十九、政策执行状态不能只有“有 / 无”

建议：

```text
NOT_CHECKED    # 中文：尚未检查

NOT_APPLICABLE    # 中文：政策不适用于当前项目 / 产品 / 供应商

APPLICABLE_PENDING_EVIDENCE    # 中文：政策可能适用，但证明材料尚不完整

APPLICABLE_CONFIRMED    # 中文：政策适用条件和证据已确认

BENEFIT_CALCULATED    # 中文：优惠 / 份额已经按规则计算

CONFLICT_REVIEW_REQUIRED    # 中文：存在政策冲突或适用顺序不明确，需要复核

EXCEPTION_APPLIES    # 中文：适用政策例外

POLICY_MISAPPLIED    # 中文：发现政策执行方式错误

HUMAN_REVIEW_REQUIRED    # 中文：高影响或规则不明确，需要人工复核
```

因此：

\[
\boxed{
PolicyExecutionState
\neq
PolicyKeywordFound
}
\]

**中文业务释义：** 政策执行状态 ≠ 在采购文件里搜到了一个政策关键词。

---

# 五十、Policy Finding
## 政策合规发现项

一个完整政策 Finding 至少：

```text
finding_id    # 中文：政策合规发现项标识

review_domain    # 中文：审查域，这里固定为POLICY政府采购政策

policy_id    # 中文：政策规则标识

policy_version    # 中文：政策版本

policy_family    # 中文：本国产品 / 中小企业 / 绿色 / 创新 / 进口产品等政策类别

project_id    # 中文：采购项目标识

document_id    # 中文：采购文件标识

document_version    # 中文：采购文件版本

applicability_result    # 中文：政策适用性判断结果

applicability_facts    # 中文：金额、品目、项目类型、主体、时点等适用事实

benefit_type    # 中文：预留、价格扣除、优先采购、强制采购、特殊程序等

benefit_rate    # 中文：适用比例或价格优惠比例

calculation_basis    # 中文：优惠计算基数

stacking_policy_ids    # 中文：与当前政策同时适用的其他政策

evaluation_price_before    # 中文：政策调整前评审基准价格

evaluation_price_after    # 中文：政策调整后评审价格

evidence_required    # 中文：政策要求的证明材料

evidence_status    # 中文：证明材料是否完整有效

exception_status    # 中文：例外状态

treaty_status    # 中文：国际条约 / 协定特别规则状态

legal_basis_refs    # 中文：法律政策依据

policy_snapshot_id    # 中文：项目时点政策快照标识

evidence_span    # 中文：采购文件相关原文定位

decision_state    # 中文：政策审查状态

risk_level    # 中文：政策执行风险等级

confidence    # 中文：系统判断置信度

human_review_required    # 中文：是否需要人工复核

recommended_revision    # 中文：政策条款 / 计算方式修改建议
```

---

# 五十一、政策价格计算记录必须独立保存

不要只保存：

```text
evaluation_price = 600000
# 中文：最终评审价格60万元
```

还要保存：

```text
original_price    # 中文：原始报价

adjustment_01_policy_id    # 中文：第1项政策调整依据

adjustment_01_rate    # 中文：第1项政策比例

adjustment_01_amount    # 中文：第1项政策扣除金额

adjustment_02_policy_id    # 中文：第2项政策调整依据

adjustment_02_rate    # 中文：第2项政策比例

adjustment_02_amount    # 中文：第2项政策扣除金额

final_evaluation_price    # 中文：最终用于评审的价格

rounding_rule    # 中文：金额取舍 / 四舍五入规则

calculation_trace    # 中文：完整计算过程
```

因此：

\[
\boxed{
FinalNumber
\neq
AuditableCalculation
}
\]

**中文业务释义：** 只有最终数值 ≠ 可审计政策计算；必须能够还原每一步政策调整。

---

# 五十二、核心心智模型 ⑯
# 政策计算必须可重放

\[
\boxed{
SamePolicySnapshot
+
SameProjectFacts
+
SameEvidence
\Rightarrow
SamePolicyResult
}
\]

**中文业务释义：** 在相同政策版本、相同项目事实和相同证据下，政策引擎应能够重新计算出相同结果。

这就是：

# Reproducibility
## 可复现性

---

# 五十三、Hard Negative
## 政策域高难负例

这一阶段必须重点训练：

```text
HardNegative_DomesticForeignInvested
# 中文：外商投资企业生产的产品符合本国产品标准，依法平等享受政策，不应误报为“外资歧视”

HardNegative_SMEPolicyPreference
# 中文：依法执行小微企业价格评审优惠，不应误报为企业规模歧视

HardNegative_MandatoryEnergySaving
# 中文：依法执行强制采购节能产品，不应误报为不合理产品限制

HardNegative_CooperativeInnovation
# 中文：依法满足条件并执行程序的合作创新采购，不应误报为“只有创新企业才能参加”的任意偏好

HardNegative_ImportApproval
# 中文：确需进口产品并已履行法定审核程序，不应因“采购进口产品”本身直接判违规

HardNegative_PolicyStacking
# 中文：本国产品与小微企业优惠在满足条件时依法叠加，不应误报为重复计算
```

---

# 五十四、False Positive 在政策域为什么特别危险？

如果 AI 把合法政策全部报成歧视：

> 采购人员会开始忽略系统提示。

例如：

```text
依法强制采购节能产品
→ AI报“品牌 / 产品限制”

依法给予小微企业价格优惠
→ AI报“企业规模歧视”

依法支持本国产品
→ AI报“外资歧视”

依法采用合作创新采购
→ AI报“排斥普通供应商”
```

这会让系统失去专业可信度。

所以：

\[
\boxed{
ComplianceAI
必须同时知道
Prohibition
+
AuthorizedPreference
}
\]

**中文业务释义：** 合规 AI 必须同时学会“什么不能做”和“什么政策明确允许 / 要求做”，否则只会产生单向误报。

---

# 五十五、Counterfactual Pair
## 政策域反事实样本

### Pair A：本国产品

```text
外商投资企业提供在中国境内生产、符合本国产品标准的产品，不给予本国产品政策支持
# 中文：按企业投资者身份排除政策待遇
```

### Pair B

```text
只判断产品是否符合本国产品标准，不因供应商是国企、民企或外资企业改变政策待遇
# 中文：产品标准与供应商所有制分离
```

比较：

```text
OwnershipDiscrimination    # 中文：所有制 / 投资者身份歧视

ProductBasedPolicy    # 中文：依法基于产品属性执行政策
```

---

### Pair C：中小企业

```text
注册资本越小价格扣除越多
# 中文：采购人自己按资本规模设计优惠
```

### Pair D

```text
按照财库〔2020〕46号、财库〔2022〕19号及当前项目采购文件确定的小微企业政策比例执行价格评审优惠
# 中文：按法定政策机制执行
```

比较：

```text
PurchaserDefinedScalePreference    # 中文：采购人自定义企业规模偏好

AuthorizedSMEPolicy    # 中文：有政策依据的中小企业扶持
```

---

### Pair E：绿色采购

```text
获得某地方协会“绿色品牌奖”的产品加10分
# 中文：无明确政策基础的奖项加分
```

### Pair F

```text
对属于政府采购节能 / 环境标志品目清单范围并持有效政策认可认证证书的产品，按现行绿色采购政策执行
# 中文：按品目清单与有效认证执行政策
```

比较：

```text
ArbitraryGreenBonus    # 中文：任意绿色名义加分

PolicyGroundedGreenProcurement    # 中文：有政策依据的绿色采购
```

---

# 五十六、Policy Benchmark
## 政策合规 Benchmark 应该测什么？

至少：

```text
domestic_product_status_accuracy    # 中文：本国产品状态判断准确率

domestic_product_scope_accuracy    # 中文：本国产品政策适用货物范围判断准确率

domestic_price_preference_accuracy    # 中文：20%本国产品价格评审优惠计算准确率

domestic_80_percent_rule_accuracy    # 中文：多产品采购包80%成本占比规则判断准确率

foreign_invested_equal_treatment_accuracy    # 中文：外商投资企业平等待遇判断准确率

sme_status_accuracy    # 中文：中小企业政策身份判断准确率

sme_manufacturer_logic_accuracy    # 中文：货物项目制造商政策逻辑判断准确率

sme_reserved_procurement_accuracy    # 中文：中小企业预留份额判断准确率

sme_price_preference_accuracy    # 中文：小微企业价格优惠计算准确率

policy_stacking_accuracy    # 中文：多政策叠加判断与计算准确率

green_category_accuracy    # 中文：节能 / 环境标志品目清单适用判断准确率

green_certificate_validity_accuracy    # 中文：绿色认证证书有效性判断准确率

mandatory_vs_priority_accuracy    # 中文：强制采购与优先采购区分准确率

innovation_eligibility_accuracy    # 中文：合作创新采购适用条件判断准确率

import_approval_accuracy    # 中文：进口产品审核程序完整性判断准确率

temporal_policy_accuracy    # 中文：政策时点判断准确率

jurisdiction_scope_accuracy    # 中文：地域 / 项目范围判断准确率

false_positive_on_authorized_policy    # 中文：合法政策扶持被误报成歧视的比例

calculation_reproducibility    # 中文：政策价格 / 份额计算可复现性

evidence_localization_accuracy    # 中文：政策条款和证明材料定位准确率
```

---

# 五十七、核心心智模型 ⑰
# 政策域 Benchmark 必须专门测“合法政策误报率”

\[
\boxed{
PolicyComplianceReliability
=
RiskDetection
+
AuthorizedPolicyRecognition
}
\]

**中文业务释义：** 政策合规可靠性 = 能识别真正错误执行 + 能正确识别合法政策支持；只会报风险、不认识合法政策，不叫可靠。

---

# 五十八、`ProcurementPolicyCompliance_V1` 建议目录

```text
ProcurementPolicyCompliance_V1/    # 中文：政府采购政策合规工程资产根目录

├── registry/    # 中文：政策规则和版本
│   ├── domestic_product/    # 中文：本国产品政策
│   ├── sme/    # 中文：中小企业政策
│   ├── green/    # 中文：绿色采购政策
│   ├── innovation/    # 中文：合作创新采购政策
│   └── import_product/    # 中文：进口产品管理政策
│
├── resolver/    # 中文：政策适用、冲突和叠加解析
│   ├── applicability/    # 中文：政策适用性
│   ├── stacking/    # 中文：政策叠加
│   ├── conflict/    # 中文：政策冲突
│   ├── temporal/    # 中文：政策时点
│   ├── jurisdiction/    # 中文：地区 / 范围
│   └── treaty/    # 中文：国际条约 / 协定特别规则
│
├── calculator/    # 中文：确定性政策计算
│   ├── domestic_price.py    # 中文：本国产品价格评审优惠
│   ├── sme_price.py    # 中文：小微企业价格评审优惠
│   ├── reserved_share.py    # 中文：中小企业预留份额
│   └── package_ratio.py    # 中文：多产品采购包本国产品成本占比
│
├── evidence/    # 中文：政策证明材料
│   ├── declarations/    # 中文：中小企业 / 本国产品声明函
│   ├── certificates/    # 中文：节能 / 环境标志等认证
│   ├── approvals/    # 中文：进口产品审核文件
│   └── innovation_records/    # 中文：合作创新采购方案、论证、合同和里程碑
│
├── schema/    # 中文：结构化数据契约
│   ├── policy_rule.json    # 中文：政策规则Schema
│   ├── policy_applicability.json    # 中文：政策适用性Schema
│   ├── policy_calculation.json    # 中文：政策计算记录Schema
│   └── policy_finding.json    # 中文：政策合规发现项Schema
│
├── tests/    # 中文：政策合规测试集
│   ├── positive/    # 中文：政策错误执行正例
│   ├── hard_negative/    # 中文：合法政策扶持高难负例
│   ├── stacking/    # 中文：政策叠加测试
│   ├── historical/    # 中文：历史政策时点测试
│   └── cross_policy/    # 中文：跨政策组合案例
│
└── manifest.json    # 中文：版本、来源、依赖和测试清单
```

---

# 五十九、Policy Applicability Schema 第一版

```text
policy_execution_id    # 中文：单次政策执行记录标识

policy_id    # 中文：政策规则标识

policy_version    # 中文：政策版本

policy_family    # 中文：本国产品 / 中小企业 / 绿色 / 创新 / 进口产品

project_id    # 中文：采购项目标识

project_date    # 中文：政策适用判断所依据的项目时点

jurisdiction    # 中文：项目地区 / 政策适用地区

procurement_category    # 中文：货物 / 服务 / 工程

procurement_method    # 中文：采购方式

project_amount    # 中文：项目金额

package_id    # 中文：采购包标识

procurement_object_ids    # 中文：采购标的 / 产品标识列表

supplier_id    # 中文：供应商标识

manufacturer_ids    # 中文：制造商标识列表

supplier_policy_status    # 中文：供应商对应政策身份

product_policy_status    # 中文：产品对应政策状态

import_status    # 中文：进口产品状态

certificate_status    # 中文：政策认证证书状态

reserved_status    # 中文：是否为政策预留项目 / 采购包

exception_status    # 中文：例外状态

treaty_status    # 中文：国际条约 / 协定状态

applicable    # 中文：最终是否适用

applicability_reason    # 中文：适用 / 不适用的理由

evidence_refs    # 中文：政策证据引用

human_review_required    # 中文：是否需要人工复核
```

---

# 六十、Policy Calculation Schema 第一版

```text
calculation_id    # 中文：政策计算标识

policy_execution_ids    # 中文：参与本次计算的政策执行记录

original_price    # 中文：供应商原始报价

domestic_rate    # 中文：本国产品价格评审优惠比例

domestic_deduction    # 中文：本国产品扣除金额

sme_rate    # 中文：小微企业价格评审优惠比例

sme_deduction    # 中文：小微企业扣除金额

other_policy_adjustments    # 中文：其他依法适用的政策调整

stacking_allowed    # 中文：当前政策是否允许叠加

calculation_basis    # 中文：各项优惠计算基数

calculation_order    # 中文：政策规定的计算顺序

rounding_rule    # 中文：金额取舍规则

final_evaluation_price    # 中文：最终用于评审的价格

calculation_trace    # 中文：完整可审计计算过程

calculator_version    # 中文：使用的政策计算器版本
```

---

# 六十一、本阶段最重要的 18 个核心心智模型

> **心智模型 ①：`PolicyPreference ≠ IllegalDiscrimination`。有明确制度依据的政策支持，与采购人自行设置的差别歧视必须严格区分。**

> **心智模型 ②：`PolicySupport = Authority + Applicability + Mechanism + Evidence`。政策支持必须同时具备依据、适用性、执行机制和证明材料。**

> **心智模型 ③：`DomesticProduct ≠ DomesticEnterprise`。本国产品判断对象是产品，不是供应商所有制。**

> **心智模型 ④：`ForeignInvestedEnterprise + DomesticProduct ⇒ EqualPolicyTreatment`。外商投资企业符合标准的本国产品依法平等享受支持政策。**

> **心智模型 ⑤：`SameProduct + DifferentPolicyDate = PotentiallyDifferentDomesticTest`。本国产品标准必须按产品和时点解析。**

> **心智模型 ⑥：`EvaluationPrice ≠ ContractPrice`。价格评审优惠改变的是评审计算价格，不是当然改变合同成交价。**

> **心智模型 ⑦：`DomesticDeclaration ≠ SupplierQualificationGate`。本国产品声明函用于政策支持认定，不应被错误设置成供应商资格门槛。**

> **心智模型 ⑧：`NonImportedProduct ≠ DomesticProduct`。非进口产品并不自动等于本国产品。**

> **心智模型 ⑨：`SMEPolicy ≠ PriceDiscountOnly`。中小企业政策还包括预留份额、联合体 / 分包、支付和融资支持。**

> **心智模型 ⑩：`HistoricalTemporaryPolicy ≠ CurrentPermanentRule`。历史阶段性比例不能跨时点误用。**

> **心智模型 ⑪：`PolicyRange ≠ AlwaysUseUpperBound`。政策允许区间不等于每个项目都自动选最高优惠。**

> **心智模型 ⑫：`PolicyStacking ≠ DoubleCounting`。多项政策依法叠加，与错误重复计算是两回事。**

> **心智模型 ⑬：`MandatoryProcurement ≠ PriorityProcurement`。绿色强制采购和绿色优先采购必须分开。**

> **心智模型 ⑭：`InnovationSupport ≠ InnovationAwardBonus`。支持科技创新不等于任意给“创新标签”加分。**

> **心智模型 ⑮：`ForeignInvestedEnterpriseProduct ≠ ImportedProduct`。企业资本属性和产品进口属性是两套不同维度。**

> **心智模型 ⑯：`CalculateAfterApplicability`。先确认政策适用，再做比例和价格计算。**

> **心智模型 ⑰：`PolicyClaim ≠ PolicyEvidence`。声称符合政策，不等于政策证明材料已经成立。**

> **心智模型 ⑱：`ComplianceAI = Prohibition + AuthorizedPreference`。真正可靠的政府采购合规 AI，既要知道什么禁止，也要知道什么政策明确允许或要求。**

---

# 六十二、把整个政策合规判断压成一张工程图

```text
Project / Package / Supplier / Product Facts
# 中文：项目、采购包、供应商、制造商和产品事实
↓
Policy Candidate Discovery
# 中文：发现可能适用的本国产品、中小企业、绿色、创新、进口产品政策
↓
Temporal + Jurisdiction Resolver
# 中文：按项目时点和适用地区解析政策版本
↓
Applicability Matrix
# 中文：检查项目类型、金额、品目、企业状态、产品状态、证书、进口状态等
↓
Evidence Validation
# 中文：验证声明函、认证证书、审核文件、论证材料等
↓
Conflict / Exception / Treaty Check
# 中文：处理政策冲突、例外和国际条约 / 协定特别规则
↓
Stacking Resolver
# 中文：判断多项政策能否同时适用
↓
Calculator
# 中文：计算价格扣除、预留份额、成本占比等确定性结果
↓
Policy Execution State
# 中文：形成适用、不适用、待证据、错误执行、需人工复核等状态
↓
Evidence Gate
# 中文：政策依据、项目事实、证明材料和计算过程是否完整
↓
Policy Finding / Checked-No-Finding / Human Review
# 中文：政策风险发现 / 已检查无风险 / 人工复核
↓
Audit Trace + Benchmark
# 中文：完整审计链和政策评测
```

---

# 六十三、脑中最后只留一句

> **政府采购政策合规的本质，不是看到“优惠、限制、预留、强制采购、特殊程序”就判断差别待遇，而是先确认这种差异化处理有没有明确且当前适用的政策授权，再核对项目、供应商、制造商和产品是否满足适用条件，证明材料是否有效，政策之间能否叠加，比例和价格计算是否正确，最终把每一步都留成可追溯的政策证据链。真正可靠的合规 AI 必须同时认识“禁止的不合理歧视”和“制度授权的合法政策支持”。**

---

# 第十一课 · 第 8 阶段掌握测试

现在不回看正文，你应该能够解释：

```text
Policy Preference 为什么不等于 Illegal Discrimination？
# 中文：有政策依据的差异化支持与违法差别歧视的根本边界是什么？

Policy Support 为什么必须包含 Authority / Applicability / Mechanism / Evidence？
# 中文：为什么只有政策名称还不够？

Domestic Product 为什么不等于 Domestic Enterprise？
# 中文：为什么本国产品是产品属性，而不是企业所有制标签？

外商投资企业生产的本国产品为什么可以平等享受政策？
# 中文：供应商资本属性与产品属性怎样分层？

2026年的本国产品标准为什么必须按“产品 + 时点”解析？
# 中文：组件成本占比、关键组件、关键工序为什么不能一次性写死？

Evaluation Price 为什么不等于 Contract Price？
# 中文：价格评审优惠实际改变的是什么？

为什么本国产品声明函不能被错误设置成 Supplier Qualification Gate？
# 中文：政策证明和供应商准入边界在哪里？

为什么 Non-imported Product 不等于 Domestic Product？
# 中文：不接受进口产品为什么仍不能跳过本国产品政策判断？

中小企业政策为什么不只是价格扣除？
# 中文：预留份额、联合体、分包、融资等机制分别解决什么？

货物项目为什么要关注 Manufacturer，而不能只看投标供应商是不是小微企业？
# 中文：制造商身份怎样影响政策适用？

Historical Temporary Policy 为什么不能直接用于2026项目？
# 中文：为什么2022年阶段性比例不能被模型永久记住？

Policy Range 为什么不等于 Always Use Upper Bound？
# 中文：10%-20%为什么不能自动选择20%？

本国产品与小微企业价格优惠什么时候可能同时适用？
# 中文：Policy Stacking 如何先判断、后计算？

为什么 Policy Stacking 不等于 Double Counting？
# 中文：合法政策叠加与错误重复优惠怎样区分？

绿色采购中的 Mandatory 与 Priority 有什么区别？
# 中文：强制采购和优先采购为什么必须分开建模？

为什么绿色采购不能简化为 Green Keyword 或任意“绿色证书加分”？
# 中文：品目清单、认证证书和政策依据分别起什么作用？

合作创新采购为什么不是 Innovation Label Bonus？
# 中文：创新支持为什么是一套法定特殊采购程序，而不是给“创新企业”随意加分？

Innovation Policy 为什么不等于 Competition Exemption？
# 中文：合作创新采购为什么仍要关注公开竞争和平等参与？

Imported Product 与 Foreign-invested Enterprise Product 有什么根本区别？
# 中文：产品进口属性和企业资本属性为什么不能混？

进口产品采购为什么需要 Need + Approval + Evidence？
# 中文：确需进口、审核程序和专家 / 主管部门材料怎样形成证据链？

Policy Applicability Matrix 需要哪些维度？
# 中文：时点、地区、金额、品目、供应商、制造商、产品、证书、进口状态为什么缺一不可？

为什么 Policy Claim 不等于 Policy Evidence？
# 中文：模型为什么不能靠推断替代声明函、证书和审核文件？

为什么政策计算必须保存 Calculation Trace？
# 中文：只有最终评审价格为什么不够审计？

为什么合规AI必须同时学习 Prohibition + Authorized Preference？
# 中文：为什么只会“查违规”会导致大量合法政策误报？
```

如果这些能够完整解释：

\[
\boxed{
第十一课第8阶段真正掌握
}
\]

**中文业务释义：** 如果能够把本国产品、中小企业、绿色采购、合作创新、进口产品五类政策的“依据—适用—证据—计算—叠加—审计”完整讲清楚，并能够区分合法政策扶持和不合理差别待遇，就说明真正掌握了本阶段。

---

# 下一阶段：第十一课 · 第 9 阶段
# 采购方式、竞争充分性与异常低价检查
## 市场竞争是否充分？单一来源等方式是否成立？确定性低价规则什么时候应该启动审查？

下一阶段将正式建立：

# `ProcurementCompetitionCompliance_V1`

最重要的边界：

\[
\boxed{
LowPrice
\neq
AbnormallyLowPrice
}
\]

**中文业务释义：** 报价低 ≠ 异常低价；真正需要判断的是价格是否触发适用规则、是否存在履约风险和是否需要依法启动解释、审查或进一步核验。
