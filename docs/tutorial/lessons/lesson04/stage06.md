# 第四课 · 第 6 阶段：Train / Validation / Test 到底应该怎么切？
## 为什么对政府采购数据“随机按行切 8:1:1”可能从根本上就是错的？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Benchmark 泄漏不一定是把答案文件直接放进训练集。**
2. **Split 的单位不一定是 Row， 很多时候应该是 Project / Group**
3. **Train / Validation / Test 的核心区别 不是“比例”，而是“用途”**
4. **同一个 Project 的 Clause 通常不应该跨 Train / Test**
5. **Duplicate Group / Template Group 也不能随便跨 Split**
6. **时间是最接近真实生产环境的一种隔离方式**
7. **Test Set 一旦开始被反复看， 它就正在慢慢变成 Train Set**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |
| `Validation` | 验证集：开发阶段用于选模型、调参数和早停 |
| `Split` | 数据切分：按项目/时间/地区划分训练、验证、测试数据 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `Dataset` | 数据集：按统一 Schema、版本和质量标准组织的样本集合 |
| `Sample` | 样本：具有明确输入、目标和来源的一条训练/评测记录 |
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `Accuracy` | 准确率：全部样本中判断正确的比例 |
| `Checkpoint` | 检查点：保存模型和训练状态以便恢复/发布 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |
| `Metadata` | 元数据：项目、来源、时间、地区、版本等辅助信息 |
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

第五阶段结束以后，我们已经把数据从：

```text
CleanClause_V0.1
```

推进到了：

```text
DedupedClauseSet_V0.1
```

现在每一条 Clause 不仅知道：

```text
它来自哪个 project
它来自哪个 document
它属于哪个 section
它的原始文本是什么
它的规范化文本是什么
它有没有重复关系
它属于哪个 duplicate group
它属于哪个 template group
```

于是很多人接下来会非常自然地写：

```python
from sklearn.model_selection import train_test_split

train, test = train_test_split(
    data,
    test_size=0.2,
    random_state=42
)
```

甚至再切一次：

```text
80% Train
10% Validation
10% Test
```

看起来非常标准。

教科书里也经常这么写。

但对于我们的政府采购数据：

> **这可能从数据集设计的第一步就把 Benchmark 做假。**

今天这一阶段要解决的，不是“80%、10%、10%怎么写代码”。

而是一个更本质的问题：

# 什么东西绝对不能被拆到不同数据集里？

---

# 一、本阶段真正要解决的一个核心问题

今天只解决：

> **怎样把政府采购数据切成真正独立的 Train / Validation / Test，使 Test 尽量模拟模型未来遇到的“新项目”，而不是偷偷把训练数据的兄弟姐妹拿来考试？**

最终我们要产出：

# `DatasetSplit_V0.1`

从第五阶段：

```text
DedupedClauseSet_V0.1
```

推进到：

```text
Train
Validation
Test
```

但真正的流水线应该是：

```text
DedupedClauseSet
        ↓
Leakage Groups
        ↓
Group-aware Split
        ↓
Distribution Check
        ↓
Leakage Audit
        ↓
Frozen Test Set
        ↓
DatasetSplit_V0.1
```

---

# 二、先建立本阶段最重要的 6 个核心心智模型

先把这六句话钉住：

```text
① Split 的单位不一定是 Row，
   很多时候应该是 Project / Group

② Train / Validation / Test 的核心区别
   不是“比例”，而是“用途”

③ 同一个 Project 的 Clause
   通常不应该跨 Train / Test

④ Duplicate Group / Template Group
   也不能随便跨 Split

⑤ 时间是最接近真实生产环境的一种隔离方式

⑥ Test Set 一旦开始被反复看，
   它就正在慢慢变成 Train Set
```

最后一句非常重要。

以后会发现：

> Benchmark 泄漏不一定是把答案文件直接放进训练集。

人类不断根据 Test 调模型：

> 一样会泄漏。

---

# 三、先彻底理解 Train、Validation、Test 各自在干什么

很多人知道三个名字。

但没有真正理解它们的角色。

我们先不用机器学习术语。

用：

# 上课、模拟考试、期末考试

来类比。

---

# 四、Train Set 是什么？

Train：

> 教材 + 平时练习题。

模型训练时：

```text
直接看到这些样本
```

并根据这些样本：

> 修改 Weight。

---

# 五、也就是说

Train 数据直接影响：

\[
\boxed{
ModelParameters
}
\]

这是模型真正：

> “学过”的内容。

---

# 六、例如我们有一条：

```text
供应商须在本市注册。
```

Train Label：

```text
potential_risk
```

模型通过训练：

> 学习这种判断模式。

---

# 七、Validation Set 是什么？

Validation：

> 模拟考试。

它的作用不是：

> 更新模型 Weight。

而是帮助我们决定：

```text
哪个模型更好？
训练几轮？
Learning Rate多少？
LoRA Rank多少？
哪个Prompt更好？
哪个Threshold更好？
哪个Checkpoint最好？
```

---

# 八、也就是说 Validation 会影响：

# Model Selection

虽然模型没有直接对 Validation 做梯度下降，

但人类会根据 Validation：

> 改系统。

---

# 九、举个例子

我们训练：

```text
Checkpoint A
Checkpoint B
Checkpoint C
```

Validation Accuracy：

```text
A = 82%
B = 86%
C = 84%
```

于是我们选：

```text
B
```

Validation：

> 已经影响了最终模型。

---

# 十、所以 Validation 其实不是“完全没被模型见过”

更准确说：

> **它没有直接用于参数梯度更新，但它参与了整个开发决策。**

---

# 十一、Test Set 是什么？

Test：

> 真正期末考试。

它应该尽量只回答：

> **整个模型和开发流程完成以后，对真正没参与开发决策的数据表现如何？**

---

# 十二、所以三个集合可以记成

```text
Train
=
学

Validation
=
选

Test
=
最后考
```

---

# 十三、这三个字比 8:1:1 更重要

因为：

> 比例是工程参数。

角色：

> 才是统计意义。

---

# 十四、所以第二个核心心智模型可以写成

\[
\boxed{
Train = Learn
}
\]

\[
\boxed{
Validation = Select
}
\]

\[
\boxed{
Test = Estimate
}
\]

Test 最终在估计：

> 模型面对真正新数据的能力。

---

# 十五、为什么随机按行切在采购数据中危险？

先看一个非常具体的例子。

假设一个采购项目：

```text
Project P001
```

有：

```text
300个Clause
```

---

# 十六、里面包括

```text
资格条件：40条
技术参数：120条
商务要求：50条
评分标准：60条
合同条款：30条
```

---

# 十七、如果我们按行随机切 80/10/10

大概会得到：

```text
P001
├── 240条 → Train
├── 30条  → Validation
└── 30条  → Test
```

看起来：

> 很公平。

实际上：

> 非常危险。

---

# 十八、为什么？

Test 中虽然某一句 Clause：

> 没进入 Train。

但是 Train 已经包含：

```text
同一个项目名称
同一个采购需求
同一个项目预算
同一种排版
同一套模板
同一批技术参数
同一章上下文
同一个采购代理机构写作习惯
```

---

# 十九、于是 Test 不是在问：

> 模型能不能处理一个新采购项目？

而更像在问：

