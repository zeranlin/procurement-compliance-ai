# 第八课 · 第 8 阶段
# Synthetic Data & Curriculum：合成领域语料、难度分层与覆盖扩展
## 当真实政府采购语料覆盖不足时，合成数据能不能补？为什么“让 LLM 多生成一些采购文本”可能反而把模型训练得更假？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **SyntheticData ≠ FreeNewKnowledge。合成数据能扩展表达和组合覆盖，但不能凭空创造可靠事实。**
2. **SyntheticGeneration 必须由 CoverageGap 驱动。先发现真实语料缺口，再生成，不做无目标数据膨胀。**
3. **SurfaceDiversity ≠ DistributionDiversity。句子看起来不同，不代表训练分布真的扩展。**
4. **Generated ≠ TrainingEligible。合成数据必须经过验证、去重、证据检查和风险审核才能进入训练。**
5. **TeacherModel ≠ GroundTruth。教师模型是候选数据生成器，不是事实权威。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Curriculum` | 课程式训练：按难度、类型或阶段安排训练数据顺序 |
| `Synthetic Data` | 合成数据：由规则/模型生成、需质量控制的训练数据 |
| `CPT` | CPT/继续预训练：在领域语料上继续执行预训练目标 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Validation` | 验证集：开发阶段用于选模型、调参数和早停 |

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

到第 7 阶段，我们已经建立：

\[
\boxed{
Corpus
+
Tokenizer
+
Sequence
+
Mixture
+
ForgettingControl
+
Retention
}
\]

但真实项目里很快会遇到一个问题：

> **高质量真实采购语料并不总是覆盖我们希望模型掌握的全部分布。**

例如某些类型可能非常稀缺：

```text
罕见风险条款
复杂跨章节条件
特殊行业采购
极端金额场景
高难合同条款
少见文号格式
特殊异常案例
```

这时很多团队会想到：

> “那就让一个更强的 LLM 生成更多数据。”

这件事可以做。

但如果没有严格边界，也可能制造：

```text
虚构事实
语言风格趋同
教师模型偏差复制
重复模式放大
模型自己训练自己
真实分布被稀释
```

所以本阶段正式进入：

# Synthetic Data
## 合成数据

以及：

# Curriculum Learning
## 课程式训练

本阶段最终形成：

# `ProcurementCPTSyntheticCurriculumPolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

合成数据不是：

> **“免费的新知识”。**

更准确地说：

\[
\boxed{
SyntheticData
=
ControlledDistributionExpansion
}
\]

也就是：

> **在已有知识、规则和真实样本边界内，主动扩展训练分布。**

所以最重要的一条边界：

\[
\boxed{
SyntheticData
\neq
FreeNewKnowledge
}
\]

它可以：

```text
改写
组合
扩展
补难例
补格式
补覆盖
```

但不能自动保证：

```text
事实真实
规则最新
业务合理
法律结论正确
```

---

# 二、核心心智模型 ①：Synthetic Data 首先是“分布工程”，不是“内容生成”

如果只是说：

> “生成 100 万条采购文本。”

这个目标几乎没有工程意义。

真正应该先问：

```text
当前真实Corpus缺什么？

缺行业？
缺风险类型？
缺长文档？
缺极端金额？
缺稀有表达？
缺困难负样本？
```

然后才决定：

> 用 Synthetic Data 补哪一块。

所以：

\[
\boxed{
SyntheticGeneration
必须由
CoverageGap
驱动
}
\]

而不是：

> “因为可以生成，所以生成。”

---

# 三、Coverage Gap：先做缺口分析，再生成

完整流程：

```text
Real Corpus
真实语料
↓
Coverage Analysis
覆盖分析
↓
Gap Detection
发现缺口
↓
Synthetic Target Definition
定义需要补的分布
↓
Generation
生成
↓
Validation
验证
↓
Mixture Control
控制混合比例
↓
CPT
进入继续预训练
```

中文解释：

> 先看真实数据缺什么，再精确生成什么，而不是先生成再找用途。

因此：

