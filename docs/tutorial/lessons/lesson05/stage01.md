# 第五课 · 第 1 阶段
# Chat Template、Prompt、Response 与 Loss Mask
## 一条政府采购数据，究竟怎样变成“模型真正学习的 Token”？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **“这是 Prompt。”**
2. **“这是 Response。”**
3. **我们通过 Chat Template 和 Loss Mask 把这种结构编码进去。**
4. **Token₁ Token₂ Token₃ ... Tokenₙ**
5. **第一，模型最终训练的不是 JSON、Prompt 或问答表，而是一条 Token 序列。**
6. **第二，Chat Template 是 Base Model 的对话通信协议，不是排版装饰。**
7. **第三，Prompt 是模型必须看到的条件，Response 是我们主要希望它学习生成的目标。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Token` | Token：模型实际处理的离散文本单元 |
| `Loss` | 损失函数：把预测错误压缩成可优化的数值信号 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |
| `Chat Template` | 对话模板：把角色消息转换成模型训练/推理序列 |
| `Response` | 目标响应：希望模型学习生成的答案部分 |
| `Loss Mask` | 损失掩码：指定哪些 Token 参与训练 Loss |
| `Input` | 输入：模型在当前任务中允许看到的条件信息 |
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `SFT` | 监督微调：用监督样本继续更新模型参数 |
| `Tokenizer` | 分词器：文本与 Token ID 之间的编码/解码组件 |
| `LoRA` | LoRA：冻结大部分基座参数，只训练低秩增量矩阵 |
| `Dataset` | 数据集：按统一 Schema、版本和质量标准组织的样本集合 |

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

第五课从这里正式开始。

前四课我们已经解决了：

```text
模型是什么
    ↓
模型内部怎样工作
    ↓
怎样把模型跑起来
    ↓
怎样做出 ProcurementDataset_V0.1
```

现在第一次进入：

# 真正训练模型

但在写第一行训练代码之前，必须先把一件事彻底搞清楚：

> **一条专家数据送进 SFT 以后，模型到底看到了什么？又到底对哪些 Token 产生梯度？**

如果这个问题没弄懂，后面即使：

- LoRA 配置正确；
- GPU 足够；
- Learning Rate 正确；
- Loss 正常下降；

也可能从一开始：

> **训练错了目标。**

这一阶段最终我们要形成一个非常明确的工程对象：

# `SFTTrainingExample_V0.1`

---

# 一、本阶段只解决一个核心问题

第四课可能给了我们这样一条数据：

```text
采购条款：
投标人须在本市设立固定办公场所。

专家结论：
存在潜在供应商资格风险。

理由：
该条件将投标前已经具备本地固定场所作为参与条件，
需要审查其必要性和合理性。
```

那么训练模型的时候：

> 哪些部分是“给模型看的条件”？

> 哪些部分是“要求模型学会生成的答案”？

> 哪些 Token 应该计算 Loss？

> 哪些 Token 虽然模型必须看到，却不应该成为训练目标？

这就是今天全部内容。

---

# 二、先记住这一张总图

整个 SFT 样本真正经过的是：

```text
ProcurementDataset_V0.1
        │
        ▼
Structured Messages
结构化对话
        │
        ▼
Chat Template
套用模型规定的对话格式
        │
        ▼
Serialized Text
变成一条连续文本
        │
        ▼
Tokenizer
变成 Token ID
        │
        ▼
input_ids
模型实际看到的 Token
        │
        ├─────────────────┐
        │                 │
        ▼                 ▼
   Prompt Tokens     Response Tokens
     条件区域            答案区域
        │                 │
        ▼                 ▼
   不计算Loss          计算Loss
        │                 │
        └────────┬────────┘
                 ▼
              labels
                 │
                 ▼
                Loss
                 │
                 ▼
              Gradient
                 │
                 ▼
          模型参数发生变化
