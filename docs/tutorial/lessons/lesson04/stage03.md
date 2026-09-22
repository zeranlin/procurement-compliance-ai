# 第四课 · 第 3 阶段：文档结构恢复与 Clause Segmentation
## 机器已经拿到了“正确文字”，为什么它仍然不知道哪里是一章、哪里是一条资格条件，以及“一条采购条款”到底从哪里开始、在哪里结束？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Clause Segmentation ≠ Sentence Splitting 一条采购条款可能有很多句**
2. **标题不是靠“字体大”一个特征判断， 而是多个结构信号共同决定**
3. **文档结构恢复的核心不是切得越细， 而是恢复“谁属于谁”**
4. **Target Clause 可以很小， 但它必须保留 Parent Section 和必要 Context**
5. **表格中的一行、一个评分项， 也可能是一条真正的业务 Clause**
6. **结构恢复错误会直接污染： 风险类型、Train/Test切分、RAG、SFT和最终审查结果**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Clause Segmentation` | 条款切分：把连续文档恢复成可审查业务条款 |
| `Block` | 版面块：文档解析后保留布局和位置的基本块 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Parser` | 解析器：把 PDF/Word/HTML 转换为结构化可处理内容 |
| `Recovery` | 恢复：工具失败或中断后安全重试、降级和继续 |
| `SFT` | 监督微调：用监督样本继续更新模型参数 |
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `CPU` | CPU：负责通用控制、数据准备和部分算子 |
| `Loss` | 损失函数：把预测错误压缩成可优化的数值信号 |
| `Layout` | 版面结构：文字块、表格、列、坐标和阅读顺序信息 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `Representation` | 表示：模型内部承载语义或特征的向量结构 |

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

第 2 阶段结束以后，我们手里已经不再只是：

```text
一个PDF文件
```

而开始拥有类似这样的东西：

```text
ParsedDocument
│
├── Page 1
│   ├── Block 1
│   ├── Block 2
│   └── Block 3
│
├── Page 2
│   ├── Block 4
│   ├── Block 5
│   └── Table 1
│
└── ...
```

而且我们已经尽量保证：

> 文字基本正确。

> 阅读顺序基本正确。

> 页码、位置、表格和来源信息都还保留着。

这听起来似乎已经很接近训练数据了。

但实际上，中间还缺了极其关键的一层。

假设 Parser 给我们：

```text
第三章 采购需求
3.1 供应商资格条件
1. 供应商应具有独立承担民事责任的能力。
2. 供应商须在本市注册成立5年以上。
3.2 技术要求
1. 服务器CPU核心数不得少于……
2. 存储容量不得低于……
```

对于人类来说：

> 结构一眼就看出来了。

但机器如果只拿到几个 Text Block，它未必知道：

```text
“第三章 采购需求”
=
章标题

“3.1 供应商资格条件”
=
第三章下面的子章节

“2. 供应商须在本市注册成立5年以上。”
=
一条真正需要审查的资格条件

“3.2 技术要求”
=
上一节结束、新的一节开始
```

所以今天要解决的问题是：

> **怎样把一堆正确的文字块，恢复成一个有层级、有归属、能切出真实采购条款的业务结构？**

最终我们第一次要产出：

# `ClauseUnit_V0.1`

---

# 一、本阶段真正要解决的一个核心问题

可以把问题压缩成一句话：

> **文档里的文字，怎样从“平面字符串”恢复成“Project → Document → Section → Clause”的层级结构？**

第 2 阶段解决的是：

```text
文字对不对？
```

第 3 阶段开始解决：

```text
这些文字到底属于哪里？
```

这是两个完全不同的问题。

---

# 二、本阶段先建立 6 个核心心智模型

先记住这六句话：

```text
① Clause Segmentation ≠ Sentence Splitting
   一条采购条款可能有很多句

② 标题不是靠“字体大”一个特征判断，
   而是多个结构信号共同决定

③ 文档结构恢复的核心不是切得越细，
   而是恢复“谁属于谁”

④ Target Clause 可以很小，
   但它必须保留 Parent Section 和必要 Context

⑤ 表格中的一行、一个评分项，
   也可能是一条真正的业务 Clause

⑥ 结构恢复错误会直接污染：
   风险类型、Train/Test切分、RAG、SFT和最终审查结果
```

今天绝大部分内容，都在展开这六句话。

---

# 三、先看一个最简单的文档

假设原文是：

```text
第三章 采购需求

3.1 供应商资格条件

1. 供应商应具有独立承担民事责任的能力。

2. 供应商须在本市注册成立5年以上。

3.2 技术要求

1. 系统应支持不少于1000个并发用户。

2. 数据库服务器内存不得低于256GB。
```

人类会自动构建：

```text
第三章 采购需求
│
├── 3.1 供应商资格条件
│     ├── 条款1
│     └── 条款2
│
└── 3.2 技术要求
      ├── 条款1
      └── 条款2
```

机器真正需要恢复的，就是这棵树。

---

# 四、所以结构恢复不是“切文本”

更准确地说，是：

# Tree Reconstruction

也就是：

> **重新构建文档树。**

你可以把原始 Parser 输出看成：

```text
一排积木
```

Structure Recovery 的任务是：

> 把它们重新搭回原来的楼。

---

# 五、为什么“谁属于谁”这么重要？

假设机器拿到这句话：

```text
不得低于500万元。
```

单独看：

> 意义不完整。

但如果 Parent Section 是：

```text
第三章
供应商资格条件
```

含义可能是：

> 注册资本或者类似资格门槛。

---

# 六、如果它的 Parent Section 是

```text
项目预算
```

那：

```text
不得低于500万元
```

可能完全不是供应商资格。

---

# 七、所以一个很重要的公式式直觉

\[
\boxed{
ClauseMeaning
=
ClauseText
+
StructuralContext
}
\]

这里的 Structural Context 就包括：

```text
它在哪一章？
在哪一节？
属于什么表格？
前面的标题是什么？
```

---

# 八、第一件要恢复的东西：Heading

Heading：

> 标题。

例如：

```text
第一章 招标公告

第二章 投标人须知

第三章 采购需求

第四章 评标办法
```

这些显然是高级标题。

---

# 九、但现实不会永远这么整齐

有的文件写：

```text
第三章 采购需求
```

有的写：

```text
第三部分 采购需求
```

有的写：

```text
三、采购需求
```

有的甚至只是：

```text
采购需求
```

然后字体：

> 加粗、居中、字号大。

---

# 十、所以 Heading Detection 不能只靠一个规则

例如：

```text
字号 > 16
→ 标题
```

会非常危险。

---

# 十一、因为正文里也可能有大字

比如：

> “特别提示：”

可能被加粗、放大。

但它并不一定是：

> 章级 Heading。

---

# 十二、所以标题判断通常要组合多个信号

例如：

```text
文本内容
+
编号模式
+
字号
+
加粗
+
缩进
+
居中
+
上下间距
+
页面位置
+
上下文
```

这些一起看。

---

# 十三、编号模式是非常强的信号

政府采购文件特别喜欢编号。

例如：

```text
第一章
第二章
第三章
```

---

# 十四、下一层可能是

```text
一、
二、
三、
```

---

# 十五、还可能是

```text
1.
2.
3.
```

---

# 十六、下一层又可能是

```text
1.1
1.2
1.3
```

---

# 十七、甚至

```text
3.2.1
3.2.2
3.2.3
```

---

# 十八、中文法律和政府文件里还常见

```text
（一）
（二）
（三）
```

再下一层：

```text
1）
2）
3）
```

甚至：

```text
①
②
③
```

---

# 十九、所以我们需要一个 Numbering Grammar

不用把它想成复杂语言学。

就是：

> **建立对编号体系的识别规则。**

比如机器看见：

```text
第三章
```

很可能判断：

```text
level = 1
```

看到：

```text
3.2
```

可能：

```text
level = 2
```

看到：

```text
3.2.1
```

可能：

```text
level = 3
```

---

# 二十、但编号也不能盲信

例如：

```text
1. 供应商应……
```

这可能是：

> 条款编号。

不一定是：

> Section Heading。

---

# 二十一、所以机器需要区分

```text
Section Number
```

