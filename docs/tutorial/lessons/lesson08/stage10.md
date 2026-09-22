# 第八课 · 第 10 阶段
# 真正训练 `ProcurementLM_V0.2`：端到端 CPT、评测、回归测试与 Release Gate
## 怎样把前 9 个阶段全部接成一个真正可运行、可复现、可审计、可回滚的 CPT 工程系统？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **CPTExperiment ≠ ModelRelease。训练跑完只是得到实验 Checkpoint，不代表模型可以发布。**
2. **ModelRelease ≠ WeightsOnly。真正模型版本必须包含 Tokenizer、配置、数据血缘、评测证据和 Release Manifest。**
3. **NoFrozenBaseline = NoReliableComparison。没有固定基线，就无法可靠证明模型到底变好还是变坏。**
4. **Scale amplifies Signal and Error。扩大训练规模会同时放大正确方向和错误配置，所以 Full Run 前必须先做 Pilot。**
5. **BestCheckpoint = MultiObjectiveDecision。最优发布 Checkpoint 不是 Loss 最低，而是领域收益、通用保持、成本和兼容性的综合折中。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `CPT` | CPT/继续预训练：在领域语料上继续执行预训练目标 |
| `Checkpoint` | 检查点：保存模型和训练状态以便恢复/发布 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `SFT` | 监督微调：用监督样本继续更新模型参数 |
| `Tokenizer` | 分词器：文本与 Token ID 之间的编码/解码组件 |
| `Regression` | 回归测试：更新后验证旧能力和关键切片没有退化 |

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

前 9 个阶段，我们已经分别解决了：

- CPT 到底在学什么；
- 什么样的领域 Corpus 才值得训练；
- Tokenizer 要不要改；
- Sequence、Context Length、Packing 和 Loss 怎样定义真实训练任务；
- Data Mixture 怎样分配训练预算；
- 怎样检测 Catastrophic Forgetting；
- 怎样通过 Replay、Regularization 和参数约束保持能力；
- Synthetic Data 与 Curriculum 怎样补覆盖而不是制造“假数据世界”；
- CPT、SFT、RAG、Agent 到底分别解决什么问题。

第 10 阶段不再增加一个孤立概念。

它要做的是：

> **把这些东西真正接成一条可以执行、可以停止、可以恢复、可以比较、可以发布的模型工程流水线。**

本阶段最终交付：

# `ProcurementLM_V0.2`

并正式完成第八课。

---

# 一、先锁死本阶段最重要的一句话

一次 CPT 训练成功跑完，只代表：

> **得到一个实验 Checkpoint。**

它不等于：

> **得到一个可以发布的模型。**

所以本阶段最重要的总边界是：

\[
\boxed{
CPTExperiment
\neq
ModelRelease
}
\]

真正的模型发布至少还需要：

\[
\boxed{
Reproducibility
+
Evaluation
+
RegressionControl
+
ArtifactCompleteness
+
ReleaseGate
+
Rollbackability
}
\]

也就是：

> **能复现、能评测、能证明没把旧能力弄坏、产物完整、通过发布门槛，而且出问题能回滚。**

---

# 二、核心心智模型 ①：Model Release 是“证据包”，不是一个 `model.safetensors`

很多人把模型发布理解成：

```text
训练结束
↓
保存权重
↓
上传模型
```

这远远不够。

一个真正可发布的模型至少应该能回答：

```text
它从哪个 Base Model 来？

用了哪个 Corpus Version？

用了哪个 Tokenizer Version？

Sequence Builder 是哪一版？

Mixture 怎么配的？

训练了多少 Effective Tokens？

选的是哪个 Checkpoint？

为什么选它？

CPT 后重新做了哪版 SFT？

领域能力涨了多少？

通用能力掉了多少？

Release Gate 为什么通过？

如果出问题，回滚到哪里？
```

所以：

\[
\boxed{
ModelArtifact
\neq
WeightsOnly
}
\]

更准确地说：