```

压缩成一句：

> **先把对话格式化成 Token，再用 Loss Mask 决定哪些 Token 真正产生训练信号。**

这就是第五课第一阶段的主线。

---

# 三、先锁死 5 个核心心智模型

这一阶段最重要的不是记 API。

是下面五句话。

---

## 心智模型 1：SFT 训练的不是“问答表”，而是一条 Token 序列

人类看到的是：

```text
问题
→
答案
```

模型实际上看到的是：

```text
Token₁
Token₂
Token₃
...
Tokenₙ
```

所以：

\[
\boxed{
SFTExample
最终必须变成
TokenSequence
}
\]

模型并不知道：

> “这是 Prompt。”

> “这是 Response。”

除非：

> **我们通过 Chat Template 和 Loss Mask 把这种结构编码进去。**

---

## 心智模型 2：Chat Template 不是美化排版，而是模型的“通信协议”

# Chat Template
## 对话模板

它负责把：

```json
[
  {
    "role": "user",
    "content": "请判断以下采购条款……"
  },
  {
    "role": "assistant",
    "content": "该条款存在潜在风险……"
  }
]
```

转换成模型真正训练过的格式。

概念上可能变成：

```text
<|user|>
请判断以下采购条款……
<|assistant|>
该条款存在潜在风险……
<|end|>
```

另一种模型可能是：

```text
<|im_start|>user
……
<|im_end|>
<|im_start|>assistant
……
<|im_end|>
```

还有模型可能完全不同。

因此：

\[
\boxed{
ChatTemplate
=
ModelConversationProtocol
}
\]

它不是装饰。

是：

> **这个模型认得什么样的“用户”和“助手”。**

---

## 心智模型 3：Prompt 是条件，Response 才是主要学习目标

我们先采用第五课的默认训练策略：

# Assistant-only Loss
## 只对助手回答计算主要 Loss

于是：

```text
User / System
=
Condition
条件

Assistant Response
=
Target
目标
```

模型必须看到 Prompt。

但：

> **看到 ≠ 要预测它。**

这是今天最重要的区别之一。

---

## 心智模型 4：`input_ids` 和 `labels` 看起来很像，但职责完全不同

这是很多初学者真正开始训练以后最容易混淆的地方。

`input_ids`：

> 模型看到了什么。

`labels`：

> 哪些 Token 要求模型预测正确。

所以：

\[
\boxed{
input\_ids
\neq
labels
}
\]

虽然在 Causal LM 训练中：

> `labels` 通常是从 `input_ids` 复制出来再 Mask。

---

## 心智模型 5：Loss Mask 决定了“模型到底在学谁”

如果 Mask 错了：

> 数据内容再好都没用。

所以：

\[
\boxed{
TrainingTarget
由
LossMask
最终决定
}
\]

不是你的 JSON 字段名字。

不是：

```text
"target": "..."
```

就天然意味着模型只学 target。

真正决定梯度的是：

> **哪些 Label Token 被保留下来计算 Loss。**

---

# 四、现在精准区分四个概念

以后看到这四个词，不要再混。

| 概念 | 精准理解 |
|---|---|
| **Prompt** | 给模型的条件、问题、上下文 |
| **Response** | 希望模型学习生成的答案 |
| **Chat Template** | 把角色和内容编码成模型规定的 Token 格式 |
| **Loss Mask** | 决定哪些 Token 参与 Loss |

它们解决的是四个完全不同的问题。

---

# 五、先看 Prompt 和 Response

比如第四课产生：

```json
{
  "input": {
    "target_clause": "投标人须在本市设立固定办公场所。",
    "section_context": "供应商资格条件"
  },

  "target": {
    "risk_present": true,
    "risk_type": "supplier_qualification",
    "reason": "该条件将投标前本地固定场所作为参与条件，应进一步审查其必要性。"
  }
}
```

第五课不能直接把这段 JSON：

> 一股脑扔给模型。

我们要先设计：

# Training Conversation

例如：

```text
System:
你是一名政府采购风险审查助手。
请根据提供的采购条款进行风险筛查。
不要把风险提示表述为最终法律结论。

User:
章节：供应商资格条件

采购条款：
投标人须在本市设立固定办公场所。

请判断是否存在潜在风险，并说明理由。

Assistant:
风险判断：存在潜在风险。

风险类型：供应商资格条件。

理由：该条款将投标前已经具备本地固定办公场所作为参与条件，
需要进一步审查该要求与项目实际需求之间的必要性和合理性。
```

这里可以直接分成：

```text
System + User
=
Prompt

Assistant
=
Response
```

---

# 六、但模型实际上还没有看到这些“角色”

模型最终没有一个神秘的：

```text
role = user
```

输入槽。

它最终仍然只接收：

# Token IDs

所以：

```text
messages
```

必须经过：

# Chat Template

---

# 七、Chat Template 到底在干什么？

假设我们现在有：

```json
[
  {
    "role": "system",
    "content": "你是一名政府采购风险审查助手。"
  },
  {
    "role": "user",
    "content": "请判断以下条款……"
  },
  {
    "role": "assistant",
    "content": "该条款存在潜在风险……"
  }
]
```

Chat Template 的工作就是：

```text
结构化 Messages
        ↓
按照模型约定增加角色标记
        ↓
增加开始 / 结束特殊 Token
        ↓
确定角色顺序
        ↓
