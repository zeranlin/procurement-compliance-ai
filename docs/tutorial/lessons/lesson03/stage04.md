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
