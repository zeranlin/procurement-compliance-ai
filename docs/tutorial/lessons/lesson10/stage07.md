# 第十课 · 第 7 阶段
# Serving Architecture：把 Model + RAG + Agent 接成真实 API 服务
## 模型能启动，不代表系统能上线。怎样把 Gateway、Model Server、Retriever、Agent、Tool、State、Queue、Auth 和 Trace 真正接成生产服务？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Deployment ≠ ModelLoading。**
2. **ProductionAI = ModelSystem + DistributedSystem。**
3. **Traceability 从统一 Request ID 开始。**
4. **AgentControlPlane ≠ ModelExecutionPlane。**
5. **Decision ≠ Authorization。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `State` | 状态：保存任务进度、事实和待办 |
| `Serving` | 服务化：把模型包装成可扩展、可观测、可治理的在线服务 |
| `Idempotency` | 幂等：重复执行不会产生不可控重复副作用 |
| `Observability` | 可观测性：通过指标、日志、追踪理解系统内部状态 |

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

到第 6 阶段，我们已经解决：

```text
显存
Batch
Inference Engine
多GPU
```

但生产系统不是：

```text
python model.generate()
```

它还必须面对：

```text
鉴权
限流
排队
超时
重试
RAG
Agent
Tool
状态
日志
审计
```

所以本阶段第一条边界：

\[
\boxed{
Deployment
\neq
ModelLoading
}
\]

本阶段最终形成：

# `ProcurementServingArchitecture_V0.1`

---

# 一、完整生产链

```text
Client
↓
API Gateway
↓
Auth / Rate Limit
↓
Request Router
↓
RAG / Agent Orchestrator
↓
Model Server
↓
Tool Services
↓
State / DB / Cache
↓
Response Stream
```

每一层都可能成为：

> 性能瓶颈、故障点或安全边界。

---

# 二、核心心智模型 ①
# `ProductionAI = ModelSystem + DistributedSystem`

模型只是其中一个组件。

真正上线后，

我们面对的是：

> 分布式系统问题。

---

# 三、API Gateway

至少负责：

```text
Authentication
鉴权

Authorization
授权

Rate Limiting
限流

Routing
路由

Quota
配额

TLS
加密传输
```

它是外部流量进入系统的第一层控制面。

---

# 四、Request ID

每个请求创建：

```text
request_id
```

并贯穿：

```text
Gateway
RAG
Model
Agent
Tool
Database
```

所以：

\[
\boxed{
Traceability
从
RequestID
开始
}
\]

---

# 五、核心心智模型 ②
# 没有统一 Request ID，就没有真正端到端追踪

日志再多，

如果无法串成同一个请求：

> 排障仍然很困难。

---

# 六、RAG Service

RAG 可以独立：

```text
Retriever
Reranker
Context Builder
```

好处：

```text
独立扩容
独立版本化
独立回滚
```

因此：

\[
\boxed{
RAGVersion
\neq
ModelVersion
}
\]

---

# 七、Agent Orchestrator

它负责：

```text
Goal
Plan
Tool Routing
State
Retry
Human Escalation
Completion
```

而 Model Server：

> 负责推理执行。

所以：

\[
\boxed{
AgentControlPlane
\neq
ModelExecutionPlane
}
\]

---

# 八、Tool Service

工具可能：

```text
查预算
写数据库
提交审批
发送消息
```

所以必须有：

```text
权限
超时
幂等
审计
重试策略
```

模型可以决定：

> 想调用什么。

但系统策略决定：

> 能不能调用。

所以：

\[
\boxed{
Decision
\neq
Authorization
}
\]

---

# 九、Timeout Budget

整个请求：

> 应有总超时预算。

内部组件：

```text
RAG
Model
Tool
Database
```

也要有分层 Timeout。

否则一个依赖卡住：

> 整条链都会无限等待。

---

# 十、Retry 与 Idempotency

读请求：

> 通常更容易安全重试。

写请求：

> 可能产生重复副作用。

所以：

\[
\boxed{
RetryPolicy
必须感知
Idempotency
}
\]

---

# 十一、Circuit Breaker

如果某个依赖持续失败，

继续调用会放大故障。

所以：

# Circuit Breaker
## 熔断器

在达到阈值时：

> 暂停调用、降级或转人工。

---

# 十二、核心心智模型 ③
# `RetryEverything` 会把局部故障变成雪崩

成熟 Retry 必须考虑：

```text
上限
Backoff
Jitter
Idempotency
Circuit Breaker
```

---

# 十三、Backpressure

下游模型满载时，

上游不能无限灌请求。

需要：

# Backpressure
## 背压

可以通过：

```text
限流
排队
降级
拒绝
```

保护下游。

---

# 十四、业务 State 不能只存在 Prompt 里

真实状态应该存：

```text
Database
Durable Store
State Service
```

模型上下文只是：

# Working Context
## 工作上下文

所以：

\[
\boxed{
BusinessState
\neq
PromptMemory
}
\]

---

# 十五、Streaming 与 Cancellation

流式服务还要处理：

```text
连接保持
客户端取消
断线
中途超时
```

如果用户取消：

> 后端应该尽快停止 Decode。

所以：

\[
\boxed{
ClientCancellation
\rightarrow
ComputeCancellation
}
\]

---

# 十六、Observability 与 Privacy

更多日志：

> 更容易排障。

但也带来：

```text
隐私
敏感数据
留存
访问风险
```

因此：

\[
\boxed{
Observability
必须和
Privacy
一起设计
}
\]

---

# 十七、System Version

生产版本不能只记：

```text
model=v0.2
```

还要记：

```text
rag_index_version
retriever_version
reranker_version
agent_policy_version
tool_registry_version
prompt_version
gateway_version
serving_engine_version
```

所以：

\[
\boxed{
SystemVersion
>
ModelVersion
}
\]

这里表示：

> 系统版本包含更多依赖。

---

# 十八、本阶段正式工程产物
# `ProcurementServingArchitecture_V0.1`

至少锁定：

```text
serving_architecture_version
api_gateway
auth_policy
authorization_policy
rate_limit
request_id_policy
router
model_server_version
rag_service_version
retriever_version
reranker_version
agent_orchestrator_version
tool_registry_version
tool_auth_policy
state_store
cache
timeout_budget
retry_policy
idempotency_policy
circuit_breaker
backpressure
queue_policy
streaming
cancellation
privacy_logging_policy
trace_context
release_gate
```

---

# 十九、本阶段最重要的 9 个核心心智模型

> **① `Deployment ≠ ModelLoading`。**

> **② `ProductionAI = ModelSystem + DistributedSystem`。**

> **③ Traceability 从统一 Request ID 开始。**

> **④ `AgentControlPlane ≠ ModelExecutionPlane`。**

> **⑤ `Decision ≠ Authorization`。**

> **⑥ Retry 必须与 Idempotency、Backoff、Circuit Breaker 联动。**

> **⑦ `BusinessState ≠ PromptMemory`。**

> **⑧ Client Cancellation 应传播到计算层。**

> **⑨ `SystemVersion > ModelVersion`。**

---

# 下一阶段：第十课 · 第 8 阶段
# Observability：Metrics、Logs、Tracing、GPU 与业务监控

最关键的边界：

\[
\boxed{
Monitoring
\neq
GPUUtilizationOnly
}
\]

并建立：

# `ProcurementObservabilityPolicy_V0.1`

---
