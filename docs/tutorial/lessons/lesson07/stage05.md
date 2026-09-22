# 第七课 · 第 5 阶段
# Agent Loop：Plan → Act → Observe → Continue / Stop
## Tool Calling 已经会了，为什么还不等于一个真正会完成多步任务的 Agent？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，Tool Calling 解决“这一刻调用什么”，Agent Loop 解决“怎样持续执行直到整个任务完成”；Action Success ≠ Task Success。**
2. **第二，可靠 Agent Loop 的最小结构是 State → Plan → Act → Observe → Update State → Continue / Stop，而 Plan 应该依赖当前真实 State，不应假装一开始就知道未来全部步骤。**
3. **第三，Stop Condition 和 Completion Check 必须分开：停止可以因为完成、预算耗尽、不可恢复错误或等待人工，而只有 Completion Requirements 全部满足才叫任务完成。**
4. **第四，Retry 适合“动作正确但执行暂时失败”，Replan 适合“原策略本身需要改变”；两者混用会导致死循环或无效重试。**
5. **第五，Agent 必须检测 Repeated Action 和 No-progress，并为 Write Tool 考虑 Idempotency、Checkpoint 和 Resume，否则重试可能造成重复副作用或任务重跑。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Tool Calling` | 工具调用：模型按受控协议选择工具并构造参数 |
| `Observe` | Observe/观察：读取当前状态和工具结果 |
| `Tool Registry` | 工具注册表：管理工具能力、权限和版本 |
| `State` | 状态：保存任务进度、事实和待办 |

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

到第 4 阶段，我们已经具备：

```text
Tool Registry
Tool Discovery
Structured Arguments
Runtime Validation
Authorization
Approval Boundary
```

也就是说，模型现在已经能够：

> **在受控权限下，选择一个 Tool，并生成可执行参数。**

但这仍然可能只是一次：

```text
User
↓
Model
↓
Tool Call
↓
Tool Result
↓
Answer
```

真正的 Agent 必须解决另一个问题：

> **如果任务需要 5 步、10 步，甚至某一步失败以后要重新规划，系统怎样持续运行，直到任务真正完成？**

这就是：

# Agent Loop
## 智能体循环

本阶段最终形成：

# `ProcurementAgentLoopPolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

一个 Agent Loop 的本质不是：

> **“让模型连续说很多次。”**

而是：

\[
\boxed{
State_t
\rightarrow
Plan_t
\rightarrow
Action_t
\rightarrow
Observation_{t+1}
\rightarrow
State_{t+1}
}
\]

然后系统判断：

\[
\boxed{
Continue
\quad or \quad
Stop
}
\]

所以真正的循环是：

```text
读取当前状态
↓
决定下一步
↓
执行真实动作
↓
读取真实结果
↓
更新状态
↓
检查是否完成
↓
继续 / 停止
```

---

# 二、为什么“会 Tool Calling”还不够？

Tool Calling 只解决：

> **这一刻该调用什么工具。**

Agent Loop 还必须解决：

```text
前面已经做了什么？
当前缺什么？
下一步为什么这样做？
工具失败后怎么办？
重复调用怎么办？
是否已经完成？
何时停止？
```

所以：

\[
\boxed{
ToolCalling
=
LocalAction
}
\]

而：

\[
\boxed{
AgentLoop
=
TaskLevelControlFlow
}
\]

---

# 三、Plan：计划不是一次写死，而是当前状态下的下一步意图

很多人把 Agent Planning 理解成：

> 一开始先生成 20 步完整计划。

这不一定可靠。

因为后面的步骤可能依赖：

> 前面工具真实返回什么。

所以第一版更稳的方式通常是：

# Short-horizon Planning
## 短视野规划

例如当前状态：

```text
目标：
审查资格条件

已完成：
读取采购文件

当前观察：
发现3条资格条件

下一步：
逐条检索适用规则
```

这里只规划：

> **下一步或少量后续步骤。**

而不是假装已经知道整个任务未来会发生什么。

所以：

\[
\boxed{
Plan_t
依赖
State_t
}
\]

---

# 四、Act：Action 必须是“系统可以真实执行的动作”

