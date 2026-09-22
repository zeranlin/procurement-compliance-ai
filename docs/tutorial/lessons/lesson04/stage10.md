# 第四课 · 第 10 阶段
# Hard Negative 与边界案例设计
## 为什么模型真正的专业能力，不是在“明显对 / 明显错”的题目上体现，而是在两个几乎一样的案例之间做出不同判断？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Hard Negative 不是普通负样本，而是“非常像正样本的负样本”。 它的作用是打掉模型的错误捷径。**
2. **真正有价值的数据经常是一对，而不是一条。 两个案例越相似、结论越不同，越能暴露模型是否抓住了关键条件。**
3. **最好的 Hard Case 往往来自真实错误和专家分歧，而不是靠人凭空编故事。 模型错过什么，就围绕什么补数据。**
4. **Boundary Case（边界案例）不是必须强行二选一。 如果合理结论确实依赖缺失上下文，就应该保留 uncertain / needs_review。**
5. **Hard Case 既是训练材料，也是 Benchmark 的压力测试材料。 但同一个案例及其改写版本绝不能一边训练、一边考试。**
6. **Hard Negative 的价值，是让模型不能再靠关键词和表面模式取巧。**
7. **真正高价值的数据经常不是一条样本，而是一对只差关键条件的对比样本。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Hard Negative` | 高难负例：表面像风险但正确结论不应判风险 |
| `ANN` | ANN/近似最近邻：在大规模向量中快速寻找相似项 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `Hard Positive` | 高难正例：没有明显关键词但确实需要识别的风险 |
| `Dataset` | 数据集：按统一 Schema、版本和质量标准组织的样本集合 |
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `Accuracy` | 准确率：全部样本中判断正确的比例 |
| `Shortcut Learning` | 捷径学习：利用表面相关线索而非真正任务规律 |
| `Annotation Guideline` | 标注规范：统一专家如何理解字段、边界和例外 |
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

第 9 阶段我们已经建立了：

```text
Annotation Schema
标什么
        ↓
Annotation Guideline
怎么统一判断
        ↓
双人独立标注
        ↓
一致性测量
        ↓
分歧分析
        ↓
专家裁决
        ↓
AdjudicatedGoldSet_V0.1
```

现在终于有了一批相对可信的专家 Label。

但这时候会出现一个很危险的假象。

假设模型测试结果：

```text
Accuracy = 94%
```

看起来已经非常优秀。

可我们仔细看 Test Set：

```text
明显违规表达
→ Risk

普通标准条款
→ No Risk
```

模型甚至不用真正理解政府采购业务。

只需要学几个词：

```text
“本市”
“唯一”
“指定品牌”
“注册满5年”
```

就可能拿到非常漂亮的分数。

这类模型一旦进入真实文件，就会迅速暴露：

> **它学会的是关键词，不是判断边界。**

所以第 10 阶段要解决的是：

# 怎样专门构造“容易骗过模型”的数据？

最终产物是：

# `HardCaseSet_V0.1`

---

# 一、本阶段只解决一个核心问题

> **怎样让训练数据和测试数据包含足够多的“表面很像、专业结论却不同”的案例，从而迫使模型学习真正决定判断结果的关键条件，而不是记关键词、模板和表面模式？**

先看整条流程。

```text
专家Gold数据
    │
    ▼
发现容易案例与困难案例
    │
    ▼
构造对比案例
Contrastive Cases
    │
    ▼
设计Hard Negative / Hard Positive
    │
    ▼
加入边界案例
Boundary Cases
    │
    ▼
专家复核
    │
    ▼
切分与泄漏检查
    │
    ▼
