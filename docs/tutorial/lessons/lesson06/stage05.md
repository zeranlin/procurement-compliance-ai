# 第六课 · 第 5 阶段
# Vector Index / Vector Database：向量到底怎样被快速找到？
## 从“逐个比相似度”到真正可扩展的 Top-K 检索系统

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：MEDIUM。** 审计原因：核心心智模型出现偏后，阅读前段缺少认知锚点；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，Exact Search 是把 Query 和全部向量逐个比较；ANN 则通过索引结构减少搜索范围，用少量近似误差换更低延迟和更高吞吐。**
2. **第二，Vector Index 是近邻搜索的数据结构，Vector Database 则还负责向量、Metadata、过滤、增删改、持久化和生命周期管理，两者不是同一个概念。**
3. **第三，HNSW 的核心直觉是“图导航”，IVF 的核心直觉是“先定位候选区域再局部搜索”；两者都在用搜索范围控制 Recall / Latency Trade-off。**
4. **第四，Metadata Filter、Similarity Metric、Normalization、Top-K 和 ANN 参数都会直接影响最终检索结果，不能把它们当成与 Embedding 无关的数据库配置。**
5. **第五，Vector Index 的目标不是单独追求最快，而是在可接受的内存和延迟下，保持足够高的 Index Recall 和真正业务上的 Retrieval Recall。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Vector Database` | 向量数据库：存储向量并支持相似度检索 |
| `Recall` | 召回率：真实风险中被系统成功找出的比例 |
| `ANN` | ANN/近似最近邻：在大规模向量中快速寻找相似项 |
| `Embedding` | 嵌入：把离散 Token 映射到连续高维向量 |
| `Query` | Query/Q：当前 Token 表示“我要找什么”的向量 |
| `Metadata` | 元数据：项目、来源、时间、地区、版本等辅助信息 |
| `Latency` | 延迟：单个请求从进入到完成的时间 |
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

第 4 阶段，我们已经把每个 Chunk 变成了：

\[
\mathbf{d_i}
\in
\mathbb{R}^{d}
\]

用户问题也能变成：

\[
\mathbf{q}
\in
\mathbb{R}^{d}
\]

理论上，只要计算：

\[
sim(\mathbf{q},\mathbf{d_i})
\]

然后把所有 Chunk 排序，就能找到 Top-K。

如果只有：

```text
1,000 个向量
```

这样做完全可以。

但如果知识库有：

```text
1,000万 个向量
```

每一次 Query 都和全部向量逐个比较，

成本就会迅速变大。

所以今天真正解决的是：

> **怎样让“找最近向量”从数学公式变成一个可扩展的工程系统。**

本阶段最终形成：

# `ProcurementVectorIndexPolicy_V0.1`

---

# 一、先锁死 4 个概念：Vector、Index、Search、Database

这四个词经常被混在一起。

## Vector

就是 Embedding：

\[
\mathbf{e}
=
[0.13,-0.72,\ldots]
\]

它只是：

> 一条数值表示。

---

## Vector Search

给定 Query Vector：

\[
\mathbf{q}
\]

寻找最相近的：

\[
\mathbf{d_i}
\]

例如：

\[
TopK
=
\operatorname{arg\,topk}_i
sim(\mathbf{q},\mathbf{d_i})
\]

这是：

> 搜索任务。

---

## Vector Index

为了让这个搜索更快，

提前建立的数据结构。

它解决：

> **怎样少看一些候选，就尽快找到最可能的近邻。**

---

## Vector Database

它通常不只是 Index。

还会负责：

```text
向量存储
Metadata
增删改
持久化
查询接口
过滤
索引管理
权限 / 多租户
备份恢复
```

所以：

\[
\boxed{
VectorDatabase
\neq
VectorIndex
}
\]

更准确地说：

> **Index 是搜索加速结构，Database 是围绕向量检索构建的完整数据管理系统。**

---

# 二、最朴素的方法：Exact Search

假设知识库有：

\[
N
\]

个向量。

Query 来了以后：

```text
Query Vector
↓
和 d1 比
和 d2 比
和 d3 比
...
和 dN 比
↓
完整排序 / Top-K
```

这就是：

# Exact Nearest Neighbor Search
## 精确近邻搜索

如果每个向量维度是：

\[
d
\]

那么一次完整比较的粗略计算规模接近：

\[
O(Nd)
\]

也就是说：

> 数据量越大，逐个扫描越贵。

但 Exact Search 有一个很重要的优点：

> **如果实现和度量正确，它不会因为近似索引本身而漏掉真正的最近邻。**

所以小规模数据集里：

> 暴力搜索并不“低级”。

它经常是非常好的 Baseline。

---

# 三、为什么要 ANN？

当：

\[
N
\]

越来越大，

系统常常愿意接受一个交换：

\[
\boxed{
少量Recall损失
\quad
换取
\quad
更低Latency / 更高吞吐
}
\]

这就是：

# ANN
## Approximate Nearest Neighbor
## 近似最近邻

关键词是：

# Approximate
## 近似

ANN 不保证每一次都找出数学上绝对最近的 K 个向量。

它的目标是：

> **以明显更低的搜索成本，找到足够接近真正 Top-K 的候选。**

所以 ANN 的核心不是“更准”。

而是：

\[
\boxed{
Recall
\leftrightarrow
Latency
}
\]

的工程权衡。

---

# 四、ANN 的 Recall 到底是什么？

假设 Exact Search 的真实 Top-5 是：

```text
A
B
C
D
E
```

ANN 找到：

```text
A
B
C
F
G
```

那么如果按集合重合计算：

\[
Recall@5
=
\frac{3}{5}
=
0.6
\]

这里的 Recall 不是：

> 政府采购“风险召回率”。

而是：

# Index Recall
## 索引近邻召回率

意思是：

> **ANN 找回了多少真正的最近邻。**

所以后面我们会同时遇到两类 Recall：

```text
Index Recall
ANN有没有找回真实近邻

