# 第五课 · 第 6 阶段
# LoRA 到底在改什么？
## 为什么两个很小的矩阵，就能改变一个几十亿参数模型的行为？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **把 Base Model 某一层删掉，再装一个小层。**
2. **Base Model 保留原能力，LoRA 在旁边提供任务相关的修正。**
3. **“重新学习这个巨大矩阵。”**
4. **“学习这个巨大矩阵需要改变多少。”**
5. **原矩阵 \(W\) 本身是低秩的。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `LoRA` | LoRA：冻结大部分基座参数，只训练低秩增量矩阵 |
| `Rank` | LoRA Rank：低秩增量的容量参数 |
| `Alpha` | LoRA Alpha：控制低秩更新缩放幅度 |
| `Transformer` | Transformer：以注意力和前馈网络为核心的序列架构 |
| `Adapter` | 适配器：附加在基座模型上的轻量可训练参数模块 |
| `Loss` | 损失函数：把预测错误压缩成可优化的数值信号 |

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

上一阶段我们最后停在：

\[
W' = W + \Delta W
\]

这句话其实已经把 LoRA 的门打开了一半。

Base Model 原来的参数是：

\[
W
\]

领域微调真正需要学习的是：

\[
\Delta W
\]

也就是：

> **为了让模型更符合政府采购任务，原来的权重到底需要发生怎样的变化？**

Full Fine-Tuning 的思路是：

> 直接让整个 \(W\) 自己变化。

LoRA 的思路完全不同：

> **冻结 \(W\)，不直接训练它；另外学习一个很小的 \(\Delta W\)。**

而 LoRA 最核心的一步是：

\[
\boxed{
\Delta W = BA
}
\]

本阶段只需要彻底搞懂这一件事。

最终形成：

# `LoRAUpdateModel_V0.1`

---

# 一、本阶段只有一个核心问题

假设 Transformer 中有一个巨大线性层：

\[
y = Wx
\]

其中 \(W\) 有几百万甚至几千万参数。

如果我们想微调它，为什么不直接训练整个：

\[
W
\]

而要额外增加：

\[
A
\]

和：

\[
B
\]

两个小矩阵？

整个 LoRA 流程可以先压缩成：

```text
输入 x
  │
  ├──────────────► Frozen W ──────────┐
  │                                   │
  └──► A ──► 小空间 ──► B ───────────┤
                                      ▼
                                    相加
                                      │
                                      ▼
                                 最终输出 y
```

数学上就是：

\[
\boxed{
y = Wx + BAx
}
\]

先把这张图锁进脑子。

---

# 二、先锁死 5 个核心心智模型

## 心智模型 1：LoRA 不替换 Base Model，而是在原模型旁边学习一个“修正量”

原模型：

\[
Wx
\]

LoRA：

\[
BAx
\]

最终：

\[
Wx + BAx
\]

所以 LoRA 不是：

> 把 Base Model 某一层删掉，再装一个小层。

而是：

> **Base Model 保留原能力，LoRA 在旁边提供任务相关的修正。**

因此：

\[
\boxed{
LoRA
=
BaseBehavior
+
TaskSpecificCorrection
}
\]

---

## 心智模型 2：真正学习的是 \(\Delta W\)，不是重新学习 \(W\)

LoRA 可以理解成：

\[
W' = W + \Delta W
\]

其中：

\[
W
\]

冻结。

而：

\[
\Delta W
\]

可学习。

于是训练问题从：

> “重新学习这个巨大矩阵。”

变成：

> **“学习这个巨大矩阵需要改变多少。”**

这是一种非常重要的思维转变。

---

## 心智模型 3：LoRA 的关键假设是——有用的参数变化可能存在于低维子空间

LoRA 并不是说：

> 原矩阵 \(W\) 本身是低秩的。

这一点千万别混。

它真正假设的是：

> **下游任务所需要的权重变化 \(\Delta W\)，可能不需要拥有完整矩阵那么高的自由度。**

因此：

