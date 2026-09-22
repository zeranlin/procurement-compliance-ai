# 第七课 · 第 1 阶段
# Agent 到底是什么？从一次性生成到 Observe → Decide → Act
## 为什么 `ProcurementRAG_V0.1` 会回答问题，却还不等于一个真正能完成任务的 Agent？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，Agent 不是“更会聊天的 LLM”，而是 Model + State + Tools + Policy + Loop 组成的任务执行系统。**
2. **第二，普通 LLM 是 Prompt → Generate，RAG 通常是固定的 Retrieve → Generate Pipeline；Agent 的关键升级是模型可以根据 Observation 动态决定下一步 Action。**
3. **第三，真正的 Agent Action 必须由 Tool Runtime 实际执行；模型说“我执行了”不等于真实世界已经执行。**
4. **第四，Workflow 与 Agent 的核心区别不是步骤多少，而是谁决定下一步：Workflow 主要由预定义控制流决定，Agent 允许模型在受控范围内动态决策。**
5. **第五，Agent 必须维护 State、拥有 Stop Condition，并受 Policy 与 Human Approval 约束；自主程度越高不代表工程质量越高。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Decide` | Decide/决策：根据目标和状态选择下一步动作 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Observe` | Observe/观察：读取当前状态和工具结果 |
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

第六课结束时，我们已经得到：

\[
\boxed{
ProcurementRAG\_V0.1
}
\]

它已经能够：

```text
理解用户问题
↓
检索外部知识
↓
找到证据
↓
组织Context
↓
生成带Citation的回答
```

这已经比普通 LLM 强很多。

但假设用户提出一个更真实的任务：

> “请审查这份采购文件，找出资格条件中的潜在风险；如果发现疑似本地化限制，再检索适用规则；最后生成一份结构化审查报告，并把无法确定的问题标记给人工复核。”

这时系统不只需要：

> **回答一个问题。**

它还需要自己决定：

```text
先读什么
再查什么
要不要调用工具
工具返回以后下一步做什么
什么时候继续
什么时候停止
什么时候必须交给人
```

所以第七课开始，我们正式从：

# Answering System

走向：

# Acting System

也就是：

# Agent
## 智能体 / 任务执行系统

本阶段最终形成：

# `ProcurementAgentBoundaryModel_V0.1`

---

# 一、先锁死本阶段最重要的一句话

Agent 的本质不是：

> **“一个更聪明的聊天机器人。”**

更准确地说：

\[
\boxed{
Agent
=
Model
+
State
+
Tools
+
Policy
+
Loop
}
\]

其中：

- **Model**：判断下一步做什么；
- **State**：保存任务当前进度；
- **Tools**：对外部世界执行动作；
- **Policy**：限制什么能做、什么不能做；
- **Loop**：观察结果以后继续决策，直到任务结束。

所以：

\[
\boxed{
LLM
\neq
Agent
}
\]

LLM 是 Agent 里的一个决策组件。

---

# 二、普通 LLM 为什么还不是 Agent？

普通 LLM 的最小工作方式是：

\[
Prompt
\rightarrow
Generate
\rightarrow
Answer
\]

用户输入一次，

模型输出一次。

例如：

```text
User:
判断下面资格条件是否有风险。

LLM:
这项条件可能存在……
```

这属于：

# One-shot Generation
## 一次性生成

模型不会天然拥有：

```text
外部工具
真实任务状态
执行反馈
重试机制
停止条件
权限系统
```

它只是：

> **根据当前 Context 预测接下来该输出哪些 Token。**

所以即使语言非常像“在计划”，

也不等于它真的：

> 执行了计划。

---

# 三、RAG 为什么也还不等于 Agent？

第六课的 RAG 链是：

\[
Query
\rightarrow
Retrieve
\rightarrow
Context
\rightarrow
Generate
\]

它已经比普通 LLM 多了一步：

# Retrieval
## 外部知识检索

但它通常仍然是：

> **固定 Pipeline。**

例如：

```text
每次都：
Query Processing
→ Retrieval
→ Rerank
→ Context
→ LLM
```

真正决定流程的是：

> **工程师预先写好的程序。**

模型本身通常没有在运行时决定：

```text
这次需不需要检索？
是否需要先解析文件？
是否要先算金额？
检索失败后是不是换一种策略？
是否应该请求人工确认？
```

所以：

