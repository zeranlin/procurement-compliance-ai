# C1-01 Benchmark Metric Spec V0.2

**文档状态**：`FROZEN_FOR_SCHEMA_V0.2_COMPATIBILITY`  
**生效日期**：2026-09-22  
**责任团队**：测试与评测组  
**任务 ID**：`C1-01_LOCAL_ENTRY_PRECONDITION`  
**上位版本**：`C1_01_Benchmark_Metric_Spec_V0.1`（保持不可变）  
**适用范围**：`C1_01_Dataset_Schema_V0.2` 对应的 Benchmark Assembly 与 Blind Test

## 1. 版本目的

V0.2 只处理 Dataset Schema V0.2 引入的生命周期兼容性，不改变业务标签语义、不降低任何 Demo Gate、不修改 V0.1 的指标公式。

本版本新增并冻结一个必要区分：

```text
Prediction Invalid
!=
Benchmark Assembly Invalid
```

V0.1 保留为历史冻结版本，不能原地改写。任何使用 Schema V0.2 的 Benchmark Snapshot 必须引用本 V0.2 规范并登记其内容哈希。

## 2. Benchmark Snapshot Eligibility Rule

一条记录只有同时满足以下条件，才可进入 `BenchmarkSnapshot` 的候选集合：

```text
parser_quality       = PASS
review_state         = INTERNAL_REVIEWED
data_eligibility     = BENCHMARK_CANDIDATE
target               != null
```

并且必须满足 Schema V0.2 的结构与来源不变量：

```text
annotation_state                    = LABELED
input.source_defect_prevents_judgment = false
metadata.evidence_status            = VERIFIED
```

`target != null` 是必要条件，但不是充分条件。仅有 target、Schema 校验通过或业务组暂定标签，均不能绕过 Benchmark Eligibility。

### 2.1 明确排除

以下任一状态的记录必须在 Freeze 前挡掉：

```text
REWORK_SOURCE
PARSE_FAILURE
DISPUTED
HOLD
PENDING_DATA_QA
```

其中：

- `REWORK_SOURCE` / `PARSE_FAILURE` 表示输入原文、OCR、表格关系或来源证据不足，不能形成可靠监督 target；
- `DISPUTED`、`HOLD`、`PENDING_DATA_QA` 表示尚未完成业务裁决、来源核验或数据验收；
- 即使这些记录暂时带有 target，也不得进入 Blind Gold；
- 被排除记录进入 `Benchmark Assembly Audit`，但不进入预测评分分母。

## 3. 两类 Invalid 的规范边界

| 类型 | 发生层级 | 触发条件 | `sample_id` | 是否进入评分分母 | 处理 |
|---|---|---|---|---|---|
| `Benchmark Assembly Invalid` | Freeze 前 | 候选记录不满足 Eligibility；含 `REWORK_SOURCE`、`PARSE_FAILURE`、`DISPUTED`、`HOLD`、`PENDING_DATA_QA`、`target=null` 或来源不可靠 | 保留在 Assembly Audit，不生成正式 Prediction 请求 | 否 | 阻止入 Snapshot；修复后新建/重建 Snapshot |
| `Prediction Invalid` | Freeze 后 | 对已入 Snapshot 的合格 sample，模型输出非法 JSON、缺字段、枚举冲突、证据定位非法、缺失或重复/未知 ID | 必须保留 | 是；影响 `structured_output_valid_rate`，并在适用情况下计漏检 | 记 `INVALID` 与错误码，不删除样本 |

### 3.1 `REWORK_SOURCE` 的强制规则

`REWORK_SOURCE` 不是 `Prediction Invalid`，而是 `Benchmark Assembly Invalid`：

```text
REWORK_SOURCE
    → 不送模型正式推理
    → 不生成 Prediction
    → 不参加评分
    → 不作为 few-shot
    → 不作为 DEV
    → 不作为 BLIND_GOLD
```

如果系统在 Assembly 已拒绝后仍收到该 `sample_id` 的预测，记录为 `UNEXPECTED_PREDICTION_FOR_EXCLUDED_SAMPLE`，不得把它重新纳入预测指标。

### 3.2 `Prediction Invalid` 的强制规则

对已经通过 Eligibility、进入冻结 Snapshot 的 sample：

- 保留原 `sample_id` 和提交位置；
- 非法输出记为 `INVALID`，不能丢弃、补写默认标签或改成 `NO_MATCH`；
- 计入 `structured_output_valid_rate` 的总分母；
- 在 `match_recall` 等适用指标中按漏检处理；
- `match_precision` 仍按“预测为 MATCH 的样本”定义，不把 INVALID 伪装成 MATCH；
- 记录具体错误码、原始响应哈希和运行 ID，原始响应不得进入算法组报告。

## 4. 评测输入与对齐

预测集与冻结真值集必须满足：

- `sample_id` 集合完全一致；
- 无缺失、重复或未知 ID；
- 预测输入只来自 `blind_test_input` 和冻结输出契约；
- 不向模型提供 target、切片名、`leakage_group_id`、`label_authority` 或真值派生字段；
- Assembly Invalid 不出现在正式预测集，Prediction Invalid 不能改变冻结样本集合。

## 5. 指标与 Gate 保持不变

V0.2 继续使用 V0.1 的指标公式和 Gate，不降低阈值：

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

`Benchmark Assembly Invalid` 不计入上述预测指标分母；`Prediction Invalid` 按第 3.2 节处理。脚本不能自动给出 `PASS_DEMO`，也不能用排除 Assembly Invalid 的方式制造可通过的样本集。

## 6. Freeze 前 Preflight

每次组装 Snapshot 必须按以下顺序执行：

1. Schema 版本与 `schema_sha256` 检查；
2. Eligibility 四项硬条件检查；
3. `annotation_state`、source defect、evidence status 交叉字段检查；
4. `REWORK_SOURCE`、`PARSE_FAILURE`、`DISPUTED`、`HOLD`、`PENDING_DATA_QA` 排除检查；
5. 项目/模板/`leakage_group_id` 去重与 split 隔离；
6. 反事实 pair 不跨 split；
7. Blind input 与 Gold 生成并分别计算哈希；
8. BusinessTaskSpec、LabelGuide、DatasetSchema、BaselineProtocol、MetricSpec、Snapshot 六项哈希全部登记；
9. 任一失败即 `FREEZE ABORTED`，不产生可宣称 Frozen 的 Benchmark Snapshot。

## 7. 兼容性验收

- [ ] Schema V0.2 的 nullable target 能表达 `UNAVAILABLE_SOURCE_REWORK`；
- [ ] `target=null` 不会被误读为 `NEEDS_CONTEXT`；
- [ ] `REWORK_SOURCE` 在 Assembly 层被排除，不进入 Prediction Invalid 统计；
- [ ] 合格 sample 的非法预测保留 `sample_id` 并计入结构化有效率；
- [ ] 预测缺失、重复和未知 ID 不会被静默丢弃；
- [ ] Gate 阈值与 V0.1 完全一致；
- [ ] 评测器版本、六项资产哈希和 Snapshot 哈希可追溯。

