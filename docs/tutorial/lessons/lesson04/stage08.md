# 第四课 · 第 8 阶段：政府采购 Label Schema 与标注体系
## 为什么“有风险 / 没风险”两个标签，远远不够训练一个真正能工作的政府采购专业模型？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **ClauseUnit ▼ 事实层 What does the document say? ▼ 判断层 Is there a potential risk? ▼ 分类层 What kind of risk? ▼ 证据层 Why / based on what? ▼ 不确定性层 Can we conclude confidently? ▼ 行动层 What should happen next? ▼ AnnotationSchema_V0.1**
2. **政府采购专业 Label Schema 的目标，不是把所有 Clause 压缩成“有风险 / 没风险”，而是把专家的判断拆成风险状态、风险类型、不确定性、理由、证据、行动建议和标注来源，让“专家脑子里的专业判断”第一次变成可以训练、可以评测、可以审计的数据结构。**
3. **missing ≠ fabricated**
4. **二百五十五、本阶段最重要的 7 个“≠”**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `Label Schema` | 标签结构：定义风险状态、类型、等级、证据等标注字段 |
| `Raw Document` | 原始文档：未经结构化处理的采购文件源材料 |
| `ANN` | ANN/近似最近邻：在大规模向量中快速寻找相似项 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Citation` | 引用：把生成结论和具体来源建立可追踪链接 |
| `Dataset` | 数据集：按统一 Schema、版本和质量标准组织的样本集合 |
| `SFT` | 监督微调：用监督样本继续更新模型参数 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `Sample` | 样本：具有明确输入、目标和来源的一条训练/评测记录 |

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

到第 7 阶段为止，我们已经完成：

```text
Raw Document
      ↓
ParsedDocument
      ↓
ClauseUnit
      ↓
CleanClause
      ↓
DedupedClauseSet
      ↓
DatasetSplit
      ↓
LeakageAudit
```

现在的数据已经开始具备几个非常重要的性质：

```text
文字基本可信
来源可以追溯
结构可以定位
重复关系已知
Train / Validation / Test 有边界
Benchmark 泄漏开始受到控制
```

接下来终于轮到一个看起来最直观、实际上非常容易把整个项目带歪的问题：

# 专家到底应该标什么？

假设我们给专家看这条采购要求：

> “供应商须在本市设有固定服务机构。”

如果只让专家选择：

```text
有风险
没风险
```

看起来很简单。

但很快就会出现一堆问题：

```text
是什么类型的风险？

风险来自哪几个字？

为什么认为有风险？

是否需要结合项目履约场景？

有没有可以支持判断的依据？

如果依据不足怎么办？

是“确定有问题”，还是“需要重点复核”？

应该删除、修改，还是只需要补充说明？

一个Clause同时涉及资格和评分怎么办？
```

如果这些问题没有统一定义，不同专家最终会产生完全不同的数据语言。

一个专家写：

```text
违规
```

另一个写：

```text
疑似不合理限制
```

另一个写：

```text
建议修改
```

还有一个写：

```text
需结合具体项目判断
```

这些到底是不是同一个标签？

机器不知道。

所以第 8 阶段真正解决的，是：

> **把专家脑子里的专业判断，变成机器能够稳定学习、稳定评测、稳定统计的一套结构化语言。**

最终产物是：

# `AnnotationSchema_V0.1`

---

# 一、本阶段只解决一个核心问题

这一阶段的核心问题可以压缩成：

> **怎样设计一套 Label Schema，让同一个采购条款被不同专家看到时，他们至少在“应该回答哪些问题、答案应该用什么结构表达”这件事上保持一致？**

注意，这和下一阶段不同。

第 8 阶段先解决：

> **标什么。**

第 9 阶段才解决：

> **不同专家怎么把它标一致。**

这两个问题必须分开。

---

# 二、先建立 6 个核心心智模型

第一，**Label 不是一个词，而是一组结构化判断。** 对 ProcurementAI 来说，一个专业判断通常至少包含“有没有风险、是什么类型、为什么、依据在哪里、是否需要人工复核”。

第二，**事实、判断、证据和建议必须分开。** “原文写了什么”属于事实；“可能存在风险”属于判断；“依据是什么”属于证据；“建议怎么修改”属于行动建议。四者混在一个字段里，后面几乎无法稳定训练和评测。

第三，**Unknown 不等于 No。** “没有风险”和“证据不足，目前无法判断”是完全不同的状态。强迫专家二选一，会制造大量假标签。

第四，**一个 Clause 可以同时拥有多个维度的标签。** 风险类别、复核优先级、证据状态和建议动作并不是互斥的一维分类。

第五，**Label Schema 必须服务下游任务。** 如果未来要做分类、SFT、RAG、审查报告和 Benchmark，同一个 Master Annotation 应该能够派生出多个 Task View。

第六，**Gold Label 不是“专家随手写的一句话”。** 它必须有 Schema、定义、证据、来源、版本和状态。

把整个阶段先压成一张脑内地图：

```text
ClauseUnit
    │
    ▼
事实层
What does the document say?
    │
    ▼
判断层
Is there a potential risk?
    │
    ▼
分类层
What kind of risk?
    │
    ▼
证据层
Why / based on what?
    │
    ▼
不确定性层
Can we conclude confidently?
    │
    ▼
行动层
What should happen next?
    │
    ▼
AnnotationSchema_V0.1
```

---

# 三、为什么二分类远远不够？

假设有下面三条 Clause。

第一条：

> “供应商应具有独立承担民事责任的能力。”

第二条：

> “供应商必须为本市注册企业。”

第三条：

> “中标后应在项目所在地提供7×24小时现场服务。”

如果我们只有：

```text
risk = true / false
```

机器最后只学会：

> “哪些句子长得像风险句子。”

但它并不知道风险到底来自：

```text
供应商主体资格？
地域条件？
履约要求？
评分规则？
技术参数？
```

更麻烦的是，第二条和第三条都出现：

```text
本市 / 项目所在地
```

如果只是关键词学习，模型很容易形成：

\[
\boxed{
出现地域词
\Rightarrow
风险
}
\]

这显然不是我们希望得到的专业能力。

第三条如果是在合理履约场景中：

> 可能需要结合项目实际进一步判断。

所以模型必须学会：

# Context matters

而不是：

# Keyword = Label

---

# 四、一个专业 Annotation 应该像“病例”，而不是“红绿灯”

生活里可以把二分类想成红绿灯：

```text
红
绿
```

简单任务够用。

但专业审查更像医生写病历。

医生不会只写：

```text
有病 = true
```

而会记录：

```text
症状是什么
疑似什么问题
严重程度
检查依据
哪些结果支持
哪些结果还缺失
下一步建议
```

政府采购专业标注也是一样。

我们希望专家输出的不是：

> 一个 Yes / No。

而是：

# Structured Expert Judgment

---

# 五、先把一条 Sample 拆成四层

一个成熟样本最好区分四层：

| 层级 | 回答的问题 | 示例 |
|---|---|---|
| **Source / Fact** | 原文件写了什么？ | “供应商须在本市注册” |
| **Judgment** | 是否存在潜在风险？ | `true` |
| **Evidence / Reasoning** | 为什么？依据是什么？ | 地域条件需要进一步审查其必要性 |
| **Action** | 下一步怎么办？ | 修改 / 补充依据 / 人工复核 |

为什么一定要拆？

因为这四层：

> 未来会用于不同任务。

分类模型可能只学：

```text
Judgment
```

SFT 模型可能学：

```text
Judgment + Rationale
```

RAG 系统重点验证：

```text
Evidence
```

产品工作流可能主要使用：

```text
Action
```

---

# 六、因此 Master Annotation 不应该等于最终 Prompt 输出

这是非常重要的一点。

不要因为现在准备用 SFT，就把数据库直接设计成：

```json
{
  "question": "...",
  "answer": "..."
}
```

这太早绑定某一种训练形式。

更专业的是：

```text
Master Annotation
        │
        ├── Classification View
        ├── SFT View
        ├── Evaluation View
        ├── RAG Evidence View
        └── Product Review View
