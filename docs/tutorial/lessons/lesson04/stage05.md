# 第四课 · 第 5 阶段：去重与近似去重
## 为什么 100 万条“干净数据”可能实际上只有 30 万条独立信息？为什么重复数据不仅浪费训练，还会制造虚假的 Benchmark？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **主要让模型偏科。**
2. **会让考试成绩造假。**
3. **Data Count ≠ Independent Information Count**
4. **去重 ≠ 删除所有相似文本**
5. **Exact Duplicate 最容易， Near Duplicate 才是真正困难的部分**
6. **模板相同 ≠ 项目完全相同**
7. **Duplicate Detection 应先“聚类和建立关系”， 再决定是否删除**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `Raw Document` | 原始文档：未经结构化处理的采购文件源材料 |
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Dataset` | 数据集：按统一 Schema、版本和质量标准组织的样本集合 |
| `Metadata` | 元数据：项目、来源、时间、地区、版本等辅助信息 |
| `Block` | 版面块：文档解析后保留布局和位置的基本块 |
| `CPT` | CPT/继续预训练：在领域语料上继续执行预训练目标 |
| `Embedding` | 嵌入：把离散 Token 映射到连续高维向量 |
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `Split` | 数据切分：按项目/时间/地区划分训练、验证、测试数据 |
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

第四阶段结束以后，我们已经拥有：

```text
Raw Document
      ↓
ParsedDocument_V0.1
      ↓
ClauseUnit_V0.1
      ↓
CleanClause_V0.1
```

现在每一条 Clause 已经尽量做到：

```text
文字可信
结构可信
来源可追
格式稳定
高风险字符受到保护
```

看起来，似乎已经可以直接：

> 开始训练。

但现在我们会碰到一个特别隐蔽的问题。

假设你统计数据库：

```text
CleanClause 总数 = 1,000,000
```

团队非常兴奋：

> “我们已经有 100 万条政府采购专业数据！”

但当我们真正检查以后，可能发现：

```text
20万条
来自同一个采购模板

10万条
只是同一公告PDF和HTML各存了一份

15万条
来自网站镜像和重复下载

18万条
只有项目名、日期、金额不同

7万条
是更正前后高度相似的版本
```

最后真正独立的信息，可能远远不到：

```text
100万
```

这就是第五阶段要处理的核心问题：

# Duplicate

重复。

但今天很快会看到：

> 去重绝对不是“相同文本删掉一条”这么简单。

---

# 一、本阶段真正要解决的一个核心问题

今天只解决：

> **怎样识别政府采购数据里的完全重复、近似重复、模板重复和版本重复，并在不误删真实业务差异的前提下，控制重复信息对训练和评测造成的偏差？**

最终我们要得到：

# `DedupedClauseSet_V0.1`

主线是：

```text
CleanClause_V0.1
        ↓
Duplicate Detection
        ↓
Duplicate Clustering
        ↓
Canonical / Relation Decision
        ↓
DedupedClauseSet_V0.1
```

---

# 二、先建立本阶段最重要的 6 个核心心智模型

```text
① Data Count ≠ Independent Information Count

② 去重 ≠ 删除所有相似文本

③ Exact Duplicate 最容易，
   Near Duplicate 才是真正困难的部分

④ 模板相同 ≠ 项目完全相同

⑤ Duplicate Detection 应先“聚类和建立关系”，
   再决定是否删除

⑥ Train / Test 之间的近重复
   比训练集内部重复更危险
```

最后一句尤其重要。

因为训练集里重复很多：

> 主要让模型偏科。

而 Train/Test 之间出现重复：

> 会让考试成绩造假。

---

# 三、先看最简单的重复

假设硬盘里有两个文件：

```text
A/
某市智慧交通项目招标文件.pdf
```

和：

```text
B/
最终版-某市智慧交通项目招标文件.pdf
```

名字不同。

但是两个文件：

> 一个 Byte 都没变。

---

# 四、这是最简单的一类

# Exact File Duplicate

完全文件重复。

这类非常容易发现。

---

# 五、怎么发现？

第四课第二阶段已经埋好了一个字段：

```text
file_hash
```

例如：

# SHA-256

如果：

```text
SHA256(File A)
=
SHA256(File B)
```

那么在实际工程中，我们可以极高置信度认为：

> 内容完全相同。

---

# 六、注意

文件名不同：

```text
招标文件.pdf
最终招标文件.pdf
下载(1).pdf
```

完全不重要。

Hash 看的是：

> 文件内容。

---

# 七、所以第一层 Dedup 非常简单

```text
Raw File
   │
   ▼
SHA-256
   │
   ▼
Hash相同？
   │
   ├── 是 → Exact File Duplicate
   └── 否 → 继续检查
