# 第五课 · 第 3 阶段
# 训练样本长度、Truncation 与 Padding
## 为什么一条内容完全正确的数据，也可能因为长度处理错误而被训练坏？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **每条训练样本都应该做成 32K。**
2. **一次序列允许使用的最大 Token 空间。**
3. **32K Context**
4. **业务所需上下文 + Response长度 + 显存 + 训练速度 + Batch Size**
5. **第一，Context Window 是模型容量上限，不等于所有训练样本都应该使用最大长度。**
6. **第二，Truncation 本质是信息优先级决策；优先保护 Target Clause、决定判断的上下文和完整 Assistant Response。**
7. **第三，真正专业的顺序是 Context Selection → Tokenize → 必要 Truncation，而不是把完整文档 Tokenize 后粗暴切头或切尾。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Padding` | 补齐：把不同长度序列补到统一批次长度 |
| `Truncation` | 截断：超过最大长度时裁掉部分 Token |
| `Loss` | 损失函数：把预测错误压缩成可优化的数值信号 |
| `SFT` | 监督微调：用监督样本继续更新模型参数 |
| `Gradient` | 梯度：损失对参数变化方向和敏感度的局部信息 |
| `Step` | 训练步：通常指一次优化器更新 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Response` | 目标响应：希望模型学习生成的答案部分 |
| `Batch` | 批次：一次参与计算的一组样本 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |
| `Attention` | 注意力：根据内容相关性动态聚合信息 |
| `Sample` | 样本：具有明确输入、目标和来源的一条训练/评测记录 |

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

第 2 阶段我们解决了：

> **一次 SFT Step 怎样从预测产生 Loss，再通过 Gradient 改变参数。**

现在进入真正训练前的另一个高风险环节：

> **样本到底怎样装进模型的 Context Window？**

政府采购数据天然长短差异很大：

```text
短条款        80 Tokens
普通案例      500 Tokens
带上下文案例  2,000 Tokens
复杂案例      6,000 Tokens
完整文档      数万 Tokens
```

但模型一次能接收的 Token 数量：

> **不是无限的。**

如果这里处理错误，最危险的情况不是程序报错。

而是：

> **程序正常训练，但关键证据或专家答案已经被悄悄截掉。**

本阶段最终形成：

# `SFTSequencePolicy_V0.1`

---

# 一、本阶段只解决一个核心问题

> **怎样在有限 Context Window 和 GPU 显存下，尽量完整保留决定专家判断的关键信息，同时把不同长度的 SFT 样本安全组成 Batch？**

先记住整个流程：

```text
Semantic Example
原始SFT样本
      │
      ▼
Chat Template
      │
      ▼
Tokenize
      │
      ▼
Measure Length
计算Token长度
      │
      ▼
Length Policy
长度策略
      │
      ├───────────────┐
      ▼               ▼
长度允许           超过限制
      │               │
      │               ▼
      │          Truncation
      │             截断
      │               │
      └───────┬───────┘
              ▼
           Padding
             补齐
              │
              ▼
       Attention Mask
          注意力掩码
              │
              ▼
          Batch Tensor
              │
              ▼
             GPU
```

压缩成一句：

> **先测长度，再决定截什么，最后只把 Batch 补到必要长度。**

---

# 二、今天只锁死 5 个核心心智模型

## 心智模型 1：Context Window 是“容量上限”，不是推荐你每条都塞满

假设模型支持：

```text
32K Context
```

不意味着：

> 每条训练样本都应该做成 32K。

它只表示：

> **一次序列允许使用的最大 Token 空间。**

真正训练长度还受：

```text
业务所需上下文
+
Response长度
+
显存
+
训练速度
+
Batch Size
```

共同决定。

所以：

\[
\boxed{
ModelMaxContext
\neq
TrainingSequenceLength
}
\]

---

## 心智模型 2：Truncation 不是“删掉多余文本”，而是在做信息取舍

# Truncation
## 截断

一旦样本过长，我们其实是在回答：

