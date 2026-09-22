# 第二课 · 第 6 阶段：Optimizer 与 Learning Rate——梯度已经算出来了，参数究竟应该怎样迈出下一步？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Gradient 告诉你局部方向，Optimizer 决定怎样利用当前和历史梯度真正更新参数。**
2. **Learning Rate 是最关键的更新尺度：太大可能震荡/发散，太小可能训练极慢或停在差的区域。**
3. **Adam / AdamW 会利用梯度一阶、二阶统计量做自适应更新，它不是“自动保证收敛”的魔法。**
4. **Weight Decay 与 Learning Rate 是不同控制量：前者用于参数规模正则化，后者控制更新步幅。**
5. **Warmup / Decay / Scheduler 属于完整优化策略的一部分，不能把“优化器名称”当成全部训练方案。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Optimizer` | 优化器：依据梯度规则更新参数 |
| `Learning Rate` | 学习率：控制每次参数更新步幅 |
| `Gradient` | 梯度：损失对参数变化方向和敏感度的局部信息 |
| `Loss` | 损失函数：把预测错误压缩成可优化的数值信号 |
| `Batch` | 批次：一次参与计算的一组样本 |
| `Step` | 训练步：通常指一次优化器更新 |
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `Gradient Accumulation` | 梯度累积：多次小 Batch 累积梯度后再更新参数 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Backpropagation` | 反向传播：把最终损失沿计算图反向分配到参数 |
| `State` | 状态：保存任务进度、事实和待办 |
| `LoRA` | LoRA：冻结大部分基座参数，只训练低秩增量矩阵 |

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

第 5 阶段，我们把最重要的一件事搞清楚了：

\[
\boxed{
Backward
\rightarrow
\nabla_\theta L
}
\]

也就是说，Backpropagation 给每一个参数算出了：

> 当前 Loss 对这个参数的局部敏感度。

但这还没有完成学习。

假设某个参数：

\[
w=2.0
\]

梯度：

\[
g=\frac{\partial L}{\partial w}=30
\]

现在怎么办？

直接：

\[
w\leftarrow w-30
\]

显然可能一步飞出银河系。

所以真正训练还需要一个新的决策系统：

\[
\boxed{
Gradient
\rightarrow
Optimizer
\rightarrow
ParameterUpdate
}
\]

这一阶段就是要把这件事彻底拆开。

---

## 1. 先把训练闭环补完整

现在我们已经学过：

\[
X
\rightarrow
Forward
\rightarrow
Prediction
\rightarrow
Loss
\rightarrow
Backward
\]

第 6 阶段补最后一步：

\[
\boxed{
OptimizerStep
}
\]

完整训练闭环：

\[
\boxed{
Batch
\rightarrow
Forward
\rightarrow
Loss
\rightarrow
Backward
\rightarrow
Optimizer
\rightarrow
NewParameters
}
\]

然后下一批数据再次开始。

---

## 2. Backward 和 Optimizer 再严格区分一次

Backward 回答：

\[
\boxed{
当前Loss对每个参数的梯度是多少？
}
\]

Optimizer 回答：

\[
\boxed{
知道这些梯度以后，
参数具体应该移动多少？
}
\]

所以：

\[
\nabla_\theta L
\]

不是参数更新本身。

真正更新：

\[
\Delta\theta
\]

由 Optimizer 决定。

---

## 3. 最基础 Optimizer：Gradient Descent

最基础公式：

\[
\boxed{
\theta_{t+1}
=
\theta_t
-
\eta\nabla_\theta L
}
\]

其中：

\[
\theta_t
\]

是当前参数。

\[
\nabla_\theta L
\]

是梯度。

\[
\eta
\]

就是：

# Learning Rate

学习率。

---

## 4. Learning Rate 在做什么？

Gradient 告诉我们：

> 哪边是上坡，哪边是下坡。

Learning Rate 决定：

> 一步迈多远。

所以一个非常稳定的直觉是：

\[
\boxed{
Gradient
=
Direction+LocalSlope
}
\]

\[
\boxed{
LearningRate
=
StepSizeScale
}
\]

---

## 5. 第一个核心心智模型

### 心智模型 ①：梯度给方向，Optimizer 决定怎样走，Learning Rate 控制基本步长

不要把三者混成一件事。

训练实际上是：

```text
Loss
↓
Gradient
↓
Optimizer rule
↓
Update
↓
New Parameters
```

---

## 6. 一个最简单数值例子

假设：

\[
w=3
\]

梯度：

\[
g=4
\]

Learning Rate：

\[
\eta=0.1
\]

则：

\[
w_{new}
=
3-0.1(4)
\]

所以：

\[
\boxed{
w_{new}=2.6
}
\]

这就是最普通的一步 Gradient Descent。

---

## 7. 如果 LR = 0.01 呢？

\[
w_{new}
=
3-0.01(4)
\]

得到：

\[
\boxed{
2.96
}
\]

方向一样。

但走得：

> 更小。

---

## 8. 如果 LR = 1 呢？

\[
w_{new}
=
3-1(4)
\]

得到：

\[
-1
\]

可能直接：

> 越过低 Loss 区域。

所以 Learning Rate 是训练里最重要的超参数之一。

---

## 9. 为什么不能直接找到 Loss 最低点？

因为真实神经网络可能有：

\[
10^9
\]

甚至更多参数。

Loss：

\[
L(\theta_1,\theta_2,\ldots,\theta_n)
\]

存在于一个极高维空间。

我们不能：

> 把所有参数组合都试一遍。

只能利用当前局部信息：

\[
\nabla L
\]

一点一点走。

---

## 10. Loss Landscape

可以把：

\[
L(\theta)
\]

想成一个地形：

# Loss Landscape

损失地形。

低处：

> Loss 小。

高处：

> Loss 大。

训练相当于：

> 在超高维山地里寻找低地。

---

## 11. 一维时比较简单

例如：

\[
L(w)=(w-3)^2
\]

最低点：

\[
w=3
\]

导数：

\[
\frac{dL}{dw}
=
2(w-3)
\]

如果：

\[
w=5
\]

梯度：

\[
4
\]

于是向左走。

---

## 12. 但神经网络不是一维

真实参数可能：

\[
\theta\in\mathbb R^{7B}
\]

Loss Landscape 不是二维山谷。

而是：

> 数十亿维的复杂几何空间。

所以所谓“往下走”：

\[
-\nabla L
\]

本质是：

> 当前点最陡下降方向。

---

## 13. Gradient Descent 为什么叫“Descent”？

因为：

\[
-\nabla L
\]

在一阶近似下，是：

> Loss 下降最快的局部方向。

注意：

# 局部

不是说：

> 一定通往全局最优。

---

## 14. Taylor Expansion 的直觉

在当前参数：

\[
\theta
\]

附近，小幅改变：

\[
\Delta\theta
\]

有：

\[
L(\theta+\Delta\theta)
\approx
L(\theta)
+
\nabla L^T\Delta\theta
\]

如果：

\[
\Delta\theta=-\eta\nabla L
\]

那么：

\[
\nabla L^T\Delta\theta
=
-\eta\|\nabla L\|^2
\]

通常为负。

所以小步时：

