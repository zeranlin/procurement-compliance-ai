# 第八课 · 第 4 阶段
# CPT Training Objective：Next Token Prediction、Sequence、Context Length 与 Loss
## CPT 明明还是 Next Token Prediction，为什么数据拼接方式、Sequence Length、Packing 和 Loss Masking 会直接改变模型到底在学什么？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **ObjectiveFormula 相同 ≠ LearningContext 相同。Next Token Prediction 的公式没变，但 Sequence 怎样构造会改变模型看到的条件上下文。**
2. **Sequence Boundary = Dependency Boundary。切在哪里，会决定哪些跨段关系能够在一次训练上下文中被直接学习。**
3. **ChooseContextLength ≠ MaxSupportedContext。Context Length 应由任务依赖距离、文档长度分布和计算预算共同决定。**
4. **Attention Mask ≠ Loss Mask。前者控制能看什么，后者控制哪里算损失，这是两套完全不同的机制。**
5. **TruncationPolicy = ImplicitSamplingPolicy。截断不是简单裁长度，而是在重新定义哪些文档区域更常进入训练。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Token` | Token：模型实际处理的离散文本单元 |
| `Loss` | 损失函数：把预测错误压缩成可优化的数值信号 |
| `CPT` | CPT/继续预训练：在领域语料上继续执行预训练目标 |
| `Loss Mask` | 损失掩码：指定哪些 Token 参与训练 Loss |
| `Next Token Prediction` | 下一 Token 预测：大语言模型预训练核心目标 |
| `Attention` | 注意力：根据内容相关性动态聚合信息 |

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

第 3 阶段我们已经锁定：

\[
\boxed{
Text
\rightarrow
Tokenizer
\rightarrow
TokenIDs
}
\]

现在问题继续往下走。

Tokenizer 已经把采购文本变成：

```text
[1542, 3098, 881, 7712, ...]
```

但这些 Token IDs 还不能直接丢给 GPU。

我们还必须决定：

```text
怎样组成Sequence？
一条Sequence多长？
多个文档能不能拼在一起？
文档边界怎样表示？
哪些Token参与Loss？
长文档截断还是切块？
Padding算不算Loss？
```

这些选择看起来像：

> “数据管道细节”。

实际上它们会直接改变：

> **模型正在解决的学习问题。**

所以本阶段最终形成：

# `ProcurementCPTObjectivePolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

同一份 Corpus，

只要 Sequence 构造方式不同，

模型实际接受的训练任务就已经不同。

\[
\boxed{
SameCorpus
+
DifferentSequenceConstruction
=
DifferentLearningProblem
}
\]

所以 CPT 的训练目标不能只写一句：

```text
Next Token Prediction
```

还必须进一步明确：

```text
Sequence Construction
序列怎样构造

Context Length
每条序列多长

Packing
多个样本怎样拼接

Document Boundary
文档边界怎样表达

Loss Masking
哪些位置参与损失

Truncation
超长文本怎样处理

Sampling
不同长度文档怎样进入训练
```

这些共同决定：

\[
\boxed{
EffectiveTrainingObjective
}
\]

---

# 二、CPT 的数学目标其实没有变

CPT 仍然是：

# Causal Language Modeling
## 因果语言建模

也就是：

> 根据前面的 Token，预测下一个 Token。

对一个 Token 序列：

\[
x_1,x_2,\dots,x_T
\]

模型学习：

\[
p_\theta(x_t|x_{<t})
\]

训练 Loss：

\[
\mathcal{L}
=
-\sum_{t=1}^{T}
\log p_\theta(x_t|x_{<t})
\]

翻译成人话：

```text
前面已经看到：
“供应商应当具有”

模型预测：
下一个Token是什么？
```

然后继续：

```text
“供应商应当具有独立”
→ 预测下一个Token

“供应商应当具有独立承担”
→ 再预测下一个Token
```

所以：

\[
\boxed{
CPT
本质仍然是LanguageModeling
}
\]

变化的不是基本目标，

而是：

> **训练数据分布与 Sequence 组织方式。**

---

# 三、核心心智模型 ①：Objective 不只是公式，还包括“你给模型看什么样的上下文”

很多人看到：

