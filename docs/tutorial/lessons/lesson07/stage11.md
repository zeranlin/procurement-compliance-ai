# 第七课 · 第 11 阶段
# 真正搭建 `ProcurementAgent_V0.1`：端到端政府采购工作流
## 怎样把 RAG、Tools、Planning、State、Recovery、Safety、Human Approval 和 Evaluation 全部接成一个真正可以执行、可以审计、可以评测的系统？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：缺少统一、醒目的阶段核心心智模型入口；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，LLM 不是 Agent；Agent 是 Model + State + Tools + Policy + Loop，模型只是决策组件。**
2. **第二，Tool Calling 不是模型直接执行函数，而是 Structured Tool Request → Runtime Execution → Tool Result → New Observation。**
3. **第三，复杂任务必须经过 Planning 与 Task Graph，Agent Loop 必须依赖真实 State，而不是只靠聊天历史。**
4. **第四，RAG、Database、File、Compute、Action Tool 不能混为一谈；Routing 首先要找到正确 Source of Truth。**
5. **第五，可靠 Agent 不是永不失败，而是失败以后能够正确 Retry、Replan、Verify、Fallback、Compensate 或 Escalate。**
6. **第六，Agent Safety 不是让模型“更听话”，而是用 Least Privilege、Capability Boundary、Approval Gate、Data Boundary 和 Runtime Policy 阻止不该发生的真实动作。**
7. **第七，真正可发布的 Agent 必须让 Planning、Tool、State、Recovery、Safety、Evidence、Completion 与 Audit 都能单独评测和 Trace；AgentQuality ≠ FinalAnswerQualityOnly。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `State` | 状态：保存任务进度、事实和待办 |
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `Recovery` | 恢复：工具失败或中断后安全重试、降级和继续 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Planning` | 任务规划：把目标拆成可执行、带依赖的子任务 |
| `ANN` | ANN/近似最近邻：在大规模向量中快速寻找相似项 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `Routing` | 路由：决定当前任务交给哪个工具/模块 |
| `Validation` | 验证集：开发阶段用于选模型、调参数和早停 |
| `Tool Calling` | 工具调用：模型按受控协议选择工具并构造参数 |
| `Memory` | 任务记忆：保存跨步骤需要复用的结构化信息 |

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

前 10 个阶段，我们已经分别建立了：

```text
Stage 1
Agent Boundary

Stage 2
Tool Calling Protocol

Stage 3
Structured Output

Stage 4
Tool Registry / Capability Boundary

Stage 5
Agent Loop

Stage 6
Planning / Task Decomposition

Stage 7
State / Memory / Working Context

Stage 8
RAG + Tool Routing

Stage 9
Failure Recovery / Human-in-the-loop

Stage 10
Agent Safety / Audit Trail
```

最后一个阶段不再继续增加新的“大概念”。

我们要做的是：

> **把这些组件真正接起来。**

最终形成：

# `ProcurementAgent_V0.1`

---

# 一、先锁死最终系统定义

`ProcurementAgent_V0.1` 不是：

> 一个会自动调用工具的大模型。

更准确地说：

\[
\boxed{
ProcurementAgent\_V0.1
=
ProcurementRAG\_V0.1
+
Planning
+
State
+
Tools
+
Policy
+
Recovery
+
HumanApproval
+
Evaluator
}
\]

其中：

```text
ProcurementRAG_V0.1
负责：
外部知识与证据

Planning
负责：
把目标拆成任务

State
负责：
保存真实任务进度

Tools
负责：
执行外部动作

Policy
负责：
限制能力和权限

Recovery
负责：
失败后的恢复

Human Approval
负责：
高风险节点的人类控制

