# 第七课 · 第 7 阶段
# State、Memory 与 Working Context：Agent 怎样记住任务进度？
## Agent 已经会拆任务，也会循环执行，但“记住什么、保存在哪里、下一轮把什么重新交给模型”到底应该怎样设计？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，Agent Memory 绝不等于把全部聊天历史塞回 Context；Persistent State ≠ Working Context，前者保存真实任务状态，后者只提供当前一步最需要的信息。**
2. **第二，Conversation History 只是交互历史，Task State 才应该成为当前任务的结构化 Source of Truth；Artifact Store 保存大对象，State 只保存必要引用。**
3. **第三，Short-term Memory 服务当前任务，Long-term Memory 服务跨任务信息，但长期记忆必须有 Write Policy、Validity、Provenance 和 Staleness Control。**
4. **第四，Observation 不能直接修改 State，必须经过 State Transition Rule；Task State 还需要 Version 和并发控制，避免 Lost Update。**
5. **第五，Working Context 应该从 State、Recent Observation、Relevant Memory、Artifacts、RAG Evidence 和 Tool Schema 中按当前 Subtask 选择，而不是 Dump Everything。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `State` | 状态：保存任务进度、事实和待办 |
| `Memory` | 任务记忆：保存跨步骤需要复用的结构化信息 |
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |

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

到第 6 阶段，我们已经有：

\[
\boxed{
Goal
\rightarrow
Subgoal
\rightarrow
TaskGraph
\rightarrow
Dependency
\rightarrow
Execution
\rightarrow
PlanRevision
}
\]

现在新的问题是：

> **这些信息到底保存在哪里？**

如果一个 Agent 执行了 30 步，

它不可能每一轮都把：

```text
全部聊天
全部Tool Result
全部文件
全部中间推理
全部历史状态
```

重新塞进 Prompt。

这会导致：

```text
Context膨胀
Token成本上升
关键信息被淹没
旧信息污染当前决策
状态难以验证
失败后难以恢复
```

所以第七课现在正式进入：

# State
## 状态

# Memory
## 记忆

# Working Context
## 当前工作上下文

本阶段最终形成：

# `ProcurementAgentStatePolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

Agent 的“记忆”绝对不等于：

> **把所有历史聊天永久塞进 Context。**

更准确地说：

\[
\boxed{
PersistentState
\neq
WorkingContext
}
\]

其中：

```text
Persistent State
负责：
保存任务真实状态

Working Context
负责：
给当前这一轮模型提供“现在最需要看到的信息”
```

所以：

\[
\boxed{
MemorySystem
=
Store
+
Retrieve
+
Select
+
Update
}
\]

不是：

> 无限堆历史 Token。

---

# 二、Conversation History：聊天记录只是输入历史，不是完整任务状态

Conversation History 保存：

```text
用户说了什么
模型回答了什么
工具调用消息
工具返回消息
```

它很有价值。

但它存在三个问题：

```text
信息是自然语言
结构不稳定
任务事实可能散落在不同轮次
```

例如：

```text
用户第2轮说：
项目在广东

第8轮说：
只审查资格条件

第15轮说：
这个文件是更正版
```

如果每次都靠模型从历史里重新找：

> 风险很高。

所以：

\[
\boxed{
ConversationHistory
\neq
CanonicalTaskState
}
\]

---

# 三、Task State：Agent 真正需要的是结构化“当前事实”

Task State 应该保存：

> **当前任务此刻已经确认的状态。**

例如：

```json
{
  "task_id": "T_001",
  "goal": "审查采购文件资格条件",
  "status": "running",
  "project_id": "P_001",
  "jurisdiction": "CN-GD",
  "document_version": "V2",
  "completed_tasks": [
    "read_file",
    "extract_requirements"
  ],
  "pending_tasks": [
    "review_requirements",
    "create_report"
  ],
  "evidence_ids": [
    "E1",
    "E2"
  ],
  "needs_review": false
}
```

这类 State 的特点是：

```text
结构化
可验证
可更新
可比较
可持久化
```

因此：

\[
\boxed{
TaskState
=
CurrentSourceOfTruth
}
\]

---

# 四、Working Context：模型当前这一轮到底应该看到什么？

Working Context 是：

> **从所有可用信息里，为当前一步挑出的最小必要集合。**