> **看过这本书 80% 内容以后，能不能猜剩下 10%？**

---

# 二十、这当然比处理一本从没见过的新书容易。

---

# 二十一、所以这里发生的是

# Group Leakage

分组泄漏。

---

# 二十二、最常见的 Group 就是：

# Project

因此第一条极其重要的原则：

\[
\boxed{
同一个Project
尽量只属于一个Split
}
\]

---

# 二十三、也就是说

正确方式更像：

```text
Project P001
全部 → Train

Project P002
全部 → Train

Project P003
全部 → Validation

Project P004
全部 → Test
```

---

# 二十四、而不是：

```text
P001的一部分 → Train
P001的一部分 → Validation
P001的一部分 → Test
```

---

# 二十五、这叫

# Group-aware Split

按 Group 切分。

---

# 二十六、第一个核心概念出现了

\[
\boxed{
SplitUnit
\neq
SampleRow
}
\]

Split Unit：

> 不一定是一行样本。

对于我们的项目：

> 经常是一个 Project Group。

---

# 二十七、为什么不是 Document？

假设一个项目有：

```text
招标文件
更正公告
采购公告
评分附件
合同草案
```

如果按 Document 切：

```text
招标文件 → Train
更正公告 → Test
```

还是可能泄漏。

---

# 二十八、因为它们属于：

> 同一个真实采购事件。

所以：

```text
project_id
```

通常比：

```text
document_id
```

更适合作为基础 Split Group。

---

# 二十九、这就是为什么第一阶段我们那么早就要求：

```text
project_id
```

必须保存。

当时可能觉得：

> 一个 Metadata 字段而已。

现在终于看到：

> 没有它，Benchmark 甚至可能无法正确建立。

---

# 三十、这就是好 Schema 的长期价值

前面一个字段设计正确，

后面：

> 省掉大量返工。

---

# 三十一、但是 Project Group 就够了吗？

不够。

第五阶段刚刚发现：

```text
Project A
```

和：

```text
Project B
```

虽然 project_id 不同，

可能：

> 使用完全相同的采购模板。

---

# 三十二、例如：

Project A：

> 智慧校园系统项目。

Project B：

> 智慧政务系统项目。

两个项目来自：

> 同一个代理机构。

---

# 三十三、资格条件几乎完全一样：

```text
供应商须……
供应商应……
供应商不得……
```

只替换：

```text
项目名称
项目编号
预算
日期
```

---

# 三十四、于是：

```text
Project A → Train
Project B → Test
```

表面上：

> Project 隔离了。

但实际上：

> Template 泄漏了。

---

# 三十五、这就是：

# Template Leakage

第五阶段已经见过。

现在它第一次变成：

> Split 设计问题。

---

# 三十六、所以我们还需要考虑：

```text
template_group_id
```

---

# 三十七、例如：

```text
TG-0017
├── Project A
├── Project B
├── Project C
├── Project D
└── Project E
```

---

# 三十八、如果我们真的要测试：

> 对新模板的泛化能力，

这五个项目：

> 最好不要跨 Train/Test。

---

# 三十九、于是 Split Group 开始变复杂：

```text
Project Group
+
Duplicate Group
+
Template Group
```

---

# 四十、接下来还有一个 Group

# Duplicate Group

假设：

```text
Clause A
```

和：

```text
Clause B
```

是同一内容不同格式。

第五阶段已经放进：

```text
DG-0031
```

---

# 四十一、如果：

```text
A → Train
B → Test
```

那几乎就是：

> 开卷考试。

---

# 四十二、所以所有：

```text
duplicate_group_id
```

成员：

> 绝对不应该跨 Train/Test。

---

# 四十三、因此我们已经有第一版 Leakage Constraint：

```text
同Project
不能跨Train/Test

同DuplicateGroup
不能跨Train/Test

高相似TemplateGroup
尽量不能跨Train/Test
```

---

# 四十四、这可以写成一个非常直观的数学约束

对任意 Group \(G\)：

\[
\boxed{
G
\subseteq
Train
\quad
\text{or}
\quad
G
\subseteq
Validation
\quad
\text{or}
\quad
G
\subseteq
Test
}
\]

不能：

\[
G
\cap Train \neq \varnothing
\]

同时又：

\[
G
\cap Test \neq \varnothing
\]

---

# 四十五、翻译成人话：

> **同一个泄漏群体只能进一个集合。**

---

# 四十六、但现在出现一个麻烦问题

假设：

```text
Project A
```

和：

```text
Project B
```

不同 Project。

但共享：

```text
Template Group T1
```

---

# 四十七、同时：

Project B 的某条 Clause

又和：

Project C 的 Clause

属于：

```text
Duplicate Group D7
```

---

# 四十八、那么：

```text
A
↔ Template
B
↔ Duplicate
C
```

实际上：

> 三个 Project 被连接起来了。

---

# 四十九、这时不能：

```text
A → Train
B → Train
C → Test
```

因为：

B 和 C：

> 有 Duplicate Link。

---

# 五十、所以更专业的做法是：

# Build Leakage Graph

建立泄漏关系图。

---

# 五十一、节点可以是：

```text
Project
```

边可以是：

```text
Duplicate Relation
Template Relation
Version Relation
```

---

# 五十二、例如：

```text
Project A
   │ Template
   ▼
Project B
   │ Duplicate
   ▼
Project C
```

那么 A、B、C：

> 可能应该作为一个 Connected Group。

---

# 五十三、也就是：

# Connected Component

连通分量。

---

# 五十四、别被术语吓到。

生活类比：

假设老师规定：

> 同一家族的人不能有人进训练题库、有人进考试题库。

---

# 五十五、A 是 B 的兄弟。

B 是 C 的兄弟。

即使 A 和 C：

> 没直接关系。

A、B、C 仍然属于：

> 同一个家庭群。

---

# 五十六、数据也是一样。

只要通过高风险泄漏关系：

> 连起来，

就可以考虑：

> 整体一起 Split。

---

# 五十七、这会形成：

```text
split_group_id
```

例如：

```text
SG-0001
```

里面：

```text
Project A
Project B
Project C
```

---

# 五十八、然后真正切的是：

# Split Group

而不是：

# Clause Row

---

# 五十九、于是第一版总关系变成：

```text
Clause
  ↓
Document
  ↓
Project
  ↓
Duplicate / Template Relations
  ↓
Leakage Connected Group
  ↓
split_group_id
```

---

# 六十、这个 `split_group_id`

以后极其重要。

---

# 六十一、现在理解 Train / Validation / Test 的真正切分单位了

不是：

```text
一条 Clause
```

而更像：

```text
一个独立信息群体
```

---

# 六十二、于是我们可以把今天核心压成：

\[
\boxed{
真正的Split
是在切独立信息源
而不是在切行
}
\]

---

# 六十三、现在讨论比例

是不是一定要：

```text
80 / 10 / 10
```

不是。

---

# 六十四、常见比例可能有：

```text
80 / 10 / 10
```

也可能：

```text
70 / 15 / 15
```

或者：

```text
90 / 5 / 5
```

---

# 六十五、真正应该问的是：

> Test 是否足够大，能稳定估计业务能力？

以及：

> Validation 是否足够支撑模型选择？

---

# 六十六、假设只有：

```text
1000个项目
```

