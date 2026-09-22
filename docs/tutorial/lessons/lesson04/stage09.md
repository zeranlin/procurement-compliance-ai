# 第四课 · 第 9 阶段
# 专家标注、双人复核与一致性
## 为什么两个真正懂政府采购的专家，也可能给同一个 Clause 完全不同的 Label？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **“这个专家很厉害，所以他说什么就是什么。”**
2. **明确规则 + 独立标注 + 分歧检测 + 专家裁决 + 可追溯记录。**
3. **“删掉这条，太麻烦了。”**
4. **为什么他们会不一致？**
5. **专家分歧常常是在帮助我们找到 Dataset 最重要的边界。**
6. **Label定义不清 上下文不足 风险类别边界重叠 标注指南没覆盖这种情况 案例本身就是Hard Case 法规依据存在解释空间**
7. **使用自己的经验规则；**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `ANN` | ANN/近似最近邻：在大规模向量中快速寻找相似项 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `Adjudication` | 专家裁决：对分歧样本形成最终 Gold 结论 |
| `Annotation Guideline` | 标注规范：统一专家如何理解字段、边界和例外 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `Calibration` | 校准：使模型置信度更接近实际正确率 |
| `Sample` | 样本：具有明确输入、目标和来源的一条训练/评测记录 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `Dataset` | 数据集：按统一 Schema、版本和质量标准组织的样本集合 |
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |
| `Observe` | Observe/观察：读取当前状态和工具结果 |

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

第 8 阶段我们已经解决：

> **专家到底应该标什么？**

我们建立了：

```text
risk_present
primary_risk_type
risk_subtype
risk_level
needs_review
rationale
evidence
suggested_action
```

也就是：

# `AnnotationSchema_V0.1`

但现在出现一个更棘手的问题。

假设有这样一条采购要求：

> “供应商近三年应具有不少于 5 个类似项目业绩。”

我们把完全相同的 Clause 分别交给三位专家。

专家 A：

```text
risk_present = true
risk_type = supplier_qualification
```

专家 B：

```text
risk_present = uncertain
needs_review = true
```

专家 C：

```text
risk_present = false
```

三个人都不是乱点。

甚至三个人都可能有很多年采购业务经验。

那到底发生了什么？

问题很可能并不是：

> “谁不专业？”

而是：

> **三个人脑子里使用的判断规则并不完全相同。**

这就是第 9 阶段真正要解决的问题。

---

# 一、本阶段只解决一个核心问题

> **怎样把多个专家个人脑子里的经验，变成一套可重复、可衡量、可复核、可持续改进的团队标注标准，并最终产出真正可以称为 Gold 的数据？**

今天最终要得到两个东西：

# `AnnotationGuideline_V0.1`

即：

> **专家标注指南 V0.1**

以及：

# `AdjudicatedGoldSet_V0.1`

即：

> **经过分歧裁决后的 Gold 数据集 V0.1**

先把整个阶段的路线看完。

```text
Annotation Schema
标注字段已经定义
        │
        ▼
Annotation Guideline
把每个Label写成统一判断规则
        │
        ▼
Pilot Annotation
小批量试标，先发现规则问题
        │
        ▼
Blind Double Annotation
两位专家独立、互不看答案地标
        │
        ▼
Agreement Measurement
测量两位专家到底有多一致
        │
        ▼
Disagreement Analysis
分析为什么不一致
        │
        ▼
Adjudication
第三位/高级专家进行裁决
        │
        ▼
Guideline Revision
把裁决形成的新规则写回指南
        │
        ▼
Adjudicated Gold Set
形成可用于Benchmark的高质量Gold数据
```

一句话理解：

> **不是“找专家来标”，而是建立一条专家知识生产流水线。**

---

# 二、今天最重要的 5 个核心心智模型

这 5 个请当成第 9 阶段的骨架。

## 心智模型 1：Gold ≠ 某一个专家说了算

\[
\boxed{
Gold
\neq
SingleExpertOpinion
}
\]

Gold 不是：

> “这个专家很厉害，所以他说什么就是什么。”

Gold 更接近：

> **明确规则 + 独立标注 + 分歧检测 + 专家裁决 + 可追溯记录。**

一个资深专家仍然可能：

- 忽略上下文；
- 使用自己的经验规则；
- 前后尺度漂移；
- 疲劳；
- 对模糊边界有个人偏好。

所以专业数据系统不能把：

> 专家权威

替代：

> 数据质量流程。

---

## 心智模型 2：专家分歧不是垃圾，而是最值钱的信号之一

\[
\boxed{
Disagreement
=
Information
}
\]

如果两位专家对同一条 Clause 不一致，我们第一反应不应该是：

> “删掉这条，太麻烦了。”

而应该问：

> **为什么他们会不一致？**

因为分歧可能在告诉我们：

```text
Label定义不清
上下文不足
风险类别边界重叠
标注指南没覆盖这种情况
案例本身就是Hard Case
法规依据存在解释空间
```

所以：

