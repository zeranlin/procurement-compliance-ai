# 第十一课 · 第 16 阶段
# 真正交付 `ProcurementLM_V1.0`
## 生产部署、规则热更新、法规热更新、审计、反馈闭环、灰度发布、回滚与长期运营

第 15 阶段我们已经建立：

\[
\boxed{
OverallAccuracy
\neq
ComplianceReliability
}
\]

**中文业务释义：** 总体准确率高 ≠ 政府采购合规系统已经可靠；关键规则漏检、法规引用错误、证据错配、错误弃权和 Agent 工作流失败，都可能被一个漂亮的总体分数掩盖。

并建立：

\[
\boxed{
ReleaseReady
=
ModelGate
\land
RuleGate
\land
LegalGate
\land
AgentGate
\land
RedTeamGate
}
\]

**中文业务释义：** 发布就绪 = 模型门 ∧ 规则门 ∧ 法规门 ∧ Agent 门 ∧ 红队门；任何关键门失败，都不能靠其他高分平均掉。

现在进入第十一课，也是整个 130 阶段课程的最后一个阶段。

真正的问题不再是：

> “模型能不能跑？”

而是：

> **“这套政府采购合规系统能不能长期、安全、稳定、可回滚、可审计地运行？”**

所以本阶段第一条核心边界正式锁定：

\[
\boxed{
DeploymentSuccess
\neq
ProductionReadiness
}
\]

**中文业务释义：** 模型和 Agent 已经成功部署、接口可以返回结果 ≠ 系统已经具备政府采购生产环境所需的稳定性、版本治理、权限、审计、监控、热更新、回滚和持续改进能力。

本阶段最终交付：

# `ProcurementLM_V1.0`

---

# 一、最终系统到底是什么？

它不是一个单独模型文件。

最终系统应理解为：

\[
\boxed{
ProcurementLM\_V1.0
=
Data
+
Rules
+
Policy
+
LegalRAG
+
Calculator
+
ComplianceLM
+
Engine
+
Agent
+
Benchmark
+
ProductionOps
}
\]

**中文业务释义：** `ProcurementLM_V1.0` = 数据工程 + 规则体系 + 法规政策体系 + 法规 RAG + 确定性计算器 + 合规模型 + 混合合规引擎 + Agent 工作流 + Gold Benchmark + 生产运维治理。

所以：

\[
\boxed{
ProductVersion
\neq
ModelCheckpoint
}
\]

**中文业务释义：** 产品版本 ≠ 某一个模型 Checkpoint；生产系统版本必须同时绑定模型、规则、法规、RAG、Agent、工具和代码版本。

---

# 二、核心心智模型 ①
# `ModelVersion` 不等于 `SystemVersion`

\[
\boxed{
ModelVersion
\neq
SystemVersion
}
\]

**中文业务释义：** 模型版本号 ≠ 整套政府采购合规系统版本号。

例如同一个：

```text
model_version = ProcurementComplianceLM_V1-RC3
# 中文：模型发布候选版本
```

如果同时更换了：

```text
rule_bundle_version    # 中文：D01-D22及其他规则包版本

policy_snapshot_id    # 中文：法规政策快照

rag_index_version    # 中文：法规检索索引版本

agent_version    # 中文：Agent编排版本

tool_registry_version    # 中文：工具注册表版本
```

那么：

> 系统行为已经可能发生变化。

---

# 三、Production Release Bundle
## 生产发布包必须把关键版本锁在一起

建议每一次发布生成不可变 Release Bundle：

```text
system_release_id    # 中文：整套系统发布版本标识

release_channel    # 中文：开发 / 测试 / 灰度 / 正式生产通道

model_version_id    # 中文：合规模型版本

base_model_id    # 中文：基础模型版本

adapter_version_id    # 中文：LoRA / QLoRA适配器版本

tokenizer_version    # 中文：Tokenizer版本

rule_bundle_version    # 中文：D01-D22及其他规则包版本

policy_snapshot_id    # 中文：法规政策快照

legal_rag_index_version    # 中文：法规RAG索引版本

parser_version    # 中文：采购文件解析器版本

dataset_schema_version    # 中文：采购数据Schema版本

agent_version    # 中文：Agent工作流版本

tool_registry_version    # 中文：工具注册表版本

prompt_template_version    # 中文：受控Prompt模板版本

benchmark_snapshot_id    # 中文：通过Release Gate的Benchmark快照

runtime_image_version    # 中文：运行环境镜像版本

application_code_version    # 中文：应用代码版本

release_manifest_hash    # 中文：发布清单指纹
```

---

# 四、核心心智模型 ②
# `ReleaseBundle` 必须不可变

\[
\boxed{
ReleasedBundle
\Rightarrow
Immutable
}
\]

**中文业务释义：** 已发布生产版本 ⇒ 发布包本身应保持不可变；如果需要改变规则、法规快照或模型，应形成新的发布版本，而不是悄悄改旧版本内容。

这样才能回答：

> “某个项目在某一天到底由哪一套系统版本审查？”

---

# 五、最终生产架构

建议的逻辑架构：

```text
User / Reviewer
# 中文：采购业务人员、法规人员、技术专家或审计人员
↓
API Gateway / Access Control
# 中文：统一入口、身份认证、权限和请求控制
↓
Project Service
# 中文：采购项目、文件、版本和审查任务管理
↓
Document Pipeline
# 中文：PDF / Word / 表格 / OCR解析和Stage10数据质量门
↓
Compliance Agent
# 中文：Stage14任务规划、状态、工具和人工复核编排
↓
Hybrid Compliance Engine
# 中文：Stage11规则、计算、法规RAG、LLM和证据验证
├── Rule Engine
│   # 中文：D01-D22及资格、技术、评分、政策等确定性规则
├── Calculator
│   # 中文：价格、比例、期限、异常低价等确定性计算
├── Policy Resolver
│   # 中文：法规政策时点、辖区、范围和例外解析
├── Legal RAG
│   # 中文：法规条文、版本和引用支持检索
└── Compliance LLM
    # 中文：复杂语义关系、必要性、等效性和证据充分性判断
↓
Human Review Service
# 中文：法规、业务、技术等人工复核队列
↓
Report Service
# 中文：从已验证结构化状态生成报告
↓
Audit / Event Store
# 中文：保存版本、工具调用、状态变化和人工结论
↓
Monitoring / Release Governance
# 中文：生产监控、回归、告警、发布、回滚和反馈闭环
```

---

# 六、核心心智模型 ③
# `Serving` 不是只把模型放进 GPU

\[
\boxed{
ProductionServing
\neq
ModelLoading
}
\]

**中文业务释义：** 生产服务 ≠ 只把模型加载到 GPU；真正生产服务还包括认证、任务编排、法规快照、规则服务、缓存、限流、日志、监控、故障转移和人工复核。

---

# 七、环境分层
## 不要直接从开发机上线

建议至少：

```text
DEV    # 中文：开发环境，用于代码和规则开发

TEST    # 中文：自动化测试环境

STAGING    # 中文：与生产配置尽量一致的发布前验证环境

CANARY    # 中文：有限真实流量的灰度环境

PRODUCTION    # 中文：正式生产环境
```

注意：

> `CANARY` 流量比例不应在课程里写死统一数字，应由组织根据业务量、风险和回滚能力设定。

---

# 八、核心心智模型 ④
# `Release` 不等于 `Rollout`

\[
\boxed{
Release
\neq
Rollout
}
\]

**中文业务释义：** 一个版本已经具备发布资格 ≠ 应立即对所有生产用户全面启用；Release 是“允许发布”，Rollout 是“逐步把版本暴露给真实流量”。

---

# 九、Shadow / Canary / Full Rollout
## 三种常见生产验证方式

### Shadow
## 影子运行

```text
production_input_copy    # 中文：复制真实生产输入

new_version_runs_silently    # 中文：新版本后台执行

no_user_visible_effect    # 中文：结果不影响用户和业务决策

compare_with_current_version    # 中文：与当前生产版本对比
```

适合：

> 新模型、新规则、新 RAG 索引上线前观察真实分布表现。

### Canary
## 灰度发布

```text
limited_real_traffic    # 中文：只让部分真实业务流量进入新版本

real_user_effect    # 中文：结果会真正进入业务流程

strict_monitoring    # 中文：必须强化监控

fast_rollback_required    # 中文：必须能够快速回滚
```

### Full Rollout
## 全量发布

只有：

> 灰度指标、Release Gate和人工治理都满足要求以后，

才进入全量。

---

# 十、核心心智模型 ⑤
# `ShadowPass` 不等于 `CanaryPass`

\[
\boxed{
ShadowPass
\neq
CanaryPass
}
\]

**中文业务释义：** 影子运行表现良好 ≠ 真实灰度一定安全；Shadow 不影响真实用户，而 Canary 会真正进入业务流程，因此风险等级不同。

---

# 十一、Rollback
## 回滚必须在上线前设计

第十课已经建立：

\[
\boxed{
ReleaseReady
\Rightarrow
RollbackReady
}
\]

**中文业务释义：** 真正发布就绪 ⇒ 必须已经准备好回滚路径。

Stage 16 进一步要求每个 Release Bundle 保存：