Test 放：

```text
100个项目
```

可能已经不错。

---

# 六十七、如果有：

```text
100万个项目
```

Test 未必需要：

> 10 万个。

因为评测成本：

> 很高。

---

# 六十八、特别是 Expert Gold Set

人工高质量审核：

> 非常昂贵。

所以 Test 比例：

> 不是越大越好。

---

# 六十九、真正重要的是

# Effective Test Size

有效测试规模。

---

# 七十、如果 Test 有：

```text
100,000条Clause
```

但是：

> 90,000 条来自同一个模板，

有效信息量：

> 可能远少于 100,000。

---

# 七十一、反过来，

Test 只有：

```text
5,000条
```

但覆盖：

```text
100个项目类型
多个地区
多种风险
大量Hard Case
```

可能：

> 更有价值。

---

# 七十二、所以 Test Size 不应该只看：

# Row Count

还要看：

# Diversity

---

# 七十三、再次出现第五阶段那个公式：

\[
\boxed{
MoreRows
\neq
MoreInformation
}
\]

---

# 七十四、现在进入第二个大问题

# Distribution

如果按 Group 切，

有可能出现：

```text
Train
90% 技术参数

Test
70% 资格条件
```

---

# 七十五、这时候 Test 分数不好，

不一定是：

> 模型泛化特别差。

可能只是：

> Train 和 Test 的任务组成完全不一样。

---

# 七十六、所以一般需要检查：

# Label Distribution

例如五类风险：

```text
qualification
technical
commercial
scoring
requirements
```

---

# 七十七、我们希望 Train / Val / Test：

> 不一定完全一样，

但至少知道：

> 各自分布是什么。

---

# 七十八、例如：

| Risk Type | Train | Val | Test |
|---|---:|---:|---:|
| Qualification | 21% | 20% | 22% |
| Technical | 29% | 30% | 28% |
| Commercial | 18% | 17% | 19% |
| Scoring | 17% | 18% | 16% |
| Requirements | 15% | 15% | 15% |

这种比较容易解释。

---

# 七十九、但是不要为了让比例漂亮：

> 把同 Project 拆开。

---

# 八十、也就是说

# Group Integrity

优先级通常高于：

# Perfect Stratification

---

# 八十一、这是很重要的权衡。

你不能为了：

```text
每类刚好20%
```

把同一个项目：

> 拆进三个集合。

---

# 八十二、因此我们需要：

# Group-aware Stratification

不是普通 Stratification。

---

# 八十三、什么是 Stratification？

简单说：

> 切分时尽量保持类别比例。

---

# 八十四、普通二分类：

```text
正样本 20%
负样本 80%
```

希望：

Train / Val / Test：

> 都大约保持这个比例。

---

# 八十五、但我们的 Group 很大。

一个项目可能有：

```text
80% technical
20% commercial
```

另一个项目：

```text
90% scoring
```

---

# 八十六、所以 Group-aware Stratification 本质上变成一个：

# Packing Problem

---

# 八十七、就像有很多箱子。

每个箱子里装：

> 不同比例的彩球。

你不能拆箱。

现在要把箱子分成：

```text
Train堆
Val堆
Test堆
```

同时尽量让：

> 三堆颜色分布合理。

---

# 八十八、这就是 Group Split 的现实难度。

---

# 八十九、因此切分算法不一定一次随机完成。

可以：

```text
多次候选 Split
↓
计算分布偏差
↓
选择较好的
```

---

# 九十、甚至用优化算法。

但第一版不需要复杂。

先建立正确原则：

> **Group First, Balance Second。**

---

# 九十一、现在看另一个很重要的维度：

# Positive / Negative

假设 Risk Review 数据：

```text
Potential Risk
No Risk
Needs Review
```

---

# 九十二、如果 Test 几乎全是：

```text
No Risk
```

模型只要一直回答：

```text
No Risk
```

Accuracy：

> 可能很漂亮。

---

# 九十三、但风险识别：

> 完全没用。

---

# 九十四、所以 Test 必须保证：

> 业务关键类别有足够样本。

---

# 九十五、尤其我们最终最关心：

# False Negative

真正有风险的条款，

模型却说：

> 没风险。

---

# 九十六、这类样本在 Test：

> 必须有足够规模。

---

# 九十七、所以 Test 设计本质上是：

# Evaluation Design

不是简单 Data Split。

---

# 九十八、你想测什么能力，

就必须：

> 在 Test 里有对应案例。

---

# 九十九、例如想测：

```text
技术参数倾向性
```

如果 Test：

> 只有 8 条这种案例。

那结果：

> 波动会非常大。

---

# 一百、8 条里错 1 条：

Accuracy：

```text
87.5%
```

错 2 条：

```text
75%
```

---

# 一百零一、样本太少：

> 一条错误就大幅改变指标。

---

# 一百零二、所以关键 Slice：

> 需要最小样本量。

---

# 一百零三、这和第八课的 Gold Benchmark 会深度连接。

现在先记：

> **Test 不只是总量够，还要每个关键 Slice 够。**

---

# 一百零四、现在进入今天非常重要的主题：

# Time-aware Split

时间切分。

---

# 一百零五、假设我们有：

```text
2023
2024
2025
2026
```

四年的采购项目。

---

# 一百零六、我们可以随机按项目切。

也可以：

```text
2023～2025
→ Train

2026年1～6月
→ Validation

2026年7～9月
→ Test
```

---

# 一百零七、后者更接近什么？

现实部署。

---

# 一百零八、真实生产环境永远是：

```text
过去的数据
      ↓
训练
      ↓
面对未来的数据
```

模型不可能：

> 用未来数据训练以后再回到过去部署。

---

# 一百零九、所以从真实业务模拟角度：

# Temporal Split

时间切分非常强。

---

# 一百一十、可以写成：

\[
\boxed{
TrainTime
<
ValidationTime
<
TestTime
}
\]

---

# 一百一十一、这个方法特别能检测：

# Temporal Generalization

模型能不能：

> 对未来的新项目继续工作。

---

# 一百一十二、这比纯随机 Split：

> 更难。

但也：

> 更真实。

---

# 一百一十三、为什么时间切分通常更难？

因为未来会发生：

```text
政策变化
法规更新
采购模板变化
新技术产品出现
新项目类型出现
语言表达变化
```

---

# 一百一十四、所以 Test 不再只是：

> 同一分布的随机样本。

而开始包含：

# Distribution Shift

分布漂移。

---

# 一百一十五、这其实正是部署中：

> 真正会发生的事情。

---

# 一百一十六、比如 2025 年以前：

某类采购文件普遍使用：

```text
传统服务器参数
```

2026 年开始：

> 出现新的 AI 算力采购。

---

# 一百一十七、模型在历史数据训练以后，

能不能处理：

> 新采购类别？

Temporal Test：

> 能测出来。

---

# 一百一十八、但时间切分也不是永远必须。

取决于：

> 我们想回答什么问题。

---

# 一百一十九、例如研究问题 A：

> 在当前数据分布中，模型对新项目表现如何？

可以：

# Project Holdout

---

# 一百二十、研究问题 B：

> 用历史数据训练后，面对未来项目表现如何？

可以：

# Temporal Holdout

---

# 一百二十一、研究问题 C：

> 在某些未见地区能不能泛化？

