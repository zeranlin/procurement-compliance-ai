# C1-01 Baseline Protocol V0.2.1

**状态：`FROZEN`**  
**生效日期：2026-09-22**  
**任务：`C1-01_LOCAL_ENTRY_PRECONDITION`**  
**责任方：算法组；依赖由业务组、数据工程组、测试与评测组共同冻结**

## 1. 冻结结论

本文件保留 `C1_01_Baseline_Protocol_V0.2` 的历史冻结内容，并发布其不可覆盖的 dependency patch `V0.2.1`。本 patch 只将 BenchmarkMetricSpec 从 V0.1 重绑定到已冻结的 V0.2；输入资格、版本与 hash 绑定、模型请求投影、严格 prediction 输出、Preflight Gate、非法输出记录方式和评分入口保持不变。冻结对象不是某一个 Base Model 的能力结果，也不包含 Fine-tune、Prompt 调优或 Blind Test 结果。

算法组在本版本只执行 `Protocol Integration`。正式 Base Model Run 必须先通过 Preflight；Preflight 有一项失败，运行状态为 `RUN_ABORTED`，适配器不得被调用。

### 1.1 Patch lineage

| 字段 | 固定值 |
|---|---|
| `previous_version` | `C1_01_Baseline_Protocol_V0.2` |
| `change_reason` | `ALG-PATCH-01`：修正 stale MetricSpec dependency；不改 MetricSpec 语义 |
| `change_scope` | protocol/lock/preflight/run-manifest/dependency-registry/hash-chain |
| `history_policy` | V0.2 原文件与原 hash 保留，不静默覆盖 |

## 2. 依赖锁定

运行清单必须同时保存下列字段：`spec_version` / `spec_hash`、`label_guide_version` / `label_guide_hash`、`schema_version` / `schema_hash`、`metric_spec_version` / `metric_spec_hash`。`blind_test_rules` 和 `blind_gold_boundary` 是额外的权限依赖，也锁定版本与 hash。

| 依赖 | 版本 | SHA-256 | 状态 |
|---|---|---|---|
| BusinessTaskSpec | `BR_C1_01_Business_Task_Spec_V0.1` | `0fa169fa0fa34ef8e702c4cae8e10e89cdce4260aa198f7a45a4a28d5c3a74ab` | `FROZEN` |
| LabelGuide | `C1_01_Label_Guide_V0.1` | `9b6352b5f6e400f2ad9ecca1cead4e26b03b3e81b8e6f761276b15ac3ffd67a6` | `FROZEN` |
| DatasetSchema | `C1_01_Dataset_Schema_V0.2` | `484cb50e52e337d24cd014db9ddf1af98d5d82fee9706c512307bb8190da25fb` | `FROZEN` |
| BenchmarkMetricSpec | `C1_01_Benchmark_Metric_Spec_V0.2` | `cb443a64178fb894d751bc02dbc6fc9f142e33a9e2130a121ab9e0a881f64a7d` | `FROZEN_FOR_SCHEMA_V0.2_COMPATIBILITY` |
| Blind Test Management | `C1_01_Blind_Test_Management_Rules_V0.1` | `43514c360ff21586e13f0e91c91eae21459c8a157e816c092f3d462ccdca667a` | `FROZEN` |
| Blind Gold Access Boundary | `C1_01_Blind_Test_Gold_Access_Boundary_V0.1` | `6b6a895c29703f1a66df22fb6fdab884b197ed085abdea7dad16f543d3fe2338` | `FROZEN` |

机器可读锁定内容在 `C1_01_Baseline_Protocol_V0.2.1.lock.json`；六资产登记也复制到 `C1_01_Protocol_Dependency_Registry_V0.2.1.json`。Preflight 按文件字节计算 SHA-256；版本或 hash 任一不一致都中止运行。

## 3. Dataset Candidate 与 Model Prediction 的边界

Dataset Schema V0.2 把记录分成两种状态：

```text
LABELED
  target = MATCH | NO_MATCH | NEEDS_CONTEXT

UNAVAILABLE_SOURCE_REWORK
  target = null
  parser_quality = UNCERTAIN
  data_eligibility = REWORK_SOURCE
```

`UNAVAILABLE_SOURCE_REWORK` 是 Dataset Snapshot 形成前的无效任务候选，必须：

