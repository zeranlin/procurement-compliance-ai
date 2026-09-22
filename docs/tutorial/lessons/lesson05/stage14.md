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
