# 第八课 · 第 7 阶段
# Replay、Regularization 与能力保持：怎样防止 CPT 越训越窄？
## 已经知道模型为什么会遗忘，下一步就是把“能力保持”真正做成训练机制，而不是只在训练后发现问题。

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **DetectForgetting ≠ PreventForgetting。发现遗忘是诊断，能力保持是训练控制。**
2. **Retention ≠ FreezeEverything。能力保持不是不让模型变化，而是让变化发生在值得变化的地方。**
3. **Replay = OldDistributionReminder。回放的本质是让旧分布在训练过程中继续获得梯度支持。**
4. **Retention = Data Constraint + Objective Constraint + Parameter Constraint。能力保持可以从数据、目标函数和参数更新范围三个层面同时实现。**
5. **ReferenceModel ≠ GroundTruth。参考模型只是行为锚点，不是永远正确的老师。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Replay` | 回放：混入旧/通用数据以减少遗忘 |
| `CPT` | CPT/继续预训练：在领域语料上继续执行预训练目标 |
| `Retention` | 能力保持：领域增强时尽量保住原有通用能力 |
| `Regression` | 回归测试：更新后验证旧能力和关键切片没有退化 |
| `Batch` | 批次：一次参与计算的一组样本 |
| `Checkpoint` | 检查点：保存模型和训练状态以便恢复/发布 |

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

第 6 阶段我们解决的是：

\[
\boxed{
DetectForgetting
}
\]

也就是：

> 怎样知道模型什么时候开始遗忘、遗忘了什么、哪个 Checkpoint 已经不适合发布。

但这还不够。

真正成熟的 CPT 系统还必须进一步解决：

\[
\boxed{
PreventForgetting
}
\]

也就是：

> **训练过程中怎样主动限制能力退化，而不是等训练结束以后才发现模型已经被训窄了。**

所以本阶段正式进入：

# Capability Retention
## 能力保持

并最终形成：

# `ProcurementCPTRetentionPolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

发现遗忘和防止遗忘，是两件不同的事情。

\[
\boxed{
DetectForgetting
\neq
PreventForgetting
}
\]

第 6 阶段解决：

```text
模型忘了什么？
什么时候开始忘？
忘了多少？
```

第 7 阶段解决：

```text
训练时怎样降低遗忘？
怎样让新能力和旧能力共存？
怎样限制模型偏离原始分布？
```

所以：

\[
\boxed{
RetentionPolicy
=
TrainingTimeControl
}
\]

它不是训练后的补救。

而是：

> **训练过程中就要生效的约束机制。**

---

# 二、核心心智模型 ①：Retention 不是“别让模型变”，而是“让模型只在值得变的地方变”

一个常见误区是：

> 为了防止遗忘，就尽量少更新参数。

但如果模型几乎不更新：

> CPT 也学不到新领域。

所以真正目标不是：

\[
\boxed{
NoChange
}
\]

而是：

\[
\boxed{
UsefulChange
+
ControlledChange
}
\]

这意味着：

```text
需要领域能力增长
但避免无关能力大幅漂移
```

因此：

\[
\boxed{
Retention
\neq
FreezeEverything
}
\]

---

# 三、最直接的方法：Replay

# Replay
## 通用语料回放

Replay 的核心思想非常简单：

> 不要让模型在 CPT 期间只看采购领域。

而是继续给它一部分：

```text
高质量通用文本
数学
代码
百科知识
一般语言
通用指令风格
```

让原有能力持续得到梯度支持。

流程：

```text
Domain Batch
采购领域数据

+

Replay Batch
通用回放数据

↓

Mixed Training
混合训练

↓

Domain Gain
+
General Retention
```

所以：

\[
\boxed{
Replay
=
OldDistributionReminder
}
\]

可以把它理解成：

> 在模型学习新领域时，持续提醒它“旧世界仍然存在”。

---

# 四、Replay Ratio：回放比例到底怎么定？

假设训练总 Token Budget 是：

\[
B
\]

我们定义领域占比：

\[
p_d
\]

回放占比：

\[
p_r
\]

满足：

\[
p_d+p_r=1
\]

例如：

```text
Domain
80%

Replay
20%
```

但这个比例不能机械固定。

真正应该通过：

```text
Domain Gain
领域收益

General Regression
通用能力回归

Training Cost
训练成本
```

共同决定。

如果 Replay 太少：

> 遗忘可能明显。

如果 Replay 太多：

> 领域学习速度会变慢。

所以：

