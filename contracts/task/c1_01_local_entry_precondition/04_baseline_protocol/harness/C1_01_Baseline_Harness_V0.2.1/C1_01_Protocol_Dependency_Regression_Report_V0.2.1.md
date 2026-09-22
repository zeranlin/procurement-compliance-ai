# C1-01 Protocol Dependency Regression Report V0.2.1

**任务**：`C1-01_LOCAL_ENTRY_PRECONDITION`  
**整改**：`ALG-PATCH-01`  ️  
**协议**：`C1_01_Baseline_Protocol_V0.2.1`  
**状态**：`PASS`  
**执行时间**：2026-09-22T09:19:41Z  
**范围**：`CONTRACT_FIXTURE_ONLY`

## 1. 回归目的

验证 BaselineProtocol V0.2.1 已将唯一过期依赖
`C1_01_Benchmark_Metric_Spec_V0.1` 修正为冻结的
`C1_01_Benchmark_Metric_Spec_V0.2`，并验证版本匹配、hash 匹配、Dataset
Candidate 拒绝边界和 Model Prediction Invalid 语义。该回归不运行 Base
Model、DEV Benchmark 或 Blind Test，不读取 Blind Gold。

## 2. 六资产 Frozen Contract Chain

| 资产 | version | SHA-256 | 状态 |
|---|---|---|---|
| BusinessTaskSpec | `BR_C1_01_Business_Task_Spec_V0.1` | `0fa169fa0fa34ef8e702c4cae8e10e89cdce4260aa198f7a45a4a28d5c3a74ab` | `FROZEN` |
| LabelGuide | `C1_01_Label_Guide_V0.1` | `9b6352b5f6e400f2ad9ecca1cead4e26b03b3e81b8e6f761276b15ac3ffd67a6` | `FROZEN` |
| DatasetSchema | `C1_01_Dataset_Schema_V0.2` | `484cb50e52e337d24cd014db9ddf1af98d5d82fee9706c512307bb8190da25fb` | `FROZEN` |
| BenchmarkMetricSpec | `C1_01_Benchmark_Metric_Spec_V0.2` | `cb443a64178fb894d751bc02dbc6fc9f142e33a9e2130a121ab9e0a881f64a7d` | `FROZEN_FOR_SCHEMA_V0.2_COMPATIBILITY` |
| Blind Test Management | `C1_01_Blind_Test_Management_Rules_V0.1` | `43514c360ff21586e13f0e91c91eae21459c8a157e816c092f3d462ccdca667a` | `FROZEN` |
| Blind Gold Access Boundary | `C1_01_Blind_Test_Gold_Access_Boundary_V0.1` | `6b6a895c29703f1a66df22fb6fdab884b197ed085abdea7dad16f543d3fe2338` | `FROZEN` |

`DatasetSchema=V0.2` and `BenchmarkMetricSpec=V0.2` are the active nodes in
this patch. The other four frozen hashes are unchanged from Protocol V0.2.

## 3. Preflight regression matrix

The regression runner was:

```bash
python3 regression_tests.py --output protocol_dependency_regression.json
```

| Case | Input mutation | Expected | Observed |
|---|---|---|---|
| CASE 01 | MetricSpec V0.2 + correct hash | `PASS` | `PASS` |
| CASE 02 | MetricSpec V0.1 | `RUN_ABORTED` | `RUN_ABORTED` |
| CASE 03 | MetricSpec V0.2 + wrong hash | `RUN_ABORTED` | `RUN_ABORTED` |
| CASE 04 | DatasetSchema V0.2 + correct hash | `PASS` | `PASS` |
| CASE 05 | DatasetSchema V0.1 | `RUN_ABORTED` | `RUN_ABORTED` |
| CASE 06 | `REWORK_SOURCE` Dataset Candidate | `RUN_ABORTED` before model; Harness `REFUSED_INPUT` | `RUN_ABORTED` + `REFUSED_INPUT` |
| CASE 07 | `HOLD` Dataset Candidate | `RUN_ABORTED` before model | `RUN_ABORTED` |
| CASE 08 | `DISPUTED` Dataset Candidate | `RUN_ABORTED` before model | `RUN_ABORTED` |
| CASE 09 | `PENDING_DATA_QA` Dataset Candidate | `RUN_ABORTED` before model | `RUN_ABORTED` |

The valid TRAIN / DEV / BLIND_INPUT contract fixture passed formal Preflight,
including schema hash and split isolation. Every negative case stopped at the
dataset/preflight boundary; no adapter was started for a formal run.

The direct Harness boundary also returned `REFUSED_INPUT` for all four blocked
states (`REWORK_SOURCE`, `HOLD`, `DISPUTED`, and `PENDING_DATA_QA`), before the
adapter command could receive an input.

## 4. Metric semantic compatibility

The regression also checked one already-eligible sample with an invalid model
response:

- `sample_id` remained in the prediction record;
- `status=INVALID` was retained;
- `structured_output_valid_rate=0.0` for the one-sample fixture;
- the `MATCH` gold row contributed a recall miss (`match_recall=0.0`);
- no default `NO_MATCH`, JSON repair, row deletion, or denominator removal occurred.

`REWORK_SOURCE` was tested separately as an Assembly/Dataset invalid candidate:
it was not converted to `NEEDS_CONTEXT`, did not produce a Prediction, and was
refused before adapter invocation. Metric semantics remain delegated to
BenchmarkMetricSpec V0.2; the algorithm harness did not redefine them.

## 5. Regression conclusion

All required cases passed. Version match plus hash match is enforced as the
run-allow condition; any mismatch returns `RUN_ABORTED`. Protocol V0.2 remains
the immutable historical freeze, and V0.2.1 is the new dependency-patched
freeze candidate for 04 QA incremental compatibility and traceability review.
