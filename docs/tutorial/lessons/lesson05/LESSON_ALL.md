# 第五课：SFT + LoRA / QLoRA 微调

> **V2 教学增强版。** 共 14 个阶段；主要产物/主线：`ProcurementLM_V0.1`。  
> 核心心智模型前置、中文释义增强、详细正文完整保留。

---


<!-- LESSON 05 STAGE 01 START -->

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

<!-- LESSON 05 STAGE 01 END -->


<!-- LESSON 05 STAGE 02 START -->

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

<!-- LESSON 05 STAGE 02 END -->


<!-- LESSON 05 STAGE 03 START -->

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

<!-- LESSON 05 STAGE 03 END -->


<!-- LESSON 05 STAGE 04 START -->

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

<!-- LESSON 05 STAGE 04 END -->


<!-- LESSON 05 STAGE 05 START -->

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

<!-- LESSON 05 STAGE 05 END -->


<!-- LESSON 05 STAGE 06 START -->

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

<!-- LESSON 05 STAGE 06 END -->


<!-- LESSON 05 STAGE 07 START -->

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

<!-- LESSON 05 STAGE 07 END -->


<!-- LESSON 05 STAGE 08 START -->

# 第五课 · 第 8 阶段
# Target Modules：LoRA 到底插在哪里？
## `q_proj`、`k_proj`、`v_proj`、`o_proj` 和 MLP，到底该训练哪些？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **A 容量一定更大，因为 64 > 16。**
2. **“Rank 用多少？”**
3. **Rank 多大，并且 LoRA 装在哪里？**
4. **只训练 Attention 和同时训练 MLP，给模型的适配自由度是不一样的。**
5. **“知识全在 MLP。”**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Target Modules` | 目标模块：指定 LoRA 插入哪些线性层 |
| `LoRA` | LoRA：冻结大部分基座参数，只训练低秩增量矩阵 |
| `MLP` | MLP/前馈网络：对每个位置表示做非线性变换 |
| `Attention` | 注意力：根据内容相关性动态聚合信息 |
| `Rank` | LoRA Rank：低秩增量的容量参数 |
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

到现在，我们已经理解：

\[
\Delta W = BA
\]

也知道了：

```text
Rank
=
每个 LoRA Adapter 有多少容量
```

但还有一个比 Rank 更基础的问题：

> **这个 Adapter 到底装在哪个权重矩阵上？**

因为 Transformer 里不是只有一个 \(W\)。

一层里就可能有：

```text
Attention
├── q_proj
├── k_proj
├── v_proj
└── o_proj

MLP
├── gate_proj
├── up_proj
└── down_proj
```

LoRA 不需要天然装到所有地方。

你必须决定：

> **哪些计算路径允许政府采购数据去修改。**

这就是今天的核心：

# Target Modules
## LoRA 目标模块

本阶段最终形成：

# `LoRATargetModulePolicy_V0.1`

---

# 一、本阶段只解决一个核心问题

假设某个 Transformer 权重：

\[
W_m
\]

被选为 LoRA Target Module。

那么：

\[
W_m'
=
W_m
+
\frac{\alpha}{r}B_mA_m
\]

如果它**没有**被选中：

\[
W_m'=W_m
\]

继续冻结。

所以 Target Modules 本质上是在回答：

> **Transformer 的哪些矩阵拥有“可学习的领域修正通道”？**

整个流程先锁成这一张图：

```text
                    Transformer Layer
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
         Attention                      MLP
             │                           │
     ┌───────┼───────┐           ┌───────┼───────┐
     ▼       ▼       ▼           ▼       ▼       ▼
   q_proj  k_proj  v_proj      gate    up      down
     │       │       │
     └── o_proj ─────┘

             ↓ Target Modules 决策

        哪些 W 保持完全 Frozen？
        哪些 W 旁边增加 LoRA ΔW？
```

一句话压缩：

> **Rank 决定“改多宽”，Target Modules 决定“改哪里”。**

---

# 二、先锁死 5 个核心心智模型

## 心智模型 1：Target Modules 决定“修改路径”，Rank 决定“修改容量”

这两个必须彻底分开。

假设：

```text
配置 A

r = 64
只给 q_proj 装 LoRA
```

另一组：

```text
配置 B

r = 16
给 q/k/v/o + MLP
全部装 LoRA
```

你不能简单说：

> A 容量一定更大，因为 64 > 16。

因为真实可训练空间同时受：

\[
\boxed{
Rank
\times
TargetModules
\times
Layers
}
\]

影响。

所以以后不要只问：

> “Rank 用多少？”

要问：

> **Rank 多大，并且 LoRA 装在哪里？**

---

## 心智模型 2：Attention Modules 和 MLP Modules 改的是不同计算路径

极简理解：

```text
Attention
更直接参与：
当前 Token 如何从上下文读取、组合信息

MLP
更直接参与：
读取后的表示怎样被非线性转换、重编码
```

因此：

> 只训练 Attention 和同时训练 MLP，给模型的适配自由度是不一样的。

注意，这只是工程直觉。

不能简单粗暴地说：

> “知识全在 MLP。”

或者：

> “推理全在 Attention。”

真实能力是整个网络共同产生的。

---

## 心智模型 3：`q/k/v/o` 不是四个同义矩阵

它们都属于 Attention，但角色不同。

非常粗略地记：

```text
q_proj
当前 Token 用什么表示去“寻找”相关信息

k_proj
上下文信息以什么表示被“匹配”

v_proj
匹配到以后真正携带什么内容

o_proj
多头 Attention 的结果怎样重新投回主表示空间
```

这不是四个装饰性的名字。

它们控制的是：

> Attention 计算不同阶段的表示变换。

---

## 心智模型 4：Target Modules 越多，自由度和成本通常都越大，但不保证业务效果越好

更多模块：

```text
Trainable Parameters ↑
Adapter Size ↑
Optimizer State ↑
训练计算 ↑
适配自由度 ↑
```

同时也可能：

```text
过拟合空间 ↑
实验变量 ↑
调试难度 ↑
```

所以：

\[
\boxed{
MoreTargetModules
\neq
AutomaticallyBetter
}
\]

真正要找的是：

> **完成任务所需的足够修改范围。**

---

## 心智模型 5：模块选择最终必须靠 Benchmark，而不是模块名称的“听感”

`q_proj` 看起来重要。

`v_proj` 也看起来重要。

MLP 更看起来重要。

但真正问题不是：

> 哪个名字更高级？

而是：

```text
固定 Dataset
+
固定 Rank / Alpha
+
改变 Target Modules
+
验证 Validation / Hard Case
```

所以：

\[
\boxed{
TargetModuleChoice
=
EmpiricalDesignDecision
}
\]

---

# 三、重新把 Attention 拉回来

第二课我们已经学过：

\[
Q=XW_Q
\]

\[
K=XW_K
\]

\[
V=XW_V
\]

Attention：

\[
Attention(Q,K,V)
=
Softmax
\left(
\frac{QK^T}{\sqrt{d_k}}
\right)V
\]

最后还通常有：

\[
O = Attention(Q,K,V)W_O
\]

对应到代码名称，大致就是：

```text
W_Q → q_proj
W_K → k_proj
W_V → v_proj
W_O → o_proj
```

LoRA 所做的事情就是：

> 对其中选中的某些 \(W\)，允许增加一个低秩 \(\Delta W\)。

---

# 四、`q_proj`：改变“当前表示怎样提出查询”

原本：

\[
Q=XW_Q
\]

加 LoRA 后：

\[
Q
=
X
\left(
W_Q+\Delta W_Q
\right)
\]

其中：

\[
\Delta W_Q=B_QA_Q
\]

直觉上，它会影响：

> 当前 Token 用怎样的内部表示去匹配上下文。

放到政府采购场景里，可以粗略理解：

模型看到：

```text
投标人在投标截止日前
须已在本市设立固定服务机构
```

它到底更重视：

```text
“本市”
```

还是更重视：

```text
“投标截止日前”
+
“须已设立”
+
“参与资格”
```

其中一部分适配可能通过 Query 表示改变而实现。

再次强调：

> 这不是“q_proj 专门存判断规则”。

而是它改变 Attention 中查询表示形成的方式。

---

# 五、`k_proj`：改变“上下文怎样被建立匹配索引”

Key 可以粗略理解成：

> 每个上下文位置拿什么表示参与 Query–Key 匹配。

于是：

\[
K=XW_K
\]

加 LoRA：

\[
K
=
X
\left(
W_K+\Delta W_K
\right)
\]

它会影响：

> 哪些上下文位置与当前 Query 更容易形成高匹配。

例如：

```text
资格条件
投标前
本地机构
中标后
服务响应
```

哪些信息之间应该建立更强的关系，

理论上都可能受到 K 路径适配的影响。

---

# 六、`v_proj`：改变“被读取的信息实际携带什么表示”

Attention 权重最终作用在：

\[
V
\]

上。

所以 V 可以粗略记成：

> **匹配完成以后，被带走的内容表示。**

公式：

\[
V=XW_V
\]

LoRA：

\[
V
=
X
\left(
W_V+\Delta W_V
\right)
\]

因此调整 `v_proj`：

> 会改变上下文信息被 Attention 读取后，以怎样的内部表示传递出去。

这也是为什么 `q_proj` / `v_proj` 经常会作为一个简洁 LoRA Baseline 的候选组合。

---

# 七、`o_proj`：改变 Attention 结果怎样重新写回主表示流

Attention 并不是最终直接结束。

多个 Head 产生的结果还需要重新映射：

\[
H_{\text{attn}}
W_O
\]

也就是：

```text
o_proj
```

可以粗略理解：

> **Attention 已经读到的信息，怎样重新整合进模型的 Residual Stream。**

所以：

```text
q/k/v
```

主要影响：

> Attention 内部怎样构造和读取信息。

而：

```text
o_proj
```

影响：

> 读取结果怎样重新进入后续 Transformer 计算。

---

# 八、现在进入 MLP：`gate_proj / up_proj / down_proj`

现代 LLM 的 MLP 往往不只是一个简单：

\[
Wx
\]

例如常见门控 MLP 可以抽象成：

\[
MLP(x)
=
W_{down}
\left[
\sigma(W_{gate}x)
\odot
(W_{up}x)
\right]
\]

具体不同模型会不同。

但核心结构可以理解成：

```text
hidden state
     │
     ├── gate_proj
     │
     └── up_proj
           │
           ▼
     高维中间表示
           │
           ▼
       down_proj
           │
           ▼
回到 hidden dimension
```

所以 MLP 是：

> Transformer 中另一个非常大的表示变换路径。

---

# 九、三个 MLP Projection 怎么理解？

不需要死抠名字。

### `up_proj`

大致把：

\[
d_{model}
\]

映射到更高的中间维度。

可以记成：

> **展开表示空间。**

---

### `gate_proj`

与门控激活一起：

> 决定哪些中间特征被激活和保留。

可以记成：

> **控制特征通路。**

---

### `down_proj`

最后把高维中间表示：

> 压回模型 Hidden Size。

可以记成：

> **把转换后的特征重新写回主表示流。**

因此：

```text
Attention
=
怎么读取上下文

MLP
=
读完以后怎样转换表示
```

作为长期直觉已经够用了。

---

# 十、所以 LoRA Target Modules 实际上有几种典型“范围”

为了建立清晰心智模型，可以把它分成三档。

### 窄范围

```text
q_proj
v_proj
```

特点：

> 参数少、实验简单、训练成本低。

适合：

> 做一个非常轻量的 Baseline。

---

### Attention 全投影

```text
q_proj
k_proj
v_proj
o_proj
```

意味着：

> 整个 Attention Projection 路径都获得 LoRA 适配能力。

相比 q/v：

> 修改范围更广。

---

### Attention + MLP

```text
q_proj
k_proj
v_proj
o_proj
gate_proj
up_proj
down_proj
```

这通常意味着：

> Transformer Layer 中主要 Linear Projection 都获得低秩适配能力。

适配容量明显更大。

同时：

> 参数量和训练成本也更高。

---

# 十一、为什么不能直接永远选择“全部 Linear”？

因为我们真正追求的是：

\[
\boxed{
MinimumSufficientAdaptation
}
\]

而不是：

\[
MaximumPossibleAdaptation
\]

例如：

```text
q/v 已经能让
Procurement Benchmark
达到目标
```

那么增加：

```text
k/o + MLP
```

如果没有明显业务收益，

就只是在增加：

```text
参数
成本
Checkpoint
实验复杂度
```

没有必要。

---

# 十二、反过来，为什么不能永远只用 `q_proj + v_proj`？

因为任务可能需要：

> 更广泛地调整 Transformer 内部表示。

如果出现：

```text
简单格式学会了

基础分类学会了

但复杂决策边界长期不足

增加 Rank 收益很小

数据与训练配置已确认正常
```

这时候真正的瓶颈可能不是：

> Adapter 不够宽。

而是：

> **允许修改的模型路径太窄。**

也就是：

# Module Coverage Bottleneck

这时候扩大 Target Modules：

> 可能比继续堆 Rank 更合理。

---

# 十三、Rank 和 Target Modules 是两个完全不同的扩容方向

这是今天最重要的工程判断之一。

### 增大 Rank

```text
原来的模块
装更宽的 Adapter
```

回答：

> **同一个地方多给一些修改容量。**

---

### 增加 Target Modules

```text
让更多模型路径
可以被修改
```

回答：

> **扩大可以动手术的位置。**

所以：

\[
\boxed{
IncreaseRank
\neq
IncreaseModuleCoverage
}
\]

一个是：

> 深一点。

一个是：

> 广一点。

---

# 十四、总 LoRA 参数量到底怎么计算？

如果 Target Modules 有多个，

总参数量大致就是：

\[
N_{\text{LoRA,total}}
=
\sum_{m\in M}
r_m
\left(
d_{in,m}+d_{out,m}
\right)
\]

其中：

\[
M
\]

就是：

> 所有 Target Modules。

如果所有模块 Rank 相同：

\[
r_m=r
\]

那么模块越多：

> 总可训练参数自然越多。

所以实际实验必须记录：

```text
Target Modules
+
Rank
+
Trainable Parameter Count
```

而不能只保存：

```text
r = 16
```

---

# 十五、这里还有一个重要现实：不同 Base Model 的模块名称并不完全一样

不要认为所有模型一定叫：

```text
q_proj
k_proj
v_proj
o_proj
```

有些架构：

> 名字不同。

有些：

> QKV 可能采用组合投影。

还有些模型使用：

```text
Grouped Query Attention
Multi-Query Attention
```

此时 Q、K、V 的维度甚至可能不同。

所以真正开始训练以前：

> **必须检查 `model.named_modules()` 或模型架构，而不是照抄别人模型的 `target_modules`。**

这是非常关键的工程习惯。

---

# 十六、最危险的 Bug：你以为装了 LoRA，其实根本没装到目标层

例如配置：

```python
target_modules=["q_proj", "v_proj"]
```

但当前 Base Model：

> 实际模块命名完全不同。

轻则：

> 框架直接报错。

更危险的情况是：

> 部分匹配错误或训练范围和预期不同。

所以训练前必须打印：

```text
Matched Target Modules
```

以及：

```text
Trainable Parameter Count
```

确认：

> LoRA 到底被插进了哪里。

---

# 十七、第一版 ProcurementLM 怎么选更专业？

不要一开始做几十组组合爆炸。

建议建立三档实验。

```text
Experiment A
Narrow Baseline

q_proj
v_proj
```

```text
Experiment B
Attention Coverage

q_proj
k_proj
v_proj
o_proj
```

```text
Experiment C
Broad Linear Coverage

q_proj
k_proj
v_proj
o_proj
gate_proj
up_proj
down_proj
```

然后：

> Rank、Alpha、Learning Rate 等主要变量尽量固定。

比较：

```text
Validation
Hard Negative
Boundary Case
General Capability Regression
Trainable Parameters
Training Cost
```

这才真正回答：

> 扩大修改范围是否值得。

---

# 十八、一个 ProcurementAI 的诊断例子

假设配置 A：

```text
q_proj + v_proj

r = 16
```

结果：

```text
输出格式             很好
简单风险识别         很好
Hard Negative        一般
复杂理由              一般
Boundary Case         较弱
```

第一反应不要立刻：

```text
r = 128
```

而应该建立两个假设：

```text
假设 1
当前模块已经合适
只是容量不够

→ 增大 Rank
```

```text
假设 2
修改路径太窄

→ 扩大 Target Modules
```

然后：

> 做控制变量实验。

这就是专业调参和“玄学调参”的区别。

---

# 十九、哪些东西第一版通常不要随便动？

例如：

```text
Embedding
LM Head
LayerNorm
```

不是说：

> 永远不能训练。

而是第一版 LoRA Baseline：

> 没有充分证据时，不要为了“多训练一些”随意把所有模块都纳入。

原因非常简单：

> 每增加一类 Trainable Scope，都增加新的实验变量。

第一版最重要的是：

# Attribution
## 可归因性

也就是：

> 模型为什么变好或变坏，我们能够解释。

---

# 二十、Target Modules 和模型能力不是一一对应关系

这是一个必须纠正的直觉。

不要说：

```text
q_proj
=
学习推理

v_proj
=
学习知识

MLP
=
储存知识
```

这种说法太绝对。

正确理解是：

> 不同模块承担不同数学计算角色，但最终语言能力、知识使用、推理行为都是整个 Transformer 联合形成的。

因此 Target Modules 选择：

> 不是把业务需求机械映射成某个单独矩阵。

而是：

> 决定允许哪些计算路径获得任务适配自由度。

---

# 二十一、我们现在可以建立一个非常清楚的调参顺序

不要这样：

```text
模型效果不好
↓
Rank改
Alpha改
Dropout改
Modules改
LR改
全部一起改
```

应该：

```text
Step 1
确认 Dataset / Mask / Training 正确

        ↓

Step 2
建立稳定 Target Module Baseline

        ↓

Step 3
确认 Rank 是否足够

        ↓

Step 4
如果出现 Module Coverage Bottleneck
再扩大 Target Modules

        ↓

Step 5
用 Benchmark 判断收益是否值得成本
```

这样每一次变化：

> 都有解释。

---

# 二十二、这一阶段最重要的“模块地图”

| 模块 | 所处位置 | 最简工程直觉 |
|---|---|---|
| `q_proj` | Attention | 当前表示怎样构造 Query |
| `k_proj` | Attention | 上下文怎样构造 Key 参与匹配 |
| `v_proj` | Attention | 被读取的信息携带什么表示 |
| `o_proj` | Attention | Attention 结果怎样写回主表示 |
| `gate_proj` | MLP | 中间特征怎样被门控 |
| `up_proj` | MLP | 怎样扩展到中间表示空间 |
| `down_proj` | MLP | 怎样压回 Hidden Size |

这张表不是让你背定义。

它是让你看到：

> **选择 Target Modules，其实是在选择允许修改 Transformer 的哪些计算路径。**

---

# 二十三、本阶段工程产物：`LoRATargetModulePolicy_V0.1`

正式记录至少应该包括：

```text
base_model
base_model_revision

architecture_family

available_linear_modules

target_modules

excluded_modules

target_layer_scope

rank
alpha
dropout

matched_module_count