> **专家分歧常常是在帮助我们找到 Dataset 最重要的边界。**

---

## 心智模型 3：先独立判断，再讨论

这个流程叫：

# Blind Annotation
## 盲标 / 独立标注

意思是：

> 专家 A 在提交答案之前，看不到专家 B 的答案。

为什么？

因为如果专家 A 先看到：

```text
专家B：High Risk
```

A 很容易受到影响。

这叫：

# Anchoring
## 锚定效应

尤其是高级专家意见，会让其他标注员下意识靠拢。

所以真正测专家是否一致：

> 必须先让他们独立回答。

---

## 心智模型 4：一致率不是为了给专家打分，而是为了给 Schema 体检

\[
\boxed{
AgreementMetric
\rightarrow
SchemaDiagnostic
}
\]

如果两位专家一致率只有 55%，不要立刻说：

> “专家水平不行。”

可能真正的问题是：

> **这个 Label 根本没有定义清楚。**

比如 `high risk` 如果指南只写：

> “风险较大的情况标 High。”

那 55% 一致率一点都不奇怪。

因此一致性指标首先是在问：

> **我们的标注规则是否足够清楚，能让专业人员重复得到相似结果？**

---

## 心智模型 5：裁决的真正产物，不只是最终 Label

# Adjudication
## 分歧裁决

很多团队把裁决理解成：

```text
A说Risk
B说No Risk
高级专家选Risk
结束
```

这是浪费。

真正高价值的是：

```text
为什么A这么判断？
为什么B这么判断？
最终为什么选这个？
以后遇到同类案例怎么统一？
```

然后把最后一条写回：

# Annotation Guideline

因此：

\[
\boxed{
Adjudication
\rightarrow
BetterGuideline
\rightarrow
BetterFutureLabels
}
\]

这才是闭环。

---

# 三、Annotation Guideline 到底是什么？

我们上一阶段已经有：

# Annotation Schema
## 标注结构

例如：

```text
risk_present
risk_type
needs_review
risk_level
```

但 Schema 只告诉专家：

> “要填哪些格子。”

它没有完整告诉专家：

> “什么情况下应该填哪个值。”

这就需要：

# Annotation Guideline
## 标注指南

可以把两者想成：

```text
Schema
=
考试答题卡

Guideline
=
考试评分标准
```

只有答题卡，没有评分标准：

> 大家当然各填各的。

---

# 四、一个专业 Label Guide 至少要回答 5 类问题

我们拿：

```text
risk_present
```

举例。

如果指南只写：

```text
true = 有风险
false = 无风险
uncertain = 不确定
```

几乎等于没写。

专业指南应该告诉专家：

| 项目 | 要回答的问题 |
|---|---|
| 定义 | 这个 Label 到底代表什么？ |
| 纳入条件 | 什么情况应该选它？ |
| 排除条件 | 什么情况看起来像，但不要选？ |
| 边界案例 | 最容易混淆的情况是什么？ |
| 所需上下文 | 判断之前必须看到什么信息？ |

这五项非常重要。

---

# 五、例如 `risk_present = true`

教学版定义可以写成：

> 根据当前可获得的采购条款、必要上下文和适用依据，存在较明确的风险信号，足以进入风险处理流程；但该 Label 本身不代表最终法律裁决。

注意：

> `Potential Risk`

和：

> `Final Illegal`

不是一回事。

---

# 六、那 `false` 呢？

不是：

> “我暂时没看出来，所以 False。”

而更应该是：

> **在必要上下文相对充分的情况下，按照当前标注规则，没有发现达到风险标记阈值的明显风险信号。**

关键词是：

# 上下文相对充分

---

# 七、那 `uncertain` 呢？

可以定义：

> **当前信息不足、规则适用存在明显不确定性，或者不同合理解释可能产生不同结论，不适合强制归入 true / false。**

于是：

```text
uncertain
```

不是失败。

它是在表达：

> **专业不确定性。**

---

# 八、一个非常典型的政府采购边界案例

条款：

> “供应商应保证故障发生后 2 小时内到达项目现场。”

专家 A：

> “2 小时现场响应，对外地供应商不利，Risk。”

专家 B：

> “这里只要求服务能力，并没有要求投标前就在本地设机构，No Risk。”

两个答案为什么不同？

因为 A 实际判断的是：

```text
响应时间是否形成事实性地域限制
```

B 判断的是：

```text
是否存在显性的本地机构准入条件
```

他们回答的：

> 其实不是完全同一个问题。

这时候真正需要修的，可能不是专家。

而是：

# Guideline

应该明确：

> “现场响应要求”和“预先设立本地机构”必须分别判断。

这就是专家分歧的价值。

---

# 九、正式标数据以前，千万不要一上来就标 10 万条

应该先做：

# Pilot Annotation
## 小规模试标

例如先抽：

```text
100～300条
```

教学示例。

重点不是数量。

而是：

> **让标注系统先撞墙。**

---

# 十、试标阶段专门找什么？

重点找：

