# 第四课 · 第 4 阶段：数据清洗与规范化
## 为什么“看起来更干净”不一定代表“数据更正确”？哪些东西可以删，哪些字符绝对不能乱改？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **Cleaning ≠ Rewriting 清洗不是改写原文**
2. **原始文本必须保留， Normalized Text 应该是派生版本**
3. **可以统一“表现形式”， 不能擅自统一“业务含义”**
4. **数字、单位、否定词、比较符号、日期、编号 都属于高风险信息**
5. **自动修复必须可追踪、可回滚、可审计**
6. **不确定的时候， 宁可标 Warning，也不要偷偷猜**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Raw Document` | 原始文档：未经结构化处理的采购文件源材料 |
| `Normalization` | 规范化：稳定中间激活与训练过程 |
| `OCR` | OCR：把扫描图像中的文字转换成机器可读文本 |
| `Block` | 版面块：文档解析后保留布局和位置的基本块 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Value` | Value/V：被注意力权重实际汇聚的内容向量 |
| `Recovery` | 恢复：工具失败或中断后安全重试、降级和继续 |
| `Tokenizer` | 分词器：文本与 Token ID 之间的编码/解码组件 |
| `Layout` | 版面结构：文字块、表格、列、坐标和阅读顺序信息 |
| `Transformer` | Transformer：以注意力和前馈网络为核心的序列架构 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |

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

第三阶段结束以后，我们已经完成了一件非常关键的事：

```text
Raw Document
      ↓
ParsedDocument_V0.1
      ↓
Section Tree
      ↓
ClauseUnit_V0.1
```

也就是说，现在机器已经不只是拿到一堆 PDF 字符，而是开始知道：

```text
这句话来自哪个项目
来自哪份文件
属于哪一章
属于哪一节
是不是一条完整 Clause
原文在哪一页
由哪些 Block 构成
```

接下来很多团队会非常自然地做一件事：

> “现在文本有了，我们清洗一下吧。”

然后开始：

```python
text = text.replace(" ", "")
text = text.replace("\n", "")
text = text.replace("\t", "")
text = text.strip()
```

再加几十条正则。

最后数据看起来非常漂亮。

但这里藏着第四课里一个非常危险的问题：

# “更干净”不一定等于“更正确”。

例如原文是：

```text
投标报价不得超过 500 万元。
```

清理成：

```text
投标报价不得超过500万元。
```

通常没什么问题。

但如果某个清洗规则把：

```text
不得
```

误删，变成：

```text
投标报价超过500万元。
```

这已经不是格式错误了。

而是：

> **语义被反转。**

所以第四阶段真正要建立的不是一堆 `.replace()`。

而是：

# 一套“安全清洗”的边界意识。

---

# 一、本阶段真正要解决的一个核心问题

今天只解决：

> **怎样在不改变采购文件原始业务含义的前提下，把 `ClauseUnit_V0.1` 变成适合去重、标注、训练、检索和评测的规范文本？**

也就是：

```text
ClauseUnit_V0.1
      ↓
Safe Normalization
      ↓
CleanClause_V0.1
```

这里最重要的词不是：

> Clean。

而是：

# Safe

---

# 二、先建立今天最重要的 6 个核心心智模型

```text
① Cleaning ≠ Rewriting
   清洗不是改写原文

② 原始文本必须保留，
   Normalized Text 应该是派生版本

③ 可以统一“表现形式”，
   不能擅自统一“业务含义”

④ 数字、单位、否定词、比较符号、日期、编号
   都属于高风险信息

⑤ 自动修复必须可追踪、可回滚、可审计

⑥ 不确定的时候，
   宁可标 Warning，也不要偷偷猜
```

如果这六句话真正理解，

第四阶段最重要的东西就掌握了一半。

---

# 三、先把 Cleaning 和 Normalization 分开

这两个词经常混着用。

可以先这样理解。

# Cleaning

主要解决：

> 明显噪声。

例如：

```text
重复页眉
重复页脚
乱码控制字符
OCR产生的异常空白
无意义的页面装饰
```

---

# 四、Normalization

主要解决：

> 同一个东西有很多不同写法。

例如：

```text
５００万元
```

和：

```text
500万元
```

可以规范成：

```text
500万元
```

因为：

> 全角数字和半角数字在这里通常只是表现形式不同。

---

# 五、但这两个操作都不能变成

# Semantic Editing

例如：

```text
注册资本不低于500万元
```

不能为了“更自然”改成：

```text
企业规模应达到较高水平
```

这已经不是 Normalization。

而是：

> 改写。

---

# 六、所以今天第一个非常重要的边界

\[
\boxed{
Normalization
\neq
Paraphrasing
}
\]

我们的目标不是让文字：

> 更漂亮。

而是让文字：

> **机器更容易稳定处理，同时保持原始语义。**

---

# 七、最推荐的数据结构是什么？

永远不要只有：

```text
clean_text
```

最好至少保留：

```text
raw_text
```

和：

```text
normalized_text
```

例如：

```json
{
  "raw_text": "供应商注册资本不得低于５００ 万元。",
  "normalized_text": "供应商注册资本不得低于500万元。"
}
```

---

# 八、为什么一定要保留 Raw？

因为半年后如果有人问：

> “500 万元是不是原文件真的这么写？”

你可以直接检查：

```text
raw_text
```

---

# 九、如果只保存 Normalized Text

你看到：

```text
500万元
```

却不知道：

> 原来是不是 `５００ 万元`

甚至不知道：

> 清洗器有没有把别的东西改错。

---

# 十、所以推荐的基本结构是

```text
Original Source
      ↓
Raw Parsed Text
      ↓
Normalized Text
      ↓
Training / Retrieval View
```

而不是：

```text
Original
↓
疯狂replace
↓
覆盖原文
```

---

# 十一、这和照片修图完全一样

你不会因为：

> 调亮了照片

就把：

> RAW 原片删掉。

数据工程也一样。

---

# 十二、今天第二个核心心智模型

# 派生，不覆盖

可以记成：

\[
\boxed{
Raw
\rightarrow
Derived
}
\]

而不是：

\[
\boxed{
Raw
\rightarrow
Overwrite
}
\]

---

# 十三、现在开始处理最基础的问题：Whitespace

空格。

政府采购解析结果里可能出现：

```text
供应商    应    具有
```

或者：

```text
供应商应具 有独立承担民事责任的能力
```

---

# 十四、这些空格可能来自

```text
PDF坐标
OCR
表格
中英文排版
人为输入
```

所以空格清洗：

> 不能只写一句 `replace(" ", "")`。

---

# 十五、为什么全部删除空格很危险？

例如：

```text
Windows Server 2025
```

删掉以后：

```text
WindowsServer2025
```

Tokenizer 和检索结果可能发生变化。

---

# 十六、再比如型号

```text
ABC 1000 Pro
```

变成：

```text
ABC1000Pro
```

可能已经不是：

> 原始型号写法。

---

# 十七、又例如英文法规、技术参数

```text
SQL Server
```

空格本身：

> 有意义。

---

# 十八、所以更合理的方法是

针对：

# 异常空格

做规则。

而不是：

> 删除所有空格。

---

# 十九、例如中文字符之间

```text
供 应 商
```

如果确认这是 OCR 导致的：

> 单字间空格，

可以安全考虑合并。

---

# 二十、但：

```text
Microsoft SQL Server
```

不能按同样规则处理。

---

# 二十一、所以空格 Normalization 需要理解

```text
字符类型
+
邻近字符
+
语言模式
```