```text
previous_stable_release_id    # 中文：上一稳定版本

rollback_compatible_schema    # 中文：数据Schema是否兼容回滚

rollback_policy_snapshot_id    # 中文：回滚时对应法规政策快照

rollback_rule_bundle_version    # 中文：回滚规则包版本

rollback_runtime_image    # 中文：回滚运行环境

rollback_validation_tests    # 中文：回滚后必须立即执行的验证测试
```

---

# 十二、核心心智模型 ⑥
# `Rollback` 不是“重新部署旧模型”这么简单

\[
\boxed{
Rollback
=
Model
+
Rules
+
Policy
+
RAG
+
Agent
+
SchemaCompatibility
}
\]

**中文业务释义：** 回滚 = 模型 + 规则 + 法规快照 + RAG + Agent + 数据结构兼容性一起回退；只换回旧模型可能仍然保留了错误的新规则或新索引。

---

# 十三、规则热更新
## Rule Hot Update 为什么必须独立？

D01-D22等规则可能发生：

> 规则表达修复、判断逻辑优化、例外补充、测试样本扩展。

这通常不需要重新训练模型。

所以：

\[
\boxed{
RuleUpdate
\neq
ModelRetraining
}
\]

**中文业务释义：** 规则更新 ≠ 必须重新训练模型。

推荐工作流：

```text
RULE_DRAFTED    # 中文：规则修改草案

SOURCE_BOUND    # 中文：绑定法规 / 专项整治 / 业务依据

UNIT_TESTED    # 中文：规则单元测试通过

SLICE_REGRESSION_PASSED    # 中文：对应Dxx / 业务切片回归通过

SHADOW_VALIDATED    # 中文：影子运行验证

APPROVED    # 中文：有权限人员批准

ACTIVATED    # 中文：生产激活

ROLLBACK_READY    # 中文：旧规则版本可立即恢复
```

---

# 十四、核心心智模型 ⑦
# `RuleHotUpdate` 不能绕过 Benchmark

\[
\boxed{
RuleHotUpdate
\neq
UnreviewedHotPatch
}
\]

**中文业务释义：** 规则热更新 ≠ 可以绕过测试和审批直接修改生产规则；“热更新”只是不用重训模型，不代表不用验证。

---

# 十五、规则 Activation
## 规则激活建议使用版本切换，而不是覆盖

```text
rule_id = D05    # 中文：规则逻辑身份

rule_version = 1.4.0    # 中文：当前规则具体版本

activation_time    # 中文：生产激活时间

deactivation_time    # 中文：停止使用时间

previous_version    # 中文：上一稳定规则版本

change_reason    # 中文：为什么修改

regression_report_id    # 中文：对应回归测试报告

approver_id    # 中文：批准人 / 角色
```

---

# 十六、法规热更新
## Policy Hot Update 与 Rule Update 不是一回事

Stage 12 已经建立：

\[
\boxed{
PolicyUpdate
\neq
ModelRetraining
}
\]

**中文业务释义：** 法规政策更新 ≠ 必须重新训练模型；法规版本、时间、辖区和检索索引应由Policy Registry与Legal RAG独立热更新。

生产流程至少：

```text
INGEST_OFFICIAL_SOURCE    # 中文：抓取 / 接收新的官方法规政策来源

VERIFY_SOURCE    # 中文：核验发文机关、文号、来源和版本

CREATE_POLICY_VERSION    # 中文：创建新的法规政策版本记录

RESOLVE_TEMPORAL_RELATION    # 中文：解析发布、生效、失效、替代和过渡时间

RESOLVE_JURISDICTION_SCOPE    # 中文：解析中央 / 地方、地区、预算级次和事项范围

UPDATE_RELATION_GRAPH    # 中文：建立修改、废止、替代、实施、例外关系

BUILD_INCREMENTAL_INDEX    # 中文：增量更新法规RAG索引

RUN_LEGAL_REGRESSION    # 中文：运行法规检索和适用性回归

PUBLISH_POLICY_SNAPSHOT    # 中文：发布新的法规政策快照

ACTIVATE_FOR_NEW_REVIEWS    # 中文：让新的项目审查使用新快照
```

---

# 十七、核心心智模型 ⑧
# `PolicySnapshot` 必须支持项目级 Pin

\[
\boxed{
ProjectReview
\Rightarrow
PinnedPolicySnapshot
}
\]

**中文业务释义：** 一次正式项目审查 ⇒ 应绑定固定法规政策快照；审查进行过程中即使有新政策发布，也不能悄悄改变正在执行项目的法律环境。

如确需重新评估：

> 应创建新的 Review Snapshot 或明确 Reopen。

---

# 十八、核心心智模型 ⑨
# `LatestPolicyAvailable` 不等于 `CurrentReviewShouldSwitch`

\[
\boxed{
LatestPolicyAvailable
\neq
AutomaticMidReviewSwitch
}
\]

**中文业务释义：** 法规库已经有更新版本 ≠ 正在进行中的项目审查应自动切换到新版本；是否切换必须由业务事件时间、适用性和审查版本治理决定。

---

# 十九、Change Classification
## 每次生产变化都要先分类

建议：

```text
MODEL_CHANGE    # 中文：模型或Adapter变化

RULE_CHANGE    # 中文：D01-D22等规则变化

POLICY_CHANGE    # 中文：法规政策和Policy Snapshot变化

RAG_CHANGE    # 中文：向量模型、索引、检索器、重排器变化

PARSER_CHANGE    # 中文：PDF / Word / OCR / 表格解析变化

AGENT_CHANGE    # 中文：任务图、状态机、工具路由变化

TOOL_CHANGE    # 中文：Calculator、市场证据工具等变化

REPORT_CHANGE    # 中文：报告Schema或渲染逻辑变化

INFRA_CHANGE    # 中文：推理服务、数据库、网络、GPU等基础设施变化

SECURITY_CHANGE    # 中文：认证、权限、密钥或安全策略变化
```

---

# 二十、核心心智模型 ⑩
# `ChangeType` 决定 `RegressionScope`

\[
\boxed{
ChangeType
\rightarrow
RequiredRegressionSuite
}
\]

**中文业务释义：** 变更类型 → 决定必须运行哪些回归测试，而不是所有修改都只跑同一套最小测试。

例如：

> Rule Change 必须跑规则切片；

> Policy Change 必须跑 Temporal / Jurisdiction / Citation；

> Agent Change 必须跑任务图、状态、人工、Coverage 和 Report E2E。

---

# 二十一、生产监控
## 不能只看 GPU 和 HTTP 200

Lesson 10 已经建立：

\[
\boxed{
Monitoring
\neq
GPUUtilizationOnly
}
\]

**中文业务释义：** 生产监控 ≠ 只看 GPU 利用率。

Stage 16 至少分五层：

```text
INFRA_METRICS    # 中文：GPU、CPU、内存、网络、数据库、队列

MODEL_METRICS    # 中文：模型延迟、Token、失败、超时、弃权

COMPLIANCE_METRICS    # 中文：D01-D22覆盖、Finding、误报反馈、证据完整性

LEGAL_METRICS    # 中文：法规快照新鲜度、Citation Support、索引更新时间

AGENT_METRICS    # 中文：任务阻塞、工具失败、人工队列、Coverage、报告完整性
```

---

# 二十二、核心心智模型 ⑪
# `SystemHealthy` 不等于 `ServiceUp`

\[
\boxed{
HTTP200
\neq
ComplianceHealthy
}
\]

**中文业务释义：** 接口返回 HTTP 200 ≠ 合规系统处于健康状态；如果法规索引过期、D01-D22覆盖下降、人工队列堵塞或报告过度声明，系统仍可能不健康。

---

# 二十三、生产业务指标建议

```text
review_completion_rate    # 中文：项目按预期完成审查的比例

partial_review_rate    # 中文：只能部分审查的项目比例

coverage_completion_rate    # 中文：必需规则和业务域完成覆盖的比例

supported_finding_rate    # 中文：证据支持的Finding比例

evidence_insufficient_rate    # 中文：证据不足案例比例

human_escalation_rate    # 中文：转人工比例

human_queue_age    # 中文：人工复核任务等待时长

tool_failure_rate    # 中文：工具执行失败率

safe_fallback_rate    # 中文：工具失败后安全降级比例

report_integrity_error_rate    # 中文：报告与结构化状态不一致的比例

policy_freshness_lag    # 中文：新法规进入可用Policy Snapshot的延迟

rule_activation_lag    # 中文：批准规则进入生产的延迟

rollback_time    # 中文：发现严重问题后恢复稳定版本所需时间
```

---

# 二十四、SLO
## 服务级目标不是只有延迟

SLO = Service Level Objective
## 服务级目标

可以针对：

```text
availability_slo    # 中文：服务可用性目标

latency_slo    # 中文：接口 / 项目审查时延目标

coverage_slo    # 中文：审查覆盖完整性目标

policy_freshness_slo    # 中文：法规知识更新及时性目标

audit_write_slo    # 中文：审计事件写入可靠性目标

human_review_slo    # 中文：高风险人工复核响应时效目标
```

具体目标数字：

> 应由组织根据生产规模、风险等级、人工资源和基础设施能力设定，不应在课程中伪装成统一行业法定值。

---

# 二十五、核心心智模型 ⑫
# `LatencySLO` 不能替代 `ComplianceSLO`

