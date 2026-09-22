# 第一课 · 第 7 阶段：模型诊断——Bias、Drift、OOD 与数据污染

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：MEDIUM。** 审计原因：核心心智模型出现偏后，阅读前段缺少认知锚点。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **模型有经验边界，能力必须描述“在哪些分布内经过验证”。**
2. **Label 只是对现实的测量，专家也可能错，分歧本身也是信息。**
3. **模型是某一时刻训练分布的 Snapshot，现实会 Drift。**
4. **可靠系统必须知道什么时候不应该自动回答。**
5. **先诊断再优化，Error Analysis 往往比盲目 Scale 更重要。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `OOD` | 分布外数据：明显偏离训练/验证分布的新输入 |
| `Drift` | 漂移：数据、业务、政策或模型行为分布发生变化 |
| `Split` | 数据切分：按项目/时间/地区划分训练、验证、测试数据 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Counterfactual` | 反事实：改变关键事实，检查正确结论是否应随之变化 |

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

> **原文级教材源文件**：本 Markdown 是该阶段唯一内容源。HTML 由本文件直接生成，不再二次压缩、合并知识点或改写公式。

这一阶段开始从“会训练”进入“会诊断”。当模型效果变差时，不先假设模型不够大，而是系统排查 Data、Label、Split、Distribution、Model、Optimization 与 Deployment。

\[
Diagnosis \ before \ Optimization
\]

重点包括 Data Bias、Label Noise、Distribution Shift、OOD、Data Contamination、Shortcut Learning、Error Taxonomy 与 Root Cause Analysis。

---

## 1. 第七阶段总问题：模型表现差，到底改哪里？

错误可能来自 Data、Label、Split、Distribution、Model、Optimization、Deployment。专家先诊断，再优化。

> **公式 / 关键表达**
>
> Diagnosis before Optimization

---

## 2. 一个错误现象可能有多个原因

“医疗技术参数漏报”可能是医疗数据少、标签错、分布漂移、模型容量不足或解析问题，不能从现象直接跳到结论。

---

## 3. Data Bias

训练数据本身偏向某些项目类型、行业、地区或时间，模型会继承这种经验偏差。

---

## 4. Coverage 比总量更重要

10 万条数据如果 70% 是 IT，也不能代表整个政府采购世界。

---

## 5. Sampling Bias

采集机制使样本不是现实总体的代表。

---

## 6. 投诉案例采样偏差

如果风险样本几乎都来自投诉决定，模型可能学会投诉文件风格，而不是一般采购文件中的风险规律。

---

## 7. Representation Bias

中央/省级文件多、基层县级少，模型可能对基层语言与业务结构陌生。

---

## 8. Model Envelope

专业描述模型能力时，要说明“在哪些分布内经过验证”，而不是笼统说“支持政府采购”。

> **专家心智模型**
>
> 心智模型①：模型永远有经验边界。

---

## 9. Label Bias

Y 本身可能系统性偏差。错误标签会产生错误梯度。

---

## 10. Label Noise

专家误标、边界模糊、数据录入错误都会形成噪声。

---

## 11. 专家分歧

不同专家对“5个同类业绩”可能有不同判断，说明任务本身带不确定性。

---

## 12. 不要把分歧硬压成 0/1

可以保存 expert_votes、ambiguity、confidence 等字段。

---

## 13. Adjudication

模型与标签冲突时应复核：模型错、专家错、还是案例本身有争议。

---

## 14. Ground Truth 不是绝对真理

专业标签是当前专家体系对现实的最佳测量。

> **专家心智模型**
>
> 心智模型②：Label 也是测量结果。

---

## 15. Distribution Shift

训练分布和部署分布不同。

---

## 16. Covariate Shift

P(X) 变了，但 P(Y|X) 大致不变。例：IT 比例下降、医疗比例上升。

---

## 17. Label Shift

P(Y) 变了。例：行业规范后真实风险比例明显下降。

---

## 18. Concept Drift

P(Y|X) 变了。例：新法规改变同一条款的适用结论。

---

## 19. 时间维度是政府采购核心风险

规则会更新，模型必须知道“什么时候有效”。

---

## 20. 法规元数据

document_id、jurisdiction、publish/effective/expiry date、status、supersedes 等应进入知识系统。

---

## 21. 模型是分布快照

训练好模型可以看成某一时刻 P_train 的 Snapshot。现实持续变化，因此必须监控。

> **专家心智模型**
>
> 心智模型③：模型不是永久有效。

---

## 22. OOD：Out-of-Distribution

新输入远离训练分布时，模型缺少直接经验。

---

## 23. 流畅回答不代表 In Distribution

LLM 在 OOD 上也可能非常流畅甚至高置信度。

---

## 24. Abstention

可靠系统应在低置信、OOD、证据不足时拒绝给确定结论或转人工。

---

## 25. Selective Prediction

只自动处理模型足够可靠的一部分问题。

---

## 26. 专业 AI 的能力边界意识

会判断 + 会怀疑 + 会拒答，比“什么都敢回答”更适合高风险领域。

> **专家心智模型**
>
> 心智模型④：知道自己不会也是能力。

---

## 27. Data Contamination

Test 内容已经进入 Train，导致离线成绩虚高。

---

## 28. Exact Duplicate 污染

完全相同样本同时出现在 Train/Test。

---

## 29. Near Duplicate 污染

只换数字、名称或同义改写，也可能造成严重泄漏。

---

## 30. Project Leakage

同一项目不同文件分到 Train/Test，项目身份和答案相互泄漏。

---

## 31. Template Leakage

同一家代理机构大量高度一致模板随机拆分，会把模板记忆当成泛化。

---

## 32. Institution Leakage

采购人/代理机构身份本身可能成为捷径，应设计跨机构评测。

---

## 33. Future Leakage

用后续投诉、更正、中标信息预测发布时风险，是“用未来预测过去”。

---

## 34. False Confidence

污染最大的危害是让团队误以为模型已经足够好。

---

## 35. Spurious Correlation

模型利用业务上不正确、但训练数据里好用的特征。

---

## 36. Counterfactual Test

只改变关键词或关键条件，看模型判断是否按业务逻辑变化。

---

## 37. Perturbation Test

保持语义基本不变，改写表达。如果性能暴跌，说明表面词汇依赖严重。

---

## 38. Train/Val 第一层诊断

Train差+Val差：欠拟合/数据/优化；Train好+Val差：过拟合/分布差；Val好+线上差：漂移/污染/Serving skew。

---

## 39. Slice Evaluation 第二层诊断

总体 90% → 技术参数 68% → 医疗技术 52% → 边界案例 37%，逐层定位错误区域。

---

## 40. Confidence × Correctness

高置信度错误是最高优先级；低置信度错误更多是模型诚实地犹豫。

---

## 41. 人工错误归因

输入缺信息、标签错、法规过期、知识缺失、语义理解错、复杂推理错、OOD、长上下文丢失等。

---

## 42. Error Analysis > 盲目 Scale

先知道错误来自哪里，再决定加数据、修标签、加 RAG、换模型还是改训练。

---

## 43. 模块化诊断

Parser→Risk Detector→Classifier→Retriever→Reasoner→Citation Validator→Suggestion Generator，最终错时要能定位层级。

---

## 44. Error Taxonomy

系统错误必须可归因，而不是“AI 有时就是会错”。

> **专家心智模型**
>
> 心智模型⑤：先诊断再优化。

---

## 45. Controlled Experiment

一次主要改一个变量，才能知道提升来自哪里。

---

## 46. Hypothesis-driven Diagnosis

提出“医疗表现差是数据覆盖不足”假设→补医疗数据→重新评测→验证或否定。

---

## 47. 诊断案例：医疗技术参数

若资格 Recall 90%、评分82%、技术42%，再查训练分布发现医疗技术只有700条，优先补 Coverage，而不是立即换70B。

---

## 48. 诊断案例：法规依据错

风险判断95%但引用准确61%，优先优化 RAG/Metadata/Reranker，而不是继续训练分类能力。

---

## 49. 第七阶段五个心智模型

模型有经验边界；标签是测量；模型是分布快照；可靠系统要能拒答；先诊断再优化。

---

## 50. 阶段掌握标准

看到线上掉点时，你应先问错误集中在哪里、Train/Val 是否正常、分布/标签/污染/OOD/Drift 哪一层最可疑。

---

---

## 51. 三种 Distribution Shift 再做一次严格区分

Covariate Shift：\(P(X)\) 变了，例如 IT 项目从 70% 变成医疗项目 60%，但同一 X 的判定机制大致没变。Label Shift：\(P(Y)\) 变了，例如行业规范后风险条款占比从 20% 降到 5%。Concept Drift：\(P(Y|X)\) 变了，例如新规实施后同一做法对应的合规结论改变。

三者修复方式不同：Covariate 更偏覆盖与采样；Label Shift 可能需要重新调阈值；Concept Drift 往往需要更新知识、规则、标签甚至重新训练。

## 52. OOD 最大的危险：模型不一定知道自己没见过

流畅输出并不能证明样本在训练分布内。一个几乎没见过特殊科研设备的模型，仍可能非常自信地生成完整理由。成熟系统应该把 OOD Score、领域覆盖和证据充分性放进决策策略，必要时 Abstain。

## 53. 专业系统的 Abstention 不是失败，而是能力边界管理

可靠输出可以是：“当前项目与训练/案例库常见项目差异较大；缺少专项市场数据和足够相似案例；当前置信度低，建议专家复核。”

\[
Predict+EstimateUncertainty+DetectOOD+Abstain
\]

比“什么都敢判”更适合高影响专业场景。

## 54. Data Contamination 的三个层次

Exact Duplicate：Test 原句出现在 Train；Near Duplicate：只换措辞或数字；Project Leakage：同一采购项目的其他文书进入 Train。还可能有 Template Leakage、机构泄漏和 Future Leakage。

污染最危险之处不是分数高，而是制造 False Confidence，让团队误以为模型已具备上线能力。

## 55. Counterfactual / Perturbation Test 用来找 Shortcut

保持语义基本不变只换措辞，如果预测大变，说明模型过度依赖表面词汇；保留关键词但改变语义，如果预测不变，说明模型可能没有理解上下文。

例如“注册资本不得低于5000万元”和“采购文件不得以注册资本作为不合理限制条件”都含“注册资本”，但业务方向相反。

## 56. 四层 Diagnosis 工作流

第一层看 Train/Validation；第二层做 Slice Evaluation；第三层看 Confidence × Correctness，优先 High-Confidence Wrong；第四层让专家对错误做 Root Cause 标注。

只有把错误定位到具体 Slice 和根因，才能决定下一步是加数据、修标签、加 RAG、改 Parser、换模型还是调训练。

## 57. 一个完整医疗技术参数诊断案例

线上客户反馈医疗项目漏报多。总体 Recall 91% 并不能否认问题。先切医疗 Recall=61%；再切资格 90%、评分 82%、技术参数 42%；再查训练集发现医疗技术参数只有 700/20,000。

错误集中于专用设备兼容性、临床场景和市场替代信息。此时主要根因是 Data Coverage，而不是 Model Capacity。补充医疗 Normal/Hard Positive/Hard Negative 和专家案例后再评测，才是诊断驱动训练。

## 58. 模块化诊断：最终答案错不等于 LLM 本身错

生产系统可以拆为 Document Parser → Risk Detector → Classifier → Retriever → Reasoner → Citation Validator → Suggestion Generator。若风险判断正确但法律依据错，应优先修 Retriever/法规 Metadata，而不是继续 Fine-tune 风险分类器。

## 59. Error Taxonomy 应该成为结构化资产

至少保存 error_type、root_cause、domain、difficulty、confidence、ood_score、label_review、recommended_action。这样“模型错了”才能转化为下一轮具体的数据和实验计划。

## 60. Controlled Experiment：一次不要同时改十件事

若一次同时换模型、加数据、改 LR、改 Prompt、换 Loss、加 RAG，即使 F1 提高，也不知道哪个因素有效。成熟研发使用 Hypothesis → Experiment → Measurement → Diagnosis → Next Hypothesis。

## 61. 第七阶段五个核心心智模型

1. 模型有经验边界，能力必须描述“在哪些分布内经过验证”。
2. Label 只是对现实的测量，专家也可能错，分歧本身也是信息。
3. 模型是某一时刻训练分布的 Snapshot，现实会 Drift。
4. 可靠系统必须知道什么时候不应该自动回答。
5. 先诊断再优化，Error Analysis 往往比盲目 Scale 更重要。

---
