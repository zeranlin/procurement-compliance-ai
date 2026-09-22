# 第五课 · 第 2 阶段
# SFT 到底在训练什么？
## 一次 SFT Step 里，专家答案究竟怎样变成参数更新？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，SFT 仍然是在做 Next Token Prediction，只是正确答案来自我们的专家数据。**
2. **第二，Forward 负责产生预测，Cross Entropy 把预测和正确 Token 比较后得到 Loss。**
3. **第三，Loss 只告诉模型“错多少”，Backward 才通过链式法则计算每个可训练参数应该往哪个方向调整。**
4. **第四，loss.backward() 负责计算 Gradient，optimizer.step() 才真正更新参数。**
5. **第五，SFT 的最终效果，是大量小的参数更新不断重塑 P(Response | Prompt)；训练 Loss 下降并不等于真实业务能力一定提升。**
6. **优化目标正在改善。**
7. **Business Quality ↑**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Token` | Token：模型实际处理的离散文本单元 |
| `Step` | 训练步：通常指一次优化器更新 |
| `SFT` | 监督微调：用监督样本继续更新模型参数 |
| `Loss` | 损失函数：把预测错误压缩成可优化的数值信号 |
| `Gradient` | 梯度：损失对参数变化方向和敏感度的局部信息 |
| `Optimizer` | 优化器：依据梯度规则更新参数 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |
| `LoRA` | LoRA：冻结大部分基座参数，只训练低秩增量矩阵 |
| `Response` | 目标响应：希望模型学习生成的答案部分 |
| `Input` | 输入：模型在当前任务中允许看到的条件信息 |
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `Transformer` | Transformer：以注意力和前馈网络为核心的序列架构 |

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

第 1 阶段我们已经解决了一个非常关键的问题：

> **哪些 Token 应该学？**

我们建立了这条链：

```text
Messages
   ↓
Chat Template
   ↓
Tokenizer
   ↓
input_ids
   ↓
labels
   ↓
Loss Mask
```

也就是说，我们已经能告诉训练系统：

```text
Prompt
=
给模型看的条件

Assistant Response
=
主要学习目标
```

但还有一个更深的问题。

假设专家答案是：

> “该条款存在潜在供应商资格风险。”

Base Model 却更倾向于回答：

> “该条款不存在明显风险。”

这两个答案之间的差异：

> **究竟怎样从一串文字，变成一次真实的参数更新？**

今天只解决这一件事。

最终你需要在脑中形成：

# `SFTTrainingStep_V0.1`

---

# 一、本阶段只解决一个核心问题

> **一个 Assistant Token 预测错误以后，Loss 怎样产生，Gradient 怎样反向传播，Optimizer 又怎样最终改变模型参数？**

整阶段只有这一条主线：

```text
正确答案 Token
      │
      ▼
Forward
前向计算
      │
      ▼
Logits
每个候选 Token 的原始分数
      │
      ▼
Probability
转成概率
      │
      ▼
Cross Entropy
和正确答案比较
      │
      ▼
Loss
预测错误有多严重
      │
      ▼
Backward
反向传播
      │
      ▼
Gradient
参数应该往哪个方向改
      │
      ▼
Optimizer
真正执行参数更新
      │
      ▼
下一次更容易预测正确答案
```

中文压缩成：

> **先预测 → 再比较 → 算错多少 → 找谁负责 → 改一点参数。**

这就是一次 SFT Step 的本质。

---

# 二、先锁死本阶段 5 个核心心智模型

今天真正需要长期记住的只有五句话。

## 心智模型 1：SFT 本质仍然是 Next Token Prediction

SFT 并没有给 Transformer 安装一个新的“问答模块”。

它仍然只干一件事：

> **根据前面的 Token，预测下一个 Token。**

所以：

\[
\boxed{
SFT
=
受监督的 Next Token Prediction
}
\]

所谓“监督”，就是：

> 我们已经知道这个位置正确的下一个 Token 应该是什么。

---

## 心智模型 2：Forward 负责“做答案”，Loss 负责“判多少分”

Forward：

> 模型根据当前参数做一次预测。

Loss：

> 拿预测结果和专家答案比较。

所以：

```text
Forward
=
当前模型会怎么答？

Loss
=
这个回答离专家答案有多远？
```

这两个角色必须分开。

---

## 心智模型 3：Gradient 不是“错误大小”，而是“参数应该往哪边改”

Loss 只告诉我们：

> 错得多不多。

Gradient 才告诉我们：

> **每个可训练参数应该增一点还是减一点。**

所以：

\[
\boxed{
Loss
\neq
Gradient
}
\]

更准确地说：

```text
Loss
告诉你：
总体犯错程度

Gradient
告诉你：
每个参数该怎么动
```

---

## 心智模型 4：Backward 计算修改建议，Optimizer 才真正改参数

这是非常容易混淆的一对。

```text
loss.backward()
```

主要负责：

> 算 Gradient。

而：

```text
optimizer.step()
```

才负责：

> 真正更新参数。

所以：

\[
\boxed{
Backward
\neq
ParameterUpdate
}
\]

正确顺序是：

```text
Backward
↓
得到 Gradient
↓
Optimizer Step
↓
参数变化
```

---

## 心智模型 5：LoRA 训练时，Base Model 负责计算，但主要不被更新

以后我们会正式讲 LoRA。

今天先建立一个准确心智模型：

```text
Base Model
大量参数
被冻结
      │
      │ 仍参与 Forward
      │ 仍传递计算信号
      ▼
