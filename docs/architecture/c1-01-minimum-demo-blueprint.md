# ProcurementComplianceLM C1-01 Minimum Demo Execution Blueprint V0.1
## L4 政府采购合规模型——第1类第1项最小闭环 Demo 执行蓝图

> **项目负责人版本：V0.1**
>
> **目标：** 不先做7类22项全部能力，只选择附件9“第1类”的“第1项表现形式”，把 **业务要求 → 案例采集 → 结构化标注 → 数据集 → Baseline → 微调训练 → Blind Benchmark → 评审决策** 全流程完整跑通。
>
> **重要边界：** 当前没有独立专家组，因此本Demo的数据只能定义为 `Internal Silver / 内部暂定标注数据`，不能定义为正式Gold。专家治理在后续版本补入。

---

# 0. 本Demo到底做什么

## 0.1 来源业务范围

附件9第1类问题为：

> **直接或变相对外地企业进入本地市场设置阻碍。**

本Demo只做其中第1项表现形式：

> **采购文件设置供应商注册地、所在地距采购人的距离、在某行政区域内设立分支机构等不合理的资格条件、评审因素。**

为了避免把内部工程编号误认为财政部原文编号，本项目暂定工程ID：

`C1-01_LOCAL_ENTRY_PRECONDITION`

中文：**第1类-第1项：供应商注册地 / 距采购人距离 / 预先设立区域分支机构等准入或评审限制。**

正式D01-D22内部编号以后由 Rule Registry 冻结，本Demo不抢先把内部ID说成官方编号。

---

# 1. Demo 的核心心智模型

## 1.1 Task != FinalViolationJudgment

中文：本Demo训练的不是“自动判违法模型”，而是：

> **识别采购条款是否匹配 C1-01 这一具体表现形式，并抽取证据、识别子类型和不确定状态。**

目标输出是 `MATCH / NO_MATCH / NEEDS_CONTEXT`，不是“违法/合法”。

## 1.2 KeywordMatch != ItemMatch

中文：出现“本地”“服务”“距离”“分公司”等词，不等于命中。

## 1.3 LocalServiceNeed != LocalEntityPrecondition

中文：要求中标后提供本地服务能力，与要求投标前已经在本地注册/设分支机构，不是同一件事。

## 1.4 Clause != Requirement

中文：一段采购文字可能包含多个要求，模型和数据必须以可独立判断的 Requirement 为单位。

## 1.5 CollectedCase != TrainingCase

中文：业务组收集到的原始案例，必须经过结构化、标注、数据质量检查，才能进入训练数据。

## 1.6 InternalSilver != Gold

中文：当前没有专家组，内部标注只能作为Demo验证资产，不得宣称是正式Gold真值。

## 1.7 TrainingSet != BenchmarkSet

中文：训练数据与Blind Benchmark必须按项目/模板家族隔离，不能简单随机切分。

---

# 2. Demo 的最小系统边界

本次只建设：

```text
业务组 / 产品组
BusinessTaskSpec + Case Intake + Internal Label
        ↓
数据工程组
Clause / Requirement / Evidence → Dataset
        ↓
算法组
Base Model Baseline → LoRA/QLoRA SFT → Candidate Model
        ↓
测试与评测组
Blind Benchmark → Metrics → Gate Decision
```

本次**暂不建设**完整：

- Policy Registry；
- Legal RAG；
- D01-D22 Rule Engine；
- Hybrid Compliance Engine；
- Agent Workflow；
- WorkBuddy最终接入。

这些不是被否定，而是为了先证明 L4 模型训练闭环能稳定运行。

---

# 3. 四个小组的职责边界

| 小组 | 负责 | 明确不负责 | 核心交付 |
|---|---|---|---|
| 业务组 / 产品组 | 定义C1-01业务范围、收案例、内部标注、边界案例 | 不训练模型、不改测试Blind结果 | `BusinessTaskSpec`、`CasePack`、`LabelGuide` |
| 数据工程组 | 文档/条款结构化、Schema、清洗、去重、Leakage Group、Dataset Split | 不修改业务标签含义 | `DatasetSnapshot`、`DataQualityReport` |
| 算法组 | Baseline、训练、模型版本、推理输出、实验追踪 | 不接触Blind Gold、不自行改标签 | `ModelArtifact`、`TrainingManifest`、`Prediction` |
| 测试与评测组 | Benchmark冻结、Blind测试、指标、Error Analysis、Gate | 不为了模型通过而改Gold | `BenchmarkSnapshot`、`EvaluationReport`、`GateDecision` |

