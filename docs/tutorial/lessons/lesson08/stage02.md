# 第八课 · 第 2 阶段
# Domain Corpus：什么样的政府采购领域语料值得用于 CPT？
## “采购文本越多越好”为什么是错的？怎样把原始文档变成真正适合继续预训练的领域语料？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **CPTCorpus ≠ DocumentDump。Corpus 是你希望模型长期吸收的领域分布，不是采购文件仓库。**
2. **MoreDocuments ≠ MoreSignal。真正有意义的是经过质量过滤、去重和领域相关性折算后的 Effective Tokens。**
3. **CorpusQuality × Coverage 决定 CPT 上限。训练更久不能弥补语料里根本不存在的领域覆盖。**
4. **Authority ≠ Representativeness。权威法规很重要，但只训练法规并不能代表完整政府采购语言世界。**
5. **Coverage 是多维空间。文件类型、行业、地区、时间、复杂度和生命周期必须一起看，不能只看总 Token。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `CPT` | CPT/继续预训练：在领域语料上继续执行预训练目标 |
| `Domain Corpus` | 领域语料：用于继续预训练的政府采购专业文本集合 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `OCR` | OCR：把扫描图像中的文字转换成机器可读文本 |

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

第 1 阶段我们已经锁定：

\[
\boxed{
CPT
=
在领域语料分布上继续执行预训练目标
}
\]

所以第 2 阶段真正要解决的问题不是：

> **“去哪里找更多采购文件？”**

而是：

> **“什么样的数据分布，值得让模型继续改 Weight？”**

因为 CPT 和 RAG 不一样。

RAG 的坏文档主要会污染一次检索。

而 CPT 的坏语料会通过梯度：

> **直接写进模型参数。**

所以本阶段最终形成：

# `ProcurementCPTCorpusPolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

CPT Corpus 不是：

> **一堆采购文件的集合。**

更准确地说：

\[
\boxed{
CPTCorpus
=
我们希望模型长期吸收的领域分布
}
\]

这句话非常重要。

因为你把什么文本长期、大量、重复地放进 CPT，

模型就会逐渐认为：

> **这就是这个领域“正常语言世界”的样子。**

所以：

\[
\boxed{
CorpusDesign
=
DomainPriorDesign
}
\]

也就是说：

> **你不是在“喂文件”，你是在设计模型未来的领域先验。**

---

# 二、核心心智模型 ①：Data Volume 不等于 Effective Learning Signal

第一个必须彻底改掉的直觉是：

\[
\boxed{
MoreDocuments
\neq
MoreUsefulSignal
}
\]

假设你收集了：

```text
1000万页采购文本
```

但其中：

```text
40% 是重复公告模板
20% 是网页导航 / 页眉页脚
15% 是OCR错误
10% 是同一项目不同镜像站重复
10% 是无关附件
真正高质量领域正文只剩 5%
```

那么表面上：

> 数据量巨大。

实际上：

> **有效学习信号非常低。**

所以真正要关注的是：

# Effective Domain Tokens
## 有效领域 Token

可以概念化为：

\[
EffectiveTokens
=
RawTokens
\times
QualityRate
\times
UniquenessRate
\times
DomainRelevance
\]

这里不是要求你真的机械相乘。

而是建立一个工程直觉：

> **Token 数量只有经过质量、去重和领域相关性折算以后，才有意义。**

---

# 三、核心心智模型 ②：Corpus Quality 决定 CPT 上限

CPT 最终能学到什么，

首先取决于：

> Corpus 本身提供了什么。

所以：

\[
\boxed{
CPTUpperBound
\approx
CorpusQuality
\times
CorpusCoverage
\times
TrainingQuality
}
\]

如果 Corpus 里没有：

```text
复杂技术参数
高质量合同条款
评分办法
履约验收文本
中小企业政策表达
跨行业采购需求
```

模型就不可能凭空学会：

> 这些领域分布。

所以：

\[
\boxed{
MissingCoverage
不能靠MoreEpochs补回来
}
\]

这是非常重要的专业判断。

训练更久：

