# 第十一课 · 第 13 阶段
# SFT / Hard Cases / Counterfactual Training：训练真正的合规判断能力
## 怎样让模型学习“为什么构成风险、为什么不构成风险、哪个关键事实变化会让结论翻转”，而不是背关键词？

第 12 阶段我们已经建立：

\[
\boxed{
RelevantLaw
\neq
ApplicableLaw
}
\]

**中文业务释义：** 语义上相关的法规政策 ≠ 当前采购项目真正适用的法规政策。

并建立：

\[
\boxed{
LegalQuery
\rightarrow
PolicyRegistry
\rightarrow
HybridRetrieval
\rightarrow
TemporalResolver
\rightarrow
JurisdictionResolver
\rightarrow
ApplicabilityDecision
\rightarrow
CitationValidator
}
\]

**中文业务释义：** 法律问题 → 法规政策注册表 → 混合检索 → 时间适用解析 → 辖区适用解析 → 形成适用性判断 → 验证引用是否真正支持结论。

到这里我们已经有：

```text
ProcurementComplianceDataset_V1    # 中文：可靠的采购文件结构化事实底座
ProcurementComplianceEngine_V1    # 中文：规则、计算、RAG、LLM和人工协作的混合合规引擎
ProcurementLegalRAG_V1    # 中文：能够解析法规版本、时间、辖区和引用支持的法规RAG
```

现在进入一个非常容易被做错的环节：

> **到底应该把什么东西“训练进模型”？**

很多项目会走向：

```text
收集“违规条款”    # 中文：只收明显风险文本
→
给每条标“违规 / 不违规”    # 中文：压成二分类
→
直接做SFT    # 中文：直接监督微调
→
模型学会几个高频词    # 中文：最后退化为关键词报警器
```

最终得到的往往不是“政府采购合规判断模型”，而是“本地、品牌、注册资本、证书、业绩”等高频词报警器。

所以本阶段第一条核心边界正式锁定：

\[
\boxed{
ComplianceTraining
\neq
KeywordMemorization
}
\]

**中文业务释义：** 合规训练 ≠ 让模型背住高风险关键词；真正需要训练的是规则适用条件、业务语境、例外、证据和结论翻转边界。

本阶段最终形成：

# `ProcurementComplianceLM_V1-RC`

其中：

```text
RC = Release Candidate    # 中文：发布候选版本，已经进入严格评测阶段，但还不是最终生产正式版
```

---

# 一、Stage 13 真正要训练的是什么？

最核心对象不是：

```text
risk_keyword    # 中文：风险关键词
```

而是：

# Decision Boundary
## 判断边界

也就是：

> **哪一个关键事实变化以后，正确结论应该改变？**

例如：

```text
“投标前必须在本地设分支机构”    # 中文：前置市场准入条件，可能形成地域限制
“中标后应根据现场服务需要配置能够满足响应时限的服务资源”    # 中文：履约阶段要求，业务性质已经不同
```

两句话都可能出现“本地 / 现场服务”概念，真正决定结论的不是关键词，而是：

```text
timing    # 中文：投标前还是中标后
business_role    # 中文：资格门槛还是履约义务
necessity    # 中文：是否存在项目实际履约必要性
scope    # 中文：要求是否过度
competition_impact    # 中文：是否不合理压缩潜在供应商范围
evidence    # 中文：采购需求和履约证据是否支持
```

所以：

\[
\boxed{
GoodComplianceModel
=
LearnDecisionBoundary
\neq
MemorizeSurfaceWords
}
\]

**中文业务释义：** 好的合规模型 = 学会判断边界 ≠ 记住表面词语。

---

# 二、核心心智模型 ①：Keyword 不是 Label

\[
\boxed{
Keyword
\neq
ComplianceLabel
}
\]

**中文业务释义：** 出现某个高风险词 ≠ 可以直接把样本标成风险。

例如：

```text
“不得以供应商所在地限制供应商参加政府采购活动”    # 中文：禁止性规则表达，不是在设置地域准入门槛
```

如果训练数据只看“供应商所在地”就标风险，模型会把禁止违规的句子本身也学成风险。

---

# 三、四类核心训练样本

```text
HARD_POSITIVE    # 中文：表达隐晦、不含明显关键词，但实质可能形成风险的高难正例
HARD_NEGATIVE    # 中文：表面很像风险，但结合业务角色、政策授权、时点或例外后不应直接报风险的高难负例
COUNTERFACTUAL_PAIR    # 中文：只改变一个关键事实，正确结论随之保持或翻转的反事实样本对
BOUNDARY_CASE    # 中文：处于规则边界，需要补证据或人工判断的样本
```

普通明显正例仍然需要，但真正决定模型是不是“只会背词”的，是 Hard Negative、Counterfactual 和 Boundary Case。

---

# 四、核心心智模型 ②：训练价值来自边界信息

\[
\boxed{
TrainingValue
\propto
BoundaryInformation
}
\]

**中文业务释义：** 一个样本越能帮助模型理解“结论为什么在这里翻转”，训练价值通常越高。这里的 `\propto` 表示工程直觉上的正相关，不是严格统计定律。

明显样本：

```text
“只允许本地企业参加”    # 中文：风险信号非常直接
```

当然要有，但如果训练集几乎全是这种样本，模型很快会学会词表，却学不会边界。

---

# 五、Hard Positive：高难正例

典型特征：

```text
no_obvious_keyword    # 中文：没有明显“本地、品牌、注册资本”等关键词
distributed_evidence    # 中文：风险事实分散在多个条款、表格或附件
semantic_proxy    # 中文：使用代理条件间接形成限制
cross_domain_effect    # 中文：只有把资格、技术、评分等跨域连接后才看出风险
market_fingerprint    # 中文：参数组合可能隐性指向特定产品或供应商
```

例如没有写任何品牌名称，但一组非常具体的接口、尺寸、专有组件和兼容条件组合后，只剩极少数甚至单一产品路径。

\[
\boxed{
NoExplicitBrand
\neq
NoProductDirectionRisk
}
\]

**中文业务释义：** 没有出现品牌名称 ≠ 一定不存在特定产品指向风险。

---

# 六、Hard Negative：高难负例

Hard Negative 不是随便找一句完全正常的话，而是“和风险样本非常像，但存在一个合法、合理或业务角色上的关键差别”。

```text
authorized_policy_preference    # 中文：有明确制度依据的中小企业、本国产品等政策支持
post_award_performance_requirement    # 中文：中标后的履约义务，而不是投标前市场准入门槛
law_text_quoting_prohibition    # 中文：引用“不得设置某条件”的禁止规则
valid_exception    # 中文：确实满足明确例外条件
fact_missing    # 中文：证据不足，只能UNRESOLVED，不能直接判风险
```

---

# 七、核心心智模型 ③：Hard Negative 决定误报率

\[
\boxed{
WeakHardNegatives
\Rightarrow
HighFalsePositiveRisk
}
\]

**中文业务释义：** 高难负例不足 ⇒ 模型容易把“看起来像风险”的正常或合法场景也报成问题，误报率会上升。

---

# 八、Counterfactual Pair：反事实样本对

反事实样本对要求尽量只改变一个关键变量。

### Pair A：投标前市场准入

```text
供应商投标时必须已经在采购人所在地设有分支机构。    # 中文：把本地机构作为投标前条件
```

### Pair B：中标后履约能力

```text
中标供应商应根据项目现场服务需要配置能够满足响应时限的服务资源。    # 中文：围绕履约结果表达，不要求投标前已有本地机构
```

主要改变：

```text
timing    # 中文：投标前 → 中标后
business_function    # 中文：市场准入 → 履约能力
```

模型应该学到：不能只看到“服务地点 / 本地服务”就输出同一结论。

---

# 九、核心心智模型 ④：反事实训练必须控制变量

\[
\boxed{
CounterfactualPair
=
SameContext
+
OneCriticalChange
+
ExpectedDecisionRelation
}
\]

**中文业务释义：** 反事实样本对 = 尽量保持其余背景不变 + 只改变一个关键事实 + 明确预期结论应保持、翻转或进入不确定状态。

如果一次同时改变项目类型、条款位置、时间、法源、金额和主体，就很难知道模型究竟学到了哪个判断边界。

---

# 十、Boundary Case：边界案例

Boundary Case 不是“标注员不知道答案”，而是规则本身要求结合事实、必要性、市场情况、证据或专业判断，不能仅凭一句文本直接二分。

例如某项技术参数非常具体，真正需要继续看：

