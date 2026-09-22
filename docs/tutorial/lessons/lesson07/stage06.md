# 第七课 · 第 6 阶段
# Planning 与 Task Decomposition：复杂采购任务怎样拆步骤？
## Agent 已经会循环了，但它到底怎样把一个模糊大任务拆成可执行、可验证、可恢复的子任务？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，Planning 不是写待办清单，而是把 Goal → Subgoal → Executable Task → Dependency → Completion Criteria 变成一个可执行任务模型。**
2. **第二，复杂任务更适合表示成 Task Graph，而不是单一线性步骤；Dependency 决定 Sequential / Parallel，Join 决定并行分支何时可以重新汇合。**
3. **第三，一个 Task 最好具有清楚的 Inputs、Preconditions、Action、Outputs 和 Completion Criteria；拆得太粗无法执行，拆得太细则会造成步骤爆炸。**
4. **第四，可靠规划通常采用“稳定高层骨架 + 动态细节展开”：High-level Plan 可以稳定，Detailed Plan 应根据真实 Observation 随时 Revision。**
5. **第五，Planning Error 必须和 Tool Execution Error 分开；即使所有 Tool 都成功，只要遗漏 Subtask、依赖错误或错误并行化，整个任务仍然可能失败。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Planning` | 任务规划：把目标拆成可执行、带依赖的子任务 |
| `ANN` | ANN/近似最近邻：在大规模向量中快速寻找相似项 |
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `State` | 状态：保存任务进度、事实和待办 |
| `Observe` | Observe/观察：读取当前状态和工具结果 |

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

第 5 阶段我们已经得到：

\[
\boxed{
State
\rightarrow
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

这解决了：

> **Agent 怎样持续运行。**

但新的问题是：

> **Plan 到底从哪里来？**

用户可能只说一句：

```text
“帮我完整审查这份采购文件。”
```

这不是一个 Tool 可以直接完成的动作。

Agent 必须把这个 Goal 拆成：

```text
读取文件
↓
识别文档结构
↓
抽取资格条件
↓
抽取评分标准
↓
抽取技术参数
↓
抽取合同要求
↓
分别检索适用规则
↓
识别风险
↓
整合证据
↓
生成报告
```

所以本阶段正式进入：

# Planning
## 规划

以及：

# Task Decomposition
## 任务分解

本阶段最终形成：

# `ProcurementTaskPlanningPolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

Planning 的本质不是：

> **“让模型写一个很长的待办清单。”**

而是：

\[
\boxed{
Goal
\rightarrow
Subgoals
\rightarrow
ExecutableTasks
\rightarrow
Dependencies
\rightarrow
CompletionCriteria
}
\]

一个好的 Plan 必须回答五件事：

```text
最终目标是什么？

为了达到目标，需要哪些子目标？

每个子目标对应哪些可执行任务？

这些任务之间有什么依赖？

怎样判断每个任务真的完成？
```

所以：

\[
\boxed{
Plan
\neq
PrettyChecklist
}
\]

---

# 二、Goal 和 Action 之间通常差了很多层

用户目标可能是：

```text
完成采购文件风险审查
```

而 Runtime 真正能执行的是：

```text
read_file
extract_requirements
search_regulation
calculate_score
create_report
```

中间需要一层：

# Task Decomposition

把：

\[
HighLevelGoal
\]

变成：

\[
ExecutableActions
\]

例如：

```text
Goal:
完成采购文件风险审查

Subgoal A:
理解采购文件内容

Subgoal B:
识别潜在风险点

Subgoal C:
找到适用证据

Subgoal D:
形成审查结果

Executable Tasks:
read_file
extract_sections
extract_requirements
search_regulation
evaluate_risk
create_report
```

这就是：

\[
\boxed{
Goal
\rightarrow
Subgoal
\rightarrow
Task
\rightarrow
Action
}
\]

---

# 三、Task Graph：复杂任务不应该只是一条线

很多任务不是：

```text
A → B → C → D
```

而更像：

```text
                读取文件
                   │
                   ▼
               识别结构
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
     资格条件    评分标准    技术参数
        │          │          │
        ▼          ▼          ▼
     检索规则    检索规则    检索规则
        │          │          │
        └──────────┼──────────┘
                   ▼
                汇总风险
                   │
                   ▼
                生成报告
```

这就是：

# Task Graph
## 任务图

任务图中的节点是：

