# 第八课 · 第 6 阶段
# Catastrophic Forgetting：为什么模型学会领域知识以后，反而可能忘掉原来的能力？
## CPT 的真正难点不是“领域能力能不能涨”，而是“涨了以后有没有把模型其他能力一起弄坏”。

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **SharedParameters ⇒ CapabilityInterference。模型能力共享参数，学习新领域可能干扰旧能力。**
2. **DomainGain ≠ NetModelGain。领域能力上涨只是收益的一面，原有能力回归必须同时计入。**
3. **Overfitting ≠ Forgetting。前者是新任务泛化变差，后者是旧能力被新学习破坏。**
4. **BestDomainCheckpoint ≠ BestReleaseCheckpoint。领域分数最高的模型，不一定是综合能力最适合发布的模型。**
5. **WeightDistance ≠ CapabilityRegression。参数漂移只能做诊断，行为 Benchmark 才是最终证据。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `CPT` | CPT/继续预训练：在领域语料上继续执行预训练目标 |
| `Catastrophic Forgetting` | 灾难性遗忘：领域训练后通用能力明显退化 |
| `Regression` | 回归测试：更新后验证旧能力和关键切片没有退化 |
| `Checkpoint` | 检查点：保存模型和训练状态以便恢复/发布 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Retention` | 能力保持：领域增强时尽量保住原有通用能力 |

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

到第 5 阶段，我们已经能够设计：

\[
\boxed{
Corpus
+
Tokenizer
+
Sequence
+
Mixture
}
\]

也就是说，我们已经知道：

> 用什么数据、怎样切 Token、怎样组成训练序列、不同数据分别训练多少。

接下来必须面对 CPT 最危险的问题之一：

# Catastrophic Forgetting
## 灾难性遗忘

模型在政府采购语料上持续更新参数以后，可能发生：

```text
采购语言能力上升

但同时：

通用语言能力下降
数学能力下降
代码能力下降
一般知识下降
指令遵循下降
原有SFT行为变弱
```

所以本阶段最终形成：

# `ProcurementCPTForgettingPolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

CPT 成功不能只看：

> **Domain Score 有没有上涨。**

真正应该看：

\[
\boxed{
DomainGain
\neq
NetModelGain
}
\]

进一步：

\[
\boxed{
NetModelGain
=
DomainGain
-
CapabilityRegressionCost
}
\]

这里不是要求把所有能力真的压成一个简单数字。

而是建立工程判断：

> **领域能力上涨，只是收益的一面；被破坏的原有能力，是必须同时计入的成本。**

---

# 二、什么是 Catastrophic Forgetting？

可以把模型参数记成：

\[
\theta_0
\]

表示 CPT 之前的模型。

经过领域训练以后变成：

\[
\theta_1
\]

如果训练目标几乎只来自采购领域，

梯度会持续推动参数：

\[
\theta_0
\rightarrow
\theta_1
\]

去适应新的领域分布。

问题在于：

> 原来的参数同时承担着通用语言、知识、数学、代码、指令行为等很多能力。

当这些参数为了采购分布不断调整时，

原来的某些能力可能下降。

这就是：

\[
\boxed{
NewLearning
可能干扰
OldCapability
}
\]

---

# 三、核心心智模型 ①：模型参数是“共享资产”，不是一个能力一个独立文件夹

不要把模型想象成：

```text
采购能力
放在A文件夹

数学能力
放在B文件夹

代码能力
放在C文件夹
```

真实神经网络更接近：

> 大量能力共享同一套参数和表示空间。

所以：

\[
\boxed{
SharedParameters
\Rightarrow
CapabilityInterference
}
\]

学习采购领域时更新同一套参数，

就可能同时影响：

```text
语言表示
注意力模式
事实关联
推理习惯
输出分布
```

这就是为什么：

> “只是继续训练一些采购文本”

并不等于：

> “只增加采购知识，不碰其他能力”。

---

# 四、Forgettting 和 Overfitting 不是一回事

这两个非常容易混。

# Overfitting
## 过拟合

主要指：

> 对训练数据学得太死，泛化到同分布新样本时变差。

例如：

```text
训练集采购条款
表现很好

新的采购条款
表现明显下降
```

而：

# Catastrophic Forgetting
## 灾难性遗忘

主要指：

> 学习新领域以后，原本已有能力退化。

例如：

```text
采购能力
上涨

数学
下降

通用问答
下降

代码
下降
```

所以：

\[
\boxed{
Overfitting
\neq
Forgetting
}
\]

一个模型甚至可能：

> 采购领域没有过拟合，

但仍然发生明显遗忘。

---