```

---

# 八、但 Hash 不同，是不是说明内容不同？

不一定。

这就是事情开始变麻烦的地方。

---

# 九、假设有两个 PDF

文件 A：

```text
某项目招标文件.pdf
```

文件 B：

```text
某项目招标文件-官网下载.pdf
```

看起来内容完全一样。

但 B 的 PDF Metadata 多了：

```text
Creator
CreationTime
Producer
```

---

# 十、文件 Byte 不一样

所以：

```text
SHA256(A)
≠
SHA256(B)
```

但用户看到的正文：

> 完全一样。

---

# 十一、这就是第二层

# Content Duplicate

内容重复。

---

# 十二、所以我们已经有两个不同概念

```text
File Duplicate
```

和：

```text
Content Duplicate
```

千万不要混。

---

# 十三、可以记：

\[
\boxed{
FileHash不同
\not\Rightarrow
DocumentContent不同
}
\]

---

# 十四、同样的事情在 HTML 特别常见

两个网址：

```text
site-a.gov.cn/notice/123
```

和：

```text
mirror.gov.cn/archive/456
```

网页结构完全不同。

一个有：

```text
导航栏
分享按钮
版权信息
```

另一个没有。

---

# 十五、但采购公告正文：

> 一模一样。

原 HTML Hash：

> 完全不同。

正文：

> 相同。

---

# 十六、所以第二层去重最好发生在：

# Parsed / Clean Content

而不只是原文件。

---

# 十七、这就是为什么我们之前一直保留分层数据

现在终于看到收益：

```text
Raw File Hash
```

可以找：

> 文件级重复。

```text
Normalized Document Text
```

可以找：

> 正文级重复。

```text
CleanClause
```

可以找：

> 条款级重复。

---

# 十八、所以 Dedup 本身也是多层的

今天最重要的一张图之一：

```text
Duplicate
│
├── File-level Duplicate
│
├── Document-level Duplicate
│
├── Section-level Duplicate
│
├── Clause-level Duplicate
│
├── Template-level Duplicate
└── Semantic Near Duplicate
```

不是一个：

> `drop_duplicates()`。

---

# 十九、现在看 Clause-level Exact Duplicate

假设两个不同项目都有：

```text
供应商应具有独立承担民事责任的能力。
```

字符串完全一致。

是不是应该：

> 留一条，删除另一条？

---

# 二十、答案：

# 不一定。

这句话特别重要。

---

# 二十一、为什么？

因为它们可能来自：

```text
Project A
```

和：

```text
Project B
```

两个真实、独立的采购项目。

---

# 二十二、从“文本内容”来看

它们：

> 完全重复。

---

# 二十三、但从“业务事件”来看

它们：

> 发生了两次。

---

# 二十四、所以这里出现一个很重要的区别：

# Text Duplicate

和：

# Observation Duplicate

不是一回事。

---

# 二十五、举个生活例子

调查 100 家商店。

发现 80 家都写：

> “营业时间 9:00—21:00”。

是不是应该说：

> “这句话一样，所以只算一家商店”？

当然不是。

---

# 二十六、因为你研究的是：

> 商店分布。

重复本身：

> 可能是真实统计信息。

---

# 二十七、同样，

如果你研究：

> 政府采购文件中某类标准资格条件的真实出现频率，

这些重复：

> 本身就是数据。

---

# 二十八、但如果你在训练 LLM

同一句标准模板出现：

```text
100,000次
```

另外一个重要边界条件只出现：

```text
100次
```

模型会发生什么？

---

# 二十九、它会非常强烈地学到：

> 高频模板。

而对真正稀有、困难的风险：

> 学得很差。

---

# 三十、所以 Dedup 的目标不是问：

> “重复是不是坏？”

而应该问：

> **“对于当前任务，这种重复会不会不合理地改变数据权重？”**

---

# 三十一、这是第五阶段最重要的思想之一：

\[
\boxed{
DedupPolicy
取决于
DatasetPurpose
}
\]

---

# 三十二、比如 CPT 语料

大量行业标准表达重复出现：

> 未必完全是坏事。

它反映：

> 真实行业语言分布。

---

# 三十三、但如果某一个网站镜像了同一批公告 20 次

那 20 倍频率：

> 是数据采集过程制造的。

不是行业真实分布。

这就应该去掉。

---

# 三十四、这两种重复必须区分

### Natural Repetition

真实业务重复。

### Artificial Duplication

采集流程制造的重复。

---

# 三十五、我们真正最想消灭的是：

# Artificial Duplication

---

# 三十六、比如：

```text
同一PDF重复下载
同一网页不同URL镜像
同一个附件被保存5份
解析器重复输出同一个Block
```

这些：

> 都不是新的业务观察。

---

# 三十七、而不同项目都包含：

```text
供应商应具有良好的商业信誉。
```

则可能是：

> 真实自然重复。

---

# 三十八、所以去重数据库最好不要简单只有

```text
is_duplicate = true
```

而应该知道：

# Duplicate Relation

到底是哪种关系。

---

# 三十九、例如：

```text
exact_copy
```

```text
mirror_copy
```

```text
same_document_different_format
```

```text
template_reuse
```

```text
revised_version
```

```text
semantic_near_duplicate
```

---

# 四十、这些关系：

> 处理方式不一样。

---

# 四十一、现在看第三种典型情况

# Same Document, Different Format

采购网站可能同时提供：

```text
公告正文 HTML
```

和：

```text
公告附件 PDF
```

正文有时：

> 几乎完全相同。

---

# 四十二、如果我们两边都收

Dataset 里：

> 同一内容变成两次。

---

# 四十三、哪一个留？

可能要根据：

```text
Source Authority
Parse Quality
Completeness
Traceability
```

选择：

# Canonical Copy

权威代表版本。

---

# 四十四、例如：

```text
PDF:
正式签章附件
```

和：

```text
HTML:
网站正文
```

不能机械说：

> HTML 更干净，所以删 PDF。

---

# 四十五、因为 Source Authority：

> 也很重要。

---

# 四十六、因此 Duplicate Cluster 内最好有：

```text
canonical_document_id
```

指向：

> 代表版本。

其他版本：

> 不一定物理删除。

可以保留关系。

---

# 四十七、这就是今天另一个核心原则：

# Dedup ≠ Physical Delete

---

# 四十八、更安全的架构是：

```text
Duplicate Cluster
│
├── Canonical Record
├── Duplicate Record 1
├── Duplicate Record 2
└── Duplicate Record 3
```

---

# 四十九、训练 View：

> 只取 Canonical。

Master Data：

> 全部保留。

---

# 五十、这和第四阶段：

```text
Raw
+
Normalized
```

的哲学完全一致。

---

# 五十一、永远尽量：

# Non-destructive Data Engineering

---

# 五十二、现在进入真正困难的部分

# Near Duplicate

近似重复。

---

# 五十三、例如条款 A：

> 供应商应在本市设有固定售后服务机构。

条款 B：

> 投标人须在项目所在地设立固定售后服务机构。

---

# 五十四、字符串：

> 不一样。

但是业务含义：

> 非常接近。

---

# 五十五、再例如：

A：

> 供应商注册资本不得低于5000万元。

B：

> 投标人注册资本应达到人民币5000万元以上。

---

# 五十六、表面字符不同。

但核心条件：

```text
注册资本
>=
5000万元
```

基本一样。

---

# 五十七、这就是：

# Semantic Near Duplicate

语义近重复。

---

# 五十八、如果只用：

```text
text == other_text
```

完全发现不了。

---

# 五十九、这就是为什么：

> SHA-256 只能解决最容易的一层。

---

# 六十、那么近重复怎么检测？

我们先不要上复杂算法。

先建立最直观的方法：

# Token Overlap

---

# 六十一、假设：

A：

```text
供应商 须 在 本市 设立 售后 服务 机构
```

B：

```text
供应商 应 在 本市 设立 固定 服务 机构
```

很多词：

> 是一样的。

---

# 六十二、于是可以问：

> 两条文本共享多少内容？

这就是 Similarity。

---

# 六十三、一个经典直觉指标：

# Jaccard Similarity

公式非常简单：

\[
J(A,B)
=
\frac{|A\cap B|}
{|A\cup B|}
\]

---

# 六十四、先不怕公式。

它只是在说：

> 两组元素里，共同出现的东西占全部不同元素的多少。

---

# 六十五、例如 A 有：

```text
{供应商, 本市, 服务, 机构}
```

B 有：

```text
{供应商, 本市, 固定, 服务, 机构}
```

共同：

```text
供应商
本市
服务
机构
```

有 4 个。

全部不同元素：

```text
供应商
本市
固定
服务
机构
```

有 5 个。

---

# 六十六、所以：

\[
J(A,B)=\frac45=0.8
\]

也就是：

> 80% 相似。

---

# 六十七、这比：

```text
必须100%相同
```

聪明很多。

---

# 六十八、但是直接按“词集合”比较也有问题

A：

> 供应商不得在本市设立机构。

B：

> 供应商必须在本市设立机构。

---

# 六十九、它们绝大多数词：

> 一模一样。

Jaccard：

> 可能非常高。

---

# 七十、但是：

```text
不得
```

和：

```text
必须
```

让业务意义：

> 几乎相反。

---

# 七十一、所以第五阶段再次碰到第四阶段那个老朋友：

# High-risk Tokens

---

# 七十二、Near Duplicate Detection 也必须保护：

```text
否定词
数字
金额
单位
比较符
日期
品牌型号
地域
评分值
```

---

# 七十三、所以不能因为：

```text
Similarity = 0.95
```

就直接删。

---

# 七十四、Similarity 只是：

# Candidate Generator

候选生成器。

不是：

# Final Truth

---

# 七十五、这是今天非常重要的一句话：

> **相似度负责告诉你“值得比较”，而不是负责替你决定“它们完全一样”。**

---

# 七十六、现在再看一个例子

A：

> 响应时间不得超过2小时。

B：

> 响应时间不得超过4小时。

---

# 七十七、两个句子只有一个字符不同。

文本相似度：

> 极高。

---

# 七十八、但业务条件：

> 差了一倍。

---

# 七十九、所以如果 Dedup 把它们合并，

你直接丢失：

> 真实业务差异。

---

# 八十、这说明 Near Dedup 必须有：

# Difference Awareness

不仅看：

> 像不像。

还要看：

> **到底哪里不一样。**

---

# 八十一、特别需要做：

```text
Numeric Diff
Comparator Diff
Negation Diff
Entity Diff
Unit Diff
```

---

# 八十二、例如：

```text
A:
不少于3年

