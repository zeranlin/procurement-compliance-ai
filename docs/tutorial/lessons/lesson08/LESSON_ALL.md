# 第八课：CPT 与高级领域适配

> **V2 教学增强版。** 共 10 个阶段；主要产物/主线：`ProcurementLM_V0.2`。  
> 核心心智模型前置、中文释义增强、详细正文完整保留。

---


<!-- LESSON 08 STAGE 01 START -->

# 第八课 · 第 1 阶段
# CPT 到底在学什么？为什么已经有 SFT / RAG / Agent 还要继续预训练？
## Continued Pretraining 的真正边界：什么时候应该继续改模型参数，什么时候根本不该做 CPT？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，CPT 是在领域语料上继续执行 Next Token Prediction，让模型参数适应新的 Domain Distribution；它不是 SFT，也不是把知识库简单写进 Weight。**
2. **第二，CPT 学的是领域语言与统计结构，SFT 学的是任务行为，RAG 提供当前外部证据，Agent 负责受控执行工作流。**
3. **第三，课程把 CPT 放在第八课，但真实训练顺序通常更接近 Base → CPT → SFT；如果在 SFT 后直接大量 CPT，可能破坏原有对齐行为。**
4. **第四，CPT 最适合“大量高质量无标注领域语料 + 明显领域分布差距”的场景；实时知识、结构化输出和任务格式问题往往应该优先用 RAG 或 SFT。**
5. **第五，CPT 的核心风险包括 Catastrophic Forgetting、Domain Over-specialization 和 Benchmark Contamination，所以必须同时评测领域收益、通用能力回归和数据防泄漏。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `CPT` | CPT/继续预训练：在领域语料上继续执行预训练目标 |
| `SFT` | 监督微调：用监督样本继续更新模型参数 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `Continued Pretraining` | 继续预训练：让基座模型适应特定领域语言和知识分布 |
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

到第七课结束，我们已经拥有：

\[
\boxed{
ProcurementLM\_V0.1
+
ProcurementRAG\_V0.1
+
ProcurementAgent\_V0.1
}
\]

看起来系统已经会：

```text
理解任务
检索法规
调用工具
维护状态
生成报告
```

那为什么还需要 CPT？

因为：

> **“系统会做采购任务”不等于“模型本体已经真正适应政府采购领域分布”。**

CPT 要解决的是另一类问题：

# Continued Pretraining
## 继续预训练

本阶段最终形成：

# `ProcurementCPTBoundaryModel_V0.1`

---

# 一、先锁死本阶段最重要的一句话

CPT 的本质不是：

> “再做一次 SFT。”

也不是：

> “把法规全文背进模型。”

更准确地说：

\[
\boxed{
CPT
=
在领域语料分布上继续执行预训练目标
}
\]

它仍然学习：

\[
\boxed{
NextTokenPrediction
}
\]

也就是：

\[
\mathcal{L}_{CPT}
=
-\sum_{t=1}^{T}
\log
p_{\theta}
(
x_t
\mid
x_{<t}
)
\]

模型仍然在做：

> **根据前面的 Token，预测下一个 Token。**

只是训练数据从通用互联网分布，

变成了：

> 政府采购领域分布。

---

# 二、CPT 真正在改变什么？

假设 Base Model 大量见过：

```text
新闻
百科
代码
社交媒体
一般法律文本
```

但政府采购领域经常出现：

```text
资格条件
评分办法
采购需求
履约验收
中小企业声明函
采购人代表
实质性响应
不合理条件
评审因素
采购标的所属行业
```

这些词模型也许“认识”。

但不代表它已经充分学会：

```text
这些词怎样共同出现
哪些概念经常互相约束
文档结构怎样组织
采购语言的统计规律
典型上下文怎样延续
```

所以 CPT 改的是：

\[
\boxed{
DomainLanguageDistribution
}
\]

以及由此形成的：

> **模型参数中的领域先验。**

---

# 三、最重要的边界：CPT、SFT、RAG、Agent 分别解决什么？

这四个东西必须彻底分开。

| 技术 | 主要解决的问题 | 主要改变什么 |
|---|---|---|
| CPT | 模型对领域语言与分布不够熟 | Weights |
| SFT | 模型不会按任务要求回答 | Weights / Behavior |
| RAG | 模型缺当前外部知识与证据 | Context |
| Agent | 模型不会执行多步骤真实任务 | Control Loop + Tools |

可以压成：

\[
\boxed{
CPT
=
LearnDomainDistribution
}
\]

\[
\boxed{
SFT
=
LearnTaskBehavior
}
\]

\[
\boxed{
RAG
=
ProvideExternalEvidence
}
\]

\[
\boxed{
Agent
=
ExecuteControlledWorkflow
}
\]

这四者不是替代关系。

---

# 四、为什么已经做过 SFT，仍然可能需要 CPT？

假设 `ProcurementLM_V0.1` 已经学会：

```text
输入：
采购条款

输出：
风险判断
理由
证据需求
```

但模型可能仍然存在：

```text
遇到长篇采购文件理解不稳定
领域术语之间关系不够自然
少见采购表达容易误解
生成文本虽然格式正确，但领域语言“味道不对”
复杂条款续写与结构理解弱
```

这说明：

> SFT 教会了“任务形式”，但底层领域分布可能仍然不够强。

所以：

\[
\boxed{
TaskBehaviorGood
\not\Rightarrow
DomainModelingGood
}
\]

---

# 五、一个非常重要的训练顺序问题：CPT 通常应该在 SFT 之前

真实工程里，最常见的顺序是：

```text
Base Model
↓
CPT
↓
Domain-adapted Base
↓
SFT
↓
Task Model
```

为什么？

因为 CPT 的目标仍然是：

> 无监督 / 自监督语言建模。

而 SFT 已经把模型推向：

> 指令遵循和任务格式。

如果你在 SFT 以后直接做大量 CPT，

可能发生：

```text
指令遵循变弱
Chat Template行为退化
结构化输出能力下降
原来的任务对齐被冲淡
```

所以：

\[
\boxed{
CourseOrder
\neq
TrainingOrder
}
\]

我们现在第八课才学 CPT，

是课程教学顺序。

真正训练 `ProcurementLM_V0.2` 时，

很可能采用：

\[
\boxed{
Base
\rightarrow
CPT
\rightarrow
SFT
}
\]

重新形成一个更强版本。

---

# 六、什么时候 CPT 是值得做的？

CPT 最有价值的场景通常满足：

```text
有大量高质量领域无标注文本

领域语言分布与通用语料明显不同

模型对领域术语 / 结构 / 语义组合不够稳定

SFT数据有限，无法覆盖整个领域分布

希望增强领域基础能力，而不只是某一个任务
```

例如你有：

```text
数百万页采购公告
采购文件
合同文本
评审规则
采购需求
政策解读
行业采购语料
```

其中真正人工标注的也许只有：

```text
几万条
```

那么：

> 无标注领域语料远多于 Gold SFT 数据。

CPT 就可能非常有价值。

---

# 七、什么时候不应该优先做 CPT？

第一种：

> **问题主要是实时知识缺失。**

例如：

```text
今天最新的采购政策是什么？
某项目当前预算是多少？
某规则现在是否仍有效？
```

这类问题优先：

\[
\boxed{
RAG / Tool
}
\]

而不是 CPT。

因为把动态事实写入 Weight：

> 更新慢、不可追踪、难以保证新鲜度。

---

第二种：

> **问题主要是输出格式和任务行为。**

例如：

```text
总是不按JSON输出
不会按照风险Schema回答
不会遵守审查模板
```

优先应该看：

\[
\boxed{
SFT
}
\]

---

第三种：

> **领域语料数量太少或质量很差。**

如果只有：

```text
几百篇文档
大量重复
OCR错误严重
版本混乱
```

贸然 CPT 很可能：

> 收益有限，甚至把模型训坏。

---

# 八、CPT 不是“把知识背进 Weight”的可靠数据库方案

这是最容易误解的地方之一。

模型经过 CPT 后，

可能更熟悉：

```text
政府采购术语
采购文件结构
常见政策表达
领域推理模式
```

但不能因此认为：

> “法规已经永久写进参数，所以以后不用 RAG。”

因为 Weight 中的知识：

```text
难以精确追踪来源
更新成本高
可能记错
可能混版本
不能保证逐字准确
```

所以：

\[
\boxed{
CPT
\neq
KnowledgeDatabase
}
\]

更合理的是：

\[
\boxed{
CPT
提高领域理解底座
+
RAG
提供当前可追溯证据
}
\]

---

# 九、CPT 最大的风险之一：Catastrophic Forgetting

如果只拿大量采购文本继续训练，

模型可能越来越像：

> 一个采购领域专用模型。

但同时：

```text
通用语言能力下降
代码能力下降
数学能力下降
一般指令遵循下降
其他领域理解下降
```

这叫：

# Catastrophic Forgetting
## 灾难性遗忘

可以把它理解为：

\[
\boxed{
DomainGain
可能换来
GeneralCapabilityLoss
}
\]

所以 CPT 不能只看：

> “采购 Benchmark 涨没涨。”

还必须检查：

> 通用能力有没有退化。

---

# 十、CPT 的第二个风险：Domain Over-specialization

即使没有严重遗忘，

也可能发生：

> 模型对采购语言过度敏感。

例如看到：

```text
本市
注册资本
业绩
服务机构
```

就过度联想到：

> 风险。

这和第一课讲过的 Shortcut Learning 很像。

所以 CPT 数据如果分布偏斜：

> 模型会把领域偏差一起学进去。

因此：

\[
\boxed{
MoreDomainData
\neq
BetterDomainModel
}
\]

关键是：

> **领域语料的质量、覆盖与分布。**

---

# 十一、CPT 的第三个风险：Benchmark Contamination

假设未来 `ProcurementBench_V1` 中包含：

```text
1000个高质量Gold案例
```

如果这些测试样本原文被混进 CPT Corpus，

模型测试时可能：

> 见过原题。

此时 Benchmark 分数再高，

也不能证明泛化能力。

所以：

\[
\boxed{
CPTCorpus
必须和Benchmark建立Firewall
}
\]

至少要检查：

```text
exact duplicate
near duplicate
same project
same document lineage
future benchmark candidate
```

这一点会直接连接后面的 Benchmark 课程。

---

# 十二、CPT 真正需要建立的是“决策门”，不是“训练冲动”

在决定 CPT 前，

先问五个问题：

```text
1. 当前主要错误真的是领域分布不足吗？

2. 有没有足够规模的高质量领域语料？

3. 这些问题能不能更便宜地通过RAG / SFT解决？

4. 我们有没有能力检测灾难性遗忘？

5. 我们有没有干净的Benchmark证明CPT真的带来收益？
```

只有这些问题大体成立，

才进入：

> CPT Experiment。

所以：

\[
\boxed{
DoCPT
必须是EvidenceBasedDecision
}
\]

而不是：

> “听说领域模型都要继续预训练。”

---

# 十三、本阶段工程产物：`ProcurementCPTBoundaryModel_V0.1`

第一版至少锁定：

```text
cpt_goal

domain_gap_hypothesis

target_capabilities

non_targets

candidate_domain_corpus

expected_domain_gain

general_capability_risk

forgetting_evaluation_plan

benchmark_firewall

rag_alternative

sft_alternative

cpt_go_no_go_criteria

training_order

release_target
=
ProcurementLM_V0.2
```

我们以后任何 CPT 实验，

都不能只写：

```text
“继续训练100B tokens”
```

而必须先回答：

> **为什么训练、想提升什么、可能损失什么、怎样证明收益。**

---

# 十四、把本阶段压成最精准的 6 句话

> **第一，CPT 是在领域语料上继续执行 Next Token Prediction，让模型参数适应新的 Domain Distribution；它不是 SFT，也不是把知识库简单写进 Weight。**

> **第二，CPT 学的是领域语言与统计结构，SFT 学的是任务行为，RAG 提供当前外部证据，Agent 负责受控执行工作流。**

> **第三，课程把 CPT 放在第八课，但真实训练顺序通常更接近 `Base → CPT → SFT`；如果在 SFT 后直接大量 CPT，可能破坏原有对齐行为。**

> **第四，CPT 最适合“大量高质量无标注领域语料 + 明显领域分布差距”的场景；实时知识、结构化输出和任务格式问题往往应该优先用 RAG 或 SFT。**

> **第五，CPT 的核心风险包括 Catastrophic Forgetting、Domain Over-specialization 和 Benchmark Contamination，所以必须同时评测领域收益、通用能力回归和数据防泄漏。**

> **第六，真正专业的 CPT 起点不是启动 GPU，而是先建立 `Go / No-Go` 决策门：证明问题确实需要改 Weight，而且收益能够被干净 Benchmark 验证。**

---

# 本阶段最核心的一张图

```text
                      Current System
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
     Domain Gap?      Task Behavior?   Fresh Knowledge?
          │                │                │
          ▼                ▼                ▼
         CPT              SFT              RAG
          │
          ▼
   Domain Corpus Ready?
          │
      ┌───┴───┐
      ▼       ▼
     Yes      No
      │        │
      ▼        ▼
 Forgetting   Improve Data
 Evaluation
      │
      ▼
 Benchmark Firewall
      │
      ▼
   CPT Experiment
      │
      ▼
 Domain Gain + General Regression
      │
      ▼
      SFT
      │
      ▼
 ProcurementLM_V0.2
```

脑中最后只留一句：

> **CPT 的价值不是“让模型多背一些采购文本”，而是当模型的底层语言分布与政府采购领域存在真实差距时，用大量高质量领域语料继续塑造参数，同时用 Replay、Benchmark 和回归测试防止模型为了更懂采购而忘掉原本会的东西。**

---

# 第八课 · 第 1 阶段掌握测试

现在不回看正文，你应该能够解释：CPT 的训练目标为什么仍然是 Next Token Prediction；CPT、SFT、RAG、Agent 四者分别解决什么问题；为什么 SFT 已经成功并不代表领域建模已经充分；为什么真实训练顺序通常是 `Base → CPT → SFT`；什么场景值得做 CPT；哪些问题应该优先交给 RAG 或 SFT；为什么 CPT 不能替代知识库；什么是 Catastrophic Forgetting；什么是 Domain Over-specialization；为什么 Benchmark Contamination 会让 CPT 评测失真；以及为什么真正开始 CPT 前必须先建立 Go / No-Go 决策标准。

如果这些能够完整讲出来：

\[
\boxed{
第八课第1阶段真正掌握
}
\]

---

# 下一阶段：第八课 · 第 2 阶段
# Domain Corpus：什么样的政府采购领域语料值得用于 CPT？
## “采购文本越多越好”为什么是错的？怎样把原始文档变成真正适合继续预训练的领域语料？

下一阶段会正式进入：

```text
Source Selection
Corpus Scope
Quality Filter
Deduplication
Document Mix
Domain Coverage
Temporal Coverage
Document Lineage
PII / Sensitive Data
Benchmark Firewall
Token Budget
Corpus Versioning
```

并建立：

# `ProcurementCPTCorpusPolicy_V0.1`

核心问题是：

\[
\boxed{
CPT效果的上限
首先由Corpus决定
}
\]

---

<!-- LESSON 08 STAGE 01 END -->


<!-- LESSON 08 STAGE 02 START -->

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

<!-- LESSON 08 STAGE 02 END -->


<!-- LESSON 08 STAGE 03 START -->

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

<!-- LESSON 08 STAGE 03 END -->


<!-- LESSON 08 STAGE 04 START -->

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

<!-- LESSON 08 STAGE 04 END -->


<!-- LESSON 08 STAGE 05 START -->

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

<!-- LESSON 08 STAGE 05 END -->


<!-- LESSON 08 STAGE 06 START -->

# 第八课 · 第 6 阶段
# Catastrophic Forgetting：为什么模型学会领域知识以后，反而可能忘掉原来的能力？
## CPT 的真正难点不是“领域能力能不能涨”，而是“涨了以后有没有把模型其他能力一起弄坏”。

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **SharedParameters ⇒ CapabilityInterference。模型能力共享参数，学习新领域可能干扰旧能力。**
2. **DomainGain ≠ NetModelGain。领域能力上涨只是收益的一面，原有能力回归必须同时计入。**
3. **Overfitting ≠ Forgetting。前者是新任务泛化变差，后者是旧能力被新学习破坏。**
4. **BestDomainCheckpoint ≠ BestReleaseCheckpoint。领域分数最高的模型，不一定是综合能力最适合发布的模型。**
5. **WeightDistance ≠ CapabilityRegression。参数漂移只能做诊断，行为 Benchmark 才是最终证据。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `CPT` | CPT/继续预训练：在领域语料上继续执行预训练目标 |
| `Catastrophic Forgetting` | 灾难性遗忘：领域训练后通用能力明显退化 |
| `Regression` | 回归测试：更新后验证旧能力和关键切片没有退化 |
| `Checkpoint` | 检查点：保存模型和训练状态以便恢复/发布 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Retention` | 能力保持：领域增强时尽量保住原有通用能力 |

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

到第 5 阶段，我们已经能够设计：

\[
\boxed{
Corpus
+
Tokenizer
+
Sequence
+
Mixture
}
\]

也就是说，我们已经知道：

> 用什么数据、怎样切 Token、怎样组成训练序列、不同数据分别训练多少。

接下来必须面对 CPT 最危险的问题之一：

# Catastrophic Forgetting
## 灾难性遗忘

模型在政府采购语料上持续更新参数以后，可能发生：

```text
采购语言能力上升

