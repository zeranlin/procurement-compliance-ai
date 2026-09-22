# C1-01 Protocol Freeze Record V0.2.1

**冻结决定**：`FROZEN`  
**协议版本**：`C1_01_Baseline_Protocol_V0.2.1`  
**任务**：`C1-01_LOCAL_ENTRY_PRECONDITION`  
**整改**：`ALG-PATCH-01`  
**freeze_time**：`2026-09-22T09:21:36Z`  
**owner**：`03-算法组`  
**change_scope**：`Protocol dependency patch only`

## 1. 版本沿革

| 字段 | 固定值 |
|---|---|
| `previous_version` | `C1_01_Baseline_Protocol_V0.2` |
| `previous_status` | `FROZEN`（历史版本，保留不覆盖） |
| `change_reason` | 修正 BaselineProtocol 对 BenchmarkMetricSpec 的 stale dependency，从 V0.1 绑定到 V0.2 |
| `new_status` | `FROZEN` |

V0.2 的原文、lock、Preflight 与历史 hash 保留；本记录只冻结 V0.2.1
这一条新的依赖节点，不代表任何模型表现冻结。

## 2. Frozen Contract Chain

| 字段 | 固定值 |
|---|---|
| `protocol_version` | `C1_01_Baseline_Protocol_V0.2.1` |
| `protocol_sha256` | `f6844fef88b06d0844f8e086656eebabbb7ce873479fba1e5c3492a246401d2b` |
| `spec_version` | `BR_C1_01_Business_Task_Spec_V0.1` |
| `spec_sha256` | `0fa169fa0fa34ef8e702c4cae8e10e89cdce4260aa198f7a45a4a28d5c3a74ab` |
| `label_guide_version` | `C1_01_Label_Guide_V0.1` |
| `label_guide_sha256` | `9b6352b5f6e400f2ad9ecca1cead4e26b03b3e81b8e6f761276b15ac3ffd67a6` |
| `schema_version` | `C1_01_Dataset_Schema_V0.2` |
| `schema_sha256` | `484cb50e52e337d24cd014db9ddf1af98d5d82fee9706c512307bb8190da25fb` |
| `metric_spec_version` | `C1_01_Benchmark_Metric_Spec_V0.2` |
| `metric_spec_sha256` | `cb443a64178fb894d751bc02dbc6fc9f142e33a9e2130a121ab9e0a881f64a7d` |
| `blind_test_rule_version` | `C1_01_Blind_Test_Management_Rules_V0.1` |
| `blind_test_rule_sha256` | `43514c360ff21586e13f0e91c91eae21459c8a157e816c092f3d462ccdca667a` |
| `blind_gold_boundary_version` | `C1_01_Blind_Test_Gold_Access_Boundary_V0.1` |
| `blind_gold_boundary_sha256` | `6b6a895c29703f1a66df22fb6fdab884b197ed085abdea7dad16f543d3fe2338` |

The machine-readable lock is
`C1_01_Baseline_Harness_V0.2.1/C1_01_Baseline_Protocol_V0.2.1.lock.json`.
Its SHA-256 is
`cdfc432c56892625d7dab1ab6b60515942e20e8a3c45f35fafd3bc62ea228758`.

## 3. Patch deliverables

| 交付物 | SHA-256 |
|---|---|
| `C1_01_Baseline_Protocol_V0.2.1.md` | `f6844fef88b06d0844f8e086656eebabbb7ce873479fba1e5c3492a246401d2b` |
| `C1_01_Preflight_Check_V0.2.1.py` | `76a4f6a594423c6038be9b8095c06ab6f7711228d748ce69e475b0a05287a233` |
| `C1_01_Model_Output_Schema_V0.2.json` | `6680eca2912a0e84d47e8cd02baab2235c365dadcd482c5c10fb2ebedefbf6c9` |
| `harness.py` | `861b7a7d1a94dab7a9181e6cd402703c353e352735e30c291284c7908e513d08` |
| `adapter_stub.py` | `998bfea3a146abdd4fe14ddb5a8f0763feee7d44a46f44d1af3c617468ea9177` |
| `C1_01_Protocol_Dependency_Registry_V0.2.1.json` | `f5944d533ad7bddf7cc47da9d8b4b7f75dcfb266c827651b0b10a74810508fb0` |
| `C1_01_Baseline_Run_Manifest_Template_V0.2.1.json` | `f96acbb2b86c4cc2ceb6305340a478a75d58f4ec29a2a19f1fd8b47299d37b03` |
| `protocol_smoke_report.json` | `553e96cb156fa51378f1da9edc05f70fcf33724e34b386c386afe7562e5bba98` |
| `C1_01_Protocol_Dependency_Regression_Report_V0.2.1.md` | `46377dd0af80eb2ee8557c259a7dc13cbc8441efbe0a67776feb19f434966f47` |

## 4. Acceptance result

- MetricSpec V0.2 with the exact hash: `PASS`。
- MetricSpec V0.1 and MetricSpec hash mismatch: `RUN_ABORTED`。
- DatasetSchema V0.2 with the exact hash: `PASS`；DatasetSchema V0.1: `RUN_ABORTED`。
- `REWORK_SOURCE` / `HOLD` / `DISPUTED` / `PENDING_DATA_QA`: dataset Preflight `RUN_ABORTED`；source rework adapter boundary `REFUSED_INPUT`。
- Stub `MATCH` / `NO_MATCH` / `NEEDS_CONTEXT`: `VALID`；illegal JSON: `INVALID`。
- Invalid Prediction keeps `sample_id`, affects structured-output denominator, and counts as a MATCH miss when applicable。
- No model run, DEV Benchmark, Blind Test, Fine-tune, Prompt optimization, label change, Gate change, or Blind Gold access occurred。

V0.2.1 is ready for 04 QA's incremental Contract Compatibility,
Traceability Verification, and Freeze Manifest review.
