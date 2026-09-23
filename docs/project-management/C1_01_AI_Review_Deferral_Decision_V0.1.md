# C1-01 AI Review Deferral Decision V0.1

**任务**：`C1-01_LOCAL_ENTRY_PRECONDITION`
**决策日期**：`2026-09-23`
**Owner**：项目负责人
**决策类型**：`PROJECT_OWNER_APPROVED_DEFERRAL`
**工作项状态**：`COMPLETE_WITH_DEFERRED_REVIEW`
**Gate-B 结论**：`NOT_PASS`

## 1. 决策背景

候选数据工程已形成 403 条候选记录。项目负责人决定本阶段暂停剩余候选的 Codex 逐条业务复核，并将人工专家二审延期至专家团队入驻后执行。该决定关闭的是本阶段的复核工作项，不代表未复核样本已经完成业务审核，也不改变其标签、训练资格或 Gold 资格。

## 2. 决策范围与事实基线

| 项目 | 数量 / 状态 |
|---|---|
| 候选记录总数 | 403 |
| 已完成 Codex 暂代复核 | 1 |
| 未完成逐条复核 | 402 |
| 未复核记录状态 | `PENDING_01_CODEX_REVIEW` |
| 未复核记录标签 | `null` |
| 未复核记录训练资格 | `training_eligible=false` |
| 未复核记录专家签署 | `expert_signoff=false` |
| 未复核记录 Gold 资格 | `gold_eligible=false` |
| 旧版解析阻塞文档 | 6，保持 `PARSER_BLOCKED` |
| 专家二审 | `DEFERRED_UNTIL_EXPERT_TEAM_ONBOARDING` |

上述 402 条不得描述为 `REVIEW_PASS`、`HUMAN_REVIEWED`、`EXPERT_REVIEWED` 或 Gold。文档级扫描、候选发现和结构化组装也不得替代候选级逐条业务复核。

## 3. 已知风险

- 402 条候选尚无逐条业务标签，真实正负例分布、边界冲突和证据质量仍未知；
- 高风险、HOLD 或两遍结论冲突样本可能仍包含未关闭的业务争议；
- 在专家复核前进行训练会把候选信号误当监督标签，形成不可审计的数据污染；
- 6 个旧版文档仍受解析能力限制，不能通过推测或其他候选记录补标签；
- 后续若静默覆盖现有状态或标签，将破坏延期决策、复核责任和版本追溯链。

## 4. 临时允许动作

在不改变候选审核状态和授权边界的前提下，允许继续：

- 模型与运行环境准备；
- 候选数据工程、去重、分层、队列编排和质量统计；
- 使用无真实标签夹具或明确非正式候选执行 E2E Dry-Run；
- 完善 Schema、适配器、日志、ACL、审计和可复现性检查；
- 为专家回归准备只读队列、抽样方案和版本化输出位置。

## 5. 明确禁止动作

- 不得把 402 条未复核候选用于正式训练、正式 DEV、Benchmark Gold 或 Blind Gold；
- 不得为未复核候选补写推测标签，或将候选信号视为正式标签；
- 不得把本工作项关闭解释为数据质量 PASS、Gate-B PASS 或训练授权；
- 不得把 Codex 暂代复核写成人工或专家复核；
- 不得绕过 6 个 `PARSER_BLOCKED` 文档形成监督样本；
- 不得静默覆盖现有记录；任何新标签、裁决或修复必须新增版本并保留旧状态。

## 6. 专家回归触发条件与顺序

满足以下任一条件即重开复核工作项：

1. 专家团队完成入驻并确认 Owner、访问边界和复核协议；
2. 项目申请正式训练、正式 DEV、Benchmark Snapshot 或 Blind Benchmark；
3. 候选池、标签口径、Schema 或证据链发生影响审核结论的版本变化；
4. PM、数据 Owner 或 QA 发现高风险冲突、泄漏或状态漂移。

重开后的优先顺序：

1. 高风险、HOLD、两遍冲突和证据不完整候选；
2. 按类别、信号强度、项目族和疑似标签进行分层抽样；
3. 完成剩余候选全量回归，并对抽样发现的问题向同层级回溯；
4. 单列处理 6 个 `PARSER_BLOCKED` 文档，先修复解析和来源证据，再进入业务复核。

## 7. 回滚与重开规则

- 重开状态使用 `REOPENED_FOR_EXPERT_REVIEW`，不得把原延期记录删除或改写为已完成；
- 专家结论写入新版本，至少记录版本、Owner、时间、依据和前一版本引用；
- 新标签不得静默覆盖 `label=null` 或既有暂代标签；
- 只有全部必需复核、数据 QA、泄漏检查和独立 Gate 签署完成后，才能重新评估 `benchmark_ready` 或 `training_authorized`；
- 若延期决定被撤销，必须由项目负责人形成新的版本化决策记录，并同步更新计划、Checklist、验收矩阵和 Project Control。

## 8. 当前授权边界

```text
review_task_status = COMPLETE_WITH_DEFERRED_REVIEW
expert_review_status = DEFERRED_UNTIL_EXPERT_TEAM_ONBOARDING
reviewed_count = 1
pending_count = 402
parser_blocked_document_count = 6
benchmark_ready = false
training_authorized = false
gate_b_pass = false
```