形成完整训练字符串
```

最终类似：

```text
<system>
你是一名政府采购风险审查助手。
</system>

<user>
请判断以下条款……
</user>

<assistant>
该条款存在潜在风险……
</assistant>
```

注意：

这只是概念展示。

**实际特殊 Token 必须使用所选 Base Model 自己的 Chat Template。**

---

# 八、为什么不能自己随便发明模板？

假设某个 Base Model 原本训练时一直看到：

```text
<|im_start|>user
...
<|im_end|>
```

你微调时却自行使用：

```text
### USER:
...
### ASSISTANT:
...
```

模型当然仍可能学到东西。

但你相当于强迫它：

> 同时重新学习一套对话协议。

这是没有必要的额外负担。

所以第五课一个非常重要的原则是：

\[
\boxed{
PreferNativeChatTemplate
}
\]

中文：

> **优先沿用 Base Model 原生 Chat Template。**

---

# 九、Chat Template 还有一个更隐蔽的重要作用

它不仅告诉模型：

> 谁在说话。

还告诉模型：

> **Assistant 从哪里开始。**

例如：

```text
User Tokens
...
<assistant_start>
Assistant Tokens
...
<assistant_end>
```

后面构造 Loss Mask 时：

> 就需要知道 Assistant 区域到底在哪里。

所以：

```text
Chat Template
        ↓
角色边界
        ↓
Loss Mask
```

这两者：

> 是直接关联的。

---

# 十、现在进入真正的核心：Loss Mask

假设 Tokenizer 以后得到：

```text
[System][你][是][采购][助手]
[User][判断][这][条款]
[Assistant][存在][潜在][风险][EOS]
```

为了讲清楚，我们给 Token 编号：

```text
位置

1   [System]
2   你
3   是
4   采购
5   助手

6   [User]
7   判断
8   这
9   条款

10  [Assistant]
11  存在
12  潜在
13  风险
14  [EOS]
```

模型真正看到的：

```text
input_ids

1  2  3  4  5  6  7  8  9  10  11  12  13  14
```

但是我们不一定希望：

> System 和 User 的文字也成为训练目标。

于是创建：

```text
Loss Mask

System     0
User       0
Assistant  1
```

概念上：

```text
Token           Loss?

[System]         ×
你               ×
是               ×
采购             ×
助手             ×

[User]           ×
判断             ×
这               ×
条款             ×

[Assistant]      × / 视实现而定
存在             ✓
潜在             ✓
风险             ✓
[EOS]            ✓
```

于是：

> 真正产生主要训练信号的是 Assistant 答案。

---

# 十一、在 Hugging Face 类训练流程里，它通常怎样实现？

常见做法是：

```text
input_ids
=
完整Token序列
```

然后：

```text
labels
=
input_ids的副本
```

再把不计算 Loss 的位置设成：

```text
-100
```

例如：

```text
input_ids

[21, 83, 17, 95, 62, 44, 31, 76, 52, 91, 18, 36, 49, 2]
```

对应：

```text
labels

[-100,
 -100,
 -100,
 -100,
 -100,
 -100,
 -100,
 -100,
 -100,
 -100,
 18,
 36,
 49,
 2]
```

其中：

```text
-100
```

通常表示：

> **Cross Entropy Loss 忽略这个位置。**

所以：

\[
\boxed{
-100
=
DoNotComputeLoss
}
\]

在常见 PyTorch / Hugging Face Causal LM 训练中可以这样理解。

---

# 十二、这时模型还能看到 Prompt 吗？

能。

这是特别容易误解的地方。

例如 User Tokens：

```text
请判断这条采购条款
```

虽然它们的 Label 是：

```text
-100
```

但是：

> **它们仍然存在于 `input_ids`。**

所以 Assistant 生成：

```text
存在潜在风险
```

时仍然可以通过 Attention：

> 读取整个 Prompt。

因此：

\[
\boxed{
MaskedFromLoss
\neq
MaskedFromAttention
}
\]

这句话非常重要。

中文：

> **不计算 Loss，不等于模型看不见。**

---

# 十三、这张图必须记住

```text
                 Prompt
            System + User
                  │
                  │ 模型可以看
                  ▼
          ┌──────────────┐
          │ Transformer  │
          └──────────────┘
                  │
                  ▼
             Assistant
              Response
                  │
                  ▼
                Loss
                  │
                  ▼
              Gradient
```

Prompt：

> 是条件。

Response：

> 是主要学习目标。

---

# 十四、这里回到第二课：模型真正预测的仍然是“下一个 Token”

SFT 并没有把 Transformer 改成一个新的机器。

它依然在做：

\[
P(x_t \mid x_{<t})
\]

例如答案：

```text
存在 潜在 风险
```

模型实际学习的是：

```text
看到前面的Prompt
        ↓
