# 第十一课 · 第 12 阶段
# 法规 RAG 与 Temporal / Jurisdiction Reasoning
## 怎么保证引用的是正确法规、正确条文、正确版本、正确地区、正确生效时间？怎样让系统不仅“搜到相关法规”，而是真正解析“当前项目适用哪一套规则”？

第 11 阶段我们已经建立：

\[
\boxed{
OneModel
\neq
ComplianceSystem
}
\]

**中文业务释义：** 一个大语言模型 ≠ 一个完整、可靠、可审计的政府采购合规系统。

并建立：

\[
\boxed{
ComplianceEngine
=
Rules
+
Calculator
+
PolicyResolver
+
LegalRAG
+
LLM
+
Evidence
+
Human
}
\]

**中文业务释义：** 合规引擎 = 规则 + 计算器 + 政策适用解析 + 法规检索 + 大语言模型 + 证据验证 + 人工专家。

但 Stage 11 还留下了一个非常危险的问题：

> Legal RAG 可以“搜到”法规，却不代表它搜到的是 **当前项目真正适用的法规版本**。

同一个政府采购问题，系统可能同时搜到：

```text
current_effective_rule    # 中文：当前生效规则

old_repealed_rule    # 中文：已经废止 / 被替代的旧规则

future_effective_rule    # 中文：已经发布但尚未生效的新规则

local_rule    # 中文：只在特定地区 / 预算层级适用的地方规则

national_rule    # 中文：全国层面的法律、行政法规、部门规章或政策文件

draft_rule    # 中文：征求意见稿 / 草案，并非现行有效规则

official_interpretation    # 中文：官方答复、政策解读等解释性材料

news_summary    # 中文：新闻摘要，不是正式规范文本
```

它们在语义上可能都“非常相关”。

但：

\[
\boxed{
RelevantLaw
\neq
ApplicableLaw
}
\]

**中文业务释义：** 语义上相关的法规政策 ≠ 当前采购项目真正适用的法规政策。

本阶段最终形成：

# `ProcurementLegalRAG_V1`

---

# 一、Stage 12 真正解决的不是“怎么做向量检索”

普通 RAG 的问题通常是：

> “哪段文字与问题最相似？”

政府采购 Legal RAG 真正的问题则是：

> **“哪一个法律政策规范，在这个项目、这个地区、这个预算层级、这个业务事项、这个时间点上具有适用可能？”**

所以：

\[
\boxed{
LegalRetrieval
\neq
SemanticSimilaritySearch
}
\]

**中文业务释义：** 法规检索 ≠ 单纯语义相似度搜索。

真正需要同时解决：

```text
authority    # 中文：制定 / 发布机关是谁

legal_level    # 中文：法律、行政法规、地方性法规、规章、规范性政策文件等层级 / 类型

jurisdiction    # 中文：国家、地方及具体适用区域 / 预算层级

subject_matter    # 中文：法规调整的政府采购业务事项

effective_time    # 中文：何时开始生效

expiry_or_repeal    # 中文：何时失效、废止、被替代

version_chain    # 中文：法规版本、修改、替代关系

transition_rule    # 中文：新旧规则过渡安排

exception_rule    # 中文：例外、但书、特殊情形

source_authority    # 中文：法源是否来自可靠官方发布渠道
```

---

# 二、当前法规校对基线：为什么 Stage 12 必须做 Temporal Reasoning？

截至本阶段校对时点：

```text
snapshot_date = 2026-09-20    # 中文：本阶段法规快照日期

财库〔2026〕2号    # 中文：《关于推动解决政府采购异常低价问题的通知》，已于2026年2月1日起施行

财库〔2026〕12号    # 中文：《紧急采购管理暂行办法》，已发布，但到2026年9月20日尚未生效；自2026年10月1日起施行

国办发〔2025〕34号    # 中文：政府采购本国产品标准及相关政策，自2026年1月1日起施行

《中华人民共和国政府采购法实施条例》    # 中文：国务院令第658号，自2015年3月1日起施行
```

因此同一个问题：

> “紧急采购现在应该执行什么规则？”

在：

```text
2026-09-20    # 中文：新《紧急采购管理暂行办法》尚未生效
```

和：

```text
2026-10-02    # 中文：新办法已经进入施行期，但仍需检查项目是否满足办法定义和范围
```

答案可能不同。

所以：

\[
\boxed{
SameQuestion
+
DifferentEventTime
=
PotentiallyDifferentApplicableRule
}
\]

**中文业务释义：** 同一个法律问题 + 不同业务事件时间 = 可能适用不同规则版本。

---

# 三、核心心智模型 ①
# `PublicationDate` 不等于 `EffectiveDate`

\[
\boxed{
Published
\neq
Effective
}
\]

**中文业务释义：** 已经发布 ≠ 已经生效。

例如财库〔2026〕12号：

```text
issue_date = 2026-09-07    # 中文：印发日期

effective_date = 2026-10-01    # 中文：正式施行日期

status_on_2026_09_20 = PUBLISHED_NOT_EFFECTIVE    # 中文：2026年9月20日状态为“已发布、尚未生效”
```

如果 Legal RAG 只按：

> “发布日期最新”

排序，

就可能提前把未来规则当成现行规则。

---

# 四、法规状态机必须显式存在

建议：

```text
DRAFT    # 中文：征求意见稿 / 草案

PUBLISHED_NOT_EFFECTIVE    # 中文：已经正式发布，但尚未进入施行期

EFFECTIVE    # 中文：当前有效

AMENDED    # 中文：已经发生修改，需要解析当前版本

PARTIALLY_REPEALED    # 中文：部分条款已经被废止或替代

REPEALED    # 中文：已经废止

EXPIRED    # 中文：有明确期限并已到期

SUPERSEDED    # 中文：已经被后续规则整体替代

STATUS_UNRESOLVED    # 中文：系统目前无法可靠确认状态
```

所以：

\[
\boxed{
LegalDocument
\neq
AlwaysApplicableText
}
\]

**中文业务释义：** 法规政策文件进入知识库以后 ≠ 它在任何时间都可以直接作为现行适用依据。

---

# 五、核心心智模型 ②
# `LatestPolicy` 不等于 `ApplicablePolicy`

\[
\boxed{
LatestPolicy
\neq
ApplicablePolicy
}
\]

**中文业务释义：** 最新发布的政策 ≠ 当前项目真正适用的政策。

原因至少包括：

```text
not_effective_yet    # 中文：还没生效

project_event_before_effective_date    # 中文：项目关键法律事件发生在新规生效前

out_of_jurisdiction    # 中文：不属于该地区 / 预算层级

out_of_scope    # 中文：不属于该政策调整的采购对象 / 业务事项

transition_clause    # 中文：存在专门新旧规则过渡安排

special_rule    # 中文：存在更具体的特别规则

treaty_or_authorized_exception    # 中文：存在条约、授权或其他特殊适用规则
```

---

# 六、Legal Time 不是一个 Date 字段就够了

每份法规政策至少要区分：

```text
promulgation_date    # 中文：公布 / 发布日期

effective_from    # 中文：开始生效日期

effective_to    # 中文：有效终止日期，如已明确

repeal_date    # 中文：废止日期

amendment_dates    # 中文：历次修改日期

transition_start    # 中文：过渡期开始

transition_end    # 中文：过渡期结束

snapshot_recorded_at    # 中文：系统何时抓取 / 记录该版本
```

---

# 七、核心心智模型 ③
# `Valid Time` 与 `System Time` 必须分开

这是一个非常重要的专业数据模型：

```text
valid_time    # 中文：法规在现实世界中“对哪个时间段有效”

system_time    # 中文：系统“什么时候知道 / 保存了这个版本”
```

因此：

\[
\boxed{
LegalKnowledgeTime
\neq
LegalValidTime
}
\]

**中文业务释义：** 系统什么时候获得法规文本 ≠ 法规在法律关系中什么时候开始 / 停止适用。

例如：

> 系统 2026-09-11 抓到了财库〔2026〕12号，

并不代表：

> 它从 2026-09-11 就是现行有效规则。

---

# 八、为什么要做 Bitemporal Model？
## 双时间模型

建议为法规版本保存：

```text
valid_from    # 中文：现实适用开始时间

valid_to    # 中文：现实适用结束时间

recorded_from    # 中文：系统开始持有该版本的时间

recorded_to    # 中文：系统中该记录何时被后续记录替换
```

这样才能回答两个不同问题：