B:
不少于5年
```

标记：

```text
text_similarity = high
numeric_difference = true
```

---

# 八十三、这种关系更适合叫：

```text
template_variant
```

而不是：

```text
duplicate
```

---

# 八十四、这就进入采购数据中特别重要的一类：

# Template Duplicate

模板重复。

---

# 八十五、政府采购文件大量使用模板。

例如 100 个项目都写：

```text
项目名称：XXX
项目编号：XXX
预算金额：XXX
```

---

# 八十六、甚至资格条件：

```text
供应商须具有独立承担民事责任的能力；
具有良好的商业信誉；
具有履行合同所必需的设备和专业技术能力；
……
```

很多文件：

> 大片完全相同。

---

# 八十七、还有招标机构自己的标准模板。

比如：

```text
采购人名称不同
项目名称不同
预算不同
日期不同
```

其余 90%：

> 一样。

---

# 八十八、如果按普通字符串比较

这些文件：

> 不是完全相同。

---

# 八十九、如果按语义比较

它们：

> 高度接近。

---

# 九十、从训练角度看

如果把 10,000 份模板全喂进去，

模型会不断看到：

> 同一结构。

---

# 九十一、这可能造成：

# Template Overweighting

模板过权重。

---

# 九十二、尤其如果某一个地区的数据：

> 特别容易爬取。

你可能无意中让模型学成：

> 某地区采购模板专家。

而不是：

> 全国政府采购专家。

---

# 九十三、所以 Dedup 其实也在解决：

# Sampling Bias

采样偏差。

---

# 九十四、例如：

```text
地区A
采集到30万份

地区B
采集到2万份
```

如果 A 大量使用统一模板，

模型看到的不是：

> 15 倍新的知识。

可能只是：

> 同一模板重复 15 倍。

---

# 九十五、这就是：

\[
\boxed{
Volume
\neq
Diversity
}
\]

---

# 九十六、对领域模型来说，

数据多当然重要。

但更重要的是：

# Information Diversity

信息多样性。

---

# 九十七、我们真正希望覆盖的是：

```text
不同地区
不同采购方式
不同项目类型
不同预算规模
不同风险类型
不同写法
不同边界案例
不同法规场景
```

而不是：

> 同一个模板复制 100 万次。

---

# 九十八、那么怎么发现 Template Duplicate？

一个方法是：

# Variable Masking

---

# 九十九、例如：

原文 A：

```text
项目编号：ABC-2026-001
预算金额：500万元
投标截止日期：2026年9月30日
```

B：

```text
项目编号：XYZ-2026-812
预算金额：800万元
投标截止日期：2026年10月8日
```

---

# 一百、我们可以产生一个：

# Template View

例如：

```text
项目编号：<PROJECT_ID>
预算金额：<AMOUNT>
投标截止日期：<DATE>
```

---

# 一百零一、于是 A 和 B 的 Template View：

> 完全一致。

---

# 一百零二、这说明：

> 它们高度可能来自同一模板。

---

# 一百零三、但是注意！

不能把这个 Template View：

> 替代原文。

---

# 一百零四、因为：

```text
500万元
```

和：

```text
800万元
```

业务意义仍然存在。

---

# 一百零五、所以正确架构是：

```text
raw_text
normalized_text
template_view
```

三个不同 View。

---

# 一百零六、其中：

```text
template_view
```

只用于：

> 检测结构重复。

---

# 一百零七、这就是 Multiple Views 思维再次出现。

---

# 一百零八、现在有一个问题：

哪些东西可以 Mask？

比如：

```text
项目名称
项目编号
日期
```

相对容易。

---

# 一百零九、那金额呢？

就要谨慎。

因为有些任务中：

> 金额是业务核心。

---

# 一百一十、例如：

> “注册资本不得低于5000万元。”

这里的：

```text
5000万元
```

不能简单 Mask 后就说：

> 和 500 万元完全一样。

---

# 一百一十一、Template Detection 可以说：

> 结构一样。

但业务内容层：

> 不是同一条样本。

---

# 一百一十二、因此最好同时保留两个判断：

```text
template_similarity
```

和：

```text
business_value_difference
```

---

# 一百一十三、例如：

```json
{
  "template_similarity": 0.99,
  "numeric_difference": true,
  "dedup_relation": "template_variant"
}
```

---

# 一百一十四、而不是：

```json
{
  "duplicate": true
}
```

一句话解决。

---

# 一百一十五、这就是专业 Dedup：

> **不是只有相似度，而是有重复关系类型。**

---

# 一百一十六、现在看 Version Duplicate

政府采购中特别常见：

```text
原招标文件
```

然后：

```text
更正公告
```

然后：

```text
更正后招标文件
```

---

# 一百一十七、两个版本可能有：

> 99.5% 内容一样。

只改了一句话：

```text
注册资本不得低于5000万元
```

变成：

```text
删除注册资本要求
```

---

# 一百一十八、如果 Near Dedup 系统看到：

```text
99.5%相似
```

直接删一个，

会发生什么？

---

# 一百一十九、你可能把整个：

# Correction Event

更正事件删掉。

---

# 一百二十、而这种数据：

> 恰恰极其有价值。

---

# 一百二十一、为什么？

因为：

> 原条件被官方修改，

本身可能说明：

> 这类条款存在问题或者需要调整。

---

# 一百二十二、所以：

# Version Similarity ≠ Duplicate

---

# 一百二十三、我们应该建立：

```text
version_of
```

关系。

---

# 一百二十四、例如：

```text
DOC_V1
   ↓ revised_by
DOC_V2
```

---

# 一百二十五、然后保存：

# Diff

到底改了什么。

---

# 一百二十六、比如：

```text
删除：
供应商注册资本不得低于5000万元。

