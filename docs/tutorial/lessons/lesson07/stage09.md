# 第七课 · 第 9 阶段
# Failure Recovery、Retry 与 Human-in-the-loop
## Agent 已经会路由、会调用工具、会循环，但真实系统一旦超时、权限失败、证据不足、执行结果不确定，怎样才能安全恢复？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，可靠 Agent 的目标不是“永不失败”，而是 Fails Explicitly + Recovers Safely + Escalates When Needed；Retry 只是 Recovery 的一种。**
2. **第二，失败必须先分类：Transient Failure 才适合 Retry，Validation Error 应修参数或 Replan，Authorization / Policy Failure 应停止或请求权限，Terminal Failure 应明确终止。**
3. **第三，有副作用的 Action 一旦超时，不能直接视为失败；Timeout ≠ DefinitelyFailed，必须先 Verify 执行状态，再决定是否用同一个 Idempotency Key 重试。**
4. **第四，Partial Failure、Rollback、Compensation 和 Circuit Breaker 都属于真实 Agent 必备的恢复机制；多步任务不能只有“成功 / 失败”两个状态。**
5. **第五，Human-in-the-loop 至少要区分 Clarification、Approval 和 Escalation；需要人工时 Agent 应进入正式暂停状态，而不是继续猜测或绕过控制。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Recovery` | 恢复：工具失败或中断后安全重试、降级和继续 |
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `Human-in-the-loop` | 人在回路：高风险或不确定任务引入人工复核 |
| `State` | 状态：保存任务进度、事实和待办 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Idempotency` | 幂等：重复执行不会产生不可控重复副作用 |

### C. 建议阅读层级

```text
一级：核心心智模型    # 中文：先建立判断框架
↓
二级：关键公式 / 流程 / Schema    # 中文：理解系统怎样工作
↓
三级：政府采购案例与反例    # 中文：把抽象边界落到业务
↓
四级：编号细节与工程扩展    # 中文：按需要查阅，不要求一次全部记忆
```
<!-- PEDAGOGY_CN_ENHANCEMENT_V2 END -->

到第 8 阶段，我们已经得到：

\[
\boxed{
SourceOfTruth
\rightarrow
Route
\rightarrow
RAG / Database / File / Compute / Action
}
\]

这解决了：

> **Agent 应该走哪条路径。**

但真实系统不会永远成功。

你一定会遇到：

```text
网络超时
接口限流
数据库暂时不可用
权限不足
参数合法但业务状态已变化
只完成一半
写操作是否成功不确定
多个并行分支部分失败
证据不足
需要人工确认
```

所以一个真正可靠的 Agent，绝不能把目标定义成：

> **“永远不失败。”**

更准确地说：

\[
\boxed{
ReliableAgent
\neq
NeverFails
}
\]

而应该是：

\[
\boxed{
ReliableAgent
=
FailsExplicitly
+
RecoversSafely
+
EscalatesWhenNeeded
}
\]

本阶段最终形成：

# `ProcurementAgentRecoveryPolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

错误发生以后，Agent 第一件事不是：

> **“重试。”**

而是：

\[
\boxed{
ClassifyFailure
\rightarrow
ChooseRecovery
}
\]

也就是说：

```text
这是什么错误？
↓
它会不会自己恢复？
↓
原动作能不能安全重试？
↓
是否应该换策略？
↓
是否应该停止？
↓
是否必须交给人？
```

所以：

\[
\boxed{
Retry
只是Recovery的一种
}
\]

不是 Recovery 的全部。

---

# 二、先把 Failure 分成几类

第一版至少应该区分：

```text
Transient Failure
临时故障

Validation Failure
输入 / Schema / 业务校验失败

Authorization Failure
权限失败

Policy Failure
策略禁止

Not Found / Empty Result
没有找到数据

Conflict Failure
状态冲突 / 版本冲突

Partial Failure
部分步骤成功、部分失败

Uncertain Execution
不知道动作到底成功没有

Terminal Failure
当前条件下无法继续
```

不同错误：

> Recovery 策略完全不同。

---

# 三、Transient Failure：这类错误才真正适合 Retry

典型例子：

```text
HTTP 503
短暂网络错误
Rate Limit
连接重置
临时锁
服务过载
```

这种情况下：

> Action 本身可能没错。

只是：

> 执行环境暂时失败。

所以可以：

# Retry
## 重试

但必须带：

```text
max_attempts
backoff
jitter
timeout
retryable_error_types
```