但同时：

通用语言能力下降
数学能力下降
代码能力下降
一般知识下降
指令遵循下降
原有SFT行为变弱
```

所以本阶段最终形成：

# `ProcurementCPTForgettingPolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

CPT 成功不能只看：

> **Domain Score 有没有上涨。**

真正应该看：

\[
\boxed{
DomainGain
\neq
NetModelGain
}
\]

进一步：

\[
\boxed{
NetModelGain
=
DomainGain
-
CapabilityRegressionCost
}
\]

这里不是要求把所有能力真的压成一个简单数字。

而是建立工程判断：

> **领域能力上涨，只是收益的一面；被破坏的原有能力，是必须同时计入的成本。**

---

# 二、什么是 Catastrophic Forgetting？

可以把模型参数记成：

\[
\theta_0
\]

表示 CPT 之前的模型。

经过领域训练以后变成：

\[
\theta_1
\]

如果训练目标几乎只来自采购领域，

梯度会持续推动参数：

\[
\theta_0
\rightarrow
\theta_1
\]

去适应新的领域分布。

问题在于：

> 原来的参数同时承担着通用语言、知识、数学、代码、指令行为等很多能力。

当这些参数为了采购分布不断调整时，

原来的某些能力可能下降。

这就是：

\[
\boxed{
NewLearning
可能干扰
OldCapability
}
\]

---

# 三、核心心智模型 ①：模型参数是“共享资产”，不是一个能力一个独立文件夹

不要把模型想象成：

```text
采购能力
放在A文件夹

数学能力
放在B文件夹

代码能力
放在C文件夹
```

真实神经网络更接近：

> 大量能力共享同一套参数和表示空间。

所以：

\[
\boxed{
SharedParameters
\Rightarrow
CapabilityInterference
}
\]

学习采购领域时更新同一套参数，

就可能同时影响：

```text
语言表示
注意力模式
事实关联
推理习惯
输出分布
```

这就是为什么：

> “只是继续训练一些采购文本”

并不等于：

> “只增加采购知识，不碰其他能力”。

---

# 四、Forgettting 和 Overfitting 不是一回事

这两个非常容易混。

# Overfitting
## 过拟合

主要指：

> 对训练数据学得太死，泛化到同分布新样本时变差。

例如：

```text
训练集采购条款
表现很好

新的采购条款
表现明显下降
```

而：

# Catastrophic Forgetting
## 灾难性遗忘

主要指：

> 学习新领域以后，原本已有能力退化。

例如：

```text
采购能力
上涨

数学
下降

通用问答
下降

代码
下降
```

所以：

\[
\boxed{
Overfitting
\neq
Forgetting
}
\]

一个模型甚至可能：

> 采购领域没有过拟合，

但仍然发生明显遗忘。

---

# 五、核心心智模型 ②：Domain Improvement 和 General Retention 是两个独立坐标轴

不要只用一条：

```text
采购分数
```

评估 CPT。

至少要同时看：

```text
X轴：
Domain Gain
领域能力提升

Y轴：
General Retention
通用能力保留
```

于是可能出现四种情况：

| 领域能力 | 通用能力 | 解释 |
|---|---|---|
| ↑ | 稳定 | 理想 |
| ↑ | ↓ | 有收益但发生遗忘 |
| ≈ | 稳定 | CPT收益有限 |
| ↓ | ↓ | 明显失败 |

所以：

\[
\boxed{
CPTSuccess
=
DomainGain
+
GeneralRetention
}
\]

---

# 六、哪些能力最需要做回归监控？

第一版至少可以分成五层。

## 1. General Language
### 通用语言能力

检查：

```text
摘要
改写
阅读理解
常识问答
基本写作
```

---

## 2. Reasoning
### 推理能力

例如：

```text
基础数学
逻辑判断
多步推理
简单表格理解
```

---

## 3. Code / Structured Reasoning
### 代码与结构化推理

如果底座模型原本具备：

```text
代码生成
JSON
Schema遵循
简单程序理解
```

也应该监控。

---

## 4. Instruction Following
### 指令遵循

尤其重要，因为我们的最终系统不是纯 Base Model。

要检查：

```text
遵循任务要求
格式约束
拒答 / Abstention
结构化输出
```

---

## 5. Procurement Domain
### 政府采购领域能力

包括：

```text
领域语言建模
术语理解
长文档理解
规则表达
风险识别
专业生成
```

这样才形成：

\[
\boxed{
DomainEval
+
RegressionEval
}
\]

---

# 七、Forgetting Score：怎样把“忘了多少”变成可测指标？

假设某项能力 CPT 前得分：

\[
S_{before}
\]

CPT 后得分：

\[
S_{after}
\]

可以定义一个简单的绝对回归量：

\[
Regression
=
S_{before}
-
S_{after}
\]

如果：

\[
Regression > 0
\]

说明能力下降。

也可以用相对回归：

\[
RelativeRegression
=
\frac{S_{before}-S_{after}}
{S_{before}}
\]

用于比较不同指标。

注意：

> 不同 Benchmark 的量纲不同。

所以真正工程中通常应该：

```text
按能力单独设阈值
而不是把所有分数直接相加
```

---

# 八、核心心智模型 ③：Forgetting 必须看 Curve，而不是只看最终 Checkpoint

如果只比较：

```text
CPT前

和

CPT最终
```

你会丢掉很多信息。

更专业的是：

# Forgetting Curve
## 遗忘曲线

例如每隔：

```text
5B tokens
```

做一次：

```text
Domain Eval
+
General Regression Eval
```

于是可以得到：

```text
0B
领域 60
通用 80

5B
领域 67
通用 79

10B
领域 72
通用 77

20B
领域 74
通用 71
```

你可能发现：

> 10B Token 以后，领域收益越来越小，但通用能力继续快速下降。

这就是非常重要的：

# Marginal Tradeoff
## 边际收益—损失关系

---

# 九、核心心智模型 ④：最佳 CPT Checkpoint 不一定是训练最久的那个

假设：

```text
Checkpoint A
领域 +6
通用 -1

Checkpoint B
领域 +10
通用 -3

Checkpoint C
领域 +11
通用 -10
```

如果只看领域能力，

你会选：

> C。

但从整体系统来看，

C 可能明显更差。

所以：

\[
\boxed{
BestDomainCheckpoint
\neq
BestReleaseCheckpoint
}
\]

真正发布时应该看：

> 多目标约束下的最优点。

---

# 十、为什么 Learning Rate 会影响遗忘？

Learning Rate：

# 学习率

决定参数每一步更新幅度。

概念上：

\[
\theta_{t+1}
=
\theta_t
-
\eta
\nabla_\theta \mathcal{L}
\]

其中：

\[
\eta
=
LearningRate
\]

如果学习率过大，

参数可能快速偏离原始能力区域。

所以：

\[
\boxed{
HigherLearningRate
\Rightarrow
PotentiallyFasterParameterDrift
}
\]

但要注意：

> 不是“学习率越小越安全”。

太小可能：

> CPT 几乎学不到东西。

真正问题仍然是：

\[
\boxed{
DomainGain
vs
Retention
}
\]

---

# 十一、Training Duration：训练越久为什么也可能遗忘越严重？

如果模型持续在一个窄领域分布上训练：

```text
1B tokens
5B tokens
20B tokens
50B tokens
```

领域 Loss 可能持续下降，

但参数也会越来越适应：

> 采购分布。

如果通用数据完全不出现，

模型原来的分布会逐渐被弱化。

所以：

\[
\boxed{
MoreCPT
\neq
AlwaysBetterCPT
}
\]

训练长度必须由：

```text
领域收益
通用回归
边际收益
预算
```

共同决定。

---

# 十二、Parameter Drift：参数变化大就一定遗忘严重吗？

可以定义参数变化：

\[
\Delta\theta
=
\theta_{CPT}
-
\theta_{Base}
\]

也可以看某种范数：

\[
\|\Delta\theta\|
\]

但必须注意：

\[
\boxed{
ParameterDrift
\neq
CapabilityRegression
}
\]

参数变化大：

> 不一定意味着能力一定坏。

参数变化小：

> 也不保证所有能力都安全。

所以 Parameter Drift 更适合作为：

> 诊断信号。

真正 Release 判断仍然依赖：

> 行为和能力评测。

---

# 十三、核心心智模型 ⑤：Weight Distance 是代理指标，Behavior Regression 才是最终证据

工程上可以监控：

```text
Weight Norm Change
权重变化

Layer-wise Drift
分层参数漂移

Embedding Drift
Embedding变化

Gradient Norm
梯度范数
```

但这些都属于：

# Proxy Metrics
## 代理指标

最终真正重要的是：

```text
模型还会不会做原来会做的事情？
```

所以：

\[
\boxed{
WeightMetric
<
CapabilityBenchmark
}
\]

这里的 `<` 表达的是：

> 在最终判断中的证据优先级更低。

---

# 十四、Plasticity–Stability Dilemma：CPT 的本质是“可塑性”和“稳定性”之间找平衡

这是持续学习领域非常经典的核心矛盾。

# Plasticity
## 可塑性

表示：

> 模型能否学会新的领域分布。

# Stability
## 稳定性

表示：

> 模型能否保留原来的能力。

如果太追求 Stability：

> 模型几乎不变，领域能力学不上去。

如果太追求 Plasticity：

> 模型学得很快，但旧能力掉得厉害。

所以：

\[
\boxed{
ContinualLearning
=
Plasticity
\leftrightarrow
Stability
}
\]

这就是 CPT 真正的优化问题。

---

# 十五、核心心智模型 ⑥：CPT 不是单目标优化，而是受约束的多目标优化

我们真正希望：

\[
DomainScore
\uparrow
\]

同时：

\[
GeneralRegression
\leq
Threshold
\]

并且：

\[
TrainingCost
\leq
Budget
\]

所以更专业地说：

\[
\boxed{
Maximize
\quad
DomainGain
}
\]

subject to：

\[
\boxed{
GeneralRegression
\leq
AllowedThreshold
}
\]

以及：

\[
\boxed{
Cost
\leq
Budget
}
\]

这比单纯说：

> “CPT Loss 越低越好”

要专业得多。

---

# 十六、Forgetting 可能发生在哪些层？

不应该只看最终 Benchmark。

还可以分层诊断：

```text
Language Modeling Regression
通用语言建模退化

Knowledge Regression
一般知识退化

Reasoning Regression
推理退化

Instruction Regression
指令遵循退化

Format Regression
结构化输出退化

Safety / Abstention Regression
拒答和不确定性行为退化
```

尤其如果后续还要重新 SFT，

就要区分：

> 是 Base Capability 丢失了，

还是：

> Instruction Alignment 丢失了。

这两类问题恢复策略可能不同。

---

# 十七、CPT 后重新 SFT 能不能“把遗忘救回来”？

有时：

> 可以恢复一部分行为。

例如 CPT 后：

```text
JSON输出变差
聊天格式变弱
```

重新做 SFT 可能改善。

但不能因此假设：

\[
\boxed{
SFT
可以修复所有Forgetting
}
\]

如果 CPT 已经导致：

```text
通用知识表示退化
数学能力退化
底层语言建模能力下降
```

少量 SFT 不一定能完全恢复。

所以：

\[
\boxed{
PostCPTSFT
\neq
UniversalRepair
}
\]

---

# 十八、Checkpoint Strategy：为什么 CPT 必须高频保存检查点？

因为最佳点可能出现在：

> 训练中途。

所以不能只保存：

```text
final_model
```

建议至少根据 Token Progress：

```text
Checkpoint_5B
Checkpoint_10B
Checkpoint_15B
Checkpoint_20B
```

然后每个 Checkpoint 都跑：

```text
Domain Validation

General Regression

Downstream Probe
```

这样才能找到：

# Pareto-efficient Checkpoint
## 多目标折中较优检查点

而不是：

> 默认最后一个就是最好。

---

# 十九、Early Stop：CPT 什么时候应该提前停止？

可以设置：

```text
DomainGainImprovement
边际领域收益

GeneralRegression
通用能力下降

LossPlateau
Loss进入平台期

BudgetLimit
预算上限
```

例如：

```text
如果连续两个Checkpoint：

领域收益 < 最小增益阈值

同时

通用回归 > 允许阈值
```

就进入：

# Early Stop
## 提前停止

所以：

\[
\boxed{
StopCPT
不能只看TrainingLoss
}
\]

---

# 二十、政府采购案例：怎样判断一次 CPT 是成功还是失败？

假设 Base Model：

```text
采购领域评分
62

通用语言
82

数学
76

代码
70

指令遵循
84
```

CPT 后：

```text
采购领域
76
↑14

通用语言
81
↓1

数学
75
↓1

代码
69
↓1

指令遵循
83
↓1
```

这是：

> 很可能可接受的方向。

但如果：

```text
采购领域
78
↑16

通用语言
72
↓10

数学
61
↓15

代码
55
↓15

指令遵循
70
↓14
```

就不能简单宣布：

> “CPT 成功，因为采购分数提升 16。”

因为：

\[
\boxed{
DomainGain
没有自动抵消
GeneralRegression
}
\]

---

# 二十一、Regression Benchmark：必须在 CPT 前冻结

如果 CPT 前后使用不同测试集，

就无法判断：

> 真的是模型变化，还是测试集变化。

所以需要：

# Regression Benchmark
## 能力回归测试集

在 CPT 开始前冻结：

```text
benchmark_version

task_list

metric_definition

evaluation_prompt

decoding_config

scoring_rule
```

这样每个 Checkpoint 都用：

> 同一套评测协议。

所以：

\[
\boxed{
ForgettingMeasurement
需要
StableBenchmark
}
\]

---

# 二十二、核心心智模型 ⑦：No Regression 也不等于 CPT 成功

假设：

```text
采购能力
不变

通用能力
不变
```

这说明：

> 没明显遗忘。

但也可能意味着：

> CPT 根本没学到东西。

所以：

\[
\boxed{
Retention
\neq
Improvement
}
\]

真正目标必须同时满足：

```text
DomainGain成立

GeneralRegression受控
```

所以：

\[
\boxed{
CPTSuccess
=
LearnNew
+
KeepOld
}
\]

---

# 二十三、完整 Forgetting Evaluation 流程

英文流程：

```text
Freeze Baseline
↓
Define Capability Suite
↓
Run Pre-CPT Evaluation
↓
Start CPT
↓
Periodic Checkpoint
↓
Domain Evaluation
↓
General Regression Evaluation
↓
Compute Forgetting Curves
↓
Compare Tradeoffs
↓
Early Stop / Continue
↓
Select Release Checkpoint
```

中文解释：

```text
冻结CPT前基线模型
↓
定义要保护的能力集合
↓
跑一次CPT前完整评测
↓
开始继续预训练
↓
定期保存Checkpoint
↓
测领域能力有没有提升
↓
测通用能力有没有下降
↓
形成遗忘曲线
↓
比较领域收益和能力回归
↓
决定继续还是提前停止
↓
选择真正适合发布的Checkpoint
```

这一条流程必须进入工程规范。

---

# 二十四、本阶段正式工程产物：`ProcurementCPTForgettingPolicy_V0.1`

第一版至少锁定：

```text
forgetting_policy_version

baseline_model_id

baseline_checkpoint

domain_eval_suite

general_regression_suite

instruction_regression_suite

structured_output_regression

reasoning_regression

code_regression

pre_cpt_scores

checkpoint_interval_tokens

checkpoint_eval_required
=
true

absolute_regression

relative_regression

allowed_regression_thresholds

domain_gain_threshold

early_stop_policy

release_checkpoint_policy

parameter_drift_monitoring

layerwise_drift_monitoring

forgetting_curve

evaluation_config_version

trace_logging
=
enabled
```

每个 Checkpoint 至少记录：

```text
checkpoint_id

tokens_seen

training_loss

domain_metrics

general_metrics

instruction_metrics

regression_delta

relative_regression

parameter_drift

continue_stop_decision

decision_reason
```

这样以后才能回答：

> **模型到底是在什么时候开始“越训越窄”的？**

---

# 二十五、本阶段最重要的 8 个核心心智模型

> **心智模型 ①：`SharedParameters ⇒ CapabilityInterference`。模型能力共享参数，学习新领域可能干扰旧能力。**

> **心智模型 ②：`DomainGain ≠ NetModelGain`。领域能力上涨只是收益的一面，原有能力回归必须同时计入。**

> **心智模型 ③：`Overfitting ≠ Forgetting`。前者是新任务泛化变差，后者是旧能力被新学习破坏。**

> **心智模型 ④：`BestDomainCheckpoint ≠ BestReleaseCheckpoint`。领域分数最高的模型，不一定是综合能力最适合发布的模型。**

> **心智模型 ⑤：`WeightDistance ≠ CapabilityRegression`。参数漂移只能做诊断，行为 Benchmark 才是最终证据。**

> **心智模型 ⑥：`Plasticity ↔ Stability`。CPT 的核心矛盾是既要学得进去，又要保得住原能力。**

> **心智模型 ⑦：`CPTSuccess = LearnNew + KeepOld`。不遗忘但没学会新领域，不算成功；领域变强但旧能力崩掉，也不算成功。**