新增：
供应商应具有履行合同所必需的能力。
```

这种信息：

> 对未来专家模型非常值钱。

---

# 一百二十七、所以去重时一定要先问：

> **这是重复，还是版本演化？**

---

# 一百二十八、这两种如果混：

> 会直接毁掉时间信息。

---

# 一百二十九、以后 RAG 也一样。

旧法规和新法规：

> 可能 95% 相同。

但你不能说：

> 相似，所以删掉旧的。

---

# 一百三十、因为法律知识需要：

```text
effective_from
effective_to
```

版本和时间：

> 本身就是知识。

---

# 一百三十一、第五阶段虽然主要讲训练数据，

但这个思维以后第六课：

> 法规 RAG

会非常重要。

---

# 一百三十二、现在进入一个经典文本方法：

# Shingling

这个词第一次看会陌生。

其实非常简单。

---

# 一百三十三、假设一句话：

```text
供应商必须具备相关资质
```

我们可以连续取若干字符。

比如 3 个字符一组：

```text
供应商
应商必
商必须
必须具
须具备
具备相
备相关
相关资
关资质
```

---

# 一百三十四、这些连续小片段：

> 就可以叫 Shingles。

---

# 一百三十五、然后比较两条文本的 Shingle 集合：

> 有多少相同。

---

# 一百三十六、这样比单纯看词：

> 对长文本局部重复非常好用。

---

# 一百三十七、例如两个招标文件：

90% 内容一样，

只改：

> 项目名称和日期。

它们的 Shingle：

> 会大量重合。

---

# 一百三十八、于是可以用：

# Jaccard Similarity

判断内容重合度。

---

# 一百三十九、但如果我们有：

```text
1,000,000 条 Clause
```

能不能每两条都比较？

---

# 一百四十、不能。

两两比较规模会爆炸。

直觉上：

```text
100万 × 100万
```

太大。

---

# 一百四十一、所以工程上需要：

# Approximate Search

近似候选检索。

---

# 一百四十二、这就是 MinHash 出现的地方。

不用现在学算法推导。

只记一个心智模型：

# MinHash = 给集合相似度做一个小指纹

---

# 一百四十三、原来每条文档可能有：

```text
数万个 Shingle
```

MinHash 把它压成：

> 一个较短的 Signature。

---

# 一百四十四、相似文本：

> Signature 也更容易相似。

---

# 一百四十五、于是系统可以快速找到：

> 值得做精确比较的候选。

---

# 一百四十六、所以：

```text
Shingle
+
MinHash
+
LSH
```

经常用于：

> 大规模文本近重复检测。

---

# 一百四十七、LSH 又是什么？

先不用学数学。

可以理解成：

> **把可能相似的东西尽量扔到同一个桶里。**

---

# 一百四十八、于是：

```text
100万条数据
```

不用：

> 全部彼此比较。

只比较：

> 同桶候选。

---

# 一百四十九、这就像：

100 万个人找长得像的人。

不是：

> 每个人和另外 999,999 人握手比较。

而是先按：

```text
大概特征
```

分组。

---

# 一百五十、再在组内：

> 精细比较。

---

# 一百五十一、所以一个工程流程可以是：

```text
Clean Text
   ↓
Shingle
   ↓
MinHash Signature
   ↓
LSH Candidate Search
   ↓
Exact Similarity
   ↓
Business Difference Check
```

---

# 一百五十二、最后那一步：

# Business Difference Check

特别重要。

因为算法只知道：

> 字很像。

它不知道：

```text
2小时
```

和：

```text
24小时
```

可能是本质差异。

---

# 一百五十三、除了 MinHash，还有：

# SimHash

也是一种近重复指纹思路。

---

# 一百五十四、非常粗略地理解：

MinHash 更适合：

> 集合重合。

SimHash 更像：

> 给文本整体特征生成一个二进制指纹。

---

# 一百五十五、相似文本的 SimHash：

> 汉明距离通常较近。

---

# 一百五十六、现在不用比较：

> 哪个算法“最好”。

因为真实系统：

> 经常多种策略并用。

---

# 一百五十七、例如：

```text
File SHA-256
→ 找完全文件重复

Normalized Text Hash
→ 找完全正文重复

MinHash
→ 找高文本重叠

Embedding
→ 找语义近似
```

---

# 一百五十八、这就是：

# Multi-stage Dedup

多阶段去重。

---

# 一百五十九、现在说 Embedding。

第二课里我们已经学过：

> 文本可以映射到向量空间。

---

# 一百六十、那么：

> “供应商必须在本市设立服务机构”

和：

> “投标人须于项目所在地设置固定售后机构”

Embedding：

> 可能非常接近。

---

# 一百六十一、这非常适合发现：

# Paraphrase Duplicate

同义改写近重复。

---

# 一百六十二、但这里又有一个巨坑。

A：

> 本项目接受联合体投标。

B：

> 本项目不接受联合体投标。

---

# 一百六十三、语义主题极其接近。

Embedding：

> 很可能也非常近。

---

# 一百六十四、但业务含义：

> 相反。

---

# 一百六十五、所以再强调一次：

\[
\boxed{
EmbeddingSimilarity
\neq
BusinessEquivalence
}
\]

---

# 一百六十六、Embedding 最适合：

> 找候选。

不适合单独承担：

> 自动删除裁判。

---

# 一百六十七、特别是政府采购这种：

> 数字、否定、条件范围特别重要的领域。

---

# 一百六十八、一个更稳健的策略：

```text
Embedding高相似
        ↓
文本Diff
        ↓
关键字段Diff
        ↓
规则判断
        ↓
必要时人工复核
```

---

# 一百六十九、例如：

```text
Similarity = 0.98
```

但是发现：

```text
numeric_difference = true
```

那么不要合并。

---

# 一百七十、又例如：

```text
Similarity = 0.99
```

但是：

```text
negation_difference = true
```

直接：

> 高风险。

---

# 一百七十一、所以我们可以建立：

# Dedup Guardrails

---

# 一百七十二、保护项可以包括：

```text
数字
单位
比较符
否定词
日期
分值
项目地域
品牌型号
法规条号
```

---

# 一百七十三、这和第四阶段的 Semantic Guardrail：

> 直接复用。

---

# 一百七十四、好的数据工程是这样的：

前面建立的能力，

后面：

> 一直复用。

而不是每阶段重新发明一套。

---

# 一百七十五、现在讲 Canonical Record

假设发现三个完全重复文档：

```text
D1
官网PDF

D2
镜像网站PDF

D3
第三方转载PDF
```

应该留谁？

---

# 一百七十六、优先考虑：

```text
Source Authority
```

---

# 一百七十七、然后：

```text
Parse Quality
```

---

# 一百七十八、再考虑：

```text
Completeness
```

---

# 一百七十九、再考虑：

```text
Metadata Quality
```

---

# 一百八十、例如：

```text
D1
官方来源
解析质量0.98
有发布日期
```

通常就比：

```text
D3
第三方转载
无来源时间
```

更适合当：

> Canonical。

---

# 一百八十一、所以 Canonical Selection：

> 不是随机留第一条。

---

# 一百八十二、可以有一个优先级：

```text
Official Source
    >
