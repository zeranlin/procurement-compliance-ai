# 第五课 · 第 5 阶段
# Full Fine-Tuning 与 PEFT
## 为什么一个 7B / 14B 模型有几十亿参数，我们却往往只训练其中极少的一部分？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **仍然使用整个 7B 模型。**
2. **模型有没有参加训练计算。**
3. **Optimizer 最后可以更新谁。**
4. **从零重新学习语言和世界知识。**
5. **未必是最合理的工程选择。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `LoRA` | LoRA：冻结大部分基座参数，只训练低秩增量矩阵 |
| `Gradient` | 梯度：损失对参数变化方向和敏感度的局部信息 |
| `Optimizer` | 优化器：依据梯度规则更新参数 |
| `Memory` | 任务记忆：保存跨步骤需要复用的结构化信息 |
| `Checkpoint` | 检查点：保存模型和训练状态以便恢复/发布 |
| `State` | 状态：保存任务进度、事实和待办 |

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

前 4 个阶段，我们实际上一直在解决：

> **训练信号怎样正确进入模型。**

现在链条已经到了这里：

```text
ProcurementDataset_V0.1
        ↓
Messages
        ↓
Chat Template
        ↓
Loss Mask
        ↓
Length / Truncation
        ↓
Padding / Packing
        ↓
Forward
        ↓
Loss
        ↓
Backward
        ↓
Gradient
```

今天第一次回答：

> **这些 Gradient 最后到底允许修改哪些参数？**

这就是：

# Parameter-Efficient Fine-Tuning
# PEFT
## 参数高效微调

本阶段最终形成一个工程决策：

# `FineTuningStrategy_V0.1`

---

# 一、本阶段只解决一个核心问题

假设我们的 Base Model 有：

```text
7B
=
约 70 亿参数
```

训练时有两个完全不同的方向：

```text
方案 A

70亿参数
几乎全部允许更新
        ↓
Full Fine-Tuning
全参数微调
```

或者：

```text
方案 B

70亿 Base Model
绝大多数冻结
        +
少量新增参数
参与训练
        ↓
PEFT
参数高效微调
```

今天真正要建立的判断能力是：

> **什么情况下值得修改整个模型，什么情况下只修改极少一部分参数反而更合理？**

---

# 二、先锁死 5 个核心心智模型

## 心智模型 1：使用整个模型 ≠ 训练整个模型

这是今天最重要的一句话。

假设：

```text
Base Model
=
7B Parameters
```

即使我们采用 PEFT，

Forward 时：

> 仍然使用整个 7B 模型。

并不是：

```text
只使用其中1%
```

真正发生的是：

```text
整个模型参与计算

但是

只有少量参数允许更新
```

所以：

\[
\boxed{
ModelSize
\neq
TrainableParameterCount
}
\]

---

## 心智模型 2：Full Fine-Tuning 和 PEFT 的核心区别，是“谁允许被 Gradient 改写”

Full Fine-Tuning：

```text
Base Model
████████████████████
几乎全部 Trainable
```

PEFT：

```text
Base Model
████████████████████
Frozen

少量参数
▓
Trainable
```

所以真正的区别不是：

> 模型有没有参加训练计算。

而是：

> **Optimizer 最后可以更新谁。**

---

## 心智模型 3：PEFT 不是“低配版训练”，而是一个不同的参数更新策略

很容易产生这种误解：

```text
Full FT
=
专业

PEFT
=
没钱时凑合
```

这不准确。

对于很多领域适配任务，我们真正想改变的是：

```text
回答格式
风险判断习惯
专业术语使用
任务边界
输出结构
领域决策模式
```

而不是：

> 从零重新学习语言和世界知识。

这时让整个几十亿参数全部移动：

> 未必是最合理的工程选择。

所以：

\[
\boxed{
PEFT
=
SelectiveAdaptation
}
\]

中文：

> **选择性适配。**

---

## 心智模型 4：可训练参数越多，不代表最终效果一定越好

更多 Trainable Parameters 意味着：

```text
表达能力 ↑
```

但同时可能意味着：

```text
显存 ↑
计算量 ↑
Checkpoint ↑
训练风险 ↑
过拟合风险 ↑
遗忘原能力风险 ↑
实验成本 ↑
```