trainable_parameter_count
trainable_parameter_ratio

target_module_policy_version
```

训练启动前必须额外验证：

```text
1. 配置中的模块名称真实存在

2. 匹配数量符合预期

3. Trainable Parameter Count 符合预期

4. Base Parameters 仍正确 Frozen

5. Adapter 确实只出现在目标模块
```

这一步叫：

# Adapter Injection Audit
## Adapter 注入审计

---

# 二十四、本阶段最危险的 6 个反例

**第一，只看 Rank，不看 Target Modules。**  
LoRA 总容量同时取决于“每个 Adapter 多宽”和“装了多少位置”。

**第二，认为 q/k/v/o 都做同一件事。**  
它们处于 Attention 的不同变换阶段。

**第三，认为 MLP 只是附属模块。**  
它是 Transformer 中极大的表示变换路径之一。

**第四，一上来就 `all-linear`，然后发现效果好，却不知道究竟哪些模块带来了收益。**  
失去实验可归因性。

**第五，把别的模型的 `target_modules` 原样复制。**  
不同架构的模块命名和形状可能不同。

**第六，配置写完以后不检查真正 Trainable Parameters。**  
你以为在训练的东西和实际训练的东西可能不是一回事。

---

# 二十五、现在把本阶段压成最精准的 5 句话

> **第一，Rank 决定 LoRA 在一个目标矩阵上“能改多宽”，Target Modules 决定 Transformer “哪些计算路径允许被改”。**

> **第二，`q/k/v/o` 分别参与 Attention 的 Query、Key、Value 和输出投影；MLP 的 `gate/up/down` 则参与后续非线性表示转换。**

> **第三，增加 Rank 和增加 Target Modules 是两种不同扩容方式：一个增加局部容量，一个扩大修改覆盖范围。**

> **第四，更多 Target Modules 会增加可训练参数和适配自由度，但是否带来真实业务收益必须由 Validation、Hard Case 和成本共同判断。**

> **第五，永远不要照抄模块名称；训练前必须检查模型真实架构、实际匹配模块和 Trainable Parameter Count。**

如果这五句能脱口而出：

> Target Modules 就不再是配置文件里一串莫名其妙的字符串。

---

# 二十六、本阶段最核心的一张图

```text
                     Transformer Layer
                            │
            ┌───────────────┴───────────────┐
            │                               │
            ▼                               ▼
        Attention                          MLP
            │                               │
   ┌────────┼────────┐             ┌────────┼────────┐
   ▼        ▼        ▼             ▼        ▼        ▼
 q_proj   k_proj   v_proj       gate      up       down
   │                 │
   └────── o_proj ───┘
            │
            ▼
       Target Modules
            │
      哪些位置加 LoRA？
            │
            ▼
   Frozen W + ΔW=BA
            │
            ▼
       Trainable Scope
            │
     ┌──────┴───────┐
     ▼              ▼
  Rank              Module Coverage
局部容量             修改范围
     │              │
     └──────┬───────┘
            ▼
     Validation / Hard Case
            │
            ▼
   是否值得扩大修改范围？
```

脑中只记：

> **Rank 决定“改多宽”，Target Modules 决定“改哪里”。**

---

# 二十七、本阶段掌握测试

现在不回看正文，你应该能自己解释：Target Modules 到底决定什么；为什么它和 Rank 不是同一个超参数；`q_proj / k_proj / v_proj / o_proj` 在 Attention 中分别处于什么位置；为什么不能简单说“Q 是推理、V 是知识”；MLP 的 `gate/up/down` 大致完成什么计算；为什么 `q+v`、完整 Attention、Attention+MLP 是不同的适配范围；为什么增加 Rank 和增加 Target Modules 是两种不同的扩容方式；为什么模型效果不足不能总靠提高 Rank；什么叫 Module Coverage Bottleneck；为什么不同 Base Model 不能照抄同一组模块名称；为什么训练前必须检查实际匹配模块和 Trainable Parameter Count；为什么第一版不应该没有证据就随便训练 Embedding、LM Head 等更多模块；以及为什么最终模块选择必须回到固定 Benchmark 上验证。

如果这些能够自己讲清楚：

\[
\boxed{
第五课第8阶段真正掌握
}
\]

---

# 本阶段最后只记一句话

> **LoRA 不只是决定“用多大的 Adapter”，还必须决定“把 Adapter 装在哪里”：Rank 控制每个低秩更新的容量，Target Modules 控制哪些 Transformer 计算路径获得领域适配权；专业的模块选择不是把 `q_proj/v_proj` 当口诀，而是先看真实模型架构，再通过可归因的控制实验验证修改范围是否真正改善 Procurement Benchmark。**

---

# 下一阶段：第五课 · 第 9 阶段
# QLoRA 与 4-bit / NF4
## 为什么 Base Model 可以用 4-bit 加载，却仍然能够训练出高质量 LoRA Adapter？

现在我们已经知道：

```text
Base Model
Frozen

+

选定 Target Modules
安装 LoRA

+

A / B
真正训练
```

但还有一个大头：

> **Frozen Base Model 虽然不更新，它依然占显存。**

第 9 阶段会解决：

```text
7B / 14B Base Model
        ↓
4-bit Quantization
        ↓
NF4
        ↓
低显存保存 Frozen Base
        +
BF16 / FP16 等计算路径
        +
LoRA Adapter 继续训练
```

最后真正建立：

> **量化的是谁、谁仍然训练、计算时为什么还能保持足够精度——这三件事必须彻底分开。**

---

<!-- LESSON 05 STAGE 08 END -->


<!-- LESSON 05 STAGE 09 START -->

# 第五课 · 第 9 阶段
# QLoRA 与 4-bit / NF4
## 为什么一个几十亿参数的 Base Model 可以用 4-bit 保存，却仍然能训练出有效的 LoRA Adapter？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Base Model 的存储方式。**
2. **Base Model BF16 / FP16 等 Frozen + LoRA Adapter Trainable**
3. **Base Model 4-bit Quantized Frozen + LoRA Adapter Trainable**
4. **Input Attention MLP Loss Gradient**
5. **全部都只有4-bit**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `LoRA` | LoRA：冻结大部分基座参数，只训练低秩增量矩阵 |
| `QLoRA` | QLoRA：量化基座模型并训练 LoRA，以降低显存成本 |
| `NF4` | NF4：适合近似正态权重的 4 位量化格式 |
| `Adapter` | 适配器：附加在基座模型上的轻量可训练参数模块 |
| `Quantization` | 量化：用更低位宽表示权重/激活以降低显存和计算成本 |
| `BF16` | BF16：保留较大指数范围的 16 位浮点，常用于大模型 |

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

前面我们已经把 LoRA 拆得非常清楚了：

\[
W' = W + \Delta W
\]

其中：

\[
\Delta W = BA
\]

并且：

```text
Base Weight W
=
Frozen

LoRA A / B
=
Trainable
```

到这里，还有一个巨大的工程问题没有解决。

即使：

> Base Model 不训练，

它仍然要：

> **驻留在显存里。**

假设 Base Model 有 7B 参数。

BF16 大致需要：

\[
7\times10^9\times2
\approx14GB
\]

仅仅模型权重就已经非常大。

于是 QLoRA 出现了。

今天要彻底搞懂的不是某个配置参数，而是这条链：

```text
Frozen Base Model
        ↓
4-bit Quantization
低位宽保存
        ↓
Forward 时按需恢复到计算精度
        ↓
Base Path 继续参与计算
        +
LoRA A/B 保持可训练
        ↓
Loss
        ↓
Backward
        ↓
只更新 LoRA
```

最终形成：

# `QLoRAMemoryModel_V0.1`

---

# 一、本阶段只解决一个核心问题

> **QLoRA 到底量化了谁？4-bit 存在哪里？Forward 真的是用 4-bit 做所有计算吗？LoRA 参数又是什么精度？**

先把最重要的一句话放在这里：

\[
\boxed{
QLoRA
\neq
EverythingRunsIn4Bit
}
\]

QLoRA 更准确的理解是：

> **把冻结的 Base Model 权重以低位宽量化形式保存，从而显著减少权重显存；计算时按需要恢复到合适的计算精度，同时继续训练正常的 LoRA Adapter。**

这句话掌握，本阶段已经通了一半。

---

# 二、先锁死 5 个核心心智模型

## 心智模型 1：QLoRA = Quantized Base + Trainable LoRA

普通 LoRA：

```text
Base Model
BF16 / FP16 等
Frozen
      +
LoRA Adapter
Trainable
```

QLoRA：

```text
Base Model
4-bit Quantized
Frozen
      +
LoRA Adapter
Trainable
```

所以：

\[
\boxed{
QLoRA
=
QuantizedFrozenBase
+
LoRA
}
\]

关键变化发生在：

> **Base Model 的存储方式。**

LoRA 的低秩学习思想本身：

> 没有变。

---

## 心智模型 2：4-bit 主要是“权重存储精度”，不是“整个训练过程只有 4-bit”

这是最容易犯的错误。

不要想象：

```text
Input
↓
Attention
↓
MLP
↓
Loss
↓
Gradient

全部都只有4-bit
```

这不是 QLoRA 的正确心智模型。

实际更接近：

```text
GPU显存里
Base Weight
以4-bit形式保存
        ↓
需要做矩阵计算时
        ↓
按块反量化 / Dequantize
        ↓
BF16 / FP16 等计算精度
        ↓
Matrix Multiply
```

所以必须区分：

# Storage Dtype
存储精度

和：

# Compute Dtype
计算精度

两者：

\[
\boxed{
可以不同
}
\]

---

## 心智模型 3：NF4 是一种 4-bit 量化表示，不是“保留四位小数”

NF4：

# NormalFloat 4-bit

它不是：

> “一个浮点数只留 4 位小数。”

4-bit 真正意味着：

> 每个量化值只用大约 4 个二进制位来表示其离散编码。

4 bit 能表示：

\[
2^4=16
\]

种离散状态。

NF4 的设计思路是：

> 针对神经网络权重常见的近似正态分布特性，设计更合适的 16 个表示级别。

所以：

\[
\boxed{
NF4
=
4bit Quantization Format
}
\]

而不是：

\[
4\text{ decimal places}
\]

---

## 心智模型 4：量化一定引入近似误差，QLoRA 的问题不是“有没有误差”，而是“误差是否值得换显存”

原始 Base Weight：

\[
W
\]

量化以后：

\[
Q(W)
\]

再反量化：

\[
\hat W
\]

一般不会满足：

\[
\hat W=W
\]

而更像：

\[
\hat W
=
W+\epsilon_q
\]

其中：

\[
\epsilon_q
\]

就是：

> Quantization Error，量化误差。

所以：

\[
\boxed{
Quantization
=
Compression
+
Approximation
}
\]

真正工程问题是：

> **这点近似误差带来的能力损失，是否远小于我们得到的显存收益？**

答案只能由 Benchmark 判断。

---

## 心智模型 5：QLoRA 大幅减少 Base Weight 显存，但不会把所有训练显存都消灭

训练显存我们已经拆过：

```text
Model Weights
+
Gradients
+
Optimizer States
+
Activations
+
Temporary Buffers
```

QLoRA 非常擅长压缩：

> Frozen Base Model Weights。

LoRA 又大幅减少：

> Trainable Gradient / Optimizer State 对应的参数规模。

但是：

# Activations

仍然存在。

Sequence Length 越长：

> Activation 仍可能很贵。

所以：

\[
\boxed{
QLoRA
\neq
UnlimitedContextForFree
}
\]

这会直接接到下一阶段：

> **训练显存到底花在哪里。**

---

# 三、先精准区分 LoRA 和 QLoRA

| 对象 | LoRA | QLoRA |
|---|---|---|
| Base Model | Frozen | Frozen |
| Base Weight 存储 | 常见 BF16 / FP16 等 | 常见 4-bit |
| LoRA A/B | Trainable | Trainable |
| LoRA 是否低秩 | 是 | 是 |
| Base Weight 是否更新 | 否 | 否 |
| 主要额外目标 | 减少可训练参数 | 再进一步减少 Base Weight 显存 |
| Activation | 仍存在 | 仍存在 |

所以一句话：

> **LoRA 解决“不要训练整个 Base Model”，QLoRA 进一步解决“既然 Base Model 冻结了，能不能连它的显存也省下来”。**

---

# 四、为什么 4-bit 可以省这么多？

假设：

\[
N
\]

个参数。

BF16：

\[
16\text{ bits}
=
2\text{ bytes}
\]

理论权重存储：

\[
Memory_{BF16}
\approx
2N
\]

bytes。

4-bit：

\[
4\text{ bits}
=
0.5\text{ bytes}
\]

理论权重存储：

\[
Memory_{4bit}
\approx
0.5N
\]

所以理想裸权重比例：

\[
\frac{4}{16}
=
\frac14
\]

也就是：

> 4-bit 原始权重编码理论上约为 BF16 的四分之一。

例如 7B：

BF16：

\[
7B\times2
\approx14GB
\]

4-bit 裸编码理论值：

\[
7B\times0.5
\approx3.5GB
\]

但是这里一定要加一句：

> **真实显存不会精确等于 3.5GB。**

因为量化还需要：

```text
Scale
Zero / Quantization Metadata
Block Information
Temporary Buffers
Framework Overhead
其他未量化参数
```

所以：

\[
\boxed{
4bit理论裸权重大小
\neq
实际GPU显存占用
}
\]

---

# 五、量化究竟怎么发生？

不要把量化想成：

> 整个 70 亿参数只找一个最大值，然后压成 16 档。

实际通常会：

# Block-wise Quantization
## 分块量化

也就是把权重分成很多小块。

例如概念上：

```text
Block 1
[w1 w2 w3 ...]
      ↓
找到这个Block自己的缩放信息
      ↓
映射到16个NF4状态

Block 2
[w...]
      ↓
自己的scale
      ↓
映射到16个状态
```

这样相比整个大矩阵只用一个统一尺度：

> 能更好地保留局部数值结构。

所以一个量化权重实际上不仅有：

```text
4-bit codes
```

还需要：

```text
quantization scales / metadata
```

来恢复近似权重。

---

# 六、Forward 时最精准的流程是什么？

这一段非常关键。

假设原始 Base Weight：

\[
W
\]

加载成：

\[
W_q
\]

即 4-bit 量化存储。

Forward 不是简单：

\[
W_qx
\]

然后整个矩阵乘法都按普通整数 4-bit 思维理解。

概念上更接近：

```text
4-bit Quantized Weight
W_q
      ↓
Dequantization
反量化
      ↓
Compute Dtype
例如 BF16
      ↓
Matrix Multiply
      ↓
Base Output
      +
LoRA Output
```

公式上可以粗略写：

\[
y
=
Dequant(W_q)x
+
\frac{\alpha}{r}BAx
\]

其中：

\[
Dequant(W_q)
\approx
W
\]

这就是 QLoRA 最核心的一张公式。

---

# 七、为什么“反量化”以后还省显存？

你可能马上发现一个问题：

> 既然最后要恢复成 BF16，为什么不一开始直接保存 BF16？

关键在于：

> **不需要把整个 Base Model 永久以 BF16 完整副本驻留在显存中。**

权重主要保持：

```text
4-bit compressed storage
```

计算某一层时：

> 按实际 kernel / 实现需要，把相关量化权重转换到计算表示完成矩阵运算。

所以要区分：

```text
长期驻留的模型权重表示
```

和：

```text
计算瞬间使用的数值表示
```

这就是为什么：

> Storage Dtype 与 Compute Dtype 的区别如此重要。

---

# 八、LoRA Adapter 本身会不会也变成 4-bit？

第一版心智模型：

> **不要这样理解。**

QLoRA 中被低位宽量化的核心对象是：

# Frozen Base Model

而 LoRA：

\[
A,B
\]

是真正需要梯度更新的训练参数。

它们通常保持：

> 更适合训练的浮点精度。

例如常见会使用：

```text
BF16
FP16
或框架适合的训练dtype
```

所以：

```text
4-bit
=
Frozen Base Storage

BF16 / FP16 等
=
主要计算与可训练Adapter相关精度
```

这个边界一定要牢牢记住。

---

# 九、NF4 为什么不是普通 INT4？

这里不需要深入信息论，但必须建立准确直觉。

普通均匀 INT4 可以想象：

> 把一个数值区间相对均匀地划成有限档位。

NF4 的设计思想则更加针对：

> 神经网络权重的统计分布。

它试图让有限的 16 个编码：

> 更有效地覆盖常见权重值所在的区域。

因此在 QLoRA 语境里：

```text
4-bit
```

只说明：

> 位宽。

而：

```text
NF4
```

说明：

> **这 4 个 bit 怎样解释。**

所以：

\[
\boxed{
BitWidth
\neq
QuantizationFormat
}
\]

4-bit 可以有不同量化格式。

NF4 是其中一种。

---

# 十、什么是 Double Quantization？

这是 QLoRA 里另一个值得认识、但不用过度钻数学的技术。

第一次量化：

> 把 Base Weight 压成 4-bit。

但前面说过：

> 每个量化 Block 还需要 Scale 等量化常数。

这些常数本身：

> 也占空间。

于是 Double Quantization 的思路是：

> **连这些量化常数本身也再做进一步量化。**

流程：

```text
Base Weights
      ↓
第一次Quantization
      ↓
4-bit weight codes
+
quantization constants
      ↓
再压缩这些constants
      ↓
进一步节省显存
```

所以：

\[
\boxed{
DoubleQuantization
不是把权重“量化两遍”
}
\]

更准确地说：

> 第二层主要进一步压缩第一层量化产生的量化参数。

---

# 十一、把 LoRA、QLoRA、NF4 一次性放对位置

整个结构应该这样看：

```text
                Base Model Weight W
                         │
                         ▼
                 4-bit Quantization
                         │
                         ▼
                        NF4
              低位宽保存Frozen Base
                         │
                  Forward时按需
                   Dequantize
                         │
                         ▼
                      Base Path
                         │
                         ├──────────────┐
                         │              │
输入 x ─────────────────┤              ▼
                         │            相加
                         │              │
                         ▼              ▼
                    LoRA A → B       Output
                    Trainable
                         │
                         ▼
                       Loss
                         │
                         ▼
                     Backward
                         │
                         ▼
                    更新 LoRA
                    Base不更新