HardCaseSet_V0.1
```

中文记忆就是：

> **找“容易被骗”的地方 → 做成成对案例 → 专家确认 → 加入训练和考试。**

---

# 二、本阶段最重要的 5 个核心心智模型

这 5 个，是第 10 阶段真正需要留下来的东西。

1. **Hard Negative 不是普通负样本，而是“非常像正样本的负样本”。** 它的作用是打掉模型的错误捷径。  
2. **真正有价值的数据经常是一对，而不是一条。** 两个案例越相似、结论越不同，越能暴露模型是否抓住了关键条件。  
3. **最好的 Hard Case 往往来自真实错误和专家分歧，而不是靠人凭空编故事。** 模型错过什么，就围绕什么补数据。  
4. **Boundary Case（边界案例）不是必须强行二选一。** 如果合理结论确实依赖缺失上下文，就应该保留 `uncertain / needs_review`。  
5. **Hard Case 既是训练材料，也是 Benchmark 的压力测试材料。** 但同一个案例及其改写版本绝不能一边训练、一边考试。

这五句话先记住。

下面所有内容都只是它们的展开。

---

# 三、先把四类样本彻底分清

我们先不用复杂术语。

看这张表。

| 类型 | 中文理解 | 模型难度 | 示例 |
|---|---|---:|---|
| Easy Positive | 明显正例 | 低 | 明确要求投标企业必须在本市注册 |
| Easy Negative | 明显负例 | 低 | 普通的履约质量要求 |
| Hard Positive | 隐蔽正例 | 高 | 风险不靠明显关键词，而藏在组合条件中 |
| Hard Negative | 迷惑性负例 | 高 | 出现“本地”等敏感词，但实际上不是投标准入限制 |
| Boundary Case | 边界案例 | 很高 | 必须结合项目场景才能判断 |

真正决定专业模型质量的：

> 往往是后三类。

---

# 四、什么叫 Hard Negative？

# Hard Negative
## 高难负样本 / 迷惑性负样本

它不是：

> 普通“没有风险”的条款。

而是：

> **表面特征很像风险案例，但专业判断不应该直接判为风险。**

这是最关键的定义。

---

## 一个最典型的例子

案例 A：

> “供应商须在本市设立固定服务机构方可参与投标。”

可能进入：

```text
Potential Risk
```

因为这里把：

> 投标前已经设立本地机构

作为了参与条件。

再看案例 B：

> “中标供应商应保证故障发生后 2 小时内到达项目现场，不限制服务机构设立方式。”

它同样出现：

```text
现场
2小时
项目所在地
```

甚至模型可能觉得：

> “又是地域限制。”

但是它和 A 有一个非常关键的区别：

```text
A
投标前必须存在本地机构

B
要求履约响应能力
但不限定实现方式
```

这个差异：

> 才是模型真正应该学习的东西。

所以 B 就是一个很有价值的：

# Hard Negative

---

# 五、为什么普通负样本远远不够？

假设训练数据是：

```text
Risk:
必须在本市注册
必须拥有本地办公场所
必须为某品牌认证代理商

No Risk:
按时交货
提供培训
提供质量保证
```

模型很快就会学到：

```text
出现“本市”
→ Risk

出现“品牌”
→ Risk
```

这叫：

# Shortcut Learning
## 捷径学习

意思是：

> 模型找到了一个很容易的表面规律，于是懒得学习真正复杂的业务逻辑。

---

# 六、Hard Negative 的核心作用就是“拆捷径”

可以把它写成：

\[
\boxed{
HardNegative
\rightarrow
BreakShortcut
}
\]

例如你发现模型学成：

\[
出现“本地”
\Rightarrow
Risk
\]

那就应该专门加入：

```text
包含“本地”
但是
No Risk / Needs Review
```

的案例。

模型就再也不能：

> 只看“本地”两个字。

它必须继续问：

```text
本地要求针对谁？
发生在投标前还是中标后？
是固定机构要求还是服务能力要求？
是否限制实现方式？
是否有业务必要性？
```

这时它才开始逼近真正的专业判断。

---

# 七、真正强的数据单位不是“一条”，而是“一对”

这是第 10 阶段最值得记住的一个专业思想：

# Contrastive Pair
## 对比样本对

例如：

### 样本 A

> 供应商必须在本市注册满 3 年。

### 样本 B

> 供应商中标后须在本市项目现场提供为期 3 年的运维服务。

两个句子都出现：

```text
本市
3年
供应商
```

但是“3 年”修饰的东西完全不同。

A：

```text
注册年限
```

B：

```text
服务期限
```

如果模型只学关键词：

> 非常容易混。

如果模型真正理解：

> 才能区分。

---

# 八、这可以理解成“最小差异测试”

英语里常用一个词：

# Minimal Pair
## 最小对比样本

意思是：

> 两个案例尽可能相似，只改变一个关键条件，看答案是否应该随之改变。

这是极其强大的数据设计方法。

---

## 例子

版本 A：

> 投标人须在投标截止日前已在本市设立售后服务机构。

版本 B：

> 中标人应在合同履行期间保证本市项目现场的售后服务响应。

我们只改了几个关键条件：

```text
投标人
→ 中标人