\[
\boxed{
FastResponse
\neq
ReliableReview
}
\]

**中文业务释义：** 响应快 ≠ 合规审查可靠；生产系统必须同时治理速度、覆盖、证据、法规新鲜度和人工处理。

---

# 二十六、Critical Alert
## 哪些生产事件应该立即告警？

建议：

```text
STALE_POLICY_SNAPSHOT    # 中文：法规快照超过允许新鲜度

AUDIT_WRITE_FAILURE    # 中文：关键审计日志写入失败

SILENT_TOOL_FAILURE    # 中文：工具失败却被系统当作已检查

COVERAGE_OVERCLAIM    # 中文：部分审查被报告成完整审查

HIGH_RISK_HUMAN_BYPASS    # 中文：高风险Finding绕过人工门

POLICY_VERSION_MISMATCH    # 中文：Finding使用的法规版本与项目快照不一致

RULE_BUNDLE_MISMATCH    # 中文：执行规则版本与Release Bundle不一致

PROMPT_INJECTION_SUCCESS    # 中文：文档 / 工具文字成功改变Agent策略

CRITICAL_SLICE_REGRESSION    # 中文：D01-D22关键切片出现明显退化

REPORT_STATE_MISMATCH    # 中文：报告内容与结构化项目状态不一致
```

---

# 二十七、核心心智模型 ⑬
# 有些告警需要自动进入 Safe Mode

\[
\boxed{
CriticalIntegrityFailure
\Rightarrow
SafeMode
}
\]

**中文业务释义：** 关键完整性故障 ⇒ 应自动进入安全模式，而不是继续正常出正式报告。

---

# 二十八、Safe Mode
## 安全模式可以怎样设计？

```text
READ_ONLY_AUDIT_MODE    # 中文：只允许查看历史结果和审计，不继续生成新正式结论

HUMAN_REVIEW_ONLY_MODE    # 中文：自动系统只整理证据，所有结论必须人工确认

NO_FINAL_REPORT_MODE    # 中文：允许分析但禁止生成正式报告

LEGAL_RAG_DEGRADED_MODE    # 中文：法规RAG不可用时禁止形成依赖法源的正式Finding

MODEL_DEGRADED_MODE    # 中文：模型故障时只运行确定性规则和人工流程

NEW_PROJECT_PAUSED    # 中文：暂停接收新的正式审查项目
```

---

# 二十九、核心心智模型 ⑭
# `DegradedMode` 不是“假装一切正常”

\[
\boxed{
GracefulDegradation
=
ReducedCapability
+
ExplicitDisclosure
}
\]

**中文业务释义：** 优雅降级 = 功能减少 + 明确告知能力边界；降级状态必须对业务人员可见，不能继续输出“完整审查”。

---

# 三十、Incident Response
## 生产事故处理流程

建议：

\[
\boxed{
Detect
\rightarrow
Contain
\rightarrow
SwitchSafeMode
\rightarrow
RollbackOrPin
\rightarrow
HumanReview
\rightarrow
RootCause
\rightarrow
Fix
\rightarrow
Regression
\rightarrow
ReRelease
}
\]

**中文业务释义：** 发现事故 → 控制影响范围 → 进入安全模式 → 回滚或锁定稳定版本 → 人工复核受影响项目 → 根因分析 → 修复 → 回归测试 → 重新发布。

---

# 三十一、核心心智模型 ⑮
# `IncidentClosed` 不等于 `ServiceRestored`

\[
\boxed{
ServiceRestored
\neq
IncidentClosed
}
\]

**中文业务释义：** 服务恢复可用 ≠ 事故已经完全关闭；还必须确认受影响项目范围、旧结论是否需要重审、审计是否完整以及根因是否修复。

---

# 三十二、Affected Review Identification
## 事故后必须知道哪些项目受影响

每个 Finding / Review 都必须能回查：

```text
system_release_id    # 中文：使用哪个系统发布版本

model_version_id    # 中文：使用哪个模型

rule_bundle_version    # 中文：使用哪个规则包

policy_snapshot_id    # 中文：使用哪个法规快照

parser_version    # 中文：使用哪个解析器

agent_version    # 中文：使用哪个Agent

tool_call_versions    # 中文：具体工具版本

review_time_range    # 中文：项目执行时间范围
```

才能执行：

```text
affected_review_query    # 中文：查询受事故版本影响的项目

reopen_required    # 中文：是否需要重新打开审查

recompute_scope    # 中文：只重算哪些受影响任务
```

---

# 三十三、核心心智模型 ⑯
# `VersionTraceability` 是事故响应能力

\[
\boxed{
NoVersionTrace
\Rightarrow
NoReliableImpactAnalysis
}
\]

**中文业务释义：** 没有版本追踪 ⇒ 无法可靠判断事故影响了哪些项目。

---

# 三十四、权限治理
## RBAC

RBAC = Role-Based Access Control
## 基于角色的访问控制

建议至少区分：

```text
PROCUREMENT_REVIEWER    # 中文：采购业务审查人员

LEGAL_REVIEWER    # 中文：法规 / 法务复核人员

TECHNICAL_REVIEWER    # 中文：技术参数专业复核人员

POLICY_ADMIN    # 中文：法规政策库管理员

RULE_ADMIN    # 中文：规则库管理员

MODEL_ADMIN    # 中文：模型和Adapter管理员

RELEASE_MANAGER    # 中文：生产发布负责人

AUDITOR    # 中文：审计人员，只读审计和版本轨迹

SYSTEM_ADMIN    # 中文：基础设施管理员
```

---

# 三十五、核心心智模型 ⑰
# `Admin` 不应成为万能角色

\[
\boxed{
OneSuperAdmin
\neq
GoodGovernance
}
\]

**中文业务释义：** 一个拥有所有模型、规则、法规、发布和审计权限的超级管理员 ≠ 良好治理；高风险系统应尽量拆分职责、执行最小权限。

---

# 三十六、Separation of Duties
## 职责分离

例如：

```text
RULE_ADMIN can edit rule draft
# 中文：规则管理员可以修改规则草案

RELEASE_MANAGER activates approved version
# 中文：发布负责人激活已经审批的版本

AUDITOR cannot modify production rule
# 中文：审计人员不能修改生产规则
```

这可以减少：

> 单人误操作或未经复核直接上线。

---

# 三十七、核心心智模型 ⑱
# `CanEdit` 不等于 `CanActivate`

\[
\boxed{
EditPermission
\neq
ActivationPermission
}
\]

**中文业务释义：** 有权修改规则 / 法规元数据 ≠ 有权直接激活生产版本。

---

# 三十八、数据与安全
## 生产系统至少要回答哪些问题？

```text
who_can_upload    # 中文：谁可以上传采购文件

who_can_view    # 中文：谁可以查看项目和Finding

who_can_export    # 中文：谁可以导出报告 / 证据

who_can_reopen    # 中文：谁可以重新打开已关闭审查

who_can_override    # 中文：谁可以覆盖自动判断

who_can_publish_policy_snapshot    # 中文：谁可以发布法规快照

who_can_activate_rule_bundle    # 中文：谁可以激活规则包

who_can_release_system    # 中文：谁可以发布整套系统
```

---

# 三十九、Data Lineage
## 每一个输出都要知道从哪里来

\[
\boxed{
Report
\rightarrow
Finding
\rightarrow
DecisionTrace
\rightarrow
Evidence
\rightarrow
SourceDocument
}
\]

**中文业务释义：** 报告 → Finding → 决策轨迹 → 证据 → 原始采购文件；任何正式结论都应该能沿链条回到来源。

同时：

\[
\boxed{
Finding
\rightarrow
LegalProposition
\rightarrow
PolicyVersion
\rightarrow
OfficialSource
}
\]

**中文业务释义：** Finding → 法律命题 → 法规版本 → 官方来源；任何法律依据也必须能追溯到对应正式来源。

---

# 四十、核心心智模型 ⑲
# `Auditability` 不是多记日志

\[
\boxed{
Auditability
=
TraceableDecision
+
VersionedInputs
+
ControlledChanges
}
\]

**中文业务释义：** 可审计性 = 可追踪决策 + 已版本化输入 + 受控制的变更；不是简单把日志数量堆得很多。

---

# 四十一、Production Feedback
## 生产反馈不能直接回灌训练

典型反馈：

```text
FALSE_POSITIVE    # 中文：生产误报

FALSE_NEGATIVE    # 中文：人工发现系统漏检

WRONG_CITATION    # 中文：法规引用错误

WRONG_EVIDENCE    # 中文：采购证据定位错误

WRONG_ABSTENTION    # 中文：不该转人工却转人工，或该转人工却强判

WORKFLOW_FAILURE    # 中文：Agent状态、工具或报告流程失败

USER_CLARIFICATION    # 中文：采购人员补充真实业务上下文
```

---

# 四十二、核心心智模型 ⑳
# `ProductionFeedback` 不等于 `TrainingData`

\[
\boxed{
ProductionFeedback
\neq
ImmediateTrainingData
}
\]

**中文业务释义：** 生产反馈 ≠ 可以直接塞进下一轮训练；它必须先经过复现、证据绑定、法规快照确认和专家裁决。

---

# 四十三、Feedback Triage
## 反馈分流

推荐：