例如当前任务是：

```text
审查资格条件R3
```

那么这一轮模型真正需要看到的可能只有：

```text
当前Goal
当前Subtask
R3原文
项目辖区
查询时间
相关Evidence
可用Tools
最近一次Tool Result
关键Policy
```

而不需要重新看到：

```text
已经完成的技术参数审查全文
20轮之前的闲聊
无关Tool Result
已经过期的中间猜测
```

所以：

\[
\boxed{
WorkingContext
=
RelevantSubset(
State,
Memory,
Artifacts,
RecentObservations
)
}
\]

---

# 五、Context Window 和 Memory 不是一回事

LLM 有：

# Context Window
## 上下文窗口

这是模型一次推理时：

> 能看到多少 Token。

但 Agent Memory 讨论的是：

> 信息怎样跨轮次、跨步骤、甚至跨会话保存和取回。

所以：

\[
\boxed{
ContextWindow
\neq
MemoryStore
}
\]

模型 Context 再长：

> 也不能替代结构化状态管理。

因为问题不只是容量。

更重要的是：

```text
哪一条信息是当前有效状态？
哪一条已经过期？
哪一条来自Tool？
哪一条只是模型猜测？
哪一条应该被覆盖？
```

这些都需要显式 State。

---

# 六、Short-term Memory：当前任务里的临时记忆

Short-term Memory：

# 短期记忆

通常只在当前任务有效。

例如：

```text
刚刚解析出来的章节列表
当前检索候选
本轮失败原因
刚生成的临时摘要
当前分支的中间结果
```

任务结束后：

> 很多信息不需要永久保留。

所以：

\[
\boxed{
ShortTermMemory
=
TaskScopedTemporaryInformation
}
\]

它的生命周期通常和：

```text
task_id
```

绑定。

---

# 七、Long-term Memory：不是所有东西都值得长期记

Long-term Memory：

# 长期记忆

应该保存：

> **跨任务仍然稳定、有价值、允许保存的信息。**

例如在企业 Agent 中可能包括：

```text
稳定业务偏好
组织级规则
长期项目配置
经确认的系统映射关系
长期工具使用约束
```

但不能把所有东西都自动写进去。

因为长期记忆最危险的问题是：

# Stale Memory
## 过期记忆

例如：

```text
旧项目辖区
旧法规状态
旧联系人
旧版本配置
```

如果一直保留：

> 未来任务可能被错误污染。

所以：

\[
\boxed{
LongTermMemory
必须有
WritePolicy
+
Validity
+
Provenance
}
\]

---

# 八、Artifact Store：大文件和中间产物不应该全部塞进 State

Agent 会产生很多 Artifact：

```text
采购文件解析结果
结构化条款
检索结果集
生成的报告草稿
表格
JSON
图片
附件
```

这些东西不适合全部塞进 Task State。

更合理的是：

# Artifact Store
## 产物存储

State 里只保存引用：

```json
{
  "parsed_document_artifact_id": "ART_001",
  "review_report_artifact_id": "ART_014"
}
```

真正的大对象存储在：

> 外部 Artifact Store。

所以：

\[
\boxed{
State
保存Reference
ArtifactStore
保存Payload
}
\]

---

# 九、External State：Agent 之外的真实世界状态必须单独看待

Agent 自己的 Task State 不等于：

> 外部系统真实状态。

例如：

```text
Agent State:
notice_status = "draft"

External Procurement System:
notice_status = "published"
```

如果两者不一致：

> Agent State 已经过期。

所以必须区分：

# Internal State
## Agent 内部状态

和：

# External State
## 外部系统真实状态

重要动作前最好重新确认：

\[
\boxed{
ReadBeforeWrite
}
\]

即：

> 写入前先读取当前外部状态。

避免根据旧 State 做高风险操作。

---

# 十、Checkpoint：状态快照和 Memory 不是一回事

Checkpoint 是：

> 某个时间点完整可恢复的任务快照。

例如：

```json
{
  "checkpoint_id": "CP_007",
  "task_id": "T_001",
  "step": 12,
  "task_state_version": 18,
  "pending_tasks": [
    "review_R3",
    "create_report"
  ],
  "artifact_refs": [
    "ART_001",
    "ART_009"
  ],
  "approval_state": "not_required"
}
```