```

也就是之前一直强调的：

\[
\boxed{
RichMasterData
\rightarrow
TaskSpecificViews
}
\]

---

# 七、第一核心字段：`risk_present`

最基本的问题仍然需要回答：

> 这条 Clause 是否存在需要关注的潜在合规风险？

第一版不要只用：

```text
true
false
```

更稳健的设计可以是：

```text
true
false
uncertain
```

或者在数据库内部设计成：

```text
risk_present = true / false / null
```

再配合：

```text
judgment_status
```

但语义必须明确。

---

# 八、为什么一定要允许 `uncertain`？

假设条款：

> “供应商应在项目所在地具备及时提供现场服务的能力。”

只看这一句话，我们不知道：

```text
项目是什么？
现场响应是否属于核心履约需求？
服务半径是否客观必要？
是否要求投标前就已经设立机构？
还是只要求中标以后具备服务能力？
```

如果强迫专家：

```text
Risk
No Risk
```

专家可能只能猜。

于是 Dataset 把：

> 不确定性

伪装成：

> 确定真相。

这是很危险的。

---

# 九、所以一个成熟系统必须允许说

# 我现在不知道

可以记成：

\[
\boxed{
Unknown
\neq
Negative
}
\]

---

# 十、这也是为什么我们之前一直保留 `needs_review`

比如：

```json
{
  "risk_present": "uncertain",
  "needs_review": true
}
```

它表达的是：

> 目前证据不足，必须进一步复核。

而不是：

> 没风险。

---

# 十一、`risk_present` 和 `needs_review` 是不是重复？

不是。

看四种情况：

| risk_present | needs_review | 含义 |
|---|---:|---|
| `true` | false | 风险判断已经相对明确 |
| `true` | true | 已发现风险，但仍需专家确认程度或依据 |
| `false` | false | 当前认为没有明显风险 |
| `uncertain` | true | 信息不足，不能可靠判断 |

这比：

```text
0 / 1
```

丰富得多。

---

# 十二、第二核心字段：`risk_type`

现在进入我们的采购风险 taxonomy。

第一版已经确定五个主类：

| Code | Risk Type | 含义 |
|---|---|---|
| **A** | Supplier Qualification | 供应商资格 |
| **B** | Technical Requirement | 技术参数 |
| **C** | Commercial Requirement | 商务要求 |
| **D** | Scoring Rule | 评分标准 |
| **E** | Procurement Requirement | 采购需求 |

这五类不是在说：

> “只要属于这个章节就有风险。”

而是在说：

> **如果有风险，它主要属于哪个业务维度。**

再次强调：

\[
\boxed{
SectionType
\neq
RiskType
}
\]

---

# 十三、例如某条 Clause 位于“技术要求”

```text
CPU核心数不少于32核。
```

它的：

```text
section_type
```

可能是：

```text
technical_requirement
```

但：

```text
risk_present
```

完全可能是：

```text
false
```

不能因为它在技术章节：

> 就标成技术风险。

---

# 十四、`risk_type` 应该单选还是多选？

这是一个真正值得设计的问题。

假设：

> “供应商须具有某品牌原厂认证，并在本市设有服务机构，否则不得参与投标。”

它可能同时涉及：

```text
供应商资格
品牌/技术相关限制
地域相关条件
```

如果强迫：

> 只能选一个 Risk Type，

可能丢信息。

---

# 十五、所以第一版可以采用：

```text
primary_risk_type
```

加：

```text
secondary_risk_types
```

例如：

```json
{
  "primary_risk_type": "A",
  "secondary_risk_types": ["B"]
}
```

这样既有一个主标签，方便统计和基础分类，

又不强迫现实世界：

> 只能属于一个盒子。

---

# 十六、这就是 Multi-label 思维

传统 Multi-class：

\[
y \in \{A,B,C,D,E\}
\]

意味着：

> 五选一。

Multi-label：

\[
y \subseteq \{A,B,C,D,E\}
\]

意味着：

> 可以同时属于多个类别。

我们的 Master Schema：

> 最好保留这种表达能力。

最终某个具体模型如果只做单分类：

> 再派生 Primary Label。

---

# 十七、不要把模型限制反过来污染数据设计

如果第一个 Baseline 只能做：

```text
5-class classification
```

不要因此把 Master Data 设计成：

> 永远只能五选一。

这叫：

# Schema should outlive Model V0.1

Schema 的生命周期：

> 应该比第一版模型更长。

---

# 十八、第三层：Risk Subtype

五个一级类别仍然比较粗。

例如 A 类“供应商资格”中可能继续出现：

```text
地域条件
成立年限
注册资本
特定证书
企业规模
业绩条件
人员条件
所有制/组织形式相关条件
```

这里的名称只是教学 taxonomy 示例，不是自动法律结论。

---

# 十九、为什么需要 Subtype？

假设模型总体：

```text
Qualification Recall = 90%
```

看起来很好。

但进一步发现：

```text
地域条件 = 97%
成立年限 = 94%
业绩条件 = 89%
特殊证书 = 63%
```

真正问题立刻暴露。

---

# 二十、这就是 Label Schema 对评测的价值

没有细粒度标签：

> 你只能知道“资格风险整体不好”。

有 Subtype：

> 才知道到底哪里不好。

---

# 二十一、但 Subtype 不要第一天设计 200 个

这是常见错误。

专家坐下来一拍脑袋：

```text
一级分类 15个
二级分类 80个
三级分类 320个
```

最终大部分 Label：

> 只有两三条样本。

几乎无法：

```text
训练
统计
评测
保持一致
```

---

# 二十二、正确路线应该是

```text
先用少量稳定的大类
        ↓
积累真实数据
        ↓
观察高频失败模式
        ↓
再扩展Subtype
```

可以记成：

# Taxonomy grows with evidence

而不是：

# Taxonomy grows with imagination

---

# 二十三、第四核心字段：`risk_level`

这个字段特别容易被误解。

这里的 `risk_level` 不应该被设计成：

> AI 自动作出的最终法律责任结论。

更适合作为：

# Operational Review Priority

审查工作中的风险/复核优先级。

例如：

```text
low
medium
high
needs_review
```

---

# 二十四、为什么要强调 Operational？

因为 ProcurementAI 的目标首先是：

> 辅助审查和风险筛查。

不是让模型单独宣布：

> “违法等级三级。”

这既不符合我们的工程任务，也不符合谨慎的专业工作方式。

---

# 二十五、例如 High 可以定义为

> 若该判断成立，可能对供应商准入、竞争范围、评分结果等产生较大影响，应优先人工复核。

注意这里的关键词：

```text
若判断成立
可能
应优先复核
```

不是：

> 自动法律裁决。

---

# 二十六、Risk Level 必须写定义，而不能只写三个词

如果标注指南只写：

```text
High
Medium
Low
```

专家 A 的 High：

> “我觉得挺严重。”

专家 B 的 High：

> “我觉得一定违法。”

专家 C 的 High：

> “我觉得领导会关注。”

数据必然乱掉。

---

# 二十七、所以 Label Schema 必须配

# Operational Definition

例如概念上：

| Level | 工作定义 |
|---|---|
| Low | 存在轻微疑点或影响有限，可常规复核 |
| Medium | 有较明确风险信号，需要专家核查上下文及依据 |
| High | 可能显著影响准入、竞争、评分或重要采购条件，应优先复核 |
| Needs Review | 当前信息不足，暂不适合可靠分级 |

这些只是模型工程和标注工作定义。

具体项目的正式法律判断：

> 仍需结合事实、有效规范和专业审查。

---

# 二十八、第五核心字段：`rationale`

现在进入最重要的一个部分。

假设专家标：

```json
{
  "risk_present": true,
  "risk_type": "A"
}
```

这够不够？

对于训练一个分类器：

> 勉强够。

对于训练一个真正能工作的专业 LLM：

> 不够。

因为模型最终还要回答：

> 为什么？

---

# 二十九、所以我们需要：

```text
rationale
```

即：

> 专业判断理由。

但这里有一个巨大风险。

如果完全让专家自由写：

专家 A：

> “存在地域限制。”

专家 B：

> “该条件将供应商注册地限定为本市，需审查该地域条件是否与项目履约存在客观必要联系。”

专家 C：

> “不合理。”

---

# 三十、三条都可能在表达类似东西

但训练价值：

> 差距巨大。

所以 Rationale 本身也需要：

# Structure

---

# 三十一、一个好的 Rationale 可以拆成

```text
Observed Fact
      ↓