```text
What rule was legally applicable on 2026-02-10?
# 中文：2026年2月10日现实中应适用什么规则？

What did our system know on 2026-02-10?
# 中文：系统在2026年2月10日当时掌握了什么规则版本？
```

这对：

> 历史审计、事故复盘、规则更新责任追踪

非常重要。

---

# 九、核心心智模型 ④
# `ProjectDate` 也不是一个万能日期

政府采购项目有很多业务时间：

```text
budget_approval_date    # 中文：预算批准时间

procurement_plan_date    # 中文：采购计划时间

announcement_date    # 中文：采购公告日期

document_issue_date    # 中文：采购文件发出日期

bid_submission_deadline    # 中文：投标 / 响应截止时间

bid_opening_date    # 中文：开标 / 响应开启日期

evaluation_date    # 中文：评审日期

award_date    # 中文：中标 / 成交日期

contract_date    # 中文：合同签订日期

performance_date    # 中文：履约发生日期

acceptance_date    # 中文：验收日期
```

不同规则：

> 可能以不同事件作为适用判断锚点。

所以：

\[
\boxed{
OneProject
\neq
OneLegalEventTime
}
\]

**中文业务释义：** 一个采购项目 ≠ 只有一个法律适用时间点。

---

# 十、Event-time Resolver
## 业务事件时间解析器

每条 Policy Rule 建议保存：

```text
application_event_type    # 中文：该规则应以哪一个业务事件时间判断适用

application_event_source    # 中文：这个事件时间从哪份采购文件 / 系统记录取得

event_time    # 中文：当前项目实际事件时间

transition_event_rule    # 中文：如果有过渡条款，如何确定新旧规则适用
```

因此：

\[
\boxed{
ApplicableAt
=
RuleSpecificEventTime
}
\]

**中文业务释义：** 法规是否适用，应按这条规则规定或应解析的特定业务事件时间判断，而不是全系统统一使用“项目创建日期”。

---

# 十一、不要把“默认不溯及既往”机械套到所有文件

《中华人民共和国立法法》对法律、行政法规、地方性法规、自治条例和单行条例、规章规定了不溯及既往的一般原则，并规定特定例外。

但合规引擎不能把这一句话简化成：

> “所有政策文件都永远不可能影响过去项目。”

正确设计是：

```text
retroactivity_rule    # 中文：该规则是否具有明确溯及安排

transition_clause    # 中文：是否存在过渡条款

applicable_event_type    # 中文：以哪个业务事件作为适用节点

legal_level    # 中文：当前文件属于什么法律规范层级 / 类型

human_review_required    # 中文：复杂历史适用问题是否必须人工复核
```

---

# 十二、核心心智模型 ⑤
# `NoRetroactivityDefault` 不等于 `NoTransitionAnalysis`

\[
\boxed{
NoRetroactivityDefault
\neq
SkipTransitionAnalysis
}
\]

**中文业务释义：** 存在“不溯及既往”的一般原则 ≠ 可以跳过新旧规则过渡条款、适用事件和特别规定分析。

---

# 十三、Jurisdiction 到底是什么？

在政府采购中，Jurisdiction 不能简单理解成：

> “供应商注册在哪个省”。

至少要看：

```text
procuring_entity    # 中文：采购人是谁

budget_level    # 中文：中央预算还是地方预算

procurement_region    # 中文：采购项目所属行政区域 / 制度适用区域

rule_issuer_scope    # 中文：规则制定机关的权限与适用范围

procurement_object    # 中文：货物 / 服务 / 工程及其他业务类型

special_regime    # 中文：涉密、紧急采购、进口产品等特殊制度
```

---

# 十四、核心心智模型 ⑥
# `SupplierLocation` 不等于 `ProcurementJurisdiction`

\[
\boxed{
SupplierLocation
\neq
ProcurementJurisdiction
}
\]

**中文业务释义：** 供应商注册地 ≠ 政府采购法规适用辖区的当然决定因素；法规适用通常应结合采购人预算级次、项目所属制度范围、规则自身适用区域和具体业务事项判断。

这条边界与 D01：

> 不得不合理限制外地企业进入本地政府采购市场

具有直接关系。

---

# 十五、中央预算与地方预算为什么必须进入 Legal RAG 元数据？

《中华人民共和国政府采购法》第七条、第八条和第二十七条明确区分：

```text
central_budget_project    # 中文：中央预算政府采购项目

local_budget_project    # 中文：地方预算政府采购项目
```

在：

```text
集中采购目录    # 中文：目录制定层级

政府采购限额标准    # 中文：限额标准制定层级

公开招标数额标准    # 中文：货物服务公开招标数额标准制定层级
```

方面存在中央 / 地方规则来源差异。

所以：

\[
\boxed{
SameProvince
+
DifferentBudgetLevel
=
PotentiallyDifferentThresholdSource
}
\]

**中文业务释义：** 同一个省份内的项目 + 不同预算级次 = 可能需要检索不同来源的集中采购目录或数额标准。

---

# 十六、核心心智模型 ⑦
# `Jurisdiction` 是一个 Rule Scope，不只是地图坐标

\[
\boxed{
Jurisdiction
=
AuthorityScope
+
BudgetScope
+
GeographicScope
+
SubjectMatterScope
}
\]

**中文业务释义：** 适用辖区 = 制定权限范围 + 预算层级范围 + 地理范围 + 事项范围。

所以 Legal RAG 元数据里不能只有：

```text
province = Beijing    # 中文：只有一个省市字段远远不够
```

---

# 十七、Legal Level
## 法规层级为什么不能靠模型猜？

根据现行《中华人民共和国立法法》，法律的效力高于行政法规、地方性法规、规章；行政法规的效力高于地方性法规、规章；地方性法规与地方政府规章、不同规章之间还存在进一步的效力和冲突处理规则。

因此至少需要：

```text
CONSTITUTION    # 中文：宪法

LAW    # 中文：法律

ADMINISTRATIVE_REGULATION    # 中文：行政法规

LOCAL_REGULATION    # 中文：地方性法规

DEPARTMENT_RULE    # 中文：部门规章

LOCAL_GOVERNMENT_RULE    # 中文：地方政府规章

NORMATIVE_POLICY_DOCUMENT    # 中文：规范性 / 政策性文件，需按制定主体和具体依据管理

SPECIAL_INSPECTION_RULE    # 中文：专项整治 / 检查工作规则

OFFICIAL_INTERPRETIVE_REFERENCE    # 中文：官方答复、政策解读等解释性参考材料

DRAFT_OR_CONSULTATION    # 中文：草案 / 征求意见稿
```

---

# 十八、核心心智模型 ⑧
# `LegalLevel` 不等于简单数字排名

\[
\boxed{
LegalHierarchy
\neq
SortByLevelAndPickTop1
}
\]

**中文业务释义：** 法律规范效力层级 ≠ 把所有文件按“级别数字”排序后永远取最高的一份。

为什么？

因为还存在：

```text
special_vs_general    # 中文：特别规定与一般规定

new_vs_old    # 中文：新规定与旧规定

same_authority_conflict    # 中文：同一机关制定规则之间冲突

cross_authority_conflict    # 中文：不同制定机关规则之间冲突

authorized_variation    # 中文：依法授权的变通 / 特别制度

subject_matter_scope    # 中文：不同规则调整的事项范围不同
```

---

# 十九、《立法法》对新旧、特别 / 一般规则有什么启示？

现行《立法法》明确：

> 同一机关制定的法律、行政法规、地方性法规、自治条例和单行条例、规章，特别规定与一般规定不一致的，适用特别规定；新的规定与旧的规定不一致的，适用新的规定。

所以工程上至少保存：

```text
is_special_rule    # 中文：是否属于特别规定

is_general_rule    # 中文：是否属于一般规定

same_issuer_relation    # 中文：是否由同一机关制定

new_old_relation    # 中文：规则之间的新旧关系

subject_overlap    # 中文：是否确实调整同一事项
```

---

# 二十、核心心智模型 ⑨
# `Newer` 不是跨所有法规冲突的万能答案

\[
\boxed{
NewerDocument
\neq
UniversalConflictWinner
}
\]

**中文业务释义：** 文件更新 ≠ 在任何冲突场景下都自动优先适用。

现行《立法法》对于：

> 法律之间的新一般规定与旧特别规定冲突；

> 行政法规之间的新一般规定与旧特别规定冲突；

以及：

> 地方性法规与部门规章、部门规章之间等冲突

规定了相应裁决机制。

因此：

> Legal RAG 不能把复杂法规冲突变成“发布时间晚的赢”。

---