> 只能更充分地学习已有数据分布。

不能创造：

> 语料中根本不存在的领域结构。

---

# 四、Domain Corpus 的完整工程流程

英文流程先给出来：

```text
Source Discovery
↓
Eligibility Check
↓
Document Extraction
↓
Normalization
↓
Quality Filtering
↓
Deduplication
↓
Sensitive / Compliance Filtering
↓
Benchmark Firewall
↓
Coverage Balancing
↓
Token Budgeting
↓
Corpus Versioning
↓
CPT Ready Corpus
```

翻译成人话：

```text
先找到候选来源
↓
判断是否应该进入训练
↓
把文件可靠解析成正文
↓
做不改变语义的规范化
↓
过滤低质量文档
↓
删除重复和模板堆积
↓
处理敏感数据与使用边界
↓
隔离未来Benchmark
↓
检查领域覆盖是否偏斜
↓
计算真正可用的Token预算
↓
冻结版本和来源清单
↓
得到可训练Corpus
```

这里最重要的是：

\[
\boxed{
RawDocuments
\neq
TrainingCorpus
}
\]

中间必须经过一整条数据治理链。

---

# 五、核心心智模型 ③：Source Authority 不等于 Corpus Fitness

这条非常容易被忽略。

某份文件很权威，

不代表它一定适合 CPT。

例如：

```text
法律法规原文
```

权威性非常高。

但如果你的 CPT 目标是：

> 让模型更熟悉采购文件结构和采购实务语言，

那么只用法规文本会导致：

> 领域分布过窄。

反过来：

```text
采购文件
成交公告
采购需求
合同
验收材料
```

可能更接近：

> 真实业务语言分布。

所以：

\[
\boxed{
Authority
\neq
Representativeness
}
\]

CPT Corpus 需要的是：

> **“权威 + 代表性 + 质量 + 覆盖”共同成立。**

---

# 六、政府采购 CPT Corpus 应该有哪些 Source Type？

第一版可以把来源分成六类。

## 1. Regulatory Corpus
### 法规与规范语料

例如：

```text
法律法规
部门规章
规范性文件
政策解释
官方指南
```

作用：

> 建立规范性语言和规则表达分布。

---

## 2. Procurement Document Corpus
### 采购文件语料

例如：

```text
招标文件
竞争性磋商文件
询价文件
采购需求
评分办法
资格条件
技术参数
```

作用：

> 建立真实采购文件结构和条款语言。

---

## 3. Transaction / Notice Corpus
### 交易与公告语料

例如：

```text
采购公告
更正公告
成交公告
中标公告
终止公告
```

作用：

> 学习项目生命周期和公开交易表达。

---

## 4. Contract / Performance Corpus
### 合同与履约语料

例如：

```text
合同条款
履约要求
验收标准
付款条件
售后服务
```

作用：

> 补足采购后半程语言。

---

## 5. Industry-specific Corpus
### 行业专项语料

例如：

```text
医疗
教育
信息化
工程
物业
检测
科研设备
```

作用：

> 避免模型只懂通用采购，不懂行业采购。

---

## 6. High-quality Explanatory Corpus
### 高质量解释性语料

例如：

```text
官方问答
政策解读
业务指南
培训材料
专家校对后的解释文本
```

作用：

> 增强概念之间的解释连接。

---

# 七、核心心智模型 ④：Coverage 是多维空间，不是“文件类型齐了”

很多团队说：

> “我们公告、文件、合同都有了，覆盖已经很全。”

这远远不够。

真正的 Coverage 至少应该看：

```text
Document Type
采购方式
行业
地区
年份
项目金额区间
项目复杂度
风险类型
文档长度
语言风格
生命周期阶段
```

所以 Corpus Coverage 更像：

\[
\boxed{
Coverage
=
DocumentType
\times
Industry
\times
Region
\times
Time
\times
Complexity
}
\]

不是数学上真的要做笛卡尔积，

而是建立：

> **覆盖是多维的。**

例如总体有 1 亿 Token，

但其中：

```text
80% 都来自IT采购
```

那么对医疗和工程采购来说：

