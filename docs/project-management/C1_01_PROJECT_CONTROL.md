# C1-01 PROJECT CONTROL

> **Single Source of Truth / 项目唯一总控入口**  
> 项目：ProcurementComplianceLM  
> 任务：`C1-01_LOCAL_ENTRY_PRECONDITION`  
> 中文：第1类-第1项——外地企业进入本地市场前置限制识别  
> 当前版本：`PROJECT_CONTROL_V0.1`  
> 当前日期：`2026-09-23`

> 算法协议当前冻结实现：`C1_01_Baseline_Protocol_V0.2.1`；对应指标接口：`C1_01_Benchmark_Metric_Spec_V0.2`（SHA-256：`cb443a...`）；依赖锁与 Gate-A 回归证据见 `04_baseline_protocol/protocol/`、`04_baseline_protocol/harness/` 及 `05_benchmark_metric_spec/deliverables/`。

---

## 0. 10 秒状态总览

```text
Project Status:
GATE_B_PREPARATION_WITH_DEFERRED_REVIEW

Current Owner:
项目负责人 + 02/03/04 工作流 Owner

Current Task:
Gate-B 准备继续；候选逐条复核工作项按 Owner 决策延期关闭

Current Position:
[业务 ✅] → [数据 ✅] → [算法 ✅] → [测试最终验收 ✅]
→ [Final Freeze ✅ GATE-A_COMPLETE] → [Gate-B Readiness ▶ REVIEW_DEFERRED]
→ [Base Model ⏸] → [Fine-tune ⏸]
→ [Blind Test ⏸] → [Demo Gate ⏸]

Next Gate:
GATE-B DATA / BENCHMARK READINESS

Formal Model Run:
BLOCKED

Blocking Reason:
402 条候选尚未逐条复核、专家二审延期、6 个旧版文档解析阻塞；Gate-B 其他数据、Snapshot、ACL、Evaluator 和环境证据也未完成
```

### 当前结论

| 项目 | 状态 |
|---|---|
| 01 业务组整改 | ✅ DONE |
| 02 数据工程组整改 | ▶ GATE_B_DATA_PREP |
| 03 算法组整改 | ▶ GATE_B_ENVIRONMENT_PREP |
| 04 测试与评测组最终验收 | ▶ GATE_B_SNAPSHOT_ACL_PREP |
| 项目负责人 Final Freeze Review | ✅ COMPLETE |
| `C1-01 END-TO-END CONTRACT FROZEN` | ✅ GATE-A_COMPLETE |
| Gate-B Data / Benchmark Readiness | ▶ PREPARATION_WITH_DEFERRED_REVIEW |
| 候选逐条 Codex 暂代复核工作项 | ✅ COMPLETE_WITH_DEFERRED_REVIEW |
| 已复核 / 待复核候选 | 1 / 402 |
| 人工专家二审 | ⏸ DEFERRED_UNTIL_EXPERT_TEAM_ONBOARDING |
| 旧版文档解析阻塞 | 6 / PARSER_BLOCKED |
| `benchmark_ready` | ❌ FALSE |
| `training_authorized` | ❌ FALSE |
| 正式 Base Model Benchmark | ⏸ BLOCKED |
| Fine-tune | ⏸ BLOCKED |
| Blind Benchmark | ⏸ BLOCKED |
| Demo Gate | ⏸ BLOCKED |

---

# 1. 项目目标

本项目当前不铺开完整 7 类 22 项，而是先完成 C1-01 单项完整闭环：

```text
业务定义
    ↓
Label Guide
    ↓
Dataset Contract
    ↓
Baseline Protocol
    ↓
Benchmark Contract
    ↓
Blind Test Governance
    ↓
Base Model Baseline
    ↓
Fine-tune / Candidate Model
    ↓
Blind Benchmark
    ↓
Demo Gate
```

核心策略：

```text
OneItemPipelineFirst > TwentyTwoItemsChaos
ContractFirst > ModelFirst
GoldAsset > OneCheckpoint
```

当前阶段只允许先完成 Contract Freeze，再进入正式模型效果实验。

