# 第五课 · 第 4 阶段
# Packing：怎样减少 GPU 浪费？
## 多条短样本怎样安全装进同一条训练 Sequence，而又不互相“串台”？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **对齐 Tensor。**
2. **尽量让 GPU 算真实训练 Token，而不是 PAD。**
3. **为了提高 GPU 利用率，把多个独立 Sample 放进同一个计算容器。**
4. **可能仍然能够 Attention 到 A。**
5. **A A A PAD PAD PAD**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Batch` | 批次：一次参与计算的一组样本 |
| `Padding` | 补齐：把不同长度序列补到统一批次长度 |
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `Sample` | 样本：具有明确输入、目标和来源的一条训练/评测记录 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Attention` | 注意力：根据内容相关性动态聚合信息 |

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

第 3 阶段我们解决了：

> **单条样本太长怎么办，以及不同长度样本怎样通过 Padding 组成 Batch。**

但现在出现相反的问题。

假设我们的训练长度：

```text
max_sequence_length = 4096
```

大量政府采购样本却只有：

```text
Sample A    180 Tokens
Sample B    260 Tokens
Sample C    420 Tokens
Sample D    310 Tokens
```

如果每条样本都大量 Padding：

> GPU 会花很多算力处理没有信息价值的空位。

于是出现今天的核心技术：

# Packing
## 样本装箱 / 序列打包

本阶段最终形成：

# `SFTPackingPolicy_V0.1`

---

# 一、本阶段只解决一个核心问题

> **怎样把多条短 SFT 样本尽可能紧凑地放进固定长度 Sequence，同时保持每条样本自己的对话边界、Loss 边界和必要的 Attention 隔离？**

整个过程只需要记住这一张图：

```text
Sample A
180 Tokens
      ┐
Sample B
260 Tokens
      │
Sample C
420 Tokens
      ├──── Packing ────► Packed Sequence
Sample D                         │
310 Tokens                      │
      ┘                         ▼
                         Sample Boundaries
                                │
                     ┌──────────┼──────────┐
                     ▼          ▼          ▼
                   EOS       Loss Mask   Attention
                  边界         正确         隔离
                     │          │          │
                     └──────────┼──────────┘
                                ▼
                              GPU
```

中文只记一句：

> **Packing 的目标是减少空算，而不是把不同训练样本混成一条业务对话。**

---

# 二、先锁死 5 个核心心智模型

## 心智模型 1：Packing ≠ Padding

这两个看起来都在解决长度问题，但方向正好相反。

### Padding

短样本后面：

```text
补空位
```

例如：

```text
A A A PAD PAD PAD
```

目的是：

> 对齐 Tensor。

### Packing

把多个真实样本：

```text
A + B + C
```

紧凑放到同一 Sequence。

所以：

\[
\boxed{
Padding
=
FillWithEmptyTokens
}
\]

而：

\[
\boxed{
Packing
=
FillWithRealTokens
}
\]

Packing 的价值就是：

> **尽量让 GPU 算真实训练 Token，而不是 PAD。**

---

## 心智模型 2：Packed Sequence 是计算容器，不是一条新业务样本

这是今天最重要的一句话。

假设：

```text
Sample A
=
供应商资格审查

Sample B
=
评分办法审查
```

Packing 后可能物理上变成：

```text
[A Tokens][EOS][B Tokens][EOS]
```

但语义上：

```text
A 和 B
仍然是两条独立样本
```

所以：

\[
\boxed{
OnePackedSequence
\neq
OneSemanticExample
}
\]

它只是：

> **为了提高 GPU 利用率，把多个独立 Sample 放进同一个计算容器。**

---

## 心智模型 3：Packing 真正危险的不是拼接，而是“边界泄漏”

如果只是简单：

```text
A + EOS + B
```

然后使用普通 Causal Attention，

那么 B 后面的 Token：

> 可能仍然能够 Attention 到 A。

也就是：

```text
Sample B
← 可以看到 Sample A
```

这叫：

# Cross-sample Attention
## 跨样本注意力

于是模型可能在训练 Sample B 时：

> 使用本来不属于 B 的 Sample A 信息。

因此：

\[
\boxed{
Packing
必须同时考虑
SampleBoundary
}
\]

不是拼起来就完事。

---

## 心智模型 4：EOS、Loss Mask、Attention Mask 各管一件不同的事

Packing 后至少有三个边界。

### EOS