```

这就是 QLoRA。

不是：

> “把整个 LoRA 也压成 4-bit 然后训练。”

---

# 十二、政府采购项目为什么特别适合把 QLoRA 作为 Baseline 候选？

因为我们的第一版目标是：

```text
强 Base Model
+
高质量政府采购 SFT 数据
+
有限训练资源
+
频繁实验
+
多个 Adapter Version
```

我们真正想训练的：

> 是领域行为增量。

而不是：

> 整套 Base Model。

于是 QLoRA 可以让：

```text
大模型能力
```

与：

```text
较低训练显存门槛
```

同时存在。

但这里必须防止另一个极端：

> **QLoRA 不是因为省显存，所以永远应该优先于 LoRA。**

如果 GPU 足够，

普通 BF16 LoRA：

> 结构更简单。

有时调试也更直接。

所以最终比较仍然是：

```text
BF16 LoRA
vs
QLoRA
```

在相同 Dataset、Benchmark 和 Target Modules 下：

> 看显存、速度、稳定性和业务指标。

---

# 十三、QLoRA 最容易产生的 7 个错误理解

| 错误理解 | 正确理解 |
|---|---|
| “QLoRA 就是 4-bit LoRA” | 核心是 4-bit Frozen Base + Trainable LoRA |
| “所有训练计算都是 4-bit” | 4-bit 主要用于 Base Weight 存储，计算通常使用更高精度 |
| “NF4 是保留四位小数” | NF4 是 4-bit 量化编码格式 |
| “4-bit 没有误差” | 量化一定是近似表示 |
| “LoRA A/B 也必须是 4-bit” | 可训练 Adapter 通常保持适合训练的浮点精度 |
| “7B 4-bit 一定只占 3.5GB” | 3.5GB 只是裸权重理论值，实际还有元数据和运行开销 |
| “QLoRA 解决所有 OOM” | Activation、Sequence Length、Batch 等仍可能导致 OOM |

这张表建议真正记住。

---

# 十四、本阶段工程产物：`QLoRAMemoryModel_V0.1`

第一版配置记录不要只写：

```text
load_in_4bit = true
```

至少应该把这些信息放在一起：

```text
base_model_revision

quantization_enabled
=
true

base_weight_bit_width
=
4

quantization_format
=
NF4

double_quantization
=
enabled / disabled

compute_dtype
=
BF16 / FP16 / actual setting

base_weights
=
frozen

adapter_method
=
LoRA

adapter_train_dtype
=
actual framework setting

rank
alpha
dropout
target_modules

measured_peak_vram

benchmark_version
```

为什么最后两个特别重要？

因为理论上：

> “应该省很多显存。”

不等于：

> 你的真实训练配置真的省了多少。

最终必须测：

# Peak VRAM

同时测：

# Business Quality

---

# 十五、把本阶段压缩成最精准的 5 句话

如果一周以后只剩五句话，我希望是：

> **第一，QLoRA 不是把整个训练变成 4-bit，而是主要把冻结 Base Model 的权重低位宽保存，再继续训练 LoRA Adapter。**

> **第二，必须区分 Storage Dtype 与 Compute Dtype：权重可以 4-bit 存储，但矩阵计算通常会在 BF16、FP16 等更合适的计算精度下完成。**

> **第三，NF4 是针对神经网络权重设计的 4-bit 量化表示；4-bit 表示位宽，NF4 表示这些 4 个 bit 如何编码数值。**

> **第四，量化一定产生近似误差，QLoRA 的价值是用可接受的量化误差换取巨大的 Base Weight 显存节省，最终是否值得必须由 Benchmark 验证。**

> **第五，QLoRA 主要解决 Base Weight Memory，不会让 Activation、Context Length、Batch Size 和训练临时内存问题自动消失。**

这五句话真正掌握：

> QLoRA 就不会再变成“神秘省显存开关”。

---

# 本阶段最核心的一张图

```text
Original Base Model
BF16 / FP16 Weights
        │
        ▼
4-bit Quantization
        │
        ▼
NF4 Frozen Base
低显存驻留
        │
        │ Forward
        ▼
On-the-fly Dequantization
        │
        ▼
Compute Dtype
BF16 / FP16 等
        │
        ▼
       Wx
        │
        ├────────────────┐
        │                │
        │           LoRA Branch
        │             A → B
        │           Trainable
        │                │
        └───────┬────────┘
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
         LoRA A/B Updated
                │
         Quantized Base
             Frozen
```

脑中只记一句：

> **Base 低位宽存，计算高精度做，LoRA 正常训练。**

---

# 本阶段掌握测试

现在不回看正文，你应该能够自己解释：QLoRA 和普通 LoRA 的真正区别是什么；QLoRA 到底量化了谁；为什么 Frozen Base 仍然值得量化；为什么 4-bit 不意味着所有 Forward、Backward 都只有 4-bit；Storage Dtype 和 Compute Dtype 有什么区别；为什么 4-bit 理论上相对 BF16 能把裸权重存储缩到约四分之一；为什么实际显存不会严格等于理论值；什么是 Block-wise Quantization；NF4 的 4-bit 与“四位小数”为什么完全不是一回事；为什么 NF4 和 INT4 不是同一个概念；什么是 Quantization Error；为什么 `Dequant(W_q)` 只能近似原始 \(W\)；为什么 LoRA A/B 通常不跟着 Base 一起量化成训练用 4-bit；Double Quantization 进一步压缩的是什么；以及为什么 QLoRA 之后仍然可能因为长 Context、Activation 或 Batch Size 而 OOM。

如果这些能够完整讲出来：

\[
\boxed{
第五课第9阶段真正掌握
}
\]

---

# 本阶段最后只记一句话

> **QLoRA 的本质，是把“不需要更新但必须驻留”的巨大 Base Model 权重以 NF4 等 4-bit 形式压缩保存，在 Forward 时按需要恢复到合适的计算精度参与完整模型计算，同时保持 LoRA Adapter 为真正可训练参数；它省掉的是 Base Weight 的大头显存，而不是把整个训练系统魔法般变成 4-bit。**

---

# 下一阶段：第五课 · 第 10 阶段
# 训练显存到底花在哪里？
## 为什么明明 7B 4-bit Base Model 只有几 GB，训练时还是可能 OOM？

第 9 阶段解决了：

> **Base Weight 怎样从 BF16 的大体积压到 4-bit。**

第 10 阶段要正式把训练显存账本摊开：

```text
Model Weights
+
LoRA Parameters
+
Gradients
+
Optimizer States
+
Activations
+
Attention / Temporary Buffers
+
CUDA / Framework Overhead
```

然后真正回答：

> **哪个东西跟模型参数量走，哪个东西跟 Sequence Length 走，哪个东西跟 Batch Size 走，以及 OOM 时到底应该先改什么。**

---

<!-- LESSON 05 STAGE 09 END -->


<!-- LESSON 05 STAGE 10 START -->

# 第五课 · 第 10 阶段
# 训练显存到底花在哪里？
## 为什么 7B 模型已经 QLoRA 4-bit 了，训练时照样可能 OOM？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **能推理，不代表能训练。**
2. **Model Weights + KV Cache + Activations / Runtime Buffers**
3. **Model Weights + Forward中间结果 + Backward所需信息 + Gradients + Optimizer States**
4. **BF16 Base 约16-bit/parameter**
5. **NF4 Base 约4-bit/parameter + metadata**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `LoRA` | LoRA：冻结大部分基座参数，只训练低秩增量矩阵 |
| `QLoRA` | QLoRA：量化基座模型并训练 LoRA，以降低显存成本 |
| `Gradient` | 梯度：损失对参数变化方向和敏感度的局部信息 |
| `Batch` | 批次：一次参与计算的一组样本 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
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

第 9 阶段我们解决的是：

> **怎样把 Frozen Base Model 的权重显存压下来。**

现在必须解决一个非常现实的问题：

```text
7B Base
已经4-bit了

LoRA
也只有几千万参数

为什么24GB显卡
还是可能突然 OOM？
```

答案是：

> **训练显存从来不只有 Model Weights。**

真正的训练显存账本更接近：

\[
\boxed{
M_{peak}
\approx
M_{base}
+
M_{trainable}
+
M_{grad}
+
M_{optimizer}
+
M_{activation}
+
M_{temporary}
+
M_{runtime}
}
\]

本阶段最终形成：

# `TrainingMemoryBudget_V0.1`

---

# 一、本阶段只解决一个核心问题

你以后碰到：

```text
CUDA out of memory
```

第一反应不能再是：

> “模型太大。”

而应该问：

> **到底是哪一类显存在涨？它主要跟 Parameter Count、Trainable Parameters、Sequence Length，还是 Micro Batch Size 有关？**

先把总图锁死：

```text
                         GPU VRAM
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
    Model Side          Training Side       Runtime Side
        │                   │                   │
 Base Weights           Gradients          Temp Buffers
 LoRA Weights           Optimizer          CUDA Context
                        Activations        Allocator
                                           Framework
```

一句话：

> **模型有多大，只解释了显存账本的一部分。**

---

# 二、今天只锁死 5 个核心心智模型

## 心智模型 1：Inference Memory ≠ Training Memory

推理时主要关心：

```text
Model Weights
+
KV Cache
+
Activations / Runtime Buffers
```

训练时则需要：

```text
Model Weights
+
Forward中间结果
+
Backward所需信息
+
Gradients
+
Optimizer States
```

所以同一个模型：

> 能推理，不代表能训练。

\[
\boxed{
CanLoadForInference
\neq
CanTrain
}
\]

---

## 心智模型 2：QLoRA 主要砍掉 Base Weight Memory，不会自动砍掉 Activation

第 9 阶段：

```text
BF16 Base
约16-bit/parameter
```

变成：

```text
NF4 Base
约4-bit/parameter + metadata
```

这对：

# Base Weights

非常有效。

但 Forward 过程中每一层产生的：

```text
Hidden States
Attention中间量
MLP中间量
```

并不会因为 Base Weight 是 4-bit：

> 全部自动缩成四分之一。

所以：

\[
\boxed{
4bitWeights
\neq
4bitActivations
}
\]

---

## 心智模型 3：LoRA 让 Gradient / Optimizer 很小，但 Activation 仍经过完整 Base Model

QLoRA 中真正 Trainable 的：

```text
LoRA A/B
```

很少。

因此：

```text
Gradient Memory
Optimizer State Memory
```

相对 Full Fine-Tuning 可以小很多。

但一条 Token 仍然要跑过：

> 整个 Transformer。

所以：

```text
7B Base
虽然Frozen
```

不等于：

```text
Forward只算1%的模型
```

整个模型仍参与计算。

---

## 心智模型 4：Sequence Length 和 Micro Batch Size 是 Activation Memory 的两大旋钮

非常粗略地说：

\[
M_{\text{activation}}
\propto
B_{\text{micro}}
\times
S
\times
L
\times
H
\]

其中：

- \(B_{\text{micro}}\)：单次真正送进 GPU 的样本数；
- \(S\)：Sequence Length；
- \(L\)：Transformer 层数；
- \(H\)：Hidden Size。

真实公式会复杂得多，但这个心智模型非常有用。

也就是说：

> **参数没变，只把 2048 Token 改成 8192 Token，训练显存也可能完全变成另一回事。**

---

## 心智模型 5：OOM 要按“显存来源”诊断，不能随机调参

最差的调试方式：

```text
OOM
↓
rank乱改
↓
batch乱改
↓
alpha乱改
↓
再装几个包
```

正确思路：

```text
OOM
 ↓
是哪类Memory？
 ↓
对应哪个Scaling变量？
 ↓
只改最相关的旋钮
 ↓
重新测Peak VRAM
```

这叫：

# Memory Attribution
## 显存归因

---

# 三、训练显存正式拆成 7 个账户

| 显存账户 | 主要由什么决定 | QLoRA 是否明显降低 |
|---|---|---|
| **Base Weights** | Base 参数量、量化位宽 | **是，核心收益** |
| **LoRA / Trainable Weights** | Rank、Target Modules | 数量本来就小 |
| **Gradients** | Trainable 参数量 | **LoRA 大幅降低** |
| **Optimizer States** | Trainable 参数量、优化器 | **LoRA 大幅降低** |
| **Activations** | Batch、Sequence、模型结构 | **不会自动消失** |
| **Temporary Buffers** | Attention/kernel/算子 | 部分受实现影响 |
| **Runtime Overhead** | CUDA、allocator、框架等 | 与4-bit不是一回事 |

以后看到显存：

> 就用这 7 个账户查账。

---

# 四、账户 1：Base Model Weights

这是最好理解的一块。

如果模型有：

\[
N
\]

个参数。

BF16 理论裸权重：

\[
M_{\text{base}}
\approx
2N \text{ bytes}
\]

7B：

\[
7\times10^9\times2
\approx14GB
\]

QLoRA 4-bit 裸编码理论上：

\[
7\times10^9\times0.5
\approx3.5GB
\]

但上一阶段已经强调：

> 实际驻留显存还要加量化 Scale、Metadata、非量化参数、临时工作区等。

因此这里最重要的不是死记：

```text
7B = X GB
```

而是：

\[
\boxed{
BaseWeightMemory
\propto
ParameterCount
\times
StorageBits
}
\]

这块就是 QLoRA 最擅长压缩的地方。

---

# 五、账户 2～4：LoRA Weight、Gradient、Optimizer State

假设 LoRA 真正可训练参数只有：

```text
20M Parameters
```

那么需要 Gradient 的：

> 主要也是这 20M。

Optimizer 需要保存状态的：

> 主要也是这些 Trainable Parameters。

这和 Full Fine-Tuning 完全不同。

Full FT：

```text
7B参数
都可能需要Gradient和Optimizer State
```

LoRA：

```text
7B Base
Frozen

20M LoRA
Trainable
```

所以：

\[
\boxed{
OptimizerMemory
主要跟
TrainableParameterCount
走
}
\]

而不是简单跟：

> Base Model 总参数量走。

---

# 六、为什么 Optimizer State 有时比你想象得更贵？

例如常见 AdamW 会为可训练参数维护：

```text
First Moment
m

Second Moment
v
```

这些状态可能使用 FP32 等精度。

某些训练方案还可能存在：

```text
Master Weights
```

等额外副本。

因此不能机械记：

> “一个参数训练永远固定 X bytes。”

因为这取决于：

```text
Optimizer
Parameter Dtype
Gradient Dtype
Mixed Precision实现
8-bit Optimizer与否
Framework
```

长期正确心智模型：

\[
\boxed{
OptimizerState
跟 Trainable Parameters 强相关
}
\]

这正是 LoRA 为什么能省大量训练显存。

---

# 七、真正的大户：Activations

这里就是很多人第一次 QLoRA OOM 的原因。

假设输入经过第 1 层 Transformer：

```text
Hidden State
↓
Attention
↓
MLP
↓
Layer Output
```

然后还有：

```text
第2层
第3层
...
第32层
```

Backward 要计算：

> 每一步参数变化对最终 Loss 的影响。

因此训练期间需要保存或能够重新得到大量中间信息。

这些中间结果统称：

# Activations
## 激活值 / 中间激活

可以把它理解成：

> **Forward 为了让 Backward 以后能够追责，留下的计算现场。**

---

# 八、为什么 Batch Size 会直接推高 Activation？

假设：

```text
micro_batch_size = 1
```

GPU 同时保存：

> 一条 Sequence 的大量中间结果。

改成：

```text
micro_batch_size = 4
```

现在同一时刻要处理：

> 4 条。

因此很多 Activation Memory 会近似跟：

\[
B_{\text{micro}}
\]

一起增加。

注意我这里特意写：

# Micro Batch Size

而不是：

# Effective Batch Size

这两个后面必须分开。

---

# 九、为什么 Sequence Length 更危险？

假设：

```text
Batch = 1
```

但长度：

```text
2048
→
4096
→
8192
```

每层都要处理更多 Token。

大量 Hidden State 相关存储大致会随：

\[
S
\]

增长。

Attention 又更特殊。

经典 Attention 计算里：

\[
QK^T
\]

会形成与：

\[
S\times S
\]

相关的结构。

因此传统实现的某些 Attention 中间内存：

\[
O(S^2)
\]

增长非常快。

这就是为什么：

> 长上下文训练特别容易吃显存。

---

# 十、但这里必须做一个现代实现修正：FlashAttention 会改变“显存复杂度”，不会改变所有计算规律

如果使用传统 Attention，并显式保存完整 Attention Matrix：

> \(S^2\) 中间结果会非常昂贵。

FlashAttention / 高效 SDPA 等实现：

> 不需要把完整 Attention Matrix 长时间写回显存。

因此能显著降低 Attention 的峰值显存。

所以不能简单说：

> “序列长度翻倍，所有训练显存一定四倍。”

这是不精确的。

更准确：

> **Attention 的理论计算量依然随序列长度呈近似二次增长，而高效 Attention Kernel 可以避免完整 \(S^2\) Attention Matrix 的显存驻留，使实际峰值显存增长比朴素实现健康很多。**

这条区别很重要：

\[
\boxed{
ComputeComplexity
\neq
StoredActivationMemory
}
\]

---

# 十一、Gradient Checkpointing 为什么能省显存？

正常做法：

```text
Forward
↓
保存大量Activation
↓
Backward直接使用
```

Gradient Checkpointing：

# 梯度检查点

采用：

```text
Forward
↓
只保留部分Checkpoint
↓
其他Activation不长期保存
↓
Backward需要时
重新Forward计算
```

也就是：

\[
\boxed{
Memory
\downarrow
\quad
\text{换取}
\quad
Compute
\uparrow
}
\]

中文：

> **不存那么多计算现场，等需要的时候再重算。**

---

# 十二、Gradient Checkpointing 省的不是 Model Weight

这一点很容易搞混。

QLoRA：

> 主要压 Base Weight。

Gradient Checkpointing：

> 主要压 Activation。

所以二者非常互补：

```text
QLoRA
        ↓
Base Weight Memory ↓

Gradient Checkpointing
        ↓
Activation Memory ↓
```

这也是为什么这两个技术经常一起出现。

---

# 十三、Gradient Accumulation 又是在解决什么？

假设你希望：

```text
Effective Batch Size = 16
```

但 GPU 一次只能放：

```text
Micro Batch Size = 2
```

可以让 8 个 Micro-batch：

```text
forward
backward

forward
backward

...

累计8次Gradient
```

然后：

```text
optimizer.step()
```

于是：

\[
B_{\text{effective}}
=
B_{\text{micro}}
\times
GradientAccumulationSteps
\]

单卡、单进程的简化情况例如：

\[
2\times8=16
\]

这叫：

# Gradient Accumulation
## 梯度累积

---

# 十四、Gradient Accumulation 最容易被误解的一点

它可以让：

> **有效 Batch 变大，而不要求一次把整个 Batch 放进 GPU。**

但是：

\[
\boxed{
GradientAccumulation
不会让单个MicroBatch本身变小
}
\]

所以如果：

```text
micro_batch = 1
sequence_length = 32K
```

这一条本身已经 OOM，

再把：

```text
gradient_accumulation_steps
```

从 4 调到 32：

> 没用。

因为连第一条 Forward 都进不去。

---

# 十五、Packing 对显存又是什么关系？

第 4 阶段学了 Packing。

Packing 的主要目标是：

# Token Utilization

减少 Padding Waste。

但一定不要误解成：

> `packing=True` 必然降低 Peak VRAM。

如果 Packed Sequence 最终仍是：

```text
4096 Tokens
```

GPU 依然需要处理：

> 一条 4096 长度 Sequence。

Packing 的主要收益更接近：

> **同样的计算长度中，装更多真实训练 Token。**

它是：

# Efficiency Optimization

而不一定是：

# Peak Memory Reduction

这一点很关键。

---

# 十六、为什么 Rank 通常不是 QLoRA OOM 的第一嫌疑人？

假设：

```text
r = 16
```

改成：

```text
r = 8
```

LoRA Trainable Parameters 的确减少。

Gradient 和 Optimizer State：

> 也会减少。

但如果真正显存大头已经变成：

# Activations

那么这个变化：

> 可能救不了多少显存。

所以出现 OOM 时，不要机械：

```text
先砍Rank
```

要看账本。

对于 QLoRA，一个很常见的优先诊断方向反而是：

```text
Micro Batch Size

