# 第五课 · 第 7 阶段
# LoRA Rank、Alpha、Dropout
## `r`、`alpha`、`dropout` 到底分别在控制什么，怎样避免“照抄参数”？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，Rank r 决定 LoRA 的低秩适配容量，并线性影响 Adapter 参数量。**
2. **第二，Alpha 不增加容量；在标准 LoRA 中真正起作用的是 alpha / r 这样的有效 Scaling。**
3. **第三，Learning Rate 决定参数怎样更新，Alpha 决定 LoRA 分支怎样缩放，两者不是同一个东西。**
4. **第四，Dropout 是训练阶段的正则化工具，不是能力旋钮，也不是越大越好。**
5. **第五，任何 r / alpha / dropout 配置都必须放进固定 Dataset、固定 Target Modules、固定 Benchmark 的控制变量实验里判断。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `LoRA` | LoRA：冻结大部分基座参数，只训练低秩增量矩阵 |
| `Rank` | LoRA Rank：低秩增量的容量参数 |
| `Alpha` | LoRA Alpha：控制低秩更新缩放幅度 |
| `Adapter` | 适配器：附加在基座模型上的轻量可训练参数模块 |
| `Target Modules` | 目标模块：指定 LoRA 插入哪些线性层 |
| `Validation` | 验证集：开发阶段用于选模型、调参数和早停 |

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

第 6 阶段我们真正搞懂了：

\[
\Delta W = BA
\]

也就是说，LoRA 不直接改 Base Weight \(W\)，而是学习：

\[
\Delta W
\]

现在马上会遇到训练配置：

```python
r = 16
lora_alpha = 32
lora_dropout = 0.05
```

很多人到这里开始变成：

> “网上别人这么配，我也这么配。”

这一阶段的目标正好相反。

你最终要做到：

> **看到 `r / alpha / dropout`，脑子里立刻知道它们分别改变了“容量、尺度、正则化”中的哪一件事。**

本阶段最终形成：

# `LoRAHyperparameterPolicy_V0.1`

---

# 一、本阶段只解决一个核心问题

LoRA 的输出可以写成：

\[
y
=
Wx
+
sBAx
\]

其中常见标准 LoRA 实现采用：

\[
s=\frac{\alpha}{r}
\]

于是：

\[
\boxed{
y
=
Wx
+
\frac{\alpha}{r}BAx
}
\]

今天所有内容其实都围绕三件事：

```text
Rank r
决定：
LoRA有多少“变化容量”

Alpha
决定：
LoRA分支采用什么缩放尺度

Dropout
决定：
训练时对LoRA路径施加多少随机正则化
```

总图先锁住：

```text
                    Base Model
                       Wx
                        │
输入 x ─────────────────┼────────────► 相加 ──► 输出
                        │
                        │
                  LoRA Branch
                        │
                  Dropout(x)
                        │
                        ▼
                        A
                        │
                  低维空间 r
                        │
                        ▼
                        B
                        │
                        ▼
                       BAx
                        │
                        ▼
                  Scaling α/r
```

一句话：

> **Rank 管容量，Alpha 管缩放，Dropout 管训练正则化。**

---

# 二、先锁死 5 个核心心智模型

## 心智模型 1：Rank 是“容量旋钮”，不是“强度旋钮”

上一阶段：

\[
A\in\mathbb{R}^{r\times d_{in}}
\]

\[
B\in\mathbb{R}^{d_{out}\times r}
\]

中间的：

\[
r
\]

决定 LoRA 有多少低秩维度。

所以：

\[
\boxed{
r\uparrow
\Rightarrow
AdaptationCapacity\uparrow
}
\]

同时：

\[
\boxed{
TrainableParameters\uparrow
}
\]

Rank 主要回答：

> **允许 LoRA 表达多复杂的权重变化？**

它不是直接回答：

> LoRA 对 Base Model “声音有多大”。

---

## 心智模型 2：Alpha 不增加表达维度，它主要改变 LoRA 更新的缩放尺度

在常见标准 LoRA 中：

\[
\Delta W_{\text{effective}}
=
\frac{\alpha}{r}BA
\]

这里：

\[
\alpha
\]

并没有给 A、B 增加新的行或列。

也就是说：

> **Alpha 不增加 Rank。**

它主要控制：

\[
BA
\]

进入最终模型时的缩放。

所以：

