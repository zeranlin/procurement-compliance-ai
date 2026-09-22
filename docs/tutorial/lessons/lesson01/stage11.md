# 第一课 · 第 11 阶段：不确定性、校准、选择性预测与风险控制

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：MEDIUM。** 审计原因：核心心智模型出现偏后，阅读前段缺少认知锚点。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **答案和对答案的自知能力是两种不同能力。**
2. **不确定性要区分问题本身不确定与模型知道得不够。**
3. **Accuracy 与 Calibration 必须分别评估和优化。**
4. **拒答、补信息、转专家是专业系统能力，不是失败。**
5. **最终目标是最小化高代价业务错误，而不是最大化模型自信或自动化率。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Calibration` | 校准：使模型置信度更接近实际正确率 |
| `OOD` | 分布外数据：明显偏离训练/验证分布的新输入 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `Accuracy` | 准确率：全部样本中判断正确的比例 |
| `Threshold` | 阈值：把连续分数转成业务动作的决策门槛 |
| `Embedding` | 嵌入：把离散 Token 映射到连续高维向量 |
| `Temperature` | 温度：控制采样分布平滑程度和随机性 |

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

这一阶段研究模型的“自知能力”：答案正确与否是一种能力，知道自己的答案是否值得相信是另一种能力。

\[
Prediction \rightarrow Confidence \rightarrow Calibration \rightarrow Uncertainty \rightarrow OOD \rightarrow Abstention \rightarrow RiskControl
\]

重点包括概率校准、Aleatoric/Epistemic Uncertainty、Selective Prediction、Risk-Coverage、Decision Policy 与高代价错误控制。

---

## 1. 第十一阶段总问题：什么时候值得相信模型？

专业系统不仅追求答对，还要知道什么时候不应该完全相信自己的答案。

---

## 2. 从风险分数开始

RiskScore=.92 首先只是模型分数，不自动等于“现实中92%违规”。

---

## 3. Calibration

如果模型说 80% 的一组样本，长期真的约 80% 为正类，才叫校准良好。

---

## 4. Accuracy ≠ Calibration

两个准确率同为90%的模型，一个可能总给0.99而明显过度自信。

---

## 5. Overconfidence

模型概率比真实正确率系统性更极端。

---

## 6. Underconfidence

模型其实经常答对，却总给很保守分数。

---

## 7. 为什么政府采购需要 Calibration

概率可能参与人工复核优先级、自动化区间和风险排序。

---

## 8. 答案与把握程度是两种能力

Prediction + Confidence + Evidence + Uncertainty 应逐步分开表示。

> **专家心智模型**
>
> 心智模型①：做对和知道自己可能错，是不同能力。

---

## 9. Probability / Confidence / Certainty

数学概率、模型自信和现实是否确定不是同一个概念。

---

## 10. Aleatoric Uncertainty

问题本身带不可约不确定性。

---

## 11. 政府采购中的 Aleatoric

“5个同类业绩是否合理”在缺少项目规模、市场竞争和必要性时可能本来就无唯一答案。

---

## 12. Epistemic Uncertainty

模型因为经验/知识不足而不确定，理论上可通过更多数据、知识或更好模型降低。

---

## 13. Epistemic 例子

模型没见过核设施特殊采购，属于认知边界。

---

## 14. 信息不足与模型不足要区分

缺现实信息时应 Ask for More Information，而不是盲目加参数。

> **专家心智模型**
>
> 心智模型②：先判断不确定性来自世界还是模型。

---

## 15. Reliability Diagram

把预测分箱，比较平均预测概率与真实正类比例。

---

## 16. 高置信区过度自信

模型说90%，实际只有72%，说明高分区域校准差。

---

## 17. ECE

Expected Calibration Error 衡量分箱后预测概率与实际频率的偏差。

---

## 18. Brier Score

平均 (p−y)²，衡量概率预测质量。

---

## 19. 为什么 Precision/Recall 不够

它们依赖某个 Threshold，把 p=.51 与 p=.99 都压成同一个类别。

---

## 20. Ranking / Classification / Calibration 三层

排序能力、阈值分类能力、概率可信度应分别评估。

---

## 21. 排序好但概率不可信

风险分数都比正常高，但所有概率整体偏高，仍然可能校准差。

---

## 22. Platt Scaling

训练后用简单概率映射重新校准。

---

## 23. Isotonic Regression

非参数单调校准方法，适合某些数据规模。

---

## 24. Temperature Scaling

深度模型常见，用温度 T 调整 logit 的尖锐程度。

> **公式 / 关键表达**
>
> Softmax(z/T)

---

## 25. 校准不等于重新训练分类能力

类别排序可不变，但概率更符合真实频率。

---

## 26. 准确性和可信度要分别优化

Correct + Well Calibrated 才适合进入风险策略。

> **专家心智模型**
>
> 心智模型③：高 Accuracy 不能替代 Calibration。

---

## 27. Selective Prediction

模型只在足够可靠时自动回答，不可靠时 Abstain。

---

## 28. 为什么拒答是一种能力

70% 自动处理、97% 准确 + 30% 人工，可能比100%自动、85%准更有价值。

---

## 29. Coverage

模型自动处理多少比例的问题。

---

## 30. Risk

在自动处理部分里的错误率。

---

## 31. Coverage ↔ Reliability Trade-off

覆盖越高，通常不得不接更多难例；降低 Coverage 可以降低风险。

---

## 32. Risk-Based Automation Zones

高可信自动提示；中等可信专家确认；低可信/OOD 直接人工。

---

## 33. 不能只看单一 Confidence

真正系统可信度还要结合 OOD、Evidence、Context Completeness、Rule Consistency。

---

## 34. System Confidence ≠ Model Probability

模型0.97但无相关法规、OOD=.92，系统仍应谨慎。

---

## 35. 可信度向量

可以分别记录 Model、Retrieval、Evidence、Context、Distribution 的置信度。

---

## 36. OOD 检测思路

Embedding 距离、最近邻、模型分歧、Entropy、专门 Detector、元数据超范围。

---

## 37. Embedding 距离直觉

新样本远离训练样本云，说明分布外风险更高。

---

## 38. 模型分歧是 Uncertainty Signal

A/B/C 模型意见差异大时，优先人工复核。

---

## 39. Ensemble / MC Dropout 直觉

多次略有差异预测非常不稳定，说明认知不确定性高。

---

## 40. LLM 的不确定性是多维的

分类、引用、推理、建议都可以各自有 Confidence。

---

## 41. 分类对但依据错

Risk 判断稳定不代表法规引用可靠，因此 Citation Confidence 要独立。

---

## 42. Uncertainty-aware AI

输出中应说明当前缺少哪些事实和为什么不能形成确定结论。

---

## 43. 答案成立的条件

专业 AI 应输出 Conclusion | Assumptions，而不是无条件断言。

> **专家心智模型**
>
> 心智模型④：答案应带条件和证据边界。

---

## 44. Conditional Prediction

“若市场调查显示只有极少数供应商满足，则风险上升；若有充分必要性证明，则风险下降。”

---

## 45. Risk Control 的目标

模型不可能零错误，目标是降低高代价错误穿透业务流程的概率。

---

## 46. Defense in Depth

模型→RAG验证→规则→专家，多道防线让单次模型错误不必直接变最终错误。

---

## 47. 多信号一致才自动高风险

ModelScore、EvidenceScore、OOD、Rule Match 共同决定 Action。

---

## 48. Model 与 Decision Policy 分离

模型输出 Score；Policy 根据 Score+Evidence+OOD+Cost 决定行动。

> **公式 / 关键表达**
>
> Action=f(Prediction,Uncertainty,Evidence,Cost)

---

## 49. 同一分数在不同业务动作中意义不同

普通提示可容忍较低门槛，自动否定供应商资格则需要极高标准和人工监督。

---

## 50. Cost-sensitive Risk Control

自动化权限越高，所需可靠性、证据和人工监督越高。

---

## 51. 自动化阶梯

信息检索→风险提示→修改建议→推荐结论→自动执行，风险逐层升高。

---

## 52. 政府采购更适合 Decision Support

高影响场景不应把模型当最终责任主体。

---

## 53. Error Budget

例如 Critical FN Rate<1%，超出预算就暂停自动化或降级。

---

## 54. Abstention Threshold 也要评估

Coverage90%但CriticalError4%可能不如Coverage65%且0.5%。

---

## 55. Risk-Coverage Curve

展示自动化覆盖率与自动处理错误率之间的关系。

---

## 56. 最安全的自动化程度

目标不是自动化越多越好，而是 Expected Business Risk↓、Efficiency↑。

> **专家心智模型**
>
> 心智模型⑤：优化高代价错误，而不是模型自信。

---

## 57. Value of Information

当前不确定时，系统应告诉用户下一条什么信息最能降低不确定性。

---

## 58. VoI 与 Active Learning

一个问“下一个标哪个样本”，一个问“当前案例补什么信息”，本质都是最大化信息增益。

---

## 59. 第十一阶段五个心智模型

答案与自知分离；区分两类不确定性；Accuracy与Calibration分离；选择性预测；优化业务风险。

---

## 60. 阶段掌握标准

看到 RiskScore=.98 的陌生医疗项目时，你应追问：校准过吗、OOD吗、领域覆盖、上下文、RAG证据、规则冲突、业务代价、是否应该转人工。

---

---

## 61. “模型给 0.92”到底能不能读成“92%概率有风险”

不能自动这样解释。0.92 首先只是当前模型在当前分布下的输出分数。只有经过 Calibration，并且确认当前数据与校准集足够相似，才更有资格把它当成近似现实概率使用。

## 62. 一个直观 Calibration 例子

从历史预测中找 100 个分数约 0.8 的案例。如果长期真实正类比例也约 80%，模型在这个区间校准较好；如果真实只有 55%，说明明显 Overconfidence。

Accuracy 高与 Calibration 好是两个独立维度。

## 63. Reliability Diagram、ECE 与 Brier Score

Reliability Diagram 比较每个置信度桶的平均预测与真实发生率；ECE 把这些偏差汇总成一个校准误差；Brier Score 计算概率预测的平方误差。它们都在回答分类 Accuracy 无法回答的问题：**概率值本身是否可信。**

## 64. Aleatoric 与 Epistemic Uncertainty

Aleatoric：问题本身或现有事实就存在不可约不确定性，例如缺少市场供应数据，专家也无法唯一判断。Epistemic：模型知识不足，例如从未见过某特殊设备领域；补数据、知识或模型可能降低。

诊断不确定性时必须先问：缺的是模型能力，还是现实信息？

## 65. Selective Prediction：模型不需要每题都自动回答

模型可以只处理自己最可靠的 70%，剩下 30% 转人工。若这 70% Accuracy=97%，对政府采购可能比 100% 自动化但 Accuracy=85% 更有价值。

核心 Trade-off 是 Coverage 与 Risk。

## 66. Risk-Coverage Curve

随着自动化门槛提高，Coverage 通常下降、自动处理错误率下降。业务可以明确选择：例如自动 60% 但 Critical Error<1%，而不是追求 100% 自动处理。

这让“自动化率”从宣传数字变成可治理的风险参数。

## 67. System Confidence 不等于 Model Probability

可以综合：Model Confidence、OOD、Evidence Quality、Context Completeness、Rule Consistency。即使模型 p=0.97，如果 OOD 高、RAG 没找到有效证据、上下文残缺，系统也应该降级为人工复核。

## 68. 多维置信度向量

\[
C=[C_{model},C_{retrieval},C_{evidence},C_{context},C_{distribution}]
\]

生成式系统还可以分别评估 classification、citation、reasoning 和 suggestion 的可信度，因为“判断对”与“依据对”并不是同一件事。

## 69. Decision Policy 与 Model 必须分离

\[
f_\theta(X)\rightarrow Score
\]

而业务动作由：

\[
Action=g(Score,Uncertainty,Evidence,Cost)
\]

同一个 0.75 分数，在“提示专家多看一眼”和“自动否定供应商资格”两个场景中显然不能采取同样动作。

## 70. Defense in Depth：让单个模型错误不直接穿透到高影响决策

风险模型 → 法规 RAG → Rule Engine → 专家复核可以形成多道防线。高风险自动标记甚至可以要求 ModelScore、EvidenceScore、OOD、规则一致性同时达到标准，否则自动降级。

## 71. Error Budget 与风险门禁

可以提前定义 Critical FN Rate 的最大允许值。如果超过阈值，停止某类自动化并转人工，而不是继续运行等待更多事故。专业 AI 的目标不是零错误，而是让高代价错误难以穿透系统。

## 72. Value of Information：不知道时下一步应该问什么

“不确定”不应只是结束语。系统可以指出降低不确定性最有价值的信息：项目规模、市场可满足品牌数、技术参数必要性、替代方案、同类采购情况等。

Active Learning 问“下一条该标哪个案例”，Value of Information 问“当前案例下一步该补什么事实”，二者都在最大化信息增益。

## 73. 第十一阶段五个核心心智模型

1. 答案和对答案的自知能力是两种不同能力。
2. 不确定性要区分问题本身不确定与模型知道得不够。
3. Accuracy 与 Calibration 必须分别评估和优化。
4. 拒答、补信息、转专家是专业系统能力，不是失败。
5. 最终目标是最小化高代价业务错误，而不是最大化模型自信或自动化率。

如果只记一句：

\[
\boxed{可靠模型不仅要尽量答对，还要知道什么时候自己的答案不值得被完全相信。}
\]

---
