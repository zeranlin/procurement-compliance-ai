# C1-01 Final Contract Freeze Review V0.1

**任务**：`C1-01_LOCAL_ENTRY_PRECONDITION`  
**复核日期**：2026-09-22  
**候选分支**：`codex/c1-01-final-contract-freeze`  
**技术底座**：`a720a03460a99725f3892ec005ad566cd66a52ec`（03 最终协议 + 04 Gate-A 资产）  
**01 集成提交**：`0751558`（来源 `a7592ec`，仅引入 01 业务专属 6 个文件）  
**02 来源核对**：`83aff9a`；其 9 个数据文件与底座逐字节一致，未重复引入  
**当前结论**：`WAITING_FINAL_SIGNOFF`  

> 本文是项目负责人最终签署前的集成复核记录。`GATE-A_REVERIFY_PASS` 与 `contract_ready=true` 可以引用；在 02 `DATA_SIGNOFF` 和 04 `QA_FINAL_SIGNOFF` 完成前，不宣布 `C1-01 END-TO-END CONTRACT FROZEN`。

## 1. 业务语义最终复核

1. 本任务识别投标前或评分阶段针对外地供应商设置的本地注册、既有分支机构、既有办公/服务地点、与采购人距离等市场准入条件或竞争优势。
2. 中标后服务承诺、响应时限、到场/维修时限，以及履约后再建立服务机制，不属于本项；保持 `NO_MATCH`，除非同时出现独立的投标前本地实体条件。
3. 原文可靠但缺少业务判断事实时使用 `NEEDS_CONTEXT`；OCR、附件、页码或表格结构不可靠时使用 `REWORK_SOURCE` / `PARSE_FAILURE`，不得伪装成 `NEEDS_CONTEXT`。
4. `C101-SEED-03` 保持暂定 `MATCH/OTHER_RELATED`，状态为 `DISPUTED/HOLD`，不进入训练、开发或盲测。
5. `C101-SEED-21` 保持 `REWORK_SOURCE`，`reviewed_label=null`、`target=null`，不进入普通 `NEEDS_CONTEXT`、训练、开发或 `blind_test_gold`。
6. 三组反事实 Pair 保持原有正负标签及 leakage group：`CF01`（24/25）、`CF02`（26/27）、`CF03`（28/29）。
7. 29 条种子没有被集成过程升级为 `TRAIN`、`DEV` 或 `BLIND_GOLD`。

## 2. 正式资产与依赖链

| 资产 | 版本 | SHA-256 | Owner | 集成来源 | 主要依赖 |
|---|---|---|---|---|---|
| BusinessTaskSpec | `BR_C1_01_Business_Task_Spec_V0.1` | `0fa169fa0fa34ef8e702c4cae8e10e89cdce4260aa198f7a45a4a28d5c3a74ab` | 01 业务组 | 底座 `a720a03` | 项目业务边界 |
| LabelGuide | `C1_01_Label_Guide_V0.1` | `9b6352b5f6e400f2ad9ecca1cead4e26b03b3e81b8e6f761276b15ac3ffd67a6` | 01 业务组 | `0751558`（来源 `a7592ec`） | BusinessTaskSpec |
| DatasetSchema | `C1_01_Dataset_Schema_V0.2` | `484cb50e52e337d24cd014db9ddf1af98d5d82fee9706c512307bb8190da25fb` | 02 数据工程组 | 底座 `a720a03`；对照 `83aff9a` | BusinessTaskSpec + LabelGuide |
| BaselineProtocol | `C1_01_Baseline_Protocol_V0.2.1` | `f6844fef88b06d0844f8e086656eebabbb7ce873479fba1e5c3492a246401d2b` | 03 算法组 | 底座 `a720a03`（协议交付 `4019011`） | BusinessTaskSpec、LabelGuide、DatasetSchema、MetricSpec、盲测治理 |
| BenchmarkMetricSpec | `C1_01_Benchmark_Metric_Spec_V0.2` | `cb443a64178fb894d751bc02dbc6fc9f142e33a9e2130a121ab9e0a881f64a7d` | 04 测试与评测组 | 底座 `a720a03`（Gate-A `3bea201`） | DatasetSchema、LabelGuide、BusinessTaskSpec |
| Blind Test Governance | `C1_01_Blind_Test_Management_Rules_V0.1` + `C1_01_Blind_Test_Gold_Access_Boundary_V0.1` | `43514c360ff21586e13f0e91c91eae21459c8a157e816c092f3d462ccdca667a` + `6b6a895c29703f1a66df22fb6fdab884b197ed085abdea7dad16f543d3fe2338` | 04 测试与评测组 | 底座 `a720a03`（Gate-A `3bea201`） | MetricSpec、DatasetSchema、BaselineProtocol |

02 的 9 个数据文件逐一与底座比较，全部同字节同 SHA-1 Git blob；因此本候选不机械叠加 `83aff9a`，来源和签署责任仍保留为 02 数据工程组。

## 3. 验收范围与边界

### 已纳入

- 01 业务任务、标签指南、裁决日志、二次复核记录和 29 条种子材料；
- 02 Dataset Schema V0.2 及其现有校验/Manifest 资产；
- 03 Baseline Protocol V0.2.1、依赖锁、Harness、Preflight、Smoke 与 Regression 资产；
- 04 MetricSpec V0.2、Gate-A Manifest、独立正向/拒绝场景证据和盲测治理规则；
- 版本、字节和 hash chain 复核。

### 明确未授权或未完成

- `C1_01_Case_Intake_V0.1.jsonl` 与 `C1_01_InternalSilver_CasePack_V0.1.jsonl` 不存在，本候选不伪造这两个正式交付文件；
- 当前没有 `TRAIN`、`DEV` 或 `BLIND_GOLD` 数据集；
- 未运行 Base Model、DEV Benchmark、Blind Benchmark 或 Fine-tune；
- 不包含 Blind Gold 明文，不改变 QA 独占访问边界；
- 不合并 `main`，不宣布 `C1-01 END-TO-END CONTRACT FROZEN`。

## 4. 签署要求

当前集成结论保持：

```text
WAITING_FINAL_SIGNOFF
```

请 02 数据工程组完成 `DATA_SIGNOFF`，请 04 测试与评测组完成 `QA_FINAL_SIGNOFF`。两项签署完成后，项目负责人再决定是否将总控状态推进为最终冻结。