而不是：

> 全局删除。

---

# 二十二、现在看换行

第三阶段已经知道：

```text
Visual Line Break
≠
Semantic Boundary
```

所以：

```text
供应商不得以不合理条件对其他供
应商实行差别待遇。
```

应该恢复成：

```text
供应商不得以不合理条件对其他供应商实行差别待遇。
```

---

# 二十三、但不能把所有换行都删除

例如：

```text
1. 资格条件
2. 技术要求
3. 商务要求
```

如果合成：

```text
1.资格条件2.技术要求3.商务要求
```

结构反而坏了。

---

# 二十四、所以要区分

```text
layout_line_break
```

和：

```text
semantic_break
```

---

# 二十五、这也是为什么 Cleaning 最好发生在

# Structure Recovery 之后

因为第三阶段已经告诉我们：

> 哪些 Block 属于同一个 Clause。

---

# 二十六、如果在结构恢复之前就疯狂删除换行

你可能把：

> 原本有价值的版式信号

提前毁掉。

---

# 二十七、这就是课程为什么设计成

```text
Stage 2 Parsing
      ↓
Stage 3 Structure
      ↓
Stage 4 Cleaning
```

而不是反过来。

---

# 二十八、现在进入 Unicode

Unicode 是什么不用深入。

只要理解：

> 同样看起来的字符，计算机内部可能有不同编码表示。

---

# 二十九、例如：

```text
ＡＢＣ１２３
```

这是全角。

而：

```text
ABC123
```

是半角。

---

# 三十、对很多自然语言任务来说

把：

```text
ＡＢＣ１２３
```

规范成：

```text
ABC123
```

通常是合理的。

---

# 三十一、因为业务含义一般没有变化

只是：

> 字符表现形式不同。

---

# 三十二、这种操作属于

# Unicode Normalization

---

# 三十三、但 Unicode Normalization 也不能闭眼做

例如某些：

- 数学符号；
- 法律符号；
- 特殊单位；
- 技术型号；

不同字符：

> 可能真的代表不同含义。

---

# 三十四、比如

```text
≤
```

和：

```text
<
```

绝对不能认为：

> 差不多。

---

# 三十五、因为：

```text
≤ 10
```

表示：

> 可以等于 10。

而：

```text
< 10
```

表示：

> 不可以等于 10。

---

# 三十六、对于技术参数

这一点尤其危险。

例如：

```text
响应时间≤2小时
```

和：

```text
响应时间<2小时
```

并不是完全相同要求。

---

# 三十七、再比如：

```text
≥
```

和：

```text
>
```

也不能随便互换。

---

# 三十八、所以比较运算符属于

# High-risk Symbols

高风险符号。

---

# 三十九、采购数据中建议特别保护的符号包括：

```text
>
<
≥
≤
=
≠
%
‰
±
～
-
+
/
×
```

它们很多：

> 直接改变条件。

---

# 四十、例如

```text
5±0.5mm
```

如果清洗成：

```text
50.5mm
```

那就是灾难。

---

# 四十一、再比如：

```text
1:1000
```

不能随便变成：

```text
11000
```

---

# 四十二、所以第三个核心心智模型：

> **标点不总是装饰。**

技术文档里的符号：

> 经常就是数据本身。

---

# 四十三、现在看数字

采购文档中数字极其重要。

例如：

```text
500万元
3年
2小时
5分
10%
20人
3个项目
```

这些很多时候：

> 就是风险判断的核心。

---

# 四十四、所以数字 Normalization 必须特别保守

例如：

```text
５００
```

转成：

```text
500
```

一般安全。

---

# 四十五、但是：

```text
5OO
```

这里到底是：

```text
500
```

还是字母：

```text
O
```

就不能直接猜。

---

# 四十六、尤其 OCR 常见：

```text
0 ↔ O

1 ↔ I

5 ↔ S

8 ↔ B
```

如果自动修：

> 可能修对。

也可能：

> 创造假数据。

---

# 四十七、例如型号：

```text
ABO-100
```

里面的 `O`：

> 可能真的就是字母 O。

你如果改成：

```text
AB0-100
```

反而错了。

---

# 四十八、所以 OCR Correction 应分两类

```text
High-confidence Correction
```

和：

```text
Ambiguous Correction
```

---

# 四十九、例如

```text
５００万元
```

全角→半角：

> 高置信度。

---

# 五十、而：

```text
S00万元
```

猜成：

```text
500万元
```

应该：

> 谨慎得多。

---

# 五十一、如果上下文非常明确：

```text
项目预算为S00万元
```

机器可以产生：

```text
correction_candidate = "500万元"
```

但最好不要：

> 静默覆盖。

---

# 五十二、而是记录：

```text
raw:
S00万元

normalized:
500万元

correction_type:
ocr_candidate

confidence:
0.82
```

甚至：

```text
needs_review = true
```

---

# 五十三、这就是第四个核心心智模型：

# 自动修复要有证据等级

不是：

> “我觉得像错字，所以改了。”

---

# 五十四、特别是金额

例如：

```text
500万元
```

和：

```text
5000万元
```

只差一个 0。

但业务意义：

> 差一个数量级。

---

# 五十五、所以金额应该视为：

# Critical Field

关键字段。

---

# 五十六、类似还有：

```text
分值
百分比
日期
年限
数量
人数
距离
响应时间
业绩数量
注册资本
预算金额
```

这些字段：

> 都值得更严格保护。

---

# 五十七、现在看单位

例如：

```text
500 万元
```

变成：

```text
500万元
```

通常安全。

---

# 五十八、但：

```text
500元
```

和：

```text
500万元
```

绝对不能混。

---

# 五十九、所以不要做一种荒唐 Normalization：

```text
所有金额
统一变成数字
```

例如只保存：

```text
500
```

因为：

> 单位丢了。

---

# 六十、正确方式可以是

保留文本：

```text
500万元
```

同时结构化派生：

```json
{
  "amount_value": 500,
  "amount_unit": "万元"
}
```

---

# 六十一、甚至进一步：

```json
{
  "amount_cny": 5000000
}
```

但注意：

> 这是结构化派生字段。

不是修改原文。

---

# 六十二、原文仍然保留：

```text
500万元
```

---

# 六十三、这是一个非常重要的数据工程习惯

\[
\boxed{
NormalizeByAddingStructure
>
NormalizeByDestroyingText
}
\]

中文：

> **能通过增加结构化字段解决的问题，不要靠破坏原文解决。**

---

# 六十四、比如日期

原文：

```text
2026年9月15日
```

我们可以结构化成：

```text
2026-09-15
```

但不需要删掉原文本身。

---

# 六十五、可以保存：

```json
{
  "date_raw": "2026年9月15日",
  "date_iso": "2026-09-15"
}
```

---

# 六十六、这样既方便机器排序，

又可以：

> 精确回到原文。

---

# 六十七、但日期也有危险情况

例如：

```text
2026年9月
```

不能自动补成：

```text
2026-09-01
```

因为原文：

> 根本没有说 1 日。

---

# 六十八、这叫：

# Information Fabrication

制造原文不存在的信息。

---

# 六十九、所以 Normalization 可以

> 统一已有信息。

不能：

> 补造未知信息。

---

# 七十、再看一个日期

```text
9月15日前
```

不要只结构化成：

```text
2026-09-15
```

因为你会丢掉：

```text
前
```

也就是：

> Deadline Semantics。

---

# 七十一、所以业务语义字段可能是：