```text
functional_need    # 中文：采购功能目标
market_alternatives    # 中文：市场可替代方案
compatibility_need    # 中文：兼容性要求是否真实存在
evidence_quality    # 中文：采购需求论证是否充分
competition_impact    # 中文：对潜在竞争的实际影响
```

正确标签可能是：

```text
HUMAN_REVIEW_REQUIRED    # 中文：需要人工专业复核
EVIDENCE_INSUFFICIENT    # 中文：证据不足，不能形成确定结论
```

而不是硬塞成 `0` 或 `1`。

---

# 十一、核心心智模型 ⑤：合规标签不能只有二分类

\[
\boxed{
ComplianceLabel
\neq
\{0,1\}
}
\]

**中文业务释义：** 政府采购合规标签不应该只有“违规 / 不违规”两个值。

推荐至少：

```text
SUPPORTED_FINDING    # 中文：现有证据和适用规则支持风险发现
CHECKED_NO_FINDING    # 中文：完整检查后未发现该类风险
NOT_APPLICABLE    # 中文：该规则对当前项目或条款不适用
EVIDENCE_INSUFFICIENT    # 中文：证据不足，无法形成可靠结论
HUMAN_REVIEW_REQUIRED    # 中文：需要人工专业复核
PARSER_OR_DATA_FAILURE    # 中文：底层数据失败，不能伪装成合规判断
```

---

# 十二、模型不应该学习“现行法规全文记忆”

Stage 12 已经建立：

\[
\boxed{
PolicyUpdate
\neq
ModelRetraining
}
\]

**中文业务释义：** 法规更新 ≠ 必须重新训练模型。

因此 Stage 13 训练目标不是把所有现行政府采购法规塞进模型参数，而是训练模型：

```text
read_structured_fact    # 中文：理解结构化采购事实
read_policy_context    # 中文：理解系统提供的适用法规上下文
map_fact_to_rule    # 中文：把事实与候选规则条件对应
judge_semantic_relation    # 中文：判断必要性、相关性、等效性等语义关系
check_missing_evidence    # 中文：识别还缺什么事实或证据
respect_exception    # 中文：正确处理例外
abstain_when_needed    # 中文：证据不足时拒绝武断结论
produce_auditable_output    # 中文：输出可审计的结构化判断
```

---

# 十三、核心心智模型 ⑥：训练 How to Judge，而不是死记 Current Law

\[
\boxed{
TrainJudgmentBehavior
>
MemorizeCurrentPolicyText
}
\]

**中文业务释义：** 对长期可维护的合规模型而言，训练“如何基于给定规则和证据判断”比让模型死记当前政策文本更重要。这里的 `>` 表示工程优先级。

---

# 十四、哪些东西不应该交给 SFT 学？

```text
abnormal_low_price_formula    # 中文：异常低价明确阈值公式
additional_purchase_ratio    # 中文：明确比例计算
price_score_formula    # 中文：价格分公式
effective_date_comparison    # 中文：明确生效日期比较
policy_status_lookup    # 中文：法规当前状态查询
exact_rule_predicate    # 中文：能够完全规则化的明确结构条件
```

这些原则上优先留在 Rule / Calculator / Policy Resolver。

---

# 十五、核心心智模型 ⑦：Can Train 不等于 Should Train

\[
\boxed{
CanTrain
\neq
ShouldTrain
}
\]

**中文业务释义：** 某个任务技术上可以让 LLM 学会 ≠ 工程上就应该让 LLM 负责。

如果 Calculator 可以 100% 重放、可解释、可测试地算出来，就没有必要把主要责任交给概率模型。

---

# 十六、SFT 在这里到底训练什么？

# Supervised Fine-Tuning
## 监督微调

Stage 13 重点训练：

```text
task_understanding    # 中文：理解当前合规子任务
structured_input_following    # 中文：正确读取项目事实、规则和证据字段
semantic_relation_judgment    # 中文：判断需求与条件之间的语义关系
exception_mapping    # 中文：把项目事实映射到候选例外
evidence_grounding    # 中文：只基于给定证据形成判断
abstention_behavior    # 中文：证据不足时输出无法判断或转人工
structured_output    # 中文：稳定输出Finding Schema / Judgment Schema
revision_suggestion    # 中文：在证据充分时给出贴近采购文件的修改建议
```

---

# 十七、核心心智模型 ⑧：一个 SFT 样本应该是一项可审计任务

错误样本：

```text
instruction = “请审查整份采购文件”    # 中文：任务边界过宽
output = “总体来看基本合规，但部分条款需要关注”    # 中文：输出不可验证、不可定位
```

推荐样本：

```text
task_type = BUSINESS_RELEVANCE_JUDGMENT    # 中文：业务相关性判断
project_context = ...    # 中文：项目背景
requirement = ...    # 中文：被判断的独立业务要求
candidate_rule = ...    # 中文：候选规则
applicable_policy_context = ...    # 中文：当前适用法源上下文
evidence_spans = ...    # 中文：采购文件原文证据
target = structured_judgment    # 中文：结构化Gold判断
```

---

# 十八、SFT Training Unit 第一版

```text
sample_id    # 中文：训练样本唯一标识
task_type    # 中文：语义判断、例外匹配、证据判断、人工升级等任务类型
project_family_id    # 中文：项目族标识，用于防止同项目泄漏到训练集和测试集
document_version_id    # 中文：采购文件版本
policy_snapshot_id    # 中文：标注时使用的法规政策快照
source_clause_ids    # 中文：来源条款
source_requirement_ids    # 中文：来源独立要求
candidate_rule_ids    # 中文：候选D01-D22或其他规则
project_context    # 中文：采购标的、采购方式、预算级次等必要上下文
applicable_policy_context    # 中文：由Stage12解析出的适用法源上下文
evidence_spans    # 中文：采购文件原文证据
market_or_business_evidence    # 中文：必要时提供市场、技术、履约事实
gold_decision    # 中文：专家Gold结论
gold_reason_summary    # 中文：可审计简要判断理由，不要求保存私有思维过程
gold_evidence_refs    # 中文：支持Gold结论的证据
exception_state    # 中文：是否存在例外及其状态
missing_fact_refs    # 中文：如无法判断，缺少什么事实
human_review_required    # 中文：Gold是否要求人工复核
hard_case_type    # 中文：普通、Hard Positive、Hard Negative、Counterfactual、Boundary
pair_id    # 中文：如属于反事实样本对，记录Pair ID
split_group_id    # 中文：数据切分时必须保持同组样本在同一Split
```

---

# 十九、核心心智模型 ⑨：PolicySnapshotID 必须进入训练样本

\[
\boxed{
TrainingLabel
=
Facts
+
ApplicablePolicySnapshot
}
\]

**中文业务释义：** 合规训练标签 = 项目事实 + 当时适用法规政策快照共同决定。

否则同一句条款在不同政策时点可能得到不同结论，但数据里看起来却像“标注冲突”。

---

# 二十、当前政策样例为什么必须带时间上下文？

Stage 12 已校对的当前时点示例包括：

```text
财库〔2026〕2号    # 中文：自2026年2月1日起施行
财库〔2026〕12号    # 中文：自2026年10月1日起施行；在2026年9月20日快照日尚未生效
国办发〔2025〕34号    # 中文：自2026年1月1日起施行
```

训练样本不应该只保存 `text + label`，而应保存：

```text
event_time    # 中文：业务法律事件时间
policy_snapshot_id    # 中文：当时适用法规快照
applicability_context    # 中文：Stage12的适用性解析结果
```

模型需要学习“使用适用性上下文”，而不是死记这些日期。

---

# 二十一、Hard Negative 类型 1：Polarity Trap

### 风险样本

```text
供应商须提供本地区类似项目业绩。    # 中文：直接把本地区业绩作为要求
```

### 高难负例

```text
不得将供应商具有本地区类似项目业绩作为资格条件或者评分条件。    # 中文：禁止设置本地区业绩条件
```

两者都有“本地区类似项目业绩”，模型真正要学的是：

```text
polarity    # 中文：要求、禁止、允许、例外
business_function    # 中文：资格、评分还是法规说明
```

---

# 二十二、核心心智模型 ⑩：Same Words 不等于 Same Meaning

\[
\boxed{
SameWords
\neq
SameComplianceMeaning
}
\]

**中文业务释义：** 相同关键词 ≠ 相同合规含义；否定、业务角色、时点和上下文都会改变判断。

---

# 二十三、Hard Negative 类型 2：Authorized Policy

### 风险候选

```text
采购人自行规定：仅小型企业可以参加，但没有任何适用政策依据。    # 中文：采购人自行设置企业规模限制的候选风险
```

