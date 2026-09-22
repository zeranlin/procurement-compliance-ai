# 第九课：Gold Benchmark、评测与可靠性

> **V2 教学增强版。** 共 12 个阶段；主要产物/主线：`ProcurementBench_V1`。  
> 核心心智模型前置、中文释义增强、详细正文完整保留。

---


<!-- LESSON 09 STAGE 01 START -->

# 第九课 · 第 1 阶段
# Benchmark 到底是什么？Validation、Test、Gold Benchmark 的边界
## 为什么“测过了”不等于“评测可信”？为什么真正专业的 Benchmark 首先是一套治理边界，而不是一份题库？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Benchmark ≠ DatasetOnly。Benchmark 是被冻结的数据、协议、指标与治理的组合。**
2. **Training ≠ Validation ≠ Test ≠ Gold Benchmark。四者的核心区别是它们在模型开发生命周期中的信息权限不同。**
3. **NoGradientLeakage ≠ NoEvaluationLeakage。即使没有直接训练，也可能通过反复调参产生决策泄漏。**
4. **ComparableScore requires ComparableProtocol。协议、Prompt、阈值、评分脚本不同，分数不能直接归因给模型。**
5. **Component Eval ≠ End-to-End Eval。组件评测负责定位问题，端到端评测负责判断结果是否真正成功。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |
| `Validation` | 验证集：开发阶段用于选模型、调参数和早停 |
| `Gold Benchmark` | Gold Benchmark：由高质量证据、专家标注和治理形成的正式评测集 |
| `Dataset` | 数据集：按统一 Schema、版本和质量标准组织的样本集合 |
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

第八课结束以后，我们已经有了：

```text
ProcurementDataset_V0.1
ProcurementLM_V0.1
ProcurementRAG_V0.1
ProcurementAgent_V0.1
ProcurementLM_V0.2
```

现在出现了一个非常现实的问题：

> **这些版本到底谁更好？**

很多团队会马上说：

```text
跑一下Accuracy
跑一下F1
让几个专家看看
抽十几个案例
让LLM打个分
```

这些都可以是评测的一部分。

但它们还不是：

# Benchmark System
## 基准评测系统

因为真正的问题不是：

> “有没有测？”

而是：

> **测的东西是不是被冻结的、可重复的、没有被训练偷看、覆盖真实风险、评分规则稳定，而且不同版本之间可以公平比较？**

所以第九课第 1 阶段先不急着讲 Precision、Recall、F1。

我们先把评测最底层的边界锁死。

本阶段最终形成：

# `ProcurementBenchmarkBoundaryPolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

很多人把 Benchmark 理解成：

> “一套测试题。”

这不够。

更专业的定义是：

\[
\boxed{
Benchmark
=
FrozenData
+
StableProtocol
+
StableMetrics
+
Governance
}
\]

也就是：

> **Benchmark 不只是数据，它是被冻结的数据 + 固定评测协议 + 固定评分标准 + 治理规则。**

所以第一条核心边界是：

\[
\boxed{
Benchmark
\neq
DatasetOnly
}
\]

如果同一批题：

```text
今天Prompt A
明天Prompt B

今天Temperature 0
明天Temperature 0.7

今天人工打分标准A
明天人工打分标准B
```

那么即使“题目没有变”，

你也已经不是在做同一套 Benchmark。

---

# 二、Training、Validation、Test、Gold Benchmark 到底有什么区别？

先用最专业但最容易落地的方式拆开。

## Training Data
### 训练数据

作用：

> **用来更新模型参数。**

包括：

```text
CPT Corpus
SFT Dataset
LoRA训练数据
Synthetic Training Data
Replay Data
```

它会进入：

\[
\boxed{
GradientUpdate
}
\]

所以：

\[
\boxed{
TrainingData
允许被模型直接学习
}
\]

---

## Validation Set
### 验证集

作用：

> **在开发过程中帮助我们做技术选择。**

例如：

```text
选Learning Rate
选Checkpoint
选Prompt
选Chunk Size
选Top-K
选Reranker
选Threshold
```

虽然 Validation Set：

> 不直接用于梯度更新，

但它会影响工程决策。

所以：

\[
\boxed{
ValidationSet
虽然不Train
但会InfluenceDesign
}
\]

---

## Test Set
### 测试集

作用：

> **在开发决策完成以后，用相对独立的数据估计最终系统表现。**

它不应该被频繁拿来：

```text
调Prompt
调Threshold
改RAG参数
选模型
反复看错误再修
```

因为一旦你反复根据 Test Set 调系统，

它就会逐渐失去：

> 独立评估价值。

---

## Gold Benchmark
### 金标准基准集

它比一般 Test Set 更严格。

通常还要求：

```text
高质量专家标注
明确评分协议
争议样本裁决
版本冻结
Slice覆盖
Benchmark Firewall
审计记录
Release Gate关联
```

所以：

\[
\boxed{
GoldBenchmark
=
HighTrustTestAsset
}
\]

它不仅用来“测分”。

它还是：

> **模型升级和发布决策的可信裁判。**

---

# 三、核心心智模型 ①
# `Training ≠ Validation ≠ Test ≠ Gold Benchmark`

这四者最大的区别，

不是文件名不同。

而是：

> **它们拥有不同的“信息权限”。**

可以理解成：

| 数据类型 | 可以更新 Weight？ | 可以调工程参数？ | 可以反复看错误？ | 主要用途 |
|---|---:|---:|---:|---|
| Training | 是 | 是 | 是 | 学习 |
| Validation | 否 | 是 | 是 | 开发与选择 |
| Test | 否 | 原则上否 | 应严格限制 | 独立评估 |
| Gold Benchmark | 否 | 否 | 高治理 | 发布与长期比较 |

最重要的不是把表背下来。

而是记住：

\[
\boxed{
TheMoreYouUseASetToImproveTheSystem,
TheLessIndependentItBecomes
}
\]

中文：

> **一套数据越被你拿来反复改系统，它就越不再是独立测试。**

---

# 四、为什么 Validation 也会“泄漏”？

很多人以为：

> 只要没把 Validation 样本放进训练集，就没有泄漏。

其实不是。

例如你跑了 30 次实验：

```text
Run 01
Run 02
Run 03
...
Run 30
```

每次都看同一个 Validation Set。

然后不断：

```text
改Prompt
改Threshold
改Top-K
改LoRA Rank
改Sampling
改规则
```

最终选择：

> 在这套 Validation 上最好的版本。

那么系统已经逐渐：

> **适配了这套 Validation。**

这叫：

# Development Overfitting
## 开发过程过拟合

所以：

\[
\boxed{
NoGradientLeakage
\neq
NoEvaluationLeakage
}
\]

即使没有梯度泄漏，

也可能存在：

> 决策层泄漏。

---

# 五、核心心智模型 ②
# `Leakage` 不只有 Training Leakage，还有 Decision Leakage

我们可以把泄漏分成至少三层：

```text
Training Leakage
训练数据直接包含测试内容

Decision Leakage
根据测试结果反复调系统

Information Leakage
通过标注说明、答案、元数据间接暴露测试信息
```

所以：

\[
\boxed{
BenchmarkLeakage
>
ExactDuplicateLeakage
}
\]

这里的 `>` 表示：

> Benchmark 泄漏是一个更大的集合，不只是完全重复样本。

---

# 六、一个非常典型的错误：把 Test Set 当成 Validation Set 用

错误流程：

```text
模型A
↓
跑Test
↓
发现召回差
↓
改Threshold
↓
再跑Test
↓
发现某类行业差
↓
补规则
↓
再跑Test
```

当这个循环重复几次以后，

你所谓的 Test Set：

> 已经成为开发集。

所以：

\[
\boxed{
RepeatedTuningOnTest
\Rightarrow
TestBecomesValidation
}
\]

这不是语义游戏。

这是评测可信度直接下降。

---

# 七、那真正的 Benchmark 应该“冻结”什么？

不只是冻结题目。

至少要冻结：

```text
Dataset Version
数据版本

Item IDs
样本ID

Labels
标准答案 / 标签

Scoring Rule
评分规则

Prompt / Eval Template
评测提示模板

Decoding Config
生成配置

Metric Definition
指标定义

Aggregation Rule
汇总规则

Slice Definition
切片定义
```

所以：

\[
\boxed{
FrozenBenchmark
=
FrozenData
+
FrozenProtocol
}
\]

只冻结数据，

但评测协议天天变：

> 仍然不能公平比较模型版本。

---

# 八、核心心智模型 ③
# `Benchmark Score` 只有在 Protocol Stable 时才可比较

假设：

```text
ProcurementLM_V0.1
F1 = 0.78
```

后来：

```text
ProcurementLM_V0.2
F1 = 0.83
```

看起来涨了 5 个点。

但如果：

```text
V0.1使用Prompt_A
V0.2使用Prompt_B

V0.1使用Threshold_0.5
V0.2使用Threshold_0.35

V0.1用旧评分脚本
V0.2用新评分脚本
```

那么：

\[
\boxed{
0.78
vs
0.83
}
\]

并不能直接归因于模型变好。

所以：

\[
\boxed{
ComparableScore
需要
ComparableProtocol
}
\]

---

# 九、Benchmark 到底评“模型”还是评“系统”？

这是政府采购 AI 特别重要的一点。

我们现在不是只有 LLM。

还有：

```text
Model
RAG
Rules
Agent
Tools
Policy
```

所以必须区分：

# Model Benchmark
## 模型基准

评：

> 模型本体。

例如：

```text
领域理解
分类
生成
长上下文
```

---

# System Benchmark
## 系统基准

评：

> 完整 ProcurementAI Pipeline。

例如：

```text
检索是否找到正确证据
Reranker是否排序正确
Agent是否选对工具
流程是否真正完成
引用是否正确
拒答是否正确
```

所以：

\[
\boxed{
ModelQuality
\neq
SystemQuality
}
\]

一个模型本体一般，

但 RAG 很强：

> 系统可以表现不错。

反过来，

模型很强，

但检索错了：

> 最终系统仍然失败。

---

# 十、核心心智模型 ④
# `Component Eval ≠ End-to-End Eval`

我们至少需要两层。

## Component Evaluation
### 组件评测

分别测：

```text
LLM
Retriever
Reranker
Citation
Agent Planner
Tool Calling
```

回答：

> 哪一层出了问题？

---

## End-to-End Evaluation
### 端到端评测

从真实用户输入开始，

一直评到：

> 最终任务结果。

回答：

> 系统整体能不能完成任务？

所以：

\[
\boxed{
ComponentEval
用于Diagnosis
}
\]

\[
\boxed{
EndToEndEval
用于Outcome
}
\]

二者缺一不可。

---

# 十一、Gold Benchmark 为什么不能只是一堆“容易题”？

如果 Benchmark 全是：

```text
简单术语解释
明显风险条款
标准格式文本
短文档
```

模型很容易拿高分。

但真实采购场景里真正困难的是：

```text
隐含风险
多条件组合
跨章节冲突
行业专项
OCR噪声
边界案例
需要拒答的样本
```

所以：

\[
\boxed{
BenchmarkCoverage
决定
BenchmarkMeaning
}
\]

一个 Benchmark 分数只有在：

> 覆盖了你真正关心的风险分布时，

才有业务意义。

---

# 十二、核心心智模型 ⑤
# `Average Score` 可以掩盖 Critical Failure

假设：

```text
总体Accuracy
= 92%
```

听起来很好。

但如果：

```text
普通样本
96%

高风险限制性条款
58%
```

那这个系统可能：

> 根本不适合上线。

所以：

\[
\boxed{
OverallMetric
\neq
SafetyOnCriticalSlices
}
\]

这就是为什么第九课后面一定会进入：

# Slice Evaluation
## 切片评测

---

# 十三、Benchmark 不是越大越好

这是一个反直觉点。

一个 100 万条、低质量、自动生成、标签噪声很高的 Benchmark，

可能不如：

> 2,000 条经过专家高质量标注、争议裁决、分布设计的 Gold Set。

所以：

\[
\boxed{
BenchmarkValue
\neq
SampleCount
}
\]

更接近：

\[
\boxed{
BenchmarkValue
=
LabelQuality
\times
Coverage
\times
ProtocolStability
\times
Governance
}
\]

这里不是要求机械相乘。

而是强调：

> Benchmark 的价值来自可信度和代表性，不只是规模。

---

# 十四、核心心智模型 ⑥
# `More Test Data ≠ Better Benchmark`

扩大 Benchmark 当然有价值。

但前提是新增样本真的提升：

```text
Coverage
覆盖

Difficulty
难度

Slice Balance
切片平衡

Uncertainty Reduction
统计不确定性降低
```

而不是只是：

> 再复制更多类似样本。

所以专业扩展 Benchmark 的问题是：

> “新增的这批样本解决了哪个评测盲区？”

不是：

> “我们又加了多少条。”

---

# 十五、Benchmark Freeze 之后还能不能改？

可以。

但不能：

> 静默修改。

必须：

# Versioning
## 版本化

例如：

```text
ProcurementBench_V1.0
↓
发现标注错误
↓
ProcurementBench_V1.0.1
```

或者：

```text
新增行业覆盖
↓
ProcurementBench_V1.1
```

关键原则：

\[
\boxed{
Frozen
\neq
NeverChange
}
\]

而是：

\[
\boxed{
Frozen
=
NoSilentChange
}
\]

---

# 十六、核心心智模型 ⑦
# `Frozen Benchmark` 的本质是“可追溯变化”，不是“永远不更新”

真实业务会变化：

```text
新政策
新行业
新文档格式
新风险模式
```

所以 Benchmark 当然需要演化。

但每次变化必须留下：

```text
旧版本
新版本
新增样本
删除样本
修正标签
指标变化
版本原因
```

这样才能：

> 历史模型和新模型仍然可公平比较。

---

# 十七、Validation、Test、Gold Benchmark 的推荐数据治理结构

可以设计：

```text
Training Pool
训练池

Development Validation
开发验证集

Locked Test
锁定测试集

Gold Benchmark
高可信发布基准
```

更严格一点：

```text
Raw Data Lake
原始数据湖
↓
Benchmark Firewall
评测隔离墙
↓
Training Eligible
可训练数据
↓
Validation Registry
验证集登记
↓
Test Registry
测试集登记
↓
Gold Registry
Gold Benchmark登记
```

这里最重要的是：

> **先登记、再训练。**

不能等模型训完以后才说：

> “这几条以后算 Benchmark。”

---

# 十八、为什么 Benchmark Firewall 要在训练前建立？

假设一条 Gold 样本：

```text
某复杂采购条款
```

已经进入：

```text
CPT
SFT
Synthetic Seed
RAG Eval开发过程
```

后来你再把它放进 Gold Benchmark，

这个 Benchmark 已经受污染。

所以：

\[
\boxed{
BenchmarkFirewall
必须PreTraining
}
\]

而不是：

> Post-hoc Cleanup。

这和第八课的数据治理完全接上了。

---

# 十九、Benchmark Firewall 需要检查什么？

至少包括：

```text
Exact Match
完全重复

Near Duplicate
近似重复

Semantic Similarity
语义相似

Same Project
同项目

Same Document Lineage
同文档血缘

Synthetic Derivative
合成派生

Prompt Leakage
评测提示泄漏
```

所以：

\[
\boxed{
TrainingCorpus
\cap
GoldBenchmark
\approx
\varnothing
}
\]

更严格地说：

> 不只是文本完全不重复，还要尽量避免高相似、同项目、同血缘和派生样本污染。

---

# 二十、核心心智模型 ⑧
# `Benchmark Firewall` 不是去重工具，而是评测独立性的治理系统

去重只回答：

> “两条文本像不像？”

Benchmark Firewall 还要回答：

```text
它们是否来自同一个项目？

是否是同一文件的不同版本？

是否是Teacher从Benchmark生成的改写？

是否在开发过程中被人工反复研究？

是否通过Prompt暴露了答案？
```

所以：

\[
\boxed{
Dedup
\subset
BenchmarkGovernance
}
\]

Benchmark Governance 比去重更大。

---

# 二十一、什么时候可以看 Gold Benchmark 的错误案例？

这是一个很专业的问题。

如果团队：

> 每次模型跑完都逐条研究 Gold 错误，

然后针对它修模型，

Gold 就会逐渐变成：

> Validation。

所以通常要有：

# Access Policy
## 访问策略

例如区分：

```text
Score Access
只看聚合分数

Slice Access
看切片结果

Error Access
看具体错误

Label Access
看标准答案
```

不同角色：

> 权限可以不同。

这叫：

# Benchmark Governance
## 基准治理

---

# 二十二、Hidden Test 为什么有价值？

最强的独立评测方式之一是：

# Hidden Test
## 隐藏测试集

开发者：

> 不知道具体题目和标签。

只能提交模型或系统版本，

由评测系统统一执行。

优势：

\[
\boxed{
ReducedHumanOverfitting
}
\]

也就是：

> 降低工程团队“记住测试题”的风险。

对内部重要 Release Gate，

隐藏测试集非常有价值。

---

# 二十三、Benchmark 需要哪些角色？

至少可能有：

```text
Dataset Owner
数据负责人

Domain Annotator
领域标注专家

Adjudicator
争议裁决人

Benchmark Maintainer
Benchmark维护者

Model Developer
模型开发者

Evaluator
评测执行者

Release Owner
发布负责人
```

这些角色不一定必须由不同人承担。

但职责必须区分。

因为：

\[
\boxed{
WhoBuilds
WhoSees
WhoScores
WhoReleases
}
\]

如果完全没有边界，

评测独立性会不断下降。

---

# 二十四、Benchmark 生命周期完整流程

英文流程：

```text
Define Evaluation Objective
↓
Create Candidate Pool
↓
Separate Train / Validation / Test
↓
Gold Annotation
↓
Adjudication
↓
Slice Design
↓
Benchmark Freeze
↓
Benchmark Firewall
↓
Controlled Evaluation
↓
Score Aggregation
↓
Regression Comparison
↓
Release Decision
↓
Versioned Update
```

中文解释：

```text
先定义到底要评什么
↓
建立候选样本池
↓
明确训练、验证、测试边界
↓
进行高质量Gold标注
↓
处理专家争议
↓
设计关键业务切片
↓
冻结Benchmark版本
↓
隔离训练和开发泄漏
↓
按固定协议运行评测
↓
统一汇总指标
↓
比较模型版本回归
↓
决定是否允许发布
↓
需要更新时发布新版本
```

所以：

\[
\boxed{
Benchmark
=
LifecycleManagedAsset
}
\]

Benchmark 不是一次性文件。

它是一项：

> **长期治理资产。**

---

# 二十五、本阶段正式工程产物
# `ProcurementBenchmarkBoundaryPolicy_V0.1`

第一版至少锁定：

```text
benchmark_policy_version

training_data_definition

validation_set_definition

test_set_definition

gold_benchmark_definition

benchmark_owner

benchmark_access_policy

gold_label_access_policy

benchmark_freeze_policy

benchmark_versioning_policy

evaluation_protocol_version

prompt_template_version

decoding_config_version

metric_definition_version

slice_definition_version

benchmark_firewall_policy

exact_match_check

near_duplicate_check

semantic_similarity_check

project_lineage_check

synthetic_derivative_check

hidden_test_policy

error_review_policy

release_gate_usage

audit_log
=
enabled
```

每次 Benchmark Run 至少记录：

```text
benchmark_run_id

model_version

system_version

benchmark_version

evaluation_protocol_version

prompt_version

decoding_config

metric_version

timestamp

overall_metrics

slice_metrics

release_decision
```

以后才能回答：

> **这个 0.83，到底是谁、在什么 Benchmark、什么协议、什么 Prompt、什么模型版本下跑出来的？**

---

# 二十六、本阶段最重要的 9 个核心心智模型

> **心智模型 ①：`Benchmark ≠ DatasetOnly`。Benchmark 是被冻结的数据、协议、指标与治理的组合。**

> **心智模型 ②：`Training ≠ Validation ≠ Test ≠ Gold Benchmark`。四者的核心区别是它们在模型开发生命周期中的信息权限不同。**

> **心智模型 ③：`NoGradientLeakage ≠ NoEvaluationLeakage`。即使没有直接训练，也可能通过反复调参产生决策泄漏。**

> **心智模型 ④：`ComparableScore requires ComparableProtocol`。协议、Prompt、阈值、评分脚本不同，分数不能直接归因给模型。**

> **心智模型 ⑤：`Component Eval ≠ End-to-End Eval`。组件评测负责定位问题，端到端评测负责判断结果是否真正成功。**

> **心智模型 ⑥：`OverallMetric ≠ SafetyOnCriticalSlices`。总体分高，仍然可能在关键高风险切片上失败。**

> **心智模型 ⑦：`BenchmarkValue ≠ SampleCount`。Benchmark 的价值来自标注质量、覆盖度、协议稳定性和治理，不只是样本数量。**

> **心智模型 ⑧：`Frozen ≠ NeverChange`。冻结意味着不能静默修改，所有变化必须版本化并可追溯。**

> **心智模型 ⑨：`BenchmarkFirewall ≠ Dedup`。Firewall 保护的是评测独立性，去重只是其中一个工具。**

---

# 二十七、把完整 Benchmark Boundary 压成一张专业工程图

```text
                     Raw Evaluation Candidates
                         候选评测样本
                                │
                                ▼
                     Evaluation Objective
                        明确评测目标
                                │
                                ▼
                     Data Role Assignment
                     给数据分配生命周期角色
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
          Training         Validation            Test
           训练集             验证集              测试集
                                                    │
                                                    ▼
                                             Gold Selection
                                              Gold样本筛选
                                                    │
                                                    ▼
                                            Expert Annotation
                                               专家标注
                                                    │
                                                    ▼
                                              Adjudication
                                               争议裁决
                                                    │
                                                    ▼
                                           Slice Construction
                                               构建切片
                                                    │
                                                    ▼
                                             Benchmark Freeze
                                               冻结版本
                                                    │
                                                    ▼
                                          Benchmark Firewall
                                              隔离训练泄漏
                                                    │
                                                    ▼
                                         Controlled Evaluation
                                             固定协议评测
                                                    │
                                                    ▼
                                    Overall + Slice + Regression
                                      总体 + 切片 + 回归结果
                                                    │
                                                    ▼
                                              Release Gate
                                               发布决策
                                                    │
                                                    ▼
                                          Versioned Evolution
                                             版本化演进
```