告诉语言模型：

> **前一条序列结束了。**

### Loss Mask

告诉训练系统：

> **哪些 Token 计算 Loss。**

### Attention Boundary

告诉模型：

> **哪些 Token 可以看到哪些 Token。**

三者不能混成一个概念。

---

## 心智模型 5：Packing 优化的是 Token Utilization，不应该改变训练语义

如果实现正确：

```text
不Packing训练
```

和：

```text
Packing训练
```

应该学习：

> 基本相同的 Sample → Target 关系。

Packing 只是让计算更紧凑。

所以：

\[
\boxed{
Packing
=
ComputeOptimization
}
\]

而不是：

\[
Packing
=
ChangeTaskMeaning
\]

如果打开 Packing 后模型学习内容发生巨大变化：

> 首先应该怀疑边界、Mask 或实现。

---

# 三、先看最简单的问题

假设：

```text
max_sequence_length = 2048
```

有四条数据：

```text
A = 300 Tokens
B = 400 Tokens
C = 250 Tokens
D = 500 Tokens
```

真实 Token 一共：

\[
300+400+250+500=1450
\]

如果分别独占一个 2048 Sequence：

```text
A + 1748 PAD
B + 1648 PAD
C + 1798 PAD
D + 1548 PAD
```

大量位置：

> 没有真实训练内容。

---

# 四、Packing 做什么？

Packing 可以尝试把它们组成：

```text
┌──────────────────────────────────────────────┐
│ Sample A │ EOS │ Sample B │ EOS │ Sample C │
└──────────────────────────────────────────────┘

另一个 Sequence：

┌─────────────────────┐
│ Sample D │ EOS │ ...│
└─────────────────────┘
```

也就是说：

> 一条计算 Sequence 内可以装多条训练 Sample。

这很像：

# 装箱问题

---

# 五、真正的目标指标：Packing Efficiency

可以定义：

\[
PackingEfficiency
=
\frac{RealTokens}
{AllocatedSequenceTokens}
\]

假设一个 2048 Sequence 最后放进去：

```text
1950 个真实 Token
```

那么：

\[
PackingEfficiency
=
\frac{1950}{2048}
\approx95.2\%
\]

这就是非常高的利用率。

---

# 六、但是我们已经学了 Dynamic Padding，为什么还需要 Packing？

这是个关键问题。

第 3 阶段：

# Dynamic Padding

解决的是：

> **一个 Batch 中，不要全部 Pad 到全局最大长度。**

例如：

```text
120
180
240
300
```

只 Pad 到：

```text
300
```

已经比 Pad 到 4096 好很多。

但仍然会产生：

```text
120 → 300
180 → 300
240 → 300
300 → 300
```

真实 Token：

\[
840
\]

计算位置：

\[
1200
\]

仍有浪费。

Packing 进一步问：

> 能不能直接把多个短样本连续装起来？

---

# 七、所以 Length Bucketing、Dynamic Padding、Packing 是三级优化

可以这样理解：

```text
最原始
所有样本 Pad 到全局 max_length
        ↓
Dynamic Padding
只 Pad 到当前 Batch 最大长度
        ↓
Length Bucketing
让长度相近的样本组 Batch
        ↓
Packing
把多个短样本直接塞进同一 Sequence
```

它们不是互斥技术。

而是：

> **逐步减少无效 Token 计算。**

---

# 八、现在看真正危险的地方：Sample B 能不能看到 A？

假设：

```text
Packed Sequence:

[A1 A2 A3 EOS B1 B2 B3 EOS]
```

普通 Causal Attention 的规则只有：

> 只能看当前位置左边。

那么：

```text
B1
```

左边包括：

```text
A1 A2 A3 EOS
```

所以理论上：

> B 可以读取 A。

这和我们真正希望的训练语义：

```text
Sample B
只依赖 Sample B 自己的Prompt
```

不完全一致。

---

# 九、严格 Packing 应该怎样理解？

最干净的规则是：

> 一个 Sample 内保持 Causal Attention。

> 不同 Sample 之间禁止 Attention。

概念上：

\[
Attention(i,j)=0
\]

如果：

\[
sample(i)\neq sample(j)
\]

即使：

```text
j
```

在物理位置上位于：

```text
i
```

左边。

---

# 十、这就形成 Block-diagonal Attention

假设：

```text
A1 A2 A3 | B1 B2 B3
```

理想 Attention 关系大致是：