Risk Concern
      ↓
Context Needed
      ↓
Basis / Evidence
      ↓
Conclusion Scope
```

例如：

```text
Observed Fact:
条款要求供应商须在本市注册。

Risk Concern:
该要求把供应商注册地作为准入条件。

Context Needed:
需要确认项目是否存在足以支持该限制的特殊客观必要性。

Conclusion Scope:
建议作为资格条件风险点进入人工复核。
```

---

# 三十二、注意这里没有直接说

> “一定违法。”

而是清楚地区分：

```text
事实
关注点
还缺什么
当前结论
```

这非常适合专业 AI。

---

# 三十三、第六核心字段：Evidence

真正高质量的数据不能只有：

> 专家感觉。

最好保存：

```text
evidence
```

---

# 三十四、Evidence 至少可以分两类

第一类：

# Source Evidence

也就是：

> 招标文件里的原始证据。

例如：

```text
第三章 / 供应商资格条件 / 第（二）项
```

---

# 三十五、第二类：

# External Basis

例如：

```text
适用法律
法规
规范性文件
正式政策
权威解释
```

它回答：

> 判断有什么外部依据？

---

# 三十六、因此 Evidence 不能只是一个大字符串

第一版可以概念设计：

```json
{
  "evidence": [
    {
      "type": "source_clause",
      "document_id": "DOC-001",
      "page": 27,
      "text_span": "供应商须在本市注册"
    }
  ]
}
```

---

# 三十七、外部依据可以：

```json
{
  "basis": [
    {
      "source_id": "REG-001",
      "citation_status": "verified",
      "relevance": "supports_review"
    }
  ]
}
```

---

# 三十八、为什么要有 `citation_status`？

因为专家可能知道：

> “这里应该有相关依据。”

但一时没有确认：

```text
具体规范名称
条号
有效状态
适用地域
```

如果强迫填：

> 很容易制造假引用。

---

# 三十九、所以 Evidence 可以拥有状态

```text
verified
candidate
missing
not_required
```

这里最重要的是：

# missing ≠ fabricated

没有找到依据时：

> 宁可标 missing。

不要为了 Schema 完整：

> 随便填一条法规。

---

# 四十、这和 Stage 3 Baseline 里的原则完全一致

> **Never invent legal basis.**

这是 ProcurementAI 非常重要的一条底线。

---

# 四十一、`evidence` 和 `rationale` 有什么区别？

Rationale：

> 为什么这样判断。

Evidence：

> 判断依靠哪些可验证的信息。

例如：

```text
Rationale:
该资格条件限定供应商注册地域，需要审查其与项目需求之间的必要性。

Evidence:
原文件第三章资格条件第2项……
```

如果还有外部法规：

> 再单独引用。

---

# 四十二、所以：

\[
\boxed{
Reasoning
\neq
Evidence
}
\]

模型说得很有道理：

> 不等于证据真实存在。

这是未来评测里非常重要的区分。

---

# 四十三、第七核心字段：`suggested_action`

发现风险以后：

> 接下来怎么办？

可能包括：

```text
retain
revise
remove
clarify
request_evidence
human_review
```

但建议动作不一定总能直接给出。

---

# 四十四、例如：

> “供应商应在项目所在地具备2小时现场服务能力。”

如果项目本身确实需要：

> 极短现场响应，

可能要结合：

```text
项目性质
履约地点
服务要求
市场供给情况
```

判断。

这时最合理的 Suggested Action 可能不是：

```text
remove
```

而是：

```text
human_review
```

或者：

```text
clarify_business_necessity
```

---

# 四十五、这就是为什么系统不能把

```text
发现潜在风险
```

自动等价为：

```text
删除条款
```

---

# 四十六、可以写成：

\[
\boxed{
RiskDetection
\neq
RemediationDecision
}
\]

发现问题：

> 和最终怎么处理，

是两个任务。

---

# 四十七、现在第一次把核心 Annotation 拼起来

例如：

```json
{
  "sample_id": "SAMPLE-00178",
  "clause_id": "CLAUSE-00178",

  "judgment": {
    "risk_present": true,
    "primary_risk_type": "A",
    "secondary_risk_types": [],
    "risk_subtype": "geographic_requirement",
    "risk_level": "high",
    "needs_review": true
  },

  "rationale": {
    "observed_fact": "条款将供应商注册地限定为本市。",
    "risk_concern": "该条件可能限制潜在供应商参与范围。",
    "context_needed": "需要核查该地域限制是否存在与采购需求直接相关的客观必要性。",
    "conclusion_scope": "建议作为资格条件风险点优先人工复核。"
  },

  "evidence": {
    "source_evidence": [],
    "external_basis": [],
    "citation_status": "missing"
  },

  "suggested_action": "human_review",

  "annotation_status": "draft",

  "schema_version": "annotation_schema_v0.1"
}
```

这只是：

> 第一版概念 Schema。

不是法律结论模板。

---

# 四十八、为什么 `annotation_status` 必须存在？

因为一条 Annotation 的状态可能是：

```text
draft
reviewed
adjudicated
gold
```

---

# 四十九、`draft` 是什么？

一个专家：

> 初次标注。

---

# 五十、`reviewed` 是什么？

已经：

> 被第二人复核。

---

# 五十一、`adjudicated` 是什么？

两个专家意见不一致以后：

> 经过裁决。

---

# 五十二、`gold` 是什么？

达到当前项目定义的：

> Benchmark 质量要求。

这部分会在第 9 阶段详细讲。

现在只需要知道：

\[
\boxed{
LabelValue
\neq
LabelQualityStatus
}
\]

一个 Label 写着 `true`：

> 不代表它已经是 Gold。

---

# 五十三、非常重要：Negative Label 也需要理由

很多标注项目只要求：

风险样本：

> 写解释。

无风险样本：

> 点 `No Risk` 就结束。

这会造成一个严重问题：

> 我们不知道专家是真的认真判断过，还是随手点了 No。

---

# 五十四、因此高质量 Gold Set 里的负样本

最好至少记录：

```text
why_not_risk
```

或者结构化：

```text
negative_rationale
```

例如：

> “该要求描述的是中标后的履约能力，并未将供应商注册地作为投标资格条件；基于当前上下文未发现明显准入地域限制。”

---

# 五十五、这对 Hard Negative 特别重要

未来模型最容易学成：

```text
看到本地
→ 报风险
```

真正高价值负样本应该告诉模型：

> 为什么虽然词很像风险，但是这里不是。

---

# 五十六、所以：

\[
\boxed{
GoodNegative
\neq
NoLabel
}
\]

好负样本：

> 也应该有清楚的专业边界。

---

# 五十七、这为第 10 阶段 Hard Negative 做准备

到时候我们会专门构造：

```text
看起来很像风险
但实际上需要不同判断
```

的数据。

---

# 五十八、现在进入一个非常容易混淆的问题

# `false`、`unknown`、`missing`、`not_applicable`

这四个绝对不能混。

---

# 五十九、`false`

表示：

> 专家已经进行了判断，目前认为该风险不存在。

---

# 六十、`unknown`

表示：

> 当前信息不足，无法可靠判断。

---

# 六十一、`missing`

表示：

> 这个字段本来应该有，但数据目前缺失。

例如：

> 专家还没填写 Rationale。

---

# 六十二、`not_applicable`

表示：

> 这个字段对当前样本不适用。

例如：

无风险样本可能：

```text
risk_subtype = not_applicable
```

---

# 六十三、这四者如果都存成：

```text
null
```

以后谁也不知道：

> null 到底是什么意思。

---

# 六十四、所以优秀 Schema 必须定义：

# Null Semantics

数据库中的“空”：

> 也应该有含义。

---

# 六十五、例如可以设计

```text
risk_subtype = null
```

只允许在：

```text
risk_present = false
```

时出现。

但如果：

```text
risk_present = true
```

而 `risk_subtype = null`：

> 就触发 Schema Warning。

---

# 六十六、这就是数据契约再次出现

例如：

```text
if risk_present == true:
    primary_risk_type must exist