和：

```text
Clause Number
```

这不是同一个东西。

---

# 二十二、怎么区分？

看上下文。

比如：

```text
3.2 售后服务要求
```

很像标题。

因为：

- 内容短；
- 没有完整句末；
- 后面跟很多子项。

---

# 二十三、而

```text
1. 供应商应具有……
```

很像 Clause。

因为：

> 已经是完整业务要求。

---

# 二十四、这就是一个很重要的思想

# Structure is contextual

结构不是单个 Block 自己决定的。

还要看：

> 前后 Block。

---

# 二十五、比如连续文本：

```text
3.2 售后服务

1. 提供7×24小时服务热线。

2. 故障发生后2小时内到达现场。

3. 提供不少于3年的维护服务。
```

机器应该推断：

```text
3.2 售后服务
=
Parent Section
```

而下面三个编号项：

> 都属于它。

---

# 二十六、这叫 Parent-Child Relation

也就是：

```text
父节点
↓
子节点
```

---

# 二十七、文档结构恢复真正核心的不是

> “这是标题吗？”

而是：

> **“如果是标题，它是谁的父节点？”**

这一步特别重要。

---

# 二十八、最终 Section Tree 可能长这样

```text
第三章 采购需求
│
├── 3.1 项目概况
│
├── 3.2 售后服务
│     ├── Clause 1
│     ├── Clause 2
│     └── Clause 3
│
└── 3.3 技术参数
      ├── Clause 4
      └── Clause 5
```

---

# 二十九、这时 `section_path` 就可以自动产生

比如 Clause 2：

```text
第三章 采购需求
/
3.2 售后服务
```

也就是：

```text
section_path
```

---

# 三十、上一阶段我们已经知道这个字段非常值钱

因为它可以帮助：

- 模型理解；
- 条款分类；
- 产品定位；
- 错误追踪；
- RAG；
- 数据切片。

---

# 三十一、现在进入今天第二个核心概念

# Clause Segmentation

什么叫 Clause？

可以先理解为：

> **一个能够被独立审查、标注或执行的业务要求单元。**

注意这里没有说：

> “一句话”。

---

# 三十二、这是非常重要的区别

# Clause ≠ Sentence

例如：

> “供应商应提供7×24小时服务热线，并应在收到故障通知后30分钟内响应；对于一级故障，应在2小时内到达现场。”

这里有多个标点。

但业务上：

> 完全可以是一条完整的售后服务要求。

---

# 三十三、如果用普通 Sentence Splitter

可能切成：

```text
A：
供应商应提供7×24小时服务热线。

B：
并应在收到故障通知后30分钟内响应。

C：
对于一级故障，应在2小时内到达现场。
```

---

# 三十四、问题是什么？

B 单独看：

> 主语缺失。

C 单独看：

> 不知道服务对象是谁。

---

# 三十五、所以简单按

```text
。！？；
```

全部切开：

> 很危险。

---

# 三十六、Clause Segmentation 更接近

> **业务语义边界识别。**

它问：

> 哪些文本必须一起看，才能形成一个完整要求？

---

# 三十七、一个采购条款可能只有一句

例如：

> “本项目不接受联合体投标。”

这非常适合作为一个独立 Clause。

---

# 三十八、也可能有三句

例如：

> “项目服务期为三年。合同一年一签。采购人根据年度考核结果决定是否续签。”

这三个句子：

> 很可能属于一个完整合同期限机制。

---

# 三十九、如果拆太细

模型会看不完整。

---

# 四十、如果不拆

整页甚至整章作为一个 Clause，

模型又无法：

> 精确定位风险。

---

# 四十一、所以 Clause Segmentation 的本质又是一个平衡

```text
太细
→ Context丢失

太粗
→ 判断对象不清楚
```

我们要找：

# Business Atomicity

业务原子性。

---

# 四十二、什么叫 Business Atomicity？

就是：

> **再往下拆，就会让一个独立业务要求失去完整意义。**

---

# 四十三、比如

```text
供应商必须是本市注册企业，且注册时间不少于5年。
```

这里有两个条件：

```text
本市注册
+
注册满5年
```

要不要拆成两条？

---

# 四十四、答案不是绝对的

如果未来任务是：

> 风险类型细粒度识别，

可能值得拆。

因为：

```text
本地注册要求
```

和：

```text
企业成立年限
```

可能是两类不同风险。

---

# 四十五、但如果拆以后变成：

```text
且注册时间不少于5年
```

上下文又不完整。

所以更好的做法可能是：

> 保留一个 Parent Clause，

再允许有：

# Sub-conditions

---

# 四十六、例如

```text
Clause C001
供应商必须是本市注册企业，且注册时间不少于5年。

Subcondition 1
必须是本市注册企业

Subcondition 2
注册时间不少于5年
```

这样：

> 既保留完整条款，

又能细粒度分析。

---

# 四十七、这是一种很重要的设计思路

\[
\boxed{
保留原始Clause
+
允许派生Sub-Clause
}
\]

不要一上来：

> 永久切碎原文。

---

# 四十八、这和上一阶段“Lossless First”完全一致

数据工程里我们越来越看到一个共同原则：

> **早期尽量保留，后期按任务派生。**

---

# 四十九、现在看一个真实一点的采购结构

```text
第四章 评标办法

4.1 评标方法

本项目采用综合评分法。

4.2 评分标准

（一）技术部分，满分40分

1. 技术方案，20分
根据投标人技术方案的完整性、可行性评分。

2. 项目经验，10分
每提供一个类似项目业绩得2分，最高10分。

（二）商务部分，满分30分
...
```

---

# 五十、这里到底有哪些 Clause？

可能至少有：

```text
本项目采用综合评分法。
```

以及：

```text
技术方案，20分
根据投标人技术方案的完整性、可行性评分。
```

以及：

```text
项目经验，10分
每提供一个类似项目业绩得2分，最高10分。
```

---

# 五十一、注意第二条

如果只切：

```text
技术方案，20分
```

信息不够。

---

# 五十二、如果只切：

```text
根据投标人技术方案的完整性、可行性评分。
```

又丢了：

> 20 分。

所以这两个 Block：

> 应该属于同一个评分 Clause。

---

# 五十三、这就是为什么 Clause Segmentation 不能只按段落

有时：

```text
多个Paragraph
=
一个Clause
```

---

# 五十四、反过来也可能

一个 Paragraph 里：

> 包含多个 Clause。

例如：

> “供应商应具有软件开发能力；应具备3名高级工程师；应在项目所在地设置服务点。”

三个业务条件挤在一段。

---

# 五十五、所以：

```text
Paragraph
≠
Clause
```

这条也值得记。

---

# 五十六、到这里我们已经有三个不同概念

```text
Sentence
Paragraph
Clause
```

必须彻底分开。

---

# 五十七、Sentence

语言学边界。

例如：

> 句号、问号。

---

# 五十八、Paragraph

版式边界。

例如：

> 一个段落。

---

# 五十九、Clause

业务判断边界。

例如：

> 一个完整资格条件、技术要求、评分项。

---

# 六十、这三个层次偶尔一致

但：

> 经常不一致。

---

# 六十一、现在看表格

假设技术参数表：

| 序号 | 技术指标 | 要求 |
|---|---|---|
| 1 | CPU | 核心数≥32 |
| 2 | 内存 | ≥256GB |
| 3 | 存储 | ≥10TB |

这里每一行：

> 很可能就是一个 Clause。

---

# 六十二、所以 Table Row 也可以变成

# ClauseUnit

例如：

```text
Clause 1
技术指标：CPU
要求：核心数≥32
```

---

# 六十三、但不能只保存：

```text
核心数≥32
```

因为缺少：

> CPU。

---

# 六十四、所以表格 Clause 的 Context 往往包括

```text
Column Header
+
Row Header
+
Cell Content
+
Table Caption
+
Parent Section
```

---

# 六十五、比如：

```text
Section:
第三章 / 技术要求

Table:
服务器技术参数表

Item:
CPU

Requirement:
核心数≥32
```

这样才完整。

---

# 六十六、这就是表格的结构化价值

表格不是：

> 转成纯文本越早越好。

更理想的是先保存：

```text
row
column
header
cell
```