所以：

\[
\boxed{
MoreTrainableParameters
\neq
AutomaticallyBetterModel
}
\]

真正目标是：

> **用足够的参数容量完成任务，而不是把能训练的全训练一遍。**

---

## 心智模型 5：微调方法选择，本质是“能力变化幅度 × 数据量 × 算力 × 风险”的联合决策

不能只问：

> “LoRA 和 Full FT 哪个更强？”

应该问：

```text
我要改变多少能力？
        ×
有多少高质量数据？
        ×
有多少GPU资源？
        ×
能承受多少训练风险？
        ×
需要多快迭代？
```

这才是：

# Fine-Tuning Strategy

---

# 三、先把“参数”重新放回 Transformer

第二课我们已经见过 Transformer 内部大量矩阵：

```text
Attention

Wq
Wk
Wv
Wo

+

MLP

W_up
W_gate
W_down

+

Embedding
LayerNorm
LM Head
...
```

所有这些矩阵里的数字：

> 都是参数。

例如一个线性层：

\[
y = Wx
\]

这里：

\[
W
\]

就是一组模型参数。

---

# 四、Full Fine-Tuning 到底是什么意思？

# Full Fine-Tuning
## 全参数微调

简单理解：

> Base Model 绝大部分甚至全部可训练参数都允许接收 Gradient 并被 Optimizer 更新。

流程：

```text
Base Model
        ↓
Forward
        ↓
Loss
        ↓
Backward
        ↓
几乎所有权重获得Gradient
        ↓
Optimizer
        ↓
大量Base Weight被修改
```

也就是说：

> 你真的在重新塑造整个模型。

---

# 五、例如一个极简模型

假设只有：

```text
Wq
Wk
Wv
Wo
MLP
Embedding
LM Head
```

Full Fine-Tuning：

```text
Wq          ✓ update
Wk          ✓ update
Wv          ✓ update
Wo          ✓ update
MLP         ✓ update
Embedding   ✓ update
LM Head     ✓ update
```

真实 LLM 当然是：

> 数十亿这样的参数。

---

# 六、Full Fine-Tuning 最大的优势是什么？

一句话：

> **自由度最大。**

模型几乎所有参数都可以重新调整。

如果领域变化非常大，数据极其充足，而且有足够算力：

> Full Fine-Tuning 可以提供非常高的适配容量。

例如一个模型需要进行：

```text
大规模语言迁移
巨大领域分布变化
大量专业语料行为重构
```

全参数训练可能有价值。

---

# 七、但它为什么贵？

这里要分清三个不同东西：

```text
Model Weights
模型权重

Gradients
梯度

Optimizer States
优化器状态
```

Full Fine-Tuning 时：

> 大量权重都需要训练。

所以不仅要保存模型本身，

还要保存：

```text
Gradient
+
Optimizer State
```

这会显著增加显存需求。

---

# 八、只看模型权重大小是不够的

假设：

```text
7B Parameters
```

使用：

```text
BF16
≈
2 bytes / parameter
```

仅模型权重大约就是：

\[
7\times10^9 \times 2
\approx14GB
\]

但训练绝不是：

> “我有 14GB 显存，所以 7B 一定能 Full Fine-Tune。”

因为还需要：

```text
Activation
Gradient
Optimizer State
临时Tensor
CUDA开销
```

所以：

\[
\boxed{
InferenceMemory
\neq
TrainingMemory
}
\]

这是后面显存课程还会详细算的一句话。

---

# 九、Full Fine-Tuning 还有一个风险：原能力也在移动

假设 Base Model 原本已经会：

```text
中文理解
数学
通用推理
摘要
写作
代码
```

现在你拿一批相对狭窄的：

```text
政府采购风险数据
```

让整个模型大量更新。

可能得到：

```text
政府采购能力 ↑
```

但如果训练控制不好，也可能：

```text
通用能力 ↓
```

这类问题通常与：

# Catastrophic Forgetting
## 灾难性遗忘

相关。

---

# 十、不要把“灾难性遗忘”理解成模型突然失忆

更准确的理解是：

> 新训练数据反复推动大量参数朝一个狭窄分布移动，使旧任务所依赖的参数结构受到破坏。

