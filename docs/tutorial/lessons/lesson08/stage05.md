# 第八课 · 第 5 阶段
# Data Mixture & Sampling：领域语料比例、质量权重、重复控制与采样策略
## Corpus 已经干净了，Sequence 也构造好了，但不同类型语料到底各训练多少？为什么 10 倍数据量并不意味着应该获得 10 倍训练权重？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **CorpusShare ≠ TrainingShare。原始数据占比只是“你有什么”，训练占比才决定“模型实际看什么”。**
2. **SamplingPolicy = GradientAllocationPolicy。采样策略本质上是在给不同能力分配训练梯度。**
3. **Oversampling = SignalAmplification + DuplicateExposure。过采样能强化稀有能力，也会放大重复和过拟合风险。**
4. **SameTrainingShare ≠ SameExposure。同样的训练占比，对不同大小的 Unique Token Pool 会产生完全不同的重复曝光。**
5. **Eligibility ≠ Priority。Filter 决定能不能训练，Weight 决定有资格的数据训练多频繁。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `CPT` | CPT/继续预训练：在领域语料上继续执行预训练目标 |
| `Data Mixture` | 数据混合：控制通用语料和领域语料等来源比例 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Temperature` | 温度：控制采样分布平滑程度和随机性 |
| `Alpha` | LoRA Alpha：控制低秩更新缩放幅度 |
| `Loss` | 损失函数：把预测错误压缩成可优化的数值信号 |

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

到第 4 阶段，我们已经把 CPT 的训练链条建立到：

\[
\boxed{
Corpus
\rightarrow
Tokenizer
\rightarrow
SequenceConstruction
\rightarrow
Loss
}
\]

但现在还有一个决定模型最终能力分布的问题：

> **不同类型的数据，训练时到底各出现多少次？**

假设我们的 CPT Corpus 中有：

```text
法规与规范文件
5B tokens

采购文件
30B tokens

公告
40B tokens

合同与履约
8B tokens

医疗采购
4B tokens

工程采购
3B tokens

高质量政策解读
1B tokens
```

最简单的做法是：

> 按原始 Token 占比直接训练。

但这往往不是最专业的做法。

因为：

\[
\boxed{
CorpusShare
\neq
TrainingShare
}
\]

某类数据在磁盘里占 40%，

不代表它就应该贡献：

> 40% 的训练梯度。

所以本阶段最终形成：

# `ProcurementCPTMixturePolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

CPT 的 Data Mixture 不是：

> **“把所有语料混在一起然后随机抽。”**

更准确地说：

\[
\boxed{
TrainingDistribution
=
DesignedDistribution
}
\]

也就是说：

> **模型最终更像什么，不只由你收集了什么数据决定，也由训练时哪些数据被看了多少次决定。**

因此：

\[
\boxed{
SamplingPolicy
=
GradientAllocationPolicy
}
\]

翻译成人话：

> 采样策略本质上是在决定训练梯度被分配到哪些数据分布上。

---

# 二、核心心智模型 ①：Corpus Share 不等于 Training Share

假设原始 Corpus：

```text
公告类文本
50%

采购文件
25%

法规
10%

合同履约
8%

行业专项
5%

高质量解释文本
2%
```

如果直接按自然比例采样，

训练时：

```text
50%的Token
都来自公告
```

模型会大量学习：

> 公告语言。

但我们的目标可能是：

```text
理解采购文件结构
理解资格条件
理解评分办法
理解合同和履约
保持法规语言能力
```

于是：

\[
\boxed{
NaturalDistribution
\neq
TargetCapabilityDistribution
}
\]

所以 Data Mixture 的第一步不是：

> “统计数据占比。”

而是：

> **先定义目标能力，再设计训练占比。**

---

# 三、Data Mixture 的完整工程流程

英文流程：

```text
Corpus Inventory
↓
Capability Mapping
↓
Source Bucketing
↓
Raw Token Share
↓
Quality Scoring
↓
Target Mixture Design
↓
Sampling Weight Calculation
↓
Exposure Simulation
↓
Train-time Sampling
↓
Mixture Monitoring
↓
Evaluation & Rebalance
```