Sequence Length

Gradient Checkpointing

Attention Implementation
```

---

# 十七、7B QLoRA 为什么“模型才几 GB”仍然会 OOM？

现在可以精准回答了。

假设只是概念例子：

```text
4-bit Base
≈ 几GB级

LoRA
≈ 相对较小
```

但你又设置：

```text
Sequence Length = 8192

Micro Batch = 4

Gradient Checkpointing = OFF

Attention implementation
不够省显存
```

那么：

```text
Base Weight
并不是主犯

Activation
+
Attention Temp
+
Runtime Buffer
```

完全可能把剩余显存吃光。

所以：

\[
\boxed{
SmallWeightFootprint
\neq
SmallTrainingFootprint
}
\]

这是今天最重要的一句话之一。

---

# 十八、还有一个经常混进来的东西：KV Cache

推理阶段我们经常讨论：

# KV Cache

它会随着生成长度和 Batch 增长。

但普通 Causal LM 训练时：

> 通常并不需要像自回归推理那样保留跨生成步骤的 KV Cache。

训练配置里一般会：

```text
use_cache = False
```

尤其和 Gradient Checkpointing 一起时。

所以看到训练 OOM：

> 不要第一时间把所有显存都归因到推理阶段熟悉的 KV Cache。

训练真正的大头通常另有其人。

---

# 十九、OOM 时建立一个精准的处理顺序

对于我们的 `ProcurementLM_V0.1` QLoRA Baseline，可以采用：

```text
OOM
 │
 ▼
1. 先确认有没有错误配置
   ├─ 是否意外加载BF16完整Base副本？
   ├─ 是否use_cache不合理开启？
   └─ 实际dtype是否符合预期？
 │
 ▼
2. 降低 Micro Batch Size
 │
 ▼
3. 检查 / 降低 Sequence Length
   并优化Context Selection
 │
 ▼
4. 开启 Gradient Checkpointing
 │
 ▼
5. 使用合适的高效Attention实现
 │
 ▼
6. 再检查 Packing / Length Bucketing 等吞吐效率
 │
 ▼
7. 如果仍不足
   再考虑Rank / Target Modules等Trainable Scope
 │
 ▼
8. 更进一步
   Offload / Distributed / 更大显存GPU
```

这里有一个原则：

> **先砍无效显存，再砍业务信息。**

例如不要为了 OOM：

> 第一刀直接把关键上下文从 4096 暴力砍到 512。

先确认有没有其他浪费。

---

# 二十、真正应该监控的是 Peak VRAM，而不是“理论估计”

理论公式可以帮助定位方向。

但真实训练最终要记录：

```text
Peak Allocated VRAM

Peak Reserved VRAM

Sequence Length

Micro Batch Size

Gradient Accumulation

Gradient Checkpointing

Attention Backend

Quantization Config

Trainable Parameters
```

因为 CUDA Allocator 还会涉及：

# Reserved Memory

以及：

# Fragmentation
## 显存碎片

所以有时：

```text
实际Tensor总量
```

没有完全占满显卡，

仍可能因为：

> 当前找不到足够大的连续可用块

而 OOM。

因此：

\[
\boxed{
TheoreticalMemory
\neq
ObservedPeakVRAM
}
\]

---

# 二十一、本阶段工程产物：`TrainingMemoryBudget_V0.1`

第一版至少记录这些字段：

```text
base_model
base_model_revision

quantization
compute_dtype

parameter_count
trainable_parameter_count

max_sequence_length
micro_batch_size
gradient_accumulation_steps

gradient_checkpointing

attention_backend

packing_enabled

optimizer
optimizer_precision

peak_allocated_vram
peak_reserved_vram

tokens_per_step
supervised_tokens_per_step

oom_status
```

同时建立显存归因：

```text
Base Weight
Trainable Weight
Gradient
Optimizer
Activation
Temporary / Attention
Runtime Overhead
```

不是要求你精确算到：

> 每个字节。

而是要求：

> **知道哪一个旋钮主要影响哪一块。**

---

# 二十二、这一阶段最值得保留的一张“变量地图”

| 你修改的变量 | 最直接影响的显存 |
|---|---|
| Base Model 参数量 | Base Weight |
| 4-bit / BF16 | Base Weight |
| Rank | LoRA Weight、Grad、Optimizer |
| Target Modules | LoRA Weight、Grad、Optimizer |
| Micro Batch Size | **Activation** |
| Sequence Length | **Activation + Attention + Compute** |
| Gradient Accumulation | 有效 Batch；对单 Micro-batch Peak VRAM影响较小 |
| Gradient Checkpointing | **Activation ↓，Compute ↑** |
| FlashAttention / 高效 Attention | Attention 中间内存、吞吐 |
| Packing | Token 利用率，未必直接降低 Peak VRAM |

这张表比背 CUDA 参数值重要得多。

---

# 二十三、把本阶段压成最精准的 5 句话

> **第一，训练显存不只是模型权重，而是 Base Weight、Trainable Weight、Gradient、Optimizer State、Activation、Temporary Buffer 和 Runtime Overhead 的总和。**

> **第二，QLoRA 主要降低冻结 Base Model 的 Weight Memory，LoRA 主要降低 Gradient 和 Optimizer 对应的 Trainable Parameter Memory，但完整 Transformer 的 Activation 仍然存在。**

> **第三，Micro Batch Size 和 Sequence Length 是 Activation 显存的核心变量；长上下文尤其昂贵，高效 Attention 可以降低中间显存，但不会让长序列计算免费。**

> **第四，Gradient Checkpointing 用额外计算换 Activation 显存；Gradient Accumulation 用多个小 Micro-batch 组成较大的 Effective Batch，两者解决的是完全不同的问题。**

> **第五，OOM 不是“模型太大”四个字能解释的；必须先定位显存账户，再调对应变量，并用真实 Peak VRAM 验证。**

---

# 二十四、本阶段最核心的一张图

```text
                    Training Peak VRAM
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
     Weights             Training           Runtime
       │                   │                   │
 Quantized Base        Activations         Buffers
 LoRA Params           Gradients           CUDA
                      Optimizer            Allocator
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
        Sequence       Micro Batch     Checkpointing
         Length           Size              │
             │             │                ▼
             └──────┬──────┘           Memory ↓
                    │                  Compute ↑
                    ▼
             Activation Peak
                    │
                    ▼
              OOM or Stable
```

脑子里只留一句：

> **QLoRA 省权重，Checkpointing 省激活，Accumulation 省一次性 Batch；三件事别混。**

---

# 二十五、本阶段掌握测试

不回看正文，你现在应该能够解释：为什么同一个 7B 模型能够推理却未必能够训练；训练显存有哪些主要组成；QLoRA 主要压缩哪一部分；为什么 LoRA 能显著减少 Gradient 和 Optimizer State；为什么 Base Model Frozen 后 Activation 仍然存在；为什么 Micro Batch Size 和 Effective Batch Size 不是一回事；Gradient Accumulation 为什么不能解决“单条 32K Sequence 已经 OOM”；Gradient Checkpointing 为什么能省显存以及它付出的代价是什么；为什么 Sequence Length 会强烈影响 Activation 和 Attention；FlashAttention 为什么能省显存但不会消除 Attention 的计算成本；为什么 Packing 主要提升 Token Utilization 而不保证降低 Peak VRAM；为什么 QLoRA OOM 时 Rank 往往不是第一刀；为什么训练阶段不应该把所有显存问题都归因于 KV Cache；以及为什么最终必须记录真实的 Peak Allocated / Reserved VRAM，而不能只看理论权重大小。

如果这些能完整讲出来：

\[
\boxed{
第五课第10阶段真正掌握
}
\]

---

# 本阶段最后只记一句话

> **训练显存是一张完整账本：QLoRA 把冻结 Base Weight 压下来，LoRA 把需要 Gradient 和 Optimizer 的参数规模压下来，但真正训练时仍然要为完整 Transformer 的 Activation、Attention 中间量和运行时缓冲付费；所以 OOM 的正确解决方式不是盲目缩模型，而是先判断显存到底花在哪，再针对 Sequence Length、Micro Batch、Checkpointing、Attention 实现和 Trainable Scope 精准下刀。**

---

# 下一阶段：第五课 · 第 11 阶段
# 真正跑一次 SFT 训练
## 前面 10 个阶段，终于要第一次全部接成可执行训练流程

下一阶段不再新增一堆理论概念，而是把目前所有组件真正组装起来：

```text
ProcurementDataset_V0.1
        ↓
Chat Template
        ↓
Assistant-only Loss
        ↓
Length Policy
        ↓
Packing
        ↓
4-bit NF4 Base
        ↓
LoRA Config
        ↓
Target Modules
        ↓
Training Arguments
        ↓
Trainer / Training Loop
        ↓
Forward
        ↓
Loss
        ↓
Backward
        ↓
Optimizer Step
        ↓
ProcurementLM_V0.1 Adapter
```

下一阶段我们会第一次真正回答：

> **从 `from_pretrained()` 到训练启动，一个完整可运行的 ProcurementLM QLoRA SFT 脚本到底由哪些部分组成，每一行为什么存在，以及开跑前必须检查哪几项才不会“代码能跑、训练却是错的”。**

---

<!-- LESSON 05 STAGE 10 END -->


<!-- LESSON 05 STAGE 11 START -->

# 第五课 · 第 11 阶段
# 真正跑一次 SFT 训练
## 从 `ProcurementDataset_V0.1` 到第一个真正会更新参数的 `ProcurementLM_V0.1`

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：MEDIUM。** 审计原因：核心心智模型出现偏后，阅读前段缺少认知锚点；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，真正的 SFT 不是 trainer.train()，而是一份由 Dataset、Template、Mask、Length、Model、LoRA、Optimizer 和 Evaluation 共同构成的训练协议。**
2. **第二，在正式花 GPU 时间以前，必须人工 Decode Chat Template、检查 Assistant Loss Mask、检查长度和 Trainable Parameters，并先跑 5～20 Step Smoke Test。**
3. **第三，loss.backward() 只是计算和累积 Gradient，真正改变 LoRA A/B 的时刻是 optimizer.step()；Gradient Accumulation 决定多少个 Micro-batch 合成一次参数更新。**
4. **第四，Learning Rate、Warmup、Epoch、Batch、Gradient Clipping 各自解决不同问题，不能把一个异常全部归因于“LoRA 参数不够”。**
5. **第五，Training Loss 下降只说明训练目标的 Token 概率在改善；是否真的成为更好的政府采购模型，必须交给独立 Validation、Hard Case 和最终 Benchmark。**
6. **真正可靠的 SFT 训练，不是“代码终于跑起来了”，而是我们能够证明：模型看到了正确的 Prompt，只有正确的 Response Token 在产生 Loss，正确的 LoRA 参数在获得 Gradient，每次 Optimizer Step 都在按可复现配置更新它们，而且整个过程能被 Validation 和 Benchmark 独立检验。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Dataset` | 数据集：按统一 Schema、版本和质量标准组织的样本集合 |
| `SFT` | 监督微调：用监督样本继续更新模型参数 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Loss` | 损失函数：把预测错误压缩成可优化的数值信号 |
| `Step` | 训练步：通常指一次优化器更新 |
| `LoRA` | LoRA：冻结大部分基座参数，只训练低秩增量矩阵 |
| `Gradient` | 梯度：损失对参数变化方向和敏感度的局部信息 |
| `Batch` | 批次：一次参与计算的一组样本 |

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

前 10 个阶段，我们一直在制造零件。

现在终于装机器。

到目前为止，我们已经有：

```text
训练数据
    ↓
Chat Template
    ↓
Assistant-only Loss
    ↓
Length Policy
    ↓
Packing Policy
    ↓
QLoRA 4-bit Base
    ↓
LoRA Rank / Alpha / Dropout
    ↓
Target Modules
    ↓
Training Memory Budget
```

今天只做一件事：

> **把这些东西接成一条真正能够执行的训练流水线，并知道 `trainer.train()` 背后每一步究竟发生了什么。**

本阶段最终形成：

# `ProcurementSFTTrainingRun_V0.1`

---

## 一、先锁死这一阶段最重要的心智模型

真正的 SFT 训练不是：

```python
trainer.train()
```

这一行代码。

它其实代表整条链：

```text
Dataset
   ↓
Semantic Validation
   ↓
Chat Template
   ↓
Tokenization
   ↓
Loss Mask
   ↓
Length / Packing
   ↓
Batch
   ↓
Forward
   ↓
Logits
   ↓
Causal LM Loss
   ↓
Backward
   ↓
Gradients on LoRA A/B
   ↓
Gradient Accumulation
   ↓
Optimizer Step
   ↓
Learning-rate Scheduler
   ↓
下一 Batch
```

所以今天最重要的一句话是：

> **Trainer 只是替我们执行训练协议，它不能替我们保证协议本身是正确的。**

代码能够跑通：

\[
\neq
\]

训练正确。

---

# 二、正式训练前，先建立一个“不可越过的闸门”

第一版训练不要直接上：

```text
全量数据
+
3 epochs
+
packing
+
几个小时训练
```

我们分成两次。

### 第一次：Smoke Test

只跑：

```text
少量样本
5～20 Steps
Packing = OFF
```

目标不是效果。

而是确认：

```text
Template 对
Loss Mask 对
Trainable Parameters 对
显存正常
Loss 有限
Gradient 正常
Checkpoint 能保存
```

然后才进入：

### 第二次：Formal Run

```text
完整训练集
Packing = ON（通过审计后）
正式 Epoch
Validation
Checkpoint
```

这是很重要的工程原则：

> **先证明训练系统是对的，再花 GPU 钱。**

---

# 三、我们最终需要的项目目录

第一版可以非常简单：

```text
ProcurementLM/
│
├── data/
│   ├── train.jsonl
│   └── validation.jsonl
│
├── train_sft.py
│
├── outputs/
│
└── configs/
    └── run_v0.1.json
```

数据继续保留第 4 课确定的语义结构，而不是预先拼成一大坨文本：

```json
{
  "messages": [
    {
      "role": "system",
      "content": "你是政府采购文件审查助手。"
    },
    {
      "role": "user",
      "content": "审查以下条款：投标人须在投标截止日前在本市设立固定办公场所。"
    },
    {
      "role": "assistant",
      "content": "存在潜在风险。该要求将投标前已具备本地固定场所作为参与条件，可能形成地域性准入限制。"
    }
  ]
}
```

当前 TRL 的 `SFTTrainer` 可以直接处理这种 conversational `messages` 数据，也支持预先准备好的 `input_ids / labels`；如果已经提供 `labels`，其中 `-100` 的位置会被排除在 Loss 之外。([huggingface.co](https://huggingface.co/docs/trl/sft_trainer))

这正好把第 1 阶段和今天接起来：

> **`messages` 是语义源，`input_ids / labels` 是训练表示。**

---

# 四、先把完整训练脚本的大骨架摆出来

下面这份不是“背代码”。

你只需要先看结构：

```python
import torch

from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)

from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
)

from trl import SFTConfig, SFTTrainer


# 1. 实验身份
BASE_MODEL_ID = "你的-base-model-id"
OUTPUT_DIR = "./outputs/procurement_sft_v0.1"

# 来自第 3 阶段的 Sequence Policy
MAX_LENGTH = 2048

# 来自第 8 阶段的 Target Module Policy
TARGET_MODULES = [
    "q_proj",
    "v_proj",
]


# 2. 加载 Dataset
dataset = load_dataset(
    "json",
    data_files={
        "train": "./data/train.jsonl",
        "validation": "./data/validation.jsonl",
    },
)

train_dataset = dataset["train"]
eval_dataset = dataset["validation"]


# 3. Tokenizer
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


# 4. QLoRA 量化配置
use_bf16 = torch.cuda.is_bf16_supported()
compute_dtype = torch.bfloat16 if use_bf16 else torch.float16

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=compute_dtype,
)


# 5. 加载 Frozen Base Model
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_ID,
    quantization_config=quant_config,
    dtype="auto",
)

model.config.use_cache = False


# 6. 为 k-bit 训练准备模型
model = prepare_model_for_kbit_training(
    model,
    use_gradient_checkpointing=True,
)


# 7. LoRA
lora_config = LoraConfig(
    task_type="CAUSAL_LM",
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=TARGET_MODULES,
    bias="none",
)

model = get_peft_model(model, lora_config)

model.print_trainable_parameters()


# 8. Training Config
training_args = SFTConfig(
    output_dir=OUTPUT_DIR,

    max_length=MAX_LENGTH,

    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=8,

    learning_rate=1e-4,
    num_train_epochs=2,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",

    gradient_checkpointing=True,
    max_grad_norm=1.0,

    bf16=use_bf16,
    fp16=not use_bf16,

    assistant_only_loss=True,

    packing=False,          # Smoke Test 先关闭
    eval_packing=False,

    logging_steps=10,

    eval_strategy="steps",
    eval_steps=100,

    save_strategy="steps",
    save_steps=100,
    save_total_limit=2,

    report_to="none",

    seed=42,
    data_seed=42,

    use_cache=False,
)


# 9. Trainer
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    processing_class=tokenizer,
)


# 10. 真正开始训练
trainer.train()


# 11. 保存 LoRA Adapter + Tokenizer
FINAL_ADAPTER_DIR = f"{OUTPUT_DIR}/final_adapter"

trainer.model.save_pretrained(FINAL_ADAPTER_DIR)
tokenizer.save_pretrained(FINAL_ADAPTER_DIR)
```

这一套技术组合与当前 Hugging Face 官方接口是一致的：`BitsAndBytesConfig` 支持 4-bit、NF4、BF16 compute dtype；PEFT 提供 `prepare_model_for_kbit_training()`、`LoraConfig` 和 `get_peft_model()`；TRL 的 `SFTTrainer` 原生支持 PEFT/LoRA 训练。([huggingface.co](https://huggingface.co/docs/transformers/main/quantization/bitsandbytes?utm_source=chatgpt.com))

不过这份代码里：

```text
BASE_MODEL_ID
MAX_LENGTH
TARGET_MODULES
r / alpha / dropout
Epoch
Learning Rate
```

都不是“宇宙最优参数”。

它们必须回到我们前面定义的各个 Policy 和 Benchmark。

---

# 五、现在从上往下拆：第一个关键点不是 Model，而是 Dataset

训练第一步：

```python
dataset = load_dataset(...)
```

看起来平平无奇。

但真正应该先检查的是：

```text
Train / Validation
是否已经隔离？

有没有 near duplicate？

有没有未来信息泄漏？

messages role 顺序是否正常？

assistant 是否为空？

审计字段有没有误塞进 Prompt？
```

训练前最少应该做：

```python
sample = train_dataset[0]

print(sample["messages"])
```

然后确认角色：

```text
system
↓
user
↓
assistant
```

如果这一关错了：

> 后面所有 GPU 计算都是在把错误变得更牢固。

---

# 六、第二个关键闸门：训练前必须把 Chat Template 真正打印出来

不要只看：

```python
sample["messages"]
```

还必须看模型实际吃到的东西：

```python
rendered = tokenizer.apply_chat_template(
    sample["messages"],
    tokenize=False,
    add_generation_prompt=False,
)