```text
REPRODUCE    # 中文：先复现生产错误

CLASSIFY_FAILURE    # 中文：判断是Parser、Rule、Policy、RAG、LLM、Agent还是Report问题

BIND_EVIDENCE    # 中文：绑定原始证据和当时系统版本

ADJUDICATE    # 中文：专家形成Gold结论

ASSIGN_DATA_ROLE    # 中文：决定进入训练集、Benchmark、Red Team还是规则回归集

FIX_COMPONENT    # 中文：修复真正的问题组件

REGRESSION_TEST    # 中文：验证修复没有造成新退化
```

---

# 四十四、核心心智模型 ㉑
# `FixTheComponent`，不要什么都靠重训模型

\[
\boxed{
FailureSource
\rightarrow
CorrectComponentFix
}
\]

**中文业务释义：** 错误来自哪个组件 → 修哪个组件。

例如：

```text
wrong OCR    # 中文：修Parser / OCR

wrong numeric calculation    # 中文：修Calculator

wrong legal version    # 中文：修Policy Resolver / Legal RAG

wrong deterministic predicate    # 中文：修Rule Engine

semantic relevance failure    # 中文：才可能需要改训练数据 / 模型

wrong task routing    # 中文：修Agent Router

wrong report wording from correct state    # 中文：修Report Renderer
```

---

# 四十五、Feedback-to-Benchmark First
## 高价值生产失败先成为测试资产

推荐数据飞轮：

\[
\boxed{
ProductionFailure
\rightarrow
GoldAdjudication
\rightarrow
BenchmarkOrRedTeam
\rightarrow
Fix
\rightarrow
Regression
\rightarrow
TrainingCandidate
}
\]

**中文业务释义：** 生产失败 → 专家Gold裁决 → 先进入Benchmark或Red Team → 修复 → 回归验证 → 再判断是否作为训练候选。

这样能防止：

> 修了一个错误，却没有留下以后防止复发的测试。

---

# 四十六、核心心智模型 ㉒
# `EveryCriticalBug` 应留下 Regression Case

\[
\boxed{
CriticalProductionFailure
\Rightarrow
PermanentRegressionCase
}
\]

**中文业务释义：** 关键生产故障 ⇒ 应形成长期保留的回归案例，确保后续版本不会再次犯同样错误。

---

# 四十七、避免反馈闭环污染 Benchmark

不能：

> 同一个案例既进入 Train，又继续当作“未见过Gold测试”。

所以反馈进入数据治理后要标记：

```text
TRAIN_ELIGIBLE    # 中文：可进入训练集

BENCHMARK_ONLY    # 中文：只用于正式Benchmark，不进入训练

REDTEAM_ONLY    # 中文：只用于红队

REGRESSION_ONLY    # 中文：只用于组件回归

BLIND_HOLDOUT    # 中文：保持开发团队和模型未见状态
```

---

# 四十八、核心心智模型 ㉓
# `DataFlywheel` 必须有防泄漏治理

\[
\boxed{
FeedbackLoop
\neq
BlindDataRecycling
}
\]

**中文业务释义：** 反馈闭环 ≠ 把所有生产数据反复回灌训练；必须控制 Train / Benchmark / Holdout 角色，避免评测污染。

---

# 四十九、Drift
## 生产分布为什么会变？

至少可能发生：

```text
DOCUMENT_DRIFT    # 中文：采购文件格式和模板变化

BUSINESS_DRIFT    # 中文：采购品类和业务场景变化

POLICY_DRIFT    # 中文：法规政策变化

MARKET_DRIFT    # 中文：产品、供应商、技术路线变化

LANGUAGE_DRIFT    # 中文：风险条件出现新的表达方式

TOOL_DRIFT    # 中文：外部检索或解析工具行为变化

MODEL_BEHAVIOR_DRIFT    # 中文：新模型版本产生新的行为分布
```

---

# 五十、核心心智模型 ㉔
# `Drift` 不一定是模型问题

\[
\boxed{
ObservedPerformanceShift
\neq
ModelDriftOnly
}
\]

**中文业务释义：** 生产表现变化 ≠ 一定是模型漂移；可能是法规、文档格式、市场或工具发生变化。

---

# 五十一、Drift Monitoring
## 漂移监控建议

```text
document_schema_change_rate    # 中文：文件结构变化率

unknown_clause_pattern_rate    # 中文：未知条款模式比例

new_rule_candidate_rate    # 中文：现有规则无法覆盖的新风险模式比例

policy_update_frequency    # 中文：法规政策更新频率

out_of_distribution_rate    # 中文：超出训练 / Benchmark已知分布比例

human_override_rate    # 中文：人工推翻自动结论比例

slice_metric_drift    # 中文：D01-D22等关键切片指标随时间变化
```

---

# 五十二、Periodic Revalidation
## 即使没有代码更新，也要重新验证

因为：

> 法规、采购模板和市场都可能变化。

所以：

\[
\boxed{
NoCodeChange
\neq
NoRevalidationNeeded
}
\]

**中文业务释义：** 没有代码变化 ≠ 不需要重新验证生产可靠性。

可以建立：

```text
scheduled_benchmark_run    # 中文：周期性Benchmark

policy_change_triggered_run    # 中文：法规更新触发Benchmark

critical_incident_triggered_run    # 中文：重大事故后强制Benchmark

model_change_triggered_run    # 中文：模型变化触发Benchmark

rule_change_triggered_run    # 中文：规则变化触发对应切片Benchmark
```

---

# 五十三、核心心智模型 ㉕
# `PreviouslyPassed` 不等于 `AlwaysPassed`

\[
\boxed{
PastReleasePass
\neq
PermanentProductionApproval
}
\]

**中文业务释义：** 过去通过 Release Gate ≠ 永久获得生产资格；关键组件和业务环境变化后必须重新验证。

---

# 五十四、Multi-tenant Isolation
## 如果面向多个组织使用怎么办？

如果系统服务：

> 多个采购单位、代理机构或不同组织，

至少需要隔离：

```text
tenant_id    # 中文：组织 / 租户标识

project_data_scope    # 中文：项目数据访问边界

policy_overlay_scope    # 中文：组织允许使用的地方政策 / 内部规则范围

role_scope    # 中文：用户角色仅在本组织有效

audit_scope    # 中文：审计人员可查看的组织范围

storage_scope    # 中文：文件和证据存储隔离范围
```

---

# 五十五、核心心智模型 ㉖
# `SharedModel` 不等于 `SharedData`

\[
\boxed{
SharedModelService
\neq
SharedProjectData
}
\]

**中文业务释义：** 多组织可以共享同一模型服务 ≠ 项目文件、Finding、人工结论和审计数据可以互相访问。

---

# 五十六、Disaster Recovery
## 灾备要保护什么？

至少保护：

```text
project_state    # 中文：项目审查状态

evidence_store    # 中文：采购文件和证据

policy_registry    # 中文：法规政策注册表

rule_registry    # 中文：规则版本库

audit_log    # 中文：审计事件

release_manifests    # 中文：生产发布包

human_review_records    # 中文：人工复核结论
```

模型权重本身：

> 通常可以从受控仓库重新部署，

但：

> 业务状态和审计记录丢失可能更严重。

---

# 五十七、核心心智模型 ㉗
# `ModelBackup` 不等于 `BusinessRecovery`

\[
\boxed{
ModelBackup
\neq
BusinessContinuity
}
\]

**中文业务释义：** 备份了模型权重 ≠ 能恢复政府采购合规业务；项目状态、法规版本、Finding、人工结论和审计同样必须可恢复。

---

# 五十八、Recovery Objectives
## 恢复目标

工程上可以定义：

```text
RTO    # 中文：Recovery Time Objective，系统故障后目标恢复时间

RPO    # 中文：Recovery Point Objective，允许丢失的数据时间窗口
```

具体数值：

> 应根据业务连续性要求和组织风险治理设定，不在课程中写死。

---

# 五十九、核心心智模型 ㉘
# `Availability` 不等于 `Recoverability`

\[
\boxed{
HighAvailability
\neq
DisasterRecoverability
}
\]

**中文业务释义：** 平时可用性高 ≠ 发生严重故障后一定能够恢复；灾备和恢复演练必须单独验证。

---

# 六十、生产演练
## 不要等真的出事故才第一次回滚

建议定期演练：

```text
rollback_drill    # 中文：版本回滚演练

policy_snapshot_restore_drill    # 中文：法规快照恢复演练

audit_recovery_drill    # 中文：审计记录恢复演练

human_queue_failover_drill    # 中文：人工复核服务故障切换演练

safe_mode_drill    # 中文：安全模式切换演练

disaster_restore_drill    # 中文：灾备恢复演练
```

---

# 六十一、核心心智模型 ㉙
# `UntestedRecoveryPlan` 只是文档

\[
\boxed{
RecoveryPlan
+
NoDrill
\neq
RecoveryCapability
}
\]

**中文业务释义：** 写了恢复方案但从未演练 ≠ 真正具备恢复能力。

---

# 六十二、Human Override
## 人工能否推翻系统？

可以，但不能：

> 无痕迹改结论。

建议：