核心原则：

\[
\boxed{
OnlyRetryRetryableErrors
}
\]

---

# 四、Backoff：为什么不能失败以后立刻疯狂重试？

假设服务已经过载。

如果 100 个 Agent 同时：

```text
失败
↓
立即重试
↓
再次失败
↓
立即重试
```

只会把服务压得更死。

所以 Retry 通常需要：

# Backoff
## 退避

例如概念上：

\[
Delay_n
=
BaseDelay
\times
2^n
\]

再加入随机扰动：

# Jitter
## 抖动

避免所有请求在同一时刻重新涌入。

重点不是公式本身。

而是：

\[
\boxed{
Retry
必须受节奏控制
}
\]

---

# 五、Validation Failure：参数错了，重试原动作没有意义

假设 Tool 返回：

```text
400 invalid project_id
```

如果 Agent 原样 Retry：

```text
project_id = "P-???"
```

再试 5 次，

不会变好。

这种情况应该：

```text
修正参数
重新获取字段
请求用户补充
或
Replan
```

所以：

\[
\boxed{
InvalidInput
\neq
RetryableFailure
}
\]

---

# 六、Authorization / Policy Failure：不能靠重试绕过权限

如果 Runtime 返回：

```text
permission_denied
```

或者：

```text
approval_required
```

正确做法不是：

> 换个参数继续撞。

而应该进入：

```text
request_approval
request_permission
switch_to_read_only_path
or
stop
```

所以：

\[
\boxed{
AuthorizationFailure
不能通过Retry解决
}
\]

更不能：

> 换一个名字相似的 Tool 绕过 Policy。

---

# 七、Retry 和 Replan 再次精确区分

第 5 阶段我们已经讲过：

\[
Retry
=
SameActionAgain
\]

\[
Replan
=
DifferentDecision
\]

这一阶段再加一层：

> **什么时候该 Retry，什么时候该 Replan？**

可以按错误来源判断：

```text
执行环境暂时失败
→ Retry

参数 / 路由 / Tool 选择错误
→ Replan

权限 / Policy 阻止
→ Escalate / Stop

证据长期不足
→ Clarify / Human Review

动作结果不确定
→ Verify Before Retry
```

所以 Recovery 不是“一条重试规则”。

而是一张：

> **错误类型 → 恢复动作**

的映射表。

---

# 八、最危险的一类错误：Uncertain Execution

假设 Agent 调用：

```text
publish_notice
```

请求超时。

现在你不知道：

```text
情况A：
服务根本没收到

情况B：
服务已经执行成功
只是响应丢了
```

如果直接 Retry：

> 可能重复发布。

所以：

\[
\boxed{
Timeout
\neq
DefinitelyFailed
}
\]

对有副作用的 Tool，

超时后第一步应该是：

# Verify
## 验证执行状态

例如：

```text
query_action_status
check_idempotency_key
read_current_external_state
```

只有确认未执行：

> 才考虑 Retry。

---

# 九、Idempotency：Recovery 能不能安全，关键看重复执行会发生什么

如果同一个动作重复两次：

```text
create_draft_report
create_draft_report
```

结果只是返回同一份报告，

这叫：

> 接近幂等。

如果重复两次：

```text
publish_notice
publish_notice
```

产生两条正式公告，

那就非常危险。

所以写操作应尽量携带：

```text
idempotency_key
operation_id
request_id
```

让 Runtime 能判断：

> 这是不是同一个业务动作的重复提交。

因此：

\[
\boxed{
SafeRetry
依赖
Idempotency
}
\]

---

# 十、Partial Failure：多步任务失败不一定意味着“全部失败”

假设一个采购文件审查任务有四个并行分支：

```text
资格条件审查
评分标准审查
技术参数审查
合同条款审查
```

结果：

```text
资格 = success
评分 = success
技术 = failed
合同 = success
```

这不是：

> 全部成功。

也不是：

> 全部失败。

而是：

# Partial Success
## 部分成功

所以 State 应明确：

```json
{
  "status": "partial_success",
  "completed": [
    "qualification",
    "scoring",
    "contract"
  ],
  "failed": [
    "technical"
  ]
}
```

然后决定：

```text
只重试失败分支
降低结果范围
标记needs_review
或
请求人工补充
```

---

# 十一、Rollback 和 Compensation 不是一回事

如果事务还没真正提交，

有时可以：

# Rollback
## 回滚

即：

> 恢复到之前状态。

