# 第七课 · 第 8 阶段
# RAG + Tools：什么时候检索知识，什么时候调用外部工具？
## Agent 已经有 State 和 Memory，但面对“查规则、查项目、读文件、算金额、写报告、执行动作”时，到底应该走哪条路径？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，RAG + Tools Routing 的核心不是“选择一个最方便的工具”，而是先确定这个问题真正的 Source of Truth 在哪里。**
2. **第二，规则依据优先走 RAG，实时结构化业务事实优先走权威数据库，具体文件内容走 File Tool，确定性计算走 Compute Tool，改变现实状态的请求才进入 Action Tool。**
3. **第三，Routing 至少要同时考虑 Information Type、Authority、Freshness、Determinism 和 Side Effect；同一个用户问题完全可能需要多个 Source 联合完成。**
4. **第四，Vector Search 不能替代业务数据库，Memory 不能替代更权威的实时系统，LLM 参数知识也不能替代当前有效规则或实时项目状态。**
5. **第五，多 Source 结果进入 Working Context 前必须保留 Provenance、Version、Time 和 Authority；如果来源冲突，必须显式解决或标记 needs_review，不能让模型静默选边。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Memory` | 任务记忆：保存跨步骤需要复用的结构化信息 |
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `State` | 状态：保存任务进度、事实和待办 |
| `Routing` | 路由：决定当前任务交给哪个工具/模块 |
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

到第 7 阶段，我们已经建立：

\[
\boxed{
TaskState
+
WorkingContext
+
Memory
+
ArtifactStore
+
Checkpoint
}
\]

也就是说，Agent 现在已经能够：

> **记住任务进行到了哪里，并把当前最需要的信息送回模型。**

但接下来会碰到一个非常现实的问题：

用户问：

```text
“这个资格条件有没有法规风险？”
```

我们应该去：

```text
知识库检索？
项目数据库？
当前采购文件？
计算器？
互联网？
内部业务系统？
```

再比如用户问：

```text
“这个项目预算金额是多少？”
```

如果 Agent 去 RAG 知识库里找：

> 很可能就错了。

因为这个问题真正的 Source of Truth 可能是：

> **项目业务数据库。**

所以本阶段正式解决：

# RAG + Tools Routing
## 知识检索与工具调用路由

本阶段最终形成：

# `ProcurementRAGToolRoutingPolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

Agent 不应该先问：

> **“我现在能调用什么工具？”**

而应该先问：

\[
\boxed{
这个问题的真实答案
应该来自哪里？
}
\]

也就是：

# Source of Truth
## 事实真源

然后再决定：

```text
RAG
Database Tool
File Tool
Compute Tool
Action Tool
Memory
或
直接由模型回答
```

所以：

\[
\boxed{
Routing
首先是Source-of-Truth问题
其次才是Tool选择问题
}
\]

---

# 二、RAG 适合解决什么问题？

RAG 最适合：

> **从外部知识集合中找依据。**

例如：

```text
法规条文
政策文件
采购规则
历史制度文件
业务指南
标准解释材料
项目采购文件中的相关条款
```

它的典型流程是：

\[
Query
\rightarrow
Retrieve
\rightarrow
Evidence
\rightarrow
Generate
\]

所以 RAG 擅长的问题是：

```text
“依据是什么？”
“哪个文件提到了这件事？”
“当前规则怎样规定？”
“这段条款与什么规则相关？”
```

核心是：

\[
\boxed{
KnowledgeQuestion
\rightarrow
KnowledgeRetrieval
}
\]

---

# 三、Database Tool 适合解决什么问题？

数据库工具适合：

> **读取业务系统中的当前结构化事实。**

例如：

```text
项目预算
项目编号
采购方式
当前审批状态
供应商数量
项目负责人
合同金额
履约状态
```

这些信息可能：

> 每小时都在变化。

所以如果用户问：

```text
“P_001项目现在预算多少？”
```

真正应该查询：

```text
project_database.get_budget
```

而不是依赖：

```text
旧文档
模型记忆
历史RAG Chunk
```

因此：

\[
\boxed{
OperationalFact
\rightarrow
AuthoritativeOperationalSystem
}
\]

---

# 四、File Tool 适合解决什么问题？

如果问题针对的是：

> **一个具体文件本身。**

例如：

```text
“这份PDF第几页有评分标准？”
“把这份采购文件的资格条件抽出来。”
“比较原版和更正版的差异。”
```