### 高难负例

```text
项目根据当前适用中小企业政府采购政策依法执行专门面向中小企业采购或价格评审优惠。    # 中文：有明确政策依据的政府采购支持机制
```

\[
\boxed{
AuthorizedPolicyPreference
\neq
PurchaserCreatedDiscrimination
}
\]

**中文业务释义：** 法规政策授权的差异化支持 ≠ 采购人自行设置的不合理差别待遇。

---

# 二十四、Hard Negative 类型 3：Pre-award vs Post-award

```text
投标人必须在投标截止日前已在项目所在地设有常驻服务机构。    # 中文：把本地机构作为投标前准入条件
中标供应商应在合同履行阶段保证2小时内到达项目现场，并自行安排满足该要求的服务资源。    # 中文：围绕履约结果设置响应时限，并不直接要求投标前已有本地机构
```

模型应该重点理解：

```text
timing    # 中文：投标前 / 中标后
means_vs_outcome    # 中文：限定具体组织形式 / 只规定履约结果
business_necessity    # 中文：响应时限与项目实际需要是否匹配
```

\[
\boxed{
PreAward
\neq
PostAward
}
\]

**中文业务释义：** 投标前市场准入要求与中标后合同履约要求属于不同业务阶段，不能混为一谈。

---

# 二十五、Hard Negative 类型 4：Specific ≠ Discriminatory

技术要求具体，不代表一定不合理。训练样本要覆盖：

```text
specific_but_necessary    # 中文：参数具体，但有采购功能和履约证据支撑
specific_and_unjustified    # 中文：参数具体，同时缺乏功能必要性且显著压缩竞争
equivalent_path_available    # 中文：存在能够达到同一功能目标的其他技术路径
equivalent_path_blocked    # 中文：条款无必要地排除了等效技术路径
```

\[
\boxed{
Specific
\neq
Discriminatory
}
\]

**中文业务释义：** 技术参数具体 ≠ 自动构成差别歧视；真正判断需要功能目标、必要性、市场替代性和竞争影响证据。

---

# 二十六、Hard Positive 类型 1：Proxy Restriction

风险不一定直接写“大企业优先”，它可能使用：

```text
scale_linked_credit    # 中文：与企业规模高度相关的第三方信用或评价条件
excessive_financial_indicator    # 中文：与项目实际履约能力不成比例的财务指标
region_specific_award    # 中文：只接受特定地区颁发的奖项或荣誉
organization_form_proxy    # 中文：通过组织形式、股权结构等间接限制主体
```

模型要学：条款表面写了什么字段，不如它实际上筛掉谁重要。

\[
\boxed{
SurfaceFeature
\neq
CompetitionEffect
}
\]

**中文业务释义：** 条款表面字段 ≠ 对市场竞争的实际影响。

---

# 二十七、Hard Positive 类型 2：Cross-clause Composition

```text
设备必须满足接口A。    # 中文：单独看可能合理
必须兼容现有模块B。    # 中文：单独看也可能合理
核心部件尺寸、通信协议和安装方式全部限定为一组非常特殊组合。    # 中文：组合后可能显著缩小市场范围
```

单条看都不一定足以报风险，组合以后才可能形成特定产品路径。

\[
\boxed{
RiskUnit
\neq
SingleSentence
}
\]

**中文业务释义：** 风险分析单元 ≠ 永远是一句话；有些风险必须跨条款、跨表格组合后识别。

---

# 二十八、Counterfactual Axis：反事实训练轴

```text
TIMING_AXIS    # 中文：投标前 ↔ 中标后 ↔ 履约阶段
BUSINESS_ROLE_AXIS    # 中文：资格条件 ↔ 实质性要求 ↔ 评分因素 ↔ 合同义务
JURISDICTION_AXIS    # 中文：中央 / 地方、不同地区规则范围
POLICY_TIME_AXIS    # 中文：生效前 ↔ 生效后
EXCEPTION_AXIS    # 中文：不满足例外 ↔ 满足例外
EVIDENCE_AXIS    # 中文：无证据 ↔ 有充分证据
MARKET_AXIS    # 中文：多种等效方案 ↔ 客观唯一方案
SCOPE_AXIS    # 中文：必要最低范围 ↔ 过度范围
OPERATOR_AXIS    # 中文：< ↔ <=、必须 ↔ 优先等逻辑边界
POLARITY_AXIS    # 中文：要求 ↔ 禁止 ↔ 允许
```

建议每个 Pair 保存：

```text
pair_id    # 中文：反事实样本对标识
changed_axis    # 中文：只改变了哪一个判断轴
old_value    # 中文：改变前值
new_value    # 中文：改变后值
expected_label_shift    # 中文：预期结论怎样变化
why_label_changed    # 中文：可审计的简要翻转原因
```

---

# 二十九、反事实例子：Manufacturer Authorization

```text
对非进口货物，要求供应商必须取得制造商授权才能参加投标。    # 中文：需要进入制造商授权限制规则审查的典型场景
```

与：

```text
项目明确属于依法采购进口产品的情形，并提供当前适用规则所要求的相关文件。    # 中文：存在进口产品这一关键事实，需要按适用规则和例外继续判断
```

这里改变的是：

```text
import_status_and_exception_context    # 中文：产品是否属于进口产品及相关例外上下文
```

模型不能看到“制造商授权”四个字就无条件输出同一标签。

---

# 三十、反事实例子：异常低价——训练模型尊重 Calculator

```text
calculator_result = TRIGGERED    # 中文：确定性计算器已经确认命中异常低价数值触发条件
```

模型正确输出应是“需要启动异常低价审查”，而不是“直接无效”。

另一个样本：

```text
calculator_result = NOT_TRIGGERED    # 中文：确定性数值条件均未命中
professional_judgment_evidence = PRESENT    # 中文：仍存在基于质量或履约风险的专业判断证据
```

模型应理解：没有数值触发 ≠ 绝对不存在异常低价审查可能。

\[
\boxed{
LLM
\neq
CalculatorReplacement
}
\]

**中文业务释义：** LLM ≠ Calculator 的替代品；训练应强化“读取和尊重确定性工具结果”。

---

# 三十一、反事实例子：Policy Effective Date

不推荐让模型死记“某文号 = 某日期”。推荐给模型：

```text
policy_status = PUBLISHED_NOT_EFFECTIVE    # 中文：Stage12解析器已确认尚未生效
project_event_time = 2026-09-20    # 中文：当前业务事件发生在施行前
```

另一个样本：

```text
policy_status = APPLICABLE    # 中文：Stage12解析器已确认当前项目时点和范围满足适用条件
```

要求模型改变判断。

\[
\boxed{
TrainPolicyContextUse
\neq
MemorizePolicyDate
}
\]

**中文业务释义：** 训练模型使用 Policy Resolver 提供的法规上下文 ≠ 训练模型死记政策日期。

---

# 三十二、Gold Label Schema

```text
gold_state    # 中文：SUPPORTED_FINDING / CHECKED_NO_FINDING / UNRESOLVED等最终Gold状态
gold_rule_ids    # 中文：专家确认关联规则
gold_legal_propositions    # 中文：样本真正需要证明的法律或政策命题
gold_evidence_refs    # 中文：采购文件事实证据
gold_policy_refs    # 中文：适用法源证据
gold_exception_result    # 中文：例外检查结果
gold_missing_fact_refs    # 中文：如果无法判断，缺什么事实
gold_human_review_reason    # 中文：为什么必须人工复核
gold_revision_direction    # 中文：如适用，采购文件应往什么方向修正
```

\[
\boxed{
GoldLabel
=
Evidence
+
ApplicableRule
+
Adjudication
}
\]

**中文业务释义：** Gold 标签 = 原文证据 + 当前适用规则 + 必要专家裁决。

---

# 三十三、标注员需要什么材料？

不能只给一条孤立 Clause。至少按任务提供：

```text
project_context    # 中文：项目背景
document_role    # 中文：条款属于资格、技术、评分、合同等哪个位置
neighbor_context    # 中文：必要前后文
cross_reference_context    # 中文：被引用附件、表格或章节
policy_snapshot    # 中文：标注时适用法规政策快照
candidate_rules    # 中文：候选规则
evidence_spans    # 中文：原文证据
annotation_guideline_version    # 中文：当前标注规范版本
```

---

# 三十四、Annotation Guideline 必须版本化