# 二十一、核心心智模型 ⑩
# `ConflictDetected` 不等于 `ModelCanResolve`

\[
\boxed{
LegalConflictDetected
\neq
LLMChooseOne
}
\]

**中文业务释义：** 系统发现法规冲突 ≠ LLM 可以自行挑一个文件作为最终依据。

正确状态可能是：

```text
CONFLICT_RESOLVED_BY_RULE    # 中文：依据明确适用规则已经解决

CONFLICT_REQUIRES_AUTHORITY_RESOLUTION    # 中文：依法应由特定机关处理 / 裁决

CONFLICT_REQUIRES_HUMAN_LEGAL_REVIEW    # 中文：需要人工法律专业复核

CONFLICT_UNRESOLVED    # 中文：当前系统无法形成可靠结论
```

---

# 二十二、Legal RAG 的 Source Authority
## 来源权威性必须进入排序

普通搜索常按：

> 点击率、SEO、文本相似度。

法规 RAG 不行。

建议来源优先级至少考虑：

```text
promulgating_authority_official_source    # 中文：制定 / 发布机关官方来源

official_gazette_or_official_legal_database    # 中文：政府公报 / 官方法规数据库等标准来源

official_government_procurement_portal    # 中文：政府采购官方平台的法规政策页面

authorized_official_republication    # 中文：其他政府部门对正式文件的官方转载

official_interpretation    # 中文：主管部门政策解读、问答、答复等解释材料

secondary_professional_source    # 中文：专业研究 / 媒体二次材料，仅作辅助
```

因此：

\[
\boxed{
SourceAuthority
>
SemanticSimilarity
}
\]

**中文业务释义：** 在法规证据排序中，来源权威性应高于单纯文本相似度。这里的 `>` 表示工程优先级，不是法律效力公式。

---

# 二十三、核心心智模型 ⑪
# `OfficialInterpretation` 不等于 `NormativeRule`

\[
\boxed{
OfficialInterpretation
\neq
NormativeRule
}
\]

**中文业务释义：** 官方答复 / 政策解读可以帮助理解和执行，但不能在数据模型里与法律、行政法规、规章、正式政策文件混成同一种法源对象。

因此保存：

```text
source_role = INTERPRETIVE_REFERENCE    # 中文：解释性参考，而不是直接伪装成正式规范文本
```

---

# 二十四、专项整治“22 项”与正式法源也必须分层

第 4 阶段的附件 9 二十二项是：

# Inspection / Enforcement Rule Set
## 专项检查与处理规则体系

但最终 Finding 的法律 / 政策支持可能还需要：

```text
政府采购法    # 中文：上位法律依据

政府采购法实施条例    # 中文：行政法规依据

财政部规章    # 中文：具体程序 / 评审规则

规范性政策文件    # 中文：中小企业、本国产品、绿色采购等具体政策

专项整治工作指引 / 附件9    # 中文：专项检查和处理口径
```

所以：

\[
\boxed{
InspectionRule
\neq
CompleteLegalBasis
}
\]

**中文业务释义：** 专项检查规则 ≠ 最终 Finding 所需的全部法律政策依据。

---

# 二十五、Legal Corpus 不能只存整篇 PDF

每份法规应该拆为：

```text
document    # 中文：整份法规 / 政策文件

chapter    # 中文：章

article    # 中文：条

paragraph    # 中文：款 / 段

item    # 中文：项

subitem    # 中文：目 / 更细分结构

definition    # 中文：定义条款

exception    # 中文：例外 / 但书

appendix    # 中文：附件

cross_reference    # 中文：条文之间引用关系
```

---

# 二十六、核心心智模型 ⑫
# `LegalChunk` 应优先尊重规范结构，而不是 Token 数

\[
\boxed{
LegalChunkBoundary
=
NormativeStructure
+
SemanticCompleteness
}
\]

**中文业务释义：** 法规 Chunk 边界优先由条、款、项、定义、例外等规范结构和完整语义决定，而不是固定每 500 tokens 切一次。

---

# 二十七、Article ID 必须版本化

不能只有：

```text
article_id = Article_20    # 中文：只有“第二十条”这个编号不够
```

因为修改后：

> 条文编号、内容、适用版本可能变化。

建议：

```text
policy_id    # 中文：逻辑法规文件身份

policy_version_id    # 中文：法规具体版本

article_id    # 中文：当前版本内条文标识

canonical_article_id    # 中文：跨版本逻辑条文身份

article_number_raw    # 中文：原始“第二十条”等编号

article_text_raw    # 中文：该版本原文

effective_from    # 中文：该条文版本开始适用时间

effective_to    # 中文：该条文版本结束适用时间
```

---

# 二十八、核心心智模型 ⑬
# `ArticleNumber` 不等于稳定法律身份

\[
\boxed{
ArticleNumber
\neq
StableLegalIdentity
}
\]

**中文业务释义：** “第二十条”这种显示编号 ≠ 跨版本永久稳定的法律身份；引用系统必须绑定具体法规版本。

---

# 二十九、Definition Expansion
## 定义条款为什么必须联动？

例如某一规则使用：

> “本国产品”

如果只召回价格优惠条款，而没有召回：

> “本国产品”的标准定义，

LLM 仍可能错误理解。

因此：

\[
\boxed{
RuleArticle
+
DefinitionArticle
=
UsableLegalContext
}
\]

**中文业务释义：** 规则条文 + 关键定义条文 = 更完整可用的法规上下文。

---

# 三十、Exception Expansion
## 例外条款必须主动检索

如果 RAG 只召回：

> 一般禁止 / 一般要求，

却没有召回：

> “但……除外”

就会系统性误报。

所以：

\[
\boxed{
GeneralRuleRetrieval
\Rightarrow
ExceptionSearch
}
\]

**中文业务释义：** 召回一般规则 ⇒ 必须主动搜索相关例外、但书和特殊情形。

---

# 三十一、核心心智模型 ⑭
# `RuleWithoutException` 可能是错误规则

\[
\boxed{
RuleContext
=
GeneralRule
+
Exception
+
Definition
+
CrossReference
}
\]

**中文业务释义：** 可用于判断的规则上下文 = 一般规则 + 例外 + 定义 + 条文交叉引用。

---

# 三十二、Cross-reference Graph
## 法规之间也需要图结构

例如：

```text
GovernmentProcurementLaw
# 中文：《政府采购法》

→ ImplementationRegulation
# 中文：《政府采购法实施条例》

→ DepartmentRule
# 中文：财政部规章

→ PolicyNotice
# 中文：具体政策通知

→ FAQOrInterpretation
# 中文：主管部门实施答复 / 解读
```

这不是简单的“引用链”。

每条边应记录：

```text
IMPLEMENTS    # 中文：实施 / 细化

BASED_ON    # 中文：以某法源为依据

AMENDS    # 中文：修改

REPEALS    # 中文：废止

SUPERSEDES    # 中文：替代

INTERPRETS    # 中文：解释

REFERS_TO    # 中文：引用

EXCEPTION_TO    # 中文：构成特定例外关系
```

---

# 三十三、核心心智模型 ⑮
# `VectorDB` 不等于 `LegalDatabase`

\[
\boxed{
VectorDatabase
\neq
LegalKnowledgeBase
}
\]

**中文业务释义：** 向量数据库 ≠ 法规知识库。

真正法规知识库至少还需要：

> 元数据、版本链、状态、辖区、效力层级、条文结构、交叉引用、例外、来源权威性。

---

# 三十四、Legal Query Planner
## 法规检索前先把问题拆开

一个业务问题：

> “某地方预算项目使用这个评分条件是否有风险？”

不能只生成一个自然语言 query。

建议先拆：

```text
subject_matter    # 中文：评分标准合规

risk_type    # 中文：可能涉及差别歧视 / 资格评分化 / 量化等

procurement_category    # 中文：货物 / 服务 / 工程

budget_level    # 中文：中央 / 地方

jurisdiction    # 中文：适用地区

event_time    # 中文：规则适用的业务事件时间

candidate_rule_ids    # 中文：可能关联Dxx规则

special_policy_context    # 中文：是否涉及中小企业、本国产品等特殊政策
```

---

# 三十五、核心心智模型 ⑯
# `SearchQuery` 应由业务事实生成，而不是只复述用户问题

\[
\boxed{
LegalQuery
=
Issue
+
Facts
+
Time
+
Jurisdiction
+
RuleType
}
\]

**中文业务释义：** 法规检索 Query = 法律问题 + 项目事实 + 适用时间 + 适用辖区 + 规则类型。

---