> Loss 倾向下降。

---

## 15. 这也解释为什么步长不能无限大

上面的推导依赖：

> 局部线性近似。

如果一步：

\[
\Delta\theta
\]

特别大，

那么：

> 当前 Gradient 对远处已经不再可靠。

这就是为什么：

\[
LearningRate
\]

必须受控制。

---

## 16. 一个政府采购模型例子

假设风险模型某个抽象参数：

\[
w_{local}
\]

表示某种对“地域性条件模式”的敏感方向。

当前 Batch：

> 模型大量漏掉真正风险样本。

Backward 给：

\[
g=-0.6
\]

如果：

\[
\eta=0.01
\]

那么：

\[
\Delta w
=
-0.01(-0.6)
=
+0.006
\]

于是参数：

> 略微加强这一方向。

---

## 17. 为什么训练需要很多 Step？

因为每一次更新通常都很小：

\[
\Delta\theta
\]

模型不会：

> 看一批数据就完全重写知识。

而是：

\[
\boxed{
Millions\ of\ Small\ Updates
}
\]

逐渐塑造参数。

---

## 18. Step 到底是什么？

通常一次：

\[
optimizer.step()
\]

称为一个：

# Optimization Step

或者：

# Global Step

即：

> 参数真正更新一次。

---

## 19. Step 和 Batch 不一定一一对应

没有 Gradient Accumulation 时：

```text
1 Batch
→ 1 Backward
→ 1 Optimizer Step
```

但如果 Gradient Accumulation = 8：

```text
Micro Batch 1 → Backward
Micro Batch 2 → Backward
...
Micro Batch 8 → Backward
↓
Optimizer Step
```

所以：

\[
\boxed{
8个MicroBatch
\rightarrow
1个OptimizerStep
}
\]

---

## 20. 第二个核心心智模型

### 心智模型 ②：真正的训练时间尺度是 Optimizer Step，而不仅仅是“看了多少 Batch”

例如：

> Learning Rate Scheduler

通常很多情况下按照：

\[
OptimizerStep
\]

推进。

不是按照：

> 每一次 Forward。

---

## 21. 最理想的 Gradient 是什么？

假设训练集有：

\[
N
\]

个样本。

总 Loss：

\[
L(\theta)
=
\frac1N
\sum_{i=1}^N
L_i(\theta)
\]

完整梯度：

\[
\boxed{
\nabla L
=
\frac1N
\sum_i\nabla L_i
}
\]

这叫：

# Full-Batch Gradient

---

## 22. 问题是什么？

如果：

\[
N=100,000,000
\]

每更新一次参数都必须：

> 把全部数据跑一遍。

成本太高。

所以现实训练：

> 使用部分样本估计梯度。

---

## 23. Stochastic Gradient Descent

严格历史意义下：

# SGD

可以指：

> 每次随机取一个或小批样本估计梯度。

现代工程里 `SGD` 这个名字经常对应：

> Mini-batch SGD。

---

## 24. Mini-batch 梯度

假设 Batch：

\[
B
\]

则：

\[
g_B
=
\frac1{|B|}
\sum_{i\in B}
\nabla L_i
\]

用：

\[
g_B
\]

近似：

\[
\nabla L_{full}
\]

---

## 25. 这个近似有噪声

不同 Batch：

\[
B_1,B_2
\]

可能得到：

\[
g_1\neq g_2
\]

所以参数路线不是：

> 平滑直线下山。

更像：

> 一边晃一边往低处走。

---

## 26. 这听起来像缺点，但不全是

Gradient Noise 有时可以：

> 帮助优化过程跳出一些狭窄区域。

因此训练中的随机性：

> 并不全是坏东西。

---

## 27. Batch Size 和 Gradient Noise

通常：

\[
BatchSize\uparrow
\]

梯度估计：

> 更稳定。

\[
BatchSize\downarrow
\]

梯度：

> 更 noisy。

所以：

\[
\boxed{
BatchSize
也会改变Optimizer看到的世界
}
\]

---

## 28. 这就是为什么改变 Batch Size 不能只看显存

它不仅是：

> GPU 工程参数。

也会改变：

\[
OptimizationDynamics
\]

即训练动力学。

---

## 29. 假设 Loss Landscape 是一个狭长山谷

横向：

> 很陡。

纵向：

> 很缓。

你真正想沿山谷：

> 向前走。

但 Gradient 每一步都可能：

> 强烈左右摆动。

---

## 30. 一个二维直觉

假设：

\[
L(w_1,w_2)
=
100w_1^2+w_2^2
\]

对：

\[
w_1
\]

方向非常陡。

对：

\[
w_2
\]

方向很缓。

---

## 31. Gradient

\[
\nabla L
=
\begin{bmatrix}
200w_1\\
2w_2
\end{bmatrix}
\]

所以：

\[
w_1
\]

方向的梯度可能远大于：

\[
w_2
\]

训练就会：

> 在陡峭方向来回震荡。

---

## 32. 这就是 Optimization Geometry

同样的一个全局 LR：

\[
\eta
\]

要同时服务：

> 很陡的维度和很平的维度。

非常困难。

---

## 33. 如果 LR 为照顾陡峭方向设得很小

那么平坦方向：

> 走得极慢。

如果 LR 为平坦方向设得很大：

> 陡峭方向可能爆炸。

这就是优化器要面对的问题之一。

---

## 34. Momentum 想解决什么？

基本思路：

> 不要只看当前这一批数据的 Gradient。

还参考：

> 最近一段时间的方向。

这叫：

# Momentum

动量。

---

## 35. 一个常见形式

\[
v_t
=
\beta v_{t-1}
+
g_t
\]

然后：

\[
\theta_{t+1}
=
\theta_t
-
\eta v_t
\]

其中：

\[
v_t
\]

可以理解为：

> 带历史记忆的更新方向。

---

## 36. 另一种等价风格

有些教材写：

\[
v_t
=
\beta v_{t-1}
+
(1-\beta)g_t
\]

本质：

> 都是在做梯度的指数移动平均。

具体缩放约定不同。

---

## 37. 什么是 Exponential Moving Average？

EMA：

\[
m_t
=
\beta m_{t-1}
+
(1-\beta)x_t
\]

最近数据：

> 权重更高。

很久以前的数据：

> 权重指数衰减。

---

## 38. 如果 \(\beta=0.9\)

新值：

\[
10\%
\]

进入当前平均。

历史：

\[
90\%
\]

继续保留。

这就让 Optimizer：

> 有了“惯性”。

---

## 39. 第三个核心心智模型

### 心智模型 ③：Momentum 不是让参数“走得更猛”，核心是积累持续方向、抵消高频抖动

如果连续很多 Batch 都说：

> 向右。

Momentum：

> 会越来越确信向右。

如果左右交替：

> 会部分抵消。

---

## 40. 山谷中的 Momentum

横向梯度：

```text
左
右
左
右
左
右
```

平均以后：

> 接近抵消。

纵向梯度：

```text
前
前
前
前
前
```

持续积累。

于是模型：

> 更顺畅地沿山谷前进。

---

## 41. 一个简单数值例子

假设：

\[
\beta=0.9
\]

初始：

\[
v_0=0
\]

