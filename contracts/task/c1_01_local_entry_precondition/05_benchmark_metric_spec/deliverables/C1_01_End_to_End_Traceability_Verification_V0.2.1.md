# C1-01 End-to-End Traceability Verification V0.2.1

**项目**：ProcurementComplianceLM  
**任务 ID**：C1-01_LOCAL_ENTRY_PRECONDITION  
**验证编号**：QA-REVERIFY-GATE-A-01 / QA-REVERIFY-02  
**Owner**：04-测试与评测组  
**verification_time**：2026-09-22T14:27:06Z  
**状态**：PASS  
**最终结论**：GATE-A_REVERIFY_PASS

本轮使用 evidence 目录内的 V0.2.1 lock、六项依赖、独立 fixtures 和 Preflight；依赖目录已补齐并完成独立复跑。

## 1. 六资产追踪矩阵

| Asset | Version | Hash | Owner | Dependency | Semantic / Contract Result | Final |
|---|---|---|---|---|---|---|
| BusinessTaskSpec | BR_C1_01_Business_Task_Spec_V0.1 | 0fa169fa0fa34ef8e702c4cae8e10e89cdce4260aa198f7a45a4a28d5c3a74ab | 01 业务组 | 项目业务任务边界 | 业务语义冻结，未被本轮修改 | PASS |
| LabelGuide | C1_01_Label_Guide_V0.1 | 9b6352b5f6e400f2ad9ecca1cead4e26b03b3e81b8e6f761276b15ac3ffd67a6 | 01 业务组 | BusinessTaskSpec | Label 语义、ParseFailure/NeedsContext 分流一致 | PASS |
| DatasetSchema | C1_01_Dataset_Schema_V0.2 | 484cb50e52e337d24cd014db9ddf1af98d5d82fee9706c512307bb8190da25fb | 02 数据工程组 | BusinessTaskSpec + LabelGuide | 生命周期、target nullable、Eligibility cross-field 规则一致 | PASS |
| BaselineProtocol | C1_01_Baseline_Protocol_V0.2.1 | f6844fef88b06d0844f8e086656eebabbb7ce873479fba1e5c3492a246401d2b | 03 算法组 | 六项依赖 + Output Schema | FROZEN；MetricSpec 正确重绑定为 V0.2；Preflight 一致 | PASS |
| BenchmarkMetricSpec | C1_01_Benchmark_Metric_Spec_V0.2 | cb443a64178fb894d751bc02dbc6fc9f142e33a9e2130a121ab9e0a881f64a7d | 04 测试与评测组 | DatasetSchema + LabelGuide + BusinessTaskSpec | Eligibility、Assembly Invalid、Prediction Invalid 一致 | PASS |
| Blind Test Governance | Rules V0.1 + Gold Boundary V0.1 | Rules 43514c360ff21586e13f0e91c91eae21459c8a157e816c092f3d462ccdca667a; Boundary 6b6a895c29703f1a66df22fb6fdab884b197ed085abdea7dad16f543d3fe2338 | 04 测试与评测组 | MetricSpec + DatasetSchema + BaselineProtocol | QA 独占 Gold policy；Algorithm 仅见 blind input/聚合报告 | PASS |

## 2. Asset 状态逐项打分

每个状态只使用 PASS / FAIL / BLOCKED / N/A。

| Asset | Version | Hash | Owner | Dependency | Semantics | Lifecycle / Preflight | Final |
|---|---|---|---|---|---|---|---|
| BusinessTaskSpec | PASS | PASS | PASS | PASS | PASS | N/A | PASS |
| LabelGuide | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| DatasetSchema V0.2 | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| BaselineProtocol V0.2.1 | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| BenchmarkMetricSpec V0.2 | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| Blind Test Governance | PASS | PASS | PASS | PASS | PASS | PASS | PASS |

## 3. Gate-A 最终验收矩阵

| Gate 项目目标 | 结果 | 证据摘要 |
|---|---|---|
| A-G1 Business semantics frozen | PASS | BusinessTaskSpec hash 与冻结状态一致 |
| A-G2 Label semantics frozen | PASS | LabelGuide hash 与业务分流规则一致 |
| A-G3 Dataset Schema V0.2 locked | PASS | Schema V0.2 hash、生命周期和 cross-field 规则一致 |
| A-G4 ParseFailure isolated | PASS | PARSE_FAILURE/REWORK_SOURCE 为 Assembly Invalid，target=null |
| A-G5 BaselineProtocol V0.2.1 locked | PASS | Protocol、lock、Freeze Record 三方一致 |
| A-G6 BenchmarkMetricSpec V0.2 locked | PASS | Metric V0.2 hash 与 Protocol V0.2.1 完全匹配 |
| A-G7 Blind Test governance frozen | PASS | Management Rules hash 已登记 |
| A-G8 Gold policy boundary frozen | PASS | Gold Access Boundary hash 已登记；QA-only policy PASS |
| A-G9 Six-asset version/hash chain consistent | PASS | 六资产与两项 Blind Governance hash chain 一致 |
| A-G10 Open Contract P0 | PASS | 0 |

## 4. Access Policy Contract

本轮只验 Policy Contract；真实运行时探针属于 Gate-B，不影响本轮 Gate-A：

| 主体 | 允许/禁止 | Policy 结果 |
|---|---|---|
| Algorithm | 不得读 Gold；只读 blind_test_input；只获得批准的聚合报告 | PASS |
| Business | Freeze 后不得读 Frozen Gold | PASS |
| Data | Freeze 后不得读 Frozen Gold | PASS |
| PM | Approval 不等于 Gold Read | PASS |
| Ops | Admin 不等于 Gold Plaintext Read | PASS |
| QA isolated evaluator | 受控读取 blind_test_gold | PASS |

## 5. Gate-B 边界声明

~~~text
Contract Ready
!=
Benchmark Ready
~~~

以下保持 Gate-B 状态，不倒灌 Gate-A：

~~~text
BENCHMARK_CANDIDATE = 0
Blind Test N < 50
blind_test_input / blind_test_gold 尚未生成
QA isolated evaluator 尚未部署
Runtime ACL probe 尚未执行
正式 Base Model / Blind Benchmark 尚未运行
~~~

## 6. 最终判定

~~~text
Version Locked       = PASS
Hash Locked          = PASS
Owner Known          = PASS
Dependency Known     = PASS
Semantic Compatible  = PASS
Open Contract P0     = 0
~~~

因此：

~~~text
GATE-A_REVERIFY_PASS
~~~

C1-01 Contract 已具备提交项目负责人 FINAL CONTRACT FREEZE REVIEW 的条件；在 PM 正式审查前，不提前宣称项目已完成最终 Freeze。
