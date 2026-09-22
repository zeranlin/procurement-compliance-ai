# 第十一课 · 第 3 阶段
# 采购文件业务解剖：Qualification、Technical、Commercial、Scoring、Contract
## 为什么 RAG 切出来的 Text Chunk 还不是“业务条款”？怎样把一整份真实采购文件恢复成 AI 真正能理解、能检查、能追溯的业务结构？

> **中文阅读增强说明（本次修订新增）**：为方便中国政府采购业务人员、合规人员和工程人员共同阅读，本阶段所有关键英文工程字段、状态值、流程节点和 Schema 标识均保留原英文名称，并在同一代码块中增加 `# 中文：...` 的业务释义。英文名称用于后续数据库、JSON/YAML、API 和程序实现保持稳定；中文释义用于说明它在政府采购合规审查中的实际含义。


第 2 阶段我们已经建立：

\[
\boxed{
PolicyRegistry
\neq
VectorDatabase
}
\]

**中文业务释义：** 政策法规注册表 ≠ 向量数据库。

并且把法规侧正式拆成：

```text
Source Document    # 中文：来源文件
来源文件
↓
Provision    # 中文：具体条文 / 规定
具体条文 / 规定
↓
Executable Rule    # 中文：可执行规则
可执行规则
```

现在进入采购文件这一侧。

政府采购合规 AI 的另一半问题是：

> **系统到底怎样理解一份采购文件？**

如果只是把 PDF / Word 按：

```text
500 tokens    # 中文：500 个 Token（机械文本块长度示例）
1000 tokens    # 中文：1000 个 Token（机械文本块长度示例）
1500 tokens    # 中文：1500 个 Token（机械文本块长度示例）
```

机械切块，

然后丢给 Embedding 和 RAG，

系统得到的是：

# Text Chunk
## 文本块

但政府采购业务真正需要的是：

# Business Clause
## 业务条款

两者完全不是一回事。

所以本阶段第一条边界必须先锁死：

\[
\boxed{
TextChunk
\neq
BusinessClause
}
\]

**中文业务释义：** 检索文本块 ≠ 政府采购业务条款。

本阶段最终形成：

# `ProcurementDocumentSchema_V1`

它会成为后续：

```text
D01-D22 Rule Engine    # 中文：D01-D22 差别歧视规则引擎
Qualification Review    # 中文：资格条件审查
Technical Review    # 中文：技术要求审查
Scoring Review    # 中文：评分标准审查
Legal RAG    # 中文：法规检索增强生成
SFT    # 中文：监督微调
Compliance Agent    # 中文：合规智能体
Gold Benchmark    # 中文：金标准评测基准
```

共同依赖的：

# Business Document Contract
## 采购文件业务结构契约

---

# 一、为什么采购文件不能只当“长文本”？

一份真实采购文件通常同时包含：

```text
采购公告
投标人须知
供应商资格条件
采购需求
技术要求
服务要求
商务要求
实质性条款
评分办法
评分细则
合同草案
履约要求
附件
表格
声明函
报价表
技术响应表
```

这些内容在自然语言上可能很像，

但在合规意义上：

> 角色完全不同。

例如：

```text
“供应商应具有某项证书”
```

如果出现在：

```text
资格条件
```

它可能决定：

> 能不能参加。

如果出现在：

```text
评分标准
```

它可能决定：

> 能不能加分。

如果出现在：

```text
合同履约要求
```

它可能只是：

> 中标以后必须满足。

同一句话，

业务位置不同，

法律与合规含义可能完全不同。

所以：

\[
\boxed{
SameText
+
DifferentDocumentRole
=
DifferentComplianceMeaning
}
\]

**中文业务释义：** 相同文本 + 不同文档业务角色 = 不同合规含义。

---

# 二、核心心智模型 ①
# `Meaning = Text + BusinessPosition`

LLM 不能只看：

> 句子本身是什么意思。

还要看：

> **这句话在采购文件哪个业务位置上出现。**

因此：

\[
\boxed{
ClauseMeaning
=
ClauseText
+
SectionRole
+
ProjectContext
}
\]

**中文业务释义：** 条款含义 = 条款原文 + 章节业务角色 + 项目上下文。

这也是为什么：

> 文档解析不是简单 OCR。

---

# 三、Stage 1 的 Product Scope 在这里开始落地

第 1 阶段已经定义了审查范围：

```text
Procurement Requirement    # 中文：采购需求
采购需求

Qualification    # 中文：资格条件
资格条件

Substantive Requirement    # 中文：实质性要求
实质性条款

Technical Requirement    # 中文：技术要求
技术要求

Commercial Requirement    # 中文：商务要求
商务要求

Scoring Criteria    # 中文：评分标准
评分标准

Procurement Policy    # 中文：政府采购政策
政府采购政策

Competition / Procurement Method    # 中文：竞争性 / 采购方式
竞争性与采购方式

Contract / Performance    # 中文：合同 / 履约
合同与履约
```

你上传的《2025 年政府采购领域“四类”违法违规行为专项整治工作指引》对“采购人设置差别歧视条款”也明确要求：

> 全面检查采购文件、采购公告，重点包括采购需求、资格要求、实质性条款以及评分标准等。

因此这些业务域不是：

> 课程为了方便随便分的。

它们本身就是实际政府采购检查中的重要审查位置。

---

# 四、第一层 Schema：Project

所有 Document 都必须属于：

# Project
## 采购项目

最少字段：

```text
project_id    # 中文：项目标识

project_name    # 中文：项目名称

procurement_entity    # 中文：采购实体 / 主体
采购人

procurement_agency    # 中文：采购代理机构
采购代理机构

procurement_category    # 中文：采购类别
货物 / 服务 / 工程等

procurement_method    # 中文：采购方法
采购方式

budget_amount    # 中文：预算金额

maximum_price    # 中文：最高价格
最高限价

jurisdiction    # 中文：辖区

announcement_date    # 中文：公告日期

bid_deadline    # 中文：投标截止时间

evaluation_date    # 中文：评审日期

contract_stage    # 中文：合同阶段

policy_snapshot_id    # 中文：政策法规快照标识
```

