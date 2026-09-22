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