# 五、核心心智模型 ②：Domain Improvement 和 General Retention 是两个独立坐标轴

不要只用一条：

```text
采购分数
```

评估 CPT。

至少要同时看：

```text
X轴：
Domain Gain
领域能力提升

Y轴：
General Retention
通用能力保留
```

于是可能出现四种情况：

| 领域能力 | 通用能力 | 解释 |
|---|---|---|
| ↑ | 稳定 | 理想 |
| ↑ | ↓ | 有收益但发生遗忘 |
| ≈ | 稳定 | CPT收益有限 |
| ↓ | ↓ | 明显失败 |

所以：

\[
\boxed{
CPTSuccess
=
DomainGain
+
GeneralRetention
}
\]

---

# 六、哪些能力最需要做回归监控？

第一版至少可以分成五层。

## 1. General Language
### 通用语言能力

检查：

```text
摘要
改写
阅读理解
常识问答
基本写作
```

---

## 2. Reasoning
### 推理能力

例如：

```text
基础数学
逻辑判断
多步推理
简单表格理解
```

---

## 3. Code / Structured Reasoning
### 代码与结构化推理

如果底座模型原本具备：

```text
代码生成
JSON
Schema遵循
简单程序理解
```

也应该监控。

---

## 4. Instruction Following
### 指令遵循

尤其重要，因为我们的最终系统不是纯 Base Model。

要检查：

```text
遵循任务要求
格式约束
拒答 / Abstention
结构化输出
```

---

## 5. Procurement Domain
### 政府采购领域能力

包括：

```text
领域语言建模
术语理解
长文档理解
规则表达
风险识别
专业生成
```

这样才形成：

\[
\boxed{
DomainEval
+
RegressionEval
}
\]

---

# 七、Forgetting Score：怎样把“忘了多少”变成可测指标？

假设某项能力 CPT 前得分：

\[
S_{before}
\]

CPT 后得分：

\[
S_{after}
\]

可以定义一个简单的绝对回归量：

\[
Regression
=
S_{before}
-
S_{after}
\]

如果：

\[
Regression > 0
\]

说明能力下降。

也可以用相对回归：

\[
RelativeRegression
=
\frac{S_{before}-S_{after}}
{S_{before}}
\]

用于比较不同指标。

注意：

> 不同 Benchmark 的量纲不同。

所以真正工程中通常应该：

```text
按能力单独设阈值
而不是把所有分数直接相加
```

---

# 八、核心心智模型 ③：Forgetting 必须看 Curve，而不是只看最终 Checkpoint

如果只比较：

```text
CPT前

和

CPT最终
```

你会丢掉很多信息。

更专业的是：

# Forgetting Curve
## 遗忘曲线

例如每隔：

```text
5B tokens
```

做一次：

```text
Domain Eval
+
General Regression Eval
```

于是可以得到：

```text
0B
领域 60
通用 80

5B
领域 67
通用 79

10B
领域 72
通用 77

20B
领域 74
通用 71
```

你可能发现：

> 10B Token 以后，领域收益越来越小，但通用能力继续快速下降。

这就是非常重要的：

# Marginal Tradeoff
## 边际收益—损失关系

---

# 九、核心心智模型 ④：最佳 CPT Checkpoint 不一定是训练最久的那个

假设：

```text
Checkpoint A
领域 +6
通用 -1

Checkpoint B
领域 +10
通用 -3

Checkpoint C
领域 +11
通用 -10
```

如果只看领域能力，

你会选：

> C。

但从整体系统来看，

C 可能明显更差。

所以：

\[
\boxed{
BestDomainCheckpoint
\neq
BestReleaseCheckpoint
}
\]

真正发布时应该看：

> 多目标约束下的最优点。

---

# 十、为什么 Learning Rate 会影响遗忘？

Learning Rate：

# 学习率

决定参数每一步更新幅度。

概念上：

\[
\theta_{t+1}
=
\theta_t
-
\eta
\nabla_\theta \mathcal{L}
\]

其中：

\[
\eta
=
LearningRate
\]

如果学习率过大，

参数可能快速偏离原始能力区域。

所以：

\[
\boxed{
HigherLearningRate
\Rightarrow
PotentiallyFasterParameterDrift
}
\]

但要注意：

> 不是“学习率越小越安全”。

太小可能：

> CPT 几乎学不到东西。

真正问题仍然是：

\[
\boxed{
DomainGain
vs
Retention
}
\]

---

# 十一、Training Duration：训练越久为什么也可能遗忘越严重？

如果模型持续在一个窄领域分布上训练：

```text
1B tokens
5B tokens
20B tokens
50B tokens
```