```text
date = 2026-09-15
operator = before_or_on
```

而不是：

> 只剩日期。

---

# 七十二、这和比较符号完全一样

文本：

```text
不少于3年
```

可以结构化成：

```text
operator = >=
value = 3
unit = year
```

但原文：

> 仍保留。

---

# 七十三、这类结构化会对后面规则引擎非常有价值

比如：

```text
registration_years >= 5
```

可以直接进入：

> 规则检查。

---

# 七十四、但是注意：

# Extraction ≠ Cleaning

抽取：

```text
operator/value/unit
```

属于：

> 更高层的数据结构化。

今天我们只是提前建立正确思路。

---

# 七十五、现在进入极其危险的一类字符

# Negation

否定词。

政府采购中常见：

```text
不
不得
不应
不可
无需
不得超过
不得低于
不接受
不允许
禁止
未
无
```

---

# 七十六、这些词绝对不能当“停用词”

普通 NLP 时代经常有人做：

```text
Stopword Removal
```

把：

```text
的
了
和
不
```

之类删掉。

---

# 七十七、如果把：

```text
不
```

删掉：

```text
本项目不接受联合体
```

变成：

```text
本项目接受联合体
```

意思直接反转。

---

# 七十八、所以对于我们的 ProcurementAI：

# 不建议做传统停用词删除

至少：

> 绝不能把否定词机械删除。

---

# 七十九、事实上现代 Transformer

通常也：

> 不需要把自然语言预先删成关键词袋。

---

# 八十、模型真正需要的是：

> 完整语义。

不是：

```text
项目
接受
联合体
```

这种残缺关键词。

---

# 八十一、所以第五个核心心智模型

\[
\boxed{
LLM Cleaning
\neq
传统Bag-of-Words预处理
}
\]

---

# 八十二、我们不会做类似：

```text
去停用词
词干化
删标点
只留关键词
```

这种传统文本分类式暴力处理。

---

# 八十三、因为对 LLM 来说：

> 语法、关系、否定、条件、修饰范围

都很重要。

---

# 八十四、现在看标点

有人会想：

> “标点都是噪声，删掉能省 Token。”

很危险。

---

# 八十五、例如：

```text
A、B不得参加。
```

和：

```text
A不得参加，B可以参加。
```

标点结构：

> 帮助表达关系。

---

# 八十六、再比如：

```text
供应商应满足：
1. 条件A；
2. 条件B；
3. 条件C。
```

如果全部删掉：

```text
供应商应满足条件A条件B条件C
```

层级：

> 变差。

---

# 八十七、所以 Normalization 可以统一

```text
；;
```

这类视觉变体。

但不能：

> 把标点全部删掉。

---

# 八十八、现在看中文引号

可能有：

```text
“政府采购”
```

和：

```text
"政府采购"
```

需要不需要统一？

---

# 八十九、如果只是训练普通语言模型：

> 可以考虑统一。

但如果原始引用格式本身：

> 有法律引用意义，

也可以保留。

---

# 九十、更稳妥的方法依然是：

```text
raw_text
+
normalized_text
```

---

# 九十一、现在看括号

例如：

```text
（含）
```

和：

```text
（不含）
```

括号内容：

> 绝对不能因为觉得“像备注”就删。

---

# 九十二、例如：

```text
500万元以上（不含500万元）
```

如果清理掉括号：

```text
500万元以上
```

业务条件：

> 已经改变。

---

# 九十三、类似：

```text
3年以内（含3年）
```

和：

```text
3年以内（不含3年）
```

不能混。

---

# 九十四、因此括号里的内容可能是

# Semantic Modifier

语义修饰条件。

---

# 九十五、采购文本里建议默认策略：

> **括号内容保留，除非有非常明确证据它只是版式噪声。**

---

# 九十六、现在看编号

例如：

```text
（一）
```

```text
1.
```

```text
1）
```

要不要全部删掉？

---

# 九十七、第三阶段已经告诉我们：

编号：

> 本身包含结构信息。

所以 Master Layer：

> 不应该删。

---

# 九十八、训练 View 是否保留编号？

看任务。

例如：

```text
父Clause:
供应商应满足以下条件：

（一）……
（二）……
```

编号可以帮助模型理解：

> 子项关系。

---

# 九十九、所以通常建议：

> 在结构化 Clause View 中保留。

---

# 一百、但我们还可以单独结构化：

```text
raw_number = "（二）"
```

于是模型输入不一定：

> 必须依赖这个字符。

---

# 一百零一、这就是：

```text
Text
+
Metadata
```

一起服务不同用途。

---

# 一百零二、现在处理重复页眉页脚

第二阶段已经识别：

```text
header
footer
```

第四阶段终于可以真正：

> 从 Normalized Text View 中去除。

---

# 一百零三、注意：

不是删除 Raw Block。

而是：

```text
include_in_clean_view = false
```

或者：

```text
block_role = footer
```

---

# 一百零四、Raw Parsed Layer：

> 仍保留。

---

# 一百零五、比如：

```text
某某政府采购中心
第37页
```

如果确认是重复 Footer，

Normalized Clause：

> 不再包含。

---

# 一百零六、这叫

# Non-destructive Cleaning

非破坏性清洗。

---

# 一百零七、同样适用于网页模板

HTML 中：

```text
首页
登录
网站地图
版权信息
```

可以：

> 从 Content View 排除。

但原始网页抓取：

> 最好仍保留。

---

# 一百零八、现在看重复内容

有些 PDF 解析器会把同一文字抽两次。

例如：

```text
供应商应具有独立承担民事责任的能力。
供应商应具有独立承担民事责任的能力。
```

---

# 一百零九、是不是直接删一条？

不一定。

---

# 一百一十、如果两条来自：

> 同一个页面、同一个 bbox、相同内容，

很可能：

> Parser Duplicate。

---

# 一百一十一、但如果它们来自：

```text
资格条件
```

和：

```text
合同条款
```

只是碰巧内容一样，

这可能：

> 是真实重复。

---

# 一百一十二、两者不能混。

所以：

# Parsing Duplicate

和：

# Document Duplicate

是两个问题。

---

# 一百一十三、解析器产生的假重复

可以在 Cleaning 中处理。

---

# 一百一十四、真实文档里的重复 Clause

应该：

> 保留到第五阶段专门做去重判断。

---

# 一百一十五、这就是为什么第四课把

```text
Cleaning
```

和：

```text
Deduplication
```

拆成两个阶段。

---

# 一百一十六、Cleaning 只负责：

> 明显表现层噪声。

第五阶段才处理：

> 相同/近似业务内容。

---

# 一百一十七、现在看 OCR Noise

例如：

```text
供 应 商□□□应具备
```

其中：

```text
□□□
```

可能是无法识别字符。

---

# 一百一十八、是否直接删除？

危险。

因为这三个字符：

> 可能正好是关键内容。

---

# 一百一十九、例如真正原文可能是：

```text
供应商不得应……
```

虽然这个例子语法怪，但核心思想是：

> 你不知道丢的是什么。

---

# 一百二十、所以 Unknown Character 应该更像：

```text
<UNK_OCR>
```

或者：

> 保留替代符并加 Warning。

---

# 一百二十一、例如：

```json
{
  "normalized_text": "供应商□□□应具备……",
  "warnings": [
    "UNRESOLVED_OCR_GLYPH"
  ]
}
```

---

# 一百二十二、而不是：

```text
供应商应具备……
```

然后假装：

> 中间什么都没有。

---

# 一百二十三、这叫：

