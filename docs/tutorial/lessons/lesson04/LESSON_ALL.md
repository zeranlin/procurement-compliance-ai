# 第四课：政府采购数据工程与训练数据集

> **V2 教学增强版。** 共 12 个阶段；主要产物/主线：`ProcurementDataset_V0.1`。  
> 核心心智模型前置、中文释义增强、详细正文完整保留。

---


<!-- LESSON 04 STAGE 01 START -->

# 第四课 · 第 1 阶段：Task Schema 与数据单元设计
## 为什么“先收集 10 万份采购文件”可能从第一天就把整个数据工程做错？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **文件 ≠ 数据样本**
2. **Schema = 我们对“一个样本是什么”的正式契约**
3. **先定义任务，再定义样本，再开始收数据**
4. **一个原始采购文件可以产生很多不同任务的数据**
5. **Input、Label、Evidence、Metadata 必须分清楚**
6. **数据最重要的不是“多少条”， 而是每一条到底代表什么**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `Sample` | 样本：具有明确输入、目标和来源的一条训练/评测记录 |
| `Input` | 输入：模型在当前任务中允许看到的条件信息 |
| `Metadata` | 元数据：项目、来源、时间、地区、版本等辅助信息 |
| `SFT` | 监督微调：用监督样本继续更新模型参数 |
| `Hard Negative` | 高难负例：表面像风险但正确结论不应判风险 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Split` | 数据切分：按项目/时间/地区划分训练、验证、测试数据 |
| `Raw Document` | 原始文档：未经结构化处理的采购文件源材料 |
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |

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

第三课结束的时候，我们已经拥有了一件很重要的东西：

```text
可运行的基础模型
        ↓
可以做Baseline
        ↓
可以开始发现模型错误
```

从第四课开始，我们要处理另一个世界：

# Data

很多团队第一次做行业大模型，会马上开始：

```text
下载PDF
下载PDF
下载PDF
下载PDF
……
```

硬盘迅速变成：

```text
200GB
500GB
2TB
```

然后非常兴奋地说：

> “我们已经有海量政府采购数据了。”

但这里有一个非常致命的问题：

> **这些 PDF 到底准备拿来教模型学什么？**

如果这句话回答不清楚，那么：

> 文件越多，后面可能越乱。

所以第四课第一阶段，我们暂时：

**不解析 PDF。**

**不做 OCR。**

**不做 LoRA。**

甚至：

**先不写数据清洗代码。**

我们先解决最根本的问题：

# 一条真正的机器学习样本，到底应该长什么样？

---

# 一、本阶段真正要解决的一个核心问题

今天只解决：

> **如何把“政府采购业务问题”翻译成一个机器能够训练、评测、追踪的数据结构？**

最后要得到的不是一堆文件。

而是一份：

# `ProcurementTaskSchema_V0.1`

也就是：

> **ProcurementAI 数据世界的第一份“宪法”。**

---

# 二、先记住今天最重要的 6 个核心心智模型

```text
① 文件 ≠ 数据样本

② Schema = 我们对“一个样本是什么”的正式契约

③ 先定义任务，再定义样本，再开始收数据

④ 一个原始采购文件可以产生很多不同任务的数据

⑤ Input、Label、Evidence、Metadata 必须分清楚

⑥ 数据最重要的不是“多少条”，
   而是每一条到底代表什么
```

这六句话如果真正吃透，

第四课后面的：

- 文档解析；
- 清洗；
- 去重；
- 标注；
- Hard Negative；
- Train/Test Split；

都会突然清晰很多。

---

# 三、第一个核心心智模型：文件 ≠ 样本

假设我们下载了一份：

```text
某市智慧交通系统采购项目招标文件.pdf
```

200 页。

这是：

# Raw Document

也就是：

> 原始文件。

但它是不是一条训练样本？

通常不是。

---

# 四、为什么不是？

因为这份文件里面可能同时包含：

```text
采购公告
资格条件
采购需求
技术参数
商务要求
评分办法
合同条款
附件
格式模板
```

如果直接把整本 PDF 扔给模型说：

> “学习吧。”

机器到底要学什么？

非常模糊。

---

# 五、真正的机器学习样本通常需要一个清楚的问题

比如：

> **这条供应商资格条件是否存在潜在不合理限制？**

这时候：

输入是什么？

```text
供应商须在本市注册成立5年以上。
```

目标是什么？

```text
存在潜在风险
```

风险类型是什么？

```text
供应商资格 / 地域性限制
```

这才开始像：

# Sample

---

# 六、所以要先把三个概念彻底分开

```text
Raw Document
原始文件

        ↓

Data Unit
从文件中切出的业务单元

        ↓

Training / Evaluation Sample
具有明确输入和目标的数据样本
```

不要混。

---

# 七、举一个非常直观的例子

原始文件里有一句：

> “供应商应在项目所在地设立售后服务机构。”

这是：

> 文档中的一段文字。

但我们可以围绕它制造很多不同任务。

---

# 八、任务 A：风险分类

输入：

```text
供应商应在项目所在地设立售后服务机构。
```

输出：

```text
潜在风险
```

---

# 九、任务 B：风险类型识别

输入：

```text
供应商应在项目所在地设立售后服务机构。
```

输出：

```text
资格/商务条件中的地域性要求
```

---

# 十、任务 C：理由生成

输入：

> 条款 + 必要上下文

输出：

> 为什么这个条件需要审查。

---

# 十一、任务 D：修改建议

输入：

> 原条款

输出可能是：

> 将“必须设立本地机构”改为与实际履约需求相关的响应时限、服务能力等要求。

---

# 十二、任务 E：法规证据检索

输入：

> 风险条款

目标：

> 找到真正相关的法规、规章或规范性依据。

---

# 十三、注意发生了什么

完全同一句原始文字：

```text
供应商应在项目所在地设立售后服务机构。
```

可以产生：

```text
分类数据
抽取数据
推理数据
RAG检索数据
SFT数据
评测数据
```

所以：

\[
\boxed{
一份文件
\neq
一个任务
}
\]

也：

\[
\boxed{
一段文字
\neq
只有一种训练用途
}
\]

---

# 十四、第二个核心心智模型：Schema 是数据契约

Schema 这个词以后会反复出现。

先不要把它理解成复杂数据库术语。

最简单：

> **Schema 就是在正式规定：“一条样本必须有哪些字段，每个字段是什么意思。”**

---

# 十五、像身份证表格

如果没有固定 Schema：

有人记录：

```text
姓名：
出生日期：
```

有人记录：

```text
Name：
Age：
```

有人只记录：

```text
张三，男，北京
```

最后：

> 很难统一处理。

---

# 十六、政府采购数据也是一样

有人标：

```text
违法
```

有人标：

```text
不合理
```

有人标：

```text
有倾向性
```

有人标：

```text
高风险
```

有人写：

```text
建议核验
```

如果没有 Schema，

这五个人可能：

> 其实表达的是完全不同层次的事情。

---

# 十七、所以 Schema 的第一项作用

# 统一语言

它告诉所有人：

```text
risk_present
到底是什么意思？

risk_type
有哪些合法值？

risk_level
怎么定义？

needs_review
什么时候为true？

evidence
放什么？

reason
写到什么粒度？
```

---

# 十八、Schema 的第二项作用

# 让机器知道每个字段是什么

例如：

```json
{
  "risk_present": true,
  "risk_type": "supplier_qualification",
  "risk_level": "high"
}
```

模型训练、评测程序：

> 可以直接使用。

---

# 十九、Schema 的第三项作用

# 让不同团队能够协作

以后会有：

```text
数据工程师
采购专家
算法工程师
标注人员
评测人员
后端工程师
```

如果大家没有同一份 Schema，

项目很容易变成：

> 六个人心里有六套 ProcurementAI。

---

# 二十、所以 Schema 本质上是一个跨团队合同

可以这样理解：

```text
业务专家
   │
   ▼
定义业务含义
   │
   ▼
Schema
   │
   ├── 数据工程
   ├── 标注
   ├── SFT
   ├── RAG
   ├── Evaluation
   └── API
```

所有模块：

> 围绕同一套数据语言工作。

---

# 二十一、现在开始设计 ProcurementAI 的第一版 Task Schema

我们暂时不要贪大。

第一版继续围绕第三课确定的：

# 政府采购文件合规风险审查

五个主要风险域：

```text
A 供应商资格

B 技术参数

C 商务要求

D 评分标准

E 采购需求
```

---

# 二十二、首先要决定：最小业务单元是什么？

这是整个阶段最关键的问题之一。

我们可以选择：

```text
整份文件
一章
一节
一条
一句
一个短语
```

哪一个最好？

答案：

> 没有永远正确的粒度。

要看任务。

---

# 二十三、整份文件做一条样本有什么问题？

比如：

```text
200页招标文件
```

对应：

```text
风险 = 有
```

这几乎没什么学习价值。

模型会问：

> 到底哪儿有？

---

# 二十四、就像医学诊断数据

如果一份 500 页病历只标：

```text
有问题
```

机器也很难学。

真正有价值的是：

```text
具体异常在哪里
是什么异常
依据是什么
```

---

# 二十五、所以第一版 ProcurementAI 更适合采用

# Clause-level

也就是：

> **条款级样本**

作为非常重要的基础单位。

---

# 二十六、例如

原文：

```text
供应商须在本市注册并连续经营满5年。
```

作为一个：

```text
clause_text
```

然后给它：

```text
risk_present
risk_type
risk_level
reason
```

---

# 二十七、但是只保留一句条款又会产生另一个问题

上下文可能丢失。

例如：

> “应在两小时内到达现场。”

单独看：

> 不知道谁到现场。

---

# 二十八、如果加上下文

```text
项目类型：
核心生产系统7×24小时维护服务

条款：
故障发生后，供应商技术人员应在2小时内到达项目现场。
```

这时意义就不同。

---

# 二十九、所以第三个重要心智模型出现了

\[
\boxed{
最小判断单元
\neq
最小文本片段
}
\]

判断对象可以是：

> 一条条款。

但判断它可能需要：

> 更大的 Context。

---

# 三十、这就产生一个很重要的数据结构

```text
Target Clause
+
Surrounding Context
+
Document Metadata
```

也就是：

```text
我们判断谁
+
判断时需要看什么
+
它来自哪里
```

---

# 三十一、用法官类比

法官真正要判断的是：

> 某一个争议点。

但法官不能只看：

> 争议句子。

还需要：

- 合同背景；
- 当事人身份；
- 相关条款；
- 证据。

LLM 也一样。

---

# 三十二、所以一个好样本最好保留“层级关系”

例如：

```text
项目
 └── 招标文件
      └── 第三章 采购需求
           └── 3.2 售后服务
                └── 条款17
```

我们不要只留下：

```text
条款17
```

而把它来自哪里全部扔掉。

---

# 三十三、这叫 Document Hierarchy

也就是：

> 文档层级。

以后解析 PDF 时，这个东西非常重要。

---

# 三十四、一个 ProcurementAI 样本可以拥有这样的来源信息

```text
project_id
document_id
section_path
clause_id
```

例如：

```text
project_id:
P2026_00152

document_id:
P2026_00152_BID_01

section_path:
第三章/采购需求/售后服务

clause_id:
CLAUSE_00317
```

---

# 三十五、为什么 `project_id` 特别重要？

因为以后：

# Train / Test Split

不能简单按行随机切。

---

# 三十六、假设一个项目有 300 条样本

你随机切：

```text
240条 → Train
30条 → Validation
30条 → Test
```

看起来很标准。

实际上可能：

> 数据严重泄漏。

---

# 三十七、为什么？

因为同一个项目里的条款：

> 大量模板、语言、背景、公司名称都一样。

模型训练时已经看过：

> 项目的大部分信息。

考试时只是在看：

> 同项目另外几条。

分数会虚高。

---

# 三十八、所以我们从 Schema 第一阶段就必须保留

```text
project_id
```

否则第 6、第 7 阶段要防泄漏时：

> 已经来不及。

---

# 三十九、这就是 Schema 的一个深层价值

Schema 不只是：

> “方便存 JSON。”

它会决定你未来：

- 能不能正确切数据；
- 能不能追溯来源；
- 能不能去重；
- 能不能复现；
- 能不能审计。

---

# 四十、现在把一个样本分成 5 个区域

这是今天最重要的一张图之一：

```text
┌───────────────────────────────┐
│ ① Identity / Source           │
│    它是谁、来自哪里            │
├───────────────────────────────┤
│ ② Input                       │
│    模型真正看到什么            │
├───────────────────────────────┤
│ ③ Target / Label              │
│    我们希望模型学什么          │
├───────────────────────────────┤
│ ④ Evidence / Rationale        │
│    为什么这样判断              │
├───────────────────────────────┤
│ ⑤ Quality / Governance        │
│    谁标的、版本、是否复核等     │
└───────────────────────────────┘
```

我们一个个拆。

---

# 四十一、第一层：Identity / Source

核心字段可以有：

```text
sample_id
project_id
document_id
clause_id
source_type
section_path
```

---

# 四十二、`sample_id`

这是一条样本：

> 永久的身份证。

例如：

```text
PROC-RISK-000001
```

---

# 四十三、为什么不能只用行号？

因为今天：

```text
第328行
```

明天数据重新排序：

> 就不是第328行了。

所以：

> 样本需要稳定 ID。

---

# 四十四、`project_id`

告诉我们：

> 属于哪个采购项目。

这对：

- 去重；
- Split；
- 追踪；

都特别重要。

---

# 四十五、`document_id`

一个项目可能有很多文档：

```text
采购公告
招标文件
更正公告
采购结果
合同
```

不能全部混成：

> “项目文件”。

---

# 四十六、`source_type`

可以明确：

```text
tender_document
procurement_notice
requirement_document
scoring_rules
contract
regulation
case
```

不同数据源：

> 可靠性和用途可能不同。

---

# 四十七、第二层：Input

这是模型训练时：

> 真正看到的东西。

第一版可能包括：

```text
clause_text
context_before
context_after
project_context
section_path
```

---

# 四十八、最重要的字段当然是

# `clause_text`

也就是：

> 我们当前审查的目标条款。

---

# 四十九、为什么还要有 `context_before` 和 `context_after`？

因为很多采购条件：

> 单句无法正确解释。

例如：

```text
不得低于500万元。
```

单独看：

> 完全不知道什么不得低于。

---

# 五十、完整一点可能是

```text
项目预算：
3000万元

前文：
本项目需要持续提供核心系统运维服务。

目标条款：
供应商注册资本不得低于500万元。
```

判断能力：

> 完全不同。

---

# 五十一、但是 Context 是不是越多越好？

不是。

如果每条样本都塞：

> 200 页全文，

你又回到了：

> “整本文件当数据”。

---

# 五十二、所以 Context 设计本质上是在做

# Information Boundary

我们要问：

> **专家判断这一条，最低需要看到什么信息？**

这句话特别重要。

---

# 五十三、第三层：Target / Label

这是：

> 模型应该学习什么。

对风险识别 Baseline，

可能包括：

```text
risk_present
risk_type
risk_level
needs_review
```

---

# 五十四、`risk_present`

最简单：

```text
true
false
```

但是马上就遇到一个问题。

---

# 五十五、有些情况根本不能简单 true / false

例如：

> “供应商须保证 2 小时内现场响应。”

到底有没有风险？

必须看：

- 项目性质；
- 是否确需现场服务；
- 是否变相要求本地机构；
- 是否允许其它履约方式。

---

# 五十六、所以如果强迫专家只能标

```text
true
false
```

专家可能：

> 被迫瞎猜。

这会制造：

# Label Noise

---

# 五十七、因此我们很可能需要第三种状态

```text
needs_review
```

或者更直接：

```text
uncertain
```

---

# 五十八、这是一个非常重要的数据原则

> **现实世界有不确定性，Schema 不要逼专家假装确定。**

否则模型以后会学会：

> 任何问题都强行给肯定答案。

这正是我们不希望 ProcurementAI 产生的行为。

---

# 五十九、比如第一版可以把判断结果设计成

```text
no_risk
potential_risk
needs_review
```

而不是粗暴：

```text
0 / 1
```

具体最终枚举：

> 后面标注阶段再正式定。

---

# 六十、`risk_type`

风险类型不能随意写中文。

否则有人写：

```text
地域限制
```

有人写：

```text
本地化要求
```

有人写：

```text
供应商资格歧视
```

机器会认为：

> 三种标签。

---

# 六十一、所以我们要建立 Controlled Vocabulary

也就是：

> 受控标签集合。

例如第一层：

```text
supplier_qualification
technical_specification
commercial_requirement
scoring_rule
procurement_requirement
```

---

# 六十二、未来还可以有第二层

例如：

```text
supplier_qualification
    ├── geographic_restriction
    ├── unreasonable_scale_requirement
    ├── unnecessary_license
    └── performance_requirement
```

形成：

# Label Taxonomy

---

# 六十三、先不要把 Taxonomy 做成 300 类

这是很常见的坑。

第一版如果标签太细：

> 专家自己都标不一致。

机器更学不好。

---

# 六十四、好的第一版标签体系应该

```text
数量适中
定义清楚
边界明确
专家能一致使用
```

然后：

> 再逐步细化。

---

# 六十五、`risk_level`

例如：

```text
low
medium
high
```

看起来简单。

但如果没有定义：

> 完全没有意义。

---

# 六十六、什么叫 High？

必须有规则。

例如可能考虑：

```text
法律明确禁止程度
竞争影响程度
投诉风险
对供应商参与影响
是否直接构成资格门槛
```

这些以后：

> 必须写进标注指南。

---

# 六十七、否则专家 A 的 Medium

可能就是：

> 专家 B 的 High。

这叫：

# Annotation Inconsistency

后面第 9 阶段会专门处理。

---

# 六十八、第四层：Evidence / Rationale

这是 ProcurementAI 特别重要的一层。

不仅要知道：

> 结论是什么。

还要知道：

> 为什么。

---

# 六十九、第一种字段

# `rationale`

专家理由。

比如：

> 该条件将企业注册地直接作为参与资格要求，而履约能力未必与注册地存在必然关系，因此需要审查其必要性和合理性。

---

# 七十、第二种字段

# `evidence`

支持结论的：

- 法律；
- 行政法规；
- 部门规章；
- 规范性文件；
- 官方案例；
- 项目事实。

---

# 七十一、注意 Reason 和 Evidence 不是一个东西

Reason：

> 专家怎么推理。

Evidence：

> 推理依据什么事实或规范。

可以记成：

```text
Evidence
=
“根据什么”

Rationale
=
“为什么从这些依据得到这个判断”
```

---

# 七十二、举例

Evidence：

```text
某相关政府采购公平竞争要求
```

Rationale：

> 采购条件如果与合同履行没有必要联系，却限制外地供应商参与，可能产生不合理差别待遇。

两个：

> 不是同一个字段。

---

# 七十三、为什么要分开？

因为未来 RAG 主要负责：

# Evidence

SFT 很大一部分负责：

# Rationale / Working Style

这和我们整个系统架构直接对应。

---

# 七十四、这就是数据 Schema 和模型架构开始连接

```text
evidence
        ↓
未来RAG

rationale
        ↓
未来SFT

risk_type
        ↓
分类评测

suggestion
        ↓
生成任务
```

所以：

> Schema 设计会影响未来所有技术路线。

---

# 七十五、第五层：Quality / Governance

很多数据集会忽略这一层。

其实对我们的项目：

> 特别重要。

可能包括：

```text
label_status
annotator_id
reviewer_id
adjudication_status
quality_flag
schema_version
created_at
```

---

# 七十六、为什么记录 `label_status`？

因为一条样本可能处于：

```text
machine_generated
human_labeled
expert_reviewed
adjudicated
gold
```

这些：

> 质量完全不同。

---

# 七十七、千万不能把它们都叫

```text
training_data
```

否则以后根本不知道：

> 哪些是真的专家 Gold，哪些只是模型自己生成的。

---

# 七十八、我们可以建立一个数据质量阶梯

```text
L0
Raw

↓

L1
Parsed

↓

L2
Machine Labeled

↓

L3
Human Labeled

↓

L4
Expert Reviewed

↓

L5
Adjudicated Gold
```

这只是一个初版心智模型。

非常有用。

---

# 七十九、为什么 `annotator_id` 不应该随便写人名？

因为数据工程通常只需要：

> 可追踪标注来源。

可以使用：

```text
annotator_017
```

而不是把：

> 不必要的个人信息

塞进训练数据。

这是一个基本的数据治理习惯。

---

# 八十、`schema_version`

非常重要。

今天我们设计：

```text
Schema V0.1
```

半年后可能：

```text
V0.3
```

字段变了。

---

# 八十一、如果没有 Schema Version

你最后可能出现：

```text
10000条
用旧标签

20000条
用新标签

5000条
不知道是什么版本
```

这会非常痛苦。

---

# 八十二、所以每一条数据最好都知道

```text
它遵循哪一版Schema
```

例如：

```text
schema_version:
procurement_risk_v0.1
```

---

# 八十三、现在看第一版完整样本

先不考虑最终数据库格式。

只看思想：

```json
{
  "sample_id": "PROC-RISK-000001",
  "project_id": "PROJECT-00152",
  "document_id": "DOC-00152-01",
  "source_type": "tender_document",

  "section_path": "第一章/供应商资格条件",

  "clause_text": "供应商须在本市注册成立5年以上。",
  "context_before": "",
  "context_after": "",

  "risk_present": true,
  "risk_type": "supplier_qualification",
  "risk_subtype": "geographic_restriction",
  "risk_level": "high",
  "needs_review": false,

  "rationale": "将供应商注册地直接作为参与条件，需要审查其与履约需求的必要关联。",
  "evidence_ids": ["REG-XXXX"],

  "suggestion": "优先改为与实际履约能力直接相关的要求。",

  "label_status": "expert_reviewed",
  "schema_version": "procurement_risk_v0.1"
}
```

注意：

> 这是教学用 Schema 雏形，不是今天就永久冻结。

---

# 八十四、但这已经比一份 PDF 前进了巨大一步

PDF 只能告诉你：

> 有这些文字。

Schema Sample 告诉你：

```text
这是什么项目
它来自哪里
我们判断哪句话
上下文是什么
结论是什么
风险类型是什么
专家为什么这么判断
依据是什么
数据质量是什么
```

这才是真正的数据资产雏形。

---

# 八十五、第四个核心心智模型：一个 Raw Document 可以产生 N 个 Sample

假设：

> 一份招标文件。

我们切出：

```text
63条资格条件
148条技术要求
27条商务要求
42条评分项
85条采购需求
```

可能产生：

> 数百条任务样本。

---

# 八十六、但是不能简单说

```text
365条
=
365个完全独立样本
```

因为它们来自：

> 同一个项目。

---

# 八十七、所以必须保留 Group 信息

以后：

```text
Split by Project
```

而不是：

```text
Split by Row
```

这件事我们已经提前埋好了。

---

# 八十八、现在进入一个最危险的问题：Input 和 Label 泄漏

假设我们的输入是：

```text
专家审查意见：
该条款属于明显地域限制。

原条款：
供应商须在本市注册。
```

目标：

```text
地域限制
```

---

# 八十九、模型考试时会怎样？

几乎直接：

> 抄答案。

因为 Input 里面已经有：

```text
属于明显地域限制
```

---

# 九十、最终得到非常高的 Accuracy

团队很开心：

```text
98.9%
```

但模型其实：

> 根本没学会判断。

它只学会：

> 找答案词。

这就是：

# Label Leakage

---

# 九十一、所以 Schema 设计阶段必须问

> **哪些字段训练时允许给模型看到？**

以及：

> **哪些字段只能用于监督答案，不能出现在 Input？**

---

# 九十二、我们可以把字段明确分成

```text
INPUT_FIELDS
```

与：

```text
TARGET_FIELDS
```

---

# 九十三、例如

Input：

```text
clause_text
project_context
section_path
```

Target：

```text
risk_present
risk_type
rationale
```

Evaluation Metadata：

```text
project_id
document_id
annotator_id
schema_version
```

这三类：

> 不要混。

---

# 九十四、尤其 `project_id`

模型通常：

> 没必要把内部 project_id 当语言输入。

但 Dataset Pipeline：

> 必须保留。

---

# 九十五、这叫“模型需要什么”和“数据系统需要什么”分开

数据集字段可以很多。

但真正喂给模型的：

> 只是其中一部分。

---

# 九十六、举个很实用的图

```text
Dataset Row
│
├── Model Input
│   ├── clause_text
│   └── context
│
├── Training Target
│   ├── risk_type
│   ├── risk_level
│   └── rationale
│
└── Pipeline Metadata
    ├── project_id
    ├── source
    ├── split_group
    └── version
```

这张图特别值得记。

---

# 九十七、第五个核心心智模型：一份数据集不应该服务所有任务

一个常见思路：

> “做一个超级 JSON，把所有东西全部塞进去，所有模型都用它。”

可以有：

> 统一底层 Master Dataset。

但不同任务最终应该：

> 生成不同 Dataset View。

---

# 九十八、例如 Master Record

可能拥有：

```text
clause
risk
evidence
reason
suggestion
metadata
```

---

# 九十九、任务 T1：Risk Classification

最终训练 View：

```text
Input:
clause + context

Target:
risk_present + risk_type
```

---

# 一百、任务 T2：Rationale SFT

```text
Input:
clause + context + evidence

Target:
expert rationale
```

---

# 一百零一、任务 T3：Modification Suggestion

```text
Input:
clause + confirmed risk

Target:
suggestion
```

---

# 一百零二、任务 T4：Evidence Retrieval

```text
Query:
clause + risk question

Positive:
relevant regulation chunk
```

再加：

> Hard Negative Evidence。

---

# 一百零三、所以推荐架构是

```text
               Master Dataset
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
 Classification    SFT View      RAG View
       │             │             │
       ▼             ▼             ▼
  分类训练        行为训练        检索训练
```

而不是：

> 三套完全不相关的数据体系。

---

# 一百零四、这叫 Single Source of Truth

我们希望底层真实事实：

> 只有一个权威源。

不同训练任务：

> 从它派生。

---

# 一百零五、否则会发生非常讨厌的问题

分类数据说：

```text
Sample 17 = 高风险
```

SFT 数据说：

```text
Sample 17 = 无风险
```

RAG 数据又说：

> 另一个结论。

最后：

> 自己的数据互相打架。

---

# 一百零六、所以 Data Lineage 从第一天就重要

Lineage：

> 血缘。

就是：

> 这条训练数据究竟从哪里来的？

例如：

```text
Raw PDF
 ↓
Page 37
 ↓
Clause 12
 ↓
Parsed Record
 ↓
Expert Annotation
 ↓
SFT Example 00318
```

---

# 一百零七、未来如果发现原始 PDF 解析错了

我们可以沿血缘找到：

```text
哪些样本受影响？
```

而不是：

> 全库猜。

---

# 一百零八、现在再看“样本粒度”

政府采购项目很适合：

# Hierarchical Samples

层级数据。

---

# 一百零九、可能至少有四层

```text
Project Level

Document Level

Section Level

Clause Level
```

---

# 一百一十、为什么要保留 Project Level？

例如：

```text
项目类型
预算
采购方式
所属地区
发布时间
```

这些背景：

> 有时会影响判断。

---

# 一百一十一、为什么 Document Level 重要？

同一个项目：

> 招标文件

和：

> 结果公告

完全不是一种语境。

---

# 一百一十二、为什么 Section Level 重要？

一句：

```text
不得低于500万元
```

在：

> 供应商资格

和：

> 项目预算

语义完全不同。

所以：

```text
section_path
```

本身就是很有价值的上下文。

---

# 一百一十三、为什么 Clause Level 是核心？

因为风险最终往往需要定位到：

> 具体条款。

这对：

- 标注；
- 模型训练；
- 用户展示；
- 风险报告；

都非常方便。

---

# 一百一十四、所以我们未来的数据不是“扁平文本库”

而更像：

```text
Project
  │
  └── Document
        │
        └── Section
              │
              └── Clause
                    │
                    └── Annotation
```

这张结构图特别重要。

---

# 一百一十五、现在讨论 Positive 和 Negative Sample

如果只收：

> 有风险的条款，

模型会发生什么？

---

# 一百一十六、它可能学会

> “看到采购条款就报风险。”

Recall：

> 非常漂亮。

Precision：

> 惨不忍睹。

---

# 一百一十七、所以必须同时有

```text
Positive
有风险

Negative
没有风险
```

而且后面还要专门做：

# Hard Negative

---

# 一百一十八、普通 Negative

例如：

> “供应商应具有独立承担民事责任的能力。”

可能比较容易。

---

# 一百一十九、Hard Negative

例如：

> “项目所在地为本市，供应商应保证 2 小时内现场响应，但不限制服务机构设立方式。”

它包含：

```text
本市
2小时
现场
```

看起来：

> 很像地域限制。

但实际上：

> 需要结合履约必要性判断，不能机械地因为出现“本市”就判违规。

这种样本：

> 特别值钱。

---

# 一百二十、为什么 Hard Negative 极其重要？

它防止模型学习：

# Shortcut

例如：

```text
出现“本市”
→ 风险
```

这是假的规律。

---

# 一百二十一、我们真正希望模型学习

```text
是否限制供应商身份/资格？

是否与履约必要性相关？

有没有合理替代实现？

是否产生不合理差别待遇？
```

这才是：

> 深层规则。

---

# 一百二十二、所以 Schema 要为 Hard Case 留空间

例如：

```text
difficulty:
easy / medium / hard
```

或者：

```text
case_type:
standard / boundary / hard_negative
```

这样以后：

> 可以单独做 Slice Evaluation。

---

# 一百二十三、什么叫 Slice？

Slice：

> 数据切片。

例如单独看：

```text
地域限制类
技术参数类
Hard Negative
长文本
评分标准
```

模型总体 90 分，

可能在：

```text
Hard Negative
```

只有：

> 52 分。

如果只看平均分：

> 完全看不到。

---

# 一百二十四、所以 Metadata 不是废字段

好的 Metadata：

> 是以后诊断模型的手术刀。

---

# 一百二十五、但 Metadata 也不能无限堆

第一版不要出现：

```text
200个字段
```

然后：

> 80% 永远没人用。

---

# 一百二十六、设计字段时问三个问题

```text
这个字段未来会用于：

训练？
评测？
治理？
```

三者都不是：

> 暂时不要加。

---

# 一百二十七、Schema 设计的原则之一

# Minimal but Sufficient

中文：

> **尽量简单，但足够支撑任务。**

---

# 一百二十八、现在建立第一版字段地图

可以先分成：

| 区域 | 典型字段 |
|---|---|
| Identity | sample_id, project_id, document_id |
| Structure | section_path, clause_id |
| Input | clause_text, context |
| Label | risk_present, risk_type, risk_level |
| Reasoning | rationale |
| Evidence | evidence_ids |
| Action | suggestion |
| Quality | label_status, needs_review |
| Governance | schema_version, source_type |
| Analysis | difficulty, case_type |

这已经足够支撑：

> 第一版系统设计。

---

# 一百二十九、现在看一个“不好的 Schema”

```json
{
  "text": "供应商须在本市注册。",
  "answer": "不合理。"
}
```

看起来很简单。

问题在哪里？

---

# 一百三十、问题一

不知道：

> 来自哪个项目。

无法：

> 防泄漏。

---

# 一百三十一、问题二

不知道：

> 属于哪个章节。

上下文丢失。

---

# 一百三十二、问题三

“不合理”到底是什么类型？

无法做：

> Category Evaluation。

---

# 一百三十三、问题四

没有：

> Evidence。

以后无法检验：

> 法律依据。

---

# 一百三十四、问题五

不知道：

> 谁标的。

也不知道：

> 有没有专家复核。

---

# 一百三十五、问题六

无法区分：

```text
确定风险
```

和：

```text
需要进一步核验
```

---

# 一百三十六、所以“两字段数据集”虽然简单

但可能把以后大量能力：

> 永久切掉。

---

# 一百三十七、反过来也不能过度设计

例如第一天就要求专家填写：

```text
46个标签
17种置信度
13层法规关系
8个推理阶段
```

专家会：

> 标到怀疑人生。

标注一致性：

> 反而下降。

---

# 一百三十八、所以 Schema 不是一次设计完美

正确方式是：

```text
V0.1
↓
小规模试标
↓
发现问题
↓
V0.2
↓
再试
↓
稳定
↓
V1.0
```

这叫：

# Schema Iteration

---

# 一百三十九、为什么先做 Pilot Annotation？

Pilot：

> 小规模试标。

例如先找：

```text
50～200条
```

真实条款。

让 2～3 位专家：

> 按 V0.1 Schema 标。

---

# 一百四十、然后看什么？

看：

```text
哪些字段大家总理解不一样？

哪些字段几乎没用？

哪些业务状态Schema根本表达不了？

哪些标签总冲突？

哪些上下文不够？
```

这比坐办公室：

> 凭想象设计三个月 Schema

靠谱得多。

---

# 一百四十一、Schema 是通过真实数据“撞”出来的

这句话非常值得记。

你真正拿 100 条采购条款去标，

很快就会发现：

> 现实永远比设计表复杂。

---

# 一百四十二、一个很典型的现实问题

你可能设计：

```text
risk_level:
low
medium
high
```

然后专家问：

> “这个条款本身看不出，需要结合项目性质怎么办？”

这时你才发现：

> 缺少 `needs_review`。

---

# 一百四十三、另一个现实问题

你设计：

```text
risk_type:
qualification
technical
commercial
```

专家说：

> “这个评分条件同时涉及技术参数倾向性和评分标准。”

于是你要决定：

```text
单标签？
```

还是：

```text
多标签？
```

---

# 一百四十四、这就是 Schema Design 真正困难的地方

不是：

> JSON 会不会写。

而是：

> **真实业务世界到底应该怎么被离散化。**

---

# 一百四十五、单标签还是多标签？

例如一条：

> “特定品牌产品得 10 分，其它品牌得 0 分。”

它可能同时涉及：

```text
技术参数倾向性
+
评分标准不合理
```

---

# 一百四十六、如果 Schema 强迫只能选一个

会丢失信息。

但如果允许：

```text
无限多标签
```

标注和评测又变复杂。

---

# 一百四十七、第一版可以考虑

```text
primary_risk_type
```

加：

```text
secondary_risk_types
```

例如：

```text
primary:
scoring_rule

secondary:
technical_specification
```

这是一个不错的折中思路。

---

# 一百四十八、但今天不把字段最终冻结

第四课第 8、9 阶段：

> 会结合标注体系进一步定型。

今天的目标是：

> 建立设计框架。

---

# 一百四十九、什么字段绝对不要让模型偷看？

比如：

```text
expert_final_decision
```

如果它在 Input：

> 泄漏。

---

# 一百五十、什么字段应该留在 Metadata？

例如：

```text
project_id
document_id
split_group
annotation_status
```

模型不必看。

Pipeline：

> 必须看。

---

# 一百五十一、什么字段可以同时用于 Input 和展示？

例如：

```text
section_path
```

有时模型看到章节名称：

> 有助于判断。

产品展示也：

> 可以告诉用户风险在哪里。

---

# 一百五十二、所以字段还可以进一步标记用途

例如：

```text
use_for_training_input: true
use_for_training_target: false
use_for_evaluation: true
use_for_traceability: true
```

实际实现不一定这样写。

但设计思想很重要。

---

# 一百五十三、现在第一次定义“数据单元”

我们的第一版可以这样想：

\[
\boxed{
DataUnit
=
TargetClause
+
MinimalNecessaryContext
+
SourceIdentity
+
ExpertAnnotation
}
\]

这几乎是本阶段唯一值得保留的“公式”。

---

# 一百五十四、翻译成人话

一条好数据需要：

> **我要判断的那句话**

加：

> **为了判断它必须知道的上下文**

加：

> **它究竟来自哪里**

加：

> **专家到底怎么判断**

---

# 一百五十五、这个结构以后会贯穿整个 ProcurementAI

因为：

```text
Clause
```

支撑：

> 风险定位。

```text
Context
```

支撑：

> 合理判断。

```text
Source
```

支撑：

> 追溯与数据隔离。

```text
Annotation
```

支撑：

> 训练与评测。

---

# 一百五十六、现在看三个案例

### Case A：明显风险

```text
供应商必须是在本市依法注册的企业。
```

可能：

```text
risk_present:
true

risk_type:
supplier_qualification

subtype:
geographic_restriction
```

---

# 一百五十七、Case B：明显普通条件

```text
供应商应具有履行合同所必需的设备和专业技术能力。
```

可能：

```text
risk_present:
false
```

---

# 一百五十八、Case C：边界案例

```text
供应商应确保故障发生后2小时内到达项目现场。
```

单独：

> 不应该机械判断。

可能：

```text
needs_review:
true
```

并要求 Context：

```text
项目性质
服务场景
履约方式
```

---

# 一百五十九、这三个案例一起放进数据集才有价值

模型需要同时学习：

```text
明显有风险

明显没风险

不能武断判断
```

这就是专业模型与关键词分类器之间的区别。

---

# 一百六十、一个非常危险的数据集是什么样？

全是：

```text
“必须本地注册”
→ 风险

“必须本地公司”
→ 风险

“必须本市分支”
→ 风险
```

模型很快就学会：

```text
本地 / 本市
=
风险
```

---

# 一百六十一、然后遇到

> “项目所在地为本市，供应商应保证2小时现场响应，但不限制服务机构设立方式。”

它也判：

> 地域歧视。

这就是：

# Shortcut Learning

---

# 一百六十二、所以从 Schema 阶段就要给未来留出

```text
case_type
difficulty
context_required
```

等诊断字段的可能性。

---

# 一百六十三、以后 Hard Negative 可以专门筛出来

例如：

```text
case_type = hard_negative
```

然后单独计算：

```text
Hard Negative Accuracy
```

这才是真正专业的 Benchmark。

---

# 一百六十四、现在谈“法规数据”和“采购文件数据”要不要放一张表

可以统一管理。

但不要假设：

> 它们是同一种 Sample。

---

# 一百六十五、法规文本更像 Knowledge Corpus

例如：

```text
法律
行政法规
部门规章
规范性文件
```

主要服务：

> RAG / CPT / Evidence。

---

# 一百六十六、采购文件 + 专家判断

更像：

# Task Data

服务：

> SFT / Classification / Evaluation。

---

# 一百六十七、监管案例

介于两者之间。

既包含：

> 知识。

又包含：

> 专家判断模式。

非常有价值。

---

# 一百六十八、所以长期 Master Data 可以有不同 Entity

```text
Regulation
Project
Document
Clause
Case
Annotation
EvidenceLink
```

以后可以形成：

> 关系化的数据资产。

---

# 一百六十九、但是第一版不要先建“宇宙数据库”

我们现在先把：

# Clause + Annotation

做好。

这是最重要的基础。

---

# 一百七十、这一阶段真正的工程产物是什么？

不是一段代码。

而是三样东西：

```text
1. Task Definition

2. Sample Schema

3. Label Dictionary Draft
```

---

# 一百七十一、Task Definition 可以写成

```text
Task Name:
Procurement Clause Risk Review

Input:
目标采购条款 + 必要上下文

Output:
风险存在性
风险类型
风险等级/需核验状态
理由

Primary Use:
Baseline Evaluation / SFT Dataset
```

---

# 一百七十二、Sample Schema Draft

第一版可以是：

```text
sample_id

project_id
document_id
source_type

section_path
clause_id

clause_text
context_before
context_after
project_context

risk_present
risk_type
risk_subtype
risk_level
needs_review

rationale
evidence_ids
suggestion

difficulty
case_type

label_status
schema_version
```

---

# 一百七十三、其中有些字段第一版可以为空

重要的是：

> Schema 知道它们是什么。

不是每条：

> 所有字段必须填满。

---

# 一百七十四、字段应该区分

```text
Required
```

和：

```text
Optional
```

---

# 一百七十五、例如第一版 Mandatory

可能是：

```text
sample_id
project_id
document_id
clause_text
risk_present
label_status
schema_version
```

---

# 一百七十六、Optional

可能：

```text
risk_subtype
evidence_ids
suggestion
difficulty
```

具体后面：

> 再随 Pilot 调整。

---

# 一百七十七、为什么 Mandatory 不能太多？

因为标注成本会爆炸。

每多一个必填字段：

> 都是在向专家收时间。

---

# 一百七十八、专家时间是整个项目最贵的资源之一

所以 Schema 设计还要问：

> **这个字段值不值得专家花 30 秒？**

这非常现实。

---

# 一百七十九、如果一个字段每条多花 30 秒

10 万条数据：

```text
100000 × 30秒
```

就是：

> 833 小时以上。

一个看似不起眼的字段：

> 可能增加几个月标注成本。

---

# 一百八十、所以 Schema 设计本身也是成本设计

这点很多算法工程师容易忽略。

---

# 一百八十一、能机器自动产生的字段

尽量不要让专家手填。

例如：

```text
sample_id
document_id
section_path
source_url
created_at
```

应该：

> Pipeline 自动生成。

---

# 一百八十二、专家真正应该花时间的地方

是：

```text
风险判断
风险类型
推理理由
边界判断
证据确认
```

这才值得专业人的时间。

---

# 一百八十三、这叫 Human-in-the-Loop Optimization

人：

> 做人最擅长的判断。

机器：

> 做机器擅长的机械工作。

---

# 一百八十四、所以好的数据系统不是“让专家多填表”

而是：

> **让专家只处理真正需要专业判断的字段。**

---

# 一百八十五、再回到我们整个项目

第三课最后问的是：

> 哪个模型适合我们？

第四课第一阶段现在问的是：

> **我们到底准备拿什么东西公平地训练和测试这些模型？**

两课之间已经接起来了。

---

# 一百八十六、没有 Schema 会发生什么？

你会有：

```text
很多PDF
很多Excel
很多人工笔记
很多Word审查意见
很多模型生成文本
```

但它们：

> 互相不能稳定连接。

---

# 一百八十七、有 Schema 以后

它们可以开始进入：

```text
统一的数据流水线
```

---

# 一百八十八、最终我们希望得到

```text
Raw Documents
      ↓
Parser
      ↓
Structured Documents
      ↓
Clause Units
      ↓
Task Schema
      ↓
Expert Annotation
      ↓
Master Dataset
      ↓
Train / Val / Gold
      ↓
SFT / RAG / Evaluation
```

这就是第四课后面所有阶段的总骨架。

---

# 一百八十九、本阶段最容易犯的 10 个错误

### 错误 1

> 下载了 PDF 就等于有训练数据。

错。

### 错误 2

> 一份文件就是一条 Sample。

通常错。

### 错误 3

> 条款切得越短越好。

错。

需要保留必要 Context。

### 错误 4

> Schema 只是数据库工程师的事情。

错。

它定义的是模型到底学习什么。

### 错误 5

> 所有情况强制二分类。

危险。

现实存在 `needs_review`。

### 错误 6

> Label 想怎么写就怎么写。

错。

需要 Controlled Vocabulary。

### 错误 7

> 专家理由和法规证据是一回事。

不是。

### 错误 8

> Metadata 模型不用看，所以可以不要。

错。

它对数据治理和评测极其重要。

### 错误 9

> Schema 字段越多越专业。

错。

### 错误 10

> Schema 一次设计完以后永远不改。

错。

真实 Schema 应该通过 Pilot 迭代。

---

# 一百九十、本阶段最重要的三个“≠”

```text
Raw Document
≠
Training Sample
```

```text
Target Clause
≠
Complete Context
```

```text
More Fields
≠
Better Schema
```

---

# 一百九十一、再加一个非常重要的“=”

\[
\boxed{
GoodSchema
=
ClearMeaning
+
Traceability
+
Trainability
+
Evaluability
}
\]

翻译成中文：

> 一份好的 Schema，要让数据**含义清楚、来源可追、能用于训练、也能公平评测**。

---

# 一百九十二、本阶段掌握测试

如果现在不看前文，你能自己回答下面这些问题，这一阶段就真正掌握了：

> 为什么一份 PDF 不等于一条训练样本？

> Raw Document、Data Unit、Training Sample 有什么区别？

> 为什么必须先定义任务，再开始大量收数据？

> Schema 到底是什么？

> 为什么 Clause-level 很适合采购风险审查？

> 为什么 Clause 很重要，但单独 Clause 又可能不够？

> Target Clause 和 Context 为什么必须分开？

> 为什么要保留 project_id？

> project_id 和模型 Input 为什么又不是一回事？

> 为什么随机按行切 Train/Test 会产生风险？

> Input Field、Target Field、Metadata Field 有什么区别？

> 什么是 Label Leakage？

> risk_present 为什么未必只有 true / false？

> `needs_review` 为什么对专业系统特别重要？

> risk_type 为什么必须使用受控标签体系？

> Reason 和 Evidence 为什么不是同一个字段？

> 为什么 Evidence 更接近 RAG，而 Rationale 更接近 SFT？

> 为什么 label_status 要区分机器标注、人工标注和专家 Gold？

> 为什么 Schema 必须版本化？

> 为什么一份采购文件可以派生多个训练任务？

> Master Dataset 和 Task-specific Dataset View 是什么关系？

> 什么是 Data Lineage？

> 为什么 Positive 和 Negative 必须同时存在？

> Hard Negative 为什么特别重要？

> 为什么“本市”不能直接等价于“违法”？

> 为什么 Metadata 对 Slice Evaluation 很重要？

> 为什么字段不能无限增加？

> 为什么 Schema 应该先经过 Pilot Annotation？

> 专家应该把时间花在哪些字段上？

如果这些都能自己讲清楚：

\[
\boxed{
第四课第1阶段真正掌握
}
\]

---

# 一百九十三、本阶段最终只记一句话

> **政府采购数据工程的第一步不是下载更多文件，而是先明确“一条数据究竟代表什么”：用 Schema 把目标条款、必要上下文、来源身份、专家标签、证据理由和质量状态组织成一个可追溯、可训练、可评测的数据单元。**

最后压成一张图：

```text
                  真实采购业务
                       │
                       ▼
                  Task Definition
                       │
                       ▼
                     Schema
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
   Source ID          Input           Target
 project/doc      clause/context   risk/label
       │               │                │
       └───────────────┼────────────────┘
                       ▼
               Evidence / Rationale
                       │
                       ▼
                Quality Metadata
                       │
                       ▼
                  Master Sample
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      SFT View      RAG View     Eval View
```

---

# 下一阶段：第四课 · 第 2 阶段
## PDF、HTML、DOCX 到底怎样变成“可信文本”？为什么 `extract_text()` 成功，并不代表文档解析成功？

下一阶段我们会真正碰第一批原始采购文件。

但重点不是：

> “调用一个 PDF 库把文字抽出来。”

而是第一次建立这张脑图：

```text
文件看起来正确
        ≠
机器解析出来正确
```

我们会拆：

```text
PDF到底是不是“文字文件”？

文字型PDF和扫描PDF有什么区别？

为什么两栏排版会把阅读顺序抽乱？

页眉页脚为什么会污染训练数据？

表格为什么特别难？

为什么一个金额“300万元”
可能被解析成：
“300”
和
“万元”
跑到两个不同位置？

为什么 OCR 应该是必要时使用的后备方案，
而不是所有PDF第一步就OCR？
```

并最终把：

```text
Raw Procurement Documents
```

第一次推进到：

```text
ParsedDocument_V0.1
```

也就是第四课真正开始进入数据工程流水线。

---

<!-- LESSON 04 STAGE 01 END -->


<!-- LESSON 04 STAGE 02 START -->

# 第四课 · 第 2 阶段：PDF、HTML、DOCX 到底怎样变成“可信文本”？
## 为什么 `extract_text()` 成功，并不代表文档解析成功？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **文件里“看得见文字” ≠ 文件里真的存着可直接读取的文字**
2. **Extract Text ≠ Parse Document**
3. **文档解析真正要恢复的是： 文字 + 阅读顺序 + 结构 + 表格 + 来源位置**
4. **OCR 是扫描页的后备方案， 不是所有PDF默认第一步**
5. **原始文档解析时不要过早丢失： 页码、位置、区块类型、来源信息**
6. **解析质量不是看“程序有没有报错”， 而是看“下游业务判断会不会被解析错误带偏”**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `OCR` | OCR：把扫描图像中的文字转换成机器可读文本 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Layout` | 版面结构：文字块、表格、列、坐标和阅读顺序信息 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Sample` | 样本：具有明确输入、目标和来源的一条训练/评测记录 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `OOD` | 分布外数据：明显偏离训练/验证分布的新输入 |
| `Raw Document` | 原始文档：未经结构化处理的采购文件源材料 |
| `Tokenizer` | 分词器：文本与 Token ID 之间的编码/解码组件 |
| `Data Unit` | 数据单元：从原始文件切出的可追踪业务片段 |
| `Embedding` | 嵌入：把离散 Token 映射到连续高维向量 |

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

上一阶段，我们先做了一件看起来“不像数据工程”，实际上最重要的事情：

> **先定义一条数据究竟是什么。**

我们已经建立了这条主线：

```text
Raw Document
      ↓
Data Unit
      ↓
Task Schema
      ↓
Training / Evaluation Sample
```

现在终于可以真正碰：

# 原始采购文件

但这一阶段有一个特别容易踩的坑。

很多人第一次做 PDF 处理时，会写：

```python
text = extract_text("招标文件.pdf")
```

然后程序成功返回了一大段中文。

于是宣布：

> “PDF 解析完成。”

实际上：

> **很可能只是“拿到了一些字符”，距离“拿到可信文档”还差得很远。**

今天这一阶段真正解决的问题只有一个：

> **机器怎样把 PDF、HTML、DOCX 还原成一个足够可信、足够可追溯、能够继续切条款的数据结构？**

---

# 一、本阶段先建立 6 个核心心智模型

先把这六句话钉住：

```text
① 文件里“看得见文字”
   ≠
   文件里真的存着可直接读取的文字

② Extract Text
   ≠
   Parse Document

③ 文档解析真正要恢复的是：
   文字 + 阅读顺序 + 结构 + 表格 + 来源位置

④ OCR 是扫描页的后备方案，
   不是所有PDF默认第一步

⑤ 原始文档解析时不要过早丢失：
   页码、位置、区块类型、来源信息

⑥ 解析质量不是看“程序有没有报错”，
   而是看“下游业务判断会不会被解析错误带偏”
```

整个第 2 阶段，基本都围绕这六句话展开。

---

# 二、先看最简单的误区

假设人眼看到一页采购文件：

```text
第三章 采购需求

3.1 供应商资格条件

1. 供应商应具有独立承担民事责任的能力。
2. 供应商注册资本不得低于500万元。
3. 供应商应在本市设立固定服务机构。

第 37 页
```

人类非常自然地理解：

```text
标题
↓
小节标题
↓
条款1
↓
条款2
↓
条款3
↓
页脚
```

但 PDF 内部：

> **不一定按照这个顺序存。**

---

# 三、PDF 本质上是什么？

初学时非常容易把 PDF 想成：

> 一个“只读版 Word”。

其实这不准确。

PDF 更接近：

> **一套告诉渲染器“页面上的东西应该画在哪里”的固定版式描述。**

它首先关心的是：

```text
这里画一个字
那里画一条线
这里放一张图
那里放一个文本块
```

而不是：

```text
这是一级标题
这是第二段
这是表格第三行第二列
这是资格条件
```

---

# 四、这就是 PDF 和 DOCX 的根本区别之一

DOCX 更偏：

> **文档结构。**

PDF 更偏：

> **页面最终长什么样。**

可以先这么理解：

```text
DOCX
更像“文章的结构说明”

PDF
更像“最终打印出来的页面”
```

---

# 五、所以 PDF 最擅长什么？

保持：

- 字体；
- 页面；
- 位置；
- 打印效果；
- 跨设备视觉一致性。

也正因为这样：

> 它并不天然适合机器恢复语义结构。

---

# 六、第一个核心心智模型

\[
\boxed{
VisualLayout
\neq
SemanticStructure
}
\]

人眼看到：

> “这是标题。”

PDF 可能只知道：

> “这一行字号 18、粗体、坐标在页面顶部。”

---

# 七、先把 PDF 分成三类

政府采购文件里，我们至少会碰到：

```text
① 文字型PDF

② 扫描型PDF

③ 混合型PDF
```

这三种必须分清。

---

# 八、第一类：文字型 PDF

比如：

> Word 导出 PDF。

页面看起来是文字。

内部通常也存在：

> Text Layer。

你可以：

- 鼠标选择文字；
- 搜索关键字；
- 复制粘贴。

这种 PDF：

> 通常优先做原生文字提取。

---

# 九、第二类：扫描型 PDF

来源可能是：

```text
纸质文件
↓
扫描仪
↓
PDF
```

这时候整页对机器来说可能只是：

# Image

也就是：

> 一张照片。

---

# 十、你人眼看到的是

```text
供应商应……
```

但 PDF 内部可能只有：

```text
一张 2480 × 3508 像素图片
```

没有字符：

```text
供
应
商
```

这个概念。

---

# 十一、这时普通 `extract_text()` 会怎样？

可能：

```text
返回空字符串
```

或者：

```text
几乎没有文字
```

---

# 十二、这种情况才真正需要 OCR

OCR：

# Optical Character Recognition

光学字符识别。

它做的是：

```text
Pixel
↓
识别字形
↓
Character
↓
Text
```

---

# 十三、第三类：混合型 PDF

这其实很常见。

例如：

```text
第1～20页
正常电子文本

第21页
扫描盖章文件

第22～40页
正常文本

附件
又是扫描件
```

所以：

> **不能只给整个 PDF 打一个“可提取/不可提取”的标签。**

更合理的是：

# Page-level Detection

按页判断。

---

# 十四、一个 100 页 PDF 可能长这样

```text
Page 1   Native Text
Page 2   Native Text
Page 3   Native Text
...
Page 38  Scan
Page 39  Scan
Page 40  Native Text
...
Page 95  Native Text
Page 96  Scan
```

所以：

> OCR 策略应该可以精确到页。

---

# 十五、为什么我特别强调“不要所有 PDF 都 OCR”？

因为很多人会觉得：

> “OCR 什么都能认，那我把所有页面先转图片再 OCR，不就统一了吗？”

听起来很省事。

实际通常不是最佳方案。

---

# 十六、如果 PDF 本来就有高质量文字层

原生提取可以直接拿到：

```text
政府采购法
```

OCR 却需要：

```text
图片
↓
识别
↓
猜这是哪几个字
```

无端增加了一次：

> 识别错误机会。

---

# 十七、尤其政府采购文件里有很多敏感字符

比如：

```text
500万元
```

OCR 如果变成：

```text
S00万元
```

问题就非常大。

---

# 十八、再比如

原文：

```text
≤3%
```

OCR：

```text
< 8%
```

对于普通文章：

> 也许只是一个错字。

对于：

> 评分标准

可能直接改变业务含义。

---

# 十九、再比如型号

```text
ZX-1080
```

可能被识别成：

```text
ZX-I080
```

---

# 二十、再比如法律条款

```text
第三十一条
```

变成：

```text
第三十—条
```

RAG 检索：

> 可能就被影响。

---

# 二十一、所以 OCR 最重要的心智模型是

\[
\boxed{
OCR
=
必要时把像素恢复成文字
}
\]

而不是：

\[
\boxed{
OCR
=
所有文档解析第一步
}
\]

---

# 二十二、这就是今天的第一个决策树

```text
拿到PDF
   │
   ▼
页面是否有可信文字层？
   │
   ├── 是
   │    ↓
   │  Native Text Extraction
   │
   └── 否
        ↓
       OCR
```

混合 PDF：

> 每页单独判断。

---

# 二十三、但注意

即使：

```text
Native Text Extraction
```

成功，

仍然不能说：

> 文档解析完成。

为什么？

因为第二个大问题来了：

# Reading Order

---

# 二十四、阅读顺序是什么？

人类看文件时会自动知道：

```text
先读标题
再读正文
从左到右
从上到下
```

但复杂 PDF：

> 阅读顺序可能被打乱。

---

# 二十五、例如一页两栏

人眼看到：

```text
左栏                    右栏

1. 条件A               4. 条件D
2. 条件B               5. 条件E
3. 条件C               6. 条件F
```

正确顺序应该是：

```text
A
B
C
D
E
F
```

---

# 二十六、某些简单提取器可能得到

```text
A
D
B
E
C
F
```

为什么？

因为它可能按：

> 页面对象内部顺序

而不是：

> 人类阅读顺序。

---

# 二十七、于是文字都“提取成功”了

一个字都没丢。

但语义：

> 已经乱了。

这就是：

\[
\boxed{
CharacterCorrect
\neq
DocumentCorrect
}
\]

---

# 二十八、这对采购数据有多危险？

原本：

```text
1. 供应商资格条件：
供应商须具有……
```

解析后变成：

```text
1. 供应商资格条件：
评分标准：
价格得分……
```

然后资格要求：

> 跑到别处。

---

# 二十九、以后条款切分会怎样？

模型会把：

> 评分内容

误认为：

> 资格条件。

所以解析错误：

> 会一路传到训练数据。

---

# 三十、这就是数据工程中的一个重要概念

# Upstream Error Propagation

上游一个小错误：

```text
阅读顺序错
```

会向下游传播成：

```text
章节错
↓
条款错
↓
标签错
↓
训练样本错
↓
模型学错
```

---

# 三十一、所以 Parsing 绝对不是“辅助小工具”

它决定：

> 你后面数据集到底是不是在描述真实文档。

---

# 三十二、第三个大问题：页眉页脚

采购文件经常每页都有：

```text
某某政府采购中心
项目编号：XXXX
第 37 页 / 共 128 页
```

这些视觉上：

> 很自然。

人类几乎自动忽略。

---

# 三十三、机器不会自动忽略

提取 128 页以后：

```text
项目编号：XXXX
项目编号：XXXX
项目编号：XXXX
……
```

可能出现：

> 128 次。

---

# 三十四、这会产生什么问题？

首先：

> 重复污染。

---

# 三十五、其次 Token 浪费

模型每次读长文档：

> 都反复读无用页眉页脚。

---

# 三十六、再次，切分污染

原本：

```text
条款A
```

跨页。

中间突然变成：

```text
条款A前半部分

第37页
某某采购中心
项目编号XXX

条款A后半部分
```

后续切条款：

> 会被干扰。

---

# 三十七、还有一个更隐蔽的问题

模型可能把：

> 页眉里的项目名称

错误拼进：

> 正文句子。

---

# 三十八、所以“去页眉页脚”不是简单删除第一页和最后一页

而是：

> **识别页面中重复出现、位置稳定、语义上属于版式装饰的区域。**

---

# 三十九、一个好的方法通常会利用

```text
多个页面之间
重复文本
+
相似位置
```

例如：

```text
页面顶部 30px～60px
连续80页出现相同字符串
```

很可能：

> Header。

---

# 四十、同理 Footer

```text
页面底部
+
连续出现
+
页码变化
```

可能：

> Footer。

---

# 四十一、但是不能机械删除“页面顶部所有文字”

因为第一页顶部可能就是：

# 项目名称

甚至：

# 采购公告标题

删掉：

> 数据也坏了。

---

# 四十二、所以这里再次体现

# Rules + Context

不能只：

> 写死坐标。

---

# 四十三、第四个大问题：换行

PDF 经常是按视觉行存储。

例如人眼看到：

> 供应商不得以不合理条件对其他供应商实行差别待遇或者歧视待遇。

提取以后可能变成：

```text
供应商不得以不合理条件对其他供
应商实行差别待遇或者歧视待遇。
```

---

# 四十四、这里的换行是语义换行吗？

不是。

只是：

> 页面宽度到了。

---

# 四十五、如果我们直接把每行当句子

就会出现：

```text
“供应商不得以不合理条件对其他供”
```

和：

```text
“应商实行差别待遇或者歧视待遇。”
```

两个假样本。

---

# 四十六、所以要区分

```text
Visual Line Break
```

和：

```text
Semantic Paragraph Break
```

这两个不是一回事。

---

# 四十七、相反，有时真正的段落边界

可能没有空行。

比如：

```text
1. 资格要求……
2. 本项目不接受联合体……
3. 投标人不得……
```

机器必须识别：

> 编号变化本身就是结构信号。

---

# 四十八、所以正确的解析不是

```text
每出现换行
→ 新段落
```

而是综合：

```text
位置
缩进
字号
编号
标点
行距
文本内容
```

去判断。

---

# 四十九、第五个问题：连字符与断词

英文文档里特别明显。

例如：

```text
govern-
ment
```

其实是：

```text
government
```

中文里也可能出现：

> 字符被版面拆开。

---

# 五十、如果后续 Embedding / RAG 直接使用错误断词

会影响：

- Tokenizer；
- 搜索；
- 去重；
- 语义匹配。

---

# 五十一、第六个问题：字体编码

有些 PDF 人眼显示完全正常。

但内部并不是标准：

```text
Unicode Text
```

可能用了：

> 特殊字符映射。

---

# 五十二、于是复制出来可能是

```text

```

甚至乱码。

---

# 五十三、人眼为什么还能看到中文？

因为 PDF 里面可能告诉渲染器：

> “这个字符代码，用这个字体画成某个字形。”

但未必保存了：

> 正确 Unicode 对应关系。

---

# 五十四、这种页面看起来是“文字 PDF”

却可能：

> 无法可靠提取文字。

这类页面有时也需要：

> 转为图像后识别

或者使用更适合该 PDF 的解析工具。

---

# 五十五、所以判断“文字型 PDF”不能只靠

> 能不能鼠标框选。

最好还检查：

```text
提取出的Unicode是否合理
```

---

# 五十六、第七个问题：隐藏文字层

扫描 PDF 有时已经做过 OCR。

于是页面里同时有：

```text
视觉图像
+
不可见Text Layer
```

---

# 五十七、好消息

搜索：

> 可以工作。

---

# 五十八、坏消息

这个隐藏 OCR 层：

> 可能质量很差。

于是：

> `extract_text()` 有结果，

但结果不是可信文本。

---

# 五十九、所以不要只判断

```text
text_length > 0
```

然后就说：

> Native Text 很好。

还要做：

# Text Quality Check

---

# 六十、可以检查哪些简单信号？

例如：

```text
可打印字符比例
中文字符比例
乱码比例
异常符号比例
重复字符比例
单字间异常空格
```

---

# 六十一、例如正常中文：

```text
供应商应具有良好的商业信誉
```

异常 OCR/编码：

```text
供 应 商 应 具 有 良 好 的 商 业 信 誉
```

如果每个字之间：

> 都多一个空格，

后续 Tokenizer：

> 可能完全不同。

---

# 六十二、再例如

```text
供应商须……
```

被识别成：

```text
供应商须……□□□□□□
```

这是一个明显：

> 质量警报。

---

# 六十三、于是 PDF 页可以有一个状态

例如：

```text
native_text_good

native_text_suspicious

image_only

mixed
```

这样 Pipeline：

> 再选择处理路线。

---

# 六十四、现在进入最麻烦的对象之一

# Table

政府采购文件里：

> 表格特别多。

比如评分标准。

---

# 六十五、人眼看到

| 评分因素 | 分值 | 评分标准 |
|---|---:|---|
| 技术方案 | 20 | 根据方案完整性评分 |
| 项目经验 | 10 | 每提供一个案例得2分 |
| 价格 | 30 | 按价格公式计算 |

人类一下就懂：

> 三列，三行。

---

# 六十六、但 PDF 内部可能没有“Table”这个概念

它可能只是：

```text
画几条横线
画几条竖线
把文字摆在对应坐标
```

---

# 六十七、一个简单 Text Extractor 可能输出

```text
评分因素
20
技术方案
项目经验
10
价格
30
根据方案完整性评分
每提供一个案例得2分
按价格公式计算
```

文字全部都在。

结构：

> 完全丢了。

---

# 六十八、对评分标准审查来说

这几乎等于：

> 数据损坏。

因为：

```text
“20”
```

到底对应：

- 技术方案？
- 价格？
- 项目经验？

已经不知道。

---

# 六十九、所以表格解析的目标不是

> 把所有 Cell 文字拿出来。

而是恢复：

\[
\boxed{
Row \times Column Relationship
}
\]

---

# 七十、也就是

```text
这个内容
属于哪一行
属于哪一列
```

---

# 七十一、表格还有更难的情况

# Merged Cell

例如：

| 一级指标 | 二级指标 | 分值 |
|---|---|---:|
| 技术 | 方案 | 10 |
| 技术 | 人员 | 10 |

视觉上：

> “技术”可能纵向合并。

---

# 七十二、解析时如果处理不好

可能：

```text
第一行有“技术”
第二行一级指标为空
```

后续你必须知道：

> 空白不是缺失数据。

而是：

> 继承合并单元格。

---

# 七十三、还有跨页表格

第 1 页：

```text
表格头
行1
行2
行3
```

第 2 页：

```text
表格头
行4
行5
```

机器需要判断：

> 这是同一张表延续，

还是：

> 新表。

---

# 七十四、还有表格嵌套

单元格里面：

- 多段文字；
- 编号；
- 子条款；
- 换行。

所以：

> 表格是独立的文档解析问题。

---

# 七十五、对于政府采购项目

尤其需要重点保护：

```text
资格审查表
技术参数表
评分标准表
报价表
合同条款表
```

因为这些通常：

> 业务价值非常高。

---

# 七十六、所以我们以后不能只有

```text
plain_text
```

最好还要保留：

# Block Type

---

# 七十七、例如一个解析后的 Block 可以是

```text
title

paragraph

list_item

table

table_cell

header

footer

image

caption
```

---

# 七十八、为什么保留类型很有用？

以后第三阶段做：

# Document Structure Recovery

时我们可以更容易知道：

> 哪些是标题、正文、表格、条款。

---

# 七十九、如果第一步全部 flatten

变成：

```text
一条巨大字符串
```

结构就已经：

> 提前丢掉了。

后面想恢复：

> 非常困难。

---

# 八十、这是本阶段一个非常重要的原则

\[
\boxed{
不要在解析早期做不可逆的信息丢失
}
\]

---

# 八十一、比如页面坐标要不要保留？

建议：

> 在原始 Parsed Layer 保留。

例如：

```json
{
  "text": "供应商资格条件",
  "page": 12,
  "bbox": [72, 110, 320, 145]
}
```

---

# 八十二、`bbox` 是什么？

Bounding Box。

也就是：

> 这个文本块在页面上的位置框。

可以粗略理解为：

```text
左边
上边
右边
下边
```

---

# 八十三、为什么位置以后有用？

比如：

> 连续 100 页都在页面顶部同一位置出现“项目编号”。

很可能：

> Header。

---

# 八十四、再比如

两个文本块：

> 横向并排。

可能：

> 两栏排版。

---

# 八十五、再比如表格

多个 Block：

> 坐标规律排列。

有助于：

> 恢复行列。

---

# 八十六、所以 Position 不是无意义的版式垃圾

它是：

> 恢复结构的证据。

---

# 八十七、但是最后训练模型时要不要把 bbox 喂进去？

通常文本模型：

> 不一定需要。

注意这两层：

```text
Data Engineering需要位置
≠
LLM Training必须看位置
```

---

# 八十八、再次印证上一阶段

数据系统字段：

> 可以比模型输入字段多很多。

---

# 八十九、现在看 HTML

很多政府采购公告来自：

> 网页。

HTML 相比 PDF：

> 通常更容易恢复结构。

因为它本身可能有：

```html
<h1>
<p>
<table>
<li>
```

这样的 DOM 结构。

---

# 九十、于是 HTML 理论上可以直接知道

```text
标题
段落
列表
表格
链接
```

比 PDF：

> 结构信息丰富得多。

---

# 九十一、但 HTML 也不是无脑简单

网页里还可能有：

```text
导航栏
广告
网站页脚
分享按钮
登录入口
相关推荐
版权信息
面包屑导航
```

这些：

> 不是采购正文。

---

# 九十二、例如你抓下来一篇公告

真正正文：

```text
3000字
```

网站模板：

```text
5000字
```

如果全部训练：

> 大部分 Token 都是垃圾。

---

# 九十三、所以 HTML 解析需要

# Main Content Extraction

也就是：

> 找到真正正文 DOM 区域。

---

# 九十四、HTML 还有一个问题

有些页面内容：

> JavaScript 动态加载。

下载最初 HTML：

> 可能根本没有正文。

浏览器运行 JS 后：

> 才出现。

---

# 九十五、所以“浏览器能看到”

并不一定意味着：

```text
HTTP GET到的HTML
```

里面直接有。

---

# 九十六、还有隐藏文本

网页里可能：

```text
display:none
```

或者：

> 无障碍辅助文本。

机器抓下来：

> 可能看到了用户根本没看到的内容。

---

# 九十七、所以 HTML 也要回答

```text
什么是正文？
什么是模板？
什么是隐藏内容？
什么是脚本生成内容？
```

---

# 九十八、但是 HTML 最大优势依然明显

如果网站语义标签规范：

> 它可以比 PDF 更好地保存结构。

所以同一公告如果同时有：

```text
HTML正文
+
PDF附件
```

不一定：

> PDF 永远优先。

---

# 九十九、这引出 Source Priority

对于每类文档，

我们以后可能制定：

> 哪种源最可信。

---

# 一百、例如某些项目

公告正文：

> HTML 更干净。

正式招标文件：

> PDF / DOCX 才完整。

所以：

> 不能一刀切。

---

# 一百零一、现在看 DOCX

DOCX 看起来像一个文件。

实际上它本质上：

> 是一组压缩后的 XML 等资源。

---

# 一百零二、它通常保存很多真正的结构

例如：

```text
Paragraph
Style
Table
Header
Footer
Numbering
```

所以比 PDF：

> 更容易解析语义结构。

---

# 一百零三、例如标题可能有 Style

```text
Heading 1
Heading 2
Normal
```

如果原作者规范使用样式，

我们几乎可以直接恢复：

```text
章
节
正文
```

---

# 一百零四、但现实中的采购 Word 文件有多规范？

经常：

> 不太规范。

有人不用 Heading Style。

只是：

```text
字体变大
加粗
居中
```

来假装标题。

---

# 一百零五、这时 DOCX 虽然有结构

但结构信息：

> 并不完全可信。

---

# 一百零六、DOCX 还有文本框

例如一个重要说明放在：

> Text Box。

某些简单解析库：

> 可能根本读不到。

---

# 一百零七、还有 Header / Footer

和 PDF 一样：

> 可能污染正文。

---

# 一百零八、还有表格

DOCX 的表格结构通常比 PDF：

> 更容易提取。

因为内部确实存在：

```text
row
cell
```

概念。

---

# 一百零九、但它也有合并单元格

以及：

- 嵌套表格；
- 文本框；
- 图片；
- 批注；
- 修订痕迹。

所以：

> 仍然需要明确解析策略。

---

# 一百一十、还有一个政府文件很常见的问题

# Track Changes

修订模式。

文档里可能同时包含：

```text
删除前文字
+
修改后文字
```

---

# 一百一十一、人眼可能看到

> 最终版本。

解析程序却可能：

> 把删除内容也抽出来。

于是出现：

```text
旧条款
新条款
```

同时进入 Dataset。

---

# 一百一十二、这会制造非常隐蔽的数据污染

尤其：

> 更正文件、修改稿、征求意见稿。

所以：

# Document Version

以后也很重要。

---

# 一百一十三、现在把 PDF、HTML、DOCX 放一张表

| 格式 | 最大优势 | 主要风险 |
|---|---|---|
| PDF | 页面视觉稳定 | 语义结构弱、阅读顺序、扫描、表格 |
| HTML | DOM 结构丰富 | 网站模板、动态加载、隐藏内容 |
| DOCX | 段落/样式/表格结构较好 | 样式不规范、文本框、修订、复杂对象 |

没有哪个格式：

> 永远最好。

---

# 一百一十四、因此真正专业的 Pipeline

不是：

```text
所有文件
↓
一个extract_text()
```

而是：

```text
识别文件类型
↓
选择对应Parser
↓
进行质量检查
↓
统一转换为内部数据模型
```

---

# 一百一十五、这叫 Adapter 思维

外部格式可能很多：

```text
PDF
HTML
DOCX
TXT
```

但内部统一变成：

# ParsedDocument

---

# 一百一十六、这特别重要

因为后续：

- 清洗；
- 结构恢复；
- 条款切分；
- 去重；

不应该每一步都重新判断：

> 这是 PDF 还是 DOCX。

---

# 一百一十七、我们希望形成

```text
PDF Parser ───┐
              │
HTML Parser ──┼──→ ParsedDocument
              │
DOCX Parser ──┘
```

然后后面：

> 统一处理。

---

# 一百一十八、现在第一次设计 `ParsedDocument_V0.1`

先不要追求完美。

一个文档可以有：

```text
document_id
source_file
file_type
file_hash
parser_version
pages
warnings
```

---

# 一百一十九、为什么 `file_hash` 很重要？

例如：

# SHA-256

可以把一个文件内容：

> 算成固定指纹。

---

# 一百二十、同一个 PDF 被重命名

```text
招标文件.pdf
```

变成：

```text
最终版招标文件.pdf
```

文件名不同。

如果内容一样：

> Hash 一样。

---

# 一百二十一、以后去重时特别有价值

你可以先快速发现：

# Exact Duplicate

完全重复文件。

---

# 一百二十二、为什么 `parser_version` 很重要？

今天：

```text
parser_v0.1
```

半年后改进阅读顺序：

```text
parser_v0.3
```

同一个 PDF：

> 解析结果可能不同。

---

# 一百二十三、如果不记录 Parser Version

未来看到一条异常数据：

> 根本不知道当初用哪套规则解析的。

---

# 一百二十四、这又回到了

# Reproducibility

数据工程同样需要复现。

---

# 一百二十五、Page 应该有哪些东西？

可以先想成：

```text
page_number
width
height
page_type
blocks
warnings
```

---

# 一百二十六、`page_type`

比如：

```text
native_text
scan
mixed
```

---

# 一百二十七、Block 可以是什么？

例如：

```json
{
  "block_id": "B00031",
  "type": "paragraph",
  "text": "供应商应具有……",
  "bbox": [72, 154, 510, 208],
  "reading_order": 7,
  "extraction_method": "native",
  "confidence": 0.99
}
```

---

# 一百二十八、这里最重要的不是 JSON 写法

而是我们没有把信息压成：

```text
一个巨大字符串
```

---

# 一百二十九、`reading_order`

就是：

> 这个 Block 应该第几个读。

后续重新构建正文：

> 按它排序。

---

# 一百三十、`extraction_method`

告诉我们：

```text
native
ocr
table_parser
```

文本到底怎么来的。

---

# 一百三十一、为什么要记录它？

假设一个金额：

```text
5000万元
```

模型后面出现异常。

我们可以看到：

```text
extraction_method = OCR
confidence = low
```

马上知道：

> 可能是 OCR 错误。

---

# 一百三十二、这叫 Provenance

来源可追溯性。

我们不仅保存：

> “这句话是什么。”

还保存：

> “这句话是怎么来的。”

---

# 一百三十三、这对专业数据非常重要

因为数据错误最终要能够回答：

```text
原文件是什么？
第几页？
哪个坐标？
哪个Parser？
是否OCR？
什么版本？
```

---

# 一百三十四、以后专家如果说

> “这条训练样本原文是不是错了？”

我们不是：

> 到 2TB 文件夹里人工找。

而是直接：

```text
sample
↓
clause
↓
block
↓
page 37
↓
raw PDF
```

---

# 一百三十五、这就是 Data Lineage 的基础

第四课第一阶段刚讲过。

现在它开始真正落地。

---

# 一百三十六、ParsedDocument 可以形成这样的结构

```text
ParsedDocument
│
├── Metadata
│   ├── document_id
│   ├── source
│   ├── file_type
│   ├── file_hash
│   └── parser_version
│
├── Page 1
│   ├── Block 1
│   ├── Block 2
│   └── Table 1
│
├── Page 2
│   ├── Block 3
│   └── Block 4
│
└── Warnings
```

---

# 一百三十七、注意：这一阶段我们还没做真正的“条款识别”

现在只做到：

> 页面内容可信恢复。

下一阶段才会做：

```text
Block
↓
Heading
↓
Section
↓
Clause
```

不要把阶段混在一起。

---

# 一百三十八、这是一个很重要的数据工程习惯

# Separate Concerns

把不同问题拆开。

---

# 一百三十九、第一层问题

> 我到底有没有把文档内容正确拿出来？

这是：

# Parsing

---

# 一百四十、第二层问题

> 哪些 Block 属于同一个章节？

这是：

# Structure Recovery

---

# 一百四十一、第三层问题

> 哪一段是一条采购条件？

这是：

# Clause Segmentation

---

# 一百四十二、第四层问题

> 这条条件有没有风险？

这是：

# Annotation / Modeling

---

# 一百四十三、如果四层一次全部做

出错以后：

> 很难定位。

---

# 一百四十四、比如模型说错了

可能是：

```text
模型不会判断
```

也可能其实是：

```text
PDF漏了一行
```

甚至：

```text
表格列错位
```

如果 Pipeline 不分层：

> 你会把数据错误误判成模型错误。

---

# 一百四十五、这就是一个非常重要的工程原则

\[
\boxed{
先证明输入正确
再讨论模型为什么错
}
\]

---

# 一百四十六、现在说 Parser Confidence

很多系统喜欢给：

```text
0.97
```

一个数字。

但要谨慎。

---

# 一百四十七、这个 0.97 到底代表什么？

可能：

- OCR 字符置信度；
- Layout 模型置信度；
- Table 检测置信度。

它们：

> 不是同一个概念。

---

# 一百四十八、所以不要把所有东西混成一个

```text
confidence = 0.92
```

然后觉得：

> 文档 92% 正确。

---

# 一百四十九、更好的做法

分别记录：

```text
text_quality
ocr_confidence
layout_confidence
table_warning
```

至少：

> 含义明确。

---

# 一百五十、尤其业务关键字段要额外验证

比如：

```text
预算金额
百分比
日期
项目编号
法律条号
评分分值
品牌型号
```

这些字段：

> 一个字符错了，业务意义可能完全变。

---

# 一百五十一、我们可以把它们叫

# High-risk Tokens

不是机器学习里的风险 Token。

只是数据工程意义上：

> 特别需要保护的文本。

---

# 一百五十二、比如

原文：

```text
不得超过10%
```

解析：

```text
不得超过70%
```

只错一个字符。

业务含义：

> 天差地别。

---

# 一百五十三、再比如

```text
500万元
```

变成：

```text
5000万元
```

一个 `0`。

模型可能得出：

> 完全不同的合规判断。

---

# 一百五十四、所以采购 Parsing Quality 不能只用

# Character Accuracy

还要看：

> 业务关键字段准确率。

---

# 一百五十五、我们可以以后做一个 Parsing Gold Set

人工选：

```text
50份
100份
```

典型采购文件。

---

# 一百五十六、覆盖

```text
文字PDF
扫描PDF
双栏
复杂表格
跨页表格
盖章扫描
DOCX
HTML
```

---

# 一百五十七、然后人工确认

这些文档的：

```text
正文
阅读顺序
表格
标题
关键数字
```

---

# 一百五十八、每次 Parser 更新

重新跑：

> Parsing Benchmark。

这样才知道：

```text
parser_v0.3
```

到底比：

```text
parser_v0.2
```

好没好。

---

# 一百五十九、不要靠“我随便看了两页，感觉不错”

这和模型评测一样。

Parser：

> 也要 Benchmark。

---

# 一百六十、现在看一个失败案例

原页面：

```text
评分标准

技术方案       20分
项目经验       10分
价格           30分
```

Parser 输出：

```text
评分标准
技术方案
项目经验
价格
20
10
30
```

---

# 一百六十一、从字符层面看

一个字都没丢。

如果计算：

> 文本召回率

可能 100%。

---

# 一百六十二、从业务层面看

它已经：

> 不可信。

因为行列关系丢了。

---

# 一百六十三、所以第六个核心心智模型

\[
\boxed{
ParsingQuality
必须由下游任务定义
}
\]

---

# 一百六十四、对普通文章摘要

可能：

> 表格稍微乱一点也能接受。

---

# 一百六十五、对评分标准审查

表格错一列：

> 不可接受。

---

# 一百六十六、所以不同文档区域还可能有不同质量门槛

比如：

```text
正文段落
容忍少量版式差异

评分表
要求高结构准确率

金额/分值
要求极高字符准确率
```

---

# 一百六十七、这就是 Risk-based Data Engineering

把质量控制资源：

> 花在最可能影响业务判断的地方。

---

# 一百六十八、现在谈扫描页 OCR 后最容易出现的错误类型

可以大致分：

```text
字符错误
空格错误
换行错误
阅读顺序错误
表格结构错误
漏字
多字
```

---

# 一百六十九、字符错误

例如：

```text
0 ↔ O

1 ↔ I

5 ↔ S
```

中文也会出现：

> 形近字。

---

# 一百七十、空格错误

```text
供 应 商
```

或者：

```text
供应商须具 有
```

---

# 一百七十一、换行错误

一条完整条款：

> 被拆成好几段。

---

# 一百七十二、阅读顺序错误

两栏：

> 左右交叉。

---

# 一百七十三、表格错误

单元格：

> 顺序打乱。

---

# 一百七十四、漏字

原文：

```text
不得低于500万元
```

OCR：

```text
低于500万元
```

注意：

> “不得”被漏掉。

意思：

> 几乎反转。

---

# 一百七十五、这类错误特别危险

因为它不是：

> 随便少了一个形容词。

而是：

# Negation Error

否定词错误。

---

# 一百七十六、所以业务关键词也需要重点关注

例如：

```text
不得
不应
必须
应当
可以
不得超过
不得低于
不少于
不高于
```

这些：

> 对规则意义非常重要。

---

# 一百七十七、以后可以设计规则检查

如果 OCR 页面里：

> 否定词附近置信度很低，

可以：

> 标记人工复核。

---

# 一百七十八、这比“整页重新人工检查”

更经济。

---

# 一百七十九、所以 Parser 可以输出 Warning

比如：

```text
LOW_OCR_CONFIDENCE

TABLE_STRUCTURE_UNCERTAIN

READING_ORDER_AMBIGUOUS

ENCODING_SUSPECT

HEADER_FOOTER_UNCERTAIN
```

---

# 一百八十、为什么 Warning 不应该直接丢？

因为后面生成 Dataset 时：

> 可以根据质量筛选。

---

# 一百八十一、例如 Gold Set

可能只允许：

```text
parse_quality = verified
```

的样本进入。

---

# 一百八十二、而 CPT 语料

可能允许：

> 稍低一些的格式质量。

不同用途：

> 数据质量门槛可以不同。

---

# 一百八十三、这再次说明

# Dataset Purpose Matters

同一份 Parsed Data：

> 可以派生不同质量要求的数据集。

---

# 一百八十四、现在设计一次完整的文档解析流水线

先看总图：

```text
Raw File
   │
   ▼
File Validation
   │
   ▼
Type Detection
   │
   ├── PDF
   ├── HTML
   └── DOCX
   │
   ▼
Parser Adapter
   │
   ▼
Page / Block Extraction
   │
   ▼
Native Text Quality Check
   │
   ├── Good → 保留
   │
   └── Bad/Image → OCR
   │
   ▼
Layout / Reading Order
   │
   ▼
Table Recovery
   │
   ▼
Header / Footer Marking
   │
   ▼
Quality Validation
   │
   ▼
ParsedDocument_V0.1
```

注意：

> 这里只是概念流程。

实际不同格式：

> 某些步骤顺序会不同。

---

# 一百八十五、第一步 File Validation

我们先确认：

```text
文件能不能打开？
是否损坏？
是否加密？
文件类型和扩展名一致吗？
```

---

# 一百八十六、为什么扩展名不能完全相信？

一个文件叫：

```text
abc.pdf
```

并不意味着：

> 内部一定是真 PDF。

有时下载接口甚至返回：

```text
HTML错误页面
```

但文件名：

> 仍然 `.pdf`。

---

# 一百八十七、所以最好检查

# MIME / File Signature

而不是：

> 只看后缀。

---

# 一百八十八、第二步 Hash

给原始文件生成：

> 内容指纹。

以后：

- 去重；
- 版本；
- 来源审计；

都能用。

---

# 一百八十九、第三步选择 Parser

```text
PDF
→ PDF Adapter

HTML
→ HTML Adapter

DOCX
→ DOCX Adapter
```

---

# 一百九十、第四步做内容恢复

不要急着清洗。

先尽量：

> 忠实保留。

---

# 一百九十一、为什么“清洗”不能太早？

假设你看到：

```text
第 37 页
```

马上删除。

后面才发现：

> 其实这是正文中的某个引用。

已经找不回来了。

---

# 一百九十二、所以推荐一个思想

# Extract First, Normalize Later

先保留：

> 原始解析层。

然后生成：

> 清洗层。

---

# 一百九十三、可以拥有两个版本

```text
Raw Parsed Blocks
```

和：

```text
Normalized Text
```

前者：

> 用于追溯。

后者：

> 用于下游任务。

---

# 一百九十四、千万不要只有最终清洗文本

否则一旦清洗错了：

> 无法诊断。

---

# 一百九十五、这像照片修图

应该保留：

```text
原片
```

然后产生：

```text
编辑版
```

而不是：

> 直接覆盖原片。

---

# 一百九十六、数据工程也一样

```text
Raw
↓
Parsed
↓
Normalized
↓
Structured
↓
Task Sample
```

每一层最好：

> 有清楚边界。

---

# 一百九十七、这就是 Data Layering

分层数据架构。

---

# 一百九十八、采购数据以后可以至少有

```text
L0 Raw File

L1 Parsed Document

L2 Clean Document

L3 Structured Clause

L4 Annotated Sample

L5 Train / Gold Dataset
```

---

# 一百九十九、每层解决不同问题

### L0

> 原文件到底是什么？

### L1

> 文件里有什么？

### L2

> 去掉明显版式噪声后是什么？

### L3

> 文档业务结构是什么？

### L4

> 专家怎么判断？

### L5

> 哪些数据真正用于模型？

---

# 二百、这样以后发现问题可以定位

例如：

```text
模型输出错误
```

一路回溯：

```text
Label对吗？
↓
Clause切对吗？
↓
Clean文本对吗？
↓
Parsed Block对吗？
↓
原PDF是什么？
```

---

# 二百零一、这就是专业的数据可追溯链

而不是：

> 一个 CSV 放 100 万行文本，没人知道从哪里来的。

---

# 二百零二、现在看一个采购 PDF 的完整例子

人眼页面：

```text
第三章 采购需求

3.2 售后服务

供应商须在项目所在地设立固定服务机构，
并保证故障发生后2小时内到达现场。

—— 第42页 ——
```

---

# 二百零三、一个差 Parser 可能输出

```text
第三章采购需求供应商须在项目
第42页
3.2售后服务所在地设立固定服务机构
并保证故障发生后2小时内到达现场
```

字基本都在。

但：

> 顺序坏了。

---

# 二百零四、一个较好的 Parsed Layer

可能是：

```text
Block 1
type=heading
text=第三章 采购需求

Block 2
type=heading
text=3.2 售后服务

Block 3
type=paragraph
text=供应商须在项目所在地设立固定服务机构，并保证故障发生后2小时内到达现场。

Block 4
type=footer
text=第42页
```

---

# 二百零五、下一阶段再进一步

```text
第三章 采购需求
   ↓
3.2 售后服务
   ↓
目标条款
```

这就开始产生：

# Clause Unit

---

# 二百零六、看出课程设计了吗？

第四课现在是：

```text
Stage 1
定义Sample

Stage 2
恢复可信文本

Stage 3
恢复业务结构

Stage 4
清洗和规范化

Stage 5
去重

Stage 6
切Train / Val / Test

Stage 7
防数据泄漏

Stage 8
Label Schema

Stage 9
专家标注与一致性

Stage 10
Hard Negative

Stage 11
Version / Lineage

Stage 12
ProcurementDataset_V0.1
```

是一条完整流水线。

---

# 二百零七、现在说一个非常重要的工程原则

# Never Trust a Successful Parse

程序返回：

```text
status = success
```

只能说明：

> 程序没有崩。

不能说明：

> 内容正确。

---

# 二百零八、比如

```text
extract_text()
```

返回 50,000 字。

从程序角度：

> 成功。

但如果：

- 两栏打乱；
- 表格全部 flatten；
- 数字错位；
- 页脚反复插入；

业务角度：

> 失败。

---

# 二百零九、所以我们需要

# Semantic Validation

至少抽样检查：

> 人眼看到的文档意义有没有保留下来。

---

# 二百一十、自动质量检查可以做什么？

例如：

```text
页面文字长度异常？

某页突然0字符？

乱码率异常？

重复页眉比例异常？

页号突然乱序？

表格数量异常？

OCR置信度异常？
```

---

# 二百一十一、这些可以形成

# Quality Flags

例如：

```text
EMPTY_PAGE
TEXT_TOO_SHORT
GARBLED_TEXT
POSSIBLE_SCAN
TABLE_DETECTED
OCR_LOW_CONFIDENCE
```

---

# 二百一十二、然后不是全部人工检查

而是：

> 优先检查 Warning 多的文档。

---

# 二百一十三、这就是自动化数据质检的价值

不是：

> 机器保证100%正确。

而是：

> 把有限的人力集中在高风险样本。

---

# 二百一十四、政府采购文件还有一个特殊问题

# Stamp / Seal

扫描件可能有：

> 红色公章

压住文字。

---

# 二百一十五、OCR 可能把公章字符混进正文

例如：

```text
某某市财政局
```

盖在正文上。

机器可能：

> 把它当句子的一部分。

---

# 二百一十六、还有手写签字

可能：

> 被 OCR 成奇怪文字。

---

# 二百一十七、所以图像页 OCR 之后

最好还保留：

> 页面图像引用 / 页码。

对于重要样本：

> 可以人工回看原页。

---

# 二百一十八、另一个特殊问题

# Redaction / Mask

有些文件可能：

> 用黑框遮住敏感信息。

视觉上看不到。

但底层文字层：

> 有时仍存在。

---

# 二百一十九、数据治理上不能假设

> “页面看不见，所以机器也拿不到。”

对于敏感信息：

> 必须做专门检查。

---

# 二百二十、这和模型训练有什么关系？

如果隐藏文字层里包含：

- 联系电话；
- 身份信息；
- 账号；
- 其它不应进入训练的数据；

解析器可能：

> 无意提取出来。

---

# 二百二十一、所以 Parsed Layer 之后还需要

# Privacy / Sensitive Data Filtering

这不是本阶段重点。

但必须知道：

> 后面有这一层。

---

# 二百二十二、再谈来源 URL

如果文档来自网站，

最好保留：

```text
source_url
download_time
```

为什么？

---

# 二百二十三、半年以后法规或公告页面变化

你至少知道：

> 当初从哪里拿的。

---

# 二百二十四、对于法律法规

还可能需要：

```text
发布日期
生效日期
失效日期
发布机关
```

这些以后：

> 对 RAG 非常重要。

---

# 二百二十五、但是不要在 Parser 里做所有事情

Parser 的职责先保持清楚：

> **忠实恢复内容和来源。**

法规有效性判断：

> 后面 Knowledge Engineering 再做。

---

# 二百二十六、这就是边界意识

一个模块职责越明确：

> 越容易测试。

---

# 二百二十七、现在给 `ParsedDocument_V0.1` 一个概念 Schema

```json
{
  "document_id": "DOC-00152-01",
  "file_type": "pdf",
  "file_hash": "sha256:...",
  "parser_version": "parser_v0.1",
  "source_url": "...",

  "pages": [
    {
      "page_number": 1,
      "page_type": "native_text",
      "blocks": [
        {
          "block_id": "B0001",
          "type": "heading",
          "text": "第三章 采购需求",
          "bbox": [72, 90, 400, 130],
          "reading_order": 1,
          "extraction_method": "native"
        }
      ],
      "warnings": []
    }
  ],

  "document_warnings": []
}
```

这是：

> 结构思想。

不是最终数据库实现。

---

# 二百二十八、为什么不直接保存

```json
{
  "text": "整本文件全部正文……"
}
```

因为你会失去：

- Page；
- Block；
- Position；
- Type；
- Provenance；
- Warning。

---

# 二百二十九、以后如果真的只需要全文

完全可以从 Block：

> 重新拼接。

---

# 二百三十、但反过来

如果一开始只保存全文：

> 无法可靠恢复 Block。

所以还是那个原则：

\[
\boxed{
早期保留信息
晚期按需简化
}
\]

---

# 二百三十一、一个很好用的数据工程习惯

# Lossless First

先尽量：

> 无损保留。

然后再建立：

# Task-specific View

---

# 二百三十二、第四课第 1 阶段已经讲过

```text
Master Dataset
↓
Classification View
SFT View
RAG View
```

现在 Parsed Data 也同理：

```text
Rich Parsed Document
↓
Plain Text View
Table View
Clause View
```

---

# 二百三十三、同一个 Rich Representation

可以支持：

> 多个下游任务。

这比不断重新解析原始文件：

> 更可靠。

---

# 二百三十四、现在说一个未来非常实用的问题

假设同一项目同时有：

```text
招标文件.docx
招标文件.pdf
```

应该选哪个？

---

# 二百三十五、不能机械说

> DOCX 永远优先。

但通常可以比较：

```text
内容完整性
结构质量
版本时间
是否最终发布版本
是否与官网正式附件一致
```

---

# 二百三十六、比如 DOCX 是工作稿

PDF 是：

> 正式发布版。

那正式内容：

> 应以 PDF 为准。

---

# 二百三十七、所以 Source Authority

来源权威性：

> 和 Parsing Quality 是两个维度。

---

# 二百三十八、一个来源解析得特别干净

但它是：

> 草稿。

另一个解析困难：

> 却是正式版。

不能因为 Parser 方便：

> 就选草稿当真相。

---

# 二百三十九、所以最终数据质量至少有两条轴

```text
Source Authority
```

和：

```text
Parse Quality
```

---

# 二百四十、可以想象四象限

```text
                  Parse Quality 高
                         ▲
                         │
正式来源 + 高质量解析   │   非正式来源 + 高质量解析
                         │
─────────────────────────┼────────────→
                         │
正式来源 + 低质量解析   │   非正式来源 + 低质量解析
                         │
```

真正 Gold Data：

> 尽量来自左上。

---

# 二百四十一、如果正式来源解析质量低怎么办？

不是：

> 换一个不可靠来源。

而是：

> 提升解析、人工复核。

---

# 二百四十二、这就是专业数据工程和“抓网页文本”的区别

我们不仅关心：

> 有没有字。

还关心：

```text
字对不对？
顺序对不对？
结构对不对？
来源对不对？
能不能追溯？
```

---

# 二百四十三、本阶段 6 个核心心智模型总结

| 核心心智模型 | 真正含义 |
|---|---|
| **① 看得见 ≠ 有文字层** | 扫描 PDF 可能只是图像 |
| **② Extract ≠ Parse** | 拿到字符不代表阅读顺序和结构正确 |
| **③ Parsing = 内容 + 结构 + 来源位置** | 不能只保存大字符串 |
| **④ OCR 是后备方案** | 有可信原生文字时优先原生提取 |
| **⑤ 早期不要丢 Provenance** | 页码、bbox、来源、Parser 版本以后都很有价值 |
| **⑥ Parsing Quality 由业务决定** | 对评分表、金额、法规引用等要更严格 |

---

# 二百四十四、再加 4 个辅助心智模型

### 辅助模型 A

```text
Character Correct
≠
Document Correct
```

---

### 辅助模型 B

```text
Parser Success
≠
Business Success
```

---

### 辅助模型 C

```text
Visual Line
≠
Semantic Paragraph
```

---

### 辅助模型 D

```text
Source Authority
≠
Parse Quality
```

这四个也很重要。

---

# 二百四十五、思维实验 A

一份 PDF：

> 可以搜索文字。

是不是一定不需要 OCR？

不一定。

因为：

> 隐藏 OCR Text Layer 也可能质量很差。

要先：

> 检查文字质量。

---

# 二百四十六、思维实验 B

`extract_text()` 返回 80,000 字。

是不是说明：

> 解析非常成功？

不是。

还要检查：

- 顺序；
- 表格；
- 页眉；
- 字符；
- 结构。

---

# 二百四十七、思维实验 C

两栏页面：

> 所有字符都被正确提取。

但顺序是：

```text
左1
右1
左2
右2
```

解析成功吗？

> 对业务而言可能失败。

---

# 二百四十八、思维实验 D

扫描 PDF 全部先 OCR。

是不是最统一、最专业？

不是。

有高质量原生文字层：

> 没必要主动引入 OCR 误差。

---

# 二百四十九、思维实验 E

一个评分表：

> 所有文字提取正确，

但行列关系丢了。

是不是还能直接拿去训练评分标准审查？

> 通常不能。

---

# 二百五十、思维实验 F

页眉每页重复 100 次。

为什么不直接在原始解析阶段永久删除？

因为最好：

> 先标记和保留原始层，

再在 Normalization 层处理。

---

# 二百五十一、思维实验 G

DOCX 一定比 PDF 更可信？

不是。

DOCX：

> 可能是内部工作稿。

PDF：

> 可能是正式发布版。

来源权威性：

> 必须单独判断。

---

# 二百五十二、思维实验 H

一个 OCR 字符准确率 99.9%。

是不是对采购业务一定足够？

不一定。

剩下的 0.1%：

> 如果集中在金额、否定词、分值、法律条号，

就可能非常严重。

---

# 二百五十三、本阶段最容易犯的 12 个错误

### 错误 1

> PDF 就是只读 Word。

错。

### 错误 2

> PDF 能复制文字就一定解析可靠。

错。

### 错误 3

> 有 OCR 就不需要 Native Parsing。

错。

### 错误 4

> OCR 越早越好。

错。

### 错误 5

> 字都提出来了，结构就不重要。

错。

### 错误 6

> 每个换行都是新段落。

错。

### 错误 7

> 表格只是普通文字。

错。

### 错误 8

> 页眉页脚直接全部删就行。

危险。

### 错误 9

> HTML 一定天然干净。

错。

### 错误 10

> DOCX 一定天然有完美结构。

错。

### 错误 11

> Parser 没报错就是成功。

错。

### 错误 12

> 最终只保存 plain text 就足够。

对我们的长期项目来说：

> 通常太早丢失信息。

---

# 二百五十四、本阶段最重要的一张故障树

以后遇到“解析文本有问题”，不要乱修。

可以这样问：

```text
解析结果异常
   │
   ├─ 原文件损坏？
   │
   ├─ 扫描页？
   │      ↓
   │     OCR
   │
   ├─ Text Layer乱码？
   │      ↓
   │     Encoding / OCR fallback
   │
   ├─ 阅读顺序错？
   │      ↓
   │     Layout Analysis
   │
   ├─ 表格错？
   │      ↓
   │     Table Recovery
   │
   ├─ 页眉页脚污染？
   │      ↓
   │     Repetition + Position
   │
   └─ 清洗规则误删？
          ↓
        回到Raw Parsed Layer
```

这比：

> “换一个 PDF 库试试”

专业很多。

---

# 二百五十五、这一阶段之后，我们已经有两个重要对象

Stage 1：

```text
Task Schema
```

回答：

> **最后训练样本应该长什么样？**

Stage 2：

```text
ParsedDocument
```

回答：

> **原始文件怎样变成可信的机器可读内容？**

---

# 二百五十六、但中间还缺一座桥

现在 ParsedDocument 里只有：

```text
Page
Block
Table
```

我们还没真正知道：

```text
哪一个是章标题？

哪一个是资格条件？

哪一个是技术参数？

哪几个Block其实属于同一条条款？
```

这就是下一阶段。

---

# 二百五十七、第 2 阶段掌握标准

如果现在不看前文，你能够自己回答下面这些问题，本阶段就算真正掌握：

> 为什么 PDF 不能简单理解成只读 Word？

> 为什么人眼能看到文字，不代表 PDF 内存在可靠 Text Layer？

> 什么是文字型 PDF、扫描型 PDF、混合型 PDF？

> 为什么混合 PDF 最好按页决定是否 OCR？

> 为什么 OCR 不应该成为所有 PDF 的默认第一步？

> `extract_text()` 成功为什么不等于文档解析成功？

> Reading Order 为什么重要？

> 两栏 PDF 为什么容易产生顺序错误？

> Character Correct 和 Document Correct 有什么区别？

> 页眉页脚为什么会污染训练语料？

> Visual Line Break 和 Semantic Paragraph Break 为什么不同？

> 为什么表格不能只 flatten 成普通字符串？

> 为什么评分标准表尤其需要保存行列关系？

> 为什么要保存 Block Type？

> 为什么 bbox / 页面坐标对结构恢复有帮助？

> 为什么训练模型未必需要 bbox，但数据工程应该保留？

> HTML 相比 PDF 有什么结构优势？

> HTML 为什么仍然需要正文抽取？

> DOCX 为什么通常比 PDF 更容易恢复结构？

> DOCX 又有哪些文本框、修订、表格等陷阱？

> 为什么解析时应该记录 file hash？

> 为什么 parser_version 需要版本化？

> 为什么 `extraction_method=native/ocr` 值得保存？

> 什么叫 Provenance？

> 为什么 Parsed Layer 不应该只保存一条全文字符串？

> 为什么要区分 Raw、Parsed、Normalized、Structured、Annotated？

> 为什么程序 `success=True` 不能证明业务解析成功？

> 为什么金额、分值、否定词和法规条号需要更严格的准确性？

> 为什么 OCR 99.9% 字符准确率仍可能在采购业务中不够？

> Source Authority 和 Parse Quality 为什么是两个不同维度？

如果这些你都可以自己解释：

\[
\boxed{
第四课第2阶段真正掌握
}
\]

---

# 二百五十八、本阶段最终只记一句话

> **文档解析的目标不是“从文件里抠出一大段文字”，而是尽可能忠实地恢复人类实际看到和理解的内容关系：文字是什么、先后怎么读、属于什么版式结构、表格怎样对应、它来自哪一页哪一个位置，以及这段文字究竟是原生提取还是 OCR 得到的。**

最后压成一张图：

```text
                  Raw Document
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
        PDF           HTML          DOCX
         │             │             │
         └─────────────┼─────────────┘
                       ▼
                 Format Adapter
                       │
                       ▼
              Text / Block Extraction
                       │
              ┌────────┴────────┐
              ▼                 ▼
       Native Text Good     Scan / Bad Text
              │                 │
              │                 ▼
              │                OCR
              │                 │
              └────────┬────────┘
                       ▼
                 Layout Recovery
                       │
                       ▼
                 Reading Order
                       │
                       ▼
                  Table Recovery
                       │
                       ▼
               Quality Validation
                       │
                       ▼
              ParsedDocument_V0.1
```

---

# 下一阶段：第四课 · 第 3 阶段
## 文档结构恢复与 Clause Segmentation——机器拿到“正确文字”之后，怎样知道哪里是章、节、表格、资格条件，以及“一条采购条款”到底从哪里开始、在哪里结束？

第 3 阶段我们会处理一个很有意思的问题：

假设 Parser 已经完美给出了：

```text
第三章 采购需求
3.1 资格条件
1. 供应商……
2. 供应商……
3.2 技术要求
1. 设备……
2. 系统……
```

机器仍然只看到：

> 一系列 Block。

我们要第一次把它恢复成：

```text
Project
  ↓
Document
  ↓
Section
  ↓
Subsection
  ↓
Clause
```

并真正产生第一批：

# `ClauseUnit_V0.1`

也就是说，第 2 阶段解决：

> **“文字拿对了吗？”**

第 3 阶段开始解决：

> **“这些文字在业务上到底属于哪里？”**

---

<!-- LESSON 04 STAGE 02 END -->


<!-- LESSON 04 STAGE 03 START -->

# 第四课 · 第 3 阶段：文档结构恢复与 Clause Segmentation
## 机器已经拿到了“正确文字”，为什么它仍然不知道哪里是一章、哪里是一条资格条件，以及“一条采购条款”到底从哪里开始、在哪里结束？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Clause Segmentation ≠ Sentence Splitting 一条采购条款可能有很多句**
2. **标题不是靠“字体大”一个特征判断， 而是多个结构信号共同决定**
3. **文档结构恢复的核心不是切得越细， 而是恢复“谁属于谁”**
4. **Target Clause 可以很小， 但它必须保留 Parent Section 和必要 Context**
5. **表格中的一行、一个评分项， 也可能是一条真正的业务 Clause**
6. **结构恢复错误会直接污染： 风险类型、Train/Test切分、RAG、SFT和最终审查结果**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Clause Segmentation` | 条款切分：把连续文档恢复成可审查业务条款 |
| `Block` | 版面块：文档解析后保留布局和位置的基本块 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Parser` | 解析器：把 PDF/Word/HTML 转换为结构化可处理内容 |
| `Recovery` | 恢复：工具失败或中断后安全重试、降级和继续 |
| `SFT` | 监督微调：用监督样本继续更新模型参数 |
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `CPU` | CPU：负责通用控制、数据准备和部分算子 |
| `Loss` | 损失函数：把预测错误压缩成可优化的数值信号 |
| `Layout` | 版面结构：文字块、表格、列、坐标和阅读顺序信息 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `Representation` | 表示：模型内部承载语义或特征的向量结构 |

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

第 2 阶段结束以后，我们手里已经不再只是：

```text
一个PDF文件
```

而开始拥有类似这样的东西：

```text
ParsedDocument
│
├── Page 1
│   ├── Block 1
│   ├── Block 2
│   └── Block 3
│
├── Page 2
│   ├── Block 4
│   ├── Block 5
│   └── Table 1
│
└── ...
```

而且我们已经尽量保证：

> 文字基本正确。

> 阅读顺序基本正确。

> 页码、位置、表格和来源信息都还保留着。

这听起来似乎已经很接近训练数据了。

但实际上，中间还缺了极其关键的一层。

假设 Parser 给我们：

```text
第三章 采购需求
3.1 供应商资格条件
1. 供应商应具有独立承担民事责任的能力。
2. 供应商须在本市注册成立5年以上。
3.2 技术要求
1. 服务器CPU核心数不得少于……
2. 存储容量不得低于……
```

对于人类来说：

> 结构一眼就看出来了。

但机器如果只拿到几个 Text Block，它未必知道：

```text
“第三章 采购需求”
=
章标题

“3.1 供应商资格条件”
=
第三章下面的子章节

“2. 供应商须在本市注册成立5年以上。”
=
一条真正需要审查的资格条件

“3.2 技术要求”
=
上一节结束、新的一节开始
```

所以今天要解决的问题是：

> **怎样把一堆正确的文字块，恢复成一个有层级、有归属、能切出真实采购条款的业务结构？**

最终我们第一次要产出：

# `ClauseUnit_V0.1`

---

# 一、本阶段真正要解决的一个核心问题

可以把问题压缩成一句话：

> **文档里的文字，怎样从“平面字符串”恢复成“Project → Document → Section → Clause”的层级结构？**

第 2 阶段解决的是：

```text
文字对不对？
```

第 3 阶段开始解决：

```text
这些文字到底属于哪里？
```

这是两个完全不同的问题。

---

# 二、本阶段先建立 6 个核心心智模型

先记住这六句话：

```text
① Clause Segmentation ≠ Sentence Splitting
   一条采购条款可能有很多句

② 标题不是靠“字体大”一个特征判断，
   而是多个结构信号共同决定

③ 文档结构恢复的核心不是切得越细，
   而是恢复“谁属于谁”

④ Target Clause 可以很小，
   但它必须保留 Parent Section 和必要 Context

⑤ 表格中的一行、一个评分项，
   也可能是一条真正的业务 Clause

⑥ 结构恢复错误会直接污染：
   风险类型、Train/Test切分、RAG、SFT和最终审查结果
```

今天绝大部分内容，都在展开这六句话。

---

# 三、先看一个最简单的文档

假设原文是：

```text
第三章 采购需求

3.1 供应商资格条件

1. 供应商应具有独立承担民事责任的能力。

2. 供应商须在本市注册成立5年以上。

3.2 技术要求

1. 系统应支持不少于1000个并发用户。

2. 数据库服务器内存不得低于256GB。
```

人类会自动构建：

```text
第三章 采购需求
│
├── 3.1 供应商资格条件
│     ├── 条款1
│     └── 条款2
│
└── 3.2 技术要求
      ├── 条款1
      └── 条款2
```

机器真正需要恢复的，就是这棵树。

---

# 四、所以结构恢复不是“切文本”

更准确地说，是：

# Tree Reconstruction

也就是：

> **重新构建文档树。**

你可以把原始 Parser 输出看成：

```text
一排积木
```

Structure Recovery 的任务是：

> 把它们重新搭回原来的楼。

---

# 五、为什么“谁属于谁”这么重要？

假设机器拿到这句话：

```text
不得低于500万元。
```

单独看：

> 意义不完整。

但如果 Parent Section 是：

```text
第三章
供应商资格条件
```

含义可能是：

> 注册资本或者类似资格门槛。

---

# 六、如果它的 Parent Section 是

```text
项目预算
```

那：

```text
不得低于500万元
```

可能完全不是供应商资格。

---

# 七、所以一个很重要的公式式直觉

\[
\boxed{
ClauseMeaning
=
ClauseText
+
StructuralContext
}
\]

这里的 Structural Context 就包括：

```text
它在哪一章？
在哪一节？
属于什么表格？
前面的标题是什么？
```

---

# 八、第一件要恢复的东西：Heading

Heading：

> 标题。

例如：

```text
第一章 招标公告

第二章 投标人须知

第三章 采购需求

第四章 评标办法
```

这些显然是高级标题。

---

# 九、但现实不会永远这么整齐

有的文件写：

```text
第三章 采购需求
```

有的写：

```text
第三部分 采购需求
```

有的写：

```text
三、采购需求
```

有的甚至只是：

```text
采购需求
```

然后字体：

> 加粗、居中、字号大。

---

# 十、所以 Heading Detection 不能只靠一个规则

例如：

```text
字号 > 16
→ 标题
```

会非常危险。

---

# 十一、因为正文里也可能有大字

比如：

> “特别提示：”

可能被加粗、放大。

但它并不一定是：

> 章级 Heading。

---

# 十二、所以标题判断通常要组合多个信号

例如：

```text
文本内容
+
编号模式
+
字号
+
加粗
+
缩进
+
居中
+
上下间距
+
页面位置
+
上下文
```

这些一起看。

---

# 十三、编号模式是非常强的信号

政府采购文件特别喜欢编号。

例如：

```text
第一章
第二章
第三章
```

---

# 十四、下一层可能是

```text
一、
二、
三、
```

---

# 十五、还可能是

```text
1.
2.
3.
```

---

# 十六、下一层又可能是

```text
1.1
1.2
1.3
```

---

# 十七、甚至

```text
3.2.1
3.2.2
3.2.3
```

---

# 十八、中文法律和政府文件里还常见

```text
（一）
（二）
（三）
```

再下一层：

```text
1）
2）
3）
```

甚至：

```text
①
②
③
```

---

# 十九、所以我们需要一个 Numbering Grammar

不用把它想成复杂语言学。

就是：

> **建立对编号体系的识别规则。**

比如机器看见：

```text
第三章
```

很可能判断：

```text
level = 1
```

看到：

```text
3.2
```

可能：

```text
level = 2
```

看到：

```text
3.2.1
```

可能：

```text
level = 3
```

---

# 二十、但编号也不能盲信

例如：

```text
1. 供应商应……
```

这可能是：

> 条款编号。

不一定是：

> Section Heading。

---

# 二十一、所以机器需要区分

```text
Section Number
```

和：

```text
Clause Number
```

这不是同一个东西。

---

# 二十二、怎么区分？

看上下文。

比如：

```text
3.2 售后服务要求
```

很像标题。

因为：

- 内容短；
- 没有完整句末；
- 后面跟很多子项。

---

# 二十三、而

```text
1. 供应商应具有……
```

很像 Clause。

因为：

> 已经是完整业务要求。

---

# 二十四、这就是一个很重要的思想

# Structure is contextual

结构不是单个 Block 自己决定的。

还要看：

> 前后 Block。

---

# 二十五、比如连续文本：

```text
3.2 售后服务

1. 提供7×24小时服务热线。

2. 故障发生后2小时内到达现场。

3. 提供不少于3年的维护服务。
```

机器应该推断：

```text
3.2 售后服务
=
Parent Section
```

而下面三个编号项：

> 都属于它。

---

# 二十六、这叫 Parent-Child Relation

也就是：

```text
父节点
↓
子节点
```

---

# 二十七、文档结构恢复真正核心的不是

> “这是标题吗？”

而是：

> **“如果是标题，它是谁的父节点？”**

这一步特别重要。

---

# 二十八、最终 Section Tree 可能长这样

```text
第三章 采购需求
│
├── 3.1 项目概况
│
├── 3.2 售后服务
│     ├── Clause 1
│     ├── Clause 2
│     └── Clause 3
│
└── 3.3 技术参数
      ├── Clause 4
      └── Clause 5
```

---

# 二十九、这时 `section_path` 就可以自动产生

比如 Clause 2：

```text
第三章 采购需求
/
3.2 售后服务
```

也就是：

```text
section_path
```

---

# 三十、上一阶段我们已经知道这个字段非常值钱

因为它可以帮助：

- 模型理解；
- 条款分类；
- 产品定位；
- 错误追踪；
- RAG；
- 数据切片。

---

# 三十一、现在进入今天第二个核心概念

# Clause Segmentation

什么叫 Clause？

可以先理解为：

> **一个能够被独立审查、标注或执行的业务要求单元。**

注意这里没有说：

> “一句话”。

---

# 三十二、这是非常重要的区别

# Clause ≠ Sentence

例如：

> “供应商应提供7×24小时服务热线，并应在收到故障通知后30分钟内响应；对于一级故障，应在2小时内到达现场。”

这里有多个标点。

但业务上：

> 完全可以是一条完整的售后服务要求。

---

# 三十三、如果用普通 Sentence Splitter

可能切成：

```text
A：
供应商应提供7×24小时服务热线。

B：
并应在收到故障通知后30分钟内响应。

C：
对于一级故障，应在2小时内到达现场。
```

---

# 三十四、问题是什么？

B 单独看：

> 主语缺失。

C 单独看：

> 不知道服务对象是谁。

---

# 三十五、所以简单按

```text
。！？；
```

全部切开：

> 很危险。

---

# 三十六、Clause Segmentation 更接近

> **业务语义边界识别。**

它问：

> 哪些文本必须一起看，才能形成一个完整要求？

---

# 三十七、一个采购条款可能只有一句

例如：

> “本项目不接受联合体投标。”

这非常适合作为一个独立 Clause。

---

# 三十八、也可能有三句

例如：

> “项目服务期为三年。合同一年一签。采购人根据年度考核结果决定是否续签。”

这三个句子：

> 很可能属于一个完整合同期限机制。

---

# 三十九、如果拆太细

模型会看不完整。

---

# 四十、如果不拆

整页甚至整章作为一个 Clause，

模型又无法：

> 精确定位风险。

---

# 四十一、所以 Clause Segmentation 的本质又是一个平衡

```text
太细
→ Context丢失

太粗
→ 判断对象不清楚
```

我们要找：

# Business Atomicity

业务原子性。

---

# 四十二、什么叫 Business Atomicity？

就是：

> **再往下拆，就会让一个独立业务要求失去完整意义。**

---

# 四十三、比如

```text
供应商必须是本市注册企业，且注册时间不少于5年。
```

这里有两个条件：

```text
本市注册
+
注册满5年
```

要不要拆成两条？

---

# 四十四、答案不是绝对的

如果未来任务是：

> 风险类型细粒度识别，

可能值得拆。

因为：

```text
本地注册要求
```

和：

```text
企业成立年限
```

可能是两类不同风险。

---

# 四十五、但如果拆以后变成：

```text
且注册时间不少于5年
```

上下文又不完整。

所以更好的做法可能是：

> 保留一个 Parent Clause，

再允许有：

# Sub-conditions

---

# 四十六、例如

```text
Clause C001
供应商必须是本市注册企业，且注册时间不少于5年。

Subcondition 1
必须是本市注册企业

Subcondition 2
注册时间不少于5年
```

这样：

> 既保留完整条款，

又能细粒度分析。

---

# 四十七、这是一种很重要的设计思路

\[
\boxed{
保留原始Clause
+
允许派生Sub-Clause
}
\]

不要一上来：

> 永久切碎原文。

---

# 四十八、这和上一阶段“Lossless First”完全一致

数据工程里我们越来越看到一个共同原则：

> **早期尽量保留，后期按任务派生。**

---

# 四十九、现在看一个真实一点的采购结构

```text
第四章 评标办法

4.1 评标方法

本项目采用综合评分法。

4.2 评分标准

（一）技术部分，满分40分

1. 技术方案，20分
根据投标人技术方案的完整性、可行性评分。

2. 项目经验，10分
每提供一个类似项目业绩得2分，最高10分。

（二）商务部分，满分30分
...
```

---

# 五十、这里到底有哪些 Clause？

可能至少有：

```text
本项目采用综合评分法。
```

以及：

```text
技术方案，20分
根据投标人技术方案的完整性、可行性评分。
```

以及：

```text
项目经验，10分
每提供一个类似项目业绩得2分，最高10分。
```

---

# 五十一、注意第二条

如果只切：

```text
技术方案，20分
```

信息不够。

---

# 五十二、如果只切：

```text
根据投标人技术方案的完整性、可行性评分。
```

又丢了：

> 20 分。

所以这两个 Block：

> 应该属于同一个评分 Clause。

---

# 五十三、这就是为什么 Clause Segmentation 不能只按段落

有时：

```text
多个Paragraph
=
一个Clause
```

---

# 五十四、反过来也可能

一个 Paragraph 里：

> 包含多个 Clause。

例如：

> “供应商应具有软件开发能力；应具备3名高级工程师；应在项目所在地设置服务点。”

三个业务条件挤在一段。

---

# 五十五、所以：

```text
Paragraph
≠
Clause
```

这条也值得记。

---

# 五十六、到这里我们已经有三个不同概念

```text
Sentence
Paragraph
Clause
```

必须彻底分开。

---

# 五十七、Sentence

语言学边界。

例如：

> 句号、问号。

---

# 五十八、Paragraph

版式边界。

例如：

> 一个段落。

---

# 五十九、Clause

业务判断边界。

例如：

> 一个完整资格条件、技术要求、评分项。

---

# 六十、这三个层次偶尔一致

但：

> 经常不一致。

---

# 六十一、现在看表格

假设技术参数表：

| 序号 | 技术指标 | 要求 |
|---|---|---|
| 1 | CPU | 核心数≥32 |
| 2 | 内存 | ≥256GB |
| 3 | 存储 | ≥10TB |

这里每一行：

> 很可能就是一个 Clause。

---

# 六十二、所以 Table Row 也可以变成

# ClauseUnit

例如：

```text
Clause 1
技术指标：CPU
要求：核心数≥32
```

---

# 六十三、但不能只保存：

```text
核心数≥32
```

因为缺少：

> CPU。

---

# 六十四、所以表格 Clause 的 Context 往往包括

```text
Column Header
+
Row Header
+
Cell Content
+
Table Caption
+
Parent Section
```

---

# 六十五、比如：

```text
Section:
第三章 / 技术要求

Table:
服务器技术参数表

Item:
CPU

Requirement:
核心数≥32
```

这样才完整。

---

# 六十六、这就是表格的结构化价值

表格不是：

> 转成纯文本越早越好。

更理想的是先保存：

```text
row
column
header
cell
```

然后根据任务：

> 生成 Clause View。

---

# 六十七、评分表更加明显

| 评分项 | 分值 | 评分规则 |
|---|---:|---|
| 本地服务机构 | 5 | 在本市设有服务机构得5分 |

这里真正要审查的 Clause 不是：

```text
5
```

也不是：

```text
本地服务机构
```

而是完整关系：

```text
本地服务机构
+
5分
+
在本市设有服务机构得5分
```

---

# 六十八、否则模型可能完全不知道

> 这个“5”奖励的是什么。

---

# 六十九、所以结构恢复的目标不仅是标题层级

还包括：

> **业务关系。**

---

# 七十、现在看跨页 Clause

这是政府采购文件特别常见的问题。

第 27 页底部：

```text
供应商应提供本项目所需的技术支持服务，包括但不限于：
```

第 28 页顶部：

```text
（1）7×24小时电话支持；
（2）重大故障2小时内到场；
（3）每季度提供一次巡检服务。
```

---

# 七十一、如果按页独立切

第 27 页：

```text
供应商应提供……包括但不限于：
```

是一条残缺 Clause。

---

# 七十二、第 28 页：

```text
（1）7×24小时电话支持
```

又缺少：

> 主语和上位要求。

---

# 七十三、所以 Page Boundary

不能等价于：

# Clause Boundary

---

# 七十四、这一点特别重要

\[
\boxed{
PageBoundary
\neq
SemanticBoundary
}
\]

PDF 页只是：

> 打印版式。

不是：

> 业务语义边界。

---

# 七十五、所以跨页结构恢复要利用

```text
编号连续
+
句法连续
+
缩进连续
+
Section未变化
```

判断：

> 这是上一页延续。

---

# 七十六、比如上一页最后是：

```text
包括：
```

下一页直接：

```text
（1）
```

这是很强的延续信号。

---

# 七十七、再比如表格

上一页表格有：

```text
序号 评分项 分值
```

下一页继续：

```text
4 企业实力 5分
```

很可能：

> 还是同一张表。

---

# 七十八、所以结构恢复一定要跨页看

不能：

> 每页独立处理后永不联系。

---

# 七十九、现在看另一个危险对象

# Appendix / Attachment

例如：

```text
附件1：
中小企业声明函格式
```

里面也有：

```text
一、
二、
1.
2.
```

编号形式和正文一样。

---

# 八十、如果机器没有识别

```text
附件
```

这个新的 Section Boundary，

可能把模板里的内容：

> 接到采购需求下面。

---

# 八十一、所以一些特殊结构词也很重要

例如：

```text
附件
附表
格式
投标文件格式
合同草案
评分办法
采购需求
资格条件
```

这些往往：

> 是高价值 Structural Anchor。

---

# 八十二、什么叫 Structural Anchor？

就是：

> 对文档层级特别有提示作用的文本。

---

# 八十三、比如：

```text
第三章 采购需求
```

几乎明确告诉你：

> 后面进入采购需求区域。

---

# 八十四、

```text
第四章 评标办法
```

意味着：

> 后面的条款很可能属于评分和评标。

---

# 八十五、这对后面 Risk Type 也有帮助

比如同一句：

```text
在本市设有机构
```

如果位于：

```text
供应商资格条件
```

可能是：

> Qualification Risk。

---

# 八十六、如果位于：

```text
评分标准
```

可能是：

> Scoring Rule Risk。

---

# 八十七、所以 Structure 和 Risk Taxonomy

不是完全独立的。

---

# 八十八、但这里有一个重要边界

不要在结构恢复阶段直接说：

> “这是违规条款。”

结构阶段应该主要回答：

```text
它是什么结构？
属于哪里？
```

---

# 八十九、而风险阶段回答：

```text
它有没有问题？
```

不要混。

---

# 九十、这叫

# Structural Classification

和：

# Compliance Classification

分离。

---

# 九十一、例如结构恢复可以标记：

```text
section_type = supplier_qualification
```

这不代表：

```text
risk_present = true
```

---

# 九十二、资格条件本身：

> 完全可以合法合理。

所以：

\[
\boxed{
SectionType
\neq
RiskLabel
}
\]

---

# 九十三、这个区别非常重要

否则模型很容易学成：

```text
资格条件
=
风险
```

那就废了。

---

# 九十四、现在开始设计 Section Type

为了帮助后续任务，可以给 Section 一个业务类别。

例如第一版：

| Section Type | 含义 |
|---|---|
| procurement_notice | 采购公告 |
| supplier_qualification | 供应商资格 |
| procurement_requirement | 采购需求 |
| technical_requirement | 技术要求 |
| commercial_requirement | 商务要求 |
| scoring_rule | 评分标准 |
| contract_term | 合同条款 |
| attachment | 附件/格式 |

这只是结构标签。

---

# 九十五、为什么不直接只保存标题文字？

因为不同文件会写：

```text
资格要求
```

```text
投标人资格
```

```text
申请人的资格要求
```

```text
供应商条件
```

其实都可能对应：

```text
supplier_qualification
```

---

# 九十六、所以可以同时保存

```text
section_title_raw
```

和：

```text
section_type
```

---

# 九十七、例如：

```json
{
  "section_title_raw": "申请人的资格要求",
  "section_type": "supplier_qualification"
}
```

这样：

> 原文不丢。

同时：

> 结构统一。

---

# 九十八、这是非常好的数据工程习惯

```text
Raw Value
+
Normalized Value
```

两者同时保留。

---

# 九十九、现在设计 Section Node

概念上可以是：

```json
{
  "section_id": "SEC-0032",
  "title": "3.2 售后服务",
  "level": 2,
  "section_type": "commercial_requirement",
  "parent_section_id": "SEC-0030",
  "start_page": 27,
  "end_page": 29
}
```

---

# 一百、注意 `parent_section_id`

这非常关键。

有了它：

> Section Tree 才能重建。

---

# 一百零一、然后 ClauseUnit 可以引用 Section

例如：

```json
{
  "clause_id": "CLAUSE-00178",
  "section_id": "SEC-0032",
  "text": "供应商应保证故障发生后2小时内到达现场。"
}
```

---

# 一百零二、这样就形成：

```text
Document
↓
Section
↓
Clause
```

---

# 一百零三、但 Clause 还应该保存来源 Block

因为以后要追溯。

例如：

```text
source_block_ids
```

可能：

```text
B00872
B00873
```

---

# 一百零四、为什么可能两个 Block？

因为一条 Clause：

> 可能跨两个段落。

或者：

> 跨页。

---

# 一百零五、所以 Clause 不应该强迫：

```text
1 Clause = 1 Block
```

更好的关系是：

```text
1 Clause
←
1..N Source Blocks
```

---

# 一百零六、反过来也可能

```text
1 Block
→
N Clauses
```

因为一个段落可能有多个独立条件。

---

# 一百零七、这说明：

> Block 和 Clause 是不同层。

这个概念一定要稳住。

---

# 一百零八、第 2 阶段的 Block 是

> 页面版式单元。

第 3 阶段的 Clause 是：

> 业务语义单元。

---

# 一百零九、它们关系很多对多

概念上：

```text
Layout Block
   ↕
Clause Unit
```

不是简单一一对应。

---

# 一百一十、现在看嵌套条款

例如：

```text
1. 供应商须满足以下条件：
   （1）具有独立法人资格；
   （2）注册资本不低于5000万元；
   （3）在本市设有固定服务机构。
```

这里到底应该切几条？

---

# 一百一十一、至少有两种表示方式

方式 A：

> 整体作为一个 Clause。

---

# 一百一十二、方式 B：

Parent Clause：

```text
供应商须满足以下条件：
```

三个 Child Clause：

```text
具有独立法人资格
注册资本不低于5000万元
在本市设有固定服务机构
```

---

# 一百一十三、对于我们的风险审查任务

方式 B：

> 更有价值。

因为三个子条件：

> 风险性质可能不同。

---

# 一百一十四、但我们不能丢掉 Parent

因为子条款：

> 是在“供应商须满足以下条件”的语境下成立。

---

# 一百一十五、所以 Clause 本身也可以形成小树

```text
Clause Parent
│
├── Subclause 1
├── Subclause 2
└── Subclause 3
```

---

# 一百一十六、这时可以有：

```text
parent_clause_id
```

---

# 一百一十七、于是文档树可以变成

```text
Project
└── Document
    └── Section
        └── Clause
            └── Sub-Clause
```

这已经非常接近真正的政府采购数据结构。

---

# 一百一十八、但不要无限嵌套

现实文档可能：

```text
1
（1）
1）
①
a.
```

层级非常深。

如果完整复制所有层级：

> 数据会很复杂。

---

# 一百一十九、所以我们要问

> **哪些层级对业务判断真正有用？**

这和 Schema 第一阶段的原则一样：

# Minimal but Sufficient

---

# 一百二十、例如对于 ClauseUnit

第一版可能只保留：

```text
section_path
parent_clause_text
clause_text
```

就已经足够。

数据库内部可以：

> 保留完整树。

训练 View：

> 再简化。

---

# 一百二十一、再次看到

```text
Master Representation
```

和：

```text
Task View
```

的区别。

---

# 一百二十二、现在说一个非常关键的问题

# Clause Boundary Detection

机器究竟怎么判断：

> 一条 Clause 结束了？

---

# 一百二十三、强信号之一：编号变化

例如：

```text
1. 条件A
2. 条件B
```

通常：

> `2.` 是新 Clause 开始。

---

# 一百二十四、但编号也可能在 Clause 内部

例如：

> “服务内容包括：1）巡检；2）培训；3）应急支持。”

这里：

```text
1）
2）
3）
```

可能只是：

> 一个 Clause 里的子项目。

---

# 一百二十五、所以单看编号不够

要看：

> 当前层级。

---

# 一百二十六、如果当前已经在：

```text
1.
```

下面看到：

```text
1）
```

很可能：

> 子级。

---

# 一百二十七、如果连续出现：

```text
1.
2.
3.
```

并且格式一致，

很可能：

> 同级 Clause。

---

# 一百二十八、强信号之二：缩进

例如：

```text
1. 主条款
    （1）子条件
    （2）子条件
```

缩进：

> 帮助推断层级。

---

# 一百二十九、强信号之三：字体与 Style

标题可能：

> 粗体。

Clause：

> 正文字体。

子项：

> 缩进但不加粗。

---

# 一百三十、强信号之四：标点与句法

例如：

```text
供应商应满足以下条件：
```

冒号：

> 很可能提示下面还有子项。

---

# 一百三十一、如果下一 Block 是：

```text
（1）……
```

非常可能：

> 属于上一个 Parent。

---

# 一百三十二、强信号之五：空白距离

标题上下通常：

> 空间更大。

同一 Clause 内连续行：

> 间距更紧。

---

# 一百三十三、强信号之六：页面位置

比如一行：

> 居中、页面顶部、字号大。

更像：

> Heading。

---

# 一百三十四、强信号之七：词汇模式

比如：

```text
采购需求
供应商资格
评审标准
合同条款
技术要求
```

很像：

> Section Anchor。

---

# 一百三十五、所以整体思路不是

```text
if 字号大:
    标题
```

而是：

```text
多个信号
↓
综合判断
```

---

# 一百三十六、这可以用规则做吗？

可以。

第一版其实很适合：

> Rule-based + Heuristic。

因为政府采购文档：

> 编号和格式有很强规律。

---

# 一百三十七、例如简单规则：

```text
如果文本匹配
“第X章”
+
长度短
+
字体较大

→ Heading Level 1
```

---

# 一百三十八、再比如：

```text
如果匹配
^\d+\.\d+
+
后面没有长句
+
后面有多个编号项

→ Section Heading
```

---

# 一百三十九、但规则能解决所有文档吗？

当然不能。

因为现实文件：

> 太乱。

---

# 一百四十、有些标题完全没有编号

例如：

```text
特别资格条件
```

只有：

> 加粗。

---

# 一百四十一、有些正文恰好很短

例如：

```text
不接受联合体。
```

长度也很短。

但：

> 它不是标题。

---

# 一百四十二、所以成熟方案可能是

```text
Rules
+
Layout Features
+
Statistical / ML Model
```

甚至：

> LLM 辅助结构判断。

---

# 一百四十三、但这里有一个重要工程原则

不要一上来就用大模型：

> 识别所有标题和层级。

为什么？

---

# 一百四十四、因为很多结构信号

本来是：

> 确定性规则可以很好识别。

比如：

```text
第三章
```

根本不需要：

> 让 LLM 花钱思考。

---

# 一百四十五、所以推荐：

```text
确定性明显的
→ Rule

模糊的
→ Model

极难的
→ Human Review
```

这又是：

# Hybrid Pipeline

---

# 一百四十六、这和 ProcurementAI 最终架构其实一模一样

```text
规则擅长的
→ Rule Engine

模糊语义判断
→ LLM

高风险边界
→ Human
```

数据工程和产品架构：

> 思路高度一致。

---

# 一百四十七、现在说 Confidence

假设系统识别：

```text
“第三章 采购需求”
```

置信度：

> 很高。

---

# 一百四十八、但遇到：

```text
其他要求
```

它不知道这是：

> 一级标题、二级标题还是正文小标题。

可以：

```text
structure_confidence = low
```

---

# 一百四十九、然后不要硬猜

而是标记：

```text
STRUCTURE_AMBIGUOUS
```

---

# 一百五十、这和第一阶段 `needs_review` 是同一个哲学

> **不确定时允许说不确定。**

不要逼 Pipeline：

> 假装百分之百知道。

---

# 一百五十一、低置信度 Section 会影响什么？

比如：

> 下一步 Clause 属于哪里。

所以可以：

> 触发人工复核。

---

# 一百五十二、特别是 Gold Set 来源文件

我们更应该：

> 提高结构校验标准。

---

# 一百五十三、而大量 CPT Corpus

可能允许：

> 较低的结构精度。

再次出现：

# Purpose-specific Quality Threshold

---

# 一百五十四、现在看一个特别典型的失败案例

原文：

```text
第四章 评标办法

4.2 商务评分

1. 企业业绩，10分。
近三年每提供一个类似项目得2分，最高10分。

2. 服务能力，5分。
在本市设有固定服务机构得5分。
```

---

# 一百五十五、错误切分方法：

```text
Clause A:
企业业绩，10分。

Clause B:
近三年每提供一个类似项目得2分，最高10分。

Clause C:
服务能力，5分。

Clause D:
在本市设有固定服务机构得5分。
```

---

# 一百五十六、问题是

A+B：

> 其实一个评分项。

C+D：

> 也是一个评分项。

---

# 一百五十七、如果拆错

模型看到：

```text
在本市设有固定服务机构得5分。
```

还能判断一些东西。

但失去了：

```text
评分项：服务能力
分值：5
```

---

# 一百五十八、而这些信息对风险解释很重要

因为：

> 它不是资格门槛，

而是：

> 评分加分项。

业务性质：

> 完全不同。

---

# 一百五十九、所以 Clause Segmentation 必须尽量保留

# Functional Context

也就是：

> 这条话在文件里承担什么功能。

---

# 一百六十、例如同一句：

```text
在本市设有服务机构
```

放在：

```text
资格条件
```

含义：

> 进入资格门槛。

---

# 一百六十一、放在：

```text
评分办法
```

含义：

> 竞争评分条件。

---

# 一百六十二、放在：

```text
合同履约要求
```

又可能：

> 是中标后的履约要求。

---

# 一百六十三、三者：

> 风险判断完全可能不同。

---

# 一百六十四、所以我们不应该把 Clause 当成孤岛

更合理：

```text
Clause
+
Section Type
+
Section Path
+
Parent Context
```

一起存在。

---

# 一百六十五、现在第一次设计 `ClauseUnit_V0.1`

可以先长这样：

```json
{
  "clause_id": "CLAUSE-00178",
  "document_id": "DOC-00152-01",

  "section_id": "SEC-0032",
  "section_path": [
    "第三章 采购需求",
    "3.2 售后服务"
  ],
  "section_type": "commercial_requirement",

  "clause_text": "供应商应保证故障发生后2小时内到达项目现场。",

  "parent_clause_text": null,

  "source_block_ids": [
    "B00872"
  ],

  "start_page": 27,
  "end_page": 27,

  "clause_order": 18,

  "structure_confidence": 0.98,

  "warnings": []
}
```

这就是第一版概念。

---

# 一百六十六、如果 Clause 跨页

可能：

```json
{
  "start_page": 27,
  "end_page": 28
}
```

---

# 一百六十七、如果有 Parent

比如：

```text
供应商应满足以下条件：
```

可以：

```json
{
  "parent_clause_id": "CLAUSE-00177"
}
```

---

# 一百六十八、如果来自表格

可以增加：

```text
source_type = table_row
```

或者：

```text
table_id
row_id
```

---

# 一百六十九、例如评分表 Clause

```json
{
  "clause_id": "CLAUSE-00421",
  "section_type": "scoring_rule",

  "table_caption": "商务评分表",
  "row_label": "服务能力",
  "score": 5,

  "clause_text": "在本市设有固定服务机构得5分。"
}
```

注意：

> 不一定最终这么设计。

但思想已经很清楚。

---

# 一百七十、ClauseUnit 最重要的不是字段多

而是保证三件事：

```text
① 知道它是什么

② 知道它属于哪里

③ 知道它从原文哪里来
```

---

# 一百七十一、也就是：

\[
\boxed{
Identity
+
Hierarchy
+
Provenance
}
\]

---

# 一百七十二、这三个是 Clause 数据的骨架

后面才加：

> Annotation。

---

# 一百七十三、现在谈稳定 ID

`clause_id`：

> 不能只用当前行号。

---

# 一百七十四、为什么？

Parser 更新以后：

> Clause 顺序可能变化。

如果 ID 是：

```text
row_328
```

可能全部乱掉。

---

# 一百七十五、可以考虑基于

```text
document_id
+
stable local identifier
```

生成 Clause ID。

---

# 一百七十六、或者再保存：

```text
clause_fingerprint
```

帮助以后追踪：

> 同一条 Clause 在 Parser 版本更新后是否变化。

---

# 一百七十七、比如：

```text
旧 Parser:
CLAUSE-102
文本A

新 Parser:
CLAUSE-102
文本A + 补回漏掉的半句
```

你需要知道：

> 这其实是同一业务条款被修正。

---

# 一百七十八、这会影响后面

# Dataset Versioning

第 11 阶段会专门处理。

现在先埋下意识。

---

# 一百七十九、接下来一个重要问题

# Section Boundary

什么时候一个 Section 结束？

---

# 一百八十、最直接：

> 遇到同级或者更高级 Heading。

例如：

```text
3.1 资格条件
...
3.2 技术要求
```

那么：

```text
3.1
```

结束于：

```text
3.2
```

之前。

---

# 一百八十一、树算法上可以理解为

当出现：

```text
new_level <= current_level
```

就要：

> 关闭当前某些层级。

不用背算法。

记住：

> 标题层级像一个栈。

---

# 一百八十二、可以想象

```text
第三章
    3.1
        3.1.1
```

现在遇到：

```text
3.2
```

说明：

```text
3.1.1结束
3.1结束
```

回到：

```text
第三章
```

下面开：

```text
3.2
```

---

# 一百八十三、这就叫 Hierarchy Stack

是非常常见的结构恢复方法。

---

# 一百八十四、现实中编号会乱怎么办？

例如：

```text
3.1
3.2
3.2.1
3.4
```

缺少：

```text
3.3
```

不能因为编号不连续：

> 就判文档损坏。

---

# 一百八十五、因为原文真的可能：

> 没有 3.3。

所以规则应该：

> 容忍缺号。

---

# 一百八十六、还有重复编号

例如：

```text
1.
1.
2.
```

可能：

> 原文编辑错误。

---

# 一百八十七、结构恢复应该做什么？

保留：

> 原文编号。

同时加：

```text
NUMBERING_INCONSISTENT
```

Warning。

不要偷偷：

> 帮原文改成 1、2、3。

---

# 一百八十八、这又是一个重要原则

# Preserve Source Truth

数据工程：

> 不应该悄悄替原文件“纠错”。

---

# 一百八十九、如果需要规范化编号

可以另存：

```text
normalized_order
```

但原始：

```text
raw_number
```

应该保留。

---

# 一百九十、类似：

```json
{
  "raw_number": "1.",
  "normalized_order": 2
}
```

这样：

> 可追溯。

---

# 一百九十一、现在谈标题正文混排

现实里可能：

```text
3.1 资格条件：供应商应满足以下条件：
```

标题和正文：

> 同一行。

---

# 一百九十二、机器需要拆成

```text
Heading:
3.1 资格条件

Lead Text:
供应商应满足以下条件：
```

---

# 一百九十三、否则如果整行都当 Heading

会丢掉：

> “供应商应满足以下条件”。

---

# 一百九十四、反过来全当正文

又会丢掉：

> Section Heading。

---

# 一百九十五、这说明有时一个 Block：

> 需要内部再拆。

---

# 一百九十六、这叫 Block Refinement

第 2 阶段是：

> Layout Block。

第 3 阶段可以：

> 根据语义继续精炼。

---

# 一百九十七、但不要修改原 Block

更好的方式：

```text
Raw Block
↓
Derived Structural Nodes
```

仍然保留：

> 来源关系。

---

# 一百九十八、例如

```text
B0123
原始：
“3.1 资格条件：供应商应满足以下条件：”
```

派生：

```text
Section Heading
“3.1 资格条件”
```

和：

```text
Lead Clause
“供应商应满足以下条件：”
```

两者都指向：

```text
B0123
```

---

# 一百九十九、这样不会丢 provenance。

---

# 二百、现在讲“标题重复”

跨页打印时可能每页顶部重复：

```text
第三章 采购需求
```

这到底是：

> Header

还是：

> Section Heading？

---

# 二百零一、第 2 阶段已经告诉我们

如果它：

- 每页固定顶部；
- 大量重复；
- 位置稳定；

更可能：

> Running Header。

---

# 二百零二、结构恢复时不能把每一页都当：

> 新的第三章开始。

否则：

> 文档树被切碎。

---

# 二百零三、这说明第 2 阶段的 Layout 信息

会直接帮助第 3 阶段。

课程阶段虽然分开：

> 数据本身是连续流水线。

---

# 二百零四、现在看“目录页”

TOC：

```text
第三章 采购需求 ........ 37
第四章 评标办法 ........ 82
```

里面也有很多标题。

---

# 二百零五、如果机器把目录页也当正文结构

会生成：

> 虚假的 Section。

---

# 二百零六、所以要识别

# Table of Contents

目录。

---

# 二百零七、目录常见信号：

```text
目录
点线
页码
大量标题+数字
```

然后标记：

```text
block_type = toc
```

---

# 二百零八、后续 Structure Recovery：

> 不把它当真正 Section Start。

---

# 二百零九、类似还有

# List of Tables

# List of Figures

在部分技术采购文件中也可能出现。

---

# 二百一十、所以“标题文字出现了”

不等于：

> 文档真的进入那个 Section。

还要看：

> 它出现在哪种结构区域。

---

# 二百一十一、现在进入 Semantic Section Classification

当结构已经识别出：

```text
3.2 申请人的资格要求
```

我们可以再映射：

```text
section_type =
supplier_qualification
```

---

# 二百一十二、这个映射可以先用字典

例如：

```text
资格要求
申请人资格
供应商资格
资格条件
```

映射到：

```text
supplier_qualification
```

---

# 二百一十三、

```text
评分办法
评审标准
评分标准
综合评分表
```

映射到：

```text
scoring_rule
```

---

# 二百一十四、

```text
技术要求
技术参数
技术规格
```

映射到：

```text
technical_requirement
```

---

# 二百一十五、这叫 Normalization Mapping

不是改原文。

而是：

> 额外添加统一类别。

---

# 二百一十六、如果标题是：

```text
其他要求
```

怎么办？

语义太模糊。

可以：

```text
section_type = other
```

或者：

```text
unknown
```

---

# 二百一十七、不要强行分类

这又回到：

> 允许不确定。

---

# 二百一十八、现在看一个完整示例

原始 Parsed Blocks：

```text
B1 第三章 采购需求
B2 3.1 资格条件
B3 1. 供应商应具有独立承担民事责任的能力。
B4 2. 供应商须在本市注册成立5年以上。
B5 3.2 技术要求
B6 1. 数据库服务器内存不得低于256GB。
```

---

# 二百一十九、Structure Recovery 后

```text
SEC1
title = 第三章 采购需求
level = 1
type = procurement_requirement
```

---

# 二百二十、

```text
SEC2
title = 3.1 资格条件
level = 2
parent = SEC1
type = supplier_qualification
```

---

# 二百二十一、

```text
C1
text = 供应商应具有独立承担民事责任的能力。
section = SEC2
```

---

# 二百二十二、

```text
C2
text = 供应商须在本市注册成立5年以上。
section = SEC2
```

---

# 二百二十三、

```text
SEC3
title = 3.2 技术要求
level = 2
parent = SEC1
type = technical_requirement
```

---

# 二百二十四、

```text
C3
text = 数据库服务器内存不得低于256GB。
section = SEC3
```

这时：

> 文档真正开始变成业务数据。

---

# 二百二十五、然后 Stage 1 的 Schema 就可以接进来

比如：

```text
Clause C2
↓
送给专家标注
↓
risk_present
risk_type
rationale
evidence
```

---

# 二百二十六、所以整个链终于连起来

```text
Raw PDF
↓
Parsed Block
↓
Section Tree
↓
ClauseUnit
↓
Task Schema
↓
Annotation
```

---

# 二百二十七、这就是为什么第 1、2、3 阶段顺序不能乱

如果一开始直接：

> 对 PDF 全文做 SFT，

你跳过了：

```text
结构恢复
+
业务单元定义
```

后面几乎一定付出代价。

---

# 二百二十八、现在讲一个非常重要的错误

# Over-segmentation

切得太细。

---

# 二百二十九、例如：

> “投标人应在合同签订后10日内完成系统部署，并在部署完成后提供不少于三年的免费维护服务。”

切成：

```text
投标人应在合同签订后10日内完成系统部署
```

和：

```text
并在部署完成后提供不少于三年的免费维护服务
```

第二段：

> 主语弱化。

---

# 二百三十、而这两个条件：

> 可能属于同一个履约要求。

切太细：

> Context 损失。

---

# 二百三十一、另一个错误：

# Under-segmentation

切得太粗。

---

# 二百三十二、比如整段：

```text
供应商须具备以下条件：
1. 本市注册；
2. 注册资本5000万元以上；
3. 具有ISO认证；
4. 近三年完成5个同类项目；
5. 配备20名工程师。
```

全部作为一个 Clause。

---

# 二百三十三、模型如果说：

> “有风险。”

你很难知道：

> 是哪一项。

---

# 二百三十四、也很难标：

```text
risk_subtype
```

因为里面可能：

> 同时有四种不同风险。

---

# 二百三十五、所以理想结构是：

```text
Parent Clause
供应商须具备以下条件

Child 1
本市注册

Child 2
注册资本5000万元以上

Child 3
ISO认证

Child 4
业绩要求

Child 5
人员要求
```

---

# 二百三十六、这就是

# Hierarchical Segmentation

层级切分。

通常比：

> 暴力平铺

更适合政府采购文件。

---

# 二百三十七、接下来一个特别重要的问题

# Minimal Context Window

切出 Clause 后，

到底带多少上下文给模型？

---

# 二百三十八、如果只带 Clause：

```text
不得低于500万元。
```

不够。

---

# 二百三十九、如果带整份 200 页：

> 太多。

---

# 二百四十、所以第一版可以考虑：

```text
Parent Section Title
+
Parent Clause
+
Target Clause
+
必要邻近文本
```

---

# 二百四十一、例如：

```text
Section:
供应商资格条件

Parent:
供应商应满足以下条件：

Target:
注册资本不得低于5000万元。
```

这已经比：

> 单独一句

强很多。

---

# 二百四十二、如果项目背景很重要

再加：

```text
Project Context
```

例如：

```text
项目预算：
300万元
```

---

# 二百四十三、于是模型就能发现

> 注册资本要求和项目规模之间是否可能失衡。

---

# 二百四十四、这再次连接第一阶段

当时我们说：

\[
\boxed{
TargetClause
+
MinimalNecessaryContext
}
\]

现在我们开始真正知道：

> 这个 Context 从哪里来。

就是：

# Document Structure

---

# 二百四十五、所以结构恢复的价值之一

就是：

> 帮助自动构造合理 Context。

---

# 二百四十六、如果没有 Section Tree

你只能：

> 粗暴取前后 500 字。

---

# 二百四十七、这可能把：

> 无关上一节内容

也塞进来。

---

# 二百四十八、有 Section Tree 后

可以优先取：

```text
同一Section
```

或者：

```text
Parent Clause
```

这会更准确。

---

# 二百四十九、这对 RAG 也同样重要

将来法规 RAG：

> 按法规条款层级切。

采购文件 RAG：

> 按 Section / Clause 切。

通常会比：

> 固定 500 Token 切块

更符合语义。

---

# 二百五十、所以 Clause Segmentation 不是只服务 SFT

它同时服务：

```text
SFT
RAG
Evaluation
UI定位
Error Analysis
```

---

# 二百五十一、例如产品 UI

模型告诉用户：

> 风险出现在：

```text
第三章 采购需求
→ 3.1 供应商资格
→ 第2条
```

而不是：

> “大概在第 17,823 个字符附近。”

结构化数据：

> 直接提升产品体验。

---

# 二百五十二、这就是 Structure 的另一种价值

# Explainability

可追溯定位。

---

# 二百五十三、现在谈 Structure Benchmark

和 Parser 一样，

Structure Recovery：

> 也需要评测。

---

# 二百五十四、不能只是看：

> “好像标题都识别出来了。”

可以建立小型 Gold。

---

# 二百五十五、人工标：

```text
哪些是Heading
Heading Level
Parent Section
Clause Boundary
Clause Parent
Table Row Clause
```

---

# 二百五十六、然后评价

例如：

```text
Heading Detection Accuracy

Hierarchy Accuracy

Clause Boundary Precision

Clause Boundary Recall
```

不用现在背公式。

---

# 二百五十七、直觉上：

如果系统把不是 Clause 的地方：

> 切成很多假 Clause，

Precision 会差。

---

# 二百五十八、如果很多真实 Clause：

> 没切出来，

Recall 会差。

---

# 二百五十九、为什么两个都重要？

切太多：

> 数据碎。

切太少：

> 风险混在一起。

---

# 二百六十、我们甚至可以单独看

```text
Table Clause Accuracy
```

---

# 二百六十一、因为采购文件中：

> 表格是高风险区域。

---

# 二百六十二、还可以单独看

```text
Cross-page Clause Accuracy
```

因为：

> 跨页很容易出错。

---

# 二百六十三、这就是 Slice Evaluation

第一课学过的思维又回来。

---

# 二百六十四、数据工程同样不能只看平均分

一个结构模型：

> 普通段落 99%。

但：

> 评分表只有 60%。

对 ProcurementAI：

> 仍然可能不能用。

---

# 二百六十五、现在设计结构 Warning

可以有：

```text
HEADING_LEVEL_AMBIGUOUS

NUMBERING_INCONSISTENT

CROSS_PAGE_CLAUSE

TABLE_CLAUSE_UNCERTAIN

ORPHAN_SUBCLAUSE

PARENT_MISSING

OVERLONG_CLAUSE
```

---

# 二百六十六、什么叫 Orphan Subclause？

比如：

```text
（2）注册资本不低于500万元
```

但系统找不到：

```text
（1）
```

也找不到 Parent。

---

# 二百六十七、这可能说明：

- 上一页漏解析；
- Parent 被误删；
- 编号本来就错；
- Clause Boundary 错。

应该：

> 标 Warning。

---

# 二百六十八、什么叫 Overlong Clause？

如果系统切出：

```text
18,000字
```

一个 Clause，

大概率：

> 切分失败。

---

# 二百六十九、当然不是说超过某字数一定错。

而是：

> 异常检测信号。

---

# 二百七十、同理 Extremely Short Clause

比如只有：

```text
“如下：”
```

也可能只是：

> Parent Lead Text。

不应该当独立业务 Clause。

---

# 二百七十一、所以结构质量检查可以利用

```text
长度分布
编号模式
父子关系
Section一致性
```

自动发现异常。

---

# 二百七十二、这其实越来越像编译器

原始文件：

> 像源代码。

Parser：

> 读字符和布局。

Structure Recovery：

> 建 AST。

---

# 二百七十三、AST 是什么？

Abstract Syntax Tree。

不用记术语。

只要知道：

> 把平面的符号恢复成有层级的结构树。

---

# 二百七十四、政府采购文档也可以有自己的“文档 AST”

例如：

```text
Document
├── Chapter
│   ├── Section
│   │   ├── Clause
│   │   └── Clause
│   └── Section
└── Appendix
```

---

# 二百七十五、这个类比很漂亮

因为以后很多操作：

> 都可以在树上完成。

---

# 二百七十六、比如删除整段页眉

在 Block 层。

---

# 二百七十七、比如找全部技术要求

查：

```text
section_type = technical_requirement
```

---

# 二百七十八、比如取某 Clause 的 Parent

直接：

> 向树上走一层。

---

# 二百七十九、比从一整串字符串里：

> 正则乱找

可靠得多。

---

# 二百八十、现在看一个复杂案例

原文：

```text
第三章 采购需求

一、项目概况
……

二、服务要求

（一）人员要求

1. 项目经理应具有……
2. 项目团队不少于10人。

（二）响应要求

供应商应提供7×24小时服务，并满足以下要求：
1）普通故障30分钟内响应；
2）重大故障2小时内到场；
3）每季度开展一次巡检。
```

---

# 二百八十一、文档树应该大致是

```text
第三章 采购需求
│
├── 一、项目概况
│
└── 二、服务要求
     │
     ├── （一）人员要求
     │     ├── Clause 1
     │     └── Clause 2
     │
     └── （二）响应要求
           └── Parent Clause
                 ├── Subclause 1
                 ├── Subclause 2
                 └── Subclause 3
```

---

# 二百八十二、这就是我们真正想恢复的东西。

---

# 二百八十三、如果只是 Plain Text

你只有：

> 一串字。

---

# 二百八十四、有 Tree 后

你知道：

```text
重大故障2小时内到场
```

属于：

```text
采购需求
→ 服务要求
→ 响应要求
```

---

# 二百八十五、这就是 Structural Semantics

结构本身：

> 就带语义。

---

# 二百八十六、再看一个评分表案例

```text
第四章 评标办法

商务评分表

项目经验 | 10分 | 每个同类项目2分
本地服务 | 5分  | 本市有服务机构得5分
人员资质 | 5分  | 每名高级工程师1分
```

---

# 二百八十七、Structure Recovery 后最好不是：

```text
10分
5分
5分
```

---

# 二百八十八、而是：

```text
评分项1
name = 项目经验
score = 10
rule = 每个同类项目2分
```

---

# 二百八十九、

```text
评分项2
name = 本地服务
score = 5
rule = 本市有服务机构得5分
```

---

# 二百九十、然后每一个评分项：

> 都可以派生为 Clause。

---

# 二百九十一、未来模型审查：

```text
risk_type = scoring_rule
```

就非常自然。

---

# 二百九十二、所以表格恢复和 Clause Segmentation

要协同。

但依然建议：

> 先保留 Table Structure，

再派生 Clause。

---

# 二百九十三、现在讲一个常见错误

# Flatten First

有人会：

```text
所有表格
↓
转成Markdown字符串
↓
以后只保存字符串
```

---

# 二百九十四、这样方便喂 LLM。

但代价是：

> Row / Cell 原始关系可能丢失。

---

# 二百九十五、更好的方法：

```text
Structured Table
作为Master
```

然后生成：

```text
Markdown View
```

供模型使用。

---

# 二百九十六、这再次是：

```text
Master Representation
>
Task Representation
```

---

# 二百九十七、现在讲文件里的“注释”

比如：

```text
注：
1. 本项仅适用于……
2. 如为联合体……
```

这些是不是 Clause？

---

# 二百九十八、答案：

> 有时是。

因为“注”可能改变：

> 上面规则的适用范围。

---

# 二百九十九、所以不能简单把：

```text
注：
```

都当无关文本。

---

# 三百、需要判断它是：

```text
explanatory_note
```

还是：

> 真正具有约束意义的条件。

---

# 三百零一、所以结构类型还可以包括

```text
note
remark
footnote
```

---

# 三百零二、尤其表格脚注

例如：

> “以上证书须在有效期内，否则不得分。”

虽然只是表格下面一行小字。

但业务上：

> 非常重要。

---

# 三百零三、如果 Parser 或 Structure Recovery 把它当普通 Footer 删除

就出大问题。

---

# 三百零四、所以“看起来像脚注”

不等于：

> 无业务意义。

要区分：

```text
页面Footer
```

和：

```text
业务Footnote
```

---

# 三百零五、这也是为什么仅靠位置：

> 不够。

还需要内容语义。

---

# 三百零六、现在看“合同条款”

合同草案可能有：

```text
第十二条 违约责任
12.1 ...
12.2 ...
12.3 ...
```

结构非常像法规。

Clause Segmentation：

> 也可以沿同一框架处理。

---

# 三百零七、所以今天学的不是：

> 只适用于招标文件的技巧。

而是一套：

# Hierarchical Document Parsing

通用框架。

---

# 三百零八、未来法规 RAG 也会用

例如：

```text
法律
↓
章
↓
节
↓
条
↓
款
↓
项
```

---

# 三百零九、所以第四课第 3 阶段

其实也在为第 6 课 RAG：

> 提前打地基。

---

# 三百一十、现在讨论一条 Clause 是否需要保留原始编号

答案：

> 强烈建议保留。

比如：

```text
raw_clause_number = "（三）"
```

---

# 三百一十一、为什么？

用户以后问：

> “第三章第二节第（三）项为什么有风险？”

系统可以：

> 精确对应。

---

# 三百一十二、法律和采购工作非常重视

# Citation / Localization

也就是：

> 能不能定位回原文。

---

# 三百一十三、所以 Clause 应该尽量保存：

```text
page
section_path
raw_number
source_blocks
```

---

# 三百一十四、如果来自表格：

```text
table_caption
row_label
column_labels
```

也应该尽量保留。

---

# 三百一十五、这会让最终审查报告

从：

> “AI 说有风险”

升级为：

> “第三章采购需求 → 供应商资格条件 → 第（二）项存在潜在风险。”

这才是专业系统。

---

# 三百一十六、现在看数据切分的提前收益

同一项目里：

> 很多 Clause。

它们全部有：

```text
project_id
```

以及：

```text
document_id
```

---

# 三百一十七、第 6 阶段切数据时

就可以：

```text
Group by Project
```

而不是：

> 按 Clause 行随机切。

---

# 三百一十八、如果 Section / Clause 来源丢了

之后想修复：

> 非常难。

所以今天保存 Hierarchy：

> 其实也在帮后面防数据泄漏。

---

# 三百一十九、现在设计一个 Clause Quality Status

例如：

```text
auto_segmented
```

---

# 三百二十、

```text
human_verified
```

---

# 三百二十一、

```text
structure_uncertain
```

---

# 三百二十二、为什么值得有？

因为自动切出的 Clause：

> 并不都同样可信。

---

# 三百二十三、未来 Gold Set

可以优先使用：

```text
human_verified
```

---

# 三百二十四、大规模预训练数据

可能允许：

```text
auto_segmented
```

---

# 三百二十五、再次强调：

> 数据质量是分层的。

不需要所有数据：

> 用最高成本处理。

---

# 三百二十六、现在做一次完整的 Structure Pipeline

总图：

```text
ParsedDocument
      │
      ▼
过滤Layout噪声标记
      │
      ▼
Heading Candidate Detection
      │
      ▼
Heading Level Inference
      │
      ▼
Section Tree Construction
      │
      ▼
Section Type Normalization
      │
      ▼
Paragraph / List / Table Analysis
      │
      ▼
Clause Boundary Detection
      │
      ▼
Parent / Child Clause Recovery
      │
      ▼
Cross-page Merge
      │
      ▼
Clause Quality Check
      │
      ▼
ClauseUnit_V0.1
```

这就是这一阶段的工程主线。

---

# 三百二十七、再把三个层级放在一起

```text
L1 Parsed Block
```

回答：

> 页面上有什么内容？

---

# 三百二十八、

```text
L2 Document Structure
```

回答：

> 这些内容属于哪一章、哪一节？

---

# 三百二十九、

```text
L3 Clause Unit
```

回答：

> 哪个最小业务要求应该成为训练/审查对象？

---

# 三百三十、然后第 4 层才是

```text
L4 Annotation
```

回答：

> 这个 Clause 有没有风险？

---

# 三百三十一、层层分开

最大的好处：

> 出错能定位。

---

# 三百三十二、例如某条模型预测错了

你可以检查：

```text
模型错？
```

如果不是：

```text
Label错？
```

再不是：

```text
Clause切错？
```

再不是：

```text
Section归错？
```

再不是：

```text
Parser错？
```

---

# 三百三十三、这就是：

# Debuggable Data Pipeline

可调试的数据流水线。

---

# 三百三十四、对专业 AI 项目特别重要

因为很多所谓：

> 模型错误

其实是：

> 数据工程错误。

---

# 三百三十五、本阶段最容易犯的 12 个错误

**错误 1：**

> 句号就是 Clause 边界。

错。

**错误 2：**

> Paragraph 就等于 Clause。

错。

**错误 3：**

> Block 就等于 Clause。

错。

**错误 4：**

> 页尾就是 Clause 结束。

错。

**错误 5：**

> 标题字号大就一定是 Heading。

错。

**错误 6：**

> 有编号就一定是新 Clause。

错。

可能是子项。

**错误 7：**

> 表格转成全文字符串以后结构就不重要了。

错。

**错误 8：**

> Section Type 就是 Risk Type。

错。

**错误 9：**

> Clause 越短越适合训练。

错。

**错误 10：**

> Clause 越长信息越完整，所以越好。

也错。

**错误 11：**

> 自动结构恢复必须强行给每个地方一个确定答案。

错。

允许 Warning / Unknown。

**错误 12：**

> 只保留最终 Clause 文本就够。

不够。

还需要：

> Hierarchy + Provenance。

---

# 三百三十六、本阶段最重要的 5 个“≠”

```text
Sentence
≠
Clause
```

```text
Paragraph
≠
Clause
```

```text
Block
≠
Clause
```

```text
Page Boundary
≠
Clause Boundary
```

```text
Section Type
≠
Risk Label
```

如果这五个不再混，

本阶段已经成功了一半。

---

# 三百三十七、再记一个最重要的“=”

\[
\boxed{
ClauseUnit
=
BusinessAtomicRequirement
+
StructuralContext
+
SourceProvenance
}
\]

翻译成人话：

> **一条 Clause 不只是那一句文字，而是一个尽量完整的业务要求，加上它属于哪一章哪一节，以及它能回到原文件哪里。**

---

# 三百三十八、现在看 Stage 1～3 的完整关系

```text
第四课 · Stage 1
Task Schema
“未来一条训练样本应该是什么？”

             ↓

第四课 · Stage 2
ParsedDocument
“原文件怎样恢复成可信机器文本？”

             ↓

第四课 · Stage 3
ClauseUnit
“可信文本怎样恢复成业务结构和条款？”
```

现在数据已经第一次从：

```text
文件
```

走到：

```text
业务单元
```

---

# 三百三十九、这一步的重要性非常大

因为从下一阶段开始，

我们才能真正讨论：

> 哪些东西应该删？

> 哪些东西应该规范化？

> 数字、空格、标点到底能不能改？

也就是：

# Cleaning

---

# 三百四十、第 3 阶段掌握测试

如果现在不看前文，你能够自己解释下面这些问题，本阶段就真正掌握：

> 为什么正确提取文字以后仍然需要 Structure Recovery？

> 为什么文档结构更像一棵树，而不是一串字符串？

> Heading Detection 为什么不能只靠字号？

> 编号体系为什么对政府采购文档特别重要？

> Section Number 和 Clause Number 为什么不同？

> 什么叫 Parent-Child Relation？

> `section_path` 为什么对模型理解和产品定位都重要？

> Clause 为什么不能简单定义成一句话？

> Sentence、Paragraph、Block、Clause 四者有什么区别？

> 什么叫 Business Atomicity？

> 为什么一条 Clause 可能由多个 Block 组成？

> 为什么一个 Block 也可能包含多个 Clause？

> 为什么 Parent Clause 和 Sub-Clause 最好都保留？

> 为什么 Page Boundary 不能作为 Clause Boundary？

> 跨页 Clause 怎样判断连续性？

> 为什么表格的一行可以成为一个 Clause？

> 为什么评分项需要把“评分名称 + 分值 + 规则”一起保存？

> 为什么 Table Master Structure 不应该过早 flatten？

> `section_type` 和 `risk_type` 为什么不能混？

> 为什么 Raw Section Title 和 Normalized Section Type 最好同时保留？

> Clause 为什么要保存 source_block_ids？

> 为什么 Clause ID 需要稳定？

> 为什么编号不连续不代表结构一定错误？

> 为什么原始编号应该保留，而不是自动偷偷纠正？

> 什么叫 Over-segmentation？

> 什么叫 Under-segmentation？

> 为什么 Hierarchical Segmentation 比暴力切段更适合采购文件？

> Minimal Context 为什么可以由 Section Tree 帮助构造？

> Structure Recovery 为什么同时服务 SFT、RAG、评测和产品 UI？

> 为什么结构解析也需要自己的 Gold Set 和 Benchmark？

> 为什么 Gold 数据更适合使用人工确认过的 ClauseUnit？

如果这些你都能讲清楚：

\[
\boxed{
第四课第3阶段真正掌握
}
\]

---

# 三百四十一、本阶段最终只记一句话

> **Clause Segmentation 不是把文本按句号切开，而是把一个采购文档重新恢复成“章—节—条款”的业务树：让每一条 Clause 既是尽量完整的最小业务要求，又保留它的父级章节、必要上下文以及回到原文件页码和 Block 的来源路径。**

最后把整个阶段压成一张图：

```text
                 ParsedDocument
                       │
                       ▼
                Layout Blocks
                       │
                       ▼
              Heading Detection
                       │
                       ▼
                Section Tree
             ┌─────────┴─────────┐
             ▼                   ▼
       Section Type         Parent / Child
             │                   │
             └─────────┬─────────┘
                       ▼
              Clause Segmentation
                       │
              ┌────────┼────────┐
              ▼        ▼        ▼
           Paragraph  List    Table Row
              │        │        │
              └────────┼────────┘
                       ▼
               Parent / Sub-Clause
                       │
                       ▼
                 ClauseUnit_V0.1
                       │
            ┌──────────┼──────────┐
            ▼          ▼          ▼
           SFT        RAG       Evaluation
```

---

# 下一阶段：第四课 · 第 4 阶段
## 数据清洗与规范化——为什么“看起来更干净”不一定代表“数据更正确”？哪些东西可以删，哪些字符绝对不能乱改？

第 4 阶段我们会第一次真正做：

# Cleaning

但重点绝不是：

> 多写几个 `.replace()`。

我们会专门解决一个很危险的问题：

```text
清洗
≠
把文本改得漂亮
```

比如：

```text
500 万元
```

能不能自动改成：

```text
500万元
```

通常问题不大。

但：

```text
不得低于500万元
```

如果清洗程序误删：

```text
不得
```

整个语义直接翻转。

下一阶段我们会建立：

```text
Raw Text
↓
Normalized Text
```

之间的安全边界，并拆清：

**空格、Unicode、全半角、页码、重复 Header/Footer、乱码、OCR 噪声、数字、单位、日期、编号、否定词、表格内容以及规范化日志应该怎样处理。**

最终得到：

# `CleanClause_V0.1`

也就是第一次把 `ClauseUnit_V0.1` 变成真正可以进入后续去重、切分和标注流程的高质量文本单元。

---

<!-- LESSON 04 STAGE 03 END -->


<!-- LESSON 04 STAGE 04 START -->

# 第四课 · 第 4 阶段：数据清洗与规范化
## 为什么“看起来更干净”不一定代表“数据更正确”？哪些东西可以删，哪些字符绝对不能乱改？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Cleaning ≠ Rewriting 清洗不是改写原文**
2. **原始文本必须保留， Normalized Text 应该是派生版本**
3. **可以统一“表现形式”， 不能擅自统一“业务含义”**
4. **数字、单位、否定词、比较符号、日期、编号 都属于高风险信息**
5. **自动修复必须可追踪、可回滚、可审计**
6. **不确定的时候， 宁可标 Warning，也不要偷偷猜**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Raw Document` | 原始文档：未经结构化处理的采购文件源材料 |
| `Normalization` | 规范化：稳定中间激活与训练过程 |
| `OCR` | OCR：把扫描图像中的文字转换成机器可读文本 |
| `Block` | 版面块：文档解析后保留布局和位置的基本块 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Value` | Value/V：被注意力权重实际汇聚的内容向量 |
| `Recovery` | 恢复：工具失败或中断后安全重试、降级和继续 |
| `Tokenizer` | 分词器：文本与 Token ID 之间的编码/解码组件 |
| `Layout` | 版面结构：文字块、表格、列、坐标和阅读顺序信息 |
| `Transformer` | Transformer：以注意力和前馈网络为核心的序列架构 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |

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

第三阶段结束以后，我们已经完成了一件非常关键的事：

```text
Raw Document
      ↓
ParsedDocument_V0.1
      ↓
Section Tree
      ↓
ClauseUnit_V0.1
```

也就是说，现在机器已经不只是拿到一堆 PDF 字符，而是开始知道：

```text
这句话来自哪个项目
来自哪份文件
属于哪一章
属于哪一节
是不是一条完整 Clause
原文在哪一页
由哪些 Block 构成
```

接下来很多团队会非常自然地做一件事：

> “现在文本有了，我们清洗一下吧。”

然后开始：

```python
text = text.replace(" ", "")
text = text.replace("\n", "")
text = text.replace("\t", "")
text = text.strip()
```

再加几十条正则。

最后数据看起来非常漂亮。

但这里藏着第四课里一个非常危险的问题：

# “更干净”不一定等于“更正确”。

例如原文是：

```text
投标报价不得超过 500 万元。
```

清理成：

```text
投标报价不得超过500万元。
```

通常没什么问题。

但如果某个清洗规则把：

```text
不得
```

误删，变成：

```text
投标报价超过500万元。
```

这已经不是格式错误了。

而是：

> **语义被反转。**

所以第四阶段真正要建立的不是一堆 `.replace()`。

而是：

# 一套“安全清洗”的边界意识。

---

# 一、本阶段真正要解决的一个核心问题

今天只解决：

> **怎样在不改变采购文件原始业务含义的前提下，把 `ClauseUnit_V0.1` 变成适合去重、标注、训练、检索和评测的规范文本？**

也就是：

```text
ClauseUnit_V0.1
      ↓
Safe Normalization
      ↓
CleanClause_V0.1
```

这里最重要的词不是：

> Clean。

而是：

# Safe

---

# 二、先建立今天最重要的 6 个核心心智模型

```text
① Cleaning ≠ Rewriting
   清洗不是改写原文

② 原始文本必须保留，
   Normalized Text 应该是派生版本

③ 可以统一“表现形式”，
   不能擅自统一“业务含义”

④ 数字、单位、否定词、比较符号、日期、编号
   都属于高风险信息

⑤ 自动修复必须可追踪、可回滚、可审计

⑥ 不确定的时候，
   宁可标 Warning，也不要偷偷猜
```

如果这六句话真正理解，

第四阶段最重要的东西就掌握了一半。

---

# 三、先把 Cleaning 和 Normalization 分开

这两个词经常混着用。

可以先这样理解。

# Cleaning

主要解决：

> 明显噪声。

例如：

```text
重复页眉
重复页脚
乱码控制字符
OCR产生的异常空白
无意义的页面装饰
```

---

# 四、Normalization

主要解决：

> 同一个东西有很多不同写法。

例如：

```text
５００万元
```

和：

```text
500万元
```

可以规范成：

```text
500万元
```

因为：

> 全角数字和半角数字在这里通常只是表现形式不同。

---

# 五、但这两个操作都不能变成

# Semantic Editing

例如：

```text
注册资本不低于500万元
```

不能为了“更自然”改成：

```text
企业规模应达到较高水平
```

这已经不是 Normalization。

而是：

> 改写。

---

# 六、所以今天第一个非常重要的边界

\[
\boxed{
Normalization
\neq
Paraphrasing
}
\]

我们的目标不是让文字：

> 更漂亮。

而是让文字：

> **机器更容易稳定处理，同时保持原始语义。**

---

# 七、最推荐的数据结构是什么？

永远不要只有：

```text
clean_text
```

最好至少保留：

```text
raw_text
```

和：

```text
normalized_text
```

例如：

```json
{
  "raw_text": "供应商注册资本不得低于５００ 万元。",
  "normalized_text": "供应商注册资本不得低于500万元。"
}
```

---

# 八、为什么一定要保留 Raw？

因为半年后如果有人问：

> “500 万元是不是原文件真的这么写？”

你可以直接检查：

```text
raw_text
```

---

# 九、如果只保存 Normalized Text

你看到：

```text
500万元
```

却不知道：

> 原来是不是 `５００ 万元`

甚至不知道：

> 清洗器有没有把别的东西改错。

---

# 十、所以推荐的基本结构是

```text
Original Source
      ↓
Raw Parsed Text
      ↓
Normalized Text
      ↓
Training / Retrieval View
```

而不是：

```text
Original
↓
疯狂replace
↓
覆盖原文
```

---

# 十一、这和照片修图完全一样

你不会因为：

> 调亮了照片

就把：

> RAW 原片删掉。

数据工程也一样。

---

# 十二、今天第二个核心心智模型

# 派生，不覆盖

可以记成：

\[
\boxed{
Raw
\rightarrow
Derived
}
\]

而不是：

\[
\boxed{
Raw
\rightarrow
Overwrite
}
\]

---

# 十三、现在开始处理最基础的问题：Whitespace

空格。

政府采购解析结果里可能出现：

```text
供应商    应    具有
```

或者：

```text
供应商应具 有独立承担民事责任的能力
```

---

# 十四、这些空格可能来自

```text
PDF坐标
OCR
表格
中英文排版
人为输入
```

所以空格清洗：

> 不能只写一句 `replace(" ", "")`。

---

# 十五、为什么全部删除空格很危险？

例如：

```text
Windows Server 2025
```

删掉以后：

```text
WindowsServer2025
```

Tokenizer 和检索结果可能发生变化。

---

# 十六、再比如型号

```text
ABC 1000 Pro
```

变成：

```text
ABC1000Pro
```

可能已经不是：

> 原始型号写法。

---

# 十七、又例如英文法规、技术参数

```text
SQL Server
```

空格本身：

> 有意义。

---

# 十八、所以更合理的方法是

针对：

# 异常空格

做规则。

而不是：

> 删除所有空格。

---

# 十九、例如中文字符之间

```text
供 应 商
```

如果确认这是 OCR 导致的：

> 单字间空格，

可以安全考虑合并。

---

# 二十、但：

```text
Microsoft SQL Server
```

不能按同样规则处理。

---

# 二十一、所以空格 Normalization 需要理解

```text
字符类型
+
邻近字符
+
语言模式
```

而不是：

> 全局删除。

---

# 二十二、现在看换行

第三阶段已经知道：

```text
Visual Line Break
≠
Semantic Boundary
```

所以：

```text
供应商不得以不合理条件对其他供
应商实行差别待遇。
```

应该恢复成：

```text
供应商不得以不合理条件对其他供应商实行差别待遇。
```

---

# 二十三、但不能把所有换行都删除

例如：

```text
1. 资格条件
2. 技术要求
3. 商务要求
```

如果合成：

```text
1.资格条件2.技术要求3.商务要求
```

结构反而坏了。

---

# 二十四、所以要区分

```text
layout_line_break
```

和：

```text
semantic_break
```

---

# 二十五、这也是为什么 Cleaning 最好发生在

# Structure Recovery 之后

因为第三阶段已经告诉我们：

> 哪些 Block 属于同一个 Clause。

---

# 二十六、如果在结构恢复之前就疯狂删除换行

你可能把：

> 原本有价值的版式信号

提前毁掉。

---

# 二十七、这就是课程为什么设计成

```text
Stage 2 Parsing
      ↓
Stage 3 Structure
      ↓
Stage 4 Cleaning
```

而不是反过来。

---

# 二十八、现在进入 Unicode

Unicode 是什么不用深入。

只要理解：

> 同样看起来的字符，计算机内部可能有不同编码表示。

---

# 二十九、例如：

```text
ＡＢＣ１２３
```

这是全角。

而：

```text
ABC123
```

是半角。

---

# 三十、对很多自然语言任务来说

把：

```text
ＡＢＣ１２３
```

规范成：

```text
ABC123
```

通常是合理的。

---

# 三十一、因为业务含义一般没有变化

只是：

> 字符表现形式不同。

---

# 三十二、这种操作属于

# Unicode Normalization

---

# 三十三、但 Unicode Normalization 也不能闭眼做

例如某些：

- 数学符号；
- 法律符号；
- 特殊单位；
- 技术型号；

不同字符：

> 可能真的代表不同含义。

---

# 三十四、比如

```text
≤
```

和：

```text
<
```

绝对不能认为：

> 差不多。

---

# 三十五、因为：

```text
≤ 10
```

表示：

> 可以等于 10。

而：

```text
< 10
```

表示：

> 不可以等于 10。

---

# 三十六、对于技术参数

这一点尤其危险。

例如：

```text
响应时间≤2小时
```

和：

```text
响应时间<2小时
```

并不是完全相同要求。

---

# 三十七、再比如：

```text
≥
```

和：

```text
>
```

也不能随便互换。

---

# 三十八、所以比较运算符属于

# High-risk Symbols

高风险符号。

---

# 三十九、采购数据中建议特别保护的符号包括：

```text
>
<
≥
≤
=
≠
%
‰
±
～
-
+
/
×
```

它们很多：

> 直接改变条件。

---

# 四十、例如

```text
5±0.5mm
```

如果清洗成：

```text
50.5mm
```

那就是灾难。

---

# 四十一、再比如：

```text
1:1000
```

不能随便变成：

```text
11000
```

---

# 四十二、所以第三个核心心智模型：

> **标点不总是装饰。**

技术文档里的符号：

> 经常就是数据本身。

---

# 四十三、现在看数字

采购文档中数字极其重要。

例如：

```text
500万元
3年
2小时
5分
10%
20人
3个项目
```

这些很多时候：

> 就是风险判断的核心。

---

# 四十四、所以数字 Normalization 必须特别保守

例如：

```text
５００
```

转成：

```text
500
```

一般安全。

---

# 四十五、但是：

```text
5OO
```

这里到底是：

```text
500
```

还是字母：

```text
O
```

就不能直接猜。

---

# 四十六、尤其 OCR 常见：

```text
0 ↔ O

1 ↔ I

5 ↔ S

8 ↔ B
```

如果自动修：

> 可能修对。

也可能：

> 创造假数据。

---

# 四十七、例如型号：

```text
ABO-100
```

里面的 `O`：

> 可能真的就是字母 O。

你如果改成：

```text
AB0-100
```

反而错了。

---

# 四十八、所以 OCR Correction 应分两类

```text
High-confidence Correction
```

和：

```text
Ambiguous Correction
```

---

# 四十九、例如

```text
５００万元
```

全角→半角：

> 高置信度。

---

# 五十、而：

```text
S00万元
```

猜成：

```text
500万元
```

应该：

> 谨慎得多。

---

# 五十一、如果上下文非常明确：

```text
项目预算为S00万元
```

机器可以产生：

```text
correction_candidate = "500万元"
```

但最好不要：

> 静默覆盖。

---

# 五十二、而是记录：

```text
raw:
S00万元

normalized:
500万元

correction_type:
ocr_candidate

confidence:
0.82
```

甚至：

```text
needs_review = true
```

---

# 五十三、这就是第四个核心心智模型：

# 自动修复要有证据等级

不是：

> “我觉得像错字，所以改了。”

---

# 五十四、特别是金额

例如：

```text
500万元
```

和：

```text
5000万元
```

只差一个 0。

但业务意义：

> 差一个数量级。

---

# 五十五、所以金额应该视为：

# Critical Field

关键字段。

---

# 五十六、类似还有：

```text
分值
百分比
日期
年限
数量
人数
距离
响应时间
业绩数量
注册资本
预算金额
```

这些字段：

> 都值得更严格保护。

---

# 五十七、现在看单位

例如：

```text
500 万元
```

变成：

```text
500万元
```

通常安全。

---

# 五十八、但：

```text
500元
```

和：

```text
500万元
```

绝对不能混。

---

# 五十九、所以不要做一种荒唐 Normalization：

```text
所有金额
统一变成数字
```

例如只保存：

```text
500
```

因为：

> 单位丢了。

---

# 六十、正确方式可以是

保留文本：

```text
500万元
```

同时结构化派生：

```json
{
  "amount_value": 500,
  "amount_unit": "万元"
}
```

---

# 六十一、甚至进一步：

```json
{
  "amount_cny": 5000000
}
```

但注意：

> 这是结构化派生字段。

不是修改原文。

---

# 六十二、原文仍然保留：

```text
500万元
```

---

# 六十三、这是一个非常重要的数据工程习惯

\[
\boxed{
NormalizeByAddingStructure
>
NormalizeByDestroyingText
}
\]

中文：

> **能通过增加结构化字段解决的问题，不要靠破坏原文解决。**

---

# 六十四、比如日期

原文：

```text
2026年9月15日
```

我们可以结构化成：

```text
2026-09-15
```

但不需要删掉原文本身。

---

# 六十五、可以保存：

```json
{
  "date_raw": "2026年9月15日",
  "date_iso": "2026-09-15"
}
```

---

# 六十六、这样既方便机器排序，

又可以：

> 精确回到原文。

---

# 六十七、但日期也有危险情况

例如：

```text
2026年9月
```

不能自动补成：

```text
2026-09-01
```

因为原文：

> 根本没有说 1 日。

---

# 六十八、这叫：

# Information Fabrication

制造原文不存在的信息。

---

# 六十九、所以 Normalization 可以

> 统一已有信息。

不能：

> 补造未知信息。

---

# 七十、再看一个日期

```text
9月15日前
```

不要只结构化成：

```text
2026-09-15
```

因为你会丢掉：

```text
前
```

也就是：

> Deadline Semantics。

---

# 七十一、所以业务语义字段可能是：

```text
date = 2026-09-15
operator = before_or_on
```

而不是：

> 只剩日期。

---

# 七十二、这和比较符号完全一样

文本：

```text
不少于3年
```

可以结构化成：

```text
operator = >=
value = 3
unit = year
```

但原文：

> 仍保留。

---

# 七十三、这类结构化会对后面规则引擎非常有价值

比如：

```text
registration_years >= 5
```

可以直接进入：

> 规则检查。

---

# 七十四、但是注意：

# Extraction ≠ Cleaning

抽取：

```text
operator/value/unit
```

属于：

> 更高层的数据结构化。

今天我们只是提前建立正确思路。

---

# 七十五、现在进入极其危险的一类字符

# Negation

否定词。

政府采购中常见：

```text
不
不得
不应
不可
无需
不得超过
不得低于
不接受
不允许
禁止
未
无
```

---

# 七十六、这些词绝对不能当“停用词”

普通 NLP 时代经常有人做：

```text
Stopword Removal
```

把：

```text
的
了
和
不
```

之类删掉。

---

# 七十七、如果把：

```text
不
```

删掉：

```text
本项目不接受联合体
```

变成：

```text
本项目接受联合体
```

意思直接反转。

---

# 七十八、所以对于我们的 ProcurementAI：

# 不建议做传统停用词删除

至少：

> 绝不能把否定词机械删除。

---

# 七十九、事实上现代 Transformer

通常也：

> 不需要把自然语言预先删成关键词袋。

---

# 八十、模型真正需要的是：

> 完整语义。

不是：

```text
项目
接受
联合体
```

这种残缺关键词。

---

# 八十一、所以第五个核心心智模型

\[
\boxed{
LLM Cleaning
\neq
传统Bag-of-Words预处理
}
\]

---

# 八十二、我们不会做类似：

```text
去停用词
词干化
删标点
只留关键词
```

这种传统文本分类式暴力处理。

---

# 八十三、因为对 LLM 来说：

> 语法、关系、否定、条件、修饰范围

都很重要。

---

# 八十四、现在看标点

有人会想：

> “标点都是噪声，删掉能省 Token。”

很危险。

---

# 八十五、例如：

```text
A、B不得参加。
```

和：

```text
A不得参加，B可以参加。
```

标点结构：

> 帮助表达关系。

---

# 八十六、再比如：

```text
供应商应满足：
1. 条件A；
2. 条件B；
3. 条件C。
```

如果全部删掉：

```text
供应商应满足条件A条件B条件C
```

层级：

> 变差。

---

# 八十七、所以 Normalization 可以统一

```text
；;
```

这类视觉变体。

但不能：

> 把标点全部删掉。

---

# 八十八、现在看中文引号

可能有：

```text
“政府采购”
```

和：

```text
"政府采购"
```

需要不需要统一？

---

# 八十九、如果只是训练普通语言模型：

> 可以考虑统一。

但如果原始引用格式本身：

> 有法律引用意义，

也可以保留。

---

# 九十、更稳妥的方法依然是：

```text
raw_text
+
normalized_text
```

---

# 九十一、现在看括号

例如：

```text
（含）
```

和：

```text
（不含）
```

括号内容：

> 绝对不能因为觉得“像备注”就删。

---

# 九十二、例如：

```text
500万元以上（不含500万元）
```

如果清理掉括号：

```text
500万元以上
```

业务条件：

> 已经改变。

---

# 九十三、类似：

```text
3年以内（含3年）
```

和：

```text
3年以内（不含3年）
```

不能混。

---

# 九十四、因此括号里的内容可能是

# Semantic Modifier

语义修饰条件。

---

# 九十五、采购文本里建议默认策略：

> **括号内容保留，除非有非常明确证据它只是版式噪声。**

---

# 九十六、现在看编号

例如：

```text
（一）
```

```text
1.
```

```text
1）
```

要不要全部删掉？

---

# 九十七、第三阶段已经告诉我们：

编号：

> 本身包含结构信息。

所以 Master Layer：

> 不应该删。

---

# 九十八、训练 View 是否保留编号？

看任务。

例如：

```text
父Clause:
供应商应满足以下条件：

（一）……
（二）……
```

编号可以帮助模型理解：

> 子项关系。

---

# 九十九、所以通常建议：

> 在结构化 Clause View 中保留。

---

# 一百、但我们还可以单独结构化：

```text
raw_number = "（二）"
```

于是模型输入不一定：

> 必须依赖这个字符。

---

# 一百零一、这就是：

```text
Text
+
Metadata
```

一起服务不同用途。

---

# 一百零二、现在处理重复页眉页脚

第二阶段已经识别：

```text
header
footer
```

第四阶段终于可以真正：

> 从 Normalized Text View 中去除。

---

# 一百零三、注意：

不是删除 Raw Block。

而是：

```text
include_in_clean_view = false
```

或者：

```text
block_role = footer
```

---

# 一百零四、Raw Parsed Layer：

> 仍保留。

---

# 一百零五、比如：

```text
某某政府采购中心
第37页
```

如果确认是重复 Footer，

Normalized Clause：

> 不再包含。

---

# 一百零六、这叫

# Non-destructive Cleaning

非破坏性清洗。

---

# 一百零七、同样适用于网页模板

HTML 中：

```text
首页
登录
网站地图
版权信息
```

可以：

> 从 Content View 排除。

但原始网页抓取：

> 最好仍保留。

---

# 一百零八、现在看重复内容

有些 PDF 解析器会把同一文字抽两次。

例如：

```text
供应商应具有独立承担民事责任的能力。
供应商应具有独立承担民事责任的能力。
```

---

# 一百零九、是不是直接删一条？

不一定。

---

# 一百一十、如果两条来自：

> 同一个页面、同一个 bbox、相同内容，

很可能：

> Parser Duplicate。

---

# 一百一十一、但如果它们来自：

```text
资格条件
```

和：

```text
合同条款
```

只是碰巧内容一样，

这可能：

> 是真实重复。

---

# 一百一十二、两者不能混。

所以：

# Parsing Duplicate

和：

# Document Duplicate

是两个问题。

---

# 一百一十三、解析器产生的假重复

可以在 Cleaning 中处理。

---

# 一百一十四、真实文档里的重复 Clause

应该：

> 保留到第五阶段专门做去重判断。

---

# 一百一十五、这就是为什么第四课把

```text
Cleaning
```

和：

```text
Deduplication
```

拆成两个阶段。

---

# 一百一十六、Cleaning 只负责：

> 明显表现层噪声。

第五阶段才处理：

> 相同/近似业务内容。

---

# 一百一十七、现在看 OCR Noise

例如：

```text
供 应 商□□□应具备
```

其中：

```text
□□□
```

可能是无法识别字符。

---

# 一百一十八、是否直接删除？

危险。

因为这三个字符：

> 可能正好是关键内容。

---

# 一百一十九、例如真正原文可能是：

```text
供应商不得应……
```

虽然这个例子语法怪，但核心思想是：

> 你不知道丢的是什么。

---

# 一百二十、所以 Unknown Character 应该更像：

```text
<UNK_OCR>
```

或者：

> 保留替代符并加 Warning。

---

# 一百二十一、例如：

```json
{
  "normalized_text": "供应商□□□应具备……",
  "warnings": [
    "UNRESOLVED_OCR_GLYPH"
  ]
}
```

---

# 一百二十二、而不是：

```text
供应商应具备……
```

然后假装：

> 中间什么都没有。

---

# 一百二十三、这叫：

# Preserve Uncertainty

保留不确定性。

---

# 一百二十四、因为“缺数据”

和：

> “确定没有数据”

不是一回事。

---

# 一百二十五、这在专业 AI 系统中特别重要。

---

# 一百二十六、现在看错别字

假设招标文件原文真的写：

```text
供应商因提供相关证书。
```

可能作者本来想写：

```text
应提供
```

---

# 一百二十七、我们要不要帮它改？

默认：

> 不应该直接修改 Raw。

---

# 一百二十八、因为数据工程的任务不是：

> 替采购人润色文件。

---

# 一百二十九、可以做：

```text
suspected_typo = true
```

甚至提供：

```text
suggested_text
```

但原文：

> 必须保留。

---

# 一百三十、这和法律证据意识有关

以后用户问：

> “原文件到底写了什么？”

系统必须回答：

> 原文。

不能回答：

> 我们觉得作者应该这么写。

---

# 一百三十一、所以：

\[
\boxed{
SourceTruth
>
LinguisticBeauty
}
\]

---

# 一百三十二、现在看繁体与简体

例如：

```text
採購
```

和：

```text
采购
```

要不要统一？

---

# 一百三十三、对于大量中文检索，

可以考虑构建：

> 规范化搜索 View。

但不要直接：

> 删除原始文本。

---

# 一百三十四、因为某些正式文件来源：

> 字体和原文形式本身也有追溯意义。

---

# 一百三十五、所以可以：

```text
raw_text
```

保留原始。

同时：

```text
search_normalized_text
```

做简繁规范化。

---

# 一百三十六、这就出现一个很重要的概念

# Multiple Views

同一个 Clause：

> 可以有多个派生文本 View。

---

# 一百三十七、例如：

```text
raw_text
```

用于：

> 审计和追溯。

---

# 一百三十八、

```text
normalized_text
```

用于：

> SFT / Evaluation。

---

# 一百三十九、

```text
search_text
```

用于：

> BM25 / 检索。

---

# 一百四十、

```text
display_text
```

用于：

> 用户界面。

---

# 一百四十一、这四个 Text View

不一定：

> 完全一样。

---

# 一百四十二、这是一种非常成熟的数据系统思路

不要逼：

> 一个字符串同时满足所有任务。

---

# 一百四十三、比如 BM25 Search View

可能会做更多：

> 空格和 Unicode 统一。

---

# 一百四十四、而 Gold Evaluation View

可能：

> 更接近原文。

---

# 一百四十五、因此：

\[
\boxed{
OneSource
\rightarrow
MultipleSafeViews
}
\]

---

# 一百四十六、现在看标点统一

例如：

```text
,
```

和：

```text
，
```

是否统一成中文逗号？

可以。

但要先确认：

> 不影响技术表达。

---

# 一百四十七、例如 CSV 或型号：

```text
A,B,C
```

也许逗号就是：

> 数据格式的一部分。

---

# 一百四十八、所以不同 Section Type

甚至可以使用：

> 不同 Normalization Policy。

---

# 一百四十九、例如普通正文

可以更积极：

> 统一全半角标点。

---

# 一百五十、技术参数表

应该：

> 更保守。

---

# 一百五十一、评分表

尤其：

```text
数字
%
±
≤
≥
```

几乎：

> 原样保护。

---

# 一百五十二、这叫

# Context-sensitive Normalization

---

# 一百五十三、不是所有文本：

> 同一套 regex 打到底。

---

# 一百五十四、现在看表格中的空白单元格

例如：

| 一级指标 | 二级指标 | 分值 |
|---|---|---:|
| 技术 | 方案 | 10 |
|  | 人员 | 10 |

空白一级指标：

> 可能继承“技术”。

---

# 一百五十五、如果 Cleaning 阶段看到：

```text
empty
```

就删掉这一行，

那就出大问题。

---

# 一百五十六、空白：

> 不总是垃圾。

有时代表：

# Merged Cell Semantics

---

# 一百五十七、正确做法可能是结构化：

```text
raw_cell = ""
inherited_value = "技术"
```

而不是：

> 偷偷把原表改掉。

---

# 一百五十八、同样，

表格中的：

```text
—
```

可能表示：

- 无；
- 不适用；
- 横线装饰；
- 同上。

不能一刀切。

---

# 一百五十九、所以表格数据 Normalization：

> 要比普通正文更谨慎。

---

# 一百六十、现在讲电话号码、邮箱、联系人

采购文档经常包含：

```text
联系人
手机号
邮箱
地址
```

这些不是“噪声”。

但它们也不一定应该：

> 进入模型训练。

---

# 一百六十一、这属于：

# Privacy / Sensitive Data Filtering

严格说：

> 和 Cleaning 不完全一回事。

---

# 一百六十二、为什么要分开？

如果你把：

```text
138xxxxxx
```

删掉，

应该知道：

> 是出于隐私治理。

不是因为：

> 它解析错了。

---

# 一百六十三、所以建议分别记录：

```text
normalization_log
```

和：

```text
privacy_redaction_log
```

不要混。

---

# 一百六十四、例如：

```json
{
  "operation": "redact_phone",
  "reason": "privacy_policy"
}
```

而不是：

```text
cleaning
```

三个字带过。

---

# 一百六十五、这就是 Data Governance

> 每一次改变数据，都应该知道为什么。

---

# 一百六十六、现在进入非常重要的东西

# Normalization Log

如果 Clean Text 被修改过，

最好记录：

> 改了什么。

---

# 一百六十七、例如 Raw：

```text
供应商注册资本不得低于５００ 万元。
```

Clean：

```text
供应商注册资本不得低于500万元。
```

可以记录：

```json
[
  {
    "rule": "fullwidth_digit_to_ascii",
    "before": "５００",
    "after": "500"
  },
  {
    "rule": "remove_space_between_number_and_unit",
    "before": "500 万元",
    "after": "500万元"
  }
]
```

---

# 一百六十八、是不是每个字符修改都必须人工看？

当然不是。

日志：

> 机器自动产生。

---

# 一百六十九、为什么日志重要？

因为如果半年后发现：

```text
Normalization Rule 17
```

有 Bug，

可以直接查询：

> 哪些 Clause 用过 Rule 17。

---

# 一百七十、然后只重跑受影响数据。

---

# 一百七十一、如果没有日志，

你只能：

> 全库重跑，

甚至：

> 不知道哪些数据被改错。

---

# 一百七十二、所以 Normalization 也需要

# Data Lineage

---

# 一百七十三、第一阶段讲：

```text
Sample
↓
来源
```

第二阶段讲：

```text
Text
↓
Parser
```

第三阶段讲：

```text
Clause
↓
Source Blocks
```

第四阶段进一步：

```text
Normalized Text
↓
Normalization Operations
```

整条 Lineage 越来越完整。

---

# 一百七十四、这就是未来 `ProcurementDataset_V0.1`

真正有工程价值的原因。

不是只有：

> 文本和标签。

---

# 一百七十五、现在讨论 Idempotence

这是一个稍微工程一点的词。

不用怕。

它意思很简单。

如果文本：

```text
T
```

经过 Normalizer：

```text
N(T)
```

再跑一次：

```text
N(N(T))
```

结果最好仍然一样。

---

# 一百七十六、可以写成：

\[
\boxed{
N(N(x))=N(x)
}
\]

---

# 一百七十七、为什么？

如果第一次运行得到：

```text
500 万元
→
500万元
```

第二次又变成：

```text
500万元
→
5000000元
```

第三次：

```text
5000000元
→
5,000,000元
```

Pipeline：

> 每跑一次结果都不同。

非常难维护。

---

# 一百七十八、所以一个好的 Normalizer：

> **重复执行应该稳定。**

---

# 一百七十九、这就是今天极少数值得记住的工程公式之一：

\[
\boxed{
Normalize(Normalize(x))
=
Normalize(x)
}
\]

---

# 一百八十、这叫：

# Idempotent

幂等。

---

# 一百八十一、以后你会发现：

数据 Pipeline 很喜欢幂等。

因为：

> 可以安全重跑。

---

# 一百八十二、现在看 Normalization Version

今天：

```text
normalizer_v0.1
```

以后可能发现：

> 空格规则有问题。

升级：

```text
normalizer_v0.2
```

---

# 一百八十三、每条 CleanClause 最好知道：

```text
normalizer_version
```

---

# 一百八十四、否则：

100 万条数据里：

> 一半 v0.1，一半 v0.3，

没人知道。

---

# 一百八十五、所以版本字段至少包括：

```text
parser_version
structure_version
normalizer_version
schema_version
```

以后还会有：

```text
label_version
dataset_version
```

---

# 一百八十六、这一整套版本控制：

> 最终会在第 11 阶段正式串起来。

---

# 一百八十七、现在看一个完整清洗示例

Raw：

```text
第 37 页
某某市政府采购中心

（二）供应商注册资本不得低于５００ 万元，
且须在本 市连续经营不少于 5 年。

项目编号：ABC-2026-001
```

---

# 一百八十八、结构阶段已经知道：

```text
第37页
某某市政府采购中心
项目编号
```

属于：

> Header / Footer / Metadata。

---

# 一百八十九、于是 Clean Clause 可以变成：

```text
（二）供应商注册资本不得低于500万元，且须在本市连续经营不少于5年。
```

---

# 一百九十、发生了什么？

```text
重复页眉页脚
→ 从Clean View排除

５００
→ 500

500 万元
→ 500万元

本 市
→ 本市

5 年
→ 5年
```

---

# 一百九十一、但是没有做什么？

没有改：

```text
不得低于
```

没有改：

```text
且须
```

没有改：

```text
本市
```

没有把：

```text
不少于5年
```

改成：

```text
5年以上
```

---

# 一百九十二、最后那个特别重要

虽然：

```text
不少于5年
```

和：

```text
5年以上
```

日常理解非常接近。

但我们不应该在 Cleaning 中：

> 主动改写。

---

# 一百九十三、因为：

> Cleaning 的职责不是语言同义改写。

---

# 一百九十四、如果未来需要统一逻辑表达

可以额外结构化：

```text
operator = >=
value = 5
unit = year
```

而不是：

> 改原句。

---

# 一百九十五、再看一个有风险的例子

Raw：

```text
技术参数：CPU 主频≥3.0GHz，核心数不少于32核。
```

错误 Cleaning：

```text
技术参数CPU主频3.0GHz核心数32核
```

---

# 一百九十六、它删掉了：

```text
≥
```

和：

```text
不少于
```

于是：

> 约束关系丢失。

---

# 一百九十七、模型现在不知道：

```text
3.0
```

是：

- 等于；
- 至少；
- 不超过；
- 推荐值。

---

# 一百九十八、所以这种“清洗”

不是 Cleaning。

是：

# Information Destruction

---

# 一百九十九、再看评分案例

Raw：

```text
近三年每提供1个同类项目业绩得2分，最高得10分。
```

错误 Normalization：

```text
同类项目业绩2分10分
```

---

# 二百、这对关键词搜索：

> 也许还能凑合。

但对 LLM：

> 业务关系几乎被摧毁。

---

# 二百零一、所以我们从今天开始要坚定一个原则：

# LLM 需要完整语言关系

不是：

> 极限压缩的关键词。

---

# 二百零二、现在看数字中的千位分隔符

```text
5,000,000元
```

和：

```text
5000000元
```

是否统一？

可以考虑。

---

# 二百零三、但要先判断逗号是不是：

> 数字分隔符。

---

# 二百零四、例如：

```text
型号A,B,C
```

这里：

> 不是数字逗号。

---

# 二百零五、所以规则应该：

> 有 Pattern Context。

而不是：

```python
replace(",", "")
```

---

# 二百零六、再看小数点

```text
3.0GHz
```

绝对不能清成：

```text
30GHz
```

---

# 二百零七、扫描文档里：

```text
3．0
```

可能使用全角句点。

这个可以：

> 规范成 `3.0`。

但必须确认：

> 它位于数字之间。

---

# 二百零八、这叫局部规则

例如：

```text
数字 + 全角小数点 + 数字
→
数字 + "." + 数字
```

比：

> 全局把所有 `．` 变成 `.`

更安全。

---

# 二百零九、现在看百分号

```text
10％
```

可以规范：

```text
10%
```

---

# 二百一十、但：

```text
0.1
```

不能自动转成：

```text
10%
```

除非：

> 业务 Schema 明确知道这是比例字段。

---

# 二百一十一、为什么？

因为 `0.1`：

> 可能就是数值 0.1。

不是一定：

> 百分之十。

---

# 二百一十二、所以清洗器不能：

> 自作聪明。

---

# 二百一十三、现在看金额中文数字

```text
人民币伍佰万元整
```

要不要直接改成：

```text
500万元
```

不建议覆盖。

---

# 二百一十四、可以做结构化解析：

```text
amount_cny = 5000000
```

但：

```text
raw_text
```

继续保存：

```text
人民币伍佰万元整
```

---

# 二百一十五、这对于合同和金额审查特别重要。

---

# 二百一十六、现在看文件中的特殊空字符

例如：

```text
\u00A0
```

Non-breaking space。

人眼：

> 看起来就是空格。

---

# 二百一十七、还有：

```text
zero-width space
```

人眼：

> 完全看不见。

---

# 二百一十八、这些可能严重影响

```text
字符串比较
Hash
去重
关键词搜索
```

---

# 二百一十九、所以这类 Unicode 控制字符：

> 通常可以安全规范化。

---

# 二百二十、例如零宽空格

如果确认不承载语义：

> 可以删除。

---

# 二百二十一、这类操作属于典型

# Safe Normalization

---

# 二百二十二、和下面这些形成鲜明对比：

```text
删除“不得”
删除“以上”
删除“含”
修改数字
修改单位
修改比较符
```

这些属于：

# High-risk Normalization

---

# 二百二十三、于是我们可以第一次建立

# Normalization Risk Levels

概念上分三类。

---

# 二百二十四、Low Risk

例如：

```text
零宽空格
全角英文字母→半角
连续无意义空白
明确重复页脚
```

通常：

> 可自动处理。

---

# 二百二十五、Medium Risk

例如：

```text
OCR断行合并
中文字符间异常空格
表格单元格换行
```

需要：

> 上下文规则和质量检测。

---

# 二百二十六、High Risk

例如：

```text
数字修改
单位修复
否定词修复
比较符修复
法律条号修复
型号修复
```

最好：

> 不自动静默修改。

---

# 二百二十七、这张分类不是法律标准。

只是：

> 我们工程上的风险思维。

---

# 二百二十八、这种设计可以让 Pipeline 做：

```text
Low Risk
→ 自动

Medium Risk
→ 自动 + Warning

High Risk
→ 建议值 + 人工核验
```

---

# 二百二十九、这和最终 ProcurementAI 的架构：

```text
Rule
+
Model
+
Human
```

再次一致。

---

# 二百三十、现在看一条 OCR 文本

```text
供应商注册资本不得低于5OO万元。
```

我们可以怎么处理？

---

# 二百三十一、错误做法：

```text
直接改500
```

不记录。

---

# 二百三十二、更好的方式：

```json
{
  "raw_text": "供应商注册资本不得低于5OO万元。",
  "normalized_text": "供应商注册资本不得低于5OO万元。",
  "correction_candidate": "供应商注册资本不得低于500万元。",
  "warnings": [
    "AMBIGUOUS_OCR_NUMERIC_TOKEN"
  ]
}
```

---

# 二百三十三、如果后续人工确认：

```text
500万元
```

再产生：

```text
verified_text
```

---

# 二百三十四、这样系统明确区分：

```text
机器猜测
```

和：

```text
专家确认
```

---

# 二百三十五、这个区别对 Gold Dataset 极其重要。

---

# 二百三十六、现在讨论法律名称

例如：

```text
《中华人民共和国政府采购法》
```

不要清洗成：

```text
中华人民共和国政府采购法
```

虽然一般搜索仍能找到。

---

# 二百三十七、为什么最好保留书名号？

因为它帮助模型识别：

> 这是正式规范名称。

---

# 二百三十八、同样：

```text
第三十一条
```

不要随便：

> 删除“第”和“条”。

---

# 二百三十九、因为：

```text
31
```

本身语义弱很多。

---

# 二百四十、如果做 RAG 索引，可以额外派生：

```text
article_number = 31
```

但原文：

> 保留。

---

# 二百四十一、这是我们反复强调的：

# Add Structure, Don't Destroy Meaning

---

# 二百四十二、现在讲 Markdown 化

为了喂 LLM，

有些系统会把表格转成：

```markdown
| 评分项 | 分值 | 规则 |
|---|---:|---|
| 本地服务 | 5 | 本市有机构得5分 |
```

这是可以的。

---

# 二百四十三、但这个 Markdown 应该是：

# View

不是：

> 唯一 Master Data。

---

# 二百四十四、Master 仍然应该保留：

```text
rows
columns
cells
headers
```

---

# 二百四十五、这样以后模型格式变化，

可以重新生成：

```text
Markdown
JSON
Plain Text
```

而不用：

> 重新解析 PDF。

---

# 二百四十六、这就是第四课一直在建立的核心数据哲学：

\[
\boxed{
RichMasterData
\rightarrow
TaskSpecificViews
}
\]

---

# 二百四十七、现在第一次设计 `CleanClause_V0.1`

它可以概念上长这样：

```json
{
  "clause_id": "CLAUSE-00178",
  "document_id": "DOC-00152-01",

  "section_path": [
    "第三章 采购需求",
    "3.2 售后服务"
  ],

  "raw_text": "供应商应保证故障发生后 2 小时内到达项目现场。",
  "normalized_text": "供应商应保证故障发生后2小时内到达项目现场。",

  "source_block_ids": [
    "B00872"
  ],

  "normalizer_version": "normalizer_v0.1",

  "normalization_ops": [
    "remove_unnecessary_space_between_number_and_unit"
  ],

  "warnings": [],

  "normalization_status": "auto_verified"
}
```

---

# 二百四十八、这里已经有几个重要字段

```text
raw_text
normalized_text
normalizer_version
normalization_ops
warnings
```

---

# 二百四十九、如果 OCR 有不确定内容

可能：

```text
normalization_status =
needs_review
```

---

# 二百五十、如果专家已经确认：

```text
human_verified
```

---

# 二百五十一、所以 Cleaning 同样可以有质量状态。

---

# 二百五十二、现在把第 1～4 阶段的数据对象串起来

```text
Stage 1
TaskSchema_V0.1

Stage 2
ParsedDocument_V0.1

Stage 3
ClauseUnit_V0.1

Stage 4
CleanClause_V0.1
```

---

# 二百五十三、它们不是四份互不相关的数据。

而是一条 Lineage：

```text
Raw File
   ↓
ParsedDocument
   ↓
ClauseUnit
   ↓
CleanClause
   ↓
Annotated Sample
```

---

# 二百五十四、未来如果某个 Gold Sample 出问题，

我们可以：

```text
Gold Sample
↓
CleanClause
↓
ClauseUnit
↓
Source Blocks
↓
Page
↓
Original File
```

一路追到底。

---

# 二百五十五、这才是真正专业的数据资产。

---

# 二百五十六、现在看一个反例：过度清洗

原文：

```text
供应商近3年（2023年1月1日至投标截止日）至少具有5个类似项目业绩。
```

某清洗器想“简化文本”：

```text
供应商近3年至少具有5个类似项目业绩。
```

---

# 二百五十七、看起来更干净。

实际上删掉了：

```text
2023年1月1日至投标截止日
```

这可能：

> 正是争议核心。

---

# 二百五十八、所以：

# Redundancy to human ≠ Redundancy to model

你觉得某句话“啰嗦”。

它可能：

> 对业务判断非常关键。

---

# 二百五十九、再一个例子

Raw：

```text
供应商须具有ISO 9001认证（认证范围须包含信息系统运维服务）。
```

过度清洗：

```text
供应商须具有ISO 9001认证。
```

---

# 二百六十、括号里的：

```text
认证范围
```

被删除。

但它：

> 可能正是限制性的核心。

---

# 二百六十一、所以不要用：

> “看起来像补充说明”

作为删除依据。

---

# 二百六十二、再看一个评分规则

```text
具有本地服务机构得5分；承诺中标后设立服务机构得3分；其他不得分。
```

如果只保留：

```text
本地服务机构得5分
```

你就丢掉了：

> 其它竞争方式。

---

# 二百六十三、于是模型风险判断：

> 可能变得过于激进。

---

# 二百六十四、这就是为什么 Clean Data 也必须：

> 保持完整关系。

---

# 二百六十五、现在讲 Normalization Testing

Normalizer 也应该有测试集。

比如准备几十个案例：

```text
全角数字
OCR空格
比较符
中文/英文标点
金额
日期
型号
法律条号
否定词
表格
```

---

# 二百六十六、每条测试记录：

```text
Input
Expected Output
Must Preserve Tokens
```

---

# 二百六十七、例如：

```text
Input:
注册资本不得低于５００ 万元。

Expected:
注册资本不得低于500万元。

Must Preserve:
不得低于
500
万元
```

---

# 二百六十八、再例如：

```text
Input:
响应时间≤2小时。

Expected:
响应时间≤2小时。

Must Preserve:
≤
2
小时
```

---

# 二百六十九、再例如：

```text
Input:
本项目不接受联合体投标。

Expected:
本项目不接受联合体投标。

Must Preserve:
不接受
```

---

# 二百七十、这样每次改 Normalizer：

> 跑一遍回归测试。

---

# 二百七十一、否则你修复：

> 空格规则

可能意外破坏：

> 技术型号。

---

# 二百七十二、这叫：

# Regression Test

第一课我们在模型里讲过。

现在：

> 数据 Pipeline 也需要。

---

# 二百七十三、所以整个项目里：

# 几乎所有重要模块都应该被评测

不仅：

> LLM。

还包括：

```text
Parser
Structure Recovery
Normalizer
Deduplicator
Label Pipeline
RAG
```

---

# 二百七十四、这是成熟 AI 工程和 Demo 最大的区别之一。

---

# 二百七十五、现在做一个安全清洗决策树

```text
发现异常文本
   │
   ▼
是否明确属于表现层噪声？
   │
   ├── 是
   │    ↓
   │  可以自动规范
   │
   └── 否
        │
        ▼
是否可能改变业务含义？
        │
        ├── 否
        │    ↓
        │  规则规范 + 日志
        │
        └── 是
             │
             ▼
       不静默修改
             │
      ┌──────┴──────┐
      ▼             ▼
   Warning      Human Review
```

---

# 二百七十六、如果只能记一张操作图，

就记这张。

---

# 二百七十七、现在给数据字段分风险

可以建立类似：

```text
Protected Tokens
```

保护字段。

---

# 二百七十八、第一类：

# Negation

```text
不
不得
禁止
无需
未
无
```

---

# 二百七十九、第二类：

# Comparison

```text
大于
小于
以上
以下
不少于
不高于
≤
≥
```

---

# 二百八十、第三类：

# Quantity

```text
金额
人数
数量
分值
比例
时间
期限
距离
容量
性能参数
```

---

# 二百八十一、第四类：

# Identity

```text
项目编号
法规名称
条号
型号
证书名称
机构名称
```

---

# 二百八十二、第五类：

# Scope Modifier

```text
仅
全部
任一
同时
至少
最多
其中
除外
含
不含
```

---

# 二百八十三、这些词看起来很小。

但经常：

> 决定整个 Clause 的约束范围。

---

# 二百八十四、例如：

```text
至少一个
```

和：

```text
全部
```

完全不是同一个条件。

---

# 二百八十五、所以 Normalizer 最好有：

# Protected Pattern Tests

---

# 二百八十六、例如如果清洗前后：

```text
不得
```

消失了，

自动触发：

```text
NEGATION_CHANGED
```

---

# 二百八十七、如果数字数量发生变化：

```text
500
→
5000
```

触发：

```text
NUMERIC_TOKEN_CHANGED
```

---

# 二百八十八、如果：

```text
≤
→
<
```

触发：

```text
COMPARATOR_CHANGED
```

---

# 二百八十九、这叫：

# Semantic Guardrail

语义护栏。

---

# 二百九十、甚至可以做一个简单 Diff

```text
Raw
vs
Normalized
```

自动检查：

> 哪些字符变了。

---

# 二百九十一、如果变化只发生在：

```text
全角数字
多余空格
零宽字符
```

风险较低。

---

# 二百九十二、如果变化触及：

```text
数字
比较符
否定词
单位
```

风险升高。

---

# 二百九十三、这样 Cleaning 就不再是一堆黑盒 `.replace()`。

而变成：

> 可审计的 Transformation Pipeline。

---

# 二百九十四、现在谈 Schema Validation

CleanClause 还可以做结构验证。

例如：

```text
normalized_text不能为空
```

---

# 二百九十五、

```text
raw_text必须存在
```

---

# 二百九十六、

```text
clause_id必须存在
```

---

# 二百九十七、

```text
normalizer_version必须存在
```

---

# 二百九十八、如果发生文本修改：

```text
normalization_ops
```

不能为空。

---

# 二百九十九、如果存在高风险 Warning：

```text
normalization_status
```

不能自动标：

```text
verified
```

---

# 三百、这就开始形成：

# Data Contract

数据契约。

---

# 三百零一、第一阶段我们说 Schema 是合同。

现在终于看到：

> 合同可以被程序验证。

---

# 三百零二、例如：

```python
assert raw_text != ""
assert normalized_text != ""
assert clause_id is not None
```

真实工程会更复杂。

但思想就是：

> 不让坏数据悄悄流下去。

---

# 三百零三、这叫：

# Fail Loudly

发现异常：

> 明确报出来。

不要：

# Fail Silently

悄悄产生坏数据。

---

# 三百零四、例如 OCR 异常：

```text
供应商□□□5OO万元
```

系统不应该：

> 默默当成正常 Clause。

---

# 三百零五、应该带：

```text
warnings
```

让下游知道：

> 这条数据不完全可信。

---

# 三百零六、以后第 12 阶段组装 Dataset 时，

可以直接过滤：

```text
normalization_status != verified
```

的样本。

---

# 三百零七、Gold Set 更可以要求：

```text
parse_verified
+
structure_verified
+
normalization_verified
+
expert_label_verified
```

---

# 三百零八、这就是 Gold 的真正含义：

> 不只是 Label 专家看过。

而是：

> 整条数据链都可信。

---

# 三百零九、现在说一个特别常见的错误：

# 用 LLM 自动“清理”全部数据

例如：

> “请把下面采购条款改写成规范、通顺、简洁的中文。”

---

# 三百一十、LLM 很可能输出：

> 更漂亮。

但它可能：

- 删细节；
- 合并条件；
- 改数字；
- 改语气；
- 补推论。

---

# 三百一十一、这对于：

# Data Cleaning

是非常危险的。

---

# 三百一十二、LLM 可以做什么？

它可以：

> 帮助发现可疑文本。

例如：

```text
这段是不是OCR错误？
```

或者：

```text
这里是不是疑似乱码？
```

---

# 三百一十三、但对于高风险字段：

> 最好让它提出 Candidate，

而不是：

> 直接覆盖 Source Truth。

---

# 三百一十四、可以记住：

```text
LLM as Inspector
>
LLM as Silent Rewriter
```

对于高价值数据尤其如此。

---

# 三百一十五、现在看 Cleaning 的成本问题

是不是所有 100 万条 Clause：

> 都要专家逐条校对？

不现实。

---

# 三百一十六、合理方式是：

```text
低风险规则
→ 全自动

中风险
→ 抽样QA

高风险
→ 人工复核

Gold Set
→ 高强度复核
```

---

# 三百一十七、这叫：

# Tiered Quality Control

分层质量控制。

---

# 三百一十八、它和我们的数据质量阶梯非常一致。

---

# 三百一十九、例如：

```text
CPT Corpus
```

可以容忍：

> 少量格式噪声。

---

# 三百二十、

```text
SFT Training
```

要求：

> 明显更高。

---

# 三百二十一、

```text
Gold Benchmark
```

要求：

> 极高。

---

# 三百二十二、所以不存在一个万能：

```text
clean = true
```

---

# 三百二十三、Data Quality 必须：

> 根据用途定义。

---

# 三百二十四、现在给第四阶段建立完整 Pipeline

```text
ClauseUnit_V0.1
       │
       ▼
 Preserve Raw Text
       │
       ▼
 Unicode Normalization
       │
       ▼
 Safe Whitespace Cleanup
       │
       ▼
 Line-break Repair
       │
       ▼
 Header/Footer Exclusion
       │
       ▼
 OCR Noise Detection
       │
       ▼
 Critical Token Guardrails
       │
       ▼
 Numeric / Unit Validation
       │
       ▼
 Normalization Diff
       │
       ▼
 Quality Warnings
       │
       ▼
 CleanClause_V0.1
```

---

# 三百二十五、注意这里没有一步叫：

```text
Rewrite to Beautiful Chinese
```

这不是我们的目标。

---

# 三百二十六、本阶段最容易犯的 12 个错误

第一类错误是：

> **直接覆盖 Raw Text。**

一旦错了，无法回滚。

第二类错误是：

> **删除所有空格。**

会破坏英文、型号和结构。

第三类错误是：

> **删除所有换行。**

会破坏 Section / List / Clause 关系。

第四类错误是：

> **删除所有标点。**

技术符号和逻辑结构会丢。

第五类错误是：

> **做传统停用词删除。**

尤其可能删掉否定词。

第六类错误是：

> **OCR 猜到什么就自动改什么。**

会制造假数据。

第七类错误是：

> **修改数字却不记录。**

极其危险。

第八类错误是：

> **单位和数字分开保存后把单位丢掉。**

业务意义会改变。

第九类错误是：

> **删除括号内容。**

括号经常包含关键限定。

第十类错误是：

> **把真实重复当成解析重复删掉。**

这应该留到去重阶段。

第十一类错误是：

> **用 LLM 批量润色原始条款。**

会产生隐性语义漂移。

第十二类错误是：

> **Normalizer 没版本、没日志、没测试。**

半年后几乎无法追责。

---

# 三百二十七、本阶段最重要的 5 个“≠”

```text
Cleaning
≠
Rewriting
```

```text
Normalized Text
≠
Source Truth
```

```text
Whitespace
≠
Always Noise
```

```text
Punctuation
≠
Always Decoration
```

```text
Cleaner-looking
≠
More Correct
```

最后这一条尤其重要。

---

# 三百二十八、再记一个最重要的“=”

\[
\boxed{
SafeNormalization
=
SemanticPreservation
+
Traceability
+
Reversibility
+
Consistency
}
\]

翻译成人话：

> **好的清洗不是把文本变漂亮，而是在尽量保持原始语义的前提下，让表示方式更稳定，同时保证每次修改都能追踪、能回滚、能重复得到同样结果。**

---

# 三百二十九、现在把第四课前四阶段连起来

```text
第四课 · 第1阶段
Task Schema
│
│  定义：一条业务样本是什么
▼

第四课 · 第2阶段
ParsedDocument
│
│  恢复：文件里到底写了什么
▼

第四课 · 第3阶段
ClauseUnit
│
│  恢复：这些文字属于哪里
▼

第四课 · 第4阶段
CleanClause
│
│  规范：怎样安全统一文本表现
▼
```

我们离真正的数据集：

> 已经越来越近。

---

# 三百三十、但现在会出现一个新问题

假设我们收集了：

```text
10万条 CleanClause
```

看起来都很干净。

但里面可能有：

```text
同一个项目重复下载3次

同一公告HTML和PDF各来一份

同一条法规被复制到50个文档

不同项目使用同一个模板

同一个条款只是换了项目名称
```

---

# 三百三十一、也就是说：

> **文本干净，不代表数据独立。**

---

# 三百三十二、如果这些重复数据直接进入训练

某类模板可能：

> 被重复几十倍。

模型会误以为：

> 这是整个行业最重要的规律。

---

# 三百三十三、更危险的是

如果同一条重复内容：

```text
一份进入Train
一份进入Test
```

你会得到：

> 非常漂亮但完全虚假的 Benchmark。

---

# 三百三十四、所以第四阶段之后，

下一个大问题就是：

# Deduplication

---

# 三百三十五、本阶段掌握测试

如果现在不看前文，你能自己回答下面这些问题，本阶段就真正掌握了：

> 为什么 Cleaning 不等于 Rewrite？

> 为什么必须同时保留 `raw_text` 和 `normalized_text`？

> 为什么 Normalized Text 只能是派生版本？

> 为什么不能简单删除所有空格？

> 为什么 Visual Line Break 和 Semantic Break 必须区分？

> 为什么全角数字转半角通常属于低风险 Normalization？

> 为什么 `<`、`≤`、`>`、`≥` 绝对不能随便互换？

> 为什么金额、分值、比例、年限、响应时间属于高风险信息？

> 为什么 OCR 中的 `O` 和 `0` 不能总是自动纠正？

> 为什么单位不能被丢弃？

> 为什么“2026年9月”不能自动变成“2026-09-01”？

> 为什么 `9月15日前` 不能只保存一个日期值？

> 为什么否定词绝对不能作为普通停用词删除？

> 为什么现代 LLM 数据通常不需要传统 Stopword Removal？

> 为什么括号内容不能默认认为是噪声？

> 为什么编号最好保留？

> 为什么页眉页脚可以从 Clean View 去除，却仍应保留在 Raw Parsed Layer？

> Parsing Duplicate 和真实文档重复有什么区别？

> 为什么真正的业务去重要留到下一阶段？

> 为什么无法识别的 OCR 字符不能直接静默删除？

> 为什么原文件中的疑似错别字不能随便替作者改正？

> 为什么同一个 Clause 可以有 Raw、Normalized、Search、Display 多个 View？

> 为什么金额、日期等更适合“增加结构字段”，而不是改写原文？

> 什么是 Normalization Log？

> 为什么需要 `normalizer_version`？

> 什么叫 Idempotence？

> 为什么希望满足：

\[
N(N(x))=N(x)
\]

> 为什么 Normalizer 也需要 Regression Test？

> 什么是 Semantic Guardrail？

> 为什么数字、单位、否定词、比较符变化应该触发 Warning？

> 为什么 Gold Dataset 对清洗质量的要求应该高于普通 CPT Corpus？

> 为什么不建议让 LLM 批量“润色”采购原文后直接作为训练真相？

如果这些问题你可以自己完整解释：

\[
\boxed{
第四课第4阶段真正掌握
}
\]

---

# 三百三十六、本阶段最终只记一句话

> **政府采购数据清洗的目标不是把文本变得漂亮，而是在不改变原始业务含义的前提下，安全地统一字符、空格、换行和版式噪声；所有高风险修改都必须可追踪、可回滚，并且原始文本永远保留。**

最后压成一张图：

```text
                    ClauseUnit_V0.1
                           │
                           ▼
                    Preserve Raw Text
                           │
                           ▼
              ┌────────────────────────┐
              │ Safe Normalization     │
              │                        │
              │ Unicode                │
              │ Whitespace             │
              │ Line Break             │
              │ Header / Footer        │
              │ OCR Noise              │
              └────────────┬───────────┘
                           │
                           ▼
                 Semantic Guardrails
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           数字/单位      否定词       比较符
              │            │            │
              └────────────┼────────────┘
                           ▼
                  Normalization Diff
                           │
                           ▼
                   Warning / Review
                           │
                           ▼
                   CleanClause_V0.1
                           │
               ┌───────────┼───────────┐
               ▼           ▼           ▼
             SFT          RAG        Evaluation
```

---

# 下一阶段：第四课 · 第 5 阶段
## 去重与近似去重——为什么 100 万条“干净数据”可能实际上只有 30 万条独立信息？为什么重复数据不仅浪费训练，还会制造虚假的 Benchmark？

第五阶段我们会第一次真正解决：

```text
Exact Duplicate
```

与：

```text
Near Duplicate
```

以及一个政府采购数据中特别麻烦的问题：

```text
不同项目
+
同一份模板
+
只替换项目名称、金额和日期
```

它们到底算不算重复？

我们会建立这张脑图：

```text
Duplicate
│
├── File-level Duplicate
│
├── Document-level Duplicate
│
├── Clause-level Duplicate
│
├── Template Duplicate
│
└── Semantic Near Duplicate
```

并第一次真正解释：

> 为什么单纯用 SHA-256 只能解决最容易的一层。

以及为什么：

```text
Train/Test Leakage
```

很多时候不是发生在完全相同的文本上，

而是发生在：

> **模板级近重复。**

最终第五阶段会得到第一版：

# `DedupedClauseSet_V0.1`

也就是把第四课的数据第一次从“干净”推进到：

> **尽量独立、尽量不重复。**

---

<!-- LESSON 04 STAGE 04 END -->


<!-- LESSON 04 STAGE 05 START -->

# 第四课 · 第 5 阶段：去重与近似去重
## 为什么 100 万条“干净数据”可能实际上只有 30 万条独立信息？为什么重复数据不仅浪费训练，还会制造虚假的 Benchmark？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **主要让模型偏科。**
2. **会让考试成绩造假。**
3. **Data Count ≠ Independent Information Count**
4. **去重 ≠ 删除所有相似文本**
5. **Exact Duplicate 最容易， Near Duplicate 才是真正困难的部分**
6. **模板相同 ≠ 项目完全相同**
7. **Duplicate Detection 应先“聚类和建立关系”， 再决定是否删除**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `Raw Document` | 原始文档：未经结构化处理的采购文件源材料 |
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Dataset` | 数据集：按统一 Schema、版本和质量标准组织的样本集合 |
| `Metadata` | 元数据：项目、来源、时间、地区、版本等辅助信息 |
| `Block` | 版面块：文档解析后保留布局和位置的基本块 |
| `CPT` | CPT/继续预训练：在领域语料上继续执行预训练目标 |
| `Embedding` | 嵌入：把离散 Token 映射到连续高维向量 |
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `Split` | 数据切分：按项目/时间/地区划分训练、验证、测试数据 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |

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

第四阶段结束以后，我们已经拥有：

```text
Raw Document
      ↓
ParsedDocument_V0.1
      ↓
ClauseUnit_V0.1
      ↓
CleanClause_V0.1
```

现在每一条 Clause 已经尽量做到：

```text
文字可信
结构可信
来源可追
格式稳定
高风险字符受到保护
```

看起来，似乎已经可以直接：

> 开始训练。

但现在我们会碰到一个特别隐蔽的问题。

假设你统计数据库：

```text
CleanClause 总数 = 1,000,000
```

团队非常兴奋：

> “我们已经有 100 万条政府采购专业数据！”

但当我们真正检查以后，可能发现：

```text
20万条
来自同一个采购模板

10万条
只是同一公告PDF和HTML各存了一份

15万条
来自网站镜像和重复下载

18万条
只有项目名、日期、金额不同

7万条
是更正前后高度相似的版本
```

最后真正独立的信息，可能远远不到：

```text
100万
```

这就是第五阶段要处理的核心问题：

# Duplicate

重复。

但今天很快会看到：

> 去重绝对不是“相同文本删掉一条”这么简单。

---

# 一、本阶段真正要解决的一个核心问题

今天只解决：

> **怎样识别政府采购数据里的完全重复、近似重复、模板重复和版本重复，并在不误删真实业务差异的前提下，控制重复信息对训练和评测造成的偏差？**

最终我们要得到：

# `DedupedClauseSet_V0.1`

主线是：

```text
CleanClause_V0.1
        ↓
Duplicate Detection
        ↓
Duplicate Clustering
        ↓
Canonical / Relation Decision
        ↓
DedupedClauseSet_V0.1
```

---

# 二、先建立本阶段最重要的 6 个核心心智模型

```text
① Data Count ≠ Independent Information Count

② 去重 ≠ 删除所有相似文本

③ Exact Duplicate 最容易，
   Near Duplicate 才是真正困难的部分

④ 模板相同 ≠ 项目完全相同

⑤ Duplicate Detection 应先“聚类和建立关系”，
   再决定是否删除

⑥ Train / Test 之间的近重复
   比训练集内部重复更危险
```

最后一句尤其重要。

因为训练集里重复很多：

> 主要让模型偏科。

而 Train/Test 之间出现重复：

> 会让考试成绩造假。

---

# 三、先看最简单的重复

假设硬盘里有两个文件：

```text
A/
某市智慧交通项目招标文件.pdf
```

和：

```text
B/
最终版-某市智慧交通项目招标文件.pdf
```

名字不同。

但是两个文件：

> 一个 Byte 都没变。

---

# 四、这是最简单的一类

# Exact File Duplicate

完全文件重复。

这类非常容易发现。

---

# 五、怎么发现？

第四课第二阶段已经埋好了一个字段：

```text
file_hash
```

例如：

# SHA-256

如果：

```text
SHA256(File A)
=
SHA256(File B)
```

那么在实际工程中，我们可以极高置信度认为：

> 内容完全相同。

---

# 六、注意

文件名不同：

```text
招标文件.pdf
最终招标文件.pdf
下载(1).pdf
```

完全不重要。

Hash 看的是：

> 文件内容。

---

# 七、所以第一层 Dedup 非常简单

```text
Raw File
   │
   ▼
SHA-256
   │
   ▼
Hash相同？
   │
   ├── 是 → Exact File Duplicate
   └── 否 → 继续检查
```

---

# 八、但 Hash 不同，是不是说明内容不同？

不一定。

这就是事情开始变麻烦的地方。

---

# 九、假设有两个 PDF

文件 A：

```text
某项目招标文件.pdf
```

文件 B：

```text
某项目招标文件-官网下载.pdf
```

看起来内容完全一样。

但 B 的 PDF Metadata 多了：

```text
Creator
CreationTime
Producer
```

---

# 十、文件 Byte 不一样

所以：

```text
SHA256(A)
≠
SHA256(B)
```

但用户看到的正文：

> 完全一样。

---

# 十一、这就是第二层

# Content Duplicate

内容重复。

---

# 十二、所以我们已经有两个不同概念

```text
File Duplicate
```

和：

```text
Content Duplicate
```

千万不要混。

---

# 十三、可以记：

\[
\boxed{
FileHash不同
\not\Rightarrow
DocumentContent不同
}
\]

---

# 十四、同样的事情在 HTML 特别常见

两个网址：

```text
site-a.gov.cn/notice/123
```

和：

```text
mirror.gov.cn/archive/456
```

网页结构完全不同。

一个有：

```text
导航栏
分享按钮
版权信息
```

另一个没有。

---

# 十五、但采购公告正文：

> 一模一样。

原 HTML Hash：

> 完全不同。

正文：

> 相同。

---

# 十六、所以第二层去重最好发生在：

# Parsed / Clean Content

而不只是原文件。

---

# 十七、这就是为什么我们之前一直保留分层数据

现在终于看到收益：

```text
Raw File Hash
```

可以找：

> 文件级重复。

```text
Normalized Document Text
```

可以找：

> 正文级重复。

```text
CleanClause
```

可以找：

> 条款级重复。

---

# 十八、所以 Dedup 本身也是多层的

今天最重要的一张图之一：

```text
Duplicate
│
├── File-level Duplicate
│
├── Document-level Duplicate
│
├── Section-level Duplicate
│
├── Clause-level Duplicate
│
├── Template-level Duplicate
└── Semantic Near Duplicate
```

不是一个：

> `drop_duplicates()`。

---

# 十九、现在看 Clause-level Exact Duplicate

假设两个不同项目都有：

```text
供应商应具有独立承担民事责任的能力。
```

字符串完全一致。

是不是应该：

> 留一条，删除另一条？

---

# 二十、答案：

# 不一定。

这句话特别重要。

---

# 二十一、为什么？

因为它们可能来自：

```text
Project A
```

和：

```text
Project B
```

两个真实、独立的采购项目。

---

# 二十二、从“文本内容”来看

它们：

> 完全重复。

---

# 二十三、但从“业务事件”来看

它们：

> 发生了两次。

---

# 二十四、所以这里出现一个很重要的区别：

# Text Duplicate

和：

# Observation Duplicate

不是一回事。

---

# 二十五、举个生活例子

调查 100 家商店。

发现 80 家都写：

> “营业时间 9:00—21:00”。

是不是应该说：

> “这句话一样，所以只算一家商店”？

当然不是。

---

# 二十六、因为你研究的是：

> 商店分布。

重复本身：

> 可能是真实统计信息。

---

# 二十七、同样，

如果你研究：

> 政府采购文件中某类标准资格条件的真实出现频率，

这些重复：

> 本身就是数据。

---

# 二十八、但如果你在训练 LLM

同一句标准模板出现：

```text
100,000次
```

另外一个重要边界条件只出现：

```text
100次
```

模型会发生什么？

---

# 二十九、它会非常强烈地学到：

> 高频模板。

而对真正稀有、困难的风险：

> 学得很差。

---

# 三十、所以 Dedup 的目标不是问：

> “重复是不是坏？”

而应该问：

> **“对于当前任务，这种重复会不会不合理地改变数据权重？”**

---

# 三十一、这是第五阶段最重要的思想之一：

\[
\boxed{
DedupPolicy
取决于
DatasetPurpose
}
\]

---

# 三十二、比如 CPT 语料

大量行业标准表达重复出现：

> 未必完全是坏事。

它反映：

> 真实行业语言分布。

---

# 三十三、但如果某一个网站镜像了同一批公告 20 次

那 20 倍频率：

> 是数据采集过程制造的。

不是行业真实分布。

这就应该去掉。

---

# 三十四、这两种重复必须区分

### Natural Repetition

真实业务重复。

### Artificial Duplication

采集流程制造的重复。

---

# 三十五、我们真正最想消灭的是：

# Artificial Duplication

---

# 三十六、比如：

```text
同一PDF重复下载
同一网页不同URL镜像
同一个附件被保存5份
解析器重复输出同一个Block
```

这些：

> 都不是新的业务观察。

---

# 三十七、而不同项目都包含：

```text
供应商应具有良好的商业信誉。
```

则可能是：

> 真实自然重复。

---

# 三十八、所以去重数据库最好不要简单只有

```text
is_duplicate = true
```

而应该知道：

# Duplicate Relation

到底是哪种关系。

---

# 三十九、例如：

```text
exact_copy
```

```text
mirror_copy
```

```text
same_document_different_format
```

```text
template_reuse
```

```text
revised_version
```

```text
semantic_near_duplicate
```

---

# 四十、这些关系：

> 处理方式不一样。

---

# 四十一、现在看第三种典型情况

# Same Document, Different Format

采购网站可能同时提供：

```text
公告正文 HTML
```

和：

```text
公告附件 PDF
```

正文有时：

> 几乎完全相同。

---

# 四十二、如果我们两边都收

Dataset 里：

> 同一内容变成两次。

---

# 四十三、哪一个留？

可能要根据：

```text
Source Authority
Parse Quality
Completeness
Traceability
```

选择：

# Canonical Copy

权威代表版本。

---

# 四十四、例如：

```text
PDF:
正式签章附件
```

和：

```text
HTML:
网站正文
```

不能机械说：

> HTML 更干净，所以删 PDF。

---

# 四十五、因为 Source Authority：

> 也很重要。

---

# 四十六、因此 Duplicate Cluster 内最好有：

```text
canonical_document_id
```

指向：

> 代表版本。

其他版本：

> 不一定物理删除。

可以保留关系。

---

# 四十七、这就是今天另一个核心原则：

# Dedup ≠ Physical Delete

---

# 四十八、更安全的架构是：

```text
Duplicate Cluster
│
├── Canonical Record
├── Duplicate Record 1
├── Duplicate Record 2
└── Duplicate Record 3
```

---

# 四十九、训练 View：

> 只取 Canonical。

Master Data：

> 全部保留。

---

# 五十、这和第四阶段：

```text
Raw
+
Normalized
```

的哲学完全一致。

---

# 五十一、永远尽量：

# Non-destructive Data Engineering

---

# 五十二、现在进入真正困难的部分

# Near Duplicate

近似重复。

---

# 五十三、例如条款 A：

> 供应商应在本市设有固定售后服务机构。

条款 B：

> 投标人须在项目所在地设立固定售后服务机构。

---

# 五十四、字符串：

> 不一样。

但是业务含义：

> 非常接近。

---

# 五十五、再例如：

A：

> 供应商注册资本不得低于5000万元。

B：

> 投标人注册资本应达到人民币5000万元以上。

---

# 五十六、表面字符不同。

但核心条件：

```text
注册资本
>=
5000万元
```

基本一样。

---

# 五十七、这就是：

# Semantic Near Duplicate

语义近重复。

---

# 五十八、如果只用：

```text
text == other_text
```

完全发现不了。

---

# 五十九、这就是为什么：

> SHA-256 只能解决最容易的一层。

---

# 六十、那么近重复怎么检测？

我们先不要上复杂算法。

先建立最直观的方法：

# Token Overlap

---

# 六十一、假设：

A：

```text
供应商 须 在 本市 设立 售后 服务 机构
```

B：

```text
供应商 应 在 本市 设立 固定 服务 机构
```

很多词：

> 是一样的。

---

# 六十二、于是可以问：

> 两条文本共享多少内容？

这就是 Similarity。

---

# 六十三、一个经典直觉指标：

# Jaccard Similarity

公式非常简单：

\[
J(A,B)
=
\frac{|A\cap B|}
{|A\cup B|}
\]

---

# 六十四、先不怕公式。

它只是在说：

> 两组元素里，共同出现的东西占全部不同元素的多少。

---

# 六十五、例如 A 有：

```text
{供应商, 本市, 服务, 机构}
```

B 有：

```text
{供应商, 本市, 固定, 服务, 机构}
```

共同：

```text
供应商
本市
服务
机构
```

有 4 个。

全部不同元素：

```text
供应商
本市
固定
服务
机构
```

有 5 个。

---

# 六十六、所以：

\[
J(A,B)=\frac45=0.8
\]

也就是：

> 80% 相似。

---

# 六十七、这比：

```text
必须100%相同
```

聪明很多。

---

# 六十八、但是直接按“词集合”比较也有问题

A：

> 供应商不得在本市设立机构。

B：

> 供应商必须在本市设立机构。

---

# 六十九、它们绝大多数词：

> 一模一样。

Jaccard：

> 可能非常高。

---

# 七十、但是：

```text
不得
```

和：

```text
必须
```

让业务意义：

> 几乎相反。

---

# 七十一、所以第五阶段再次碰到第四阶段那个老朋友：

# High-risk Tokens

---

# 七十二、Near Duplicate Detection 也必须保护：

```text
否定词
数字
金额
单位
比较符
日期
品牌型号
地域
评分值
```

---

# 七十三、所以不能因为：

```text
Similarity = 0.95
```

就直接删。

---

# 七十四、Similarity 只是：

# Candidate Generator

候选生成器。

不是：

# Final Truth

---

# 七十五、这是今天非常重要的一句话：

> **相似度负责告诉你“值得比较”，而不是负责替你决定“它们完全一样”。**

---

# 七十六、现在再看一个例子

A：

> 响应时间不得超过2小时。

B：

> 响应时间不得超过4小时。

---

# 七十七、两个句子只有一个字符不同。

文本相似度：

> 极高。

---

# 七十八、但业务条件：

> 差了一倍。

---

# 七十九、所以如果 Dedup 把它们合并，

你直接丢失：

> 真实业务差异。

---

# 八十、这说明 Near Dedup 必须有：

# Difference Awareness

不仅看：

> 像不像。

还要看：

> **到底哪里不一样。**

---

# 八十一、特别需要做：

```text
Numeric Diff
Comparator Diff
Negation Diff
Entity Diff
Unit Diff
```

---

# 八十二、例如：

```text
A:
不少于3年

B:
不少于5年
```

标记：

```text
text_similarity = high
numeric_difference = true
```

---

# 八十三、这种关系更适合叫：

```text
template_variant
```

而不是：

```text
duplicate
```

---

# 八十四、这就进入采购数据中特别重要的一类：

# Template Duplicate

模板重复。

---

# 八十五、政府采购文件大量使用模板。

例如 100 个项目都写：

```text
项目名称：XXX
项目编号：XXX
预算金额：XXX
```

---

# 八十六、甚至资格条件：

```text
供应商须具有独立承担民事责任的能力；
具有良好的商业信誉；
具有履行合同所必需的设备和专业技术能力；
……
```

很多文件：

> 大片完全相同。

---

# 八十七、还有招标机构自己的标准模板。

比如：

```text
采购人名称不同
项目名称不同
预算不同
日期不同
```

其余 90%：

> 一样。

---

# 八十八、如果按普通字符串比较

这些文件：

> 不是完全相同。

---

# 八十九、如果按语义比较

它们：

> 高度接近。

---

# 九十、从训练角度看

如果把 10,000 份模板全喂进去，

模型会不断看到：

> 同一结构。

---

# 九十一、这可能造成：

# Template Overweighting

模板过权重。

---

# 九十二、尤其如果某一个地区的数据：

> 特别容易爬取。

你可能无意中让模型学成：

> 某地区采购模板专家。

而不是：

> 全国政府采购专家。

---

# 九十三、所以 Dedup 其实也在解决：

# Sampling Bias

采样偏差。

---

# 九十四、例如：

```text
地区A
采集到30万份

地区B
采集到2万份
```

如果 A 大量使用统一模板，

模型看到的不是：

> 15 倍新的知识。

可能只是：

> 同一模板重复 15 倍。

---

# 九十五、这就是：

\[
\boxed{
Volume
\neq
Diversity
}
\]

---

# 九十六、对领域模型来说，

数据多当然重要。

但更重要的是：

# Information Diversity

信息多样性。

---

# 九十七、我们真正希望覆盖的是：

```text
不同地区
不同采购方式
不同项目类型
不同预算规模
不同风险类型
不同写法
不同边界案例
不同法规场景
```

而不是：

> 同一个模板复制 100 万次。

---

# 九十八、那么怎么发现 Template Duplicate？

一个方法是：

# Variable Masking

---

# 九十九、例如：

原文 A：

```text
项目编号：ABC-2026-001
预算金额：500万元
投标截止日期：2026年9月30日
```

B：

```text
项目编号：XYZ-2026-812
预算金额：800万元
投标截止日期：2026年10月8日
```

---

# 一百、我们可以产生一个：

# Template View

例如：

```text
项目编号：<PROJECT_ID>
预算金额：<AMOUNT>
投标截止日期：<DATE>
```

---

# 一百零一、于是 A 和 B 的 Template View：

> 完全一致。

---

# 一百零二、这说明：

> 它们高度可能来自同一模板。

---

# 一百零三、但是注意！

不能把这个 Template View：

> 替代原文。

---

# 一百零四、因为：

```text
500万元
```

和：

```text
800万元
```

业务意义仍然存在。

---

# 一百零五、所以正确架构是：

```text
raw_text
normalized_text
template_view
```

三个不同 View。

---

# 一百零六、其中：

```text
template_view
```

只用于：

> 检测结构重复。

---

# 一百零七、这就是 Multiple Views 思维再次出现。

---

# 一百零八、现在有一个问题：

哪些东西可以 Mask？

比如：

```text
项目名称
项目编号
日期
```

相对容易。

---

# 一百零九、那金额呢？

就要谨慎。

因为有些任务中：

> 金额是业务核心。

---

# 一百一十、例如：

> “注册资本不得低于5000万元。”

这里的：

```text
5000万元
```

不能简单 Mask 后就说：

> 和 500 万元完全一样。

---

# 一百一十一、Template Detection 可以说：

> 结构一样。

但业务内容层：

> 不是同一条样本。

---

# 一百一十二、因此最好同时保留两个判断：

```text
template_similarity
```

和：

```text
business_value_difference
```

---

# 一百一十三、例如：

```json
{
  "template_similarity": 0.99,
  "numeric_difference": true,
  "dedup_relation": "template_variant"
}
```

---

# 一百一十四、而不是：

```json
{
  "duplicate": true
}
```

一句话解决。

---

# 一百一十五、这就是专业 Dedup：

> **不是只有相似度，而是有重复关系类型。**

---

# 一百一十六、现在看 Version Duplicate

政府采购中特别常见：

```text
原招标文件
```

然后：

```text
更正公告
```

然后：

```text
更正后招标文件
```

---

# 一百一十七、两个版本可能有：

> 99.5% 内容一样。

只改了一句话：

```text
注册资本不得低于5000万元
```

变成：

```text
删除注册资本要求
```

---

# 一百一十八、如果 Near Dedup 系统看到：

```text
99.5%相似
```

直接删一个，

会发生什么？

---

# 一百一十九、你可能把整个：

# Correction Event

更正事件删掉。

---

# 一百二十、而这种数据：

> 恰恰极其有价值。

---

# 一百二十一、为什么？

因为：

> 原条件被官方修改，

本身可能说明：

> 这类条款存在问题或者需要调整。

---

# 一百二十二、所以：

# Version Similarity ≠ Duplicate

---

# 一百二十三、我们应该建立：

```text
version_of
```

关系。

---

# 一百二十四、例如：

```text
DOC_V1
   ↓ revised_by
DOC_V2
```

---

# 一百二十五、然后保存：

# Diff

到底改了什么。

---

# 一百二十六、比如：

```text
删除：
供应商注册资本不得低于5000万元。

新增：
供应商应具有履行合同所必需的能力。
```

这种信息：

> 对未来专家模型非常值钱。

---

# 一百二十七、所以去重时一定要先问：

> **这是重复，还是版本演化？**

---

# 一百二十八、这两种如果混：

> 会直接毁掉时间信息。

---

# 一百二十九、以后 RAG 也一样。

旧法规和新法规：

> 可能 95% 相同。

但你不能说：

> 相似，所以删掉旧的。

---

# 一百三十、因为法律知识需要：

```text
effective_from
effective_to
```

版本和时间：

> 本身就是知识。

---

# 一百三十一、第五阶段虽然主要讲训练数据，

但这个思维以后第六课：

> 法规 RAG

会非常重要。

---

# 一百三十二、现在进入一个经典文本方法：

# Shingling

这个词第一次看会陌生。

其实非常简单。

---

# 一百三十三、假设一句话：

```text
供应商必须具备相关资质
```

我们可以连续取若干字符。

比如 3 个字符一组：

```text
供应商
应商必
商必须
必须具
须具备
具备相
备相关
相关资
关资质
```

---

# 一百三十四、这些连续小片段：

> 就可以叫 Shingles。

---

# 一百三十五、然后比较两条文本的 Shingle 集合：

> 有多少相同。

---

# 一百三十六、这样比单纯看词：

> 对长文本局部重复非常好用。

---

# 一百三十七、例如两个招标文件：

90% 内容一样，

只改：

> 项目名称和日期。

它们的 Shingle：

> 会大量重合。

---

# 一百三十八、于是可以用：

# Jaccard Similarity

判断内容重合度。

---

# 一百三十九、但如果我们有：

```text
1,000,000 条 Clause
```

能不能每两条都比较？

---

# 一百四十、不能。

两两比较规模会爆炸。

直觉上：

```text
100万 × 100万
```

太大。

---

# 一百四十一、所以工程上需要：

# Approximate Search

近似候选检索。

---

# 一百四十二、这就是 MinHash 出现的地方。

不用现在学算法推导。

只记一个心智模型：

# MinHash = 给集合相似度做一个小指纹

---

# 一百四十三、原来每条文档可能有：

```text
数万个 Shingle
```

MinHash 把它压成：

> 一个较短的 Signature。

---

# 一百四十四、相似文本：

> Signature 也更容易相似。

---

# 一百四十五、于是系统可以快速找到：

> 值得做精确比较的候选。

---

# 一百四十六、所以：

```text
Shingle
+
MinHash
+
LSH
```

经常用于：

> 大规模文本近重复检测。

---

# 一百四十七、LSH 又是什么？

先不用学数学。

可以理解成：

> **把可能相似的东西尽量扔到同一个桶里。**

---

# 一百四十八、于是：

```text
100万条数据
```

不用：

> 全部彼此比较。

只比较：

> 同桶候选。

---

# 一百四十九、这就像：

100 万个人找长得像的人。

不是：

> 每个人和另外 999,999 人握手比较。

而是先按：

```text
大概特征
```

分组。

---

# 一百五十、再在组内：

> 精细比较。

---

# 一百五十一、所以一个工程流程可以是：

```text
Clean Text
   ↓
Shingle
   ↓
MinHash Signature
   ↓
LSH Candidate Search
   ↓
Exact Similarity
   ↓
Business Difference Check
```

---

# 一百五十二、最后那一步：

# Business Difference Check

特别重要。

因为算法只知道：

> 字很像。

它不知道：

```text
2小时
```

和：

```text
24小时
```

可能是本质差异。

---

# 一百五十三、除了 MinHash，还有：

# SimHash

也是一种近重复指纹思路。

---

# 一百五十四、非常粗略地理解：

MinHash 更适合：

> 集合重合。

SimHash 更像：

> 给文本整体特征生成一个二进制指纹。

---

# 一百五十五、相似文本的 SimHash：

> 汉明距离通常较近。

---

# 一百五十六、现在不用比较：

> 哪个算法“最好”。

因为真实系统：

> 经常多种策略并用。

---

# 一百五十七、例如：

```text
File SHA-256
→ 找完全文件重复

Normalized Text Hash
→ 找完全正文重复

MinHash
→ 找高文本重叠

Embedding
→ 找语义近似
```

---

# 一百五十八、这就是：

# Multi-stage Dedup

多阶段去重。

---

# 一百五十九、现在说 Embedding。

第二课里我们已经学过：

> 文本可以映射到向量空间。

---

# 一百六十、那么：

> “供应商必须在本市设立服务机构”

和：

> “投标人须于项目所在地设置固定售后机构”

Embedding：

> 可能非常接近。

---

# 一百六十一、这非常适合发现：

# Paraphrase Duplicate

同义改写近重复。

---

# 一百六十二、但这里又有一个巨坑。

A：

> 本项目接受联合体投标。

B：

> 本项目不接受联合体投标。

---

# 一百六十三、语义主题极其接近。

Embedding：

> 很可能也非常近。

---

# 一百六十四、但业务含义：

> 相反。

---

# 一百六十五、所以再强调一次：

\[
\boxed{
EmbeddingSimilarity
\neq
BusinessEquivalence
}
\]

---

# 一百六十六、Embedding 最适合：

> 找候选。

不适合单独承担：

> 自动删除裁判。

---

# 一百六十七、特别是政府采购这种：

> 数字、否定、条件范围特别重要的领域。

---

# 一百六十八、一个更稳健的策略：

```text
Embedding高相似
        ↓
文本Diff
        ↓
关键字段Diff
        ↓
规则判断
        ↓
必要时人工复核
```

---

# 一百六十九、例如：

```text
Similarity = 0.98
```

但是发现：

```text
numeric_difference = true
```

那么不要合并。

---

# 一百七十、又例如：

```text
Similarity = 0.99
```

但是：

```text
negation_difference = true
```

直接：

> 高风险。

---

# 一百七十一、所以我们可以建立：

# Dedup Guardrails

---

# 一百七十二、保护项可以包括：

```text
数字
单位
比较符
否定词
日期
分值
项目地域
品牌型号
法规条号
```

---

# 一百七十三、这和第四阶段的 Semantic Guardrail：

> 直接复用。

---

# 一百七十四、好的数据工程是这样的：

前面建立的能力，

后面：

> 一直复用。

而不是每阶段重新发明一套。

---

# 一百七十五、现在讲 Canonical Record

假设发现三个完全重复文档：

```text
D1
官网PDF

D2
镜像网站PDF

D3
第三方转载PDF
```

应该留谁？

---

# 一百七十六、优先考虑：

```text
Source Authority
```

---

# 一百七十七、然后：

```text
Parse Quality
```

---

# 一百七十八、再考虑：

```text
Completeness
```

---

# 一百七十九、再考虑：

```text
Metadata Quality
```

---

# 一百八十、例如：

```text
D1
官方来源
解析质量0.98
有发布日期
```

通常就比：

```text
D3
第三方转载
无来源时间
```

更适合当：

> Canonical。

---

# 一百八十一、所以 Canonical Selection：

> 不是随机留第一条。

---

# 一百八十二、可以有一个优先级：

```text
Official Source
    >
Verified Mirror
    >
Unknown Repost
```

再结合：

> 解析质量。

---

# 一百八十三、但是其它 Record：

> 不要一定删除。

可以保存：

```text
duplicate_of = D1
```

---

# 一百八十四、为什么？

因为未来我们可能需要：

> 检查数据来源。

---

# 一百八十五、或者发现：

> D1 后来网页下线了。

D2：

> 仍然可以提供证据。

---

# 一百八十六、所以 Master Data：

> 保留多来源关系。

Training View：

> 去重。

这是很好的架构。

---

# 一百八十七、现在进入 Cluster 思维。

如果：

```text
A重复B
B重复C
```

那不能只保存：

```text
A→B
B→C
```

更好是形成：

# Duplicate Group

---

# 一百八十八、例如：

```text
duplicate_group_id:
DG-000137
```

里面：

```text
A
B
C
D
```

---

# 一百八十九、其中：

```text
canonical_id = A
```

其它：

```text
member_of = DG-000137
```

---

# 一百九十、这对后面数据切分：

> 极其重要。

---

# 一百九十一、为什么？

如果：

```text
A → Train
```

而：

```text
B → Test
```

模型考试时：

> 几乎已经见过答案。

---

# 一百九十二、所以后面第 6 阶段切数据的时候：

# Duplicate Group 必须作为一个 Split Group

---

# 一百九十三、也就是：

```text
DG-000137
```

里面所有成员：

> 必须一起去 Train，

或者一起：

> 去 Test。

不能拆开。

---

# 一百九十四、这一点非常关键。

即使 Training View 最后只取 Canonical，

我们仍然应该保留：

```text
duplicate_group_id
```

---

# 一百九十五、因为 Near Duplicate：

> 可能并没有真正被删除。

但它们仍然：

> 不应该跨 Split。

---

# 一百九十六、这就是今天和第 6、7 阶段的连接点。

---

# 一百九十七、现在看为什么随机切分特别危险。

假设一个模板：

> 被使用了 1000 次。

---

# 一百九十八、随机做：

```text
80% Train
20% Test
```

那么大概：

```text
800个模板变体
→ Train

200个模板变体
→ Test
```

---

# 一百九十九、模型考试看到：

> 几乎一模一样的结构。

---

# 二百、最后 Accuracy：

```text
97%
```

团队非常开心。

---

# 二百零一、但模型真正遇到新模板：

> 可能只有 65%。

---

# 二百零二、这叫：

# Template Leakage

模板泄漏。

---

# 二百零三、它比完全相同文本泄漏：

> 更难发现。

因为：

```text
text1 != text2
```

---

# 二百零四、传统 `drop_duplicates()`：

> 完全抓不到。

---

# 二百零五、所以 Procurement Benchmark：

> 必须考虑近重复和模板重复。

---

# 二百零六、这是第五阶段最重要的成果之一。

---

# 二百零七、再看法律文本。

多个招标文件都引用：

> 同一个法规原文。

例如某一条法律规定：

> 在 5000 份采购文件里被重复引用。

---

# 二百零八、这些引用要不要：

> 全部删成一份？

取决于任务。

---

# 二百零九、如果做：

# Regulation Corpus

那同一法规正文：

> 一份权威源即可。

---

# 二百一十、如果做：

# Procurement Document Understanding

文档里有没有引用某法规：

> 可能本身就是上下文。

所以不能简单删。

---

# 二百一十一、再次说明：

# Dedup Unit Matters

你是在去重：

```text
法规知识
```

还是：

```text
采购项目观察
```

完全不一样。

---

# 二百一十二、所以每个 Dataset View：

> 可以有自己的 Dedup Policy。

---

# 二百一十三、例如：

### RAG Knowledge Corpus

可以对相同法规条文：

> 强去重。

---

# 二百一十四、### SFT Dataset

高度重复的标准答案：

> 可以采样降权。

---

# 二百一十五、### Evaluation Gold Set

需要：

> 严格控制模板近重复。

---

# 二百一十六、### Statistical Analysis

可能要保留：

> 自然重复频率。

---

# 二百一十七、这就是为什么：

> “去重率越高越专业”

是错的。

---

# 二百一十八、有的团队喜欢说：

> “我们把 70% 数据都去掉了，数据非常纯。”

这句话：

> 本身没有意义。

---

# 二百一十九、正确问题应该是：

> **你删掉的 70% 到底是什么关系？**

---

# 二百二十、如果删掉的是：

```text
镜像
重复下载
Parser Duplicate
```

很好。

---

# 二百二十一、如果删掉的是：

> 真实发生于不同项目的 Hard Cases，

那：

> 可能反而毁了数据。

---

# 二百二十二、现在看重复和 Label 的关系。

假设：

A：

```text
供应商须在本市注册。
```

Label：

```text
potential_risk
```

---

# 二百二十三、B 的文本完全一样：

```text
供应商须在本市注册。
```

但专家标成：

```text
no_risk
```

---

# 二百二十四、这时候系统不能：

> 直接随机留一条。

因为这暴露了：

# Label Conflict

---

# 二百二十五、可能原因：

```text
标注错误
上下文不同
Schema版本不同
专家意见不同
```

---

# 二百二十六、所以重复检测还能帮助：

# Data Quality Audit

---

# 二百二十七、如果相同 Clause：

> Label 不一致，

应该产生：

```text
DUPLICATE_LABEL_CONFLICT
```

---

# 二百二十八、然后进入：

> 人工复核。

---

# 二百二十九、这特别重要。

因为重复不仅是：

> 要删的垃圾。

它还可以暴露：

> 标注问题。

---

# 二百三十、再例如：

同一个条款：

A 的上下文是：

```text
资格条件
```

B 的上下文是：

```text
合同履约
```

---

# 二百三十一、虽然 `clause_text` 一样，

Label 不同：

> 可能完全合理。

---

# 二百三十二、所以 Dedup 不能只比较：

```text
clause_text
```

还要保存：

```text
section_type
context
project_context
```

---

# 二百三十三、这说明：

# Text Equality ≠ Sample Equality

---

# 二百三十四、第一阶段我们定义 Sample：

```text
Clause
+
Context
+
Source
+
Annotation
```

今天终于看到为什么：

> 这些字段一个都不能随便扔。

---

# 二百三十五、现在再看 Hard Negative。

假设：

A：

> 供应商必须在本市设立服务机构。

Label：

> Potential Risk。

---

# 二百三十六、B：

> 供应商无须在本市设立服务机构，但应保证2小时内提供现场服务。

Label：

> 需要结合履约场景判断。

---

# 二百三十七、这两条词汇高度相似。

一个差的 Near Dedup：

> 可能删掉 B。

---

# 二百三十八、但 B 恰恰是：

# Hard Negative / Boundary Case

非常有价值。

---

# 二百三十九、所以近重复检测要特别保护：

> **标签边界附近的数据。**

---

# 二百四十、这也是为什么：

# Rare Hard Cases > Repeated Easy Cases

对于专业模型训练往往很重要。

---

# 二百四十一、以后第 10 阶段：

> Hard Negative

会专门展开。

今天先记住：

> 不要因为文字相似，就把最宝贵的边界案例删掉。

---

# 二百四十二、现在建立第一版 Dedup Pipeline。

```text
CleanClauseSet
       │
       ▼
Exact File Hash
       │
       ▼
Exact Text Hash
       │
       ▼
Normalized Text Hash
       │
       ▼
Template Fingerprint
       │
       ▼
MinHash / Similarity Candidate
       │
       ▼
Embedding Candidate
       │
       ▼
Critical Field Diff
       │
       ▼
Duplicate Relation Classification
       │
       ▼
Duplicate Cluster
       │
       ▼
Canonical Selection
       │
       ▼
DedupedClauseSet_V0.1
```

---

# 二百四十三、注意这个 Pipeline 不是说：

> 所有项目一定要同时用所有算法。

第一版：

> 可以从简单开始。

---

# 二百四十四、第一版非常合理的路线可能是：

```text
1. File SHA-256
2. Exact normalized_text hash
3. High-overlap MinHash
4. Critical-field difference
5. Cluster
```

---

# 二百四十五、等数据量变大以后：

再增加：

```text
Embedding Near-Duplicate
```

---

# 二百四十六、这是一个重要工程原则：

# Start Simple, Measure Errors

---

# 二百四十七、不要第一天就搞：

> 17 种相似度算法 + 神经网络 Dedup。

---

# 二百四十八、先做一个：

> 可解释、能 Benchmark 的 Baseline。

---

# 二百四十九、然后看：

```text
False Merge
```

和：

```text
Missed Duplicate
```

---

# 二百五十、什么叫 False Merge？

系统认为：

> 两条重复。

实际上：

> 有重要差异。

---

# 二百五十一、例如：

```text
不少于3年
```

和：

```text
不少于5年
```

被合并。

这是：

> 非常危险的 False Merge。

---

# 二百五十二、什么叫 Missed Duplicate？

实际上：

> 同一份内容。

系统没有发现。

---

# 二百五十三、例如：

```text
HTML正文
```

和：

```text
PDF正文
```

只有空格和格式不同。

系统没认出来。

---

# 二百五十四、对于我们的项目：

两种错误：

> 风险并不相同。

---

# 二百五十五、False Merge 往往更危险。

因为：

> 它会永久丢掉真实差异。

---

# 二百五十六、Missed Duplicate：

> 更多是冗余和泄漏风险。

---

# 二百五十七、所以 Dedup 阈值应该：

> 偏保守。

---

# 二百五十八、特别是业务关键数据：

> 宁可先保留相似样本并标 Group，

也不要过早删除。

---

# 二百五十九、这就是：

# Cluster First, Delete Later

特别推荐记住。

---

# 二百六十、可以压成：

\[
\boxed{
Detect
\rightarrow
Link
\rightarrow
Cluster
\rightarrow
Decide
}
\]

不是：

\[
\boxed{
Detect
\rightarrow
Delete
}
\]

---

# 二百六十一、现在设计 `DuplicateRelation`

可以概念上有：

```text
exact_file_duplicate
exact_text_duplicate
format_variant
mirror_copy
template_variant
near_duplicate
revised_version
possible_duplicate
```

---

# 二百六十二、还可以有：

```text
not_duplicate
```

用于：

> 人工确认后排除。

---

# 二百六十三、为什么保存：

```text
not_duplicate
```

也有价值？

因为系统下一版运行时：

> 不应该每次重新怀疑同一对样本。

---

# 二百六十四、这叫：

# Adjudicated Pair

人工裁决过的 Pair。

---

# 二百六十五、以后这些 Pair：

> 还能成为 Dedup 算法自己的 Gold Set。

---

# 二百六十六、例如人工标：

```text
Pair 1:
duplicate

Pair 2:
template_variant

Pair 3:
not_duplicate
```

---

# 二百六十七、然后评测 Dedup Algorithm：

```text
Precision
Recall
```

---

# 二百六十八、和第一课学的一样。

---

# 二百六十九、如果系统说：

> 100 对是 Duplicate。

其中：

> 95 对真的重复。

Dedup Precision：

> 很高。

---

# 二百七十、如果真实共有：

> 200 对 Duplicate，

系统只找到：

> 100 对。

Recall：

> 就不高。

---

# 二百七十一、对删除型 Dedup：

> Precision 尤其重要。

为什么？

因为 False Positive：

> 会误删数据。

---

# 二百七十二、所以我们通常不希望：

> “宁可多删一点。”

---

# 二百七十三、而更倾向：

> **宁可把不确定的留作 Cluster Candidate。**

---

# 二百七十四、现在看一个 Procurement Dedup Gold Set 应该覆盖什么？

至少包括：

```text
完全重复文件
不同格式同内容
镜像网页
空格/标点差异
项目名称替换
日期替换
金额替换
数字条件变化
否定词变化
更正版本
模板复用
同义改写
Hard Negative
```

---

# 二百七十五、特别是：

```text
2小时
vs
4小时
```

---

# 二百七十六、

```text
不得
vs
应当
```

---

# 二百七十七、

```text
本市
vs
项目所在地
```

---

# 二百七十八、

```text
500万元
vs
5000万元
```

这些必须：

> 专门测试。

---

# 二百七十九、否则一个普通互联网文本 Dedup 方法：

> 在采购数据上可能非常危险。

---

# 二百八十、现在设计第一版 `DedupedClauseSet_V0.1`。

例如：

```json
{
  "clause_id": "CLAUSE-00178",

  "duplicate_group_id": "DG-000031",

  "canonical_clause_id": "CLAUSE-00178",

  "dedup_relation": "canonical",

  "template_group_id": "TG-000712",

  "exact_text_hash": "sha256:...",

  "similarity": {
    "jaccard": null,
    "embedding": null
  },

  "critical_differences": [],

  "dedup_status": "verified",

  "dedup_version": "dedup_v0.1"
}
```

---

# 二百八十一、另一个成员：

```json
{
  "clause_id": "CLAUSE-08317",

  "duplicate_group_id": "DG-000031",

  "canonical_clause_id": "CLAUSE-00178",

  "dedup_relation": "exact_text_duplicate",

  "dedup_status": "auto_verified"
}
```

---

# 二百八十二、模板相同但金额不同：

```json
{
  "clause_id": "CLAUSE-10291",

  "duplicate_group_id": null,

  "template_group_id": "TG-000712",

  "dedup_relation": "template_variant",

  "critical_differences": [
    "amount"
  ]
}
```

---

# 二百八十三、看到区别了吗？

它并没有：

> 被删除。

---

# 二百八十四、只是知道：

> 和谁同模板。

这对 Stage 6：

> Split

非常有价值。

---

# 二百八十五、后面我们甚至可以决定：

```text
同一个template_group
尽量不要同时跨Train/Test
```

---

# 二百八十六、这会显著减少：

# Template Leakage

---

# 二百八十七、现在谈 Dedup Version。

和前面一样：

```text
dedup_v0.1
```

以后可能升级：

```text
dedup_v0.2
```

---

# 二百八十八、为什么？

因为阈值会变。

算法会变。

Template Mask 规则会变。

---

# 二百八十九、同一个 Pair：

v0.1 可能认为：

```text
near_duplicate
```

v0.2 可能认为：

```text
template_variant
```

---

# 二百九十、所以每条决定：

> 必须知道是哪一版 Dedup Pipeline 产生的。

---

# 二百九十一、现在 Stage 1～5 已经有：

```text
schema_version
parser_version
structure_version
normalizer_version
dedup_version
```

---

# 二百九十二、到了第 11 阶段，

这些会被正式组织成：

# Dataset Lineage

---

# 二百九十三、现在说一个特别容易误解的地方：

# 去重不是为了让数据数量变小

数据变小只是：

> 副作用。

---

# 二百九十四、真正目标是让：

```text
样本权重更合理
信息多样性更高
评测更诚实
训练更高效
```

---

# 二百九十五、如果最后：

```text
100万
↓
92万
```

但 92 万信息质量很好：

> 完全没问题。

---

# 二百九十六、如果：

```text
100万
↓
20万
```

也不一定：

> 就更高级。

---

# 二百九十七、核心不是：

> 去掉多少。

而是：

> 去掉了什么。

---

# 二百九十八、现在看训练层面的影响。

假设有：

```text
10万条普通标准条款
```

重复很多。

而：

```text
1000条技术参数倾向性Hard Case
```

非常少。

---

# 二百九十九、不做 Dedup / Reweight：

模型训练梯度大量来自：

> 简单标准条款。

---

# 三百、模型最后可能表现：

```text
普通资格条件：
99%

复杂技术参数：
55%
```

---

# 三百零一、总体 Accuracy：

> 看起来很高。

---

# 三百零二、实际业务：

> 关键地方很差。

---

# 三百零三、所以 Dedup 和 Rebalancing：

> 会直接影响模型学什么。

---

# 三百零四、但注意：

# Dedup ≠ Class Balancing

这是两个问题。

---

# 三百零五、Dedup：

> 控制重复信息。

---

# 三百零六、Class Balancing：

> 控制不同 Label / Risk Type 的训练比例。

---

# 三百零七、后面构造 Dataset 时：

> 可能两者都要做。

不要混。

---

# 三百零八、现在看 RAG。

如果向量数据库里：

> 同一法规条款存了 30 份。

用户检索一次：

Top 10 结果可能全是：

> 同一句法规。

---

# 三百零九、结果：

> 检索多样性极差。

---

# 三百一十、于是 Dedup 也能改善：

# Retrieval Diversity

---

# 三百一十一、但如果 30 份来自：

> 30 个不同监管案例，

每个案例虽然引用同一法规，

案例上下文：

> 仍然不同。

---

# 三百一十二、所以 RAG 可能去重：

> 法规原文。

但保留：

> 不同案例。

---

# 三百一十三、再次体现：

# Entity-aware Dedup

按数据实体类型：

> 定义不同策略。

---

# 三百一十四、未来我们的 Master Data 可能有：

```text
Regulation
Project
Document
Clause
Case
Annotation
```

每种 Entity：

> Dedup Policy 不一样。

---

# 三百一十五、现在做几个思维实验。

### 思维实验 A

两个 PDF 的 SHA-256 一样。

它们是不是可以认为文件完全相同？

> 是，工程上可以极高置信度认为是 Exact File Duplicate。

---

# 三百一十六、### 思维实验 B

两个文件 Hash 不同。

正文是不是一定不同？

> 不是。

PDF Metadata、封装方式、HTML 模板都可能导致 Hash 不同。

---

# 三百一十七、### 思维实验 C

两个 Clause 文字完全相同，

但属于两个不同采购项目。

是不是应该物理删除一个？

> 不一定。

先看数据用途和是否属于自然重复。

---

# 三百一十八、### 思维实验 D

A：

```text
不少于3年
```

B：

```text
不少于5年
```

文本极其相似。

是不是 Near Duplicate？

> 可以是模板近重复。

但绝不能当业务等价 Duplicate 删除。

---

# 三百一十九、### 思维实验 E

两个招标文件 99.8% 相同，

其中一个是更正后版本。

删旧版本？

> 不应简单当重复处理。

应该建立 Version Relation。

---

# 三百二十、### 思维实验 F

Embedding Similarity = 0.99。

是不是可以自动删除一条？

> 不能。

需要检查数字、否定词、单位、比较符等业务关键差异。

---

# 三百二十一、### 思维实验 G

同一个模板在 1000 个项目中出现。

能不能让 800 个进 Train、200 个进 Test？

> 这可能造成严重 Template Leakage。

---

# 三百二十二、### 思维实验 H

同一法规在 5000 个采购文件里被引用。

是不是全都只留一次？

> 要看任务。

法规知识库和项目分析数据的去重目标不同。

---

# 三百二十三、### 思维实验 I

两条完全相同文本的 Label 不同。

应该随机保留一个吗？

> 不应该。

这是 Label Conflict，需要调查 Context 和标注来源。

---

# 三百二十四、### 思维实验 J

一条边界样本与常规样本 95% 相似。

是不是优先删边界样本？

> 恰恰相反。边界样本通常更有价值。

---

# 三百二十五、本阶段最容易犯的 12 个错误

**错误 1：**

> `drop_duplicates()` 就完成去重。

错。

---

**错误 2：**

> SHA-256 能发现所有重复。

错。

它只能非常好地发现完全文件重复。

---

**错误 3：**

> 文本一样就一定是同一个业务观察。

错。

---

**错误 4：**

> 相似度高就可以删除。

错。

---

**错误 5：**

> Embedding 很智能，所以最适合直接做删除决定。

危险。

---

**错误 6：**

> 数字差异很小，可以忽略。

错。

---

**错误 7：**

> 99% 相同的更正版本属于无用重复。

错。

---

**错误 8：**

> 模板重复只影响训练速度。

错。

还会制造模型偏差和 Benchmark 泄漏。

---

**错误 9：**

> 去重率越高，数据越专业。

错。

---

**错误 10：**

> 检测到重复就应该立刻物理删除。

错。

优先 Cluster / Link。

---

**错误 11：**

> Dedup 只影响训练集。

错。

它对 Evaluation 和 RAG 一样重要。

---

**错误 12：**

> 完全相同文本的不同 Label，任选一个即可。

错。

这可能暴露标注冲突。

---

# 三百二十六、本阶段最重要的 6 个“≠”

```text
File Difference
≠
Content Difference
```

```text
Text Duplicate
≠
Observation Duplicate
```

```text
Similarity
≠
Equivalence
```

```text
Template Similarity
≠
Business Equality
```

```text
Version Similarity
≠
Duplicate
```

```text
More Rows
≠
More Independent Information
```

---

# 三百二十七、再记一个非常重要的“=”

\[
\boxed{
GoodDedup
=
DuplicateDetection
+
RelationshipClassification
+
CriticalDifferenceProtection
+
ProvenancePreservation
}
\]

翻译成人话：

> **好的去重不是“把相似文本删掉”，而是先判断哪些数据彼此相关、它们到底是什么重复关系、有没有关键业务差异，再决定哪些只在训练 View 中降权或只保留代表样本，同时完整保留来源关系。**

---

# 三百二十八、现在把第四课前五阶段连起来

```text
Stage 1
Task Schema
“什么是一条样本？”
       │
       ▼
Stage 2
ParsedDocument
“文件里到底有什么？”
       │
       ▼
Stage 3
ClauseUnit
“文字属于哪一条业务要求？”
       │
       ▼
Stage 4
CleanClause
“怎样安全规范表示？”
       │
       ▼
Stage 5
DedupedClauseSet
“这些样本到底有多少独立信息？”
```

---

# 三百二十九、现在我们已经解决了：

```text
数据是什么
文本对不对
结构对不对
格式稳不稳
重复多不多
```

但还没有解决一个极其致命的问题：

# 这些数据怎样切 Train / Validation / Test？

---

# 三百三十、很多人会直接：

```python
train_test_split(
    data,
    test_size=0.2,
    random_state=42
)
```

看起来非常标准。

---

# 三百三十一、但对于 ProcurementAI，

如果按行随机切：

> 很可能直接把整个 Benchmark 做假。

---

# 三百三十二、因为同一个项目可能有：

```text
300个Clause
```

随机切以后：

```text
240条进Train
60条进Test
```

---

# 三百三十三、模型考试的时候虽然没见过：

> Test 的具体那句话。

但是它已经见过：

```text
项目名称
项目背景
模板风格
相关条款
大量相邻内容
```

---

# 三百三十四、更麻烦的是：

同一个 Template Group：

> 也可能跨 Train/Test。

---

# 三百三十五、所以真正正确的数据切分必须考虑：

```text
Project Group
Document Group
Duplicate Group
Template Group
Time
```

---

# 三百三十六、本阶段掌握测试

如果现在不看前文，你能完整解释下面这些问题，第 5 阶段就真正掌握了：

> 为什么数据行数不等于独立信息量？

> 什么是 Exact File Duplicate？

> SHA-256 能解决哪一层去重？

> 为什么文件 Hash 不同不代表正文不同？

> File Duplicate 和 Content Duplicate 有什么区别？

> 为什么需要 Document-level 和 Clause-level Dedup？

> Text Duplicate 和 Observation Duplicate 为什么不同？

> 什么是 Natural Repetition？

> 什么是 Artificial Duplication？

> 为什么真正优先去掉的是人工采集过程制造的重复？

> 为什么 Dedup Policy 必须根据 Dataset Purpose 决定？

> 为什么检测到 Duplicate 不应该立即物理删除？

> 什么是 Canonical Record？

> 为什么要建立 Duplicate Group？

> 什么叫 Near Duplicate？

> Jaccard Similarity 的直觉是什么？

> 为什么高 Jaccard 相似度不等于业务等价？

> 为什么 `不得` 和 `必须` 是 Dedup 中必须保护的差异？

> 为什么 `2小时` 和 `4小时` 不能因为文本高度相似而合并？

> 什么叫 Template Duplicate？

> 为什么采购数据里模板重复特别常见？

> 什么是 Template View？

> 为什么 Template View 只能用于检测，不能替代原文？

> 为什么数字 Mask 必须谨慎？

> 什么叫 Version Duplicate / Version Relation？

> 为什么更正前后文件不能简单去重？

> 什么是 Shingle？

> MinHash 的核心用途是什么？

> 为什么大规模数据不能全部两两比较？

> LSH 的直觉是什么？

> Embedding 可以在 Near Dedup 中做什么？

> 为什么 Embedding Similarity 不等于 Business Equivalence？

> 什么是 Critical Field Diff？

> 为什么应该先 Cluster，再 Delete？

> Duplicate Group 为什么以后必须参与 Train/Test Split？

> 什么是 Template Leakage？

> 为什么同一个模板随机进入 Train 和 Test 会导致虚假高分？

> 为什么不同数据实体需要不同 Dedup Policy？

> 为什么相同文本、不同 Label 应该触发 Label Conflict Review？

> 为什么边界案例不能因为和普通样本相似就删除？

> 什么叫 False Merge？

> 什么叫 Missed Duplicate？

> 对政府采购数据来说，为什么 False Merge 往往特别危险？

> 为什么 Dedup Algorithm 自己也需要 Gold Set 和 Benchmark？

> 为什么 Dedup 和 Class Balancing 不是一回事？

如果这些你都能讲清楚：

\[
\boxed{
第四课第5阶段真正掌握
}
\]

---

# 三百三十七、本阶段最终只记一句话

> **政府采购数据去重的目标不是“把相似文本删掉”，而是识别同一文件、同一正文、同一模板、同一版本链和语义近重复之间的关系，保护数字、否定词、单位和条件等关键业务差异，并通过 Duplicate Group 控制重复信息对训练权重和 Benchmark 的污染。**

最后压成一张图：

```text
                   CleanClauseSet
                         │
                         ▼
                Exact File Duplicate
                         │
                         ▼
                 Exact Text Duplicate
                         │
                         ▼
                   Near Duplicate
            ┌────────────┼─────────────┐
            ▼            ▼             ▼
         MinHash      Template       Embedding
            │            │             │
            └────────────┼─────────────┘
                         ▼
                 Critical Field Diff
            ┌────────────┼─────────────┐
            ▼            ▼             ▼
          数字          否定词         单位/符号
            │            │             │
            └────────────┼─────────────┘
                         ▼
             Duplicate Relation Type
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
       Exact          Template        Version
      Duplicate        Variant        Relation
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                  Duplicate Cluster
                         │
                         ▼
                 Canonical Selection
                         │
                         ▼
                DedupedClauseSet_V0.1
```

---

# 下一阶段：第四课 · 第 6 阶段
## Train / Validation / Test 到底应该怎么切？为什么对政府采购数据“随机按行切 8:1:1”可能从根本上就是错的？

第 6 阶段我们会第一次真正建立：

# Data Split

但不会只讲：

```text
80%
10%
10%
```

真正重要的是：

> **什么东西绝对不能被拆到两个数据集里。**

我们会把今天得到的：

```text
duplicate_group_id
template_group_id
```

和之前已经保存的：

```text
project_id
document_id
```

真正串起来。

最终会建立：

```text
Project-aware Split
+
Duplicate-aware Split
+
Template-aware Split
+
Time-aware Split
```

并第一次回答这个最核心的问题：

> **测试集到底应该模拟“同一批项目里的陌生条款”，还是模拟“未来真正从未见过的新项目”？**

第 6 阶段最终会产出：

# `DatasetSplit_V0.1`

也就是第一次把数据从“整理好的样本库”，推进成：

> **可以开始严肃训练和评测的 Train / Validation / Test 数据结构。**

---

<!-- LESSON 04 STAGE 05 END -->


<!-- LESSON 04 STAGE 06 START -->

# 第四课 · 第 6 阶段：Train / Validation / Test 到底应该怎么切？
## 为什么对政府采购数据“随机按行切 8:1:1”可能从根本上就是错的？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Benchmark 泄漏不一定是把答案文件直接放进训练集。**
2. **Split 的单位不一定是 Row， 很多时候应该是 Project / Group**
3. **Train / Validation / Test 的核心区别 不是“比例”，而是“用途”**
4. **同一个 Project 的 Clause 通常不应该跨 Train / Test**
5. **Duplicate Group / Template Group 也不能随便跨 Split**
6. **时间是最接近真实生产环境的一种隔离方式**
7. **Test Set 一旦开始被反复看， 它就正在慢慢变成 Train Set**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |
| `Validation` | 验证集：开发阶段用于选模型、调参数和早停 |
| `Split` | 数据切分：按项目/时间/地区划分训练、验证、测试数据 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `Dataset` | 数据集：按统一 Schema、版本和质量标准组织的样本集合 |
| `Sample` | 样本：具有明确输入、目标和来源的一条训练/评测记录 |
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `Accuracy` | 准确率：全部样本中判断正确的比例 |
| `Checkpoint` | 检查点：保存模型和训练状态以便恢复/发布 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |
| `Metadata` | 元数据：项目、来源、时间、地区、版本等辅助信息 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |

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

第五阶段结束以后，我们已经把数据从：

```text
CleanClause_V0.1
```

推进到了：

```text
DedupedClauseSet_V0.1
```

现在每一条 Clause 不仅知道：

```text
它来自哪个 project
它来自哪个 document
它属于哪个 section
它的原始文本是什么
它的规范化文本是什么
它有没有重复关系
它属于哪个 duplicate group
它属于哪个 template group
```

于是很多人接下来会非常自然地写：

```python
from sklearn.model_selection import train_test_split

train, test = train_test_split(
    data,
    test_size=0.2,
    random_state=42
)
```

甚至再切一次：

```text
80% Train
10% Validation
10% Test
```

看起来非常标准。

教科书里也经常这么写。

但对于我们的政府采购数据：

> **这可能从数据集设计的第一步就把 Benchmark 做假。**

今天这一阶段要解决的，不是“80%、10%、10%怎么写代码”。

而是一个更本质的问题：

# 什么东西绝对不能被拆到不同数据集里？

---

# 一、本阶段真正要解决的一个核心问题

今天只解决：

> **怎样把政府采购数据切成真正独立的 Train / Validation / Test，使 Test 尽量模拟模型未来遇到的“新项目”，而不是偷偷把训练数据的兄弟姐妹拿来考试？**

最终我们要产出：

# `DatasetSplit_V0.1`

从第五阶段：

```text
DedupedClauseSet_V0.1
```

推进到：

```text
Train
Validation
Test
```

但真正的流水线应该是：

```text
DedupedClauseSet
        ↓
Leakage Groups
        ↓
Group-aware Split
        ↓
Distribution Check
        ↓
Leakage Audit
        ↓
Frozen Test Set
        ↓
DatasetSplit_V0.1
```

---

# 二、先建立本阶段最重要的 6 个核心心智模型

先把这六句话钉住：

```text
① Split 的单位不一定是 Row，
   很多时候应该是 Project / Group

② Train / Validation / Test 的核心区别
   不是“比例”，而是“用途”

③ 同一个 Project 的 Clause
   通常不应该跨 Train / Test

④ Duplicate Group / Template Group
   也不能随便跨 Split

⑤ 时间是最接近真实生产环境的一种隔离方式

⑥ Test Set 一旦开始被反复看，
   它就正在慢慢变成 Train Set
```

最后一句非常重要。

以后会发现：

> Benchmark 泄漏不一定是把答案文件直接放进训练集。

人类不断根据 Test 调模型：

> 一样会泄漏。

---

# 三、先彻底理解 Train、Validation、Test 各自在干什么

很多人知道三个名字。

但没有真正理解它们的角色。

我们先不用机器学习术语。

用：

# 上课、模拟考试、期末考试

来类比。

---

# 四、Train Set 是什么？

Train：

> 教材 + 平时练习题。

模型训练时：

```text
直接看到这些样本
```

并根据这些样本：

> 修改 Weight。

---

# 五、也就是说

Train 数据直接影响：

\[
\boxed{
ModelParameters
}
\]

这是模型真正：

> “学过”的内容。

---

# 六、例如我们有一条：

```text
供应商须在本市注册。
```

Train Label：

```text
potential_risk
```

模型通过训练：

> 学习这种判断模式。

---

# 七、Validation Set 是什么？

Validation：

> 模拟考试。

它的作用不是：

> 更新模型 Weight。

而是帮助我们决定：

```text
哪个模型更好？
训练几轮？
Learning Rate多少？
LoRA Rank多少？
哪个Prompt更好？
哪个Threshold更好？
哪个Checkpoint最好？
```

---

# 八、也就是说 Validation 会影响：

# Model Selection

虽然模型没有直接对 Validation 做梯度下降，

但人类会根据 Validation：

> 改系统。

---

# 九、举个例子

我们训练：

```text
Checkpoint A
Checkpoint B
Checkpoint C
```

Validation Accuracy：

```text
A = 82%
B = 86%
C = 84%
```

于是我们选：

```text
B
```

Validation：

> 已经影响了最终模型。

---

# 十、所以 Validation 其实不是“完全没被模型见过”

更准确说：

> **它没有直接用于参数梯度更新，但它参与了整个开发决策。**

---

# 十一、Test Set 是什么？

Test：

> 真正期末考试。

它应该尽量只回答：

> **整个模型和开发流程完成以后，对真正没参与开发决策的数据表现如何？**

---

# 十二、所以三个集合可以记成

```text
Train
=
学

Validation
=
选

Test
=
最后考
```

---

# 十三、这三个字比 8:1:1 更重要

因为：

> 比例是工程参数。

角色：

> 才是统计意义。

---

# 十四、所以第二个核心心智模型可以写成

\[
\boxed{
Train = Learn
}
\]

\[
\boxed{
Validation = Select
}
\]

\[
\boxed{
Test = Estimate
}
\]

Test 最终在估计：

> 模型面对真正新数据的能力。

---

# 十五、为什么随机按行切在采购数据中危险？

先看一个非常具体的例子。

假设一个采购项目：

```text
Project P001
```

有：

```text
300个Clause
```

---

# 十六、里面包括

```text
资格条件：40条
技术参数：120条
商务要求：50条
评分标准：60条
合同条款：30条
```

---

# 十七、如果我们按行随机切 80/10/10

大概会得到：

```text
P001
├── 240条 → Train
├── 30条  → Validation
└── 30条  → Test
```

看起来：

> 很公平。

实际上：

> 非常危险。

---

# 十八、为什么？

Test 中虽然某一句 Clause：

> 没进入 Train。

但是 Train 已经包含：

```text
同一个项目名称
同一个采购需求
同一个项目预算
同一种排版
同一套模板
同一批技术参数
同一章上下文
同一个采购代理机构写作习惯
```

---

# 十九、于是 Test 不是在问：

> 模型能不能处理一个新采购项目？

而更像在问：

> **看过这本书 80% 内容以后，能不能猜剩下 10%？**

---

# 二十、这当然比处理一本从没见过的新书容易。

---

# 二十一、所以这里发生的是

# Group Leakage

分组泄漏。

---

# 二十二、最常见的 Group 就是：

# Project

因此第一条极其重要的原则：

\[
\boxed{
同一个Project
尽量只属于一个Split
}
\]

---

# 二十三、也就是说

正确方式更像：

```text
Project P001
全部 → Train

Project P002
全部 → Train

Project P003
全部 → Validation

Project P004
全部 → Test
```

---

# 二十四、而不是：

```text
P001的一部分 → Train
P001的一部分 → Validation
P001的一部分 → Test
```

---

# 二十五、这叫

# Group-aware Split

按 Group 切分。

---

# 二十六、第一个核心概念出现了

\[
\boxed{
SplitUnit
\neq
SampleRow
}
\]

Split Unit：

> 不一定是一行样本。

对于我们的项目：

> 经常是一个 Project Group。

---

# 二十七、为什么不是 Document？

假设一个项目有：

```text
招标文件
更正公告
采购公告
评分附件
合同草案
```

如果按 Document 切：

```text
招标文件 → Train
更正公告 → Test
```

还是可能泄漏。

---

# 二十八、因为它们属于：

> 同一个真实采购事件。

所以：

```text
project_id
```

通常比：

```text
document_id
```

更适合作为基础 Split Group。

---

# 二十九、这就是为什么第一阶段我们那么早就要求：

```text
project_id
```

必须保存。

当时可能觉得：

> 一个 Metadata 字段而已。

现在终于看到：

> 没有它，Benchmark 甚至可能无法正确建立。

---

# 三十、这就是好 Schema 的长期价值

前面一个字段设计正确，

后面：

> 省掉大量返工。

---

# 三十一、但是 Project Group 就够了吗？

不够。

第五阶段刚刚发现：

```text
Project A
```

和：

```text
Project B
```

虽然 project_id 不同，

可能：

> 使用完全相同的采购模板。

---

# 三十二、例如：

Project A：

> 智慧校园系统项目。

Project B：

> 智慧政务系统项目。

两个项目来自：

> 同一个代理机构。

---

# 三十三、资格条件几乎完全一样：

```text
供应商须……
供应商应……
供应商不得……
```

只替换：

```text
项目名称
项目编号
预算
日期
```

---

# 三十四、于是：

```text
Project A → Train
Project B → Test
```

表面上：

> Project 隔离了。

但实际上：

> Template 泄漏了。

---

# 三十五、这就是：

# Template Leakage

第五阶段已经见过。

现在它第一次变成：

> Split 设计问题。

---

# 三十六、所以我们还需要考虑：

```text
template_group_id
```

---

# 三十七、例如：

```text
TG-0017
├── Project A
├── Project B
├── Project C
├── Project D
└── Project E
```

---

# 三十八、如果我们真的要测试：

> 对新模板的泛化能力，

这五个项目：

> 最好不要跨 Train/Test。

---

# 三十九、于是 Split Group 开始变复杂：

```text
Project Group
+
Duplicate Group
+
Template Group
```

---

# 四十、接下来还有一个 Group

# Duplicate Group

假设：

```text
Clause A
```

和：

```text
Clause B
```

是同一内容不同格式。

第五阶段已经放进：

```text
DG-0031
```

---

# 四十一、如果：

```text
A → Train
B → Test
```

那几乎就是：

> 开卷考试。

---

# 四十二、所以所有：

```text
duplicate_group_id
```

成员：

> 绝对不应该跨 Train/Test。

---

# 四十三、因此我们已经有第一版 Leakage Constraint：

```text
同Project
不能跨Train/Test

同DuplicateGroup
不能跨Train/Test

高相似TemplateGroup
尽量不能跨Train/Test
```

---

# 四十四、这可以写成一个非常直观的数学约束

对任意 Group \(G\)：

\[
\boxed{
G
\subseteq
Train
\quad
\text{or}
\quad
G
\subseteq
Validation
\quad
\text{or}
\quad
G
\subseteq
Test
}
\]

不能：

\[
G
\cap Train \neq \varnothing
\]

同时又：

\[
G
\cap Test \neq \varnothing
\]

---

# 四十五、翻译成人话：

> **同一个泄漏群体只能进一个集合。**

---

# 四十六、但现在出现一个麻烦问题

假设：

```text
Project A
```

和：

```text
Project B
```

不同 Project。

但共享：

```text
Template Group T1
```

---

# 四十七、同时：

Project B 的某条 Clause

又和：

Project C 的 Clause

属于：

```text
Duplicate Group D7
```

---

# 四十八、那么：

```text
A
↔ Template
B
↔ Duplicate
C
```

实际上：

> 三个 Project 被连接起来了。

---

# 四十九、这时不能：

```text
A → Train
B → Train
C → Test
```

因为：

B 和 C：

> 有 Duplicate Link。

---

# 五十、所以更专业的做法是：

# Build Leakage Graph

建立泄漏关系图。

---

# 五十一、节点可以是：

```text
Project
```

边可以是：

```text
Duplicate Relation
Template Relation
Version Relation
```

---

# 五十二、例如：

```text
Project A
   │ Template
   ▼
Project B
   │ Duplicate
   ▼
Project C
```

那么 A、B、C：

> 可能应该作为一个 Connected Group。

---

# 五十三、也就是：

# Connected Component

连通分量。

---

# 五十四、别被术语吓到。

生活类比：

假设老师规定：

> 同一家族的人不能有人进训练题库、有人进考试题库。

---

# 五十五、A 是 B 的兄弟。

B 是 C 的兄弟。

即使 A 和 C：

> 没直接关系。

A、B、C 仍然属于：

> 同一个家庭群。

---

# 五十六、数据也是一样。

只要通过高风险泄漏关系：

> 连起来，

就可以考虑：

> 整体一起 Split。

---

# 五十七、这会形成：

```text
split_group_id
```

例如：

```text
SG-0001
```

里面：

```text
Project A
Project B
Project C
```

---

# 五十八、然后真正切的是：

# Split Group

而不是：

# Clause Row

---

# 五十九、于是第一版总关系变成：

```text
Clause
  ↓
Document
  ↓
Project
  ↓
Duplicate / Template Relations
  ↓
Leakage Connected Group
  ↓
split_group_id
```

---

# 六十、这个 `split_group_id`

以后极其重要。

---

# 六十一、现在理解 Train / Validation / Test 的真正切分单位了

不是：

```text
一条 Clause
```

而更像：

```text
一个独立信息群体
```

---

# 六十二、于是我们可以把今天核心压成：

\[
\boxed{
真正的Split
是在切独立信息源
而不是在切行
}
\]

---

# 六十三、现在讨论比例

是不是一定要：

```text
80 / 10 / 10
```

不是。

---

# 六十四、常见比例可能有：

```text
80 / 10 / 10
```

也可能：

```text
70 / 15 / 15
```

或者：

```text
90 / 5 / 5
```

---

# 六十五、真正应该问的是：

> Test 是否足够大，能稳定估计业务能力？

以及：

> Validation 是否足够支撑模型选择？

---

# 六十六、假设只有：

```text
1000个项目
```

Test 放：

```text
100个项目
```

可能已经不错。

---

# 六十七、如果有：

```text
100万个项目
```

Test 未必需要：

> 10 万个。

因为评测成本：

> 很高。

---

# 六十八、特别是 Expert Gold Set

人工高质量审核：

> 非常昂贵。

所以 Test 比例：

> 不是越大越好。

---

# 六十九、真正重要的是

# Effective Test Size

有效测试规模。

---

# 七十、如果 Test 有：

```text
100,000条Clause
```

但是：

> 90,000 条来自同一个模板，

有效信息量：

> 可能远少于 100,000。

---

# 七十一、反过来，

Test 只有：

```text
5,000条
```

但覆盖：

```text
100个项目类型
多个地区
多种风险
大量Hard Case
```

可能：

> 更有价值。

---

# 七十二、所以 Test Size 不应该只看：

# Row Count

还要看：

# Diversity

---

# 七十三、再次出现第五阶段那个公式：

\[
\boxed{
MoreRows
\neq
MoreInformation
}
\]

---

# 七十四、现在进入第二个大问题

# Distribution

如果按 Group 切，

有可能出现：

```text
Train
90% 技术参数

Test
70% 资格条件
```

---

# 七十五、这时候 Test 分数不好，

不一定是：

> 模型泛化特别差。

可能只是：

> Train 和 Test 的任务组成完全不一样。

---

# 七十六、所以一般需要检查：

# Label Distribution

例如五类风险：

```text
qualification
technical
commercial
scoring
requirements
```

---

# 七十七、我们希望 Train / Val / Test：

> 不一定完全一样，

但至少知道：

> 各自分布是什么。

---

# 七十八、例如：

| Risk Type | Train | Val | Test |
|---|---:|---:|---:|
| Qualification | 21% | 20% | 22% |
| Technical | 29% | 30% | 28% |
| Commercial | 18% | 17% | 19% |
| Scoring | 17% | 18% | 16% |
| Requirements | 15% | 15% | 15% |

这种比较容易解释。

---

# 七十九、但是不要为了让比例漂亮：

> 把同 Project 拆开。

---

# 八十、也就是说

# Group Integrity

优先级通常高于：

# Perfect Stratification

---

# 八十一、这是很重要的权衡。

你不能为了：

```text
每类刚好20%
```

把同一个项目：

> 拆进三个集合。

---

# 八十二、因此我们需要：

# Group-aware Stratification

不是普通 Stratification。

---

# 八十三、什么是 Stratification？

简单说：

> 切分时尽量保持类别比例。

---

# 八十四、普通二分类：

```text
正样本 20%
负样本 80%
```

希望：

Train / Val / Test：

> 都大约保持这个比例。

---

# 八十五、但我们的 Group 很大。

一个项目可能有：

```text
80% technical
20% commercial
```

另一个项目：

```text
90% scoring
```

---

# 八十六、所以 Group-aware Stratification 本质上变成一个：

# Packing Problem

---

# 八十七、就像有很多箱子。

每个箱子里装：

> 不同比例的彩球。

你不能拆箱。

现在要把箱子分成：

```text
Train堆
Val堆
Test堆
```

同时尽量让：

> 三堆颜色分布合理。

---

# 八十八、这就是 Group Split 的现实难度。

---

# 八十九、因此切分算法不一定一次随机完成。

可以：

```text
多次候选 Split
↓
计算分布偏差
↓
选择较好的
```

---

# 九十、甚至用优化算法。

但第一版不需要复杂。

先建立正确原则：

> **Group First, Balance Second。**

---

# 九十一、现在看另一个很重要的维度：

# Positive / Negative

假设 Risk Review 数据：

```text
Potential Risk
No Risk
Needs Review
```

---

# 九十二、如果 Test 几乎全是：

```text
No Risk
```

模型只要一直回答：

```text
No Risk
```

Accuracy：

> 可能很漂亮。

---

# 九十三、但风险识别：

> 完全没用。

---

# 九十四、所以 Test 必须保证：

> 业务关键类别有足够样本。

---

# 九十五、尤其我们最终最关心：

# False Negative

真正有风险的条款，

模型却说：

> 没风险。

---

# 九十六、这类样本在 Test：

> 必须有足够规模。

---

# 九十七、所以 Test 设计本质上是：

# Evaluation Design

不是简单 Data Split。

---

# 九十八、你想测什么能力，

就必须：

> 在 Test 里有对应案例。

---

# 九十九、例如想测：

```text
技术参数倾向性
```

如果 Test：

> 只有 8 条这种案例。

那结果：

> 波动会非常大。

---

# 一百、8 条里错 1 条：

Accuracy：

```text
87.5%
```

错 2 条：

```text
75%
```

---

# 一百零一、样本太少：

> 一条错误就大幅改变指标。

---

# 一百零二、所以关键 Slice：

> 需要最小样本量。

---

# 一百零三、这和第八课的 Gold Benchmark 会深度连接。

现在先记：

> **Test 不只是总量够，还要每个关键 Slice 够。**

---

# 一百零四、现在进入今天非常重要的主题：

# Time-aware Split

时间切分。

---

# 一百零五、假设我们有：

```text
2023
2024
2025
2026
```

四年的采购项目。

---

# 一百零六、我们可以随机按项目切。

也可以：

```text
2023～2025
→ Train

2026年1～6月
→ Validation

2026年7～9月
→ Test
```

---

# 一百零七、后者更接近什么？

现实部署。

---

# 一百零八、真实生产环境永远是：

```text
过去的数据
      ↓
训练
      ↓
面对未来的数据
```

模型不可能：

> 用未来数据训练以后再回到过去部署。

---

# 一百零九、所以从真实业务模拟角度：

# Temporal Split

时间切分非常强。

---

# 一百一十、可以写成：

\[
\boxed{
TrainTime
<
ValidationTime
<
TestTime
}
\]

---

# 一百一十一、这个方法特别能检测：

# Temporal Generalization

模型能不能：

> 对未来的新项目继续工作。

---

# 一百一十二、这比纯随机 Split：

> 更难。

但也：

> 更真实。

---

# 一百一十三、为什么时间切分通常更难？

因为未来会发生：

```text
政策变化
法规更新
采购模板变化
新技术产品出现
新项目类型出现
语言表达变化
```

---

# 一百一十四、所以 Test 不再只是：

> 同一分布的随机样本。

而开始包含：

# Distribution Shift

分布漂移。

---

# 一百一十五、这其实正是部署中：

> 真正会发生的事情。

---

# 一百一十六、比如 2025 年以前：

某类采购文件普遍使用：

```text
传统服务器参数
```

2026 年开始：

> 出现新的 AI 算力采购。

---

# 一百一十七、模型在历史数据训练以后，

能不能处理：

> 新采购类别？

Temporal Test：

> 能测出来。

---

# 一百一十八、但时间切分也不是永远必须。

取决于：

> 我们想回答什么问题。

---

# 一百一十九、例如研究问题 A：

> 在当前数据分布中，模型对新项目表现如何？

可以：

# Project Holdout

---

# 一百二十、研究问题 B：

> 用历史数据训练后，面对未来项目表现如何？

可以：

# Temporal Holdout

---

# 一百二十一、研究问题 C：

> 在某些未见地区能不能泛化？

可以：

# Geographic Holdout

---

# 一百二十二、比如：

```text
Train:
东部若干地区

Test:
一个从未进入训练的地区
```

---

# 一百二十三、这会测试：

> 区域泛化。

---

# 一百二十四、再比如：

# Agency Holdout

某些采购代理机构：

> 使用自己的模板。

---

# 一百二十五、如果同一家代理机构：

Train/Test 都有，

模型可能只是：

> 学会这个代理机构的模板。

---

# 一百二十六、所以甚至可以做：

```text
Agency-level Holdout
```

测试：

> 新机构。

---

# 一百二十七、这说明一个非常深的概念：

# Test Set should represent the generalization question

测试集应该代表：

> **你真正想知道的泛化问题。**

---

# 一百二十八、所以：

> “Test 怎么切？”

不能脱离：

> “未来模型要面对什么？”

---

# 一百二十九、这就是为什么没有万能：

```text
80/10/10
```

答案。

---

# 一百三十、现在给 ProcurementAI 建三个层级的评测 Split

这是一个很有价值的设计。

---

# 一百三十一、第一层：

# IID-like Project Holdout

虽然项目隔离，

但 Train/Test：

> 时间、地区、任务分布接近。

---

# 一百三十二、它回答：

> **面对同类分布中的新项目，模型表现如何？**

---

# 一百三十三、第二层：

# Temporal Holdout

Test 来自：

> 未来时间窗口。

---

# 一百三十四、它回答：

> **面对未来项目，性能掉多少？**

---

# 一百三十五、第三层：

# Stress / OOD Holdout

例如：

```text
新地区
新项目类型
稀有风险
Hard Negative
超长文档
复杂评分表
```

---

# 一百三十六、它回答：

> **模型离开舒适区以后会怎样？**

---

# 一百三十七、所以以后成熟 Benchmark 不一定只有：

# 一个 Test Set

可以有：

```text
Test-IID
Test-Future
Test-Hard
```

---

# 一百三十八、但是现在 Stage 6：

第一版先建立：

# 主 Train / Val / Test

并为后面：

> 多测试集

保留 Metadata。

---

# 一百三十九、现在看 Validation 怎么切

很多团队非常重视 Test 隔离，

但忽略 Validation。

---

# 一百四十、假设：

```text
Train
和Validation
大量共享模板
```

会发生什么？

---

# 一百四十一、你会根据 Validation：

> 选择模型。

模型 A：

> 更会背模板。

于是 Validation 分数高。

---

# 一百四十二、你最后选了 A。

虽然 Test 最终可能揭露问题，

但整个模型开发过程：

> 已经被 Validation 偏置。

---

# 一百四十三、所以 Validation 也应该：

> 做类似 Group Isolation。

---

# 一百四十四、通常我们希望：

\[
\boxed{
Train \cap Validation = \varnothing
}
\]

\[
\boxed{
Train \cap Test = \varnothing
}
\]

\[
\boxed{
Validation \cap Test = \varnothing
}
\]

当然这里不是只说：

> Row 不重叠。

而是：

# Leakage Group 不重叠

---

# 一百四十五、更准确可以写：

\[
\boxed{
SplitGroup_{Train}
\cap
SplitGroup_{Val}
=
\varnothing
}
\]

\[
\boxed{
SplitGroup_{Train}
\cap
SplitGroup_{Test}
=
\varnothing
}
\]

---

# 一百四十六、这才是我们真正关心的。

---

# 一百四十七、现在出现一个常见问题：

# 我数据很少怎么办？

假设只有：

```text
200个项目
```

再按 Group 切：

> Test 很小。

---

# 一百四十八、这时可以使用：

# Cross-validation

交叉验证。

---

# 一百四十九、但注意：

不能用普通 Row-level K-fold。

应该使用：

# Group K-fold

---

# 一百五十、例如 5 Fold：

```text
Project Group
```

整体进入一个 Fold。

---

# 一百五十一、每次：

```text
4份 Train
1份 Validation
```

轮流测试。

---

# 一百五十二、这样能够更充分利用小数据。

---

# 一百五十三、但对于最终 Test：

> 仍然最好保留独立 Holdout。

---

# 一百五十四、也就是说：

```text
Train/Dev Pool
       ↓
Group Cross Validation
```

用于开发。

另外：

```text
Final Test
```

彻底冻结。

---

# 一百五十五、这是一种很稳健的架构。

---

# 一百五十六、现在讲一个非常危险的现象：

# Test Set Peeking

偷看 Test。

---

# 一百五十七、比如第一次 Test：

```text
Accuracy = 78%
```

你查看错误：

> 技术参数类很差。

---

# 一百五十八、于是修改：

```text
Prompt
```

再跑 Test：

```text
82%
```

---

# 一百五十九、再发现：

> 评分条款不行。

又修改：

```text
Rule
```

Test：

```text
85%
```

---

# 一百六十、重复 50 次。

这个 Test 还是 Test 吗？

---

# 一百六十一、统计意义上：

> 越来越不像了。

因为你已经根据 Test：

> 开发系统。

---

# 一百六十二、Test 开始扮演：

# Validation

的角色。

---

# 一百六十三、所以第六个核心心智模型：

\[
\boxed{
RepeatedTestFeedback
\rightarrow
TestContamination
}
\]

---

# 一百六十四、人没有把 Test 文件直接送去训练。

但人类大脑：

> 已经在训练。

---

# 一百六十五、所以成熟项目通常有：

```text
Development Validation Set
```

可以经常看。

---

# 一百六十六、以及：

```text
Final Locked Test Set
```

尽量少碰。

---

# 一百六十七、甚至更成熟可以有：

# Hidden Test

开发者：

> 看不到答案。

---

# 一百六十八、每次提交模型：

> 自动评分。

这能减少：

> 人工针对 Test 调参。

---

# 一百六十九、第八课做 Benchmark 时，

我们会再次回到：

> Test Governance。

---

# 一百七十、现在看一个完整的泄漏案例

假设：

```text
Project P001
```

有 100 个 Clause。

其中一条：

```text
供应商须在本市设有服务机构。
```

---

# 一百七十一、另一个：

```text
Project P381
```

用了同一模板。

写成：

```text
供应商须在项目所在地设有服务机构。
```

---

# 一百七十二、现在：

```text
P001 → Train
P381 → Test
```

Project 不重复。

---

# 一百七十三、但：

```text
template_group_id
```

一样。

模型训练时：

> 见过大量高度相似表达。

---

# 一百七十四、测试成绩：

> 可能虚高。

---

# 一百七十五、是不是所有 Template Group 都必须严格隔离？

不一定。

---

# 一百七十六、这取决于：

> 你想测什么。

如果生产环境里：

> 未来确实会继续大量使用相同模板，

那么 Test 里出现同模板新项目：

> 也有现实意义。

---

# 一百七十七、所以成熟评测可以同时测两类：

```text
Seen-template New-project
```

和：

```text
Unseen-template New-project
```

---

# 一百七十八、这是一个非常专业的切片。

---

# 一百七十九、第一类回答：

> 模型面对熟悉模板的新项目能力如何？

---

# 一百八十、第二类回答：

> 模型面对陌生模板的新项目能力如何？

---

# 一百八十一、如果只给一个总分，

这两种能力：

> 会被混在一起。

---

# 一百八十二、所以我们以后可以有字段：

```text
template_seen_in_train = true / false
```

---

# 一百八十三、然后单独评测：

```text
Seen Template Accuracy
```

和：

```text
Unseen Template Accuracy
```

---

# 一百八十四、这就是 Metadata 的力量。

---

# 一百八十五、现在再看法规引用。

Train 项目和 Test 项目：

> 都引用同一法律条文。

这算泄漏吗？

---

# 一百八十六、不一定。

如果我们训练的是：

> 合规分析模型，

法规本来就是：

> 应该掌握的公共知识。

---

# 一百八十七、所以不能说：

> Test 里引用的法规在 Train 出现过，就一定泄漏。

---

# 一百八十八、这暴露了一个更深的概念：

# What is supposed to generalize?

---

# 一百八十九、我们真正希望模型泛化的是：

```text
新采购项目
新条款表达
新业务组合
```

而不是：

> 每次考试都必须遇到完全陌生的法律。

---

# 一百九十、所以：

# Shared Knowledge ≠ Leakage

---

# 一百九十一、但是：

# Shared Answer Instance

通常才是危险。

---

# 一百九十二、比如 Test Case：

```text
Clause + Expert Rationale
```

如果同一 Clause 和同一 Rationale：

> 已经进入 SFT Train。

这当然：

> 是严重泄漏。

---

# 一百九十三、所以 Leakage 判断要问：

> **模型训练时是否已经接触了这个测试问题本身，或者高度等价的答案实例？**

---

# 一百九十四、共享通用法规知识：

> 可以接受。

共享同一项目的判例式答案：

> 很危险。

---

# 一百九十五、这也为第七阶段：

# Data Leakage

铺路。

第六阶段重点是：

> 正确 Split。

第七阶段会专门研究：

> 即使 Split 看起来正确，数据仍然怎样偷偷泄漏。

---

# 一百九十六、现在看 Label Leakage 与 Split Leakage 的区别

第四课第一阶段讲过：

# Label Leakage

Input 里直接出现：

> 答案。

---

# 一百九十七、今天讲的是：

# Split Leakage

训练集和测试集之间：

> 信息隔离失败。

---

# 一百九十八、两者完全不同。

---

# 一百九十九、例如：

Input：

```text
专家判断：本条存在地域歧视。
原条款：……
```

这是：

> Label Leakage。

---

# 二百、而：

```text
同一项目的99条Clause在Train
第100条在Test
```

这是：

> Split Leakage。

---

# 二百零一、再比如：

```text
同一模板变体
Train/Test各一半
```

属于：

> Template Leakage。

---

# 二百零二、再比如：

```text
同一Duplicate Group
Train/Test各一个
```

属于：

> Duplicate Leakage。

---

# 二百零三、所以以后我们可以建立 Leakage Taxonomy：

```text
Label Leakage
Project Leakage
Document Leakage
Duplicate Leakage
Template Leakage
Temporal Leakage
Answer Leakage
```

---

# 二百零四、第七阶段会把这张图做完整。

---

# 二百零五、现在回到真正工程操作。

第一版 Split Pipeline 可以这样做。

---

# 二百零六、Step 1：确定 Split Objective

先写一句：

> Test 想模拟什么？

例如我们的 Baseline：

> **模拟模型面对未来从未参与训练的新政府采购项目时的风险审查能力。**

---

# 二百零七、这句话决定：

> 后面怎么 Split。

---

# 二百零八、Step 2：定义基础 Group

至少：

```text
project_id
```

---

# 二百零九、Step 3：加入泄漏关系

比如：

```text
duplicate_group_id
```

---

# 二百一十、必要时：

```text
template_group_id
```

---

# 二百一十一、Step 4：生成 `split_group_id`

将相互连接的项目：

> 合成不可拆单位。

---

# 二百一十二、Step 5：按 Group 分 Train / Val / Test

例如目标：

```text
80 / 10 / 10
```

只是：

> 近似目标。

---

# 二百一十三、Step 6：检查分布

至少检查：

```text
Risk Type
Positive / Negative
Region
Year
Project Type
Document Type
Difficulty
Case Type
```

---

# 二百一十四、Step 7：做 Cross-split Similarity Audit

即使 Group 已切好，

仍然再检查：

> Train 和 Test 是否有异常相似文本。

---

# 二百一十五、比如随机抽：

```text
每个Test Clause
```

去 Train：

> 找最相似邻居。

---

# 二百一十六、如果发现：

```text
Similarity = 0.998
```

就值得调查。

---

# 二百一十七、这个步骤非常强。

因为它能发现：

> 前面 Dedup 没抓到的泄漏。

---

# 二百一十八、我们可以保存：

```text
nearest_train_similarity
```

---

# 二百一十九、例如：

```json
{
  "test_clause_id": "C-991",
  "nearest_train_clause_id": "C-117",
  "similarity": 0.997
}
```

---

# 二百二十、然后人工检查：

> 是不是泄漏？

---

# 二百二十一、这就是：

# Leakage Audit

---

# 二百二十二、Step 8：冻结 Test

生成：

```text
split_version = split_v0.1
```

---

# 二百二十三、以后再训练：

> 不随意重新洗牌。

---

# 二百二十四、为什么不能每次训练都重新 Random Split？

因为模型 A：

> 用 Split A。

模型 B：

> 用 Split B。

最后两个分数：

> 不能公平比较。

---

# 二百二十五、所以：

# Benchmark Split 必须版本化

---

# 二百二十六、例如：

```text
ProcurementSplit_v0.1
```

以后模型全部：

> 用同一 Test。

---

# 二百二十七、如果数据规模大幅变化，

可以建立：

```text
v0.2
```

但不能：

> 偷偷改。

---

# 二百二十八、否则你会发现：

```text
Model A = 84%
Model B = 87%
```

实际上：

> 考卷不同。

---

# 二百二十九、这根本不能比较。

---

# 二百三十、所以每个实验记录：

```text
dataset_version
split_version
```

极其重要。

---

# 二百三十一、现在设计 `DatasetSplit_V0.1`

一条样本可以有：

```json
{
  "clause_id": "CLAUSE-00178",
  "project_id": "PROJECT-00152",

  "duplicate_group_id": null,
  "template_group_id": "TG-00017",
  "split_group_id": "SG-00091",

  "split": "train",

  "split_reason": "group_assignment",

  "split_version": "procurement_split_v0.1"
}
```

---

# 二百三十二、一个 Test 样本：

```json
{
  "clause_id": "CLAUSE-88102",
  "project_id": "PROJECT-09112",

  "template_group_id": "TG-00772",
  "split_group_id": "SG-03188",

  "split": "test",

  "template_seen_in_train": false,

  "split_version": "procurement_split_v0.1"
}
```

---

# 二百三十三、甚至可以加：

```text
time_bucket
region
project_category
```

帮助后面 Slice。

---

# 二百三十四、现在看一个非常实用的数据表

最终 Split Summary 可以自动生成：

| Metric | Train | Validation | Test |
|---|---:|---:|---:|
| Projects | 8,000 | 1,000 | 1,000 |
| Clauses | 320,000 | 39,000 | 41,000 |
| Positive Risk | 31% | 30% | 32% |
| Hard Negative | 7% | 8% | 8% |
| Unique Templates | 1,420 | 182 | 201 |
| Regions | 28 | 27 | 28 |

---

# 二百三十五、注意这里：

> 项目数和 Clause 数都要看。

---

# 二百三十六、因为有的 Project：

```text
10条Clause
```

有的：

```text
1000条Clause
```

---

# 二百三十七、如果只按 Project 数量：

```text
80 / 10 / 10
```

Clause 数量可能变成：

```text
60 / 20 / 20
```

---

# 二百三十八、所以 Split 是多目标平衡：

```text
Project数量
Clause数量
Label分布
Risk Type
Time
Region
Template
```

---

# 二百三十九、这就是为什么现实 Split：

> 比 `train_test_split()` 难很多。

---

# 二百四十、但是第一版不要追求数学完美。

只要做到：

```text
Group不泄漏
关键类别不过度失衡
Test具有足够覆盖
```

就已经：

> 非常专业。

---

# 二百四十一、现在看极端 Group Size

假设一个超级项目：

```text
Project Mega
```

有：

```text
50,000条Clause
```

---

# 二百四十二、而普通项目平均：

```text
100条
```

---

# 二百四十三、如果 Mega Project 被分到 Test，

整个 Test：

> 一半都被它占了。

---

# 二百四十四、怎么办？

不能把它随便拆掉。

因为：

> Group Integrity。

---

# 二百四十五、可以考虑：

```text
特殊大Group单独处理
```

例如：

> 不进入主 Benchmark，

单独成为：

# Stress Test

---

# 二百四十六、或者：

> 设计项目级采样。

---

# 二百四十七、这再次说明：

> 不要让一个异常项目支配整个指标。

---

# 二百四十八、类似还有：

# Very Large Template Group

一个模板覆盖：

```text
20,000个项目
```

---

# 二百四十九、如果严格不跨 Split，

可能：

> 整个数据集都难切。

---

# 二百五十、这时就要重新问：

> 我们是想测试“新项目”，还是“新模板”？

---

# 二百五十一、如果生产环境会继续使用这个主流模板，

可以允许：

> 同模板不同 Project 跨 Split。

但需要：

> 明确标记。

---

# 二百五十二、然后同时建立：

```text
Unseen-template Slice
```

专门测陌生模板。

---

# 二百五十三、这比强行：

> 所有 Template 永不跨 Split

更现实。

---

# 二百五十四、所以 Group Constraint 有两类：

# Hard Constraint

绝不能跨。

---

# 二百五十五、例如：

```text
同一个Project
Exact Duplicate Group
同一个Annotation Instance
```

通常：

> Hard。

---

# 二百五十六、第二类：

# Soft Constraint

最好隔离，

但根据评测目标：

> 可以允许。

例如：

```text
Template Group
Agency
Region
```

---

# 二百五十七、这张区别非常重要。

---

# 二百五十八、可以设计：

```text
Hard Leakage Groups:
Project
Exact Duplicate

Soft Generalization Groups:
Template
Agency
Region
```

---

# 二百五十九、Hard Group：

> 用于保证评测合法。

Soft Group：

> 用于定义评测难度。

---

# 二百六十、这是一个非常漂亮的框架。

---

# 二百六十一、例如主 Benchmark：

```text
Project-disjoint
Duplicate-disjoint
```

保证：

> 基本独立。

---

# 二百六十二、然后标记：

```text
Template Seen
Template Unseen
Region Seen
Region Unseen
```

用于：

> Slice Analysis。

---

# 二百六十三、这就避免把所有目标：

> 强行塞进一个 Split 规则。

---

# 二百六十四、现在进入另一个问题

# Time Leakage

假设你做 Temporal Split：

```text
2025以前 → Train
2026 → Test
```

看起来很严谨。

---

# 二百六十五、但你使用了一个：

```text
2026年12月生成的专家整理文档
```

它总结了：

> 2026 年全年案例。

然后把这份材料：

> 放进 Train。

---

# 二百六十六、虽然 Clause 时间是过去，

但知识来源：

> 包含未来。

这还是：

# Temporal Leakage

---

# 二百六十七、所以时间切分不能只看：

```text
project_date
```

还要考虑：

> 数据来源生成时间。

---

# 二百六十八、例如：

```text
annotation_date
knowledge_snapshot_date
```

都可能重要。

---

# 二百六十九、这将在第七阶段专门展开。

---

# 二百七十、现在看 Synthetic Data

以后模型会生成：

> 合成训练样本。

如果 Synthetic Sample 是从：

> Test Case 改写出来的。

---

# 二百七十一、即使字完全不同，

也可能：

> 把 Test 答案泄漏进 Train。

---

# 二百七十二、所以未来 Synthetic Data 也必须知道：

```text
source_sample_id
```

---

# 二百七十三、如果来源：

> 属于 Test，

它的派生数据：

> 不能进入 Train。

---

# 二百七十四、这叫：

# Lineage-aware Split

根据血缘切分。

---

# 二百七十五、非常重要。

我们前面一直保存：

# Data Lineage

现在再次产生巨大价值。

---

# 二百七十六、如果 Sample A：

> 派生出 Sample B、C、D。

那么：

```text
A → Test
```

B/C/D：

> 也应该跟着 Test 或被排除。

---

# 二百七十七、不能：

```text
A → Test
B → Train
```

然后说：

> 文本不一样，所以没事。

---

# 二百七十八、所以除了 Group Relation，

还有：

# Derivation Relation

---

# 二百七十九、最终 Split Graph 可能包括：

```text
Same Project
Exact Duplicate
Derived From
Same Original Case
```

这些都是：

> Hard Edges。

---

# 二百八十、可以画成：

```text
Sample A
├── duplicate → Sample B
├── derived   → Sample C
└── same_case → Sample D
```

A/B/C/D：

> 必须一起 Split。

---

# 二百八十一、这个思想非常强。

---

# 二百八十二、现在看一个很现实的 SFT 数据问题。

原始专家案例：

```text
Clause A
+
Expert Rationale A
```

---

# 二百八十三、我们让 LLM 产生：

```text
Paraphrase 1
Paraphrase 2
Paraphrase 3
```

作为数据增强。

---

# 二百八十四、如果原始 A：

> 在 Test。

Paraphrase：

> 进入 Train。

---

# 二百八十五、测试几乎必然虚高。

---

# 二百八十六、所以：

# Augmentation must inherit split

数据增强应该：

> 继承母样本 Split。

---

# 二百八十七、这句话以后做 SFT 时：

> 非常重要。

---

# 二百八十八、现在看 RAG Knowledge Corpus 和 Task Split 的关系。

假设我们评测：

> 法规风险审查。

Test Case 需要用某条法律。

RAG Knowledge Base：

> 包含这条法律。

是不是泄漏？

---

# 二百八十九、不是。

因为生产系统本来：

> 就应该允许查法规。

---

# 二百九十、这叫：

# Allowed External Knowledge

---

# 二百九十一、但是如果 RAG 知识库里：

> 直接存了 Test Case 的专家答案，

那就：

> 泄漏。

---

# 二百九十二、所以评测时必须定义：

```text
Allowed Knowledge
```

和：

```text
Forbidden Test-specific Knowledge
```

---

# 二百九十三、这会在第八课评测系统里正式解决。

现在先有意识。

---

# 二百九十四、现在做一个非常典型的 Split 失败案例。

数据：

```text
10,000个项目
400,000条Clause
```

随机按 Clause：

```text
320k Train
40k Val
40k Test
```

---

# 二百九十五、模型 Test Accuracy：

```text
94%
```

---

# 二百九十六、改成 Project-disjoint：

```text
86%
```

---

# 二百九十七、再改成 Unseen-template：

```text
74%
```

---

# 二百九十八、哪个分数是真的？

三个都可能是真的。

---

# 二百九十九、它们回答了三个不同问题。

94%：

> 看过同项目大量兄弟 Clause 后的能力。

---

# 三百、

86%：

> 面对新项目，但模板可能熟悉。

---

# 三百零一、

74%：

> 面对新项目 + 新模板。

---

# 三百零二、所以：

# Metric without Split Definition is almost meaningless

没有 Split 定义的分数：

> 几乎没有解释力。

---

# 三百零三、以后看到别人说：

> “我们的采购模型准确率 95%。”

你第一反应应该问：

```text
怎么切的？
```

---

# 三百零四、甚至比问：

```text
用什么模型？
```

更重要。

---

# 三百零五、因为一个错误 Split：

> 可以让普通模型看起来像超级模型。

---

# 三百零六、这就是 Dataset Engineering 对 AI 项目的影响。

---

# 三百零七、现在建立 `Split Manifest`

每次 Split 最好保存：

```text
split_version
random_seed
grouping_policy
date_boundary
hard_constraints
soft_constraints
created_at
dataset_version
```

---

# 三百零八、例如：

```json
{
  "split_version": "procurement_split_v0.1",
  "dataset_version": "procurement_dataset_v0.1",

  "strategy": "project_group_holdout",

  "hard_constraints": [
    "same_project_same_split",
    "exact_duplicate_same_split",
    "derived_sample_same_split"
  ],

  "soft_constraints": [
    "template_balance",
    "region_balance"
  ],

  "target_ratio": {
    "train": 0.8,
    "validation": 0.1,
    "test": 0.1
  },

  "random_seed": 20260915
}
```

这里的数字只是：

> 教学示例。

---

# 三百零九、为什么保存 Seed？

因为如果是可随机重现的 Split，

以后：

> 能重新生成。

---

# 三百一十、但仅保存 Seed 还不够。

还要保存：

```text
算法版本
排序方式
输入数据版本
```

---

# 三百一十一、否则同一个 Seed，

Dataset 变了以后：

> Split 也会变。

---

# 三百一十二、所以最稳妥还应该直接保存：

# Split Assignment Table

---

# 三百一十三、例如：

| project_id | split_group_id | split |
|---|---|---|
| P001 | SG001 | train |
| P002 | SG002 | train |
| P003 | SG003 | validation |
| P004 | SG004 | test |

---

# 三百一十四、这个表：

> 就是最终真相。

---

# 三百一十五、以后新增数据怎么办？

这是非常现实的问题。

---

# 三百一十六、假设今天有：

```text
Dataset v0.1
```

半年后新增：

```text
20万条
```

是不是重新把所有数据：

> 洗牌？

---

# 三百一十七、不建议随便这么做。

因为旧 Benchmark：

> 会失去连续性。

---

# 三百一十八、一个常见思路是：

旧 Test：

> 保持冻结。

新增项目：

> 进入 Train/Val，或者构建新的 Test v0.2。

---

# 三百一十九、例如：

```text
Test_v1
=
长期稳定回归集
```

---

# 三百二十、

```text
Test_v2
=
加入最新时间窗口
```

---

# 三百二十一、这样可以同时知道：

> 对历史稳定 Benchmark 有没有退化。

以及：

> 对新数据表现如何。

---

# 三百二十二、这就是：

# Benchmark Versioning

---

# 三百二十三、以后第八课会正式展开。

---

# 三百二十四、现在看看 Validation 是否也要冻结。

通常：

> 可以比 Test 灵活。

---

# 三百二十五、因为 Validation：

> 本来就用于开发。

随着任务变化：

> 可以增加新的 Validation Slice。

---

# 三百二十六、但为了实验公平，

某一轮模型比较：

> 仍然应该使用固定 Validation Version。

---

# 三百二十七、否则今天：

Model A 在 Val A。

明天：

Model B 在 Val B。

你又无法：

> 公平比较。

---

# 三百二十八、所以任何有分数的东西，

都应该知道：

```text
Dataset Version
Split Version
Benchmark Version
```

---

# 三百二十九、现在把第六阶段工程架构压缩成一张图

```text
                 DedupedClauseSet_V0.1
                          │
                          ▼
                    Build Hard Groups
             ┌────────────┼─────────────┐
             ▼            ▼             ▼
          Project      Duplicate      Lineage
             │            │             │
             └────────────┼─────────────┘
                          ▼
                    split_group_id
                          │
                          ▼
                   Group-aware Split
             ┌────────────┼─────────────┐
             ▼            ▼             ▼
           Train       Validation       Test
             │            │             │
             └────────────┼─────────────┘
                          ▼
                 Distribution Audit
                          │
                          ▼
                  Similarity Leakage Audit
                          │
                          ▼
                    Freeze Test
                          │
                          ▼
                  DatasetSplit_V0.1
```

---

# 三百三十、本阶段最容易犯的 12 个错误

### 错误 1

> 直接按 Clause 行随机 8:1:1。

对于采购数据：

> 很危险。

### 错误 2

> 同一个项目里的不同 Clause 可以随便分到 Train/Test。

容易产生 Project Leakage。

### 错误 3

> Document 不同，所以一定独立。

不一定。

可能同项目、同模板、同版本链。

### 错误 4

> Exact Duplicate 去掉以后就不会泄漏。

错。

还有 Near Duplicate 和 Template Leakage。

### 错误 5

> 比例必须严格 80/10/10。

错。

独立性和评测覆盖更重要。

### 错误 6

> 为了类别比例漂亮，可以拆 Project。

通常不值得。

### 错误 7

> Validation 泄漏没关系，只有 Test 需要干净。

错。

Validation 会影响模型选择。

### 错误 8

> Test 可以每天反复跑、反复看、反复调。

会逐渐污染 Test。

### 错误 9

> Temporal Split 只需要看项目发布日期。

不一定。

还要注意知识和标注来源的时间。

### 错误 10

> Synthetic Data 字不同，所以不会泄漏。

错。

需要看 Lineage。

### 错误 11

> 同一法规知识出现在 Train/Test 就一定是泄漏。

不一定。

共享公共知识和共享测试答案不是一回事。

### 错误 12

> 一个总 Accuracy 就足够评价 Split。

错。

必须看关键 Slice 和 Split 定义。

---

# 三百三十一、本阶段最重要的 6 个“≠”

```text
Row Split
≠
Independent Split
```

```text
Different Document
≠
Independent Project
```

```text
Different Project
≠
Different Template
```

```text
No Exact Duplicate
≠
No Leakage
```

```text
Fixed Ratio
≠
Good Benchmark
```

```text
Never Used for Gradient
≠
Never Influenced Development
```

最后一句描述的就是：

> Validation 和频繁查看的 Test。

---

# 三百三十二、再记住一个最重要的“=”

\[
\boxed{
GoodSplit
=
Independence
+
Representativeness
+
LeakageControl
+
Reproducibility
}
\]

翻译成人话：

> **好的数据切分不是把行数按比例切开，而是让 Train、Validation、Test 尽量来自彼此独立的信息群，同时保持业务代表性、控制重复和模板泄漏，并且整个切分过程可以复现和审计。**

---

# 三百三十三、Stage 1～6 现在已经形成一条完整的数据流水线

```text
Stage 1
Task Schema
“什么是一条样本？”
        │
        ▼
Stage 2
ParsedDocument
“原文件里到底有什么？”
        │
        ▼
Stage 3
ClauseUnit
“文字属于哪条业务要求？”
        │
        ▼
Stage 4
CleanClause
“怎样安全规范表示？”
        │
        ▼
Stage 5
DedupedClauseSet
“到底有多少独立信息？”
        │
        ▼
Stage 6
DatasetSplit
“哪些数据可以教模型，
哪些数据必须留着考试？”
```

现在我们第一次拥有：

> 真正意义上的 Train / Validation / Test。

---

# 三百三十四、但是还有一个坏消息

即使我们做到：

```text
Project-disjoint
Duplicate-disjoint
Lineage-disjoint
```

是不是就能保证：

> Test 一定干净？

还不能。

---

# 三百三十五、因为数据泄漏比“切错行”狡猾得多。

例如：

```text
Test里的专家答案
```

可能曾经出现在：

> 一个 Excel 说明文件里。

---

# 三百三十六、或者：

Test 项目的风险审查结论，

已经被整理进：

> 一篇培训材料。

---

# 三百三十七、或者：

同一案例被：

> LLM 改写成另一种语言，

然后进了 Train。

---

# 三百三十八、或者更隐蔽：

我们使用 Test Set 调 Prompt：

> 调了 200 次。

---

# 三百三十九、甚至：

未来 SFT 数据由当前模型错误生成，

而这些错误案例本来来自：

> Test。

---

# 三百四十、这时候即使：

```text
project_id
```

完全不重叠，

Benchmark：

> 仍然可能被污染。

---

# 三百四十一、本阶段掌握测试

如果现在不看前文，你能完整解释下面这些问题，第 6 阶段就真正掌握了：

> Train、Validation、Test 的真正角色分别是什么？

> 为什么 Train = Learn、Validation = Select、Test = Estimate？

> 为什么比例不是 Split 最重要的东西？

> 为什么 ProcurementAI 不应该默认按 Clause 行随机切？

> 为什么同一项目中的不同 Clause 会造成 Project Leakage？

> 为什么 `project_id` 从 Schema 第一阶段就非常重要？

> 为什么按 Document Split 仍然可能泄漏？

> 什么是 Group-aware Split？

> 什么叫 Split Unit？

> Duplicate Group 为什么绝对不能跨 Train/Test？

> Template Group 为什么也可能造成泄漏？

> 什么叫 Leakage Graph？

> 什么是 Connected Component / Split Group？

> 为什么真正 Split 的应该是“独立信息群”？

> 为什么 Group Integrity 通常优先于完美类别比例？

> 什么叫 Group-aware Stratification？

> 为什么 Test Set 不能只看行数？

> 为什么 Test Diversity 很重要？

> 为什么关键 Risk Slice 必须有足够样本？

> 什么是 Temporal Split？

> 为什么 Temporal Split 更接近真实部署？

> Project Holdout、Temporal Holdout、Geographic Holdout 分别在测什么？

> 为什么 Test Set 必须围绕“泛化问题”设计？

> 为什么成熟系统可能同时拥有 IID Test、Future Test、Hard Test？

> Validation 为什么也必须控制泄漏？

> 为什么 Group K-fold 比普通 K-fold 更适合小规模采购项目数据？

> 什么叫 Test Set Peeking？

> 为什么反复查看 Test 并调模型会污染 Test？

> Seen-template 与 Unseen-template 为什么应该分开评测？

> 为什么共享法规知识不一定构成泄漏？

> Shared Knowledge 和 Shared Answer Instance 有什么区别？

> Label Leakage 和 Split Leakage 有什么区别？

> 什么是 Template Leakage？

> 为什么 Synthetic Data 必须继承母样本 Split？

> 什么叫 Lineage-aware Split？

> 为什么数据增强不能从 Test 派生以后放进 Train？

> 什么是 Hard Split Constraint？

> 什么是 Soft Generalization Constraint？

> Project、Exact Duplicate 为什么更接近 Hard Constraint？

> Template、Agency、Region 为什么可以作为 Soft Constraint 或评测 Slice？

> 为什么同一个 Benchmark 必须固定 `split_version`？

> 为什么不同模型若使用不同 Test Split，分数不能直接比较？

> 为什么必须保存 Split Assignment Table？

> 新数据加入以后为什么不应该随便重洗旧 Test？

> 为什么一个“95%准确率”如果没有 Split 定义几乎没有解释力？

如果这些你都能自己讲清楚：

\[
\boxed{
第四课第6阶段真正掌握
}
\]

---

# 三百四十二、本阶段最终只记一句话

> **政府采购数据的 Train / Validation / Test 不能只按行随机切，而应该围绕“独立信息群”切分：同项目、重复样本和派生样本必须严格隔离，模板、时间、地区等维度则用来定义模型真正要面对的泛化难度；一个好的 Test Set 不是数据剩下的 10%，而是一套被严格保护、真正代表未来未知项目的考试。**

最后压成一张图：

```text
                  Procurement Data
                         │
                         ▼
                    Clause Rows
                         │
                         ▼
                ┌────────────────┐
                │ Leakage Links  │
                │                │
                │ Same Project   │
                │ Duplicate      │
                │ Derived From   │
                └───────┬────────┘
                        │
                        ▼
                  Split Groups
                        │
              ┌─────────┼─────────┐
              ▼         ▼         ▼
            Train      Val       Test
              │         │         │
           学参数     选方案     最后考
              │         │         │
              └─────────┼─────────┘
                        ▼
               Distribution Audit
                        │
                        ▼
                Cross-split Audit
                        │
                        ▼
                  Frozen Test
                        │
                        ▼
                DatasetSplit_V0.1
```

---

# 下一阶段：第四课 · 第 7 阶段
## 数据泄漏与 Benchmark 污染——为什么 Train 和 Test 明明已经按 Project 完全分开，模型仍然可能“提前看过答案”？

第 7 阶段我们会专门处理一个比随机切分更隐蔽的问题：

# Data Leakage

我们会把泄漏分成：

```text
Label Leakage
Project Leakage
Duplicate Leakage
Template Leakage
Temporal Leakage
Lineage Leakage
Answer Leakage
Benchmark Contamination
Human-in-the-loop Leakage
```

尤其会拆一个非常容易被忽视的问题：

> **当你根据 Test 的错误不断改 Prompt、改规则、补训练数据时，Test 是怎么一点一点被“训练进去”的？**

还会第一次建立：

```text
Leakage Audit Checklist
```

以及：

```text
Benchmark Firewall
```

最终产出第一版：

# `LeakageAudit_V0.1`

到那一步，第四课的数据才开始从“形式上分开”，进入真正意义上的：

> **可信评测数据。**

---

<!-- LESSON 04 STAGE 06 END -->


<!-- LESSON 04 STAGE 07 START -->

# 第四课 · 第 7 阶段：数据泄漏与 Benchmark 污染
## 为什么 Train 和 Test 明明已经按 Project 完全分开，模型仍然可能“提前看过答案”？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **泄漏的本质，是测试问题相关的信息通过某条不被允许的路径参与了模型开发。**
2. **Split不重叠 ≠ 没有泄漏**
3. **Leakage 的本质不是“文件重复”， 而是答案相关信息越过了不该越过的边界**
4. **泄漏既可能发生在数据里， 也可能发生在Prompt、RAG、规则和人脑里**
5. **时间方向非常重要： 未来信息不能帮助模型回答过去时点的测试问题**
6. **Test被反复用于改系统， 就会逐渐变成Validation**
7. **防泄漏不能只靠“大家小心一点”， 必须建立Benchmark Firewall**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |
| `Input` | 输入：模型在当前任务中允许看到的条件信息 |
| `Split` | 数据切分：按项目/时间/地区划分训练、验证、测试数据 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Sample` | 样本：具有明确输入、目标和来源的一条训练/评测记录 |
| `ANN` | ANN/近似最近邻：在大规模向量中快速寻找相似项 |
| `Dataset` | 数据集：按统一 Schema、版本和质量标准组织的样本集合 |
| `Threshold` | 阈值：把连续分数转成业务动作的决策门槛 |

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

第 6 阶段结束以后，我们已经做了一件非常专业的事情：

没有再用：

```text
Clause Row
```

作为唯一切分单位。

而是开始建立：

```text
Project
+
Duplicate Group
+
Lineage
+
必要的 Template Relation
```

最终得到：

# `DatasetSplit_V0.1`

也就是说，我们已经尽量确保：

```text
同一项目
不会一半Train、一半Test

完全重复样本
不会一边Train、一边Test

由同一母样本派生的数据
不会跨Split乱跑
```

看起来似乎已经安全了。

但现在我要给你一个有点残酷的结论：

> **Train/Test 完全没有相同 `project_id`，仍然不能证明 Benchmark 没有泄漏。**

例如 Test 中有这样一条采购条款：

> “供应商须在本市设有固定服务机构。”

项目本身：

> 从没进入 Train。

但是团队以前已经把这条 Test Case 的专家分析写进：

```text
内部培训材料
专家案例Excel
Prompt示例
规则库
RAG知识库
错误分析报告
Synthetic Data生成源
```

甚至开发人员已经看过它几十遍。

那么模型虽然没有：

> 直接训练那一行 Test 数据，

整个系统却可能已经：

> **提前知道答案。**

这就是今天要解决的东西：

# Data Leakage

以及更加隐蔽的：

# Benchmark Contamination

---

# 一、本阶段真正要解决的一个核心问题

今天只解决：

> **怎样判断一份 Test Set 是否真的处于“模型开发流程之外”，并建立一套机制，防止测试答案通过标签、时间、派生数据、RAG、Prompt、规则、人类调参等路径重新流回训练和开发系统？**

最终我们要得到：

# `LeakageAudit_V0.1`

整个过程可以先压成：

```text
DatasetSplit_V0.1
        ↓
Identify Leakage Paths
        ↓
Trace Data Lineage
        ↓
Check Train / Val / Test Boundaries
        ↓
Check RAG / Prompt / Rules / Synthetic Data
        ↓
Check Time Direction
        ↓
Check Human Feedback Loop
        ↓
Benchmark Firewall
        ↓
LeakageAudit_V0.1
```

---

# 二、本阶段先建立 6 个核心心智模型

先把这六句话钉住：

```text
① Split不重叠
   ≠
   没有泄漏

② Leakage 的本质不是“文件重复”，
   而是答案相关信息越过了不该越过的边界

③ 泄漏既可能发生在数据里，
   也可能发生在Prompt、RAG、规则和人脑里

④ 时间方向非常重要：
   未来信息不能帮助模型回答过去时点的测试问题

⑤ Test被反复用于改系统，
   就会逐渐变成Validation

⑥ 防泄漏不能只靠“大家小心一点”，
   必须建立Benchmark Firewall
```

如果今天只能记住一句：

> **泄漏的本质，是测试问题相关的信息通过某条不被允许的路径参与了模型开发。**

---

# 三、先回答：什么才叫“泄漏”？

很多人想到 Data Leakage，会立刻想到：

```text
Train里有Test原文
```

这当然是最明显的一种。

但定义应该更宽。

我们可以先这样理解：

\[
\boxed{
Leakage
=
不应该在开发阶段可用的信息
进入了模型开发路径
}
\]

这里关键有三个词：

```text
不应该
信息
开发路径
```

---

# 四、“信息”不一定是原始文本

它可以是：

```text
Test原文
Test标签
专家解释
最终裁决
更正结果
投诉处理结果
中标结果
Test案例摘要
Test案例改写
Test答案提炼出的规则
```

甚至可以只是：

> 一个开发人员看完 Test 错误后总结出来的经验。

---

# 五、“开发路径”也不只是 SFT

可能包括：

```text
CPT
SFT
Few-shot Prompt
System Prompt
Rule Engine
RAG Index
Synthetic Data
Threshold Tuning
Model Selection
Error Analysis
Human Workflow
```

所以如果只检查：

```text
train.jsonl
```

远远不够。

---

# 六、今天第一张总图

```text
                     TEST CASE
                         │
       ┌─────────────────┼──────────────────┐
       ▼                 ▼                  ▼
     原文               标签              专家解释
       │                 │                  │
       └────────────┬────┴────────────┬─────┘
                    │                 │
                    ▼                 ▼
                 数据集             文档/报告
                    │                 │
          ┌─────────┼────────┐        │
          ▼         ▼        ▼        ▼
         SFT       CPT    Synthetic   RAG
          │         │        │        │
          └─────────┼────────┼────────┘
                    ▼
                  MODEL
                    │
                    ▼
                  TEST
```

只要 Test Case 的答案相关信息：

> 绕了一圈又回到模型，

就可能污染 Benchmark。

---

# 七、第一类泄漏：Label Leakage

这是最直接的一类。

假设我们的任务是：

> 输入采购条款，判断有没有潜在风险。

理想输入：

```text
供应商须在本市注册满5年。
```

Label：

```text
potential_risk
```

---

# 八、结果数据工程师生成训练输入时变成：

```text
风险条款：
供应商须在本市注册满5年。
```

模型还需要判断吗？

几乎不需要。

---

# 九、因为：

```text
风险条款
```

已经告诉它：

> 答案。

这就是：

# Label Leakage

---

# 十、现实中 Label Leakage 往往没有这么傻

它可能藏得很深。

例如 Excel：

| 条款 | 专家意见 | 风险类别 |
|---|---|---|
| 供应商须…… | 建议删除地域限制 | 资格风险 |

后来构造模型 Input 时：

```text
条款：
供应商须……

专家意见：
建议删除地域限制
```

Output：

```text
是否有风险？
```

---

# 十一、这不是让模型判断风险。

这是让模型：

> 从专家意见里抄答案。

---

# 十二、再例如文件夹结构

数据来自：

```text
/risky_cases/
```

和：

```text
/normal_cases/
```

如果你把文件路径也作为 Feature：

模型可能根本不看正文。

---

# 十三、甚至文件名

```text
违规案例_001.pdf
```

如果 OCR Pipeline 把：

```text
违规案例
```

写进输入 Metadata，

答案又泄漏了。

---

# 十四、所以第一个检查问题

不是：

> “Label 列有没有放进 Input？”

而是：

> **Input 里有没有任何由 Label、裁决或专家结论派生出来的信息？**

---

# 十五、这叫 Target Proxy

目标代理变量。

它没有直接写：

```text
risk=true
```

但实际上高度暗示答案。

---

# 十六、例如：

```text
review_status = 已责令整改
```

模型看到这个字段，

再判断：

> “有没有风险？”

几乎已经知道答案。

---

# 十七、再比如：

```text
complaint_result = 投诉成立
```

如果你的任务是在投诉发生之前判断采购条款风险，

这个字段：

> 来自未来。

同时属于：

# Label Leakage

和：

# Temporal Leakage

---

# 十八、这就是泄漏的一个特点

一条信息：

> 可能同时属于多个泄漏类型。

---

# 十九、第二类：Project Leakage

第六阶段已经重点讲过。

例如：

```text
Project A
├── Clause 1 → Train
├── Clause 2 → Train
└── Clause 3 → Test
```

---

# 二十、Clause 3 虽然没有进入 Train，

但模型已经知道：

```text
项目背景
采购类型
模板
同章上下文
大量相关条件
```

这叫：

# Project Leakage

---

# 二十一、这类泄漏通常通过：

```text
project_id
```

做 Group Split 可以明显降低。

但注意：

> “不同 project_id”仍然不代表完全独立。

因为还可能有：

> Template Leakage。

---

# 二十二、第三类：Duplicate Leakage

例如：

Train：

> “投标人须在本市设立固定服务机构。”

Test：

> “投标人须在本市设立固定的服务机构。”

只多了一个：

```text
的
```

---

# 二十三、Exact Hash：

> 不一样。

但模型实际上：

> 几乎看过原题。

---

# 二十四、这就是：

# Near Duplicate Leakage

第五阶段已经建立：

```text
duplicate_group_id
```

和相似度审计。

今天真正要记：

> **泄漏不要求字符完全一样。**

---

# 二十五、甚至可以改写成：

Train：

> “供应商必须在本地设置售后机构。”

Test：

> “投标人应在项目所在地建立固定服务网点。”

字符串完全不同。

业务结构：

> 极其接近。

---

# 二十六、这时：

# Embedding / Semantic Similarity

就可以成为泄漏审计工具之一。

但仍然要结合：

```text
数字
否定词
单位
上下文
```

判断是不是：

> 真正等价。

---

# 二十七、第四类：Template Leakage

政府采购数据里非常重要。

假设某代理机构有模板：

```text
供应商须：
1. ……
2. ……
3. ……
```

Project A、B、C、D：

> 都使用它。

---

# 二十八、Train 有：

```text
A
B
C
```

Test 有：

```text
D
```

虽然项目完全不同，

模型可能已经：

> 把模板套路学得滚瓜烂熟。

---

# 二十九、这不一定代表 Benchmark 完全无效。

关键看：

> 你想测什么。

---

# 三十、如果生产环境本来就会继续出现同模板项目，

Seen-template Test：

> 是合理的。

---

# 三十一、但如果你声称：

> “模型对新采购文件结构具有强泛化能力。”

那最好还要有：

# Unseen-template Test

---

# 三十二、所以 Template Leakage 更准确地说：

> 有时不是“绝对非法泄漏”，而是“需要被明确控制和报告的泛化重叠”。

---

# 三十三、这就是为什么上一阶段我们把：

```text
Project / Exact Duplicate
```

更多视为：

# Hard Constraint

而：

```text
Template
Agency
Region
```

更多可以作为：

# Generalization Slice

---

# 三十四、第五类：Temporal Leakage

这是专业项目最容易忽视的一种。

先看一个简单例子。

我们要模拟：

> 2026 年 1 月 1 日时，模型审查一个采购项目。

---

# 三十五、理想情况：

模型只能使用：

> 2026 年 1 月 1 日之前已经存在的信息。

---

# 三十六、但是训练数据中加入了：

> 2026 年 3 月发布的更正公告。

这份更正公告说：

> 删除原资格条件。

---

# 三十七、现在模型回头判断 1 月的原始 Clause：

> “这条可能存在问题。”

它为什么这么聪明？

可能不是它真正推理出来的。

而是因为：

> 它已经知道后来被删掉了。

---

# 三十八、这就是典型的：

# Look-ahead Bias

向未来偷看。

---

# 三十九、可以写成：

\[
\boxed{
InformationTime
\le
PredictionTime
}
\]

这应该是很多时序任务的基本约束。

---

# 四十、如果：

```text
information_time
>
prediction_time
```

就要高度警惕：

> Temporal Leakage。

---

# 四十一、政府采购数据里“未来信息”非常多

例如：

```text
更正公告
投诉处理结果
质疑答复
监管处罚
中标结果
废标结果
合同履约结果
法院裁判
后续审计报告
```

---

# 四十二、这些东西当然非常有价值。

但如果任务是：

> 在采购文件发布时预测风险，

这些未来结果：

> 不能进入 Input。

---

# 四十三、但是它们可以干什么？

可以用于：

# Label Construction

---

# 四十四、比如：

原始项目发布时间：

```text
T0
```

半年后出现监管结论：

```text
T1
```

我们可以用 T1：

> 帮助专家构造 Gold Label。

---

# 四十五、但模型输入必须仍然是：

> T0 时点可见的信息。

这叫：

# Retrospective Label, Prospective Input

---

# 四十六、中文可以理解成：

> **允许未来帮助我们知道正确答案，但不能让模型在回答时提前看到未来。**

---

# 四十七、这和考试很像。

老师可以：

> 看标准答案批卷。

学生考试时：

> 不能拿标准答案。

---

# 四十八、所以 Dataset 里最好区分：

```text
event_time
information_available_time
annotation_time
```

---

# 四十九、例如：

```json
{
  "project_publish_time": "2025-06-01",
  "correction_time": "2025-06-08",
  "annotation_time": "2026-01-10"
}
```

---

# 五十、训练样本如果模拟：

```text
2025-06-01
```

模型输入：

> 不应该使用 6 月 8 日更正内容。

---

# 五十一、但是 Label 可以由：

> 2026 年专家回顾判定。

这完全合理。

---

# 五十二、所以 Temporal Dataset 最重要的不是：

> “数据是哪一年爬的”。

而是：

> **当时模型应该知道什么？**

---

# 五十三、第六类：Lineage Leakage

这是我们前几阶段反复保存 Data Lineage 的重要原因。

假设 Test 中有样本：

```text
T001
```

团队把它交给 LLM：

> “帮我生成 20 种改写。”

得到：

```text
S001
S002
...
S020
```

---

# 五十四、这些 Synthetic Samples：

> 文本全都和 T001 不完全一样。

Exact Dedup：

> 抓不到。

---

# 五十五、然后 S001～S020：

> 进入 Train。

最终测试 T001：

模型表现特别好。

---

# 五十六、这是：

# Lineage Leakage

因为训练数据：

> 是从 Test 派生出来的。

---

# 五十七、所以 Data Augmentation 的一个铁律：

\[
\boxed{
ChildSample
inherits
ParentSplit
}
\]

---

# 五十八、如果 Parent：

```text
Test
```

Child：

> 不能去 Train。

---

# 五十九、同理：

```text
翻译
改写
摘要
扩写
格式转换
问题生成
答案生成
Hard Negative生成
```

都属于：

> Derivation。

---

# 六十、所以每一个合成样本最好保存：

```text
source_sample_id
parent_sample_id
generation_method
generation_model
generation_prompt_version
```

---

# 六十一、例如：

```json
{
  "sample_id": "SYN-001",
  "source_sample_id": "TEST-991",
  "generation_method": "paraphrase",
  "split": "test"
}
```

而不是：

> 重新随机 Split。

---

# 六十二、这是 Data Lineage 真正开始发挥作用的地方。

---

# 六十三、第七类：Answer Leakage

这比 Label Leakage 更广。

假设 Test Case：

```text
Clause:
供应商须在本市设立固定服务机构。
```

Gold Rationale：

> 该条件可能构成与履约无直接必要联系的地域性限制，需要结合项目实际服务要求审查。

---

# 六十四、团队没有把 Test Clause 放进 Train。

但是把：

# Gold Rationale

放进了一个：

```text
专家知识库
```

---

# 六十五、模型测试时通过 RAG：

> 检索出了这条专家解释。

然后几乎原样回答。

---

# 六十六、项目隔离了吗？

隔离了。

Train/Test Row 重叠了吗？

没有。

但 Benchmark：

> 仍然污染。

---

# 六十七、这就是：

# Answer Leakage

---

# 六十八、它可以通过：

```text
RAG
Prompt Examples
Rule Engine
FAQ
Knowledge Base
Few-shot Cases
```

进入系统。

---

# 六十九、所以 Benchmark 不只是测试：

# Model Weights

而是测试：

# Full System

---

# 七十、如果最终产品是：

```text
LLM
+
RAG
+
Rules
```

那么评测隔离必须针对整个：

# System Boundary

---

# 七十一、可以画成：

```text
                 Benchmark Firewall
        ┌──────────────────────────────┐
        │                              │
        │  Model Weights               │
        │  Prompt                      │
        │  RAG                         │
        │  Rules                       │
        │  Tools                       │
        │  Synthetic Data              │
        │                              │
        └──────────────────────────────┘
                        │
                        ▼
                      TEST
```

不是只检查：

> Model Weight。

---

# 七十二、第八类：RAG Leakage

这一类尤其值得单独拿出来。

假设我们评测：

> 模型是否能识别某采购风险。

RAG 数据库里有：

```text
法律法规
财政部门规范
正式政策
```

这是：

> 合理知识。

---

# 七十三、但 RAG 里还有：

```text
该Test项目的专家审查报告
该项目投诉处理结果
该项目内部风险结论
```

那就：

> 不合理。

---

# 七十四、所以要区分：

# Allowed Knowledge

与：

# Test-specific Knowledge

---

# 七十五、Allowed Knowledge 可以包括：

```text
公开法律
公开法规
一般业务指南
截至评测时点有效的政策
```

---

# 七十六、Test-specific Knowledge 可能包括：

```text
测试项目专家答案
测试项目内部分析
测试项目最终投诉结果
专门针对该Test Case编写的解释
```

---

# 七十七、这是非常重要的 Benchmark Contract

在评测前要写清楚：

> **系统允许访问哪些外部知识？**

---

# 七十八、例如：

```text
允许：
截至项目发布日期已经生效的法规库

禁止：
该项目后续投诉结论
该项目人工Gold答案
```

---

# 七十九、如果不定义，

两个系统比较会非常不公平。

Model A：

> 只看法律。

Model B：

> 知识库里藏着答案。

然后 B 得分更高。

---

# 八十、你实际上不是比较：

> 模型能力。

而是在比较：

> 谁更接近看过标准答案。

---

# 八十一、第九类：Human-in-the-loop Leakage

这是最容易被忽略的一类。

假设 Final Test：

> 1000 条。

---

# 八十二、第一版模型错了：

> 300 条。

团队逐条看完这 300 条。

---

# 八十三、总结：

```text
本地服务机构类容易错
ISO证书类容易错
评分年限类容易错
```

然后修改：

```text
Prompt
Rule
Training Data
```

---

# 八十四、第二版再跑同一 Test。

错：

> 200 条。

---

# 八十五、团队再次看完。

再改。

---

# 八十六、跑 30 个版本以后：

Test 成绩：

> 越来越高。

---

# 八十七、但是 Test 还是：

> 真正独立的 Test 吗？

严格意义上：

> 已经不是了。

---

# 八十八、因为 Test 的信息已经通过：

# Human Brain

进入了系统设计。

---

# 八十九、这就是：

# Human-in-the-loop Leakage

或者：

# Test Peeking

---

# 九十、所以 Test 污染不需要：

> Copy/Paste。

人类记住错误模式：

> 就已经形成信息通道。

---

# 九十一、这可以写成：

```text
Test
 ↓
Developer sees errors
 ↓
Prompt / Rules / Data changes
 ↓
System
 ↓
Same Test
```

形成一个反馈环。

---

# 九十二、这叫：

# Benchmark Feedback Loop

---

# 九十三、而 Validation 的存在：

> 就是为了让你合法地做这种事情。

---

# 九十四、所以开发阶段应该：

```text
Train
+
Validation
```

不断迭代。

Final Test：

> 少碰。

---

# 九十五、成熟一点可以设计三层

```text
Development Set
Validation Set
Locked Test Set
```

---

# 九十六、甚至：

```text
Public Test
Private Hidden Test
```

开发人员：

> 只看到 Public。

Final Score：

> Private。

---

# 九十七、这就是很多竞赛为什么会有：

> 私榜。

因为大家如果一直调公开榜：

> 会对公开榜过拟合。

---

# 九十八、LLM 项目也是一样。

---

# 九十九、第十类：Benchmark Contamination

这是比普通 Data Leakage 更大的概念。

什么意思？

某个 Benchmark：

> 已经长期公开。

---

# 一百、基础模型训练语料中：

> 可能已经包含它。

你下载一个开源模型，

即使你自己从未：

> 用 Test 做 SFT，

它的 Pretraining 阶段：

> 可能已经见过这个 Benchmark。

---

# 一百零一、那么你的分数：

> 可能高估真正泛化能力。

---

# 一百零二、这就是：

# Pretraining Contamination

---

# 一百零三、对于我们的政府采购领域，

这给出一个很有价值的策略：

高价值 Gold Test 最好尽可能包含：

```text
内部专家新标案例
近期新增项目
从未公开发布的衍生Benchmark
高质量私有Hard Cases
```

---

# 一百零四、不是因为：

> 私有就天然更正确。

而是因为：

> 更容易控制模型有没有见过。

---

# 一百零五、特别是公开互联网题库，

现在越来越需要问：

> 基础模型预训练是否可能见过？

---

# 一百零六、但这里要避免走极端。

并不是所有公开资料：

> 都不能测试。

而是：

> **必须知道公开 Benchmark 的污染风险更高。**

---

# 一百零七、所以可以给 Benchmark Case 增加：

```text
contamination_risk
```

例如：

```text
low
medium
high
```

---

# 一百零八、什么可能是 High？

比如：

> 公开多年、广泛转载、Github大量镜像的测试题。

---

# 一百零九、什么可能 Low？

比如：

> 最近内部专家刚构造、未进入公开网络的案例。

---

# 一百一十、这不是绝对证明。

只是：

> 风险评级。

---

# 一百一十一、现在看一个非常隐蔽的泄漏：

# Post-outcome Feature Leakage

假设我们训练一个模型判断：

> 招标文件是否可能引起投诉。

Input 中加入：

```text
complaint_count
```

---

# 一百一十二、但是：

`complaint_count`：

> 只有项目结束以后才知道。

---

# 一百一十三、模型准确率可能非常高。

为什么？

因为它不是在预测：

> 会不会投诉。

它在读取：

> 已经投诉了几次。

---

# 一百一十四、这就是：

# Outcome Leakage

---

# 一百一十五、类似字段还有：

```text
是否被更正
最终废标原因
质疑次数
监管处理结果
最终合同是否签署
```

如果任务时点早于这些结果：

> 都不能放进 Input。

---

# 一百一十六、所以任何 Feature 都要问：

> **在预测时点，它真的可用吗？**

---

# 一百一十七、可以建立：

# Availability Test

对每个字段问：

```text
这个字段什么时候产生？
模型什么时候做预测？
```

---

# 一百一十八、如果：

\[
FeatureAvailableTime
>
PredictionTime
\]

那么：

> 高度可疑。

---

# 一百一十九、这个原则不限政府采购。

金融、医疗、风控：

> 都一样。

---

# 一百二十、现在看一个采购例子

我们要判断：

> 某资格条件发布时是否需要重点复核。

字段：

```text
项目预算
采购方式
采购品目
原始资格条款
```

在发布时：

> 都存在。

合理。

---

# 一百二十一、另一些字段：

```text
后续更正次数
质疑是否成立
投诉结果
最终中标供应商
```

在发布时：

> 还不存在。

不能作为预测 Input。

---

# 一百二十二、但是它们可以帮助：

> 建 Label。

再次强调：

```text
Label Construction Data
≠
Model Input Data
```

---

# 一百二十三、这一条非常重要。

---

# 一百二十四、现在看 Annotation Leakage

假设专家在标注时看到：

```text
后续监管认定结果
```

然后确定：

```text
risk_present = true
```

这是允许的吗？

---

# 一百二十五、可以。

如果我们的目的：

> 是建立尽量准确的回顾性 Gold Label。

---

# 一百二十六、但模型 Input：

> 不能看到后续监管结果。

---

# 一百二十七、所以标注系统要区分两个界面：

```text
Annotator View
```

和：

```text
Model View
```

---

# 一百二十八、Annotator View 可以有：

```text
原文件
上下文
法规
后续证据
裁决
```

---

# 一百二十九、Model View 只允许：

> 预测时点可得的信息。

---

# 一百三十、这就是：

# Annotation Privilege

标注者可以有更多证据。

模型：

> 不可以。

---

# 一百三十一、如果没有这个区别，

很多团队会无意中：

> 把标注辅助信息一起导出成模型 Feature。

---

# 一百三十二、现在看 Metadata Leakage

例如：

```text
annotator_comment = “典型地域限制案例”
```

你以为训练只用了：

```text
clause_text
```

但数据加载代码：

> 把整个 JSON 序列化给模型。

于是 Prompt 里出现：

```text
annotator_comment
```

---

# 一百三十三、这类 Bug 特别隐蔽。

所以 SFT Input Builder 应该：

> **白名单字段。**

而不是：

> “除了 label 之外全部输入”。

---

# 一百三十四、也就是：

```text
allowed_input_fields = [
    clause_text,
    section_path,
    allowed_context
]
```

---

# 一百三十五、而不是：

```text
drop(label)
然后剩下全部喂进去
```

---

# 一百三十六、这叫：

# Allowlist > Blocklist

对于高风险数据系统，

白名单通常：

> 更安全。

---

# 一百三十七、为什么？

新加一个字段：

```text
expert_final_decision
```

如果采用 Blocklist，

开发者忘了加进删除列表：

> 它就泄漏。

---

# 一百三十八、如果用 Allowlist：

> 新字段默认不会进入模型。

---

# 一百三十九、非常实用。

---

# 一百四十、现在看 Prompt Leakage

假设 Test 中有一类特别难：

> 本地服务机构。

团队根据 Test 错误改 System Prompt：

```text
特别注意：
涉及要求供应商在项目所在地预先设立机构时，
重点判断是否与履约存在必要关系。
```

---

# 一百四十一、这条规则本身：

> 没有复制 Test 原文。

但它是根据 Test 错误：

> 专门总结出来的。

---

# 一百四十二、如果以后还拿同一 Test 报最终成绩，

分数：

> 已经受到 Test 信息影响。

---

# 一百四十三、这就是：

# Prompt Overfitting to Test

---

# 一百四十四、同理：

Rule Engine：

```text
if "本市设立固定机构":
    increase_risk_score()
```

如果这个 Rule：

> 是看了 Final Test 后写的，

也是 Test 污染。

---

# 一百四十五、所以完整 Benchmark Audit 必须记录：

```text
prompt_version
rule_version
rag_version
model_version
```

---

# 一百四十六、不然：

> 你甚至不知道某次 Test 到底测了什么系统。

---

# 一百四十七、现在看 Threshold Leakage

假设模型输出风险概率：

```text
0～1
```

我们需要选择：

```text
threshold
```

---

# 一百四十八、如果在 Test 上试：

```text
0.3
0.4
0.5
0.6
```

然后选择 Test F1 最好的：

```text
0.42
```

---

# 一百四十九、你已经：

> 用 Test 调参。

---

# 一百五十、正确做法：

Threshold：

> 在 Validation 上选。

Test：

> 只使用已经冻结的 Threshold。

---

# 一百五十一、所以 Test 污染不只是：

> 文本。

一个数字参数：

> 也可以因为 Test 而过拟合。

---

# 一百五十二、类似还有：

```text
Temperature
Top-p
Retrieval k
Rerank threshold
Abstention threshold
Rule weight
```

---

# 一百五十三、所有这些：

> 都应该主要用 Validation 调。

---

# 一百五十四、现在建立一个重要分类：

# Direct Leakage

与：

# Indirect Leakage

---

# 一百五十五、Direct：

```text
Test原文进入Train
Test标签进入Input
Test答案进入RAG
```

比较容易理解。

---

# 一百五十六、Indirect：

```text
看Test错误后改Prompt
根据Test调Threshold
从Test生成Synthetic Data
根据Test写Rule
```

---

# 一百五十七、Indirect 往往：

> 更难审计。

---

# 一百五十八、因此真正专业的 Benchmark Governance：

> 需要记录开发历史。

---

# 一百五十九、例如每次实验：

```text
experiment_id
model_version
prompt_version
rule_version
rag_snapshot
dataset_version
split_version
```

---

# 一百六十、以及：

```text
which benchmark was inspected
```

---

# 一百六十一、这会让我们以后知道：

> 某个 Final Test 是否已经被开发人员多次使用。

---

# 一百六十二、现在出现一个重要概念：

# Benchmark Firewall

Benchmark 防火墙。

---

# 一百六十三、什么是 Firewall？

不是某一个算法。

而是一套：

> **让 Final Test 与日常开发流程隔离的制度 + 数据 + 工程机制。**

---

# 一百六十四、第一层 Firewall：

# Access Control

不是所有人：

> 都能看到 Final Test Label。

---

# 一百六十五、例如：

```text
Developers
→ 可以看Train / Validation

Benchmark owner
→ 管理Hidden Test
```

---

# 一百六十六、开发者提交：

```text
model endpoint
```

系统自动：

> 跑 Hidden Test。

只返回：

```text
summary metrics
```

---

# 一百六十七、这样减少：

> 针对单个 Test Case 调参。

---

# 一百六十八、第二层 Firewall：

# Dataset Isolation

Final Test 文件：

> 放在独立目录 / 权限空间。

---

# 一百六十九、不要：

```text
dataset/
  train.jsonl
  val.jsonl
  test.jsonl
```

然后大家都随便打开。

对早期课程练习当然可以。

但成熟项目：

> 可以更严格。

---

# 一百七十、第三层 Firewall：

# Input Allowlist

测试运行时：

只给系统允许的字段。

例如：

```text
clause_text
section_path
allowed_context
```

---

# 一百七十一、不传：

```text
gold_label
expert_rationale
future_outcome
annotation_note
```

---

# 一百七十二、第四层 Firewall：

# RAG Snapshot

评测时记录：

```text
knowledge_snapshot_version
```

---

# 一百七十三、例如：

```text
rag_knowledge_2026_09_01
```

---

# 一百七十四、这样以后知道：

> 模型当时查的是哪一版知识库。

---

# 一百七十五、第五层 Firewall：

# Time Cutoff

对于 Temporal Benchmark：

明确：

```text
knowledge_cutoff
```

---

# 一百七十六、例如：

```text
Test项目发布日期：
2026-06-01

允许知识：
≤ 2026-06-01
```

---

# 一百七十七、这样未来法规：

> 不会倒灌回去。

---

# 一百七十八、第六层 Firewall：

# Lineage Guard

任何：

```text
Synthetic
Paraphrase
Translation
Derived Sample
```

如果祖先属于 Test：

> 自动禁止进入 Train。

---

# 一百七十九、第七层 Firewall：

# Evaluation Log

每次运行 Final Test：

记录：

```text
who
when
which model
which prompt
which rules
which RAG snapshot
```

---

# 一百八十、这样可以知道：

> Test 被使用了多少次。

---

# 一百八十一、这七层组合起来：

才真正接近：

# Benchmark Firewall

---

# 一百八十二、现在给它画一张图

```text
                   Final Test
                       │
             ┌─────────┴─────────┐
             │ Benchmark Firewall │
             └─────────┬─────────┘
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
 Access Control   Input Allowlist    Time Cutoff
       │               │                │
       ├───────────────┼────────────────┤
       ▼               ▼                ▼
 Lineage Guard    RAG Snapshot      Eval Logging
       │               │                │
       └───────────────┼────────────────┘
                       ▼
                  Model/System
                       │
                       ▼
                    Metrics
```

---

# 一百八十三、现在建立 Leakage Audit Checklist

这是第七阶段最实用的产物之一。

第一组：

# Split Integrity

检查：

```text
同project_id是否跨Split？
同duplicate_group_id是否跨Split？
同source_case_id是否跨Split？
派生样本是否跨Split？
```

---

# 一百八十四、第二组：

# Text Similarity

检查：

```text
Test vs Train
Exact match?

Near duplicate?

Template overlap?

High embedding similarity?
```

---

# 一百八十五、第三组：

# Label Leakage

检查：

```text
Input中是否存在Gold Label？

是否存在专家结论？

是否存在修改建议？

是否存在裁决结果？

是否存在风险类别名称？
```

---

# 一百八十六、第四组：

# Temporal Leakage

检查：

```text
Input字段是否在预测时点可用？

法规版本是否符合时间点？

是否使用了后续更正？

是否使用了后续投诉结论？

是否使用了未来统计信息？
```

---

# 一百八十七、第五组：

# RAG Leakage

检查：

```text
RAG中是否存在Test Case本身？

是否存在Test Gold Rationale？

是否存在该项目后续审查报告？

知识库Snapshot是否被冻结？
```

---

# 一百八十八、第六组：

# Prompt / Rule Leakage

检查：

```text
Prompt是否根据Final Test错误专门改过？

Rules是否根据Final Test写过？

Threshold是否在Test上调过？
```

---

# 一百八十九、第七组：

# Human Leakage

检查：

```text
开发人员是否看过Test Label？

是否逐条看过Final Test Error？

Final Test被跑过多少轮？

是否已经实际上变成Validation？
```

---

# 一百九十、第八组：

# Contamination Risk

检查：

```text
Benchmark是否公开多年？

基础模型是否可能见过？

Test是否来自大量互联网转载材料？

是否有低污染的私有/近期补充集？
```

---

# 一百九十一、把这 8 组跑完，

我们才真正可以说：

> “做过泄漏审计。”

---

# 一百九十二、现在谈 Leakage Severity

不是每个问题都一样严重。

可以概念分：

```text
Critical
High
Medium
Low
```

---

# 一百九十三、Critical

例如：

```text
Test答案进入SFT Train
Test Gold Rationale进入RAG
同一Exact Duplicate跨Train/Test
```

这基本：

> 直接破坏 Benchmark。

---

# 一百九十四、High

例如：

```text
Test改写样本进入Train
测试项目后续裁决进入Input
长期反复用Final Test调Prompt
```

---

# 一百九十五、Medium

例如：

```text
大量Template overlap
同代理机构风格高度重合
```

是否致命：

> 取决于评测目标。

---

# 一百九十六、Low

可能是：

```text
公共法规知识在Train和Test都出现
```

如果它本来就是：

> Allowed Knowledge。

这通常：

> 不叫问题。

---

# 一百九十七、所以不要把 Leakage Audit 变成：

> “只要任何信息重复就全部判死刑。”

---

# 一百九十八、我们还是要问：

# Does this invalidate the generalization claim?

它是否让你的：

> 泛化结论失真？

---

# 一百九十九、这是最核心的判断。

---

# 二百、例如同一部《政府采购法》

Train 和 Test：

> 都涉及。

并不会使：

> “新项目泛化”

这个结论失效。

---

# 二百零一、但同一个项目的专家答案：

Train/Test 都出现。

就会直接：

> 让泛化结论失真。

---

# 二百零二、所以：

\[
\boxed{
Leakage
不是简单的“信息重复”
而是“不恰当的信息可用性”
}
\]

---

# 二百零三、现在设计一个 Leakage Record

发现一个问题时，

不要只写：

```text
有泄漏
```

---

# 二百零四、最好记录：

```json
{
  "audit_id": "LEAK-00017",
  "test_sample_id": "TEST-0091",
  "related_train_sample_id": "TRAIN-2217",

  "leakage_type": "lineage_leakage",
  "severity": "critical",

  "evidence": "train sample derived from test sample paraphrase",

  "action": "remove_train_sample",

  "status": "resolved",

  "audit_version": "leakage_audit_v0.1"
}
```

---

# 二百零五、为什么需要 `evidence`？

因为：

> “疑似泄漏”

和：

> “确认泄漏”

不是一回事。

---

# 二百零六、可以有：

```text
suspected
confirmed
resolved
accepted_risk
```

---

# 二百零七、例如 Template Overlap：

可能：

```text
accepted_risk
```

因为我们主 Benchmark 本来就允许：

> Seen Template。

---

# 二百零八、但是报告里：

> 必须说清楚。

---

# 二百零九、这叫：

# Evaluation Transparency

不是所有问题都必须消灭。

但：

> 必须让分数的含义清楚。

---

# 二百一十、现在看一个很真实的案例

假设我们有：

```text
Test Sample T1
```

条款：

> “供应商注册地须在本市。”

Gold：

```text
potential_risk
```

---

# 二百一十一、Train 里没有 T1。

项目也不同。

看起来很干净。

---

# 二百一十二、但我们发现 Train 中有：

```text
Synthetic S77:
投标企业须为本地注册企业。
```

它来自专家培训案例 E12。

---

# 二百一十三、继续查 Lineage：

```text
E12
```

原来就是：

> T1 的内部专家分析版本。

---

# 二百一十四、于是链条是：

```text
T1 Test Case
   ↓
Expert Case E12
   ↓
Synthetic Rewrite S77
   ↓
Train
```

---

# 二百一十五、文本 Dedup：

> 很可能发现不了。

Project ID：

> 完全不同。

---

# 二百一十六、只有：

# Lineage

才能发现。

---

# 二百一十七、这就是为什么前六个阶段一直强调：

> 来源和血缘不能丢。

---

# 二百一十八、再看另一个案例

Test：

> 某评分办法。

RAG 里没有 Gold Answer。

但 Rule Engine 有：

```text
如果“本地服务机构”得分 > 0
则标记地域风险
```

---

# 二百一十九、这条 Rule：

> 是开发人员看 Test 错误后加的。

---

# 二百二十、那么最终系统测试成功，

到底是谁成功？

```text
LLM？
Rule？
Test-specific patch？
```

---

# 二百二十一、这就是为什么一个成熟的 Benchmark：

> 评的是系统版本。

需要记录：

```text
model_version
prompt_version
rule_version
rag_version
```

---

# 二百二十二、否则你没法解释：

> 分数为什么提高。

---

# 二百二十三、现在看 Validation 的正确角色

假设你发现：

> “本地服务机构”这种案例总出错。

应该在哪里发现？

最好：

# Validation

---

# 二百二十四、然后：

```text
改Prompt
改SFT
改Rule
```

继续看 Validation。

---

# 二百二十五、等方案冻结以后：

> 才去 Final Test。

---

# 二百二十六、如果 Final Test 又暴露新问题怎么办？

可以记录。

但如果你：

> 根据这些问题继续开发，

那下一轮最好：

# 新建 Test Version

或者：

> 把当前 Test 降级为 Development Benchmark。

---

# 二百二十七、这是一种很成熟的 Benchmark 生命周期管理。

---

# 二百二十八、比如：

```text
GoldTest_v1
```

使用一段时间后：

> 团队已经熟悉大量案例。

---

# 二百二十九、此时它仍然很适合：

# Regression Test

---

# 二百三十、也就是说：

> 检查新模型有没有退化。

---

# 二百三十一、但不再适合声称：

> “完全未见过的最终泛化成绩”。

---

# 二百三十二、然后创建：

```text
GoldTest_v2_private
```

作为新 Final Test。

---

# 二百三十三、所以 Benchmark 也有生命周期：

```text
Hidden Final Test
       ↓
被使用/被分析
       ↓
Development Regression Set
       ↓
新Hidden Test替代
```

---

# 二百三十四、这叫：

# Benchmark Rotation

---

# 二百三十五、尤其长期 AI 产品：

> 很有必要。

---

# 二百三十六、否则一个 Test 用三年，

团队每个人都能背答案。

最后 99%：

> 不代表任何新能力。

---

# 二百三十七、现在看 Benchmark Contamination 与 Memorization

假设模型真的见过测试题。

是不是一定：

> 会背出来？

不一定。

---

# 二百三十八、但我们已经不能确定高分来自：

```text
真正推理
```

还是：

```text
记忆
```

---

# 二百三十九、这就是污染最大的问题：

> **它破坏的是分数的可解释性。**

---

# 二百四十、所以 Benchmark 的价值不是：

> 有 1000 道题。

而是：

> 这些题能支持一个可信结论。

---

# 二百四十一、例如：

> “模型对未来未见采购项目的高风险条款召回率为 91%。”

要说这句话，

你必须能证明：

```text
未来
未见
项目
高风险
```

这些限定：

> 基本成立。

---

# 二百四十二、如果 Test 已经污染，

“91%”只是一个数字。

---

# 二百四十三、这就是第七阶段最深的一层：

# Benchmark = Claim

一个 Benchmark 本质上是在支持：

> 一个能力声明。

---

# 二百四十四、所以每个 Benchmark 都应该有：

# Evaluation Claim

例如：

> **评估 ProcurementAI 在没有访问该项目后续裁决和专家答案的情况下，对未参与训练的新采购项目条款进行潜在合规风险筛查的能力。**

---

# 二百四十五、有了这句话，

我们就能判断：

某个信息是否泄漏。

---

# 二百四十六、例如 RAG 使用有效法规：

> 与这个 Claim 不冲突。

---

# 二百四十七、RAG 使用该项目最终投诉结论：

> 与这个 Claim 冲突。

---

# 二百四十八、所以 Leakage 不是凭感觉判断。

它应该相对于：

# Evaluation Claim

判断。

---

# 二百四十九、这是一套特别强的思维框架：

```text
先写能力声明
      ↓
定义允许信息
      ↓
定义禁止信息
      ↓
再做Leakage Audit
```

---

# 二百五十、现在第一次设计

# Benchmark Contract

可以概念包括：

```text
task
prediction_time
allowed_inputs
allowed_external_knowledge
forbidden_information
split_policy
test_access_policy
```

---

# 二百五十一、例如：

```json
{
  "task": "procurement_compliance_risk_review",

  "prediction_time": "document_publication_time",

  "allowed_inputs": [
    "target_clause",
    "same-document prior context",
    "project_metadata_available_at_publication"
  ],

  "allowed_external_knowledge": [
    "regulations effective at prediction_time"
  ],

  "forbidden_information": [
    "future_correction_notice",
    "complaint_result",
    "gold_rationale",
    "expert_final_decision"
  ]
}
```

---

# 二百五十二、注意：

这不是最终法律制度。

只是：

> 我们的评测工程合同。

---

# 二百五十三、这个 Contract 非常有用。

因为不同人不会：

> 各自猜什么算泄漏。

---

# 二百五十四、现在看 RAG 的时间问题

例如法规：

2025 年版本：

```text
Rule V1
```

2026 年修订：

```text
Rule V2
```

---

# 二百五十五、Test Case 发生于：

```text
2025
```

如果 RAG 永远只返回：

> 2026 V2，

可能发生：

# Future Law Leakage

---

# 二百五十六、所以法规 RAG 最终必须支持：

```text
effective_from
effective_to
```

---

# 二百五十七、第六课我们会详细处理：

> 法规时间、层级、地域。

今天只需要知道：

> Benchmark Leakage 和 RAG Versioning 是连在一起的。

---

# 二百五十八、现在看另一个时间陷阱

某个项目：

> 2025 年发布。

专家：

> 2026 年标注。

---

# 二百五十九、专家可以用 2026 年新法规吗？

如果我们的 Label 定义是：

> “按 2025 年当时有效规则判断”。

那么：

> 不能直接按 2026 新规则重新定罪。

---

# 二百六十、所以 Annotation 本身也有：

# Temporal Semantics

---

# 二百六十一、标注说明应该写清：

> **按照哪个时点的规范环境判断。**

---

# 二百六十二、否则 Test Gold 本身：

> 可能时间穿越。

---

# 二百六十三、这不是模型泄漏。

这是：

# Gold Construction Error

---

# 二百六十四、但最终效果一样：

> Benchmark 不可信。

---

# 二百六十五、所以第七阶段其实在告诉我们：

# Leakage Audit 不能只查 Train/Test

还要查：

> Gold 本身是怎么来的。

---

# 二百六十六、现在我们给整个数据链加时间

```text
Raw Document
    │ event_time
    ▼
ParsedDocument
    ▼
ClauseUnit
    ▼
Annotation
    │ annotation_time
    ▼
Gold Sample
    ▼
Split
    ▼
Training / Test
```

---

# 二百六十七、再加：

```text
knowledge_snapshot_time
```

和：

```text
model_training_cutoff
```

整个系统就开始真正具有：

# Temporal Provenance

---

# 二百六十八、以后如果问：

> “为什么 2025 年这个 Case 这么判断？”

可以回答：

```text
依据的是当时有效规则
Gold由2026专家回顾标注
模型输入不含2025之后项目结果
```

这才是：

> 专业可解释。

---

# 二百六十九、现在谈泄漏自动检测

哪些能自动？

第一类：

# ID overlap

```text
project_id
document_id
duplicate_group_id
source_case_id
```

很好自动查。

---

# 二百七十、第二类：

# Exact Hash

```text
normalized_text_hash
```

很好查。

---

# 二百七十一、第三类：

# Near Similarity

可以用：

```text
MinHash
Embedding
```

找候选。

---

# 二百七十二、第四类：

# Lineage

沿着：

```text
parent_sample_id
source_sample_id
```

图搜索。

---

# 二百七十三、第五类：

# Temporal Check

比较：

```text
feature_available_time
prediction_time
```

---

# 二百七十四、第六类：

# Input Schema Audit

检查 Input 中：

> 是否包含禁用字段。

---

# 二百七十五、哪些很难全自动？

例如：

> 某条 Prompt 规则是不是因为看 Final Test 才写的？

这需要：

# Process Governance

---

# 二百七十六、所以：

\[
\boxed{
LeakageControl
=
Automation
+
Governance
}
\]

只靠代码：

> 不够。

只靠制度：

> 也不够。

---

# 二百七十七、现在给 `LeakageAudit_V0.1` 设计一个总报告

概念上可以包含：

```text
Audit Scope
Split Version
Dataset Version
Benchmark Version
Model Development Cutoff
```

---

# 二百七十八、然后统计：

```text
Project overlap count
Exact duplicate overlap count
Near duplicate suspects
Lineage violations
Temporal violations
Forbidden-field violations
RAG contamination findings
Human test exposure
```

---

# 二百七十九、例如：

```json
{
  "audit_version": "leakage_audit_v0.1",

  "dataset_version": "procurement_dataset_v0.1",
  "split_version": "procurement_split_v0.1",

  "project_overlap": 0,
  "exact_duplicate_overlap": 0,

  "near_duplicate_suspects": 27,
  "confirmed_near_duplicate_leaks": 3,

  "lineage_violations": 0,
  "temporal_violations": 2,

  "forbidden_input_field_violations": 0,

  "audit_status": "needs_remediation"
}
```

---

# 二百八十、这时不能说：

> Benchmark 已通过。

要先解决：

```text
3个Near Duplicate Leak
2个Temporal Leak
```

---

# 二百八十一、修完再跑：

```text
LeakageAudit_v0.2
```

---

# 二百八十二、这就是工程化质量门槛：

# Quality Gate

---

# 二百八十三、比如规定：

```text
Critical Leakage = 0
```

才能发布 Benchmark。

---

# 二百八十四、High Severity：

> 必须人工审议。

---

# 二百八十五、Medium：

> 可以记录为已知限制。

---

# 二百八十六、这比：

> “我们觉得没泄漏”

靠谱得多。

---

# 二百八十七、现在看一个常见误区：

> “我们从来没把 Test 放进 Train，所以肯定没泄漏。”

错。

---

# 二百八十八、Test 可能通过：

```text
Synthetic
RAG
Rule
Prompt
Threshold
Human
```

六条路回来。

---

# 二百八十九、另一个误区：

> “我们已经做了去重，所以不会泄漏。”

错。

去重：

> 只能解决部分内容重合。

解决不了：

```text
未来信息
答案知识库
Test调Prompt
```

---

# 二百九十、另一个误区：

> “基础模型冻结，没有训练，所以 RAG 泄漏没关系。”

错。

Benchmark 测的是最终系统输出。

RAG 如果：

> 藏着标准答案，

系统一样作弊。

---

# 二百九十一、另一个误区：

> “人看Test不算机器看Test。”

如果人的观察：

> 改变了系统，

就产生了信息通道。

---

# 二百九十二、另一个误区：

> “只要测试样本够新，就一定没污染。”

也不一定。

如果 Test 是从旧案例：

> 改写而来，

而旧案例已在 Train，

仍可能高度相关。

---

# 二百九十三、所以真正核心始终是：

# Information Lineage

信息从哪里来。

---

# 二百九十四、现在做几个思维实验

### 思维实验 A

Train/Test 没有任何相同 `project_id`。

是不是就可以宣布：

> 无泄漏？

不能。

还要检查：

> Duplicate、Template、Lineage、Time、RAG、Human Feedback。

---

# 二百九十五、### 思维实验 B

Test 的原文从未进 Train，

但 Gold Rationale 在 RAG 中。

是否泄漏？

> 是，属于严重 Answer/RAG Leakage。

---

# 二百九十六、### 思维实验 C

Test Case 的改写版本进入 Train。

文字不一样。

是否泄漏？

> 是，属于 Lineage Leakage。

---

# 二百九十七、### 思维实验 D

测试 2025 年项目时，

系统查到了 2026 年才生效的法规。

是否有问题？

> 如果评测目标是模拟 2025 年当时决策，这是 Temporal Leakage。

---

# 二百九十八、### 思维实验 E

专家在 2026 年利用后续证据给 2025 项目标 Gold。

允许吗？

> 可以，只要后续证据不进入模型 Input，并且 Gold 定义明确。

---

# 二百九十九、### 思维实验 F

同一法律法规同时存在于 Train 和 Test 相关 Context。

一定泄漏吗？

> 不一定。公共允许知识不等于测试答案。

---

# 三百、### 思维实验 G

Final Test 跑过 50 次，每次团队根据错误改系统。

它还是完全独立 Final Test 吗？

> 基本不能再这样理解。

它已经逐渐变成 Development Benchmark。

---

# 三百零一、### 思维实验 H

模型 Base Pretraining 可能看过公开 Benchmark。

我们自己没有训练过它。

有没有污染风险？

> 有，属于 Pretraining / Benchmark Contamination 风险。

---

# 三百零二、### 思维实验 I

Input 里没有 Label，

但有字段：

```text
整改状态 = 已整改
```

任务是判断：

> 是否存在问题。

是否可能泄漏？

> 很可能，因为这个字段是结果代理。

---

# 三百零三、### 思维实验 J

Threshold 是在 Test 上挑出来的最佳值。

训练数据完全干净。

Test 分数还能作为纯 Final Estimate 吗？

> 不能，因为 Test 已参与模型选择。

---

# 三百零四、现在总结本阶段最容易犯的 12 个错误

**错误 1：**

> Project 不重叠 = 没有泄漏。

错。

---

**错误 2：**

> 只有原文重复才算泄漏。

错。

答案、派生数据、未来信息都可以泄漏。

---

**错误 3：**

> Label 没进 Input，所以不会 Label Leakage。

错。

可能有 Target Proxy。

---

**错误 4：**

> RAG 不改权重，所以 RAG 里的 Test Answer 不算泄漏。

错。

---

**错误 5：**

> Synthetic Data 字不一样，所以安全。

错。

Lineage 才重要。

---

**错误 6：**

> 未来结果可以作为模型 Feature，因为能提高准确率。

这正是严重 Temporal / Outcome Leakage。

---

**错误 7：**

> 专家能看到的信息，模型也都能看到。

错。

Annotator View 和 Model View 应分开。

---

**错误 8：**

> Final Test 可以无限次调 Prompt。

会产生 Test Peeking。

---

**错误 9：**

> Threshold 调节不算使用 Test。

算。

---

**错误 10：**

> 公开 Benchmark 一定能代表真实泛化。

不一定，可能存在预训练污染。

---

**错误 11：**

> 只要技术上做了隔离，流程治理不重要。

错。

人类反馈也能造成泄漏。

---

**错误 12：**

> Leakage Audit 是一次性的。

错。

Dataset、RAG、Prompt、Rules 每次重要更新后都应该重新检查。

---

# 三百零五、本阶段最重要的 7 个“≠”

```text
Different Project
≠
No Leakage
```

```text
No Exact Duplicate
≠
No Contamination
```

```text
Label Column Removed
≠
No Label Leakage
```

```text
Frozen Model Weights
≠
Clean Evaluation
```

```text
Public Knowledge
≠
Test-specific Answer
```

```text
Future Evidence for Annotation
≠
Future Evidence for Model Input
```

```text
Test Not Used for Gradient
≠
Test Not Used for Development
```

最后一条尤其重要。

---

# 三百零六、再记住本阶段最重要的“=”

\[
\boxed{
CleanBenchmark
=
SplitIsolation
+
TemporalIntegrity
+
LineageIntegrity
+
SystemIsolation
+
HumanProcessControl
}
\]

翻译成人话：

> **真正干净的 Benchmark，不只是 Train 和 Test 的行不重复，而是测试项目、答案、派生数据、时间信息、RAG、Prompt、规则和人工开发反馈都处在被明确控制的边界之内。**

---

# 三百零七、现在把第四课前 7 个阶段连起来

```text
Stage 1
Task Schema
“什么是一条样本？”
       │
       ▼
Stage 2
ParsedDocument
“文件里到底有什么？”
       │
       ▼
Stage 3
ClauseUnit
“文字属于哪个业务要求？”
       │
       ▼
Stage 4
CleanClause
“怎样安全规范文本？”
       │
       ▼
Stage 5
DedupedClauseSet
“这些样本到底有多少独立信息？”
       │
       ▼
Stage 6
DatasetSplit
“哪些数据用来学，哪些留下考试？”
       │
       ▼
Stage 7
LeakageAudit
“考试题真的没有被提前泄露吗？”
```

到这里，我们的数据才第一次开始拥有：

> **可信评测边界。**

---

# 三百零八、但还有一个巨大问题没有解决

现在我们有：

```text
Clause
Clean Text
Dedup Group
Split
Leakage Audit
```

但是：

> **到底让专家标什么？**

---

# 三百零九、如果专家 A 标：

```text
违规
```

专家 B 标：

```text
有风险
```

专家 C 标：

```text
建议修改
```

专家 D 标：

```text
需要进一步核查
```

这些到底是不是：

> 同一个 Label？

---

# 三百一十、再比如风险类型

有人写：

```text
地域限制
```

有人写：

```text
资格条件不合理
```

有人写：

```text
差别待遇
```

有人写：

```text
供应商资格风险
```

---

# 三百一十一、如果没有统一 Schema，

最后得到的不是：

> Gold Dataset。

而是：

> 一堆专家各自语言风格的 Excel。

---

# 三百一十二、所以泄漏控制以后，

第四课的下一步终于进入：

# Label Schema

---

# 三百一十三、本阶段掌握测试

如果现在不看前文，你能够完整解释下面这些问题，第 7 阶段就算真正掌握：

> 为什么 Project-disjoint 不等于没有数据泄漏？

> Data Leakage 的本质是什么？

> 为什么答案相关信息不一定以 Label 字段出现？

> 什么是 Target Proxy？

> 什么是 Label Leakage？

> 为什么“专家意见”也可能泄漏答案？

> 什么是 Duplicate Leakage？

> 什么是 Template Leakage？

> Template overlap 为什么有时不是绝对非法，而是泛化难度问题？

> 什么是 Temporal Leakage？

> 为什么未来更正公告不能帮助模型模拟过去时点判断？

> Prediction Time 和 Information Available Time 有什么关系？

> 为什么未来结果可以辅助 Gold Label，却不能进入 Model Input？

> 什么是 Retrospective Label / Prospective Input？

> 什么是 Lineage Leakage？

> 为什么 Synthetic Data 必须继承母样本 Split？

> 翻译、改写、摘要为什么都属于派生关系？

> 什么是 Answer Leakage？

> 为什么 Gold Rationale 进入 RAG 会污染 Benchmark？

> Allowed Knowledge 和 Test-specific Knowledge 有什么区别？

> 为什么 Benchmark 必须定义 RAG 允许访问的知识范围？

> 什么是 Human-in-the-loop Leakage？

> 为什么反复看 Test Error 会让 Test 逐渐变成 Validation？

> 什么是 Benchmark Feedback Loop？

> 什么是 Pretraining Contamination？

> 为什么公开 Benchmark 的污染风险通常更高？

> 什么是 Outcome Leakage？

> 为什么“后续是否被投诉”不能用于预测发布时的风险？

> Annotator View 和 Model View 为什么必须分开？

> 为什么模型 Input Builder 最好用字段白名单？

> Prompt 如何产生 Test Leakage？

> Rule Engine 如何产生 Test Leakage？

> 为什么 Threshold 也不能在 Final Test 上调？

> Direct Leakage 和 Indirect Leakage 有什么区别？

> 什么叫 Benchmark Firewall？

> Benchmark Firewall 为什么不仅是一个算法？

> Access Control 在 Benchmark 中有什么作用？

> 为什么 Final Test 可以设置 Hidden Label？

> 为什么 RAG Snapshot 需要版本化？

> 为什么 Temporal Benchmark 需要 Knowledge Cutoff？

> 什么是 Lineage Guard？

> 为什么每次 Final Test Run 都值得记录？

> 什么是 Leakage Audit Checklist？

> Leakage Severity 为什么需要分级？

> 为什么“任何重复信息都是泄漏”这种理解也是错误的？

> Evaluation Claim 为什么决定了什么算泄漏？

> 什么叫 Benchmark Contract？

> 为什么 Gold Label 本身也可能存在时间错误？

> 什么是 Temporal Provenance？

> 哪些泄漏可以自动检查？

> 哪些泄漏必须依靠流程治理？

> 为什么 `LeakageAudit_V0.1` 应该成为 Dataset 的正式组成部分？

> 为什么 Final Test 用久以后可以降级为 Regression Set？

> 什么是 Benchmark Rotation？

如果这些你都能自己讲清楚：

\[
\boxed{
第四课第7阶段真正掌握
}
\]

---

# 三百一十四、本阶段最终只记一句话

> **Data Leakage 不只是“Train 里出现了 Test 原文”，而是任何不应该在开发阶段可用的测试相关信息——标签、专家答案、未来结果、派生样本、RAG 内容、Prompt 规则、阈值，甚至人类对 Test 错误的反复观察——越过评测边界并影响了系统；真正可信的 Benchmark 必须依靠数据血缘、时间约束、系统隔离和 Benchmark Firewall 共同保护。**

最后把这一阶段压成一张图：

```text
                    Final Test
                        │
                        ▼
                Evaluation Claim
                        │
                        ▼
                Benchmark Contract
                        │
       ┌────────────────┼─────────────────┐
       ▼                ▼                 ▼
  Allowed Info      Forbidden Info      Time Cutoff
       │                │                 │
       └────────────────┼─────────────────┘
                        ▼
                 Leakage Audit
       ┌────────────────┼──────────────────┐
       ▼                ▼                  ▼
    Dataset           System             Human
       │                │                  │
 Project/Dup       Prompt/RAG/Rules     Test Peeking
 Lineage/Time      Threshold/Tools      Error Feedback
       │                │                  │
       └────────────────┼──────────────────┘
                        ▼
                Benchmark Firewall
                        │
                        ▼
                LeakageAudit_V0.1
                        │
                        ▼
                 Trusted Evaluation
```

---

# 下一阶段：第四课 · 第 8 阶段
## Label Schema——专家到底应该标什么？为什么“有风险 / 没风险”两个标签远远不够构建一个真正的政府采购专业模型？

第 8 阶段我们会第一次真正把：

```text
专家判断
```

变成：

# 可训练、可评测、可统计的结构化标签。

核心会解决：

```text
risk_present
risk_type
risk_level
needs_review
rationale
evidence
suggested_action
```

这些字段究竟：

> 哪些应该成为训练 Target？

哪些：

> 只是 Metadata？

哪些：

> 应该由专家填写？

哪些：

> 可以后续派生？

而且会正式建立我们政府采购风险审查的第一版五大类：

```text
A 供应商资格
B 技术参数
C 商务要求
D 评分标准
E 采购需求
```

同时处理一个非常关键的问题：

> **“不知道 / 证据不足 / 需要人工复核”到底是不是一个合法答案？**

最终我们会得到：

# `AnnotationSchema_V0.1`

从那个阶段开始，我们的数据才真正进入：

> **专家标注体系。**

---

<!-- LESSON 04 STAGE 07 END -->


<!-- LESSON 04 STAGE 08 START -->

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

<!-- LESSON 04 STAGE 08 END -->


<!-- LESSON 04 STAGE 09 START -->

# 第四课 · 第 9 阶段
# 专家标注、双人复核与一致性
## 为什么两个真正懂政府采购的专家，也可能给同一个 Clause 完全不同的 Label？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **“这个专家很厉害，所以他说什么就是什么。”**
2. **明确规则 + 独立标注 + 分歧检测 + 专家裁决 + 可追溯记录。**
3. **“删掉这条，太麻烦了。”**
4. **为什么他们会不一致？**
5. **专家分歧常常是在帮助我们找到 Dataset 最重要的边界。**
6. **Label定义不清 上下文不足 风险类别边界重叠 标注指南没覆盖这种情况 案例本身就是Hard Case 法规依据存在解释空间**
7. **使用自己的经验规则；**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `ANN` | ANN/近似最近邻：在大规模向量中快速寻找相似项 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `Adjudication` | 专家裁决：对分歧样本形成最终 Gold 结论 |
| `Annotation Guideline` | 标注规范：统一专家如何理解字段、边界和例外 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `Calibration` | 校准：使模型置信度更接近实际正确率 |
| `Sample` | 样本：具有明确输入、目标和来源的一条训练/评测记录 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `Dataset` | 数据集：按统一 Schema、版本和质量标准组织的样本集合 |
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |
| `Observe` | Observe/观察：读取当前状态和工具结果 |

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

第 8 阶段我们已经解决：

> **专家到底应该标什么？**

我们建立了：

```text
risk_present
primary_risk_type
risk_subtype
risk_level
needs_review
rationale
evidence
suggested_action
```

也就是：

# `AnnotationSchema_V0.1`

但现在出现一个更棘手的问题。

假设有这样一条采购要求：

> “供应商近三年应具有不少于 5 个类似项目业绩。”

我们把完全相同的 Clause 分别交给三位专家。

专家 A：

```text
risk_present = true
risk_type = supplier_qualification
```

专家 B：

```text
risk_present = uncertain
needs_review = true
```

专家 C：

```text
risk_present = false
```

三个人都不是乱点。

甚至三个人都可能有很多年采购业务经验。

那到底发生了什么？

问题很可能并不是：

> “谁不专业？”

而是：

> **三个人脑子里使用的判断规则并不完全相同。**

这就是第 9 阶段真正要解决的问题。

---

# 一、本阶段只解决一个核心问题

> **怎样把多个专家个人脑子里的经验，变成一套可重复、可衡量、可复核、可持续改进的团队标注标准，并最终产出真正可以称为 Gold 的数据？**

今天最终要得到两个东西：

# `AnnotationGuideline_V0.1`

即：

> **专家标注指南 V0.1**

以及：

# `AdjudicatedGoldSet_V0.1`

即：

> **经过分歧裁决后的 Gold 数据集 V0.1**

先把整个阶段的路线看完。

```text
Annotation Schema
标注字段已经定义
        │
        ▼
Annotation Guideline
把每个Label写成统一判断规则
        │
        ▼
Pilot Annotation
小批量试标，先发现规则问题
        │
        ▼
Blind Double Annotation
两位专家独立、互不看答案地标
        │
        ▼
Agreement Measurement
测量两位专家到底有多一致
        │
        ▼
Disagreement Analysis
分析为什么不一致
        │
        ▼
Adjudication
第三位/高级专家进行裁决
        │
        ▼
Guideline Revision
把裁决形成的新规则写回指南
        │
        ▼
Adjudicated Gold Set
形成可用于Benchmark的高质量Gold数据
```

一句话理解：

> **不是“找专家来标”，而是建立一条专家知识生产流水线。**

---

# 二、今天最重要的 5 个核心心智模型

这 5 个请当成第 9 阶段的骨架。

## 心智模型 1：Gold ≠ 某一个专家说了算

\[
\boxed{
Gold
\neq
SingleExpertOpinion
}
\]

Gold 不是：

> “这个专家很厉害，所以他说什么就是什么。”

Gold 更接近：

> **明确规则 + 独立标注 + 分歧检测 + 专家裁决 + 可追溯记录。**

一个资深专家仍然可能：

- 忽略上下文；
- 使用自己的经验规则；
- 前后尺度漂移；
- 疲劳；
- 对模糊边界有个人偏好。

所以专业数据系统不能把：

> 专家权威

替代：

> 数据质量流程。

---

## 心智模型 2：专家分歧不是垃圾，而是最值钱的信号之一

\[
\boxed{
Disagreement
=
Information
}
\]

如果两位专家对同一条 Clause 不一致，我们第一反应不应该是：

> “删掉这条，太麻烦了。”

而应该问：

> **为什么他们会不一致？**

因为分歧可能在告诉我们：

```text
Label定义不清
上下文不足
风险类别边界重叠
标注指南没覆盖这种情况
案例本身就是Hard Case
法规依据存在解释空间
```

所以：

> **专家分歧常常是在帮助我们找到 Dataset 最重要的边界。**

---

## 心智模型 3：先独立判断，再讨论

这个流程叫：

# Blind Annotation
## 盲标 / 独立标注

意思是：

> 专家 A 在提交答案之前，看不到专家 B 的答案。

为什么？

因为如果专家 A 先看到：

```text
专家B：High Risk
```

A 很容易受到影响。

这叫：

# Anchoring
## 锚定效应

尤其是高级专家意见，会让其他标注员下意识靠拢。

所以真正测专家是否一致：

> 必须先让他们独立回答。

---

## 心智模型 4：一致率不是为了给专家打分，而是为了给 Schema 体检

\[
\boxed{
AgreementMetric
\rightarrow
SchemaDiagnostic
}
\]

如果两位专家一致率只有 55%，不要立刻说：

> “专家水平不行。”

可能真正的问题是：

> **这个 Label 根本没有定义清楚。**

比如 `high risk` 如果指南只写：

> “风险较大的情况标 High。”

那 55% 一致率一点都不奇怪。

因此一致性指标首先是在问：

> **我们的标注规则是否足够清楚，能让专业人员重复得到相似结果？**

---

## 心智模型 5：裁决的真正产物，不只是最终 Label

# Adjudication
## 分歧裁决

很多团队把裁决理解成：

```text
A说Risk
B说No Risk
高级专家选Risk
结束
```

这是浪费。

真正高价值的是：

```text
为什么A这么判断？
为什么B这么判断？
最终为什么选这个？
以后遇到同类案例怎么统一？
```

然后把最后一条写回：

# Annotation Guideline

因此：

\[
\boxed{
Adjudication
\rightarrow
BetterGuideline
\rightarrow
BetterFutureLabels
}
\]

这才是闭环。

---

# 三、Annotation Guideline 到底是什么？

我们上一阶段已经有：

# Annotation Schema
## 标注结构

例如：

```text
risk_present
risk_type
needs_review
risk_level
```

但 Schema 只告诉专家：

> “要填哪些格子。”

它没有完整告诉专家：

> “什么情况下应该填哪个值。”

这就需要：

# Annotation Guideline
## 标注指南

可以把两者想成：

```text
Schema
=
考试答题卡

Guideline
=
考试评分标准
```

只有答题卡，没有评分标准：

> 大家当然各填各的。

---

# 四、一个专业 Label Guide 至少要回答 5 类问题

我们拿：

```text
risk_present
```

举例。

如果指南只写：

```text
true = 有风险
false = 无风险
uncertain = 不确定
```

几乎等于没写。

专业指南应该告诉专家：

| 项目 | 要回答的问题 |
|---|---|
| 定义 | 这个 Label 到底代表什么？ |
| 纳入条件 | 什么情况应该选它？ |
| 排除条件 | 什么情况看起来像，但不要选？ |
| 边界案例 | 最容易混淆的情况是什么？ |
| 所需上下文 | 判断之前必须看到什么信息？ |

这五项非常重要。

---

# 五、例如 `risk_present = true`

教学版定义可以写成：

> 根据当前可获得的采购条款、必要上下文和适用依据，存在较明确的风险信号，足以进入风险处理流程；但该 Label 本身不代表最终法律裁决。

注意：

> `Potential Risk`

和：

> `Final Illegal`

不是一回事。

---

# 六、那 `false` 呢？

不是：

> “我暂时没看出来，所以 False。”

而更应该是：

> **在必要上下文相对充分的情况下，按照当前标注规则，没有发现达到风险标记阈值的明显风险信号。**

关键词是：

# 上下文相对充分

---

# 七、那 `uncertain` 呢？

可以定义：

> **当前信息不足、规则适用存在明显不确定性，或者不同合理解释可能产生不同结论，不适合强制归入 true / false。**

于是：

```text
uncertain
```

不是失败。

它是在表达：

> **专业不确定性。**

---

# 八、一个非常典型的政府采购边界案例

条款：

> “供应商应保证故障发生后 2 小时内到达项目现场。”

专家 A：

> “2 小时现场响应，对外地供应商不利，Risk。”

专家 B：

> “这里只要求服务能力，并没有要求投标前就在本地设机构，No Risk。”

两个答案为什么不同？

因为 A 实际判断的是：

```text
响应时间是否形成事实性地域限制
```

B 判断的是：

```text
是否存在显性的本地机构准入条件
```

他们回答的：

> 其实不是完全同一个问题。

这时候真正需要修的，可能不是专家。

而是：

# Guideline

应该明确：

> “现场响应要求”和“预先设立本地机构”必须分别判断。

这就是专家分歧的价值。

---

# 九、正式标数据以前，千万不要一上来就标 10 万条

应该先做：

# Pilot Annotation
## 小规模试标

例如先抽：

```text
100～300条
```

教学示例。

重点不是数量。

而是：

> **让标注系统先撞墙。**

---

# 十、试标阶段专门找什么？

重点找：

```text
专家最容易争论的Label
Other特别多的地方
Unknown特别多的地方
同一句指南被不同人理解成不同意思的地方
上下文不足的地方
Subtype互相重叠的地方
```

如果发现 200 条里：

```text
60条都有严重争议
```

不要赶紧开 50 人标注大军。

应该先停下来：

> 修 Schema 和 Guideline。

---

# 十一、推荐的专业标注流程

从现在开始，你可以把政府采购专家标注流程记成：

```text
第一步
规则校准
Calibration

第二步
盲式双人独立标注
Blind Double Annotation

第三步
一致性测量
Agreement Measurement

第四步
分歧归因
Disagreement Analysis

第五步
专家裁决
Adjudication

第六步
规则回写
Guideline Revision

第七步
形成Gold
Gold Finalization
```

以后看到英文的时候，直接记中文：

> **校准 → 双盲标 → 测一致 → 找分歧 → 裁决 → 改规则 → 出 Gold**

这条链比英文名字重要得多。

---

# 十二、什么叫 Double Annotation？

# Double Annotation
## 双人标注

意思是：

> 同一条样本由两位专家分别独立标一次。

例如：

```text
Sample 001

专家 A：
risk_present = true
risk_type = A
needs_review = true

专家 B：
risk_present = uncertain
risk_type = A
needs_review = true
```

这里可以立刻看到：

```text
risk_type
一致

needs_review
一致

risk_present
不一致
```

这比只看：

> “整条一样/不一样”

专业很多。

---

# 十三、所以一致性必须“按字段测”

不要只算一个：

```text
Overall Agreement = 80%
```

应该分别看：

| 字段 | 一致性重点 |
|---|---|
| `risk_present` | 最核心 |
| `primary_risk_type` | 风险分类 |
| `risk_subtype` | 细粒度边界 |
| `risk_level` | 优先级标准是否稳定 |
| `needs_review` | 不确定性判断 |
| `evidence` | 证据选择是否稳定 |

这样你可能发现：

```text
risk_present       92%
risk_type          88%
needs_review       90%
risk_level         61%
risk_subtype       58%
```

这说明什么？

不是整个 Schema 都坏了。

而是：

> **Risk Level 和 Subtype 的定义明显还不够稳定。**

这才是可操作的信息。

---

# 十四、最简单的一致性指标：Percent Agreement

# Percent Agreement
## 直接一致率

公式很简单：

\[
Agreement
=
\frac{两人相同的样本数}
{总双标样本数}
\]

假设两位专家共同标了：

```text
100条
```

其中：

```text
86条risk_present一致
```

那么：

\[
Agreement=86\%
\]

非常直观。

---

# 十五、但 86% 一定很高吗？

不一定。

假设数据里：

```text
95%
都是No Risk
```

两位专家都懒得判断，全部点：

```text
No Risk
```

就能得到：

> 95% 一致。

但这并不说明他们真的很专业。

所以我们需要一个稍微聪明一点的指标。

---

# 十六、Cohen's Kappa 是什么？

# Cohen's Kappa
## Cohen κ 系数 / 扣除随机一致后的专家一致性

不用背数学推导。

只理解一个问题：

> **两个人的一致，有多少不是“碰巧选到同一个答案”？**

公式是：

\[
\kappa
=
\frac{p_o-p_e}
{1-p_e}
\]

其中：

\[
p_o
\]

表示：

> 实际观察到的一致率。

\[
p_e
\]

表示：

> 如果按两个人自己的 Label 分布随机选择，理论上能碰巧一致多少。

---

# 十七、生活类比

假设考试只有：

```text
A
B
```

但所有人 95% 时间都选 A。

那么两个人随便乱答：

> 也很容易一样。

Kappa 做的事情，就是：

> 把这种“因为类别极度不平衡造成的幸运一致”扣掉一些。

---

# 十八、一个直觉例子

假设：

```text
Observed Agreement
实际一致率
= 0.90
```

而由于 Label 分布，随机也可能得到：

```text
Expected Agreement
随机期望一致率
= 0.70
```

那么：

\[
\kappa
=
\frac{0.90-0.70}
{1-0.70}
=
0.67
\]

所以看起来：

> 90% 一致。

扣掉随机因素以后：

> Kappa 只有约 0.67。

---

# 十九、Kappa 到底多少才算合格？

这里特别容易陷入“背阈值”。

不要这样。

没有一个数字能脱离：

```text
任务难度
Label数量
类别不平衡
业务风险
专家数量
```

直接宣布：

> “0.8 就好，0.6 就垃圾。”

我们更应该看：

> **它是否足以支撑这个 Label 的用途？**

比如：

Gold Benchmark 的核心 `risk_present`：

> 要求应该比普通训练语料更高。

细粒度 Subtype：

> 可以允许低一些，然后继续迭代定义。

所以：

# Agreement 是诊断指标，不是宗教数字。

---

# 二十、自由文本 Rationale 怎么算一致？

这是个很现实的问题。

专家 A：

> “该条件可能限制外地供应商参与。”

专家 B：

> “该条款将供应商注册地作为准入条件，需要审查其必要性。”

文字完全不同。

但意思：

> 基本一致。

显然不能用：

```text
string equality
```

---

# 二十一、Rationale 更适合按“信息要素”评

例如拆成：

```text
Observed Fact
Risk Concern
Context Needed
Conclusion Scope
```

然后问：

> 两个专家是否抓住相同核心事实？

是否识别同一风险机制？

是否认为需要相似的上下文？

---

# 二十二、所以结构化 Rationale 再次发挥价值

如果自由文本只有一个大段：

> 很难比较专家是否一致。

如果拆成：

```text
observed_fact
risk_concern
context_needed
```

就可以分别判断。

这也再次说明：

> 第 8 阶段设计 Schema，不是多此一举。

---

# 二十三、专家出现分歧以后，不能只记录“不同”

应该做：

# Disagreement Taxonomy
## 分歧类型分类

这是非常专业的一步。

我们至少应该区分几种分歧。

---

# 二十四、第一种：Label Definition Disagreement
## 标签定义分歧

例如：

专家 A 认为：

> 本地响应要求属于资格风险。

专家 B 认为：

> 属于商务履约风险。

说明：

> Risk Type 边界定义不清。

---

# 二十五、第二种：Context Disagreement
## 上下文不足导致的分歧

A 看 Clause：

> 认为有风险。

B 认为：

> 必须先知道项目是否真的需要现场服务。

这说明：

> 输入给专家的 Context 不够。

---

# 二十六、第三种：Evidence Disagreement
## 证据解释分歧

两位专家：

> 对 Clause 本身理解差不多。

但是：

> 对适用依据或证据权重理解不同。

---

# 二十七、第四种：Severity Disagreement
## 风险等级分歧

两个人都认为：

> 有潜在风险。

但一个标：

```text
High
```

另一个：

```text
Medium
```

说明：

> `risk_level` 的工作定义需要加强。

---

# 二十八、第五种：Annotation Error
## 单纯标注错误

例如：

专家自己复核以后说：

> “这个我点错了。”

这当然存在。

但不能把所有分歧：

> 都归因于专家手滑。

---

# 二十九、第六种：True Boundary Case
## 真正边界案例

即使：

```text
指南清楚
上下文完整
专家都认真
```

合理专业人员：

> 仍然可能存在不同判断。

这种案例非常重要。

因为它告诉我们：

> **这个任务本来就不是完全确定性的。**

---

# 三十、这六种分歧的处理方法完全不同

比如：

```text
定义分歧
→ 改Guideline

上下文分歧
→ 补Context

证据分歧
→ 明确Evidence规则

等级分歧
→ 重写Severity标准

标注错误
→ 修正Label

真实边界案例
→ 保留uncertain / needs_review
```

所以：

> **分歧分析比“统计一致率”更重要。**

---

# 三十一、什么叫 Adjudication？

# Adjudication
## 专家裁决

当 A、B 不一致时，

由：

```text
高级专家
专家小组
领域负责人
```

根据统一规则：

> 做最终裁决。

但是正确的裁决过程不是：

> “老板说 A 对。”

应该记录：

```text
A为什么这么标
B为什么这么标
最终选什么
为什么
需要新增哪条指南
```

---

# 三十二、一个裁决记录可以长这样

```json
{
  "sample_id": "SAMPLE-00217",

  "annotator_a": {
    "risk_present": true
  },

  "annotator_b": {
    "risk_present": "uncertain"
  },

  "disagreement_type": "context_disagreement",

  "adjudicated_label": {
    "risk_present": "uncertain",
    "needs_review": true
  },

  "adjudication_reason": "现有上下文不足以判断该服务时限是否具有充分业务必要性。",

  "guideline_update": "遇到现场响应时间要求时，应区分履约能力要求与投标前本地机构要求。"
}
```

这才是一条真正有价值的裁决记录。

---

# 三十三、你会发现：最后那一行最值钱

```text
guideline_update
```

因为它让：

> 以后 1000 条同类数据不再重复争论。

所以高质量标注系统应该形成：

\[
\boxed{
OneDisagreement
\rightarrow
OneReusableRule
}
\]

理想情况下如此。

---

# 三十四、Annotation Guideline 应该越标越厚吗？

不一定越厚越好。

我们要的是：

> **越来越准确。**

如果一份 Guideline 最后有：

```text
900页
```

专家根本不会看。

真正有用的方式是：

# Decision Tree
## 决策树

---

# 三十五、比如地域条件可以做成一张判断树

```text
看到“本地 / 项目所在地 / 本市”
                │
                ▼
是否把所在地作为投标前准入条件？
        │
    ┌───┴───┐
    │       │
   是       否
    │       │
    ▼       ▼
进入资格   是否只是履约能力要求？
风险审查        │
           ┌────┴────┐
           │         │
          是         否
           │         │
           ▼         ▼
检查必要性      进入其他规则
和比例性
```

这种比十页散文：

> 好用得多。

---

# 三十六、所以从第 9 阶段开始，Annotation Guide 最好包含三种东西

这里是本回答唯一集中列出的结构清单：

1. **Definition（定义）**：这个 Label 到底是什么意思；
2. **Decision Rule（判断规则）**：遇到什么条件选什么；
3. **Positive Example（正例）**：典型应该标什么；
4. **Negative Example（反例）**：长得像但不要这么标；
5. **Boundary Example（边界例）**：什么情况下应 `uncertain / needs_review`；
6. **Evidence Requirement（证据要求）**：做判断前至少需要什么；
7. **Escalation Rule（升级规则）**：什么时候必须交给高级专家裁决。

这比“写一份长说明书”更专业。

---

# 三十七、为什么 Blind Double Annotation 特别适合 Gold Set？

因为 Gold Set 最终要拿来：

> 给模型考试。

如果 Gold 本身只是：

> 一个专家快速点出来的，

那 Test Score 再精确也没意义。

例如模型与某专家的一致率：

```text
92%
```

听起来很高。

但如果另一个专家和这个专家本身：

```text
只有65%
```

那我们应该先问：

> Gold 到底稳不稳？

---

# 三十八、这出现一个非常重要的关系

\[
\boxed{
ModelPerformance
不能脱离
HumanAgreement
解释
}
\]

如果人类专家自己都难以稳定判断，

模型达到一个上限以后：

> 继续追求 100% Accuracy 可能没有意义。

---

# 三十九、这不是说“人不一致，模型就不用做好”

而是说：

> **Benchmark 必须告诉我们哪些 Case 是高共识，哪些是低共识。**

于是以后可以有：

```text
consensus_level
```

例如：

```text
high_consensus
adjudicated
boundary_case
```

---

# 四十、这样评测模型时可以分别看

```text
High-consensus Accuracy
```

和：

```text
Boundary-case Accuracy
```

这两个数字：

> 含义完全不同。

---

# 四十一、举个简单例子

假设 Test 里 1000 条。

其中：

```text
800条
专家双标直接一致

200条
经过裁决
```

模型：

```text
高共识样本 94%

裁决样本 68%
```

这比只报：

```text
总准确率 88.8%
```

有用太多。

---

# 四十二、为什么？

因为你马上知道：

> 模型真正困难的是专家自己也容易争议的边界区。

而不是：

> 基础判断能力全面失效。

---

# 四十三、这会直接指导训练

以后可以专门增加：

# Hard Cases

也就是：

> 专家分歧高、模型也容易错的案例。

这正好会进入：

> 第 10 阶段 Hard Negative。

所以第四课的阶段不是孤立的。

---

# 四十四、专家一致率越高越好吗？

一般来说当然希望：

> 稳定。

但这里有一个坑。

假设为了提高一致率，我们规定：

> “所有不确定的都标 No Risk。”

专家一致率可能立刻：

> 变高。

---

# 四十五、但 Dataset 变好了吗？

没有。

我们只是：

> 把真实不确定性藏掉了。

所以真正目标不是：

# Maximum Agreement

而是：

# Valid Agreement

有效一致。

---

# 四十六、可以理解成

\[
\boxed{
GoodAgreement
=
Consistency
+
CorrectMeaning
}
\]

如果大家一致地错：

> 没价值。

---

# 四十七、因此 Gold 数据必须同时关心

```text
Reliability
可靠性：不同人能不能稳定复现

Validity
有效性：这个Label到底是不是在表达我们真正想测的东西
```

这两个词以后会经常遇到。

简单记：

> **Reliable = 稳不稳。**

> **Valid = 对不对题。**

---

# 四十八、一个极端例子

让所有专家按规则：

> “出现‘本市’就标 Risk。”

他们一致率可能：

```text
99%
```

Reliability：

> 极高。

但这显然不能代表真正的专业风险判断。

Validity：

> 很差。

---

# 四十九、所以 Annotation Quality 不能只看 Agreement

还要：

> 抽样专家审查、案例复盘、依据核验。

---

# 五十、正式大规模标注以前，还有一步很重要

# Calibration Session
## 专家校准会

什么意思？

先抽：

```text
20～50条代表性案例
```

大家分别判断。

然后集中讨论：

> 为什么不同？

---

# 五十一、Calibration 的目标不是

> 让所有人服从某一个人。

而是：

> 把隐含规则说出来。

例如专家 A 可能说：

> “我默认资格条件应该考虑项目规模。”

专家 B：

> “我只有看到明显限制时才标 Risk。”

---

# 五十二、原来两个人心里使用的是：

> 两个不同阈值。

这时候 Guideline 就应该明确：

> 我们的数据任务究竟采用哪个判断阈值。

---

# 五十三、所以 Calibration 做的是

# Mental Model Alignment
## 专家心智模型对齐

这几个字特别重要。

最终我们不只是：

> 对齐按钮。

而是：

> 对齐判断方式。

---

# 五十四、推荐的 Gold 标注组织结构

可以分成三层角色。

```text
Annotator
标注专家

Reviewer
复核专家

Adjudicator
裁决专家
```

---

# 五十五、Annotator 的职责

根据 Guide：

> 独立判断。

不要猜：

> “裁决专家喜欢什么答案。”

---

# 五十六、Reviewer 的职责

检查：

```text
Label
Rationale
Evidence
Schema逻辑
```

是否符合标准。

---

# 五十七、Adjudicator 的职责

处理：

> 真正分歧和规则边界。

同时负责：

> 更新 Guideline。

---

# 五十八、注意一个很重要的治理原则

最好不要：

> 每一条数据都让最贵的高级专家从头标。

这非常浪费。

合理的方式是：

```text
普通明确案例
→ 双人标准标注

存在分歧
→ 高级专家裁决

复杂高价值Gold
→ 加强审核
```

这叫：

# Escalation
## 分级升级处理

---

# 五十九、这样成本才能控制

假设：

100,000 条数据。

如果每条都需要：

> 首席采购专家 10 分钟，

项目基本不可持续。

---

# 六十、而如果：

```text
80%
双标直接一致

15%
需要普通复核

5%
进入高级专家裁决
```

整体成本：

> 就现实得多。

这些比例只是教学示例，不是固定标准。

---

# 六十一、现在谈一个很重要的数据字段

# disagreement_type

为什么值得保存？

因为半年以后可以统计：

```text
40%的分歧来自risk_level
30%的分歧来自context不足
20%的分歧来自Subtype边界
10%的分歧来自操作错误
```

那下一版数据工程优先级就非常清楚。

---

# 六十二、如果没有保存分歧原因

你只知道：

> “专家有 18% 不一致。”

然后：

> 不知道该修哪里。

---

# 六十三、所以专家分歧本身也应该成为 Dataset Metadata

例如：

```json
{
  "double_annotated": true,
  "initial_agreement": false,
  "disagreement_type": "context_insufficient",
  "adjudication_required": true
}
```

---

# 六十四、现在设计 Gold 状态

我们上一阶段有：

```text
draft
reviewed
adjudicated
gold
```

现在可以真正理解它们。

```text
draft
=
单人初标

reviewed
=
经过第二人检查

adjudicated
=
曾有分歧，已经裁决

gold
=
达到当前Gold发布标准
```

---

# 六十五、注意

```text
adjudicated
```

和：

```text
gold
```

仍然不完全一样。

一条样本可能经过裁决，

但发现：

> 原始 PDF OCR 不可靠。

那么：

> 仍然不应该进 Gold Benchmark。

因为 Gold 需要：

```text
Parse可信
Structure可信
Normalization可信
Split可信
Leakage可信
Annotation可信
```

---

# 六十六、到这里，第四课前面的东西终于全部合流

真正的 Gold Sample 可能要求：

```text
parse_status = verified
structure_status = verified
normalization_status = verified
dedup_status = verified
split_status = valid
leakage_status = passed
annotation_status = gold
```

这才叫：

# End-to-End Gold

不是：

> “Label 看过了就叫 Gold。”

---

# 六十七、这是这一课非常重要的专业化升级

\[
\boxed{
GoldQuality
=
WholePipelineQuality
}
\]

---

# 六十八、现在设计 `AnnotationGuideline_V0.1`

它不是一篇长文章。

可以组织成：

```text
Task Definition
任务到底在判断什么

Label Definitions
每个标签正式定义

Decision Trees
常见场景判断流程

Positive Examples
正例

Negative Examples
反例

Boundary Cases
边界例

Required Context
需要查看的上下文

Evidence Rules
证据规则

Escalation Rules
什么时候升级裁决

Version History
规则怎么变化
```

每个英文后面都应该像这样直接给中文含义。

以后课程我都会保持这个规则。

---

# 六十九、再设计 `AdjudicatedGoldSet_V0.1`

一条 Gold Record 概念可以是：

```json
{
  "sample_id": "GOLD-000217",

  "final_label": {
    "risk_present": "uncertain",
    "primary_risk_type": "A",
    "needs_review": true
  },

  "annotation_a": {
    "risk_present": true
  },

  "annotation_b": {
    "risk_present": "uncertain"
  },

  "initial_agreement": false,

  "disagreement_type": "context_insufficient",

  "adjudication": {
    "final_decision": "uncertain",
    "reason": "现有材料不足以确认该条件的客观必要性。",
    "adjudicator_id": "EXP-SENIOR-003"
  },

  "consensus_status": "adjudicated",

  "guideline_version": "annotation_guideline_v0.1",

  "annotation_schema_version": "annotation_schema_v0.1",

  "gold_status": "gold"
}
```

---

# 七十、这里有一个很关键的设计

不要只保存：

```text
final_label
```

最好保留：

```text
A原始判断
B原始判断
最终裁决
```

为什么？

因为以后 Schema 更新以后：

> 我们可以重新分析专家分歧。

否则历史信息：

> 永远丢了。

---

# 七十一、这也是 Non-destructive Data Engineering

我们前面反复讲：

> Raw Text 不覆盖。

今天同样：

> Initial Annotation 也不要被 Final Gold 覆盖。

---

# 七十二、关系变成：

```text
Annotation A ─┐
              ├→ Adjudication → Final Gold
Annotation B ─┘
```

原始意见：

> 都保留。

---

# 七十三、现在做一个完整政府采购案例

Clause：

> “投标人须在本市设立固定办公场所，并提供房屋产权证明或租赁合同。”

专家 A：

```text
Risk = true
Type = Supplier Qualification
Level = high
```

专家 B：

```text
Risk = uncertain
Type = Supplier Qualification
Needs Review = true
```

---

# 七十四、分歧不是：

> Risk Type。

两个人都认为：

> 属于供应商资格维度。

真正分歧是：

> **是否已有足够信息把它从“需复核”提升为明确 Potential Risk。**

于是：

```text
disagreement_type
=
decision_threshold
```

即：

> 判断阈值分歧。

---

# 七十五、裁决专家可能认为

按照当前项目 Dataset 的任务定义：

> “只要条款将投标前固定本地办公场所作为准入条件，即进入 Potential Risk 筛查；最终合理性仍需结合完整事实复核。”

于是 Final：

```text
risk_present = true
needs_review = true
```

---

# 七十六、注意这个结果很有意思

```text
true
+
needs_review
```

并不矛盾。

它表示：

> **已经达到风险筛查阈值，但还没有达到最终裁决阈值。**

这就是第 8 阶段多维 Schema 的价值。

---

# 七十七、然后 Guideline 增加一句

> “`risk_present=true` 表示达到风险筛查标准，不等同于最终法律结论；仍可同时设置 `needs_review=true`。”

以后专家再遇到这种问题：

> 一致性就会提高。

---

# 七十八、这就是一次漂亮的 Guideline Learning Loop

```text
Case
 ↓
Disagreement
 ↓
Adjudication
 ↓
New Rule
 ↓
Future Agreement Improves
```

---

# 七十九、如果一致率一直上不去怎么办？

不要马上：

> “换专家。”

先检查三个层次。

第一层：

# Schema Problem

是不是 Label 本身重叠？

---

# 八十、第二层：

# Guideline Problem

定义是不是太模糊？

---

# 八十一、第三层：

# Task Problem

这个任务是不是天然无法仅靠现有输入判断？

例如：

> Clause 本身根本没有足够上下文。

---

# 八十二、如果第三种成立

那正确修复不是：

> 逼专家猜。

而是：

```text
增加Context
```

或者：

```text
允许uncertain
```

---

# 八十三、这也是专业数据项目一个重要能力

# 不强行制造确定性

---

# 八十四、现在看一个反例

团队规定：

> 两个专家不一致时，一律以高级专家意见覆盖。

最终数据库只留下：

```text
final_label
```

看起来很干净。

---

# 八十五、但几年以后：

发现模型在某一类数据表现很差。

想分析：

> 这些 Case 当初是不是专家也很争议？

已经无法知道。

因为：

> 初始分歧被覆盖了。

---

# 八十六、所以应该保留：

```text
annotation_a
annotation_b
adjudication
```

这叫：

# Annotation Lineage
## 标注血缘

---

# 八十七、我们以前有：

```text
Document Lineage
Data Lineage
Normalization Lineage
```

现在又加：

# Label Lineage

---

# 八十八、于是一个 Gold Label 可以一路追：

```text
Gold Label
   ↓
Adjudication Decision
   ↓
Expert A / Expert B
   ↓
Annotation Guideline Version
   ↓
Clause
   ↓
Source Block
   ↓
Original PDF
```

这已经非常接近真正专业的数据资产。

---

# 八十九、现在回到“专家一致性指标”

我们目前记两个就够：

```text
Percent Agreement
直接一致率
```

以及：

```text
Cohen's Kappa
扣除随机一致后的Kappa
```

现在先不用学更多统计指标。

后面真正遇到多标签、多专家、序数等级时，再扩展。

---

# 九十、关键不是收集指标名称

而是能回答：

> **哪一个字段不稳定？为什么不稳定？怎么修？**

这比背 10 个一致性公式：

> 有价值得多。

---

# 九十一、什么时候可以开始大规模标注？

不是：

> “Guideline 写完了。”

而是 Pilot 后至少确认：

```text
核心Label基本稳定
主要分歧类型已经知道
专家知道什么时候选uncertain
上下文基本足够
裁决流程可以运转
Guideline可以版本化
```

然后再扩大。

---

# 九十二、否则会发生什么？

假设先标：

```text
100,000条
```

后来发现：

> `High Risk` 定义从一开始就不统一。

那 10 万条：

> 可能全部要重新审。

这种成本非常可怕。

---

# 九十三、所以小规模试标本质上是：

# Schema Unit Test
## 给标注体系做单元测试

程序上线前要 Test。

Annotation System：

> 也要 Test。

---

# 九十四、现在把整个第 9 阶段压缩成专业版流程

```text
1. Schema已经定义
       ↓
2. 写Annotation Guideline
   把Label变成可执行规则
       ↓
3. Calibration
   专家先做小批量心智对齐
       ↓
4. Pilot
   小批量试标
       ↓
5. Blind Double Annotation
   两位专家独立双标
       ↓
6. Agreement Measurement
   按字段测一致性
       ↓
7. Disagreement Analysis
   分析分歧类型
       ↓
8. Adjudication
   高级专家裁决
       ↓
9. Guideline Revision
   把新规则写回指南
       ↓
10. Gold Finalization
    形成可发布Gold
```

如果以后忘掉所有英文：

> **写规则 → 校准 → 试标 → 双标 → 测一致 → 找分歧 → 裁决 → 改规则 → 出 Gold。**

就记这条。

---

# 九十五、本阶段最值得警惕的几个反例

第一种：

> “找一个最资深专家，把 10 万条全部标完。”

问题是：

> 没有独立复核，也无法估计标签可靠性。

第二种：

> “两个人一起讨论着标。”

这不是 Independent Annotation。

你根本测不出：

> 两人是否真正独立一致。

第三种：

> “不一致的全部删掉。”

这会专门删掉：

> 最有价值的 Hard Case。

第四种：

> “为了提高一致率，把所有 Unknown 都改成 No Risk。”

指标更漂亮，

数据反而更假。

第五种：

> “只保存最终裁决，不保存初始分歧。”

以后完全无法研究：

> 标注不确定性。

第六种：

> “Kappa 到 0.8 就万事大吉。”

错误。

指标只是开始，

还要问：

> 具体哪里分歧、Gold 是否有效。

---

# 九十六、这次我们把核心模型再集中一次

如果第 9 阶段只记五句话：

> **Gold 不是某一个专家的意见，而是一套质量流程。**

> **专家分歧不是垃圾，而是发现边界和修正规则的高价值信号。**

> **必须先盲式独立标注，再讨论，否则测不到真实一致性。**

> **一致性指标首先是在给 Schema 和 Guideline 做体检，不是在给专家排名。**

> **裁决最有价值的产物不是那个最终 Label，而是可以复用到未来案例的新规则。**

这五句话，就是本阶段真正的核心。

---

# 九十七、本阶段最终工程产物

第一个：

# `AnnotationGuideline_V0.1`

它规定：

```text
Label定义
判断规则
正例
反例
边界案例
必需上下文
证据要求
升级裁决条件
版本记录
```

第二个：

# `AdjudicatedGoldSet_V0.1`

每条 Gold 不只有：

```text
final_label
```

还保留：

```text
双标结果
一致状态
分歧类型
裁决过程
指南版本
Gold质量状态
```

---

# 九十八、本阶段掌握测试

现在不看正文，你应该能回答：为什么一个资深专家单独标出来的数据不能天然叫 Gold？为什么专家分歧本身是有价值的信息？Blind Annotation 为什么必须在专家讨论之前进行？Double Annotation 和 Review 有什么区别？为什么一致性要按 `risk_present`、`risk_type`、`risk_level` 等字段分别测？Percent Agreement 在测什么？Cohen's Kappa 为什么要扣除“随机碰巧一致”？为什么不应该迷信某一个 Kappa 阈值？Rationale 为什么不能简单用字符串相等来算一致性？专家分歧至少可能来自哪些不同原因？为什么 Context 不足应该补 Context，而不是逼专家二选一？Adjudication 的真正作用是什么？为什么裁决结果必须写回 Annotation Guideline？为什么 Gold 数据应该保留 Expert A、Expert B 和 Final Decision 三层信息？什么叫 Annotation Lineage？为什么高一致率不一定代表高质量数据？Reliability 和 Validity 有什么区别？为什么 Gold Quality 必须是整条数据 Pipeline 的质量，而不仅仅是 Label 被专家看过？

如果这些能讲清楚：

\[
\boxed{
第四课第9阶段真正掌握
}
\]

---

# 九十九、本阶段最终只记一句话

> **高质量专家标注不是“请专家给答案”，而是先用统一 Guideline 对齐判断标准，再让专家独立双标，用一致性指标发现规则问题，对真正分歧进行裁决，并把裁决经验不断写回指南；Gold 的本质不是专家权威，而是一个可复现、可审计、可持续改进的专家知识生产流程。**

最后只留这一张图：

```text
                  AnnotationSchema
                  专家要标什么
                        │
                        ▼
                AnnotationGuideline
                  怎么统一判断
                        │
                        ▼
                   Calibration
                   专家先校准
                        │
                        ▼
              Blind Double Annotation
                 两位专家独立双标
                        │
                        ▼
               Agreement Measurement
                 测到底有多一致
                        │
                        ▼
                Disagreement Analysis
                 为什么会不一致
                        │
                        ▼
                    Adjudication
                    专家裁决
                        │
                        ▼
                 Guideline Revision
                   新规则写回
                        │
                        ▼
               AdjudicatedGoldSet_V0.1
                   真正Gold数据
```

下一阶段会接着这条线进入：

<!-- LESSON 04 STAGE 09 END -->


<!-- LESSON 04 STAGE 10 START -->

# 第四课 · 第 10 阶段
# Hard Negative 与边界案例设计
## 为什么模型真正的专业能力，不是在“明显对 / 明显错”的题目上体现，而是在两个几乎一样的案例之间做出不同判断？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Hard Negative 不是普通负样本，而是“非常像正样本的负样本”。 它的作用是打掉模型的错误捷径。**
2. **真正有价值的数据经常是一对，而不是一条。 两个案例越相似、结论越不同，越能暴露模型是否抓住了关键条件。**
3. **最好的 Hard Case 往往来自真实错误和专家分歧，而不是靠人凭空编故事。 模型错过什么，就围绕什么补数据。**
4. **Boundary Case（边界案例）不是必须强行二选一。 如果合理结论确实依赖缺失上下文，就应该保留 uncertain / needs_review。**
5. **Hard Case 既是训练材料，也是 Benchmark 的压力测试材料。 但同一个案例及其改写版本绝不能一边训练、一边考试。**
6. **Hard Negative 的价值，是让模型不能再靠关键词和表面模式取巧。**
7. **真正高价值的数据经常不是一条样本，而是一对只差关键条件的对比样本。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Hard Negative` | 高难负例：表面像风险但正确结论不应判风险 |
| `ANN` | ANN/近似最近邻：在大规模向量中快速寻找相似项 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `Hard Positive` | 高难正例：没有明显关键词但确实需要识别的风险 |
| `Dataset` | 数据集：按统一 Schema、版本和质量标准组织的样本集合 |
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `Accuracy` | 准确率：全部样本中判断正确的比例 |
| `Shortcut Learning` | 捷径学习：利用表面相关线索而非真正任务规律 |
| `Annotation Guideline` | 标注规范：统一专家如何理解字段、边界和例外 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |

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

第 9 阶段我们已经建立了：

```text
Annotation Schema
标什么
        ↓
Annotation Guideline
怎么统一判断
        ↓
双人独立标注
        ↓
一致性测量
        ↓
分歧分析
        ↓
专家裁决
        ↓
AdjudicatedGoldSet_V0.1
```

现在终于有了一批相对可信的专家 Label。

但这时候会出现一个很危险的假象。

假设模型测试结果：

```text
Accuracy = 94%
```

看起来已经非常优秀。

可我们仔细看 Test Set：

```text
明显违规表达
→ Risk

普通标准条款
→ No Risk
```

模型甚至不用真正理解政府采购业务。

只需要学几个词：

```text
“本市”
“唯一”
“指定品牌”
“注册满5年”
```

就可能拿到非常漂亮的分数。

这类模型一旦进入真实文件，就会迅速暴露：

> **它学会的是关键词，不是判断边界。**

所以第 10 阶段要解决的是：

# 怎样专门构造“容易骗过模型”的数据？

最终产物是：

# `HardCaseSet_V0.1`

---

# 一、本阶段只解决一个核心问题

> **怎样让训练数据和测试数据包含足够多的“表面很像、专业结论却不同”的案例，从而迫使模型学习真正决定判断结果的关键条件，而不是记关键词、模板和表面模式？**

先看整条流程。

```text
专家Gold数据
    │
    ▼
发现容易案例与困难案例
    │
    ▼
构造对比案例
Contrastive Cases
    │
    ▼
设计Hard Negative / Hard Positive
    │
    ▼
加入边界案例
Boundary Cases
    │
    ▼
专家复核
    │
    ▼
切分与泄漏检查
    │
    ▼
HardCaseSet_V0.1
```

中文记忆就是：

> **找“容易被骗”的地方 → 做成成对案例 → 专家确认 → 加入训练和考试。**

---

# 二、本阶段最重要的 5 个核心心智模型

这 5 个，是第 10 阶段真正需要留下来的东西。

1. **Hard Negative 不是普通负样本，而是“非常像正样本的负样本”。** 它的作用是打掉模型的错误捷径。  
2. **真正有价值的数据经常是一对，而不是一条。** 两个案例越相似、结论越不同，越能暴露模型是否抓住了关键条件。  
3. **最好的 Hard Case 往往来自真实错误和专家分歧，而不是靠人凭空编故事。** 模型错过什么，就围绕什么补数据。  
4. **Boundary Case（边界案例）不是必须强行二选一。** 如果合理结论确实依赖缺失上下文，就应该保留 `uncertain / needs_review`。  
5. **Hard Case 既是训练材料，也是 Benchmark 的压力测试材料。** 但同一个案例及其改写版本绝不能一边训练、一边考试。

这五句话先记住。

下面所有内容都只是它们的展开。

---

# 三、先把四类样本彻底分清

我们先不用复杂术语。

看这张表。

| 类型 | 中文理解 | 模型难度 | 示例 |
|---|---|---:|---|
| Easy Positive | 明显正例 | 低 | 明确要求投标企业必须在本市注册 |
| Easy Negative | 明显负例 | 低 | 普通的履约质量要求 |
| Hard Positive | 隐蔽正例 | 高 | 风险不靠明显关键词，而藏在组合条件中 |
| Hard Negative | 迷惑性负例 | 高 | 出现“本地”等敏感词，但实际上不是投标准入限制 |
| Boundary Case | 边界案例 | 很高 | 必须结合项目场景才能判断 |

真正决定专业模型质量的：

> 往往是后三类。

---

# 四、什么叫 Hard Negative？

# Hard Negative
## 高难负样本 / 迷惑性负样本

它不是：

> 普通“没有风险”的条款。

而是：

> **表面特征很像风险案例，但专业判断不应该直接判为风险。**

这是最关键的定义。

---

## 一个最典型的例子

案例 A：

> “供应商须在本市设立固定服务机构方可参与投标。”

可能进入：

```text
Potential Risk
```

因为这里把：

> 投标前已经设立本地机构

作为了参与条件。

再看案例 B：

> “中标供应商应保证故障发生后 2 小时内到达项目现场，不限制服务机构设立方式。”

它同样出现：

```text
现场
2小时
项目所在地
```

甚至模型可能觉得：

> “又是地域限制。”

但是它和 A 有一个非常关键的区别：

```text
A
投标前必须存在本地机构

B
要求履约响应能力
但不限定实现方式
```

这个差异：

> 才是模型真正应该学习的东西。

所以 B 就是一个很有价值的：

# Hard Negative

---

# 五、为什么普通负样本远远不够？

假设训练数据是：

```text
Risk:
必须在本市注册
必须拥有本地办公场所
必须为某品牌认证代理商

No Risk:
按时交货
提供培训
提供质量保证
```

模型很快就会学到：

```text
出现“本市”
→ Risk

出现“品牌”
→ Risk
```

这叫：

# Shortcut Learning
## 捷径学习

意思是：

> 模型找到了一个很容易的表面规律，于是懒得学习真正复杂的业务逻辑。

---

# 六、Hard Negative 的核心作用就是“拆捷径”

可以把它写成：

\[
\boxed{
HardNegative
\rightarrow
BreakShortcut
}
\]

例如你发现模型学成：

\[
出现“本地”
\Rightarrow
Risk
\]

那就应该专门加入：

```text
包含“本地”
但是
No Risk / Needs Review
```

的案例。

模型就再也不能：

> 只看“本地”两个字。

它必须继续问：

```text
本地要求针对谁？
发生在投标前还是中标后？
是固定机构要求还是服务能力要求？
是否限制实现方式？
是否有业务必要性？
```

这时它才开始逼近真正的专业判断。

---

# 七、真正强的数据单位不是“一条”，而是“一对”

这是第 10 阶段最值得记住的一个专业思想：

# Contrastive Pair
## 对比样本对

例如：

### 样本 A

> 供应商必须在本市注册满 3 年。

### 样本 B

> 供应商中标后须在本市项目现场提供为期 3 年的运维服务。

两个句子都出现：

```text
本市
3年
供应商
```

但是“3 年”修饰的东西完全不同。

A：

```text
注册年限
```

B：

```text
服务期限
```

如果模型只学关键词：

> 非常容易混。

如果模型真正理解：

> 才能区分。

---

# 八、这可以理解成“最小差异测试”

英语里常用一个词：

# Minimal Pair
## 最小对比样本

意思是：

> 两个案例尽可能相似，只改变一个关键条件，看答案是否应该随之改变。

这是极其强大的数据设计方法。

---

## 例子

版本 A：

> 投标人须在投标截止日前已在本市设立售后服务机构。

版本 B：

> 中标人应在合同履行期间保证本市项目现场的售后服务响应。

我们只改了几个关键条件：

```text
投标人
→ 中标人

投标前已有
→ 合同履行期间具备

固定机构
→ 服务响应
```

最终专业判断：

> 可能发生明显变化。

模型如果无法区分：

说明它还没有学到：

# Decision Boundary
## 决策边界

---

# 九、所以真正的专业能力，本质上是学“边界”

可以把模型想成一个裁判。

最容易的球：

> 离界线 10 米。

谁都能判。

真正考验裁判的是：

> 球压在线上。

AI 也是一样。

如果 Benchmark 全是：

```text
离边界很远的案例
```

模型 98%：

> 没什么值得骄傲。

我们真正想知道：

> **它在边界附近表现怎么样？**

---

# 十、这就是 Boundary Case

# Boundary Case
## 边界案例

边界案例不是：

> “故意出刁钻题。”

而是：

> **专业判断真的依赖更多事实、上下文或者规范解释的案例。**

例如：

> “供应商应具备 2 小时现场响应能力。”

单看这一句，很难永远固定为：

```text
Risk
```

或者：

```text
No Risk
```

因为可能涉及：

```text
医院核心系统
普通办公软件
应急设备
远程服务项目
全天候生产系统
```

项目不同：

> 2 小时响应的合理性也可能不同。

所以这种 Case 很可能应该：

```text
risk_present = uncertain
needs_review = true
```

并说明：

```text
context_needed
=
项目性质
现场服务必要性
停机影响
市场供应情况
```

---

# 十一、边界案例最重要的价值是什么？

不是让模型猜答案。

而是教模型：

> **什么时候不能武断地下结论。**

这是专业模型和普通分类器之间很重要的区别。

可以写成：

\[
\boxed{
ProfessionalModel
\neq
AlwaysAnswer
}
\]

更好的专业模型应该：

\[
\boxed{
KnowWhenToAnswer
+
KnowWhenToEscalate
}
\]

也就是：

> 知道什么时候可以判断，也知道什么时候该交给人。

---

# 十二、Hard Positive 又是什么？

# Hard Positive
## 隐蔽正样本

很多人只关注 Hard Negative。

其实 Hard Positive 同样重要。

Hard Positive 是：

> **真正存在风险信号，但没有明显危险关键词。**

例如某些条款不写：

```text
必须购买某品牌
```

而是列出：

```text
尺寸
接口
协议
特殊认证
独有功能
多个技术指标组合
```

单个指标看：

> 都正常。

组合起来：

> 可能高度指向极少数产品。

这里真正需要判断的是：

# Constraint Combination
## 约束组合

---

# 十三、模型如果只学显眼关键词，会漏掉 Hard Positive

这种错误叫：

# False Negative
## 漏报

对于风险筛查系统：

> 漏报往往非常值得关注。

所以一个专业 Dataset 不能只是防：

```text
误报
False Positive
```

还要防：

```text
漏报
False Negative
```

Hard Negative：

> 主要帮助降低误报。

Hard Positive：

> 主要帮助降低漏报。

---

# 十四、因此训练数据应该同时塑造两条边界

```text
Hard Negative
告诉模型：
“看起来像风险，但别乱报。”

Hard Positive
告诉模型：
“看起来不明显，但别漏掉。”
```

这两者一起，才是在真正训练：

# Decision Boundary

---

# 十五、Hard Case 最好的来源在哪里？

这里我们直接接第 9 阶段。

最好的第一来源是：

# Expert Disagreement
## 专家分歧

如果两位专家经常在某类 Case 上不一致：

> 这里天然就是困难区。

例如：

```text
本地服务能力
vs
本地机构准入
```

经常争议。

那就说明：

> 这类案例值得专门建设 Hard Case Slice。

---

# 十六、第二个高价值来源：Model Error

让 Baseline 模型跑一批人工 Gold。

然后把错误分成：

```text
False Positive
误报

False Negative
漏报
```

假设模型大量把：

> “项目所在地现场响应”

误判成地域准入风险。

这不是坏消息。

这是数据建设的方向。

---

# 十七、这形成一个非常重要的闭环

```text
模型
 ↓
犯错
 ↓
错误分类
 ↓
找到错误模式
 ↓
补Hard Case
 ↓
重新训练
 ↓
重新评测
```

这叫：

# Error-driven Data Improvement
## 错误驱动的数据改进

这个心智模型非常重要。

很多团队遇到模型问题第一反应是：

> 换更大的模型。

而真实项目中，经常更有效的是：

> **把模型反复犯错的边界变成更好的数据。**

---

# 十八、第三个来源：专家裁决记录

第 9 阶段我们保留了：

```text
annotation_a
annotation_b
disagreement_type
adjudication
```

特别是：

```text
disagreement_type = true_boundary_case
```

这些案例：

> 天然就是 Hard Case 候选。

所以保存专家分歧，不只是为了审计。

它直接成为：

# Future Training Asset
## 未来训练资产

---

# 十九、第四个来源：真实投诉、质疑、审查中的复杂案例

现实业务里真正发生争议的 Case：

> 往往比人工凭空编的案例更有价值。

但这里仍然要注意第 7 阶段的规则：

```text
后续裁决结果
可以帮助构造Gold

但不能泄漏到
预测时点的Model Input
```

所以：

> 真实案例 ≠ 可以随便把后续答案塞给模型。

---

# 二十、第五个来源：Counterfactual Editing

# Counterfactual
## 反事实改写

这个词很重要，但理解很简单。

意思是：

> **如果我只改一个关键条件，答案会不会改变？**

例如原句：

> “投标人须在本市设立服务机构。”

改成：

> “中标人须保证项目所在地现场服务能力。”

---

# 二十一、我们不是为了“改写得好看”

而是为了：

> 改一个决定判断的变量。

可以写成：

\[
x
\rightarrow
y
\]

如果改变一个关键条件：

\[
x'
\]

那么：

\[
y'
\]

也应该变化。

---

# 二十二、模型应该对真正重要的变化敏感

而对无关变化稳定。

例如：

```text
供应商
→ 投标人
```

如果语义不变，

Label：

> 不应该乱跳。

---

# 二十三、但如果：

```text
投标前必须已有本地机构
→
中标后自行保障现场服务
```

这种业务条件改变，

Label：

> 可能应该变化。

---

# 二十四、这就是一个非常专业的模型能力

# Invariance
## 对无关变化保持稳定

以及：

# Sensitivity
## 对关键变化保持敏感

一个好模型应该同时做到：

\[
\boxed{
对无关变化稳定
}
\]

\[
\boxed{
对关键条件敏感
}
\]

---

# 二十五、这也是为什么“成对数据”这么强

单独给模型：

> 一条 Risk。

模型不知道：

> 到底哪部分是决定性因素。

但如果同时有：

```text
案例A
Risk

案例B
No Risk
```

而两者只差一个关键条件，

模型更容易学习：

> 那个条件才是真正重要的。

---

# 二十六、从工程角度，我们可以给 Hard Case 保存哪些字段？

第一版不需要复杂。

一个 Hard Case 可以概念设计成：

```json
{
  "sample_id": "HC-000217",

  "case_type": "hard_negative",

  "source_sample_id": "CLAUSE-00918",

  "paired_sample_id": "HC-000218",

  "confusing_feature": "local_service_wording",

  "decision_factor": "pre_bid_local_entity_requirement",

  "risk_present": false,

  "needs_review": false,

  "difficulty": "hard",

  "annotation_status": "gold",

  "hardcase_version": "hardcase_v0.1"
}
```

---

# 二十七、这里最值得注意的是两个字段

```text
confusing_feature
```

表示：

> 为什么模型容易被骗？

例如：

```text
出现“本地”
```

---

另一个：

```text
decision_factor
```

表示：

> 真正决定答案的是什么？

例如：

```text
是否把投标前已有本地机构作为参与条件
```

这两个字段特别有研究价值。

---

# 二十八、Hard Case 不等于长文本

这是一个常见误解。

很多人觉得：

> 越复杂越难。

不一定。

最难的 Case 甚至可能只有一句话。

例如：

> “供应商须在本市设有服务机构。”

真正困难的不是文本长度。

而是：

> 缺了上下文。

所以：

\[
\boxed{
Difficulty
\neq
Length
}
\]

---

# 二十九、Hard Case 也不等于生僻案例

真正高价值的 Hard Case：

> 最好是业务中经常遇到，又容易混淆的。

如果一个案例：

```text
极其罕见
只出现一次
```

即使很难，

业务价值：

> 未必高。

所以 Hard Case 设计还要考虑：

# Frequency × Impact

即：

> 出现频率 × 出错影响。

---

# 三十、可以建立一个简单优先级

\[
Priority
=
Frequency
\times
ErrorRate
\times
BusinessImpact
\]

不需要把这个公式当成精确数学模型。

它只是提醒我们：

> **高频、模型常错、业务影响大的 Case，最值得优先建设。**

---

# 三十一、举例

假设：

| Case | 出现频率 | 模型错误率 | 业务影响 |
|---|---:|---:|---:|
| 本地服务要求 | 高 | 高 | 高 |
| 极少见附件格式 | 低 | 高 | 低 |
| 一般日期格式 | 高 | 低 | 低 |

很明显：

> 第一类最值得成为 Hard Case 建设重点。

---

# 三十二、Hard Case 在 Train 和 Test 中的角色不同

这点一定要分清。

Train 中的 Hard Case：

> 是用来教模型。

Test 中的 Hard Case：

> 是用来考模型。

所以绝不能：

```text
同一个Hard Case
→ Train

它的近似改写
→ Test
```

否则又回到第 7 阶段：

# Leakage

---

# 三十三、特别是 Counterfactual Pair

如果 A、B 是一组成对样本：

```text
A ↔ B
```

最好把它们视为：

# One Leakage Group

也就是说：

\[
\boxed{
Pair
应该整体进入同一个Split
}
\]

否则：

> 模型训练时看了 A，

考试时考 B，

成绩可能虚高。

---

# 三十四、Synthetic Hard Case 也必须继承父样本 Split

如果：

```text
Parent Sample
→ Train
```

它生成的 Counterfactual：

> 通常也留在 Train。

如果 Parent：

```text
Test
```

它生成的改写：

> 不得放入 Train。

第 6、7 阶段的：

# Lineage-aware Split

在这里继续生效。

---

# 三十五、是不是 Hard Case 越多越好？

也不是。

如果训练数据全部都是：

> 极端边界案例，

模型可能反而不知道：

> 正常世界是什么样。

所以我们需要：

# Difficulty Spectrum
## 难度光谱

```text
Easy
        ↓
Medium
        ↓
Hard
        ↓
Boundary
```

真正好的 Dataset：

> 应该覆盖整条光谱。

---

# 三十六、为什么？

Easy Case：

> 教基础模式。

Medium Case：

> 建立一般泛化。

Hard Case：

> 修决策边界。

Boundary Case：

> 学会不确定性和升级人工。

所以它们不是互相替代。

---

# 三十七、这个阶段最重要的一张图

```text
                      数据难度
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
        Easy           Hard         Boundary
          │              │              │
       学基本模式      学决策边界      学会不强答
          │              │              │
          └──────────────┼──────────────┘
                         ▼
               Professional Model
```

---

# 三十八、现在做一个更完整的采购案例

### Case A

> “投标人须在本市注册成立 3 年以上。”

可能：

```text
Potential Risk
Supplier Qualification
```

---

### Case B

> “中标供应商应为本项目提供 3 年运维服务。”

同样出现：

```text
3年
```

但显然：

> 不是注册年限。

这是：

# Hard Negative Pair

---

### Case C

> “投标人须具备不少于 3 个同类项目业绩。”

是否一定 Risk？

不能脱离：

```text
采购规模
项目复杂程度
业绩定义
时间范围
金额门槛
必要性
```

这是：

# Boundary Case

---

### Case D

没有写“指定品牌”。

但技术参数组合：

> 可能只覆盖极少数产品。

这是：

# Hard Positive

---

# 三十九、看出来了吗？

真正专业的数据集应该逼模型回答的不是：

> “有没有敏感词？”

而是：

```text
约束针对什么？
发生在什么阶段？
限制了谁？
是否有替代实现方式？
是否需要上下文？
关键事实是什么？
```

这才是业务推理。

---

# 四十、Hard Negative 为什么对 Precision 特别重要？

先回忆两个概念。

# Precision
## 查准率

模型报出来的风险中：

> 有多少真的是风险。

如果模型见到：

```text
本地
品牌
认证
业绩
```

就全部报警，

Recall 可能很高。

但 Precision：

> 会很差。

Hard Negative：

> 正是在教育模型“不要乱报警”。

---

# 四十一、Hard Positive 为什么对 Recall 重要？

# Recall
## 查全率 / 召回率

所有真正需要关注的风险里：

> 模型找出了多少。

如果模型只认识显眼关键词，

隐蔽风险：

> 就会漏掉。

Hard Positive：

> 在帮模型减少这种漏报。

---

# 四十二、所以可以简单记成

\[
\boxed{
HardNegative
\rightarrow
提高精确判断
}
\]

\[
\boxed{
HardPositive
\rightarrow
提高隐蔽风险发现能力
}
\]

当然实际指标不会这么单一，但作为心智模型很好用。

---

# 四十三、模型错了一条以后，怎么把它变成数据资产？

不要只修这一条。

应该问：

> **这属于哪一种错误模式？**

例如模型误报：

> “2 小时现场响应”。

不要只添加这一句。

应该建立一个：

```text
local_service_requirement
```

Hard Case Family。

---

# 四十四、什么叫 Case Family？

就是同一种判断机制的案例族。

例如：

```text
投标前本地机构
中标后服务能力
现场响应时间
远程响应
服务网点
驻场人员
临时派驻
固定办公场所
```

它们看起来有关联，

但专业含义：

> 不完全一样。

这组案例放在一起，

模型才真正学边界。

---

# 四十五、这比“补一条错题”强得多

可以写成：

\[
\boxed{
OneError
\rightarrow
ErrorPattern
\rightarrow
CaseFamily
}
\]

这就是专业的数据迭代。

---

# 四十六、这也决定了未来 Error Analysis 的方式

不要只统计：

```text
错了127条
```

而要统计：

```text
地域服务边界 37条
技术参数组合 26条
业绩条件 21条
评分年限 18条
上下文不足 15条
其他 10条
```

这样才能知道：

> 下一个 Dataset Version 应该补什么。

---

# 四十七、Hard Case 需要比普通样本更强的专家复核

为什么？

因为它本来就在边界附近。

如果 Hard Case 的 Label 本身错了：

> 会比普通错标伤害更大。

---

# 四十八、所以推荐

普通 Train 样本：

> 可以采用标准质量流程。

Hard Case / Benchmark：

> 更适合双标 + 裁决。

也就是：

```text
Hard Case
        ↓
Double Annotation
        ↓
Disagreement Check
        ↓
Adjudication
        ↓
Gold
```

第 9 阶段的流程：

> 在这里直接复用。

---

# 四十九、Hard Case 的 Rationale 也必须更精确

普通样本可能只写：

> “存在资格限制。”

Hard Pair 更应该明确：

```text
共同点是什么？
关键差异是什么？
为什么这个差异改变Label？
```

例如：

> 两个案例都涉及项目所在地，但本案例仅要求中标后的履约响应能力，并未要求供应商在投标前已设立本地机构，因此不能仅凭“项目所在地”一词直接归入地域准入风险。

这样的 Rationale：

> 对模型训练价值极高。

---

# 五十、它实际上在教模型“对比推理”

# Contrastive Reasoning
## 对比式推理

不是告诉模型：

> A 是什么。

而是告诉它：

> **为什么 A 和 B 不一样。**

这比孤立标签：

> 更接近专业学习。

---

# 五十一、以后做 SFT 时，可以直接派生成这种训练任务

```text
以下两个采购条款非常相似，
请指出决定其风险判断不同的关键条件。
```

然后输出：

```text
共同特征：
都涉及项目所在地服务。

关键差异：
A要求投标前已存在本地机构；
B只要求中标后的履约能力。

因此：
不能仅根据“本地/所在地”关键词做判断。
```

这会是非常有价值的专家 SFT 数据。

---

# 五十二、这说明 HardCaseSet 不只是分类数据

它还能派生：

```text
Classification
分类

SFT
专业解释

Evaluation
压力测试

Error Analysis
错误诊断
```

再次体现：

# Master Data → Multiple Views

---

# 五十三、现在定义 `HardCaseSet_V0.1`

第一版我们不用搞得很复杂。

可以包含：

```text
sample_id
source_sample_id
paired_sample_id
case_type
case_family
confusing_feature
decision_factor
risk_present
primary_risk_type
needs_review
difficulty
rationale
annotation_status
split
schema_version
```

其中真正关键的是：

```text
case_type
case_family
confusing_feature
decision_factor
paired_sample_id
```

因为这些字段：

> 让我们知道为什么它“难”。

---

# 五十四、建议的 Case Type

我们只保留五类就够：

```text
easy_positive
easy_negative
hard_positive
hard_negative
boundary_case
```

不要一开始做：

> 37 个 Difficulty Type。

仍然遵守：

# Minimal but Sufficient

---

# 五十五、如何判断某条是不是 Hard Case？

不是靠专家说：

> “我感觉挺难。”

更好的信号包括：

```text
专家经常分歧
模型经常预测错误
与另一类样本高度相似
需要多个上下文条件
容易触发关键词捷径
```

出现越多：

> 越值得进入 Hard Case Pool。

---

# 五十六、甚至可以保存一个简单的 Difficulty Score

例如不是人为拍脑袋 0.83，

而由几个信号组成：

\[
Difficulty
=
ExpertDisagreement
+
ModelError
+
SemanticConfusability
+
ContextDependency
\]

这里只是概念公式。

重点是：

> 难度应该有依据。

---

# 五十七、Hard Case 的比例应该是多少？

没有一个通用固定比例。

关键取决于：

```text
模型当前水平
任务复杂度
数据量
真实业务中的困难案例比例
Benchmark目的
```

但有一个原则非常重要：

> **不要让总分被大量 Easy Case 淹没。**

---

# 五十八、例如 Test 有 10,000 条

其中：

```text
9,800条 Easy
200条 Hard
```

模型：

```text
Easy = 99%
Hard = 40%
```

总 Accuracy 仍然非常漂亮。

但业务上：

> 可能完全不够用。

---

# 五十九、所以成熟 Benchmark 应该单独报告

```text
Overall
总成绩

Easy Slice
容易案例

Hard Negative Slice
高难负样本

Hard Positive Slice
隐蔽正样本

Boundary Slice
边界案例
```

这样：

> 模型的真实短板不会被平均数掩盖。

---

# 六十、这也是第 8 课 Benchmark 会做的事情

今天第 10 阶段只负责：

> **把这些高价值数据准备好。**

未来第 8 课：

> 再把它们正式做成 Slice Evaluation。

---

# 六十一、这一阶段最重要的反例

如果你发现模型一看到：

> “本地”

就报风险，

错误做法是：

> 在 Prompt 里写一句“不要看到本地就报风险”。

这可能暂时有效。

但更稳的办法是：

> 给模型大量经过专家确认的对比样本。

---

# 六十二、为什么？

Prompt 是：

> 口头提醒。

Hard Case Data 是：

> 反复训练出来的边界经验。

两者价值：

> 完全不同。

---

# 六十三、第二个反例

模型漏掉复杂技术参数风险。

错误做法：

> 继续收更多明显“指定品牌”的案例。

因为模型本来就会。

真正应该补的是：

> **没有品牌名、但限制组合高度异常的 Hard Positive。**

---

# 六十四、第三个反例

专家有分歧：

> 直接删除。

这样做会让 Dataset：

> 越来越简单。

最后模型的 Test：

> 看起来越来越高。

实际上你把真实世界最难的部分：

> 全删掉了。

---

# 六十五、第四个反例

人工生成一大批所谓 Hard Negative：

> 但从没让专家复核。

这很危险。

因为 Hard Case 本身：

> 就最容易标错。

所以“难例增强”不能变成：

# Synthetic Noise
## 合成噪声

---

# 六十六、第五个反例

把某个 Test Hard Case：

> 改几个词，

然后放回 Train。

这是典型：

# Benchmark Leakage

Stage 7 已经明确禁止。

---

# 六十七、现在把本阶段工程流程压成最终版

```text
AdjudicatedGoldSet_V0.1
        │
        ▼
收集真实错误
Model Errors
        │
        ├──────────────┐
        ▼              ▼
专家分歧         高频业务边界
        │              │
        └──────┬───────┘
               ▼
        建立Case Family
        按错误机制归类
               │
               ▼
      设计Contrastive Pair
          对比样本对
               │
        ┌──────┼───────┐
        ▼      ▼       ▼
     Hard+   Hard-   Boundary
        │      │       │
        └──────┼───────┘
               ▼
        专家双标与裁决
               │
               ▼
          Split / Leakage
               │
               ▼
        HardCaseSet_V0.1
```

中文只记：

> **找错误 → 找规律 → 做成对比 → 专家确认 → 防泄漏 → 进入难例库。**

---

# 六十八、本阶段再强化一次 5 个核心心智模型

如果这一阶段过一周以后只剩下五句话，我希望是：

> **Hard Negative 的价值，是让模型不能再靠关键词和表面模式取巧。**

> **真正高价值的数据经常不是一条样本，而是一对只差关键条件的对比样本。**

> **专家分歧和模型错误不是失败记录，而是 Hard Case 的主要矿藏。**

> **Boundary Case 不应该被强迫二选一，它可以训练模型学会“需要人工复核”。**

> **Hard Case 的训练集和测试集必须严格隔离，成对样本和派生样本都要继承同一个 Split。**

这五句话，就是第 10 阶段的骨架。

---

# 六十九、本阶段最终工程产物

我们今天真正得到的是：

# `HardCaseSet_V0.1`

它不只是：

> 一堆难题。

而是一个结构化的高价值数据资产：

```text
HardCaseSet_V0.1
│
├── Hard Positive
│   隐蔽风险
│
├── Hard Negative
│   看起来像风险但不是
│
├── Boundary Case
│   需要上下文或人工复核
│
└── Contrastive Pair
    只改变关键条件的对比样本
```

其中最关键的是：

> **每一条难例最好知道“模型为什么容易错，以及真正决定答案的条件是什么”。**

---

# 七十、本阶段掌握测试

现在不回看正文，你应该能解释：Hard Negative 为什么不是普通 No Risk；Hard Positive 与 Hard Negative 分别主要在解决什么问题；为什么政府采购模型特别容易产生关键词捷径；什么叫 Shortcut Learning；什么叫 Contrastive Pair；什么叫 Minimal Pair；为什么两个只差一个业务条件的案例比两个完全不相关案例更有训练价值；Boundary Case 为什么可以合法地标记 `uncertain / needs_review`；为什么专业模型必须学习什么时候不应该强答；Hard Case 为什么最好来自专家分歧和真实模型错误；什么叫 Error-driven Data Improvement；为什么一次模型错误应该进一步发展成一个 Case Family；什么是 Counterfactual Editing；模型为什么要对无关变化保持稳定、对关键条件保持敏感；为什么 Hard Case 不等于长文本，也不等于生僻案例；为什么 Hard Case 需要更强的专家复核；为什么 Contrastive Pair 不应该被拆到 Train 和 Test 两边；为什么 Synthetic Hard Case 必须继承父样本 Split；为什么 Benchmark 不能只报告 Overall Accuracy；以及为什么一个专业模型真正的能力，往往是在“两个看起来几乎一样的案例”之间体现。

如果这些都能讲清楚：

\[
\boxed{
第四课第10阶段真正掌握
}
\]

---

# 本阶段最终只记一句话

> **Hard Case 数据的价值，不是故意把题出难，而是围绕模型真实错误和专家真实分歧，构造“表面相似、关键条件不同”的对比案例，迫使模型放弃关键词捷径，真正学习政府采购判断的决策边界，并在证据不足时学会主动进入人工复核。**

最后只留一张图：

```text
             普通训练数据
                  │
                  ▼
               模型
                  │
                  ▼
              犯错误
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
      误报                 漏报
False Positive        False Negative
        │                   │
        ▼                   ▼
 Hard Negative        Hard Positive
        │                   │
        └─────────┬─────────┘
                  ▼
          Contrastive Pair
             对比样本
                  │
                  ▼
          Boundary Cases
             边界案例
                  │
                  ▼
          专家双标 + 裁决
                  │
                  ▼
          HardCaseSet_V0.1
                  │
                  ▼
         更可靠的决策边界
```

---

# 下一阶段：第四课 · 第 11 阶段
## Dataset Versioning、Lineage 与数据质量报告

第 10 阶段之后，我们已经有了：

```text
Raw Document
ParsedDocument
ClauseUnit
CleanClause
DedupedClauseSet
DatasetSplit
LeakageAudit
AnnotationSchema
AdjudicatedGoldSet
HardCaseSet
```

下一阶段不再继续“加工某一条数据”。

而要解决一个更工程化的问题：

> **半年以后，你还能不能准确说清楚 ProcurementDataset_V0.1 到底由哪些原始文件、哪一版解析器、哪一版清洗规则、哪一版 Label Schema、哪一批专家标注以及哪一个 Split 组成？**

第 11 阶段会把这整条链真正变成：

# 可版本化、可追溯、可审计的数据产品

最终会产出：

# `DatasetManifest_V0.1`
# `DatasetQualityReport_V0.1`

然后第 12 阶段，我们就能正式组装整个第四课最终工程产物：

# `ProcurementDataset_V0.1`

---

<!-- LESSON 04 STAGE 10 END -->


<!-- LESSON 04 STAGE 11 START -->

# 第四课 · 第 11 阶段
# Dataset Versioning、Lineage 与数据质量报告
## 数据集已经做完了，为什么半年以后却可能没人说得清“当时到底用的是哪一批数据”？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **一套冻结的数据状态。**
2. **数据 + 代码版本 + 配置版本。**
3. **final_dataset_v2_really_final/**
4. **包含哪些样本？ 样本内容是什么？ 用了什么Schema？ 怎么切的Train/Test？ 标签是哪一版？ 处理程序是哪一版？**
5. **Parser v1**
6. **Parser v2**
7. **Dedup threshold = 0.85**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Dataset` | 数据集：按统一 Schema、版本和质量标准组织的样本集合 |
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `ANN` | ANN/近似最近邻：在大规模向量中快速寻找相似项 |
| `Split` | 数据切分：按项目/时间/地区划分训练、验证、测试数据 |
| `Parser` | 解析器：把 PDF/Word/HTML 转换为结构化可处理内容 |
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `Validation` | 验证集：开发阶段用于选模型、调参数和早停 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Sample` | 样本：具有明确输入、目标和来源的一条训练/评测记录 |
| `Normalization` | 规范化：稳定中间激活与训练过程 |
| `Label Schema` | 标签结构：定义风险状态、类型、等级、证据等标注字段 |

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

第 10 阶段结束以后，我们已经拥有了一条相当完整的数据生产链：

```text
原始采购文件
      ↓
文档解析
      ↓
Clause结构恢复
      ↓
清洗与规范化
      ↓
去重
      ↓
Train / Validation / Test切分
      ↓
泄漏审计
      ↓
专家标注
      ↓
双人复核与裁决
      ↓
Hard Case建设
```

从“内容质量”看，我们已经做得很深了。

但现在换一个场景。

半年以后，你看到实验报告：

```text
ProcurementModel_V0.3
Test F1 = 0.87
```

你问团队：

> 这个模型到底是用哪一版数据训练的？

有人回答：

> “应该就是去年那批数据。”

再问：

> 那批数据用了哪一版 PDF 解析器？

不知道。

> 去重阈值是多少？

不知道。

> Test Set 后来有没有改？

好像改过。

> 专家标签是第一次标注，还是裁决后的 Gold？

不确定。

> 当时用的是 `AnnotationSchema_v0.1` 还是 `v0.2`？

没人记得。

这时候即使模型代码、权重全部还在：

> **这个实验实际上已经无法完整复现。**

所以第 11 阶段要解决的不是“怎样让一条数据更正确”。

而是：

# 怎样让整个 Dataset 成为一个可以被准确识别、完整追溯、重新生成、质量可证明的数据产品？

最终得到两个正式工程产物：

# `DatasetManifest_V0.1`

数据集清单 / 身份档案。

以及：

# `DatasetQualityReport_V0.1`

数据质量报告。

---

## 一、本阶段只解决一个核心问题

> **当别人问“ProcurementDataset_V0.1 到底是什么？”时，我们能不能不用靠人的记忆，而是用一套机器可读的版本、血缘和质量记录，把它完整回答出来？**

先看今天的总图。

```text
                 原始文件
                    │
                    ▼
             数据处理流水线
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
    Parser       Cleaning      Dedup
   解析版本       清洗版本      去重版本
       │            │            │
       └────────────┼────────────┘
                    ▼
                 Annotation
                 标注版本
                    │
                    ▼
                  Split
                 切分版本
                    │
                    ▼
              Dataset Snapshot
                数据集快照
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
 Dataset Manifest        Quality Report
 数据身份与血缘          数据质量证据
        │                       │
        └───────────┬───────────┘
                    ▼
          ProcurementDataset_V0.1
```

中文只记一句：

> **数据是谁 → 从哪里来 → 怎么变成现在这样 → 质量怎么样。**

---

# 二、第 11 阶段最重要的 5 个核心心智模型

这五个请直接当成本阶段骨架。

## 心智模型 1：Dataset Version 不是一个文件名，而是一个不可含糊的数据快照

\[
\boxed{
DatasetVersion
\neq
FolderName
}
\]

把文件夹改成：

```text
final_dataset_v2_really_final/
```

不叫版本管理。

真正的数据版本必须能够回答：

```text
包含哪些样本？
样本内容是什么？
用了什么Schema？
怎么切的Train/Test？
标签是哪一版？
处理程序是哪一版？
```

所以 Dataset Version 本质是：

> **一套冻结的数据状态。**

---

## 心智模型 2：可复现不等于“我还保存着 CSV”

\[
\boxed{
Reproducibility
=
Data
+
Code
+
Configuration
+
Versions
}
\]

数据文件还在，并不代表可以复现。

同一批 PDF：

```text
Parser v1
```

和：

```text
Parser v2
```

可能得到不同 Clause。

同一批 Clause：

```text
Dedup threshold = 0.85
```

和：

```text
0.93
```

也可能产生完全不同的 Dataset。

因此必须同时保存：

> 数据 + 代码版本 + 配置版本。

---

## 心智模型 3：Lineage 的核心不是“记录历史”，而是能够回答“这条数据从哪里来的”

# Lineage
## 数据血缘 / 来源链

一条 Gold Sample 最理想可以一路追到：

```text
Gold Label
    ↓
专家裁决
    ↓
双人初始标注
    ↓
Clean Clause
    ↓
原始 Clause
    ↓
Page / Block
    ↓
原始 PDF
```

所以：

\[
\boxed{
EveryDerivedRecord
ShouldHaveAParent
}
\]

任何派生数据：

> 最好都知道父对象是谁。

---

## 心智模型 4：Quality 不是一个“总分”，而是一组可解释的质量维度

一个 Dataset 可以：

```text
文本解析很好
```

但是：

```text
专家标签很差
```

也可以：

```text
标签很好
```

但是：

```text
Train/Test泄漏严重
```

所以不能只写：

```text
Dataset Quality = 92
```

而应该拆成：

```text
Parsing Quality
Structure Quality
Dedup Quality
Annotation Quality
Split Quality
Leakage Quality
Coverage Quality
```

也就是说：

\[
\boxed{
Quality
=
MultiDimensional
}
\]

---

## 心智模型 5：Dataset 发布不是“导出文件”，而是通过一组 Release Gate

# Release Gate
## 发布质量门槛

真正专业的数据产品不能：

> “处理完了就发版。”

而应该先问：

```text
有没有Critical Leakage？
Gold样本有没有未裁决分歧？
Schema Validation有没有失败？
Train/Test有没有重复？
关键Risk Type有没有严重缺失？
Manifest是否完整？
```

全部达到要求后：

> 才发布新版本。

因此：

\[
\boxed{
DatasetRelease
=
Snapshot
+
Lineage
+
QualityEvidence
+
ReleaseDecision
}
\]

---

# 三、先彻底理解：什么叫 Dataset Snapshot？

# Snapshot
## 数据快照

意思是：

> 在某个确定时点，把数据的完整状态冻结下来。

例如：

```text
ProcurementDataset_V0.1
```

发布以后，它的核心内容不应该今天是：

```text
400,213条
```

明天偷偷变成：

```text
402,718条
```

但名字还是：

```text
V0.1
```

这会直接破坏实验可复现性。

---

## 一个非常重要的规则

> **同一个 Version 的内容，不应该悄悄变化。**

如果数据发生实质性改变：

```text
新增样本
删除错误样本
重新标注
修改Train/Test
修复解析
更新Label Schema
```

就应该：

> 创建新版本。

例如：

```text
V0.1
↓
V0.2
```

而不是覆盖旧版。

这叫：

# Immutable Snapshot
## 不可变快照

---

# 四、Dataset Version 和其他 Version 一定要分开

这是实际项目里特别容易混乱的地方。

你可能同时拥有：

| Version | 中文 | 它控制什么 |
|---|---|---|
| `dataset_version` | 数据集版本 | 整个最终数据快照 |
| `parser_version` | 解析器版本 | PDF/DOCX如何解析 |
| `normalization_version` | 清洗规则版本 | 文本怎样规范化 |
| `dedup_version` | 去重版本 | 重复数据如何识别 |
| `schema_version` | 数据结构版本 | 字段定义 |
| `annotation_schema_version` | 标注结构版本 | 专家标什么 |
| `guideline_version` | 标注指南版本 | 专家怎么判断 |
| `split_version` | 数据切分版本 | Train/Val/Test怎么分 |
| `leakage_audit_version` | 泄漏审计版本 | 用什么规则检查泄漏 |

注意：

> **它们不是同一个版本号。**

---

## 为什么不能只保存 `dataset_v0.1`？

因为当模型出现问题时，我们需要定位：

到底是：

```text
Dataset整体变化？
Parser变化？
Label定义变化？
Split变化？
```

如果所有东西只有：

```text
version = 1
```

基本无法 Debug。

---

# 五、政府采购项目里的一个真实感很强的版本问题

假设：

```text
ProcurementDataset_V0.1
```

使用：

```text
Parser_v1.3
```

后来我们发现 PDF 表格恢复存在问题：

评分表：

```text
项目经验 | 5分
技术方案 | 20分
售后服务 | 10分
```

被错误解析成：

```text
项目经验
5分技术方案
20分售后服务
10分
```

于是修复 Parser：

```text
Parser_v1.4
```

重新解析以后：

> Clause 内容发生变化。

那么即使原始 PDF 完全没变：

# Dataset 已经变了。

因此应该生成：

```text
ProcurementDataset_V0.2
```

或者至少：

> 新的数据快照。

这说明：

\[
\boxed{
RawDataUnchanged
\neq
DatasetUnchanged
}
\]

---

# 六、现在进入 Lineage：一条数据到底怎样追到原文？

假设模型在 Test 中错了一条：

```text
CLAUSE-009817
```

内容是：

> “供应商须在本市设立固定服务机构。”

我们不应该只能看到这一个字符串。

理想系统应该能一路追：

```text
CLAUSE-009817
       ↓
CleanClause-009817
       ↓
Parsed Block B-77218
       ↓
Page 37
       ↓
Document DOC-00152
       ↓
Project PROJECT-00152
       ↓
raw file hash
       ↓
原始采购PDF
```

同时 Label 另一条路径：

```text
Gold Label
    ↓
Adjudication-771
    ↓
Expert A Annotation
Expert B Annotation
    ↓
AnnotationGuideline_v0.1
```

这两条路径合起来：

> 才形成真正完整的数据血缘。

---

# 七、可以把 Lineage 想成“食品追溯码”

超市里一盒食品出问题。

真正专业的供应链不是只知道：

> “这是牛奶。”

而是知道：

```text
哪家牧场
哪批原料
哪条生产线
哪天生产
哪个包装批次
```

Dataset 也是一样。

如果模型出了问题：

> 不能只知道“这是训练数据之一”。

最好能追到：

> **它到底是怎样产生的。**

---

# 八、Lineage 为什么不仅仅为了审计？

它至少解决三个核心工程问题。

首先是：

# Debug
## 故障定位

模型回答错：

> 是模型错？

还是：

```text
OCR错
Clause切错
Clean错
Label错
```

没有 Lineage：

> 很难知道。

---

其次是：

# Impact Analysis
## 影响分析

假设发现：

```text
Parser_v1.2
```

有 Bug。

我们应该能够问：

> 哪些 Dataset Sample 是由 Parser_v1.2 生成的？

然后精准重处理。

而不是：

> 整个数据集全部推倒重来。

---

第三是：

# Rebuild
## 重建

如果 Dataset 文件损坏，

只要：

```text
Raw Data
Code
Configuration
Lineage
```

还在，

理论上应该能够：

> 重新构建。

---

# 九、Hash 在这里有什么用？

# Hash
## 内容指纹

例如一个 PDF 可以计算：

```text
SHA256
```

得到类似：

```text
8f1c...
```

只要文件内容改变一个字节：

> Hash 通常也会变化。

所以 Hash 可以回答：

> **这是不是完全相同的那一个文件？**

---

## Dataset 也可以有 Hash

例如最终：

```text
train.jsonl
validation.jsonl
test.jsonl
```

都保存：

```text
sha256
```

这样别人拿到文件以后：

> 可以验证有没有被改。

---

## 但一定记住

\[
\boxed{
Hash
证明内容一致
\neq
证明数据正确
}
\]

一份错误 Dataset：

> 一样可以有非常完美的 SHA256。

Hash 是：

> 身份和完整性工具。

不是：

> 质量工具。

---

# 十、什么是 Dataset Manifest？

# Manifest
## 数据集清单 / 数据身份档案

可以把它理解成：

> **Dataset 的身份证 + 配方表。**

一个最小版 `DatasetManifest_V0.1` 可以长这样：

```json
{
  "dataset_name": "ProcurementDataset",
  "dataset_version": "0.1",

  "created_at": "2026-09-15",

  "source_snapshot": "raw_procurement_2026_09",

  "pipeline": {
    "parser_version": "parser_v0.3",
    "structure_version": "structure_v0.2",
    "normalization_version": "normalize_v0.2",
    "dedup_version": "dedup_v0.1"
  },

  "annotation": {
    "schema_version": "annotation_schema_v0.1",
    "guideline_version": "annotation_guideline_v0.1"
  },

  "split": {
    "split_version": "procurement_split_v0.1"
  },

  "audit": {
    "leakage_audit_version": "leakage_audit_v0.1"
  },

  "counts": {
    "projects": 10000,
    "documents": 18214,
    "clauses": 412806
  }
}
```

数字只是教学示例。

重点不是字段名称一模一样。

重点是：

> **你必须能够精确描述 Dataset 是怎样生成的。**

---

# 十一、Manifest 里最值得保存的不是“漂亮描述”，而是机器可验证的信息

例如：

```text
版本
Hash
样本数量
Split数量
Schema版本
Pipeline版本
来源快照
```

这些都是：

> 机器可以检查的。

相反：

```text
“本数据集质量较高”
```

这种文字：

> 几乎没有工程价值。

---

# 十二、Manifest 最好再保存文件清单

例如：

```json
{
  "artifacts": [
    {
      "name": "train.jsonl",
      "rows": 320000,
      "sha256": "..."
    },
    {
      "name": "validation.jsonl",
      "rows": 41000,
      "sha256": "..."
    },
    {
      "name": "test.jsonl",
      "rows": 51806,
      "sha256": "..."
    }
  ]
}
```

这样能够同时回答：

```text
文件是什么？
有多少条？
有没有被修改？
```

---

# 十三、现在进入第二个最终产物：Dataset Quality Report

# Dataset Quality Report
## 数据质量报告

Manifest 回答的是：

> “这是谁？”

Quality Report 回答的是：

> **“它到底好不好？”**

这两个一定要分开。

---

# 十四、数据质量至少看 6 个维度

为了保持这一阶段精简，我们只保留六个真正核心维度：

| 质量维度 | 核心问题 |
|---|---|
| **Integrity 完整性** | 必填字段是否缺失？文件是否完整？ |
| **Validity 合法性** | 数据是否符合 Schema 与业务逻辑？ |
| **Uniqueness 独立性** | 是否还有大量重复/近重复？ |
| **Annotation Quality 标注质量** | 专家一致性、Gold比例怎样？ |
| **Leakage Safety 泄漏安全性** | Train/Test 是否存在信息泄漏？ |
| **Coverage 覆盖性** | 关键风险类型、难例、项目类型是否覆盖？ |

这六个先够用了。

---

# 十五、Integrity：完整性

例如统计：

```text
clause_text缺失率
project_id缺失率
source_page缺失率
risk_present缺失率
```

可以定义一个简单的字段完整率：

\[
Completeness
=
1-
\frac{MissingRequiredFields}
{TotalRequiredFields}
\]

例如：

```text
Required Cells = 1,000,000
Missing = 500
```

则：

\[
Completeness=99.95\%
\]

但注意：

> **字段不为空，不代表内容正确。**

---

# 十六、Validity：业务合法性

例如：

```text
risk_present = false
risk_level = high
```

这可能违反 Annotation Contract。

又比如：

```text
annotation_status = gold
```

但没有：

```text
reviewer_id
```

如果我们的 Gold 规则要求双人复核：

> 这就是 Invalid Record。

所以需要统计：

```text
schema_validation_failure_count
cross_field_validation_failure_count
```

---

# 十七、Uniqueness：独立性

这里不是要求：

> 所有文字必须不同。

而是检查：

```text
Exact Duplicate
Near Duplicate
Template Concentration
```

例如 Dataset 有：

```text
400,000条Clause
```

但是：

```text
180,000条
```

来自十个高度重复模板。

那实际信息多样性：

> 比 Row Count 看起来低很多。

所以第 5 阶段的 Dedup 结果：

> 应该进入 Quality Report。

---

# 十八、Annotation Quality：标注质量

第 9 阶段的成果开始进入正式质量报告。

例如：

```text
double_annotation_rate
direct_agreement_rate
Cohen's Kappa
adjudication_rate
gold_sample_rate
```

假设：

```text
risk_present agreement = 92%
risk_type agreement = 89%
risk_level agreement = 63%
```

Quality Report 不应该只写：

> “总体一致率很好。”

而要明确：

> `risk_level` 仍是弱项。

---

# 十九、Leakage Safety：泄漏安全性

这里直接复用第 7 阶段。

例如：

```text
Project overlap = 0
Exact duplicate overlap = 0
Confirmed lineage leakage = 0
Temporal violation = 0
```

以及：

```text
Near duplicate suspects = 17
```

如果仍然有未解决的 Critical Leakage：

> Dataset 不应该进入正式 Benchmark 发布。

---

# 二十、Coverage：覆盖性

这是最容易被“数据量很大”掩盖的问题。

假设：

```text
总样本 = 500,000
```

很大。

但 Risk Type：

```text
A 供应商资格 = 420,000
B 技术参数     = 60,000
C 商务要求     = 18,000
D 评分规则     = 1,900
E 采购需求     = 100
```

那么：

> E 类模型基本没多少可学。

---

## 所以 Coverage 要看

不仅看：

```text
Total Rows
```

还要看：

```text
Risk Type
Subtype
Region
Year
Project Category
Difficulty
Hard Positive
Hard Negative
Boundary Case
```

这就是：

# Slice Coverage
## 分切片覆盖率

---

# 二十一、尤其要检查 Hard Case Coverage

第 10 阶段刚刚建立：

```text
easy_positive
easy_negative
hard_positive
hard_negative
boundary_case
```

到了 Quality Report 中应该统计：

```text
每类有多少？
Train多少？
Validation多少？
Test多少？
```

否则可能出现：

> Hard Case 全在 Train，Test 几乎没有。

那 Benchmark：

> 仍然太简单。

---

# 二十二、数据质量报告不能只有“比例”，还需要阈值

比如我们决定第一版发布门槛：

```text
Critical Leakage
=
0
```

这是硬门槛。

再例如：

```text
Required Field Completeness
>=
99.9%
```

只是教学示例。

这些阈值：

> 应根据项目实际确定。

---

# 二十三、所以 Quality Report 最后最好有一个：

# Release Decision
## 发布决定

例如：

```text
PASS
```

或者：

```text
PASS WITH KNOWN LIMITATIONS
```

或者：

```text
FAIL
```

这比：

> “总体质量不错”

专业很多。

---

# 二十四、什么是 Known Limitation？

# Known Limitation
## 已知限制

真正专业的数据产品：

> 不会假装自己没有缺陷。

例如：

```text
D类评分规则Hard Positive样本不足

2024年前部分PDF OCR质量较低

部分地区数据覆盖不足

risk_level专家一致性仍偏低
```

这些都可以明确写进：

# Known Limitations

这不是丢脸。

恰恰说明：

> **我们知道 Dataset 能支持什么结论，也知道不能支持什么结论。**

---

# 二十五、可以把 Dataset Quality Report 想成“体检报告”

体检报告不会只写：

> “身体质量 87 分。”

而会分别告诉：

```text
血压
血脂
血糖
肝功能
```

Dataset 也一样。

你需要知道：

> 到底哪里健康，哪里需要修。

---

# 二十六、现在把 Manifest 和 Quality Report 放在一起

```text
DatasetManifest
=
身份

DatasetQualityReport
=
体检
```

这是今天最简单也最重要的类比。

---

# 二十七、版本变化时，最好还保存 Change Log

# Change Log
## 版本变更记录

假设：

```text
V0.1 → V0.2
```

应该明确写：

```text
新增12,000个项目
修复表格解析Bug
Annotation Guideline升级v0.2
重新裁决1,217条样本
新增3,400条Hard Negative
Test Set保持冻结
```

这样大家立刻知道：

> 为什么 V0.2 和 V0.1 不一样。

---

# 二十八、尤其要记录 Test 有没有变化

这是非常重要的。

如果：

```text
Model A
在Dataset v0.1 Test上
= 86%
```

而：

```text
Model B
在Dataset v0.2 Test上
= 90%
```

如果 Test 已经变化：

> 两个数字不能直接说 B 提升 4%。

所以 Change Log 必须说明：

```text
test_split_changed = true / false
```

---

# 二十九、这就是 Versioning 和 Benchmark 公平性的关系

\[
\boxed{
ComparableModelScores
需要
ComparableBenchmark
}
\]

如果考试卷都变了：

> 分数变化就不能简单归因于模型。

---

# 三十、推荐建立两个不同概念

# Dataset Version
整个训练数据产品版本。

和：

# Benchmark Version
测试基准版本。

例如：

```text
ProcurementDataset_v0.4

ProcurementBench_v1.0
```

Dataset 可以持续新增 Train 数据。

Benchmark：

> 可以长期冻结。

这样模型迭代才有可比性。

---

# 三十一、这为第 8 课埋下了非常重要的基础

第 8 课我们会正式建设：

# `ProcurementBench_V1`

现在第 11 阶段只需要记住：

> **Dataset 可以成长，Benchmark 不应该随便漂移。**

---

# 三十二、再看一个非常现实的问题：发现错误样本怎么办？

假设发布：

```text
Dataset_V0.1
```

以后发现一条 Gold Label 明显标错。

能不能直接修改 V0.1 文件？

不建议。

---

## 更稳的处理方式

保留：

```text
V0.1
```

作为历史快照。

然后：

```text
Issue:
GOLD-00128 label incorrect
```

在：

```text
V0.2
```

中修复。

这样以前训练的模型：

> 仍然可以准确知道当时用的是什么数据。

---

# 三十三、这和软件版本控制非常像

软件 Bug 修复以后：

> 不会假装旧版本从来没有 Bug。

会有：

```text
v1.0
v1.1
```

Dataset 也应该如此。

所以：

# Dataset is Software-like

它不是一堆静态文件。

而是：

> **有版本、有依赖、有测试、有发布、有缺陷修复的数据产品。**

---

# 三十四、一个非常重要的专业思想：Data Contract

# Data Contract
## 数据契约

到第 11 阶段，我们已经有很多规则：

```text
Schema
Label Schema
Split Policy
Leakage Policy
Gold Policy
```

这些可以共同形成：

> Dataset 必须遵守的数据契约。

例如：

```text
Gold Sample必须有source provenance

Test Sample不能与Train共享project_id

uncertain必须配needs_review

Synthetic Sample必须记录parent_sample_id
```

如果违反：

> Pipeline 应该自动报警。

---

# 三十五、Data Quality 最好尽量自动化

每次准备发布新 Dataset：

自动运行：

```text
Schema Check
      ↓
Missing Value Check
      ↓
Duplicate Check
      ↓
Split Integrity Check
      ↓
Leakage Check
      ↓
Label Logic Check
      ↓
Distribution Report
      ↓
Hard Case Coverage
      ↓
Generate Quality Report
```

这就像软件里的：

# CI
## Continuous Integration / 持续集成

但我们这里可以理解成：

> **每次发数据版本之前自动体检。**

---

# 三十六、所以高质量 Dataset Pipeline 不应该靠“人记得检查”

而应该：

\[
\boxed{
ImportantCheck
\rightarrow
AutomatedCheck
}
\]

能自动化的：

> 尽量自动化。

不能自动判断的：

> 明确进入人工 Review。

---

# 三十七、什么必须人工？

例如：

```text
专家判断是否合理
Hard Case是否真的成立
法规证据是否适用
某个Boundary Case的裁决
```

这些：

> 不能因为追求自动化而假装机器已经解决。

---

# 三十八、所以最终质量控制应该是

\[
\boxed{
AutomatedValidation
+
ExpertReview
}
\]

这和第 7 阶段的：

```text
Automation + Governance
```

其实是一脉相承的。

---

# 三十九、现在设计第一版 `DatasetQualityReport_V0.1`

概念上可以有：

```text
Dataset Identity
数据集身份

Volume
数据规模

Integrity
完整性

Schema Validity
结构合法性

Dedup Statistics
去重统计

Split Statistics
切分统计

Leakage Audit
泄漏审计

Annotation Quality
标注质量

Hard Case Coverage
难例覆盖

Known Limitations
已知限制

Release Decision
发布结论
```

不需要写成 100 页。

核心是：

> 能支持工程决策。

---

# 四十、例如一份极简报告可以是

```text
ProcurementDataset_V0.1

Projects:
10,000

Clauses:
412,806

Required Field Completeness:
99.97%

Cross-field Validation Failures:
0

Train/Test Project Overlap:
0

Exact Duplicate Cross-split:
0

risk_present Expert Agreement:
92%

Hard Negative:
8,214

Hard Positive:
3,127

Boundary Cases:
2,806

Critical Leakage:
0

Known Limitation:
Scoring-rule hard positives underrepresented

Release Decision:
PASS WITH KNOWN LIMITATIONS
```

这已经比一句：

> “数据质量很好。”

强太多。

---

# 四十一、现在看一个典型反例

团队把 Dataset 发到服务器：

```text
dataset_new/
```

一个月后：

```text
dataset_new2/
```

后来：

```text
dataset_final/
```

再后来：

```text
dataset_final_fix/
```

最后：

```text
dataset_final_fix_0822_new/
```

看到这种文件名：

> 基本可以确定版本治理已经失控。

---

# 四十二、另一个反例

每次训练前：

> 临时重新 Random Split。

结果每个模型：

> 都考不同的 Test。

即使 Dataset 文件相同：

> Benchmark 版本也不同。

所以：

```text
split_version
```

必须正式进入 Manifest。

---

# 四十三、另一个反例

团队记录：

```text
Data Version = 3
```

却没有说明：

> Version 2 到 Version 3 到底改了什么。

那么版本号：

> 几乎只是装饰。

所以 Version 必须配：

# Change Log

---

# 四十四、再一个反例

Quality Report 只有：

```text
Total Samples = 2,000,000
```

这不是质量指标。

它只是：

# Quantity
## 数量

千万不要把：

\[
\boxed{
Quantity
}
\]

误当成：

\[
\boxed{
Quality
}
\]

200 万条高度重复、标签混乱的数据：

> 可能远不如 20 万条高质量数据。

---

# 四十五、第 11 阶段真正的专业化升级

前十个阶段主要解决：

> **怎样把数据做好。**

第 11 阶段第一次开始解决：

> **怎样证明它做得好，并且以后还能知道当时是怎么做的。**

这是两个完全不同的成熟度层级。

可以写成：

\[
\boxed{
GoodData
\neq
ManagedDataProduct
}
\]

---

# 四十六、真正的数据产品应该同时具备

```text
Identity
我是谁

Version
我是第几版

Provenance
我从哪里来

Reproducibility
我能不能重建

Quality Evidence
我凭什么说自己质量合格

Known Limitations
我有什么明确缺陷
```

这六个词基本就是：

> Dataset Governance 的核心。

---

# 四十七、把今天所有东西压缩成一个最终公式

\[
\boxed{
TrustedDataset
=
FrozenSnapshot
+
VersionedPipeline
+
TraceableLineage
+
QualityReport
+
ReleaseGate
}
\]

中文就是：

> **可信 Dataset = 冻结的数据快照 + 明确版本的处理流程 + 可追溯的数据血缘 + 可解释的质量报告 + 发布门槛。**

---

# 四十八、本阶段最后再强化一次 5 个核心心智模型

如果过一周以后，第 11 阶段你只记得五句话，我希望是：

> **Dataset Version 不是文件夹名字，而是一个不能悄悄变化的数据快照。**

> **可复现不是保存 CSV，而是保存数据、代码、配置和所有关键版本。**

> **任何派生数据最好都能沿着 Lineage 一路追到原始文件和专家判断。**

> **Dataset Quality 不是一个总分，而是完整性、合法性、独立性、标注质量、泄漏安全和覆盖性的组合。**

> **发布 Dataset 不是导出文件，而是通过一套 Release Gate 后正式冻结并记录。**

这五句，就是第 11 阶段的骨架。

---

# 四十九、本阶段两个最终工程产物

第一个：

# `DatasetManifest_V0.1`

它回答：

```text
这是什么数据集？
哪一版？
包含什么？
用了什么处理版本？
用了什么Annotation Schema？
用了什么Split？
文件Hash是什么？
```

第二个：

# `DatasetQualityReport_V0.1`

它回答：

```text
数据完整吗？
Schema合法吗？
重复控制怎么样？
专家标注可靠吗？
Train/Test泄漏了吗？
Hard Case够不够？
哪些地方仍然不足？
是否允许发布？
```

两者合起来：

```text
Manifest
=
“我是谁”

Quality Report
=
“我怎么样”
```

这就是今天最简单的记忆方式。

---

# 五十、本阶段掌握测试

现在不回看正文，你应该能够解释：为什么 Dataset Version 不能只是一个文件夹名字；什么叫 Immutable Snapshot（不可变快照）；为什么 Raw File 没变化，Dataset 仍然可能因为 Parser 更新而变化；Dataset Version、Parser Version、Schema Version、Split Version 为什么必须分开；什么叫 Data Lineage（数据血缘）；为什么 Gold Label 最好能够一路追到原始 PDF；Lineage 为什么同时服务 Debug、影响分析和重建；Hash 能证明什么、不能证明什么；Dataset Manifest 的核心作用是什么；Manifest 和 Quality Report 有什么区别；为什么 Dataset Quality 必须是多维度的；Integrity、Validity、Uniqueness、Annotation Quality、Leakage Safety、Coverage 分别在检查什么；为什么总样本数不能代表质量；为什么 Hard Case Coverage 必须进入质量报告；什么叫 Release Gate；为什么 Critical Leakage 通常应该成为发布阻断条件；什么叫 Known Limitation；为什么 Dataset 可以持续增长，但 Benchmark 不应该随便改变；为什么发现旧版错误时不应该悄悄覆盖历史数据；为什么数据工程越来越像软件工程；什么叫 Data Contract；为什么重要的数据质量检查应该尽量自动化；以及为什么最终发布的数据产品必须同时具备版本、血缘、质量证据和发布记录。

如果这些都能自己讲清楚：

\[
\boxed{
第四课第11阶段真正掌握
}
\]

---

# 本阶段最终只记一句话

> **真正专业的数据集不是一个 `train.jsonl` 文件，而是一个有明确身份、有冻结版本、有完整血缘、有可复现处理流程、有质量证据、有已知限制、并经过正式发布门槛的数据产品；只有做到这一点，模型半年以后取得的每一个分数才仍然能够被解释、复现和审计。**

最后只留这张图：

```text
              Raw Procurement Files
                     原始采购文件
                          │
                          ▼
                  Versioned Pipeline
                  有版本的数据流水线
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
       Parser          Cleaning         Dedup
        解析              清洗             去重
          │               │               │
          └───────────────┼───────────────┘
                          ▼
                     Annotation
                       专家标注
                          │
                          ▼
                    Split / Audit
                    切分与泄漏审计
                          │
                          ▼
                   Frozen Snapshot
                     冻结数据快照
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
   DatasetManifest_V0.1       DatasetQualityReport_V0.1
       身份与血缘                     质量证据
            │                           │
            └─────────────┬─────────────┘
                          ▼
                 Release Gate
                   发布质量门槛
                          │
                          ▼
               ProcurementDataset
                  可信数据产品
```

---

# 下一阶段：第四课 · 第 12 阶段
# 正式组装 `ProcurementDataset_V0.1`

第 12 阶段是第四课最后一个阶段。

它不再新增一个孤立的数据概念，而是把前 11 阶段真正合并成一套**可以交给第五课 SFT + LoRA/QLoRA 使用的数据产品**：

```text
Task Schema
+
ParsedDocument
+
ClauseUnit
+
CleanClause
+
Dedup
+
Train/Val/Test
+
Leakage Audit
+
Annotation Schema
+
Adjudicated Gold
+
Hard Case
+
Manifest / Quality Report
        ↓
ProcurementDataset_V0.1
```

第 12 阶段最重要的问题会变成：

> **一个真正可以交付的政府采购训练数据集，目录到底长什么样？Train、Validation、Test、Gold、Hard Case、Manifest、Schema、Quality Report 应该怎样组织？哪些文件第五课真正拿去训练，哪些绝对不能喂给模型？**

最后我们会得到第四课真正的工程交付物：

# `ProcurementDataset_V0.1`

到这里，第四课就从“讲数据工程”正式结束为：

> **做出第一版政府采购 AI 数据资产。**

---

<!-- LESSON 04 STAGE 11 END -->


<!-- LESSON 04 STAGE 12 START -->

# 第四课 · 第 12 阶段
# 正式组装 `ProcurementDataset_V0.1`
## 前 11 个阶段学了这么多东西，最后到底怎样变成一套真的可以交给模型训练的数据产品？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **只是 Dataset 派生出来的一种使用方式。**
2. **我已经有 train.jsonl 所以我已经有 Dataset**
3. **Master Data 主数据**
4. **Task Views 训练 / 评测视图**
5. **Governance Assets 治理与审计资产**
6. **第一，Dataset 不是一个训练文件，而是 Master Data、Task View 和 Governance Asset 的组合。**
7. **第二，Master Data 是完整真相源，训练数据只是从它派生出来的任务视图。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Dataset` | 数据集：按统一 Schema、版本和质量标准组织的样本集合 |
| `Split` | 数据切分：按项目/时间/地区划分训练、验证、测试数据 |
| `Sample` | 样本：具有明确输入、目标和来源的一条训练/评测记录 |
| `ANN` | ANN/近似最近邻：在大规模向量中快速寻找相似项 |
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |
| `Input` | 输入：模型在当前任务中允许看到的条件信息 |
| `Validation` | 验证集：开发阶段用于选模型、调参数和早停 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `SFT` | 监督微调：用监督样本继续更新模型参数 |
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `LoRA` | LoRA：冻结大部分基座参数，只训练低秩增量矩阵 |

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

这是第四课最后一个阶段。

前 11 个阶段，我们一直在解决局部问题：

```text
Stage 1   什么是一条数据？
Stage 2   原始文件怎么可信解析？
Stage 3   怎样恢复章—节—条款结构？
Stage 4   怎样安全清洗文本？
Stage 5   怎样去掉重复信息？
Stage 6   Train / Validation / Test 怎么切？
Stage 7   怎样防止数据泄漏？
Stage 8   专家到底标什么？
Stage 9   怎样得到可信 Gold Label？
Stage 10  怎样建设 Hard Case？
Stage 11  怎样版本化、追溯和证明质量？
```

到了今天，我们不再新增一个孤立概念。

而是要把所有东西真正装起来。

最终交付物只有一个：

# `ProcurementDataset_V0.1`

它将成为第五课：

# SFT + LoRA / QLoRA 微调

真正开始训练政府采购模型之前的**数据底座**。

---

# 一、本阶段只解决一个核心问题

> **怎样把原始采购文件、结构化 Clause、专家标签、Hard Case、Train/Validation/Test、数据血缘、质量报告等所有资产，组织成一个既能训练、又能评测、还能审计和复现的正式 Dataset？**

先看第四课最终总图。

```text
                    原始政府采购文件
                            │
                            ▼
                     ParsedDocument
                       可信文档解析
                            │
                            ▼
                       ClauseUnit
                      条款结构恢复
                            │
                            ▼
                       CleanClause
                      安全规范化文本
                            │
                            ▼
                    DedupedClauseSet
                       独立信息集合
                            │
                            ▼
                 Group-aware Dataset Split
                  按项目/血缘安全切分
                            │
                            ▼
                       Leakage Audit
                        数据泄漏审计
                            │
                            ▼
                    Expert Annotation
                         专家标注
                            │
                            ▼
                 Double Review + Adjudication
                       双标复核与裁决
                            │
                            ▼
                       HardCaseSet
                        高价值难例
                            │
                            ▼
                  Version + Lineage + QA
                    版本、血缘、质检
                            │
                            ▼
              ┌───────────────────────────┐
              │ ProcurementDataset_V0.1  │
              │ 政府采购AI第一版数据资产 │
              └───────────────────────────┘
                         │        │
                         ▼        ▼
                     Training   Evaluation
                       训练        评测
```

中文只记：

> **原始文件 → 可信 Clause → 专家判断 → 安全切分 → 任务视图 → 正式发布。**

---

# 二、本阶段最重要的 5 个核心心智模型

这次先把最重要的东西说透。

---

## 心智模型 1：Dataset ≠ `train.jsonl`

这是第四课最后必须纠正的一个误区。

很多人认为：

```text
我已经有 train.jsonl
所以我已经有 Dataset
```

不对。

真正的 `ProcurementDataset_V0.1` 至少同时包含三层东西：

```text
Master Data
主数据

Task Views
训练 / 评测视图

Governance Assets
治理与审计资产
```

所以：

\[
\boxed{
Dataset
\neq
TrainingFile
}
\]

而是：

\[
\boxed{
Dataset
=
MasterData
+
TaskViews
+
Governance
}
\]

其中 `train.jsonl`：

> 只是 Dataset 派生出来的一种使用方式。

---

## 心智模型 2：Master Data 是“真相源”，训练文件只是“投影视图”

# Master Data
## 主数据 / Single Source of Truth

我们前面保存了很多信息：

```text
raw_text
normalized_text
section_path
project_id
source_page
risk_present
risk_type
rationale
evidence
annotation_status
split
lineage
```

这些信息不能因为某个模型不需要：

> 就直接删掉。

真正正确的关系是：

```text
                 Master Dataset
                 完整主数据
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
 Classification     SFT View     Evaluation
    分类视图          微调视图       评测视图
```

也就是我们这一课反复出现的：

\[
\boxed{
RichMasterData
\rightarrow
TaskSpecificViews
}
\]

不要反过来：

> 用第一版模型需要什么，决定整个数据库永远只能保存什么。

---

## 心智模型 3：数据“存在” ≠ 数据“允许喂给模型”

这是整个 Dataset 组装里最重要的安全原则之一。

Master Data 里面可能存在：

```text
gold_label
gold_rationale
adjudication_comment
future_outcome
reviewer_note
benchmark_slice
```

这些字段：

> 为了治理、评测、审计，非常有价值。

但它们绝不能因此：

> 自动成为模型 Input。

所以必须建立：

# Input Firewall
## 模型输入防火墙

可以写成：

\[
\boxed{
StoredField
\neq
AllowedModelInput
}
\]

这句话特别重要。

---

## 心智模型 4：Split 是样本血缘属性，不是文件夹属性

很多人会这样理解：

```text
把一些JSON放进train文件夹
→ 它就是Train
```

这太脆弱。

真正应该保存的是：

```text
sample_id → split
project_id → split
lineage_group → split
```

也就是说：

> **一个样本属于 Train / Validation / Test，是数据身份的一部分。**

不是复制文件时临时决定的。

因此：

\[
\boxed{
Split
=
LineageProperty
}
\]

这直接保证：

```text
原样本
近重复样本
Counterfactual
Hard Case Pair
Synthetic派生样本
```

不会被错误拆到考试两边。

---

## 心智模型 5：正式 Dataset 是 Build 出来的，不是手工拖文件拼出来的

最终数据产品最好不是：

> 小王复制几个 CSV，小李补一个 JSON，再压成 ZIP。

而应该是一条明确的：

# Dataset Build Pipeline
## 数据集构建流水线

```text
Master Data
    ↓
Schema Validation
    ↓
Lineage Validation
    ↓
Split Validation
    ↓
Leakage Audit
    ↓
Task View Generation
    ↓
Quality Checks
    ↓
Manifest + Hash
    ↓
Release Gate
    ↓
Frozen Dataset Version
```

因此：

\[
\boxed{
DatasetRelease
=
ReproducibleBuild
}
\]

这才叫工程化。

---

# 三、现在真正打开 `ProcurementDataset_V0.1`

第一版正式数据资产，可以设计成这样的目录。

```text
ProcurementDataset_V0.1/
│
├── README.md
├── CHANGELOG.md
├── manifest.json
│
├── schemas/
│   ├── master_schema.json
│   ├── annotation_schema.json
│   ├── hardcase_schema.json
│   └── data_contract.md
│
├── source_registry/
│   └── documents.jsonl
│
├── master/
│   ├── clauses.jsonl
│   ├── annotations.jsonl
│   ├── lineage.jsonl
│   └── split_map.jsonl
│
├── views/
│   ├── classification/
│   │   ├── train.jsonl
│   │   ├── validation.jsonl
│   │   └── test.jsonl
│   │
│   ├── sft_candidate/
│   │   ├── train.jsonl
│   │   └── validation.jsonl
│   │
│   └── retrieval/
│       └── evidence_pairs.jsonl
│
├── evaluation/
│   ├── heldout_gold.jsonl
│   ├── hard_cases.jsonl
│   └── slices.json
│
├── audit/
│   ├── leakage_report.json
│   ├── dedup_report.json
│   └── annotation_agreement.json
│
└── reports/
    ├── DatasetQualityReport_V0.1.md
    └── DatasetQualityReport_V0.1.json
```

先别急着记目录。

真正重要的是：

> **每类文件职责完全不同。**

---

# 四、第一层：`source_registry/`

这里不是训练数据。

它解决的是：

> 原始文件到底是谁？

例如：

```json
{
  "document_id": "DOC-00152",
  "project_id": "PROJECT-00152",
  "source_type": "tender_document",
  "source_filename": "某项目采购文件.pdf",
  "file_sha256": "8f1c...",
  "publication_date": "2026-05-18",
  "source_status": "verified"
}
```

注意：

这里可以只保存：

> 原文件 Registry / 引用。

不一定必须把所有原始 PDF：

> 直接打进发布给训练人员的数据包。

原文件如何存储：

> 应按照项目授权、隐私、安全和数据治理要求决定。

---

# 五、第二层：`master/`

这是整个 Dataset 的核心。

可以把它理解成：

# 数据总账

---

## `clauses.jsonl`

保存：

> 采购 Clause 本身。

例如：

```json
{
  "sample_id": "SAMPLE-00178",

  "project_id": "PROJECT-00152",
  "document_id": "DOC-00152",
  "clause_id": "CLAUSE-00178",

  "section_path": [
    "第三章 采购需求",
    "3.2 售后服务"
  ],

  "raw_text": "供应商应保证故障发生后 2 小时内到达项目现场。",
  "normalized_text": "供应商应保证故障发生后2小时内到达项目现场。",

  "source_page": 27,

  "parser_version": "parser_v0.3",
  "structure_version": "structure_v0.2",
  "normalizer_version": "normalize_v0.2"
}
```

这回答：

> 文本是什么？

---

# 六、`annotations.jsonl`

保存：

> 专家判断是什么？

例如：

```json
{
  "sample_id": "SAMPLE-00178",

  "risk_present": "uncertain",
  "primary_risk_type": "C",
  "needs_review": true,

  "rationale": {
    "observed_fact": "要求2小时内到达现场。",
    "risk_concern": "需要结合项目实际判断该服务时限的必要性。",
    "context_needed": "项目性质、停机影响、履约地点及服务模式。"
  },

  "annotation_status": "gold",

  "annotation_schema_version": "annotation_schema_v0.1",
  "guideline_version": "annotation_guideline_v0.1"
}
```

这回答：

> 专家怎么看？

---

# 七、为什么 Clause 和 Annotation 可以分开？

因为文本和 Label：

> 生命周期并不完全相同。

Clause 可能不变，

但是：

```text
Annotation Guideline v0.1
→
v0.2
```

专家可能重新裁决。

如果文本和 Label 永远硬编码成一个无法拆开的对象：

> 后面更新比较麻烦。

所以工程上可以根据实际存储技术决定是否物理分表，

但概念上一定要知道：

\[
\boxed{
SourceContent
\neq
ExpertJudgment
}
\]

---

# 八、第三个核心文件：`lineage.jsonl`

它保存：

> 这条数据从哪里来的。

例如：

```json
{
  "sample_id": "SAMPLE-00178",

  "project_id": "PROJECT-00152",
  "document_id": "DOC-00152",

  "source_block_ids": [
    "BLOCK-00872"
  ],

  "parent_sample_ids": [],

  "derived_sample_ids": [
    "HC-00318"
  ]
}
```

如果是一条 Counterfactual Hard Case：

```json
{
  "sample_id": "HC-00318",

  "parent_sample_ids": [
    "SAMPLE-00178"
  ],

  "derivation_type": "counterfactual_edit",

  "pair_id": "PAIR-00072"
}
```

这就是：

# Data Lineage

---

# 九、第四个核心文件：`split_map.jsonl`

例如：

```json
{
  "sample_id": "SAMPLE-00178",
  "project_id": "PROJECT-00152",
  "lineage_group_id": "LG-00152",
  "split": "train",
  "split_version": "procurement_split_v0.1"
}
```

真正重要的是：

> Split 信息独立保存。

这样无论以后派生：

```text
Classification View
SFT View
RAG View
Hard Case View
```

都必须读取：

> 同一份 `split_map`。

---

# 十、这解决一个非常危险的问题

假设：

```text
SAMPLE-00178
→ Train
```

然后根据它生成：

```text
HC-00318
```

如果 View Builder 自己 Random Split，

可能出现：

```text
SAMPLE-00178
→ Train

HC-00318
→ Test
```

这就是：

# Leakage

所以我们的规则是：

\[
\boxed{
DerivedSample
InheritsSplitFromLineageGroup
}
\]

派生样本：

> 继承父级血缘 Group 的 Split。

---

# 十一、现在进入最关键的 `views/`

这才是：

> **真正给模型使用的文件。**

注意：

Master Data：

> 不是默认直接训练。

而应该经过：

# View Builder
## 任务视图生成器

---

# 十二、例如 Classification View

Master 中：

```text
raw_text
normalized_text
project_id
section_path
expert_rationale
gold_label
evidence
adjudication_comment
...
```

我们构造分类任务：

Input：

```text
normalized_text
section_path
允许的上下文
```

Target：

```text
risk_present
primary_risk_type
```

于是最终 Training Record 可能只有：

```json
{
  "sample_id": "SAMPLE-00178",

  "input": {
    "clause_text": "供应商应保证故障发生后2小时内到达项目现场。",
    "section_path": [
      "第三章 采购需求",
      "3.2 售后服务"
    ]
  },

  "target": {
    "risk_present": "uncertain",
    "primary_risk_type": "C"
  }
}
```

---

# 十三、注意消失了什么

这里没有：

```text
adjudication_reason
gold_evidence
reviewer_note
future_outcome
```

为什么？

因为这些：

> 是答案侧信息。

不能偷偷出现在 Input。

这就是：

# Input Firewall

---

# 十四、现在正式定义三类字段

这是 `ProcurementDataset_V0.1` 中非常重要的一张表。

| 字段类型 | 含义 | 是否可直接进入模型输入 |
|---|---|---|
| **Input Field** | 真实推理时能够获得的信息 | 可以 |
| **Target Field** | 希望模型学习预测/生成的信息 | 只能作为训练目标 |
| **Audit Field** | Gold、裁决、血缘、未来结果等治理信息 | 默认禁止 |

例如：

```text
clause_text
→ Input

risk_present
→ Target

adjudication_comment
→ Audit
```

---

# 十五、最重要的规则之一

\[
\boxed{
InferenceTimeAvailable
\Rightarrow
PotentialInput
}
\]

也就是说：

> **只有真实上线推理时也能够获得的信息，才适合成为普通模型 Input。**

这是判断一个字段是否可能泄漏的最好问题。

---

# 十六、举个明显的错误

模型 Input：

```text
项目条款：
供应商须……

专家复核状态：
已确认高风险

请判断是否存在风险。
```

模型当然表现极好。

因为：

> 答案已经写在题目里。

这就是典型：

# Label Leakage

---

# 十七、`sft_candidate/` 为什么叫 Candidate？

因为第四课还没有正式学习：

```text
Chat Template
Loss Mask
Packing
SFT格式
```

这些是第五课的内容。

所以第四课可以先生成：

# SFT Candidate View
## SFT 候选视图

例如：

```json
{
  "sample_id": "SAMPLE-00178",

  "input": {
    "target_clause": "供应商应保证故障发生后2小时内到达项目现场。",
    "section_context": "第三章采购需求 / 售后服务"
  },

  "target": {
    "risk_present": "uncertain",
    "needs_review": true,
    "reason": "需要结合项目性质与现场服务必要性进一步判断。"
  }
}
```

到了第五课：

> 再把它正式转换成 Chat Template。

---

# 十八、这是课程之间非常重要的边界

第四课负责：

> **数据内容正确。**

第五课负责：

> **怎样把内容喂给模型训练。**

可以写成：

\[
\boxed{
Lesson4
=
WhatData
}
\]

\[
\boxed{
Lesson5
=
HowToTrain
}
\]

不要混在一起。

---

# 十九、现在进入 `evaluation/`

这个目录跟 Train 完全不同。

它的任务不是：

> 教模型。

而是：

> **考模型。**

---

# 二十、`heldout_gold.jsonl`

这是：

# Held-out Gold
## 完全隔离的 Gold 测试集

例如包含：

```text
Input
Gold Label
Gold Rationale
Gold Evidence
Difficulty
Slice
```

但评测程序必须保证：

> Gold Answer 不进入模型 Input。

---

# 二十一、这里顺便澄清一个非常容易混淆的概念

# Gold ≠ Test

`gold` 描述的是：

> **标注质量。**

`test` 描述的是：

> **数据用途。**

因此可能存在：

```text
Gold Train Sample
```

高质量专家数据，用于训练。

也可以存在：

```text
Gold Test Sample
```

高质量专家数据，用于考试。

所以：

\[
\boxed{
GoldStatus
\neq
Split
}
\]

这是一个很重要的专业区别。

---

# 二十二、真正的 Benchmark Gold 必须同时满足

```text
annotation_status = gold
+
split = test
+
leakage_status = passed
```

才能成为：

> 可靠考试数据。

---

# 二十三、`hard_cases.jsonl`

这里保存第 10 阶段的：

```text
Hard Positive
Hard Negative
Boundary Case
Contrastive Pair
```

但最好明确：

> 哪些属于 Train Hard Case，

哪些属于：

> Evaluation Hard Case。

两边不能混用。

---

# 二十四、`slices.json`

# Slice
## 评测切片

例如：

```json
{
  "risk_types": [
    "supplier_qualification",
    "technical_requirement",
    "commercial_requirement",
    "scoring_rule",
    "procurement_requirement"
  ],

  "difficulty": [
    "easy",
    "hard",
    "boundary"
  ]
}
```

未来第 8 课评测时，

我们就可以问：

```text
模型整体表现怎样？

资格风险怎样？

技术参数怎样？

Hard Negative怎样？

Boundary Case怎样？
```

而不是：

> 只有一个总 Accuracy。

---

# 二十五、现在进入 `audit/`

这里的文件：

> **绝对不是训练素材。**

例如：

```text
leakage_report.json
dedup_report.json
annotation_agreement.json
```

这些文件是：

# Governance Data
## 数据治理信息

它们帮助人：

> 判断 Dataset 是否可信。

不是帮助模型：

> 回答采购问题。

---

# 二十六、这引出了一个极重要的隔离原则

可以把整个 Dataset 分成三个安全区：

```text
Zone A
Model Input Zone
模型允许看到

Zone B
Target Zone
训练阶段作为答案

Zone C
Governance / Gold Zone
只用于评测、审计、治理
```

模型运行时：

> 不应该随意穿越这些区。

---

# 二十七、这实际上就是 Dataset 层面的权限设计

以后大型团队里，

甚至可以物理分权限：

```text
训练团队
看Train View

评测团队
掌握Benchmark Gold

审计人员
查看Lineage和裁决记录
```

这样能够降低：

> Benchmark 被无意污染的风险。

---

# 二十八、现在第一次真正定义 `ProcurementDataset_V0.1`

它不是一个表。

而是：

\[
\boxed{
ProcurementDataset_{V0.1}
=
SourceRegistry
+
MasterData
+
Annotations
+
Lineage
+
SplitMap
+
TaskViews
+
EvaluationSet
+
AuditReports
+
Manifest
}
\]

中文就是：

> **来源 + 主数据 + 专家判断 + 数据血缘 + 安全切分 + 训练视图 + 测试视图 + 质检证据 + 版本身份。**

这才是一个真正的数据产品。

---

# 二十九、那么真正发布 V0.1 之前，要按什么顺序 Build？

不要手工拼。

正确心智模型是：

```text
Freeze Source Snapshot
冻结来源
        ↓
Validate Master Data
验证主数据
        ↓
Validate Annotation
验证专家标签
        ↓
Resolve Lineage Groups
确定血缘组
        ↓
Apply Frozen Split
应用冻结切分
        ↓
Run Leakage Audit
泄漏审计
        ↓
Generate Task Views
生成任务视图
        ↓
Validate Input Firewall
检查答案是否泄漏
        ↓
Generate Quality Report
生成质量报告
        ↓
Compute Hashes
生成内容Hash
        ↓
Release Gate
发布门槛
        ↓
Freeze V0.1
正式冻结
```

这条链：

> 就是第四课最后的工程总流程。

---

# 三十、这里为什么要“先 Split，再派生 View”？

因为如果先：

```text
生成各种改写
生成Hard Case
生成SFT数据
```

然后各自 Random Split，

极容易产生：

> 血缘泄漏。

所以更专业的思路是：

\[
\boxed{
GroupIdentity
\rightarrow
Split
\rightarrow
DerivedViews
}
\]

不是：

\[
DerivedViews
\rightarrow
RandomSplit
\]

这是第四课一个很重要的总原则。

---

# 三十一、一个正式 Build 最好“失败得响亮”

假设发现：

```text
Test Sample
与
Train Sample
共享同一个lineage_group
```

不要：

> 打个 warning 然后继续发版。

应该：

# FAIL

同理：

```text
Gold样本缺source provenance
```

如果这是项目硬要求：

> Build 直接失败。

---

# 三十二、这叫：

# Fail Loudly
## 显式失败

宁可 Dataset 发布失败，

也不要：

> 悄悄生成一个看起来正常的错误数据集。

---

# 三十三、所以最终 Release Gate 可以长这样

| 检查项 | V0.1 发布要求 |
|---|---|
| Schema Validation | 必须通过 |
| Cross-field Validation | 无 Critical Error |
| Train/Test Project Overlap | 0 |
| Confirmed Leakage | 0 |
| Critical Gold Disagreement | 已处理 |
| Manifest | 完整 |
| Hash | 已生成 |
| Known Limitations | 已记录 |
| Quality Report | 已生成 |

实际阈值：

> 由真实项目决定。

但“有发布门槛”这件事：

> 必须存在。

---

# 三十四、现在模拟一次完整的数据流

原始采购文件：

```text
DOC-00152.pdf
```

Stage 2：

```text
ParsedDocument
```

Stage 3：

```text
CLAUSE-00178
```

Stage 4：

```text
CleanClause-00178
```

Stage 5：

```text
duplicate_cluster = DC-0021
```

Stage 6：

```text
project_id PROJECT-00152
→ train
```

Stage 7：

```text
leakage_status = passed
```

Stage 8：

```text
risk_present = uncertain
```

Stage 9：

```text
annotation_status = gold
```

Stage 10：

```text
case_type = boundary_case
```

Stage 11：

```text
dataset_version = 0.1
```

最终：

```text
ProcurementDataset_V0.1
```

中它可能进入：

```text
Train Master
+
SFT Candidate Train View
+
Boundary Case Statistics
```

但因为：

```text
split = train
```

它：

> 永远不能突然出现在 Test。

---

# 三十五、这就是整个第四课最重要的一个贯穿关系

一条数据：

> 从出生到最终使用，

所有状态应该彼此相连。

```text
Raw File
   ↓
Parsed Block
   ↓
Clause
   ↓
Normalized Clause
   ↓
Dedup Group
   ↓
Split Group
   ↓
Annotation
   ↓
Gold Status
   ↓
Hard Case Status
   ↓
Task View
   ↓
Model Experiment
```

这叫：

# End-to-End Lineage
## 端到端数据血缘

---

# 三十六、到了第五课，我们真正需要哪些文件？

这点要非常明确。

第五课训练模型时，

最主要使用的是：

```text
views/sft_candidate/train.jsonl
views/sft_candidate/validation.jsonl
```

以及必要的：

```text
schema
manifest
```

用于确认：

> 数据到底是什么版本。

---

# 三十七、第五课绝对不应该直接把这些文件喂给模型

```text
evaluation/heldout_gold.jsonl
audit/leakage_report.json
master/adjudication_comments
reviewer_notes
future_outcomes
```

尤其：

# `heldout_gold`

在模型最终测试之前：

> 必须像真正考试卷一样保护。

---

# 三十八、为什么 Test 必须像考试卷？

因为模型开发阶段很容易发生：

```text
测试一次
看错题
改Prompt

再测试
继续看错题
再改
```

做得次数足够多，

Test：

> 实际上已经变成开发数据。

---

# 三十九、所以 Validation 和 Test 的职责必须分开

# Validation
## 验证集

用来：

> 调模型、调参数、选方案。

# Test
## 测试集

用来：

> 最终评估泛化能力。

可以简单记：

```text
Train
=
学习

Validation
=
练习考试

Test
=
正式考试
```

---

# 四十、这就是为什么第四课 Stage 6 那么重要

如果这个边界从一开始就错：

后面：

```text
SFT
LoRA
RAG
Benchmark
```

所有数字都可能：

> 看起来很科学，实际上不可信。

---

# 四十一、现在看 `manifest.json` 的最终角色

它可能记录：

```json
{
  "dataset_name": "ProcurementDataset",
  "dataset_version": "0.1",

  "master_schema_version": "master_schema_v0.1",
  "annotation_schema_version": "annotation_schema_v0.1",
  "annotation_guideline_version": "annotation_guideline_v0.1",

  "parser_version": "parser_v0.3",
  "structure_version": "structure_v0.2",
  "normalizer_version": "normalize_v0.2",
  "dedup_version": "dedup_v0.1",

  "split_version": "procurement_split_v0.1",
  "leakage_audit_version": "leakage_audit_v0.1",

  "release_status": "released"
}
```

这相当于：

> **整个第四课所有版本的最终汇合点。**

---

# 四十二、质量报告则回答“这版到底值不值得用”

例如：

```text
ProcurementDataset_V0.1

Schema Validation:
PASS

Cross-split Project Overlap:
0

Confirmed Leakage:
0

Gold Annotation:
verified

Hard Case Coverage:
present

Known Limitations:
D类评分规则Hard Positive仍不足

Release Decision:
PASS WITH KNOWN LIMITATIONS
```

注意：

> `PASS WITH KNOWN LIMITATIONS`

完全可以是专业的发布状态。

专业不是：

> 假装没有问题。

而是：

> 知道问题在哪里。

---

# 四十三、第四课从第一阶段走到这里，其实完成了一次巨大的转变

一开始我们看到的是：

```text
10万份PDF
```

这只是：

# Documents

现在得到的是：

```text
ProcurementDataset_V0.1
```

它已经包含：

```text
可定位的Clause
可追溯的来源
安全规范化文本
重复关系
固定Split
泄漏审计
专家结构化判断
Gold质量状态
Hard Case
任务视图
数据版本
质量报告
```

这才叫：

# Training Asset
## 可训练的数据资产

---

# 四十四、第四课最容易犯的终极错误

就是：

> “文件都清洗好了，所以可以开始训练了。”

其实真正应该问的是：

```text
这条数据为什么在Train？
它的父样本是谁？
专家标签是哪一版？
有没有近重复进入Test？
它的Input里有没有答案信息？
这个Gold是不是已经裁决？
这个Dataset到底是哪一版？
```

如果这些回答不了：

> 还不应该急着训练。

---

# 四十五、第 12 阶段真正的专业升级

前面很多阶段是在：

> 优化数据内容。

最后这一阶段是在建立：

# Data Boundary
## 数据使用边界

它规定：

```text
什么是事实
什么是Label
什么能训练
什么只能评测
什么只能审计
什么绝对不能泄漏
```

这比单纯“数据格式整理漂亮”：

> 重要得多。

---

# 四十六、第四课最后只需要牢牢记住 5 个核心心智模型

> **第一，Dataset 不是一个训练文件，而是 Master Data、Task View 和 Governance Asset 的组合。**

> **第二，Master Data 是完整真相源，训练数据只是从它派生出来的任务视图。**

> **第三，数据存在于数据库里，不代表它允许进入模型 Input；Gold、裁决、未来结果必须建立 Input Firewall。**

> **第四，Split 是数据血缘的一部分，所有近重复、Counterfactual、Hard Case 和 Synthetic 派生样本必须继承同一个 Leakage Group。**

> **第五，正式 Dataset 必须通过可复现的 Build Pipeline 和 Release Gate 生成，而不是人工拖文件拼出来。**

如果第四课只长期记住这五句话：

> 整套政府采购数据工程的大方向就不会走偏。

---

# 四十七、现在正式定义本课最终工程交付物

\[
\boxed{
ProcurementDataset_{V0.1}
}
\]

它至少满足：

```text
来源可追溯
结构可理解
文本可训练
重复可识别
Split可复现
Leakage可审计
Label可解释
Gold可验证
Hard Case可分析
版本可冻结
质量可报告
任务视图可生成
```

这 12 个性质，

比：

> “有多少 GB 数据”

重要得多。

---

# 四十八、第四课最终掌握测试

现在不回看前面十二阶段，你应该已经能完整讲出这样一条链：

一份政府采购 PDF 为什么不能直接等于一个训练样本；为什么首先要定义 Task Schema；为什么解析成功不等于获得可信文本；为什么 Clause Segmentation 不能简单按句号切；为什么 Cleaning 不能改写原始业务含义；为什么 Exact Duplicate 只是去重最容易的一层；为什么 Train / Validation / Test 应按项目、血缘或时间等安全单位切分；为什么 Benchmark Leakage 会制造虚假成绩；为什么 `unknown` 不能等同于 `false`；为什么专家 Gold 需要双人独立标注、分歧分析和裁决；为什么 Hard Negative 能阻止模型学习关键词捷径；为什么 Counterfactual Pair 必须保持 Split 一致；为什么 Dataset Version 不是文件名；为什么 Lineage 能让一条 Gold Label 一路追到原始 PDF；为什么 Dataset Quality 必须拆成多个维度；为什么 Master Data 和 Training View 不应该是同一个东西；为什么 Gold 字段不能因为存在就进入模型 Input；为什么 Validation 与 Test 的职责不同；以及为什么一个真正可以交付的 Dataset 必须同时具备版本、血缘、质量、使用边界和可复现 Build。

如果这一整条链已经能够自己讲清楚：

\[
\boxed{
第四课真正掌握
}
\]

---

# 四十九、第四课最后只记一句话

> **政府采购 AI 的训练数据，不是“把很多 PDF 清洗成 JSON”，而是把原始采购文件经过可信解析、业务结构恢复、安全规范化、去重、安全切分、防泄漏、专家标注、分歧裁决、Hard Case 建设、版本治理和质量验证，最终封装成一个 Master Data 完整、训练与考试边界清楚、可追溯、可复现、可审计的数据产品。**

最终就是：

# `ProcurementDataset_V0.1`

---

# 五十、第四课最终总图

```text
                 政府采购原始文件
                        │
                        ▼
             ┌────────────────────┐
             │  1. Task Schema    │
             │   定义一条数据是什么 │
             └─────────┬──────────┘
                       ▼
             ┌────────────────────┐
             │ 2. Document Parse  │
             │     可信文档解析     │
             └─────────┬──────────┘
                       ▼
             ┌────────────────────┐
             │ 3. Clause Restore  │
             │   恢复业务条款结构   │
             └─────────┬──────────┘
                       ▼
             ┌────────────────────┐
             │ 4. Normalization   │
             │    安全文本规范化    │
             └─────────┬──────────┘
                       ▼
             ┌────────────────────┐
             │     5. Dedup       │
             │   精确/近似/模板去重 │
             └─────────┬──────────┘
                       ▼
             ┌────────────────────┐
             │      6. Split      │
             │ Train / Val / Test │
             └─────────┬──────────┘
                       ▼
             ┌────────────────────┐
             │  7. Leakage Audit  │
             │       防止偷题       │
             └─────────┬──────────┘
                       ▼
             ┌────────────────────┐
             │ 8. Label Schema    │
             │    专家到底标什么    │
             └─────────┬──────────┘
                       ▼
             ┌────────────────────┐
             │ 9. Expert Gold     │
             │ 双标、复核、专家裁决 │
             └─────────┬──────────┘
                       ▼
             ┌────────────────────┐
             │ 10. Hard Cases     │
             │     学习决策边界     │
             └─────────┬──────────┘
                       ▼
             ┌────────────────────┐
             │ 11. Governance     │
             │ 版本、血缘、质量报告 │
             └─────────┬──────────┘
                       ▼
             ┌────────────────────┐
             │ 12. Dataset Build  │
             │ 主数据→任务视图→发布 │
             └─────────┬──────────┘
                       ▼
        ╔══════════════════════════════╗
        ║   ProcurementDataset_V0.1  ║
        ║   政府采购AI第一版数据资产   ║
        ╚══════════════╤═══════════════╝
                       │
                       ▼
                 第五课开始
              SFT + LoRA / QLoRA
```

---

# 第四课正式结束

到这里，我们已经完成整个课程里的第 **4 / 10 课**。

前三课解决：

```text
第一课
机器学习到底在学什么

第二课
LLM内部到底怎样工作

第三课
怎样真正把一个开源大模型跑起来
```

第四课解决：

> **拿什么教它。**

而第五课终于进入一个非常关键的转折：

# 第五课：SFT + LoRA / QLoRA 微调
## 我们怎样第一次真正改变一个开源大模型的行为？

第五课开始以后，我们会从：

```text
ProcurementDataset_V0.1
```

真正走到：

```text
ProcurementLM_V0.1
```

其中第 1 阶段不会急着跑训练命令。

我们首先会解决：

# Chat Template、Prompt、Response 与 Loss Mask
## 模型训练时，到底哪些 Token 是“题目”，哪些 Token 才是它真正应该学习预测的答案？

因为如果这一点没搞清楚，即使 Dataset 做得再好：

> SFT 也可能从第一批 Token 就训错。




---

<!-- LESSON 04 STAGE 12 END -->