为什么要有 Project？

因为很多条款是否合理，

无法只从条款本身判断。

例如：

```text
要求 7×24 小时现场服务
```

是否合理，

要看：

```text
项目类型
服务对象
履约地点
时效要求
实际业务必要性
```

所以：

\[
\boxed{
ClauseJudgment
需要
ProjectContext
}
\]

---

# 五、第二层 Schema：Document

一个项目可能有多个 Document：

```text
采购公告
招标文件
磋商文件
谈判文件
询价通知书
采购需求附件
更正公告
澄清文件
合同草案
```

所以：

\[
\boxed{
Project
\neq
SingleDocument
}
\]

**中文业务释义：** 采购项目 ≠ 单一文件。

Document 至少记录：

```text
document_id    # 中文：文档标识

project_id    # 中文：项目标识

document_type    # 中文：文档类型

document_title    # 中文：文档标题

document_version    # 中文：文档版本

source_file    # 中文：来源文件

source_hash    # 中文：来源哈希

publication_time    # 中文：发布时间

effective_for_project    # 中文：生效用于项目

supersedes_document_id    # 中文：替代文档标识

is_latest_for_project    # 中文：是否最新用于项目

parse_status    # 中文：解析状态

page_count    # 中文：页数量
```

特别要注意：

> 更正文件可能修改原采购文件。

所以：

\[
\boxed{
LatestProjectDocument
\neq
FirstUploadedDocument
}
\]

**中文业务释义：** 项目当前有效 / 最新文件 ≠ 首次上传文件。

---

# 六、核心心智模型 ②
# `DocumentVersion` 是采购合规判断的一部分

如果：

```text
V1采购文件
→ 有风险条款

V2更正文件
→ 已删除
```

系统不能继续基于 V1：

> 报告当前文件仍违规。

所以必须建立：

```text
document_version    # 中文：文档版本
supersedes    # 中文：替代
effective_from    # 中文：生效起始
current_for_review    # 中文：是否为当前审查使用版本
```

后面 Finding 必须绑定：

> **具体 Document Version。**

---

# 七、第三层 Schema：Section Tree

采购文件不是平铺文本。

它天然具有：

# Hierarchy
## 层级结构

例如：

```text
第一章 采购公告
第二章 投标人须知
  2.1 供应商资格
  2.2 投标文件要求
第三章 采购需求
  3.1 技术要求
  3.2 服务要求
  3.3 商务要求
第四章 评标办法
  4.1 资格审查
  4.2 符合性审查
  4.3 评分标准
第五章 合同条款
```

因此需要：

# Section Tree
## 章节树

最少：

```text
section_id    # 中文：章节标识

parent_section_id    # 中文：父级 / 上级章节标识

section_level    # 中文：章节层级

section_number    # 中文：章节编号

section_title    # 中文：章节标题

section_role    # 中文：章节业务角色

page_start    # 中文：页开始

page_end    # 中文：页结束

order_index    # 中文：顺序索引
```

所以：

\[
\boxed{
Document
\rightarrow
SectionTree
}
\]

**中文业务释义：** 采购文件 → 章节树。

而不是：

\[
\boxed{
Document
\rightarrow
FlatChunks
}
\]

**中文业务释义：** 采购文件 → 平铺文本块。

---

# 八、为什么 Section Role 比标题文本更重要？

真实文件标题不统一。

可能写：

```text
资格条件
供应商资格
申请人的资格要求
投标人资格要求
供应商条件
```

它们业务上可能都属于：

# Qualification
## 资格条件

所以我们需要：

# Section Role Classification
## 章节业务角色分类

标准化成：

```text
NOTICE    # 中文：公告 / 通知章节
INSTRUCTIONS    # 中文：供应商 / 投标人须知章节
QUALIFICATION    # 中文：资格条件章节
SUBSTANTIVE    # 中文：实质性要求章节
TECHNICAL    # 中文：技术要求章节
SERVICE    # 中文：服务要求章节
COMMERCIAL    # 中文：商务要求章节
SCORING    # 中文：评分标准章节
CONTRACT    # 中文：合同条款章节
POLICY    # 中文：政府采购政策章节
ATTACHMENT    # 中文：附件
FORM    # 中文：表单 / 格式文件
OTHER    # 中文：其他
```

因此：

\[
\boxed{
SectionTitle
\neq
SectionRole
}
\]

**中文业务释义：** 章节标题 ≠ 章节业务角色。

标题是原文。

Role 是：

> 标准化业务语义。

---

# 九、核心心智模型 ③
# `OriginalText` 和 `NormalizedBusinessRole` 必须同时保存

如果只保存标准化后的：

```text
QUALIFICATION    # 中文：资格条件章节
```

会丢掉原文件原貌。

如果只保存：

```text
“供应商应具备以下条件”
```

又不利于跨文件统一计算。

所以需要：

\[
\boxed{
Raw
+
Normalized
}
\]

**中文业务释义：** 原始值 + 标准化值。

这是整个政府采购数据工程里反复出现的原则。

---

# 十、第四层 Schema：Clause

# Clause
## 条款

它是合规审查最重要的基本单位之一。

一条 Clause 应该是：

> **在业务上能够形成一个相对独立要求、条件、规则或评价标准的最小可审查单元。**

例如：

```text
供应商须具有……
```

可能是一条 Clause。

但：

```text
评分项：
1. 类似业绩 5分
2. 人员证书 3分
3. 服务方案 10分
```

不能全部当成一个 Clause。

应该拆成：

```text
ScoringClause A    # 中文：评分条款 A
ScoringClause B    # 中文：评分条款 B
ScoringClause C    # 中文：评分条款 C
```

所以：

\[
\boxed{
ClauseBoundary
\neq
ParagraphBoundary
}
\]

**中文业务释义：** 条款边界 ≠ 段落边界。

---

# 十一、段落、句子、条款、要求为什么不能混？

一个 Paragraph：

> 可能包含多个 Requirement。

一个 Requirement：

> 可能跨多个 Sentence。

一个 Table Row：