> **心智模型 ⑧：`StopCPT ≠ WaitForLowestLoss`。停止训练必须依据领域收益、能力回归、边际收益和预算共同决定。**

---

# 二十六、把完整 Catastrophic Forgetting 流程压成一张专业工程图

```text
                    Base / Pre-CPT Model
                         CPT前基线模型
                               │
                               ▼
                      Baseline Evaluation
                  领域 + 通用 + 指令能力基线
                               │
                               ▼
                             CPT
                        领域继续预训练
                               │
                               ▼
                      Periodic Checkpoints
                       定期保存检查点
                               │
                 ┌─────────────┼─────────────┐
                 ▼             ▼             ▼
           Domain Eval    General Eval   Drift Metrics
            领域评测        通用回归       参数漂移
                 │             │             │
                 └─────────────┼─────────────┘
                               ▼
                       Forgetting Curve
                         形成遗忘曲线
                               │
                               ▼
                     Tradeoff Evaluation
                 比较领域收益与能力回归
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
                 Continue    Early Stop   Reject
                   继续        提前停止     否决
                    │          │          │
                    └──────────┼──────────┘
                               ▼
                    Release Checkpoint
                    选择最终发布检查点
```

脑中最后只留一句：

> **Catastrophic Forgetting 的本质不是“模型突然把知识全忘了”，而是持续在窄领域分布上更新共享参数以后，模型对新领域越来越适应，却可能逐渐偏离原有能力；因此 CPT 必须同时优化“学会新的”和“保住旧的”。**

---

# 第八课 · 第 6 阶段掌握测试

现在不回看正文，你应该能够解释：为什么共享参数会导致 Capability Interference；Catastrophic Forgetting 与 Overfitting 有什么区别；为什么 Domain Gain 和 General Retention 必须分开评测；CPT 应该监控哪些通用能力；Absolute Regression 和 Relative Regression 分别表达什么；为什么要看 Forgetting Curve 而不能只看最终模型；为什么最佳领域 Checkpoint 不等于最佳发布 Checkpoint；Learning Rate 和 Training Duration 为什么会影响遗忘；Parameter Drift 能说明什么、不能说明什么；什么是 Plasticity–Stability Dilemma；为什么 CPT 本质上是受约束的多目标优化；为什么 SFT 不能被当作万能遗忘修复器；为什么需要频繁保存 Checkpoint；Early Stop 应该依据什么；为什么 Regression Benchmark 必须在训练前冻结；以及为什么 `CPTSuccess = LearnNew + KeepOld`。

如果这些能够完整讲出来：

\[
\boxed{
第八课第6阶段真正掌握
}
\]

---

# 下一阶段：第八课 · 第 7 阶段
# Replay、Regularization 与能力保持：怎样防止 CPT 越训越窄？
## 已经知道模型为什么会遗忘，下一步就是把“能力保持”真正做成训练机制，而不是只在训练后发现问题。

下一阶段会正式进入：

```text
Replay
通用语料回放

Replay Ratio
回放比例

Interleaving
领域与通用数据交错训练

Regularization
正则化

Weight Anchoring
参数锚定

KL Constraint
分布约束

Teacher Reference
参考模型

Layer Freezing
层冻结

Selective Training
选择性训练

Capability Retention
能力保持

Retention Budget
能力回归预算
```

并建立：

# `ProcurementCPTRetentionPolicy_V0.1`

下一阶段最关键的一条边界会是：

\[
\boxed{
DetectForgetting
\neq
PreventForgetting
}
\]

也就是说：

> **第 6 阶段解决“怎么知道模型忘了”，第 7 阶段才真正解决“训练时怎样让它尽量别忘”。**

---

<!-- LESSON 08 STAGE 06 END -->


<!-- LESSON 08 STAGE 07 START -->

# 第八课 · 第 7 阶段
# Replay、Regularization 与能力保持：怎样防止 CPT 越训越窄？
## 已经知道模型为什么会遗忘，下一步就是把“能力保持”真正做成训练机制，而不是只在训练后发现问题。

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **DetectForgetting ≠ PreventForgetting。发现遗忘是诊断，能力保持是训练控制。**
2. **Retention ≠ FreezeEverything。能力保持不是不让模型变化，而是让变化发生在值得变化的地方。**
3. **Replay = OldDistributionReminder。回放的本质是让旧分布在训练过程中继续获得梯度支持。**
4. **Retention = Data Constraint + Objective Constraint + Parameter Constraint。能力保持可以从数据、目标函数和参数更新范围三个层面同时实现。**
5. **ReferenceModel ≠ GroundTruth。参考模型只是行为锚点，不是永远正确的老师。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Replay` | 回放：混入旧/通用数据以减少遗忘 |
| `CPT` | CPT/继续预训练：在领域语料上继续执行预训练目标 |
| `Retention` | 能力保持：领域增强时尽量保住原有通用能力 |
| `Regression` | 回归测试：更新后验证旧能力和关键切片没有退化 |
| `Batch` | 批次：一次参与计算的一组样本 |
| `Checkpoint` | 检查点：保存模型和训练状态以便恢复/发布 |

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

第 6 阶段我们解决的是：

\[
\boxed{
DetectForgetting
}
\]

也就是：

> 怎样知道模型什么时候开始遗忘、遗忘了什么、哪个 Checkpoint 已经不适合发布。

但这还不够。

真正成熟的 CPT 系统还必须进一步解决：

\[
\boxed{
PreventForgetting
}
\]

也就是：

> **训练过程中怎样主动限制能力退化，而不是等训练结束以后才发现模型已经被训窄了。**

所以本阶段正式进入：

# Capability Retention
## 能力保持

并最终形成：

# `ProcurementCPTRetentionPolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

发现遗忘和防止遗忘，是两件不同的事情。

\[
\boxed{
DetectForgetting
\neq
PreventForgetting
}
\]

第 6 阶段解决：

```text
模型忘了什么？
什么时候开始忘？
忘了多少？
```

第 7 阶段解决：

```text
训练时怎样降低遗忘？
怎样让新能力和旧能力共存？
怎样限制模型偏离原始分布？
```

所以：

\[
\boxed{
RetentionPolicy
=
TrainingTimeControl
}
\]

它不是训练后的补救。

而是：

> **训练过程中就要生效的约束机制。**

---

# 二、核心心智模型 ①：Retention 不是“别让模型变”，而是“让模型只在值得变的地方变”

一个常见误区是：

> 为了防止遗忘，就尽量少更新参数。

但如果模型几乎不更新：

> CPT 也学不到新领域。

所以真正目标不是：

\[
\boxed{
NoChange
}
\]

而是：

\[
\boxed{
UsefulChange
+
ControlledChange
}
\]

这意味着：

```text
需要领域能力增长
但避免无关能力大幅漂移
```

因此：

\[
\boxed{
Retention
\neq
FreezeEverything
}
\]

---

# 三、最直接的方法：Replay

# Replay
## 通用语料回放

Replay 的核心思想非常简单：

> 不要让模型在 CPT 期间只看采购领域。

而是继续给它一部分：

```text
高质量通用文本
数学
代码
百科知识
一般语言
通用指令风格
```

让原有能力持续得到梯度支持。

流程：

```text
Domain Batch
采购领域数据

+

Replay Batch
通用回放数据

↓

Mixed Training
混合训练

↓

Domain Gain
+
General Retention
```

所以：

\[
\boxed{
Replay
=
OldDistributionReminder
}
\]

可以把它理解成：

> 在模型学习新领域时，持续提醒它“旧世界仍然存在”。

---

# 四、Replay Ratio：回放比例到底怎么定？

假设训练总 Token Budget 是：

\[
B
\]

我们定义领域占比：

\[
p_d
\]

回放占比：

\[
p_r
\]

满足：

\[
p_d+p_r=1
\]

例如：

```text
Domain
80%

Replay
20%
```

但这个比例不能机械固定。

真正应该通过：

```text
Domain Gain
领域收益

General Regression
通用能力回归

Training Cost
训练成本
```

共同决定。

如果 Replay 太少：

> 遗忘可能明显。

如果 Replay 太多：

> 领域学习速度会变慢。

所以：

\[
\boxed{
ReplayRatio
=
PlasticityStabilityTradeoff
}
\]

---

# 五、核心心智模型 ②：Replay 不是“把旧数据重新训练一遍”，而是维持分布覆盖

Replay 不要求：

> 把原始预训练数据全部拿回来。

现实里也不可能。

更专业的目标是：

> 建立一个足够代表原有能力分布的 Replay Corpus。

例如：

```text
General Language
通用语言

Reasoning
推理

Math
数学

Code
代码

Instruction-like Text
指令风格文本
```

这些数据不需要巨大，

但要覆盖：

> 我们最不希望丢掉的能力。

所以：

\[
\boxed{
ReplayCorpus
\neq
OriginalPretrainingCorpus
}
\]

而更接近：

\[
\boxed{
RetentionRepresentativeCorpus
}
\]

即：

> 能力保持代表集。

---

# 六、Interleaving：领域数据和 Replay 怎样混？

# Interleaving
## 交错训练

一种常见做法：

```text
Domain Batch
↓
Replay Batch
↓
Domain Batch
↓
Domain Batch
↓
Replay Batch
```

另一种：

```text
同一个Batch中
混合Domain与Replay样本
```

核心目标都是：

> 避免长时间连续暴露在单一窄分布上。

所以：

\[
\boxed{
Interleaving
=
DistributionSmoothingOverTime
}
\]

中文可以理解为：

> 把训练时间轴上的数据分布“摊平”。

---

# 七、核心心智模型 ③：能力保持不只靠 Data，也可以靠 Objective Constraint

Replay 是：

> 数据层面的能力保持。

但还可以进一步做：

# Regularization
## 正则化约束

核心思想：

> 在优化领域 Loss 的同时，增加一个“不要偏离太远”的约束。

因此总 Loss 可以概念化为：

\[
\mathcal{L}_{total}
=
\mathcal{L}_{domain}
+
\lambda
\mathcal{L}_{retention}
\]

其中：

\[
\lambda
\]

表示：

> 保持约束的强度。

所以：

\[
\boxed{
Retention
可以来自
DataConstraint
+
ObjectiveConstraint
}
\]

---

# 八、Weight Anchoring：参数锚定

一种直觉化方法是：

> 不希望新模型的参数离原模型太远。

设 CPT 前参数：

\[
\theta_0
\]

训练中参数：

\[
\theta
\]

可以加入：

\[
\mathcal{L}_{anchor}
=
\|\theta-\theta_0\|^2
\]

总 Loss：

\[
\mathcal{L}_{total}
=
\mathcal{L}_{domain}
+
\lambda
\|\theta-\theta_0\|^2
\]

这叫：

# Weight Anchoring
## 参数锚定

直觉：

> 模型可以学，但别漂得太远。

但必须注意：

\[
\boxed{
ParameterCloseness
\neq
CapabilityCloseness
}
\]

所以 Weight Anchoring 只能作为：

> 辅助约束。

不能替代行为评测。

---

# 九、KL Constraint：约束输出分布不要偏离参考模型太远

除了约束参数，

还可以约束：

> 模型输出分布。

假设原模型：

\[
p_{ref}(x)
\]

CPT 模型：

\[
p_{\theta}(x)
\]

可以在 Replay / Anchor 数据上加入：

# KL Divergence
## KL 散度约束

概念上：

\[
\mathcal{L}_{KL}
=
D_{KL}
(
p_{ref}
\|
p_{\theta}
)
\]

总目标：

\[
\mathcal{L}_{total}
=
\mathcal{L}_{domain}
+
\beta\mathcal{L}_{KL}
\]

直觉上：

> 在一些我们希望保持稳定的输入上，新模型输出分布不要和旧模型差得太离谱。

---

# 十、核心心智模型 ④：Reference Model 是“行为锚点”，不是永远正确的老师

使用 KL Constraint 时通常需要：

# Reference Model
## 参考模型

它可以是：

```text
CPT前Base Model
或
CPT前Domain/SFT Model
```

但必须注意：

\[
\boxed{
ReferenceModel
\neq
GroundTruth
}
\]

它不是：

> 永远正确的 Teacher。

它只是：

> 我们希望保留某些行为的参考点。

如果 Reference Model 本身有问题，

过强约束反而会阻止新模型改进。

所以：

\[
\boxed{
Reference
是Anchor
不是Oracle
}
\]

---

# 十一、Layer Freezing：能不能直接冻结一部分层？

可以。

# Layer Freezing
## 层冻结

例如：

```text
冻结Embedding

冻结底部若干Transformer层

只训练顶部若干层
```

直觉：

> 保护底层通用表示，减少整体参数漂移。

但问题是：

> 领域能力可能也需要修改底层表示。

所以：

\[
\boxed{
FreezeMore
\Rightarrow
RetentionPotential\uparrow
}
\]

但可能：

\[
\boxed{
Plasticity\downarrow
}
\]

因此 Layer Freezing 不是：

> “越多越安全”。

而是：

> 稳定性和可塑性的再一次折中。

---

# 十二、Selective Training：只训练部分参数

除了 Layer Freezing，

还可以选择：

# Selective Training
## 选择性训练

例如：

```text
只训练LoRA Adapter

只训练Attention Projection

只训练MLP部分

只训练新增Embedding

只训练特定Layer
```

这样可以降低：

> 全模型参数漂移。

但同时也会限制：

> CPT 的表达能力。

所以：

\[
\boxed{
FewerTrainableParameters
\neq
AlwaysBetterRetention
}
\]

它只是：

> 降低干扰的一种手段。

---

# 十三、LoRA CPT 能不能天然避免遗忘？

不能。

这是非常重要的一条。

LoRA 的确只更新少量参数。

但只要最终推理时：

```text
Base
+
LoRA Adapter
```

整体输出行为就可能发生明显变化。

所以：

\[
\boxed{
ParameterEfficient
\neq
ForgettingFree
}
\]

LoRA 只能说明：

> 更新的参数数量更少。

不能说明：

> 原能力一定不会退化。

最终仍然要跑：

> Regression Benchmark。

---

# 十四、核心心智模型 ⑤：减少参数更新范围，不等于消除行为漂移

这条必须锁死。

\[
\boxed{
SmallParameterDelta
\neq
SmallBehaviorDelta
}
\]

尤其在 Transformer 中，

少量关键参数变化也可能引起：

> 大范围输出变化。

所以：

```text
LoRA
Layer Freezing
Selective Training
```

都是：

> Retention Mechanism。

但不是：

> Retention Guarantee。

---

# 十五、Retention Budget：能力保持必须有明确“预算”

不要只写：

> “尽量不要退化。”

而应该定义：

# Retention Budget
## 能力回归预算

例如：

```text
General Language
最大允许下降 1.5%

Math
最大允许下降 2%

Code
最大允许下降 2%

Instruction Following
最大允许下降 1%

Structured Output
不得显著下降
```

注意：

> 这些具体阈值不是通用标准。

必须由：

```text
业务风险
Benchmark稳定性
模型用途
人工成本
可接受回归范围
```

决定。

所以：

\[
\boxed{
RetentionPolicy
必须MachineCheckable
}
\]

而不是一句：

> “保持通用能力。”

---

# 十六、核心心智模型 ⑥：没有 Retention Budget，就没有真正的“能力保持”

因为如果没有阈值，

训练结束以后：

```text
数学下降3%
```

团队很难回答：

> 这是可以接受，还是必须回滚？

所以：

\[
\boxed{
NoThreshold
=
NoDecisionRule
}
\]

真正工程化应该写成：

```text
if regression <= threshold:
    pass
else:
    reject_or_rebalance
```

也就是：

> 评测结果必须能驱动决策。

---

# 十七、Dynamic Retention：Retention 强度可以动态调整

假设 CPT 初期：

```text
领域能力提升慢
通用能力稳定
```

可以：

> 降低约束强度，提高可塑性。

但如果中期出现：

```text
领域继续小幅增长
通用能力快速下降
```

可以：

```text
提高Replay比例
增加KL约束
降低Learning Rate
冻结更多层
或提前停止
```

所以：

# Dynamic Retention Control
## 动态能力保持控制

本质上是在：

> 根据 Forgetting Curve 调训练控制参数。

---

# 十八、完整能力保持流程

英文流程：

```text
Freeze Baseline
↓
Define Retention Suite
↓
Set Retention Budget
↓
Build Replay Corpus
↓
Choose Retention Mechanisms
↓
Start CPT
↓
Periodic Regression Eval
↓
Measure Forgetting
↓
Adjust Replay / Regularization / LR
↓
Continue / Stop / Rollback
↓
Release Checkpoint
```

中文解释：

```text
冻结CPT前基线
↓
定义需要保护的能力集合
↓
为每项能力设回归预算
↓
建立通用回放语料
↓
选择Replay / KL / Freeze等保持机制
↓
启动CPT
↓
定期跑通用能力回归
↓
计算遗忘程度
↓
必要时调整回放比例、正则强度或学习率
↓
决定继续、停止或回滚
↓
选择最终发布Checkpoint
```

这才是：

> **真正闭环的能力保持系统。**

---

# 十九、Replay 和 Regularization 应该怎么组合？

可以把策略分成三类。

## A. Data-level Retention
### 数据层能力保持

```text
General Replay
通用语料回放

Balanced Mixture
平衡数据混合

Interleaving
交错训练
```

