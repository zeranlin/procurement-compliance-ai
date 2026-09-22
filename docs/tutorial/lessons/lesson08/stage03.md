# 第八课 · 第 3 阶段
# Tokenizer Audit：领域术语怎样被切分，什么时候需要调整 Tokenizer？
## “模型看见了一个采购术语”到底意味着什么？一个术语被切成 1 个 Token、3 个 Token、10 个 Token，会怎样影响 CPT？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Token ≠ Word ≠ Concept。Token 是模型输入单位，不是天然语言学词，也不是一个完整知识概念。**
2. **High Fragmentation ≠ No Knowledge。切得碎首先意味着效率和表示成本上升，不等于模型一定不懂。**
3. **TokenizerVocabulary ↔ EmbeddingRows。Tokenizer 是模型架构的一部分，不是随便替换的文本工具。**
4. **Audit First, Modify Second。先量化碎片率、Token 成本和真实错误，再决定是否动词表。**
5. **AddToken ≠ AddKnowledge。新增 Token 只新增 ID 和参数入口，知识必须通过 CPT 学出来。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Token` | Token：模型实际处理的离散文本单元 |
| `Tokenizer` | 分词器：文本与 Token ID 之间的编码/解码组件 |
| `CPT` | CPT/继续预训练：在领域语料上继续执行预训练目标 |
| `Tokenizer Audit` | 分词器审计：检查专业术语、数字、符号的 Token 化质量 |
| `Embedding` | 嵌入：把离散 Token 映射到连续高维向量 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |

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

第 2 阶段我们已经把 CPT Corpus 从“文件堆”变成了：

\[
\boxed{
质量可控
+
覆盖可解释
+
重复受控
+
版本可复现
}
\]

但真正送进模型训练的并不是“中文文本”。

而是：

> **Token ID 序列。**

所以第 3 阶段正式进入：

# Tokenizer Audit
## 分词器审计

本阶段最终形成：

# `ProcurementTokenizerAudit_V0.1`

---

# 一、先锁死本阶段最重要的一句话

Tokenizer 的职责不是：

> **理解采购术语。**

Tokenizer 的职责是：

\[
\boxed{
Text
\rightarrow
Tokens
\rightarrow
TokenIDs
}
\]

也就是：

> 把字符串转换成模型可以读取的离散编号序列。

所以：

\[
\boxed{
TokenizerIssue
\neq
ModelKnowledgeIssue
}
\]

模型“不懂某个术语”，可能有两类完全不同的问题：

```text
A. Tokenizer切得很差
输入表示成本高、碎片多

B. Tokenizer切得没问题
但模型参数没有学会这个概念
```

这两个问题的解决方法完全不同。

---

# 二、Tokenizer 的完整流程到底是什么？

一个典型 Tokenization 流程可以概念化为：

```text
Raw Text
原始文本
↓
Normalization
字符规范化
↓
Pre-tokenization / Segmentation
初步切分
↓
Subword Encoding
子词编码
↓
Token IDs
词表编号
↓
Embedding Lookup
查找对应向量
↓
Transformer
进入模型
```

其中不同模型使用的 Tokenizer 算法可能不同，例如：

```text
BPE
Byte Pair Encoding
字节对编码

WordPiece
子词切分方法

Unigram
基于概率的子词模型

