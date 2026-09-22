# C1-01 Data Contract Freeze Record V0.2

## 1. Freeze identity

| 项目 | 值 |
|---|---|
| Contract | `C1-01_LOCAL_ENTRY_PRECONDITION` |
| Frozen artifact | `C1_01_Dataset_Schema_V0.2.json` |
| Schema version | `0.2` |
| Freeze status | `FROZEN_FOR_DATA_ENGINEERING_HANDOFF` |
| Freeze date | `2026-09-22` |
| Change class | Breaking structural change from V0.1 |
| Label authority | `INTERNAL_SILVER` |
| Upstream semantic owner | 01-业务组 |
| Data contract owner | 02-数据工程组 |
| Blind gold owner | 测试与评测组 |

本记录冻结的是数据结构、生命周期和机器闸门。它不把内部 Silver 标注提升为 Gold，也不把 `FROZEN_FOR_DATA_ENGINEERING_HANDOFF` 解释为生产就绪。

## 2. Frozen hashes

以下哈希是本次交付批次的审计锚点。只要 Schema 或 validator 内容变化，就必须生成新版本或新快照，不能静默替换。

| Artifact | SHA-256 |
|---|---|
| `C1_01_Seed_Cases_V0.1.jsonl`（本次重验证输入） | `fa3db35e81e259eb3c406ca12bbead9ba18b4cb87316acf5c5916539d75f067e` |
| `C1_01_Dataset_Schema_V0.2.json` | `484cb50e52e337d24cd014db9ddf1af98d5d82fee9706c512307bb8190da25fb` |
| `validate_sample.py` | `f8a8431419814965b0cc35926ec0ab559fe87729cd232f3cd4790a34f46e3c22` |
| `C1_01_Seed_Cases_Revalidated_V0.2.jsonl` | `a63fdb8cb103c17600c43f121bdc5137c48eb5f75d82a44aeb996a647dbbea04` |
| `C1_01_Seed_Cases_Revalidation_Report_V0.2.json` | `849e54c8eb2d37d4862aa460aef0b32690c049f50aadeaa213fd3ed603fb11c4` |
| `C1_01_Seed_Cases_Revalidation_Report_V0.2.md` | `4c4ece3bbe47610721c9e95a1ab7110e1d52c7f03395f8dde3cbb0e2306f21bd` |
| `C1_01_Dataset_Schema_ChangeLog_V0.2.md` | `5667dc8805157a6b705dd83d4f582b9a211ab386efd21c186acbd8acb1a350cf` |

## 3. Frozen invariants

### 3.1 Annotation lifecycle

```text
annotation_state=LABELED
  → target is an object
  → target.match_state ∈ {MATCH, NO_MATCH, NEEDS_CONTEXT}

annotation_state=UNAVAILABLE_SOURCE_REWORK
  → target=null
  → parser_quality=UNCERTAIN
  → source_defect_prevents_judgment=true
  → data_eligibility=REWORK_SOURCE
  → dataset_role∉{TRAIN, DEV, BLIND_GOLD}
```

### 3.2 Business label invariants

- `MATCH` 必须有非 `NONE` subtype；
- `NO_MATCH` 必须是 `NONE`；
- `NEEDS_CONTEXT` 必须保留 target、至少一个 `missing_context_question`，且 `human_review_required=true`；
- `NEEDS_CONTEXT` 只表示原文可靠而业务事实不足；不能接收 OCR、表格结构或原件缺失；
- `review_state=DISPUTED` 强制 `data_eligibility=HOLD`；
- `TRAIN/DEV` 只允许 `TRAIN_ELIGIBLE`；`BLIND_GOLD` 只允许 `BENCHMARK_CANDIDATE`。

### 3.3 Evidence and provenance invariants

- evidence span 采用 `[start_char, end_char)`，必须等于原始 clause/context 的连续子串；
- span 和 ref 必须一一对应并指向同一文档版本、页码和章节；
- 可训练或 Benchmark candidate 必须是逐字采购文件来源，具有 source SHA-256、可核对定位和 VERIFIED evidence；
- `OFFICIAL_CASE_PARAPHRASE` 与 `SYNTHETIC` 保持非逐字来源身份，不能自动进入训练或盲测候选。

## 4. Revalidation gate result

本次使用当前 29 条种子输入全量运行：

| Gate | 结果 |
|---|---|
| Schema Validation | PASS，29/29 |
| Cross-field Validation | PASS，29/29 |
| Evidence Substring Validation | PASS；当前种子均未核验逐字证据，0 条进入 evidence span 检查 |
| Source Traceability | PASS；29 条均可追溯到 seed snapshot，采购文件逐字核验 0 条 |
| Pair Integrity | PASS，3 组 pair 均同 leakage group |
| Leakage Group Integrity | PASS；当前没有分配 train/dev/blind role |
| Eligibility Validation | PASS |
| Dataset Role Validation | PASS；TRAIN/DEV/BLIND_GOLD 均为 0 |
| Parse Failure Isolation | PASS，1 条 source-rework 记录 target=null |

重点行：

- `C101-SEED-03`：`LABELED`、暂定 `MATCH/OTHER_RELATED`、`DISPUTED/HOLD`、`UNASSIGNED`；保留 target 供审计，不得入训练或盲测。
- `C101-SEED-21`：`UNAVAILABLE_SOURCE_REWORK`、`target=null`、`parser_quality=UNCERTAIN`、`REWORK_SOURCE`、`UNASSIGNED`；历史 `NEEDS_CONTEXT` 不进入监督 target。

## 5. Required downstream behavior

1. Baseline Harness 读取 `annotation_state`，跳过 source-rework 的 target loss；记录 skip reason。
2. Dataset split 先按 `project/template/leakage_group_id`，再分配角色；pair 不跨 split。
3. Benchmark 评测分母排除 `UNAVAILABLE_SOURCE_REWORK`；source repair 后重新标注并生成新快照。
4. Blind gold 由测试与评测组独占；算法组只接收 blind input。
5. 若上游 BusinessTaskSpec 或 LabelGuide 改变 Requirement 粒度、三分类、subtype 或例外边界，必须新建 Schema/Benchmark 版本并更新 Traceability Matrix。

## 6. Acceptance record

| 责任方 | 本轮验收事实 | 状态 |
|---|---|---|
| 01-业务组 | 已完成 C1-01 业务边界裁决；SEED-03 的暂定标签和 SEED-21 的源件修复状态可被数据契约表达 | READY_FOR_DATA_HANDOFF |
| 02-数据工程组 | V0.2 Schema、validator、29 条重验证、变更日志、哈希和本冻结记录完成 | FROZEN_FOR_DATA_ENGINEERING_HANDOFF |
| 算法组 | 需按 V0.2 读取 nullable target 和 annotation_state | PENDING_DOWNSTREAM_ACK |
| 测试与评测组 | 需按 V0.2 更新 blind gold 入库闸门 | PENDING_DOWNSTREAM_ACK |

下游签署完成前，数据工程组不把任何当前种子行升级到 TRAIN、DEV 或 BLIND_GOLD。