---

## B. Objective-level Retention
### 目标函数层能力保持

```text
Weight Anchoring
参数锚定

KL Constraint
输出分布约束
```

---

## C. Parameter-level Retention
### 参数层能力保持

```text
Layer Freezing
层冻结

Selective Training
选择性训练

LoRA / Adapter
参数高效更新
```

三者可以组合。

所以：

\[
\boxed{
RetentionSystem
=
Data
+
Objective
+
Parameter
}
\]

---

# 二十、核心心智模型 ⑦：Retention Mechanism 不是越多越好

如果同时：

```text
Replay 40%

强KL

强Weight Anchor

冻结一半Layer

Learning Rate很低
```

结果可能是：

> 模型几乎不再学习采购领域。

所以：

\[
\boxed{
MoreProtection
\neq
BetterCPT
}
\]

能力保持不是：

> 把模型绑死。

而是：

> 找到刚好足够的约束强度。

这又回到：

\[
\boxed{
Plasticity
\leftrightarrow
Stability
}
\]

---

# 二十一、Retention Ablation：必须知道到底哪种机制在起作用

假设我们有四组实验：

```text
Run A
No Retention

Run B
Replay Only

Run C
Replay + KL

Run D
Replay + KL + Layer Freeze
```

其他条件保持一致：

```text
Same Base
Same Corpus
Same Token Budget
Same Mixture
Same Learning Rate
```

然后比较：

```text
Domain Gain

General Regression

Training Cost

Convergence Speed
```

这样才能知道：

> 真正有效的是哪种机制。

所以：

\[
\boxed{
RetentionPolicy
必须可Ablate
}
\]

---

# 二十二、Release Gate：Retention 最终必须进入发布门槛

训练结束后，

不能只判断：

```text
领域指标上涨
→ 发布
```

而应该：

```text
Domain Gain
达到最低收益

AND

General Regression
不超过阈值

AND

Instruction Regression
不超过阈值

AND

No Critical Capability Failure
没有关键能力崩溃
```

只有全部通过：

\[
\boxed{
ReleaseGate=True
}
\]

才允许进入下一阶段。

---

# 二十三、核心心智模型 ⑧：Retention 不是单独模块，而是 Release Policy 的一部分

如果 Retention 只存在于：

> 训练脚本里，

而没有进入：

> 发布决策，

那它就没有真正工程化。

所以：

\[
\boxed{
Retention
必须进入
ReleaseGate
}
\]

也就是说：

> 能力保持是发布条件，不是训练建议。

---

# 二十四、本阶段正式工程产物：`ProcurementCPTRetentionPolicy_V0.1`

第一版至少锁定：

```text
retention_policy_version

baseline_model_id

retention_capability_suite

retention_budget

replay_enabled

replay_corpus_version

replay_ratio

interleaving_policy

weight_anchor_enabled

weight_anchor_lambda

kl_constraint_enabled

kl_beta

reference_model_id

layer_freezing_policy

trainable_parameter_scope

lora_or_adapter_policy

learning_rate_policy

dynamic_retention_enabled

adjustment_triggers

regression_eval_interval

forgetting_curve_required

retention_ablation_plan

release_gate

rollback_policy

trace_logging
=
enabled
```

每个训练 Run 至少记录：

```text
run_id

checkpoint_id

replay_ratio

retention_loss_weight

kl_beta

trainable_parameters

frozen_layers

learning_rate

domain_metrics

general_metrics

regression_delta

retention_budget_status

adjustment_action

release_decision
```

这样以后才能回答：

> **模型为什么既学会了采购，又没有明显忘掉原来的能力？**

---

# 二十五、本阶段最重要的 8 个核心心智模型

> **心智模型 ①：`DetectForgetting ≠ PreventForgetting`。发现遗忘是诊断，能力保持是训练控制。**

> **心智模型 ②：`Retention ≠ FreezeEverything`。能力保持不是不让模型变化，而是让变化发生在值得变化的地方。**

> **心智模型 ③：`Replay = OldDistributionReminder`。回放的本质是让旧分布在训练过程中继续获得梯度支持。**

> **心智模型 ④：`Retention = Data Constraint + Objective Constraint + Parameter Constraint`。能力保持可以从数据、目标函数和参数更新范围三个层面同时实现。**

> **心智模型 ⑤：`ReferenceModel ≠ GroundTruth`。参考模型只是行为锚点，不是永远正确的老师。**

> **心智模型 ⑥：`SmallParameterDelta ≠ SmallBehaviorDelta`。少量参数更新仍然可能带来明显行为变化。**

> **心智模型 ⑦：`RetentionBudget = DecisionRule`。没有可量化的回归阈值，就没有真正可执行的能力保持策略。**

> **心智模型 ⑧：`MoreProtection ≠ BetterCPT`。约束过强会让模型学不进去，Retention 仍然必须平衡 Plasticity 与 Stability。**

---

# 二十六、把完整 Retention 流程压成一张专业工程图

```text
                    Pre-CPT Baseline
                       CPT前基线
                            │
                            ▼
                    Retention Suite
                  定义要保护的能力
                            │
                            ▼
                    Retention Budget
                  为每项能力设回归阈值
                            │
                            ▼
                  Retention Mechanisms
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
          Replay       Regularization   Parameter Scope
         通用回放        正则化约束        参数更新范围
            │               │               │
            └───────────────┼───────────────┘
                            ▼
                          CPT
                        继续预训练
                            │
                            ▼
                 Periodic Regression Eval
                   定期通用能力回归
                            │
                            ▼
                      Forgetting Curve
                       形成遗忘曲线
                            │
                            ▼
                  Dynamic Retention Control
             调整Replay / KL / LR / Freeze
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
          Continue        Early Stop      Rollback
            继续            提前停止        回滚
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                      Release Gate
                   通过能力保持发布门
                            │
                            ▼
                    Release Checkpoint
```

脑中最后只留一句：

> **能力保持的真正目标不是让 CPT 模型“尽量像原模型”，而是在明确回归预算下，让模型获得足够的领域可塑性，同时通过 Replay、正则化和参数约束把旧能力的损失控制在可接受范围内。**

---

# 第八课 · 第 7 阶段掌握测试

现在不回看正文，你应该能够解释：为什么 Detect Forgetting 和 Prevent Forgetting 是两件事；Replay 的本质是什么；Replay Ratio 为什么不能固定照抄；Replay Corpus 为什么不需要等于原始预训练语料；Interleaving 在训练时间轴上解决什么问题；Regularization 为什么属于 Objective-level Retention；Weight Anchoring 如何工作；KL Constraint 为什么需要 Reference Model；为什么 Reference Model 不等于 Ground Truth；Layer Freezing 和 Selective Training 分别解决什么问题；为什么 LoRA 不能自动避免遗忘；为什么 `SmallParameterDelta ≠ SmallBehaviorDelta`；Retention Budget 为什么必须机器可检查；Dynamic Retention 怎样根据 Forgetting Curve 调整；Data-level、Objective-level、Parameter-level Retention 如何组合；为什么 More Protection 不一定更好；Retention Ablation 为什么重要；以及为什么能力保持最终必须进入 Release Gate。

如果这些能够完整讲出来：

\[
\boxed{
第八课第7阶段真正掌握
}
\]

---

# 下一阶段：第八课 · 第 8 阶段
# Synthetic Data & Curriculum：合成领域语料、难度分层与覆盖扩展
## 当真实政府采购语料覆盖不足时，合成数据能不能补？为什么“让 LLM 多生成一些采购文本”可能反而把模型训练得更假？

下一阶段会正式进入：

```text
Synthetic Data
合成数据

Teacher Generation
教师模型生成

Data Augmentation
数据增强

Coverage Expansion
覆盖扩展

Hard Case Generation
难例生成

Curriculum Learning
课程式训练

Difficulty Scheduling
难度调度

Quality Filtering
质量过滤

Synthetic Contamination
合成污染

Model Collapse Risk
模型坍缩风险

Human Validation
人工验证
```

并建立：

# `ProcurementCPTSyntheticCurriculumPolicy_V0.1`

下一阶段最关键的一条边界会是：

\[
\boxed{
SyntheticData
\neq
FreeNewKnowledge
}
\]

也就是说：

> **合成数据可以重组、放大和补覆盖，但它不能凭空创造可靠的新事实世界。**

---

<!-- LESSON 08 STAGE 07 END -->


<!-- LESSON 08 STAGE 08 START -->

# 第八课 · 第 8 阶段
# Synthetic Data & Curriculum：合成领域语料、难度分层与覆盖扩展
## 当真实政府采购语料覆盖不足时，合成数据能不能补？为什么“让 LLM 多生成一些采购文本”可能反而把模型训练得更假？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **SyntheticData ≠ FreeNewKnowledge。合成数据能扩展表达和组合覆盖，但不能凭空创造可靠事实。**
2. **SyntheticGeneration 必须由 CoverageGap 驱动。先发现真实语料缺口，再生成，不做无目标数据膨胀。**
3. **SurfaceDiversity ≠ DistributionDiversity。句子看起来不同，不代表训练分布真的扩展。**
4. **Generated ≠ TrainingEligible。合成数据必须经过验证、去重、证据检查和风险审核才能进入训练。**
5. **TeacherModel ≠ GroundTruth。教师模型是候选数据生成器，不是事实权威。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Curriculum` | 课程式训练：按难度、类型或阶段安排训练数据顺序 |
| `Synthetic Data` | 合成数据：由规则/模型生成、需质量控制的训练数据 |
| `CPT` | CPT/继续预训练：在领域语料上继续执行预训练目标 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Validation` | 验证集：开发阶段用于选模型、调参数和早停 |

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

到第 7 阶段，我们已经建立：

\[
\boxed{
Corpus
+
Tokenizer
+
Sequence
+
Mixture
+
ForgettingControl
+
Retention
}
\]

但真实项目里很快会遇到一个问题：

> **高质量真实采购语料并不总是覆盖我们希望模型掌握的全部分布。**

例如某些类型可能非常稀缺：

```text
罕见风险条款
复杂跨章节条件
特殊行业采购
极端金额场景
高难合同条款
少见文号格式
特殊异常案例
```

这时很多团队会想到：

> “那就让一个更强的 LLM 生成更多数据。”

这件事可以做。

但如果没有严格边界，也可能制造：

```text
虚构事实
语言风格趋同
教师模型偏差复制
重复模式放大
模型自己训练自己
真实分布被稀释
```

所以本阶段正式进入：

# Synthetic Data
## 合成数据

以及：

# Curriculum Learning
## 课程式训练

本阶段最终形成：

# `ProcurementCPTSyntheticCurriculumPolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

合成数据不是：

> **“免费的新知识”。**

更准确地说：

\[
\boxed{
SyntheticData
=
ControlledDistributionExpansion
}
\]

也就是：

> **在已有知识、规则和真实样本边界内，主动扩展训练分布。**

所以最重要的一条边界：

\[
\boxed{
SyntheticData
\neq
FreeNewKnowledge
}
\]

它可以：

```text
改写
组合
扩展
补难例
补格式
补覆盖
```

但不能自动保证：

```text
事实真实
规则最新
业务合理
法律结论正确
```

---

# 二、核心心智模型 ①：Synthetic Data 首先是“分布工程”，不是“内容生成”

如果只是说：

> “生成 100 万条采购文本。”

这个目标几乎没有工程意义。

真正应该先问：

```text
当前真实Corpus缺什么？

缺行业？
缺风险类型？
缺长文档？
缺极端金额？
缺稀有表达？
缺困难负样本？
```

然后才决定：

> 用 Synthetic Data 补哪一块。

所以：

\[
\boxed{
SyntheticGeneration
必须由
CoverageGap
驱动
}
\]

而不是：

> “因为可以生成，所以生成。”

---

# 三、Coverage Gap：先做缺口分析，再生成

完整流程：

```text
Real Corpus
真实语料
↓
Coverage Analysis
覆盖分析
↓
Gap Detection
发现缺口
↓
Synthetic Target Definition
定义需要补的分布
↓
Generation
生成
↓
Validation
验证
↓
Mixture Control
控制混合比例
↓
CPT
进入继续预训练
```

中文解释：

> 先看真实数据缺什么，再精确生成什么，而不是先生成再找用途。

因此：

\[
\boxed{
SyntheticData
=
GapFillingTool
}
\]

---

# 四、Synthetic Data 可以分成哪几类？

第一类：

# Paraphrase Augmentation
## 改写增强

例如把：

```text
供应商须在本地设立固定服务机构
```

改写成多种表达：

```text
要求供应商具备本地服务网点

供应商应在项目所在地设置常驻服务机构

投标人须提供当地服务场所证明
```

作用：

> 扩展语言表达变体。

---

第二类：

# Template Variation
## 模板变体生成

在不改变核心结构的情况下变化：

```text
项目名称
金额
行业
地点
时间
服务范围
```

作用：

> 增加结构分布多样性。

---

第三类：

# Hard Case Generation
## 难例生成

故意生成：

```text
边界条件
相互矛盾条款
隐含限制条件
跨章节依赖
容易误判的负样本
```

作用：

> 增强模型对复杂模式的学习机会。

---

第四类：

# Counterfactual Generation
## 反事实生成

例如从一个风险条款出发：

```text
要求供应商必须在本市注册
```

生成更合理版本：

```text
供应商应根据项目实际需要提供本地化服务能力，但不限制注册地
```

或者反过来：

> 从合理条款生成一个边界风险版本。

作用：

> 学习相似表达之间的细微差异。

---

第五类：

# Structure Synthesis
## 结构合成

生成：

```text
完整采购需求章节
评分表
合同条款组合
长文档章节衔接
```

作用：

> 补足长结构训练分布。

---

# 五、核心心智模型 ②：Synthetic Diversity 不等于 Real-world Diversity

LLM 很容易生成：

> 看起来很多样的文本。

但底层可能仍然高度同质。

例如生成 10 万条：

```text
不同项目名
不同金额
不同地点
```

表面差异很大。

但句式可能几乎都一样：

```text
供应商应……
投标人须……
采购人要求……
```

所以：

\[
\boxed{
SurfaceDiversity
\neq
DistributionDiversity
}
\]

真正应该看：

```text
语法结构
业务逻辑
行业分布
长度分布
难度分布
错误类型
推理路径
文档结构
```

是否真的扩展。

---

# 六、Teacher Generation：教师模型生成到底是什么？

可以用更强模型作为：

# Teacher Model
## 教师模型

生成合成数据。

流程：

```text
Seed Data
真实种子样本
↓
Teacher Prompt
教师生成指令
↓
Teacher Model
高能力模型
↓
Synthetic Candidates
候选合成数据
↓
Rule / Model Filter
规则和模型过滤
↓
Human Audit
人工抽检
↓
Approved Synthetic Set
通过审核的数据集
```

注意：

\[
\boxed{
TeacherOutput
\neq
GroundTruth
}
\]

教师模型同样会：

```text
幻觉
编造
过度规范化
重复自己的风格
复制训练偏差
```

所以 Teacher 只是：

> 候选数据生成器。

不是：

> 事实权威。

---

# 七、核心心智模型 ③：Synthetic Pipeline 必须有 Validator，不能“生成即训练”

这是非常重要的工程边界。

错误流程：

```text
LLM Generate
↓
直接进CPT
```

正确流程：

```text
Generate
生成候选
↓
Schema Check
结构检查
↓
Rule Validation
规则验证
↓
Dedup
去重
↓
Consistency Check
一致性检查
↓
Source / Evidence Check
来源或证据核验
↓
Human Sampling Audit
人工抽样审核
↓
Training Eligible
获得训练资格
```

所以：

\[
\boxed{
Generated
\neq
TrainingEligible
}
\]

这和第 2 阶段的：

\[
AvailableData
\neq
TrainingEligibleData
\]

是一脉相承的。

---

# 八、事实型 Synthetic Data 为什么特别危险？

如果让模型直接生成：

```text
某政策具体规定
某法规具体条款
某项目真实事实
```

很容易出现：

> 看起来非常专业，但实际上不存在。

所以事实型合成数据应该优先采用：

```text
Grounded Generation
基于真实来源生成

Retrieval-grounded Synthesis
基于检索证据合成

Rule-conditioned Generation
基于明确规则约束生成
```

而不是：

> 让模型自由发挥。

所以：

\[
\boxed{
FactSynthesis
必须有
ExternalGrounding
}
\]

---

# 九、Synthetic Data 的来源血缘必须单独记录

每条合成数据至少要知道：

```text
synthetic_id

teacher_model

teacher_version

prompt_version

seed_document_id

source_evidence

generation_temperature

generation_timestamp

validation_status

human_review_status
```

因为合成数据也是：

# Derived Data
## 派生数据

必须能够追溯：

> 它从哪里来、谁生成、基于什么、是否验证。

所以：

\[
\boxed{
SyntheticData
必须有Lineage
}
\]

---

# 十、核心心智模型 ④：Synthetic Data 可以扩展“组合空间”，但不能自动扩展“事实世界”

这条非常关键。

假设真实数据中已有：

```text
行业A
金额区间B
风险类型C
文档结构D
```

合成数据可以把这些元素重新组合：

```text
A + B + C
A + D
B + C + D
```

从而扩大：

> 组合覆盖。

但如果真实世界里根本没有某个规则事实，

