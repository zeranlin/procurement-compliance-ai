# 第六课 · 第 7 阶段
# BM25 + Dense Retrieval：为什么只靠向量检索不够？
## 当“字面精确匹配”和“语义相似匹配”各有盲区时，怎样把两种 Retriever 接成一个更可靠的 Hybrid Retrieval？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，BM25 属于 Sparse Retrieval，依赖词项匹配、IDF、词频饱和和长度归一化；它尤其擅长文号、金额、条款号、标准号和专有名词等精确信号。**
2. **第二，Dense Retrieval 擅长同义改写和语义泛化，但可能淡化数字、编号和细粒度字面差异；因此 Sparse 与 Dense 的盲区具有明显互补性。**
3. **第三，Hybrid Retrieval 的稳妥第一版是 BM25 与 Dense 并行召回，各自得到候选，再做去重、融合和后续排序，而不是让其中一条路径先把另一条路径的候选空间砍掉。**
4. **第四，BM25 Score 和 Dense Similarity 通常不能直接裸相加；Score Fusion 需要归一化 / 校准，而 RRF 可以直接利用排名进行相对稳健的融合。**
5. **第五，Hybrid 是否值得采用，必须回到 ProcurementRetrievalBenchmark_V0.1 比较 Hit@K、Recall@K、MRR、Hard Negative、No-answer 和 Latency，不能因为“用了两种检索”就默认更强。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `BM25` | BM25：基于词频和逆文档频率的经典词法检索算法 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `Hybrid Retrieval` | 混合检索：结合词法/稀疏检索与向量语义检索 |
| `Query` | Query/Q：当前 Token 表示“我要找什么”的向量 |
| `Embedding` | 嵌入：把离散 Token 映射到连续高维向量 |
| `Token` | Token：模型实际处理的离散文本单元 |

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

第 6 阶段，我们已经有了正式的：

# `ProcurementRetrievalBenchmark_V0.1`

现在我们终于可以不靠感觉，真正比较 Retriever。

到目前为止，我们主要使用的是：

# Dense Retrieval
## 稠密向量检索

也就是：

```text
Query
↓
Embedding
↓
Query Vector
↓
Vector Index
↓
Top-K
```

它特别擅长：

> **文字不完全相同，但语义接近。**

例如用户问：

> “投标前要求供应商必须在本地设立机构是否存在风险？”

而法规写的是：

> “不得以供应商所在地或者要求预先设立本地分支机构等条件限制供应商。”

即使词面不完全一致，

Dense Retrieval 仍有机会把它们拉近。

但政府采购文档里还有另一类信息：

```text
财库〔2026〕17号
第十二条
100万元
30日
财政部
项目编号 XYZ-2026-001
ISO 9001
GB/T 19001
```

这些内容的价值，往往就在于：

> **必须精确命中。**

这时候只靠语义向量并不总是最稳。

所以今天正式进入：

# Hybrid Retrieval
## 混合检索

本阶段最终形成：

# `ProcurementHybridRetrievalPolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

Sparse Retrieval 和 Dense Retrieval 不是：

> **两个互相淘汰的时代。**

更准确地说：

\[
\boxed{
Sparse
擅长字面精确性
}
\]

\[
\boxed{
Dense
擅长语义泛化
}
\]

而 Hybrid Retrieval 的目标是：

\[
\boxed{
ExactLexicalSignal
+
SemanticSignal
}
\]

也就是：

> **让“说得一样”和“意思一样”两种证据同时有机会进入候选集。**

---

# 二、什么是 Sparse Retrieval？

Sparse Retrieval：

# 稀疏检索

最经典的思路之一，就是：

> 根据 Query 中出现的词，与文档中出现的词进行匹配。

这里的“Sparse”不是说：

> 文档内容很少。

而是说：

> 表示空间通常非常高维，但单条文本只激活其中少量词项维度。

可以把词表想象成：

```text
供应商
采购人
资格条件
本地机构
中标
合同
投诉
财政部
财库
第十二条
...
```

