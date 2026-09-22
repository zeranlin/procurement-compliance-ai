# 第二课 · 第 5 阶段：Backpropagation——最终 Loss 到底怎样穿过计算图，把“错误责任”一层层分配给每一个 Weight？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Backpropagation = Loss 通过 Chain Rule 沿计算图反向传播，把错误信号分配给可训练参数。**
2. **Gradient ≠ Parameter Update。backward() 计算梯度，optimizer.step() 才真正改变参数。**
3. **Credit Assignment 的核心是回答“最终错误应该由前面哪些参数承担多少责任”。**
4. **深层网络中的梯度是局部导数连续相乘的结果，因此会遇到梯度过小、过大和数值不稳定问题。**
5. **只有 requires_grad / 可训练参数会被优化；被冻结参数即使参与 Forward，也不应该被更新。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Loss` | 损失函数：把预测错误压缩成可优化的数值信号 |
| `Backpropagation` | 反向传播：把最终损失沿计算图反向分配到参数 |
| `Gradient` | 梯度：损失对参数变化方向和敏感度的局部信息 |
| `Optimizer` | 优化器：依据梯度规则更新参数 |
| `Batch` | 批次：一次参与计算的一组样本 |
| `State` | 状态：保存任务进度、事实和待办 |
| `Step` | 训练步：通常指一次优化器更新 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Learning Rate` | 学习率：控制每次参数更新步幅 |
| `Embedding` | 嵌入：把离散 Token 映射到连续高维向量 |
| `PyTorch` | PyTorch：张量计算、自动求导和训练/推理框架 |
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

前四阶段，我们已经把 Forward 完整走通：

\[
\boxed{
X
\rightarrow
Linear
\rightarrow
Activation
\rightarrow
HiddenState
\rightarrow
Logit
\rightarrow
Prediction
\rightarrow
Loss
}
\]

现在模型知道：

> “我错了多少。”

但还不知道：

> **到底是谁导致了这个错误？**

这就是 Backpropagation 要解决的问题。

它的核心不是一句：

> “把梯度传回去。”

而是：

\[
\boxed{
Loss
\rightarrow
找到每一个中间变量的责任
\rightarrow
找到每一个参数的责任
\rightarrow
Optimizer更新参数
}
\]

这就是：

# Credit Assignment

责任分配。

---

## 1. 先把 Backprop 放回整个训练闭环

完整训练过程：

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
OptimizerStep
}
\]

其中：

Forward：

\[
X\rightarrow \hat Y
\]

Loss：

\[
\hat Y,Y\rightarrow L
\]

Backward：

\[
L\rightarrow \nabla_\theta L
\]

Optimizer：

\[
\theta\rightarrow\theta'
\]

所以：

\[
\boxed{
Backward
本身不修改参数
}
\]

它只计算：

\[
Gradient
\]

真正修改参数的是：

\[
Optimizer
\]

---

## 2. 这是一个特别容易混淆的地方

很多初学者会说：

> “Backprop 更新模型。”

严格来说不够准确。

更准确是：

\[
\boxed{
Backpropagation
=
计算梯度
}
\]

\[
\boxed{
Optimizer
=
利用梯度更新参数
}
\]

以后看到：

```python
loss.backward()
optimizer.step()
```

就应该知道：

> 这是两个不同动作。

---

## 3. 为什么模型需要梯度？

假设只有一个参数：

\[
w
\]

Loss：

\[
L(w)
\]

现在模型在：

\[
w=2
\]

我们想知道：

> \(w\) 应该增加还是减少？

需要：

\[
\frac{dL}{dw}
\]

如果：

\[
\frac{dL}{dw}>0
\]

说明：

> \(w\) 增大时 Loss 倾向增加。

所以为了降低 Loss：

\[
w
\]

应该减小。

---

## 4. 如果梯度是负数呢？

如果：

\[
\frac{dL}{dw}<0
\]

说明：

> 增大 \(w\) 会降低 Loss。

所以参数应该：

> 增加。

这就是 Gradient Descent：

\[
\boxed{
w_{new}
=
w_{old}
-
\eta
\frac{dL}{dw}
}
\]

---

## 5. 第一个核心心智模型

### 心智模型 ①：Gradient 是“如果轻微改变这个参数，Loss 会怎样变化？”

不是：

> “这个参数好不好。”

而是：

\[
\boxed{
Sensitivity
}
\]

敏感度。

\[
\frac{\partial L}{\partial w}
\]

回答：

> 当 \(w\) 轻微增加一点，最终 Loss 大约会怎样变化？

---

## 6. 从最小模型开始

我们先不要碰矩阵。

只看：

\[
z=wx+b
\]

假设：

\[
x=2
\]

\[
w=3
\]

\[
b=1
\]

那么：

\[
z=3\times2+1
\]

所以：

\[
\boxed{
z=7
}
\]

---

## 7. 如果目标就是让 \(z\) 接近 5

为了方便手算，先用平方误差：

\[
L=\frac12(z-y)^2
\]

其中：

\[
y=5
\]

于是：

\[
L
=
\frac12(7-5)^2
\]

\[
=
\frac12\times4
\]

\[
\boxed{
L=2
}
\]

---

## 8. 现在问题来了

Loss：

\[
2
\]

我们知道模型错了。

但要训练：

> 必须知道 \(w\) 应该怎么变。

即：

\[
\frac{\partial L}{\partial w}
\]

---

## 9. 不要直接跳公式，先拆计算图

模型：

\[
z=wx+b
\]

Loss：

\[
L=\frac12(z-y)^2
\]

计算链：

```text
w
 \
  × x
   ↓
   + b
   ↓
   z
   ↓
  z-y
   ↓
 square
   ↓
   × 1/2
   ↓
   L
```

---

## 10. Backprop 的核心策略

我们不一次性问：

\[
w
\rightarrow L
\]

而是拆成：

\[
w
\rightarrow z
\rightarrow L
\]

于是：

\[
\boxed{
\frac{\partial L}{\partial w}
=
\frac{\partial L}{\partial z}
\frac{\partial z}{\partial w}
}
\]

这就是：

# Chain Rule

