# 第十课 · 第 9 阶段
# Model Versioning、Canary、Shadow、A/B 与 Rollback
## 新模型为什么不能直接全量替换？怎样用 Canary、Shadow、A/B、Feature Flag 和 Rollback 把发布风险限制在可控范围？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **NewVersionReady ≠ 100% Traffic Ready。**
2. **ProductionVersion = ArtifactBundle。**
3. **Canary = LimitBlastRadius。**
4. **Shadow 用真实流量观察，但必须阻断真实副作用。**
5. **A/B 测真实用户因果效果，Shadow 更适合先测技术风险。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Rollback` | 回滚：出现问题时恢复上一稳定系统版本 |
| `Canary` | 灰度发布：让有限真实流量先使用新版本 |
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |

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

一个版本通过：

```text
ProcurementBench_V1
```

仍然不代表：

> 可以直接接 100% 真实流量。

因为生产还有：

```text
真实流量
真实并发
真实工具
真实依赖
真实故障
```

所以本阶段第一条边界：

\[
\boxed{
NewVersionReady
\neq
NewVersionShouldReceive100PercentTraffic
}
\]

本阶段最终形成：

# `ProcurementReleaseRolloutPolicy_V0.1`

---

# 一、Production Version 是 Artifact Bundle

至少包含：

```text
Model
Tokenizer
Quantization
Prompt
RAG Index
Retriever
Reranker
Agent Policy
Tool Registry
Thresholds
Serving Engine
Runtime Config
```

因此：

\[
\boxed{
ProductionVersion
=
ArtifactBundle
}
\]

而不是：

> 一个模型文件。

---

# 二、核心心智模型 ①
# `ModelVersion` 只是 `SystemVersion` 的一个节点

Prompt、RAG Index、Threshold：

> 任一个变化都可能改变系统行为。

所以所有生产变更都要进入：

> Release Trace。

---

# 三、Canary

# Canary Release
## 金丝雀发布

先让新版本接：

```text
1%
5%
10%
```

小流量，

观察：

```text
SLO
错误率
质量代理指标
成本
Tool失败
```

稳定后再扩大。

所以：

\[
\boxed{
Canary
=
LimitBlastRadius
}
\]

---

# 四、核心心智模型 ②
# Canary 的核心不是“慢慢上线”，而是限制故障爆炸半径

如果新版本有隐藏问题：

> 只影响少量用户。

---

# 五、Shadow Traffic

真实请求同时复制给：

```text
Champion
Challenger
```

但用户只看到 Champion。

Challenger 结果：

> 只用于评估。

所以：

\[
\boxed{
Shadow
=
ProductionWorkload
WithoutUserImpact
}
\]

---

# 六、Shadow 的副作用安全

如果 Agent 会：

```text
提交
写数据库
发送
审批
```

不能直接 Shadow 执行真实副作用。

需要：

```text
Dry Run
Mock
Sandbox
```

所以：

\[
\boxed{
ShadowSafety
必须感知
SideEffects
}
\]

---

# 七、A/B Test

随机把真实用户分到：

```text
A = Champion
B = Challenger
```

比较：

```text
成功率
完成率
延迟
转人工
成本
```

所以 A/B 更适合：

> 测真实用户因果效果。

Shadow 更适合：

> 先测技术风险。

---

# 八、核心心智模型 ③
# 风险可以逐步增加

一种典型路线：

```text
Offline Benchmark
↓
Shadow
↓
Canary
↓
A/B
↓
Full Rollout
```

不是唯一固定顺序，

但体现：

> 从低风险证据到高风险真实流量。

---

# 九、Feature Flag

可以运行时控制：

```text
新模型
新RAG
新Agent工具
新Prompt
```

是否启用。

所以：

\[
\boxed{
FeatureFlag
=
RuntimeReleaseControl
}
\]

---

# 十、Rollback

必须提前定义：

```text
previous_stable_version
compatibility_matrix
rollback_trigger
rollback_action
rollback_validation
```

所以：

\[
\boxed{
ReleaseReady
\Rightarrow
RollbackReady
}
\]

---

# 十一、核心心智模型 ④
# Rollback 不等于只换回旧 Weight

如果新版本还改了：

```text
Tokenizer
Prompt Schema
RAG Index
Agent State
Tool API
```

只换模型：

> 可能不兼容。

所以必须有：

# Compatibility Matrix
## 兼容矩阵

---

# 十二、State / Schema Migration

新 Agent 如果写入了新状态格式，

旧版本可能无法读取。

因此要区分：

```text
Backward Compatible
Forward Compatible
Breaking Change
```

所以：

\[
\boxed{
Rollbackability
必须在
Schema设计阶段考虑
}
\]

---

# 十三、Rollback Trigger

可以来自：

```text
P99超阈值
OOM
Critical Error
Tool Side Effect
错误率
质量代理指标异常
成本异常
```

这些触发条件应该：

> 预先定义。

所以：

\[
\boxed{
Rollback
=
PolicyDriven
}
\]

---

# 十四、Automatic Rollback

基础设施信号：

```text
OOM
错误率
延迟
```

更适合自动化。

复杂质量问题：

> 可能需要人工确认。

所以：

\[
\boxed{
AutomationLevel
取决于
SignalReliability
}
\]

---

# 十五、核心心智模型 ⑤
# `FastRollback` 比 `PerfectDetection` 更现实

生产不可能提前发现所有问题。

所以成熟系统必须：

> 能快速限制影响。

---

# 十六、Release Manifest

每次发布至少记录：

```text
release_id
system_version
model_version
quantization_version
prompt_version
rag_index_version
agent_policy_version
serving_engine_version
feature_flags
traffic_percentage
benchmark_result
slo_result
rollback_target
```

因此：

\[
\boxed{
WhatIsRunningNow
必须机器可回答
}
\]

---

# 十七、本阶段正式工程产物
# `ProcurementReleaseRolloutPolicy_V0.1`

至少锁定：

```text
rollout_policy_version
release_manifest_schema
champion_version
challenger_version
shadow_policy
canary_stages
traffic_split
ab_test_policy
feature_flags
side_effect_shadow_policy
compatibility_matrix
rollback_target
rollback_trigger
automatic_rollback
manual_approval
rollback_validation
database_migration_policy
state_compatibility
slo_guardrail
quality_guardrail
cost_guardrail
release_audit
```

---

# 十八、本阶段最重要的 9 个核心心智模型

> **① `NewVersionReady ≠ 100% Traffic Ready`。**

> **② `ProductionVersion = ArtifactBundle`。**

> **③ `Canary = LimitBlastRadius`。**

> **④ Shadow 用真实流量观察，但必须阻断真实副作用。**

> **⑤ A/B 测真实用户因果效果，Shadow 更适合先测技术风险。**

> **⑥ `ReleaseReady ⇒ RollbackReady`。**

> **⑦ Rollback 是兼容性问题，不只是旧 Weight 重部署。**

> **⑧ `FastRollback` 是生产安全核心能力。**

> **⑨ `WhatIsRunningNow` 必须机器可查询。**

---

# 下一阶段：第十课 · 第 10 阶段
# 真正部署 `ProcurementAI`：性能压测、SLO、Release Gate 与生产闭环

最关键的总边界：

\[
\boxed{
DeploymentSuccess
\neq
ProductionReadiness
}
\]

最终交付：

# `ProcurementAI`

---