一条文档只会命中其中一部分。

所以它的表示是：

> **高维、但大量维度为 0。**

这和 Dense Embedding：

\[
[0.13,-0.72,0.08,\ldots]
\]

这种几乎每一维都有连续数值的向量不同。

---

# 三、BM25 到底在做什么？

BM25 是经典的 Sparse Retrieval 排序方法之一。

不要先死记公式。

它真正想回答三个问题：

```text
1. Query里的词
在这篇文档里出现了吗？

2. 出现得越多
是不是应该更加分？

3. 一篇很长的文档
仅仅因为词更多
是不是不应该天然占便宜？
```

经典 BM25 的一个常见形式可以写成：

\[
score(D,Q)
=
\sum_{t \in Q}
IDF(t)
\cdot
\frac{
f(t,D)(k_1+1)
}{
f(t,D)
+
k_1
\left(
1-b+b\frac{|D|}{avgdl}
\right)
}
\]

其中：

- \(Q\)：Query；
- \(D\)：Document / Chunk；
- \(t\)：Query 中的词项；
- \(f(t,D)\)：词项 \(t\) 在文档中的出现次数；
- \(|D|\)：当前文档长度；
- \(avgdl\)：语料平均文档长度；
- \(k_1\)：控制 Term Frequency 饱和程度；
- \(b\)：控制文档长度归一化强度；
- \(IDF(t)\)：衡量词项在整个语料中有多“稀有”。

不同实现对 IDF 的具体写法可能略有差异，

但核心思想不变。

---

# 四、为什么 IDF 很重要？

假设 Query 是：

> “财库〔2026〕17号第十二条”

其中：

```text
“第”
“条”
“采购”
```

可能在很多文档里都出现。

但：

```text
财库〔2026〕17号
```

可能非常稀有。

所以 BM25 会更重视：

> **能够区分文档身份的稀有词项。**

这就是 IDF 的直觉：

\[
\boxed{
越少见的词
通常区分力越强
}
\]

因此 BM25 对下面这些特别有价值：

```text
文号
项目编号
标准编号
机构名称
专有名词
条款编号
精确金额
特定日期
```

---

# 五、为什么词频不是“出现越多分数无限上涨”？

假设 Query 有：

> “供应商”

文档 A 出现 2 次。

文档 B 出现 50 次。

如果简单按词频线性加分，

B 可能因为机械重复“供应商”就远远超过 A。

BM25 不这么做。

它引入：

# TF Saturation
## 词频饱和

直觉上：

```text
出现0次
非常重要

0 → 1次
加分很明显

1 → 2次
还有价值

20 → 21次
额外价值已经很小
```

所以：

\[
\boxed{
MoreTermFrequency
\neq
LinearMoreRelevance
}
\]

这也是 BM25 相比简单关键词计数更成熟的地方。

---

# 六、为什么还要做文档长度归一化？

假设：

```text
Chunk A
200 Tokens

Chunk B
3000 Tokens
```

Chunk B 因为更长，

天然更容易“碰巧”出现 Query 里的词。

如果完全不处理，

长文档容易获得不公平优势。

所以 BM25 用：

\[
\frac{|D|}{avgdl}
\]

参与长度归一化。

参数：

\[
b
\]

控制这种长度惩罚有多强。

因此：

\[
\boxed{
LengthNormalization
是为了减少
“长文本天然更容易命中词”
带来的偏差
}
\]

这也再次说明：

> Chunking Policy 会直接影响 BM25 的统计特性。

---

# 七、BM25 的弱点也非常明确：它不天然理解“同义表达”

假设用户问：

> “投标前必须有本地分公司合法吗？”

法规写的是：

> “不得将预先设立区域性服务机构作为参与采购活动的条件。”

两边可能没有大量完全相同的词。

BM25 可能找得不够好。

因为它主要依赖：

> **Lexical Match，字面词项匹配。**

而 Dense Retrieval 有机会理解：