链式法则。

---

## 11. Chain Rule 是 Backprop 的数学核心

如果：

\[
y=f(g(x))
\]

那么：

\[
\boxed{
\frac{dy}{dx}
=
\frac{dy}{dg}
\frac{dg}{dx}
}
\]

一句人话：

> x 先影响 g，g 再影响 y。

那么：

> x 对 y 的影响 = 每一段影响乘起来。

---

## 12. 用“责任传递”理解 Chain Rule

比如：

```text
参数 w
↓
影响 z
↓
影响 Loss
```

如果：

\[
w
\]

对：

\[
z
\]

影响很大，

但：

\[
z
\]

对 Loss 几乎没有影响，

那么最终：

\[
w
\]

责任仍然很小。

所以：

\[
\boxed{
总责任
=
上游责任
\times
本地影响
}
\]

---

## 13. 什么叫 Local Gradient？

例如：

\[
z=wx+b
\]

对于：

\[
w
\]

本地导数：

\[
\boxed{
\frac{\partial z}{\partial w}=x
}
\]

这只描述：

> 这个局部运算里，w 对 z 的影响。

---

## 14. Loss 对 z 的导数呢？

\[
L=\frac12(z-y)^2
\]

所以：

\[
\boxed{
\frac{\partial L}{\partial z}
=
z-y
}
\]

现在：

\[
z=7
\]

\[
y=5
\]

所以：

\[
\frac{\partial L}{\partial z}=2
\]

---

## 15. 于是 w 的梯度

Chain Rule：

\[
\frac{\partial L}{\partial w}
=
\frac{\partial L}{\partial z}
\frac{\partial z}{\partial w}
\]

已知：

\[
\frac{\partial L}{\partial z}=2
\]

而：

\[
\frac{\partial z}{\partial w}=x=2
\]

所以：

\[
\boxed{
\frac{\partial L}{\partial w}
=
2\times2
=
4
}
\]

---

## 16. 这个 4 怎么解释？

意思不是：

> w 错了 4。

而是：

> 在当前点附近，w 每增加约 1 个单位，Loss 的变化趋势约为 +4。

因此为了降低 Loss：

\[
w
\]

应该：

> 向小的方向走。

---

## 17. 假设 Learning Rate 是 0.1

更新：

\[
w_{new}
=
3
-
0.1\times4
\]

得到：

\[
\boxed{
w_{new}=2.6
}
\]

---

## 18. 再 Forward 一次看看

新：

\[
w=2.6
\]

那么：

\[
z=2.6\times2+1
\]

\[
=6.2
\]

新 Loss：

\[
L
=
\frac12(6.2-5)^2
\]

\[
=
0.72
\]

原来：

\[
2
\]

现在：

\[
0.72
\]

真的下降了。

---

## 19. 这就是学习最小闭环

\[
\boxed{
Forward
\rightarrow
Loss
\rightarrow
Gradient
\rightarrow
Update
\rightarrow
LowerLoss
}
\]

这套逻辑：

> 从一个参数，

一直扩展到几十亿参数。

---

## 20. 第二个核心心智模型

### 心智模型 ②：Backprop 不是“智能算法”，而是高效执行 Chain Rule

Backpropagation 真正厉害的地方不是：

> 发明了一个神秘学习规则。

而是：

\[
\boxed{
高效复用计算图里的中间结果，
把ChainRule应用到大量参数
}
\]

---

## 21. Bias 怎么算梯度？

还是：

\[
z=wx+b
\]

显然：

\[
\frac{\partial z}{\partial b}=1
\]

所以：

\[
\frac{\partial L}{\partial b}
=
\frac{\partial L}{\partial z}
\times1
\]

也就是：

\[
\boxed{
\frac{\partial L}{\partial b}=z-y
}
\]

---

## 22. 在刚才例子里

\[
z-y=2
\]

所以：

\[
\boxed{
\frac{\partial L}{\partial b}=2
}
\]

如果 LR：

\[
0.1
\]

则：

\[
b_{new}
=
1-0.1(2)
\]

得到：

\[
0.8
\]

---

## 23. 输入 x 有没有梯度？

当然可以有：

\[
\frac{\partial z}{\partial x}=w
\]

所以：

\[
\boxed{
\frac{\partial L}{\partial x}
=
\frac{\partial L}{\partial z}w
}
\]

这里：

\[
2\times3=6
\]

---

## 24. 但我们通常会更新 x 吗？

如果：

\[
x
\]

只是训练数据：

> 不会。

我们只关心：

\[
W,b
\]

这些：

# Trainable Parameters

可训练参数。

---

## 25. 但有时输入本身也是可训练的

例如：

# Embedding

Token 对应的 Embedding Vector：

> 本质也是参数。

因此梯度会传到：

\[
EmbeddingMatrix
\]

并更新它。

所以以后不要把：

> “输入向量”

永远理解成不可训练。

---

## 26. 现在进入 Sigmoid

政府采购风险二分类：

\[
z=wx+b
\]

然后：

\[
p=\sigma(z)
\]

Loss：

\[
L
\]

计算图：

```text
w,x,b
↓
z
↓
Sigmoid
↓
p
↓
Loss
```

---

## 27. Backward 就多了一段

现在：

\[
\frac{\partial L}{\partial w}
=
\frac{\partial L}{\partial p}
\frac{\partial p}{\partial z}
\frac{\partial z}{\partial w}
\]

这就是多个 Local Gradient 连乘。

---

## 28. Sigmoid 的局部梯度

我们第 2 阶段学过：

\[
\boxed{
\frac{d\sigma(z)}{dz}
=
\sigma(z)(1-\sigma(z))
}
\]

也就是：

\[
\frac{\partial p}{\partial z}
=
p(1-p)
\]

---

## 29. 为什么 Forward 的中间值很有用？

因为 Forward 已经算出了：

\[
p
\]

所以 Backward 时不必重新从头算指数函数。

可以直接：

\[
p(1-p)
\]

这就是 Backprop 高效的一个原因：

> **复用 Forward 的中间结果。**

---

## 30. 现在重新看 Cross Entropy

二分类：

