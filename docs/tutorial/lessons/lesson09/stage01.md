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