# Preserve Uncertainty

保留不确定性。

---

# 一百二十四、因为“缺数据”

和：

> “确定没有数据”

不是一回事。

---

# 一百二十五、这在专业 AI 系统中特别重要。

---

# 一百二十六、现在看错别字

假设招标文件原文真的写：

```text
供应商因提供相关证书。
```

可能作者本来想写：

```text
应提供
```

---

# 一百二十七、我们要不要帮它改？

默认：

> 不应该直接修改 Raw。

---

# 一百二十八、因为数据工程的任务不是：

> 替采购人润色文件。

---

# 一百二十九、可以做：

```text
suspected_typo = true
```

甚至提供：

```text
suggested_text
```

但原文：

> 必须保留。

---

# 一百三十、这和法律证据意识有关

以后用户问：

> “原文件到底写了什么？”

系统必须回答：

> 原文。

不能回答：

> 我们觉得作者应该这么写。

---

# 一百三十一、所以：

\[
\boxed{
SourceTruth
>
LinguisticBeauty
}
\]

---

# 一百三十二、现在看繁体与简体

例如：

```text
採購
```

和：

```text
采购
```

要不要统一？

---

# 一百三十三、对于大量中文检索，

可以考虑构建：

> 规范化搜索 View。

但不要直接：

> 删除原始文本。

---

# 一百三十四、因为某些正式文件来源：

> 字体和原文形式本身也有追溯意义。

---

# 一百三十五、所以可以：

```text
raw_text
```

保留原始。

同时：

```text
search_normalized_text
```

做简繁规范化。

---

# 一百三十六、这就出现一个很重要的概念

# Multiple Views

同一个 Clause：

> 可以有多个派生文本 View。

---

# 一百三十七、例如：

```text
raw_text
```

用于：

> 审计和追溯。

---

# 一百三十八、

```text
normalized_text
```

用于：

> SFT / Evaluation。

---

# 一百三十九、

```text
search_text
```

用于：

> BM25 / 检索。

---

# 一百四十、

```text
display_text
```

用于：

> 用户界面。

---

# 一百四十一、这四个 Text View

不一定：

> 完全一样。

---

# 一百四十二、这是一种非常成熟的数据系统思路

不要逼：

> 一个字符串同时满足所有任务。

---

# 一百四十三、比如 BM25 Search View

可能会做更多：

> 空格和 Unicode 统一。

---

# 一百四十四、而 Gold Evaluation View

可能：

> 更接近原文。

---

# 一百四十五、因此：

\[
\boxed{
OneSource
\rightarrow
MultipleSafeViews
}
\]

---

# 一百四十六、现在看标点统一

例如：

```text
,
```

和：

```text
，
```

是否统一成中文逗号？

可以。

但要先确认：

> 不影响技术表达。

---

# 一百四十七、例如 CSV 或型号：

```text
A,B,C
```

也许逗号就是：

> 数据格式的一部分。

---

# 一百四十八、所以不同 Section Type

甚至可以使用：

> 不同 Normalization Policy。

---

# 一百四十九、例如普通正文

可以更积极：

> 统一全半角标点。

---

# 一百五十、技术参数表

应该：

> 更保守。

---

# 一百五十一、评分表

尤其：

```text
数字
%
±
≤
≥
```

几乎：

> 原样保护。

---

# 一百五十二、这叫

# Context-sensitive Normalization

---

# 一百五十三、不是所有文本：

> 同一套 regex 打到底。

---

# 一百五十四、现在看表格中的空白单元格

例如：

| 一级指标 | 二级指标 | 分值 |
|---|---|---:|
| 技术 | 方案 | 10 |
|  | 人员 | 10 |

空白一级指标：

> 可能继承“技术”。

---

# 一百五十五、如果 Cleaning 阶段看到：

```text
empty
```

就删掉这一行，

那就出大问题。

---

# 一百五十六、空白：

> 不总是垃圾。

有时代表：

# Merged Cell Semantics

---

# 一百五十七、正确做法可能是结构化：

```text
raw_cell = ""
inherited_value = "技术"
```

而不是：

> 偷偷把原表改掉。

---

# 一百五十八、同样，

表格中的：

```text
—
```

可能表示：

- 无；
- 不适用；
- 横线装饰；
- 同上。

不能一刀切。

---

# 一百五十九、所以表格数据 Normalization：

> 要比普通正文更谨慎。

---

# 一百六十、现在讲电话号码、邮箱、联系人

采购文档经常包含：

```text
联系人
手机号
邮箱
地址
```

这些不是“噪声”。

但它们也不一定应该：

> 进入模型训练。

---

# 一百六十一、这属于：

# Privacy / Sensitive Data Filtering

严格说：

> 和 Cleaning 不完全一回事。

---

# 一百六十二、为什么要分开？

如果你把：

```text
138xxxxxx
```

删掉，

应该知道：

> 是出于隐私治理。

不是因为：

> 它解析错了。

---

# 一百六十三、所以建议分别记录：

```text
normalization_log
```

和：

```text
privacy_redaction_log
```

不要混。

---

# 一百六十四、例如：

```json
{
  "operation": "redact_phone",
  "reason": "privacy_policy"
}
```

而不是：

```text
cleaning
```

三个字带过。

---

# 一百六十五、这就是 Data Governance

> 每一次改变数据，都应该知道为什么。

---

# 一百六十六、现在进入非常重要的东西

# Normalization Log

如果 Clean Text 被修改过，

最好记录：

> 改了什么。

---

# 一百六十七、例如 Raw：

```text
供应商注册资本不得低于５００ 万元。
```

Clean：

```text
供应商注册资本不得低于500万元。
```

可以记录：

```json
[
  {
    "rule": "fullwidth_digit_to_ascii",
    "before": "５００",
    "after": "500"
  },
  {
    "rule": "remove_space_between_number_and_unit",
    "before": "500 万元",
    "after": "500万元"
  }
]
```

---

# 一百六十八、是不是每个字符修改都必须人工看？

当然不是。

日志：

> 机器自动产生。

---

# 一百六十九、为什么日志重要？

因为如果半年后发现：

```text
Normalization Rule 17
```

有 Bug，

可以直接查询：

> 哪些 Clause 用过 Rule 17。

---

# 一百七十、然后只重跑受影响数据。

---

# 一百七十一、如果没有日志，

你只能：

> 全库重跑，

甚至：

> 不知道哪些数据被改错。

---

# 一百七十二、所以 Normalization 也需要

# Data Lineage

---

# 一百七十三、第一阶段讲：

```text
Sample
↓
来源
```

第二阶段讲：

```text
Text
↓
Parser
```

第三阶段讲：

```text
Clause
↓
Source Blocks
```

第四阶段进一步：

```text
Normalized Text
↓
Normalization Operations
```

整条 Lineage 越来越完整。

---

# 一百七十四、这就是未来 `ProcurementDataset_V0.1`

真正有工程价值的原因。

不是只有：

> 文本和标签。

---

# 一百七十五、现在讨论 Idempotence

这是一个稍微工程一点的词。

不用怕。

它意思很简单。

如果文本：

```text
T
```

经过 Normalizer：

```text
N(T)
```

再跑一次：

```text
N(N(T))
```

结果最好仍然一样。

---

# 一百七十六、可以写成：

\[
\boxed{
N(N(x))=N(x)
}
\]

---

# 一百七十七、为什么？

如果第一次运行得到：

```text
500 万元
→
500万元
```

第二次又变成：

```text
500万元
→
5000000元
```