投标前已有
→ 合同履行期间具备

固定机构
→ 服务响应
```

最终专业判断：

> 可能发生明显变化。

模型如果无法区分：

说明它还没有学到：

# Decision Boundary
## 决策边界

---

# 九、所以真正的专业能力，本质上是学“边界”

可以把模型想成一个裁判。

最容易的球：

> 离界线 10 米。

谁都能判。

真正考验裁判的是：

> 球压在线上。

AI 也是一样。

如果 Benchmark 全是：

```text
离边界很远的案例
```

模型 98%：

> 没什么值得骄傲。

我们真正想知道：

> **它在边界附近表现怎么样？**

---

# 十、这就是 Boundary Case

# Boundary Case
## 边界案例

边界案例不是：

> “故意出刁钻题。”

而是：

> **专业判断真的依赖更多事实、上下文或者规范解释的案例。**

例如：

> “供应商应具备 2 小时现场响应能力。”

单看这一句，很难永远固定为：

```text
Risk
```

或者：

```text
No Risk
```

因为可能涉及：

```text
医院核心系统
普通办公软件
应急设备
远程服务项目
全天候生产系统
```

项目不同：

> 2 小时响应的合理性也可能不同。

所以这种 Case 很可能应该：

```text
risk_present = uncertain
needs_review = true
```

并说明：

```text
context_needed
=
项目性质
现场服务必要性
停机影响
市场供应情况
```

---

# 十一、边界案例最重要的价值是什么？

不是让模型猜答案。

而是教模型：

> **什么时候不能武断地下结论。**

这是专业模型和普通分类器之间很重要的区别。

可以写成：

\[
\boxed{
ProfessionalModel
\neq
AlwaysAnswer
}
\]

更好的专业模型应该：

\[
\boxed{
KnowWhenToAnswer
+
KnowWhenToEscalate
}
\]

也就是：

> 知道什么时候可以判断，也知道什么时候该交给人。

---

# 十二、Hard Positive 又是什么？

# Hard Positive
## 隐蔽正样本

很多人只关注 Hard Negative。

其实 Hard Positive 同样重要。

Hard Positive 是：

> **真正存在风险信号，但没有明显危险关键词。**

例如某些条款不写：

```text
必须购买某品牌
```

而是列出：

```text
尺寸
接口
协议
特殊认证
独有功能
多个技术指标组合
```

单个指标看：

> 都正常。

组合起来：

> 可能高度指向极少数产品。

这里真正需要判断的是：

# Constraint Combination
## 约束组合

---

# 十三、模型如果只学显眼关键词，会漏掉 Hard Positive

这种错误叫：

# False Negative
## 漏报

对于风险筛查系统：

> 漏报往往非常值得关注。

所以一个专业 Dataset 不能只是防：

```text
误报
False Positive
```

还要防：

```text
漏报
False Negative
```

Hard Negative：

> 主要帮助降低误报。

Hard Positive：

> 主要帮助降低漏报。

---

# 十四、因此训练数据应该同时塑造两条边界

```text
Hard Negative
告诉模型：
“看起来像风险，但别乱报。”

Hard Positive
告诉模型：
“看起来不明显，但别漏掉。”
```

这两者一起，才是在真正训练：

# Decision Boundary

---

# 十五、Hard Case 最好的来源在哪里？

这里我们直接接第 9 阶段。

最好的第一来源是：

# Expert Disagreement
## 专家分歧

如果两位专家经常在某类 Case 上不一致：

> 这里天然就是困难区。

例如：

```text
本地服务能力
vs
本地机构准入
```

经常争议。

那就说明：

> 这类案例值得专门建设 Hard Case Slice。

---

# 十六、第二个高价值来源：Model Error

让 Baseline 模型跑一批人工 Gold。

然后把错误分成：

```text
False Positive
误报

False Negative
漏报
```

假设模型大量把：

> “项目所在地现场响应”

误判成地域准入风险。

这不是坏消息。

这是数据建设的方向。

---

# 十七、这形成一个非常重要的闭环

```text
模型
 ↓
犯错
 ↓
错误分类
 ↓
找到错误模式
 ↓
补Hard Case
 ↓
重新训练
 ↓