然后根据任务：

> 生成 Clause View。

---

# 六十七、评分表更加明显

| 评分项 | 分值 | 评分规则 |
|---|---:|---|
| 本地服务机构 | 5 | 在本市设有服务机构得5分 |

这里真正要审查的 Clause 不是：

```text
5
```

也不是：

```text
本地服务机构
```

而是完整关系：

```text
本地服务机构
+
5分
+
在本市设有服务机构得5分
```

---

# 六十八、否则模型可能完全不知道

> 这个“5”奖励的是什么。

---

# 六十九、所以结构恢复的目标不仅是标题层级

还包括：

> **业务关系。**

---

# 七十、现在看跨页 Clause

这是政府采购文件特别常见的问题。

第 27 页底部：

```text
供应商应提供本项目所需的技术支持服务，包括但不限于：
```

第 28 页顶部：

```text
（1）7×24小时电话支持；
（2）重大故障2小时内到场；
（3）每季度提供一次巡检服务。
```

---

# 七十一、如果按页独立切

第 27 页：

```text
供应商应提供……包括但不限于：
```

是一条残缺 Clause。

---

# 七十二、第 28 页：

```text
（1）7×24小时电话支持
```

又缺少：

> 主语和上位要求。

---

# 七十三、所以 Page Boundary

不能等价于：

# Clause Boundary

---

# 七十四、这一点特别重要

\[
\boxed{
PageBoundary
\neq
SemanticBoundary
}
\]

PDF 页只是：

> 打印版式。

不是：

> 业务语义边界。

---

# 七十五、所以跨页结构恢复要利用

```text
编号连续
+
句法连续
+
缩进连续
+
Section未变化
```

判断：

> 这是上一页延续。

---

# 七十六、比如上一页最后是：

```text
包括：
```

下一页直接：

```text
（1）
```

这是很强的延续信号。

---

# 七十七、再比如表格

上一页表格有：

```text
序号 评分项 分值
```

下一页继续：

```text
4 企业实力 5分
```

很可能：

> 还是同一张表。

---

# 七十八、所以结构恢复一定要跨页看

不能：

> 每页独立处理后永不联系。

---

# 七十九、现在看另一个危险对象

# Appendix / Attachment

例如：

```text
附件1：
中小企业声明函格式
```

里面也有：

```text
一、
二、
1.
2.
```

编号形式和正文一样。

---

# 八十、如果机器没有识别

```text
附件
```

这个新的 Section Boundary，

可能把模板里的内容：

> 接到采购需求下面。

---

# 八十一、所以一些特殊结构词也很重要

例如：

```text
附件
附表
格式
投标文件格式
合同草案
评分办法
采购需求
资格条件
```

这些往往：

> 是高价值 Structural Anchor。

---

# 八十二、什么叫 Structural Anchor？

就是：

> 对文档层级特别有提示作用的文本。

---

# 八十三、比如：

```text
第三章 采购需求
```

几乎明确告诉你：

> 后面进入采购需求区域。

---

# 八十四、

```text
第四章 评标办法
```

意味着：

> 后面的条款很可能属于评分和评标。

---

# 八十五、这对后面 Risk Type 也有帮助

比如同一句：

```text
在本市设有机构
```

如果位于：

```text
供应商资格条件
```

可能是：

> Qualification Risk。

---

# 八十六、如果位于：

```text
评分标准
```

可能是：

> Scoring Rule Risk。

---

# 八十七、所以 Structure 和 Risk Taxonomy

不是完全独立的。

---

# 八十八、但这里有一个重要边界

不要在结构恢复阶段直接说：

> “这是违规条款。”

结构阶段应该主要回答：

```text
它是什么结构？
属于哪里？
```

---

# 八十九、而风险阶段回答：

```text
它有没有问题？
```

不要混。

---

# 九十、这叫

# Structural Classification

和：

# Compliance Classification

分离。

---

# 九十一、例如结构恢复可以标记：

```text
section_type = supplier_qualification
```

这不代表：

```text
risk_present = true
```

---

# 九十二、资格条件本身：

> 完全可以合法合理。

所以：

\[
\boxed{
SectionType
\neq
RiskLabel
}
\]

---

# 九十三、这个区别非常重要

否则模型很容易学成：

```text
资格条件
=
风险
```

那就废了。

---

# 九十四、现在开始设计 Section Type

为了帮助后续任务，可以给 Section 一个业务类别。

例如第一版：

| Section Type | 含义 |
|---|---|
| procurement_notice | 采购公告 |
| supplier_qualification | 供应商资格 |
| procurement_requirement | 采购需求 |
| technical_requirement | 技术要求 |
| commercial_requirement | 商务要求 |
| scoring_rule | 评分标准 |
| contract_term | 合同条款 |
| attachment | 附件/格式 |

这只是结构标签。

---

# 九十五、为什么不直接只保存标题文字？

因为不同文件会写：

```text
资格要求
```

```text
投标人资格
```

```text
申请人的资格要求
```

```text
供应商条件
```

其实都可能对应：

```text
supplier_qualification
```

---

# 九十六、所以可以同时保存

```text
section_title_raw
```

和：

```text
section_type
```

---

# 九十七、例如：

```json
{
  "section_title_raw": "申请人的资格要求",
  "section_type": "supplier_qualification"
}
```

这样：

> 原文不丢。

同时：

> 结构统一。

---

# 九十八、这是非常好的数据工程习惯

```text
Raw Value
+
Normalized Value
```

两者同时保留。

---

# 九十九、现在设计 Section Node

概念上可以是：

```json
{
  "section_id": "SEC-0032",
  "title": "3.2 售后服务",
  "level": 2,
  "section_type": "commercial_requirement",
  "parent_section_id": "SEC-0030",
  "start_page": 27,
  "end_page": 29
}
```

---

# 一百、注意 `parent_section_id`

这非常关键。

有了它：

> Section Tree 才能重建。

---

# 一百零一、然后 ClauseUnit 可以引用 Section

例如：

```json
{
  "clause_id": "CLAUSE-00178",
  "section_id": "SEC-0032",
  "text": "供应商应保证故障发生后2小时内到达现场。"
}
```

---

# 一百零二、这样就形成：

```text
Document
↓
Section
↓
Clause
```

---

# 一百零三、但 Clause 还应该保存来源 Block

因为以后要追溯。

例如：

```text
source_block_ids
```

可能：

```text
B00872
B00873
```

---

# 一百零四、为什么可能两个 Block？

因为一条 Clause：

> 可能跨两个段落。

或者：

> 跨页。

---

# 一百零五、所以 Clause 不应该强迫：

```text
1 Clause = 1 Block
```

更好的关系是：

```text
1 Clause
←
1..N Source Blocks
```

---

# 一百零六、反过来也可能

```text
1 Block
→
N Clauses
```

因为一个段落可能有多个独立条件。

---

# 一百零七、这说明：

> Block 和 Clause 是不同层。

这个概念一定要稳住。

---

# 一百零八、第 2 阶段的 Block 是

> 页面版式单元。

第 3 阶段的 Clause 是：

> 业务语义单元。

---

# 一百零九、它们关系很多对多

概念上：

```text
Layout Block
   ↕
Clause Unit
```

不是简单一一对应。

---

# 一百一十、现在看嵌套条款

例如：

```text
1. 供应商须满足以下条件：
   （1）具有独立法人资格；
   （2）注册资本不低于5000万元；
   （3）在本市设有固定服务机构。
```

这里到底应该切几条？

---

# 一百一十一、至少有两种表示方式

方式 A：

> 整体作为一个 Clause。

---

# 一百一十二、方式 B：

Parent Clause：

```text
供应商须满足以下条件：
```

三个 Child Clause：

```text
具有独立法人资格
注册资本不低于5000万元
在本市设有固定服务机构
```

---

# 一百一十三、对于我们的风险审查任务

方式 B：

> 更有价值。

因为三个子条件：

> 风险性质可能不同。

---

# 一百一十四、但我们不能丢掉 Parent

因为子条款：

> 是在“供应商须满足以下条件”的语境下成立。

---

# 一百一十五、所以 Clause 本身也可以形成小树