> 可能就是一个完整评分条款。

所以：

\[
\boxed{
Sentence
\neq
Requirement
\neq
Clause
}
\]

**中文业务释义：** 句子 ≠ 业务要求 ≠ 业务条款。

这就是纯 NLP 切句不够的原因。

---

# 十二、Clause ID 必须稳定

建议建立：

```text
clause_id    # 中文：条款标识
```

例如：

```text
PRJ001-DOC003-S04-C012    # 中文：稳定条款编号示例：项目001-文档003-章节04-条款012
```

代表：

```text
Project 001    # 中文：项目 001
Document 003    # 中文：文档 003
Section 04    # 中文：章节 04
Clause 012    # 中文：条款 012
```

Clause ID 用于：

```text
Finding定位
Rule命中
人工复核
报告跳转
Benchmark标注
版本Diff
```

所以：

\[
\boxed{
NoStableClauseID
=
NoReliableAuditTrail
}
\]

**中文业务释义：** 没有稳定条款ID = 没有可靠审计链。

---

# 十三、核心心智模型 ④
# Evidence Span 必须能回到原文位置

Clause 不是只保存清洗后的文本。

还要保存：

```text
page_number    # 中文：页编号

paragraph_index    # 中文：段落索引

table_id    # 中文：表格标识

row_id    # 中文：行标识

cell_id    # 中文：单元格标识

char_start    # 中文：字符开始

char_end    # 中文：字符结束

bounding_box    # 中文：边界框位置框
可选

source_text    # 中文：来源文本
```

这样一个 Finding 才能真正回答：

> 原文在哪里？

所以：

\[
\boxed{
Evidence
\neq
CopiedTextOnly
}
\]

**中文业务释义：** 证据 ≠ 仅复制出的文本。

真正 Evidence 应该包含：

\[
\boxed{
Text
+
Location
+
SourceIdentity
}
\]

**中文业务释义：** 文本 + 位置 + 来源身份。

---

# 十四、第五层 Schema：Requirement

一个 Clause 里面可能有多个：

# Requirement
## 业务要求

例如：

```text
供应商应具有 A 证书，并在本地设置服务机构，
同时近三年具有两个同类项目业绩。
```

实际上包含：

```text
Requirement 1    # 中文：要求1
A证书

Requirement 2    # 中文：要求2
本地服务机构

Requirement 3    # 中文：要求3
近三年两个同类业绩
```

这三个要求：

> 可能命中三个完全不同的规则。

因此：

\[
\boxed{
Clause
可以包含
MultipleRequirements
}
\]

---

# 十五、Requirement 应拆成什么结构？

可以抽象成：

\[
\boxed{
Requirement
=
Subject
+
Action
+
Object
+
Condition
+
Threshold
+
Timing
+
Consequence
}
\]

**中文业务释义：** 业务要求 = 主体 + 动作 + 对象 + 条件 + 阈值 + 时点 + 后果。

例如：

```text
供应商须在投标截止前在本市设立分公司，否则投标无效。
```

可以拆为：

```text
Subject    # 中文：主体
供应商

Action    # 中文：动作
设立

Object    # 中文：对象
分公司

Condition    # 中文：条件
在本市

Timing    # 中文：适用 / 发生时点
投标截止前

Consequence    # 中文：不满足时的后果
否则投标无效
```

于是它不再只是自然语言。

而成为：

# Structured Requirement
## 结构化要求

---

# 十六、核心心智模型 ⑤
# `RequirementStructure` 比 `Keyword` 更接近合规判断

例如：

```text
本市
```

这个词单独出现：

> 没有足够信息。

但结构：

```text
Subject = Supplier    # 中文：主体 = 供应商
Action = MustEstablish    # 中文：动作 = 必须设立
Object = Branch    # 中文：对象 = 分支机构
Location = ThisCity    # 中文：地点条件 = 本市
Timing = BeforeBid    # 中文：适用 / 发生时点 = 之前投标
Consequence = QualificationFailure    # 中文：不满足时的后果 = 资格失败 / 不满足
```

已经明显更接近：

> 合规审查需要的业务事实。

所以：

\[
\boxed{
Keyword
<
StructuredRequirement
}
\]

**中文业务释义：** 关键词 < 结构化业务要求。（这里的 `>` / `<` 若用于心智模型，表示工程优先级或信息价值关系，不一定是数学数值大小。）

这里的 `<` 表示：

> 对合规判断的信息量更低。

---

# 十七、Normative Strength：要求有多“硬”？

采购文件常见：

```text
必须
应当
须
不得
应
原则上
建议
优先
可以
鼓励
```

这些词反映：

# Normative Strength
## 规范强度

可以标准化：

```text
MANDATORY    # 中文：强制要求
PROHIBITED    # 中文：禁止性要求
CONDITIONAL    # 中文：条件性要求
PREFERRED    # 中文：优先 / 偏好
OPTIONAL    # 中文：可选
ADVISORY    # 中文：建议性要求
```

例如：

```text
必须
→ MANDATORY    # 中文： → 强制要求

不得
→ PROHIBITED    # 中文： → 禁止性要求

优先
→ PREFERRED    # 中文： → 优先 / 偏好
```

但不能只靠词典。

要看整句结构。

---

# 十八、为什么 Normative Strength 很重要？

因为：

```text
“具有A证书的优先”
```

和：

```text
“必须具有A证书”
```

合规影响不同。

前者可能是：

> 评分 / 优先因素。

后者可能是：

> 准入条件。

所以：

\[
\boxed{
SameObject
+
DifferentNormativeStrength
=
DifferentRisk
}
\]

**中文业务释义：** 同一对象 + 不同规范强度 = 不同风险。

---

# 十九、Business Function：一条要求到底起什么作用？

这是非常重要的一层。

同一个 Requirement 要知道它的：

# Business Function
## 业务功能

例如：