一个合法 Action 应该来自：

```text
Visible Tools
∩
Authorized Tools
```

例如：

```json
{
  "action": "regulation.search",
  "arguments": {
    "query": "投标前本地机构限制"
  }
}
```

而不是：

```text
“去查一下相关政策”
```

因为后者只是：

> 自然语言意图，

不能直接进入 Runtime。

所以：

\[
\boxed{
Action
=
ExecutableDecision
}
\]

---

# 五、Observe：Agent 必须读取“真实结果”，不是自己猜

Action 执行以后，

Agent 得到新的 Observation：

```text
success
error
empty_result
permission_denied
timeout
partial_result
```

或者具体内容：

```text
找到3份规则
其中1份已失效
1份为当前有效
1份辖区不匹配
```

这个 Observation 必须来自：

> Tool Runtime / Environment。

不是模型自己编。

因此：

\[
\boxed{
Observation
=
ExternalRealityReturnedToAgent
}
\]

---

# 六、Update State：工具结果不应该只塞进聊天历史

假设 Agent 已经完成：

```text
文件读取
资格条件抽取
条件1检索
条件2检索
```

如果系统只靠 Conversation History 记住这些，

会越来越混乱。

更稳的是维护：

# Task State
## 任务状态

例如：

```json
{
  "task_id": "T_001",
  "goal": "审查采购文件资格条件",
  "completed_steps": [
    "read_file",
    "extract_requirements",
    "review_requirement_1",
    "review_requirement_2"
  ],
  "pending_steps": [
    "review_requirement_3",
    "create_report"
  ],
  "artifacts": {
    "requirements": ["R1", "R2", "R3"],
    "evidence_ids": ["E1", "E2"]
  },
  "needs_review": false
}
```

因此：

\[
\boxed{
ConversationHistory
\neq
TaskState
}
\]

---

# 七、Continue：为什么不能每次 Tool Result 后立刻结束？

假设用户要求：

> “审查整份采购文件并生成报告。”

Agent 第一次调用：

```text
read_file
```

结果成功。

如果此时直接输出：

> “文件已经读取完成。”

那只是：

> **局部动作成功。**

不是：

> **用户任务完成。**

所以每轮都要判断：

\[
\boxed{
ActionSuccess
\neq
TaskSuccess
}
\]

系统必须继续检查：

> Goal 是否真的已经满足。

---

# 八、Stop Condition：Agent 为什么必须有明确停止条件？

没有 Stop Condition，

Agent 很容易：

```text
继续搜索
继续确认
继续调用
继续重试
继续规划
```

最后进入死循环。

第一版至少应该有：

```text
goal_completed

max_steps_reached

time_budget_exceeded

cost_budget_exceeded

no_progress

repeated_action

unrecoverable_error

human_approval_required
```

所以：

\[
\boxed{
Stop
不是模型“觉得差不多了”
}
\]

而应该是：

> **Runtime 可检查的结束条件。**

---

# 九、Completion Check：停止之前必须验证“任务真的完成了”

假设任务要求：

```text
审查3类风险
+
输出证据
+
生成报告
```

但 Agent 只完成：

```text
审查3类风险
```

然后说：

> “任务完成。”

这是：

# Premature Completion
## 过早完成

所以可以定义：

```text
completion_requirements:
- qualification_review_done
- evidence_attached
- report_generated
```

只有全部满足：

\[
\boxed{
CompletionCheck=True
}
\]

才允许结束。

---

# 十、Step Budget：为什么 Agent 必须限制最大步数？

假设没有：

```text
max_steps
```

Agent 可能因为：

```text
搜索结果不满意
工具反复超时
模型不断重新规划
```

跑上几百轮。

所以需要：

# Step Budget
## 步数预算

例如：

```text
max_steps = 20
```

它不是为了：

> 粗暴截断任务。

而是：

> **防止失控，并强迫系统在达到上限时进入可解释状态。**

例如：

```text
status = incomplete
reason = max_steps_reached
```

---

# 十一、No-progress Detection：最危险的不是失败，而是“看起来一直在做事”

Agent 可能出现：

```text
Step 7
搜索A

Step 8
还是搜索A

Step 9
换个措辞搜索A

Step 10
继续搜索A
```