中文解释：

```text
盘点所有语料
↓
映射每类语料支持什么能力
↓
把语料按来源 / 类型 / 行业分桶
↓
计算原始Token占比
↓
评估每桶数据质量
↓
设计目标训练比例
↓
计算采样权重
↓
训练前模拟每类数据会被看多少次
↓
按权重进入训练
↓
训练中监控真实混合比例
↓
根据评测结果重新平衡
```

最关键的是：

\[
\boxed{
MixtureDesign
发生在训练之前
}
\]

而不是：

> 训练完以后才发现模型偏科。

---

# 四、核心心智模型 ②：Sampling Weight 是“训练曝光权”，不是“数据重要性标签”

假设：

```text
法规
Raw Share = 5%

Target Training Share = 15%
```

这不意味着：

> 法规“比采购文件重要三倍”。

它只意味着：

> 在这次训练目标下，我们希望法规类 Token 获得更多曝光。

所以：

\[
\boxed{
SamplingWeight
\neq
IntrinsicImportance
}
\]

它只是当前 Experiment 的：

> **Exposure Allocation。**

不同版本的模型，

目标不同，

Sampling Weight 也可以不同。

---

# 五、最简单的采样权重怎样定义？

假设有 \(K\) 个数据桶：

\[
D_1,D_2,\dots,D_K
\]

每个桶目标采样概率：

\[
p_i
\]

满足：

\[
\sum_{i=1}^{K}p_i=1
\]

训练时每次选择一个数据桶：

\[
D_i\sim p
\]

然后从该桶里抽样本。

这就是：

# Weighted Sampling
## 加权采样

如果目标比例是：

```text
法规 15%
采购文件 35%
公告 20%
合同履约 10%
行业专项 15%
解释文本 5%
```

那么训练的真实数据流应该尽量接近：

> 这套目标分布。

---

# 六、Natural Sampling：按原始数据量采样什么时候有问题？

自然采样可以概念化为：

\[
p_i
=
\frac{N_i}{\sum_jN_j}
\]

其中：

\[
N_i
=
第i类数据的Token数
\]

优点：

> 简单、自然、不会人为放大稀有桶。

但缺点是：

> 大数据桶会完全主导梯度。

例如公告有：

```text
40B tokens
```

法规只有：

```text
4B tokens
```

那么自然采样下公告曝光约 10 倍。

如果公告高度模板化，

你实际上可能在训练：

> “公告语言模型”。

而不是：

> “政府采购领域模型”。

所以：

\[
\boxed{
RawVolume
可能放大
LowValueDistribution
}
\]

---

# 七、Temperature Sampling：为什么要“压平”大数据桶？

一种常见思路是：

# Temperature Sampling
## 温度采样

概念上：

\[
p_i
\propto
N_i^\alpha
\]

其中：

\[
0<\alpha\leq1
\]

当：

\[
\alpha=1
\]

就是自然采样。

当：

\[
\alpha<1
\]

大数据桶的优势会被压缩，

小数据桶相对获得更多曝光。

例如：

```text
公告
40B

法规
4B
```

原始规模相差：

\[
10\times
\]

经过温度变换以后，

训练曝光差距可以显著缩小。

核心不是记公式。

而是理解：

\[
\boxed{
TemperatureSampling
=
ReduceSizeDominance
}
\]

即：

> 降低“谁数据多谁统治训练”的现象。

---

# 八、核心心智模型 ③：Oversampling 会放大信号，也会放大重复

如果一个高质量小桶只有：

```text
500M tokens
```

但我们希望它贡献：

```text
10%的训练Token
```

它可能会被反复抽到很多次。

这叫：

# Oversampling
## 过采样

好处：

> 让稀有但重要能力获得足够训练曝光。

风险：

```text
同一文档被重复看到
固定表达被过度记忆
小桶更容易过拟合
Benchmark近似样本风险被放大
```

所以：