```text
专家最容易争论的Label
Other特别多的地方
Unknown特别多的地方
同一句指南被不同人理解成不同意思的地方
上下文不足的地方
Subtype互相重叠的地方
```

如果发现 200 条里：

```text
60条都有严重争议
```

不要赶紧开 50 人标注大军。

应该先停下来：

> 修 Schema 和 Guideline。

---

# 十一、推荐的专业标注流程

从现在开始，你可以把政府采购专家标注流程记成：

```text
第一步
规则校准
Calibration

第二步
盲式双人独立标注
Blind Double Annotation

第三步
一致性测量
Agreement Measurement

第四步
分歧归因
Disagreement Analysis

第五步
专家裁决
Adjudication

第六步
规则回写
Guideline Revision

第七步
形成Gold
Gold Finalization
```

以后看到英文的时候，直接记中文：

> **校准 → 双盲标 → 测一致 → 找分歧 → 裁决 → 改规则 → 出 Gold**

这条链比英文名字重要得多。

---

# 十二、什么叫 Double Annotation？

# Double Annotation
## 双人标注

意思是：

> 同一条样本由两位专家分别独立标一次。

例如：

```text
Sample 001

专家 A：
risk_present = true
risk_type = A
needs_review = true

专家 B：
risk_present = uncertain
risk_type = A
needs_review = true
```

这里可以立刻看到：

```text
risk_type
一致

needs_review
一致

risk_present
不一致
```

这比只看：

> “整条一样/不一样”

专业很多。

---

# 十三、所以一致性必须“按字段测”

不要只算一个：

```text
Overall Agreement = 80%
```

应该分别看：

| 字段 | 一致性重点 |
|---|---|
| `risk_present` | 最核心 |
| `primary_risk_type` | 风险分类 |
| `risk_subtype` | 细粒度边界 |
| `risk_level` | 优先级标准是否稳定 |
| `needs_review` | 不确定性判断 |
| `evidence` | 证据选择是否稳定 |

这样你可能发现：

```text
risk_present       92%
risk_type          88%
needs_review       90%
risk_level         61%
risk_subtype       58%
```

这说明什么？

不是整个 Schema 都坏了。

而是：

> **Risk Level 和 Subtype 的定义明显还不够稳定。**

这才是可操作的信息。

---

# 十四、最简单的一致性指标：Percent Agreement

# Percent Agreement
## 直接一致率

公式很简单：

\[
Agreement
=
\frac{两人相同的样本数}
{总双标样本数}
\]

假设两位专家共同标了：

```text
100条
```

其中：

```text
86条risk_present一致
```

那么：

\[
Agreement=86\%
\]

非常直观。

---

# 十五、但 86% 一定很高吗？

不一定。

假设数据里：

```text
95%
都是No Risk
```

两位专家都懒得判断，全部点：

```text
No Risk
```

就能得到：

> 95% 一致。

但这并不说明他们真的很专业。

所以我们需要一个稍微聪明一点的指标。

---

# 十六、Cohen's Kappa 是什么？

# Cohen's Kappa
## Cohen κ 系数 / 扣除随机一致后的专家一致性

不用背数学推导。

只理解一个问题：

> **两个人的一致，有多少不是“碰巧选到同一个答案”？**

公式是：

\[
\kappa
=
\frac{p_o-p_e}
{1-p_e}
\]

其中：

\[
p_o
\]

表示：

> 实际观察到的一致率。

\[
p_e
\]

表示：

> 如果按两个人自己的 Label 分布随机选择，理论上能碰巧一致多少。

---

# 十七、生活类比

假设考试只有：

```text
A
B
```

但所有人 95% 时间都选 A。

那么两个人随便乱答：

> 也很容易一样。

Kappa 做的事情，就是：

> 把这种“因为类别极度不平衡造成的幸运一致”扣掉一些。

---

# 十八、一个直觉例子

假设：

```text
Observed Agreement
实际一致率
= 0.90
```

而由于 Label 分布，随机也可能得到：

```text
Expected Agreement
随机期望一致率
= 0.70
```

那么：

\[
\kappa
=
\frac{0.90-0.70}
{1-0.70}
=
0.67
\]

所以看起来：

> 90% 一致。

扣掉随机因素以后：

> Kappa 只有约 0.67。

---

# 十九、Kappa 到底多少才算合格？

这里特别容易陷入“背阈值”。

不要这样。

没有一个数字能脱离：

```text
任务难度
Label数量
类别不平衡
业务风险
专家数量
```

直接宣布：

> “0.8 就好，0.6 就垃圾。”

我们更应该看：

> **它是否足以支撑这个 Label 的用途？**

比如：

Gold Benchmark 的核心 `risk_present`：

> 要求应该比普通训练语料更高。

细粒度 Subtype：

> 可以允许低一些，然后继续迭代定义。

所以：

# Agreement 是诊断指标，不是宗教数字。

---

# 二十、自由文本 Rationale 怎么算一致？

这是个很现实的问题。

专家 A：

> “该条件可能限制外地供应商参与。”

专家 B：