Byte-level Tokenization
字节级编码
```

但无论算法叫什么，最终目标都一样：

\[
\boxed{
String
\rightarrow
IntegerSequence
}
\]

---

# 三、核心心智模型 ①：Token 不是“词”，Token 是模型的输入单位

例如：

```text
“政府采购”
```

Tokenizer A 可能切成：

```text
["政府", "采购"]
```

Tokenizer B 可能切成：

```text
["政", "府", "采", "购"]
```

Tokenizer C 甚至可能有：

```text
["政府采购"]
```

这三种都可以工作。

所以：

\[
\boxed{
OneWord
\neq
OneToken
}
\]

进一步：

\[
\boxed{
OneToken
\neq
OneConcept
}
\]

模型的概念理解不是简单存放在某一个 Token 里。

Transformer 可以通过多个 Token 的组合表示一个概念。

---

# 四、一个领域术语被切碎，会产生什么真实成本？

假设：

```text
“中小企业声明函”
```

Tokenizer A：

```text
["中小企业", "声明函"]
```

共 2 个 Token。

Tokenizer B：

```text
["中", "小", "企", "业", "声", "明", "函"]
```

共 7 个 Token。

这不意味着：

> B 一定理解不了。

但会带来几个真实工程影响。

第一：

# Sequence Length Cost
## 序列长度成本

同一篇文件需要更多 Token。

第二：

# Context Efficiency
## 上下文效率下降

固定 Context Window 内能装下的实际中文内容更少。

第三：

# Training Compute
## 训练计算量增加

训练按 Token 计费和计算。

第四：

# Learning Signal Fragmentation
## 学习信号更分散

一个稳定术语的统计模式需要跨多个位置组合学习。

所以：

\[
\boxed{
BadFragmentation
主要首先表现为
EfficiencyProblem
}
\]

它可能进一步影响学习难度，

但不能简单说：

> “多 Token = 模型不懂。”

---

# 五、核心心智模型 ②：Fragmentation 是成本信号，不是知识判决

这是本阶段非常重要的一条边界。

如果：

```text
“政府采购促进中小企业发展管理办法”
```

被切成很多 Token，

我们可以说：

> Tokenization 成本高。

但不能直接得出：

> 模型不知道这个办法。

所以：

\[
\boxed{
HighFragmentation
\neq
NoKnowledge
}
\]

真正专业的分析应该分成两层：

```text
Tokenizer Layer
切分是否高效？

Model Layer
模型是否真正理解？
```

不要混在一起。

---

# 六、Tokenizer Audit 到底审计什么？

第一版至少要审计六类对象：

```text
1. 高频采购术语
2. 低频但关键术语
3. 法规名称与文号
4. 数字、金额、百分比和单位
5. 项目编号 / 统一社会信用代码等结构化字符串
6. 中英混合缩写与行业专有名词
```

政府采购例子：

```text
实质性响应
政府采购政策功能
采购标的所属行业
中小企业声明函
联合体投标
履约保证金
竞争性磋商
单一来源采购
```

还要审计：

```text
财库〔2020〕46号
500万元
3%
30日历天
GB/T 19001
CPU/GPU
API
SaaS
```

因为这些模式对采购文本同样重要。

---

# 七、专业指标 ①：Term Fragment Count

最简单的指标：

# Term Fragment Count
## 术语碎片数

定义：

\[
F_{term}(x)
=
N_{tokens}(x)
\]

例如：

```text
“中小企业声明函”
→ 7 tokens
```

则：

\[
F_{term}=7
\]

对于关键术语，

可以统计：

```text
Median Fragment Count
P90 Fragment Count
P95 Fragment Count
```

这样就不是凭感觉说：

> “切得有点碎。”

而是有数据。

---

# 八、专业指标 ②：Token Fertility

在 Tokenizer 研究中，

# Fertility
## 分词繁殖率

通常表示：

> 一个原始语言单位平均被拆成多少个子词 Token。

英语里常按 Word 统计。

中文没有天然空格词边界，

所以工程里可以同时保留两套指标：

```text
Term Fertility
关键领域术语平均Token数

Character-normalized Token Rate
每个中文字符对应多少Token
```

例如：

\[
R_{char}
=
\frac{N_{tokens}}{N_{characters}}
\]

这个指标主要用于：

> 比较不同 Tokenizer 对同一批中文采购文本的编码效率。

注意：

\[
\boxed{
Lower
不自动等于Better
}
\]

因为 Token 太粗也不自动意味着：

> 语义更强。

它只是效率指标之一。

---

# 九、专业指标 ③：Corpus Tokenization Cost

CPT 最终训练的是整个 Corpus。

所以必须看：

\[
C_{token}
=
N_{tokens}(Corpus)
\]

假设同一个采购 Corpus：

```text
Tokenizer A
12.0B tokens

