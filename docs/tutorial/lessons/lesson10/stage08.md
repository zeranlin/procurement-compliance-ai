# 第十课 · 第 8 阶段
# Observability：Metrics、Logs、Tracing、GPU 与业务监控
## 线上突然变慢、答错、RAG 漏检、Agent 工具失败，到底怎样知道“发生了什么、发生在哪一层、影响多少用户”？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Monitoring ≠ GPUUtilizationOnly。**
2. **Observability = Metrics + Logs + Traces + Quality + Cost。**
3. **HealthyGPU ≠ HealthyAI。**
4. **Metrics 适合聚合，Logs/Traces 适合高基数细节。**
5. **没有 Trace Span 只能知道慢，不能知道哪里慢。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `Observability` | 可观测性：通过指标、日志、追踪理解系统内部状态 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `Monitoring` | 监控：持续观察系统、模型和业务指标是否健康 |
| `Latency` | 延迟：单个请求从进入到完成的时间 |

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

系统上线以后，

最危险的不只是：

> 出问题。

而是：

> **出了问题却不知道原因。**

所以本阶段第一条边界：

\[
\boxed{
Monitoring
\neq
GPUUtilizationOnly
}
\]

本阶段最终形成：

# `ProcurementObservabilityPolicy_V0.1`

---

# 一、Monitoring 与 Observability

# Monitoring
## 监控

关注：

> 已知指标有没有异常。

# Observability
## 可观测性

关注：

> 能否通过系统产生的信号推断内部发生了什么。

经典三类信号：

```text
Metrics
Logs
Traces
```

对 AI 系统还要补：

```text
Quality Signals
Cost Signals
```

所以：

\[
\boxed{
Observability
=
Metrics
+
Logs
+
Traces
+
Quality
+
Cost
}
\]

---

# 二、Metrics 至少分四层

## Infrastructure

```text
GPU Utilization
GPU Memory
CPU
RAM
Network
Disk
```

## Inference

```text
TTFT
TPOT
E2E
Queue Time
Tokens/s
Batch
KV Utilization
OOM
```

## Application

```text
Request Rate
Error Rate
Timeout
Retry
RAG Latency
Tool Failure
```

## Quality

```text
Abstention Rate
Citation Failure
User Correction
Escalation Rate
Audit Failure
```

---

# 三、核心心智模型 ①
# `HealthyGPU ≠ HealthyAI`

GPU 95% 利用率、

没有 OOM，

但系统仍可能：

```text
引用错误
RAG漏检
Agent重复提交
```

所以：

\[
\boxed{
InfrastructureHealth
\neq
ProductQuality
}
\]

---

# 四、Golden Signals

传统服务常关注：

```text
Latency
Traffic
Errors
Saturation
```

AI 系统还应该显式加入：

```text
Quality
Cost
```

所以：

\[
\boxed{
AIServiceHealth
=
Latency
+
Traffic
+
Errors
+
Saturation
+
Quality
+
Cost
}
\]

---

# 五、Logs

日志可以记录：

```text
request_id
model_version
prompt_version
rag_version
tool_calls
status_code
latency
token_count
error_code
```

但用户原文、采购文件、敏感字段：

> 需要脱敏和留存策略。

所以：

\[
\boxed{
MoreLogs
\neq
BetterObservability
}
\]

日志应该：

> 结构化、分级、采样、可关联。

---

# 六、Tracing

一次请求可能：

```text
Gateway
↓
Retriever
↓
Reranker
↓
LLM
↓
Tool A
↓
LLM
↓
Tool B
```

总延迟 12 秒时，

Trace 可以告诉我们：

> 哪个步骤耗了多少时间。

所以：

\[
\boxed{
Trace
=
LatencyAttribution
+
FailureAttribution
}
\]

---

# 七、Span

Trace 中每个步骤是：

# Span
## 链路片段

例如：

```text
retrieval_span
rerank_span
prefill_span
decode_span
tool_span
```

没有 Span：

> 只能知道“慢”。

有 Span：

> 才能知道“哪里慢”。

---