\[
\boxed{
SyntheticData
=
GapFillingTool
}
\]

---

# 四、Synthetic Data 可以分成哪几类？

第一类：

# Paraphrase Augmentation
## 改写增强

例如把：

```text
供应商须在本地设立固定服务机构
```

改写成多种表达：

```text
要求供应商具备本地服务网点

供应商应在项目所在地设置常驻服务机构

投标人须提供当地服务场所证明
```

作用：

> 扩展语言表达变体。

---

第二类：

# Template Variation
## 模板变体生成

在不改变核心结构的情况下变化：

```text
项目名称
金额
行业
地点
时间
服务范围
```

作用：

> 增加结构分布多样性。

---

第三类：

# Hard Case Generation
## 难例生成

故意生成：

```text
边界条件
相互矛盾条款
隐含限制条件
跨章节依赖
容易误判的负样本
```

作用：

> 增强模型对复杂模式的学习机会。

---

第四类：

# Counterfactual Generation
## 反事实生成

例如从一个风险条款出发：

```text
要求供应商必须在本市注册
```

生成更合理版本：

```text
供应商应根据项目实际需要提供本地化服务能力，但不限制注册地
```

或者反过来：

> 从合理条款生成一个边界风险版本。

作用：

> 学习相似表达之间的细微差异。

---

第五类：

# Structure Synthesis
## 结构合成

生成：

```text
完整采购需求章节
评分表
合同条款组合
长文档章节衔接
```

作用：

> 补足长结构训练分布。

---

# 五、核心心智模型 ②：Synthetic Diversity 不等于 Real-world Diversity

LLM 很容易生成：

> 看起来很多样的文本。

但底层可能仍然高度同质。

例如生成 10 万条：

```text
不同项目名
不同金额
不同地点
```

表面差异很大。

但句式可能几乎都一样：

```text
供应商应……
投标人须……
采购人要求……
```

所以：

\[
\boxed{
SurfaceDiversity
\neq
DistributionDiversity
}
\]

真正应该看：

```text
语法结构
业务逻辑
行业分布
长度分布
难度分布
错误类型
推理路径
文档结构
```

是否真的扩展。

---

# 六、Teacher Generation：教师模型生成到底是什么？

可以用更强模型作为：

# Teacher Model
## 教师模型

生成合成数据。

流程：

```text
Seed Data
真实种子样本
↓
Teacher Prompt
教师生成指令
↓
Teacher Model
高能力模型
↓
Synthetic Candidates
候选合成数据
↓
Rule / Model Filter
规则和模型过滤
↓
Human Audit
人工抽检
↓
Approved Synthetic Set
通过审核的数据集
```

注意：

\[
\boxed{
TeacherOutput
\neq
GroundTruth
}
\]

教师模型同样会：

```text
幻觉
编造
过度规范化
重复自己的风格
复制训练偏差
```

所以 Teacher 只是：

> 候选数据生成器。

不是：

> 事实权威。

---

# 七、核心心智模型 ③：Synthetic Pipeline 必须有 Validator，不能“生成即训练”

这是非常重要的工程边界。

错误流程：

```text
LLM Generate
↓
直接进CPT
```

正确流程：

```text
Generate
生成候选
↓
Schema Check
结构检查
↓
Rule Validation
规则验证
↓
Dedup
去重
↓
Consistency Check
一致性检查
↓
Source / Evidence Check
来源或证据核验
↓
Human Sampling Audit
人工抽样审核
↓
Training Eligible
获得训练资格
```

所以：

\[
\boxed{
Generated
\neq
TrainingEligible
}
\]

这和第 2 阶段的：

\[
AvailableData
\neq
TrainingEligibleData
\]

是一脉相承的。

---

# 八、事实型 Synthetic Data 为什么特别危险？

如果让模型直接生成：

```text
某政策具体规定
某法规具体条款
某项目真实事实
```

很容易出现：

> 看起来非常专业，但实际上不存在。

所以事实型合成数据应该优先采用：

```text
Grounded Generation
基于真实来源生成

Retrieval-grounded Synthesis
基于检索证据合成

Rule-conditioned Generation
基于明确规则约束生成
```

