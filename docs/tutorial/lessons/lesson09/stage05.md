# 第九课 · 第 5 阶段
# Generation Evaluation：理由、引用、事实性、幻觉与 Groundedness
## 生成答案“看起来很专业”，到底怎样证明它事实正确、有证据、没有幻觉，而且真正回答了问题？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **FluentAnswer ≠ CorrectAnswer。语言流畅和事实正确是两个不同维度。**
2. **ReferenceSimilarity ≠ SemanticCorrectness。文本重合度不能替代语义正确性。**
3. **Factuality ≠ Groundedness。事实可能是真的，但当前证据未必支持。**
4. **AnswerLevelEval 应尽可能拆到 ClaimLevelEval，否则很难定位幻觉。**
5. **CitationPresent ≠ CitationCorrect，而 CitationCorrect ≠ CitationComplete。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Citation` | 引用：把生成结论和具体来源建立可追踪链接 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `Generalization` | 泛化：对未见项目、时间、地区和表达的有效能力 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |

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

分类任务的答案空间有限。

但生成任务不同。

同一个正确答案可以有很多种表达。

所以生成评测不能简单依赖：

```text
Exact Match
```

最危险的情况是：

> 模型语言非常流畅、专业术语很多、格式也很好，但事实和证据是错的。

因此本阶段第一条边界：

\[
\boxed{
FluentAnswer
\neq
CorrectAnswer
}
\]

本阶段最终形成：

# `ProcurementGenerationEvalPolicy_V0.1`

---

# 一、生成评测为什么比分类难？

分类：

```text
Gold = 风险
Pred = 风险
```

比较直接。

生成：

```text
Gold：
该条款存在潜在地域限制风险……

Pred：
从履约便利性角度看，该要求具有一定合理性……
```

需要判断：

```text
结论
事实
理由
证据
完整性
引用
不确定性
任务遵循
```

所以：

\[
\boxed{
GenerationEval
=
MultiDimensionalJudgment
}
\]

---

# 二、核心心智模型 ①
# `ReferenceSimilarity ≠ SemanticCorrectness`

传统 NLP 常用：

```text
BLEU
ROUGE
```

这些指标衡量：

> 文本表面重合度。

但在高自由度生成任务里：

一个答案和 Gold 用词不同，

仍可能完全正确。

反过来：

一个答案和 Gold 很像，

也可能在关键事实处错了一句。

所以：

\[
\boxed{
LexicalOverlap
\neq
Truth
}
\]

---

# 三、生成评测至少拆成哪些维度？

建议至少：

```text
Task Correctness
任务结论正确性

Factuality
事实正确性

Groundedness
证据支撑度

Completeness
完整性

Relevance
相关性

Citation Correctness
引用正确性

Citation Completeness
引用覆盖度

Instruction Following
指令遵循

Abstention Quality
拒答质量

Style / Clarity
表达清晰度
```

注意：

> Style 应该放在较后层。

因为：

\[
\boxed{
PrettyWriting
不能补偿
FalseFacts
}
\]

---

# 四、Factuality 和 Groundedness 有什么区别？

# Factuality
## 事实正确性

问：

> 这句话本身是否符合真实事实？

# Groundedness
## 证据支撑度

问：

> 这句话是否被当前提供的证据支持？

例如某句话：

> 在现实中可能是真的，

但当前 RAG Context 没有提供这个事实。

那么：

```text
Factuality = 可能正确
Groundedness = 不充分
```

所以：

\[
\boxed{
Factuality
\neq
Groundedness
}
\]

---

# 五、核心心智模型 ②
# `TrueButUngrounded` 仍然可能是系统风险

在要求：

> 基于指定采购文件回答

的任务中，

模型即使凭记忆说了一个真实知识，

也可能违反：

> 只能基于文档证据回答。

所以：

\[
\boxed{
TaskTruth
=
WorldTruth
+
EvidenceConstraint
}
\]

在 Grounded QA 里，

证据边界本身就是任务定义的一部分。

---

# 六、Claim-level Evaluation：为什么要把答案拆成 Claim？

一段生成答案可能包含 8 个断言。

如果只给整段：

```text
overall = 0.8
```

很难定位哪里错。

更专业的是：

# Claim Decomposition
## 断言拆解

例如：

```text
Claim 1：该条款限制供应商注册地
Claim 2：该限制与履约必要性缺乏关联
Claim 3：因此属于高风险
```

然后逐条评：

```text
Supported?
Contradicted?
NotEnoughEvidence?
```

所以：

\[
\boxed{
AnswerLevelEval
可以进一步拆成
ClaimLevelEval
}
\]

---

# 七、Hallucination 怎么定义？

在评测里不要只写：

> “有幻觉。”

要做 Taxonomy。

例如：

```text
Unsupported Claim
无证据断言