模型不能凭空可靠创造。

所以：

\[
\boxed{
SyntheticData
擅长
CombinatorialExpansion
}
\]

不擅长：

\[
\boxed{
AuthoritativeFactCreation
}
\]

---

# 十一、Model Collapse Risk：为什么模型训练太多合成数据会越来越“像模型”？

如果模型大量训练在：

> 其他模型生成的数据上，

而真实数据比例越来越低，

可能出现：

# Model Collapse
## 模型坍缩风险

直觉上：

> 模型开始不断学习模型自己偏好的表达和分布。

结果可能是：

```text
语言更规整
真实噪声减少
罕见表达消失
边缘模式丢失
风格趋同
```

所以：

\[
\boxed{
SyntheticDominance
可能导致
DistributionNarrowing
}
\]

这和我们的目标：

> 扩展覆盖

恰好相反。

---

# 十二、核心心智模型 ⑤：Synthetic Data 比例应该受上限约束

不能因为合成数据便宜，

就让它无限增长。

Data Mixture 中应该单独记录：

```text
real_token_share

synthetic_token_share

synthetic_by_type

synthetic_by_teacher

synthetic_by_quality
```

并设置：

# Synthetic Share Cap
## 合成数据占比上限

具体上限：

> 没有统一标准答案。

必须通过：

```text
真实验证集
领域Benchmark
通用回归
分布分析
Ablation
```

共同确定。

所以：

\[
\boxed{
CheapData
\neq
UnlimitedData
}
\]

---

# 十三、Curriculum Learning：为什么训练顺序本身也会影响学习？

现在进入第二个主题：

# Curriculum Learning
## 课程式学习

它不是：

> 把数据混在一起随机训练。

而是：

> **按照难度、结构或目标阶段安排训练顺序。**

例如：

```text
Phase 1
高质量、短、清晰文本

Phase 2
标准采购文件

Phase 3
长文档、多章节

Phase 4
复杂行业专项

Phase 5
高难、边界、反事实样本
```

这类似：

> 人类先学基础，再学复杂问题。

---

# 十四、核心心智模型 ⑥：Mixture 决定“每阶段吃什么”，Curriculum 决定“什么时候吃什么”

第 5 阶段已经讲过：

# Mixture
## 数据混合

关注：

\[
\boxed{
WithinStageDistribution
}
\]

即：

> 同一训练阶段不同数据各占多少。

而 Curriculum 关注：

\[
\boxed{
AcrossStageSchedule
}
\]

即：

> 不同训练阶段的数据难度和分布怎样变化。

所以：

\[
\boxed{
Mixture
\neq
Curriculum
}
\]

---

# 十五、Curriculum 的“难度”到底怎么定义？

难度不能只看：

> 文档长不长。

还可以从多个维度定义：

```text
Length Difficulty
长度难度

Structural Difficulty
结构复杂度

Semantic Difficulty
语义难度

Reasoning Difficulty
推理难度

Domain Rarity
领域稀有度

Noise Level
噪声程度

Cross-section Dependency
跨章节依赖
```

例如：

```text
简单：
单一条款、短文本、明确语义

中等：
多条件条款、行业术语

困难：
跨章节、隐含约束、矛盾信息、边界情形
```

因此：

\[
\boxed{
Difficulty
=
MultiDimensional
}
\]

---

# 十六、Progressive Curriculum：从简单到复杂

一种常见策略：

# Progressive Curriculum
## 递进式课程

```text
Stage A
基础领域语言

Stage B
标准文档结构

Stage C
长文档和跨章节

Stage D
行业专项

Stage E
难例与边界案例
```

优势：

> 让模型先稳定建立领域分布，再逐步接触复杂结构。

但也不能机械认为：

\[
EasyToHard
=
AlwaysBest
\]

有些模型可能已经具备足够通用能力，

过多简单数据反而浪费训练预算。

---

# 十七、Anti-Curriculum / Mixed Difficulty：为什么有时需要混合难度？

如果训练长期只从简单到难，

模型可能：

> 在进入高难阶段时忘掉简单分布。

所以一种策略是：

```text
高难数据逐步增加

但始终保留部分基础数据
```

这可以理解成：

# Mixed Curriculum
## 混合式课程

即：

> 难度逐步提升，但基础分布不完全退出。

所以：

\[
\boxed{
Curriculum
也需要Retention
}
\]

---

# 十八、核心心智模型 ⑦：Curriculum 是训练分布随时间变化的 Policy

可以把第 \(t\) 个训练阶段的数据分布写成：

\[
P_t(D)
\]

Curriculum 本质上是：

\[
\boxed{
P_1(D)
\rightarrow
P_2(D)
\rightarrow
...
\rightarrow
P_T(D)
}
\]

也就是：

> 训练分布随时间有计划地变化。

所以它必须版本化：

```text
curriculum_phase

phase_start_tokens

phase_end_tokens

difficulty_mix

synthetic_share

replay_share

transition_rule
```

而不是：

> “前面简单一点，后面难一点。”

---

# 十九、Synthetic Hard Case：难例生成为什么特别有价值？

真实世界中的真正难例通常：

```text
少
贵
标注慢
覆盖不均
```

这时合成数据很适合：

# Hard Case Expansion
## 难例扩展

例如围绕真实风险条款生成：

```text
近似但无风险的负例

轻微改动后有风险的正例

多条件组合

语义相似但法律效果不同

跨章节冲突
```

这种合成方式比：

> 纯自由生成采购文本

更有价值。

因为目标清晰：

\[
\boxed{
ExpandDecisionBoundary
}
\]

即：

> 扩展模型在决策边界附近的训练密度。

---

# 二十、核心心智模型 ⑧：Synthetic Hard Case 的价值在“边界密度”，不是“数量”

如果随机生成 100 万条很简单的采购文本，

可能不如：

> 1 万条高质量边界难例。

所以：

\[
\boxed{
HardCaseValue
\propto
BoundaryInformation
}
\]

而不是：

\[
\boxed{
RawCount
}
\]

这和机器学习里：

> 决策边界附近样本信息量更高

是一致的。

---

# 二十一、Synthetic Data 也必须做 Dedup

LLM 非常容易生成：

> 高度相似文本。

即使表面词汇变化，

结构可能几乎一样。

所以仍然要做：

```text
Exact Dedup
完全重复去重

Near Dedup
近似重复去重

Semantic Cluster
语义聚类

Template Similarity
模板相似度分析
```

否则：

> 合成数据会制造新的“假大数据”。

所以：

\[
\boxed{
SyntheticGeneration
后面仍然需要
Deduplication
}
\]

---

# 二十二、Synthetic Benchmark Leakage：合成数据也会污染测试集

如果 Teacher 生成时：

```text
直接看到Benchmark题目
```

然后生成很多改写版本，

这些数据进入 CPT，

依然属于：

> Benchmark Contamination。

所以 Synthetic Pipeline 同样必须经过：

```text
Benchmark Registry

Exact Match

Near Match

Semantic Similarity

Same Seed Check

Lineage Check
```

所以：

\[
\boxed{
Synthetic
\neq
LeakageSafe
}
\]

---

# 二十三、Human Validation：什么情况下必须人工复核？

并不是每条都要人工审核。

但这些类型应该优先提高人工审核比例：

```text
事实型合成

法规解释

高风险判断

复杂反事实

跨章节难例

Teacher之间冲突样本

高曝光合成桶
```

可以采用：

```text
Risk-based Human Sampling
基于风险的人工抽样
```

即：

> 风险越高、训练权重越大，人工审核越严格。

---

# 二十四、Synthetic Quality Score：可以怎样做质量分层？

可以概念化成：

\[
Q_{syn}
=
f(
Validity,
Grounding,
Diversity,
Difficulty,
Consistency
)
\]

其中：

```text
Validity
格式和规则有效性

Grounding
是否有真实依据

Diversity
是否提供新分布

Difficulty
是否真有难度

Consistency
内部逻辑是否一致
```

再分成：

```text
Gold-like Synthetic
高质量合成

Standard Synthetic
标准合成

Low-confidence Synthetic
低置信合成
```

不同等级使用不同：

> Sampling Weight。

---

# 二十五、Synthetic Data 和 SFT Synthetic Data 有什么区别？

这点必须分清。

CPT Synthetic Data 主要目标是：

> 扩展领域语言和分布。

所以更像：

```text
文档
条款
章节
行业语料
长文本
```

而 SFT Synthetic Data 主要目标是：

> 教模型任务行为。

更像：

```text
Instruction
Response
JSON输出
理由
拒答
工具选择
```

所以：

\[
\boxed{
SyntheticCPTData
\neq
SyntheticSFTData
}
\]

二者数据结构和目标完全不同。

---

# 二十六、本阶段正式工程产物：`ProcurementCPTSyntheticCurriculumPolicy_V0.1`

第一版至少锁定：

```text
synthetic_policy_version

coverage_gap_definition

synthetic_use_cases

teacher_model

teacher_version

prompt_version

seed_data_policy

source_grounding_required

generation_temperature

generation_count

synthetic_type

hard_case_policy

counterfactual_policy

synthetic_dedup_policy

synthetic_quality_score

human_review_policy

benchmark_firewall

synthetic_share_cap

real_synthetic_mix

curriculum_enabled

curriculum_phases

difficulty_definition

phase_transition_rule

replay_share_by_phase

synthetic_share_by_phase

ablation_plan

release_gate

trace_logging
=
enabled
```

每条 Synthetic Sample 至少记录：

```text
synthetic_id

teacher_model

teacher_version

prompt_version

seed_id

source_evidence

synthetic_type

difficulty_level

quality_score

validation_status

human_review_status

benchmark_blocked

training_eligible
```

---

# 二十七、本阶段最重要的 8 个核心心智模型

> **心智模型 ①：`SyntheticData ≠ FreeNewKnowledge`。合成数据能扩展表达和组合覆盖，但不能凭空创造可靠事实。**

> **心智模型 ②：`SyntheticGeneration 必须由 CoverageGap 驱动`。先发现真实语料缺口，再生成，不做无目标数据膨胀。**

> **心智模型 ③：`SurfaceDiversity ≠ DistributionDiversity`。句子看起来不同，不代表训练分布真的扩展。**

> **心智模型 ④：`Generated ≠ TrainingEligible`。合成数据必须经过验证、去重、证据检查和风险审核才能进入训练。**

> **心智模型 ⑤：`TeacherModel ≠ GroundTruth`。教师模型是候选数据生成器，不是事实权威。**

> **心智模型 ⑥：`SyntheticShare 必须受控`。合成数据过多会稀释真实世界分布，并增加 Model Collapse 风险。**

> **心智模型 ⑦：`Mixture ≠ Curriculum`。Mixture 控制同一阶段的数据比例，Curriculum 控制训练分布如何随阶段变化。**

> **心智模型 ⑧：`HardCaseValue ∝ BoundaryInformation`。合成难例的价值在决策边界信息密度，不在原始数量。**

---

# 二十八、把完整 Synthetic + Curriculum 流程压成一张专业工程图

```text
                      Real CPT Corpus
                        真实领域语料
                              │
                              ▼
                       Coverage Analysis
                         分析覆盖缺口
                              │
                              ▼
                       Gap Definition
                      定义需要补的分布
                              │
                              ▼
                     Synthetic Generation
                  教师模型生成候选数据
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
            Paraphrase     Hard Case    Counterfactual
              改写          难例          反事实
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                        Validation
                规则 / 证据 / 一致性验证
                              │
                              ▼
                      Dedup + Firewall
                 去重 + Benchmark隔离
                              │
                              ▼
                      Quality Scoring
                        合成质量评分
                              │
                              ▼
                       Mixture Control
                  控制真实/合成数据比例
                              │
                              ▼
                     Curriculum Schedule
                   按难度设计训练阶段
                              │
                              ▼
                    Phase-wise Training
                       分阶段继续预训练
                              │
                              ▼
                 Domain + Regression Eval
                   领域与通用能力评测
                              │
                              ▼
                    Rebalance / Reject
                      调整比例或淘汰
```

脑中最后只留一句：

> **Synthetic Data 的专业价值不是“便宜地把数据做大”，而是针对真实 Corpus 的明确覆盖缺口，用可追溯、可验证、可去重、可控比例的合成样本扩展训练分布，并通过 Curriculum 把这些数据按难度和阶段有计划地送进模型。**

---

# 第八课 · 第 8 阶段掌握测试

现在不回看正文，你应该能够解释：为什么 Synthetic Data 不等于免费新知识；为什么合成前必须先做 Coverage Gap 分析；Paraphrase、Template Variation、Hard Case、Counterfactual 和 Structure Synthesis 分别解决什么问题；为什么 Surface Diversity 不等于 Distribution Diversity；Teacher Model 为什么不是 Ground Truth；为什么 Generated Data 不能直接进入训练；事实型 Synthetic Data 为什么需要 Grounding；为什么 Synthetic Data 必须记录 Lineage；什么是 Model Collapse 风险；为什么合成数据必须设置占比上限；Mixture 和 Curriculum 有什么区别；Difficulty 为什么是多维的；Progressive Curriculum 和 Mixed Curriculum 有什么差别；为什么 Hard Case 的价值在决策边界信息量；为什么合成数据仍要做 Dedup 和 Benchmark Firewall；什么情况下应该加强人工审核；Synthetic CPT Data 和 Synthetic SFT Data 为什么不能混为一谈；以及为什么 Synthetic + Curriculum 最终必须和领域评测、通用回归一起闭环。

如果这些能够完整讲出来：

\[
\boxed{
第八课第8阶段真正掌握
}
\]

---

# 下一阶段：第八课 · 第 9 阶段
# CPT vs SFT：什么时候继续预训练，什么时候监督微调，怎样正确串联？
## 两者都会改 Weight，但一个在学“领域分布”，一个在学“任务行为”；真实项目里怎样判断到底该做哪一个、先做哪一个、做完以后怎样评测？

下一阶段会正式进入：

```text
CPT vs SFT
继续预训练与监督微调

Domain Gap
领域分布差距

Behavior Gap
任务行为差距

Training Order
训练顺序

Base → CPT → SFT
基础模型 → 继续预训练 → 监督微调

SFT after CPT
CPT后重新对齐

Adapter Compatibility
适配器兼容

Evaluation Separation
分层评测

Decision Matrix
技术路线决策矩阵

Go / No-Go Gate
是否进入CPT或SFT
```

并建立：

# `ProcurementCPTSFTDecisionPolicy_V0.1`

下一阶段最关键的一条边界会是：

\[
\boxed{
DomainGap
\neq
BehaviorGap
}
\]

也就是说：

> **模型“不够懂采购”和“模型不会按要求做采购任务”，是两种不同的问题。**

---

<!-- LESSON 08 STAGE 08 END -->


<!-- LESSON 08 STAGE 09 START -->

# 第八课 · 第 9 阶段
# CPT vs SFT：什么时候继续预训练，什么时候监督微调，怎样正确串联？
## 两者都会改 Weight，但一个在学“领域分布”，一个在学“任务行为”；真实项目里怎样判断到底该做哪一个、先做哪一个、做完以后怎样评测？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **DomainGap ≠ BehaviorGap。不懂领域和不会按要求做任务，是两个不同问题。**
2. **TrainingChoice 必须由 ErrorDiagnosis 驱动。先判断错误发生在哪一层，再决定 CPT、SFT、RAG 或 Agent。**
3. **DomainCompetence ≠ InstructionBehavior。领域底座能力和任务行为能力必须分层看。**
4. **CPT = WorldModeling，SFT = BehaviorShaping。CPT 主要塑造领域表示，SFT 主要塑造任务行为。**
5. **CourseOrder ≠ ProductionTrainingGraph。课程先学 SFT 后学 CPT，不代表真实训练顺序就应该如此。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `CPT` | CPT/继续预训练：在领域语料上继续执行预训练目标 |
| `SFT` | 监督微调：用监督样本继续更新模型参数 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `Observe` | Observe/观察：读取当前状态和工具结果 |

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

到第 8 阶段，我们已经把 CPT 的数据、训练目标、采样、遗忘、能力保持和合成数据都串起来了。

现在必须解决一个真实项目里最容易做错的技术路线问题：

> **模型效果不好，到底应该继续做 CPT，还是做 SFT？**

很多团队会把这两件事混在一起：

```text
模型不懂领域
→ 做SFT

模型格式不好
→ 继续CPT

模型答错政策
→ 再训练一遍

模型不会按Schema输出
→ 加更多领域语料
```

这些做法的问题是：

> 没有先判断“错的是哪一层”。

所以本阶段正式建立：

# `ProcurementCPTSFTDecisionPolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

CPT 和 SFT 都会改变模型参数。

但它们优化的不是同一个问题。

\[
\boxed{
DomainGap
\neq
BehaviorGap
}
\]

# Domain Gap
## 领域分布差距

指：

> 模型对政府采购语言、结构、术语和统计分布本身不够熟。

# Behavior Gap
## 任务行为差距

指：

> 模型虽然理解输入，但不会按要求完成任务、遵守格式或执行输出协议。

所以：

\[
\boxed{
CPT
主要解决
DomainGap
}
\]

\[
\boxed{
SFT
主要解决
BehaviorGap
}
\]

---

# 二、核心心智模型 ①：先诊断 Error Layer，再选择 Training Method