但在分布式业务系统里，

很多动作已经发生：

```text
邮件已发
文件已生成
外部系统已接收
审批已提交
```

这时往往不能真正“回滚时间”。

只能做：

# Compensation
## 补偿动作

例如：

```text
错误创建草稿
→ 删除草稿

错误提交审批
→ 发起撤回

错误写入临时记录
→ 写入纠正记录
```

所以：

\[
\boxed{
Rollback
=
UndoBeforeCommit
}
\]

而：

\[
\boxed{
Compensation
=
BusinessLevelCorrectiveAction
}
\]

---

# 十二、Circuit Breaker：外部服务坏了，不要让所有 Agent 一直撞

假设：

```text
regulation.search
```

连续 50 次失败。

继续让 Agent 调：

> 没意义。

这时可以触发：

# Circuit Breaker
## 熔断器

状态可以简化为：

```text
CLOSED
正常调用

OPEN
暂时禁止调用

HALF_OPEN
少量探测恢复
```

所以：

\[
\boxed{
RepeatedInfrastructureFailure
应该进入系统级保护
}
\]

而不是让每个 Agent 自己傻重试。

---

# 十三、Human-in-the-loop 不只有“审批”

人类介入至少可以分三种：

## 1. Clarification
### 澄清

缺少必要信息：

```text
项目辖区不明
文件版本不明
用户意图不清
```

这时需要：

> 用户补充事实。

---

## 2. Approval
### 审批

动作本身清楚，

但属于高风险：

```text
发布公告
发送正式函件
修改正式数据
提交审批
```

这时需要：

> 人类授权执行。

---

## 3. Escalation
### 升级人工处理

Agent 已经尽力，但：

```text
证据冲突
规则解释不确定
异常状态无法恢复
高风险结论缺乏足够依据
```

这时需要：

> 专业人员接管判断。

所以：

\[
\boxed{
Clarification
\neq
Approval
\neq
Escalation
}
\]

---

# 十四、Human-in-the-loop 以后，Agent 应该进入正式暂停状态

如果需要人工，

Agent 不应该继续猜。

State 应进入：

```text
waiting_for_user

waiting_for_approval

waiting_for_expert
```

并保存：

```text
为什么暂停？
需要谁处理？
需要什么输入？
当前任务做到哪里？
恢复后下一步是什么？
```

人类回复以后：

\[
HumanResponse
=
NewObservation
\]

再恢复 Loop。

---

# 十五、Recovery State Machine：恢复过程也应该是状态机

可以定义：

```text
RUNNING
↓
FAILED_RECOVERABLE
↓
RETRYING
↓
RUNNING
```

或者：

```text
RUNNING
↓
FAILED_RECOVERABLE
↓
REPLANNING
↓
RUNNING
```

还可能：

```text
RUNNING
↓
WAITING_FOR_APPROVAL
↓
APPROVED
↓
RUNNING
```

以及：

```text
RUNNING
↓
FAILED_TERMINAL
↓
STOPPED
```

所以：

\[
\boxed{
Recovery
本身也需要显式State
}
\]

---

# 十六、Structured Error：错误结果也必须结构化

Tool 不应该只返回：

```text
“出错了”
```

更可靠的是：

```json
{
  "status": "error",
  "error_type": "rate_limited",
  "retryable": true,
  "retry_after_ms": 2000,
  "operation_id": "OP_018",
  "side_effect_state": "not_started",
  "message": "服务限流"
}
```

或者：

```json
{
  "status": "error",
  "error_type": "permission_denied",
  "retryable": false,
  "required_action": "request_approval"
}
```

因此：

\[
\boxed{
RecoveryQuality
依赖
ErrorContractQuality
}
\]

---

# 十七、Recovery Budget：恢复也不能无限花时间和成本

Agent 可能一直：

```text
Retry
Replan
Fallback
Search Again
Ask Another Tool
```

如果没有预算，

Recovery 本身也会失控。

所以应该有：

```text
max_retry_count
max_replan_count
max_recovery_steps
recovery_time_budget
recovery_cost_budget
```

超过以后进入：

```text
partial_success
needs_review
failed_terminal
```

所以：

\[
\boxed{
Recovery
也需要Budget
}
\]

---

# 十八、Fallback：降级可以，但不能装作没降级

例如主 Source：

```text
project_database
```

不可用。

Fallback：

```text
latest_project_document
```

系统可以继续，

但必须记录：

