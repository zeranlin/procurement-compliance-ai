# 第三课 · 第 5 阶段：第一次真正让一个开源 LLM 从“文字输入”走到“文字输出”
## 一条政府采购条款，究竟怎样变成 Token、Tensor、Logits，再重新变成中文回答？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **完整生成链是 Text → Token IDs → Tensor → Forward → Logits → Decode，不应把“文字直接进入神经网络”当作真实过程。**
2. **generate() 本质是 Autoregressive Loop：反复 Forward、选择下一个 Token、追加到序列再继续。**
3. **Tokenizer / Chat Template 是输入协议的一部分；协议不一致会让同一模型表现明显变化。**
4. **Logits ≠ Final Text。Logits 只是下一 Token 的分数，解码策略决定如何从分数得到实际 Token。**
5. **推理时要区分 eval()/no_grad() 与训练状态，避免无谓梯度和随机层行为影响结果与显存。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Token` | Token：模型实际处理的离散文本单元 |
| `Tokenizer` | 分词器：文本与 Token ID 之间的编码/解码组件 |
| `Input` | 输入：模型在当前任务中允许看到的条件信息 |
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `Transformer` | Transformer：以注意力和前馈网络为核心的序列架构 |
| `Attention` | 注意力：根据内容相关性动态聚合信息 |
| `CPU` | CPU：负责通用控制、数据准备和部分算子 |
| `Embedding` | 嵌入：把离散 Token 映射到连续高维向量 |
| `CUDA` | CUDA：NVIDIA GPU 通用并行计算平台与软件生态 |
| `Batch` | 批次：一次参与计算的一组样本 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |
| `Block` | 版面块：文档解析后保留布局和位置的基本块 |

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

前四个阶段，我们一直在准备“发动机”。

第三课第 1 阶段，我们知道了：

```text
SSD → RAM → VRAM → GPU
```

第 2 阶段，我们知道了：

```text
Transformers
↓
PyTorch
↓
CUDA
↓
Driver
↓
GPU
```

第 3 阶段，我们打开了模型文件夹：

```text
config
+
tokenizer
+
weights
```

第 4 阶段，我们终于知道：

```python
from_pretrained(...)
```

背后实际上是在做一场大型搬家。

现在模型已经：

> **真正装进电脑里了。**

这一阶段我们只解决一个问题：

> **用户输入一句中文以后，这句话到底经历了什么，最后才变成模型回答？**

这次不先讲代码。

先把整个过程变成一部“流水线电影”。

---

# 一、先看最终总图

假设用户输入：

> **“请审查：供应商注册资本不得低于5000万元。”**

它不会直接进入 Transformer。

真正发生的是：

```text
用户中文
   │
   ▼
Tokenizer
   │
   ▼
Token IDs
   │
   ▼
PyTorch Tensor
   │
   │ 搬到GPU
   ▼
Transformer
   │
   ▼
Logits
   │
   ▼
选择下一个Token
   │
   ▼
把新Token接到原序列后面
   │
   ▼
再次运行模型
   │
   ▼
继续生成
   │
   ▼
一串Token IDs
   │
   ▼
Tokenizer Decode
   │
   ▼
中文回答
```

这一阶段真正要留下 **5 个核心心智模型**。

---

# 二、本阶段的 5 个核心心智模型

### 心智模型 ①

\[
\boxed{
模型从来没有直接看到“文字”
}
\]

它真正收到的是：

> **Token ID Tensor。**

---

### 心智模型 ②

\[
\boxed{
Tokenizer负责翻译，
Transformer负责计算
}
\]

一个解决：

> “文字怎么编码？”

另一个解决：

> “这些编码之间怎么计算？”

---

### 心智模型 ③

\[
\boxed{
模型输出的不是中文，
而是一整张“下一个Token候选评分表”
}
\]

这个评分表就是：

# Logits

---

### 心智模型 ④

\[
\boxed{
generate()
不是一次生成整段答案，
而是反复执行：
预测一个Token → 接回去 → 再预测
}
\]

---

### 心智模型 ⑤

\[
\boxed{
Encode和Decode是Tokenizer的两个方向
}
\]

```text
文字 → Token IDs
叫 Encode

Token IDs → 文字
叫 Decode
```

先把这五根柱子立起来。

---

# 三、第一步：用户输入的其实只是一个普通字符串

## 1. 最开始，模型还没有参与

用户输入：

```text
请审查以下资格条件：
供应商注册资本不得低于5000万元。
```

在 Python 中，它一开始只是：

```python
text = "请审查以下资格条件：供应商注册资本不得低于5000万元。"
```

这时候它通常存在：

> CPU 侧的普通内存。

也就是：

# RAM

---

## 2. GPU 现在还不知道这句话是什么

GPU 不理解：

> “供应商”

也不理解：

> “注册资本”

甚至不理解：

> 汉字是什么。

GPU 擅长的是：

> 数字计算。

所以第一件事必须是：

\[
\boxed{
文字
\rightarrow
数字
}
\]

---

# 四、Tokenizer 出场

第二课已经学过 Tokenizer。

这里不再重新推 BPE。

今天只问：

> **实际运行时它到底干什么？**

---

## 3. Tokenizer 拿到字符串

例如：

```text
供应商注册资本不得低于5000万元
```

可能切成若干 Token。

为了方便理解，我们用完全虚构的示意：

```text
供应商
注册资本
不得
低于
5000
万元
```

真实模型怎么切：

> 由它自己的 Tokenizer 决定。

---

## 4. 然后每个 Token 对应一个 ID

例如仍然只是示意：

```text
供应商   →  18452
注册资本 →  76103
不得     →  9321
低于     →  4178
5000     →  550
万元     →  23891
```

于是：

```text
“供应商注册资本不得低于5000万元”
```

变成：

```text
[18452, 76103, 9321, 4178, 550, 23891]
```

---

# 五、这里必须建立一个非常牢固的直觉

## 5. Token ID 本身没有语义

例如：

```text
18452
```

不是：

> “供应商的数学意义”。

它只是：

> **词表里的地址。**

第二课第 8 阶段那句话仍然成立：

\[
\boxed{
TokenID=Address
}
\]

---

## 6. 真正有连续数值意义的是下一步

模型用这个 ID：

> 去 Embedding Matrix 中取对应向量。

例如概念上：

```text
Token ID 18452
        ↓
