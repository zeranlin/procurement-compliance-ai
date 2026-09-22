# 第六课 · 第 2 阶段
# Knowledge Base：法规、采购文件与知识版本怎样进入 RAG？
## 在研究“怎么检索”以前，先保证我们检索的东西是真的、有效的、能追溯的

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：MEDIUM。** 审计原因：核心心智模型出现偏后，阅读前段缺少认知锚点；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，RAG Knowledge Base 不是 PDF 文件夹，而是“正文 + Metadata + Provenance + Version + Validity”组成的可治理知识系统。**
2. **第二，每一份知识都必须能够从 Chunk 追溯到 Document，再追溯到原始 Source；否则 Citation 只是表面上有链接，并不是真正可审计。**
3. **第三，政府采购知识天然带时间和辖区条件，所以 effective_from / effective_to / jurisdiction / validity_status 必须成为一等字段。**
4. **第四，新版本不能简单覆盖旧版本；真正的版本管理要保留 supersedes / superseded_by 等关系，因为最新版本不一定是历史问题的正确版本。**
5. **第五，Metadata、去重、有效性审查和来源验证不是 Embedding 之前的杂活，它们直接决定未来 Retriever 有没有机会找到正确证据。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Metadata` | 元数据：项目、来源、时间、地区、版本等辅助信息 |
| `Embedding` | 嵌入：把离散 Token 映射到连续高维向量 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `Rank` | LoRA Rank：低秩增量的容量参数 |
| `Reranker` | 重排器：对初筛候选做更精细相关性排序 |
| `Chunking` | 分块：把长文档切成适合检索和上下文组装的片段 |
| `Deduplication` | 去重：识别并处理完全重复或近似重复的数据 |

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

第 1 阶段我们已经建立：

\[
\boxed{
RAG
=
Retrieve\ Evidence
+
Add\ Evidence\ to\ Context
+
Generate
}
\]

这里有一个特别容易被忽略的前提：

> **Evidence 本身必须可信。**

如果知识库里装的是：

```text
过期法规
+
来源不明转载
+
同一文件的三个版本
+
已经废止但没有标记的条款
+
解析错位的PDF文本
```

那么后面即使：

```text
Embedding 很强
Retriever 很准
Reranker 很聪明
```

也只是在：

> **更高效地找到错误证据。**

所以这一阶段先不碰 Embedding。

我们真正要建立的是：

# `ProcurementKnowledgeBase_V0.1`

---

## 一、知识库不是“一个放 PDF 的文件夹”

这是本阶段第一条必须锁死的心智模型。

最原始的做法可能是：

```text
knowledge/
├── 法规A.pdf
├── 法规B.pdf
├── 政策C.docx
└── 案例D.html
```

这叫：

> 文档集合。

但它还不能称为一个成熟的 RAG Knowledge Base。

真正的知识库至少要知道：

```text
这是什么文件？
谁发布的？
什么时候发布？
什么时候生效？
适用于哪里？
当前是否仍有效？
它是哪一个版本？
原始来源在哪里？
解析后的文本来自哪一页？
有没有后续文件替代它？
```

所以更准确地说：

\[
\boxed{
KnowledgeBase
=
Content
+
Metadata
+
Provenance
+
Version
+
Validity
}
\]

中文就是：

> **正文 + 元数据 + 来源链 + 版本关系 + 有效性信息。**

---

## 二、先把 Source of Truth 建起来

对于政府采购 RAG，最危险的一件事就是：

> 搜到一篇内容看起来很像法规的网页，就直接入库。

我们必须先建立：

# Source of Truth
## 权威来源原则

一个文档进入正式知识库前，至少应该保留：

| 字段 | 含义 |
|---|---|
| `source_id` | 我们系统内部的唯一来源 ID |
| `source_url` / `document_id` | 原始来源位置 |
| `issuer` | 发布主体 |
| `title` | 文件正式标题 |
| `document_number` | 文号，如果存在 |
| `publication_date` | 发布日期 |
| `retrieved_at` | 我们抓取 / 入库时间 |
| `source_hash` | 原始文件内容哈希 |
| `source_type` | 法律、规章、政策、采购文件、案例等 |

其中最重要的一条不是标题。

而是：

> **我们能不能从当前知识条目一路追溯回原始来源。**

这叫：

# Provenance
## 数据来源链 / 证据溯源

以后模型引用某一条内容时，我们最终要能够回答：

> 这段文字到底是从哪份原始文件来的？

---

## 三、Document Identity：同名文件不一定是同一份知识

假设我们看到：

```text
《某某政府采购管理办法》
```

不能只拿标题当主键。

因为可能存在：

```text
2019版
2022修订版
2025修订版
```

甚至可能：

```text
不同地区
标题非常相似
```

所以真正的文档身份更接近：

\[
DocumentIdentity
=
(
Issuer,
DocumentNumber,
Title,
Version,
Jurisdiction
)
\]

工程上不一定真的用这个 Tuple 当数据库主键，

但心智模型必须如此。

否则最危险的情况是：

> 新版本入库时直接覆盖旧版本。

然后以后有人问：

> “2022 年当时适用什么规定？”

知识库已经无法回答。

---

## 四、时间是政府采购知识库的一等公民

RAG 中很多知识库只保存：

```text
title
text
```

政府采购场景远远不够。

我们至少需要区分：

```text
publication_date
effective_from
effective_to
repeal_date
retrieved_at
```

因为这些时间不是一回事。

例如：

```text
2026-01-01
发布