LoRA Parameters
少量可训练参数
      │
      ▼
接收 Gradient
      │
      ▼
Optimizer 更新
```

所以：

> **冻结 ≠ 不参与计算。**

更准确地说：

> Base Model 仍然参与 Forward 和反向信号传播，但被冻结的权重本身不由 Optimizer 更新。

这句话后面非常重要。

---

# 三、现在从一个真实采购案例开始

我们的 Prompt：

```text
User:

请判断以下采购条款是否存在潜在风险：

“投标人须在本市设立固定服务机构方可参与投标。”
```

专家 Response：

```text
Assistant:

风险判断：存在潜在风险。
风险类型：供应商资格条件。
```

经过第 1 阶段以后，我们已经得到：

```text
Prompt Tokens
→ 不计算主要 Loss

Assistant Tokens
→ 计算 Loss
```

假设现在模型正在学习 Assistant 的第一个答案 Token：

```text
“存在”
```

---

# 四、第一步：Forward Pass

# Forward Pass
## 前向传播 / 前向计算

模型拿到：

```text
Prompt
+
前面已经提供的正确 Token
```

然后经过：

```text
Embedding
   ↓
Transformer Layers
   ↓
Attention
   ↓
MLP
   ↓
Final Hidden State
   ↓
LM Head
```

最后输出：

# Logits

---

# 五、Logits 到底是什么？

假设词表只有五个候选 Token：

```text
存在
不存在
需要
符合
无法
```

模型输出：

| Token | Logit |
|---|---:|
| 存在 | 1.2 |
| 不存在 | 2.8 |
| 需要 | 0.9 |
| 符合 | 0.4 |
| 无法 | 0.1 |

Logit 可以简单理解成：

> **模型对每个候选 Token 的原始打分。**

注意：

它还不是概率。

因为：

```text
2.8
```

不是：

> 280%。

---

# 六、Logits 是模型“当前偏好”的原始形态

这里正确答案其实是：

```text
存在
```

但当前最大 Logit 是：

```text
不存在
```

这说明：

> 当前模型更偏向错误答案。

也就是说：

```text
Base Model当前参数
        ↓
认为“不存在”
比“存在”
更可能
```

这正是我们需要通过训练纠正的地方。

---

# 七、第二步：Softmax

Softmax 负责：

> 把所有 Logit 转换成一个概率分布。

可以把它理解成：

```text
Logits
原始分数
   ↓
Softmax
   ↓
Probabilities
候选Token概率
```

公式知道意思就够：

\[
P_i
=
\frac{e^{z_i}}
{\sum_j e^{z_j}}
\]

其中：

- \(z_i\)：某个 Token 的 Logit；
- \(P_i\)：转换后的概率。

---

# 八、假设转换以后得到

| Token | Probability |
|---|---:|
| 存在 | 0.14 |
| 不存在 | 0.70 |
| 需要 | 0.09 |
| 符合 | 0.05 |
| 无法 | 0.02 |

专家正确答案：

```text
存在
```

但是模型只给：

```text
14%
```

而给错误答案：

```text
不存在
=
70%
```

这时候：

> 必须产生一个比较大的惩罚。

---

# 九、第三步：Cross Entropy

# Cross Entropy
## 交叉熵损失

不用先记复杂定义。

在当前场景里，它最重要的作用就是：

> **看模型给正确 Token 分配了多大概率。**

如果正确 Token 概率：

```text
0.95
```

Loss：

> 很小。

如果正确 Token 概率：

```text
0.14
```

Loss：

> 很大。

---

# 十、最重要的公式只有这个

对于一个正确 Token：

\[
L
=
-\log P(\text{正确 Token})
\]

例如：

正确答案概率：

\[
P=0.9
\]

那么 Loss 比较小。

如果：

\[
P=0.01
\]

Loss：

> 非常大。

所以：

\[
\boxed{
正确答案概率越高
\Rightarrow
Loss越低
}
\]

---

# 十一、这就是 Loss 最精准的心智模型

Loss 不是：

> “模型有没有答对”的 0 / 1 开关。

它表示：

> **模型对正确答案究竟有多不自信。**

例如两个模型都预测错了。

模型 A：

```text
正确Token概率
=
40%
```

模型 B：

```text
正确Token概率
=
0.01%
```

虽然都错：

> B 错得更加坚定。

所以 B：

> Loss 更大。

---

# 十二、完整 Response 不是只有一个 Token

假设专家答案经过 Tokenizer 后大致是：

```text
存在
潜在
供应商
资格
风险
EOS
```

模型要分别学习：

```text
Prompt
→ 存在

Prompt + 存在
→ 潜在

Prompt + 存在 + 潜在
→ 供应商

...

Prompt + 完整答案
→ EOS
```

每一个位置：

> 都可能产生一个 Token Loss。

---

# 十三、然后把这些有效位置的 Loss 汇总

概念上：

\[
L
=
\frac{1}{N}
\sum_{t \in A} L_t
\]

其中：

- \(A\)：参与 Loss 的 Assistant Token；
- \(N\)：有效目标 Token 数量。

不用背。

真正要记的是：

> **一次训练样本的 Loss，是很多 Assistant Token 预测误差的综合。**

---

# 十四、Loss Mask 在这里再次出现

第 1 阶段我们已经知道：

```text
Prompt Token
label = -100

