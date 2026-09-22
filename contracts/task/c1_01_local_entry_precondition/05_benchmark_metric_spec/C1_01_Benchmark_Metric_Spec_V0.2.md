# C1-01 Benchmark Metric Spec V0.2

**文档状态：`FROZEN`**
**生效日期：2026-09-22**
**适用范围：C1-01 同一 Benchmark Snapshot 的 DEV / Blind 评测**

V0.2 是与 Baseline Protocol V0.2 的接口对齐版本：明确 canonical `INVALID`、全量分母和对齐失败处理。它不改变 V0.1 已冻结的业务标签语义、阈值、切片意义或 Gold 访问边界。

## 1. 对齐规则

- 预测与真值按 `sample_id` 精确对齐；缺失、重复、未知 ID 是评测错误，不能按文件顺序修复或丢弃。
- 每个对齐样本都有一个状态：`MATCH`、`NO_MATCH`、`NEEDS_CONTEXT` 或 `INVALID`。
- 非法 JSON、额外文本、字段/枚举/跨字段错误、证据定位错误均为 `INVALID`；保留样本并计入所有适用分母。
- `REWORK_SOURCE`、`HOLD`、`PENDING_DATA_QA`、`DISPUTED` 不得进入 Benchmark Snapshot；它们在数据组装/Preflight 阶段阻断，而不是当作模型 `INVALID`。
- 所有分母为零的指标返回 `null`。
- `evidence_hit_rate` 由测试组人工或批准规则产生，算法侧不得自行填充。

## 2. 指标

设 `N` 为完整对齐样本数，`TP_MATCH` 为真值与预测均为 `MATCH` 的样本数，`P_MATCH` 为有效预测为 `MATCH` 的样本数，`G_MATCH` 为真值 `MATCH` 数。

| 指标 | 定义 |
|---|---|
| `structured_output_valid_rate` | 有效结构化输出数 ÷ `N` |
| `match_precision` | `TP_MATCH ÷ P_MATCH` |
| `match_recall` | `TP_MATCH ÷ G_MATCH`；`INVALID` 是漏检 |
| `match_f1` | precision 与 recall 的调和平均 |
| `hard_negative_fpr` | Hard Negative 中预测 `MATCH` 数 ÷ Hard Negative 总数 |
| `needs_context_recall` | 真值 `NEEDS_CONTEXT` 且预测同态数 ÷ 真值 `NEEDS_CONTEXT` 数 |
| `unnecessary_abstention_rate` | 真值非 `NEEDS_CONTEXT` 却预测 `NEEDS_CONTEXT` 数 ÷ 真值非 `NEEDS_CONTEXT` 数 |
| `match_subtype_accuracy` | 真值 `MATCH` 中预测 MATCH 且 subtype 正确数 ÷ `G_MATCH` |
| `evidence_overlap_proxy_recall` | 真值 MATCH 中预测 MATCH 且证据源区间重叠数 ÷ `G_MATCH` |
| `counterfactual_pair_accuracy` | 完整、同 leakage group 且金标状态翻转的 pair 两侧均正确数 ÷ 合格 pair 数 |
| `evidence_hit_rate` | 通过测试组人工/批准规则的必要事实证据数 ÷ 纳入人工核查的真值 MATCH 数 |

## 3. Gate 与报告

V0.2 保持现有 Demo Gate 阈值和合取规则：结构化有效率 100%、无泄漏、Blind N≥50、MATCH recall≥90%、precision≥85%、Hard Negative FPR≤15%、Evidence Hit≥90%、Counterfactual Pair Accuracy≥90%、相对同快照 Base Model 的 MATCH F1 提升≥8 个百分点。所有硬条件通过且无阻塞项才可进入 Gate Decision；脚本不自动生成 `PASS_DEMO`。

报告至少记录：`run_id`、模型版本、Snapshot、Metric Spec 版本、评测器版本、输入/预测哈希、整体与切片指标、`INVALID` 摘要、逐例错误码、Base Model 对照、Gate Decision、审核人与时间。对算法组发布的报告不得包含盲测 Gold 原文或可重建真值的派生物。

## 4. 版本变更

公式、分母、`INVALID` 处理、阈值、切片语义或输入协议变化必须生成新的 Metric Spec / Benchmark Snapshot，并重新做泄漏、对齐和预注册 Gate 检查。修复评测器 bug 只提升 `evaluator_version`，不得覆盖历史结果。