\[
\boxed{
W\ 可以很复杂
}
\]

但：

\[
\boxed{
\Delta W\ 可能可以用低秩结构近似
}
\]

这是 LoRA 最核心的数学直觉。

---

## 心智模型 4：Rank 控制的是“允许 LoRA 学多少种独立变化方向”

如果：

\[
\Delta W = BA
\]

中间维度是：

\[
r
\]

这个 \(r\) 就叫：

# Rank
## 秩 / 低秩维度

直觉上：

> \(r\) 越小，允许表达的变化空间越受限制。

> \(r\) 越大，LoRA 拥有更多调整自由度。

今天先理解这个意义。

具体：

```text
r 到底选 8、16、32 还是 64？
alpha 怎么配？
dropout 怎么配？
```

放到下一阶段专门解决。

---

## 心智模型 5：LoRA 省参数的真正原因，是把一个“大矩阵”拆成两个“瘦矩阵”

这是最重要的计算直觉。

一个大矩阵：

\[
\Delta W
\]

本来可能需要：

\[
d_{out}\times d_{in}
\]

个参数。

LoRA 改成：

\[
B A
\]

只需要：

\[
r(d_{in}+d_{out})
\]

个参数。

只要：

\[
r \ll d_{in},d_{out}
\]

参数量就会大幅下降。

---

# 三、先从最普通的 Linear Layer 开始

Transformer 里大量计算都可以写成：

\[
y = Wx
\]

假设：

\[
x\in\mathbb{R}^{d_{in}}
\]

权重：

\[
W\in\mathbb{R}^{d_{out}\times d_{in}}
\]

那么输出：

\[
y\in\mathbb{R}^{d_{out}}
\]

---

# 四、如果做 Full Fine-Tuning

直接修改：

\[
W
\]

例如：

\[
W
=
4096\times4096
\]

那么一个矩阵的参数量就是：

\[
4096\times4096
=
16,777,216
\]

也就是：

> 约 1678 万个参数。

仅仅：

> 一个矩阵。

Transformer 里这样的矩阵：

> 有很多。

---

# 五、LoRA 怎么做？

LoRA 不直接训练：

\[
W
\]

而是：

\[
W' = W + BA
\]

其中：

\[
A\in\mathbb{R}^{r\times d_{in}}
\]

而：

\[
B\in\mathbb{R}^{d_{out}\times r}
\]

所以：

```text
输入维度 d_in
      │
      ▼
      A
d_in → r
      │
      ▼
一个很小的中间空间
      │
      ▼
      B
r → d_out
      │
      ▼
输出维度 d_out
```

---

# 六、这里真正发生了一次“压缩 → 展开”

矩阵 A：

\[
A:
d_{in}\rightarrow r
\]

把高维输入：

> 投影到一个很小的低维空间。

然后矩阵 B：

\[
B:
r\rightarrow d_{out}
\]

再把这个低维变化：

> 投影回原来的输出维度。

所以 LoRA 的直觉可以压成：

```text
高维输入
   ↓
A
   ↓
低维任务变化空间
   ↓
B
   ↓
高维修正量
```

这个“低维任务变化空间”：

> 就是 LoRA 真正省参数的地方。

---

# 七、用一个数字例子彻底看懂

仍然假设：

\[
W\in\mathbb{R}^{4096\times4096}
\]

如果直接训练完整更新矩阵：

\[
\Delta W
\]

需要：

\[
16,777,216
\]

个自由参数。

现在假设：

\[
r=8
\]

那么：

\[
A:
8\times4096
\]

参数：

\[
32,768
\]

而：

\[
B:
4096\times8
\]

参数：

\[
32,768
\]

总共：

\[
65,536
\]

所以：

```text
完整矩阵变化
≈ 1678万参数

LoRA低秩变化
≈ 6.55万参数
```

差距非常大。

---

# 八、但最终 \(\Delta W\) 的形状没有变

这一点特别重要。

虽然：

\[
A
\]

和：

\[
B
\]

很小，