比如：

```text
原模型

通用中文
数学
常识
政府采购
法律文本
写作
      │
      ▼
大量狭窄领域Gradient
      │
      ▼
整个参数空间持续移动
```

结果：

> 部分旧能力退化。

---

# 十一、这并不是说 Full Fine-Tuning 不好

关键是：

> **它的自由度很高，因此能力强，风险也高。**

可以记成：

```text
Full Fine-Tuning

Adaptation Capacity
高

Compute Cost
高

Memory Cost
高

Checkpoint Size
大

Modification Scope
大

Risk Surface
大
```

---

# 十二、现在进入 PEFT

# PEFT
## Parameter-Efficient Fine-Tuning
## 参数高效微调

核心思想非常简单：

> **Base Model 大量参数冻结，只训练非常少的一部分参数。**

概念上：

```text
Base Model
████████████████████████
Frozen

        +

Trainable Parameters
▓▓
```

Forward：

> 两者一起工作。

Backward：

> 产生训练信号。

Optimizer：

> 主要只更新 `▓▓`。

---

# 十三、“冻结参数”到底是什么意思？

在 PyTorch 心智模型里，大致对应：

```python
parameter.requires_grad = False
```

表示：

> 这个参数不作为常规可训练参数被 Optimizer 更新。

而可训练参数：

```python
parameter.requires_grad = True
```

才参与：

> 训练参数更新链。

所以我们可以定义：

\[
N_{\text{trainable}}
\]

表示：

> 可训练参数数量。

---

# 十四、一个很重要的指标：Trainable Parameter Ratio

定义：

\[
TrainableRatio
=
\frac{N_{\text{trainable}}}
{N_{\text{total}}}
\]

假设：

```text
Base Model
=
7,000,000,000
```

可训练参数：

```text
20,000,000
```

那么：

\[
\frac{20M}{7000M}
\approx0.286\%
\]

意味着：

> 整个模型仍然是 7B。

但真正更新：

> 不到 0.3%。

这就是 PEFT 最让人觉得“反直觉”的地方。

---

# 十五、为什么这么少参数还能改变模型行为？

因为我们不是：

> 从零训练语言模型。

Base Model 已经拥有大量能力：

```text
语言理解
Token表示
Attention模式
知识结构
生成能力
推理基础
```

我们只需要：

> **对已有能力进行方向性的调整。**

可以类比：

```text
Base Model
=
已经受过完整教育的专业人员

PEFT
=
给他进行针对性岗位培训
```

不是：

> 重新从小学教一遍。

---

# 十六、对 ProcurementLM，我们到底想改变什么？

第一版真正希望改变的是：

```text
看到采购条款以后
        ↓
更关注专业风险特征
        ↓
更少使用错误Shortcut
        ↓
学会Unknown / needs_review
        ↓
按照稳定结构输出
        ↓
给出更接近专家标注的理由
```

而不是：

```text
重新学习中文
重新学习Transformer
重新学习世界知识
```

所以：

> 这是非常典型的“领域行为适配”问题。

---

# 十七、PEFT 是一个家族，不等于 LoRA

这个概念必须精准。

# PEFT

是一个大类。

其中可以有：

```text
Adapters

Prompt Tuning

Prefix Tuning

LoRA

其他参数高效方法
```

所以：

\[
\boxed{
LoRA
\subset
PEFT
}
\]

LoRA 是：

> PEFT 中最重要、最常见的一类方法之一。

下一阶段才真正拆 LoRA 数学。

---

# 十八、为什么我们的课程重点选择 LoRA / QLoRA？

因为它们在实际 LLM 领域适配里非常实用。

可以同时获得：

```text
较少可训练参数
+
较低训练显存
+
较小Adapter文件
+
较快实验迭代
+
容易保留多个领域版本
```

特别适合我们这种：

> 需要不断实验、评测、修正政府采购行为的项目。

---

# 十九、PEFT 还有一个非常大的工程优势：一个 Base Model 可以挂多个 Adapter

想象：

```text
Base Model
Qwen / Llama / 其他模型
       │
       ├── Procurement Adapter V0.1
       │
       ├── Procurement Adapter V0.2
       │
       ├── Contract Review Adapter
       │
       └── Evaluation Experiment Adapter
```