```text
fallback_used = true
confidence_degraded = true
source_freshness_lower = true
```

否则用户看到的答案表面一样，

实际上：

> 可信度已经下降。

所以：

\[
\boxed{
GracefulDegradation
必须Transparent
}
\]

---

# 十九、政府采购案例：发布更正公告时发生超时

假设流程：

```text
生成更正公告草稿
↓
人工审批通过
↓
调用 publish_notice
```

Runtime 返回：

```text
timeout
```

错误做法：

```text
立即再次 publish_notice
```

正确 Recovery：

```text
Step 1
根据 operation_id 查询发布状态

Step 2
如果已发布
→ 标记 success

Step 3
如果明确未发布
→ 使用相同 idempotency_key 重试

Step 4
如果状态无法确认
→ waiting_for_expert / manual_check
```

因为：

\[
\boxed{
UncertainWrite
必须VerifyBeforeRetry
}
\]

---

# 二十、另一个案例：法规检索连续为空

任务：

> “判断本地机构资格限制是否有依据。”

第一次 RAG：

```text
0 results
```

这不代表：

> “没有规则。”

可能是：

```text
Query写错
Metadata Filter太严格
辖区识别错误
知识库缺失
```

所以 Recovery 可以是：

```text
Replan Query
↓
放宽Filter
↓
Hybrid Retrieval
↓
仍为空
↓
标记EvidenceInsufficient
↓
Human Review
```

这里：

> 不能把 Empty Retrieval 直接解释成“没有法律依据”。

这就是：

\[
\boxed{
Recovery
也必须尊重ErrorTaxonomy
}
\]

---

# 二十一、本阶段错误分类：Recovery 自己也会出错

至少要区分：

```text
1. Retry Storm
无限重试

2. Wrong Retry
不可重试错误被反复重试

3. Missing Retry
临时错误直接终止

4. Retry Without Idempotency
写操作重复产生副作用

5. Wrong Replan
本应重试却换策略

6. Hidden Partial Failure
部分失败被当成全部成功

7. Failed Compensation
补偿动作失败

8. Approval Bypass
需要人工却自动执行

9. Escalation Too Late
高风险异常拖太久才交给人

10. Recovery State Loss
恢复过程中状态丢失
```

所以：

> Recovery Policy 本身也必须被评测。

---

# 二十二、怎样评测 Failure Recovery？

第一版至少可以记录：

```text
retry_success_rate

retry_precision
真正可重试的错误中有多少被正确重试

retry_false_positive_rate
不可重试错误被错误重试比例

replan_success_rate

uncertain_execution_verification_rate

duplicate_side_effect_rate

partial_failure_detection_rate

compensation_success_rate

circuit_breaker_trigger_accuracy

human_escalation_precision

human_escalation_recall

approval_bypass_rate

recovery_completion_rate

mean_recovery_steps

recovery_cost

terminal_failure_accuracy
```

最终仍然要看：

\[
\boxed{
TaskRecoveredSafely
}
\]

而不是：

> “系统总算跑完了。”

---

# 二十三、本阶段工程产物：`ProcurementAgentRecoveryPolicy_V0.1`

第一版至少锁定：

```text
recovery_policy_version

error_schema

error_type_enum

retryable_error_types

terminal_error_types

max_retry_count

backoff_policy

jitter_policy

timeout_policy

verify_before_retry_for_side_effect_tools
=
true

idempotency_policy

partial_failure_policy

rollback_policy

compensation_policy

circuit_breaker_policy

fallback_policy

confidence_degradation_policy

clarification_policy

approval_policy

human_escalation_policy

recovery_state_schema

recovery_step_budget

recovery_time_budget

recovery_cost_budget

trace_logging
=
enabled
```

每次恢复至少记录：

```text
failure_id

step_id

tool_call_id

operation_id

error_type

retryable

side_effect_state

recovery_decision

retry_count

replan_reason

fallback_used

human_intervention_type

state_before_recovery

state_after_recovery

final_recovery_status
```

这样才真正做到：

> **失败可见、恢复可控、过程可审计。**

---

# 二十四、把本阶段压成最精准的 6 句话

> **第一，可靠 Agent 的目标不是“永不失败”，而是 `Fails Explicitly + Recovers Safely + Escalates When Needed`；Retry 只是 Recovery 的一种。**

> **第二，失败必须先分类：Transient Failure 才适合 Retry，Validation Error 应修参数或 Replan，Authorization / Policy Failure 应停止或请求权限，Terminal Failure 应明确终止。**