\[
\boxed{
Oversampling
=
SignalAmplification
+
DuplicateExposure
}
\]

不能只看：

> “这个桶很重要，所以多抽。”

还要看：

> 它到底能承受多少重复曝光。

---

# 九、Exposure：专业分析必须看“看过多少次”，不能只看采样比例

假设某一桶：

```text
Corpus Size
=
1B tokens
```

训练过程中从该桶累计抽取：

```text
5B tokens
```

可以说：

> 平均 Token Exposure 约为 5 次。

概念化：

\[
Exposure_i
=
\frac{SampledTokens_i}{UniqueTokens_i}
\]

这不是严格等同于传统 Epoch，

因为：

```text
随机采样
Packing
长文档切分
去重策略
```

会让实际曝光更复杂。

但它是非常重要的工程直觉：

\[
\boxed{
TrainingShare
+
CorpusSize
\Rightarrow
Exposure
}
\]

同样 10% Training Share，

对 100M Token 小桶和 10B Token 大桶：

> 重复强度完全不同。

---

# 十、核心心智模型 ④：Training Share 必须和 Unique Token Pool 一起看

假设：

```text
法规桶
1B unique tokens
训练占比15%

公告桶
20B unique tokens
训练占比20%
```

如果总训练量是：

```text
100B tokens
```

那么法规桶大约被抽：

```text
15B tokens
```

平均曝光约：

\[
15\times
\]

公告桶被抽：

```text
20B tokens
```

平均曝光约：

\[
1\times
\]

所以：

\[
\boxed{
SameTrainingShare
\neq
SameExposure
}
\]

这条极其重要。

Data Mixture 设计时至少同时看：

```text
Target Training Share
Unique Token Pool
Expected Exposure
```

---

# 十一、Quality Weighting：高质量数据应该获得更多权重吗？

通常：

> 可以考虑。

但不能简单写成：

```text
高质量
→ 10倍权重
```

更合理的做法是：

```text
先按Source / Type分桶

再给每桶做质量分层

High Quality
高质量

Medium Quality
中等质量

Low Quality
低质量
```

然后：

```text
Low Quality
→ Remove / Downsample

Medium Quality
→ Normal Sampling

High Quality
→ Normal / Mild Upsampling
```

所以：

\[
\boxed{
QualityWeighting
应该先Filter
再Reweight
}
\]

坏数据不应该靠：

> “低一点权重”

就无限保留。

---

# 十二、核心心智模型 ⑤：Filter 和 Weight 是两种不同工具

# Filter
## 过滤

回答：

> 这条数据有没有训练资格？

# Weight
## 权重

回答：

> 有资格的数据，训练时应该出现多频繁？

所以：

\[
\boxed{
Eligibility
\neq
Priority
}
\]

先判断：

\[
Eligible?
\]

再判断：

\[
HowOften?
\]

如果把这两步混在一起，

容易出现：

> 明明应该删除的低质数据，只是被“降权”保留。

---

# 十三、Domain Balance：行业平衡不能只看行业 Token 数

假设行业 Corpus：

```text
IT采购
10B

医疗
2B

工程
1B

物业
1B

检测
0.5B
```

自然采样一定会让 IT 主导。

但是否应该完全均匀成：

```text
每个行业20%
```

也不一定。

因为：

```text
真实业务量不同
语言复杂度不同
目标用户分布不同
行业风险不同
```

所以 Domain Balance 应该综合：

\[
\boxed{
BusinessImportance
+
DataQuality
+
CoverageGap
+
CorpusSize
}
\]

而不是：

> “平均分”。

---

# 十四、Replay Mix：为什么 CPT 里要混入通用语料？

第 1 阶段我们已经知道：

# Catastrophic Forgetting
## 灾难性遗忘

如果训练几乎全部是采购文本，

模型可能：

```text
采购能力上涨
通用能力下降
```

一种重要思路是：

# Replay
## 通用语料回放

即训练时保留一定比例：

```text
高质量通用语言
数学
代码
一般知识
通用指令相关文本
```

作为：