---

# 2. 项目阶段总控

| Phase | 阶段 | 核心目标 | Owner | 状态 | Exit Gate |
|---|---|---|---|---|---|
| P0 | Business Contract | 冻结任务定义、标签语义、业务边界 | 01 业务组 | ✅ DONE | BusinessTaskSpec + LabelGuide Frozen |
| P1 | Data Contract | 冻结 Dataset 生命周期、资格、Schema、Leakage | 02 数据工程组 | ✅ DONE | DatasetSchema Frozen |
| P2 | Model Protocol | 冻结模型输入、输出、Preflight、版本绑定 | 03 算法组 | ✅ DONE | BaselineProtocol Frozen |
| P3 | Benchmark Governance | 验证六资产兼容、Blind 权限、Freeze Manifest | 04 测试组 | ✅ QA_FINAL_SIGNOFF_PASS | Cross-Team Verification PASS |
| P4 | Final Contract Freeze | 13 项 Freeze Gate 总验收 | 项目负责人 | ✅ GATE-A_COMPLETE | `C1-01 END-TO-END CONTRACT FROZEN` |
| P4.5 | Gate-B Data / Benchmark Readiness | 数据、Snapshot、ACL、Evaluator、模型环境就绪 | 项目负责人 + 02/03/04 | ▶ PREPARATION_WITH_DEFERRED_REVIEW | Gate-B Readiness Review |
| P5 | Base Model Baseline | Zero-shot / Few-shot / DEV Benchmark | 03 + 04 | ⏸ BLOCKED | Baseline Report |
| P6 | Training Decision | 判断是否进入 SFT / LoRA / QLoRA | 项目负责人 | ⏸ BLOCKED | Fine-tune Decision |
| P7 | Candidate Model | 训练、版本、实验追踪、回归 | 03 算法组 | ⏸ BLOCKED | Candidate Release |
| P8 | Blind Benchmark | 隔离评测、Error Analysis | 04 测试组 | ⏸ BLOCKED | Blind Evaluation Complete |
| P9 | Demo Gate | 硬 Gate + 阻塞项审查 | PM + QA | ⏸ BLOCKED | PASS_DEMO / FAIL_DEMO |

---

# 3. 四个小组状态

## 01 - 业务组 / 产品组

**状态：✅ DONE / REVIEW_TASK_COMPLETE_WITH_DEFERRED_REVIEW**

已完成：

- `BusinessTaskSpec` 冻结；
- `LabelGuide` 冻结；
- `ParseFailure != NeedsContext` 正式业务裁决；
- `Missing Business Context != Broken Source`；
- 业务边界争议与 Source Failure 分流；
- 解析失败不得进入普通监督标签；
- 业务边界案例保持 `DISPUTED / HOLD`；
- Source Rework 保持 `REWORK_SOURCE`。

核心不变量：

```text
NEEDS_CONTEXT
=
原文已可靠读取
但业务判断所需信息不足

REWORK_SOURCE / PARSE_FAILURE
=
输入本身不可靠
当前不能形成正式业务标签
```

当前动作：

```text
候选逐条 Codex 暂代复核工作项：COMPLETE_WITH_DEFERRED_REVIEW
已完成暂代复核：1
待复核：402（PENDING_01_CODEX_REVIEW / label=null）
专家二审：DEFERRED_UNTIL_EXPERT_TEAM_ONBOARDING
```

该状态关闭的是本阶段工作项，不代表 402 条样本已复核。除非 QA 发现真实业务契约冲突，否则不重新打开已冻结业务口径；专家团队入驻后按延期台账重开候选复核。

---

## 02 - 数据工程组

**状态：▶ GATE_B_DATA_PREP**

已完成：