\[
\boxed{
ReplayRatio
=
PlasticityStabilityTradeoff
}
\]

---

# 五、核心心智模型 ②：Replay 不是“把旧数据重新训练一遍”，而是维持分布覆盖

Replay 不要求：

> 把原始预训练数据全部拿回来。

现实里也不可能。

更专业的目标是：

> 建立一个足够代表原有能力分布的 Replay Corpus。

例如：

```text
General Language
通用语言

Reasoning
推理

Math
数学

Code
代码

Instruction-like Text
指令风格文本
```

这些数据不需要巨大，

但要覆盖：

> 我们最不希望丢掉的能力。

所以：

\[
\boxed{
ReplayCorpus
\neq
OriginalPretrainingCorpus
}
\]

而更接近：

\[
\boxed{
RetentionRepresentativeCorpus
}
\]

即：

> 能力保持代表集。

---

# 六、Interleaving：领域数据和 Replay 怎样混？

# Interleaving
## 交错训练

一种常见做法：

```text
Domain Batch
↓
Replay Batch
↓
Domain Batch
↓
Domain Batch
↓
Replay Batch
```

另一种：

```text
同一个Batch中
混合Domain与Replay样本
```

核心目标都是：

> 避免长时间连续暴露在单一窄分布上。

所以：

\[
\boxed{
Interleaving
=
DistributionSmoothingOverTime
}
\]

中文可以理解为：

> 把训练时间轴上的数据分布“摊平”。

---

# 七、核心心智模型 ③：能力保持不只靠 Data，也可以靠 Objective Constraint

Replay 是：

> 数据层面的能力保持。

但还可以进一步做：

# Regularization
## 正则化约束

核心思想：

> 在优化领域 Loss 的同时，增加一个“不要偏离太远”的约束。

因此总 Loss 可以概念化为：

\[
\mathcal{L}_{total}
=
\mathcal{L}_{domain}
+
\lambda
\mathcal{L}_{retention}
\]

其中：

\[
\lambda
\]

表示：

> 保持约束的强度。

所以：

\[
\boxed{
Retention
可以来自
DataConstraint
+
ObjectiveConstraint
}
\]

---

# 八、Weight Anchoring：参数锚定

一种直觉化方法是：

> 不希望新模型的参数离原模型太远。

设 CPT 前参数：

\[
\theta_0
\]

训练中参数：

\[
\theta
\]

可以加入：

\[
\mathcal{L}_{anchor}
=
\|\theta-\theta_0\|^2
\]

总 Loss：

\[
\mathcal{L}_{total}
=
\mathcal{L}_{domain}
+
\lambda
\|\theta-\theta_0\|^2
\]

这叫：

# Weight Anchoring
## 参数锚定

直觉：

> 模型可以学，但别漂得太远。

但必须注意：

\[
\boxed{
ParameterCloseness
\neq
CapabilityCloseness
}
\]

所以 Weight Anchoring 只能作为：

> 辅助约束。

不能替代行为评测。

---

# 九、KL Constraint：约束输出分布不要偏离参考模型太远

除了约束参数，

还可以约束：

> 模型输出分布。

假设原模型：

\[
p_{ref}(x)
\]

CPT 模型：

\[
p_{\theta}(x)
\]

可以在 Replay / Anchor 数据上加入：

# KL Divergence
## KL 散度约束

概念上：

\[
\mathcal{L}_{KL}
=
D_{KL}
(
p_{ref}
\|
p_{\theta}
)
\]

总目标：

\[
\mathcal{L}_{total}
=
\mathcal{L}_{domain}
+
\beta\mathcal{L}_{KL}
\]

直觉上：

> 在一些我们希望保持稳定的输入上，新模型输出分布不要和旧模型差得太离谱。

---

# 十、核心心智模型 ④：Reference Model 是“行为锚点”，不是永远正确的老师

使用 KL Constraint 时通常需要：

# Reference Model
## 参考模型

它可以是：

```text
CPT前Base Model
或
CPT前Domain/SFT Model
```

但必须注意：

\[
\boxed{
ReferenceModel
\neq
GroundTruth
}
\]

它不是：

> 永远正确的 Teacher。

它只是：

> 我们希望保留某些行为的参考点。

如果 Reference Model 本身有问题，

过强约束反而会阻止新模型改进。

所以：

\[
\boxed{
Reference
是Anchor
不是Oracle
}
\]

---

# 十一、Layer Freezing：能不能直接冻结一部分层？

可以。

# Layer Freezing
## 层冻结