```text
        A1 A2 A3 | B1 B2 B3

A1      ✓
A2      ✓  ✓
A3      ✓  ✓  ✓
-----------------------
B1               ✓
B2               ✓  ✓
B3               ✓  ✓  ✓
```

而不是：

```text
B1 → A
B2 → A
B3 → A
```

这叫：

# Block-diagonal Causal Attention
## 分块对角因果注意力

---

# 十一、为什么这比单纯加 EOS 更严格？

EOS 的意义是：

> 文本上告诉模型“一个序列结束了”。

但 EOS 本身通常并不意味着：

> Attention 数学上自动断开。

所以：

\[
\boxed{
EOSBoundary
\neq
AttentionIsolation
}
\]

这是今天一个非常重要的专业区别。

---

# 十二、实际框架里有两类 Packing

你以后看到 `packing=True`，不要立即认为实现都一样。

第一类大致是：

# Concatenation Packing

```text
Sample A
+ EOS
+ Sample B
+ EOS
```

然后仍使用普通 Causal Attention。

优点：

> 实现简单。

但：

> 后面的样本理论上可能看到前面的样本。

---

第二类是：

# Isolated / Block Packing

除了拼接，

还建立：

```text
sequence_id
block_attention_mask
position information
```

确保：

> 不同 Sample 在 Attention 上彼此隔离。

这是语义上更干净的做法。

---

# 十三、那是不是 Concatenation Packing 一定不能用？

不能这么绝对。

现实中一些训练系统会：

> 依赖 EOS 和大量随机样本边界，接受这种轻微跨样本上下文。

很多模型也确实这样训练过。

但我们的工程心智模型应该很清楚：

> **“有 EOS”与“严格隔离”不是同一件事。**

所以真正使用某个 Trainer 时：

> 必须确认它的 Packing 实现到底是哪一种。

不要看到：

```python
packing=True
```

就以为所有边界问题自动解决了。

---

# 十四、Packing 后 Loss Mask 也必须保留

假设 A：

```text
User A
Assistant A
```

B：

```text
User B
Assistant B
```

Packing 后：

```text
User A
Assistant A
EOS
User B
Assistant B
EOS
```

我们的 Loss Policy 仍然应该是：

```text
User A        -100
Assistant A   Loss

User B        -100
Assistant B   Loss
```

Packing：

> **不能把原来每条样本的 Loss Mask 结构抹掉。**

---

# 十五、正确心智模型是“先独立构造，再 Packing”

不要：

```text
把一堆Raw Text拼起来
        ↓
再猜谁是User谁是Assistant
```

更专业的顺序：

```text
Sample A
Messages → Template → Token IDs → Labels

Sample B
Messages → Template → Token IDs → Labels

Sample C
Messages → Template → Token IDs → Labels
        │
        ▼
然后再进行 Packing
```

因此：

\[
\boxed{
SemanticPreparation
Before
Packing
}
\]

Packing 应该是：

> 靠近训练 Batch 的计算优化层。

不是：

> 破坏 Semantic Dataset 的预处理层。

---

# 十六、一个 Packed Sequence 实际要同步 Packing 什么？

不仅是：

```text
input_ids
```

还至少包括：

```text
labels
attention information
sample boundaries
```

概念上：

```text
PackedInputIDs
=
A.input_ids
+
B.input_ids
+
C.input_ids
```

同时：

```text
PackedLabels
=
A.labels
+
B.labels
+
C.labels
```

边界也必须同步。

否则可能出现：

> Token 已经属于 B，但 Label Mask 仍按照 A 的位置处理。

那就属于非常危险的 Alignment Bug。

---

# 十七、Position IDs 怎么办？

Packed Sequence 还有一个更技术性的边界：

# Position IDs
## 位置编号

例如普通连续序列：

```text
A:
0 1 2 3

B:
4 5 6 7
```

某些严格隔离实现可能希望 B：

```text
0 1 2 3
```

重新开始。

是否重置 Position：

> 和模型结构、RoPE、Trainer 及 Packing 实现有关。

这里不需要死背实现。

只记一个原则：

> **不要自己随便改 Position IDs；遵循当前模型和 Packing Framework 的实现契约。**

---

# 十八、Packing 最不应该做的一件事：把样本从中间切断

假设剩余空间：

```text
200 Tokens
```

下一条 Sample：

```text
350 Tokens
```

最简单的 Packing 算法可能想：