- Dataset Target 生命周期整改；
- 支持 `annotation_state`；
- 支持 Source Rework 与业务已标注记录分流；
- `REWORK_SOURCE → target=null`；
- `REWORK_SOURCE` 不得进入 TRAIN / DEV / BLIND_GOLD；
- `DISPUTED → HOLD`；
- Seed / affected data 重新验证；
- Schema / Validator / Data Contract 更新。
- 已形成 403 条本地隔离候选，其中 1 条为 Codex 暂代复核、402 条保持 `PENDING_01_CODEX_REVIEW`；全部 `training_eligible=false`、`expert_signoff=false`、`gold_eligible=false`；
- 已将 402 条候选登记为 `deferred_expert_review_queue`，6 个旧版文档继续单列 `PARSER_BLOCKED`。

目标结构：

```text
annotation_state = LABELED
    ↓
target.match_state
= MATCH / NO_MATCH / NEEDS_CONTEXT
```

```text
annotation_state = UNAVAILABLE_SOURCE_REWORK
    ↓
target = null
parser_quality = UNCERTAIN
data_eligibility = REWORK_SOURCE
```

当前动作：

```text
GATE_B_DATA_PREP
仅继续候选工程、隔离、统计和 Dry-Run 准备
不得把延期候选升级为正式标签或训练数据
```

---

## 03 - 算法组

**状态：▶ GATE_B_ENVIRONMENT_PREP**

已完成：

- Baseline Protocol 升级；
- 绑定已冻结的 Business / Label / Dataset / Metric Contract；
- 正式输入资格检查；
- `REWORK_SOURCE` 不送模型；
- `HOLD / DISPUTED / PENDING_DATA_QA` 阻断；
- Dataset Schema version/hash 校验；
- Preflight Gate；
- Prediction Output Contract；
- 模型输入与 Gold / metadata 隔离。

关键规则：

```text
Invalid Dataset Candidate
!=
Invalid Model Prediction
```

```text
REWORK_SOURCE
→ 不送模型
→ 不评分
→ 不做 few-shot
→ 不做 DEV
```

```text
INVALID Prediction
→ 已进入 Benchmark
→ 保留 sample_id
→ 进入评测分母
```

当前动作：

```text
GATE_B_ENVIRONMENT_PREP
```

---

## 04 - 测试与评测组

**状态：▶ GATE_B_SNAPSHOT_ACL_PREP**

本轮已完成：

### QA-FIX-01
更新 Benchmark Snapshot Eligibility Rule：

```text
parser_quality = PASS
review_state = INTERNAL_REVIEWED
data_eligibility = BENCHMARK_CANDIDATE
target != null
```

明确排除：

```text
REWORK_SOURCE
PARSE_FAILURE
DISPUTED
HOLD
PENDING_DATA_QA
```

### QA-FIX-02
验证新版 DatasetSchema / BaselineProtocol 与 BenchmarkMetricSpec 兼容：

```text
INVALID Prediction
→ Benchmark Runtime Error
→ 保留并处罚
```

```text
REWORK_SOURCE
→ Benchmark Assembly Invalid
→ Freeze 前挡掉
```

### QA-FIX-03
生成新版 Freeze Manifest，锁定六资产版本 + hash。

### QA-FIX-04
执行 Gold Access Boundary Regression Test。

### QA-FIX-05
执行 End-to-End Traceability Verification：

```text
PASS
FAIL
BLOCKED
N/A
```

禁止使用：

```text
基本通过
原则上没问题
大致一致
```

---

# 4. 六资产 Contract Registry

| # | Asset | Owner | 当前状态 | Freeze 要求 |
|---|---|---|---|---|
| A1 | `BR_C1_01_Business_Task_Spec` | 01 | 🔒 FROZEN | version + sha256 |
| A2 | `C1_01_Label_Guide` | 01 | 🔒 FROZEN | version + sha256 |
| A3 | `C1_01_Dataset_Schema` | 02 | 🔒 FROZEN | version + sha256 |
| A4 | `C1_01_Baseline_Protocol_V0.2` | 03 | 🔒 FROZEN | version + sha256 |
| A5 | `C1_01_Benchmark_Metric_Spec_V0.2` | 04 | 🔒 FROZEN | version + sha256 |
| A6 | `C1_01_Blind_Test_Rules / Gold_Access_Boundary` | 04 | 🔒 FROZEN | version + sha256 |