Tokenizer B
9.5B tokens
```

如果其他条件相近，

B 的训练成本可能明显更低。

因为：

> 同样的原始文本被编码成了更短的 Token 序列。

所以：

\[
\boxed{
Tokenizer
会直接影响CPT Token Budget
}
\]

第 2 阶段的：

> Token Budget

到了这里才真正落到：

> Tokenizer Version。

---

# 十、核心心智模型 ③：Tokenizer 是模型架构的一部分，不是随便换的文本工具

Tokenizer 文件看起来只是：

```text
tokenizer.json
vocab.json
merges.txt
special_tokens_map.json
```

但它和模型的：

# Embedding Matrix
## 输入嵌入矩阵

直接绑定。

如果词表大小是：

\[
V
\]

Embedding Dimension 是：

\[
d
\]

那么输入 Embedding：

\[
E
\in
\mathbb{R}^{V\times d}
\]

每个 Token ID：

> 都对应 Embedding Matrix 中的一行。

所以：

\[
\boxed{
TokenizerVocabulary
\leftrightarrow
EmbeddingRows
}
\]

这就是为什么：

> Tokenizer 不是可以随时替换的前处理插件。

---

# 十一、绝对不能做的事：重新映射已有 Token ID

假设原模型：

```text
Token 1001
→ “政府”
```

模型已经训练了对应：

```text
Embedding Row 1001
```

如果你重新训练一个词表，

让：

```text
Token 1001
→ “医疗”
```

那么原来的 Weight 和 Tokenizer：

> 彻底错位。

所以：

\[
\boxed{
ExistingTokenIDMapping
必须保持稳定
}
\]

如果确实要扩展词表，

通常更安全的方向是：

> **Append New Tokens**

也就是：

> 在现有 Vocabulary 后面追加。

而不是重写旧 ID。

---

# 十二、什么时候根本不需要改 Tokenizer？

这是最重要的工程决策之一。

很多项目做完 Audit 后，

正确结论其实是：

\[
\boxed{
KeepExistingTokenizer
}
\]

例如：

```text
关键术语虽然拆成2～4个Token
但整体Token成本可接受

没有明显UNK问题

中文覆盖正常

训练预算可以接受

下游模型理解并没有明显受限
```

那么：

> 不要为了“看起来更领域化”去改 Tokenizer。

因为修改 Tokenizer 会引入：

```text
Embedding兼容问题
训练复杂度增加
Serving版本风险
已有Checkpoint兼容问题
Adapter兼容问题
数据需要重新Tokenize
```

所以：

\[
\boxed{
TokenizerChange
必须有MeasuredBenefit
}
\]

---

# 十三、核心心智模型 ④：Audit First，Modify Second

不要先问：

> “我们要不要做一个采购专用 Tokenizer？”

先做：

```text
Benchmark Corpus
↓
Critical Lexicon
↓
Tokenize
↓
Measure Fragmentation
↓
Measure Token Cost
↓
Inspect Rare Patterns
↓
Downstream Error Analysis
↓
Decide
```

中文解释：

```text
先准备代表性文本
↓
建立关键术语清单
↓
用当前Tokenizer实际切分
↓
统计碎片程度
↓
计算Corpus Token成本
↓
检查数字、单位、文号等异常模式
↓
和真实模型错误做关联
↓
再决定是否修改
```

所以：

\[
\boxed{
TokenizerAudit
先于
TokenizerExtension
}
\]

---

# 十四、什么时候才值得考虑 Vocabulary Extension？

可以考虑扩展词表的典型条件是：

```text
关键领域术语高频出现

这些术语长期稳定

现有Tokenizer持续严重碎片化

碎片化显著增加Corpus Token成本

CPT规模足够大，可以真正训练新Embedding

有完整回归测试验证兼容性
```

例如一个术语：

```text
“中小企业声明函”
```

在几十亿 Token 的 Corpus 中出现极高频率，

并且长期被拆得非常碎，

才可能值得考虑：

> 增加一个 Normal Token。

注意：

> **Normal Token**

不是：

> Special Token。

---

# 十五、Special Token 和 Domain Token 不能混淆

Special Token 通常用于：

```text
BOS
序列开始