```text
前200塞当前Sequence
后150塞下一Sequence
```

但这会造成：

```text
Prompt在前一个Sequence

Assistant答案
跑到下一个Sequence
```

非常危险。

所以对我们第一版 ProcurementLM：

# No-split Packing
## 样本完整打包

是更稳妥的默认方案。

原则：

> 一条 Semantic Example 要么完整放进去，要么放到下一个 Container。

---

# 十九、这和 Truncation 是两个不同问题

如果 Sample 本身：

```text
5000 Tokens
```

但：

```text
max_length = 4096
```

这是：

# Truncation / Long Sample Policy

不是 Packing 应该解决的。

Packing 只应该处理：

> **已经满足 Sequence Contract 的样本怎样高效组合。**

所以流程应该是：

```text
Sample Validation
      ↓
Length Policy
      ↓
合法的独立Sample
      ↓
Packing
```

---

# 二十、一个最简单的 Packing Algorithm

可以想象：

```text
Container = 4096 Tokens
```

按顺序加入：

```text
Sample A = 800
剩余3296

Sample B = 1200
剩余2096

Sample C = 1700
剩余396

Sample D = 600
放不下
```

于是：

```text
Packed Sequence 1
=
A + B + C
```

然后：

```text
Packed Sequence 2
=
D + ...
```

这就是最直观的：

# Greedy Packing
## 贪心装箱

---

# 二十一、还可以更聪明地装

例如：

```text
A = 2000
B = 1800
C = 600
D = 400
```

如果顺序不好：

> 可能留下大量碎片。

于是工程上还有：

```text
First Fit
Best Fit
First Fit Decreasing
```

等装箱算法。

这些名字现在不值得背。

核心只需要知道：

> **Packing 本质上也是一个“怎样减少剩余空位”的装箱问题。**

---

# 二十二、但不要为了 100% 利用率牺牲随机性

这是一个容易走极端的地方。

假设为了完美 Packing：

> 永远把相同长度、相同任务类型绑定在一起。

可能改变：

```text
数据Shuffle特性
Batch分布
任务混合方式
```

所以工程目标不是：

\[
PackingEfficiency = 100\%
\]

不惜一切代价。

而是：

> **效率足够高，同时训练数据仍然正常随机化。**

---

# 二十三、Packing 会改变“Batch Size”的直觉

这是非常重要的一点。

假设：

```text
per_device_train_batch_size = 4
```

没有 Packing 时：

```text
4 Sequences
≈
4 Samples
```

但 Packing 后：

```text
Sequence 1
包含3条Sample

Sequence 2
包含4条Sample

Sequence 3
包含2条Sample

Sequence 4
包含5条Sample
```

那么一个 Batch 实际可能包含：

```text
14 条原始Sample
```

所以：

\[
\boxed{
PackedBatchSize
\neq
OriginalSampleCount
}
\]

---

# 二十四、以后真正该关注的是 Tokens per Step

Packing 以后：

```text
Samples / Step
```

会变得比较不稳定。

更加稳健的训练规模指标是：

# Tokens per Step

甚至更进一步：

# Supervised Tokens per Step

也就是：

> 一个 Optimizer Step 到底消化了多少真实 Token，以及多少真正参与 Loss 的 Token。

---

# 二十五、这和 Gradient Accumulation 会进一步连接

未来我们会看到：

```text
micro batch
×
gradient accumulation
×
packed sequence length
```

共同决定：

> 每次参数更新实际使用多少训练信号。

所以后面看配置：

```text
batch_size=2
```

不能直接认为：

> “一次只学两条数据。”

这在 Packing 场景里很可能完全错。

---

# 二十六、Packing 会不会改变 Loss 权重？

这是个专业问题。

假设：

```text
Sample A
Assistant Response = 20 Tokens

Sample B
Assistant Response = 200 Tokens
```

如果 Loss 是：

> 对所有有效 Token 求平均，

那么 Sample B：

> 天然贡献更多监督 Token。

这本来就是 Token-level Causal LM Loss 的常见行为。

Packing 本身：

> 不应该额外改变这件事。

但如果你希望：

```text
每条Sample等权
```

而不是：

```text
每个Token等权
```

那就是另一个：

# Loss Weighting Policy

不能误以为 Packing 自动解决。

---

# 二十七、我们的第一版原则：不要一次把三个复杂问题混起来

第一版先保持：