它解决的是：

# Recovery
## 恢复

因此：

\[
\boxed{
Memory
帮助Agent记住
}
\]

而：

\[
\boxed{
Checkpoint
帮助系统恢复
}
\]

两者相关，但不是同一个概念。

---

# 十一、Event Log：为什么只保存“最终 State”还不够？

假设 Task State 现在是：

```text
status = needs_review
```

我们还需要知道：

> 为什么变成 needs_review？

所以除了 Current State，

最好还保存：

# Event Log
## 事件日志

例如：

```text
E001:
file_read_success

E002:
requirement_R3_found

E003:
regulation_search_empty

E004:
replan_triggered

E005:
second_search_insufficient

E006:
needs_review_set_true
```

因此：

\[
\boxed{
CurrentState
告诉你“现在是什么”
}
\]

\[
\boxed{
EventLog
告诉你“怎么变成这样”
}
\]

这对：

```text
审计
调试
重放
恢复
错误归因
```

都非常重要。

---

# 十二、State Update：谁有资格修改状态？

如果任何 Tool Result 都可以直接覆盖 State，

很危险。

例如恶意内容返回：

```text
status = completed
```

不代表任务真的完成。

所以应该有：

# State Update Policy
## 状态更新策略

流程：

```text
Observation
↓
Parse
↓
Validate
↓
Apply State Transition Rule
↓
Update State
```

所以：

\[
\boxed{
Observation
\neq
StateMutation
}
\]

Observation 是输入。

State Mutation 是：

> 经过规则验证后的状态变化。

---

# 十三、State Version：为什么状态也必须版本化？

Agent 在多步甚至并行执行时，

可能出现：

```text
Worker A读取State v10
Worker B也读取State v10

A更新为v11
B随后拿旧状态覆盖成v11
```

这叫：

# Lost Update
## 丢失更新

所以 Task State 应有：

```text
state_version
```

更新时可以要求：

```text
expected_version = 10
```

如果实际已经是：

```text
11
```

就拒绝盲目覆盖，

重新读取再合并。

所以：

\[
\boxed{
State
也需要ConcurrencyControl
}
\]

---

# 十四、Memory Retrieval：长期保存以后，下一轮怎样取回来？

Long-term Memory 不能每次全部注入。

更合理的是：

```text
Current Task
↓
Memory Query
↓
Relevant Memory Candidates
↓
Validity / Permission Filter
↓
Selected Memory
↓
Working Context
```

这和 RAG 很像。

但要注意：

> Memory Retrieval 和 Knowledge Retrieval 不完全相同。

Knowledge Base 保存的是：

```text
法规
政策
采购文件
外部知识
```

Memory 保存的更多是：

```text
任务状态
历史确认信息
长期偏好
过去交互中形成的稳定上下文
```

所以：

\[
\boxed{
Knowledge
\neq
Memory
}
\]

---

# 十五、Memory Write Policy：什么信息才允许进入长期记忆？

这是 Agent Memory 最关键的治理点之一。

不要采用：

```text
模型觉得重要
→
直接永久保存
```

更好的规则是：

```text
是否稳定？
是否跨任务有价值？
是否已经确认？
是否允许保存？
是否包含敏感信息？
是否有失效时间？
是否有来源？
```

只有通过后：

> 才进入 Long-term Memory。

所以：

\[
\boxed{
MemoryWrite
必须是PolicyDecision
}
\]

而不是模型随手写。

---

# 十六、Provenance：每条 Memory 最好知道从哪里来

假设 Memory 里写着：

```text
“项目辖区 = 广东省”
```

必须知道它来自：

```text
用户明确提供？
项目数据库？
模型推断？
某份文件？
人工确认？
```

所以每条重要 Memory 可以带：

```json
{
  "key": "jurisdiction",
  "value": "CN-GD",
  "source_type": "project_database",
  "source_id": "P_001",
  "confirmed": true,
  "valid_from": "2026-09-17",
  "valid_to": null
}
```

这叫：

# Provenance
## 来源追踪

没有 Provenance 的 Memory：

> 很难判断可信度。

---

# 十七、Staleness：记住错误信息比忘记更危险

一个典型错误是：

> Agent 以前记住了一个正确事实，但后来事实变了。