Embedding表第18452行
        ↓
一个几千维向量
```

---

# 六、Tokenizer 实际返回的不只是 ID 列表

以后你会经常写：

```python
inputs = tokenizer(text, return_tensors="pt")
```

你可能看到结果里有：

```text
input_ids
attention_mask
```

今天重点理解这两个。

---

# 七、`input_ids` 是什么？

## 7. 它就是刚才那些 Token ID

但是现在被整理成：

# Tensor

例如概念上：

```text
input_ids =
[[18452, 76103, 9321, 4178, 550, 23891]]
```

注意外面还有一层：

```text
[ [ ... ] ]
```

---

## 8. 为什么？

因为神经网络通常支持：

# Batch

也就是：

> 一次处理多个样本。

---

## 9. 如果只有一个样本

Shape 可能是：

```text
(1, 6)
```

可以理解成：

```text
Batch Size = 1
Sequence Length = 6
```

---

# 八、第一次用“盒子”理解 Shape

不要先想数学。

想一张表：

```text
             Token位置
          1   2   3   4   5   6

样本1    184  761  932  417  550  238
```

所以：

```text
1 行
6 列
```

就是：

```text
(1, 6)
```

---

# 九、如果一次处理三条采购条款呢？

例如：

```text
样本A：注册资本条件……
样本B：本地网点条件……
样本C：业绩条件……
```

那么可能是：

```text
Batch Size = 3
```

于是：

```text
input_ids.shape
=
(3, S)
```

---

# 十、问题来了：三句话长度不一样怎么办？

例如：

```text
A：6个Token

B：9个Token

C：5个Token
```

Tensor 通常喜欢整齐矩形。

于是可能需要：

# Padding

---

## 10. 变成

```text
A  x x x x x x PAD PAD PAD
B  x x x x x x x   x   x
C  x x x x x   PAD PAD PAD PAD
```

每一行：

> 长度统一为 9。

---

# 十一、但是模型怎么知道 PAD 不是正文？

这就需要：

# `attention_mask`

---

## 11. 可以把它理解成“座位使用表”

比如：

```text
input_ids

A：x x x x x x PAD PAD PAD
B：x x x x x x x   x   x
C：x x x x x PAD PAD PAD PAD
```

对应：

```text
attention_mask

A：1 1 1 1 1 1 0 0 0
B：1 1 1 1 1 1 1 1 1
C：1 1 1 1 1 0 0 0 0
```

---

## 12. `1` 可以先理解成

> 这是有效 Token。

`0`：

> 这是为了补齐 Shape 放进去的 Padding。

---

# 十二、不要把两种 Mask 混起来

第二课学过：

# Causal Mask

控制：

> 当前 Token 能不能看到未来 Token。

这里的：

# Padding Attention Mask

主要告诉模型：

> 哪些位置只是 PAD。

它们解决：

> 不同问题。

---

# 十三、到这里，第一段流水线完成

```text
中文字符串
     │
     ▼
Tokenizer
     │
     ├── input_ids
     │
     └── attention_mask
     │
     ▼
PyTorch Tensor
```

模型终于开始能“接货”。

---

# 十四、但是现在 Tensor 在哪里？

通常 Tokenizer：

> 主要在 CPU 上执行。

所以产生的 Tensor 一开始很可能：

```text
device = cpu
```

---

## 13. 而我们的模型 Weight 在哪里？

假设前面已经放到：

```text
cuda:0
```

于是出现：

```text
Input Tensor → CPU

Model Weight → GPU
```

不能直接正常一起计算。

---

# 十五、所以需要把输入搬过去

概念代码：

```python
inputs = inputs.to("cuda")
```

或者对里面的 Tensor：

```python
input_ids = input_ids.to("cuda")
```

---

## 14. 从硬件角度发生什么？

```text
RAM
 │
 │ Host-to-Device Transfer
 ▼
VRAM
```

于是现在：

```text
Model Weight
+
Input Tensor
```

都在 GPU。

---

# 十六、用采购会议类比

模型专家团队：

> 已经坐在 GPU 办公室。

用户材料：

> 还在 CPU 办公室。

你不能说：

> “开始审查！”

材料得先：

```text
CPU办公室
    ↓
送文件
    ↓