```text
Assistant-only Loss
+
Token-level Mean Loss
+
No-split Packing
```

先把训练跑清楚。

以后真的有数据证明：

> 长回答样本权重过高，

再研究：

```text
Sample Weighting
Task Weighting
Loss Reweighting
```

不要第一版就把所有技巧堆满。

---

# 二十八、政府采购场景中，哪些样本特别适合 Packing？

最适合的是大量：

```text
短条款审查
结构化风险判断
短理由
Hard Negative Pair中的单条样本
```

例如：

```text
300
450
220
600
380 Tokens
```

这类数据：

> Packing 收益通常比较明显。

---

# 二十九、哪些数据 Packing 收益不大？

如果样本本身经常：

```text
3500
3800
4000
4090 Tokens
```

而：

```text
max_length = 4096
```

本来已经接近装满。

此时 Packing：

> 没多少空间可以优化。

因此：

\[
\boxed{
PackingValue
依赖
LengthDistribution
}
\]

所以在开 Packing 前：

> 先看第 3 阶段做的长度分布。

---

# 三十、这就把 Stage 3 和 Stage 4 接起来了

Stage 3 给我们：

```text
P50
P90
P95
P99
```

如果发现：

```text
P50 = 350
max_length = 4096
```

说明：

> 大量样本很短。

Packing：

> 很值得考虑。

如果：

```text
P50 = 3700
max_length = 4096
```

Packing 收益自然有限。

---

# 三十一、Evaluation 通常不要 Packing

训练时 Packing：

> 是为了提高计算利用率。

但 Validation / Test：

> 我们往往希望每条样本独立。

这样方便：

```text
生成
指标计算
错误分析
sample_id对应
Slice分析
```

所以第一版可以采用：

```text
Train
Packing = ON

Validation
Packing = OFF

Test
Packing = OFF
```

具体实现仍取决于框架。

---

# 三十二、Inference 也不属于今天这个 Packing

这里讲的是：

# Training Packing

不是推理系统的：

```text
Continuous Batching
Paged Attention
Request Batching
```

那些属于第 9 课部署。

不要把：

> 训练数据 Packing

和：

> 推理请求 Batch

混在一起。

---

# 三十三、现在给 ProcurementLM 定一个第一版 Packing Contract

# `SFTPackingPolicy_V0.1`

可以先规定：

```text
packing_scope
=
train_only

sample_integrity
=
no_split

boundary_token
=
native EOS / template boundary

loss_policy
=
preserve per-sample assistant mask

attention_isolation
=
framework_verified

max_sequence_length
=
follow SFTSequencePolicy_V0.1

shuffle
=
enabled

packing_algorithm
=
deterministic/versioned
```

最后两项意味着：

> Packing 过程本身也应该能够复现。

---

# 三十四、为什么 Packing Version 也值得记录？

假设实验 A：

```text
packing = false
```

实验 B：

```text
packing = true
```

或者：

```text
concatenation packing
```

改成：

```text
block-isolated packing
```

那么训练输入的实际计算结构已经发生变化。

所以实验记录最好有：

```text
packing_enabled
packing_strategy
packing_version
```

---

# 三十五、训练前一定要做一次 Packed Decode Audit

就像前面检查：

```text
input_ids
labels
```

Packing 后也应该抽几条：

> Decode。

看看是不是：

```text
Sample A
正常结束
EOS

Sample B
正常开始
...
```

而不是：

```text
Sample A回答
直接黏到
Sample B问题
```

或者：

> Assistant Mask 跨边界错位。

---

# 三十六、最好还能打印 Sample Boundary

例如：

```text
Token 0–319
sample_id = A

Token 320
EOS

Token 321–701
sample_id = B

Token 702
EOS
```

并检查：

```text
labels
attention boundary
position handling
```

这比只看：

```text
packing=True
```

可靠得多。

---

# 三十七、本阶段最危险的 6 个反例

第一，认为 Packing 就是把字符串直接 `join()`。

> 错。还涉及模板边界、Label、EOS 和 Attention。

第二，认为有 EOS 就一定不存在跨样本 Attention。

> 错。EOS 是语义边界，不自动等于数学隔离。

第三，让一个样本被随意切成两段塞进不同 Sequence。

> 很容易破坏 Prompt / Response 完整性。

第四，Packing 后重建 Loss Mask 时发生错位。

> 可能训练 User、屏蔽 Assistant，或者跨 Sample 监督。