表面上：

> 一直在行动。

实际上：

> 没有新增信息。

这叫：

# No-progress Loop
## 无进展循环

可以定义：

```text
最近N步
没有新增Evidence
没有新增Artifact
没有State变化
```

则触发：

```text
replan
or
stop
```

所以：

\[
\boxed{
Activity
\neq
Progress
}
\]

---

# 十二、Repeated Action Detection：重复调用要被识别

如果 Agent 连续生成相同：

```text
tool_name
+
arguments
```

例如：

```json
{
  "tool": "regulation.search",
  "arguments": {
    "query": "本地机构限制"
  }
}
```

重复 5 次，

系统应该识别：

# Repeated Action

而不是傻傻继续执行。

可以记录：

```text
action_hash
```

如果：

```text
same_action_count > threshold
```

就触发：

```text
replan
fallback
stop
```

---

# 十三、Replanning：计划失败以后，不是所有情况都应该重试原动作

假设：

```text
regulation.search
```

返回：

```text
0 results
```

Agent 有几种选择：

```text
换Query
换Tool
扩大检索范围
删除错误Filter
请求用户补充信息
停止并标记证据不足
```

这就是：

# Replanning
## 重新规划

它的本质是：

\[
\boxed{
NewPlan
=
f(
CurrentState,
FailedAction,
Observation
)
}
\]

而不是：

> “同一个动作再试一次看看。”

---

# 十四、Retry 和 Replan 不是一回事

## Retry
### 重试

适合：

```text
网络超时
临时限流
偶发服务错误
```

因为：

> Action 本身没错，

只是执行暂时失败。

---

## Replan
### 重新规划

适合：

```text
查询策略错误
工具选择错误
过滤条件太严格
当前路线无法完成任务
```

因为：

> 不是执行偶发失败，

而是原策略本身需要改变。

所以：

\[
\boxed{
Retry
=
SameActionAgain
}
\]

\[
\boxed{
Replan
=
DifferentDecision
}
\]

---

# 十五、Failure State：失败也必须是正式状态

Agent 不应该只有：

```text
running
completed
```

还应该有：

```text
waiting_for_user
waiting_for_approval
blocked
partial_success
failed_recoverable
failed_terminal
```

例如：

```json
{
  "status": "waiting_for_user",
  "reason": "jurisdiction_missing",
  "required_input": [
    "项目所在地区"
  ]
}
```

这比模型硬猜一个地区：

> 可靠得多。

---

# 十六、Human Approval 进入 Loop 以后发生什么？

如果 Agent 要执行：

```text
publish_notice
```

系统检查：

```text
approval_required = true
```

Agent Loop 不应该：

> 继续往下执行。

而应该进入：

```text
waiting_for_approval
```

流程：

```text
Agent proposes action
↓
Loop pauses
↓
Human approves / rejects
↓
New Observation
↓
Agent resumes
```

所以：

\[
\boxed{
HumanResponse
也是Observation
}
\]

---

# 十七、Idempotency：为什么重复执行 Write Tool 很危险？

假设 Agent 调用：

```text
create_report
```

Runtime 超时，

Agent 不知道：

> 报告到底创建成功没有。

如果直接 Retry，

可能生成：

```text
Report_001
Report_002
Report_003
```

这就需要：

# Idempotency
## 幂等性

例如给动作一个：

```text
idempotency_key
```

使同一个业务动作重复提交时：

> 不产生重复副作用。

所以：

\[
\boxed{
RetrySafe
\neq
AlwaysRetry
}
\]

尤其 Write / External Action Tool 必须考虑幂等性。

---

# 十八、Checkpoint：长任务为什么要保存中间状态？

假设一个任务跑了：

```text
18步
```

第 19 步系统崩了。

如果没有 Checkpoint：

> 可能全部重来。

所以应该定期保存：

# Checkpoint
## 检查点

至少包括：

```text
task_state
completed_actions
artifacts
tool_results
pending_actions
approval_state
```

这样恢复时：

\[
\boxed{
ResumeFromCheckpoint
}
\]

而不是：

\[
\boxed{
RestartFromZero
}
\]