\[
\boxed{
ModelRelease
=
Weights
+
Tokenizer
+
Config
+
DataLineage
+
EvalBundle
+
ReleaseManifest
}
\]

---

# 三、端到端总流程：从 Domain Gap 到 `ProcurementLM_V0.2`

先给完整英文工程链，再逐步翻译。

```text
Failure Evidence
↓
Domain Gap Diagnosis
↓
CPT Go / No-Go
↓
Freeze Baseline
↓
Corpus Build & Benchmark Firewall
↓
Tokenizer Audit
↓
Sequence Construction
↓
Mixture & Replay Design
↓
Pilot CPT
↓
Checkpoint Evaluation
↓
Full CPT
↓
Forgetting / Retention Control
↓
Checkpoint Selection
↓
SFT on CPT Base
↓
Foundation + Behavior + Regression Evaluation
↓
Release Gate
↓
Release Bundle
↓
ProcurementLM_V0.2
```

中文解释：

```text
先从真实失败案例出发
↓
证明问题确实属于领域底座不足
↓
判断是否值得进入CPT
↓
冻结训练前基线模型和评测结果
↓
建设可训练Corpus并隔离未来Benchmark
↓
审计Tokenizer是否真的构成瓶颈
↓
定义Sequence、Context、Packing、Loss规则
↓
设计领域数据、Replay和各数据桶训练比例
↓
先做小规模Pilot验证路线
↓
周期性评测Checkpoint
↓
确认路线有效后再做正式CPT
↓
持续监控遗忘并动态调Retention
↓
从多个Checkpoint中选择最合适的领域底座
↓
在新底座上重新做SFT
↓
分别评测底座能力、任务行为和通用回归
↓
通过Release Gate
↓
打包完整模型发布资产
↓
形成ProcurementLM_V0.2
```

所以：

\[
\boxed{
TrainingPipeline
=
DecisionPipeline
+
ExecutionPipeline
+
EvidencePipeline
}
\]

训练流水线不只是“执行训练”。

它同时是一条：

> **技术决策链 + 计算执行链 + 证据链。**

---

# 四、Phase 0：先冻结 Baseline，不然以后根本不知道模型有没有变好

在任何新 CPT Run 开始之前，先冻结：

# Baseline
## 基线

至少包括：

```text
base_model_id

base_model_hash

tokenizer_version

baseline_domain_metrics

baseline_general_metrics

baseline_instruction_metrics

baseline_generation_config

baseline_eval_config
```

为什么？

因为如果 CPT 前后：

```text
Prompt变了
Decoding参数变了
评测集变了
Tokenizer变了
Scoring Rule变了
```

你就无法确定：

> 分数变化到底来自模型，还是来自评测条件变化。

所以：

\[
\boxed{
NoFrozenBaseline
=
NoReliableComparison
}
\]

---

# 五、核心心智模型 ②：Reproducibility 不是“我还记得大概怎么训的”

真正的：

# Reproducibility
## 可复现性

不是：

> “我大概记得用了 2e-5 学习率。”

而是至少冻结：

```text
Base Model Version

Tokenizer Version

Corpus Version

Sequence Builder Version

Mixture Policy Version

Training Config

Code Commit

Environment

Random Seed

Checkpoint Policy

Evaluation Config
```

可以把一次 Run 表示成：

\[
R
=
(
M_0,
T,
D,
S,
P,
C,
E
)
\]

其中：

- \(M_0\)：Base Model；
- \(T\)：Tokenizer；
- \(D\)：Corpus；
- \(S\)：Sequence / Sampling Policy；
- \(P\)：训练参数；
- \(C\)：代码与环境；
- \(E\)：评测协议。

所以：

\[
\boxed{
Reproducibility
=
VersionEverythingThatChangesOutcome
}
\]

注意：

> 固定 Seed 不代表所有 GPU / Kernel 场景都能做到逐 bit 完全一致。

工程目标首先是：

> **配置、数据、代码、环境和评测都可追溯，结果能够在合理误差内被重复验证。**

---

# 六、Phase 1：先做 Pilot CPT，不要一上来烧完整 Token Budget