第五，看到 `batch_size=4` 就认为一次训练只有 4 条原始样本。

> Packing 后这个直觉不成立。

第六，为追求 100% Packing Efficiency，破坏数据随机化和可复现性。

> 计算效率不能凌驾于训练语义。

---

# 三十八、现在把第 4 阶段压成最精准的 5 句话

> **第一，Packing 的目标不是改变数据，而是用真实 Token 替代 Padding，让同样的 GPU 计算更多有效训练内容。**

> **第二，一个 Packed Sequence 可以包含多条 Semantic Sample；它是计算容器，不是一条新的业务对话。**

> **第三，EOS 只表示序列边界，不自动保证 Attention 隔离；严格 Packing 还需要确认不同 Sample 的 Attention Boundary。**

> **第四，Packing 必须完整保留每条样本自己的 `input_ids / labels / Loss Mask / sample boundary`，第一版优先采用 No-split Packing。**

> **第五，Packing 以后不要只看 Samples/Batch，而应重点看 Token Utilization、Tokens per Step 和 Supervised Tokens per Step。**

这五句掌握：

> 今天最重要的东西已经拿到了。

---

# 三十九、本阶段最核心的一张图

```text
Independent Samples
独立训练样本

A
Messages → Template → Tokens → Labels
                           │
B                          │
Messages → Template → Tokens → Labels
                           │
C                          │
Messages → Template → Tokens → Labels
                           │
                           ▼
                    Packing Layer
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       Sample Boundaries            EOS Boundaries
              │                         │
              └────────────┬────────────┘
                           ▼
                 Attention Isolation
                           │
                           ▼
┌────────────────────────────────────────────┐
│ A Tokens │ EOS │ B Tokens │ EOS │ C Tokens│
└────────────────────────────────────────────┘
                           │
                           ▼
                    Packed Sequence
                           │
                           ▼
                     Less Padding
                           │
                           ▼
                  Higher Token Utilization
                           │
                           ▼
                          GPU
```

一句话：

> **独立建样本，安全做边界，高效装 Sequence。**

---

# 四十、本阶段掌握测试

现在不回看正文，你应该能够解释：Packing 和 Padding 为什么不是一回事；为什么 Packed Sequence 只是计算容器而不是新业务样本；Packing 为什么能够提高 Token Utilization；Dynamic Padding、Length Bucketing 和 Packing 分别解决什么浪费；为什么 `A + EOS + B` 不等于 A/B 在 Attention 上一定隔离；什么是 Cross-sample Attention；什么是 Block-diagonal Causal Attention；为什么 EOS Boundary 和 Attention Isolation 不是同一个概念；Packing 后为什么必须同步组合 `input_ids` 和 `labels`；为什么原有 Assistant-only Loss Mask 必须保持；为什么第一版优先采用 No-split Packing；为什么长于 `max_length` 的样本应该由 Truncation Policy 处理而不是交给 Packing 强拆；为什么 Packing 后 `batch_size=4` 不等于 4 条原始 Sample；为什么 Tokens per Step 比 Samples per Step 更适合描述 Packed Training；为什么 Training 可以 Packing，而 Evaluation 通常更适合保持独立样本；以及为什么打开 `packing=True` 之前必须弄清框架到底采用普通拼接还是严格 Sample Isolation。

如果这些都能自己讲出来：

\[
\boxed{
第五课第4阶段真正掌握
}
\]

---

# 本阶段最后只记一句话

> **Packing 的本质，是在不改变每条训练样本语义和监督边界的前提下，把多个短 Sample 安全装进同一个固定长度 Sequence，用真实训练 Token 替代 Padding；真正专业的 Packing 不只是“拼起来”，而是同时守住 Sample Boundary、EOS、Loss Mask 和 Attention Isolation。**

---

# 下一阶段：第五课 · 第 5 阶段
# Full Fine-Tuning 与 PEFT
## 为什么一个 7B / 14B 模型明明有几十亿参数，我们却往往只训练其中极少的一部分？

到目前为止我们已经把：

```text
专家数据
↓
Chat Template
↓
Loss Mask
↓
Forward / Backward
↓
Sequence Length
↓
Truncation / Padding
↓
Packing
```

全部弄清楚。

下一阶段开始进入真正的：

# 参数训练策略

核心问题会变成：

> **为什么“不训练整个模型”，反而可能是政府采购项目第一版更合理的工程选择？**

---