例如：

```text
冻结Embedding

冻结底部若干Transformer层

只训练顶部若干层
```

直觉：

> 保护底层通用表示，减少整体参数漂移。

但问题是：

> 领域能力可能也需要修改底层表示。

所以：

\[
\boxed{
FreezeMore
\Rightarrow
RetentionPotential\uparrow
}
\]

但可能：

\[
\boxed{
Plasticity\downarrow
}
\]

因此 Layer Freezing 不是：

> “越多越安全”。

而是：

> 稳定性和可塑性的再一次折中。

---

# 十二、Selective Training：只训练部分参数

除了 Layer Freezing，

还可以选择：

# Selective Training
## 选择性训练

例如：

```text
只训练LoRA Adapter

只训练Attention Projection

只训练MLP部分

只训练新增Embedding

只训练特定Layer
```

这样可以降低：

> 全模型参数漂移。

但同时也会限制：

> CPT 的表达能力。

所以：

\[
\boxed{
FewerTrainableParameters
\neq
AlwaysBetterRetention
}
\]

它只是：

> 降低干扰的一种手段。

---

# 十三、LoRA CPT 能不能天然避免遗忘？

不能。

这是非常重要的一条。

LoRA 的确只更新少量参数。

但只要最终推理时：

```text
Base
+
LoRA Adapter
```

整体输出行为就可能发生明显变化。

所以：

\[
\boxed{
ParameterEfficient
\neq
ForgettingFree
}
\]

LoRA 只能说明：

> 更新的参数数量更少。

不能说明：

> 原能力一定不会退化。

最终仍然要跑：

> Regression Benchmark。

---

# 十四、核心心智模型 ⑤：减少参数更新范围，不等于消除行为漂移

这条必须锁死。

\[
\boxed{
SmallParameterDelta
\neq
SmallBehaviorDelta
}
\]

尤其在 Transformer 中，

少量关键参数变化也可能引起：

> 大范围输出变化。

所以：

```text
LoRA
Layer Freezing
Selective Training
```

都是：

> Retention Mechanism。

但不是：

> Retention Guarantee。

---

# 十五、Retention Budget：能力保持必须有明确“预算”

不要只写：

> “尽量不要退化。”

而应该定义：

# Retention Budget
## 能力回归预算

例如：

```text
General Language
最大允许下降 1.5%

Math
最大允许下降 2%

Code
最大允许下降 2%

Instruction Following
最大允许下降 1%

Structured Output
不得显著下降
```

注意：

> 这些具体阈值不是通用标准。

必须由：

```text
业务风险
Benchmark稳定性
模型用途
人工成本
可接受回归范围
```

决定。

所以：

\[
\boxed{
RetentionPolicy
必须MachineCheckable
}
\]

而不是一句：

> “保持通用能力。”

---

# 十六、核心心智模型 ⑥：没有 Retention Budget，就没有真正的“能力保持”

因为如果没有阈值，

训练结束以后：

```text
数学下降3%
```

团队很难回答：

> 这是可以接受，还是必须回滚？

所以：

\[
\boxed{
NoThreshold
=
NoDecisionRule
}
\]

真正工程化应该写成：

```text
if regression <= threshold:
    pass
else:
    reject_or_rebalance
```

也就是：

> 评测结果必须能驱动决策。

---

# 十七、Dynamic Retention：Retention 强度可以动态调整

假设 CPT 初期：

```text
领域能力提升慢
通用能力稳定
```

可以：

> 降低约束强度，提高可塑性。

但如果中期出现：

```text
领域继续小幅增长
通用能力快速下降
```

可以：

```text
提高Replay比例
增加KL约束
降低Learning Rate
冻结更多层
或提前停止
```

所以：

# Dynamic Retention Control
## 动态能力保持控制

本质上是在：

> 根据 Forgetting Curve 调训练控制参数。

---

# 十八、完整能力保持流程

英文流程：

```text
Freeze Baseline
↓
Define Retention Suite
↓
Set Retention Budget
↓
Build Replay Corpus
↓
Choose Retention Mechanisms
↓
Start CPT
↓
Periodic Regression Eval
↓
Measure Forgetting
↓
Adjust Replay / Regularization / LR
↓
Continue / Stop / Rollback
↓
Release Checkpoint
```

中文解释：