可以：

# Geographic Holdout

---

# 一百二十二、比如：

```text
Train:
东部若干地区

Test:
一个从未进入训练的地区
```

---

# 一百二十三、这会测试：

> 区域泛化。

---

# 一百二十四、再比如：

# Agency Holdout

某些采购代理机构：

> 使用自己的模板。

---

# 一百二十五、如果同一家代理机构：

Train/Test 都有，

模型可能只是：

> 学会这个代理机构的模板。

---

# 一百二十六、所以甚至可以做：

```text
Agency-level Holdout
```

测试：

> 新机构。

---

# 一百二十七、这说明一个非常深的概念：

# Test Set should represent the generalization question

测试集应该代表：

> **你真正想知道的泛化问题。**

---

# 一百二十八、所以：

> “Test 怎么切？”

不能脱离：

> “未来模型要面对什么？”

---

# 一百二十九、这就是为什么没有万能：

```text
80/10/10
```

答案。

---

# 一百三十、现在给 ProcurementAI 建三个层级的评测 Split

这是一个很有价值的设计。

---

# 一百三十一、第一层：

# IID-like Project Holdout

虽然项目隔离，

但 Train/Test：

> 时间、地区、任务分布接近。

---

# 一百三十二、它回答：

> **面对同类分布中的新项目，模型表现如何？**

---

# 一百三十三、第二层：

# Temporal Holdout

Test 来自：

> 未来时间窗口。

---

# 一百三十四、它回答：

> **面对未来项目，性能掉多少？**

---

# 一百三十五、第三层：

# Stress / OOD Holdout

例如：

```text
新地区
新项目类型
稀有风险
Hard Negative
超长文档
复杂评分表
```

---

# 一百三十六、它回答：

> **模型离开舒适区以后会怎样？**

---

# 一百三十七、所以以后成熟 Benchmark 不一定只有：

# 一个 Test Set

可以有：

```text
Test-IID
Test-Future
Test-Hard
```

---

# 一百三十八、但是现在 Stage 6：

第一版先建立：

# 主 Train / Val / Test

并为后面：

> 多测试集

保留 Metadata。

---

# 一百三十九、现在看 Validation 怎么切

很多团队非常重视 Test 隔离，

但忽略 Validation。

---

# 一百四十、假设：

```text
Train
和Validation
大量共享模板
```

会发生什么？

---

# 一百四十一、你会根据 Validation：

> 选择模型。

模型 A：

> 更会背模板。

于是 Validation 分数高。

---

# 一百四十二、你最后选了 A。

虽然 Test 最终可能揭露问题，

但整个模型开发过程：

> 已经被 Validation 偏置。

---

# 一百四十三、所以 Validation 也应该：

> 做类似 Group Isolation。

---

# 一百四十四、通常我们希望：

\[
\boxed{
Train \cap Validation = \varnothing
}
\]

\[
\boxed{
Train \cap Test = \varnothing
}
\]

\[
\boxed{
Validation \cap Test = \varnothing
}
\]

当然这里不是只说：

> Row 不重叠。

而是：

# Leakage Group 不重叠

---

# 一百四十五、更准确可以写：

\[
\boxed{
SplitGroup_{Train}
\cap
SplitGroup_{Val}
=
\varnothing
}
\]

\[
\boxed{
SplitGroup_{Train}
\cap
SplitGroup_{Test}
=
\varnothing
}
\]

---

# 一百四十六、这才是我们真正关心的。

---

# 一百四十七、现在出现一个常见问题：

# 我数据很少怎么办？

假设只有：

```text
200个项目
```

再按 Group 切：

> Test 很小。

---

# 一百四十八、这时可以使用：

# Cross-validation

交叉验证。

---

# 一百四十九、但注意：

不能用普通 Row-level K-fold。

应该使用：

# Group K-fold

---

# 一百五十、例如 5 Fold：

```text
Project Group
```

整体进入一个 Fold。

---

# 一百五十一、每次：

```text
4份 Train
1份 Validation
```

轮流测试。

---

# 一百五十二、这样能够更充分利用小数据。

---

# 一百五十三、但对于最终 Test：

> 仍然最好保留独立 Holdout。

---

# 一百五十四、也就是说：

```text
Train/Dev Pool
       ↓
Group Cross Validation
```

用于开发。

另外：

```text
Final Test
```

彻底冻结。

---

# 一百五十五、这是一种很稳健的架构。

---

# 一百五十六、现在讲一个非常危险的现象：

# Test Set Peeking

偷看 Test。

---

# 一百五十七、比如第一次 Test：

```text
Accuracy = 78%
```

你查看错误：

> 技术参数类很差。

---

# 一百五十八、于是修改：

```text
Prompt
```

再跑 Test：

```text
82%
```

---

# 一百五十九、再发现：

> 评分条款不行。

又修改：

```text
Rule
```

Test：

```text
85%
```

---

# 一百六十、重复 50 次。

这个 Test 还是 Test 吗？

---

# 一百六十一、统计意义上：

> 越来越不像了。

因为你已经根据 Test：

> 开发系统。

---

# 一百六十二、Test 开始扮演：

# Validation

的角色。

---

# 一百六十三、所以第六个核心心智模型：

\[
\boxed{
RepeatedTestFeedback
\rightarrow
TestContamination
}
\]

---

# 一百六十四、人没有把 Test 文件直接送去训练。

但人类大脑：

> 已经在训练。

---

# 一百六十五、所以成熟项目通常有：

```text
Development Validation Set
```

可以经常看。

---

# 一百六十六、以及：

```text
Final Locked Test Set
```

尽量少碰。

---

# 一百六十七、甚至更成熟可以有：

# Hidden Test

开发者：

> 看不到答案。

---

# 一百六十八、每次提交模型：

> 自动评分。

这能减少：

> 人工针对 Test 调参。

---

# 一百六十九、第八课做 Benchmark 时，

我们会再次回到：

> Test Governance。

---

# 一百七十、现在看一个完整的泄漏案例

假设：

```text
Project P001
```

有 100 个 Clause。

其中一条：

```text
供应商须在本市设有服务机构。
```

---

# 一百七十一、另一个：

```text
Project P381
```

用了同一模板。

写成：

```text
供应商须在项目所在地设有服务机构。
```

---

# 一百七十二、现在：

```text
P001 → Train
P381 → Test
```

Project 不重复。

---

# 一百七十三、但：

```text
template_group_id
```

一样。

模型训练时：

> 见过大量高度相似表达。

---

# 一百七十四、测试成绩：

> 可能虚高。

---

# 一百七十五、是不是所有 Template Group 都必须严格隔离？

不一定。

---

# 一百七十六、这取决于：

> 你想测什么。

如果生产环境里：

> 未来确实会继续大量使用相同模板，

那么 Test 里出现同模板新项目：

> 也有现实意义。

---

# 一百七十七、所以成熟评测可以同时测两类：

```text
Seen-template New-project
```

和：

```text
Unseen-template New-project
```

---

# 一百七十八、这是一个非常专业的切片。

---

# 一百七十九、第一类回答：

> 模型面对熟悉模板的新项目能力如何？

---

# 一百八十、第二类回答：

> 模型面对陌生模板的新项目能力如何？

---

# 一百八十一、如果只给一个总分，

这两种能力：