脑中最后只留一句：

> **Benchmark 的本质不是“拿一套题给模型考试”，而是建立一套与训练和开发过程隔离、数据和协议都被冻结、评分可重复、关键切片可解释、版本变化可追溯，并最终能够驱动 Release Gate 的长期质量裁判系统。**

---

# 第九课 · 第 1 阶段掌握测试

现在不回看正文，你应该能够解释：Training、Validation、Test、Gold Benchmark 的真正边界是什么；为什么 Validation 虽然不参与梯度也会导致开发过拟合；为什么没有 Gradient Leakage 也不代表没有 Evaluation Leakage；Benchmark 为什么不只是 Dataset；为什么 Prompt、Threshold、Decoding Config 和 Scoring Rule 也必须版本化；为什么 Test 被反复调参以后会变成 Validation；Model Benchmark 和 System Benchmark 有什么区别；Component Evaluation 与 End-to-End Evaluation 分别负责什么；为什么总体指标可能掩盖关键高风险切片；为什么 Benchmark 不是越大越好；为什么 Frozen 不等于永远不能更新；Benchmark Firewall 为什么必须在训练前建立；为什么 Firewall 不只是 Dedup；为什么 Gold 错误案例的访问权限也需要治理；Hidden Test 为什么能够降低 Human Overfitting；以及为什么真正的 Benchmark 是一个 Lifecycle Managed Asset。

如果这些能够完整讲出来：

\[
\boxed{
第九课第1阶段真正掌握
}
\]

---

# 下一阶段：第九课 · 第 2 阶段
# Gold Set：专家标注、Adjudication 与 Ground Truth
## “标准答案”是谁说了算？多个采购专家意见不一致时，怎样把主观判断变成可审计、可复现的 Gold Label？

下一阶段会正式进入：

```text
Annotation Schema
标注结构

Annotator Qualification
标注者资格

Independent Annotation
独立标注

Inter-Annotator Agreement
标注者一致性

Adjudication
争议裁决

Ground Truth
标准答案

Ambiguous Case
模糊样本

Evidence Requirement
证据要求

Label Confidence
标签置信度

Gold Set Versioning
Gold集版本化
```

并建立：

# `ProcurementGoldSetPolicy_V0.1`

下一阶段最关键的一条边界会是：

\[
\boxed{
ExpertOpinion
\neq
GroundTruth
}
\]

也就是说：

> **一个专家的判断可以是高质量意见，但只有经过明确标注规范、独立标注、证据要求和争议裁决以后，才有资格成为 Gold Label。**

---

<!-- LESSON 09 STAGE 01 END -->


<!-- LESSON 09 STAGE 02 START -->

# 第九课 · 第 2 阶段
# Gold Set：专家标注、Adjudication 与 Ground Truth
## “标准答案”是谁说了算？多个采购专家意见不一致时，怎样把主观判断变成可审计、可复现的 Gold Label？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **ExpertOpinion ≠ GroundTruth。专家意见只是输入，Gold Truth 来自受控标注与裁决流程。**
2. **Gold = AuthorityByProcess。Gold 的权威性来自 Schema、证据、独立判断、裁决和版本治理，而不是单一专家身份。**
3. **BadSchema + GoodExperts = UnstableGold。标注结构和边界没定义清楚，再好的专家也会产生不稳定标签。**
4. **GoodExpert ≠ GoodAnnotator。领域知识和高一致性标注能力是两种不同能力。**
5. **Agreement Metric ≠ Ground Truth Quality。一致性高不代表一定正确，一致性低也不等于谁必须被淘汰。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `Adjudication` | 专家裁决：对分歧样本形成最终 Gold 结论 |
| `ANN` | ANN/近似最近邻：在大规模向量中快速寻找相似项 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |

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

第 1 阶段我们已经锁定：

\[
\boxed{
Training
\neq
Validation
\neq
Test
\neq
GoldBenchmark
}
\]

并且进一步建立：

\[
\boxed{
Benchmark
=
FrozenData
+
StableProtocol
+
StableMetrics
+
Governance
}
\]

但现在出现了一个更根本的问题：

> **Gold Benchmark 里面的“Gold”，到底是谁定义的？**

假设有一条采购条款：

```text
供应商须在项目所在地设立固定服务机构。
```

专家 A 认为：

> 存在不合理地域限制风险。

专家 B 认为：

> 如果项目确实需要本地即时服务，可能具有合理业务依据。

专家 C 认为：

> 需要结合采购需求、履约时效、服务半径和替代措施后才能判断。

那么真正的问题是：

> **谁对？**

如果我们只是：

```text
找一个资深专家
↓
他说是什么
↓
就记成Gold Label
```

那我们得到的不是严格意义上的 Ground Truth。

更准确地说：

> 我们得到的是一个 Expert Opinion。

所以本阶段最重要的第一条边界是：

\[
\boxed{
ExpertOpinion
\neq
GroundTruth
}
\]

本阶段最终形成：

# `ProcurementGoldSetPolicy_V0.1`

---

# 一、Gold Label 到底是什么？

Gold Label 不是：

> “专家觉得最合理的答案。”

更专业的定义是：

\[
\boxed{
GoldLabel
=
Schema
+
Evidence
+
IndependentJudgment
+
Adjudication
+
VersionedDecision
}
\]

也就是说，一个 Gold Label 至少需要：

```text
明确标注结构
证据依据
独立判断
争议裁决
版本化记录
```

所以：

\[
\boxed{
Gold
不是
AuthorityByPerson
}
\]

而是：

\[
\boxed{
Gold
=
AuthorityByProcess
}
\]

中文：

> **Gold 的可信度来自过程，而不是来自某一个人“资历很高”。**

---

# 二、核心心智模型 ①
# `ExpertOpinion ≠ GoldLabel`

一个专家的判断可以：

```text
专业
有经验
有依据
高质量
```

但它仍然只是：

# Expert Opinion
## 专家意见

只有经过：

```text
Annotation Guideline
标注规范

Independent Annotation
独立标注

Evidence Requirement
证据要求

Conflict Resolution
冲突处理

Adjudication
正式裁决
```

以后，

才有资格升级成：

# Gold Label
## 金标准标签

所以：

\[
\boxed{
GoldLabel
=
ProcessControlledExpertJudgment
}
\]

---

# 三、为什么 Gold Set 最先要定义 Annotation Schema？

# Annotation Schema
## 标注结构

回答的是：

> **每个样本到底要标什么字段？**

例如一个采购风险样本，如果只标：

```text
risk = yes / no
```

信息可能远远不够。

更完整的 Schema 可以是：

```text
sample_id

risk_label

risk_type

risk_severity

evidence_span

reason

applicable_context

ambiguity_flag

confidence

source_reference
```

其中：

### `risk_label`
是否存在目标风险。

### `risk_type`
属于哪一类风险。

### `evidence_span`
文本里哪一段支持这个判断。

### `reason`
为什么这样判。

### `applicable_context`
这个判断成立需要什么上下文。

### `ambiguity_flag`
是不是存在合理争议。

### `confidence`
标注者对判断有多大把握。

所以：

\[
\boxed{
AnnotationSchema
决定
WhatGroundTruthMeans
}
\]

如果 Schema 本身含糊，

后面再专业的专家也很难得到稳定 Gold。

---

# 四、核心心智模型 ②
# `BadSchema + GoodExperts = UnstableGold`

很多团队遇到专家意见不一致，

第一反应是：

> “专家水平不一样。”

但真正问题可能是：

```text
标签定义不清
类别边界重叠
风险类型互相包含
证据要求没写
模糊案例没定义
```

所以：

\[
\boxed{
AnnotatorDisagreement
可能来自
SchemaAmbiguity
}
\]

而不一定来自：

> “某个专家错了”。

因此标注一致性差时，

第一步不应该立刻淘汰标注者，

而要先检查：

# Annotation Guideline
## 标注规范

---

# 五、Annotation Guideline 应该写到什么程度？

至少需要回答：

```text
这个Label的正式定义是什么？

什么情况属于正例？

什么情况属于负例？

有哪些边界案例？

哪些证据是必须的？

什么时候允许标Ambiguous？

什么时候允许Abstain？

多标签能不能同时成立？

冲突时优先看什么证据？
```

例如不要只写：

```text
标签：
地域限制
```

而应该写成更接近：

```text
Label:
地域限制风险

Definition:
对供应商注册地、设立地、经营地、服务机构所在地等提出与项目实际需要缺乏充分关联的限制。

Positive Example:
明确要求供应商必须在某地注册，且没有与履约必要性相对应的合理说明。

Negative Example:
要求供应商具备能够满足明确时效要求的服务能力，但不限定注册地。

Ambiguous Example:
要求在本地设置服务点，但采购需求同时存在高频现场响应要求，需要进一步结合上下文判断。
```

这才叫：

# Operational Definition
## 可操作定义

即：

> 不是“概念解释”，而是能指导不同标注者做出一致判断的定义。

---

# 六、Annotator Qualification：谁有资格做 Gold 标注？

# Annotator Qualification
## 标注者资格

Gold Set 不适合完全依赖：

> 无领域背景的普通众包标注。

但也不是说：

> 只要专家职称高就一定适合。

真正应该看：

```text
领域知识
规则理解
标注规范理解
证据意识
边界案例判断能力
一致性表现
```

所以：

\[
\boxed{
DomainExpertise
\neq
AnnotationSkill
}
\]

一个很懂采购的人，

不一定天然会做：

> 高一致性的 Benchmark 标注。

---

# 七、核心心智模型 ③
# `GoodExpert ≠ GoodAnnotator`

标注者必须经过：

```text
Guideline Training
标注规范培训

Calibration Round
校准轮次

Trial Annotation
试标

Error Review
错误复盘

Qualification Test
资格测试
```

然后才进入正式 Gold 标注。

所以：

\[
\boxed{
AnnotatorQuality
=
Expertise
+
GuidelineMastery
+
Calibration
}
\]

---

# 八、为什么必须 Independent Annotation？

# Independent Annotation
## 独立标注

意思是：

> 多个标注者先独立判断，不能提前互相讨论答案。

例如：

```text
Sample 001

Annotator A
→ risk

Annotator B
→ no_risk

Annotator C
→ ambiguous
```

为什么必须先独立？

因为如果一开始就一起讨论：

```text
资深专家先说答案
↓
其他人跟随
```

你就无法知道：

> 他们是真的独立一致，还是发生了从众。

这会产生：

# Anchoring Bias
## 锚定偏差

和：

# Authority Bias
## 权威偏差

所以：

\[
\boxed{
IndependentFirst
\rightarrow
DiscussLater
}
\]

---

# 九、Inter-Annotator Agreement：专家一致性到底怎么量化？

# Inter-Annotator Agreement
## 标注者间一致性

最简单可以看：

# Percent Agreement
## 简单一致率

例如：

\[
Agreement
=
\frac{NumberOfAgreedItems}
{TotalItems}
\]

如果 100 个样本中：

```text
85个样本两位专家一致
```

那么：

\[
Agreement=85\%
\]

但简单一致率有一个问题：

> 没有扣除“随机碰巧一致”。

---

# 十、Cohen's Kappa：为什么比简单一致率更严格？

如果是两个标注者、类别型标签，

常见指标之一是：

# Cohen's Kappa
## Cohen κ 一致性系数

概念公式：

\[
\kappa
=
\frac{p_o-p_e}
{1-p_e}
\]

其中：

\[
p_o
=
ObservedAgreement
\]

即：

> 实际观察到的一致率。

\[
p_e
=
ExpectedAgreementByChance
\]

即：

> 按两位标注者各自标签分布，随机情况下预期会有多少一致。

所以：

\[
\boxed{
Kappa
=
AgreementBeyondChance
}
\]

它回答：

> **两位专家的一致，超过随机巧合多少？**

---

# 十一、核心心智模型 ④
# `Agreement Metric ≠ Ground Truth Quality`

这是非常容易误解的一点。

如果：

\[
\kappa
\]

很高，

只能说明：

> 标注者很一致。

不自动说明：

> 他们判断一定正确。

例如如果：

```text
所有人都误解了Guideline
```

也可能：

> 高度一致地标错。

所以：

\[
\boxed{
Consistency
\neq
Correctness
}
\]

Agreement 是：

> Gold Quality 的一个指标。

不是：

> Gold Quality 的全部。

---

# 十二、那一致性低意味着什么？

低一致性可能意味着：

```text
Schema有问题

Guideline不清楚

案例本身真的有争议

标注者培训不足

上下文缺失

标签类别设计不合理
```

所以低一致性应该触发：

# Root Cause Analysis
## 根因分析

不能简单：

```text
一致性低
→ 把少数意见删掉
```

否则可能正好删掉了：

> 最有价值的边界信息。

---

# 十三、Adjudication 到底是什么？

# Adjudication
## 争议裁决

指：

> 当独立标注不一致时，通过一个受控流程产生最终 Gold 决策。

注意：

\[
\boxed{
Adjudication
\neq
MajorityVoteOnly
}
\]

简单多数投票：

```text
A = risk
B = risk
C = no_risk
```

可能得到：

> risk。

但如果 C 提供了：

> 更强的权威证据或关键上下文，

那多数票不一定更合理。

所以真正 Adjudication 应考虑：

```text
标注规范
证据
上下文
规则定义
争议点
裁决理由
```

---

# 十四、核心心智模型 ⑤
# `Consensus ≠ Truth`

三个人都同意：

> 不代表一定真。

一个人持少数意见：

> 也不代表一定错。

所以：

\[
\boxed{
MajorityVote
是Aggregation
不是TruthGuarantee
}
\]

Gold Set 的关键不是：

> 让所有人看起来一致。

而是：

> **让最终决策有证据、有规则、有记录。**

---

# 十五、Adjudication 推荐流程

英文流程：

```text
Independent Labels
↓
Disagreement Detection
↓
Evidence Comparison
↓
Guideline Check
↓
Context Review
↓
Adjudicator Decision
↓
Decision Rationale
↓
Gold Label
```

中文解释：

```text
先收集独立标注
↓
识别哪些样本存在冲突
↓
比较每个判断引用的证据
↓
检查标注规范
↓
补充必要上下文
↓
由裁决者作最终决定
↓
记录为什么这样裁决
↓
形成Gold Label
```

所以：

\[
\boxed{
Adjudication
=
Decision
+
Rationale
+
Evidence
}
\]

---

# 十六、Ground Truth 真的“绝对真实吗”？

在很多机器学习任务里：

```text
猫
狗
数字
字符
```

Ground Truth 相对明确。

但政府采购很多任务不是纯客观事实识别。

例如：

```text
条款是否构成不合理限制？

理由是否充分？

风险级别是高还是中？

是否需要进一步人工审核？
```

这些可能带有：

> 规范性判断和上下文依赖。

所以更专业的理解是：

\[
\boxed{
GroundTruth
=
BestAvailableOperationalTruth
}
\]

即：

> **在当前任务定义、证据、规范和版本下，经过治理流程得到的最可信可操作答案。**

不是哲学意义上的：

> 永恒绝对真理。

---

# 十七、核心心智模型 ⑥
# `GroundTruth` 在高争议任务中，本质上是“治理后的可操作真值”

这并不会降低 Gold 的价值。

相反，

它要求我们把：

```text
任务定义
证据来源
裁决原则
不确定性
版本
```

全部写清楚。

所以：

\[
\boxed{
GroundTruthWithoutProvenance
=
WeakGroundTruth
}
\]

没有来源和决策记录的 Gold，

可信度是有限的。

---

# 十八、Ambiguous Case：有些样本本来就不应该硬标 Yes / No

假设一个样本：

```text
要求供应商在本地设置服务点
```

但上下文只给了这一句话。

没有：

```text
响应时效
履约场景
服务范围
行业特性
```

这时强行标：

```text
risk = yes
```

或者：

```text
risk = no
```

可能都会制造：

# Label Noise
## 标签噪声

所以 Gold Schema 应该允许：

```text
ambiguous

insufficient_context

needs_review
```

---

# 十九、核心心智模型 ⑦
# `ForcedCertainty = LabelNoise`

如果真实世界本来存在不确定性，

而标注系统只允许：

```text
Yes
No
```

那么所有不确定性都会被：

> 强行压成错误确定性。

所以：

\[
\boxed{
Uncertainty
应该被
Represented
}
\]

而不是：

> Erased。

这会直接影响后面第 9 阶段：

# Calibration / Abstention / OOD

---

# 二十、Evidence Requirement：Gold Label 为什么必须绑定证据？

如果专家只给：

```text
label = risk
```

以后别人很难判断：

> 为什么？

所以高价值 Gold Sample 最好包含：

```text
evidence_span

source_document

source_section

reference_rule

decision_reason
```

这样可以支持：

```text
专家复核
错误审计
模型解释评测
Citation评测
未来标签修订
```

所以：

\[
\boxed{
GoldLabel
+
Evidence
>
GoldLabelOnly
}
\]

这里的 `>` 表示：

> 审计与评测价值更高。

---

# 二十一、Label Confidence：专家也应该表达不确定性

可以让标注者记录：

# Label Confidence
## 标签置信度

例如：

```text
high
medium
low
```

或者数值：

```text
0.95
0.70
0.55
```

但必须注意：

\[
\boxed{
AnnotatorConfidence
\neq
ProbabilityOfTruth
}
\]

它只是：

> 标注者主观把握程度。

不能直接当作：

> 客观概率。

---

# 二十二、核心心智模型 ⑧
# `Confidence` 是元数据，不是替代 Adjudication 的捷径

一个专家：

```text
confidence = 0.99
```

不能自动压过：

> 另一个专家提供的更强证据。

所以：

\[
\boxed{
HighConfidence
\neq
AutomaticAuthority
}
\]

Confidence 可以帮助：

```text
筛选复核样本
识别边界案例
设计难度Slice
```

但不能直接替代：

> 证据和裁决。

---

# 二十三、Single-label 和 Multi-label 要不要提前定义？

必须。

例如一个条款可能同时涉及：

```text
地域限制
资格条件
履约能力
中小企业政策
```

如果任务天然允许多个风险同时存在，

却把 Schema 设计成：

# Single-label
## 单标签

那 Gold 会丢失真实结构。

如果任务业务上只允许：

> 一个主风险类型，

那就需要明确：

```text
primary_label
secondary_labels
```

所以：

\[
\boxed{
LabelCardinality
必须由TaskDefinition决定
}
\]

---

# 二十四、Gold Set 不只需要 Label，还需要 Provenance

# Provenance
## 来源血缘

至少记录：

```text
sample_id

source_document_id

source_version

project_id

section_id

annotation_guideline_version

annotator_ids

annotation_timestamp

adjudicator_id

adjudication_reason

gold_version
```

为什么？

因为以后如果：

```text
规则更新
源文件更正
发现标注错误
Guideline变化
```

你必须知道：

> 哪些 Gold 样本受影响。

所以：

\[
\boxed{
GoldSet
=
Labels
+
Lineage
}
\]

---

# 二十五、Gold Label Freeze：什么时候一条样本才算正式 Gold？

可以定义一个：

# Gold Promotion Gate
## Gold 晋级门槛

例如：

```text
Schema完整
AND

独立标注完成
AND

必要证据存在
AND

冲突已裁决
AND

Benchmark Firewall通过
AND

Lineage完整
```

只有全部通过：

\[
\boxed{
GoldEligible=True
}
\]

才进入正式 Gold Set。

所以：

\[
\boxed{
Annotated
\neq
Gold
}
\]

---

# 二十六、Gold Set Versioning：标注修正以后怎么办？

不能直接覆盖旧标签。

例如：

```text
ProcurementGold_V1.0
```

后来发现：

```text
17条标签需要修订
```

应该形成：

```text
ProcurementGold_V1.0.1
```

并记录：

```text
changed_item_ids

old_label

new_label

change_reason

adjudicator

timestamp
```

所以：

\[
\boxed{
GoldCorrection
必须Versioned
}
\]

不能：

> 悄悄改答案。

---

# 二十七、核心心智模型 ⑨
# `Gold Set` 是审计资产，不是一次性标注结果

真正 Gold Set 应该能回答：

```text
谁标的？

按哪版Guideline标的？

当时用了什么证据？

谁裁决的？

为什么这样裁决？

后来有没有改过？

哪个Benchmark版本使用了它？
```

所以：

\[
\boxed{
GoldSet
=
AuditableDecisionAsset
}
\]

这也是为什么：

> Benchmark 评测质量的上限，首先受 Gold 质量限制。

---

# 二十八、Gold Quality 的上限决定 Benchmark 的上限

如果 Gold 本身：

```text
标签不稳定
证据缺失
大量争议
版本混乱
```

那么即使模型评测系统再精密，

得到的指标也会很可疑。

所以：

\[
\boxed{
BenchmarkQuality
\leq
GoldQuality
}
\]

这里不是严格数学不等式。

它表达：

> **评测体系不可能长期比自己的标准答案更可信。**

---

# 二十九、完整 Gold Set 生产流程

英文流程：

```text
Task Definition
↓
Annotation Schema
↓
Guideline Design
↓
Annotator Qualification
↓
Calibration Round
↓
Independent Annotation
↓
Agreement Measurement
↓
Disagreement Detection
↓
Evidence Review
↓
Adjudication
↓
Confidence / Ambiguity Tagging
↓
Gold Promotion Gate
↓
Freeze
↓
Versioned Maintenance
```

中文解释：

