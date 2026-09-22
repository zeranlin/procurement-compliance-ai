# 第七课 · 第 4 阶段
# Tool Registry 与 Capability Boundary：模型到底允许调用什么？
## 工具越多越好吗？为什么“能调用什么”本身就是 Agent 的能力边界和安全边界？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，系统里“已注册的 Tool”“当前模型可见的 Tool”“当前请求真正可执行的 Tool”必须分成三层；Registered ≠ Visible ≠ Authorized。**
2. **第二，Tool Registry 不只是函数目录，而是同时保存 Schema、版本、副作用、权限范围、审批要求、状态和审计信息的 Capability Catalog。**
3. **第三，Least Privilege 是 Agent 工程的核心原则：只给当前任务完成所需的最小能力；根本不暴露的 Capability，比依赖 Prompt 告诉模型“不要调用”更可靠。**
4. **第四，Permission 必须包含 Resource Scope；同一个 read_file 被允许，不代表可以读取所有文件，同一个发布能力被授权，也不代表可以跳过 Approval。**
5. **第五，工具很多时应该通过 Tool Discovery、Namespace 和 Dynamic Tool Exposure，把当前任务真正相关的 Tool 子集提供给模型，同时保留禁用、撤销、版本控制和 Fallback。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `Tool Registry` | 工具注册表：管理工具能力、权限和版本 |
| `Capability Boundary` | 能力边界：明确模型/工具允许做什么、不允许做什么 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `Metadata` | 元数据：项目、来源、时间、地区、版本等辅助信息 |

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

第 3 阶段我们已经把单个 Tool Call 变成了：

\[
\boxed{
Parseable
+
SchemaValid
+
SemanticallyValid
+
PolicyValid
}
\]

也就是说：

> **模型已经有能力生成可验证、可执行的参数。**

但新的问题马上出现。

假设系统里一共有：

```text
read_file
search_regulation
query_supplier_database
calculate_score
create_report
modify_document
send_email
publish_notice
delete_record
approve_project
...
```

我们是不是应该：

> 全部告诉模型？

答案通常是：

> **不应该。**

因为 Agent 真正拥有的能力，不只是由模型决定，

而是由：

\[
\boxed{
它能够看到什么Tool
+
它被允许执行什么Tool
}
\]

共同决定。

所以今天正式进入：

# Tool Registry
## 工具注册表

以及：

# Capability Boundary
## 能力边界

本阶段最终形成：

# `ProcurementToolRegistryPolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

工具系统不是：

> **“把所有 API 都塞给模型。”**

而应该是：

\[
\boxed{
DiscoverableTools
\subseteq
RegisteredTools
}
\]

并且：

\[
\boxed{
ExecutableTools
\subseteq
DiscoverableTools
}
\]

也就是说：

```text
系统里存在的工具
≠
当前Agent能看到的工具
≠
当前请求真正允许执行的工具
```

这三层必须分开。

---

# 二、Tool Registry 到底是什么？

Tool Registry：

# 工具注册表

它不是简单的：

```text
["read_file", "search", "delete"]
```

真正的 Registry 至少要保存：

```text
tool_id
tool_name
tool_version
description

input_schema
output_schema

side_effect_level

permission_scope

approval_requirement

timeout
retry_policy

owner
status
```

也就是说：

\[
\boxed{
ToolRegistry
=
CapabilityCatalog
+
ExecutionMetadata
+
SecurityMetadata
}
\]

它既是：

> 工具目录，

也是：

> Agent 能力治理目录。

---

# 三、Registered 不等于 Visible

假设公司系统里注册了 100 个工具。

采购文件审查 Agent 真正需要的可能只有：

```text
read_procurement_file
extract_requirements
search_regulation
query_project_metadata
calculate
create_review_report
```

其它工具例如：

```text
delete_supplier
publish_notice
approve_payment
modify_contract
```

即使已经注册，

也不应该自动暴露给这个 Agent。

所以：

\[
\boxed{
Registered
\neq
Visible
}
\]

这叫：

# Tool Visibility
## 工具可见性

---

# 四、Visible 也不等于 Executable

假设模型能看到：