\[
L
=
-[y\log p+(1-y)\log(1-p)]
\]

你可能觉得：

> 导数一定会很复杂。

但 Sigmoid + BCE 会出现一个极其漂亮的结果。

---

## 31. 最终结果

对于：

\[
p=\sigma(z)
\]

加 BCE：

\[
\boxed{
\frac{\partial L}{\partial z}
=
p-y
}
\]

第一课已经见过这个结果。

现在我们终于知道：

> 它其实是 Chain Rule 一层层推出来的。

---

## 32. 为什么这个公式这么重要？

因为：

\[
p-y
\]

可以直接理解成：

# Prediction Error Signal

预测误差信号。

如果：

\[
y=1
\]

而：

\[
p=0.2
\]

则：

\[
p-y=-0.8
\]

是一个很强的负梯度信号。

---

## 33. 如果 y=1，p=0.95 呢？

\[
p-y=-0.05
\]

梯度：

> 很小。

说明：

> 已经预测得不错，不需要大改。

这非常符合直觉。

---

## 34. 如果 y=0，p=0.9 呢？

\[
p-y=0.9
\]

梯度很大而且为正。

意味着：

> Logit 应该往下压。

因为模型把无风险样本：

> 高置信度判成风险。

---

## 35. 这就是错误如何变成训练信号

\[
\boxed{
标签
+
预测
\rightarrow
误差信号
\rightarrow
梯度
}
\]

模型并不会听懂：

> “你这里错了。”

它收到的是：

\[
\boxed{
数值梯度
}
\]

---

## 36. 一个政府采购二分类例子

真实：

\[
y=1
\]

表示：

> 专家标记为风险。

模型：

\[
p=0.30
\]

那么：

\[
\frac{\partial L}{\partial z}
=
0.30-1
\]

得到：

\[
\boxed{
-0.70
}
\]

---

## 37. 再传播到 Weight

假设：

\[
z=w_1x_1+w_2x_2+b
\]

那么：

\[
\frac{\partial z}{\partial w_1}
=
x_1
\]

所以：

\[
\boxed{
\frac{\partial L}{\partial w_1}
=
(p-y)x_1
}
\]

这正是第一课第四阶段学过的公式。

---

## 38. 如果 x1=0.8

那么：

\[
\frac{\partial L}{\partial w_1}
=
-0.7\times0.8
\]

得到：

\[
\boxed{
-0.56
}
\]

Gradient Descent：

\[
w_1
\leftarrow
w_1-\eta(-0.56)
\]

所以：

\[
w_1
\]

会上升。

---

## 39. 为什么会上升？

因为当前样本真实是：

> 风险。

而：

\[
x_1
\]

当前是比较强的输入信号。

模型却预测偏低。

于是训练推动：

> 与这个输入相关的风险方向权重变强。

---

## 40. 第三个核心心智模型

### 心智模型 ③：Backprop 是“误差信号 × 本地敏感度”的连续传播

每一个节点都做：

\[
\boxed{
UpstreamGradient
\times
LocalGradient
}
\]

然后得到：

\[
DownstreamGradient
\]

这就是理解 Backprop 最稳定的方法。

---

## 41. 什么叫 Upstream Gradient？

假设：

\[
a\rightarrow b\rightarrow L
\]

当我们已经知道：

\[
\frac{\partial L}{\partial b}
\]

这个就是：

> 从 Loss 方向传过来的梯度。

可以叫：

# Upstream Gradient

---

## 42. Local Gradient 呢？

如果：

\[
b=f(a)
\]

则：

\[
\frac{\partial b}{\partial a}
\]

就是：

> 当前这个小运算自己的导数。

---

## 43. 然后乘起来

\[
\boxed{
\frac{\partial L}{\partial a}
=
\frac{\partial L}{\partial b}
\frac{\partial b}{\partial a}
}
\]

也就是：

```text
上游梯度
×
本地梯度
=
继续向前传播的梯度
```

---

## 44. 这其实就是“反向传递消息”

Forward：

```text
Value →
```

Backward：

```text
← Gradient
```

所以同一张计算图上：

\[
\boxed{
Forward\ flows\ values
}
\]

\[
\boxed{
Backward\ flows\ sensitivities
}
\]

---

## 45. 加法节点的 Backward 很简单

如果：

\[
z=a+b
\]

那么：

\[
\frac{\partial z}{\partial a}=1
\]

\[
\frac{\partial z}{\partial b}=1
\]

所以 Backward：

> 上游梯度原样分别传给 a 和 b。

---

## 46. 乘法节点呢？

如果：

\[
z=ab
\]

那么：

\[
\frac{\partial z}{\partial a}=b
\]

\[
\frac{\partial z}{\partial b}=a
\]

所以：

> 对 a 的梯度要乘 b，对 b 的梯度要乘 a。

---

## 47. ReLU 节点呢？

\[
h=ReLU(z)
\]

如果：

\[
z>0
\]

局部梯度：

\[
1
\]

如果：

\[
z<0
\]

局部梯度：

\[
0
\]

因此：

\[
\boxed{
\frac{\partial L}{\partial z}
=
\frac{\partial L}{\partial h}
\cdot
\mathbf 1(z>0)
}
\]

---

## 48. 这就是 ReLU Mask

Forward：

```text
[-2, 0.4, 1.8, -0.3]
```

经过 ReLU：

```text
[0, 0.4, 1.8, 0]
```

Backward：

> 负值位置的梯度被截断成 0。

---

## 49. 政府采购表示的直觉

假设一个 Hidden Unit 当前输入下：

> 完全没有“地域限制”相关激活。

ReLU 关闭：

\[
0
\]

那么这条路径在当前样本：

> 对前面的参数可能没有梯度贡献。

注意：

> 这是帮助理解的简化类比，不代表真实神经元一定对应某个人类概念。

---

## 50. 进入真正的 Hidden Layer Backprop

两层网络：

\[
z_1=W_1X+b_1
\]

\[
h_1=ReLU(z_1)
\]

\[
z_2=W_2h_1+b_2
\]

\[
L=L(z_2,y)
\]

---

## 51. Backward 顺序必须反过来