Evaluator
负责：
判断任务是否真的完成
```

所以最终边界是：

\[
\boxed{
LLM
负责Decision
}
\]

\[
\boxed{
Runtime
负责Execution
}
\]

\[
\boxed{
State
负责TruthOfProgress
}
\]

\[
\boxed{
Policy
负责CapabilityBoundary
}
\]

\[
\boxed{
Evaluator
负责CompletionTruth
}
\]

---

# 二、最终端到端主链

整个 `ProcurementAgent_V0.1` 的在线执行链可以压成：

```text
User Goal
↓
Goal Understanding
↓
Task Planning
↓
Task State Initialization
↓
Tool Discovery
↓
RAG / Tool Routing
↓
Structured Tool Call
↓
Runtime Validation
↓
Authorization / Approval
↓
Execution
↓
Observation
↓
State Update
↓
Progress / Completion Check
↓
Continue / Replan / Recover / Stop
↓
Final Artifact
↓
Audit Trace
↓
Evaluation
```

用公式表达：

\[
S_{t+1}
=
Update(
S_t,
Observation_t
)
\]

而下一步决策：

\[
Decision_{t+1}
=
Policy(
Goal,
S_{t+1},
WorkingContext_{t+1}
)
\]

直到：

\[
CompletionCheck(S_t)=True
\]

或：

\[
StopCondition(S_t)=True
\]

---

# 三、真正开始运行以前：先建立 Task Contract

用户说：

> “帮我完整审查这份采购文件，并生成带依据的风险报告。”

不能马上乱调 Tool。

先建立一个：

# Task Contract
## 任务契约

至少包括：

```json
{
  "task_id": "T_001",
  "goal": "完整审查采购文件并生成风险报告",
  "scope": {
    "document_id": "FILE_001"
  },
  "required_outputs": [
    "qualification_review",
    "scoring_review",
    "technical_review",
    "contract_review",
    "evidence_map",
    "final_report"
  ],
  "allowed_side_effect": "draft_only",
  "human_approval_required_for": [
    "external_publish",
    "formal_submission"
  ],
  "completion_criteria": [
    "required_sections_reviewed",
    "evidence_attached",
    "unresolved_items_marked",
    "report_generated"
  ]
}
```

这一步非常重要。

因为：

\[
\boxed{
Goal
必须先变成
MachineCheckableTaskContract
}
\]

否则后面根本无法判断：

> “任务到底算不算完成？”

---

# 四、初始化 State：系统一开始必须知道自己处于什么状态

第一版 Task State：

```json
{
  "task_id": "T_001",
  "status": "running",
  "step": 0,
  "goal": "完整审查采购文件并生成风险报告",
  "task_graph_version": 1,
  "completed_tasks": [],
  "pending_tasks": [],
  "blocked_tasks": [],
  "artifact_refs": [],
  "evidence_ids": [],
  "needs_review": false,
  "approval_state": {},
  "state_version": 1
}
```

然后 Planning 模块生成 Task Graph。

例如：

```text
T0 读取采购文件
↓
T1 识别文档结构
↓
├─ T2 资格条件审查
├─ T3 评分标准审查
├─ T4 技术参数审查
└─ T5 合同条款审查
↓
T6 汇总证据
↓
T7 生成报告
↓
T8 Completion Check
```

这样系统从第一步开始就不是：

> “聊天。”

而是：

> **执行一个有状态的任务实例。**

---

# 五、Tool Discovery：每一步只暴露当前真正需要的能力

当任务处于：

```text
T0 读取采购文件
```

当前可见 Tool 可以只有：

```text
procurement.read_file
procurement.parse_document
```

进入规则审查以后再暴露：

```text
regulation.search
project.get_metadata
compute.basic
```

准备生成报告时：

```text
report.create_draft
artifact.save
```

所以：

\[
\boxed{
VisibleTools_t
=
RelevantCapabilities(
Task_t,
Policy,
UserPermission
)
}
\]

而不是：

> 从任务第一秒开始就把全部系统能力暴露给模型。

---

# 六、Routing：每一个信息需求先找 Source of Truth

假设当前子任务是：

> “判断资格条件 R1 是否存在风险。”

Agent 需要的不是一个 Tool，

而可能是多路 Source：

```text
R1原文
→ File / Artifact

项目辖区
→ Project Database

当前查询时间
→ Runtime State

适用规则
→ ProcurementRAG_V0.1