> 会被混在一起。

---

# 一百八十二、所以我们以后可以有字段：

```text
template_seen_in_train = true / false
```

---

# 一百八十三、然后单独评测：

```text
Seen Template Accuracy
```

和：

```text
Unseen Template Accuracy
```

---

# 一百八十四、这就是 Metadata 的力量。

---

# 一百八十五、现在再看法规引用。

Train 项目和 Test 项目：

> 都引用同一法律条文。

这算泄漏吗？

---

# 一百八十六、不一定。

如果我们训练的是：

> 合规分析模型，

法规本来就是：

> 应该掌握的公共知识。

---

# 一百八十七、所以不能说：

> Test 里引用的法规在 Train 出现过，就一定泄漏。

---

# 一百八十八、这暴露了一个更深的概念：

# What is supposed to generalize?

---

# 一百八十九、我们真正希望模型泛化的是：

```text
新采购项目
新条款表达
新业务组合
```

而不是：

> 每次考试都必须遇到完全陌生的法律。

---

# 一百九十、所以：

# Shared Knowledge ≠ Leakage

---

# 一百九十一、但是：

# Shared Answer Instance

通常才是危险。

---

# 一百九十二、比如 Test Case：

```text
Clause + Expert Rationale
```

如果同一 Clause 和同一 Rationale：

> 已经进入 SFT Train。

这当然：

> 是严重泄漏。

---

# 一百九十三、所以 Leakage 判断要问：

> **模型训练时是否已经接触了这个测试问题本身，或者高度等价的答案实例？**

---

# 一百九十四、共享通用法规知识：

> 可以接受。

共享同一项目的判例式答案：

> 很危险。

---

# 一百九十五、这也为第七阶段：

# Data Leakage

铺路。

第六阶段重点是：

> 正确 Split。

第七阶段会专门研究：

> 即使 Split 看起来正确，数据仍然怎样偷偷泄漏。

---

# 一百九十六、现在看 Label Leakage 与 Split Leakage 的区别

第四课第一阶段讲过：

# Label Leakage

Input 里直接出现：

> 答案。

---

# 一百九十七、今天讲的是：

# Split Leakage

训练集和测试集之间：

> 信息隔离失败。

---

# 一百九十八、两者完全不同。

---

# 一百九十九、例如：

Input：

```text
专家判断：本条存在地域歧视。
原条款：……
```

这是：

> Label Leakage。

---

# 二百、而：

```text
同一项目的99条Clause在Train
第100条在Test
```

这是：

> Split Leakage。

---

# 二百零一、再比如：

```text
同一模板变体
Train/Test各一半
```

属于：

> Template Leakage。

---

# 二百零二、再比如：

```text
同一Duplicate Group
Train/Test各一个
```

属于：

> Duplicate Leakage。

---

# 二百零三、所以以后我们可以建立 Leakage Taxonomy：

```text
Label Leakage
Project Leakage
Document Leakage
Duplicate Leakage
Template Leakage
Temporal Leakage
Answer Leakage
```

---

# 二百零四、第七阶段会把这张图做完整。

---

# 二百零五、现在回到真正工程操作。

第一版 Split Pipeline 可以这样做。

---

# 二百零六、Step 1：确定 Split Objective

先写一句：

> Test 想模拟什么？

例如我们的 Baseline：

> **模拟模型面对未来从未参与训练的新政府采购项目时的风险审查能力。**

---

# 二百零七、这句话决定：

> 后面怎么 Split。

---

# 二百零八、Step 2：定义基础 Group

至少：

```text
project_id
```

---

# 二百零九、Step 3：加入泄漏关系

比如：

```text
duplicate_group_id
```

---

# 二百一十、必要时：

```text
template_group_id
```

---

# 二百一十一、Step 4：生成 `split_group_id`

将相互连接的项目：

> 合成不可拆单位。

---

# 二百一十二、Step 5：按 Group 分 Train / Val / Test

例如目标：

```text
80 / 10 / 10
```

只是：

> 近似目标。

---

# 二百一十三、Step 6：检查分布

至少检查：

```text
Risk Type
Positive / Negative
Region
Year
Project Type
Document Type
Difficulty
Case Type
```

---

# 二百一十四、Step 7：做 Cross-split Similarity Audit

即使 Group 已切好，

仍然再检查：

> Train 和 Test 是否有异常相似文本。

---

# 二百一十五、比如随机抽：

```text
每个Test Clause
```

去 Train：

> 找最相似邻居。

---

# 二百一十六、如果发现：

```text
Similarity = 0.998
```

就值得调查。

---

# 二百一十七、这个步骤非常强。

因为它能发现：

> 前面 Dedup 没抓到的泄漏。

---

# 二百一十八、我们可以保存：

```text
nearest_train_similarity
```

---

# 二百一十九、例如：

```json
{
  "test_clause_id": "C-991",
  "nearest_train_clause_id": "C-117",
  "similarity": 0.997
}
```

---

# 二百二十、然后人工检查：

> 是不是泄漏？

---

# 二百二十一、这就是：

# Leakage Audit

---

# 二百二十二、Step 8：冻结 Test

生成：

```text
split_version = split_v0.1
```

---

# 二百二十三、以后再训练：

> 不随意重新洗牌。

---

# 二百二十四、为什么不能每次训练都重新 Random Split？

因为模型 A：

> 用 Split A。

模型 B：

> 用 Split B。

最后两个分数：

> 不能公平比较。

---

# 二百二十五、所以：

# Benchmark Split 必须版本化

---

# 二百二十六、例如：

```text
ProcurementSplit_v0.1
```

以后模型全部：

> 用同一 Test。

---

# 二百二十七、如果数据规模大幅变化，

可以建立：

```text
v0.2
```

但不能：

> 偷偷改。

---

# 二百二十八、否则你会发现：

```text
Model A = 84%
Model B = 87%
```

实际上：

> 考卷不同。

---

# 二百二十九、这根本不能比较。

---

# 二百三十、所以每个实验记录：

```text
dataset_version
split_version
```

极其重要。

---

# 二百三十一、现在设计 `DatasetSplit_V0.1`

一条样本可以有：

```json
{
  "clause_id": "CLAUSE-00178",
  "project_id": "PROJECT-00152",

  "duplicate_group_id": null,
  "template_group_id": "TG-00017",
  "split_group_id": "SG-00091",

  "split": "train",

  "split_reason": "group_assignment",

  "split_version": "procurement_split_v0.1"
}
```

---

# 二百三十二、一个 Test 样本：

```json
{
  "clause_id": "CLAUSE-88102",
  "project_id": "PROJECT-09112",

  "template_group_id": "TG-00772",
  "split_group_id": "SG-03188",

  "split": "test",

  "template_seen_in_train": false,

  "split_version": "procurement_split_v0.1"
}
```

---

# 二百三十三、甚至可以加：

```text
time_bucket
region
project_category
```

帮助后面 Slice。

---

# 二百三十四、现在看一个非常实用的数据表

最终 Split Summary 可以自动生成：

| Metric | Train | Validation | Test |
|---|---:|---:|---:|
| Projects | 8,000 | 1,000 | 1,000 |
| Clauses | 320,000 | 39,000 | 41,000 |
| Positive Risk | 31% | 30% | 32% |
| Hard Negative | 7% | 8% | 8% |
| Unique Templates | 1,420 | 182 | 201 |
| Regions | 28 | 27 | 28 |