print(rendered)
```

你要亲眼检查：

```text
System 在哪里？

User 边界在哪里？

Assistant 边界在哪里？

EOS / end-of-turn 在哪里？

有没有重复 BOS / EOS？

有没有把 answer 截掉？
```

训练数据中已经包含 Assistant Gold Answer，因此训练格式通常使用 `add_generation_prompt=False`；推理时才通常给未完成的对话增加 assistant generation prompt。Chat Template 本质上负责把结构化角色消息编译成模型真正看到的 Token 协议。([huggingface.co](https://huggingface.co/docs/transformers/v5.9.0/en/chat_templating?utm_source=chatgpt.com))

---

# 七、第三个闸门：Assistant-only Loss 必须真的验证，而不是相信配置名

我们现在写了：

```python
assistant_only_loss=True
```

但这背后有一个非常重要的前提：

> **Chat Template 必须能够标出哪些 Token 属于 Assistant。**

当前 TRL 的 `assistant_only_loss=True` 依赖模板支持 assistant token mask；模板通常需要用 `{% generation %}...{% endgeneration %}` 标记生成区域，TRL 对若干已知模型家族会提供相应支持。([huggingface.co](https://huggingface.co/docs/trl/sft_trainer))

训练之前直接做审计：

```python
audit = tokenizer.apply_chat_template(
    sample["messages"],
    tokenize=True,
    add_generation_prompt=False,
    return_dict=True,
    return_assistant_tokens_mask=True,
)

input_ids = audit["input_ids"]
assistant_mask = audit["assistant_masks"]

assert len(input_ids) == len(assistant_mask)
assert sum(assistant_mask) > 0

assistant_ids = [
    token_id
    for token_id, is_assistant
    in zip(input_ids, assistant_mask)
    if is_assistant
]

print("监督 Token 数:", sum(assistant_mask))
print(
    "监督区域:",
    tokenizer.decode(assistant_ids)
)
```

`return_assistant_tokens_mask=True` 的当前 tokenizer 接口就是用于返回 Assistant Token Mask；它只有在模板支持 generation 区域标记时才可用。([huggingface.co](https://huggingface.co/docs/transformers/main_classes/tokenizer?utm_source=chatgpt.com))

### 这里有一个非常重要的工程分叉

如果这一步不能可靠返回 Assistant Mask：

> **不要硬跑。**

有两条路：

```text
路线 A
修正 / 使用支持 assistant mask 的 Chat Template
```

或者：

```text
路线 B
按照第1阶段的 Formatting Contract
自己构造 input_ids + labels

Prompt位置:
labels = -100

Assistant位置:
labels = token_id
```

而当前 `SFTTrainer` 对已经 pre tokenized 且包含 `labels` 的 Dataset 会直接使用这些 labels。([huggingface.co](https://huggingface.co/docs/trl/sft_trainer))

所以我们第 1 阶段学的 Loss Mask：

> 到今天不是理论知识，而是训练前的生死检查。

---

# 八、第四个闸门：长度检查必须发生在 `trainer.train()` 之前

假设：

```python
MAX_LENGTH = 2048
```

不能直接相信所有数据都合规。

可以先检查：

```python
def count_tokens(example):
    ids = tokenizer.apply_chat_template(
        example["messages"],
        tokenize=True,
        add_generation_prompt=False,
    )
    return len(ids)


lengths = [
    count_tokens(train_dataset[i])
    for i in range(len(train_dataset))
]

print("max =", max(lengths))
print("avg =", sum(lengths) / len(lengths))
```

如果出现：

```text
MAX_LENGTH = 2048

某条样本 = 4267
```

此时不要期待：

> Trainer 替我们聪明地决定业务上该删哪一段。

应该回到：

# `SFTSequencePolicy_V0.1`

决定：

```text
Reject
Context Selection
Structured Truncation
Long-sample Route
```

而不是静默：

> 把 Gold Answer 截掉。

---

# 九、第五步：QLoRA Base 和 LoRA Adapter 真正组起来

这一部分就是前 5～10 阶段第一次全部落地。

首先：

```python
quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=compute_dtype,
)
```

对应第 9 阶段：

```text
Frozen Base
↓
NF4 4-bit Storage
↓
更高精度 Compute
```

然后：

```python
model = prepare_model_for_kbit_training(model)
```

再给指定模块注入：

```python
LoraConfig(...)
```

和：

```python
get_peft_model(...)
```

当前 PEFT 官方流程就是先建立 LoRA 配置、将其应用到 Base Model，并可以通过 `print_trainable_parameters()` 检查真正训练了多少参数。([huggingface.co](https://huggingface.co/docs/peft/main/package_reference/lora?utm_source=chatgpt.com))

因此：

```python
model.print_trainable_parameters()
```

不是装饰。

它是：

# Adapter Injection Audit

如果你期望：

```text
0.3%
```

结果打印：

```text
100%
```

不要开始训练。

如果你期望：

```text
20M trainable
```

结果只有：

```text
100K
```

也不要开始训练。

---

# 十、Training Arguments 到底在控制什么？

这几个参数必须从“配置项”变成因果关系。

```python
per_device_train_batch_size=1
gradient_accumulation_steps=8
```

在单卡简化情况下：

\[
B_{\text{effective}}
=
1\times8
=
8
\]

多卡则更完整地是：

\[
B_{\text{effective}}
=
B_{\text{micro}}
\times
Accumulation
\times
WorldSize
\]

但如果使用 Packing：

> “原始 Sample 数 / Step”就不再是很干净的规模指标，最好同时记录 `Tokens per Step` 与 `Supervised Tokens per Step`。

---

`learning_rate=1e-4`：

> 控制 Optimizer 每次更新 LoRA 参数的步长尺度。

当前 TRL 文档也指出，训练 Adapter 时通常会采用比 Full Fine-Tuning 更高的学习率，并以大约 `1e-4` 作为常见量级示例。([huggingface.co](https://huggingface.co/docs/trl/sft_trainer))

但：

\[
10^{-4}
\]

只是 Baseline，

不是政府采购模型的“正确答案”。

---

`warmup_ratio=0.03`：

意味着训练最开始的一小段 Step：

> 不立刻让 Learning Rate 跳到目标峰值，而是逐渐升高。

可以把它理解成：

> **让刚开始训练的 Adapter 先慢慢接管。**

---

`num_train_epochs=2`：

意味着：

> 整套训练 Dataset 大约被遍历两次。

注意：

\[
MoreEpochs
\neq
Better
\]

数据不大时：

> 多跑 Epoch 很容易从“学习模式”变成“背训练集”。

---

`max_grad_norm=1.0`：

对应：

# Gradient Clipping
## 梯度裁剪

当 Gradient Norm 异常大时：

> 限制整体梯度规模，降低一次异常更新把训练冲坏的风险。

它不是：

> Loss 修复器。

如果 Grad Norm 经常爆炸：

> 应继续找 Learning Rate、数值稳定性、数据异常等根因。

---

# 十一、现在终于看 `trainer.train()` 背后真正发生了什么

这行：

```python
trainer.train()
```

概念上等价于：

```python
for batch in dataloader:

    outputs = model(
        input_ids=batch["input_ids"],
        attention_mask=batch["attention_mask"],
        labels=batch["labels"],
    )

    loss = outputs.loss

    loss.backward()

    # 如果还没累计够 gradient_accumulation_steps：
    # 暂时不 optimizer.step()

    optimizer.step()

    scheduler.step()

    optimizer.zero_grad()
```

真实 Trainer 会处理：

```text
Mixed Precision
Distributed Training
Gradient Accumulation
Logging
Evaluation
Checkpoint
Scheduler
```

但底层逻辑没有魔法。

仍然是：

\[
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
\]

在我们的 QLoRA 场景：

```text
Base W
Frozen

LoRA A
Updated

LoRA B
Updated
```

所以：

> **每一个 Optimizer Step，都是 `ProcurementLM_V0.1` 真正发生一点变化的时刻。**

---

# 十二、Gradient Accumulation 的精确时间轴

假设：

```text
gradient_accumulation_steps = 4
```

那么不是：

```text
Batch1 → update
Batch2 → update
Batch3 → update
Batch4 → update
```

而是：

```text
Micro Batch 1
Forward
Backward
Gradient 累积
        │
Micro Batch 2
Forward
Backward
Gradient 累积
        │
Micro Batch 3
Forward
Backward
Gradient 累积
        │
Micro Batch 4
Forward
Backward
Gradient 累积
        │
        ▼
Optimizer Step
        │
Scheduler Step
        │
Zero Grad
```

这也纠正一个很常见的误解：

> **Backward 不等于模型参数已经更新。**

真正更新发生在：

```python
optimizer.step()
```

而：

```python
loss.backward()
```

只是：

> 算出 / 累积 Gradient。

这一点一定要锁死。

---

# 十三、第一次训练应该采用“5-Step Smoke Test”

正式大跑之前，把配置临时改成：

```python
training_args = SFTConfig(
    ...
    max_steps=5,
    packing=False,
    eval_strategy="no",
    save_strategy="no",
    logging_steps=1,
)
```

然后观察：

```text
Step 1
Loss 是否 finite？

Step 2
Loss 是否仍正常？

有没有 NaN？

有没有 OOM？

Grad Norm 是否异常？

GPU Peak VRAM 是否在预算内？

Trainable Parameters 是否符合预期？
```

这 5 个 Step 的目标：

> **不是让模型变强。**

而是证明：

# Training Contract Works

Smoke Test 通过以后，再恢复：

```text
完整Dataset
正式Epoch
Evaluation
Checkpoint
Packing
```

这一步通常能省掉大量“训练两小时以后才发现 Mask 错了”的惨剧。

---

# 十四、Packing 不要在第一秒就打开

我们已经学过 Packing 的价值。

但第一次真正训练时，我建议：

```text
Smoke Test
packing=False
```

原因不是 Packing 不好。

而是：

> **先把最简单路径验证正确。**

然后再打开：

```python
packing=True
packing_strategy="bfd"
```

当前 TRL 的 `SFTConfig` 原生支持 `packing=True`，并以 `max_length` 作为 Packed Sequence 长度；当前接口也提供 `packing_strategy` 与独立的 `eval_packing`。([huggingface.co](https://huggingface.co/docs/trl/sft_trainer?utm_source=chatgpt.com))

我们的第一版正式策略可以是：

```text
Train
Packing = ON

Validation
Packing = OFF
```

但有一个前提：

> 训练前已经保证 Semantic Samples 自身满足 Length Contract。

这样 Packing 才是在：

> 优化 GPU 利用率，

而不是：

> 替我们偷偷解决长样本业务问题。

---

# 十五、真正开跑前，我要你检查这 10 件事

这次这 10 项值得直接当 Checklist：

```text
□ 1. Base Model ID / Revision 正确

□ 2. Tokenizer 与 Base Model 对应

□ 3. Chat Template Decode 已人工看过

□ 4. Assistant Mask 非空且边界正确

□ 5. EOS / End-of-turn 正确

□ 6. 样本长度没有静默破坏 Response

□ 7. Target Modules 实际匹配

□ 8. Trainable Parameter Count 符合预期

□ 9. 4-bit / Compute Dtype / Gradient Checkpointing 符合预期

□ 10. 5-Step Smoke Test 正常
```

十项任意一项失败：

> 不进入正式 Run。

这就是：

# Preflight Training Audit
## 训练起飞前审计

---

# 十六、训练过程中究竟看什么？

不要只盯：

```text
loss
```

至少同时观察：

```text
Train Loss
Validation Loss
Learning Rate
Gradient Norm
Peak VRAM
Tokens / Step
Throughput
```

一个健康现象可能是：

```text
Train Loss
逐渐下降

Validation Loss
先下降然后趋稳

Grad Norm
总体有限，没有频繁巨大尖峰

VRAM
稳定在预算范围内
```

但：

> **Loss 下降只能证明模型越来越会预测训练目标 Token。**

不能证明：

> “政府采购风险判断已经变好。”

所以最终仍要进入：

```text
Procurement Benchmark
Hard Negative
Boundary Case
General Capability Regression
```

这就是第 14 阶段存在的原因。

---

# 十七、训练异常怎么读？

这里先建立最实用的诊断地图。

| 现象 | 不要立刻得出什么结论 | 优先检查 |
|---|---|---|
| Loss 完全不降 | “LoRA 太小” | Mask、LR、Gradient、Target Modules、数据 |
| Loss 很快接近极低 | “模型太强” | 泄漏、重复、任务太简单、过拟合 |
| Loss 出现 NaN | “重启试试” | LR、数值精度、异常样本、Grad Norm |
| Train 降、Val 升 | “继续多跑几轮” | 过拟合、数据分布、Epoch |
| OOM | “砍 Rank” | Sequence、Micro Batch、Checkpointing、dtype |
| 输出格式好但业务判断差 | “训练成功” | 数据覆盖、Hard Case、判断监督 |
| 模型复述 User 内容 | “生成参数不好” | Assistant-only Mask / Template |

最后一条特别重要。

如果训练后模型喜欢：

> 把用户问题先完整复述一遍，

第一个嫌疑对象就应该包括：

# Loss Mask

而不是先去改 Temperature。

---

# 十八、Stage 11 最终要留下的 Run Manifest

每一次正式训练必须有一个身份。

例如：

# `ProcurementSFTTrainingRun_V0.1`

记录：

```text
run_id
timestamp

base_model
base_model_revision
tokenizer_revision
chat_template_hash

dataset_version
train_split_hash
validation_split_hash

max_length
packing_policy
loss_policy

quantization_config
compute_dtype

lora_rank
lora_alpha
lora_dropout
target_modules

trainable_parameter_count
trainable_ratio

micro_batch_size
gradient_accumulation_steps
effective_batch

learning_rate
warmup
scheduler
epochs
max_grad_norm

gradient_checkpointing
attention_backend

seed
data_seed

peak_vram

final_train_loss
final_validation_loss

output_adapter_path
```

因为半年以后真正的问题不是：

> “当时模型效果挺好的吧？”

而是：

> **我们能不能准确重建那一次训练？**

---

# 十九、把今天所有内容压成一条完整流程

```text
ProcurementDataset_V0.1
          │
          ▼
Semantic Audit
          │
          ▼
messages
          │
          ▼
Chat Template
          │
          ▼
Assistant Mask Audit
          │
          ▼
Length Audit
          │
          ▼
Tokenizer
          │
          ▼
4-bit NF4 Frozen Base
          │
          ▼
prepare_model_for_kbit_training
          │
          ▼
LoRA Injection
          │
          ▼
Trainable Parameter Audit
          │
          ▼
SFTConfig
          │
          ▼
5-Step Smoke Test
          │
          ▼
Formal Training
          │
          ▼
Forward
          │
          ▼
Causal LM Loss
          │
          ▼
Backward
          │
          ▼
LoRA Gradients
          │
          ▼
Gradient Accumulation
          │
          ▼
Optimizer Step
          │
          ▼
Checkpoint
          │
          ▼
ProcurementLM_V0.1 Adapter
```

这就是我们从第 1 阶段铺到今天的完整训练链。

---

# 二十、本阶段真正需要记住的 5 句话

> **第一，真正的 SFT 不是 `trainer.train()`，而是一份由 Dataset、Template、Mask、Length、Model、LoRA、Optimizer 和 Evaluation 共同构成的训练协议。**

> **第二，在正式花 GPU 时间以前，必须人工 Decode Chat Template、检查 Assistant Loss Mask、检查长度和 Trainable Parameters，并先跑 5～20 Step Smoke Test。**

> **第三，`loss.backward()` 只是计算和累积 Gradient，真正改变 LoRA A/B 的时刻是 `optimizer.step()`；Gradient Accumulation 决定多少个 Micro-batch 合成一次参数更新。**

> **第四，Learning Rate、Warmup、Epoch、Batch、Gradient Clipping 各自解决不同问题，不能把一个异常全部归因于“LoRA 参数不够”。**

> **第五，Training Loss 下降只说明训练目标的 Token 概率在改善；是否真的成为更好的政府采购模型，必须交给独立 Validation、Hard Case 和最终 Benchmark。**

---

# 本阶段最后只记一句话

> **真正可靠的 SFT 训练，不是“代码终于跑起来了”，而是我们能够证明：模型看到了正确的 Prompt，只有正确的 Response Token 在产生 Loss，正确的 LoRA 参数在获得 Gradient，每次 Optimizer Step 都在按可复现配置更新它们，而且整个过程能被 Validation 和 Benchmark 独立检验。**

---

# 下一阶段：第五课 · 第 12 阶段
# Checkpoint、Logging 与训练曲线
## 一场训练跑了几个小时以后，我们怎样判断它是在“正常学习”、已经过拟合，还是正在悄悄出问题？

第 11 阶段解决了：

```text
训练怎样真正启动
```

第 12 阶段会开始读训练过程本身：

```text
Train Loss
Validation Loss
Learning Rate
Grad Norm
Step
Epoch
Checkpoint
Peak VRAM
```

并真正解决：

> **什么时候该继续，什么时候该停，哪个 Checkpoint 值得保留，以及训练中断以后怎样恢复，而不是从头再烧一遍 GPU。**

---

<!-- LESSON 05 STAGE 11 END -->


<!-- LESSON 05 STAGE 12 START -->

# 第五课 · 第 12 阶段
# Checkpoint、Logging 与训练曲线
## 模型已经开始训练以后，我们怎样知道它在正常学习、已经过拟合，还是正在悄悄出问题？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **训练样本上的目标 Token 概率在上升。**
2. **Logging 告诉你训练过程正在发生什么**
3. **Checkpoint 保存某一时刻的模型 / 训练状态**
4. **Evaluation 检查这个时刻的模型在未训练数据上表现如何**
5. **政府采购判断更准确 Hard Negative更好 新项目泛化更强 幻觉更少**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Checkpoint` | 检查点：保存模型和训练状态以便恢复/发布 |
| `Loss` | 损失函数：把预测错误压缩成可优化的数值信号 |
| `Step` | 训练步：通常指一次优化器更新 |
| `Validation` | 验证集：开发阶段用于选模型、调参数和早停 |
| `State` | 状态：保存任务进度、事实和待办 |
| `Adapter` | 适配器：附加在基座模型上的轻量可训练参数模块 |

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

第 11 阶段，我们终于真正启动了：

```text
Forward
↓
Loss
↓
Backward
↓
Gradient
↓
Optimizer Step
↓
LoRA A/B 更新
```

但训练能跑起来，只解决了：

> **“机器有没有动。”**

现在要解决的是更专业的问题：

> **机器正在往正确方向走吗？走到哪里应该保存？哪一个版本值得保留？中途断电以后怎样继续？**

本阶段最终形成：

# `SFTMonitoringAndCheckpointPolicy_V0.1`

---

## 一、先锁死 5 个核心心智模型

**心智模型 1：Logging 是仪表盘，Checkpoint 是存档，Evaluation 是体检。**

三者完全不同：

```text
Logging
告诉你训练过程正在发生什么

Checkpoint
保存某一时刻的模型 / 训练状态

Evaluation
检查这个时刻的模型在未训练数据上表现如何
```

所以：

\[
\boxed{
Logging
\neq
Checkpoint
\neq
Evaluation
}
\]