```

---

# 六十七、如果：

```text
needs_review == false
```

但：

```text
risk_present == uncertain
```

也可能：

> 逻辑矛盾。

---

# 六十八、因此 Annotation Schema 需要：

# Cross-field Validation

不是只检查：

> 每个字段有没有值。

还要检查：

> 字段之间是否逻辑一致。

---

# 六十九、第一版可以有这样的规则

```text
risk_present = true
→ primary_risk_type required

risk_present = uncertain
→ needs_review should usually be true

citation_status = verified
→ evidence source required

annotation_status = gold
→ rationale required
→ source provenance required
→ reviewer status required
```

这就是：

# Annotation Contract

---

# 七十、为什么 Schema Validation 非常重要？

假设收到：

```json
{
  "risk_present": false,
  "risk_level": "high"
}
```

程序如果不检查：

> 这条数据照样进入训练。

模型会看到：

```text
No Risk
+
High Risk
```

这不是训练模型。

这是：

> 训练精神分裂。

---

# 七十一、还有：

```json
{
  "risk_present": true,
  "primary_risk_type": null
}
```

可能说明：

> 标注没完成。

---

# 七十二、所以 Annotation Pipeline 不能只问：

> JSON 能不能解析？

还要问：

> 业务逻辑是否成立？

---

# 七十三、现在谈“证据粒度”

专家说：

> “依据政府采购相关规定。”

够不够？

对于真正的专业系统：

> 太弱。

---

# 七十四、理想情况下 Evidence 最终可以追到：

```text
source_name
article / clause
effective_time
jurisdiction
quoted_span / evidence_span
verification_status
```

但这是未来第 6 课法规 RAG 会进一步实现的。

第四课当前阶段只需要：

> Schema 留出位置。

---

# 七十五、也就是说

不要因为现在暂时没有完善法规库，就把 Schema 设计成：

```text
reason = "..."
```

一个字段塞全部。

应该从一开始就区分：

```text
rationale
```

和：

```text
evidence_refs
```

未来 RAG 才能无痛接上。

---

# 七十六、这就是好 Schema 的价值

它不是只满足：

> 今天。

而是能够支撑：

> 后面课程。

---

# 七十七、现在讨论 `risk_type` 是 Label 还是 Metadata

它是：

> Label。

因为模型未来：

> 可能需要预测它。

---

# 七十八、那 `project_id` 呢？

一般是：

> Metadata。

模型不需要预测：

```text
PROJECT-00152
```

---

# 七十九、那 `section_type` 呢？

它可以是：

> Input Metadata。

也可以成为某些辅助任务的 Label。

取决于：

> Task View。

---

# 八十、所以同一个字段在 Master Data 中

最好先定义：

# Semantic Role

例如：

| 字段 | Master Role |
|---|---|
| `clause_text` | Source |
| `section_type` | Structural Metadata |
| `risk_present` | Expert Label |
| `risk_type` | Expert Label |
| `rationale` | Expert Annotation |
| `evidence_refs` | Provenance / Evidence |
| `project_id` | Group Metadata |
| `annotation_status` | Quality Metadata |
| `schema_version` | Version Metadata |

这张区分非常重要。

---

# 八十一、为什么？

因为未来构造 SFT Dataset 时：

> 不能把所有字段都塞给模型。

第 7 阶段刚讲过：

> Metadata 可能产生 Leakage。

---

# 八十二、因此 Task View Builder 应明确写：

```text
Input Fields
Target Fields
Hidden Metadata
Audit Fields
```

---

# 八十三、例如 Classification View

Input：

```text
clause_text
section_path
allowed_context
```

Target：

```text
risk_present
primary_risk_type
```

隐藏：

```text
gold_rationale
expert_comment
future_outcome
```

---

# 八十四、SFT View

Input：

```text
target_clause
section_context
project_context
```

Target 可以是：

```text
risk_present
risk_type
reason
evidence_needed
suggested_action
```

---

# 八十五、Evaluation View

可能保留：

```text
Gold Label
Gold Rationale
Gold Evidence
Slice Metadata
Difficulty
```

但这些：

> 不会作为模型输入。

---

# 八十六、这就是：

# One Annotation → Multiple Task Views

---

# 八十七、现在讲 Structured Output

为什么我们希望模型最终不要只回答：

> “这条有风险。”

更好的输出可能是：

```json
{
  "risk_present": true,
  "risk_type": "supplier_qualification",
  "risk_level": "high",
  "needs_review": true,
  "reason": "...",
  "evidence_status": "needed",
  "suggested_action": "human_review"
}
```

---

# 八十八、Structured Output 的优势

首先：

> 更容易评测。

`risk_present`：

> 可以直接算 Precision / Recall。

`risk_type`：

> 可以做分类评测。

`needs_review`：

> 可以评估不确定性处理。

---

# 八十九、其次：

> 更容易进入产品。

UI 可以分别展示：

```text
风险类型
复核优先级
理由
证据
建议
```

而不是解析一大段自由文本。

---

# 九十、再次：

> 更容易发现模型具体哪里错。

例如：

```text
风险判断正确
风险类别错误
依据错误
建议过度
```

错误可以拆开。

---

# 九十一、这会直接连接第 8 课 Benchmark

以后不会只看：

```text
Answer Correct / Wrong
```

而会分别看：

```text
Risk Detection
Risk Type
Rationale
Citation
Abstention
Action
```

---

# 九十二、所以 Schema 其实是在定义未来 Benchmark

这是一个很深的关系：

\[
\boxed{
AnnotationSchema
\rightarrow
EvaluationSchema
}
\]

你今天没标的数据：

> 明天通常就评不了。

---

# 九十三、例如今天完全没有保存 Evidence

半年后想评：

# Citation Correctness

你会发现：

> 没有 Gold Evidence。

只能重新请专家标。

---

# 九十四、所以设计 Label Schema 时一定要问

> **一年以后，我们希望怎样评价模型？**

如果答案是：

> 要评法规依据是否正确，

今天最好：

> 留 Evidence 字段。

---

# 九十五、但又不能什么都标

这是另一个极端。

有人会说：

> 那我们一次性让专家填 80 个字段。

结果专家标一条：

> 15 分钟。

10 万条数据：

> 项目直接破产。

---

# 九十六、所以 Schema 必须遵循

\[
\boxed{
Value
>
AnnotationCost
}
\]

也就是：

> 每一个字段都要证明它值得专家花时间。

---

# 九十七、第一版 AnnotationSchema 最好：

> 小而强。

核心字段控制在真正重要的部分。

---

# 九十八、一个很实用的分层方式

# Tier 1：所有样本必标

例如：

```text
risk_present
primary_risk_type
needs_review
```

---

# 九十九、Tier 2：风险样本必标

例如：

```text
risk_subtype
risk_level
rationale
```

---

# 一百、Tier 3：Gold / 高价值样本必标

例如：

```text
verified evidence
citation
detailed suggested action
```

---

# 一百零一、这样：

大规模 Train：

> 成本可控。

高质量 Gold：

> 信息丰富。

---

# 一百零二、这叫：

# Tiered Annotation

分层标注。

它比：

> 所有数据统一最高标准

更现实。

---

# 一百零三、现在谈 `needs_review`

这是整个 ProcurementAI 中非常重要的一个 Label。

为什么？

因为现实专家系统最危险的不是：

> 偶尔说“不知道”。

而是：

> 明明不知道，却非常自信。

---

# 一百零四、因此我们的系统应该学会：

# Abstention

也就是：

> 在适当的时候不强答。

---

# 一百零五、可以设计：

```text
needs_review = true
```

作为明确 Target。

---

# 一百零六、例如以下情况都可能触发：

```text
上下文缺失
法规依据不确定
项目特殊性明显
条款存在多义性
OCR有关键字段不确定
无法判断履约必要性
```

---

# 一百零七、这样模型不是只能：

```text
Risk
No Risk
```

而可以：

```text
Need Human Review
```

---

# 一百零八、这对高风险专业系统非常重要。

---

# 一百零九、如果不标 `needs_review`

模型会被训练成：

> 每个问题都必须给确定答案。

---

# 一百一十、这就是 Forced Certainty

强迫确定性。

最终很容易造成：

# Overconfidence

---

# 一百一十一、以后第 8 课我们还会评：

```text
Calibration
Abstention
OOD
```

而这些能力的种子：

> 就埋在今天的 Label Schema 里。

---

# 一百一十二、现在看一个完整案例

条款：

> “投标人须在项目所在地设有不少于20人的固定技术服务团队。”

先不要直接下最终法律结论。

Annotation 可以先分解。

---

# 一百一十三、事实层

```text
主体：
投标人