---

# 十九、Agent Loop 不是无限“自主”，而是受控状态机

到这里可以看清：

Agent Loop 本质上非常像：

# State Machine
## 状态机

例如：

```text
RUNNING
↓
WAITING_FOR_TOOL
↓
RUNNING
↓
WAITING_FOR_APPROVAL
↓
RUNNING
↓
COMPLETED
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

所以真正可靠的 Agent：

> 不是“让模型自由发挥”。

而是：

\[
\boxed{
LLMDecision
在
ExplicitStateMachine
里运行
}
\]

---

# 二十、政府采购案例：完整审查 Loop

用户目标：

> “审查采购文件中的资格条件，并生成带依据的风险报告。”

初始状态：

```json
{
  "status": "running",
  "goal": "qualification_review",
  "step": 0,
  "completed": [],
  "pending": [
    "read_file",
    "extract_requirements",
    "review_requirements",
    "create_report"
  ]
}
```

Step 1：

```text
Plan:
读取采购文件

Act:
procurement.read_file
```

Observation：

```text
读取成功
```

Update State：

```text
read_file = completed
```

Step 2：

```text
Plan:
抽取资格条件

Act:
procurement.extract_requirements
```

Observation：

```text
R1 本地机构
R2 注册满3年
R3 认证要求
```

Step 3～5：

```text
分别检索R1 / R2 / R3
```

其中 R3 返回：

```text
evidence insufficient
```

Agent 更新：

```text
R1 = reviewed
R2 = reviewed
R3 = needs_review
```

最后：

```text
create_report
```

Completion Check：

```text
qualification_review_done = true
evidence_attached = true
report_generated = true
```

因此：

\[
Stop=True
\]

这才叫：

> **任务级完成。**

---

# 二十一、本阶段错误分类：Agent Loop 会怎样坏掉？

至少要区分：

```text
1. Premature Stop
任务没完成就结束

2. Endless Loop
无限循环

3. Repeated Action
重复同一动作

4. No-progress Loop
一直执行但没有新进展

5. Wrong Retry
本应Replan却一直Retry

6. Wrong Replan
临时失败却频繁换策略

7. State Drift
状态记录与真实执行不一致

8. Lost Observation
Tool Result没有进入State

9. Duplicate Side Effect
重试造成重复写入

10. Completion False Positive
Completion Check错误通过
```

所以：

> Agent Loop 的稳定性

必须单独评测。

---

# 二十二、怎样评测 Agent Loop？

第一版至少记录：

```text
task_completion_rate

average_steps

p95_steps

premature_stop_rate

max_step_termination_rate

repeated_action_rate

no_progress_rate

retry_success_rate

replan_success_rate

state_consistency_rate

duplicate_side_effect_rate

checkpoint_resume_success_rate

human_approval_resume_rate
```

同时必须测：

# Task Success

而不只是：

# Tool Success

因为：

\[
\boxed{
所有Tool都成功
也可能任务失败
}
\]

---

# 二十三、本阶段工程产物：`ProcurementAgentLoopPolicy_V0.1`

第一版至少锁定：

```text
loop_policy_version

initial_state_schema

agent_status_enum

plan_horizon
=
short

max_steps

time_budget

cost_budget

progress_definition

no_progress_window

repeated_action_threshold

retry_policy

replan_policy

retryable_errors

terminal_errors

completion_requirements

stop_conditions

human_approval_pause_policy

checkpoint_interval

resume_policy

idempotency_required_for_write_tools
=
true

trace_logging
=
enabled
```

每一步至少记录：

```text
step_id

state_before

plan

selected_action

arguments

tool_result

observation

state_after

progress_delta

retry_count

replan_reason

stop_check

