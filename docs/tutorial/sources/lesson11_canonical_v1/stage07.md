# 第十一课 · 第 7 阶段
# 评审标准合规：量化、分值、业绩、奖项、人员、主观分与资格评分化
## 怎样识别“看起来可以打分，实际上与采购需求无关”“资格门槛换个位置放进评分表”“分值已经数字化，但评分逻辑仍然不可验证”等问题？

第 6 阶段我们已经建立：

\[
\boxed{
TechnicalSpecificity
\neq
TechnicalDiscrimination
}
\]

**中文业务释义：** 技术参数写得具体，不自动等于技术歧视或不合理技术排斥；真正要检查的是参数是否具有项目必要性、是否属于最小充分约束、是否保留合理竞争空间。

并且建立：

\[
\boxed{
TechnicalRequirement
\rightarrow
FunctionalGoal
\rightarrow
MinimalSufficientConstraint
\rightarrow
EquivalentPath
\rightarrow
MarketEvidence
}
\]

**中文业务释义：** 技术要求 → 真实功能目标 → 最小充分约束 → 等效进入路径 → 市场可满足性证据。

现在进入采购文件里另一个决定竞争结果的核心区域：

# Scoring Criteria
## 评审因素 / 评分标准

评分标准的危险之处在于：

> **它通常不会直接把供应商挡在门外，但会通过分值设计改变竞争优势。**

因此一个条件即使没有被设置成：

```text
qualification_gate    # 中文：资格准入门槛
```

只要被设置成：

```text
scoring_factor    # 中文：评分因素
```

仍然可能影响：

> 谁更容易成为中标候选人。

本阶段第一条核心边界正式锁定为：

\[
\boxed{
Scorable
\neq
CompliantScoringFactor
}
\]

**中文业务释义：** 一个条件“可以被打分” ≠ 它就当然适合作为合规的政府采购评分因素。

本阶段最终形成：

# `ProcurementScoringCompliance_V1`

---

# 一、本阶段的法规与专项整治业务基线

本阶段至少连接以下正式规则层：

```text
《中华人民共和国政府采购法实施条例》第三十四条
# 中文：综合评分法要求按照评审因素的量化指标评审，分值设置应与量化指标对应；招标文件没有规定的评标标准不得作为评审依据

《政府采购货物和服务招标投标管理办法》（财政部令第87号）第五十五条
# 中文：评审因素应与货物服务质量相关，资格条件不得作为评审因素；评审因素应细化、量化，并与商务条件和采购需求对应

《政府采购需求管理办法》（财库〔2021〕22号）第二十一条
# 中文：采用综合性评审方法时，评审因素应按照采购需求和实现项目目标相关因素确定；客观但不可量化的采购需求指标原则上应作为实质性要求，不得作为评分项；参与评分的指标应按量化等次设置对应分值

《2025年政府采购领域“四类”违法违规行为专项整治工作指引》
# 中文：专项整治明确把评分标准列为差别歧视条款检查重点，并关注特定区域 / 行业业绩、奖励、企业规模条件、证书奖项等被设置为评审因素的情形
```

因此：

\[
\boxed{
ScoringCompliance
=
DemandRelation
+
Quantifiability
+
ScoreMapping
+
QualificationBoundary
+
CompetitionNeutrality
+
Evidence
}
\]

**中文业务释义：** 评分合规 = 与采购需求的关联性 + 可量化性 + 分值映射关系 + 资格与评分边界 + 竞争中立性 + 可验证证据。

---

# 二、评分标准到底在做什么？

综合评分场景中，可以把评分理解成：

\[
\boxed{
SupplierResponse
\rightarrow
ScoringFactors
\rightarrow
FactorScores
\rightarrow
WeightedTotal
\rightarrow
Ranking
}
\]

**中文业务释义：** 供应商响应文件 → 各项评分因素 → 各因素得分 → 按权重汇总总分 → 形成排序结果。

所以评分标准本质上是：

# Decision Function
## 决策函数

它不是采购文件里的“装饰性表格”。

分值怎么设置：

> 会直接改变供应商排序。

因此：

\[
\boxed{
ScoringDesign
=
DecisionDesign
}
\]

**中文业务释义：** 设计评分标准，本质上就是在设计最终竞争结果的决策机制。

---

# 三、核心心智模型 ①
# `Score` 不是“意见”，而是“可追溯的决策变量”

一个专业评分项至少应该回答：

```text
what_is_scored    # 中文：到底评什么
why_it_matters    # 中文：为什么它与采购目标 / 服务质量 / 履约能力有关
how_to_measure    # 中文：用什么指标或证据测量
how_to_map_score    # 中文：指标达到不同等次时怎样映射成分值
what_evidence    # 中文：供应商用什么材料证明
what_is_cap    # 中文：最高分 / 封顶规则是什么
what_is_zero    # 中文：什么情况下不得分
```

因此：

\[
\boxed{
ScoreWithoutMeasurementRule
=
JudgmentRisk
}
\]

**中文业务释义：** 只有分值、没有明确测量规则的评分项，会形成较大的自由裁量和评审不一致风险。

---

# 四、Scoring Factor
## 评分因素的工程结构

建议把每个评分项结构化成：

\[
\boxed{
ScoringFactor
=
Objective
+
Metric
+
Level
+
Score
+
Evidence
+
Cap
}
\]

**中文业务释义：** 评分因素 = 评价目标 + 可评价指标 + 指标等次 + 对应分值 + 证明材料 + 分值上限。

对应字段：

```text
score_item_id    # 中文：评分项标识
factor_name    # 中文：评分因素名称
factor_objective    # 中文：该评分项想比较供应商哪一种真实能力 / 质量差异
metric_name    # 中文：实际用于评价的指标
metric_type    # 中文：数值型、等级型、布尔型、方案型等指标类型
level_definition    # 中文：不同指标等次怎样定义
score_mapping    # 中文：每个等次对应多少分
maximum_score    # 中文：该评分项最高分
minimum_score    # 中文：该评分项最低分
evidence_required    # 中文：需要什么证明材料
business_relation    # 中文：与采购需求 / 服务质量 / 履约目标的对应关系
```

---

# 五、核心心智模型 ②
# `NumberedScore` 不等于 `QuantifiedCriterion`

一个评分项写成：