```text
ENTRY_GATE    # 中文：准入门槛
准入门槛

SUBSTANTIVE_GATE    # 中文：实质性门槛
实质性响应门槛

SCORING_FACTOR    # 中文：评分因素
评分因素

PERFORMANCE_OBLIGATION    # 中文：履约义务
履约义务

PREFERENCE    # 中文：政策偏好 / 优先待遇
政策优惠

INFORMATION_DISCLOSURE    # 中文：信息披露要求
信息披露

DOCUMENT_SUBMISSION    # 中文：材料提交要求
材料提交
```

于是：

\[
\boxed{
ClauseRole
\neq
BusinessFunction
}
\]

**中文业务释义：** 条款角色 ≠ 业务功能 / 条款作用。

一个技术要求：

> 可能同时又是实质性门槛。

一个商务要求：

> 可能只是履约义务。

---

# 二十、核心心智模型 ⑥
# `WhereItAppears` 和 `WhatItDoes` 必须分开

例如：

```text
SectionRole = TECHNICAL    # 中文：章节业务角色 = 技术要求章节
```

只说明：

> 它出现在技术章节。

但：

```text
BusinessFunction = SCORING_FACTOR    # 中文：业务功能 = 评分因素
```

说明：

> 它实际上参与评分。

所以模型需要同时知道：

```text
位置
+
作用
```

---

# 二十一、Qualification 到底怎么建模？

# Qualification
## 资格条件

核心问题：

> **决定供应商有没有资格进入后续竞争。**

因此 Qualification Clause 至少要抽：

```text
qualification_type    # 中文：资格条件类型

subject    # 中文：主体 / 事项

required_document    # 中文：是否需要文档

required_certificate    # 中文：是否需要证书

required_experience    # 中文：是否需要业绩

required_financial_condition    # 中文：是否需要财务条件

required_location    # 中文：是否需要位置 / 地域

required_enterprise_form    # 中文：是否需要企业表单

required_industry    # 中文：是否需要行业

required_scale    # 中文：要求的企业规模条件

time_window    # 中文：适用时间窗口

failure_consequence    # 中文：不满足条件的后果
```

这直接关联后面的：

```text
地域限制
行业限制
规模限制
企业形式限制
业绩限制
```

也就是 D01-D22 里大量规则。

---

# 二十二、Technical Requirement 怎样建模？

# Technical Requirement
## 技术要求

至少抽：

```text
technical_object    # 中文：技术对象

parameter_name    # 中文：参数名称

parameter_value    # 中文：参数值

operator    # 中文：运算符 / 运营主体
>= / <= / = / range    # 中文：大于等于 / 小于等于 / 等于 / 区间

brand_reference    # 中文：品牌引用

patent_reference    # 中文：专利引用

origin_reference    # 中文：原产地引用

component_reference    # 中文：部分引用

compatibility_requirement    # 中文：兼容性要求

performance_requirement    # 中文：履约要求

test_method    # 中文：测试方法

proof_document    # 中文：证明材料文档

mandatory_or_scored    # 中文：强制OR评分
```

为什么？

因为：

```text
“CPU 主频不得低于 X”
```

和：

```text
“须采用某品牌某型号 CPU”
```

语义都属于技术要求，

但合规风险类型完全不同。

---

# 二十三、核心心智模型 ⑦
# `TechnicalSpecificity` 不等于 `TechnicalDiscrimination`

技术参数具体：

> 不自动等于违法违规。

需要继续判断：

```text
是否与项目实际需要相适应

是否指向特定供应商 / 产品

是否存在合理功能目标

是否可以通过多个竞争产品满足

是否存在等效机制
```

所以：

\[
\boxed{
Specific
\neq
Discriminatory
}
\]

**中文业务释义：** 具体 / 严格 ≠ 歧视性 / 不合理排斥。

---

# 二十四、Commercial Requirement 怎样建模？

# Commercial Requirement
## 商务要求

例如：

```text
付款方式
交付时间
服务地点
质保
售后响应
履约保证
人员驻场
服务机构
保险
```

建议抽：

```text
commercial_type    # 中文：商务类型

obligation_subject    # 中文：义务主体 / 事项

location    # 中文：位置 / 地域

timing    # 中文：时点

duration    # 中文：持续时长

service_level    # 中文：服务层级

payment_condition    # 中文：付款条件

warranty_period    # 中文：质保期限

response_time    # 中文：响应时间

on_site_requirement    # 中文：ON现场要求

pre_award_or_post_award    # 中文：前中标 / 成交OR后中标 / 成交

failure_consequence    # 中文：不满足条件的后果
```

这里特别重要的是：

\[
\boxed{
PreAward
\neq
PostAward
}
\]

**中文业务释义：** 中标前 ≠ 中标后。

---

# 二十五、为什么“投标前”与“中标后”差别巨大？

例如：

```text
投标前必须在本地设立分公司
```

和：

```text
中标后为履约需要建立本地服务能力
```

表面都包含：

```text
本地
服务机构
```

但竞争影响可能完全不同。

所以必须抽：

# Temporal Position
## 条件发生时点

```text
PRE_BID    # 中文：投标前
AT_BID    # 中文：投标 / 响应时
POST_AWARD    # 中文：中标 / 成交后
PERFORMANCE    # 中文：合同履约阶段
```

因此：

\[
\boxed{
Timing
是合规语义的一部分
}
\]

---

# 二十六、Scoring Criteria 为什么最复杂？

# Scoring Criteria
## 评分标准

一条评分规则通常不是普通句子。

它更像：

\[
\boxed{
ScoreRule
=
Condition
+
Score
+
Cap
+
Evidence
+
Aggregation
}
\]

**中文业务释义：** Score规则 = 条件 + Score + Cap + 证据 + Aggregation。

例如：

```text
每提供一个同类项目业绩得2分，最高6分。
```

结构化为：

```text
scoring_factor = similar_project_experience    # 中文：评分因素 = 类似项目业绩

unit_score = 2    # 中文：单位评分 = 2

max_score = 6    # 中文：MAX评分 = 6

counting_rule = per_project    # 中文：计分规则 = 逐项 / 每项目

evidence = contract / acceptance_document    # 中文：证明材料 = 合同 / 验收材料
```

这才能真正做：

```text
合规审查
Benchmark    # 中文：评测基准
规则判断
```