\[
\boxed{
Rank
\neq
Alpha
}
\]

一个管：

> 能表达多少方向。

一个管：

> 这些变化以什么尺度作用。

---

## 心智模型 3：比较 Rank 时，必须注意 Scaling Policy，否则实验变量混在一起了

这是非常实用的一条。

假设实验 A：

```text
r = 8
alpha = 16
```

那么：

\[
\frac{\alpha}{r}=2
\]

实验 B：

```text
r = 16
alpha = 16
```

那么：

\[
\frac{\alpha}{r}=1
\]

你以为自己只改变了：

> Rank。

其实同时还改变了：

> LoRA Scaling。

所以结果不好时，你不知道到底是：

```text
容量变化
```

还是：

```text
缩放变化
```

导致的。

因此做 Rank 对照实验时：

> **必须明确你的 Alpha / Scaling 策略。**

---

## 心智模型 4：Dropout 主要是“防止 Adapter 过度依赖固定特征”，不是增加模型能力

LoRA Dropout 通常只在训练阶段生效。

概念上：

```text
LoRA输入
   ↓
随机丢掉一部分激活
   ↓
A
   ↓
B
```

这样 Adapter 不能总是：

> 死死依赖某几个固定输入模式。

因此它主要属于：

# Regularization
## 正则化

而不是：

# Capacity

所以：

\[
\boxed{
Dropout
不是“能力越大越好”的参数
}
\]

---

## 心智模型 5：`r / alpha / dropout` 没有脱离 Dataset 和 Benchmark 的“最佳答案”

真正参数选择流程不是：

```text
查博客
↓
复制 16 / 32 / 0.05
```

而是：

```text
固定Dataset
      ↓
固定Target Modules
      ↓
建立Baseline
      ↓
改一个核心变量
      ↓
Validation
      ↓
Hard Case
      ↓
Training Stability
      ↓
决定是否调整
```

最终原则：

\[
\boxed{
Hyperparameter
必须由Evidence决定
}
\]

---

# 三、把三个参数一次精准区分

| 参数 | 核心作用 | 增大以后主要发生什么 |
|---|---|---|
| **Rank `r`** | LoRA 容量 | 可表达的低秩变化空间增大、参数量增加 |
| **Alpha `α`** | LoRA 缩放 | 改变 LoRA 更新分支的有效尺度 |
| **Dropout** | 正则化 | 训练时随机屏蔽部分 LoRA 输入，降低过度依赖 |
| **Target Modules** | 改哪里 | 决定哪些模型计算路径拥有 LoRA |

最后一项虽然不是今天主角，但一定要放进脑子里。

因为真实 LoRA 容量不是只由：

\[
r
\]

决定。

更接近：

\[
\boxed{
LoRACapacity
\sim
Rank
\times
TargetModules
\times
Layers
}
\]

---

# 四、Rank：到底控制什么？

第 6 阶段已经知道：

\[
N_{\text{LoRA}}
=
r(d_{in}+d_{out})
\]

假设：

\[
d_{in}=d_{out}=4096
\]

那么：

### `r = 8`

\[
8(4096+4096)
=
65,536
\]

### `r = 16`

\[
16(4096+4096)
=
131,072
\]

### `r = 32`

\[
32(4096+4096)
=
262,144
\]

也就是说：

> Rank 翻倍，这个 LoRA 模块的可训练参数量也大约翻倍。

所以 Rank 是一个真正的：

# Capacity–Cost Tradeoff
## 容量—成本权衡

---

# 五、Rank 太小会怎样？

如果任务变化复杂，但 Rank 很小：

```text
模型想学：
风险分类
+
结构化输出
+
边界案例
+
abstention
+
复杂理由模式
```

而 LoRA 允许的变化空间过窄，

可能出现：

```text
Training Loss降不下去
        或
Train可以改善
但Validation很早到瓶颈
        或
简单案例改善
Hard Case仍长期失败
```

这种情况才开始支持一个判断：

> **可能存在 Adapter Capacity Bottleneck。**

注意：

不是只看 Loss 不理想就立刻增大 Rank。

因为还可能是：

```text
数据错
Learning Rate错
Target Modules选错
Prompt格式错
训练时间不够
```

---

# 六、Rank 太大又会怎样？

更大的 Rank：

> 给 Adapter 更多自由度。

但代价是：