```text
优秀：10分    # 中文：最高档
良好：7分    # 中文：中间档
一般：4分    # 中文：较低档
```

看起来已经有数字。

但如果没有说明：

```text
什么叫优秀？    # 中文：可观察判据是什么
什么叫良好？    # 中文：与优秀有什么客观差异
什么叫一般？    # 中文：最低达到什么要求
```

那么：

\[
\boxed{
NumericScore
\neq
MeaningfulQuantification
}
\]

**中文业务释义：** 分值写成数字 ≠ 评审因素已经真正细化量化；关键是指标等次必须具有可识别、可验证的差异。

---

# 六、Quantifiability
## 可量化性

可量化并不只意味着“必须是连续数字”。

它可以包括：

```text
numeric_range    # 中文：连续数值区间，例如响应时间、容量、数量
discrete_level    # 中文：离散等级，但每个等级必须有明确客观判据
boolean_condition    # 中文：满足 / 不满足明确客观条件
count_based    # 中文：按符合条件的数量计分
evidence_based_level    # 中文：依据可验证材料划分客观等次
```

真正关键的是：

\[
\boxed{
SameEvidence
\rightarrow
SameScoreRule
}
\]

**中文业务释义：** 面对相同证据，评分规则应尽可能导向相同的分值判断，而不是完全依赖评委个人感受。

---

# 七、核心心智模型 ③
# `Quantifiable` 的工程目标是减少“无边界裁量”

因此：

\[
\boxed{
Quantification
\neq
EliminateHumanJudgment
}
\]

**中文业务释义：** 量化 ≠ 完全消灭人工判断；它的目标是给人工判断建立边界、尺度和证据规则。

特别是：

```text
设计方案    # 中文：方案类项目
实施方案    # 中文：实施组织类内容
服务方案    # 中文：服务类项目响应
风险控制方案    # 中文：风险治理类方案
```

可能无法全部转换成纯机械数字，但系统仍然应该尽可能明确：

```text
evaluation_dimensions    # 中文：评价维度
observable_evidence    # 中文：每个维度可以观察的事实 / 内容
level_anchors    # 中文：各评分等级的锚点描述
score_range    # 中文：各等级对应的分值范围
missing_element_rule    # 中文：关键内容缺失怎样扣分
contradiction_rule    # 中文：方案内部矛盾或不响应需求怎样处理
```

---

# 八、方案评分：主观 ≠ 任意

本阶段正式建立：

\[
\boxed{
SubjectiveEvaluation
\neq
ArbitraryScoring
}
\]

**中文业务释义：** 方案类评审允许存在专业判断，但专业判断 ≠ 没有客观边界的任意打分。

如果一个方案评分项只有：

```text
方案科学合理、完整可行：10分    # 中文：看似专业但缺少明确判据
方案较合理：6分    # 中文：等级差异不清
方案一般：2分    # 中文：无法稳定复现
```

系统应提出：

# Quantification Risk
## 细化量化风险

不是因为“出现主观词就一定违规”，而是因为评分等级之间没有足够可验证的区分标准。

---

# 九、核心心智模型 ④
# `Subjectivity` 应被结构化，而不是被假装不存在

可以把方案评分拆成：

```text
coverage    # 中文：是否覆盖采购需求要求的关键内容
specificity    # 中文：方案是否针对当前项目，而非通用模板
feasibility    # 中文：人员、流程、资源、时间是否具有可执行性
risk_control    # 中文：是否识别关键风险并提出对应措施
service_level    # 中文：是否满足明确服务水平目标
evidence_consistency    # 中文：方案内容是否与供应商其他响应材料一致
```

再为每个维度设置：

```text
observable_anchor    # 中文：可观察的评分锚点
score_band    # 中文：分值档位
missing_rule    # 中文：缺项扣分规则
```

这样：

\[
\boxed{
ExpertJudgment
+
StructuredRubric
>
UnboundedSubjectivity
}
\]

**中文业务释义：** 专家判断 + 结构化评分量表，比没有边界的主观判断更可靠、更可审计。这里的 `>` 表示工程可靠性和可复现性更高。

---

# 十、资格条件为什么不能“换个位置继续打分”？

财政部令第 87 号第五十五条明确规定资格条件不得作为评审因素。

因此：

\[
\boxed{
QualificationCondition
\neq
ScoringFactor
}
\]

**中文业务释义：** 资格准入条件 ≠ 可以继续作为评分因素加分的条件。

这与 Stage 5 的：

\[
\boxed{
QualificationGate
\neq
ScoringPreference
}
\]

**中文业务释义：** 决定“能不能参加”的资格门槛 ≠ 决定“通过资格后得多少分”的评分偏好。

完全接起来。

---

# 十一、Qualification-to-Scoring Leakage
## 资格条件评分化 / 资格条件泄漏进评分表

这是 Stage 7 必须重点做的 Cross-domain Review。

例如：

```text
资格条件：供应商必须具有某证书    # 中文：没有该证书不能进入评审
评分标准：具有该证书得5分    # 中文：同一证书又被拿来加分
```

系统必须检测：

```text
canonical_requirement_id    # 中文：同一业务要求跨章节的归一化标识
qualification_clause_id    # 中文：资格条款位置
scoring_clause_id    # 中文：评分条款位置
same_requirement    # 中文：是否属于同一个实质条件
duplicate_role    # 中文：是否同时承担准入和评分作用
```

因此：

\[
\boxed{
CrossSectionDuplicate
\neq
HarmlessDuplicate
}
\]

**中文业务释义：** 同一条件跨资格章节和评分章节重复出现，不一定只是文本重复；它可能意味着资格条件被再次评分。

---

# 十二、核心心智模型 ⑤
# `Deduplicate` 不能把业务角色差异抹掉

Stage 3 已经建立：

\[
\boxed{
Deduplicate
\neq
EraseRoleDifferences
}
\]

**中文业务释义：** 文本去重 ≠ 删除同一要求在不同业务位置上的角色差异。

Stage 7 必须继续保留：

```text
ENTRY_GATE    # 中文：资格准入门槛
SCORING_FACTOR    # 中文：评分因素
SUBSTANTIVE_GATE    # 中文：实质性响应门槛
PERFORMANCE_OBLIGATION    # 中文：合同履约义务
```

然后做：

# Role Conflict Detection
## 业务角色冲突检查