\[
\boxed{
RAG
可以成为Agent的一个Tool
但RAG本身不必然是Agent
}
\]

---

# 四、Workflow 和 Agent 到底差在哪里？

这是第七课必须先切清楚的边界。

## Workflow
### 工作流

流程主要由程序提前确定：

```text
Step 1
读取文件

Step 2
抽取资格条件

Step 3
检索法规

Step 4
生成报告
```

无论输入是什么，

大体都按这个顺序走。

可以写成：

\[
\boxed{
Workflow
=
PredefinedControlFlow
}
\]

---

## Agent
### 智能体

部分控制流由模型根据当前状态动态决定：

```text
先观察当前任务状态
↓
决定下一步
↓
执行动作
↓
读取结果
↓
重新决定
```

可以写成：

\[
\boxed{
Agent
=
DynamicDecisionInsideControlLoop
}
\]

最重要的区别不是：

> 有没有很多步骤。

而是：

> **下一步是谁决定的。**

---

# 五、Agent 的核心循环：Observe → Decide → Act

Agent 最小闭环可以写成：

\[
\boxed{
Observe
\rightarrow
Decide
\rightarrow
Act
}
\]

然后继续：

\[
Observe_{t}
\rightarrow
Decide_{t}
\rightarrow
Act_{t}
\rightarrow
Observe_{t+1}
\]

直到停止。

---

## Observe
### 观察

Agent 读取当前可见状态，例如：

```text
用户目标
当前任务进度
工具返回结果
检索证据
文件内容
错误信息
人工确认结果
```

---

## Decide
### 决策

模型判断：

```text
下一步要不要行动？
调用哪个Tool？
参数是什么？
是否需要换策略？
是否已经可以结束？
是否需要人工确认？
```

---

## Act
### 行动

真正执行：

```text
搜索
读取文件
调用数据库
运行计算
保存结果
请求审批
生成最终报告
```

关键点是：

> **Act 不是“模型说自己做了”。**

Act 必须由真实执行系统完成。

---

# 六、“我已经执行了”与“真的执行了”是两回事

这是 Agent 工程里极其重要的一条边界。

模型可能生成：

> “我已经查询了数据库，发现有 17 条记录。”

但如果系统实际上没有调用数据库：

> 这只是文本生成。

所以：

\[
\boxed{
ClaimedAction
\neq
ExecutedAction
}
\]

真实 Agent 必须形成：

\[
ModelDecision
\rightarrow
ToolExecution
\rightarrow
ToolResult
\]

而不是：

\[
ModelDecision
\rightarrow
ModelPretendsResult
\]

因此以后我们判断一个系统是不是 Agent，

不能只看：

> 它说话像不像 Agent。

而要看：

> **它是否真的拥有受控的行动通道。**

---

# 七、Environment：Agent 不是活在纯 Prompt 里

Agent 要完成真实任务，

一定存在一个：

# Environment
## 环境

环境可能包括：

```text
本地文件
知识库
数据库
API
搜索系统
计算器
审批系统
业务系统
用户
其他Agent
```

Agent 的动作会改变或查询 Environment。

例如：

```text
read_procurement_file
search_regulation
calculate_score
query_supplier_database
create_review_report
request_human_approval
```

所以更完整的闭环是：

\[
AgentState_t
+
Observation_t
\rightarrow
Decision_t
\rightarrow
Action_t
\rightarrow
Environment
\rightarrow
Observation_{t+1}
\]

这时 Agent 才真正从：

> 文本生成系统

变成：

> **和外部世界交互的任务系统。**

---

# 八、State：为什么 Agent 必须知道“自己做到哪一步了”？

假设采购文件审查需要：

```text
审查资格条件
审查技术参数
审查评分标准
审查履约要求
生成最终报告
```

如果系统每一步都忘记之前发生过什么，

就会：

```text
重复调用工具
重复分析
漏掉子任务
无法恢复失败
不知道是否已经完成
```

所以需要：

# State
## 状态

概念上：

\[
S_t
=
\{
Goal,
Progress,
Observations,
Artifacts,
PendingActions
\}
\]

例如：

```json
{
  "goal": "审查采购文件",
  "completed": [
    "qualification_review"
  ],
  "pending": [
    "scoring_review",
    "contract_review"
  ],
  "evidence_found": [
    "E1",
    "E2"
  ],
  "needs_review": false
}
```

Agent 不是只拥有聊天历史。

它还需要：

> **任务状态。**