> 仍然是严重缺覆盖。

---

# 八、Temporal Coverage：时间分布为什么非常重要？

采购规则、模板、表达方式会随时间变化。

如果 Corpus 主要来自：

```text
2018～2020
```

模型可能学到：

> 旧表达、旧模板、旧规则语言。

所以至少要保留：

```text
publish_date
effective_date
document_version
source_version
```

并分析：

# Temporal Distribution
## 时间分布

核心不是简单追求：

> 越新越好。

而是：

> **知道哪些是历史分布，哪些是当前主流分布。**

---

# 九、核心心智模型 ⑤：Historical Data 可以训练，但必须带时间意识

历史文档不是都应该删除。

因为历史语料可以帮助模型理解：

```text
政策演化
旧文书表达
版本变化
历史项目语言
```

但问题是：

> 如果历史语料和当前语料完全混在一起，没有任何时间边界，

模型就可能把：

> 过期表达

当成：

> 当前主流表达。

所以：

\[
\boxed{
Historical
\neq
Invalid
}
\]

但：

\[
\boxed{
Historical
必须可识别
}
\]

---

# 十、Deduplication：采购语料为什么特别容易“假大数据”？

政府采购数据非常容易重复。

同一个项目可能出现在：

```text
中央平台
地方平台
代理机构网站
镜像站
转载站
搜索缓存
```

还可能存在：

```text
原公告
更正公告
复制公告
附件重复
模板复用
```

所以至少要做：

```text
Exact Deduplication
完全重复去重

Near Deduplication
近似重复去重

Template Deduplication
模板级去重

Document Lineage Analysis
文档血缘分析
```

这里要特别注意：

> 更正公告和原公告不能简单当重复删掉。

因为它们可能表达：

> 真实业务变化。

所以：

\[
\boxed{
Similarity
\neq
SameMeaning
}
\]

去重必须保留：

> Lineage。

---

# 十一、Boilerplate：模板文本到底该不该删？

采购文档里有大量：

```text
页眉
页脚
固定免责声明
平台导航
版权信息
重复联系人模板
固定投标须知
```

如果全部保留，

模型会浪费大量容量学习：

> 高频但低价值模板。

但如果全部删除模板，

又可能损失：

> 真实文书结构。

所以正确思路不是：

\[
Boilerplate
\rightarrow
DeleteAll
\]

而是：

\[
\boxed{
Boilerplate
\rightarrow
Classify
\rightarrow
Keep / Downsample / Remove
}
\]

例如：

```text
网页导航
→ Remove

文档结构标题
→ Keep

固定法律声明
→ Downsample

高频投标须知模板
→ Keep部分代表样本
```

---

# 十二、Quality Filter：什么叫“高质量 CPT 文档”？

可以用几个维度检查：

```text
Parse Integrity
解析是否完整

Text Coherence
上下文是否连贯

Domain Relevance
是否真正属于采购领域

Structure Integrity
章节结构是否保留

Noise Rate
乱码 / OCR噪声比例

Metadata Completeness
来源、时间、版本是否完整

Semantic Density
有效业务内容比例

Authenticity
是否接近真实业务文本
```

可以建立一个概念化质量函数：

\[
Q(d)
=
f(
Integrity,
Relevance,
Coherence,
Metadata,
Noise
)
\]

这里不要求一开始就做复杂模型打分。

第一版完全可以：

> **规则过滤 + 抽样人工复核。**

---

# 十三、OCR 文本为什么不能“能读就进 CPT”？

假设原文：

```text
投标人须具有三级资质
```

OCR 变成：

```text
投标人须具有三汲资质
```

单条看似问题不大。

但如果亿级 Token 里到处都是这种错误：

> 模型会把 OCR 错误本身学成语言分布。

所以：

\[
\boxed{
OCRReadable
\neq
TrainingReady
}
\]

OCR 文档至少要经过：

```text
字符异常率
版面完整性
数字一致性
单位完整性
随机人工抽检
```

对于质量过低的来源：

> 宁可不进 CPT。

---

# 十四、Sensitive Data：训练语料不是“公开抓到就能随便进”