乘起来：

\[
BA
\]

仍然得到：

\[
d_{out}\times d_{in}
\]

也就是说：

\[
BA
\]

与：

\[
W
\]

形状完全兼容。

所以才能：

\[
W+BA
\]

---

# 九、这就是 LoRA 最漂亮的地方

它不是：

> 只修改原矩阵的一小块。

也不是：

> 输出一个低维答案。

最终产生的修正：

\[
\Delta W=BA
\]

仍然作用在：

> **完整高维权重空间。**

只是这个变化：

> 被限制在一个低秩结构中。

---

# 十、为什么叫 Low-Rank Adaptation？

# Low-Rank Adaptation
## 低秩适配

名字来自：

\[
\Delta W = BA
\]

因为它的秩最多受：

\[
r
\]

限制。

可以写成：

\[
\operatorname{rank}(BA)\le r
\]

所以当：

\[
r\ll4096
\]

时：

> \(\Delta W\) 是一个低秩变化。

这就是：

# LoRA

名字真正的来源。

---

# 十一、低秩到底意味着什么？

不要把“秩”搞成纯数学名词。

可以把一个大矩阵能够做的变化想成：

> 有很多很多可能的独立方向。

完整矩阵更新：

```text
方向1
方向2
方向3
方向4
……
可能非常多
```

LoRA 说：

> 对这个具体领域任务，也许实际上只需要少数几个主要变化方向。

例如非常粗略地想象政府采购任务：

```text
变化方向 A
更关注资格条件

变化方向 B
减少关键词Shortcut

变化方向 C
证据不足时更愿意needs_review

变化方向 D
输出结构更加稳定
```

真实神经网络当然不会这么整齐地“一方向对应一规则”。

但这种类比能帮助理解：

> **领域适配可能只需要改变原模型行为空间中的有限几个主方向。**

---

# 十二、为什么这个假设可能成立？

因为 Base Model 已经不是一张白纸。

它本来已经会：

```text
中文
法律语言
推理
分类
解释
生成
结构化输出
```

我们不是在要求它：

> 学会一种全新的智能。

我们更多是在要求：

> **重新组合和偏置已经存在的能力。**

所以可能不需要：

\[
4096\times4096
\]

这么多独立变化自由度。

只需要：

> 一个小得多的有效适配空间。

---

# 十三、把它和政府采购项目对应起来

Base Model 本身可能已经理解：

```text
“供应商”
“资格条件”
“本地”
“履约”
“评分”
“风险”
```

但它没有形成我们希望的稳定决策边界。

例如原模型：

```text
看到“本地”
       ↓
很容易直接报警
```

我们的数据则不断告诉它：

```text
投标前必须已有本地机构
        ≠
中标后保证本地服务能力
```

LoRA 并不需要：

> 重新创造“本地”“供应商”这些概念。

而是：

> 调整这些已有表示在任务中的使用方式。

这正是低秩适配特别有吸引力的地方。

---

# 十四、训练时到底谁会变？

假设：

\[
y = Wx + BAx
\]

训练开始：

```text
W
Frozen
不更新

A
Trainable

B
Trainable
```

Forward：

```text
x
│
├──► W x
│
└──► B A x
       │
       ▼
      相加
       │
       ▼
       y
```

然后：

```text
y
↓
Loss
↓
Backward
```

梯度主要更新：

\[
A,B
\]

而不是：

\[
W
\]

---

# 十五、所以第 2 阶段的 Gradient 链现在可以升级了

以前：

```text
Loss
↓
Backward
↓
Gradient
↓
Model Parameters
```

现在 LoRA 场景变成：

```text
Loss
      ↓
Backward
      ↓
┌───────────────────────┐
│ Frozen Base W         │
│ 不由Optimizer更新     │
│                       │
│ LoRA A       ✓ grad   │
│ LoRA B       ✓ grad   │
└──────────┬────────────┘
           ↓
      Optimizer
           ↓
      更新 A / B
```

这就是：