Forward：

\[
X
\rightarrow z_1
\rightarrow h_1
\rightarrow z_2
\rightarrow L
\]

Backward：

\[
\boxed{
L
\rightarrow z_2
\rightarrow h_1
\rightarrow z_1
\rightarrow W_1
}
\]

---

## 52. 为什么必须从后往前？

因为要算：

\[
\frac{\partial L}{\partial W_1}
\]

必须先知道：

\[
\frac{\partial L}{\partial z_1}
\]

而它又依赖：

\[
\frac{\partial L}{\partial h_1}
\]

而这个又来自：

\[
z_2
\]

所以自然只能：

> 从 Loss 往回走。

---

## 53. 这不是“时间倒流”

Backward 不会：

> 把 Forward 撤销。

它只是沿同样依赖关系：

> 反方向计算导数。

---

## 54. 先算输出层

二分类情况下：

\[
\delta_2
=
\frac{\partial L}{\partial z_2}
\]

如果使用 Sigmoid+BCE：

\[
\boxed{
\delta_2=p-y
}
\]

这里常用：

\[
\delta
\]

表示某层误差信号。

---

## 55. 输出层 Weight 梯度

\[
z_2=W_2h_1+b_2
\]

所以：

\[
\boxed{
\frac{\partial L}{\partial W_2}
=
\delta_2h_1^T
}
\]

如果暂时不熟悉矩阵：

> 可以把它理解成每个 Hidden Activation 与输出误差信号相乘。

---

## 56. 输出层 Bias 梯度

因为：

\[
\frac{\partial z_2}{\partial b_2}=1
\]

所以：

\[
\boxed{
\frac{\partial L}{\partial b_2}
=
\delta_2
}
\]

Batch 情况下：

> 通常还会对多个样本求和或平均。

---

## 57. 怎么把梯度继续传给 Hidden Layer？

输出：

\[
z_2=W_2h_1+b_2
\]

所以：

\[
\boxed{
\frac{\partial L}{\partial h_1}
=
W_2^T\delta_2
}
\]

这一步非常关键。

---

## 58. 为什么会乘 \(W_2^T\)？

因为：

> Hidden Unit 对输出影响有多大，由 \(W_2\) 决定。

如果某个 Hidden Dimension 到输出的权重：

\[
\approx0
\]

那它对最终 Loss 的责任：

> 也会很小。

---

## 59. 这就是 Credit Assignment

最终 Loss：

> 不平均怪罪所有神经元。

它会根据：

- 谁真正影响了输出；
- 影响方向；
- 当前激活；
- 后续权重；

逐层计算责任。

---

## 60. 再穿过 ReLU

有了：

\[
\frac{\partial L}{\partial h_1}
\]

还不能直接得到：

\[
\frac{\partial L}{\partial z_1}
\]

因为：

\[
h_1=ReLU(z_1)
\]

所以：

\[
\boxed{
\delta_1
=
\frac{\partial L}{\partial z_1}
=
\frac{\partial L}{\partial h_1}
\odot
ReLU'(z_1)
}
\]

---

## 61. 这里的 \(\odot\) 是什么？

表示：

# Element-wise Multiplication

逐元素相乘。

也就是说：

> 每一个 Hidden Dimension 都乘自己的 ReLU Mask。

---

## 62. 最后第一层 Weight 梯度

\[
z_1=W_1X+b_1
\]

所以：

\[
\boxed{
\frac{\partial L}{\partial W_1}
=
\delta_1X^T
}
\]

Bias：

\[
\boxed{
\frac{\partial L}{\partial b_1}
=
\delta_1
}
\]

---

## 63. 到这里整个 Backprop 已经闭环

\[
\boxed{
\delta_2
\rightarrow
\nabla W_2
\rightarrow
\nabla h_1
\rightarrow
\delta_1
\rightarrow
\nabla W_1
}
\]

这就是一个最基础 MLP 的 Backprop。

---

## 64. 第四个核心心智模型

### 心智模型 ④：每一层都同时承担两个 Backward 任务

对于一个 Linear Layer：

它要计算：

\[
\boxed{
ParameterGradient
}
\]

即：

> 自己的参数责任。

同时还要计算：

\[
\boxed{
InputGradient
}
\]

即：

> 应该继续向前一层传多少责任。

---

## 65. 这句话很重要

每层 Backward 不只是：

> “算自己的 Weight 梯度。”

还必须：

> 把梯度传给前面。

否则：

> 网络早期层永远学不到。

---

## 66. 用一个小数值例子

假设：

\[
h_1=
\begin{bmatrix}
0.8\\
0.2
\end{bmatrix}
\]

输出 Weight：

\[
W_2=
\begin{bmatrix}
1.5&-1
\end{bmatrix}
\]

预测：

\[
p=0.3
\]

真实：

\[
y=1
\]

---

## 67. 输出误差信号

\[
\delta_2=p-y
\]

所以：

\[
\boxed{
\delta_2=-0.7
}
\]

---

## 68. \(W_2\) 梯度

\[
\nabla W_2
=
\delta_2h_1^T
\]

所以：

\[
=
-0.7
\begin{bmatrix}
0.8&0.2
\end{bmatrix}
\]

得到：

\[
\boxed{
[-0.56,-0.14]
}
\]

---

## 69. 传播给 Hidden State

\[
\nabla h_1
=
W_2^T\delta_2
\]

所以：

\[
=
\begin{bmatrix}
1.5\\
-1
\end{bmatrix}
(-0.7)
\]

得到：

\[
\boxed{
\begin{bmatrix}
-1.05\\
0.7
\end{bmatrix}
}
\]

---

## 70. 这个结果什么意思？

第一个 Hidden Dimension：

\[
-1.05
\]

第二个：

\[
0.7
\]

说明：

> 对当前样本来说，它们对最终 Loss 的影响方向完全不同。

这就是：

> 责任并不是平均分配。

---

## 71. 如果第一层 ReLU 前值是

\[
z_1=
\begin{bmatrix}
1.2\\
-0.5
\end{bmatrix}
\]

ReLU Mask：

\[
\begin{bmatrix}
1\\
0
\end{bmatrix}
\]