```text
override_id    # 中文：人工覆盖记录

finding_id    # 中文：被覆盖Finding

old_state    # 中文：覆盖前状态

new_state    # 中文：人工修改后的状态

reviewer_role    # 中文：复核人员角色

reason_code    # 中文：覆盖原因

evidence_refs    # 中文：支持人工覆盖的证据

created_at    # 中文：覆盖时间
```

---

# 六十三、核心心智模型 ㉚
# `HumanOverride` 必须可审计

\[
\boxed{
HumanOverride
\Rightarrow
Reason
+
Evidence
+
Identity
+
Time
}
\]

**中文业务释义：** 人工覆盖自动结论 ⇒ 必须记录理由 + 证据 + 操作者身份 + 时间。

---

# 六十四、Production Policy
## 哪些结论允许自动，哪些必须人工？

可以建立：

```text
AUTO_ALLOWED    # 中文：满足充分证据和低风险条件时允许自动形成结论

AUTO_WITH_SAMPLE_REVIEW    # 中文：允许自动，但按治理策略抽样人工复核

HUMAN_CONFIRM_REQUIRED    # 中文：必须人工确认后才能进入正式报告

HUMAN_ONLY    # 中文：系统只能整理证据，不得自动形成最终决定
```

具体映射：

> 应由组织根据风险、法务责任、业务影响和Benchmark表现配置。

---

# 六十五、核心心智模型 ㉛
# `AutomationPolicy` 应独立于模型 Prompt

\[
\boxed{
AutomationPolicy
\neq
PromptInstruction
}
\]

**中文业务释义：** 哪类事项允许自动化属于系统治理策略，不应只写在 Prompt 里；必须结构化、版本化并可审计。

---

# 六十六、Report Versioning
## 报告也必须版本化

当采购文件更正、人工结论变化或规则更新触发重审后：

```text
report_id    # 中文：报告逻辑标识

report_version    # 中文：报告版本

supersedes_report_version    # 中文：替代的上一版本

source_review_snapshot_id    # 中文：本报告绑定的审查快照

generated_at    # 中文：生成时间

status    # 中文：草稿 / 正式 / 已被替代
```

所以：

\[
\boxed{
UpdatedReview
\Rightarrow
NewReportVersion
}
\]

**中文业务释义：** 审查结果发生正式变化 ⇒ 应生成新的报告版本，而不是静默覆盖旧报告。

---

# 六十七、核心心智模型 ㉜
# `HistoricalReport` 不能被“修没了”

\[
\boxed{
AuditHistory
\Rightarrow
AppendOnlyChangeRecord
}
\]

**中文业务释义：** 审计历史 ⇒ 应保留可追踪的追加式变更记录；旧报告和旧Finding即使被新版本替代，也应能够审计回放。

---

# 六十八、Production Manifest
## 最终项目审查必须留下什么版本信息？

每个正式审查结果建议绑定：

```text
project_review_id    # 中文：项目审查标识

system_release_id    # 中文：系统发布版本

dataset_snapshot_id    # 中文：采购数据快照

policy_snapshot_id    # 中文：法规政策快照

rule_bundle_version    # 中文：规则包版本

legal_rag_index_version    # 中文：法规RAG索引版本

model_version_id    # 中文：合规模型版本

agent_version    # 中文：Agent版本

tool_registry_version    # 中文：工具注册表版本

benchmark_snapshot_id    # 中文：该发布版本对应的Benchmark

report_version    # 中文：报告版本

started_at    # 中文：审查开始时间

completed_at    # 中文：审查完成时间
```

---

# 六十九、核心心智模型 ㉝
# `Reproducibility` 是生产能力，不只是科研习惯

\[
\boxed{
ProductionReproducibility
=
PinnedVersions
+
ImmutableArtifacts
+
AuditTrace
}
\]

**中文业务释义：** 生产可复现 = 固定版本 + 不可变制品 + 审计轨迹。

---

# 七十、最终验收
## `ProcurementLM_V1.0` 到底什么时候算真正交付？

至少要回答：

```text
Can ingest real procurement files?
# 中文：能否稳定接收真实PDF、Word、表格和附件？

Can preserve document/version evidence?
# 中文：能否保存采购文件版本和精确证据？

Can cover D01-D22?
# 中文：二十二项规则是否有明确覆盖状态？

Can distinguish rules, calculation, RAG and semantic judgment?
# 中文：不同问题是否交给正确组件？

Can resolve policy time and jurisdiction?
# 中文：法规时点和辖区是否可解析？

Can abstain and escalate?
# 中文：证据不足时是否会正确弃权和转人工？

Can survive tool failure?
# 中文：工具失败时是否安全降级？

Can produce evidence-grounded reports?
# 中文：报告是否完全来自已验证状态？

Can hot-update rules and policies?
# 中文：规则和法规是否可以独立热更新？

Can rollback?
# 中文：生产版本是否能完整回滚？

Can audit every important decision?
# 中文：关键结论是否可追溯？

Can detect production drift?
# 中文：能否发现数据、法规、市场和系统行为漂移？

Can turn failures into permanent tests?
# 中文：生产失败是否会沉淀为长期Benchmark / Regression资产？
```

---

# 七十一、核心心智模型 ㉞
# `FeatureComplete` 不等于 `ProductionComplete`

\[
\boxed{
FeatureComplete
\neq
ProductionComplete
}
\]

**中文业务释义：** 功能都做完了 ≠ 生产系统真正完成；还必须具备发布、监控、回滚、审计、权限、反馈和恢复能力。

---

# 七十二、最终系统目录
## `ProcurementLM_V1.0`

```text
ProcurementLM_V1.0/
# 中文：政府采购合规智能体最终生产系统根目录

├── product_spec/
│   # 中文：产品边界、责任边界和风险治理
│   └── ProcurementComplianceProductSpec_V1/    # 中文：产品目标与系统边界产物
│
├── policy_registry/
│   # 中文：法规政策注册表和版本体系
│   └── ProcurementPolicyRegistry_V1/    # 中文：法规政策注册表产物
│
├── document_schema/
│   # 中文：采购文件业务Schema、Clause、Requirement和Evidence结构
│   └── ProcurementDocumentSchema_V1/    # 中文：采购文件业务结构产物
│
├── rules/
│   # 中文：专项整治D01-D22及各业务域规则
│   ├── ProcurementDiscrimination22RuleSet_V1/    # 中文：附件9二十二项规则工程化产物
│   ├── ProcurementQualificationCompliance_V1/    # 中文：资格条件合规产物
│   ├── ProcurementTechnicalCompliance_V1/    # 中文：技术参数合规产物
│   ├── ProcurementScoringCompliance_V1/    # 中文：评分标准合规产物
│   ├── ProcurementPolicyCompliance_V1/    # 中文：政府采购政策合规产物
│   └── ProcurementCompetitionCompliance_V1/    # 中文：采购方式、竞争与异常低价合规产物
│
├── data_pipeline/
│   # 中文：PDF / Word / OCR / 表格 / 章节 / 证据数据工程
│   └── ProcurementComplianceDataset_V1/    # 中文：采购文件合规数据工程产物
│
├── engine/
│   # 中文：Rules + Calculator + Policy Resolver + Legal RAG + LLM混合引擎
│   └── ProcurementComplianceEngine_V1/    # 中文：混合合规引擎产物
│
├── legal_rag/
│   # 中文：法规版本、时间、辖区、冲突、例外和Citation Support
│   └── ProcurementLegalRAG_V1/    # 中文：法规RAG与时间/辖区推理产物
│
├── model/
│   # 中文：经过Hard Case、Counterfactual和Abstention训练的合规模型
│   └── ProcurementComplianceLM_V1-RC/    # 中文：合规模型发布候选产物
│
├── agent/
│   # 中文：多轮任务、工具、状态、人工复核和报告编排
│   └── ProcurementComplianceAgent_V1/    # 中文：合规Agent工作流产物
│
├── benchmark/
│   # 中文：Gold Benchmark、Red Team和Release Gate
│   └── ProcurementComplianceBench_V1/    # 中文：Gold Benchmark、Red Team与Release Gate产物
│
├── release/
│   # 中文：生产发布包、灰度和回滚
│   ├── manifests/    # 中文：不可变Release Manifest
│   ├── canary/    # 中文：灰度发布配置
│   ├── rollback/    # 中文：回滚包和验证脚本
│   └── approvals/    # 中文：发布审批记录
│
├── operations/
│   # 中文：生产监控、告警、事故、安全模式和灾备
│   ├── monitoring/    # 中文：基础设施、模型、合规、法规和Agent监控
│   ├── alerts/    # 中文：关键告警
│   ├── incidents/    # 中文：事故处理和影响分析
│   ├── safe_mode/    # 中文：安全降级模式
│   └── disaster_recovery/    # 中文：灾备和恢复演练
│
├── governance/
│   # 中文：权限、职责分离、人工覆盖和豁免治理
│   ├── rbac/    # 中文：角色权限
│   ├── separation_of_duties/    # 中文：职责分离
│   ├── human_override/    # 中文：人工覆盖记录
│   └── waivers/    # 中文：发布豁免
│
├── feedback/
│   # 中文：生产反馈、Gold裁决、Hard Case和数据飞轮
│   ├── triage/    # 中文：生产反馈分流
│   ├── adjudication/    # 中文：专家裁决
│   ├── regression_cases/    # 中文：永久回归案例
│   └── training_candidates/    # 中文：训练候选数据
│
├── audit/
│   # 中文：决策、工具、版本、人工和发布的完整审计
│   ├── decision_trace/    # 中文：Finding决策轨迹
│   ├── execution_trace/    # 中文：Agent / 工具执行轨迹
│   ├── release_trace/    # 中文：发布和回滚轨迹
│   └── access_trace/    # 中文：访问和权限操作轨迹
│
└── manifest.json
    # 中文：ProcurementLM_V1.0全系统组件、版本、状态和验收结果总清单
```