> **LoRA 真正训练的东西。**

---

# 十六、一个非常重要的理解：Base Path 和 LoRA Path 同时存在

很多人第一次看 LoRA 会误以为：

```text
W
被BA替代了
```

不是。

实际上：

\[
Wx
\]

还在。

而：

\[
BAx
\]

是额外加上去的。

因此：

\[
\boxed{
LoRAOutput
=
BaseOutput
+
AdaptationOutput
}
\]

这句话非常重要。

---

# 十七、为什么刚开始训练时不能一下把模型行为破坏掉？

理想情况下：

> LoRA 刚挂上去时，应尽量接近原 Base Model 行为。

也就是初始：

\[
\Delta W\approx0
\]

于是：

\[
W' \approx W
\]

常见实现会让两个 LoRA 矩阵中的一个：

> 随机初始化，

另一个：

> 零初始化，

从而让初始：

\[
BA=0
\]

或非常接近 0。

具体初始化规则由实现决定。

心智模型只记：

> **LoRA 刚加入时尽量不改变 Base Model，然后通过训练逐渐长出任务修正量。**

---

# 十八、这件事非常漂亮

训练刚开始：

```text
Base Model
100%

LoRA Correction
≈ 0
```

训练逐渐进行：

```text
Base能力
+
越来越有意义的领域修正
```

所以 LoRA 的训练不是：

> 先把原模型打碎，再重新拼。

而更像：

> **在稳定底模旁边逐步学出一层任务偏置。**

---

# 十九、LoRA Forward 更完整的公式

实际常见形式会带一个缩放因子：

\[
y
=
Wx
+
sBAx
\]

其中：

\[
s
\]

控制：

> LoRA 分支的整体作用强度。

一种常见形式是：

\[
s=\frac{\alpha}{r}
\]

也就是后面会看到的：

```text
lora_alpha
rank r
```

但今天先不要陷入参数选择。

只知道：

> **A、B 决定变化方向和内容，Scaling 决定这条变化分支整体有多强。**

下一阶段专门讲：

```text
Rank
Alpha
Dropout
```

---

# 二十、现在精准区分四个对象

| 对象 | 作用 |
|---|---|
| \(W\) | Base Model 原权重，通常冻结 |
| \(A\) | 将输入映射到低维 LoRA 空间 |
| \(B\) | 将低维变化映射回输出空间 |
| \(BA\) | 实际产生的权重修正 \(\Delta W\) |

所以：

\[
\boxed{
\Delta W = BA
}
\]

不是两个完全独立的模型。

而是一整个：

> **低秩更新结构。**

---

# 二十一、LoRA 参数少，为什么 Checkpoint 也小？

因为保存 Adapter 时：

> 主要保存训练出来的 A、B 等 Adapter 参数。

并不需要重新保存：

> 整套巨大 Base Model。

于是：

```text
Base Model
7B
保持原样

+

LoRA Adapter
只保存小量新增参数
```

所以实验版本可以是：

```text
Base Model
│
├── LoRA-A
├── LoRA-B
├── LoRA-C
└── LoRA-D
```

这也是为什么 LoRA 特别适合：

> 快速实验和版本对比。

---

# 二十二、推理时是不是每次都必须保留两个分支？

不一定。

有两种常见思路。

### Adapter 模式

推理时：

\[
Wx + BAx
\]

两个分支一起计算。

优点：

> Adapter 可以自由挂载和切换。

---

### Merge 模式

因为：

\[
W' = W + BA
\]

可以事先计算：

\[
W_{\text{merged}}
=
W+BA
\]

然后推理时直接：

\[
y=W_{\text{merged}}x
\]

这叫：

# Merge

后面的 Checkpoint / Adapter 阶段会详细讲。

---

# 二十三、所以 LoRA 既可以“外挂”，也可以“合并”

```text
训练阶段

Base W Frozen
     +
LoRA A/B
     ↓
得到 Adapter
```

然后：

```text
方案 A
Base + Adapter
动态使用
```

或者：