```text
Trainable Parameters ↑
Optimizer State ↑
Adapter Size ↑
训练计算 ↑
过拟合空间 ↑
```

特别是数据量不大时，

模型可能越来越擅长：

> 记训练表达。

却不一定更擅长：

> 处理真正新的采购条款。

所以：

\[
\boxed{
RankEnough
>
RankMaximum
}
\]

我们真正找的是：

> **足够的 Rank。**

不是：

> 最大的 Rank。

---

# 七、Alpha：最容易被误解的参数

常见标准 LoRA：

\[
y
=
Wx
+
\frac{\alpha}{r}BAx
\]

因此定义：

\[
s
=
\frac{\alpha}{r}
\]

我们真正应该盯住的是：

# Effective Scaling
## 有效缩放

而不仅仅是 Alpha 这个数字。

例如：

```text
r = 8
alpha = 16
```

则：

\[
s=2
\]

而：

```text
r = 16
alpha = 32
```

仍然：

\[
s=2
\]

虽然 Rank 翻倍，

但 Scaling 保持不变。

这是一种很容易理解的控制方式。

---

# 八、Alpha 越大是不是 LoRA 就一定“学得更快”？

不要这样理解。

Alpha 直接进入的是：

> LoRA 分支的缩放。

而真正训练速度和稳定性还受到：

```text
Learning Rate
Optimizer
Gradient
Initialization
Rank
Target Modules
```

共同影响。

所以：

\[
\boxed{
Alpha
\neq
LearningRate
}
\]

Learning Rate：

> 控制参数每一步怎样更新。

Alpha / Scaling：

> 控制 LoRA 分支怎样贡献到网络输出。

这两个特别容易混。

---

# 九、一个非常关键的对照

假设：

\[
BAx = v
\]

那么：

### 情况 A

\[
s=0.5
\]

LoRA 贡献：

\[
0.5v
\]

### 情况 B

\[
s=2
\]

LoRA 贡献：

\[
2v
\]

所以 Alpha / Scaling 更像：

> **LoRA 分支输出的增益旋钮。**

但 A、B 本身会在训练过程中适应这个尺度，

因此不要把它理解成：

> 单纯把最终效果机械放大 4 倍。

真实训练是一个动态优化系统。

---

# 十、为什么实际框架里必须确认 Scaling Convention？

因为并不是所有 LoRA 变体都永远使用完全相同的：

\[
\frac{\alpha}{r}
\]

例如某些 Rank-Stabilized LoRA 变体可能采用不同的 Rank Scaling 设计。

所以工程上必须记录：

```text
peft_method
scaling_policy
rank
alpha
library_version
```

不要只记录：

```text
alpha = 32
```

却不知道：

> 它最后到底被框架怎样解释。

---

# 十一、Dropout：究竟 Drop 的是什么？

常见 LoRA 实现中，可以概念理解成：

\[
BA(Dropout(x))
\]

也就是：

> 在 LoRA 分支训练时随机屏蔽一部分输入激活。

例如：

```text
x

[1.2, 0.7, 2.1, 0.4, 1.8]
```

训练时某一步可能暂时类似：

```text
[1.2, 0, 2.1, 0, 1.8]
```

实际 Dropout 还涉及缩放规则，这里不用展开。

核心是：

> Adapter 不能保证每次都依赖完全相同的一组激活。

---

# 十二、Dropout 为什么可能帮助泛化？

假设训练集中很多 Risk 样本都恰好包含：

```text
“本地”
```

如果 Adapter 过度依赖这个特征，

可能学成：

```text
本地
→
Risk
```

适度正则化希望推动模型：

> 不要把全部能力压在少数脆弱特征上。

它应该更多结合：

```text
时间条件
+
准入性质
+
履约阶段
+
上下文
```

但要注意：

> Dropout 绝对不是解决 Shortcut Learning 的主要手段。

真正主要手段还是：

```text
Hard Negative
数据多样性
正确Label
Benchmark
```

Dropout 只是辅助正则化。

---

# 十三、Dropout 太大会怎样？

如果 Dropout 很高，

LoRA 分支训练时大量输入被随机抹掉，

可能造成：

```text
训练变慢
有效信号下降
Adapter难以充分拟合
```

所以：

\[
\boxed{
MoreDropout
\neq
MoreGeneralization
}
\]

特别是：

> 高质量数据本来就少。