如果每一次实验都是 Full Fine-Tuning：

> 每次都可能得到一个完整几十 GB 的模型副本。

如果是 PEFT：

> 很多情况下只需要保存小得多的 Adapter。

---

# 二十、这对版本治理非常重要

例如：

```text
Base Model
=
BASE-001
```

上面有：

```text
Adapter A
=
ProcurementLM_V0.1

Adapter B
=
ProcurementLM_V0.1-hardcase

Adapter C
=
ProcurementLM_V0.1-schema2
```

我们可以快速比较：

```text
A vs B vs C
```

而不必复制很多完整 Base Model。

这和第四课 Dataset Versioning：

> 是同一种工程思想。

---

# 二十一、但是 Adapter 不是完整模型

这是非常重要的边界。

如果只保存：

```text
LoRA Adapter
```

通常不能脱离：

```text
Compatible Base Model
```

独立工作。

逻辑是：

```text
Base Model
+
Adapter
=
Fine-tuned Behavior
```

所以：

\[
\boxed{
Adapter
\neq
StandaloneBaseModel
}
\]

除非后面：

> Merge 成完整权重。

这会在后面专门讲。

---

# 二十二、因此必须记录 Base Model Identity

一个 Adapter 最低限度必须知道：

```text
base_model_name

base_model_revision

tokenizer_version

chat_template

adapter_config
```

否则：

> 以后可能连 Adapter 应该挂在哪个 Base Model 上都说不清。

这也是为什么：

# Reproducibility

从 Dataset 一直延伸到 Model。

---

# 二十三、现在比较 Full FT 与 PEFT

| 维度 | Full Fine-Tuning | PEFT |
|---|---|---|
| Base 参数 | 大量更新 | 大量冻结 |
| Trainable 参数 | 很多 | 很少 |
| 训练显存 | 高 | 通常更低 |
| Optimizer State | 大 | 小很多 |
| Checkpoint | 大 | 通常小 |
| 实验迭代 | 较重 | 较快 |
| 参数自由度 | 高 | 较低 |
| 原模型扰动范围 | 大 | 较小 |
| 多 Adapter 管理 | 不自然 | 很适合 |
| 第一版领域适配 | 成本较高 | 常很合适 |

这里没有：

> 谁永远优于谁。

而是：

> **适合不同条件。**

---

# 二十四、什么时候更可能考虑 Full Fine-Tuning？

可以先用四个条件判断。

如果：

```text
1
拥有大量高质量领域训练数据

2
任务与Base Model原分布差异非常大

3
拥有足够GPU与训练工程能力

4
评测证明PEFT容量明显不足
```

那么：

> Full Fine-Tuning 的价值开始上升。

---

# 二十五、什么时候 PEFT 特别合理？

如果：

```text
高质量数据有限
        +
模型本身已经很强
        +
主要做领域行为适配
        +
GPU资源有限
        +
需要快速实验
```

那么：

# PEFT

通常非常有吸引力。

这正好很符合：

> `ProcurementLM_V0.1` 的第一版目标。

---

# 二十六、为什么“数据有限”时 Full FT 反而可能更危险？

因为你给模型：

```text
很大的可训练自由度
```

却只有：

```text
很少的数据约束
```

模型可能非常容易：

> 把训练集学得很好。

但泛化：

> 未必好。

这和统计学习里一直存在的问题一样：

\[
Capacity
\uparrow
\]

而数据量不足时，

可能：

\[
OverfittingRisk
\uparrow
\]

---

# 二十七、这并不意味着 PEFT 自动不会过拟合

注意这句话。

LoRA 一样可以：

```text
过拟合
记住训练表达
学习错误Shortcut
学到Label噪声
```

所以：

\[
\boxed{
PEFT
\neq
AntiOverfittingMagic
}
\]

它只是：

> 限制了可训练参数空间。

并没有取消：

```text
Validation
Hard Case
Benchmark
```

的重要性。

---

# 二十八、PEFT 也不会自动解决错误数据

第四课的一条原则仍然成立：

```text
Garbage Data
      ↓
Garbage Gradient
      ↓
Garbage Adapter
```