重新评测
```

这叫：

# Error-driven Data Improvement
## 错误驱动的数据改进

这个心智模型非常重要。

很多团队遇到模型问题第一反应是：

> 换更大的模型。

而真实项目中，经常更有效的是：

> **把模型反复犯错的边界变成更好的数据。**

---

# 十八、第三个来源：专家裁决记录

第 9 阶段我们保留了：

```text
annotation_a
annotation_b
disagreement_type
adjudication
```

特别是：

```text
disagreement_type = true_boundary_case
```

这些案例：

> 天然就是 Hard Case 候选。

所以保存专家分歧，不只是为了审计。

它直接成为：

# Future Training Asset
## 未来训练资产

---

# 十九、第四个来源：真实投诉、质疑、审查中的复杂案例

现实业务里真正发生争议的 Case：

> 往往比人工凭空编的案例更有价值。

但这里仍然要注意第 7 阶段的规则：

```text
后续裁决结果
可以帮助构造Gold

但不能泄漏到
预测时点的Model Input
```

所以：

> 真实案例 ≠ 可以随便把后续答案塞给模型。

---

# 二十、第五个来源：Counterfactual Editing

# Counterfactual
## 反事实改写

这个词很重要，但理解很简单。

意思是：

> **如果我只改一个关键条件，答案会不会改变？**

例如原句：

> “投标人须在本市设立服务机构。”

改成：

> “中标人须保证项目所在地现场服务能力。”

---

# 二十一、我们不是为了“改写得好看”

而是为了：

> 改一个决定判断的变量。

可以写成：

\[
x
\rightarrow
y
\]

如果改变一个关键条件：

\[
x'
\]

那么：

\[
y'
\]

也应该变化。

---

# 二十二、模型应该对真正重要的变化敏感

而对无关变化稳定。

例如：

```text
供应商
→ 投标人
```

如果语义不变，

Label：

> 不应该乱跳。

---

# 二十三、但如果：

```text
投标前必须已有本地机构
→
中标后自行保障现场服务
```

这种业务条件改变，

Label：

> 可能应该变化。

---

# 二十四、这就是一个非常专业的模型能力

# Invariance
## 对无关变化保持稳定

以及：

# Sensitivity
## 对关键变化保持敏感

一个好模型应该同时做到：

\[
\boxed{
对无关变化稳定
}
\]

\[
\boxed{
对关键条件敏感
}
\]

---

# 二十五、这也是为什么“成对数据”这么强

单独给模型：

> 一条 Risk。

模型不知道：

> 到底哪部分是决定性因素。

但如果同时有：

```text
案例A
Risk

案例B
No Risk
```

而两者只差一个关键条件，

模型更容易学习：

> 那个条件才是真正重要的。

---

# 二十六、从工程角度，我们可以给 Hard Case 保存哪些字段？

第一版不需要复杂。

一个 Hard Case 可以概念设计成：

```json
{
  "sample_id": "HC-000217",

  "case_type": "hard_negative",

  "source_sample_id": "CLAUSE-00918",

  "paired_sample_id": "HC-000218",

  "confusing_feature": "local_service_wording",

  "decision_factor": "pre_bid_local_entity_requirement",

  "risk_present": false,

  "needs_review": false,

  "difficulty": "hard",

  "annotation_status": "gold",

  "hardcase_version": "hardcase_v0.1"
}
```

---

# 二十七、这里最值得注意的是两个字段

```text
confusing_feature
```

表示：

> 为什么模型容易被骗？

例如：

```text
出现“本地”
```

---

另一个：

```text
decision_factor
```

表示：

> 真正决定答案的是什么？

例如：

```text
是否把投标前已有本地机构作为参与条件
```

这两个字段特别有研究价值。

---

# 二十八、Hard Case 不等于长文本

这是一个常见误解。

很多人觉得：

> 越复杂越难。

不一定。

最难的 Case 甚至可能只有一句话。

例如：

> “供应商须在本市设有服务机构。”

真正困难的不是文本长度。

而是：

> 缺了上下文。

所以：

\[
\boxed{
Difficulty
\neq
Length
}
\]

---

# 二十九、Hard Case 也不等于生僻案例

真正高价值的 Hard Case：

> 最好是业务中经常遇到，又容易混淆的。

如果一个案例：

```text
极其罕见
只出现一次
```

即使很难，

业务价值：

> 未必高。

所以 Hard Case 设计还要考虑：

# Frequency × Impact

即：

> 出现频率 × 出错影响。

---

# 三十、可以建立一个简单优先级

\[
Priority
=
Frequency
\times
ErrorRate
\times
BusinessImpact
\]

不需要把这个公式当成精确数学模型。

它只是提醒我们：

> **高频、模型常错、业务影响大的 Case，最值得优先建设。**

---

# 三十一、举例

假设：

| Case | 出现频率 | 模型错误率 | 业务影响 |
|---|---:|---:|---:|
| 本地服务要求 | 高 | 高 | 高 |
| 极少见附件格式 | 低 | 高 | 低 |
| 一般日期格式 | 高 | 低 | 低 |

很明显：

> 第一类最值得成为 Hard Case 建设重点。

---

# 三十二、Hard Case 在 Train 和 Test 中的角色不同

这点一定要分清。

Train 中的 Hard Case：

> 是用来教模型。

Test 中的 Hard Case：

> 是用来考模型。

所以绝不能：

```text
同一个Hard Case
→ Train

