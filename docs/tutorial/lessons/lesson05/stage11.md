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