Retrieval Recall
正确业务证据有没有进入Top-K
```

这两个不要混。

---

# 五、HNSW：把向量组织成“可导航图”

一个非常常见的 ANN 思路是：

# HNSW
## Hierarchical Navigable Small World

不需要死记完整算法细节。

先建立正确心智模型。

它不是：

> 给所有向量做一个简单排序。

而是把向量连接成一个：

# Graph
## 图结构

概念上：

```text
A ─── B ─── C
│     │     │
D ─── E ─── F
      │
      G
```

相近的向量之间建立邻接关系。

查询时：

> 不从第一个向量扫到最后一个向量。

而是：

```text
从某个入口开始
↓
沿着“更接近Query”的邻居移动
↓
逐渐进入更接近的局部区域
↓
找到候选近邻
```

所以可以把 HNSW 理解成：

> **在高维向量空间里建立一张“导航地图”。**

---

# 六、为什么 HNSW 叫 Hierarchical？

因为它不是只有一层图。

更接近：

```text
高层
少量节点
负责快速跨区域跳跃

中层
更多节点
进一步定位

底层
大量节点
做局部精细搜索
```

很像：

```text
高速公路
↓
城市主干道
↓
社区道路
```

查询时先在高层快速接近目标区域，

然后逐层下沉。

这就是：

# Hierarchical
## 分层

的直觉。

---

# 七、HNSW 的核心权衡是什么？

HNSW 常见会有几类控制因素：

```text
图连接密度
建索引时搜索宽度
查询时搜索宽度
```

这些参数名字在具体实现里可能不同，

但长期正确的因果关系是：

> 搜得更宽，通常 Recall 更高，但查询更慢。

也就是说：

\[
\boxed{
SearchBreadth
\uparrow
\Rightarrow
Recall
\uparrow
\quad
Latency
\uparrow
}
\]

同时，更密的图通常还意味着：

> 更高内存占用。

所以 HNSW 不是：

> “打开以后自动又快又准。”

它仍然要在：

```text
Recall
Latency
Memory
Build Cost
```

之间做权衡。

---

# 八、IVF：先找“区域”，再在区域里搜

另一类经典思路：

# IVF
## Inverted File Index

可以先用一个直觉理解。

假设有 1,000 万个向量。

我们先把向量空间划成很多区域：

```text
Cluster 1
Cluster 2
Cluster 3
...
Cluster 1000
```

每个区域有一个代表中心：

# Centroid
## 聚类中心

Query 来以后，

先问：

> Query 最接近哪些 Cluster？

然后只在这些 Cluster 里找。

所以：

```text
Query
↓
找最近的Centroid
↓
选择若干候选Cluster
↓
只扫描这些Cluster
↓
Top-K
```

而不是扫描全部向量。

---

# 九、IVF 的核心旋钮：Probe 多少个区域？

如果只检查：

```text
1 个Cluster
```

速度很快，

但正确近邻如果刚好落在相邻 Cluster：

> 可能漏掉。

如果检查：

```text
20 个Cluster
```

Recall 往往更高，

但计算也更多。

所以又回到：

\[
\boxed{
更多候选区域
\Rightarrow
Recall\uparrow
Latency\uparrow
}
\]

这和 HNSW 虽然算法不同，

但工程本质非常相似：

> **用搜索范围换 Recall。**

---

# 十、HNSW 和 IVF 不要问“谁绝对更好”

这是一个经常出现的错误问题。

真正应该问：

```text
数据规模多大？
维度多高？
内存多少？
更新频率多高？
查询延迟要求是多少？
Metadata Filter多不多？
目标Recall是多少？
```

HNSW 往往在：

> 高 Recall、低延迟的内存型近邻搜索

上很有吸引力。

IVF 一类方法则常用于：

> 通过聚类缩小候选范围，并进一步和压缩技术组合。

但这不是绝对规则。

真正选择必须：

> **在自己的数据和硬件上 Benchmark。**

---

# 十一、Product Quantization：为什么有时还要压缩向量？

如果：

```text
10,000,000 vectors
×
1536 dimensions
×
4 bytes
```

仅原始 FP32 向量理论上就需要：

\[
10^7
\times
1536
\times
4
\]

bytes。

也就是几十 GB 级别。

所以大规模系统可能进一步使用：

# Quantization
## 向量压缩

例如：

# Product Quantization
## PQ

它的核心思路不是今天要求掌握完整算法，

只需要知道：

> **把原始高精度向量压缩成更紧凑的表示，以减少存储和搜索成本。**

代价通常是：

> 又引入一层近似误差。

所以：

\[
\boxed{
Compression
\uparrow
\Rightarrow
Memory
\downarrow
\quad
可能
Recall
\downarrow
}
\]

这和 QLoRA 里的量化思想很像：

> 都是用近似表示换资源效率，

但对象完全不同。

QLoRA 压的是：

> 模型权重。

PQ 压的是：

> 检索向量。

---

# 十二、Metadata Filter 和 Vector Search 必须一起设计

第 2 阶段我们保存了：

```text
jurisdiction
effective_from
effective_to
validity_status
document_type
version_id
```

现在这些字段终于进入查询路径。

假设用户问：

> “2026 年广东省现行政府采购规则里，是否可以要求投标前设立本地机构？”

真正搜索不应该只是：

```text
vector similarity
```

更合理的是先加入条件：

```text
jurisdiction = 广东省

