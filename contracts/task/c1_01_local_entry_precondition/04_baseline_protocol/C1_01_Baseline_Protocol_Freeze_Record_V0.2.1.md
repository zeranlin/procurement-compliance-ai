# C1-01 Baseline Protocol Freeze Record V0.2.1

**冻结时间：** 2026-09-22
**冻结状态：** `FROZEN`
**责任团队：** 03 - 算法组；由 04 - QA / Benchmark Team 做兼容性验收
**适用任务：** `C1-01_LOCAL_ENTRY_PRECONDITION`

## 1. ALG-PATCH-01～05 处置结果

| Patch | 处置 | 结果 |
|---|---|---|
| ALG-PATCH-01 | 对齐 Benchmark Metric Spec V0.2 的 `INVALID`、全量分母、ID 对齐与 `null` 规则 | `PASS` |
| ALG-PATCH-02 | 固化裸 JSON prediction、跨字段与证据 Unicode 区间校验 | `PASS` |
| ALG-PATCH-03 | 生成 V0.2.1 SHA-256 dependency lock | `PASS` |
| ALG-PATCH-04 | 执行 Preflight 回归与 Stub smoke | `PASS` |
| ALG-PATCH-05 | 写入本 Freeze Record；未打开 Blind Gold，未执行 Fine-tune 或效果迭代 | `PASS` |

## 2. Frozen Assets

以下哈希与同目录 `C1_01_Baseline_Protocol_V0.2.1_Dependency_Lock.json` 一致；算法组后续运行必须先通过 lock 校验。

| Asset | Version | SHA-256 |
|---|---|---|
| BusinessTaskSpec | `BR_C1_01_Business_Task_Spec_V0.1` | `0fa169fa0fa34ef8e702c4cae8e10e89cdce4260aa198f7a45a4a28d5c3a74ab` |
| LabelGuide | `C1_01_Label_Guide_V0.1` | `9b6352b5f6e400f2ad9ecca1cead4e26b03b3e81b8e6f761276b15ac3ffd67a6` |
| DatasetSchema | `C1_01_Dataset_Schema_V0.1` | `b75008d2368857da02e2a7fd98c1b89f99ac155ae72830cda3b8b11c8aeb7fa7` |
| BaselineProtocol | `C1_01_Baseline_Protocol_V0.2` | `20fcb71fee5dedbc7150110c3e749c7a7296eb00dd5fce7e9f55c0d7e3ab54f9` |
| BenchmarkMetricSpec | `C1_01_Benchmark_Metric_Spec_V0.2` | `18b73e559485317ee0883486fd14923196ca017d862d6797209da96b53a5046c` |
| BlindTestManagementRules | `C1_01_Blind_Test_Management_Rules_V0.1` | `43514c360ff21586e13f0e91c91eae21459c8a157e816c092f3d462ccdca667a` |
| BlindTestGoldAccessBoundary | `C1_01_Blind_Test_Gold_Access_Boundary_V0.1` | `6b6a895c29703f1a66df22fb6fdab884b197ed085abdea7dad16f543d3fe2338` |
| BaselineHarness | `C1_01_Baseline_Harness_V0.2` | `59a25235e6d9bf94a8f1c4b59063c6b62c9bb6e3a92feae4ecc49fc9ba3545aa` |
| AdapterStub | `C1_01_Adapter_Stub_V0.2` | `4359b0598dbb3c897be8fc7276f8fe9245939085f395bc9397d87c4d528f570b` |

**Dependency lock SHA-256：** `3420e33997006c4c2d0be113ca96112a3ef6d4f39f5a722d0890f6a431bbd8e3`

## 3. Regression Evidence

```text
preflight: PASS
  dependency_lock: PASS
  unique_sample_ids: PASS
  dataset_eligibility (--smoke fixture): PASS
  few_shot_isolation: PASS

stub smoke: PASS
  rows: 1
  invalid_output_count: 0
  structured_output_valid_rate: 1.0
  blind_test_gold read: 0
```

The smoke fixture is synthetic and held out from any benchmark claim. It confirms only protocol execution and does not unlock Base Model, Fine-tune, Blind Benchmark, or Demo Gate.

## 4. Freeze Boundaries

- `REWORK_SOURCE` requires `target=null` and is rejected before model execution.
- `target`、`metadata`、`leakage_group_id`、切片和标签字段不会进入 adapter request。
- Adapter stdout is one bare JSON object; invalid output remains an `INVALID` scored row rather than being dropped.
- `score` is for DEV / Regression only in this algorithm-group harness. Protected Gold paths are refused before file open.
- No Metric Spec semantics, Blind Gold content, prompt optimization, Fine-tune, or Blind Test result was changed by this freeze.