领域 Loss 可能持续下降，

但参数也会越来越适应：

> 采购分布。

如果通用数据完全不出现，

模型原来的分布会逐渐被弱化。

所以：

\[
\boxed{
MoreCPT
\neq
AlwaysBetterCPT
}
\]

训练长度必须由：

```text
领域收益
通用回归
边际收益
预算
```

共同决定。

---

# 十二、Parameter Drift：参数变化大就一定遗忘严重吗？

可以定义参数变化：

\[
\Delta\theta
=
\theta_{CPT}
-
\theta_{Base}
\]

也可以看某种范数：

\[
\|\Delta\theta\|
\]

但必须注意：

\[
\boxed{
ParameterDrift
\neq
CapabilityRegression
}
\]

参数变化大：

> 不一定意味着能力一定坏。

参数变化小：

> 也不保证所有能力都安全。

所以 Parameter Drift 更适合作为：

> 诊断信号。

真正 Release 判断仍然依赖：

> 行为和能力评测。

---

# 十三、核心心智模型 ⑤：Weight Distance 是代理指标，Behavior Regression 才是最终证据

工程上可以监控：

```text
Weight Norm Change
权重变化

Layer-wise Drift
分层参数漂移

Embedding Drift
Embedding变化

Gradient Norm
梯度范数
```

但这些都属于：

# Proxy Metrics
## 代理指标

最终真正重要的是：

```text
模型还会不会做原来会做的事情？
```

所以：

\[
\boxed{
WeightMetric
<
CapabilityBenchmark
}
\]

这里的 `<` 表达的是：

> 在最终判断中的证据优先级更低。

---

# 十四、Plasticity–Stability Dilemma：CPT 的本质是“可塑性”和“稳定性”之间找平衡

这是持续学习领域非常经典的核心矛盾。

# Plasticity
## 可塑性

表示：

> 模型能否学会新的领域分布。

# Stability
## 稳定性

表示：

> 模型能否保留原来的能力。

如果太追求 Stability：

> 模型几乎不变，领域能力学不上去。

如果太追求 Plasticity：

> 模型学得很快，但旧能力掉得厉害。

所以：

\[
\boxed{
ContinualLearning
=
Plasticity
\leftrightarrow
Stability
}
\]

这就是 CPT 真正的优化问题。

---

# 十五、核心心智模型 ⑥：CPT 不是单目标优化，而是受约束的多目标优化

我们真正希望：

\[
DomainScore
\uparrow
\]

同时：

\[
GeneralRegression
\leq
Threshold
\]

并且：

\[
TrainingCost
\leq
Budget
\]

所以更专业地说：

\[
\boxed{
Maximize
\quad
DomainGain
}
\]

subject to：

\[
\boxed{
GeneralRegression
\leq
AllowedThreshold
}
\]

以及：

\[
\boxed{
Cost
\leq
Budget
}
\]

这比单纯说：

> “CPT Loss 越低越好”

要专业得多。

---

# 十六、Forgetting 可能发生在哪些层？

不应该只看最终 Benchmark。

还可以分层诊断：

```text
Language Modeling Regression
通用语言建模退化

Knowledge Regression
一般知识退化

Reasoning Regression
推理退化

Instruction Regression
指令遵循退化

Format Regression
结构化输出退化

Safety / Abstention Regression
拒答和不确定性行为退化
```

尤其如果后续还要重新 SFT，

就要区分：

> 是 Base Capability 丢失了，

还是：

> Instruction Alignment 丢失了。

这两类问题恢复策略可能不同。

---

# 十七、CPT 后重新 SFT 能不能“把遗忘救回来”？

有时：

> 可以恢复一部分行为。

例如 CPT 后：

```text
JSON输出变差
聊天格式变弱
```

重新做 SFT 可能改善。

但不能因此假设：

\[
\boxed{
SFT
可以修复所有Forgetting
}
\]

如果 CPT 已经导致：

```text
通用知识表示退化
数学能力退化
底层语言建模能力下降
```

少量 SFT 不一定能完全恢复。

所以：

\[
\boxed{
PostCPTSFT
\neq
UniversalRepair
}
\]

---

# 十八、Checkpoint Strategy：为什么 CPT 必须高频保存检查点？

因为最佳点可能出现在：

> 训练中途。

所以不能只保存：

```text
final_model
```

建议至少根据 Token Progress：

```text
Checkpoint_5B
Checkpoint_10B
Checkpoint_15B
Checkpoint_20B
```

然后每个 Checkpoint 都跑：

```text
Domain Validation

General Regression

Downstream Probe
```

这样才能找到：