第三次：

```text
5000000元
→
5,000,000元
```

Pipeline：

> 每跑一次结果都不同。

非常难维护。

---

# 一百七十八、所以一个好的 Normalizer：

> **重复执行应该稳定。**

---

# 一百七十九、这就是今天极少数值得记住的工程公式之一：

\[
\boxed{
Normalize(Normalize(x))
=
Normalize(x)
}
\]

---

# 一百八十、这叫：

# Idempotent

幂等。

---

# 一百八十一、以后你会发现：

数据 Pipeline 很喜欢幂等。

因为：

> 可以安全重跑。

---

# 一百八十二、现在看 Normalization Version

今天：

```text
normalizer_v0.1
```

以后可能发现：

> 空格规则有问题。

升级：

```text
normalizer_v0.2
```

---

# 一百八十三、每条 CleanClause 最好知道：

```text
normalizer_version
```

---

# 一百八十四、否则：

100 万条数据里：

> 一半 v0.1，一半 v0.3，

没人知道。

---

# 一百八十五、所以版本字段至少包括：

```text
parser_version
structure_version
normalizer_version
schema_version
```

以后还会有：

```text
label_version
dataset_version
```

---

# 一百八十六、这一整套版本控制：

> 最终会在第 11 阶段正式串起来。

---

# 一百八十七、现在看一个完整清洗示例

Raw：

```text
第 37 页
某某市政府采购中心

（二）供应商注册资本不得低于５００ 万元，
且须在本 市连续经营不少于 5 年。

项目编号：ABC-2026-001
```

---

# 一百八十八、结构阶段已经知道：

```text
第37页
某某市政府采购中心
项目编号
```

属于：

> Header / Footer / Metadata。

---

# 一百八十九、于是 Clean Clause 可以变成：

```text
（二）供应商注册资本不得低于500万元，且须在本市连续经营不少于5年。
```

---

# 一百九十、发生了什么？

```text
重复页眉页脚
→ 从Clean View排除

５００
→ 500

500 万元
→ 500万元

本 市
→ 本市

5 年
→ 5年
```

---

# 一百九十一、但是没有做什么？

没有改：

```text
不得低于
```

没有改：

```text
且须
```

没有改：

```text
本市
```

没有把：

```text
不少于5年
```

改成：

```text
5年以上
```

---

# 一百九十二、最后那个特别重要

虽然：

```text
不少于5年
```

和：

```text
5年以上
```

日常理解非常接近。

但我们不应该在 Cleaning 中：

> 主动改写。

---

# 一百九十三、因为：

> Cleaning 的职责不是语言同义改写。

---

# 一百九十四、如果未来需要统一逻辑表达

可以额外结构化：

```text
operator = >=
value = 5
unit = year
```

而不是：

> 改原句。

---

# 一百九十五、再看一个有风险的例子

Raw：

```text
技术参数：CPU 主频≥3.0GHz，核心数不少于32核。
```

错误 Cleaning：

```text
技术参数CPU主频3.0GHz核心数32核
```

---

# 一百九十六、它删掉了：

```text
≥
```

和：

```text
不少于
```

于是：

> 约束关系丢失。

---

# 一百九十七、模型现在不知道：

```text
3.0
```

是：

- 等于；
- 至少；
- 不超过；
- 推荐值。

---

# 一百九十八、所以这种“清洗”

不是 Cleaning。

是：

# Information Destruction

---

# 一百九十九、再看评分案例

Raw：

```text
近三年每提供1个同类项目业绩得2分，最高得10分。
```

错误 Normalization：

```text
同类项目业绩2分10分
```

---

# 二百、这对关键词搜索：

> 也许还能凑合。

但对 LLM：

> 业务关系几乎被摧毁。

---

# 二百零一、所以我们从今天开始要坚定一个原则：

# LLM 需要完整语言关系

不是：

> 极限压缩的关键词。

---

# 二百零二、现在看数字中的千位分隔符

```text
5,000,000元
```

和：

```text
5000000元
```

是否统一？

可以考虑。

---

# 二百零三、但要先判断逗号是不是：

> 数字分隔符。

---

# 二百零四、例如：

```text
型号A,B,C
```

这里：

> 不是数字逗号。

---

# 二百零五、所以规则应该：

> 有 Pattern Context。

而不是：

```python
replace(",", "")
```

---

# 二百零六、再看小数点

```text
3.0GHz
```

绝对不能清成：

```text
30GHz
```

---

# 二百零七、扫描文档里：

```text
3．0
```

可能使用全角句点。

这个可以：

> 规范成 `3.0`。

但必须确认：

> 它位于数字之间。

---

# 二百零八、这叫局部规则

例如：

```text
数字 + 全角小数点 + 数字
→
数字 + "." + 数字
```

比：

> 全局把所有 `．` 变成 `.`

更安全。

---

# 二百零九、现在看百分号

```text
10％
```

可以规范：

```text
10%
```

---

# 二百一十、但：

```text
0.1
```

不能自动转成：

```text
10%
```

除非：

> 业务 Schema 明确知道这是比例字段。

---

# 二百一十一、为什么？

因为 `0.1`：

> 可能就是数值 0.1。

不是一定：

> 百分之十。

---

# 二百一十二、所以清洗器不能：

> 自作聪明。

---

# 二百一十三、现在看金额中文数字

```text
人民币伍佰万元整
```

要不要直接改成：

```text
500万元
```

不建议覆盖。

---

# 二百一十四、可以做结构化解析：

```text
amount_cny = 5000000
```

但：

```text
raw_text
```

继续保存：

```text
人民币伍佰万元整
```

---

# 二百一十五、这对于合同和金额审查特别重要。

---

# 二百一十六、现在看文件中的特殊空字符

例如：

```text
\u00A0
```

Non-breaking space。

人眼：

> 看起来就是空格。

---

# 二百一十七、还有：

```text
zero-width space
```

人眼：

> 完全看不见。

---

# 二百一十八、这些可能严重影响

```text
字符串比较
Hash
去重
关键词搜索
```

---

# 二百一十九、所以这类 Unicode 控制字符：

> 通常可以安全规范化。

---

# 二百二十、例如零宽空格

如果确认不承载语义：

> 可以删除。

---

# 二百二十一、这类操作属于典型

# Safe Normalization

---

# 二百二十二、和下面这些形成鲜明对比：

```text
删除“不得”
删除“以上”
删除“含”
修改数字
修改单位
修改比较符
```

这些属于：

# High-risk Normalization

---

# 二百二十三、于是我们可以第一次建立

# Normalization Risk Levels

概念上分三类。

---

# 二百二十四、Low Risk

例如：

```text
零宽空格
全角英文字母→半角
连续无意义空白
明确重复页脚
```

通常：

> 可自动处理。

---

# 二百二十五、Medium Risk

例如：

```text
OCR断行合并
中文字符间异常空格
表格单元格换行
```

需要：

> 上下文规则和质量检测。

---

# 二百二十六、High Risk

例如：

```text
数字修改
单位修复
否定词修复
比较符修复
法律条号修复
型号修复
```

最好：

> 不自动静默修改。

---

# 二百二十七、这张分类不是法律标准。

只是：

> 我们工程上的风险思维。

---

# 二百二十八、这种设计可以让 Pipeline 做：

```text
Low Risk
→ 自动

Medium Risk
→ 自动 + Warning

High Risk
→ 建议值 + 人工核验
```

---

# 二百二十九、这和最终 ProcurementAI 的架构：