```text
方案 B
W + BA
   ↓
Merged Weight
```

但要记住：

> Merge 改变的是部署表达方式，不改变 LoRA 当初学习的数学含义。

---

# 二十四、LoRA 到底应该加在哪些矩阵上？

现在我们知道 Transformer 有：

```text
q_proj
k_proj
v_proj
o_proj

up_proj
gate_proj
down_proj
...
```

理论上：

> 可以给不同 Linear Layer 加 LoRA。

但是：

> 加到哪里，会直接决定哪些模型计算路径拥有可训练修正。

这就是：

# Target Modules

不过这里先踩刹车。

今天只需要知道：

> **LoRA 并不是自动加到整个模型所有地方。**

下一阶段之后我们会专门讨论：

> q/k/v/o、MLP 到底怎么选。

---

# 二十五、所以 LoRA 有两个不同维度的“容量”

以后千万不要只盯着 Rank。

第一个：

# 每个 Adapter 有多宽？

也就是：

\[
r
\]

---

第二个：

# 到底给多少层、多少模块装 Adapter？

也就是：

```text
Target Modules
+
Number of Layers
```

因此真正 LoRA 总容量大致受到：

```text
Rank
×
Target Module数量
×
Layer数量
```

共同影响。

这就是为什么：

> 单纯问“r=8 好还是 r=16 好”其实信息不够。

---

# 二十六、现在来算 LoRA 参数量公式

假设：

\[
W
\in
\mathbb{R}^{d_{out}\times d_{in}}
\]

完整矩阵：

\[
N_{\text{full}}
=
d_{out}d_{in}
\]

LoRA：

\[
A
\in
\mathbb{R}^{r\times d_{in}}
\]

参数数：

\[
rd_{in}
\]

以及：

\[
B
\in
\mathbb{R}^{d_{out}\times r}
\]

参数数：

\[
d_{out}r
\]

所以：

\[
\boxed{
N_{\text{LoRA}}
=
r(d_{in}+d_{out})
}
\]

这条公式值得记。

---

# 二十七、什么时候 LoRA 不再“很省”？

如果：

\[
r
\]

越来越接近：

\[
d_{in},d_{out}
\]

那么：

\[
r(d_{in}+d_{out})
\]

自然越来越大。

所以 LoRA 有意义的基本前提之一就是：

\[
\boxed{
r\ll d
}
\]

即：

> 中间低秩空间远小于原模型隐藏维度。

---

# 二十八、Rank 太小是不是一定不够？

不一定。

这就是为什么不能靠直觉拍参数。

如果任务变化非常简单：

> 很小的 \(r\) 可能已经足够。

如果任务非常复杂：

> 更大 \(r\) 可能带来额外容量。

真正答案需要：

```text
固定 Dataset
+
固定 Benchmark
+
控制变量实验
```

而不是：

> “网上都用 64，所以我们也用 64。”

---

# 二十九、这和第四课的数据思想完全一致

LoRA Rank 是：

> 模型容量变量。

而是否足够：

> 必须由 Hard Case / Validation / Benchmark 证明。

所以：

```text
Config
        ↓
Train
        ↓
Validation
        ↓
Slice / Hard Case
        ↓
决定是否增加容量
```

而不是：

```text
参数越大
        ↓
肯定越好
```

---

# 三十、LoRA 真正改变的是概率分布，不是“插入规则”

这和第 2 阶段必须连起来。

LoRA 训练以后：

> 不是在模型里出现了一条：

```text
IF 条款含“本地”
THEN 风险=true
```

而是：

\[
A,B
\]

改变了网络中的中间表示和最终 Logits。

于是：

\[
P_\theta(Response\mid Prompt)
\]

发生变化。

例如：

```text
训练前

P(存在潜在风险)
= 0.31
```

训练后：

```text
P(存在潜在风险)
= 0.74
```

这是：

> 概率行为被低秩更新重新塑造。

---

# 三十一、LoRA 不等于知识库

这点必须再次强调。