```text
本地分公司
≈
区域性服务机构

投标前必须有
≈
预先设立作为参与条件
```

所以：

\[
\boxed{
BM25
不擅长跨表达方式的语义泛化
}
\]

这正是 Dense Retrieval 的优势。

---

# 八、Dense Retrieval 的弱点，恰好又是 BM25 的强项

Dense Retrieval 能处理：

> 文字不同但语义相似。

但它可能对一些极其精确的 Token 不够敏感。

例如：

```text
Query A:
财库〔2026〕17号

Query B:
财库〔2026〕71号
```

对人来说：

> 17 和 71 是完全不同的文号。

但对于某些 Embedding Model，

两句话整体语义可能仍然非常接近。

同样：

```text
100万元
vs
1000万元
```

或者：

```text
第十二条
vs
第二十二条
```

这些差异：

> 字面只差一点，

但业务含义可能完全不同。

所以：

\[
\boxed{
SemanticSimilarity
可能会淡化
ExactIdentifierDifference
}
\]

而 BM25 往往更容易保留这种字面精确性。

---

# 九、中文 BM25 的质量，很大程度取决于 Analyzer / Tokenizer

英语里单词之间天然有空格。

中文没有。

例如：

```text
供应商不得在投标截止日前设立本地机构
```

系统到底切成：

```text
供应商
不得
投标
截止日
本地
机构
```

还是：

```text
供应
商不得
投标截止
日前
本地机构
```

会直接影响 BM25。

因此中文 Sparse Retrieval 必须记录：

# Analyzer / Tokenizer Policy

包括：

```text
中文分词策略
数字处理
英文字母大小写
标点归一化
文号保留
条款号保留
同义词扩展
停用词策略
```

特别是政府采购里：

```text
财库〔2026〕17号
GB/T 19001
XYZ-2026-001
```

这些结构化标识符：

> 不应该被预处理随手拆坏。

---

# 十、Hybrid Retrieval 最稳妥的第一版：并行召回，再合并

第一版不要先追求复杂模型。

可以直接：

```text
                   Query
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
       BM25                  Dense
     Top-N_sparse          Top-N_dense
          │                     │
          └──────────┬──────────┘
                     ▼
                 Candidate Union
                     │
                     ▼
                   Dedup
                     │
                     ▼
               Fusion / Rerank
                     │
                     ▼
                  Final Top-K
```

关键点是：

> BM25 和 Dense 都先独立拥有一次“召回机会”。

然后再合并。

这比：

> 先用 Dense 把候选砍到 5 条，再在这 5 条里跑 BM25

更能保留二者互补性。

---

# 十一、为什么不能直接把 BM25 Score 和 Cosine Score 相加？

假设：

```text
BM25 Score
=
12.7

Cosine Similarity
=
0.83
```

直接：

\[
12.7+0.83
\]

没有稳定意义。

因为两个分数：

> **量纲、范围、分布都不同。**

不同 Query 下 BM25 分布也可能变化。

所以：

\[
\boxed{
RawScore_{BM25}
+
RawScore_{Dense}
}
\]

通常不是一个稳健的默认方案。

如果要做 Weighted Score Fusion：

\[
Score
=
\alpha S_{sparse}
+
(1-\alpha)S_{dense}
\]

通常需要先考虑：

```text
Score Normalization
Score Calibration
Query-level Distribution
```

否则一个 Retriever 可能仅仅因为分数范围更大而支配结果。

---

# 十二、RRF：不比原始分数，直接融合“排名”

一种很实用的方法叫：

# Reciprocal Rank Fusion
## RRF / 倒数排名融合

它不要求 BM25 Score 和 Dense Score 在同一个尺度上。

概念公式：

\[
RRF(d)
=
\sum_{r \in R}
\frac{1}{k + rank_r(d)}
\]

其中：

- \(R\)：多个 Retriever；
- \(rank_r(d)\)：文档 \(d\) 在 Retriever \(r\) 中的排名；
- \(k\)：用于减小前几名之间过大差异的常数。