```text
guideline_id    # 中文：标注规范标识
guideline_version    # 中文：标注规范版本
effective_from    # 中文：该版本从何时开始用于新标注
rule_mapping_version    # 中文：关联D01-D22等规则集版本
policy_snapshot_baseline    # 中文：默认法规政策基线
changed_definitions    # 中文：本次规范修改了哪些标签定义
migration_policy    # 中文：旧标注是否需要重审或迁移
```

\[
\boxed{
LabelChange
\neq
AnnotatorError
}
\]

**中文业务释义：** 同类样本前后标签变化 ≠ 一定是标注员错误；可能是规则版本、政策快照或标注规范变化。

---

# 三十五、双人标注 + Adjudication

高风险 / Boundary Case 建议使用：

```text
annotator_A    # 中文：第一位业务或法规标注员
annotator_B    # 中文：第二位独立标注员
disagreement_state    # 中文：两人是否存在分歧
adjudicator    # 中文：负责裁决的高级专家
adjudication_reason    # 中文：最终Gold结论的简要裁决理由
```

专家分歧本身也是训练资产：

\[
\boxed{
AnnotatorDisagreement
\Rightarrow
HardCaseCandidate
}
\]

**中文业务释义：** 专家分歧 ⇒ 高价值 Hard Case 候选；不要简单当脏数据删除。

---

# 三十六、训练数据来源分层

```text
REAL_EXPERT_LABELED    # 中文：真实采购文件中的专家Gold样本
RULE_GENERATED    # 中文：由确定性规则自动生成、可严格验证的样本
COUNTERFACTUAL_SYNTHETIC    # 中文：基于真实样本控制变量生成的反事实样本
PARAPHRASE_SYNTHETIC    # 中文：保持业务含义不变的表达改写样本
ADVERSARIAL_SYNTHETIC    # 中文：专门攻击关键词依赖和表面模式的对抗样本
PRODUCTION_FAILURE_REPLAY    # 中文：未来生产中的真实误报、漏报、弃权错误回放样本
```

\[
\boxed{
SyntheticData
\neq
LegalTruthSource
}
\]

**中文业务释义：** 合成数据 ≠ 法律结论的权威来源；合成数据适合扩充表达、生成反事实和对抗样本，但 Gold 必须由规则、法源或专家验证。

---

# 三十七、Paraphrase Training：训练语义不变性

例如本地机构限制可能改写成：

```text
在本市设有分公司    # 中文：显式本地分支
在项目所在地有固定办公场所    # 中文：固定本地场所
在本区域配置常驻团队    # 中文：常驻人员要求
在距离采购人50公里范围内设置服务点    # 中文：以距离形成地域条件
```

\[
\boxed{
SameBusinessMeaning
+
DifferentSurfaceForm
\Rightarrow
SameDecision
}
\]

**中文业务释义：** 相同业务含义 + 不同表面表达 ⇒ 在其他关键事实不变时，应产生一致判断。

---

# 三十八、Adversarial Negative：专门攻击关键词依赖

```text
“品牌”出现在“不得指定品牌”的条款中    # 中文：包含高风险词，但语义是在禁止违规
“注册资本”出现在合规培训附件中    # 中文：不是对供应商设置准入条件
“本地”出现在项目现场地址说明中    # 中文：只是履约地点事实，不等于要求供应商本地注册
“业绩”出现在合同履约总结中    # 中文：不是投标资格或评分要求
```

这些样本用于把模型从词频依赖里拉回来。

---

# 三十九、Hard Case Mining：围绕错误模式增长数据

未来最有价值的高难正例来源：

```text
rule_miss_llm_hit    # 中文：规则没抓到，但LLM或专家发现真实风险
human_found_after_no_finding    # 中文：系统报无风险后，人工发现漏检
cross_clause_risk    # 中文：跨条款组合后才出现风险
market_evidence_required    # 中文：需要市场证据才确认的技术指向风险
implicit_proxy_restriction    # 中文：代理性企业规模、地域或组织形式限制
```

高难负例来源：

```text
llm_false_positive    # 中文：LLM高置信度误报
rule_hit_exception_applies    # 中文：规则候选命中，但存在合法例外
authorized_policy_case    # 中文：合法政府采购政策被误报成歧视
post_award_case    # 中文：履约要求被误当市场准入限制
quoted_rule_case    # 中文：引用法规禁止条款被误当采购要求
insufficient_evidence_case    # 中文：本应UNRESOLVED却被强行二分类
```

\[
\boxed{
DataFlywheel
=
ModelFailure
\rightarrow
HardCase
\rightarrow
Adjudication
\rightarrow
Training
\rightarrow
Benchmark
}
\]

**中文业务释义：** 数据飞轮 = 模型错误 → 高难案例 → 专家裁决 → 加入训练 → 进入评测验证。

---

# 四十、不要随机按 Clause 切 Train / Val / Test

同一项目的 V1、V2 更正、V3 澄清高度相似。如果 V1 进 Train、V2 进 Test，模型实际上已经见过答案。

\[
\boxed{
RandomClauseSplit
\neq
LeakageSafeSplit
}
\]

**中文业务释义：** 随机按条款切训练 / 测试集 ≠ 防泄漏的数据划分。

推荐分组：

```text
project_family_id    # 中文：同一采购项目及其澄清、更正、版本、派生样本归为同组
template_family_id    # 中文：高度相似采购模板归为同一模板族
counterfactual_pair_id    # 中文：反事实样本对必须留在同一个Split
source_document_family    # 中文：同源文件派生样本避免跨Split泄漏
```

---

# 四十一、Label Leakage：标签泄漏

如果输入里直接写：

```text
“本条违反D05，原因是……”    # 中文：把Gold标签直接泄露在输入中
```

模型没有学判断。

还应防止后生成审查报告重新混入“原始采购文件”语料。

```text
gold_phrase_filter    # 中文：过滤明显泄露Gold结论的文本
report_source_separation    # 中文：原始采购文件与审查报告分层
annotation_metadata_masking    # 中文：训练输入移除标注员结论字段
rule_id_visibility_policy    # 中文：按任务决定是否允许看到候选Rule ID
```

\[
\boxed{
HighOfflineAccuracy
+
Leakage
=
FalseConfidence
}
\]

**中文业务释义：** 离线准确率很高 + 数据泄漏 = 虚假的系统信心。

---

# 四十二、Near-duplicate Detection：近重复检测

政府采购文件模板化程度高，需要：

```text
text_hash    # 中文：文本哈希
normalized_hash    # 中文：标准化后哈希
minhash_or_simhash    # 中文：近重复文本指纹方法
embedding_similarity    # 中文：语义近似检测
template_signature    # 中文：采购模板结构指纹
```

目的不是把所有重复文本删除，而是防止同一模板族跨 Train/Test 泄漏。

---

# 四十三、数据切分建议

```text
TRAIN    # 中文：用于模型参数更新
VALIDATION    # 中文：用于超参数、停止点和版本选择
DEV_HARD_CASE    # 中文：开发阶段高难案例集，不用于最终发布结论
TEST_GOLD    # 中文：最终Gold测试集，不参与模型选择
TEMPORAL_HOLDOUT    # 中文：按时间留出的后期政策或项目测试集
JURISDICTION_HOLDOUT    # 中文：按地区或预算层级留出的泛化测试集
TEMPLATE_HOLDOUT    # 中文：留出未见过采购模板族
```

\[
\boxed{
OneTestSet
\neq
ReliabilityEvidence
}
\]

**中文业务释义：** 一个随机测试集 ≠ 足以证明合规模型可靠；至少还需要高难、时间、地区、模板等独立切片。

---

# 四十四、Class Imbalance：类别不平衡

真实采购文件中“没有问题的条款”通常比真正风险条款多。如果机械照真实比例训练，模型可能学会永远回答“无风险”；如果风险样本过度采样，又会高误报。

训练采样应同时考虑：

```text
business_prevalence    # 中文：真实业务出现频率
risk_criticality    # 中文：漏掉该风险的业务后果
rule_coverage    # 中文：D01-D22等规则是否都有足够样本
hard_case_density    # 中文：高难案例比例
negative_diversity    # 中文：负例表达和业务类型多样性
```

\[
\boxed{
TrainingDistribution
\neq
RawProductionFrequency
}
\]

**中文业务释义：** 训练数据分布 ≠ 简单复制生产数据原始频率；训练还需要保证关键风险覆盖和判断边界学习。

---

# 四十五、Multi-task SFT

同一模型可以训练多个受控子任务：

