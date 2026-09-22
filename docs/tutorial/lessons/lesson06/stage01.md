# 第六课 · 第 1 阶段
# RAG 到底是什么？从 Parametric Memory 到 External Knowledge
## 为什么已经 Fine-tune 了，还需要 RAG？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：MEDIUM。** 审计原因：核心心智模型出现偏后，阅读前段缺少认知锚点；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，Parametric Memory 是模型通过 Weight 表现出来的已有能力与知识；External Knowledge 是模型外部、可以独立更新和检索的知识资产。**
2. **第二，Fine-tuning 主要改变参数 \(\theta\)，RAG 主要在推理时增加检索证据 \(E\)，把 \(P_\theta(Y|X)\) 变成 \(P_\theta(Y|X,E)\)。**
3. **第三，Knowledge Base 只是知识仓库，Retriever 负责找证据，RAG 是“检索 → 组装 Context → 生成”的完整系统流程，Prompt 则是最终真正送进模型的输入。**
4. **第四，SFT 更适合稳定行为和任务模式，RAG 更适合动态知识、巨大知识库、来源追溯和频繁更新；两者不是竞争关系，而是互补关系。**
5. **第五，RAG 答错以后必须先定位 Knowledge、Retrieval、Ranking、Context 还是 Generation 出错，不能把所有问题统称为“LLM 幻觉”。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Parametric Memory` | 参数记忆：编码在模型权重中的知识和模式 |
| `Memory` | 任务记忆：保存跨步骤需要复用的结构化信息 |
| `External Knowledge` | 外部知识：位于模型参数之外、可检索可更新的资料 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `SFT` | 监督微调：用监督样本继续更新模型参数 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |
| `LoRA` | LoRA：冻结大部分基座参数，只训练低秩增量矩阵 |

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

第五课结束时，我们已经拥有：

\[
\boxed{
ProcurementLM\_V0.1
}
\]

它通过 SFT + LoRA / QLoRA，已经比原始 Base Model 更懂我们的政府采购任务。

但现在马上遇到一个问题。

假设明天发布了一份新的政府采购政策文件。

你希望模型回答：

> “按照目前有效规定，这条采购要求是否存在风险？依据是什么？”

这时候我们有两个完全不同的办法。

第一种：

```text
新法规
↓
重新整理训练数据
↓
再次SFT
↓
训练新Adapter
↓
重新评测
↓
重新发布
```

第二种：

```text
新法规
↓
进入Knowledge Base
↓
用户提问
↓
检索相关法规
↓
把法规放进Context
↓
ProcurementLM_V0.1基于证据回答
```

第二条路线，就是今天正式进入的：

# RAG
## Retrieval-Augmented Generation
## 检索增强生成

本阶段最终形成一个核心工程模型：

# `RAGBoundaryModel_V0.1`

---

## 一、先把 RAG 压缩成一句最准确的话

RAG 不是一种新的 Transformer。

也不是一种新的 Fine-tuning。

它是一套**推理时系统**：

\[
\boxed{
Query
\rightarrow
Retrieve\ Evidence
\rightarrow
Add\ Evidence\ to\ Context
\rightarrow
Generate
}
\]

中文就是：

> **先根据用户问题从外部知识源找到相关证据，再把这些证据交给 LLM，让模型基于证据生成答案。**

所以 RAG 最核心的变化不是：

\[
\theta
\]

也就是模型参数。

而是：

\[
Context
\]

---

# 二、Parametric Memory：知识已经进入了模型参数

第五课我们训练模型时，本质上不断修改：

\[
\theta
\]

也就是模型内部参数。

于是可以粗略把模型已经学进去的能力和知识称为：

# Parametric Memory
## 参数化记忆

例如 Base Model 本来可能已经知道：

```text
什么是供应商
什么是资格条件
什么是履约能力
中文法律文本怎样表达
什么叫“投标截止日前”
```

第五课的 SFT 又进一步教它：

```text
看到什么业务结构应该判断风险
怎样区分准入条件和履约条件
怎样按照我们的Schema输出
怎样解释理由
什么时候needs_review
```

这些东西最终体现为：

> 模型 Weight 的变化。

因此可以写成：

\[
P_{\theta}(Y|X)
\]

模型用：

> 参数 \(\theta\)

去处理输入 \(X\)。

但是这里一定要注意：

> **Parametric Memory 不是一个可以打开浏览的法规数据库。**

你不能问某个 Weight：

> “你这里存的是财政部哪一份文件？”

知识是：

> 分布式地编码在大量参数及其交互中。

---

# 三、External Knowledge：知识不进 Weight，而留在模型外面

另一种知识形态是：

# External Knowledge
## 外部知识

例如我们的政府采购系统可以维护：

```text
法律
法规
财政部门规章
规范性文件
政策文件
地方规则
采购文件
质疑答复
投诉处理案例
专家解释
内部审查规则
```

这些东西不用全部训练进模型。

它们可以作为：

# Knowledge Base
## 知识库

独立存在。

用户提问以后，我们临时找到最相关的几段：

```text
Evidence 1
Evidence 2
Evidence 3
```

再交给模型。

于是推理变成：

\[
P_{\theta}
(
Y
\mid
X,\;E
)
\]

其中：

\[
E
=
RetrievedEvidence
\]

非常关键的一点：

> **此时 \(\theta\) 可以完全不变。**

变的是：

\[
E
\]

也就是模型这一次看到的外部证据。

---

# 四、这就是 Fine-tuning 和 RAG 最根本的数学区别

第五课 Fine-tuning：

\[
\theta
\rightarrow
\theta'
\]

于是：

\[
P_{\theta}(Y|X)
\rightarrow
P_{\theta'}(Y|X)
\]

也就是：

> **换参数。**

RAG：

\[
\theta
\text{ 不一定变化}
\]

而是：

\[
P_{\theta}(Y|X)
\rightarrow
P_{\theta}(Y|X,E)
\]

也就是：

> **增加检索到的证据条件。**

所以整个课程到这里，可以形成一个非常漂亮的边界：

\[
\boxed{
FineTuning
=
改变模型怎样思考和行动
}
\]

\[
\boxed{
RAG
=
改变模型这一次拿什么资料思考
}
\]

这是第六课最重要的第一根柱子。

---

# 五、Prompt、RAG、Knowledge Base、Fine-tuning 四者不要混

这四个概念非常容易搅在一起。

| 概念 | 本质 | 主要解决什么 |
|---|---|---|
| **Prompt** | 当前送给模型的输入指令与上下文 | 告诉模型这一次做什么 |
| **Knowledge Base** | 模型外部的知识资产 | 保存可更新、可追溯的事实和证据 |
| **RAG** | 动态检索并注入知识的系统流程 | 决定这一次应该把哪些知识放进 Prompt |
| **Fine-tuning** | 修改模型参数 | 改变稳定行为、任务能力和输出习惯 |

所以：

\[
\boxed{
KnowledgeBase
\neq
RAG
}
\]

知识库只是：

> “仓库”。

RAG 才是：

> **根据问题去仓库找东西，并把找到的东西送给模型。**

同样：

\[
\boxed{
Prompt
\neq
RAG
}
\]

Prompt 是最终输入。

RAG 是：

> **动态构造 Prompt Context 的机制之一。**

---

# 六、用一个政府采购案例完整看一次

用户问：

> 某采购文件要求“投标供应商必须在本市连续经营三年以上”，这种要求是否存在风险？

如果没有 RAG：

```text
用户问题
   ↓
