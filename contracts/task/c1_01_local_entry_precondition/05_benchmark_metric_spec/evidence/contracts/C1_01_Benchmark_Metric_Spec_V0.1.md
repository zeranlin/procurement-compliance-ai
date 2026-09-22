# C1-01 Benchmark Metric Spec V0.1

**文档状态**：`FROZEN`  
**生效日期**：2026-09-22  
**责任团队**：测试与评测组  
**任务 ID**：`C1-01_LOCAL_ENTRY_PRECONDITION`  
**适用范围**：C1-01 Blind Benchmark V0.1 及其同快照的 DEV 对照评测

## 1. 冻结对象与非目标

本文件冻结：

1. 预测与真值的对齐规则；
2. 指标名称、公式、分母和非法输出处理；
3. 必须报告的整体指标与切片指标；
4. Demo Gate 的目标阈值及变更规则；
5. 评测报告的最小字段和审计要求。

本文件不把当前 `INTERNAL_SILVER` 标签升级为外部专家 Gold，也不把 Demo Gate 变成生产 Release Gate。若上游 `Business Task Spec`、`Label Guide` 或 `Dataset Schema` 发生语义变化，必须生成新的 Benchmark Snapshot 和本规范版本，不得在原快照上静默修改。

## 2. 上游依赖与核心原则

评测必须记录并锁定以下版本及内容哈希：

- `BR_C1_01_Business_Task_Spec_V0.1`；
- `C1_01_Label_Guide_V0.1`；
- `C1_01_Dataset_Schema_V0.1`；
- `C1_01_Baseline_Harness_V0.1`；
- `C1_01_BenchmarkSnapshot_V0.1`。

执行原则：

- `Overall Score != Slice Reliability`：不得用一个总分掩盖高风险切片的失效。
- 所有非法格式、缺失预测和 ID 错误都必须保留；它们计入样本总数、结构化有效率以及适用的指标分母，在 `match_recall` 中按漏检处理，不得先删除错误样本再评分。
- `NO_MATCH` 只表示当前 Requirement 未命中 C1-01，不是整份采购文件的合规结论。
- `NEEDS_CONTEXT` 是受约束的弃权，不是“模型不确定时的万能出口”。
- `MATCH` 的证据评价只验证候选识别任务需要的事实，不输出最终违法认定或处罚判断。
- 分母为 0 时返回 `null`，不得改写为 0 或 100%。

## 3. 评测输入与对齐

### 3.1 真值侧

`blind_test_gold.jsonl` 由测试组独占保管。每条记录至少能提供：

```text
sample_id
target.match_state
target.subtype
target.evidence_spans
target.missing_context_questions
leakage_group_id
case_slice
pair_id（如适用）
```

`label_authority=INTERNAL_SILVER` 必须保留。`blind_test_gold` 是评测运行中的隐藏参考，不代表已经完成独立专家治理。

### 3.2 预测侧

模型提交必须包含：

```text
sample_id
prediction（符合 C1_01_Dataset_Schema_V0.1 的 target 结构）
```

允许的输入只能来自 `blind_test_input.jsonl` 及冻结的输出契约；不得接收 `target`、`metadata`、`case_slice`、`leakage_group_id`、`label_authority` 或任何真值派生字段。

### 3.3 对齐规则

- 预测集与真值集的 `sample_id` 集合必须完全相同；
- 缺失、重复、未知 ID 均为评测错误；
- 不能通过丢弃错误 ID、重复取第一条或按文件顺序强行对齐；
- 预测解析失败时保留该 `sample_id`，将该例状态记为 `INVALID`；
- 每一次评分记录输入哈希、预测哈希、真值快照 ID、评测器版本和运行 ID。

## 4. 指标定义

设 `N` 为对齐后的全部样本数；`TP_MATCH` 为真值 `MATCH` 且预测 `MATCH` 的样本数；`P_MATCH` 为预测 `MATCH` 的样本数；`G_MATCH` 为真值 `MATCH` 的样本数。

| 指标 | 公式 / 判定 | V0.1 用途 |
|---|---|---|
| `structured_output_valid_rate` | 通过 JSON 解析、Schema、字段枚举、跨字段约束、证据定位校验的样本数 ÷ `N` | Gate |
| `match_precision` | `TP_MATCH ÷ P_MATCH`；把真值 `NEEDS_CONTEXT` 预测成 `MATCH` 计误报 | Gate |
| `match_recall` | `TP_MATCH ÷ G_MATCH` | Gate |
| `match_f1` | `2 × precision × recall ÷ (precision + recall)` | Gate及基线比较 |
| `hard_negative_fpr` | Hard Negative 中预测 `MATCH` 的数量 ÷ Hard Negative 总数 | Gate |
| `needs_context_recall` | 真值 `NEEDS_CONTEXT` 且预测同为 `NEEDS_CONTEXT` 的数量 ÷ 真值 `NEEDS_CONTEXT` 数量 | 必报，V0.1 观察项 |
| `unnecessary_abstention_rate` | 真值非 `NEEDS_CONTEXT` 但预测 `NEEDS_CONTEXT` 的数量 ÷ 真值非 `NEEDS_CONTEXT` 数量 | 必报，风险诊断 |
| `match_subtype_accuracy` | 真值 `MATCH` 中同时预测 `MATCH` 且 `subtype` 正确的数量 ÷ `G_MATCH` | 必报，切片诊断 |
| `evidence_overlap_proxy_recall` | 真值 `MATCH` 中，预测 `MATCH` 且至少一个证据跨度与真值同源区间重叠的数量 ÷ `G_MATCH` | 自动代理指标 |
| `counterfactual_pair_accuracy` | 完整反事实对中两侧均正确的 pair 数 ÷ 合格 pair 总数 | Gate |
| `evidence_hit_rate` | 通过测试组人工或已批准判定规则、同时覆盖必要关键事实的样本数 ÷ 纳入人工核查的真值 `MATCH` 数 | Gate；不可用时必须为 `null` |