预测“存在”

看到Prompt + 存在
        ↓
预测“潜在”

看到Prompt + 存在 + 潜在
        ↓
预测“风险”
```

所以 SFT 本质还是：

# Next Token Prediction

只是：

> **我们精心挑选了什么上下文之后应该生成什么答案。**

---

# 十五、Loss 最简单应该怎样理解？

不要先背复杂推导。

假设正确的 Assistant Token 是：

```text
风险
```

模型给出：

```text
风险        0.80
问题        0.10
条款        0.05
其他        0.05
```

这个位置：

> Loss 比较小。

如果：

```text
风险        0.05
问题        0.70
条款        0.15
其他        0.10
```

Loss：

> 会更大。

核心目标就是：

\[
\boxed{
提高正确Response Token的概率
}
\]

---

# 十六、完整一点的公式只需要这一条

对于我们真正计算 Loss 的 Assistant Token：

\[
\mathcal{L}
=
-\sum_{t \in A}
\log
P_\theta(x_t\mid x_{<t})
\]

这里：

\[
A
\]

表示：

> Assistant Response 中参与训练的 Token 位置集合。

不用背公式。

它只是把今天的核心说成数学语言：

> **只在我们选定的回答 Token 上惩罚模型。**

---

# 十七、为什么通常不希望 User Prompt 也计算 Loss？

假设训练样本是：

```text
User:
请判断以下采购条款是否存在风险。

Assistant:
该条款存在潜在风险……
```

如果全部 Token 都算 Loss，

模型还会花训练能力学习：

```text
请
判断
以下
采购
条款
```

也就是说它不仅学习：

> 怎样回答。

还学习：

> 怎样模仿用户提问。

这不一定绝对错误。

但我们的 ProcurementLM 主要目标是：

> **学会作为 Assistant 输出专业判断。**

所以第五课默认采用：

# Assistant-focused Supervision

---

# 十八、但是“Prompt 不算 Loss”不是宇宙定律

这一点要专业一点。

有些训练方案会采用：

# Full Sequence Loss
## 整段序列都计算 Loss

也有：

# Assistant-only Loss
## 只计算 Assistant

还有多轮对话中：

> 只计算所有 Assistant Turn。

不同框架和任务：

> 可能采取不同策略。

我们这一课的默认工程原则是：

\[
\boxed{
ProcurementSFT
默认采用
AssistantOnlyLoss
}
\]

因为我们的核心目标是：

> 学专业回答行为，而不是学用户怎样提问。

---

# 十九、现在看一个完整 Token 流程

假设数据：

```text
System:
你是政府采购风险审查助手。

User:
条款：
投标人须在本市注册。

请进行风险筛查。

Assistant:
该条款存在潜在供应商资格风险。
```

完整流程：

```text
Step 1
messages

[
 system,
 user,
 assistant
]

        ↓

Step 2
Chat Template

<system>...</system>
<user>...</user>
<assistant>...</assistant>

        ↓

Step 3
Tokenizer

Token IDs

        ↓

Step 4
input_ids

整个序列都存在

        ↓

Step 5
labels

System → -100
User   → -100
Assistant Response → Token ID

        ↓

Step 6
Forward Pass

模型预测每一个位置的下一Token

        ↓

Step 7
Loss

只读取有效Label位置

        ↓

Step 8
Backward

只有这些Loss产生梯度

        ↓

Step 9
Optimizer

LoRA / 模型参数被更新
```

这就是：

# 一条 SFT Sample 的完整生命流程

---

# 二十、把这条流程再压缩一次

以后看到训练代码，脑中只需要：

```text
Messages
   ↓
Template
   ↓
Tokens
   ↓
input_ids
   ↓
labels
   ↓
Loss Mask
   ↓
Loss
   ↓
Gradient
```

如果代码出了问题：

> 就沿着这条链查。

---

# 二十一、现在进入一个非常容易被忽略的东西：EOS

# EOS
## End Of Sequence / 结束 Token

假设 Assistant 的答案：

```text
存在潜在风险。
```

模型除了要学：

```text
存在
潜在
风险
```

最好还要学：

> **什么时候停止。**

于是通常答案结束会有：

```text
EOS
```

概念上：

```text
存在
潜在
风险
。
<EOS>
```

---

# 二十二、如果训练数据从来没有正确的结束标记，会怎样？

模型可能学到：

> 回答结束以后继续往下生成。

例如：

```text
风险判断……
理由……
建议……