风险判断
→ ProcurementLM_V0.1
```

所以：

\[
\boxed{
OneSubtask
可能需要
MultiSourceRoute
}
\]

最终进入 Working Context 的不是“无来源文本”，而是：

```text
Requirement R1
+
Project Metadata
+
Evidence E1 / E2
+
Source Version
+
Validity
+
Current Task State
```

---

# 七、Structured Tool Call：所有动作都必须经过数据契约

模型决定调用：

```text
regulation.search
```

输出不能是：

```text
“帮我查一下本地机构规定”
```

而应该是：

```json
{
  "tool": "regulation.search",
  "arguments": {
    "query": "投标前要求供应商设立本地机构",
    "jurisdiction_code": "CN-XX",
    "query_time": "2026-09-17"
  }
}
```

Runtime 依次执行：

```text
JSON Parse
↓
Schema Validation
↓
Semantic Validation
↓
Capability Check
↓
Resource Scope Check
↓
Risk / Approval Check
↓
Execution
```

所以：

\[
\boxed{
ModelOutput
不能直接等于Execution
}
\]

中间永远存在 Runtime Gate。

---

# 八、Agent Loop：每一次 Tool Result 都要回到 State

Tool Result：

```json
{
  "status": "success",
  "evidence_ids": [
    "E1",
    "E2"
  ]
}
```

不能只塞进聊天历史。

应该产生：

```text
Observation
↓
State Transition
↓
State Version + 1
↓
Event Log
↓
Working Context Refresh
```

例如：

```json
{
  "task_id": "T_001",
  "current_task": "review_requirement_R1",
  "evidence_ids": [
    "E1",
    "E2"
  ],
  "current_task_status": "evidence_ready",
  "state_version": 12
}
```

然后模型才进行下一次 Decision。

这就是：

\[
\boxed{
ToolResult
\rightarrow
Observation
\rightarrow
State
\rightarrow
NextDecision
}
\]

而不是：

\[
ToolResult
\rightarrow
直接生成最终答案
\]

---

# 九、Recovery：失败以后必须走显式恢复路径

假设：

```text
regulation.search
```

返回：

```text
timeout
```

Recovery Policy 先判断：

```text
这是Transient Failure吗？
有没有Side Effect？
是否可Retry？
是否需要Backoff？
```

因为这是只读 Tool，

可以：

```text
Retry
→ Backoff
→ Retry
```

如果最终仍失败：

```text
Fallback
或
Replan
或
needs_review
```

但如果失败的是：

```text
publish_notice
```

则必须：

```text
Verify External State
↓
Check Operation ID
↓
Confirm Not Executed
↓
Retry with Same Idempotency Key
```

所以：

\[
\boxed{
RecoveryPath
必须和ToolSideEffect绑定
}
\]

---

# 十、Human Approval：人工不是异常，而是正式控制节点

如果最终用户要求：

> “把修改后的公告正式发布。”

系统不能因为：

```text
报告已经生成
```

就自动调用：

```text
publish_notice
```

而应该：

```text
Draft Ready
↓
Risk Classification
↓
Approval Required
↓
waiting_for_approval
↓
Trusted Human Approval
↓
Runtime Revalidates State
↓
Execute
```

注意：

> Approval 后还要重新检查 External State。

因为等待审批期间：

```text
文件可能更新
项目状态可能改变
审批权限可能变化
```

所以：

\[
\boxed{
Approval
不是解除所有后续检查
}
\]

---

# 十一、Completion Check：最终不是模型说“完成了”就算完成

假设 Task Contract 要求：

```text
资格条件审查
评分标准审查
技术参数审查
合同条款审查
证据映射
风险报告
未解决项标记
```

Completion Evaluator 应逐项检查：

```text
qualification_review_done
scoring_review_done
technical_review_done
contract_review_done
evidence_map_complete
report_generated
unresolved_items_explicit
```

只有满足：

\[
\boxed{
AllRequiredCompletionCriteria=True
}
\]

任务状态才能进入：

```text
completed
```

否则可能是：

```text
partial_success
needs_review
blocked
failed_terminal
```

所以：

\[
\boxed{
ModelSaysDone
\neq
TaskCompleted
}
\]

---

# 十二、最终系统数据契约

一个真实 Agent 系统必须让模块之间传递：

> 内容 + 身份 + 状态 + 来源 + 版本。

第一版可以有以下核心对象。

## 1. TaskRequest

```json
{
  "task_id": "T_001",
  "user_goal": "...",
  "actor_id": "U_001",
  "input_artifacts": [
    "FILE_001"
  ],
  "request_time": "..."
}
```

## 2. TaskState

```json
{
  "task_id": "T_001",
  "status": "running",
  "state_version": 12,
  "current_task": "review_R1",
  "completed_tasks": [],
  "pending_tasks": [],
  "artifact_refs": [],
  "evidence_ids": [],
  "approval_state": {}
}
```

## 3. ToolRequest

```json
{
  "tool_call_id": "TC_018",
  "tool_name": "regulation.search",
  "tool_version": "v2",
  "arguments": {},
  "requested_by_task": "T_001"
}
```

## 4. ToolResult

```json
{
  "tool_call_id": "TC_018",
  "status": "success",
  "result": {},
  "source_version": "...",
  "executed_at": "..."
}
```

## 5. AgentResponse

```json
{
  "task_id": "T_001",
  "status": "completed",
  "answer": "...",
  "artifact_refs": [
    "ART_014"
  ],
  "evidence_ids": [
    "E1",
    "E2"
  ],
  "needs_review": false,
  "trace_id": "TRACE_001"
}
```

核心原则：

\[
\boxed{
每个模块传递的不只是Text
还必须传递Identity / Version / Provenance / State
}
\]

---

# 十三、最终运行时伪代码

可以把 `ProcurementAgent_V0.1` 压成下面的库无关逻辑：

```python
def run_agent(task_request):
    state = initialize_state(task_request)
    plan = build_task_graph(task_request, state)

    while True:
        if stop_condition(state):
            break

        if completion_check(state):
            state.status = "completed"
            break

        current_task = choose_ready_task(plan, state)

        visible_tools = discover_tools(
            task=current_task,
            state=state,
            actor=task_request.actor_id
        )

        working_context = build_working_context(
            task=current_task,
            state=state,
            artifacts=load_relevant_artifacts(state),
            memory=retrieve_relevant_memory(state),
            evidence=retrieve_relevant_evidence(state)
        )

        decision = llm_decide(
            task=current_task,
            context=working_context,
            tools=visible_tools
        )

        validated_action = runtime_validate(
            decision=decision,
            state=state,
            actor=task_request.actor_id
        )

        if validated_action.requires_approval:
            state = pause_for_approval(state, validated_action)
            break

        result = execute_tool(validated_action)

        observation = normalize_result(result)

        state = update_state(
            state=state,
            observation=observation
        )

        if observation.is_failure:
            state = recover_or_replan(
                state=state,
                observation=observation
            )

        plan = revise_plan_if_needed(
            plan=plan,
            state=state
        )

    return build_final_response(state)