核心心智模型：

`ParallelDevelopment = StableContract + ClearOwnership + FrozenInterfaces`

---

# 4. 业务组 / 产品组 Work Package

## WP-BIZ-01：BusinessTaskSpec

### 交付物

`BR_C1_01_Business_Task_Spec_V0.1.md`

必须写清楚：

```yaml
task_id: C1-01_LOCAL_ENTRY_PRECONDITION
task_name_cn: 外地企业进入本地市场前置限制识别

source_category:
  category_no: 1
  category_name: 直接或变相对外地企业进入本地市场设置阻碍

target_manifestation:
  注册地 / 所在地距采购人的距离 / 某行政区域内预先设立分支机构
  被设置为不合理的资格条件或评审因素

model_task:
  candidate_detection

allowed_output:
  - MATCH
  - NO_MATCH
  - NEEDS_CONTEXT

not_in_scope:
  - 最终法律责任判断
  - 行政处罚判断
  - 完整7类22项
```

### 验收

- 业务范围只有1项，不能偷偷扩大；
- 正例、负例、不确定边界明确；
- `MATCH` 不等于最终违法；
- 测试组签字确认“可测”。

---

## WP-BIZ-02：LabelGuide

### 交付物

`C1_01_Label_Guide_V0.1.md`

### Label Schema

```yaml
match_state:
  MATCH:
    # 中文：当前Requirement明确匹配C1-01表现形式
  NO_MATCH:
    # 中文：当前Requirement不属于C1-01
  NEEDS_CONTEXT:
    # 中文：现有文字不足以可靠判断

subtype:
  SUPPLIER_REGISTRATION_LOCATION:
    # 中文：以供应商注册地/所在地为条件
  DISTANCE_TO_PURCHASER:
    # 中文：以所在地距采购人距离为条件
  PREEXISTING_LOCAL_BRANCH:
    # 中文：要求投标前已在特定行政区域设立分支机构
  OTHER_RELATED:
    # 中文：同类但不属于前三个标准子型
  NONE:
    # 中文：不命中

business_stage:
  QUALIFICATION:
    # 中文：资格准入
  SCORING:
    # 中文：评审加分/评分
  TECHNICAL:
    # 中文：技术或服务要求
  CONTRACT:
    # 中文：合同履约阶段
```

---

## WP-BIZ-03：Case Intake

### 原始案例输入格式

`C1_01_Case_Intake_V0.1.jsonl`

单条示例：

```json
{
  "case_id": "CASE-C101-0001",
  "project_id": "P-001",
  "document_id": "DOC-001",
  "document_version": "V1",
  "source_text": "投标人须为本市注册企业。",
  "source_location": {
    "page": 8,
    "section": "供应商资格条件"
  },
  "suspected_subtype": "SUPPLIER_REGISTRATION_LOCATION",
  "collector_note": "疑似以注册地作为供应商准入条件",
  "source_verified": true
}
```

---

## WP-BIZ-04：内部暂定标注包

当前无专家组，正式命名：

`C1_01_InternalSilver_CasePack_V0.1.jsonl`

不要叫Gold。

单条示例：

```json
{
  "case_id": "CASE-C101-0001",
  "requirement_text": "投标人须为本市注册企业。",
  "business_stage": "QUALIFICATION",
  "label": {
    "match_state": "MATCH",
    "subtype": "SUPPLIER_REGISTRATION_LOCATION"
  },
  "evidence_text": "投标人须为本市注册企业。",
  "reasoning_factors": [
    "pre_award_condition",
    "supplier_location_attribute",
    "market_entry_gate"
  ],
  "review_state": "INTERNAL_REVIEWED",
  "label_authority": "INTERNAL_SILVER"
}
```

### 业务组必须准备的案例类型

1. Typical Positive / 典型正例；
2. Hard Positive / 隐蔽表达正例；
3. Normal Negative / 普通负例；
4. Hard Negative / 高相似但不命中；
5. Missing Context / 信息不足；
6. Counterfactual Pair / 反事实样本对。