风险判断……
理由……
建议……
```

甚至出现重复和拖尾。

所以：

\[
\boxed{
LearnWhatToSay
+
LearnWhenToStop
}
\]

同样重要。

---

# 二十三、特殊 Token 不能随便重复添加

这是后面真正写代码时经常踩的坑。

假设：

```text
Chat Template
```

已经自动加入：

```text
BOS / EOS
```

然后你又调用 Tokenizer：

```text
add_special_tokens=True
```

可能得到：

```text
<BOS>
<BOS>
...
<EOS>
<EOS>
```

于是：

> 训练格式与 Base Model 原格式不一致。

所以以后写代码必须确认：

> **到底是谁负责添加特殊 Token。**

---

# 二十四、Chat Template 和 Tokenizer 是一套东西

不要把它们完全割裂理解。

Chat Template：

> 决定文本怎样排列和角色怎样标记。

Tokenizer：

> 决定这些内容怎样变成 Token IDs。

两者组合起来才真正形成：

\[
\boxed{
ModelInputProtocol
}
\]

---

# 二十五、现在进入多轮对话

假设未来 ProcurementAI 支持：

```text
User:
这条款有风险吗？

Assistant:
可能存在风险。

User:
为什么？

Assistant:
因为……
```

结构就变成：

```text
System
User 1
Assistant 1
User 2
Assistant 2
```

---

# 二十六、多轮训练时怎样 Mask？

一种常见策略：

```text
System
不算Loss

User 1
不算Loss

Assistant 1
算Loss

User 2
不算Loss

Assistant 2
算Loss
```

也就是：

```text
User → Condition
Assistant → Target
```

反复出现。

---

# 二十七、但是这里有一个工程选择

有时候我们只希望训练：

> 最后一个 Assistant Response。

那么可能是：

```text
Assistant 1
也作为Context

Assistant 2
才算Loss
```

所以：

> Loss Mask 是 Dataset Design 的一部分。

不是一个永远固定的 API 参数。

---

# 二十八、政府采购模型第一版建议怎么办？

为了让第一版足够清晰：

# `ProcurementLM_V0.1`

先优先使用：

```text
单轮任务
或
简单多轮任务
```

核心形式：

```text
System
+
User
→
Assistant
```

并采用：

```text
Assistant Response Loss
```

先把训练逻辑跑稳。

不要第一版就搞：

> 十几轮复杂 Agent 对话。

---

# 二十九、System Prompt 应该负责什么？

例如：

```text
你是一名政府采购风险审查助手。
你的任务是进行潜在风险筛查。
不要将风险筛查结果表述为最终法律结论。
证据不足时应明确说明需要进一步复核。
```

System Prompt 的作用是：

> 定义角色和稳定行为边界。

但要注意：

> 它不能代替训练数据。

---

# 三十、一个常见错误：把所有专业知识全塞进 System Prompt

例如 System Prompt 写成：

```text
1. 地域限制是……
2. 资格条件是……
3. 技术参数是……
4. 评分规则是……
……
共12000字
```

然后每个 Sample 重复一遍。

结果：

```text
大量重复Token
+
训练成本增加
+
真正样本内容占比下降
```

不是好设计。

System Prompt 应该：

> 简洁、稳定、定义任务。

具体知识：

> 放在训练样本、RAG 或任务上下文里。

---

# 三十一、Prompt 应该提供“真实推理时能获得的东西”

这和第四课的 Input Firewall 完全接上了。

Prompt 可以有：

```text
目标条款
父章节
必要上下文
项目类型
```

前提是：

> 上线推理时也能得到。

不要包含：

```text
专家最终结论
裁决备注
未来投诉结果
Benchmark标签
```

否则：

> SFT 直接产生 Leakage。

---

# 三十二、所以第四课和第五课在这里真正接上了

第四课建立：

```text
Input Field
Target Field
Audit Field
```

第五课现在把它映射成：

```text
Input Field
        ↓
Prompt

Target Field
        ↓
Assistant Response

Audit Field
        ↓