例如：

```text
旧Memory：
document_version = V1

当前真实状态：
document_version = V3
```

如果长期记忆没有失效机制，

Agent 会稳定地做错。

所以应该支持：

```text
valid_from
valid_to
last_verified_at
source_version
stale_after
```

因此：

\[
\boxed{
MemoryQuality
不仅取决于Recall
还取决于Freshness
}
\]

---

# 十八、Working Context Assembly：每一步到底怎样组装给模型？

最终每一轮模型真正看到的上下文，

可以来自：

```text
System Policy

Current Goal

Current Subtask

Selected Task State

Recent Observation

Relevant Memory

Relevant Artifacts

Relevant RAG Evidence

Visible Tools
```

可以写成：

\[
\boxed{
WorkingContext_t
=
Policy
+
Goal
+
TaskState_t
+
Observation_t
+
SelectedMemory
+
SelectedEvidence
+
ToolSchema
}
\]

关键是：

> **Select。**

不是：

> Dump Everything。

---

# 十九、政府采购案例：长任务怎样跨 20 步仍保持清楚？

用户目标：

> “完整审查采购文件，并生成风险报告。”

第 1 步读取文件后：

```text
ArtifactStore:
ART_001 = parsed_document
```

Task State：

```json
{
  "parsed_document": "ART_001",
  "status": "running",
  "completed": ["read_file"],
  "pending": ["extract_sections", "review", "report"]
}
```

第 8 步已经完成资格审查：

```text
State:
qualification_review = completed

Artifact:
ART_007 = qualification_review_result
```

第 15 步审查评分标准时，

Working Context 不需要重新注入：

> 前 14 步所有对话。

只需要：

```text
Goal
当前Subtask
必要项目Metadata
ART_001中评分标准片段
相关Evidence
当前Task State摘要
```

这样：

> Agent 才能长时间执行而不被历史淹没。

---

# 二十、本阶段错误分类：State / Memory 会怎样坏掉？

至少要区分：

```text
1. State Drift
内部State和真实世界不一致

2. Lost Update
并发更新覆盖

3. Missing State
关键事实没有进入State

4. Wrong State Mutation
错误Observation修改了State

5. Context Overflow
历史信息塞太多

6. Context Omission
当前关键事实没有进入Working Context

7. Stale Memory
使用过期长期记忆

8. Memory Hallucination
模型写入未经确认的事实

9. Provenance Loss
不知道Memory来源

10. Artifact Reference Error
State引用了错误或不存在的Artifact
```

因此：

> “Agent 记忆不好”

不是一个足够精确的诊断。

---

# 二十一、应该怎样评测 Agent State / Memory？

第一版至少可以记录：

```text
state_consistency_rate

state_update_accuracy

lost_update_rate

working_context_precision

working_context_recall

stale_memory_usage_rate

memory_write_precision

memory_retrieval_precision

memory_retrieval_recall

provenance_coverage

artifact_reference_accuracy

checkpoint_restore_success_rate

task_resume_success_rate
```

尤其要分别看：

\[
\boxed{
State正确吗？
}
\]

和：

\[
\boxed{
当前模型看到了正确State吗？
}
\]

这是两回事。

---

# 二十二、本阶段工程产物：`ProcurementAgentStatePolicy_V0.1`

第一版至少锁定：

```text
state_policy_version

task_state_schema

state_version

state_transition_rules

conversation_history_policy

working_context_policy

short_term_memory_policy

long_term_memory_policy

memory_write_policy

memory_retrieval_policy

memory_validity_policy

provenance_required
=
true

artifact_store_policy

artifact_reference_schema

external_state_sync_policy

checkpoint_policy

event_log_enabled
=
true

concurrency_control_enabled
=
true

trace_logging
=
enabled
```

每次循环至少记录：

```text
step_id

state_version_before

selected_working_context

memory_items_retrieved

artifact_refs_loaded

observation

state_transition

state_version_after

event_log_ids

checkpoint_id
```

这样 Agent 才能真正做到：

> **记得住、取得准、改得对、恢复得回来。**

---

# 二十三、把本阶段压成最精准的 6 句话

> **第一，Agent Memory 绝不等于把全部聊天历史塞回 Context；`Persistent State ≠ Working Context`，前者保存真实任务状态，后者只提供当前一步最需要的信息。**