第一步：

\[
g_1=2
\]

如果使用：

\[
v_t=0.9v_{t-1}+0.1g_t
\]

则：

\[
v_1=0.2
\]

---

## 42. 第二步梯度仍然是 2

\[
v_2
=
0.9(0.2)+0.1(2)
\]

\[
=
0.38
\]

第三步：

\[
v_3
=
0.9(0.38)+0.2
\]

\[
=
0.542
\]

持续方向被：

> 逐渐积累。

---

## 43. 如果突然梯度变成 -2

\[
v_4
=
0.9(0.542)+0.1(-2)
\]

\[
=
0.2878
\]

虽然当前 Gradient 已经反向，

Momentum：

> 不会立刻完全掉头。

---

## 44. 这是好事还是坏事？

两者都有可能。

优点：

> 不被单个 noisy Batch 轻易带偏。

缺点：

> 如果真的到了该转弯的位置，可能产生 overshoot。

所以：

\[
Momentum
\]

也是一个需要调节的系统。

---

## 45. Nesterov Momentum

你以后可能看到：

# Nesterov Momentum

核心直觉：

> 普通 Momentum 是看当前位置 Gradient 再走。

Nesterov：

> 先大致看一下按照动量会走到哪里，再在那里估计修正方向。

---

## 46. 现在不需要死背 Nesterov 公式

这一阶段更重要的是建立：

\[
\boxed{
Optimizer
可以利用GradientHistory
}
\]

而不是：

> 只使用当前一步。

Adam 也是从这里继续发展。

---

## 47. SGD 的一个限制

普通 SGD：

\[
\Delta\theta_i
=
-\eta g_i
\]

所有参数共用：

\[
\eta
\]

只是 Gradient 本身不同。

---

## 48. 现实中不同维度梯度尺度差异可能巨大

参数 A：

\[
g_A=0.0001
\]

参数 B：

\[
g_B=100
\]

同一个 LR：

> 很难同时合适。

于是出现：

# Adaptive Optimizer

自适应优化器。

---

## 49. AdaGrad 的核心思想

某个参数历史梯度一直很大：

> 那就自动缩小它未来的有效步长。

某个参数梯度一直很小：

> 相对允许走大一些。

---

## 50. 累积平方梯度

\[
s_t
=
s_{t-1}
+
g_t^2
\]

然后：

\[
\theta_{t+1}
=
\theta_t
-
\eta
\frac{g_t}
{\sqrt{s_t}+\epsilon}
\]

---

## 51. 为什么平方？

因为：

\[
g_t^2
\]

只关心：

> 梯度幅度。

不关心：

> 正负方向。

所以：

\[
s_t
\]

反映该参数历史上：

> 梯度有多大。

---

## 52. AdaGrad 的问题

因为：

\[
s_t
\]

一直累计，只增不减。

训练时间很长以后：

\[
\sqrt{s_t}
\]

越来越大。

于是有效 LR：

> 越来越小。

最终可能：

> 几乎走不动。

---

## 53. RMSProp 的改进

不要把从训练开始以来的平方梯度：

> 永久累加。

而是做：

# Exponential Moving Average

---

## 54. 公式直觉

\[
v_t
=
\beta v_{t-1}
+
(1-\beta)g_t^2
\]

更新：

\[
\boxed{
\theta_{t+1}
=
\theta_t
-
\eta
\frac{g_t}
{\sqrt{v_t}+\epsilon}
}
\]

---

## 55. 这相当于什么？

每个参数都有一个：

> 自己的梯度尺度估计器。

Gradient 经常很大：

> 分母变大。

有效步长：

> 自动变小。

---

## 56. \(\epsilon\) 是干什么的？

例如：

\[
\epsilon=10^{-8}
\]

主要用于：

> 数值稳定。

避免：

\[
\sqrt{v_t}=0
\]

时除以 0。

---

## 57. 现在终于到最常见的 Adam

# Adam

可以粗略理解为：

\[
\boxed{
Momentum
+
AdaptiveScale
}
\]

即同时维护：

> 梯度一阶统计量。

和：

> 梯度平方的二阶统计量。

---

## 58. 一阶矩

\[
m_t
=
\beta_1m_{t-1}
+
(1-\beta_1)g_t
\]

它像：

> Momentum。

记录：

> 梯度平均方向。

---

## 59. 二阶矩

\[
v_t
=
\beta_2v_{t-1}
+
(1-\beta_2)g_t^2
\]

记录：

> 梯度平方的移动平均。

也就是：

> 近期梯度尺度。

---

## 60. Adam 核心更新

经过偏差修正后，大致：

\[
\boxed{
\theta_{t+1}
=
\theta_t
-
\eta
\frac{\hat m_t}
{\sqrt{\hat v_t}+\epsilon}
}
\]

这就是 Adam 的核心。

---

## 61. 为什么分子是 \(m_t\)？

它告诉：

> 最近总体往哪个方向走。

---

## 62. 为什么分母是 \(\sqrt{v_t}\)？

它告诉：

> 这个参数近期梯度尺度有多大。

于是：

> 大梯度维度会被适当缩小。

> 小梯度维度相对放大。

---

## 63. 第四个核心心智模型

### 心智模型 ④：Adam 给每个参数形成了“带历史记忆的自适应有效步长”

它不是一个统一：

\[
\eta
\]

直接乘全部 Gradient。

实际更新还受：

\[
m_t
\]

\[
v_t
\]

影响。

所以真正的：

\[
EffectiveStep
\]

比表面 LR 复杂得多。

---

## 64. 常见 Adam 默认值

经常看到：

\[
\beta_1=0.9
\]

\[
\beta_2=0.999
\]

\[
\epsilon=10^{-8}
\]

这些是常见默认值。

不是：

> 宇宙真理。

不同模型和训练配方可能调整。

---

## 65. 为什么 \(\beta_2\) 经常很大？

因为我们希望：

> 梯度尺度估计相对平稳。

例如：

\[
0.999
\]

意味着：

> 二阶统计记忆很长。

---

## 66. 什么叫 Bias Correction？

初始化时：

\[
m_0=0
\]

\[
v_0=0
\]

训练早期 EMA：

> 会偏向 0。

Adam 会做：

\[
\hat m_t
=
\frac{m_t}{1-\beta_1^t}
\]

以及：

\[
\hat v_t
=
\frac{v_t}{1-\beta_2^t}
\]

进行修正。

---

## 67. 为什么第一步尤其需要修正？

例如：

\[
\beta_1=0.9
\]

第一步：

\[
m_1=0.1g_1
\]

如果不修正：

> 看起来梯度平均只有真实值的十分之一。

修正：

\[
\frac{0.1g_1}{1-0.9}
=
g_1
\]

就恢复合理尺度。

---

## 68. 现在做一个极简 Adam 例子

假设：

\[
g_1=2
\]

\[
\beta_1=0.9
\]

则：

\[
m_1=0.2
\]

偏差修正：

\[
\hat m_1
=
\frac{0.2}{0.1}
=
2
\]

---

## 69. 二阶矩

假设：

\[
\beta_2=0.999
\]

则：

\[
v_1
=
0.001(2^2)
\]

\[
=0.004
\]