```

这段代码最重要的不是语法。

而是顺序：

\[
\boxed{
Plan
\rightarrow
Discover
\rightarrow
Context
\rightarrow
Decide
\rightarrow
Validate
\rightarrow
Execute
\rightarrow
Observe
\rightarrow
State
\rightarrow
Recover/Replan
\rightarrow
Complete
}
\]

---

# 十四、端到端评测：不能只看最终答案

真正 Agent 至少要分层评测。

## Layer 1：Planning

```text
subtask_coverage
dependency_accuracy
plan_revision_success_rate
```

## Layer 2：Tool / Routing

```text
source_of_truth_accuracy
tool_selection_accuracy
argument_valid_rate
authorization_accuracy
```

## Layer 3：State

```text
state_consistency_rate
state_update_accuracy
checkpoint_resume_success_rate
```

## Layer 4：Recovery

```text
retry_precision
replan_success_rate
duplicate_side_effect_rate
recovery_completion_rate
```

## Layer 5：Safety

```text
prompt_injection_resistance_rate
unauthorized_execution_rate
approval_bypass_rate
audit_trace_coverage
```

## Layer 6：Task Completion

```text
task_completion_rate
partial_success_rate
needs_review_accuracy
completion_false_positive_rate
```

## Layer 7：Quality / Evidence

```text
business_conclusion_accuracy
evidence_correctness
citation_correctness
unsupported_claim_rate
```

所以：

\[
\boxed{
AgentQuality
\neq
FinalAnswerQualityOnly
}
\]

---

# 十五、最终 Trace：出了错必须知道是哪一层

如果最终报告错了，

排查顺序应该是：

```text
1. Goal Understanding
↓
2. Planning
↓
3. Tool Discovery
↓
4. Routing
↓
5. Structured Arguments
↓
6. Runtime Validation
↓
7. Tool Execution
↓
8. Observation
↓
9. State Update
↓
10. Recovery / Replan
↓
11. Completion Check
↓
12. Final Generation
↓
13. Audit / Citation
```

例如：

> 报告漏掉一项技术风险。

不能直接说：

> “模型能力不够。”

可能是：

```text
Planning漏了技术参数子任务
或
File Tool没有提取到对应章节
或
State错误标记为completed
或
Completion Check错误通过
```

所以：

\[
\boxed{
Answer
\rightarrow
Trace
\rightarrow
EveryLayer
}
\]

这是 Agent 工程真正可调试的前提。

---

# 十六、Latency 与 Cost：Agent 成本必须拆解到阶段

端到端延迟可以写成：

\[
T_{total}
=
T_{plan}
+
T_{routing}
+
T_{tool}
+
T_{rag}
+
T_{llm}
+
T_{recovery}
+
T_{approval}
\]

其中某些步骤可以并行。

成本同样应该拆成：

```text
LLM Tokens