---

# 二十七、核心心智模型 ⑧
# `ScoringText` 必须转成 `ScoringFunction`

因为合规检查要判断：

```text
评分项是否可量化？

分值是否对应明确条件？

是否把不应作为评分因素的条件加分？

是否与采购需求和履约相关？

是否设置特定地域 / 行业 / 奖项 / 业绩加分？
```

所以：

\[
\boxed{
ScoringClause
\rightarrow
ScoringFunction
}
\]

**中文业务释义：** 评分条款 → 评分函数。

---

# 二十八、评分项至少抽哪些字段？

```text
score_item_id    # 中文：评分品目 / 项标识

factor_name    # 中文：因素名称

factor_type    # 中文：因素类型

condition    # 中文：条件

score_operator    # 中文：评分运算符 / 运营主体

score_value    # 中文：评分值

unit_score    # 中文：单位评分

maximum_score    # 中文：最高评分

minimum_score    # 中文：最低评分

evidence_required    # 中文：证据是否需要

evidence_type    # 中文：证据类型

subject    # 中文：主体 / 事项

industry_constraint    # 中文：行业限制条件

region_constraint    # 中文：地域限制条件

award_constraint    # 中文：中标 / 成交限制条件

experience_constraint    # 中文：业绩限制条件

certificate_constraint    # 中文：证书限制条件

personnel_constraint    # 中文：人员限制条件

brand_constraint    # 中文：品牌限制条件

quantifiable    # 中文：可量化

subjective_component    # 中文：主观部分
```

这会直接支持后面的：

# `ProcurementScoringCompliance_V1`

---

# 二十九、Substantive Requirement

# Substantive Requirement
## 实质性条款

表示：

> 不满足可能导致响应无效、否决投标或不能进入下一阶段的关键条件。

至少记录：

```text
is_substantive    # 中文：是否实质性

failure_consequence    # 中文：不满足条件的后果

explicit_rejection_language    # 中文：明确否决 / 无效表述

linked_clause_ids    # 中文：关联条款标识列表
```

因为有时：

> 一个要求本身写在技术章节，

但另一条说明：

```text
带★项不允许负偏离，否则投标无效
```

所以系统必须解析：

# Cross-reference
## 跨条款引用

---

# 三十、核心心智模型 ⑨
# `ClauseMeaning` 可能来自其他 Clause

这就是：

\[
\boxed{
LocalText
\neq
CompleteMeaning
}
\]

**中文业务释义：** 局部文本 ≠ 完整含义。

例如：

```text
Clause A    # 中文：条款A
技术参数X

Clause B    # 中文：条款B
所有带★条款均为实质性要求
```

A 的真正业务功能：

> 需要结合 B 才能确定。

所以 Document Schema 必须支持：

```text
references_to    # 中文：引用关系截止
referenced_by    # 中文：被引用由
depends_on    # 中文：依赖ON
defines    # 中文：定义
applies_to    # 中文：适用于截止
```

---

# 三十一、Contract Clause 为什么不能被忽略？

# Contract
## 合同条款

很多不合理条件可能：

> 不出现在资格和评分中，

而藏在：

```text
付款
验收
违约责任
知识产权
售后
人员驻场
履约地点
```

里。

合同侧至少抽：

```text
obligation    # 中文：义务

obligation_subject    # 中文：义务主体 / 事项

counterparty    # 中文：合同相对方

trigger    # 中文：触发

deadline    # 中文：截止时间

payment_term    # 中文：付款条件

acceptance_condition    # 中文：验收条件

breach_consequence    # 中文：违约后果

penalty    # 中文：处罚

termination_condition    # 中文：合同解除条件

performance_location    # 中文：履约位置 / 地域
```

因此：

\[
\boxed{
TenderCompliance
\neq
QualificationOnly
}
\]

**中文业务释义：** Tender合规 ≠ 资格仅。

---

# 三十二、Table 为什么是采购文件解析中的高风险区域？

采购文件大量关键内容存在：

```text
技术参数表
评分表
商务偏离表
资格审查表
符合性审查表
报价表
```

这些不是普通文本段落。

例如评分表：

| 评分因素 | 分值 | 评分标准 |
|---|---:|---|
| 类似业绩 | 6 | 每个2分，最高6分 |

如果 OCR 变成：

```text
类似业绩 6 每个2分最高6分
```

可能还能勉强理解。

但复杂表格存在：

```text
合并单元格
多级表头
跨行条件
脚注
```

所以：

\[
\boxed{
TableFlattening
可能破坏
BusinessSemantics
}
\]

---

# 三十三、核心心智模型 ⑩
# `VisualStructure` 是文档语义的一部分

因此 Document Parser 需要保留：

```text
table_id    # 中文：表格标识

row_index    # 中文：行索引

column_index    # 中文：表格列序号

header_path    # 中文：多级表头路径

merged_cell_relation    # 中文：合并单元格关联

footnote_link    # 中文：脚注关联
```

而不是只输出：

> 一大段 OCR 文本。

---

# 三十四、附件和正文之间的关系也要建模

例如：

```text
正文：
详见附件3技术参数表
```

真正要求：

> 在附件 3。

所以需要：

```text
attachment_id    # 中文：附件标识

referenced_by    # 中文：被引用由

attachment_role    # 中文：附件业务角色

inherits_section_role    # 中文：继承章节业务角色
```

因此：

\[
\boxed{
MainDocument
\neq
WholeRequirementSet
}
\]

**中文业务释义：** 正文 ≠ 完整要求集合。

---

# 三十五、Negative Requirement 也必须识别

例如：

```text
不得联合体投标

不接受进口产品

不得分包

不得使用某类材料
```

需要识别：

# Prohibition
## 禁止性要求

所以 Requirement 不能只有：

```text
required = true    # 中文：是否需要 = 正确 / 真
```

还要有：

```text
polarity    # 中文：要求极性
=
REQUIRED    # 中文：必须
PROHIBITED    # 中文：禁止性要求
ALLOWED    # 中文：允许
PREFERRED    # 中文：优先 / 偏好
```

---

# 三十六、Condition Scope