> **第二，Conversation History 只是交互历史，Task State 才应该成为当前任务的结构化 Source of Truth；Artifact Store 保存大对象，State 只保存必要引用。**

> **第三，Short-term Memory 服务当前任务，Long-term Memory 服务跨任务信息，但长期记忆必须有 Write Policy、Validity、Provenance 和 Staleness Control。**

> **第四，Observation 不能直接修改 State，必须经过 State Transition Rule；Task State 还需要 Version 和并发控制，避免 Lost Update。**

> **第五，Working Context 应该从 State、Recent Observation、Relevant Memory、Artifacts、RAG Evidence 和 Tool Schema 中按当前 Subtask 选择，而不是 Dump Everything。**

> **第六，真正可靠的 Agent Memory 系统要同时做到：State 正确、Memory 不过期、Context 选得准、Artifact 引用正确、Checkpoint 可恢复。**

---

# 本阶段最核心的一张图

```text
                     Conversation History
                              │
                              │
               ┌──────────────┴──────────────┐
               ▼                             ▼
          Task State                   Memory Stores
               │                     ┌───────┴────────┐
               │                     ▼                ▼
               │                Short-term        Long-term
               │
               ├──────────────► Artifact Store
               │
               ├──────────────► Event Log
               │
               └──────────────► Checkpoint

                              │
                              ▼
                    Working Context Builder
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
             State         Memory        Evidence
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                         Current LLM Turn
                              │
                              ▼
                         New Observation
                              │
                              ▼
                      State Transition Rule
                              │
                              ▼
                         Updated State
```

脑中最后只留一句：

> **Agent 真正的“记忆能力”，不是记得越多越好，而是把真实任务状态长期保存，把大对象放在合适的 Store，把过期信息及时失效，再在每一步只取回当前决策真正需要的那部分。**

---

# 第七课 · 第 7 阶段掌握测试

现在不回看正文，你应该能够解释：Conversation History、Task State、Working Context 三者有什么根本区别；为什么 Context Window 不能替代 Memory Store；Short-term Memory 和 Long-term Memory 分别服务什么生命周期；Artifact Store 为什么只在 State 里保留引用；Internal State 和 External State 为什么必须区分；Checkpoint 和 Memory 的目标有什么不同；Event Log 为什么能解释 State 是怎样演化出来的；为什么 Observation 不能直接修改 State；State Version 和并发控制解决什么问题；Memory Retrieval 与 RAG Retrieval 有什么区别；为什么 Long-term Memory 必须有 Write Policy、Provenance 和 Staleness；Working Context 应该怎样从多个信息源选择内容；以及为什么最终要分别评测 State 正确性与 Context 选择质量。

如果这些能够完整讲出来：

\[
\boxed{
第七课第7阶段真正掌握
}
\]

---

# 下一阶段：第七课 · 第 8 阶段
# RAG + Tools：什么时候检索知识，什么时候调用外部工具？
## Agent 已经有 State 和 Memory，但面对“查规则、查数据库、算分、读文件、生成报告”时，到底应该走哪条路径？

到第 7 阶段，我们已经拥有：

```text
Task State
Working Context
Short-term Memory
Long-term Memory
Artifact Store
External State
Checkpoint
```

下一阶段要解决的是：

> **不同信息需求到底应该交给 RAG，还是交给 Tool？**

例如：

```text
“这条资格条件是否有规则依据？”
→ RAG / Knowledge Retrieval

“这个项目预算金额是多少？”
→ Project Database Tool

“这份PDF里评分标准在哪一页？”
→ File Tool

“综合评分是多少？”
→ Calculator / Compute Tool

“生成报告草稿”
→ Report Tool / LLM
```

我们会正式建立：

```text
Knowledge Retrieval
Operational Tool
Database Query
File Access
Computation
Action Tool
Routing Policy
Freshness
Authority
Side Effect
```

并形成：

# `ProcurementRAGToolRoutingPolicy_V0.1`

核心目标是：

\[
\boxed{
不要把所有问题都当RAG问题
也不要把所有问题都变成Tool Call
}
\]

而是让 Agent 根据：

> **信息类型、权威来源、实时性、可执行性与副作用**

选择正确路径。



---
