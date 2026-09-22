# C1-01 Baseline Harness V0.1

**状态：DRAFT；算法组接口联调版，尚未产生 Base Model 成绩。**

## 交付范围与上游版本

本包为 `C1-01_LOCAL_ENTRY_PRECONDITION` 的同一输入、输出与评分接口。语义依据 `BR_C1_01_Business_Task_Spec_V0.1.md`、`C1_01_Label_Guide_V0.1.md`；字段依据包内 `C1_01_Dataset_Schema_V0.1.json` 的快照。每行一个可独立判定的 Requirement。`MATCH` 仅表示 C1-01 候选线索，绝非最终违法认定；`NO_MATCH` 仅排除此项；关键事实缺失时使用 `NEEDS_CONTEXT` 并提出可执行的补件问题。当前业务规范、指南与 Schema 均须经过联合评审才可冻结。

### 模型适配器协议

`harness.py run --adapter-command "python3 model_adapter.py"` 按样本调用适配器。适配器从 **stdin 读取一个 JSON 请求**，向 **stdout 只写一个 JSON 对象**，日志写 stderr；不允许 Markdown 代码围栏、解释或多行附言。每次为一个新进程，输出本身就是 dataset `target` 对象，不能裹在 `target` 或 `prediction` 中。

请求包含 `protocol_version`、`task_id`、`mode`、`instruction`、`input`、`examples`、`output_contract`、`generation`。`input` 严格白名单投影自 dataset 的 `input`；无 `target`、`metadata`、切片名或标签。`output_contract` 是当前 Schema 的 `target` 描述。`examples` 在 zero shot 时为空；few shot 时只选另行审核的 TRAIN 样本，同组不得与 DEV 重叠。适配器实现 Base Model 调用、系统/用户提示词渲染、模型版本锁定与生成参数应用；需将实际 prompt/template hash、模型权重 revision、tokenizer revision、推理框架版本和真实温度/seed 补记在实验登记中。本工具记录 CLI 声明值，不验证适配器是否真的执行该配置。

标准响应所有字段必填，类型/枚举遵循 Schema：

```json
{
  "item_id": "C1-01_LOCAL_ENTRY_PRECONDITION",
  "requirement_id": "REQ-001",
  "match_state": "MATCH",
  "subtype": "SUPPLIER_REGISTRATION_LOCATION",
  "evidence_text": "投标人须在本市注册。",
  "evidence_spans": [{"text":"投标人须在本市注册。","anchor":"CLAUSE","context_id":null,"document_id":"DOC-001","document_version":"V1","page":8,"section":"供应商资格","start_char":0,"end_char":10}],
  "evidence_refs": [{"document_id":"DOC-001","document_version":"V1","page":8,"section":"供应商资格"}],
  "reasoning_factors": ["supplier_location_attribute", "pre_award_condition", "market_entry_gate"],
  "missing_context_questions": [],
  "confidence": null,
  "human_review_required": false
}
```

上述偏移只是接口示意；**实际必须按原文 Python Unicode 字符序号 `[start_char,end_char)` 计算**，`evidence_text` 等于某一段连续原文。跨条款要分别引用 `CLAUSE` 和 `CONTEXT`；各段与 `evidence_refs` 一一对应。`MATCH` 需要非 `NONE` 子型和已定位原文；`NO_MATCH`、`NEEDS_CONTEXT` 子型必须为 `NONE`。后者还需要问题与 `human_review_required=true`。`confidence` 可为 `null`，不得当作违法概率；事实因子为受控枚举，不是内部推理链。

## 运行

仅联调现有待二次复核的原始采购条款（`HOLD`），不评分：

```bash
python3 harness.py run \
  --input C1_01_Original_Clause_Sample_V0.1.jsonl \
  --adapter-command "python3 adapter_stub.py" \
  --model-id STUB --model-revision interface-only \
  --output smoke_predictions.jsonl --manifest smoke_manifest.json --smoke
```