\[
-\log p(x_t|x_{<t})
\]

就觉得：

> “目标函数确定了，剩下都是工程细节。”

这是不够专业的。

因为：

\[
x_{<t}
\]

到底是什么，

完全取决于：

```text
Sequence怎么切
文档是否拼接
上下文长度
是否跨文档
是否包含模板
哪里被截断
```

所以：

\[
\boxed{
ObjectiveFormula
相同
\not\Rightarrow
LearningContext
相同
}
\]

进一步：

> **模型学到的统计关系，取决于你怎样构造它能看到的条件上下文。**

---

# 四、Sequence Construction：原始文档怎样变成训练序列？

假设有一份采购文件：

```text
封面
采购公告
资格条件
采购需求
评分办法
合同条款
附件
```

Tokenize 后有：

```text
18000 tokens
```

而你的训练 Sequence Length 是：

```text
4096
```

那么必须把文档处理成若干训练序列。

最简单：

```text
Sequence 1
Token 1～4096

Sequence 2
Token 4097～8192

Sequence 3
Token 8193～12288

Sequence 4
Token 12289～16384

Sequence 5
剩余Token
```

这叫：

# Chunked Sequential Construction
## 顺序切分构造

但这只是第一种方案。

---

# 五、核心心智模型 ②：Sequence Boundary 会改变模型看到的“关系距离”

假设资格条件在：

```text
Token 3800
```

而评分办法在：

```text
Token 4500
```

如果 Sequence Length 是：

```text
4096
```

这两个内容会被分到：

> 两个训练 Sequence。

模型在这条训练样本里：

> 看不到它们之间的直接上下文关系。

如果 Sequence Length 是：

```text
8192
```

它们可能在同一个上下文里。

所以：

\[
\boxed{
ContextLength
决定
哪些关系能够在一次训练上下文中被直接建模
}
\]

这就是为什么 Context Length 不只是：

> “能装多少字”。

它决定：

> **模型可以学习多远的依赖关系。**

---

# 六、Context Length：长一点一定更好吗？

不一定。

更长 Context 的好处：

```text
完整章节更容易保留

跨章节关系更容易同场出现

长文档结构信息保留更多

减少人为切断
```

但代价包括：

```text
显存压力更大

训练吞吐下降

Attention计算更贵

Batch Size可能变小

短文档需要更多Packing
```

经典 Attention 计算对序列长度通常有近似：

\[
O(L^2)
\]

其中：

\[
L
=
SequenceLength
\]

所以：

\[
\boxed{
LongerContext
\neq
FreeImprovement
}
\]

Context Length 是：

> 能力收益、训练成本与数据分布之间的折中。

---

# 七、核心心智模型 ③：Context Length 应该由“目标依赖距离”决定，而不是越长越专业

专业决策不是：

```text
模型支持128K
→ 就训练128K
```

而应该先问：

```text
采购任务真正需要学习多远的上下文关系？

一份典型采购文件有多长？

风险判断常依赖同一章节还是跨章节？

长文档样本占多少？

预算是否允许？
```

所以：

\[
\boxed{
ChooseContextLength
=
TaskDependencyDistance
+
DocumentLengthDistribution
+
ComputeBudget
}
\]

而不是：

\[
\boxed{
MaxSupportedContext
}
\]

---

# 八、Packing：为什么短文档不应该大量浪费 Padding？

假设 Sequence Length：

```text
4096
```

但某些公告只有：

```text
700 tokens
900 tokens
1200 tokens
```

如果一条文档占一条 Sequence，

剩余位置只能 Padding：

```text
700 real tokens
+
3396 padding tokens
```

大量算力浪费在：

> 无效位置。

所以常用：

# Packing
## 样本拼接

例如：

```text
Document A
700 tokens

<EOS>

Document B
900 tokens

<EOS>

Document C
1200 tokens

<EOS>
```

拼成同一个 4096 Sequence。

这样：

\[
\boxed{
TokenUtilization
提高
}
\]

---

# 九、Packing 的完整流程

英文流程：

```text
Documents
↓
Tokenize
↓
Append EOS
↓
Length-aware Grouping
↓
Pack into Fixed-length Sequences
↓
Attention / Loss Policy
↓
Training Batch
```