```text
先定义评测任务
↓
设计标注字段
↓
写清楚标注规范
↓
筛选并培训标注者
↓
先做一轮校准标注
↓
正式独立标注
↓
测量一致性
↓
发现冲突样本
↓
比较证据
↓
做正式争议裁决
↓
记录置信度和模糊状态
↓
通过Gold晋级门槛
↓
冻结成Gold版本
↓
以后所有修改都版本化
```

所以：

\[
\boxed{
GoldCreation
=
ControlledDecisionPipeline
}
\]

---

# 三十、本阶段正式工程产物
# `ProcurementGoldSetPolicy_V0.1`

第一版至少锁定：

```text
gold_policy_version

task_definition

annotation_schema_version

annotation_guideline_version

label_definition

positive_examples

negative_examples

ambiguous_examples

annotator_qualification_policy

calibration_round_required

independent_annotation_required

minimum_annotators

agreement_metric

agreement_threshold

disagreement_policy

adjudication_required

adjudicator_role

evidence_required

evidence_schema

ambiguity_policy

insufficient_context_policy

abstain_policy

label_confidence_policy

single_multi_label_policy

provenance_required

gold_promotion_gate

benchmark_firewall_required

gold_freeze_policy

gold_versioning_policy

audit_log
=
enabled
```

每个 Gold Sample 至少记录：

```text
sample_id

source_id

source_version

annotation_schema_version

guideline_version

annotator_labels

annotator_reasons

annotator_evidence

agreement_status

adjudication_status

adjudicated_label

adjudication_reason

ambiguity_flag

label_confidence

gold_eligible

gold_version
```

这样以后才能回答：

> **这个 Gold Label 为什么是这个答案，而不是另一个答案？**

---

# 三十一、本阶段最重要的 10 个核心心智模型

> **心智模型 ①：`ExpertOpinion ≠ GroundTruth`。专家意见只是输入，Gold Truth 来自受控标注与裁决流程。**

> **心智模型 ②：`Gold = AuthorityByProcess`。Gold 的权威性来自 Schema、证据、独立判断、裁决和版本治理，而不是单一专家身份。**

> **心智模型 ③：`BadSchema + GoodExperts = UnstableGold`。标注结构和边界没定义清楚，再好的专家也会产生不稳定标签。**

> **心智模型 ④：`GoodExpert ≠ GoodAnnotator`。领域知识和高一致性标注能力是两种不同能力。**

> **心智模型 ⑤：`Agreement Metric ≠ Ground Truth Quality`。一致性高不代表一定正确，一致性低也不等于谁必须被淘汰。**

> **心智模型 ⑥：`Consensus ≠ Truth`。多数投票只是聚合方法，不是事实保证；最终 Gold 必须有证据和裁决理由。**

> **心智模型 ⑦：`ForcedCertainty = LabelNoise`。真实存在模糊性时，强制 Yes / No 会制造错误确定性。**

> **心智模型 ⑧：`GoldLabel + Evidence > GoldLabelOnly`。有证据的标签才具备更高的复核、审计和生成评测价值。**

> **心智模型 ⑨：`Annotated ≠ Gold`。完成标注只是中间状态，只有通过 Gold Promotion Gate 才能进入正式 Gold Set。**

> **心智模型 ⑩：`GoldSet = AuditableDecisionAsset`。Gold Set 不是一张标签表，而是一套可以追溯谁、依据什么、如何裁决、何时修改的决策资产。**

---

# 三十二、把完整 Gold Set 流程压成一张专业工程图

```text
                         Task Definition
                           定义评测任务
                                │
                                ▼
                       Annotation Schema
                         设计标注结构
                                │
                                ▼
                      Annotation Guideline
                         编写标注规范
                                │
                                ▼
                    Annotator Qualification
                         标注者资格校准
                                │
                                ▼
                     Independent Annotation
                           独立标注
                                │
                                ▼
                    Agreement Measurement
                          一致性评估
                                │
                  ┌─────────────┴─────────────┐
                  ▼                           ▼
               Agree                      Disagree
                一致                         冲突
                  │                           │
                  │                           ▼
                  │                    Evidence Review
                  │                       证据复核
                  │                           │
                  │                           ▼
                  │                      Adjudication
                  │                       正式裁决
                  │                           │
                  └─────────────┬─────────────┘
                                ▼
                     Ambiguity / Confidence
                       模糊性与置信度记录
                                │
                                ▼
                      Gold Promotion Gate
                         Gold晋级门槛
                                │
                  ┌─────────────┴─────────────┐
                  ▼                           ▼
                Reject                       Pass
                 淘汰                         通过
                                              │
                                              ▼
                                         Gold Freeze
                                          冻结版本
                                              │
                                              ▼
                                    Versioned Maintenance
                                        版本化维护
```

脑中最后只留一句：

> **Gold Set 的本质不是“让专家给每道题一个答案”，而是先定义可操作的标注 Schema，再通过合格标注者的独立判断、一致性测量、证据要求、争议裁决、不确定性表达和版本治理，把专家判断加工成可审计、可复现、可长期比较的 Ground Truth。**

---

# 第九课 · 第 2 阶段掌握测试

现在不回看正文，你应该能够解释：为什么 Expert Opinion 不等于 Ground Truth；Gold Label 的权威为什么来自流程而不是个人；Annotation Schema 为什么决定 Ground Truth 的含义；为什么 Bad Schema 即使配上好专家也会产生不稳定标签；Good Expert 和 Good Annotator 有什么区别；为什么标注者必须先独立判断再讨论；Percent Agreement 和 Cohen's Kappa 分别在测什么；为什么高一致性不自动等于高正确性；低一致性可能暴露哪些系统性问题；Adjudication 和简单多数投票有什么区别；为什么 Consensus 不等于 Truth；高争议任务里的 Ground Truth 应该怎样理解；为什么允许 Ambiguous / Insufficient Context 比强制 Yes / No 更专业；Evidence Requirement 为什么重要；Label Confidence 能说明什么、不能说明什么；Single-label 和 Multi-label 为什么必须在任务定义阶段决定；Gold Set 为什么必须记录 Provenance；为什么 Annotated 不等于 Gold；Gold Promotion Gate 应该检查什么；为什么 Gold 修正必须版本化；以及为什么 Benchmark 质量的上限首先受 Gold 质量限制。

如果这些能够完整讲出来：

\[
\boxed{
第九课第2阶段真正掌握
}
\]

---

# 下一阶段：第九课 · 第 3 阶段
# Evaluation Schema：到底评什么，不只是 Correct / Wrong
## 一个政府采购 AI 到底应该被拆成哪些能力维度评测？为什么只给最终答案打一个“对 / 错”，无法定位模型、RAG 和 Agent 真正的问题？

下一阶段会正式进入：

```text
Evaluation Unit
评测单元

Task Taxonomy
任务分类体系

Capability Dimension
能力维度

Outcome Metric
结果指标

Process Metric
过程指标

Evidence Quality
证据质量

Error Taxonomy
错误分类

Severity
错误严重度

Partial Credit
部分得分

Composite Score
复合指标
```

并建立：

# `ProcurementEvaluationSchema_V0.1`

下一阶段最关键的一条边界会是：

\[
\boxed{
CorrectAnswer
\neq
CompleteEvaluation
}
\]

也就是说：

> **最终答案看起来正确，只能说明“结果可能对了”；它并不能证明证据正确、过程可靠、风险边界正确，更不能告诉我们错的时候到底错在哪一层。**

---

<!-- LESSON 09 STAGE 02 END -->


<!-- LESSON 09 STAGE 03 START -->

# 第九课 · 第 3 阶段
# Evaluation Schema：到底评什么，不只是 Correct / Wrong
## 一个政府采购 AI 到底应该被拆成哪些能力维度评测？为什么只给最终答案打一个“对 / 错”，无法定位模型、RAG 和 Agent 真正的问题？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **CorrectAnswer ≠ CompleteEvaluation。最终答案正确，不代表过程、证据和系统行为都可靠。**
2. **WhatYouMeasure → WhatYouCanImprove。评测维度决定你能诊断和优化到什么粒度。**
3. **TaskType → EvaluationLogic。分类、检索、生成、Agent 不应该被同一套指标粗暴衡量。**
4. **Outcome ≠ Process。结果对不代表过程可靠，尤其在需要审计的系统里。**
5. **SameErrorRate ≠ SameRiskProfile。错误数量相同，错误结构和严重度可能完全不同。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `Citation` | 引用：把生成结论和具体来源建立可追踪链接 |

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

前两阶段，我们已经解决了两个最底层的问题：

\[
\boxed{
Benchmark
\neq
DatasetOnly
}
\]

以及：

\[
\boxed{
ExpertOpinion
\neq
GroundTruth
}
\]

现在 Gold Set 已经有了相对可信的“标准答案”。

但马上会出现第三个问题：

> **到底拿这些 Gold 样本评什么？**

假设系统最终给出一个结论：

```text
风险类型：地域限制
结论：存在风险
理由：要求供应商在本地设立服务机构
```

如果最终标签和 Gold 一样，我们能不能直接说：

> “这个样本评测通过”？

不一定。

因为系统可能：

```text
结论碰巧对了
但证据引用错了

结论对了
但理由是编的

结论对了
但RAG检索到了错误政策

结论对了
但Agent调用了错误工具

结论对了
但遇到信息不足时本应该拒答
```

所以本阶段最重要的边界是：

\[
\boxed{
CorrectAnswer
\neq
CompleteEvaluation
}
\]

本阶段最终形成：

# `ProcurementEvaluationSchema_V0.1`

---

# 一、Evaluation Schema 到底是什么？

# Evaluation Schema
## 评测结构

它回答的不是：

> “用什么 Metric？”

而是更前一层：

> **一个样本到底要从哪些维度被判定。**

可以把它表示成：

\[
\boxed{
EvaluationSchema
=
EvaluationUnit
+
CapabilityDimensions
+
Outcome
+
Process
+
Evidence
+
ErrorTaxonomy
+
Severity
}
\]

中文就是：

> 先定义评测单元，再定义能力维度、最终结果、过程、证据、错误类型和错误严重度。

所以：

\[
\boxed{
Metric
是Schema的一部分
不是Schema本身
}
\]

---

# 二、核心心智模型 ①
# `WhatYouMeasure` 决定 `WhatYouCanImprove`

如果 Benchmark 只记录：

```text
final_correct = true / false
```

那么系统失败时你只能知道：

> “错了。”

却不知道：

```text
Retriever没找到？
Reranker排错？
LLM理解错？
证据引用错？
Agent工具选错？
格式错？
该拒答却没拒答？
```

所以：

\[
\boxed{
CoarseEvaluation
\Rightarrow
CoarseDiagnosis
}
\]

评测 Schema 越粗，

你能做的工程诊断就越粗。

---

# 三、第一步：定义 Evaluation Unit

# Evaluation Unit
## 评测单元

到底“一条评测样本”是什么？

可以是：

```text
一个分类样本
一个问题
一段采购条款
一份完整文档
一次RAG问答
一次Agent任务
一个完整采购工作流
```

这些不是同一种 Evaluation Unit。

例如：

### Item-level
样本级

评：

> 单条输入输出。

### Document-level
文档级

评：

> 一份完整采购文件的理解。

### Session-level
会话级

评：

> 多轮交互是否保持状态。

### Task-level
任务级

评：

> Agent 是否最终完成真实目标。

所以：

\[
\boxed{
EvaluationUnit
决定
MetricMeaning
}
\]

如果 Unit 定义不清，

不同指标会混在一起。

---

# 四、Task Taxonomy：先把任务类型分清

政府采购 AI 至少可能包含：

```text
Classification
分类

Extraction
信息抽取

Retrieval
检索

Ranking
排序

Question Answering
问答

Summarization
摘要

Risk Analysis
风险分析

Citation
引用

Tool Calling
工具调用

Workflow Completion
工作流完成
```

每类任务的“正确”都不同。

例如：

> Classification 可以有明确标签。

但：

> Generation 往往不是唯一正确文本。

所以：

\[
\boxed{
OneMetric
不能覆盖
AllTaskTypes
}
\]

---

# 五、核心心智模型 ②
# `TaskType` 决定 `EvaluationLogic`

分类任务：

> 更适合 Confusion Matrix、Precision、Recall、F1。

检索任务：

> 更适合 Recall@K、MRR、nDCG。

生成任务：

> 更适合事实性、Groundedness、完整性、引用质量等 Rubric。

Agent：

> 更关心 Task Completion、Tool Correctness、Recovery、Safety。

所以：

\[
\boxed{
MetricChoice
必须由
TaskSemantics
驱动
}
\]

不是哪个 Metric 流行就用哪个。

---

# 六、Capability Dimension：不要把所有能力混成一个分数

# Capability Dimension
## 能力维度

对政府采购系统，可以拆成：

```text
Domain Understanding
领域理解

Factual Correctness
事实正确性

Risk Recognition
风险识别

Evidence Grounding
证据支撑

Citation Correctness
引用正确性

Instruction Following
指令遵循

Structured Output
结构化输出

Abstention
拒答与不确定性

Retrieval Quality
检索质量

Tool Use
工具使用

Task Completion
任务完成

Safety / Policy Compliance
安全与策略遵循
```

于是一个样本可能：

```text
结论正确 = 1
证据正确 = 0
引用正确 = 0
格式正确 = 1
```

这比：

```text
overall = 1
```

信息量高得多。

---

# 七、Outcome Metric 和 Process Metric 必须分开

# Outcome Metric
## 结果指标

回答：

> 最终结果对不对？

例如：

```text
最终风险类型是否正确
最终答案是否正确
任务是否完成
```

# Process Metric
## 过程指标

回答：

> 系统是怎样得到这个结果的？

例如：

```text
是否检索到正确证据
是否调用正确工具
是否使用了正确参数
是否进行了必要复核
```

所以：

\[
\boxed{
Outcome
\neq
Process
}
\]

---

# 八、核心心智模型 ③
# `RightAnswerForWrongReason` 仍然是系统风险

如果系统：

> 通过错误证据碰巧给出正确结论，

今天可能得分。

但换一个样本：

> 很可能崩。

所以：

\[
\boxed{
CorrectOutcome
+
InvalidProcess
\neq
ReliableSystem
}
\]

特别是政府采购这类需要：

```text
可解释
可审计
可追溯
```

的场景，

过程质量不能被忽略。

---

# 九、Evidence Quality：证据本身也要评

对于有 RAG 或引用的系统，

不能只看：

> “有没有引用。”

还要分：

```text
Evidence Relevance
证据是否相关

Evidence Sufficiency
证据是否足够

Evidence Correctness
证据是否支持结论

Evidence Coverage
关键结论是否都有证据
```

所以：

\[
\boxed{
CitationPresent
\neq
EvidenceValid
}
\]

有引用，

不代表引用真的支持答案。

---

# 十、Error Taxonomy：错误分类体系为什么重要？

假设 100 个失败样本。

如果只记：

```text
wrong = 100
```

价值很低。

更专业的做法是：

# Error Taxonomy
## 错误分类体系

例如：

```text
E1 Domain Misunderstanding
领域理解错误

E2 Retrieval Miss
检索漏召回

E3 Ranking Error
排序错误

E4 Unsupported Claim
无证据断言

E5 Wrong Citation
错误引用

E6 Instruction Violation
指令违反

E7 Schema Error
结构输出错误

E8 Overclaim
过度确定

E9 Failed Abstention
该拒答未拒答

E10 Tool Error
工具调用错误

E11 State Error
状态管理错误

E12 Completion Failure
任务未完成
```

这样才能回答：

> 新模型到底把哪类错误减少了？

---

# 十一、核心心智模型 ④
# `ErrorCount` 不如 `ErrorStructure` 有价值

两个系统都错 100 条：

```text
系统A：
90条格式错
10条事实错

系统B：
10条格式错
90条事实错
```

这两个系统风险完全不同。

所以：

\[
\boxed{
SameErrorRate
\neq
SameRiskProfile
}
\]

评测必须理解：

> 错误结构。

---

# 十二、Severity：错误严重度必须进入 Schema

同样是一个错误：

```text
少一个标点
```

和：

```text
把高风险限制条款判断成无风险
```

不能同等对待。

所以需要：

# Severity
## 错误严重度

例如：

```text
S0 Cosmetic
展示问题

S1 Minor
轻微错误

S2 Material
影响业务判断

S3 Critical
可能导致重大决策风险
```

于是：

\[
\boxed{
ErrorProbability
\neq
ErrorCost
}
\]

这为后面：

> 风险加权、Release Gate

打基础。

---

# 十三、Partial Credit：生成任务为什么不能只有 0 / 1？

一段回答可能：

```text
结论正确
理由部分正确
证据不完整
格式完全正确
```

如果直接：

```text
score = 0
```

会丢失信息。

如果：

```text
score = 1
```

又过于乐观。

所以可以采用：

# Partial Credit
## 部分得分

例如：

| 维度 | 分数 |
|---|---:|
| 结论正确 | 1.0 |
| 理由完整 | 0.7 |
| 证据充分 | 0.5 |
| 引用正确 | 1.0 |
| 格式遵循 | 1.0 |

但需要注意：

\[
\boxed{
PartialCredit
必须有Rubric
}
\]

不能靠评测者随意感觉。

---

# 十四、核心心智模型 ⑤
# `PartialCredit` 的价值在诊断，不在制造漂亮小数

如果最终只是算：

```text
0.83
```

但不知道 0.83 来自哪里，

意义仍然有限。

更重要的是：

> 每个维度为什么得这个分。

所以：

\[
\boxed{
DecomposedScore
>
OpaqueScore
}
\]

这里的 `>` 表示：

> 工程诊断价值更高。

---

# 十五、Composite Score：能不能把所有东西合成一个总分？

可以，

但必须谨慎。

# Composite Score
## 复合指标

可以概念化：

\[
S
=
\sum_i w_i s_i
\]

其中：

\[
w_i
=
第i个能力维度权重
\]

\[
s_i
=
该维度得分
\]

但风险是：

> 高分维度可以把关键失败“平均掉”。

例如：

```text
格式 100
语言 95
事实 60
安全 40
```

如果直接平均，

总分仍可能看起来不错。

所以：

\[
\boxed{
CompositeScore
不能替代
CriticalGate
}
\]

---

# 十六、核心心智模型 ⑥
# `WeightedAverage` 不能把 Critical Failure 洗掉

对关键能力应该设置：

# Hard Gate
## 硬门槛

例如：

```text
Critical Risk Recall >= threshold

Citation Correctness >= threshold

Failed Abstention <= threshold
```

即使综合分很高，

只要关键门槛没过：

\[
\boxed{
ReleaseGate=False
}
\]

这比单一总分安全得多。

---

# 十七、Evaluation Record：每次评测到底要保存什么？

建议每个样本记录：

```text
benchmark_item_id

task_type

input

gold_output

gold_evidence

model_output

retrieved_context

tool_trace

outcome_score

process_score

evidence_score

error_codes

severity

slice_tags

judge_version

metric_version

evaluation_timestamp
```

这样评测不是一张最终分数表。

而是：

# Evaluation Trace
## 评测追踪记录

---

# 十八、Judge 到底是谁？

不同任务可能使用：

```text
Exact Matcher
精确规则

Programmatic Scorer
程序评分器

Domain Expert
领域专家

LLM-as-a-Judge
大模型裁判

Hybrid Judge
混合裁判
```

所以 Evaluation Schema 还必须明确：

# Judge Type
## 裁判类型

因为：

\[
\boxed{
Score
依赖
Judge
}
\]

如果 Judge 变了，

分数也可能变。

---

# 十九、核心心智模型 ⑦
# `JudgeVersion` 也是 Benchmark Protocol 的一部分

如果使用 LLM-as-a-Judge，

至少要版本化：

```text
judge_model

judge_prompt

judge_temperature

rubric_version
```

否则：

> 同一个模型输出，换了 Judge，分数可能变。

所以：

\[
\boxed{
JudgeChange
=
ProtocolChange
}
\]

---

# 二十、Evaluation Schema 应该支持 Model、RAG、Agent 共用吗？

应该：

> 共用顶层框架，但允许任务专属字段。

可以设计：

```text
Common Layer
通用层

+
Task-specific Layer
任务专属层
```

Common Layer：

```text
correctness
severity
evidence
slice
error_type
```

RAG Layer：

```text
retrieval_recall
ranking
context_quality
```

Agent Layer：

```text
tool_selection
tool_args
state
recovery
completion
```

这样：

\[
\boxed{
SharedSchema
+
TaskSpecificSchema
}
\]

既能统一，

又不会强行一刀切。

---

# 二十一、Evaluation Schema 的版本也必须冻结

例如：

```text
ProcurementEvaluationSchema_V1.0
```

以后发现：

> 需要新增“Abstention Quality”。

应该：

```text
ProcurementEvaluationSchema_V1.1
```

而不是直接改旧字段。

因为：

\[
\boxed{
SchemaChange
可能改变
HistoricalScoreMeaning
}
\]

---

# 二十二、本阶段正式工程产物
# `ProcurementEvaluationSchema_V0.1`

第一版至少锁定：

```text
evaluation_schema_version

evaluation_unit

task_taxonomy

capability_dimensions

outcome_metrics

process_metrics

evidence_metrics

error_taxonomy

severity_levels

partial_credit_policy

composite_score_policy

critical_gate_policy

judge_type

judge_version

task_specific_fields

slice_fields

evaluation_trace_schema

schema_versioning_policy
```

每个 Evaluation Item 至少记录：

```text
item_id

task_type

gold_reference

gold_evidence

system_output

system_trace

dimension_scores

error_codes

severity

slice_tags

judge_metadata

final_status
```

---

# 二十三、本阶段最重要的 9 个核心心智模型

> **心智模型 ①：`CorrectAnswer ≠ CompleteEvaluation`。最终答案正确，不代表过程、证据和系统行为都可靠。**

> **心智模型 ②：`WhatYouMeasure → WhatYouCanImprove`。评测维度决定你能诊断和优化到什么粒度。**