GPU办公室
```

专家才能真正工作。

---

# 十七、现在真正进入 Transformer

## 15. `input_ids` 进入 Embedding

例如：

```text
18452
```

会找到：

> Embedding Matrix 对应 Row。

于是：

```text
Token ID
↓
Vector
```

---

## 16. 假设 Hidden Size 是 4096

原来的：

```text
input_ids
shape:
(1, 6)
```

经过 Embedding 以后：

```text
Hidden States
shape:
(1, 6, 4096)
```

---

# 十八、别被 Shape 吓到

它只是说：

```text
1个样本

6个Token

每个Token
拥有4096维表示
```

就是：

```text
Batch
×
Sequence
×
Hidden Size
```

---

# 十九、然后进入几十层 Transformer Block

脑内画面：

```text
Token Embeddings
      ↓
Block 1
      ↓
Block 2
      ↓
Block 3
      ↓
...
      ↓
Block 32
      ↓
Final Norm
```

每一层都会：

> 改写 Token Representation。

---

# 二十、这里不要再重新推 Attention

第二课已经学过。

现在只记运行意义：

```text
输入Token
↓
互相读取上下文
↓
MLP加工
↓
形成新的上下文化表示
```

---

# 二十一、到最后会得到什么？

不是文字。

还不是 Token ID。

而是：

> 每个位置最终的 Hidden State。

然后进入：

# LM Head

---

# 二十二、LM Head 做什么？

假设词表一共有：

```text
100,000 个 Token
```

模型必须回答：

> “下一个 Token 应该是哪一个？”

---

## 17. 所以最后一个位置会得到

大概：

```text
100,000 个分数
```

例如：

```text
Token A → 8.7
Token B → 2.1
Token C → -1.4
Token D → 6.3
...
```

---

# 二十三、这就是第三个核心心智模型

## 模型不会直接输出：

> “该条款可能存在风险。”

它先输出：

# Logits

可以理解成：

> **给词表里所有候选 Token 打分。**

---

# 二十四、用采购专家打分表理解 Logits

假设模型现在要生成回答的第一个 Token。

候选可能概念上有：

```text
“该”      8.7

“存在”    7.9

“根据”    6.2

“未”      3.4

“采购人”  1.7

……
```

模型不是先“写完一整句话”。

它只是：

> 对下一步所有候选 Token 打分。

---

# 二十五、这里最值得记的一句话

\[
\boxed{
LLM每一步面对的核心问题不是
“整段答案是什么？”
而是
“下一个Token是什么？”
}
\]

---

# 二十六、为什么输出 Shape 很大？

假设：

```text
Batch = 1

Sequence = 20

Vocabulary = 100000
```

那么 Logits 概念 Shape：

```text
(1, 20, 100000)
```

---

## 18. 为什么每个位置都有 10 万个分数？

因为训练语言模型时：

> 每个位置都曾经学习预测它的下一个 Token。

---

# 二十七、推理时真正最关心哪个位置？

在普通自回归生成中，

我们要继续当前序列：

> 最关心最后一个有效位置。

---

## 19. 可以想成

Prompt：

```text
请 审 查 这 个 条 款
                   ↑
               最后位置
```

模型问：

> “在整个 Prompt 后面，下一 Token 最可能是什么？”

---

# 二十八、所以会取“最后一个位置”的 Logits

概念上：

```text
所有位置Logits
      ↓
取最后位置
      ↓
Vocabulary候选分数
```

例如：

```text
100000个分数
```

---

# 二十九、然后怎样从分数变成一个 Token？

这里会涉及：

- Greedy；
- Temperature；
- Top-k；
- Top-p。

但这些是第 8 阶段重点。

今天只抓一个总概念：

\[
\boxed{
Model负责打分
}
\]

\[
\boxed{
DecodingPolicy负责从分数里选Token
}
\]

---

# 三十、一个非常好用的类比

模型像：

> 专家评委。

他给 10 万个候选答案：

> 全部打分。

---

## 20. Decoding Strategy 像

> 最后的选人规则。

可能是：

> 最高分直接录取。

也可能：

> 在高分候选中随机抽取。

---

## 21. 所以

```text
Model
=
评分系统

Sampling
=
录取规则
```

这个区别后面特别重要。

---

# 三十一、假设选中了一个 Token

例如：

```text
Token ID = 4321
```

它对应文字：

> “该”

---

## 22. 是不是生成结束了？

当然不是。

现在答案只有：

```text
该
```

---

# 三十二、下一步才是 LLM 最关键的循环

把刚生成的 Token：

> 接到原 Prompt 后面。

原来：

```text
[Prompt Tokens]
```

现在：

```text
[Prompt Tokens] + [该]
```

---

## 23. 再送进模型

模型再次问：

> “现在下一个 Token 是什么？”

可能选：

> “条款”。

---

## 24. 然后变成

```text
[Prompt Tokens]
+
[该]
+
[条款]
```

---

## 25. 再来

可能：

> “可能”。

---

## 26. 再来

可能：

> “存在”。

---

# 三十三、于是整段回答实际上这样长出来

```text
第1步：
该

第2步：
该 条款

第3步：
该 条款 可能

第4步：
该 条款 可能 存在

第5步：
该 条款 可能 存在 ...

...
```

这就是：

# Autoregressive Generation

---

# 三十四、第四个核心心智模型

\[
\boxed{
生成文本
=
不断把自己刚刚生成的Token
重新作为下一步输入的一部分
}
\]

这句话必须真正理解。

---

# 三十五、所以 `generate()` 到底干了什么？

你以后可能只写：

```python
outputs = model.generate(...)
```

看起来：

> 一行代码生成整段回答。

---

## 27. 但它背后可以想成

```text
while 没有结束：

    1. 看当前序列

    2. 模型计算下一Token的Logits

    3. 选择一个Token

    4. 接到序列尾部

    5. 再继续