# Pareto-efficient Checkpoint
## 多目标折中较优检查点

而不是：

> 默认最后一个就是最好。

---

# 十九、Early Stop：CPT 什么时候应该提前停止？

可以设置：

```text
DomainGainImprovement
边际领域收益

GeneralRegression
通用能力下降

LossPlateau
Loss进入平台期

BudgetLimit
预算上限
```

例如：

```text
如果连续两个Checkpoint：

领域收益 < 最小增益阈值

同时

通用回归 > 允许阈值
```

就进入：

# Early Stop
## 提前停止

所以：

\[
\boxed{
StopCPT
不能只看TrainingLoss
}
\]

---

# 二十、政府采购案例：怎样判断一次 CPT 是成功还是失败？

假设 Base Model：

```text
采购领域评分
62

通用语言
82

数学
76

代码
70

指令遵循
84
```

CPT 后：

```text
采购领域
76
↑14

通用语言
81
↓1

数学
75
↓1

代码
69
↓1

指令遵循
83
↓1
```

这是：

> 很可能可接受的方向。

但如果：

```text
采购领域
78
↑16

通用语言
72
↓10

数学
61
↓15

代码
55
↓15

指令遵循
70
↓14
```

就不能简单宣布：

> “CPT 成功，因为采购分数提升 16。”

因为：

\[
\boxed{
DomainGain
没有自动抵消
GeneralRegression
}
\]

---

# 二十一、Regression Benchmark：必须在 CPT 前冻结

如果 CPT 前后使用不同测试集，

就无法判断：

> 真的是模型变化，还是测试集变化。

所以需要：

# Regression Benchmark
## 能力回归测试集

在 CPT 开始前冻结：

```text
benchmark_version

task_list

metric_definition

evaluation_prompt

decoding_config

scoring_rule
```

这样每个 Checkpoint 都用：

> 同一套评测协议。

所以：

\[
\boxed{
ForgettingMeasurement
需要
StableBenchmark
}
\]

---

# 二十二、核心心智模型 ⑦：No Regression 也不等于 CPT 成功

假设：

```text
采购能力
不变

通用能力
不变
```

这说明：

> 没明显遗忘。

但也可能意味着：

> CPT 根本没学到东西。

所以：

\[
\boxed{
Retention
\neq
Improvement
}
\]

真正目标必须同时满足：

```text
DomainGain成立

GeneralRegression受控
```

所以：

\[
\boxed{
CPTSuccess
=
LearnNew
+
KeepOld
}
\]

---

# 二十三、完整 Forgetting Evaluation 流程

英文流程：

```text
Freeze Baseline
↓
Define Capability Suite
↓
Run Pre-CPT Evaluation
↓
Start CPT
↓
Periodic Checkpoint
↓
Domain Evaluation
↓
General Regression Evaluation
↓
Compute Forgetting Curves
↓
Compare Tradeoffs
↓
Early Stop / Continue
↓
Select Release Checkpoint
```

中文解释：

```text
冻结CPT前基线模型
↓
定义要保护的能力集合
↓
跑一次CPT前完整评测
↓
开始继续预训练
↓
定期保存Checkpoint
↓
测领域能力有没有提升
↓
测通用能力有没有下降
↓
形成遗忘曲线
↓
比较领域收益和能力回归
↓
决定继续还是提前停止
↓
选择真正适合发布的Checkpoint
```

这一条流程必须进入工程规范。

---

# 二十四、本阶段正式工程产物：`ProcurementCPTForgettingPolicy_V0.1`

第一版至少锁定：

```text
forgetting_policy_version

baseline_model_id

baseline_checkpoint

domain_eval_suite

general_regression_suite

instruction_regression_suite

structured_output_regression

reasoning_regression

code_regression

pre_cpt_scores

checkpoint_interval_tokens

checkpoint_eval_required
=
true

absolute_regression

relative_regression

allowed_regression_thresholds

domain_gain_threshold

early_stop_policy

release_checkpoint_policy

parameter_drift_monitoring

layerwise_drift_monitoring

forgetting_curve

evaluation_config_version

trace_logging
=
enabled
```

每个 Checkpoint 至少记录：

```text
checkpoint_id

tokens_seen

training_loss

domain_metrics

general_metrics

instruction_metrics

regression_delta

relative_regression

parameter_drift

continue_stop_decision

decision_reason
```

这样以后才能回答：

> **模型到底是在什么时候开始“越训越窄”的？**

---

# 二十五、本阶段最重要的 8 个核心心智模型

> **心智模型 ①：`SharedParameters ⇒ CapabilityInterference`。模型能力共享参数，学习新领域可能干扰旧能力。**