最合适的通常是：

# File Tool
## 文件工具

例如：

```text
read_file
parse_pdf
extract_section
compare_versions
```

这里的 Source of Truth 是：

> 当前这份具体文件。

不是通用知识库。

所以：

\[
\boxed{
ArtifactSpecificQuestion
\rightarrow
ArtifactTool
}
\]

---

# 五、Compute Tool 适合解决什么问题？

如果答案应该由：

> **确定性计算**

得到，

就不应该让 LLM 靠语言推理“估算”。

例如：

```text
金额合计
税率计算
比例
评分加总
时间间隔
阈值判断
排序
去重
```

这类问题更适合：

# Compute Tool
## 计算工具

例如：

```text
calculator
date_diff
score_aggregate
threshold_check
```

因为：

\[
\boxed{
DeterministicCalculation
\rightarrow
DeterministicTool
}
\]

而不是：

\[
\boxed{
DeterministicCalculation
\rightarrow
FreeFormGeneration
}
\]

---

# 六、Action Tool 适合解决什么问题？

Action Tool 不只是“查”。

它会：

> **改变外部系统状态。**

例如：

```text
create_draft
update_record
send_message
submit_for_approval
publish_notice
```

这里的问题已经从：

> “答案是什么？”

变成：

> **“要不要执行一个动作？”**

所以 Action Tool 必须同时经过：

```text
Intent Check
Authorization
Resource Scope
Approval
Idempotency
Audit
```

因此：

\[
\boxed{
ActionRequest
\neq
KnowledgeQuery
}
\]

不能把两类事情混在一个 RAG 流程里。

---

# 七、Memory 什么时候可以用，什么时候不能当真源？

Memory 可以帮助 Agent 记住：

```text
用户已经确认的任务偏好
当前项目的临时上下文
前面已经完成的步骤
已确认的项目参数
```

但 Memory 不是天然的权威真源。

例如 Memory 里记着：

```text
项目预算 = 500万元
```

但如果预算可能发生变化，

当前业务数据库才是：

> 更高权威、更高新鲜度的 Source of Truth。

所以：

\[
\boxed{
Memory
适合减少重复询问
不适合替代更权威的实时系统
}
\]

---

# 八、模型参数本身什么时候可以直接回答？

如果问题是：

```text
“什么是RAG？”
“JSON Schema是干什么的？”
“Agent Loop是什么意思？”
```

这类：

> 稳定、通用、非高风险概念

可以直接由模型回答。

但如果问题涉及：

```text
当前项目状态
当前有效规则
实时金额
具体文件内容
正式业务动作
```

就应该优先使用外部 Source of Truth。

因此：

\[
\boxed{
ParametricKnowledge
适合稳定概念
}
\]

\[
\boxed{
ExternalSource
适合动态事实与可核验证据
}
\]

---

# 九、Routing 的第一个维度：Information Type

可以先把用户需求分成几类：

| 信息类型 | 典型问题 | 首选路径 |
|---|---|---|
| 通用概念 | 什么是 RAG？ | 模型参数知识 |
| 规则知识 | 当前规则怎样规定？ | RAG |
| 项目事实 | 项目预算是多少？ | Database Tool |
| 文件内容 | 这份 PDF 有什么要求？ | File Tool |
| 确定性计算 | 总分是多少？ | Compute Tool |
| 外部动作 | 发布公告 | Action Tool |
| 历史任务上下文 | 前面已经审到哪一步？ | Task State / Memory |

这张表非常重要。

因为：

\[
\boxed{
不同问题类型
应该路由到不同真源
}
\]

---

# 十、Routing 的第二个维度：Authority

如果多个 Source 都能回答，

优先级不应该按：

> 哪个最快。

而应该先看：

# Authority
## 权威性

例如：

```text
项目预算：

项目数据库
>
旧采购文件
>
Memory
>
模型猜测
```

再比如：

```text
当前有效规则：

经过版本管理的法规知识库
>
历史报告
>
普通网页摘要
>
模型参数记忆
```

所以：

\[
\boxed{
SourcePriority
首先看Authority
}
\]

---

# 十一、Routing 的第三个维度：Freshness

有些信息变化慢：

```text
概念定义
算法原理
稳定业务术语
```

有些变化快：

```text
项目状态
预算
审批进度
当前版本
供应商信息
接口状态
```

所以需要：

# Freshness
## 新鲜度