那么：

\[
\delta_1
=
\begin{bmatrix}
-1.05\\
0.7
\end{bmatrix}
\odot
\begin{bmatrix}
1\\
0
\end{bmatrix}
\]

---

## 72. 得到

\[
\boxed{
\delta_1=
\begin{bmatrix}
-1.05\\
0
\end{bmatrix}
}
\]

第二条路径：

> 当前样本下被 ReLU 截断了。

---

## 73. 这就是 Gradient Flow

# 梯度流

梯度沿网络：

> 从 Loss 向输入方向流动。

每经过一个运算：

> 会被变换一次。

最终网络是否好训练，

很大程度取决于：

\[
\boxed{
Gradient\ Flow
}
\]

是否健康。

---

## 74. 梯度为什么会消失？

Chain Rule：

\[
\frac{\partial L}{\partial W_1}
\]

中间可能乘：

\[
0.1\times0.1\times0.1\times\cdots
\]

网络很深时：

> 越乘越小。

这就是：

# Vanishing Gradient

---

## 75. Sigmoid 是典型例子

Sigmoid 导数最大：

\[
0.25
\]

如果很多层都处于：

> 小导数区域，

那么：

\[
Gradient
\]

快速衰减。

前面层几乎学不到。

---

## 76. 梯度也可能爆炸

如果每一层局部放大：

\[
2\times2\times2\times\cdots
\]

深度一大：

> 梯度会非常巨大。

这叫：

# Exploding Gradient

---

## 77. 梯度爆炸会怎样？

可能看到：

- Loss 突然爆炸；
- Gradient Norm 极大；
- 参数出现 Inf；
- 参数出现 NaN；
- 训练崩溃。

第一课第 5 阶段提到的：

\[
GradientNorm
\]

现在终于有了内部解释。

---

## 78. 为什么要监控 Gradient Norm？

例如：

\[
\|\nabla_\theta L\|
\]

如果长期：

\[
\approx0
\]

可能：

> 梯度消失。

如果突然：

\[
10^5
\]

甚至更大：

> 可能出现梯度爆炸。

---

## 79. 什么是 Gradient Clipping？

一种常见保护：

> 当梯度太大时，把它限制到某个范围。

例如：

\[
\|\nabla\|>1
\]

就把整体缩放到：

\[
1
\]

附近。

---

## 80. 这不是“修好模型”

Gradient Clipping：

> 更多像安全护栏。

它可以防止：

> 一次异常大梯度毁掉训练。

但如果根本原因是：

- LR 太大；
- 初始化差；
- 数值不稳定；

还是要真正诊断。

---

## 81. 初始化为什么影响 Backprop？

假设权重一开始：

> 全部非常大。

Forward：

> Activation 可能爆炸。

Backward：

> 梯度也可能爆炸。

如果权重：

> 全部太小，

信号和梯度可能逐层衰减。

---

## 82. Xavier / He 初始化的深层意义

它们不是为了：

> “随机得更漂亮”。

目标之一是：

\[
\boxed{
让Forward信号和Backward梯度
在网络深处保持合理尺度
}
\]

---

## 83. Residual Connection 为什么重要？

以后 Transformer 会大量看到：

\[
\boxed{
y=x+F(x)
}
\]

这种：

# Residual Connection

残差连接。

---

## 84. 从 Backprop 看 Residual

如果：

\[
y=x+F(x)
\]

那么：

\[
\frac{\partial y}{\partial x}
=
1+
\frac{\partial F}{\partial x}
\]

里面天然有一条：

\[
1
\]

的梯度通道。

这让深层网络：

> 更容易传播梯度。

---

## 85. 所以 ResNet / Transformer 的残差不是装饰

它对：

- 信息流；
- 梯度流；
- 深层训练稳定性；

都非常关键。

以后学 Transformer Block 时会重新深入。

---

## 86. Normalization 也和梯度稳定有关

LayerNorm / RMSNorm：

> 不只是控制 Forward 数值范围。

它们也会改变：

\[
GradientFlow
\]

所以现代深网络中的：

\[
Activation
+
Initialization
+
Normalization
+
Residual
\]

是一个整体。

---

## 87. 第五个核心心智模型

### 心智模型 ⑤：深度网络能不能学，不只取决于“有没有梯度”，还取决于梯度能不能健康地走完整个网络

所以专业训练会关注：

\[
\boxed{
Gradient\ Flow
}
\]

而不是只看：

> Train Loss 有没有下降。

---

## 88. 现在进入 Batch Gradient

前面都是单样本：

\[
L_i
\]

真实训练：

> 一个 Batch 有很多样本。

通常定义：

\[
L_{batch}
=
\frac1B
\sum_{i=1}^{B}L_i
\]

---

## 89. 梯度也会平均

因为求导是线性的：

\[
\boxed{
\nabla L_{batch}
=
\frac1B
\sum_i\nabla L_i
}
\]

也就是说：

> Batch Gradient 是多个样本训练意见的综合。

---

## 90. 这和第一课 Mini-batch 连接起来了

当时说：

> Batch 是全数据梯度的一个 noisy estimate。

现在能看到数学原因：

\[
\boxed{
BatchGradient
=
样本梯度的平均/聚合
}
\]

不同 Batch：

> 样本不同，

所以 Gradient：

> 会有噪声。

---

## 91. 为什么 Batch 太小梯度更抖？

因为样本少：

> 单个特殊样本影响更大。

例如一个 Batch：

\[
B=2
\]

恰好两个都是 Hard Example，

梯度方向可能很极端。

---

## 92. 大 Batch 呢？

样本更多：

> 平均以后梯度更稳定。

但：

- 显存更大；
- 更新频率相对下降；
- 优化行为也会变化。

所以仍然不存在：

> 越大越好。

---

## 93. Gradient Accumulation 到底累积什么？

现在可以真正理解了。

Micro-batch 1：

\[
\nabla L_1
\]

Micro-batch 2：

\[
\nabla L_2
\]

……

先不：

\[
optimizer.step()
\]

而是把 `.grad` 累积。

然后统一更新。

---

