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