LoRA 不是：

> 自动纠错器。

所以我们前面为什么花整整一课做 Dataset？

答案就在这里。

---

# 二十九、PEFT 最大的价值可以用一句话概括

> **尽可能复用 Base Model 已经拥有的能力，只训练完成新任务所必需的最小参数增量。**

数学上可以先抽象成：

\[
W'
=
W
+
\Delta W
\]

其中：

\[
W
\]

代表：

> Base Model 已经学好的权重。

我们尽量不直接大范围改它。

而学习：

\[
\Delta W
\]

也就是：

> 为政府采购任务增加的“变化量”。

---

# 三十、这已经开始靠近 LoRA 的核心了

注意：

今天我们只先建立：

\[
W'
=
W+\Delta W
\]

这个心智模型。

Full FT：

> 直接让 \(W\) 本身大量更新。

LoRA：

> 试图用一种非常高效的方法表示和学习 \(\Delta W\)。

下一阶段真正的关键问题就是：

> **为什么这个 \(\Delta W\) 可以近似成两个很小的低秩矩阵？**

---

# 三十一、先用一张图把区别锁死

```text
Full Fine-Tuning

        Base Model
┌─────────────────────────┐
│ W1  ✓                   │
│ W2  ✓                   │
│ W3  ✓                   │
│ W4  ✓                   │
│ W5  ✓                   │
└─────────────────────────┘
          │
          ▼
大量Base Weight更新
```

而 PEFT：

```text
PEFT

        Base Model
┌─────────────────────────┐
│ W1  Frozen              │
│ W2  Frozen       + ΔW ✓ │
│ W3  Frozen       + ΔW ✓ │
│ W4  Frozen              │
│ W5  Frozen       + ΔW ✓ │
└─────────────────────────┘
          │
          ▼
主要只学习小规模增量参数
```

这就是今天最核心的区别。

---

# 三十二、为什么这会显著减少 Optimizer Memory？

因为 Optimizer 主要需要为：

> Trainable Parameters

维护训练状态。

如果从：

```text
7B Trainable
```

变成：

```text
20M Trainable
```

Optimizer 需要维护的状态规模：

> 会大幅降低。

这正是 PEFT 在训练资源上的关键价值之一。

---

# 三十三、但是 Activation 不会凭空消失

这是个非常容易过度宣传 PEFT 的地方。

即使只有少量参数可训练：

```text
整个Transformer
```

Forward 仍然要跑。

而训练时为了 Backward：

> 仍然需要处理大量中间 Activation。

所以：

\[
\boxed{
PEFT
大幅减少参数相关训练成本
}
\]

但不等于：

\[
\boxed{
所有显存成本都消失
}
\]

后面 QLoRA、Gradient Checkpointing 等技术：

> 还会继续处理剩下的内存问题。

---

# 三十四、所以训练显存可以先粗分成四块

```text
1. Model Weights
模型权重

2. Trainable Gradients
梯度

3. Optimizer States
优化器状态

4. Activations
中间激活
```

Full FT：

> 2、3 都非常大。

PEFT：

> 2、3 可以显著缩小。

但：

> 1 和 4 仍然必须认真处理。

这是非常精准的显存心智模型。

---

# 三十五、QLoRA 为什么会继续出现？

因为 LoRA 解决的是：

> **哪些参数训练。**

但 Base Model 权重本身：

> 仍需要放进显存。

QLoRA 后面会进一步问：

> 能不能把冻结的 Base Model 用 4-bit 形式加载，同时仍然训练高精度 LoRA Adapter？

于是：

```text
LoRA
解决
Trainable Parameter Cost

QLoRA
进一步解决
Frozen Base Weight Memory
```

先记这层关系即可。

---

# 三十六、Full FT、LoRA、QLoRA 的大地图

```text
                 Fine-Tuning
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
 Full Fine-Tuning               PEFT
 大量Base参数更新                 │
                                  ▼
                                LoRA
                      冻结Base + 训练低秩Adapter
                                  │
                                  ▼
                               QLoRA
                      量化冻结Base + 训练LoRA
```

后面三个阶段会沿着：

```text
PEFT
↓
LoRA
↓
QLoRA
```

逐层往下拆。

---