`adapter_stub.py` 永远输出 `NO_MATCH`，只用于验证协议；绝不可作为 Base Model。正式跑 Base Model 时提供真实模型适配器，删除 `--smoke`，输入改为经复核且 `data_eligibility` 已验收、`dataset_role=DEV` 的快照，命令分别固定 zero shot 和 few shot 的独立运行目录。few shot 可增加 `--few-shot-file reviewed_train.jsonl`；只接收已审核 `TRAIN_ELIGIBLE` 的 TRAIN 示例，并拒绝与 DEV 共用 `leakage_group_id`。`run` 输出逐条 `sample_id`、原始响应、解析对象或 null、校验错误和耗时；manifest 写明 schema/input/prediction/few shot 文件哈希、模型标识、数量、声明的采样参数。

DEV 评分接口（输入必须是独立复核且已验收的 Internal Silver；不接受种子 `HOLD`）：

```bash
python3 harness.py score \
  --gold reviewed_dev.jsonl \
  --predictions base_zero_predictions.jsonl \
  --output base_zero_metrics.json
```

测试组的独立环境可在 `BLIND_GOLD` 上使用 `--qa-blind`；算法组不得接触盲测真值，也不得在自己的工作区运行此选项。盲测输入的预测由测试组与隐藏真值按 `sample_id` 对齐后评分。代码选项不是访问控制，真实权限须由文件与团队边界落实。

## 评分定义与限制

所有分母都包含非法格式与缺失判定输出，非法输出记为 `INVALID`，并计入 MATCH 漏检。预测集与真值集必须 ID 完全一致，无重复；错误组无法隐形丢弃。

| 指标 | 定义 |
|---|---|
| `match_precision` | 正确预测 MATCH ÷ 所有预测 MATCH；误把 NEEDS_CONTEXT 判 MATCH 也算误报 |
| `match_recall` | 正确预测 MATCH ÷ 真值 MATCH |
| `match_f1` | 上述二者的调和平均 |
| `hard_negative_fpr` | hard negative 中预测 MATCH ÷ hard negative 总数 |
| `needs_context_recall` | 真值 NEEDS_CONTEXT 中正确弃权的比例 |
| `unnecessary_abstention_rate` | 真值非 NEEDS_CONTEXT 中错误弃权的比例 |
| `structured_output_valid_rate` | 能解析且通过输出约束、证据定位校验的比例 |
| `match_subtype_accuracy` | 真值 MATCH 中同时正确预测 MATCH 和子型的比例 |
| `evidence_overlap_proxy_recall` | 真值 MATCH 中正确预测 MATCH 且至少有一段证据与真值区间同源重叠的比例 |
| `counterfactual_pair_accuracy` | 完整两例、同 leakage group、金标应翻转的反事实对中两侧均正确的比例 |

`null` 表示无合格分母；不要改写成 0 或 100%。证据重叠只是**自动代理指标**，不能声称“同时覆盖身份条件与竞争后果”；测试组须另行人工或经过批准的判定规则核查 Evidence Hit。输出还含每个 slice 的数量和 exact state、逐例错误清单。正式 Demo Gate 指标与阈值由项目负责人和测试组在打开盲测真值前冻结；脚本不自动给 `PASS_DEMO`。小样本 smoke 不代表准确率，更不代表微调增益。

## 当前输入状态与下一步

数据组已完成 Schema 和一条可追溯原始条款样本，但该样本 `PENDING_SECOND_PASS`、`HOLD`、`UNASSIGNED`。29 条种子为改写/合成、均 `HOLD`，含一条业务边界争议，不能用于 Base Model 正式对比。等待业务联合冻结标签与数据组交付分组隔离的 DEV / TRAIN 快照；算法组此时可对接真实 Base Model 适配器并做协议 smoke，之后在同一 DEV 上固定 Base zero/few shot 的配置、完整预测和 BaselineReport。
