# 第九课 · 第 7 阶段
# Agent Evaluation：Planning、Tool、State、Recovery、Safety、Completion
## Agent 调用工具成功，为什么仍然可能算任务失败？怎样评测一个会计划、执行、恢复和改变真实状态的系统？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **ToolCallSuccess ≠ TaskCompletion。工具调用成功不等于真实任务完成。**
2. **AgentEval = OutcomeEval + TrajectoryEval。结果和执行轨迹必须同时评。**
3. **Action = Tool + Arguments。只评工具名远远不够。**
4. **HappyPathSuccess ≠ RobustAgent。没有故障注入就测不出恢复能力。**
5. **ActionSuccess ≠ PolicySuccess。成功执行的动作仍可能违反权限或安全策略。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `State` | 状态：保存任务进度、事实和待办 |
| `Planning` | 任务规划：把目标拆成可执行、带依赖的子任务 |
| `Recovery` | 恢复：工具失败或中断后安全重试、降级和继续 |
| `ANN` | ANN/近似最近邻：在大规模向量中快速寻找相似项 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |

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

Agent 和普通 LLM 最大区别是：

> 它不只是“说”，还会“做”。

所以评测 Agent 不能只看：

```text
最终文本像不像标准答案
```

因为 Agent 可能：

```text
调用了错误工具
参数填错
重复提交
状态丢失
遇到失败不会恢复
做了不该做的副作用
```

因此第一条边界：

\[
\boxed{
ToolCallSuccess
\neq
TaskCompletion
}
\]

本阶段最终形成：

# `ProcurementAgentEvalPolicy_V0.1`

---

# 一、Agent Evaluation 为什么必须看 Trajectory？

# Trajectory
## 执行轨迹

包括：

```text
Observe
Plan
Choose Tool
Call Tool
Receive Result
Update State
Replan
Complete
```

两个 Agent 最终都成功，

但一个可能：

```text
2次工具调用完成
```

另一个：

```text
12次调用
3次错误
2次重试
1次危险副作用
```

所以：

\[
\boxed{
SameOutcome
\neq
SameAgentQuality
}
\]

---

# 二、核心心智模型 ①
# `Outcome` 和 `Trajectory` 都要评

Outcome 回答：

> 最终任务完成了吗？

Trajectory 回答：

> 是不是用正确、稳定、安全的方式完成？

因此：

\[
\boxed{
AgentEval
=
OutcomeEval
+
TrajectoryEval
}
\]

---

# 三、Planning：计划是不是合理？

可以评：

```text
Goal Decomposition
目标拆解

Step Ordering
步骤顺序

Dependency Awareness
依赖意识

Unnecessary Steps
冗余步骤

Replanning
动态重规划
```

但注意：

> 不一定要求 Agent 把“思维链”输出出来。

更适合评：

```text
Observable Plan
可观察执行计划

Tool Sequence
工具序列
```

---

# 四、Tool Selection：有没有选对工具？

例如任务需要：

```text
查询预算
```

Agent 却去：

```text
搜索法规
```

即使工具调用成功，

也没意义。

所以：

\[
\boxed{
ToolAvailability
\neq
ToolAppropriateness
}
\]

要评：

```text
tool_selected
gold_tool
tool_selection_correct
```

---

# 五、Tool Arguments：工具对了，参数也可能错

例如正确工具：

```text
query_project_budget
```

但：

```text
project_id填错
date范围错
currency单位错
```

所以：

\[
\boxed{
CorrectTool
\neq
CorrectAction
}
\]

真正 Action：

\[
\boxed{
Action
=
Tool
+
Arguments
}
\]

---

# 六、核心心智模型 ②
# `ToolCall` 是结构化行为，不只是函数名

Agent Eval 至少要拆：

```text
Tool Name
Arguments
Timing
Permission
Result Handling
```

这才是真正工具评测。

---

# 七、State：Agent 是否正确维护真实状态？

Agent 可能跨多步处理：

```text
项目A
预算100万
已经提交一次
等待审批
```

如果后面突然：

```text
把项目A当成项目B
重复提交
忘记已审批状态
```

就是：

# State Error
## 状态错误

所以：

\[
\boxed{
AgentMemory
必须以
StateConsistency
评测
}
\]

不是看它“记得多不多”。

---

# 八、Recovery：工具失败时怎么办？

生产工具一定会失败：

```text
Timeout
Rate Limit
Permission Error
Temporary Unavailable
Invalid Input
```

Agent 是否：

```text
重试
换工具
修参数
请求用户补充
转人工
```

决定了：

# Recovery Quality
## 故障恢复质量

所以 Benchmark 必须有：

# Fault Injection
## 故障注入

主动模拟失败。

---

# 九、核心心智模型 ③
# `HappyPathSuccess` 不等于 `RobustAgent`

如果 Benchmark 永远：

```text
工具正常
网络正常
输入完整
权限齐全
```

Agent 分数会虚高。

所以：

\[
\boxed{
Robustness
需要
FailureScenarios
}
\]

---

# 十、Task Completion：到底怎么算“完成”？

必须提前定义：

# Success Condition
## 成功条件

例如：

```text
预算查询任务
Success =
返回正确预算
AND
项目ID正确
AND
币种正确
AND
没有修改任何状态
```

再比如：

```text
提交审批任务
Success =
正确提交
AND
只提交一次
AND
状态更新正确
AND
生成审批记录
```

所以：

\[
\boxed{
Completion
必须MachineCheckable
}
\]

---