它的近似改写
→ Test
```

否则又回到第 7 阶段：

# Leakage

---

# 三十三、特别是 Counterfactual Pair

如果 A、B 是一组成对样本：

```text
A ↔ B
```

最好把它们视为：

# One Leakage Group

也就是说：

\[
\boxed{
Pair
应该整体进入同一个Split
}
\]

否则：

> 模型训练时看了 A，

考试时考 B，

成绩可能虚高。

---

# 三十四、Synthetic Hard Case 也必须继承父样本 Split

如果：

```text
Parent Sample
→ Train
```

它生成的 Counterfactual：

> 通常也留在 Train。

如果 Parent：

```text
Test
```

它生成的改写：

> 不得放入 Train。

第 6、7 阶段的：

# Lineage-aware Split

在这里继续生效。

---

# 三十五、是不是 Hard Case 越多越好？

也不是。

如果训练数据全部都是：

> 极端边界案例，

模型可能反而不知道：

> 正常世界是什么样。

所以我们需要：

# Difficulty Spectrum
## 难度光谱

```text
Easy
        ↓
Medium
        ↓
Hard
        ↓
Boundary
```

真正好的 Dataset：

> 应该覆盖整条光谱。

---

# 三十六、为什么？

Easy Case：

> 教基础模式。

Medium Case：

> 建立一般泛化。

Hard Case：

> 修决策边界。

Boundary Case：

> 学会不确定性和升级人工。

所以它们不是互相替代。

---

# 三十七、这个阶段最重要的一张图

```text
                      数据难度
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
        Easy           Hard         Boundary
          │              │              │
       学基本模式      学决策边界      学会不强答
          │              │              │
          └──────────────┼──────────────┘
                         ▼
               Professional Model