Corpus Governance 还必须考虑：

```text
个人信息
联系人手机号
身份证号
银行账户
内部账号
未公开商业信息
密钥
内部标记
```

需要：

# Sensitive Data Filtering
## 敏感数据过滤

核心原则是：

\[
\boxed{
AvailableData
\neq
TrainingEligibleData
}
\]

也就是说：

> 数据能拿到，不代表应该进入长期模型参数。

---

# 十五、Benchmark Firewall：CPT Corpus 和未来 Benchmark 必须隔离

这是第 1 阶段已经提过，

但第 2 阶段必须工程化。

流程：

```text
Candidate Corpus
↓
Benchmark Registry
↓
Exact Match Check
↓
Near-Duplicate Check
↓
Project / Document Lineage Check
↓
Blocked Set
↓
Training Eligible Set
```

翻译成人话：

> 候选语料在进入训练之前，先拿未来测试集和测试候选项目来做一道防火墙。

所以：

\[
\boxed{
TrainingCorpus
\cap
Benchmark
=
\varnothing
}
\]

现实里未必能做到绝对数学意义上的零交集，

但必须建立：

> **主动隔离和审计机制。**

---

# 十六、Token Budget：真正训练的是 Token，不是文件数

假设：

```text
100万份文件
```

这对训练预算没有直接意义。

真正影响训练的是：

# Token Budget
## Token 预算

例如：

\[
TotalTokens
=
\sum_{d=1}^{N}
Tokens(d)
\]

但真正应该看的是：

\[
\boxed{
EffectiveTokens
=
TokensAfterFilter
+
TokensAfterDedup
+
CoverageQualifiedTokens
}
\]

更准确地说：

> 去重、过滤以后还剩多少 Token？

> 这些 Token 分布在哪些领域？

这才决定：

> CPT 的有效训练规模。

Tokenizer 的具体审计，

我们留到第 3 阶段。

---

# 十七、Corpus Versioning：Corpus 也必须像软件一样发布

最终不能只保存一个目录：

```text
/data/cpt/final/
```

半年以后没人知道：

> “final 到底是哪一版？”

至少应该有：

```text
ProcurementCPTCorpus_V0.1

corpus_manifest.json

source_registry.json

filter_policy_version

dedup_version

benchmark_firewall_version

document_count

token_count

time_range

domain_distribution
```

所以：

\[
\boxed{
Corpus
必须Versioned
}
\]

因为模型版本能不能复现，

首先取决于：

> 训练 Corpus 能不能复现。

---

# 十八、本阶段工程产物：`ProcurementCPTCorpusPolicy_V0.1`

第一版至少锁定：

```text
corpus_policy_version

source_types

source_registry

eligibility_rules

exclusion_rules

parse_quality_rules

normalization_policy

exact_dedup_policy

near_dedup_policy

template_policy

document_lineage_policy

temporal_coverage

industry_coverage

region_coverage

document_type_coverage

sensitive_data_policy

benchmark_firewall_policy

token_budget

quality_sampling_plan

corpus_version

manifest_required
=
true
```

每份 Document 最好至少保留：

```text
document_id

source_id

source_type

project_id

document_type

industry

region

publish_date

document_version

lineage_id

parse_quality

dedup_group_id

benchmark_blocked

sensitive_flag

token_count

corpus_eligible
```

这就是：

> **一个真正可以审计的 CPT Corpus。**

---

# 十九、本阶段最重要的 7 个核心心智模型

把整阶段压成七条。

> **心智模型 ①：`CPTCorpus ≠ DocumentDump`。Corpus 是你希望模型长期吸收的领域分布，不是采购文件仓库。**

> **心智模型 ②：`MoreDocuments ≠ MoreSignal`。真正有意义的是经过质量过滤、去重和领域相关性折算后的 Effective Tokens。**

> **心智模型 ③：`CorpusQuality × Coverage` 决定 CPT 上限。训练更久不能弥补语料里根本不存在的领域覆盖。**

> **心智模型 ④：`Authority ≠ Representativeness`。权威法规很重要，但只训练法规并不能代表完整政府采购语言世界。**

