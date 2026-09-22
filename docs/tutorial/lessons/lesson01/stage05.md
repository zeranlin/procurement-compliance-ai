# 第一课 · 第 5 阶段：Batch、Step、Epoch 与真实训练过程

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：MEDIUM。** 审计原因：核心心智模型出现偏后，阅读前段缺少认知锚点。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Batch 是对整体数据分布的有噪声局部估计。**
2. **Epoch 是训练深度，不是模型能力分数。**
3. **Gradient、Optimizer、Learning Rate 是三个不同角色。**
4. **训练本质是随机/有噪声优化，曲线抖动不等于失败。**
5. **Monitoring 本身就是训练的一部分，没有日志就难以诊断。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Batch` | 批次：一次参与计算的一组样本 |
| `Epoch` | 训练轮次：训练数据完整遍历一次 |
| `Step` | 训练步：通常指一次优化器更新 |
| `Gradient` | 梯度：损失对参数变化方向和敏感度的局部信息 |
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `Optimizer` | 优化器：依据梯度规则更新参数 |
| `Dataset` | 数据集：按统一 Schema、版本和质量标准组织的样本集合 |
| `Gradient Accumulation` | 梯度累积：多次小 Batch 累积梯度后再更新参数 |

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

这一阶段回答真实训练循环如何运行：Dataset 如何拆成 Batch，一次 Step 发生什么，Epoch 是什么，Optimizer 与 Gradient 有什么区别，以及 GPU 显存不足时为什么会用 Gradient Accumulation。

\[
EffectiveBatch = PerDeviceBatch \times NumGPUs \times GradientAccumulation
\]

对于政府采购长文本，还必须开始从“样本数”升级到“Token 数、上下文长度、Chunking、Packing”的思维。

---

## 1. 第五阶段总问题：真实训练到底怎么跑？

把一个样本的数学更新扩展到成千上万样本：Dataset → Batch → Forward → Loss → Backward → Optimizer → Step → Epoch。

---

## 2. Dataset

训练集是很多 (x,y) 样本的集合。

> **公式 / 关键表达**
>
> D={(x₁,y₁),…,(x_N,y_N)}

---

## 3. Batch

一次前向/反向通常只取一小批样本，而不是整个数据集。

---

## 4. 为什么不用 Batch=1

单样本梯度噪声很大，更新方向容易受偶然样本影响。

---

## 5. 为什么不用 Full Batch

整个数据集一起算虽然稳定，但内存和计算代价极大，更新也太慢。

---

## 6. Mini-batch 是折中

小批量梯度可以看成对全数据梯度的随机估计。

> **公式 / 关键表达**
>
> MiniBatchGradient ≈ FullDatasetGradient

---

## 7. Batch = 局部民意调查

每个 Batch 只代表数据世界的一小部分，所以梯度会波动。

> **专家心智模型**
>
> 心智模型①：Batch 是对全体分布的局部有噪估计。

---

## 8. 一个 Batch 内发生什么

Forward → 样本 Loss → Batch 平均 Loss → Backward → Optimizer Update。

---

## 9. Optimizer Step

真正修改参数的一次动作。注意它和“做了一次 forward/backward”不一定一一对应，因为可能有梯度累积。

---

## 10. Epoch

完整看过一遍训练集叫一个 Epoch。

---

## 11. Epoch 不是能力分数

训练更多 Epoch 只代表更深地拟合训练数据，不保证泛化更好。

> **专家心智模型**
>
> 心智模型②：Epoch 是训练深度，不是能力。

---

## 12. Steps per Epoch

如果 N=100000、有效 Batch=50，则每轮约 2000 个 optimizer steps。

> **公式 / 关键表达**
>
> StepsPerEpoch ≈ N / EffectiveBatch

---

## 13. Total Steps

训练 5 Epoch，则约 10000 steps。

> **公式 / 关键表达**
>
> TotalSteps = StepsPerEpoch × Epochs

---

## 14. Learning Rate 再进入工程

训练中 η 往往不是常数，而是随 Step 变化。

---

## 15. Warmup

训练初期用较小 LR，让模型和优化器状态稳定，再逐渐升高。

---

## 16. Decay

训练后期逐渐减小 LR，用更小步长细化参数。

---

## 17. Parameter vs Hyperparameter

参数由训练学得；学习率、Batch、Epoch、Weight Decay、LoRA Rank 等由人设定，叫 Hyperparameters。

---

## 18. SGD

直接用当前 mini-batch 梯度更新，思想简单。

---

## 19. Momentum

利用历史方向降低对单个 noisy batch 的过度反应。

---

## 20. Adam

为不同参数自适应调整步长，并维护梯度历史统计。

---

## 21. AdamW

Transformer/LLM 中常见，采用解耦 Weight Decay。

---

## 22. Gradient ≠ Optimizer

Gradient 是方向信号；Optimizer 是利用信号更新参数的策略。

> **专家心智模型**
>
> 心智模型③：不要把梯度和优化器混为一谈。

---

## 23. Micro Batch

单张 GPU 一次真正放进显存的样本数。

---

## 24. Gradient Accumulation

显存放不下目标 Batch 时，可以连续计算多个 micro-batch 的梯度，累积后再做一次 optimizer step。

---

## 25. Effective Batch

多卡训练时有效 batch 还要乘 GPU 数量。

> **公式 / 关键表达**
>
> EffectiveBatch = PerDeviceBatch × NumGPUs × GradientAccumulation

---

## 26. 有效 Batch 例子

4 GPU × 每卡2 × 累积8 = 64。

---

## 27. Micro-step ≠ Optimizer Step

梯度累积期间做了多次 forward/backward，但参数只在累积完成后更新一次。

---

## 28. Shuffle

Train 内每个 Epoch 通常打乱样本顺序，让 Batch 更能代表总体分布。

---

## 29. Shuffle 与 Split 不同

先按项目/时间做 Train/Val/Test 隔离，再在 Train 内 shuffle。不能用 shuffle 破坏隔离。

---

## 30. 训练是随机优化

不同 Batch 带来不同梯度，所以 Loss 曲线轻微抖动是正常的。

> **专家心智模型**
>
> 心智模型④：看趋势，不要把每一个 step 的波动都当故障。

---

## 31. Train Loss

观察模型是否在拟合训练集。

---

## 32. Validation Loss

观察泛化趋势和过拟合信号。

---

## 33. Learning Rate 曲线

确认 warmup/decay 是否按预期执行。

---

## 34. Gradient Norm

梯度突然巨大可能提示 exploding gradient 或数值问题。

---

## 35. 训练曲线：正常下降

Train 与 Val 都下降，通常说明模型在学习并泛化。

---

## 36. 训练曲线：剧烈振荡

优先检查 LR 是否过大，也要考虑 Batch 太小、数据噪声和数值问题。

---

## 37. 训练曲线：长期平坦

可能 LR 太小、数据/任务不可学、可训练参数配置错或梯度没有流动。

---

## 38. 训练曲线：Train 降、Val 升

典型过拟合，考虑 Early Stopping、数据增强、正则或更好的数据。

---

## 39. 文本训练要看 Token，不只看样本数

100 token 与 8000 token 的样本计算成本完全不同。

---

## 40. Context Length

长采购文件容易截断，必须设计 chunking、packing 和上下文策略。

---

## 41. 一个 PDF 不等于一个样本

采购公告很短，招标文件几十页，投标文件几百页。训练单元必须根据任务切分。

---

## 42. Packing

把多个短样本拼进一个上下文窗口，提高 GPU token 利用率。

---

## 43. GPU 的概念角色

GPU 负责高吞吐矩阵/张量运算；它不是“知识仓库”。知识能力通过参数值体现。

---

## 44. 监控是训练的一部分

没有日志、曲线和验证指标的训练，很难知道发生了什么。

> **专家心智模型**
>
> 心智模型⑤：Monitoring 不是可选附件。

---

## 45. 计算练习

Dataset=24000，GPU=2，每卡batch=4，累积=3，Epoch=5。EffectiveBatch=24，Steps/Epoch=1000，总 Steps=5000。

---

## 46. 第五阶段掌握标准

你应能计算 Effective Batch、Steps/Epoch、Total Steps，并能从曲线判断 LR、过拟合和训练异常。

---

---

## 47. 用 10 万条样本完整走一次训练循环

假设 Dataset 有 100,000 个 \((x_i,y_i)\)。Batch Size=50，则一个 Epoch 大约需要：

\[
100000/50=2000\text{ steps}
\]

如果训练 5 个 Epoch，理论上约经历 10,000 次 Batch；若没有梯度累积，每个 Batch 通常对应一次 Optimizer Step。

## 48. Batch 为什么是“局部民意调查”

Full Batch 使用整个训练集计算精确梯度，但计算和显存成本巨大；Batch=1 梯度噪声很大。Mini-Batch 折中：用一小批样本估计总体梯度。

\[
MiniBatchGradient\approx FullDatasetGradient
\]

由于每批样本不同，Loss 曲线轻微抖动是正常现象。

## 49. Epoch 不是能力分数

一个 Epoch 只表示训练数据整体被看过一遍。多看几遍可能学得更充分，也可能强化记忆和过拟合。真正选择训练深度需要观察 Validation，而不是迷信“3 Epoch”“10 Epoch”这样的固定经验数字。

## 50. Learning Rate 的三种典型失败

LR 太大：Loss 剧烈振荡甚至爆炸；LR 太小：训练非常慢，看起来几乎不学习；合理 LR：能够稳定下降并逐渐细化。现代 Transformer 常使用 Warmup + Decay：开始小步稳定进入训练，后期减小步长精修。

## 51. Parameter 与 Hyperparameter

Parameter 是训练自动学的权重；Hyperparameter 是训练前由工程师设置的策略，例如 Learning Rate、Batch Size、Epoch、Weight Decay、Warmup Ratio、LoRA Rank。不要把二者混为一谈。

## 52. SGD、Momentum、Adam、AdamW 的高层区别

SGD 直接按当前梯度走；Momentum 带有历史方向；Adam 根据梯度一阶、二阶统计量为不同参数自适应步长；AdamW 在 Transformer/LLM 训练中很常见，并把 Weight Decay 处理方式与 Adam 更清楚地分离。

第一课不要求推导优化器公式，但要建立：Gradient 给信息，Optimizer 决定怎样使用信息。

## 53. Gradient Accumulation：显存小也能模拟更大有效 Batch

若单卡只能放 Micro Batch=4，而希望 Effective Batch=32，可以累积 8 次梯度后再更新一次参数。

多 GPU 时：

\[
EffectiveBatch=PerDeviceBatch\times NumGPUs\times GradientAccumulation
\]

例如 4 GPU × 每卡 2 × Accumulation 8 = 64。

## 54. Micro-Batch 次数不等于 Optimizer Step

梯度累积期间会多次 Forward/Backward，但参数尚未改变；只有执行 Optimizer Step 时参数才更新。这一点在计算总训练步数、Scheduler 和日志时非常重要。

## 55. Shuffle 与 Split 是两个完全不同的问题

Split 决定哪些项目属于 Train/Val/Test，必须先防止泄漏；Shuffle 只是训练集内部每个 Epoch 重新打乱顺序，使 Batch 更接近整体分布。不能用“我已经 Shuffle 了”来证明没有项目级泄漏。

## 56. 训练曲线应该至少监控什么

至少记录 Train Loss、Validation Loss、Learning Rate、Gradient Norm、Step、Epoch；进入 GPU 工程后再增加显存、利用率、tokens/sec、samples/sec。

Train Loss 下降而 Validation 上升提示过拟合；Loss 剧烈振荡先检查 LR；Loss 长期不动要检查学习率、数据、可训练参数和梯度链路；突然爆炸要考虑梯度或数值稳定性。

## 57. 文本训练不能只看“样本数”

一条 100 Token 的资格条款和一条 8000 Token 的完整采购需求，在显存、计算和有效上下文上完全不同。政府采购文件从短公告到数百页投标文件跨度极大，因此还要关注 Tokens per Batch、Context Length、Chunking 与 Packing。

“一个 PDF = 一个训练样本”往往是非常粗糙甚至错误的数据单位。

## 58. GPU 在训练中的真正角色

GPU 擅长并行矩阵/张量计算，负责高吞吐 Forward、Backward 和 Optimizer 运算。概念上不要把 GPU 想成“知识存储器”；训练完成后的知识表现主要由参数 Checkpoint 表示。

## 59. 第五阶段完整计算练习

Dataset=24,000；GPU=2；每卡 Batch=4；Gradient Accumulation=3；Epoch=5。

\[
EffectiveBatch=4\times2\times3=24
\]

\[
StepsPerEpoch=24000/24=1000
\]

\[
TotalOptimizerSteps=1000\times5=5000
\]

若第 3 Epoch 后 Train Loss 继续下降但 Validation Loss 上升，优先保留第 2～3 Epoch 附近的最佳 Checkpoint，而不是因为预设 5 Epoch 就一定用最后一个。

## 60. 第五阶段五个核心心智模型

1. Batch 是对整体数据分布的有噪声局部估计。
2. Epoch 是训练深度，不是模型能力分数。
3. Gradient、Optimizer、Learning Rate 是三个不同角色。
4. 训练本质是随机/有噪声优化，曲线抖动不等于失败。
5. Monitoring 本身就是训练的一部分，没有日志就难以诊断。

---