2026-03-01
正式生效
```

那么在：

```text
2026-02-15
```

做历史判断时，

不能因为文件已经发布：

> 就默认它已经生效。

所以知识查询实际上经常包含一个隐含条件：

\[
\boxed{
Evidence
必须满足
ValidAt(QueryTime)
}
\]

也就是：

> **证据在用户所问的那个时间点是否有效。**

这叫：

# Temporal Retrieval
## 时间有效性检索

它会在后面 Metadata Filter 阶段变得非常重要。

---

## 五、Jurisdiction：正确法规放错地区，一样是错误证据

政府采购知识还天然带有：

# Jurisdiction
## 适用辖区

例如：

```text
全国
某省
某市
某区县
特定系统
特定采购主体
```

所以文档至少应该有类似：

```text
jurisdiction_level
jurisdiction_code
jurisdiction_name
```

但这里有一个重要原则：

> **不要仅根据标题猜适用范围。**

真正的适用范围应该来自：

```text
原文件内容
发布主体
正式元数据
人工审核
```

因为：

> “某省发布”

并不自动等于：

> 文件所有条款只适用于某省所有主体。

所以 Metadata 应该记录：

> 已验证的信息，

而不是：

> 系统自己脑补的信息。

---

## 六、Authority / Document Type：来源层级必须记录，但不要让模型只按“名字大小”判断效力

知识库里可能同时存在：

```text
法律
行政法规
部门规章
规范性文件
政策解释
地方文件
采购文件
投诉处理案例
专家文章
内部审查规则
```

这些内容：

> 不能全部当成同一种证据。

所以应该记录：

```text
document_type
issuer
authority_level
official_status
```

但不要做一个危险的简化：

```text
document_type = 法律
→ 永远直接覆盖其他所有内容
```

真实规范适用可能还涉及：

```text
特别法 / 一般法
新旧规则
适用对象
适用区域
授权关系
具体条款
```

RAG 系统应该做的是：

> **保留足够元数据，让后续检索、排序和业务规则有判断材料。**

而不是：

> 在入库阶段擅自做完所有法律解释。

---

## 七、Versioning：新版不是把旧版删掉，而是建立“版本关系”

这是本阶段最重要的工程点之一。

假设：

```text
Document V1
2019版
```

后来出现：

```text
Document V2
2023修订版
```

再后来：

```text
Document V3
2026修订版
```

一个成熟知识库更应该保存：

```text
V1
│
└── superseded_by → V2
                       │
                       └── superseded_by → V3
```

并记录：

```text
version_id
effective_from
effective_to
status
supersedes
superseded_by
```

而不是：

```text
V1
删除

V2
删除