如果明天法规更新：

> LoRA 参数不会自动知道。

LoRA 更适合学习：

```text
任务行为
输出格式
专业判断模式
偏好
决策边界
```

而：

```text
最新法规全文
最新政策日期
实时文件
```

通常仍然应该通过：

> RAG / Knowledge System

动态提供。

---

# 三十二、一个政府采购例子

假设 Base Model 原本面对：

```text
供应商须在投标截止前
在项目所在地设立分支机构。
```

模型倾向：

```text
无明显风险
```

经过专家 SFT：

```text
Prompt
+
Gold Response
```

Loss 不断推动 LoRA：

\[
A,B
\]

改变。

最终 LoRA 分支可能使内部表示更重视：

```text
“投标截止前”
+
“已经设立”
+
“作为参与条件”
```

而不是只看：

```text
“本地”
```

于是模型对类似案例：

> 风险识别概率上升。

---

# 三十三、再加入 Hard Negative

另一条：

```text
中标后应保证项目现场
2小时内响应。
供应商可自行选择服务实现方式。
```

如果模型因为：

```text
现场
+
本地
```

而错误报警，

Hard Negative 会产生相反方向的 Gradient。

于是同一组 LoRA 参数逐渐学习：

> **不是关键词本身，而是关键词与条件结构之间的关系。**

这就是：

# Decision Boundary Adaptation

---

# 三十四、这也解释了为什么 LoRA 容量不是越大越好

如果容量太大、数据又少：

> Adapter 也可能记住训练表达。

例如：

```text
见到某个固定模板
→ 直接输出固定答案
```

而不是：

> 学到真正稳定的边界。

所以 LoRA 仍然需要：

```text
Hard Negative
Validation
Data Diversity
Leakage Control
```

PEFT 并没有取消机器学习基本规律。

---

# 三十五、本阶段最容易混淆的 5 件事

### 误区 1

> LoRA 把大模型变成小模型。

错。

Base Model：

> 仍然完整存在。

---

### 误区 2

> LoRA 认为 Base Weight \(W\) 是低秩的。

错。

LoRA 重点约束的是：

\[
\Delta W
\]

---

### 误区 3

> A、B 是两个独立答案模型。

错。

它们一起表达：

\[
BA=\Delta W
\]

---

### 误区 4

> Rank 越大一定越好。

错。

它只是增加适配容量和参数成本。

---

### 误区 5

> LoRA 挂上去以后 Base Model 不再参与计算。

错。

最终仍然有：

\[
Wx
\]

---

# 三十六、现在给 LoRA 建立一个精准的三层模型

## 第一层：Base Capability

\[
Wx
\]

回答：

> Base Model 原本会什么？

---

## 第二层：Adaptation Capacity

\[
BAx
\]

回答：

> 我允许领域任务改变多少？

---

## 第三层：Final Behavior

\[
Wx+BAx
\]

回答：

> Base 能力加上领域修正以后，最终怎么表现？

这三层不要再混。

---

# 三十七、本阶段工程产物：`LoRAUpdateModel_V0.1`

现在应该能够记录：

```text
base_weight
=
frozen

update_parameterization
=
B @ A

rank
=
r

input_dimension
=
d_in

output_dimension
=
d_out

trainable_parameters
=
r * (d_in + d_out)

scaling
=
framework/config defined

initial_delta_weight
≈
0

merge_supported
=
true / implementation dependent
```

此外还必须关联：

```text
base_model_revision
target_module
layer
adapter_version
```

这样 Adapter 才真正可复现。

---

# 三十八、本阶段最核心的一张图

```text
                         输入 x
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
       Base Model Path              LoRA Path
             │                           │
             ▼                           ▼
        Frozen W                     Matrix A
             │                      d_in → r
             │                           │
             │                           ▼
             │                      Low-rank Space
             │                           │
             │                           ▼
             │                        Matrix B
             │                      r → d_out
             │                           │
             ▼                           ▼
            Wx                          BAx
             │                           │
             └─────────────┬─────────────┘
                           ▼
                          相加
                           │
                           ▼
                 y = Wx + BAx
                           │
                           ▼
                         Loss
                           │
                           ▼
                       Backward
                           │
                           ▼
                    A / B 得到梯度
                           │
                           ▼
                  Optimizer 更新 A / B
                           │
                           ▼
                      W 保持冻结
```