注意这里的 \(k\)：

> **不是 Top-K 的那个 K。**

例如某个 Chunk：

```text
BM25 排第 1
Dense 排第 4
```

另一个 Chunk：

```text
BM25 排第 20
Dense 排第 2
```

RRF 会根据：

> 两条排名共同计算融合分数。

它最大的工程优点是：

\[
\boxed{
不需要直接比较
BM25原始分数
和
Dense原始分数
}
\]

所以很适合做第一版 Hybrid Baseline。

---

# 十三、Hybrid Retrieval 不是简单“结果取并集”

如果只是：

```text
BM25 Top-20
+
Dense Top-20
=
40条
```

然后全部送给 LLM，

这不是一个完整 Hybrid Retrieval。

我们还需要解决：

```text
重复Chunk
同一Parent下大量相邻Chunk
不同Retriever重复命中
旧版本和新版本同时出现
Hard Negative挤进前排
```

所以 Candidate Union 后至少需要：

```text
Dedup
Version / Validity Check
Metadata Constraint
Fusion
```

后面第 8 阶段还会继续加：

# Reranker

因此完整链更接近：

\[
\boxed{
SparseRecall
+
DenseRecall
\rightarrow
Fusion
\rightarrow
Rerank
}
\]

---

# 十四、Hybrid 到底有没有变好，必须由 Stage 6 Benchmark 判

我们现在已经有：

# `ProcurementRetrievalBenchmark_V0.1`

所以可以正式做四组实验：

```text
A
BM25 Only

B
Dense Only

C
BM25 + Dense + RRF

D
BM25 + Dense + Score Fusion
```

固定：

```text
同一Query Set
同一Knowledge Base
同一Chunk Policy
同一Metadata Filter
同一Gold Evidence
同一Top-K
```

比较：

```text
Hit@K
Recall@K
MRR
Median Gold Rank
Hard Negative Above Gold Rate
No-answer False Retrieval Rate
Latency
```

这时候才能回答：

> Hybrid 是否真的比单一路径更好。

所以：

\[
\boxed{
Hybrid
\neq
AutomaticallyBetter
}
\]

如果融合策略不好，

它完全可能：

> 把两边的噪声也一起合并。

---

# 十五、政府采购里，哪些 Query 特别适合 Sparse，哪些特别适合 Dense？

可以建立一个非常实用的第一版映射。

| Query 类型 | Sparse / BM25 | Dense |
|---|---:|---:|
| 文号 | 强 | 可辅助 |
| 法条编号 | 强 | 可辅助 |
| 项目编号 | 强 | 通常弱 |
| 精确金额 | 强 | 可辅助 |
| 标准编号 | 强 | 通常弱 |
| 机构正式名称 | 强 | 可辅助 |
| 同义改写 | 弱 | 强 |
| 自然语言问题 | 中 | 强 |
| 隐含语义 | 弱 | 强 |
| 长问题概括 | 中 | 强 |

但不要把它变成：

> “看到文号就只跑 BM25。”

更稳妥的默认仍然是：

> **并行召回，再由融合与后续 Reranker 判断。**

除非 Benchmark 证明某些 Query Routing 策略确实更好。

---

# 十六、本阶段工程产物：`ProcurementHybridRetrievalPolicy_V0.1`

第一版至少记录：

```text
sparse_retriever
=
BM25

sparse_analyzer_version

dense_embedding_model
dense_embedding_revision

dense_index_version

sparse_top_n
dense_top_n

candidate_union_policy

dedup_policy

fusion_method
=
rrf / weighted_score / other

rrf_k
如果采用RRF

score_normalization
如果采用Score Fusion

metadata_filter_policy

version_validity_policy

final_top_k

retrieval_benchmark_version
```

同时必须记录实验结果：

```text
bm25_only_metrics
dense_only_metrics
hybrid_metrics

delta_hit_at_k
delta_recall_at_k
delta_mrr

hard_negative_delta
no_answer_delta

latency_delta
```

我们最终不是保存一句：

