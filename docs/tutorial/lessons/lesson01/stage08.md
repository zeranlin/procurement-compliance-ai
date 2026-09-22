# 第一课 · 第 8 阶段：完整机器学习实验——ProcurementML Experiment 001

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：MEDIUM。** 审计原因：核心心智模型出现偏后，阅读前段缺少认知锚点。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **大模型项目应该拆成一串可证伪的小实验。**
2. **Test Set 不是剩余数据，而是未来使用场景模拟器。**
3. **模型价值来自相对 Baseline 的提升和成本差异。**
4. **成功标准必须在看到结果之前定义。**
5. **实验记录、失败结论和错误分析都是研发资产。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Split` | 数据切分：按项目/时间/地区划分训练、验证、测试数据 |
| `Dataset` | 数据集：按统一 Schema、版本和质量标准组织的样本集合 |
| `Recall` | 召回率：真实风险中被系统成功找出的比例 |
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |
| `Precision` | 精确率：系统报出的风险中真正成立的比例 |
| `Hard Positive` | 高难正例：没有明显关键词但确实需要识别的风险 |
| `Regression` | 回归测试：更新后验证旧能力和关键切片没有退化 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |

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

这一阶段把前七个阶段真正装成一个实验：定义 Problem、Hypothesis、X/Y、Dataset、Split、Baseline、Success Criteria、Training、Evaluation、Error Analysis 和 Next Experiment。

\[
Problem \rightarrow Hypothesis \rightarrow Dataset \rightarrow Baseline \rightarrow Train \rightarrow Evaluate \rightarrow ErrorAnalysis
\]

目标是完整设计第一个政府采购机器学习实验 `ProcurementML Experiment 001`。

---

## 1. 第八阶段目标：把前 7 个阶段装成一台机器

这一阶段不再堆新概念，而是完整设计第一个可执行实验 ProcurementML Experiment 001。

---

## 2. 完整实验主线

科学实验式研发应该从问题和假设出发，而不是先开 GPU。

> **公式 / 关键表达**
>
> Problem → Hypothesis → Dataset → Baseline → Train → Evaluate → Error Analysis → Next Experiment

---

## 3. Experiment 001 的任务边界

先做“供应商资格条件是否存在潜在不合理限制风险”的二分类任务，不做大而全。

---

## 4. 为什么先选资格条件风险

输入较清晰、标签相对可定义、业务价值明确、可计算 Precision/Recall，也便于后续扩展。

---

## 5. 第一步：定义 X

最小 X 是一条资格条件文本。

---

## 6. Experiment 001-A

X=单条资格条件，用于验证仅凭条款文本能做到什么。

---

## 7. Experiment 001-B

X=[资格条件,采购标的,项目类型,上下文]，用于验证上下文是否显著提升。

---

## 8. 上下文是可实验变量

A/B 的差异本身就是一个可证伪假设：增加上下文是否减少 FN？

---

## 9. 第二步：定义 Y

第一版先用二分类：1=存在潜在不合理限制风险，0=未发现明显风险。

---

## 10. 为什么第一版不把 Y 做得太复杂

如果同时训练风险类型、依据、理由、建议，很难知道哪一部分导致失败。

---

## 11. One Experiment, One Main Question

一次实验尽量回答一个核心问题。

> **专家心智模型**
>
> 心智模型①：大模型研发是很多小实验，而不是一个“大项目”。

---

## 12. Hypothesis-driven Development

Experiment 001 资格风险；002 上下文；003 Hard Negative；004 7B vs 14B；005 RAG 提升引用准确率。

---

## 13. 第三步：定义数据 Schema

sample_id、project_id、text、label、risk_type、category、industry、region、date、difficulty、source、expert、confidence 等字段不是装饰。

---

## 14. project_id 的用途

用于项目级 Split，防止同项目泄漏。

---

## 15. industry / region 的用途

用于 Slice Evaluation 和分布诊断。

---

## 16. date 的用途

用于 Time Split、Concept Drift 和法规时效判断。

---

## 17. difficulty 的用途

用于 Hard Positive/Negative 和边界案例分析。

---

## 18. Data Schema = Future Evaluation Infrastructure

今天多保存一个字段，未来就多一个可诊断维度。

---

## 19. 第四步：设计样本组成

假设第一批 10000 条，可以显式安排明显风险、普通风险、普通正常、Hard Negative、Hard Positive、边界案例。

---

## 20. 为什么不是简单 50/50

类别平衡只是一个维度，真正要保证决策边界附近的样本质量。

---

## 21. 第五步：Train/Val/Test Split

可以先 8000/1000/1000，但切分单位应是 Project ID。

---

## 22. 项目级隔离

Project A 的所有条款、公告、答复等必须进入同一 split。

---

## 23. 时间外测试

过去训练、未来测试，模拟真实部署。

---

## 24. Challenge Set

专门放未见行业、新地区、Hard Example、同义改写和 OOD 样本。

---

## 25. Test 是未来场景模拟器

Test 不是“剩余数据”，而是对真实部署的预演。

> **专家心智模型**
>
> 心智模型②：测试设计本身就是产品设计的一部分。

---

## 26. 第六步：先建立 Baseline

不要一开始就 Fine-tune 14B。

---

## 27. Baseline 0：永远预测正常

如果风险率30%，Accuracy 可以70%，但 Recall=0。

---

## 28. Baseline 1：关键词规则

“注册资本/成立年限/本地分公司”等规则可以得到一个朴素起点。

---

## 29. Baseline 2：TF-IDF + Logistic Regression

便宜、可解释，能验证任务本身是否可学。

---

## 30. 为什么 Baseline 极重要

7B F1=.82，如果 TF-IDF=.81，复杂模型增益很小；如果 Baseline=.63，提升就很有意义。

---

## 31. Improvement over Baseline

模型价值来自相对提升和成本收益，而不是孤立漂亮分数。

> **专家心智模型**
>
> 心智模型③：永远问相对提升。

---

## 32. 第七步：定义 Primary Metric

风险筛查优先 Recall。

---

## 33. Secondary Metrics

Precision、F1/F2、High-Risk Recall、各 Slice 指标。

---

## 34. 第八步：训练前写 Success Criteria

例如 Recall≥90%、Precision≥80%、High-Risk Recall≥95%，并要求相对 Baseline 有明显提升。

---

## 35. 为什么必须训练前定义成功

否则结果出来后容易挑最好看的指标宣布成功。

---

## 36. Metric Gaming / Cherry Picking

Accuracy94%但Recall61%时，如果目标事先写 Recall≥90%，就不能自欺欺人。

---

## 37. 心智模型④：预注册成功标准

Define Success → Run → Judge，不要反过来。

---

## 38. 第九步：选择第一个模型

优先 Logistic Regression、LightGBM/XGBoost 或小型 Transformer，先验证数据与任务。

---

## 39. 复杂度阶梯

Rule → Logistic Regression → Small Transformer → 7B → 14B，每一层都问增益是否值得。

---

## 40. 第十步：正式训练

假设 Train=8000、Batch=32，则约250 steps/epoch，5 epoch 最多1250 steps。

---

## 41. 训练监控表

记录 Train Loss、Val Loss、Precision、Recall、F1/F2、LR、Step/Epoch、Best Checkpoint。

---

## 42. 曲线案例

Epoch3 Val 最好，Epoch4/5 Train 继续改善但 Val 变差，应选择 Epoch3 附近。

---

## 43. 第十一步：Test 只在模型冻结后打开

模型、阈值、超参数确定后再做最终 Test。

---

## 44. Confusion Matrix 例子

TP=270,FN=30,FP=60,TN=640 → Recall=90%，Precision≈81.8%。

---

## 45. 实验通过 ≠ 项目结束

达到门槛后真正重要的是 Error Analysis。

---

## 46. 把 FN 全拉出来

按 Hard Positive、上下文缺失、医疗知识、标签错、新型风险等分类。

---

## 47. Root Cause 决定 Experiment 002

如果最大错误来源是上下文缺失，就提出“加入上下文降低 FN”的新假设。

---

## 48. Controlled Experiment

一次主要改变一个变量，才能知道提升因果来源。

---

## 49. 实验日志是知识资产

EXP001、002、003 的成功/失败共同形成团队经验。

> **专家心智模型**
>
> 心智模型⑤：真正能力来自实验积累，而非某次幸运训练。

---

## 50. Experiment Card

Question、Hypothesis、Dataset、Split、Baseline、Model、Metric、Success、Result、Error Analysis、Next Experiment 全部记录。

---

## 51. Experiment Tracking

实验多起来后使用 MLflow/W&B/TensorBoard 或自建数据库跟踪参数、指标和 artifacts。

---

## 52. Data Version

没有 dataset_v0.1/v0.2，就无法判断模型提升来自数据还是代码。

---

## 53. Reproducibility

记录 Random Seed、Dataset Version、Code Version、Base Model、Environment、Hyperparameters。

---

## 54. Experiment 001 完整闭环

业务问题→X/Y→Schema→采集标注→Project Split→Baseline→Train→Validation→Threshold→Test→Slice→Error Analysis→Root Cause→Experiment002。

---

## 55. 第八阶段五个心智模型

小实验；Test 模拟未来；Baseline；预注册成功标准；实验积累是知识。

---

## 56. 阶段掌握标准

给你“训练评分标准审查模型”的需求时，你应自然追问 X/Y、标签、Split、Baseline、主指标、FN/FP成本、成功门槛、错误归因和下一轮实验。

---

---

## 57. Experiment 001 的完整实验卡

**Question**：仅根据供应商资格条件文本，能否识别潜在不合理限制风险？

**Hypothesis**：高质量专家标注数据训练出的文本分类模型，能在项目级隔离测试集上显著超过关键词规则。

**Dataset**：10,000 条；Train/Val/Test=8000/1000/1000；同一 project_id 不跨集合。

**Primary Metric**：Recall；Secondary：Precision、F1/F2、High-Risk Recall。

**Success Criteria**：例如 Recall≥90%、Precision≥80%，且相比关键词 Baseline 的 F1 至少提高 10 个百分点。成功标准必须在看到结果之前写下。

## 58. Baseline 0、1、2 为什么都值得做

Baseline 0 永远预测正常，用于暴露类别不平衡；Baseline 1 使用关键词规则，体现现有人工规则系统能做到什么；Baseline 2 使用 TF-IDF + Logistic Regression，验证复杂模型是否真的带来语义增益。

如果 7B LLM F1=0.82，而 Logistic Regression=0.81，就要重新审视复杂度成本；若 Baseline=0.63、LLM=0.88，增益才非常明确。

## 59. 数据 Schema 是未来评测基础设施

sample_id、project_id、industry、region、case_date、difficulty、source_type、expert_confidence 等字段不是装饰。project_id 用于防泄漏；industry 用于 Slice；date 用于时间泛化；difficulty 用于 Hard Cases；label_confidence 用于标签复核。

设计 Schema 时其实已经在设计未来可以问哪些评测问题。

## 60. Challenge Set 与普通 Test 的作用不同

普通 Test 模拟主流真实部署；Challenge Set 可以故意放未见行业、Hard Positive/Negative、同义改写、长文本、特殊地区和 OOD，用来测鲁棒性。不要把两者合成一个平均分，否则容易失去诊断价值。

## 61. 训练前先写 Success Criteria 可以防止 Metric Gaming

如果结果 Accuracy=94%、Recall=61%，没有预注册目标时团队很容易宣传 Accuracy；若训练前已经规定 Recall≥90%，实验就明确失败。科学实验的价值之一，就是让结果不能事后挑指标解释。

## 62. 一个 Epoch 表格应该怎样读

假设 Epoch 1～3：Train Loss 0.63→0.36，Val Loss 0.59→0.38，Recall 78%→90%，Precision 76%→82%；Epoch 4～5 Train Loss 继续下降，但 Val Loss 上升、Precision 跌到 71%。最佳模型更可能是 Epoch 3，而不是最后一轮。

## 63. Test 之后才真正开始 Error Analysis

如果 Test TP=270、FN=30、FP=60、TN=640，则 Recall=90%、Precision≈81.8%。即使达到 Success Criteria，也应把 30 个 FN 全部分类：Hard Positive、上下文缺失、医疗知识、标签错、新型风险等。

这张错误分布表才决定 Experiment 002 做什么。

## 64. Experiment 002 的控制实验示例

若最大根因是上下文缺失，提出 Hypothesis 002：“加入采购标的和上下文可显著降低 FN”。只改变 X，从单条条款升级为 [条款,采购标的,上下文]，其余数据、模型、阈值尽量保持不变。

若 Recall 从 90% 提高到 94%，才有证据支持“上下文有效”。

## 65. Experiment Log 也是模型资产

真正有价值的不是只剩一个 `model_v27.pt`，而是知道 Experiment 001 什么有效、002 什么无效、003 为什么失败。随着实验积累，团队形成的是 Empirical Knowledge，而不是一次幸运训练。

## 66. 第八阶段五个核心心智模型

1. 大模型项目应该拆成一串可证伪的小实验。
2. Test Set 不是剩余数据，而是未来使用场景模拟器。
3. 模型价值来自相对 Baseline 的提升和成本差异。
4. 成功标准必须在看到结果之前定义。
5. 实验记录、失败结论和错误分析都是研发资产。

---