```text
TASK_FACT_INTERPRETATION    # 中文：结构化事实解释
TASK_RULE_MAPPING    # 中文：候选规则映射
TASK_BUSINESS_RELEVANCE    # 中文：业务必要性 / 相关性判断
TASK_EXCEPTION_MAPPING    # 中文：例外条件映射
TASK_EVIDENCE_SUFFICIENCY    # 中文：证据是否足够
TASK_ABSTENTION    # 中文：是否应该拒绝确定判断
TASK_REVISION_SUGGESTION    # 中文：采购文件修改建议
TASK_STRUCTURED_FINDING    # 中文：生成结构化Finding
```

\[
\boxed{
SingleTaskClassifier
\neq
ComplianceReasoner
}
\]

**中文业务释义：** 只会输出风险 / 无风险的分类器 ≠ 能理解规则、例外、证据和修订方向的合规判断模型。

---

# 四十六、模型输入契约 `ComplianceTrainingInput_V1`

```text
task_type    # 中文：当前训练 / 推理任务
project_context    # 中文：必要项目背景
business_location    # 中文：条款所在资格 / 技术 / 评分 / 合同等业务位置
requirements    # 中文：结构化业务要求
related_requirements    # 中文：跨章节关联要求
candidate_rules    # 中文：候选规则
applicable_policy_context    # 中文：Stage12已解析的适用法规上下文
deterministic_tool_results    # 中文：Rule / Calculator已确认结果
evidence_spans    # 中文：采购文件原文证据
market_business_evidence    # 中文：必要市场、技术、履约证据
known_missing_facts    # 中文：系统已经知道缺失的事实
```

---

# 四十七、模型输出契约 `ComplianceJudgmentOutput_V1`

```text
decision_state    # 中文：SUPPORTED_FINDING / CHECKED_NO_FINDING / EVIDENCE_INSUFFICIENT等
candidate_rule_ids    # 中文：最终关联候选规则
fact_matches    # 中文：哪些结构化事实与规则条件匹配
exception_state    # 中文：例外是否成立或待确认
evidence_refs    # 中文：支持判断的采购文件证据
legal_context_refs    # 中文：系统提供的适用法源上下文引用
missing_facts    # 中文：仍缺少的关键事实
reason_summary    # 中文：简短、可审计的理由摘要
human_review_required    # 中文：是否需要人工复核
recommended_revision    # 中文：在适用时提供可操作的采购文件修订方向
```

---

# 四十八、不训练私有 Chain-of-Thought

训练和生产不需要保存冗长内部思维过程，需要的是：

```text
reason_summary    # 中文：可审计、面向业务的简要理由
fact_refs    # 中文：事实引用
evidence_refs    # 中文：证据引用
rule_refs    # 中文：规则引用
decision_state    # 中文：结构化结论
```

\[
\boxed{
AuditableRationale
\neq
PrivateChainOfThought
}
\]

**中文业务释义：** 可审计业务理由 ≠ 私有内部思维过程；系统需要的是能够验证的事实—规则—证据映射。

---

# 四十九、必要的多任务 Loss

概念上：

\[
\boxed{
\mathcal{L}
=
w_d\mathcal{L}_{decision}
+
w_r\mathcal{L}_{rule}
+
w_e\mathcal{L}_{evidence}
+
w_a\mathcal{L}_{abstain}
+
w_s\mathcal{L}_{schema}
}
\]

**中文业务释义：** 总训练损失可以由“决策状态 + 规则映射 + 证据引用 + 弃权 / 转人工行为 + 结构化输出格式”多个目标加权组成。

```text
w_d    # 中文：决策状态任务权重
w_r    # 中文：规则映射任务权重
w_e    # 中文：证据选择任务权重
w_a    # 中文：弃权 / 人工升级任务权重
w_s    # 中文：结构化输出格式任务权重
```

这些权重不是法规参数，需要用 Validation / Benchmark 调整。

\[
\boxed{
GoodTrainingObjective
=
Decision
+
Evidence
+
Abstention
+
Structure
}
\]

**中文业务释义：** 好的训练目标 = 判断正确 + 证据正确 + 该不确定时会不确定 + 输出结构稳定。

---

# 五十、Curriculum Training：训练课程顺序

### Phase 1：Schema Following

```text
read_fields_correctly    # 中文：正确读取结构化字段
output_schema_correctly    # 中文：稳定输出规定Schema
```

### Phase 2：Clear Boundary Cases

```text
clear_positive    # 中文：明显风险
clear_negative    # 中文：明显无风险
polarity_cases    # 中文：要求 / 禁止等极性差异
```

### Phase 3：Hard Positive / Hard Negative

```text
implicit_restriction    # 中文：隐性限制
authorized_policy    # 中文：合法政策支持
pre_vs_post_award    # 中文：投标前与中标后
specific_vs_unjustified    # 中文：具体但合理 vs 具体且缺乏必要性
```

### Phase 4：Counterfactual

```text
one_axis_change    # 中文：一次只改变一个关键判断轴
label_flip_or_hold    # 中文：模型应随关键事实正确翻转或保持结论
```

### Phase 5：Abstention / Human Escalation

```text
missing_evidence    # 中文：证据不足
policy_conflict    # 中文：法规冲突
market_uncertainty    # 中文：市场事实不足
high_risk_borderline    # 中文：高风险边界案件
```

\[
\boxed{
DecisionBoundaryFirst
>
VerboseExplanation
}
\]

**中文业务释义：** 训练优先保证判断边界稳定，再追求很长、很花哨的解释。

---

# 五十一、LoRA / QLoRA 在 Stage 13 怎么用？

Lesson 5 已经学习：

```text
LoRA    # 中文：低秩适配微调，只训练少量新增参数
QLoRA    # 中文：在量化基础模型上进行低秩适配，以降低显存成本
```

Stage 13 不重复算法原理，重点是用什么训练数据和任务契约去微调。

\[
\boxed{
CourseOrder
\neq
TrainingOrder
}
\]

**中文业务释义：** 教学顺序 ≠ 真正模型训练流水线顺序；实际项目可能是 Base → CPT → SFT，而课程为了系统理解采用不同教学顺序。

---

# 五十二、不要把所有任务塞进很多 Adapter

可以考虑：

```text
shared_compliance_adapter    # 中文：通用合规判断能力
domain_specific_adapter    # 中文：资格 / 技术 / 评分等特定域适配器
experiment_adapter    # 中文：实验性模型分支，不进入正式发布
```

是否拆 Adapter 应由数据量、任务冲突、部署复杂度和 Benchmark 决定。

\[
\boxed{
MoreAdapters
\neq
BetterCompliance
}
\]

**中文业务释义：** Adapter 越多 ≠ 合规能力越强；过度拆分会增加路由、版本和发布治理复杂度。

---

# 五十三、Catastrophic Forgetting：灾难性遗忘

微调后要检查：

```text
instruction_following    # 中文：基础指令遵循是否下降
Chinese_understanding    # 中文：中文语义理解是否下降
table_reasoning    # 中文：表格理解能力是否下降
tool_use_behavior    # 中文：是否还会正确读取Rule / Calculator结果
citation_grounding    # 中文：是否仍能按证据引用
abstention_behavior    # 中文：是否因为SFT变得过度自信
```

\[
\boxed{
DomainGain
\neq
AcceptableGeneralCollapse
}
\]

**中文业务释义：** 领域能力提升 ≠ 可以接受基础理解、工具使用和弃权能力明显退化。

---

# 五十四、Overfitting to Rule IDs

如果训练输入总是：

```text
candidate_rule_id = D05    # 中文：直接把规则编号告诉模型
```

模型可能只会固定话术。要混合：

```text
RULE_ID_VISIBLE    # 中文：候选规则由Rule Engine提供，模型做事实映射和解释
RULE_ID_HIDDEN    # 中文：模型需要从结构化事实中识别可能关联规则，用于测试迁移能力
```

\[
\boxed{
RuleIDAccuracy
\neq
ComplianceJudgmentQuality
}
\]

**中文业务释义：** D01-D22编号预测正确 ≠ 合规判断一定正确；还必须有事实、证据、例外和业务结论。

---

# 五十五、Counterfactual Consistency Test

定义：

\[
\boxed{
CounterfactualConsistency
=
CorrectPairRelations
/
AllCounterfactualPairs
}
\]

**中文业务释义：** 反事实一致性 = 模型正确处理“应该翻转 / 应该保持”的样本对数量 ÷ 全部反事实样本对数量。

\[
\boxed{
SingleSampleAccuracy
\neq
BoundaryUnderstanding
}
\]

**中文业务释义：** 单条样本判断正确 ≠ 模型真正理解判断边界；Pair-level 指标更能测试关键事实变化时模型是否正确改变结论。

