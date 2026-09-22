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
