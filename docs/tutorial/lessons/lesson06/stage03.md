# 第六课 · 第 3 阶段
# Chunking：长文档到底应该怎样切？
## 80 页法规怎样变成既能被检索、又不破坏业务语义的 Knowledge Unit？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，Chunking 不是把长文本机械切短，而是在定义 Retriever 眼中的“知识最小单位”。**
2. **第二，Chunk 太大会产生语义稀释，Chunk 太小会产生语义碎片化，所以目标是兼顾检索聚焦度与语义完整性。**
3. **第三，政府采购法规和采购文件优先采用 Structure-aware Chunking：先尊重章、节、条、款、项等业务结构，再用 Token 长度做二次约束。**
4. **第四，Overlap 只能缓解局部边界断裂，不能解决远距离依赖；需要时可以用 Parent-Child Retrieval 实现“小单元检索、大上下文生成”。**
5. **第五，每个 Chunk 必须继承 Document 的版本、时间、辖区、来源和结构 Metadata，否则检索出来的只是匿名文本，无法真正 Citation 和审计。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Chunking` | 分块：把长文档切成适合检索和上下文组装的片段 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Metadata` | 元数据：项目、来源、时间、地区、版本等辅助信息 |
| `Embedding` | 嵌入：把离散 Token 映射到连续高维向量 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Tokenization` | Token 化：把文本转换成 Token 序列 |

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

第 2 阶段我们已经把一份知识文档治理成：

```text
Source
↓
Document
↓
Version
↓
Validity
↓
Jurisdiction
↓
Structure
↓
Metadata
```

现在它已经：

> 可信、可追溯、版本明确。

但 Retriever 仍然不能直接把整份 80 页法规当成一个检索单元。

原因很简单：

> 用户问的是一个具体问题，而不是“把整本法规都给我”。

所以今天要解决的是：

# Chunking
## 文档切分

也就是把：

\[
Document
\]

变成：

\[
RetrievableKnowledgeUnit
\]

本阶段最终形成：

# `ProcurementChunkingPolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

Chunking 的本质不是：

> **把长文本机械切短。**

而是：

> **决定“检索系统把什么当成一条知识”。**

这两句话差别非常大。

如果把一份法规切成：

```text
每500字符一段
```

技术上它已经被切开。

但如果恰好把：

```text
前提条件
```

留在 Chunk A，

把：

```text
例外条件
```

切到 Chunk B，

那么 Retriever 即使准确找到 Chunk A，

也可能只拿到：

> **一半事实。**

因此：

\[
\boxed{
GoodChunk
=
可检索
+
语义完整
+
可追溯
+
大小受控
}
\]

---

# 二、Chunking 和 Tokenization 完全不是一回事

这一点前面已经预告过，现在正式锁死。

## Tokenization

把字符串变成模型输入单位：

```text
"供应商资格条件"
↓
Token 1
Token 2
Token 3
...
```

它解决：

> 模型怎样读取文本。

---

## Chunking

把长文档拆成检索单元：

```text
80页法规
↓
总则
↓
资格条件
↓
评审规则
↓
投诉处理
...
```

它解决：

> Retriever 搜索什么单位。

所以：

\[
\boxed{
Token
\neq
Chunk
}
\]

一个 Chunk：

> 通常内部还会包含很多 Token。

---

# 三、为什么“整篇文档一个 Chunk”通常不好？

假设一份 30,000 Token 的采购办法整体做一个 Chunk。

用户问：

> “资格条件能不能要求供应商投标前在本地设机构？”

Embedding 看到的却是：

```text
总则
资格条件
采购程序
开标
评审
合同
履约
投诉
监督
附则
```

一个巨大向量要同时代表：

> 这么多不同主题。

于是具体的“本地机构限制”信号很容易被其它内容稀释。

这叫一个非常实用的直觉：

# Semantic Dilution
## 语义稀释

Chunk 太大：

> 包含的信息太多，检索主题不够聚焦。

所以：

\[
\boxed{
TooLargeChunk
\rightarrow
RetrievalSpecificity\downarrow
}
\]