```

---

# 三十六、用伪代码表示

```python
tokens = prompt_tokens

while not finished:

    logits = model(tokens)

    next_token = choose(logits)

    tokens.append(next_token)
```

这就是最核心的思想。

真实实现：

> 会高效得多。

---

# 三十七、但是这里出现一个严重效率问题

假设 Prompt 有：

```text
10,000 Token
```

第一次预测：

> 读 10,000 个。

---

## 28. 生成一个新 Token 后

现在：

```text
10,001 Token
```

难道又要：

> 从头把前 10,000 个 Token 所有 Attention 计算完全重做一遍？

如果这样：

> 非常浪费。

---

# 三十八、这就是 KV Cache 又回来

第二课、第三课第 1 阶段都已经见过它。

现在终于看到它为什么存在。

---

## 29. 第一次处理整个 Prompt

模型会计算过去 Token 的：

```text
K
V
```

---

## 30. 然后把它们存下来

```text
KV Cache
```

---

## 31. 下一步只生成一个新 Token

模型主要需要：

> 计算新 Token 的新 Q/K/V。

过去大量 K/V：

> 可以直接复用。

---

# 三十九、用会议秘书类比

第一次读 300 页采购文件：

> 秘书做了 300 页结构化笔记。

---

## 32. 后面你问第二个问题时

不用让秘书：

> 再从第 1 页开始重新抄一遍。

可以利用：

> 已经整理好的笔记。

这就是 KV Cache 的直觉。

---

# 四十、Prefill 与 Decode 现在终于落地

第三课前面提过这两个词。

现在可以真正理解。

---

## 33. Prefill

第一次处理：

> 整个 Prompt。

例如：

```text
5000 Token
```

一次进入模型。

这一阶段：

> 创建大量 KV Cache。

---

## 34. Decode

后面开始：

> 一个 Token 一个 Token 生成。

例如：

```text
第5001个
第5002个
第5003个
...
```

利用：

> 已经存在的 KV Cache。

---

# 四十一、一张非常重要的图

```text
           Prompt
      5000个Token
            │
            ▼
        PREFILL
一次处理整个Prompt
            │
            ├── 建立KV Cache
            │
            ▼
      生成第1个新Token
            │
            ▼
          DECODE
            │
      ┌─────┴─────┐
      ▼           ▼
复用旧KV      计算新Token
      │           │
      └─────┬─────┘
            ▼
      生成第2个Token
            │
            ▼
          重复……
```

---

# 四十二、为什么长 Prompt 会让“第一字等待时间”变长？

因为 Prefill 要先处理：

> 整个 Prompt。

---

## 35. 一句话

可能：

```text
30 Token
```

---

## 36. 一份长采购文件

可能：

```text
30,000 Token
```

甚至更多。

模型吐出第一个回答 Token 前：

> 必须先完成大量 Prompt 计算。

---

# 四十三、这就是 TTFT

# Time To First Token

也就是：

> 用户提交问题以后，等多久才看到第一个生成 Token。

---

## 37. 长采购文档

往往会增加：

> Prefill 工作量。

所以 TTFT：

> 可能升高。

---

# 四十四、第一 Token 出来以后，又进入另一种体验

模型开始：

```text
一个Token
一个Token
一个Token
```

往外吐。

这时你感受到：

> 每秒生成多少 Token。

---

# 四十五、所以用户体验至少有两个速度

```text
提交问题
   │
   ├─────────────► 第一个字出现
   │                 ↑
   │                TTFT
   │
   ▼
后续不断生成
   │
   ▼
Tokens Per Second
```

---

# 四十六、为什么“感觉快不快”不能只看一个数字？

假设模型 A：

> 2 秒出第一个 Token。

之后：

> 20 token/s。

---

## 38. 模型 B

> 8 秒才出第一个 Token。

但之后：

> 80 token/s。

---

## 39. 哪个体验更好？

取决于：

- Prompt 多长；
- 输出多长；
- 业务要求。

所以后面第 9 阶段会专门做：

# Performance Benchmark

---

# 四十七、现在回到 `generate()`

一个常见概念代码可能是：

```python
outputs = model.generate(
    **inputs,
    max_new_tokens=200
)
```

这一行里第一个特别重要的参数：

# `max_new_tokens`

---

# 四十八、`max_new_tokens=200` 是 200 个汉字吗？

不是。

它表示：

> 最多再生成 200 个新 Token。

---

## 40. Token 不等于汉字

一个 Token：

> 可能对应一个字。

也可能：

> 多个字。

也可能：

> 半个词、数字片段、标点等。

---

## 41. 所以

```text
200 Token
≠
固定200字
```

这是一个非常重要的实务区别。

---

# 四十九、它限制的是 Prompt 吗？

也不是。

假设：

```text
Prompt = 1000 Token
```

然后：

```text
max_new_tokens = 200
```

---

## 42. 最长生成序列大概可能达到

```text
1000 Prompt Token
+
最多200 Output Token
```

也就是：

```text
约1200 Token
```

还要考虑特殊 Token 等具体实现。

---

# 五十、所以最好把两个概念分开

```text
Input Tokens
=
用户给模型看的东西