可以概念化为：

\[
RequiredFreshness
\le
SourceFreshness
\]

如果用户问：

> “现在项目审批到哪一步了？”

就不能用：

> 三天前同步进 RAG 的静态文档。

---

# 十二、Routing 的第四个维度：Determinism

有些任务有明确确定结果：

```text
7 + 13
日期差
金额求和
评分计算
```

如果让 LLM 自由生成，

哪怕准确率很高：

> 也没有必要承担随机性。

所以：

\[
\boxed{
HighDeterminismTask
优先使用ComputeTool
}
\]

模型更适合做：

```text
解释结果
判断下一步
组织表达
```

而不是替代计算器。

---

# 十三、Routing 的第五个维度：Side Effect

只读路径：

```text
RAG
Read Database
Read File
Compute
```

通常不会改变业务状态。

但：

```text
Write
Submit
Publish
Delete
Approve
```

会产生副作用。

所以 Side Effect 一旦升高，

Routing Policy 就必须提高控制强度：

\[
\boxed{
HigherSideEffect
\Rightarrow
StrongerAuthorization
+
Approval
+
Audit
}
\]

这不是模型能力问题，

是系统治理问题。

---

# 十四、不要把 RAG 误当成万能数据访问层

一个常见错误是：

> “反正我们已经有向量数据库了，什么都搜进去。”

于是：

```text
项目预算
供应商实时状态
当前审批节点
业务流水
```

全部定期做 Chunk + Embedding。

这样做的问题是：

```text
同步延迟
版本不一致
字段精度丢失
结构化查询变模糊
实时状态容易过期
```

所以：

\[
\boxed{
VectorSearch
不是DatabaseQuery的替代品
}
\]

结构化业务事实：

> 优先从结构化权威系统读取。

---

# 十五、也不要把每个问题都变成 Tool Call

另一个极端是：

> 什么都 Tool。

例如：

```text
“什么是资格条件？”
```

如果每次都：

```text
search
database
file
```

反而增加：

```text
延迟
成本
失败点
不必要依赖
```

所以：

\[
\boxed{
ExternalCall
必须有必要性
}
\]

稳定常识可以直接回答。

动态事实、高风险依据、实时状态才更需要外部调用。

---

# 十六、Hybrid Route：真实任务经常需要多条路径组合

用户问：

> “这个项目要求供应商投标前在本市设立机构，有没有风险？”

这其实至少需要两个 Source：

```text
项目文件
→ File Tool

适用规则
→ RAG
```

如果还要确认项目所在辖区：

```text
项目Metadata
→ Database Tool
```

完整路径可能是：

```text
File Tool
↓
提取资格条件

Database Tool
↓
获取项目辖区 / 项目时间

RAG
↓
检索适用规则

LLM
↓
基于证据形成判断
```

所以：

\[
\boxed{
OneUserQuestion
可能需要
MultiSourceRoute
}
\]

---

# 十七、Source Fusion：多个 Source 返回结果以后，不能简单混在一起

假设：

```text
RAG说：
某规则当前有效

数据库说：
项目时间是2024年

文件说：
资格条件要求投标前本地机构
```

这些信息角色不同。

应该保留：

```text
source_type
source_id
source_version
retrieved_at
authority
validity
```

再统一送进 Working Context。

所以：

\[
\boxed{
MultiSource
必须保留Provenance
}
\]

而不是把所有结果拼成一段无来源文本。

---

# 十八、Routing Policy：哪些判断应该写死，哪些可以交给模型？

不是所有 Routing 都应该让 LLM 自由决定。

有些规则可以 Hard-code：

```text
如果是精确算术
→ calculator

如果请求修改外部系统
→ action tool + authorization

如果请求读取上传文件
→ file tool

如果请求当前项目实时状态
→ operational database
```

模型更适合处理：

```text
模糊意图识别
多Source组合
是否还需要补充检索
下一步路径选择
```

因此：

\[
\boxed{
Routing
=
DeterministicRules
+
ModelDecision
}
\]

这通常比：

> 全部交给模型

更稳定。

---

# 十九、Fallback：首选 Source 不可用怎么办？

假设：

```text
project_database
```

暂时不可用。

系统不应该偷偷切到：

> 模型猜测。

应该显式进入 Fallback Policy。

例如：

```text
Primary:
project_database

Fallback:
latest_project_document

If still unavailable:
needs_review / ask_user
```

所以：