Response Token
label = Token ID
```

所以 Loss 计算时：

```text
System
忽略

User
忽略

Assistant
参与
```

这意味着：

> 第 2 阶段所有 Cross Entropy，实际上只作用在第 1 阶段挑出来的有效 Token 上。

所以两阶段关系是：

```text
第1阶段
决定哪里算Loss
      ↓
第2阶段
决定Loss怎样改变参数
```

---

# 十五、到这里 Forward 结束了

现在我们已经拥有一个数。

例如：

```text
Loss = 2.37
```

但注意：

> **参数现在还一丁点都没变。**

这是极其重要的一点。

当前只是：

```text
模型做了一次预测
      +
我们算出了它错多少
```

还没有学习。

---

# 十六、那模型什么时候真正开始“学习”？

接下来：

# Backward Pass
## 反向传播

---

# 十七、Backward 在问什么？

Forward 问：

> 当前参数给出什么结果？

Backward 问：

> **如果希望 Loss 下降，每个可训练参数应该往哪个方向动？**

这是完全不同的问题。

---

# 十八、举一个极简例子

假设模型只有一个参数：

\[
w
\]

当前：

```text
w = 2.0
```

Loss：

```text
L = 3.0
```

我们想知道：

> 如果把 \(w\) 稍微增加一点，Loss 会增加还是下降？

这就是：

\[
\frac{\partial L}{\partial w}
\]

---

# 十九、Gradient 最简单怎么理解？

# Gradient
## 梯度

例如：

\[
\frac{\partial L}{\partial w}
=
+0.8
\]

可以粗略理解：

> 往正方向增加 \(w\)，Loss 会升高。

那么为了降低 Loss：

> 我们应该让 \(w\) 往负方向走一点。

---

如果：

\[
\frac{\partial L}{\partial w}
=
-0.8
\]

则意味着：

> 增加 \(w\) 有助于降低 Loss。

---

# 二十、所以 Gradient 同时包含两类信息

### 方向

```text
+
或
-
```

告诉：

> 参数往哪边移动。

### 大小

例如：

```text
0.001
```

和：

```text
12.5
```

代表：

> Loss 对这个参数的敏感程度不同。

所以：

\[
\boxed{
Gradient
=
Direction
+
Sensitivity
}
\]

---

# 二十一、Backward 为什么叫“反向”？

因为计算方向和 Forward 大致相反。

Forward：

```text
Parameters
   ↓
Transformer
   ↓
Logits
   ↓
Loss
```

Backward：

```text
Loss
   ↓
Logits
   ↓
Transformer
   ↓
Parameters
```

它从最终 Loss 出发：

> 一层层往回计算责任。

---

# 二十二、可以把 Backpropagation 想成“追责系统”

假设一个采购审核结果错了。

管理者不能只说：

> “最终答案错了。”

还要往回查：

```text
最终判断错
   ↓
风险类型判断出了问题
   ↓
某个特征权重过高
   ↓
某层表示产生偏差
   ↓
哪些参数应该调整
```

Backpropagation：

> 就是在数学上做类似的责任传递。

---

# 二十三、这里真正依赖的是 Chain Rule

# Chain Rule
## 链式法则

假设：

\[
w
\rightarrow
h
\rightarrow
z
\rightarrow
L
\]

我们想知道：

\[
w
\]

对最终：

\[
L
\]

的影响。

通过链式法则：

\[
\frac{\partial L}{\partial w}
=
\frac{\partial L}{\partial z}
\cdot
\frac{\partial z}{\partial h}
\cdot
\frac{\partial h}{\partial w}
\]

不用计算。

只记：

> **最终错误可以沿着计算链，一层一层传回早期参数。**

---

# 二十四、这就是为什么第二课学 Backpropagation 很重要

第二课我们是在神经网络角度理解：

```text
Forward
↓
Loss
↓
Backward
```

第五课现在把它真正接到：

# LLM SFT

整个 Transformer 虽然有几十亿参数，

本质仍然遵循：

```text
Forward
↓
Compare
↓
Backward
↓
Update
```

没有神秘的新机制。

---

# 二十五、Backward 结束以后发生了什么？

现在模型里大量参数拥有：

```text
.grad
```

概念上：

```text
parameter_1.grad
parameter_2.grad
parameter_3.grad
...
```

这些 Gradient：

> 已经算出来。

但是注意第二次：

> **参数依然还没有真正修改。**

---

# 二十六、真正修改参数的是 Optimizer

# Optimizer
## 优化器

例如常见的：

```text
AdamW
```

Optimizer 会读取：

```text
Current Parameters
+
Gradients
```

然后决定：

> 实际移动多少。

---

# 二十七、最简单的 Gradient Descent

最基本公式：

\[
\theta_{\text{new}}
=
\theta_{\text{old}}
-
\eta
\nabla_\theta L
\]

这里：

- \(\theta\)：参数；
- \(L\)：Loss；
- \(\nabla_\theta L\)：Gradient；
- \(\eta\)：Learning Rate。

真正记住：

> **参数沿着让 Loss 下降的方向移动一小步。**

---

# 二十八、Learning Rate 是什么？

# Learning Rate
## 学习率

就是公式里的：

\[
\eta
\]

可以理解成：

> **每次相信 Gradient 多少。**

如果 Learning Rate 很小：

```text
每次只改一点点
```

如果太大：

```text
一下跳太远
```

---

# 二十九、生活类比：下山

你站在山坡上。

目标：

> 到最低点。

Gradient 告诉：

> 哪边是上坡。

于是你往反方向走。

Learning Rate 决定：

> 一步迈多大。

```text
Gradient
=
方向

