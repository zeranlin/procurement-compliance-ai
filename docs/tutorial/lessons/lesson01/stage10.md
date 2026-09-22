# 第一课 · 第 10 阶段：Production ML——监控、反馈与持续学习

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：MEDIUM。** 审计原因：核心心智模型出现偏后，阅读前段缺少认知锚点。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **上线才是真实考试，离线 Test 只是模拟。**
2. **生产质量由完整系统决定，不由单个 LLM 决定。**
3. **必须主动监控沉默的 FN，而不是只看报警项。**
4. **专家不是失败兜底，而是持续学习系统的一部分。**
5. **每个新模型都默认可能退化，必须 Shadow/Canary/Regression/Rollback。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Observe` | Observe/观察：读取当前状态和工具结果 |
| `Drift` | 漂移：数据、业务、政策或模型行为分布发生变化 |
| `Recall` | 召回率：真实风险中被系统成功找出的比例 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Rollback` | 回滚：出现问题时恢复上一稳定系统版本 |
| `Canary` | 灰度发布：让有限真实流量先使用新版本 |

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

这一阶段进入 Production ML。上线不是结束，而是模型第一次进入真实数据分布。核心闭环是：

\[
Train \rightarrow Deploy \rightarrow Observe \rightarrow Feedback \rightarrow Retrain \rightarrow Redeploy
\]

重点包括 Training-Serving Skew、线上监控、Human-in-the-Loop、Drift、Retraining Trigger、Shadow、Canary、Rollback、持续学习与灾难性遗忘。

---

## 1. 第十阶段总问题：上线后是不是训练结束？

不是。Production ML 的核心是持续观察真实世界、收集反馈、发现漂移、再训练和安全发布。

---

## 2. Continuous ML Lifecycle

Train→Deploy→Observe→Fail→Feedback→Retrain→Redeploy。

---

## 3. 上线才是真实考试

Test 只是现实模拟，Production 才面对 P_real(X,Y)。

> **专家心智模型**
>
> 心智模型①：离线高分不是终点。

---

## 4. 为什么线上会比离线差

输入格式、行业比例、法规、解析器、RAG、Prompt、Serving 环境都可能变化。

---

## 5. Training-Serving Skew

训练时和线上推理时的数据处理方式不一致。

---

## 6. Parser Skew 案例

训练文本结构清晰，线上 PDF 解析丢表格/标题错位，X_serve 与 X_train 已不同。

---

## 7. 系统表现由整个 Pipeline 决定

Quality≈DataPipeline×Model×Retrieval×Rules×Serving。

> **专家心智模型**
>
> 心智模型②：不要把所有线上错误都归因于 LLM。

---

## 8. Production Monitoring 五层

System + Data + Model + Business + Human Feedback。

---

## 9. System Metrics

请求成功率、Latency、GPU、显存、吞吐、错误率、队列。

---

## 10. P95 Latency

95% 请求在某时间内完成，是比平均延迟更实用的系统指标。

---

## 11. Data Monitoring

文档类型、文本长度、Token、采购类型、地区、行业、年份、OCR 比例、解析失败率。

---

## 12. Data Drift Signal

医疗项目从 8% 上升到 45% 就值得触发重新评估。

---

## 13. Token Distribution

平均 500 token 变成 8000 token，意味着截断、长上下文、成本和遗漏风险都改变。

---

## 14. Model Output Monitoring

风险报警率、平均分数、高风险比例、风险类型分布、拒答率、低置信度比例。

---

## 15. 报警率突变

RiskFlagRate 18%→65%，可能是输入、Threshold、模型版本、Prompt 或分布发生变化。

---

## 16. Confidence 只是一种信号

平均置信度下降可能提示陌生数据，但 Confidence≠Truth。

---

## 17. Business Metrics

最终要看专家接受率、漏报率、修改采用率、法规引用正确率等。

---

## 18. Expert Acceptance Rate

模型报警1000条，专家确认820条值得关注，则接受率82%。

---

## 19. 为什么线上 Recall 难测

模型没报警的地方不会自动暴露，所以要主动抽样审计。

---

## 20. Sample Audit

每周从“无风险”中抽 100 条人工复核，才能估计沉默漏报。

---

## 21. 沉默错误必须被监控

风险系统不能只看模型报出来什么，还要看它没报什么。

> **专家心智模型**
>
> 心智模型③：FN 不会主动向你报错。

---

## 22. Human Feedback