最终 Freeze Manifest 必须至少记录：

```text
asset_name
version
content_sha256
owner
freeze_status
freeze_time
dependency_versions
dependency_hashes
```

任何一项 hash 改变：

```text
原 Snapshot 不得继续声称为同一个 Frozen Snapshot
```

---

# 5. End-to-End Traceability 关键不变量

| ID | Contract | 状态 |
|---|---|---|
| T01 | `Task != FinalViolationJudgment` | ✅ |
| T02 | `Clause != Requirement` | ✅ |
| T03 | `MATCH / NO_MATCH / NEEDS_CONTEXT` 三态统一 | ✅ |
| T04 | `MATCH → subtype != NONE` | ✅ |
| T05 | `NO_MATCH / NEEDS_CONTEXT → subtype = NONE` | ✅ |
| T06 | `NEEDS_CONTEXT → missing_context_questions >= 1` | ✅ |
| T07 | `NEEDS_CONTEXT → human_review_required=true` | ✅ |
| T08 | `ParseFailure != NeedsContext` | ✅ |
| T09 | `REWORK_SOURCE → target=null` | ✅ |
| T10 | `REWORK_SOURCE` 不进入 Train / Dev / Blind | ✅ |
| T11 | `DISPUTED → HOLD` | ✅ |
| T12 | Hard Negative 独立切片 | ✅ |
| T13 | Counterfactual pair 同 leakage group | ✅ |
| T14 | Train / Benchmark Leakage = 0 | ✅ |
| T15 | Invalid Prediction 不得静默删除 | ✅ |
| T16 | Blind Gold QA 独占 | ✅ Gate-A policy；runtime ACL 属 Gate-B |
| T17 | 六资产 version/hash 全锁定 | ✅ |
| T18 | 无 Open P0 Integration Issue | ✅ |

---

# 6. Final Freeze Gate

项目负责人只有在以下 **13 个 Gate 全部 PASS** 时，才能宣布：

```text
C1-01 END-TO-END CONTRACT FROZEN
```

| Gate | 验收项 | 当前 |
|---|---|---|
| G1 | Business semantics frozen | ✅ |
| G2 | Label semantics frozen | ✅ |
| G3 | Dataset schema frozen | ✅ |
| G4 | ParseFailure isolated | ✅ |
| G5 | Baseline protocol frozen | ✅ |
| G6 | Benchmark metric frozen | ✅ |
| G7 | Blind test rules frozen | ✅ |
| G8 | Gold access boundary verified | ✅ |
| G9 | All six asset hashes pinned | ✅ |
| G10 | Seed / affected data revalidated | ✅ |
| G11 | No DISPUTED enters Train/Dev | ✅ |
| G12 | No REWORK_SOURCE enters Train/Blind | ✅ |
| G13 | No known P0 integration issue | ✅ |

当前：

```text
FINAL FREEZE = C1-01 END-TO-END CONTRACT FROZEN / GATE-A_COMPLETE
```

---

# 7. 正式模型实验解锁条件

以下任务目前全部 **BLOCKED**：

```text
Base Model Zero-shot
Base Model Few-shot
DEV Benchmark
Fine-tune
Candidate Model Training
Blind Benchmark
Demo Gate
```

唯一解锁条件：

```text
G1 ~ G13 ALL PASS
        ↓
C1-01 END-TO-END CONTRACT FROZEN
        ↓
Project Status:
GATE_B_DATA_BENCHMARK_READINESS
```

---

# 8. Baseline Execution 解锁后的任务

Gate-B Data / Benchmark Readiness 完成并授权后，才进入 Baseline Execution，严格按以下顺序：

```text
B01 Base Model Zero-shot
    ↓
B02 Base Model Few-shot
    ↓
B03 DEV Benchmark
    ↓
B04 Baseline Report
    ↓
B05 Error Taxonomy
    ↓
B06 Fine-tune Decision
```

不得直接跳到 Fine-tune。

需要回答的核心问题：