Embedding / Retrieval

Reranker

Tool API Calls

Database Queries

Artifact Processing

Human Review

Retries / Recovery
```

因此：

\[
\boxed{
AgentOptimization
不能只优化LLMLatency
}
\]

真正应该优化：

> Critical Path + Unnecessary Calls + Recovery Waste。

---

# 十七、端到端 Benchmark 应该覆盖哪些场景？

第一版 Benchmark 至少要有：

```text
Normal Task
正常完整任务

Multi-step Task
多步任务

Parallel Task
可并行任务

Missing Information
缺少辖区 / 时间 / 文件

Tool Failure
工具超时 / 空结果

Permission Failure
权限不足

Partial Failure
部分分支失败

Conflict
多Source冲突

No-answer / Insufficient Evidence
证据不足

Prompt Injection
文件 / 网页 / Tool Result注入

High-risk Action
需要Approval

Recovery
重试 / Replan / Fallback

Checkpoint Resume
中断后恢复

Version Change
执行中外部状态更新

Completion Trap
表面完成但缺少必要输出
```

因为：

\[
\boxed{
AgentBenchmark
必须测过程
不能只测问答
}
\]

---

# 十八、Release Gate：什么情况下才允许发布 `ProcurementAgent_V0.1`？

最终 Release Gate 至少要覆盖：

```text
Planning Gate
关键子任务覆盖达到基线

Routing Gate
Source-of-Truth错误受控

Tool Gate
结构化参数与执行成功率达标

State Gate
状态一致性与恢复能力达标

Recovery Gate
无高风险重复副作用

Safety Gate
越权、Approval Bypass、Injection测试通过

Evidence Gate
关键结论可追溯

Completion Gate
Completion False Positive受控

Latency Gate
p95延迟可接受

Cost Gate
单任务成本可接受

Regression Gate
升级后不破坏既有能力
```

具体阈值不能在课堂里随便拍脑袋写一个固定数字。

应该由：

```text
真实Benchmark
+
业务风险
+
系统SLA
+
人工成本
```

共同确定。

所以：

\[
\boxed{
ReleaseGateThreshold
必须来自真实验证
}
\]

---

# 十九、最终 Release Bundle

`ProcurementAgent_V0.1` 不应该只交付一段 Agent Prompt。

至少应该包含：

```text
1. ProcurementRAG_V0.1

2. ProcurementAgentBoundaryModel_V0.1

3. ProcurementToolCallingProtocol_V0.1