Accept、Edit、Reject、Missed Risk 都能产生训练信号。

---

## 23. Production Feedback Dataset

model_prediction + expert_final_answer 自然形成 (X, Ŷ, Y)。

---

## 24. 反馈不能直接当 Ground Truth

用户误操作或标准不一，Raw Feedback 需要质量审核和专家确认。

---

## 25. Human-in-the-Loop

AI 初审→专家复核→最终意见→反馈数据库→下一轮训练。

---

## 26. 哪些案例优先专家复核

低置信、高风险、OOD、LLM/规则冲突、版本分歧、高置信错误。

---

## 27. 专家不是失败后的补丁

专家本身就是持续学习系统的一部分。

> **专家心智模型**
>
> 心智模型④：Human Feedback 是数据飞轮的燃料。

---

## 28. Drift Monitoring

生产环境中真正监控 Data Drift、Label Drift、Concept Drift。

---

## 29. Data Drift

P(X) 变化，例如服务类变成医疗货物为主。

---

## 30. Label Drift

P(Y) 变化，例如治理后真实风险率从20%降到6%。

---

## 31. Concept Drift

P(Y|X) 变化，例如新法规改变同一条款的判断。

---

## 32. 知识更新和模型更新要分开

法规变化通常先更新 RAG/Rules，参数训练周期可以更慢。

---

## 33. Stable Expertise vs Changing Knowledge

稳定能力放模型；快速变化、要求精确引用的知识放 RAG/Rules。

---

## 34. Retraining Trigger 1：Performance Drop

Recall 或 High-Risk Recall 持续低于门槛时触发调查。

---

## 35. Trigger 2：Drift

明显分布变化先重新评估，不一定立刻训练。

---

## 36. Trigger 3：Enough New Data

积累足够确认反馈和难例后再训练，避免频繁无价值更新。

---

## 37. Trigger 4：Major Rule Change

先知识库/规则更新，再形成新政策案例，最后考虑 Retrain。

---

## 38. Trigger 5：New Domain

进入医疗/工程等新领域前先建立独立测试集和能力差距分析。

---

## 39. 新模型不能直接替换生产模型

离线 Recall 95% 不等于生产更安全。

---

## 40. Shadow Deployment

新模型接真实流量但不影响用户，只做静默预测比较。

---

## 41. Shadow 的价值

能发现 OOD、Latency、Token、RAG、预测分布问题。

---

## 42. Canary Deployment

先给 5% 流量，逐步 20%→50%→100%。

---

## 43. A/B Test

两个安全候选模型可以比较真实工作流指标。

---

## 44. Rollback

新版本异常时应能立刻退回上一稳定版本。

---

## 45. 新模型默认可能退化

Evaluate→Shadow→Canary→Monitor→Promote，并随时准备 Rollback。

> **专家心智模型**
>
> 心智模型⑤：防御性发布。

---

## 46. Continual Learning 不是随时在线改参数

未经控制的持续更新会带来不可复现和能力遗忘。

---

## 47. Catastrophic Forgetting

只拿大量医疗数据继续训练，可能把资格条件能力从96%打到78%。

---

## 48. Replay Data

新数据训练时保留历史代表性样本，目标 Learn New + Preserve Old。

---

## 49. Regression Protection

每次 Retrain 后固定核心能力 Slice 做回归评测。

---

## 50. 模型健康仪表盘：System

Requests/min、Latency、Error Rate、GPU。

---

## 51. 模型健康仪表盘：Data

行业、地区、Token、解析成功率、OOD。

---

## 52. 模型健康仪表盘：Model

Risk Rate、Confidence、Abstention、抽检 Precision/Recall。

---

## 53. 模型健康仪表盘：Knowledge

法规命中率、有效法规比例、过期引用率。

---

## 54. 模型健康仪表盘：Human

接受率、修改率、驳回率、漏报补充数。

---

## 55. Inference Lineage

Request→Document→Parser→Model→Prompt→RAG→Rules→Output→Final Decision。

---

## 56. Prompt 也要版本化

LLM 权重不变，system_prompt_v12→v13 也可能显著改变表现。

---

## 57. System Version

LLM、Prompt、Retriever、Embedding、Knowledge Base、Rule Engine、Parser 共同组成一次生产系统版本。

---

## 58. Model Metric → Workflow Metric → Business Outcome

Recall 提高只是中间层，最终还要看审查时间、Critical Miss、专家工时和返工。

---

## 59. Feedback Loop 会改变现实