ProcurementLM_V0.1
   ↓
依靠模型已有参数
   ↓
回答
```

模型可能依据第五课训练出的行为判断：

> 该条件可能构成地域或经营年限方面的不合理准入限制。

这个回答可能是对的。

但用户进一步问：

> “依据当前有效的哪一份规则？”

问题就来了。

模型参数里即使“知道一些”，也很难保证：

```text
文件名称正确
条款编号正确
版本仍然有效
没有被后续文件替代
适用地区正确
发布日期正确
```

RAG 系统则变成：

```text
用户问题
   ↓
Retrieval
   ↓
找到当前有效法规 / 文件
   ↓
筛选相关条款
   ↓
加入Context
   ↓
ProcurementLM_V0.1
   ↓
基于证据判断
   ↓
回答 + 来源
```

于是模型处理的不再只是：

> “凭参数记忆回答。”

而是：

> **拿着当前证据回答。**

---

# 七、为什么第五课 Fine-tuning 不能代替 RAG？

因为有几类信息天然更适合留在模型外。

最典型就是：

### 经常变化的信息

例如：

```text
新法规
政策调整
废止文件
地区规则变化
最新采购项目
最新案例
```

如果全部依赖 Fine-tuning：

> 每更新一次知识，都要重新训练模型。

这非常笨重。

---

第二类是：

### 必须可追溯的信息

政府采购系统经常不能只回答：

> “我觉得有风险。”

还需要：

```text
依据什么？
哪份文件？
哪个条款？
哪个版本？
什么时候生效？
适用于哪里？
```

参数化记忆很难天然提供可靠出处。

外部知识库则可以保留：

```text
source_id
title
article
issuer
effective_date
expiry_date
jurisdiction
version
URL / document_id
```

于是：

> 答案能够连接回证据。

---

第三类是：

### 规模巨大但单次只需要一小部分的信息

假设我们最终有：

```text
100万份采购文件
10万份政策法规
几十万案例
```

用户一次只问：

> 一个资格条款。

没必要把全部内容塞进 Context，更没必要每次全部训练进 Weight。

RAG 的思想恰恰是：

\[
\boxed{
HugeKnowledgeBase
\rightarrow
SmallRelevantEvidenceSet
}
\]

---

# 八、但是 RAG 也绝对不能代替 Fine-tuning

这又是另一个常见误区。

有人会说：

> “既然可以 RAG，那还微调干什么？”

不对。

假设 Base Model 拿到了正确法规，但它：

```text
不会按采购审查Schema输出
不会区分资格与履约
不会处理Hard Negative
总是给出冗长泛泛解释
不知道什么时候needs_review
```

那么即使检索完全正确：

> 最终答案还是可能很差。

因为 RAG 给模型解决的是：

> **Know what evidence to see**

但 SFT 更接近解决：

> **Know how to behave with that evidence**

因此我们的最终系统不是二选一：

\[
FineTuning
\quad vs \quad
RAG
\]

而是：

\[
\boxed{
FineTunedModel
+
RAG
}
\]

也就是：

```text
ProcurementLM_V0.1
负责：
判断方式
输出格式
业务行为
推理习惯