> **这条数据中什么最值得留下？**

如果机械：

```text
超过2048
→
直接从右边砍掉
```

可能恰好把：

> Assistant 专家答案砍没了。

如果机械从左边砍：

> 又可能把决定判断的采购条件砍掉。

所以：

\[
\boxed{
Truncation
=
InformationPrioritization
}
\]

不是单纯数组裁剪。

---

## 心智模型 3：Response 通常比“可有可无的上下文”更应该保护

对 SFT 来说：

```text
Prompt
=
条件

Response
=
监督目标
```

如果 Response 被截断：

> 模型根本学不到完整答案。

所以我们第一版 ProcurementLM 一个重要原则是：

# Response Preservation
## 优先保护目标答案

通常应该：

> 先删低价值 Context，再考虑缩短 Response。

---

## 心智模型 4：Padding 只负责“对齐形状”，不应该变成模型要学习的内容

一个 Batch 可能有：

```text
Sample A = 500 Tokens
Sample B = 900 Tokens
Sample C = 1,400 Tokens
```

GPU Tensor 需要规则矩阵。

所以短样本会补：

```text
<PAD>
```

但 PAD：

> 不是业务文本。

所以一般必须：

```text
attention_mask = 0
```

同时其 Label：

```text
-100
```

也就是说：

\[
\boxed{
Padding
\neq
TrainingContent
}
\]

---

## 心智模型 5：训练效率看的是“实际计算了多少 Token”，不是只有样本数量

假设两套数据：

```text
Dataset A
10,000 Samples
平均 300 Tokens
```

和：

```text
Dataset B
10,000 Samples
平均 3,000 Tokens
```

它们都叫：

> 10,000 条数据。

但计算量：

> 完全不是一个量级。

所以以后谈训练规模：

> **不能只报 Samples。**

还要看：

```text
Total Tokens
Average Length
Length Distribution
Effective Tokens
```

---

# 三、先精准区分四个经常混在一起的概念

| 概念 | 精准含义 |
|---|---|
| **Context Window** | 模型允许处理的最大序列容量 |
| **Sequence Length** | 当前训练样本实际 Token 数 |
| **Truncation** | 样本过长时删除部分 Token |
| **Padding** | Batch 中短样本补齐到统一长度 |

最容易混淆的是：

> Truncation 是处理“太长”。

> Padding 是处理“同一 Batch 长短不同”。

两者完全不是一件事。

---

# 四、政府采购 SFT 的长度，到底由哪些东西组成？

一个训练样本通常不是只有采购条款。

可能是：

```text
System Prompt
+
Task Instruction
+
Document Metadata
+
Section Context
+
Target Clause
+
Neighbor Clauses
+
Assistant Response
+
Special Tokens
```

因此：

\[
L_{\text{total}}
=
L_{\text{system}}
+
L_{\text{user}}
+
L_{\text{response}}
+
L_{\text{special}}
\]

其中真正决定能不能塞进去的：

> 是 Token 数。

不是：

> 中文字符数。

---

# 五、为什么不能拿“字数”代替 Token 数？

因为 Tokenizer 不一定：

```text
1个汉字 = 1 Token
```

英文：

```text
supplier qualification
```

数字：

```text
2026-09-16
```

特殊符号、表格、代码：

> Token 化方式都可能不同。

所以任何长度治理：

\[
\boxed{
MeasureAfterTokenization
}
\]

都应该基于：

> **真实 Tokenizer 输出。**

不要说：

> “这条大概 2000 字，所以肯定小于 2048 Token。”

这不可靠。

---

# 六、真正危险的是哪里？

假设我们设：

```text
max_length = 2048
```

完整样本：

```text
System          100
User Context   1900
Response        300
Special Tokens   20
──────────────────
Total          2320
```

超了：

```text
272 Tokens
```

如果直接：

```text
tokenizer(
    truncation=True,
    max_length=2048
)
```

并默认从右边截，

可能得到：