EOS
序列结束

PAD
填充

角色边界
System / User / Assistant
```

它们具有：

> 协议和结构功能。

而：

```text
“中小企业声明函”
```

即使加入 Vocabulary，

通常也只是：

> 普通领域 Token。

所以：

\[
\boxed{
DomainTerm
\neq
SpecialToken
}
\]

不要把采购术语全部做成 Special Token。

---

# 十六、Vocabulary Extension 以后发生什么？

假设原词表：

\[
V=128000
\]

新增：

\[
500
\]

个 Token。

新词表：

\[
V'=128500
\]

那么 Embedding Matrix 从：

\[
128000\times d
\]

扩展为：

\[
128500\times d
\]

新增的 500 行：

> 一开始并没有经过原始预训练。

所以必须初始化。

常见思路包括：

```text
Random Initialization
随机初始化

Average Initialization
用组成子词Embedding的平均值初始化

Weighted Composition
根据原切分子词做加权组合初始化
```

但一定要记住：

\[
\boxed{
Initialization
\neq
Knowledge
}
\]

初始化只是：

> 给新 Token 一个训练起点。

真正的语义仍然需要后续 CPT 学出来。

---

# 十七、核心心智模型 ⑤：Adding Token 不等于 Adding Knowledge

假设我们新增：

```text
“政府采购促进中小企业发展管理办法”
```

这个 Token。

模型不会因为 Vocabulary 里出现了这个字符串，

就自动知道：

```text
它是什么
有什么内容
适用什么场景
与哪些规则关联
```

新 Token 一开始只是：

> 一个新 ID + 一行新 Embedding。

所以：

\[
\boxed{
AddToken
\neq
AddKnowledge
}
\]

必须经过足够训练，

才可能形成稳定表示。

---

# 十八、LoRA / QLoRA 场景为什么尤其要小心新 Token？

如果新增 Token，

但训练时只 LoRA：

```text
q_proj
k_proj
v_proj
o_proj
```

而新的：

```text
Embedding Rows
```

根本没有被训练，

那新增词表可能几乎没有意义。

所以扩词表后必须明确：

```text
Embedding是否Trainable？

LM Head是否需要同步？

是否Weight Tying？

Adapter保存是否包含新增Embedding？

最终Checkpoint怎样加载？
```

这里的具体实现取决于模型架构。

但工程原则不变：

\[
\boxed{
NewVocabulary
必须有
TrainableParameters
承接
}
\]

---

# 十九、数字、金额和单位为什么要单独审计？

采购文本大量出现：

```text
5万元
5000000元
3%
30日历天
1.5%
2026年9月18日
GB/T 19001-2016
```

如果 Tokenizer 对数字和符号切分很异常，

会增加：

```text
序列长度
数值关系学习难度
格式生成错误
```

所以 Tokenizer Audit 不应该只有：

> 中文词语表。

还要单独建立：

# Numeric / Unit Test Set
## 数字与单位测试集

检查：

```text
金额
百分比
日期
文号
标准编号
项目编号
统一社会信用代码
```

---

# 二十、Tokenizer 改了以后，旧数据必须重新 Tokenize

这一点非常关键。

如果：

```text
Tokenizer_V1
```

生成了一批 Token IDs，

后来升级：

```text
Tokenizer_V2
```

那么旧的 Token ID Cache：

> 不能默认继续使用。

必须：

\[
\boxed{
Text
\rightarrow
Retokenize
\rightarrow
NewTokenIDs
}
\]

所以训练数据必须记录：

```text
tokenizer_name
tokenizer_version
tokenizer_hash
vocab_size
special_token_config
```

否则：

> Corpus Version 和 Tokenizer Version 对不上。

---

# 二十一、核心心智模型 ⑥：Tokenizer Version 是 Model Version 的组成部分

一个模型版本不能只写：

```text
ProcurementLM_V0.2
```

还应该能够追溯：

```text
Base Model Version

Tokenizer Version

Vocabulary Hash

