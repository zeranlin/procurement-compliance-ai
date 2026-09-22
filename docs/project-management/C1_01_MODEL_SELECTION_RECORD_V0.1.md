# C1-01 Model Selection Record V0.1

**任务**：`C1-01_LOCAL_ENTRY_PRECONDITION`  
**基线**：`67948a8`（Gate-A 已冻结）  
**记录状态**：`CANDIDATE_SELECTION_ONLY`  
**Owner**：项目总控 + 03 算法/平台组  
**限制**：本记录不下载模型、不调用 API、不运行推理或训练。

## 1. 选择结论

| 用途 | 首选/候选 | 精确标识 | 角色 | 当前状态 |
|---|---|---|---|---|
| Base / Student 首选 | Qwen post-trained | `Qwen/Qwen3.5-4B` | Base baseline、后续 Student | 首选；Gate-B 环境待交付 |
| 可选消融 | Qwen Base | `Qwen/Qwen3.5-4B-Base` | 仅消融对照 | 非默认；需相同 Snapshot/配置 |
| Teacher | DeepSeek V4.1 Flash | API `model=deepseek-flash` | 仅生成 Silver candidate | 仅候选；不得作为 Gold 权威 |

Qwen 首选配置约束：`text-only`、`non-thinking`。任何开启 thinking、改变输入模态或替换 revision 的运行都必须作为新的模型候选登记，不得冒充本记录的同一运行。

## 2. 角色边界

### Base / Student

- Base 首先用于 Zero-shot / Few-shot 基线，比较业务边界、Hard Negative、NEEDS_CONTEXT、证据和结构化输出错误；
- Student 只有在 Base 结果完成、DEV 误差分析完成、Training Decision 明确为 GO 后，才可申请 LoRA/QLoRA；
- Base 与 Student 必须使用同一冻结 MetricSpec、同一 Benchmark Snapshot 规则和可比的 generation config；
- Student 不得接收 Blind Gold、逐例 Gold 反馈或测试组隐藏切片信息。

### Teacher

- `deepseek-flash` 只能生成带完整 lineage 的 `INTERNAL_SILVER` 候选；
- Teacher 输出必须记录 API model、调用时间、prompt/template hash、输入来源、输出 hash、过滤规则和审核状态；
- Teacher 输出必须经过 Schema、业务规则、来源核查、去重、leakage 和人工/QA 闸门；
- Teacher 输出不能直接写入 `TRAIN`、`DEV`、`BENCHMARK_CANDIDATE` 或 `blind_test_gold`；
- Teacher 不是事实权威，不得把模型一致性、置信度或多数票当作 Gold 证明；
- Teacher 不得接触 Blind Gold、隐藏切片、泄漏组或可逆真值派生字段。

## 3. 选择理由与验证项

| 候选 | 选择理由 | 必须验证 | 淘汰/暂停条件 |
|---|---|---|---|
| `Qwen/Qwen3.5-4B` | 作为 text-only、non-thinking 的统一 Base/Student 候选，便于先测基线再决定训练 | revision、tokenizer、framework、硬件、context、generation config、协议 adapter | revision 不可固定、环境不可复现、输出契约不稳定 |
| `Qwen/Qwen3.5-4B-Base` | 用于回答“post-trained 能力与 Base 能力差异”这一可选消融问题 | 与首选相同的输入、Snapshot、指标、随机性和资源约束 | 只能作为消融；不得替代首选结论或增加未注册变量 |
| `deepseek-flash` | 作为候选 Silver 生成器，不占用 Gold 权威角色 | API model、request/response hash、限额、脱敏、lineage、人工/QA 审核 | 输出无来源、无法审计、接触 Gold、自动升格标签 |

## 4. 授权顺序

```text
数据就绪
    ↓
Benchmark Snapshot / Blind 隔离 / ACL 就绪
    ↓
Base Model Zero-shot / Few-shot
    ↓
DEV 误差分析与 Training Decision
    ↓
LoRA / QLoRA（仅 PM 明确授权）
```

任何“先生成 Teacher 数据再训练”“先微调再补 Benchmark”“用 Blind 结果改 Prompt/标签”的流程均不被本记录授权。

## 5. 当前判定

```text
MODEL_SELECTION = RECORDED
MODEL_ENVIRONMENT = NOT_READY
MODEL_RUN = NOT_AUTHORIZED
TEACHER_API_CALL = NOT_AUTHORIZED
TRAINING = NOT_AUTHORIZED
```