completion_check
```

这样 Agent 才真正可以：

> 重放、调试、恢复、评测。

---

# 二十四、把本阶段压成最精准的 6 句话

> **第一，Tool Calling 解决“这一刻调用什么”，Agent Loop 解决“怎样持续执行直到整个任务完成”；`Action Success ≠ Task Success`。**

> **第二，可靠 Agent Loop 的最小结构是 `State → Plan → Act → Observe → Update State → Continue / Stop`，而 Plan 应该依赖当前真实 State，不应假装一开始就知道未来全部步骤。**

> **第三，Stop Condition 和 Completion Check 必须分开：停止可以因为完成、预算耗尽、不可恢复错误或等待人工，而只有 Completion Requirements 全部满足才叫任务完成。**

> **第四，Retry 适合“动作正确但执行暂时失败”，Replan 适合“原策略本身需要改变”；两者混用会导致死循环或无效重试。**

> **第五，Agent 必须检测 Repeated Action 和 No-progress，并为 Write Tool 考虑 Idempotency、Checkpoint 和 Resume，否则重试可能造成重复副作用或任务重跑。**

> **第六，真正可靠的 Agent Loop 本质上是“LLM 决策运行在显式状态机中”，而不是让模型无限自由地继续思考和调用工具。**

---

# 本阶段最核心的一张图

```text
                         User Goal
                            │
                            ▼
                       Initial State
                            │
                            ▼
                           Plan
                            │
                            ▼
                           Act
                            │
                            ▼
                       Tool Runtime
                            │
                            ▼
                        Observation
                            │
                            ▼
                       Update State
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 ▼                     ▼
             Progress?              Stop Check
                 │                     │
          ┌──────┴──────┐        ┌─────┴─────┐
          ▼             ▼        ▼           ▼
         Yes            No     Continue      Stop
          │             │        │           │
          │         Replan /     └─────┐     ▼
          │          Retry             │ Completion
          │             │              │   Check
          └─────────────┴──────────────┘
```

脑中最后只留一句：

> **Agent Loop 的目标不是“让模型一直做事”，而是让每一步都能产生可验证进展，并在任务真正完成、无法继续或需要人工介入时正确停止。**

---

# 第七课 · 第 5 阶段掌握测试

现在不回看正文，你应该能够解释：为什么 Tool Calling 不等于 Agent Loop；Plan 为什么更适合短视野而不是一次生成完整未来；Action 为什么必须是可执行决策；Observation 为什么必须来自真实 Runtime；Conversation History 为什么不能替代 Task State；为什么 Action Success 不等于 Task Success；Stop Condition 和 Completion Check 有什么区别；Step Budget 为什么必要；怎样识别 No-progress 和 Repeated Action；Retry 与 Replan 的根本区别是什么；为什么 Failure State 必须正式建模；Human Approval 怎样让 Loop 暂停和恢复；Write Tool 为什么需要 Idempotency；Checkpoint 为什么重要；为什么可靠 Agent 更像“LLM 决策 + 状态机”而不是无限自由循环；以及为什么最终评测必须看 Task Completion Rate。

如果这些能够完整讲出来：

\[
\boxed{
第七课第5阶段真正掌握
}
\]

---

# 下一阶段：第七课 · 第 6 阶段
# Planning 与 Task Decomposition：复杂采购任务怎样拆步骤？
## Agent 已经会循环了，但它到底怎样把一个模糊大任务拆成可执行的子任务？

到第 5 阶段，我们已经有：

\[
\boxed{
Plan
\rightarrow
Act
\rightarrow
Observe
\rightarrow
UpdateState
\rightarrow
Continue/Stop
}
\]

下一阶段要进一步解决：

> **Plan 到底是怎么产生的？**

例如用户说：

```text
“帮我完整审查这份采购文件。”
```

这不是一个 Tool 能完成的。

Agent 必须拆成：

```text
读取文件
↓
识别文件结构
↓
抽取资格条件
↓
抽取评分标准
↓
抽取技术参数
↓
抽取合同要求
↓
分别检索规则
↓
识别风险
↓
整合证据
↓
生成报告
```

下一阶段我们会正式进入：

```text
Goal
Subgoal
Task Graph
Dependency
Sequential / Parallel
Critical Path
Dynamic Decomposition
Plan Revision
Over-decomposition
Under-decomposition
```

并建立：

# `ProcurementTaskPlanningPolicy_V0.1`

这会把 Agent 从：

> “知道下一步怎么循环”

推进到：

> **“知道复杂任务应该被拆成什么结构，哪些步骤先做、哪些可以并行、哪些依赖前一步结果”。**



---