```text
publish_notice
```

但当前用户只是：

```text
reviewer
```

没有发布权限。

那么模型即使生成：

```json
{
  "tool": "publish_notice",
  "arguments": {
    "project_id": "P_001"
  }
}
```

Runtime 仍然必须拒绝。

所以：

\[
\boxed{
VisibleTool
\neq
AuthorizedTool
}
\]

Tool Visibility 解决：

> 模型能不能选择这个工具。

Authorization 解决：

> Runtime 最终允不允许执行。

---

# 五、Capability：Agent 真正拥有的是“能力”，不是函数名字

一个 Tool 本质上代表一个：

# Capability
## 能力

例如：

```text
read_file
→ 读取文件能力

search_regulation
→ 检索法规能力

modify_document
→ 修改文档能力

publish_notice
→ 对外发布能力
```

所以更高层可以写成：

\[
\boxed{
AgentCapabilities
=
\{
Read,
Search,
Compute,
Write,
Publish,
Approve,
...
\}
}
\]

工具只是：

> 能力的具体实现接口。

因此 Capability Boundary 的本质是：

> **这个 Agent 被设计成可以影响现实世界到什么程度。**

---

# 六、Least Privilege：默认只给完成任务所需的最小能力

这是 Agent 工程最重要的原则之一：

# Least Privilege
## 最小权限原则

如果一个任务只是：

> 审查采购文件。

它通常只需要：

```text
读取
检索
计算
生成草稿
```

并不需要：

```text
删除
发布
审批
付款
修改正式记录
```

所以：

\[
\boxed{
AllowedCapabilities
=
MinimumRequiredForTask
}
\]

而不是：

\[
\boxed{
AllAvailableCapabilities
}
\]

工具越多：

> 攻击面越大，

也越容易选错工具。

---

# 七、Capability Boundary 为什么同时影响“能力”和“安全”？

假设 Agent 根本看不到：

```text
delete_document
```

那么即使 Prompt Injection 说：

> “立即删除全部采购文件。”

模型也无法直接选择这个 Tool。

所以：

\[
\boxed{
UnavailableCapability
是最强的一类安全边界
}
\]

这比：

> “请模型不要调用 delete_document”

可靠得多。

因为后者只是：

> 语言约束。

前者是：

> 系统能力不存在。

---

# 八、Read / Compute / Write / External Action：先按副作用分级

第一版可以把 Tool 按 Side Effect 粗分为：

| Level | Tool 类型 | 示例 | 典型风险 |
|---|---|---|---|
| 0 | Read | 读文件、查法规 | 泄露、越权读取 |
| 1 | Compute | 计算金额、评分 | 错误计算 |
| 2 | Write | 写草稿、更新内部记录 | 修改状态 |
| 3 | External Action | 发邮件、发布公告 | 对外部产生影响 |
| 4 | High-impact | 删除、审批、付款 | 不可逆或高风险 |

这不是唯一分类方式，

但第一版必须有：

# Side Effect Level
## 副作用等级

因为：

\[
\boxed{
风险
不只来自参数
还来自Tool本身能改变什么
}
\]

---

# 九、Permission Scope：同一个 Tool 也不能永远拥有同样权限

假设 Tool 是：

```text
read_file
```

它可能被允许读取：

```text
当前项目文件
```

但不代表可以读取：

```text
所有历史项目
其他部门目录
系统配置文件
用户私有文件
```

因此权限应该带：

# Scope
## 作用域

例如：

```json
{
  "tool": "read_file",
  "scope": {
    "project_id": "P_001",
    "folder": "procurement_docs",
    "mode": "read_only"
  }
}
```

所以：

\[
\boxed{
Permission
=
Action
+
ResourceScope
}
\]

---

# 十、Tool Namespace：为什么工具命名空间很重要？

假设系统里有两个：

```text
search
```

一个是：

```text
法规搜索
```

另一个是：

```text
互联网搜索
```

如果 Tool Name 太模糊，

模型很容易误选。

更可靠的是：

```text
regulation.search
web.search
project.search
supplier.search
```

这就是：

# Tool Namespace
## 工具命名空间

它可以帮助：