如果正式计划：

```text
100B CPT tokens
```

不应该第一步就把 100B 全跑完。

先做：

# Pilot Run
## 小规模试验训练

例如只使用正式预算的一小部分，

主要验证：

```text
Data Loader是否正确

Tokenizer / Sequence是否兼容

Loss是否正常下降

Mixture是否符合配置

Replay是否真正进入训练

Checkpoint是否可恢复

Domain Metric是否有正向趋势

General Regression是否开始失控
```

Pilot 的目的不是：

> 得到最终最好模型。

而是：

\[
\boxed{
Pilot
=
ValidateTrainingHypothesis
}
\]

也就是：

> **验证整条训练假设值得继续放大。**

---

# 七、核心心智模型 ③：Scale Up 之前先证明 Direction Correct

一条错误路线：

```text
小规模已经看不到收益
↓
那就多训十倍看看
```

通常不是好工程。

因为规模放大会同时放大：

```text
计算成本
数据偏差
遗忘风险
错误配置
Benchmark污染
重复曝光
```

所以：

\[
\boxed{
Scale
放大的是
Signal
也放大
Error
}
\]

正式 Full Run 之前至少应该看到：

```text
领域指标有稳定正向趋势

通用回归仍在阈值内

数据分布符合预期

训练数值稳定

恢复流程可用
```

---

# 八、Phase 2：正式 CPT Run 不是一条直线，而是一串 Checkpoint Decision

正式训练过程中：

```text
Checkpoint_01
Checkpoint_02
Checkpoint_03
...
Checkpoint_N
```

每个 Checkpoint 都应该进入统一评测。

至少记录：

```text
tokens_seen

effective_training_tokens

training_loss

validation_loss

domain_perplexity

domain_probe_metrics

general_regression_metrics

instruction_regression_metrics

mixture_observed_share

replay_share

parameter_drift

training_cost
```

然后形成：

# Training Trajectory
## 训练轨迹

所以：

\[
\boxed{
FinalCheckpoint
\neq
AutomaticallyBestCheckpoint
}
\]

---

# 九、Checkpoint Selection：怎样选择真正值得进入 SFT 的 CPT 底座？

不要只选：

> Domain Score 最高。

要同时看：

```text
Domain Gain
领域收益

General Retention
通用能力保持

Training Stability
训练稳定性

Cost
训练成本

Marginal Gain
边际收益

Compatibility
Tokenizer / Serving兼容
```

可以把它理解成：

# Pareto Selection
## 多目标折中选择

也就是说：

> 找不到“所有指标都绝对最好”的模型时，选择在多个目标之间没有被明显支配的 Checkpoint。

所以：

\[
\boxed{
BestCheckpoint
=
MultiObjectiveDecision
}
\]

不是：

\[
\boxed{
LowestLoss
}
\]

---

# 十、核心心智模型 ④：Loss 是训练信号，不是发布裁判

CPT Loss 很重要。

因为它告诉我们：

> 模型是否越来越适应训练分布。

但它不能回答：

```text
采购任务是否真的更好？

通用能力是否退化？

指令遵循是否保持？

长文档能力是否真的提升？

结构化输出是否仍稳定？
```

所以：

\[
\boxed{
TrainingLoss
\neq
ReleaseMetric
}
\]

同理：

\[
\boxed{
Perplexity
\neq
ReleaseDecision
}
\]

Loss / PPL 是：

> 训练层指标。

Release Gate 需要：

> 多层证据。

---

# 十一、Phase 3：CPT 后不要直接宣布 `ProcurementLM_V0.2`，先重新 SFT

第 9 阶段已经锁定：

\[
\boxed{
Base
\rightarrow
CPT
\rightarrow
SFT
}
\]

所以选定 CPT Checkpoint 以后，

它只是：

# Domain-adapted Base
## 领域适配底座

接下来必须重新做：

# SFT
## 任务行为对齐

重新让模型恢复 / 学习：