4. ProcurementStructuredOutputPolicy_V0.1

5. ProcurementToolRegistryPolicy_V0.1

6. ProcurementAgentLoopPolicy_V0.1

7. ProcurementTaskPlanningPolicy_V0.1

8. ProcurementAgentStatePolicy_V0.1

9. ProcurementRAGToolRoutingPolicy_V0.1

10. ProcurementAgentRecoveryPolicy_V0.1

11. ProcurementAgentSafetyPolicy_V0.1

12. Tool Registry Manifest

13. Task State Schema

14. Benchmark Dataset

15. End-to-End Evaluation Report

16. Safety / Injection Test Report

17. Known Limitations

18. Release Manifest
```

所以：

\[
\boxed{
AgentRelease
\neq
OnePrompt
}
\]

而是：

> **一个完整系统版本。**

---

# 二十、把完整政府采购工作流跑一遍

用户目标：

> “审查这份采购文件中的资格条件、评分标准、技术参数和合同要求；找出潜在风险并给出依据；证据不足的地方标记人工复核；最后生成一份结构化报告草稿。”

系统流程：

```text
1. Goal Understanding
识别：
完整采购文件审查

2. Task Contract
锁定：
审查范围
输出要求
只生成草稿
不允许自动发布

3. Planning
拆成：
资格
评分
技术
合同
四个审查分支

4. State Initialization
记录：
pending tasks
artifact refs
approval policy

5. File Tool
读取并解析采购文件

6. Artifact Store
保存结构化解析结果

7. Parallel Review
四个分支分别执行

8. Routing
文件事实
→ Artifact / File

项目元数据
→ Database

规则依据
→ ProcurementRAG_V0.1

计算
→ Compute Tool

9. Evidence
每个风险点绑定 Evidence ID

10. Recovery
某分支检索失败
→ Retry / Replan

11. Human-in-the-loop
证据冲突
→ needs_review

12. State Join
四个分支状态汇合

13. Report Draft
生成结构化风险报告

14. Completion Check
确认：
四类审查都有状态
证据已映射
人工复核项已显式标记
报告已生成

15. Final Response
返回：
报告草稿
Evidence Map
needs_review
trace_id
```

如果用户接着说：

> “把报告里的修改建议直接发布成正式更正公告。”

系统必须开启新的高风险动作链：

```text
Intent Recheck
↓
Capability Check
↓
Resource Scope
↓
Approval Gate
↓
External State Revalidation
↓
Idempotency
↓
Execution
↓
Audit
```

绝不能因为前面的“审查任务”已经完成，

就自动继承：

> 发布权限。

---

# 二十一、第七课 11 个阶段现在怎样连成一个系统？

可以把整课压成下面这张映射：

```text
Stage 1
Agent是什么？
→ 建立边界

Stage 2
Tool Calling
→ 让模型提出真实Action Request

Stage 3
Structured Output
→ 让Action参数可验证

Stage 4
Tool Registry
→ 限定能看到和能执行的Capability

Stage 5
Agent Loop
→ 让动作连续执行

Stage 6
Planning
→ 把复杂Goal拆成Task Graph

Stage 7
State / Memory
→ 让任务长期保持一致状态

Stage 8
RAG + Tool Routing
→ 让每类信息去正确Source of Truth

Stage 9
Recovery
→ 让失败可恢复、可升级

Stage 10
Safety
→ 让能力受到权限、Approval和Audit约束