Output Tokens
=
模型新生成的东西
```

---

# 五十一、什么是 Context？

很多人会把：

> Prompt 长度

等于：

> Context。

但生成过程中，Context 其实会不断增长。

---

## 43. 刚开始

```text
Context
=
Prompt
```

---

## 44. 生成 100 Token 后

```text
Context
=
Prompt
+
已生成100个Token
```

因为模型后面预测时：

> 也要看到自己前面生成的内容。

---

# 五十二、一个极其重要的“上下文预算”概念

假设模型最大上下文窗口：

```text
32768 Token
```

你不能简单认为：

> Prompt 可以永远塞满 32768。

---

## 45. 如果 Prompt 已经用了

```text
32000
```

你又希望模型回答：

```text
2000 Token
```

那总需求：

```text
34000
```

已经超过窗口。

---

# 五十三、所以 Context Window 像一间会议室

会议室最大：

> 32,768 个座位。

---

## 46. 用户材料先占

> 30,000 个座位。

系统提示占：

> 1,000 个。

RAG 证据占：

> 1,000 个。

---

## 47. 已经用了

> 32,000。

留给回答：

> 只剩不多。

---

# 五十四、这是未来 ProcurementRAG 极其重要的一件事

Context Budget 不是无限的。

你要在里面安排：

```text
System Prompt
+
User Question
+
采购文件
+
法规证据
+
示例
+
模型回答
```

---

## 48. 所以以后做 RAG 不是：

> 检索越多越好。

而是：

> **最有价值的信息应该进入有限 Context。**

---

# 五十五、现在说 EOS

模型什么时候知道：

> “我回答完了”？

其中一个重要机制是：

# EOS Token

End Of Sequence。

---

## 49. 模型可以生成一个特殊 Token

概念上：

```text
<EOS>
```

表示：

> 序列结束。

---

## 50. `generate()` 检测到停止条件

就可以：

> 停止继续生成。

---

# 五十六、如果模型一直不生成 EOS 怎么办？

还需要其它限制，例如：

```text
max_new_tokens
```

否则理论上：

> 可能一直生成到其它长度限制。

---

# 五十七、所以生成停止可以来自不同原因

```text
生成EOS
     │
     ├── 停止
     │
达到max_new_tokens
     │
     ├── 停止
     │
达到Context限制
     │
     └── 不能再继续
```

真实框架还可能支持：

> 更多停止条件。

---

# 五十八、生成完以后为什么还是 Token IDs？

假设模型最终生成：

```text
[4321, 7188, 332, 981, ...]
```

用户看不懂。

---

## 51. 所以 Tokenizer 再次登场

这次方向反过来：

```text
Token IDs
↓
Tokenizer Decode
↓
字符串
```

---

# 五十九、第五个核心心智模型正式闭环

Tokenizer 有两种方向：

```text
ENCODE

Text
↓
Token IDs
```

和：

```text
DECODE

Token IDs
↓
Text
```

---

# 六十、所以 Tokenizer 在整个系统头尾各出现一次

```text
           ENCODE
中文 ─────────────► Token IDs
                       │
                       ▼
                     LLM
                       │
                       ▼
                    New IDs
                       │
           DECODE      │
中文 ◄─────────────────┘
```

这个图非常值得记。

---

# 六十一、一个容易困惑的问题：`generate()` 返回的只有新 Token 吗？

很多 Decoder-only 模型/接口中，

返回序列可能包含：

```text
原Prompt Token
+
新生成Token
```

---

## 52. 例如输入

```text
[10, 20, 30]
```

生成：

```text
[40, 50]
```

返回可能是：

```text
[10, 20, 30, 40, 50]
```

---

# 六十二、那我们只想看回答怎么办？

可以根据：

> 输入长度

把前面的 Prompt Token 切掉。

概念上：

```text
完整输出：
[PROMPT][ANSWER]

切掉PROMPT：
          [ANSWER]
```

---

# 六十三、这就是为什么以后代码里可能看到

概念形式：

```python
generated = outputs[:, input_length:]
```

不是神秘技巧。

它只是：

> **把原输入部分去掉，只留下新生成部分。**

---

# 六十四、Chat 模型比普通字符串还多一步

假设用户写：

> “请审查这个采购条款。”

真正送进模型之前，通常还会有：

# Chat Template

---

## 53. 屏幕上看起来是

```text
System:
你是政府采购审查助手

User:
请审查……
```

---

## 54. 模型真正看到的 Token Sequence

可能包含：

> 特殊角色标记。

概念上：

```text
<System>
你是政府采购审查助手
<User>
请审查……
<Assistant>
```

不同模型：

> 格式不同。

---

# 六十五、所以真实输入流水线更完整地应该画成

```text
聊天消息
   │
   ▼
Chat Template
   │
   ▼
一个模型熟悉的字符串/Token结构
   │
   ▼
Tokenizer
   │
   ▼