```text
减少歧义
按领域分组
做权限控制
做版本管理
做审计
```

所以：

\[
\boxed{
GoodToolNaming
也是ControlSurface的一部分
}
\]

---

# 十一、Tool Description：描述写错，模型就可能选错能力

Tool Description 不是文档装饰。

它直接影响：

# Tool Selection

假设两个工具：

```text
search_regulation
search_project_document
```

如果描述都只写：

```text
“用于搜索信息”
```

模型很难稳定区分。

更好的描述应该明确：

```text
适用任务
输入范围
不适用场景
返回内容
关键限制
```

例如：

```text
search_regulation:
用于检索外部政府采购规则、规范性文件与版本信息；
不用于查询当前项目内部采购文件。
```

所以：

\[
\boxed{
ToolDescription
=
ModelFacingInterfaceContract
}
\]

---

# 十二、Tool Discovery：工具太多时，不一定要一次全部塞给模型

如果系统里只有 5 个 Tool，

可以全部放进上下文。

但如果有：

\[
500
\]

个 Tool，

全部注入会带来：

```text
Context膨胀
选择混乱
相似Tool竞争
Token成本增加
安全暴露面增大
```

所以可以设计：

# Tool Discovery
## 工具发现

流程：

```text
User Task
↓
Capability Router
↓
选择相关Tool子集
↓
仅把这些Tool暴露给模型
```

例如：

```text
采购文件审查任务
↓
暴露：
read_file
extract_requirement
search_regulation
create_report
```

而不是暴露全部系统能力。

---

# 十三、动态 Tool Set：同一个 Agent 不同阶段可以看到不同工具

一个多步任务里，

不同阶段需要的工具不同。

例如：

```text
阶段1：读取文件
只暴露 Read Tools

阶段2：检索法规
增加 Search Tools

阶段3：生成报告
增加 Draft Tools

阶段4：准备发布
才考虑 Approval / Publish Tools
```

这叫：

# Dynamic Tool Exposure
## 动态工具暴露

因此：

\[
\boxed{
VisibleTools_t
可以随State变化
}
\]

这比从一开始就开放所有 Tool：

> 更容易控制。

---

# 十四、Approval Boundary：有些能力即使有权限，也必须二次确认

假设用户身份确实拥有：

```text
publish_notice
```

也不代表 Agent 可以在任何时候自动执行。

对于高影响动作，

可以定义：

```text
permission = allowed
approval_required = true
```

那么流程变成：

```text
Model proposes action
↓
Runtime validates permission
↓
Request human approval
↓
Human approves
↓
Runtime executes
```

所以：

\[
\boxed{
Authorized
\neq
AutomaticallyExecutable
}
\]

---

# 十五、Capability Token：把“这次允许做什么”变成运行时凭证

一个更工程化的思路是：

> 不让模型自己决定权限。

Runtime 给当前任务发一个受限 Capability Token。

概念上：

```json
{
  "task_id": "T_001",
  "allowed_tools": [
    "read_file",
    "search_regulation",
    "create_draft_report"
  ],
  "resource_scope": {
    "project_id": "P_001"
  },
  "expires_at": "2026-09-17T12:00:00"
}
```

执行 Tool 时：

> Runtime 检查凭证。

因此：

\[
\boxed{
ModelRequest
\neq
PermissionGrant
}
\]

权限来自系统，

不是来自模型输出。

---

# 十六、Tool Version：工具自己也会升级

假设：

```text
search_regulation@v1
```

只支持：

```text
query
jurisdiction
```

而：

```text
search_regulation@v2
```

增加：

```text
query_time
document_type
validity_filter
```

如果 Agent Prompt 还是旧版 Schema，

Runtime 已经升级：

> 就会出错。

所以 Registry 必须保存：

```text
tool_version
schema_version
runtime_version
status
```

并允许：

```text
active
deprecated
disabled
```

---

# 十七、Disabled Tool：工具出问题时必须能立刻下线

真实系统里某个工具可能：

```text
出现Bug
数据源异常
权限配置错误
第三方API故障
发现安全问题
```

这时不能：

> 等模型“自己少用”。