---

# 七十三、Final System Manifest 第一版

```text
system_name    # 中文：系统名称ProcurementLM_V1.0

system_release_id    # 中文：当前生产发布版本

release_state    # 中文：PASS / PASS_WITH_WAIVER / BLOCKED等

product_spec_version    # 中文：产品边界版本

dataset_schema_version    # 中文：采购数据Schema版本

parser_version    # 中文：文档解析器版本

rule_bundle_version    # 中文：规则包版本

policy_snapshot_id    # 中文：法规政策快照

legal_rag_index_version    # 中文：法规RAG索引版本

model_version_id    # 中文：合规模型版本

agent_version    # 中文：Agent版本

tool_registry_version    # 中文：工具注册表版本

benchmark_snapshot_id    # 中文：最近一次通过的Benchmark快照

release_gate_id    # 中文：发布门决策标识

runtime_image_version    # 中文：运行环境版本

application_code_version    # 中文：应用代码版本

monitoring_policy_version    # 中文：监控和告警策略版本

rbac_policy_version    # 中文：权限策略版本

rollback_target_release_id    # 中文：默认回滚目标版本

created_at    # 中文：Manifest生成时间
```

---

# 七十四、Production Review Record Schema 第一版

```text
project_review_id    # 中文：项目审查标识

project_id    # 中文：采购项目

tenant_id    # 中文：所属组织 / 租户，如适用

system_release_id    # 中文：执行本次审查的生产版本

dataset_snapshot_id    # 中文：采购数据快照

policy_snapshot_id    # 中文：法规快照

rule_bundle_version    # 中文：规则包版本

model_version_id    # 中文：模型版本

agent_version    # 中文：Agent版本

coverage_state    # 中文：审查覆盖状态

finding_ids    # 中文：正式Finding集合

human_review_ids    # 中文：人工复核记录

report_id    # 中文：最终报告

audit_trace_id    # 中文：完整审计轨迹

review_state    # 中文：完整 / 部分 / 重开 / 关闭等状态

started_at    # 中文：开始时间

completed_at    # 中文：完成时间
```

---

# 七十五、Rule Update Record Schema 第一版

```text
rule_update_id    # 中文：规则更新记录

rule_id    # 中文：D01-D22或其他规则身份

from_version    # 中文：旧版本

to_version    # 中文：新版本

change_type    # 中文：逻辑修复 / 例外补充 / 文案调整等变更类型

change_reason    # 中文：修改原因

source_refs    # 中文：法规、专项整治或业务依据

affected_benchmark_slices    # 中文：必须回归的Benchmark切片

regression_report_id    # 中文：回归测试报告

approver_roles    # 中文：批准角色

activation_time    # 中文：生产激活时间

rollback_version    # 中文：回滚目标规则版本
```

---

# 七十六、Policy Update Record Schema 第一版

```text
policy_update_id    # 中文：法规政策更新记录

policy_id    # 中文：法规政策逻辑身份

new_policy_version_id    # 中文：新法规版本

official_source_ref    # 中文：官方来源

promulgation_date    # 中文：发布 / 公布日期

effective_from    # 中文：开始生效日期

jurisdiction_scope    # 中文：适用地区 / 预算级次 / 事项范围

supersedes_refs    # 中文：替代 / 修改的旧版本

transition_rule_refs    # 中文：过渡条款

legal_rag_index_version    # 中文：更新后的法规索引版本

regression_report_id    # 中文：法规回归测试报告

new_policy_snapshot_id    # 中文：发布的新法规快照

activation_policy    # 中文：哪些新审查开始使用该快照
```

---

# 七十七、Incident Record Schema 第一版

```text
incident_id    # 中文：生产事故标识

severity    # 中文：工程影响等级

detected_at    # 中文：发现时间

detected_by    # 中文：监控 / 用户 / 人工审计等发现来源

affected_release_ids    # 中文：受影响发布版本

affected_component    # 中文：模型 / Rule / Policy / RAG / Agent / Report等组件

failure_mode    # 中文：具体失败模式

safe_mode_state    # 中文：是否进入安全模式

rollback_release_id    # 中文：如已回滚，目标版本

affected_review_ids    # 中文：已识别受影响项目

reopen_required    # 中文：是否需要重开项目审查

root_cause    # 中文：根因

fix_version    # 中文：修复版本

regression_case_ids    # 中文：新增永久回归案例

closed_at    # 中文：事故关闭时间
```

---

# 七十八、本阶段最重要的 40 个核心心智模型

> **心智模型 ①：`DeploymentSuccess ≠ ProductionReadiness`。部署成功不是生产就绪。**

> **心智模型 ②：`ProcurementLM_V1.0 ≠ ModelCheckpoint`。最终产品不是单一模型文件。**

> **心智模型 ③：`ModelVersion ≠ SystemVersion`。模型版本不等于系统版本。**

> **心智模型 ④：`ReleasedBundle ⇒ Immutable`。已发布版本必须不可变。**

> **心智模型 ⑤：`ProductionServing ≠ ModelLoading`。生产服务不等于模型加载。**

> **心智模型 ⑥：`Release ≠ Rollout`。允许发布和全面上线不是一回事。**

> **心智模型 ⑦：`ShadowPass ≠ CanaryPass`。影子验证通过不等于真实灰度通过。**

> **心智模型 ⑧：`Rollback = Model + Rules + Policy + RAG + Agent + SchemaCompatibility`。回滚是整套系统回滚。**

> **心智模型 ⑨：`RuleUpdate ≠ ModelRetraining`。规则热更新不需要默认重训模型。**

> **心智模型 ⑩：`RuleHotUpdate ≠ UnreviewedHotPatch`。热更新不等于跳过测试。**

> **心智模型 ⑪：`PolicyUpdate ≠ ModelRetraining`。法规更新不应依赖模型重训。**

> **心智模型 ⑫：`ProjectReview ⇒ PinnedPolicySnapshot`。正式审查应绑定法规快照。**

> **心智模型 ⑬：`LatestPolicyAvailable ≠ AutomaticMidReviewSwitch`。新规可用不代表正在审查的项目自动换规则。**

> **心智模型 ⑭：`ChangeType → RequiredRegressionSuite`。变更类型决定回归范围。**

> **心智模型 ⑮：`HTTP200 ≠ ComplianceHealthy`。接口成功不等于合规健康。**

> **心智模型 ⑯：`FastResponse ≠ ReliableReview`。快不等于可靠。**

> **心智模型 ⑰：`CriticalIntegrityFailure ⇒ SafeMode`。关键完整性故障应进入安全模式。**

> **心智模型 ⑱：`GracefulDegradation = ReducedCapability + ExplicitDisclosure`。降级必须缩减能力并显式告知。**

> **心智模型 ⑲：`ServiceRestored ≠ IncidentClosed`。服务恢复不等于事故关闭。**

> **心智模型 ⑳：`NoVersionTrace ⇒ NoReliableImpactAnalysis`。没有版本追踪就无法可靠分析事故影响。**

> **心智模型 ㉑：`OneSuperAdmin ≠ GoodGovernance`。超级管理员不是良好治理。**

> **心智模型 ㉒：`EditPermission ≠ ActivationPermission`。能编辑不等于能激活生产。**

> **心智模型 ㉓：`Auditability = TraceableDecision + VersionedInputs + ControlledChanges`。可审计性是决策、输入和变更的整体可追踪。**

> **心智模型 ㉔：`ProductionFeedback ≠ ImmediateTrainingData`。生产反馈不能直接回灌训练。**

> **心智模型 ㉕：`FailureSource → CorrectComponentFix`。错误来自哪一层就修哪一层。**

> **心智模型 ㉖：`CriticalProductionFailure ⇒ PermanentRegressionCase`。关键生产错误必须沉淀永久回归案例。**

> **心智模型 ㉗：`FeedbackLoop ≠ BlindDataRecycling`。反馈闭环不是无脑回收训练数据。**

> **心智模型 ㉘：`ObservedPerformanceShift ≠ ModelDriftOnly`。表现漂移不一定是模型问题。**

> **心智模型 ㉙：`NoCodeChange ≠ NoRevalidationNeeded`。没有代码变化也可能需要重新验证。**

> **心智模型 ㉚：`PastReleasePass ≠ PermanentProductionApproval`。过去通过发布门不等于永久有效。**

> **心智模型 ㉛：`SharedModelService ≠ SharedProjectData`。共享模型服务不等于共享项目数据。**

> **心智模型 ㉜：`ModelBackup ≠ BusinessContinuity`。模型备份不等于业务连续性。**

> **心智模型 ㉝：`HighAvailability ≠ DisasterRecoverability`。高可用不等于灾备可恢复。**

> **心智模型 ㉞：`RecoveryPlan + NoDrill ≠ RecoveryCapability`。没演练的恢复方案不是恢复能力。**

