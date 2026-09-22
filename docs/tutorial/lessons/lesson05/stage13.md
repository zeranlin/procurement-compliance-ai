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