## 94. PyTorch 为什么要 `zero_grad()`？

因为 PyTorch 默认：

> Gradient 会累加。

例如第一次：

\[
w.grad=0.4
\]

第二次 Backward 又：

\[
0.3
\]

结果可能变：

\[
0.7
\]

而不是自动覆盖。

---

## 95. 标准训练循环于是变得很清楚

```python
optimizer.zero_grad()

logits = model(x)
loss = criterion(logits, y)

loss.backward()

optimizer.step()
```

四个关键动作：

```text
清旧梯度
→ Forward
→ Backward算新梯度
→ 更新参数
```

---

## 96. 如果忘了 zero_grad 会怎样？

梯度会：

> 一直累积。

除非你就是故意做：

# Gradient Accumulation

否则训练会完全偏离预期。

这是非常经典的初学者 Bug。

---

## 97. `loss.backward()` 到底做了什么？

概念上：

1. 从 Loss 开始；
2. 找到 Loss 的计算图；
3. 反向遍历；
4. 应用各节点 Local Gradient；
5. 把最终参数梯度写进 `.grad`。

所以：

\[
\boxed{
backward()
\neq
optimizer.step()
}
\]

再强调一次。

---

## 98. 参数本身存在哪里？

例如：

```python
linear.weight
```

保存：

\[
W
\]

而：

```python
linear.weight.grad
```

保存：

\[
\frac{\partial L}{\partial W}
\]

这是两个完全不同的 Tensor。

---

## 99. 这就是 Weight 和 Gradient 的关系

训练中一个参数有两套重要数字：

\[
\boxed{
Value
}
\]

当前参数值。

以及：

\[
\boxed{
Gradient
}
\]

当前 Batch 告诉它：

> 应该往什么方向调整。

---

## 100. Optimizer 还可能保存第三套状态

比如 Adam：

> 不只看当前 Gradient。

还会维护：

- 一阶动量；
- 二阶动量。

所以训练状态可能包含：

\[
Parameter
+
Gradient
+
OptimizerState
\]

这就是为什么训练 Checkpoint 比纯推理 Weight 大很多。

---

## 101. `requires_grad` 是什么？

PyTorch 中 Tensor 可以指定：

```python
requires_grad=True
```

意思是：

> 希望 Autograd 跟踪与它有关的梯度。

模型 Parameter：

> 通常默认如此。

---

## 102. 数据 Tensor 一般不需要参数梯度

输入：

```python
x
```

通常：

\[
requires\_grad=False
\]

因为我们不准备：

> 优化训练数据本身。

但模型：

\[
W
\]

要：

\[
requires\_grad=True
\]

---

## 103. 什么叫 Detach？

假设你有：

\[
h
\]

但不希望后续操作的梯度：

> 再传回 h 之前的网络。

可以：

# Detach

概念上相当于：

\[
\boxed{
StopGradient
}
\]

---

## 104. Stop Gradient 有什么意义？

有些模型结构需要：

> 使用一个值，

但不希望：

> 通过这条路径训练前面的参数。

这时可以人为切断计算图。

以后强化学习、对比学习、教师模型等会经常看到。

---

## 105. `no_grad()` 和 detach 不一样

`no_grad()`：

> 在一个代码区域内关闭梯度记录。

Detach：

> 针对某个 Tensor 切断历史计算图。

两者目的相关：

> 但不是同一个概念。

---

## 106. 为什么同一计算图通常不能无限 backward？

框架为了节省内存：

> 第一次 Backward 后，很多计算图中间缓存会释放。

如果想再次 Backward：

> 有时需要保留图。

PyTorch 可见：

```python
retain_graph=True
```

但普通训练：

> 通常不需要。

---

## 107. 为什么要释放图？

因为深网络计算图：

> 很占显存。

如果每个 Step 的图都一直保存：

> 很快 OOM。

所以典型训练：

```text
Forward
↓
Backward
↓
释放当前图
↓
Next Batch
```

---

## 108. 现在看“计算图动态构建”

PyTorch 常被称为：

# Dynamic Computation Graph

不同 Forward：

> 可以根据 Python 控制流构造不同图。

这对调试和研究：

> 很方便。

---

## 109. Autograd 为什么不是数值差分？

一种最笨求梯度方法：

\[
\frac{L(w+\epsilon)-L(w)}{\epsilon}
\]

叫：

> 数值差分近似。

但几十亿参数：

> 根本不可行。

---

## 110. Backprop / Automatic Differentiation 更高效

它利用：

> 运算规则 + Chain Rule + 计算图复用。

通常一次 Forward + Backward：

> 就能计算所有参数梯度。

这就是神经网络训练能够成立的工程基础。

---

## 111. Gradient Checking 是什么？

虽然实际训练用 Autograd，

但开发一个自定义算子时：

> 可以用数值差分检查梯度是否正确。

即比较：

\[
Gradient_{analytic}
\]

和：

\[
Gradient_{numeric}
\]

是否接近。

---

## 112. 为什么这是好办法？

因为：

> Forward 看起来正常，

不代表：

> Backward 写对了。

一个自定义算子的梯度错：

> 模型可能还能跑，

但永远学不好。

---

## 113. Backprop 能告诉模型“法律逻辑”吗？

不能。

它只告诉：

\[
\boxed{
怎样改变参数才能降低当前Loss
}
\]

如果标签设计错误：

> Backprop 仍会非常勤奋地学习错误目标。

这重新连接第一课最核心的一句话：

\[
\boxed{
模型不知道我们的真实业务目标，
它只会降低我们定义的Loss。
}
\]

---

## 114. 一个政府采购错误标签例子

条款实际上：

> 不应直接判高风险。

但标注：

\[
y=1
\]

模型预测：

\[
p=0.2
\]

那么：

\[
p-y=-0.8
\]

Backprop 会告诉模型：

> 你应该更倾向于把这种样本判风险。

---

## 115. 也就是说 Backprop 不会纠正老师

它假设：

> Loss 是对的。

> Label 是训练目标。

所以：

\[
\boxed{
BadLabel
\rightarrow
ValidGradient
\rightarrow
WrongLearning
}
\]