> Task。

边表示：

> Dependency。

---

# 四、Dependency：哪些任务必须先做，哪些可以并行？

如果：

```text
B 需要 A 的输出
```

那么：

\[
A
\rightarrow
B
\]

例如：

```text
读取文件
→
抽取资格条件
```

因为没有文件内容：

> 不能抽取资格条件。

但：

```text
审查资格条件
审查评分标准
审查技术参数
```

在文件结构已经提取后，

可能互不依赖。

因此可以并行：

```text
             ┌→ qualification_review
parse_file ──┼→ scoring_review
             └→ technical_review
```

所以：

\[
\boxed{
Dependency
决定
Sequential\ or\ Parallel
}
\]

---

# 五、DAG：为什么任务图最好尽量是有向无环图？

很多规划可以表示为：

# DAG
## Directed Acyclic Graph，有向无环图

意思是：

```text
任务有方向
但不要形成无意义循环
```

例如：

```text
A → B → C
```

是正常依赖。

而：

```text
A → B → C → A
```

就意味着：

> 任务定义本身可能形成循环依赖。

注意：

> Agent Loop 可以循环。

但：

> 高层 Task Dependency 不应该无缘无故形成闭环。

因此：

\[
\boxed{
Loop
用于执行控制
}
\]

而：

\[
\boxed{
TaskGraph
用于表达任务依赖
}
\]

两者不是一回事。

---

# 六、每个 Task 都必须有 Preconditions 和 Completion Criteria

一个 Task 不能只写：

```text
“审查资格条件”
```

还应该明确：

# Preconditions
## 前置条件

例如：

```text
采购文件已读取
资格条件已抽取
项目辖区已知
```

以及：

# Completion Criteria
## 完成标准

例如：

```text
每条资格条件都有：
risk_status
reason
evidence_ids
needs_review
```

所以一个 Task 可以抽象为：

\[
Task
=
\{
Inputs,
Preconditions,
Action,
Outputs,
CompletionCriteria
\}
\]

这会极大降低：

> “看起来做过，实际上没完成”

的问题。

---

# 七、Granularity：任务拆多细才合适？

这是 Planning 最难的工程问题之一。

如果拆得太粗：

# Under-decomposition
## 分解不足

例如：

```text
Task 1:
完整审查采购文件
```

Runtime 根本不知道怎么执行。

---

如果拆得太细：

# Over-decomposition
## 过度分解

例如：

```text
打开文件
读取第一页
识别第一个标题
读取第二页
识别第二个标题
……
```

会导致：

```text
步骤爆炸
成本上升
状态复杂
错误机会增多
计划难以维护
```

所以合适粒度是：

\[
\boxed{
一个Task
最好对应
一个清楚输入
+
一个可执行能力
+
一个可验证输出
}
\]

---

# 八、稳定骨架 + 动态分支，比“一次生成完整计划”更可靠

第 5 阶段我们强调：

> Short-horizon Planning。

第 6 阶段把它进一步精确化。

可以先有一个：

# Stable Skeleton
## 稳定任务骨架

例如：

```text
读取
→
抽取
→
检索
→
判断
→
汇总
```

然后运行过程中根据 Observation 动态展开：

```text
如果发现资格条件
→ 展开资格审查分支

如果发现评分条款
→ 展开评分审查分支

如果证据冲突
→ 增加版本核验任务

如果辖区未知
→ 增加澄清任务
```

所以：

\[
\boxed{
HighLevelPlan
可以相对稳定
}
\]

但：

\[
\boxed{
DetailedPlan
应随Observation动态调整
}
\]

---

# 九、Conditional Branch：真实任务一定会出现条件分支

规划不只是：

```text
Step 1
Step 2
Step 3
```

还会有：

```text
IF 发现本地化要求
THEN 检索本地机构相关规则

IF 文号明确
THEN 精确检索

ELSE
语义检索

IF 证据不足
THEN needs_review

IF 高风险动作
THEN human_approval
```

这就是：

# Conditional Planning
## 条件式规划

因此一个真实 Plan 更像：

> Task Graph + Conditions

而不是简单列表。

---

# 十、Join：并行子任务最后必须重新汇合

假设三个分支并行：

```text
qualification_review
scoring_review
technical_review
```

最终生成报告之前，

必须确认：

```text
三个分支都完成
或
某个分支明确标记 incomplete / needs_review
```

这叫：