```text
Instruction Following
指令遵循

Structured Output
结构化输出

Risk Classification
风险分类

Rationale
理由生成

Abstention
拒答与不确定性

Task Schema
任务协议
```

因此：

\[
\boxed{
CPTCheckpoint
\neq
ProcurementLM\_V0.2
}
\]

真正链路是：

\[
\boxed{
CPTCheckpoint
\rightarrow
SFT
\rightarrow
ReleaseCandidate
}
\]

---

# 十二、CPT 后重新 SFT 的关键原则：重新验证，不机械复用

可以复用原来的：

```text
SFT Dataset
Task Schema
Evaluation Set
```

但必须重新验证：

```text
Tokenizer Compatibility

Prompt Template

Max Sequence Length

Loss Mask

Adapter Target Modules

Embedding Training Policy

Learning Rate

SFT Baseline
```

特别是如果第 3 阶段最终真的：

> 修改了 Tokenizer / Vocabulary，

那旧 SFT Token Cache：

> 必须重新生成。

所以：

\[
\boxed{
ReusableArtifact
\neq
BlindlyReusableArtifact
}
\]

---

# 十三、Phase 4：评测必须分三层，而不是把所有指标搅成一个总分

第一层：

# Foundation Evaluation
## 底座能力评测

回答：

> CPT 真的让领域底座变强了吗？

看：

```text
Domain Perplexity
领域困惑度

Domain Probe
领域理解探针

Long-document Probe
长文档探针

Terminology Understanding
术语理解
```

---

第二层：

# Behavior Evaluation
## 任务行为评测

回答：

> 重新 SFT 后，模型会不会完成目标任务？

看：

```text
Task Accuracy / F1

Schema Compliance

Instruction Following

Abstention

Reason Quality

Citation / Evidence Use
```

---

第三层：

# Regression Evaluation
## 回归评测

回答：

> 为了更懂采购，损坏了什么？

看：

```text
General Language

Reasoning

Math

Code

Structured Output

Instruction Following
```

所以：

\[
\boxed{
ReleaseEvidence
=
Foundation
+
Behavior
+
Regression
}
\]

---

# 十四、核心心智模型 ⑤：一个模型必须有“收益证明”和“损失证明”

只证明：

> “采购能力更高”

是不够的。

还要证明：

> “关键原能力没有退化到不可接受”。

所以一次 Release Candidate 至少要形成两份证据：

# Gain Evidence
## 收益证据

证明：

\[
DomainCapability\uparrow
\]

以及：

# Regression Evidence
## 回归证据

证明：

\[
CriticalCapabilities
\not\downarrow
BeyondThreshold
\]

因此：

\[
\boxed{
Release
=
GainEvidence
+
RegressionEvidence
}
\]

---

# 十五、Release Gate：把“感觉可以发布”变成机器可检查规则

真正的：

# Release Gate
## 发布门槛

应该是明确条件。

概念上：

\[
ReleaseGate
=
G_{domain}
\land
G_{behavior}
\land
G_{regression}
\land
G_{artifact}
\land
G_{reproducibility}
\]

其中：

```text
G_domain
领域收益达到最低门槛

G_behavior
任务行为达到最低门槛

G_regression
关键能力退化不超过阈值

G_artifact
发布资产完整

G_reproducibility
训练和评测可追溯
```

只有全部为 True：

\[
\boxed{
ReleaseGate=True
}
\]

才允许升级成正式模型版本。

---

# 十六、核心心智模型 ⑥：Release Gate 必须在训练前定义，而不是训练后“看结果再定标准”

如果训练完以后才说：

> “这个指标掉 3% 好像也能接受。”

那很容易产生：

# Post-hoc Rationalization
## 事后合理化

所以真正专业的方式是：

> **训练前就定义成功和失败标准。**

例如：

```text
Domain Gain
必须达到预设最低改善

General Regression
不得超过预设阈值

Critical Task
不得出现严重退化

Artifact Completeness
必须全部通过
```

因此：

\[
\boxed{
PredefinedGate
>
PostHocJudgment
}
\]

这里的 `>` 表示：