中文解释：

```text
多份原始文档
↓
转成Token IDs
↓
每份文档结尾加入EOS
↓
根据长度做组合
↓
尽量填满固定Sequence
↓
明确跨文档Attention和Loss规则
↓
组成训练Batch
```

所以：

\[
\boxed{
Packing
不是简单字符串拼接
}
\]

它涉及：

> 文档边界、Attention 行为与 Loss 语义。

---

# 十、Document Boundary：为什么 EOS 非常重要？

假设直接把两个完全无关文档拼起来：

```text
Document A最后一句
+
Document B第一句
```

如果没有边界，

模型会看到一种虚假的统计关系：

> A 结尾之后天然接 B 开头。

所以需要：

# EOS
## End Of Sequence / 文档结束标记

例如：

```text
Document A
<EOS>
Document B
<EOS>
```

EOS 告诉模型：

> 前一文档结束了。

因此：

\[
\boxed{
DocumentBoundary
必须显式表达
}
\]

否则 Packing 可能制造：

# False Transition
## 虚假文档过渡

---

# 十一、跨文档 Attention 到底要不要允许？

这是更细的工程问题。

在一些标准 causal LM packing 中：

> 后面的文档仍可能 Attention 到前一文档 Token，

只是中间有 EOS。

这通常是可接受的工程实现。

但如果你希望：

> 文档之间完全隔离，

就需要：

# Block-diagonal Attention Mask
## 分块对角注意力掩码

概念上：

```text
Document A
只能看A内部历史

Document B
只能看B内部历史

Document C
只能看C内部历史
```

这能更严格避免跨样本信息串扰，

但实现复杂度更高。

所以：

\[
\boxed{
PackingPolicy
必须明确
CrossDocumentAttention
}
\]

不能默认“拼起来就结束”。

---

# 十二、Loss Masking：不是所有 Token 都应该参与 Loss

训练序列里可能包含：

```text
真实正文Token
EOS
PAD
特殊控制Token
某些结构占位Token
```

一般来说：

# Padding Token
## 填充 Token

不应该参与语言建模 Loss。

可以用：

\[
m_t
\in
\{0,1\}
\]

表示某个位置是否计入 Loss。

于是：

\[
\mathcal{L}
=
-\sum_{t=1}^{T}
m_t
\log p_\theta(x_t|x_{<t})
\]

其中：

```text
m_t = 1
这个Token参与训练损失

m_t = 0
这个Token忽略
```

这就是：

# Loss Mask
## 损失掩码

---

# 十三、核心心智模型 ④：Attention Mask 和 Loss Mask 不是一回事

这两个名字很像，

但作用完全不同。

# Attention Mask
## 注意力掩码

决定：

> 当前 Token 能看哪些历史位置。

# Loss Mask
## 损失掩码

决定：

> 当前 Token 的预测错误要不要计入训练 Loss。

所以：

\[
\boxed{
AttentionMask
\neq
LossMask
}
\]

一个 Token：

> 可以被其他 Token 看见，

但自己不一定参与 Loss。

这是非常重要的底层区别。

---

# 十四、CPT 和 SFT 的 Loss Mask 通常不一样

CPT 典型目标：

> 对绝大多数真实文本 Token 都计算 Next Token Loss。

例如：

```text
采购人应当根据项目特点...
```

基本整段都参与 Loss。

而 SFT 里经常：

```text
User Prompt
→ mask掉Loss

Assistant Response
→ 计算Loss
```

也就是只训练：

> Assistant 的目标回答。

所以：

\[
\boxed{
CPTLossMask
通常更接近FullTextLM
}
\]

而：

\[
\boxed{
SFTLossMask
通常更接近TargetResponseOnly
}
\]

这也是 CPT 和 SFT 的根本区别之一。

---

# 十五、Truncation：超长文档直接截断有什么问题？

假设文档：

```text
50000 tokens
```

训练 Context：

```text
8192
```

如果简单：

```text
只保留前8192 tokens
```

那么模型长期看到的是：

> 文档前半部分。

采购文件通常前面可能是：

```text
公告
须知
资格部分
```

后面则可能是：