\[
\boxed{
Fallback
必须显式定义可信度下降
}
\]

如果 Source 变弱：

> 结论确定性也应该下降。

---

# 二十、Conflict：多个 Source 冲突怎么办？

例如：

```text
项目数据库：
预算 = 500万

采购文件：
预算 = 480万
```

Agent 不应该：

> 随便选一个。

而应该检查：

```text
哪个Source更权威？
时间戳谁更新？
文件是不是旧版本？
数据库是不是当前正式值？
```

如果仍无法解决：

```text
conflict = true
needs_review = true
```

所以：

\[
\boxed{
SourceConflict
不能被LLM静默消解
}
\]

---

# 二十一、RAG Result 和 Tool Result 都只是 Observation

第 2 阶段我们讲过：

\[
ToolResult
=
Observation
\]

现在要扩展为：

\[
\boxed{
RAGResult
+
DatabaseResult
+
FileResult
+
ComputeResult
=
Observations
}
\]

它们都必须：

```text
带来源
带版本
带时间
经过校验
再进入State / Working Context
```

所以 Agent 不应该因为：

> “这是工具返回的”

就自动相信。

---

# 二十二、政府采购案例：完整路由

用户：

> “请判断这份采购文件里要求供应商投标前已经在本市设立三年以上分支机构是否有风险，并给出依据；如果有风险，生成修改建议草稿。”

Routing：

```text
Step 1
File Tool
读取当前采购文件

Step 2
Extract Tool
提取资格条件

Step 3
Project Database
获取项目辖区、采购阶段、当前时间点

Step 4
RAG
检索当前适用规则与相关证据

Step 5
LLM
进行证据约束判断

Step 6
Report / Draft Tool
生成修改建议草稿
```

如果用户进一步说：

> “直接替我发布更正公告。”

则 Route 发生变化：

```text
Action Tool
+
Authorization
+
Human Approval
```

这说明：

\[
\boxed{
同一个任务
不同阶段
路由可以完全不同
}
\]

---

# 二十三、本阶段错误分类：Routing 会在哪些地方失败？

至少要区分：

```text
1. Wrong Source Error
选择了错误真源

2. Stale Source Error
使用过期来源

3. Authority Error
低权威来源覆盖高权威来源

4. Unnecessary Tool Call
本可直接回答却调用工具

5. Missing Tool Call
需要外部真源却直接生成

6. Wrong Tool Type
该算却检索，该查库却RAG

7. Side-effect Misroute
读请求误路由到写工具

8. Source Conflict Suppression
冲突被静默忽略

9. Fallback Degradation Hidden
降级后没有暴露可信度下降

10. Provenance Loss
结果进入Context后丢失来源
```

这张错误地图非常重要。

---

# 二十四、应该怎样评测 RAG + Tool Routing？

第一版至少记录：

```text
route_accuracy

source_of_truth_accuracy

rag_route_precision
rag_route_recall

database_route_accuracy

file_tool_route_accuracy

compute_tool_route_accuracy

action_tool_route_accuracy

unnecessary_external_call_rate

missing_external_call_rate

stale_source_usage_rate

authority_violation_rate

source_conflict_detection_rate

fallback_correctness

provenance_coverage

end_to_end_task_success
```

其中最核心的不是：

> Tool Selection Accuracy。

而是：

\[
\boxed{
SourceOfTruthAccuracy
}
\]

因为 Tool 选对名字，

但如果真源选错：

> 整个答案仍然可能错。

---

# 二十五、本阶段工程产物：`ProcurementRAGToolRoutingPolicy_V0.1`

第一版至少锁定：

```text
routing_policy_version

information_type_schema

source_of_truth_map

authority_priority

freshness_requirement

deterministic_task_rules

side_effect_routing_rules

rag_route_policy

database_route_policy

file_route_policy

compute_route_policy

action_route_policy

memory_usage_policy

parametric_answer_policy

multi_source_route_policy

source_fusion_policy

conflict_policy

fallback_policy

provenance_required
=
true

trace_logging
=
enabled
```

每次路由至少记录：

```text
request_id

detected_information_type

candidate_sources

selected_sources

routing_reason

authority_level

freshness_requirement

tool_calls

rag_queries

fallback_used

conflict_detected

provenance_map

final_task_result
```

这样我们以后才能回答：

> **为什么这个问题走了 RAG，而不是数据库？为什么调用了这个 Tool？如果错了，到底是路由错、数据错，还是模型判断错？**