---

# 十三、D02：特定区域 / 特定主体业绩、奖励加分

附件 9 第一类中的 D02 直接连接评分标准。

风险候选可能表现为：

```text
本省业绩加分    # 中文：按特定行政区域业绩加分
本市业绩加分    # 中文：按本地业绩加分
某类特定采购人业绩加分    # 中文：按特定主体业绩加分
本地区奖项加分    # 中文：按特定行政区域奖励加分
```

所以：

\[
\boxed{
ExperienceScoring
\neq
RegionalPreference
}
\]

**中文业务释义：** 业绩可以作为需要审查其合理性的履约能力评价因素，但不能把“在哪个地区做过”简单变成区域竞争优势。

---

# 十四、D03：特定行业业绩、奖励评分

系统要区分：

```text
capability_similarity    # 中文：业绩是否证明与当前项目相似的真实履约能力
industry_identity    # 中文：仅仅因为属于某行业而获得优势
award_relevance    # 中文：奖项到底证明什么项目能力
score_weight    # 中文：该业绩 / 奖项对总分影响有多大
```

因此：

\[
\boxed{
RelevantExperience
\neq
IndustryIdentityBonus
}
\]

**中文业务释义：** 与当前合同履约能力相关的经验 ≠ 因属于某一行业身份而直接获得额外分值。

---

# 十五、业绩评分必须问哪几个问题？

建议形成：

# Experience Scoring Test
## 业绩评分检验

至少检查：

```text
experience_objective    # 中文：为什么要评历史业绩
capability_dimension    # 中文：业绩想证明哪一种履约能力
similarity_definition    # 中文：“类似业绩”到底按什么能力维度定义
region_constraint    # 中文：是否限定特定地域
industry_constraint    # 中文：是否限定特定行业身份
specific_entity_constraint    # 中文：是否限定特定采购人 / 主体
contract_amount_constraint    # 中文：是否使用特定合同金额门槛
time_window    # 中文：业绩时间范围
counting_rule    # 中文：每个业绩怎样计分
maximum_score    # 中文：业绩项最高分
evidence_required    # 中文：合同、验收等证明材料要求
```

---

# 十六、核心心智模型 ⑥
# `PastPerformance` 必须映射到 `FuturePerformanceCapability`

\[
\boxed{
PastPerformance
\rightarrow
CapabilityDimension
\rightarrow
ExpectedContractPerformance
}
\]

**中文业务释义：** 历史业绩 → 对应的真实能力维度 → 对当前合同未来履约能力的合理证明关系。

如果中间这一层不存在，业绩评分就容易变成“历史身份奖励”。

---

# 十七、D05：企业规模条件进入评分表

Stage 5 已经处理了资格门槛中的：

```text
经营年限    # 中文：企业成立 / 经营年限
注册资本    # 中文：注册资本
资产总额    # 中文：企业资产规模
营业收入    # 中文：营收规模
从业人员    # 中文：企业人员规模
利润    # 中文：利润水平
纳税额    # 中文：纳税规模
```

Stage 7 必须继续检查它们有没有从“资格门槛”换成“评分加分”。

因此：

\[
\boxed{
MoveFromGateToScore
\neq
RiskRemoved
}
\]

**中文业务释义：** 一个不适合作为资格门槛的规模条件，挪到评分表里，不代表其差别歧视风险自动消失。

---

# 十八、核心心智模型 ⑦
# “不淘汰供应商，只少给几分”仍然会影响竞争

评分会改变：

\[
\boxed{
SupplierRanking
}
\]

**中文业务释义：** 供应商最终排序。

因此要看：

# Score Leverage
## 分值杠杆

即某一个评分因素：

> 对总分和最终排名具有多大影响。

---

# 十九、Score Leverage
## 分值杠杆

可以定义工程指标：

\[
\boxed{
ScoreLeverage
=
FactorMaxScore
/
TotalScore
}
\]

**中文业务释义：** 分值杠杆 = 某评分项最高分 ÷ 总分；用于表示该因素对最终排序的潜在影响强度。

例如：

```text
factor_max_score = 20    # 中文：某项最高20分
total_score = 100    # 中文：总分100分
score_leverage = 0.20    # 中文：该项最高可以影响总分20%
```

但 Score Leverage 是工程风险指标，不是单独法律结论。

---

# 二十、D15：证书、奖项进入评分表

附件 9 对：

```text
AAA级信用证书    # 中文：特定信用评价证书
守合同重信用证书    # 中文：特定荣誉 / 信用类证明
行业协会 / 组织颁发的证书、奖项    # 中文：非当然具有法定强制性的证书奖项
```

作为资格条件或评审因素的风险进行了明确关注。

因此评分引擎至少抽：

```text
certificate_name    # 中文：证书名称
award_name    # 中文：奖项名称
issuer_name    # 中文：颁发机构
issuer_type    # 中文：行政机关、法定机构、协会、社会组织、商业机构等
legal_status    # 中文：证书 / 奖项的政策法律属性
project_relation    # 中文：与采购需求 / 履约质量有什么关系
score_value    # 中文：给予多少分
score_leverage    # 中文：对总分的影响强度
```

---

# 二十一、核心心智模型 ⑧
# `Prestige` 不是政府采购评分的天然业务目标

\[
\boxed{
Prestige
\neq
ProcurementQuality
}
\]

**中文业务释义：** 企业“名气大、奖项多、证书漂亮” ≠ 当前采购项目的货物、服务质量或履约能力一定更高。

因此奖项 / 荣誉需要回答：

> 它到底证明什么与当前合同相关的能力？

---

# 二十二、人员评分怎么建模？

人员条件在服务项目中非常常见，例如：

```text
project_manager    # 中文：项目负责人
technical_leader    # 中文：技术负责人
service_staff    # 中文：服务人员
certified_personnel    # 中文：持证专业人员
key_experts    # 中文：关键专家人员
```

人员评分本身不是附件 9 单独的一项 Dxx。

因此必须保持来源纪律：

\[
\boxed{
PersonnelScoring
=
EngineeringReviewObject
}
\]

**中文业务释义：** 人员评分属于评分合规引擎的重要工程审查对象，但不能虚构成附件 9 新增规则。

---

# 二十三、核心心智模型 ⑨
# `PersonIdentity` 与 `PerformanceContribution` 必须分开