---

**心智模型 2：Train Loss 下降，只说明模型越来越会拟合训练目标。**

第 2 阶段我们已经知道：

\[
Loss
=
-\log P(\text{正确Target Token})
\]

所以 Train Loss 下降意味着：

> 训练样本上的目标 Token 概率在上升。

但它不自动意味着：

```text
政府采购判断更准确
Hard Negative更好
新项目泛化更强
幻觉更少
```

因此：

\[
\boxed{
LowerTrainLoss
\neq
BetterBusinessModel
}
\]

---

**心智模型 3：真正判断过拟合，要看 Train 和 Validation 的“分叉”。**

典型情况：

```text
Train Loss
持续下降

Validation Loss
先下降
然后上升
```

这非常像：

```text
前期
模型学到可泛化模式

后期
开始越来越贴合训练集细节
```

这就是经典：

# Overfitting
## 过拟合

---

**心智模型 4：能用于推理的 Checkpoint，不一定足够“无缝恢复训练”。**

这是非常重要的一点。

如果你只保存：

```text
LoRA Adapter Weights
```

它足够让你：

> 加载 Base + Adapter 做推理。

但如果想从 Step 2400 精确继续训练，

通常还需要：

```text
Optimizer State
Scheduler State
Global Step
Random State
Trainer State
```

所以：

\[
\boxed{
InferenceCheckpoint
\neq
ResumeCheckpoint
}
\]

---

**心智模型 5：最好的 Checkpoint 不应该由“最后一步”或“最低 Train Loss”自动决定。**

真正要问：

> **哪一个 Checkpoint 在独立验证集和业务 Benchmark 上最好？**

最终：

```text
Last Checkpoint
```

和：

```text
Best Checkpoint
```

完全可能不是同一个。

---

# 二、先建立训练监控的 4 层结构

一场正式 SFT Run 最好同时看四层：

| 层 | 核心指标 | 回答的问题 |
|---|---|---|
| 优化层 | Train Loss、Grad Norm、Learning Rate | 优化过程正常吗？ |
| 泛化层 | Validation Loss | 有没有开始过拟合？ |
| 系统层 | VRAM、吞吐、Step Time | 训练系统稳定吗？ |
| 业务层 | Procurement Benchmark / Hard Case | 模型真的更有用了吗？ |

所以一个成熟训练系统，不是只有：

```text
loss = 0.82
```

而应该能够回答：

> **训练是否稳定、泛化是否改善、系统是否健康、业务是否变好。**

---

# 三、Step、Micro-step、Epoch 必须再精准一次

假设：

```text
micro_batch_size = 1
gradient_accumulation_steps = 8
```

GPU 会经历：

```text
Micro Batch 1
Backward

Micro Batch 2
Backward

...

Micro Batch 8
Backward
↓
Optimizer Step 1
```

因此训练日志里的：

# Global Step

通常应该理解成：

> **Optimizer Update 的进度单位。**

而不是：

> 每个 Micro-batch 都一定算一个完整参数更新。

---

Epoch 则表示：

> 训练集大约被完整遍历一次。

所以：

```text
Step
=
参数更新次数

Epoch
=
数据集遍历进度
```

二者不要混。

如果使用：

```text
Packing
Distributed Training
Gradient Accumulation
```

那么：

> “一个 Step 等于几条原始 Sample”

就更不稳定。

这也是为什么我们前面一直强调：

# Tokens per Step

---

# 四、Train Loss 曲线应该怎么看？

不要期待：

```text
Step 1    2.3
Step 2    2.2
Step 3    2.1
Step 4    2.0
```

像教科书一样完美。

真实训练更可能是：

```text
2.31
2.08
2.19
1.92
2.04
1.81
1.76
1.83
...
```

因为每个 Batch 难度不同。

所以真正应该看：

> **趋势，而不是单个点。**

概念上：

```text
Loss
│\
│ \
│  \__
│     \___
│         \__
└────────────── Step
```

健康训练通常是：

> 在噪声中总体下降。

---

# 五、Validation Loss 为什么更重要？

训练数据：

> 模型已经看过。

Validation 数据：

> 不参与参数更新。

所以 Validation Loss 更接近回答：

> **模型学到的是可迁移模式，还是只在背训练集？**

最经典的三种曲线：

### 情况 A：正常学习

```text
Train Loss      ↓
Validation Loss ↓
```

说明：

> 训练和泛化都在改善。

---

### 情况 B：过拟合

```text
Train Loss      ↓↓↓
Validation Loss ↓ → ↑
```

这时候继续训练：

> 训练集会越来越漂亮。

但真实泛化：

> 反而越来越差。

---

### 情况 C：两边都基本不动

```text
Train Loss      ───
Validation Loss ───
```

这不应该第一时间解释成：

> “Epoch 不够。”

可能是：

```text
Learning Rate不合适
Loss Mask错误
LoRA没有真正注入
Gradient异常
数据质量问题
任务容量不足
```

需要诊断。

---

# 六、Learning Rate 曲线为什么必须和 Loss 一起看？

假设采用：

```text
Warmup
+
Cosine Decay
```

Learning Rate 可能类似：

```text
LR
│      /\
│     /  \
│    /    \
│___/      \____
└─────────────── Step
```

前期：

> Warmup。

中期：

> 较高更新强度。

后期：

> 逐渐降低。

如果你发现：

```text
Loss突然剧烈震荡
```

不能只看 Loss。

要同时看：

```text
当前 Learning Rate
Grad Norm
是否刚进入某个LR阶段
```

因为优化现象需要：

> 多条曲线一起解释。

---

# 七、Grad Norm：它不是“模型有多错”，而是参数更新信号的规模指标

第 2 阶段讲过：

Gradient 表示：

> Loss 对可训练参数的局部敏感度和更新方向。

Gradient Norm：

# 梯度范数

则把大量 Gradient Tensor 压缩成一个总体规模指标。

例如：

```text
正常区域
0.6
0.8
1.1
0.7

异常突然
38.4
```

这种尖峰值得检查。

但不要机械规定：

> “Grad Norm 超过 1 就一定错误。”

因为数值尺度和：

```text
模型
参数量
Optimizer
Loss Scale
Gradient Clipping
```

有关。

我们主要看：

> **趋势和异常尖峰。**

---

# 八、Training Curve 真正有价值的是“联合诊断”

例如你看到：

```text
Train Loss ↓
Validation Loss ↑
Grad Norm 正常
Learning Rate 正常
```

最合理的第一假设：

> 过拟合。

---

如果：

```text
Train Loss 突然 NaN
Grad Norm 先剧烈爆炸
```

更像：

> 数值或优化稳定性问题。

---

如果：

```text
Train Loss 基本不降
Grad Norm ≈ 0
```

则值得检查：

```text
LoRA参数有没有梯度？
Loss Mask是否全是-100？
Target Modules是否真正匹配？
```

所以不要：

> 一条曲线单独判案。

---

# 九、Checkpoint 到底应该保存什么？

这里建立一个非常好用的三层模型。

## 第一层：Model Artifact

对于 LoRA / QLoRA：

```text
Adapter Weights
Adapter Config
Tokenizer / Template相关信息
Base Model Identity
```

作用：

> **部署和推理。**

---

## 第二层：Training State

例如：

```text
Optimizer State
Scheduler State
Global Step
Epoch Progress
Random State
Trainer State
```

作用：

> **从中断位置继续训练。**

---

## 第三层：Run Metadata

例如：

```text
Dataset Version
Code Version
Hyperparameters
Trainable Params
Peak VRAM
Metrics
Timestamp
```

作用：

> **复现和审计。**

这三个东西千万别混成一个：

# “模型文件”

---

# 十、为什么“只保存 Adapter”不能保证精确续训？

假设训练到：

```text
Step 2000
```

AdamW 内部已经形成：

```text
m
v
```

也就是优化器的一阶、二阶状态。

Scheduler 此时：

> Learning Rate 也已经走到了特定位置。

如果你只加载 Adapter：

```text
A/B 权重恢复了
```

但：

```text
Optimizer重新初始化
Scheduler重新开始
```

那么你其实不是：

> 从 Step 2000 原地继续。

而是在：

> **从相同模型权重启动一场新的优化过程。**

这两者可能得到不同结果。

所以真正 Resume：

\[
\boxed{
ModelState
+
OptimizerState
+
SchedulerState
+
ProgressState
}
\]

才更完整。

具体框架保存哪些状态、文件名是什么，会随实现和版本不同；我们记住这个**状态层级**即可。

---

# 十一、多久保存一次 Checkpoint？

这是一个成本权衡。

保存太频繁：

```text
每10 Steps
```

可能导致：

```text
I/O频繁
磁盘大量占用
训练受影响
```

保存太稀：

```text
每5000 Steps
```

如果中途机器掉了：

> 可能损失大量训练进度。

因此第一版应该根据：

```text
单次Run总时长
机器稳定性
Checkpoint大小
Evaluation频率
```

确定。

一个很实用的原则：

> **让一次故障造成的最大可接受训练损失，反推 Save Interval。**

例如：

> 能接受最多损失 20～30 分钟训练，

那就应该让 Checkpoint 周期与此大致匹配。

而不是死记：

```text
save_steps = 100
```

---

# 十二、Evaluation 和 Save 最好建立关联

例如训练：

```text
Step 500
Evaluate
↓
保存 Checkpoint 500

Step 1000
Evaluate
↓
保存 Checkpoint 1000

Step 1500
Evaluate
↓
保存 Checkpoint 1500
```

这样每个保存点都有：

```text
Train状态
+
Validation指标
```

以后才能真正比较：

```text
Checkpoint 500
vs
Checkpoint 1000
vs
Checkpoint 1500
```

否则你保留了一堆 Adapter：

> 却不知道哪个更好。

---

# 十三、Best Checkpoint 应该怎么选？

第一层可以先使用：

# Validation Loss

例如：

```text
Checkpoint 500
Val Loss = 1.04

Checkpoint 1000
Val Loss = 0.88

Checkpoint 1500
Val Loss = 0.91
```

从 Token-level 泛化角度：

> Step 1000 更值得保留。

但我们政府采购项目必须再向前一步。

因为：

\[
\boxed{
LowestValidationLoss
\neq
GuaranteedBestProcurementModel
}
\]

有可能：

```text
Checkpoint A
Val Loss更低

但Hard Negative更差
```

所以最终“Best”应该基于：

> **预先定义的业务评测标准。**

Stage 12 可以暂时建立：

```text
Loss-based candidate selection
```

Stage 14 再进行：

```text
正式业务决赛
```

---

# 十四、Early Stopping：什么时候应该停止继续训练？

假设：

```text
Eval 1  = 0.95
Eval 2  = 0.87
Eval 3  = 0.84
Eval 4  = 0.85
Eval 5  = 0.87
Eval 6  = 0.90
```

而 Train Loss：

> 还在不断下降。

这说明：

> 继续训练越来越可能只是在贴合训练数据。

于是可以建立：

# Early Stopping
## 提前停止

基本思想：

```text
Validation长时间没有改善
↓
达到Patience阈值
↓
停止训练
```

这里：

# Patience

意思不是：

> 等几个 Step。

而通常应该理解为：

> **允许连续多少次 Evaluation 没有改善。**

所以 Early Stopping 必须和：

```text
Evaluation Frequency
```

一起理解。

---

# 十五、不要因为一次 Validation 变差就立刻停

Validation 本身也有噪声。

例如：

```text
0.86
0.84
0.85
0.83
```

这不能简单解释成：

> 第三次 Eval 已经过拟合。

正确看法：

> 看持续趋势。

所以我们通常需要：

```text
Patience
+
Minimum Improvement
```

这样的思想。

也就是说：

> 只有持续没有实质改善，才认为训练已经进入收益递减区。

---

# 十六、Logging Frequency 也不是越密越好

假设：

```text
logging_steps = 1
```

优点：

> 能看到极细训练变化。

缺点：

> 曲线非常吵，日志非常多。

如果：

```text
logging_steps = 1000
```

又太稀。

可能错过：

```text
NaN前兆
Loss异常跳变
Grad Norm尖峰
```

所以应该根据：

> 总 Step 数

来决定。

如果整个训练只有：

```text
500 Steps
```

每 100 Step Log 一次：

> 太粗。

如果总共：

```text
100,000 Steps
```

每一步都写日志：

> 没什么必要。

核心不是固定数字，而是：

\[
\boxed{
LoggingResolution
应足以看见训练动态
}
\]

---

# 十七、给 ProcurementLM_V0.1 定一个第一版 Monitoring Contract

我们可以先规定：

```text
每次Logging记录：
train_loss
learning_rate
grad_norm
epoch
global_step
throughput

每次Evaluation记录：
validation_loss
Procurement validation metrics
hard_negative metrics

系统记录：
peak_vram
step_time
tokens_per_second

每次Checkpoint关联：
global_step
eval metrics
run_id
dataset_version
config version
```

这样一个 Checkpoint 就不再是：

```text
checkpoint-1200/
```

这么一个没有意义的目录名。

它应该能回答：

> **它来自哪次实验，训练到哪里，当时效果怎样。**

---

# 十八、一个训练曲线的完整阅读示例

假设我们训练 `ProcurementLM_V0.1`：

```text
Step    Train Loss    Val Loss
200       1.42          1.38
400       1.10          1.09
600       0.89          0.94
800       0.72          0.91
1000      0.58          0.93
1200      0.47          0.99
```

可以看到：

```text
Train
持续改善

Validation
到Step 800最好
然后开始恶化
```

第一判断：

> Step 800 左右可能已经进入最佳泛化区域。

但接下来不能直接宣布：

> “800 就是最终模型。”

还要拿：

```text
600
800
1000
```

这几个候选 Checkpoint 跑：

```text
Hard Negative
Boundary Case
输出Schema
通用能力回归
```

可能最终发现：

```text
Step 600
业务边界最好
```

这完全合理。

---

# 十九、如果训练中断，恢复训练时必须验证什么？

假设机器断电，最后有：

```text
checkpoint-1200
```

恢复前应该确认：

```text
Base Model Revision没变
Tokenizer没变
Dataset版本没变
LoRA Config没变
Target Modules没变
Optimizer / Scheduler State存在
Global Step正确
```

然后 Resume。

如果 Dataset 已经从：

```text
V0.1
```

改成：

```text
V0.2
```

这时候最好不要还叫：

> “继续同一次训练”。

更准确：

> **这是从旧 Checkpoint 初始化的一次新 Run。**

这对实验治理非常重要。

---

# 二十、Checkpoint 不等于最终发布模型

训练阶段可能产生：

```text
checkpoint-200
checkpoint-400
checkpoint-600
checkpoint-800
final_adapter
```

这些都属于：

# Training Artifacts

真正发布：

# `ProcurementLM_V0.1`

之前还需要：

```text
选择候选Checkpoint
↓
固定Benchmark
↓
正式对比
↓
确认回归
↓
冻结版本
↓
保存 / Merge
```

所以：

\[
\boxed{
Checkpoint
\neq
Release
}
\]

Checkpoint 是：

> 候选状态。

Release 是：

> 经过评测和版本冻结的模型产品。

---

# 二十一、本阶段最危险的 7 个反例

第一，**只看 Train Loss，看到一直下降就一直训练。**  
可能已经严重过拟合。

第二，**默认最后一个 Checkpoint 就是最好的。**  
最后一步可能已经过了最佳泛化点。

第三，**只保存 LoRA Adapter，却以为一定能精确 Resume。**  
缺少 Optimizer / Scheduler 等状态时，不是严格原地续训。

第四，**一次 Validation 变差就立刻 Early Stop。**  
单点噪声不等于趋势。

第五，**Checkpoint 保存很多，却不记录对应 Eval Metric。**  
以后无法判断谁值得保留。

第六，**训练日志只有 Loss。**  
Grad Norm、LR、VRAM 和业务指标都可能暴露不同问题。

第七，**改了 Dataset 还继续沿用同一个 Run ID。**  
实验边界被破坏，结果无法解释。

---

# 二十二、把整个第 12 阶段压成 5 句话

> **第一，Logging 是训练仪表盘，Evaluation 是泛化检查，Checkpoint 是状态存档；三者职责不同。**

> **第二，Train Loss 下降只能证明模型更贴合训练目标，判断过拟合必须同时看 Validation，并关注 Train/Val 是否持续分叉。**

> **第三，一个可推理的 Adapter Checkpoint 不等于一个可无缝续训的 Checkpoint；精确 Resume 还需要 Optimizer、Scheduler、Step 和随机状态等训练状态。**

> **第四，Best Checkpoint 不应该默认是最后一个或 Train Loss 最低的，而应先由独立 Validation 筛选，再由固定业务 Benchmark 最终决定。**

> **第五，训练曲线必须联合看：Loss、Validation、Learning Rate、Grad Norm、VRAM 和业务指标一起解释，不能拿单个数字判案。**

---

# 本阶段最核心的一张图

```text
                         Training Run
                              │
                              ▼
                      Optimizer Step
                              │
               ┌──────────────┼──────────────┐
               │              │              │
               ▼              ▼              ▼
            Logging       Evaluation     Checkpoint
               │              │              │
               ▼              ▼              ▼
        Train Loss        Val Loss       Adapter State
        Learning Rate     Hard Cases     Optimizer State
        Grad Norm         Metrics        Scheduler State
        Throughput                       Trainer State
               │              │              │
               └──────────────┼──────────────┘
                              ▼
                         Curve Analysis
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
         正常学习           过拟合           不稳定
             │                │                │
             ▼                ▼                ▼
          继续训练          Early Stop        Diagnose
             │
             └───────────┬────┘
                         ▼
                Candidate Checkpoints
                         │
                         ▼
                  Procurement Benchmark
                         │
                         ▼
                    Best Candidate
```

脑中只留一句：

> **训练不是跑到结束，而是持续观察、保存证据、选择最佳状态。**

---

# 二十三、本阶段掌握测试

现在不回看正文，你应该能够解释：Logging、Evaluation、Checkpoint 三者有什么区别；为什么 Train Loss 一直下降并不等于模型一直变好；什么样的 Train/Validation 曲线提示过拟合；什么是 Global Step，为什么它不能简单等同于 Micro-batch 数量；Learning Rate 曲线为什么必须和 Loss 一起看；Grad Norm 可以帮助诊断什么；为什么一个 Adapter 文件可以用于推理，却不一定足以精确 Resume；Optimizer State 和 Scheduler State 为什么影响续训；为什么 Best Checkpoint 不一定是 Last Checkpoint；Early Stopping 的 Patience 为什么应该以 Evaluation 次数理解；为什么单次 Val Loss 反弹不能直接判定过拟合；为什么 Checkpoint 必须和 Run ID、Dataset Version、指标绑定；以及为什么最终发布模型必须经过 Stage 14 的正式 Benchmark，而不是训练结束自动宣布胜利。

如果这些能完整讲出来：

\[
\boxed{
第五课第12阶段真正掌握
}
\]

---

# 本阶段最后只记一句话

> **Checkpoint 是“某一时刻模型与训练状态的存档”，Logging 是“训练过程的仪表盘”，Evaluation 是“模型离开训练集后的体检”；真正可靠的 SFT 不是把 Epoch 跑完，而是用 Train/Validation 曲线、Grad Norm、Learning Rate 和业务指标持续判断模型何时仍在学习、何时开始过拟合，并把最值得进入最终评测的状态完整保存下来。**