而不是：

> 让模型自由发挥。

所以：

\[
\boxed{
FactSynthesis
必须有
ExternalGrounding
}
\]

---

# 九、Synthetic Data 的来源血缘必须单独记录

每条合成数据至少要知道：

```text
synthetic_id

teacher_model

teacher_version

prompt_version

seed_document_id

source_evidence

generation_temperature

generation_timestamp

validation_status

human_review_status
```

因为合成数据也是：

# Derived Data
## 派生数据

必须能够追溯：

> 它从哪里来、谁生成、基于什么、是否验证。

所以：

\[
\boxed{
SyntheticData
必须有Lineage
}
\]

---

# 十、核心心智模型 ④：Synthetic Data 可以扩展“组合空间”，但不能自动扩展“事实世界”

这条非常关键。

假设真实数据中已有：

```text
行业A
金额区间B
风险类型C
文档结构D
```

合成数据可以把这些元素重新组合：

```text
A + B + C
A + D
B + C + D
```

从而扩大：

> 组合覆盖。

但如果真实世界里根本没有某个规则事实，

模型不能凭空可靠创造。

所以：

\[
\boxed{
SyntheticData
擅长
CombinatorialExpansion
}
\]

不擅长：

\[
\boxed{
AuthoritativeFactCreation
}
\]

---

# 十一、Model Collapse Risk：为什么模型训练太多合成数据会越来越“像模型”？

如果模型大量训练在：

> 其他模型生成的数据上，

而真实数据比例越来越低，

可能出现：

# Model Collapse
## 模型坍缩风险

直觉上：

> 模型开始不断学习模型自己偏好的表达和分布。

结果可能是：

```text
语言更规整
真实噪声减少
罕见表达消失
边缘模式丢失
风格趋同
```

所以：

\[
\boxed{
SyntheticDominance
可能导致
DistributionNarrowing
}
\]

这和我们的目标：

> 扩展覆盖

恰好相反。

---

# 十二、核心心智模型 ⑤：Synthetic Data 比例应该受上限约束

不能因为合成数据便宜，

就让它无限增长。

Data Mixture 中应该单独记录：

```text
real_token_share

synthetic_token_share

synthetic_by_type

synthetic_by_teacher

synthetic_by_quality
```

并设置：

# Synthetic Share Cap
## 合成数据占比上限

具体上限：

> 没有统一标准答案。

必须通过：

```text
真实验证集
领域Benchmark
通用回归
分布分析
Ablation
```

共同确定。

所以：

\[
\boxed{
CheapData
\neq
UnlimitedData
}
\]

---

# 十三、Curriculum Learning：为什么训练顺序本身也会影响学习？

现在进入第二个主题：

# Curriculum Learning
## 课程式学习

它不是：

> 把数据混在一起随机训练。

而是：

> **按照难度、结构或目标阶段安排训练顺序。**

例如：

```text
Phase 1
高质量、短、清晰文本

Phase 2
标准采购文件

Phase 3
长文档、多章节

Phase 4
复杂行业专项

Phase 5
高难、边界、反事实样本
```

这类似：

> 人类先学基础，再学复杂问题。

---

# 十四、核心心智模型 ⑥：Mixture 决定“每阶段吃什么”，Curriculum 决定“什么时候吃什么”

第 5 阶段已经讲过：

# Mixture
## 数据混合

关注：

\[
\boxed{
WithinStageDistribution
}
\]

即：

> 同一训练阶段不同数据各占多少。

而 Curriculum 关注：

\[
\boxed{
AcrossStageSchedule
}
\]

即：

> 不同训练阶段的数据难度和分布怎样变化。

所以：

\[
\boxed{
Mixture
\neq
Curriculum
}
\]

---

# 十五、Curriculum 的“难度”到底怎么定义？

难度不能只看：

> 文档长不长。

还可以从多个维度定义：

```text
Length Difficulty
长度难度

Structural Difficulty
结构复杂度

Semantic Difficulty
语义难度

Reasoning Difficulty
推理难度

Domain Rarity
领域稀有度

Noise Level
噪声程度

Cross-section Dependency
跨章节依赖
```