```text
System        完整
User          完整
Response      只剩前28 Tokens
```

训练仍然能跑。

甚至 Loss：

> 看起来正常。

但模型真正学到的可能只是：

```text
风险判断：存在潜在风险。
风险类型……
```

而关键：

```text
理由
证据
复核条件
```

全被砍掉了。

这就是：

# Silent Data Corruption
## 静默数据破坏

---

# 七、所以第一原则：先给 Response 留预算

假设：

```text
max_length = 4096
```

不要直接让 Prompt 无限扩张到：

```text
4090
```

然后给 Response 剩几个 Token。

更专业的做法是先定义：

```text
Response Reserve
```

例如：

```text
总预算             4096
预留Response         800
特殊Token             50
────────────────────────
Prompt最大预算       3246
```

即：

\[
L_{\text{prompt}}
\le
L_{\max}
-
L_{\text{response reserve}}
-
L_{\text{special}}
\]

这叫：

# Length Budget
## Token 长度预算

---

# 八、但“永远固定预留 800”也不是最终答案

真正应该根据数据统计决定。

第四课的数据出来以后，可以先统计：

```text
Response P50
Response P90
Response P95
Response P99
```

例如：

```text
50% Response ≤ 260 Tokens
90% Response ≤ 520 Tokens
95% Response ≤ 680 Tokens
99% Response ≤ 1100 Tokens
```

那么我们就有依据决定：

> Response Budget 到底设置多少。

而不是拍脑袋。

---

# 九、Length Distribution 是训练前必须看的第一张数据图

至少应该统计：

```text
Prompt Length

Response Length

Total Length
```

并看：

```text
P50
P90
P95
P99
Max
```

例如：

| 指标 | Prompt | Response | Total |
|---|---:|---:|---:|
| P50 | 620 | 240 | 880 |
| P90 | 1,850 | 520 | 2,410 |
| P95 | 2,700 | 680 | 3,420 |
| P99 | 6,300 | 1,050 | 7,420 |

看到这张表以后：

> `max_length=4096` 才开始有业务意义。

---

# 十、不要盲目追求覆盖 100% 样本

假设：

```text
99%样本 < 8K
```

但为了最后：

```text
1%
```

极端长样本，把全体训练长度提高到：

```text
32K
```

可能导致：

```text
显存大幅增加
Batch Size下降
训练速度下降
总成本上升
```

这通常不是好交易。

所以长度策略本质上是：

\[
\boxed{
Coverage
\leftrightarrow
ComputeCost
}
\]

之间的工程权衡。

---

# 十一、为什么长序列特别贵？

Transformer Attention 的经典计算复杂度近似：

\[
O(n^2)
\]

其中：

\[
n
=
SequenceLength
\]

直觉上：

如果从：

```text
2K
```

增长到：

```text
4K
```

Attention 相关计算并不是简单只变成 2 倍。

经典全注意力部分可能接近：

\[
2^2=4
\]

倍级别增长。

真实现代实现会受到：

```text
FlashAttention
模型结构
硬件
KV实现
```

等影响。

但长期心智模型应该是：

> **长序列非常贵。**

---

# 十二、所以“把所有上下文都塞进去”通常不是专业方案

例如一个 Clause：

```text
供应商应……
```

真正需要判断它的可能只是：

```text
父章节标题
+
前后2个相关条款
+
项目类型
```

而不是：

> 整份 180 页采购文件。

所以第四课 Stage 3 的：

# Minimal Sufficient Context
## 最小充分上下文

到第五课现在真正产生训练价值。

原则是：

\[
\boxed{
KeepEnoughContext
\neq
KeepAllContext
}
\]

---

# 十三、我们应该怎样决定“截什么”？

对政府采购 SFT，可以建立优先级。

## 第一优先级：绝不能轻易丢

```text
Target Clause
Assistant Response
决定判断的关键上下文
```

---

## 第二优先级：尽量保留

```text
父章节
紧邻条款
必要项目属性
```