人员评分真正应该问：

```text
role_required    # 中文：项目履约是否真的需要这个角色
qualification_relevance    # 中文：人员资格 / 证书与岗位职责有什么关系
experience_relevance    # 中文：人员经验与当前项目任务有什么关系
time_commitment    # 中文：该人员是否真实投入当前项目
replaceability    # 中文：人员更换时怎样保证能力不下降
contract_binding    # 中文：投标承诺人员是否进入合同履约约束
```

因此：

\[
\boxed{
PersonnelScore
\rightarrow
ContractPerformanceLink
}
\]

**中文业务释义：** 人员评分应当能够对应到合同履约能力和实际项目投入，而不是只奖励“履历漂亮”。

---

# 二十四、人员证书 ≠ 人员能力的全部

例如：

```text
certificate_count    # 中文：证书数量
certificate_level    # 中文：证书等级
years_of_experience    # 中文：从业年限
similar_project_count    # 中文：类似项目数量
```

这些都是：

# Proxy Signals
## 代理能力信号

所以：

\[
\boxed{
PersonnelProxy
\neq
CompleteCapability
}
\]

**中文业务释义：** 人员证书、年限、项目数量只是能力代理信号，不应被系统误认为完整的真实履约能力。

---

# 二十五、主观方案评分怎样降低自由裁量？

可以设计：

# Scoring Rubric
## 评分量表

例如对：

```text
应急响应方案    # 中文：供应商针对项目突发事件的响应方案
```

拆成：

```text
trigger_definition    # 中文：是否明确何种情形启动应急机制
response_roles    # 中文：是否明确责任人和组织分工
response_timeline    # 中文：是否明确响应时间节点
resource_plan    # 中文：是否明确需要投入的资源
escalation_path    # 中文：重大事件怎样升级处理
recovery_target    # 中文：恢复目标是否明确
project_specificity    # 中文：是否针对当前项目场景
```

然后每一项都有明确检查点。

---

# 二十六、核心心智模型 ⑩
# `Rubric` 应描述“可观察差异”，而不是“形容词差异”

\[
\boxed{
ObservableDifference
>
AdjectiveDifference
}
\]

**中文业务释义：** “是否包含明确机制、责任人、时间节点、证据”等可观察差异，比“优秀、良好、一般”等单纯形容词差异更可靠。这里的 `>` 表示工程可验证性更高。

---

# 二十七、评分区间必须和采购需求区间对应

例如采购需求已经定义：

```text
响应时间 <= 4小时    # 中文：基本需求上限
```

如果允许更优响应获得评分，可以设置清楚的区间，例如：

```text
0 < response_time <= 1h    # 中文：第一档
1h < response_time <= 2h    # 中文：第二档
2h < response_time <= 4h    # 中文：第三档
```

再映射对应分值。

因此：

\[
\boxed{
DemandInterval
\leftrightarrow
ScoreInterval
}
\]

**中文业务释义：** 采购需求的指标区间，应与评分标准里的分值区间形成可追踪对应关系。

---

# 二十八、核心心智模型 ⑪
# `ScoreDifference` 必须对应 `MeaningfulCapabilityDifference`

如果两个技术 / 服务水平对项目履约没有实质差异，却设置非常细的分差，就可能形成：

# False Precision
## 虚假精度

所以：

\[
\boxed{
ScorePrecision
\neq
BusinessPrecision
}
\]

**中文业务释义：** 分值可以写得非常精细，但不代表业务能力差异真的同样精细。

---

# 二十九、Double Counting
## 重复计分

一个能力可能被多个评分项重复奖励。

例如：

```text
项目经理证书：5分    # 中文：人员能力代理指标1
项目经理从业年限：5分    # 中文：人员能力代理指标2
项目经理类似业绩：5分    # 中文：人员能力代理指标3
项目经理获奖：5分    # 中文：人员声誉代理指标4
```

四项可能实际都在重复评价：

> “项目经理资历”。

所以需要：

# Score Correlation Review
## 评分因素相关性检查

---

# 三十、核心心智模型 ⑫
# `DifferentFactorNames` 不等于 `DifferentCapabilityDimensions`

\[
\boxed{
DifferentFactorNames
\neq
IndependentCapabilityDimensions
}
\]

**中文业务释义：** 评分项名称不同 ≠ 它们真的在评价不同能力；多个指标可能反复奖励同一种能力代理信号。

因此系统要检查：

```text
capability_dimension_id    # 中文：评分项真实对应的能力维度
related_factor_ids    # 中文：评价相同 / 高度相关能力的评分项
combined_weight    # 中文：同一能力维度累计占总分多少
```

---

# 三十一、评分权重为什么必须进入合规分析？

同一个评分因素：

```text
1分    # 中文：低影响
20分    # 中文：高影响
```

对竞争结果的影响完全不同。

所以：

\[
\boxed{
FactorRisk
=
ContentRisk
\times
ScoreLeverage
}
\]

**中文业务释义：** 评分因素风险可以工程化理解为：因素本身的合规风险 × 该因素对总分的影响强度。这里是风险建模思路，不是法律计算公式。

---

# 三十二、核心心智模型 ⑬
# 评分因素合规不只看“有没有问题”，还要看“能改变多少排序”

这就是：

# Ranking Impact
## 排序影响

可以分析：

```text
factor_weight    # 中文：评分项权重
maximum_score_gap    # 中文：供应商在该项最大可能拉开多少分
historical_margin    # 中文：历史同类项目中中标与次中标总分差，可选工程数据
ranking_flip_potential    # 中文：该评分项是否具有改变供应商排序的潜力
```

---

# 三十三、Qualification / Scoring / Contract 三域必须连起来

一个评分因素不应该孤立存在。

理想结构：

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

如果一个高分评分项中标以后完全不需要履行，就会产生：

# Performance Link Risk
## 履约关联风险

---

# 三十四、核心心智模型 ⑭
# `HighScorePromise` 应该进入 `ContractPerformance`

\[
\boxed{
HighScorePromise
\Rightarrow
ContractPerformanceLink
}
\]

**中文业务释义：** 供应商凭某项承诺获得高分后，该承诺应当能够进入合同履约、验收或后续责任约束，而不应只在评标时存在。