# 三十六、Legal RAG 推荐检索链

\[
\boxed{
Question
\rightarrow
QueryPlanner
\rightarrow
MetadataFilter
\rightarrow
HybridRetrieval
\rightarrow
LegalReranker
\rightarrow
VersionResolver
\rightarrow
JurisdictionResolver
\rightarrow
ExceptionExpansion
\rightarrow
CitationValidator
}
\]

**中文业务释义：** 问题 → 法律检索查询规划 → 元数据过滤 → 关键词 + 向量混合检索 → 法规专用重排 → 版本解析 → 辖区解析 → 例外扩展 → 引用验证。

---

# 三十七、为什么需要 Hybrid Retrieval？
## 混合检索

Lexical Search——词法检索：

> 特别擅长精确文号、法条编号、固定术语。

例如：

```text
财库〔2026〕2号    # 中文：精确文号

第二十条    # 中文：精确条文编号

“公开招标数额标准”    # 中文：固定法律术语
```

Embedding Search——向量语义检索：

> 适合用户没有使用法规原词，但表达了相同法律问题的情况。

所以：

\[
\boxed{
LegalRetrieval
=
Lexical
+
Embedding
+
Metadata
}
\]

**中文业务释义：** 法规检索 = 精确词法检索 + 向量语义检索 + 法规元数据约束。

---

# 三十八、核心心智模型 ⑰
# `TopK` 不是适用法集合

\[
\boxed{
RetrievalTopK
\neq
ApplicableLawSet
}
\]

**中文业务释义：** 相似度最高的 Top-K 文档 ≠ 当前项目真正适用的法规集合。

Top-K 只是：

# Candidate Pool
## 候选池

后面还必须经过：

> Version / Time / Jurisdiction / Scope / Exception Resolver。

---

# 三十九、Metadata Filter 不能把历史版本全删掉

如果只保留：

```text
status = EFFECTIVE    # 中文：当前有效
```

会导致：

> 无法审查历史项目。

所以建议维护：

```text
current_candidate_pool    # 中文：当前适用候选池

historical_version_pool    # 中文：历史版本池

future_published_pool    # 中文：已发布未来生效规则池

superseded_neighbor_pool    # 中文：被替代 / 修改版本邻接池
```

---

# 四十、核心心智模型 ⑱
# `Current Corpus` 不等于 `Historical Audit Corpus`

\[
\boxed{
CurrentCompliance
\neq
HistoricalComplianceReplay
}
\]

**中文业务释义：** 审查今天的项目 ≠ 复盘过去项目；历史审计必须能够恢复当时的有效规则环境。

---

# 四十一、Legal Reranker
## 法规重排不能只看语义相关度

建议至少考虑：

\[
\boxed{
LegalRankScore
=
SemanticRelevance
+
SourceAuthority
+
TemporalFit
+
JurisdictionFit
+
SubjectMatterFit
+
VersionFit
}
\]

**中文业务释义：** 法规重排分数 = 语义相关性 + 来源权威性 + 时间适配度 + 辖区适配度 + 事项适配度 + 版本适配度。

这是工程排序模型，不是法律效力计算公式。

---

# 四十二、核心心智模型 ⑲
# `HighSimilarity` 不等于 `HighLegalFit`

\[
\boxed{
HighSemanticSimilarity
\neq
HighLegalApplicability
}
\]

**中文业务释义：** 文本语义很相似 ≠ 对当前项目具有很高的法规适用性。

---

# 四十三、Applicability Resolver
## 适用性解析器

对每一个法规候选至少输出：

```text
policy_id    # 中文：法规 / 政策逻辑标识

policy_version_id    # 中文：具体版本

legal_level    # 中文：法律规范层级 / 文件类型

issuer    # 中文：制定 / 发布机关

jurisdiction_match    # 中文：辖区是否匹配

budget_scope_match    # 中文：预算级次是否匹配

subject_matter_match    # 中文：业务事项是否匹配

temporal_match    # 中文：业务事件时间是否在适用区间

status_at_event_time    # 中文：在项目事件时点的法规状态

transition_result    # 中文：过渡条款解析结果

exception_result    # 中文：例外是否适用

supersession_result    # 中文：是否已被替代 / 修改

conflict_state    # 中文：是否存在法规冲突

applicability_state    # 中文：最终适用状态
```

---

# 四十四、Applicability State
## 不要只用 true / false

建议：

```text
APPLICABLE    # 中文：当前事实、时点、辖区和范围均支持适用

NOT_YET_EFFECTIVE    # 中文：项目事件时点尚未生效

EXPIRED    # 中文：项目事件时点已过有效期

REPEALED    # 中文：在适用时点已经废止

SUPERSEDED    # 中文：已被后续规则替代

OUT_OF_JURISDICTION    # 中文：不属于该法规辖区

OUT_OF_BUDGET_SCOPE    # 中文：预算层级不匹配

OUT_OF_SUBJECT_SCOPE    # 中文：业务事项 / 采购对象不匹配

TRANSITION_REVIEW_REQUIRED    # 中文：存在过渡条款，需要进一步解析

EXCEPTION_APPLIES    # 中文：一般规则存在适用例外

CONFLICT_UNRESOLVED    # 中文：规则冲突尚未解决

APPLICABILITY_UNKNOWN    # 中文：证据不足，无法可靠判断
```

---

# 四十五、核心心智模型 ⑳
# `NotApplicable` 必须有原因

\[
\boxed{
NotApplicable
\Rightarrow
ReasonCode
}
\]

**中文业务释义：** 判断某法规不适用 ⇒ 必须记录不适用原因，例如尚未生效、地区不符、预算层级不符、事项范围不符或已被替代。

---

# 四十六、案例 1：财库〔2026〕2号异常低价规则

假设规则适用事件发生在：

```text
event_time = 2026-01-20    # 中文：发生在2026年2月1日施行前
```

则：

```text
policy = 财库〔2026〕2号    # 中文：异常低价通知

status_at_event_time = NOT_YET_EFFECTIVE    # 中文：在该时点尚未生效
```

如果适用事件发生在：

```text
event_time = 2026-02-10    # 中文：已经进入施行期
```

则：

> 该文件进入 `APPLICABLE` 候选，但仍需继续确认项目类型、采购文件配置和具体业务事实。

所以：

\[
\boxed{
EffectiveDatePassed
\neq
AutomaticallyApplicable
}
\]

**中文业务释义：** 已经过生效日期 ≠ 不检查其他适用条件就自动认定适用。

---

# 四十七、案例 2：财库〔2026〕12号紧急采购新规

当前快照：

```text
snapshot_date = 2026-09-20    # 中文：本课程本阶段校对时点

effective_date = 2026-10-01    # 中文：办法正式施行时点
```

所以当前状态：

```text
PUBLISHED_NOT_EFFECTIVE    # 中文：已发布、尚未生效
```

对于：

```text
event_time = 2026-09-25    # 中文：发生在新办法施行前
```

不能把财库〔2026〕12号当成已经生效的现行规则。

对于：

```text
event_time = 2026-10-03    # 中文：发生在施行后
```

才进入：

> “是否符合紧急采购定义、资金和项目范围、具体程序条件”的进一步适用性判断。

---

# 四十八、案例 3：国办发〔2025〕34号本国产品政策

该通知明确：

```text
effective_date = 2026-01-01    # 中文：自2026年1月1日起施行
```

因此对适用事件发生在 2025 年的项目：

> 不能把其中 2026 年开始施行的本国产品价格评审优惠机械套用。

而适用事件进入 2026 年以后：

> 仍然要继续判断采购标的是否在政策范围、产品状态是否满足标准、是否存在国际条约 / 协定特别规则等。

---

# 四十九、核心心智模型 ㉑
# `Effective` 只是适用性的一个条件

\[
\boxed{
ApplicablePolicy
=
Effective
+
JurisdictionMatch
+
ScopeMatch
+
EventMatch
+
ExceptionCheck
}
\]

**中文业务释义：** 适用政策 = 已生效 + 辖区匹配 + 事项范围匹配 + 业务事件匹配 + 例外检查。

---

# 五十、案例 4：中央预算和地方预算的公开招标数额标准

政府采购法明确：

> 中央预算政府采购项目和地方预算政府采购项目的公开招标数额标准来源不同。

因此 Query Planner 不能只搜：

```text
“公开招标数额标准”
```

而应生成：

```text
budget_level = CENTRAL / LOCAL    # 中文：中央预算还是地方预算

jurisdiction = specific_region    # 中文：如为地方预算，解析具体地区

object_type = goods_or_services    # 中文：货物 / 服务等采购对象

event_time = applicable_event_time    # 中文：项目适用时点
```