Verified Mirror
    >
Unknown Repost
```

再结合：

> 解析质量。

---

# 一百八十三、但是其它 Record：

> 不要一定删除。

可以保存：

```text
duplicate_of = D1
```

---

# 一百八十四、为什么？

因为未来我们可能需要：

> 检查数据来源。

---

# 一百八十五、或者发现：

> D1 后来网页下线了。

D2：

> 仍然可以提供证据。

---

# 一百八十六、所以 Master Data：

> 保留多来源关系。

Training View：

> 去重。

这是很好的架构。

---

# 一百八十七、现在进入 Cluster 思维。

如果：

```text
A重复B
B重复C
```

那不能只保存：

```text
A→B
B→C
```

更好是形成：

# Duplicate Group

---

# 一百八十八、例如：

```text
duplicate_group_id:
DG-000137
```

里面：

```text
A
B
C
D
```

---

# 一百八十九、其中：

```text
canonical_id = A
```

其它：

```text
member_of = DG-000137
```

---

# 一百九十、这对后面数据切分：

> 极其重要。

---

# 一百九十一、为什么？

如果：

```text
A → Train
```

而：

```text
B → Test
```

模型考试时：

> 几乎已经见过答案。

---

# 一百九十二、所以后面第 6 阶段切数据的时候：

# Duplicate Group 必须作为一个 Split Group

---

# 一百九十三、也就是：

```text
DG-000137
```

里面所有成员：

> 必须一起去 Train，

或者一起：

> 去 Test。

不能拆开。

---

# 一百九十四、这一点非常关键。

即使 Training View 最后只取 Canonical，

我们仍然应该保留：

```text
duplicate_group_id
```

---

# 一百九十五、因为 Near Duplicate：

> 可能并没有真正被删除。

但它们仍然：

> 不应该跨 Split。

---

# 一百九十六、这就是今天和第 6、7 阶段的连接点。

---

# 一百九十七、现在看为什么随机切分特别危险。

假设一个模板：

> 被使用了 1000 次。

---

# 一百九十八、随机做：

```text
80% Train
20% Test
```

那么大概：

```text
800个模板变体
→ Train

200个模板变体
→ Test
```

---

# 一百九十九、模型考试看到：

> 几乎一模一样的结构。

---

# 二百、最后 Accuracy：

```text
97%
```

团队非常开心。

---

# 二百零一、但模型真正遇到新模板：

> 可能只有 65%。

---

# 二百零二、这叫：

# Template Leakage

模板泄漏。

---

# 二百零三、它比完全相同文本泄漏：

> 更难发现。

因为：

```text
text1 != text2
```

---

# 二百零四、传统 `drop_duplicates()`：

> 完全抓不到。

---

# 二百零五、所以 Procurement Benchmark：

> 必须考虑近重复和模板重复。

---

# 二百零六、这是第五阶段最重要的成果之一。

---

# 二百零七、再看法律文本。

多个招标文件都引用：

> 同一个法规原文。

例如某一条法律规定：

> 在 5000 份采购文件里被重复引用。

---

# 二百零八、这些引用要不要：

> 全部删成一份？

取决于任务。

---

# 二百零九、如果做：

# Regulation Corpus

那同一法规正文：

> 一份权威源即可。

---

# 二百一十、如果做：

# Procurement Document Understanding

文档里有没有引用某法规：

> 可能本身就是上下文。

所以不能简单删。

---

# 二百一十一、再次说明：

# Dedup Unit Matters

你是在去重：

```text
法规知识
```

还是：

```text
采购项目观察
```

完全不一样。

---

# 二百一十二、所以每个 Dataset View：

> 可以有自己的 Dedup Policy。

---

# 二百一十三、例如：

### RAG Knowledge Corpus

可以对相同法规条文：

> 强去重。

---

# 二百一十四、### SFT Dataset

高度重复的标准答案：

> 可以采样降权。

---

# 二百一十五、### Evaluation Gold Set

需要：

> 严格控制模板近重复。

---

# 二百一十六、### Statistical Analysis

可能要保留：

> 自然重复频率。

---

# 二百一十七、这就是为什么：

> “去重率越高越专业”

是错的。

---

# 二百一十八、有的团队喜欢说：

> “我们把 70% 数据都去掉了，数据非常纯。”

这句话：

> 本身没有意义。

---

# 二百一十九、正确问题应该是：

> **你删掉的 70% 到底是什么关系？**

---

# 二百二十、如果删掉的是：

```text
镜像
重复下载
Parser Duplicate
```

很好。

---

# 二百二十一、如果删掉的是：

> 真实发生于不同项目的 Hard Cases，

那：

> 可能反而毁了数据。

---

# 二百二十二、现在看重复和 Label 的关系。

假设：

A：

```text
供应商须在本市注册。
```

Label：

```text
potential_risk
```

---

# 二百二十三、B 的文本完全一样：

```text
供应商须在本市注册。
```

但专家标成：

```text
no_risk
```

---

# 二百二十四、这时候系统不能：

> 直接随机留一条。

因为这暴露了：

# Label Conflict

---

# 二百二十五、可能原因：

```text
标注错误
上下文不同
Schema版本不同
专家意见不同
```

---

# 二百二十六、所以重复检测还能帮助：

# Data Quality Audit

---

# 二百二十七、如果相同 Clause：

> Label 不一致，

应该产生：

```text
DUPLICATE_LABEL_CONFLICT
```

---

# 二百二十八、然后进入：

> 人工复核。

---

# 二百二十九、这特别重要。

因为重复不仅是：

> 要删的垃圾。

它还可以暴露：

> 标注问题。

---

# 二百三十、再例如：

同一个条款：

A 的上下文是：

```text
资格条件
```

B 的上下文是：

```text
合同履约
```

---

# 二百三十一、虽然 `clause_text` 一样，

Label 不同：

> 可能完全合理。

---

# 二百三十二、所以 Dedup 不能只比较：

```text
clause_text
```

还要保存：

```text
section_type
context
project_context
```

---

# 二百三十三、这说明：

# Text Equality ≠ Sample Equality

---

# 二百三十四、第一阶段我们定义 Sample：

```text
Clause
+
Context
+
Source
+
Annotation
```

今天终于看到为什么：

> 这些字段一个都不能随便扔。

---

# 二百三十五、现在再看 Hard Negative。

假设：

A：

> 供应商必须在本市设立服务机构。

Label：

> Potential Risk。

---

# 二百三十六、B：

> 供应商无须在本市设立服务机构，但应保证2小时内提供现场服务。

Label：

> 需要结合履约场景判断。

---

# 二百三十七、这两条词汇高度相似。

一个差的 Near Dedup：

> 可能删掉 B。

---

# 二百三十八、但 B 恰恰是：

# Hard Negative / Boundary Case

非常有价值。

---

# 二百三十九、所以近重复检测要特别保护：

> **标签边界附近的数据。**

---

# 二百四十、这也是为什么：

# Rare Hard Cases > Repeated Easy Cases

对于专业模型训练往往很重要。

---

# 二百四十一、以后第 10 阶段：

> Hard Negative

会专门展开。

今天先记住：

> 不要因为文字相似，就把最宝贵的边界案例删掉。

---

# 二百四十二、现在建立第一版 Dedup Pipeline。

```text
CleanClauseSet
       │
       ▼