```text
Rule
+
Model
+
Human
```

再次一致。

---

# 二百三十、现在看一条 OCR 文本

```text
供应商注册资本不得低于5OO万元。
```

我们可以怎么处理？

---

# 二百三十一、错误做法：

```text
直接改500
```

不记录。

---

# 二百三十二、更好的方式：

```json
{
  "raw_text": "供应商注册资本不得低于5OO万元。",
  "normalized_text": "供应商注册资本不得低于5OO万元。",
  "correction_candidate": "供应商注册资本不得低于500万元。",
  "warnings": [
    "AMBIGUOUS_OCR_NUMERIC_TOKEN"
  ]
}
```

---

# 二百三十三、如果后续人工确认：

```text
500万元
```

再产生：

```text
verified_text
```

---

# 二百三十四、这样系统明确区分：

```text
机器猜测
```

和：

```text
专家确认
```

---

# 二百三十五、这个区别对 Gold Dataset 极其重要。

---

# 二百三十六、现在讨论法律名称

例如：

```text
《中华人民共和国政府采购法》
```

不要清洗成：

```text
中华人民共和国政府采购法
```

虽然一般搜索仍能找到。

---

# 二百三十七、为什么最好保留书名号？

因为它帮助模型识别：

> 这是正式规范名称。

---

# 二百三十八、同样：

```text
第三十一条
```

不要随便：

> 删除“第”和“条”。

---

# 二百三十九、因为：

```text
31
```

本身语义弱很多。

---

# 二百四十、如果做 RAG 索引，可以额外派生：

```text
article_number = 31
```

但原文：

> 保留。

---

# 二百四十一、这是我们反复强调的：

# Add Structure, Don't Destroy Meaning

---

# 二百四十二、现在讲 Markdown 化

为了喂 LLM，

有些系统会把表格转成：

```markdown
| 评分项 | 分值 | 规则 |
|---|---:|---|
| 本地服务 | 5 | 本市有机构得5分 |
```

这是可以的。

---

# 二百四十三、但这个 Markdown 应该是：

# View

不是：

> 唯一 Master Data。

---

# 二百四十四、Master 仍然应该保留：

```text
rows
columns
cells
headers
```

---

# 二百四十五、这样以后模型格式变化，

可以重新生成：

```text
Markdown
JSON
Plain Text
```

而不用：

> 重新解析 PDF。

---

# 二百四十六、这就是第四课一直在建立的核心数据哲学：

\[
\boxed{
RichMasterData
\rightarrow
TaskSpecificViews
}
\]

---

# 二百四十七、现在第一次设计 `CleanClause_V0.1`

它可以概念上长这样：

```json
{
  "clause_id": "CLAUSE-00178",
  "document_id": "DOC-00152-01",

  "section_path": [
    "第三章 采购需求",
    "3.2 售后服务"
  ],

  "raw_text": "供应商应保证故障发生后 2 小时内到达项目现场。",
  "normalized_text": "供应商应保证故障发生后2小时内到达项目现场。",

  "source_block_ids": [
    "B00872"
  ],

  "normalizer_version": "normalizer_v0.1",

  "normalization_ops": [
    "remove_unnecessary_space_between_number_and_unit"
  ],

  "warnings": [],

  "normalization_status": "auto_verified"
}
```

---

# 二百四十八、这里已经有几个重要字段

```text
raw_text
normalized_text
normalizer_version
normalization_ops
warnings
```

---

# 二百四十九、如果 OCR 有不确定内容

可能：

```text
normalization_status =
needs_review
```

---

# 二百五十、如果专家已经确认：

```text
human_verified
```

---

# 二百五十一、所以 Cleaning 同样可以有质量状态。

---

# 二百五十二、现在把第 1～4 阶段的数据对象串起来

```text
Stage 1
TaskSchema_V0.1

Stage 2
ParsedDocument_V0.1

Stage 3
ClauseUnit_V0.1

Stage 4
CleanClause_V0.1
```

---

# 二百五十三、它们不是四份互不相关的数据。

而是一条 Lineage：

```text
Raw File
   ↓
ParsedDocument
   ↓
ClauseUnit
   ↓
CleanClause
   ↓
Annotated Sample
```

---

# 二百五十四、未来如果某个 Gold Sample 出问题，

我们可以：

```text
Gold Sample
↓
CleanClause
↓
ClauseUnit
↓
Source Blocks
↓
Page
↓
Original File
```

一路追到底。

---

# 二百五十五、这才是真正专业的数据资产。

---

# 二百五十六、现在看一个反例：过度清洗

原文：

```text
供应商近3年（2023年1月1日至投标截止日）至少具有5个类似项目业绩。
```

某清洗器想“简化文本”：

```text
供应商近3年至少具有5个类似项目业绩。
```

---

# 二百五十七、看起来更干净。

实际上删掉了：

```text
2023年1月1日至投标截止日
```

这可能：

> 正是争议核心。

---

# 二百五十八、所以：

# Redundancy to human ≠ Redundancy to model

你觉得某句话“啰嗦”。

它可能：

> 对业务判断非常关键。

---

# 二百五十九、再一个例子

Raw：

```text
供应商须具有ISO 9001认证（认证范围须包含信息系统运维服务）。
```

过度清洗：

```text
供应商须具有ISO 9001认证。
```

---

# 二百六十、括号里的：

```text
认证范围
```

被删除。

但它：

> 可能正是限制性的核心。

---

# 二百六十一、所以不要用：

> “看起来像补充说明”

作为删除依据。

---

# 二百六十二、再看一个评分规则

```text
具有本地服务机构得5分；承诺中标后设立服务机构得3分；其他不得分。
```

如果只保留：

```text
本地服务机构得5分
```

你就丢掉了：

> 其它竞争方式。

---

# 二百六十三、于是模型风险判断：

> 可能变得过于激进。

---

# 二百六十四、这就是为什么 Clean Data 也必须：

> 保持完整关系。

---

# 二百六十五、现在讲 Normalization Testing

Normalizer 也应该有测试集。

比如准备几十个案例：

```text
全角数字
OCR空格
比较符
中文/英文标点
金额
日期
型号
法律条号
否定词
表格
```

---

# 二百六十六、每条测试记录：

```text
Input
Expected Output
Must Preserve Tokens
```

---

# 二百六十七、例如：

```text
Input:
注册资本不得低于５００ 万元。

Expected:
注册资本不得低于500万元。

Must Preserve:
不得低于
500
万元
```

---

# 二百六十八、再例如：

```text
Input:
响应时间≤2小时。

Expected:
响应时间≤2小时。

Must Preserve:
≤
2
小时
```

---

# 二百六十九、再例如：

```text
Input:
本项目不接受联合体投标。

Expected:
本项目不接受联合体投标。

Must Preserve:
不接受
```

---

# 二百七十、这样每次改 Normalizer：

> 跑一遍回归测试。

---

# 二百七十一、否则你修复：

> 空格规则

可能意外破坏：

> 技术型号。

---

# 二百七十二、这叫：

# Regression Test

第一课我们在模型里讲过。

现在：

> 数据 Pipeline 也需要。

---

# 二百七十三、所以整个项目里：

# 几乎所有重要模块都应该被评测

不仅：

> LLM。

还包括：

```text
Parser
Structure Recovery
Normalizer
Deduplicator
Label Pipeline
RAG
```

---

# 二百七十四、这是成熟 AI 工程和 Demo 最大的区别之一。

---

# 二百七十五、现在做一个安全清洗决策树