这也是为什么专家标注质量如此重要。

---

## 116. Hard Example 为什么会产生有价值梯度？

如果模型已经预测：

\[
p=0.999
\]

真实：

\[
y=1
\]

那么：

\[
p-y\approx0
\]

梯度非常小。

说明：

> 这个样本已经没什么可教的。

---

## 117. 高置信度错误则完全相反

模型：

\[
p=0.99
\]

真实：

\[
y=0
\]

那么：

\[
p-y=0.99
\]

训练信号：

> 非常强。

这就是第一课为什么说：

\[
\boxed{
HighConfidenceWrong
=
高价值训练数据
}
\]

现在你看到数学原因了。

---

## 118. 但“大梯度 = 好样本”也不能机械理解

一个大梯度也可能来自：

- 错标；
- OOD；
- 异常数据；
- 数值问题。

所以依然需要：

> Error Analysis。

---

## 119. Gradient 是局部信息

非常重要。

\[
\nabla L
\]

只告诉：

> 当前参数点附近的下降方向。

它并不知道：

> 整个 Loss Landscape 的全局最佳点在哪。

所以训练是：

\[
\boxed{
Many\ Small\ Local\ Decisions
}
\]

很多次局部小决策。

---

## 120. 这就是为什么 Learning Rate 很重要

Gradient：

> 告诉方向和局部斜率。

LR：

> 决定走多远。

\[
\Delta\theta=-\eta\nabla L
\]

如果：

\[
\eta
\]

太大：

> 可能一步跨过好区域。

---

## 121. 如果 LR 太小

方向正确，

但：

> 每一步像蜗牛。

训练：

> 非常慢。

所以：

\[
\boxed{
Gradient
决定方向
}
\]

\[
\boxed{
LearningRate
决定步长
}
\]

---

## 122. Optimizer 为什么还需要比 SGD 更复杂？

因为真实 Loss Landscape：

> 非常高维、弯曲、噪声大。

单纯：

\[
-\eta g
\]

不一定高效。

于是：

- Momentum；
- Adam；
- AdamW；

会利用更多历史信息。

下一阶段可以专门讲。

---

## 123. Backprop 和 Optimizer 必须分离理解

Backprop：

\[
\boxed{
What\ is\ the\ gradient?
}
\]

Optimizer：

\[
\boxed{
Given\ the\ gradient,\ how\ should\ parameters\ move?
}
\]

这是两个不同层次的问题。

---

## 124. 现在把矩阵 Backprop 的 Shape 串起来

Forward：

\[
X:(B,d_{in})
\]

\[
W:(d_{out},d_{in})
\]

输出：

\[
Z:(B,d_{out})
\]

---

## 125. 假设上游梯度

\[
G_Z=
\frac{\partial L}{\partial Z}
\]

Shape：

\[
(B,d_{out})
\]

那么：

\[
\nabla W
\]

Shape 必须和：

\[
W
\]

一样：

\[
\boxed{
(d_{out},d_{in})
}
\]

---

## 126. 输入梯度 Shape 呢？

\[
\nabla X
\]

必须和：

\[
X
\]

一样：

\[
\boxed{
(B,d_{in})
}
\]

这是一个非常实用的调试规律：

\[
\boxed{
GradientShape
=
VariableShape
}
\]

---

## 127. Bias Gradient 呢？

Bias：

\[
(d_{out},)
\]

所以：

\[
\nabla b
\]

也必须：

\[
(d_{out},)
\]

Batch 维度：

> 被求和或平均掉。

---

## 128. 这就是 Shape 对 Backward 也重要

不是只有 Forward 才追 Shape。

Backward 也要问：

> 这个梯度属于哪个 Tensor？

它的 Shape：

> 必须匹配原变量。

---

## 129. Transformer Backprop 本质有没有变？

没有。

虽然 Attention 看起来复杂：

\[
QK^T
\]

\[
Softmax
\]

\[
AV
\]

但每一个运算：

> 都有自己的 Local Gradient。

Autograd：

> 沿巨大计算图执行 Chain Rule。

---

## 130. LLM 的 70B 参数怎么一起获得梯度？

不是：

> 人工为 700 亿参数分别写规则。

而是：

1. Forward 构建计算；
2. 最终得到 Loss；
3. Autograd 从 Loss 反向遍历图；
4. 每个 Parameter 自动得到自己的 Gradient。

本质没有离开今天的：

\[
\boxed{
ChainRule
}
\]

---

## 131. LoRA 又怎么理解？

未来你微调 ProcurementLM 时：

> 可能冻结原始大部分 Weight。

即：

\[
requires\_grad=False
\]

只让：

> LoRA 参数参与梯度计算和更新。

---

## 132. 所以 LoRA 的内部本质之一

不是：

> 不需要 Backprop。

而是：

\[
\boxed{
Backprop仍然存在，
只是TrainableParameters少了
}
\]

这会减少：

- Gradient Memory；
- Optimizer State；
- 更新成本。

---

## 133. QLoRA 呢？

基础模型可以：

> 以低比特量化形式存储。

同时训练：

> LoRA Adapter。

Backward：

> 主要为 Adapter 参数产生需要更新的梯度。

这也是为什么显存需求大幅下降。

---

## 134. 冻结参数意味着什么？

参数仍可能参加：

# Forward

但：

> 不需要为它保存可更新 Gradient / Optimizer State。

所以：

\[
\boxed{
UsedInForward
\neq
Trainable
}
\]

这个区别以后非常重要。

---

## 135. 一个模型输出错了，Backprop 能知道“为什么错”吗？

数学上的“为什么”：

> 能追踪哪些参数影响了 Loss。

业务上的“为什么”：

> 不一定。

这两个“解释”不同。

Backprop 是：

# Mathematical Credit Assignment

不是：

# Legal Reasoning Explanation

---

## 136. 所以不要把 Gradient 当成业务因果解释

某个参数 Gradient 很大：

> 只意味着当前 Loss 对它敏感。

不能直接推出：

> 这个现实因素就是合规风险的因果原因。

这又和第一课第 12 阶段连接起来。

---

## 137. Backprop 的真正奇妙之处