---

## 第三优先级：可优先裁剪

```text
重复背景
远距离无关条款
 boilerplate
冗长模板说明
无关目录
```

所以不要：

```text
从左边砍
```

或者：

```text
从右边砍
```

作为唯一策略。

更专业的是：

# Structure-aware Truncation
## 结构感知截断

---

# 十四、举一个具体例子

原 Prompt：

```text
项目名称
采购方式
采购背景
完整技术需求
大量无关条款
……
目标章节
目标条款
前后相关条款
```

如果超长，

不应该机械：

```text
保留前2048 Tokens
```

因为这样：

> Target Clause 甚至可能直接消失。

应该优先组织成：

```text
必要Metadata
      ↓
父章节
      ↓
关键前文
      ↓
Target Clause
      ↓
关键后文
```

再按信息价值裁剪。

---

# 十五、这叫“先组织，再截断”

非常重要。

错误流程：

```text
整个Document
↓
Tokenize
↓
超长
↓
砍
```

更好的流程：

```text
Document Structure
↓
Context Selection
↓
Prompt Assembly
↓
Tokenize
↓
必要时最后安全Truncate
```

所以：

\[
\boxed{
SelectionBeforeTruncation
}
\]

通常优于：

\[
RandomTruncation
\]

---

# 十六、Response 本身太长怎么办？

也不能一律无限保留。

假设专家答案：

```text
3500 Tokens
```

但其中：

```text
前500 Tokens
是真正判断

后3000 Tokens
是重复解释
```

此时正确做法不是：

> 偷偷砍掉。

而应该回到：

# Target Design
## 输出目标设计

问：

> 我们到底希望 ProcurementLM 生成多长的回答？

例如把第一版输出设计稳定成：

```text
1. 风险判断
2. 风险类型
3. 核心理由
4. 需要补充的上下文
5. 是否人工复核
```

让回答：

> 信息密度更高。

这是数据设计问题，

不只是 Truncation 问题。

---

# 十七、这也是为什么结构化 Response 很重要

例如：

```text
风险判断：uncertain

风险类型：supplier_qualification

核心理由：
……

需补充信息：
……

建议：
human_review
```

相比漫无边际的长 essay：

> 更容易控制长度，也更容易评测。

所以：

\[
\boxed{
StructuredOutput
\rightarrow
BetterLengthControl
}
\]

---

# 十八、现在进入 Padding

假设 Batch 里有三条 Token 序列：

```text
A = 6 Tokens
B = 9 Tokens
C = 12 Tokens
```

Tensor 不能直接长成：

```text
[6]
[9]
[12]
```

所以通常要补成：

```text
A = 12
B = 12
C = 12
```

短的地方：

```text
<PAD>
```

---

# 十九、概念上变成

```text
A:
[a b c d e f PAD PAD PAD PAD PAD PAD]

B:
[a b c d e f g h i PAD PAD PAD]

C:
[a b c d e f g h i j k l]
```

这叫：

# Padding

目的只有一个：

> **让 Batch 形成规则 Tensor。**

---

# 二十、Attention Mask 到底做什么？

对真实 Token：

```text
1
```

对 PAD：

```text
0
```

例如：

```text
input_ids

[a b c PAD PAD]
```

对应：

```text
attention_mask

[1 1 1 0 0]
```

告诉模型：

> 后两个位置不是正常上下文内容。

---

# 二十一、Loss Mask 和 Attention Mask 必须彻底分开

这是本阶段最容易混淆的一对。

## Attention Mask

解决：

> **模型在 Attention 计算中哪些位置属于有效序列？**

---

## Loss Mask

解决：

> **哪些目标位置参与 Loss？**

两者不同。

例如 Prompt：

```text
User:
请判断……
```

它：

```text
attention_mask = 1
```

因为：

> 模型必须看见。

但：

```text
label = -100
```

因为：

> 不要求它学习生成 User Prompt。

因此：

\[
\boxed{
AttentionMask
\neq
LossMask
}
\]

