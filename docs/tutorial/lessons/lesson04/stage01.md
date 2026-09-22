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
