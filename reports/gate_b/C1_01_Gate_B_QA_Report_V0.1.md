# C1-01 Gate-B QA Report V0.1

**项目**：ProcurementComplianceLM
**任务**：C1-01_LOCAL_ENTRY_PRECONDITION
**Owner**：04-测试与评测组
**验证时间**：2026-09-23
**状态**：`GATE-B_BLOCKED_READINESS_GAP`

## 1. 结论

Gate-B 的流程、输入资格闸门、合成评测、ID 对齐、INVALID 分母和 ACL 拒绝探针已具备可执行证据；真实数据规模尚未就绪，不能宣称 `Benchmark Ready`，不能宣称 Gate-B PASS。

```text
Contract Ready    = true   （Gate-A 已冻结）
Benchmark Ready   = false
Gate-B            = BLOCKED_READINESS_GAP
Blind Gold        = 未生成、未进入 Git
正式模型/盲测     = 未运行
```

## 2. 02 组 Data Readiness Pilot 复核

输入来源：`codex/c1-01-gate-b-data-readiness`，commit `f018855769d435471468a97267d6fa6c0ace5543`；Data Manifest SHA-256：`d5373c907aff721319c91c0ab10e3f729837a6688fc0fc9ee04f26c052850556`。

| 检查项 | 预期/门槛 | 实际 | 结论 |
|---|---:|---:|---|
| V0.2 Schema/cross-field | 全部通过 | 3/3、3/3 | PASS |
| Internal Silver candidate | 记录数 | 3 | 仅 Pilot |
| TRAIN | ≥ 300 | 0 | BLOCKED |
| DEV | ≥ 80 | 0 | BLOCKED |
| Review state | 可入候选需 INTERNAL_REVIEWED | 3×PENDING_SECOND_PASS | BLOCKED |
| Eligibility | 可入候选需 BENCHMARK_CANDIDATE | 3×HOLD | BLOCKED |
| Source coverage | 多独立采购项目 | 1 个来源、3 条 clause | BLOCKED |
| Leakage | 不跨 split | duplicate=0、pair 跨 split=0 | PASS（仅 Pilot） |
| Blind Gold | 不读取 | `NOT_READ` | PASS |

04 QA 用当前分支的 `validate_sample.py` 和 `benchmark_snapshot.py` 对 02 组 Internal Silver 重新执行：Schema 3/3、cross-field 3/3；DEV=0、Blind=0，全部被 Assembly 拒绝，未生成 Gold。

## 3. Assembly 输入契约

只有同时满足以下条件的记录才允许进入 DEV/Blind Snapshot：

```text
annotation_state = LABELED
target != null
parser_quality = PASS
source_defect_prevents_judgment = false
review_state = INTERNAL_REVIEWED
source_kind = PROCUREMENT_DOCUMENT
source_verified_at_procurement_document_level = true
evidence_status = VERIFIED
DEV  -> data_eligibility=TRAIN_ELIGIBLE, dataset_role=DEV
Blind -> data_eligibility=BENCHMARK_CANDIDATE, dataset_role=BLIND_INPUT/BLIND_GOLD
```

`HOLD`、`PENDING_SECOND_PASS`、`DISPUTED`、`REWORK_SOURCE`、`target=null` 均在 Assembly 层拒绝，不生成模型请求，不进入评分分母。

实际 readiness manifest：

[`C1_01_Gate_B_Readiness_V0.1/manifest.json`](../../datasets/snapshots/c1_01_gate_b/C1_01_Gate_B_Readiness_V0.1/manifest.json)

结果：`source_record_count=29`、`DEV=0`、`BLIND_INPUT=0`、`gold_exported=false`、`benchmark_ready=false`。

## 4. 可执行流程和合成回归

### 4.1 已验证 PASS

- 合成输入包含 `MATCH`、`NO_MATCH`、`NEEDS_CONTEXT`。
- 覆盖四个 MATCH subtype：`SUPPLIER_REGISTRATION_LOCATION`、`DISTANCE_TO_PURCHASER`、`PREEXISTING_LOCAL_BRANCH`、`OTHER_RELATED`。
- 覆盖 Hard Negative 和 Counterfactual Pair。
- 预测缺失、重复、未知 `sample_id` 均返回 `INVALID_SUBMISSION`。
- 1 条 INVALID prediction 保留记录并计入结构化输出分母；12 条合成输入的有效率为 `11/12`。
- 算法可读 `blind_test_input`，QA 隔离评测账号可读 Gold；Algorithm/Business/Data/PM/Ops 读取 Gold 均被拒绝。
- 审计日志不含 Gold 明文。

证据：

- `reports/gate_b/C1_01_Gate_B_Evaluator_Regression_V0.1.json`
- `reports/gate_b/C1_01_Gate_B_Access_Boundary_Regression_V0.1.json`
- `tests/fixtures/gate_b/C1_01_Synthetic_Blind_Input_V0.1.jsonl`

### 4.2 明确不是 PASS 的项目

- 合成 12 条不是正式 Benchmark，不能替代真实 `N>=50`。
- 当前没有真实 `blind_test_input.jsonl` 或 `blind_test_gold.jsonl`。
- 生产 IAM/service account、对象存储 ACL、真实隔离 evaluator 和线上审计管道尚未部署；当前 ACL 是可执行 policy harness 和回归探针。
- 未运行正式 Base Model、DEV Benchmark 或 Blind Benchmark。

## 5. Readiness Gap / Owner / Required Fix

| ID | 缺口 | Owner | Required Fix |
|---|---|---|---|
| GB-DATA-001 | TRAIN=0、DEV=0；仅 3 条待二审 Silver | 02 数据工程组 | 完成独立人工二审，扩充多采购项目来源，按 V0.2 重新分配资格和 split |
| GB-DATA-002 | 仅 1 个公开来源，缺少正例、四 subtype、NEEDS_CONTEXT、Hard Negative、反事实覆盖 | 02 数据工程组 + 01 业务组 | 补齐来源和边界案例，保持 `leakage_group_id`/pair 不跨 split |
| GB-DATA-003 | Blind N=0，距离 N>=50 缺口 50 | 02 数据工程组 + 04 测试组 | 真实候选满足资格后再组装 Snapshot；不得用合成样本冒充正式规模 |
| GB-RUNTIME-001 | 生产运行时 ACL/evaluator 未部署 | 平台/运维 + 04 测试组 | 部署 QA-only service account、拒绝探针、审计日志和隔离 evaluator，再做运行时回归 |

## 6. Gate-B 判定

```text
GATE-B_BLOCKED_READINESS_GAP
```

本报告不修改 Gate-A、不降低任何阈值、不创建 Gold、不运行正式盲测。待上述数据规模和运行时隔离缺口关闭后，必须用新的 Snapshot ID、输入/Gold 哈希、evaluator 版本和审计记录重新验收。