错误流程：

```text
效果不好
↓
训练更多
```

专业流程：

```text
Observed Error
观察到错误
↓
Error Decomposition
拆解错误来源
↓
Domain Gap?
是否领域理解不足
↓
Behavior Gap?
是否任务行为不足
↓
Knowledge Freshness Gap?
是否外部知识过期
↓
Tool / Workflow Gap?
是否执行链问题
↓
Choose Intervention
选择干预方式
```

中文解释：

> 先判断问题发生在领域理解、任务行为、知识新鲜度，还是工具执行层，再决定 CPT、SFT、RAG 或 Agent。

所以：

\[
\boxed{
TrainingChoice
必须由
ErrorDiagnosis
驱动
}
\]

---

# 三、CPT 到底学什么？

CPT 仍然做：

# Causal Language Modeling
## 因果语言建模

它学习：

```text
政府采购术语怎样共同出现
采购文件结构怎样延续
领域语言有哪些统计模式
长文档章节之间怎样关联
行业采购文本是什么风格
```

所以更接近：

\[
\boxed{
CPT
=
LearnDomainDistribution
}
\]

它在提升的是：

> 模型的领域底座。

---

# 四、SFT 到底学什么？

SFT：

# Supervised Fine-Tuning
## 监督微调

通常有明确的：

```text
Input
输入

Target Response
目标回答
```

例如：

```text
输入：
某采购条款

目标输出：
risk_type
reason
evidence
recommendation
```

SFT 主要学习：

```text
任务格式
输出风格
指令遵循
Schema结构
回答边界
拒答行为
```

所以：

\[
\boxed{
SFT
=
LearnTaskBehavior
}
\]

---

# 五、核心心智模型 ②：Language Modeling Competence 和 Instruction Behavior 是两个不同能力层

一个模型可能：

```text
很懂采购语言
但不会按JSON输出
```

也可能：

```text
JSON输出非常稳定
但对采购概念理解浅
```

所以：

\[
\boxed{
DomainCompetence
\neq
InstructionBehavior
}
\]

前者偏：

> CPT。

后者偏：

> SFT。

这就是为什么两者不能互相简单替代。

---

# 六、什么时候优先做 CPT？

典型信号包括：

```text
大量高质量无标注领域文本存在

模型对领域术语和结构理解不稳定

长采购文档语言建模明显弱

行业语料分布和通用语料差异大

SFT样本有限但无标注Corpus很大

希望提升的是多任务共享的领域底座
```

例如：

> 不只是风险识别弱，而是多个采购任务都表现出领域理解不足。

这时更像：

\[
\boxed{
SharedDomainRepresentationGap
}
\]

CPT 更有价值。

---

# 七、什么时候优先做 SFT？

典型信号包括：

```text
模型基本理解输入
但不会按要求回答

格式不稳定
Schema不遵守
不会拒答
任务边界不清
分类标签不稳定
解释模板不一致
```

这类问题更像：

\[
\boxed{
TaskAlignmentGap
}
\]

所以优先：

> SFT。

---

# 八、核心心智模型 ③：如果问题只发生在一个任务上，先怀疑 Behavior；如果多个任务都受影响，才更像 Domain Foundation 问题

假设：

```text
风险分类
表现差

但：
摘要正常
术语解释正常
文件理解正常
问答正常
```

那不一定需要 CPT。

可能只是：

> 风险分类任务本身没有对齐好。

反过来，如果：

```text
风险识别差
文件问答差
术语理解差
长文档摘要也差
```

多个任务共同受影响，

就更像：

> 共享领域表示不足。

所以：

\[
\boxed{
SingleTaskFailure
优先检查
BehaviorGap
}
\]

\[
\boxed{
CrossTaskFailure
更值得检查
DomainGap
}
\]

---

# 九、什么问题其实既不该 CPT，也不该 SFT？

非常重要。

如果用户问：

```text
2026年最新采购政策是什么？
```

而模型不知道，

这更像：

# Knowledge Freshness Gap
## 知识新鲜度差距

应该优先：

\[
\boxed{
RAG / Tool
}
\]

不是把最新政策重新写进 Weight。

---

如果问题是：

```text
需要读取项目当前预算
需要查实时供应商信息
需要提交审批
```

这更像：

# Tool / Workflow Gap
## 工具或工作流差距

应该优先：

\[
\boxed{
Agent / Tool Calling
}
\]

所以：

\[
\boxed{
NotEveryError
NeedsWeightUpdate
}
\]

---

# 十、完整技术路线诊断流程

英文流程：

```text
Observe Failure
↓
Classify Failure
↓
Domain Gap?
↓
Behavior Gap?
↓
Fresh Knowledge Gap?
↓
Execution Gap?
↓
Select Intervention
↓
Run Controlled Experiment
↓
Evaluate
↓
Promote / Reject
```

中文解释：

```text
观察真实失败案例
↓
给错误分类
↓
判断是不是领域理解不足
↓
判断是不是任务行为不对
↓
判断是不是外部知识过期
↓
判断是不是工具执行链问题
↓
选择CPT / SFT / RAG / Agent
↓
做受控实验
↓
分别评测能力变化
↓
决定升级还是否决
```

所以：

\[
\boxed{
Intervention
必须匹配
FailureType
}
\]

---

# 十一、真实训练顺序为什么通常是 Base → CPT → SFT？

经典路线：

```text
Base Model
基础模型
↓
CPT
学习领域分布
↓
Domain-adapted Base
领域适配底座
↓
SFT
学习任务行为
↓
Task Model
任务模型
```

也就是：

\[
\boxed{
Base
\rightarrow
CPT
\rightarrow
SFT
}
\]

为什么？

因为 CPT 先塑造：

> 模型“懂什么样的语言世界”。

SFT 再塑造：

> 模型“应该怎样完成任务”。

---

# 十二、核心心智模型 ④：CPT 先学“世界”，SFT 再学“行为”

可以压成一句：

\[
\boxed{
CPT
=
WorldModeling
}
\]

\[
\boxed{
SFT
=
BehaviorShaping
}
\]

这里的 World Modeling 不是说模型真的构建完整世界模型，

而是强调：

> CPT 更偏向学习领域文本分布和表示结构。

SFT 更偏向：

> 把已有能力导向指定任务行为。

---

# 十三、为什么 SFT → CPT 可能破坏对齐？

假设你已经有：

```text
ProcurementLM_V0.1
```

它经过 SFT 后会：

```text
遵守JSON Schema
按任务格式回答
保持拒答边界
```

如果这时直接做大量 CPT，

训练目标重新变成：

> 全文 Next Token Prediction。

模型可能逐渐弱化：

```text
Instruction Following
Chat格式
Schema遵循
任务对齐
```

所以：

\[
\boxed{
SFT
\rightarrow
LargeCPT
可能导致
BehaviorRegression
}
\]

---

# 十四、那已经有 SFT 模型了怎么办？

这正是我们当前项目的现实情况。

我们已经有：

```text
ProcurementLM_V0.1
```

如果现在决定 CPT，

更稳的工程路线通常是：

```text
回到Base Model
↓
做CPT
↓
得到Domain-adapted Base
↓
重新做SFT
↓
得到ProcurementLM_V0.2
```

即：

\[
\boxed{
Base
\rightarrow
CPT
\rightarrow
SFT
\rightarrow
V0.2
}
\]

而不是：

\[
\boxed{
V0.1
\rightarrow
直接CPT
\rightarrow
结束
}
\]

---

# 十五、核心心智模型 ⑤：课程顺序不是最终训练图谱

我们先学过 SFT，

现在才学 CPT。

但这只是：

> 教学顺序。

真实工程 DAG 可能是：

```text
Base
├─ CPT
│   └─ Domain Base
│       └─ SFT
│           └─ ProcurementLM_V0.2
│
└─ 原有SFT实验
    └─ ProcurementLM_V0.1
```

所以：

\[
\boxed{
CourseOrder
\neq
ProductionTrainingGraph
}
\]

这条在第 1 阶段提过，

现在正式进入技术路线决策。

---

# 十六、CPT 后 SFT，SFT 数据还可以继续用原来的么？

通常可以：

> 但必须重新做兼容性和分布检查。

因为 CPT 后模型的：

```text
领域表示
Token概率分布
可能的Tokenizer
Embedding
```

都可能变化。

所以应该重新验证：

```text
SFT Dataset Version
Tokenizer Compatibility
Prompt Template
Loss Mask
Max Length
Evaluation Baseline
```

不能简单：

> “旧 SFT 脚本原样跑。”

---

# 十七、Adapter Compatibility：LoRA 能不能直接从旧模型搬过去？

如果旧的 LoRA 是在：

```text
BaseModel_A
```

上训练的。

CPT 后得到：

```text
BaseModel_A_CPT
```

即使模型结构相同，

参数底座已经变化。

所以旧 Adapter：

> 可能还能加载。

但这不等于：

> 行为一定仍然正确。

所以：

\[
\boxed{
Loadable
\neq
Compatible
}
\]

真正应该：

```text
重新评测

最好重新SFT / 重新训练Adapter
```

---

# 十八、核心心智模型 ⑥：Checkpoint Compatibility 和 Behavioral Compatibility 是两回事

一个 Adapter：

```text
shape对得上
可以load
不报错
```

只能说明：

# Structural Compatibility
## 结构兼容

不能说明：

# Behavioral Compatibility
## 行为兼容

所以：

\[
\boxed{
StructuralCompatibility
\neq
BehavioralCompatibility
}
\]

这条对 LoRA、Tokenizer、Checkpoint 组合都成立。

---

# 十九、CPT 和 SFT 应该怎样分层评测？

CPT 后先测：

```text
Domain Perplexity
领域困惑度

Domain Probes
领域理解探针

General Regression
通用能力回归

Long Context
长文档能力
```

这是：

# Foundation Evaluation
## 底座能力评测

然后 SFT 后再测：

```text
Instruction Following
指令遵循

Task Accuracy
任务正确率

Schema Compliance
结构化输出

Abstention
拒答与不确定性

Procurement Workflow Tasks
采购业务任务
```

这是：

# Behavior Evaluation
## 行为评测

所以：

\[
\boxed{
CPTEval
\neq
SFTEval
}
\]

---

# 二十、核心心智模型 ⑦：不要用下游任务分数替代 CPT 诊断，也不要用 Perplexity 替代 SFT 诊断

如果 CPT 后：

```text
PPL下降
```

只能说明：

> 语言建模改善。

不能自动说明：

> 风险识别一定更好。

如果 SFT 后：

```text
任务F1提高
```

也不能自动说明：

> 模型领域底座更强。

所以：

\[
\boxed{
FoundationMetric
\neq
BehaviorMetric
}
\]

两层必须分开。

---

# 二十一、Decision Matrix：到底该选 CPT、SFT、RAG 还是 Agent？

可以建立第一版决策矩阵：

| 现象 | 更可能的问题 | 优先技术 |
|---|---|---|
| 多个采购任务都不懂领域术语 | Domain Gap | CPT |
| 只是不按格式输出 | Behavior Gap | SFT |
| 不知道最新政策 | Fresh Knowledge Gap | RAG |
| 不会调用系统完成任务 | Execution Gap | Agent |
| 长采购文件结构理解弱 | Domain / Context Gap | CPT + Context策略 |
| 会理解但分类标签不稳定 | Behavior Gap | SFT |
| 会回答但引用旧规则 | Freshness / Evidence Gap | RAG |
| 工具会调用但流程混乱 | Workflow Control Gap | Agent |

这张表非常重要。

因为：

\[
\boxed{
BestTechnique
取决于
FailureLayer
}
\]

---

# 二十二、Go / No-Go Gate：什么时候允许进入 CPT？

进入 CPT 前至少确认：

```text
跨任务Domain Gap存在

高质量无标注领域语料足够

RAG / SFT不能更低成本解决

Benchmark已隔离

Forgetting Eval已准备

Retention机制已准备
```

如果不满足：

> 不应该直接开始大规模 CPT。

所以：

\[
\boxed{
CPT
需要
GoNoGoGate
}
\]

---

# 二十三、什么时候允许进入 SFT？

SFT 前至少确认：

```text
任务定义稳定

输入输出Schema明确

Gold / High-quality Target存在

评价指标明确

Prompt / Template版本锁定

错误主要属于Behavior Gap
```

否则：

> 可能在用监督数据“硬教”一个本来没定义清楚的任务。

---

# 二十四、Ablation：怎样证明 CPT 真的值得？

至少可以比较三组：

```text
A
Base → SFT

B
Base → CPT → SFT

C
Base → CPT
```

然后分别比较：

```text
Domain Foundation Metrics
领域底座能力

Task Metrics
任务能力

General Regression
通用回归

Training Cost
训练成本
```

如果：

```text
B 相比 A
没有明显收益
```

那就要认真质疑：

> CPT 是否真的值得。

所以：

\[
\boxed{
CPTValue
需要
ControlledComparison
}
\]

---

# 二十五、核心心智模型 ⑧：技术路线的目标不是“把所有方法都用上”，而是最小充分干预

这条非常重要。

工程上不是：

```text
CPT
+
SFT
+
RAG
+
Agent
全上
```

就一定最好。

而是：

\[
\boxed{
UseMinimumSufficientIntervention
}
\]

中文：

> **用最小但足够的技术干预解决当前错误。**

因为每加一层：

```text
成本增加
版本复杂度增加
评测复杂度增加
失败模式增加
维护负担增加
```

所以：

\[
\boxed{
MoreTech
\neq
BetterSystem
}
\]

---

# 二十六、把 CPT、SFT、RAG、Agent 压成一张能力边界图

```text
                    Observed Failure
                       观察到失败
                           │
                           ▼
                     Error Diagnosis
                        错误诊断
                           │
          ┌────────────────┼────────────────┬────────────────┐
          ▼                ▼                ▼                ▼
      Domain Gap      Behavior Gap    Knowledge Gap     Execution Gap
      领域分布差距      任务行为差距      外部知识差距      执行流程差距
          │                │                │                │
          ▼                ▼                ▼                ▼
         CPT              SFT              RAG             Agent
    学领域底座        学任务行为        补当前证据        完成真实流程
          │                │                │                │
          └────────────────┼────────────────┴────────────────┘
                           ▼
                    Controlled Eval
                       受控评测
                           │
                           ▼
                     Release Decision
                       发布决策
```

这张图必须成为后面所有模型升级决策的基础。

---

# 二十七、本阶段正式工程产物：`ProcurementCPTSFTDecisionPolicy_V0.1`

第一版至少锁定：

```text
decision_policy_version

failure_taxonomy

domain_gap_definition

behavior_gap_definition

knowledge_gap_definition

execution_gap_definition

cpt_go_no_go

sft_go_no_go

rag_preferred_conditions

agent_preferred_conditions

training_order

base_model_version

cpt_checkpoint

sft_dataset_version

sft_config_version

adapter_compatibility_check

tokenizer_compatibility_check

foundation_eval_suite

behavior_eval_suite

general_regression_suite

ablation_plan

minimum_sufficient_intervention

release_gate

trace_logging
=
enabled
```

每次技术路线决策至少记录：

```text
issue_id

observed_failure

failure_layer

evidence

candidate_interventions

selected_intervention

reason

experiment_id

before_metrics

after_metrics

cost

regression

final_decision
```

这样以后才能回答：

> **为什么这个问题选择 CPT，而不是 SFT / RAG / Agent？**

---

# 二十八、本阶段最重要的 8 个核心心智模型

> **心智模型 ①：`DomainGap ≠ BehaviorGap`。不懂领域和不会按要求做任务，是两个不同问题。**

> **心智模型 ②：`TrainingChoice 必须由 ErrorDiagnosis 驱动`。先判断错误发生在哪一层，再决定 CPT、SFT、RAG 或 Agent。**

> **心智模型 ③：`DomainCompetence ≠ InstructionBehavior`。领域底座能力和任务行为能力必须分层看。**

> **心智模型 ④：`CPT = WorldModeling，SFT = BehaviorShaping`。CPT 主要塑造领域表示，SFT 主要塑造任务行为。**

> **心智模型 ⑤：`CourseOrder ≠ ProductionTrainingGraph`。课程先学 SFT 后学 CPT，不代表真实训练顺序就应该如此。**

> **心智模型 ⑥：`StructuralCompatibility ≠ BehavioralCompatibility`。Checkpoint 或 Adapter 能加载，不代表行为一定兼容。**

> **心智模型 ⑦：`FoundationMetric ≠ BehaviorMetric`。CPT 与 SFT 的评测必须分层，不能用一个指标替代另一个。**

> **心智模型 ⑧：`MoreTech ≠ BetterSystem`。真正专业的系统优先采用最小但足够的干预，而不是把所有技术都堆上去。**

---

# 二十九、把完整 CPT / SFT 决策流程压成一张专业工程图