---

# 五十六、Abstention Benchmark Slice

必须有：

```text
missing_market_evidence    # 中文：缺市场替代性证据
missing_policy_status    # 中文：法规适用状态未知
conflicting_clarifications    # 中文：采购文件与更正 / 澄清互相冲突
ocr_critical_field_uncertain    # 中文：OCR关键数值不可靠
ambiguous_business_role    # 中文：条款业务角色无法确定
true_legal_conflict    # 中文：存在需要法律专业复核的规则冲突
```

Gold 应是：

```text
EVIDENCE_INSUFFICIENT    # 中文：证据不足
HUMAN_REVIEW_REQUIRED    # 中文：需要人工复核
```

而不是强制模型给风险 / 无风险。

\[
\boxed{
AlwaysAnswer
\neq
ReliableCompliance
}
\]

**中文业务释义：** 永远给确定答案 ≠ 可靠合规；专业系统必须在证据不足或超出能力边界时正确弃权。

---

# 五十七、Revision Suggestion Training

错误建议：

> “删除所有相关要求。”

更好的训练目标：

```text
remove_unnecessary_restriction    # 中文：删除与项目实际需要无关的限制
replace_identity_with_capability    # 中文：把企业身份 / 地域条件改成实际履约能力要求
replace_brand_with_function    # 中文：把品牌指向改成功能 / 性能目标
quantify_scoring_anchor    # 中文：把主观评分改成可观察、可验证评分锚点
move_post_award_obligation    # 中文：把真正属于履约阶段的条件移到合同履约要求
add_exception_or_scope    # 中文：补充正确例外和适用范围
```

\[
\boxed{
FindingCorrect
\neq
RevisionSuggestionCorrect
}
\]

**中文业务释义：** 风险识别正确 ≠ 修改建议一定正确；修改建议也需要单独 Gold 和 Benchmark。

---

# 五十八、Training Data Quality Gate

样本进入正式训练前至少检查：

```text
source_evidence_exists    # 中文：存在可回查原始证据
policy_snapshot_bound    # 中文：绑定法规政策快照
gold_state_adjudicated    # 中文：Gold状态达到要求的专家确认等级
rule_mapping_checked    # 中文：规则映射已核对
exception_checked    # 中文：相关例外已检查
pair_integrity_checked    # 中文：反事实样本只改变预期关键变量
no_label_leakage    # 中文：输入中没有直接泄露Gold结论
split_group_assigned    # 中文：项目族 / 模板族 / Pair已分组
unneeded_sensitive_removed    # 中文：不需要的敏感字段已脱敏或排除
source_usage_allowed    # 中文：训练使用权限和来源治理符合项目要求
```

\[
\boxed{
MoreData
\neq
BetterComplianceTraining
}
\]

**中文业务释义：** 样本数量更多 ≠ 合规训练质量更高；错误Gold、泄漏样本、重复模板和缺少边界的样本会放大错误。

---

# 五十九、Sample Quality Tier

```text
TIER_A    # 中文：真实采购文件 + 专家双人标注 / 裁决 + 完整法源和证据
TIER_B    # 中文：真实采购文件 + 单专家高置信标注 + 完整证据
TIER_C    # 中文：基于A/B真实样本受控生成并通过规则 / 专家验证的合成反事实
TIER_D    # 中文：仅用于探索 / 对抗生成，尚未完成Gold验证，不得直接进入正式训练
```

---

# 六十、训练版本必须可重放

```text
training_run_id    # 中文：训练运行标识
base_model_id    # 中文：基础模型版本
cpt_checkpoint_id    # 中文：如使用CPT后的检查点
adapter_config    # 中文：LoRA / QLoRA等适配器配置
dataset_snapshot_id    # 中文：训练数据快照
annotation_guideline_version    # 中文：标注规范版本
policy_snapshot_range    # 中文：训练样本涉及的政策快照范围
split_manifest    # 中文：Train / Val / Test项目族切分清单
hyperparameters    # 中文：学习率、batch size、epoch等训练参数
code_version    # 中文：训练代码版本
random_seed    # 中文：随机种子
checkpoint_hashes    # 中文：模型检查点指纹
```

\[
\boxed{
ModelVersion
\Rightarrow
DatasetSnapshot
+
CodeVersion
+
TrainingConfig
}
\]

**中文业务释义：** 模型版本 ⇒ 必须能够追溯到数据快照、代码版本和训练配置。

---

# 六十一、为什么 Stage 13 叫 V1-RC？

因为训练完成还远远不等于可以上线。

`RC` 还需要进入：

```text
GoldBenchmark    # 中文：正式Gold Benchmark
RedTeam    # 中文：误报、漏报、提示注入、证据错配等红队测试
Calibration    # 中文：置信度与实际正确率校准
CriticalSliceEvaluation    # 中文：D01-D22及高风险业务切片评测
CitationEvaluation    # 中文：证据 / 法规引用正确率
ReleaseGate    # 中文：满足发布门槛才能进入生产
```

\[
\boxed{
TrainingComplete
\neq
ReleaseReady
}
\]

**中文业务释义：** 微调训练完成 ≠ 模型已经达到发布条件。

---

# 六十二、Stage 13 完整训练流水线

\[
\boxed{
RealProcurementCases
\rightarrow
EvidenceGrounding
\rightarrow
ApplicablePolicySnapshot
\rightarrow
Annotation
\rightarrow
Adjudication
\rightarrow
HardCaseMining
\rightarrow
CounterfactualGeneration
\rightarrow
LeakageControl
\rightarrow
ProjectFamilySplit
\rightarrow
MultiTaskSFT
\rightarrow
HardCaseSFT
\rightarrow
AbstentionTraining
\rightarrow
RCCheckpoint
}
\]

**中文业务释义：** 真实政府采购案例 → 绑定原文证据 → 绑定适用法规快照 → 专家标注 → 分歧裁决 → 高难案例挖掘 → 反事实生成 → 泄漏控制 → 按项目族切分 → 多任务监督微调 → 高难案例强化 → 弃权 / 人工升级训练 → 形成发布候选模型。

---

# 六十三、`ProcurementComplianceLM_V1-RC` 建议目录

```text
ProcurementComplianceLM_V1-RC/    # 中文：政府采购合规模型发布候选版本根目录
├── dataset/    # 中文：训练数据与快照
│   ├── real_expert_labeled/    # 中文：真实专家Gold样本
│   ├── hard_positive/    # 中文：高难正例
│   ├── hard_negative/    # 中文：高难负例
│   ├── counterfactual_pairs/    # 中文：反事实样本对
│   ├── boundary_cases/    # 中文：边界 / 人工复核样本
│   ├── synthetic_verified/    # 中文：经过验证的合成样本
│   └── snapshot_manifest.json    # 中文：数据快照清单
├── annotation/    # 中文：标注规范、结果和专家裁决
│   ├── guideline.md    # 中文：标注规范
│   ├── guideline_versions/    # 中文：历史标注规范版本
│   ├── adjudication.jsonl    # 中文：专家裁决记录
│   └── agreement_metrics.json    # 中文：标注一致性指标
├── splits/    # 中文：防泄漏数据切分
│   ├── train.jsonl    # 中文：训练集
│   ├── validation.jsonl    # 中文：验证集
│   ├── dev_hard_case.jsonl    # 中文：开发高难集
│   ├── temporal_holdout.jsonl    # 中文：时间留出集
│   ├── jurisdiction_holdout.jsonl    # 中文：辖区留出集
│   └── template_holdout.jsonl    # 中文：模板留出集
├── schemas/    # 中文：训练输入 / 输出契约
│   ├── compliance_training_input.json    # 中文：训练输入Schema
│   ├── compliance_judgment_output.json    # 中文：判断输出Schema
│   ├── counterfactual_pair.json    # 中文：反事实样本Schema
│   └── gold_label.json    # 中文：Gold标签Schema
├── leakage/    # 中文：标签泄漏、项目族和近重复检测
│   ├── duplicate_detector.py    # 中文：重复 / 近重复检测
│   ├── project_family_map.json    # 中文：项目族映射
│   ├── template_family_map.json    # 中文：模板族映射
│   └── leakage_report.json    # 中文：数据泄漏检查报告
├── training/    # 中文：SFT / LoRA / QLoRA训练配置
│   ├── curriculum.yaml    # 中文：分阶段训练课程
│   ├── sft_config.yaml    # 中文：监督微调配置
│   ├── adapter_config.json    # 中文：LoRA / QLoRA适配器配置
│   └── run_manifest.json    # 中文：训练运行和可重放信息
├── checkpoints/    # 中文：模型检查点
│   ├── phase1_schema/    # 中文：结构化任务阶段
│   ├── phase2_boundary/    # 中文：清晰判断边界阶段
│   ├── phase3_hard_cases/    # 中文：高难案例阶段
│   ├── phase4_counterfactual/    # 中文：反事实阶段
│   └── rc/    # 中文：发布候选检查点
├── evaluation/    # 中文：Stage13开发阶段评测，不替代Stage15正式Benchmark
│   ├── counterfactual_consistency.json    # 中文：反事实一致性
│   ├── abstention_slice.json    # 中文：弃权 / 人工升级切片
│   ├── hard_negative_precision.json    # 中文：高难负例精度
│   └── regression.json    # 中文：基础能力回归检查
└── manifest.json    # 中文：模型、数据、规则、政策快照、代码和训练配置总清单
```