```text
Base Model 当前能力到底在哪里？
主要错误来自：
- 业务边界？
- Evidence？
- Abstention？
- Hard Negative？
- Counterfactual？
- Structured Output？
- 数据覆盖？
```

只有 Error Analysis 支持，才进入训练。

---

# 9. Candidate Model / Training 阶段

如 Fine-tune Decision = GO：

```text
T01 Training Dataset Freeze
T02 Training Manifest
T03 SFT / LoRA / QLoRA Experiment
T04 Candidate Checkpoint
T05 Same-DEV Evaluation
T06 General Regression Check
T07 Candidate Selection
T08 Blind Submission Freeze
```

禁止使用 Blind Test 迭代模型。

---

# 10. Blind Benchmark / Demo Gate

Blind 阶段：

```text
Algorithm
    ↓
blind_test_input
    ↓
Prediction Submission
    ↓
QA Isolated Evaluator
    ↑
blind_test_gold
    ↓
Evaluation Report
    ↓
Error Analysis
    ↓
Gate Decision
```

算法组不得访问：

```text
blind_test_gold
hidden slice membership
leakage_groups
sample_id → gold label
逐例 Gold Feedback
```

---

# 11. Demo Gate Thresholds

当前冻结目标：

| Metric / Gate | Target |
|---|---:|
| `structured_output_valid_rate` | 100% |
| Train/Test Leakage | 0 |
| Blind Test N | ≥ 50 |
| `match_recall` | ≥ 90% |
| `match_precision` | ≥ 85% |
| `hard_negative_fpr` | ≤ 15% |
| `evidence_hit_rate` | ≥ 90% |
| `counterfactual_pair_accuracy` | ≥ 90% |
| `match_f1` vs Base Model | ≥ 8 pp |

辅助必报：

```text
needs_context_recall
unnecessary_abstention_rate
match_subtype_accuracy
evidence_overlap_proxy_recall
```

Gate：

```text
ALL HARD CONDITIONS PASS
+
NO BLOCKING ISSUE
```

不是加权总分。

---

# 12. 当前 Blocker Board

| ID | Blocker | Owner | Severity | 状态 |
|---|---|---|---|---|
| BLK-01 | QA Cross-Team Compatibility Verification | 04 | P0 | ✅ PASS |
| BLK-02 | Gold Access Boundary Regression | 04 | P0 | ✅ PASS |
| BLK-03 | Six-Asset Freeze Manifest | 04 | P0 | ✅ LOCKED |
| BLK-04 | 04 QA_FINAL_SIGNOFF / PM Final Freeze Review | 04 / PM | P0 | ✅ SIGNED |
| BLK-05 | 402 条候选未完成逐条业务复核与专家二审 | 专家团队 / 01 / PM | P0（正式数据准入） | DEFERRED_UNTIL_EXPERT_TEAM_ONBOARDING |
| BLK-06 | 6 个旧版文档解析阻塞 | 02 / 01 | P1 | PARSER_BLOCKED |

Gate-A 当前无已知 P0 blocker；Gate-B 正式数据准入存在 `BLK-05`，因此不得声明数据质量、Benchmark Ready 或 Training Authorized PASS。

---

# 13. Current Next Actions

## 当前唯一主责

```text
Owner:
项目负责人 + 02/03/04 工作流 Owner
```

本阶段允许并行继续：

```text
1. 模型与运行环境准备
2. 候选数据工程、去重、分层和队列维护
3. 不使用正式标签权威的 E2E Dry-Run
4. QA isolated evaluator、runtime ACL 和审计准备
```

专家团队入驻后必须依次完成：

```text
1. 重开为 REOPENED_FOR_EXPERT_REVIEW
2. 优先复核高风险、HOLD、冲突与证据不完整候选
3. 执行分层抽样并对问题同层回溯
4. 完成 402 条全量回归；新标签新增版本，不静默覆盖
5. 单列修复并复核 6 个 PARSER_BLOCKED 文档
6. 重跑数据 QA、Schema、leakage、角色资格与 Gate-B 评审
```

之后：

```text
Project Manager
    ↓
Gate-B Readiness Review
    ↓
BASELINE_EXECUTION 授权判断
```