```

---

# 三十八、现在做一个更完整的采购案例

### Case A

> “投标人须在本市注册成立 3 年以上。”

可能：

```text
Potential Risk
Supplier Qualification
```

---

### Case B

> “中标供应商应为本项目提供 3 年运维服务。”

同样出现：

```text
3年
```

但显然：

> 不是注册年限。

这是：

# Hard Negative Pair

---

### Case C

> “投标人须具备不少于 3 个同类项目业绩。”

是否一定 Risk？

不能脱离：

```text
采购规模
项目复杂程度
业绩定义
时间范围
金额门槛
必要性
```

这是：

# Boundary Case

---

### Case D

没有写“指定品牌”。

但技术参数组合：

> 可能只覆盖极少数产品。

这是：

# Hard Positive

---

# 三十九、看出来了吗？

真正专业的数据集应该逼模型回答的不是：

> “有没有敏感词？”

而是：

```text
约束针对什么？
发生在什么阶段？
限制了谁？
是否有替代实现方式？
是否需要上下文？
关键事实是什么？
```

这才是业务推理。

---

# 四十、Hard Negative 为什么对 Precision 特别重要？

先回忆两个概念。

# Precision
## 查准率

模型报出来的风险中：

> 有多少真的是风险。

如果模型见到：

```text
本地
品牌
认证
业绩
```

就全部报警，

Recall 可能很高。

但 Precision：

> 会很差。

Hard Negative：

> 正是在教育模型“不要乱报警”。

---

# 四十一、Hard Positive 为什么对 Recall 重要？

# Recall
## 查全率 / 召回率

所有真正需要关注的风险里：

> 模型找出了多少。

如果模型只认识显眼关键词，

隐蔽风险：

> 就会漏掉。

Hard Positive：

> 在帮模型减少这种漏报。

---

# 四十二、所以可以简单记成

\[
\boxed{
HardNegative
\rightarrow
提高精确判断
}
\]

\[
\boxed{
HardPositive
\rightarrow
提高隐蔽风险发现能力
}
\]

当然实际指标不会这么单一，但作为心智模型很好用。

---

# 四十三、模型错了一条以后，怎么把它变成数据资产？

不要只修这一条。

应该问：

> **这属于哪一种错误模式？**

例如模型误报：

> “2 小时现场响应”。

不要只添加这一句。

应该建立一个：

```text
local_service_requirement
```

Hard Case Family。

---

# 四十四、什么叫 Case Family？

就是同一种判断机制的案例族。

例如：

```text
投标前本地机构
中标后服务能力
现场响应时间
远程响应
服务网点
驻场人员
临时派驻
固定办公场所
```

它们看起来有关联，

但专业含义：

> 不完全一样。

这组案例放在一起，

模型才真正学边界。

---

# 四十五、这比“补一条错题”强得多

可以写成：

\[
\boxed{
OneError
\rightarrow
ErrorPattern
\rightarrow
CaseFamily
}
\]

这就是专业的数据迭代。

---

# 四十六、这也决定了未来 Error Analysis 的方式

不要只统计：

```text
错了127条
```

而要统计：

```text
地域服务边界 37条
技术参数组合 26条
业绩条件 21条
评分年限 18条
上下文不足 15条
其他 10条
```

这样才能知道：

> 下一个 Dataset Version 应该补什么。

---

# 四十七、Hard Case 需要比普通样本更强的专家复核

为什么？

因为它本来就在边界附近。

如果 Hard Case 的 Label 本身错了：

> 会比普通错标伤害更大。

---

# 四十八、所以推荐

普通 Train 样本：

> 可以采用标准质量流程。

Hard Case / Benchmark：

> 更适合双标 + 裁决。

也就是：

```text
Hard Case
        ↓
Double Annotation
        ↓
Disagreement Check
        ↓
Adjudication
        ↓
Gold
```

第 9 阶段的流程：

> 在这里直接复用。

---

# 四十九、Hard Case 的 Rationale 也必须更精确

普通样本可能只写：

> “存在资格限制。”

Hard Pair 更应该明确：

```text
共同点是什么？
关键差异是什么？
为什么这个差异改变Label？
```

例如：

> 两个案例都涉及项目所在地，但本案例仅要求中标后的履约响应能力，并未要求供应商在投标前已设立本地机构，因此不能仅凭“项目所在地”一词直接归入地域准入风险。

这样的 Rationale：

> 对模型训练价值极高。

---

# 五十、它实际上在教模型“对比推理”

# Contrastive Reasoning
## 对比式推理

不是告诉模型：

> A 是什么。

而是告诉它：

> **为什么 A 和 B 不一样。**

这比孤立标签：

> 更接近专业学习。

---

# 五十一、以后做 SFT 时，可以直接派生成这种训练任务

```text
以下两个采购条款非常相似，
请指出决定其风险判断不同的关键条件。
```

然后输出：

```text
共同特征：
都涉及项目所在地服务。

关键差异：
A要求投标前已存在本地机构；
B只要求中标后的履约能力。

因此：
不能仅根据“本地/所在地”关键词做判断。
```

这会是非常有价值的专家 SFT 数据。

---

# 五十二、这说明 HardCaseSet 不只是分类数据

它还能派生：

```text
Classification
分类

SFT
专业解释

Evaluation
压力测试