input_ids
```

---

# 六十六、为什么用错 Chat Template 会伤害模型？

假设一个采购办要求所有文件格式是：

```text
项目编号
采购人
供应商
风险类型
```

---

## 55. 结果你提交：

```text
供应商
然后项目编号
再混进其它标记
```

虽然内容：

> 都存在。

但工作流程：

> 被打乱。

Chat 模型也类似。

---

## 56. 它在 SFT 时已经习惯某种角色结构

如果推理时格式完全不同：

> 模型行为可能明显变差。

---

# 六十七、所以“Prompt”并不只是用户那句话

真实 Prompt 可能包括：

```text
System Prompt
+
Conversation History
+
User Message
+
RAG Documents
+
Tool Results
+
Chat Template Tokens
```

全部合起来：

> 才是模型当前真正看到的 Context。

---

# 六十八、ProcurementAI 的完整案例开始

现在我们真正走一遍。

用户输入：

> **“请审查以下资格条件：供应商注册资本不得低于5000万元。”**

为了教学，我们假设系统提示：

> “你是政府采购文件风险审查助手。请指出潜在风险、理由和需要核验的依据。”

---

# 六十九、Step 1：形成聊天消息

概念上：

```text
SYSTEM
你是政府采购文件风险审查助手……

USER
请审查以下资格条件：
供应商注册资本不得低于5000万元。
```

---

# 七十、Step 2：应用 Chat Template

变成模型训练时熟悉的结构。

概念上：

```text
<SYSTEM>
你是政府采购文件风险审查助手……
<USER>
请审查……
<ASSISTANT>
```

---

# 七十一、Step 3：Tokenizer Encode

变成：

```text
[151643, 894, 2311, 9928, ...]
```

这些数字只是：

> 示意。

不是任何具体模型的真实 Token ID。

---

# 七十二、Step 4：创建 Tensor

例如：

```text
input_ids.shape
=
(1, 48)
```

意思：

```text
1个样本

48个Token
```

---

# 七十三、Step 5：搬到 GPU

```text
RAM
↓
VRAM
```

现在：

```text
input_ids
→ cuda:0
```

模型：

```text
weights
→ cuda:0
```

---

# 七十四、Step 6：Prefill

48 个 Prompt Token：

> 一次经过 Transformer。

---

## 57. 内部发生

```text
Token Embedding
↓
RoPE
↓
Attention
↓
MLP
↓
几十层Block
↓
Final Hidden State
↓
LM Head
```

同时：

> 建立 KV Cache。

---

# 七十五、Step 7：产生第一个回答 Token 的 Logits

例如模型可能给出：

```text
“该”       高分

“此”       高分

“存在”     较高分

“未”       较低分

……
```

---

# 七十六、Step 8：Decoding Policy 选出一个

假设选：

> “该”。

把它：

> 接回 Context。

---

# 七十七、Step 9：进入 Decode

利用：

> Prompt 的 KV Cache。

只处理：

> 新增 Token 所需的新计算。

然后生成：

> “条件”。

---

# 七十八、继续循环

```text
该

该 条件

该 条件 可能

该 条件 可能 涉及

……
```

---

# 七十九、最终可能形成

例如：

> “该条件可能涉及对供应商设置与采购项目实际需要无直接关联的规模性资格要求，应结合项目特点、履约需求及现行法规进一步核验其必要性与合法性……”

这里只是：

> 教学示意。

不是对真实项目作正式法律结论。

---

# 八十、为什么我这里故意没有直接说“违法”？

因为这正好体现未来 ProcurementLM 的要求。

模型不能只学：

```text
注册资本
↓
违法
```

---

## 58. 真正专业系统需要结合

- 完整上下文；
- 采购项目性质；
- 实际履约需要；
- 适用法规；
- 当前有效版本；
- 专家复核。

所以未来我们追求的是：

\[
\boxed{
EvidenceBasedJudgment
}
\]

而不是：

\[
\boxed{
KeywordTrigger
}
\]

---

# 八十一、现在看一段最小概念代码

先看，不要求现在运行：

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

text = "请审查：供应商注册资本不得低于5000万元。"

inputs = tokenizer(text, return_tensors="pt")

outputs = model.generate(
    **inputs,
    max_new_tokens=200
)

answer = tokenizer.decode(
    outputs[0],
    skip_special_tokens=True
)

print(answer)
```

---

# 八十二、不要背代码，逐行翻译

## 59.

```python
AutoTokenizer.from_pretrained(...)
```

意思：

> 把模型配套的语言编码系统加载起来。

---

## 60.

```python
AutoModelForCausalLM.from_pretrained(...)
```

意思：

> 按第四阶段的流程，把模型真正装起来。

---

## 61.

```python
tokenizer(text)
```

意思：

```text
Text
↓
Token IDs
↓
Tensor
```

---

## 62.

```python
model.generate(...)
```

不是：

> “神奇地写文章。”

而是：

```text
Forward
↓
Logits
↓
选Token
↓
接回去
↓
继续Forward
↓
……
```

---

## 63.

```python
tokenizer.decode(...)
```

就是：

```text
Token IDs
↓
Human-readable Text
```

---

# 八十三、这段代码还有一个问题

如果模型在 GPU：

> inputs 也需要到正确 Device。

所以实际代码还需要处理：

> Device Placement。

---

## 64. 这正好连接第 2、4 阶段

```text
模型在哪？
↓
输入也必须去相应计算设备
```

---

# 八十四、完整一点的脑内执行顺序

以后看到推理代码，先别看语法。

问这 8 个问题：

```text
1. Tokenizer加载了吗？

2. Model加载了吗？

3. Prompt格式对吗？

4. Tokenize以后有多少Token？

5. Tensor在哪里？

6. Model在哪里？

7. generate怎样停止？

8. 输出怎么Decode？
```