禁止进入普通训练输入
```

这条映射非常重要。

---

# 三十三、`SFTTrainingExample_V0.1` 应该长什么样？

我们现在可以正式设计。

Canonical 数据建议保留：

```json
{
  "sample_id": "SAMPLE-00178",

  "messages": [
    {
      "role": "system",
      "content": "你是一名政府采购风险审查助手。"
    },
    {
      "role": "user",
      "content": "请判断以下采购条款是否存在潜在风险……"
    },
    {
      "role": "assistant",
      "content": "该条款存在潜在风险……"
    }
  ],

  "split": "train",

  "chat_template_version": "base_model_native",
  "loss_policy": "assistant_only",

  "source_dataset_version": "ProcurementDataset_V0.1"
}
```

注意：

这里最好保存：

# Messages

作为高层训练语义。

而不是一开始就只保存：

```text
1745, 9182, 315...
```

---

# 三十四、为什么不建议把 `input_ids` 当成唯一真相源？

因为：

```text
Tokenizer
```

可能升级。

Base Model：

> 可能更换。

Chat Template：

> 可能调整。

一旦只剩 Token IDs：

> 很难知道它原本代表什么。

所以建议：

\[
\boxed{
Messages
=
SemanticSource
}
\]

而：

```text
input_ids
labels
loss_mask
```

属于：

# Derived Training Artifacts
## 派生训练产物

---

# 三十五、也就是说第五课会有两层数据

第一层：

# Semantic Training Example

```text
messages
role
content
```

第二层：

# Tokenized Training Example

```text
input_ids
attention_mask
labels
```

关系是：

```text
Semantic Example
        ↓
Template + Tokenizer
        ↓
Tokenized Example
```

---

# 三十六、这里再增加一个非常重要的字段

# `chat_template_version`

为什么？

假设：

```text
ProcurementLM experiment A
```

用：

```text
Template v1
```

实验 B：

```text
Template v2
```

结果不同。

如果你没有记录：

> 两个实验为什么不同很难解释。

---

# 三十七、Tokenizer Version 也要记录

以后模型实验最好记录：

```text
base_model
tokenizer
chat_template
dataset
loss_policy
```

这和第四课 Dataset Manifest 是同一种工程思想：

# Reproducibility
## 可复现性

---

# 三十八、真正检查一条 SFT 数据时，不要只看 JSON

这是一个非常重要的实战习惯。

训练前一定要：

# Decode and Inspect
## 解码检查

也就是说：

把 Tokenizer 之后的数据重新 Decode 出来。

确认模型真正看到的是：

```text
System:
...

User:
...

Assistant:
...
```

而不是：

```text
<unk><unk>
重复BOS
少了Assistant标记
答案被截掉一半
```

---

# 三十九、甚至还应该可视化 Loss Mask

例如：

```text
[System]        灰色
你              灰色
是              灰色
采购            灰色

[User]          灰色
请              灰色
判断            灰色

[Assistant]     灰色
存在            ★
潜在            ★
风险            ★
EOS             ★
```

★：

> 计算 Loss。

灰色：

> 只提供 Context。

如果训练前能看懂这张图：

> 很多 SFT Bug 会在训练之前就被发现。

---

# 四十、第五课第 1 阶段最值得做的实际检查

每次换：

```text
Base Model
Tokenizer
Chat Template
```

先拿：

# 3～10 条样本

不要训练。

只检查：

```text
原始messages
        ↓
apply_chat_template
        ↓
tokenize
        ↓
input_ids
        ↓
labels
        ↓
decode
        ↓
loss mask
```

确认全部正确：

> 再跑几万条数据。

---

# 四十一、这其实和第四课 Pilot Annotation 是同一种思想

第四课：

```text
先标100条
发现Schema问题
```

第五课：

```text
先Tokenize几条
发现Training Format问题
```

共同原则：

\[
\boxed{
SmallValidation
Before
LargeScaleRun
}
\]

中文：

> **大规模运行之前，先用极小样本把逻辑验证正确。**

---

# 四十二、一个最危险的 SFT Bug：答案根本没算 Loss

比如 Mask 写反：

```text
Prompt
✓ ✓ ✓ ✓