# 十一、Side Effect：Agent 最大风险之一

Agent 不只是读取。

有些工具会：

```text
写入
修改
提交
删除
发送
审批
```

所以必须评：

# Side Effect Safety
## 副作用安全

包括：

```text
是否获得必要确认
是否越权
是否重复执行
是否可回滚
是否记录审计日志
```

---

# 十二、核心心智模型 ④
# `SuccessfulAction` 也可能是 `UnsafeAction`

如果 Agent 成功删除了不该删的记录，

技术上：

> API 调用成功。

但系统上：

> 严重失败。

所以：

\[
\boxed{
ActionSuccess
\neq
PolicySuccess
}
\]

---

# 十三、Idempotency：重复调用会不会造成重复副作用？

# Idempotency
## 幂等性

例如：

> “提交采购审批”

如果网络超时，

Agent 不确定是否已经提交。

它再次调用：

> 会不会重复创建两个审批？

所以：

\[
\boxed{
RetrySafety
需要
IdempotencyAwareness
}
\]

Benchmark 应设计：

> 第一次调用成功但响应丢失

这种场景。

---

# 十四、Human-in-the-loop：什么时候应该停下来找人？

Agent 不应该什么都自己做。

可以评：

```text
Escalation Correctness
升级人工是否正确

Confirmation Timing
确认时机

Uncertainty Handling
不确定性处理
```

所以：

\[
\boxed{
GoodAgent
包括
KnowingWhenToStop
}
\]

---

# 十五、Cost / Latency：完成同一任务的代价不同

可以记录：

```text
tool_calls
tokens
latency
retries
external_cost
```

于是：

\[
\boxed{
AgentEfficiency
=
GoalCompletion
per
ResourceCost
}
\]

不是严格一个固定公式，

而是工程思想。

---

# 十六、核心心智模型 ⑤
# `MoreToolCalls` 不代表 `MoreReasoning`

Agent 乱试工具，

可能产生很多调用。

所以：

\[
\boxed{
ToolCallCount
不是
IntelligenceMetric
}
\]

更重要的是：

> 是否必要、正确、有效。

---

# 十七、Agent Eval 需要真实工具还是 Mock？

两种都需要。

# Mock / Sandbox Tools
## 模拟工具

优点：

```text
稳定
可复现
无真实副作用
便于Fault Injection
```

适合 Benchmark。

# Live Tools
## 真实工具

能检验：

> 真正系统集成。

但不稳定、成本高、风险高。

所以：

\[
\boxed{
OfflineAgentEval
+
ControlledLiveEval
}
\]

更完整。

---

# 十八、Agent Failure Taxonomy

建议至少：

```text
A1 Goal Misunderstanding
目标理解错误

A2 Planning Error
计划错误

A3 Wrong Tool
工具选择错误

A4 Wrong Arguments
参数错误

A5 State Error
状态错误

A6 Recovery Failure
恢复失败

A7 Permission Violation
权限违规

A8 Unsafe Side Effect
危险副作用

A9 Duplicate Action
重复动作

A10 Failed Escalation
该转人工未转

A11 Incomplete Task
任务未完成
```

---

# 十九、核心心智模型 ⑥
# `Agent Failure` 必须区分“没完成”和“危险地完成”

一个 Agent：

> 没完成审批。

另一个 Agent：

> 完成了审批，但越权提交。

第二种可能更危险。

所以：

\[
\boxed{
CompletionRate
不能替代
SafetyRate
}
\]

---

# 二十、本阶段正式工程产物
# `ProcurementAgentEvalPolicy_V0.1`

至少锁定：

```text
agent_eval_policy_version

task_definition

success_condition

trajectory_capture

planning_eval

tool_selection_eval

tool_argument_eval

state_consistency_eval

fault_injection_suite

recovery_eval

side_effect_policy

permission_eval

idempotency_eval

human_escalation_eval

completion_metric

safety_metric

latency_metric

cost_metric

mock_tool_policy

live_tool_policy

failure_taxonomy

release_gate
```

---

# 二十一、本阶段最重要的 9 个核心心智模型

> **心智模型 ①：`ToolCallSuccess ≠ TaskCompletion`。工具调用成功不等于真实任务完成。**

> **心智模型 ②：`AgentEval = OutcomeEval + TrajectoryEval`。结果和执行轨迹必须同时评。**

> **心智模型 ③：`Action = Tool + Arguments`。只评工具名远远不够。**

> **心智模型 ④：`HappyPathSuccess ≠ RobustAgent`。没有故障注入就测不出恢复能力。**

> **心智模型 ⑤：`ActionSuccess ≠ PolicySuccess`。成功执行的动作仍可能违反权限或安全策略。**

> **心智模型 ⑥：`RetrySafety` 需要 Idempotency Awareness。重试可能制造重复副作用。**

> **心智模型 ⑦：`GoodAgent` 包括知道什么时候停下来、确认或转人工。**

> **心智模型 ⑧：`ToolCallCount ≠ IntelligenceMetric`。工具调用越多不等于 Agent 越聪明。**

> **心智模型 ⑨：`CompletionRate ≠ SafetyRate`。完成任务和安全完成是两个不同目标。**

---

# 二十二、下一阶段：第九课 · 第 8 阶段
# Slice Evaluation：Risk Type、行业、地区、难度、Hard Case

最关键的边界：

\[
\boxed{
OverallScore
\neq
SliceReliability
}
\]

并建立：

# `ProcurementSliceEvalPolicy_V0.1`

---