这是一个重要工程审查信号；具体如何进入合同仍要结合项目类型和适用制度设计。

---

# 三十五、招标文件没有规定的标准怎么办？

《政府采购法实施条例》第三十四条明确：

> 招标文件中没有规定的评标标准不得作为评审依据。

因此系统必须建立：

\[
\boxed{
EvaluationCriterion
\subseteq
PublishedProcurementDocument
}
\]

**中文业务释义：** 实际使用的评审标准，必须能够在已发布 / 生效的采购文件中找到对应依据。

所以评审记录审计阶段需要检查：

```text
criterion_used    # 中文：评审现场实际使用的标准
criterion_source_clause_id    # 中文：该标准在采购文件中的来源条款
published_before_deadline    # 中文：是否在供应商响应前已经明确公布
ad_hoc_criterion    # 中文：是否属于评审现场临时增加的标准
```

---

# 三十六、核心心智模型 ⑮
# `ExpertPreference` 不能替代 `PublishedCriterion`

\[
\boxed{
ExpertPreference
\neq
EvaluationRule
}
\]

**中文业务释义：** 评审专家个人偏好 ≠ 可以临时变成项目评审标准。

---

# 三十七、价格分也必须进入 Scoring Function

对于采用综合评分法、且适用财政部令第87号价格评分规则的货物服务招标项目，价格分属于确定性计算部分。

概念上：

\[
\boxed{
PriceScore
=
ReferencePrice
/
BidPrice
\times
100
}
\]

**中文业务释义：** 价格得分 = 评标基准价 ÷ 投标报价 × 100；实际工程实现还必须结合适用政府采购政策调整、项目类型和当前有效规则，不能把公式硬编码成永不变化的常量。

如果再乘价格权重：

\[
\boxed{
WeightedPriceContribution
=
PriceScore
\times
PriceWeight
}
\]

**中文业务释义：** 价格对总分的实际贡献 = 价格项得分 × 价格权重。

因此价格分应优先由 Calculator 计算，而不是 LLM 心算。

---

# 三十八、核心心智模型 ⑯
# `DeterministicScore` 应交给 `Calculator`

\[
\boxed{
DeterministicScore
\Rightarrow
CalculatorFirst
}
\]

**中文业务释义：** 价格公式、明确数量计分、明确区间计分等确定性评分，应优先由规则引擎 / 计算器计算，而不是让大语言模型自由生成结果。

---

# 三十九、Policy Adjustment
## 政府采购政策调整与评分必须分层

例如：

```text
政策性价格扣除    # 中文：根据政府采购政策对评审价格进行调整
本国产品相关政策    # 中文：按适用政策执行的价格评审支持
中小企业政策    # 中文：按现行政策落实的扶持规则
```

这些属于：

# Policy Engine
## 政策执行层

不能和采购人自己设计的：

```text
ad_hoc_bonus    # 中文：无明确政策依据的临时加分
```

混在一起。

因此：

\[
\boxed{
PolicyAdjustment
\neq
AdHocBonus
}
\]

**中文业务释义：** 有明确政策依据的政府采购政策调整 ≠ 采购人自行设计的随意加分。

Stage 8 会进一步展开政府采购政策合规。

---

# 四十、Scoring State
## 评分项审查状态

每一个评分项不应该只有：

```text
compliant = true / false    # 中文：简单二元合规标签
```

建议使用：

```text
NOT_REVIEWED    # 中文：尚未审查
STRUCTURE_PARSED    # 中文：评分规则已经成功结构化
RELATION_UNCLEAR    # 中文：与采购需求 / 履约目标的关系不清楚
QUANTIFICATION_RISK    # 中文：存在细化量化不足风险
QUALIFICATION_LEAKAGE    # 中文：疑似把资格条件放入评分
DISCRIMINATION_CANDIDATE    # 中文：疑似命中D02/D03/D05/D15等差别歧视规则
EVIDENCE_INSUFFICIENT    # 中文：证明材料或依据不足
NEEDS_HUMAN_REVIEW    # 中文：需要人工复核
SUPPORTED_FINDING    # 中文：证据充分支持风险发现
CHECKED_NO_FINDING    # 中文：已审查，未发现该类风险
```

所以：

\[
\boxed{
ScoringReviewState
\neq
BinaryComplianceLabel
}
\]

**中文业务释义：** 评分审查状态 ≠ 简单“合规 / 不合规”二选一，而应显式表达解析、候选风险、证据和人工复核状态。

---

# 四十一、Scoring Finding
## 评分标准合规发现项

一个完整 Finding 至少包括：

```text
finding_id    # 中文：评分合规发现项标识
review_domain    # 中文：审查域，这里固定为SCORING评审标准
document_id    # 中文：采购文件标识
document_version    # 中文：采购文件版本
section_id    # 中文：评分章节标识
clause_id    # 中文：评分条款标识
score_item_id    # 中文：评分项标识
factor_name    # 中文：评分因素名称
factor_objective    # 中文：该项想评价的真实能力 / 质量目标
metric_name    # 中文：评分指标
metric_type    # 中文：指标类型
level_definition    # 中文：评分等次定义
score_mapping    # 中文：等次与分值映射
maximum_score    # 中文：最高分
score_leverage    # 中文：该项对总分的潜在影响强度
business_relation    # 中文：与采购需求 / 履约目标的对应关系
qualification_overlap    # 中文：是否与资格条件重叠
substantive_overlap    # 中文：是否与实质性条款重叠
contract_performance_link    # 中文：评分承诺是否进入合同履约
experience_constraints    # 中文：业绩地域、行业、金额等限制
certificate_award_constraints    # 中文：证书 / 奖项要求
personnel_constraints    # 中文：人员评分要求
subjective_rubric_status    # 中文：主观方案评分是否有结构化量表
candidate_rule_ids    # 中文：候选Dxx规则标识
legal_basis_refs    # 中文：适用法律政策依据
policy_snapshot_id    # 中文：项目时点法规快照
evidence_span    # 中文：评分标准原文及定位
risk_level    # 中文：评分风险等级
confidence    # 中文：系统判断置信度
human_review_required    # 中文：是否需要人工复核
recommended_revision    # 中文：评分标准修改建议
```

---

# 四十二、评分标准完整判断流程