---

# 二十二、这张表必须掌握

| Token 类型 | Attention | Loss |
|---|---:|---:|
| System Prompt | 1 | 通常不算 |
| User Prompt | 1 | 通常不算 |
| Assistant Response | 1 | 算 |
| PAD | 0 | 不算 |

这就是最清楚的四区域模型。

---

# 二十三、Padding Token 为什么也要从 Loss 排除？

假设：

```text
PAD PAD PAD PAD
```

也参与 Loss。

那么模型会浪费学习能力：

> 学会预测 Padding。

这不是我们想要的专业行为。

所以 PAD 一般：

```text
attention_mask = 0
```

并且：

```text
labels = -100
```

---

# 二十四、Padding 最大的工程问题不是正确性，而是浪费

假设一个 Batch：

```text
最长样本 = 8000
```

其他样本：

```text
600
700
900
1000
```

如果全部 Padding 到：

```text
8000
```

会产生大量：

# Padding Waste
## 补齐浪费

GPU 进行了很多没有业务价值的计算。

---

# 二十五、所以通常不要每条都 Padding 到全局最大长度

例如全局：

```text
max_length = 8192
```

并不意味着所有 Batch 都必须：

```text
pad_to_8192
```

更常用的是：

# Dynamic Padding
## 动态补齐

一个 Batch：

> 只补到这个 Batch 当前最长样本附近。

---

# 二十六、例如

Batch A：

```text
510
620
680
750
```

只补到：

```text
750
```

左右。

Batch B：

```text
1800
1900
2200
2400
```

补到：

```text
2400
```

而不是所有样本：

```text
8192
```

这会节省大量计算。

---

# 二十七、但 Dynamic Padding 还有进一步优化

如果一个 Batch 随机抽到：

```text
200
300
400
7000
```

还是很浪费。

于是可以做：

# Length Bucketing
## 按长度分桶

大致：

```text
短样本和短样本组成Batch

中样本和中样本组成Batch

长样本和长样本组成Batch
```

这样：

> Padding 少很多。

---

# 二十八、这就是一个很重要的效率链

```text
Measure Length
      ↓
Length Bucket
      ↓
Batch Similar Lengths
      ↓
Dynamic Padding
      ↓
Less Padding Waste
      ↓
Higher GPU Utilization
```

这比：

> 单纯疯狂调 CUDA 参数

往往更值得先做。

---

# 二十九、现在看一个特别重要的指标

# Padding Ratio
## Padding 占比

可以定义一个直觉指标：

\[
PaddingRatio
=
\frac{PaddingTokens}
{TotalBatchTokens}
\]

例如：

```text
一个Batch总Tensor位置
=
32,000

真实Token
=
20,000

PAD
=
12,000
```

那么：

\[
PaddingRatio
=
37.5\%
\]

意味着：

> 很大一部分计算位置没有承载真实训练内容。

---

# 三十、另外一个更重要的训练规模指标：有效监督 Token

一条样本可能：

```text
Prompt = 1800 Tokens
Response = 200 Tokens
```

总共：

```text
2000
```

但真正计算 Loss 的：

> 可能只有 Response 的约 200 Tokens。

所以还可以关注：

# Supervised Token Ratio
## 有效监督 Token 占比

\[
SupervisedRatio
=
\frac{LossTokens}
{NonPaddingTokens}
\]

在这个例子：

\[
\frac{200}{2000}
=
10\%
\]

这不一定说明错误。

但是它告诉我们：

> 大量计算都在提供 Context，真正监督信号集中在少数 Response Token。

---

# 三十一、这对政府采购数据特别重要

如果 Prompt：

```text
7000 Tokens
```

Response：

```text
100 Tokens
```

那么训练成本很高，

但直接监督非常稀疏。

这时候应该问：

> 那 7000 Tokens 真的都必要吗？

如果不是：

> 应该优化 Context Selection。

不是单纯增加 GPU。

---

