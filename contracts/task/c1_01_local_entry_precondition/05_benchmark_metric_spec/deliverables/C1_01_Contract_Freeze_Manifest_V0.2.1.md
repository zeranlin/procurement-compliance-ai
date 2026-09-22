# C1-01 Contract Freeze Manifest V0.2.1

**项目**：ProcurementComplianceLM  
**任务 ID**：C1-01_LOCAL_ENTRY_PRECONDITION  
**验证编号**：QA-REVERIFY-GATE-A-01 / QA-REVERIFY-03  
**Owner**：04-测试与评测组  
**verification_time**：2026-09-22T14:27:06Z  
**manifest_status**：FROZEN_FOR_GATE_A_REVERIFY  
**最终结论**：GATE-A_REVERIFY_PASS

## 1. Manifest 目的

本 Manifest 只冻结 Gate-A 的六资产 Contract 及 Blind Test Governance Policy 依赖链，不冻结真实 Benchmark Snapshot、Blind Gold、模型效果或 Gate-B 运行环境。

~~~text
Contract Freeze
!=
Benchmark Snapshot Freeze
~~~

任何登记资产的 version 或 SHA-256 改变，都必须重新生成本 Manifest 或产生新的 Snapshot/Freeze 版本；原链不得继续声称为同一 Frozen Contract。

## 2. 核心资产与治理资产 Hash Chain

| Asset | Version | SHA-256 | Owner | Freeze Status | Dependency | Verification |
|---|---|---|---|---|---|---|
| BusinessTaskSpec | BR_C1_01_Business_Task_Spec_V0.1 | 0fa169fa0fa34ef8e702c4cae8e10e89cdce4260aa198f7a45a4a28d5c3a74ab | 01 业务组 | FROZEN | 项目业务任务边界 | PASS |
| LabelGuide | C1_01_Label_Guide_V0.1 | 9b6352b5f6e400f2ad9ecca1cead4e26b03b3e81b8e6f761276b15ac3ffd67a6 | 01 业务组 | FROZEN | BusinessTaskSpec | PASS |
| DatasetSchema | C1_01_Dataset_Schema_V0.2 | 484cb50e52e337d24cd014db9ddf1af98d5d82fee9706c512307bb8190da25fb | 02 数据工程组 | FROZEN | BusinessTaskSpec + LabelGuide | PASS |
| BaselineProtocol | C1_01_Baseline_Protocol_V0.2.1 | f6844fef88b06d0844f8e086656eebabbb7ce873479fba1e5c3492a246401d2b | 03 算法组 | FROZEN | 六项依赖 + Model Output Schema | PASS |
| BenchmarkMetricSpec | C1_01_Benchmark_Metric_Spec_V0.2 | cb443a64178fb894d751bc02dbc6fc9f142e33a9e2130a121ab9e0a881f64a7d | 04 测试与评测组 | FROZEN_FOR_SCHEMA_V0.2_COMPATIBILITY | DatasetSchema + LabelGuide + BusinessTaskSpec | PASS |
| Blind Test Management Rules | C1_01_Blind_Test_Management_Rules_V0.1 | 43514c360ff21586e13f0e91c91eae21459c8a157e816c092f3d462ccdca667a | 04 测试与评测组 | FROZEN | MetricSpec + DatasetSchema | PASS |
| Blind Gold Access Boundary | C1_01_Blind_Test_Gold_Access_Boundary_V0.1 | 6b6a895c29703f1a66df22fb6fdab884b197ed085abdea7dad16f543d3fe2338 | 04 测试与评测组 | FROZEN | Blind Rules + BaselineProtocol | PASS |

## 3. Protocol Evidence Chain

本轮独立验证使用的 `evidence/protocol/deps/` 六项依赖目录已完整登记；其版本和哈希与 BaselineProtocol V0.2.1 lock 一致。

| Evidence | Version / File | SHA-256 | Result |
|---|---|---|---|
| Baseline lock | C1_01_Baseline_Protocol_V0.2.1.lock.json | cdfc432c56892625d7dab1ab6b60515942e20e8a3c45f35fafd3bc62ea228758 | PASS |
| Protocol Freeze Record | C1_01_Protocol_Freeze_Record_V0.2.1.md | cd461acff02c9932f0e6861aea42f0acae5ab0cd6cb27248152df708385d3072 | PASS |
| Dependency Registry | C1_01_Protocol_Dependency_Registry_V0.2.1.json | f5944d533ad7bddf7cc47da9d8b4b7f75dcfb266c827651b0b10a74810508fb0 | PASS |
| Model Output Schema | C1_01_Model_Output_Schema_V0.2.json | 6680eca2912a0e84d47e8cd02baab2235c365dadcd482c5c10fb2ebedefbf6c9 | PASS |

## 4. Freeze Preflight

| Preflight 项 | 结果 |
|---|---|
| BaselineProtocol version = V0.2.1 | PASS |
| DatasetSchema version = V0.2 | PASS |
| BenchmarkMetricSpec version = V0.2 | PASS |
| MetricSpec exact hash match | PASS |
| DatasetSchema exact hash match | PASS |
| Blind Rules / Gold Boundary version + hash registered | PASS |
| REWORK_SOURCE blocked before model | PASS |
| HOLD / DISPUTED / PENDING_DATA_QA blocked before model | PASS |
| Prediction Invalid remains post-Snapshot audit state | PASS |
| No Open Contract P0 | PASS / 0 |

## 5. Access Policy Freeze

| Subject | Policy boundary | Result |
|---|---|---|
| Algorithm | No Gold Read；only blind_test_input and approved aggregate report | PASS |
| Business | No Frozen Gold Read after Freeze | PASS |
| Data | No Frozen Gold Read after Freeze | PASS |
| PM | Approval does not imply Gold Read | PASS |
| Ops | Admin does not imply Gold plaintext Read | PASS |
| QA isolated evaluator | Controlled Gold Read | PASS |

本轮只确认 Policy Contract；真实 runtime ACL probe、service account、audit log 和 evaluator deployment 属于 Gate-B。

## 6. Gate-A Decision

~~~text
A-G1  Business semantics frozen                 PASS
A-G2  Label semantics frozen                    PASS
A-G3  Dataset Schema V0.2 locked                PASS
A-G4  ParseFailure isolated                     PASS
A-G5  BaselineProtocol V0.2.1 locked            PASS
A-G6  BenchmarkMetricSpec V0.2 locked           PASS
A-G7  Blind Test governance frozen              PASS
A-G8  Gold policy boundary frozen               PASS
A-G9  Six-asset version/hash chain consistent   PASS
A-G10 Open Contract P0                          0
~~~

最终状态：

~~~text
GATE-A_REVERIFY_PASS
~~~

C1-01 Contract is ready for Project Manager Final Freeze Review。

## 7. Gate-B Handoff

以下不影响本次 Gate-A 结论，统一转入 Gate-B / Data & Benchmark Readiness：

~~~text
BENCHMARK_CANDIDATE = 0
Blind Test N < 50
blind_test_input.jsonl 尚未生成
blind_test_gold.jsonl 尚未生成
QA isolated evaluator 尚未部署
Runtime ACL Regression 尚未完成
正式 Base Model / Blind Benchmark 尚未运行
~~~

因此本 Manifest 不授权 Fine-tune，不授权正式 Blind Benchmark，也不代表项目负责人已经完成最终宣布。