---

# 二百三十五、注意这里：

> 项目数和 Clause 数都要看。

---

# 二百三十六、因为有的 Project：

```text
10条Clause
```

有的：

```text
1000条Clause
```

---

# 二百三十七、如果只按 Project 数量：

```text
80 / 10 / 10
```

Clause 数量可能变成：

```text
60 / 20 / 20
```

---

# 二百三十八、所以 Split 是多目标平衡：

```text
Project数量
Clause数量
Label分布
Risk Type
Time
Region
Template
```

---

# 二百三十九、这就是为什么现实 Split：

> 比 `train_test_split()` 难很多。

---

# 二百四十、但是第一版不要追求数学完美。

只要做到：

```text
Group不泄漏
关键类别不过度失衡
Test具有足够覆盖
```

就已经：

> 非常专业。

---

# 二百四十一、现在看极端 Group Size

假设一个超级项目：

```text
Project Mega
```

有：

```text
50,000条Clause
```

---

# 二百四十二、而普通项目平均：

```text
100条
```

---

# 二百四十三、如果 Mega Project 被分到 Test，

整个 Test：

> 一半都被它占了。

---

# 二百四十四、怎么办？

不能把它随便拆掉。

因为：

> Group Integrity。

---

# 二百四十五、可以考虑：

```text
特殊大Group单独处理
```

例如：

> 不进入主 Benchmark，

单独成为：

# Stress Test

---

# 二百四十六、或者：

> 设计项目级采样。

---

# 二百四十七、这再次说明：

> 不要让一个异常项目支配整个指标。

---

# 二百四十八、类似还有：

# Very Large Template Group

一个模板覆盖：

```text
20,000个项目
```

---

# 二百四十九、如果严格不跨 Split，

可能：

> 整个数据集都难切。

---

# 二百五十、这时就要重新问：

> 我们是想测试“新项目”，还是“新模板”？

---

# 二百五十一、如果生产环境会继续使用这个主流模板，

可以允许：

> 同模板不同 Project 跨 Split。

但需要：

> 明确标记。

---

# 二百五十二、然后同时建立：

```text
Unseen-template Slice
```

专门测陌生模板。

---

# 二百五十三、这比强行：

> 所有 Template 永不跨 Split

更现实。

---

# 二百五十四、所以 Group Constraint 有两类：

# Hard Constraint

绝不能跨。

---

# 二百五十五、例如：

```text
同一个Project
Exact Duplicate Group
同一个Annotation Instance
```

通常：

> Hard。

---

# 二百五十六、第二类：

# Soft Constraint

最好隔离，

但根据评测目标：

> 可以允许。

例如：

```text
Template Group
Agency
Region
```

---

# 二百五十七、这张区别非常重要。

---

# 二百五十八、可以设计：

```text
Hard Leakage Groups:
Project
Exact Duplicate

Soft Generalization Groups:
Template
Agency
Region
```

---

# 二百五十九、Hard Group：

> 用于保证评测合法。

Soft Group：

> 用于定义评测难度。

---

# 二百六十、这是一个非常漂亮的框架。

---

# 二百六十一、例如主 Benchmark：

```text
Project-disjoint
Duplicate-disjoint
```

保证：

> 基本独立。

---

# 二百六十二、然后标记：

```text
Template Seen
Template Unseen
Region Seen
Region Unseen
```

用于：

> Slice Analysis。

---

# 二百六十三、这就避免把所有目标：

> 强行塞进一个 Split 规则。

---

# 二百六十四、现在进入另一个问题

# Time Leakage

假设你做 Temporal Split：

```text
2025以前 → Train
2026 → Test
```

看起来很严谨。

---

# 二百六十五、但你使用了一个：

```text
2026年12月生成的专家整理文档
```

它总结了：

> 2026 年全年案例。

然后把这份材料：

> 放进 Train。

---

# 二百六十六、虽然 Clause 时间是过去，

但知识来源：

> 包含未来。

这还是：

# Temporal Leakage

---

# 二百六十七、所以时间切分不能只看：

```text
project_date
```

还要考虑：

> 数据来源生成时间。

---

# 二百六十八、例如：

```text
annotation_date
knowledge_snapshot_date
```

都可能重要。

---

# 二百六十九、这将在第七阶段专门展开。

---

# 二百七十、现在看 Synthetic Data

以后模型会生成：

> 合成训练样本。

如果 Synthetic Sample 是从：

> Test Case 改写出来的。

---

# 二百七十一、即使字完全不同，

也可能：

> 把 Test 答案泄漏进 Train。

---

# 二百七十二、所以未来 Synthetic Data 也必须知道：

```text
source_sample_id
```

---

# 二百七十三、如果来源：

> 属于 Test，

它的派生数据：

> 不能进入 Train。

---

# 二百七十四、这叫：

# Lineage-aware Split

根据血缘切分。

---

# 二百七十五、非常重要。

我们前面一直保存：

# Data Lineage

现在再次产生巨大价值。

---

# 二百七十六、如果 Sample A：

> 派生出 Sample B、C、D。

那么：

```text
A → Test
```

B/C/D：

> 也应该跟着 Test 或被排除。

---

# 二百七十七、不能：

```text
A → Test
B → Train
```

然后说：

> 文本不一样，所以没事。

---

# 二百七十八、所以除了 Group Relation，

还有：

# Derivation Relation

---

# 二百七十九、最终 Split Graph 可能包括：

```text
Same Project
Exact Duplicate
Derived From
Same Original Case
```

这些都是：

> Hard Edges。

---

# 二百八十、可以画成：

```text
Sample A
├── duplicate → Sample B
├── derived   → Sample C
└── same_case → Sample D
```

A/B/C/D：

> 必须一起 Split。

---

# 二百八十一、这个思想非常强。

---

# 二百八十二、现在看一个很现实的 SFT 数据问题。

原始专家案例：

```text
Clause A
+
Expert Rationale A
```

---

# 二百八十三、我们让 LLM 产生：

```text
Paraphrase 1
Paraphrase 2
Paraphrase 3
```

作为数据增强。

---

# 二百八十四、如果原始 A：

> 在 Test。

Paraphrase：

> 进入 Train。

---

# 二百八十五、测试几乎必然虚高。

---

# 二百八十六、所以：

# Augmentation must inherit split

数据增强应该：

> 继承母样本 Split。

---

# 二百八十七、这句话以后做 SFT 时：

> 非常重要。

---

# 二百八十八、现在看 RAG Knowledge Corpus 和 Task Split 的关系。

假设我们评测：

> 法规风险审查。

Test Case 需要用某条法律。

RAG Knowledge Base：

> 包含这条法律。

是不是泄漏？

---

# 二百八十九、不是。

因为生产系统本来：

> 就应该允许查法规。

---

# 二百九十、这叫：

# Allowed External Knowledge

---

# 二百九十一、但是如果 RAG 知识库里：

> 直接存了 Test Case 的专家答案，

那就：

> 泄漏。

---

# 二百九十二、所以评测时必须定义：

```text
Allowed Knowledge
```

和：

```text
Forbidden Test-specific Knowledge
```

---

# 二百九十三、这会在第八课评测系统里正式解决。