> **心智模型 ㉟：`HumanOverride ⇒ Reason + Evidence + Identity + Time`。人工覆盖必须可审计。**

> **心智模型 ㊱：`AutomationPolicy ≠ PromptInstruction`。自动化权限策略不能只写在Prompt里。**

> **心智模型 ㊲：`UpdatedReview ⇒ NewReportVersion`。审查变化应产生新报告版本。**

> **心智模型 ㊳：`AuditHistory ⇒ AppendOnlyChangeRecord`。历史审计应保留追加式变更轨迹。**

> **心智模型 ㊴：`ProductionReproducibility = PinnedVersions + ImmutableArtifacts + AuditTrace`。生产可复现来自版本、制品和审计。**

> **心智模型 ㊵：`FeatureComplete ≠ ProductionComplete`。功能做完不等于生产交付完成。**

---

# 七十九、把整个 `ProcurementLM_V1.0` 压成一张最终工程图

```text
Authoritative Procurement Files
# 中文：真实采购文件、附件、澄清、更正和合同材料
↓
ProcurementComplianceDataset_V1
# 中文：结构化Clause、Requirement、Evidence和版本事实
↓
Policy Registry + ProcurementLegalRAG_V1
# 中文：法规版本、时点、辖区、冲突、例外和Citation Support
↓
D01-D22 + Domain Rule Sets
# 中文：差别歧视、资格、技术、评分、政策、竞争等规则体系
↓
ProcurementComplianceEngine_V1
# 中文：Rules + Calculator + Policy Resolver + Legal RAG + LLM混合判断
↓
ProcurementComplianceLM_V1-RC
# 中文：训练过Hard Case、Counterfactual、Evidence和Abstention的语义模型
↓
ProcurementComplianceAgent_V1
# 中文：Planner + State + Tools + Human Review + Coverage + Report
↓
ProcurementComplianceBench_V1
# 中文：D01-D22 Gold、Hard Cases、Counterfactual、Red Team和Release Gate
↓
Immutable Release Bundle
# 中文：固定模型、规则、法规快照、RAG、Agent、工具和代码版本
↓
Shadow → Canary → Production
# 中文：影子验证 → 灰度发布 → 正式全量
↓
Monitoring + Audit + Safe Mode
# 中文：生产监控、完整审计和安全降级
↓
Rule / Policy Hot Update
# 中文：规则与法规独立热更新并经过回归
↓
Incident / Rollback / Reopen
# 中文：事故响应、整套回滚和受影响项目重审
↓
Production Feedback → Gold → Benchmark → Fix → Regression
# 中文：生产失败沉淀成永久测试和受控数据飞轮
↓
ProcurementLM_V1.0
# 中文：真正可长期运行、可更新、可回滚、可审计、可治理的政府采购合规智能体
```

---

# 八十、整个第十一课的 16 阶段最终串联

```text
Stage 1    # 中文：第1阶段
ProcurementComplianceProductSpec_V1
# 中文：定义产品目标、责任边界和Finding契约
↓
Stage 2    # 中文：第2阶段
ProcurementPolicyRegistry_V1
# 中文：建立法规版本、状态、辖区和Policy Snapshot
↓
Stage 3    # 中文：第3阶段
ProcurementDocumentSchema_V1
# 中文：把采购文件还原为可审查业务结构
↓
Stage 4    # 中文：第4阶段
ProcurementDiscrimination22RuleSet_V1
# 中文：附件9二十二项差别歧视规则工程化
↓
Stage 5    # 中文：第5阶段
ProcurementQualificationCompliance_V1
# 中文：资格条件和市场准入合规
↓
Stage 6    # 中文：第6阶段
ProcurementTechnicalCompliance_V1
# 中文：技术参数、品牌、专利、检测、认证、授权和样品合规
↓
Stage 7    # 中文：第7阶段
ProcurementScoringCompliance_V1
# 中文：评分标准、量化、业绩、奖项、人员和主观分合规
↓
Stage 8    # 中文：第8阶段
ProcurementPolicyCompliance_V1
# 中文：本国产品、中小企业、绿色采购、创新、进口产品等政策合规
↓
Stage 9    # 中文：第9阶段
ProcurementCompetitionCompliance_V1
# 中文：采购方式、竞争充分性和异常低价检查
↓
Stage 10    # 中文：第10阶段
ProcurementComplianceDataset_V1
# 中文：PDF / Word / 表格 / OCR / Clause ID / Evidence Span数据工程
↓
Stage 11    # 中文：第11阶段
ProcurementComplianceEngine_V1
# 中文：Rules + LLM + RAG + Calculator混合合规引擎
↓
Stage 12    # 中文：第12阶段
ProcurementLegalRAG_V1
# 中文：法规时间、辖区、版本和引用支持
↓
Stage 13    # 中文：第13阶段
ProcurementComplianceLM_V1-RC
# 中文：Hard Case、Counterfactual、Evidence和Abstention训练
↓
Stage 14    # 中文：第14阶段
ProcurementComplianceAgent_V1
# 中文：多轮任务、工具、状态、人工和报告工作流
↓
Stage 15    # 中文：第15阶段
ProcurementComplianceBench_V1
# 中文：Gold Benchmark、Red Team和Release Gate
↓
Stage 16    # 中文：第16阶段
ProcurementLM_V1.0
# 中文：生产发布、热更新、监控、回滚、审计、反馈闭环和长期运营
```

---

# 八十一、整个第十一课最终 16 条超级心智模型

如果最后只保留 16 条：

> **① `AIProject ≠ ModelProject`。政府采购AI项目不是模型项目。**

> **② `LatestPolicy ≠ ApplicablePolicy`。最新政策不等于当前项目适用政策。**

> **③ `TextChunk ≠ BusinessClause`。文本块不等于可审查业务条款。**

> **④ `22项 ≠ 22个关键词`。专项整治规则不能退化成关键词。**

> **⑤ `CapabilityRequirement ≠ MarketAccessBarrier`。能力要求与准入壁垒必须区分。**

> **⑥ `TechnicalSpecificity ≠ TechnicalDiscrimination`。技术要求具体不自动等于技术歧视。**

> **⑦ `ScoringPreference ≠ UnboundedSubjectivity`。评分可以评价优劣，但不能失去可观察、可验证边界。**

> **⑧ `PolicyPreference ≠ IllegalDiscrimination`。依法实施政策支持不等于采购人自行差别待遇。**

> **⑨ `CompetitionProblem ≠ LowSupplierCountOnly`。竞争问题不能只看供应商数量。**

> **⑩ `ParsedText ≠ ReliableComplianceFact`。提取到文字不等于得到可靠合规事实。**

> **⑪ `OneModel ≠ ComplianceSystem`。一个LLM不是完整合规系统。**

> **⑫ `RelevantLaw ≠ ApplicableLaw`。相关法规不等于适用法规。**

> **⑬ `ComplianceTraining ≠ KeywordMemorization`。合规训练不是关键词记忆。**

> **⑭ `Agent ≠ LLMWithLongPrompt`。Agent不是长Prompt模型。**

> **⑮ `OverallAccuracy ≠ ComplianceReliability`。总体准确率不是合规可靠性。**

> **⑯ `DeploymentSuccess ≠ ProductionReadiness`。部署成功不是生产就绪。**

---

# 八十二、整套系统的 Master Mental Model

整个第十一课最终可以压缩成：

\[
\boxed{
ProcurementComplianceAI
=
ApplicableRules
+
BusinessContext
+
Evidence
+
DeterministicComputation
+
SemanticReasoning
+
Uncertainty
+
HumanGovernance
+
ProductionGovernance
}
\]

**中文业务释义：** 政府采购合规 AI = 当前适用规则 + 真实业务上下文 + 原文和法源证据 + 确定性计算 + 语义判断 + 不确定性管理 + 人工治理 + 生产治理。

如果再进一步压缩：

\[
\boxed{
ReliableAI
=
CorrectWhenKnown
+
AbstainWhenUnknown
+
EscalateWhenHighRisk
+
TraceEverything
+
RollbackWhenWrong
}
\]

**中文业务释义：** 可靠 AI = 知道时正确判断 + 不知道时拒绝武断 + 高风险时升级人工 + 全过程可追踪 + 出错时能够回滚。

---

# 八十三、最终交付检查清单