但这只是问题的一半。

---

# 四、为什么 Chunk 也不能越小越好？

假设把文本切成：

```text
“不得”
```

一条 Chunk。

下一条：

```text
“以不合理的条件”
```

再下一条：

```text
“对供应商实行差别待遇”
```

每条都很短，

但没有一条能够独立表达完整规则。

这时会发生：

# Semantic Fragmentation
## 语义碎片化

Chunk 太小：

> 检索得到的是词语碎片，而不是可解释证据。

因此：

\[
\boxed{
TooSmallChunk
\rightarrow
SemanticCompleteness\downarrow
}
\]

所以 Chunking 永远是在找一个平衡：

\[
\boxed{
RetrievalPrecision
\quad vs \quad
SemanticCompleteness
}
\]

---

# 五、Fixed-size Chunking：最简单，但只能当 Baseline

最常见做法：

```text
每 512 Tokens 切一块
```

或者：

```text
每 1000 字符切一块
```

优点很明显：

```text
实现简单
速度快
长度稳定
容易批处理
```

所以它非常适合作为：

# Baseline

但问题也明显：

> 它不知道哪里是“第十二条”的边界。

可能切成：

```text
Chunk A
第十二条前半段

Chunk B
第十二条后半段 + 第十三条开头
```

这在法律、采购规则、合同文本里经常是危险的。

因此：

\[
\boxed{
FixedSize
=
工程简单
\neq
业务语义最佳
}
\]

---

# 六、Paragraph / Article-aware Chunking：开始尊重文档结构

政府采购法规天然有结构。

例如：

```text
第一章 总则

第一条 ...
第二条 ...

第二章 采购需求

第十条 ...
第十一条 ...
```

因此更合理的做法是：

> 优先沿着业务结构切。

例如：

```text
一条法规条文
=
一个候选 Chunk
```

如果某一条很短，

可以把相邻且同主题的条款组合。

如果某一条特别长，

再在条内按：

```text
款
项
段落
列表
```

继续切。

这叫：

# Structure-aware Chunking
## 结构感知切分

对于政府采购文本，它通常比纯 Fixed-size 更符合业务语义。

---

# 七、我们真正要保护的不是“段落”，而是最小充分语义

这一点非常关键。

某个自然段不一定就是一个好 Chunk。

例如：

```text
供应商应当具备相应履约能力。
具体要求见附件三。
```

如果只保留这一段，

用户问：

> “具体要求是什么？”

这个 Chunk 本身无法回答。

所以我们更应该问：

> **这段文字独立检索出来以后，是否拥有回答相关问题所需的最小充分语义？**

这可以叫：

# Minimal Sufficient Retrieval Unit
## 最小充分检索单元

它和第三课、第五课里讲过的：

> Minimal Sufficient Context

其实是同一个工程哲学：

> **不要多到淹没主题，也不要少到失去关键条件。**

---

# 八、Overlap：它解决边界断裂，但不是万能药

Fixed-size Chunking 常见：

```text
chunk_size = 512
overlap = 64
```

意思是：

```text
Chunk 1
Token 1 ... 512

Chunk 2
Token 449 ... 960
```

中间重复一部分。

Overlap 的价值是：

> 降低关键信息恰好被切在边界两侧的风险。

例如：

```text
前一个 Chunk
“供应商不得在投标前...”

后一个 Chunk
“被要求在采购人所在地设立分支机构。”
```

有了 Overlap，

两边可能都保留足够上下文。

但是：

\[
\boxed{
Overlap
\neq
SemanticUnderstanding
}
\]

它不能解决：

```text
第5条定义
和
第42条例外
相隔30页
```

这样的远距离依赖。

Overlap 只是：

> **局部边界保险。**

---

# 九、Chunk Size 到底应该是多少？

没有一个所有项目都正确的：

```text
512 Tokens
```

或：

```text
1024 Tokens
```

Chunk Size 应该同时受四类因素约束：