Assistant
× × × ×
```

训练照样：

> 可以跑。

GPU：

> 也在算。

甚至 Loss：

> 也可能有数字。

但模型：

> 根本没有在学习你真正想学的 Response。

所以：

# Training Runs ≠ Training Is Correct

---

# 四十三、另一个危险 Bug：Prompt 也全部算 Loss

变成：

```text
System     ✓
User       ✓
Assistant  ✓
```

模型会同时学习：

```text
怎样扮演用户
怎样重复固定System Prompt
怎样生成Assistant答案
```

不一定完全不能用。

但它已经：

> 偏离了我们设计的训练目标。

---

# 四十四、第三个危险 Bug：Assistant 起始位置错一位

例如真正应该：

```text
<assistant>
存在潜在风险
```

但 Mask 从：

```text
潜在
```

才开始。

那么：

```text
“存在”
```

永远没有监督。

这种 Token Alignment Bug：

> 肉眼看 Dataset 完全看不出来。

只有检查：

```text
input_ids
labels
```

才能发现。

---

# 四十五、第四个危险 Bug：EOS 被 Mask 掉

如果模型从来没有学习答案结束：

> 推理时可能非常啰嗦或重复。

所以是否保留：

```text
EOS Loss
```

需要明确。

对我们第一版：

> 通常应该让 Assistant 结束 Token 也参与正确训练。

---

# 四十六、第五个危险 Bug：训练格式和推理格式不一致

训练：

```text
### User:
...
### Assistant:
```

上线推理：

```text
<|im_start|>user
...
```

模型接受到的结构分布完全不同。

所以：

\[
\boxed{
TrainFormat
\approx
InferenceFormat
}
\]

最好保持一致。

---

# 四十七、这叫 Train–Inference Alignment

# Train–Inference Alignment
## 训练—推理格式对齐

训练时模型看到什么协议：

上线最好：

> 尽量使用同一协议。

否则可能产生：

# Distribution Shift
## 输入分布变化

---

# 四十八、到这里，可以把今天最重要的工程原则压成一张表

| 层 | 核心问题 |
|---|---|
| **Messages** | 谁说什么？ |
| **Chat Template** | 模型怎样识别角色？ |
| **Tokenizer** | 文本怎样变 Token？ |
| **input_ids** | 模型到底看到什么？ |
| **labels** | 正确答案 Token 是什么？ |
| **Loss Mask** | 哪些位置真正算 Loss？ |
| **EOS** | 模型什么时候停止？ |
| **Template Version** | 以后能不能复现？ |

这 8 个问题如果全部回答清楚：

> SFT 数据层基本不会糊涂。

---

# 四十九、现在做一个 ProcurementAI 完整示例

原始数据：

```text
条款：
供应商须在本市设立固定服务机构方可参与投标。
```

专家 Label：

```text
risk_present = true
risk_type = supplier_qualification
```

专家理由：

```text
将投标前本地固定服务机构作为参与条件，
需要审查其与实际采购需求之间的必要性。
```

---

## Step A：构造 Messages

```text
SYSTEM

你是一名政府采购风险审查助手。
你的任务是进行潜在风险筛查。
不得将筛查结果直接表述为最终法律结论。
```

```text
USER

请审查以下采购条款：

供应商须在本市设立固定服务机构方可参与投标。

请输出：
1. 风险判断
2. 风险类型
3. 简要理由
```

```text
ASSISTANT

风险判断：存在潜在风险。

风险类型：供应商资格条件。

简要理由：
该条款将投标前已经具备本地固定服务机构作为参与条件，
需要进一步审查该要求与项目实际需求之间的必要性和合理性。
```

---

## Step B：Chat Template

概念上：

```text
<system>
SYSTEM TEXT
</system>

<user>
USER TEXT
</user>

<assistant>
ASSISTANT TEXT
</assistant>
```

---

## Step C：Tokenizer

最终：

```text
input_ids
=
[
  system tokens,
  user tokens,
  assistant tokens,
  EOS
]
```

---

## Step D：Labels

```text
System Tokens
→ -100

User Tokens
→ -100

Assistant Role Prefix
→ 根据具体模板策略

Assistant Answer
→ 原Token ID

EOS
→ 原Token ID
```

---

## Step E：Loss

只在：

```text
风险判断……
风险类型……
简要理由……
EOS
```

这些目标位置上：

> 产生主要训练 Loss。

---

## Step F：Gradient

这些错误：

```text
模型认为应该回答“No Risk”
```

就会产生较大 Loss。

然后：

```text
Loss
↓
Backward
↓
Gradient
↓
LoRA参数更新
```

这就是：

> **专家知识第一次真正开始进入模型参数。**

---

# 五十、为什么这一阶段比 LoRA 参数更重要？

很多人学微调直接搜索：

```text
LoRA rank多少？
alpha多少？
learning rate多少？
```

但如果你的：

```text
Chat Template错
Loss Mask错
Response边界错
EOS错
```

那么：

> 再漂亮的 LoRA 参数也救不了。

所以训练优先级应该是：

```text
1 数据语义正确

2 Chat Template正确

3 Loss Target正确

4 Tokenization正确

