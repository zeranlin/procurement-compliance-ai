# C1-01 Preflight Independent Verification V0.2.1

**项目**：ProcurementComplianceLM  
**任务 ID**：C1-01_LOCAL_ENTRY_PRECONDITION  
**验证编号**：QA-REVERIFY-GATE-A-01 / QA-REVERIFY-04  
**Owner**：04-测试与评测组  
**verification_time**：2026-09-22T14:27:06Z  
**执行方式**：04 QA 独立调用 Preflight 与 Prediction Validator  
**状态**：PASS  
**最终结论**：GATE-A_REVERIFY_PASS

本轮使用 evidence 目录自身的 V0.2.1 lock、六项依赖、fixtures 和 Preflight；依赖目录缺口已补齐后重新执行。

## 1. 独立性声明

本报告不是引用 03-算法组的 PASS 报告，而是由 04 QA 使用已锁定的 V0.2.1 Preflight 代码、lock 文件和独立测试夹具重新执行。

验证对象：

| 对象 | 版本 | SHA-256 |
|---|---|---|
| Preflight code | C1_01_Preflight_Check_V0.2.1.py | 由当前版本文件独立读取 |
| Protocol lock | C1_01_Baseline_Protocol_V0.2.1.lock.json | cdfc432c56892625d7dab1ab6b60515942e20e8a3c45f35fafd3bc62ea228758 |
| DatasetSchema | C1_01_Dataset_Schema_V0.2 | 484cb50e52e337d24cd014db9ddf1af98d5d82fee9706c512307bb8190da25fb |
| BenchmarkMetricSpec | C1_01_Benchmark_Metric_Spec_V0.2 | cb443a64178fb894d751bc02dbc6fc9f142e33a9e2130a121ab9e0a881f64a7d |

## 2. Preflight Scenario Matrix

| 场景 | 预期 | 独立实际结果 | Exit |
|---|---|---|---:|
| MetricSpec V0.2 + 正确 hash | PASS | PASS | 0 |
| MetricSpec V0.1 | RUN_ABORTED | RUN_ABORTED；dependency version mismatch | 2 |
| MetricSpec V0.2 + 错误 hash | RUN_ABORTED | RUN_ABORTED；dependency hash mismatch | 2 |
| DatasetSchema V0.2 | PASS | PASS | 0 |
| DatasetSchema V0.1 | RUN_ABORTED | RUN_ABORTED；version/schema mismatch | 2 |
| REWORK_SOURCE | REFUSED / ABORT | RUN_ABORTED；BLIND_INPUT FAIL | 2 |
| HOLD | ABORT | RUN_ABORTED；BLIND_INPUT FAIL | 2 |
| DISPUTED | ABORT | RUN_ABORTED；BLIND_INPUT FAIL | 2 |
| PENDING_DATA_QA | ABORT | RUN_ABORTED；BLIND_INPUT FAIL | 2 |
| 合格 TRAIN / DEV / BLIND_INPUT | PASS | PASS；split leakage PASS | 0 |
| 合法 NEEDS_CONTEXT | PASS | PASS | 0 |

## 3. Dataset Lifecycle Checks

### 3.1 REWORK_SOURCE

独立夹具：

~~~text
annotation_state = UNAVAILABLE_SOURCE_REWORK
target = null
data_eligibility = REWORK_SOURCE
parser_quality = UNCERTAIN
source_defect_prevents_judgment = true
~~~

实际结果：

~~~text
BLIND_INPUT = FAIL
status = RUN_ABORTED
~~~

该结果满足：

~~~text
REFUSED / ABORT
adapter 不应被调用
不进入 Prediction
不进入评分
~~~

### 3.2 HOLD / DISPUTED / PENDING_DATA_QA

三类夹具均被 Preflight 拦截，不会被误当作合格 Benchmark sample：

| 状态 | 实际结果 | 核心拒绝原因 |
|---|---|---|
| HOLD | RUN_ABORTED | data_eligibility=HOLD is blocked |
| DISPUTED | RUN_ABORTED | review_state=DISPUTED is blocked |
| PENDING_DATA_QA | RUN_ABORTED | data_eligibility=PENDING_DATA_QA is blocked |

### 3.3 NEEDS_CONTEXT

独立合法夹具满足：

~~~text
target != null
match_state = NEEDS_CONTEXT
subtype = NONE
missing_context_questions >= 1
human_review_required = true
~~~

实际结果：

~~~text
BLIND_INPUT = PASS
status = PASS
~~~

## 4. Prediction Validator Independent Checks

04 QA 独立调用 validator，结果如下：

| 输入 | 结果 |
|---|---|
| 合法 MATCH prediction | VALID |
| 非法 JSON | INVALID |
| 缺失字段 | INVALID |
| 错误枚举 | INVALID |
| 错误 evidence span | INVALID |
| 额外/未知 record identifier | INVALID |

详细 validator 结果见 `evidence/reports/prediction_validator_independent.json`。

Protocol 规则同时要求：

~~~text
Prediction Invalid
→ 保留 sample_id 和原始输出
→ 进入 structured_output_valid_rate 分母
→ 在适用情况下计为 MATCH 漏检
→ 不自动补标签
→ 不静默删除
~~~

## 5. Hash / Version Rejection

以下拒绝行为均已由独立执行确认：

~~~text
Version Match + Hash Match = Run Allowed
Version mismatch = RUN_ABORTED
Hash mismatch = RUN_ABORTED
~~~

独立观察到的六项依赖 hash：

~~~text
BusinessTaskSpec       0fa169fa0fa34ef8e702c4cae8e10e89cdce4260aa198f7a45a4a28d5c3a74ab
LabelGuide             9b6352b5f6e400f2ad9ecca1cead4e26b03b3e81b8e6f761276b15ac3ffd67a6
DatasetSchema          484cb50e52e337d24cd014db9ddf1af98d5d82fee9706c512307bb8190da25fb
BenchmarkMetricSpec    cb443a64178fb894d751bc02dbc6fc9f142e33a9e2130a121ab9e0a881f64a7d
Blind Test Rules       43514c360ff21586e13f0e91c91eae21459c8a157e816c092f3d462ccdca667a
Gold Access Boundary   6b6a895c29703f1a66df22fb6fdab884b197ed085abdea7dad16f543d3fe2338
~~~

## 6. Gate-A / Gate-B 边界

本轮只验证 Gate-A Contract。以下项目不是本轮失败项：

~~~text
BENCHMARK_CANDIDATE = 0
Blind Test N < 50
blind_test_input / blind_test_gold 尚未生成
QA isolated evaluator 尚未部署
Runtime ACL Regression 尚未完成
正式 Base Model / Blind Benchmark 尚未运行
~~~

这些项目记录为 Gate-B handoff，不改变本报告的 Gate-A PASS。

## 7. 最终结论

~~~text
Preflight independent verification = PASS
Open Contract P0 = 0
GATE-A_REVERIFY_PASS
~~~

本报告支持项目负责人进入 FINAL CONTRACT FREEZE REVIEW。