修正：

\[
\hat v_1
=
\frac{0.004}{0.001}
=
4
\]

---

## 70. Adam 更新

忽略很小的 \(\epsilon\)：

\[
\frac{\hat m_1}{\sqrt{\hat v_1}}
=
\frac2{2}
=
1
\]

所以：

\[
\Delta w
\approx
-\eta
\]

这说明 Adam：

> 对原始梯度尺度做了归一化式调整。

---

## 71. 但不要误以为 Adam 每一步永远都是 \(\eta\)

随着历史：

\[
m_t,v_t
\]

不断变化，

不同参数的：

> 实际更新大小也会变化。

所以 Adam 是一个动态系统。

---

## 72. 为什么现在训练 Transformer 经常看到 AdamW？

因为现代 Transformer / LLM 训练中：

# AdamW

非常常见。

它最重要的区别之一：

> 对 Weight Decay 的处理方式。

---

## 73. 先说 Weight Decay

我们不希望某些权重：

> 无限制变得很大。

一个直觉办法：

> 每一步都稍微把参数往 0 拉一点。

例如：

\[
\theta
\leftarrow
(1-\eta\lambda)\theta
\]

这就是：

# Weight Decay

权重衰减的直觉。

---

## 74. 为什么叫 Decay？

即使某一步：

\[
Gradient=0
\]

只要 Weight Decay 存在，

参数：

\[
|\theta|
\]

仍会略微缩小。

---

## 75. L2 Regularization

经典目标中也可以加入：

\[
L_{total}
=
L_{data}
+
\frac{\lambda}{2}\|\theta\|^2
\]

于是梯度：

\[
\nabla L_{total}
=
\nabla L_{data}
+
\lambda\theta
\]

---

## 76. 在普通 SGD 中

L2 Regularization：

> 与 Weight Decay 在很多情况下可以形成等价更新。

但是：

> 在 Adam 这种 adaptive optimizer 里，两者不再简单等价。

---

## 77. AdamW 的关键思想

把：

> 优化 Loss 的 Gradient Update

和：

> Weight Decay

分离。

也就是：

\[
\boxed{
AdaptiveGradientStep
+
SeparateWeightDecay
}
\]

---

## 78. 一个简化 AdamW 更新

可以想成：

\[
\theta
\leftarrow
\theta
-
\eta\cdot AdamDirection
-
\eta\lambda\theta
\]

重点：

> Weight Decay 不先混进 Adam 的自适应 Gradient 归一化里。

---

## 79. 第五个核心心智模型

### 心智模型 ⑤：AdamW 中“学数据”和“控制参数规模”是两个分开的作用

Gradient：

> 来自任务 Loss。

Weight Decay：

> 是额外正则化偏好。

不要把：

\[
WeightDecay
\]

理解成：

> Learning Rate 的另一种写法。

---

## 80. Weight Decay 越大越好吗？

当然不是。

太小：

> 正则化作用弱。

太大：

> 参数可能被过度压缩，导致欠拟合或损害已有能力。

---

## 81. 所有参数都应该 Weight Decay 吗？

实践中经常：

> 不对 Bias、LayerNorm/RMSNorm 的某些参数应用 Weight Decay。

而主要对：

> 大型 Weight Matrix

应用。

具体要看训练配方。

---

## 82. 为什么 Norm 参数经常不 Decay？

因为它们通常：

> 控制缩放和偏移。

对它们做相同正则化：

> 未必符合设计目的。

所以常见 Optimizer Parameter Groups：

```text
Decay parameters

No-decay parameters
```

---

## 83. 很多人第一次训练会问

> SGD 还是 Adam？

> Adam 还是 AdamW？

这是重要的。

但很多时候：

\[
\boxed{
LearningRate
}
\]

对训练成败更直接。

同一个 AdamW：

LR 合适：

> 学得很好。

LR 大 100 倍：

> 直接炸掉。

---

## 84. LR 太大时会看到什么？

可能：

- Loss 不降；
- Loss 剧烈震荡；
- Loss 突然爆炸；
- Gradient Norm 异常；
- NaN / Inf；
- Validation 性能快速恶化。

---

## 85. LR 太小时呢？

典型现象：

- Loss 缓慢下降；
- 几千 Step 几乎没变化；
- GPU 很忙；
- 模型却没怎么学。

这是最贵的一种：

> “稳定地浪费算力”。

---

## 86. 一个重要区分

如果：

Train Loss 完全不下降，

不能立刻说：

> LR 太小。

还可能：

- 标签错；
- 数据管道错；
- Loss 写错；
- 参数被冻结；
- Gradient 为 0；
- Optimizer 没 step；
- 输入有问题。

所以仍然需要第一课的：

\[
Diagnosis
\]

---

## 87. LR 一定整个训练过程保持不变吗？

不一定。

现实训练经常使用：

# Learning Rate Scheduler

即：

\[
\eta_t
\]

随着 Step 改变。

---

## 88. 为什么需要 Scheduler？

训练早期：

> 参数离好区域很远。

中后期：

> 已经比较接近低 Loss 区域。

我们希望：

> 前期允许较大探索。

> 后期逐渐精细调整。

于是：

\[
LearningRate
\]

常随时间下降。

---

## 89. 最简单：Constant LR

整个训练：

\[
\eta_t=\eta
\]

优点：

> 简单。

短小实验：

> 完全可以先使用。

---

## 90. Step Decay

训练到某些节点：

\[
\eta
\]

突然乘：

\[
0.1
\]

例如：

```text
Epoch 1–10: 1e-3

Epoch 11–20: 1e-4

Epoch 21–30: 1e-5
```

传统深度学习中很常见。

---

## 91. Linear Decay

例如：

\[
\eta_t
=
\eta_{max}
\left(
1-\frac{t}{T}
\right)
\]

随着训练：

> 线性下降。

---

## 92. Cosine Decay

现代训练常见：

\[
\eta_t
=
\eta_{min}
+
\frac12
(\eta_{max}-\eta_{min})
\left(
1+\cos\frac{\pi t}{T}
\right)
\]

看起来复杂。

直觉很简单：

> 前期降得慢，中后期平滑下降。

---

## 93. 为什么 Cosine 很受欢迎？

因为它：

- 连续；
- 平滑；
- 没有突然跳变；
- 后期自然减小。

在 Transformer 训练和微调里：

> 经常看到。

---

## 94. 现在进入非常重要的 Warmup

训练开始时：

> 不直接使用最大 LR。

而是：

\[
0
\rightarrow
\eta_{max}
\]

慢慢升起来。

这叫：

# Learning Rate Warmup

---

## 95. 为什么刚开始反而要小？

因为训练刚开始：

- 参数状态尚未适应任务；
- Adam 的动量统计尚未稳定；
- 梯度可能比较剧烈；
- 大模型对早期错误更新很敏感。

如果一上来就：

> 大 LR 猛踩油门，

可能直接破坏参数。

---

## 96. Warmup 直觉

像汽车发动机：

> 刚启动先平稳加速。

而不是：

> 直接油门到底。

---

## 97. 常见 Warmup 形式

假设 Warmup Steps：

\[
T_w
\]

可以：