```text
Clause Parent
│
├── Subclause 1
├── Subclause 2
└── Subclause 3
```

---

# 一百一十六、这时可以有：

```text
parent_clause_id
```

---

# 一百一十七、于是文档树可以变成

```text
Project
└── Document
    └── Section
        └── Clause
            └── Sub-Clause
```

这已经非常接近真正的政府采购数据结构。

---

# 一百一十八、但不要无限嵌套

现实文档可能：

```text
1
（1）
1）
①
a.
```

层级非常深。

如果完整复制所有层级：

> 数据会很复杂。

---

# 一百一十九、所以我们要问

> **哪些层级对业务判断真正有用？**

这和 Schema 第一阶段的原则一样：

# Minimal but Sufficient

---

# 一百二十、例如对于 ClauseUnit

第一版可能只保留：

```text
section_path
parent_clause_text
clause_text
```

就已经足够。

数据库内部可以：

> 保留完整树。

训练 View：

> 再简化。

---

# 一百二十一、再次看到

```text
Master Representation
```

和：

```text
Task View
```

的区别。

---

# 一百二十二、现在说一个非常关键的问题

# Clause Boundary Detection

机器究竟怎么判断：

> 一条 Clause 结束了？

---

# 一百二十三、强信号之一：编号变化

例如：

```text
1. 条件A
2. 条件B
```

通常：

> `2.` 是新 Clause 开始。

---

# 一百二十四、但编号也可能在 Clause 内部

例如：

> “服务内容包括：1）巡检；2）培训；3）应急支持。”

这里：

```text
1）
2）
3）
```

可能只是：

> 一个 Clause 里的子项目。

---

# 一百二十五、所以单看编号不够

要看：

> 当前层级。

---

# 一百二十六、如果当前已经在：

```text
1.
```

下面看到：

```text
1）
```

很可能：

> 子级。

---

# 一百二十七、如果连续出现：

```text
1.
2.
3.
```

并且格式一致，

很可能：

> 同级 Clause。

---

# 一百二十八、强信号之二：缩进

例如：

```text
1. 主条款
    （1）子条件
    （2）子条件
```

缩进：

> 帮助推断层级。

---

# 一百二十九、强信号之三：字体与 Style

标题可能：

> 粗体。

Clause：

> 正文字体。

子项：

> 缩进但不加粗。

---

# 一百三十、强信号之四：标点与句法

例如：

```text
供应商应满足以下条件：
```

冒号：

> 很可能提示下面还有子项。

---

# 一百三十一、如果下一 Block 是：

```text
（1）……
```

非常可能：

> 属于上一个 Parent。

---

# 一百三十二、强信号之五：空白距离

标题上下通常：

> 空间更大。

同一 Clause 内连续行：

> 间距更紧。

---

# 一百三十三、强信号之六：页面位置

比如一行：

> 居中、页面顶部、字号大。

更像：

> Heading。

---

# 一百三十四、强信号之七：词汇模式

比如：

```text
采购需求
供应商资格
评审标准
合同条款
技术要求
```

很像：

> Section Anchor。

---

# 一百三十五、所以整体思路不是

```text
if 字号大:
    标题
```

而是：

```text
多个信号
↓
综合判断
```

---

# 一百三十六、这可以用规则做吗？

可以。

第一版其实很适合：

> Rule-based + Heuristic。

因为政府采购文档：

> 编号和格式有很强规律。

---

# 一百三十七、例如简单规则：

```text
如果文本匹配
“第X章”
+
长度短
+
字体较大

→ Heading Level 1
```

---

# 一百三十八、再比如：

```text
如果匹配
^\d+\.\d+
+
后面没有长句
+
后面有多个编号项

→ Section Heading
```

---

# 一百三十九、但规则能解决所有文档吗？

当然不能。

因为现实文件：

> 太乱。

---

# 一百四十、有些标题完全没有编号

例如：

```text
特别资格条件
```

只有：

> 加粗。

---

# 一百四十一、有些正文恰好很短

例如：

```text
不接受联合体。
```

长度也很短。

但：

> 它不是标题。

---

# 一百四十二、所以成熟方案可能是

```text
Rules
+
Layout Features
+
Statistical / ML Model
```

甚至：

> LLM 辅助结构判断。

---

# 一百四十三、但这里有一个重要工程原则

不要一上来就用大模型：

> 识别所有标题和层级。

为什么？

---

# 一百四十四、因为很多结构信号

本来是：

> 确定性规则可以很好识别。

比如：

```text
第三章
```

根本不需要：

> 让 LLM 花钱思考。

---

# 一百四十五、所以推荐：

```text
确定性明显的
→ Rule

模糊的
→ Model

极难的
→ Human Review
```

这又是：

# Hybrid Pipeline

---

# 一百四十六、这和 ProcurementAI 最终架构其实一模一样

```text
规则擅长的
→ Rule Engine

模糊语义判断
→ LLM

高风险边界
→ Human
```

数据工程和产品架构：

> 思路高度一致。

---

# 一百四十七、现在说 Confidence

假设系统识别：

```text
“第三章 采购需求”
```

置信度：

> 很高。

---

# 一百四十八、但遇到：

```text
其他要求
```

它不知道这是：

> 一级标题、二级标题还是正文小标题。

可以：

```text
structure_confidence = low
```

---

# 一百四十九、然后不要硬猜

而是标记：

```text
STRUCTURE_AMBIGUOUS
```

---

# 一百五十、这和第一阶段 `needs_review` 是同一个哲学

> **不确定时允许说不确定。**

不要逼 Pipeline：

> 假装百分之百知道。

---

# 一百五十一、低置信度 Section 会影响什么？

比如：

> 下一步 Clause 属于哪里。

所以可以：

> 触发人工复核。

---

# 一百五十二、特别是 Gold Set 来源文件

我们更应该：

> 提高结构校验标准。

---

# 一百五十三、而大量 CPT Corpus

可能允许：

> 较低的结构精度。

再次出现：

# Purpose-specific Quality Threshold

---

# 一百五十四、现在看一个特别典型的失败案例

原文：

```text
第四章 评标办法

4.2 商务评分

1. 企业业绩，10分。
近三年每提供一个类似项目得2分，最高10分。

2. 服务能力，5分。
在本市设有固定服务机构得5分。
```

---

# 一百五十五、错误切分方法：

```text
Clause A:
企业业绩，10分。

Clause B:
近三年每提供一个类似项目得2分，最高10分。

Clause C:
服务能力，5分。

Clause D:
在本市设有固定服务机构得5分。
```

---

# 一百五十六、问题是

A+B：

> 其实一个评分项。

C+D：

> 也是一个评分项。

---

# 一百五十七、如果拆错

模型看到：

```text
在本市设有固定服务机构得5分。
```

还能判断一些东西。

但失去了：

```text
评分项：服务能力
分值：5
```

---

# 一百五十八、而这些信息对风险解释很重要

因为：

> 它不是资格门槛，

而是：

> 评分加分项。

业务性质：

> 完全不同。

---

# 一百五十九、所以 Clause Segmentation 必须尽量保留

# Functional Context

也就是：

> 这条话在文件里承担什么功能。

---

# 一百六十、例如同一句：

```text
在本市设有服务机构
```

放在：

```text
资格条件
```

含义：

> 进入资格门槛。

---

# 一百六十一、放在：

```text
评分办法
```

含义：

> 竞争评分条件。

---

# 一百六十二、放在：

```text
合同履约要求
```

又可能：

> 是中标后的履约要求。

---

# 一百六十三、三者：

> 风险判断完全可能不同。

---

# 一百六十四、所以我们不应该把 Clause 当成孤岛

更合理：

```text
Clause
+
Section Type
+
Section Path
+
Parent Context
```

一起存在。

---

# 一百六十五、现在第一次设计 `ClauseUnit_V0.1`

可以先长这样：

```json
{
  "clause_id": "CLAUSE-00178",
  "document_id": "DOC-00152-01",

  "section_id": "SEC-0032",
  "section_path": [
    "第三章 采购需求",
    "3.2 售后服务"
  ],
  "section_type": "commercial_requirement",

  "clause_text": "供应商应保证故障发生后2小时内到达项目现场。",

  "parent_clause_text": null,

  "source_block_ids": [
    "B00872"
  ],

  "start_page": 27,
  "end_page": 27,

  "clause_order": 18,

  "structure_confidence": 0.98,

  "warnings": []
}
```