网络可能有：

\[
100
\]

层。

参数：

\[
Billion+
\]

最终只有：

\[
一个Loss
\]

却能够把这个单一误差信号：

> 分解成每一个参数自己的梯度。

这就是：

\[
\boxed{
CreditAssignment
}
\]

---

## 138. 但 Loss 可以有多个组成部分

例如政府采购模型：

\[
L
=
L_{risk}
+
\lambda_1L_{type}
+
\lambda_2L_{citation}
\]

那么最终 Gradient：

\[
\boxed{
\nabla L
=
\nabla L_{risk}
+
\lambda_1\nabla L_{type}
+
\lambda_2\nabla L_{citation}
}
\]

---

## 139. 这就是 Multi-task Training 的内部机制

不同任务：

> 都在对同一批参数施加梯度。

有时方向一致：

> 相互帮助。

有时方向冲突：

> Gradient Conflict。

---

## 140. 政府采购例子

风险判断任务希望：

> 强调竞争限制。

法规引用任务希望：

> 强调条文匹配。

文书生成任务希望：

> 强调语言表达。

这些 Loss：

> 会共同塑造 Hidden Representation。

---

## 141. Gradient Conflict 为什么值得关注？

如果一个参数：

任务 A：

\[
g_A>0
\]

任务 B：

\[
g_B<0
\]

它们会：

> 互相抵消。

所以 Multi-task 并不是：

> 任务越多越好。

---

## 142. Loss Weight 就变得很重要

\[
L
=
L_1
+
10L_2
\]

意味着：

> 第二个任务对 Gradient 的影响可能大很多。

所以：

\[
\boxed{
LossWeight
=
TrainingPriority
}
\]

这是很重要的心智模型。

---

## 143. Backprop 和“模型在思考”不是一回事

Forward：

> 产生当前预测。

Backward：

> 是训练阶段的参数学习机制。

模型实际回答用户时：

> 一般只有 Forward，不会现场 Backprop。

---

## 144. 所以模型不会每聊一句都自动学习

普通推理：

\[
ForwardOnly
\]

不会自动：

\[
UpdateWeights
\]

这也是为什么：

> 对话上下文和长期模型参数要分开理解。

---

## 145. In-context Learning 又是什么？

Prompt 给示例：

> 会改变当前输入 Context。

于是：

\[
HiddenActivation
\]

发生变化。

但模型 Weight：

> 不需要更新。

所以这更接近：

\[
\boxed{
Learning-like\ behavior\ without\ weight\ update
}
\]

---

## 146. Fine-tuning 才真正修改 Weight

Fine-tuning：

\[
Forward
\rightarrow
Loss
\rightarrow
Backward
\rightarrow
Optimizer
\]

重复很多次。

于是：

\[
W
\]

真正发生改变。

---

## 147. 第六个核心心智模型

### 心智模型 ⑥：推理改变 Activation，训练通过 Backprop 改变 Weight

这是理解 LLM 很关键的一条线：

\[
\boxed{
Inference
\rightarrow
DynamicState
}
\]

\[
\boxed{
Training
\rightarrow
ParameterState
}
\]

---

## 148. 本阶段最应该会手算什么？

至少要能手算：

\[
z=wx+b
\]

\[
L=\frac12(z-y)^2
\]

然后得到：

\[
\boxed{
\frac{\partial L}{\partial w}
=
(z-y)x
}
\]

---

## 149. 还应该理解二分类核心结果

Sigmoid + BCE：

\[
\boxed{
\frac{\partial L}{\partial z}
=
p-y
}
\]

再：

\[
\boxed{
\frac{\partial L}{\partial w_i}
=
(p-y)x_i
}
\]

这两个公式以后会成为非常稳定的直觉锚点。

---

## 150. 第二课 · 第 5 阶段核心总结

把整个 Backprop 压缩成：

\[
\boxed{
Loss
\rightarrow
UpstreamGradient
\rightarrow
LocalGradient
\rightarrow
ParameterGradient
}
\]

再进入：

\[
\boxed{
Optimizer
\rightarrow
ParameterUpdate
}
\]

如果只保留 5 个核心专家心智模型：

| 心智模型 | 核心认知 |
|---|---|
| **① Gradient 是 Loss 对参数的局部敏感度** | 它告诉方向和局部变化率，不是业务“好坏分” |
| **② Backprop 本质是高效执行 Chain Rule** | 复杂网络只是计算图更大，数学原则没变 |
| **③ 每个节点都在做“上游梯度 × 本地梯度”** | 这是理解所有反向传播的统一语言 |
| **④ 每一层既算自己的参数梯度，也负责把梯度继续传给前层** | 这就是真正的 Credit Assignment |
| **⑤ 可训练性取决于 Gradient Flow 是否健康** | Vanishing、Exploding、Residual、Initialization、Normalization 都围绕它展开 |

如果只记一句：

\[
\boxed{
Forward回答“模型现在算出了什么”，
Backward回答“为了让Loss下降，每个参数分别应该承担多少责任”。
}
\]

---

## 151. 第二课前五阶段现在真正闭环

第 1 阶段：

\[
z=WX+b
\]

> 参数如何组合信息。

第 2 阶段：

\[
h=f(z)
\]

> 非线性如何产生复杂能力。

第 3 阶段：

\[
X\rightarrow H_1\rightarrow H_2
\]

> 模型如何逐层学习 Representation。

第 4 阶段：

\[
Forward
\]

> 当前参数如何处理一个具体输入。

第 5 阶段：

\[
Backward
\]

> 最终错误如何反向分配到所有参数。

现在已经形成：

\[
\boxed{
Forward
\rightarrow
Loss
\rightarrow
Backward
}
\]

下一块自然就是：

\[
\boxed{
Optimizer
}
\]

因为我们已经知道：

> 梯度是什么。

下一阶段就该回答：

> **拿到 Gradient 以后，为什么不是简单减一下就结束？SGD、Momentum、Adam、AdamW 到底分别在解决什么问题？**

也就是 **第二课 · 第 6 阶段：Optimizer 与 Learning Rate——参数究竟怎样真正迈出每一步。**

---