# Join
## 汇合

可以写成：

\[
JoinReady
=
AllRequiredDependenciesResolved
\]

这里的“Resolved”不一定意味着：

> 成功。

也可以意味着：

> 已明确失败并记录状态。

关键是：

> 上游状态必须清楚。

---

# 十一、Critical Path：什么决定整个任务最快多久完成？

在一个 Task Graph 中，

有些任务可以并行，

但有一条最长依赖链会决定：

> 整体最短完成时间。

这叫：

# Critical Path
## 关键路径

例如：

```text
读取文件
→
解析结构
→
资格审查
→
汇总
→
报告生成
```

如果资格审查是最慢分支，

即使评分和技术分支很快：

> 整个报告仍然要等资格分支。

所以：

\[
\boxed{
优化Agent延迟
不只是让每个Tool都更快
}
\]

还要看：

> 哪些任务位于关键路径。

---

# 十二、Plan Revision：什么时候应该改计划？

计划必须允许修改。

例如：

```text
原计划：
直接检索适用规则
```

但 Observation 发现：

```text
项目辖区缺失
```

那么继续检索可能产生错误结果。

此时应该：

```text
暂停原分支
↓
新增任务：获取辖区
↓
获得辖区
↓
恢复检索
```

这就是：

# Plan Revision
## 计划修订

所以：

\[
\boxed{
Plan
是可更新的任务模型
不是不可改变的剧本
}
\]

---

# 十三、Planning Error：规划错误和执行错误必须分开

假设 Agent 最终没完成任务。

可能不是 Tool 失败，

而是：

> 一开始就没规划这个子任务。

例如用户要求：

```text
资格条件
+
评分标准
+
技术参数
+
合同要求
```

Agent 只规划了前三项。

所有 Tool 都执行成功，

最终仍然失败。

这叫：

# Missing Subtask Error
## 缺失子任务错误

所以至少要区分：

```text
Missing Subtask
Wrong Dependency
Wrong Ordering
Over-decomposition
Under-decomposition
Invalid Parallelization
Missing Join
Wrong Branch Condition
Premature Plan Completion
```

这些都属于：

> Planning Error。

---

# 十四、怎样评测 Task Planning？

第一版至少记录：

```text
subtask_coverage

dependency_accuracy

ordering_accuracy

parallelization_accuracy

branch_accuracy

completion_criteria_coverage

missing_subtask_rate

over_decomposition_rate

under_decomposition_rate

plan_revision_success_rate

critical_path_latency

final_task_completion_rate
```

最重要的是：

\[
\boxed{
PlanQuality
最终必须由TaskSuccess验证
}
\]

因为一个“看起来很专业”的 Plan：

> 也可能漏任务、依赖错、无法执行。

---

# 十五、政府采购案例：完整采购文件审查 Task Graph

用户目标：

> “完整审查这份采购文件，并生成带证据的风险报告。”

第一版 Task Graph 可以是：

```text
T0 读取采购文件
        │
        ▼
T1 识别文档结构
        │
   ┌────┼────┬────┐
   ▼    ▼    ▼    ▼
 T2    T3    T4    T5
资格  评分  技术  合同
抽取  抽取  抽取  抽取
   │    │    │    │
   ▼    ▼    ▼    ▼
 T6    T7    T8    T9
规则  规则  规则  规则
检索  检索  检索  检索
   │    │    │    │
   ▼    ▼    ▼    ▼
T10   T11   T12   T13
风险  风险  风险  风险
判断  判断  判断  判断
   └────┬────┴────┘
        ▼
T14 汇总证据与风险
        │
        ▼
T15 生成审查报告
        │
        ▼
T16 Completion Check
```

如果某个分支证据不足：

```text
T12
=
needs_review
```

并不一定阻止整个任务继续。

最终报告可以明确：

```text
已完成：
资格 / 评分 / 合同

需要人工复核：
技术参数第3项
```

这比：

> 为了“全部成功”而强行生成确定结论

可靠得多。

---

# 十六、本阶段工程产物：`ProcurementTaskPlanningPolicy_V0.1`

第一版至少锁定：

```text
planning_policy_version

goal_schema

subgoal_schema

task_schema

task_id

task_type

inputs

outputs

preconditions

dependencies

completion_criteria

parallelizable

branch_condition

join_policy

priority

critical_path_tracking

decomposition_granularity

max_subtasks

dynamic_expansion_enabled
=
true

plan_revision_policy

missing_information_policy

human_clarification_policy

trace_logging
=
enabled
```