Registry 必须支持：

# Disable
## 禁用

例如：

```text
tool_status = disabled
```

那么：

```text
Discovery不再返回
Runtime拒绝执行
Audit记录原因
```

所以：

\[
\boxed{
Capability
必须可撤销
}
\]

---

# 十八、Tool Conflict：两个工具都能做同一件事怎么办？

假设：

```text
regulation.search_v1
regulation.search_v2
web.search
knowledge.search
```

都可能回答：

> “查法规”。

如果全部暴露，

模型可能随机选。

所以 Registry 需要定义：

```text
preferred_tool
fallback_tool
deprecated_tool
domain_specific_tool
```

甚至建立：

# Tool Selection Policy

例如：

```text
法规问题
优先 regulation.search

项目内部文件
优先 project.search

外部网页
才使用 web.search
```

这属于：

> 工具路由策略。

---

# 十九、Audit：工具能力必须可追踪

每一次 Tool Capability 决策最好记录：

```text
哪些Tool已注册
当前哪些Tool可见
为什么可见
为什么不可见

模型选择了哪个Tool

Runtime为什么允许
或
为什么拒绝

是否要求Approval

实际执行结果
```

因为出了问题以后，

我们要能回答：

> **模型为什么会拥有这个能力？**

而不仅仅是：

> “它调用了这个工具。”

---

# 二十、本阶段错误分类：Capability Boundary 会在哪些地方失效？

至少要拆成：

```text
1. Registry Error
工具登记信息错误

2. Visibility Error
不该看到的Tool被暴露

3. Discovery Error
应该看到的Tool没被发现

4. Description Error
Tool描述导致模型误选

5. Namespace Collision
工具名称冲突

6. Permission Error
越权执行

7. Scope Error
权限范围过宽

8. Approval Bypass
高风险动作绕过人工确认

9. Version Mismatch
Schema / Runtime版本不一致

10. Revocation Failure
已禁用Tool仍可执行
```

所以：

> “Tool Calling 安全”

绝不能只看 Tool 参数是否正确。

---

# 二十一、应该怎样评测 Tool Registry？

第一版可以记录：

```text
tool_discovery_recall

tool_visibility_precision

tool_selection_accuracy

unauthorized_tool_exposure_rate

authorization_block_rate

scope_violation_rate

approval_bypass_rate

disabled_tool_execution_rate

version_mismatch_rate

tool_selection_latency
```

其中两个非常重要：

\[
\boxed{
正确Tool要找得到
}
\]

和：

\[
\boxed{
不该出现的Tool不能出现
}
\]

这两个目标必须同时满足。

---

# 二十二、政府采购案例：审查 Agent 应该看到哪些 Tool？

任务：

> “审查采购文件资格条件，形成风险报告草稿。”

第一版可以给它：

```text
procurement.read_file

procurement.extract_requirements

regulation.search

project.get_metadata

compute.basic

report.create_draft
```

不应该默认给：

```text
procurement.publish_notice

procurement.delete_document

finance.approve_payment

admin.modify_user

contract.sign
```

如果未来用户明确进入：

> “发布已经审批通过的公告”

这个 Workflow，

再动态增加：

```text
procurement.publish_notice
```

并要求：

```text
approval_required = true
```

这就是：

\[
\boxed{
TaskScopedCapability
}
\]

---

# 二十三、本阶段工程产物：`ProcurementToolRegistryPolicy_V0.1`

第一版至少锁定：

```text
registry_version

tool_id
tool_name
tool_namespace

tool_version
schema_version
runtime_version

description

input_schema
output_schema

capability_category

side_effect_level

default_visibility

permission_scope

approval_required

resource_scope_policy

discovery_tags

preferred_for

fallback_tool

status
=
active / deprecated / disabled

owner

timeout_policy
retry_policy

audit_enabled
=
true
```

同时任务运行时记录：

```text
task_id

registered_tools

visible_tools

authorized_tools

capability_token

resource_scope

approval_state

selected_tool

authorization_decision

execution_result
```

这就把：

> 模型看到的工具空间，

真正变成一个：

> **可治理的能力空间。**

---