---

# 二十六、把本阶段压成最精准的 6 句话

> **第一，RAG + Tools Routing 的核心不是“选择一个最方便的工具”，而是先确定这个问题真正的 Source of Truth 在哪里。**

> **第二，规则依据优先走 RAG，实时结构化业务事实优先走权威数据库，具体文件内容走 File Tool，确定性计算走 Compute Tool，改变现实状态的请求才进入 Action Tool。**

> **第三，Routing 至少要同时考虑 Information Type、Authority、Freshness、Determinism 和 Side Effect；同一个用户问题完全可能需要多个 Source 联合完成。**

> **第四，Vector Search 不能替代业务数据库，Memory 不能替代更权威的实时系统，LLM 参数知识也不能替代当前有效规则或实时项目状态。**

> **第五，多 Source 结果进入 Working Context 前必须保留 Provenance、Version、Time 和 Authority；如果来源冲突，必须显式解决或标记 `needs_review`，不能让模型静默选边。**

> **第六，真正可靠的 Routing 应该是“确定性硬规则 + 模型动态决策”的组合，并通过 Source-of-Truth Accuracy、Staleness、Conflict Handling 和最终 Task Success 来评测。**

---

# 本阶段最核心的一张图

```text
                         User Request
                              │
                              ▼
                    Information Type
                              │
                              ▼
                    Source-of-Truth Map
                              │
             ┌────────────────┼─────────────────┐
             ▼                ▼                 ▼
          Knowledge        Operational       Artifact
             │                │                 │
             ▼                ▼                 ▼
            RAG          Database Tool       File Tool
             │                │                 │
             └────────┬───────┴─────────┬──────┘
                      │                 │
                      ▼                 ▼
                  Compute?          Action?
                      │                 │
                      ▼                 ▼
                Compute Tool      Action Tool
                                         │
                                         ▼
                                  Auth / Approval
                      │                 │
                      └────────┬────────┘
                               ▼
                         Observations
                               │
                               ▼
                    Provenance / Conflict
                               │
                               ▼
                       Working Context
                               │
                               ▼
                              LLM
```

脑中最后只留一句：

> **Agent 不应该“有什么 Tool 就用什么 Tool”，而应该先找到事实真源，再根据权威性、实时性、确定性与副作用选择最合适的 RAG、数据库、文件、计算或行动路径。**

---

# 第七课 · 第 8 阶段掌握测试

现在不回看正文，你应该能够解释：为什么 Routing 首先是 Source-of-Truth 问题；RAG、Database Tool、File Tool、Compute Tool、Action Tool 分别适合什么；Memory 为什么不能天然当权威真源；什么时候可以直接依赖模型参数知识；Information Type、Authority、Freshness、Determinism、Side Effect 五个维度怎样影响路由；为什么 Vector Search 不能替代 Database Query；为什么也不能把所有问题都变成 Tool Call；什么是 MultiSource Route；多个 Source 结果为什么必须保留 Provenance；哪些路由应该由硬规则决定，哪些可以交给模型；Fallback 时为什么必须暴露可信度下降；多个 Source 冲突时为什么不能静默选择；以及为什么最终最关键的指标是 Source-of-Truth Accuracy，而不是单纯 Tool Selection Accuracy。

如果这些能够完整讲出来：

\[
\boxed{
第七课第8阶段真正掌握
}
\]

---

# 下一阶段：第七课 · 第 9 阶段
# Failure Recovery、Retry 与 Human-in-the-loop
## Agent 已经会路由、会调用工具、会循环，但真实系统一旦超时、权限失败、证据不足、写操作不确定，怎样才能安全恢复？

到第 8 阶段，我们已经拥有：

```text
Source-of-Truth Routing
RAG
Database Tool
File Tool
Compute Tool
Action Tool
MultiSource Fusion
Conflict Detection
Fallback
```

下一阶段要解决：

> **真实世界不会永远成功。**

我们会正式拆开：

```text
Retryable Error
Terminal Error
Timeout
Rate Limit
Permission Denied
Partial Failure
Compensation
Rollback
Idempotency
Circuit Breaker
Human Escalation
Approval
Recovery State
```

并建立：

# `ProcurementAgentRecoveryPolicy_V0.1`

核心目标是：

\[
\boxed{
ReliableAgent
\neq
NeverFails
}
\]

而是：

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



---