> **心智模型 ②：`DomainGain ≠ NetModelGain`。领域能力上涨只是收益的一面，原有能力回归必须同时计入。**

> **心智模型 ③：`Overfitting ≠ Forgetting`。前者是新任务泛化变差，后者是旧能力被新学习破坏。**

> **心智模型 ④：`BestDomainCheckpoint ≠ BestReleaseCheckpoint`。领域分数最高的模型，不一定是综合能力最适合发布的模型。**

> **心智模型 ⑤：`WeightDistance ≠ CapabilityRegression`。参数漂移只能做诊断，行为 Benchmark 才是最终证据。**

> **心智模型 ⑥：`Plasticity ↔ Stability`。CPT 的核心矛盾是既要学得进去，又要保得住原能力。**

> **心智模型 ⑦：`CPTSuccess = LearnNew + KeepOld`。不遗忘但没学会新领域，不算成功；领域变强但旧能力崩掉，也不算成功。**

> **心智模型 ⑧：`StopCPT ≠ WaitForLowestLoss`。停止训练必须依据领域收益、能力回归、边际收益和预算共同决定。**

---

# 二十六、把完整 Catastrophic Forgetting 流程压成一张专业工程图

```text
                    Base / Pre-CPT Model
                         CPT前基线模型
                               │
                               ▼
                      Baseline Evaluation
                  领域 + 通用 + 指令能力基线
                               │
                               ▼
                             CPT
                        领域继续预训练
                               │
                               ▼
                      Periodic Checkpoints
                       定期保存检查点
                               │
                 ┌─────────────┼─────────────┐
                 ▼             ▼             ▼
           Domain Eval    General Eval   Drift Metrics
            领域评测        通用回归       参数漂移
                 │             │             │
                 └─────────────┼─────────────┘
                               ▼
                       Forgetting Curve
                         形成遗忘曲线
                               │
                               ▼
                     Tradeoff Evaluation
                 比较领域收益与能力回归
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
                 Continue    Early Stop   Reject
                   继续        提前停止     否决
                    │          │          │
                    └──────────┼──────────┘
                               ▼
                    Release Checkpoint
                    选择最终发布检查点
```

脑中最后只留一句：

> **Catastrophic Forgetting 的本质不是“模型突然把知识全忘了”，而是持续在窄领域分布上更新共享参数以后，模型对新领域越来越适应，却可能逐渐偏离原有能力；因此 CPT 必须同时优化“学会新的”和“保住旧的”。**

---

# 第八课 · 第 6 阶段掌握测试

现在不回看正文，你应该能够解释：为什么共享参数会导致 Capability Interference；Catastrophic Forgetting 与 Overfitting 有什么区别；为什么 Domain Gain 和 General Retention 必须分开评测；CPT 应该监控哪些通用能力；Absolute Regression 和 Relative Regression 分别表达什么；为什么要看 Forgetting Curve 而不能只看最终模型；为什么最佳领域 Checkpoint 不等于最佳发布 Checkpoint；Learning Rate 和 Training Duration 为什么会影响遗忘；Parameter Drift 能说明什么、不能说明什么；什么是 Plasticity–Stability Dilemma；为什么 CPT 本质上是受约束的多目标优化；为什么 SFT 不能被当作万能遗忘修复器；为什么需要频繁保存 Checkpoint；Early Stop 应该依据什么；为什么 Regression Benchmark 必须在训练前冻结；以及为什么 `CPTSuccess = LearnNew + KeepOld`。

如果这些能够完整讲出来：

\[
\boxed{
第八课第6阶段真正掌握
}
\]

---

# 下一阶段：第八课 · 第 7 阶段
# Replay、Regularization 与能力保持：怎样防止 CPT 越训越窄？
## 已经知道模型为什么会遗忘，下一步就是把“能力保持”真正做成训练机制，而不是只在训练后发现问题。

下一阶段会正式进入：

```text
Replay
通用语料回放

Replay Ratio
回放比例

Interleaving
领域与通用数据交错训练

Regularization
正则化

Weight Anchoring
参数锚定

KL Constraint
分布约束

Teacher Reference
参考模型

Layer Freezing
层冻结

Selective Training
选择性训练

Capability Retention
能力保持

Retention Budget
能力回归预算
```

并建立：

# `ProcurementCPTRetentionPolicy_V0.1`

下一阶段最关键的一条边界会是：

\[
\boxed{
DetectForgetting
\neq
PreventForgetting
}
\]

也就是说：

> **第 6 阶段解决“怎么知道模型忘了”，第 7 阶段才真正解决“训练时怎样让它尽量别忘”。**

---