> “该条款将供应商注册地作为准入条件，需要审查其必要性。”

文字完全不同。

但意思：

> 基本一致。

显然不能用：

```text
string equality
```

---

# 二十一、Rationale 更适合按“信息要素”评

例如拆成：

```text
Observed Fact
Risk Concern
Context Needed
Conclusion Scope
```

然后问：

> 两个专家是否抓住相同核心事实？

是否识别同一风险机制？

是否认为需要相似的上下文？

---

# 二十二、所以结构化 Rationale 再次发挥价值

如果自由文本只有一个大段：

> 很难比较专家是否一致。

如果拆成：

```text
observed_fact
risk_concern
context_needed
```

就可以分别判断。

这也再次说明：

> 第 8 阶段设计 Schema，不是多此一举。

---

# 二十三、专家出现分歧以后，不能只记录“不同”

应该做：

# Disagreement Taxonomy
## 分歧类型分类

这是非常专业的一步。

我们至少应该区分几种分歧。

---

# 二十四、第一种：Label Definition Disagreement
## 标签定义分歧

例如：

专家 A 认为：

> 本地响应要求属于资格风险。

专家 B 认为：

> 属于商务履约风险。

说明：

> Risk Type 边界定义不清。

---

# 二十五、第二种：Context Disagreement
## 上下文不足导致的分歧

A 看 Clause：

> 认为有风险。

B 认为：

> 必须先知道项目是否真的需要现场服务。

这说明：

> 输入给专家的 Context 不够。

---

# 二十六、第三种：Evidence Disagreement
## 证据解释分歧

两位专家：

> 对 Clause 本身理解差不多。

但是：

> 对适用依据或证据权重理解不同。

---

# 二十七、第四种：Severity Disagreement
## 风险等级分歧

两个人都认为：

> 有潜在风险。

但一个标：

```text
High
```

另一个：

```text
Medium
```

说明：

> `risk_level` 的工作定义需要加强。

---

# 二十八、第五种：Annotation Error
## 单纯标注错误

例如：

专家自己复核以后说：

> “这个我点错了。”

这当然存在。

但不能把所有分歧：

> 都归因于专家手滑。

---

# 二十九、第六种：True Boundary Case
## 真正边界案例

即使：

```text
指南清楚
上下文完整
专家都认真
```

合理专业人员：

> 仍然可能存在不同判断。

这种案例非常重要。

因为它告诉我们：

> **这个任务本来就不是完全确定性的。**

---

# 三十、这六种分歧的处理方法完全不同

比如：

```text
定义分歧
→ 改Guideline

上下文分歧
→ 补Context

证据分歧
→ 明确Evidence规则

等级分歧
→ 重写Severity标准

标注错误
→ 修正Label

真实边界案例
→ 保留uncertain / needs_review
```

所以：

> **分歧分析比“统计一致率”更重要。**

---

# 三十一、什么叫 Adjudication？

# Adjudication
## 专家裁决

当 A、B 不一致时，

由：

```text
高级专家
专家小组
领域负责人
```

根据统一规则：

> 做最终裁决。

但是正确的裁决过程不是：

> “老板说 A 对。”

应该记录：

```text
A为什么这么标
B为什么这么标
最终选什么
为什么
需要新增哪条指南
```

---

# 三十二、一个裁决记录可以长这样

```json
{
  "sample_id": "SAMPLE-00217",

  "annotator_a": {
    "risk_present": true
  },

  "annotator_b": {
    "risk_present": "uncertain"
  },

  "disagreement_type": "context_disagreement",

  "adjudicated_label": {
    "risk_present": "uncertain",
    "needs_review": true
  },

  "adjudication_reason": "现有上下文不足以判断该服务时限是否具有充分业务必要性。",

  "guideline_update": "遇到现场响应时间要求时，应区分履约能力要求与投标前本地机构要求。"
}
```

这才是一条真正有价值的裁决记录。

---

# 三十三、你会发现：最后那一行最值钱

```text
guideline_update
```

因为它让：

> 以后 1000 条同类数据不再重复争论。

所以高质量标注系统应该形成：

\[
\boxed{
OneDisagreement
\rightarrow
OneReusableRule
}
\]

理想情况下如此。

---

# 三十四、Annotation Guideline 应该越标越厚吗？

不一定越厚越好。

我们要的是：

> **越来越准确。**

如果一份 Guideline 最后有：

```text
900页
```

专家根本不会看。

真正有用的方式是：

# Decision Tree
## 决策树

---

# 三十五、比如地域条件可以做成一张判断树

```text
看到“本地 / 项目所在地 / 本市”
                │
                ▼
是否把所在地作为投标前准入条件？
        │
    ┌───┴───┐
    │       │
   是       否
    │       │
    ▼       ▼
进入资格   是否只是履约能力要求？
风险审查        │
           ┌────┴────┐
           │         │
          是         否
           │         │
           ▼         ▼
检查必要性      进入其他规则
和比例性
```

这种比十页散文：

> 好用得多。

---

# 三十六、所以从第 9 阶段开始，Annotation Guide 最好包含三种东西

