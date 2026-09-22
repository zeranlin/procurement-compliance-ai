# 第一课 · 第 9 阶段：工程化与可复现性——Versioning、Tracking、Registry

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：MEDIUM。** 审计原因：核心心智模型出现偏后，阅读前段缺少认知锚点。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **模型是完整训练状态，不是一个权重文件。**
2. **所有影响结果的东西都应该版本化。**
3. **单次训练结果具有随机性，要考虑 Seed 和方差。**
4. **训练日志和实验记录是科学证据，不是临时垃圾。**
5. **专业模型必须可追溯到数据、代码、配置、评测和规则。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Dataset` | 数据集：按统一 Schema、版本和质量标准组织的样本集合 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Checkpoint` | 检查点：保存模型和训练状态以便恢复/发布 |
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `Recall` | 召回率：真实风险中被系统成功找出的比例 |
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `Label Schema` | 标签结构：定义风险状态、类型、等级、证据等标注字段 |

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

这一阶段解决可复现与工程治理：今天训练出来的模型，三个月后是否还能准确知道它由什么数据、代码、参数和环境产生。

\[
ModelArtifact = Weights + BaseModel + DatasetVersion + CodeVersion + Config + Environment + Evaluation
\]

重点包括 Dataset Version、Label Schema、Git Commit、Config、Seed、Checkpoint、Experiment Tracking、Model Registry、Lineage 和 Regression Test。

---

## 1. 第九阶段总问题：三个月后还能复现今天的模型吗？

工程化不是把代码整理漂亮，而是确保模型来源、数据、配置、评测和生产版本都可追溯。

---

## 2. 一个模型不是一个 .pt 文件

模型身份应包含权重、Base Model、Dataset、Code、Config、Environment、Evaluation。

> **公式 / 关键表达**
>
> ModelArtifact = Weights + BaseModel + DatasetVersion + CodeVersion + Config + Environment + Evaluation

---

## 3. 为什么只留 model.safetensors 不够

没有训练来源，就无法解释、复现、审计或安全升级。

---

## 4. Dataset Version

专家修标签、新增 Hard Negative、补行业数据后，必须产生新数据版本。

---

## 5. Dataset Card

每个版本记录数量、来源、时间范围、地区、任务、标签 Schema、正负比例、难例、去重方式、已知缺陷和 Split。

---

## 6. 模型版本不能脱离数据版本

Model A/B 分数差异只有在知道各自 Dataset Version 时才有解释意义。

---

## 7. Label Schema Version

0/1 改成低/中/高风险，任务本身已经变化，必须版本化。

---

## 8. Annotation Guideline Version

专家标注规则从“一律高风险”改成“结合必要性判断”，旧标签语义已经不同。

---

## 9. Label Drift

标注标准随时间变化会形成隐形任务漂移。

---

## 10. 所有影响结果的东西都要版本化

Data、Labels、Code、Config、Model、Evaluation Set。

> **专家心智模型**
>
> 心智模型②：不可追踪的变化就是实验污染。

---

## 11. Code Version

用 Git commit 固定训练、数据处理和评估代码。

---

## 12. Evaluation Code 也必须版本化

Recall 计算 Bug 可能制造“模型提升”的假象。

---

## 13. Training Config

学习率、Epoch、Batch、Accumulation、Optimizer、Weight Decay、Warmup、Seed 等写入 YAML/JSON。

---

## 14. Config 与代码分离

代码负责怎么训练，Config 负责这次实验具体参数。

---

## 15. 同一代码 + 不同 Config = 不同 Experiment

这样才能做干净的 Controlled Experiment。

---

## 16. Random Seed

控制数据 shuffle、初始化、dropout、采样等随机过程的起点。

---

## 17. 相同 Seed 也不保证逐位一致

GPU、CUDA、PyTorch、并行方式可能带来细微非确定性。

---

## 18. 重要实验跑多个 Seed

比较均值与标准差，而不是只报最好一次。

---

## 19. Metric 是随机变量

F1=.884±.004 比“最好一次 .889”更科学。

> **专家心智模型**
>
> 心智模型③：不要把一次训练结果当绝对真理。

---

## 20. Environment Version

记录 Python、PyTorch、Transformers、CUDA、Driver、GPU 等。

---

## 21. requirements / conda / Docker

依赖环境必须可复制。

---

## 22. Docker 的角色

把 Code + Dependencies + Runtime 封装，使团队和服务器环境更一致。