# 三十二、长度问题真正的核心不是“能不能塞进去”

而是：

\[
\boxed{
InformationDensity
}
\]

即：

> 每一个投入计算的 Token，到底贡献了多少任务相关信息？

高质量训练数据应该尽量：

```text
少冗余
+
足够上下文
+
完整目标
```

而不是：

> 越长越专业。

---

# 三十三、现在讨论 Left Padding 和 Right Padding

例如真实内容：

```text
ABC
```

Right Padding：

```text
A B C PAD PAD
```

Left Padding：

```text
PAD PAD A B C
```

不同模型 / 训练框架：

> 可能有不同推荐。

---

# 三十四、训练阶段最重要的不是死记 left/right

而是：

> **遵循当前 Base Model、Tokenizer 和 Training Framework 的预期。**

因为这还涉及：

```text
Position IDs
Causal Mask
Generation behavior
```

所以不能简单说：

> “所有模型训练都必须左 Padding。”

或者：

> “全部必须右 Padding。”

---

# 三十五、但有一个长期不变的原则

无论 Left 还是 Right：

> PAD 都必须被正确 Mask。

否则它就从：

> 形状补齐工具

变成：

> 假训练数据。

---

# 三十六、现在建立第一版 ProcurementLM 的长度策略

我们先不追求极复杂。

推荐第一版逻辑：

```text
1
统计真实Token长度分布

2
确定训练 max_length

3
给 Assistant Response 留安全预算

4
优先通过结构化 Context Selection 减少 Prompt

5
只在最后一步做必要 Truncation

6
保证 Target Clause 不被截掉

7
保证 Response 关键字段完整

8
使用 Dynamic Padding

9
尽量按相近长度组 Batch

10
训练前抽样 Decode 检查
```

这是够专业、又不复杂的 V0.1 策略。

---

# 三十七、真正的 Truncation Policy 可以这样定义

假设超长。

裁剪顺序：

```text
Level 1
删除无关 Boilerplate

      ↓

Level 2
缩减远距离 Context

      ↓

Level 3
只保留最近的必要 Neighbor Clauses

      ↓

Level 4
压缩非关键 Metadata

      ↓

Level 5
仍然过长
→ 标记 special_long_case
→ 单独处理
```

而不是：

```text
直接砍最后N个Tokens
```

---

# 三十八、有些样本根本就不应该被“硬截”

例如一个专家结论必须依赖：

```text
第一页资格条件
+
第45页技术要求
+
第92页评分标准
```

如果把它简单压到：

```text
2048 Tokens
```

可能无论怎么截都不合理。

那么正确策略可能是：

```text
重新设计Sample
```

或者：

```text
任务拆分
```

或者：

```text
交给RAG / 长上下文架构
```

而不是：

> 强行做成一个 SFT Sample。

---

# 三十九、这是非常重要的边界

\[
\boxed{
NotEveryDocument
ShouldBecome
OneSFTSequence
}
\]

完整文档：

> 是信息载体。

SFT Sample：

> 是训练单元。

两者不是同一个东西。

这和第四课第一阶段：

> File ≠ Sample

完全一致。

---

# 四十、所以面对超长政府采购文档，有三种不同问题

## 问题 A：局部条款判断

需要：

```text
Target Clause
+
Local Context
```

适合：

> SFT。

---

## 问题 B：跨章节证据检索

需要从长文档中找证据。

更适合：

> RAG。

---

## 问题 C：整份项目综合审查

可能需要：

```text
RAG
+
多阶段推理
+
规则
+
模型
```

而不是：

> 把整本采购文件塞成一条训练样本。

这个职责边界以后第 6 课会再次出现。

---

# 四十一、Truncation 以后必须留下审计信息

不要只生成：

```text
final_input_ids
```

最好还能知道：

```text
original_length
final_length
was_truncated
truncated_tokens
truncation_policy
response_truncated
```

例如：