### 4.1 结构化输出有效性

以下任一情况都不是“跳过样本”，而是 `INVALID` 并计入全部指标分母：

- 非法 JSON、额外解释文本或多对象输出；
- 缺字段、未知字段、类型或枚举错误；
- `MATCH/NONE`、`NO_MATCH/非 NONE`、`NEEDS_CONTEXT/非 NONE` 等跨字段冲突；
- `MATCH` 无有效证据，或证据不是输入原文的连续子串；
- `NEEDS_CONTEXT` 缺少具体补件问题或未标记人工复核；
- 证据定位与 `document_id`、版本、页码或字符区间不一致。

### 4.2 反事实对

只有以下条件全部满足时才进入 `counterfactual_pair_accuracy` 分母：

- 两侧均存在且同属一个 `pair_id`；
- 两侧同属一个 `leakage_group_id`；
- 金标明确要求翻转；
- 两侧预测是否可解析不影响分母；任一侧 `INVALID` 或缺失时，该 pair 直接判错。

两侧必须分别正确；只答对一侧不算该 pair 正确。反事实对不跨 Train、Dev、Blind Test。

## 5. 强制切片报告

除整体结果外，必须按 Benchmark manifest 中登记的以下切片报告 `N`、各指标、分母和 `null` 原因：

- `case_slice`：典型正例、隐蔽正例、普通负例、Hard Negative、Missing Context、Counterfactual；
- `match_state`：`MATCH`、`NO_MATCH`、`NEEDS_CONTEXT`；
- `subtype`：四类 C1-01 子型及 `NONE`；
- `business_stage`：`QUALIFICATION`、`SCORING`、`TECHNICAL`、`CONTRACT`；
- `parser_quality`：`PASS`、`UNCERTAIN`；
- `case_origin`：真实采集与合成/改写样本（若 manifest 提供）。

切片报告不得在不说明分母的情况下做宏平均或加权总分。`Counterfactual` 既报告逐例状态，也单独报告 pair 级结果，不能把两侧样本当成两个独立成功事件替代 pair 指标。

## 6. Demo Gate V0.1

这是 Demo Gate，不是生产发布结论。除非另有冻结记录，目标阈值如下：

| Gate | 目标 |
|---|---:|
| `structured_output_valid_rate` | 100% |
| Train/Test Leakage | 0 |
| Blind Test 数量 | ≥ 50 |
| `match_recall` | ≥ 90% |
| `match_precision` | ≥ 85% |
| `hard_negative_fpr` | ≤ 15% |
| `evidence_hit_rate` | ≥ 90% |
| `counterfactual_pair_accuracy` | ≥ 90% |
| `match_f1` 相对同快照 Base Model 提升 | ≥ 8 个百分点 |

`needs_context_recall`、`unnecessary_abstention_rate`、`match_subtype_accuracy` 和自动证据代理指标在 V0.1 必须报告，但尚不单独构成 PASS 条件；若出现明显退化，测试组可将其列为阻塞问题。

Gate 采用“全部硬条件通过 + 无阻塞问题”的合取规则，不用加权总分替代。脚本只计算指标，不自动生成 `PASS_DEMO`。最终由测试负责人和项目负责人签署 `GateDecision`。

在 `blind_test_gold` 首次打开前，若确有阈值错误，只能由项目负责人和测试负责人共同形成冻结变更记录；打开真值或产生任何正式盲测结果后，不得为了让模型通过而改门槛。

## 7. 报告最小内容

`EvaluationReport` 至少包含：

```text
run_id
model_version
benchmark_snapshot
metric_spec_version
evaluator_version
input_manifest_hash
prediction_manifest_hash
gold_snapshot_hash（仅测试组内部完整保留）
overall_metrics
slice_metrics
invalid_output_summary
per_example_error_codes
baseline_reference
gate_decision
reviewer_and_timestamp
```

对算法组发布的报告不得暴露 `blind_test_gold` 原文、完整金标文件、未授权的逐例真值导出或可重建金标的调试日志。

## 8. 版本与变更

- 指标公式、分母、非法输出处理和 Gate 阈值均属于冻结接口；
- 修正评测器 bug 必须提升 `evaluator_version`，并保留旧结果；
- 修改标签语义、切片成员、真值或输入协议必须生成新的 Benchmark Snapshot；
- 任何新版本都要重新做泄漏检查、对齐检查和预注册 Gate；
- 历史报告不可被覆盖，只能追加“重算结果”并说明原因。

## 9. 冻结验收

- [ ] 测试组确认公式、分母、`INVALID` 处理和 `null` 规则；
- [ ] 算法组确认可按输出契约提交预测，但不需要访问真值；
- [ ] 数据工程组确认 split、`leakage_group_id`、反事实对和切片元数据可审计；
- [ ] 项目负责人确认 Gate 在打开 Blind Gold 前已冻结；
- [ ] 三方签署日期、版本和内容哈希。