CPT Corpus Version

Training Config

SFT Version
```

因为 Serving 如果加载错 Tokenizer，

哪怕模型 Weight 完全正确：

> 输出也可能彻底异常。

所以：

\[
\boxed{
ModelArtifact
=
Weights
+
Tokenizer
+
Config
}
\]

而不是只有：

> `model.safetensors`。

---

# 二十二、到底有哪三种 Tokenizer 决策？

审计以后，通常有三条路径。

## Path A：Keep
### 保持原 Tokenizer

适合：

```text
总体效率合理
关键术语碎片可接受
没有明显输入瓶颈
```

这是默认优先路径。

---

## Path B：Extend
### 在现有 Vocabulary 后追加少量领域 Token

适合：

```text
少数稳定高频术语严重碎片化
收益能够量化
有足够CPT训练新Embedding
```

---

## Path C：Retrain Tokenizer
### 重新训练整个 Tokenizer

这是最高风险路径。

因为它可能导致：

> 整个 Token ID 空间改变。

对于已有 Pretrained Model，

通常意味着：

> 极高兼容成本。

所以除非：

```text
重新从头训练模型
或
有非常充分的架构和训练资源
```

否则不应轻易采用。

所以：

\[
\boxed{
Keep
>
Extend
>
Retrain
}
\]

这里的 `>` 不是说性能一定更好，

而是表达：

> **默认工程风险从低到高。**

---

# 二十三、Tokenizer Audit 的最终评测不能只看 Token 数

假设扩词表以后：

```text
Corpus Token数下降 8%
```

这很好。

但还要检查：

```text
领域CPT Loss
下游任务表现
通用文本表现
指令遵循
生成稳定性
Serving兼容性
```

因为：

\[
\boxed{
TokenizerMetricGain
\neq
ModelQualityGain
}
\]

最终必须回到：

> 模型实际能力。

---

# 二十四、本阶段工程产物：`ProcurementTokenizerAudit_V0.1`

第一版至少锁定：

```text
tokenizer_name

tokenizer_version

tokenizer_hash

vocab_size

algorithm_family

special_tokens

critical_lexicon

term_fragment_count

term_fertility

character_normalized_token_rate

corpus_token_count

numeric_unit_test

document_id_test

regulation_reference_test

high_fragmentation_terms

candidate_new_tokens

decision
=
keep / extend / retrain

embedding_resize_required

embedding_training_policy

lm_head_policy

retokenization_required

compatibility_test

serving_version_policy
```

如果选择 Extend，

还要记录：

```text
added_tokens

old_vocab_size

new_vocab_size

token_id_range

initialization_method

training_exposure

checkpoint_compatibility

adapter_compatibility
```

这样 Tokenizer 才真正进入：

> 可审计工程资产。

---

# 二十五、本阶段最重要的 7 个核心心智模型

> **心智模型 ①：`Token ≠ Word ≠ Concept`。Token 是模型输入单位，不是天然语言学词，也不是一个完整知识概念。**

> **心智模型 ②：`High Fragmentation ≠ No Knowledge`。切得碎首先意味着效率和表示成本上升，不等于模型一定不懂。**

> **心智模型 ③：`TokenizerVocabulary ↔ EmbeddingRows`。Tokenizer 是模型架构的一部分，不是随便替换的文本工具。**

> **心智模型 ④：`Audit First, Modify Second`。先量化碎片率、Token 成本和真实错误，再决定是否动词表。**

> **心智模型 ⑤：`AddToken ≠ AddKnowledge`。新增 Token 只新增 ID 和参数入口，知识必须通过 CPT 学出来。**

> **心智模型 ⑥：`TokenizerVersion ∈ ModelVersion`。Weights、Tokenizer、Config 必须作为一个整体发布和加载。**

> **心智模型 ⑦：`TokenizerMetricGain ≠ ModelQualityGain`。Token 数下降只是局部优化，最终必须用 CPT、下游任务和回归测试证明收益。**

---

# 二十六、把完整 Tokenizer Audit 流程压成一张专业工程图

```text
                  Representative CPT Corpus
                    代表性CPT语料样本
                            │
                            ▼
                     Critical Lexicon
                 建立关键领域术语清单
                            │
                            ▼
                    Current Tokenizer
                   使用当前分词器编码
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
      Term Fragment     Numeric / Unit   Corpus Cost
        术语碎片率       数字单位测试      全语料Token成本
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                     Error Correlation
             与真实CPT / 下游错误做关联分析
                            │
                            ▼
                       Decision Gate
                  是否真的值得修改Tokenizer
                 ┌──────────┼──────────┐
                 ▼          ▼          ▼
                Keep      Extend      Retrain
              保持原版    追加少量词    重训词表
                 │          │          │
                 │          ▼          │
                 │    Resize Embedding │
                 │      扩展Embedding  │
                 │          │          │
                 │          ▼          │
                 │    Train New Rows   │
                 │      训练新增参数    │
                 └──────────┼──────────┘
                            ▼
                    Retokenize Corpus
                      重新编码训练语料
                            │
                            ▼
                   Compatibility Tests
               Checkpoint / Adapter / Serving
                            │
                            ▼
                    CPT + Regression Eval
                 CPT与下游回归评测
                            │
                            ▼
                Tokenizer Release Decision