- 不送模型正式推理；
- 不进入 TRAIN、DEV、BLIND_INPUT 或 BLIND_GOLD；
- 不作为 few-shot；
- 不参加评分分母。

这与模型产生的非法预测不同。非法 JSON、额外文本、字段错误、证据偏移错误或缺失预测，属于 `INVALID` Model Prediction：它们保留在预测文件中，进入结构化有效率和适用指标分母；`MATCH` Recall 按漏检处理。Harness 不删除、修复、猜测或静默重试。

正式 Base Model 输入必须满足：`annotation_state=LABELED`、`target` 非空、`parser_quality=PASS`、`review_state=INTERNAL_REVIEWED`、`data_eligibility` 与 split 相符、来源证据已核验，并且不得含 `HOLD`、`DISPUTED`、`REWORK_SOURCE` 或 `BLIND_GOLD`。

### 3.1 MetricSpec binding invariant

本协议只绑定 `C1_01_Benchmark_Metric_Spec_V0.2`，不重新定义或实现其指标语义。因而：

- Dataset / Assembly Invalid（包括 `REWORK_SOURCE`、`target=null`、`HOLD`、`DISPUTED`、`PENDING_DATA_QA`）在 Snapshot 形成前拒绝，不进入 Prediction 或评分；
- 已入 Snapshot 的 Model Prediction Invalid 保留 `sample_id` 和原始输出，计入 `structured_output_valid_rate` 分母，并在适用情况下作为 `MATCH` 漏检；
- Harness 不把 `REWORK_SOURCE` 改成 `NEEDS_CONTEXT`，不把非法输出补成 `NO_MATCH`，不删除缺失 prediction，也不自动修复 JSON。

## 4. Model Input Protocol

模型只接收每个 Requirement 的白名单输入：

```json
{
  "protocol_version": "0.2.1",
  "task_id": "C1-01_LOCAL_ENTRY_PRECONDITION",
  "mode": "zero_shot",
  "instruction": "Return ONLY one JSON object matching output_contract...",
  "input": {
    "requirement_id": "REQ-001",
    "project_id": "P-001",
    "document_id": "DOC-001",
    "document_version": "V1",
    "clause_id": "CL-001",
    "clause_text": "投标人须在本市注册。",
    "business_stage": "QUALIFICATION",
    "context": null,
    "source_location": {"page": 8, "section": "供应商资格"},
    "parser_quality": "PASS",
    "source_defect_prevents_judgment": false,
    "source_defect_reason": null
  },
  "examples": [],
  "output_contract": "C1_01_Model_Output_Schema_V0.2",
  "generation": {"temperature": 0.0, "seed": 42}
}
```

`target`、`metadata`、`annotation_state`、`data_eligibility`、`dataset_role`、切片标签和盲测真值不会进入模型请求。few-shot 示例只允许来自已经通过资格检查的 TRAIN 记录；不得与 DEV 或 BLIND_INPUT 共用 `leakage_group_id` 或 `pair_id`。

## 5. Frozen Model Output Protocol

模型 stdout 必须是**一个裸 JSON 对象**，字段集合必须与 `C1_01_Model_Output_Schema_V0.2.json` 完全相同：

```json
{
  "item_id": "C1-01_LOCAL_ENTRY_PRECONDITION",
  "requirement_id": "REQ-001",
  "match_state": "MATCH",
  "subtype": "SUPPLIER_REGISTRATION_LOCATION",
  "evidence_text": "投标人须在本市注册。",
  "evidence_spans": [{"text":"投标人须在本市注册。","anchor":"CLAUSE","context_id":null,"document_id":"DOC-001","document_version":"V1","page":8,"section":"供应商资格","start_char":0,"end_char":10}],
  "evidence_refs": [{"document_id":"DOC-001","document_version":"V1","page":8,"section":"供应商资格"}],
  "reasoning_factors": ["supplier_location_attribute","pre_award_condition","market_entry_gate"],
  "missing_context_questions": [],
  "confidence": null,
  "human_review_required": false
}
```

Harness 严格禁止：

- Markdown fence；
- JSON 前后的自然语言；
- 多个 JSON 对象或 wrapper（包括 `{ "target": {...} }`、`{ "prediction": {...} }`）；
- `违法`、`合法`、`处罚`、法条责任判断等额外字段；
- 把私有思维链放进 `reasoning_factors`。