一条要求可能只适用于：

```text
某采购包
某品目
某岗位
某评分项
某阶段
```

如果系统错误扩展到整个项目：

> 会误报。

所以要抽：

# Scope
## 适用范围

例如：

```text
lot_id    # 中文：采购包标识

item_id    # 中文：品目 / 项标识

role_id    # 中文：业务角色标识

stage    # 中文：阶段

supplier_type    # 中文：供应商类型

condition_scope    # 中文：条件范围
```

因此：

\[
\boxed{
ClauseScope
必须显式
}
\]

---

# 三十七、Coreference：谁是“其”“该供应商”“上述人员”？

真实采购文件大量使用：

```text
其
该供应商
上述人员
前述项目
本项
上述证书
```

所以需要：

# Coreference Resolution
## 指代消解

把：

```text
“其应具有……”
```

恢复成：

```text
Subject = Supplier    # 中文：主体 = 供应商
```

否则结构化 Requirement 会失去主体。

---

# 三十八、核心心智模型 ⑪
# `EntityResolution` 是合规推理的前置条件

如果主体识别错：

> 后面 Rule Engine 再精准也没用。

所以：

\[
\boxed{
BadParsing
\rightarrow
BadCompliance
}
\]

**中文业务释义：** BadParsing → Bad合规。

---

# 三十九、Conflict Detection：采购文件内部自己打架怎么办？

真实文件可能出现：

```text
公告资格条件
≠
采购文件资格条件

正文评分表
≠
附件评分表

技术参数
≠
合同要求
```

因此需要：

# Intra-document Conflict
## 文件内部冲突

例如：

```text
conflict_id    # 中文：冲突标识

clause_a    # 中文：条款A

clause_b    # 中文：条款B

conflict_type    # 中文：冲突类型

severity    # 中文：严重程度

needs_human_review    # 中文：是否需要人工复核
```

所以：

\[
\boxed{
DocumentConsistency
也是
ComplianceSignal
}
\]

---

# 四十、Duplicate Requirement

同一个要求可能：

> 在多个位置重复。

不能每出现一次就生成一个 Finding。

所以需要：

# Requirement Canonicalization
## 要求归一化

例如：

```text
requirement_group_id    # 中文：要求分组标识
```

把：

```text
公告
资格章节
评审表
```

里的同一业务要求关联起来。

因此：

\[
\boxed{
DuplicateText
\neq
MultipleIndependentRisks
}
\]

**中文业务释义：** Duplicate文本 ≠ MultipleIndependentRisks。

---

# 四十一、但是“重复出现”本身也有业务意义

如果一个条件同时出现在：

```text
资格要求
+
评分标准
```

它可能意味着：

> 同一个条件既作为准入门槛又作为加分因素。

这可能需要特别检查。

所以：

\[
\boxed{
Deduplicate
\neq
EraseRoleDifferences
}
\]

**中文业务释义：** Deduplicate ≠ Erase角色Differences。

归一化后仍然要保留：

> 每个原始出现位置和业务作用。

---

# 四十二、D01-D22 怎样接入 Document Schema？

每一条 Clause / Requirement 都可以产生：

```text
candidate_rule_ids    # 中文：候选规则标识列表
```

例如：

```text
D01    # 中文：D01 规则编号（附件9工程化规则标识）
D05    # 中文：D05 规则编号（附件9工程化规则标识）
D12    # 中文：D12 规则编号（附件9工程化规则标识）
```

但注意：

\[
\boxed{
CandidateRule
\neq
ConfirmedRule
}
\]

**中文业务释义：** 候选规则 ≠ 证据支持 / 已确认规则。

Document Schema 只负责：

> 把业务事实准备好。

真正的规则判断：

> 在第 4 阶段 RuleSet 和后续 Hybrid Engine 中完成。

---

# 四十三、核心心智模型 ⑫
# `Parsing` 和 `Judgment` 必须分层

Document Parser 做：

```text
原文恢复
结构识别
Clause切分
Requirement结构化
角色分类
引用关系
表格恢复
```

Rule Engine / LLM Judge 做：

```text
是否违规
是否存在合理性
是否有例外
风险等级
```

所以：

\[
\boxed{
Parser
\neq
Judge
}
\]

**中文业务释义：** 文档解析器 ≠ 判断器。

---

# 四十四、为什么这一层必须有 Gold Annotation？

如果 Document Schema 本身错了：

> 后面的合规模型会在错误结构上工作。

因此 Stage 10 的 Dataset 不只标：

```text
违规 / 不违规
```

还要标：

```text
Section Role    # 中文：章节业务角色
Clause Boundary    # 中文：条款边界
Requirement Boundary    # 中文：要求边界
Business Function    # 中文：业务功能
Normative Strength    # 中文：规范强度
Cross Reference    # 中文：跨条款引用
Table Structure    # 中文：表格结构
Evidence Span    # 中文：证据片段及原文定位
```

所以：

\[
\boxed{
ComplianceGold
需要
ParsingGold
}
\]

---

# 四十五、文档结构的“最低可靠性门槛”

如果出现：

```text
关键页 OCR失败

评分表无法恢复

资格条件章节缺失

附件未读取

Clause ID不稳定

更正文件未合并
```

系统不应该：

> 继续输出“全文件已完成合规检查”。

而应：

```text
parse_status = PARTIAL    # 中文：解析状态 = 部分完成 / 部分解析

coverage_status = INCOMPLETE    # 中文：覆盖状态 = 覆盖不完整

human_review_required = true    # 中文：是否需要人工复核 = 正确 / 真
```

所以：

\[
\boxed{
ParseFailure
\Rightarrow
CoverageFailure
}
\]

**中文业务释义：** 解析失败 ⇒ 覆盖失败。

---

# 四十六、核心心智模型 ⑬
# `ParserConfidence` 必须进入最终 Coverage Report

如果某一页：

> 解析置信度很低，

最终报告必须告诉用户：

> 这里存在未可靠检查区域。

而不能静默忽略。

---

# 四十七、最终 `ProcurementDocumentSchema_V1`

第一版建议至少形成：