---

# 五十一、核心心智模型 ㉒
# `SameLegalTerm` 可能需要不同 Rule Source

\[
\boxed{
SameLegalTerm
+
DifferentScope
=
DifferentRuleSource
}
\]

**中文业务释义：** 相同法律术语 + 不同预算层级 / 地区 / 事项范围 = 可能需要检索不同的具体规则来源。

---

# 五十二、Citation Validator
## 法规引用正确到底是什么意思？

至少分四层：

```text
document_correctness    # 中文：引用的是正确法规文件

version_correctness    # 中文：引用的是正确版本

article_correctness    # 中文：引用的是正确条 / 款 / 项

support_correctness    # 中文：引用内容真正支持当前风险结论
```

所以：

\[
\boxed{
LegalCitationCorrectness
\neq
LegalSupportCorrectness
}
\]

**中文业务释义：** 法规引用形式正确 ≠ 这条法规真的支持当前结论。

---

# 五十三、核心心智模型 ㉓
# `LegalCitation` 不等于 `LegalSupport`

\[
\boxed{
LegalCitation
\neq
LegalSupport
}
\]

**中文业务释义：** 给出了一条法条 ≠ 该法条已经构成当前 Finding 的实质依据。

例如：

> 引用了公平竞争原则，

但具体 Finding 是：

> “某一评分因素为何不得设置”。

仍需要：

> 更直接、更具体的法规政策依据和事实匹配。

---

# 五十四、Citation Atom
## 引用粒度应该多细？

不要默认只引用：

> 整份法规标题。

建议 Citation Atom：

```text
document_id    # 中文：法规文件

policy_version_id    # 中文：法规版本

article_id    # 中文：条

paragraph_id    # 中文：款 / 段

item_id    # 中文：项

text_span    # 中文：直接支持判断的条文片段

source_url    # 中文：官方来源链接

source_hash    # 中文：抓取时保存的来源文本 / 文件哈希

retrieved_at    # 中文：抓取时间
```

---

# 五十五、核心心智模型 ㉔
# `WholeDocumentCitation` 可能无法审计

\[
\boxed{
DocumentLevelCitation
<
ArticleLevelEvidence
}
\]

**中文业务释义：** 对精确合规 Finding 而言，能定位到条、款、项的证据通常比只引用整份文件更容易审计。这里的 `<` 表示证据精度层级，不是法律效力大小。

---

# 五十六、Multi-source Legal Support
## 一个 Finding 可能需要多份法源

例如某个差别歧视 Finding 可能同时需要：

```text
GovernmentProcurementLaw    # 中文：原则性公平竞争 / 市场准入基础

ImplementationRegulation    # 中文：不合理限制、差别待遇的具体规则

DepartmentRule    # 中文：资格、评分、程序的细化要求

SpecialInspectionGuide    # 中文：专项整治检查和处理口径
```

所以：

\[
\boxed{
OneFinding
\neq
OneCitation
}
\]

**中文业务释义：** 一个风险发现项 ≠ 永远只需要一条法规引用。

---

# 五十七、核心心智模型 ㉕
# 法规证据也要形成 Evidence Graph

\[
\boxed{
Finding
\rightarrow
LegalProposition
\rightarrow
LegalSource
\rightarrow
ArticleSpan
}
\]

**中文业务释义：** 风险发现 → 需要证明的法律命题 → 支持该命题的法源 → 具体条款证据片段。

---

# 五十八、Legal Proposition
## 先说“要证明什么”，再找法条

错误流程：

```text
先搜到一个看起来相关的法规
→
再硬解释它支持结论
```

正确流程：

```text
legal_proposition    # 中文：当前 Finding 需要证明的具体法律 / 政策命题

candidate_sources    # 中文：可能支持该命题的法源

support_test    # 中文：条文是否真的支持这个命题
```

所以：

\[
\boxed{
CitationSearch
\rightarrow
PropositionSupportTest
}
\]

**中文业务释义：** 找到候选引用之后，还必须验证它是否支持当前具体法律命题。

---

# 五十九、Staleness
## 法规索引过期怎么办？

即使数据库本身设计正确，也可能：

> 最新文件已经发布，但索引尚未更新。

因此保存：

```text
last_source_check_at    # 中文：最近一次检查官方来源时间

index_built_at    # 中文：当前检索索引生成时间

source_version_hash    # 中文：官方来源版本指纹

freshness_sla    # 中文：法规库允许的最大更新延迟

stale_status    # 中文：索引是否已超过允许新鲜度
```

---

# 六十、核心心智模型 ㉖
# `FreshModel` 不等于 `FreshLaw`

\[
\boxed{
ModelKnowledgeFreshness
\neq
LegalCorpusFreshness
}
\]

**中文业务释义：** 模型知识新旧 ≠ 法规知识库是否已经同步最新官方规则。

生产系统必须把：

> 法规更新机制

独立于：

> 模型训练更新时间。

---

# 六十一、Legal Hot Update
## 为什么法规 RAG 必须支持热更新？

如果新规发布：

> 不应该重新训练整个 LLM 才能使用。

应该：

```text
ingest_new_source    # 中文：抓取新的官方法规政策文本

verify_metadata    # 中文：确认发文机关、文号、时间、状态

create_policy_version    # 中文：建立新法规版本

update_relation_graph    # 中文：建立修改 / 替代 / 实施等关系

rebuild_incremental_index    # 中文：增量更新检索索引

run_regression_tests    # 中文：运行法规检索和适用性回归测试

publish_policy_snapshot    # 中文：发布新的Policy Snapshot
```

所以：

\[
\boxed{
PolicyUpdate
\neq
ModelRetraining
}
\]

**中文业务释义：** 法规政策更新 ≠ 必须重新训练模型；法规知识应当能够独立热更新。

---

# 六十二、核心心智模型 ㉗
# `PolicySnapshot` 是可重放审计的核心

每次完整项目审查必须绑定：

```text
policy_snapshot_id    # 中文：本次审查使用的法规政策快照

snapshot_created_at    # 中文：快照生成时间

included_policy_versions    # 中文：快照包含的法规版本

source_hashes    # 中文：各官方来源指纹

index_version    # 中文：法规检索索引版本

resolver_version    # 中文：适用性解析器版本
```

这样半年以后才能回答：

> “当时系统为什么引用的是这条法规？”

---

# 六十三、Legal RAG Finding Trace
## 法规检索轨迹

建议：

```text
legal_retrieval_id    # 中文：法规检索记录标识

task_id    # 中文：对应合规任务

query_text    # 中文：实际法规检索问题

query_metadata    # 中文：时点、地区、预算级次、事项等元数据

candidate_policy_ids    # 中文：初始候选法规

retrieval_scores    # 中文：词法 / 向量检索得分

rerank_scores    # 中文：法规重排得分

filtered_out_candidates    # 中文：被版本 / 辖区 / 范围过滤掉的候选

applicability_results    # 中文：各候选法规适用性结果

selected_legal_basis    # 中文：最终进入Finding的法源

citation_spans    # 中文：具体条款证据

conflict_state    # 中文：是否存在规则冲突

human_review_required    # 中文：是否需要人工法规适用复核
```

---

# 六十四、核心心智模型 ㉘
# 被过滤掉的法规也值得保存

\[
\boxed{
ExcludedCandidate
\Rightarrow
ExclusionReason
}
\]

**中文业务释义：** 一个高相关法规最终没有被使用 ⇒ 也应该记录为什么被排除，例如尚未生效、已废止、地区不符或事项不符。

这对：

> 审计 Legal RAG 是否“漏法 / 错法”

非常重要。

---

# 六十五、Hard Negative
## 法规 RAG 的高难负例

Stage 12 必须重点加入：

```text
HardNegative_OldVersionSameTitle
# 中文：标题相同、文本非常相似，但属于旧版本 / 被替代版本

HardNegative_PublishedNotEffective
# 中文：正式发布、语义完全相关，但项目时点尚未生效

HardNegative_WrongJurisdiction
# 中文：规则内容正确，但只适用于其他省份 / 预算层级

HardNegative_DraftPolicy
# 中文：征求意见稿内容高度相关，但并非现行有效规则

HardNegative_InterpretationAsRule
# 中文：官方解读 / 答复有参考价值，但不能伪装成规范性法条

HardNegative_CurrentRuleForHistoricalProject
# 中文：今天有效的规则被错误用于过去项目

HardNegative_HistoricalRuleForCurrentProject
# 中文：旧规则被错误用于当前项目

HardNegative_GeneralRuleMissingException
# 中文：一般规则召回正确，但漏掉决定结论翻转的例外

HardNegative_SameArticleNumberDifferentDocument
# 中文：不同法规都有“第二十条”，不能只按条号匹配

HardNegative_NewsInsteadOfOfficialSource
# 中文：新闻摘要文本相关，但不应替代官方正式来源
```