再随机丢太多信号，

未必划算。

---

# 十四、Dropout = 0 是不是一定不好？

也不是。

很多 LoRA 训练：

```text
dropout = 0
```

也完全可能有效。

尤其在：

```text
数据充足
训练轮数受控
其他正则化足够
```

的情况下。

所以 Dropout 不是：

> “训练 LoRA 必须设置 0.05”。

它应该由：

> 泛化表现和训练行为决定。

---

# 十五、现在把三者真正放在一起

可以用一个非常简单的比喻：

假设 LoRA 是一个专业顾问团队。

### Rank

决定：

> 团队里允许存在多少种不同专业思路。

---

### Alpha / Scaling

决定：

> 顾问意见进入最终决策时，整体以什么尺度参与。

---

### Dropout

决定：

> 培训时不让顾问总依赖固定的几条线索。

因此：

```text
Rank
=
能学多少

Alpha
=
修正分支怎样缩放

Dropout
=
怎样防止训练过度依赖
```

这三个终于彻底分开。

---

# 十六、一个很重要的实验原则：不要同时乱改三个

假设实验 A：

```text
r = 8
alpha = 16
dropout = 0.0
```

实验 B：

```text
r = 64
alpha = 128
dropout = 0.1
```

B 好了。

你能得出什么结论？

几乎不能。

因为同时改变了：

```text
容量
Scaling
正则化
```

所以专业实验更像：

```text
Baseline
r=16
α=32
dropout=0.05

       ↓

实验1
只改Rank

       ↓

实验2
只改Scaling policy

       ↓

实验3
只改Dropout
```

这叫：

# Controlled Experiment
## 控制变量实验

---

# 十七、ProcurementLM_V0.1 第一轮应该怎么想？

不是先追求“最佳参数”。

先追求：

# Stable Baseline
## 稳定基线

例如可以选择一套中等容量配置作为**实验起点**：

```text
r = 16
alpha = 32
dropout = 0.05
```

这里不是说：

> 这是政府采购模型的最优答案。

它只是一个方便理解的 Baseline：

\[
\frac{\alpha}{r}=2
\]

然后我们真正做的事情是：

```text
固定Dataset
固定Target Modules
固定Learning Rate策略
固定Epoch
固定Benchmark
```

只改变需要研究的变量。

---

# 十八、什么时候优先试更大的 Rank？

出现以下证据组合时才值得怀疑容量不足：

```text
Training表现仍受限
+
Validation也受限
+
更多训练Step没有明显改善
+
数据质量确认正常
+
Target Modules合理
+
Learning Rate已排除明显问题
```

尤其是：

> 简单 Case 已经很好，复杂 Hard Case 长期无法进一步改善。

这时可以实验：

```text
r = 16
↓
r = 32
```

甚至更高。

但必须重新评测。

---

# 十九、什么时候反而应该减小 Rank？

如果出现：

```text
Train持续变好
但Validation开始变差
```

或者：

```text
训练集表达几乎完美复现
但新项目泛化差
```

那么你首先应该检查：

```text
过拟合
数据重复
训练Epoch
Learning Rate
数据泄漏
```

在这些因素排除以后，

降低 Adapter 容量：

> 才可能是合理实验方向之一。

---

# 二十、什么时候考虑调整 Dropout？

如果：

```text
Train Loss持续下降

Validation停滞 / 恶化

Hard Case泛化不好
```

并且已经排除：

```text
数据泄漏
Train/Test近重复
错误Label
过长训练
```

那么可以把：

> LoRA Dropout

作为正则化实验变量之一。

但它不是：

> 第一诊断按钮。

---

# 二十一、什么时候调整 Alpha？

更专业的思考不是：

> Alpha 大还是小？

而是：

> **当前 Scaling Convention 下，LoRA 分支的尺度是否稳定合理？**

我们会观察：

```text
训练Loss
Gradient Norm
训练稳定性
Validation
Base能力是否过度漂移
```

同时必须保持：

> Rank / Scaling 实验设计清楚。

否则 Alpha 很容易变成一个没有解释力的“神秘旋钮”。

---

# 二十二、一个特别重要的工程原则：Rank 实验不要忘了参数量变化

例如从：

\[
r=8
\]

到：

\[
r=64
\]

不是只有一个抽象数字变了。

LoRA 参数量近似：