> General Replay Corpus。

于是 Mixture 可能从：

```text
100% Procurement
```

变成：

```text
80% Domain
20% General Replay
```

具体比例不能凭感觉拍脑袋。

但原则是：

\[
\boxed{
DomainGain
需要和
GeneralRetention
共同优化
}
\]

---

# 十五、核心心智模型 ⑥：Replay 不是“浪费领域训练预算”，而是能力保险

直觉上很多人会觉得：

> “既然做 CPT，为什么还要喂模型通用数据？”

因为 CPT 不是只追求：

\[
DomainScore\uparrow
\]

还要控制：

\[
GeneralScore\downarrow
\]

所以目标更像：

\[
\boxed{
MaximizeDomainGain
\quad
SubjectTo
\quad
GeneralRegression\leq Threshold
}
\]

也就是：

> **在通用能力退化不超过允许阈值的前提下，最大化领域收益。**

Replay 是：

> Ability Retention Mechanism。

这一点会在第 6 阶段深入展开。

---

# 十六、Mixture 不是一次设计完就不动

训练初期可能采用：

```text
Domain 70%
Replay 30%
```

中期发现：

```text
领域Loss下降慢
通用能力稳定
```

可能调整：

```text
Domain 80%
Replay 20%
```

反过来，

如果通用能力快速下降：

> 就需要提高 Replay。

所以：

# Dynamic Mixture
## 动态混合

可以根据：

```text
Domain Validation Loss

General Validation Loss

Forgetting Metrics

Target Capability Metrics
```

进行阶段性调整。

但必须注意：

> 动态调整要版本化和可追踪。

不能变成：

> 训练中随手改参数，最后没人知道怎么训出来的。

---

# 十七、Curriculum 和 Mixture 有什么区别？

# Mixture
## 数据混合

回答：

> 同一阶段，不同数据各占多少？

# Curriculum
## 课程式训练

回答：

> 不同训练阶段，数据难度或分布怎样变化？

例如：

```text
阶段A
高质量、通用采购语言

阶段B
复杂专业采购文档

阶段C
高难行业专项文本
```

所以：

\[
\boxed{
Mixture
=
WithinStageDistribution
}
\]

\[
\boxed{
Curriculum
=
AcrossStageSchedule
}
\]

第 8 阶段会专门讲 Synthetic Data & Curriculum。

这里先锁死边界。

---

# 十八、Mixture Drift：配置比例和真实训练比例可能不一样

你配置：

```text
法规
15%
```

不代表真正训练时一定就是：

```text
15%
```

因为：

```text
不同样本长度
Packing
Data Loader行为
过滤
失败重试
Shard不均
分布式Worker
```

都可能造成实际比例偏差。

这叫：

# Mixture Drift
## 混合分布漂移

所以必须记录：

```text
Configured Share
配置比例

Observed Share
实际比例

Token Exposure
真实Token曝光
```

因此：

\[
\boxed{
ConfiguredMixture
\neq
ObservedMixture
}
\]

---

# 十九、核心心智模型 ⑦：按“样本数”采样和按“Token数”采样不是一回事

假设：

```text
公告平均
800 tokens

采购文件平均
20000 tokens
```

如果按文档数：

```text
各抽50%
```

实际 Token 比例可能完全不是：

```text
50% : 50%
```

所以 Data Mixture 必须明确：

```text
Document-level Sampling
按文档采样

Sequence-level Sampling
按训练序列采样

Token-level Target
按Token曝光控制
```

CPT 真正影响梯度的更接近：

> Token / Sequence Exposure。

所以：

\[
\boxed{
SampleShare
\neq
TokenShare
}
\]

---

# 二十、政府采购 CPT 第一版 Mixture 应该怎样设计？

不是直接给一个“标准比例”。

而是建立一张：

# Mixture Design Table
## 数据混合设计表

例如：