这就是第一版概念。

---

# 一百六十六、如果 Clause 跨页

可能：

```json
{
  "start_page": 27,
  "end_page": 28
}
```

---

# 一百六十七、如果有 Parent

比如：

```text
供应商应满足以下条件：
```

可以：

```json
{
  "parent_clause_id": "CLAUSE-00177"
}
```

---

# 一百六十八、如果来自表格

可以增加：

```text
source_type = table_row
```

或者：

```text
table_id
row_id
```

---

# 一百六十九、例如评分表 Clause

```json
{
  "clause_id": "CLAUSE-00421",
  "section_type": "scoring_rule",

  "table_caption": "商务评分表",
  "row_label": "服务能力",
  "score": 5,

  "clause_text": "在本市设有固定服务机构得5分。"
}
```

注意：

> 不一定最终这么设计。

但思想已经很清楚。

---

# 一百七十、ClauseUnit 最重要的不是字段多

而是保证三件事：

```text
① 知道它是什么

② 知道它属于哪里

③ 知道它从原文哪里来
```

---

# 一百七十一、也就是：

\[
\boxed{
Identity
+
Hierarchy
+
Provenance
}
\]

---

# 一百七十二、这三个是 Clause 数据的骨架

后面才加：

> Annotation。

---

# 一百七十三、现在谈稳定 ID

`clause_id`：

> 不能只用当前行号。

---

# 一百七十四、为什么？

Parser 更新以后：

> Clause 顺序可能变化。

如果 ID 是：

```text
row_328
```

可能全部乱掉。

---

# 一百七十五、可以考虑基于

```text
document_id
+
stable local identifier
```

生成 Clause ID。

---

# 一百七十六、或者再保存：

```text
clause_fingerprint
```

帮助以后追踪：

> 同一条 Clause 在 Parser 版本更新后是否变化。

---

# 一百七十七、比如：

```text
旧 Parser:
CLAUSE-102
文本A

新 Parser:
CLAUSE-102
文本A + 补回漏掉的半句
```

你需要知道：

> 这其实是同一业务条款被修正。

---

# 一百七十八、这会影响后面

# Dataset Versioning

第 11 阶段会专门处理。

现在先埋下意识。

---

# 一百七十九、接下来一个重要问题

# Section Boundary

什么时候一个 Section 结束？

---

# 一百八十、最直接：

> 遇到同级或者更高级 Heading。

例如：

```text
3.1 资格条件
...
3.2 技术要求
```

那么：

```text
3.1
```

结束于：

```text
3.2
```

之前。

---

# 一百八十一、树算法上可以理解为

当出现：

```text
new_level <= current_level
```

就要：

> 关闭当前某些层级。

不用背算法。

记住：

> 标题层级像一个栈。

---

# 一百八十二、可以想象

```text
第三章
    3.1
        3.1.1
```

现在遇到：

```text
3.2
```

说明：

```text
3.1.1结束
3.1结束
```

回到：

```text
第三章
```

下面开：

```text
3.2
```

---

# 一百八十三、这就叫 Hierarchy Stack

是非常常见的结构恢复方法。

---

# 一百八十四、现实中编号会乱怎么办？

例如：

```text
3.1
3.2
3.2.1
3.4
```

缺少：

```text
3.3
```

不能因为编号不连续：

> 就判文档损坏。

---

# 一百八十五、因为原文真的可能：

> 没有 3.3。

所以规则应该：

> 容忍缺号。

---

# 一百八十六、还有重复编号

例如：

```text
1.
1.
2.
```

可能：

> 原文编辑错误。

---

# 一百八十七、结构恢复应该做什么？

保留：

> 原文编号。

同时加：

```text
NUMBERING_INCONSISTENT
```

Warning。

不要偷偷：

> 帮原文改成 1、2、3。

---

# 一百八十八、这又是一个重要原则

# Preserve Source Truth

数据工程：

> 不应该悄悄替原文件“纠错”。

---

# 一百八十九、如果需要规范化编号

可以另存：

```text
normalized_order
```

但原始：

```text
raw_number
```

应该保留。

---

# 一百九十、类似：

```json
{
  "raw_number": "1.",
  "normalized_order": 2
}
```

这样：

> 可追溯。

---

# 一百九十一、现在谈标题正文混排

现实里可能：

```text
3.1 资格条件：供应商应满足以下条件：
```

标题和正文：

> 同一行。

---

# 一百九十二、机器需要拆成

```text
Heading:
3.1 资格条件

Lead Text:
供应商应满足以下条件：
```

---

# 一百九十三、否则如果整行都当 Heading

会丢掉：

> “供应商应满足以下条件”。

---

# 一百九十四、反过来全当正文

又会丢掉：

> Section Heading。

---

# 一百九十五、这说明有时一个 Block：

> 需要内部再拆。

---

# 一百九十六、这叫 Block Refinement

第 2 阶段是：

> Layout Block。

第 3 阶段可以：

> 根据语义继续精炼。

---

# 一百九十七、但不要修改原 Block

更好的方式：

```text
Raw Block
↓
Derived Structural Nodes
```

仍然保留：

> 来源关系。

---

# 一百九十八、例如

```text
B0123
原始：
“3.1 资格条件：供应商应满足以下条件：”
```

派生：

```text
Section Heading
“3.1 资格条件”
```

和：

```text
Lead Clause
“供应商应满足以下条件：”
```

两者都指向：

```text
B0123
```

---

# 一百九十九、这样不会丢 provenance。

---

# 二百、现在讲“标题重复”

跨页打印时可能每页顶部重复：

```text
第三章 采购需求
```

这到底是：

> Header

还是：

> Section Heading？

---

# 二百零一、第 2 阶段已经告诉我们

如果它：

- 每页固定顶部；
- 大量重复；
- 位置稳定；

更可能：

> Running Header。

---

# 二百零二、结构恢复时不能把每一页都当：

> 新的第三章开始。

否则：

> 文档树被切碎。

---

# 二百零三、这说明第 2 阶段的 Layout 信息

会直接帮助第 3 阶段。

课程阶段虽然分开：

> 数据本身是连续流水线。

---

# 二百零四、现在看“目录页”

TOC：

```text
第三章 采购需求 ........ 37
第四章 评标办法 ........ 82
```

里面也有很多标题。

---

# 二百零五、如果机器把目录页也当正文结构

会生成：

> 虚假的 Section。

---

# 二百零六、所以要识别

# Table of Contents

目录。

---

# 二百零七、目录常见信号：

```text
目录
点线
页码
大量标题+数字
```

然后标记：

```text
block_type = toc
```

---

# 二百零八、后续 Structure Recovery：

> 不把它当真正 Section Start。

---

# 二百零九、类似还有

# List of Tables

# List of Figures

在部分技术采购文件中也可能出现。

---

# 二百一十、所以“标题文字出现了”

不等于：

> 文档真的进入那个 Section。

还要看：

> 它出现在哪种结构区域。

---

# 二百一十一、现在进入 Semantic Section Classification

当结构已经识别出：

```text
3.2 申请人的资格要求
```

我们可以再映射：

```text
section_type =
supplier_qualification
```

---

# 二百一十二、这个映射可以先用字典

例如：

```text
资格要求
申请人资格
供应商资格
资格条件
```

映射到：

```text
supplier_qualification
```

---

# 二百一十三、

```text
评分办法
评审标准
评分标准
综合评分表
```

映射到：

```text
scoring_rule
```

---

# 二百一十四、

```text
技术要求
技术参数
技术规格
```

映射到：

```text
technical_requirement
```

---

# 二百一十五、这叫 Normalization Mapping

不是改原文。

而是：

> 额外添加统一类别。

---

# 二百一十六、如果标题是：

```text
其他要求
```

怎么办？

语义太模糊。

可以：

```text
section_type = other
```

或者：

```text
unknown
```

---

# 二百一十七、不要强行分类

这又回到：

> 允许不确定。

---

# 二百一十八、现在看一个完整示例

原始 Parsed Blocks：