```text
                      Real Failure Cases
                        真实失败案例
                              │
                              ▼
                       Error Taxonomy
                        错误类型归因
                              │
          ┌───────────────────┼───────────────────┬───────────────────┐
          ▼                   ▼                   ▼                   ▼
      Domain Gap         Behavior Gap       Knowledge Gap        Execution Gap
       领域差距             行为差距            知识差距              执行差距
          │                   │                   │                   │
          ▼                   ▼                   ▼                   ▼
         CPT                 SFT                 RAG                Agent
          │                   │                   │                   │
          └───────────────────┼───────────────────┴───────────────────┘
                              ▼
                     Controlled Experiment
                         受控对比实验
                              │
                              ▼
               Foundation + Behavior Evaluation
                  底座能力 + 行为能力评测
                              │
                              ▼
                    General Regression Check
                       通用能力回归检查
                              │
                              ▼
                  Cost / Benefit / Complexity
                     成本收益与复杂度分析
                              │
                              ▼
                 Minimum Sufficient Intervention
                       最小充分技术干预
                              │
                              ▼
                        Release Gate
```

脑中最后只留一句：

> **CPT 和 SFT 的专业区别，不是“无监督训练”和“有监督训练”这么简单，而是先判断模型缺的是领域分布能力还是任务行为能力，再用最小充分干预解决对应问题，并把底座能力、任务行为、通用回归和训练成本分层评测。**

---

# 第八课 · 第 9 阶段掌握测试

现在不回看正文，你应该能够解释：Domain Gap 和 Behavior Gap 为什么不是一回事；CPT 和 SFT 分别在学习什么；为什么单任务失败更优先检查 Behavior，而跨任务共同失败更值得怀疑 Domain Foundation；为什么最新政策问题优先是 RAG 而不是 Weight Update；为什么工具执行问题优先属于 Agent；为什么真实训练顺序通常是 `Base → CPT → SFT`；为什么 `SFT → Large CPT` 可能破坏对齐；已经有 SFT 模型时为什么更稳的做法通常是回到 Base 做 CPT 后重新 SFT；为什么 Course Order 不等于 Production Training Graph；LoRA Adapter 能加载为什么不代表行为兼容；CPT 和 SFT 应该分别评什么；为什么 Foundation Metric 和 Behavior Metric 不能混；什么时候 CPT 应该被 Go / No-Go Gate 拦住；怎样用 Ablation 证明 CPT 是否真的值得；以及为什么真正专业的路线是 Minimum Sufficient Intervention，而不是把 CPT、SFT、RAG、Agent 全部堆上去。

如果这些能够完整讲出来：

\[
\boxed{
第八课第9阶段真正掌握
}
\]

---

# 下一阶段：第八课 · 第 10 阶段
# 真正训练 `ProcurementLM_V0.2`：端到端 CPT、评测、回归测试与 Release Gate
## 怎样把前 9 个阶段全部接成一个真正可运行、可复现、可审计、可回滚的 CPT 工程系统？

下一阶段会正式把：

```text
Domain Gap Diagnosis
领域差距诊断

Corpus Governance
语料治理

Tokenizer Audit
分词器审计

Sequence Construction
训练序列构造

Data Mixture
数据混合

Forgetting Evaluation
遗忘评测

Retention
能力保持

Synthetic Data
合成数据

Curriculum
课程式训练

CPT → SFT
训练链路

Release Gate
发布门槛
```

全部连接起来。

最终形成：

# `ProcurementLM_V0.2`

并把第八课正式闭环。

下一阶段最重要的总原则会是：

\[
\boxed{
CPTExperiment
\neq
ModelRelease
}
\]

也就是说：

> **训练跑完，只代表得到一个实验 Checkpoint；只有通过完整评测、回归、版本、可复现和 Release Gate，才算真正得到可发布的 `ProcurementLM_V0.2`。**

---

<!-- LESSON 08 STAGE 09 END -->


<!-- LESSON 08 STAGE 10 START -->

# 第八课 · 第 10 阶段
# 真正训练 `ProcurementLM_V0.2`：端到端 CPT、评测、回归测试与 Release Gate
## 怎样把前 9 个阶段全部接成一个真正可运行、可复现、可审计、可回滚的 CPT 工程系统？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **CPTExperiment ≠ ModelRelease。训练跑完只是得到实验 Checkpoint，不代表模型可以发布。**
2. **ModelRelease ≠ WeightsOnly。真正模型版本必须包含 Tokenizer、配置、数据血缘、评测证据和 Release Manifest。**
3. **NoFrozenBaseline = NoReliableComparison。没有固定基线，就无法可靠证明模型到底变好还是变坏。**
4. **Scale amplifies Signal and Error。扩大训练规模会同时放大正确方向和错误配置，所以 Full Run 前必须先做 Pilot。**
5. **BestCheckpoint = MultiObjectiveDecision。最优发布 Checkpoint 不是 Loss 最低，而是领域收益、通用保持、成本和兼容性的综合折中。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `CPT` | CPT/继续预训练：在领域语料上继续执行预训练目标 |
| `Checkpoint` | 检查点：保存模型和训练状态以便恢复/发布 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `SFT` | 监督微调：用监督样本继续更新模型参数 |
| `Tokenizer` | 分词器：文本与 Token ID 之间的编码/解码组件 |
| `Regression` | 回归测试：更新后验证旧能力和关键切片没有退化 |

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

前 9 个阶段，我们已经分别解决了：

- CPT 到底在学什么；
- 什么样的领域 Corpus 才值得训练；
- Tokenizer 要不要改；
- Sequence、Context Length、Packing 和 Loss 怎样定义真实训练任务；
- Data Mixture 怎样分配训练预算；
- 怎样检测 Catastrophic Forgetting；
- 怎样通过 Replay、Regularization 和参数约束保持能力；
- Synthetic Data 与 Curriculum 怎样补覆盖而不是制造“假数据世界”；
- CPT、SFT、RAG、Agent 到底分别解决什么问题。

第 10 阶段不再增加一个孤立概念。

它要做的是：

> **把这些东西真正接成一条可以执行、可以停止、可以恢复、可以比较、可以发布的模型工程流水线。**

本阶段最终交付：

# `ProcurementLM_V0.2`

并正式完成第八课。

---

# 一、先锁死本阶段最重要的一句话

一次 CPT 训练成功跑完，只代表：

> **得到一个实验 Checkpoint。**

它不等于：

> **得到一个可以发布的模型。**

所以本阶段最重要的总边界是：

\[
\boxed{
CPTExperiment
\neq
ModelRelease
}
\]

真正的模型发布至少还需要：

\[
\boxed{
Reproducibility
+
Evaluation
+
RegressionControl
+
ArtifactCompleteness
+
ReleaseGate
+
Rollbackability
}
\]

也就是：

> **能复现、能评测、能证明没把旧能力弄坏、产物完整、通过发布门槛，而且出问题能回滚。**

---

# 二、核心心智模型 ①：Model Release 是“证据包”，不是一个 `model.safetensors`

很多人把模型发布理解成：

```text
训练结束
↓
保存权重
↓
上传模型
```

这远远不够。

一个真正可发布的模型至少应该能回答：

```text
它从哪个 Base Model 来？

用了哪个 Corpus Version？

用了哪个 Tokenizer Version？

Sequence Builder 是哪一版？

Mixture 怎么配的？

训练了多少 Effective Tokens？

选的是哪个 Checkpoint？

为什么选它？

CPT 后重新做了哪版 SFT？

领域能力涨了多少？

通用能力掉了多少？

Release Gate 为什么通过？

如果出问题，回滚到哪里？
```

所以：

\[
\boxed{
ModelArtifact
\neq
WeightsOnly
}
\]

更准确地说：

\[
\boxed{
ModelRelease
=
Weights
+
Tokenizer
+
Config
+
DataLineage
+
EvalBundle
+
ReleaseManifest
}
\]

---

# 三、端到端总流程：从 Domain Gap 到 `ProcurementLM_V0.2`

先给完整英文工程链，再逐步翻译。

```text
Failure Evidence
↓
Domain Gap Diagnosis
↓
CPT Go / No-Go
↓
Freeze Baseline
↓
Corpus Build & Benchmark Firewall
↓
Tokenizer Audit
↓
Sequence Construction
↓
Mixture & Replay Design
↓
Pilot CPT
↓
Checkpoint Evaluation
↓
Full CPT
↓
Forgetting / Retention Control
↓
Checkpoint Selection
↓
SFT on CPT Base
↓
Foundation + Behavior + Regression Evaluation
↓
Release Gate
↓
Release Bundle
↓
ProcurementLM_V0.2
```

中文解释：

```text
先从真实失败案例出发
↓
证明问题确实属于领域底座不足
↓
判断是否值得进入CPT
↓
冻结训练前基线模型和评测结果
↓
建设可训练Corpus并隔离未来Benchmark
↓
审计Tokenizer是否真的构成瓶颈
↓
定义Sequence、Context、Packing、Loss规则
↓
设计领域数据、Replay和各数据桶训练比例
↓
先做小规模Pilot验证路线
↓
周期性评测Checkpoint
↓
确认路线有效后再做正式CPT
↓
持续监控遗忘并动态调Retention
↓
从多个Checkpoint中选择最合适的领域底座
↓
在新底座上重新做SFT
↓
分别评测底座能力、任务行为和通用回归
↓
通过Release Gate
↓
打包完整模型发布资产
↓
形成ProcurementLM_V0.2
```

所以：

\[
\boxed{
TrainingPipeline
=
DecisionPipeline
+
ExecutionPipeline
+
EvidencePipeline
}
\]

训练流水线不只是“执行训练”。

它同时是一条：

> **技术决策链 + 计算执行链 + 证据链。**

---

# 四、Phase 0：先冻结 Baseline，不然以后根本不知道模型有没有变好

在任何新 CPT Run 开始之前，先冻结：

# Baseline
## 基线

至少包括：

```text
base_model_id

base_model_hash

tokenizer_version

baseline_domain_metrics

baseline_general_metrics

baseline_instruction_metrics

baseline_generation_config

baseline_eval_config
```

为什么？

因为如果 CPT 前后：

```text
Prompt变了
Decoding参数变了
评测集变了
Tokenizer变了
Scoring Rule变了
```

你就无法确定：

> 分数变化到底来自模型，还是来自评测条件变化。

所以：

\[
\boxed{
NoFrozenBaseline
=
NoReliableComparison
}
\]

---

# 五、核心心智模型 ②：Reproducibility 不是“我还记得大概怎么训的”

真正的：

# Reproducibility
## 可复现性

不是：

> “我大概记得用了 2e-5 学习率。”

而是至少冻结：

```text
Base Model Version

Tokenizer Version

Corpus Version

Sequence Builder Version

Mixture Policy Version

Training Config

Code Commit

Environment

Random Seed

Checkpoint Policy

Evaluation Config
```

可以把一次 Run 表示成：

\[
R
=
(
M_0,
T,
D,
S,
P,
C,
E
)
\]

其中：

- \(M_0\)：Base Model；
- \(T\)：Tokenizer；
- \(D\)：Corpus；
- \(S\)：Sequence / Sampling Policy；
- \(P\)：训练参数；
- \(C\)：代码与环境；
- \(E\)：评测协议。

所以：

\[
\boxed{
Reproducibility
=
VersionEverythingThatChangesOutcome
}
\]

注意：

> 固定 Seed 不代表所有 GPU / Kernel 场景都能做到逐 bit 完全一致。

工程目标首先是：

> **配置、数据、代码、环境和评测都可追溯，结果能够在合理误差内被重复验证。**

---

# 六、Phase 1：先做 Pilot CPT，不要一上来烧完整 Token Budget

如果正式计划：

```text
100B CPT tokens
```

不应该第一步就把 100B 全跑完。

先做：

# Pilot Run
## 小规模试验训练

例如只使用正式预算的一小部分，

主要验证：

```text
Data Loader是否正确

Tokenizer / Sequence是否兼容

Loss是否正常下降

Mixture是否符合配置

Replay是否真正进入训练

Checkpoint是否可恢复

Domain Metric是否有正向趋势

General Regression是否开始失控
```

Pilot 的目的不是：

> 得到最终最好模型。

而是：

\[
\boxed{
Pilot
=
ValidateTrainingHypothesis
}
\]

也就是：

> **验证整条训练假设值得继续放大。**

---

# 七、核心心智模型 ③：Scale Up 之前先证明 Direction Correct

一条错误路线：

```text
小规模已经看不到收益
↓
那就多训十倍看看
```

通常不是好工程。

因为规模放大会同时放大：

```text
计算成本
数据偏差
遗忘风险
错误配置
Benchmark污染
重复曝光
```

所以：

\[
\boxed{
Scale
放大的是
Signal
也放大
Error
}
\]

正式 Full Run 之前至少应该看到：

```text
领域指标有稳定正向趋势

通用回归仍在阈值内

数据分布符合预期

训练数值稳定

恢复流程可用
```

---

# 八、Phase 2：正式 CPT Run 不是一条直线，而是一串 Checkpoint Decision

正式训练过程中：

```text
Checkpoint_01
Checkpoint_02
Checkpoint_03
...
Checkpoint_N
```

每个 Checkpoint 都应该进入统一评测。

至少记录：

```text
tokens_seen

effective_training_tokens

training_loss

validation_loss

domain_perplexity

domain_probe_metrics

general_regression_metrics

instruction_regression_metrics

mixture_observed_share

replay_share

parameter_drift

training_cost
```

然后形成：

# Training Trajectory
## 训练轨迹

所以：

\[
\boxed{
FinalCheckpoint
\neq
AutomaticallyBestCheckpoint
}
\]

---

# 九、Checkpoint Selection：怎样选择真正值得进入 SFT 的 CPT 底座？

不要只选：

> Domain Score 最高。

要同时看：

```text
Domain Gain
领域收益

General Retention
通用能力保持

Training Stability
训练稳定性

Cost
训练成本

Marginal Gain
边际收益

Compatibility
Tokenizer / Serving兼容
```

可以把它理解成：

# Pareto Selection
## 多目标折中选择

也就是说：

> 找不到“所有指标都绝对最好”的模型时，选择在多个目标之间没有被明显支配的 Checkpoint。

所以：

\[
\boxed{
BestCheckpoint
=
MultiObjectiveDecision
}
\]

不是：

\[
\boxed{
LowestLoss
}
\]

---

# 十、核心心智模型 ④：Loss 是训练信号，不是发布裁判

CPT Loss 很重要。

因为它告诉我们：

> 模型是否越来越适应训练分布。

但它不能回答：

```text
采购任务是否真的更好？

通用能力是否退化？

指令遵循是否保持？

长文档能力是否真的提升？

结构化输出是否仍稳定？
```

所以：

\[
\boxed{
TrainingLoss
\neq
ReleaseMetric
}
\]

同理：

\[
\boxed{
Perplexity
\neq
ReleaseDecision
}
\]

Loss / PPL 是：

> 训练层指标。

Release Gate 需要：

> 多层证据。

---

# 十一、Phase 3：CPT 后不要直接宣布 `ProcurementLM_V0.2`，先重新 SFT

第 9 阶段已经锁定：

\[
\boxed{
Base
\rightarrow
CPT
\rightarrow
SFT
}
\]

所以选定 CPT Checkpoint 以后，

它只是：

# Domain-adapted Base
## 领域适配底座

接下来必须重新做：

# SFT
## 任务行为对齐

重新让模型恢复 / 学习：

```text
Instruction Following
指令遵循

Structured Output
结构化输出

Risk Classification
风险分类

Rationale
理由生成

Abstention
拒答与不确定性

Task Schema
任务协议
```

因此：

\[
\boxed{
CPTCheckpoint
\neq
ProcurementLM\_V0.2
}
\]

真正链路是：

\[
\boxed{
CPTCheckpoint
\rightarrow
SFT
\rightarrow
ReleaseCandidate
}
\]

---

# 十二、CPT 后重新 SFT 的关键原则：重新验证，不机械复用

可以复用原来的：

```text
SFT Dataset
Task Schema
Evaluation Set
```

但必须重新验证：

```text
Tokenizer Compatibility

Prompt Template

Max Sequence Length

Loss Mask

Adapter Target Modules

Embedding Training Policy

Learning Rate

SFT Baseline
```

特别是如果第 3 阶段最终真的：

> 修改了 Tokenizer / Vocabulary，

那旧 SFT Token Cache：

> 必须重新生成。

所以：

\[
\boxed{
ReusableArtifact
\neq
BlindlyReusableArtifact
}
\]

---

# 十三、Phase 4：评测必须分三层，而不是把所有指标搅成一个总分

第一层：

# Foundation Evaluation
## 底座能力评测

回答：

> CPT 真的让领域底座变强了吗？

看：

```text
Domain Perplexity
领域困惑度

Domain Probe
领域理解探针

Long-document Probe
长文档探针

Terminology Understanding
术语理解
```

---

第二层：

# Behavior Evaluation
## 任务行为评测

回答：

> 重新 SFT 后，模型会不会完成目标任务？

看：

```text
Task Accuracy / F1

Schema Compliance

Instruction Following

Abstention

Reason Quality

Citation / Evidence Use
```

---

第三层：

# Regression Evaluation
## 回归评测

回答：

> 为了更懂采购，损坏了什么？

看：

```text
General Language

Reasoning

Math

Code

Structured Output

Instruction Following
```

所以：

\[
\boxed{
ReleaseEvidence
=
Foundation
+
Behavior
+
Regression
}
\]

---

# 十四、核心心智模型 ⑤：一个模型必须有“收益证明”和“损失证明”

只证明：

> “采购能力更高”

是不够的。

还要证明：

> “关键原能力没有退化到不可接受”。

所以一次 Release Candidate 至少要形成两份证据：

# Gain Evidence
## 收益证据

证明：

