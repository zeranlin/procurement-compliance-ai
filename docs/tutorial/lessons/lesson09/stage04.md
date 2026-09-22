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