> 工程决策可信度更高。

---

# 十七、Release Candidate 和 Released Model 必须分开

训练 + SFT 完成以后得到的是：

# Release Candidate
## 发布候选模型

例如：

```text
ProcurementLM_V0.2-RC1
```

它还要经历：

```text
完整评测
回归
兼容性
可复现检查
模型资产检查
```

通过以后才晋级：

```text
ProcurementLM_V0.2
```

所以：

\[
\boxed{
ReleaseCandidate
\neq
ReleasedModel
}
\]

这能防止：

> “刚训练出来的模型直接覆盖线上版本”。

---

# 十八、完整 Release Bundle 应该包含什么？

最终不要只交付一个权重目录。

第一版至少应该包含：

```text
ProcurementLM_V0.2/

├── model/
│   ├── weights
│   ├── config
│   └── generation_config
│
├── tokenizer/
│   ├── tokenizer files
│   └── tokenizer_manifest
│
├── training/
│   ├── cpt_config
│   ├── sft_config
│   ├── mixture_policy
│   ├── retention_policy
│   └── checkpoint_manifest
│
├── data_lineage/
│   ├── corpus_manifest
│   ├── synthetic_manifest
│   └── benchmark_firewall_report
│
├── evaluation/
│   ├── foundation_eval
│   ├── behavior_eval
│   ├── regression_eval
│   └── release_gate_report
│
├── provenance/
│   ├── base_model
│   ├── code_commit
│   ├── environment
│   └── run_manifest
│
└── MODEL_CARD.md
```

这就是：

# Release Bundle
## 发布资产包

---

# 十九、核心心智模型 ⑦：模型版本其实是一张 Artifact Graph

一个模型不是孤立文件。

它依赖：

```text
Base Model
↓
Tokenizer
↓
Corpus
↓
Sequence Builder
↓
Mixture Policy
↓
CPT Run
↓
Checkpoint
↓
SFT Run
↓
Evaluation Bundle
↓
Release Manifest
```

这其实是一张：

# Artifact Graph
## 工程产物依赖图

所以：

\[
\boxed{
ModelVersion
=
ArtifactGraphVersion
}
\]

如果其中任何关键节点无法追溯，

这个模型版本就不完整。

---

# 二十、Rollback：真正能发布的系统必须先设计好怎么退回去

发布 `ProcurementLM_V0.2` 前，

必须知道：

```text
上一个稳定版本是谁？

回滚需要换哪些文件？

Tokenizer是否同时回滚？

Adapter是否同时回滚？

RAG / Agent是否依赖某个输出Schema？

回滚后服务是否还能兼容？
```

所以：

# Rollback Plan
## 回滚方案

至少包含：

```text
previous_stable_model

previous_tokenizer

previous_adapter

compatibility_matrix

rollback_trigger

rollback_procedure

rollback_validation
```

因此：

\[
\boxed{
Deployable
\Rightarrow
Rollbackable
}
\]

如果一个模型：

> 只能升级，不能可靠回退，

那它还没有达到成熟发布状态。

---

# 二十一、Resume：训练中断后也必须可恢复

CPT 往往很长。

训练可能因为：

```text
节点故障
网络故障
存储故障
作业超时
人工停止
```

中断。

所以每个 Checkpoint 不只是模型 Weight，

还要尽量保存：

```text
optimizer_state

scheduler_state

global_step

tokens_seen

sampler_state

rng_state

data_shard_position
```

这样才能：

# Resume Training
## 断点续训

真正目标是：

> 恢复后尽量继续原来的训练轨迹，而不是从一个模糊状态重新开始。

所以：

\[
\boxed{
Checkpoint
=
ModelState
+
TrainingState
}
\]

---

# 二十二、核心心智模型 ⑧：Checkpoint 的价值不只是“保存模型”，而是保存决策点和恢复点

每个重要 Checkpoint 同时有三种角色：

```text
Recovery Point
故障恢复点

Evaluation Point
能力评测点

Decision Point
继续/停止/回滚决策点
```

所以：

