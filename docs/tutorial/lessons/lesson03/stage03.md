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
