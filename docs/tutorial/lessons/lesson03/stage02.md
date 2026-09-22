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