例如：

```text
简单：
单一条款、短文本、明确语义

中等：
多条件条款、行业术语

困难：
跨章节、隐含约束、矛盾信息、边界情形
```

因此：

\[
\boxed{
Difficulty
=
MultiDimensional
}
\]

---

# 十六、Progressive Curriculum：从简单到复杂

一种常见策略：

# Progressive Curriculum
## 递进式课程

```text
Stage A
基础领域语言

Stage B
标准文档结构

Stage C
长文档和跨章节

Stage D
行业专项

Stage E
难例与边界案例
```

优势：

> 让模型先稳定建立领域分布，再逐步接触复杂结构。

但也不能机械认为：

\[
EasyToHard
=
AlwaysBest
\]

有些模型可能已经具备足够通用能力，

过多简单数据反而浪费训练预算。

---

# 十七、Anti-Curriculum / Mixed Difficulty：为什么有时需要混合难度？

如果训练长期只从简单到难，

模型可能：

> 在进入高难阶段时忘掉简单分布。

所以一种策略是：

```text
高难数据逐步增加

但始终保留部分基础数据
```

这可以理解成：

# Mixed Curriculum
## 混合式课程

即：

> 难度逐步提升，但基础分布不完全退出。

所以：

\[
\boxed{
Curriculum
也需要Retention
}
\]

---

# 十八、核心心智模型 ⑦：Curriculum 是训练分布随时间变化的 Policy

可以把第 \(t\) 个训练阶段的数据分布写成：

\[
P_t(D)
\]

Curriculum 本质上是：

\[
\boxed{
P_1(D)
\rightarrow
P_2(D)
\rightarrow
...
\rightarrow
P_T(D)
}
\]

也就是：

> 训练分布随时间有计划地变化。

所以它必须版本化：

```text
curriculum_phase

phase_start_tokens

phase_end_tokens

difficulty_mix

synthetic_share

replay_share

transition_rule
```

而不是：

> “前面简单一点，后面难一点。”

---

# 十九、Synthetic Hard Case：难例生成为什么特别有价值？

真实世界中的真正难例通常：

```text
少
贵
标注慢
覆盖不均
```

这时合成数据很适合：

# Hard Case Expansion
## 难例扩展

例如围绕真实风险条款生成：

```text
近似但无风险的负例

轻微改动后有风险的正例

多条件组合

语义相似但法律效果不同

跨章节冲突
```

这种合成方式比：

> 纯自由生成采购文本

更有价值。

因为目标清晰：

\[
\boxed{
ExpandDecisionBoundary
}
\]

即：

> 扩展模型在决策边界附近的训练密度。

---

# 二十、核心心智模型 ⑧：Synthetic Hard Case 的价值在“边界密度”，不是“数量”

如果随机生成 100 万条很简单的采购文本，

可能不如：

> 1 万条高质量边界难例。

所以：

\[
\boxed{
HardCaseValue
\propto
BoundaryInformation
}
\]

而不是：

\[
\boxed{
RawCount
}
\]

这和机器学习里：

> 决策边界附近样本信息量更高

是一致的。

---

# 二十一、Synthetic Data 也必须做 Dedup

LLM 非常容易生成：

> 高度相似文本。

即使表面词汇变化，

结构可能几乎一样。

所以仍然要做：

```text
Exact Dedup
完全重复去重

Near Dedup
近似重复去重

Semantic Cluster
语义聚类

Template Similarity
模板相似度分析
```

否则：

> 合成数据会制造新的“假大数据”。

所以：

\[
\boxed{
SyntheticGeneration
后面仍然需要
Deduplication
}
\]

---

# 二十二、Synthetic Benchmark Leakage：合成数据也会污染测试集

如果 Teacher 生成时：

```text
直接看到Benchmark题目
```

然后生成很多改写版本，

这些数据进入 CPT，

依然属于：

> Benchmark Contamination。

所以 Synthetic Pipeline 同样必须经过：