```text
技术需求
评分表
合同
附件
```

于是长期训练后：

> Corpus 表面完整，实际后半段系统性缺失。

这叫：

# Truncation Bias
## 截断偏差

---

# 十六、核心心智模型 ⑤：Truncation 是 Sampling Decision，不只是长度处理

一旦你决定：

```text
保留前4096
```

你其实是在提高：

> 文档前部内容的采样概率。

降低：

> 文档后部内容的采样概率。

所以：

\[
\boxed{
TruncationPolicy
=
ImplicitSamplingPolicy
}
\]

更好的长文档策略可能包括：

```text
Sequential Chunking
顺序分块

Random Window Sampling
随机窗口采样

Section-aware Sampling
按章节采样

Importance-aware Sampling
按重要区域采样

Multi-window Sampling
同一长文档抽多个窗口
```

---

# 十七、采购文档为什么特别适合 Section-aware Sampling？

政府采购文档天然有章节结构：

```text
采购公告
供应商须知
资格条件
采购需求
技术参数
评分办法
合同条款
附件
```

如果只是机械按 Token 长度切，

可能把：

```text
一个评分项
```

从中间切断。

Section-aware 的思路是：

> 尽量保持语义章节完整。

流程：

```text
Document
原始文档
↓
Section Parse
识别章节结构
↓
Section Tokens
每章Token化
↓
Length Check
判断长度
↓
Keep / Split / Pack
整章保留、长章再切、短章拼接
```

所以：

\[
\boxed{
StructureAwareSequence
往往比
BlindChunking
更适合领域文档
}
\]

---

# 十八、Sliding Window 要不要用？

对于超长章节，

可以使用：

# Sliding Window
## 滑动窗口

例如：

```text
Window 1
Token 1～4096

Window 2
Token 3073～7168

Window 3
Token 6145～10240
```

有：

```text
1024 tokens overlap
```

好处：

> 降低边界切断。

坏处：

> 重叠区域被重复训练。

所以：

\[
\boxed{
Overlap
提高上下文连续性
但增加重复Token权重
}
\]

是否使用，

要看：

> 长文本依赖和重复训练成本。

---

# 十九、Sequence Length Distribution：不要只记录一个 max_length

即使配置：

```text
max_seq_length = 8192
```

实际训练序列可能是：

```text
2048
4096
8192
不同长度混合
```

所以需要记录：

# Sequence Length Distribution
## 序列长度分布

例如：

```text
P50 = 4096
P90 = 8192
Padding Rate = 3%
Packed Token Utilization = 96%
```

因为：

\[
\boxed{
MaxLength
\neq
ActualTrainingLengthDistribution
}
\]

---

# 二十、核心心智模型 ⑥：训练“看过长文本”不等于模型“学会长上下文能力”

假设你训练了 8192 Token Sequence。

这只能说明：

> 模型训练时见过 8192 长度上下文。

不自动意味着：

```text
能够准确利用8000Token前的信息
能够做跨章节推理
能够可靠长文档检索
```

这些能力必须单独评测。

所以：

\[
\boxed{
LongSequenceExposure
\neq
LongContextCompetence
}
\]

真正长上下文能力还受到：

```text
Base Model原生位置编码
Attention结构
训练长度分布
数据任务结构
评测方式
```

影响。

---

# 二十一、Perplexity：为什么它能看 CPT 学习，但不能单独代表业务能力？

Causal LM 常用：

# Perplexity
## 困惑度

概念上：

\[
PPL
=
\exp(\mathcal{L})
\]

如果 Loss 更低，

Perplexity 通常也更低。

可以直觉理解：

> 模型对下一个 Token 更不“意外”。

因此 CPT 后：

```text
Procurement Validation Corpus
PPL下降
```

说明：

> 模型对采购语言分布建模得更好。

但：

\[
\boxed{
LowerPerplexity
\neq
BetterProcurementAgent
}
\]

因为它不直接证明：

```text
风险判断更准
引用更准
指令遵循更好
工具调用更好
```

所以 Perplexity 是：

> Language Modeling Metric。

不是：

> 最终业务 KPI。

---

# 二十二、核心心智模型 ⑦：Token-level Loss 和 Business-level Quality 必须分层