Learning Rate
=
步长

Optimizer
=
走路策略
```

这个类比以后一直能用。

---

# 三十、为什么不能 Learning Rate 越大越好？

假设最低点就在前面。

合理步长：

```text
→ → → → 最低点
```

太大：

```text
左边
   ↘
     最低点
           ↗
              右边
```

不断跨过去。

训练可能：

```text
Loss震荡
Loss爆炸
NaN
模型能力破坏
```

所以：

> 梯度方向正确，不代表步子可以无限大。

---

# 三十一、AdamW 比最简单 Gradient Descent 多做了什么？

今天不展开公式。

只需要理解：

AdamW 不只是看：

```text
当前一次Gradient
```

它还会维护一些历史统计，

大致帮助它判断：

```text
这个方向是不是一直稳定？
这个参数最近梯度大不大？
不同参数应该走多大的步？
```

所以它是一种：

> 更聪明的更新规则。

---

# 三十二、到这里一次真正的参数更新终于发生了

完整过程：

```text
optimizer.zero_grad()
        ↓
Forward
        ↓
Loss
        ↓
loss.backward()
        ↓
Gradient
        ↓
optimizer.step()
        ↓
Parameters Updated
```

这是一个极其重要的训练骨架。

---

# 三十三、为什么前面还有 `zero_grad()`？

因为在 PyTorch 中：

> Gradient 默认会累加。

如果上一步 Gradient 没清理：

```text
Step 1 Gradient
+
Step 2 Gradient
```

可能会继续叠加。

如果你本来不想做 Gradient Accumulation：

> 就会训练错。

所以普通训练 Step 通常有：

```text
zero_grad
↓
forward
↓
loss
↓
backward
↓
step
```

---

# 三十四、以后我们还会故意“不立刻 zero”

那就是：

# Gradient Accumulation
## 梯度累积

但这是后面的训练工程内容。

今天只需要知道：

> Gradient 可以故意累积，也可以每一步清空。

关键是：

> 必须知道自己在做哪一种。

---

# 三十五、现在进入一个极其重要的概念：Teacher Forcing

# Teacher Forcing
## 教师强制

这个名字看起来复杂。

实际非常简单。

训练时，模型预测第二个 Response Token 时：

> 通常看到的是**真实的第一个专家 Token**。

不是：

> 模型刚才自己预测出来的错误 Token。

---

# 三十六、举例最容易理解

正确答案：

```text
存在 潜在 风险
```

训练时：

### 预测“存在”

Input：

```text
Prompt
```

Target：

```text
存在
```

---

预测“潜在”：

Input：

```text
Prompt + 正确的“存在”
```

Target：

```text
潜在
```

---

预测“风险”：

Input：

```text
Prompt + 正确的“存在 潜在”
```

Target：

```text
风险
```

这就是 Teacher Forcing。

---

# 三十七、训练时和推理时有一个关键区别

训练时：

```text
Prompt
+
专家正确历史答案
→
预测下一个Token
```

推理时：

```text
Prompt
+
模型自己刚生成的Token
→
预测下一个Token
```

所以：

\[
\boxed{
TrainingHistory
\neq
InferenceHistory
}
\]

这是一个很重要的区别。

---

# 三十八、为什么训练可以一次算很多 Token？

虽然我们概念上写：

```text
预测“存在”
再预测“潜在”
再预测“风险”
```

但 Transformer 训练时并不是必须：

> 一个 Token 一个 Token 地串行跑完整模型。

因为有：

# Causal Mask

训练可以在一次 Forward 中并行计算多个位置的预测。

---

# 三十九、这张图非常重要

序列：

```text
Prompt | 存在 | 潜在 | 风险
```

模型在同一次 Forward 中可以得到：

```text
位置 A
预测：存在

位置 B
预测：潜在

位置 C
预测：风险

位置 D
预测：EOS
```

但每个位置：

> 只能看到自己左边允许看到的 Token。

这就是 Causal Language Model。

---

# 四十、Teacher Forcing 和 Loss Mask 不是一回事

这两个特别容易混。

Loss Mask：

> **哪些位置要评分。**

Teacher Forcing：

> **训练时前文使用真实历史 Token。**

所以：

```text
Loss Mask
解决：
“考哪几题？”

Teacher Forcing
解决：
“做后面的题时，前面的正确答案是否给你？”
```

完全不同。

---

# 四十一、现在把第 1、2 阶段真正合起来

```text
Messages
   ↓
Chat Template
   ↓
Tokenizer
   ↓
input_ids
   ↓
Loss Mask
选择Assistant Token
   ↓
Forward
   ↓
Logits
   ↓
Softmax
   ↓
Cross Entropy
   ↓