> **心智模型 ③：`TaskType → EvaluationLogic`。分类、检索、生成、Agent 不应该被同一套指标粗暴衡量。**

> **心智模型 ④：`Outcome ≠ Process`。结果对不代表过程可靠，尤其在需要审计的系统里。**

> **心智模型 ⑤：`SameErrorRate ≠ SameRiskProfile`。错误数量相同，错误结构和严重度可能完全不同。**

> **心智模型 ⑥：`PartialCredit` 必须基于 Rubric。部分得分是诊断工具，不是随意打小数。**

> **心智模型 ⑦：`CompositeScore ≠ ReleaseGate`。综合分不能掩盖关键能力失败。**

> **心智模型 ⑧：`JudgeVersion` 属于 Benchmark Protocol。换裁判就等于改变评测协议。**

> **心智模型 ⑨：`SharedSchema + TaskSpecificSchema`。统一评测框架和任务专属维度必须同时存在。**

---

# 二十四、把 Evaluation Schema 压成一张专业工程图

```text
                         Benchmark Item
                           Gold样本
                              │
                              ▼
                       Evaluation Unit
                         定义评测单元
                              │
                              ▼
                         Task Taxonomy
                           识别任务类型
                              │
                              ▼
                    Capability Dimensions
                       拆分能力维度
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
            Outcome         Process        Evidence
             结果            过程            证据
               │              │              │
               └──────────────┼──────────────┘
                              ▼
                        Error Taxonomy
                         错误类型归因
                              │
                              ▼
                           Severity
                          错误严重度
                              │
                              ▼
                     Partial / Exact Score
                         分维度评分
                              │
                              ▼
                        Critical Gates
                         关键能力门槛
                              │
                              ▼
                       Evaluation Trace
                         评测记录
```

脑中最后只留一句：

> **Evaluation Schema 的本质不是“给模型打多少分”，而是把一次系统输出拆成结果、过程、证据、错误类型和严重度，使我们既能公平比较版本，又能知道系统到底为什么成功、为什么失败。**

---

# 第九课 · 第 3 阶段掌握测试

现在不回看正文，你应该能够解释：为什么 Correct Answer 不等于 Complete Evaluation；Evaluation Unit 为什么会改变指标含义；Task Taxonomy 为什么必须先于 Metric；Outcome Metric 和 Process Metric 有什么区别；为什么 Right Answer for Wrong Reason 仍然是系统风险；Evidence Quality 应该拆成哪些维度；Error Taxonomy 为什么比单纯 Error Count 更有价值；Severity 为什么必须进入 Schema；Partial Credit 为什么需要 Rubric；Composite Score 为什么不能替代 Critical Gate；Judge 为什么也要版本化；为什么 RAG、Agent 需要 Task-specific Schema；以及为什么 Evaluation Schema 本身也必须版本化。

如果这些能够完整讲出来：

\[
\boxed{
第九课第3阶段真正掌握
}
\]

---

# 下一阶段：第九课 · 第 4 阶段
# Classification Metrics：Precision、Recall、F1、PR-AUC 与业务代价
## 为什么采购风险识别不能只看 Accuracy？False Negative 和 False Positive 在业务上到底谁更贵？

下一阶段最关键的边界：

\[
\boxed{
Accuracy
\neq
RiskQuality
}
\]

并建立：

# `ProcurementClassificationMetricPolicy_V0.1`

---

<!-- LESSON 09 STAGE 03 END -->


<!-- LESSON 09 STAGE 04 START -->

# 第九课 · 第 4 阶段
# Classification Metrics：Precision、Recall、F1、PR-AUC 与业务代价
## 为什么采购风险识别不能只看 Accuracy？False Negative 和 False Positive 在业务上到底谁更贵？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Accuracy ≠ RiskQuality。类别不平衡时，高 Accuracy 可能掩盖风险类完全失效。**
2. **Precision 对应误报负担，Recall 对应漏报风险，两者必须绑定业务代价。**
3. **SameModel + DifferentThreshold = DifferentOperatingPoint。Threshold 是部署行为的一部分。**
4. **PRCurve = OperatingTradeoffMap。不要只看单个阈值，要看整条误报—漏报权衡。**
5. **AggregateMetric 必须配合 PerClassMetric，否则稀有关键类会被平均掉。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Recall` | 召回率：真实风险中被系统成功找出的比例 |
| `Precision` | 精确率：系统报出的风险中真正成立的比例 |
| `Accuracy` | 准确率：全部样本中判断正确的比例 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `Threshold` | 阈值：把连续分数转成业务动作的决策门槛 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |

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

第 3 阶段我们已经把评测 Schema 拆开。

现在进入第一个真正的 Metric 系统：

# Classification Evaluation
## 分类评测

政府采购里大量任务都是分类：

```text
是否存在风险？
属于哪类风险？
是否需要人工复核？
是否应拒答？
文档是否属于目标类型？
```

但分类评测最常见的误区就是：

> “Accuracy 够高就行。”

本阶段第一条边界：

\[
\boxed{
Accuracy
\neq
RiskQuality
}
\]

本阶段最终形成：

# `ProcurementClassificationMetricPolicy_V0.1`

---

# 一、先从 Confusion Matrix 开始

二分类最基本的四种结果：

| Gold | Prediction | 名称 |
|---|---|---|
| Positive | Positive | TP |
| Negative | Positive | FP |
| Negative | Negative | TN |
| Positive | Negative | FN |

中文：

### True Positive
真正例

> 真有风险，模型也识别出风险。

### False Positive
假正例

> 实际没风险，模型误报风险。

### True Negative
真负例

> 实际没风险，模型判断无风险。

### False Negative
假负例

> 实际有风险，模型却漏掉了。

真正业务里：

\[
\boxed{
FP
和
FN
通常不是同样贵
}
\]

---

# 二、核心心智模型 ①
# `Metric` 必须和 `ErrorCost` 绑定

如果 False Positive 的代价是：

> 多一次人工复核。

而 False Negative 的代价是：

> 高风险条款被系统漏过。

那两类错误显然不能等价。

所以：

\[
\boxed{
ClassificationQuality
=
StatisticalPerformance
+
BusinessCost
}
\]

Metric 不是抽象数学游戏。

它最终要服务业务决策。

---

# 三、Accuracy 为什么可能骗人？

Accuracy：

\[
Accuracy
=
\frac{TP+TN}
{TP+TN+FP+FN}
\]

假设 1000 条样本里：

```text
950条无风险
50条有风险
```

一个模型永远预测：

```text
无风险
```

那么：

\[
Accuracy=95\%
\]

看起来很高。

但：

\[
Recall_{risk}=0
\]

也就是：

> 一个风险都没抓到。

所以：

\[
\boxed{
ImbalancedData
下
Accuracy
可能严重误导
}
\]

---

# 四、Precision：报出来的风险里，有多少是真的？

\[
Precision
=
\frac{TP}{TP+FP}
\]

中文：

> 模型说“有风险”的案例里，真正有风险的比例。

如果 Precision 很低：

```text
系统一天报100条
只有20条真风险
```

那么人工团队会：

> 被大量误报淹没。

所以 Precision 更接近：

# Alert Quality
## 告警质量

---

# 五、Recall：真实风险里，抓到了多少？

\[
Recall
=
\frac{TP}{TP+FN}
\]

中文：

> 所有真实风险里，模型成功识别了多少。

如果 Recall 低：

> 风险漏检严重。

所以在高风险识别里：

\[
\boxed{
Recall
常常直接关系
MissedRisk
}
\]

---

# 六、核心心智模型 ②
# `Precision` 和 `Recall` 代表两种完全不同的业务痛点

Precision 低：

> 误报多。

Recall 低：

> 漏报多。

所以：

\[
\boxed{
Precision
\neq
Recall
}
\]

不存在脱离业务目标的：

> “哪个指标永远更重要”。

必须结合：

```text
人工复核成本
风险漏检代价
场景风险等级
用户容忍度
```

共同决定。

---

# 七、F1：为什么要同时平衡 Precision 和 Recall？

\[
F1
=
2
\cdot
\frac{Precision\cdot Recall}
{Precision+Recall}
\]

它是调和平均。

特点：

> 如果 Precision 或 Recall 某一个很低，F1 会被明显拉低。

所以 F1 适合：

> 希望同时兼顾误报和漏报的场景。

但：

\[
\boxed{
F1
仍然没有表达
真实业务成本
}
\]

如果 FN 代价远高于 FP，

F1 仍可能不够。

---

# 八、F-beta：当 Recall 比 Precision 更重要

可以使用：

\[
F_\beta
=
(1+\beta^2)
\frac{PR}
{\beta^2P+R}
\]

当：

\[
\beta>1
\]

Recall 权重更高。

当：

\[
\beta<1
\]

Precision 权重更高。

所以：

\[
\boxed{
F_\beta
=
PreferenceEncodedFScore
}
\]

它把业务偏好显式写进 Metric。

---

# 九、核心心智模型 ③
# `Threshold` 也是模型行为的一部分

很多分类模型输出：

```text
risk_score = 0.73
```

最后是否判为风险取决于：

\[
threshold
\]

例如：

```text
threshold = 0.5
```

如果把 Threshold 从 0.5 降到 0.3：

通常：

```text
Recall ↑
Precision ↓
```

所以：

\[
\boxed{
SameModel
+
DifferentThreshold
=
DifferentOperatingPoint
}
\]

因此：

> Benchmark 比较模型时，Threshold Policy 必须固定或显式说明。

---

# 十、PR Curve：为什么不能只看一个 Threshold？

# Precision-Recall Curve
## 精确率-召回率曲线

通过不断改变 Threshold，

得到一组：

\[
(Recall, Precision)
\]

点。

它告诉我们：

> 模型在不同误报 / 漏报权衡下能达到什么表现。

因此：

\[
\boxed{
PRCurve
=
OperatingTradeoffMap
}
\]

不是只看一个固定阈值。

---

# 十一、PR-AUC 为什么适合稀有风险类？

# PR-AUC
## Precision-Recall 曲线下面积

当 Positive 很稀有时，

PR Curve 通常比 ROC 更直接反映：

> 正类识别质量。

因为它重点关注：

```text
Precision
Recall
```

而不是大量 TN。

所以：

\[
\boxed{
RarePositiveTask
通常更关注
PR-AUC
}
\]

---

# 十二、ROC-AUC 能不能用？

当然可以。

# ROC
## Receiver Operating Characteristic

看：

\[
TPR
\]

和：

\[
FPR
\]

不同 Threshold 下的关系。

ROC-AUC 适合看：

> 模型整体排序能力。

但在极度不平衡场景：

> ROC-AUC 可能看起来不错，但实际 Precision 很差。

所以：

\[
\boxed{
ROCAUC
\neq
OperationalPrecision
}
\]

---

# 十三、Specificity：负类识别也要看

\[
Specificity
=
\frac{TN}{TN+FP}
\]

它表示：

> 真实无风险样本中，有多少被正确判断为无风险。

如果 Specificity 太低：

> 大量正常采购条款被误报。

所以：

\[
\boxed{
HighRecall
也不能无限牺牲
Specificity
}
\]

---

# 十四、Macro / Micro / Weighted F1 有什么区别？

多分类时非常重要。

### Macro F1
宏平均

> 每个类别先算 F1，再平均。

特点：

> 小类别和大类别权重相同。

适合：

> 关注稀有风险类别。

### Micro F1
微平均

> 汇总所有 TP / FP / FN 后再算。

特点：

> 大类别影响更大。

### Weighted F1
加权平均

> 按类别样本数加权。

所以：

\[
\boxed{
Macro
更关心
SmallClasses
}
\]

而：

\[
\boxed{
Micro
更接近
OverallVolume
}
\]

---

# 十五、核心心智模型 ④
# `Overall F1` 可能掩盖稀有关键类别

假设：

```text
常见风险类别 F1 = 0.95
关键稀有风险 F1 = 0.40
```

如果大类别样本很多，

Micro F1 仍可能很漂亮。

所以：

\[
\boxed{
AggregateMetric
必须配合
PerClassMetric
}
\]

---

# 十六、Multi-label 任务怎么评？

如果一个条款可同时属于：

```text
地域限制
资格条件
履约要求
```

就是：

# Multi-label Classification
## 多标签分类

这时不能只用单标签 Accuracy。

可以关注：

```text
Per-label Precision / Recall / F1
Micro F1
Macro F1
Hamming Loss
Exact Match Ratio
```

其中：

# Exact Match Ratio
要求整组标签完全一致。

很严格。

# Hamming Loss
关注每个标签位有多少错。

所以：

\[
\boxed{
MultiLabelCorrectness
有多个粒度
}
\]

---

# 十七、Cost-sensitive Evaluation：业务代价怎么进入评测？

可以定义成本矩阵。

例如：

```text
FP cost = 1
FN cost = 10
```

总成本概念上：

\[
Cost
=
c_{FP}\cdot FP
+
c_{FN}\cdot FN
\]

这里不是说实际业务一定用 1 和 10。

而是：

> 把错误代价显式建模。

因此：

\[
\boxed{
BestThreshold
不一定是
BestF1Threshold
}
\]

而可能是：

> 最小业务风险成本的 Threshold。

---

# 十八、核心心智模型 ⑤
# `MetricOptimal` 不一定等于 `BusinessOptimal`

某个 Threshold：

```text
F1最高
```

不代表：

> 业务总风险最低。

所以：

\[
\boxed{
MetricOptimization
\neq
DecisionOptimization
}
\]

最终 Threshold 应由：

```text
业务成本
风险偏好
人工容量
安全边界
```

共同决定。

---

# 十九、Top-K / Ranking 形式的分类怎么办？

有些系统会输出：

```text
Top1 风险类型
Top2 候选风险
Top3 候选风险
```

这时可以看：

```text
Top-1 Accuracy
Top-K Recall
```

如果人工专家后续会从候选里选择，

Top-K Recall 可能更重要。

所以：

\[
\boxed{
Metric
要匹配
HumanWorkflow
}
\]

---

# 二十、Threshold 不能在 Test 上调

这一条和第 1 阶段完全衔接。

应该：

```text
Validation Set
↓
选Threshold
↓
Freeze
↓
Test / Gold Benchmark
```

不能：

```text
Test跑一遍
↓
看结果
↓
调Threshold
↓
再跑Test
```

否则：

\[
\boxed{
ThresholdTuningOnTest
=
DecisionLeakage
}
\]

---

# 二十一、本阶段正式工程产物
# `ProcurementClassificationMetricPolicy_V0.1`

第一版至少锁定：

```text
classification_metric_policy_version

task_type

positive_class_definition

negative_class_definition

class_distribution

confusion_matrix_required

precision_required

recall_required

f1_required

fbeta_policy

specificity_required

pr_auc_required

roc_auc_policy

macro_micro_weighted_policy

per_class_metrics_required

multi_label_policy

threshold_selection_set

threshold_value

threshold_version

cost_matrix

critical_false_negative_policy

critical_false_positive_policy

release_gate_thresholds
```

每次 Classification Run 至少记录：

```text
model_version

benchmark_version

threshold

TP
FP
TN
FN

precision
recall
f1
fbeta
specificity
pr_auc
roc_auc

per_class_metrics

business_cost

release_status
```

---

# 二十二、本阶段最重要的 9 个核心心智模型

> **心智模型 ①：`Accuracy ≠ RiskQuality`。类别不平衡时，高 Accuracy 可能掩盖风险类完全失效。**

> **心智模型 ②：`Precision` 对应误报负担，`Recall` 对应漏报风险，两者必须绑定业务代价。**

> **心智模型 ③：`SameModel + DifferentThreshold = DifferentOperatingPoint`。Threshold 是部署行为的一部分。**

> **心智模型 ④：`PRCurve = OperatingTradeoffMap`。不要只看单个阈值，要看整条误报—漏报权衡。**

> **心智模型 ⑤：`AggregateMetric` 必须配合 `PerClassMetric`，否则稀有关键类会被平均掉。**

> **心智模型 ⑥：`Macro` 更重视小类别，`Micro` 更受大类别影响。**

> **心智模型 ⑦：`MetricOptimal ≠ BusinessOptimal`。最优 F1 阈值不一定是最低业务风险阈值。**

> **心智模型 ⑧：`Metric` 必须匹配 `HumanWorkflow`。机器只是给候选时，Top-K Recall 可能比 Top-1 更有价值。**

> **心智模型 ⑨：`ThresholdTuningOnTest = DecisionLeakage`。阈值必须在 Validation 上选择，再到 Test / Gold 上冻结评估。**

---

# 二十三、下一阶段：第九课 · 第 5 阶段
# Generation Evaluation：理由、引用、事实性、幻觉与 Groundedness

最关键的边界：

\[
\boxed{
FluentAnswer
\neq
CorrectAnswer
}
\]

并建立：

# `ProcurementGenerationEvalPolicy_V0.1`

---

<!-- LESSON 09 STAGE 04 END -->


<!-- LESSON 09 STAGE 05 START -->

# 第九课 · 第 5 阶段
# Generation Evaluation：理由、引用、事实性、幻觉与 Groundedness
## 生成答案“看起来很专业”，到底怎样证明它事实正确、有证据、没有幻觉，而且真正回答了问题？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **FluentAnswer ≠ CorrectAnswer。语言流畅和事实正确是两个不同维度。**
2. **ReferenceSimilarity ≠ SemanticCorrectness。文本重合度不能替代语义正确性。**
3. **Factuality ≠ Groundedness。事实可能是真的，但当前证据未必支持。**
4. **AnswerLevelEval 应尽可能拆到 ClaimLevelEval，否则很难定位幻觉。**
5. **CitationPresent ≠ CitationCorrect，而 CitationCorrect ≠ CitationComplete。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Citation` | 引用：把生成结论和具体来源建立可追踪链接 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `Generalization` | 泛化：对未见项目、时间、地区和表达的有效能力 |
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

分类任务的答案空间有限。

但生成任务不同。

同一个正确答案可以有很多种表达。

所以生成评测不能简单依赖：

```text
Exact Match
```

最危险的情况是：

> 模型语言非常流畅、专业术语很多、格式也很好，但事实和证据是错的。

因此本阶段第一条边界：

\[
\boxed{
FluentAnswer
\neq
CorrectAnswer
}
\]

本阶段最终形成：

# `ProcurementGenerationEvalPolicy_V0.1`

---

# 一、生成评测为什么比分类难？

分类：

```text
Gold = 风险
Pred = 风险
```

比较直接。

生成：

```text
Gold：
该条款存在潜在地域限制风险……

Pred：
从履约便利性角度看，该要求具有一定合理性……
```

需要判断：

```text
结论
事实
理由
证据
完整性
引用
不确定性
任务遵循
```

所以：

\[
\boxed{
GenerationEval
=
MultiDimensionalJudgment
}
\]

---

# 二、核心心智模型 ①
# `ReferenceSimilarity ≠ SemanticCorrectness`

传统 NLP 常用：

```text
BLEU
ROUGE
```

这些指标衡量：

> 文本表面重合度。

但在高自由度生成任务里：

一个答案和 Gold 用词不同，

仍可能完全正确。

反过来：

一个答案和 Gold 很像，

也可能在关键事实处错了一句。

所以：

\[
\boxed{
LexicalOverlap
\neq
Truth
}
\]

---

# 三、生成评测至少拆成哪些维度？

建议至少：

```text
Task Correctness
任务结论正确性

Factuality
事实正确性

Groundedness
证据支撑度

Completeness
完整性

Relevance
相关性

Citation Correctness
引用正确性

Citation Completeness
引用覆盖度

Instruction Following
指令遵循

Abstention Quality
拒答质量

Style / Clarity
表达清晰度
```

注意：

> Style 应该放在较后层。

因为：

\[
\boxed{
PrettyWriting
不能补偿
FalseFacts
}
\]

---

# 四、Factuality 和 Groundedness 有什么区别？

# Factuality
## 事实正确性

问：

> 这句话本身是否符合真实事实？

# Groundedness
## 证据支撑度

问：

> 这句话是否被当前提供的证据支持？

例如某句话：

> 在现实中可能是真的，

但当前 RAG Context 没有提供这个事实。

那么：

```text
Factuality = 可能正确
Groundedness = 不充分
```

所以：

\[
\boxed{
Factuality
\neq
Groundedness
}
\]

---

# 五、核心心智模型 ②
# `TrueButUngrounded` 仍然可能是系统风险

在要求：

> 基于指定采购文件回答

的任务中，

模型即使凭记忆说了一个真实知识，

也可能违反：

> 只能基于文档证据回答。

所以：

\[
\boxed{
TaskTruth
=
WorldTruth
+
EvidenceConstraint
}
\]

在 Grounded QA 里，

证据边界本身就是任务定义的一部分。

---

# 六、Claim-level Evaluation：为什么要把答案拆成 Claim？

一段生成答案可能包含 8 个断言。

如果只给整段：

```text
overall = 0.8
```

很难定位哪里错。

更专业的是：

# Claim Decomposition
## 断言拆解

例如：

```text
Claim 1：该条款限制供应商注册地
Claim 2：该限制与履约必要性缺乏关联
Claim 3：因此属于高风险
```

然后逐条评：

```text
Supported?
Contradicted?
NotEnoughEvidence?
```

所以：

\[
\boxed{
AnswerLevelEval
可以进一步拆成
ClaimLevelEval
}
\]

---

# 七、Hallucination 怎么定义？

在评测里不要只写：

> “有幻觉。”

要做 Taxonomy。

例如：

```text
Unsupported Claim
无证据断言

Contradicted Claim
与证据矛盾

Fabricated Citation
伪造引用

Wrong Attribution
错误归因

Invented Number
编造数字

Invented Policy
编造政策

Overgeneralization
过度泛化
```

所以：

\[
\boxed{
Hallucination
不是单一错误类型
}
\]

---

# 八、核心心智模型 ③
# `Hallucination Rate` 必须知道“幻觉是什么”

如果不同团队对 Hallucination 定义不同，

那么：

```text
Hallucination Rate = 3%
```