RAG
负责：
当前法规
项目事实
可追溯证据
动态知识
```

这两个是互补关系。

---

# 九、RAG 真正的完整链条，其实有两套系统

一个 RAG 系统至少有：

### Offline / Indexing Path
知识准备链

```text
Documents
   ↓
Parse
   ↓
Clean
   ↓
Chunk
   ↓
Embedding / Index
   ↓
Knowledge Base Ready
```

另一套是：

### Online / Query Path
在线查询链

```text
User Query
   ↓
Query Processing
   ↓
Retrieval
   ↓
Ranking
   ↓
Context Assembly
   ↓
LLM
   ↓
Answer + Citation
```

这两个必须分开。

因为：

> 用户每问一次问题，我们不会重新把整个法规库 Chunk 一遍。

知识库构建通常是：

> 离线准备。

用户查询则是：

> 在线检索。

后面第 2～10 阶段，基本就是把这两条链一层层拆开。

---

# 十、RAG 最重要的工程思想：先检索，再生成

以后一个 RAG 答错了，绝不能只说：

> “LLM 又幻觉了。”

因为错误可能发生在完全不同的位置。

例如用户问：

> “本项目要求供应商投标前在当地设立机构是否合法？”

最终答案错误。

至少存在五种可能：

| 错误层 | 真正发生了什么 |
|---|---|
| **Knowledge Error** | 知识库缺少正确法规，或者保存的是过期版本 |
| **Retrieval Error** | 正确证据存在，但没有被检索出来 |
| **Ranking Error** | 正确证据找到了，但排名太低，没有进入最终 Context |
| **Context Error** | 正确证据进入系统，但拼接、截断或冲突处理出了问题 |
| **Generation Error** | 正确证据已经清楚放进 Prompt，模型仍然理解或判断错误 |

这就是第六课相较第五课最大的思维升级：

> **模型错误开始变成“系统错误定位”。**

---

# 十一、为什么 RAG 不能保证“有证据就绝对不幻觉”？

这是必须提前拆掉的一个神话。

错误理解：

\[
RAG
=
NoHallucination
\]

不成立。

RAG 只能让模型获得：

> **更好的外部证据条件。**

但模型依然可能：

```text
忽略证据
误解证据
把两份法规混在一起
引用正确但结论错误
把旧规则和新规则搞反
在证据没有覆盖的地方自行补充
```

甚至检索本身就可能给错材料。

所以更正确的表达是：

\[
\boxed{
RAG
可以提高Grounding机会
但不自动保证Grounded Answer
}
\]

因此后面我们必须同时评测：

\[
RetrievalQuality
\]

和：

\[
GenerationQuality
\]

---

# 十二、什么时候应该用 Fine-tuning，什么时候应该用 RAG？

到这里已经可以建立第一版工程决策模型。

如果需求是：

> “模型以后统一按照这种 JSON Schema 输出。”

优先考虑：

# SFT

如果需求是：

> “让模型掌握政府采购风险判断的稳定模式。”

可以考虑：

# SFT / LoRA

如果需求是：

> “今天新增一份法规，明天就能引用。”

优先：

# RAG

如果需求是：

> “回答必须告诉我依据哪一条文件。”

优先：

# RAG + Citation

如果需求是：

> “某个具体采购项目的 300 页招标文件里，第 87 页和第 142 页是否冲突？”

这通常也是：

# Retrieval / Document Context

而不是：

> 重新 Fine-tune 一个模型。

所以一个很好用的长期判断是：

\[
\boxed{
稳定行为
\rightarrow
FineTuning
}
\]

\[
\boxed{
动态事实与证据
\rightarrow
RAG
}
\]

当然真实系统里：

> 二者经常同时存在。

---

# 十三、本阶段工程产物：`RAGBoundaryModel_V0.1`

从现在开始，我们给系统能力建立一个明确责任表：

```text
Base Model
=
通用语言 / 推理基础能力