如果这张图已经能在脑中直接运行：

> LoRA 最核心的 80% 已经掌握。

---

# 三十九、把整个阶段压成最精准的 5 句话

> **第一，LoRA 不重新训练 Base Weight，而是在冻结的 \(W\) 旁边学习一个任务修正量 \(\Delta W\)。**

> **第二，LoRA 的核心是 \(\Delta W=BA\)：用两个瘦矩阵表示一个完整高维权重变化。**

> **第三，低秩假设针对的是“任务所需的权重变化可能只占少数有效方向”，不是说 Base Model 本身很简单。**

> **第四，Forward 仍然使用完整 Base Model，最终输出是 \(Wx+BAx\)；Backward 主要更新 A、B，而 W 保持冻结。**

> **第五，LoRA 节省参数的本质来自 \(r(d_{in}+d_{out})\ll d_{in}d_{out}\)，但 Rank 多大、装在哪些模块上，必须由任务和 Benchmark 决定。**

---

# 四十、本阶段掌握测试

现在不回看正文，你应该能够自己解释：LoRA 的全称是什么；为什么 LoRA 不等于把大模型变成小模型；\(W' = W+\Delta W\) 表示什么；为什么 LoRA 冻结 \(W\) 而学习 \(\Delta W\)；为什么 \(\Delta W\) 可以写成 \(BA\)；A、B 的形状分别是什么；为什么 \(BA\) 最终仍然和 \(W\) 具有相同形状；什么叫 Low Rank；为什么 \(\operatorname{rank}(BA)\le r\)；为什么 LoRA 的低秩假设针对的是参数更新而不是 Base Weight；为什么 \(r(d_{in}+d_{out})\) 会比 \(d_{in}d_{out}\) 小很多；为什么 Base Path 和 LoRA Path 会同时存在；为什么刚初始化 LoRA 时希望 \(\Delta W\) 接近 0；为什么 LoRA Adapter 通常依赖对应 Base Model；Adapter 模式和 Merge 模式有什么关系；为什么 Target Modules 也会影响 LoRA 总容量；以及为什么 LoRA 最终改变的仍然是 `P(Response | Prompt)`，而不是在模型内部硬编码一条采购规则。

如果这些能自己完整讲出来：

\[
\boxed{
第五课第6阶段真正掌握
}
\]

---

# 本阶段最后只记一句话

> **LoRA 的本质不是“训练一个小模型”，而是在完整且冻结的 Base Model 旁边学习一个低秩权重修正 \(\Delta W=BA\)：Base Model 保留原能力，A、B 用极少参数学习政府采购任务真正需要改变的少数方向，最终通过 \(W' = W+BA\) 重塑模型的专业行为。**

---

# 下一阶段：第五课 · 第 7 阶段
# LoRA Rank、Alpha、Dropout
## `r`、`alpha`、`dropout` 到底在控制什么？

现在我们已经真正理解：

\[
\Delta W=BA
\]

下一阶段就不再把：

```text
r = 16
lora_alpha = 32
lora_dropout = 0.05
```

当成网上抄来的三个数字。

我们会精准区分：

```text
Rank
=
容量

Alpha / Scaling
=
修正分支的作用尺度

Dropout
=
训练时对LoRA路径的正则化
```

并建立一条真正能自己选参数的判断链：

```text
Task Complexity
      ↓
Rank Capacity
      ↓
Scaling Strength
      ↓
Regularization
      ↓
Validation / Hard Case
      ↓
是否需要扩大或收缩 LoRA

<!-- integration-only repair: close unmatched fence at stage boundary; canonical stage file unchanged -->
```

---