\[
N_{\text{LoRA}}
=
r(d_{in}+d_{out})
\]

因此 Rank 扩大 8 倍：

> 对相同 Target Modules 而言，LoRA 参数量也近似扩大 8 倍。

于是：

```text
Adapter文件
Optimizer State
Gradient存储
训练计算
```

都会随之增加。

虽然仍远小于 Full Fine-Tuning，

但绝不是：

> “Rank 免费增大”。

---

# 二十三、Target Modules 会让 Rank 的含义进一步变化

假设：

### 配置 A

```text
r = 32

只训练
q_proj
v_proj
```

而配置 B：

```text
r = 16

训练
q_proj
k_proj
v_proj
o_proj
up_proj
gate_proj
down_proj
```

谁的总 LoRA 参数更多？

不能只看：

```text
32 > 16
```

因为 B：

> 装了更多模块。

因此：

\[
\boxed{
Rank
不能脱离
TargetModules
讨论
}
\]

这就是下一阶段为什么必须专门讲 Target Modules。

---

# 二十四、政府采购例子：什么叫“容量不足”？

假设较小 Rank 已经学会：

```text
输出格式稳定
基础风险分类
```

但在以下对比中反复失败：

```text
A:
投标前必须已有本地机构

B:
中标后必须达到现场响应要求
但不限制机构设立方式
```

并且 Hard Negative 很充分、数据没有明显问题，

那么更大的 Adapter Capacity：

> 可能帮助表达更细的决策边界。

但注意：

如果训练数据根本没有这些边界案例，

把 Rank 从：

```text
8
```

调到：

```text
128
```

也不会凭空创造正确监督。

所以：

\[
\boxed{
ModelCapacity
不能替代
DataCoverage
}
\]

---

# 二十五、这是本阶段最重要的一条因果链

```text
Data Coverage
决定：
模型有没有机会学

        ↓

Target Modules
决定：
哪些计算路径能被改

        ↓

Rank
决定：
这些路径能有多少适配容量

        ↓

Alpha / Scaling
决定：
这些变化以什么尺度参与Forward

        ↓

Dropout
决定：
训练时施加多少随机正则化

        ↓

Validation / Benchmark
决定：
这一组配置到底有没有价值
```

这就是完整思路。

---

# 二十六、本阶段几个最危险的反例

**反例 1：Rank 越大越专业。**  
错误。Rank 更大只是容量更大，同时成本和过拟合空间也更大。

**反例 2：Alpha = Learning Rate。**  
错误。Alpha 是 LoRA 分支 Scaling；Learning Rate 控制参数更新步长。

**反例 3：`alpha=32` 本身有绝对意义。**  
不完整。必须结合 Rank 和框架 Scaling Convention。

**反例 4：Dropout 越大泛化越好。**  
错误。过强 Dropout 也可能破坏有效训练信号。

**反例 5：换 Rank 时完全不关注 Alpha。**  
可能把容量变化和 Scaling 变化混为一个实验。

**反例 6：Hard Case 学不好就直接把 Rank 拉满。**  
先检查数据、Loss Mask、Target Modules、Learning Rate 和训练是否正常。

**反例 7：把网上常见的 `16/32/0.05` 当作领域最佳参数。**  
它最多是 Baseline 起点，不是证据。

---

# 二十七、本阶段工程产物：`LoRAHyperparameterPolicy_V0.1`

正式实验至少记录：

```text
adapter_method
=
LoRA

rank
=
r

alpha
=
α

scaling_policy
=
α / r
或框架实际规则

effective_scaling
=
s

dropout
=
p

target_modules
=
[...]

trainable_parameter_count

trainable_parameter_ratio

learning_rate

dataset_version

benchmark_version
```

每个实验还应该记录：

```text
train_loss
validation_loss
hard_case_metrics
grad_norm
general_capability_regression
adapter_size
```

这样：

> 参数变化和结果才有因果解释空间。

---

# 二十八、这一阶段最值得掌握的“诊断表”

| 现象 | 第一反应不要是什么 | 更应该先检查什么 |
|---|---|---|
| Train 和 Val 都很差 | 立刻加 Rank | 数据、格式、LR、Target Modules、训练是否充分 |
| Train 好、Val 差 | 再加 Rank | 过拟合、重复、泄漏、Epoch、正则化 |
| Hard Case 长期差 | Rank 拉到最大 | Hard Case 覆盖、Target Modules、容量瓶颈证据 |
| 训练震荡 | 改 Dropout | LR、Grad Norm、数值稳定性、Scaling |
| Adapter 效果很弱 | Alpha 拉大 | 是否真正训练到目标模块、梯度、数据、Scaling |