---

# 六十六、Counterfactual Pair
## 法规 RAG 反事实样本

### Pair A：生效日前一天 / 生效日后一天

```text
event_time = 2026-09-30    # 中文：新办法生效日前一天
policy = 财库〔2026〕12号
# 中文：新《紧急采购管理暂行办法》尚未施行
```

### Pair B

```text
event_time = 2026-10-01    # 中文：新办法正式施行日
policy = 财库〔2026〕12号
# 中文：进入施行期，但还需继续检查项目是否符合紧急采购定义和范围
```

只改变：

> `event_time`

就可能改变：

> `status_at_event_time`。

---

### Pair C：中央预算 / 地方预算

```text
budget_level = CENTRAL
# 中文：中央预算项目
```

### Pair D

```text
budget_level = LOCAL    # 中文：地方预算项目
jurisdiction = 某省
# 中文：地方预算项目，需要解析对应省级规则来源
```

只改变：

> 预算级次和辖区，

公开招标数额标准的具体规则来源就可能发生变化。

---

### Pair E：官方正式通知 / 新闻摘要

```text
source_role = NORMATIVE_POLICY_DOCUMENT
# 中文：正式政策文件
```

### Pair F

```text
source_role = NEWS_SUMMARY
# 中文：新闻摘要
```

内容可能高度相似，

但：

> Source Authority 和 Citation Role 完全不同。

---

# 六十七、核心心智模型 ㉙
# Legal RAG 最需要学会的是“拒绝错误相关性”

普通 RAG 追求：

> 找到更多相关文本。

Legal RAG 更重要的是：

> **不要把错误时间、错误地区、错误版本、错误法源类型的高相关文本当成适用规则。**

所以：

\[
\boxed{
LegalRAGQuality
=
RelevantRecall
+
ApplicabilityPrecision
}
\]

**中文业务释义：** 法规 RAG 质量 = 相关法源召回能力 + 适用法规筛选精度。

---

# 六十八、Legal RAG Benchmark
## `ProcurementLegalRAG_V1` 应该测什么？

至少包括：

```text
policy_document_recall_at_k    # 中文：正确法规文件Recall@K

article_recall_at_k    # 中文：正确条文Recall@K

current_version_accuracy    # 中文：当前版本选择准确率

historical_version_accuracy    # 中文：历史项目旧版本选择准确率

effective_date_accuracy    # 中文：生效时间解析准确率

repeal_supersession_accuracy    # 中文：废止 / 替代关系解析准确率

transition_rule_accuracy    # 中文：新旧规则过渡条款判断准确率

jurisdiction_accuracy    # 中文：适用辖区判断准确率

budget_scope_accuracy    # 中文：中央 / 地方预算规则来源判断准确率

subject_matter_scope_accuracy    # 中文：法规事项范围判断准确率

legal_level_accuracy    # 中文：法律规范层级 / 文件类型识别准确率

conflict_detection_recall    # 中文：法规冲突发现召回率

conflict_resolution_safety    # 中文：不应由模型自行裁决时正确升级人工的比例

exception_recall    # 中文：例外 / 但书召回率

definition_dependency_recall    # 中文：关键定义条文联动召回率

official_source_precision    # 中文：正式官方来源使用精确率

draft_false_positive_rate    # 中文：草案被误作现行规则的比例

future_rule_false_positive_rate    # 中文：未来生效规则被提前适用的比例

wrong_jurisdiction_false_positive_rate    # 中文：错误地区规则被误用比例

citation_document_accuracy    # 中文：引用文件准确率

citation_article_accuracy    # 中文：条款定位准确率

citation_support_accuracy    # 中文：法条是否真正支持Finding的准确率

legal_basis_completeness    # 中文：多法源支撑是否完整

source_freshness_accuracy    # 中文：法规索引新鲜度判断准确率

policy_snapshot_reproducibility    # 中文：同一快照能否重放得到相同法规适用结果

human_escalation_accuracy    # 中文：复杂法规冲突 / 适用边界正确转人工的准确率
```

---

# 六十九、核心心智模型 ㉚
# `RetrievalRecall` 不等于 `LegalRAGReliability`

\[
\boxed{
RetrievalRecall
\neq
LegalRAGReliability
}
\]

**中文业务释义：** 能把相关法条搜出来 ≠ 法规 RAG 已经可靠；还必须证明版本、时间、辖区、例外和引用支持关系都正确。

---

# 七十、`ProcurementLegalRAG_V1` 建议目录

```text
ProcurementLegalRAG_V1/
# 中文：政府采购法规RAG与适用性推理根目录

├── registry/
│   # 中文：法规政策元数据、状态和版本注册表
│   ├── policies.jsonl    # 中文：法规政策逻辑文档
│   ├── policy_versions.jsonl    # 中文：具体版本
│   ├── status_history.jsonl    # 中文：生效、修改、废止、替代状态历史
│   └── source_registry.jsonl    # 中文：官方来源和来源权威性
│
├── temporal/
│   # 中文：时间、生效和历史重放
│   ├── valid_time.jsonl    # 中文：现实适用时间区间
│   ├── system_time.jsonl    # 中文：系统记录时间区间
│   ├── transition_rules.jsonl    # 中文：新旧规则过渡安排
│   └── event_time_resolver.py    # 中文：项目法律事件时间解析
│
├── jurisdiction/
│   # 中文：中央 / 地方、预算层级、地区和事项范围
│   ├── jurisdiction_graph.jsonl    # 中文：辖区 / 权限关系图
│   ├── budget_scope.jsonl    # 中文：中央和地方预算适用范围
│   └── resolver.py    # 中文：适用辖区解析器
│
├── hierarchy/
│   # 中文：法律规范层级和冲突关系
│   ├── legal_level.jsonl    # 中文：法律、行政法规、规章等层级
│   ├── relation_graph.jsonl    # 中文：修改、替代、实施、解释、例外关系
│   └── conflict_resolver.py    # 中文：明确可规则化冲突的解析及人工升级
│
├── corpus/
│   # 中文：法规正文结构化语料
│   ├── documents.jsonl    # 中文：法规文件
│   ├── articles.jsonl    # 中文：条文
│   ├── paragraphs.jsonl    # 中文：款 / 段
│   ├── items.jsonl    # 中文：项 / 目
│   ├── definitions.jsonl    # 中文：定义条款
│   ├── exceptions.jsonl    # 中文：例外 / 但书
│   └── cross_references.jsonl    # 中文：条文交叉引用
│
├── retrieval/
│   # 中文：词法、向量和重排检索
│   ├── lexical_index/    # 中文：文号、条号、固定术语精确检索
│   ├── embedding_index/    # 中文：法规语义向量索引
│   ├── hybrid_retriever.py    # 中文：混合检索器
│   └── legal_reranker.py    # 中文：融合来源、时间、辖区的法规重排器
│
├── applicability/
│   # 中文：法规适用性判断
│   ├── resolver.py    # 中文：适用性解析器
│   ├── state_schema.json    # 中文：适用 / 未生效 / 已废止等状态
│   └── exception_expander.py    # 中文：例外和特别规则扩展
│
├── citation/
│   # 中文：法源引用、证据片段和支持关系验证
│   ├── citation_atom.json    # 中文：条 / 款 / 项级引用对象
│   ├── validator.py    # 中文：引用正确性验证
│   └── support_checker.py    # 中文：法条是否真正支持法律命题
│
├── snapshots/
│   # 中文：每次项目审查绑定的法规政策快照
│   ├── policy_snapshots.jsonl    # 中文：快照元数据
│   └── source_hashes.jsonl    # 中文：官方来源指纹
│
├── tests/
│   # 中文：法规RAG、时间和辖区测试集
│   ├── temporal/    # 中文：生效日前后、历史版本、过渡期
│   ├── jurisdiction/    # 中文：中央 / 地方、不同地区
│   ├── hard_negative/    # 中文：旧版、草案、未来规则、错误地区
│   ├── conflicts/    # 中文：一般 / 特别、新 / 旧及跨机关冲突
│   ├── citation_support/    # 中文：引用与实质支持测试
│   └── source_authority/    # 中文：官方来源与二次来源区分
│
└── manifest.json
    # 中文：语料版本、索引版本、解析器版本、快照和Benchmark状态
```