Stage 11
End-to-End Integration
→ 让整个系统真正可运行、可评测、可发布
```

所以第七课真正完成的是：

\[
\boxed{
从AnsweringSystem
升级到
ControlledActingSystem
}
\]

---

# 二十二、把整课压成最后 7 句话

> **第一，LLM 不是 Agent；Agent 是 `Model + State + Tools + Policy + Loop`，模型只是决策组件。**

> **第二，Tool Calling 不是模型直接执行函数，而是 `Structured Tool Request → Runtime Execution → Tool Result → New Observation`。**

> **第三，复杂任务必须经过 Planning 与 Task Graph，Agent Loop 必须依赖真实 State，而不是只靠聊天历史。**

> **第四，RAG、Database、File、Compute、Action Tool 不能混为一谈；Routing 首先要找到正确 Source of Truth。**

> **第五，可靠 Agent 不是永不失败，而是失败以后能够正确 Retry、Replan、Verify、Fallback、Compensate 或 Escalate。**

> **第六，Agent Safety 不是让模型“更听话”，而是用 Least Privilege、Capability Boundary、Approval Gate、Data Boundary 和 Runtime Policy 阻止不该发生的真实动作。**

> **第七，真正可发布的 Agent 必须让 Planning、Tool、State、Recovery、Safety、Evidence、Completion 与 Audit 都能单独评测和 Trace；`AgentQuality ≠ FinalAnswerQualityOnly`。**

---

# 本阶段最核心的一张图

```text
                           User Goal
                              │
                              ▼
                        Task Contract
                              │
                              ▼
                           Planning
                              │
                              ▼
                         Task State
                              │
                              ▼
                       Tool Discovery
                              │
                              ▼
                    RAG / Tool Routing
                              │
                              ▼
                       LLM Decision
                              │
                              ▼
                    Structured Tool Call
                              │
                              ▼
                     Runtime Policy Gate
                   ┌──────────┼──────────┐
                   ▼          ▼          ▼
                Schema     Capability  Approval
                   │          │          │
                   └──────────┼──────────┘
                              ▼
                          Execution
                              │
                              ▼
                         Observation
                              │
                              ▼
                       State Transition
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
              Progress      Failure      Complete?
                 │            │            │
                 │       Recovery /        │
                 │        Replan           │
                 └────────────┼────────────┘
                              ▼
                       Completion Check
                              │
                              ▼
                        Final Artifact
                              │
                              ▼
                         Audit Trace
                              │
                              ▼
                          Evaluation
```

脑中最后只留一句：

> **`ProcurementAgent_V0.1` 不是一个“会自己干活的大模型”，而是一套让模型在明确 Task、State、Tool、Policy、Approval、Recovery、Evidence 与 Audit 边界里持续决策和执行，直到真实任务被可验证地完成的受控工作流系统。**

---

# 第七课 · 第 11 阶段掌握测试

现在不回看正文，你应该能够解释：`ProcurementAgent_V0.1` 为什么不等于一个会 Tool Calling 的 LLM；Task Contract 为什么必须在任务开始时建立；Task State 和 Task Graph 分别负责什么；为什么 Tool Discovery 要动态限制当前可见能力；一个采购风险判断为什么可能同时需要 File、Database、RAG 和 LLM；Structured Tool Call 到真实执行之间必须经过哪些 Runtime Gate；为什么 Tool Result 必须进入 State；Recovery 为什么必须和 Side Effect 绑定；Human Approval 为什么是正式控制节点而不是异常；为什么 Completion Check 不能由模型一句“完成了”替代；核心数据契约为什么必须携带 Identity、Version、Provenance 和 State；Agent 为什么必须分层评测；Trace 怎样帮助定位最终错误；Latency 和 Cost 为什么要按阶段拆；Agent Benchmark 为什么必须包含失败、安全、恢复、冲突和完成陷阱；Release Gate 为什么不能只看最终回答正确率；以及为什么 Agent Release 最终交付的是一整套系统资产，而不是一个 Prompt。

如果这些能够完整讲出来：

\[
\boxed{
第七课第11阶段真正掌握
}
\]

---

# 第七课正式完成
# `ProcurementAgent_V0.1`

第七课完整系统演化：

\[
\boxed{
ProcurementDataset\_V0.1
\rightarrow
ProcurementLM\_V0.1
\rightarrow
ProcurementRAG\_V0.1
\rightarrow
ProcurementAgent\_V0.1
}
\]

我们已经从：

> **训练一个模型**

一路走到：

> **构建一个能够基于证据、调用工具、维护状态、拆解任务、恢复失败、接受人工控制、限制真实权限并留下完整审计轨迹的政府采购 Agent 系统。**

这就是第七课的最终交付：

# `ProcurementAgent_V0.1`

---