Exact File Hash
       │
       ▼
Exact Text Hash
       │
       ▼
Normalized Text Hash
       │
       ▼
Template Fingerprint
       │
       ▼
MinHash / Similarity Candidate
       │
       ▼
Embedding Candidate
       │
       ▼
Critical Field Diff
       │
       ▼
Duplicate Relation Classification
       │
       ▼
Duplicate Cluster
       │
       ▼
Canonical Selection
       │
       ▼
DedupedClauseSet_V0.1
```

---

# 二百四十三、注意这个 Pipeline 不是说：

> 所有项目一定要同时用所有算法。

第一版：

> 可以从简单开始。

---

# 二百四十四、第一版非常合理的路线可能是：

```text
1. File SHA-256
2. Exact normalized_text hash
3. High-overlap MinHash
4. Critical-field difference
5. Cluster
```

---

# 二百四十五、等数据量变大以后：

再增加：

```text
Embedding Near-Duplicate
```

---

# 二百四十六、这是一个重要工程原则：

# Start Simple, Measure Errors

---

# 二百四十七、不要第一天就搞：

> 17 种相似度算法 + 神经网络 Dedup。

---

# 二百四十八、先做一个：

> 可解释、能 Benchmark 的 Baseline。

---

# 二百四十九、然后看：

```text
False Merge
```

和：

```text
Missed Duplicate
```

---

# 二百五十、什么叫 False Merge？

系统认为：

> 两条重复。

实际上：

> 有重要差异。

---

# 二百五十一、例如：

```text
不少于3年
```

和：

```text
不少于5年
```

被合并。

这是：

> 非常危险的 False Merge。

---

# 二百五十二、什么叫 Missed Duplicate？

实际上：

> 同一份内容。

系统没有发现。

---

# 二百五十三、例如：

```text
HTML正文
```

和：

```text
PDF正文
```

只有空格和格式不同。

系统没认出来。

---

# 二百五十四、对于我们的项目：

两种错误：

> 风险并不相同。

---

# 二百五十五、False Merge 往往更危险。

因为：

> 它会永久丢掉真实差异。

---

# 二百五十六、Missed Duplicate：

> 更多是冗余和泄漏风险。

---

# 二百五十七、所以 Dedup 阈值应该：

> 偏保守。

---

# 二百五十八、特别是业务关键数据：

> 宁可先保留相似样本并标 Group，

也不要过早删除。

---

# 二百五十九、这就是：

# Cluster First, Delete Later

特别推荐记住。

---

# 二百六十、可以压成：

\[
\boxed{
Detect
\rightarrow
Link
\rightarrow
Cluster
\rightarrow
Decide
}
\]

不是：

\[
\boxed{
Detect
\rightarrow
Delete
}
\]

---

# 二百六十一、现在设计 `DuplicateRelation`

可以概念上有：

```text
exact_file_duplicate
exact_text_duplicate
format_variant
mirror_copy
template_variant
near_duplicate
revised_version
possible_duplicate
```

---

# 二百六十二、还可以有：

```text
not_duplicate
```

用于：

> 人工确认后排除。

---

# 二百六十三、为什么保存：

```text
not_duplicate
```

也有价值？

因为系统下一版运行时：

> 不应该每次重新怀疑同一对样本。

---

# 二百六十四、这叫：

# Adjudicated Pair

人工裁决过的 Pair。

---

# 二百六十五、以后这些 Pair：

> 还能成为 Dedup 算法自己的 Gold Set。

---

# 二百六十六、例如人工标：

```text
Pair 1:
duplicate

Pair 2:
template_variant

Pair 3:
not_duplicate
```

---

# 二百六十七、然后评测 Dedup Algorithm：

```text
Precision
Recall
```

---

# 二百六十八、和第一课学的一样。

---

# 二百六十九、如果系统说：

> 100 对是 Duplicate。

其中：

> 95 对真的重复。

Dedup Precision：

> 很高。

---

# 二百七十、如果真实共有：

> 200 对 Duplicate，

系统只找到：

> 100 对。

Recall：

> 就不高。

---

# 二百七十一、对删除型 Dedup：

> Precision 尤其重要。

为什么？

因为 False Positive：

> 会误删数据。

---

# 二百七十二、所以我们通常不希望：

> “宁可多删一点。”

---

# 二百七十三、而更倾向：

> **宁可把不确定的留作 Cluster Candidate。**

---

# 二百七十四、现在看一个 Procurement Dedup Gold Set 应该覆盖什么？

至少包括：

```text
完全重复文件
不同格式同内容
镜像网页
空格/标点差异
项目名称替换
日期替换
金额替换
数字条件变化
否定词变化
更正版本
模板复用
同义改写
Hard Negative
```

---

# 二百七十五、特别是：

```text
2小时
vs
4小时
```

---

# 二百七十六、

```text
不得
vs
应当
```

---

# 二百七十七、

```text
本市
vs
项目所在地
```

---

# 二百七十八、

```text
500万元
vs
5000万元
```

这些必须：

> 专门测试。

---

# 二百七十九、否则一个普通互联网文本 Dedup 方法：

> 在采购数据上可能非常危险。

---

# 二百八十、现在设计第一版 `DedupedClauseSet_V0.1`。

例如：

```json
{
  "clause_id": "CLAUSE-00178",

  "duplicate_group_id": "DG-000031",

  "canonical_clause_id": "CLAUSE-00178",

  "dedup_relation": "canonical",

  "template_group_id": "TG-000712",

  "exact_text_hash": "sha256:...",

  "similarity": {
    "jaccard": null,
    "embedding": null
  },

  "critical_differences": [],

  "dedup_status": "verified",

  "dedup_version": "dedup_v0.1"
}
```

---

# 二百八十一、另一个成员：

```json
{
  "clause_id": "CLAUSE-08317",

  "duplicate_group_id": "DG-000031",

  "canonical_clause_id": "CLAUSE-00178",

  "dedup_relation": "exact_text_duplicate",

  "dedup_status": "auto_verified"
}
```

---

# 二百八十二、模板相同但金额不同：

```json
{
  "clause_id": "CLAUSE-10291",

  "duplicate_group_id": null,

  "template_group_id": "TG-000712",

  "dedup_relation": "template_variant",

  "critical_differences": [
    "amount"
  ]
}
```

---

# 二百八十三、看到区别了吗？

它并没有：

> 被删除。

---

# 二百八十四、只是知道：

> 和谁同模板。

这对 Stage 6：

> Split

非常有价值。

---

# 二百八十五、后面我们甚至可以决定：

```text
同一个template_group
尽量不要同时跨Train/Test
```

---

# 二百八十六、这会显著减少：

# Template Leakage

---

# 二百八十七、现在谈 Dedup Version。

和前面一样：

```text
dedup_v0.1
```

以后可能升级：

```text
dedup_v0.2
```

---

# 二百八十八、为什么？

因为阈值会变。

算法会变。

Template Mask 规则会变。

---

# 二百八十九、同一个 Pair：

v0.1 可能认为：

```text
near_duplicate
```

v0.2 可能认为：

```text
template_variant
```

---

# 二百九十、所以每条决定：

> 必须知道是哪一版 Dedup Pipeline 产生的。

---

# 二百九十一、现在 Stage 1～5 已经有：

```text
schema_version
parser_version
structure_version
normalizer_version
dedup_version
```

---

# 二百九十二、到了第 11 阶段，

这些会被正式组织成：

# Dataset Lineage

---

# 二百九十三、现在说一个特别容易误解的地方：

# 去重不是为了让数据数量变小

数据变小只是：

> 副作用。

---

# 二百九十四、真正目标是让：

```text
样本权重更合理
信息多样性更高
评测更诚实
训练更高效
```

---

# 二百九十五、如果最后：

```text
100万
↓
92万
```

但 92 万信息质量很好：

> 完全没问题。

---

# 二百九十六、如果：

```text
100万
↓
20万
```

也不一定：

> 就更高级。

---

# 二百九十七、核心不是：

> 去掉多少。

而是：

> 去掉了什么。

---

# 二百九十八、现在看训练层面的影响。

假设有：

```text
10万条普通标准条款
```

重复很多。

而：

```text
1000条技术参数倾向性Hard Case
```

非常少。

---

# 二百九十九、不做 Dedup / Reweight：

模型训练梯度大量来自：

> 简单标准条款。

---

# 三百、模型最后可能表现：

```text
普通资格条件：
99%