---

# 七十一、Policy Version Schema 第一版

```text
policy_id    # 中文：法规政策逻辑身份

policy_version_id    # 中文：具体版本标识

title    # 中文：法规政策标题

document_number    # 中文：文号

issuer    # 中文：制定 / 发布机关

legal_level    # 中文：法律规范层级 / 文件类型

source_role    # 中文：正式规范文本 / 专项规则 / 官方解释 / 草案等角色

jurisdiction    # 中文：适用地区 / 范围

budget_scope    # 中文：中央 / 地方预算范围

subject_matter_tags    # 中文：资格、评分、政策、异常低价等事项标签

promulgation_date    # 中文：公布 / 发布日期

effective_from    # 中文：开始生效日期

effective_to    # 中文：结束适用日期

repeal_date    # 中文：废止日期

status    # 中文：草案 / 尚未生效 / 有效 / 废止 / 替代等状态

amended_by_ids    # 中文：修改该版本的后续规则

repealed_by_id    # 中文：废止该版本的规则

superseded_by_id    # 中文：替代该版本的后续规则

transition_rule_ids    # 中文：关联过渡条款

official_source_url    # 中文：官方来源

official_source_hash    # 中文：抓取版本指纹

recorded_at    # 中文：系统记录时间
```

---

# 七十二、Article Schema 第一版

```text
article_id    # 中文：具体法规版本中的条文标识

canonical_article_id    # 中文：跨版本逻辑条文身份

policy_version_id    # 中文：所属法规版本

chapter_id    # 中文：所属章

article_number_raw    # 中文：原始条文编号

article_text_raw    # 中文：条文原文

paragraph_ids    # 中文：款 / 段

item_ids    # 中文：项 / 目

definition_refs    # 中文：依赖的定义条款

exception_refs    # 中文：关联例外 / 但书

cross_reference_ids    # 中文：引用其他条文 / 文件

valid_from    # 中文：当前条文版本开始适用时间

valid_to    # 中文：当前条文版本结束适用时间

source_span    # 中文：官方来源中的精确证据位置
```

---

# 七十三、Applicability Decision Schema 第一版

```text
applicability_id    # 中文：法规适用性判断记录标识

task_id    # 中文：对应合规任务

policy_version_id    # 中文：待判断法规版本

project_event_type    # 中文：用于判断适用的业务事件类型

project_event_time    # 中文：具体业务事件时间

jurisdiction_result    # 中文：辖区匹配结果

budget_scope_result    # 中文：预算级次匹配结果

subject_scope_result    # 中文：事项范围匹配结果

temporal_result    # 中文：生效 / 失效 / 过渡状态

legal_level_result    # 中文：法律规范层级信息

supersession_result    # 中文：新旧替代关系

exception_result    # 中文：例外判断

conflict_result    # 中文：与其他规则冲突状态

applicability_state    # 中文：最终适用状态

reason_codes    # 中文：形成该适用状态的原因代码

evidence_refs    # 中文：支持适用性判断的法规和项目证据

human_review_required    # 中文：是否需要人工法律复核
```

---

# 七十四、本阶段最重要的 30 个核心心智模型

> **心智模型 ①：`RelevantLaw ≠ ApplicableLaw`。语义相关法规不等于当前项目适用法规。**

> **心智模型 ②：`LegalRetrieval ≠ SemanticSimilaritySearch`。法规检索不能退化为向量相似度搜索。**

> **心智模型 ③：`Published ≠ Effective`。正式发布不代表已经生效。**

> **心智模型 ④：`LatestPolicy ≠ ApplicablePolicy`。最新政策不一定适用于当前项目时点和范围。**

> **心智模型 ⑤：`LegalKnowledgeTime ≠ LegalValidTime`。系统知道规则的时间和规则现实适用时间必须分开。**

> **心智模型 ⑥：`OneProject ≠ OneLegalEventTime`。采购项目有公告、评审、合同、履约等多个法律事件时间。**

> **心智模型 ⑦：`NoRetroactivityDefault ≠ SkipTransitionAnalysis`。一般不溯及既往不意味着可以跳过过渡条款。**

> **心智模型 ⑧：`SupplierLocation ≠ ProcurementJurisdiction`。供应商注册地不是适用辖区的当然决定因素。**

> **心智模型 ⑨：`Jurisdiction = AuthorityScope + BudgetScope + GeographicScope + SubjectMatterScope`。辖区是多维规则范围。**

> **心智模型 ⑩：`LegalHierarchy ≠ SortByLevelAndPickTop1`。法律层级不能简化成一个数字排序器。**

> **心智模型 ⑪：`NewerDocument ≠ UniversalConflictWinner`。新文件不是所有冲突场景下的万能赢家。**

> **心智模型 ⑫：`LegalConflictDetected ≠ LLMChooseOne`。复杂法规冲突不能交给LLM自由选择。**

> **心智模型 ⑬：`SourceAuthority > SemanticSimilarity`。法规证据排序中，官方来源权威性优先于纯文本相似度。**

> **心智模型 ⑭：`OfficialInterpretation ≠ NormativeRule`。官方答复和解读不能与正式规范文本混成一个法源层级。**

> **心智模型 ⑮：`InspectionRule ≠ CompleteLegalBasis`。附件9专项规则不等于Finding完整法律依据。**

> **心智模型 ⑯：`LegalChunkBoundary = NormativeStructure + SemanticCompleteness`。法规切块优先尊重条款结构和完整含义。**

> **心智模型 ⑰：`ArticleNumber ≠ StableLegalIdentity`。条文编号不是跨版本稳定身份。**

> **心智模型 ⑱：`RuleContext = GeneralRule + Exception + Definition + CrossReference`。规则上下文必须包含一般规则、例外、定义和引用。**

> **心智模型 ⑲：`VectorDatabase ≠ LegalKnowledgeBase`。向量数据库不是完整法规知识库。**

> **心智模型 ⑳：`LegalQuery = Issue + Facts + Time + Jurisdiction + RuleType`。法规检索问题必须带业务事实、时间和辖区。**

> **心智模型 ㉑：`RetrievalTopK ≠ ApplicableLawSet`。Top-K相关文档只是候选，不是适用法集合。**

> **心智模型 ㉒：`CurrentCompliance ≠ HistoricalComplianceReplay`。今天项目审查和历史项目重放需要不同时间视图。**

> **心智模型 ㉓：`HighSemanticSimilarity ≠ HighLegalApplicability`。高语义相似度不等于高法律适配度。**

> **心智模型 ㉔：`NotApplicable ⇒ ReasonCode`。法规不适用必须能够说明具体原因。**

> **心智模型 ㉕：`ApplicablePolicy = Effective + JurisdictionMatch + ScopeMatch + EventMatch + ExceptionCheck`。生效只是适用性的一部分。**

> **心智模型 ㉖：`LegalCitation ≠ LegalSupport`。给出法条不等于法条真正支持Finding。**

> **心智模型 ㉗：`OneFinding ≠ OneCitation`。复杂Finding可能需要多层法源共同支撑。**

> **心智模型 ㉘：`ModelKnowledgeFreshness ≠ LegalCorpusFreshness`。模型知识新旧与法规库是否最新是两件事。**

> **心智模型 ㉙：`PolicyUpdate ≠ ModelRetraining`。法规热更新不应依赖重新训练LLM。**

> **心智模型 ㉚：`RetrievalRecall ≠ LegalRAGReliability`。召回法条只是开始，适用性和引用支持正确才决定法规RAG可靠性。**

---

# 七十五、把整个 Procurement Legal RAG 压成一张工程图