> “Hybrid 开启。”

而是保存：

> **为什么开启，以及它到底改善了什么。**

---

# 十七、把本阶段压成最精准的 5 句话

> **第一，BM25 属于 Sparse Retrieval，依赖词项匹配、IDF、词频饱和和长度归一化；它尤其擅长文号、金额、条款号、标准号和专有名词等精确信号。**

> **第二，Dense Retrieval 擅长同义改写和语义泛化，但可能淡化数字、编号和细粒度字面差异；因此 Sparse 与 Dense 的盲区具有明显互补性。**

> **第三，Hybrid Retrieval 的稳妥第一版是 BM25 与 Dense 并行召回，各自得到候选，再做去重、融合和后续排序，而不是让其中一条路径先把另一条路径的候选空间砍掉。**

> **第四，BM25 Score 和 Dense Similarity 通常不能直接裸相加；Score Fusion 需要归一化 / 校准，而 RRF 可以直接利用排名进行相对稳健的融合。**

> **第五，Hybrid 是否值得采用，必须回到 `ProcurementRetrievalBenchmark_V0.1` 比较 Hit@K、Recall@K、MRR、Hard Negative、No-answer 和 Latency，不能因为“用了两种检索”就默认更强。**

---

# 本阶段最核心的一张图

```text
                           Query
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
        Sparse Retrieval              Dense Retrieval
             BM25                       Embedding
              │                             │
              ▼                             ▼
        Sparse Top-N                  Dense Top-N
              │                             │
              └──────────────┬──────────────┘
                             ▼
                       Candidate Union
                             │
                             ▼
                           Dedup
                             │
                             ▼
                    Fusion / RRF / Score
                             │
                             ▼
                         Reranker
                             │
                             ▼
                        Final Top-K
                             │
                             ▼
                    Retrieval Benchmark
```

脑中最后只留一句：

> **BM25 找“字面必须对得上”的证据，Dense 找“意思相近但说法不同”的证据；Hybrid 的价值，就是让两种信号同时进入候选竞争。**

---

# 第六课 · 第 7 阶段掌握测试

现在不回看正文，你应该能够解释：Sparse Retrieval 和 Dense Retrieval 的表示方式有什么不同；BM25 为什么不是简单关键词计数；IDF、Term Frequency Saturation 和 Length Normalization 分别解决什么问题；为什么文号、金额、法条编号和项目编号特别适合 Sparse Retrieval；为什么 BM25 对同义改写存在天然弱点；为什么 Dense Retrieval 可能把“17号”和“71号”看得过于接近；为什么中文 Analyzer 会直接影响 BM25；为什么 Hybrid 第一版应该优先并行召回再融合；为什么 BM25 Score 和 Cosine Score 不能直接裸相加；RRF 的核心思想是什么；RRF 公式里的 \(k\) 为什么不是 Top-K；为什么 Candidate Union 后还需要 Dedup 和版本有效性处理；以及为什么最终必须用第 6 阶段的 Retrieval Benchmark 来证明 Hybrid 真的变好。

如果这些能够完整讲出来：

\[
\boxed{
第六课第7阶段真正掌握
}
\]

---

# 下一阶段：第六课 · 第 8 阶段
# Reranker：为什么“先召回，再精排”比直接 Top-K 更可靠？

到第 7 阶段，我们已经有：

\[
BM25
+
DenseRetrieval
\rightarrow
CandidateSet
\]

下一阶段要解决：

> **召回阶段为了不漏掉 Gold Evidence，通常宁愿多拿一些候选；但真正送进 LLM 的 Context 很宝贵，怎样从几十条候选里重新判断谁最值得排在前面？**

我们会正式区分：

```text
Retriever
负责高Recall召回

Reranker
负责高Precision精排
```

并进入：

# Cross-Encoder

以及：

# `ProcurementRerankingPolicy_V0.1`

这会是 RAG 检索链从：

> “找得到”

走向：

> **“把最正确的证据排到最前面”**

的关键一步。

---