Contradicted Claim
与证据矛盾

Fabricated Citation
伪造引用

Wrong Attribution
错误归因

Invented Number
编造数字

Invented Policy
编造政策

Overgeneralization
过度泛化
```

所以：

\[
\boxed{
Hallucination
不是单一错误类型
}
\]

---

# 八、核心心智模型 ③
# `Hallucination Rate` 必须知道“幻觉是什么”

如果不同团队对 Hallucination 定义不同，

那么：

```text
Hallucination Rate = 3%
```

没有可比性。

所以：

\[
\boxed{
MetricDefinition
先于
MetricValue
}
\]

---

# 九、Citation Correctness：引用“存在”不等于引用“正确”

可以拆成：

```text
Citation Presence
有没有引用

Citation Validity
引用是否指向真实来源

Citation Entailment
引用内容是否真的支持结论

Citation Location
引用定位是否正确
```

所以：

\[
\boxed{
CitationPresent
\neq
CitationCorrect
}
\]

---

# 十、Citation Completeness：有些关键结论根本没引证

一个回答可能：

```text
第一段有引用
第二段有三个关键结论但没有引用
```

这时：

> Citation Correctness 可能很高，

但：

> Citation Completeness 很差。

所以：

\[
\boxed{
CorrectCitation
\neq
CompleteCitationCoverage
}
\]

---

# 十一、Reason Quality：理由怎么评？

理由评测至少可以看：

```text
Logical Consistency
逻辑一致

Evidence Use
是否使用证据

Causal Validity
因果是否合理

Rule Application
规则适用是否正确