```text
Compliance Legal Question
# 中文：来自资格、技术、评分、政策、竞争等合规任务的法律问题
↓
Legal Query Planner
# 中文：抽取事项、项目事实、业务事件时间、预算级次、辖区和候选规则
↓
Policy Registry
# 中文：读取法规元数据、版本、效力状态、发文机关和来源
↓
Metadata Candidate Pool
# 中文：按事项、时间、地区、预算级次形成候选法规集合，同时保留必要历史 / 未来版本邻居
↓
Hybrid Retrieval
# 中文：文号 / 条号精确检索 + 向量语义检索
↓
Legal Reranker
# 中文：加入官方来源权威性、时间适配、辖区适配、版本适配进行重排
↓
Temporal Resolver
# 中文：解析生效、失效、过渡、历史适用和业务事件时间
↓
Jurisdiction Resolver
# 中文：解析中央 / 地方、预算层级、地理和事项范围
↓
Hierarchy / Conflict Resolver
# 中文：解析法律层级、特别 / 一般、新 / 旧和需要机关裁决的冲突
↓
Definition + Exception + Cross-reference Expansion
# 中文：补齐定义、例外、但书和关联条文
↓
Applicability Decision
# 中文：形成APPLICABLE / NOT_YET_EFFECTIVE / OUT_OF_JURISDICTION等明确状态
↓
Citation Validator
# 中文：验证文件、版本、条文和法条对Finding的实质支持关系
↓
Policy Snapshot + Audit Trace
# 中文：固定本次审查使用的法规快照、来源指纹和检索轨迹
↓
ProcurementLegalRAG_V1
# 中文：形成能做时间、辖区、版本和引用支持推理的政府采购法规RAG
```

---

# 七十六、脑中最后只留一句

> **政府采购法规 RAG 的本质，不是“把相关法条搜出来”，而是先把每一个法律问题绑定到具体项目事实、业务事件时间、预算级次和适用地区，再从版本化法规库中召回候选规则，解析其效力状态、适用范围、新旧关系、特别与一般规则、例外和冲突，最后验证具体条款是否真正支持当前 Finding；只有经过这一整条链，检索到的 Relevant Law 才可能升级成 Applicable Law。**

---

# 第十一课 · 第 12 阶段掌握测试

现在不回看正文，你应该能够解释：

```text
Relevant Law 为什么不等于 Applicable Law？
# 中文：为什么语义相关只是第一步？

Publication Date 和 Effective Date 为什么必须分开？
# 中文：财库〔2026〕12号为什么在2026年9月20日仍不能按生效规则使用？

Legal Status 为什么必须有DRAFT、PUBLISHED_NOT_EFFECTIVE、EFFECTIVE、REPEALED等状态？
# 中文：为什么法规文件进入数据库不代表永远可用？

Latest Policy 为什么不等于 Applicable Policy？
# 中文：最新文件还可能在哪些维度不适用？

Valid Time 和 System Time 有什么区别？
# 中文：法规现实适用时间和系统记录时间为什么必须分开？

为什么需要Bitemporal Model？
# 中文：它如何支持历史项目重放和系统责任审计？

One Project 为什么不等于 One Legal Event Time？
# 中文：公告、评审、合同、履约为什么可能对应不同规则适用时点？

Event-time Resolver 解决什么问题？
# 中文：为什么不能统一用“项目创建时间”判断所有法规？

为什么“不溯及既往”不能替代Transition Analysis？
# 中文：过渡条款、特别规则和业务事件时点为什么仍要解析？

Supplier Location 为什么不等于 Procurement Jurisdiction？
# 中文：适用规则到底主要看哪些维度？

中央预算和地方预算为什么必须进入Legal RAG Query？
# 中文：集中采购目录、限额标准、公开招标数额标准的规则来源怎样发生变化？

Jurisdiction 为什么是 Authority + Budget + Geographic + Subject Matter Scope？
# 中文：为什么不能只存一个province字段？

Legal Level 为什么不能由LLM临时猜？
# 中文：法律、行政法规、地方性法规、规章、政策文件为什么必须结构化登记？

Legal Hierarchy 为什么不等于Sort by Level and Pick Top1？
# 中文：特别 / 一般、新 / 旧和冲突裁决为什么会打破简单排序？

Newer Document 为什么不是Universal Conflict Winner？
# 中文：哪些冲突不能简单按发布时间决定？

Legal Conflict Detected 为什么不等于LLM Choose One？
# 中文：什么时候应该进入机关裁决逻辑或人工法律复核？

为什么 Source Authority 应优先于纯Semantic Similarity？
# 中文：官方正式来源和互联网二次转载怎样区分？

Official Interpretation 为什么不等于 Normative Rule？
# 中文：财政部门答复 / 政策解读应该怎样进入知识库？

附件9 Inspection Rule 为什么不等于Complete Legal Basis？
# 中文：专项检查规则和上位法律政策怎样共同支持Finding？

Legal Chunk 为什么应该按条、款、项和完整语义切分？
# 中文：固定Token切块会破坏什么？

Article Number 为什么不是Stable Legal Identity？
# 中文：跨版本引用为什么必须绑定policy_version_id？

为什么检索一般规则后必须主动搜索Exception？
# 中文：“但……除外”为什么能改变最终结论？

Vector Database 为什么不等于Legal Knowledge Base？
# 中文：法规库还缺哪些版本、状态和关系数据？

Legal Query Planner 为什么必须加入Time和Jurisdiction？
# 中文：只复述用户问题为什么不够？

Lexical + Embedding + Metadata 为什么需要一起使用？
# 中文：文号、条号、术语与语义问题分别由什么检索方式擅长？

Retrieval TopK 为什么不等于Applicable Law Set？
# 中文：Top-K之后还必须过哪些Resolver？

为什么历史版本不能从法规库直接删除？
# 中文：Historical Compliance Replay 怎样依赖旧版本？

Legal Reranker 为什么要加入Source Authority、Temporal Fit和Jurisdiction Fit？
# 中文：高语义相似法规为什么仍可能不能用？

Applicability State 为什么不能只有true / false？
# 中文：NOT_YET_EFFECTIVE、OUT_OF_JURISDICTION、SUPERSEDED等状态有什么审计价值？

Effective Date Passed 为什么不等于Automatically Applicable？
# 中文：范围、地区、项目事实、例外还需要检查什么？

财库〔2026〕2号怎样构成Temporal测试样本？
# 中文：2026-02-01前后怎样改变规则状态？

财库〔2026〕12号怎样构成Published-not-effective测试样本？
# 中文：2026-09-30和2026-10-01为什么是重要反事实对？

国办发〔2025〕34号怎样构成政策生效时间测试？
# 中文：2026-01-01前后为什么必须分开？

中央预算和地方预算为什么构成Jurisdiction / Budget Scope测试？
# 中文：同一法律术语为什么可能对应不同具体规则来源？

Legal Citation Correctness 为什么不等于Legal Support Correctness？
# 中文：引用对文件、版本、条文、实质支持分别要检查什么？

为什么Citation Atom最好到条 / 款 / 项级？
# 中文：整份文件级引用为什么不够精确？

One Finding 为什么不等于One Citation？
# 中文：复杂差别歧视Finding为什么可能需要多层法源共同支持？

什么是Legal Proposition？
# 中文：为什么应该先定义“要证明什么”，再找法条？

Model Knowledge Freshness 为什么不等于Legal Corpus Freshness？
# 中文：为什么法规更新必须独立于模型训练？

Policy Update 为什么不等于Model Retraining？
# 中文：法规热更新怎样通过Registry、Index和Snapshot完成？

Policy Snapshot 为什么是审计核心？
# 中文：半年后怎样重放系统当时使用的法规环境？

为什么Excluded Candidate也要保存Exclusion Reason？
# 中文：这怎样帮助检查Legal RAG有没有错过滤？

Legal RAG的Hard Negative有哪些？
# 中文：旧版、草案、未来规则、错误地区、新闻摘要为什么都必须进入测试？

Retrieval Recall 为什么不等于Legal RAG Reliability？
# 中文：真正的法规RAG还必须证明哪些适用性和引用能力？
```

如果这些能够完整解释：

\[
\boxed{
第十一课第12阶段真正掌握
}
\]

**中文业务释义：** 如果能够从“相关法条检索”继续推到法规版本、生效时间、业务事件时间、中央 / 地方预算、辖区范围、法律层级、特别 / 一般、新 / 旧、例外、冲突、官方来源、条款引用和Policy Snapshot，并能解释为什么系统在不确定时必须拒绝自行选法，就说明真正掌握了本阶段。

---

# 下一阶段：第十一课 · 第 13 阶段
# SFT / Hard Cases / Counterfactual Training：训练真正的合规判断能力
## 怎样让模型学习“为什么构成风险、为什么不构成风险、哪个事实变化会让结论翻转”，而不是背关键词？

下一阶段将正式建立：

# `ProcurementComplianceLM_V1-RC`

最重要的边界：

\[
\boxed{
ComplianceTraining
\neq
KeywordMemorization
}
\]

**中文业务释义：** 合规训练 ≠ 让模型记住“本地、注册资本、品牌、证书”等高风险关键词；真正需要学习的是规则适用条件、业务必要性、例外、证据和结论翻转的 Decision Boundary——判断边界。
