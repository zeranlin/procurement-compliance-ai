# 第一课 · 第 4 阶段：概率、Loss、Gradient 与反向传播

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：MEDIUM。** 审计原因：核心心智模型出现偏后，阅读前段缺少认知锚点。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Score 与 Decision 分离：模型分数不是最终业务动作。**
2. **Loss 定义错误的几何形状：不同 Loss 对不同错误施加不同压力。**
3. **Gradient 是 Credit Assignment：决定每个参数应该承担多少纠错责任。**
4. **训练是无数微小参数更新的累积：不是一次“灌知识”。**
5. **Confidence ≠ Truth：概率必须经过评测、校准和证据验证。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Loss` | 损失函数：把预测错误压缩成可优化的数值信号 |
| `Gradient` | 梯度：损失对参数变化方向和敏感度的局部信息 |
| `Optimizer` | 优化器：依据梯度规则更新参数 |
| `Threshold` | 阈值：把连续分数转成业务动作的决策门槛 |
| `Recall` | 召回率：真实风险中被系统成功找出的比例 |
| `Calibration` | 校准：使模型置信度更接近实际正确率 |
| `Backpropagation` | 反向传播：把最终损失沿计算图反向分配到参数 |
| `Learning Rate` | 学习率：控制每次参数更新步幅 |

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

这一阶段第一次真正进入“训练内部”：`Logit → Sigmoid → Probability → Cross Entropy → Gradient → Backprop → 参数更新`。

核心链路：

\[
X \rightarrow z \rightarrow \sigma(z) \rightarrow p \rightarrow Loss \rightarrow Gradient \rightarrow Update
\]

最重要的认识是：模型并不理解我们的业务目标，它只在努力降低我们定义的 Loss。

---

## 1. 第四阶段总链路

这一阶段把“预测分数如何变成 Loss，再变成参数更新”完整串起来。

> **公式 / 关键表达**
>
> X → z → Sigmoid → p → Cross Entropy → Loss → Gradient → 参数更新

---

## 2. 为什么模型不直接输出 0/1

如果只有硬分类，训练无法区分“差一点错”和“极其自信地错”。连续分数提供更细反馈。

---

## 3. Logit z

线性模型先产生一个不受限制的原始分数。

> **公式 / 关键表达**
>
> z=wᵀX+b

---

## 4. Logit 的直觉

z 很大为正时倾向风险，z 很大为负时倾向正常，z≈0 时模型犹豫。

---

## 5. Sigmoid

把任意实数压到 0～1。

> **公式 / 关键表达**
>
> σ(z)=1/(1+e^{-z})

---

## 6. Sigmoid 数值直觉

z=-5≈0.007，-2≈0.12，0=0.5，2≈0.88，5≈0.993。

---

## 7. Logistic Regression

把线性 logit 与 Sigmoid 结合，得到二分类概率分数。

> **公式 / 关键表达**
>
> P(Y=1|X)=σ(wᵀX+b)

---

## 8. 概率分数不等于真实概率

模型输出 0.82 不自动意味着现实有 82% 概率存在风险；是否能这样解释要看 Calibration。

---

## 9. Binary Cross Entropy

二分类常用交叉熵衡量概率预测。

> **公式 / 关键表达**
>
> L=−[y log p +(1−y)log(1−p)]

---

## 10. 当 y=1

Loss 简化为 −log p。预测越接近 1，Loss 越小。

> **公式 / 关键表达**
>
> y=1 ⇒ L=−log p

---

## 11. 当 y=0

Loss 简化为 −log(1−p)。预测越接近 0，Loss 越小。

> **公式 / 关键表达**
>
> y=0 ⇒ L=−log(1−p)

---

## 12. 自信地错会被重罚

真实 y=1 时，p=.99→Loss≈.01，p=.5→.693，p=.2→1.609，p=.01→4.605。

---

## 13. Cross Entropy 的核心直觉

它不断推动正确答案的概率质量上升，并强烈惩罚高置信度错误。

---

## 14. Loss 的“几何形状”

不同 Loss 对不同错误的惩罚方式不同，因此 Loss 本身就是我们对模型学习方向的设计。

---

## 15. Gradient

∂L/∂w 表示参数轻微变化对 Loss 的影响方向和敏感度。

---

## 16. Gradient Descent

沿 Loss 下降方向更新参数。

> **公式 / 关键表达**
>
> w_new=w_old−η∂L/∂w

---

## 17. BCE + Sigmoid 的漂亮结果

对 logit 的导数非常简洁。

> **公式 / 关键表达**
>
> ∂L/∂z=p−y

---

## 18. 当 y=1,p=.2

p−y=-.8，说明需要强烈把 z 往上推。

---

## 19. 当 y=1,p=.95

p−y=-.05，只需小幅修正。

---

## 20. 当 y=0,p=.9

p−y=.9，说明模型高置信度错，需要强烈把 z 往下推。

---

## 21. 线性权重的梯度

如果 z=wᵀx+b，则每个权重梯度包含对应输入特征。

> **公式 / 关键表达**
>
> ∂L/∂w_i=(p−y)x_i

---

## 22. 这就是 Credit Assignment 的起点

最终错误信号如何分配回每个参数，是后面 Backprop 的核心问题。

---

## 23. Forward Pass

输入从前往后经过模型得到预测。

---

## 24. Backward Pass

从 Loss 反向计算各层参数梯度。

---

## 25. Backpropagation

反向传播不是“把答案传回去”，而是高效应用链式法则计算梯度。

---

## 26. Optimizer

梯度给方向，Optimizer 决定如何利用当前与历史梯度更新参数。

---

## 27. Learning Rate 再理解

η 是每次参数移动尺度。过大振荡/发散，过小收敛缓慢。

---

## 28. Loss 与 Metric 不同

Loss 是可微训练目标；Recall/F1 等 Metric 是业务评估指标，通常不能直接拿来反向传播。

---

## 29. 业务重视 Recall 怎么办

可以通过 Class Weight、Focal Loss、采样、阈值、Cost-sensitive 设计让训练更接近业务目标。

---

## 30. Score 与 Decision 分离

模型负责输出连续 Score；业务层通过 Threshold 与策略把 Score 变成行动。

> **公式 / 关键表达**
>
> X → Score/Probability → Threshold → Decision

---

## 31. 为什么不同风险可以不同 Threshold

高代价 FN 的风险类型可以用更宽松阈值保障召回。

---

## 32. Confidence ≠ Truth

模型越自信不代表越接近现实；这将在第 11 阶段进入 Calibration 与不确定性。

---

## 33. 政府采购例子：高置信错误

模型把“项目地点在本市”判 0.99 风险，说明它可能学了关键词捷径；Cross Entropy 会在正确标签下强烈纠正这类错误。

---

## 34. 第四阶段五个心智模型

Score 与 Decision 分离；Loss 定义错误惩罚；Gradient 是信用分配；训练是微小参数更新的累积；Confidence 不等于 Truth。

---

## 35. 一句最重要的话

模型并不理解我们的业务目标，它只在努力降低我们定义的 Loss。

> **专家心智模型**
>
> 如果业务目标没有进入数据、Loss、采样、阈值或系统策略，模型不会凭空替我们优化它。

---

## 36. 思维实验：p=.99 但错了

为什么比 p=.51 错得更值得关注？因为它既带来更大 Cross Entropy，也暴露模型内部可能存在非常确定的错误规律。

---

## 37. 第四阶段掌握标准

你应能解释 Logit、Sigmoid、Cross Entropy、Gradient、Forward/Backward、Optimizer，以及 Loss 与 Metric 的区别。

---

---

## 38. 为什么不让模型直接输出 0 或 1

如果模型只输出硬分类，我们无法区分“差一点错”和“非常自信地错”。连续分数让训练系统知道错误程度，也允许后续使用不同 Threshold。

最简单二分类模型先计算 Logit：

\[
z=w^TX+b
\]

再用 Sigmoid 映射到 0～1：

\[
p=\sigma(z)=\frac{1}{1+e^{-z}}
\]

## 39. Sigmoid 数值直觉

| z | p |
|---:|---:|
| -5 | ≈0.007 |
| -2 | ≈0.12 |
| 0 | 0.50 |
| 2 | ≈0.88 |
| 5 | ≈0.993 |

z=0 表示模型处于边界；z 大幅为正或负表示模型把样本推向某一侧。这个 p 是模型分数，不自动等于真实世界经过校准的客观概率。

## 40. Binary Cross Entropy 为什么适合概率分类

\[
L=-[y\log p+(1-y)\log(1-p)]
\]

当 y=1 时，Loss=-log p。预测 0.99 的 Loss 约 0.01，预测 0.5 是 0.693，预测 0.2 是 1.609，预测 0.01 达到约 4.605。它会特别重罚“非常自信地答错”。

## 41. Cross Entropy 的核心直觉：把概率质量推向正确答案

Loss 并不要求模型先形成我们理解的法律概念，它只是让正确标签的概率变高、错误标签的概率变低。模型内部最终形成什么表示，是大量这种压力共同作用的结果。

## 42. 最漂亮的一条导数：Sigmoid + BCE 得到 p-y

对于二分类：

\[
\frac{\partial L}{\partial z}=p-y
\]

若真实 y=1、模型 p=0.2，则误差信号为 -0.8，更新压力很强；若 p=0.95，则只有 -0.05，说明已经接近正确方向，不需要大改。

## 43. 误差信号如何进一步传给权重

在线性模型中：

\[
\frac{\partial L}{\partial w_i}=(p-y)x_i
\]

这就是 Credit Assignment 的最小版本：最终错误会沿计算图向后分配到对结果有贡献的参数。深层神经网络的 Backpropagation 本质上把同样思想扩展到很多层。

## 44. Forward、Backward、Optimizer 三者不要混淆

Forward：用当前参数从 X 算到预测；Backward：从 Loss 往回计算梯度；Optimizer：根据梯度和自己的更新规则真正修改参数。

可以用类比：Gradient 是坡度方向，Optimizer 是走路策略，Learning Rate 是步长。

## 45. Loss 与 Metric 为什么可以不同

训练需要可微 Loss，因此常用 Cross Entropy；业务评估可能更关心 Recall、F2、High-Risk Recall。可以通过 Class Weight、Focal Loss、Sampling、Threshold 和成本敏感策略，让训练目标更贴近业务指标。

## 46. Score 与 Decision 必须分离

完整链路应该是：

\[
X\rightarrow Score\rightarrow Threshold\rightarrow Decision
\]

这意味着同一模型可以在不同业务流程使用不同 Decision Policy，不必为了每个阈值重新训练模型。

## 47. Confidence ≠ Truth

模型输出 0.82 不自动意味着“现实世界有 82% 概率违规”。是否可以把模型概率当成现实概率，需要额外做 Calibration。这个提醒会在第 11 阶段发展成完整的概率校准与选择性预测体系。

## 48. 一个采购条款的单步更新直觉

若条款真实是风险 y=1，模型只给 p=0.1，它会产生很大 Loss 和负的 p-y，参数更新会尝试把未来类似输入的 z 往正方向推。如果同类正确样本反复出现，这种微小更新会累计成稳定模式。

但若标签本身错成 y=0，同样机制会非常认真地把模型往错误方向教。这再次说明数据和标签是训练系统的一部分。

## 49. 第四阶段五个核心心智模型

1. **Score 与 Decision 分离**：模型分数不是最终业务动作。
2. **Loss 定义错误的几何形状**：不同 Loss 对不同错误施加不同压力。
3. **Gradient 是 Credit Assignment**：决定每个参数应该承担多少纠错责任。
4. **训练是无数微小参数更新的累积**：不是一次“灌知识”。
5. **Confidence ≠ Truth**：概率必须经过评测、校准和证据验证。

如果只记一句：

\[
\boxed{模型并不理解我们的业务目标，它只在努力降低我们定义的Loss。}
\]

---