| 因素 | 对 Chunk Size 的影响 |
|---|---|
| 文档语义结构 | 一条规则能否完整表达 |
| Embedding Model 上限 | 单个 Chunk 能编码多少 Token |
| Retriever 特性 | 太大是否导致语义稀释 |
| 最终 LLM Context Budget | Top-K 证据能否一起放进 Prompt |

所以：

\[
\boxed{
ChunkSize
不是孤立超参数
}
\]

它实际上会影响后面的：

```text
Embedding
Top-K
Reranking
Context Assembly
Latency
Cost
```

---

# 十、检索 Chunk 和最终给 LLM 的 Context，不一定必须是同一个粒度

这是一个很重要的进阶心智模型。

我们可以：

> 用小 Chunk 检索，

但最终：

> 给 LLM 更大的父级上下文。

例如：

```text
Parent:
第十二条完整条文

Child 1:
第十二条第一款

Child 2:
第十二条第二款

Child 3:
第十二条第三款
```

检索时：

```text
Query
↓
命中 Child 2
```

然后生成阶段拿回：

```text
Parent Article
第十二条完整内容
```

这就是：

# Parent-Child Retrieval
## 父子检索

它试图同时得到：

\[
\boxed{
SmallUnitRetrievalPrecision
+
LargeUnitContextCompleteness
}
\]

这在法规和采购文件里非常有价值。

---

# 十一、Chunk 必须继承 Metadata，而不能变成“失忆文本块”

假设第 2 阶段 Document 有：

```text
document_id
title
issuer
jurisdiction
effective_from
effective_to
version_id
validity_status
source_url
```

切成 Chunk 后，

不能只留下：

```json
{
  "text": "供应商不得..."
}
```

否则未来 Retriever 返回它时，

我们不知道：

> 它来自哪里、什么时候有效、适用于哪里。

所以 Chunk Record 至少应该继承或引用：

```text
chunk_id
document_id
parent_section_id
article_number
page_number
title_path

jurisdiction
effective_from
effective_to
validity_status
version_id

source_id
source_url
```

这保证：

\[
Chunk
\rightarrow
Document
\rightarrow
Source
\]

始终可追溯。

---

# 十二、对政府采购文本，第一版 Chunking Policy 应该怎么设计？

我们的第一版不追求花哨。

建议采用：

# Structure First, Size Second
## 先结构，后长度

流程：

```text
Document
↓
识别章 / 节 / 条 / 款 / 项
↓
优先按完整业务条款形成候选单元
↓
过短
→ 与同主题相邻内容合并

过长
→ 在条款内部按款 / 项 / 段落继续切

跨边界风险
→ 适量 Overlap

生成 Parent / Child 关系
↓
写入 Metadata
```

也就是说：

> **先问“法律语义在哪里结束”，再问“Token 长度是多少”。**

而不是反过来。

---

# 十三、怎样判断 Chunking 好不好？不要只看平均长度

一个 Chunking Policy 的质量至少要从四个方向评估。

### 1. Retrieval Recall

正确证据有没有机会被搜到？

---

### 2. Semantic Completeness

检索到的 Chunk 是否包含：

```text
条件
结论
例外
适用对象
```

这些关键内容？

---

### 3. Redundancy

Overlap / 重复是不是太多，

导致 Top-K 全是相似 Chunk？

---

### 4. Context Efficiency

最终放进 LLM 的证据是不是：

> 大量 Token 都是无关背景？

所以不能只说：

```text
平均 Chunk 长度 = 512
```

然后宣布策略合理。

我们最终要用后面的 Retrieval Benchmark 来判断。

---

# 十四、本阶段工程产物：`ProcurementChunkingPolicy_V0.1`

第一版可以记录：

```text
strategy
=
structure_aware

primary_boundary
=
chapter / section / article / paragraph

target_token_range
=
实验配置

max_tokens
=
Embedding / Retrieval约束

min_tokens
=
避免过碎

overlap_tokens
=
仅用于必要的局部边界保护

parent_child_enabled
=
true / false

metadata_inheritance
=
enabled

preserve_article_number
=
true

preserve_title_path
=
true

preserve_page_reference
=
true

dedup_after_chunking
=
enabled

chunk_policy_version
=
V0.1
```