Loss
   ↓
Backward
   ↓
Gradient
   ↓
Optimizer
   ↓
Parameter Update
```

这就是目前为止：

# SFT 最核心的一整条链

---

# 四十二、现在进入 LoRA 场景

假设 Base Model：

```text
7B Parameters
```

如果做 Full Fine-Tuning：

> 大量模型权重都可以更新。

但是后面我们的 ProcurementLM 很可能采用：

# LoRA / QLoRA

那么情况变成：

```text
Base Model Parameters
requires_grad = False
被冻结

LoRA Parameters
requires_grad = True
可训练
```

---

# 四十三、这里最容易产生一个误解

有人会想：

> Base Model 冻结了，那 Backward 是不是就不经过它？

不是这么理解。

Forward 仍然要经过：

```text
Base Model
```

反向信号也需要沿计算图传播到：

```text
LoRA Parameters
```

只是：

> Base Model 自己被冻结的权重不作为可训练参数被 Optimizer 更新。

---

# 四十四、最精准的图是这样

```text
Input
  │
  ▼
┌────────────────────────────┐
│ Base Model Weight          │
│ Frozen 冻结                │
│                            │
│       +                    │
│                            │
│ LoRA Adapter               │
│ Trainable 可训练           │
└────────────┬───────────────┘
             │
             ▼
           Output
             │
             ▼
            Loss
             │
             ▼
          Backward
             │
             ▼
      LoRA gets Gradient
             │
             ▼
        Optimizer Step
             │
             ▼
        LoRA Updated
```

---

# 四十五、所以“训练 7B 模型”不一定意味着更新 70 亿参数

这就是后面 LoRA 最重要的价值之一。

例如：

```text
Base Model
7,000,000,000 parameters

LoRA Trainable
可能只有几百万或几千万
```

那么：

> 我们依然利用整个 7B 模型做 Forward。

但真正 Optimizer 更新的：

> 只是小部分参数。

---

# 四十六、这也是为什么要区分三种东西

```text
Model Parameters
模型全部参数

Trainable Parameters
允许求训练梯度并优化的参数

Updated Parameters
Optimizer实际更新的参数
```

在简单训练里后两者通常对应。

但理解上：

> 不应该把“整个模型参数量”等同于“实际训练参数量”。

---

# 四十七、政府采购知识究竟“写进哪里”？

这是一个很好的问题。

不是：

> 某条专家规则完整存进某一个神经元。

而是大量训练样本不断产生：

```text
Gradient
```

这些 Gradient：

> 对大量可训练参数做微小调整。

最终使模型的概率分布发生变化。

---

# 四十八、例如训练前

看到：

```text
投标人须在本市设立固定机构方可投标
```

模型可能：

```text
P(存在潜在风险) = 0.25
P(不存在风险)   = 0.60
```

经过很多类似高质量样本训练以后：

```text
P(存在潜在风险) = 0.78
P(不存在风险)   = 0.12
```

这才叫：

> 模型行为改变了。

---

# 四十九、SFT 真正改变的是“条件概率分布”

这是这一阶段最专业、也最值得留下来的理解。

模型在学的是：

\[
P_\theta(
Response
\mid
Prompt
)
\]

SFT 通过更新参数：

\[
\theta
\]

让高质量专家 Response：

> 在给定 Prompt 条件下获得更高概率。

所以：

\[
\boxed{
SFT
=
重塑条件概率分布
}
\]

---

# 五十、不是简单把“知识文本存进去”

这一点要特别清楚。

SFT 不等于数据库：

```text
条款A
→
答案A
```

简单存储。

它试图学习：

> 许多 Prompt 与专业 Response 之间的统计规律和行为模式。

所以我们真正希望学到的是：

```text
看见什么条件
    ↓
关注什么差异
    ↓
采用什么判断方式
    ↓
输出什么结构
```

---

# 五十一、这也是为什么 Hard Case 特别重要

第四课我们专门建设：

```text
Hard Negative
Hard Positive
Boundary Case
```

这些样本产生的 Gradient：

> 正是在修模型最容易出错的决策边界。

例如模型错误认为：

```text
出现“本地”
→
一定Risk
```

Hard Negative：

> 会对这种错误偏好产生反向训练信号。

---

# 五十二、所以第四课的 Hard Case 到第五课真正变成了什么？

变成：

# Gradient Signal
## 梯度信号

第四课时：

```text
Hard Negative
=
高价值困难数据
```

第五课时：

```text
Hard Negative
        ↓
模型预测错
        ↓
较高Loss
        ↓
Gradient
        ↓
参数调整
        ↓
