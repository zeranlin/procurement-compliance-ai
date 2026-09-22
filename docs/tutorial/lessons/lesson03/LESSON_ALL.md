# 第三课：GPU 环境与第一个开源大模型

> **V2 教学增强版。** 共 10 个阶段；主要产物/主线：`开源模型与 GPU 实操`。  
> 核心心智模型前置、中文释义增强、详细正文完整保留。

---


<!-- LESSON 03 STAGE 01 START -->

# 第三课 · 第 1 阶段：CPU、GPU、内存、显存、CUDA
## 为什么“电脑很强”不等于“能跑大模型”？为什么“能跑模型”又不等于“能训练模型”？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Compute Capacity ≠ Memory Capacity。GPU 算得快，不代表显存一定装得下模型和上下文。**
2. **RAM ≠ VRAM。系统内存与 GPU 显存位置、带宽和用途不同，不能用硬盘/内存数字替代显存预算。**
3. **Inference ≠ Training。训练除了权重，还需要梯度、优化器状态和激活，因此显存需求通常远高于推理。**
4. **GPU Speed 依赖并行算子、数据搬运和 Kernel；不是所有工作都比 CPU 快。**
5. **“模型权重能装下”只是第一道门，真正可用还要给 KV Cache、Batch、Context 和运行时 Workspace 留余量。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `CPU` | CPU：负责通用控制、数据准备和部分算子 |
| `CUDA` | CUDA：NVIDIA GPU 通用并行计算平台与软件生态 |
| `LoRA` | LoRA：冻结大部分基座参数，只训练低秩增量矩阵 |
| `BF16` | BF16：保留较大指数范围的 16 位浮点，常用于大模型 |
| `QLoRA` | QLoRA：量化基座模型并训练 LoRA，以降低显存成本 |
| `VRAM` | 显存：GPU 上存放权重、激活和 KV Cache 等的高速内存 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Tokenizer` | 分词器：文本与 Token ID 之间的编码/解码组件 |
| `KV Cache` | KV 缓存：生成时缓存历史 Key/Value 以减少重复计算 |
| `PyTorch` | PyTorch：张量计算、自动求导和训练/推理框架 |
| `Driver` | 驱动：操作系统与 GPU 硬件之间的底层接口 |

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

这一阶段我会明显换一种讲法。

先不堆公式，也先不讲 CUDA 安装命令。我们先建立一张**脑内地图**。只要这张图真正形成，以后看到“24GB 显存”“8 张 GPU”“CUDA OOM”“14B 模型”“BF16”“QLoRA”，你都会知道它们在整套系统里的位置。

这一阶段真正需要带走 **5 个核心心智模型**：

\[
\boxed{
① CPU=总调度员
}
\]

\[
\boxed{
② GPU=大规模并行计算工厂
}
\]

\[
\boxed{
③ RAM=电脑的公共工作区
}
\]

\[
\boxed{
④ VRAM=GPU身边的高速工作台
}
\]

\[
\boxed{
\text{⑤ 能推理}\neq\text{能训练}
}
\]

先把这五根柱子立起来。

---

# 一、先看整台电脑：LLM 到底跑在哪里？

假设你下载了一个开源模型：

```text
Qwen / Llama / Mistral / DeepSeek ...
```

它最开始在哪里？

答案非常朴素：

> **硬盘。**

比如：

```text
SSD / HDD
    │
    │ 读取模型文件
    ▼
RAM（内存）
    │
    │ 把需要 GPU 计算的数据搬过去
    ▼
VRAM（显存）
    │
    │ GPU直接高速读取
    ▼
GPU
    │
    │ 矩阵计算
    ▼
模型输出
```

先把这张图记住：

```text
┌──────────┐
│ SSD/硬盘 │  ← 长期仓库
└────┬─────┘
     │
     ▼
┌──────────┐
│ RAM/内存 │  ← 电脑公共工作区
└────┬─────┘
     │
     ▼
┌──────────┐
│ VRAM显存 │  ← GPU高速工作台
└────┬─────┘
     │
     ▼
┌──────────┐
│   GPU    │  ← 大规模并行计算
└──────────┘
```

模型文件虽然“存在硬盘里”，但**硬盘里的模型不会自己计算**。

要真正运行：

> 必须把参数加载到计算设备能够高效读取的位置。

---

# 二、第一个核心心智模型：CPU 是总调度员

## 1. CPU 是什么？

CPU：

# Central Processing Unit

中央处理器。

日常电脑里的：

- Windows；
- 浏览器；
- Python；
- PDF 解析；
- 文件读写；
- 数据库程序；

大量工作首先都由 CPU 控制。

---

## 2. CPU 最大的优势不是“数量多”

而是：

> **单个核心非常灵活。**

CPU 很适合处理：

- 条件判断；
- 程序控制；
- 文件操作；
- 操作系统；
- 各种不同类型的逻辑任务。

---

## 3. 可以把 CPU 想成什么？

想象一个政府采购项目办公室。

CPU 像：

> **项目总负责人。**

他会：

- 接收文件；
- 判断下一步干什么；
- 调度各个部门；
- 发起任务；
- 管理程序流程。

---

## 4. 但是有一天你让这个负责人做什么？

你给他：

> 40 亿个乘法。

然后说：

> “一个一个帮我算。”

这就麻烦了。

---

# 三、GPU 为什么出现？

GPU：

# Graphics Processing Unit

图形处理器。

它最早的重要任务之一，就是：

> 计算大量像素。

---

## 5. 一张图有多少像素？

例如：

\[
3840\times2160
\]

也就是大约：

> 830 万个像素。

每一帧都要处理大量相似计算。

---

## 6. GPU 的设计哲学因此非常不一样

CPU 更像：

> 几个特别聪明、特别灵活的专家。

GPU 更像：

> **成千上万个可以同时干相似工作的工人。**

---

# 四、最重要的一张对比图

```text
CPU
━━━━━━━━━━━━━━━━━━━━━━
少量强力核心
│
├─ 工人A：处理文件
├─ 工人B：判断条件
├─ 工人C：运行系统
└─ 工人D：执行复杂程序

擅长：复杂、分支多、灵活任务


GPU
━━━━━━━━━━━━━━━━━━━━━━
大量并行计算单元
│
├─ 计算1
├─ 计算2
├─ 计算3
├─ 计算4
├─ ...
└─ 计算几万/几十万个

擅长：大量相似数学运算
```

这就是第一层直觉。

---

# 五、第二个核心心智模型

## GPU = 大规模并行计算工厂

不是简单：

\[
\boxed{
GPU比CPU快
}
\]

这句话太粗糙。

更准确的是：

\[
\boxed{
GPU特别擅长可以大量并行的数值计算
}
\]

有些工作：

> GPU 非常快。

有些工作：

> CPU 反而更合适。

---

# 六、为什么神经网络刚好特别适合 GPU？

第二课我们已经看到，大模型里面反复出现：

\[
XW
\]

\[
QK^T
\]

\[
AV
\]

\[
XW_{up}
\]

本质上大量都是：

> **矩阵乘法。**

先不管公式。

你只要把矩阵理解成：

> 一大堆数字排成表格。

---

## 7. 一个很小的矩阵

比如：

```text
1  2  3
4  5  6
```

真正的大模型可能是：

```text
4096 × 4096
```

甚至更大。

---

## 8. 一次矩阵乘法意味着什么？

里面有：

> 海量小乘法和加法。

而这些小计算中：

> 很多可以同时做。

这正好就是 GPU 喜欢的工作。

---

# 七、一个施工队类比

假设你有：

> 10 万块砖。

CPU 像：

> 8 个非常熟练的高级工人。

他们会干各种活。

GPU 像：

> 5000 个只负责搬砖和砌砖的工人。

如果任务是：

> 写采购方案、接电话、判断异常。

高级工人更合适。

但如果任务是：

> 把 10 万块砖同时搬到指定位置。

那 5000 个工人就很吓人了。

LLM 里的巨大矩阵计算：

> 很像后一种任务。

---

# 八、政府采购系统里 CPU 和 GPU 怎么分工？

假设用户上传：

> 一份 300 页政府采购招标文件。

整个系统可能大致是：

```text
PDF文件
   ↓
CPU
解析PDF
提取文本
解析表格
处理文件
   ↓
Tokenizer
文字变Token
   ↓
GPU
运行大语言模型
   ↓
CPU / GPU
后处理
   ↓
输出风险报告
```

所以：

\[
\boxed{
做AI系统
\neq
所有事情全部丢给GPU
}
\]

---

# 九、一个非常实用的 ProcurementAI 分工例子

| 工作 | 通常主要依赖 |
|---|---|
| 读取 PDF | CPU / RAM |
| 解压文件 | CPU |
| 解析 Word / HTML | CPU |
| 数据清洗 | CPU |
| Tokenization | 通常 CPU |
| 大模型 Forward | GPU |
| LoRA 训练 | GPU |
| 向量 Embedding | CPU 或 GPU |
| Vector Search | CPU/GPU 都可能 |
| 写 JSON 文件 | CPU |
| 数据库存取 | CPU / RAM / Storage |

所以以后不要产生一种印象：

> “AI 项目 = GPU 项目。”

更准确是：

\[
\boxed{
AI系统
=
CPU系统
+
内存
+
存储
+
GPU计算
+
软件栈
}
\]

---

# 十、现在进入 RAM：内存

RAM：

# Random Access Memory

我们日常说：

> 32GB 内存。

> 64GB 内存。

一般就是 RAM。

---

## 10. RAM 可以理解成什么？

还是用办公室类比。

硬盘：

> 档案仓库。

RAM：

> **办公室桌面。**

---

## 11. 为什么不能所有东西直接从硬盘操作？

因为硬盘：

> 相对慢。

工作时如果每看一行文件都跑去地下档案室取一次：

> 效率会非常差。

---

## 12. 所以电脑会把正在使用的东西放进 RAM

例如：

- Python 程序；
- 数据集；
- PDF 内容；
- 模型文件的一部分；
- 当前运行程序的数据。

---

# 十一、非常重要：硬盘容量 ≠ 内存容量

例如：

你的电脑：

```text
SSD：2TB
RAM：32GB
```

并不意味着：

> 你能同时在内存里放 2TB 数据。

---

## 13. 一个仓库可以很大

但桌子：

> 只有那么大。

这是非常好的心智模型。

\[
\boxed{
SSD=仓库
}
\]

\[
\boxed{
RAM=工作桌
}
\]

---

# 十二、那显存 VRAM 又是什么？

VRAM：

# Video Random Access Memory

简单说：

> GPU 自己旁边的高速内存。

---

## 14. 为什么 GPU 还要自己有一块内存？

因为 GPU 做计算特别快。

如果它每算一个数字：

> 都去很远的普通 RAM 取数据，

GPU 会经常：

> 等数据。

---

## 15. 所以需要把它正在大量使用的数据

放在 GPU 附近。

这个地方就是：

\[
\boxed{
VRAM
}
\]

显存。

---

# 十三、第三个与第四个心智模型

可以这样记：

```text
硬盘 SSD
= 仓库

RAM
= 总办公室工作桌

VRAM
= GPU车间里的高速工作台

GPU
= 车间工人
```

这四者关系非常重要。

---

# 十四、为什么大家买 GPU 总问“显存多少”？

因为大模型首先面临一个非常现实的问题：

> **模型装不装得进去？**

假设：

> GPU 很快。

但是显存只有：

\[
8GB
\]

而模型运行需要：

\[
20GB
\]

会发生什么？

---

## 16. 很简单

就像：

> 你有一个速度极快的厨师，

但厨房操作台：

> 只有 30 厘米宽。

菜、锅、原料：

> 根本摆不开。

厨师快也没有意义。

---

# 十五、所以 GPU 有两个完全不同的指标

以后看 GPU，不要只看：

> “性能强不强。”

至少要区分：

### 计算能力

GPU：

> 算得多快。

### 显存容量

VRAM：

> 能放多少东西。

---

## 17. 这两件事情不是一回事

一个 GPU：

> 算力强。

但显存：

> 小。

仍然可能：

> 装不下大模型。

---

# 十六、模型到底在显存里放什么？

我们先不展开复杂显存公式。

只看最重要的几个东西。

推理时，显存里通常至少需要考虑：

```text
┌────────────────────┐
│ 模型 Weights       │
├────────────────────┤
│ KV Cache           │
├────────────────────┤
│ Activations        │
├────────────────────┤
│ 临时计算空间       │
└────────────────────┘
```

---

## 18. 第一大块：Weights

也就是：

> 模型参数。

第二课里的：

\[
W_Q
\]

\[
W_K
\]

\[
W_V
\]

\[
W_O
\]

MLP Matrix 等等。

---

## 19. 模型写着 7B 是什么意思？

大致意味着：

\[
7B
=
70亿
\]

个 Parameter。

---

## 20. 每个参数都需要空间存储

先用一个非常粗的例子。

如果每个 Parameter 使用：

> 2 Bytes

那么：

\[
70亿\times2Bytes
\]

大约：

\[
14GB
\]

---

## 21. 这一阶段不用背公式

只记住这个直觉：

> **参数越多，每个参数用的字节越多，模型 Weight 就越占显存。**

后面第 6、7 阶段我们再真正拆：

- FP32；
- FP16；
- BF16；
- INT8；
- INT4；
- Quantization。


---

# 十七、一个非常重要的案例

假设你有：

# 16GB GPU

你下载一个：

# 7B BF16 模型

仅 Weight 就大约：

\[
14GB
\]

你可能想：

> “16GB > 14GB，那不是刚好吗？”

不一定。

---

## 22. 因为显存不只装 Weight

还需要：

- KV Cache；
- Temporary Buffer；
- Framework overhead；
- Activations。

所以：

> 14GB Weight 不意味着 16GB 卡一定舒服运行。

---

## 23. 这就是以后最常见的一句话

\[
\boxed{
模型权重大小
\neq
实际显存需求
}
\]

非常重要。

---

# 十八、什么是 OOM？

你以后一定会见到：

# CUDA Out Of Memory

简称：

# OOM

---

## 24. 它不一定意味着 GPU 坏了

通常只是：

> **显存装不下了。**

---

## 25. 就像桌子已经摆满

你还要再放一摞文件。

电脑说：

> 没地方了。

---

## 26. 常见原因可能包括

- 模型太大；
- Batch 太大；
- Context 太长；
- KV Cache 太大；
- Training Activation 太多；
- Precision 太高。

后面每一个我们都会单独拆。

---

# 十九、为什么 Context 越长也越吃显存？

假设：

> 用户只问一句话。

模型只需要记：

> 少量 Context。

---

## 27. 但如果输入一份

\[
100,000
\]

Token 的采购文件，

模型为了生成后续内容：

> 必须保存大量过去 Token 的 K/V 信息。

这就是：

# KV Cache

---

## 28. 可以把 KV Cache 想成什么？

模型在读长文件时：

> 不想每生成一个 Token，就把过去 10 万 Token 全部重新整理一次。

于是提前把一些中间结果：

> 存下来。

---

## 29. 很像会议秘书

已经整理过：

> 第 1～100 页笔记。

到了第 101 页：

> 不需要从第 1 页重新做全部笔记。

把过去笔记：

> 存着继续使用。

这就是 KV Cache 的第一层直觉。

---

# 二十、Context 长度增加时发生什么？

```text
短问题
↓
小 KV Cache


长文档
↓
大 KV Cache


超长文档
↓
更大的 KV Cache
↓
显存压力增加
```

所以：

\[
\boxed{
大模型显存问题
不只是参数量问题
}
\]

---

# 二十一、现在进入本阶段最重要的区别

# 推理 ≠ 训练

这是第三课必须建立的第五个核心心智模型。

---

# 二十二、什么叫推理 Inference？

你打开一个已经训练好的模型：

> 给它问题。

它：

> 给你答案。

例如：

> “审查以下资格条件是否存在潜在竞争限制。”

模型回答：

> 风险分析……

这叫：

# Inference

---

## 30. Inference 最核心的事情

主要是：

\[
\boxed{
Forward
}
\]

第二课第 4 阶段已经学过。

---

## 31. 它使用已经存在的 Weight

计算：

\[
Input
\rightarrow
Output
\]

---

## 32. Weight 通常不更新

也就是说：

```text
模型参数
   │
   │ 读取使用
   ▼
Forward
   ▼
答案
```

---

# 二十三、训练是什么？

Training：

> 模型答完以后，我们告诉它“答案错在哪里”。

然后：

\[
Forward
\]

↓

\[
Loss
\]

↓

\[
Backward
\]

↓

\[
Optimizer
\]

↓

\[
WeightUpdate
\]

---

## 33. 所以训练需要比推理更多东西

推理：

```text
Weights
+
当前计算
+
KV Cache
```

训练：

```text
Weights
+
Forward Activations
+
Gradients
+
Optimizer States
+
临时计算空间
```

---

# 二十四、用一个学生类比

## 推理

相当于：

> 已经毕业的学生参加考试。

需要：

- 大脑；
- 试卷；
- 草稿纸。

---

## 训练

相当于：

> 学生一边考试，一边老师逐题批改，还要保存错误记录、调整学习方法。

需要：

- 大脑；
- 试卷；
- 草稿纸；
- 批改记录；
- 错题本；
- 学习状态。

所以自然：

> 更占资源。

---

# 二十五、非常重要的一句话

\[
\boxed{
能把模型加载进GPU
\neq
能训练这个模型
}
\]

以后看到某人说：

> “我的 24GB 显卡可以跑 14B。”

不要立刻得出：

> “那就可以训练 14B。”

这两个问题：

> 完全不同。

---

# 二十六、一个很实际的例子

假设：

> 某个经过压缩/量化的 14B 模型能够塞进 24GB 显存并推理。

这并不意味着：

> 14B Full Fine-tuning 也能在 24GB 上完成。

---

## 34. 为什么？

Full Fine-tuning 需要额外保存：

- Gradient；
- Optimizer State；
- Activations。

显存需求：

> 会比纯推理大很多。

---

## 35. 那 LoRA 为什么有价值？

后面我们会详细学。

现在只需要有一个印象：

LoRA 的目的之一，就是：

> **减少真正需要训练和保存训练状态的参数。**

所以：

> 原本全量训练非常困难，

变成：

> 参数高效微调。

---

# 二十七、采购项目中的三个不同目标

以后买 GPU 前先问：

### A. 我只是要跑模型吗？

\[
Inference
\]

### B. 我要 LoRA / QLoRA 吗？

\[
ParameterEfficientFineTuning
\]

### C. 我要 Full Fine-tuning / CPT 吗？

\[
HeavyTraining
\]

---

## 36. 三种需求的硬件要求完全不同

所以：

\[
\boxed{
先定义任务
再选GPU
}
\]

而不是：

\[
先买GPU
再想干什么
\]

---

# 二十八、再认识 CUDA

现在才进入 CUDA。

CUDA：

# Compute Unified Device Architecture

由 NVIDIA 建立的一套 GPU 计算平台/软件生态。

---

## 37. 最重要的一个误区

\[
\boxed{
CUDA
\neq
GPU
}
\]

GPU 是：

> 硬件。

CUDA 是：

> 让软件能够利用 NVIDIA GPU 做通用计算的重要平台/软件栈。

---

# 二十九、还是用工厂类比

GPU：

> 工厂。

CUDA：

> **让程序能够指挥工厂干活的一套规则、工具和通道。**

---

## 38. 你的 Python 不会天然知道怎么让 GPU 算矩阵

需要：

> 软件层连接。

---

# 三十、PyTorch 又是什么？

PyTorch：

> 深度学习框架。

我们通常写：

```python
model(x)
```

而不是自己控制：

> 每一个 CUDA 核心。

---

## 39. PyTorch 帮我们做什么？

它帮你把：

```text
矩阵乘法
```

这样的高级操作，

转化成：

> GPU 可以高效执行的计算。

---

# 三十一、整个软件链第一次出现

以后你会经常看到这张图：

```text
你的 Python 代码
      ↓
   PyTorch
      ↓
 CUDA Runtime / Libraries
      ↓
 NVIDIA Driver
      ↓
 NVIDIA GPU
```

---

## 40. 这张图非常重要

因为以后你会遇到：

> “为什么我明明有 NVIDIA GPU，PyTorch 却检测不到？”

问题可能不在：

> GPU。

而在这条链上的其它地方。

---

# 三十二、第六个辅助心智模型

虽然本阶段只要求记 5 个核心模型，但这里送一个很实用的：

\[
\boxed{
Hardware
\rightarrow
Driver
\rightarrow
CUDA
\rightarrow
Framework
\rightarrow
Model
}
\]

其中任何一层出问题：

> 整个 GPU 计算链都可能不工作。

---

# 三十三、Driver 是什么？

Driver：

# 驱动程序

简单理解：

> 操作系统和 GPU 硬件之间的沟通层。

---

## 41. 没有合适 Driver

你的系统可能：

> 知道插了一块 GPU，

但很多 CUDA 工作：

> 不能正常进行。

---

# 三十四、CUDA Toolkit 又是什么？

你以后会看到：

```text
CUDA 12.x
CUDA Toolkit
nvcc
cuBLAS
cuDNN
```

现在先不要背。

---

## 42. 只需要知道

CUDA 生态里包含：

> 很多让 GPU 做高性能计算的组件。

例如矩阵计算库。

---

## 43. PyTorch 往往会调用这些底层能力

你不需要自己写：

> GPU 汇编代码。

---

# 三十五、为什么 AI 工程师经常被 CUDA 折磨？

因为：

> 软件版本必须兼容。

例如可能涉及：

```text
GPU型号
↓
Driver版本
↓
CUDA兼容性
↓
PyTorch版本
↓
Transformers版本
↓
模型实现
```

其中某个组合：

> 不兼容。

就可能报错。

---

# 三十六、但是这一阶段不要进入“版本地狱”

这一阶段只建立认知。

下一阶段：

<!-- LESSON 03 STAGE 01 END -->


<!-- LESSON 03 STAGE 02 START -->

# 第三课 · 第 2 阶段：Driver、CUDA、PyTorch 到底是什么关系？
## 为什么电脑里明明有 NVIDIA GPU，Python 却可能告诉你 `CUDA unavailable`？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Driver ≠ CUDA Toolkit ≠ PyTorch CUDA Build。三者是不同层级，必须分别确认版本与兼容性。**
2. **nvidia-smi 能看到 GPU ≠ PyTorch 一定能用 CUDA；它只能证明驱动层基本工作。**
3. **正确诊断顺序应从 Hardware/Driver → Python Environment → PyTorch Build → cuda.is_available() → Tensor/Model 实测。**
4. **Python Interpreter / Virtual Environment 也是环境链的一部分，同一机器不同环境可能安装完全不同的 PyTorch。**
5. **遇到 CUDA unavailable 时先定位断在哪一层，不要直接“全卸载重装”。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `CUDA` | CUDA：NVIDIA GPU 通用并行计算平台与软件生态 |
| `PyTorch` | PyTorch：张量计算、自动求导和训练/推理框架 |
| `Driver` | 驱动：操作系统与 GPU 硬件之间的底层接口 |
| `CPU` | CPU：负责通用控制、数据准备和部分算子 |
| `CUDA Toolkit` | CUDA 工具包：开发、编译和运行 CUDA 程序的工具与库 |
| `Transformer` | Transformer：以注意力和前馈网络为核心的序列架构 |
| `Transformers` | Transformers：Hugging Face 的模型加载与推理库 |
| `Memory` | 任务记忆：保存跨步骤需要复用的结构化信息 |
| `Attention` | 注意力：根据内容相关性动态聚合信息 |
| `Gradient` | 梯度：损失对参数变化方向和敏感度的局部信息 |
| `MLP` | MLP/前馈网络：对每个位置表示做非线性变换 |

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

这一阶段先不急着安装任何东西。

我们先把上一阶段留下的这条链真正看懂：

```text
你的 Python 程序
        ↓
      PyTorch
        ↓
 CUDA Runtime / CUDA Libraries
        ↓
   NVIDIA Driver
        ↓
    NVIDIA GPU
```

今天真正需要带走的不是一堆版本号，而是 **5 个核心心智模型**：

\[
\boxed{\text{① GPU 是硬件，Driver 是硬件的翻译官}}
\]

\[
\boxed{\text{② CUDA 是 GPU 计算生态，不等于显卡，也不等于 Driver}}
\]

\[
\boxed{\text{③ PyTorch 是我们真正编写深度学习程序的上层框架}}
\]

\[
\boxed{\text{④ 有 NVIDIA GPU，不代表 PyTorch 一定能使用它}}
\]

\[
\boxed{\text{⑤ 排查 GPU 环境，本质是在逐层检查一条调用链}}
\]

我们会用一个贯穿全阶段的采购 AI 场景：

> **你有一台服务器，准备运行 ProcurementLM。操作系统能看到显卡，但执行 `torch.cuda.is_available()` 返回 `False`。到底是哪一层出了问题？**

---

# 一、先看一张“六层楼”总图

把整套 GPU 软件环境想成一栋楼：

```text
┌───────────────────────────────┐
│ 第6层：你的 ProcurementAI 代码 │
│ model.generate(...)            │
├───────────────────────────────┤
│ 第5层：Transformers / vLLM      │
│ 模型加载、生成、推理框架         │
├───────────────────────────────┤
│ 第4层：PyTorch                  │
│ Tensor、矩阵乘法、Autograd       │
├───────────────────────────────┤
│ 第3层：CUDA Runtime / Libraries │
│ GPU计算库、矩阵计算实现           │
├───────────────────────────────┤
│ 第2层：NVIDIA Driver           │
│ 软件 ↔ GPU硬件通信              │
├───────────────────────────────┤
│ 第1层：NVIDIA GPU              │
│ 真正执行并行计算的硬件           │
└───────────────────────────────┘
```

以后环境出问题，不要第一反应就是：

> “CUDA 坏了。”

真正的问题是：

> **哪一层断了？**

这就是本阶段最重要的诊断方式。

---

# 二、先从最底层开始：GPU Hardware

## 1. GPU 是实体硬件

例如你机器里插着一张 NVIDIA GPU。

它有：

> GPU 芯片、显存、计算单元、PCIe 接口等。

它和 CPU、内存条、SSD 一样，是现实存在的硬件。

---

## 2. 但是 GPU 本身不会理解 Python

你写：

```python
x = torch.randn(1000, 1000)
```

GPU 不知道：

> `torch.randn` 是什么意思。

甚至操作系统也不能凭空知道：

> 该怎样向这块显卡发送命令。

所以硬件上面必须有：

# Driver

---

# 三、第一个核心心智模型：Driver 是“硬件翻译官”

## 3. Driver 到底在做什么？

可以把 GPU 想成一台进口大型工业设备。

它很强。

但电脑操作系统不能直接喊：

> “帮我做一个 4096×4096 的矩阵乘法。”

需要有一套接口：

> 告诉系统怎样识别 GPU、管理显存、提交任务、读取结果。

这套关键软件之一就是：

# NVIDIA Driver

---

## 4. 一个非常直观的类比

```text
Python程序
    ↓
“我要计算这个矩阵”
    ↓
软件系统
    ↓
NVIDIA Driver
    ↓
把请求翻译成GPU能够接受的命令
    ↓
GPU执行
```

所以：

\[
\boxed{
GPU=工厂
}
\]

\[
\boxed{
Driver=工厂的官方控制系统/翻译官
}
\]

---

## 5. 没有 Driver 会怎么样？

可能出现：

> 操作系统无法正确识别 GPU。

或者：

> 能看到某种显示设备，但无法用于 CUDA 计算。

---

# 四、你以后最常见的第一个检查：`nvidia-smi`

在 NVIDIA GPU 环境里，经常先运行：

```bash
nvidia-smi
```

它非常值得理解，而不是死记。

---

## 6. `nvidia-smi` 主要是在问什么？

粗略理解：

> “NVIDIA Driver 能不能正常和 GPU 对话？”

如果它能显示类似：

```text
GPU Name
Driver Version
Memory Usage
GPU Utilization
Processes
```

至少说明：

> GPU + NVIDIA Driver 这一层大体是通的。

---

## 7. 所以第一层诊断可以画成

```text
GPU
 ↑
Driver
 ↑
nvidia-smi
```

如果：

```bash
nvidia-smi
```

都失败，

通常还没必要先去怀疑：

> Transformers。

因为底层都还没通。

---

# 五、一个最容易误解的字段：`CUDA Version`

运行 `nvidia-smi` 时，你可能看到：

```text
Driver Version: ...
CUDA Version: ...
```

很多初学者马上认为：

> “太好了，我已经安装这个版本的 CUDA Toolkit。”

这个结论不一定对。

---

## 8. 这里显示的 CUDA Version 更接近什么？

更准确地理解：

> **当前 Driver 大致能够支持到什么 CUDA 兼容级别。**

它不自动证明：

> 你的电脑里安装了对应版本的完整 CUDA Toolkit。

---

## 9. 这一点非常重要

假设你看到：

```text
nvidia-smi
CUDA Version: 12.x
```

然后输入：

```bash
nvcc --version
```

却提示：

```text
command not found
```

这完全可能。

---

## 10. 为什么不矛盾？

因为：

```text
nvidia-smi
```

主要反映：

> Driver / GPU。

而：

```text
nvcc
```

属于：

> CUDA Toolkit 中的 CUDA 编译器。

这是两个不同层面。

---

# 六、第二个核心心智模型：CUDA 不是一个单一软件

很多初学者听到 CUDA，会以为：

> “CUDA 就是我安装的某个程序。”

实际上更适合把 CUDA 看成：

# NVIDIA GPU 通用计算生态

里面有很多东西。

---

## 11. 你可以先把 CUDA 想成“一整套高速公路系统”

GPU 是城市。

Driver 是：

> 进入城市的官方交通管理系统。

CUDA 生态则包含：

> 道路规则、高速公路、工具、数学库、开发工具。

---

## 12. 其中一个很重要的部分：CUDA Runtime

程序真正执行 GPU 计算时：

> 需要 CUDA Runtime 等组件帮助创建和运行 GPU 工作。

---

## 13. 还有很多 CUDA Libraries

例如做：

> 大规模矩阵乘法。

并不是 PyTorch 每次从头自己发明一个矩阵乘法算法。

底层通常会利用高度优化的 GPU 库。

---

## 14. 对 LLM 来说尤其重要

因为第二课已经知道：

```text
Q/K/V Projection
Attention
MLP
LM Head
```

大量核心计算都是：

> Matrix Multiplication。

所以底层高性能数学库非常关键。

---

# 七、CUDA Toolkit 又是什么？

CUDA Toolkit 可以粗略理解成：

> **给开发者使用的一整套 CUDA 开发工具。**

其中包括很多组件。

我们今天只抓住一个最容易见到的：

# `nvcc`

---

## 15. `nvcc` 是什么？

它是 NVIDIA CUDA Compiler。

如果你自己写 CUDA 程序，例如：

```text
my_kernel.cu
```

需要编译成 GPU 能执行的代码，

可能就会用：

```bash
nvcc
```

---

## 16. 但这里出现一个非常重要的现实问题

### 跑 PyTorch，一定必须自己安装完整 CUDA Toolkit 吗？

**不一定。**

这句话一定要记住。

---

# 八、这是很多教程最容易把人绕晕的地方

以前很多安装教程会让你：

```text
先装 Driver
再装 CUDA Toolkit
再装 cuDNN
再装 PyTorch
```

于是初学者形成了：

> “不用自己装完整 CUDA Toolkit，PyTorch 就绝对不能用 GPU。”

并不总是这样。

---

## 17. 现代 PyTorch 发行包通常会带上它所需要的一部分 CUDA Runtime / Libraries

也就是说，你可能：

> 没有系统级 `nvcc`。

但 PyTorch：

> 仍然能够正常使用 NVIDIA GPU。

---

## 18. 一个非常好用的类比

你去餐厅吃饭。

你需要：

> 厨房能做菜。

但你不一定需要：

> 自己拥有完整餐饮培训学校和厨师培训设备。

---

## 19. CUDA Toolkit 更像

> 完整开发工具箱。

而普通 PyTorch 用户很多时候只是：

> 使用已经打包好的 GPU 能力。

---

# 九、什么时候 CUDA Toolkit 会更重要？

例如你需要：

> 自己编译 CUDA Extension。

或者某些特殊库需要：

> 本地编译 CUDA Kernel。

这时：

```bash
nvcc
```

和本地 CUDA Toolkit 就更加重要。

---

## 20. 对我们 ProcurementLM 第一阶段来说

最开始：

> **不需要急着自己写 CUDA Kernel。**

我们的目标先是：

```text
PyTorch
↓
能识别GPU
↓
模型能运行
```

---

# 十、现在轮到 PyTorch

PyTorch 是什么？

很多人说：

> “PyTorch 是一个 AI 框架。”

这没错，但有点抽象。

---

## 21. 最简单的理解

PyTorch 给我们提供：

# Tensor + Neural Network + Autograd + GPU Operations

也就是说：

> 它把你和底层 CUDA 之间隔开。

---

## 22. 如果没有 PyTorch

你要训练一个模型，可能需要自己处理：

- GPU 内存；
- CUDA Kernel；
- Gradient；
- Matrix Operations；
- Device Management。

这会极其痛苦。

---

## 23. 有了 PyTorch

你可以写：

```python
x = torch.tensor([1, 2, 3])
```

---

## 24. 然后可以告诉它

> “把这个 Tensor 搬到 GPU。”

概念上：

```python
x = x.to("cuda")
```

---

## 25. 之后很多运算

PyTorch 会：

> 自动选择相应 CUDA 实现。

所以你写的是：

```python
y = x @ W
```

而不是：

> 亲自控制几千个 GPU 计算线程。

---

# 十一、第三个核心心智模型

\[
\boxed{
PyTorch
=
我们操作Tensor和神经网络的高级控制台
}
\]

而底层：

\[
\boxed{
PyTorch
\rightarrow
CUDA
\rightarrow
Driver
\rightarrow
GPU
}
\]

---

# 十二、为什么 Python 里可能出现 `CUDA unavailable`？

现在终于进入今天最核心的诊断问题。

假设：

```python
import torch

print(torch.cuda.is_available())
```

输出：

```text
False
```

它不等于：

> “你没有 GPU。”

---

## 26. 它真正表示什么？

粗略说：

> 当前这份 PyTorch 环境无法正常使用 CUDA GPU。

这中间有很多可能原因。

---

# 十三、案例一：电脑根本没有 NVIDIA GPU

这是最简单的。

```text
PyTorch
↓
寻找CUDA设备
↓
没有NVIDIA CUDA GPU
↓
False
```

---

# 十四、案例二：有 NVIDIA GPU，但 Driver 没有正常工作

机器硬件：

```text
有GPU
```

但是：

```bash
nvidia-smi
```

失败。

那问题大概率还在：

```text
GPU
↕
Driver
```

这一层。

---

# 十五、案例三：GPU 和 Driver 都正常，但装了 CPU 版 PyTorch

这是非常经典的坑。

---

## 27. 想象一下

底层 GPU：

> 完全正常。

Driver：

> 也正常。

但是你安装的 PyTorch：

> 本身没有 CUDA 支持。

那么：

```python
torch.cuda.is_available()
```

仍然可能是：

```text
False
```

---

## 28. 这说明

\[
\boxed{
有GPU
\neq
当前PyTorch支持GPU
}
\]

---

# 十六、把这个案例画出来

```text
NVIDIA GPU       ✅
    ↑
Driver           ✅
    ↑
PyTorch CPU版    ❌
    ↑
Python
```

系统仍然：

> 无法通过这份 PyTorch 使用 CUDA。

---

# 十七、案例四：Driver 太旧

假设你的 PyTorch 是按一个较新的 CUDA Runtime 构建的。

但机器 Driver：

> 太旧，无法支持它。

那么就可能出现：

> 兼容性问题。

---

## 29. 所以不是“版本号越新越好”

真正的问题是：

\[
\boxed{
Compatibility
}
\]

---

# 十八、第四个核心心智模型

### GPU 软件环境不是“装几个东西”，而是一条兼容性链

```text
GPU Hardware
       ↓
Driver Compatibility
       ↓
PyTorch CUDA Build
       ↓
Libraries
       ↓
Model
```

你以后排错：

> 不要乱卸载重装所有东西。

先确定：

> 哪一层不通。

---

# 十九、现在认识几个最重要的检查命令

这一阶段我们不执行，只理解它们分别在问谁。

| 检查 | 主要在看什么 | 如果失败，优先怀疑 |
|---|---|---|
| `nvidia-smi` | GPU + Driver | Driver / GPU |
| `nvcc --version` | 本地 CUDA Toolkit 编译器 | Toolkit 是否安装 |
| `torch.__version__` | PyTorch 版本 | 当前 Python 环境 |
| `torch.version.cuda` | 这份 PyTorch 对应的 CUDA 构建信息 | PyTorch CUDA Build |
| `torch.cuda.is_available()` | PyTorch 能否真正使用 CUDA | 整条 PyTorch→CUDA→Driver→GPU 链 |
| `torch.cuda.get_device_name(0)` | PyTorch 实际看到哪块 GPU | Device 识别 |

这是本阶段唯一值得保留的一张表。

---

# 二十、重点理解 `torch.version.cuda`

假设：

```python
print(torch.version.cuda)
```

输出类似：

```text
12.x
```

它更接近表示：

> 当前这份 PyTorch 是围绕某个 CUDA 版本构建/打包的。

---

## 30. 它不一定等于

```bash
nvcc --version
```

显示的系统 Toolkit 版本。

---

## 31. 更不一定等于

```bash
nvidia-smi
```

顶部的 CUDA Version。

这三个地方：

> 可能出现三个不同数字。

而且不一定有问题。

---

# 二十一、这是本阶段最容易产生的困惑

假设机器显示：

```text
nvidia-smi
CUDA Version: A
```

然后：

```text
nvcc --version
CUDA Toolkit: B
```

PyTorch：

```python
torch.version.cuda
```

显示：

```text
C
```

很多人看到：

\[
A\neq B\neq C
\]

立即认为：

> “环境彻底坏了。”

不一定。

---

# 二十二、为什么会有三个版本？

因为它们在回答三个不同问题。

```text
nvidia-smi
↓
Driver大概支持什么CUDA能力


nvcc
↓
系统安装的CUDA开发Toolkit是什么版本


torch.version.cuda
↓
当前PyTorch构建时使用/绑定的CUDA运行版本是什么
```

所以：

\[
\boxed{
名字里都有CUDA
\neq
它们是同一个东西
}
\]

---

# 二十三、一个医院类比

为了彻底消化这件事，我们不用电脑，换成医院。

GPU：

> CT 机器。

Driver：

> CT 机器官方控制软件。

CUDA Runtime：

> 让医学程序调用 CT 计算能力的运行接口。

CUDA Toolkit：

> 给设备研发工程师用的完整开发工具箱。

PyTorch：

> 医生使用的高级诊断软件。

Transformers：

> 某一种专门的智能诊断应用。

模型：

> 已经训练好的“专科知识”。

---

## 32. 你真正使用模型时

你通常不是直接：

> 拆开 CT 机器控制电路。

而是：

```text
医生
↓
诊断软件
↓
运行接口
↓
设备Driver
↓
CT设备
```

这就是我们日常使用 PyTorch GPU 的关系。

---

# 二十四、Transformers 又在哪一层？

Hugging Face Transformers 并不替代 PyTorch。

它是在更上层。

---

## 33. 例如你以后会写

```python
from transformers import AutoModelForCausalLM
```

---

## 34. Transformers 帮你处理

例如：

> 模型结构。

> Tokenizer。

> 模型权重加载。

> `generate()`。

---

## 35. 但真正 Tensor 计算

很多时候仍然通过：

# PyTorch

完成。

---

# 二十五、把整个 ProcurementLM 软件栈画完整

```text
你的采购AI应用
        │
        ▼
┌────────────────────┐
│ Transformers / vLLM │
│ 模型加载、推理       │
└─────────┬──────────┘
          ▼
┌────────────────────┐
│      PyTorch        │
│ Tensor / NN / GPU   │
└─────────┬──────────┘
          ▼
┌────────────────────┐
│ CUDA Runtime / Libs│
└─────────┬──────────┘
          ▼
┌────────────────────┐
│ NVIDIA Driver      │
└─────────┬──────────┘
          ▼
┌────────────────────┐
│ NVIDIA GPU + VRAM  │
└────────────────────┘
```

这张图应该成为你这一阶段最重要的长期记忆。

---

# 二十六、为什么虚拟环境也会制造问题？

假设你电脑上有：

```text
Python环境 A
Python环境 B
Python环境 C
```

---

## 36. 环境 A 可能装的是

> GPU 版 PyTorch。

---

## 37. 环境 B

可能装的是：

> CPU 版 PyTorch。

---

## 38. 你在终端测试环境 A

```python
torch.cuda.is_available()
```

得到：

```text
True
```

---

## 39. 但 Jupyter Notebook 实际使用环境 B

结果：

```text
False
```

---

## 40. 你可能开始怀疑

> Driver、CUDA、显卡。

其实真正问题只是：

> **你根本没在同一个 Python 环境里。**

---

# 二十七、这个坑为什么特别常见？

因为系统里可能同时有：

```text
Python
Conda
venv
Jupyter Kernel
IDE Interpreter
```

每一个都可能：

> 指向不同环境。

---

## 41. 所以以后诊断时还要问一句

\[
\boxed{
我现在运行的到底是哪一个Python？
}
\]

这句话极其重要。

---

# 二十八、一个真实风格的故障现场

假设工程师告诉你：

> “服务器 GPU 坏了，PyTorch 检测不到。”

你不要马上信。

应该按层查。

---

## 42. 第一步

运行：

```bash
nvidia-smi
```

结果：

```text
GPU 正常显示
```

说明：

> GPU + Driver 基本正常。

---

## 43. 第二步

Python：

```python
import torch
print(torch.__version__)
print(torch.version.cuda)
```

发现：

```text
torch.version.cuda = None
```

这就非常可疑。

---

## 44. 很可能是什么？

当前安装的是：

> CPU Build 的 PyTorch。

---

## 45. 所以根本无需

> 重装 GPU Driver。

问题发生在：

```text
PyTorch层
```

---

# 二十九、另一个故障案例

`nvidia-smi`：

```text
正常
```

PyTorch：

```text
有CUDA构建
```

但：

```python
torch.cuda.is_available()
```

仍异常。

这时候才进一步考虑：

> Driver compatibility、运行环境、设备权限、容器配置等。

---

# 三十、这就是第五个核心心智模型

### 环境排错 = 从下往上逐层验证，而不是乱重装

正确思路：

```text
1. GPU存在吗？
      ↓
2. Driver正常吗？
      ↓
3. 当前Python是谁？
      ↓
4. 当前PyTorch是什么Build？
      ↓
5. PyTorch能看到GPU吗？
      ↓
6. Tensor真的能放GPU吗？
      ↓
7. 模型能加载吗？
```

这条顺序以后会给你省非常多时间。

---

# 三十一、`torch.cuda.is_available()` 到底有多重要？

它是非常方便的：

> **快速总检查。**

但是它不是：

> 完整诊断报告。

---

## 46. `False`

只能说明：

> 当前 PyTorch CUDA 使用链不通。

不能单凭这一行判断：

> 是 GPU 坏了。

---

## 47. `True`

又说明什么？

至少说明：

> 当前 PyTorch 环境大体能够访问 CUDA GPU。

这是非常好的第一道门。

---

# 三十二、然后为什么还要 `get_device_name()`？

假设服务器有：

> 4 张 GPU。

PyTorch 需要知道：

> 它到底能看到哪些。

---

## 48. 例如：

```python
torch.cuda.device_count()
```

可以检查：

> PyTorch 看到多少 CUDA Device。

---

## 49. 然后：

```python
torch.cuda.get_device_name(0)
```

问的是：

> 第 0 号 GPU 到底叫什么。

---

# 三十三、GPU 编号 `cuda:0` 是什么？

如果机器有四张卡：

```text
GPU 0
GPU 1
GPU 2
GPU 3
```

PyTorch 中可能表示：

```text
cuda:0
cuda:1
cuda:2
cuda:3
```

---

## 50. 所以：

```python
model.to("cuda:0")
```

粗略意思是：

> 把模型搬到第 0 个可见 CUDA Device。

---

# 三十四、但注意一个工程坑

系统物理上的：

> “第 0 张卡”

和程序里：

> `cuda:0`

不一定永远指同一个物理设备。

---

## 51. 为什么？

因为可以使用：

```text
CUDA_VISIBLE_DEVICES
```

之类的环境机制重新定义：

> 哪些 GPU 对程序可见。

---

## 52. 例如物理上有

```text
GPU0
GPU1
GPU2
GPU3
```

程序只允许看到：

```text
GPU2
```

那么程序里的：

```text
cuda:0
```

可能实际就是：

> 物理 GPU2。

---

## 53. 现在不需要学习配置语法

只建立认知：

\[
\boxed{
PyTorchDeviceID
\neq
永远等于机箱物理编号
}
\]

---

# 三十五、为什么服务器经常这样做？

因为多人共享机器。

例如：

```text
研究员A → GPU0, GPU1
研究员B → GPU2
研究员C → GPU3
```

每个人程序里：

> 都可能看到自己的 `cuda:0`。

---

# 三十六、现在说一个很实用的概念：Device

PyTorch Tensor 不仅有：

> Shape、Dtype。

还拥有：

# Device

---

## 54. 例如

```text
Tensor A
device = cpu
```

---

## 55. Tensor B

```text
device = cuda:0
```

---

## 56. 这两个 Tensor

如果直接一起计算：

> 往往会报 Device Mismatch。

---

# 三十七、为什么？

因为一个数据：

> 在 CPU RAM。

另一个：

> 在 GPU VRAM。

它们物理上不在同一个计算设备。

---

## 57. 可以想象

你在东京办公室有一份文件。

同事在大阪工厂有另一份。

你不能直接说：

> “把这两张纸立即做矩阵乘法。”

先得：

> 搬到同一工作地点。

---

# 三十八、所以 `.to("cuda")` 真正发生了什么？

概念上：

```python
x = x.to("cuda")
```

不是一句魔法。

它实际上意味着：

> **把 Tensor 数据从 CPU Memory 搬到 GPU Memory。**

---

## 58. 这叫

# Host-to-Device Transfer

CPU 侧：

> Host。

GPU：

> Device。

---

# 三十九、把模型 `.to("cuda")` 又意味着什么？

模型内部有很多参数：

\[
W_Q,W_K,W_V,\ldots
\]

---

## 59. `model.to("cuda")`

本质上是在把这些 Parameter：

> 搬进 GPU 显存。

---

## 60. 所以又回到第三课第 1 阶段

如果模型太大：

> VRAM 装不下。

于是：

# OOM

---

# 四十、为什么 CPU → GPU 数据传输也有成本？

GPU 很快。

但是如果每一次计算都做：

```text
RAM
↓
VRAM
↓
RAM
↓
VRAM
```

大量来回搬运，

性能可能：

> 被数据传输拖慢。

---

## 61. 这就像一个超级工厂

每秒能加工：

> 一万件产品。

但运输卡车：

> 每分钟只送 10 件。

那么：

> 工厂大部分时间都在等货。

---

# 四十一、所以 GPU 利用率低不一定因为 GPU 太差

可能是：

> 数据没有及时送进去。

例如 ProcurementAI：

```text
PDF Parsing 太慢
↓
Tokenizer 太慢
↓
Batch 准备太慢
↓
GPU 等待
```

最终你看到：

```text
GPU utilization: 20%
```

---

## 62. 错误做法

> “再买更贵 GPU。”

---

## 63. 正确问题

> “GPU 为什么在等待？”

这就是系统思维。

---

# 四十二、CUDA 和 Apple GPU 是什么关系？

这也很值得提前知道。

CUDA：

> 是 NVIDIA 生态。

---

## 64. 如果电脑是 Apple Silicon

GPU 不是 NVIDIA。

所以通常不会走：

```text
CUDA
```

这条路线。

---

## 65. PyTorch 在 Apple 平台可以使用其它 Backend

例如：

# MPS

所以可能写：

```text
device = "mps"
```

而不是：

```text
cuda
```

---

## 66. 这再次说明

PyTorch：

> 是上层 Framework。

它下面可以有不同硬件 Backend。

概念上：

```text
                ┌─ CUDA → NVIDIA GPU
PyTorch ────────┼─ MPS → Apple GPU
                └─ CPU → CPU
```

---

# 四十三、CUDA 不是“所有 GPU 的统称”

这一点请彻底固定。

\[
\boxed{
CUDA
=
NVIDIA GPU计算生态
}
\]

不是：

\[
GPU的另一个名字
\]

---

# 四十四、为什么我们课程仍以 CUDA 为主？

因为目前大量：

- 大模型训练；
- 开源 LLM；
- PyTorch 高性能生态；
- 分布式训练；
- 推理框架；

围绕 NVIDIA CUDA 非常成熟。

所以学习 ProcurementLM：

> 掌握 CUDA 路线非常实用。

---

# 四十五、回到 ProcurementLM：一次模型加载经过哪些层？

假设以后我们执行：

```python
model = AutoModelForCausalLM.from_pretrained(...)
```

这背后不是：

> “Transformers 自己把答案算出来。”

而更接近：

```text
模型文件
   ↓
Transformers解析模型结构
   ↓
PyTorch创建Parameter Tensor
   ↓
Parameter进入RAM
   ↓
搬到VRAM
   ↓
PyTorch调用CUDA计算
   ↓
Driver提交GPU任务
   ↓
GPU执行Transformer
```

这张图非常关键。

---

# 四十六、如果模型加载成功但特别慢，怎么想？

不要第一反应只看：

> 模型本身。

先问：

```text
模型是不是其实跑在CPU？
```

---

## 67. 因为模型即使成功加载

也可能：

> 根本没有使用 GPU。

---

## 68. 于是你看到

```text
CPU 100%
GPU 0%
```

回答每个 Token：

> 慢得离谱。

---

## 69. 这时问题可能不是

> 模型太大。

而是：

> Device Placement 错了。

---

# 四十七、一个非常实用的诊断场景

你运行 ProcurementLM。

回答一句话用了：

> 3 分钟。

老板说：

> “模型不行。”

你应该先检查：

```text
GPU有没有被识别？
↓
模型是不是在cuda？
↓
GPU利用率是多少？
↓
显存用了多少？
```

再谈：

> 模型能力。

---

# 四十八、性能问题和模型质量问题是两回事

\[
\boxed{
SlowModel
\neq
BadModel
}
\]

---

## 70. 慢

可能是：

- CPU 推理；
- Device 搬运；
- GPU 吃不饱；
- Quantization 配置；
- 推理框架问题。

---

## 71. 回答错误

才更多属于：

> 模型质量 / 数据 / Prompt / RAG / Fine-tuning。

这是两个不同诊断方向。

---

# 四十九、一个很重要的环境原则：先最小化验证

不要一上来就：

> 下载 70B 模型。

---

## 72. 环境刚配好时

先做最小测试：

```text
PyTorch 能不能 import？
↓
CUDA 能不能识别？
↓
能不能创建GPU Tensor？
↓
小矩阵能不能计算？
↓
再加载小模型
↓
最后加载目标模型
```

---

# 五十、为什么这叫最小可验证路径？

因为如果直接：

```text
70B模型
+
Transformers
+
Quantization
+
FlashAttention
+
多GPU
+
vLLM
```

然后报错，

你不知道：

> 到底哪一层坏了。

---

## 73. 而最小化测试

每次只增加一个变量。

这其实就是第一课学过的：

\[
\boxed{
ControlledExperiment
}
\]

再次回来了。

---

# 五十一、环境搭建本身也是一个实验

假设：

```text
Step 1 Driver ✅
Step 2 PyTorch CUDA ✅
Step 3 Tensor GPU ✅
Step 4 Small Model ✅
Step 5 Large Model ❌
```

那么你已经知道：

> 问题大概率发生在模型规模/显存/模型依赖这一层。

---

## 74. 而不是 Driver

因为 Driver：

> 前面已经验证成功。

---

# 五十二、专业工程师和“乱试教程”的区别

初学者常见：

```text
报错
↓
Google一个帖子
↓
卸载CUDA
↓
换PyTorch
↓
换Python
↓
重装Driver
↓
又出现新错误
```

---

## 75. 专业思路

```text
建立系统层级
↓
定位失败层
↓
形成假设
↓
做最小实验
↓
验证
↓
只改一件事
```

---

## 76. 这就是第一课的方法论

\[
\boxed{
Hypothesis
\rightarrow
Experiment
\rightarrow
Measurement
\rightarrow
Diagnosis
}
\]

现在真的开始落地了。

---

# 五十三、第三课第 2 阶段的五个核心心智模型

| 心智模型 | 你应该真正理解的东西 |
|---|---|
| **① Driver = 硬件翻译官** | GPU 硬件必须通过 Driver 与操作系统和上层软件协作 |
| **② CUDA = NVIDIA GPU 计算生态** | CUDA 不等于 GPU，也不等于单独一个 Toolkit |
| **③ PyTorch = 高级 Tensor/神经网络控制层** | 我们通常通过 PyTorch 使用 CUDA，而不是直接操作 GPU |
| **④ GPU 可用性是一条兼容链** | GPU、Driver、PyTorch CUDA Build、运行环境任何一层都可能出错 |
| **⑤ Debug 要逐层验证** | `nvidia-smi → Python → PyTorch → CUDA → Tensor → Model`，不要乱重装 |

---

# 五十四、把整个阶段压成一幅“脑内地图”

```text
                         你写的ProcurementAI
                                  │
                                  ▼
                        Transformers / vLLM
                                  │
                                  ▼
                              PyTorch
                       Tensor / NN / Autograd
                                  │
                                  ▼
                         CUDA Runtime/Libraries
                                  │
                                  ▼
                           NVIDIA Driver
                                  │
                                  ▼
                       NVIDIA GPU + VRAM
```

如果上面任意一层断掉：

```text
模型
↓
可能无法使用GPU
```

---

# 五十五、再给你一个“故障定位图”

```text
nvidia-smi 失败
      │
      └── 优先看 GPU / Driver


nvidia-smi 正常
torch.cuda.is_available() = False
      │
      └── 看 Python环境 / PyTorch Build / Driver兼容


torch.cuda.is_available() = True
但模型很慢
      │
      └── 看 Device Placement / GPU利用率 / 数据流水线


模型加载时报 CUDA OOM
      │
      └── 看 VRAM / 模型大小 / Precision / Context / Batch
```

以后真遇到问题，这张图比“重装 CUDA”有用得多。

---

# 五十六、本阶段四个思维实验

### 思维实验 A

你的机器：

```text
nvidia-smi 正常
```

但：

```python
torch.cuda.is_available()
```

返回：

```text
False
```

能不能马上判断 GPU 坏了？

**不能。**

底层 GPU/Driver 反而已经有证据说明大体正常。

更应该查：

> 当前 Python 和 PyTorch。

---

### 思维实验 B

`nvidia-smi` 显示 CUDA 12.x，

但：

```bash
nvcc
```

不存在。

CUDA 环境一定坏了吗？

**不一定。**

这可能只是：

> Driver 支持 CUDA，但系统没安装完整 CUDA Toolkit。

PyTorch 仍可能正常 GPU 推理。

---

### 思维实验 C

PyTorch：

```python
torch.cuda.is_available()
```

是：

```text
True
```

模型却 100% 跑 CPU。

有没有可能？

**有。**

因为：

> PyTorch 能看到 GPU，不代表 Model 已经被放到 GPU。

---

### 思维实验 D

模型在 GPU，GPU 利用率只有 15%。

是不是应该买更贵的卡？

**先别买。**

很可能 GPU：

> 正在等 CPU、Tokenizer、磁盘或数据传输。

---

# 五十七、本阶段掌握标准

学完后，你应该可以用自己的话回答：

> GPU 与 CUDA 为什么不是同一个东西？

> Driver 在整个系统里到底起什么作用？

> `nvidia-smi` 主要检查哪一层？

> 为什么 `nvidia-smi` 里的 CUDA Version 不等于本机一定安装了同版本 CUDA Toolkit？

> `nvcc` 是什么？

> 为什么很多普通 PyTorch 用户没有 `nvcc` 也可能正常使用 GPU？

> PyTorch 与 CUDA 是什么关系？

> Transformers 与 PyTorch 又是什么关系？

> 为什么电脑有 NVIDIA GPU，`torch.cuda.is_available()` 仍可能是 `False`？

> CPU 版 PyTorch 是什么意思？

> 为什么三个“CUDA 版本号”可能不一样却仍然正常？

> `.to("cuda")` 从物理上大概发生了什么？

> 为什么 Tensor 和 Model 必须注意 Device？

> 为什么 GPU utilization 低不一定说明 GPU 太弱？

> 为什么环境排错应该自下而上，而不是全部重装？

如果这些你都能解释：

\[
\boxed{
第三课第2阶段真正掌握
}
\]

---

# 五十八、这一阶段真正只记一句话

\[
\boxed{
PyTorch并不是直接“看见”GPU，
它要通过一整条GPU软件栈去使用硬件；
环境排错的本质，就是找到这条链究竟断在哪一层。
}
\]

再压缩：

```text
GPU
↑
Driver
↑
CUDA
↑
PyTorch
↑
Transformers
↑
你的ProcurementAI
```

---

# 下一阶段：第三课 · 第 3 阶段
## 一个开源大模型下载下来后，文件夹里到底有什么？

下一阶段会开始真正接触一个模型目录，但仍然先讲“地图”，不先背文件名。

我们会把一个模型拆成三大件：

```text
模型文件夹
│
├── ① Architecture
│      config.json
│      ↓
│      “这个模型长什么样”
│
├── ② Tokenizer
│      tokenizer.json / vocab ...
│      ↓
│      “文字怎样变成Token”
│
└── ③ Weights
       model-*.safetensors
       ↓
       “这个模型到底学到了哪些参数”
```

到第三阶段结束，你看到 `config.json`、`tokenizer.json`、`generation_config.json`、`.safetensors`、Shard、Index 文件时，不再是一堆陌生文件，而会知道：

\[
\boxed{
模型
=
结构说明书
+
语言切分规则
+
真正学到的参数
}
\]

这一步一旦看懂，第四阶段的 `from_pretrained()` 就会非常自然。

---

<!-- LESSON 03 STAGE 02 END -->


<!-- LESSON 03 STAGE 03 START -->

# 第三课 · 第 3 阶段：一个开源大模型的文件夹里到底有什么？
## `config.json`、Tokenizer、`.safetensors`、Shard、Index 各自到底是什么？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **config.json 定义 Architecture Metadata，Tokenizer 定义 Text↔Token 协议，safetensors 保存真正的参数数值。**
2. **Model Weight ≠ Model Code。权重只是训练后的参数状态，模型结构仍需要代码和配置解释。**
3. **Shard 只是把大权重文件分箱保存，Index 记录参数在哪个 Shard；分片本身不改变模型能力。**
4. **一个可运行 Checkpoint 需要结构、权重、Tokenizer 和必要配置彼此匹配，不能随意混用不同仓库文件。**
5. **Generation Config / Chat Template 等文件影响推理协议，但它们与核心权重承担的职责不同。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Token` | Token：模型实际处理的离散文本单元 |
| `Tokenizer` | 分词器：文本与 Token ID 之间的编码/解码组件 |
| `Transformer` | Transformer：以注意力和前馈网络为核心的序列架构 |
| `Attention` | 注意力：根据内容相关性动态聚合信息 |
| `Embedding` | 嵌入：把离散 Token 映射到连续高维向量 |
| `MLP` | MLP/前馈网络：对每个位置表示做非线性变换 |
| `Transformers` | Transformers：Hugging Face 的模型加载与推理库 |
| `Block` | 版面块：文档解析后保留布局和位置的基本块 |
| `PyTorch` | PyTorch：张量计算、自动求导和训练/推理框架 |
| `Normalization` | 规范化：稳定中间激活与训练过程 |
| `RoPE` | RoPE：旋转位置编码，把位置信息融入注意力 |
| `Chat Template` | 对话模板：把角色消息转换成模型训练/推理序列 |

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

这一阶段我们继续坚持一个原则：

> **先看地图，后看文件名。**

不要一上来背：

```text
config.json
tokenizer.json
tokenizer_config.json
generation_config.json
model-00001-of-00004.safetensors
...
```

那样很快又会变成：

> 每个名字都见过，但不知道为什么存在。

今天我们真正只需要建立 **5 个核心心智模型**：

```text
① config = 模型结构说明书

② tokenizer = 模型与文字世界之间的翻译系统

③ weights = 模型训练后真正学到的数字

④ shard + index = 把巨大的权重仓库拆成多个箱子，再配一张货物地图

⑤ 一个“模型”不是单个文件，而是一套必须彼此匹配的资产
```

先把这五根柱子立起来。

---

# 一、先看一眼完整“模型包”

假设以后我们下载一个开源模型。

文件夹可能长这样：

```text
ProcurementBaseModel/
│
├── config.json
│
├── generation_config.json
│
│
├── tokenizer.json
├── tokenizer_config.json
├── special_tokens_map.json
│
├── model-00001-of-00004.safetensors
├── model-00002-of-00004.safetensors
├── model-00003-of-00004.safetensors
├── model-00004-of-00004.safetensors
├── model.safetensors.index.json
│
├── README.md
├── LICENSE
└── 其它可能文件...
```

第一次看确实像一地零件。

但只要换一种分类方式，马上简单很多：

```text
模型文件夹
│
├── A. 结构
│      └── config.json
│
├── B. 文字入口
│      ├── tokenizer.json
│      ├── tokenizer_config.json
│      └── special_tokens_map.json
│
├── C. 学到的参数
│      ├── *.safetensors
│      └── *.index.json
│
├── D. 默认生成设置
│      └── generation_config.json
│
└── E. 说明与附加资产
       ├── README.md
       ├── LICENSE
       └── 可能的模型代码
```

整个阶段实际上就在理解这五组东西。

---

# 二、核心心智模型 ①：`config.json` = 建筑蓝图

## 1. 先想一个采购办公楼

你拿到一张建筑蓝图。

上面写着：

```text
楼有多少层
每层多宽
有多少个房间
电梯有几部
楼梯在哪里
```

蓝图告诉你：

> **这栋楼应该长什么样。**

但蓝图本身：

> 不是办公楼。

---

## 2. `config.json` 就是类似的角色

它告诉软件：

> 这个神经网络到底应该搭成什么结构。

比如里面可能描述：

```text
模型类型
Hidden Size
Transformer Layer 数量
Attention Head 数量
KV Head 数量
Intermediate Size
Vocabulary Size
RoPE 参数
Normalization 类型
```

这些词我们第二课已经基本学过了。

---

## 3. 例如你可能看到类似概念

```json
{
  "hidden_size": 4096,
  "num_hidden_layers": 32,
  "num_attention_heads": 32,
  "num_key_value_heads": 8,
  "intermediate_size": 11008,
  "vocab_size": 100000
}
```

今天不用关心这些数字来自哪个真实模型。

重点是理解：

> **这不是模型学到的知识，而是在描述模型骨架。**

---

# 三、蓝图和“知识”不是一回事

## 4. 假设两栋办公楼

它们：

```text
都是 32 层
每层结构一样
房间数量一样
```

说明：

> 建筑结构相同。

---

## 5. 但第一栋里面

住的是：

> 政府采购专家。

第二栋里面：

> 医生。

它们能做的事情：

> 完全不同。

---

## 6. 对模型也是一样

两个模型可能拥有相同 Architecture：

```text
32 Layers
4096 Hidden Size
32 Attention Heads
```

但因为训练数据不同、参数不同：

> 能力可能完全不同。

---

## 7. 所以第一条非常重要

```text
Architecture
≠
Learned Knowledge
```

或者用最直观的话：

> **楼长得一样，不代表楼里的人会一样的东西。**

---

# 四、`config.json` 解决的是“怎么搭模型”

## 8. 假设 PyTorch 现在什么都不知道

你告诉它：

```text
我要加载一个大模型。
```

它首先得问：

> 我要创建多少 Transformer Block？

> 每层 Hidden Size 是多少？

> Attention 有几个 Head？

> MLP 中间层多宽？

---

## 9. 谁来回答？

通常就是：

> `config.json`

---

## 10. 所以加载模型的早期过程可以先想成

```text
config.json
     ↓
读取模型蓝图
     ↓
PyTorch / Transformers
     ↓
创建一个“空的模型骨架”
```

此时有：

> 结构。

但还没真正装入训练后的 Weight。

---

# 五、第二个核心心智模型：Weights = 模型真正学到的东西

## 11. 现在想象一个刚造好的大脑

神经网络结构已经搭好了：

```text
Embedding
↓
Transformer Block
↓
Transformer Block
↓
...
↓
LM Head
```

但里面所有参数如果还是：

> 随机数。

这个模型基本不会工作。

---

## 12. 为什么？

因为第二课我们知道：

模型的能力最终被训练写进：

```text
Wq
Wk
Wv
Wo
MLP weights
Embedding
...
```

大量参数里。

---

## 13. 训练真正改变的就是这些数字

例如最开始：

```text
0.0031
-0.021
0.0098
...
```

经过海量训练以后：

> 变成另一组数字。

单独看每个数字：

> 没什么人类可读含义。

但数十亿个数字共同工作：

> 就形成模型能力。

---

# 六、一个最重要的类比

`config.json`：

> **大脑结构图。**

Weights：

> **这个大脑经过学习以后形成的神经连接状态。**

所以：

```text
config
=
脑子长什么样

weights
=
脑子学成了什么样
```

---

# 七、为什么模型文件最大的通常是 Weight？

## 14. 假设一个 7B 模型

大约：

> 70 亿个参数。

而 `config.json`：

> 可能只是一个很小的文本文件。

---

## 15. 所以你可能看到

```text
config.json
几 KB

tokenizer.json
几 MB / 十几 MB

model weights
十几 GB
```

数量级完全不同。

---

## 16. 这很好理解

建筑蓝图：

> 几张纸。

真正的整栋办公楼：

> 巨大。

---

# 八、`.safetensors` 是什么？

接下来第一次认真认识：

```text
*.safetensors
```

---

## 17. 最简单理解

它是：

> **保存模型 Tensor / Weight 的一种文件格式。**

也就是说：

```text
model.safetensors
```

里面主要装：

> 大量参数 Tensor。

---

## 18. 为什么叫 Tensor？

第二课学过，一个 Weight Matrix 本身就是：

> Tensor。

例如：

```text
q_proj.weight
k_proj.weight
v_proj.weight
...
```

模型有成千上万个这样的参数对象。

---

## 19. `.safetensors` 就像什么？

可以想象一个超级仓库：

```text
safetensors
│
├── Layer 0 的参数
├── Layer 1 的参数
├── Layer 2 的参数
├── ...
├── MLP 参数
├── Attention 参数
├── Embedding
└── LM Head
```

当然真实文件内部不是这样给人看的目录结构。

这是帮助建立直觉。

---

# 九、为什么不是普通 `.txt`？

## 20. 因为模型参数可能有几十亿个数字

如果用普通文本：

```text
0.123456
-0.03381
...
```

会：

- 空间浪费巨大；
- 读取很慢；
- 类型信息难管理。

所以需要：

> 高效的二进制 Tensor 存储格式。

---

# 十、为什么现在经常看到 `safetensors`？

## 21. 一个重要原因

它设计时非常强调：

> 安全、高效地保存和读取 Tensor。

尤其是：

> 不需要像某些通用序列化机制那样在加载权重时执行任意 Python 对象逻辑。

---

## 22. 这里你先建立一个原则

从陌生来源下载模型时：

> **“模型文件也是软件供应链的一部分。”**

不要因为它叫“AI 模型”：

> 就默认任何文件都安全。

这个意识以后做政府采购生产系统会非常重要。

---

# 十一、为什么一个模型有四五个 `.safetensors`？

你可能看到：

```text
model-00001-of-00004.safetensors
model-00002-of-00004.safetensors
model-00003-of-00004.safetensors
model-00004-of-00004.safetensors
```

第一次看到很容易问：

> “我下载了四个模型吗？”

不是。

---

# 十二、核心心智模型 ③：Shard = 把一个巨大仓库拆成几个箱子

## 23. 想象你搬家

你有：

> 800 本政府采购资料。

不可能把所有东西塞进：

> 一个 200 公斤纸箱。

---

## 24. 所以你分成

```text
第1箱
第2箱
第3箱
第4箱
```

每个箱子里：

> 放一部分书。

---

## 25. 模型权重也一样

一个模型可能非常大。

于是将权重拆成：

# Shards

也就是：

> 权重分片。

---

## 26. 所以

```text
model-00001-of-00004
```

大致是在说：

> 这是总共 4 片中的第 1 片。

---

## 27. 四个文件加起来

才构成：

> 完整 Weight。

所以：

```text
4 shards
≠
4 models
```

而是：

```text
4 shards
=
1 model's weights
```

---

# 十三、为什么要拆？

主要有一些非常实际的工程理由：

- 单文件过大不方便管理；
- 上传下载更麻烦；
- 文件系统或托管平台可能有大小限制；
- 加载时可以更灵活处理。

---

# 十四、但是拆开以后出现一个新问题

假设现在有四个箱子：

```text
箱子 1
箱子 2
箱子 3
箱子 4
```

你需要找：

> “第 17 层的 `q_proj.weight` 在哪个箱子？”

怎么办？

---

# 十五、这时候 Index 出场了

可能看到：

```text
model.safetensors.index.json
```

---

## 28. 最简单理解

它就是：

> **权重分片地图。**

---

## 29. 类似仓库目录

```text
Embedding → 箱子1

Layer 0 → 箱子1

Layer 12 → 箱子2

Layer 23 → 箱子3

LM Head → 箱子4
```

真实 Index 更细：

> 会把具体 Parameter Name 映射到具体 Shard。

---

# 十六、第四个核心心智模型

```text
Shard
=
货箱

Index
=
货物清单 + 箱子位置地图
```

于是：

```text
model-00001-of-00004.safetensors
model-00002-of-00004.safetensors
...
             ↑
             │
model.safetensors.index.json
告诉加载器每个参数在哪
```

这就很好懂了。

---

# 十七、一个采购档案库类比

假设你有 20 万页采购文件。

档案室分成：

```text
A柜
B柜
C柜
D柜
```

然后有一张索引：

```text
项目2026-A023
→ C柜
→ 第4层
→ 文件盒17
```

---

## 30. Index 本身没有采购内容

它只是：

> 告诉你内容在哪。

同样：

> 权重 Index 本身不是模型知识。

---

# 十八、现在进入 Tokenizer 文件

第二课已经知道：

```text
原始文字
↓
Tokenizer
↓
Token IDs
```

所以一个模型只有 Weight：

> 还不够。

---

## 31. 举一个极端例子

模型训练时：

```text
“供应商”
→ Token ID 5172
```

---

## 32. 但你运行模型时使用另一个错误 Tokenizer

它把：

```text
“供应商”
→ Token ID 813
```

---

## 33. 发生什么？

模型的 Embedding 表里：

> 813 原本代表的是别的 Token。

于是整个输入：

> 从第一步就错位。

---

# 十九、所以 Tokenizer 不是附属品

它和 Weight 必须：

> 对得上。

可以把它理解成：

```text
Tokenizer
=
模型自己的字典 + 编码协议
```

---

# 二十、政府采购案例

假设一个采购专家系统里有内部编码：

```text
001 → 资格条件
002 → 技术参数
003 → 评分标准
```

然后某天你换了一本字典：

```text
001 → 合同条款
002 → 履约验收
003 → 供应商地址
```

---

## 34. 专家脑子没变

但输入编码：

> 全乱了。

结果自然乱套。

这就是 Tokenizer 和 Weight 必须配套的直觉。

---

# 二十一、`tokenizer.json` 是什么？

它通常承载：

> Tokenizer 的重要规则和数据。

具体内容取决于 Tokenizer 实现。

---

## 35. 里面可能涉及

- Vocabulary；
- 分词规则；
- Merge 规则；
- Normalization；
- Pre-tokenization；
- Decoder 等。

现在不需要进去读几万行 JSON。

---

## 36. 只需要记住

```text
tokenizer.json
↓
模型怎样把字符串变成Token
以及怎样把Token变回文本
```

---

# 二十二、`tokenizer_config.json` 又是什么？

名字很接近。

所以很容易混淆。

---

## 37. 可以先粗略区分

```text
tokenizer.json
=
Tokenizer本身的大量规则/词表资产

tokenizer_config.json
=
告诉Transformers如何使用这个Tokenizer的一些配置
```

---

## 38. 例如可能涉及

```text
Tokenizer class

最大长度信息

特殊 Token

Padding 行为

Chat Template
```

具体字段：

> 因模型而异。

---

# 二十三、什么是 Special Token？

普通 Token 代表：

> 文本内容。

但 LLM 往往还需要一些特殊控制符号。

例如概念上的：

```text
<BOS>
<EOS>
<PAD>
```

---

## 39. BOS

Beginning Of Sequence

可以理解：

> 序列开始。

---

## 40. EOS

End Of Sequence

可以理解：

> 序列结束。

---

## 41. PAD

Padding

用于：

> 批处理时把不同长度样本补到兼容长度。

---

# 二十四、Chat 模型还有更重要的一类特殊结构

例如一段对话：

```text
System:
你是政府采购审查助手

User:
审查以下资格条件……

Assistant:
……
```

模型并不一定直接看到：

> 我们屏幕上的漂亮聊天气泡。

---

## 42. 它真正看到的可能更像某种序列格式

概念上：

```text
<system>
你是政府采购审查助手
</system>

<user>
审查以下资格条件……
</user>

<assistant>
```

真实格式：

> 每个模型家族可能完全不同。

---

# 二十五、这就是 Chat Template

Chat Template 的作用可以粗略理解成：

> **把“角色化对话”转换成模型训练时熟悉的 Token 序列格式。**

---

## 43. 这是一个非常重要的东西

两个模型都支持聊天：

> 并不意味着它们的 Chat Template 相同。

---

## 44. 如果用错 Template

可能出现：

- 回答质量下降；
- 模型不知道该继续谁的话；
- 特殊 Token 错误；
- 输出格式奇怪；
- 重复生成。

---

# 二十六、核心心智模型 ④：Tokenizer 不只负责“切词”

对于 Chat LLM，它还可能参与：

```text
文字切分
+
Token ID映射
+
特殊Token
+
对话格式
```

所以千万不要把 Tokenizer 理解成：

> 一个简单的中文分词器。

---

# 二十七、`special_tokens_map.json`

有些模型目录中可能看到：

```text
special_tokens_map.json
```

它可以用于描述：

> 哪些 Token 扮演 BOS、EOS、PAD 等特殊角色。

---

## 45. 但不同模型仓库

文件组织方式可能：

> 不完全一样。

有些信息可能写在其它 Tokenizer 配置里。

所以以后不要背：

> “每个模型一定必须有这 7 个文件。”

---

# 二十八、这是今天非常重要的一个习惯

不要学习：

```text
固定文件清单
```

而要学习：

```text
每一种功能需要什么资产
```

比如：

```text
Architecture information
Tokenizer assets
Weights
Generation defaults
Metadata / code
```

具体文件名：

> 可以变化。

---

# 二十九、`generation_config.json` 是什么？

现在看另一个常见文件：

```text
generation_config.json
```

---

## 46. 很多人看到它会误以为

> “这是不是模型能力参数？”

不是。

它更接近：

> **生成时的默认驾驶设置。**

---

# 三十、还是用汽车类比

模型 Weight：

> 汽车本身。

`generation_config`：

> 默认驾驶方式。

---

## 47. 比如可能涉及

```text
max_new_tokens
temperature
top_p
do_sample
eos_token_id
```

具体字段依模型和配置而异。

---

## 48. 修改它意味着什么？

可能改变：

> 模型如何从 Logits 选择 Token。

但不会因此：

> 把 7B 模型变成 70B。

也不会让它：

> 突然学会没训练过的法规。

---

# 三十一、所以要牢牢记住

```text
Model Capability
≠
Generation Policy
```

比如：

> Temperature 调低，

可以让输出：

> 更稳定。

但不能保证：

> 法规依据就变正确。

---

# 三十二、采购系统中的例子

同一个模型面对：

> “请给出该资格条款的风险判断。”

生成设置 A：

```text
低随机性
```

可能每次比较稳定。

---

## 49. 设置 B

```text
高随机性
```

可能措辞更丰富。

但底层：

> 还是同一套 Weight。

---

# 三十三、那么 README 是干什么的？

很多模型仓库会有：

```text
README.md
```

或者页面上的：

# Model Card

---

## 50. 它不参与神经网络 Forward

但对工程师：

> 非常重要。

---

## 51. 因为它可能告诉你

- 模型是什么；
- 谁发布；
- 用途；
- License；
- Context Length；
- 推荐推理方式；
- Chat Template；
- 已知限制；
- 训练信息；
- 使用示例。

---

# 三十四、为什么政府采购项目尤其不能跳过 README / License？

因为你不只是：

> 自己玩一个模型。

以后可能是：

> 企业产品。

---

## 52. 所以必须问

```text
可以商用吗？

允许修改吗？

允许再发布吗？

有没有使用限制？

有没有归属/通知要求？
```

这些属于：

> 模型选型的一部分。

---

# 三十五、第五个核心心智模型

### 一个开源模型不是“一个 Weight 文件”，而是一套版本必须彼此匹配的资产

```text
Architecture
+
Tokenizer
+
Weights
+
Generation Settings
+
Metadata / License
+
有时还有Model Code
```

---

# 三十六、为什么“版本匹配”这么重要？

想象你有：

```text
A车型发动机
+
B车型变速箱
+
C车型控制软件
```

虽然每一个零件：

> 都是好东西。

但拼起来：

> 不一定能工作。

---

## 53. LLM 也是一样

例如：

```text
Model A 的 Weight
+
Model B 的 Tokenizer
```

可能：

> 完全错误。

---

## 54. 或者

```text
新版本 config
+
旧版本 weight
```

也可能：

> Shape 对不上。

---

# 三十七、Shape 对不上是什么意思？

假设 `config.json` 告诉程序：

```text
Hidden Size = 4096
```

于是模型创建：

```text
4096 × 4096
```

某个 Weight Matrix。

---

## 55. 但实际 Weight 文件里

这个参数是：

```text
5120 × 5120
```

加载时软件就会发现：

> “这块零件塞不进去。”

这类问题会表现成：

> Weight Shape Mismatch。

---

# 三十八、所以 `config` 和 Weight 必须一致

可以记成：

```text
config
=
模具尺寸

weight
=
真正要塞进模具里的零件
```

尺寸不同：

> 装不进去。

---

# 三十九、Tokenizer 错了为什么有时反而“不报错”？

这个问题更危险。

---

## 56. 因为某些情况下

错误 Tokenizer 仍然能输出：

> 合法整数 Token ID。

模型也能运行。

所以程序：

> 可能不崩。

---

## 57. 但是语义已经错了

这比直接报错更麻烦。

因为：

```text
程序正常运行
≠
模型输入正确
```

---

# 四十、这和第一课里的 Silent Failure 很像

显式报错：

> 反而容易发现。

最危险的是：

> 程序看起来正常，结果悄悄变差。

---

# 四十一、什么叫 Weight Name？

以后如果你查看模型，会看到类似：

```text
model.layers.0.self_attn.q_proj.weight

model.layers.0.self_attn.k_proj.weight

model.layers.0.mlp.gate_proj.weight
```

---

## 58. 现在这些名字已经不再陌生

第二课学过：

```text
Layer 0

Self Attention

Q Projection

K Projection

MLP Gate Projection
```

---

## 59. 所以 Weight 文件不是神秘黑盒

它里面实际上是在保存：

> 第二课那些 Matrix 的训练后数值。

这一刻第二课和第三课就真正接上了。

---

# 四十二、一个很重要的“第二课 → 第三课”映射

```text
第二课理论                 第三课文件

Hidden Size         ←→     config.json

Layer Count         ←→     config.json

Attention Heads     ←→     config.json

Tokenizer           ←→     tokenizer assets

Wq / Wk / Wv        ←→     safetensors

MLP weights         ←→     safetensors

LM Head             ←→     safetensors

Sampling            ←→     generation_config
```

以后你看到模型目录：

> 不再只是在看文件。

你是在看到：

> 第二课理论的实体化版本。

---

# 四十三、为什么模型仓库可能还有 Python 文件？

有些模型架构：

> Transformers 内置就认识。

例如加载时根据：

```text
model_type
```

可以直接找到对应实现。

---

## 60. 但某些模型可能带有

```text
modeling_xxx.py
configuration_xxx.py
```

之类的自定义代码。

这意味着：

> 模型可能需要仓库里的代码定义某些结构。

---

# 四十四、这时会遇到一个关键词

```text
trust_remote_code
```

以后有些教程会直接写：

```python
trust_remote_code=True
```

然后一句解释都没有。

这种习惯不好。

---

## 61. 它真正意味着什么？

粗略说：

> 允许加载并执行模型仓库提供的自定义代码。

---

## 62. 所以为什么要谨慎？

因为：

> Weight 数据和可执行 Python Code 是两类完全不同的安全风险。

你不应该对任何陌生仓库：

> 无脑信任远程代码。

---

# 四十五、政府采购 AI 尤其需要软件供应链意识

未来我们的系统可能处理：

- 采购文件；
- 企业信息；
- 内部审查材料；
- 专家意见。

---

## 63. 因此模型来源要有治理

至少应该知道：

```text
模型从哪里下载？

哪个版本？

Hash / Revision 是什么？

License 是什么？

有没有Remote Code？

有没有经过安全审查？
```

这不是“运维小事”。

是：

> 生产 AI 治理的一部分。

---

# 四十六、什么叫 Revision？

模型仓库也会更新。

今天的模型：

```text
Version A
```

一个月后作者可能：

> 更新 Tokenizer、Config 或 Weight。

---

## 64. 如果你永远只写

```text
下载最新版本
```

那么半年后：

> 你的实验可能无法复现。

---

## 65. 所以专业实验需要记录

```text
Model ID
+
Revision / Commit
+
Tokenizer Version
+
Framework Version
```

这正是第一课：

# Reproducibility

真正落地。

---

# 四十七、不要把模型名字当成完整版本

例如：

```text
SomeModel-7B-Instruct
```

只是：

> 人类可读名字。

---

## 66. 真正的实验身份应该更严格

概念上：

```text
Model:
SomeModel-7B-Instruct

Revision:
abc123...

Tokenizer:
same revision

Transformers:
某版本

PyTorch:
某版本
```

---

# 四十八、Base 和 Instruct 有什么区别？

以后经常看到：

```text
Model-7B-Base

Model-7B-Instruct
```

---

## 67. Base

通常更接近：

> 经过预训练的基础语言模型。

它主要学：

> Next-token Prediction。

---

## 68. Instruct

通常又经过：

> Instruction Tuning / Post-training。

因此更擅长：

> 遵循用户指令、对话。

---

# 四十九、是不是 Instruct 一定比 Base 强？

不能这么说。

---

## 69. 对聊天任务

Instruct：

> 通常更方便。

---

## 70. 但如果我们要做某种 Continued Pretraining

或者特殊训练路线，

Base：

> 可能有不同价值。

---

## 71. 所以又回到第一课

```text
没有“最强模型”
只有“适合什么任务的模型”
```

---

# 五十、一个 ProcurementLM 选型例子

假设我们未来有两个候选：

```text
7B Base
7B Instruct
```

---

## 72. 如果目标是

> 马上建立采购问答 Baseline。

通常：

> Instruct 更方便直接测试。

---

## 73. 如果目标是

> 大规模采购领域 Continued Pretraining。

Base 和 Instruct：

> 都需要更仔细评估训练路线。

不能仅凭名字决定。

---

# 五十一、模型目录里还有什么可能出现？

不同模型可能还包括：

```text
merges.txt
vocab.json
tokenizer.model
added_tokens.json
chat_template...
preprocessor...
```

等等。

---

## 74. 不用慌

不要问：

> “为什么我的模型没有和教程一模一样的文件？”

先问：

> **这些功能由哪个文件承担？**

---

# 五十二、今天的“功能视角”比“文件名视角”重要

你真正应该看的是：

| 功能 | 典型资产 |
|---|---|
| 模型长什么样 | `config.json` |
| 文字如何变 Token | Tokenizer 文件 |
| 模型学到的参数 | `.safetensors` 等 Weight |
| Weight 在哪些分片 | `*.index.json` |
| 默认怎样生成 | `generation_config.json` |
| 如何使用/限制 | README / Model Card |
| 是否有自定义实现 | 可能的 Python 代码 |

具体文件：

> 可以因模型而异。

---

# 五十三、我们用一个“采购专家公司”把所有文件串起来

想象你买下一家政府采购咨询公司。

你拿到了五类资产。

---

## 75. 第一类：组织架构图

```text
config.json
```

告诉你：

> 公司有多少部门、多少层级。

---

## 76. 第二类：内部术语字典

```text
Tokenizer
```

告诉你：

> 公司怎样编码和理解文字输入。

---

## 77. 第三类：专家真正的大脑和经验

```text
Weights
```

这是：

> 最值钱的部分。

---

## 78. 第四类：档案箱目录

```text
Shard + Index
```

告诉系统：

> 哪部分知识参数装在哪个文件。

---

## 79. 第五类：默认工作习惯

```text
generation_config
```

例如：

> 回答偏保守还是偏随机、何时停止等默认设置。

---

## 80. 第六类：员工手册和许可证

```text
README
LICENSE
Model Card
```

告诉你：

> 应该怎么使用、有哪些限制、是否合法部署。

这就是完整模型仓库。

---

# 五十四、再看一遍模型文件夹，现在感觉应该完全不同

```text
ProcurementBaseModel/
│
├── config.json
│      └─ 模型骨架
│
├── tokenizer...
│      └─ 语言入口
│
├── model-00001-of-00004.safetensors
├── model-00002-of-00004.safetensors
├── model-00003-of-00004.safetensors
├── model-00004-of-00004.safetensors
│      └─ 真正训练后的参数
│
├── model.safetensors.index.json
│      └─ 权重分片地图
│
├── generation_config.json
│      └─ 默认生成设置
│
└── README / LICENSE
       └─ 使用说明与治理信息
```

这时候它已经不再是一堆陌生文件。

---

# 五十五、接下来做一个完整加载思维实验

假设我们执行：

```python
AutoModelForCausalLM.from_pretrained(...)
```

先别管代码。

想象程序要完成什么。

---

## 81. 第一步：找到模型仓库

```text
模型在哪里？
```

本地目录？

远程模型仓库？

---

## 82. 第二步：读取 `config`

回答：

```text
我要搭一个什么神经网络？
```

---

## 83. 第三步：建立模型骨架

例如：

```text
Embedding
+
32个Decoder Block
+
Final Norm
+
LM Head
```

---

## 84. 第四步：读取 Weight Index

如果有 Shard：

> 先知道每个 Parameter 在哪个文件。

---

## 85. 第五步：读取 `.safetensors`

把真正的 Weight：

> 填入对应 Parameter。

---

## 86. 第六步：处理 Device / Precision

例如：

> CPU？

> GPU？

> BF16？

后面第 4、6、7 阶段会展开。

---

## 87. 与此同时 Tokenizer 单独加载

它负责：

```text
Text
→
Token IDs
```

---

# 五十六、整个过程画成一张图

```text
                 模型目录
                    │
        ┌───────────┼────────────┐
        │           │            │
        ▼           ▼            ▼
   config.json   tokenizer    safetensors
        │           │            │
        │           │            │
        ▼           ▼            ▼
   创建模型骨架   建立文字入口   装入训练参数
        │                        │
        └───────────┬────────────┘
                    ▼
              可运行的模型
                    │
                    ▲
                    │
             generation config
             控制默认生成策略
```

这就是本阶段最重要的一张总图。

---

# 五十七、现在回到第三课第 1 阶段

模型文件最开始：

> 在 SSD。

---

## 88. 当真正加载时

会发生类似：

```text
SSD
↓
RAM
↓
创建 Tensor
↓
VRAM
↓
GPU
```

---

## 89. 所以“模型文件夹”和“运行中的模型”不是同一个东西

磁盘上的：

```text
model.safetensors
```

是：

> 静态文件。

---

## 90. 运行中的 Model

是：

> RAM / VRAM 中已经创建好的 Tensor 和网络对象。

这个区别非常重要。

---

# 五十八、一个容易犯的错误

有人看模型文件夹：

```text
总大小 14GB
```

就说：

> “这个模型运行只需要 14GB。”

第三课第 1 阶段已经知道：

> 错。

---

## 91. 磁盘大小只是一个信息

实际运行还受：

- 保存格式；
- Dtype；
- Device；
- KV Cache；
- Context；
- Buffer；

影响。

---

# 五十九、模型文件也可能被量化

以后你还会看到：

```text
FP16 model
BF16 model
INT8 model
4-bit model
GGUF...
```

这些不仅影响：

> 文件大小。

也可能影响：

> 加载方式、运行框架、显存和精度。

---

## 92. 但今天先不要展开

第三课第 6 阶段会专门讲：

> **一个数字到底为什么可以占 4 Bytes、2 Bytes、1 Byte 甚至更少。**

---

# 六十、这阶段真正的 5 个核心心智模型

## ① `config` = 蓝图

它回答：

> **模型长什么样？**

不是：

> 模型学会了什么。

---

## ② Tokenizer = 语言接口

它回答：

> **文字怎样变成模型认识的 Token ID？**

对于 Chat Model：

> 还可能管理特殊 Token 和 Chat Template。

---

## ③ Weights = 真正训练成果

`.safetensors` 中的大量 Parameter：

> 才是训练以后形成的数值状态。

---

## ④ Shard + Index = 分箱 + 地图

```text
Shard
=
装参数的箱子

Index
=
哪个参数在哪个箱子的目录
```

---

## ⑤ Model = 一套彼此匹配的资产

不是：

```text
一个神秘的大文件
```

而是：

```text
Architecture
+
Tokenizer
+
Weights
+
Generation Configuration
+
Metadata / Code / License
```

---

# 六十一、最重要的三个区分

请把下面三组彻底分开。

### 第一组

```text
config
≠
weights
```

一个是：

> 结构。

一个是：

> 学习结果。

---

### 第二组

```text
tokenizer
≠
model weights
```

一个是：

> 文字编码规则。

一个是：

> 神经网络参数。

---

### 第三组

```text
generation config
≠
model capability
```

一个主要影响：

> 怎样从输出分布选择 Token。

另一个决定：

> 模型能形成什么分布。

---

# 六十二、政府采购模型的故障思维实验 A

你加载模型以后：

> 输出全是奇怪乱码或极不自然内容。

第一反应是不是一定要重训模型？

**不是。**

先检查：

> Tokenizer 是否正确匹配。

这是一个典型：

```text
Input Interface Failure
```

---

# 六十三、思维实验 B

加载模型时报：

```text
size mismatch
```

最值得优先想到什么？

> `config` 描述的网络 Shape 与实际 Weight 可能不匹配。

不是马上说：

> GPU 坏了。

---

# 六十四、思维实验 C

模型目录中有：

```text
model-00001-of-00008.safetensors
...
model-00008-of-00008.safetensors
```

是不是 8 个模型？

**不是。**

是：

> 一个模型的 8 个 Weight Shard。

---

# 六十五、思维实验 D

你把 Temperature 从 0.2 改到 0.8。

模型 Weight 有没有重新训练？

**没有。**

改变的是：

> Decode / Sampling Policy。

---

# 六十六、思维实验 E

你只有 `.safetensors` Weight，却完全不知道模型结构。

能不能天然知道应该如何连接所有 Matrix？

**不能简单这样假设。**

需要：

> Architecture / Config 等信息告诉软件如何解释这些 Weight。

---

# 六十七、本阶段掌握测试

如果你现在能够不用看前文，自己回答这些问题，第 3 阶段就算真正掌握：

> 一个“开源模型”为什么不是单个文件？

> `config.json` 解决的到底是什么问题？

> 为什么相同 Architecture 的两个模型能力可以完全不同？

> Weight 到底是什么？

> `.safetensors` 主要保存什么？

> 为什么大模型 Weight 会拆成多个 Shard？

> `model.safetensors.index.json` 为什么存在？

> Tokenizer 为什么必须和 Weight 匹配？

> `tokenizer.json` 和 `tokenizer_config.json` 从功能上怎么理解？

> Special Token 是干什么的？

> Chat Template 为什么会影响 Chat Model？

> `generation_config.json` 修改的是模型能力还是生成策略？

> 为什么 README / License 在企业模型选型中很重要？

> `trust_remote_code=True` 为什么不能无脑加？

> 为什么要固定 Model Revision？

> Base 与 Instruct 至少在训练阶段上有什么概念区别？

> 模型磁盘文件大小为什么不等于最终 VRAM 需求？

如果这些都能解释：

```text
第三课第3阶段
=
真正掌握
```

---

# 六十八、这一阶段真正只记一句话

> **一个开源大模型不是一个神秘文件，而是一套彼此配套的资产：`config` 告诉你脑子怎么搭，Tokenizer 告诉你文字怎么进，Weights 保存真正学到的参数，Index 告诉你参数放在哪，Generation Config 告诉你默认怎样生成。**

再压缩成一张脑图：

```text
                 MODEL
                   │
     ┌─────────────┼─────────────┐
     │             │             │
     ▼             ▼             ▼
   config       tokenizer      weights
   怎么搭         怎么读         学到了什么
                                   │
                                   ▼
                             shard + index
                             参数放在哪里

                   │
                   ▼
          generation_config
             默认怎么生成
```

当这张图进入脑子以后，下一阶段的 `from_pretrained()` 就不再是魔法。

---

# 下一阶段：第三课 · 第 4 阶段
## `from_pretrained()` 背后到底发生了什么？模型怎样从 SSD 一步步变成 GPU 里真正可以运行的 Transformer？

下一阶段我们会第一次把**文件世界**和**运行时世界**接起来：

```text
模型仓库
   ↓
读取 config
   ↓
创建空模型骨架
   ↓
读取 safetensors
   ↓
填入 Weight
   ↓
选择 Dtype
   ↓
选择 Device
   ↓
RAM / VRAM
   ↓
可执行 Forward
```

并且会重点拆清四个特别容易混淆的问题：

```text
① “下载模型”和“加载模型”是不是一回事？

② Weight 从 SSD 到 RAM，再到 VRAM，到底发生了什么？

③ device_map="auto" 到底在自动什么？

④ 为什么加载一个大模型时，RAM 和 VRAM 可能会同时暴涨？
```

到了那一阶段，`AutoModelForCausalLM.from_pretrained()` 就会从一行“魔法代码”，变成你能在脑子里逐步模拟出来的一整条加载流水线。

---

<!-- LESSON 03 STAGE 03 END -->


<!-- LESSON 03 STAGE 04 START -->

# 第三课 · 第 4 阶段：`from_pretrained()` 背后到底发生了什么？
## 模型怎样从 SSD 上的一堆文件，一步步变成 GPU 里真正可以运行的 Transformer？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **from_pretrained() 不是一个神秘黑盒：读取 Config → 构建模型结构 → 加载权重 → 设置 dtype/device → 返回可运行对象。**
2. **Download Complete ≠ Model Ready。文件到磁盘后还要完成解析、权重装载和设备放置。**
3. **device_map / Offloading 改变“权重放在哪里”，不等于改变模型语义能力。**
4. **Loading Peak Memory 可能高于最终驻留内存；能保存文件不代表加载过程一定不会 OOM。**
5. **第三方 Remote Code / 自定义模型实现属于执行代码边界，加载前要关注来源与安全，而不只是模型参数大小。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `Transformer` | Transformer：以注意力和前馈网络为核心的序列架构 |
| `VRAM` | 显存：GPU 上存放权重、激活和 KV Cache 等的高速内存 |
| `CPU` | CPU：负责通用控制、数据准备和部分算子 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `dtype` | 数据类型：FP32/FP16/BF16 等，影响显存、速度和数值稳定性 |
| `device_map` | 设备映射：指定模型模块放在哪个 GPU/CPU |
| `Tokenizer` | 分词器：文本与 Token ID 之间的编码/解码组件 |
| `Checkpoint` | 检查点：保存模型和训练状态以便恢复/发布 |
| `Memory` | 任务记忆：保存跨步骤需要复用的结构化信息 |
| `Attention` | 注意力：根据内容相关性动态聚合信息 |
| `MLP` | MLP/前馈网络：对每个位置表示做非线性变换 |

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

第三阶段我们已经把**模型文件夹**看懂了：

```text
模型仓库
│
├── config
│      └── 模型怎么搭
│
├── tokenizer
│      └── 文字怎么进模型
│
├── weights
│      └── 模型真正学到了什么
│
├── shard + index
│      └── 参数放在哪
│
└── generation_config
       └── 默认怎么生成
```

现在真正的问题来了。

以后你会看到这样一行代码：

```python
model = AutoModelForCausalLM.from_pretrained(...)
```

看起来只有一行。

但这一行背后实际上可能发生几十件事。

这一阶段我们不追源码细节，先把它变成一部你脑子里能播放的“装机电影”。

今天真正需要带走 **5 个核心心智模型**：

```text
① 下载模型 ≠ 加载模型

② from_pretrained()
   = 看蓝图 → 搭空架子 → 找参数 → 把参数装进去

③ SSD、RAM、VRAM 是三个不同地点
   模型会在它们之间搬家

④ dtype 决定“每个参数占多少空间”
   device_map 决定“这些参数放在哪里”

⑤ 加载大模型最危险的不只是最终显存，
   还有加载过程中的峰值内存
```

如果这五件事真正吃透，后面再看到：

```text
device_map="auto"
torch_dtype="auto"
low_cpu_mem_usage=True
offload
meta device
```

你就不会把它们当魔法参数。

---

# 一、先看整部电影

假设你的 SSD 上已经有一个模型：

```text
ProcurementBaseModel/
│
├── config.json
├── tokenizer.json
├── model-00001-of-00004.safetensors
├── model-00002-of-00004.safetensors
├── model-00003-of-00004.safetensors
├── model-00004-of-00004.safetensors
└── model.safetensors.index.json
```

你运行：

```python
model = AutoModelForCausalLM.from_pretrained(
    "ProcurementBaseModel"
)
```

脑子里应该马上出现：

```text
SSD上的模型文件
      │
      ▼
读取 config
      │
      ▼
知道模型应该长什么样
      │
      ▼
创建 Transformer 骨架
      │
      ▼
读取 Weight Index
      │
      ▼
找到每个参数在哪个 safetensors
      │
      ▼
逐步读取 Weight
      │
      ▼
把 Weight 填进对应 Layer
      │
      ▼
决定参数用什么 dtype
      │
      ▼
决定参数放 CPU 还是 GPU
      │
      ▼
形成可执行模型
```

这就是本阶段最重要的总图。

---

# 二、第一个核心心智模型：下载 ≠ 加载

这个区别看起来简单，却是以后排错的基础。

## 1. 什么叫下载模型？

下载解决的是：

> **模型文件有没有来到你的机器。**

比如远程仓库里有：

```text
config.json
tokenizer.json
*.safetensors
```

下载以后：

> 它们出现在你的 SSD / 磁盘缓存里。

到这里模型只是：

# Files on Disk

---

## 2. 它还不会回答问题

模型文件安静躺在 SSD 上：

```text
SSD
│
└── 14GB / 30GB / 60GB 模型文件
```

它不会自己：

> 跑 Attention。

不会：

> 做矩阵乘法。

不会：

> 生成一个 Token。

---

## 3. 什么叫加载模型？

加载解决的是：

> **把磁盘上的静态文件，变成程序内真正可以参与计算的 Tensor 和 Model Object。**

所以：

```text
Download
=
网络 → SSD

Load
=
SSD → 内存中的模型对象
```

---

## 4. 一个政府采购类比

你从全国法规库下载了：

> 20GB 政府采购法规资料。

文件已经在电脑里。

这叫：

> **资料已经到货。**

但专家还没：

- 打开；
- 分类；
- 放到桌面；
- 建立索引；
- 开始工作。

---

## 5. `from_pretrained()` 更像什么？

它更像：

> 把整个专家团队叫到办公室，按照组织架构安排好岗位，再把每个人原来的知识和工作状态恢复回来。

所以：

```text
下载
=
资料运到办公楼

加载
=
让整个组织真正进入工作状态
```

---

# 三、第二个核心心智模型：先搭骨架，再装参数

第三阶段我们已经区分：

```text
config
≠
weights
```

现在这个区别真正开始发挥作用。

---

## 6. 第一步通常要先知道模型长什么样

假设 `config` 告诉系统：

```text
Hidden Size = 4096
Layers = 32
Attention Heads = 32
KV Heads = 8
Intermediate Size = 11008
```

于是加载器大概知道：

> 要创建 32 个 Decoder Layer。

每层里面要有：

```text
Attention
MLP
Norm
Residual相关结构
```

---

## 7. 这时候可以先想象一个“空壳模型”

```text
Embedding          [空]
   ↓
Layer 0
 ├─ q_proj         [空]
 ├─ k_proj         [空]
 ├─ v_proj         [空]
 ├─ o_proj         [空]
 ├─ gate_proj      [空]
 ├─ up_proj        [空]
 └─ down_proj      [空]
   ↓
Layer 1            [空]
   ↓
...
   ↓
Layer 31           [空]
   ↓
Final Norm         [空]
   ↓
LM Head            [空]
```

结构：

> 已经知道了。

但真正训练后的数字：

> 还没装进去。

---

# 四、什么叫“把 Weight 装进去”？

## 8. Weight 文件里可能有这样的参数名字

概念上：

```text
model.layers.0.self_attn.q_proj.weight

model.layers.0.self_attn.k_proj.weight

model.layers.0.mlp.gate_proj.weight

...

model.layers.31.mlp.down_proj.weight
```

---

## 9. 加载器要做的事情

本质上就是：

```text
文件里的参数名
        ↓
找到模型里对应的位置
        ↓
检查 Shape
        ↓
把真实 Tensor 放进去
```

---

## 10. 例如

空模型里有：

```text
Layer 0
└── q_proj.weight
```

Weight 文件里也有：

```text
model.layers.0.self_attn.q_proj.weight
```

于是把训练后的矩阵：

> 装进这里。

---

# 五、用“酒店开业”类比

这次我们不用大脑，换一个更直观的。

`config.json`：

> 酒店建筑设计图。

模型骨架：

> 已经建好的空酒店。

Weights：

> 房间里的家具、设备、员工工作状态。

---

## 11. `from_pretrained()` 干的事情

```text
读建筑图
   ↓
知道有32层
   ↓
搭好每一层结构
   ↓
打开货运清单
   ↓
床送进101房
桌子送进102房
设备送进机房
   ↓
酒店进入可运营状态
```

---

## 12. 如果东西送错房会怎么样？

比如：

> 给 4096 宽的位置塞一个 5120 宽的参数。

就相当于：

> 一张 5 米床硬塞进 3 米房间。

加载器会说：

> Shape 不匹配。

---

# 六、Shard 在加载阶段到底发挥什么作用？

假设模型 Weight 有 4 个分片：

```text
Shard 1
Shard 2
Shard 3
Shard 4
```

加载器不会随便乱猜：

> Layer 17 在哪个文件。

---

## 13. 它可以先读 Index

概念上：

```text
layer.0.q_proj
→ shard 1

layer.8.mlp
→ shard 2

layer.20.k_proj
→ shard 3

lm_head
→ shard 4
```

---

## 14. 然后按地图找箱子

```text
Index
   ↓
参数A在哪？
   ↓
Shard 2
   ↓
读取参数A
   ↓
放入模型
```

第三阶段的：

```text
Shard = 货箱

Index = 货物地图
```

现在正式进入运行过程。

---

# 七、第三个核心心智模型：SSD、RAM、VRAM 是三个不同地点

这是整个第三课非常重要的一条线。

把一台机器想成：

```text
SSD
=
仓库


RAM
=
总装区


VRAM
=
GPU车间工作台
```

---

## 15. 模型最开始在哪里？

SSD。

---

## 16. CPU 要读取 Weight 时

通常数据要进入：

# RAM

---

## 17. 如果要 GPU 运行

最终相关 Tensor 还需要来到：

# VRAM

---

## 18. 所以最朴素的模型加载路径

可以想成：

```text
SSD
 │
 │ 读取
 ▼
RAM
 │
 │ CPU → GPU Transfer
 ▼
VRAM
 │
 ▼
GPU计算
```

---

# 八、这里有一个非常重要的问题

假设模型 Weight 最终只占：

> 20GB VRAM。

是不是意味着：

> 加载时最多只需要 20GB RAM + 20GB VRAM？

不一定。

因为：

> **加载过程本身也可能产生额外副本。**

这就是今天后半段最重要的问题。

---

# 九、先看最笨的加载方法

假设模型 Weight：

> 20GB。

一种非常朴素的实现可能是：

```text
1. 从SSD把全部20GB权重读到RAM

2. 在RAM里创建完整模型参数

3. 把参数再复制到GPU

4. GPU里再占20GB
```

某些阶段中可能同时出现：

```text
RAM：
一份 checkpoint 数据
+
一份 model parameter

VRAM：
一份 GPU parameter
```

---

## 19. 于是出现什么？

最终模型可能只需要：

> 20GB VRAM。

但加载过程中：

> RAM 峰值可能高得多。

---

# 十、这就是“峰值内存”

我们以后会经常遇到：

# Peak Memory

它与：

# Final Memory

完全不是一回事。

---

## 20. 一个办公室搬家类比

新办公室最终只需要：

> 100 张桌子。

但搬家当天可能同时存在：

```text
旧办公室：
100张旧桌子

仓库：
100张新桌子

新办公室：
正在摆100张桌子
```

于是搬家那天：

> 空间需求特别高。

搬完以后：

> 又降下来。

---

## 21. 模型加载也可能这样

所以：

```text
最终装得下
≠
加载过程一定装得下
```

这是非常重要的工程直觉。

---

# 十一、为什么大模型加载经常把 RAM 打爆？

假设：

```text
模型最终显存需求：
30GB

服务器RAM：
32GB
```

你可能觉得：

> “GPU 有足够显存，应该没问题。”

结果：

> 加载过程中系统 RAM 先爆了。

---

## 22. 原因可能是什么？

不是 GPU 不够。

而是：

```text
SSD
↓
RAM
```

这一段的临时空间：

> 不够。

---

# 十二、所以模型加载要同时看两块内存

```text
CPU侧
RAM

GPU侧
VRAM
```

以后不要只问：

> “显存够不够？”

还要问：

> “加载过程中 CPU RAM 够不够？”

---

# 十三、什么是“逐片加载”？

既然模型已经 Shard 了，

一个更聪明的策略是：

```text
读取 Shard 1
↓
把里面参数放到目标位置
↓
释放不需要的临时数据

读取 Shard 2
↓
放参数
↓
释放

...
```

---

## 23. 而不是

```text
先把所有Shard
全部堆进RAM
↓
再慢慢装
```

这样可以：

> 降低加载峰值。

---

# 十四、这就是为什么 Shard 不只是为了下载方便

它还可以让大型模型：

> 更适合流式、逐部分处理。

当然具体加载实现：

> 会因框架而异。

我们这里只建立心智模型。

---

# 十五、一个关键词：`low_cpu_mem_usage`

以后你可能看到类似：

```python
low_cpu_mem_usage=True
```

今天不要把它当作：

> “加上就神奇省内存。”

---

## 24. 它试图解决的核心问题是什么？

就是刚才那个：

> **不要在 CPU RAM 中不必要地同时保留多份巨大的模型参数。**

---

## 25. 它背后的工程思想

可以先记成：

```text
不要：
完整空模型
+
完整Checkpoint副本
+
完整加载后参数

同时全堆RAM
```

而是尽量：

> 边创建、边装载、边释放。

---

# 十六、另一个重要概念：Meta Device

这个名字第一次看到会很吓人。

其实心智模型很简单。

---

## 26. 普通 Tensor

如果你创建：

```text
4096 × 4096
```

矩阵，

它要：

> 真正分配内存。

---

## 27. Meta Tensor 可以粗略理解成

> **只有“尺寸说明”，暂时不真正存这些数字。**

---

## 28. 像什么？

你在仓库管理系统里先创建：

```text
货架A：
需要放4096 × 4096的货物
```

但货架里：

> 暂时没有实际货物。

---

## 29. 为什么这样有价值？

如果你一开始创建整个 30B 模型的随机 Weight：

> 就已经要占大量 RAM。

然后又马上用 checkpoint：

> 把这些随机 Weight 覆盖掉。

这其实很浪费。

---

## 30. 更聪明的思路

先创建：

> 只有 Shape 和结构的“空架子”。

不分配完整真实参数空间。

然后：

> 从 checkpoint 直接把训练后的 Weight 放进去。

---

# 十七、把它画出来

### 传统直觉

```text
创建完整随机模型
      ↓
占一大块RAM
      ↓
读取训练Weight
      ↓
再覆盖随机参数
```

---

### 更节省内存的直觉

```text
创建“Meta骨架”
      ↓
知道Shape，但少占真实参数内存
      ↓
读取Checkpoint
      ↓
把真实Weight直接填进去
```

---

# 十八、这就是第四个核心理解的前半部分

很多所谓：

```text
大模型省内存加载
```

本质并不是：

> 模型 Weight 凭空变少。

而是：

> **减少加载过程中的不必要副本。**

这句话非常值得记。

---

# 十九、现在进入 `dtype`

第三课后面第 6 阶段会专门学精度。

今天只建立：

> `dtype` 在加载阶段到底控制什么。

---

## 31. 一个参数不是抽象数字

计算机必须决定：

> 用多少 bit / byte 存它。

例如以后会学：

```text
FP32
FP16
BF16
INT8
INT4
```

---

## 32. 对加载器来说

这意味着：

> **同样 70 亿个参数，每个参数占多少空间？**

---

# 二十、一个最直观例子

假设模型：

# 7B

大约 70 亿参数。

如果每个参数：

> 4 Bytes。

Weight 大约：

```text
28GB
```

---

## 33. 如果每个参数

> 2 Bytes。

大约：

```text
14GB
```

---

## 34. 如果有效做到

> 1 Byte 左右。

大约：

```text
7GB
```

先不要纠结额外 metadata 和实际实现差异。

今天只抓直觉：

```text
参数数量
×
每个参数占用
=
权重空间数量级
```

---

# 二十一、所以 `dtype` 在加载阶段是什么？

可以把它想成：

> **决定每件货物用多大的包装箱。**

同样：

> 70 亿件货。

如果每件都用 4 单位空间：

> 很大。

换成 2：

> 大约一半。

---

# 二十二、但这里有一个特别容易踩的坑

假设磁盘上的 Weight 是：

> BF16。

你加载时要求：

> FP32。

可能会发生：

> 参数在内存中变大。

---

## 35. 反过来

如果模型支持用更低精度运行，

你加载成：

> BF16 / FP16。

可以减少：

> VRAM。

---

## 36. 所以 `dtype` 不只是“数学精度”

它直接关系：

```text
RAM
VRAM
Bandwidth
Compute
```

第 6 阶段会彻底展开。

---

# 二十三、现在进入 `device`

我们上一阶段已经学过：

```text
cpu
cuda:0
cuda:1
...
```

---

## 37. 模型加载完以后必须回答

> 每一个参数到底住在哪里？

例如：

```text
Embedding
→ GPU0

Layer 0
→ GPU0

Layer 1
→ GPU0

...

LM Head
→ GPU0
```

这是最简单的单 GPU 情况。

---

# 二十四、如果一张 GPU 装不下呢？

假设：

> 一个模型需要 40GB。

但你只有两张：

```text
GPU0：24GB
GPU1：24GB
```

---

## 38. 一个可能的思路

把模型切开：

```text
GPU0
├─ Embedding
├─ Layer 0
├─ Layer 1
├─ ...
└─ Layer 15


GPU1
├─ Layer 16
├─ ...
├─ Layer 31
└─ LM Head
```

---

# 二十五、这就是 `device_map` 的第一层直觉

```text
device_map
=
模型的“住宿分配表”
```

它告诉加载器：

> 哪个模块放哪个 Device。

---

# 二十六、所以 `device_map="auto"` 在自动什么？

它不是：

> “自动让模型变聪明。”

也不是：

> “自动优化所有性能。”

---

## 39. 它主要是在尝试

根据可用：

```text
GPU显存
CPU内存
模型模块大小
```

等信息，

决定：

> **模型各部分放到哪里。**

---

## 40. 可以想象成酒店安排住宿

现在有 32 个专家团队：

```text
Layer 0
Layer 1
...
Layer 31
```

你有：

```text
酒店A：24个房间
酒店B：24个房间
```

`device_map="auto"`：

> 尝试自动安排谁住哪家酒店。

---

# 二十七、但“自动”不等于“最优”

这是必须强调的。

自动分配可能优先目标是：

> **能装下。**

但：

> 能装下

不一定等于：

> 性能最好。

---

## 41. 为什么？

如果每一层在不同设备间频繁搬数据：

```text
GPU0
↓
GPU1
↓
CPU
↓
GPU1
```

通信成本：

> 可能很高。

---

# 二十八、所以再次出现一个核心区别

```text
Fits
≠
Fast
```

也就是：

\[
\boxed{
装得下
\neq
跑得快
}
\]

这和第三课第一阶段：

> Possible ≠ Practical

是一条线。

---

# 二十九、CPU Offload 是什么？

假设 GPU 装不下完整模型。

一种方案是：

> 有些模块放 GPU。

> 有些放 CPU RAM。

---

## 42. 例如

```text
GPU
├─ Layer 0 ~ 20

CPU
├─ Layer 21 ~ 31
```

这就属于某种：

# Offload

思想。

---

## 43. 这样有什么好处？

模型：

> 可能终于装得下。

---

## 44. 代价是什么？

CPU RAM 与 GPU VRAM 之间：

> 需要数据传输。

可能明显变慢。

---

# 三十、再极端一点：Disk Offload

如果：

> RAM 也不够。

某些系统还可以把部分内容放在：

> SSD。

---

## 45. 但速度会怎么样？

想象：

```text
GPU VRAM
最快工作台

RAM
远一点仓库

SSD
更远的大仓库
```

如果运行中频繁去 SSD 取模型层：

> 会非常慢。

---

# 三十一、一张“模型居住层级图”

```text
最快
▲
│
│  GPU VRAM
│  ─────────
│  GPU直接高速访问
│
│  CPU RAM
│  ─────────
│  容量通常更大，但离GPU更远
│
│  SSD
│  ─────────
│  容量更大，主要长期存储
│
▼
更慢
```

这只是概念图，不代表所有机器的固定性能比例。

---

# 三十二、第五个核心心智模型：模型加载其实是在做“空间规划”

以前你可能觉得：

```python
from_pretrained()
```

只是：

> 打开模型。

现在应该看到：

```text
我要读什么架构？

参数在哪里？

参数是什么dtype？

RAM够不够？

VRAM够不够？

需要分片吗？

要不要多GPU？

要不要CPU Offload？

加载峰值会不会OOM？
```

这已经是：

> **资源规划问题。**

---

# 三十三、一个完整 ProcurementLM 场景

假设我们未来选了一个：

> 14B Instruct 模型。

服务器：

```text
RAM：64GB

GPU0：24GB VRAM

SSD：2TB
```

---

## 46. 第一问

模型 Weight 在 SSD 上。

能下载吗？

> 当然，只要磁盘够。

---

## 47. 第二问

能放 RAM 吗？

要看：

> Weight 大小和加载峰值。

---

## 48. 第三问

能完整放 GPU 吗？

如果它是高精度 Weight：

> 可能装不下 24GB。

---

## 49. 那怎么办？

可能考虑：

```text
降低Precision / Quantization

CPU Offload

选择更小模型

多GPU
```

---

## 50. 注意

我们现在不是在推荐哪一个。

而是在建立：

> **决策树。**

---

# 三十四、决策树第一次出现

```text
目标模型
   │
   ▼
Weight大约多大？
   │
   ▼
单GPU装得下吗？
   │
   ├── 是
   │    ↓
   │   单GPU
   │
   └── 否
        ↓
    是否允许低精度？
        │
        ├── 是 → Quantization
        │
        └── 否
             ↓
          多GPU / Offload / 换模型
```

后面第 6、7 阶段会把它变得真正可计算。

---

# 三十五、`from_pretrained()` 为什么有时很慢？

即使网络已经下载完成。

加载仍可能花时间。

因为还要：

```text
SSD读取

JSON解析

Shard读取

Tensor创建

dtype转换

CPU→GPU传输

多GPU分配
```

---

## 51. 所以“下载速度”与“加载速度”

也是两个不同指标。

```text
Download Time
≠
Load Time
```

---

# 三十六、为什么 NVMe SSD 会有帮助？

如果模型几十 GB、几百 GB，

第一次加载要从磁盘读取大量数据。

---

## 52. 如果磁盘特别慢

GPU 再快：

> 也要等 Weight 读出来。

所以存储 IO：

> 也可能影响模型启动时间。

---

# 三十七、但 SSD 不直接决定生成 TPS

模型加载完以后：

> Weight 已经主要在 RAM / VRAM 中。

这时生成速度：

> 主要由其它瓶颈决定。

---

## 53. 所以要区分

```text
Model Startup / Load Time
```

和：

```text
Inference Runtime Speed
```

---

# 三十八、再来一个很常见的疑问

> “为什么加载时 GPU 显存一点点增加？”

可能因为：

> 模型 Shard 正在逐步被读取并放进 GPU。

---

## 54. 为什么 RAM 也同时变化？

因为：

> 数据可能正在经过 CPU 侧加载、解析、临时缓存。

这就是：

```text
SSD → RAM → VRAM
```

在现实中的表现。

---

# 三十九、模型加载完成后能不能把 RAM 全释放？

不一定。

---

## 55. 一些程序本身还需要

- Python；
- Tokenizer；
- CPU 数据结构；
- 文件缓存；
- Offload 参数；
- 推理框架状态。

所以：

> RAM 不会变成零。

---

# 四十、Tokenizer 和 Model 是不是同一个 `from_pretrained()`？

通常不是一个对象。

概念上经常是：

```python
tokenizer = AutoTokenizer.from_pretrained(...)

model = AutoModelForCausalLM.from_pretrained(...)
```

---

## 56. 为什么分开？

因为它们解决不同问题。

```text
Tokenizer
=
Text ↔ Token IDs

Model
=
Token IDs → Hidden States → Logits
```

第二课现在又和运行时接起来了。

---

# 四十一、一个完整请求真正进系统

模型已经加载完成。

用户输入：

> “审查以下评分标准是否存在倾向性。”

---

## 57. Tokenizer 在 CPU 侧生成

概念上：

```text
input_ids
attention_mask
```

---

## 58. 然后 Tensor 搬到

```text
cuda:0
```

---

## 59. 模型 Weight 也在

```text
cuda:0
```

---

## 60. 于是：

```text
Input Tensor
+
Model Weights
```

在同一个 GPU 上：

> 执行 Forward。

---

# 四十二、如果 Input 在 CPU，Model 在 GPU 会怎样？

常见情况：

> 报 Device Mismatch。

---

## 61. 为什么？

因为：

```text
输入文件在东京
模型在大阪
```

你却要求：

> “立刻在同一张桌子上做运算。”

设备不一致。

---

# 四十三、所以加载模型只是第一步

一个可运行推理系统还需要：

```text
模型在哪里？

输入在哪里？

新生成的Tensor在哪里？

KV Cache在哪里？
```

Device：

> 必须贯穿整个运行流程。

---

# 四十四、为什么 `device_map="auto"` 和 `model.to("cuda")` 不是一回事？

这两个很容易混。

---

## 62. `model.to("cuda")`

最直观的意思：

> 尝试把整个模型搬到一个 CUDA Device。

---

## 63. `device_map`

允许更细粒度：

```text
Layer A → GPU0

Layer B → GPU1

Layer C → CPU
```

---

## 64. 所以如果已经使用复杂 Device Map

再随便：

```python
model.to("cuda")
```

可能：

> 破坏原来的分配意图。

以后实操时会专门说明。

今天只记：

```text
.to("cuda")
=
整体搬家思维

device_map
=
分房思维
```

---

# 四十五、什么叫模型“Materialize”？

这个词以后可能看到。

它可以粗略理解成：

> 从“只有结构/Shape 的空架子”，真正变成“拥有实际数值 Tensor 的模型”。

---

## 65. Meta Tensor 阶段

```text
我知道这里需要一个4096×4096矩阵
```

---

## 66. Materialize 以后

```text
这里真的有4096×4096个参数值
```

---

# 四十六、为什么这个概念对大模型特别重要？

因为一个 70B 模型：

> 随便多创建一次完整参数副本，

都可能意味着：

> 数十 GB 甚至更多内存。

所以大型模型工程非常关注：

```text
什么时候真正分配内存？

在哪里分配？

有没有多余副本？
```

---

# 四十七、这也是为什么“小模型写法”不一定适合“大模型”

小模型：

```text
几百MB
```

你创建两份、三份：

> 可能无所谓。

---

## 67. 大模型

```text
30GB
60GB
140GB
```

多复制一份：

> 服务器直接爆内存。

---

# 四十八、一个很关键的工程思维转变

在小模型时代：

> 我们主要担心“数学对不对”。

进入大模型以后还必须担心：

> **数据到底住在哪里。**

这句话特别重要。

---

# 四十九、第三课到这里已经出现一条主线

第一阶段：

```text
硬件资源在哪里？
```

第二阶段：

```text
软件如何调用GPU？
```

第三阶段：

```text
模型文件是什么？
```

第四阶段：

```text
这些文件怎么变成运行中的模型？
```

这四阶段其实是一个连续故事。

---

# 五十、四阶段合体图

```text
                    模型仓库
                       │
                       ▼
SSD ──────────── config + tokenizer + weights
                       │
                       │ from_pretrained()
                       ▼
RAM ──────────── 模型结构 + 临时Tensor
                       │
                       │ device placement
                       ▼
VRAM ─────────── Model Weights
                       │
                       ▼
GPU ──────────── Transformer Forward
                       │
                       ▼
                    Logits
```

而软件调用链是：

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

把这两张图叠起来：

> 就开始像真正的 LLM 系统工程了。

---

# 五十一、一个加载失败案例：RAM OOM

情况：

```text
GPU VRAM：够
RAM：不够
```

---

## 68. 加载时发生

```text
SSD
↓
RAM暴涨
↓
系统OOM
```

模型甚至：

> 还没真正进入 GPU。

---

## 69. 这时候错误结论

> “显卡不够。”

不一定。

真正问题：

> CPU RAM 加载峰值。

---

# 五十二、第二个案例：CUDA OOM

情况：

```text
RAM：足够
GPU：不够
```

---

## 70. 加载过程

```text
SSD
↓
RAM
↓
VRAM不断增加
↓
CUDA OOM
```

这时候才主要属于：

> VRAM Capacity 问题。

---

# 五十三、第三个案例：模型能加载，但极慢

情况：

```text
一部分Layer在GPU

一部分Layer在CPU
```

---

## 71. 结果

模型：

> 能跑。

但每次 Forward：

> 频繁跨设备传输。

所以：

```text
Fits ✅

Fast ❌
```

---

# 五十四、第四个案例：加载成功但输出一团糟

这时未必是：

> Device 问题。

---

## 72. 可能是

```text
Tokenizer不匹配

Chat Template错误

模型类型用错

Prompt格式错误
```

这说明：

> **系统问题要分层诊断。**

---

# 五十五、第五个案例：下载完还是提示缺文件

可能原因：

> Shard 没下载完整。

---

## 73. 例如 Index 说

```text
某参数
→ model-00004-of-00004.safetensors
```

但本地只有：

```text
00001
00002
00003
```

那完整模型：

> 根本装不起来。

---

# 五十六、为什么模型缓存很重要？

从远程仓库下载的大模型：

> 通常不会每次运行都重新下载。

框架一般会使用：

> 本地缓存。

---

## 74. 所以第二次加载

可能是：

```text
本地Cache
↓
RAM
↓
VRAM
```

而不是：

```text
Internet
↓
重新下载几十GB
```

---

# 五十七、Cache 和运行中的 Model 又不是一回事

Cache：

> 仍然是磁盘文件。

运行中的 Model：

> 是内存里的 Tensor。

所以：

```text
Cache exists
≠
Model currently loaded
```

---

# 五十八、为什么服务器重启以后要重新加载模型？

因为：

> RAM / VRAM 是易失工作内存。

机器关机：

> 内容消失。

---

## 75. SSD 上模型还在

所以重启后：

```text
SSD
↓
重新Load
↓
RAM/VRAM
```

又要来一遍。

---

# 五十九、为什么模型服务启动要“Warm Up”？

加载完 Weight：

> 并不一定代表第一请求已经达到稳定最快状态。

---

## 76. 某些系统还会经历

- Kernel 初始化；
- 内存分配；
- 图编译；
- Cache 建立；
- 第一次实际 Forward。

所以第一次请求：

> 可能比后续慢。

---

## 77. 这叫 Warm-up 的直觉

就像工厂：

> 机器刚通电不代表流水线立刻满速。

---

# 六十、以后我们部署 ProcurementAI 时要区分三种时间

```text
① Download Time
模型第一次到机器要多久

② Load / Startup Time
文件变成运行模型要多久

③ Inference Time
用户真正问问题后要多久
```

三个时间：

> 完全不同。

---

# 六十一、再看 `from_pretrained()`，现在应该是什么感觉？

以前：

```python
model = AutoModelForCausalLM.from_pretrained(...)
```

看起来：

> 一句魔法。

现在你应该能在脑子里展开：

```text
找到模型
↓
读config
↓
创建骨架
↓
找到weight shards
↓
逐块读参数
↓
检查shape
↓
决定dtype
↓
决定device
↓
减少不必要副本
↓
把参数放进目标内存
↓
完成可执行模型
```

这就是这一阶段真正的目标。

---

# 六十二、五个核心心智模型再压缩一次

| 心智模型 | 真正要理解的东西 |
|---|---|
| **① Download ≠ Load** | 下载把文件放到 SSD；加载把文件变成内存中的可计算模型 |
| **② 先骨架，后参数** | `config` 定义结构，checkpoint 把训练后的 Weight 填进去 |
| **③ SSD → RAM → VRAM** | 模型运行前经历不同存储层，三者容量和速度完全不同 |
| **④ dtype 管“多大”，device_map 管“住哪”** | 一个控制参数存储形式，一个控制参数放置位置 |
| **⑤ Peak Memory ≠ Final Memory** | 模型最终装得下，不代表加载过程中不会因为临时副本而 OOM |

---

# 六十三、两个辅助心智模型

第一个：

```text
Meta Device
=
先登记房间尺寸
暂时不把家具真正搬进去
```

第二个：

```text
Offload
=
GPU工作台放不下
就把部分货放到更远的RAM甚至SSD
```

代价通常是：

> 更慢。

---

# 六十四、ProcurementAI 的一个完整加载故事

假设明天我们真的部署模型。

服务器启动：

```text
Step 1
读取模型仓库

Step 2
config告诉程序：
32层、4096维……

Step 3
创建空Transformer骨架

Step 4
读取safetensors index

Step 5
逐个Shard加载参数

Step 6
根据dtype决定参数占用

Step 7
根据device_map安排GPU/CPU

Step 8
模型进入RAM/VRAM

Step 9
Tokenizer加载完成

Step 10
ProcurementAI开始接收采购文件
```

这时候一个开源模型：

> 才真正从“文件”变成“服务”。

---

# 六十五、本阶段思维实验 A

你的 SSD 有：

> 500GB 空间。

GPU：

> 8GB VRAM。

你成功下载了一个：

> 60GB 模型。

是不是代表可以直接 GPU 推理？

**不是。**

因为：

```text
磁盘能放下
≠
VRAM能放下
```

---

# 六十六、思维实验 B

GPU 有：

> 48GB VRAM。

模型最终需要：

> 40GB。

RAM 只有：

> 16GB。

是不是一定可以正常加载？

**仍然不能保证。**

因为：

> 加载过程可能先受到 RAM 峰值限制。

---

# 六十七、思维实验 C

两张 GPU：

```text
24GB + 24GB
```

是不是自动等于：

> 一张 48GB GPU？

**不是。**

容量可以通过某些模型分片方式共同利用，

但：

> 两块物理显存不是天然形成一块连续统一 VRAM。

还存在：

- 模块分配；
- GPU 间通信；
- 软件框架；

等问题。

这个以后再展开。

---

# 六十八、思维实验 D

模型使用 CPU Offload 后：

> 成功运行。

是不是说明问题彻底解决？

取决于目标。

如果目标只是：

> 能运行。

可能解决了。

如果目标是：

> 高吞吐生产服务。

可能：

> 速度完全不够。

所以：

```text
Technical Success
≠
Production Success
```

---

# 六十九、思维实验 E

模型文件只有：

> 10GB。

加载以后 VRAM：

> 14GB。

是不是框架一定“浪费”了 4GB？

不能这样判断。

还可能有：

- Tensor 表示；
- Runtime Workspace；
- KV Cache；
- Kernel Buffer；
- 其它 GPU Allocation。

所以：

```text
File Size
≠
Runtime VRAM
```

---

# 七十、本阶段最容易犯的六个错误

### 错误 1

> 下载成功 = 模型已经在 GPU。

错。

---

### 错误 2

> 模型磁盘 20GB = 运行只要 20GB VRAM。

错。

---

### 错误 3

> 最终显存装得下 = 加载一定成功。

错。

还可能：

> RAM 峰值先爆。

---

### 错误 4

> `device_map="auto"` = 性能自动最优。

错。

首先更像：

> 自动设备放置。

---

### 错误 5

> Offload = 免费增加显存。

错。

它用：

> 速度换容量。

---

### 错误 6

> dtype 只是模型精度问题。

不完整。

它还直接影响：

> Weight Memory、Bandwidth 和可运行规模。

---

# 七十一、本阶段掌握测试

如果你现在不看前文，能够自己解释下面这些问题，第 4 阶段就真正建立起来了：

> 下载模型和加载模型到底有什么区别？

> `from_pretrained()` 为什么不能简单理解成“打开一个文件”？

> `config` 和 checkpoint 分别在加载过程中承担什么角色？

> 什么叫“空模型骨架”？

> Shard 和 Index 在加载时怎么配合？

> SSD、RAM、VRAM 分别在加载过程中承担什么角色？

> 为什么模型最终显存只需要 20GB，加载过程中 RAM 却可能超过 20GB？

> 什么叫 Peak Memory？

> 为什么大模型加载要减少不必要参数副本？

> Meta Device 的核心直觉是什么？

> `dtype` 主要决定什么？

> `device_map` 主要决定什么？

> `device_map="auto"` 为什么不等于“自动性能最优”？

> CPU Offload 的好处和代价分别是什么？

> 为什么两张 24GB GPU 不能简单理解成一张 48GB GPU？

> 为什么模型文件大小不等于 Runtime VRAM？

> Download Time、Load Time、Inference Time 为什么必须分别看？

如果这些可以自己讲出来：

\[
\boxed{
第三课第4阶段真正掌握
}
\]

---

# 七十二、这一阶段只记一句话

> **`from_pretrained()` 的本质，不是“打开模型”，而是根据蓝图搭好神经网络，把磁盘里的训练参数按正确 Shape、dtype 和 device 装进模型，并在 SSD、RAM、VRAM 之间完成一次受内存约束的大型搬家。**

把它压成最后一张图：

```text
            SSD
     config + weights
             │
             ▼
       读取模型蓝图
             │
             ▼
        创建空骨架
             │
             ▼
       逐Shard装参数
             │
       ┌─────┴─────┐
       │           │
     dtype     device_map
   每件多大      放在哪里
       │           │
       └─────┬─────┘
             ▼
          RAM / VRAM
             │
             ▼
        可执行Transformer
             │
             ▼
           Forward
```

---

# 下一阶段：第三课 · 第 5 阶段
## 第一次真正让一个开源 LLM 从“文字输入”走到“文字输出”

下一阶段开始，我们会第一次把前四阶段全部串起来，不再只看加载。

整条流程会变成：

```text
用户输入
“请审查这个资格条件”
        ↓
Tokenizer
        ↓
input_ids
        ↓
Tensor → GPU
        ↓
Transformer Forward
        ↓
Logits
        ↓
Sampling / Decoding
        ↓
新的 Token ID
        ↓
Tokenizer Decode
        ↓
中文回答
```

我们会重点回答几个非常直观但极重要的问题：

> `input_ids` 到底长什么样？

> 为什么模型输出的不是文字，而先是 Logits？

> `generate()` 为什么会反复调用模型？

> 为什么模型一次只生成一个或少量新 Token，却最后能形成整段回答？

> Prompt 是在 CPU 里还是 GPU 里？

> `max_new_tokens` 到底限制的是“字数”、Token 数，还是 Context？

然后我们会用一个**政府采购条款审查样例**，完整走一遍“文字 → Token → Tensor → GPU → 模型 → Token → 中文回答”的全过程。

---

<!-- LESSON 03 STAGE 04 END -->


<!-- LESSON 03 STAGE 05 START -->

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

<!-- LESSON 03 STAGE 05 END -->


<!-- LESSON 03 STAGE 06 START -->

# 第三课 · 第 6 阶段：FP32、FP16、BF16、INT8、INT4 与 Quantization
## 为什么同一个 7B 模型可以接近 28GB，也可以只有几 GB？“精度降低”到底牺牲了什么？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Weight Memory 的第一近似 = Parameter Count × Bytes per Parameter；7B 模型在不同 dtype 下显存差异巨大。**
2. **dtype ≠ Quantization。FP16/BF16 是浮点精度选择，INT8/INT4 量化是更强的离散近似与压缩。**
3. **Quantization = Memory/Quality/Kernel Trade-off。更低 bit 通常更省显存，但可能带来精度损失和算子限制。**
4. **Smaller Storage ≠ Faster Inference。真实速度还取决于硬件是否有高效低位宽 Kernel。**
5. **Training Precision 与 Serving Precision 可以不同；选择精度必须匹配训练稳定性、推理质量和硬件支持。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `BF16` | BF16：保留较大指数范围的 16 位浮点，常用于大模型 |
| `FP16` | FP16：16 位浮点，节省显存但数值范围较窄 |
| `Quantization` | 量化：用更低位宽表示权重/激活以降低显存和计算成本 |
| `dtype` | 数据类型：FP32/FP16/BF16 等，影响显存、速度和数值稳定性 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `KV Cache` | KV 缓存：生成时缓存历史 Key/Value 以减少重复计算 |
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `Precision` | 精确率：系统报出的风险中真正成立的比例 |
| `Gradient` | 梯度：损失对参数变化方向和敏感度的局部信息 |
| `Metadata` | 元数据：项目、来源、时间、地区、版本等辅助信息 |
| `Loss` | 损失函数：把预测错误压缩成可优化的数值信号 |
| `Optimizer` | 优化器：依据梯度规则更新参数 |

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

前五阶段，我们已经知道模型最终真正占地方的核心之一是：

> **数十亿个 Weight 数字。**

例如一个 7B 模型，大约有：

> 70 亿个参数。

现在真正的问题是：

> 这 70 亿个数字，一个数字到底要占多大地方？

答案不同，模型大小就会完全不同。

这一阶段真正需要带走 **5 个核心心智模型**：

```text
① bit / byte = 数字的“包装尺寸”

② 参数量决定“有多少件货”
   dtype决定“每件货多大”

③ FP16 和 BF16 都占2 Bytes
   但“数字尺子”的设计不同

④ Quantization = 用更少的刻度近似原来的Weight

⑤ 4-bit模型 ≠ 整个模型所有东西永远都是4-bit
```

先把这五根柱子立起来。

---

# 一、先忘掉 FP32，先想“70 亿件货”

假设你有一个仓库。

里面要放：

```text
70亿件商品
```

每件商品有四种包装方案：

```text
方案A：每件4 Bytes
方案B：每件2 Bytes
方案C：每件1 Byte
方案D：每件0.5 Byte
```

不用懂 AI，我们先算仓库。

一个 7B 模型大约：

```text
7,000,000,000 个参数
```

如果每个参数用 4 Bytes：

```text
约 28GB
```

每个参数 2 Bytes：

```text
约 14GB
```

每个参数 1 Byte：

```text
约 7GB
```

每个参数大约半个 Byte：

```text
约 3.5GB
```

先停在这里。

这张表就是这一阶段最重要的地基：

| 表示方式 | 每参数理论占用 | 7B Weight 的粗略数量级 |
|---|---:|---:|
| FP32 | 4 Bytes | 约 28GB |
| FP16 / BF16 | 2 Bytes | 约 14GB |
| INT8 | 1 Byte | 约 7GB |
| INT4 / 4-bit | 0.5 Byte | 约 3.5GB |

这里全部是**方便做容量预算的近似值**。

真实文件和真实显存还可能有：

> Scale、Metadata、Packing、KV Cache、Buffer 等额外开销。

所以不要把：

```text
3.5GB
```

理解成：

> 4-bit 7B 模型在任何环境下一定只占 3.5GB 显存。

---

# 二、第一个核心心智模型：参数量和精度是两个不同旋钮

模型写着：

```text
7B
```

回答的是：

> 有多少 Parameter？

也就是：

```text
有多少件货？
```

而：

```text
FP32
BF16
INT8
INT4
```

回答的是：

> 每件货用多大的包装？

所以：

```text
7B
+
BF16
```

是两个信息。

---

## 1. 可以这样记

```text
Model Size
      │
      ├── Parameter Count
      │      └─ 有多少数字
      │
      └── Precision / dtype
             └─ 每个数字怎么存
```

---

# 三、什么叫 bit？

计算机最底层使用：

```text
0
1
```

一个二进制位置：

> 叫 1 bit。

---

## 2. 8 bit 大致组成

```text
1 Byte
```

所以：

```text
8 bit  = 1 Byte
16 bit = 2 Bytes
32 bit = 4 Bytes
```

这就是为什么：

```text
FP32 → 4 Bytes

FP16 → 2 Bytes

BF16 → 2 Bytes

INT8 → 1 Byte

INT4 → 半个Byte左右/参数的理论位宽
```

---

# 四、为什么数字需要这么多 bit？

因为计算机不可能：

> 用无限精确的方式保存所有实数。

例如一个 Weight：

```text
0.123456789123456...
```

机器必须决定：

> 我到底保留多少信息？

---

## 3. 就像金额记录

原始真实值假设是：

```text
12.345678901 元
```

你可以保存成：

```text
12.345678901
```

也可以只保存：

```text
12.35
```

甚至：

```text
12
```

保存越粗：

> 占用可以更低。

但损失的信息：

> 越多。

---

# 五、第二个核心心智模型

## Precision 就像“数字尺子的精细程度”

想象两把尺子。

第一把：

```text
0
0.001
0.002
0.003
0.004
...
```

刻度很密。

---

第二把：

```text
0
1
2
3
4
...
```

刻度很粗。

如果真实长度：

```text
2.36
```

细尺可能记：

```text
2.36
```

粗尺只能近似：

```text
2
```

或：

```text
2.5
```

这就是后面理解 Quantization 最好的入口。

---

# 六、先认识 FP32

FP：

# Floating Point

浮点数。

FP32：

> 使用 32 bit 表示一个浮点数字。

所以一个参数大约：

```text
4 Bytes
```

---

## 4. FP32 可以先理解成

> **比较宽裕的数字记录方式。**

它能够同时处理：

- 很小的数；
- 很大的数；
- 比较细的有效精度。

---

## 5. 但代价也很明显

如果模型：

```text
7B
```

只算 Weight：

```text
7B × 4 Bytes
≈ 28GB
```

14B：

```text
约 56GB
```

32B：

```text
约 128GB
```

仅 Weight 就已经非常大。

---

# 七、为什么不永远都用 FP32？

如果：

> 更少的 bit 已经足够让模型正常工作，

那 FP32 就意味着：

```text
更多显存
+
更多内存带宽
+
更多存储
+
可能更低吞吐效率
```

于是工程师自然会问：

> **能不能用更少的 bit？**

---

# 八、进入 FP16

FP16：

> 16-bit Floating Point。

一个参数：

```text
2 Bytes
```

于是 7B：

```text
约 14GB
```

光 Weight 就直接：

> 大约减半。

---

# 九、但是“16 位”不是简单砍掉一半小数位

浮点数不是：

> 单纯保存一个整数和小数点。

它通常要记录三类信息：

```text
正还是负
+
数字大概有多大
+
数字的细节
```

---

# 十、用科学计数法类比

例如：

```text
123400
```

可以写：

```text
1.234 × 10^5
```

这里有：

```text
1.234
```

负责：

> 数字细节。

而：

```text
10^5
```

负责：

> 数字数量级。

浮点数也有类似思想。

---

# 十一、把浮点数画成三个盒子

```text
┌──────┬─────────────┬────────────────┐
│ Sign │  Exponent   │ Fraction       │
│ 正负 │ 大概多大     │ 细节有多精确     │
└──────┴─────────────┴────────────────┘
```

现在你就能理解 FP16 和 BF16 为什么会不同了。

---

# 十二、FP16 与 BF16 都是 16 bit

这是很多初学者第一困惑：

```text
FP16 = 16 bit

BF16 = 16 bit
```

既然都 16：

> 为什么还分两个名字？

因为：

> **这 16 个位置怎么分配，不一样。**

---

# 十三、一张最值得看的结构图

为了建立直觉，可以粗略看：

```text
FP32
┌─1─┬────8────┬────────────23────────────┐
 Sign Exponent           Fraction


FP16
┌─1─┬──5──┬──────10──────┐
 Sign Exp     Fraction


BF16
┌─1─┬────8────┬──7──┐
 Sign Exponent Fraction
```

先别背 1、8、23。

真正重要的是看：

```text
FP16
更多bit留给细节
但Exponent比较短

BF16
Exponent更宽
但细节部分更短
```

---

# 十四、用“地图”理解 FP16 与 BF16

想象两张地图。

### FP16

像：

> 某个城市内部特别精细的地图。

小巷：

> 标得比较细。

但地图覆盖范围：

> 没那么大。

---

### BF16

更像：

> 全国地图。

覆盖范围：

> 很大。

但每个小巷：

> 没那么精细。

---

# 十五、第三个核心心智模型

## FP16 和 BF16 都是 2 Bytes，但它们把“数字预算”花在不同地方

可以粗略记：

```text
FP16
=
更强调局部精细度
较小动态范围


BF16
=
保留很大的动态范围
但有效精度更粗一些
```

---

# 十六、为什么训练特别关心“范围”？

训练过程中不只是保存最终 Weight。

还有：

```text
Activation
Gradient
Optimizer中的数值
```

这些数字：

> 可能跨越很大的数量级。

---

## 6. 例如有些 Gradient

可能非常小。

另一些中间值：

> 相对大很多。

如果数值格式装不下：

> 就可能发生 Overflow / Underflow。

---

# 十七、什么叫 Overflow？

假设你的计算器最大只能显示：

```text
9999
```

结果真正是：

```text
100000
```

装不下。

这就是类似：

# Overflow

---

# 十八、什么叫 Underflow？

另一边。

假设最小可表示的有效数字只能到：

```text
0.001
```

真正要保存：

```text
0.0000001
```

可能最后：

> 变成 0 或失去有效信息。

这类似：

# Underflow

---

# 十九、为什么 BF16 在现代训练里很常见？

先不谈具体 GPU 型号。

从数值设计上看：

> BF16 保留了与 FP32 类似的 Exponent 宽度。

所以训练时对：

> 数值范围

通常比较友好。

---

## 7. 代价

Fraction 更少。

也就是：

> 数字记录没那么细。

---

## 8. 但深度学习有一个很有意思的性质

很多神经网络计算：

> 并不要求每一个 Weight 保存到极端高的小数精度，

依然可以正常训练和推理。

这就给低精度计算留下了巨大空间。

---

# 二十、那么 FP16 为什么也能训练？

当然也能。

但由于数值范围更窄：

> 某些训练场景更容易出现数值问题。

因此历史上常配合：

# Loss Scaling

---

# 二十一、Loss Scaling 的直觉

假设 Gradient 小到：

```text
0.00000001
```

FP16 很难舒服表示。

怎么办？

---

## 9. 先整体放大

例如乘：

```text
1000
```

变成：

```text
0.00001
```

先完成计算。

之后：

> 再按比例还原。

---

## 10. 就像称一个很轻的东西

一根针：

> 秤不准。

那先放：

> 1000 根针一起称。

最后除以：

> 1000。

这是 Loss Scaling 的第一层直觉。

---

# 二十二、这一阶段不要把 BF16 理解成“比 FP16 更高级”

这两个格式：

> 有不同设计取舍。

真正选哪个：

> 要考虑模型、硬件、训练方式和框架支持。

---

# 二十三、现在进入 INT8

到这里发生了一个重要变化。

FP32、FP16、BF16：

> 都属于 Floating Point。

INT8：

> Integer。

也就是整数表示。

---

# 二十四、问题来了

模型 Weight 明明可能是：

```text
0.0274

-0.931

1.274
```

整数怎么存？

难道全部直接变成：

```text
0
-1
1
```

吗？

如果真这么干：

> 信息会损失得非常严重。

---

# 二十五、所以 Quantization 的核心出现了

# Quantization

量化。

最简单理解：

> **不要直接粗暴删掉小数，而是先建立一把“缩放后的整数尺子”。**

---

# 二十六、一个最直观的温度计例子

假设一批 Weight 范围是：

```text
-1.0 ~ +1.0
```

我们只有有限个整数格子。

例如教学上只假设有：

```text
-4
-3
-2
-1
0
1
2
3
```

---

## 11. 我们可以规定

```text
整数 -4
≈ 原数 -1.0

整数 0
≈ 原数 0

整数 3
≈ 原数 0.75
```

等等。

于是原来的连续数字：

> 被吸附到最近的有限刻度。

---

# 二十七、量化像什么？

想象高清照片。

原图每个颜色：

> 可以有非常细的变化。

量化以后：

> 只允许从一组有限颜色中选择。

例如真实颜色：

```text
RGB某个非常精细的蓝
```

被近似到：

```text
“蓝色编号17”
```

---

# 二十八、这就是第四个核心心智模型

\[
\boxed{
Quantization
=
用更少的离散刻度，
近似原来更精细的Weight
}
\]

关键字是：

> **近似。**

不是：

> 完全无损。

---

# 二十九、为什么还要一个 Scale？

假设整数：

```text
23
```

它本身不知道代表：

> 0.23？

还是：

> 23？

还是：

> 2300？

所以还需要告诉系统：

> 这把整数尺子对应原始数字的比例是多少。

---

## 12. 可以把 Scale 理解成

> **尺子的单位说明。**

比如：

```text
1格 = 0.01
```

那么：

```text
23格
```

大约就是：

```text
0.23
```

---

# 三十、一个极简量化过程

原始 Weight：

```text
0.13
0.24
0.81
-0.42
```

先设一把合适的尺子。

然后变成概念上的：

```text
13
24
81
-42
```

再配：

```text
Scale = 0.01
```

运行时：

> 可以近似恢复需要的数值意义。

真实量化算法会复杂得多。

但这已经抓住核心。

---

# 三十一、为什么不能整台模型只用一个 Scale？

想象两个区域。

区域 A 的 Weight：

```text
-0.01 ~ 0.01
```

区域 B：

```text
-100 ~ 100
```

---

## 13. 如果强行共用同一把尺子

为了装下：

```text
100
```

尺子必须很粗。

结果区域 A：

> 大量细微差异全没了。

---

# 三十二、所以出现 Group-wise Quantization

可以粗略理解：

> 不同小组使用自己的尺子。

例如：

```text
Weight Group 1
→ Scale A

Weight Group 2
→ Scale B

Weight Group 3
→ Scale C
```

---

# 三十三、这就是为什么真实 4-bit 模型不正好等于“每参数 0.5 Byte”

因为除了 Weight 的低 bit 编码，

还可能需要保存：

```text
Scale
Zero Point
Group Metadata
其它量化信息
```

---

## 14. 所以

```text
7B × 0.5 Byte
≈ 3.5GB
```

只是：

> **Weight 编码的理论底线式估算。**

实际：

> 通常会稍大。

---

# 三十四、什么叫 Zero Point？

现在不需要深入公式。

用尺子理解就够了。

有些量化设计中：

```text
整数0
```

不一定对应：

```text
真实数字0
```

于是还需要一个：

# Zero Point

告诉系统：

> 整数尺子的“零刻度”对应哪里。

---

# 三十五、所以一套量化尺子可能包括

```text
Quantized Integer
+
Scale
+
有时 Zero Point
```

这已经足够支撑我们后面看 INT8/INT4。

---

# 三十六、INT8 有多少种基本编码状态？

8 bit 一共有：

```text
256
```

种二进制组合。

如果作为常见有符号整数理解：

> 大致可以覆盖 256 个整数状态。

---

# 三十七、INT4 呢？

4 bit 只有：

```text
16
```

种组合。

这是一个极其重要的直觉。

---

## 15. 从 FP16 到 INT4

你可以想象：

```text
原来有非常多可表达的细微数字
          ↓
现在每个4-bit编码
只有16种基本状态
```

所以为什么：

> 不能完全没有信息损失，

现在应该很直观了。

---

# 三十八、那为什么模型没有立刻坏掉？

这正是 Quantization 很神奇、也很实用的地方。

大模型内部有：

> 数十亿参数。

其中很多参数：

> 并不需要每一个都保留极端精细的小数。

---

## 16. 只要量化方法足够合理

整体网络行为：

> 可能仍然保留得相当好。

尤其某些：

> 推理任务和模型。

---

# 三十九、用“专家工资”类比

假设公司员工真实工资精确到：

```text
31,427.83元
28,719.24元
35,188.17元
```

但你只是要做：

> 公司总薪酬规模分析。

可能把它近似成：

```text
31.4k
28.7k
35.2k
```

结果仍然：

> 很接近。

---

## 17. 但如果你的任务是

> 精确发工资，

这种近似：

> 就不够了。

这说明：

\[
\boxed{
能不能量化
与
任务容忍度有关
}
\]

---

# 四十、同样的 4-bit 模型，不代表质量一定相同

这是很重要的一点。

两个都写：

```text
4-bit
```

不代表：

> 使用了完全一样的量化方法。

还可能不同在：

- Quantization Algorithm；
- Group Size；
- Calibration；
- Weight Distribution 处理；
- 哪些 Layer 保持高精度。

---

# 四十一、所以以后不要只问

> “这是几 bit？”

还要问：

> **怎么量化的？**

---

# 四十二、什么叫 Calibration？

有些量化方法在转换之前会观察：

> 模型真实数据运行时的数值范围。

例如拿一批有代表性的文本：

```text
模型跑一遍
↓
观察Activation / Weight行为
↓
决定怎样设置量化范围
```

这种用于确定量化参数的数据过程，可以和：

# Calibration

联系起来理解。

具体算法以后按需要再展开。

---

# 四十三、Weight-only Quantization

这是一个特别重要的概念。

假设我们说：

> “这是一个 4-bit 模型。”

很多情况下更准确的意思可能是：

> **模型 Weight 主要用 4-bit 保存。**

---

## 18. Attention 里的 Activation 呢？

可能：

> 仍然是 FP16 / BF16。

---

## 19. 某些计算呢？

可能会：

> 临时反量化到更高精度参与计算。

---

## 20. 某些 Layer 呢？

可能：

> 仍保持高精度。

---

# 四十四、第五个核心心智模型

\[
\boxed{
4bit模型
\neq
模型内部所有数字、所有运算、所有缓存
全部永久都是4bit
}
\]

这句话非常重要。

---

# 四十五、一个量化推理流水线

可以粗略想成：

```text
SSD / VRAM中的Weight
        │
        │ 4-bit压缩保存
        ▼
Quantized Weight
        │
        │ 计算时按需要解释/反量化
        ▼
更适合GPU计算的形式
        │
        ▼
Matrix Multiplication
```

具体 Kernel 可能比这个聪明很多。

但心智模型够用了。

---

# 四十六、为什么低 bit 会减少显存？

很简单。

原来：

```text
一个Weight
=
2 Bytes
```

变成：

```text
一个Weight
≈
0.5 Byte
```

模型有：

```text
70亿个Weight
```

这个差距：

> 非常巨大。

---

# 四十七、为什么低 bit 还可能更快？

这里不能简单说：

> “bit 越低一定越快。”

但一个重要潜在优势是：

> **需要从显存搬的数据变少。**

---

## 21. 第三课第一阶段说过

GPU 不仅要计算。

还要：

> 不断读取 Weight。

如果每个 Weight 更小：

> Memory Bandwidth 压力可能下降。

---

# 四十八、一个卡车类比

GPU 是工厂。

VRAM 是仓库。

每一步计算都要把 Weight：

> 运到工人手里。

---

### BF16

每辆货物：

> 2 个箱子。

### 4-bit

同一批信息压缩后：

> 大约半个箱子级别。

运输：

> 可能更轻。

---

## 22. 但如果还要复杂解压

也会增加：

> 额外计算。

所以最终快不快：

> 取决于硬件和实现。

---

# 四十九、不要形成一个错误公式

```text
4-bit
=
FP16速度 × 4
```

完全不能这么算。

---

# 五十、Quantization 解决的第一个问题：装得下

假设：

```text
24GB VRAM
```

有一个 14B 模型。

BF16 Weight 粗略：

```text
14B × 2 Bytes
≈ 28GB
```

光 Weight：

> 就超过 24GB。

---

## 23. 但如果是理想化 4-bit Weight

```text
14B × 0.5 Byte
≈ 7GB
```

加上额外量化信息、KV Cache、Runtime Buffer：

> 仍可能有很大空间。

这就是：

> 量化为什么能改变“能不能跑”的边界。

---

# 五十一、一个非常关键的现实区分

## Quantization 可以帮助：

```text
模型装进显存
```

但不能自动解决：

```text
Context太长
KV Cache太大
Batch太大
```

---

# 五十二、为什么？

因为你压缩的可能主要是：

# Weights

但 KV Cache：

> 可能仍然使用 BF16 / FP16 或其它格式。

Activation：

> 也可能不是 4-bit。

---

# 五十三、所以 4-bit 以后显存不是只剩 Weight

仍然是：

```text
VRAM
│
├── Quantized Weights
├── KV Cache
├── Activations
├── Temporary Buffers
└── Framework / Kernel Workspace
```

---

# 五十四、这会直接进入下一阶段

第三课第 7 阶段我们会真正建立：

# 显存账本

不是只算：

```text
Parameters × Bytes
```

而是开始看：

```text
Weights
+
KV Cache
+
Activations
+
Buffers
```

---

# 五十五、训练时为什么又复杂很多？

推理时，低 bit Weight：

> 非常有吸引力。

但训练时我们要：

> 更新参数。

---

## 24. Gradient 本身需要精度

Optimizer State：

> 也需要精度。

---

## 25. 如果什么都只保存 4-bit

训练中的细微更新：

> 很容易丢失。

---

# 五十六、一个很直观的例子

当前 Weight：

```text
1.000
```

Gradient 希望更新：

```text
-0.0001
```

如果你的数字尺子只有：

```text
1.0
0.9
0.8
...
```

那么：

```text
1.000 - 0.0001
```

仍然只能存：

```text
1.0
```

更新：

> 消失了。

---

# 五十七、所以训练经常使用 Mixed Precision

# Mixed Precision

意思不是：

> “随便混着算。”

而是：

> 不同部分根据需要使用不同精度。

---

## 26. 例如概念上

```text
某些Weight
→ BF16

某些关键累计
→ FP32

Activation
→ BF16

Optimizer State
→ 更高精度
```

具体训练方案：

> 会因框架和算法不同。

---

# 五十八、第六个辅助心智模型

\[
\boxed{
现代LLM系统通常不是“全模型一种dtype”
}
\]

而更像：

```text
Storage Precision
+
Compute Precision
+
Accumulation Precision
```

三者可以：

> 不完全一样。

---

# 五十九、什么叫 Accumulation Precision？

想象你要加：

```text
10000个很小的数字
```

每一个都只有：

```text
0.001
```

---

## 27. 如果累计用的尺子太粗

不断相加时：

> 小误差可能积累。

所以某些计算：

> 输入可以低精度，

但累计：

> 用更高精度。

---

# 六十、这就是为什么“模型是 BF16”这句话也可能过度简化

它可能只是告诉你：

> 主要 Weight / 计算使用 BF16。

但底层 Kernel：

> 可能有其它 Accumulation Precision。

---

# 六十一、现在认识 QLoRA 的名字，但今天不展开

第五课我们会详细学习：

# QLoRA

现在只建立一张图：

```text
Base Model Weight
      ↓
4-bit量化保存
      ↓
大部分Base Weight冻结
      ↓
旁边增加小型LoRA参数
      ↓
训练LoRA
```

---

# 六十二、为什么这很聪明？

因为原本：

> 14B / 32B Base Weight

太大。

量化以后：

> Base Model 显存下降。

同时只训练：

> 很少量 LoRA Parameter。

于是：

> 单卡或少量 GPU 能做原本很难做的微调。

---

# 六十三、但 QLoRA ≠ 把 4-bit Base Weight 直接随便更新

这一点先记住。

QLoRA 的核心路线是：

> **量化 Base Model + 训练低秩 Adapter。**

第五课再彻底拆。

---

# 六十四、采购 AI 的第一个实际选择场景

假设我们准备做：

# ProcurementLM Baseline

候选模型：

```text
7B Instruct
```

GPU：

```text
12GB VRAM
```

---

## 28. BF16 Weight

大约：

```text
14GB
```

已经很紧，甚至单看 Weight 就超过 12GB。

---

## 29. INT8 Weight

粗略：

```text
7GB
```

开始有空间。

---

## 30. 4-bit Weight

粗略：

```text
3.5GB+
```

空间明显宽松。

---

## 31. 于是你可能说

> “那永远选 4-bit 不就好了？”

这又错了。

---

# 六十五、为什么不永远 4-bit？

因为你还要考虑：

```text
Quality

速度

硬件支持

Kernel支持

任务难度

训练还是推理

量化方法
```

这是一个：

> Trade-off。

---

# 六十六、专业任务为什么尤其要做实测？

假设 4-bit 模型在普通聊天 Benchmark：

> 几乎没下降。

不代表在：

> 政府采购法规引用

这种高精度任务上：

> 一定完全一样。

---

## 32. 所以最后必须回到

# Gold Set

分别跑：

```text
BF16
INT8
4-bit
```

对同一批 Procurement Benchmark。

---

# 六十七、然后比较什么？

例如：

```text
风险分类准确率

法规依据正确率

引用完整率

漏报率

误报率

生成稳定性

显存

速度
```

---

# 六十八、这才是工程意义上的量化选择

不是：

> “网上都说 4-bit 好。”

而是：

```text
Memory Saved
+
Speed
+
Quality Loss
+
Business Risk
```

一起决策。

---

# 六十九、一个采购项目里非常现实的情况

模型 A：

```text
BF16
显存 20GB
准确率 92%
```

模型 B：

```text
4-bit
显存 8GB
准确率 91.8%
```

如果结果真的稳定：

> B 可能非常有吸引力。

---

## 33. 另一个情况

模型 B：

```text
显存 8GB
准确率 86%
法规引用错误显著增加
```

那便宜：

> 也不值得。

---

# 七十、所以 Quantization 是业务决策，不只是技术参数

\[
\boxed{
QuantizationDecision
=
Cost
\times
Latency
\times
Quality
\times
Risk
}
\]

不用背公式。

意思就是：

> 四件事要一起看。

---

# 七十一、再区分一个容易混淆的词：Precision 与 Accuracy

中文都容易说成：

> “精度”。

但含义不同。

---

## 34. Numeric Precision

这里讲的 FP16、BF16：

> **数字表示精细程度。**

---

## 35. Model Accuracy

例如：

> 分类准确率 92%。

这是：

> **模型任务表现。**

---

## 36. 所以

```text
Lower Numeric Precision
```

不一定意味着：

```text
Model Accuracy
```

按同样比例降低。

它们不是一回事。

---

# 七十二、一个特别重要的反例

从：

```text
FP32
```

降到：

```text
BF16
```

数字 bit 数：

> 减半。

是不是模型准确率：

> 也一定减半？

当然不是。

---

# 七十三、为什么？

模型有大量：

> 冗余和容错。

数值稍微近似：

> 整体函数仍可能很接近。

---

# 七十四、但也不能反过来极端

> “既然模型有容错，bit 越少越好。”

也不对。

低到一定程度：

> 误差会明显破坏模型。

---

# 七十五、这就是量化研究真正的问题

不是：

> 能不能少用 bit？

而是：

\[
\boxed{
少到什么程度，
模型仍然保留足够能力？
}
\]

---

# 七十六、一个“照片压缩”类比

原始照片：

> RAW。

---

## 37. 压成高质量 JPEG

文件小很多。

肉眼：

> 几乎看不出区别。

---

## 38. 再疯狂压缩

文件继续变小。

开始出现：

- 色块；
- 模糊；
- 细节丢失。

---

## 39. Quantization 也很像

```text
高精度Weight
     ↓
合理量化
     ↓
小很多，能力保持较好
     ↓
过度量化
     ↓
模型质量明显下降
```

---

# 七十七、但是照片类比有一个边界

神经网络：

> 不是图片。

量化误差会经过：

> 多层矩阵计算传播。

所以具体影响：

> 不能靠肉眼直觉判断。

必须：

# Benchmark

---

# 七十八、Outlier 为什么麻烦？

假设一组 Weight：

```text
0.1
0.2
0.15
0.12
0.18
50.0
```

最后：

```text
50.0
```

特别大。

它就是一个极端值：

# Outlier

---

## 40. 如果整组共用一把尺子

为了装下：

```text
50
```

量化范围必须拉得很宽。

于是：

```text
0.1
0.12
0.15
```

之间的细节：

> 很难保留。

---

# 七十九、一个身高尺类比

你想精确量：

> 1.60m～1.90m 的人。

结果队伍里突然有：

> 一栋 50 米建筑。

---

## 41. 如果同一把尺子必须覆盖

```text
0 ~ 50m
```

那普通人之间：

```text
1.71
1.72
1.73
```

的差别：

> 就变得很难刻精细。

---

# 八十、所以好的 Quantization 方法会想办法处理 Outlier

可能采用：

- 分组；
- 不同 Scale；
- 特定通道处理；
- 某些部分保留更高精度；

等等。

今天不用记算法名。

只记问题：

> **极端值会让低 bit 的有限刻度变得难分配。**

---

# 八十一、为什么 Layer-by-Layer 敏感度可能不同？

模型里不是每一层：

> 都同样耐量化。

---

## 42. 某些模块

量化以后：

> 几乎没影响。

另一些：

> 更敏感。

---

## 43. 因此一些量化方案可能选择

```text
大部分Layer → 4-bit

少数敏感Layer → 8/16-bit
```

这再次说明：

> “4-bit 模型”只是一个粗标签。

---

# 八十二、Embedding 和 LM Head 呢？

它们也可能：

> 采用不同策略。

不同实现：

> 不一定把模型所有矩阵同等处理。

---

# 八十三、KV Cache 也可以量化吗？

可以有这样的技术方向。

但不要和：

> Weight Quantization

混为一谈。

---

## 44. Weight Quantization

目标主要：

> 压模型参数。

---

## 45. KV Cache Quantization

目标主要：

> 压运行时 Context Cache。

这对：

> 长 Context / 高并发

特别有意义。

---

# 八十四、为什么这个区别以后很关键？

假设 4-bit 模型 Weight：

> 非常小。

但你跑：

```text
128K Context
×
很多并发用户
```

KV Cache：

> 可能变成主要显存消费者。

---

# 八十五、所以第三课第 7 阶段会出现一个重要转折

短 Context 时：

```text
Weights
```

可能是主要显存。

长 Context、高并发时：

```text
KV Cache
```

可能越来越重要。

---

# 八十六、再认识一个概念：Compute dtype

例如 Weight：

```text
4-bit
```

不代表矩阵乘法一定：

> 用 4-bit 直接完成所有步骤。

---

## 46. 某些方案可能

```text
4-bit Weight
↓
转换/解释成 BF16
↓
与 BF16 Activation 计算
```

所以：

```text
Weight dtype
≠
Compute dtype
```

这是非常重要的区分。

---

# 八十七、再加一个：Output dtype

结果 Tensor：

> 又可能是另一种 dtype。

于是完整一点：

```text
Storage dtype
      ↓
Compute dtype
      ↓
Accumulation dtype
      ↓
Output dtype
```

不一定全部相同。

---

# 八十八、为什么 GPU 型号会影响 dtype 选择？

因为不同硬件：

> 对不同数字格式的原生支持和性能不同。

---

## 47. 有的硬件

BF16：

> 支持很好。

有的旧硬件：

> 支持有限。

---

## 48. 某些低 bit 推理

还依赖：

> 特定高效 Kernel。

所以不能只从：

> 数学位数

决定最终性能。

---

# 八十九、这就是为什么模型部署不能只看“显存能不能装下”

还要问：

```text
这个GPU对这种dtype快不快？

推理框架支持好吗？

量化Kernel成熟吗？
```

---

# 九十、一个 ProcurementAI 生产决策例子

你有两个部署方案。

### 方案 A

```text
BF16
需要2张GPU
```

### 方案 B

```text
4-bit
只需要1张GPU
```

---

## 49. 不应该立刻选 B

你还要比较：

```text
采购审查准确率

法规引用正确率

延迟

吞吐

并发

硬件成本

稳定性
```

最后才决定。

---

# 九十一、为什么这一课不直接告诉你“最佳 dtype”？

因为不存在：

> 永远最佳。

---

## 50. 推理

与：

> 训练

可能不同。

---

## 51. 单卡本地测试

与：

> 大规模生产

可能不同。

---

## 52. 普通聊天

与：

> 政府采购法规审查

容错也不同。

---

# 九十二、一个以后非常实用的判断顺序

选择精度时，可以先问：

```text
第一问：
这是训练还是推理？

第二问：
GPU原生支持什么？

第三问：
模型多大，显存多少？

第四问：
允许多大质量损失？

第五问：
有没有自己的Gold Set验证？
```

这比背：

> “某某 bit 最好”

有用得多。

---

# 九十三、把 FP32、FP16、BF16、INT8、INT4 放回一张地图

```text
更多bit
▲
│
│  FP32
│   │
│   ├─ 数值信息丰富
│   └─ 内存大
│
│  FP16 / BF16
│   │
│   ├─ 2 Bytes/参数
│   └─ 现代LLM常见低精度浮点
│
│  INT8
│   │
│   ├─ 1 Byte/参数级别
│   └─ 需要Quantization映射
│
│  INT4 / 4-bit
│   │
│   ├─ 约0.5 Byte/参数级别
│   ├─ Weight显著压缩
│   └─ 更依赖良好Quantization方法
│
▼
更少bit
```

这不是“质量排行榜”。

而是：

> 数字表示压缩程度的地图。

---

# 九十四、本阶段五个核心心智模型总结

| 核心心智模型 | 你真正应该带走什么 |
|---|---|
| **① bit / byte 是数字包装尺寸** | 32 bit=4 Bytes，16 bit=2 Bytes，8 bit=1 Byte |
| **② 参数量 × 每参数空间决定 Weight 数量级** | 7B 本身不是 GB；dtype 才决定它大约占多少 |
| **③ FP16 与 BF16 是不同的 16-bit 尺子** | 都占 2 Bytes，但对范围与细节的分配不同 |
| **④ Quantization 是有限刻度近似** | INT8/INT4 用 Scale 等方式近似原始 Weight，不是魔法无损压缩 |
| **⑤ 4-bit Weight ≠ 全系统4-bit** | Activation、KV Cache、计算和累计可能仍使用更高精度 |

---

# 九十五、三个辅助心智模型

### 辅助模型 A

```text
Parameter Count
=
有多少件货

dtype
=
每件货有多大
```

---

### 辅助模型 B

```text
Quantization
=
把高清数字
吸附到有限刻度
```

---

### 辅助模型 C

```text
Lower Precision
=
Memory ↓

但不自动意味着：
Quality按同比例 ↓
或者
Speed按同比例 ↑
```

---

# 九十六、ProcurementLM 显存粗算练习 1

模型：

```text
7B
```

FP32。

只看 Weight：

> 大约多少？

答案：

```text
约28GB
```

---

# 九十七、练习 2

同一个：

```text
7B
```

BF16。

大约：

```text
14GB
```

---

# 九十八、练习 3

INT8。

大约：

```text
7GB
```

---

# 九十九、练习 4

理想化 4-bit Weight。

大约：

```text
3.5GB
```

实际：

> 要再给 Scale、Metadata、Runtime 等留空间。

---

# 一百、练习 5

14B BF16。

粗略：

```text
14B × 2 Bytes
≈ 28GB
```

一张：

```text
24GB GPU
```

光 Weight：

> 就已经不舒服，甚至装不下。

---

# 一百零一、练习 6

14B 4-bit。

理论 Weight：

```text
约7GB
```

是不是说明 8GB GPU 一定能完美跑？

**不是。**

因为还有：

```text
量化Metadata
+
KV Cache
+
Activation
+
Runtime Buffer
```

---

# 一百零二、思维实验 A

模型从 BF16 换成 INT4。

Parameter Count 有没有变？

**没有。**

还是：

```text
7B
```

改变的是：

> 参数的存储表示。

---

# 一百零三、思维实验 B

一个 7B 4-bit 模型。

是不是“只有 17.5 亿参数”？

不是。

仍然：

> 约 70 亿参数。

只是：

> 每个参数使用更紧凑的表示。

---

# 一百零四、思维实验 C

BF16 和 FP16 都占 14GB 左右的 7B Weight。

是不是它们完全一样？

不是。

它们：

> bit 数相同，

但：

> 数值格式设计不同。

---

# 一百零五、思维实验 D

4-bit 模型比 BF16 小约很多。

是不是任务准确率必然下降同样比例？

当然不是。

Numeric Precision：

> 和业务 Accuracy 不是线性对应。

---

# 一百零六、思维实验 E

4-bit Weight 已经很小。

长文档却仍然 CUDA OOM。

有没有可能？

完全可能。

因为：

> KV Cache 随 Context 增长。

---

# 一百零七、思维实验 F

两个模型都叫：

```text
4-bit
```

是不是业务表现一定一样？

不是。

还取决于：

- 原始模型；
- 量化算法；
- Group；
- Calibration；
- 保留高精度的模块；
- Runtime 实现。

---

# 一百零八、这一阶段最容易犯的七个错误

### 错误 1

> 7B = 7GB。

错。

---

### 错误 2

> BF16 和 FP16 都是 16-bit，所以完全相同。

错。

---

### 错误 3

> INT4 就是把所有小数直接四舍五入成整数。

错。

真实量化需要：

> Scale 等映射机制。

---

### 错误 4

> 4-bit 模型里所有 Tensor 都是 4-bit。

错。

---

### 错误 5

> 4-bit 一定比 BF16 快 4 倍。

错。

---

### 错误 6

> 4-bit 质量一定很差。

也不能这样武断。

必须：

> 实测。

---

### 错误 7

> Weight 装下了，显存问题就结束了。

错。

还有：

> KV Cache、Activation、Buffer。

---

# 一百零九、把第 3～6 阶段串起来

第三阶段：

```text
Weights到底是什么文件？
```

第四阶段：

```text
Weights怎么进RAM / VRAM？
```

第五阶段：

```text
Weights怎么参与生成？
```

第六阶段：

```text
每个Weight到底占多大空间？
```

所以我们现在已经从：

> “模型文件”

一路走到了：

> “显存容量”。

---

# 一百一十、第 6 阶段掌握标准

这一阶段学完以后，你应该能不用背教材，自己解释：

> bit 和 Byte 什么关系？

> 为什么 7B 不等于 7GB？

> 为什么 FP32 的 7B Weight 粗略是 28GB？

> 为什么 BF16 / FP16 大约只有一半？

> FP16 与 BF16 明明都是 16 bit，为什么还不同？

> Exponent 和 Fraction 的直觉分别是什么？

> Overflow / Underflow 是什么？

> 为什么训练很关心数值范围？

> INT8 / INT4 为什么不能简单理解成“删掉小数”？

> Quantization 的核心思想是什么？

> Scale 可以用什么生活类比解释？

> 为什么 Group-wise Quantization 有意义？

> 为什么 Outlier 会让量化变困难？

> 为什么真实 4-bit 模型会比 `参数数 × 0.5 Byte` 稍大？

> 为什么 Weight Quantization 和 KV Cache Quantization 不是一回事？

> 为什么 4-bit Weight 不意味着 Activation 也是 4-bit？

> Weight dtype 与 Compute dtype 为什么可能不同？

> Mixed Precision 为什么存在？

> QLoRA 为什么和“量化 Base + 训练 LoRA”有关？

> 为什么选择 dtype 最终必须回到 Procurement Gold Set？

如果这些问题已经可以自己从直觉上回答：

\[
\boxed{
第三课第6阶段真正建立起来了
}
\]

---

# 一百一十一、这一阶段真正只记一句话

> **模型有多少参数，决定“有多少数字”；FP32、BF16、INT8、INT4 决定“这些数字用多精细、多大的盒子来保存”。量化就是用更少的有限刻度近似原来的高精度 Weight，用一定数值误差换取显著的存储和显存节省。**

最后把整张地图压成：

```text
             7B Parameters
                   │
                   ▼
          每个参数怎么保存？
                   │
       ┌───────────┼───────────┐
       │           │           │
       ▼           ▼           ▼
     FP32      FP16/BF16     Quantized
    4Bytes       2Bytes        │
                               ├─ INT8
                               │   ≈1Byte
                               │
                               └─ INT4
                                   ≈0.5Byte
                                      │
                                      ▼
                                  Scale / Group
                                      │
                                      ▼
                              用更少刻度近似原值
```

# 下一阶段：第三课 · 第 7 阶段
## 一张 GPU 到底能不能装下一个模型？第一次建立完整“显存账本”

下一阶段我们不会再只算：

```text
Parameters × Bytes
```

而是第一次把显存拆成真正的四个账户：

```text
VRAM
│
├── ① Model Weights
├── ② KV Cache
├── ③ Activations
└── ④ Runtime / Temporary Buffers
```

然后拿具体例子算：

```text
7B
14B
32B
```

分别在：

```text
BF16
INT8
4-bit
```

下大概是什么数量级。

更重要的是，我们会第一次回答一个真正工程化的问题：

> **“我有一张 24GB GPU，到底应该选多大的 ProcurementLM？”**

以及：

> **为什么一个 7B 模型明明 Weight 只有 14GB，Context 拉长以后还是会 OOM？**

到了第 7 阶段，我们就会真正拥有一张可以用于以后选 GPU、选模型、选量化方式的**显存账本**。

---

<!-- LESSON 03 STAGE 06 END -->


<!-- LESSON 03 STAGE 07 START -->

# 第三课 · 第 7 阶段：第一次建立完整“显存账本”
## 一张 GPU 到底能不能装下一个模型？为什么 Weight 明明放得下，Context 一长还是会 CUDA OOM？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Serving VRAM ≠ Weight VRAM。完整显存账本至少包括 Weights + KV Cache + Activations/Workspace + Runtime Overhead。**
2. **Context Length 增长会显著扩大 KV Cache；“模型刚加载成功”不代表长上下文时仍不会 OOM。**
3. **Batch / Concurrency 会让多个请求同时占用 KV Cache，因此单请求显存不能直接代表服务显存。**
4. **OOM 可能发生在生成过程中而不是加载阶段，所以显存预算必须覆盖真实 Workload Shape。**
5. **专业显存预算必须留 Headroom，不能把理论可用显存全部吃满。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `CUDA` | CUDA：NVIDIA GPU 通用并行计算平台与软件生态 |
| `KV Cache` | KV 缓存：生成时缓存历史 Key/Value 以减少重复计算 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Batch` | 批次：一次参与计算的一组样本 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `VRAM` | 显存：GPU 上存放权重、激活和 KV Cache 等的高速内存 |
| `BF16` | BF16：保留较大指数范围的 16 位浮点，常用于大模型 |
| `Attention` | 注意力：根据内容相关性动态聚合信息 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |
| `Query` | Query/Q：当前 Token 表示“我要找什么”的向量 |
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

第 6 阶段我们已经学会了第一笔账：

```text
参数量
×
每个参数占多少 Bytes
≈
模型 Weight 大小
```

例如：

```text
7B BF16
≈ 14GB Weight
```

很多人学到这里，就开始产生一个错误直觉：

> “我有 24GB 显存，14GB 模型当然随便跑。”

问题就在这里。

因为 GPU 显存不是只租给：

> **Model Weight。**

它还要住很多别的东西。

今天我们真正要建立的是一张完整账本：

```text
                    24GB VRAM
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
   Model Weight       KV Cache        Activations
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ▼
                 Runtime / Buffers
```

这一阶段真正需要带走 **5 个核心心智模型**：

```text
① VRAM 是一个共享预算，不是“模型专用仓库”

② Weight 是固定房租
   KV Cache 是按 Context 和用户数增长的住宿费

③ Context 越长，KV Cache 越大

④ Batch / 并发越高，KV Cache 基本也跟着放大

⑤ “刚好装下”不是好的部署方案
   必须给运行时留下安全余量
```

这一阶段公式会有，但只保留**真正能帮你判断显存的两个公式**。

先从直觉开始。

---

# 一、把显存想成一家酒店

假设你买了一张：

# 24GB VRAM

的 GPU。

就像你有一家：

> **24GB 容量的酒店。**

现在有四类客人要入住。

---

## 1. 第一类客人：Model Weights

这是模型本体。

比如：

```text
7B BF16
≈ 14GB
```

它们一旦模型加载好：

> 基本长期住在酒店里。

---

## 2. 第二类客人：KV Cache

这是模型针对：

> **当前正在处理的 Context**

保存的注意力历史。

用户输入越长：

> 它越大。

模型生成越长：

> 它继续变大。

---

## 3. 第三类客人：Activations

Transformer 正在计算时：

> 会产生各种中间结果。

这些结果不能凭空消失。

计算到某些阶段：

> 需要暂时存在显存里。

---

## 4. 第四类客人：Runtime / Temporary Buffers

GPU Kernel、推理框架、矩阵乘法等：

> 还可能需要临时工作区。

于是：

```text
24GB
```

绝对不能简单理解成：

```text
可以装24GB Weight
```

---

# 二、第一个核心心智模型：显存是一张预算表

以后看到一张 GPU，脑子里不要再只有：

```text
VRAM
=
Weights
```

而是：

```text
VRAM
=
┌─────────────────────────┐
│ ① Weights               │
├─────────────────────────┤
│ ② KV Cache              │
├─────────────────────────┤
│ ③ Activations           │
├─────────────────────────┤
│ ④ Runtime / Workspace   │
└─────────────────────────┘
```

这四个账户：

> **抢的是同一块显存。**

---

# 三、先把最容易算的 Weight 算清楚

这个第 6 阶段已经学过。

我们今天直接做一张表。

| 模型参数量 | BF16/FP16 Weight | INT8 粗估 | 4-bit Weight 理论粗估 |
|---|---:|---:|---:|
| 7B | 约 14GB | 约 7GB | 约 3.5GB |
| 14B | 约 28GB | 约 14GB | 约 7GB |
| 32B | 约 64GB | 约 32GB | 约 16GB |

先再次强调：

> 这是 **Weight 数量级**。

不是：

> 最终运行显存。

---

# 四、现在拿一张 24GB GPU 做第一次判断

## 5. 7B BF16

Weight：

```text
约14GB
```

24GB 减去 14GB：

```text
还剩约10GB
```

这些空间可以继续给：

- KV Cache；
- Activations；
- Runtime。

所以：

> **中等 Context、较小 Batch 下，通常是一个比较合理的单卡推理候选。**

---

# 五、14B BF16 呢？

Weight：

```text
约28GB
```

你的 GPU：

```text
24GB
```

甚至还没开始处理 Prompt：

> Weight 自己就放不下。

所以：

```text
14B BF16
→ 单24GB GPU
→ 单看Weight就不成立
```

这个判断甚至：

> 不需要跑代码。

---

# 六、如果 14B 改成 INT8 呢？

Weight：

```text
约14GB
```

这时候突然：

> 又有机会了。

剩下大约：

```text
10GB级别空间
```

给其它账户。

---

# 七、如果 14B 改成 4-bit 呢？

Weight 理论粗估：

```text
约7GB
```

显存空间明显更宽松。

但是千万别马上说：

> “那一定可以跑 128K Context。”

因为：

> **KV Cache 还没算。**

---

# 八、这就是第二个核心心智模型

可以把 Weight 看成：

# 固定房租

模型一旦选定：

```text
7B
14B
32B
```

再选定 Weight Precision：

```text
BF16
INT8
INT4
```

Weight 占用：

> 大致就定下来了。

---

## 8. KV Cache 则完全不同

它像：

# 按入住人数和住宿天数收费

Context 越长：

> 越大。

同时服务用户越多：

> 越大。

这两个变量特别重要。

---

# 九、重新认识 KV Cache

第五阶段我们已经知道：

生成过程分成：

```text
Prefill
↓
建立过去Token的K/V
↓
Decode
↓
复用过去K/V
```

如果不保存 K/V：

> 每生成一个新 Token，都得把过去大量 Attention 信息重新计算。

所以：

# KV Cache 是用显存换速度

---

# 十、一个 ProcurementAI 场景

用户上传一份采购文件。

### 用户 A

文件很短：

```text
2,000 Token
```

---

### 用户 B

文件很长：

```text
32,000 Token
```

---

### 用户 C

一次塞入：

```text
128,000 Token
```

虽然使用的：

> 是同一个模型，

模型 Weight：

> 一模一样，

但三个人的 KV Cache：

> 完全不同。

---

# 十一、用会议秘书继续理解

假设一个专家团队有：

> 32 层 Transformer。

每一层：

> 都有自己的 Attention。

秘书读一个 Token：

> 每一层都要留下部分 K/V 记录。

所以一份文档从：

```text
1,000 Token
```

增长到：

```text
32,000 Token
```

不是只多存：

> 一份笔记。

而是：

> **每一层都在增加自己的 K/V 历史。**

---

# 十二、KV Cache 受哪些东西影响？

先不要看公式。

只看这张图：

```text
KV Cache
│
├── 模型有多少层
│
├── Context有多少Token
│
├── 有多少KV Heads
│
├── 每个Head多宽
│
├── 每个数占多少Bytes
│
└── 同时有多少条Sequence
```

所以：

> KV Cache 不是只由模型 B 数决定。

---

# 十三、为什么 GQA 又回来了？

第二课 Self-Attention 学过：

```text
MHA
Query Heads很多
Key Heads很多
Value Heads很多
```

而：

```text
GQA
Query Heads很多
但多个Query Head共享较少的K/V Heads
```

---

## 9. 当时可能觉得

> “这只是 Attention 架构细节。”

现在终于看到工程意义：

> **K/V Head 越少，需要缓存的 K/V 就越少。**

---

# 十四、一个特别直观的例子

假设：

```text
Query Heads = 32
```

### 普通 MHA

```text
KV Heads = 32
```

---

### GQA

```text
KV Heads = 8
```

那么 KV Cache 中的 Head 数：

> 直接少到四分之一。

这就是为什么：

> GQA 对长 Context 和推理部署特别有价值。

---

# 十五、现在才看第一个真正有用的公式

KV Cache 的粗略容量可以理解为：

\[
\boxed{
KV
\approx
2
\times
L
\times
S
\times
H_{KV}
\times
d_h
\times
B
\times
Bytes
}
\]

别背。

我们逐个翻译。

---

# 十六、公式里的 `2` 是谁？

因为缓存两样东西：

```text
K
+
V
```

所以：

```text
2
```

---

# 十七、`L` 是什么？

```text
L
=
Transformer Layers
```

例如：

```text
32层
```

每一层：

> 都需要自己的 KV Cache。

---

# 十八、`S` 是什么？

```text
S
=
Sequence Length
```

也就是当前 Context 中：

> 大约多少 Token。

---

# 十九、`H_KV` 是什么？

```text
KV Head数量
```

比如：

```text
8
```

---

# 二十、`d_h` 呢？

每一个 Attention Head：

> 有多少维。

例如：

```text
128
```

---

# 二十一、`Bytes` 是什么？

如果 K/V 使用：

```text
BF16
```

每个数字：

```text
2 Bytes
```

---

# 二十二、最后的 `B`

这是：

# Batch / 同时活跃的 Sequence 数

先简单理解：

> 一次同时在为多少条序列保存 KV。

---

# 二十三、现在不要算大模型，先算一个特别整齐的教学模型

假设：

```text
Layers       = 32
KV Heads     = 8
Head Dim     = 128
KV dtype     = BF16 = 2 Bytes
Batch        = 1
```

只改变：

> Context Length。

---

# 二十四、Context = 8K

大约：

```text
8192 Token
```

代入后：

> KV Cache 大约 **1 GiB**。

先别管计算过程。

只记：

```text
8K Context
→ 约1GB KV Cache
```

对于这个教学架构。

---

# 二十五、如果 Context 变成 32K 呢？

32K：

> 是 8K 的 4 倍。

于是 KV Cache：

```text
约4GB
```

---

# 二十六、如果 Context = 128K？

128K：

> 是 8K 的 16 倍。

KV：

```text
约16GB
```

---

# 二十七、停一下，看这张表

仍然是：

> **完全同一个模型。**

| Context | KV Cache 粗估 |
|---|---:|
| 8K | 约 1 GiB |
| 32K | 约 4 GiB |
| 128K | 约 16 GiB |

这就是为什么：

> **Context Length 本身就是显存变量。**

---

# 二十八、现在用 24GB GPU 重做 7B BF16 案例

假设：

```text
Weights
≈ 14GB
```

GPU：

```text
24GB
```

---

## 10. 8K Context

粗略：

```text
Weights       14GB
KV Cache       1GB
------------------
≈15GB
```

还没算：

- Activations；
- Runtime；
- Buffer。

但总体：

> 有较明显余量。

---

# 二十九、换成 32K Context

```text
Weights       14GB
KV Cache       4GB
------------------
≈18GB
```

剩余空间：

> 明显变少。

---

# 三十、换成 128K Context

```text
Weights       14GB
KV Cache      16GB
------------------
≈30GB
```

已经超过：

```text
24GB
```

还没算其它东西。

于是：

# CUDA OOM

完全不奇怪。

---

# 三十一、所以第三个核心心智模型

\[
\boxed{
Context越长
\Rightarrow
KVCache越大
}
\]

而且在其它条件固定时：

> 大体是线性增长。

---

# 三十二、这解释了一个以前很奇怪的现象

用户说：

> “模型昨天明明能跑，今天怎么 OOM 了？”

可能模型：

> 完全没变。

只是昨天输入：

```text
3页采购条款
```

今天输入：

```text
400页采购文件
```

---

# 三十三、所以排查 OOM 时必须问

不要只问：

> “模型多大？”

还要问：

```text
Context多长？
```

这是非常重要的诊断习惯。

---

# 三十四、第四个核心心智模型：并发也要吃 KV

刚才全部是：

```text
Batch = 1
```

也就是：

> 只有一条 Sequence。

---

## 11. 如果同时 4 个请求呢？

还是刚才：

```text
8K Context
```

单条大约：

```text
1GB KV
```

四条类似请求：

> KV 总需求可能接近约 4GB 量级。

---

# 三十五、32K Context × 4 条呢？

一条：

```text
约4GB
```

四条：

```text
约16GB
```

---

# 三十六、这就是为什么“单用户能跑”完全不等于“能生产部署”

本地测试：

```text
1个用户
```

感觉：

> 非常顺。

上线以后：

```text
10个用户
50个用户
100个用户
```

突然：

> 显存完全是另一回事。

---

# 三十七、政府采购系统特别容易遇到这个问题

因为用户输入不是普通一句聊天。

可能是：

```text
采购需求
+
招标文件
+
评分办法
+
供应商材料
+
RAG法规证据
```

单请求本来：

> 就很长。

再加并发：

> KV Cache 压力会非常明显。

---

# 三十八、把生产推理想成酒店

Weight：

> 酒店建筑本身。

只有一份。

---

## 12. 每个用户进来

都会拿一个房间：

> 放自己的 KV Cache。

所以：

```text
更多用户
=
更多KV房间
```

---

# 三十九、Weight 不会因为用户翻倍而简单翻倍

如果同一个模型服务 10 个用户：

> 不需要复制 10 份 Weight。

模型 Weight：

> 可以共享。

---

# 四十、但是 KV Cache 是请求私有的

用户 A：

> 有自己的对话历史。

用户 B：

> 有自己的采购文件。

用户 C：

> 有自己的 Token Sequence。

这些不能：

> 全部混成同一个 KV Cache。

---

# 四十一、所以生产系统显存结构更像这样

```text
                     GPU VRAM
                         │
       ┌─────────────────┴────────────────┐
       │                                  │
       ▼                                  ▼
  Shared Model Weight               Per-request KV
                                      │
                         ┌────────────┼────────────┐
                         ▼            ▼            ▼
                       User A       User B       User C
```

这张图非常重要。

---

# 四十二、为什么 vLLM 以后会重要？

现在先不展开技术细节。

传统 KV Cache 管理可能：

> 出现大量内存碎片、预留浪费。

vLLM 等推理框架会想办法：

> 更高效地管理 KV Cache。

后面第 9 阶段会进一步讲：

# PagedAttention

---

# 四十三、现在进入第三个账户：Activations

Activation 是什么？

第二课已经学过。

例如：

```text
Token Embedding
↓
Attention输出
↓
MLP中间结果
↓
下一层Hidden State
```

这些：

> 都是中间计算结果。

---

# 四十四、用办公室类比

Weights：

> 员工长期知识。

KV Cache：

> 当前项目的会议笔记。

Activations：

> **员工现在桌面上正在计算的草稿纸。**

---

# 四十五、推理时 Activation 为什么不像训练那么夸张？

因为推理：

> 不需要为 Backprop 保存所有中间结果。

算完一部分：

> 很多临时 Activation 可以被释放或复用。

---

# 四十六、训练就完全不同

训练还要：

```text
Forward
↓
保存很多中间结果
↓
Backward
↓
计算Gradient
```

为了 Backward：

> 必须保留更多 Activation。

这就是训练显存远大于纯推理的重要原因之一。

---

# 四十七、所以我们先明确

今天这张显存账本：

> 主要先用于 **Inference**。

训练显存：

> 要额外再加很多账户。

---

# 四十八、Activation 受什么影响？

一个很实用的直觉：

```text
Batch越大
↓
同时算的数据越多
↓
Activation通常越大
```

Context 越长：

> 也会增加中间 Tensor。

---

# 四十九、所以 Batch Size 是双重压力

它可能同时让：

```text
KV Cache ↑
```

和：

```text
Activations ↑
```

---

# 五十、第四个账户：Runtime / Temporary Buffers

这类最容易被初学者忽略。

你可能粗算：

```text
Weights = 14GB
KV      = 4GB
合计     = 18GB
```

然后说：

> “24GB 肯定够，还有 6GB。”

---

## 13. 但 GPU 运行矩阵 Kernel

可能还需要：

- Workspace；
- CUDA Context；
- Kernel 临时 Buffer；
- Framework 内存；
- 内存对齐；
- 已缓存未立即归还的分配。

所以：

> 实际 `nvidia-smi` 看到的显存可能更高。

---

# 五十一、这就是第五个核心心智模型

## 不要把 GPU 用到 100% 才叫“充分利用”

生产环境真正希望的是：

> 有余量。

因为：

- Prompt 长度会波动；
- 并发会波动；
- Kernel 有临时峰值；
- 某些请求输出更长。

---

# 五十二、一个停车场类比

你有：

```text
100个停车位
```

如果日常运营计划就是：

```text
100辆车
```

看起来：

> 利用率 100%。

但第 101 辆临时车来了：

> 整个系统没有任何余地。

---

## 14. 更健康的方案

应该给：

- 临时车辆；
- 救援车辆；
- 施工车辆；

留下空间。

显存也是一样。

---

# 五十三、所以工程上不要问

> “理论上能不能塞进 24GB？”

而应该问：

> **“在我的 Context、Batch、并发和生成长度下，是否能稳定运行？”**

这句话比：

> “能跑”

专业很多。

---

# 五十四、现在建立正式“显存账本”

以后看到一个推理任务，先写：

```text
┌───────────────────────────────────┐
│       Inference VRAM Ledger       │
├───────────────────────────────────┤
│ Model Weights                     │
│ + Quantization Metadata           │
├───────────────────────────────────┤
│ KV Cache                          │
├───────────────────────────────────┤
│ Activations                       │
├───────────────────────────────────┤
│ Runtime / Kernel Workspace        │
├───────────────────────────────────┤
│ Safety Headroom                   │
└───────────────────────────────────┘
```

这就是本阶段的核心工具。

---

# 五十五、ProcurementLM 案例一：7B BF16 + 24GB

假设：

```text
Model      = 7B
Weight     = BF16
GPU        = 24GB
Context    = 8K
Batch      = 1
```

---

## 15. Weight

粗略：

```text
14GB
```

---

## 16. KV

假设模型架构接近我们刚才教学例子：

```text
约1GB
```

---

## 17. 于是基础账面

```text
14GB
+1GB
≈15GB
```

还剩：

> 一些明显空间。

所以这是：

> 一个看起来比较健康的起点。

---

# 五十六、如果同一个模型 Context 改成 32K？

KV：

```text
约4GB
```

变成：

```text
14GB Weights
+
4GB KV
=
约18GB
```

---

## 18. 还能不能跑？

有可能。

但相比 8K：

> 安全余量明显减少。

此时需要真实测：

- Runtime；
- Actual KV dtype；
- Framework；
- Output Length。

---

# 五十七、如果变成 128K？

刚才的教学架构：

```text
KV约16GB
```

Weight：

```text
14GB
```

合计：

```text
约30GB
```

于是单 24GB：

> 从账本上就已经宣告失败。

不需要等程序 OOM 才知道。

---

# 五十八、ProcurementLM 案例二：14B BF16 + 24GB

只看：

```text
Weights ≈ 28GB
```

所以：

> 直接淘汰单卡 BF16 方案。

---

# 五十九、改成 14B INT8

Weight：

```text
约14GB
```

这时：

> 重新有空间给 KV Cache。

对于适中 Context：

> 可能进入候选区。

---

# 六十、改成 14B 4-bit

Weight 粗略：

```text
约7GB+
```

显存压力大幅下降。

这时：

> Context 和 KV Cache 的预算地位开始明显上升。

---

# 六十一、这个现象非常重要

高精度大模型时：

```text
Weight
```

往往是最大块。

量化以后：

```text
Weight ↓↓↓
```

于是其它账户：

```text
KV Cache
Activations
Buffers
```

占比：

> 开始越来越显眼。

---

# 六十二、所以量化会“移动瓶颈”

这句话非常专业，也非常重要：

\[
\boxed{
Quantization
\neq
消灭显存瓶颈
}
\]

它经常只是：

> **把瓶颈从 Weight 推向 KV Cache / Runtime。**

---

# 六十三、ProcurementLM 案例三：32B 4-bit + 24GB

Weight 理论粗估：

```text
约16GB
```

加上量化 Metadata：

> 会再多一些。

---

## 19. 于是很多人会说

> “24GB 能跑 32B 4-bit！”

更准确的说法应该是：

> **在某些量化格式、推理框架、较小 Context、较低并发和合适配置下，可能有机会。**

---

# 六十四、为什么要说得这么谨慎？

因为剩下的：

```text
约8GB级别
```

不是全给你随便用。

还要分：

```text
KV
+
Activation
+
Runtime
```

---

# 六十五、如果再塞 32K 或更长 Context

显存：

> 很可能迅速吃紧。

---

# 六十六、所以“某张卡能跑某模型”这句话缺了很多参数

完整问题应该是：

```text
什么模型？
什么量化？
什么Context？
什么Batch？
多少并发？
什么推理框架？
生成多长？
```

如果这些都没说：

> “能跑”

的信息量其实很低。

---

# 六十七、现在比较三个模型在 24GB 上的直觉

### 7B BF16

```text
Weight约14GB
```

优势：

> 高精度 Weight，空间尚可。

---

### 14B 4-bit

```text
Weight约7GB+
```

优势：

> 模型参数更多，但经过量化。

---

### 32B 4-bit

```text
Weight约16GB+
```

优势：

> 模型更大。

但：

> Context 和 Runtime 余量更紧。

---

# 六十八、哪个一定最好？

没有答案。

因为：

```text
Model Size
≠
Business Quality
```

而：

```text
Lower Quantization
≠
Free Lunch
```

所以最后还是要：

# Benchmark

---

# 六十九、政府采购业务不能只看“能装最大的模型”

假设方案 A：

```text
32B 4-bit
Context只能勉强8K
```

方案 B：

```text
14B 4-bit
Context可以舒服32K
```

如果你的任务是：

> 审查 200 页招标文件，

方案 B：

> 可能反而更有业务价值。

---

# 七十、这就是系统设计思维

不是：

```text
最大模型
=
最好系统
```

而是：

```text
模型能力
×
Context能力
×
速度
×
并发
×
稳定性
×
业务准确率
```

一起看。

---

# 七十一、一个特别容易忽略的问题：Output Token 也占 Context

假设 Prompt：

```text
30K Token
```

模型最大窗口：

```text
32K
```

你觉得：

> “还有 2K。”

没错。

但如果希望生成：

```text
4K Output
```

那就：

> 不够。

---

# 七十二、而且生成中的 Output 也会增加 KV Cache

模型每生成：

> 一个新 Token，

也需要：

> 把这个 Token 的 K/V 加入 Cache。

所以：

```text
KV Cache
```

不仅由输入长度决定。

更准确：

```text
当前Context
=
Input Tokens
+
Generated Tokens
```

---

# 七十三、一个采购报告案例

输入：

```text
20K Token招标文件
```

RAG：

```text
5K Token法规证据
```

System + Prompt：

```text
1K
```

希望输出：

```text
4K Token风险报告
```

总 Context：

```text
约30K
```

这才是：

> 实际预算。

---

# 七十四、所以 Context Budget 和 VRAM Budget 是连在一起的

```text
更多RAG证据
      ↓
更多Token
      ↓
更大KV Cache
      ↓
更大VRAM需求
```

---

# 七十五、这解释了为什么 RAG 不是“文档塞越多越好”

检索 50 段法规全塞进去：

> 不仅可能干扰模型，

还会：

> 直接消耗 Context 和 KV Cache。

---

# 七十六、以后 ProcurementRAG 的目标会是

```text
更相关的证据
而不是
更多的证据
```

这就是：

# Retrieval Quality

为什么重要。

---

# 七十七、现在说 Batch

假设模型每次只处理：

```text
1条采购条款
```

Batch：

```text
1
```

---

## 20. 如果一次处理 8 条

```text
Batch = 8
```

GPU 可以：

> 更并行。

吞吐可能：

> 更高。

---

## 21. 但是代价

同时存在更多：

- Input；
- Activation；
- KV Cache。

所以显存：

> 上升。

---

# 七十八、所以 Batch 是典型的“速度换显存”

较大的 Batch：

> 可能提高 GPU 利用率。

但：

> 吃更多显存。

---

# 七十九、这和并发有什么关系？

概念上很接近，但生产推理里：

> 并发请求和传统固定 Batch 并不完全是同一件事。

推理引擎可能：

> 动态把多个请求组织成 Batch。

---

# 八十、先用简单心智模型

对我们现在而言可以先记：

```text
同时活跃Sequence越多
↓
KV总量越大
↓
显存压力越高
```

已经足够。

---

# 八十一、为什么生成长度不可忽略？

假设两个用户都输入：

```text
4K Prompt
```

---

### 用户 A

要求：

```text
一句话回答
```

输出：

```text
50 Token
```

---

### 用户 B

要求：

```text
生成完整采购风险审查报告
```

输出：

```text
4000 Token
```

---

## 22. B 的 Session

活得更久。

Context：

> 越来越长。

KV Cache：

> 也不断增长。

---

# 八十二、所以生产容量不能只测短回答

如果真实业务：

> 输出长报告，

Benchmark 却只生成：

```text
20 Token
```

得到的显存和 TPS：

> 没太大业务代表性。

---

# 八十三、这就是为什么 Benchmark 必须模拟真实工作负载

例如 ProcurementAI 测试至少应该有：

```text
短条款审查
中型采购文件
长招标文件
法规RAG输入
长报告输出
多人并发
```

---

# 八十四、显存碎片是什么直觉？

假设显存里：

```text
有很多空位
```

但它们：

> 东一块、西一块。

某个 Kernel 需要：

> 一大块连续空间。

却找不到。

---

## 23. 像停车场

空了：

```text
10个车位
```

但全是：

> 零散的单个小位。

现在一辆超长卡车：

> 需要连续 4 个位。

总空位够：

> 但仍然停不进去。

---

# 八十五、这就是为什么 OOM 有时让人觉得奇怪

你看到：

```text
理论上还有显存
```

但某次大型分配：

> 仍然失败。

实际内存分配：

> 比简单加减法复杂。

---

# 八十六、所以账本是“容量规划”，不是逐字节保证

我们今天算：

```text
14GB + 4GB
```

是为了：

> 判断方案方向。

最终是否稳定：

> 必须真实运行测峰值。

---

# 八十七、什么叫 Peak VRAM？

不是：

> 模型空闲时占多少。

而是：

> 整个实际请求过程中显存最高到多少。

---

# 八十八、为什么它更重要？

假设平时：

```text
18GB
```

某个 Attention Kernel 峰值：

```text
24.5GB
```

你的 GPU：

```text
24GB
```

结果：

> 仍然 OOM。

所以部署容量要看：

# Peak

---

# 八十九、怎样做一个简单的容量实验？

以后真正跑模型时，我们可以设计：

```text
固定Model
固定Precision
固定Batch
```

然后改变：

```text
Context
2K
4K
8K
16K
32K
```

记录：

```text
Peak VRAM
TTFT
TPS
```

---

# 九十、得到一张表

例如教学意义上的：

| Context | Peak VRAM | TTFT | TPS |
|---:|---:|---:|---:|
| 2K | ... | ... | ... |
| 8K | ... | ... | ... |
| 16K | ... | ... | ... |
| 32K | ... | ... | ... |

这比：

> “这个模型支持 32K”

有用得多。

---

# 九十一、“支持32K”到底是什么意思？

它更多是在说：

> 模型架构/位置编码允许在某个范围使用。

但它不保证：

> 你的 GPU 能以任何 Batch、任何并发舒服跑 32K。

---

# 九十二、所以要区分

```text
Model Context Capability
```

和：

```text
Hardware Context Capacity
```

前者：

> 模型理论/训练支持。

后者：

> 你机器实际装不装得下。

---

# 九十三、这两个必须同时满足

```text
模型支持128K
+
GPU只够16K
```

实际系统：

> 仍然跑不了 128K。

---

# 九十四、再来看 MHA vs GQA 的 KV 差距

刚才教学模型：

```text
32 Layers
Head Dim 128
BF16
```

---

## 24. GQA

```text
KV Heads = 8
```

8K：

```text
约1GiB
```

32K：

```text
约4GiB
```

128K：

```text
约16GiB
```

---

## 25. 如果是 MHA

```text
KV Heads = 32
```

是四倍。

同样条件：

| Context | GQA：8 KV Heads | MHA：32 KV Heads |
|---|---:|---:|
| 8K | 约 1GiB | 约 4GiB |
| 32K | 约 4GiB | 约 16GiB |
| 128K | 约 16GiB | 约 64GiB |

现在应该能非常直观地感受到：

> 为什么现代推理架构那么在意 GQA/MQA。

---

# 九十五、第二课一个抽象概念，到这里变成钱了

第二课里：

```text
GQA
```

可能只是：

> “多个 Query Head 共享 K/V。”

今天它变成：

```text
更少KV Heads
↓
更小KV Cache
↓
更长Context
↓
更多并发
↓
更低部署成本
```

这就是为什么底层架构最终会影响：

> 商业成本。

---

# 九十六、企业选模型为什么不能只看 Benchmark 分数？

假设：

### 模型 A

效果：

```text
95分
```

但：

```text
KV特别大
需要4张GPU
```

---

### 模型 B

效果：

```text
94.5分
```

但：

```text
一张GPU就能部署
```

---

## 26. 哪个更好？

要看业务。

如果 B：

> 已经达到质量门槛，

部署成本又低很多，

B：

> 可能更合理。

---

# 九十七、这就是工程中的 Pareto Frontier

这个词先认识即可。

意思是：

> 在质量、成本、速度等多个目标之间，寻找没有明显被全面碾压的方案。

---

# 九十八、ProcurementLM 最终不会只优化一个数字

至少会考虑：

```text
Accuracy / Recall
+
Citation Quality
+
VRAM
+
Latency
+
Throughput
+
Cost
```

---

# 九十九、现在讲训练显存，只建立地图

如果以后从推理进入训练：

显存账本会变成：

```text
Training VRAM
│
├── Weights
├── Gradients
├── Optimizer States
├── Activations
├── Temporary Buffers
└── Distributed Training Overhead
```

注意：

> KV Cache 通常不是训练显存的核心故事。

---

# 一百、为什么 Gradient 很大？

如果 Full Fine-tuning：

> 每个可训练 Weight 都需要 Gradient。

模型：

```text
7B Parameter
```

就意味着：

> 数十亿个 Gradient。

---

# 一百零一、Optimizer State 更可怕

例如 Adam 类优化器：

> 通常还要维护额外状态。

所以 Full Fine-tuning：

> 显存需求远大于只放 Weight。

---

# 一百零二、这就是 LoRA 的另一个价值

LoRA：

> 不让全部几十亿参数都产生可训练状态。

只训练：

> 少量 Adapter 参数。

于是：

```text
Gradient ↓
Optimizer States ↓
```

显存：

> 大幅下降。

---

# 一百零三、QLoRA 再进一步

```text
Base Weight
→ 4-bit

Base Weight
→ Frozen

LoRA
→ Trainable
```

于是：

> Weight 账户和训练状态账户同时得到缓解。

第五课会彻底算一次。

---

# 一百零四、现在把推理和训练放一起看

```text
INFERENCE
────────────
Weights
KV Cache
Activations
Runtime


TRAINING
────────────
Weights
Gradients
Optimizer
Activations
Runtime
```

两边：

> 都吃显存。

但：

> 吃法完全不同。

---

# 一百零五、所以买 GPU 前第一问仍然是

> **你究竟要干什么？**

只是：

```text
Inference
```

还是：

```text
QLoRA
```

还是：

```text
Full Fine-tuning
```

还是：

```text
CPT
```

答案不同：

> 硬件预算会差非常多。

---

# 一百零六、我们现在可以回答：24GB GPU 怎么选模型？

先不要把它理解成一个固定型号推荐。

我们做的是：

# 决策框架

```text
24GB VRAM
   │
   ▼
先预留Runtime / Safety Margin
   │
   ▼
剩余预算
   │
   ├─ Weight
   │
   └─ KV Cache
```

---

# 一百零七、如果目标是舒服学习和实验

更优先：

> 留余量。

例如：

```text
7B BF16
```

或者：

```text
更大模型的合适量化版本
```

通常比：

> 强行把最大模型塞到 23.9GB

更有学习价值。

---

# 一百零八、为什么？

因为你后面还要测试：

```text
Context变化

Batch变化

不同Prompt

不同Sampling

RAG证据
```

如果一开始显存：

> 已经顶死，

任何实验：

> 都容易 OOM。

---

# 一百零九、如果目标是极限单卡模型能力

那策略可能变成：

```text
更大的模型
+
更激进的Quantization
+
较小Batch
+
限制Context
```

---

# 一百一十、如果目标是长文档采购审查

策略可能反过来：

```text
不要把Weight塞到极限
↓
给KV Cache留空间
↓
保证更长Context
```

---

# 一百一十一、如果目标是多人生产服务

还要：

```text
给并发KV留空间
```

所以可能宁愿：

> 用稍小模型。

---

# 一百一十二、这就是同一张 GPU 的三种完全不同用法

```text
同一张24GB GPU
      │
      ├── 最大模型优先
      │
      ├── 长Context优先
      │
      └── 高并发优先
```

没有一种配置：

> 同时全部最大。

---

# 一百一十三、这是一个“资源三角形”

```text
                 更大模型
                    ▲
                   / \
                  /   \
                 /     \
                /       \
               /         \
      长Context ───────── 高并发
```

在同一块显存预算里：

> 三个方向通常互相争空间。

这张图建议牢牢记住。

---

# 一百一十四、政府采购系统最可能偏向哪里？

我们的任务特点：

> 经常需要处理较长文档。

所以未来 ProcurementAI 很可能不能只追求：

> 最大 Parameter Count。

还需要非常重视：

```text
Long Context
+
RAG Context
+
Evidence
```

---

# 一百一十五、但长 Context 也不是无限塞文件

因为长 Context 会带来：

- 更高 KV Cache；
- 更长 Prefill；
- 更高 TTFT；
- Lost-in-the-middle 等模型质量问题。

所以未来真正架构：

> 仍然会大量依靠 RAG 和文档分解。

---

# 一百一十六、这解释了 ProcurementAI 的整体结构为什么不是

```text
把1000页文件
全部塞给一个超长Context模型
```

而更可能是：

```text
文件解析
↓
结构化切分
↓
检索 / 定位
↓
选最相关内容
↓
送给LLM
↓
综合判断
```

---

# 一百一十七、显存优化其实和数据工程有关

这点很有意思。

如果你能从 300 页文件里准确找到：

> 真正相关的 20 页，

不仅：

> 检索质量更好，

还会：

> Token 更少、KV 更小、TTFT 更低。

---

# 一百一十八、所以 RAG 也可以理解成一种计算资源优化

好的 Retrieval：

```text
无关Context ↓
```

于是：

```text
KV Cache ↓
TTFT ↓
噪声 ↓
```

这是未来很重要的一条线。

---

# 一百一十九、显存不足时的决策顺序

以后真 OOM，不要乱改。

可以按这个顺序想：

```text
OOM
 │
 ├─ Weight太大？
 │     ↓
 │   Quantization / 小模型 / 多GPU
 │
 ├─ Context太长？
 │     ↓
 │   缩Context / RAG / KV优化
 │
 ├─ Batch太大？
 │     ↓
 │   降Batch
 │
 ├─ 并发太高？
 │     ↓
 │   限并发 / 调度
 │
 └─ Runtime峰值？
       ↓
     优化框架 / Buffer / Kernel
```

这是非常实用的一张故障树。

---

# 一百二十、不要第一反应就量化

如果 OOM 原因是：

```text
128K Context造成巨大KV
```

你继续把 Weight：

```text
8-bit → 4-bit
```

可能有帮助。

但如果 KV 已经占大头：

> 效果可能没有想象中那么大。

---

# 一百二十一、也不要第一反应就换更大 GPU

如果输入里：

> 80% 都是不相关文档，

更聪明的办法可能是：

> 做更好的 Retrieval。

而不是：

> 砸钱买显存。

---

# 一百二十二、这就是“Find the dominant term”

虽然这是数学味的词，但意思极简单：

> **到底是谁占得最多？**

---

## 27. 如果最大的是 Weight

优化：

> Weight。

---

## 28. 如果最大的是 KV

优化：

> Context / KV。

---

## 29. 如果最大的是 Activation

优化：

> Batch / Runtime / Training Strategy。

---

# 一百二十三、这是专家真正的显存思维

不是背：

> “7B需要多少显存。”

而是：

\[
\boxed{
先找显存主要花在哪里
}
\]

再优化。

---

# 一百二十四、本阶段 5 个核心心智模型总结

| 核心心智模型 | 真正含义 |
|---|---|
| **① VRAM = 共享预算** | Weight、KV、Activation、Runtime 都抢同一块空间 |
| **② Weight = 固定房租** | 模型和 dtype 定了以后，Weight 基本确定 |
| **③ KV = 随 Context 增长的费用** | 输入越长、输出越长，KV 越大 |
| **④ 并发 = 多份请求状态** | Weight 可以共享，但每个请求需要自己的 KV |
| **⑤ 刚好装下 ≠ 可稳定部署** | 必须考虑 Peak VRAM 和安全余量 |

---

# 一百二十五、再加三个辅助模型

### 辅助模型 A：资源三角形

```text
更大模型
   ↕
更长Context
   ↕
更高并发
```

在固定显存里：

> 三者争预算。

---

### 辅助模型 B：量化移动瓶颈

```text
Weight ↓
↓
KV占比 ↑
```

---

### 辅助模型 C：先找大头

```text
Who is dominating VRAM?
```

找到以后：

> 再优化。

---

# 一百二十六、ProcurementLM 快速判断练习 A

GPU：

```text
24GB
```

模型：

```text
14B BF16
```

只看 Weight：

```text
约28GB
```

结论：

> **单卡直接不成立。**

---

# 一百二十七、练习 B

同一模型：

```text
14B INT8
```

Weight：

```text
约14GB
```

现在：

> 有进入候选方案的可能。

但仍要问：

> Context 和 Batch。

---

# 一百二十八、练习 C

```text
32B 4-bit
```

Weight 粗略：

```text
约16GB+
```

24GB 卡：

> 有些配置下可能可以跑。

是不是可以直接承诺：

> “128K 文档也没问题”？

**绝对不能。**

---

# 一百二十九、练习 D

7B BF16：

```text
14GB Weight
```

为什么 128K Context 可能比：

```text
14B 4-bit + 8K Context
```

还更吃显存？

因为：

> 第一个方案的 KV Cache 可能非常大。

---

# 一百三十、练习 E

模型从 7B 变 14B。

KV Cache 一定刚好翻倍吗？

**不一定。**

因为 KV Cache 更直接取决于：

- Layer Count；
- KV Head Count；
- Head Dim；
- Context；
- dtype。

不同架构：

> 参数量相近也可能 KV 成本不同。

---

# 一百三十一、这个问题很关键

所以不能简单认为：

```text
模型大2倍
→
KV一定大2倍
```

Architecture：

> 很重要。

---

# 一百三十二、练习 F

同一个模型：

```text
Batch 1
→
Batch 8
```

Weight：

> 基本没有乘 8。

但 KV 和 Activation：

> 可能大幅增加。

---

# 一百三十三、练习 G

一个模型“支持128K”。

是不是意味着：

> 8GB GPU 也一定能跑 128K？

不是。

支持：

> 是模型能力范围。

能不能运行：

> 是硬件容量问题。

---

# 一百三十四、本阶段最容易犯的八个错误

### 错误 1

> 显存 = Weight。

错。

---

### 错误 2

> Weight 放得下，就一定能推理。

错。

---

### 错误 3

> Context 只影响速度，不影响显存。

错。

---

### 错误 4

> Weight 已经 4-bit，长 Context 就不再 OOM。

错。

---

### 错误 5

> 10 个用户要复制 10 份 Model Weight。

通常不是这么理解。

---

### 错误 6

> 模型官方支持 128K，我的 GPU 就支持 128K。

错。

---

### 错误 7

> 两张卡总显存加起来够，就一定像一张大卡一样简单。

错。

---

### 错误 8

> 把显存跑到 99.9% 是最专业的部署。

通常不是。

稳定生产：

> 需要余量。

---

# 一百三十五、把第三课第 1～7 阶段串起来

```text
Stage 1
GPU / VRAM是什么？
       ↓
Stage 2
软件怎么调用GPU？
       ↓
Stage 3
模型文件是什么？
       ↓
Stage 4
模型怎么加载进GPU？
       ↓
Stage 5
模型怎么真正生成文字？
       ↓
Stage 6
每个Weight占多大？
       ↓
Stage 7
所有东西加起来到底占多少显存？
```

现在我们终于真正回答了：

> **“能不能跑这个模型？”**

而不再只是凭感觉。

---

# 一百三十六、第 7 阶段掌握标准

如果现在不看前文，你能够自己解释下面这些问题，这一阶段就算真正掌握：

> 为什么 24GB GPU 不能简单装一个 24GB Weight 模型？

> 推理时显存至少有哪些主要账户？

> Weight 为什么可以理解成固定成本？

> KV Cache 为什么与 Context Length 有关？

> 为什么模型生成的 Token 也会继续增加 KV Cache？

> 为什么 GQA 可以显著降低 KV Cache？

> KV Cache 的大小大致受哪些变量控制？

> 为什么 8K → 32K Context，KV 大致会增长约 4 倍？

> 为什么 Batch / 并发会显著增加显存？

> 为什么多个请求可以共享 Weight，却不能共享同一份请求 KV？

> Activation 在推理和训练中的显存意义为什么不同？

> Runtime Buffer 为什么使简单算术低估实际 VRAM？

> Peak VRAM 为什么比空闲显存更重要？

> 为什么 7B BF16 能跑，不代表 128K Context 也能跑？

> 为什么量化之后显存瓶颈可能转向 KV Cache？

> 为什么 32B 4-bit 在 24GB 上“可能跑”与“稳定生产部署”完全不是一回事？

> 为什么支持 128K Context 和硬件能跑 128K 是两个问题？

> 为什么长文档政府采购系统需要 RAG，而不能只靠无限 Context？

> OOM 时为什么应该先判断到底是 Weight、KV、Activation 还是 Runtime 在占大头？

如果这些都能自己讲出来：

\[
\boxed{
第三课第7阶段真正掌握
}
\]

---

# 一百三十七、本阶段最终只记一句话

> **GPU 显存不是只用来装模型 Weight 的仓库，而是一张共享预算：Weight 是固定房租，KV Cache 随 Context 和并发增长，Activation 与 Runtime 还需要额外工作空间；真正的模型部署问题不是“模型文件多大”，而是“在真实工作负载下，显存峰值到底是多少”。**

最后把它压成一张图：

```text
                  GPU VRAM
                     │
      ┌──────────────┼───────────────┐
      │              │               │
      ▼              ▼               ▼
   Weights         KV Cache      Activations
  固定成本         动态增长        计算草稿
      │              │               │
      └──────────────┼───────────────┘
                     ▼
              Runtime / Buffers
                     │
                     ▼
               Safety Headroom


KV Cache 主要随着：

Context ↑
Batch / Concurrency ↑
Layers ↑
KV Heads ↑

而增长
```

---

# 下一阶段：第三课 · 第 8 阶段
## Temperature、Top-k、Top-p 到底在控制什么？为什么同一个模型，同一个问题，两次回答会不一样？

前面第 5 阶段我们留下了一个问题：

```text
Transformer
↓
Logits
↓
？？？
↓
Next Token
```

第 8 阶段就专门拆中间的：

```text
？？？
```

我们会继续坚持“先案例、后必要公式”。

比如模型面对下一 Token 时给出：

```text
A：40%
B：30%
C：15%
D：10%
其它：5%
```

然后分别看：

```text
Greedy
Temperature
Top-k
Top-p
```

究竟是在改变什么。

最后会回答一个对 ProcurementAI 特别重要的问题：

> **为什么创意写作可以接受更高随机性，而法规依据、资格条件审查、风险分类等任务往往应该更强调稳定、可复现和证据约束？**

也就是说，第 8 阶段我们会第一次把：

\[
\boxed{
“模型知道什么”
}
\]

和：

\[
\boxed{
“模型这次决定说什么”
}
\]

彻底分开。

---

<!-- LESSON 03 STAGE 07 END -->


<!-- LESSON 03 STAGE 08 START -->

# 第三课 · 第 8 阶段：Greedy、Temperature、Top-k、Top-p 与 Sampling
## 同一个模型明明没有重新训练，为什么同一个问题两次却可能回答不一样？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Greedy = 每一步选择最高概率 Token；Sampling = 按概率分布随机选择，两者只是解码策略不同。**
2. **Temperature / Top-k / Top-p 改变候选分布和随机性，不会给模型增加新知识。**
3. **More Random ≠ More Creative Truth。采样提高多样性，也可能增加不稳定和错误表达。**
4. **固定 Seed 可以改善实验复现，但不同 Kernel、并发和硬件下不一定保证逐 Token 完全一致。**
5. **Low Temperature ≠ High Truthfulness。确定性更高不代表事实、法规和业务判断一定正确。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Temperature` | 温度：控制采样分布平滑程度和随机性 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |
| `Sample` | 样本：具有明确输入、目标和来源的一条训练/评测记录 |
| `Transformer` | Transformer：以注意力和前馈网络为核心的序列架构 |
| `top_p` | Top-p：在累计概率达到 p 的候选 Token 中采样 |
| `top_k` | Top-k：只在概率最高的 k 个 Token 中采样 |
| `Softmax` | Softmax：把一组分数转换成归一化权重 |
| `Validation` | 验证集：开发阶段用于选模型、调参数和早停 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |

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

这一阶段，我们专门补上第 5 阶段留下的那个“黑箱”。

当时完整链路是：

```text
Prompt
  ↓
Transformer
  ↓
Logits
  ↓
？？？
  ↓
Next Token
```

今天只研究：

```text
？？？
```

也就是：

> **模型已经把所有候选 Token 打完分以后，我们究竟怎样决定下一 Token 选谁？**

这阶段我会刻意少用公式。

因为这里真正重要的不是背 Softmax，而是形成几个非常清楚的直觉。

---

# 一、这一阶段真正需要带走的 5 个核心心智模型

```text
① Model负责“打分”
   Decoding负责“选人”

② Greedy = 永远选当前第一名

③ Temperature = 改变候选之间的“悬殊程度”
   不是给模型增加知识

④ Top-k / Top-p = 先缩小候选池
   再从留下的人里选

⑤ 对政府采购高可靠任务：
   稳定性、证据和可复现性
   往往比“回答有创意”更重要
```

如果这五句话真正吃透，

以后看到：

```python
temperature=0.7
top_p=0.9
do_sample=True
```

就不会再变成：

> “网上这样写，我也这样写。”

---

# 二、先不讲 Temperature，先看一个“候选人排行榜”

假设我们让模型回答：

> “该资格条件可能存在______。”

模型现在准备生成下一个 Token。

经过 Transformer 和 LM Head 后，它对很多候选 Token 打了分。

为了教学，我们只看 5 个：

```text
候选 Token        模型倾向

“限制”             很高
“风险”             较高
“问题”             中等
“合理”             较低
“香蕉”             极低
```

注意。

现在模型：

> **还没有真正说出任何一个。**

它只是完成了：

> 评分。

---

# 三、第一个核心心智模型：模型打分 ≠ 最终选择

可以把模型想成：

> 一个专家评审委员会。

它把候选人全部排完：

```text
第1名：限制
第2名：风险
第3名：问题
第4名：合理
……
```

接下来还需要：

> **录取规则。**

---

# 四、模型和 Decoding Strategy 是两个不同角色

```text
LLM Weight
   ↓
根据上下文打分
   ↓
Logits / Probability Distribution
   ↓
Decoding Strategy
   ↓
真正选出的Next Token
```

所以一定记住：

\[
\boxed{
Model \neq DecodingPolicy
}
\]

模型决定：

> “哪些 Token 看起来更合适。”

Decoding 决定：

> “这一次最终选谁。”

---

# 五、这和政府采购专家评审特别像

假设一个项目来了 5 个方案。

专家评分：

```text
方案A：95
方案B：91
方案C：86
方案D：72
方案E：35
```

评分系统：

> 已经完成。

但最终规则可能不同。

---

## 1. 规则一

> 永远选择最高分。

那么一定：

```text
A
```

---

## 2. 规则二

> 在高分方案里按照一定概率抽一个。

可能：

```text
A
```

也可能：

```text
B
```

甚至偶尔：

```text
C
```

模型的评分没有改变。

改变的是：

> **最后的选择方法。**

---

# 六、先认识 Greedy Decoding

Greedy：

> 贪心选择。

名字听起来很学术。

实际超级简单：

\[
\boxed{
每一步永远选当前分数最高的Token
}
\]

---

# 七、假设下一 Token 概率是

```text
限制       45%
风险       30%
问题       15%
合理        7%
其它        3%
```

Greedy 怎么选？

答案永远是：

```text
限制
```

因为：

> 45% 最大。

---

# 八、下一步又重新排名

模型生成：

```text
该资格条件可能存在限制
```

现在重新计算下一 Token。

候选可能变成：

```text
性         55%
供应商     20%
竞争       15%
要求        5%
……
```

Greedy：

> 又选第一名。

---

# 九、所以 Greedy 不是“一次挑完整句子”

它仍然是：

```text
第1步
选当前第一名

↓

第2步
根据新的Context
再选当前第一名

↓

第3步
再选第一名
```

依然是：

# Autoregressive

---

# 十、Greedy 最大的优点：稳定

如果：

- Model Weight 相同；
- Prompt 相同；
- 推理实现没有引入其它随机性；

那么 Greedy 往往会得到：

> 高度稳定甚至相同的输出。

---

# 十一、这对政府采购任务为什么重要？

假设今天审查：

> “供应商必须在本市设立分公司。”

上午运行一次：

> 高风险。

下午同样条件重新运行：

> 完全没风险。

用户会非常困惑。

---

## 3. 专业系统更希望

同样：

```text
模型
+
Prompt
+
证据
+
配置
```

得到：

> 比较稳定的判断。

所以对于：

- 风险分类；
- 法规依据引用；
- 结构化字段抽取；

Greedy 或低随机性的策略：

> 往往更值得优先测试。

---

# 十二、但是 Greedy 也有缺点

永远选择：

> 当前第一名。

不一定等于：

> 最终整段文字一定最好。

---

## 4. 为什么？

因为语言是一个连续决策过程。

有时候：

```text
第1步的第二名
```

虽然稍微低一点，

但走下去以后：

> 后面整段句子可能更自然。

---

# 十三、一个路线类比

你从东京去某个目的地。

每一个路口：

> 永远选择“当前看起来最快的道路”。

不代表：

> 最终整体路线一定最好。

---

# 十四、不过今天先不深入 Beam Search

对于现代 Chat LLM，

我们先把重点放在：

```text
Greedy
vs
Sampling
```

---

# 十五、Sampling 是什么？

Sampling：

> **按照模型给出的概率分布抽取下一个 Token。**

还是：

```text
限制       45%
风险       30%
问题       15%
合理        7%
其它        3%
```

---

## 5. 如果 Sampling

不再保证：

> 每次都选 45% 的“限制”。

可能这次：

```text
限制
```

下一次：

```text
风险
```

偶尔：

```text
问题
```

---

# 十六、注意：Sampling 并不是完全乱选

不是：

```text
词表10万个Token
↓
随便闭眼抽一个
```

而是：

> **尊重模型原来的概率。**

高概率 Token：

> 更容易被抽中。

低概率 Token：

> 更难被抽中。

---

# 十七、用抽奖箱理解 Sampling

假设盒子里放 100 张票：

```text
45张写“限制”
30张写“风险”
15张写“问题”
7张写“合理”
3张写其它
```

随机抽一张。

这就很接近 Sampling 的第一层直觉。

---

# 十八、这就解释了为什么同一个问题可以回答不同

模型：

> 没有重新训练。

Weights：

> 没有改变。

Prompt：

> 可能也完全相同。

但只要：

```text
do_sample=True
```

每一步都有随机抽样，

整段回答就可能：

> 逐渐走向不同路径。

---

# 十九、而自回归会放大这种差异

假设第一个 Token：

### 第一次运行

选了：

```text
“该”
```

### 第二次运行

选了：

```text
“此”
```

只差一个 Token。

---

## 6. 但下一步的 Context 已经不同

第一次：

```text
…… + 该
```

第二次：

```text
…… + 此
```

于是：

> 下一轮概率分布也可能发生一点变化。

---

## 7. 再下一步

差异又继续积累。

最终两篇回答：

> 可能明显不同。

这就是：

\[
\boxed{
Sampling的微小随机差异
可以通过Autoregressive过程逐步放大
}
\]

---

# 二十、现在进入 Temperature

Temperature 是最容易被误解的一个参数。

很多教程只告诉你：

```text
Temperature低
=
保守

Temperature高
=
有创造力
```

这句话没有错。

但太模糊。

我们换一种图形化理解。

---

# 二十一、假设模型原来的候选排名

```text
限制   ████████████████████
风险   ██████████████
问题   ███████
合理   ███
其它   █
```

可以看到：

> 第一名明显领先。

---

# 二十二、低 Temperature 做什么？

它会让这种差距：

> **更悬殊。**

概念上变成：

```text
限制   ██████████████████████████████
风险   ███████
问题   ██
合理   █
其它
```

于是：

> 第一名更容易被选中。

---

# 二十三、高 Temperature 呢？

它会让差距：

> **变平。**

概念上：

```text
限制   ███████████
风险   █████████
问题   ███████
合理   █████
其它   ███
```

于是原来第二、第三、第四名：

> 获得更多机会。

---

# 二十四、第二个超级重要的心智模型

Temperature 不是：

> 给模型安装更多知识。

它是在：

> **改变当前候选分布的尖锐程度。**

可以想成：

```text
低 Temperature
=
第一名优势被放大


高 Temperature
=
候选之间差距被压平
```

---

# 二十五、如果 Temperature 很低

模型更像：

> 一个极度保守的秘书。

看到几个候选：

> 几乎永远采用最稳妥、最高分那个。

结果通常：

- 稳定；
- 可复现性更好；
- 表达变化较少。

---

# 二十六、如果 Temperature 较高

模型更像：

> 一个愿意尝试其它措辞的作者。

结果可能：

- 更多样；
- 更有变化；
- 有时更有创意；
- 但也更容易选到原本概率较低的 Token。

---

# 二十七、Temperature 高 ≠ 模型更聪明

这句话一定要单独钉住。

假设模型根本不知道：

> 某条政府采购法规的真实内容。

你把：

```text
temperature
0.1 → 1.2
```

不会让模型：

> 突然知道正确法条。

---

# 二十八、反而可能发生什么？

本来错误候选有：

```text
5%
```

高 Temperature 后：

> 它相对更有机会被采样。

所以：

\[
\boxed{
Randomness
\neq
Knowledge
}
\]

---

# 二十九、那 Temperature = 0 是什么？

不同框架具体实现可能略有差别。

但在很多常见使用方式中，

当我们追求：

> 极低随机性，

通常会采用：

- Greedy；
- `do_sample=False`；

而不是把所有概念简单压成：

> “Temperature=0”。

所以工程时：

> 要看具体 API 行为。

---

# 三十、现在进入 Top-k

Top-k 的思想更容易。

假设模型词表：

```text
100,000 Token
```

它给所有 Token 排名。

---

## 8. `top_k = 5`

意思可以先理解成：

> **只保留当前排名最高的 5 个候选。**

其余：

> 全部淘汰。

---

# 三十一、例如原来的候选

```text
1 限制      35%
2 风险      25%
3 问题      15%
4 要求      10%
5 条件       6%
6 香蕉       1%
7 飞机       0.5%
...
```

如果：

```text
top_k = 5
```

候选池只剩：

```text
限制
风险
问题
要求
条件
```

“香蕉”：

> 连抽奖资格都没有。

---

# 三十二、Top-k 像初选名单

1000 人报名。

先按照成绩：

> 只留下前 20 名。

然后：

> 再从前 20 名里做后续选择。

---

# 三十三、所以 Top-k 在控制什么？

不是直接说：

> “选第 k 名。”

而是：

> **限制抽样候选池大小。**

---

# 三十四、如果 `top_k = 1` 呢？

只剩：

> 当前第一名。

在概念上就非常接近：

> Greedy。

---

# 三十五、Top-k 有一个缺点

固定：

```text
k = 10
```

不管当前分布是什么：

> 永远留 10 个。

但实际有时：

> 前两个已经占了 99% 概率。

---

## 9. 有时又可能

前 10 个加起来：

> 只有 40%。

这时固定 10：

> 并不总合理。

这就引出：

# Top-p

---

# 三十六、Top-p 的核心不是“固定人数”

而是：

> **先从最高概率开始往下累加，直到累计概率达到某个阈值。**

---

# 三十七、先用采购专家候选池理解

模型现在给：

```text
A   50%
B   25%
C   12%
D    7%
E    3%
其它  3%
```

假设：

```text
top_p = 0.8
```

---

## 10. 从第一名开始累计

```text
A
50%
```

还不到 80%。

---

## 11. 加上 B

```text
A + B
=
75%
```

还不到 80%。

---

## 12. 再加 C

```text
A + B + C
=
87%
```

超过：

```text
80%
```

于是候选池大致是：

```text
A
B
C
```

后面的：

> 被排除。

---

# 三十八、所以 Top-p 像一个“动态候选池”

如果模型很确定：

```text
A = 95%
```

那么：

> 可能只需要极少几个候选。

---

## 13. 如果模型很犹豫

```text
A 20%
B 18%
C 15%
D 12%
E 10%
……
```

为了达到：

```text
top_p = 0.9
```

就可能需要：

> 保留更多 Token。

---

# 三十九、这就是 Top-p 很漂亮的地方

它会根据：

> 当前模型到底有多确定

动态调整：

> 候选池大小。

---

# 四十、Top-k 与 Top-p 对比

可以这样记：

```text
Top-k
=
我要前k名


Top-p
=
我要累计概率达到p的那群人
```

一个固定：

> 人数。

一个固定：

> 概率质量。

---

# 四十一、一个班级录取类比

### Top-k

不管这一届学生水平如何：

> 永远录取前 10 名。

---

### Top-p

不是固定 10 人。

而是：

> 按成绩权重从高到低选，直到覆盖大部分可靠候选。

虽然不是现实招生规则，

但很适合建立直觉。

---

# 四十二、为什么 Top-k / Top-p 可以减少“奇怪词”？

因为 Vocabulary 非常大。

即使很多非常荒谬的 Token：

> 概率不是绝对 0。

如果允许：

> 整个 Vocabulary 都参加抽样，

极低概率候选理论上仍可能被抽到。

---

## 14. Top-k / Top-p

相当于先说：

> “太离谱的候选先别参加。”

于是生成通常：

> 更可控。

---

# 四十三、Temperature、Top-k、Top-p 是怎么配合的？

可以把整个流程想成：

```text
模型原始Logits
      │
      ▼
Temperature
调整候选差距
      │
      ▼
Top-k / Top-p
缩小候选池
      │
      ▼
Sampling
从剩余候选中抽一个
```

这是非常好用的一张脑图。

---

# 四十四、真实实现顺序可能还有其它处理

例如：

- repetition penalty；
- min length；
- bad words；
- stopping criteria；

等等。

我们现在不用全部学。

核心仍然是：

> **先形成概率，再按照生成规则挑 Token。**

---

# 四十五、现在做一个非常直观的实验

模型原始倾向：

```text
A   60%
B   25%
C   10%
D    4%
E    1%
```

---

## 15. Greedy

永远：

```text
A
```

---

## 16. Sampling

大致：

```text
A经常出现
B偶尔出现
C少量出现
D很少
E极少
```

---

## 17. 低 Temperature + Sampling

变成更像：

```text
A   85%
B   10%
C    4%
其它  1%
```

更加保守。

---

## 18. 高 Temperature + Sampling

可能变成：

```text
A   35%
B   25%
C   18%
D   13%
E    9%
```

变化明显增加。

数字只是：

> 帮助理解的示意。

---

# 四十六、现在把它放进采购审查场景

Prompt：

> “请判断该资格条件的风险等级，并给出理由。”

模型内部可能对下一个词判断：

```text
高风险      50%
存在风险    30%
需核验      15%
无风险       4%
其它         1%
```

---

# 四十七、如果使用 Greedy

第一步：

> 大概率固定选择“高风险”。

---

# 四十八、如果高 Temperature Sampling

“需核验”：

> 获得更多机会。

甚至原本只有 4% 的：

> “无风险”

被选中的机会：

> 也可能上升。

---

# 四十九、这就是为什么高风险专业任务不能机械照搬创作参数

创意文案任务：

> 多样性本身可能有价值。

---

## 19. 法规判断任务

我们更关心：

- 同一事实是否稳定；
- 是否引用同一有效依据；
- 分类是否可复核；
- 结果是否一致。

所以目标函数：

> 完全不同。

---

# 五十、第五个核心心智模型正式出现

对于 ProcurementAI：

\[
\boxed{
创造性不是默认目标
}
\]

很多核心任务更需要：

\[
\boxed{
Consistency
+
Evidence
+
Reproducibility
}
\]

---

# 五十一、但“低 Temperature”也不会自动变成法律专家

这句话也非常关键。

假设模型真正的最高概率答案：

> 本身就是错的。

Greedy：

> 只会稳定地重复这个错误。

---

# 五十二、所以稳定错误仍然是错误

这特别重要。

```text
Temperature降低
↓
随机性降低
```

并不等于：

```text
事实错误降低到0
```

---

# 五十三、一个荒谬但很有用的例子

模型错误认为：

> “某不存在的《采购条例》第88条”是正确依据。

它给这个候选：

```text
90%
```

其它正确候选：

> 反而较低。

Greedy 会怎样？

> 每次都稳定地输出错误第 88 条。

---

# 五十四、所以可靠性不能靠 Sampling 参数解决

真正需要：

```text
RAG
+
Citation Validation
+
Gold Set
+
Rules
+
Human Review
```

Decoding：

> 只是最后一公里。

---

# 五十五、把模型能力和 Decoding 彻底分开

```text
模型能力
│
├─ Weight里学到了什么
├─ Prompt里看到了什么
└─ RAG给了什么证据
        │
        ▼
形成Logits
        │
        ▼
Decoding
决定本次如何从候选中选择
```

---

# 五十六、所以改 Temperature 不会发生什么？

不会：

> 修改 Weight。

不会：

> 给模型加入法规库。

不会：

> 更新知识截止日期。

不会：

> 自动修正幻觉。

---

# 五十七、它真正改变的是

```text
这一次生成路径
```

而不是：

```text
模型长期知识
```

可以记成：

\[
\boxed{
SamplingChangesOutputPath
\neq
ModelWeights
}
\]

---

# 五十八、Seed 是什么？

既然 Sampling 有随机性，

实验就出现一个问题：

> “我怎么复现实验？”

---

## 20. 随机数程序通常从某个起点开始

这个起点：

# Random Seed

---

## 21. 可以把 Seed 想成洗牌编号

你告诉机器：

```text
使用第42号洗牌方法
```

在足够相同的环境下，

它可能：

> 按相同随机序列抽样。

---

# 五十九、为什么做 Benchmark 时 Seed 很重要？

假设模型 A 和模型 B：

> 都启用 Sampling。

但 A 恰好抽到：

> 很好的路径。

B 恰好抽到：

> 较差路径。

只测一次：

> 比较不公平。

---

# 六十、专业评测怎么办？

可以：

> 优先使用确定性或低随机性的生成方案。

或者：

> 固定 Seed。

或者：

> 同一题重复多次，统计均值和方差。

---

# 六十一、这连接第一课的 Reproducibility

一个实验应该记录：

```text
Model Revision
Prompt Version
Tokenizer
Generation Config
Temperature
Top-k
Top-p
Seed
```

否则半年以后：

> 很难复现为什么当时得到那个结果。

---

# 六十二、Generation Config 本身就是实验变量

第三阶段我们见过：

```text
generation_config.json
```

现在终于知道它为什么不能随便忽略。

因为模型完全相同，

只改变：

```text
temperature
top_p
do_sample
```

就可能：

> 改变最终输出。

---

# 六十三、所以 Benchmark 不能让各模型“自由发挥”

比如：

模型 A：

```text
temperature=0.1
```

模型 B：

```text
temperature=1.0
```

然后直接比较：

> 谁更稳定。

这显然不公平。

---

# 六十四、模型评测要统一 Decoding Policy

至少同一实验组应该尽量：

> 使用一致、明确记录的 Generation Setting。

不然你测到的可能是：

```text
Model Difference
+
Decoding Difference
```

混在一起。

---

# 六十五、什么叫 Deterministic？

最简单理解：

> 相同输入、相同设置，尽量获得相同输出。

---

# 六十六、但 GPU 推理能不能保证“逐 bit 完全一致”？

现实比概念复杂。

某些底层：

- Kernel；
- 并行计算；
- 数值精度；

可能带来细微非确定性。

所以工程中：

> “确定性”也分程度。

---

# 六十七、对我们现在最重要的层次

先区分：

```text
明显启用随机Sampling
```

和：

```text
不启用Sampling
```

就已经很有价值。

---

# 六十八、`do_sample=False`

可以先理解：

> 不做概率随机抽样。

常见地会走：

> 更确定性的 Token 选择路线。

---

# 六十九、`do_sample=True`

表示：

> 允许按照概率分布进行 Sampling。

这时候：

- Temperature；
- Top-k；
- Top-p；

这些参数的作用：

> 才真正显著。

---

# 七十、一个很常见的配置错误

有人写：

```python
do_sample=False
temperature=0.8
top_p=0.9
```

然后以为：

> Temperature 一定在控制随机性。

实际是否生效：

> 要看具体框架的生成逻辑。

所以永远不要：

> 只看参数名字。

还要理解：

> **生成模式到底是什么。**

---

# 七十一、我们用三个“人格”理解 Decoding

### 模式 A：审计员

```text
Greedy / 极低随机性
```

特点：

> 稳定、保守、变化少。

---

### 模式 B：专业顾问

```text
低到中等随机性
```

特点：

> 主结论较稳定，但措辞有一定变化。

---

### 模式 C：创意策划师

```text
更高随机性
```

特点：

> 尝试更多低排名候选，表达更多样。

这不是固定数值标准。

只是帮助建立感觉。

---

# 七十二、ProcurementAI 哪些任务更像“审计员”？

例如：

```text
字段抽取
风险分类
法规引用
JSON结构输出
资格条件识别
```

我们通常希望：

> 少随机。

---

# 七十三、哪些任务可以稍微允许变化？

例如：

> 根据已经确定的风险结论，生成三种不同措辞的修改建议。

这里：

> 表达多样性

可能有一些价值。

---

# 七十四、所以同一个 ProcurementAI 系统可以有不同 Decoding Profile

而不是全系统一个：

```text
temperature=0.7
```

用到死。

---

# 七十五、例如可以概念上划分

```text
法规依据检索解释
→ 稳定模式

风险分类
→ 稳定模式

结构化抽取
→ 稳定模式

修改建议
→ 低到中等变化

用户友好解释
→ 可允许适度变化
```

真正参数：

> 要通过评测确定。

---

# 七十六、不要用 Temperature 替代“不确定性系统”

假设模型面对一个模糊条款。

我们不应该：

> 把 Temperature 调高，

让它“多想几个答案”。

---

# 七十七、更专业的方法是

系统明确输出：

```text
判断：
需要核验

缺失信息：
项目具体履约要求

证据状态：
尚未检索到足够依据

下一步：
转人工专家
```

也就是：

> **把不确定性显式建模。**

---

# 七十八、Sampling Randomness 和 Epistemic Uncertainty 不是一回事

这个词有点学术，但意思特别重要。

模型每次回答不同：

> 可能只是 Sampling 随机。

不一定代表：

> 模型真的“知道自己不知道”。

---

# 七十九、所以不能这样设计

```text
运行5次
如果答案不同
=
模型不确定
```

它有时可以作为信号之一，

但不能简单等价。

---

# 八十、因为高 Temperature 会人为制造分歧

一个模型本来：

> 对答案非常确定。

你把 Temperature 拉很高：

> 也可以人为制造很多不同回答。

---

# 八十一、反过来也成立

一个模型其实：

> 很没把握。

但你用 Greedy：

> 每次都稳定输出同一个答案。

所以：

```text
Output Stability
≠
True Confidence
```

这和第一课第 11 阶段：

> Uncertainty / Calibration

重新接上了。

---

# 八十二、一个很重要的采购案例

条款：

> “供应商须具有与本项目相适应的履约能力。”

单独看这句话：

> 信息非常不足。

---

## 22. 模型 A

Greedy 每次都回答：

> 合规。

---

## 23. 是否说明模型有 100% 信心？

当然不是。

真正合理的专业输出可能是：

> 需要结合具体能力要求、项目性质以及后续约束进一步判断。

所以：

> 稳定性不是专业置信度。

---

# 八十三、再认识 Repetition Penalty

有时候模型会生成：

```text
该条件存在风险。
该条件存在风险。
该条件存在风险。
```

生成过程中可以引入：

# Repetition Penalty

---

# 八十四、它的直觉

已经出现过很多次的 Token / Pattern：

> 后续选择时降低一些吸引力。

目标：

> 减少机械重复。

---

# 八十五、但不要把它调得过头

因为政府采购文本本身经常必须反复出现：

- 采购人；
- 供应商；
- 资格条件；
- 法规名称。

如果处罚过强：

> 正常专业术语也可能被压制。

---

# 八十六、所以所有 Decoding Parameter 都是 Trade-off

没有：

> “越大越好。”

也没有：

> “越小越专业。”

真正需要：

> 根据任务评测。

---

# 八十七、Structured Output 又是什么关系？

假设我们要求模型输出：

```json
{
  "risk_level": "high",
  "risk_type": "资格条件",
  "reason": "...",
  "evidence": "..."
}
```

这只是：

> **规定输出格式。**

---

# 八十八、结构正确 ≠ 内容正确

模型可以非常稳定地输出：

```json
{
  "risk_level": "high",
  "evidence": "不存在的法规第88条"
}
```

JSON：

> 完美。

事实：

> 错了。

---

# 八十九、所以 ProcurementAI 需要两层校验

```text
第一层
Format Validation

第二层
Semantic / Evidence Validation
```

前者：

> 能不能解析。

后者：

> 内容是不是真的。

---

# 九十、Decoding 可以帮助第一层

例如：

> 降低随机性、使用结构约束。

能够提高：

> 输出格式稳定度。

---

# 九十一、但第二层必须靠

- RAG Evidence；
- Rule Validation；
- Citation Validation；
- Gold Set；
- Human Review。

这再次说明：

> Sampling 只是系统中的一小块。

---

# 九十二、现在看一个完整采购例子

Prompt：

```text
请审查以下资格条件：

“供应商须在采购人所在地设有固定服务机构。”

输出：
1. 风险等级
2. 风险理由
3. 需要核验的法规依据
4. 修改建议
```

---

# 九十三、模式 A：Greedy

可能每次都生成类似：

```text
风险等级：中高风险
理由：可能涉及地域性条件……
需要核验：相关政府采购公平竞争要求……
修改建议：改为与履约服务响应能力相关……
```

优点：

> 稳定。

---

# 九十四、模式 B：Sampling

第一次可能：

> 强调地域限制。

第二次：

> 强调潜在排斥外地供应商。

第三次：

> 强调服务能力与注册地址之间没有必然联系。

可能都合理。

---

# 九十五、哪一种更适合最终审查结论？

通常我们会希望：

> **结论层稳定。**

而说明文字：

> 可以有有限变化。

所以成熟系统甚至可以：

> 将“分类”和“说明生成”拆成两个步骤。

---

# 九十六、这是非常重要的系统设计思想

不要把一个巨大 Prompt：

> 同时承担所有职责。

可以拆成：

```text
Stage A
风险分类
低随机性

↓

Stage B
证据检索
确定性检索

↓

Stage C
形成理由
低随机性

↓

Stage D
润色成用户友好语言
可以稍多一点表达变化
```

---

# 九十七、这样比“一个 Temperature 管天下”专业得多

因为：

> 不同子任务具有不同错误成本。

---

# 九十八、什么任务的错误成本最高？

对我们项目而言，例如：

```text
法规引用错误
高风险漏报
无风险误报
资格判断错误
```

这些：

> 应该采用严格评测和较强约束。

---

# 九十九、什么地方可以更自由？

例如：

> “把这段专业意见改写成普通采购人员更容易理解的话。”

只要事实和结论：

> 已经锁定。

文字表达：

> 可以有适度变化。

---

# 一百、所以“创造性”应该放在正确的层

```text
事实层
→ 少自由

法律依据层
→ 少自由

风险分类层
→ 少自由

措辞层
→ 可以有一些自由

解释风格层
→ 可以更灵活
```

这个心智模型对 ProcurementAI 很重要。

---

# 一百零一、现在把 Greedy、Temperature、Top-k、Top-p 放一张图

```text
                 Model
                   │
                   ▼
                 Logits
                   │
                   ▼
             Temperature
          调整概率分布形状
                   │
                   ▼
          Top-k / Top-p Filter
             缩小候选范围
                   │
                   ▼
          ┌────────┴────────┐
          │                 │
   do_sample=False      do_sample=True
          │                 │
          ▼                 ▼
    更确定性选择          随机抽样
          │                 │
          └────────┬────────┘
                   ▼
               Next Token
```

这张图就是本阶段的主地图。

---

# 一百零二、五个核心心智模型再总结

| 核心心智模型 | 真正要理解什么 |
|---|---|
| **① 模型打分，Decoding 选人** | Weight 决定概率倾向；生成策略决定本次走哪条路径 |
| **② Greedy = 当前第一名** | 稳定、简单，但不是“整段答案全局最优”的保证 |
| **③ Temperature = 改分布尖锐度** | 低温更集中，高温更平，不增加知识 |
| **④ Top-k / Top-p = 候选池过滤** | Top-k 固定人数；Top-p 按累计概率动态决定人数 |
| **⑤ 高可靠任务优先可复现与证据** | 法规审查不能把“更随机”误认为“更聪明” |

---

# 一百零三、三个特别重要的“≠”

```text
低Temperature
≠
事实一定正确
```

```text
高Temperature
≠
模型更聪明
```

```text
回答每次一样
≠
模型真的很有把握
```

这三条非常值得记。

---

# 一百零四、思维实验 A

模型认为：

```text
A：90%
B：5%
C：3%
D：2%
```

Greedy 会选谁？

> A。

---

# 一百零五、思维实验 B

同样的分布，用 Sampling。

是不是永远 A？

> 不是。

A 只是：

> 概率最大。

---

# 一百零六、思维实验 C

Temperature 降低。

模型 Weight 有没有变化？

> 没有。

---

# 一百零七、思维实验 D

Top-k 从：

```text
50
```

改成：

```text
5
```

核心变化是什么？

> 可参加 Sampling 的候选 Token 少了。

---

# 一百零八、思维实验 E

Top-p = 0.9。

是不是固定留下：

> 90% 的 Token 数量？

不是。

它留下的是：

> 从高到低累计概率达到约 90% 的候选集合。

人数：

> 每一步都可能不同。

---

# 一百零九、思维实验 F

使用 Greedy 后同一个错误法条每次都输出。

能不能说明：

> 系统可靠了？

不能。

只是：

> 错得很稳定。

---

# 一百一十、思维实验 G

一个创意广告文案模型每次输出都一模一样。

可能是什么问题？

有可能：

> Decoding 太保守。

但也要看 Prompt 和模型。

---

# 一百一十一、思维实验 H

一个政府采购风险分类器：

> 同一条款运行 10 次出现 6 种风险等级。

这是好事吗？

对于正式工作流：

> 通常是危险信号。

至少说明：

> 输出决策对 Sampling 过度敏感，或者模型本身边界不稳。

---

# 一百一十二、本阶段最容易犯的八个错误

### 错误 1

> Temperature 越高，模型越聪明。

错。

### 错误 2

> Temperature 越低，模型越正确。

错。

### 错误 3

> Greedy 不属于自回归生成。

错。

它仍然逐 Token 生成。

### 错误 4

> Top-k=10 就是选择第 10 名。

错。

是：

> 留前 10 名进入候选池。

### 错误 5

> Top-p=0.9 就留下 90% 的 Token。

错。

是：

> 留到累计概率达到阈值。

### 错误 6

> Sampling 只是随机乱说。

错。

它仍受模型概率分布约束。

### 错误 7

> 输出稳定 = 模型置信度高。

错。

### 错误 8

> 调生成参数可以解决幻觉和法规错误。

解决不了根本问题。

---

# 一百一十三、把第 5 阶段和第 8 阶段真正接起来

第 5 阶段：

```text
Prompt
↓
Transformer
↓
Logits
```

当时我们停住了。

现在补上：

```text
Prompt
↓
Transformer
↓
Logits
↓
Temperature
↓
Top-k / Top-p
↓
Sampling / Greedy
↓
Next Token
↓
加入Context
↓
重复
```

自回归生成链：

> 到这里真正完整了。

---

# 一百一十四、ProcurementAI 推荐的第一条生成原则

对于：

- 法规问答；
- 风险分类；
- 合规审查；
- 结构化抽取；

第一版 Baseline 不要追求：

> “回答每次都很有惊喜。”

而应该优先追求：

\[
\boxed{
稳定
+
可复现
+
有依据
}
\]

---

# 一百一十五、第二条原则

不要凭经验说：

> “Temperature 0.2 肯定最好。”

应该拿真实 Gold Set 测。

例如比较：

```text
配置A：确定性生成

配置B：低随机性

配置C：中等随机性
```

然后看：

- 分类一致率；
- 引用准确率；
- JSON 成功率；
- 专家评分；
- 重复运行方差。

---

# 一百一十六、我们未来甚至可以做一个 Generation Benchmark

每道采购题：

> 重复跑 5 次。

然后观察：

```text
风险等级是否变化？

法规引用是否变化？

证据是否变化？

核心事实是否变化？

只有措辞变化，
还是结论也变化？
```

---

# 一百一十七、这会暴露一个非常重要的问题

如果只是：

```text
“存在风险”
```

变成：

```text
“该条款可能存在一定风险”
```

这只是：

> Surface Variation。

---

## 24. 但如果一次说

```text
高风险
```

另一次说：

```text
无风险
```

这是：

> Decision Instability。

两者严重程度：

> 完全不同。

---

# 一百一十八、所以未来评测不要只比较字符串是否相同

更应该比较：

```text
核心结论
风险类型
引用依据
修改建议方向
```

是否稳定。

---

# 一百一十九、这又连接结构化输出

如果模型先输出：

```json
{
  "risk_level": "high",
  "risk_type": "geographic_restriction"
}
```

再根据这个结构：

> 生成自然语言解释。

系统会比：

> 从头到尾自由作文

更容易控制。

---

# 一百二十、这是一条很重要的系统工程路线

```text
先决定
↓
再解释
```

往往比：

```text
一边自由写
一边临时决定
```

更容易评测和治理。

---

# 一百二十一、第 8 阶段掌握标准

如果现在不看前文，你能够自己解释下面这些问题，这一阶段就算真正掌握：

> Transformer 输出 Logits 后为什么还不能说已经生成了文字？

> 模型和 Decoding Policy 到底是什么关系？

> Greedy 为什么通常更稳定？

> Greedy 是否仍然是一 Token 一 Token 生成？

> Sampling 为什么同一个 Prompt 可能产生不同答案？

> 自回归为什么会放大最开始很小的 Sampling 差异？

> Temperature 真正改变的是知识还是概率分布？

> 低 Temperature 为什么通常更保守？

> 高 Temperature 为什么会让低概率 Token 更有机会？

> 为什么高 Temperature 不等于模型更聪明？

> Top-k 到底在限制什么？

> Top-p 为什么是动态候选池？

> Top-k 和 Top-p 最核心的区别是什么？

> `do_sample=True/False` 从心智模型上分别意味着什么？

> Random Seed 为什么对实验复现有意义？

> 为什么不同模型 Benchmark 应统一 Generation Config？

> 为什么“回答每次一样”不能证明模型真的有信心？

> 为什么 Sampling Randomness 和模型不确定性不是同一回事？

> 为什么法规审查任务通常不应该把创造性当成第一目标？

> 为什么降低 Temperature 无法根治幻觉？

> 为什么结构正确的 JSON 仍然可能包含错误法规？

> 为什么 ProcurementAI 应该把“分类、证据、解释、润色”尽可能分层？

如果这些都能用自己的话说明：

\[
\boxed{
第三课第8阶段真正掌握
}
\]

---

# 一百二十二、本阶段最终只记一句话

> **LLM 的 Weight 决定“下一步哪些 Token 看起来更合适”，而 Greedy、Temperature、Top-k、Top-p 和 Sampling 决定“这一次究竟从这些候选中选择哪一个”；生成策略可以改变输出的稳定性和多样性，却不会给模型增加知识，也不能替代证据、评测和事实校验。**

最后压成一张图：

```text
                 LLM
                  │
                  ▼
               Logits
        “所有候选的原始评分”
                  │
                  ▼
             Temperature
        “差距拉大还是拉平？”
                  │
                  ▼
           Top-k / Top-p
        “谁有资格进入候选池？”
                  │
                  ▼
      ┌───────────┴───────────┐
      │                       │
    Greedy                  Sampling
  选第一名                按概率抽取
      │                       │
      └───────────┬───────────┘
                  ▼
              Next Token
                  │
                  ▼
             加回Context
                  │
                  ▼
                 重复
```

## 下一阶段：第三课 · 第 9 阶段
### 为什么“模型能跑”还远远不等于“模型服务能用”？TTFT、TPS、Throughput、Latency、Batching、vLLM 与 PagedAttention 到底在解决什么？

第 9 阶段会把目前学到的：

```text
Model
+
GPU
+
VRAM
+
KV Cache
+
Generation
```

真正带到**生产推理**。

重点不是继续堆术语，而是解决一个非常现实的问题：

> 两台服务器都说“可以跑 14B 模型”，为什么一台只能一个人慢慢问，另一台却可以同时服务很多用户？

我们会第一次真正区分：

```text
TTFT
=
多久看到第一个Token

TPS
=
后续Token生成多快

Latency
=
一个请求整体等多久

Throughput
=
整个系统单位时间能服务多少工作
```

然后再解释为什么：

> **Continuous Batching、PagedAttention、vLLM，本质上是在解决“怎样把 GPU 和 KV Cache 用得更像一个高效率公共服务系统”，而不是让模型本身突然变聪明。**

---

<!-- LESSON 03 STAGE 08 END -->


<!-- LESSON 03 STAGE 09 START -->

# 第三课 · 第 9 阶段：从“模型能跑”到“模型服务能用”
## TTFT、TPS、Latency、Throughput、Batching、Continuous Batching、vLLM 与 PagedAttention 到底在解决什么？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Latency ≠ Throughput。单个用户等多久与服务器单位时间处理多少请求是不同指标。**
2. **TTFT ≠ Decode Speed。首 Token 等待时间和后续 Token 流速来自不同阶段瓶颈。**
3. **Batching 可以提高 GPU 利用率和吞吐，但过度 Batch 也可能增加排队与单请求延迟。**
4. **Continuous Batching / PagedAttention 的价值在于动态请求与 KV Cache 管理，不是改变模型能力。**
5. **Serving Benchmark 必须使用真实输入长度、输出长度、并发和 P95/P99，而不是只看一个 tokens/s。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Batch` | 批次：一次参与计算的一组样本 |
| `TTFT` | 首 Token 时间：用户等待第一个输出 Token 的时间 |
| `Throughput` | 吞吐：单位时间内处理请求或生成 Token 的能力 |
| `Latency` | 延迟：单个请求从进入到完成的时间 |
| `Attention` | 注意力：根据内容相关性动态聚合信息 |
| `Continuous Batching` | 连续批处理：动态把不同时间到达的请求加入 GPU 批次 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |
| `KV Cache` | KV 缓存：生成时缓存历史 Key/Value 以减少重复计算 |
| `Serving` | 服务化：把模型包装成可扩展、可观测、可治理的在线服务 |
| `Inference` | 推理：系统接收请求并产生结果的在线计算过程 |

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

到第 8 阶段为止，我们已经解决了一个人的问题：

```text
一个用户
    ↓
一个Prompt
    ↓
模型
    ↓
一个Token一个Token生成
    ↓
得到回答
```

如果我们只是坐在电脑前：

> 自己测试模型，

到这里似乎已经够了。

但政府采购 AI 最终不是：

> 一个人在 Jupyter Notebook 里玩模型。

而是可能变成：

```text
采购人A ─┐
代理机构B ─┤
审查人员C ─┤
专家D     ─┼──→ ProcurementAI
监管人员E ─┤
……       ─┘
```

这时候问题完全变了。

我们不再只问：

> **模型能不能生成答案？**

而是开始问：

> **第一个字多久出来？**

> **后面生成快不快？**

> **10个人一起问会怎样？**

> **50个人一起上传长文件会怎样？**

> **GPU 有没有大量时间其实在浪费？**

> **KV Cache 怎么管理才不会把显存弄得一地碎片？**

这一阶段，就是从：

# Model Inference

第一次真正走向：

# Inference Serving

---

# 一、本阶段先只建立 6 个核心心智模型

先不要背任何框架名字。

这一阶段最重要的是下面六句话：

```text
① TTFT
=
用户等多久看到第一个Token

② TPS
=
第一个Token出来以后，后续Token吐得有多快

③ Latency
=
一个请求从进入系统到完成，总共等多久

④ Throughput
=
整套系统单位时间能处理多少工作

⑤ Batching
=
让很多请求一起使用GPU，
避免GPU只服务一个人

⑥ vLLM / PagedAttention这一类技术
=
主要是在提高“服务效率”和“KV内存利用率”
不是让模型Weight突然变聪明
```

先把这六根柱子立住。

---

# 二、先看一个最生活化的场景：政府办事大厅

想象一个办事大厅。

只有一个窗口。

来了一个人：

```text
用户A
```

窗口人员给他处理业务。

三分钟完成。

你会觉得：

> 挺快。

---

# 三、现在突然来了 50 个人

```text
A
B
C
D
E
...
第50个人
```

窗口工作人员的能力：

> 完全没变。

但系统体验：

> 彻底变了。

为什么？

因为现在除了：

> “一个业务办得有多快”

还多了：

> “大家要排多久队”。

这就是模型服务与单模型测试的区别。

---

# 四、一个 LLM 服务请求实际上有很多时间组成

用户点击：

> “开始审查”

到最终报告完成，

可以粗略想成：

```text
用户提交请求
      │
      ▼
排队
      │
      ▼
Prompt进入GPU
      │
      ▼
Prefill
      │
      ▼
第一个Token出现
      │
      ▼
Decode
Token
Token
Token
...
      │
      ▼
回答完成
```

于是：

> “模型速度”

根本不是一个单一数字。

---

# 五、第一个核心指标：TTFT

# Time To First Token

可以直接翻译：

> **从用户提交请求，到看到第一个生成 Token，需要多久。**

例如：

```text
点击“开始审查”
       │
       │ 2.3 秒
       ▼
“该……”
 ↑
第一个Token
```

那么：

```text
TTFT ≈ 2.3秒
```

---

# 六、为什么 TTFT 对用户体验特别重要？

想象两个系统。

### 系统 A

点击以后：

```text
0.8秒
```

就开始：

> “该条款……”

然后慢慢继续生成。

---

### 系统 B

点击以后：

```text
12秒
```

屏幕完全没动静。

然后突然高速生成。

---

多数用户会觉得：

> A 更“灵”。

哪怕最终整篇报告完成时间：

> 未必差很多。

---

# 七、TTFT 主要发生在哪一段？

最重要的一段就是我们第五阶段学过的：

# Prefill

也就是：

> 先处理整个 Prompt。

---

# 八、短 Prompt 和长 Prompt 的区别

用户 A：

```text
请判断以下资格条件是否合理。
```

可能只有：

```text
几十Token
```

---

用户 B：

上传：

```text
180页招标文件
+
法规证据
+
系统Prompt
```

可能变成：

```text
几十K Token
```

---

第二个请求在模型生成第一个 Token 之前：

> 必须先读完整个输入。

所以通常：

```text
Prompt更长
↓
Prefill工作更多
↓
TTFT更长
```

---

# 九、把 Prefill 想成专家“先读材料”

你把一页材料交给专家：

> 很快开始回答。

你把 400 页材料交给专家：

> 他不可能第 0.1 秒就开始给最终结论。

至少要：

> 先阅读。

LLM 也是一样。

---

# 十、所以 ProcurementAI 第一个非常现实的问题出现了

如果用户上传：

> 整本采购文件，

我们不能只问：

```text
模型支持128K吗？
```

还要问：

```text
128K Prefill
用户要等多久？
```

这就是：

> **Context 能塞进去**

和：

> **Context 实际好不好用**

之间的区别。

---

# 十一、第二个指标：TPS

第一个 Token 出来以后，

系统开始：

```text
Token
Token
Token
Token
Token
```

连续生成。

这时我们关注：

# Tokens Per Second

简称：

# TPS

---

# 十二、例如

模型 1 秒钟：

> 生成 50 个 Token。

可以粗略说：

```text
50 token/s
```

---

# 十三、TPS 是“阅读前”还是“写答案”速度？

更直觉地说：

> TPS 主要让你感受模型 **后续写答案有多快**。

而 TTFT：

> 更像模型 **开始说话前要准备多久**。

---

# 十四、用采购专家类比

### TTFT

像：

> 专家看完材料以后，多快开始开口。

### TPS

像：

> 专家开始说以后，说话速度多快。

这两个指标：

> 完全不是一回事。

---

# 十五、来看两个模型

### 模型 A

```text
TTFT = 1秒
TPS  = 20 token/s
```

### 模型 B

```text
TTFT = 5秒
TPS  = 80 token/s
```

哪个更快？

答案：

> **问题问得不完整。**

---

# 十六、如果只回答 20 Token

模型 A：

> 很可能体验更好。

因为 B：

> 光准备就等 5 秒。

---

# 十七、如果要生成 5000 Token 长报告

模型 B：

> 后续生成速度巨大优势可能逐渐体现出来。

所以：

\[
\boxed{
Prompt长度
+
Output长度
}
\]

会影响：

> 用户到底更在意 TTFT 还是 TPS。

---

# 十八、第三个指标：Latency

Latency：

> **一个请求从进入系统，到得到所需结果，要等多久。**

这是一个更完整的概念。

---

# 十九、不要把 Latency 只理解成模型 Forward 时间

真实请求可能经历：

```text
请求进入
  ↓
排队
  ↓
Tokenizer
  ↓
Prefill
  ↓
Decode
  ↓
后处理
  ↓
JSON校验
  ↓
Citation验证
  ↓
最终返回
```

全部加起来：

> 才是用户真正体验到的等待时间。

---

# 二十、所以一个非常重要的心智模型

可以把总等待时间粗略看成：

```text
Total Latency
=
Queue Time
+
Prefill Time
+
Decode Time
+
其它系统开销
```

这不是要你背公式。

只是告诉你：

> “慢”可能慢在不同位置。

---

# 二十一、一个 ProcurementAI 案例

用户说：

> “为什么模型今天这么慢？”

你不能马上回答：

> “GPU 不够快。”

可能实际是：

```text
GPU Forward      很快
但前面排队       18秒
```

真正的问题：

> 并发调度。

---

# 二十二、另一个案例

排队只有：

```text
0.1秒
```

但用户上传：

```text
100K Token
```

Prefill：

> 非常长。

这时真正的问题：

> Context / Prefill。

---

# 二十三、再一个案例

Prompt 很短。

但要求：

> 生成 6000 Token 审查报告。

TTFT：

> 很快。

最后完成：

> 很慢。

问题主要：

# Decode

---

# 二十四、所以以后排查性能第一件事不是问

> “模型快不快？”

而应该拆成：

```text
Queue慢？

Prefill慢？

Decode慢？

还是后处理慢？
```

这和之前显存阶段：

> 先找 dominant term

是同一种专家思维。

---

# 二十五、第四个指标：Throughput

Throughput 可以翻译成：

> **吞吐量。**

它回答的是：

> 整套系统单位时间能够完成多少工作。

---

# 二十六、例如

系统 A：

```text
每秒总共生成50 Token
```

系统 B：

```text
每秒总共生成500 Token
```

B：

> 整体吞吐更高。

---

# 二十七、也可以用 Request 来衡量

例如：

```text
每分钟完成100个请求
```

或者：

```text
每秒处理20个请求
```

取决于：

> 业务定义。

---

# 二十八、Latency 与 Throughput 不是同一个东西

这是本阶段特别重要的一组区别。

### Latency

关心：

> **一个用户等多久。**

### Throughput

关心：

> **整个系统一小时能服务多少用户。**

---

# 二十九、用高速公路类比

Latency：

> 一辆车从入口到出口要多久。

Throughput：

> 一小时能通过多少辆车。

---

# 三十、一条车道可能单车很快

但只能：

> 一辆一辆过。

所以：

> 单请求 Latency 很漂亮，

系统 Throughput：

> 可能很差。

---

# 三十一、这就是很多“跑分视频”容易误导的地方

有人展示：

```text
一个用户
一个Prompt
一张GPU
```

然后说：

> “模型每秒 70 Token，非常快。”

这只能说明：

> 单请求某种条件下挺快。

并不能说明：

> 100 个用户来时系统仍然很好。

---

# 三十二、现在终于进入 Batching

GPU 有一个特点：

> 它特别擅长做大量并行计算。

如果你每次只给 GPU：

> 一丁点工作，

它很多计算单元：

> 可能吃不饱。

---

# 三十三、想象一个 100 人大厨房

你有：

> 100 个厨师。

但现在每次只进来：

> 1 个三明治订单。

于是：

```text
1个厨师工作
99个厨师发呆
```

很浪费。

---

# 三十四、如果一次来了 32 个订单

可以：

> 同时处理。

GPU 利用率：

> 可能明显提高。

这就是 Batching 的第一层直觉。

---

# 三十五、Batching 不是让模型变聪明

Batching 改变的是：

> **我们怎样把工作交给 GPU。**

不是：

> Weight。

所以：

```text
Batching
=
Serving Efficiency
```

不是：

```text
Model Intelligence
```

---

# 三十六、最简单的 Static Batching

假设系统规定：

> 凑齐 8 个请求，再一起运行。

```text
A ┐
B │
C │
D ├──→ Batch 8 → GPU
E │
F │
G │
H ┘
```

这样可以：

> 提高并行效率。

---

# 三十七、但马上出现一个问题

请求 A：

```text
输出50 Token
```

请求 B：

```text
输出3000 Token
```

请求 C：

```text
输出200 Token
```

---

# 三十八、谁先结束？

A：

> 很快。

但如果是传统固定 Batch 思维，

可能出现：

> A 已经没事干了，但这个 Batch 还被 B 拖着。

这就是一种：

# Waste

---

# 三十九、用旅游大巴理解 Static Batch

8 个人坐一辆大巴。

规则：

> 必须所有人办完事，大巴才能走。

---

### A

办事：

> 5分钟。

### B

办事：

> 2小时。

---

结果 A：

> 等 B 两小时。

整个资源利用：

> 很差。

---

# 四十、而 LLM 请求天然就是“长短不一”

因为每个用户：

- Prompt 长度不同；
- Output 长度不同；
- EOS 出现时间不同。

所以：

> 固定 Batch 非常别扭。

---

# 四十一、这就引出 Continuous Batching

名字看起来复杂。

其实直觉非常简单：

> **谁结束了，谁就退出；有新请求，就尽快补进来。**

---

# 四十二、还是一辆动态公交

开始：

```text
A
B
C
D
```

一起在 GPU 上跑。

---

## 1. A 先结束

A 下车。

马上有：

```text
E
```

进入。

现在：

```text
B
C
D
E
```

继续。

---

## 2. C 又结束

C 下车。

新请求：

```text
F
```

加入。

---

# 四十三、这就是 Continuous 的感觉

不是：

```text
一批开始
↓
必须整批全部结束
↓
下一批才能开始
```

而更像：

```text
GPU始终保持一个动态工作池

完成一个
↓
腾出位置

新请求
↓
及时补进来
```

---

# 四十四、这对 LLM 特别合适

因为 Decode 本来就是：

```text
一步
生成一个Token

下一步
再生成一个Token
```

所以推理引擎有机会在：

> 多个请求之间动态调度。

---

# 四十五、第五个核心心智模型正式出现

\[
\boxed{
ContinuousBatching
=
把GPU当成持续运行的公共服务平台
而不是一批一批死等
}
\]

---

# 四十六、政府采购大厅类比

传统 Static Batch：

> 每 10 个人一组。

只要其中一个：

> 业务特别复杂，

另外 9 个：

> 都跟着等。

---

Continuous Batching：

> 谁办完谁走。

新的人：

> 有窗口就补进来。

所以整个大厅：

> 更高效。

---

# 四十七、为什么 Throughput 会提高？

因为 GPU：

> 更少时间闲着。

同样一小时：

> 可以处理更多 Token / 请求。

所以 Continuous Batching 主要优化：

# System Utilization

---

# 四十八、但 Throughput 提高是不是一定让每个用户都更快？

不一定。

这是一个非常重要的 Trade-off。

---

# 四十九、假设 GPU 同时服务很多用户

优点：

> 总吞吐高。

但每个人：

> 可能要和别人分享 GPU 时间。

于是某些情况下：

> 单用户 TPS 可能下降。

---

# 五十、所以又出现一组经典矛盾

```text
单用户极致速度
vs
整机最大吞吐
```

这两个目标：

> 不总是一致。

---

# 五十一、这就是为什么生产推理需要 Scheduler

Scheduler：

> 调度器。

它决定：

```text
谁先上GPU？

谁继续生成？

谁暂时等待？

一次允许多少Sequence？

Prefill和Decode怎么排？
```

---

# 五十二、Scheduler 像大厅叫号系统

不是模型专家本身。

它负责：

> **谁什么时候得到服务资源。**

所以：

```text
Scheduler
≠
LLM
```

---

# 五十三、一个很重要的问题：Prefill 和 Decode 的计算特征不太一样

不用进入 GPU 微架构。

只先建立直觉。

### Prefill

一次处理：

> 很多输入 Token。

可以形成：

> 较大的矩阵计算。

通常更加：

> Compute-heavy。

---

### Decode

每一步：

> 每个 Sequence 只增加少量新 Token。

却需要不断：

> 读取大量 Weight 和 KV。

很多场景下会更加受：

> Memory Bandwidth

影响。

---

# 五十四、用专家办公室类比

Prefill：

> 一次性读一大摞文件。

Decode：

> 每写一句话，都不断回头查自己的知识和已经读过的笔记。

两者工作模式：

> 不一样。

---

# 五十五、所以 Prefill 和 Decode 会争 GPU

假设正在有 20 个用户：

> 一个 Token 一个 Token Decode。

突然来了用户 X：

```text
100K Token Prompt
```

X 的 Prefill：

> 是一大坨工作。

---

# 五十六、如果系统让 X 一口气霸占 GPU

其他正在聊天的人可能感觉：

> 突然卡住。

这就是服务系统中的：

# Scheduling Problem

---

# 五十七、这有点像高速公路突然来了一辆超长车队

原来：

> 大家平稳通过。

突然：

> 100 辆重型卡车一起占道。

其它小车：

> 延迟暴涨。

---

# 五十八、所以好的推理服务不仅要“Batch”

还要考虑：

> **Batch 谁、什么时候 Batch、Prefill 怎么切、Decode 怎么公平调度。**

这已经开始进入真正的系统工程。

---

# 五十九、现在回到第 7 阶段的 KV Cache

每一个活跃用户都有：

> 自己的 KV Cache。

比如：

```text
User A → KV_A
User B → KV_B
User C → KV_C
User D → KV_D
```

随着：

> 请求不断进入、结束，

这些 Cache：

> 不断申请、增长、释放。

---

# 六十、如果内存管理很笨，会发生什么？

想象一块显存：

```text
[AAAAAA][BBBBBBBB][CCCC][DDDDDD]
```

A 完成了。

释放：

```text
[      ][BBBBBBBB][CCCC][DDDDDD]
```

---

# 六十一、后来 C 又完成

```text
[      ][BBBBBBBB][    ][DDDDDD]
```

现在总空闲：

> 可能不少。

但空位：

> 被切成很多小块。

这就是我们第 7 阶段说过的：

# Fragmentation

---

# 六十二、然后来了一个长请求 E

它想要一大块连续空间。

虽然：

> 总空闲显存够，

但：

> 连续的大块不够。

结果：

> 内存利用很差甚至 OOM。

---

# 六十三、这就是为什么 KV Cache 管理非常关键

它不是：

> 一个小附件。

在长 Context、多并发服务中，

KV Cache 可能就是：

> 显存调度的核心对象之一。

---

# 六十四、现在进入 PagedAttention 的核心直觉

先不要看论文公式。

只看名字：

# Paged

分页。

这个思想和操作系统管理内存：

> 很像。

---

# 六十五、传统思路像给每个用户一整套连续房间

用户 A 预计可能需要：

```text
100个房间
```

于是提前：

> 给他留 100 个连续房间。

但他最后只用了：

```text
20个
```

剩下 80：

> 被浪费。

---

# 六十六、Paged 的思路

不要提前要求：

> 一整块连续大空间。

而是把 KV Cache 切成很多：

# Blocks / Pages

---

# 六十七、像一本活页夹

用户 A：

```text
Block 7
Block 9
Block 31
Block 42
```

虽然这些 Block：

> 在物理显存里不连续，

系统仍然知道：

> 它们逻辑上属于 A 的连续上下文。

---

# 六十八、用户 B 可能占

```text
Block 2
Block 8
Block 15
```

也不需要：

> 挨在一起。

---

# 六十九、所以 PagedAttention 最值得记的不是 Attention 公式

而是：

\[
\boxed{
KV逻辑上连续
不要求物理显存里必须整块连续
}
\]

这是最重要的直觉。

---

# 七十、用政府档案库理解

以前：

> 一个项目必须占一个完整柜子。

项目只有 10 页：

> 也占一整柜。

非常浪费。

---

Paged 思路：

> 每个项目按照文件盒分页存放。

比如项目 A：

```text
盒17
盒21
盒38
```

系统目录知道：

> 这三个盒子都属于项目 A。

所以：

> 不必物理连续。

---

# 七十一、这样有什么好处？

主要直觉上有三个：

```text
① 减少大块连续预留浪费

② 减轻显存碎片问题

③ 更灵活地让KV随着Sequence增长
```

---

# 七十二、注意：PagedAttention 不会让 KV Cache 消失

它做的不是：

```text
原本10GB KV
↓
突然变0GB
```

而是：

> **把显存管理得更聪明。**

---

# 七十三、这和第 6 阶段 Quantization 是完全不同的问题

Quantization：

> 改变一个数字占多大。

PagedAttention：

> 改变这些数据怎么组织和分配内存。

---

# 七十四、两者可以同时存在

例如：

```text
4-bit Weight
+
高效KV管理
```

一个优化：

> Weight。

一个优化：

> Runtime KV Memory。

不是二选一。

---

# 七十五、现在终于可以理解 vLLM 是什么角色

不要先把 vLLM 理解成：

> 一个新模型。

它不是：

```text
Llama
Qwen
Mistral
```

这种 Model Weight。

---

# 七十六、vLLM 更像什么？

可以先理解成：

> **专门负责让 LLM 高效提供推理服务的一套引擎。**

也就是：

```text
用户请求
   ↓
vLLM等Inference Engine
   ↓
调度 / Batching / KV管理
   ↓
真正的Model Weight
   ↓
GPU
```

---

# 七十七、所以如果你用同一个模型

方案 A：

```text
Transformers
单请求简单generate
```

方案 B：

```text
高性能Inference Engine
```

模型 Weight：

> 可以完全一样。

业务质量：

> 理论上核心模型没有因为换 Serving Engine 就突然学会新知识。

但：

> 系统吞吐和资源利用可能差非常多。

---

# 七十八、这就是第六个核心心智模型

\[
\boxed{
ServingEngine
\neq
ModelIntelligence
}
\]

它主要解决：

> **如何更有效率地运行模型。**

---

# 七十九、一个采购大厅总类比

现在我们把整个 Stage 9 都放进一个大厅。

### Model Weight

> 专家团队。

### GPU

> 专家所在的办事大厅。

### KV Cache

> 每个案件的临时工作档案。

### Scheduler

> 叫号系统。

### Continuous Batching

> 有空位就让下一案件进来。

### PagedAttention

> 案件档案不用强制占连续完整柜子，而是分页灵活存储。

### vLLM

> 整套高效率办事大厅管理系统之一。

这张类比，基本可以贯穿本阶段。

---

# 八十、现在区分四个性能指标

把它们放一张图：

```text
用户发请求
    │
    │<------ TTFT ------->
    ▼
第一个Token
    │
    │ Token Token Token...
    │<--- TPS描述这一段 --->
    ▼
回答完成


从请求进入
一直到回答完成
<------ Latency ------>


整个服务器
单位时间处理多少请求/Token
<------ Throughput ------>
```

这张图要记牢。

---

# 八十一、一个具体数字案例

系统 A：

```text
TTFT = 1秒
TPS = 25 token/s
```

输出：

```text
500 Token
```

粗略感觉：

> 先等 1 秒，

然后后面约：

> 20 秒左右生成。

总时间：

> 约 21 秒级别，再加其它开销。

---

# 八十二、系统 B

```text
TTFT = 5秒
TPS = 100 token/s
```

同样 500 Token：

> 先等 5 秒，

后面约：

> 5 秒。

总共：

> 约 10 秒级别。

---

# 八十三、如果只输出 20 Token 呢？

A：

> 可能用户感觉更灵。

B：

> 5 秒第一字等待反而明显。

所以性能指标一定要和：

> **真实工作负载**

一起看。

---

# 八十四、这也是为什么 Benchmark 不能只给一个 TPS

如果别人告诉你：

```text
模型速度 = 100 token/s
```

你至少还应该问：

```text
什么GPU？

什么Model？

什么Precision？

Prompt多长？

Output多长？

Batch是多少？

并发是多少？

是单请求TPS还是系统总吞吐？

TTFT是多少？
```

否则这个数字：

> 很容易失去意义。

---

# 八十五、采购 AI 的 Benchmark 更不能只测“Hello”

真实用户可能输入：

### Case A

```text
200 Token
```

一个资格条件。

### Case B

```text
8K Token
```

一章采购需求。

### Case C

```text
32K Token
```

完整文件片段。

### Case D

```text
长Prompt
+
长RAG证据
+
2000 Token报告
```

性能：

> 会完全不同。

---

# 八十六、所以我们未来至少要建立几类 Workload

```text
短输入 + 短输出

长输入 + 短输出

短输入 + 长输出

长输入 + 长输出
```

这四类：

> 对系统压力完全不同。

---

# 八十七、长输入 + 短输出

例如：

> 审查 100 页文件，只输出 5 个风险点。

特点：

```text
Prefill重
Decode较轻
```

更关注：

> TTFT。

---

# 八十八、短输入 + 长输出

例如：

> 给一个项目概要，生成 3000 Token 审查报告。

特点：

```text
Prefill轻
Decode重
```

更关注：

> TPS 和总 Latency。

---

# 八十九、长输入 + 长输出

这个最狠。

例如：

```text
30K采购文件
+
5K法规证据
+
输出4K审查报告
```

它同时压力：

```text
Prefill
+
KV Cache
+
Decode
```

这才接近很多真实采购 AI 工作负载。

---

# 九十、现在说 Queueing

单用户测试：

> 没有排队。

生产：

> 有排队。

---

# 九十一、假设一张 GPU 每秒最多服务某个负载

突然在 1 秒钟内来了：

```text
100个请求
```

GPU 不可能：

> 同时无限处理。

所以一部分：

> 必须排队。

---

# 九十二、排队会让 TTFT 变差

注意：

用户感受到的“第一字等待”在产品层面可能包括：

```text
Queue Time
+
Prefill Time
```

所以即使模型 Prefill 很快，

队伍太长：

> 用户仍然觉得慢。

---

# 九十三、这就是为什么平均值不够

假设：

```text
平均TTFT = 2秒
```

听起来很好。

但真实可能是：

```text
90%用户：1秒

最后10%用户：12秒
```

那一部分用户：

> 体验很差。

---

# 九十四、因此生产性能经常看 Percentile

例如：

```text
P50
P95
P99
```

先只理解直觉。

---

# 九十五、P50

大约：

> 一半用户比它快，一半比它慢。

可以把它理解成：

> 典型用户体验。

---

# 九十六、P95

大约：

> 95% 的请求都不比这个值更慢太多。

更能看：

> 较差用户的体验。

---

# 九十七、P99

关注：

> 尾部极慢请求。

对于生产系统，

这种：

# Tail Latency

很重要。

---

# 九十八、为什么政府采购系统尤其不能只看平均值？

因为某个特别大的采购文件：

> 可能把队列堵住。

普通请求：

> 也被拖慢。

如果只看平均：

> 可能掩盖问题。

---

# 九十九、一个“超长文件堵大厅”的例子

正常请求：

```text
2K Token
```

突然来了一个：

```text
120K Token
```

如果调度器处理不合理，

这个大 Prefill：

> 可能对其它用户产生明显影响。

这类似：

# Head-of-Line Blocking

---

# 一百、直觉是什么？

排队第一位：

> 是一个超级复杂案件。

后面：

> 20 个简单案件。

如果规则是：

> 必须第一个完全办完，后面才能开始，

所有简单案件：

> 都被拖死。

---

# 一百零一、优秀 Scheduler 要尽量避免这种低效

也就是说：

> 不只是追求 GPU 100% 忙，

还要兼顾：

- 公平；
- 响应时间；
- 长短请求；
- Prefill / Decode 混合。

所以：

> Serving 是一个调度问题。

---

# 一百零二、这和操作系统越来越像了

一个 LLM Serving Engine 其实在同时管理：

```text
计算资源
+
显存
+
请求队列
+
KV Cache
+
执行顺序
```

这已经不只是：

> “调用 model.generate()”。

---

# 一百零三、为什么 Hugging Face `generate()` 仍然很重要？

因为学习、实验、单请求验证时：

> 它简单、直观。

我们的课程前面用它：

> 非常合适。

---

# 一百零四、但为什么生产可能需要专门推理引擎？

因为生产目标变成：

```text
多人
+
高吞吐
+
低延迟
+
长Context
+
更高GPU利用率
```

这不是简单：

> 多写一个 for 循环

就能解决。

---

# 一百零五、所以不要形成另一个极端

不是：

> “Transformers 不专业，vLLM 才专业。”

而是：

```text
不同工具
适合不同阶段
```

---

# 一百零六、学习阶段

我们需要：

```text
容易看懂
容易调试
容易观察Tensor
```

简单框架：

> 很有价值。

---

# 一百零七、生产服务阶段

我们开始追求：

```text
Batching
Scheduling
KV管理
并发
吞吐
```

专业 Serving Engine：

> 价值开始变大。

---

# 一百零八、这是“开发环境”和“生产环境”的区别

开发：

> 追求理解和可调试性。

生产：

> 追求可靠、稳定、高利用率。

不要过早：

> 把所有生产优化塞进第一天学习。

---

# 一百零九、现在回到 ProcurementAI

假设我们未来有：

```text
100个采购单位
```

每天提交：

> 采购文件风险审查。

如果每个用户都独占：

> 一套 14B 模型，

成本会非常夸张。

---

# 一百一十、更合理的方向

通常希望：

```text
一套或多套共享Model Weight
        │
        ├─ User A KV
        ├─ User B KV
        ├─ User C KV
        └─ ...
```

然后推理引擎：

> 动态调度。

---

# 一百一十一、这就是为什么 Stage 7 和 Stage 9 是连续的

Stage 7 问：

> 显存里装了什么？

Stage 9 问：

> **这些显存资源怎么在很多请求之间高效使用？**

---

# 一百一十二、一个非常重要的系统公式不需要公式

可以直接记成：

```text
单请求性能
≠
多用户服务能力
```

再重复一遍：

\[
\boxed{
SingleRequestSpeed
\neq
ServingCapacity
}
\]

---

# 一百一十三、为什么一张 GPU TPS 很高，Throughput 仍可能不高？

如果它始终：

> 一次只服务一个请求，

GPU 并行能力：

> 没有被充分利用。

---

# 一百一十四、为什么 Throughput 很高，某用户却觉得慢？

因为系统：

> 同时服务很多请求。

单个请求可能：

> 得不到全部 GPU 资源。

这就是：

```text
Throughput
vs
Latency
```

Trade-off。

---

# 一百一十五、生产系统真正要优化的是“业务 SLA”

SLA 先简单理解成：

> 我们承诺什么体验。

例如未来可以设想：

```text
普通条款审查
第一Token P95 < 某阈值

完整文件审查
总报告完成 < 某阈值

系统
支持至少某并发
```

具体数字：

> 必须靠真实 Benchmark 决定。

现在不先拍脑袋。

---

# 一百一十六、为什么不能先定“100用户并发”？

因为：

> “100 个用户”本身信息不够。

100 个用户如果都只发：

```text
20 Token Prompt
```

与 100 个用户都发：

```text
50K Token文件
```

是两个世界。

---

# 一百一十七、所以并发容量必须带 Workload

更专业的描述是：

```text
在什么输入长度
什么输出长度
什么模型
什么精度
什么硬件

条件下
支持多少并发
```

---

# 一百一十八、未来我们的 Procurement Benchmark 不仅测质量

还应该同时记录：

```text
Quality
+
TTFT
+
TPS
+
Latency
+
Throughput
+
Peak VRAM
```

这才接近：

> 真正模型选型。

---

# 一百一十九、为什么“最聪明模型”不一定是最佳生产模型？

假设：

### Model A

业务准确率：

```text
94%
```

但：

```text
只能2并发
TTFT很高
需要4张GPU
```

---

### Model B

业务准确率：

```text
93.5%
```

但：

```text
支持20并发
TTFT低
1张GPU
```

如果 B 已经超过业务质量门槛：

> 它可能更有价值。

---

# 一百二十、这是再次回到 Pareto 思维

系统设计不是只追：

```text
最高Accuracy
```

而是：

```text
Quality
Cost
Latency
Throughput
VRAM
Reliability
```

共同优化。

---

# 一百二十一、现在做一个完整“办事大厅”总图

```text
                    用户请求
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
         Request A           Request B ...
             │                   │
             └─────────┬─────────┘
                       ▼
                    Queue
                       │
                       ▼
                   Scheduler
                       │
                       ▼
             Continuous Batching
                       │
                       ▼
              ┌────────────────┐
              │      GPU       │
              │                │
              │ Shared Weights │
              │                │
              │ KV A           │
              │ KV B           │
              │ KV C           │
              └────────────────┘
                       │
                       ▼
               Token Generation
                       │
                       ▼
                     用户
```

而 PagedAttention 类思路：

> 主要在中间帮助更灵活地管理 KV Cache。

---

# 一百二十二、五个最容易混淆的概念，一次分开

| 概念 | 最直白的问题 |
|---|---|
| TTFT | 用户多久看到第一个字？ |
| TPS | 开始生成后，吐字多快？ |
| Latency | 这个请求总共等多久？ |
| Throughput | 整台服务器单位时间干多少活？ |
| Concurrency | 同时有多少请求处于活跃状态？ |

这五个：

> 不能混成一个“速度”。

---

# 一百二十三、再区分 Batching 和 Concurrency

Concurrency：

> 同时有很多请求。

Batching：

> 系统把多个请求组织起来一起高效计算。

所以：

```text
有并发
≠
一定高效Batching
```

---

# 一百二十四、一个很烂的服务器也可以“有100并发”

只是：

> 99个人都在排队。

所以：

> Concurrency Number 本身不是性能。

---

# 一百二十五、Continuous Batching 的真正价值

不是：

> “让所有人瞬间完成。”

而是：

> **让动态长短不一的 LLM 请求更充分共享 GPU。**

这句话最准确。

---

# 一百二十六、PagedAttention 的真正价值

不是：

> “Attention 更聪明。”

而是：

> **更灵活地组织 KV Cache 的显存块，减少连续大块分配和浪费。**

---

# 一百二十七、vLLM 的真正价值

先记成：

> **一个高性能 LLM Serving Engine。**

核心目标是：

```text
更高GPU利用率
+
更好的KV管理
+
更高吞吐
+
更成熟的服务调度
```

具体版本实现：

> 后面实操时再看。

---

# 一百二十八、所以这三者的关系不要混

```text
Continuous Batching
=
调度思想


PagedAttention
=
KV内存管理/Attention执行思想


vLLM
=
实现高性能推理服务的引擎之一
```

不是：

> 三个同义词。

---

# 一百二十九、思维实验 A

一个模型：

```text
单请求TPS = 100
```

是不是说明：

> 100 个用户一起时每个人还是 100 TPS？

当然不是。

---

# 一百三十、思维实验 B

模型 TTFT 很高。

第一步该调 Temperature 吗？

不是。

Temperature：

> 控制 Sampling。

TTFT：

> 主要是 Serving / Queue / Prefill 问题。

---

# 一百三十一、思维实验 C

模型已经 4-bit。

系统 Throughput 还是低。

是不是继续量化到更低 bit 就一定解决？

不一定。

可能瓶颈在：

- Batching；
- Scheduler；
- KV；
- CPU；
- 网络；
- Prefill。

---

# 一百三十二、思维实验 D

PagedAttention 能不能让一个 8GB GPU 神奇容纳无限 KV Cache？

不能。

它提高：

> 内存管理效率。

不会：

> 创造无限显存。

---

# 一百三十三、思维实验 E

Continuous Batching 以后总 Throughput 提高。

为什么单用户 TPS 可能下降一点？

因为：

> GPU 同时服务更多 Sequence。

资源：

> 被共享。

---

# 一百三十四、思维实验 F

用户说：

> “点击以后 15 秒没反应，之后文字飞快出来。”

更像哪里慢？

优先怀疑：

```text
Queue / Prefill / TTFT
```

而不是：

> Decode TPS。

---

# 一百三十五、思维实验 G

用户说：

> “第一个字马上出来，但完整报告半天写不完。”

更像：

# Decode

或者：

> 输出太长。

---

# 一百三十六、思维实验 H

单用户测试一切完美。

20 用户一起就崩。

说明至少要调查：

```text
并发KV
+
Batching
+
Peak VRAM
+
Scheduler
```

而不是马上：

> 重训模型。

---

# 一百三十七、本阶段最容易犯的九个错误

### 错误 1

> TPS 就是模型所有速度。

错。

### 错误 2

> TTFT 和 TPS 是一回事。

错。

### 错误 3

> 单用户很快，就代表生产系统很快。

错。

### 错误 4

> Throughput 高，就意味着每个用户都最快。

错。

### 错误 5

> Batch 越大永远越好。

错。

### 错误 6

> Continuous Batching 会提高模型智力。

错。

### 错误 7

> PagedAttention 会减少模型参数。

错。

### 错误 8

> vLLM 是一种新的基础模型。

错。

### 错误 9

> 平均 Latency 很低，生产体验就一定好。

错。

还要看：

> P95 / P99。

---

# 一百三十八、把第三课第 1～9 阶段串起来

```text
Stage 1
GPU / VRAM是什么？
        ↓
Stage 2
软件怎么调用GPU？
        ↓
Stage 3
模型文件是什么？
        ↓
Stage 4
模型怎么加载？
        ↓
Stage 5
一个请求怎么生成文字？
        ↓
Stage 6
Weight怎么压缩？
        ↓
Stage 7
显存怎么做账？
        ↓
Stage 8
Next Token怎么选？
        ↓
Stage 9
很多请求怎么高效共享模型？
```

到这里，

我们已经从：

> “我会运行一个 LLM”

走到了：

> **“我开始理解一个 LLM 服务为什么能或不能真正上线。”**

---

# 一百三十九、本阶段掌握标准

这一阶段结束以后，你应该能够不用背术语，自己解释：

> TTFT 到底在衡量什么？

> 为什么长 Prompt 往往会增加 TTFT？

> TPS 到底是在测哪一段？

> Latency 和 TPS 为什么不是一回事？

> Throughput 和 Latency 为什么可能互相 Trade-off？

> 单用户 TPS 很高为什么不代表多用户服务能力强？

> GPU 为什么适合 Batching？

> Static Batch 在 LLM 上为什么容易浪费？

> Continuous Batching 为什么特别适合长短不一的生成请求？

> Scheduler 在模型服务中到底负责什么？

> Prefill 和 Decode 从工作模式上有什么不同？

> 为什么超长 Prompt 可能影响其它正在 Decode 的请求？

> 什么叫 Head-of-Line Blocking？

> KV Cache 为什么会出现碎片和预留浪费？

> PagedAttention 的“分页”直觉是什么？

> 为什么逻辑连续的 KV 不一定必须物理连续？

> PagedAttention 为什么不是“新的 Attention 智力算法”？

> vLLM 和 Model Weight 是什么关系？

> 为什么换 Serving Engine 不等于重新训练模型？

> 为什么生产系统要看 P95 / P99 而不能只看平均值？

> 为什么 Benchmark 必须包含真实的 Prompt 长度、Output 长度和并发？

> 为什么 ProcurementAI 的质量评测和性能评测最终必须放在同一张选型表里？

如果这些都能自己讲出来：

\[
\boxed{
第三课第9阶段真正掌握
}
\]

---

# 一百四十、本阶段最终只记一句话

> **“模型能生成答案”只是推理的起点；真正的模型服务还必须解决排队、Prefill、Decode、并发、Batching、KV Cache 和调度问题。TTFT 决定用户多久看到第一字，TPS 决定后续生成速度，Latency 描述一个请求整体等待时间，Throughput 描述整套系统能干多少活，而 Continuous Batching、PagedAttention 和 vLLM 这一类技术，本质是在提高 GPU 与 KV Cache 的服务效率，而不是提高模型本身的知识和智力。**

最后把整个阶段压成一张图：

```text
                    多个用户
                       │
                       ▼
                     Queue
                       │
                       ▼
                   Scheduler
                       │
                       ▼
             Continuous Batching
                       │
                       ▼
        ┌─────────────────────────┐
        │          GPU            │
        │                         │
        │     Shared Weights      │
        │                         │
        │  KV_A  KV_B  KV_C ...  │
        │       ↑                 │
        │   Paged KV管理          │
        └─────────────────────────┘
                       │
            ┌──────────┴──────────┐
            ▼                     ▼
         Prefill                Decode
            │                     │
            ▼                     ▼
          TTFT                   TPS
            └──────────┬──────────┘
                       ▼
                    Latency

整个系统单位时间处理多少工作
                       │
                       ▼
                  Throughput
```

# 下一阶段：第三课 · 第 10 阶段
## 第三课最终闭环：怎样真正选择一个政府采购基础模型，并建立第一个 ProcurementAI Baseline？

第 10 阶段会把第三课前 9 个阶段第一次全部变成一张**真实选型表**。

我们不再抽象地问：

> “哪个开源模型最强？”

而是按真正项目的方法比较候选模型：

```text
模型能力
+
中文能力
+
Context
+
Tokenizer
+
License
+
VRAM
+
量化方式
+
TTFT
+
TPS
+
Throughput
+
采购Gold Set
+
法规引用正确率
+
风险漏报率
```

最后形成第三课最重要的成果：

```text
ProcurementAI Base Model Selection Matrix
```

并且第一次定义：

> **ProcurementModel V0.1 的 Baseline 到底应该怎么建立。**

到了第 10 阶段，第三课就会完整闭环：从 **GPU → CUDA → 模型文件 → 加载 → 推理 → 精度 → 显存 → Sampling → Serving → 最终模型选型与 Baseline**。

---

<!-- LESSON 03 STAGE 09 END -->


<!-- LESSON 03 STAGE 10 START -->

# 第三课 · 第 10 阶段：基础模型选型与 ProcurementAI Baseline
## 不再问“哪个模型最强”，而是第一次真正回答：哪个模型最适合我们的政府采购 AI？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Best Leaderboard Model ≠ Best Procurement Model。选型必须看真实政府采购任务，而不是只看通用榜单。**
2. **模型选型是多目标问题：中文理解、Context、RAG/Tool 兼容、质量、延迟、显存、许可证和部署成本都要一起看。**
3. **Baseline 必须可复现：固定模型版本、Tokenizer、Prompt、解码参数和 Benchmark，才能公平比较。**
4. **Model Comparison 要在 Same Protocol 下进行；测试集、Prompt 或硬件不同，分数不能直接归因给模型。**
5. **最终选择的是 System Fit，而不是参数量最大或宣传最强的模型。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Token` | Token：模型实际处理的离散文本单元 |
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `Recall` | 召回率：真实风险中被系统成功找出的比例 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `Tokenizer` | 分词器：文本与 Token ID 之间的编码/解码组件 |
| `Precision` | 精确率：系统报出的风险中真正成立的比例 |
| `VRAM` | 显存：GPU 上存放权重、激活和 KV Cache 等的高速内存 |
| `TTFT` | 首 Token 时间：用户等待第一个输出 Token 的时间 |
| `Citation` | 引用：把生成结论和具体来源建立可追踪链接 |
| `BF16` | BF16：保留较大指数范围的 16 位浮点，常用于大模型 |
| `CUDA` | CUDA：NVIDIA GPU 通用并行计算平台与软件生态 |
| `Accuracy` | 准确率：全部样本中判断正确的比例 |

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

前 9 个阶段，我们一直在拆机器。

我们已经知道了：

```text
GPU是什么
↓
CUDA怎么连接软件和GPU
↓
模型文件是什么
↓
Weight怎么加载
↓
文字怎么进入模型
↓
模型怎么生成Token
↓
精度和量化怎么影响显存
↓
显存到底花在哪里
↓
Sampling怎么影响输出
↓
多人请求怎么变成推理服务
```

现在第三课最后一个问题终于来了：

> **我们真正要做 ProcurementAI，到底选哪个基础模型？**

这个问题看起来像：

> “去排行榜上选第一名。”

实际上不是。

而且这是很多 AI 项目第一次真正走偏的地方。

---

# 一、这一阶段只先记住 6 个核心心智模型

这 6 个，是第三课最后真正需要留下的东西：

```text
① 最强模型 ≠ 最适合项目的模型

② 选模型先看“硬门槛”，再比“软能力”

③ 公共Benchmark只能帮助筛选，
   自己的Procurement Gold Set才负责最终决策

④ 模型要和部署预算一起选，
   不能先选模型、最后才问GPU够不够

⑤ Baseline不是最终产品，
   Baseline是以后所有优化必须击败的“起跑线”

⑥ 第一个Baseline的目的不是证明模型有多强，
   而是尽快暴露：
   模型到底错在哪里
```

这六句话，实际上比任何一张模型排行榜都重要。

---

# 二、第一个核心心智模型：最强模型 ≠ 最适合项目的模型

想象现在有三个候选。

### 模型 A

```text
72B
能力很强
需要多张GPU
推理成本高
```

### 模型 B

```text
14B
能力不错
单卡量化可以运行
速度较快
```

### 模型 C

```text
7B
能力稍弱
单卡很轻
部署非常便宜
```

如果只问：

> “谁最强？”

可能是 A。

但如果我们的真实条件是：

```text
单机
24GB GPU
需要处理长文档
需要多人使用
预算有限
```

A 甚至：

> 根本不是一个现实候选。

---

# 三、用公务用车做类比

你要采购一辆车。

世界上最快的赛车：

> 当然“性能很强”。

但你的需求是：

- 日常办公；
- 坐 5 个人；
- 能放材料；
- 油耗合理；
- 维修方便。

那赛车：

> 反而是很差的选型。

LLM 也一样。

---

# 四、所以模型选型真正的问题不是

```text
谁最高分？
```

而是：

```text
谁在我的业务
+
我的硬件
+
我的成本
+
我的可靠性要求

下面最好用？
```

这才是：

# Model Selection

---

# 五、先做一个非常重要的转变

以后不要说：

> “我要找最好的开源模型。”

而应该说：

> **“我要找在 ProcurementAI 目标工作负载下最合适的模型。”**

这句话听起来只是措辞变化。

实际上思维方式完全不同。

---

# 六、什么叫“目标工作负载”？

就是未来它到底要干什么。

我们的第一版 ProcurementModel，不是什么都做。

我们先聚焦一个清楚的任务：

# 政府采购文件合规风险审查

而不是：

```text
聊天
+
写诗
+
代码
+
数学
+
翻译
+
采购审查
+
所有事情
```

---

# 七、第一版任务进一步拆成 5 类风险

我们可以把第一版核心审查对象先定义为：

```text
A
供应商资格

B
技术参数

C
商务要求

D
评分标准

E
采购需求
```

于是模型选型开始有：

> 明确靶子。

而不是泛泛比较“聪明程度”。

---

# 八、为什么任务边界这么重要？

假设一个模型：

> 数学题特别强。

另一个模型：

> 中文长文本理解、规则判断更强。

如果我们的任务是：

> 政府采购文件审查，

数学榜第一：

> 不一定有多少直接价值。

---

# 九、所以第一个模型选型原则

\[
\boxed{
先定义任务
再选择模型
}
\]

不是：

\[
\boxed{
先喜欢一个模型
再想办法找任务
}
\]

这是非常常见的项目反转。

---

# 十、第二个核心心智模型：先过“硬门槛”

选模型可以想象成招聘专家。

不是所有候选人：

> 都直接进入最终面试。

先有一轮：

# Hard Gates

也就是：

> 不满足就直接淘汰的条件。

---

# 十一、硬门槛一：License

这件事很容易被技术人员忽略。

模型可能：

> 技术上很好。

但它的许可证：

> 不适合你的商业或项目使用方式。

那怎么办？

答案很简单：

> 淘汰。

---

# 十二、为什么 License 是“门槛”而不是“加分项”？

因为它不像：

> “中文能力 85 分还是 90 分。”

而更像：

> “这个项目到底能不能合法使用。”

所以一定先查：

```text
商业使用是否允许？

修改是否允许？

部署是否有限制？

衍生模型有什么义务？

是否需要注明来源？

特定规模是否存在额外条款？
```

具体模型：

> 要以其当前正式许可证为准。

---

# 十三、硬门槛二：硬件装不装得下

假设项目只有：

```text
1 × 24GB GPU
```

候选模型：

```text
72B BF16
```

哪怕能力非常高：

> 第一轮直接淘汰。

---

# 十四、但这里不是只看 Weight

第 7 阶段已经告诉我们：

```text
VRAM
=
Weights
+
KV Cache
+
Activations
+
Runtime
+
Safety Headroom
```

所以选型不能只问：

> “模型文件几 GB？”

---

# 十五、硬门槛三：Context 是否满足基本业务

假设真实采购文件：

> 经常很长。

候选模型只能舒服处理：

```text
2K / 4K
```

即使其他能力不错：

> 对我们的业务可能并不合适。

---

# 十六、但又不能犯另一个极端

模型宣传：

```text
128K Context
```

不意味着：

> 它就是最佳长文档采购模型。

因为还要看：

- 真实长文本质量；
- Lost-in-the-middle；
- 显存；
- TTFT；
- 长 Context 下推理成本。

---

# 十七、所以 Context 要问两个问题

```text
模型理论支持多长？
```

以及：

```text
我们实际硬件上能稳定跑多长？
```

这两个缺一不可。

---

# 十八、硬门槛四：Tokenizer 与中文

模型处理的是 Token。

所以即使两个模型都说：

> 支持中文，

Tokenizer 的效率也可能不同。

---

# 十九、一个简单例子

同样一份：

> 10 万字采购文件。

模型 A：

```text
120K Token
```

模型 B：

```text
80K Token
```

这意味着什么？

不是只有 Tokenizer 好不好看。

它直接影响：

```text
Context占用
↓
Prefill时间
↓
KV Cache
↓
显存
↓
成本
```

---

# 二十、Tokenizer 效率会变成钱

这件事特别值得记。

```text
更高 Token Fertility
      ↓
同样中文产生更多Token
      ↓
计算更多
      ↓
显存更多
      ↓
延迟更多
      ↓
成本更多
```

所以中文 Tokenizer：

> 是工程指标。

不是小细节。

---

# 二十一、硬门槛五：基础推理能否稳定运行

一些模型可能需要：

```text
特殊代码
特殊Kernel
特殊依赖
```

如果你的部署环境：

> 很难稳定维护，

也要计入选型。

---

# 二十二、政府项目尤其要问

> **这个模型半年以后还能不能稳定复现？**

不仅是：

> “我今天在我的电脑上跑起来了。”

---

# 二十三、所以第一层筛选图可以画成

```text
候选模型
   │
   ▼
License允许？
   │
   ├─ 否 → 淘汰
   ▼
硬件装得下？
   │
   ├─ 否 → 淘汰
   ▼
Context基本够？
   │
   ├─ 否 → 淘汰
   ▼
中文/Tokenizer可接受？
   │
   ├─ 否 → 淘汰
   ▼
运行栈可维护？
   │
   ├─ 否 → 淘汰
   ▼
进入正式Benchmark
```

这就是：

# Gate First

---

# 二十四、为什么先 Gate 很重要？

因为如果一开始就拿：

> 20 个模型

跑几千道 Benchmark，

很浪费。

其中很多模型可能：

> 业务上根本不可能部署。

---

# 二十五、第三个核心心智模型：公共榜单只能做“海选”

这是模型选型非常关键的一条。

网上有很多：

- 综合能力榜；
- 中文能力榜；
- 数学榜；
- Coding 榜；
- Arena 类评价。

它们：

> 有价值。

但用途主要是：

# Candidate Discovery

---

# 二十六、它们不能直接回答

> “谁最适合政府采购文件合规审查？”

为什么？

因为公共 Benchmark：

> 不是按照我们的业务风险设计的。

---

# 二十七、举一个极端例子

模型 A：

```text
通用Benchmark 90分
```

模型 B：

```text
通用Benchmark 87分
```

但在采购审查 Gold Set：

```text
A：
高风险漏报率 18%

B：
高风险漏报率 6%
```

你选谁？

对于合规审查：

> 很可能 B。

---

# 二十八、因为业务错误不是等价的

假设模型发生两个错误。

错误 A：

> 把“中风险”判成“高风险”。

错误 B：

> 把真正严重风险判成“无风险”。

这两个：

> 业务成本完全不同。

---

# 二十九、所以我们不能只看 Accuracy

政府采购风险审查至少应该看：

```text
Precision

Recall

F1

高风险Recall

漏报率

误报率
```

第一课其实已经讲过这些。

现在终于开始真正落地。

---

# 三十、为什么我特别强调 Recall？

如果模型的任务是：

> 帮助发现采购文件中的潜在风险，

那么：

> 真正的风险没有被发现

通常特别值得关注。

也就是：

# False Negative

---

# 三十一、用安检机类比

安检系统：

> 如果经常把普通东西误报成危险品，

会烦。

但如果：

> 真正危险品直接漏掉，

通常更严重。

采购风险审查也有类似逻辑。

---

# 三十二、但这不代表 Recall 无限高越好

如果模型为了不漏报：

> 把所有条款都标成风险，

Recall 可能很好。

但系统：

> 完全没法用。

所以还要：

> Precision。

---

# 三十三、这就是第一课的知识回来了

```text
Recall
=
风险找全多少

Precision
=
你报出来的风险有多少是真的
```

最终要：

> 平衡。

---

# 三十四、但 LLM 不只是分类器

我们还要它解释：

```text
问题在哪里？

为什么有风险？

依据是什么？

怎么修改？
```

所以还需要：

# Generation Evaluation

---

# 三十五、政府采购模型最重要的一类指标：Citation Correctness

如果模型说：

> “依据某某规定第 X 条……”

我们必须验证：

```text
法规存在吗？

法规名称对吗？

条文真的支持这个结论吗？

当前有效吗？

适用层级对吗？

适用地区对吗？
```

---

# 三十六、一个模型可能“分类对、依据错”

例如：

> 这个资格条件确实存在风险。

模型判断：

> 对。

但引用：

> 一个不存在的法条。

对于专业产品：

> 仍然不合格。

---

# 三十七、所以以后我们会把答案拆成多个评价维度

例如：

```text
风险类型正确？

风险等级合理？

依据正确？

依据充分？

理由与证据一致？

修改建议可执行？
```

而不是一个：

> “总体感觉不错”。

---

# 三十八、什么叫 Gold Set？

Gold：

> 金标准。

就是我们准备一批：

> 由专业人员确认过答案的真实业务样本。

---

# 三十九、例如一条样本

输入：

```text
供应商须在采购人所在地具有固定办公场所。
```

Gold Label 可能包含：

```text
风险类型：
潜在地域性/不合理资格条件

风险等级：
待结合项目履约必要性判断

关键证据：
……

专家理由：
……

建议修改方向：
……
```

---

# 四十、为什么 Gold Set 特别重要？

因为它代表：

> **我们自己对“好答案”的定义。**

公共 Benchmark：

> 定义的是别人的问题。

Gold Set：

> 定义的是我们的业务。

---

# 四十一、这就是模型选型最核心的一句话之一

\[
\boxed{
PublicBenchmark
负责筛候选
}
\]

\[
\boxed{
BusinessGoldSet
负责定冠军
}
\]

非常值得记。

---

# 四十二、Gold Set 一开始需要多大？

不要陷入：

> “没有 10 万条就不能开始。”

第一版可以先做：

> 小而精。

例如覆盖：

```text
A 供应商资格
B 技术参数
C 商务要求
D 评分标准
E 采购需求
```

每一类：

> 先有一批高质量典型样本。

---

# 四十三、真正重要的是覆盖“决策边界”

不是只放：

> 一眼就能看出有问题的题。

还要大量放：

# Hard Cases

---

# 四十四、什么叫 Hard Case？

例如：

### Case A

明显不合理：

> “供应商必须是本市企业。”

---

### Case B

明显合理：

> “供应商应具备履行合同所需的设备和专业技术能力。”

---

### Case C

最难：

> “供应商应在项目所在地具备 2 小时内到场服务能力。”

这时：

> 不能只看到“项目所在地”就机械判违法。

还要判断：

- 项目性质；
- 服务必要性；
- 是否可以用响应能力替代所在地要求；
- 是否构成不合理限制。

这种：

> 才真正检验模型能力。

---

# 四十五、所以 Gold Set 不能只有“简单题”

一个模型如果只在简单题上 99%：

> 没什么可炫耀的。

真正的专业能力：

> 往往体现在边界案例。

---

# 四十六、第四个核心心智模型：模型和硬件必须一起选

这是第三课全部硬件知识最后要落到的地方。

不能这样：

```text
先选72B
↓
觉得它最好
↓
最后才问：
服务器多少钱？
```

---

# 四十七、更合理的流程

```text
业务目标
+
预算
+
部署环境
      │
      ▼
形成候选模型范围
      │
      ▼
再做能力比较
```

---

# 四十八、假设我们有一张 24GB GPU

现在有三种思路。

### 方案 A

```text
7B BF16
```

---

### 方案 B

```text
14B 4-bit
```

---

### 方案 C

```text
32B 4-bit
```

---

# 四十九、不要立刻说 C 最好

我们先看每个方案。

---

# 五十、方案 A：7B BF16

优势可能是：

```text
精度高
部署简单
显存还有余量
Context空间更宽松
```

劣势：

> 模型容量较小。

---

# 五十一、方案 B：14B 4-bit

优势：

```text
模型参数更多
Weight显存较低
仍可能单卡运行
```

劣势：

```text
有量化影响
速度取决于Kernel
模型架构可能更重
```

---

# 五十二、方案 C：32B 4-bit

优势：

> 参数量更大。

但风险：

```text
Weight已经吃掉较多VRAM
KV余量变小
长Context紧张
并发能力下降
```

---

# 五十三、如果我们的核心任务是“长采购文件审查”

那很可能出现：

> 14B 4-bit 比 32B 4-bit 更实用。

不是因为：

> 14B 比 32B 更聪明。

而是：

> 整套系统更平衡。

---

# 五十四、所以我们真正优化的是

```text
Business Utility
```

不是：

```text
Parameter Count
```

---

# 五十五、模型选型需要一张矩阵

以后不要靠：

> “感觉这个模型不错。”

我们建：

# Base Model Selection Matrix

例如：

| 维度 | Model A | Model B | Model C |
|---|---:|---:|---:|
| License | ✅ | ✅ | ✅ |
| 中文能力 | 8 | 9 | 9 |
| Procurement Gold Set | 78 | 84 | 86 |
| 高风险 Recall | 82% | 91% | 92% |
| Citation Correctness | 70% | 79% | 80% |
| 32K Context 实测 | ✅ | ✅ | ⚠️ |
| Peak VRAM | 15GB | 12GB | 22GB |
| TTFT | 快 | 中 | 慢 |
| TPS | 快 | 中 | 较慢 |
| 并发余量 | 高 | 中 | 低 |
| 部署复杂度 | 低 | 中 | 中高 |

这里的数字：

> 全部只是教学示意。

真正项目要：

> 实测填表。

---

# 五十六、为什么矩阵比排行榜好？

因为排行榜通常：

> 只强调一两个能力分数。

而矩阵会逼你同时面对：

```text
能力
+
成本
+
性能
+
工程风险
```

这就是：

> 项目选型。

---

# 五十七、还应该加一个非常重要的列

# Failure Mode

也就是：

> **这个模型最容易怎么错？**

例如：

### Model A

> 法规引用经常编造。

### Model B

> 风险 Recall 很高，但误报较多。

### Model C

> 长文本后半部分容易漏看。

这比：

> 总分 84.7

更有价值。

---

# 五十八、为什么？

因为后续系统架构：

> 可以针对错误补偿。

---

# 五十九、例如模型容易法规幻觉

解决思路：

> RAG + Citation Validation。

---

# 六十、模型漏掉某类明显规则

解决思路：

> Rule Engine。

---

# 六十一、模型不会按照我们的工作格式输出

解决思路：

> SFT。

---

# 六十二、模型不熟悉采购专业语言

解决思路：

> 可能考虑 CPT / SFT / 数据增强。

---

# 六十三、这就是一个非常重要的思想

选模型时不要只问：

> “谁错误最少？”

还可以问：

> **“谁的错误最容易通过系统工程补上？”**

这是很成熟的决策思维。

---

# 六十四、比如两个模型

### Model X

总分更高。

但最大的错误：

> 经常非常自信地编造法规。

---

### Model Y

总分稍低。

但错误主要是：

> 表达格式不统一。

对于我们的系统：

> Y 可能反而更好修。

因为格式问题：

> SFT 很容易改善。

编造法规：

> 风险更大。

---

# 六十五、第五个核心心智模型：Baseline 到底是什么？

Baseline：

> 基线。

最简单说：

> **以后所有优化都要拿它来比较的第一版系统。**

---

# 六十六、Baseline 不是“垃圾模型”

也不是：

> 随便跑一下。

一个好的 Baseline 应该：

```text
简单
清楚
可重复
可测量
```

---

# 六十七、为什么 Baseline 要简单？

因为以后你会加：

```text
RAG
SFT
LoRA
规则
更好Prompt
更好数据
```

如果第一版一开始就：

> 20 个模块搅在一起，

最后提升了：

> 你都不知道是谁起作用。

---

# 六十八、所以第一版 Baseline 应该尽量朴素

例如：

```text
一个明确的Base Instruct Model
+
固定Prompt
+
固定Generation Config
+
不做SFT
+
不做CPT
+
先不加复杂Rule Engine
```

然后：

> 跑 Gold Set。

---

# 六十九、这叫 Zero-shot / Prompt Baseline 的思想

先问：

> **这个基础模型不训练，单靠现有能力，到底能做到什么？**

这个答案非常重要。

---

# 七十、为什么不要一上来就 SFT？

假设 Base Model：

> 已经 90 分。

SFT 后：

> 91 分。

那说明：

> 微调价值有限。

---

# 七十一、另一种情况

Base：

> 62 分。

加 RAG：

> 83 分。

说明：

> 核心问题可能主要是知识依据。

---

# 七十二、再一种情况

Base + RAG：

> 仍然 70 分。

但模型总是：

> 不会按专家方式组织判断。

SFT 后：

> 86 分。

说明：

> 工作方式学习很重要。

---

# 七十三、如果没有 Baseline

你根本不知道：

> 提升来自哪里。

所以 Baseline 是：

# Scientific Control

---

# 七十四、第一次设计 ProcurementModel V0.1

现在我们真正开始给它定义身份。

不是：

> “政府采购万能机器人。”

而是：

# ProcurementModel V0.1
## 政府采购文件合规风险审查 Baseline

---

# 七十五、输入是什么？

第一版输入可以定义得很清楚：

```text
一段采购条款
+
必要的上下文
```

例如：

```text
项目：
物业管理服务

资格条件：
“供应商须在本市注册成立5年以上。”
```

---

# 七十六、输出不要让它自由作文

我们可以先规定结构：

```text
风险类别：
风险等级：
是否需要进一步核验：
判断理由：
所需法规依据：
修改建议：
```

这样：

> 更容易评测。

---

# 七十七、为什么 Structured Output 重要？

如果一个模型回答：

> 一大篇漂亮文章，

很难自动统计：

```text
风险类别对不对？
```

---

# 七十八、结构化后

我们能直接提取：

```text
risk_type
risk_level
needs_review
reason
evidence
suggestion
```

然后：

> 分项评价。

---

# 七十九、Baseline 第一版甚至可以更简单

先只要求：

```text
risk_type
risk_present
reason
```

不要一开始：

> 让一个 Prompt 承担所有工作。

---

# 八十、为什么？

因为我们第一步最需要知道：

> **模型究竟会不会发现风险。**

不是：

> 它文章写得漂不漂亮。

---

# 八十一、于是 V0.1 的核心任务可以变成

```text
Input：
采购条款

↓

Output：
是否存在风险
+
风险类别
+
简短理由
```

之后再单独加：

> 法规依据检索。

---

# 八十二、这是“分层任务”的思想

不要：

```text
一个模型
一次生成
承担整个世界
```

而是：

```text
风险发现
↓
证据检索
↓
依据核验
↓
解释生成
↓
修改建议
```

---

# 八十三、为什么这会更可靠？

因为每一步：

> 都能单独测。

如果最终答案错了，

你能定位：

```text
风险识别错？

RAG检索错？

依据验证错？

还是语言生成错？
```

---

# 八十四、这和软件工程一样

一个巨大黑箱：

> 最难调试。

模块化：

> 更容易诊断。

---

# 八十五、第一版 Prompt 应该怎么设计？

先不要追求：

> “超级 Prompt”。

只需要：

> 清晰、稳定、可版本化。

---

# 八十六、例如概念模板

```text
角色：
你是政府采购文件风险审查助手。

任务：
判断给定条款是否存在潜在合规风险。

要求：
1. 不确定时明确输出“需要核验”
2. 不得编造法律依据
3. 先输出风险类别，再说明理由
4. 只根据当前提供的信息判断

输入：
{clause}
```

注意：

> 这是教学模板。

未来还会不断校正。

---

# 八十七、为什么 Prompt 也要 Version？

因为你改一句：

> “必须给出结论”

可能就改变模型行为。

所以：

```text
Prompt V0.1
Prompt V0.2
Prompt V0.3
```

应该：

> 有记录。

---

# 八十八、Generation Config 也必须固定

第 8 阶段已经学过：

```text
Greedy
Temperature
Top-p
```

Baseline 时我们不应该：

> 每次随便换。

---

# 八十九、对于合规 Baseline

可以优先测试：

> 低随机性 / 确定性方案。

目的：

> 先减少 Sampling 噪声。

这样评测出来的错误：

> 更像模型能力问题。

---

# 九十、模型版本也必须锁定

不要只记录：

```text
Model = XXX-14B
```

还应该记录：

```text
具体Revision
Tokenizer版本
Quantization版本
Runtime版本
```

因为模型仓库：

> 可能更新。

---

# 九十一、这就是 Experiment Manifest

一次实验应该至少知道：

```text
Model
Model Revision
Tokenizer
Precision
Prompt Version
Generation Config
Dataset Version
Code Version
Hardware
```

这样半年后：

> 才能真正复现。

---

# 九十二、我们第一次真正定义一个 Baseline Run

例如：

```text
Experiment：
PROC-BASE-001

Model：
Candidate-B

Precision：
4-bit

Prompt：
proc_review_v0.1

Generation：
deterministic

Dataset：
gold_v0.1

GPU：
24GB class
```

然后跑：

> 全部 Gold Set。

---

# 九十三、得到的不应该只是“总分”

我们需要：

# Error Table

---

# 九十四、例如

| Sample | Gold | Prediction | Error Type |
|---|---|---|---|
| 001 | 风险 | 风险 | Correct |
| 002 | 无风险 | 风险 | False Positive |
| 003 | 风险 | 无风险 | False Negative |
| 004 | 需核验 | 无风险 | Overconfident |
| 005 | 技术参数风险 | 资格风险 | Wrong Type |

---

# 九十五、这张表比一个“82分”重要得多

因为它告诉你：

> **模型到底怎么错。**

而后面的第四课、第五课：

> 全部会从这些错误开始。

---

# 九十六、第五个核心心智模型再强调一次

Baseline 的价值不是：

> 证明模型很强。

Baseline 的价值是：

> **创建一个可测量的起点。**

---

# 九十七、第六个核心心智模型：错误样本是资产

这是我们整个项目以后非常重要的一条。

很多人觉得：

> 模型答错了，删掉算了。

实际上：

> 错题最值钱。

---

# 九十八、为什么？

因为错误样本告诉你：

> 模型的能力边界在哪里。

---

# 九十九、例如发现 100 个错误里

```text
40个
法规知识不知道

30个
长上下文漏看

20个
判断逻辑不稳定

10个
输出格式错误
```

现在系统路线一下就清楚了。

---

# 一百、40 个知识错误怎么办？

优先考虑：

> RAG。

---

# 一百零一、30 个长文本错误怎么办？

可能需要：

- 更好的文档切分；
- 检索；
- Context 策略；
- 更合适模型。

---

# 一百零二、20 个工作逻辑错误怎么办？

可能：

> SFT。

---

# 一百零三、10 个格式错误怎么办？

可能：

> Structured Output / SFT / Validation。

---

# 一百零四、所以 Error Analysis 决定技术路线

不是：

```text
因为最近大家都在做LoRA
所以我也LoRA
```

而应该：

```text
错误是什么
↓
为什么错
↓
哪种技术专门解决它
```

---

# 一百零五、这就是专家模型开发路线

```text
Measure
↓
Diagnose
↓
Intervene
↓
Measure Again
```

中文：

```text
测量
↓
诊断
↓
干预
↓
再测量
```

这是以后整个课程的一条主线。

---

# 一百零六、现在看一张完整 ProcurementAI 模型选型流程

```text
业务任务定义
      │
      ▼
硬门槛
License / Hardware / Context
      │
      ▼
候选模型 3~5 个
      │
      ▼
统一Prompt
统一Generation
统一Hardware条件
      │
      ▼
Procurement Gold Set
      │
      ▼
质量评测
      │
      ├─ Recall
      ├─ Precision
      ├─ Risk Type
      ├─ Citation
      └─ Stability
      │
      ▼
性能评测
      │
      ├─ VRAM
      ├─ TTFT
      ├─ TPS
      ├─ Latency
      └─ Throughput
      │
      ▼
Failure Analysis
      │
      ▼
Base Model Selection Matrix
      │
      ▼
选出V0.1 Baseline
```

这就是第三课最终要得到的工程地图。

---

# 一百零七、为什么候选最好不要只有一个？

如果你从一开始就认定：

> “我就用这个模型。”

那不叫：

> 选型。

那叫：

> 先决定答案，再找理由。

---

# 一百零八、第一版可以选 3～5 个候选

例如概念上：

```text
Candidate S
小模型

Candidate M
中模型

Candidate L
较大模型
```

然后：

> 统一条件实测。

---

# 一百零九、为什么要统一条件？

因为否则你可能拿：

```text
Model A
4-bit
8K Context
```

和：

```text
Model B
BF16
32K Context
```

直接比较速度。

结果：

> 没意义。

---

# 一百一十、至少要记录差异

如果某些模型：

> 必须使用不同配置，

也可以比。

但必须明确：

> 你比较的是“部署方案”，而不是单纯 Model Weight。

---

# 一百一十一、这两个概念要分开

# Model Comparison

比较：

> 模型本身。

# Deployment Configuration Comparison

比较：

> 模型 + Quantization + Runtime + Hardware。

---

# 一百一十二、真实项目最后更关心后者

用户不会问：

> “你的 FP16 原始权重多厉害？”

用户关心：

> **系统好不好用。**

所以最终应比较：

# Solution

而不仅是：

# Checkpoint

---

# 一百一十三、ProcurementAI 选型矩阵建议分 5 个大区

为了以后真正执行，可以把表分成：

```text
① 合规与许可

② 模型能力

③ 业务质量

④ 工程性能

⑤ 运维风险
```

---

# 一百一十四、第一类：合规与许可

看：

```text
License
商业使用
衍生模型限制
部署约束
```

一票否决型。

---

# 一百一十五、第二类：模型能力

例如：

```text
中文理解
长文本
指令遵循
结构化输出
基础推理
```

---

# 一百一十六、第三类：业务质量

这才是核心：

```text
采购风险Recall
采购风险Precision
风险类型准确率
Citation Correctness
专家评分
```

---

# 一百一十七、第四类：工程性能

```text
Peak VRAM
TTFT
TPS
Latency
Throughput
Context Capacity
```

---

# 一百一十八、第五类：运维风险

例如：

```text
部署复杂度
框架兼容性
社区成熟度
版本稳定性
监控难度
```

---

# 一百一十九、最后不要简单“总分最高者获胜”

为什么？

因为一些指标：

> 是硬底线。

例如：

```text
License不允许
```

哪怕其它 99 分：

> 也不能选。

---

# 一百二十、另一些可能是最低门槛

例如：

```text
高风险Recall
必须 ≥ 某业务门槛
```

未达到：

> 淘汰。

---

# 一百二十一、然后剩下候选再看综合 Pareto

也就是：

> 谁在成本和质量之间最划算。

---

# 一百二十二、一个教学例子

假设最终三套方案：

### 方案 A

```text
业务分：88
GPU成本：1
TTFT：快
长Context：好
```

### 方案 B

```text
业务分：91
GPU成本：2
TTFT：中
长Context：好
```

### 方案 C

```text
业务分：92
GPU成本：6
TTFT：慢
长Context：一般
```

---

# 一百二十三、C 比 B 只高 1 分

但成本：

> 3 倍。

是不是值得？

这不是：

> 模型研究问题。

这是：

> 产品和项目决策。

---

# 一百二十四、政府采购 AI 尤其要看“可解释失败”

如果模型答错，

我们希望知道：

```text
哪一段证据导致的？

哪个规则冲突？

模型为什么判成这样？
```

所以未来系统不能只输出：

> “风险 0.83”。

还需要：

> 可追溯证据链。

---

# 一百二十五、这就是为什么第三课结束以后

我们不会马上进入：

> “疯狂微调模型”。

下一课先进入：

# 数据工程

因为：

> 没有好数据，就没有好的 Gold Set，也没有好的 SFT。

---

# 一百二十六、第三课最大的转折其实不是 GPU

很多人以为第三课主要是：

> 学硬件。

但真正变化是：

从第二课：

> “模型里面怎么工作？”

走到第三课：

> **“怎样把模型变成一个可测、可选、可部署的工程对象？”**

---

# 一百二十七、现在回头看第三课 10 个阶段

```text
Stage 1
GPU、CPU、VRAM、CUDA
↓
知道“计算资源在哪”

Stage 2
PyTorch / CUDA运行链
↓
知道“软件怎么调用硬件”

Stage 3
模型仓库
↓
知道“模型文件是什么”

Stage 4
from_pretrained
↓
知道“模型怎么被装起来”

Stage 5
端到端生成
↓
知道“文字怎么进去、出来”

Stage 6
Precision / Quantization
↓
知道“Weight为什么大小不同”

Stage 7
VRAM Ledger
↓
知道“显存怎么做账”

Stage 8
Decoding
↓
知道“Next Token怎么选”

Stage 9
Serving
↓
知道“多人怎么共享模型”

Stage 10
Model Selection + Baseline
↓
知道“项目到底怎么正式开始”
```

现在第三课终于不是：

> 10 个零散概念。

而是一条完整工程链。

---

# 一百二十八、第三课最终总图

```text
                         业务目标
                            │
                            ▼
                       候选模型
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
           License       Capability     Hardware
                            │             │
                            │             ▼
                            │        Precision
                            │             │
                            │             ▼
                            │           VRAM
                            │
                            ▼
                       Gold Set
                            │
              ┌─────────────┴──────────────┐
              ▼                            ▼
          Quality Eval                Performance Eval
              │                            │
     Recall / Precision             TTFT / TPS
     Citation / Stability           VRAM / Throughput
              │                            │
              └─────────────┬──────────────┘
                            ▼
                    Selection Matrix
                            │
                            ▼
                ProcurementModel V0.1
                            │
                            ▼
                       Baseline
                            │
                            ▼
                    Error Analysis
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
             RAG           SFT           Rules
```

这就是第三课最后真正需要留下的一张图。

---

# 一百二十九、ProcurementModel V0.1 不应该叫什么？

不要先叫：

> “政府采购大模型智能专家系统 V10.0”。

这种名字：

> 很容易把自己骗进去。

更专业的名字反而朴素：

```text
Procurement Compliance Baseline V0.1
```

它明确告诉所有人：

> 这是起点。

不是终点。

---

# 一百三十、Baseline 通过什么才算“建立成功”？

不是：

> “模型能输出中文。”

至少要做到：

```text
模型版本固定

Prompt固定

Generation固定

Gold Set固定

评测脚本固定

结果可以复现

错误样本可以导出
```

---

# 一百三十一、最好还要生成一张 Baseline Report

例如：

```text
Model:
xxx

Dataset:
gold_v0.1

Overall F1:
...

High-risk Recall:
...

Citation Correctness:
...

Peak VRAM:
...

TTFT:
...

TPS:
...

Top Error Categories:
1. ...
2. ...
3. ...
```

这个文件：

> 会成为以后所有实验的参照物。

---

# 一百三十二、以后每次技术升级都要问

比如增加 RAG。

不要只说：

> “感觉回答更专业了。”

而要比较：

```text
Baseline V0.1
vs
RAG V0.2
```

---

# 一百三十三、比如 SFT

比较：

```text
RAG V0.2
vs
RAG + SFT V0.3
```

---

# 一百三十四、比如 CPT

比较：

```text
V0.3
vs
CPT + SFT + RAG
```

这样：

> 每一步提升都有证据。

---

# 一百三十五、如果某个复杂优化没有提升呢？

那就：

> 不要因为花了很多时间而舍不得扔。

这就是实验纪律。

---

# 一百三十六、一个项目最危险的事情之一

叫：

# Sunk Cost

已经做了两个月的方案，

即使数据证明：

> 没有价值，

团队仍然说：

> “都做这么久了，再坚持一下。”

Baseline + Benchmark：

> 可以帮助我们抵抗这种感觉。

---

# 一百三十七、数据说话，但也不是唯分数论

因为 Gold Set：

> 本身也可能不完整。

所以还需要：

- 专家复核；
- 新错误样本；
- 线上反馈；
- Red Team。

---

# 一百三十八、Benchmark 也是会成长的

第一版：

```text
Gold V0.1
```

发现模型新的失败模式以后：

```text
Gold V0.2
```

加入更多 Hard Case。

---

# 一百三十九、这就是数据飞轮的最初形态

```text
模型运行
↓
发现错误
↓
专家确认
↓
加入Error Set / Gold Set
↓
模型再次评测
↓
系统变强
```

真正有价值的资产：

> 会越来越集中在这些高质量错误案例上。

---

# 一百四十、这就是为什么“下载了多少 PDF”不是护城河

任何团队：

> 都可以下载公开法规。

真正难复制的是：

```text
专家怎么判断

边界案例怎么处理

哪些错误最常出现

错误怎样修正

什么证据真正支持结论
```

这些才会逐渐变成：

> ProcurementAI 的核心资产。

---

# 一百四十一、本阶段最容易犯的 10 个错误

### 错误 1

> 参数越大一定越适合项目。

错。

### 错误 2

> 公共排行榜第一就直接选。

错。

### 错误 3

> License 后面再看。

危险。

### 错误 4

> Weight 能装下，部署就没问题。

错。

### 错误 5

> 支持 128K 就说明长文本业务一定强。

错。

### 错误 6

> Accuracy 一个指标就够。

错。

### 错误 7

> Baseline 越复杂越专业。

错。

### 错误 8

> 一上来就微调，比先测基础模型更先进。

不一定。

### 错误 9

> 模型答错是垃圾，没有价值。

恰恰相反。

错误样本可能是：

> 最值钱的数据之一。

### 错误 10

> 模型选型完成以后永远不用重新评估。

错。

模型、数据、业务：

> 都会变化。

---

# 一百四十二、第 10 阶段掌握标准

如果现在不看前文，你可以自己解释下面这些问题，第三课就真正完成了：

> 为什么“最强模型”不一定是最适合 ProcurementAI 的模型？

> 为什么模型选型应该先做 Hard Gate？

> License 为什么属于硬门槛？

> 为什么硬件和模型必须一起选？

> Tokenizer 为什么会影响成本和长文本能力？

> Public Benchmark 和 Procurement Gold Set 分别负责什么？

> 为什么高风险 Recall 对风险审查特别重要？

> 为什么只看 Accuracy 不够？

> Citation Correctness 为什么必须单独评？

> 什么叫 Hard Case？

> 为什么 Gold Set 不能只放简单题？

> 为什么 Model Failure Mode 也是选型指标？

> 什么叫 Baseline？

> 为什么 Baseline 应该尽量简单？

> 为什么没有 Baseline 就不知道 RAG/SFT 到底有没有贡献？

> ProcurementModel V0.1 的输入和输出为什么应该先定义清楚？

> 为什么结构化输出有助于评测？

> Prompt、Generation Config、Model Revision 为什么都要版本化？

> Error Analysis 为什么决定下一步用 RAG、SFT 还是 Rules？

> 为什么模型答错的样本反而是重要资产？

> 为什么最终选型表必须同时包含 Quality 和 Performance？

> 为什么最终真正比较的是“解决方案”，而不只是 Checkpoint？

如果这些都可以清楚讲出来：

\[
\boxed{
第三课第10阶段掌握
}
\]

---

# 一百四十三、第三课最终只记三句话

如果第三课其他细节以后忘了一半，也没关系。

只要留下这三句话。

第一句：

> **LLM 不只是一个 Weight 文件，它是一整套“硬件 + Runtime + Tokenizer + Context + Generation + Serving”的计算系统。**

第二句：

> **模型选型不是寻找最大、最新、排行榜最高的模型，而是在业务质量、硬件成本、上下文、速度、可靠性之间寻找最合适的方案。**

第三句：

> **第一个 Baseline 的最大价值，不是证明我们已经成功，而是建立一条以后任何改进都必须用数据击败的起跑线。**

---

# 一百四十四、第三课正式闭环

现在我们已经完成：

```text
第二课
“LLM为什么能工作？”

           ↓

第三课
“怎样真正把一个LLM运行、测量、部署并选出来？”
```

接下来第四课会发生一个非常明显的变化。

我们不再继续拆 GPU。

不再继续拆 Transformer。

我们开始处理整个项目最容易被低估、但实际上决定上限的东西：

# Data

---

# 下一课：第四课 · 政府采购数据工程与训练数据集

第四课计划 **12 个阶段**。

我们会从最容易被忽略的问题开始：

> **一份 PDF 招标文件，究竟什么时候才算变成了“可以训练模型的数据”？**

你会发现：

```text
下载PDF
≠
拥有训练数据
```

真正的链路是：

```text
PDF / HTML / DOCX
      ↓
解析
      ↓
文档结构恢复
      ↓
去页眉页脚
      ↓
表格处理
      ↓
条款切分
      ↓
去重
      ↓
项目级数据隔离
      ↓
任务Schema
      ↓
专家标注
      ↓
Hard Negative
      ↓
Train / Validation / Gold Test
      ↓
Dataset Version
```

第四课最终会形成：

# `ProcurementDataset_V0.1`

也就是说，到第三课这里，我们第一次拥有了：

> **可以运行和选择的模型。**

第四课开始，我们要第一次拥有：

> **真正可以拿去训练和评测的政府采购数据。**




---

<!-- LESSON 03 STAGE 10 END -->