\[
\eta_t
=
\eta_{max}
\frac{t}{T_w}
\]

当：

\[
t<T_w
\]

线性升高。

---

## 98. 之后再 Decay

完整 Schedule 可能：

```text
Warmup
   /
  /
 /\
   \
    \
     \ Cosine Decay
```

也就是：

\[
\boxed{
Warmup
\rightarrow
PeakLR
\rightarrow
Decay
}
\]

---

## 99. 这是现代 LLM 训练很重要的配方结构

以后你看训练配置，经常会看到：

```yaml
learning_rate:
warmup_ratio:
lr_scheduler_type:
```

现在这些字段不再是：

> 配置魔法。

你知道它们都在控制：

\[
\eta_t
\]

---

## 100. 什么叫 Peak LR？

如果有 Warmup：

> Warmup 结束后达到的最高 LR。

例如：

\[
2\times10^{-4}
\]

然后开始下降。

---

## 101. 不同训练方式 LR 往往不同

概念上：

# Full Fine-tuning

修改所有参数。

所以通常：

> 需要更谨慎的小 LR。

而：

# LoRA

只训练少量新参数。

通常可以：

> 使用相对更大的 LR。

但没有一个数字：

> 对所有模型通用。

---

## 102. 为什么 Full Fine-tuning 更敏感？

因为：

> 原始模型全部 Weight 都在变化。

一个不合适的大 LR：

> 可能大范围破坏已有 Representation。

这和：

# Catastrophic Forgetting

也有关。

---

## 103. LoRA 为什么相对能承受较大 LR？

因为主要调整：

> Adapter 参数。

Base Model：

> 大部分被冻结。

因此原模型主干：

> 不会被直接大规模改写。

---

## 104. 为什么 Batch Size 变化经常伴随 LR 调整？

因为 Batch 越大：

> Gradient Noise 通常越小。

Optimizer 每一步看到：

> 更稳定的梯度估计。

所以一些训练配方会：

> 随 Batch 增大而增大 LR。

---

## 105. Linear Scaling Rule

经典经验之一：

如果 Batch：

\[
B\rightarrow kB
\]

LR：

\[
\eta\rightarrow k\eta
\]

称为：

# Linear Scaling Rule

但它只是：

> 一种经验启发式。

不是永远成立的定律。

---

## 106. 为什么不能机械套？

因为还取决于：

- Optimizer；
- Warmup；
- 模型大小；
- 数据；
- Loss；
- Batch 范围；
- 训练阶段。

所以正确方法仍然是：

> 实验。

---

## 107. Gradient Accumulation 增大 Effective Batch 后呢？

例如：

\[
PerDeviceBatch=2
\]

\[
GPUs=4
\]

\[
Accumulation=8
\]

则：

\[
EffectiveBatch
=
2\times4\times8
=
64
\]

Optimizer：

> 每次 Step 大约综合 64 条样本的梯度。

---

## 108. Accumulation=8 不代表学习率也必须 ×8

这是常见误区。

是否改变 LR：

> 要看你的原 baseline、目标 effective batch 和训练配方。

没有一条：

\[
Accumulation\uparrow
\Rightarrow
LR必须同比\uparrow
\]

的铁律。

---

## 109. Backward 以后顺序是什么？

典型：

```text
Backward
↓
Gradient Unscale（如果需要）
↓
Gradient Clipping
↓
Optimizer Step
```

因为 clipping：

> 应该作用在真正将用于参数更新的 Gradient 上。

---

## 110. Clip by Norm

如果：

\[
\|g\|>c
\]

就做：

\[
g
\leftarrow
g
\frac{c}{\|g\|}
\]

让方向不变。

但总体 Norm：

> 限制在 \(c\)。

---

## 111. 例如

Gradient：

\[
g=[3,4]
\]

Norm：

\[
5
\]

如果：

\[
maxNorm=1
\]

则缩放：

\[
[3,4]
\times
\frac15
\]

得到：

\[
[0.6,0.8]
\]

方向一样。

---

## 112. 为什么不直接每个值截到 [-1,1]？

那是另一种：

# Value Clipping

但会改变：

> 梯度整体方向。

Norm Clipping：

> 更常用于深度模型。

---

## 113. FP16 训练有什么特殊问题？

FP16 可表示数值范围：

> 比 FP32 小。

非常小的 Gradient：

> 可能 underflow 成 0。

于是历史上常用：

# Loss Scaling

---

## 114. Loss Scaling

先把 Loss：

\[
L
\]

乘一个大数：

\[
S
\]

那么 Gradient：

\[
S\nabla L
\]

也被放大。

避免：

> FP16 小梯度直接变 0。

---

## 115. Optimizer Step 前怎么办？

再：

> Unscale Gradient。

恢复正确尺度。

所以实际参数更新：

> 不应该被人为放大的 S 改变。

---

## 116. BF16 为什么通常更省心？

BF16：

> 指数范围接近 FP32。

虽然尾数精度较低，

但更不容易出现：

> FP16 那种梯度下溢问题。

因此现代支持 BF16 的 GPU 上：

> 大模型训练很常用 BF16。

---

## 117. 假设一个参数是 FP32

一个参数：

\[
4Bytes
\]

如果只是推理：

> 主要存 Weight。

但 Adam 训练还要：

- Weight；
- Gradient；
- First Moment \(m\)；
- Second Moment \(v\)。

---

## 118. 粗略理解

FP32 情况：

```text
Weight     4 Bytes
Gradient   4 Bytes
m          4 Bytes
v          4 Bytes
```

已经：

\[
16Bytes/parameter
\]

还没有算：

> Activations、临时 Tensor 等。

---

## 119. Mixed Precision 还可能有 Master Weights

某些训练方式可能维护：

> FP32 master copy。

所以总内存：

> 可能进一步增加。

这就是为什么训练一个 7B 模型：

> 远不止模型权重本身的十几 GB。

---

## 120. AdamW 为什么比 SGD 更占 Optimizer Memory？

SGD 最基础：

> 可以只需要 Gradient。

Momentum SGD：

> 多一个 velocity。

Adam：

> 需要 \(m\) 和 \(v\)。

所以：

\[
\boxed{
AdaptiveOptimizer
通常用更多OptimizerState换来更好的优化行为
}
\]

---

## 121. 这直接解释 LoRA 为什么省显存

如果 Base Model 有：

\[
7B
\]

参数。

但只有：

\[
20M
\]

LoRA 参数可训练。

Adam 的：

\[
m,v
\]

主要只需要为：

> 20M 可训练参数保存。

而不是：

> 7B 全部参数。

---

## 122. 所以 LoRA 节省的不只是 Gradient

还显著减少：

\[
\boxed{
OptimizerState
}
\]

这往往是训练显存的大头之一。

---

## 123. 为什么断点续训不能只保存 Model Weight？

假设训练到 Step：

\[
20000
\]

Adam 已经形成：

\[
m_{20000},v_{20000}
\]

如果只保存 Weight，

重新启动后：

\[
m=v=0
\]

Optimizer：

> 忘掉了历史。

---

## 124. 真正 Resume Training 应该保存

通常至少：

- Model State；
- Optimizer State；
- LR Scheduler State；
- Current Step；
- RNG State；
- GradScaler State（需要时）。