没有可比性。

所以：

\[
\boxed{
MetricDefinition
先于
MetricValue
}
\]

---

# 九、Citation Correctness：引用“存在”不等于引用“正确”

可以拆成：

```text
Citation Presence
有没有引用

Citation Validity
引用是否指向真实来源

Citation Entailment
引用内容是否真的支持结论

Citation Location
引用定位是否正确
```

所以：

\[
\boxed{
CitationPresent
\neq
CitationCorrect
}
\]

---

# 十、Citation Completeness：有些关键结论根本没引证

一个回答可能：

```text
第一段有引用
第二段有三个关键结论但没有引用
```

这时：

> Citation Correctness 可能很高，

但：

> Citation Completeness 很差。

所以：

\[
\boxed{
CorrectCitation
\neq
CompleteCitationCoverage
}
\]

---

# 十一、Reason Quality：理由怎么评？

理由评测至少可以看：

```text
Logical Consistency
逻辑一致

Evidence Use
是否使用证据

Causal Validity
因果是否合理

Rule Application
规则适用是否正确

Boundary Awareness
是否意识到条件边界
```

一个看起来很长的 Explanation：

> 不代表 Reason Quality 高。

---

# 十二、核心心智模型 ④
# `LongExplanation ≠ GoodReasoning`

模型很容易生成：

> 很长、很顺、很专业的解释。

但真正评测应该问：

```text
有没有错误前提？
有没有证据跳跃？
有没有把相关性当因果？
有没有忽略关键上下文？
```

所以：

\[
\boxed{
ReasoningQuality
需要结构化Rubric
}
\]

---

# 十三、LLM-as-a-Judge 能不能用？

可以。

# LLM-as-a-Judge
## 使用大模型做评测裁判

优点：

```text
便宜
可扩展
能处理开放式文本
```

风险：

```text
Judge偏差
偏好长答案
偏好某种写作风格
自我偏好
Prompt敏感
模型版本变化
```

所以：

\[
\boxed{
LLMJudge
\neq
GroundTruth
}
\]

---

# 十四、怎样让 LLM Judge 更可靠？

至少：

```text
固定Judge Model
固定Judge Prompt
固定Temperature
固定Rubric
给Gold Evidence
要求逐维度评分
做Human Calibration
定期抽检
```

并记录：

```text
judge_model_version
judge_prompt_version
rubric_version
```

---

# 十五、核心心智模型 ⑤
# `LLM Judge` 是可扩展评测器，不是最终真相来源

最适合的定位：

> 程序规则和人工专家之间的扩展层。

可以采用：

```text
Programmatic Checks
+
LLM Judge
+
Human Audit
```

形成：

# Hybrid Evaluation
## 混合评测

---

# 十六、Pairwise Evaluation 为什么经常比绝对打分稳定？

让 Judge 判断：

```text
A = 8.2
B = 8.5
```

有时很不稳定。

但问：

> A 和 B 哪个更好？

通常更容易。

这叫：

# Pairwise Evaluation
## 成对比较

适合：

```text
模型版本比较
Prompt版本比较
生成质量比较
```

但也要防：

```text
Position Bias
顺序偏差
```

所以可以：

> A/B 和 B/A 都跑。

---

# 十七、Abstention 也属于生成质量

如果证据不足，

模型应该：

```text
无法从当前材料可靠判断
```

而不是：

> 自信补全。

所以：

\[
\boxed{
GoodGeneration
包括
KnowingWhenNotToGenerate
}
\]

这会在第 9 阶段进一步展开。

---

# 十八、Generation Rubric 示例

可以设计：

| 维度 | 0 | 1 | 2 |
|---|---|---|---|
| 结论 | 错 | 部分正确 | 正确 |
| 事实 | 多处错误 | 小瑕疵 | 无关键错误 |
| Groundedness | 无证据 | 部分支持 | 充分支持 |
| 引用 | 错/伪造 | 部分正确 | 正确完整 |
| 完整性 | 严重缺失 | 基本完整 | 完整 |
| 指令遵循 | 明显违反 | 小偏差 | 完全遵循 |

然后再配：

> Critical Error Gate。

例如：

```text
Fabricated Policy = Critical
Fabricated Citation = Critical
```

---

# 十九、核心心智模型 ⑥
# `RubricScore` 不能掩盖 Critical Hallucination

即使：

```text
总分 = 9/10
```

但如果出现：

> 编造政策依据，

仍然可能：

\[
\boxed{
ReleaseFail
}
\]

所以：

\[
\boxed{
AverageQuality
\neq
CriticalSafety
}
\]

---

# 二十、本阶段正式工程产物
# `ProcurementGenerationEvalPolicy_V0.1`

第一版至少锁定：

```text
generation_eval_policy_version

task_correctness_rubric

factuality_rubric

groundedness_rubric

completeness_rubric

relevance_rubric

citation_correctness_rubric

citation_completeness_rubric

instruction_following_rubric

abstention_rubric

claim_decomposition_policy

hallucination_taxonomy

critical_hallucination_policy

judge_type

judge_model_version

judge_prompt_version

pairwise_eval_policy

human_audit_rate

release_gate
```

每个生成样本至少记录：

```text
item_id

gold_answer
gold_evidence

model_answer

claims

claim_support_status

dimension_scores

hallucination_codes

citation_scores

judge_metadata

critical_error

final_status
```

---

# 二十一、本阶段最重要的 9 个核心心智模型

> **心智模型 ①：`FluentAnswer ≠ CorrectAnswer`。语言流畅和事实正确是两个不同维度。**

> **心智模型 ②：`ReferenceSimilarity ≠ SemanticCorrectness`。文本重合度不能替代语义正确性。**

> **心智模型 ③：`Factuality ≠ Groundedness`。事实可能是真的，但当前证据未必支持。**

> **心智模型 ④：`AnswerLevelEval` 应尽可能拆到 `ClaimLevelEval`，否则很难定位幻觉。**

> **心智模型 ⑤：`CitationPresent ≠ CitationCorrect`，而 `CitationCorrect ≠ CitationComplete`。**

> **心智模型 ⑥：`LongExplanation ≠ GoodReasoning`。解释长度不能代表推理质量。**

> **心智模型 ⑦：`LLMJudge ≠ GroundTruth`。LLM Judge 是扩展评测器，不是最终真相来源。**

> **心智模型 ⑧：`GoodGeneration` 包括正确拒答，知道什么时候不回答也是能力。**

> **心智模型 ⑨：`RubricScore ≠ CriticalSafety`。高平均分不能掩盖编造政策、伪造引用等关键失败。**

---

# 二十二、下一阶段：第九课 · 第 6 阶段
# RAG Evaluation：Retrieval、Ranking、Context、Generation 分层评测

最关键的边界：

\[
\boxed{
RAGFailure
\neq
LLMFailure
}
\]

并建立：

# `ProcurementRAGEvalPolicy_V0.1`

---

<!-- LESSON 09 STAGE 05 END -->


<!-- LESSON 09 STAGE 06 START -->

# 第九课 · 第 6 阶段
# RAG Evaluation：Retrieval、Ranking、Context、Generation 分层评测
## RAG 回答错了，到底是没检索到、排错了、上下文组装错了，还是 LLM 没用好证据？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **RAGFailure ≠ LLMFailure。RAG 错误必须分层归因。**
2. **RetrievedContext = LLMVisibleWorld。Retriever 决定模型实际看到的证据世界。**
3. **RetrievalRecall ≠ RankingQuality。找到了和排对了是两个问题。**
4. **RetrievedDocs ≠ FinalContext。Context Builder 还可能丢证据或引入噪声。**
5. **GoodContext ≠ GoodAnswer。上下文正确不代表生成一定正确。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Rank` | LoRA Rank：低秩增量的容量参数 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `Recall` | 召回率：真实风险中被系统成功找出的比例 |
| `Precision` | 精确率：系统报出的风险中真正成立的比例 |
| `Citation` | 引用：把生成结论和具体来源建立可追踪链接 |

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

RAG 系统最终只给用户一个答案。

但内部至少经历：

```text
Query
↓
Retrieval
↓
Ranking
↓
Context Construction
↓
Generation
```

如果最终答错，

不能直接说：

> “LLM 不行。”

所以本阶段第一条边界：

\[
\boxed{
RAGFailure
\neq
LLMFailure
}
\]

本阶段最终形成：

# `ProcurementRAGEvalPolicy_V0.1`

---

# 一、RAG 必须分层评测

完整链路：

\[
\boxed{
Retrieval
\rightarrow
Ranking
\rightarrow
Context
\rightarrow
Generation
}
\]

每一层都可能失败。

所以：

\[
\boxed{
EndToEndFailure
需要
LayerAttribution
}
\]

---

# 二、Retrieval Recall：有没有把正确证据捞上来？

如果 Gold Evidence 已知，

可以看：

# Recall@K
## 前 K 个结果中的召回率

概念上：

\[
Recall@K
=
\frac{
RetrievedRelevant@K
}{
TotalRelevant
}
\]

如果正确证据根本不在 Top-K：

> 后面的 LLM 再强也没用。

所以：

\[
\boxed{
MissingEvidence
是上游硬上限
}
\]

---

# 三、核心心智模型 ①
# `Retriever` 决定 LLM 能看到什么世界

RAG 的 LLM 并不是直接面对整个知识库。

它面对的是：

> Retriever 选出来的一小块世界。

所以：

\[
\boxed{
RetrievedContext
=
LLMVisibleWorld
}
\]

如果可见世界错了，

生成质量上限会直接被限制。

---

# 四、Precision@K：捞上来的东西有多少真的相关？

\[
Precision@K
=
\frac{
RelevantRetrieved@K
}{
K
}
\]

Recall 高但 Precision 很低：

> 大量噪声上下文会挤占 Context。

所以：

\[
\boxed{
MoreRetrieved
\neq
BetterContext
}
\]

---

# 五、MRR：正确答案第一次出现得有多靠前？

# Mean Reciprocal Rank
## 平均倒数排名

如果第一个相关结果排名为：

\[
r
\]

则：

\[
RR=\frac{1}{r}
\]

越靠前越好。

适合：

> 关注第一个关键证据是否足够靠前。

---

# 六、nDCG：多个相关证据有不同价值时怎么办？

# nDCG
## 归一化折损累计增益

适合：

> 相关性有等级、并且排序重要的场景。

例如：

```text
权威法规 = 高相关
地方解读 = 中相关
论坛讨论 = 低相关
```

nDCG 可以同时考虑：

> 相关度和排名位置。

---

# 七、核心心智模型 ②
# `Retrieval` 和 `Ranking` 是两个问题

Retriever 可能：

> 已经把正确文档找到了。

但 Reranker：

> 把它排到很后面。

所以：

\[
\boxed{
RetrievalRecall
\neq
RankingQuality
}
\]

必须分别评。

---

# 八、Context Construction：Top-K 正确也不代表最终 Context 正确

拿到 Top-K 文档后还会发生：

```text
Chunk Merge
Chunk Dedup
Context Truncation
Section Selection
Citation Mapping
```

如果关键段落被：

> 截断、覆盖、重复噪声挤掉，

最终 Context 仍然可能失败。

所以：

\[
\boxed{
RetrievedDocs
\neq
FinalContext
}
\]

---

# 九、Context Recall / Precision

可以定义：

# Context Recall
最终 Context 覆盖了多少 Gold Evidence。

# Context Precision
最终 Context 中有多少内容真正对回答有帮助。

这能区分：

```text
Retriever找到了
但Context Builder丢了
```

和：

```text
Retriever本身没找到
```

---

# 十、核心心智模型 ③
# `ContextBudget` 是有限资源

Context Window 有限。

多塞一个低价值 Chunk，

就可能挤掉一个高价值 Chunk。

所以：

\[
\boxed{
ContextSelection
=
BudgetAllocation
}
\]

这和第八课 Mixture 的思想非常像：

> 有限资源必须优先分配给高价值信息。

---

# 十一、Generation Groundedness：LLM 有没有真正用好 Context？

即使 Context 完全正确，

LLM 仍可能：

```text
忽略关键证据
误读证据
引用错段落
加入外部记忆
过度推断
```

所以要评：

```text
Answer Correctness
Groundedness
Citation Correctness
Evidence Coverage
```

因此：

\[
\boxed{
GoodContext
\neq
GoodAnswer
}
\]

---

# 十二、核心心智模型 ④
# `RAGQuality` 是链路乘积，而不是单点能力

概念上可以理解：

\[
\boxed{
RAGQuality
\approx
Retrieval
\times
Ranking
\times
Context
\times
Generation
}
\]

不是严格数学乘法。

它强调：

> 任一关键环节接近零，整体就会明显受限。

---

# 十三、No-answer 样本为什么必须进 Benchmark？

如果知识库里根本没有答案，

正确行为应该：

> 不回答 / 请求更多证据。

所以 RAG Benchmark 必须包含：

# Unanswerable Items
## 不可回答样本

否则系统可能养成：

> 每题必答。

所以：

\[
\boxed{
CanAnswer
+
CanAbstain
=
ReliableRAG
}
\]

---

# 十四、Gold Evidence 怎么定义？

RAG 评测最好不仅有：

```text
Gold Answer
```

还要有：

```text
Gold Document IDs
Gold Chunk IDs
Gold Evidence Spans
```

这样才能评：

```text
Retrieval
Ranking
Context
Citation
```

所以：

\[
\boxed{
RAGGold
=
AnswerGold
+
EvidenceGold
}
\]

---

# 十五、核心心智模型 ⑤
# `Answer-only Gold` 不足以诊断 RAG

如果只有最终答案，

你无法知道：

> 检索器到底有没有找到正确证据。

因此 RAG Gold 必须更丰富。

---

# 十六、Failure Attribution：一次错误应该归到哪层？

可以定义：

```text
R1 Retrieval Miss
R2 Ranking Failure
R3 Context Drop
R4 Context Noise
R5 Evidence Misuse
R6 Unsupported Generation
R7 Wrong Citation
R8 Failed Abstention
```

然后每个失败样本尽量标：

# Primary Failure
## 主失败原因

以及：

# Secondary Failures
## 次级失败原因

这样才能做真正工程优化。

---

# 十七、Counterfactual Eval：把正确证据给模型，看看它还会不会错

一个非常有价值的诊断方法：

> 直接把 Gold Evidence 放进 Context。

如果此时模型答对：

> 原问题更可能在 Retrieval / Ranking。

如果仍答错：

> 更可能在 Generation / Reasoning。

所以：

\[
\boxed{
OracleContextEval
=
FailureIsolationTool
}
\]

---

# 十八、核心心智模型 ⑥
# `Oracle Context` 可以测 RAG 的“生成上限”

它不是生产配置。

而是诊断实验：

> 如果给模型完美上下文，它最高能做到什么？

这样可以区分：

```text
Retriever瓶颈
vs
Generator瓶颈
```

---

# 十九、RAG 评测还要记录成本和延迟吗？

需要。

因为：

```text
Top-K更大
Reranker更复杂
Context更长
```

可能提升质量，

但也会增加：

```text
Latency
Token Cost
Compute Cost
```

所以 RAG 评测应保留：

```text
quality
latency
cost
```

三个坐标。

---

# 二十、核心心智模型 ⑦
# `BestOfflineQuality` 不一定是 `BestProductionRAG`

生产系统还要考虑：

\[
\boxed{
Quality
+
Latency
+
Cost
}
\]

因此：

\[
\boxed{
RAGSelection
=
MultiObjectiveDecision
}
\]

---

# 二十一、本阶段正式工程产物
# `ProcurementRAGEvalPolicy_V0.1`

至少锁定：

```text
rag_eval_policy_version

gold_answer_required

gold_document_ids

gold_chunk_ids

gold_evidence_spans

retrieval_recall_at_k

precision_at_k

mrr

ndcg

context_recall

context_precision

context_budget

ranking_eval

oracle_context_eval

answer_correctness

groundedness

citation_correctness

citation_completeness

unanswerable_items

abstention_metric

failure_taxonomy

latency_metric

cost_metric

release_gate
```

---

# 二十二、本阶段最重要的 8 个核心心智模型

> **心智模型 ①：`RAGFailure ≠ LLMFailure`。RAG 错误必须分层归因。**

> **心智模型 ②：`RetrievedContext = LLMVisibleWorld`。Retriever 决定模型实际看到的证据世界。**

> **心智模型 ③：`RetrievalRecall ≠ RankingQuality`。找到了和排对了是两个问题。**

> **心智模型 ④：`RetrievedDocs ≠ FinalContext`。Context Builder 还可能丢证据或引入噪声。**

> **心智模型 ⑤：`GoodContext ≠ GoodAnswer`。上下文正确不代表生成一定正确。**

> **心智模型 ⑥：`RAGGold = AnswerGold + EvidenceGold`。只标答案不足以诊断 RAG。**

> **心智模型 ⑦：`OracleContextEval` 是隔离 Retriever 与 Generator 瓶颈的重要工具。**

> **心智模型 ⑧：`BestOfflineQuality ≠ BestProductionRAG`。生产选择必须同时考虑质量、延迟和成本。**

---

# 二十三、下一阶段：第九课 · 第 7 阶段
# Agent Evaluation：Planning、Tool、State、Recovery、Safety、Completion

最关键的边界：

\[
\boxed{
ToolCallSuccess
\neq
TaskCompletion
}
\]

并建立：

# `ProcurementAgentEvalPolicy_V0.1`

---

<!-- LESSON 09 STAGE 06 END -->


<!-- LESSON 09 STAGE 07 START -->

# 第九课 · 第 7 阶段
# Agent Evaluation：Planning、Tool、State、Recovery、Safety、Completion
## Agent 调用工具成功，为什么仍然可能算任务失败？怎样评测一个会计划、执行、恢复和改变真实状态的系统？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **ToolCallSuccess ≠ TaskCompletion。工具调用成功不等于真实任务完成。**
2. **AgentEval = OutcomeEval + TrajectoryEval。结果和执行轨迹必须同时评。**
3. **Action = Tool + Arguments。只评工具名远远不够。**
4. **HappyPathSuccess ≠ RobustAgent。没有故障注入就测不出恢复能力。**
5. **ActionSuccess ≠ PolicySuccess。成功执行的动作仍可能违反权限或安全策略。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `State` | 状态：保存任务进度、事实和待办 |
| `Planning` | 任务规划：把目标拆成可执行、带依赖的子任务 |
| `Recovery` | 恢复：工具失败或中断后安全重试、降级和继续 |
| `ANN` | ANN/近似最近邻：在大规模向量中快速寻找相似项 |
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

Agent 和普通 LLM 最大区别是：

> 它不只是“说”，还会“做”。

所以评测 Agent 不能只看：

```text
最终文本像不像标准答案
```

因为 Agent 可能：

```text
调用了错误工具
参数填错
重复提交
状态丢失
遇到失败不会恢复
做了不该做的副作用
```

因此第一条边界：

\[
\boxed{
ToolCallSuccess
\neq
TaskCompletion
}
\]

本阶段最终形成：

# `ProcurementAgentEvalPolicy_V0.1`

---

# 一、Agent Evaluation 为什么必须看 Trajectory？

# Trajectory
## 执行轨迹

包括：

```text
Observe
Plan
Choose Tool
Call Tool
Receive Result
Update State
Replan
Complete
```

两个 Agent 最终都成功，

但一个可能：

```text
2次工具调用完成
```

另一个：

```text
12次调用
3次错误
2次重试
1次危险副作用
```

所以：

\[
\boxed{
SameOutcome
\neq
SameAgentQuality
}
\]

---

# 二、核心心智模型 ①
# `Outcome` 和 `Trajectory` 都要评

Outcome 回答：

> 最终任务完成了吗？

Trajectory 回答：

> 是不是用正确、稳定、安全的方式完成？

因此：

\[
\boxed{
AgentEval
=
OutcomeEval
+
TrajectoryEval
}
\]

---

# 三、Planning：计划是不是合理？

可以评：

```text
Goal Decomposition
目标拆解

Step Ordering
步骤顺序

Dependency Awareness
依赖意识

Unnecessary Steps
冗余步骤

Replanning
动态重规划
```

但注意：

> 不一定要求 Agent 把“思维链”输出出来。

更适合评：

```text
Observable Plan
可观察执行计划