要求：
在项目所在地设固定技术服务团队

人数：
不少于20人
```

---

# 一百一十四、判断层

可能：

```text
risk_present = uncertain
needs_review = true
```

为什么不是直接 `true`？

因为还需要：

```text
项目规模
服务内容
现场响应要求
合同履约特点
市场供给情况
```

---

# 一百一十五、风险候选类别

可能：

```text
primary_risk_type = A
```

或者根据 Schema：

> 也可能更接近商务/履约要求。

这正说明：

> 需要明确的 Label Guide。

---

# 一百一十六、Rationale

可以表达：

> 条款同时限定服务地点与最低团队人数，需要进一步审查这些条件与项目履约需求、采购规模之间是否具有充分关联和必要性。

---

# 一百一十七、Evidence

如果目前没有核实外部依据：

```text
citation_status = missing
```

不要编。

---

# 一百一十八、Suggested Action

```text
human_review
```

或者：

```text
clarify_business_necessity
```

---

# 一百一十九、看出区别了吗？

这比：

```text
风险 = 是
```

专业得多。

---

# 一百二十、现在看另一个例子

条款：

> “本项目不接受联合体投标。”

是不是直接标 Risk？

不能。

---

# 一百二十一、为什么？

因为是否合理：

> 需要结合具体采购项目、适用规范和场景分析。

如果我们的 Dataset 只学关键词：

```text
不接受联合体
→ 风险
```

模型以后会大量误报。

---

# 一百二十二、所以这个样本可能是：

```text
risk_present = uncertain
needs_review = true
```

或者在具体、充分上下文和专家判断下：

> 得到其他 Label。

关键不是这里给出一个固定法律结论。

关键是：

> **Schema 必须允许专家表达上下文依赖。**

---

# 一百二十三、这就是：

# Context-dependent Label

很多政府采购判断不是：

\[
Label=f(ClauseText)
\]

而更接近：

\[
Label
=
f(
Clause,
ProjectContext,
SectionContext,
ApplicableRules,
Time
)
\]

---

# 一百二十四、这条公式很重要

它说明为什么：

> Clause Text alone

往往不足以形成 Gold。

---

# 一百二十五、所以 Annotation Tool 在专家标注时

最好可以展示：

```text
Target Clause
Parent Section
必要前后文
项目基本信息
允许使用的法规依据
```

这部分会在下一阶段进一步讲。

---

# 一百二十六、现在讨论 Label Granularity

是不是越细越好？

不是。

过粗：

```text
Risk / No Risk
```

学不到专业结构。

---

# 一百二十七、过细：

```text
327个Subtype
```

专家记不住，

样本不够，

一致性极差。

---

# 一百二十八、理想状态：

# Decision-useful Granularity

也就是：

> 粒度细到足以支持业务决策和误差分析，但又粗到专家能够稳定区分、样本数量能够支撑训练。

---

# 一百二十九、可以把它想成地图。

全国地图只有：

```text
中国
```

太粗。

---

# 一百三十、每一栋楼都是一个类别：

> 太细。

---

# 一百三十一、我们需要：

> 省 / 市 / 区这种实用层级。

Label Taxonomy：

> 也是一样。

---

# 一百三十二、所以第一版五大类：

```text
A～E
```

就是我们的一级地图。

---

# 一百三十三、后面根据真实错误再生长：

# Subtype

这比一开始设计一个“大而全分类法”：

> 更可靠。

---

# 一百三十四、现在谈 Unknown Label 的训练处理

有人可能担心：

> “模型怎么训练 uncertain？”

这是后面训练阶段的事。

Master Dataset 首先应该：

> 保存真实专家判断状态。

---

# 一百三十五、之后可以派生不同 View

Classifier V1：

> 暂时排除 uncertain。

---

# 一百三十六、Classifier V2：

> 把 uncertain 作为第三类。

---

# 一百三十七、SFT：

> 训练模型输出 needs_review。

---

# 一百三十八、Benchmark：

> 单独评估 uncertain / abstention。

---

# 一百三十九、所以不能为了：

> 第一个模型方便训练，

把所有 uncertain：

> 强行改成 true 或 false。

---

# 一百四十、这是：

\[
\boxed{
PreserveTruthFirst
>
TrainingConvenience
}
\]

---

# 一百四十一、现在谈标签来源

一个 Label 可能来自：

```text
单专家判断
双专家一致
专家裁决
监管结果辅助
规则自动生成
模型预标注
```

这些质量：

> 完全不同。

---

# 一百四十二、所以我们需要：

```text
label_source
```

例如：

```text
expert_manual
expert_adjudicated
rule_generated
model_assisted
```

---

# 一百四十三、为什么这很重要？

假设以后发现：

```text
rule_generated
```

的一批 Label 有 Bug。

如果没有 `label_source`：

> 你不知道哪些受影响。

---

# 一百四十四、如果有：

> 可以直接重新处理。

---

# 一百四十五、所以 Annotation 同样需要 Provenance

可以写成：

\[
\boxed{
Label
+
LabelProvenance
}
\]

---

# 一百四十六、专家身份要不要存？

需要一定的审核追踪信息，

但 Master Dataset 中应该按项目的数据治理要求处理：

```text
annotator_id
reviewer_id
```

可以使用内部匿名标识。

不一定需要：

> 暴露个人姓名。

---

# 一百四十七、还要保存：

```text
annotation_time
```

为什么？

第 7 阶段已经知道：

> 时间可能影响规范环境和知识可用性。

---

# 一百四十八、例如某条数据：

2025 年第一次标。

2026 年法规变化以后：

> 可能需要重新审查。

---

# 一百四十九、如果没有 Annotation Time：

你不知道：

> 这条 Gold 是在哪个知识环境下产生的。

---

# 一百五十、所以第一版 Quality Metadata 可以包含

```json
{
  "annotator_id": "EXP-017",
  "annotation_time": "2026-09-15",
  "annotation_status": "draft",
  "label_source": "expert_manual",
  "schema_version": "annotation_schema_v0.1"
}
```

---

# 一百五十一、现在谈 `schema_version`

为什么 Annotation Schema 也必须版本化？

因为今天：

```text
Risk Type = A/B/C/D/E
```

未来可能：

> 增加 Subtype。

---

# 一百五十二、或者今天：

```text
risk_present = true/false/uncertain
```

未来改：

```text
confirmed
potential
unlikely
unknown
```

语义变化了。

---

# 一百五十三、如果不记录：

```text
schema_version
```

数据库里旧新 Label 混在一起，

你甚至不知道：

> `high` 到底是哪一版定义。

---

# 一百五十四、所以：

# Label Meaning is Versioned

不是只有数据值需要版本。

> 标签定义本身也需要版本。

---

# 一百五十五、这就是：

# Ontology Versioning

---

# 一百五十六、不要被 Ontology 这个词吓到。

这里简单理解：

> “我们是怎么定义这个世界里的类别和关系的。”

---

# 一百五十七、例如：

```text
供应商资格风险
```

到底包括什么？

不包括什么？

边界案例是什么？

这些：

> 都属于 Ontology。

---

# 一百五十八、下一阶段的 Annotation Guideline

就会把这些定义真正写给专家。

---

# 一百五十九、现在讲一个特别危险的问题

# Label by Outcome

假设某项目：

> 最后没人投诉。

于是自动标：

```text
No Risk
```

这合理吗？

不合理。

---

# 一百六十、为什么？

没有投诉：

> 不等于条款一定没有潜在风险。

可能只是：

```text
没人提出
供应商没参与
没有形成争议
```

---

# 一百六十一、反过来：

有人投诉：

> 也不自动等于投诉成立。

---

# 一百六十二、所以：

\[
\boxed{
ObservedOutcome
\neq
GoldLabel
}
\]

后续结果：

> 可以作为专家证据之一。

但不能机械映射成 Gold。

---

# 一百六十三、这是 Stage 7 时间泄漏思想在标注上的延续。

---

# 一百六十四、同样不要用“是否被更正”直接当 Label

被更正：

> 可能只是日期错误。

没被更正：

> 也不证明所有条件都没有风险。

---

# 一百六十五、所以 Gold Label 最终需要：

# Expert Judgment under a defined guideline

而不是：

> Outcome shortcut。

---

# 一百六十六、现在讨论模型预标注

以后为了节约专家时间，可以让模型先输出：

```text
risk_present
risk_type
reason
```

专家：

> 修改确认。

这种方法很常见。

---

# 一百六十七、但它有一个风险：

# Automation Bias

专家容易受到模型答案影响。

---

# 一百六十八、如果模型一开始错误地认为：

```text
本地服务 = 一律高风险
```

专家看大量预标注以后：

> 可能无意识地接受这种框架。

---

# 一百六十九、最终 Gold Dataset：

> 被原模型偏见污染。

---

# 一百七十、所以模型辅助标注可以用，

但应该记录：

```text
model_suggestion
expert_final_label
```

并且不要把模型 Suggestion：

> 当作专家答案本身。

---

# 一百七十一、这也允许以后研究：

> 专家改了模型多少次？

---

# 一百七十二、例如：

```text
model_agreement_rate
```

可以成为：

> 标注系统质量指标之一。

---

# 一百七十三、但下一阶段才会详细讨论专家流程。

今天只建立字段边界。

---

# 一百七十四、现在第一次整理出 `AnnotationSchema_V0.1`

它可以概念分成七块：

```text
Identity
Source Context
Judgment
Taxonomy
Reasoning
Evidence / Action
Quality Metadata
```

---

# 一百七十五、把它写成一个较完整的示例

```json
{
  "sample_id": "SAMPLE-00178",

  "source": {
    "project_id": "PROJECT-00152",
    "document_id": "DOC-00152-01",
    "clause_id": "CLAUSE-00178",
    "section_path": [
      "第三章 采购需求",
      "3.1 供应商资格条件"
    ]
  },

  "judgment": {
    "risk_present": "uncertain",
    "needs_review": true,
    "primary_risk_type": "A",
    "secondary_risk_types": [],
    "risk_subtype": "geographic_requirement",
    "risk_level": "needs_review"
  },

  "rationale": {
    "observed_fact": "条款对供应商所在地提出要求。",
    "risk_concern": "需要审查该要求是否形成不必要的地域限制。",
    "context_needed": "项目履约地点、响应要求及该条件的客观必要性。",
    "conclusion_scope": "当前证据不足，不作确定结论，进入人工复核。"
  },

  "evidence": {
    "source_spans": [
      {
        "page": 27,
        "text": "供应商须在本市……"
      }
    ],
    "external_basis": [],
    "citation_status": "missing"
  },

  "suggested_action": "human_review",

  "quality": {
    "label_source": "expert_manual",
    "annotator_id": "EXP-017",
    "annotation_status": "draft",
    "annotation_time": "2026-09-15",
    "schema_version": "annotation_schema_v0.1"
  }
}
```

---

# 一百七十六、这里最重要的不是 JSON 长什么样

而是：

> **我们终于把专家判断拆成可以独立学习、独立核验、独立评测的不同组件。**

---

# 一百七十七、现在看它怎样派生 Classification Dataset

可以只取：

```json
{
  "input": "供应商须在本市……",
  "risk_present": "uncertain",
  "risk_type": "A"
}
```

---

# 一百七十八、怎样派生 SFT Dataset

可能变成：

```text
User:
请审查以下采购条款……

