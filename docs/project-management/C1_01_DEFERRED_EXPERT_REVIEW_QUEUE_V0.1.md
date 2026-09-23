# C1-01 Deferred Expert Review Queue V0.1

**登记日期**：`2026-09-23`
**Owner**：项目负责人；专家团队入驻后转交指定专家 Owner
**关联决策**：`C1_01_AI_Review_Deferral_Decision_V0.1.md`
**队列状态**：`DEFERRED_UNTIL_EXPERT_TEAM_ONBOARDING`

## 1. 聚合台账

| 队列 | 数量 | 当前状态 | 标签/资格边界 | 后续动作 |
|---|---:|---|---|---|
| 已完成 Codex 暂代复核 | 1 | `AI_PROVISIONAL_REVIEWED` | 非人工、非专家、非 Gold；正式训练仍未授权 | 专家回归时纳入一致性复核 |
| 延期专家复核队列 | 402 | `PENDING_01_CODEX_REVIEW` | `label=null`、`training_eligible=false`、`expert_signoff=false`、`gold_eligible=false` | 专家入驻后逐条复核并新增版本 |
| 解析阻塞文档队列 | 6 | `PARSER_BLOCKED` | 不形成监督标签，不进入训练或 Benchmark | 先修复解析与来源证据，再进入业务复核 |

仓库仅保留聚合治理台账；候选明细继续留在本地隔离数据区，不在本记录中写入来源标识、文件名、项目编号、条款原文或个人信息。

## 2. 回归优先级

| 优先级 | 范围 | 处理要求 |
|---|---|---|
| P0 | 高风险、HOLD、两遍冲突、证据不完整 | 先独立复核；存在分歧时进入正式业务裁决，不得直接用于训练 |
| P1 | 分层抽样样本 | 按类别、信号强度、项目族和候选类型覆盖；抽样问题向同层级回溯 |
| P2 | 其余延期候选 | 完成 402 条全量回归，不以抽样通过替代逐条复核 |
| P3 | 解析阻塞文档 | 修复解析后重新提取、核验来源和证据，再按 P0/P1/P2 规则入队 |

## 3. 专家入驻后的验收要求

- 每条候选必须有独立、可追溯的专家结论及证据定位；
- 专家结论不得复用 Codex 状态字段冒充人工签署；
- 新标签写入新版本，保留原 `PENDING_01_CODEX_REVIEW` 或暂代复核历史；
- 分层抽样用于发现系统性风险，不替代 402 条全量回归；
- 解析阻塞项不得与普通候选混合统计为已复核；
- 完成后重新运行 Schema、跨字段、来源、重复、pair、leakage 和角色资格检查；
- 未经独立 Gate 签署，继续保持 `benchmark_ready=false`、`training_authorized=false`。

## 4. 版本与重开规则

```text
current_queue_version = V0.1
reopen_status = REOPENED_FOR_EXPERT_REVIEW
update_mode = APPEND_NEW_VERSION
silent_overwrite = FORBIDDEN
full_regression_required = true
```