```text
Benchmark Registry

Exact Match

Near Match

Semantic Similarity

Same Seed Check

Lineage Check
```

所以：

\[
\boxed{
Synthetic
\neq
LeakageSafe
}
\]

---

# 二十三、Human Validation：什么情况下必须人工复核？

并不是每条都要人工审核。

但这些类型应该优先提高人工审核比例：

```text
事实型合成

法规解释

高风险判断

复杂反事实

跨章节难例

Teacher之间冲突样本

高曝光合成桶
```

可以采用：

```text
Risk-based Human Sampling
基于风险的人工抽样
```

即：

> 风险越高、训练权重越大，人工审核越严格。

---

# 二十四、Synthetic Quality Score：可以怎样做质量分层？

可以概念化成：

\[
Q_{syn}
=
f(
Validity,
Grounding,
Diversity,
Difficulty,
Consistency
)
\]

其中：

```text
Validity
格式和规则有效性

Grounding
是否有真实依据

Diversity
是否提供新分布

Difficulty
是否真有难度

Consistency
内部逻辑是否一致
```

再分成：

```text
Gold-like Synthetic
高质量合成

Standard Synthetic
标准合成

Low-confidence Synthetic
低置信合成
```

不同等级使用不同：

> Sampling Weight。

---

# 二十五、Synthetic Data 和 SFT Synthetic Data 有什么区别？

这点必须分清。

CPT Synthetic Data 主要目标是：

> 扩展领域语言和分布。

所以更像：

```text
文档
条款
章节
行业语料
长文本
```

而 SFT Synthetic Data 主要目标是：

> 教模型任务行为。

更像：

```text
Instruction
Response
JSON输出
理由
拒答
工具选择
```

所以：

\[
\boxed{
SyntheticCPTData
\neq
SyntheticSFTData
}
\]

二者数据结构和目标完全不同。

---

# 二十六、本阶段正式工程产物：`ProcurementCPTSyntheticCurriculumPolicy_V0.1`

第一版至少锁定：

```text
synthetic_policy_version

coverage_gap_definition

synthetic_use_cases

teacher_model

teacher_version

prompt_version

seed_data_policy

source_grounding_required

generation_temperature

generation_count

synthetic_type

hard_case_policy

counterfactual_policy

synthetic_dedup_policy

synthetic_quality_score

human_review_policy

benchmark_firewall

synthetic_share_cap

real_synthetic_mix

curriculum_enabled

curriculum_phases

difficulty_definition

phase_transition_rule

replay_share_by_phase

synthetic_share_by_phase

ablation_plan

release_gate

trace_logging
=
enabled
```

每条 Synthetic Sample 至少记录：

```text
synthetic_id

teacher_model

teacher_version

prompt_version

seed_id

source_evidence

synthetic_type

difficulty_level

quality_score

validation_status

human_review_status

benchmark_blocked

training_eligible
```

---

# 二十七、本阶段最重要的 8 个核心心智模型

> **心智模型 ①：`SyntheticData ≠ FreeNewKnowledge`。合成数据能扩展表达和组合覆盖，但不能凭空创造可靠事实。**

> **心智模型 ②：`SyntheticGeneration 必须由 CoverageGap 驱动`。先发现真实语料缺口，再生成，不做无目标数据膨胀。**

> **心智模型 ③：`SurfaceDiversity ≠ DistributionDiversity`。句子看起来不同，不代表训练分布真的扩展。**

> **心智模型 ④：`Generated ≠ TrainingEligible`。合成数据必须经过验证、去重、证据检查和风险审核才能进入训练。**

> **心智模型 ⑤：`TeacherModel ≠ GroundTruth`。教师模型是候选数据生成器，不是事实权威。**

> **心智模型 ⑥：`SyntheticShare 必须受控`。合成数据过多会稀释真实世界分布，并增加 Model Collapse 风险。**

> **心智模型 ⑦：`Mixture ≠ Curriculum`。Mixture 控制同一阶段的数据比例，Curriculum 控制训练分布如何随阶段变化。**