\[
\boxed{
ScoringTable
\rightarrow
ScoringFunction
\rightarrow
DemandRelation
\rightarrow
QualificationCrossCheck
\rightarrow
QuantificationCheck
\rightarrow
ScoreMappingCheck
\rightarrow
D01D22Check
\rightarrow
WeightImpact
\rightarrow
ContractLink
\rightarrow
EvidenceGate
\rightarrow
Finding/HumanReview
}
\]

**中文业务释义：** 评分表 → 结构化评分函数 → 与采购需求建立对应 → 与资格条件交叉检查 → 检查细化量化 → 检查指标与分值映射 → 检查D01-D22差别歧视候选 → 评估分值权重影响 → 检查中标后履约关联 → 证据门 → 形成风险发现或升级人工复核。

---

# 四十三、评分标准的“八问模型”

看到任何评分项，至少问八个问题：

```text
1. Why    # 中文：为什么要评这个因素？
2. Relation    # 中文：它与采购需求 / 项目目标有什么关系？
3. Qualification Boundary    # 中文：它是不是资格条件，被错误放入评分？
4. Quantification    # 中文：能不能形成明确等次和可验证指标？
5. Score Mapping    # 中文：等次与分值怎样对应，为什么这样对应？
6. Evidence    # 中文：供应商用什么材料证明？
7. Competition Impact    # 中文：是否不合理偏向某类供应商？
8. Contract Link    # 中文：获得高分的承诺中标后是否真实履行？
```

于是：

\[
\boxed{
ScoringComplianceTest
=
Why
+
Relation
+
QualificationBoundary
+
Quantification
+
ScoreMapping
+
Evidence
+
CompetitionImpact
+
ContractLink
}
\]

**中文业务释义：** 评分合规八问 = 为什么评 + 与需求关系 + 资格边界 + 量化程度 + 分值映射 + 证据 + 竞争影响 + 合同履约关联。

---

# 四十四、核心心智模型 ⑰
# 评分不是“能拉开分差就行”

\[
\boxed{
Differentiation
\neq
LegitimateEvaluation
}
\]

**中文业务释义：** 一个评分项能把供应商分出高低 ≠ 这种区分方式就一定与采购质量、履约能力和公平竞争相符。

---

# 四十五、Hard Negative
## 评分域高难负例

Stage 7 后续训练和 Benchmark 必须重点加入：

```text
HardNegative_RelevantExperience    # 中文：与项目履约能力直接相关、定义合理的业绩评分
HardNegative_QuantifiedServiceLevel    # 中文：明确可量化服务水平差异评分
HardNegative_ProjectSpecificPersonnel    # 中文：关键人员确实与合同履约直接相关的人员评分
HardNegative_StructuredSolutionRubric    # 中文：方案类评分虽然包含专家判断，但评分维度和锚点充分明确
HardNegative_ValidPolicyAdjustment    # 中文：有明确政府采购政策依据的价格 / 评审调整
HardNegative_ObjectiveTechnicalScoring    # 中文：与采购需求直接对应、分值映射清楚的技术评分
```

这些样本用来防止模型变成：

> “只要有业绩 / 人员 / 方案评分就报警。”

---

# 四十六、Counterfactual Pair
## 评分域反事实样本

### Pair A

```text
本市同类项目业绩，每个2分，最高6分    # 中文：地域条件直接进入业绩评分
```

### Pair B

```text
与本项目核心服务内容相近的已完成项目经验，每个2分，最高6分；不限制项目所在地区    # 中文：把地域身份改成履约能力相似性
```

比较：

```text
RegionalPreference    # 中文：地域偏好
CapabilityRelevance    # 中文：能力相关性
```

### Pair C

```text
服务方案优秀得10分、良好得6分、一般得2分    # 中文：只有形容词，没有稳定的观察判据
```

### Pair D

```text
服务方案从组织职责、响应流程、资源配置、风险控制四个维度分别评分，每个维度明确缺项、基本满足、完整满足的观察条件    # 中文：建立结构化方案评分量表
```

比较：

```text
AdjectiveScoring    # 中文：形容词评分
StructuredRubric    # 中文：结构化评分量表
```

### Pair E

```text
注册资本达到5000万元得5分    # 中文：企业规模代理变量进入评分
```

### Pair F

```text
针对本项目配置的专业技术团队满足明确岗位和投入要求得5分    # 中文：直接评价项目履约能力
```

比较：

```text
ScaleProxy    # 中文：企业规模代理变量
DirectCapabilitySignal    # 中文：直接履约能力信号
```

---

# 四十七、Scoring Benchmark
## 评分标准 Benchmark 要测什么？

至少包括：

```text
scoring_factor_detection    # 中文：评分项识别准确率
qualification_leakage_recall    # 中文：资格条件评分化召回率
quantification_risk_recall    # 中文：细化量化不足风险召回率
score_mapping_accuracy    # 中文：指标等次与分值映射判断准确率
D02_scoring_recall    # 中文：特定地域 / 主体业绩奖励评分风险召回
D03_scoring_recall    # 中文：特定行业业绩 / 奖励评分风险召回
D05_scoring_recall    # 中文：企业规模条件评分风险召回
D15_scoring_recall    # 中文：证书 / 奖项评分风险召回
personnel_relevance_accuracy    # 中文：人员评分与履约关系判断准确率
subjective_rubric_accuracy    # 中文：方案主观评分是否具有充分量化锚点的判断准确率
cross_domain_overlap_recall    # 中文：资格 / 实质性 / 评分跨域重复条件识别召回
contract_link_accuracy    # 中文：评分承诺与合同履约关联判断准确率
ranking_impact_accuracy    # 中文：评分因素对竞争排序影响分析准确率
hard_negative_precision    # 中文：合理评分因素不被误报的精确率
human_escalation_accuracy    # 中文：边界型评分问题转人工准确率
evidence_localization_accuracy    # 中文：评分风险原文定位准确率
```

---

# 四十八、核心心智模型 ⑱
# `OverallScoringAccuracy` 不等于 `ScoringReliability`

\[
\boxed{
OverallScoringAccuracy
\neq
PerRiskSliceReliability
}
\]

**中文业务释义：** 评分标准总体准确率 ≠ 对资格评分化、地域业绩、企业规模、证书奖项、主观方案等关键风险切片都可靠。

---

# 四十九、`ProcurementScoringCompliance_V1` 建议目录