```text
冻结CPT前基线
↓
定义需要保护的能力集合
↓
为每项能力设回归预算
↓
建立通用回放语料
↓
选择Replay / KL / Freeze等保持机制
↓
启动CPT
↓
定期跑通用能力回归
↓
计算遗忘程度
↓
必要时调整回放比例、正则强度或学习率
↓
决定继续、停止或回滚
↓
选择最终发布Checkpoint
```

这才是：

> **真正闭环的能力保持系统。**

---

# 十九、Replay 和 Regularization 应该怎么组合？

可以把策略分成三类。

## A. Data-level Retention
### 数据层能力保持

```text
General Replay
通用语料回放

Balanced Mixture
平衡数据混合

Interleaving
交错训练
```

---

## B. Objective-level Retention
### 目标函数层能力保持

```text
Weight Anchoring
参数锚定

KL Constraint
输出分布约束
```

---

## C. Parameter-level Retention
### 参数层能力保持

```text
Layer Freezing
层冻结

Selective Training
选择性训练

LoRA / Adapter
参数高效更新
```

三者可以组合。

所以：

\[
\boxed{
RetentionSystem
=
Data
+
Objective
+
Parameter
}
\]

---

# 二十、核心心智模型 ⑦：Retention Mechanism 不是越多越好

如果同时：

```text
Replay 40%

强KL

强Weight Anchor

冻结一半Layer

Learning Rate很低
```

结果可能是：

> 模型几乎不再学习采购领域。

所以：

\[
\boxed{
MoreProtection
\neq
BetterCPT
}
\]

能力保持不是：

> 把模型绑死。

而是：

> 找到刚好足够的约束强度。

这又回到：

\[
\boxed{
Plasticity
\leftrightarrow
Stability
}
\]

---

# 二十一、Retention Ablation：必须知道到底哪种机制在起作用

假设我们有四组实验：

```text
Run A
No Retention

Run B
Replay Only

Run C
Replay + KL

Run D
Replay + KL + Layer Freeze
```

其他条件保持一致：

```text
Same Base
Same Corpus
Same Token Budget
Same Mixture
Same Learning Rate
```

然后比较：

```text
Domain Gain

General Regression

Training Cost

Convergence Speed
```

这样才能知道：

> 真正有效的是哪种机制。

所以：

\[
\boxed{
RetentionPolicy
必须可Ablate
}
\]

---

# 二十二、Release Gate：Retention 最终必须进入发布门槛

训练结束后，

不能只判断：

```text
领域指标上涨
→ 发布
```

而应该：

```text
Domain Gain
达到最低收益

AND

General Regression
不超过阈值

AND

Instruction Regression
不超过阈值

AND

No Critical Capability Failure
没有关键能力崩溃
```

只有全部通过：

\[
\boxed{
ReleaseGate=True
}
\]

才允许进入下一阶段。

---

# 二十三、核心心智模型 ⑧：Retention 不是单独模块，而是 Release Policy 的一部分

如果 Retention 只存在于：

> 训练脚本里，

而没有进入：

> 发布决策，

那它就没有真正工程化。

所以：

\[
\boxed{
Retention
必须进入
ReleaseGate
}
\]

也就是说：

> 能力保持是发布条件，不是训练建议。

---

# 二十四、本阶段正式工程产物：`ProcurementCPTRetentionPolicy_V0.1`

第一版至少锁定：

```text
retention_policy_version

baseline_model_id

retention_capability_suite

retention_budget

replay_enabled

replay_corpus_version

replay_ratio

interleaving_policy

weight_anchor_enabled

weight_anchor_lambda

kl_constraint_enabled

kl_beta

reference_model_id

layer_freezing_policy

trainable_parameter_scope

lora_or_adapter_policy

learning_rate_policy

dynamic_retention_enabled

adjustment_triggers

regression_eval_interval

forgetting_curve_required

retention_ablation_plan

release_gate

rollback_policy

trace_logging
=
enabled
```

每个训练 Run 至少记录：

```text
run_id

checkpoint_id

replay_ratio

retention_loss_weight

kl_beta

trainable_parameters

frozen_layers

learning_rate

domain_metrics

general_metrics

regression_delta

retention_budget_status

adjustment_action

release_decision
```

这样以后才能回答：

> **模型为什么既学会了采购，又没有明显忘掉原来的能力？**

---

# 二十五、本阶段最重要的 8 个核心心智模型

> **心智模型 ①：`DetectForgetting ≠ PreventForgetting`。发现遗忘是诊断，能力保持是训练控制。**

> **心智模型 ②：`Retention ≠ FreezeEverything`。能力保持不是不让模型变化，而是让变化发生在值得变化的地方。**