这里是本回答唯一集中列出的结构清单：

1. **Definition（定义）**：这个 Label 到底是什么意思；
2. **Decision Rule（判断规则）**：遇到什么条件选什么；
3. **Positive Example（正例）**：典型应该标什么；
4. **Negative Example（反例）**：长得像但不要这么标；
5. **Boundary Example（边界例）**：什么情况下应 `uncertain / needs_review`；
6. **Evidence Requirement（证据要求）**：做判断前至少需要什么；
7. **Escalation Rule（升级规则）**：什么时候必须交给高级专家裁决。

这比“写一份长说明书”更专业。

---

# 三十七、为什么 Blind Double Annotation 特别适合 Gold Set？

因为 Gold Set 最终要拿来：

> 给模型考试。

如果 Gold 本身只是：

> 一个专家快速点出来的，

那 Test Score 再精确也没意义。

例如模型与某专家的一致率：

```text
92%
```

听起来很高。

但如果另一个专家和这个专家本身：

```text
只有65%
```

那我们应该先问：

> Gold 到底稳不稳？

---

# 三十八、这出现一个非常重要的关系

\[
\boxed{
ModelPerformance
不能脱离
HumanAgreement
解释
}
\]

如果人类专家自己都难以稳定判断，

模型达到一个上限以后：

> 继续追求 100% Accuracy 可能没有意义。

---

# 三十九、这不是说“人不一致，模型就不用做好”

而是说：

> **Benchmark 必须告诉我们哪些 Case 是高共识，哪些是低共识。**

于是以后可以有：

```text
consensus_level
```

例如：

```text
high_consensus
adjudicated
boundary_case
```

---

# 四十、这样评测模型时可以分别看

```text
High-consensus Accuracy
```

和：

```text
Boundary-case Accuracy
```

这两个数字：

> 含义完全不同。

---

# 四十一、举个简单例子

假设 Test 里 1000 条。

其中：

```text
800条
专家双标直接一致

200条
经过裁决
```

模型：

```text
高共识样本 94%

裁决样本 68%
```

这比只报：

```text
总准确率 88.8%
```

有用太多。

---

# 四十二、为什么？

因为你马上知道：

> 模型真正困难的是专家自己也容易争议的边界区。

而不是：

> 基础判断能力全面失效。

---

# 四十三、这会直接指导训练

以后可以专门增加：

# Hard Cases

也就是：

> 专家分歧高、模型也容易错的案例。

这正好会进入：

> 第 10 阶段 Hard Negative。

所以第四课的阶段不是孤立的。

---

# 四十四、专家一致率越高越好吗？

一般来说当然希望：

> 稳定。

但这里有一个坑。

假设为了提高一致率，我们规定：

> “所有不确定的都标 No Risk。”

专家一致率可能立刻：

> 变高。

---

# 四十五、但 Dataset 变好了吗？

没有。

我们只是：

> 把真实不确定性藏掉了。

所以真正目标不是：

# Maximum Agreement

而是：

# Valid Agreement

有效一致。

---

# 四十六、可以理解成

\[
\boxed{
GoodAgreement
=
Consistency
+
CorrectMeaning
}
\]

如果大家一致地错：

> 没价值。

---

# 四十七、因此 Gold 数据必须同时关心

```text
Reliability
可靠性：不同人能不能稳定复现

Validity
有效性：这个Label到底是不是在表达我们真正想测的东西
```

这两个词以后会经常遇到。

简单记：

> **Reliable = 稳不稳。**

> **Valid = 对不对题。**

---

# 四十八、一个极端例子

让所有专家按规则：

> “出现‘本市’就标 Risk。”

他们一致率可能：

```text
99%
```

Reliability：

> 极高。

但这显然不能代表真正的专业风险判断。

Validity：

> 很差。

---

# 四十九、所以 Annotation Quality 不能只看 Agreement

还要：

> 抽样专家审查、案例复盘、依据核验。

---

# 五十、正式大规模标注以前，还有一步很重要

# Calibration Session
## 专家校准会

什么意思？

先抽：

```text
20～50条代表性案例
```

大家分别判断。

然后集中讨论：

> 为什么不同？

---

# 五十一、Calibration 的目标不是

> 让所有人服从某一个人。

而是：

> 把隐含规则说出来。

例如专家 A 可能说：

> “我默认资格条件应该考虑项目规模。”

专家 B：

> “我只有看到明显限制时才标 Risk。”

---

# 五十二、原来两个人心里使用的是：

> 两个不同阈值。

这时候 Guideline 就应该明确：

> 我们的数据任务究竟采用哪个判断阈值。

---

# 五十三、所以 Calibration 做的是

# Mental Model Alignment
## 专家心智模型对齐

这几个字特别重要。

最终我们不只是：

> 对齐按钮。

而是：

> 对齐判断方式。

---

# 五十四、推荐的 Gold 标注组织结构

可以分成三层角色。

```text
Annotator
标注专家

Reviewer
复核专家

Adjudicator
裁决专家
```