决策边界变化
```

现在前后课程真正接上了。

---

# 五十三、但 Loss 大是不是一定好？

不是。

这是一个很重要的误区。

Loss 很大可能意味着：

### 情况 A

```text
模型真的不会
```

这是有价值的学习信号。

但也可能：

### 情况 B

```text
Label错了
```

### 情况 C

```text
数据格式错了
```

### 情况 D

```text
答案被截断
```

### 情况 E

```text
Loss Mask错位
```

所以：

\[
\boxed{
HighLoss
\neq
AutomaticallyGoodTrainingSignal
}
\]

---

# 五十四、反过来，Loss 很低是不是一定模型很好？

也不是。

可能：

```text
训练样本太容易
```

或者：

```text
重复数据太多
```

甚至：

```text
发生了数据泄漏
```

所以训练 Loss：

> 只是训练过程信号。

不是：

> 最终模型能力证明。

---

# 五十五、这就是为什么第四课的 Validation / Test 必须存在

Training Loss 回答：

> **模型在训练数据上的预测越来越像 Target 了吗？**

Validation 回答：

> **对没参与参数更新的数据，它是否也在变好？**

Test 最终回答：

> **冻结开发决策后，它对真正独立数据表现怎样？**

三个问题完全不同。

---

# 五十六、训练 Loss 下降到底意味着什么？

更精准地说：

> 在当前训练数据、当前 Loss 定义、当前 Mask 规则下，模型给目标 Token 分配的概率整体提高了。

仅此而已。

它不能直接证明：

```text
法律判断更正确
泛化更好
可靠性更高
幻觉更少
```

这些需要：

> 单独评测。

---

# 五十七、这也是第 5 个核心心智模型的延伸

```text
Loss ↓
```

只能说明：

> 优化目标正在改善。

不能直接推出：

```text
Business Quality ↑
```

所以：

\[
\boxed{
OptimizationMetric
\neq
BusinessMetric
}
\]

这句话以后非常重要。

---

# 五十八、现在看一个完整 SFT Step

我们把所有过程压缩成代码逻辑：

```python
optimizer.zero_grad()

outputs = model(
    input_ids=input_ids,
    attention_mask=attention_mask,
    labels=labels
)

loss = outputs.loss

loss.backward()

optimizer.step()
```

这五步看起来非常短。

但你现在应该能看到背后发生的一整套东西。

---

# 五十九、第一行

```python
optimizer.zero_grad()
```

意思：

> 清理上一轮 Gradient。

---

# 六十、第二步 Forward

```python
outputs = model(...)
```

背后：

```text
Token IDs
   ↓
Embedding
   ↓
Transformer
   ↓
Hidden States
   ↓
LM Head
   ↓
Logits
```

如果提供：

```text
labels
```

很多 Causal LM 实现还会顺便计算 Loss。

---

# 六十一、第三步

```python
loss = outputs.loss
```

这是：

> 当前模型预测和目标 Token 之间的综合误差。

其中：

```text
label = -100
```

的位置：

> 不参与。

---

# 六十二、第四步

```python
loss.backward()
```

发生：

```text
Loss
↓
Autograd
↓
Chain Rule
↓
Gradients
```

也就是：

> 算出各可训练参数对 Loss 的责任。

---

# 六十三、第五步

```python
optimizer.step()
```

Optimizer 根据：

```text
Gradient
+
Learning Rate
+
Optimizer内部状态
```

更新参数。

到这一刻：

> **模型才真正学了一步。**

---

# 六十四、然后下一 Step 再重复

```text
Batch 1
↓
Forward
↓
Loss
↓
Backward
↓
Update

Batch 2
↓
Forward
↓
Loss
↓
Backward
↓
Update

Batch 3
↓
...
```

重复成千上万次以后：

> 模型行为逐渐改变。

---

# 六十五、一个 Step、一个 Batch、一个 Epoch 不要混

先给最简单定义。

# Sample

一条训练样本。

---

# Batch

一次一起送进模型的：

> 多条 Sample。

例如：

```text
Batch Size = 8
```

就是一次处理：

> 8 条样本。

---

# Step

通常一次：

```text
Forward
+
Backward
+
Optimizer Update
```

称为一个训练 Step。

但以后有 Gradient Accumulation 后：

> 多个 Micro-batch Forward/Backward 才可能对应一次 Optimizer Step。

后面再细讲。

---

# Epoch

整个 Train Dataset：

> 大致完整看一遍。

例如：

```text
100,000 Samples
```

跑完一遍：

```text
1 Epoch
```

---

# 六十六、暂时只需要这样记

```text
Sample
=
一道题

Batch
=
一次拿几道题一起做

Step
=
做完后进行一次学习更新

Epoch
=
整本题库学一遍
```

这个类比够用了。

---

# 六十七、现在做一个完整采购训练案例

Prompt：

```text
供应商须在投标截止日前
已经在本市设立固定售后服务机构。

请判断是否存在潜在风险。
```

Target：

```text
存在潜在风险。
```

---

假设模型当前预测：

```text
不存在风险     65%
存在潜在风险   20%
需要复核       15%
```

那么：

```text
正确答案概率低
↓
Cross Entropy较大
↓
Loss较高
```

---

# 六十八、Backward 开始追责

系统发现：

```text
当前参数组合
过分支持“不存在风险”
```

于是产生 Gradient：

```text
某些方向
需要降低

某些方向
需要提高
```

---

# 六十九、Optimizer 更新

更新以后再遇到类似条件：

```text
投标前
+
本地固定机构
+
作为投标资格
```

模型可能变成：

```text
不存在风险     45%
存在潜在风险   40%
需要复核       15%
```

还不完美。

继续训练。

---

# 七十、经过更多高质量案例以后

可能逐渐变成：

```text
不存在风险     10%
存在潜在风险   78%
需要复核       12%
```

这就是：

# Learning

不是突然“记住一条规则”。

而是：

> 参数经过大量小步更新，使正确专业行为的概率逐渐提高。

---

# 七十一、再加入一个 Hard Negative

条款：

```text
中标供应商应确保项目所在地
2小时内现场服务响应，
不限制服务机构设立方式。
```

如果模型错误预测：

```text
存在地域资格风险
=
80%
```

专家 Target：

```text
不能仅凭该条件直接判为地域准入风险
```

那么这个样本会产生：

> 与前一个案例不同方向的 Gradient。

---

# 七十二、于是两个样本一起塑造决策边界

```text
案例 A
投标前已有本地机构
        ↓