复杂技术参数：
55%
```

---

# 三百零一、总体 Accuracy：

> 看起来很高。

---

# 三百零二、实际业务：

> 关键地方很差。

---

# 三百零三、所以 Dedup 和 Rebalancing：

> 会直接影响模型学什么。

---

# 三百零四、但注意：

# Dedup ≠ Class Balancing

这是两个问题。

---

# 三百零五、Dedup：

> 控制重复信息。

---

# 三百零六、Class Balancing：

> 控制不同 Label / Risk Type 的训练比例。

---

# 三百零七、后面构造 Dataset 时：

> 可能两者都要做。

不要混。

---

# 三百零八、现在看 RAG。

如果向量数据库里：

> 同一法规条款存了 30 份。

用户检索一次：

Top 10 结果可能全是：

> 同一句法规。

---

# 三百零九、结果：

> 检索多样性极差。

---

# 三百一十、于是 Dedup 也能改善：

# Retrieval Diversity

---

# 三百一十一、但如果 30 份来自：

> 30 个不同监管案例，

每个案例虽然引用同一法规，

案例上下文：

> 仍然不同。

---

# 三百一十二、所以 RAG 可能去重：

> 法规原文。

但保留：

> 不同案例。

---

# 三百一十三、再次体现：

# Entity-aware Dedup

按数据实体类型：

> 定义不同策略。

---

# 三百一十四、未来我们的 Master Data 可能有：

```text
Regulation
Project
Document
Clause
Case
Annotation
```

每种 Entity：

> Dedup Policy 不一样。

---

# 三百一十五、现在做几个思维实验。

### 思维实验 A

两个 PDF 的 SHA-256 一样。

它们是不是可以认为文件完全相同？

> 是，工程上可以极高置信度认为是 Exact File Duplicate。

---

# 三百一十六、### 思维实验 B

两个文件 Hash 不同。

正文是不是一定不同？

> 不是。

PDF Metadata、封装方式、HTML 模板都可能导致 Hash 不同。

---

# 三百一十七、### 思维实验 C

两个 Clause 文字完全相同，

但属于两个不同采购项目。

是不是应该物理删除一个？

> 不一定。

先看数据用途和是否属于自然重复。

---

# 三百一十八、### 思维实验 D

A：

```text
不少于3年
```

B：

```text
不少于5年
```

文本极其相似。

是不是 Near Duplicate？

> 可以是模板近重复。

但绝不能当业务等价 Duplicate 删除。

---

# 三百一十九、### 思维实验 E

两个招标文件 99.8% 相同，

其中一个是更正后版本。

删旧版本？

> 不应简单当重复处理。

应该建立 Version Relation。

---

# 三百二十、### 思维实验 F

Embedding Similarity = 0.99。

是不是可以自动删除一条？

> 不能。

需要检查数字、否定词、单位、比较符等业务关键差异。

---

# 三百二十一、### 思维实验 G

同一个模板在 1000 个项目中出现。

能不能让 800 个进 Train、200 个进 Test？

> 这可能造成严重 Template Leakage。

---

# 三百二十二、### 思维实验 H

同一法规在 5000 个采购文件里被引用。

是不是全都只留一次？

> 要看任务。

法规知识库和项目分析数据的去重目标不同。

---

# 三百二十三、### 思维实验 I

两条完全相同文本的 Label 不同。

应该随机保留一个吗？

> 不应该。

这是 Label Conflict，需要调查 Context 和标注来源。

---

# 三百二十四、### 思维实验 J

一条边界样本与常规样本 95% 相似。

是不是优先删边界样本？

> 恰恰相反。边界样本通常更有价值。

---

# 三百二十五、本阶段最容易犯的 12 个错误

**错误 1：**

> `drop_duplicates()` 就完成去重。

错。

---

**错误 2：**

> SHA-256 能发现所有重复。

错。

它只能非常好地发现完全文件重复。

---

**错误 3：**

> 文本一样就一定是同一个业务观察。

错。

---

**错误 4：**

> 相似度高就可以删除。

错。

---

**错误 5：**

> Embedding 很智能，所以最适合直接做删除决定。

危险。

---

**错误 6：**

> 数字差异很小，可以忽略。

错。

---

**错误 7：**

> 99% 相同的更正版本属于无用重复。

错。

---

**错误 8：**

> 模板重复只影响训练速度。

错。

还会制造模型偏差和 Benchmark 泄漏。

---

**错误 9：**

> 去重率越高，数据越专业。

错。

---

**错误 10：**

> 检测到重复就应该立刻物理删除。

错。

优先 Cluster / Link。

---

**错误 11：**

> Dedup 只影响训练集。

错。

它对 Evaluation 和 RAG 一样重要。

---

**错误 12：**

> 完全相同文本的不同 Label，任选一个即可。

错。

这可能暴露标注冲突。

---

# 三百二十六、本阶段最重要的 6 个“≠”

```text
File Difference
≠
Content Difference
```

```text
Text Duplicate
≠
Observation Duplicate
```

```text
Similarity
≠
Equivalence
```

```text
Template Similarity
≠
Business Equality
```

```text
Version Similarity
≠
Duplicate
```

```text
More Rows
≠
More Independent Information
```

---

# 三百二十七、再记一个非常重要的“=”

\[
\boxed{
GoodDedup
=
DuplicateDetection
+
RelationshipClassification
+
CriticalDifferenceProtection
+
ProvenancePreservation
}
\]

翻译成人话：

> **好的去重不是“把相似文本删掉”，而是先判断哪些数据彼此相关、它们到底是什么重复关系、有没有关键业务差异，再决定哪些只在训练 View 中降权或只保留代表样本，同时完整保留来源关系。**

---

# 三百二十八、现在把第四课前五阶段连起来

```text
Stage 1
Task Schema
“什么是一条样本？”
       │
       ▼