```text
B1 第三章 采购需求
B2 3.1 资格条件
B3 1. 供应商应具有独立承担民事责任的能力。
B4 2. 供应商须在本市注册成立5年以上。
B5 3.2 技术要求
B6 1. 数据库服务器内存不得低于256GB。
```

---

# 二百一十九、Structure Recovery 后

```text
SEC1
title = 第三章 采购需求
level = 1
type = procurement_requirement
```

---

# 二百二十、

```text
SEC2
title = 3.1 资格条件
level = 2
parent = SEC1
type = supplier_qualification
```

---

# 二百二十一、

```text
C1
text = 供应商应具有独立承担民事责任的能力。
section = SEC2
```

---

# 二百二十二、

```text
C2
text = 供应商须在本市注册成立5年以上。
section = SEC2
```

---

# 二百二十三、

```text
SEC3
title = 3.2 技术要求
level = 2
parent = SEC1
type = technical_requirement
```

---

# 二百二十四、

```text
C3
text = 数据库服务器内存不得低于256GB。
section = SEC3
```

这时：

> 文档真正开始变成业务数据。

---

# 二百二十五、然后 Stage 1 的 Schema 就可以接进来

比如：

```text
Clause C2
↓
送给专家标注
↓
risk_present
risk_type
rationale
evidence
```

---

# 二百二十六、所以整个链终于连起来

```text
Raw PDF
↓
Parsed Block
↓
Section Tree
↓
ClauseUnit
↓
Task Schema
↓
Annotation
```

---

# 二百二十七、这就是为什么第 1、2、3 阶段顺序不能乱

如果一开始直接：

> 对 PDF 全文做 SFT，

你跳过了：

```text
结构恢复
+
业务单元定义
```

后面几乎一定付出代价。

---

# 二百二十八、现在讲一个非常重要的错误

# Over-segmentation

切得太细。

---

# 二百二十九、例如：

> “投标人应在合同签订后10日内完成系统部署，并在部署完成后提供不少于三年的免费维护服务。”

切成：

```text
投标人应在合同签订后10日内完成系统部署
```

和：

```text
并在部署完成后提供不少于三年的免费维护服务
```

第二段：

> 主语弱化。

---

# 二百三十、而这两个条件：

> 可能属于同一个履约要求。

切太细：

> Context 损失。

---

# 二百三十一、另一个错误：

# Under-segmentation

切得太粗。

---

# 二百三十二、比如整段：

```text
供应商须具备以下条件：
1. 本市注册；
2. 注册资本5000万元以上；
3. 具有ISO认证；
4. 近三年完成5个同类项目；
5. 配备20名工程师。
```

全部作为一个 Clause。

---

# 二百三十三、模型如果说：

> “有风险。”

你很难知道：

> 是哪一项。

---

# 二百三十四、也很难标：

```text
risk_subtype
```

因为里面可能：

> 同时有四种不同风险。

---

# 二百三十五、所以理想结构是：

```text
Parent Clause
供应商须具备以下条件

Child 1
本市注册

Child 2
注册资本5000万元以上

Child 3
ISO认证

Child 4
业绩要求

Child 5
人员要求
```

---

# 二百三十六、这就是

# Hierarchical Segmentation

层级切分。

通常比：

> 暴力平铺

更适合政府采购文件。

---

# 二百三十七、接下来一个特别重要的问题

# Minimal Context Window

切出 Clause 后，

到底带多少上下文给模型？

---

# 二百三十八、如果只带 Clause：

```text
不得低于500万元。
```

不够。

---

# 二百三十九、如果带整份 200 页：

> 太多。

---

# 二百四十、所以第一版可以考虑：

```text
Parent Section Title
+
Parent Clause
+
Target Clause
+
必要邻近文本
```

---

# 二百四十一、例如：

```text
Section:
供应商资格条件

Parent:
供应商应满足以下条件：

Target:
注册资本不得低于5000万元。
```

这已经比：

> 单独一句

强很多。

---

# 二百四十二、如果项目背景很重要

再加：

```text
Project Context
```

例如：

```text
项目预算：
300万元
```

---

# 二百四十三、于是模型就能发现

> 注册资本要求和项目规模之间是否可能失衡。

---

# 二百四十四、这再次连接第一阶段

当时我们说：

\[
\boxed{
TargetClause
+
MinimalNecessaryContext
}
\]

现在我们开始真正知道：

> 这个 Context 从哪里来。

就是：

# Document Structure

---

# 二百四十五、所以结构恢复的价值之一

就是：

> 帮助自动构造合理 Context。

---

# 二百四十六、如果没有 Section Tree

你只能：

> 粗暴取前后 500 字。

---

# 二百四十七、这可能把：

> 无关上一节内容

也塞进来。

---

# 二百四十八、有 Section Tree 后

可以优先取：

```text
同一Section
```

或者：

```text
Parent Clause
```

这会更准确。

---

# 二百四十九、这对 RAG 也同样重要

将来法规 RAG：

> 按法规条款层级切。

采购文件 RAG：

> 按 Section / Clause 切。

通常会比：

> 固定 500 Token 切块

更符合语义。

---

# 二百五十、所以 Clause Segmentation 不是只服务 SFT

它同时服务：

```text
SFT
RAG
Evaluation
UI定位
Error Analysis
```

---

# 二百五十一、例如产品 UI

模型告诉用户：

> 风险出现在：

```text
第三章 采购需求
→ 3.1 供应商资格
→ 第2条
```

而不是：

> “大概在第 17,823 个字符附近。”

结构化数据：

> 直接提升产品体验。

---

# 二百五十二、这就是 Structure 的另一种价值

# Explainability

可追溯定位。

---

# 二百五十三、现在谈 Structure Benchmark

和 Parser 一样，

Structure Recovery：

> 也需要评测。

---

# 二百五十四、不能只是看：

> “好像标题都识别出来了。”

可以建立小型 Gold。

---

# 二百五十五、人工标：

```text
哪些是Heading
Heading Level
Parent Section
Clause Boundary
Clause Parent
Table Row Clause
```

---

# 二百五十六、然后评价

例如：

```text
Heading Detection Accuracy

Hierarchy Accuracy

Clause Boundary Precision

Clause Boundary Recall
```

不用现在背公式。

---

# 二百五十七、直觉上：

如果系统把不是 Clause 的地方：

> 切成很多假 Clause，

Precision 会差。

---

# 二百五十八、如果很多真实 Clause：

> 没切出来，

Recall 会差。

---

# 二百五十九、为什么两个都重要？

切太多：

> 数据碎。

切太少：

> 风险混在一起。

---

# 二百六十、我们甚至可以单独看

```text
Table Clause Accuracy
```

---

# 二百六十一、因为采购文件中：

> 表格是高风险区域。

---

# 二百六十二、还可以单独看

```text
Cross-page Clause Accuracy
```

因为：

> 跨页很容易出错。

---

# 二百六十三、这就是 Slice Evaluation

第一课学过的思维又回来。

---

# 二百六十四、数据工程同样不能只看平均分

一个结构模型：

> 普通段落 99%。

但：

> 评分表只有 60%。

对 ProcurementAI：

> 仍然可能不能用。

---

# 二百六十五、现在设计结构 Warning

可以有：

```text
HEADING_LEVEL_AMBIGUOUS

NUMBERING_INCONSISTENT

CROSS_PAGE_CLAUSE

TABLE_CLAUSE_UNCERTAIN

ORPHAN_SUBCLAUSE

PARENT_MISSING

OVERLONG_CLAUSE
```

---

# 二百六十六、什么叫 Orphan Subclause？

比如：

```text
（2）注册资本不低于500万元
```

但系统找不到：

```text
（1）
```

也找不到 Parent。

---

# 二百六十七、这可能说明：

- 上一页漏解析；
- Parent 被误删；
- 编号本来就错；
- Clause Boundary 错。

应该：

> 标 Warning。

---

# 二百六十八、什么叫 Overlong Clause？

如果系统切出：

```text
18,000字
```

一个 Clause，

大概率：

> 切分失败。

---

# 二百六十九、当然不是说超过某字数一定错。

而是：

> 异常检测信号。

---