所以第一课第 9 阶段说：

\[
\boxed{
Checkpoint
\neq
WeightsOnly
}
\]

现在又得到内部解释。

---

## 125. 情况 A：Loss 突然爆炸

优先检查：

- LR 是否过大；
- Gradient Norm；
- NaN/Inf；
- Mixed precision；
- 数据异常；
- Loss 异常；
- Scheduler 是否突然跳变。

---

## 126. 情况 B：Loss 一直横盘

检查：

- LR 是否太小；
- Parameter 是否 requires_grad；
- `.grad` 是否非零；
- `optimizer.step()` 有没有执行；
- Loss 是否正确连接到模型；
- 数据与标签是否有效。

---

## 127. 情况 C：Train Loss 快速下降，Val 变差

这通常不能简单归咎：

> Optimizer。

更可能是：

# Overfitting

可能需要：

- Early stopping；
- 更好数据；
- Weight decay；
- Dropout；
- 降低训练步数；
- 更合理 LR。

---

## 128. 情况 D：Loss 剧烈来回震荡

可能：

\[
LR
\]

偏大。

也可能：

> Batch 很小导致梯度噪声大。

或者：

> 数据分布非常不稳定。

---

## 129. 情况 E：训练很慢但稳定

可能：

> LR 太保守。

但也可能：

- 模型容量不足；
- 数据难；
- 表示差；
- Gradient Flow 弱。

还是那句话：

\[
\boxed{
先诊断，再调参
}
\]

---

## 130. 只看 Gradient Norm 够吗？

不完全够。

还可以思考：

\[
\frac{\|\Delta\theta\|}
{\|\theta\|}
\]

也就是：

# Update-to-Weight Ratio

参数每一步相对自身尺度：

> 改了多少。

---

## 131. 为什么这个量有意义？

假设：

\[
\|\theta\|=1000
\]

更新：

\[
\|\Delta\theta\|=0.001
\]

变化极小。

如果：

\[
\|\Delta\theta\|=500
\]

那一步更新：

> 极其激进。

---

## 132. 这比单独看 LR 更接近真实情况

因为 Adam 下：

> 实际 Update 不等于 LR × Raw Gradient。

所以真正要理解优化行为：

\[
\boxed{
看实际ParameterUpdate
}
\]

比只看配置里的：

\[
learning\_rate
\]

更深一层。

---

## 133. 一个常见误解

LR：

\[
10^{-4}
\]

不是说：

> “每一步学习 0.01%。”

它是：

> 数值优化步长尺度。

真正参数变化还取决于：

- Gradient；
- Adam moments；
- Weight decay；
- clipping；
- scheduler。

---

## 134. 所以不同 Optimizer 的 LR 不能直接比较

SGD：

\[
LR=0.1
\]

AdamW：

\[
LR=10^{-4}
\]

并不意味着：

> SGD 比 Adam 学快 1000 倍。

它们的更新公式：

> 完全不同。

---

## 135. 假设 ProcurementML 有三个输入方向

\[
X=
[
x_1,x_2,x_3
]
\]

分别代表：

```text
x1 = 限制竞争迹象
x2 = 履约关联性
x3 = 必要性证据
```

当前模型：

\[
z=w_1x_1+w_2x_2+w_3x_3+b
\]

---

## 136. 当前样本

某采购条件：

> 要求供应商在项目所在地设固定服务机构。

当前抽象特征：

\[
X=
[0.9,0.4,0.2]
\]

专家标签：

\[
y=1
\]

这里仅作为机器学习演示，不是在脱离完整事实情况下作实际法律结论。

---

## 137. 模型当前预测

\[
p=0.35
\]

所以：

\[
\delta=p-y
\]

\[
=-0.65
\]

---

## 138. 三个 Weight 的 Gradient

\[
g_1
=
-0.65(0.9)
=
-0.585
\]

\[
g_2
=
-0.65(0.4)
=
-0.26
\]

\[
g_3
=
-0.65(0.2)
=
-0.13
\]

---

## 139. 如果普通 SGD

假设：

\[
\eta=0.01
\]

则：

\[
\Delta w_1=+0.00585
\]

\[
\Delta w_2=+0.0026
\]

\[
\Delta w_3=+0.0013
\]

这个样本推动模型：

> 提高这些活跃输入方向对风险 Logit 的贡献。

---

## 140. 但是只有一个样本不能代表真实规律

如果连续很多样本都支持：

> 某个方向，

Optimizer 会逐渐积累。

如果另一些样本反对：

> Gradient 会抵消。

最终 Weight：

> 是海量训练信号长期竞争的结果。

---

## 141. 这也是为什么参数不能解释成一条固定规则

最终：

\[
w
\]

不是简单：

> “地域条件 = 风险”。

而是大量样本、多层 Representation、多参数共同作用形成的：

> 统计计算结构。

这和第一课第 12 阶段再次呼应。

---

## 142. 预训练模型不是随机初始化

它已经拥有：

\[
\theta_{pretrained}
\]

里面包含大量：

> 语言和知识 Representation。

Fine-tuning 的目标不是：

> 从零重建。

而是：

\[
\boxed{
在已有良好参数附近，
找到更适合新任务的位置
}
\]

---

## 143. 所以 Fine-tuning 像“微调”

不是：

> 推倒重建。

如果 LR 太大：

\[
\theta
\]

可能快速远离：

\[
\theta_{pretrained}
\]

这可能破坏：

> 原有能力。

---

## 144. 对 ProcurementLM 的意义

我们希望模型增加：

- 采购文档理解；
- 风险审查行为；
- 法规引用方式；
- 专家输出结构。

但不希望：

> 把基础中文能力和通用推理能力毁掉。

因此：

\[
LearningRate
\]

是“学习新能力”和“保持旧能力”之间的重要旋钮。

---

## 145. 底层优化过程基本一样

都可能是：

\[
Forward
\rightarrow
Loss
\rightarrow
Backward
\rightarrow
AdamW
\]

区别主要在：

- 数据；
- Loss 目标；
- 训练规模；
- Learning Rate；
- Schedule；
- Trainable Parameters。

---

## 146. CPT

目标通常接近：

# Language Modeling

模型继续学习：

> 政府采购领域语言分布。

因此训练量：

> 可能较大。

---

## 147. SFT

目标是：

> 对指令和答案进行监督学习。

更强调：

- 回答格式；
- 工作流程；
- 推理行为；
- 专业表达。

训练配方：

> 往往与 CPT 不完全相同。

---

## 148. LoRA SFT

则：

\[
BaseModel
\]

大部分冻结。

Optimizer：

> 只管理 Adapter 参数。

这就是为什么以后查看代码一定要问：

\[
\boxed{
Optimizer到底拿到了哪些parameters？
}
\]

---

## 149. 最简单

```python
optimizer = torch.optim.SGD(
    model.parameters(),
    lr=0.01
)
```

表示：

> SGD 管理 `model.parameters()`。

---

## 150. AdamW

典型：

```python
optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=2e-4,
    weight_decay=0.01
)
```

这三个参数现在已经不陌生：

```text
parameters
learning rate
weight decay
```

