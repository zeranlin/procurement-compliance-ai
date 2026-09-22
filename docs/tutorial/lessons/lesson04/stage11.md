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
