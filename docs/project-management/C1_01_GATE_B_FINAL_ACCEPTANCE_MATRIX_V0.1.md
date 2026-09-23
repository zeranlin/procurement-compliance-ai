# C1-01 Gate-B Final Acceptance Matrix V0.1

**基线**：Gate-A 最终冻结 `67948a8`  
**评审对象**：Gate-B Data / Benchmark Readiness  
**当前判定**：`PENDING / REVIEW_DEFERRED`
**原则**：Gate-A 的 `contract_ready=true` 不等于 Gate-B 的 `benchmark_ready=true`。

## 1. 总体验收矩阵

| Gate-B 项 | 入口条件 | 必需证据 | Owner | 退出条件 | 当前 |
|---|---|---|---|---|---|
| GB-01 数据候选资格 | Gate-A hash 不变 | Schema/Cross-field、来源、证据、角色、pair/leakage、去重报告 | 02 | 所有候选记录满足资格，隔离争议/源件修复 | PENDING：1 条暂代复核，402 条待复核 |
| GB-02 Train/Dev 准入 | GB-01 PASS | split manifest、role allowlist、source lineage、数量与 hash | 02 | 无 `DISPUTED/HOLD/REWORK_SOURCE` 越权，项目/模板泄漏为 0 | BLOCKED_BY_DEFERRED_REVIEW |
| GB-03 Benchmark Snapshot | GB-01/02 PASS | snapshot ID、input/gold hash、split、metric/evaluator hash、freeze record | 04 | Snapshot 不可变，版本与内容一致 | PENDING |
| GB-04 Blind Gold 隔离 | GB-03 组装完成 | 存储/挂载/备份/缓存清单，算法侧脱敏 input | 04 | 非 QA 角色不能读取 Gold 或真值派生物 | PENDING |
| GB-05 Runtime ACL | GB-04 | 正向/拒绝 Probe、service account、audit log、告警 | 04 | 允许/拒绝矩阵全部符合，审计证据完整 | PENDING |
| GB-06 Isolated Evaluator | GB-03/04 | evaluator version/hash、依赖、运行命令、输出 schema | 04 | 独立评测器可复现，输出不泄漏逐例 Gold | PENDING |
| GB-07 Metric/Gate 注册 | Gate-A MetricSpec 固定 | 指标版本、阈值、分母规则、变更控制 | 04/PM | Snapshot 前预注册，模型结果不能改 Gate | Gate-A PASS；B runtime PENDING |
| GB-08 模型环境 | Gate-A 协议固定 | Qwen revision、tokenizer、framework、硬件、adapter、config | 03 | 环境清单可复现；不读取 Gold | PENDING |
| GB-09 Gate-B 联合评审 | GB-01~08 证据齐全 | 02/03/04/PM 签署、风险关闭/接受记录 | PM | `benchmark_ready=true` 或明确拒绝原因 | BLOCKED |
| GB-10 Base 运行授权 | GB-09 PASS | 单独授权单、run_id 规则、Snapshot 绑定 | PM/04 | 仅授权 Zero/Few-shot | BLOCKED |
| GB-11 Training Decision | Base/DEV 结果完成 | 基线报告、误差分析、数据/泄漏复核 | PM | 明确 GO/NO-GO | BLOCKED |
| GB-12 LoRA/QLoRA | GB-11=GO | 训练数据、代码、配置、实验登记、回归计划 | PM/03 | 单独训练授权 | BLOCKED |
| GB-13 Blind Benchmark | 新 Snapshot/ACL/evaluator PASS | run_id、提交校验、隔离评测、发布审批 | PM/04 | 单独 Blind 授权 | BLOCKED |

## 1.1 项目负责人批准的复核延期

```text
decision_type = PROJECT_OWNER_APPROVED_DEFERRAL
review_task_status = COMPLETE_WITH_DEFERRED_REVIEW
reviewed_count = 1
pending_count = 402
pending_state = PENDING_01_CODEX_REVIEW
parser_blocked_document_count = 6
expert_review_status = DEFERRED_UNTIL_EXPERT_TEAM_ONBOARDING
```

该例外允许环境准备、候选数据工程和 E2E Dry-Run 继续，但不改变 GB-01、GB-02 或 GB-09 的未通过状态。402 条候选继续保持 `label=null`、`training_eligible=false`、`expert_signoff=false`、`gold_eligible=false`。

## 2. 安全硬门槛

以下任一项失败，Gate-B 必须 `FAIL`，不得用其他项通过抵消：

- Blind Gold 明文、可逆副本或逐例真值出现在非 QA 工作区、日志、缓存、训练数据或模型输入；
- Runtime ACL 允许不应访问者读取 Gold，或拒绝/审计日志缺失；
- `DISPUTED`、`HOLD`、`REWORK_SOURCE`、`target=null` 记录进入 Train/Dev/Benchmark；
- Snapshot、Metric、Schema、Protocol、evaluator 的版本/hash 不一致；
- Teacher 输出没有 lineage，或被当作人工/Gold 权威；
- 任何团队以模型结果倒推并修改样本、标签、切片或 Gate；
- 在 Gate-B PASS 前运行模型、生成 Teacher 候选或启动训练。

## 3. 签署与记录格式

每个 Gate-B 证据包至少记录：

```text
task_id
gate_id
asset_version
content_sha256
owner
source_commit
run_or_probe_id（如适用）
observed_result
reviewer
review_time
status = PASS | FAIL | PENDING
```

Gate-B 结论必须明确区分：

```text
contract_ready
benchmark_ready
base_model_authorized
training_authorized
blind_benchmark_authorized
```

## 4. 当前矩阵摘要

```text
Gate-A Contract: PASS / FROZEN
Data Readiness: PENDING
Snapshot Readiness: PENDING
Runtime ACL: PENDING
Evaluator Readiness: PENDING
Model Environment: PENDING
Gate-B: PENDING
Codex Review Work Item: COMPLETE_WITH_DEFERRED_REVIEW
Expert Review: DEFERRED_UNTIL_EXPERT_TEAM_ONBOARDING
Reviewed / Pending: 1 / 402
Parser Blocked Documents: 6
Benchmark Ready: FALSE
Training Authorized: FALSE
Base Model: BLOCKED
Training: BLOCKED
Blind Benchmark: BLOCKED
```