这张表非常实用。

它帮你建立：

> **先诊断，再调参。**

---

# 二十九、重新强化 5 个核心心智模型

现在把本阶段压缩到最精华：

> **第一，Rank `r` 决定 LoRA 的低秩适配容量，并线性影响 Adapter 参数量。**

> **第二，Alpha 不增加容量；在标准 LoRA 中真正起作用的是 `alpha / r` 这样的有效 Scaling。**

> **第三，Learning Rate 决定参数怎样更新，Alpha 决定 LoRA 分支怎样缩放，两者不是同一个东西。**

> **第四，Dropout 是训练阶段的正则化工具，不是能力旋钮，也不是越大越好。**

> **第五，任何 `r / alpha / dropout` 配置都必须放进固定 Dataset、固定 Target Modules、固定 Benchmark 的控制变量实验里判断。**

只要这五句真的懂：

> 以后你不会再机械抄 LoRA 参数。

---

# 三十、本阶段最核心的一张图

```text
                  Procurement SFT
                       │
                       ▼
                 LoRA Adapter
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
      Rank           Alpha          Dropout
        │              │              │
        │              │              │
        ▼              ▼              ▼
   Adaptation       Scaling       Regularization
    Capacity         Scale          Strength
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                 LoRA Training
                       │
                       ▼
              Validation / Hard Case
                       │
             ┌─────────┴─────────┐
             │                   │
          不足证据             过拟合证据
             │                   │
             ▼                   ▼
       调整Capacity         检查训练/正则化
             │                   │
             └─────────┬─────────┘
                       ▼
              Controlled Experiment
```

脑中最后只留：

> **容量、尺度、正则化——三件事，三个参数，不要混。**

---

# 三十一、本阶段掌握测试

不回看正文，你现在应该能够解释：Rank 为什么代表低秩适配容量；Rank 增大为什么 LoRA 参数量近似线性增加；为什么 Rank 大不等于一定更好；标准 LoRA 中 `alpha / r` 是什么；为什么比较不同 Rank 时必须注意 Scaling Policy；Alpha 为什么不是 Learning Rate；Dropout 训练和推理时有什么区别；Dropout 为什么属于正则化而不是容量；为什么 Dropout 过大反而可能伤害训练；为什么 `r=16, alpha=32, dropout=0.05` 只能作为实验起点而不是最优答案；为什么 Target Modules 会改变对 Rank 的理解；什么时候才有证据怀疑 Rank 容量不足；为什么 Hard Case 表现差不能直接归因于 Rank；以及为什么 LoRA 调参必须围绕固定 Benchmark 做控制变量实验。

如果这些都能够自己讲出来：

\[
\boxed{
第五课第7阶段真正掌握
}
\]

---

# 本阶段最后只记一句话

> **LoRA 的三个核心超参数各管一件事：Rank 决定“允许学习多少低秩变化容量”，Alpha/Scaling 决定“这些变化以什么尺度进入模型”，Dropout 决定“训练时施加多少正则化”；真正专业的调参不是寻找神奇数字，而是在固定数据、固定 Target Modules 和固定 Benchmark 下，用控制变量实验判断到底缺的是容量、尺度还是泛化。**

---

# 下一阶段：第五课 · 第 8 阶段
# Target Modules：LoRA 到底插在哪里？
## `q_proj`、`k_proj`、`v_proj`、`o_proj` 和 MLP 到底分别意味着什么？

第 7 阶段解决了：

> **每个 LoRA Adapter 有多大，以及怎样缩放、怎样正则化。**

第 8 阶段解决另一个更根本的问题：

> **Adapter 到底应该装在哪些 Transformer 权重上？**

我们会重新把第二课的 Transformer 拉回来：

```text
Attention
│
├── q_proj
├── k_proj
├── v_proj
└── o_proj

MLP
│
├── gate_proj
├── up_proj
└── down_proj
```

然后建立真正的工程判断：

> **Rank 决定“一个 Adapter 有多宽”，Target Modules 决定“模型哪些能力路径允许被改”。**

---