---

# 五十五、Annotator 的职责

根据 Guide：

> 独立判断。

不要猜：

> “裁决专家喜欢什么答案。”

---

# 五十六、Reviewer 的职责

检查：

```text
Label
Rationale
Evidence
Schema逻辑
```

是否符合标准。

---

# 五十七、Adjudicator 的职责

处理：

> 真正分歧和规则边界。

同时负责：

> 更新 Guideline。

---

# 五十八、注意一个很重要的治理原则

最好不要：

> 每一条数据都让最贵的高级专家从头标。

这非常浪费。

合理的方式是：

```text
普通明确案例
→ 双人标准标注

存在分歧
→ 高级专家裁决

复杂高价值Gold
→ 加强审核
```

这叫：

# Escalation
## 分级升级处理

---

# 五十九、这样成本才能控制

假设：

100,000 条数据。

如果每条都需要：

> 首席采购专家 10 分钟，

项目基本不可持续。

---

# 六十、而如果：

```text
80%
双标直接一致

15%
需要普通复核

5%
进入高级专家裁决
```

整体成本：

> 就现实得多。

这些比例只是教学示例，不是固定标准。

---

# 六十一、现在谈一个很重要的数据字段

# disagreement_type

为什么值得保存？

因为半年以后可以统计：

```text
40%的分歧来自risk_level
30%的分歧来自context不足
20%的分歧来自Subtype边界
10%的分歧来自操作错误
```

那下一版数据工程优先级就非常清楚。

---

# 六十二、如果没有保存分歧原因

你只知道：

> “专家有 18% 不一致。”

然后：

> 不知道该修哪里。

---

# 六十三、所以专家分歧本身也应该成为 Dataset Metadata

例如：

```json
{
  "double_annotated": true,
  "initial_agreement": false,
  "disagreement_type": "context_insufficient",
  "adjudication_required": true
}
```

---

# 六十四、现在设计 Gold 状态

我们上一阶段有：

```text
draft
reviewed
adjudicated
gold
```

现在可以真正理解它们。

```text
draft
=
单人初标

reviewed
=
经过第二人检查

adjudicated
=
曾有分歧，已经裁决

gold
=
达到当前Gold发布标准
```

---

# 六十五、注意

```text
adjudicated
```

和：

```text
gold
```

仍然不完全一样。

一条样本可能经过裁决，

但发现：

> 原始 PDF OCR 不可靠。

那么：

> 仍然不应该进 Gold Benchmark。

因为 Gold 需要：

```text
Parse可信
Structure可信
Normalization可信
Split可信
Leakage可信
Annotation可信
```

---

# 六十六、到这里，第四课前面的东西终于全部合流

真正的 Gold Sample 可能要求：

```text
parse_status = verified
structure_status = verified
normalization_status = verified
dedup_status = verified
split_status = valid
leakage_status = passed
annotation_status = gold
```

这才叫：

# End-to-End Gold

不是：

> “Label 看过了就叫 Gold。”

---

# 六十七、这是这一课非常重要的专业化升级

\[
\boxed{
GoldQuality
=
WholePipelineQuality
}
\]

---

# 六十八、现在设计 `AnnotationGuideline_V0.1`

它不是一篇长文章。

可以组织成：

```text
Task Definition
任务到底在判断什么

Label Definitions
每个标签正式定义

Decision Trees
常见场景判断流程

Positive Examples
正例

Negative Examples
反例

Boundary Cases
边界例

Required Context
需要查看的上下文

Evidence Rules
证据规则

Escalation Rules
什么时候升级裁决

Version History
规则怎么变化
```

每个英文后面都应该像这样直接给中文含义。

以后课程我都会保持这个规则。

---

# 六十九、再设计 `AdjudicatedGoldSet_V0.1`

一条 Gold Record 概念可以是：

```json
{
  "sample_id": "GOLD-000217",

  "final_label": {
    "risk_present": "uncertain",
    "primary_risk_type": "A",
    "needs_review": true
  },

  "annotation_a": {
    "risk_present": true
  },

  "annotation_b": {
    "risk_present": "uncertain"
  },

  "initial_agreement": false,

  "disagreement_type": "context_insufficient",

  "adjudication": {
    "final_decision": "uncertain",
    "reason": "现有材料不足以确认该条件的客观必要性。",
    "adjudicator_id": "EXP-SENIOR-003"
  },

  "consensus_status": "adjudicated",

  "guideline_version": "annotation_guideline_v0.1",

  "annotation_schema_version": "annotation_schema_v0.1",

  "gold_status": "gold"
}
```

---

# 七十、这里有一个很关键的设计

不要只保存：

```text
final_label
```

最好保留：

```text
A原始判断
B原始判断
最终裁决
```

为什么？

因为以后 Schema 更新以后：

> 我们可以重新分析专家分歧。

否则历史信息：

> 永远丢了。

---

# 七十一、这也是 Non-destructive Data Engineering

我们前面反复讲：

> Raw Text 不覆盖。

今天同样：