这个 checklist 比背 API 更重要。

---

# 八十五、为什么模型会重复？

比如生成：

> “该条款存在风险，该条款存在风险，该条款……”

可能涉及：

- Decoding 参数；
- Chat Template；
- EOS 设置；
- 模型本身；
- Prompt；
- 重复惩罚策略；

等等。

---

## 65. 所以看到生成问题

不要马上得出：

> “模型训练坏了。”

先区分：

```text
Input问题？

Template问题？

Generation问题？

Model能力问题？
```

---

# 八十六、为什么输出为空？

也可能有多种原因。

比如：

- 立即生成 EOS；
- Prompt Template 不对；
- 截取输出方式错；
- `max_new_tokens` 太小；
- Decode 方法有问题。

---

# 八十七、为什么乱码或奇怪字符？

优先想到之一：

> Tokenizer 是否匹配。

第三阶段的知识又回来。

---

# 八十八、为什么报 Device Error？

优先问：

```text
Model在哪？

input_ids在哪？

attention_mask在哪？
```

第二阶段又回来。

---

# 八十九、为什么 CUDA OOM？

优先问：

- Weight 多大；
- Prompt 多长；
- KV Cache 多大；
- Batch 多大；
- Precision 是什么。

第一阶段又回来。

---

# 九十、第三课已经开始形成“故障树”

```text
模型跑不起来
│
├─ 文件问题
│   └─ Stage 3
│
├─ 加载问题
│   └─ Stage 4
│
├─ CUDA / Device问题
│   └─ Stage 1~2
│
├─ Tokenizer / Template问题
│   └─ Stage 3 / Stage 5
│
└─ Generation问题
    └─ Stage 5 / Stage 8
```

以后我们不靠猜。

---

# 九十一、核心心智模型 ① 再看一次

## 模型从没直接看到文字

用户：

```text
供应商注册资本不得低于5000万元
```

模型：

```text
18452 76103 9321 4178 550 23891 ...
```

然后才进入：

> Embedding。

---

# 九十二、核心心智模型 ②

## Tokenizer 和 Transformer 分工不同

```text
Tokenizer
=
语言编码接口

Transformer
=
上下文计算引擎
```

Tokenizer：

> 不负责专业推理。

Transformer：

> 也不会直接解析原始 Unicode 字符串。

---

# 九十三、核心心智模型 ③

## 模型输出的是候选评分，不是文字

```text
Hidden State
↓
LM Head
↓
Vocabulary Logits
↓
“下一个Token选谁？”
```

---

# 九十四、核心心智模型 ④

## `generate()` 是循环，不是一次写完

```text
预测
↓
追加
↓
预测
↓
追加
↓
预测
↓
追加
```

直到：

> 停止条件。

---

# 九十五、核心心智模型 ⑤

## Tokenizer 是入口，也是出口

```text
Text
  │
  │ Encode
  ▼
Token IDs
  │
  │ LLM
  ▼
New Token IDs
  │
  │ Decode
  ▼
Text
```

---

# 九十六、把五个心智模型装进一个“采购审查流水线”

```text
用户采购条款
      │
      ▼
Chat Template
      │
      ▼
Tokenizer Encode
      │
      ▼
input_ids
attention_mask
      │
      ▼
Tensor搬到GPU
      │
      ▼
Transformer Prefill
      │
      ▼
KV Cache
      │
      ▼
最后位置Logits
      │
      ▼
选择Next Token
      │
      ▼
加入Context
      │
      ▼
Transformer Decode
      │
      ▼
重复生成
      │
      ▼
EOS / 达到停止条件
      │
      ▼
Tokenizer Decode
      │
      ▼
最终中文风险分析
```

这就是第三课第 5 阶段最值得保存的一张图。

---

# 九十七、这一阶段暂时不需要深挖什么？

暂时不要把精力花在：

- Temperature 数学；
- Top-k 算法；
- Top-p 算法；
- Beam Search；
- Sampling 理论；
- Quantization；
- KV Cache 精确显存公式；
- vLLM；
- PagedAttention。

后面都有专门阶段。

---

# 九十八、为什么不现在全部讲？

因为目前最重要的是：

> **把一条推理链完整跑通。**

也就是：

```text
文字进去
↓
数字
↓
模型
↓
分数
↓
数字
↓
文字出来
```

脑内路线先形成。

---

# 九十九、思维实验 A

用户输入：

> “供应商应具有5年以上成立年限。”

Tokenizer 完成后：

> 程序突然删除了原始字符串。

模型还能继续 Forward 吗？

**可以。**

只要：

> 必要的 Token Tensor 已经形成。

因为 Transformer 真正使用的是：

> Token ID / 后续 Tensor 表示。

---

# 一百、思维实验 B

Tokenizer 正确。

模型正确。

但是：

```text
input_ids → CPU

model → GPU
```

能正常 Forward 吗？

通常：

> **不行。**

需要处理：

> Device 一致性。

---

# 一百零一、思维实验 C

模型已经产生一整张 Vocabulary Logit 表。

是不是说明：

> 中文答案已经存在某个隐藏字符串里？

不是。

此时只是：

> 候选 Token 的分数。

还必须：

> 选择 Token。

---

# 一百零二、思维实验 D

如果每次都选择最高分 Token，

还是在做：

> 自回归生成。

是的。

区别只在：

> Next Token 的选择规则。

---