---

## 23. Checkpoint

训练中定期保存模型状态。

---

## 24. Checkpoint 用于断点续训

服务器中断后可以从最近 checkpoint 恢复。

---

## 25. Checkpoint 用于选择最佳模型

Best Val checkpoint 不一定是最后一个。

---

## 26. 完整 Checkpoint 还要保存 Optimizer/Scheduler

否则恢复训练时优化器会“失忆”。

---

## 27. Experiment Tracking

实验多起来后，需要集中记录参数、指标、曲线、Artifacts 和比较。

---

## 28. Experiment ID

每次训练都应有唯一 ID，例如 EXP-2026-0042。

---

## 29. Experiment 输入元数据

Dataset、Base Model、Code Commit、Config、Seed。

---

## 30. Experiment 训练元数据

LR、Batch、Epoch、Loss Curve、GPU、时间、吞吐。

---

## 31. Experiment 结果元数据

Recall、Precision、F1/F2、High-Risk Recall、Best Checkpoint。

---

## 32. 训练曲线是科学证据

两个最终 F1 相同，曲线稳定性完全不同，可靠性也不同。

---

## 33. TensorBoard / MLflow / W&B

工具不同，本质都是 Experiment→Metrics→Parameters→Artifacts→Comparison。

---

## 34. 训练日志不是垃圾

Loss、LR、Step、Gradient 等日志是结论证据链。

> **专家心智模型**
>
> 心智模型④：没有实验证据就很难解释模型选择。

---

## 35. Model Registry

管理哪些模型是 Development、Candidate、Staging、Production、Archived。

---

## 36. Model Card

记录用途、训练数据、评测集、指标、优势、弱点、Out of Scope、推荐使用方式。

---

## 37. Known Limitations

专业模型必须公开能力边界，而不是“支持所有政府采购”。

---

## 38. 为什么政府采购尤其需要 Registry

出现争议时必须能回答当时是哪个模型、哪版规则、哪版数据、哪个 Threshold。

---

## 39. Traceability

专业系统要能回答 Who/WhatData/WhatModel/WhatVersion/WhatRule/WhatEvidence/When。

---

## 40. Model Lineage

Raw Data→Clean Dataset→Expert Labels→Train Dataset→Experiment→Checkpoint→Model→Production。

---

## 41. Artifact

数据、配置、模型、Tokenizer、Metrics、Error Report 都是需要保存的研发产物。

---

## 42. 推荐项目目录

data/raw/cleaned/labeled/versions、configs、src、experiments、checkpoints、models、evaluation。

---

## 43. 数据与代码分离

训练代码不应偷偷改标签；Data Pipeline 每一步输入输出都应可追踪。

---

## 44. Immutable Data

发布后的 dataset_v1.2 不要原地偷偷修，发现错误就发 v1.3。

---

## 45. Gold Test Set 也要版本化

gold_test_v1.0 升级时应变成 v2.0，而不是静默修改。

---

## 46. 反复看 Gold 会污染

日常开发用 Dev，发布前用 Gold，重大版本可以有 Hidden Challenge Set。

---

## 47. 三层评测

Dev Set→Gold Set→Hidden Challenge Set，降低团队对刷题风险。

---

## 48. CI/CD 在 ML 中更复杂

Data/Code/Config 变化都可能触发 Train→Evaluate→Quality Gate→Registry→Deploy。

---

## 49. Quality Gate

达到 High-Risk Recall、Overall Recall、Precision、引用准确率、无严重回归等门槛才能晋级。

---

## 50. Regression

新模型修好 A 却把 B 弄坏。

---

## 51. Regression Test

资格、技术、评分、商务、高风险、Hard Negative、跨地区、长文本等核心 Slice 都要防回归。

---

## 52. Model Governance

数据来源、标注、模型、法规版本、输出和操作日志都逐渐进入治理范围。

---

## 53. ProcurementML Experiment 001 的工程身份

EXP ID + Dataset + Label Schema + Guideline + Git Commit + Config + Seed + Gold + Best Checkpoint + Metrics + Error Report + Model Version。

---

## 54. 第九阶段五个心智模型

模型是完整训练状态；一切版本化；结果有随机性；日志是证据；专业模型必须可追溯。

---

## 55. 阶段掌握标准

听到“V0.5 F1=92%”时，你应追问 Dataset、Gold、Base Model、Code Commit、Config、Seed、Checkpoint、Experiment ID、回归和 Known Limitations。

