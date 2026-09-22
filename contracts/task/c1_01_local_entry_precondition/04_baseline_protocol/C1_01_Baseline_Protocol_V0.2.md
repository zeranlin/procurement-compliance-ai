# C1-01 Baseline Protocol V0.2

**状态：FROZEN**
**生效日期：2026-09-22**
**任务：`C1-01_LOCAL_ENTRY_PRECONDITION`**

本版本是 Baseline Harness 的可执行协议。它只统一输入投影、裸 JSON 输出、资格门禁和评测交接，不改变 Business Task、Label Guide、Dataset Schema 或 Benchmark Metric Spec 的业务语义。

## 1. 依赖与版本

运行必须通过同目录的 `C1_01_Baseline_Protocol_V0.2.1_Dependency_Lock.json`。锁文件逐项记录六项上游资产、运行脚本和 SHA-256；任何哈希不匹配都使 Preflight 失败。锁文件本身不作为自己的依赖，避免自引用。

当前协议依赖：

| 资产 | 版本 | 用途 |
|---|---|---|
| Business Task Spec | `V0.1` | 任务范围 |
| Label Guide | `V0.1` | 标签与证据语义 |
| Dataset Schema | `V0.1` | 数据字段与条件约束 |
| Baseline Protocol | `V0.2` | 本协议 |
| Benchmark Metric Spec | `V0.2` | 指标、分母、`INVALID` 处理 |
| Blind Test Rules / Access Boundary | `V0.1` | 访问边界；算法组不读 Gold |

## 2. 输入资格与 Preflight Gate

Harness 可读取 Dataset 行，但只将 `input` 的白名单字段投影给模型：

```text
requirement_id, project_id, document_id, document_version, clause_id,
clause_text, business_stage, context, source_location, parser_quality
```

以下字段绝不进入模型请求：`target`、`metadata`、`leakage_group_id`、`case_slice`、`label_authority` 及其派生字段。

Preflight 必须通过：

- 依赖锁存在且所有 SHA-256 匹配；
- `sample_id` 无重复，输入行可解析；
- 正式执行仅接受 `data_eligibility=BENCHMARK_CANDIDATE`、`parser_quality=PASS`、`review_state=INTERNAL_REVIEWED`，且角色为 `DEV`、`BLIND_INPUT` 或 `REGRESSION`；
- `REWORK_SOURCE` 必须为 `target=null`，并始终拒绝送模；`REWORK_SOURCE`、`HOLD`、`PENDING_DATA_QA`、`DISPUTED` 不得进入正式 Baseline；
- `BLIND_GOLD`、包含保护 Gold 路径的输入在打开文件前拒绝；
- Few-shot 仅接受 `TRAIN` + `TRAIN_ELIGIBLE`，并且 `leakage_group_id` 与评测输入完全不重叠；
- `target=null` 仅可用于 `BLIND_INPUT` 或 `REWORK_SOURCE`，不作为正常 DEV 标签。

`--smoke` 只放宽本地协议联调样本的资格状态，仍执行裸 JSON、字段和证据校验；它不产生模型成绩，也不解锁训练或盲测。

## 3. Adapter I/O

Harness 为每条样本启动一个 adapter 进程，通过 stdin 发送一个 JSON request。adapter 的 stdout 必须是**唯一一个裸 JSON 对象**，不得有 Markdown 围栏、解释、前后缀或第二个 JSON 对象；日志可写 stderr。

请求固定包含：

```json
{
  "protocol_version": "C1_01_Baseline_Protocol_V0.2",
  "task_id": "C1-01_LOCAL_ENTRY_PRECONDITION",
  "mode": "ZERO_SHOT",
  "instruction": "...",
  "input": {"...": "whitelisted input only"},
  "examples": [],
  "output_contract": {"type": "object", "additionalProperties": false},
  "generation": {"temperature": 0.0, "seed": 0}
}
```

stdout 直接就是 Dataset `target` 对象，不得再包在 `target`、`prediction` 或 `answer` 中。Harness 输出的预测 JSONL 增加 `sample_id`、解析对象、校验错误、耗时，以及原始 stdout 的 SHA-256 与长度；不原样持久化 stdout，避免意外记录 Token、密钥或密码。

## 4. Prediction Contract

预测对象必须包含 Dataset Schema `target` 的全部字段、不得含未知字段。跨字段规则与 Schema 一致：

```text
MATCH          → subtype != NONE，至少一段可回溯证据，不能有补件问题
NO_MATCH       → subtype = NONE，不得有补件问题
NEEDS_CONTEXT  → subtype = NONE，至少一个具体补件问题，human_review_required=true
```

每个证据 span 必须是输入 `clause_text` 或 `context` 的连续 Unicode 字符区间 `[start_char,end_char)`，并与 document、version、page、section 及对应 `evidence_ref` 一致。非法 JSON、未知字段、跨字段冲突和证据定位失败都保留为 `INVALID`，不得静默丢行。

## 5. Benchmark 交接

Harness 的 `score` 只用于 DEV / Regression；它严格按 `C1_01_Benchmark_Metric_Spec_V0.2` 对齐 `sample_id`，预测缺失、重复、未知 ID 都失败。有效性分母为对齐后的全量样本，`INVALID` 计入分母并在 `match_recall` 中形成漏检。分母为零返回 `null`。

`evidence_hit_rate` 需要测试组人工或已批准规则，算法 Harness 返回 `null`，不自行替代该指标。Harness 不生成 `PASS_DEMO`，也不读取或推断盲测真值。

## 6. 可重复 smoke 命令

在本目录执行：

```bash
python3 harness.py preflight \
  --input fixtures/C1_01_Baseline_Smoke_Input_V0.2.jsonl --smoke

python3 harness.py run \
  --input fixtures/C1_01_Baseline_Smoke_Input_V0.2.jsonl \
  --adapter-command "python3 adapter_stub.py" \
  --model-id STUB --model-revision interface-only \
  --output /tmp/c1_01_smoke_predictions.jsonl \
  --manifest /tmp/c1_01_smoke_manifest.json --preflight-report /tmp/c1_01_smoke_preflight.json --smoke
```

该 stub 永远返回 `NO_MATCH`，只验收接口，不是 Base Model，也不代表任何准确率。