Tool Sequence
工具序列
```

---

# 四、Tool Selection：有没有选对工具？

例如任务需要：

```text
查询预算
```

Agent 却去：

```text
搜索法规
```

即使工具调用成功，

也没意义。

所以：

\[
\boxed{
ToolAvailability
\neq
ToolAppropriateness
}
\]

要评：

```text
tool_selected
gold_tool
tool_selection_correct
```

---

# 五、Tool Arguments：工具对了，参数也可能错

例如正确工具：

```text
query_project_budget
```

但：

```text
project_id填错
date范围错
currency单位错
```

所以：

\[
\boxed{
CorrectTool
\neq
CorrectAction
}
\]

真正 Action：

\[
\boxed{
Action
=
Tool
+
Arguments
}
\]

---

# 六、核心心智模型 ②
# `ToolCall` 是结构化行为，不只是函数名

Agent Eval 至少要拆：

```text
Tool Name
Arguments
Timing
Permission
Result Handling
```

这才是真正工具评测。

---

# 七、State：Agent 是否正确维护真实状态？

Agent 可能跨多步处理：

```text
项目A
预算100万
已经提交一次
等待审批
```

如果后面突然：

```text
把项目A当成项目B
重复提交
忘记已审批状态
```

就是：

# State Error
## 状态错误

所以：

\[
\boxed{
AgentMemory
必须以
StateConsistency
评测
}
\]

不是看它“记得多不多”。

---

# 八、Recovery：工具失败时怎么办？

生产工具一定会失败：

```text
Timeout
Rate Limit
Permission Error
Temporary Unavailable
Invalid Input
```

Agent 是否：

```text
重试
换工具
修参数
请求用户补充
转人工
```

决定了：

# Recovery Quality
## 故障恢复质量

所以 Benchmark 必须有：

# Fault Injection
## 故障注入

主动模拟失败。

---

# 九、核心心智模型 ③
# `HappyPathSuccess` 不等于 `RobustAgent`

如果 Benchmark 永远：

```text
工具正常
网络正常
输入完整
权限齐全
```

Agent 分数会虚高。

所以：

\[
\boxed{
Robustness
需要
FailureScenarios
}
\]

---

# 十、Task Completion：到底怎么算“完成”？

必须提前定义：

# Success Condition
## 成功条件

例如：

```text
预算查询任务
Success =
返回正确预算
AND
项目ID正确
AND
币种正确
AND
没有修改任何状态
```

再比如：

```text
提交审批任务
Success =
正确提交
AND
只提交一次
AND
状态更新正确
AND
生成审批记录
```

所以：

\[
\boxed{
Completion
必须MachineCheckable
}
\]

---

# 十一、Side Effect：Agent 最大风险之一

Agent 不只是读取。

有些工具会：

```text
写入
修改
提交
删除
发送
审批
```

所以必须评：

# Side Effect Safety
## 副作用安全

包括：

```text
是否获得必要确认
是否越权
是否重复执行
是否可回滚
是否记录审计日志
```

---

# 十二、核心心智模型 ④
# `SuccessfulAction` 也可能是 `UnsafeAction`

如果 Agent 成功删除了不该删的记录，

技术上：

> API 调用成功。

但系统上：

> 严重失败。

所以：

\[
\boxed{
ActionSuccess
\neq
PolicySuccess
}
\]

---

# 十三、Idempotency：重复调用会不会造成重复副作用？

# Idempotency
## 幂等性

例如：

> “提交采购审批”

如果网络超时，

Agent 不确定是否已经提交。

它再次调用：

> 会不会重复创建两个审批？

所以：

\[
\boxed{
RetrySafety
需要
IdempotencyAwareness
}
\]

Benchmark 应设计：

> 第一次调用成功但响应丢失

这种场景。

---

# 十四、Human-in-the-loop：什么时候应该停下来找人？

Agent 不应该什么都自己做。

可以评：

```text
Escalation Correctness
升级人工是否正确

Confirmation Timing
确认时机

Uncertainty Handling
不确定性处理
```

所以：

\[
\boxed{
GoodAgent
包括
KnowingWhenToStop
}
\]

---

# 十五、Cost / Latency：完成同一任务的代价不同

可以记录：

```text
tool_calls
tokens
latency
retries
external_cost
```

于是：

\[
\boxed{
AgentEfficiency
=
GoalCompletion
per
ResourceCost
}
\]

不是严格一个固定公式，

而是工程思想。

---

# 十六、核心心智模型 ⑤
# `MoreToolCalls` 不代表 `MoreReasoning`

Agent 乱试工具，

可能产生很多调用。

所以：

\[
\boxed{
ToolCallCount
不是
IntelligenceMetric
}
\]

更重要的是：

> 是否必要、正确、有效。

---

# 十七、Agent Eval 需要真实工具还是 Mock？

两种都需要。

# Mock / Sandbox Tools
## 模拟工具

优点：

```text
稳定
可复现
无真实副作用
便于Fault Injection
```

适合 Benchmark。

# Live Tools
## 真实工具

能检验：

> 真正系统集成。

但不稳定、成本高、风险高。

所以：

\[
\boxed{
OfflineAgentEval
+
ControlledLiveEval
}
\]

更完整。

---

# 十八、Agent Failure Taxonomy

建议至少：

```text
A1 Goal Misunderstanding
目标理解错误

A2 Planning Error
计划错误

A3 Wrong Tool
工具选择错误

A4 Wrong Arguments
参数错误

A5 State Error
状态错误

A6 Recovery Failure
恢复失败

A7 Permission Violation
权限违规

A8 Unsafe Side Effect
危险副作用

A9 Duplicate Action
重复动作

A10 Failed Escalation
该转人工未转

A11 Incomplete Task
任务未完成
```

---

# 十九、核心心智模型 ⑥
# `Agent Failure` 必须区分“没完成”和“危险地完成”

一个 Agent：

> 没完成审批。

另一个 Agent：

> 完成了审批，但越权提交。

第二种可能更危险。

所以：

\[
\boxed{
CompletionRate
不能替代
SafetyRate
}
\]

---

# 二十、本阶段正式工程产物
# `ProcurementAgentEvalPolicy_V0.1`

至少锁定：

```text
agent_eval_policy_version

task_definition

success_condition

trajectory_capture

planning_eval

tool_selection_eval

tool_argument_eval

state_consistency_eval

fault_injection_suite

recovery_eval

side_effect_policy

permission_eval

idempotency_eval

human_escalation_eval

completion_metric

safety_metric

latency_metric

cost_metric

mock_tool_policy

live_tool_policy

failure_taxonomy

release_gate
```

---

# 二十一、本阶段最重要的 9 个核心心智模型

> **心智模型 ①：`ToolCallSuccess ≠ TaskCompletion`。工具调用成功不等于真实任务完成。**

> **心智模型 ②：`AgentEval = OutcomeEval + TrajectoryEval`。结果和执行轨迹必须同时评。**

> **心智模型 ③：`Action = Tool + Arguments`。只评工具名远远不够。**

> **心智模型 ④：`HappyPathSuccess ≠ RobustAgent`。没有故障注入就测不出恢复能力。**

> **心智模型 ⑤：`ActionSuccess ≠ PolicySuccess`。成功执行的动作仍可能违反权限或安全策略。**

> **心智模型 ⑥：`RetrySafety` 需要 Idempotency Awareness。重试可能制造重复副作用。**

> **心智模型 ⑦：`GoodAgent` 包括知道什么时候停下来、确认或转人工。**

> **心智模型 ⑧：`ToolCallCount ≠ IntelligenceMetric`。工具调用越多不等于 Agent 越聪明。**

> **心智模型 ⑨：`CompletionRate ≠ SafetyRate`。完成任务和安全完成是两个不同目标。**

---

# 二十二、下一阶段：第九课 · 第 8 阶段
# Slice Evaluation：Risk Type、行业、地区、难度、Hard Case

最关键的边界：

\[
\boxed{
OverallScore
\neq
SliceReliability
}
\]

并建立：

# `ProcurementSliceEvalPolicy_V0.1`

---

<!-- LESSON 09 STAGE 07 END -->


<!-- LESSON 09 STAGE 08 START -->

# 第九课 · 第 8 阶段
# Slice Evaluation：Risk Type、行业、地区、难度、Hard Case
## 为什么总体分数很好，系统仍然可能在最关键的采购场景里失败？怎样把平均成绩拆成真正能指导上线决策的风险切片？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **OverallScore ≠ SliceReliability。总体平均不能证明所有关键场景都可靠。**
2. **Average 会隐藏 Heterogeneity。不同子群性能可能差异巨大。**
3. **Difficulty ≠ LengthOnly。真正难度来自语义边界、结构、证据、噪声和稀有度。**
4. **SingleSlice 可能遗漏 InteractionFailure，交叉切片是生产评测的重要补充。**
5. **PointEstimate ≠ Certainty。Slice 指标必须结合 Support 和不确定性。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `OCR` | OCR：把扫描图像中的文字转换成机器可读文本 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `Recall` | 召回率：真实风险中被系统成功找出的比例 |
| `Accuracy` | 准确率：全部样本中判断正确的比例 |
| `Confidence Interval` | 置信区间：表示有限样本指标的不确定范围 |

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

到第 7 阶段，我们已经分别学会：

```text
分类评测
生成评测
RAG评测
Agent评测
```

但现在会遇到一个非常危险的问题：

> **总体指标可能很好看，但关键场景可能已经崩了。**

假设一个系统：

\[
OverallAccuracy=93\%
\]

如果进一步拆开：

```text
普通公告：97%

简单采购需求：95%

高风险限制性条款：61%

OCR噪声文档：58%

跨章节复杂案例：54%
```

那么 93% 并不能说明：

> “系统很可靠。”

所以本阶段第一条边界：

\[
\boxed{
OverallScore
\neq
SliceReliability
}
\]

本阶段最终形成：

# `ProcurementSliceEvalPolicy_V0.1`

---

# 一、Slice 到底是什么？

# Slice
## 评测切片

指：

> 按某种业务属性，把 Benchmark 切成一个有明确含义的子集。

例如：

```text
Risk Type
风险类型

Industry
行业

Region
地区

Document Type
文档类型

Difficulty
难度

Document Length
文档长度

OCR Quality
OCR质量

Answerability
可回答性

Rare Case
稀有案例
```

所以：

\[
\boxed{
Slice
=
SemanticallyMeaningfulSubset
}
\]

不是任意分组。

---

# 二、核心心智模型 ①
# `Average` 会隐藏 `Heterogeneity`

不同场景的难度和风险并不相同。

所以：

\[
\boxed{
AveragePerformance
可以掩盖
SubgroupFailure
}
\]

这和统计学里：

> 总体平均不等于每个子群都稳定，

是同一个问题。

---

# 三、Risk Type Slice：按风险类型切

例如：

```text
地域限制

所有制限制

注册资本要求

特定资质

业绩要求

评分倾向

品牌指向

本地化服务

中小企业政策
```

每个风险类型都应该有：

```text
support
precision
recall
f1
critical_fn
```

这样才能发现：

> 哪些风险类型系统最容易漏。

---

# 四、Industry Slice：按行业切

采购语言在不同行业可能差异很大：

```text
IT
医疗
工程
物业
检测
咨询
教育
交通
```

一个在 IT 数据上训练很多的模型，

可能：

> 医疗和工程明显更弱。

所以：

\[
\boxed{
DomainCoverage
必须被
SliceMetric
验证
}
\]

不能只看 Corpus 里“有这个行业”。

---

# 五、Region Slice：地区切片为什么重要？

不同地区可能存在：

```text
文书格式差异
政策表达差异
项目规模差异
公开文本质量差异
```

Region Slice 不是为了：

> 比较地区优劣。

而是为了：

> 检查系统是否在特定地区分布上明显失效。

---

# 六、Difficulty Slice：难度必须显式化

可以定义：

```text
Easy
明确关键词、短文本、单一条件

Medium
多个条件、需要局部上下文

Hard
跨章节、隐含约束、多个规则冲突

Extreme
证据不完整、OCR噪声、边界案例
```

所以：

\[
\boxed{
Benchmark
不能只有
IID Easy Cases
}
\]

必须有真正困难样本。

---

# 七、核心心智模型 ②
# `Hard Case` 不是“更长”，而是“更容易暴露错误边界”

真正的 Hard Case 可能：

```text
文本很短
但语义边界极细
```

例如只改一个限定词，

结论就不同。

所以：

\[
\boxed{
Difficulty
\neq
LengthOnly
}
\]

难度应该来自：

```text
语义
结构
证据
上下文
稀有度
噪声
决策边界
```

---

# 八、Intersection Slice：为什么单维切片还不够？

假设：

```text
医疗总体 F1 = 0.86
OCR总体 F1 = 0.84
```

但：

```text
医疗 × OCR差
F1 = 0.52
```

单维平均会把问题藏住。

这叫：

# Intersection Slice
## 交叉切片

例如：

```text
医疗 × OCR差
工程 × 长文档
高风险 × 稀有类型
地区A × 特定文档类型
```

所以：

\[
\boxed{
SingleSlice
可能遗漏
InteractionFailure
}
\]

---

# 九、核心心智模型 ③
# `Intersection Failure` 往往是真实生产事故来源

生产问题经常不是：

> 单一条件。

而是：

> 多个困难因素叠加。

所以 Release Gate 不能只看单维 Slice。

---

# 十、Slice Support：切片样本数太小怎么办？

如果某个 Slice：

```text
只有5条
```

即使：

```text
Accuracy = 40%
```

统计不确定性也很大。

所以每个 Slice 要记录：

# Support
## 样本量

并设：

```text
minimum_support
```

如果样本太少：

> 应标记为 Low Confidence Slice，

而不是直接做强结论。

---

# 十一、Confidence Interval：为什么 Slice 指标需要不确定性？

样本数有限时，

Metric 本身有波动。

可以通过：

```text
Bootstrap
自助法

Binomial Interval
二项区间
```

估计置信区间。

所以：

\[
\boxed{
PointEstimate
\neq
Certainty
}
\]

例如：

```text
Recall = 0.80
```

没有样本量和区间，

信息是不完整的。

---

# 十二、核心心智模型 ④
# `Small Slice` 的价值高，但结论要更谨慎

稀有高风险场景：

> 样本本来就少。

不能因为少就不评。

但也不能把 3/5：

> 当成稳定的 60%。

所以：

\[
\boxed{
RareCriticalSlice
=
HighImportance
+
HighUncertainty
}
\]

两者要同时处理。

---

# 十三、Worst-slice Metric：为什么要看最差切片？

可以记录：

# Worst Slice Score
## 最差切片表现

它告诉我们：

> 系统最弱的已知区域在哪里。

所以：

\[
\boxed{
AverageScore
+
WorstSliceScore
}
\]

通常比只看平均分更有意义。

---

# 十四、Critical Slice Gate：关键切片必须有硬门槛

例如：

```text
高风险漏检 Recall >= threshold

伪造政策 Slice critical_error = 0

不可回答样本 Abstention >= threshold
```

所以：

\[
\boxed{
CriticalSlice
需要
HardGate
}
\]

不是让它被综合分平均掉。

---

# 十五、核心心智模型 ⑤
# `HighAverage + CriticalSliceFailure = ReleaseFail`

这是 Slice Evaluation 最重要的工程结论之一。

如果关键业务切片失败：

\[
\boxed{
ReleaseGate=False
}
\]

即使平均分很漂亮。

---

# 十六、Slice Registry：切片定义必须版本化

不要临时：

> “这次我们看一下医疗。”

而应该维护：

# Slice Registry
## 切片注册表

至少记录：

```text
slice_id

slice_name

definition

filter_rule

business_reason

criticality

minimum_support

metric_set

owner

version
```

这样同一个 Slice 在多个版本间才可比较。

---

# 十七、Slice Drift：Benchmark 更新后切片占比变化怎么办？

例如：

```text
V1.0
医疗占10%

V1.1
医疗占25%
```

总体分数变化可能来自：

> Benchmark Composition 变了。

所以：

\[
\boxed{
OverallScoreChange
可能来自
SliceMixChange
}
\]

这就是为什么：

> Benchmark Versioning 后面要记录分布变化。

---

# 十八、核心心智模型 ⑥
# `Score Change` 不一定是 `Model Change`

如果 Benchmark Slice Mix 变了，

即使模型完全没变，

总分也可能变。

所以比较时必须确认：

```text
same benchmark version
same slice composition
same protocol
```

---

# 十九、Hard Case Registry：困难案例要不要单独维护？

建议维护：

# Hard Case Registry
## 难例注册表

来源可以是：

```text
生产事故
专家争议
模型历史失败
Red Team
Synthetic Hard Case
边界案例
```

每条难例要记录：

```text
why_hard
failure_mode
gold_reason
criticality
```

这样 Hard Case 不只是：

> “比较难的题”。

而是：

> 已知模型能力边界的证据。

---

# 二十、Slice 与 Error Taxonomy 怎样结合？

最有价值的分析往往是：

```text
Slice × Error Type
```

例如：

```text
医疗 × Retrieval Miss
工程 × Wrong Citation
OCR差 × Extraction Error
高风险 × Failed Abstention
```

这比：

> “医疗分数低”

更容易指导工程修复。

---

# 二十一、核心心智模型 ⑦
# `Slice` 告诉你“哪里坏”，`Error Taxonomy` 告诉你“怎么坏”

两者结合：

\[
\boxed{
FailureDiagnosis
=
Where
+
How
}
\]

---

# 二十二、本阶段正式工程产物
# `ProcurementSliceEvalPolicy_V0.1`

至少锁定：

```text
slice_policy_version

slice_registry

risk_type_slices

industry_slices

region_slices

document_type_slices

difficulty_slices

length_slices

ocr_quality_slices

answerability_slices

rare_case_slices

intersection_slice_policy

minimum_support

confidence_interval_policy

worst_slice_metric

critical_slice_gate

slice_drift_monitoring

hard_case_registry

slice_error_cross_analysis

release_gate
```

每个 Slice 至少记录：

```text
slice_id

definition

support

metrics

confidence_interval

criticality

error_distribution

historical_baseline

current_score

delta

release_status
```

---

# 二十三、本阶段最重要的 9 个核心心智模型

> **心智模型 ①：`OverallScore ≠ SliceReliability`。总体平均不能证明所有关键场景都可靠。**

> **心智模型 ②：`Average` 会隐藏 `Heterogeneity`。不同子群性能可能差异巨大。**

> **心智模型 ③：`Difficulty ≠ LengthOnly`。真正难度来自语义边界、结构、证据、噪声和稀有度。**

> **心智模型 ④：`SingleSlice` 可能遗漏 `InteractionFailure`，交叉切片是生产评测的重要补充。**

> **心智模型 ⑤：`PointEstimate ≠ Certainty`。Slice 指标必须结合 Support 和不确定性。**

> **心智模型 ⑥：`HighAverage + CriticalSliceFailure = ReleaseFail`。关键切片不能被平均分洗掉。**

> **心智模型 ⑦：`ScoreChange` 可能来自 Slice Mix 变化，不一定来自模型变化。**

> **心智模型 ⑧：`HardCaseRegistry` 是能力边界资产，不只是难题集合。**

> **心智模型 ⑨：`Slice + ErrorTaxonomy = Where + How`。两者结合才能真正定位失败。**

---

# 二十四、下一阶段：第九课 · 第 9 阶段
# Calibration、Abstention、OOD 与 Risk-Coverage

最关键的边界：

\[
\boxed{
ConfidenceScore
\neq
ProbabilityOfBeingCorrect
}
\]

并建立：

# `ProcurementCalibrationAbstentionPolicy_V0.1`

---

<!-- LESSON 09 STAGE 08 END -->


<!-- LESSON 09 STAGE 09 START -->

# 第九课 · 第 9 阶段
# Calibration、Abstention、OOD 与 Risk-Coverage
## 模型什么时候应该说“我不知道”？一个 0.9 的置信度真的代表 90% 正确吗？怎样把不确定性变成可控制的业务风险？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **ConfidenceScore ≠ ProbabilityOfBeingCorrect。置信分必须通过真实数据校准。**
2. **Accuracy ≠ Calibration。答得准和知道自己有多确定是两个能力。**
3. **ReliableAI = AnswerCorrectly + AbstainAppropriately。合理拒答是可靠性的一部分。**
4. **AccuracyWithoutCoverage 可能误导，拒答系统必须同时报告 Coverage。**
5. **RiskCoverage 是选择性预测的核心权衡。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Calibration` | 校准：使模型置信度更接近实际正确率 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `OOD` | 分布外数据：明显偏离训练/验证分布的新输入 |
| `Threshold` | 阈值：把连续分数转成业务动作的决策门槛 |
| `Accuracy` | 准确率：全部样本中判断正确的比例 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |

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

一个系统最危险的状态，不一定是：

> 经常答错。

而可能是：

> **答错时仍然非常自信。**

所以第九课走到这里，必须正式处理：

# Calibration
## 置信度校准

# Abstention
## 拒答 / 暂不判断

# OOD
## 分布外输入

本阶段第一条边界：

\[
\boxed{
ConfidenceScore
\neq
ProbabilityOfBeingCorrect
}
\]

本阶段最终形成：

# `ProcurementCalibrationAbstentionPolicy_V0.1`

---

# 一、Calibration 到底在校准什么？

假设模型对 100 个样本都给：

```text
confidence = 0.8
```

如果这些样本中大约：

```text
80%
```

真的正确，

我们可以说：

> 在这个区间里校准较好。

如果只有：

```text
50%
```

正确，

模型就：

# Overconfident
## 过度自信

所以：

\[
\boxed{
Calibration
=
Confidence
与
ObservedAccuracy
的一致程度
}
\]

---

# 二、核心心智模型 ①
# `Confidence` 必须被经验数据验证

模型自己输出：

```text
0.95
```

不代表客观上：

> 95% 正确。

所以：

\[
\boxed{
SelfReportedConfidence
需要
EmpiricalCalibration
}
\]

---

# 三、Reliability Diagram：怎样直观看校准？

把预测置信度分桶：

```text
0.5~0.6
0.6~0.7
0.7~0.8
0.8~0.9
0.9~1.0
```

每个桶比较：

```text
平均Confidence
vs
真实Accuracy
```

画出来就是：

# Reliability Diagram
## 可靠性图

理想情况：

> 接近对角线。

---

# 四、ECE：Expected Calibration Error

# ECE
## 期望校准误差

概念上：

\[
ECE
=
\sum_b
\frac{|B_b|}{N}
\left|
acc(B_b)-conf(B_b)
\right|
\]

它衡量：

> 各置信度区间的预测置信与真实正确率差距。

ECE 越低：

> 通常表示校准更好。

但：

\[
\boxed{
ECE
依赖
Binning
}
\]

所以必须记录分桶策略。

---

# 五、Brier Score：概率预测也可以看平方误差

二分类时：

\[
Brier
=
\frac{1}{N}
\sum_i
(p_i-y_i)^2
\]

它同时惩罚：

> 错误概率和过度自信。

所以：

\[
\boxed{
CalibrationMetric
不止一个
}
\]

不要把 ECE 当唯一真理。

---

# 六、核心心智模型 ②
# `Accuracy` 高不代表 `Calibration` 好

一个模型可能：

```text
Accuracy = 90%
```

但每次都输出：

```text
confidence = 0.99
```

它仍然可能：

> 严重过度自信。

所以：

\[
\boxed{
Discrimination
\neq
Calibration
}
\]

会不会分对，

和知不知道自己有多确定，

是两个能力。

---

# 七、Abstention：为什么拒答是一种能力？

如果模型不确定，

可以输出：