Assistant:
风险状态：需要复核
风险类型：供应商资格
理由：……
依据状态：待核实
建议：人工复核
```

---

# 一百七十九、怎样派生 Evaluation Dataset

Gold 可以保留：

```text
risk_present
risk_type
risk_subtype
rationale
evidence
needs_review
```

分别评分。

---

# 一百八十、怎样派生 Product UI

UI 可以展示：

```text
风险类别
复核等级
理由
原文证据
法规依据
建议动作
```

---

# 一百八十一、看到没有？

一个好的 Annotation Schema：

> 同时服务训练、评测和产品。

这就是 Master Data 的真正价值。

---

# 一百八十二、现在谈 Classification Loss

如果将来 `risk_present` 是：

```text
Risk
No Risk
Needs Review
```

就可以作为三分类。

模型最终输出：

\[
P(y=\text{risk}),
P(y=\text{no-risk}),
P(y=\text{review})
\]

---

# 一百八十三、例如：

```text
Risk        0.41
No Risk     0.14
Review      0.45
```

最大概率：

> Review。

这与我们的业务现实很吻合。

---

# 一百八十四、而不是强迫：

```text
Risk = 0.74
```

然后硬判风险。

---

# 一百八十五、当然真正系统以后还可以设计：

```text
risk probability
+
uncertainty
+
abstention threshold
```

这属于后面评测和部署课程。

今天只需要认识：

> Label Schema 决定模型未来有没有机会学习“不确定性”。

---

# 一百八十六、Multi-label Risk Type 以后也可以使用

每个类别一个概率：

\[
P(A),P(B),P(C),P(D),P(E)
\]

例如：

```text
A 0.91
B 0.18
C 0.62
D 0.05
E 0.11
```

说明：

> 可能同时涉及 A 和 C。

---

# 一百八十七、这比 Softmax 五选一：

> 更有表达能力。

但是否真的采用 Multi-label Training：

> 要由数据和任务验证决定。

Schema 只需要：

> 不把这条路堵死。

---

# 一百八十八、现在谈 Label Leakage 再检查一次

如果我们的 Annotation 中有：

```text
expert_rationale
gold_evidence
```

未来构造模型 Input 时：

> 这些通常不能偷偷出现。

---

# 一百八十九、因此可以明确：

```text
Gold-only Fields
```

例如：

```text
gold_rationale
gold_label
gold_evidence
adjudication_comment
```

---

# 一百九十、这些字段：

> 默认禁止进入普通模型 Input。

---

# 一百九十一、这就是 Stage 7 的

# Benchmark Firewall

进入 Stage 8 Schema。

---

# 一百九十二、好架构的特点就是这样：

每一阶段：

> 不是孤立知识。

前面的约束：

> 会进入后面的数据模型。

---

# 一百九十三、现在讨论“专家自由文本”

是不是应该完全禁止？

不是。

结构化字段适合：

```text
统计
训练
评测
```

自由文本适合：

> 保存专家没法提前编码的新洞察。

---

# 一百九十四、所以可以同时存在：

```text
structured rationale
```

和：

```text
expert_note
```

---

# 一百九十五、但 `expert_note`

更多应该视为：

# Audit / Research Field

而不是直接默认：

> 喂给模型。

---

# 一百九十六、以后如果发现专家反复在 Note 写：

> “这类情况与合同履约阶段相关。”

可能说明：

> Taxonomy 缺了一个字段。

---

# 一百九十七、所以自由文本还有一个作用：

# Discover new schema needs

Schema 不应该一成不变。

它应该根据真实标注：

> 逐步演化。

---

# 一百九十八、现在谈“Other”

分类体系永远会出现：

```text
other
```

这个 Label 可以有。

但一定要警惕。

---

# 一百九十九、如果：

```text
Other = 2%
```

可能没问题。

---

# 二百、如果：

```text
Other = 38%
```

这通常说明：

> Taxonomy 不够好。

---

# 二百零一、所以应监控：

# Other Rate

---

# 二百零二、同时：

```text
unknown
```

比例也值得监控。

---

# 二百零三、如果 `unknown` 极高

可能说明：

```text
Context提供不足
Label Guide太模糊
专家没有足够依据
任务本身定义错误
```

---

# 二百零四、因此 Label Distribution：

> 不只是训练统计。

它还帮助诊断：

# Schema Quality

---

# 二百零五、一个好的 Schema 应该让大部分真实样本：

> 能够自然表达。

而不是逼专家：

> 经常选 Other。

---

# 二百零六、现在谈“Label Balance”

是不是五大类：

> 每类一定要一样多？

不需要。

真实世界本来：

> 分布可能不一样。

---

# 二百零七、但如果某类只有：

```text
12条
```

你就不能期待模型：

> 学得很好。

---

# 二百零八、所以 Schema 定义出来以后，

我们要统计：

```text
count by risk_type
count by subtype
count by level
count by needs_review
```

---

# 二百零九、然后决定：

> 哪些类别需要继续收集数据。

---

# 二百一十、这就是：

# Annotation Schema → Data Acquisition Strategy

如果发现技术参数风险只有：

> 300 条，

而资格类有：

> 30,000 条，

下一轮数据建设：

> 就不应该继续只收资格案例。

---

# 二百一十一、所以 Label Schema 还会指导：

# Active Data Collection

---

# 二百一十二、现在讲一个典型反例

某团队设计：

```text
label:
0 = normal
1 = illegal
```

问题非常大。

---

# 二百一十三、第一：

> “illegal”是非常强的法律结论。

AI 数据中不应该随便把复杂情形都压成：

> 违法 / 不违法。

---

# 二百一十四、第二：

很多条款是：

> 需要结合上下文复核。

二分类没有位置。

---

# 二百一十五、第三：

无法区分：

```text
资格
技术
商务
评分
采购需求
```

---

# 二百一十六、第四：

无法训练：

> 原因解释。

---

# 二百一十七、第五：

无法验证：

> 证据。

---

# 二百一十八、所以更合理的第一层词汇通常是：

# Potential Risk

潜在风险。

而不是：

# Final Legal Verdict

---

# 二百一十九、这符合我们的系统定位：

> 风险筛查 + 专家辅助。

---

# 二百二十、再看另一个失败 Schema

```json
{
  "label": "供应商资格存在明显不合理限制，建议删除并按照政府采购法相关规定重新设计资格条件。"
}
```

---

# 二百二十一、看起来很专业。

但实际上：

```text
风险存在
风险类型
程度
原因
建议
依据
```

全部塞在：

> 一个字符串。

---

# 二百二十二、后果是：

想统计：

> 风险类型。

难。

想计算 Classification Recall：

> 难。

想验证法规引用：

> 难。

想把建议单独用于产品：

> 难。

---

# 二百二十三、所以：

\[
\boxed{
FreeTextOnly
\neq
ProfessionalAnnotationSchema
}
\]

---

# 二百二十四、自由文本应该：

> 建立在结构化骨架上。

不是：

> 替代结构。

---

# 二百二十五、现在讨论 Label Hierarchy

一级：

```text
Risk Present
```

二级：

```text
Risk Type
```

三级：

```text
Risk Subtype
```

四级：

```text
Specific Pattern
```

---

# 二百二十六、例如：

```text
Risk
└── Supplier Qualification
    └── Geographic Requirement
        └── Pre-existing local registration