> **心智模型 ③：`Replay = OldDistributionReminder`。回放的本质是让旧分布在训练过程中继续获得梯度支持。**

> **心智模型 ④：`Retention = Data Constraint + Objective Constraint + Parameter Constraint`。能力保持可以从数据、目标函数和参数更新范围三个层面同时实现。**

> **心智模型 ⑤：`ReferenceModel ≠ GroundTruth`。参考模型只是行为锚点，不是永远正确的老师。**

> **心智模型 ⑥：`SmallParameterDelta ≠ SmallBehaviorDelta`。少量参数更新仍然可能带来明显行为变化。**

> **心智模型 ⑦：`RetentionBudget = DecisionRule`。没有可量化的回归阈值，就没有真正可执行的能力保持策略。**

> **心智模型 ⑧：`MoreProtection ≠ BetterCPT`。约束过强会让模型学不进去，Retention 仍然必须平衡 Plasticity 与 Stability。**

---

# 二十六、把完整 Retention 流程压成一张专业工程图

```text
                    Pre-CPT Baseline
                       CPT前基线
                            │
                            ▼
                    Retention Suite
                  定义要保护的能力
                            │
                            ▼
                    Retention Budget
                  为每项能力设回归阈值
                            │
                            ▼
                  Retention Mechanisms
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
          Replay       Regularization   Parameter Scope
         通用回放        正则化约束        参数更新范围
            │               │               │
            └───────────────┼───────────────┘
                            ▼
                          CPT
                        继续预训练
                            │
                            ▼
                 Periodic Regression Eval
                   定期通用能力回归
                            │
                            ▼
                      Forgetting Curve
                       形成遗忘曲线
                            │
                            ▼
                  Dynamic Retention Control
             调整Replay / KL / LR / Freeze
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
          Continue        Early Stop      Rollback
            继续            提前停止        回滚
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                      Release Gate
                   通过能力保持发布门
                            │
                            ▼
                    Release Checkpoint
```

脑中最后只留一句：

> **能力保持的真正目标不是让 CPT 模型“尽量像原模型”，而是在明确回归预算下，让模型获得足够的领域可塑性，同时通过 Replay、正则化和参数约束把旧能力的损失控制在可接受范围内。**

---

# 第八课 · 第 7 阶段掌握测试

现在不回看正文，你应该能够解释：为什么 Detect Forgetting 和 Prevent Forgetting 是两件事；Replay 的本质是什么；Replay Ratio 为什么不能固定照抄；Replay Corpus 为什么不需要等于原始预训练语料；Interleaving 在训练时间轴上解决什么问题；Regularization 为什么属于 Objective-level Retention；Weight Anchoring 如何工作；KL Constraint 为什么需要 Reference Model；为什么 Reference Model 不等于 Ground Truth；Layer Freezing 和 Selective Training 分别解决什么问题；为什么 LoRA 不能自动避免遗忘；为什么 `SmallParameterDelta ≠ SmallBehaviorDelta`；Retention Budget 为什么必须机器可检查；Dynamic Retention 怎样根据 Forgetting Curve 调整；Data-level、Objective-level、Parameter-level Retention 如何组合；为什么 More Protection 不一定更好；Retention Ablation 为什么重要；以及为什么能力保持最终必须进入 Release Gate。

如果这些能够完整讲出来：

\[
\boxed{
第八课第7阶段真正掌握
}
\]

---

# 下一阶段：第八课 · 第 8 阶段
# Synthetic Data & Curriculum：合成领域语料、难度分层与覆盖扩展
## 当真实政府采购语料覆盖不足时，合成数据能不能补？为什么“让 LLM 多生成一些采购文本”可能反而把模型训练得更假？

下一阶段会正式进入：

```text
Synthetic Data
合成数据

Teacher Generation
教师模型生成

Data Augmentation
数据增强

Coverage Expansion
覆盖扩展

Hard Case Generation
难例生成

Curriculum Learning
课程式训练

Difficulty Scheduling
难度调度

Quality Filtering
质量过滤

Synthetic Contamination
合成污染

Model Collapse Risk
模型坍缩风险

Human Validation
人工验证
```

并建立：

# `ProcurementCPTSyntheticCurriculumPolicy_V0.1`

下一阶段最关键的一条边界会是：

\[
\boxed{
SyntheticData
\neq
FreeNewKnowledge
}
\]

也就是说：

> **合成数据可以重组、放大和补覆盖，但它不能凭空创造可靠的新事实世界。**

---