SFT / LoRA
=
稳定政府采购行为
输出Schema
决策方式
Hard Case边界

Knowledge Base
=
外部事实与证据资产

Retriever
=
从知识库找到候选证据

Reranker
=
重新判断候选证据优先级

Context Builder
=
决定哪些证据真正进入Prompt

ProcurementLM_V0.1
=
读取问题 + 证据并生成判断

Citation Layer
=
把结论连接回证据来源
```

最终系统可以压成：

\[
\boxed{
Answer
=
LLM_{\theta'}
(
Question,
RetrievedEvidence
)
}
\]

其中：

\[
\theta'
\]

来自第五课 Fine-tuning。

而：

\[
RetrievedEvidence
\]

来自第六课 RAG。

这两个终于在这里汇合。

---

# 十四、把本阶段压成最精准的 5 句话

> **第一，Parametric Memory 是模型通过 Weight 表现出来的已有能力与知识；External Knowledge 是模型外部、可以独立更新和检索的知识资产。**

> **第二，Fine-tuning 主要改变参数 \(\theta\)，RAG 主要在推理时增加检索证据 \(E\)，把 \(P_\theta(Y|X)\) 变成 \(P_\theta(Y|X,E)\)。**

> **第三，Knowledge Base 只是知识仓库，Retriever 负责找证据，RAG 是“检索 → 组装 Context → 生成”的完整系统流程，Prompt 则是最终真正送进模型的输入。**

> **第四，SFT 更适合稳定行为和任务模式，RAG 更适合动态知识、巨大知识库、来源追溯和频繁更新；两者不是竞争关系，而是互补关系。**

> **第五，RAG 答错以后必须先定位 Knowledge、Retrieval、Ranking、Context 还是 Generation 出错，不能把所有问题统称为“LLM 幻觉”。**

---

# 本阶段最核心的一张图

```text
                     Procurement AI
                           │
          ┌────────────────┴────────────────┐
          │                                 │
          ▼                                 ▼
   Parametric Memory                 External Knowledge
          │                                 │
          ▼                                 ▼
     Base Model                     Knowledge Base
          │                                 │
     SFT / LoRA                         Retrieval
          │                                 │
          ▼                                 ▼
 ProcurementLM_V0.1              Retrieved Evidence
          │                                 │
          └───────────────┬─────────────────┘
                          ▼
                       Context
                          │
                          ▼
                        LLM
                          │
                          ▼
                Answer + Evidence
```

脑中最后只留一句：

> **Fine-tuning 决定模型“怎样做事”，RAG 决定模型“这一次拿什么证据做事”。**

---

# 第六课 · 第 1 阶段掌握测试

现在不回看正文，你应该能够解释：什么是 RAG；Parametric Memory 和 External Knowledge 有什么区别；为什么模型 Weight 不能等同于法规数据库；Fine-tuning 和 RAG 数学上分别改变什么；Prompt、Knowledge Base、Retriever 和 RAG 为什么不是同一个东西；为什么新法规更适合进入 Knowledge Base 而不是每次重新训练；为什么 RAG 无法完全取代 SFT；为什么 SFT 也无法取代 RAG；Offline Indexing Path 和 Online Query Path 有什么区别；为什么检索到证据并不保证最终回答正确；Knowledge、Retrieval、Ranking、Context、Generation 五类错误分别是什么；以及为什么最终 `ProcurementRAG_V0.1` 应该是 `ProcurementLM_V0.1 + External Evidence System`，而不是另一个孤立模型。

如果这些都能自己讲清楚：

\[
\boxed{
第六课第1阶段真正掌握
}
\]

---

# 下一阶段：第六课 · 第 2 阶段
# Knowledge Base：法规、采购文件与知识版本怎样进入 RAG？

下一阶段我们暂时**不讲 Embedding**。

因为在讨论：

> “怎样找到知识”

之前，必须先解决：

> **到底有哪些知识值得进入库，以及怎么保证这份知识是真的、当前有效、可以追溯。**

下一阶段我们会正式处理：

```text
Document
↓
Source Identity
↓
Authority / Jurisdiction
↓
Effective Date
↓
Version
↓
Document Structure
↓
Metadata
↓
Knowledge Unit
↓
Knowledge Base
```

重点解决政府采购 RAG 里一个极其现实的问题：

> **如果知识库自己装着过期法规、重复版本和来源不明的文本，再强的 Embedding 和 Retriever，也只是在更高效地找错答案。**

---