AI 提示让采购人不再写某些条款，未来 P(X) 本身就会变化。

---

## 60. 第十阶段五个心智模型

上线是真考；系统决定质量；监控沉默错误；专家参与闭环；新模型默认可能退化。

---

## 61. 阶段掌握标准

线上效果变差时，你应先检查输入分布、Parser、法规/RAG、生产版本、Slice、OOD、专家反馈，再决定 Knowledge/Rules/Model 哪一层更新。

---

---

## 62. Production Quality 是乘法，而不是只看模型

可以用一个非常有用的近似直觉：

\[
Quality\approx DataPipeline\times Model\times Retrieval\times Rules\times Serving
\]

Parser 把表格丢了，即使 LLM 很强也可能错；RAG 找到过期法规，推理再漂亮也不可靠；线上 Prompt 与评测 Prompt 不一致，同一权重也会产生不同表现。

## 63. 线上监控至少分五层

System：Latency、错误率、GPU、吞吐；Data：行业、地区、Token 长度、OCR/解析失败；Model：风险率、置信度、拒答率；Business：专家接受率、审查时间、漏报；Human Feedback：接受、修改、驳回、补充遗漏风险。

只监控服务器活着不等于模型健康。

## 64. 为什么线上 Recall 必须靠抽样审计

Precision 可以检查报警项；Recall 还需要知道模型没报的东西里藏了多少 FN。因此应定期从“模型判正常”样本中随机抽取一批，让专家盲审，估计沉默错误。

风险系统最危险的错误往往恰恰没有任何报警日志。

## 65. Feedback 不能直接当 Ground Truth

用户点击 Reject 可能是误操作、个人偏好或非专家意见。正确闭环是 Raw Feedback → Quality Check → Expert Review → Confirmed Feedback → Training Data。否则生产反馈会把噪声直接放大进模型。

## 66. Retraining Trigger 应该由条件触发，而不是“想起来就训”

常见触发包括核心 Performance Drop、明显 Drift、积累足够新专家数据、重大法规变化、新业务领域上线。Drift 本身未必立即要求训练，应该先 Evaluate，确认性能真的受到影响。

## 67. 知识更新与模型参数更新是两个周期

法规变化时，优先更新 RAG/Rules 能快速生效；模型参数更新需要积累案例、专家标注和回归评测，周期更长。可以概括：稳定专家行为交给模型，快速变化知识尽量外置。

## 68. Shadow、Canary、A/B 三种上线策略

Shadow：新模型吃真实流量但结果不展示；Canary：先给 5% 用户，逐步扩大；A/B：两个安全候选同时服务不同流量，比较业务指标。它们共同避免“离线高分就一次性替换全部生产流量”。

## 69. Rollback 必须在发布之前就设计好

新版本 High-Risk Recall 异常下降时，应能快速切回上一稳定版本，而不是临时重新训练。Model Registry、系统版本和可复现 Artifact 是 Rollback 的基础设施。

## 70. Continual Learning 最大风险之一：Catastrophic Forgetting

为了提高医疗技术参数，只用大量医疗新数据继续训练，可能让资格条件 Recall 从 96% 掉到 78%。Retraining 通常需要 New Data + Replay Data，并用 Regression Set 保护历史核心能力。

## 71. 一个生产模型健康 Dashboard 应该有什么

System Health、Data Health、Model Health、Knowledge Health、Human Feedback 和 Drift 六大区块。对于 RAG 还应监控有效法规比例、过期引用率、检索命中和 Reranker 行为。

## 72. Inference Lineage：一次线上判断也应该可追溯

Request ID → Document Version → Parser Version → Model Version → Prompt Version → RAG Query → Retrieved Evidence → Rule Result → Final Output。这样用户问“为什么当时判高风险”时，不需要猜。

## 73. Model Metric → Workflow Metric → Business Outcome

Recall 提高不一定自动产生业务价值。真正结果可能是审查时间从 120 分钟降到 45 分钟，同时 Critical Miss Rate 不上升。最终应该同时看模型指标、工作流效率和业务结果。

## 74. 第十阶段五个核心心智模型

1. 上线才是真实考试，离线 Test 只是模拟。
2. 生产质量由完整系统决定，不由单个 LLM 决定。
3. 必须主动监控沉默的 FN，而不是只看报警项。
4. 专家不是失败兜底，而是持续学习系统的一部分。
5. 每个新模型都默认可能退化，必须 Shadow/Canary/Regression/Rollback。

---