```text
当前证据不足，建议人工复核
```

而不是：

> 硬猜。

这叫：

# Abstention
## 拒答 / 暂不判断

所以：

\[
\boxed{
ReliableAI
=
AnswerCorrectly
+
AbstainAppropriately
}
\]

---

# 八、Abstention Threshold：什么时候拒答？

例如：

```text
confidence < 0.65
→ abstain
```

但阈值不能拍脑袋。

应该在 Validation 上根据：

```text
风险成本
人工复核容量
目标Coverage
错误容忍度
```

选择。

---

# 九、Coverage：系统到底回答多少问题？

\[
Coverage
=
\frac{AnsweredItems}{TotalItems}
\]

如果系统：

> 所有难题都拒答，

准确率可能非常高。

但 Coverage 很低。

所以：

\[
\boxed{
AccuracyWithoutCoverage
可能误导
}
\]

---

# 十、Risk-Coverage Curve

随着 Abstention Threshold 调整：

```text
Coverage下降
但错误风险也可能下降
```

于是可以画：

# Risk-Coverage Curve
## 风险—覆盖率曲线

它回答：

> 如果只让系统回答最有把握的 80% 样本，剩余错误率是多少？

所以：

\[
\boxed{
RiskCoverage
=
SelectivePredictionTradeoff
}
\]

---

# 十一、核心心智模型 ③
# `BestModel` 可能取决于目标 Coverage

模型 A：

> 100% Coverage 时更好。

模型 B：

> 只回答最有把握的 70% 时更可靠。

所以：

\[
\boxed{
ModelRanking
可能随
Coverage
变化
}
\]

---

# 十二、Selective Risk：只在已回答样本上看风险

可以定义：

\[
SelectiveRisk
=
ErrorRate
\text{ on answered items}
\]

随着 Coverage 改变，

Selective Risk 也改变。

这对于：

> 人机协同

尤其重要。

---

# 十三、OOD：什么是 Out-of-Distribution？

# OOD
## 分布外输入

例如训练和 Benchmark 主要是：

```text
政府采购文本
```

突然输入：

```text
医学诊断
证券交易
完全不同语言
极端新格式
```

系统可能仍然给出：

> 高置信回答。

所以：

\[
\boxed{
InDistributionConfidence
不能直接代表
OODReliability
}
\]

---

# 十四、核心心智模型 ④
# `LowConfidence` 和 `OOD` 不是同一个概念

有些 OOD 输入：

> 模型仍然非常自信。

有些 In-Distribution 难题：

> 模型置信度很低。

所以：

\[
\boxed{
OODDetection
\neq
ConfidenceThresholdOnly
}
\]

---

# 十五、OOD Benchmark 应该包含什么？

可以构造：

```text
Near-OOD
相近但超出训练边界

Far-OOD
完全不同领域

Novel Format
新文档格式

Novel Policy Pattern
新型规则表达

Adversarial Input
刻意诱导
```

并评：

```text
是否识别异常
是否降低置信
是否拒答
是否转人工
```

---

# 十六、Abstention 的错误也要分类

### Over-Abstention
过度拒答

> 本来能答，却总拒答。

### Under-Abstention
拒答不足

> 明明没把握还强答。

所以：

\[
\boxed{
AbstentionQuality
=
AvoidOverAbstain
+
AvoidUnderAbstain
}
\]

---

# 十七、核心心智模型 ⑤
# `AlwaysAnswer` 和 `AlwaysAbstain` 都不是可靠系统

真正目标是：

> 在错误成本和人工成本之间找到合适 Operating Point。

---

# 十八、人机协同：Abstain 以后发生什么？

拒答不是终点。

应该进入：

```text
Human Review
人工复核

Additional Retrieval
补充检索

Ask User
请求补充信息

Escalation
升级处理
```

所以：

\[
\boxed{
Abstention
=
RoutingDecision
}
\]

不是：

> “模型失败”。

---

# 十九、Calibration by Slice：总体校准好，不代表每个 Slice 都好

可能：

```text
总体ECE很低
```

但：

```text
医疗场景严重过度自信
OCR差样本严重过度自信
```

所以：

\[
\boxed{
Calibration
也需要
SliceEvaluation
}
\]

---

# 二十、核心心智模型 ⑥
# `WellCalibratedOverall` 不等于 `WellCalibratedEverywhere`

这和前一阶段完全衔接。

关键高风险 Slice：

> 需要单独看 Calibration。

---

# 二十一、Threshold 版本化

一旦上线使用：

```text
abstain_threshold = 0.67
```

它就是系统行为的一部分。

必须记录：

```text
threshold_version
selection_dataset
objective
effective_date
```

所以：

\[
\boxed{
Threshold
=
ProductionPolicy
}
\]

---

# 二十二、本阶段正式工程产物
# `ProcurementCalibrationAbstentionPolicy_V0.1`

至少锁定：

```text
calibration_policy_version

confidence_source

calibration_dataset

reliability_diagram

ece_policy

brier_score_policy

binning_policy

abstention_enabled

abstention_threshold

threshold_selection_policy

coverage_metric

selective_risk_metric

risk_coverage_curve

over_abstention_metric

under_abstention_metric

ood_taxonomy

near_ood_set

far_ood_set

ood_detection_policy

human_escalation_policy

slice_calibration

release_gate
```

---

# 二十三、本阶段最重要的 9 个核心心智模型

> **心智模型 ①：`ConfidenceScore ≠ ProbabilityOfBeingCorrect`。置信分必须通过真实数据校准。**

> **心智模型 ②：`Accuracy ≠ Calibration`。答得准和知道自己有多确定是两个能力。**

> **心智模型 ③：`ReliableAI = AnswerCorrectly + AbstainAppropriately`。合理拒答是可靠性的一部分。**

> **心智模型 ④：`AccuracyWithoutCoverage` 可能误导，拒答系统必须同时报告 Coverage。**

> **心智模型 ⑤：`RiskCoverage` 是选择性预测的核心权衡。**

> **心智模型 ⑥：`OODDetection ≠ ConfidenceThresholdOnly`。分布外输入不一定低置信。**

> **心智模型 ⑦：`AlwaysAnswer` 和 `AlwaysAbstain` 都不是好策略。**

> **心智模型 ⑧：`Abstention = RoutingDecision`。拒答应该进入人工、补检索或补信息流程。**

> **心智模型 ⑨：`Calibration` 也必须做 Slice Evaluation，关键场景不能被总体校准掩盖。**

---

# 二十四、下一阶段：第九课 · 第 10 阶段
# Benchmark Leakage、Contamination、Firewall 与 Test Governance

最关键的边界：

\[
\boxed{
NoExactDuplicate
\neq
NoContamination
}
\]

并建立：

# `ProcurementBenchmarkFirewallPolicy_V0.1`

---

<!-- LESSON 09 STAGE 09 END -->


<!-- LESSON 09 STAGE 10 START -->

# 第九课 · 第 10 阶段
# Benchmark Leakage、Contamination、Firewall 与 Test Governance
## 怎么防止训练集“偷看”测试集？为什么没有完全重复样本，也可能已经污染 Benchmark？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **NoExactDuplicate ≠ NoContamination。没有完全重复只能说明最浅层没有泄漏。**
2. **Semantic Independence > String Independence。Benchmark 独立性要覆盖语义、项目、血缘和派生关系。**
3. **HumanExposure 也是 Benchmark Exposure，开发者同样会对测试集过拟合。**
4. **RAG 评测需要 RetrievalFirewall，否则系统可能直接检索到 Gold 答案。**
5. **Unlimited Benchmark Queries 会把 Hidden Test 逐渐变成 Validation。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |
| `Governance` | 治理：控制版本、权限、污染、审批和发布决策 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
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

第 1 阶段我们已经建立 Benchmark Firewall 的概念。

现在把它升级成完整治理系统。

因为 Benchmark 最大的敌人之一就是：

# Contamination
## 测试污染

如果模型、数据管道、开发人员、RAG 或 Synthetic Pipeline 已经提前接触 Benchmark 信息，

最终高分可能只是：

> “见过答案”。

所以本阶段第一条边界：

\[
\boxed{
NoExactDuplicate
\neq
NoContamination
}
\]

本阶段最终形成：

# `ProcurementBenchmarkFirewallPolicy_V0.1`

---

# 一、污染到底有哪些类型？

至少可以分：

```text
Training Contamination
训练污染

Validation Contamination
验证污染

Developer Contamination
开发者污染

Synthetic Contamination
合成派生污染

Retrieval Contamination
检索污染

Prompt Leakage
提示泄漏

Judge Leakage
裁判泄漏
```

所以：

\[
\boxed{
Contamination
=
InformationExposureProblem
}
\]

不只是文本重复问题。

---

# 二、Training Contamination

最直接：

```text
Benchmark样本
进入CPT / SFT / LoRA训练
```

包括：

```text
原文
答案
解释
改写
切块
摘要
```

所以：

\[
\boxed{
ExactText
只是最容易发现的一层
}
\]

---

# 三、Near Duplicate：同一文档不同版本怎么办？

例如：

```text
原公告
更正公告
最终公告
```

文本不完全相同，

但内容高度重合。

如果一个进 Training，

另一个进 Gold，

模型仍可能：

> 基本见过。

所以要检查：

# Document Lineage
## 文档血缘

---

# 四、核心心智模型 ①
# `Semantic Independence` 比 `String Independence` 更重要

Benchmark 独立性不应该只定义为：

> 字符串不一样。

而应该尽量追求：

> 语义、项目、文档血缘、派生关系也独立。

所以：

\[
\boxed{
BenchmarkIndependence
>
TextDedup
}
\]

这里的 `>` 表示治理范围更大。

---

# 五、Synthetic Contamination

如果 Teacher 看到 Gold 样本：

```text
Sample X
```

然后生成：

```text
改写X
反事实X
同结构X
```

这些再进入 Training，

Benchmark 已经间接泄漏。

所以：

\[
\boxed{
DerivativeLeakage
也是Leakage
}
\]

必须记录：

```text
seed_id
teacher_model
prompt_version
derivative_lineage
```

---

# 六、Developer Contamination

即使样本没进训练，

开发者如果长期：

```text
逐条看Gold错误
针对Gold修Prompt
针对Gold写规则
针对Gold补案例
```

Gold 也会逐渐变成：

> Validation。

所以：

\[
\boxed{
HumanExposure
也是BenchmarkExposure
}
\]

---

# 七、核心心智模型 ②
# `Evaluation Leakage` 可以发生在 Weight 之外

Benchmark 独立性不仅保护：

> 模型参数。

还要保护：

```text
Prompt
Rules
Threshold
RAG Config
Agent Policy
Human Decisions
```

---

# 八、Retrieval Contamination：RAG 特别容易忽略的一类污染

如果评测时 RAG 可以检索：

> 包含 Gold Answer 或 Benchmark 标注文件的索引，

那么系统可能直接：

> 检索到答案。

所以评测 RAG 时必须检查：

```text
retrieval_corpus_version
index_version
benchmark_exclusion
```

因此：

\[
\boxed{
RAGEval
需要
RetrievalFirewall
}
\]

---

# 九、Prompt Leakage

如果 System Prompt 里：

```text
列出了Benchmark标签定义
甚至包含具体Gold答案模式
```

也可能造成泄漏。

尤其当：

> Prompt 是根据 Benchmark 错误逐条优化的。

所以 Prompt 也属于：

# Exposure Surface
## 信息暴露面

---

# 十、Hidden Test 为什么越来越重要？

开发团队看不到：

```text
具体题目
具体标签
```

就能显著降低：

> Human Overfitting。

所以重要 Release 可以使用：

# Hidden Benchmark
## 隐藏基准

并限制：

```text
提交次数
结果粒度
错误访问
```

---

# 十一、核心心智模型 ③
# `Unlimited Benchmark Queries` 会把 Hidden Test 也变成 Validation

即使看不到题目，

如果每天提交 1000 次，

只看分数变化，

也可以逐渐：

> 反向调参。

所以：

\[
\boxed{
QueryBudget
也是Governance
}
\]

---

# 十二、Firewall 应该在什么时候执行？

至少：

```text
数据入库时
训练集构建时
Synthetic生成时
Benchmark发布时
模型Release前
```

所以：

\[
\boxed{
Firewall
不是一次检查
而是LifecycleControl
}
\]

---

# 十三、污染检查层级

可以设计：

### Level 1
Exact Hash

### Level 2
Near Duplicate

### Level 3
Semantic Similarity

### Level 4
Project / Document Lineage

### Level 5
Synthetic Derivative

### Level 6
Human / Prompt Exposure

这比只做：

```text
hash != hash
```

完整得多。

---

# 十四、核心心智模型 ④
# `Leakage Detection` 永远不是 100% 完美

语义污染很难完全检测。

所以真正策略应该是：

\[
\boxed{
Detection
+
Prevention
+
AccessControl
+
Audit
}
\]

而不是：

> “我们有一个相似度脚本，所以没污染。”

---

# 十五、Canary / Sentinel 样本

可以加入一些专门用于监控泄漏的：

# Canary Items
## 哨兵样本

如果系统在这些极少公开、严格隐藏的样本上：

> 表现异常好，

可以触发污染调查。

它不是绝对证据，

而是：

# Contamination Signal
## 污染信号

---

# 十六、Test Governance：谁可以看什么？

可以设计权限：

```text
Benchmark Owner
看全量

Evaluator
运行评测

Developer
只看聚合结果

Release Owner
看Release报告

Annotator
只看分配样本
```

核心：

\[
\boxed{
NeedToKnowAccess
}
\]

---

# 十七、核心心智模型 ⑤
# `AccessControl` 是 Benchmark 质量的一部分

如果任何人都能：

> 下载 Gold 全量答案，

那么 Benchmark 独立性长期一定下降。

所以治理不是行政附加项。

它直接影响：

> Metric Credibility。

---

# 十八、污染事件发生后怎么办？

需要：

# Contamination Incident Response
## 污染事件响应

流程：

```text
Detect
发现

↓
Scope
确定影响范围

↓
Taint
标记污染样本 / Run

↓
Invalidate
必要时作废分数

↓
Replace / Rebuild
替换或重建Benchmark

↓
Version
发布新版本

↓
Audit
记录事件
```

---

# 十九、核心心智模型 ⑥
# `Tainted Score` 不能继续当历史基线

如果某次 Run 被确认：

> 使用了被污染 Benchmark，

它的分数应该：

```text
tainted = true
```

必要时：

> 不再参与模型版本比较。

---

# 二十、Benchmark Rotation

长期使用同一套 Benchmark，

开发团队不可避免会：

> 熟悉它。

所以可以保留：

```text
Core Frozen Set
核心稳定集

+
Rotating Hidden Set
轮换隐藏集
```

既保持历史可比，

又降低长期过拟合。

---

# 二十一、核心心智模型 ⑦
# `StableBenchmark` 和 `FreshBenchmark` 都需要

只稳定：

> 容易长期过拟合。

只更新：

> 历史不可比。

所以：

\[
\boxed{
BenchmarkPortfolio
=
StableCore
+
FreshHidden
}
\]

---

# 二十二、本阶段正式工程产物
# `ProcurementBenchmarkFirewallPolicy_V0.1`

至少锁定：

```text
firewall_policy_version

training_contamination_check

exact_hash_check

near_duplicate_check

semantic_similarity_check

project_lineage_check

document_lineage_check

synthetic_derivative_check

retrieval_firewall

prompt_exposure_policy

developer_access_policy

hidden_test_policy

query_budget

canary_policy

tainted_run_policy

incident_response

benchmark_rotation_policy

audit_log

release_gate
```

---

# 二十三、本阶段最重要的 9 个核心心智模型

> **心智模型 ①：`NoExactDuplicate ≠ NoContamination`。没有完全重复只能说明最浅层没有泄漏。**

> **心智模型 ②：`Semantic Independence > String Independence`。Benchmark 独立性要覆盖语义、项目、血缘和派生关系。**

> **心智模型 ③：`HumanExposure` 也是 Benchmark Exposure，开发者同样会对测试集过拟合。**

> **心智模型 ④：RAG 评测需要 `RetrievalFirewall`，否则系统可能直接检索到 Gold 答案。**

> **心智模型 ⑤：`Unlimited Benchmark Queries` 会把 Hidden Test 逐渐变成 Validation。**

> **心智模型 ⑥：`Detection + Prevention + AccessControl + Audit` 才是完整 Firewall。**

> **心智模型 ⑦：`AccessControl` 是评测质量的一部分，不是行政附加项。**

> **心智模型 ⑧：`TaintedScore` 不应继续作为可信历史基线。**

> **心智模型 ⑨：`StableCore + FreshHidden` 能同时兼顾历史可比与抗长期过拟合。**

---

# 二十四、下一阶段：第九课 · 第 11 阶段
# Benchmark Versioning、Regression Test 与模型版本比较

最关键的边界：

\[
\boxed{
HigherOverallScore
\neq
NoRegression
}
\]

并建立：

# `ProcurementRegressionPolicy_V0.1`

---

<!-- LESSON 09 STAGE 10 END -->


<!-- LESSON 09 STAGE 11 START -->

# 第九课 · 第 11 阶段
# Benchmark Versioning、Regression Test 与模型版本比较
## 模型总分涨了，为什么仍然可能不该发布？怎样证明新版本不仅更强，而且没有把旧版本已经会的东西弄坏？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **HigherOverallScore ≠ NoRegression。总分上涨仍可能伴随关键能力退化。**
2. **BenchmarkVersion 决定 Score Meaning，跨 Benchmark 版本不能裸比。**
3. **PairedEvaluation 比单纯比较两个总分更能定位真实变化。**
4. **RegressionAnalysis = StructuredDeltaAnalysis。要按能力、Slice、错误类型和严重度看变化。**
5. **StatisticalSignificance ≠ BusinessSignificance。统计显著不等于值得发布。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Regression` | 回归测试：更新后验证旧能力和关键切片没有退化 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |
| `Citation` | 引用：把生成结论和具体来源建立可追踪链接 |
| `Confidence Interval` | 置信区间：表示有限样本指标的不确定范围 |
| `Recall` | 召回率：真实风险中被系统成功找出的比例 |

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

这一阶段解决真正的版本升级问题。

假设：

```text
ProcurementLM_V0.1
Overall = 82

ProcurementLM_V0.2
Overall = 85
```

是不是 V0.2 一定更好？

不一定。

因为：

```text
平均 +3
```

可能同时伴随：

```text
关键高风险Slice -12
Citation -8
Abstention -10
```

所以第一条边界：

\[
\boxed{
HigherOverallScore
\neq
NoRegression
}
\]

本阶段最终形成：

# `ProcurementRegressionPolicy_V0.1`

---

# 一、Regression Test 到底是什么？

# Regression Test
## 回归测试

回答：

> 新版本有没有把旧版本已经做好的能力弄坏？

所以：

\[
\boxed{
Upgrade
=
Gain
+
NoUnacceptableRegression
}
\]

和第八课 CPT 的思想完全一致。

---

# 二、核心心智模型 ①
# `NewBest` 必须同时证明 `NotWorseWhereItMatters`

只看新增能力：

> 容易产生“升级幻觉”。

所以新模型至少需要：

```text
Gain Report
收益报告

Regression Report
回归报告
```

---

# 三、Benchmark Versioning：Benchmark 自己也有版本

例如：

```text
ProcurementBench_V1.0
ProcurementBench_V1.0.1
ProcurementBench_V1.1
```

版本变化可能包括：

```text
修Gold标签
新增Slice
新增任务
修改Rubric
替换污染样本
```

所以：

\[
\boxed{
BenchmarkVersion
决定
ScoreMeaning
}
\]

---

# 四、核心心智模型 ②
# 不同 Benchmark Version 的总分不能直接裸比较

如果 V1.1：

> 增加了更多 Hard Case，

分数可能下降。

这不一定说明模型变差。

所以：

\[
\boxed{
ScoreComparison
需要
SameBenchmarkVersion
}
\]

跨版本要做：

> Bridge Evaluation。

---

# 五、Bridge Set：怎样连接两个 Benchmark 版本？

可以保留：

# Bridge Set
## 桥接集

即：

> 两个版本都存在的一组稳定样本。

这样可以判断：

```text
分数变化来自模型
还是Benchmark变化
```

---

# 六、Paired Comparison：为什么同一批 Item 上比较更强？

如果模型 A 和 B 都在同一组样本上跑，

可以做：

# Paired Evaluation
## 配对评测

看每个 Item：

```text
A对B错
A错B对
都对
都错
```

这比只比较：

```text
82 vs 85
```

信息丰富得多。

---

# 七、核心心智模型 ③
# `Delta` 比绝对分更适合版本回归

可以定义：

\[
\Delta_i
=
Score_{new,i}
-
Score_{old,i}
\]

按：

```text
总体
Task
Slice
Error Type
Severity
```

分别看 Delta。

所以：

\[
\boxed{
RegressionAnalysis
=
StructuredDeltaAnalysis
}
\]

---

# 八、Confidence Interval：+1 分真的有意义吗？

如果 Benchmark 有采样误差，

```text
82.1
vs
82.8
```

可能不稳定。

可以用：

# Bootstrap
## 自助法

对 Item 重采样，

估计：

```text
Delta Confidence Interval
```

这样知道：

> +0.7 是稳定信号，还是采样波动。

---

# 九、Statistical Significance 和 Practical Significance 不一样

即使统计上显著：

> +0.2%

也可能业务价值很小。

反过来：

> 某个关键高风险 Slice +5%

即使样本少、区间宽，

也可能业务非常重要。

所以：

\[
\boxed{
StatisticalSignificance
\neq
BusinessSignificance
}
\]

---

# 十、核心心智模型 ④
# `Significant` 不等于 `WorthShipping`

Release 决策必须结合：

```text
效果幅度
关键Slice
业务风险
成本
延迟
```

---

# 十一、Regression Budget：允许退多少？

应该预先定义：

# Regression Budget
## 回归预算

例如：

```text
General Task
允许轻微波动