5 再谈LoRA超参数
```

这才是正确顺序。

---

# 五十一、第五课第一阶段的专业化工程产物

我们现在正式得到：

# `SFTTrainingExample_V0.1`

它包含两个层次。

### 语义层

```text
sample_id
system
user
assistant
split
dataset_version
```

### 训练派生层

```text
input_ids
attention_mask
labels
chat_template_version
tokenizer_version
loss_policy
```

其中最重要的一条原则：

> **语义数据是源，Token 数据是派生结果。**

---

# 五十二、这一阶段的几个反例

### 反例 1

把：

```text
Prompt + Gold Label + Expert Comment
```

全部拼成 Input。

结果：

> Label Leakage。

---

### 反例 2

手工设计 Chat Template，却完全无视 Base Model 原生模板。

结果：

> 模型要额外学习新的通信协议。

---

### 反例 3

只检查原始 JSON，不检查 Tokenization 结果。

结果：

> Token 边界错误完全发现不了。

---

### 反例 4

Mask 所有位置都为 1。

结果：

> 模型连 User Prompt 都在学习生成。

---

### 反例 5

Mask 所有位置都为 0。

结果：

> 没有有效监督信号。

---

### 反例 6

Train 用一套格式，Inference 用另一套格式。

结果：

> Train–Inference Misalignment。

---

# 五十三、把这一阶段再压缩成最精准的 5 句话

如果明天你只能记住第五课第一阶段五句话，请记这五句：

> **第一，模型最终训练的不是 JSON、Prompt 或问答表，而是一条 Token 序列。**

> **第二，Chat Template 是 Base Model 的对话通信协议，不是排版装饰。**

> **第三，Prompt 是模型必须看到的条件，Response 是我们主要希望它学习生成的目标。**

> **第四，Loss Mask 决定哪些 Token 真正产生梯度；不算 Loss 不代表模型看不见这些 Token。**

> **第五，训练前必须把少量样本完整 Decode，并检查 `input_ids → labels → Loss Mask`，确认正确以后才允许大规模训练。**

如果这五句完全理解：

> 第五课后面的 LoRA / QLoRA 会容易很多。

---

# 五十四、本阶段最核心的一张图

```text
ProcurementDataset_V0.1
          │
          ▼
      Messages
  System/User/Assistant
          │
          ▼
    Chat Template
      对话协议
          │
          ▼
      Tokenizer
          │
          ▼
       input_ids
    模型看到全部Token
          │
          ├────────────────────┐
          │                    │
          ▼                    ▼
     Prompt Tokens       Response Tokens
       条件信息              目标答案
          │                    │
          ▼                    ▼
      labels=-100         labels=TokenID
          │                    │
          └──────────┬─────────┘
                     ▼
                  Loss
                     │
                     ▼
                 Gradient
                     │
                     ▼
               LoRA / Model
                 参数更新
```

如果这张图能在脑子里直接浮现：

> 今天这一阶段已经掌握了一大半。

---

# 五十五、本阶段掌握测试

现在不回看正文，试着回答下面的问题。

为什么 Chat Template 不是简单排版？为什么模型最终看到的并不是 `role=user` 这样的 JSON 字段，而是 Token？Prompt Token 为什么通常不计算 Loss，但模型仍然可以利用它们？`input_ids` 和 `labels` 有什么本质区别？为什么常见训练中会把某些 Label 设成 `-100`？`-100` 是否意味着模型无法 Attention 到这些 Token？为什么 Assistant-only Loss 很适合我们第一版政府采购 SFT？为什么 SFT 本质仍然是 Next Token Prediction？为什么 EOS 也属于非常重要的训练目标？Chat Template 和 Tokenizer 为什么必须匹配 Base Model？为什么 Training Format 和 Inference Format 应该尽量一致？为什么不能只看原始 JSON，一定要检查 Decode 后的 Token 序列和 Loss Mask？如果 Assistant Response 被全部 Mask 掉，会发生什么？如果整个 Prompt 也参与 Loss，会发生什么？为什么第四课的 Input / Target / Audit 三类字段到了第五课正好对应 Prompt / Response / 禁止输入的信息？

如果这些都能够自己解释：

\[
\boxed{
第五课第1阶段真正掌握
}
\]

---

# 本阶段最后只记一句话

> **SFT 的第一步不是设置 LoRA，而是把一条专家数据精确地变成“模型能识别的对话 Token 序列”，再用 Loss Mask 明确告诉训练系统：Prompt 是条件，Assistant Response 才是主要学习目标；只有 `Messages → Chat Template → Tokenizer → input_ids → labels → Loss → Gradient` 这条链完全正确，专家知识才真正开始进入模型。**

---

# 下一阶段：第五课 · 第 2 阶段
# SFT 到底在训练什么？

第一阶段我们解决了：

> **哪些 Token 应该学。**

第二阶段会继续追到模型内部：

> **当一个 Assistant Token 预测错以后，Loss 究竟怎样通过 Backpropagation 一路传到 Transformer，再传到 LoRA 参数？**

我们会把整个过程压成一条真正能在脑中运行的链：

```text
Prompt
  ↓
Forward
  ↓
Logits
  ↓
Probability
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

并真正回答：

> **一次 SFT Step 到底发生了什么。**

---