---

## 151. 训练循环

```python
for batch in dataloader:

    optimizer.zero_grad()

    logits = model(batch["x"])
    loss = criterion(logits, batch["y"])

    loss.backward()

    optimizer.step()
```

到今天：

> 你应该能解释每一行的物理意义。

---

## 152. `optimizer.zero_grad()`

清除：

\[
上一Step
\]

留下的 `.grad`。

---

## 153. `model(...)`

执行：

\[
Forward
\]

产生：

\[
Activations
\]

和：

\[
Logits
\]

同时训练模式下：

> 构造 Autograd Graph。

---

## 154. `loss = ...`

把模型输出：

> 转换成训练目标误差。

---

## 155. `loss.backward()`

沿计算图反向计算：

\[
\nabla_\theta L
\]

写进：

```python
parameter.grad
```

---

## 156. `optimizer.step()`

Optimizer 读取：

\[
parameter.grad
\]

以及自己的历史状态：

\[
m,v,\ldots
\]

计算：

\[
\Delta\theta
\]

真正修改：

\[
parameter
\]

---

## 157. 如果还有 Scheduler

通常还会：

```python
scheduler.step()
```

更新：

\[
LearningRate
\]

进入下一 Step。

---

## 158. 现实版本可能像

```text
Load Batch
↓
Forward
↓
Loss
↓
Backward
↓
Gradient Clipping
↓
Optimizer Step
↓
Scheduler Step
↓
Zero Grad
↓
Logging
```

Mixed precision、distributed training：

> 还会增加其它环节。

---

## 159. 对 Transformer 类模型

AdamW 通常是：

> 一个成熟、稳定、常见的起点。

但这并不意味着：

> 所有模型永远必须 AdamW。

还有：

- SGD；
- Adafactor；
- Lion；
- Sophia；
- 以及各种新优化器。

---

## 160. 学优化器最危险的方式

就是：

> 追每一个新 Optimizer 的名字。

而不知道它到底改变了什么。

更好的统一框架是问：

\[
\boxed{
它如何利用Gradient？
}
\]

\[
\boxed{
它是否使用历史？
}
\]

\[
\boxed{
它怎样缩放不同参数？
}
\]

\[
\boxed{
它需要多少OptimizerState？
}
\]

---

## 161. SGD

只看：

\[
g_t
\]

核心：

> 当前 Gradient。

---

## 162. Momentum

看：

\[
g_t
\]

加历史：

\[
m_{t-1}
\]

核心：

> 平滑方向。

---

## 163. Adam

看：

\[
g_t
\]

加：

\[
m_t
\]

和：

\[
v_t
\]

核心：

> 平滑方向 + 自适应尺度。

---

## 164. AdamW

在 Adam 基础上：

> 把 Weight Decay 解耦。

所以可以形成一条演化线：

\[
\boxed{
SGD
\rightarrow
Momentum
\rightarrow
AdaptiveScaling
\rightarrow
Adam
\rightarrow
AdamW
}
\]

---

## 165. 如果标签错误

换：

\[
SGD
\]

到：

\[
AdamW
\]

不会让模型：

> 自动懂正确答案。

反而可能：

> 更高效地拟合错误标签。

---

## 166. 如果 Test Leakage

换 Optimizer：

> 也解决不了。

如果数据缺少：

> Hard Negative，

AdamW：

> 也不会自动创造正确决策边界。

---

## 167. 所以第一课依然高于第二课

第二课告诉你：

> 模型内部怎么学。

第一课告诉你：

> 学什么才有意义。

二者关系：

\[
\boxed{
Optimization
不能修复错误的ProblemDefinition
}
\]

---

## 168. 如果最新法规根本不在模型上下文和训练知识里

不是：

> AdamW 参数没调好。

可能应该：

> RAG 更新知识。

所以仍要区分：

\[
ModelTraining
\]

和：

\[
KnowledgeRetrieval
\]

---

## 169. 一个很实用的诊断顺序

训练异常时先问：

\[
\boxed{
Pipeline对吗？
}
\]

再问：

\[
\boxed{
Gradient对吗？
}
\]

再问：

\[
\boxed{
LR/Optimizer对吗？
}
\]

不要一看到 Loss 异常：

> 第一反应就是换 Optimizer。

---

## 170. Sanity Check

正式大训练前：

> 用很小的数据集，尝试让模型过拟合。

例如：

\[
100
\]

条样本。

如果连 100 条都学不下来：

> 优先怀疑训练 Pipeline。

而不是：

> 模型泛化能力。

---

## 171. 为什么 Small-set Overfit Test 很有价值？

因为它测试：

- Forward 是否正常；
- Loss 是否正常；
- Backward 是否正常；
- Optimizer 是否更新；
- 数据标签是否接通。

这是训练系统非常有效的：

# Unit Test

---

## 172. 可以逐渐增大 LR

从非常小：

\[
10^{-7}
\]

逐渐升高。

观察：

> Loss 在什么时候开始明显下降。

什么时候：

> 开始爆炸。

这类方法叫：

# LR Range Test

---

## 173. 它不是绝对答案

但可以帮助判断：

> 合理 LR 大概在哪个数量级。

真正最佳值：

> 仍需要 Validation Experiment。

---

## 174. Optimizer 是实验的一部分

实验记录不能只写：

> “训练了一个模型。”

应该保存：

```yaml
optimizer: AdamW
learning_rate: ...
betas: ...
epsilon: ...
weight_decay: ...
warmup_steps: ...
scheduler: ...
gradient_clip: ...
effective_batch_size: ...
```

---

## 175. 为什么？

因为同一数据、同一模型：

> 换 LR 就可能得到完全不同结果。

所以：

\[
\boxed{
OptimizerConfig
=
ExperimentIdentity
}
\]

---

## 176. 假设 Experiment 006

问题：

> 对采购资格风险分类，LoRA SFT 的最佳初始 LR 区间是什么？

固定：

- Dataset；
- Seed；
- Base Model；
- LoRA Rank；
- Batch；
- Epoch；
- Eval Set。

只改变：

\[
LR
\]

---

## 177. 例如三个实验

```text
EXP-006A: 5e-5

EXP-006B: 1e-4

EXP-006C: 2e-4
```

比较：

- Train Loss；
- Val Loss；
- Recall；
- Precision；
- High-risk Recall；
- Calibration；
- Regression。

---

## 178. 为什么一次只改变一个主要变量？

否则：

```text
LR 改了
Batch 改了
LoRA Rank 改了
数据也改了
```

结果变好。

你不知道：

> 到底是什么原因。

仍然回到第一课：

\[
\boxed{
ControlledExperiment
}
\]

---

## 179. 训练 Loss 最低不一定 Test 最好

Optimizer 的任务是：

> 降低训练目标。

但最终我们关心：

\[
Generalization
\]

所以不能只选：

> Train Loss 最低的配置。

---

## 180. 有些 Optimizer 走到的解不同

即使两个 Optimizer：

> Train Loss 差不多。

它们最终参数位置：

\[
\theta_A,\theta_B
\]

可能不同。

所以 Validation：

> 仍然必须独立判断。

---

## 181. 一个直觉概念

某个低 Loss 点附近：