```text
ProcurementScoringCompliance_V1/    # 中文：评分标准合规审查工程资产根目录
├── schema/    # 中文：评分结构与发现项Schema
│   ├── scoring_factor.json    # 中文：单个评分因素结构
│   ├── scoring_function.json    # 中文：指标、等次、分值映射函数
│   ├── subjective_rubric.json    # 中文：方案类主观评分量表
│   ├── score_overlap.json    # 中文：资格 / 评分 / 履约跨域重叠结构
│   └── scoring_finding.json    # 中文：评分合规发现项结构
├── analysis/    # 中文：评分合规分析模块
│   ├── demand_relation/    # 中文：评分因素与采购需求关系
│   ├── qualification_crosscheck/    # 中文：资格条件评分化检查
│   ├── quantification/    # 中文：细化量化检查
│   ├── score_mapping/    # 中文：指标等次与分值映射
│   ├── factor_correlation/    # 中文：评分因素重复 / 相关性分析
│   ├── ranking_impact/    # 中文：对最终排序的影响分析
│   └── contract_link/    # 中文：评分承诺与合同履约关联
├── rules/    # 中文：D01-D22在评分域的规则映射
│   ├── D02/    # 中文：特定区域 / 主体业绩奖励
│   ├── D03/    # 中文：特定行业业绩奖励
│   ├── D05/    # 中文：企业规模条件评分
│   ├── D13/    # 中文：与项目实际需要 / 合同履行无关的评分标准
│   └── D15/    # 中文：证书、奖项类评分
├── tests/    # 中文：评分合规测试集
│   ├── positive/    # 中文：明确风险正例
│   ├── hard_negative/    # 中文：合理评分高难负例
│   ├── counterfactual/    # 中文：反事实评分对
│   ├── subjective/    # 中文：方案类评分案例
│   └── cross_domain/    # 中文：资格 / 技术 / 评分跨域案例
└── manifest.json    # 中文：版本、依赖、来源与测试清单
```

---

# 五十、Scoring Factor Schema 第一版

```text
score_item_id    # 中文：评分项标识
project_id    # 中文：采购项目标识
document_id    # 中文：采购文件标识
document_version    # 中文：采购文件版本
section_id    # 中文：评分章节标识
clause_id    # 中文：评分条款标识
factor_name    # 中文：评分因素名称
factor_objective    # 中文：评价目标
capability_dimension_id    # 中文：真实评价的能力维度标识
metric_name    # 中文：评价指标
metric_type    # 中文：指标类型
metric_unit    # 中文：指标单位
level_definition    # 中文：指标等次定义
score_mapping    # 中文：等次到分值的映射
maximum_score    # 中文：最高分
minimum_score    # 中文：最低分
factor_weight    # 中文：该因素占总评分的权重
score_leverage    # 中文：该因素对总分的最大影响强度
evidence_required    # 中文：供应商证明材料
demand_relation    # 中文：与采购需求 / 项目目标的对应关系
qualification_overlap    # 中文：是否与资格条件重叠
substantive_overlap    # 中文：是否与实质性条款重叠
contract_performance_link    # 中文：是否进入合同履约
region_constraint    # 中文：地域限制
industry_constraint    # 中文：行业限制
experience_constraint    # 中文：业绩限制
award_constraint    # 中文：奖项限制
certificate_constraint    # 中文：证书限制
personnel_constraint    # 中文：人员条件
subjective_component    # 中文：是否包含主观评价成分
rubric_id    # 中文：主观评价对应的结构化评分量表标识
candidate_rule_ids    # 中文：候选Dxx规则
parse_confidence    # 中文：评分条款解析置信度
```

---

# 五十一、Subjective Rubric Schema 第一版

```text
rubric_id    # 中文：评分量表标识
score_item_id    # 中文：对应评分项
dimension_id    # 中文：评价维度标识
dimension_name    # 中文：评价维度名称
business_objective    # 中文：该维度服务的真实采购目标
observable_anchors    # 中文：可观察、可验证的评分锚点
level_0_definition    # 中文：0分 / 最低档的明确条件
level_1_definition    # 中文：第一档条件
level_2_definition    # 中文：第二档条件
level_3_definition    # 中文：最高档条件
score_mapping    # 中文：各等级对应分值
missing_element_rule    # 中文：缺项扣分规则
contradiction_rule    # 中文：自相矛盾或不响应需求的处理规则
evidence_required    # 中文：需要核验的响应内容
reviewer_discretion_boundary    # 中文：专家自由裁量边界
human_review_required    # 中文：是否需要进一步人工校核
```

---

# 五十二、本阶段最重要的 18 个核心心智模型

> **心智模型 ①：`Scorable ≠ CompliantScoringFactor`。一个条件可以被打分，不代表它当然适合作为合规评分因素。**

> **心智模型 ②：`ScoringDesign = DecisionDesign`。评分标准设计，本质上是在设计最终竞争结果的决策机制。**

> **心智模型 ③：`NumericScore ≠ MeaningfulQuantification`。有数字不代表真正细化量化。**

> **心智模型 ④：`SameEvidence → SameScoreRule`。面对同样证据，评分规则应尽可能导向稳定一致的分值。**

> **心智模型 ⑤：`SubjectiveEvaluation ≠ ArbitraryScoring`。方案类评审可以有专业判断，但不能没有明确边界。**

> **心智模型 ⑥：`QualificationCondition ≠ ScoringFactor`。资格条件不能换个位置继续作为评分因素。**

> **心智模型 ⑦：`CrossSectionDuplicate ≠ HarmlessDuplicate`。跨资格、评分、实质性条款重复出现的同一条件可能具有完全不同的业务风险。**

> **心智模型 ⑧：`PastPerformance → CapabilityDimension → ExpectedContractPerformance`。业绩评分应能解释它怎样证明未来履约能力。**

> **心智模型 ⑨：`MoveFromGateToScore ≠ RiskRemoved`。把规模、地域等问题从资格条件移到评分表，不代表风险消失。**

> **心智模型 ⑩：`Prestige ≠ ProcurementQuality`。企业荣誉和名气不是采购质量的天然替代变量。**

> **心智模型 ⑪：`PersonnelScore → ContractPerformanceLink`。人员得分应能回到真实投入和合同履约。**