```text
Project    # 中文：采购项目

Document    # 中文：采购文档

DocumentVersion    # 中文：文档版本

Section    # 中文：章节

Clause    # 中文：条款

Requirement    # 中文：业务要求

ScoringFunction    # 中文：评分功能 / 作用

ContractObligation    # 中文：合同义务

EvidenceSpan    # 中文：证据片段及原文定位

CrossReference    # 中文：跨条款引用

TableStructure    # 中文：表格结构

Attachment    # 中文：附件

Entity    # 中文：实体 / 主体

Conflict    # 中文：冲突

ReviewCoverage    # 中文：复核覆盖
```

---

# 四十八、Project Schema

```text
project_id    # 中文：项目标识
project_name    # 中文：项目名称
procurement_entity    # 中文：采购实体 / 主体
procurement_agency    # 中文：采购代理机构
procurement_category    # 中文：采购类别
procurement_method    # 中文：采购方法
budget_amount    # 中文：预算金额
maximum_price    # 中文：最高价格
jurisdiction    # 中文：辖区
announcement_date    # 中文：公告日期
bid_deadline    # 中文：投标截止时间
evaluation_date    # 中文：评审日期
policy_snapshot_id    # 中文：政策法规快照标识
```

---

# 四十九、Document Schema

```text
document_id    # 中文：文档标识
project_id    # 中文：项目标识
document_type    # 中文：文档类型
document_title    # 中文：文档标题
document_version    # 中文：文档版本
source_file    # 中文：来源文件
source_hash    # 中文：来源哈希
publication_time    # 中文：发布时间
supersedes_document_id    # 中文：替代文档标识
current_for_review    # 中文：是否为当前审查使用版本
parse_status    # 中文：解析状态
page_count    # 中文：页数量
```

---

# 五十、Section Schema

```text
section_id    # 中文：章节标识
document_id    # 中文：文档标识
parent_section_id    # 中文：父级 / 上级章节标识
section_number    # 中文：章节编号
section_title    # 中文：章节标题
section_level    # 中文：章节层级
section_role    # 中文：章节业务角色
page_start    # 中文：页开始
page_end    # 中文：页结束
order_index    # 中文：顺序索引
```

---

# 五十一、Clause Schema

```text
clause_id    # 中文：条款标识
section_id    # 中文：章节标识

raw_text    # 中文：原始文本
normalized_text    # 中文：标准化文本

page_number    # 中文：页编号
paragraph_index    # 中文：段落索引

table_id    # 中文：表格标识
row_id    # 中文：行标识
cell_id    # 中文：单元格标识

section_role    # 中文：章节业务角色
business_function    # 中文：业务功能

normative_strength    # 中文：规范强度
polarity    # 中文：要求极性

is_substantive    # 中文：是否实质性

applies_to    # 中文：适用于截止
timing    # 中文：时点

candidate_rule_ids    # 中文：候选规则标识列表

references_to    # 中文：引用关系截止
referenced_by    # 中文：被引用由

parse_confidence    # 中文：解析置信度
```

---

# 五十二、Requirement Schema

```text
requirement_id    # 中文：要求标识
clause_id    # 中文：条款标识

subject    # 中文：主体 / 事项

action    # 中文：动作

object    # 中文：对象

condition    # 中文：条件

threshold    # 中文：阈值

unit    # 中文：单位

location    # 中文：位置 / 地域

industry    # 中文：行业

enterprise_form    # 中文：企业表单

ownership    # 中文：所有制

experience    # 中文：业绩

certificate    # 中文：证书

brand    # 中文：品牌

patent    # 中文：专利

origin    # 中文：原产地

timing    # 中文：时点

consequence    # 中文：后果

pre_award_post_award    # 中文：前中标 / 成交后中标 / 成交

scope    # 中文：范围

canonical_requirement_id    # 中文：归一化要求标识
```

---

# 五十三、ScoringFunction Schema

```text
score_item_id    # 中文：评分品目 / 项标识
clause_id    # 中文：条款标识

factor_name    # 中文：因素名称
factor_type    # 中文：因素类型

condition    # 中文：条件

score_value    # 中文：评分值
unit_score    # 中文：单位评分
max_score    # 中文：MAX评分
min_score    # 中文：MIN评分

counting_rule    # 中文：计分规则

evidence_required    # 中文：证据是否需要
evidence_type    # 中文：证据类型

quantifiable    # 中文：可量化
subjective_component    # 中文：主观部分

region_constraint    # 中文：地域限制条件
industry_constraint    # 中文：行业限制条件
award_constraint    # 中文：中标 / 成交限制条件
experience_constraint    # 中文：业绩限制条件
certificate_constraint    # 中文：证书限制条件
personnel_constraint    # 中文：人员限制条件
brand_constraint    # 中文：品牌限制条件
```

---

# 五十四、EvidenceSpan Schema

```text
evidence_id    # 中文：证据标识

document_id    # 中文：文档标识
document_version    # 中文：文档版本

page_number    # 中文：页编号

section_id    # 中文：章节标识
clause_id    # 中文：条款标识
requirement_id    # 中文：要求标识

char_start    # 中文：字符开始
char_end    # 中文：字符结束

table_id    # 中文：表格标识
row_id    # 中文：行标识
cell_id    # 中文：单元格标识

source_text    # 中文：来源文本

source_hash    # 中文：来源哈希
```

---

# 五十五、CrossReference Schema

```text
reference_id    # 中文：引用标识

source_clause_id    # 中文：来源条款标识
target_clause_id    # 中文：目标条款标识

reference_type    # 中文：引用类型

applies_to    # 中文：适用于截止
defines    # 中文：定义
modifies    # 中文：修改
supersedes    # 中文：替代
explains    # 中文：解释
exception_to    # 中文：例外截止
```

---

# 五十六、ReviewCoverage Schema