\[
\boxed{
Checkpoint
=
Recovery
+
Evaluation
+
Decision
}
\]

这也是为什么：

> Checkpoint Policy 必须在训练前定义。

---

# 二十三、训练 Trace：以后必须能回答“这个模型为什么变成现在这样”

一次完整 Run 至少要生成：

# Run Trace
## 训练追踪记录

包含：

```text
run_id

parent_model_id

corpus_version

tokenizer_version

sequence_policy_version

mixture_policy_version

retention_policy_version

training_config_hash

code_commit

environment_id

checkpoint_ids

tokens_seen

observed_mixture

domain_metrics

regression_metrics

sft_run_id

release_candidate_id

release_decision
```

这样以后出现问题时，

不是靠：

> “我记得当时大概这么配的。”

而是可以真正重建：

\[
\boxed{
Decision
\rightarrow
Training
\rightarrow
Checkpoint
\rightarrow
Evaluation
\rightarrow
Release
}
\]

---

# 二十四、真正的 `ProcurementLM_V0.2` 到底是什么？

现在可以给出正式定义：

\[
\boxed{
ProcurementLM\_V0.2
=
BaseModel
+
DomainCPT
+
Retention
+
SFT
+
Evaluation
+
ReleaseGovernance
}
\]

更工程化一点：

\[
\boxed{
ProcurementLM\_V0.2
=
M_{base}
+
D_{CPT}
+
T
+
P_{seq}
+
P_{mix}
+
P_{retention}
+
CPTCheckpoint
+
SFT
+
EvalBundle
+
ReleaseManifest
}
\]

它不是：

> “比 V0.1 多训了一轮”。

而是：

> **第一次形成完整的高级领域适配模型版本。**

---

# 二十五、一个完整的政府采购 CPT Run 示例

假设真实诊断发现：

```text
多个采购任务都存在：
长文档术语理解弱
行业表达不稳定
复杂采购结构建模不足
```

于是：

## Step 1：Domain Gap Diagnosis
### 领域差距诊断

确认：

> 问题不是单一 SFT 行为问题。

---

## Step 2：Corpus Freeze
### 冻结训练语料

形成：

```text
ProcurementCPTCorpus_V0.1
```

完成：

```text
质量过滤
去重
Lineage
Benchmark Firewall
Token统计
```

---

## Step 3：Tokenizer Audit
### 分词器审计

结果：

```text
Keep Existing Tokenizer
```

因为：

> 领域碎片率可接受，修改收益不足以覆盖兼容成本。

---

## Step 4：Sequence Policy
### 序列构造策略

采用：

```text
Section-aware Split
章节优先切分

EOS Boundary
显式文档边界

Length-aware Packing
按长度拼接

Padding Loss Mask
Padding不计Loss
```

---

## Step 5：Mixture
### 数据混合

设计：

```text
Domain Corpus
+
General Replay
```

并控制：

```text
行业比例
高质量桶
重复曝光
Observed Mixture
```

---

## Step 6：Pilot
### 小规模试训

先验证：

```text
Loss趋势
领域PPL
通用回归
Mixture
Resume
```

通过后再进入 Full Run。

---

## Step 7：Full CPT
### 正式继续预训练

持续保存 Checkpoint。

每个 Checkpoint 都执行：

```text
Domain Eval
General Regression
Instruction Regression
Forgetting Curve
```

---

## Step 8：Checkpoint Selection
### 选择领域底座

不是选：

> 最后一个。

而是选：

> 领域收益足够、通用回归仍受控的 Pareto Checkpoint。

---

## Step 9：SFT
### 重新监督微调

在新 CPT 底座上重新训练：

```text
Procurement SFT Dataset
```

恢复 / 强化：

```text
任务Schema
风险分类
结构化输出
拒答
任务行为
```

---

## Step 10：Release Evaluation
### 发布评测

同时检查：

```text
Foundation
Behavior
Regression
Compatibility
Artifact Completeness
```

---

## Step 11：Release Gate
### 发布门槛

全部通过以后：