# 二百七十、同理 Extremely Short Clause

比如只有：

```text
“如下：”
```

也可能只是：

> Parent Lead Text。

不应该当独立业务 Clause。

---

# 二百七十一、所以结构质量检查可以利用

```text
长度分布
编号模式
父子关系
Section一致性
```

自动发现异常。

---

# 二百七十二、这其实越来越像编译器

原始文件：

> 像源代码。

Parser：

> 读字符和布局。

Structure Recovery：

> 建 AST。

---

# 二百七十三、AST 是什么？

Abstract Syntax Tree。

不用记术语。

只要知道：

> 把平面的符号恢复成有层级的结构树。

---

# 二百七十四、政府采购文档也可以有自己的“文档 AST”

例如：

```text
Document
├── Chapter
│   ├── Section
│   │   ├── Clause
│   │   └── Clause
│   └── Section
└── Appendix
```

---

# 二百七十五、这个类比很漂亮

因为以后很多操作：

> 都可以在树上完成。

---

# 二百七十六、比如删除整段页眉

在 Block 层。

---

# 二百七十七、比如找全部技术要求

查：

```text
section_type = technical_requirement
```

---

# 二百七十八、比如取某 Clause 的 Parent

直接：

> 向树上走一层。

---

# 二百七十九、比从一整串字符串里：

> 正则乱找

可靠得多。

---

# 二百八十、现在看一个复杂案例

原文：

```text
第三章 采购需求

一、项目概况
……

二、服务要求

（一）人员要求

1. 项目经理应具有……
2. 项目团队不少于10人。

（二）响应要求

供应商应提供7×24小时服务，并满足以下要求：
1）普通故障30分钟内响应；
2）重大故障2小时内到场；
3）每季度开展一次巡检。
```

---

# 二百八十一、文档树应该大致是

```text
第三章 采购需求
│
├── 一、项目概况
│
└── 二、服务要求
     │
     ├── （一）人员要求
     │     ├── Clause 1
     │     └── Clause 2
     │
     └── （二）响应要求
           └── Parent Clause
                 ├── Subclause 1
                 ├── Subclause 2
                 └── Subclause 3
```

---

# 二百八十二、这就是我们真正想恢复的东西。

---

# 二百八十三、如果只是 Plain Text

你只有：

> 一串字。

---

# 二百八十四、有 Tree 后

你知道：

```text
重大故障2小时内到场
```

属于：

```text
采购需求
→ 服务要求
→ 响应要求
```

---

# 二百八十五、这就是 Structural Semantics

结构本身：

> 就带语义。

---

# 二百八十六、再看一个评分表案例

```text
第四章 评标办法

商务评分表

项目经验 | 10分 | 每个同类项目2分
本地服务 | 5分  | 本市有服务机构得5分
人员资质 | 5分  | 每名高级工程师1分
```

---

# 二百八十七、Structure Recovery 后最好不是：

```text
10分
5分
5分
```

---

# 二百八十八、而是：

```text
评分项1
name = 项目经验
score = 10
rule = 每个同类项目2分
```

---

# 二百八十九、

```text
评分项2
name = 本地服务
score = 5
rule = 本市有服务机构得5分
```

---

# 二百九十、然后每一个评分项：

> 都可以派生为 Clause。

---

# 二百九十一、未来模型审查：

```text
risk_type = scoring_rule
```

就非常自然。

---

# 二百九十二、所以表格恢复和 Clause Segmentation

要协同。

但依然建议：

> 先保留 Table Structure，

再派生 Clause。

---

# 二百九十三、现在讲一个常见错误

# Flatten First

有人会：

```text
所有表格
↓
转成Markdown字符串
↓
以后只保存字符串
```

---

# 二百九十四、这样方便喂 LLM。

但代价是：

> Row / Cell 原始关系可能丢失。

---

# 二百九十五、更好的方法：

```text
Structured Table
作为Master
```

然后生成：

```text
Markdown View
```

供模型使用。

---

# 二百九十六、这再次是：

```text
Master Representation
>
Task Representation
```

---

# 二百九十七、现在讲文件里的“注释”

比如：

```text
注：
1. 本项仅适用于……
2. 如为联合体……
```

这些是不是 Clause？

---

# 二百九十八、答案：

> 有时是。

因为“注”可能改变：

> 上面规则的适用范围。

---

# 二百九十九、所以不能简单把：

```text
注：
```

都当无关文本。

---

# 三百、需要判断它是：

```text
explanatory_note
```

还是：

> 真正具有约束意义的条件。

---

# 三百零一、所以结构类型还可以包括

```text
note
remark
footnote
```

---

# 三百零二、尤其表格脚注

例如：

> “以上证书须在有效期内，否则不得分。”

虽然只是表格下面一行小字。

但业务上：

> 非常重要。

---

# 三百零三、如果 Parser 或 Structure Recovery 把它当普通 Footer 删除

就出大问题。

---

# 三百零四、所以“看起来像脚注”

不等于：

> 无业务意义。

要区分：

```text
页面Footer
```

和：

```text
业务Footnote
```

---

# 三百零五、这也是为什么仅靠位置：

> 不够。

还需要内容语义。

---

# 三百零六、现在看“合同条款”

合同草案可能有：

```text
第十二条 违约责任
12.1 ...
12.2 ...
12.3 ...
```

结构非常像法规。

Clause Segmentation：

> 也可以沿同一框架处理。

---

# 三百零七、所以今天学的不是：

> 只适用于招标文件的技巧。

而是一套：

# Hierarchical Document Parsing

通用框架。

---

# 三百零八、未来法规 RAG 也会用

例如：

```text
法律
↓
章
↓
节
↓
条
↓
款
↓
项
```

---

# 三百零九、所以第四课第 3 阶段

其实也在为第 6 课 RAG：

> 提前打地基。

---

# 三百一十、现在讨论一条 Clause 是否需要保留原始编号

答案：

> 强烈建议保留。

比如：

```text
raw_clause_number = "（三）"
```

---

# 三百一十一、为什么？

用户以后问：

> “第三章第二节第（三）项为什么有风险？”

系统可以：

> 精确对应。

---

# 三百一十二、法律和采购工作非常重视

# Citation / Localization

也就是：

> 能不能定位回原文。

---

# 三百一十三、所以 Clause 应该尽量保存：

```text
page
section_path
raw_number
source_blocks
```

---

# 三百一十四、如果来自表格：

```text
table_caption
row_label
column_labels
```

也应该尽量保留。

---

# 三百一十五、这会让最终审查报告

从：

> “AI 说有风险”

升级为：

> “第三章采购需求 → 供应商资格条件 → 第（二）项存在潜在风险。”

这才是专业系统。

---

# 三百一十六、现在看数据切分的提前收益

同一项目里：

> 很多 Clause。

它们全部有：

```text
project_id
```

以及：

```text
document_id
```

---

# 三百一十七、第 6 阶段切数据时

就可以：

```text
Group by Project
```

而不是：

> 按 Clause 行随机切。

---

# 三百一十八、如果 Section / Clause 来源丢了

之后想修复：

> 非常难。

所以今天保存 Hierarchy：

> 其实也在帮后面防数据泄漏。

---

# 三百一十九、现在设计一个 Clause Quality Status

例如：

```text
auto_segmented
```

---

# 三百二十、

```text
human_verified
```

---

# 三百二十一、

```text
structure_uncertain
```

---

# 三百二十二、为什么值得有？

因为自动切出的 Clause：

> 并不都同样可信。

---

# 三百二十三、未来 Gold Set

可以优先使用：

```text
human_verified
```

---

# 三百二十四、大规模预训练数据

可能允许：

```text
auto_segmented
```

---

# 三百二十五、再次强调：

> 数据质量是分层的。

不需要所有数据：

> 用最高成本处理。

---

# 三百二十六、现在做一次完整的 Structure Pipeline

总图：

```text
ParsedDocument
      │
      ▼
过滤Layout噪声标记
      │
      ▼
Heading Candidate Detection
      │
      ▼
Heading Level Inference
      │
      ▼
Section Tree Construction
      │
      ▼
Section Type Normalization
      │
      ▼
Paragraph / List / Table Analysis
      │
      ▼
Clause Boundary Detection
      │
      ▼
Parent / Child Clause Recovery
      │
      ▼
Cross-page Merge
      │
      ▼
Clause Quality Check
      │
      ▼
ClauseUnit_V0.1
```