```text
发现异常文本
   │
   ▼
是否明确属于表现层噪声？
   │
   ├── 是
   │    ↓
   │  可以自动规范
   │
   └── 否
        │
        ▼
是否可能改变业务含义？
        │
        ├── 否
        │    ↓
        │  规则规范 + 日志
        │
        └── 是
             │
             ▼
       不静默修改
             │
      ┌──────┴──────┐
      ▼             ▼
   Warning      Human Review
```

---

# 二百七十六、如果只能记一张操作图，

就记这张。

---

# 二百七十七、现在给数据字段分风险

可以建立类似：

```text
Protected Tokens
```

保护字段。

---

# 二百七十八、第一类：

# Negation

```text
不
不得
禁止
无需
未
无
```

---

# 二百七十九、第二类：

# Comparison

```text
大于
小于
以上
以下
不少于
不高于
≤
≥
```

---

# 二百八十、第三类：

# Quantity

```text
金额
人数
数量
分值
比例
时间
期限
距离
容量
性能参数
```

---

# 二百八十一、第四类：

# Identity

```text
项目编号
法规名称
条号
型号
证书名称
机构名称
```

---

# 二百八十二、第五类：

# Scope Modifier

```text
仅
全部
任一
同时
至少
最多
其中
除外
含
不含
```

---

# 二百八十三、这些词看起来很小。

但经常：

> 决定整个 Clause 的约束范围。

---

# 二百八十四、例如：

```text
至少一个
```

和：

```text
全部
```

完全不是同一个条件。

---

# 二百八十五、所以 Normalizer 最好有：

# Protected Pattern Tests

---

# 二百八十六、例如如果清洗前后：

```text
不得
```

消失了，

自动触发：

```text
NEGATION_CHANGED
```

---

# 二百八十七、如果数字数量发生变化：

```text
500
→
5000
```

触发：

```text
NUMERIC_TOKEN_CHANGED
```

---

# 二百八十八、如果：

```text
≤
→
<
```

触发：

```text
COMPARATOR_CHANGED
```

---

# 二百八十九、这叫：

# Semantic Guardrail

语义护栏。

---

# 二百九十、甚至可以做一个简单 Diff

```text
Raw
vs
Normalized
```

自动检查：

> 哪些字符变了。

---

# 二百九十一、如果变化只发生在：

```text
全角数字
多余空格
零宽字符
```

风险较低。

---

# 二百九十二、如果变化触及：

```text
数字
比较符
否定词
单位
```

风险升高。

---

# 二百九十三、这样 Cleaning 就不再是一堆黑盒 `.replace()`。

而变成：

> 可审计的 Transformation Pipeline。

---

# 二百九十四、现在谈 Schema Validation

CleanClause 还可以做结构验证。

例如：

```text
normalized_text不能为空
```

---

# 二百九十五、

```text
raw_text必须存在
```

---

# 二百九十六、

```text
clause_id必须存在
```

---

# 二百九十七、

```text
normalizer_version必须存在
```

---

# 二百九十八、如果发生文本修改：

```text
normalization_ops
```

不能为空。

---

# 二百九十九、如果存在高风险 Warning：

```text
normalization_status
```

不能自动标：

```text
verified
```

---

# 三百、这就开始形成：

# Data Contract

数据契约。

---

# 三百零一、第一阶段我们说 Schema 是合同。

现在终于看到：

> 合同可以被程序验证。

---

# 三百零二、例如：

```python
assert raw_text != ""
assert normalized_text != ""
assert clause_id is not None
```

真实工程会更复杂。

但思想就是：

> 不让坏数据悄悄流下去。

---

# 三百零三、这叫：

# Fail Loudly

发现异常：

> 明确报出来。

不要：

# Fail Silently

悄悄产生坏数据。

---

# 三百零四、例如 OCR 异常：

```text
供应商□□□5OO万元
```

系统不应该：

> 默默当成正常 Clause。

---

# 三百零五、应该带：

```text
warnings
```

让下游知道：

> 这条数据不完全可信。

---

# 三百零六、以后第 12 阶段组装 Dataset 时，

可以直接过滤：

```text
normalization_status != verified
```

的样本。

---

# 三百零七、Gold Set 更可以要求：

```text
parse_verified
+
structure_verified
+
normalization_verified
+
expert_label_verified
```

---

# 三百零八、这就是 Gold 的真正含义：

> 不只是 Label 专家看过。

而是：

> 整条数据链都可信。

---

# 三百零九、现在说一个特别常见的错误：

# 用 LLM 自动“清理”全部数据

例如：

> “请把下面采购条款改写成规范、通顺、简洁的中文。”

---

# 三百一十、LLM 很可能输出：

> 更漂亮。

但它可能：

- 删细节；
- 合并条件；
- 改数字；
- 改语气；
- 补推论。

---

# 三百一十一、这对于：

# Data Cleaning

是非常危险的。

---

# 三百一十二、LLM 可以做什么？

它可以：

> 帮助发现可疑文本。

例如：

```text
这段是不是OCR错误？
```

或者：

```text
这里是不是疑似乱码？
```

---

# 三百一十三、但对于高风险字段：

> 最好让它提出 Candidate，

而不是：

> 直接覆盖 Source Truth。

---

# 三百一十四、可以记住：

```text
LLM as Inspector
>
LLM as Silent Rewriter
```

对于高价值数据尤其如此。

---

# 三百一十五、现在看 Cleaning 的成本问题

是不是所有 100 万条 Clause：

> 都要专家逐条校对？

不现实。

---

# 三百一十六、合理方式是：

```text
低风险规则
→ 全自动

中风险
→ 抽样QA

高风险
→ 人工复核

Gold Set
→ 高强度复核
```

---

# 三百一十七、这叫：

# Tiered Quality Control

分层质量控制。

---

# 三百一十八、它和我们的数据质量阶梯非常一致。

---

# 三百一十九、例如：

```text
CPT Corpus
```

可以容忍：

> 少量格式噪声。

---

# 三百二十、

```text
SFT Training
```

要求：

> 明显更高。

---

# 三百二十一、

```text
Gold Benchmark
```

要求：

> 极高。

---

# 三百二十二、所以不存在一个万能：

```text
clean = true
```

---

# 三百二十三、Data Quality 必须：

> 根据用途定义。

---

# 三百二十四、现在给第四阶段建立完整 Pipeline

```text
ClauseUnit_V0.1
       │
       ▼
 Preserve Raw Text
       │
       ▼
 Unicode Normalization
       │
       ▼
 Safe Whitespace Cleanup
       │
       ▼
 Line-break Repair
       │
       ▼
 Header/Footer Exclusion
       │
       ▼
 OCR Noise Detection
       │
       ▼
 Critical Token Guardrails
       │
       ▼
 Numeric / Unit Validation
       │
       ▼
 Normalization Diff
       │
       ▼
 Quality Warnings
       │
       ▼
 CleanClause_V0.1
```

---

# 三百二十五、注意这里没有一步叫：

```text
Rewrite to Beautiful Chinese
```

这不是我们的目标。

---

# 三百二十六、本阶段最容易犯的 12 个错误

第一类错误是：

> **直接覆盖 Raw Text。**

一旦错了，无法回滚。

第二类错误是：

> **删除所有空格。**

会破坏英文、型号和结构。

第三类错误是：

> **删除所有换行。**

会破坏 Section / List / Clause 关系。

第四类错误是：

> **删除所有标点。**

技术符号和逻辑结构会丢。

第五类错误是：