```

---

# 二百二十七、这是不是意味着：

> 每条都必须标到最底层？

不一定。

---

# 二百二十八、专家可能只能确定：

```text
Supplier Qualification
```

但不知道：

> Subtype。

可以允许：

```text
risk_type = A
risk_subtype = unknown
```

---

# 二百二十九、这比强迫猜一个 Subtype：

> 更好。

---

# 二百三十、这叫：

# Partial Label

部分标签。

---

# 二百三十一、以后训练时可以：

> 使用能够确定的上位标签。

而不是：

> 丢弃整条数据。

---

# 二百三十二、这是很实用的思想。

现实专业标注：

> 不一定每个维度都有同样置信度。

---

# 二百三十三、因此未来甚至可以有：

```text
label_confidence
```

但这里要谨慎。

专家随手填：

```text
0.83
```

没有意义。

---

# 二百三十四、相比连续数字，

更容易标准化的是：

```text
high
medium
low
```

或者：

```text
direct
inferred
insufficient_evidence
```

---

# 二百三十五、不过第一版我们不急着加太多字段。

仍然遵循：

# Minimal but Sufficient

---

# 二百三十六、现在确定 `AnnotationSchema_V0.1` 的核心字段

第一版可以把强制核心压缩成：

```text
risk_present
primary_risk_type
needs_review
rationale
annotation_status
schema_version
```

---

# 二百三十七、条件字段：

```text
risk_subtype
risk_level
secondary_risk_types
evidence_refs
suggested_action
```

---

# 二百三十八、Metadata：

```text
sample_id
project_id
document_id
clause_id
annotator_id
annotation_time
label_source
```

---

# 二百三十九、这样第一版已经足够强，

但仍然：

> 可以实际执行。

---

# 二百四十、现在建立第一版 Schema Validation

概念规则：

```text
sample_id required
clause_id required
risk_present required

if risk_present == true:
    primary_risk_type required
    rationale required

if risk_present == uncertain:
    needs_review must be true

if citation_status == verified:
    evidence_refs required

if annotation_status == gold:
    reviewer/adjudication requirements must pass