---

# 5. Demo 数据规模 V0.1

目标不是生产级训练，而是证明闭环。

建议第一轮：

- **总计接受样本：200条左右**；
- 来源尽量覆盖 **≥30个不同项目或模板家族**；
- 同一项目/模板家族必须绑定 `leakage_group_id`。

建议主标签分布：

| 类型 | 目标数量 |
|---|---:|
| `MATCH` | 80 |
| `NO_MATCH` | 100 |
| `NEEDS_CONTEXT` | 20 |
| 其中 Hard Negative | ≥50 |
| Counterfactual Pair | ≥20对（作为附加标签，不重复计数） |

拆分建议：

- Train：120
- Dev：30
- Blind Test：50

**必须按项目/模板家族 Group Split，不允许逐条随机Split。**

---

# 6. 业务组边界案例模板

## Positive

> “投标人须在本市注册。”

期望：

```yaml
match_state: MATCH
subtype: SUPPLIER_REGISTRATION_LOCATION
```

## Positive

> “投标人办公地点距离采购人不得超过20公里。”

期望：

```yaml
match_state: MATCH
subtype: DISTANCE_TO_PURCHASER
```

## Positive

> “供应商须在本行政区域内已设立分公司。”

期望：

```yaml
match_state: MATCH
subtype: PREEXISTING_LOCAL_BRANCH
```

## Hard Negative

> “中标供应商应在合同签订后建立满足2小时响应要求的项目服务机制。”

期望：

```yaml
match_state: NO_MATCH
```

关键原因：

`LocalServiceNeed != LocalEntityPrecondition`

## Missing Context

> “供应商应具备本地化服务能力。”

期望：

```yaml
match_state: NEEDS_CONTEXT
```

原因：没有说明是否要求供应商投标前已经在特定地区注册、设分支机构或满足所在地距离门槛。

## Counterfactual Pair

A：

> “投标人须在本市已设分公司。”

B：

> “中标后须建立满足本项目响应时效要求的服务保障机制。”

A期望 `MATCH`；B期望 `NO_MATCH`。

---

# 7. 数据工程组 Work Package

## WP-DATA-01：数据Schema

交付：

`C1_01_Dataset_Schema_V0.1.json`

模型训练单元：

```json
{
  "sample_id": "S-C101-0001",
  "leakage_group_id": "LG-001",
  "input": {
    "clause_text": "投标人须为本市注册企业。",
    "business_stage": "QUALIFICATION",
    "context": null
  },
  "target": {
    "item_id": "C1-01_LOCAL_ENTRY_PRECONDITION",
    "match_state": "MATCH",
    "subtype": "SUPPLIER_REGISTRATION_LOCATION",
    "evidence_text": "投标人须为本市注册企业。",
    "reasoning_factors": [
      "supplier_location_attribute",
      "pre_award_condition"
    ],
    "human_review_required": false
  },
  "metadata": {
    "case_id": "CASE-C101-0001",
    "label_authority": "INTERNAL_SILVER"
  }
}
```

---

## WP-DATA-02：标准Dataset交付结构

```text
C1_01_DatasetSnapshot_V0.1/
├── schema.json
├── train.jsonl
├── dev.jsonl
├── blind_test_input.jsonl
├── data_manifest.json
├── leakage_groups.json
├── dedup_report.json
├── data_quality_report.json
└── examples/
```

**注意：** `blind_test_gold.jsonl` 不在算法组可访问的数据包中，由测试组单独持有。

---

## WP-DATA-03：数据验收Gate

必须全部满足：

- Schema Valid Rate = 100%
- Source Traceable Rate = 100%
- Label Enum Valid Rate = 100%
- Duplicate / Near Duplicate 已检查
- Leakage Group 已分配
- Train / Dev / Blind Test 项目级隔离
- Counterfactual Pair 不跨Split
- `INTERNAL_SILVER` 标识保留
- Blind Gold 不进入训练目录

核心心智模型：

`DataClean != LeakageSafe`

---

# 8. 算法组 Work Package

## WP-ALG-01：先跑 Baseline

算法组第一件事不是训练。

先对同一个 Dev / Blind Input 跑：

1. Base Model Zero/Few-shot；
2. 如果公司可用，再跑一个 Generic Model Baseline；
3. 保存完整预测。