> **第三，有副作用的 Action 一旦超时，不能直接视为失败；`Timeout ≠ DefinitelyFailed`，必须先 Verify 执行状态，再决定是否用同一个 Idempotency Key 重试。**

> **第四，Partial Failure、Rollback、Compensation 和 Circuit Breaker 都属于真实 Agent 必备的恢复机制；多步任务不能只有“成功 / 失败”两个状态。**

> **第五，Human-in-the-loop 至少要区分 Clarification、Approval 和 Escalation；需要人工时 Agent 应进入正式暂停状态，而不是继续猜测或绕过控制。**

> **第六，Recovery 也必须有 Budget、State、Trace 和独立评测；真正的指标不是“最后跑完”，而是任务是否在没有重复副作用、没有越权、没有隐藏降级的前提下安全恢复。**

---

# 本阶段最核心的一张图

```text
                         Failure
                            │
                            ▼
                      Classify Error
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
      Transient         Strategy Error    Permission/Policy
          │                 │                 │
          ▼                 ▼                 ▼
        Retry             Replan          Human / Stop
          │                 │                 │
          └────────────┬────┴────┬────────────┘
                       │         │
                       ▼         ▼
                 Side Effect?   Terminal?
                       │         │
                 ┌─────┴─────┐   │
                 ▼           ▼   ▼
                No          Yes Stop
                 │           │
                 │        Verify State
                 │           │
                 └─────┬─────┘
                       ▼
                 Recovery Action
                       │
                       ▼
                   Update State
                       │
                       ▼
              Continue / Escalate / Stop
```

脑中最后只留一句：

> **真正可靠的 Agent，不是碰到错误就重试，而是先判断错误属于哪一类，再选择 Retry、Replan、Verify、Fallback、Compensation、Human Escalation 或 Stop，并保证整个恢复过程没有重复副作用、没有越权、没有把失败伪装成成功。**

---

# 第七课 · 第 9 阶段掌握测试

现在不回看正文，你应该能够解释：为什么 Retry 只是 Recovery 的一种；Transient、Validation、Authorization、Partial、Uncertain Execution、Terminal Failure 有什么区别；Backoff 和 Jitter 为什么必要；为什么 Invalid Input 不该原样 Retry；Authorization Failure 为什么不能靠重试绕过；Retry 和 Replan 如何进一步区分；为什么 Timeout 不等于 Definitely Failed；Idempotency 为什么决定写操作能否安全重试；Partial Success 应怎样进入 State；Rollback 和 Compensation 有什么本质区别；Circuit Breaker 解决什么系统级问题；Clarification、Approval、Escalation 三种 Human-in-the-loop 有什么区别；为什么 Recovery 需要显式状态机；Structured Error 为什么影响恢复质量；为什么 Recovery 也需要 Budget；Fallback 时为什么必须暴露可信度下降；以及为什么最终目标是 `TaskRecoveredSafely` 而不是“总算跑完”。

如果这些能够完整讲出来：

\[
\boxed{
第七课第9阶段真正掌握
}
\]

---

# 下一阶段：第七课 · 第 10 阶段
# Agent Safety：权限、Prompt Injection、Approval 与 Audit Trail
## Agent 已经会调用工具、会恢复失败，但当外部内容试图操纵模型、权限配置错误、写操作越权时，怎样保证“能做事”不会变成“乱做事”？

到第 9 阶段，我们已经拥有：

```text
Failure Classification
Retry
Replan
Idempotency
Partial Failure
Compensation
Circuit Breaker
Human Escalation
Recovery State
```

下一阶段要正式进入：

# Agent Safety
## 智能体安全边界

我们会重点拆开：

```text
Prompt Injection
Indirect Prompt Injection
Tool Result Injection
Least Privilege
Capability Isolation
Read / Write Separation
Approval Gate
Data Boundary
Secret Handling
Audit Trail
Action Confirmation
Policy Enforcement
```

并建立：

# `ProcurementAgentSafetyPolicy_V0.1`

下一阶段最重要的一条边界会是：

\[
\boxed{
UntrustedContent
\neq
TrustedInstruction
}
\]

以及：

\[
\boxed{
ModelDecision
\neq
Authorization
}
\]

也就是让 Agent 从：

> **“能恢复失败”**

继续推进到：

> **“即使面对恶意内容和高风险工具，也只能在明确权限、审批与审计边界内行动”。**



---
