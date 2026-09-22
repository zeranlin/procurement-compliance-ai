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