---

# 下一阶段：第五课 · 第 13 阶段
# LoRA Merge、模型保存与推理
## 训练出来的 Adapter 到底怎样变成真正能部署、能复现、能推理的 `ProcurementLM_V0.1`？

下一阶段我们会把：

```text
Base Model
+
LoRA Adapter
```

处理成两条正式交付路径：

```text
路径 A
Base + Adapter
动态加载

路径 B
Base + LoRA
      ↓
Merge
      ↓
Merged Model
```

并精准解决：

> **到底应该保存哪些文件、Merge 前后有什么区别、Tokenizer/Chat Template 为什么必须一起锁定，以及怎样避免“Adapter 明明训练成功，换一台机器却复现不出来”。**

---

<!-- LESSON 05 STAGE 12 END -->


<!-- LESSON 05 STAGE 13 START -->

# 第五课 · 第 13 阶段
# LoRA Merge、模型保存与推理
## 训练出来的 Adapter，怎样真正变成可部署、可复现的 `ProcurementLM_V0.1`？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **把原来分开的 Base Weight 和 LoRA 增量提前加在一起。**
2. **这个 merged checkpoint 本身不会替你保留“可随时拆出来的 LoRA”。**
3. **Merge 前永远保留 Adapter 原件。**
4. **同样的模型权重收到的是不同 Token 序列。**
5. **Adapter A/B + Adapter Config**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Adapter` | 适配器：附加在基座模型上的轻量可训练参数模块 |
| `LoRA` | LoRA：冻结大部分基座参数，只训练低秩增量矩阵 |
| `Checkpoint` | 检查点：保存模型和训练状态以便恢复/发布 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Tokenizer` | 分词器：文本与 Token ID 之间的编码/解码组件 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |

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

到第 12 阶段，我们手里已经有了一个经过训练和筛选的 LoRA Checkpoint。

现在模型仍然可以理解为：

\[
\boxed{
BaseModel + LoRAAdapter
}
\]

但到了部署阶段，我们必须做一个决定：

```text
路径 A
Base Model
+
LoRA Adapter
动态加载
```

或者：

```text
路径 B
Base Model
+
LoRA Adapter
        ↓
       Merge
        ↓
一个新的完整模型权重
```

这两条路都能得到微调后的行为，但它们的：

> 文件结构、部署方式、版本管理、磁盘大小、可切换能力

完全不同。

本阶段最终形成：

# `ProcurementLMReleaseBundle_V0.1`

---

## 一、先锁死 5 个核心心智模型

**心智模型 1：Adapter 模式与 Merge 模式，模型“学到的东西”并没有变。**

LoRA 训练时：

\[
W' = W + sBA
\]

Adapter 模式推理：

\[
y=Wx+sBAx
\]

Merge 以后：

\[
W_{\text{merged}}
=
W+sBA
\]

推理变成：

\[
y=W_{\text{merged}}x
\]

所以：

\[
\boxed{
Merge
\neq
再次训练
}
\]

它只是：

> **把原来分开的 Base Weight 和 LoRA 增量提前加在一起。**

---

**心智模型 2：保存 Adapter ≠ 保存完整模型。**

如果只保存 LoRA：

```text
Adapter A/B
+
Adapter Config
```

你仍然需要：

```text
正确的 Base Model
```

才能恢复完整行为。

因此：

\[
\boxed{
AdapterArtifact
依赖
BaseModelIdentity
}
\]

---

**心智模型 3：Merge 以后部署更像普通模型，但失去了“Adapter 可拆卸性”。**

动态 Adapter：

```text
Base
├── Procurement Adapter
├── Contract Adapter
└── Other Adapter
```

可以切换。

Merge 以后：

```text
ProcurementLM_Merged
```

LoRA 增量已经写进完整权重。

如果没有另外保存原 Adapter：

> 这个 merged checkpoint 本身不会替你保留“可随时拆出来的 LoRA”。

所以：

> **Merge 前永远保留 Adapter 原件。**

---

**心智模型 4：Tokenizer、Chat Template 与 Base Model Revision 都是模型产品的一部分。**

很多部署失败不是 Weight 坏了。

而是：

```text
训练时 Template A

部署时 Template B
```

或者：

```text
训练时 Tokenizer Revision A

部署时 Revision B
```

于是：

> 同样的模型权重收到的是不同 Token 序列。

所以发布模型不能只保存：

```text
model.safetensors
```

而要保存：

> **完整推理协议。**

---

**心智模型 5：模型保存完成 ≠ 模型发布完成。**

真正的 Release 流程应该是：

```text
Candidate Checkpoint
        ↓
Adapter / Merge Packaging
        ↓
Inference Parity Test
        ↓
Tokenizer / Template Lock
        ↓
Benchmark
        ↓
Manifest
        ↓
Release
```

所以：

\[
\boxed{
Save
\neq
Release
}
\]

---

# 二、先把两种交付方式彻底分清

| 维度 | Base + Adapter | Merged Model |
|---|---|---|
| Base Model | 单独存在 | 已写入完整权重 |
| Adapter | 单独加载 | 已合并 |
| 文件大小 | Adapter 很小 | 接近完整模型 |
| 多 Adapter 切换 | 很方便 | 不方便 |
| 部署结构 | 两部分 | 更像普通完整模型 |
| Base Revision 依赖 | 显式依赖 | 已固定进 merged 权重 |
| 实验管理 | 很方便 | 较重 |
| 单一固定部署 | 可以 | 通常更方便 |

因此不要问：

> “Merge 是不是更高级？”

真正的问题是：

> **部署到底需不需要 Adapter 可切换能力？**

---

# 三、Merge 数学上到底发生了什么？

第 6、7 阶段我们有：

\[
\Delta W
=
sBA
\]

其中标准 LoRA 常见：

\[
s=\frac{\alpha}{r}
\]

因此：

\[
W'
=
W+sBA
\]

Merge 做的就是：

\[
\boxed{
W_{\text{merged}}
=
W+sBA
}
\]

原先 Forward：

```text
输入 x
  │
  ├── Base W ───────► Wx
  │
  └── LoRA A→B ─────► sBAx
                        │
                 两条路径相加
```

Merge 后：

```text
输入 x
  │
  ▼
W_merged
  │
  ▼
W_merged x
```

数学上：

\[
(W+sBA)x
=
Wx+sBAx
\]

因此理想情况下：

> **Adapter 模式与 Merge 模式应该产生等价行为。**

实际浮点计算中可能出现极小数值差异。

---

# 四、Merge 最大的意义不是“效果变好”，而是部署结构发生变化

这是今天特别重要的一点。

不要形成：

```text
Merge前
模型一般

Merge后
模型更强
```

这样的理解。

如果同一个 Base、同一个 Adapter、同一种数值精度：

> Merge 本身不应该凭空提升业务能力。

它主要改变：

# Parameter Representation

从：

\[
W + \Delta W
\]

两份参数

变成：

\[
W_{\text{merged}}
\]

一份完整权重。

所以：

\[
\boxed{
Merge
是Packaging / Deployment操作
}
\]

而不是：

# Training Operation

---

# 五、QLoRA 场景下，Merge 要特别小心

我们训练时的 Base Model 是：

```text
4-bit NF4
Frozen Base
```

但 LoRA 学到的：

\[
\Delta W
\]

并不意味着我们应该简单地认为：

> “直接往原来的 4-bit 编码里加 BA 就完事。”

第一版最好建立这样的流程：

```text
QLoRA训练
        ↓
得到 LoRA Adapter
        ↓
重新加载
同一个 Base Model Revision
以 BF16 / FP16 等适合 Merge 的精度
        ↓
加载 Adapter
        ↓
Merge
        ↓
得到完整 Merged Model
```

也就是说：

> **QLoRA 的 4-bit 是训练时节省 Base Weight 显存的策略；最终 Merge 的权重精度与部署量化，是另一个独立决策。**

如果部署最终还需要：

```text
4-bit
8-bit
其他量化格式
```

更清楚的思路是：

```text
Base + Adapter
     ↓
Merge得到完整模型
     ↓
验证
     ↓
再做部署量化
```

即：

\[
\boxed{
TrainingQuantization
\neq
DeploymentQuantization
}
\]

这两个不要混。

---

# 六、真正应该保存哪些东西？

我们把模型产物拆成四层。

### 第一层：Adapter Artifact

至少包含概念上的：

```text
LoRA Weights
LoRA Config
Rank
Alpha
Target Modules
Base Model Identity
```

这是：

> 最小的微调成果。

---

### 第二层：Tokenizer / Protocol Artifact

至少锁定：

```text
Tokenizer
Chat Template
Special Tokens
EOS / EOT Policy
System Prompt Policy
```

这是：

> 模型怎样“听懂请求”的协议。

---

### 第三层：Model Artifact

可以有两种：

```text
Base + Adapter
```

或：

```text
Merged Model
```

这是：

> 真正用于推理的权重组合。

---

### 第四层：Release Manifest

记录：

```text
release_id
base_model
base_revision

adapter_version
adapter_hash

tokenizer_revision
chat_template_hash

dataset_version
training_run_id

selected_checkpoint

merge_dtype

generation_config

benchmark_version
benchmark_result

release_timestamp
```

这才让：

# `ProcurementLM_V0.1`

成为一个能复现的模型版本。

---

# 七、动态 Adapter 模式应该怎样理解？

部署逻辑：

```text
Base Model
    ↓
加载
    ↓
挂载 Procurement Adapter
    ↓
Inference
```

概念代码类似：

```python
base_model = load_base_model(BASE_MODEL_ID)

model = load_adapter(
    base_model,
    ADAPTER_PATH,
)

model.eval()
```

它的最大优势是：

> **一个 Base 可以挂不同 Adapter。**

例如：

```text
Base Model
│
├── Procurement-Risk-V0.1
├── Procurement-Classification-V0.2
└── Contract-Review-V0.1
```

这对于：

```text
实验
灰度测试
多业务线
快速回滚
```

特别方便。

所以研究阶段和多 Adapter 系统：

> 动态加载往往非常舒服。

---

# 八、Merged Model 模式什么时候更有吸引力？

如果生产环境只需要：

> 一个固定的政府采购模型。

那么：

```text
Base
+
Adapter
```

每次都动态组合，

可能没有必要。

Merge 后：

```text
ProcurementLM_V0.1_Merged
```

可以更接近普通 Causal LM：

```text
加载完整模型
↓
Tokenizer
↓
Generate
```

这样部署链更简单。

但代价也很明确：

> 完整模型文件会比 Adapter 大很多。

同时：

> Adapter 不再可以简单关闭来恢复 Base 行为。

因此两种路径本质上是：

\[
\boxed{
Flexibility
\quad vs \quad
DeploymentSimplicity
}
\]

---

# 九、推理阶段最重要的不是 `generate()`，而是协议一致

假设训练时：

```text
System
↓
User
↓
Assistant
```

使用某个原生 Chat Template。

部署时就必须继续遵守同样协议。

推理数据应该是：

```python
messages = [
    {
        "role": "system",
        "content": "你是政府采购文件审查助手。"
    },
    {
        "role": "user",
        "content": "审查以下采购条款：..."
    }
]
```

然后概念上：

```python
inputs = tokenizer.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=True,
)
```

注意这里和训练不同。

训练：

```text
System
User
Assistant Gold Answer
```

因此通常：

```text
add_generation_prompt=False
```

推理：

```text
System
User
```

还没有 Assistant Answer。

所以通常需要：

```text
add_generation_prompt=True
```

核心不是记布尔值。

核心是：

\[
\boxed{
训练和推理使用同一对话协议
}
\]

---

# 十、正式验证 Merge，必须做 Inference Parity Test

Merge 完以后，不能直接说：

> “文件成功保存，所以完成。”

至少选一组固定样本：

```text
Normal Case
Hard Positive
Hard Negative
Boundary Case
Unknown / needs_review
```

分别跑：

```text
A
Base + Adapter

B
Merged Model
```

并保持：

```text
同Tokenizer
同Chat Template
同Prompt
同Generation Config
```

为了减少随机噪声，第一轮最好采用：

```text
do_sample = False
```

或者其他确定性解码策略。

然后比较：

```text
输出结构
风险分类
理由
停止位置
业务结果
```

如果数值精度完全一致，输出往往应高度接近；如果 Merge、重新量化或不同 kernel/dtype 被引入，则允许存在一定数值差异。

所以真正的原则是：

\[
\boxed{
MergeSuccess
需要行为验证
}
\]

而不仅仅是：

```text
save_pretrained() 没报错
```

---

# 十一、Generation Config 也属于模型发布的一部分

同一个模型：

```text
temperature = 0
```

和：

```text
temperature = 1.2
```

可能表现非常不同。

因此不能把所有生成差异都归因于：

> 模型 Weight。

正式 Benchmark 应固定：

```text
max_new_tokens
temperature
top_p
top_k
do_sample
repetition_penalty
stop / EOS policy
```

对于政府采购第一版评测：

> 更适合先使用确定性或低随机性的 Generation Baseline。

原因很简单：

> 我们首先要比较模型能力，而不是抽样运气。

最终生产环境是否加入 Sampling：

> 再根据业务需求决定。

---

# 十二、三个最重要的保存策略

对于 `ProcurementLM_V0.1`，不要只留一个文件夹。

建议同时保留：

```text
1. 原始 Best Adapter
2. Merged Release Candidate
3. Release Manifest
```

以及对应的：

```text
Tokenizer
Chat Template
Benchmark Report
Training Run ID
```

可以形成：

```text
ProcurementLM_V0.1/
│
├── adapter/
│
├── merged/
│
├── tokenizer/
│
├── config/
│
├── benchmark/
└── release_manifest.json
```

这样以后你可以：

> 重新 Merge。

也可以：

> 恢复 Adapter 模式。

还可以：

> 对 merged 模型重新做另一种部署量化。

这比只留一个最终大模型文件可靠得多。

---

# 十三、这一阶段最危险的错误

第一，**训练完只保存 Adapter，却没有记录准确 Base Revision。**  
以后可能根本无法重建相同模型。

第二，**Merge 完以后把原 Adapter 删除。**  
你失去了最轻量、最灵活的训练成果原件。

第三，**QLoRA 训练完直接把“4-bit Base”与“最终部署量化”混为一件事。**  
训练量化与部署量化应分开管理。

第四，**Merge 前后用不同 Tokenizer 或 Chat Template 做测试。**  
你测到的就不再是 Merge 差异，而是协议差异。

第五，**只验证模型能生成文字，不验证 Hard Negative 和 Boundary Case。**  
“能说话”不是 ProcurementLM Release 标准。

第六，**把 Merge 当成一次新的训练。**  
Merge 不产生新的监督信号。

第七，**只记录模型目录，不记录 Generation Config。**  
以后相同模型也可能复现不出相同结果。

---

# 十四、本阶段工程产物：`ProcurementLMReleaseBundle_V0.1`

最终发布包至少应该有：

```text
release_id

base_model_id
base_model_revision

adapter_checkpoint
adapter_hash

merged_model_path
merge_dtype

tokenizer_revision
chat_template_hash

system_prompt_version

generation_config

dataset_version
training_run_id
selected_checkpoint

benchmark_version
benchmark_results

adapter_parity_test
merged_parity_test

release_status
```

其中：

# `release_status`

不要训练一结束就写：

```text
production
```

更合理的是：

```text
candidate
```

直到第 14 阶段完成：

# Baseline vs Fine-tuned Model 正式对比

才能决定是否：

> 冻结为正式的 `ProcurementLM_V0.1`。

---

# 十五、把整个第 13 阶段压成最精准的 5 句话

> **第一，LoRA Merge 不是继续训练，而是把 \(sBA\) 提前加回 Base Weight，形成 \(W_{\text{merged}}=W+sBA\)。**

> **第二，Base + Adapter 与 Merged Model 理论上表达相同微调行为，但前者更灵活、文件更小，后者更适合单一固定模型的简化部署。**

> **第三，QLoRA 的 4-bit 是训练时 Base Weight 的内存策略；Merge 与最终部署量化应该作为独立阶段处理，不要把三件事混在一起。**

> **第四，模型产品绝不只是权重：Base Revision、Adapter、Tokenizer、Chat Template、Generation Config 和 Release Manifest 都必须锁定。**

> **第五，Merge 成功的判据不是代码没报错，而是 Base+Adapter 与 Merged Model 在同一推理协议和固定 Benchmark 下通过行为一致性检查。**

---

# 本阶段最核心的一张图

```text
                    Best LoRA Checkpoint
                            │
                            ▼
                    Adapter Artifact
                            │
             ┌──────────────┴──────────────┐
             │                             │
             ▼                             ▼
      Dynamic Adapter Path             Merge Path
             │                             │
         Base Model                   Base Model
             +                             +
          Adapter                       ΔW=BA
             │                             │
             ▼                             ▼
         Inference                 W_merged=W+ΔW
             │                             │
             │                             ▼
             │                       Merged Model
             │                             │
             └──────────────┬──────────────┘
                            ▼
                   Same Tokenizer
                   Same Chat Template
                   Same Generation Config
                            │
                            ▼
                    Inference Parity
                            │
                            ▼
                    Procurement Benchmark
                            │
                            ▼
                   Release Candidate
```

脑中只留一句：

> **训练产物是 Adapter，部署产物可以是 Adapter，也可以是 Merge；真正的模型产品则是“权重 + 协议 + 版本 + 评测证据”。**

---

# 本阶段掌握测试

不回看正文，你现在应该能够解释：LoRA Merge 数学上到底做了什么；为什么 Merge 不等于继续训练；Base+Adapter 与 Merged Model 在行为上是什么关系；为什么 Adapter 文件通常不能脱离 Base Model；为什么 Merge 后文件会明显变大；什么时候动态 Adapter 更合理；什么时候 Merged Model 更方便；QLoRA 的 4-bit Base 与最终部署量化为什么是两回事；为什么建议用较合适精度的同版本 Base 重新加载 Adapter 再完成 Merge；为什么 Merge 后还必须保存原始 Adapter；为什么 Tokenizer 和 Chat Template 是 Release 的一部分；训练时和推理时 `add_generation_prompt` 的逻辑为什么不同；为什么 Generation Config 必须固定；什么是 Inference Parity Test；以及为什么最终模型还不能在第 13 阶段直接宣布“成功”。

如果这些能完整讲出来：

\[
\boxed{
第五课第13阶段真正掌握
}
\]

---

# 下一阶段：第五课 · 第 14 阶段
# Baseline vs Fine-tuned Model 正式对比
## 我们花了整整一课训练模型，究竟有没有真的把它变得更好？

第 14 阶段就是第五课真正的**验收阶段**。

我们不再看：

```text
Train Loss
漂亮不漂亮
```

而是正式把：

```text
Base Model
        VS
ProcurementLM_V0.1
```

放到同一套：

```text
Normal Cases
Hard Positives
Hard Negatives
Boundary Cases
Unknown / needs_review
Format Compliance
General Capability Regression
```

上进行盲测和量化对比。

最终要回答的只有一个问题：