---

# 九、Agent 不是“自由发挥越多越好”

一个常见误区是：

> Agent 越自主越高级。

不一定。

如果任务高度稳定：

```text
固定读取文件
固定字段抽取
固定规则校验
固定生成报告
```

那传统 Workflow 往往：

> 更稳定、更便宜、更容易审计。

只有当下一步确实依赖当前观察结果时，

动态 Agent 决策才真正有价值。

例如：

```text
如果发现文号
→ 精确检索文件

如果没有文号
→ 语义检索

如果证据冲突
→ 检索版本链

如果仍无法判断
→ 请求人工确认
```

所以：

\[
\boxed{
MoreAutonomy
\neq
BetterEngineering
}
\]

最好的系统经常是：

> **确定性 Workflow + 局部 Agent Decision。**

---

# 十、Agent 的自主程度其实是一条连续谱

不要把系统粗暴分成：

```text
不是Agent
vs
是Agent
```

更准确的是一条：

# Autonomy Spectrum
## 自主程度连续谱

例如：

```text
Level 0
纯LLM回答

Level 1
固定RAG Pipeline

Level 2
模型可以选择是否调用一个Tool

Level 3
模型可以在多个Tool之间选择

Level 4
模型可以做多步循环和重试

Level 5
模型可以拆任务、维护State、请求审批并恢复失败
```

并不是 Level 越高越好。

真正要问：

> **这个业务需要多大自主性？**

---

# 十一、Stopping Condition：Agent 最后必须知道什么时候停

如果没有停止规则，

Agent Loop 可能出现：

```text
继续搜索
↓
再搜索
↓
再调用工具
↓
再重新计划
↓
永远不结束
```

所以 Agent 必须有：

# Stop Condition
## 停止条件

例如：

```text
任务已经完成

达到最大步骤数

达到成本预算

找到足够证据

继续搜索没有新增信息

工具连续失败

必须等待人工确认
```

可以概念化为：

\[
Stop(S_t)=True
\]

一旦成立：

\[
Loop
\rightarrow
Terminate
\]

所以：

\[
\boxed{
Agent
不仅要会行动
还必须会停止
}
\]

---

# 十二、Human-in-the-loop：有些动作本来就不应该自动做

假设 Agent 发现：

> 某采购条件疑似存在重大合规风险。

它可以：

```text
检索
分析
整理证据
生成建议
```

但如果下一步是：

```text
正式修改采购文件
发布公告
发送正式函件
提交审批
```

这些动作可能需要：

# Human Approval
## 人工批准

所以 Agent Policy 必须能够定义：

```text
Read-only Action
可以自动执行

Low-risk Action
可以自动执行并记录

High-impact Action
必须先请求人工确认
```

因此：

\[
\boxed{
AgentAutonomy
必须受Policy约束
}
\]

这会在第 10 阶段正式展开安全设计。

---

# 十三、用一个政府采购任务看完整 Agent Loop

用户目标：

> “审查这份采购文件中的资格条件，并生成带依据的风险报告。”

Agent 第一次 Observe：

```text
Goal:
审查资格条件

Available:
采购文件
RAG
结构化抽取工具
报告生成工具
```

第一次 Decide：

> 先读取采购文件并抽取资格条件。

Act：

```text
read_file
+
extract_qualification_requirements
```

新的 Observation：

```text
发现：
1. 投标前须有本地办事处
2. 注册满3年
3. 某认证要求
```

第二次 Decide：

> 需要分别检索三类规则。

Act：

```text
search_regulation(local_presence)
search_regulation(operation_years)
search_regulation(certification)
```

新的 Observation：

```text
条件1：
找到强相关规则

条件2：
找到强相关规则

条件3：
证据不足
```

下一次 Decide：

```text
条件1、2
可以形成初步判断

条件3
需要needs_review
```

最后 Act：

```text
create_review_report
```

然后：

\[
Stop=True
\]

这才是：

> **真正的多步任务执行。**

---

# 十四、本阶段的错误分类：Agent 会在哪一层失败？

从第一阶段开始，我们就要建立 Agent Error Taxonomy。

至少有：

```text
1. Observation Error
没有正确理解Tool Result或当前状态

2. Decision Error
下一步选错了

3. Tool Selection Error
应该调用A，却调用了B

4. Argument Error
Tool选对，但参数错了

5. Execution Error
Tool本身执行失败

6. State Error
任务进度记录错了

7. Loop Error
重复、死循环、过早停止

8. Policy Error
执行了不该自动执行的动作

9. Completion Error
看起来结束了，但真实任务并没有完成
```