这就是这一阶段的工程主线。

---

# 三百二十七、再把三个层级放在一起

```text
L1 Parsed Block
```

回答：

> 页面上有什么内容？

---

# 三百二十八、

```text
L2 Document Structure
```

回答：

> 这些内容属于哪一章、哪一节？

---

# 三百二十九、

```text
L3 Clause Unit
```

回答：

> 哪个最小业务要求应该成为训练/审查对象？

---

# 三百三十、然后第 4 层才是

```text
L4 Annotation
```

回答：

> 这个 Clause 有没有风险？

---

# 三百三十一、层层分开

最大的好处：

> 出错能定位。

---

# 三百三十二、例如某条模型预测错了

你可以检查：

```text
模型错？
```

如果不是：

```text
Label错？
```

再不是：

```text
Clause切错？
```

再不是：

```text
Section归错？
```

再不是：

```text
Parser错？
```

---

# 三百三十三、这就是：

# Debuggable Data Pipeline

可调试的数据流水线。

---

# 三百三十四、对专业 AI 项目特别重要

因为很多所谓：

> 模型错误

其实是：

> 数据工程错误。

---

# 三百三十五、本阶段最容易犯的 12 个错误

**错误 1：**

> 句号就是 Clause 边界。

错。

**错误 2：**

> Paragraph 就等于 Clause。

错。

**错误 3：**

> Block 就等于 Clause。

错。

**错误 4：**

> 页尾就是 Clause 结束。

错。

**错误 5：**

> 标题字号大就一定是 Heading。

错。

**错误 6：**

> 有编号就一定是新 Clause。

错。

可能是子项。

**错误 7：**

> 表格转成全文字符串以后结构就不重要了。

错。

**错误 8：**

> Section Type 就是 Risk Type。

错。

**错误 9：**

> Clause 越短越适合训练。

错。

**错误 10：**

> Clause 越长信息越完整，所以越好。

也错。

**错误 11：**

> 自动结构恢复必须强行给每个地方一个确定答案。

错。

允许 Warning / Unknown。

**错误 12：**

> 只保留最终 Clause 文本就够。

不够。

还需要：

> Hierarchy + Provenance。

---

# 三百三十六、本阶段最重要的 5 个“≠”

```text
Sentence
≠
Clause
```

```text
Paragraph
≠
Clause
```

```text
Block
≠
Clause
```

```text
Page Boundary
≠
Clause Boundary
```

```text
Section Type
≠
Risk Label
```

如果这五个不再混，

本阶段已经成功了一半。

---

# 三百三十七、再记一个最重要的“=”

\[
\boxed{
ClauseUnit
=
BusinessAtomicRequirement
+
StructuralContext
+
SourceProvenance
}
\]

翻译成人话：

> **一条 Clause 不只是那一句文字，而是一个尽量完整的业务要求，加上它属于哪一章哪一节，以及它能回到原文件哪里。**

---

# 三百三十八、现在看 Stage 1～3 的完整关系

```text
第四课 · Stage 1
Task Schema
“未来一条训练样本应该是什么？”

             ↓

第四课 · Stage 2
ParsedDocument
“原文件怎样恢复成可信机器文本？”

             ↓

第四课 · Stage 3
ClauseUnit
“可信文本怎样恢复成业务结构和条款？”
```

现在数据已经第一次从：

```text
文件
```

走到：

```text
业务单元
```

---

# 三百三十九、这一步的重要性非常大

因为从下一阶段开始，

我们才能真正讨论：

> 哪些东西应该删？

> 哪些东西应该规范化？

> 数字、空格、标点到底能不能改？

也就是：

# Cleaning

---

# 三百四十、第 3 阶段掌握测试

如果现在不看前文，你能够自己解释下面这些问题，本阶段就真正掌握：

> 为什么正确提取文字以后仍然需要 Structure Recovery？

> 为什么文档结构更像一棵树，而不是一串字符串？

> Heading Detection 为什么不能只靠字号？

> 编号体系为什么对政府采购文档特别重要？

> Section Number 和 Clause Number 为什么不同？

> 什么叫 Parent-Child Relation？

> `section_path` 为什么对模型理解和产品定位都重要？

> Clause 为什么不能简单定义成一句话？

> Sentence、Paragraph、Block、Clause 四者有什么区别？

> 什么叫 Business Atomicity？

> 为什么一条 Clause 可能由多个 Block 组成？

> 为什么一个 Block 也可能包含多个 Clause？

> 为什么 Parent Clause 和 Sub-Clause 最好都保留？

> 为什么 Page Boundary 不能作为 Clause Boundary？

> 跨页 Clause 怎样判断连续性？

> 为什么表格的一行可以成为一个 Clause？

> 为什么评分项需要把“评分名称 + 分值 + 规则”一起保存？

> 为什么 Table Master Structure 不应该过早 flatten？

> `section_type` 和 `risk_type` 为什么不能混？

> 为什么 Raw Section Title 和 Normalized Section Type 最好同时保留？

> Clause 为什么要保存 source_block_ids？

> 为什么 Clause ID 需要稳定？

> 为什么编号不连续不代表结构一定错误？

> 为什么原始编号应该保留，而不是自动偷偷纠正？

> 什么叫 Over-segmentation？

> 什么叫 Under-segmentation？

> 为什么 Hierarchical Segmentation 比暴力切段更适合采购文件？

> Minimal Context 为什么可以由 Section Tree 帮助构造？

> Structure Recovery 为什么同时服务 SFT、RAG、评测和产品 UI？

> 为什么结构解析也需要自己的 Gold Set 和 Benchmark？

> 为什么 Gold 数据更适合使用人工确认过的 ClauseUnit？

如果这些你都能讲清楚：

\[
\boxed{
第四课第3阶段真正掌握
}
\]

---

# 三百四十一、本阶段最终只记一句话

> **Clause Segmentation 不是把文本按句号切开，而是把一个采购文档重新恢复成“章—节—条款”的业务树：让每一条 Clause 既是尽量完整的最小业务要求，又保留它的父级章节、必要上下文以及回到原文件页码和 Block 的来源路径。**

最后把整个阶段压成一张图：

```text
                 ParsedDocument
                       │
                       ▼
                Layout Blocks
                       │
                       ▼
              Heading Detection
                       │
                       ▼
                Section Tree
             ┌─────────┴─────────┐
             ▼                   ▼
       Section Type         Parent / Child
             │                   │
             └─────────┬─────────┘
                       ▼
              Clause Segmentation
                       │
              ┌────────┼────────┐
              ▼        ▼        ▼
           Paragraph  List    Table Row
              │        │        │
              └────────┼────────┘
                       ▼
               Parent / Sub-Clause
                       │
                       ▼
                 ClauseUnit_V0.1
                       │
            ┌──────────┼──────────┐
            ▼          ▼          ▼
           SFT        RAG       Evaluation
```

---

# 下一阶段：第四课 · 第 4 阶段
## 数据清洗与规范化——为什么“看起来更干净”不一定代表“数据更正确”？哪些东西可以删，哪些字符绝对不能乱改？

第 4 阶段我们会第一次真正做：

# Cleaning

但重点绝不是：

> 多写几个 `.replace()`。

我们会专门解决一个很危险的问题：

```text
清洗
≠
把文本改得漂亮
```

比如：

```text
500 万元
```

能不能自动改成：

```text
500万元
```

通常问题不大。

但：

```text
不得低于500万元
```

如果清洗程序误删：

```text
不得
```

整个语义直接翻转。

下一阶段我们会建立：

```text
Raw Text
↓
Normalized Text
```

之间的安全边界，并拆清：

**空格、Unicode、全半角、页码、重复 Header/Footer、乱码、OCR 噪声、数字、单位、日期、编号、否定词、表格内容以及规范化日志应该怎样处理。**

最终得到：

# `CleanClause_V0.1`

也就是第一次把 `ClauseUnit_V0.1` 变成真正可以进入后续去重、切分和标注流程的高质量文本单元。

---