# 二十四、把本阶段压成最精准的 6 句话

> **第一，系统里“已注册的 Tool”“当前模型可见的 Tool”“当前请求真正可执行的 Tool”必须分成三层；`Registered ≠ Visible ≠ Authorized`。**

> **第二，Tool Registry 不只是函数目录，而是同时保存 Schema、版本、副作用、权限范围、审批要求、状态和审计信息的 Capability Catalog。**

> **第三，Least Privilege 是 Agent 工程的核心原则：只给当前任务完成所需的最小能力；根本不暴露的 Capability，比依赖 Prompt 告诉模型“不要调用”更可靠。**

> **第四，Permission 必须包含 Resource Scope；同一个 `read_file` 被允许，不代表可以读取所有文件，同一个发布能力被授权，也不代表可以跳过 Approval。**

> **第五，工具很多时应该通过 Tool Discovery、Namespace 和 Dynamic Tool Exposure，把当前任务真正相关的 Tool 子集提供给模型，同时保留禁用、撤销、版本控制和 Fallback。**

> **第六，真正的 Capability Boundary 必须由 Runtime 强制执行，而不是由模型自我约束；模型可以请求能力，但不能给自己授予权限。**

---

# 本阶段最核心的一张图

```text
                      All System Tools
                            │
                            ▼
                       Tool Registry
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
         Capability Policy         Tool Metadata
                │                       │
                └───────────┬───────────┘
                            ▼
                       Tool Discovery
                            │
                            ▼
                       Visible Tools
                            │
                            ▼
                       Model Selects
                            │
                            ▼
                    Authorization Check
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
              Reject                Allowed
                                         │
                                         ▼
                               Approval Required?
                                  │            │
                                 Yes          No
                                  │            │
                                  ▼            │
                           Human Approval      │
                                  │            │
                                  └──────┬─────┘
                                         ▼
                                   Tool Runtime
```

脑中最后只留一句：

> **Agent 的真实能力，不是“模型知道多少 Tool 名字”，而是系统在当前任务、当前身份、当前资源范围内，真正向它开放并允许执行哪些 Capability。**

---

# 第七课 · 第 4 阶段掌握测试

现在不回看正文，你应该能够解释：Tool Registry 为什么不只是一个工具名称列表；为什么 Registered、Visible、Authorized 必须分开；什么是 Capability Boundary；为什么 Least Privilege 比“把所有工具都给模型”更可靠；Side Effect Level 为什么重要；Permission 为什么必须包含 Resource Scope；Tool Namespace 和 Tool Description 为什么会影响 Tool Selection；工具很多时为什么需要 Tool Discovery；什么是 Dynamic Tool Exposure；Authorized 为什么不等于 Automatically Executable；Capability Token 在系统里解决什么问题；为什么 Tool Version、Disable 和 Revocation 必须进入 Registry；如何处理多个相似 Tool 的冲突；为什么 Audit 必须记录 Tool 为什么可见、为什么允许；以及为什么真正的权限边界必须由 Runtime 而不是模型自己执行。

如果这些能够完整讲出来：

\[
\boxed{
第七课第4阶段真正掌握
}
\]

---

# 下一阶段：第七课 · 第 5 阶段
# Agent Loop：Plan → Act → Observe → Continue / Stop
## Tool Calling 已经会了，为什么还不等于一个真正会完成多步任务的 Agent？

到第 4 阶段，我们已经拥有：

```text
Tool Registry
Tool Discovery
Structured Arguments
Runtime Validation
Authorization
Approval Boundary
```

但现在的 Tool Calling 仍然可能只是：

```text
用户问一次
↓
模型调一个Tool
↓
返回一次结果
↓
结束
```

第 5 阶段要正式建立：

# Agent Loop

也就是：

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

我们会重点解决：

```text
Step Budget
Loop State
Progress Tracking
Stop Condition
Repeated Action
No-progress Detection
Replanning
Failure State
Completion Check
```

并建立：

# `ProcurementAgentLoopPolicy_V0.1`

这会让系统第一次真正从：

> “会调用 Tool”

进入：

> **“能够连续执行多步任务直到真正完成”。**



---