---

# 六十四、Training Sample Schema 第一版

```text
sample_id    # 中文：样本标识
sample_quality_tier    # 中文：TIER_A / B / C / D质量等级
task_type    # 中文：训练任务类型
project_family_id    # 中文：项目族
template_family_id    # 中文：模板族
document_version_id    # 中文：采购文件版本
policy_snapshot_id    # 中文：法规政策快照
event_time    # 中文：相关法律业务事件时间
review_domain    # 中文：资格 / 技术 / 评分 / 政策 / 竞争 / 合同
source_requirement_ids    # 中文：来源业务要求
candidate_rule_ids    # 中文：候选D01-D22等规则
input_context    # 中文：经过控制的必要输入上下文
evidence_span_ids    # 中文：采购文件原文证据
legal_context_ids    # 中文：Stage12提供的适用法源上下文
deterministic_result_refs    # 中文：Rule / Calculator确定性结果
gold_state    # 中文：专家Gold状态
gold_rule_ids    # 中文：Gold关联规则
gold_evidence_refs    # 中文：Gold证据
gold_exception_state    # 中文：Gold例外状态
gold_missing_facts    # 中文：Gold认为仍缺少的事实
gold_reason_summary    # 中文：简要、可审计Gold理由
human_review_required    # 中文：是否应转人工
hard_case_type    # 中文：高难正例 / 高难负例 / 反事实 / 边界
pair_id    # 中文：反事实Pair标识
changed_axis    # 中文：反事实改变轴
split_group_id    # 中文：防泄漏切分组
annotation_guideline_version    # 中文：标注规范版本
adjudication_id    # 中文：专家裁决记录
```

---

# 六十五、Counterfactual Pair Schema 第一版

```text
pair_id    # 中文：反事实样本对标识
base_sample_id    # 中文：基础样本
counterfactual_sample_id    # 中文：反事实样本
invariant_fields    # 中文：两条样本必须保持不变的字段
changed_axis    # 中文：唯一主要变化判断轴
old_value    # 中文：变化前值
new_value    # 中文：变化后值
base_gold_state    # 中文：基础样本Gold结论
counterfactual_gold_state    # 中文：反事实样本Gold结论
expected_relation    # 中文：标签应保持 / 翻转 / 转UNRESOLVED
boundary_explanation    # 中文：为什么这个变化会影响结论
validation_state    # 中文：规则 / 专家是否已验证Pair有效
```

---

# 六十六、Hard Case Schema 第一版

```text
hard_case_id    # 中文：高难案例标识
source_type    # 中文：专家分歧、模型误报、漏报、规则漏检等来源
failure_mode    # 中文：关键词依赖、忽略例外、证据错配等失败模式
business_domain    # 中文：资格 / 技术 / 评分 / 政策 / 竞争等
rule_ids    # 中文：关联规则
why_hard    # 中文：为什么该样本难
required_context    # 中文：正确判断必须提供哪些上下文
gold_state    # 中文：专家Gold结论
adjudication_refs    # 中文：裁决证据
training_priority    # 中文：进入训练的优先级
benchmark_candidate    # 中文：是否同时进入Stage15 Benchmark候选
```

---

# 六十七、本阶段最重要的 30 个核心心智模型

> **心智模型 ①：`ComplianceTraining ≠ KeywordMemorization`。合规训练不是关键词记忆。**

> **心智模型 ②：`GoodComplianceModel = LearnDecisionBoundary ≠ MemorizeSurfaceWords`。模型要学判断边界，不是表面词。**

> **心智模型 ③：`Keyword ≠ ComplianceLabel`。高风险词不是标签。**

> **心智模型 ④：`TrainingValue ∝ BoundaryInformation`。越能说明结论翻转边界的样本越有价值。**

> **心智模型 ⑤：`WeakHardNegatives ⇒ HighFalsePositiveRisk`。高难负例不足会导致高误报。**

> **心智模型 ⑥：`CounterfactualPair = SameContext + OneCriticalChange + ExpectedDecisionRelation`。反事实要控制变量。**

> **心智模型 ⑦：`ComplianceLabel ≠ {0,1}`。合规标签必须允许证据不足、人工复核和不适用。**

> **心智模型 ⑧：`TrainJudgmentBehavior > MemorizeCurrentPolicyText`。优先训练如何判断，而不是死记当前政策全文。**

> **心智模型 ⑨：`CanTrain ≠ ShouldTrain`。能让LLM学不代表应该让LLM负责。**

> **心智模型 ⑩：`TrainingLabel = Facts + ApplicablePolicySnapshot`。Gold标签依赖项目事实和法规快照。**

> **心智模型 ⑪：`SameWords ≠ SameComplianceMeaning`。相同词语可以有完全不同合规含义。**

> **心智模型 ⑫：`AuthorizedPolicyPreference ≠ PurchaserCreatedDiscrimination`。合法政策支持不等于采购人自行歧视。**

> **心智模型 ⑬：`PreAward ≠ PostAward`。投标前和中标后业务角色不同。**

> **心智模型 ⑭：`Specific ≠ Discriminatory`。技术要求具体不自动等于歧视。**

> **心智模型 ⑮：`SurfaceFeature ≠ CompetitionEffect`。表面字段不等于真实竞争影响。**

> **心智模型 ⑯：`RiskUnit ≠ SingleSentence`。风险可能跨多条款组合产生。**

> **心智模型 ⑰：`LLM ≠ CalculatorReplacement`。模型不能覆盖确定性计算。**

> **心智模型 ⑱：`TrainPolicyContextUse ≠ MemorizePolicyDate`。训练模型使用适用性上下文，不死记日期。**

> **心智模型 ⑲：`GoldLabel = Evidence + ApplicableRule + Adjudication`。Gold必须有证据、规则和裁决。**

> **心智模型 ⑳：`AnnotatorDisagreement ⇒ HardCaseCandidate`。专家分歧是高价值训练资产。**

> **心智模型 ㉑：`SyntheticData ≠ LegalTruthSource`。合成数据不能成为法律真相来源。**

> **心智模型 ㉒：`DataFlywheel = ModelFailure → HardCase → Adjudication → Training → Benchmark`。围绕错误模式建立数据飞轮。**

> **心智模型 ㉓：`RandomClauseSplit ≠ LeakageSafeSplit`。随机条款切分会产生项目和模板泄漏。**

> **心智模型 ㉔：`HighOfflineAccuracy + Leakage = FalseConfidence`。泄漏会制造虚假高分。**

> **心智模型 ㉕：`OneTestSet ≠ ReliabilityEvidence`。单一测试集不能证明可靠。**

> **心智模型 ㉖：`SingleTaskClassifier ≠ ComplianceReasoner`。单任务分类器不是合规判断模型。**

> **心智模型 ㉗：`AuditableRationale ≠ PrivateChainOfThought`。需要可审计理由，不需要保存私有思维过程。**

> **心智模型 ㉘：`SingleSampleAccuracy ≠ BoundaryUnderstanding`。单样本正确不代表真正理解判断边界。**

> **心智模型 ㉙：`AlwaysAnswer ≠ ReliableCompliance`。永远回答不是可靠合规。**

> **心智模型 ㉚：`TrainingComplete ≠ ReleaseReady`。训练完成不等于可以发布。**

---

# 六十八、把整个 Stage 13 压成一张工程图

