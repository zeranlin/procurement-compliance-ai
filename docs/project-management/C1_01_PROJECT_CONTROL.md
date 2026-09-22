# C1-01 PROJECT CONTROL

> **Single Source of Truth / 项目唯一总控入口**  
> 项目：ProcurementComplianceLM  
> 任务：`C1-01_LOCAL_ENTRY_PRECONDITION`  
> 中文：第1类-第1项——外地企业进入本地市场前置限制识别  
> 当前版本：`PROJECT_CONTROL_V0.1`  
> 当前日期：`2026-09-22`

> 算法协议当前冻结实现：`C1_01_Baseline_Protocol_V0.2`；对应指标接口：`C1_01_Benchmark_Metric_Spec_V0.2`；依赖锁与回归证据见 `04_baseline_protocol/C1_01_Baseline_Protocol_Freeze_Record_V0.2.1.md`。

---

## 0. 10 秒状态总览

```text
Project Status:
INTEGRATION_FREEZE

Current Owner:
04 - QA / Benchmark Team

Current Task:
Cross-Team Contract Verification

Current Position:
[业务 ✅] → [数据 ✅] → [算法 ✅] → [测试最终验收 ▶]
→ [Final Freeze ⏳] → [Base Model ⏸] → [Fine-tune ⏸]
→ [Blind Test ⏸] → [Demo Gate ⏸]

Next Gate:
C1-01 END-TO-END CONTRACT FROZEN

Formal Model Run:
BLOCKED

Blocking Reason:
Final Cross-Team Freeze 尚未签署
```

### 当前结论

| 项目 | 状态 |
|---|---|
| 01 业务组整改 | ✅ DONE |
| 02 数据工程组整改 | ✅ DONE |
| 03 算法组整改 | ✅ DONE |
| 04 测试与评测组最终验收 | ▶ CURRENT |
| 项目负责人 Final Freeze Review | ⏳ PENDING |
| `C1-01 END-TO-END CONTRACT FROZEN` | ⏳ PENDING |
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
| P3 | Benchmark Governance | 验证六资产兼容、Blind 权限、Freeze Manifest | 04 测试组 | ▶ CURRENT | Cross-Team Verification PASS |
| P4 | Final Contract Freeze | 13 项 Freeze Gate 总验收 | 项目负责人 | ⏳ PENDING | `C1-01 CONTRACT FROZEN` |
| P5 | Base Model Baseline | Zero-shot / Few-shot / DEV Benchmark | 03 + 04 | ⏸ BLOCKED | Baseline Report |
| P6 | Training Decision | 判断是否进入 SFT / LoRA / QLoRA | 项目负责人 | ⏸ BLOCKED | Fine-tune Decision |
| P7 | Candidate Model | 训练、版本、实验追踪、回归 | 03 算法组 | ⏸ BLOCKED | Candidate Release |
| P8 | Blind Benchmark | 隔离评测、Error Analysis | 04 测试组 | ⏸ BLOCKED | Blind Evaluation Complete |
| P9 | Demo Gate | 硬 Gate + 阻塞项审查 | PM + QA | ⏸ BLOCKED | PASS_DEMO / FAIL_DEMO |

---

# 3. 四个小组状态

## 01 - 业务组 / 产品组

**状态：✅ DONE / WAIT_FOR_INTEGRATION_FEEDBACK**

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
WAIT_FOR_INTEGRATION_FEEDBACK
```

除非 QA 发现真实业务契约冲突，否则不重新打开业务口径。

---

## 02 - 数据工程组

**状态：✅ DONE / WAIT_FOR_INTEGRATION_FEEDBACK**

已完成：

- Dataset Target 生命周期整改；
- 支持 `annotation_state`；
- 支持 Source Rework 与业务已标注记录分流；
- `REWORK_SOURCE → target=null`；
- `REWORK_SOURCE` 不得进入 TRAIN / DEV / BLIND_GOLD；
- `DISPUTED → HOLD`；
- Seed / affected data 重新验证；
- Schema / Validator / Data Contract 更新。

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
WAIT_FOR_INTEGRATION_FEEDBACK
```

---

## 03 - 算法组

**状态：✅ DONE / WAIT_FOR_QA**

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
WAIT_FOR_QA_COMPATIBILITY_VERIFICATION
```

---

## 04 - 测试与评测组

**状态：▶ CURRENT OWNER**

当前必须完成：

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
| A3 | `C1_01_Dataset_Schema` | 02 | ✅整改完成 | QA 确认实际 frozen version + sha256 |
| A4 | `C1_01_Baseline_Protocol_V0.2` | 03 | ✅整改完成 | QA 确认实际 frozen version + sha256 |
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
| T14 | Train / Benchmark Leakage = 0 | 待 QA 最终验收 |
| T15 | Invalid Prediction 不得静默删除 | ✅ |
| T16 | Blind Gold QA 独占 | 待权限回归测试 |
| T17 | 六资产 version/hash 全锁定 | 待 QA |
| T18 | 无 Open P0 Integration Issue | 待 QA |

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
| G3 | Dataset schema frozen | ✅整改完成 / 待 QA确认 |
| G4 | ParseFailure isolated | ✅ |
| G5 | Baseline protocol frozen | ✅整改完成 / 待 QA确认 |
| G6 | Benchmark metric frozen | ✅ |
| G7 | Blind test rules frozen | ✅ |
| G8 | Gold access boundary verified | ⏳ |
| G9 | All six asset hashes pinned | ⏳ |
| G10 | Seed / affected data revalidated | ✅ |
| G11 | No DISPUTED enters Train/Dev | ✅ / 待 QA回归 |
| G12 | No REWORK_SOURCE enters Train/Blind | ✅ / 待 QA回归 |
| G13 | No known P0 integration issue | ⏳ |

当前：

```text
FINAL FREEZE = NOT YET APPROVED
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
BASELINE_EXECUTION
```

---

# 8. Baseline Execution 解锁后的任务

Contract Frozen 后，严格按以下顺序：

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
| BLK-01 | QA Cross-Team Compatibility Verification 未完成 | 04 | P0 | ▶ OPEN |
| BLK-02 | Gold Access Boundary Regression 未完成 | 04 | P0 | ▶ OPEN |
| BLK-03 | Six-Asset Freeze Manifest 未最终锁定 | 04 | P0 | ▶ OPEN |
| BLK-04 | PM Final Freeze Review 未执行 | PM | P0 | WAITING |

当前无已知业务 / 数据 / 算法组 P0 blocker。

---

# 13. Current Next Actions

## 当前唯一主责

```text
Owner:
04 - QA / Benchmark Team
```

必须依次完成：

```text
1. Benchmark Eligibility Validation
2. Metric / Schema Compatibility Test
3. Freeze Manifest
4. Access Boundary Regression
5. Traceability Verification
6. 提交 QA Final Package
```

之后：

```text
Project Manager
    ↓
Final Freeze Review
    ↓
G1 ~ G13
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

---

# 18. 项目负责人当前判定

```text
C1-01 STATUS:
INTEGRATION_FREEZE

01 Business:
DONE

02 Data:
DONE

03 Algorithm:
DONE

04 QA:
IN_PROGRESS

FORMAL MODEL BENCHMARK:
NOT AUTHORIZED

NEXT PROJECT DECISION:
FINAL FREEZE REVIEW

TARGET:
C1-01 END-TO-END CONTRACT FROZEN
```