---

---

## 56. 一个真正可复现模型的身份公式

\[
ModelArtifact=Weights+BaseModel+DatasetVersion+CodeVersion+Config+Environment+Evaluation
\]

只保存 `model.safetensors`，却不知道 Dataset、Git Commit、Prompt、Threshold 和 Gold Set，几个月后就无法解释这个模型为什么好，也无法重新训练出接近结果的版本。

## 57. Dataset Card 应该描述“这版数据是谁”

除了样本数，还要记录来源、时间范围、地区、任务、标签 Schema、正负比例、Hard Examples、去重方法、专家标注指南版本、Train/Val/Test 划分和已知缺陷。Dataset v1.3 不是“比 v1.2 多 3000 条”这么简单。

## 58. Label Schema 与 Annotation Guideline 也必须版本化

从 0/1 二分类升级到低/中/高风险，已经改变了任务；专家规则从“本地要求一律高风险”升级到“区分注册地限制和履约服务必要性”，也改变了标签含义。

如果把不同标准的数据混在一起却不记录版本，模型会看到系统性 Label Drift。

## 59. Random Seed 为什么要记录，但不能迷信

同一代码也有 Shuffle、初始化、Dropout 等随机性。Seed 能提高复现程度，但不同 GPU/CUDA/并行算法仍可能造成差异。重要实验最好跑多个 Seed，并报告 Mean ± Std，而不是只展示最高一次。

## 60. Checkpoint 需要保存什么

为了恢复训练，完整 Checkpoint 不只包含 Model Weights，还可能包含 Optimizer State、Scheduler State、Global Step 和 Random State。只恢复权重却让 AdamW 的内部状态清零，训练轨迹会发生变化。

## 61. Best Checkpoint 不一定是 Last Checkpoint

若 step 3000 Validation F1=0.89，step 5000 只有 0.83，最终发布模型应该来自 3000，而不是因为它“更新”就选最后一个。Model Registry 应明确记录最佳 Checkpoint 来源。

## 62. Experiment Tracking 记录的是证据链

Experiment ID 应关联 Dataset、Base Model、Git Commit、Config、Seed、LR、Batch、训练时间、Loss 曲线、Metrics、Best Checkpoint 和 Error Analysis。TensorBoard、MLflow、Weights & Biases 只是不同实现，核心都是让实验可比较、可追溯。

## 63. Model Registry 是生产模型的档案馆

模型可以经历 Development → Candidate → Staging → Production → Archived。每个注册版本应有训练实验、评测集、核心指标、Known Limitations 和使用范围，不能把一个随机 checkpoint 直接复制到服务器就叫“上线”。

## 64. Model Lineage：从生产结果一路追回原始数据

\[
RawData\rightarrow CleanDataset\rightarrow ExpertLabels\rightarrow TrainDataset\rightarrow Experiment\rightarrow Checkpoint\rightarrow ProductionModel
\]

政府采购合规系统尤其需要这种 Traceability：争议发生时，应能回答当时是哪版模型、哪版法规库和哪版规则产生结果。

## 65. Immutable Artifact 原则

发布后的 dataset_v1.2 不应该原地偷偷修 100 条仍叫 v1.2；应生成 v1.3。Gold Test 同样应该冻结，确需升级则创建新版本。否则同一个版本名代表不同内容，实验比较失去意义。

## 66. Regression Test 与 Quality Gate

新模型总体分数提高，也可能把某一核心能力修坏。发布门禁应检查资格、技术、评分、Hard Negative、高风险、跨地区等固定 Slice；只有满足 High-Risk Recall、总体 Recall、Precision 和无严重回归等条件，Candidate 才能进入 Production。

## 67. Model Card 是模型说明书

至少描述 Purpose、Training Dataset、Evaluation Set、核心指标、Known Strengths、Known Weaknesses、Out of Scope 和 Recommended Use。专业表述不是“支持所有政府采购”，而是明确在哪些年份、领域和任务上经过验证。

## 68. 第九阶段五个核心心智模型

1. 模型是完整训练状态，不是一个权重文件。
2. 所有影响结果的东西都应该版本化。
3. 单次训练结果具有随机性，要考虑 Seed 和方差。
4. 训练日志和实验记录是科学证据，不是临时垃圾。
5. 专业模型必须可追溯到数据、代码、配置、评测和规则。

---
