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