```text
ProcurementLM_V0.2-RC1
↓
ProcurementLM_V0.2
```

这才算真正完成。

---

# 二十六、第八课最终 10 个工程产物怎样接起来？

第 1 阶段：

```text
ProcurementCPTBoundaryModel_V0.1
```

回答：

> 要不要做 CPT？

第 2 阶段：

```text
ProcurementCPTCorpusPolicy_V0.1
```

回答：

> 什么数据可以进 CPT？

第 3 阶段：

```text
ProcurementTokenizerAudit_V0.1
```

回答：

> Tokenizer 要不要改？

第 4 阶段：

```text
ProcurementCPTObjectivePolicy_V0.1
```

回答：

> Token 怎样组成真实训练任务？

第 5 阶段：

```text
ProcurementCPTMixturePolicy_V0.1
```

回答：

> 每类数据获得多少训练预算？

第 6 阶段：

```text
ProcurementCPTForgettingPolicy_V0.1
```

回答：

> 模型什么时候开始遗忘？

第 7 阶段：

```text
ProcurementCPTRetentionPolicy_V0.1
```

回答：

> 怎样主动控制遗忘？

第 8 阶段：

```text
ProcurementCPTSyntheticCurriculumPolicy_V0.1
```

回答：

> 怎样补覆盖并安排训练难度？

第 9 阶段：

```text
ProcurementCPTSFTDecisionPolicy_V0.1
```

回答：

> 什么时候 CPT、什么时候 SFT、怎样串联？

第 10 阶段：

```text
ProcurementLM_V0.2
```

回答：

> 怎样真正发布一个经过领域适配的模型版本？

所以第八课可以压成：

\[
\boxed{
Decision
\rightarrow
Data
\rightarrow
Tokenizer
\rightarrow
Objective
\rightarrow
Mixture
\rightarrow
Forgetting
\rightarrow
Retention
\rightarrow
Synthetic/Curriculum
\rightarrow
CPT/SFT
\rightarrow
Release
}
\]

---

# 二十七、本阶段最重要的 10 个核心心智模型

> **心智模型 ①：`CPTExperiment ≠ ModelRelease`。训练跑完只是得到实验 Checkpoint，不代表模型可以发布。**

> **心智模型 ②：`ModelRelease ≠ WeightsOnly`。真正模型版本必须包含 Tokenizer、配置、数据血缘、评测证据和 Release Manifest。**

> **心智模型 ③：`NoFrozenBaseline = NoReliableComparison`。没有固定基线，就无法可靠证明模型到底变好还是变坏。**

> **心智模型 ④：`Scale amplifies Signal and Error`。扩大训练规模会同时放大正确方向和错误配置，所以 Full Run 前必须先做 Pilot。**

> **心智模型 ⑤：`BestCheckpoint = MultiObjectiveDecision`。最优发布 Checkpoint 不是 Loss 最低，而是领域收益、通用保持、成本和兼容性的综合折中。**

> **心智模型 ⑥：`TrainingLoss ≠ ReleaseMetric`。Loss / PPL 是训练信号，不是模型发布裁判。**

> **心智模型 ⑦：`Release = GainEvidence + RegressionEvidence`。既要证明学会了新的，也要证明没有把关键旧能力破坏到不可接受。**

> **心智模型 ⑧：`ReleaseCandidate ≠ ReleasedModel`。候选模型必须通过预先定义的 Release Gate 才能晋级正式版本。**

> **心智模型 ⑨：`ModelVersion = ArtifactGraphVersion`。模型版本本质是一整张依赖图，而不是一个权重文件。**

> **心智模型 ⑩：`Deployable ⇒ Rollbackable`。真正可发布的模型必须同时具备明确的回滚路径。**

---

# 二十八、把整门第八课压成一张最终工程图