\[
DomainCapability\uparrow
\]

以及：

# Regression Evidence
## 回归证据

证明：

\[
CriticalCapabilities
\not\downarrow
BeyondThreshold
\]

因此：

\[
\boxed{
Release
=
GainEvidence
+
RegressionEvidence
}
\]

---

# 十五、Release Gate：把“感觉可以发布”变成机器可检查规则

真正的：

# Release Gate
## 发布门槛

应该是明确条件。

概念上：

\[
ReleaseGate
=
G_{domain}
\land
G_{behavior}
\land
G_{regression}
\land
G_{artifact}
\land
G_{reproducibility}
\]

其中：

```text
G_domain
领域收益达到最低门槛

G_behavior
任务行为达到最低门槛

G_regression
关键能力退化不超过阈值

G_artifact
发布资产完整

G_reproducibility
训练和评测可追溯
```

只有全部为 True：

\[
\boxed{
ReleaseGate=True
}
\]

才允许升级成正式模型版本。

---

# 十六、核心心智模型 ⑥：Release Gate 必须在训练前定义，而不是训练后“看结果再定标准”

如果训练完以后才说：

> “这个指标掉 3% 好像也能接受。”

那很容易产生：

# Post-hoc Rationalization
## 事后合理化

所以真正专业的方式是：

> **训练前就定义成功和失败标准。**

例如：

```text
Domain Gain
必须达到预设最低改善

General Regression
不得超过预设阈值

Critical Task
不得出现严重退化

Artifact Completeness
必须全部通过
```

因此：

\[
\boxed{
PredefinedGate
>
PostHocJudgment
}
\]

这里的 `>` 表示：

> 工程决策可信度更高。

---

# 十七、Release Candidate 和 Released Model 必须分开

训练 + SFT 完成以后得到的是：

# Release Candidate
## 发布候选模型

例如：

```text
ProcurementLM_V0.2-RC1
```

它还要经历：

```text
完整评测
回归
兼容性
可复现检查
模型资产检查
```

通过以后才晋级：

```text
ProcurementLM_V0.2
```

所以：

\[
\boxed{
ReleaseCandidate
\neq
ReleasedModel
}
\]

这能防止：

> “刚训练出来的模型直接覆盖线上版本”。

---

# 十八、完整 Release Bundle 应该包含什么？

最终不要只交付一个权重目录。

第一版至少应该包含：

```text
ProcurementLM_V0.2/

├── model/
│   ├── weights
│   ├── config
│   └── generation_config
│
├── tokenizer/
│   ├── tokenizer files
│   └── tokenizer_manifest
│
├── training/
│   ├── cpt_config
│   ├── sft_config
│   ├── mixture_policy
│   ├── retention_policy
│   └── checkpoint_manifest
│
├── data_lineage/
│   ├── corpus_manifest
│   ├── synthetic_manifest
│   └── benchmark_firewall_report
│
├── evaluation/
│   ├── foundation_eval
│   ├── behavior_eval
│   ├── regression_eval
│   └── release_gate_report
│
├── provenance/
│   ├── base_model
│   ├── code_commit
│   ├── environment
│   └── run_manifest
│
└── MODEL_CARD.md
```

这就是：

# Release Bundle
## 发布资产包

---

# 十九、核心心智模型 ⑦：模型版本其实是一张 Artifact Graph

一个模型不是孤立文件。

它依赖：

```text
Base Model
↓
Tokenizer
↓
Corpus
↓
Sequence Builder
↓
Mixture Policy
↓
CPT Run
↓
Checkpoint
↓
SFT Run
↓
Evaluation Bundle
↓
Release Manifest
```

这其实是一张：

# Artifact Graph
## 工程产物依赖图

所以：

\[
\boxed{
ModelVersion
=
ArtifactGraphVersion
}
\]

如果其中任何关键节点无法追溯，

这个模型版本就不完整。

---

# 二十、Rollback：真正能发布的系统必须先设计好怎么退回去

发布 `ProcurementLM_V0.2` 前，

必须知道：

```text
上一个稳定版本是谁？

回滚需要换哪些文件？

Tokenizer是否同时回滚？

Adapter是否同时回滚？

RAG / Agent是否依赖某个输出Schema？

回滚后服务是否还能兼容？
```

所以：

# Rollback Plan
## 回滚方案

至少包含：

```text
previous_stable_model

previous_tokenizer

previous_adapter

compatibility_matrix

rollback_trigger

rollback_procedure

rollback_validation
```

因此：

\[
\boxed{
Deployable
\Rightarrow
Rollbackable
}
\]

如果一个模型：

> 只能升级，不能可靠回退，

那它还没有达到成熟发布状态。

---

# 二十一、Resume：训练中断后也必须可恢复

CPT 往往很长。

训练可能因为：

```text
节点故障
网络故障
存储故障
作业超时
人工停止
```

中断。

所以每个 Checkpoint 不只是模型 Weight，

还要尽量保存：

```text
optimizer_state

scheduler_state

global_step

tokens_seen

sampler_state

rng_state

data_shard_position
```

这样才能：

# Resume Training
## 断点续训

真正目标是：

> 恢复后尽量继续原来的训练轨迹，而不是从一个模糊状态重新开始。

所以：

\[
\boxed{
Checkpoint
=
ModelState
+
TrainingState
}
\]

---

# 二十二、核心心智模型 ⑧：Checkpoint 的价值不只是“保存模型”，而是保存决策点和恢复点

每个重要 Checkpoint 同时有三种角色：

```text
Recovery Point
故障恢复点

Evaluation Point
能力评测点

Decision Point
继续/停止/回滚决策点
```

所以：

\[
\boxed{
Checkpoint
=
Recovery
+
Evaluation
+
Decision
}
\]

这也是为什么：

> Checkpoint Policy 必须在训练前定义。

---

# 二十三、训练 Trace：以后必须能回答“这个模型为什么变成现在这样”

一次完整 Run 至少要生成：

# Run Trace
## 训练追踪记录

包含：

```text
run_id

parent_model_id

corpus_version

tokenizer_version

sequence_policy_version

mixture_policy_version

retention_policy_version

training_config_hash

code_commit

environment_id

checkpoint_ids

tokens_seen

observed_mixture

domain_metrics

regression_metrics

sft_run_id

release_candidate_id

release_decision
```

这样以后出现问题时，

不是靠：

> “我记得当时大概这么配的。”

而是可以真正重建：

\[
\boxed{
Decision
\rightarrow
Training
\rightarrow
Checkpoint
\rightarrow
Evaluation
\rightarrow
Release
}
\]

---

# 二十四、真正的 `ProcurementLM_V0.2` 到底是什么？

现在可以给出正式定义：

\[
\boxed{
ProcurementLM\_V0.2
=
BaseModel
+
DomainCPT
+
Retention
+
SFT
+
Evaluation
+
ReleaseGovernance
}
\]

更工程化一点：

\[
\boxed{
ProcurementLM\_V0.2
=
M_{base}
+
D_{CPT}
+
T
+
P_{seq}
+
P_{mix}
+
P_{retention}
+
CPTCheckpoint
+
SFT
+
EvalBundle
+
ReleaseManifest
}
\]

它不是：

> “比 V0.1 多训了一轮”。

而是：

> **第一次形成完整的高级领域适配模型版本。**

---

# 二十五、一个完整的政府采购 CPT Run 示例

假设真实诊断发现：

```text
多个采购任务都存在：
长文档术语理解弱
行业表达不稳定
复杂采购结构建模不足
```

于是：

## Step 1：Domain Gap Diagnosis
### 领域差距诊断

确认：

> 问题不是单一 SFT 行为问题。

---

## Step 2：Corpus Freeze
### 冻结训练语料

形成：

```text
ProcurementCPTCorpus_V0.1
```

完成：

```text
质量过滤
去重
Lineage
Benchmark Firewall
Token统计
```

---

## Step 3：Tokenizer Audit
### 分词器审计

结果：

```text
Keep Existing Tokenizer
```

因为：

> 领域碎片率可接受，修改收益不足以覆盖兼容成本。

---

## Step 4：Sequence Policy
### 序列构造策略

采用：

```text
Section-aware Split
章节优先切分

EOS Boundary
显式文档边界

Length-aware Packing
按长度拼接

Padding Loss Mask
Padding不计Loss
```

---

## Step 5：Mixture
### 数据混合

设计：

```text
Domain Corpus
+
General Replay
```

并控制：

```text
行业比例
高质量桶
重复曝光
Observed Mixture
```

---

## Step 6：Pilot
### 小规模试训

先验证：

```text
Loss趋势
领域PPL
通用回归
Mixture
Resume
```

通过后再进入 Full Run。

---

## Step 7：Full CPT
### 正式继续预训练

持续保存 Checkpoint。

每个 Checkpoint 都执行：

```text
Domain Eval
General Regression
Instruction Regression
Forgetting Curve
```

---

## Step 8：Checkpoint Selection
### 选择领域底座

不是选：

> 最后一个。

而是选：

> 领域收益足够、通用回归仍受控的 Pareto Checkpoint。

---

## Step 9：SFT
### 重新监督微调

在新 CPT 底座上重新训练：

```text
Procurement SFT Dataset
```

恢复 / 强化：

```text
任务Schema
风险分类
结构化输出
拒答
任务行为
```

---

## Step 10：Release Evaluation
### 发布评测

同时检查：

```text
Foundation
Behavior
Regression
Compatibility
Artifact Completeness
```

---

## Step 11：Release Gate
### 发布门槛

全部通过以后：

```text
ProcurementLM_V0.2-RC1
↓
ProcurementLM_V0.2
```

这才算真正完成。

---

# 二十六、第八课最终 10 个工程产物怎样接起来？

第 1 阶段：

```text
ProcurementCPTBoundaryModel_V0.1
```

回答：

> 要不要做 CPT？

第 2 阶段：

```text
ProcurementCPTCorpusPolicy_V0.1
```

回答：

> 什么数据可以进 CPT？

第 3 阶段：

```text
ProcurementTokenizerAudit_V0.1
```

回答：

> Tokenizer 要不要改？

第 4 阶段：

```text
ProcurementCPTObjectivePolicy_V0.1
```

回答：

> Token 怎样组成真实训练任务？

第 5 阶段：

```text
ProcurementCPTMixturePolicy_V0.1
```

回答：

> 每类数据获得多少训练预算？

第 6 阶段：

```text
ProcurementCPTForgettingPolicy_V0.1
```

回答：

> 模型什么时候开始遗忘？

第 7 阶段：

```text
ProcurementCPTRetentionPolicy_V0.1
```

回答：

> 怎样主动控制遗忘？

第 8 阶段：

```text
ProcurementCPTSyntheticCurriculumPolicy_V0.1
```

回答：

> 怎样补覆盖并安排训练难度？

第 9 阶段：

```text
ProcurementCPTSFTDecisionPolicy_V0.1
```

回答：

> 什么时候 CPT、什么时候 SFT、怎样串联？

第 10 阶段：

```text
ProcurementLM_V0.2
```

回答：

> 怎样真正发布一个经过领域适配的模型版本？

所以第八课可以压成：

\[
\boxed{
Decision
\rightarrow
Data
\rightarrow
Tokenizer
\rightarrow
Objective
\rightarrow
Mixture
\rightarrow
Forgetting
\rightarrow
Retention
\rightarrow
Synthetic/Curriculum
\rightarrow
CPT/SFT
\rightarrow
Release
}
\]

---

# 二十七、本阶段最重要的 10 个核心心智模型

> **心智模型 ①：`CPTExperiment ≠ ModelRelease`。训练跑完只是得到实验 Checkpoint，不代表模型可以发布。**

> **心智模型 ②：`ModelRelease ≠ WeightsOnly`。真正模型版本必须包含 Tokenizer、配置、数据血缘、评测证据和 Release Manifest。**

> **心智模型 ③：`NoFrozenBaseline = NoReliableComparison`。没有固定基线，就无法可靠证明模型到底变好还是变坏。**

> **心智模型 ④：`Scale amplifies Signal and Error`。扩大训练规模会同时放大正确方向和错误配置，所以 Full Run 前必须先做 Pilot。**

> **心智模型 ⑤：`BestCheckpoint = MultiObjectiveDecision`。最优发布 Checkpoint 不是 Loss 最低，而是领域收益、通用保持、成本和兼容性的综合折中。**

> **心智模型 ⑥：`TrainingLoss ≠ ReleaseMetric`。Loss / PPL 是训练信号，不是模型发布裁判。**

> **心智模型 ⑦：`Release = GainEvidence + RegressionEvidence`。既要证明学会了新的，也要证明没有把关键旧能力破坏到不可接受。**

> **心智模型 ⑧：`ReleaseCandidate ≠ ReleasedModel`。候选模型必须通过预先定义的 Release Gate 才能晋级正式版本。**

> **心智模型 ⑨：`ModelVersion = ArtifactGraphVersion`。模型版本本质是一整张依赖图，而不是一个权重文件。**

> **心智模型 ⑩：`Deployable ⇒ Rollbackable`。真正可发布的模型必须同时具备明确的回滚路径。**

---

# 二十八、把整门第八课压成一张最终工程图

```text
                        Real Failure Cases
                          真实失败案例
                               │
                               ▼
                       Domain Gap Diagnosis
                         领域差距诊断
                               │
                               ▼
                         CPT Go / No-Go
                         是否进入CPT
                               │
                               ▼
                    Procurement CPT Corpus
                      建设领域训练语料
                               │
                               ▼
                        Tokenizer Audit
                         分词器审计
                               │
                               ▼
                     Sequence Construction
                       构造训练序列
                               │
                               ▼
                    Mixture + Replay Design
                     数据混合与通用回放
                               │
                               ▼
                           Pilot CPT
                         小规模试验训练
                               │
                               ▼
                            Full CPT
                         正式继续预训练
                               │
                               ▼
                     Checkpoint Evaluation
                        周期性检查点评测
                               │
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
          Domain Gain     General Retention   Training Cost
           领域收益          通用能力保持          训练成本
               │               │               │
               └───────────────┼───────────────┘
                               ▼
                       Checkpoint Selection
                         选择CPT底座
                               │
                               ▼
                              SFT
                        重新任务行为对齐
                               │
                               ▼
                       Release Candidate
                          发布候选模型
                               │
                 ┌─────────────┼─────────────┐
                 ▼             ▼             ▼
           Foundation Eval  Behavior Eval  Regression Eval
             底座评测        行为评测         回归评测
                 │             │             │
                 └─────────────┼─────────────┘
                               ▼
                          Release Gate
                           发布门槛
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
                  Reject                 Pass
                   否决                   通过
                                          │
                                          ▼
                               ProcurementLM_V0.2
```

脑中最后只留一句：

> **真正的 CPT 工程，不是“拿政府采购数据继续训练一次”，而是从领域差距诊断开始，用版本化 Corpus、Tokenizer、Sequence、Mixture、Retention 和 Checkpoint 控制训练过程，再通过重新 SFT、分层评测、通用回归、Release Gate 与 Rollback，把一个实验 Checkpoint 变成真正可发布的领域模型。**

---

# 第八课 · 第 10 阶段掌握测试

现在不回看正文，你应该能够解释：为什么 `CPTExperiment ≠ ModelRelease`；为什么发布模型不能只有 Weight；Baseline 为什么必须训练前冻结；Reproducibility 到底要版本化哪些东西；为什么正式 Full Run 前要先做 Pilot；为什么 Scale 会同时放大 Signal 和 Error；Checkpoint 为什么既是恢复点又是评测点和决策点；为什么最终 Checkpoint 不一定最好；为什么 Loss / Perplexity 不能直接决定发布；为什么 CPT 后还要重新 SFT；Foundation、Behavior、Regression 三层评测分别回答什么；为什么 Release Gate 要训练前定义；Release Candidate 和 Released Model 有什么区别；完整 Release Bundle 应该包含哪些资产；为什么模型版本本质上是一张 Artifact Graph；为什么可发布模型必须可回滚；为什么 Checkpoint 还应该保存 Training State；以及 `ProcurementLM_V0.2` 为什么不是“V0.1 多训一轮”，而是一个带完整领域适配、评测和发布治理的模型版本。

如果这些能够完整讲出来：

\[
\boxed{
第八课第10阶段真正掌握
}
\]

---

# 第八课正式完成

到这里：

\[
\boxed{
第八课
=
10/10
}
\]

最终工程交付：

\[
\boxed{
ProcurementLM\_V0.2
}
\]

课程系统演化到：

\[
\boxed{
ProcurementDataset\_V0.1
\rightarrow
ProcurementLM\_V0.1
\rightarrow
ProcurementRAG\_V0.1
\rightarrow
ProcurementAgent\_V0.1
\rightarrow
ProcurementLM\_V0.2
}
\]

下一课正式进入：

# 第九课：Gold Benchmark、评测与可靠性
## 怎样建立 `ProcurementBench_V1`，真正证明模型、RAG、Agent 到底哪里变好了、哪里退化了、能不能上线？

第八课解决的是：

> **怎样把模型本体进一步适配到政府采购领域。**

第九课开始解决：

> **怎样用冻结、可版本化、可切片、可回归的 Gold Benchmark，证明这些提升是真的，而不是训练集记忆、指标幻觉或测试污染。**

---

<!-- LESSON 08 STAGE 10 END -->