> 稍微动一点 Loss 就暴涨。

叫：

> 比较 sharp。

另一个区域：

> 参数小幅变化，Loss 仍然低。

叫：

> 比较 flat。

---

## 182. 为什么有人关注 Flatness？

一个直觉是：

> 较宽的低 Loss 区域可能对参数扰动和分布变化更稳。

但现实理论很复杂。

不要机械地：

> “flat 一定泛化好”。

---

## 183. Weight Decay 是不是万能防过拟合？

不是。

它只是：

> 正则化手段之一。

如果训练集存在严重 Leakage：

> Weight Decay 解决不了。

---

## 184. 数据正则化往往更重要

例如：

- Project-level split；
- Hard negatives；
- Temporal holdout；
- 多地区样本。

这些可能比单纯把：

\[
weight\_decay
\]

从 0.01 调到 0.02 更重要。

---

## 185. 因为 Optimizer 不是孤立模块

最终训练稳定性由：

\[
\boxed{
Data
+
Initialization
+
Architecture
+
Loss
+
GradientFlow
+
Optimizer
+
LR
+
Batch
+
Precision
}
\]

共同决定。

---

## 186. 一个配置参数变化会连锁影响其它参数

例如：

\[
BatchSize\uparrow
\]

可能影响：

- Gradient Noise；
- LR；
- Memory；
- Step 数；
- Scheduler；
- Throughput。

所以训练不是：

> 单旋钮系统。

---

## 187. 假设 7B 模型

每个 Step：

> Backward 为数十亿参数计算 Gradient。

AdamW：

> 为可训练参数维护状态。

Distributed Training：

> 多 GPU 还要同步 Gradient。

所以：

\[
optimizer.step()
\]

虽然代码只有一行，

背后是：

> 非常大的分布式数值系统。

---

## 188. Data Parallel 时发生什么？

不同 GPU：

> 各自处理不同 Batch。

得到本地梯度：

\[
g_1,g_2,\ldots,g_n
\]

然后：

> 同步/聚合。

例如：

\[
g
=
\frac1n
\sum_i g_i
\]

---

## 189. 然后各 GPU 使用同一个 Gradient

执行：

\[
OptimizerStep
\]

从而确保：

> 参数继续保持一致。

这就是 Data Parallel 的一个核心。

---

## 190. 所以 GPU 多了不是每张卡训练一个不同模型

Data Parallel：

> 多卡共同训练一份逻辑模型。

只是：

> 分担数据和计算。

---

## 191. 因为 Optimizer State 很大

Adam：

\[
m,v
\]

对大模型非常占显存。

传统 Data Parallel：

> 每张卡都复制一份。

非常浪费。

---

## 192. ZeRO 的一个核心思想

把：

- Optimizer State；
- Gradient；
- Parameters；

不同程度：

> 分片到多张 GPU。

因此减少：

> 单卡显存压力。

以后分布式训练会详细讲。

---

# 第二课 · 第 6 阶段核心结构

现在整个过程已经变成：

\[
\boxed{
Forward
\rightarrow
Loss
\rightarrow
Backward
\rightarrow
Gradient
\rightarrow
Optimizer
\rightarrow
ParameterUpdate
}
\]

Optimizer 内部又可以理解为：

\[
\boxed{
CurrentGradient
+
GradientHistory
+
GradientScale
+
LearningRate
+
Regularization
}
\]

共同决定：

\[
\Delta\theta
\]

## 本阶段五个最重要的专家心智模型

| 心智模型 | 核心认知 |
|---|---|
| **① Gradient、Optimizer、Learning Rate 是三件不同的事** | Gradient 提供局部信息，Optimizer 定更新规则，LR 控制基本步长 |
| **② 真正的训练时间尺度是 Optimizer Step** | Micro-batch、Backward 次数和参数更新次数必须区分 |
| **③ Momentum 是历史方向记忆** | 主要作用是积累一致方向、抑制高频抖动 |
| **④ Adam 是方向统计 + 梯度尺度自适应** | 每个参数拥有动态有效步长，而不是简单统一乘 LR |
| **⑤ AdamW 把任务梯度和 Weight Decay 分开** | 优化数据目标与正则化参数规模是不同机制 |

## 如果只记三个公式

第一个：

\[
\boxed{
\theta_{t+1}
=
\theta_t-\eta g_t
}
\]

这是最基础 SGD。

第二个：

\[
\boxed{
m_t
=
\beta_1m_{t-1}
+
(1-\beta_1)g_t
}
\]

这是方向历史。

第三个：

\[
\boxed{
v_t
=
\beta_2v_{t-1}
+
(1-\beta_2)g_t^2
}
\]

这是梯度尺度历史。

Adam：

> 就把它们组合起来。

## 如果只记一句话

\[
\boxed{
Backprop告诉模型“哪里该改”，
Optimizer决定“怎么改、改多少、是否参考过去”。
}
\]

## 现在第二课已经形成真正的学习机器

第 1 阶段：

\[
z=WX+b
\]

建立神经元。

第 2 阶段：

\[
h=f(z)
\]

加入非线性。

第 3 阶段：

\[
H_1,H_2,\ldots
\]

形成 Representation。

第 4 阶段：

\[
Forward
\]

计算答案。

第 5 阶段：

\[
Backward
\]

计算责任。

第 6 阶段：

\[
Optimizer
\]

真正修改参数。

所以：

\[
\boxed{
NeuralNetworkLearning
=
Forward
+
Loss
+
Backward
+
Optimizer
}
\]

到这里，**一个神经网络“如何学习”最核心的闭环已经完整了。**

## 第 6 阶段掌握标准

学完以后，你应该能自然回答：

> `loss.backward()` 和 `optimizer.step()` 有什么区别？

> Gradient 和 Learning Rate 各自负责什么？

> 为什么 LR 太大会爆炸，太小会学不动？

> Mini-batch 为什么会带来 Gradient Noise？

> Momentum 为什么可以减少来回震荡？

> Adam 的 \(m_t\) 和 \(v_t\) 分别表示什么？

> 为什么 Adam 能让不同参数拥有不同有效步长？

> Adam 与 AdamW 的 Weight Decay 有什么关键区别？

> 为什么要 Warmup？

> 为什么训练后期经常 Decay LR？

> 为什么 Gradient Accumulation 后 Optimizer Step 数和 Batch 数不同？

> 为什么 Adam 训练的显存远大于只有模型权重的推理显存？

> 为什么 LoRA 不仅省 Gradient，还省 Optimizer State？

> 为什么 Resume Training 需要保存 Optimizer State？

> 为什么不能靠换 Optimizer 修复 Bad Label、Leakage 和缺知识？

如果这些问题已经能够讲清楚，第 6 阶段就真正建立起来了。

下一阶段进入 **第二课 · 第 7 阶段：Initialization、Normalization 与 Residual Connection——为什么一个 2 层网络很好训练，而几十层、上百层网络却必须靠一整套“信号稳定系统”才能真正训起来。**

这一阶段会把我们已经零散见过的：

\[
\boxed{
Xavier/He
+
LayerNorm/RMSNorm
+
Residual
+
GradientFlow
}
\]

放进同一个统一框架。

---