> **做传统停用词删除。**

尤其可能删掉否定词。

第六类错误是：

> **OCR 猜到什么就自动改什么。**

会制造假数据。

第七类错误是：

> **修改数字却不记录。**

极其危险。

第八类错误是：

> **单位和数字分开保存后把单位丢掉。**

业务意义会改变。

第九类错误是：

> **删除括号内容。**

括号经常包含关键限定。

第十类错误是：

> **把真实重复当成解析重复删掉。**

这应该留到去重阶段。

第十一类错误是：

> **用 LLM 批量润色原始条款。**

会产生隐性语义漂移。

第十二类错误是：

> **Normalizer 没版本、没日志、没测试。**

半年后几乎无法追责。

---

# 三百二十七、本阶段最重要的 5 个“≠”

```text
Cleaning
≠
Rewriting
```

```text
Normalized Text
≠
Source Truth
```

```text
Whitespace
≠
Always Noise
```

```text
Punctuation
≠
Always Decoration
```

```text
Cleaner-looking
≠
More Correct
```

最后这一条尤其重要。

---

# 三百二十八、再记一个最重要的“=”

\[
\boxed{
SafeNormalization
=
SemanticPreservation
+
Traceability
+
Reversibility
+
Consistency
}
\]

翻译成人话：

> **好的清洗不是把文本变漂亮，而是在尽量保持原始语义的前提下，让表示方式更稳定，同时保证每次修改都能追踪、能回滚、能重复得到同样结果。**

---

# 三百二十九、现在把第四课前四阶段连起来

```text
第四课 · 第1阶段
Task Schema
│
│  定义：一条业务样本是什么
▼

第四课 · 第2阶段
ParsedDocument
│
│  恢复：文件里到底写了什么
▼

第四课 · 第3阶段
ClauseUnit
│
│  恢复：这些文字属于哪里
▼

第四课 · 第4阶段
CleanClause
│
│  规范：怎样安全统一文本表现
▼
```

我们离真正的数据集：

> 已经越来越近。

---

# 三百三十、但现在会出现一个新问题

假设我们收集了：

```text
10万条 CleanClause
```

看起来都很干净。

但里面可能有：

```text
同一个项目重复下载3次

同一公告HTML和PDF各来一份

同一条法规被复制到50个文档

不同项目使用同一个模板

同一个条款只是换了项目名称
```

---

# 三百三十一、也就是说：

> **文本干净，不代表数据独立。**

---

# 三百三十二、如果这些重复数据直接进入训练

某类模板可能：

> 被重复几十倍。

模型会误以为：

> 这是整个行业最重要的规律。

---

# 三百三十三、更危险的是

如果同一条重复内容：

```text
一份进入Train
一份进入Test
```

你会得到：

> 非常漂亮但完全虚假的 Benchmark。

---

# 三百三十四、所以第四阶段之后，

下一个大问题就是：

# Deduplication

---

# 三百三十五、本阶段掌握测试

如果现在不看前文，你能自己回答下面这些问题，本阶段就真正掌握了：

> 为什么 Cleaning 不等于 Rewrite？

> 为什么必须同时保留 `raw_text` 和 `normalized_text`？

> 为什么 Normalized Text 只能是派生版本？

> 为什么不能简单删除所有空格？

> 为什么 Visual Line Break 和 Semantic Break 必须区分？

> 为什么全角数字转半角通常属于低风险 Normalization？

> 为什么 `<`、`≤`、`>`、`≥` 绝对不能随便互换？

> 为什么金额、分值、比例、年限、响应时间属于高风险信息？

> 为什么 OCR 中的 `O` 和 `0` 不能总是自动纠正？

> 为什么单位不能被丢弃？

> 为什么“2026年9月”不能自动变成“2026-09-01”？

> 为什么 `9月15日前` 不能只保存一个日期值？

> 为什么否定词绝对不能作为普通停用词删除？

> 为什么现代 LLM 数据通常不需要传统 Stopword Removal？

> 为什么括号内容不能默认认为是噪声？

> 为什么编号最好保留？

> 为什么页眉页脚可以从 Clean View 去除，却仍应保留在 Raw Parsed Layer？

> Parsing Duplicate 和真实文档重复有什么区别？

> 为什么真正的业务去重要留到下一阶段？

> 为什么无法识别的 OCR 字符不能直接静默删除？

> 为什么原文件中的疑似错别字不能随便替作者改正？

> 为什么同一个 Clause 可以有 Raw、Normalized、Search、Display 多个 View？

> 为什么金额、日期等更适合“增加结构字段”，而不是改写原文？

> 什么是 Normalization Log？

> 为什么需要 `normalizer_version`？

> 什么叫 Idempotence？

> 为什么希望满足：

\[
N(N(x))=N(x)
\]

> 为什么 Normalizer 也需要 Regression Test？

> 什么是 Semantic Guardrail？

> 为什么数字、单位、否定词、比较符变化应该触发 Warning？

> 为什么 Gold Dataset 对清洗质量的要求应该高于普通 CPT Corpus？

> 为什么不建议让 LLM 批量“润色”采购原文后直接作为训练真相？

如果这些问题你可以自己完整解释：

\[
\boxed{
第四课第4阶段真正掌握
}
\]

---

# 三百三十六、本阶段最终只记一句话

> **政府采购数据清洗的目标不是把文本变得漂亮，而是在不改变原始业务含义的前提下，安全地统一字符、空格、换行和版式噪声；所有高风险修改都必须可追踪、可回滚，并且原始文本永远保留。**

最后压成一张图：

```text
                    ClauseUnit_V0.1
                           │
                           ▼
                    Preserve Raw Text
                           │
                           ▼
              ┌────────────────────────┐
              │ Safe Normalization     │
              │                        │
              │ Unicode                │
              │ Whitespace             │
              │ Line Break             │
              │ Header / Footer        │
              │ OCR Noise              │
              └────────────┬───────────┘
                           │
                           ▼
                 Semantic Guardrails
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           数字/单位      否定词       比较符
              │            │            │
              └────────────┼────────────┘
                           ▼
                  Normalization Diff
                           │
                           ▼
                   Warning / Review
                           │
                           ▼
                   CleanClause_V0.1
                           │
               ┌───────────┼───────────┐
               ▼           ▼           ▼
             SFT          RAG        Evaluation
```

---

# 下一阶段：第四课 · 第 5 阶段
## 去重与近似去重——为什么 100 万条“干净数据”可能实际上只有 30 万条独立信息？为什么重复数据不仅浪费训练，还会制造虚假的 Benchmark？

第五阶段我们会第一次真正解决：

```text
Exact Duplicate
```

与：

```text
Near Duplicate
```

以及一个政府采购数据中特别麻烦的问题：

```text
不同项目
+
同一份模板
+
只替换项目名称、金额和日期
```

它们到底算不算重复？

我们会建立这张脑图：

```text
Duplicate
│
├── File-level Duplicate
│
├── Document-level Duplicate
│
├── Clause-level Duplicate
│
├── Template Duplicate
│
└── Semantic Near Duplicate
```

并第一次真正解释：

> 为什么单纯用 SHA-256 只能解决最容易的一层。

以及为什么：

```text
Train/Test Leakage
```

很多时候不是发生在完全相同的文本上，

而是发生在：

> **模板级近重复。**

最终第五阶段会得到第一版：

# `DedupedClauseSet_V0.1`

也就是把第四课的数据第一次从“干净”推进到：

> **尽量独立、尽量不重复。**

---