> Initial Annotation 也不要被 Final Gold 覆盖。

---

# 七十二、关系变成：

```text
Annotation A ─┐
              ├→ Adjudication → Final Gold
Annotation B ─┘
```

原始意见：

> 都保留。

---

# 七十三、现在做一个完整政府采购案例

Clause：

> “投标人须在本市设立固定办公场所，并提供房屋产权证明或租赁合同。”

专家 A：

```text
Risk = true
Type = Supplier Qualification
Level = high
```

专家 B：

```text
Risk = uncertain
Type = Supplier Qualification
Needs Review = true
```

---

# 七十四、分歧不是：

> Risk Type。

两个人都认为：

> 属于供应商资格维度。

真正分歧是：

> **是否已有足够信息把它从“需复核”提升为明确 Potential Risk。**

于是：

```text
disagreement_type
=
decision_threshold
```

即：

> 判断阈值分歧。

---

# 七十五、裁决专家可能认为

按照当前项目 Dataset 的任务定义：

> “只要条款将投标前固定本地办公场所作为准入条件，即进入 Potential Risk 筛查；最终合理性仍需结合完整事实复核。”

于是 Final：

```text
risk_present = true
needs_review = true
```

---

# 七十六、注意这个结果很有意思

```text
true
+
needs_review
```

并不矛盾。

它表示：

> **已经达到风险筛查阈值，但还没有达到最终裁决阈值。**

这就是第 8 阶段多维 Schema 的价值。

---

# 七十七、然后 Guideline 增加一句

> “`risk_present=true` 表示达到风险筛查标准，不等同于最终法律结论；仍可同时设置 `needs_review=true`。”

以后专家再遇到这种问题：

> 一致性就会提高。

---

# 七十八、这就是一次漂亮的 Guideline Learning Loop

```text
Case
 ↓
Disagreement
 ↓
Adjudication
 ↓
New Rule
 ↓
Future Agreement Improves
```

---

# 七十九、如果一致率一直上不去怎么办？

不要马上：

> “换专家。”

先检查三个层次。

第一层：

# Schema Problem

是不是 Label 本身重叠？

---

# 八十、第二层：

# Guideline Problem

定义是不是太模糊？

---

# 八十一、第三层：

# Task Problem

这个任务是不是天然无法仅靠现有输入判断？

例如：

> Clause 本身根本没有足够上下文。

---

# 八十二、如果第三种成立

那正确修复不是：

> 逼专家猜。

而是：

```text
增加Context
```

或者：

```text
允许uncertain
```

---

# 八十三、这也是专业数据项目一个重要能力

# 不强行制造确定性

---

# 八十四、现在看一个反例

团队规定：

> 两个专家不一致时，一律以高级专家意见覆盖。

最终数据库只留下：

```text
final_label
```

看起来很干净。

---

# 八十五、但几年以后：

发现模型在某一类数据表现很差。

想分析：

> 这些 Case 当初是不是专家也很争议？

已经无法知道。

因为：

> 初始分歧被覆盖了。

---

# 八十六、所以应该保留：

```text
annotation_a
annotation_b
adjudication
```

这叫：

# Annotation Lineage
## 标注血缘

---

# 八十七、我们以前有：

```text
Document Lineage
Data Lineage
Normalization Lineage
```

现在又加：

# Label Lineage

---

# 八十八、于是一个 Gold Label 可以一路追：

```text
Gold Label
   ↓
Adjudication Decision
   ↓
Expert A / Expert B
   ↓
Annotation Guideline Version
   ↓
Clause
   ↓
Source Block
   ↓
Original PDF
```

这已经非常接近真正专业的数据资产。

---

# 八十九、现在回到“专家一致性指标”

我们目前记两个就够：

```text
Percent Agreement
直接一致率
```

以及：

```text
Cohen's Kappa
扣除随机一致后的Kappa
```

现在先不用学更多统计指标。

后面真正遇到多标签、多专家、序数等级时，再扩展。

---

# 九十、关键不是收集指标名称

而是能回答：

> **哪一个字段不稳定？为什么不稳定？怎么修？**

这比背 10 个一致性公式：

> 有价值得多。

---

# 九十一、什么时候可以开始大规模标注？

不是：

> “Guideline 写完了。”

而是 Pilot 后至少确认：

```text
核心Label基本稳定
主要分歧类型已经知道
专家知道什么时候选uncertain
上下文基本足够
裁决流程可以运转
Guideline可以版本化
```

然后再扩大。

---

# 九十二、否则会发生什么？

假设先标：

```text
100,000条
```

后来发现：

> `High Risk` 定义从一开始就不统一。

那 10 万条：

> 可能全部要重新审。

这种成本非常可怕。

---

# 九十三、所以小规模试标本质上是：

# Schema Unit Test
## 给标注体系做单元测试

程序上线前要 Test。

Annotation System：

> 也要 Test。

---

# 九十四、现在把整个第 9 阶段压缩成专业版流程