effective_from <= query_time

effective_to is null
or
effective_to >= query_time

validity_status = current
```

然后再做 Vector Search。

这叫：

# Filtered Vector Search
## 带过滤条件的向量检索

这里要特别注意：

> 不同 Vector Index / Database 对 Filter 的实现方式差别很大。

有的：

```text
先Filter
再ANN
```

有的：

```text
ANN过程中结合Filter
```

有的可能：

```text
先ANN
再Post-filter
```

这三种方式在 Recall 和性能上可能完全不同。

所以：

\[
\boxed{
MetadataFilter
不是查询语句里的装饰
}
\]

它会直接影响：

> 搜索空间和检索质量。

---

# 十三、Similarity Metric 必须和 Embedding Policy 对齐

第 4 阶段我们已经锁死：

```text
Cosine
Dot Product
L2
Normalization
```

到了建 Index 时，

不能随便换。

例如 Embedding Policy 规定：

```text
normalize_embeddings = true

similarity_metric = cosine
```

Index 却配置成一个完全不同的距离逻辑，

就可能改变排序。

因此必须保证：

\[
\boxed{
EmbeddingMetric
\leftrightarrow
IndexMetric
}
\]

一致或数学上可证明等价。

这是非常典型的：

> “代码能跑，但检索逻辑已经错了。”

---

# 十四、Top-K 不是越大越好

假设：

```text
Top-K = 5
```

只取最相近 5 条。

改成：

```text
Top-K = 50
```

确实可能提高：

> 正确证据被包含的概率。

但同时会带来：

```text
更多无关Chunk
更多重复
Reranker成本更高
Context更拥挤
LLM输入Token更多
```

所以：

\[
\boxed{
LargerK
\neq
BetterRAG
}
\]

更合理的系统往往是：

```text
Retriever
先召回较多候选

↓
Reranker
重新排序

↓
Context Builder
只选择少量真正证据
```

这会在第 8 阶段正式展开。

---

# 十五、Vector Database 真正应该负责什么？

现在可以把 Vector Database 的职责压清楚了。

一个成熟系统通常需要同时管理：

```text
Vector
Chunk ID
Document ID
Metadata
Index
Insert
Update
Delete
Filter
Top-K Search
Persistence
Version
Monitoring
```

所以它不是：

> “一个会存数组的数据库”。

它真正的工程价值是：

\[
\boxed{
Storage
+
Indexing
+
Query
+
Filtering
+
LifecycleManagement
}
\]

对于我们的政府采购系统，

还尤其需要关心：

```text
版本更新
旧法规下线
新Chunk增量入库
Metadata修改
重建Index
Embedding版本隔离
```

因为知识库是会持续变化的。

---

# 十六、本阶段工程产物：`ProcurementVectorIndexPolicy_V0.1`

第一版至少记录：

```text
vector_store_type