# 三十七、ProcurementLM_V0.1 应该先选什么？

基于我们目前的课程目标，第一版优先建立：

# PEFT / LoRA Baseline

原因不是：

> Full FT 一定差。

而是第一版需要优先获得：

```text
低实验成本
+
快速迭代
+
容易回滚
+
方便比较Adapter
+
较小Checkpoint
+
保留强Base Model能力
```

然后：

> 用 Benchmark 数据决定是否需要更大的训练自由度。

这比：

> 一上来直接训练全部参数

更容易形成可靠实验闭环。

---

# 三十八、决策顺序不要反过来

错误：

```text
我听说LoRA很流行
        ↓
所以一定用LoRA
```

更好的决策：

```text
Task Gap
任务差距有多大？
        ↓
Data Scale
高质量数据有多少？
        ↓
Base Model Capability
底模已经会多少？
        ↓
Resource Budget
资源允许多少？
        ↓
Benchmark Result
PEFT够不够？
        ↓
Fine-Tuning Strategy
```

也就是说：

> **技术选择必须由问题决定。**

---

# 三十九、给政府采购项目一个非常实用的升级梯子

第一层：

```text
Base Model
```

先测。

如果不够：

```text
↓
```

第二层：

```text
Prompt / RAG
```

先解决知识和上下文问题。

如果仍存在稳定行为缺陷：

```text
↓
```

第三层：

```text
PEFT / LoRA
```

改变模型行为。

如果有证据证明：

```text
LoRA容量不足
+
数据足够
+
收益值得成本
```

再考虑：

```text
↓
Full Fine-Tuning
```

这比一开始就：

> “训练越多越高级”

专业得多。

---

# 四十、这里还要区分“知识问题”和“行为问题”

假设模型不知道：

> 某个刚发布的政府采购规定。

这往往是：

# Knowledge Freshness Problem

可能更适合：

> RAG。

---

但如果模型已经拿到了正确法规，却仍然：

```text
不会按我们的Schema输出
总是过度下结论
不会在证据不足时abstain
总把关键词直接等同风险
```

这些更像：

# Behavior Adaptation Problem

这才是：

> SFT / PEFT

擅长解决的方向。

这条边界极其重要。

---

# 四十一、所以 SFT 不应该承担所有事情

我们最终 ProcurementAI 会形成：

```text
Base Model
        │
        ├── SFT / LoRA
        │   学行为
        │
        ├── RAG
        │   给最新知识和证据
        │
        └── Rules
            做硬约束
```

不同组件：

> 各自干最适合自己的工作。

这也是后面整个系统设计的基础。

---

# 四十二、本阶段工程产物：`FineTuningStrategy_V0.1`

我们现在应该能够正式记录：

```text
base_model
base_model_revision

adaptation_goal

full_finetuning_enabled
peft_method

total_parameters
trainable_parameters
trainable_ratio

frozen_parameter_scope
trainable_parameter_scope

expected_checkpoint_type

memory_budget

evaluation_baseline

upgrade_condition
```

其中：

# `upgrade_condition`

很重要。

例如：

> 只有当 LoRA 在固定 Benchmark 上持续表现出明确容量瓶颈，并排除数据和超参数问题后，才进入 Full Fine-Tuning 评估。

这样：

> 技术升级就不是拍脑袋。

---

# 四十三、本阶段最危险的几个反例

**反例 1：认为模型 7B，就必须训练 7B 参数。**  
模型规模和可训练参数量不是一回事。

**反例 2：认为 PEFT 就没有使用完整 Base Model。**  
整个 Base Model 仍然参与 Forward。

**反例 3：认为 Full FT 参数多，所以一定效果最好。**  
数据、任务、泛化和训练稳定性共同决定结果。

**反例 4：认为 LoRA 自动防止过拟合。**  
错误数据和过度训练仍然会得到坏 Adapter。

**反例 5：只保存 Adapter，却不记录 Base Model Revision。**  
以后模型不可可靠复现。

**反例 6：知识过时也用 SFT 硬记。**  
知识更新问题往往应该优先考虑 RAG。

**反例 7：模型行为问题只靠 Prompt 无限堆规则。**  
稳定行为差异可能需要 SFT。

---