```text
[ ] Product Boundary
# 中文：产品边界和人工责任已经明确

[ ] D01-D22 Rule Coverage
# 中文：22项规则均有实现、测试和Coverage状态

[ ] Document Parsing Quality Gate
# 中文：文档解析、表格、OCR和Evidence达到审查门槛

[ ] Policy Registry
# 中文：法规版本、生效、废止、辖区和快照可追踪

[ ] Legal RAG
# 中文：法规检索可以处理版本、时间、辖区、例外和Citation Support

[ ] Deterministic Calculator
# 中文：明确公式由可重放计算器执行

[ ] Compliance LM
# 中文：模型经过Hard Case、Counterfactual和Abstention训练

[ ] Hybrid Engine
# 中文：Rules、Calculator、RAG、LLM和Evidence职责分离

[ ] Agent Workflow
# 中文：Planner、State、Tools、Human和Coverage完整

[ ] Gold Benchmark
# 中文：D01-D22、Hard Cases和关键切片有Gold评测

[ ] Red Team
# 中文：提示注入、旧法规、错误辖区、OCR、工具失败均有测试

[ ] Release Gate
# 中文：Model / Rule / Legal / Agent / RedTeam五个门全部治理

[ ] Immutable Release Bundle
# 中文：生产版本可完整重放

[ ] Canary + Rollback
# 中文：灰度和整套回滚路径已验证

[ ] Monitoring + Alerts
# 中文：基础设施、模型、合规、法规和Agent都可监控

[ ] Audit + RBAC
# 中文：关键访问、人工覆盖、规则激活和发布都可审计

[ ] Rule / Policy Hot Update
# 中文：规则和法规能够独立更新并经过回归

[ ] Incident Response
# 中文：安全模式、影响分析、重开项目和事故闭环可执行

[ ] Feedback Flywheel
# 中文：生产错误能沉淀成Gold、Benchmark、Regression和训练候选

[ ] Disaster Recovery
# 中文：项目状态、审计、法规、规则和人工记录具备恢复能力
```

---

# 八十四、脑中最后只留一句

> **`ProcurementLM_V1.0` 的真正交付标准，不是“模型已经部署”“接口已经能返回合规结果”，而是这套系统已经形成完整的版本化事实、D01-D22规则、法规快照、Legal RAG、确定性计算、语义模型、Agent、人工复核、Gold Benchmark、Red Team、Release Gate、灰度、回滚、监控、审计、热更新和反馈闭环；任何一个正式结论都能回到原始采购证据和适用法规，任何一次系统变化都能说明改了什么、测试了什么、谁批准、何时激活，任何一次生产故障都能限制影响、回滚版本、找出受影响项目并沉淀永久回归案例。到这一步，才叫真正从“一个AI Demo”走到了“政府采购合规生产系统”。**

---

# 第十一课 · 第 16 阶段掌握测试

现在不回看正文，你应该能够解释：

```text
Deployment Success为什么不等于Production Readiness？
# 中文：接口能跑以后还缺哪些治理能力？

ProcurementLM_V1.0为什么不等于一个Model Checkpoint？
# 中文：最终系统由哪些组件组成？

Model Version为什么不等于System Version？
# 中文：为什么规则、法规、RAG、Agent变化也会改变系统行为？

Release Bundle为什么必须Immutable？
# 中文：怎样保证半年后可以重放当时系统环境？

Production Serving为什么不等于Model Loading？
# 中文：认证、状态、规则、RAG、人工和审计分别是什么角色？

DEV / TEST / STAGING / CANARY / PRODUCTION分别解决什么？
# 中文：为什么不能开发机直接全量生产？

Release和Rollout有什么区别？
# 中文：为什么具备发布资格不等于立即全量？

Shadow和Canary有什么区别？
# 中文：为什么Shadow通过还不能证明真实灰度安全？

Rollback为什么必须回滚整套Bundle？
# 中文：只回滚模型会遗漏哪些规则 / 法规 / Agent变化？

Rule Hot Update为什么不等于Model Retraining？
# 中文：规则更新怎样独立完成？

Rule Hot Update为什么仍然必须过Benchmark？
# 中文：热更新为什么不能理解成“直接改线上文件”？

Policy Hot Update怎样运行？
# 中文：官方来源、版本、生效时间、辖区、RAG索引和Snapshot怎样更新？

Project Review为什么必须Pin Policy Snapshot？
# 中文：审查过程中法规库更新为什么不能偷偷改变结论？

Latest Policy Available为什么不等于Automatic Mid-review Switch？
# 中文：新规发布后正在审查项目怎样处理？

Change Classification有哪些类型？
# 中文：Model、Rule、Policy、RAG、Parser、Agent、Tool、Report、Infra分别意味着什么？

Change Type为什么决定Regression Scope？
# 中文：为什么Rule Change和Agent Change不能只跑同一套测试？

HTTP 200为什么不等于Compliance Healthy？
# 中文：法规过期、Coverage下降、人工作业堵塞时接口可能仍然正常吗？

Production Metrics至少有哪些层？
# 中文：Infra、Model、Compliance、Legal、Agent分别监控什么？

SLO为什么不只是Latency？
# 中文：Coverage、Policy Freshness、Audit Write、Human Review为什么也是服务目标？

哪些事件应该触发Critical Alert？
# 中文：Silent Tool Failure、Coverage Overclaim、Policy Version Mismatch为什么危险？

Safe Mode怎样设计？
# 中文：法规RAG故障时为什么可能禁止形成正式Finding？

Graceful Degradation为什么必须Explicit Disclosure？
# 中文：降级后为什么不能继续输出“完整审查”？

Incident Response完整流程是什么？
# 中文：Detect、Contain、Safe Mode、Rollback、Human Review、Regression怎样串起来？

Service Restored为什么不等于Incident Closed？
# 中文：为什么还需要影响项目分析和根因闭环？

为什么每个Review都要保存完整版本指纹？
# 中文：事故发生后怎样找出受影响项目？

RBAC为什么重要？
# 中文：采购审查、法规、规则、模型、发布和审计权限为什么不能混在一起？

One Super Admin为什么不是Good Governance？
# 中文：职责分离解决什么风险？

Edit Permission为什么不等于Activation Permission？
# 中文：为什么能修改规则的人不应必然有权上线规则？

Auditability为什么不是“多打日志”？
# 中文：Traceable Decision、Versioned Inputs和Controlled Changes分别是什么？

Production Feedback为什么不能立即回灌训练？
# 中文：为什么必须先复现、绑定证据、确认Policy Snapshot和专家裁决？

Failure Source为什么决定Correct Component Fix？
# 中文：OCR错、Calculator错、Legal RAG错、LLM错分别该修哪里？

为什么Critical Production Failure必须形成Permanent Regression Case？
# 中文：怎样防止同一问题下个版本再次出现？

Feedback Loop为什么不等于Blind Data Recycling？
# 中文：Train、Benchmark、Red Team、Holdout如何防止泄漏？

Drift有哪些类型？
# 中文：Document、Business、Policy、Market、Language、Tool和Model Behavior分别是什么？

Observed Performance Shift为什么不一定是Model Drift？
# 中文：法规和市场变化怎样影响表现？

No Code Change为什么也可能需要Revalidation？
# 中文：政策和业务环境变化为什么会让旧Release Gate失效？

Shared Model为什么不等于Shared Data？
# 中文：多组织部署如何保持项目数据隔离？

Model Backup为什么不等于Business Continuity？
# 中文：还必须恢复哪些状态、规则、法规和审计数据？

High Availability为什么不等于Disaster Recoverability？
# 中文：高可用和灾备有什么区别？

为什么恢复方案必须演练？
# 中文：Untested Recovery Plan为什么只是文档？

Human Override为什么必须Reason + Evidence + Identity + Time？
# 中文：怎样避免人工无痕改结论？

Automation Policy为什么不能只写在Prompt里？
# 中文：AUTO_ALLOWED、HUMAN_CONFIRM_REQUIRED等策略为什么必须版本化？

Updated Review为什么应该生成New Report Version？
# 中文：为什么不能静默覆盖历史报告？

Production Reproducibility怎样实现？
# 中文：Pinned Versions、Immutable Artifacts和Audit Trace怎样共同工作？

Feature Complete为什么不等于Production Complete？
# 中文：生产交付最后缺哪些运维和治理能力？

ProcurementLM_V1.0最终到底是什么？
# 中文：怎样从采购文件一路追溯到Finding、法规、人工、Benchmark、Release和生产运维？
```

如果这些能够完整解释：

\[
\boxed{
第十一课第16阶段真正掌握
}
\]

**中文业务释义：** 如果能够完整解释系统版本、Release Bundle、法规和规则热更新、灰度、回滚、监控、安全模式、事故响应、RBAC、反馈数据飞轮、漂移、灾备、人工覆盖和审计，并且知道“模型上线”与“生产系统就绪”之间究竟差了什么，就说明真正掌握了本阶段。

---

# 第十一课正式完成

\[
\boxed{
第十一课
=
16/16
}
\]

**中文业务释义：** 第十一课《`ProcurementLM V1.0` 政府采购合规智能体全流程实战》全部 16 个阶段完成。

整套课程：

\[
\boxed{
130/130
}
\]

**中文业务释义：** 从“机器学习到底在学习什么”，一直到最终 `ProcurementLM_V1.0` 的生产交付，整套 130 阶段课程正式完成。

最终交付物：

# `ProcurementLM_V1.0`

最终主线：

\[
\boxed{
AIProject
\rightarrow
DomainKnowledge
\rightarrow
StructuredData
\rightarrow
Rules
\rightarrow
CPT/SFT
\rightarrow
RAG
\rightarrow
Agent
\rightarrow
Benchmark
\rightarrow
ProductionGovernance
}
\]

**中文业务释义：** AI 项目定义 → 政府采购领域知识 → 结构化数据 → 合规规则 → CPT / SFT 领域训练 → 法规 RAG → Agent 工作流 → Gold Benchmark → 生产治理。

这就是从：

> **理解模型**

到：

> **训练模型**

再到：

> **构建政府采购合规 AI 系统**

最后到：

> **真正生产交付并长期运营**

的完整闭环。