> **心智模型 ⑧：`HardCaseValue ∝ BoundaryInformation`。合成难例的价值在决策边界信息密度，不在原始数量。**

---

# 二十八、把完整 Synthetic + Curriculum 流程压成一张专业工程图

```text
                      Real CPT Corpus
                        真实领域语料
                              │
                              ▼
                       Coverage Analysis
                         分析覆盖缺口
                              │
                              ▼
                       Gap Definition
                      定义需要补的分布
                              │
                              ▼
                     Synthetic Generation
                  教师模型生成候选数据
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
            Paraphrase     Hard Case    Counterfactual
              改写          难例          反事实
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                        Validation
                规则 / 证据 / 一致性验证
                              │
                              ▼
                      Dedup + Firewall
                 去重 + Benchmark隔离
                              │
                              ▼
                      Quality Scoring
                        合成质量评分
                              │
                              ▼
                       Mixture Control
                  控制真实/合成数据比例
                              │
                              ▼
                     Curriculum Schedule
                   按难度设计训练阶段
                              │
                              ▼
                    Phase-wise Training
                       分阶段继续预训练
                              │
                              ▼
                 Domain + Regression Eval
                   领域与通用能力评测
                              │
                              ▼
                    Rebalance / Reject
                      调整比例或淘汰
```

脑中最后只留一句：

> **Synthetic Data 的专业价值不是“便宜地把数据做大”，而是针对真实 Corpus 的明确覆盖缺口，用可追溯、可验证、可去重、可控比例的合成样本扩展训练分布，并通过 Curriculum 把这些数据按难度和阶段有计划地送进模型。**

---

# 第八课 · 第 8 阶段掌握测试

现在不回看正文，你应该能够解释：为什么 Synthetic Data 不等于免费新知识；为什么合成前必须先做 Coverage Gap 分析；Paraphrase、Template Variation、Hard Case、Counterfactual 和 Structure Synthesis 分别解决什么问题；为什么 Surface Diversity 不等于 Distribution Diversity；Teacher Model 为什么不是 Ground Truth；为什么 Generated Data 不能直接进入训练；事实型 Synthetic Data 为什么需要 Grounding；为什么 Synthetic Data 必须记录 Lineage；什么是 Model Collapse 风险；为什么合成数据必须设置占比上限；Mixture 和 Curriculum 有什么区别；Difficulty 为什么是多维的；Progressive Curriculum 和 Mixed Curriculum 有什么差别；为什么 Hard Case 的价值在决策边界信息量；为什么合成数据仍要做 Dedup 和 Benchmark Firewall；什么情况下应该加强人工审核；Synthetic CPT Data 和 Synthetic SFT Data 为什么不能混为一谈；以及为什么 Synthetic + Curriculum 最终必须和领域评测、通用回归一起闭环。

如果这些能够完整讲出来：

\[
\boxed{
第八课第8阶段真正掌握
}
\]

---

# 下一阶段：第八课 · 第 9 阶段
# CPT vs SFT：什么时候继续预训练，什么时候监督微调，怎样正确串联？
## 两者都会改 Weight，但一个在学“领域分布”，一个在学“任务行为”；真实项目里怎样判断到底该做哪一个、先做哪一个、做完以后怎样评测？

下一阶段会正式进入：

```text
CPT vs SFT
继续预训练与监督微调

Domain Gap
领域分布差距

Behavior Gap
任务行为差距

Training Order
训练顺序

Base → CPT → SFT
基础模型 → 继续预训练 → 监督微调

SFT after CPT
CPT后重新对齐

Adapter Compatibility
适配器兼容

Evaluation Separation
分层评测

Decision Matrix
技术路线决策矩阵

Go / No-Go Gate
是否进入CPT或SFT
```

并建立：

# `ProcurementCPTSFTDecisionPolicy_V0.1`

下一阶段最关键的一条边界会是：

\[
\boxed{
DomainGap
\neq
BehaviorGap
}
\]

也就是说：

> **模型“不够懂采购”和“模型不会按要求做采购任务”，是两种不同的问题。**

---