`evidence_spans` 的 `start_char` / `end_char` 是 Python Unicode 字符的半开区间 `[start_char,end_char)`，必须与输入原文连续子串完全相等；`evidence_refs` 与跨度逐项对应。`MATCH` 必须使用非 `NONE` 子型；`NO_MATCH` 和 `NEEDS_CONTEXT` 必须使用 `NONE`；`NEEDS_CONTEXT` 必须有具体问题且 `human_review_required=true`。

## 6. Preflight Gate

`C1_01_Preflight_Check_V0.2.1.py` 在模型调用前执行：

1. Protocol manifest 状态为 `FROZEN`，协议版本正确；
2. BusinessTaskSpec、LabelGuide、DatasetSchema、BenchmarkMetricSpec 的版本和 SHA-256 完全匹配；
3. Blind Test 管理规则和 Gold 权限边界的版本和 hash 完全匹配；
4. Model Output Schema hash 完全匹配；
5. TRAIN、DEV、BLIND_INPUT 均存在，且每行符合 Dataset Schema V0.2 的可训练／可评测状态；
6. 无 `UNAVAILABLE_SOURCE_REWORK`、`target=null`、`REWORK_SOURCE`、`HOLD`、`PENDING_DATA_QA`、`DISPUTED` 或 `BLIND_GOLD`；
7. TRAIN、DEV、BLIND_INPUT 的 `leakage_group_id` 不交叉，反事实 `pair_id` 不跨 split；
8. 只有以上全部通过，才允许启动 Base Model adapter。

任何失败均返回 `RUN_ABORTED`。Preflight 失败时不会“先跑一下看看”，不会产生可被误读为基线的预测文件。

## 7. 运行、评分和审计

正式运行入口：

```bash
python3 harness.py run \
  --manifest C1_01_Baseline_Protocol_V0.2.1.lock.json \
  --train train.jsonl --dev dev.jsonl --blind-input blind_test_input.jsonl \
  --adapter-command "python3 model_adapter.py" \
  --model-id BASE-MODEL-X --model-revision REVISION \
  --output baseline_predictions.jsonl \
  --run-manifest baseline_run_manifest.json
```

Harness 将保存每个 `sample_id` 的原始 stdout、解析结果、校验错误和耗时。正式 run 清单必须记录四项核心依赖的 version/hash、模型标识、输入 hash、预测 hash、zero/few-shot 模式及调用数量。`--few-shot` 只能接收已通过 Preflight 的 TRAIN 文件。

评分入口保留非法输出：

```bash
python3 harness.py score \
  --gold reviewed_dev.jsonl \
  --predictions baseline_predictions.jsonl \
  --output baseline_metrics.json
```

测试组在隔离环境中才可对 `BLIND_GOLD` 使用 `--qa-blind`；算法组不得读取真值或调用该选项。脚本报告 `structured_output_valid_rate`、`match_precision`、`match_recall`、`match_f1`、`hard_negative_fpr`、`needs_context_recall`、证据重叠代理指标和反事实 pair 指标。分母为 0 时为 `null`。

## 8. 本轮验收

协议包内 Stub 仅用于接口 smoke，不代表 Base Model，也不产生模型效果结论。验收矩阵：

| 场景 | 预期 |
|---|---|
| 合法 `MATCH` | `VALID` / `PASS` |
| 合法 `NO_MATCH` | `VALID` / `PASS` |
| 合法 `NEEDS_CONTEXT` | `VALID` / `PASS` |
| `REWORK_SOURCE` | `REFUSED_INPUT`，adapter 不被调用 |
| 非法 JSON | `INVALID`，保留在预测记录 |
| Schema hash 不匹配 | Preflight `RUN_ABORTED` |
| 版本/hash 不匹配 | Preflight `RUN_ABORTED` |

测试命令：

```bash
python3 harness.py smoke \
  --manifest C1_01_Baseline_Protocol_V0.2.1.lock.json \
  --adapter-command "python3 adapter_stub.py" \
  --output protocol_smoke_report.json
```

Protocol V0.2.1 完成后，下一步仍需等待算法组和测试组共同提供符合锁定版本的正式 TRAIN / DEV / BLIND_INPUT Snapshot；本文件不授权 Fine-tune，也不授权反复运行 Blind Test。完成后交由 04 QA 进行 Contract Compatibility、Traceability Verification 和 Freeze Manifest 增量复验。