CPT 优化的是：

\[
\boxed{
TokenPredictionLoss
}
\]

但最终我们关心的是：

```text
领域理解
风险识别
长文档理解
专业语言
通用能力
SFT后任务表现
```

因此：

\[
\boxed{
TrainingMetric
\neq
ProductMetric
}
\]

专业评测必须分层：

```text
Layer 1
CPT Loss / Perplexity
语言建模层

Layer 2
Domain Probes
领域理解探针

Layer 3
Downstream Tasks
下游采购任务

Layer 4
General Regression
通用能力回归
```

---

# 二十三、Effective Tokens：真正参与 Loss 的 Token 才算有效训练量

假设 Batch 中一共：

```text
1,000,000 token positions
```

其中：

```text
Padding 100,000
Masked positions 20,000
```

真正计算 Loss 的只有：

```text
880,000
```

所以可以定义：

\[
EffectiveTrainingTokens
=
\sum_t m_t
\]

这和第 2 阶段的：

> Effective Domain Tokens

概念不同。

第 2 阶段关注：

> 数据质量后的有效语料。

本阶段关注：

> 真正进入 Loss 的训练 Token。

所以两层应该分开：

\[
\boxed{
EffectiveCorpusTokens
\neq
EffectiveTrainingTokens
}
\]

---

# 二十四、Token Utilization：Packing 做得好不好可以量化

定义：

\[
Utilization
=
\frac{RealTokens}{TotalSequenceSlots}
\]

例如：

```text
4096长度 × 100 sequences
=
409600 slots

真实Token
=
397000
```

那么：

\[
Utilization
\approx
96.9\%
\]

如果 Utilization 很低：

> 大量算力浪费在 Padding。

所以：

\[
\boxed{
PackingQuality
可以用TokenUtilization衡量
}
\]

---

# 二十五、政府采购 CPT 的推荐 Sequence Construction 思路

第一版可以采用：

```text
Document Parse
文档结构解析
↓
Section-aware Split
优先按章节切分
↓
Tokenizer
转成Token IDs
↓
Long Section Split
超长章节再分块
↓
EOS Boundary
每个独立文档/样本加入边界
↓
Length-aware Packing
短样本按长度合理拼接
↓
Loss Mask
PAD等无效位置不计Loss
↓
Batch
进入训练
```

这里的核心逻辑是：

> **优先保护语义结构，再优化 GPU 利用率。**

而不是：

> 先把所有 Token 填满。

---

# 二十六、本阶段正式工程产物：`ProcurementCPTObjectivePolicy_V0.1`

第一版至少锁定：

```text
objective_type
=
causal_language_modeling

sequence_length

sequence_length_distribution

document_boundary_policy

eos_policy

packing_enabled

packing_strategy

cross_document_attention_policy

loss_mask_policy

padding_loss_policy

truncation_policy

long_document_policy

section_aware_split

sliding_window_policy

window_overlap

sampling_policy

effective_training_tokens

token_utilization

validation_loss

validation_perplexity

domain_probe_metrics

general_regression_metrics

objective_policy_version
```

训练 Trace 至少记录：

```text
corpus_version

tokenizer_version

sequence_builder_version

max_sequence_length

actual_sequence_length

packing_rate

padding_rate

masked_token_rate

effective_training_tokens

loss

perplexity
```

这样以后才能回答：

> **为什么同一个 Corpus，两次 CPT 结果不一样？**

---

# 二十七、本阶段最重要的 7 个核心心智模型

> **心智模型 ①：`ObjectiveFormula 相同 ≠ LearningContext 相同`。Next Token Prediction 的公式没变，但 Sequence 怎样构造会改变模型看到的条件上下文。**

> **心智模型 ②：`Sequence Boundary = Dependency Boundary`。切在哪里，会决定哪些跨段关系能够在一次训练上下文中被直接学习。**

> **心智模型 ③：`ChooseContextLength ≠ MaxSupportedContext`。Context Length 应由任务依赖距离、文档长度分布和计算预算共同决定。**

> **心智模型 ④：`Attention Mask ≠ Loss Mask`。前者控制能看什么，后者控制哪里算损失，这是两套完全不同的机制。**