```

脑中最后只留一句：

> **Tokenizer Audit 的目标不是做一个“更懂采购的分词器”，而是判断当前 Tokenizer 是否正在制造可量化的领域表示成本；只有当这种成本足够大、收益能够验证、并且有足够 CPT 训练新增参数时，才值得修改词表。**

---

# 第八课 · 第 3 阶段掌握测试

现在不回看正文，你应该能够解释：Tokenizer 为什么只负责 `Text → Token IDs`；Token、Word、Concept 为什么不能画等号；领域术语切成很多 Token 会产生哪些真实成本；为什么 High Fragmentation 不等于模型没有知识；Tokenizer Audit 应该覆盖哪些采购语言模式；Term Fragment Count、Fertility、Character-normalized Token Rate 和 Corpus Tokenization Cost 分别测什么；为什么 Tokenizer Vocabulary 和 Embedding Matrix 是绑定的；为什么绝对不能随便重排已有 Token ID；什么时候保持原 Tokenizer 反而是专业选择；为什么应该先 Audit 再 Modify；什么条件下才值得 Vocabulary Extension；为什么 Domain Token 不等于 Special Token；新增 Token 后为什么必须训练新增 Embedding；为什么 `Add Token ≠ Add Knowledge`；LoRA / QLoRA 场景为什么尤其要检查 Embedding 是否真的被训练；数字、金额、单位和文号为什么需要单独测试；Tokenizer 变化以后为什么必须重新 Tokenize Corpus；以及为什么 Tokenizer Version 必须作为 Model Version 的组成部分一起发布。

如果这些能够完整讲出来：

\[
\boxed{
第八课第3阶段真正掌握
}
\]

---

# 下一阶段：第八课 · 第 4 阶段
# CPT Training Objective：Next Token Prediction、Sequence、Context Length 与 Loss
## CPT 明明还是 Next Token Prediction，为什么数据拼接方式、Sequence Length、Packing 和 Loss Masking 会直接改变模型到底在学什么？

下一阶段会正式进入：

```text
Next Token Prediction
因果语言建模

Sequence Construction
训练序列构造

Context Length
上下文长度

Packing
多文档拼接

Document Boundary
文档边界

EOS
序列结束标记

Loss Masking
损失掩码

Truncation
截断

Long-document Sampling
长文档采样

Effective Tokens
有效训练Token

Perplexity
困惑度

Training Objective Audit
训练目标审计
```

并建立：

# `ProcurementCPTObjectivePolicy_V0.1`

下一阶段最关键的边界是：

\[
\boxed{
SameCorpus
+
DifferentSequenceConstruction
=
DifferentLearningProblem
}
\]

也就是说：

> **同一批文本，只要你怎样切 Sequence、怎样 Packing、哪里算 Loss 不同，模型实际学习到的任务就已经不同。**

---