同时每个 Chunk 至少要有：

```json
{
  "chunk_id": "DOC_001_A12_C02",
  "document_id": "DOC_001",
  "parent_id": "DOC_001_A12",
  "title_path": ["第二章", "供应商资格", "第十二条"],
  "article_number": "第十二条",
  "text": "...",
  "token_count": 386,
  "page_start": 17,
  "page_end": 18,
  "version_id": "V3",
  "validity_status": "current",
  "source_id": "SRC_001"
}
```

真正重要的不是字段名本身，

而是：

> **每个 Chunk 都既是一个检索单元，又仍然知道自己是谁、来自哪里、属于什么结构。**

---

# 十五、把本阶段压成最精准的 5 句话

> **第一，Chunking 不是把长文本机械切短，而是在定义 Retriever 眼中的“知识最小单位”。**

> **第二，Chunk 太大会产生语义稀释，Chunk 太小会产生语义碎片化，所以目标是兼顾检索聚焦度与语义完整性。**

> **第三，政府采购法规和采购文件优先采用 Structure-aware Chunking：先尊重章、节、条、款、项等业务结构，再用 Token 长度做二次约束。**

> **第四，Overlap 只能缓解局部边界断裂，不能解决远距离依赖；需要时可以用 Parent-Child Retrieval 实现“小单元检索、大上下文生成”。**

> **第五，每个 Chunk 必须继承 Document 的版本、时间、辖区、来源和结构 Metadata，否则检索出来的只是匿名文本，无法真正 Citation 和审计。**

---

# 本阶段最核心的一张图

```text
                         Document
                            │
                            ▼
                    Structure Parser
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
           Chapter         Article       Paragraph
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                    Semantic Boundary
                            │
                            ▼
                     Size Constraint
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
          Too Small       Good Size       Too Large
             │              │              │
           Merge            Keep          Split
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                         Chunk
                            │
                    + Metadata
                    + Parent Link
                    + Source Link
                            │
                            ▼
              RetrievableKnowledgeUnit
```

脑中最后只留一句：

> **先按语义结构切，再用长度约束修正；检索单位可以小，但最终给模型的证据不一定必须同样小。**

---

# 第六课 · 第 3 阶段掌握测试

现在不回看正文，你应该能够解释：为什么 Chunking 不等于 Tokenization；为什么整篇文档做一个 Chunk 会产生 Semantic Dilution；为什么 Chunk 越小并不一定越好；Fixed-size Chunking 的价值和局限分别是什么；为什么政府采购文本更适合 Structure-aware Chunking；什么是 Minimal Sufficient Retrieval Unit；Overlap 真正解决什么问题、又解决不了什么；为什么 Chunk Size 会影响 Embedding、Top-K 和最终 Context Budget；什么是 Parent-Child Retrieval；为什么 Chunk 必须继承版本、时间、辖区和来源 Metadata；为什么“先结构、后长度”适合作为 ProcurementRAG 第一版策略；以及为什么评估 Chunking 不能只看平均长度，而要看 Retrieval Recall、Semantic Completeness、Redundancy 和 Context Efficiency。

如果这些能够完整讲出来：

\[
\boxed{
第六课第3阶段真正掌握
}
\]

---

# 下一阶段：第六课 · 第 4 阶段
# Embedding：文本为什么可以变成“语义向量”？

到第 3 阶段，我们终于有了真正可检索的：

\[
Chunk
\]

下一阶段才正式进入：

\[
Chunk
\rightarrow
EmbeddingVector
\]

并回答几个核心问题：

> **为什么“本地机构限制”和“要求供应商预先设立本地分支机构”文字不同，却可能在向量空间里靠得很近？**

> **Query 和 Document Chunk 为什么可以用同一个向量空间比较？**

> **Cosine Similarity 到底在比较什么？**

下一阶段我们会第一次真正把：

# Semantic Retrieval

背后的数学直觉建立起来。

---
