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