> **心智模型 ⑫：`ObservableDifference > AdjectiveDifference`。可观察、可验证的评分差异比“优秀、良好、一般”更可靠。**

> **心智模型 ⑬：`ScorePrecision ≠ BusinessPrecision`。分值写得精细，不代表业务差异真的同样精细。**

> **心智模型 ⑭：`DifferentFactorNames ≠ IndependentCapabilityDimensions`。评分项名称不同，不代表评价的是不同能力。**

> **心智模型 ⑮：`FactorRisk = ContentRisk × ScoreLeverage`。评分因素风险既要看内容问题，也要看它能影响总分多少。**

> **心智模型 ⑯：`HighScorePromise ⇒ ContractPerformanceLink`。凭承诺拿高分后，应能进入合同履约或验收约束。**

> **心智模型 ⑰：`ExpertPreference ≠ EvaluationRule`。专家个人偏好不能替代采购文件已经公布的评审标准。**

> **心智模型 ⑱：`DeterministicScore ⇒ CalculatorFirst`。确定性评分优先交给规则 / 计算器，而不是LLM自由生成。**

---

# 五十三、把整个评分合规判断压成一张工程图

```text
Scoring Table / Criteria
# 中文：评分表 / 评审标准
↓
Scoring Function
# 中文：把自然语言评分条款结构化成指标、等次、分值和证据
↓
Demand Relation
# 中文：评分项与采购需求 / 项目目标是否直接相关
↓
Qualification Cross-check
# 中文：检查是否把资格条件重新放入评分表
↓
Quantification Check
# 中文：检查评分因素是否真正细化和量化
↓
Score Mapping Check
# 中文：检查指标等次与对应分值是否匹配
↓
Experience / Awards / Personnel
# 中文：分别检查业绩、奖项和人员评分
↓
D01-D22 Rule Check
# 中文：检查地域、行业、规模、证书奖项等差别歧视候选
↓
Weight / Leverage
# 中文：评分权重和对排序的影响强度
↓
Contract Link
# 中文：高分承诺是否进入合同履约
↓
Evidence Gate
# 中文：评分原文、需求关系、法源和证据是否完整
↓
Supported Finding / Unresolved-Borderline
# 中文：证据支持风险项 / 未解决或边界问题
↓
Remediation / Human Review
# 中文：修改建议 / 人工复核
```

---

# 五十四、脑中最后只留一句

> **政府采购评分标准合规的本质，不是“评分项越细越好”，也不是“只要能拉开分数就行”，而是每一个评分因素都必须能够解释它为什么与采购需求、货物服务质量或履约能力相关，怎样通过可观察指标形成清楚的等次和分值映射，是否与资格门槛、实质性条款和合同履约边界一致，以及它会不会通过地域、行业、企业规模、证书奖项、人员履历或模糊主观评价不合理地改变供应商竞争排序。**

---

# 第十一课 · 第 7 阶段掌握测试

现在不回看正文，你应该能够解释：

```text
Scorable 为什么不等于 Compliant Scoring Factor？    # 中文：一个条件“能打分”为什么不代表“应该打分”？
政府采购评分标准为什么可以看成 Decision Function？    # 中文：评分设计为什么会直接改变竞争结果？
Numeric Score 为什么不等于 Meaningful Quantification？    # 中文：写了10分、7分、4分为什么仍可能没有真正量化？
Same Evidence → Same Score Rule 想解决什么问题？    # 中文：为什么相同证据应尽可能得到稳定一致的评分结果？
Subjective Evaluation 和 Arbitrary Scoring 的边界在哪里？    # 中文：方案评分怎样保留专业判断，同时限制无边界自由裁量？
为什么 Qualification Condition 不能继续成为 Scoring Factor？    # 中文：资格条件评分化怎样被识别？
D02 / D03 与业绩评分怎样连接？    # 中文：为什么地域业绩、行业业绩和真正履约能力相似性必须分开？
D05 为什么不仅要检查资格门槛，也要检查评分表？    # 中文：企业规模条件挪到评分项为什么风险没有自动消失？
D15 与证书、奖项评分怎样连接？    # 中文：证书奖项为什么必须解释其法律属性、颁发主体和项目关系？
人员评分为什么必须有 Contract Performance Link？    # 中文：关键人员拿高分以后为什么需要进入真实履约约束？
什么是 Structured Rubric？    # 中文：方案评分怎样用可观察锚点替代单纯“优秀、良好、一般”？
Demand Interval 和 Score Interval 为什么要对应？    # 中文：采购需求指标区间与评分区间怎样形成可追踪关系？
Score Precision 为什么不等于 Business Precision？    # 中文：过度精细的分值为什么可能制造虚假精度？
什么是 Double Counting？    # 中文：不同评分项怎样可能重复奖励同一种能力？
什么是 Score Leverage？    # 中文：为什么一个问题评分项占20分比占1分更值得关注？
为什么 High Score Promise 应连接 Contract Performance？    # 中文：评标时获得的高分承诺怎样防止中标后失效？
为什么招标文件中没有规定的评审标准不能临时加入？    # 中文：Expert Preference 为什么不等于 Evaluation Rule？
为什么确定性评分应该 Calculator First？    # 中文：价格、数量、区间等规则为什么不应让LLM心算？
Policy Adjustment 与 Ad Hoc Bonus 有什么区别？    # 中文：合法政府采购政策调整与采购人随意加分怎样区分？
为什么 Overall Scoring Accuracy 不等于 Per-risk Slice Reliability？    # 中文：评分模型为什么必须分别测资格评分化、地域业绩、规模、证书奖项、方案评分等关键切片？
```

如果这些能够完整解释：

\[
\boxed{
第十一课第7阶段真正掌握
}
\]

---

# 下一阶段：第十一课 · 第 8 阶段
# 政府采购政策合规：本国产品、中小企业、绿色采购、创新、进口产品
## 怎样区分“有明确政策依据的政府采购支持机制”和“采购人自行设置的不合理差别待遇”？

下一阶段将重点建立：

# `ProcurementPolicyCompliance_V1`

最重要的边界：

\[
\boxed{
PolicyPreference
\neq
IllegalDiscrimination
}
\]

**中文业务释义：** 有明确法律政策依据的政府采购支持 / 优惠机制 ≠ 采购人自行设置的非法差别歧视待遇。