只剩V3
```

为什么？

因为用户可能问：

> “2021 年某项目当时依据什么规则？”

这时：

\[
LatestVersion
\]

不一定等于：

\[
CorrectVersionForQuestion
\]

所以：

\[
\boxed{
Latest
\neq
HistoricallyApplicable
}
\]

---

## 八、知识状态不要只设计成 `valid=true/false`

真实世界没有那么干净。

有些文档我们可能确认：

```text
current
```

有些明确：

```text
repealed
```

有些可能：

```text
superseded
```

还有些来源状态不清楚：

```text
unknown
```

所以工程上更稳妥的是使用状态机，而不是一个布尔值。

例如概念上：

```text
current
superseded
repealed
expired
draft
unknown
```

特别重要的是：

> **Unknown 不是 False。**

如果系统无法确认一份文件当前是否有效，

正确做法应该是：

```text
validity_status = unknown
```

而不是系统偷偷猜：

```text
valid = true
```

这和第五课里的 `needs_review` 是同一种思想：

> **不知道，就是不知道。**

---

## 九、Document 不等于未来的 Retrieval Unit

现在我们有一份 80 页法规。

它在 Knowledge Base 中是一个：

# Document

但后面真正检索时，

我们不太可能每次把 80 页全部塞给模型。

后面第 3 阶段会把它拆成：

# Chunk

也就是检索单元。

所以现在就要把层级设计清楚：

```text
Source
  ↓
Document
  ↓
Section / Article / Paragraph
  ↓
Chunk
```

例如：

```text
document_id = DOC_001

第十二条
article_id = DOC_001_A12

Chunk 1
chunk_id = DOC_001_A12_C01
```

于是一个 Chunk 后面即使被单独检索出来，

仍然能够一路追溯：

\[
Chunk
\rightarrow
Article
\rightarrow
Document
\rightarrow
Source
\]

这就是：

# Traceability Chain
## 可追溯链

---

## 十、Metadata 不是“附加信息”，而是未来检索系统的一部分

很多人会认为：

> Embedding 才是真正的检索技术。

Metadata 只是：

> 顺手存一下。

这是错的。

以后用户问：

> “按照 2025 年以后广东省现行的政府采购规定……”

我们完全可以先做：

```text
jurisdiction = 广东省
effective_time <= query_time
validity_status = current
```

再在剩下的知识里做语义检索。

这比：

> 让 Embedding 在全国所有年代所有版本中瞎找

可靠得多。

因此未来 Retriever 实际上可能是：

\[
\boxed{
MetadataFilter
+
LexicalRetrieval
+
DenseRetrieval
+
Reranking
}
\]

所以今天设计 Metadata：

> 实际是在给后面的 Retrieval 打地基。

---

## 十一、去重不能只看“文件名一样不一样”

知识库很容易出现：

```text
官方网站 HTML
官方 PDF
转载网页
本地下载 PDF
OCR 文本
```

内容可能：

> 实际上是同一份文件。

如果全部当成独立知识：

```text
Retriever Top-5
```

可能返回：

```text
同一法规
同一法规
同一法规
同一法规
另一个法规
```

这叫：

# Retrieval Diversity Collapse
## 检索多样性塌缩

第一版去重至少要考虑两类。

精确重复：

\[
Hash(A)=Hash(B)
\]

可以直接识别。

近重复：

> 文本略有排版差异、页眉页脚差异、HTML/PDF 转换差异。

则需要：

```text
Normalized Text
+
Near-Duplicate Detection
```

但要特别小心：

> **两个版本高度相似，不代表它们应该被去重。**

例如新版只修改了第 12 条一个词，

这一个词可能就是最关键的法律变化。

所以：

\[
\boxed{
Deduplication
\neq
VersionDeletion
}
\]

---

## 十二、最终的入库流水线应该是什么？

现在把这一阶段压成一条真正可执行的链：

```text
Raw Source
    │
    ▼
Source Verification
确认来源
    │
    ▼
Acquire Original
保存原文件
    │
    ▼
Hash / Identity
建立唯一身份
    │
    ▼
Parse
提取正文和结构
    │
    ▼
Metadata Extraction
标题 / 文号 / 发布机关 / 日期 / 辖区
    │
    ▼
Validity & Version Review
有效性 / 版本关系
    │
    ▼
Deduplication
精确重复 / 近重复
    │
    ▼
Structure Preservation
章 / 节 / 条 / 款 / 页
    │
    ▼
Knowledge Document
    │
    ▼