风险概率提高

案例 B
中标后履约响应
不限制实现方式
        ↓
不要轻易报警
```

这就是：

> Hard Positive / Hard Negative 为什么比大量简单案例更有价值。

---

# 七十三、模型真正学的不是“本地 = Risk”

而应该逐渐学：

```text
本地
+
发生阶段
+
限制对象
+
是否为准入条件
+
是否限制实现方式
+
业务上下文
        ↓
综合判断
```

这才是我们想要的：

# Decision Boundary Learning
## 决策边界学习

---

# 七十四、一个常见误解：一条样本就会把模型改坏吗？

通常一个正常学习率下的单一样本：

> 只产生一次相对小的参数更新。

真正模型行为：

> 是大量样本、多个 Step 累积的结果。

所以：

\[
\boxed{
ModelBehavior
=
AccumulatedUpdates
}
\]

---

# 七十五、但为什么错误数据仍然危险？

因为如果有：

```text
10万条
同一种错误Label
```

这些 Gradient 会反复往错误方向推动。

所以：

> 数据质量直接决定 Gradient 质量。

可以写成：

\[
\boxed{
GarbageData
\rightarrow
GarbageGradient
}
\]

这是第五课非常值得记住的一句话。

---

# 七十六、这解释了为什么第四课不能省

很多人会问：

> 为什么不直接下载模型然后 LoRA？

因为 LoRA 不是：

> 自动把错误数据变成正确能力。

它只是：

> 更高效地执行参数更新。

如果 Dataset 本身错：

> LoRA 只会更高效地学错。

---

# 七十七、第五课和第四课真正的接口

```text
第四课
Data Quality
    ↓
Target Quality
    ↓
Loss Quality
    ↓
Gradient Quality
    ↓
第五课
Model Quality
```

这是两课之间最重要的一张因果链。

---

# 七十八、现在把本阶段几个最危险的错误挑出来

## 错误 1：认为 Loss 本身会修改参数

不对。

```text
Loss
↓
Backward
↓
Gradient
↓
Optimizer
↓
Update
```

少一步：

> 都不是完整训练。

---

## 错误 2：认为 `backward()` 就已经更新参数

不对。

`backward()`：

> 主要算 Gradient。

`optimizer.step()`：

> 才更新。

---

## 错误 3：认为 Gradient 等于参数改变量

也不完全对。

真正参数改多少还取决于：

```text
Learning Rate
Optimizer
Momentum / Adam状态
Weight Decay
```

所以：

> Gradient 是更新依据，不是最终更新量本身。

---

## 错误 4：认为 Base Model 冻结就不参与 Forward

不对。

被冻结：

> 是不更新其权重。

不是：

> 不使用它。

---

## 错误 5：认为 Training Loss 越低，模型业务能力一定越强

不对。

训练 Loss 低：

> 只说明更符合训练目标。

是否真正泛化：

> 看 Validation / Benchmark。

---

# 七十九、再压缩成一个“训练五件套”

以后你看到任何 SFT 代码，只查五件事：

```text
1. Input
模型看到了什么？

2. Target
正确答案是什么？

3. Loss
模型错了多少？

4. Gradient
哪些参数应该怎么改？

5. Optimizer
参数实际上改了多少？
```

这五件事清楚：

> 训练代码就不会神秘。

---

# 八十、本阶段的工程对象

今天我们正式形成：

# `SFTTrainingStep_V0.1`

概念记录可以包括：

```text
input_ids
labels
loss_mask

forward_logits

loss

trainable_parameters

grad_norm

learning_rate

optimizer