# 四十四、现在把本阶段压缩成最精准的 5 句话

如果一周后只记住这五句：

> **第一，使用整个模型不等于训练整个模型；PEFT 仍然使用完整 Base Model，只是大多数权重被冻结。**

> **第二，Full Fine-Tuning 与 PEFT 的本质区别，是 Gradient 最终允许改写多少模型参数。**

> **第三，PEFT 不是“廉价版训练”，而是尽可能复用 Base Model 已有能力，只学习任务所需要的最小参数增量。**

> **第四，可训练参数越多不代表效果一定越好；参数自由度必须与高质量数据、算力、泛化风险和能力变化幅度匹配。**

> **第五，对 `ProcurementLM_V0.1`，先建立 PEFT / LoRA Baseline，再通过固定 Benchmark 决定是否值得升级到更重的 Full Fine-Tuning。**

这就是本阶段的精华。

---

# 四十五、本阶段最核心的一张图

```text
                   Base Model
              已有通用模型能力
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼

Full Fine-Tuning                PEFT
        │                         │
大量Base Weight                 大量Base Weight
Trainable                       Frozen
        │                         │
        │                         + 少量Trainable Params
        │                         │
        ▼                         ▼
大量参数更新                  小规模参数增量
        │                         │
        ▼                         ▼
高训练成本                    较低训练成本
大Checkpoint                   小Adapter
大修改范围                     小修改范围
        │                         │
        └────────────┬────────────┘
                     ▼
                  Benchmark
                     │
                     ▼
            哪个满足真实任务需求？
```

脑中只留一句：

> **先决定“改多少参数”，再决定“具体怎样改”。**

---

# 四十六、本阶段掌握测试

现在不回看正文，你应该能够自己解释：为什么一个 7B 模型不等于必须训练 70 亿参数；Full Fine-Tuning 到底更新什么；Frozen Parameter 和 Trainable Parameter 有什么区别；为什么 Base Model 冻结以后仍然参与 Forward；为什么 Training Memory 明显高于 Inference Memory；为什么 Full FT 不只需要模型权重，还需要大量 Gradient 和 Optimizer State；什么是 Catastrophic Forgetting；为什么更多 Trainable Parameters 不等于更高业务效果；PEFT 的全称和本质是什么；为什么 LoRA 属于 PEFT 而 PEFT 不等于 LoRA；什么是 Trainable Parameter Ratio；为什么少量参数仍然能够改变已有大模型行为；Adapter 为什么通常离不开对应 Base Model；为什么必须记录 Base Model Revision；PEFT 主要减少显存中的哪几类开销；为什么 Activation 并不会因为 LoRA 自动消失；为什么 QLoRA 会进一步处理冻结 Base Weight 的显存；什么情况下 Full Fine-Tuning 的价值会上升；什么情况下 PEFT 更合理；以及为什么政府采购“最新法规知识”与“风险判断行为”应该分别考虑 RAG 和 SFT。

如果这些能够自己解释：

\[
\boxed{
第五课第5阶段真正掌握
}
\]

---

# 本阶段最后只记一句话

> **Full Fine-Tuning 是让大范围 Base Model 权重直接接受 Gradient 并被改写，而 PEFT 是尽量冻结已经学好的大模型，只训练完成目标任务所需要的一小部分参数增量；对于第一版 `ProcurementLM_V0.1`，专业的策略不是默认“训练越多越好”，而是先用最小必要参数变化建立可靠 Baseline，再让 Benchmark 决定是否需要更大的训练自由度。**

---

# 下一阶段：第五课 · 第 6 阶段
# LoRA 到底在改什么？
## 为什么两个很小的矩阵，就能够改变一个几十亿参数模型的行为？

今天我们停在了：

\[
W' = W + \Delta W
\]

下一阶段将真正打开 LoRA 的核心：

\[
\boxed{
\Delta W = BA
}
\]

我们只需要解决一个问题：

> **为什么一个巨大的权重矩阵不直接训练，而是可以用两个很小的低秩矩阵去表达它需要发生的变化？**

一旦这件事真正想通，后面的 `rank`、`alpha`、`target_modules`、QLoRA 才会从“配置参数”变成你能自己判断的工程变量。

---