Ready for Chunking
```

注意最后一步只是：

# Ready for Chunking

还没有：

```text
Embedding
Vector Database
```

因为这些是后面的阶段。

这一步做好以后，我们得到的是：

> **干净、可追溯、版本明确的知识资产。**

---

## 十三、本阶段工程产物：`ProcurementKnowledgeBase_V0.1`

第一版 Document Record 可以抽象成：

```json
{
  "document_id": "DOC_000001",
  "title": "某政府采购规范性文件",
  "document_number": "示例文号",
  "issuer": "示例发布机关",
  "document_type": "normative_document",

  "jurisdiction": {
    "level": "province",
    "code": "example",
    "name": "示例地区"
  },

  "publication_date": "2026-01-01",
  "effective_from": "2026-03-01",
  "effective_to": null,

  "validity_status": "current",

  "version_id": "V3",
  "supersedes": "DOC_000001_V2",
  "superseded_by": null,

  "source_url": "...",
  "retrieved_at": "...",
  "source_hash": "...",

  "raw_file_path": "...",
  "parsed_text_path": "...",

  "review_status": "verified"
}
```

这里真正重要的不是 JSON 长什么样。

而是四个问题都有答案：

\[
\boxed{
Who
+
Where
+
When
+
WhichVersion
}
\]

也就是：

> **谁发布、适用哪里、什么时候有效、到底哪个版本。**

---

## 十四、把本阶段压成最精准的 5 句话

> **第一，RAG Knowledge Base 不是 PDF 文件夹，而是“正文 + Metadata + Provenance + Version + Validity”组成的可治理知识系统。**

> **第二，每一份知识都必须能够从 Chunk 追溯到 Document，再追溯到原始 Source；否则 Citation 只是表面上有链接，并不是真正可审计。**

> **第三，政府采购知识天然带时间和辖区条件，所以 `effective_from / effective_to / jurisdiction / validity_status` 必须成为一等字段。**

> **第四，新版本不能简单覆盖旧版本；真正的版本管理要保留 `supersedes / superseded_by` 等关系，因为最新版本不一定是历史问题的正确版本。**

> **第五，Metadata、去重、有效性审查和来源验证不是 Embedding 之前的杂活，它们直接决定未来 Retriever 有没有机会找到正确证据。**

---

# 本阶段最核心的一张图

```text
                         Raw Documents
                              │
                              ▼
                      Source Verification
                              │
                              ▼
                    Identity + Provenance
                              │
                              ▼
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
          Version           Time          Jurisdiction
             │                │                │
             └────────────────┼────────────────┘
                              ▼
                        Validity State
                              │
                              ▼
                         Parsed Text
                              │
                              ▼
                    Document Structure
                              │
                              ▼
                       Metadata Record
                              │
                              ▼
                ProcurementKnowledgeBase_V0.1
                              │
                              ▼
                     Ready for Chunking
```

脑中最后只留一句：

> **检索系统真正的第一步不是向量化，而是先让每一条知识都有身份证、时间线、适用范围和来源链。**

---

# 第六课 · 第 2 阶段掌握测试

现在不回看正文，你应该能够解释：为什么一个 PDF 文件夹还不能称为成熟 Knowledge Base；什么是 Provenance；为什么标题不能单独作为 Document Identity；`publication_date`、`effective_from`、`effective_to` 和 `retrieved_at` 为什么不是同一个时间；为什么 Jurisdiction 必须作为 Metadata；为什么新版不能直接覆盖旧版；为什么 `latest` 不等于 `historically applicable`；为什么 `validity_status` 不应该只有 true/false；Document、Article、Chunk 为什么要分层；为什么 Metadata Filter 会直接影响后面的 Retrieval；为什么精确重复和版本更新不能混为一谈；以及为什么今天还没有进入 Embedding，但其实已经决定了未来 RAG 的大量上限。

如果这些能够自己讲清楚：

\[
\boxed{
第六课第2阶段真正掌握
}
\]

---

# 下一阶段：第六课 · 第 3 阶段
# Chunking：长文档到底应该怎样切？

下一阶段我们终于开始碰真正的“检索单元”。

核心问题会从：

> **这份文档是谁、什么时候有效？**

转向：

> **80 页法规到底应该切成什么粒度，Retriever 才既找得准，又不会把完整法律语义切碎？**

我们会正式比较：

```text
Fixed-size Chunking
Paragraph Chunking
Article-aware Chunking
Structure-aware Chunking
Overlap
Parent-Child Retrieval
```

并建立下一件工程产物：

# `ProcurementChunkingPolicy_V0.1`

因为到了第 3 阶段，我们才真正开始把：

\[
Document
\]

变成：

\[
RetrievableKnowledgeUnit
\]

也就是后面 Embedding 和 Vector Search 真正要处理的对象。

---