Error Analysis
错误诊断
```

再次体现：

# Master Data → Multiple Views

---

# 五十三、现在定义 `HardCaseSet_V0.1`

第一版我们不用搞得很复杂。

可以包含：

```text
sample_id
source_sample_id
paired_sample_id
case_type
case_family
confusing_feature
decision_factor
risk_present
primary_risk_type
needs_review
difficulty
rationale
annotation_status
split
schema_version
```

其中真正关键的是：

```text
case_type
case_family
confusing_feature
decision_factor
paired_sample_id
```

因为这些字段：

> 让我们知道为什么它“难”。

---

# 五十四、建议的 Case Type

我们只保留五类就够：

```text
easy_positive
easy_negative
hard_positive
hard_negative
boundary_case
```

不要一开始做：

> 37 个 Difficulty Type。

仍然遵守：

# Minimal but Sufficient

---

# 五十五、如何判断某条是不是 Hard Case？

不是靠专家说：

> “我感觉挺难。”

更好的信号包括：

```text
专家经常分歧
模型经常预测错误
与另一类样本高度相似
需要多个上下文条件
容易触发关键词捷径
```

出现越多：

> 越值得进入 Hard Case Pool。

---

# 五十六、甚至可以保存一个简单的 Difficulty Score

例如不是人为拍脑袋 0.83，

而由几个信号组成：

\[
Difficulty
=
ExpertDisagreement
+
ModelError
+
SemanticConfusability
+
ContextDependency
\]

这里只是概念公式。

重点是：

> 难度应该有依据。

---

# 五十七、Hard Case 的比例应该是多少？

没有一个通用固定比例。

关键取决于：

```text
模型当前水平
任务复杂度
数据量
真实业务中的困难案例比例
Benchmark目的
```

但有一个原则非常重要：

> **不要让总分被大量 Easy Case 淹没。**

---

# 五十八、例如 Test 有 10,000 条

其中：

```text
9,800条 Easy
200条 Hard
```

模型：

```text
Easy = 99%
Hard = 40%
```

总 Accuracy 仍然非常漂亮。

但业务上：

> 可能完全不够用。

---

# 五十九、所以成熟 Benchmark 应该单独报告

```text
Overall
总成绩

Easy Slice
容易案例

Hard Negative Slice
高难负样本

Hard Positive Slice
隐蔽正样本

Boundary Slice
边界案例
```

这样：

> 模型的真实短板不会被平均数掩盖。

---

# 六十、这也是第 8 课 Benchmark 会做的事情

今天第 10 阶段只负责：

> **把这些高价值数据准备好。**

未来第 8 课：

> 再把它们正式做成 Slice Evaluation。

---

# 六十一、这一阶段最重要的反例

如果你发现模型一看到：

> “本地”

就报风险，

错误做法是：

> 在 Prompt 里写一句“不要看到本地就报风险”。

这可能暂时有效。

但更稳的办法是：

> 给模型大量经过专家确认的对比样本。

---

# 六十二、为什么？

Prompt 是：

> 口头提醒。

Hard Case Data 是：

> 反复训练出来的边界经验。

两者价值：

> 完全不同。

---

# 六十三、第二个反例

模型漏掉复杂技术参数风险。

错误做法：

> 继续收更多明显“指定品牌”的案例。

因为模型本来就会。

真正应该补的是：

> **没有品牌名、但限制组合高度异常的 Hard Positive。**

---

# 六十四、第三个反例

专家有分歧：

> 直接删除。

这样做会让 Dataset：

> 越来越简单。

最后模型的 Test：

> 看起来越来越高。

实际上你把真实世界最难的部分：

> 全删掉了。

---

# 六十五、第四个反例

人工生成一大批所谓 Hard Negative：

> 但从没让专家复核。

这很危险。

因为 Hard Case 本身：

> 就最容易标错。

所以“难例增强”不能变成：

# Synthetic Noise
## 合成噪声

---

# 六十六、第五个反例

把某个 Test Hard Case：

> 改几个词，

然后放回 Train。

这是典型：

# Benchmark Leakage

Stage 7 已经明确禁止。

---

# 六十七、现在把本阶段工程流程压成最终版

```text
AdjudicatedGoldSet_V0.1
        │
        ▼
收集真实错误
Model Errors
        │
        ├──────────────┐
        ▼              ▼
专家分歧         高频业务边界
        │              │
        └──────┬───────┘
               ▼
        建立Case Family
        按错误机制归类
               │
               ▼
      设计Contrastive Pair
          对比样本对
               │
        ┌──────┼───────┐
        ▼      ▼       ▼
     Hard+   Hard-   Boundary
        │      │       │
        └──────┼───────┘
               ▼
        专家双标与裁决
               │
               ▼
          Split / Leakage
               │
               ▼
        HardCaseSet_V0.1