# 一百零三、思维实验 E

Prompt 有：

```text
30,000 Token
```

`max_new_tokens=5`

模型需要生成多少新 Token？

最多：

> 5 个。

不是：

> 总共 5 个。

---

# 一百零四、思维实验 F

`max_new_tokens=500`

是否代表：

> 一定输出 500 Token？

不一定。

因为模型可能：

> 提前生成 EOS。

---

# 一百零五、思维实验 G

模型回答：

> 一开头很好。

后面逐渐跑偏。

为什么前面的生成会影响后面的生成？

因为：

> **刚刚生成的 Token 会被加入后续 Context。**

所以后面模型一直在读取：

> 自己前面写出的内容。

---

# 一百零六、这也是自回归模型一个非常深的特点

错误一旦进入 Context：

> 后面有可能围绕这个错误继续发展。

比如一开始错误写：

> “根据某不存在的第27条……”

后面模型可能继续：

> 围绕这个错误引用组织论证。

---

## 66. 所以政府采购模型为什么需要 Citation Validation？

因为：

> 生成得流畅不代表第一步引用就是对的。

---

# 一百零七、这又连接未来 RAG

理想流程可能变成：

```text
用户问题
↓
先检索真实法规证据
↓
把证据放进Prompt
↓
LLM生成分析
↓
再验证Citation
```

而不是让模型：

> 凭 Weight 自己猜法规。

---

# 一百零八、我们现在终于能定义“跑通第一个模型”是什么意思

它不是：

> Python 没报错。

真正至少要验证：

```text
Tokenizer 正常

Prompt格式正确

Tensor Device正确

Model Forward正常

能产生Logits

能生成Token

能Decode成中文

EOS正常

输出基本符合模型预期
```

这才叫：

# End-to-End Inference Works

---

# 一百零九、第 5 阶段掌握标准

这一阶段结束以后，你应该能用自己的话解释：

> 用户输入的中文最开始存在哪里？

> 为什么 Transformer 不直接接收字符串？

> Tokenizer Encode 做什么？

> `input_ids` 到底是什么？

> 为什么 `input_ids` 通常是二维的？

> Batch 和 Sequence Length 分别是什么？

> 为什么不同长度样本需要 Padding？

> `attention_mask` 的直觉是什么？

> 为什么 CPU 上的 Tensor 要搬到 GPU？

> Token ID 经过模型后为什么会变成 Hidden State？

> LM Head 在做什么？

> Logit 为什么不是中文？

> 为什么一个位置会有整个 Vocabulary 的 Logits？

> 自回归生成是什么意思？

> `generate()` 为什么不是一次写完整篇答案？

> 为什么刚生成的 Token 要重新进入 Context？

> KV Cache 为什么能避免重复计算大量过去信息？

> Prefill 和 Decode 分别是什么？

> 为什么长 Prompt 会影响 TTFT？

> `max_new_tokens` 是字数还是 Token 数？

> Prompt Token 和新生成 Token 为什么要区分？

> Context Window 为什么要给答案预留空间？

> EOS Token 是做什么的？

> Tokenizer Decode 在整个流程哪个位置发生？

> 为什么 Chat Template 也属于模型输入协议的一部分？

如果这些都能自己解释：

\[
\boxed{
第三课第5阶段真正掌握
}
\]

---

# 一百一十、本阶段最终只记一句话

> **一个 LLM 并不是“读一句中文，然后一次想出一段回答”；真实过程是：Tokenizer 把文字变成 Token Tensor，Transformer 给下一个 Token 的所有候选打分，生成器选出一个 Token、把它接回上下文，再重复这个过程，最后由 Tokenizer 把生成出的 Token IDs 翻译回文字。**

最后把整条链压成一张图：

```text
               用户中文
                  │
                  ▼
             Chat Template
                  │
                  ▼
          Tokenizer Encode
                  │
                  ▼
            input_ids
                  │
             CPU → GPU
                  │
                  ▼
               Prefill
                  │
                  ▼
              KV Cache
                  │
                  ▼
               Logits
                  │
                  ▼
          选择Next Token
                  │
          ┌───────┴────────┐
          │                │
          ▼                │
      新Token加入Context    │
          │                │
          ▼                │
        Decode循环 ─────────┘
          │
          ▼
       EOS / Stop
          │
          ▼
      Tokenizer Decode
          │
          ▼
          中文回答
```

---

# 下一阶段：第三课 · 第 6 阶段
## FP32、FP16、BF16、INT8、INT4 到底是什么？为什么同一个 7B 模型可以是 28GB，也可以只有几 GB？

下一阶段我们会继续保持“先直觉、后数字”的方式，不先讲浮点数编码格式。

先解决一个生活化问题：

```text
同样是70亿个参数，

如果每个参数用：
4个字节
2个字节
1个字节
半个字节

模型要占多少空间？
```

然后才进入：

```text
FP32
   ↓
FP16 / BF16
   ↓
INT8
   ↓
INT4
   ↓
Quantization
```

重点不是背名字，而是建立三个非常重要的判断能力：

> **精度降低到底省了什么？**

> **为什么 BF16 和 FP16 都是 16-bit，却不是一回事？**

> **为什么 4-bit 模型能让一张显存较小的 GPU 跑更大的 LLM，却不等于“模型免费缩小而能力完全不变”？**

这一阶段会直接为第 7 阶段的**显存预算**铺路。

---