```

---

# 二百四十一、真正工程里：

> 可以用 JSON Schema、Pydantic 或其它验证工具实现。

现在不需要记工具。

只需要理解：

> Label Schema 不应该只是 Word 文档里的说明。

它最好能够：

# Machine Validate

---

# 二百四十二、这就是：

\[
\boxed{
HumanGuideline
+
MachineContract
}
\]

专家看：

> 标注手册。

程序看：

> Schema Validation。

两者使用：

> 同一套定义。

---

# 二百四十三、如果只写人工说明

专家可以填：

> 不合法组合。

---

# 二百四十四、如果只有机器 Schema

程序知道：

```text
string
enum
boolean
```

但不知道：

> 专业边界。

---

# 二百四十五、所以必须两者都有。

---

# 二百四十六、这一阶段之后

我们已经回答了：

> 专家要标哪些字段。

但还没有回答：

> **专家 A 和专家 B 怎么保证理解“High Risk”是同一回事？**

---

# 二百四十七、比如同一条：

> “供应商须具有5个同类项目业绩。”

专家 A：

```text
risk_present = true
```

专家 B：

```text
risk_present = false
```

专家 C：

```text
risk_present = uncertain
```

---

# 二百四十八、谁错了？

也可能：

> 谁都不是随便乱标。

而是三个人使用：

> 不同的隐含判断标准。

---

# 二百四十九、所以只有 Schema：

> 还不够。

下一阶段必须建立：

# Annotation Guideline

告诉专家：

```text
什么叫Risk？
什么叫No Risk？
什么叫Uncertain？
每个Risk Type边界在哪里？
什么上下文必须看？
什么证据算够？
什么时候必须needs_review？
```

---

# 二百五十、同时还要测：

# Inter-Annotator Agreement

不同专家：

> 到底有多一致？

---

# 二百五十一、如果一个 Label：

专家之间只有：

```text
55%
```

一致，

那模型就算达到：

```text
90%
```

Accuracy，

你都应该怀疑：

> 到底在学什么？

---

# 二百五十二、因为 Gold 本身：

> 可能没有稳定定义。

---

# 二百五十三、这就是第 9 阶段要处理的核心。

---

# 二百五十四、本阶段最容易犯的 12 个错误

唯一这组集中记一下：

1. 只设计 `Risk / No Risk` 两个 Label，丢掉风险类型、上下文和不确定性。
2. 把 `unknown` 当 `false`，把“看不出来”错误标成“没有风险”。
3. 把 Section Type 直接当成 Risk Type。
4. 强迫所有样本五选一，不允许 Multi-label 或 Secondary Type。
5. 一开始就设计几百个 Subtype，导致数据极度稀疏。
6. 把 Risk Level 写成模糊的 High / Medium / Low，却不给工作定义。
7. 把 Rationale 和 Evidence 混成一个自由文本字段。
8. 没找到依据时为了填满字段而编造 Citation。
9. 把“检测到潜在风险”自动等价为“删除条款”。
10. 只要求正样本写理由，负样本没有任何边界解释。
11. 让 Gold、专家备注、后续结果等字段默认全部进入模型 Input。
12. 没有 `schema_version` 和 `annotation_status`，旧新标签长期混在一起。

---

# 二百五十五、本阶段最重要的 7 个“≠”

```text
Risk Detection
≠
Final Legal Verdict
```

```text
Unknown
≠
No Risk
```

```text
Section Type
≠
Risk Type
```

```text
Reasoning
≠
Evidence
```

```text
Risk Detection
≠
Remediation Decision
```

```text
Label Value
≠
Label Quality Status
```

```text
Observed Outcome
≠
Gold Label
```

把这七组关系分清以后，整个政府采购 Annotation Schema 的骨架基本就稳了。

---

# 二百五十六、再记住本阶段最重要的“=”

\[
\boxed{
ProfessionalAnnotation
=
Judgment
+
Taxonomy
+
Uncertainty
+
Rationale
+
Evidence
+
Action
+
Provenance
}
\]

翻译成人话：

> **专业标注不是给一条采购 Clause 贴一个“有风险”的贴纸，而是记录专家判断是什么、属于什么风险、哪里还不确定、为什么这么判断、依据在哪里、下一步应该怎么处理，以及这个判断由谁在什么规则版本下产生。**

---

# 二百五十七、现在把第四课前 8 个阶段串起来

```text
Stage 1
Task Schema
“什么是一条样本？”
       │
       ▼
Stage 2
ParsedDocument
“原文件里有什么？”
       │
       ▼
Stage 3
ClauseUnit
“文字属于哪条业务要求？”
       │
       ▼
Stage 4
CleanClause
“怎样安全规范文本？”
       │
       ▼
Stage 5
DedupedClauseSet
“到底有多少独立信息？”
       │
       ▼
Stage 6
DatasetSplit
“哪些用来学习，哪些留着考试？”
       │
       ▼
Stage 7
LeakageAudit
“考试答案有没有提前泄露？”
       │
       ▼
Stage 8
AnnotationSchema
“专家到底应该标什么？”
```

到这里，数据终于第一次具备：

# 可以进入正式专家标注流程的结构基础。

---

# 二百五十八、本阶段掌握测试

如果现在不回看正文，你应该能够解释这些问题：为什么二分类不足以支撑政府采购专业模型；为什么 `unknown` 不能当成 `false`；`risk_present` 和 `needs_review` 为什么不是重复字段；五大 Risk Type 与 Section Type 有什么区别；为什么 Master Schema 最好支持 Primary + Secondary Risk Type；为什么 Subtype 不应该一开始设计几百个；`risk_level` 为什么应该被定义为工作上的审查优先级，而不是 AI 的最终法律责任裁决；Rationale 和 Evidence 有什么区别；为什么 Citation 找不到时应该标 Missing 而不是补一个看起来合理的法规；为什么 Risk Detection 不等于立即删除条款；为什么负样本也需要理由；`false`、`unknown`、`missing` 和 `not_applicable` 有什么区别；什么是 Cross-field Validation；为什么 Master Annotation 不应该直接等于 SFT 的 Question/Answer 格式；为什么一套 Master Annotation 可以派生 Classification、SFT、RAG、Evaluation 和 Product View；为什么 `annotation_status` 与 Label 本身必须分开；为什么 Outcome 不能机械转换成 Gold Label；为什么模型辅助标注可能产生 Automation Bias；为什么 Annotation Schema 必须版本化；为什么 Schema 设计会直接决定未来 Benchmark 能评什么；为什么 Gold Benchmark 应该拥有比大规模训练数据更丰富的标注；以及为什么“我不知道，需要人工复核”本身就是一个非常重要的专业模型能力。

如果这些问题都能讲清楚：

\[
\boxed{
第四课第8阶段真正掌握
}
\]

---

# 二百五十九、本阶段最终只记一句话

> **政府采购专业 Label Schema 的目标，不是把所有 Clause 压缩成“有风险 / 没风险”，而是把专家的判断拆成风险状态、风险类型、不确定性、理由、证据、行动建议和标注来源，让“专家脑子里的专业判断”第一次变成可以训练、可以评测、可以审计的数据结构。**

最后压成一张图：

```text
                    Clean Clause
                         │
                         ▼
                  Expert Annotation
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
      Judgment        Taxonomy      Uncertainty
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                      Rationale
                         │
                         ▼
                       Evidence
                         │
                         ▼
                  Suggested Action
                         │
                         ▼
                   Quality Metadata
                         │
                         ▼
               AnnotationSchema_V0.1
            ┌────────────┼────────────┐
            ▼            ▼            ▼
      Classification    SFT       Evaluation
            │            │            │
            └────────────┼────────────┘
                         ▼
                 ProcurementAI
```

---

# 下一阶段：第四课 · 第 9 阶段
## 专家标注、双人复核与一致性——为什么两位真正的采购专家都很专业，却仍然可能给同一个 Clause 完全不同的 Label？

第 8 阶段解决的是：

> **标什么。**

第 9 阶段要解决的是：

> **怎么让不同的人按照同一套标准去标。**

我们会第一次正式进入：

```text
Annotation Guideline
Blind Annotation
Double Annotation
Inter-Annotator Agreement
Disagreement
Adjudication
Gold Label
```

并回答一个很关键的问题：

> 如果两个专家对同一批数据只有 60% 一致率，应该继续训练模型，还是先修 Label Schema 和标注指南？

第 9 阶段还会解释为什么：

> **专家分歧本身不是垃圾数据。**

有些分歧恰恰是在告诉我们：

```text
规则边界不清
上下文不足
Schema设计不够好
案例本身就是Hard Case
```

最终我们会产出：

# `AnnotationGuideline_V0.1`
# `AdjudicatedGoldSet_V0.1`

也就是第一次真正从“有一套标签结构”，推进到：

> **有一批可以称为 Gold 的专家标注数据。**

---