| Bucket | 训练目标 | Unique Tokens | 质量 | Target Share | Expected Exposure |
|---|---|---:|---|---:|---:|
| 法规规范 | 规则语言 | 2B | 高 | 10% | 5x |
| 采购文件 | 文件结构与条款 | 12B | 高 | 30% | 2.5x |
| 公告 | 生命周期表达 | 20B | 中高 | 15% | 0.75x |
| 合同履约 | 后半程能力 | 5B | 高 | 10% | 2x |
| 行业专项 | 行业覆盖 | 6B | 高 | 15% | 2.5x |
| 解释文本 | 概念连接 | 1B | 很高 | 5% | 5x |
| General Replay | 通用能力保持 | 15B | 高 | 15% | 1x |

这里的比例只是：

> **设计示例。**

不是本课程给出的固定生产配方。

真正比例必须通过：

```text
Ablation
消融实验

Domain Eval
领域评测

General Regression
通用能力回归

Exposure Analysis
曝光分析
```

共同确定。

---

# 二十一、Ablation：为什么 Mixture 需要实验，而不是专家拍比例？

假设有三种方案：

```text
Mix A
90% Domain / 10% Replay

Mix B
80% Domain / 20% Replay

Mix C
70% Domain / 30% Replay
```

分别做小规模 Pilot Run：

```text
固定Base Model
固定Tokenizer
固定Corpus Version
固定Token Budget
只改变Mixture
```

然后比较：

```text
Domain PPL

Domain Probe

Downstream SFT Result

General Regression

Training Stability
```

这样：

\[
\boxed{
MixtureDecision
来自
ControlledExperiment
}
\]

不是：

> “20% Replay 听起来差不多。”

---

# 二十二、训练预算固定时，Mixture 本质上是在做资源分配

假设总 CPT Budget：

\[
B=100B\ tokens
\]

那么：

\[
B_i
=
p_iB
\]

每个数据桶获得：

> 一个固定的训练 Token 预算。

所以：

\[
\boxed{
MixtureDesign
=
TrainingBudgetAllocation
}
\]

换句话说：

> 给法规多 5B Token，就意味着别的桶少 5B Token。

Data Mixture 是：

> **有限训练预算下的能力投资组合。**

---

# 二十三、本阶段正式工程产物：`ProcurementCPTMixturePolicy_V0.1`

第一版至少锁定：

```text
mixture_policy_version

bucket_schema

bucket_definition

capability_mapping

unique_token_count

raw_corpus_share

quality_level

target_training_share

sampling_method

temperature_alpha

oversampling_limit

undersampling_policy

expected_exposure

max_exposure

general_replay_share

replay_source

document_sampling_policy

sequence_sampling_policy

token_share_target

configured_share

observed_share

mixture_drift_threshold

ablation_plan

rebalance_trigger

trace_logging
=
enabled
```

每次训练至少记录：

```text
run_id

bucket_id

configured_sampling_weight

sampled_documents

sampled_sequences

sampled_tokens

unique_tokens

estimated_exposure

observed_token_share

quality_distribution

replay_share

mixture_adjustment

adjustment_reason
```

这样以后才能回答：

> **这个模型到底是被什么数据分布训练出来的？**

---

# 二十四、本阶段最重要的 8 个核心心智模型

> **心智模型 ①：`CorpusShare ≠ TrainingShare`。原始数据占比只是“你有什么”，训练占比才决定“模型实际看什么”。**

> **心智模型 ②：`SamplingPolicy = GradientAllocationPolicy`。采样策略本质上是在给不同能力分配训练梯度。**

> **心智模型 ③：`Oversampling = SignalAmplification + DuplicateExposure`。过采样能强化稀有能力，也会放大重复和过拟合风险。**

> **心智模型 ④：`SameTrainingShare ≠ SameExposure`。同样的训练占比，对不同大小的 Unique Token Pool 会产生完全不同的重复曝光。**

> **心智模型 ⑤：`Eligibility ≠ Priority`。Filter 决定能不能训练，Weight 决定有资格的数据训练多频繁。**

> **心智模型 ⑥：`Replay ≠ Waste`。通用语料回放不是浪费 CPT 预算，而是在为通用能力做保险。**