> **心智模型 ⑤：Coverage 是多维空间。文件类型、行业、地区、时间、复杂度和生命周期必须一起看，不能只看总 Token。**

> **心智模型 ⑥：`Similarity ≠ Duplicate`。采购文档存在更正、版本和模板血缘，去重必须理解 Document Lineage。**

> **心智模型 ⑦：`AvailableData ≠ TrainingEligibleData`。能抓到的数据还必须通过质量、敏感信息、Benchmark Firewall 和版本治理，才能进入 Weight。**

---

# 二十、把完整流程压成一张专业工程图

```text
                     Raw Procurement Sources
                              │
                              ▼
                       Source Registry
                记录来源、权限、类型与版本
                              │
                              ▼
                      Eligibility Check
                 判断是否具备训练资格
                              │
                              ▼
                    Parse & Normalize
                恢复正文并做安全规范化
                              │
                              ▼
                      Quality Filter
               去掉乱码、低质量和无关内容
                              │
                              ▼
                     Dedup & Lineage
              去重复，同时保留版本与血缘
                              │
                              ▼
                  Sensitive Data Filter
               隔离不应写入模型参数的数据
                              │
                              ▼
                   Benchmark Firewall
               防止未来Gold/Test进入训练
                              │
                              ▼
                    Coverage Analysis
          检查行业、地区、时间、文档类型偏斜
                              │
                              ▼
                      Token Budget
             计算真正可用于训练的有效Token
                              │
                              ▼
                    Corpus Versioning
              冻结Manifest、策略和版本号
                              │
                              ▼
              ProcurementCPTCorpus_V0.1
```

如果只记一句：

> **CPT Corpus 的专业设计，不是“尽量收集更多采购文本”，而是把真实领域世界转化成一个质量可控、覆盖可解释、重复受控、时间可追踪、敏感数据受治理、Benchmark 不泄漏、版本可复现的训练分布。**

---

# 第八课 · 第 2 阶段掌握测试

现在不回看正文，你应该能够解释：为什么 CPT Corpus 不是文件仓库；为什么数据量和有效学习信号不是一回事；什么叫 Effective Domain Tokens；Corpus Quality 和 Coverage 为什么决定 CPT 上限；为什么 Source Authority 不等于 Corpus Fitness；政府采购 CPT 至少应该覆盖哪些 Source Type；为什么 Coverage 是多维空间；历史数据为什么可以保留但必须带时间意识；为什么采购语料特别容易形成“假大数据”；Exact / Near / Template Dedup 有什么区别；Document Lineage 为什么不能丢；Boilerplate 为什么不能简单全部删除；高质量 CPT 文档应该从哪些维度判断；为什么 OCR “能读”还不代表可以训练；为什么 Available Data 不等于 Training Eligible Data；Benchmark Firewall 应该放在哪个环节；为什么 Token Budget 比文件数更有意义；以及为什么 Corpus Versioning 是模型可复现的前提。

如果这些能够完整讲出来：

\[
\boxed{
第八课第2阶段真正掌握
}
\]

---

# 下一阶段：第八课 · 第 3 阶段
# Tokenizer Audit：领域术语怎样被切分，什么时候需要调整 Tokenizer？
## “模型看见了一个采购术语”到底意味着什么？一个术语被切成 1 个 Token、3 个 Token、10 个 Token，会怎样影响 CPT？

下一阶段会正式进入：

```text
Tokenization
Vocabulary Coverage
Subword Fragmentation
Token Fertility
Unknown / Rare Pattern
Numeric / Unit Tokenization
Chinese Procurement Terms
Tokenizer Extension
Embedding Resize
Initialization
Compatibility Risk
Tokenizer Versioning
```

并建立：

# `ProcurementTokenizerAudit_V0.1`

下一阶段最核心的边界是：

\[
\boxed{
TokenizerIssue
\neq
ModelKnowledgeIssue
}
\]

也就是说：

> 有些领域问题不是“模型不知道”，而是模型在输入层就把关键术语切得很差。

---
