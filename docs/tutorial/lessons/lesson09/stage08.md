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