```

中文只记：

> **找错误 → 找规律 → 做成对比 → 专家确认 → 防泄漏 → 进入难例库。**

---

# 六十八、本阶段再强化一次 5 个核心心智模型

如果这一阶段过一周以后只剩下五句话，我希望是：

> **Hard Negative 的价值，是让模型不能再靠关键词和表面模式取巧。**

> **真正高价值的数据经常不是一条样本，而是一对只差关键条件的对比样本。**

> **专家分歧和模型错误不是失败记录，而是 Hard Case 的主要矿藏。**

> **Boundary Case 不应该被强迫二选一，它可以训练模型学会“需要人工复核”。**

> **Hard Case 的训练集和测试集必须严格隔离，成对样本和派生样本都要继承同一个 Split。**

这五句话，就是第 10 阶段的骨架。

---

# 六十九、本阶段最终工程产物

我们今天真正得到的是：

# `HardCaseSet_V0.1`

它不只是：

> 一堆难题。

而是一个结构化的高价值数据资产：

```text
HardCaseSet_V0.1
│
├── Hard Positive
│   隐蔽风险
│
├── Hard Negative
│   看起来像风险但不是
│
├── Boundary Case
│   需要上下文或人工复核
│
└── Contrastive Pair
    只改变关键条件的对比样本
```

其中最关键的是：

> **每一条难例最好知道“模型为什么容易错，以及真正决定答案的条件是什么”。**

---

# 七十、本阶段掌握测试

现在不回看正文，你应该能解释：Hard Negative 为什么不是普通 No Risk；Hard Positive 与 Hard Negative 分别主要在解决什么问题；为什么政府采购模型特别容易产生关键词捷径；什么叫 Shortcut Learning；什么叫 Contrastive Pair；什么叫 Minimal Pair；为什么两个只差一个业务条件的案例比两个完全不相关案例更有训练价值；Boundary Case 为什么可以合法地标记 `uncertain / needs_review`；为什么专业模型必须学习什么时候不应该强答；Hard Case 为什么最好来自专家分歧和真实模型错误；什么叫 Error-driven Data Improvement；为什么一次模型错误应该进一步发展成一个 Case Family；什么是 Counterfactual Editing；模型为什么要对无关变化保持稳定、对关键条件保持敏感；为什么 Hard Case 不等于长文本，也不等于生僻案例；为什么 Hard Case 需要更强的专家复核；为什么 Contrastive Pair 不应该被拆到 Train 和 Test 两边；为什么 Synthetic Hard Case 必须继承父样本 Split；为什么 Benchmark 不能只报告 Overall Accuracy；以及为什么一个专业模型真正的能力，往往是在“两个看起来几乎一样的案例”之间体现。

如果这些都能讲清楚：

\[
\boxed{
第四课第10阶段真正掌握
}
\]

---

# 本阶段最终只记一句话

> **Hard Case 数据的价值，不是故意把题出难，而是围绕模型真实错误和专家真实分歧，构造“表面相似、关键条件不同”的对比案例，迫使模型放弃关键词捷径，真正学习政府采购判断的决策边界，并在证据不足时学会主动进入人工复核。**

最后只留一张图：

```text
             普通训练数据
                  │
                  ▼
               模型
                  │
                  ▼
              犯错误
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
      误报                 漏报
False Positive        False Negative
        │                   │
        ▼                   ▼
 Hard Negative        Hard Positive
        │                   │
        └─────────┬─────────┘
                  ▼
          Contrastive Pair
             对比样本
                  │
                  ▼
          Boundary Cases
             边界案例
                  │
                  ▼
          专家双标 + 裁决
                  │
                  ▼
          HardCaseSet_V0.1
                  │
                  ▼
         更可靠的决策边界
```

---

# 下一阶段：第四课 · 第 11 阶段
## Dataset Versioning、Lineage 与数据质量报告

第 10 阶段之后，我们已经有了：

```text
Raw Document
ParsedDocument
ClauseUnit
CleanClause
DedupedClauseSet
DatasetSplit
LeakageAudit
AnnotationSchema
AdjudicatedGoldSet
HardCaseSet
```

下一阶段不再继续“加工某一条数据”。

而要解决一个更工程化的问题：

> **半年以后，你还能不能准确说清楚 ProcurementDataset_V0.1 到底由哪些原始文件、哪一版解析器、哪一版清洗规则、哪一版 Label Schema、哪一批专家标注以及哪一个 Split 组成？**

第 11 阶段会把这整条链真正变成：

# 可版本化、可追溯、可审计的数据产品

最终会产出：

# `DatasetManifest_V0.1`
# `DatasetQualityReport_V0.1`

然后第 12 阶段，我们就能正式组装整个第四课最终工程产物：

# `ProcurementDataset_V0.1`

---