交付：

```text
BaselineReport_V0.1.md
baseline_predictions.jsonl
baseline_config.yaml
```

核心心智模型：

`NoBaseline => NoTrainingGain`

---

## WP-ALG-02：Model Task

输入：

```yaml
clause_text: 投标人须在本市注册
business_stage: QUALIFICATION
context: null
```

结构化输出：

```yaml
item_id: C1-01_LOCAL_ENTRY_PRECONDITION

match_state: MATCH

subtype: SUPPLIER_REGISTRATION_LOCATION

evidence_text: 投标人须在本市注册

reasoning_factors:
  - supplier_location_attribute
  - pre_award_condition

confidence: 0.96

human_review_required: false
```

### 重要约束

模型不得输出：

> “该条款违法，依据某某法应处罚……”

因为本Demo任务不是最终法律判断。

---

## WP-ALG-03：训练

第一轮优先：

`SFT + LoRA/QLoRA`

不建议第一轮做CPT。

交付：

```text
training_config.yaml
training_manifest.json
experiment_record.json
adapter/
tokenizer_manifest.json
dev_predictions.jsonl
model_card.md
```

`training_manifest.json` 必须记录：

```yaml
model_version: PCLM-C101-V0.1
base_model: BASE-MODEL-X
dataset_snapshot: C1_01_DatasetSnapshot_V0.1
method: QLoRA
seed: 42
blind_gold_accessed: false
code_version: git-commit-xxx
```

---

# 9. 测试与评测组 Work Package

## WP-QA-01：Benchmark所有权

测试组独立持有：

```text
C1_01_BenchmarkSnapshot_V0.1/
├── blind_test_input.jsonl
├── blind_test_gold.jsonl
├── benchmark_spec.md
├── metric_spec.json
└── manifest.json
```

算法组只允许看到 `blind_test_input.jsonl`。

核心心智模型：

`ModelTeam != BenchmarkOwner`

---

## WP-QA-02：指标

本Demo至少评估：

### Candidate Recall
中文：真正属于C1-01的条款，被模型识别出来的比例。

### Precision
中文：模型判定MATCH的样本中，真正属于C1-01的比例。

### F1
中文：Precision与Recall的综合指标。

### Hard Negative FPR
中文：高相似但实际不属于C1-01的样本被误报为MATCH的比例。

### Evidence Hit Rate
中文：模型输出的证据是否覆盖正确关键文字。

### Counterfactual Consistency
中文：只改变关键业务事实后，模型结论是否正确翻转。

### Structured Output Valid Rate
中文：模型输出是否100%满足Schema。

### NEEDS_CONTEXT Accuracy
中文：信息不足时模型是否愿意不强判。

---

# 10. Demo Gate V0.1

这是 **Demo Gate，不是生产Release Gate**。

建议第一版目标：

| Gate | V0.1目标 |
|---|---:|
| Schema Valid Rate | 100% |
| Train/Test Leakage | 0 |
| Blind Test数量 | ≥50 |
| MATCH Recall | ≥90% |
| Precision | ≥85% |
| Hard Negative FPR | ≤15% |
| Evidence Hit Rate | ≥90% |
| Counterfactual Consistency | ≥90% |
| F1相对Base Model提升 | ≥8个百分点 |

规则：

> 如果 Baseline 结果显示阈值明显不合理，只能在 **Blind Gold未打开之前** 由项目负责人 + 测试负责人冻结新Gate；不能看完结果后为了通过而改门槛。

---

# 11. 测试最终交付

```text
EvaluationReport_V0.1.html
EvaluationMetrics_V0.1.json
ErrorAnalysis_V0.1.md
GateDecision_V0.1.json
RegressionCaseSeed_V0.1.jsonl
```

`GateDecision` 示例：

```json
{
  "model_version": "PCLM-C101-V0.1",
  "benchmark_snapshot": "C1_01_BenchmarkSnapshot_V0.1",
  "decision": "PASS_DEMO",
  "not_production_ready": true,
  "blocking_issues": [],
  "next_action": "进入C1-02或扩大C1-01数据"
}
```

---

# 12. 四组之间的正式交付链