# 八、核心心智模型 ②
# Metrics 聚合，Logs / Traces 解释细节

像：

```text
request_id
document_id
```

这种高基数字段，

不适合无限作为 Metric Label。

所以：

\[
\boxed{
Metrics
用于Aggregation
}
\]

\[
\boxed{
Logs/Traces
用于HighCardinalityDetail
}
\]

---

# 九、SLO 与 Error Budget

当 SLO 明确以后，

允许的失败空间可以理解为：

# Error Budget
## 错误预算

它可以帮助决定：

> 当前应该继续发布新功能，还是先修稳定性。

所以：

\[
\boxed{
ErrorBudget
=
ReliabilityChangeBudget
}
\]

---

# 十、核心心智模型 ③
# SLO 不是 Dashboard 装饰，而是发布节奏控制器

Error Budget 接近耗尽时：

> 应降低发布频率、优先恢复稳定性。

---

# 十一、Alert

好的告警应该对应：

```text
SLO风险
用户影响
安全异常
资源耗尽
```

例如：

```text
P99 TTFT持续超阈值
OOM上升
Queue持续增长
Tool权限错误
Critical Citation Error
```

告警太多会造成：

# Alert Fatigue
## 告警疲劳

所以：

\[
\boxed{
AlertVolume
\neq
OperationalAwareness
}
\]

---

# 十二、Online Quality Monitoring

线上可以观察：

```text
用户纠错率
人工转交率
拒答率
引用失败率
工具失败率
抽样人工审核
```

它们是：

# Proxy Signals
## 代理质量信号

但：

\[
\boxed{
OnlineSignal
\neq
GroundTruth
}
\]

不能完全替代：

```text
ProcurementBench_V1
```

---

# 十三、Drift Monitoring

线上输入可能变化：

```text
文档更长
行业变化
新格式
OCR质量下降
```

因此要监控：

# Input Drift
## 输入漂移

以及：

# Output Drift
## 输出漂移

例如：

```text
标签分布
拒答率
输出长度
风险类型分布
```

---

# 十四、Cost Monitoring

成本与：

```text
Input Tokens
Output Tokens
GPU Time
Tool Calls
Retrieval
```

相关。

可以记录：

```text
cost_per_request
cost_per_1k_requests
cost_per_successful_task
```

所以：

\[
\boxed{
CostPerSuccessfulOutcome
>
CostPerRequest
}
\]

这里表示：

> 更接近真实效率。

---

# 十五、本阶段正式工程产物
# `ProcurementObservabilityPolicy_V0.1`

至少锁定：

```text
observability_policy_version
metric_catalog
log_schema
trace_schema
request_id
trace_id
span_policy
gpu_metrics
inference_metrics
rag_metrics
agent_metrics
tool_metrics
quality_proxy_metrics
cost_metrics
slo_dashboard
error_budget
alert_rules
alert_severity
sampling_policy
pii_redaction
retention_policy
drift_monitoring
online_audit
incident_linkage
release_gate
```

---

# 十六、本阶段最重要的 9 个核心心智模型

> **① `Monitoring ≠ GPUUtilizationOnly`。**

> **② `Observability = Metrics + Logs + Traces + Quality + Cost`。**

> **③ `HealthyGPU ≠ HealthyAI`。**

> **④ Metrics 适合聚合，Logs/Traces 适合高基数细节。**

> **⑤ 没有 Trace Span 只能知道慢，不能知道哪里慢。**

> **⑥ `SLO + ErrorBudget` 应控制发布节奏。**

> **⑦ `AlertVolume ≠ Awareness`。**

> **⑧ `OnlineSignal ≠ GroundTruth`。**

> **⑨ `CostPerSuccessfulOutcome` 比单纯 Cost per Request 更完整。**

---

# 下一阶段：第十课 · 第 9 阶段
# Model Versioning、Canary、Shadow、A/B 与 Rollback

最关键的边界：

\[
\boxed{
NewVersionReady
\neq
NewVersionShouldReceive100PercentTraffic
}
\]

并建立：

# `ProcurementReleaseRolloutPolicy_V0.1`

---