```text
                        Real Failure Cases
                          真实失败案例
                               │
                               ▼
                       Domain Gap Diagnosis
                         领域差距诊断
                               │
                               ▼
                         CPT Go / No-Go
                         是否进入CPT
                               │
                               ▼
                    Procurement CPT Corpus
                      建设领域训练语料
                               │
                               ▼
                        Tokenizer Audit
                         分词器审计
                               │
                               ▼
                     Sequence Construction
                       构造训练序列
                               │
                               ▼
                    Mixture + Replay Design
                     数据混合与通用回放
                               │
                               ▼
                           Pilot CPT
                         小规模试验训练
                               │
                               ▼
                            Full CPT
                         正式继续预训练
                               │
                               ▼
                     Checkpoint Evaluation
                        周期性检查点评测
                               │
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
          Domain Gain     General Retention   Training Cost
           领域收益          通用能力保持          训练成本
               │               │               │
               └───────────────┼───────────────┘
                               ▼
                       Checkpoint Selection
                         选择CPT底座
                               │
                               ▼
                              SFT
                        重新任务行为对齐
                               │
                               ▼
                       Release Candidate
                          发布候选模型
                               │
                 ┌─────────────┼─────────────┐
                 ▼             ▼             ▼
           Foundation Eval  Behavior Eval  Regression Eval
             底座评测        行为评测         回归评测
                 │             │             │
                 └─────────────┼─────────────┘
                               ▼
                          Release Gate
                           发布门槛
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
                  Reject                 Pass
                   否决                   通过
                                          │
                                          ▼
                               ProcurementLM_V0.2
```

脑中最后只留一句：

> **真正的 CPT 工程，不是“拿政府采购数据继续训练一次”，而是从领域差距诊断开始，用版本化 Corpus、Tokenizer、Sequence、Mixture、Retention 和 Checkpoint 控制训练过程，再通过重新 SFT、分层评测、通用回归、Release Gate 与 Rollback，把一个实验 Checkpoint 变成真正可发布的领域模型。**

---

# 第八课 · 第 10 阶段掌握测试

现在不回看正文，你应该能够解释：为什么 `CPTExperiment ≠ ModelRelease`；为什么发布模型不能只有 Weight；Baseline 为什么必须训练前冻结；Reproducibility 到底要版本化哪些东西；为什么正式 Full Run 前要先做 Pilot；为什么 Scale 会同时放大 Signal 和 Error；Checkpoint 为什么既是恢复点又是评测点和决策点；为什么最终 Checkpoint 不一定最好；为什么 Loss / Perplexity 不能直接决定发布；为什么 CPT 后还要重新 SFT；Foundation、Behavior、Regression 三层评测分别回答什么；为什么 Release Gate 要训练前定义；Release Candidate 和 Released Model 有什么区别；完整 Release Bundle 应该包含哪些资产；为什么模型版本本质上是一张 Artifact Graph；为什么可发布模型必须可回滚；为什么 Checkpoint 还应该保存 Training State；以及 `ProcurementLM_V0.2` 为什么不是“V0.1 多训一轮”，而是一个带完整领域适配、评测和发布治理的模型版本。

如果这些能够完整讲出来：

\[
\boxed{
第八课第10阶段真正掌握
}
\]

---

# 第八课正式完成

到这里：

\[
\boxed{
第八课
=
10/10
}
\]

最终工程交付：

\[
\boxed{
ProcurementLM\_V0.2
}
\]

课程系统演化到：

\[
\boxed{
ProcurementDataset\_V0.1
\rightarrow
ProcurementLM\_V0.1
\rightarrow
ProcurementRAG\_V0.1
\rightarrow
ProcurementAgent\_V0.1
\rightarrow
ProcurementLM\_V0.2
}
\]

下一课正式进入：

# 第九课：Gold Benchmark、评测与可靠性
## 怎样建立 `ProcurementBench_V1`，真正证明模型、RAG、Agent 到底哪里变好了、哪里退化了、能不能上线？

第八课解决的是：

> **怎样把模型本体进一步适配到政府采购领域。**

第九课开始解决：

> **怎样用冻结、可版本化、可切片、可回归的 Gold Benchmark，证明这些提升是真的，而不是训练集记忆、指标幻觉或测试污染。**

---