Boundary Awareness
是否意识到条件边界
```

一个看起来很长的 Explanation：

> 不代表 Reason Quality 高。

---

# 十二、核心心智模型 ④
# `LongExplanation ≠ GoodReasoning`

模型很容易生成：

> 很长、很顺、很专业的解释。

但真正评测应该问：

```text
有没有错误前提？
有没有证据跳跃？
有没有把相关性当因果？
有没有忽略关键上下文？
```

所以：

\[
\boxed{
ReasoningQuality
需要结构化Rubric
}
\]

---

# 十三、LLM-as-a-Judge 能不能用？

可以。

# LLM-as-a-Judge
## 使用大模型做评测裁判

优点：

```text
便宜
可扩展
能处理开放式文本
```

风险：

```text
Judge偏差
偏好长答案
偏好某种写作风格
自我偏好
Prompt敏感
模型版本变化
```

所以：

\[
\boxed{
LLMJudge
\neq
GroundTruth
}
\]

---

# 十四、怎样让 LLM Judge 更可靠？

至少：

```text
固定Judge Model
固定Judge Prompt
固定Temperature
固定Rubric
给Gold Evidence
要求逐维度评分
做Human Calibration
定期抽检
```

并记录：

```text
judge_model_version
judge_prompt_version
rubric_version
```

---

# 十五、核心心智模型 ⑤
# `LLM Judge` 是可扩展评测器，不是最终真相来源

最适合的定位：

> 程序规则和人工专家之间的扩展层。

可以采用：

```text
Programmatic Checks
+
LLM Judge
+
Human Audit
```

形成：

# Hybrid Evaluation
## 混合评测

---

# 十六、Pairwise Evaluation 为什么经常比绝对打分稳定？

让 Judge 判断：

```text
A = 8.2
B = 8.5
```

有时很不稳定。

但问：

> A 和 B 哪个更好？

通常更容易。

这叫：

# Pairwise Evaluation
## 成对比较

适合：

```text
模型版本比较
Prompt版本比较
生成质量比较
```

但也要防：

```text
Position Bias
顺序偏差
```

所以可以：

> A/B 和 B/A 都跑。

---

# 十七、Abstention 也属于生成质量

如果证据不足，

模型应该：

```text
无法从当前材料可靠判断
```

而不是：

> 自信补全。

所以：

\[
\boxed{
GoodGeneration
包括
KnowingWhenNotToGenerate
}
\]

这会在第 9 阶段进一步展开。

---

# 十八、Generation Rubric 示例

可以设计：

| 维度 | 0 | 1 | 2 |
|---|---|---|---|
| 结论 | 错 | 部分正确 | 正确 |
| 事实 | 多处错误 | 小瑕疵 | 无关键错误 |
| Groundedness | 无证据 | 部分支持 | 充分支持 |
| 引用 | 错/伪造 | 部分正确 | 正确完整 |
| 完整性 | 严重缺失 | 基本完整 | 完整 |
| 指令遵循 | 明显违反 | 小偏差 | 完全遵循 |

然后再配：

> Critical Error Gate。

例如：

```text
Fabricated Policy = Critical
Fabricated Citation = Critical
```

---

# 十九、核心心智模型 ⑥
# `RubricScore` 不能掩盖 Critical Hallucination

即使：

```text
总分 = 9/10
```

但如果出现：

> 编造政策依据，

仍然可能：

\[
\boxed{
ReleaseFail
}
\]

所以：

\[
\boxed{
AverageQuality
\neq
CriticalSafety
}
\]

---

# 二十、本阶段正式工程产物
# `ProcurementGenerationEvalPolicy_V0.1`

第一版至少锁定：

```text
generation_eval_policy_version

task_correctness_rubric

factuality_rubric

groundedness_rubric

completeness_rubric

relevance_rubric

citation_correctness_rubric

citation_completeness_rubric

instruction_following_rubric

abstention_rubric

claim_decomposition_policy

hallucination_taxonomy

critical_hallucination_policy

judge_type

judge_model_version

judge_prompt_version

pairwise_eval_policy

human_audit_rate

release_gate
```

每个生成样本至少记录：

```text
item_id

gold_answer
gold_evidence

model_answer

claims

claim_support_status

dimension_scores

hallucination_codes

citation_scores

judge_metadata

critical_error

final_status
```

---

# 二十一、本阶段最重要的 9 个核心心智模型

> **心智模型 ①：`FluentAnswer ≠ CorrectAnswer`。语言流畅和事实正确是两个不同维度。**

> **心智模型 ②：`ReferenceSimilarity ≠ SemanticCorrectness`。文本重合度不能替代语义正确性。**

> **心智模型 ③：`Factuality ≠ Groundedness`。事实可能是真的，但当前证据未必支持。**

> **心智模型 ④：`AnswerLevelEval` 应尽可能拆到 `ClaimLevelEval`，否则很难定位幻觉。**

> **心智模型 ⑤：`CitationPresent ≠ CitationCorrect`，而 `CitationCorrect ≠ CitationComplete`。**

> **心智模型 ⑥：`LongExplanation ≠ GoodReasoning`。解释长度不能代表推理质量。**

> **心智模型 ⑦：`LLMJudge ≠ GroundTruth`。LLM Judge 是扩展评测器，不是最终真相来源。**

> **心智模型 ⑧：`GoodGeneration` 包括正确拒答，知道什么时候不回答也是能力。**

> **心智模型 ⑨：`RubricScore ≠ CriticalSafety`。高平均分不能掩盖编造政策、伪造引用等关键失败。**

---

# 二十二、下一阶段：第九课 · 第 6 阶段
# RAG Evaluation：Retrieval、Ranking、Context、Generation 分层评测

最关键的边界：

\[
\boxed{
RAGFailure
\neq
LLMFailure
}
\]

并建立：

# `ProcurementRAGEvalPolicy_V0.1`

---