> **SFT + LoRA / QLoRA 到底给政府采购任务带来了哪些可验证的行为变化，又付出了什么代价？**

而第 14 阶段结束时，我们才会真正得到第五课最终交付物：

# `ProcurementLM_V0.1`

---

<!-- LESSON 05 STAGE 13 END -->


<!-- LESSON 05 STAGE 14 START -->

# 第五课 · 第 14 阶段
# Baseline vs Fine-tuned Model 正式对比
## 我们花了一整课训练模型，究竟有没有真的把它变得更好？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **微调的价值不是“模型参数变了”，而是它在独立、固定、可复现的业务测试上，证明自己改变了正确的行为，同时没有付出不可接受的回归代价。**
2. **模型更会预测训练目标。**
3. **真正高风险条款，**
4. **漏报了什么，误报了什么。**
5. **关键词 Shortcut。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `Regression` | 回归测试：更新后验证旧能力和关键切片没有退化 |
| `Recall` | 召回率：真实风险中被系统成功找出的比例 |
| `LoRA` | LoRA：冻结大部分基座参数，只训练低秩增量矩阵 |
| `Hard Negative` | 高难负例：表面像风险但正确结论不应判风险 |

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

这是第五课最后一个阶段。

前 13 个阶段，我们完成了：

```text
ProcurementDataset_V0.1
        ↓
SFT Formatting Contract
        ↓
Loss Mask
        ↓
Length / Packing
        ↓
LoRA / QLoRA
        ↓
Training
        ↓
Checkpoint Selection
        ↓
Merge / Release Candidate
```

现在终于到了最重要的一步：

> **不要再问“Loss 降了没有”，而要正式证明模型行为到底发生了什么变化。**

今天最终要形成两个交付物：

# `ProcurementBenchmark_V0.1`

以及第五课最终成果：

# `ProcurementLM_V0.1`

---

## 一、本阶段先锁死 5 个核心心智模型

**心智模型 1：训练完成不等于模型变好，只有固定测试集上的可重复提升才算证据。**

训练 Loss：

\[
\downarrow
\]

只能说明：

> 模型更会预测训练目标。

真正验收必须看：

\[
\boxed{
FineTunedPerformance
-
BasePerformance
}
\]

在**未参与训练和调参的数据**上到底是多少。

---

**心智模型 2：公平对比必须只改变“模型参数”，其他推理条件全部锁死。**

Base Model 和 Fine-tuned Model 必须尽量使用相同的：

```text
Base Revision
Tokenizer
Chat Template
System Prompt
Prompt
Context
Generation Config
max_new_tokens
停止规则
推理代码
```

否则：

```text
Model A
temperature = 0

Model B
temperature = 0.8
```

最后得到不同输出，

你根本不知道差异来自：

> 微调，

还是：

> 解码随机性。

所以正式实验要满足：

\[
\boxed{
OnlyModelConditionChanges
}
\]

---

**心智模型 3：不能只看一个总 Accuracy，必须看错误类型。**

政府采购风险识别尤其如此。

假设模型：

```text
100 条
预测对了 90 条
```

看起来：

\[
Accuracy=90\%
\]

但如果漏掉的 10 条全部是：

> 真正高风险条款，

这个模型并不好用。

所以必须拆：

```text
True Positive
False Positive
True Negative
False Negative
```

尤其关注：

> **漏报了什么，误报了什么。**

---

**心智模型 4：Benchmark 必须按 Slice 看，不然平均分会掩盖真正的问题。**

我们第四课专门构造了：

```text
Normal
Hard Positive
Hard Negative
Boundary Case
Unknown / needs_review
```

今天这些终于发挥作用。

一个总分可能很好，

但如果：

```text
Hard Negative
大量误报
```

那说明模型仍然在走：

> 关键词 Shortcut。

所以：

\[
\boxed{
OverallMetric
+
SliceMetric
}
\]

必须同时存在。

---

**心智模型 5：最终验收不是“Fine-tuned 所有指标都必须更高”，而是收益和代价必须透明。**

微调可能带来：

```text
采购判断 ↑
结构稳定性 ↑
专业表达 ↑
```

同时也可能带来：

```text
通用回答能力 ↓
输出变得过于模板化
Latency ↑
Adapter / Model管理成本 ↑
```

所以最终问题应该是：

> **模型获得了什么能力，又付出了什么代价？**

---

# 二、先把三个数据集彻底分开

这一阶段必须再次强调：

```text
Train
Validation
Test
```

三者职责不同。

### Train Set

用于：

> 参数更新。

---

### Validation Set

用于：

```text
选Checkpoint
调Rank
调Learning Rate
调Epoch
调Target Modules
Early Stopping
```

也就是说：

> 我们已经反复看过 Validation。

因此它已经参与了开发决策。

---

### Test Set

最终测试集必须做到：

> **训练时没看过，调参时也没看过。**

它只在模型已经被冻结为 Release Candidate 后正式运行。

所以：

\[
\boxed{
Validation
\neq
FinalTest
}
\]

如果你拿 Test Set 调了三轮参数，

它就已经不再是：

> 真正的 Final Test。

---

# 三、建立 `ProcurementBenchmark_V0.1`

第一版正式 Benchmark 不需要巨大。

但必须结构完整。

例如：

| Slice | 要测试什么 |
|---|---|
| Normal | 普通采购条款是否正确判断 |
| Hard Positive | 隐蔽风险能否识别 |
| Hard Negative | 看似危险但实际合理的条款是否避免误报 |
| Boundary Case | 相邻规则、复杂条件能否区分 |
| Unknown / needs_review | 信息不足时是否知道“不确定” |
| Format Compliance | 输出 Schema 是否稳定 |
| General Regression | 微调是否破坏基础通用能力 |

核心不是：

> 一共 500 条还是 5000 条。

第一优先级是：

> **覆盖模型真正容易失败的边界。**

---

# 四、先定义核心分类指标

假设任务中：

```text
Positive
=
存在风险
```

那么：

### Precision
## 精确率

\[
Precision
=
\frac{TP}{TP+FP}
\]

回答：

> **模型报警的案例中，有多少是真的风险？**

如果 Precision 很低：

> 模型会大量误报。

---

### Recall
## 召回率

\[
Recall
=
\frac{TP}{TP+FN}
\]

回答：

> **真正的风险案例中，有多少被模型抓到了？**

如果 Recall 很低：

> 模型会大量漏报。

---

### F1

\[
F1
=
2
\cdot
\frac{Precision\cdot Recall}
{Precision+Recall}
\]

它用于：

> 综合平衡 Precision 与 Recall。

但不要把 F1 当成唯一真理。

政府采购场景里：

> False Positive 和 False Negative 的业务成本可能并不对称。

最终必须分别看。

---

# 五、真正值得看的，是 Confusion Matrix

假设有：

```text
TP
真正风险 → 模型判风险

FP
实际合理 → 模型误判风险

TN
实际合理 → 模型判合理

FN
真正风险 → 模型漏报
```

这四个数字比一个 Accuracy 更有解释力。

例如：

| 模型 | TP | FP | TN | FN |
|---|---:|---:|---:|---:|
| Base | 61 | 32 | 68 | 39 |
| Fine-tuned | 82 | 15 | 85 | 18 |

这时候你才能清楚看到：

```text
漏报 FN
39 → 18

误报 FP
32 → 15
```

而不是只说：

> “准确率提高了。”

注意：

上面的数字只是教学示例，不是我们的实际模型成绩。

---

# 六、Hard Negative 是这次验收的核心中的核心

我们一直用这个例子：

### Hard Positive

> 投标人在投标截止日前须已在本市设立固定服务机构。

这里：

```text
投标前
+
已存在
+
准入要求
```

可能构成明显风险。

---

### Hard Negative

> 中标后供应商应保证 2 小时现场服务响应，但可自行确定服务资源组织方式。

这里虽然也出现：

```text
现场
服务
地域
```

但它更接近：

> 履约能力要求，

而不是：

> 投标准入地域限制。

如果 Fine-tuned Model 真学到了：

> 决策边界，

我们希望看到：

```text
Hard Positive Recall ↑

同时

Hard Negative False Positive ↓
```

这比：

> 普通案例 Accuracy 提高几个百分点，

有价值得多。

因为它能证明：

> 模型没有只学会看到“本地”就报警。

---

# 七、`needs_review` 必须单独评测

真实采购审查不会永远只有：

```text
risk
no_risk
```

还有：

# `needs_review`

也就是：

> 当前证据不足，不能可靠下结论。

例如输入只给：

> “供应商须满足当地要求。”

但没有：

```text
什么当地要求？
发生在投标前还是履约后？
是否限制供应商所在地？
是否允许等效方式？
```

一个成熟模型不应该强行输出：

> 有风险。

也不应该强行输出：

> 无风险。

所以 Benchmark 还要测：

# Abstention Behavior
## 拒绝武断判断 / 不确定性处理

这里真正想看到的是：

> 该不确定的时候敢不确定，该判断的时候不要全部逃到 `needs_review`。

---

# 八、结构化输出必须成为独立指标

假设我们的目标 Schema 是：

```json
{
  "risk": true,
  "risk_type": "供应商资格条件",
  "reason": "...",
  "needs_review": false
}
```

那么至少应该统计：

# Format Compliance Rate

例如：

\[
SchemaCompliance
=
\frac{\text{合法Schema输出数量}}
{\text{总输出数量}}
\]

需要检查：

```text
JSON 能否解析

必填字段是否存在

字段类型是否正确

枚举值是否有效

有没有额外废话

有没有答案被截断
```

因为一个业务模型：

> 判断是对的，但接口每天随机坏格式，

照样不能稳定接入系统。

---

# 九、理由质量不能简单用“和 Gold 文本像不像”判断

这是一个很重要的点。

专家答案可能写：

> “该要求将投标前已具备本地机构作为准入条件，具有地域限制风险。”

模型也可能写：

> “供应商必须在投标截止前已经拥有本地机构，该条件限制了外地供应商参与资格。”

两者：

> 文字不同。

但业务逻辑：

> 基本相同。

所以单纯使用：

```text
BLEU
ROUGE
字符串相似度
```

往往不能很好代表：

> 理由是否正确。

更合理的 Reason Evaluation 应该看：

```text
是否引用正确事实

是否抓住正确触发条件

是否遗漏关键条件

是否引入输入中不存在的事实

结论和理由是否一致
```

第一版可以用：

> 人工 Rubric + 抽样盲审。

---

# 十、正式做一次“成对比较”

这一阶段一个特别重要的方法叫：

# Paired Evaluation
## 成对评测

同一条 Test Case：

```text
Case 001
```

同时给：

```text
Base Model
```

和：

```text
Fine-tuned Model
```

于是每个案例都得到：

```text
Gold
Base Output
Fine-tuned Output
```

这样你能直接分类：

```text
Base错 → Fine-tuned对
真正改善

Base对 → Fine-tuned错
回归

两者都对
无变化

两者都错
仍未解决
```

这比只比较两个总分强得多。

因为它告诉你：

> **微调到底改变了哪些具体行为。**

---

# 十一、真正重要的是“净变化矩阵”

可以建立：

| Base | Fine-tuned | 意义 |
|---|---|---|
| 错 | 对 | **Gain：微调修复的案例** |
| 对 | 错 | **Regression：微调破坏的案例** |
| 对 | 对 | Stable Correct |
| 错 | 错 | Remaining Failure |

然后重点人工检查：

# Gain Set

到底修复了什么？

例如：

```text
地域准入边界
资格条件
隐性歧视
理由结构
```

以及：

# Regression Set

又破坏了什么？

例如：

```text
正常履约条件被误报
未知情况过度自信
理由开始模板化
```

这两组案例是后续模型迭代最宝贵的数据。

---

# 十二、不要忘记 General Capability Regression

LoRA 虽然只训练少量参数，

也不代表：

> 原模型其他能力绝对不受影响。

所以还应该留一小组：

# Regression Suite

例如：

```text
普通中文问答
文本摘要
指令遵循
简单逻辑
基础信息抽取
```

不是为了证明模型：

> 什么都会。

而是检查：

> 微调有没有明显破坏原来应该保留的基础能力。

因此最终不是：

\[
ProcurementGain
\]

单独决定是否发布。

而是：

\[
\boxed{
ProcurementGain
-
UnacceptableRegression
}
\]

---

# 十三、正式验收不要只做一个“综合总分”

工程上我更建议：

# Release Gates
## 发布门槛

而不是随便设计：

```text
总分 = 0.37 × F1
     + 0.19 × 格式
     + 0.44 × 理由
```

最后变成一个：

> 82.73 分。

这种数字很漂亮，

但经常缺乏业务解释。

更清楚的方法是提前定义门槛，例如：

```text
风险Recall
必须达到预先规定目标

Hard Negative误报率
不得超过规定上限

Schema Compliance
必须达到规定水平

needs_review
不得出现明显塌缩

General Regression
不得超过允许范围
```

具体阈值：

> 应在看 Final Test 结果以前，根据业务需求确定。

否则看到成绩以后再改标准：

> 就失去评测意义了。

---

# 十四、最后一次正式评测流程

现在把整个验收流程压成一条线：

```text
冻结 Fine-tuned Candidate
        ↓
冻结 Base Revision
        ↓
冻结 Tokenizer / Template
        ↓
冻结 Generation Config
        ↓
冻结 ProcurementBenchmark_V0.1
        ↓
Base 跑完整 Test Set
        ↓
Fine-tuned 跑同一 Test Set
        ↓
自动计算
Precision / Recall / F1
Schema Compliance
Slice Metrics
        ↓
生成 Paired Difference
        ↓
人工盲审
Gain / Regression / Reason Quality
        ↓
General Regression Suite
        ↓
成本检查
Latency / VRAM / Artifact Size
        ↓
对照 Release Gates
        ↓
Release / Continue Iteration
```

这里有一个特别重要的原则：

> **Final Test 跑完以后，如果你根据错误案例继续改模型，就应该进入新的模型版本和新的评测周期。**

不要：

```text
看Test
↓
改模型
↓
再看同一个Test
↓
再改
```

无限循环。

否则：

> Test Set 会逐渐变成新的 Validation Set。

---

# 十五、最终报告应该长什么样？

第一版可以直接建立：

# `ProcurementModelComparisonReport_V0.1`

核心表格类似：

| 指标 | Base Model | ProcurementLM | Delta |
|---|---:|---:|---:|
| Risk Precision | … | … | … |
| Risk Recall | … | … | … |
| Risk F1 | … | … | … |
| Hard Positive Recall | … | … | … |
| Hard Negative FP Rate | … | … | … |
| Boundary Accuracy | … | … | … |
| needs_review 质量 | … | … | … |
| Schema Compliance | … | … | … |
| General Regression | … | … | … |
| Latency | … | … | … |
| Peak VRAM | … | … | … |

再附：

```text
Top Gains
Top Regressions
Remaining Failure Modes
```

这样我们得到的不是：

> “Fine-tuned 好像好一点。”

而是一份：

> **可以审计的行为变化报告。**

---

# 十六、第五课最终工程产物：`ProcurementLM_V0.1`

只有到现在，我们才有资格把模型正式叫：

# `ProcurementLM_V0.1`

它不是一个孤零零的模型文件。

完整版本应该包含：

```text
ProcurementLM_V0.1/
│
├── adapter/
│   └── Best LoRA Adapter
│
├── merged/
│   └── Merged Model（如果采用）
│
├── tokenizer/
│
├── generation_config/
│
├── benchmark/
│   ├── ProcurementBenchmark_V0.1
│   └── ComparisonReport_V0.1
│
├── manifests/
│   ├── training_run.json
│   └── release_manifest.json
│
└── documentation/
    └── known_limitations.md
```

这里最后一个文件非常重要：

# `known_limitations.md`

它应该明确记录：

```text
模型擅长什么

模型仍然容易错什么

哪些案例必须needs_review

哪些输入超出训练分布

当前Benchmark覆盖了什么

没有覆盖什么
```

成熟模型产品：

> 不只是说明能力，

还必须说明边界。

---

# 十七、把整个第五课压成一条完整链

现在回头看 14 个阶段：

```text
1  Chat Template / Loss Mask
           ↓
2  SFT到底训练什么
           ↓
3  Length / Truncation / Padding
           ↓
4  Packing
           ↓
5  Full FT vs PEFT
           ↓
6  LoRA核心原理
           ↓
7  Rank / Alpha / Dropout
           ↓
8  Target Modules
           ↓
9  QLoRA / NF4
           ↓
10 Training Memory
           ↓
11 真正训练
           ↓
12 Logging / Checkpoint
           ↓
13 Merge / Save / Inference
           ↓
14 Base vs Fine-tuned Benchmark
           ↓
     ProcurementLM_V0.1
```

这才是一次完整的：

# Model Adaptation Lifecycle
## 模型领域适配生命周期

不是：

```text
准备数据
↓
train()
↓
结束
```

---

# 十八、本阶段只需要最终记住 5 句话

> **第一，判断微调是否成功，不能看 Training Loss，而要在完全独立的 Test Benchmark 上，将 Base 和 Fine-tuned Model 在相同推理协议下进行公平对比。**

> **第二，政府采购评测不能只看总 Accuracy；Precision、Recall、False Positive、False Negative、Hard Positive、Hard Negative、Boundary Case 和 needs_review 都必须拆开看。**

> **第三，真正有解释力的是 Paired Evaluation：逐条检查 Base 错→Fine-tuned 对的 Gain，以及 Base 对→Fine-tuned 错的 Regression。**

> **第四，模型是否可以发布，不应由一个漂亮的综合分数临时决定，而应由事先定义好的业务 Release Gates、通用能力回归和系统成本共同决定。**

> **第五，`ProcurementLM_V0.1` 不是一份权重，而是模型权重、Adapter、Tokenizer、Chat Template、Generation Config、Benchmark、训练记录、Release Manifest 和已知能力边界共同构成的可复现产品。**

---

# 第五课最终核心心智模型

如果整堂课最后只能留下这一张图：

```text
                   高质量领域数据
                         │
                         ▼
                  SFT Training Signal
                         │
                         ▼
               LoRA / QLoRA Adaptation
                         │
                         ▼
                  Candidate Model
                         │
                         ▼
            ┌─────────────────────────┐
            │                         │
            ▼                         ▼
        Base Model               Fine-tuned Model
            │                         │
            └────────────┬────────────┘
                         ▼
                 SAME TEST PROTOCOL
                         │
                         ▼
            ProcurementBenchmark_V0.1
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
      Gains          Regressions     Cost / Stability
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                   Release Gates
                         │
                         ▼
                 ProcurementLM_V0.1
```

脑中最后只留一句：

> **微调的价值不是“模型参数变了”，而是它在独立、固定、可复现的业务测试上，证明自己改变了正确的行为，同时没有付出不可接受的回归代价。**

---

# 第五课完成

到这里：

\[
\boxed{
第五课：SFT + LoRA / QLoRA 微调
=
14/14
}
\]

最终交付物：

\[
\boxed{
ProcurementLM\_V0.1
}
\]

我们已经从：

> **“模型到底怎样被训练？”**

一路走到了：

> **“怎样真正改变一个开源大模型的行为，并证明这种改变值得发布？”**

第五课到这里正式闭环。




---

<!-- LESSON 05 STAGE 14 END -->