每次任务至少记录：

```text
original_goal

initial_task_graph

task_dependencies

dynamic_tasks_added

tasks_removed

plan_revision_reason

parallel_groups

critical_path

task_statuses

final_completion_check
```

这样 Planning 才能：

> **被审计、被评测、被优化。**

---

# 十七、把本阶段压成最精准的 6 句话

> **第一，Planning 不是写待办清单，而是把 `Goal → Subgoal → Executable Task → Dependency → Completion Criteria` 变成一个可执行任务模型。**

> **第二，复杂任务更适合表示成 Task Graph，而不是单一线性步骤；Dependency 决定 Sequential / Parallel，Join 决定并行分支何时可以重新汇合。**

> **第三，一个 Task 最好具有清楚的 Inputs、Preconditions、Action、Outputs 和 Completion Criteria；拆得太粗无法执行，拆得太细则会造成步骤爆炸。**

> **第四，可靠规划通常采用“稳定高层骨架 + 动态细节展开”：High-level Plan 可以稳定，Detailed Plan 应根据真实 Observation 随时 Revision。**

> **第五，Planning Error 必须和 Tool Execution Error 分开；即使所有 Tool 都成功，只要遗漏 Subtask、依赖错误或错误并行化，整个任务仍然可能失败。**

> **第六，Plan 的最终质量不看它写得多漂亮，而看 Subtask Coverage、Dependency Accuracy、Plan Revision 和最终 Task Completion。**

---

# 本阶段最核心的一张图

```text
                         User Goal
                            │
                            ▼
                      Goal Analysis
                            │
                            ▼
                    Subgoal Decompose
                            │
                            ▼
                       Task Graph
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
          Sequential     Parallel      Conditional
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                        Execute Tasks
                            │
                            ▼
                       Observations
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
           Plan Still Valid?          Join Ready?
                │                       │
          ┌─────┴─────┐                 │
          ▼           ▼                 │
         Yes          No                 │
          │       Plan Revision          │
          └───────────┬──────────────────┘
                      ▼
                Completion Check
```

脑中最后只留一句：

> **真正的 Planning，不是提前猜完未来，而是把目标拆成有依赖、有完成标准、可并行、可修订的任务图，再让 Agent 根据真实 Observation 一步步把这张图执行完。**

---

# 第七课 · 第 6 阶段掌握测试

现在不回看正文，你应该能够解释：Goal、Subgoal、Task、Action 四层有什么区别；为什么复杂任务应该用 Task Graph 而不是简单线性列表；Dependency 怎样决定顺序和并行；为什么 Task Graph 最好尽量是 DAG；Preconditions 和 Completion Criteria 分别解决什么问题；什么叫 Under-decomposition 和 Over-decomposition；为什么“稳定高层骨架 + 动态细节展开”比一次生成完整未来计划更可靠；Conditional Branch 和 Join 分别做什么；Critical Path 为什么决定整体延迟；什么时候需要 Plan Revision；Planning Error 为什么必须和 Tool Execution Error 分开；以及为什么 Plan Quality 最终必须由 Task Completion 来验证。

如果这些能够完整讲出来：

\[
\boxed{
第七课第6阶段真正掌握
}
\]

---

# 下一阶段：第七课 · 第 7 阶段
# State、Memory 与 Working Context：Agent 怎样记住任务进度？
## Agent 已经会拆任务，也会循环执行，但“记住什么、保存在哪里、下一轮把什么重新交给模型”到底应该怎样设计？

到第 6 阶段，我们已经有：

```text
Goal
Subgoal
Task Graph
Dependency
Parallel / Sequential
Conditional Branch
Plan Revision
Completion Criteria
```

下一阶段要解决的是：

> **这些信息到底保存在哪里？**

我们会正式区分：

```text
Conversation History
Working Context
Task State
Short-term Memory
Long-term Memory
Artifact Store
External State
Checkpoint
```

并建立：

# `ProcurementAgentStatePolicy_V0.1`

下一阶段最关键的一条边界会是：

\[
\boxed{
Memory
\neq
把所有历史聊天重新塞进Context
}
\]

而是要设计：

> **什么必须长期保存，什么只在当前任务有效，什么应该结构化进入 State，什么需要按需重新取回。**



---
