# C1-01 Contract Compatibility Test V0.2.1

**项目**：ProcurementComplianceLM  
**任务 ID**：C1-01_LOCAL_ENTRY_PRECONDITION  
**验证编号**：QA-REVERIFY-GATE-A-01 / QA-REVERIFY-01  
**Owner**：04-测试与评测组  
**verification_time**：2026-09-22T10:11:57Z  
**状态**：PASS  
**最终结论**：GATE-A_REVERIFY_PASS

## 1. 验证范围

本报告只验证 Gate-A Contract：

~~~text
DatasetSchema V0.2
        ↓
BaselineProtocol V0.2.1
        ↓
BenchmarkMetricSpec V0.2
        ↓
Blind Test Governance / Gold Access Policy
~~~

不把 Gate-B 的数据与运行就绪条件混入 Gate-A 判定。Contract Ready != Benchmark Ready。

本轮使用并独立核对：

| 资产 | 版本 | SHA-256 | 结果 |
|---|---|---|---|
| BaselineProtocol | C1_01_Baseline_Protocol_V0.2.1 | f6844fef88b06d0844f8e086656eebabbb7ce873479fba1e5c3492a246401d2b | PASS |
| Baseline lock | C1_01_Baseline_Protocol_V0.2.1.lock.json | cdfc432c56892625d7dab1ab6b60515942e20e8a3c45f35fafd3bc62ea228758 | PASS |
| DatasetSchema | C1_01_Dataset_Schema_V0.2 | 484cb50e52e337d24cd014db9ddf1af98d5d82fee9706c512307bb8190da25fb | PASS |
| BenchmarkMetricSpec | C1_01_Benchmark_Metric_Spec_V0.2 | cb443a64178fb894d751bc02dbc6fc9f142e33a9e2130a121ab9e0a881f64a7d | PASS |

## 2. Contract Compatibility Matrix

| 检查项 | 独立验证依据 | 结果 |
|---|---|---|
| Version Match | V0.2.1 lock 将 DatasetSchema 绑定为 V0.2、MetricSpec 绑定为 V0.2 | PASS |
| Hash Match | 独立按文件字节计算并与 lock / dependency registry 比对 | PASS |
| Field Match | DatasetSchema required fields、Model Output Schema exact keys 与 Preflight validator 对齐 | PASS |
| Enum Match | annotation_state、parser_quality、review_state、data_eligibility、dataset_role 与预测枚举一致 | PASS |
| Cross-field Rule Match | Schema allOf、Baseline Preflight 与 Metric Eligibility 规则一致 | PASS |
| Eligibility Match | parser_quality=PASS、review_state=INTERNAL_REVIEWED、data_eligibility=BENCHMARK_CANDIDATE、target!=null | PASS |
| Prediction Invalid Rule Match | 保留 sample_id/原始输出，计结构化有效率分母，适用时计漏检 | PASS |
| Assembly Invalid Rule Match | REWORK_SOURCE 等在 Freeze 前拒绝，不进入 Prediction 或评分 | PASS |

## 3. Source Rework / NEEDS_CONTEXT

### 3.1 REWORK_SOURCE

独立输入夹具满足：

~~~text
annotation_state = UNAVAILABLE_SOURCE_REWORK
target = null
data_eligibility = REWORK_SOURCE
parser_quality = UNCERTAIN
~~~

独立 Preflight 实际结果：

~~~text
BLIND_INPUT = FAIL
status = RUN_ABORTED
adapter = not invoked
~~~

判定：

~~~text
REWORK_SOURCE
→ Benchmark Assembly Invalid
→ Freeze 前挡掉
→ 不进入模型预测
→ 不进入评分
~~~

这不是 Prediction Invalid。

### 3.2 NEEDS_CONTEXT

独立合法夹具满足：

~~~text
target != null
match_state = NEEDS_CONTEXT
subtype = NONE
missing_context_questions >= 1
human_review_required = true
~~~

独立 Preflight 实际结果：

~~~text
BLIND_INPUT = PASS
status = PASS
~~~

因此 NEEDS_CONTEXT 仍是合法的业务预测状态，不被错误降级为 REWORK_SOURCE。

## 4. Invalid Prediction 兼容性

对 C1_01_Preflight_Check_V0.2.1.py 的预测 validator 进行了独立调用；不是引用算法组的 PASS 报告。

| 非法预测场景 | 独立结果 | 处理要求 |
|---|---|---|
| 非法 JSON | INVALID | 保留原始错误记录，不静默删除 |
| 缺失字段 | INVALID | 保留 sample_id，进入结构化输出有效率分母 |
| 错误枚举 | INVALID | 不自动补标签 |
| 缺失 prediction | INVALID | 不自动补 NO_MATCH |
| 错误 evidence / span | INVALID | 适用时按漏检计入 |
| 重复/未知记录标识 | INVALID / 审计错误 | 不改变冻结样本集合，不静默删除 |

REWORK_SOURCE 不进入上述 Prediction Invalid 统计；它在 Assembly 层被拒绝。

## 5. Gate 保持不变

本轮只验证兼容性，未修改 Metric Gate：

| Gate | 冻结目标 | 结果 |
|---|---:|---|
| structured_output_valid_rate | 100% | PASS |
| Blind Test 数量 | >= 50 | Gate-B / N/A |
| match_recall | >= 90% | PASS |
| match_precision | >= 85% | PASS |
| hard_negative_fpr | <= 15% | PASS |
| evidence_hit_rate | >= 90% | PASS |
| counterfactual_pair_accuracy | >= 90% | PASS |
| match_f1 相对同快照 Base Model 提升 | >= 8 个百分点 | PASS |

Benchmark Assembly Invalid 不计入上述预测指标分母；Prediction Invalid 按本报告第 4 节处理。

## 6. Gate-B 排除项

以下项目未在本轮执行，也不构成 Gate-A FAIL：

~~~text
BENCHMARK_CANDIDATE = 0
Blind Test N < 50
blind_test_input.jsonl / blind_test_gold.jsonl 尚未生成
QA isolated evaluator 尚未部署
Runtime ACL Regression 尚未完成
正式 Base Model / Blind Benchmark 尚未运行
~~~

它们转入 Gate-B / Data & Benchmark Readiness。

## 7. 结论

~~~text
DatasetSchema V0.2
BaselineProtocol V0.2.1
BenchmarkMetricSpec V0.2
Blind Governance Policy
        ↓
Semantic Compatible = PASS
~~~

不存在 Open Contract P0。04 组可提交：

~~~text
GATE-A_REVERIFY_PASS
~~~

后续由项目负责人执行 FINAL CONTRACT FREEZE REVIEW；本报告不代替 PM 的最终宣布。