现在先有意识。

---

# 二百九十四、现在做一个非常典型的 Split 失败案例。

数据：

```text
10,000个项目
400,000条Clause
```

随机按 Clause：

```text
320k Train
40k Val
40k Test
```

---

# 二百九十五、模型 Test Accuracy：

```text
94%
```

---

# 二百九十六、改成 Project-disjoint：

```text
86%
```

---

# 二百九十七、再改成 Unseen-template：

```text
74%
```

---

# 二百九十八、哪个分数是真的？

三个都可能是真的。

---

# 二百九十九、它们回答了三个不同问题。

94%：

> 看过同项目大量兄弟 Clause 后的能力。

---

# 三百、

86%：

> 面对新项目，但模板可能熟悉。

---

# 三百零一、

74%：

> 面对新项目 + 新模板。

---

# 三百零二、所以：

# Metric without Split Definition is almost meaningless

没有 Split 定义的分数：

> 几乎没有解释力。

---

# 三百零三、以后看到别人说：

> “我们的采购模型准确率 95%。”

你第一反应应该问：

```text
怎么切的？
```

---

# 三百零四、甚至比问：

```text
用什么模型？
```

更重要。

---

# 三百零五、因为一个错误 Split：

> 可以让普通模型看起来像超级模型。

---

# 三百零六、这就是 Dataset Engineering 对 AI 项目的影响。

---

# 三百零七、现在建立 `Split Manifest`

每次 Split 最好保存：

```text
split_version
random_seed
grouping_policy
date_boundary
hard_constraints
soft_constraints
created_at
dataset_version
```

---

# 三百零八、例如：

```json
{
  "split_version": "procurement_split_v0.1",
  "dataset_version": "procurement_dataset_v0.1",

  "strategy": "project_group_holdout",

  "hard_constraints": [
    "same_project_same_split",
    "exact_duplicate_same_split",
    "derived_sample_same_split"
  ],

  "soft_constraints": [
    "template_balance",
    "region_balance"
  ],

  "target_ratio": {
    "train": 0.8,
    "validation": 0.1,
    "test": 0.1
  },

  "random_seed": 20260915
}
```

这里的数字只是：

> 教学示例。

---

# 三百零九、为什么保存 Seed？

因为如果是可随机重现的 Split，

以后：

> 能重新生成。

---

# 三百一十、但仅保存 Seed 还不够。

还要保存：

```text
算法版本
排序方式
输入数据版本
```

---

# 三百一十一、否则同一个 Seed，

Dataset 变了以后：

> Split 也会变。

---

# 三百一十二、所以最稳妥还应该直接保存：

# Split Assignment Table

---

# 三百一十三、例如：

| project_id | split_group_id | split |
|---|---|---|
| P001 | SG001 | train |
| P002 | SG002 | train |
| P003 | SG003 | validation |
| P004 | SG004 | test |

---

# 三百一十四、这个表：

> 就是最终真相。

---

# 三百一十五、以后新增数据怎么办？

这是非常现实的问题。

---

# 三百一十六、假设今天有：

```text
Dataset v0.1
```

半年后新增：

```text
20万条
```

是不是重新把所有数据：

> 洗牌？

---

# 三百一十七、不建议随便这么做。

因为旧 Benchmark：

> 会失去连续性。

---

# 三百一十八、一个常见思路是：

旧 Test：

> 保持冻结。

新增项目：

> 进入 Train/Val，或者构建新的 Test v0.2。

---

# 三百一十九、例如：

```text
Test_v1
=
长期稳定回归集
```

---

# 三百二十、

```text
Test_v2
=
加入最新时间窗口
```

---

# 三百二十一、这样可以同时知道：

> 对历史稳定 Benchmark 有没有退化。

以及：

> 对新数据表现如何。

---

# 三百二十二、这就是：

# Benchmark Versioning

---

# 三百二十三、以后第八课会正式展开。

---

# 三百二十四、现在看看 Validation 是否也要冻结。

通常：

> 可以比 Test 灵活。

---

# 三百二十五、因为 Validation：

> 本来就用于开发。

随着任务变化：

> 可以增加新的 Validation Slice。

---

# 三百二十六、但为了实验公平，

某一轮模型比较：

> 仍然应该使用固定 Validation Version。

---

# 三百二十七、否则今天：

Model A 在 Val A。

明天：

Model B 在 Val B。

你又无法：

> 公平比较。

---

# 三百二十八、所以任何有分数的东西，

都应该知道：

```text
Dataset Version
Split Version
Benchmark Version
```

---

# 三百二十九、现在把第六阶段工程架构压缩成一张图

```text
                 DedupedClauseSet_V0.1
                          │
                          ▼
                    Build Hard Groups
             ┌────────────┼─────────────┐
             ▼            ▼             ▼
          Project      Duplicate      Lineage
             │            │             │
             └────────────┼─────────────┘
                          ▼
                    split_group_id
                          │
                          ▼
                   Group-aware Split
             ┌────────────┼─────────────┐
             ▼            ▼             ▼
           Train       Validation       Test
             │            │             │
             └────────────┼─────────────┘
                          ▼
                 Distribution Audit
                          │
                          ▼
                  Similarity Leakage Audit
                          │
                          ▼
                    Freeze Test
                          │
                          ▼
                  DatasetSplit_V0.1
```

---

# 三百三十、本阶段最容易犯的 12 个错误

### 错误 1

> 直接按 Clause 行随机 8:1:1。

对于采购数据：

> 很危险。

### 错误 2

> 同一个项目里的不同 Clause 可以随便分到 Train/Test。

容易产生 Project Leakage。

### 错误 3

> Document 不同，所以一定独立。

不一定。

可能同项目、同模板、同版本链。

### 错误 4

> Exact Duplicate 去掉以后就不会泄漏。

错。

还有 Near Duplicate 和 Template Leakage。

### 错误 5

> 比例必须严格 80/10/10。

错。

独立性和评测覆盖更重要。

### 错误 6

> 为了类别比例漂亮，可以拆 Project。

通常不值得。

### 错误 7

> Validation 泄漏没关系，只有 Test 需要干净。

错。

Validation 会影响模型选择。

### 错误 8

> Test 可以每天反复跑、反复看、反复调。

会逐渐污染 Test。

### 错误 9

> Temporal Split 只需要看项目发布日期。

不一定。

还要注意知识和标注来源的时间。

### 错误 10

> Synthetic Data 字不同，所以不会泄漏。

错。

需要看 Lineage。

### 错误 11

> 同一法规知识出现在 Train/Test 就一定是泄漏。

不一定。

共享公共知识和共享测试答案不是一回事。

### 错误 12

> 一个总 Accuracy 就足够评价 Split。

错。

必须看关键 Slice 和 Split 定义。

---

# 三百三十一、本阶段最重要的 6 个“≠”

```text
Row Split
≠
Independent Split
```

```text
Different Document
≠
Independent Project
```

```text
Different Project
≠
Different Template
```

```text
No Exact Duplicate
≠
No Leakage
```

```text
Fixed Ratio
≠
Good Benchmark
```

```text
Never Used for Gradient
≠
Never Influenced Development
```

最后一句描述的就是：

> Validation 和频繁查看的 Test。

---

# 三百三十二、再记住一个最重要的“=”

