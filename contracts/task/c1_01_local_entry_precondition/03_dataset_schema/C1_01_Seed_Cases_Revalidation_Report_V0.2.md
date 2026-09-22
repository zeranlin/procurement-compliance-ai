# C1-01 Seed Cases Revalidation Report V0.2

**Status：REVALIDATED；数据仍不可直接训练。** 本报告使用当前 Library 中的 29 条 Seed Cases，按 V0.2 Schema 和 validator 全量重跑。

- Seed input：`C1_01_Seed_Cases_V0.1.jsonl`（29 条）
- Schema：`C1_01_Dataset_Schema_V0.2.json`
- Schema SHA-256：`484cb50e52e337d24cd014db9ddf1af98d5d82fee9706c512307bb8190da25fb`
- 运行口径：Schema Validation、Cross-field Validation、Evidence Substring、Source Traceability、Pair Integrity、Leakage Group Integrity、Eligibility、Dataset Role、Parse Failure Isolation

## 1. 全量结果

| 指标 | 结果 |
|---|---:|
| 总记录 | 29 |
| Schema Valid | 29/29 |
| Cross-field Valid | 29/29 |
| LABELED | 28 |
| UNAVAILABLE_SOURCE_REWORK | 1 |
| MATCH | 12 |
| NO_MATCH | 12 |
| NEEDS_CONTEXT | 4 |
| target=null | 1 |
| DISPUTED | 1 |
| REWORK_SOURCE | 1 |
| HOLD | 28 |
| TRAIN / DEV / BLIND_GOLD | 0 / 0 / 0 |

结论：29 条均通过 V0.2 结构验证；其中 28 条是有 target 但尚未完成采购文件逐字来源与证据核验的 `LABELED/HOLD`，1 条为 `UNAVAILABLE_SOURCE_REWORK/target=null/REWORK_SOURCE`。没有任何记录进入 TRAIN、DEV 或 BLIND_GOLD。

## 1.1 自动化检查项

| 检查 | 状态 | 统计 |
|---|---|---:|
| schema_validation | PASS | 29 |
| cross_field_validation | PASS | 29 |
| evidence_substring_validation | PASS | 0 |
| source_traceability | PASS | - |
| pair_integrity | PASS | 3 |
| leakage_group_integrity | PASS | 0 |
| eligibility_validation | PASS | - |
| dataset_role_validation | PASS | - |
| parse_failure_isolation | PASS | 1 |

## 2. 关键边界验收

| Seed | annotation_state | target | review_state | data_eligibility | 结果 |
|---|---|---|---|---|---|
| C101-SEED-03 | LABELED | MATCH | DISPUTED | HOLD | 通过 |
| C101-SEED-21 | UNAVAILABLE_SOURCE_REWORK | null | INTERNAL_REVIEWED | REWORK_SOURCE | 通过 |

- `C101-SEED-03`：保留业务裁决后的 `MATCH/OTHER_RELATED` 作为暂定 target，但由于标签从 proposed_label 发生变化且没有独立人工双人复核，升级为 `DISPUTED/HOLD`；不会进入训练或盲测。
- `C101-SEED-21`：`PARSE_FAILURE` 进入 `UNAVAILABLE_SOURCE_REWORK`，`parser_quality=UNCERTAIN`，`target=null`，`data_eligibility=REWORK_SOURCE`，`dataset_role=UNASSIGNED`。其历史 `proposed_label=NEEDS_CONTEXT` 不进入监督 target。

## 3. 每条记录

| Seed | Schema | Cross-field | Annotation | Target | Review | Eligibility | Role | Blockers |
|---|---|---|---|---|---|---|---|---|
| C101-SEED-01 | PASS | PASS | LABELED | MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-02 | PASS | PASS | LABELED | NO_MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-03 | PASS | PASS | LABELED | MATCH | DISPUTED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-04 | PASS | PASS | LABELED | NO_MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-05 | PASS | PASS | LABELED | NO_MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-06 | PASS | PASS | LABELED | MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-07 | PASS | PASS | LABELED | MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-08 | PASS | PASS | LABELED | MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-09 | PASS | PASS | LABELED | MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-10 | PASS | PASS | LABELED | MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-11 | PASS | PASS | LABELED | MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-12 | PASS | PASS | LABELED | MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-13 | PASS | PASS | LABELED | NO_MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-14 | PASS | PASS | LABELED | NO_MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-15 | PASS | PASS | LABELED | NO_MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-16 | PASS | PASS | LABELED | NO_MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-17 | PASS | PASS | LABELED | NO_MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-18 | PASS | PASS | LABELED | NO_MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-19 | PASS | PASS | LABELED | NEEDS_CONTEXT | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-20 | PASS | PASS | LABELED | NEEDS_CONTEXT | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-21 | PASS | PASS | UNAVAILABLE_SOURCE_REWORK | null | INTERNAL_REVIEWED | REWORK_SOURCE | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-22 | PASS | PASS | LABELED | NEEDS_CONTEXT | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-23 | PASS | PASS | LABELED | NEEDS_CONTEXT | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-24 | PASS | PASS | LABELED | MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-25 | PASS | PASS | LABELED | NO_MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-26 | PASS | PASS | LABELED | MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-27 | PASS | PASS | LABELED | NO_MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-28 | PASS | PASS | LABELED | MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |
| C101-SEED-29 | PASS | PASS | LABELED | NO_MATCH | INTERNAL_REVIEWED | HOLD | UNASSIGNED | 来源/证据未核验或尚未分配数据角色 |

## 4. 下一步入库门槛

1. 对 28 条 `LABELED/HOLD` 补齐采购文件逐字条款、页码和连续证据；证据未核验前不得升 `TRAIN_ELIGIBLE` 或 `BENCHMARK_CANDIDATE`。
2. 对 `C101-SEED-03` 完成独立人工双人复核或形成正式边界裁决记录；在此之前保持 `DISPUTED/HOLD`。
3. 对 `C101-SEED-21` 调取原 PDF 和完整附表，修复后重新解析、拆分、标注；不得直接把历史 `NEEDS_CONTEXT` 当监督标签。
4. 测试组继续独占 blind gold；项目／模板和 pair 不得跨 split。