```text
业务组
BR_C1_01_Business_Task_Spec_V0.1
C1_01_Label_Guide_V0.1
C1_01_InternalSilver_CasePack_V0.1
        ↓ FROZEN

数据工程组
C1_01_Dataset_Schema_V0.1
C1_01_DatasetSnapshot_V0.1
DataQualityReport
LeakageReport
        ↓ FROZEN

算法组
BaselineReport
PCLM-C101-V0.1
TrainingManifest
CandidatePredictions
        ↓ CANDIDATE

测试与评测组
BenchmarkSnapshot
EvaluationReport
ErrorAnalysis
GateDecision
        ↓

PASS_DEMO / FAIL_DEMO
```

---

# 13. 交付状态

所有交付物统一状态：

```text
DRAFT
→ IN_REVIEW
→ CHANGES_REQUESTED / APPROVED
→ FROZEN
→ SUPERSEDED
```

算法模型另加：

```text
CANDIDATE
→ PASS_DEMO / FAIL_DEMO
```

`FROZEN` 才允许作为下游正式依赖。

---

# 14. 第一轮10个工作日建议

| 工作日 | 业务/产品 | 数据工程 | 算法 | 测试/评测 |
|---|---|---|---|---|
| D1 | 冻结BusinessTaskSpec、LabelGuide V0.1 | 定Dataset Schema | 建Baseline Harness | 定Benchmark Spec和指标 |
| D2-D3 | 收集/标注第一批案例 | 解析、清洗、去重 | 跑Base Model Baseline | 建Blind Set框架 |
| D4 | 边界案例/Counterfactual补齐 | Leakage Group、Split | 分析Baseline错误 | 冻结Blind Gold |
| D5 | CasePack V0.1冻结 | DatasetSnapshot冻结 | 冻结训练配置 | Data/Benchmark交叉检查 |
| D6-D7 | 支持标签争议 | 修数据问题 | LoRA/QLoRA训练、Dev评测 | 准备自动评分 |
| D8 | 不修改Blind Gold | 支持回放 | Candidate Model冻结 | Blind Benchmark |
| D9 | 参加错误分析 | 数据问题归因 | 模型错误归因 | Evaluation + Error Analysis |
| D10 | Demo业务验收 | 数据验收 | 模型交付 | Gate Decision |

---

# 15. 项目负责人检查清单

在允许算法组正式训练前，我必须确认：

- [ ] C1-01业务范围已冻结；
- [ ] LabelGuide已冻结；
- [ ] 至少有Positive / Hard Negative / Missing Context / Counterfactual；
- [ ] Dataset Schema已冻结；
- [ ] Blind Benchmark已经从训练数据隔离；
- [ ] Leakage Group已完成；
- [ ] Baseline已经运行；
- [ ] 算法组没有Blind Gold访问权限。

在Demo验收时，我必须确认：

- [ ] 模型不是靠关键词“本地/分公司”硬匹配；
- [ ] Hard Negative没有大规模误报；
- [ ] Counterfactual能够正确翻转；
- [ ] Evidence输出正确；
- [ ] 结果相对Base Model有明确提升；
- [ ] 失败样本已经进入Regression Seed；
- [ ] 文档中明确写着 `INTERNAL_SILVER != GOLD`；
- [ ] 文档中明确写着 `PASS_DEMO != PRODUCTION_READY`。

---

# 16. Demo完成后的下一步

如果 `PASS_DEMO`：

优先顺序不自动扩成全部22项，而是召开Demo Review，决定：

1. 继续扩大C1-01数据，提高边界稳定性；
2. 进入第1类第2项；
3. 把第1类两项一起形成Category-1模型切片；
4. 再决定是否扩到第2类。

核心心智模型：

`OneItemPipelineFirst > TwentyTwoItemsChaos`

中文：先把一个具体规则的全流程跑通，再复制工程模式，比一开始同时铺开22项更可靠。

---

# 17. 本Demo的正式定义

`PCLM-C101-V0.1`

中文：

> **政府采购合规模型第1类第1项最小Demo版本。**

它证明的不是：

> “公司已经有生产级政府采购合规模型”。

它只需要证明三件事：

1. 四个小组能按统一Contract并行协作；
2. 一条具体政府采购业务规则可以完整转化为数据、训练和Benchmark；
3. 领域微调模型在这一冻结任务上，相比Base Model出现可重复、可度量的改进。

如果这三件事成立，才有资格复制到后续21项。