```text
1. Schema已经定义
       ↓
2. 写Annotation Guideline
   把Label变成可执行规则
       ↓
3. Calibration
   专家先做小批量心智对齐
       ↓
4. Pilot
   小批量试标
       ↓
5. Blind Double Annotation
   两位专家独立双标
       ↓
6. Agreement Measurement
   按字段测一致性
       ↓
7. Disagreement Analysis
   分析分歧类型
       ↓
8. Adjudication
   高级专家裁决
       ↓
9. Guideline Revision
   把新规则写回指南
       ↓
10. Gold Finalization
    形成可发布Gold
```

如果以后忘掉所有英文：

> **写规则 → 校准 → 试标 → 双标 → 测一致 → 找分歧 → 裁决 → 改规则 → 出 Gold。**

就记这条。

---

# 九十五、本阶段最值得警惕的几个反例

第一种：

> “找一个最资深专家，把 10 万条全部标完。”

问题是：

> 没有独立复核，也无法估计标签可靠性。

第二种：

> “两个人一起讨论着标。”

这不是 Independent Annotation。

你根本测不出：

> 两人是否真正独立一致。

第三种：

> “不一致的全部删掉。”

这会专门删掉：

> 最有价值的 Hard Case。

第四种：

> “为了提高一致率，把所有 Unknown 都改成 No Risk。”

指标更漂亮，

数据反而更假。

第五种：

> “只保存最终裁决，不保存初始分歧。”

以后完全无法研究：

> 标注不确定性。

第六种：

> “Kappa 到 0.8 就万事大吉。”

错误。

指标只是开始，

还要问：

> 具体哪里分歧、Gold 是否有效。

---

# 九十六、这次我们把核心模型再集中一次

如果第 9 阶段只记五句话：

> **Gold 不是某一个专家的意见，而是一套质量流程。**

> **专家分歧不是垃圾，而是发现边界和修正规则的高价值信号。**

> **必须先盲式独立标注，再讨论，否则测不到真实一致性。**

> **一致性指标首先是在给 Schema 和 Guideline 做体检，不是在给专家排名。**

> **裁决最有价值的产物不是那个最终 Label，而是可以复用到未来案例的新规则。**

这五句话，就是本阶段真正的核心。

---

# 九十七、本阶段最终工程产物

第一个：

# `AnnotationGuideline_V0.1`

它规定：

```text
Label定义
判断规则
正例
反例
边界案例
必需上下文
证据要求
升级裁决条件
版本记录
```

第二个：

# `AdjudicatedGoldSet_V0.1`

每条 Gold 不只有：

```text
final_label
```

还保留：

```text
双标结果
一致状态
分歧类型
裁决过程
指南版本
Gold质量状态
```

---

# 九十八、本阶段掌握测试

现在不看正文，你应该能回答：为什么一个资深专家单独标出来的数据不能天然叫 Gold？为什么专家分歧本身是有价值的信息？Blind Annotation 为什么必须在专家讨论之前进行？Double Annotation 和 Review 有什么区别？为什么一致性要按 `risk_present`、`risk_type`、`risk_level` 等字段分别测？Percent Agreement 在测什么？Cohen's Kappa 为什么要扣除“随机碰巧一致”？为什么不应该迷信某一个 Kappa 阈值？Rationale 为什么不能简单用字符串相等来算一致性？专家分歧至少可能来自哪些不同原因？为什么 Context 不足应该补 Context，而不是逼专家二选一？Adjudication 的真正作用是什么？为什么裁决结果必须写回 Annotation Guideline？为什么 Gold 数据应该保留 Expert A、Expert B 和 Final Decision 三层信息？什么叫 Annotation Lineage？为什么高一致率不一定代表高质量数据？Reliability 和 Validity 有什么区别？为什么 Gold Quality 必须是整条数据 Pipeline 的质量，而不仅仅是 Label 被专家看过？

如果这些能讲清楚：

\[
\boxed{
第四课第9阶段真正掌握
}
\]

---

# 九十九、本阶段最终只记一句话

> **高质量专家标注不是“请专家给答案”，而是先用统一 Guideline 对齐判断标准，再让专家独立双标，用一致性指标发现规则问题，对真正分歧进行裁决，并把裁决经验不断写回指南；Gold 的本质不是专家权威，而是一个可复现、可审计、可持续改进的专家知识生产流程。**

最后只留这一张图：

```text
                  AnnotationSchema
                  专家要标什么
                        │
                        ▼
                AnnotationGuideline
                  怎么统一判断
                        │
                        ▼
                   Calibration
                   专家先校准
                        │
                        ▼
              Blind Double Annotation
                 两位专家独立双标
                        │
                        ▼
               Agreement Measurement
                 测到底有多一致
                        │
                        ▼
                Disagreement Analysis
                 为什么会不一致
                        │
                        ▼
                    Adjudication
                    专家裁决
                        │
                        ▼
                 Guideline Revision
                   新规则写回
                        │
                        ▼
               AdjudicatedGoldSet_V0.1
                   真正Gold数据
```

下一阶段会接着这条线进入：