```text
ProcurementComplianceDataset_V1    # 中文：真实采购文件、Clause、Requirement和Evidence事实底座
↓
ProcurementLegalRAG_V1 / Policy Snapshot    # 中文：给每个样本绑定正确法规版本、时间和辖区上下文
↓
Task Definition    # 中文：把大而泛的合规问题拆成可审计子任务
↓
Expert Annotation    # 中文：专家基于证据和适用规则进行Gold标注
↓
Adjudication    # 中文：对专家分歧和高风险边界案例进行裁决
↓
Hard Positive / Hard Negative Mining    # 中文：挖掘真正决定漏报和误报的高难正负例
↓
Counterfactual Pair Generation    # 中文：控制变量构造结论保持 / 翻转样本对
↓
Paraphrase + Adversarial Data    # 中文：扩充表达方式并攻击关键词依赖
↓
Leakage / Near-duplicate Control    # 中文：按项目族、模板族和Pair防止训练测试泄漏
↓
Project-family Split    # 中文：建立Train / Validation / Hard / Temporal / Jurisdiction等切分
↓
Multi-task SFT    # 中文：训练语义判断、规则映射、证据选择、弃权和结构化输出
↓
Hard-case Curriculum    # 中文：逐步加入高难案例和边界案例
↓
Counterfactual Consistency Check    # 中文：检查关键事实变化时模型是否正确保持或翻转结论
↓
Abstention / Human Escalation Check    # 中文：检查证据不足时是否会拒绝武断判断并升级人工
↓
General Capability Regression    # 中文：检查中文理解、表格、工具使用和基础指令能力是否退化
↓
ProcurementComplianceLM_V1-RC    # 中文：形成进入正式Benchmark与Red Team之前的合规模型发布候选版本
```

---

# 六十九、脑中最后只留一句

> **政府采购合规模型训练的本质，不是把“违规条款”大量喂给模型，而是围绕 Decision Boundary 构造真实专家Gold、高难正例、高难负例、反事实样本和边界案例，让模型学习“哪些事实真正决定规则适用、什么时候例外成立、什么时候证据不足、什么时候必须转人工”；同时把确定性规则、数值计算和法规有效性继续留给 Rule / Calculator / Policy Resolver。只有这样，模型才能从关键词报警器升级成真正能够与混合合规引擎协作的语义判断组件。**

---

# 第十一课 · 第 13 阶段掌握测试

现在不回看正文，你应该能够解释：

```text
Compliance Training 为什么不等于 Keyword Memorization？    # 中文：为什么记住“本地、品牌、注册资本、证书、业绩”不等于学会合规？
什么是Decision Boundary？    # 中文：哪个事实变化以后，正确结论应该改变？
Hard Positive是什么？    # 中文：为什么没有明显关键词但实际有风险的案例特别重要？
Hard Negative是什么？    # 中文：为什么表面像风险、实际存在合法依据或业务差异的案例决定误报率？
Counterfactual Pair是什么？    # 中文：为什么一次最好只改变一个关键变量？
Boundary Case为什么不能强制标0/1？    # 中文：哪些案件应该标证据不足或人工复核？
Compliance Label为什么不能只有{0,1}？    # 中文：NOT_APPLICABLE、证据不足和人工复核为什么必须成为正式状态？
为什么不建议把所有现行法规全文训练进模型参数？    # 中文：PolicyUpdate为什么应该通过Legal RAG和Policy Registry热更新？
Can Train为什么不等于Should Train？    # 中文：哪些确定性任务应该继续交给Rule和Calculator？
SFT在Stage13真正训练哪些能力？    # 中文：语义判断、证据、例外、弃权和Schema分别是什么？
为什么训练样本必须绑定Policy Snapshot ID？    # 中文：政策时点变化为什么会让同类文本标签变化？
Polarity Trap是什么？    # 中文：为什么“要求本地业绩”和“不得要求本地业绩”不能靠关键词判断？
Authorized Policy为什么必须成为Hard Negative？    # 中文：合法中小企业、本国产品支持怎样避免被误报成歧视？
Pre-award和Post-award为什么是重要判断轴？    # 中文：准入门槛和履约义务为什么不能混？
Specific为什么不等于Discriminatory？    # 中文：技术参数必要性、功能目标和市场替代性如何改变结论？
Proxy Restriction是什么？    # 中文：企业规模、地域或主体限制怎样通过代理变量表达？
Risk Unit为什么不一定是一句话？    # 中文：跨条款组合风险怎样进入Hard Positive训练？
Counterfactual Axis至少有哪些？    # 中文：时点、业务角色、辖区、政策时间、例外、证据、市场、Scope、Operator、Polarity怎样构造样本？
为什么模型在异常低价任务中要Respect Calculator？    # 中文：模型应该学流程状态，而不是重新心算覆盖工具结果？
Train Policy Context Use为什么优于Memorize Policy Date？    # 中文：模型怎样与Stage12的Policy Resolver协作？
Gold Label为什么必须=Evidence + Applicable Rule + Adjudication？    # 中文：为什么标注员第一感觉不能直接成为Gold？
Annotation Guideline为什么需要版本化？    # 中文：规则、政策变化怎样导致Label Drift？
Annotator Disagreement为什么是Hard Case资产？    # 中文：它怎样暴露真实判断边界和标注规范缺陷？
Synthetic Data为什么不能成为Legal Truth Source？    # 中文：合成数据应该做什么、不应该做什么？
Paraphrase Training训练什么？    # 中文：为什么相同业务含义的不同表达应该得到相同结论？
Hard Case Mining应该主要从哪里来？    # 中文：模型误报、漏报、人工推翻和规则漏检怎样进入数据飞轮？
Random Clause Split为什么会Leakage？    # 中文：同项目不同版本、同模板条款怎样把答案泄露进测试集？
Project Family / Template Family为什么必须进入Split？    # 中文：怎样避免离线分数虚高？
Label Leakage是什么？    # 中文：审查报告、标注字段和Rule ID怎样意外泄露答案？
为什么一个Test Set不够？    # 中文：Temporal、Jurisdiction、Template Holdout分别验证什么？
Class Imbalance怎样影响模型？    # 中文：风险过少会怎样，风险过采样又会怎样？
为什么Multi-task SFT优于单纯风险分类？    # 中文：Rule Mapping、Evidence、Abstention、Revision Suggestion各训练什么？
为什么不训练私有Chain-of-Thought？    # 中文：为什么Auditable Rationale + Evidence Refs更适合生产审计？
Curriculum Training为什么有价值？    # 中文：Schema → 清晰边界 → Hard Cases → Counterfactual → Abstention为什么是合理顺序？
LoRA / QLoRA在Stage13的重点是什么？    # 中文：为什么这里重点讨论训练数据和任务契约？
Catastrophic Forgetting要监控哪些能力？    # 中文：中文理解、表格、工具使用、证据引用和弃权为什么可能退化？
Counterfactual Consistency怎样计算？    # 中文：为什么Pair-level指标比单样本准确率更能测试判断边界？
Always Answer为什么是坏习惯？    # 中文：哪些样本Gold就应该是证据不足 / 人工复核？
Finding Correct为什么不等于Revision Suggestion Correct？    # 中文：风险判断和修改建议为什么要分别做Gold？
Training Data Quality Gate至少检查什么？    # 中文：证据、法规快照、Gold、例外、Pair完整性、泄漏和Split为什么都要过门？
Model Version为什么必须绑定Dataset Snapshot？    # 中文：怎样保证一次模型训练未来可以重放？
为什么Stage13的产物叫V1-RC？    # 中文：为什么训练结束后还必须进入Stage15 Gold Benchmark、Red Team和Release Gate？
Training Complete为什么不等于Release Ready？    # 中文：正式发布前还缺哪些验证？
```

如果这些能够完整解释：

\[
\boxed{
第十一课第13阶段真正掌握
}
\]

**中文业务释义：** 如果能够解释训练什么、不训练什么，能设计 Hard Positive、Hard Negative 和 Counterfactual Pair，知道如何防止 Project / Template Leakage，并理解为什么模型必须学会证据、例外、弃权和人工升级，而不是只学“风险词”，就说明真正掌握了本阶段。

---

# 下一阶段：第十一课 · 第 14 阶段
# Compliance Agent：多轮审查、工具调用、状态、人工复核与报告生成
## 怎样让 Agent 真正跑完采购需求 → 资格 → 技术 → 评分 → 政策 → 竞争 → 合同 → 证据 → 人工复核 → 最终报告？

下一阶段将正式建立：

# `ProcurementComplianceAgent_V1`

最重要的边界：

\[
\boxed{
Agent
\neq
LLMWithLongPrompt
}
\]

**中文业务释义：** Agent ≠ 一个塞了超长 Prompt 的大语言模型；真正的合规 Agent 必须有明确任务状态、工具权限、执行顺序、失败恢复、证据链、人工队列和完成条件。