index_type
=
exact / hnsw / ivf / ...

distance_metric

embedding_model_id
embedding_model_revision
embedding_dimension
normalize_embeddings

top_k

ann_search_parameters

metadata_filter_policy

index_build_parameters

incremental_update_supported

delete_policy

reindex_policy

embedding_version

chunk_policy_version

index_version

benchmark_dataset_version
```

并且 Benchmark 至少记录：

```text
index_recall_at_k
retrieval_recall_at_k

p50_latency
p95_latency

memory_usage
index_size

build_time
update_time
```

这里最重要的是：

> **不要只测“快不快”。**

还要测：

> **快了以后，正确证据有没有被漏掉。**

---

# 十七、把本阶段压成最精准的 5 句话

> **第一，Exact Search 是把 Query 和全部向量逐个比较；ANN 则通过索引结构减少搜索范围，用少量近似误差换更低延迟和更高吞吐。**

> **第二，Vector Index 是近邻搜索的数据结构，Vector Database 则还负责向量、Metadata、过滤、增删改、持久化和生命周期管理，两者不是同一个概念。**

> **第三，HNSW 的核心直觉是“图导航”，IVF 的核心直觉是“先定位候选区域再局部搜索”；两者都在用搜索范围控制 Recall / Latency Trade-off。**

> **第四，Metadata Filter、Similarity Metric、Normalization、Top-K 和 ANN 参数都会直接影响最终检索结果，不能把它们当成与 Embedding 无关的数据库配置。**

> **第五，Vector Index 的目标不是单独追求最快，而是在可接受的内存和延迟下，保持足够高的 Index Recall 和真正业务上的 Retrieval Recall。**

---

# 本阶段最核心的一张图

```text
                         Query
                           │
                           ▼
                    Query Embedding
                           │
                           ▼
                 Metadata Filter
                           │
                           ▼
                     Vector Index
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
         Exact Scan       HNSW          IVF
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                    Candidate Top-K
                           │
                           ▼
                      Reranker
                           │
                           ▼
                    Final Evidence
```

脑中最后只留一句：

> **Embedding 把文本变成向量，Vector Index 让近邻搜索变快，Vector Database 则让这套向量检索真正能被持续运行和管理。**

---

# 第六课 · 第 5 阶段掌握测试

现在不回看正文，你应该能够解释：Vector、Vector Search、Vector Index 和 Vector Database 的区别；Exact Search 为什么是可靠 Baseline；ANN 为什么要接受近似；Index Recall 和业务 Retrieval Recall 为什么不是同一个 Recall；HNSW 为什么可以理解成高维空间导航图；HNSW 的搜索宽度为什么会同时影响 Recall 和 Latency；IVF 为什么先找 Cluster 再局部搜索；为什么 Probe 更多区域往往 Recall 更高但更慢；为什么不能简单说 HNSW 永远优于 IVF；Product Quantization 在压缩什么；为什么 Metadata Filter 会改变 ANN 的实际效果；为什么 Similarity Metric 必须和 Embedding Policy 对齐；为什么 Top-K 不是越大越好；以及为什么真正应该 Benchmark 的是 Recall、Latency、Memory、Index Size 和 Build / Update Cost 的组合。

如果这些能够完整讲出来：

\[
\boxed{
第六课第5阶段真正掌握
}
\]

---

# 下一阶段：第六课 · 第 6 阶段
# Retrieval：Top-K 找到了，真的代表找对了吗？

到第 5 阶段，我们已经解决：

\[
\boxed{
怎样快速找到“向量上最接近”的候选
}
\]

下一阶段开始解决更重要的问题：

> **向量上接近，等不等于业务上找对证据？**

我们会正式建立：

```text
Gold Evidence
Hit@K
Recall@K
MRR
Rank Position
No-answer Query
Retrieval Failure Analysis
```

并把 RAG 评测第一次真正拆成：

\[
RetrievalEvaluation
\]

和：

\[
GenerationEvaluation
\]

两条独立链路。

因为如果正确证据根本没有进入 Top-K，

后面的 LLM 再强：

> 也没有机会基于正确证据回答。

---