---

# 14. 快速查看规则

以后任何人打开本文件，只需要先看：

```text
0. 10 秒状态总览
3. 四个小组状态
6. Final Freeze Gate
12. Blocker Board
13. Current Next Actions
```

即可快速回答：

```text
现在在哪？
谁负责？
卡在哪里？
下一步是什么？
哪些任务不能开始？
```

---

# 15. 状态枚举

统一使用：

| Status | 含义 |
|---|---|
| `NOT_STARTED` | 尚未开始 |
| `READY` | 上游条件完成，可开始 |
| `IN_PROGRESS` | 当前执行中 |
| `BLOCKED` | 被硬依赖阻塞 |
| `WAITING_REVIEW` | 已完成执行，等待验收 |
| `DONE` | 当前 Work Package 已完成 |
| `FROZEN` | 已成为不可静默修改的正式 Contract |
| `QUARANTINED` | 因缺陷或泄漏暂停使用 |
| `INVALIDATED` | 运行/快照已判无效 |
| `COMPLETE_WITH_DEFERRED_REVIEW` | 本阶段工作项按 Owner 决策关闭，但明确存在未完成逐条复核 |
| `DEFERRED_UNTIL_EXPERT_TEAM_ONBOARDING` | 等待专家团队入驻后重开并执行版本化全量回归 |

禁止使用模糊状态：

```text
差不多完成
基本通过
应该没问题
快好了
```

---

# 16. 更新规则

每次项目发生以下事件，本文件必须同步更新：

```text
Work Package 完成
Contract Freeze
Version Change
Hash Change
Benchmark Snapshot Change
Blocker Open / Close
Gate Decision
Model Run Complete
Training Decision
Blind Test Complete
Release Decision
```

每次更新至少修改：

```text
Current Status
Current Owner
Current Task
Next Gate
Blocker Board
Phase Table
Change Log
```

---

# 17. Change Log

| Date | Version | Change | Owner |
|---|---|---|---|
| 2026-09-22 | PROJECT_CONTROL_V0.1 | 建立 C1-01 项目总控看板；同步 01/02/03 已完成、04 当前主责状态 | Project Manager |
| 2026-09-22 | PROJECT_CONTROL_V0.1 | 02 DATA_SIGNOFF、04 QA_FINAL_SIGNOFF 完成；C1-01 Gate-A 合同冻结，转入 Gate-B Readiness | Project Manager |
| 2026-09-22 | PROJECT_CONTROL_V0.1 | 建立 Gate-B Plan、Readiness Checklist、模型选择记录与最终验收矩阵；保持模型/训练 BLOCKED | Project Manager |
| 2026-09-23 | PROJECT_CONTROL_V0.1 | 记录 Owner 批准的 AI/专家复核延期：1 条已复核、402 条待复核、6 个解析阻塞；允许准备与 Dry-Run，保持 Benchmark/Training 未授权 | Project Manager |

---

# 18. 项目负责人当前判定

```text
C1-01 STATUS:
GATE_B_PREPARATION_WITH_DEFERRED_REVIEW

01 Business:
DONE / REVIEW_TASK_COMPLETE_WITH_DEFERRED_REVIEW

02 Data:
GATE_B_DATA_PREP

03 Algorithm:
GATE_B_ENVIRONMENT_PREP

04 QA:
GATE_B_SNAPSHOT_ACL_PREP

CODEX CANDIDATE REVIEW:
1 REVIEWED / 402 PENDING_01_CODEX_REVIEW

EXPERT REVIEW:
DEFERRED_UNTIL_EXPERT_TEAM_ONBOARDING

PARSER BLOCKED DOCUMENTS:
6

BENCHMARK_READY:
FALSE

TRAINING_AUTHORIZED:
FALSE

FORMAL MODEL BENCHMARK:
NOT AUTHORIZED

NEXT PROJECT DECISION:
GATE-B DATA / BENCHMARK READINESS

TARGET:
C1-01 END-TO-END CONTRACT FROZEN
```