这张错误地图很重要。

以后最终结果错了，

不能只说：

> “Agent 推理能力不行。”

必须知道：

> **到底是哪一层出了问题。**

---

# 十五、本阶段工程产物：`ProcurementAgentBoundaryModel_V0.1`

第一版边界模型至少锁定：

```text
agent_goal

environment

available_tools

state_schema

observation_schema

decision_schema

action_schema

policy_boundary

approval_required_actions

stop_conditions

max_steps

failure_states

trace_required
=
true
```

并明确系统架构：

```text
LLM
负责：
Decision

Tool Runtime
负责：
Execution

State Store
负责：
Progress

Policy Layer
负责：
Permission

Evaluator
负责：
Completion Check
```

这就是第七课后面所有阶段共同使用的 Agent 最小骨架。

---

# 十六、把本阶段压成最精准的 6 句话

> **第一，Agent 不是“更会聊天的 LLM”，而是 `Model + State + Tools + Policy + Loop` 组成的任务执行系统。**

> **第二，普通 LLM 是 `Prompt → Generate`，RAG 通常是固定的 `Retrieve → Generate` Pipeline；Agent 的关键升级是模型可以根据 Observation 动态决定下一步 Action。**

> **第三，真正的 Agent Action 必须由 Tool Runtime 实际执行；模型说“我执行了”不等于真实世界已经执行。**

> **第四，Workflow 与 Agent 的核心区别不是步骤多少，而是谁决定下一步：Workflow 主要由预定义控制流决定，Agent 允许模型在受控范围内动态决策。**

> **第五，Agent 必须维护 State、拥有 Stop Condition，并受 Policy 与 Human Approval 约束；自主程度越高不代表工程质量越高。**

> **第六，Agent 的最终质量必须分别检查 Observation、Decision、Tool、Argument、Execution、State、Loop、Policy 和 Completion，而不能只看最终一句回答。**

---

# 本阶段最核心的一张图

```text
                         User Goal
                            │
                            ▼
                        Agent State
                            │
                            ▼
                         Observe
                            │
                            ▼
                          Decide
                            │
                     ┌──────┴──────┐
                     │             │
                     ▼             ▼
                   Action        Finish?
                     │             │
                     ▼             │
                 Tool Runtime      │
                     │             │
                     ▼             │
                 Environment       │
                     │             │
                     ▼             │
                New Observation    │
                     │             │
                     └──────┬──────┘
                            │
                            ▼
                        Update State
                            │
                            ▼
                    Continue / Stop
```

脑中最后只留一句：

> **Agent 的本质不是“会想很多步”，而是“能够在受控循环里观察真实结果、决定下一步、执行真实动作，并在任务真正完成时停止”。**

---

# 第七课 · 第 1 阶段掌握测试

现在不回看正文，你应该能够解释：为什么普通 LLM 不等于 Agent；为什么 RAG 也不必然等于 Agent；Workflow 与 Agent 的根本区别是什么；什么是 Observe、Decide、Act；为什么模型声称执行和真实 Tool Execution 必须分开；Environment 在 Agent 中是什么；为什么 Agent 需要独立的 Task State；为什么更多 Autonomy 不一定更好；什么是 Autonomy Spectrum；为什么 Stop Condition 是 Agent 必备组件；哪些动作需要 Human-in-the-loop；以及为什么 Agent Error 不能只归结为“模型推理错了”。

如果这些能够完整讲出来：

\[
\boxed{
第七课第1阶段真正掌握
}
\]

---

# 下一阶段：第七课 · 第 2 阶段
# Tool Calling：LLM 为什么可以“调用函数”？
## 模型明明只能生成 Token，为什么最后却能真的读文件、查数据库、调用 API？

下一阶段我们会正式拆开：

```text
Tool Definition
Function Schema
Tool Selection
Arguments
Tool Call
Tool Runtime
Tool Result
Tool Message
Second Model Turn
```

并回答第七课最关键的底层问题之一：

> **模型到底有没有“直接执行函数”？**

以及：

> **Function Calling 为什么本质上仍然是结构化 Token Generation + 外部 Runtime Execution？**

下一阶段会建立：

# `ProcurementToolCallingProtocol_V0.1`



---