global_step
```

以后真正训练时：

> 这些东西会进入 Training Log。

---

# 八十一、为什么要记录 `grad_norm`？

# Gradient Norm
## 梯度范数

可以粗略理解为：

> 这一 Step 整体 Gradient 有多大。

如果突然：

```text
grad_norm
极大
```

可能意味着：

```text
异常Batch
数值不稳定
Learning Rate问题
训练爆炸
```

以后第 12 阶段讲训练曲线时会重新回来。

今天只需要认识：

> Gradient 也有需要监控的“强度”。

---

# 八十二、为什么要记录 Learning Rate？

因为有些训练不是始终固定：

```text
Learning Rate = 2e-4
```

而会：

```text
Warmup
↑
达到峰值
↓
逐渐衰减
```

所以同一个 Step 的参数更新：

> 还受当前 Learning Rate 影响。

这也是为什么实验必须记录：

```text
global_step
learning_rate
loss
```

---

# 八十三、但是这些先不要把脑子塞满

今天真正必须掌握的不是 Scheduler。

而是主干：

```text
Forward
↓
Logits
↓
Probability
↓
Loss
↓
Backward
↓
Gradient
↓
Optimizer
↓
Parameter Update
```

后面的所有训练技巧：

> 都是在这条主干周围做工程优化。

---

# 八十四、本阶段最值得记住的三个“≠”

第一：

\[
\boxed{
Loss
\neq
Gradient
}
\]

第二：

\[
\boxed{
Backward
\neq
OptimizerStep
}
\]

第三：

\[
\boxed{
TrainingLossDown
\neq
BusinessAbilityUp
}
\]

这三个如果不混：

> 已经超过很多只会复制 Trainer 参数的人。

---

# 八十五、再强化一次 5 个核心心智模型

如果过一周以后，第 2 阶段只剩五句话，我希望是：

> **第一，SFT 仍然是在做 Next Token Prediction，只是正确答案来自我们的专家数据。**

> **第二，Forward 负责产生预测，Cross Entropy 把预测和正确 Token 比较后得到 Loss。**

> **第三，Loss 只告诉模型“错多少”，Backward 才通过链式法则计算每个可训练参数应该往哪个方向调整。**

> **第四，`loss.backward()` 负责计算 Gradient，`optimizer.step()` 才真正更新参数。**

> **第五，SFT 的最终效果，是大量小的参数更新不断重塑 `P(Response | Prompt)`；训练 Loss 下降并不等于真实业务能力一定提升。**

这就是第 2 阶段真正的骨架。

---

# 八十六、本阶段最核心的一张图

```text
Expert Training Example
专家训练样本
        │
        ▼
Prompt + Correct Response
        │
        ▼
      Forward
        │
        ▼
      Logits
每个Token候选分数
        │
        ▼
      Softmax
        │
        ▼
   Probability
        │
        ▼
Cross Entropy
与正确Token比较
        │
        ▼
       Loss
模型错了多少
        │
        ▼
     Backward
数学上往回追责
        │
        ▼
     Gradient
每个可训练参数
该往哪边改
        │
        ▼
    Optimizer
结合学习率执行更新
        │
        ▼
 Parameter Update
        │
        ▼
下一次面对类似Prompt
更倾向于专家Response
```

这张图如果能直接在脑中跑起来：

> 第五课后面所有训练参数都会开始变得有意义。

---

# 八十七、本阶段掌握测试

现在不回看正文，你应该能够自己解释：SFT 为什么本质仍然是 Next Token Prediction；Logit 和 Probability 有什么区别；Softmax 做什么；Cross Entropy 为什么关注正确 Token 的概率；正确 Token 概率越低为什么 Loss 越高；Loss 和 Gradient 为什么不是一回事；Gradient 的正负和大小分别代表什么；Backward 为什么需要 Chain Rule；为什么 `loss.backward()` 不等于参数已经更新；`optimizer.step()` 到底做什么；Learning Rate 控制什么；为什么步长太大会导致训练震荡甚至数值不稳定；`zero_grad()` 为什么存在；Teacher Forcing 是什么；为什么训练时模型通常看到专家正确的历史 Response Token，而推理时只能看到自己之前生成的 Token；为什么 Loss Mask 和 Teacher Forcing 是两件完全不同的事；为什么 Transformer 训练时可以并行计算多个 Token 的 Loss；Base Model 被 LoRA 冻结以后为什么仍然参与 Forward；LoRA 真正更新的是谁；为什么 SFT 本质上是在重塑 `P(Response | Prompt)`；为什么 Hard Negative 能通过 Gradient 修正错误决策边界；为什么错误 Dataset 会产生错误 Gradient；以及为什么 Training Loss 下降不能直接证明政府采购业务能力提高。

如果这些可以完整讲出来：

\[
\boxed{
第五课第2阶段真正掌握
}
\]

---

# 本阶段最后只记一句话

> **一次 SFT Step 的本质，就是模型先用当前参数预测下一个 Token，再用 Cross Entropy 衡量它与专家答案的差距，通过 Backpropagation 把这份错误沿 Transformer 反向传成 Gradient，最后由 Optimizer 按 Learning Rate 对可训练参数做一次小更新；成千上万次这样的微小更新，最终才把 `P(Response \mid Prompt)` 逐渐塑造成我们希望的政府采购专业行为。**

---

# 下一阶段：第五课 · 第 3 阶段
# 训练样本长度、Truncation 与 Padding
## 为什么一条“内容完全正确”的政府采购训练数据，也可能因为 Token 长度处理错误而被训练坏？

第 2 阶段解决的是：

> **一次训练 Step 怎样改变参数。**

第 3 阶段开始解决一个非常现实的问题：

```text
采购条款只有 80 Tokens

另一个案例 600 Tokens

另一份复杂上下文 4,000 Tokens

Base Model Context Window
又有固定上限
```

那么我们必须决定：

```text
多长才算一个训练样本？
超过长度怎么办？
从左边截还是右边截？
Prompt和Response谁更应该保护？
Padding为什么浪费GPU？
attention_mask到底在屏蔽什么？
```

第 3 阶段会把整个问题压成一条非常清楚的工程链：

```text
Raw SFT Example
      ↓
Token Length
      ↓
Length Policy
      ↓
Truncation
      ↓
Padding
      ↓
Attention Mask
      ↓
Batch Tensor
```

核心目标只有一个：

> **不能为了把数据塞进 GPU，而把真正应该学习的专家答案和关键业务条件切掉。**

---