> **心智模型 ⑦：`ConfiguredMixture ≠ ObservedMixture`。真正训练分布必须从 Data Loader 和 Token Exposure 实测，而不能只看配置文件。**

> **心智模型 ⑧：`MixtureDesign = TrainingBudgetAllocation`。总 Token Budget 固定时，每提高一类数据的训练份额，都意味着减少另一类数据的训练资源。**

---

# 二十五、把完整 Data Mixture 流程压成一张专业工程图

```text
                       CPT Corpus
                    已治理领域语料
                          │
                          ▼
                    Bucketization
                 按来源/类型/行业分桶
                          │
                          ▼
                  Capability Mapping
               映射每桶支持哪些能力
                          │
                          ▼
                    Corpus Statistics
          统计Unique Tokens / Raw Share / Quality
                          │
                          ▼
                  Target Mixture Design
                  设计目标训练分布
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
        Quality Weight  Domain Balance  General Replay
          质量权重        领域平衡        通用回放
            │             │             │
            └─────────────┼─────────────┘
                          ▼
                  Sampling Weights
                    计算采样权重
                          │
                          ▼
                 Exposure Simulation
              训练前模拟重复曝光强度
                          │
                          ▼
                    Train-time Sampler
                     训练时真实采样
                          │
                          ▼
                   Observed Mixture
                 统计真实Token占比
                          │
                          ▼
              Domain + General Evaluation
                 领域与通用能力评测
                          │
                          ▼
                    Rebalance / Lock
                     调整或冻结比例
```

脑中最后只留一句：

> **Data Mixture 的本质不是“把各种数据搅在一起”，而是在有限 Token Budget 下，主动决定不同领域、不同质量和通用回放数据分别获得多少训练曝光，从而设计模型最终的能力分布。**

---

# 第八课 · 第 5 阶段掌握测试

现在不回看正文，你应该能够解释：为什么 Corpus Share 不等于 Training Share；为什么 Sampling Policy 本质上是 Gradient Allocation Policy；Weighted Sampling 的基本逻辑是什么；Natural Sampling 为什么容易让大数据桶统治训练；Temperature Sampling 怎样压缩规模差距；Oversampling 为什么同时强化信号和重复风险；Exposure 为什么比单纯 Training Share 更重要；为什么同样 10% Training Share 在大小不同的数据桶上会产生不同曝光；Quality Filter 和 Quality Weight 有什么区别；为什么行业平衡不能简单平均分；Replay Mix 为什么能帮助保持通用能力；为什么 Replay 不等于浪费领域训练预算；Mixture 和 Curriculum 有什么区别；Mixture Drift 为什么会发生；为什么文档占比和 Token 占比不是一回事；Mixture Design Table 应该记录哪些信息；为什么比例必须通过 Ablation 实验验证；以及为什么在固定 Token Budget 下，Data Mixture 本质上就是训练资源分配。

如果这些能够完整讲出来：

\[
\boxed{
第八课第5阶段真正掌握
}
\]

---

# 下一阶段：第八课 · 第 6 阶段
# Catastrophic Forgetting：为什么模型学会领域知识以后，反而可能忘掉原来的能力？
## CPT 的真正难点不是“领域能力能不能涨”，而是“涨了以后有没有把模型其他能力一起弄坏”。

下一阶段会正式进入：

```text
Catastrophic Forgetting
灾难性遗忘

General Capability Regression
通用能力回归

Domain-General Tradeoff
领域-通用权衡

Replay
通用语料回放

Learning Rate
学习率影响

Training Duration
训练时长

Parameter Drift
参数漂移

Capability Retention
能力保持

Forgetting Curve
遗忘曲线

Regression Benchmark
回归测试集
```

并建立：

# `ProcurementCPTForgettingPolicy_V0.1`

下一阶段最重要的一条边界会是：

\[
\boxed{
DomainGain
\neq
NetModelGain
}
\]

也就是说：

> **采购能力涨了 10 分，如果通用能力掉了 20 分，这次 CPT 仍然可能是失败的。**

---