```text
coverage_id    # 中文：覆盖标识

project_id    # 中文：项目标识
document_id    # 中文：文档标识

domain    # 中文：审查业务域

expected_units    # 中文：预期应检查的业务单元数量
parsed_units    # 中文：已成功解析的业务单元数量
reviewed_units    # 中文：已审查单元

parse_failures    # 中文：解析失败项

missing_attachments    # 中文：缺失附件

unresolved_references    # 中文：未解决引用关系

coverage_rate    # 中文：覆盖比例

coverage_status    # 中文：覆盖状态

human_review_required    # 中文：是否需要人工复核
```

---

# 五十七、本阶段最重要的 13 个核心心智模型

> **心智模型 ①：`TextChunk ≠ BusinessClause`。RAG 文本块是检索单位，业务条款才是合规判断单位。**

> **心智模型 ②：`Meaning = Text + BusinessPosition`。同一句话出现在资格、评分、技术、合同中的含义可能完全不同。**

> **心智模型 ③：`Project ≠ SingleDocument`。政府采购项目往往由公告、采购文件、更正、附件、合同等多个版本化文档组成。**

> **心智模型 ④：`SectionTitle ≠ SectionRole`。原始标题必须保留，同时映射到统一业务角色。**

> **心智模型 ⑤：`ClauseBoundary ≠ ParagraphBoundary`。条款边界是业务边界，不是排版边界。**

> **心智模型 ⑥：`RequirementStructure > Keyword`。Subject、Action、Object、Condition、Timing、Consequence 比敏感词更接近真实合规判断。**

> **心智模型 ⑦：`WhereItAppears ≠ WhatItDoes`。章节位置和业务功能必须分别建模。**

> **心智模型 ⑧：`Specific ≠ Discriminatory`。技术参数具体不自动等于差别歧视，仍需结合实际需要、竞争影响和等效可能。**

> **心智模型 ⑨：`PreAward ≠ PostAward`。投标前门槛和中标后履约要求的竞争影响完全不同。**

> **心智模型 ⑩：`ScoringText → ScoringFunction`。评分标准必须结构化成条件、分值、上限、证据和计算规则。**

> **心智模型 ⑪：`LocalText ≠ CompleteMeaning`。跨条款引用、脚注、附件和总则可能改变当前条款含义。**

> **心智模型 ⑫：`Parser ≠ Judge`。解析层负责恢复业务事实，判断层负责形成合规结论。**

> **心智模型 ⑬：`ParseFailure ⇒ CoverageFailure`。关键内容没有可靠解析，就不能声称完成全文件合规检查。**

---

# 五十八、把整个 Procurement Document Schema 压成一张工程图

```text
                           Project    # 中文：采购项目
                             项目
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
         Document A       Document B       Attachment    # 中文：文档A文档B附件
          采购文件          更正文件           附件
             │                │                │
             └────────────────┼────────────────┘
                              ▼
                         Version Resolve    # 中文：文档版本解析与当前有效版本确认
                          版本解析
                              │
                              ▼
                          Section Tree    # 中文：采购文件章节树
                           章节树
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
          Qualification    Technical      Scoring    # 中文：资格技术评分
             资格             技术           评分
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                            Clause    # 中文：条款
                            条款
                              │
                              ▼
                         Requirement    # 中文：业务要求
                           业务要求
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
   Subject/Action        Condition/Timing     Consequence    # 中文：主体 / 事项动作条件时点后果
     主体与动作             条件与时点             后果
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
                       Business Function    # 中文：业务功能
                          业务作用
                              │
                              ▼
                        Evidence Span    # 中文：证据片段及原文定位
                          证据定位
                              │
                              ▼
                    Candidate D01-D22    # 中文：候选D01D22
                       候选规则映射
                              │
                              ▼
                     Review Coverage    # 中文：复核覆盖
                         检查覆盖状态
```

脑中最后只留一句：

> **采购文件合规 AI 不能把真实采购文件看成一串 Token。它必须先恢复 Project → Document → Version → Section → Clause → Requirement → Business Function → Evidence Span 的业务结构，再把 D01-D22 和其他合规规则作用到这些结构化对象上；否则模型即使语言理解很好，也可能在错误的业务位置上作出错误判断。**

---

# 第十一课 · 第 3 阶段掌握测试

现在不回看正文，你应该能够解释：

```text
为什么 Text Chunk 不等于 Business Clause？

为什么同一句话在资格条件和合同履约中可能有不同合规含义？

为什么 Project 不能等同于一个文件？

为什么 Document Version 必须进入 Finding？

Section Title 和 Section Role 有什么区别？

为什么 Clause Boundary 不能按段落机械切？

为什么一个 Clause 可能包含多个 Requirement？

Requirement 为什么要拆成 Subject / Action / Object / Condition / Timing / Consequence？

Normative Strength 和 Business Function 分别解决什么问题？

Qualification / Technical / Commercial / Scoring / Contract 分别需要抽哪些业务字段？

为什么 PreAward 和 PostAward 必须区分？

为什么评分文本必须转成 Scoring Function？

为什么跨条款引用会改变当前 Clause 的真实含义？

为什么 Table Structure 是业务语义的一部分？

为什么附件不能当成普通补充材料忽略？

为什么 Parser 和 Judge 必须分层？

为什么 D01-D22 在这一阶段只能是 Candidate Rule，而不能直接 Confirm？

为什么 Parse Failure 必须传播到 Coverage Failure？
```

如果这些能够完整解释：

\[
\boxed{
第十一课第3阶段真正掌握
}
\]

---

# 下一阶段：第十一课 · 第 4 阶段
# “四类”专项整治——采购人设置差别歧视条款：附件 9 的 22 项规则工程化
## 怎样把 7 类问题、22 项具体表现形式转成机器可执行、可解释、可审计的政府采购合规规则体系？

下一阶段会正式建立：

# `ProcurementDiscrimination22RuleSet_V1`

最重要的边界：

\[
\boxed{
22项
\neq
22个关键词
}
\]

而是：

\[
\boxed{
D01\sim D22
=
RuleObject
+
Trigger
+
Context
+
Exception
+
Evidence
+
DecisionLogic
}
\]

**中文业务释义：** D01规则～ D22规则 = 规则对象 + 触发条件 + 业务上下文 + 例外 + 证据 + 决策逻辑。