```json
{
  "sample_id": "SAMPLE-00178",
  "original_tokens": 5230,
  "final_tokens": 4096,
  "was_truncated": true,
  "response_truncated": false,
  "truncation_policy": "context_priority_v0.1"
}
```

为什么？

因为以后发现某类案例效果很差时：

> 可以检查是不是长期被截坏了。

---

# 四十二、特别要监控 `response_truncated`

对我们第一版：

```text
response_truncated = true
```

应该是：

> 高风险事件。

对于 Gold SFT 数据，通常应该尽量做到：

\[
\boxed{
GoldResponseTruncation
=
0
}
\]

至少：

> 不能悄悄发生。

如果不得不发生：

> 应该重新设计 Sample 或 Response。

---

# 四十三、Target Clause 被截掉更加荒唐

Prompt 很长，但真正任务是：

```text
请判断目标条款……
```

结果经过 Truncation：

```text
目标条款
```

没了。

模型实际看到：

```text
大量背景
+
请判断以下条款
```

却没有条款。

程序仍可能训练。

所以还必须检查：

# Required Span Preservation
## 必需片段保留

例如：

```text
Target Clause present = true
```

---

# 四十四、因此长度治理不应该只做“数字校验”

还应该做：

# Semantic Integrity Check
## 语义完整性检查

确认截断后仍然包含：

```text
Task Instruction
Target Clause
Required Context
Assistant Target
Termination Token
```

这比单纯：

```text
len <= 4096
```

重要得多。

---

# 四十五、我们现在可以定义一个简单的 Sequence Contract

每条训练样本必须满足：

```text
1. total_tokens <= max_length

2. target_clause preserved

3. response preserved

4. response has valid termination

5. pad tokens not supervised

6. prompt tokens readable by attention

7. prompt loss policy correct
```

这叫：

# Sequence Contract

以后训练代码：

> 必须满足这份合同。

---

# 四十六、现在把长度策略放回完整 SFT 流程

第 1 阶段：

```text
Messages
↓
Chat Template
↓
Tokenization
↓
Loss Mask
```

第 2 阶段：

```text
Forward
↓
Loss
↓
Backward
↓
Update
```

今天在两者中间补上：

```text
Tokenization
      ↓
Length Measurement
      ↓
Context Selection
      ↓
Truncation
      ↓
Padding
      ↓
Attention Mask
      ↓
Batch
      ↓
Forward
```

至此：

> 数据终于真正能够安全进入 GPU。

---

# 四十七、本阶段最危险的 6 个反例

**反例 1：所有样本统一截到前 2048 Tokens。**  
结果可能直接丢掉目标条款或 Response。

**反例 2：为了“不丢信息”，所有数据都训练 32K。**  
结果可能造成巨大的计算浪费，却没有增加有效信息。

**反例 3：Padding 到全局 max_length。**  
大量 GPU 算力花在 PAD 上。

**反例 4：把 Attention Mask 和 Loss Mask 当成同一个东西。**  
Prompt 要看但通常不评分；PAD 既不应该正常参与注意力，也不应该算 Loss。

**反例 5：只检查 `len <= max_length`。**  
长度合规，但 Target Clause 已经消失。

**反例 6：Response 被截断以后仍然当 Gold 样本训练。**  
这等于主动制造残缺专家答案。

---

# 四十八、现在把整个阶段压成 5 句话

如果明天只记住五句话：

> **第一，Context Window 是模型容量上限，不等于所有训练样本都应该使用最大长度。**

> **第二，Truncation 本质是信息优先级决策；优先保护 Target Clause、决定判断的上下文和完整 Assistant Response。**

> **第三，真正专业的顺序是 Context Selection → Tokenize → 必要 Truncation，而不是把完整文档 Tokenize 后粗暴切头或切尾。**

> **第四，Padding 只用于 Batch 对齐；Attention Mask 决定哪些位置属于有效输入，Loss Mask 决定哪些位置参与监督，两者不能混。**