Critical Risk Recall
不得下降超过阈值

Citation Correctness
不得下降超过阈值

Safety
不得出现Critical Regression
```

所以：

\[
\boxed{
NoRegression
不等于
EveryMetricMustIncrease
}
\]

而是：

> 关键能力不能超过允许退化范围。

---

# 十二、Champion / Challenger

生产评测常用：

# Champion
## 当前稳定版本

# Challenger
## 候选新版本

两者在：

> 同一 Benchmark、同一 Protocol

下比较。

只有 Challenger 通过：

```text
Gain Gate
Regression Gate
Cost Gate
Safety Gate
```

才替换 Champion。

---

# 十三、核心心智模型 ⑤
# `Challenger` 必须击败的是“发布标准”，不是只击败某一个总分

一个版本：

> 总分 +2

但成本翻倍，

或者关键风险 Slice 回归，

都可能：

> 不升级。

---

# 十四、Regression Matrix

可以做：

| 能力 | Old | New | Delta | Gate |
|---|---:|---:|---:|---|
| Risk Recall | 0.86 | 0.89 | +0.03 | Pass |
| Citation | 0.92 | 0.88 | -0.04 | Fail |
| Abstention | 0.81 | 0.84 | +0.03 | Pass |
| Agent Completion | 0.76 | 0.82 | +0.06 | Pass |

这比单一：

```text
Overall +2.1
```

有用得多。

---

# 十五、Change Attribution：为什么分数变了？

版本之间可能同时改：

```text
Model
Prompt
RAG
Threshold
Rules
Agent Policy
```

如果一起改，

很难知道：

> 到底谁带来收益或回归。

所以重要升级要尽量：

# Controlled Change
## 受控变更

或者做：

# Ablation
## 消融实验

---

# 十六、核心心智模型 ⑥
# `ManyChangesAtOnce = WeakAttribution`

如果一次 Release 同时改十件事，

即使结果变好，

你也不知道：

> 哪个修改真正有效。

所以：

\[
\boxed{
VersionComparison
需要
ChangeTrace
}
\]

---

# 十七、Regression Failure 应该触发什么？

不是所有回归都：

> 自动否决。

可以根据严重度：

```text
Accept
接受

Investigate
调查

Mitigate
修复

Block Release
阻止发布
```

但规则应该：

> 训练前 / 发布前预定义。

---

# 十八、Historical Baseline：只和上一个版本比够吗？

不一定。

新版本可能：

```text
V0.3 比 V0.2 好
```

但：

```text
V0.2 本身已经比 V0.1 某项退化
```

所以长期要保留：

# Historical Trend
## 历史趋势

避免：

> 慢性能力侵蚀。

---

# 十九、核心心智模型 ⑦
# `SmallRepeatedRegression` 会积累成长期退化

每个版本都：

```text
-1%
```

看似可接受。

五个版本后：

> 已经 -5%。

所以：

\[
\boxed{
Regression
需要
TrendMonitoring
}
\]

---

# 二十、Release Diff Report

每次 Release 应生成：

```text
What Changed
改了什么

Where Improved
哪里提升

Where Regressed
哪里退化

Critical Slice Impact
关键切片

Statistical Uncertainty
统计不确定性

Cost / Latency
成本延迟

Final Decision
发布结论
```

这叫：

# Release Diff
## 发布差异报告

---

# 二十一、本阶段正式工程产物
# `ProcurementRegressionPolicy_V0.1`

至少锁定：

```text
regression_policy_version

benchmark_version

champion_version

challenger_version

paired_eval_required

delta_metrics

bootstrap_policy

confidence_interval

practical_significance

regression_budget

critical_metric_gates

critical_slice_gates

historical_baseline

trend_monitoring

change_trace

ablation_required

release_diff_report

release_decision
```

---

# 二十二、本阶段最重要的 9 个核心心智模型

> **心智模型 ①：`HigherOverallScore ≠ NoRegression`。总分上涨仍可能伴随关键能力退化。**

> **心智模型 ②：`BenchmarkVersion` 决定 Score Meaning，跨 Benchmark 版本不能裸比。**

> **心智模型 ③：`PairedEvaluation` 比单纯比较两个总分更能定位真实变化。**

> **心智模型 ④：`RegressionAnalysis = StructuredDeltaAnalysis`。要按能力、Slice、错误类型和严重度看变化。**

> **心智模型 ⑤：`StatisticalSignificance ≠ BusinessSignificance`。统计显著不等于值得发布。**

> **心智模型 ⑥：`NoRegression` 不代表每个指标都必须上涨，而是关键指标必须在预算内。**

> **心智模型 ⑦：`Challenger` 必须通过发布标准，不是只赢一个总分。**

> **心智模型 ⑧：`ManyChangesAtOnce = WeakAttribution`。一次改太多，版本收益无法归因。**

> **心智模型 ⑨：`SmallRepeatedRegression` 会累积，必须监控长期趋势。**

---

# 二十三、下一阶段：第九课 · 第 12 阶段
# 真正搭建 `ProcurementBench_V1`：端到端评测与 Release Gate

最关键的总边界：

\[
\boxed{
BenchmarkRun
\neq
ReleaseDecision
}
\]

并最终交付：

# `ProcurementBench_V1`

---

<!-- LESSON 09 STAGE 11 END -->


<!-- LESSON 09 STAGE 12 START -->

# 第九课 · 第 12 阶段
# 真正搭建 `ProcurementBench_V1`：端到端评测与 Release Gate
## 怎样把 Gold、Metrics、RAG、Agent、Slice、Calibration、Firewall、Regression 全部接成一套真正能决定“能不能上线”的质量系统？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Benchmark ≠ DatasetOnly。评测基准是数据、协议、指标和治理的组合。**
2. **ExpertOpinion ≠ GroundTruth。Gold 的权威来自受控流程，不来自单一专家身份。**
3. **CorrectAnswer ≠ CompleteEvaluation。结果、过程、证据和错误严重度都需要评。**
4. **Accuracy ≠ RiskQuality。分类指标必须和真实业务错误成本绑定。**
5. **FluentAnswer ≠ CorrectAnswer。生成质量必须拆事实、证据、引用和拒答。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Regression` | 回归测试：更新后验证旧能力和关键切片没有退化 |
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `Calibration` | 校准：使模型置信度更接近实际正确率 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |

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

前 11 个阶段，我们已经分别建立：

```text
Benchmark Boundary
Gold Set
Evaluation Schema
Classification Metrics
Generation Evaluation
RAG Evaluation
Agent Evaluation
Slice Evaluation
Calibration / Abstention / OOD
Benchmark Firewall
Regression Testing
```

第 12 阶段不再增加孤立概念。

它要把所有东西接成：

# `ProcurementBench_V1`

也就是：

> **政府采购 AI 的长期质量裁判系统。**

本阶段第一条总边界：

\[
\boxed{
BenchmarkRun
\neq
ReleaseDecision
}
\]

跑完一遍 Benchmark，

只代表：

> 得到一组评测证据。

真正是否发布，

还需要：

> Release Gate。

---

# 一、`ProcurementBench_V1` 到底是什么？

它不是：

```text
一个CSV
一个Excel
一个F1脚本
```

而是：

\[
\boxed{
ProcurementBench\_V1
=
GoldData
+
EvaluationSchema
+
Metrics
+
Slices
+
Calibration
+
Firewall
+
Regression
+
Governance
+
ReleaseGate
}
\]

所以：

\[
\boxed{
BenchmarkSystem
\neq
BenchmarkFile
}
\]

---

# 二、核心心智模型 ①
# `Benchmark` 是质量基础设施，不是一次考试

真正成熟以后，

每个模型、RAG、Agent 版本都应该经过：

```text
统一Benchmark
统一Protocol
统一Trace
统一Regression
统一ReleaseGate
```

所以 ProcurementBench 是：

# Quality Infrastructure
## 质量基础设施

---

# 三、完整端到端流程

```text
Define Evaluation Objectives
↓
Build Candidate Pool
↓
Benchmark Firewall
↓
Gold Annotation
↓
Adjudication
↓
Freeze Gold
↓
Evaluation Schema
↓
Task-specific Metrics
↓
Slice Registry
↓
Hidden / OOD Sets
↓
Run Model / RAG / Agent Eval
↓
Calibration & Risk-Coverage
↓
Regression Comparison
↓
Release Gate
↓
Release Report
↓
Versioned Benchmark Maintenance
```

这条链必须：

> 可复现、可审计、可版本化。

---

# 四、Benchmark Artifact Tree

第一版可以组织为：

```text
ProcurementBench_V1/

├── gold/
│   ├── items
│   ├── labels
│   ├── evidence
│   └── adjudication
│
├── schema/
│   ├── annotation_schema
│   ├── evaluation_schema
│   └── error_taxonomy
│
├── metrics/
│   ├── classification
│   ├── generation
│   ├── rag
│   ├── agent
│   └── calibration
│
├── slices/
│   ├── registry
│   ├── critical_slices
│   └── hard_cases
│
├── firewall/
│   ├── contamination_checks
│   ├── hidden_test
│   └── access_policy
│
├── regression/
│   ├── champion
│   ├── challenger
│   └── history
│
├── runs/
│   └── benchmark_run_manifest
│
└── release/
    ├── release_gate
    └── release_report
```

---

# 五、核心心智模型 ②
# `BenchmarkVersion = Data + Protocol + Schema + Metrics`

如果只改：

```text
Gold Data
```

是版本变化。

如果只改：

```text
Judge Prompt
Metric Definition
Slice Definition
```

同样是版本变化。

所以：

\[
\boxed{
BenchmarkVersion
\neq
DatasetVersionOnly
}
\]

---

# 六、Benchmark Run Manifest

每次 Run 至少记录：

```text
benchmark_run_id

benchmark_version

model_version

rag_version

agent_version

prompt_version

threshold_version

judge_version

metric_version

slice_registry_version

retrieval_index_version

timestamp

environment

results

release_gate_status
```

这样以后看到：

```text
Score = 84.7
```

才能知道：

> 它到底是怎么跑出来的。

---

# 七、核心心智模型 ③
# `ScoreWithoutRunManifest = WeakEvidence`

没有上下文的分数，

不能成为可靠发布证据。

---

# 八、统一 Scorecard 应该长什么样？

可以分：

### Foundation
```text
Domain Understanding
Long Context
Terminology
```

### Classification
```text
Precision
Recall
F1
PR-AUC
Critical FN
```

### Generation
```text
Factuality
Groundedness
Citation
Completeness
```

### RAG
```text
Recall@K
MRR
Context Recall
Groundedness
```

### Agent
```text
Task Completion
Tool Correctness
Recovery
Safety
```

### Reliability
```text
Calibration
Abstention
OOD
Risk-Coverage
```

### Regression
```text
Critical Delta
Worst Slice
Historical Trend
```

---

# 九、核心心智模型 ④
# `OneScore` 只能做导航，不能代替多维证据

可以有一个：

```text
Overall Score
```

用于快速导航。

但真正 Release 决策必须看：

```text
Dimension
Slice
Critical Gate
Regression
```

所以：

\[
\boxed{
OverallScore
=
Dashboard
\neq
Decision
}
\]

---

# 十、Release Gate 怎样设计？

可以概念化：

\[
ReleaseGate
=
G_{gold}
\land
G_{classification}
\land
G_{generation}
\land
G_{rag}
\land
G_{agent}
\land
G_{slice}
\land
G_{calibration}
\land
G_{regression}
\land
G_{firewall}
\]

全部为 True：

\[
\boxed{
ReleaseGate=True
}
\]

才允许：

> 发布候选系统晋级。

---

# 十一、关键门槛必须训练前定义

不能模型跑完后：

> 看哪个指标好就说哪个重要。

所以：

\[
\boxed{
PredefinedGate
>
PostHocNarrative
}
\]

这里的 `>` 表示：

> 决策可信度更高。

---

# 十二、核心心智模型 ⑤
# `Benchmark` 的价值在“阻止错误发布”，不只是证明模型很强

一个好 Benchmark 不只是：

> 给好模型发奖状。

更重要的是：

> 在高风险回归时把 Release 挡住。

所以：

\[
\boxed{
Benchmark
=
PromotionEvidence
+
ReleaseBrake
}
\]

---

# 十三、Champion / Challenger 工作流

```text
Champion
当前稳定系统

↓

Challenger
候选新系统

↓

Same Benchmark
同一基准

↓

Paired Eval
配对评测

↓

Regression Check
回归检查

↓

Release Gate
发布门槛

↓

Promote / Reject
晋级或否决
```

这会成为后面 MLOps 的核心流程。

---

# 十四、Benchmark 自身也需要 Quality Gate

谁来评 Benchmark？

至少要检查：

```text
Gold Agreement
Gold Evidence Completeness
Slice Coverage
Critical Slice Support
Contamination Status
Protocol Completeness
Metric Reproducibility
Access Governance
```

所以：

\[
\boxed{
BenchmarkQuality
也需要BenchmarkGovernance
}
\]

---

# 十五、核心心智模型 ⑥
# `BadBenchmark` 会让好模型看起来坏，也会让坏模型看起来好

所以：

\[
\boxed{
EvaluationError
也是
SystemRisk
}
\]

评测本身不能被当作绝对无误。

---

# 十六、人工评测和自动评测怎样组合？

自动：

```text
快
便宜
可重复
```

人工：

```text
贵
慢
但能处理复杂语义
```

所以推荐：

# Hybrid Evaluation
## 混合评测

例如：

```text
Programmatic Metrics
↓
LLM Judge
↓
Human Audit
↓
Expert Adjudication for Critical Cases
```

不同风险层级：

> 不同评测成本。

---

# 十七、核心心智模型 ⑦
# `EvaluationCost` 也要按风险分配

不要所有样本都人工，

也不要所有样本都自动。

可以：

```text
Low Risk
自动评

Medium Risk
LLM Judge + 抽检

High Risk
专家复核
```

所以：

\[
\boxed{
EvaluationBudget
=
RiskWeightedAllocation
}
\]

---

# 十八、Benchmark 运行以后输出什么？

至少输出：

```text
Executive Summary
总体摘要

Dimension Scorecard
能力维度

Critical Slice Report
关键切片

Regression Matrix
回归矩阵

Calibration / Coverage
校准与覆盖

Contamination Status
污染状态

Critical Failures
严重失败

Release Decision
发布结论
```

这才是完整：

# Evaluation Bundle
## 评测证据包

---

# 十九、Release Report 必须能回答哪些问题？

至少：

```text
新版本为什么更好？

哪里没有变？

哪里变差？

关键场景是否安全？

哪些问题仍然未知？

Benchmark是否干净？

是否有统计不确定性？

成本是否变化？

最终为什么Pass / Fail？
```

---

# 二十、核心心智模型 ⑧
# `Unknown` 必须被写进评测报告

Benchmark 永远不可能覆盖：

> 所有未来场景。

所以专业报告要明确：

```text
Known Strengths
Known Weaknesses
Known Unknowns
Coverage Gaps
```

而不是：

> “通过 Benchmark = 全面安全。”

所以：

\[
\boxed{
BenchmarkPass
\neq
UniversalGuarantee
}
\]

---

# 二十一、`ProcurementBench_V1` 的版本规则

建议：

```text
V1.0.0
首个冻结版

V1.0.1
标签/实现修复，不改变大范围能力定义

V1.1.0
新增Slice / 任务 / 覆盖

V2.0.0
评测体系重大改变
```

具体版本规则可以根据团队调整。

关键是：

> 变化必须显式。

---

# 二十二、本课 12 个阶段的工程产物怎样接起来？

第 1 阶段：

```text
ProcurementBenchmarkBoundaryPolicy_V0.1
```

回答：

> Benchmark 和 Validation / Test 的边界是什么？

第 2 阶段：

```text
ProcurementGoldSetPolicy_V0.1
```

回答：

> Gold Label 怎么产生？

第 3 阶段：

```text
ProcurementEvaluationSchema_V0.1
```

回答：

> 到底评哪些维度？

第 4 阶段：

```text
ProcurementClassificationMetricPolicy_V0.1
```

回答：

> 分类任务怎样量化？

第 5 阶段：

```text
ProcurementGenerationEvalPolicy_V0.1
```

回答：

> 开放式生成怎样评？

第 6 阶段：

```text
ProcurementRAGEvalPolicy_V0.1
```

回答：

> RAG 错在哪一层？

第 7 阶段：

```text
ProcurementAgentEvalPolicy_V0.1
```

回答：

> Agent 是否真正、安全完成任务？

第 8 阶段：

```text
ProcurementSliceEvalPolicy_V0.1
```

回答：

> 哪些关键场景被平均分掩盖？

第 9 阶段：

```text
ProcurementCalibrationAbstentionPolicy_V0.1
```

回答：

> 模型什么时候应该回答、什么时候应该拒答？

第 10 阶段：

```text
ProcurementBenchmarkFirewallPolicy_V0.1
```

回答：

> 如何保护测试独立性？

第 11 阶段：

```text
ProcurementRegressionPolicy_V0.1
```

回答：

> 新版本哪里进步、哪里退化？

第 12 阶段：

```text
ProcurementBench_V1
```

回答：

> 怎样用统一证据决定是否发布？

---

# 二十三、第九课最终 12 条核心心智模型

> **心智模型 ①：`Benchmark ≠ DatasetOnly`。评测基准是数据、协议、指标和治理的组合。**

> **心智模型 ②：`ExpertOpinion ≠ GroundTruth`。Gold 的权威来自受控流程，不来自单一专家身份。**

> **心智模型 ③：`CorrectAnswer ≠ CompleteEvaluation`。结果、过程、证据和错误严重度都需要评。**

> **心智模型 ④：`Accuracy ≠ RiskQuality`。分类指标必须和真实业务错误成本绑定。**

> **心智模型 ⑤：`FluentAnswer ≠ CorrectAnswer`。生成质量必须拆事实、证据、引用和拒答。**

> **心智模型 ⑥：`RAGFailure ≠ LLMFailure`。RAG 必须分层归因到 Retrieval、Ranking、Context、Generation。**

> **心智模型 ⑦：`ToolCallSuccess ≠ TaskCompletion`。Agent 要同时评结果、轨迹、安全和恢复。**

> **心智模型 ⑧：`OverallScore ≠ SliceReliability`。关键场景不能被平均分掩盖。**

> **心智模型 ⑨：`ConfidenceScore ≠ ProbabilityOfBeingCorrect`。可靠系统必须评校准、拒答和 Risk-Coverage。**

> **心智模型 ⑩：`NoExactDuplicate ≠ NoContamination`。测试独立性需要完整 Firewall 和访问治理。**

> **心智模型 ⑪：`HigherOverallScore ≠ NoRegression`。升级必须同时证明收益和关键能力不退化。**

> **心智模型 ⑫：`BenchmarkRun ≠ ReleaseDecision`。评测产生证据，Release Gate 才做最终发布决策。**

---

# 二十四、把整门第九课压成一张最终工程图

```text
                      Evaluation Objective
                         定义评测目标
                               │
                               ▼
                         Benchmark Boundary
                          锁定数据边界
                               │
                               ▼
                         Benchmark Firewall
                           防训练与开发泄漏
                               │
                               ▼
                            Gold Set
                    专家标注 + 证据 + 裁决
                               │
                               ▼
                       Evaluation Schema
                      结果 / 过程 / 证据 / 错误
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
         Classification     Generation      RAG / Agent
             分类              生成           系统链路
                │              │              │
                └──────────────┼──────────────┘
                               ▼
                        Slice Evaluation
                         关键场景切片
                               │
                               ▼
                 Calibration / Abstention / OOD
                    置信度与拒答可靠性
                               │
                               ▼
                       Regression Compare
                         新旧版本回归
                               │
                               ▼
                         Release Gate
                          发布门槛
                    ┌──────────┴──────────┐
                    ▼                     ▼
                  Reject                 Pass
                   否决                   通过
                                           │
                                           ▼
                               ProcurementBench_V1
```

脑中最后只留一句：

> **真正的 Benchmark，不是拿一批题跑一个总分，而是把高可信 Gold、任务化 Evaluation Schema、分类/生成/RAG/Agent 指标、关键 Slice、Calibration、Benchmark Firewall 和 Regression 全部接成一条证据链，最后用预先定义的 Release Gate 决定新系统是否真的值得上线。**

---

# 第九课 · 第 12 阶段掌握测试

现在不回看正文，你应该能够解释：ProcurementBench_V1 为什么不是一个数据文件；Benchmark Version 为什么同时包含数据、协议、Schema 和 Metric；为什么每次 Run 必须有 Manifest；为什么 Overall Score 只能做 Dashboard；Release Gate 应该包含哪些子门槛；为什么 Benchmark 的价值不仅是证明“更强”，还要阻止错误发布；Champion / Challenger 工作流怎样运行；为什么 Benchmark 自身也需要 Quality Gate；人工评测、LLM Judge、程序指标怎样分层组合；为什么评测预算也要按风险分配；Release Report 应该说明什么；为什么 Benchmark Pass 不等于 Universal Guarantee；以及为什么评测体系必须长期版本化维护。

如果这些能够完整讲出来：

\[
\boxed{
第九课第12阶段真正掌握
}
\]

---

# 第九课正式完成

到这里：

\[
\boxed{
第九课
=
12/12
}
\]

最终工程交付：

\[
\boxed{
ProcurementBench\_V1
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
\rightarrow
ProcurementBench\_V1
}
\]

下一课正式进入：

# 第十课：推理部署、性能优化与 MLOps
## 怎样把已经通过 Benchmark 的系统真正部署成低延迟、高吞吐、可监控、可灰度发布的 `ProcurementAI`？

第九课解决的是：

> **我们怎么知道系统真的更好。**

第十课开始解决：

> **怎样让这个已经被证明更好的系统，在真实生产环境里稳定、快速、可控地运行。**

---

<!-- LESSON 09 STAGE 12 END -->