\[
\boxed{
GoodSplit
=
Independence
+
Representativeness
+
LeakageControl
+
Reproducibility
}
\]

翻译成人话：

> **好的数据切分不是把行数按比例切开，而是让 Train、Validation、Test 尽量来自彼此独立的信息群，同时保持业务代表性、控制重复和模板泄漏，并且整个切分过程可以复现和审计。**

---

# 三百三十三、Stage 1～6 现在已经形成一条完整的数据流水线

```text
Stage 1
Task Schema
“什么是一条样本？”
        │
        ▼
Stage 2
ParsedDocument
“原文件里到底有什么？”
        │
        ▼
Stage 3
ClauseUnit
“文字属于哪条业务要求？”
        │
        ▼
Stage 4
CleanClause
“怎样安全规范表示？”
        │
        ▼
Stage 5
DedupedClauseSet
“到底有多少独立信息？”
        │
        ▼
Stage 6
DatasetSplit
“哪些数据可以教模型，
哪些数据必须留着考试？”
```

现在我们第一次拥有：

> 真正意义上的 Train / Validation / Test。

---

# 三百三十四、但是还有一个坏消息

即使我们做到：

```text
Project-disjoint
Duplicate-disjoint
Lineage-disjoint
```

是不是就能保证：

> Test 一定干净？

还不能。

---

# 三百三十五、因为数据泄漏比“切错行”狡猾得多。

例如：

```text
Test里的专家答案
```

可能曾经出现在：

> 一个 Excel 说明文件里。

---

# 三百三十六、或者：

Test 项目的风险审查结论，

已经被整理进：

> 一篇培训材料。

---

# 三百三十七、或者：

同一案例被：

> LLM 改写成另一种语言，

然后进了 Train。

---

# 三百三十八、或者更隐蔽：

我们使用 Test Set 调 Prompt：

> 调了 200 次。

---

# 三百三十九、甚至：

未来 SFT 数据由当前模型错误生成，

而这些错误案例本来来自：

> Test。

---

# 三百四十、这时候即使：

```text
project_id
```

完全不重叠，

Benchmark：

> 仍然可能被污染。

---

# 三百四十一、本阶段掌握测试

如果现在不看前文，你能完整解释下面这些问题，第 6 阶段就真正掌握了：

> Train、Validation、Test 的真正角色分别是什么？

> 为什么 Train = Learn、Validation = Select、Test = Estimate？

> 为什么比例不是 Split 最重要的东西？

> 为什么 ProcurementAI 不应该默认按 Clause 行随机切？

> 为什么同一项目中的不同 Clause 会造成 Project Leakage？

> 为什么 `project_id` 从 Schema 第一阶段就非常重要？

> 为什么按 Document Split 仍然可能泄漏？

> 什么是 Group-aware Split？

> 什么叫 Split Unit？

> Duplicate Group 为什么绝对不能跨 Train/Test？

> Template Group 为什么也可能造成泄漏？

> 什么叫 Leakage Graph？

> 什么是 Connected Component / Split Group？

> 为什么真正 Split 的应该是“独立信息群”？

> 为什么 Group Integrity 通常优先于完美类别比例？

> 什么叫 Group-aware Stratification？

> 为什么 Test Set 不能只看行数？

> 为什么 Test Diversity 很重要？

> 为什么关键 Risk Slice 必须有足够样本？

> 什么是 Temporal Split？

> 为什么 Temporal Split 更接近真实部署？

> Project Holdout、Temporal Holdout、Geographic Holdout 分别在测什么？

> 为什么 Test Set 必须围绕“泛化问题”设计？

> 为什么成熟系统可能同时拥有 IID Test、Future Test、Hard Test？

> Validation 为什么也必须控制泄漏？

> 为什么 Group K-fold 比普通 K-fold 更适合小规模采购项目数据？

> 什么叫 Test Set Peeking？

> 为什么反复查看 Test 并调模型会污染 Test？

> Seen-template 与 Unseen-template 为什么应该分开评测？

> 为什么共享法规知识不一定构成泄漏？

> Shared Knowledge 和 Shared Answer Instance 有什么区别？

> Label Leakage 和 Split Leakage 有什么区别？

> 什么是 Template Leakage？

> 为什么 Synthetic Data 必须继承母样本 Split？

> 什么叫 Lineage-aware Split？

> 为什么数据增强不能从 Test 派生以后放进 Train？

> 什么是 Hard Split Constraint？

> 什么是 Soft Generalization Constraint？

> Project、Exact Duplicate 为什么更接近 Hard Constraint？

> Template、Agency、Region 为什么可以作为 Soft Constraint 或评测 Slice？

> 为什么同一个 Benchmark 必须固定 `split_version`？

> 为什么不同模型若使用不同 Test Split，分数不能直接比较？

> 为什么必须保存 Split Assignment Table？

> 新数据加入以后为什么不应该随便重洗旧 Test？

> 为什么一个“95%准确率”如果没有 Split 定义几乎没有解释力？

如果这些你都能自己讲清楚：

\[
\boxed{
第四课第6阶段真正掌握
}
\]

---

# 三百四十二、本阶段最终只记一句话

> **政府采购数据的 Train / Validation / Test 不能只按行随机切，而应该围绕“独立信息群”切分：同项目、重复样本和派生样本必须严格隔离，模板、时间、地区等维度则用来定义模型真正要面对的泛化难度；一个好的 Test Set 不是数据剩下的 10%，而是一套被严格保护、真正代表未来未知项目的考试。**

最后压成一张图：

```text
                  Procurement Data
                         │
                         ▼
                    Clause Rows
                         │
                         ▼
                ┌────────────────┐
                │ Leakage Links  │
                │                │
                │ Same Project   │
                │ Duplicate      │
                │ Derived From   │
                └───────┬────────┘
                        │
                        ▼
                  Split Groups
                        │
              ┌─────────┼─────────┐
              ▼         ▼         ▼
            Train      Val       Test
              │         │         │
           学参数     选方案     最后考
              │         │         │
              └─────────┼─────────┘
                        ▼
               Distribution Audit
                        │
                        ▼
                Cross-split Audit
                        │
                        ▼
                  Frozen Test
                        │
                        ▼
                DatasetSplit_V0.1
```

---

# 下一阶段：第四课 · 第 7 阶段
## 数据泄漏与 Benchmark 污染——为什么 Train 和 Test 明明已经按 Project 完全分开，模型仍然可能“提前看过答案”？

第 7 阶段我们会专门处理一个比随机切分更隐蔽的问题：

# Data Leakage

我们会把泄漏分成：

```text
Label Leakage
Project Leakage
Duplicate Leakage
Template Leakage
Temporal Leakage
Lineage Leakage
Answer Leakage
Benchmark Contamination
Human-in-the-loop Leakage
```

尤其会拆一个非常容易被忽视的问题：

> **当你根据 Test 的错误不断改 Prompt、改规则、补训练数据时，Test 是怎么一点一点被“训练进去”的？**

还会第一次建立：

```text
Leakage Audit Checklist
```

以及：

```text
Benchmark Firewall
```

最终产出第一版：

# `LeakageAudit_V0.1`

到那一步，第四课的数据才开始从“形式上分开”，进入真正意义上的：

> **可信评测数据。**

---