> **第五，训练效率应该同时看 Total Tokens、Padding Ratio 和有效监督 Token，而不能只看“有多少条数据”。**

这就是今天的核心。

---

# 四十九、本阶段工程产物

我们正式形成：

# `SFTSequencePolicy_V0.1`

至少应该记录：

```text
max_sequence_length

prompt_budget

response_budget

context_selection_policy

truncation_policy

padding_policy

padding_side

attention_mask_policy

loss_mask_policy

required_spans

long_case_policy
```

每条派生样本还应记录：

```text
original_token_length
final_token_length
was_truncated
response_truncated
padding_tokens
supervised_tokens
```

这样长度策略：

> 才是可复现的数据工程规则。

---

# 五十、本阶段最核心的一张图

```text
ProcurementDataset_V0.1
        │
        ▼
   SFT Messages
        │
        ▼
   Chat Template
        │
        ▼
     Tokenizer
        │
        ▼
   Measure Length
        │
        ▼
 ┌─────────────────┐
 │ Sequence Policy │
 └───────┬─────────┘
         │
         ├──── 保护 Target Clause
         │
         ├──── 保护 Response
         │
         ├──── 删除低价值 Context
         │
         ▼
     Truncation
      必要时才截
         │
         ▼
    Length Bucket
         │
         ▼
 Dynamic Padding
         │
         ▼
 ┌─────────────────────────┐
 │ input_ids               │
 │ attention_mask          │
 │ labels                  │
 └───────────┬─────────────┘
             │
             ▼
            GPU
             │
             ▼
          Forward
```

脑中记一句：

> **保护信息，控制长度，减少空算。**

---

# 五十一、本阶段掌握测试

现在不回看正文，你应该能自己解释：Context Window 和 Training Sequence Length 为什么不是一回事；为什么字符数不能代替真实 Token 数；为什么超长样本不能简单从左或右机械截断；为什么 Assistant Response 通常应该获得独立 Token Budget；为什么 Target Clause 必须被当作 Required Span；为什么完整政府采购文件不应该天然等于一条 SFT Sequence；为什么 Context Selection 应该发生在粗暴 Truncation 之前；Padding 为什么存在；Dynamic Padding 为什么比全部 Pad 到全局最大长度高效；Length Bucketing 怎样减少计算浪费；Attention Mask 和 Loss Mask 有什么根本区别；为什么 User Prompt 可以 `attention_mask=1` 但 `label=-100`；为什么 PAD 通常两边都应该被排除；什么是 Padding Ratio；什么是 Supervised Token Ratio；为什么长 Prompt + 极短 Response 值得重新审查信息密度；以及为什么 `response_truncated=true` 对 Gold SFT 数据应该被视为高风险事件。

如果这些能够讲清楚：

\[
\boxed{
第五课第3阶段真正掌握
}
\]

---

# 本阶段最后只记一句话

> **SFT 的长度工程不是“把所有样本强行裁成同样长”，而是在有限 Context Window 和 GPU 预算下，优先保留真正决定判断的采购条件与完整专家 Response，通过结构化 Context Selection、可审计 Truncation、Length Bucketing 和 Dynamic Padding，把尽可能高的信息密度变成尽可能少的无效计算。**

---

# 下一阶段：第五课 · 第 4 阶段
# Packing：怎样减少 GPU 浪费？

今天我们解决：

> **单条样本太长怎么办，以及一个 Batch 长短不一怎么办。**

下一阶段会进一步解决一个相反的问题：

```text
很多样本只有
120 Tokens
180 Tokens
240 Tokens
```

但我们设置的训练序列可能允许：

```text
2048 / 4096 Tokens
```

如果每条短样本都独占一个完整训练 Sequence：

> GPU 又会出现另一种巨大浪费。

下一阶段我们会把：

```text
Sample A
Sample B
Sample C
Sample D
```

安全地组合进同一条训练 Sequence，并真正弄清：

> **Packing 为什么能显著提升吞吐量，以及怎样避免不同样本之间互相“串台”。**

---