> **心智模型 ⑤：`TruncationPolicy = ImplicitSamplingPolicy`。截断不是简单裁长度，而是在重新定义哪些文档区域更常进入训练。**

> **心智模型 ⑥：`LongSequenceExposure ≠ LongContextCompetence`。训练见过长序列，不代表模型已经具备可靠长上下文推理能力。**

> **心智模型 ⑦：`TrainingMetric ≠ ProductMetric`。CPT Loss / Perplexity 下降只证明语言建模改善，最终仍需领域任务和通用回归评测。**

---

# 二十八、把完整 CPT Objective 流程压成一张专业工程图

```text
                    ProcurementCPTCorpus
                         领域语料
                            │
                            ▼
                        Tokenizer
                     文本转Token IDs
                            │
                            ▼
                     Section Parsing
                      识别章节结构
                            │
                            ▼
                  Sequence Construction
                       构造训练序列
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
       Context Length     Packing      Truncation
       上下文长度       样本拼接        截断策略
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                    Document Boundary
                    EOS / 文档边界
                            │
                            ▼
                 Attention / Loss Policy
                 注意力与损失掩码策略
                            │
                            ▼
                      Training Batch
                         训练Batch
                            │
                            ▼
                  Next Token Prediction
                      下一个Token预测
                            │
                            ▼
                    Loss / Perplexity
                    损失与困惑度
                            │
                            ▼
                  Domain + Regression Eval
                    领域与通用回归评测
```

脑中最后只留一句：

> **CPT 不是“把语料 Tokenize 后直接训练”，而是先决定模型每次能看到什么上下文、文档怎样拼接、哪里是边界、哪些位置真正参与 Loss；这些 Sequence 级决策共同定义了模型实际在学习的任务。**

---

# 第八课 · 第 4 阶段掌握测试

现在不回看正文，你应该能够解释：CPT 为什么仍然是 Causal Language Modeling；为什么同一个 Loss 公式并不代表同一个学习任务；Sequence Construction 怎样改变上下文关系；Context Length 为什么决定可直接建模的依赖距离；为什么更长 Context 不一定更好；Packing 解决什么问题；为什么 Packing 必须显式处理 Document Boundary；EOS 的作用是什么；跨文档 Attention 是否允许为什么要成为 Policy；Attention Mask 和 Loss Mask 有什么本质区别；CPT 和 SFT 的 Loss Mask 为什么通常不同；为什么直接保留文档前 N 个 Token 会形成 Truncation Bias；为什么 `TruncationPolicy = ImplicitSamplingPolicy`；Section-aware Sampling 为什么适合采购文档；Sliding Window 的收益和代价是什么；为什么 `max_seq_length` 不等于真实训练长度分布；为什么长序列曝光不等于长上下文能力；Perplexity 能说明什么、不能说明什么；Effective Corpus Tokens 和 Effective Training Tokens 有什么区别；以及为什么最终评测必须同时看训练指标、领域能力和通用能力回归。

如果这些能够完整讲出来：

\[
\boxed{
第八课第4阶段真正掌握
}
\]

---

# 下一阶段：第八课 · 第 5 阶段
# Data Mixture & Sampling：领域语料比例、质量权重、重复控制与采样策略
## Corpus 已经干净了，Sequence 也构造好了，但不同类型语料到底各训练多少？为什么 10 倍数据量并不意味着应该获得 10 倍训练权重？

下一阶段会正式进入：

```text
Data Mixture
数据混合

Sampling Weight
采样权重

Temperature Sampling
温度采样

Quality Weighting
质量加权

Domain Balance
领域平衡

Replay Mix
通用语料回放混合

Oversampling
过采样

Undersampling
欠采样

Duplicate Exposure
重复曝光

Epoch / Token Exposure
训练曝光量

Mixture Drift
混合分布漂移
```

并建立：

# `ProcurementCPTMixturePolicy_V0.1`

下一阶段最关键的一条边界会是：

\[
\boxed{
CorpusShare
\neq
TrainingShare
}
\]

也就是说：

> **某类数据在磁盘里占 50%，不代表训练时就应该贡献 50% 的梯度。**

---