Stage 2
ParsedDocument
“文件里到底有什么？”
       │
       ▼
Stage 3
ClauseUnit
“文字属于哪一条业务要求？”
       │
       ▼
Stage 4
CleanClause
“怎样安全规范表示？”
       │
       ▼
Stage 5
DedupedClauseSet
“这些样本到底有多少独立信息？”
```

---

# 三百二十九、现在我们已经解决了：

```text
数据是什么
文本对不对
结构对不对
格式稳不稳
重复多不多
```

但还没有解决一个极其致命的问题：

# 这些数据怎样切 Train / Validation / Test？

---

# 三百三十、很多人会直接：

```python
train_test_split(
    data,
    test_size=0.2,
    random_state=42
)
```

看起来非常标准。

---

# 三百三十一、但对于 ProcurementAI，

如果按行随机切：

> 很可能直接把整个 Benchmark 做假。

---

# 三百三十二、因为同一个项目可能有：

```text
300个Clause
```

随机切以后：

```text
240条进Train
60条进Test
```

---

# 三百三十三、模型考试的时候虽然没见过：

> Test 的具体那句话。

但是它已经见过：

```text
项目名称
项目背景
模板风格
相关条款
大量相邻内容
```

---

# 三百三十四、更麻烦的是：

同一个 Template Group：

> 也可能跨 Train/Test。

---

# 三百三十五、所以真正正确的数据切分必须考虑：

```text
Project Group
Document Group
Duplicate Group
Template Group
Time
```

---

# 三百三十六、本阶段掌握测试

如果现在不看前文，你能完整解释下面这些问题，第 5 阶段就真正掌握了：

> 为什么数据行数不等于独立信息量？

> 什么是 Exact File Duplicate？

> SHA-256 能解决哪一层去重？

> 为什么文件 Hash 不同不代表正文不同？

> File Duplicate 和 Content Duplicate 有什么区别？

> 为什么需要 Document-level 和 Clause-level Dedup？

> Text Duplicate 和 Observation Duplicate 为什么不同？

> 什么是 Natural Repetition？

> 什么是 Artificial Duplication？

> 为什么真正优先去掉的是人工采集过程制造的重复？

> 为什么 Dedup Policy 必须根据 Dataset Purpose 决定？

> 为什么检测到 Duplicate 不应该立即物理删除？

> 什么是 Canonical Record？

> 为什么要建立 Duplicate Group？

> 什么叫 Near Duplicate？

> Jaccard Similarity 的直觉是什么？

> 为什么高 Jaccard 相似度不等于业务等价？

> 为什么 `不得` 和 `必须` 是 Dedup 中必须保护的差异？

> 为什么 `2小时` 和 `4小时` 不能因为文本高度相似而合并？

> 什么叫 Template Duplicate？

> 为什么采购数据里模板重复特别常见？

> 什么是 Template View？

> 为什么 Template View 只能用于检测，不能替代原文？

> 为什么数字 Mask 必须谨慎？

> 什么叫 Version Duplicate / Version Relation？

> 为什么更正前后文件不能简单去重？

> 什么是 Shingle？

> MinHash 的核心用途是什么？

> 为什么大规模数据不能全部两两比较？

> LSH 的直觉是什么？

> Embedding 可以在 Near Dedup 中做什么？

> 为什么 Embedding Similarity 不等于 Business Equivalence？

> 什么是 Critical Field Diff？

> 为什么应该先 Cluster，再 Delete？

> Duplicate Group 为什么以后必须参与 Train/Test Split？

> 什么是 Template Leakage？

> 为什么同一个模板随机进入 Train 和 Test 会导致虚假高分？

> 为什么不同数据实体需要不同 Dedup Policy？

> 为什么相同文本、不同 Label 应该触发 Label Conflict Review？

> 为什么边界案例不能因为和普通样本相似就删除？

> 什么叫 False Merge？

> 什么叫 Missed Duplicate？

> 对政府采购数据来说，为什么 False Merge 往往特别危险？

> 为什么 Dedup Algorithm 自己也需要 Gold Set 和 Benchmark？

> 为什么 Dedup 和 Class Balancing 不是一回事？

如果这些你都能讲清楚：

\[
\boxed{
第四课第5阶段真正掌握
}
\]

---

# 三百三十七、本阶段最终只记一句话

> **政府采购数据去重的目标不是“把相似文本删掉”，而是识别同一文件、同一正文、同一模板、同一版本链和语义近重复之间的关系，保护数字、否定词、单位和条件等关键业务差异，并通过 Duplicate Group 控制重复信息对训练权重和 Benchmark 的污染。**

最后压成一张图：

```text
                   CleanClauseSet
                         │
                         ▼
                Exact File Duplicate
                         │
                         ▼
                 Exact Text Duplicate
                         │
                         ▼
                   Near Duplicate
            ┌────────────┼─────────────┐
            ▼            ▼             ▼
         MinHash      Template       Embedding
            │            │             │
            └────────────┼─────────────┘
                         ▼
                 Critical Field Diff
            ┌────────────┼─────────────┐
            ▼            ▼             ▼
          数字          否定词         单位/符号
            │            │             │
            └────────────┼─────────────┘
                         ▼
             Duplicate Relation Type
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
       Exact          Template        Version
      Duplicate        Variant        Relation
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                  Duplicate Cluster
                         │
                         ▼
                 Canonical Selection
                         │
                         ▼
                DedupedClauseSet_V0.1
```

---

# 下一阶段：第四课 · 第 6 阶段
## Train / Validation / Test 到底应该怎么切？为什么对政府采购数据“随机按行切 8:1:1”可能从根本上就是错的？

第 6 阶段我们会第一次真正建立：

# Data Split

但不会只讲：

```text
80%
10%
10%
```

真正重要的是：

> **什么东西绝对不能被拆到两个数据集里。**

我们会把今天得到的：

```text
duplicate_group_id
template_group_id
```

和之前已经保存的：

```text
project_id
document_id
```

真正串起来。

最终会建立：

```text
Project-aware Split
+
Duplicate-aware Split
+
Template-aware Split
+
Time-aware Split
```

并第一次回答这个最核心的问题：

> **测试集到底应该模拟“同一批项目里的陌生条款”，还是模拟“未来真正从未见过的新项目”？**

第 6 阶段最终会产出：

# `DatasetSplit_V0.1`

也就是第一次把数据从“整理好的样本库”，推进成：

> **可以开始严肃训练和评测的 Train / Validation / Test 数据结构。**

---
