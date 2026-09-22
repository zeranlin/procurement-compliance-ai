# 第四课 · 第 7 阶段：数据泄漏与 Benchmark 污染
## 为什么 Train 和 Test 明明已经按 Project 完全分开，模型仍然可能“提前看过答案”？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：HEAVY。** 审计原因：详细展开点过多，主干容易被细节淹没；英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **泄漏的本质，是测试问题相关的信息通过某条不被允许的路径参与了模型开发。**
2. **Split不重叠 ≠ 没有泄漏**
3. **Leakage 的本质不是“文件重复”， 而是答案相关信息越过了不该越过的边界**
4. **泄漏既可能发生在数据里， 也可能发生在Prompt、RAG、规则和人脑里**
5. **时间方向非常重要： 未来信息不能帮助模型回答过去时点的测试问题**
6. **Test被反复用于改系统， 就会逐渐变成Validation**
7. **防泄漏不能只靠“大家小心一点”， 必须建立Benchmark Firewall**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |
| `Input` | 输入：模型在当前任务中允许看到的条件信息 |
| `Split` | 数据切分：按项目/时间/地区划分训练、验证、测试数据 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Sample` | 样本：具有明确输入、目标和来源的一条训练/评测记录 |
| `ANN` | ANN/近似最近邻：在大规模向量中快速寻找相似项 |
| `Dataset` | 数据集：按统一 Schema、版本和质量标准组织的样本集合 |
| `Threshold` | 阈值：把连续分数转成业务动作的决策门槛 |

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

第 6 阶段结束以后，我们已经做了一件非常专业的事情：

没有再用：

```text
Clause Row
```

作为唯一切分单位。

而是开始建立：

```text
Project
+
Duplicate Group
+
Lineage
+
必要的 Template Relation
```

最终得到：

# `DatasetSplit_V0.1`

也就是说，我们已经尽量确保：

```text
同一项目
不会一半Train、一半Test

完全重复样本
不会一边Train、一边Test

由同一母样本派生的数据
不会跨Split乱跑
```

看起来似乎已经安全了。

但现在我要给你一个有点残酷的结论：

> **Train/Test 完全没有相同 `project_id`，仍然不能证明 Benchmark 没有泄漏。**

例如 Test 中有这样一条采购条款：

> “供应商须在本市设有固定服务机构。”

项目本身：

> 从没进入 Train。

但是团队以前已经把这条 Test Case 的专家分析写进：

```text
内部培训材料
专家案例Excel
Prompt示例
规则库
RAG知识库
错误分析报告
Synthetic Data生成源
```

甚至开发人员已经看过它几十遍。

那么模型虽然没有：

> 直接训练那一行 Test 数据，

整个系统却可能已经：

> **提前知道答案。**

这就是今天要解决的东西：

# Data Leakage

以及更加隐蔽的：

# Benchmark Contamination

---

# 一、本阶段真正要解决的一个核心问题

今天只解决：

> **怎样判断一份 Test Set 是否真的处于“模型开发流程之外”，并建立一套机制，防止测试答案通过标签、时间、派生数据、RAG、Prompt、规则、人类调参等路径重新流回训练和开发系统？**

最终我们要得到：

# `LeakageAudit_V0.1`

整个过程可以先压成：

```text
DatasetSplit_V0.1
        ↓
Identify Leakage Paths
        ↓
Trace Data Lineage
        ↓
Check Train / Val / Test Boundaries
        ↓
Check RAG / Prompt / Rules / Synthetic Data
        ↓
Check Time Direction
        ↓
Check Human Feedback Loop
        ↓
Benchmark Firewall
        ↓
LeakageAudit_V0.1
```

---

# 二、本阶段先建立 6 个核心心智模型

先把这六句话钉住：

```text
① Split不重叠
   ≠
   没有泄漏

② Leakage 的本质不是“文件重复”，
   而是答案相关信息越过了不该越过的边界

③ 泄漏既可能发生在数据里，
   也可能发生在Prompt、RAG、规则和人脑里

④ 时间方向非常重要：
   未来信息不能帮助模型回答过去时点的测试问题

⑤ Test被反复用于改系统，
   就会逐渐变成Validation

⑥ 防泄漏不能只靠“大家小心一点”，
   必须建立Benchmark Firewall
```

如果今天只能记住一句：

> **泄漏的本质，是测试问题相关的信息通过某条不被允许的路径参与了模型开发。**

---

# 三、先回答：什么才叫“泄漏”？

很多人想到 Data Leakage，会立刻想到：

```text
Train里有Test原文
```

这当然是最明显的一种。

但定义应该更宽。

我们可以先这样理解：

\[
\boxed{
Leakage
=
不应该在开发阶段可用的信息
进入了模型开发路径
}
\]

这里关键有三个词：

```text
不应该
信息
开发路径
```

---

# 四、“信息”不一定是原始文本

它可以是：

```text
Test原文
Test标签
专家解释
最终裁决
更正结果
投诉处理结果
中标结果
Test案例摘要
Test案例改写
Test答案提炼出的规则
```

甚至可以只是：

> 一个开发人员看完 Test 错误后总结出来的经验。

---

# 五、“开发路径”也不只是 SFT

可能包括：

```text
CPT
SFT
Few-shot Prompt
System Prompt
Rule Engine
RAG Index
Synthetic Data
Threshold Tuning
Model Selection
Error Analysis
Human Workflow
```

所以如果只检查：

```text
train.jsonl
```

远远不够。

---

# 六、今天第一张总图

```text
                     TEST CASE
                         │
       ┌─────────────────┼──────────────────┐
       ▼                 ▼                  ▼
     原文               标签              专家解释
       │                 │                  │
       └────────────┬────┴────────────┬─────┘
                    │                 │
                    ▼                 ▼
                 数据集             文档/报告
                    │                 │
          ┌─────────┼────────┐        │
          ▼         ▼        ▼        ▼
         SFT       CPT    Synthetic   RAG
          │         │        │        │
          └─────────┼────────┼────────┘
                    ▼
                  MODEL
                    │
                    ▼
                  TEST
```

只要 Test Case 的答案相关信息：

> 绕了一圈又回到模型，

就可能污染 Benchmark。

---

# 七、第一类泄漏：Label Leakage

这是最直接的一类。

假设我们的任务是：

> 输入采购条款，判断有没有潜在风险。

理想输入：

```text
供应商须在本市注册满5年。
```

Label：

```text
potential_risk
```

---

# 八、结果数据工程师生成训练输入时变成：

```text
风险条款：
供应商须在本市注册满5年。
```

模型还需要判断吗？

几乎不需要。

---

# 九、因为：

```text
风险条款
```

已经告诉它：

> 答案。

这就是：

# Label Leakage

---

# 十、现实中 Label Leakage 往往没有这么傻

它可能藏得很深。

例如 Excel：

| 条款 | 专家意见 | 风险类别 |
|---|---|---|
| 供应商须…… | 建议删除地域限制 | 资格风险 |

后来构造模型 Input 时：

```text
条款：
供应商须……

专家意见：
建议删除地域限制
```

Output：

```text
是否有风险？
```

---

# 十一、这不是让模型判断风险。

这是让模型：

> 从专家意见里抄答案。

---

# 十二、再例如文件夹结构

数据来自：

```text
/risky_cases/
```

和：

```text
/normal_cases/
```

如果你把文件路径也作为 Feature：

模型可能根本不看正文。

---

# 十三、甚至文件名

```text
违规案例_001.pdf
```

如果 OCR Pipeline 把：

```text
违规案例
```

写进输入 Metadata，

答案又泄漏了。

---

# 十四、所以第一个检查问题

不是：

> “Label 列有没有放进 Input？”

而是：

> **Input 里有没有任何由 Label、裁决或专家结论派生出来的信息？**

---

# 十五、这叫 Target Proxy

目标代理变量。

它没有直接写：

```text
risk=true
```

但实际上高度暗示答案。

---

# 十六、例如：

```text
review_status = 已责令整改
```

模型看到这个字段，

再判断：

> “有没有风险？”

几乎已经知道答案。

---

# 十七、再比如：

```text
complaint_result = 投诉成立
```

如果你的任务是在投诉发生之前判断采购条款风险，

这个字段：

> 来自未来。

同时属于：

# Label Leakage

和：

# Temporal Leakage

---

# 十八、这就是泄漏的一个特点

一条信息：

> 可能同时属于多个泄漏类型。

---

# 十九、第二类：Project Leakage

第六阶段已经重点讲过。

例如：

```text
Project A
├── Clause 1 → Train
├── Clause 2 → Train
└── Clause 3 → Test
```

---

# 二十、Clause 3 虽然没有进入 Train，

但模型已经知道：

```text
项目背景
采购类型
模板
同章上下文
大量相关条件
```

这叫：

# Project Leakage

---

# 二十一、这类泄漏通常通过：

```text
project_id
```

做 Group Split 可以明显降低。

但注意：

> “不同 project_id”仍然不代表完全独立。

因为还可能有：

> Template Leakage。

---

# 二十二、第三类：Duplicate Leakage

例如：

Train：

> “投标人须在本市设立固定服务机构。”

Test：

> “投标人须在本市设立固定的服务机构。”

只多了一个：

```text
的
```

---

# 二十三、Exact Hash：

> 不一样。

但模型实际上：

> 几乎看过原题。

---

# 二十四、这就是：

# Near Duplicate Leakage

第五阶段已经建立：

```text
duplicate_group_id
```

和相似度审计。

今天真正要记：

> **泄漏不要求字符完全一样。**

---

# 二十五、甚至可以改写成：

Train：

> “供应商必须在本地设置售后机构。”

Test：

> “投标人应在项目所在地建立固定服务网点。”

字符串完全不同。

业务结构：

> 极其接近。

---

# 二十六、这时：

# Embedding / Semantic Similarity

就可以成为泄漏审计工具之一。

但仍然要结合：

```text
数字
否定词
单位
上下文
```

判断是不是：

> 真正等价。

---

# 二十七、第四类：Template Leakage

政府采购数据里非常重要。

假设某代理机构有模板：

```text
供应商须：
1. ……
2. ……
3. ……
```

Project A、B、C、D：

> 都使用它。

---

# 二十八、Train 有：

```text
A
B
C
```

Test 有：

```text
D
```

虽然项目完全不同，

模型可能已经：

> 把模板套路学得滚瓜烂熟。

---

# 二十九、这不一定代表 Benchmark 完全无效。

关键看：

> 你想测什么。

---

# 三十、如果生产环境本来就会继续出现同模板项目，

Seen-template Test：

> 是合理的。

---

# 三十一、但如果你声称：

> “模型对新采购文件结构具有强泛化能力。”

那最好还要有：

# Unseen-template Test

---

# 三十二、所以 Template Leakage 更准确地说：

> 有时不是“绝对非法泄漏”，而是“需要被明确控制和报告的泛化重叠”。

---

# 三十三、这就是为什么上一阶段我们把：

```text
Project / Exact Duplicate
```

更多视为：

# Hard Constraint

而：

```text
Template
Agency
Region
```

更多可以作为：

# Generalization Slice

---

# 三十四、第五类：Temporal Leakage

这是专业项目最容易忽视的一种。

先看一个简单例子。

我们要模拟：

> 2026 年 1 月 1 日时，模型审查一个采购项目。

---

# 三十五、理想情况：

模型只能使用：

> 2026 年 1 月 1 日之前已经存在的信息。

---

# 三十六、但是训练数据中加入了：

> 2026 年 3 月发布的更正公告。

这份更正公告说：

> 删除原资格条件。

---

# 三十七、现在模型回头判断 1 月的原始 Clause：

> “这条可能存在问题。”

它为什么这么聪明？

可能不是它真正推理出来的。

而是因为：

> 它已经知道后来被删掉了。

---

# 三十八、这就是典型的：

# Look-ahead Bias

向未来偷看。

---

# 三十九、可以写成：

\[
\boxed{
InformationTime
\le
PredictionTime
}
\]

这应该是很多时序任务的基本约束。

---

# 四十、如果：

```text
information_time
>
prediction_time
```

就要高度警惕：

> Temporal Leakage。

---

# 四十一、政府采购数据里“未来信息”非常多

例如：

```text
更正公告
投诉处理结果
质疑答复
监管处罚
中标结果
废标结果
合同履约结果
法院裁判
后续审计报告
```

---

# 四十二、这些东西当然非常有价值。

但如果任务是：

> 在采购文件发布时预测风险，

这些未来结果：

> 不能进入 Input。

---

# 四十三、但是它们可以干什么？

可以用于：

# Label Construction

---

# 四十四、比如：

原始项目发布时间：

```text
T0
```

半年后出现监管结论：

```text
T1
```

我们可以用 T1：

> 帮助专家构造 Gold Label。

---

# 四十五、但模型输入必须仍然是：

> T0 时点可见的信息。

这叫：

# Retrospective Label, Prospective Input

---

# 四十六、中文可以理解成：

> **允许未来帮助我们知道正确答案，但不能让模型在回答时提前看到未来。**

---

# 四十七、这和考试很像。

老师可以：

> 看标准答案批卷。

学生考试时：

> 不能拿标准答案。

---

# 四十八、所以 Dataset 里最好区分：

```text
event_time
information_available_time
annotation_time
```

---

# 四十九、例如：

```json
{
  "project_publish_time": "2025-06-01",
  "correction_time": "2025-06-08",
  "annotation_time": "2026-01-10"
}
```

---

# 五十、训练样本如果模拟：

```text
2025-06-01
```

模型输入：

> 不应该使用 6 月 8 日更正内容。

---

# 五十一、但是 Label 可以由：

> 2026 年专家回顾判定。

这完全合理。

---

# 五十二、所以 Temporal Dataset 最重要的不是：

> “数据是哪一年爬的”。

而是：

> **当时模型应该知道什么？**

---

# 五十三、第六类：Lineage Leakage

这是我们前几阶段反复保存 Data Lineage 的重要原因。

假设 Test 中有样本：

```text
T001
```

团队把它交给 LLM：

> “帮我生成 20 种改写。”

得到：

```text
S001
S002
...
S020
```

---

# 五十四、这些 Synthetic Samples：

> 文本全都和 T001 不完全一样。

Exact Dedup：

> 抓不到。

---

# 五十五、然后 S001～S020：

> 进入 Train。

最终测试 T001：

模型表现特别好。

---

# 五十六、这是：

# Lineage Leakage

因为训练数据：

> 是从 Test 派生出来的。

---

# 五十七、所以 Data Augmentation 的一个铁律：

\[
\boxed{
ChildSample
inherits
ParentSplit
}
\]

---

# 五十八、如果 Parent：

```text
Test
```

Child：

> 不能去 Train。

---

# 五十九、同理：

```text
翻译
改写
摘要
扩写
格式转换
问题生成
答案生成
Hard Negative生成
```

都属于：

> Derivation。

---

# 六十、所以每一个合成样本最好保存：

```text
source_sample_id
parent_sample_id
generation_method
generation_model
generation_prompt_version
```

---

# 六十一、例如：

```json
{
  "sample_id": "SYN-001",
  "source_sample_id": "TEST-991",
  "generation_method": "paraphrase",
  "split": "test"
}
```

而不是：

> 重新随机 Split。

---

# 六十二、这是 Data Lineage 真正开始发挥作用的地方。

---

# 六十三、第七类：Answer Leakage

这比 Label Leakage 更广。

假设 Test Case：

```text
Clause:
供应商须在本市设立固定服务机构。
```

Gold Rationale：

> 该条件可能构成与履约无直接必要联系的地域性限制，需要结合项目实际服务要求审查。

---

# 六十四、团队没有把 Test Clause 放进 Train。

但是把：

# Gold Rationale

放进了一个：

```text
专家知识库
```

---

# 六十五、模型测试时通过 RAG：

> 检索出了这条专家解释。

然后几乎原样回答。

---

# 六十六、项目隔离了吗？

隔离了。

Train/Test Row 重叠了吗？

没有。

但 Benchmark：

> 仍然污染。

---

# 六十七、这就是：

# Answer Leakage

---

# 六十八、它可以通过：

```text
RAG
Prompt Examples
Rule Engine
FAQ
Knowledge Base
Few-shot Cases
```

进入系统。

---

# 六十九、所以 Benchmark 不只是测试：

# Model Weights

而是测试：

# Full System

---

# 七十、如果最终产品是：

```text
LLM
+
RAG
+
Rules
```

那么评测隔离必须针对整个：

# System Boundary

---

# 七十一、可以画成：

```text
                 Benchmark Firewall
        ┌──────────────────────────────┐
        │                              │
        │  Model Weights               │
        │  Prompt                      │
        │  RAG                         │
        │  Rules                       │
        │  Tools                       │
        │  Synthetic Data              │
        │                              │
        └──────────────────────────────┘
                        │
                        ▼
                      TEST
```

不是只检查：

> Model Weight。

---

# 七十二、第八类：RAG Leakage

这一类尤其值得单独拿出来。

假设我们评测：

> 模型是否能识别某采购风险。

RAG 数据库里有：

```text
法律法规
财政部门规范
正式政策
```

这是：

> 合理知识。

---

# 七十三、但 RAG 里还有：

```text
该Test项目的专家审查报告
该项目投诉处理结果
该项目内部风险结论
```

那就：

> 不合理。

---

# 七十四、所以要区分：

# Allowed Knowledge

与：

# Test-specific Knowledge

---

# 七十五、Allowed Knowledge 可以包括：

```text
公开法律
公开法规
一般业务指南
截至评测时点有效的政策
```

---

# 七十六、Test-specific Knowledge 可能包括：

```text
测试项目专家答案
测试项目内部分析
测试项目最终投诉结果
专门针对该Test Case编写的解释
```

---

# 七十七、这是非常重要的 Benchmark Contract

在评测前要写清楚：

> **系统允许访问哪些外部知识？**

---

# 七十八、例如：

```text
允许：
截至项目发布日期已经生效的法规库

禁止：
该项目后续投诉结论
该项目人工Gold答案
```

---

# 七十九、如果不定义，

两个系统比较会非常不公平。

Model A：

> 只看法律。

Model B：

> 知识库里藏着答案。

然后 B 得分更高。

---

# 八十、你实际上不是比较：

> 模型能力。

而是在比较：

> 谁更接近看过标准答案。

---

# 八十一、第九类：Human-in-the-loop Leakage

这是最容易被忽略的一类。

假设 Final Test：

> 1000 条。

---

# 八十二、第一版模型错了：

> 300 条。

团队逐条看完这 300 条。

---

# 八十三、总结：

```text
本地服务机构类容易错
ISO证书类容易错
评分年限类容易错
```

然后修改：

```text
Prompt
Rule
Training Data
```

---

# 八十四、第二版再跑同一 Test。

错：

> 200 条。

---

# 八十五、团队再次看完。

再改。

---

# 八十六、跑 30 个版本以后：

Test 成绩：

> 越来越高。

---

# 八十七、但是 Test 还是：

> 真正独立的 Test 吗？

严格意义上：

> 已经不是了。

---

# 八十八、因为 Test 的信息已经通过：

# Human Brain

进入了系统设计。

---

# 八十九、这就是：

# Human-in-the-loop Leakage

或者：

# Test Peeking

---

# 九十、所以 Test 污染不需要：

> Copy/Paste。

人类记住错误模式：

> 就已经形成信息通道。

---

# 九十一、这可以写成：

```text
Test
 ↓
Developer sees errors
 ↓
Prompt / Rules / Data changes
 ↓
System
 ↓
Same Test
```

形成一个反馈环。

---

# 九十二、这叫：

# Benchmark Feedback Loop

---

# 九十三、而 Validation 的存在：

> 就是为了让你合法地做这种事情。

---

# 九十四、所以开发阶段应该：

```text
Train
+
Validation
```

不断迭代。

Final Test：

> 少碰。

---

# 九十五、成熟一点可以设计三层

```text
Development Set
Validation Set
Locked Test Set
```

---

# 九十六、甚至：

```text
Public Test
Private Hidden Test
```

开发人员：

> 只看到 Public。

Final Score：

> Private。

---

# 九十七、这就是很多竞赛为什么会有：

> 私榜。

因为大家如果一直调公开榜：

> 会对公开榜过拟合。

---

# 九十八、LLM 项目也是一样。

---

# 九十九、第十类：Benchmark Contamination

这是比普通 Data Leakage 更大的概念。

什么意思？

某个 Benchmark：

> 已经长期公开。

---

# 一百、基础模型训练语料中：

> 可能已经包含它。

你下载一个开源模型，

即使你自己从未：

> 用 Test 做 SFT，

它的 Pretraining 阶段：

> 可能已经见过这个 Benchmark。

---

# 一百零一、那么你的分数：

> 可能高估真正泛化能力。

---

# 一百零二、这就是：

# Pretraining Contamination

---

# 一百零三、对于我们的政府采购领域，

这给出一个很有价值的策略：

高价值 Gold Test 最好尽可能包含：

```text
内部专家新标案例
近期新增项目
从未公开发布的衍生Benchmark
高质量私有Hard Cases
```

---

# 一百零四、不是因为：

> 私有就天然更正确。

而是因为：

> 更容易控制模型有没有见过。

---

# 一百零五、特别是公开互联网题库，

现在越来越需要问：

> 基础模型预训练是否可能见过？

---

# 一百零六、但这里要避免走极端。

并不是所有公开资料：

> 都不能测试。

而是：

> **必须知道公开 Benchmark 的污染风险更高。**

---

# 一百零七、所以可以给 Benchmark Case 增加：

```text
contamination_risk
```

例如：

```text
low
medium
high
```

---

# 一百零八、什么可能是 High？

比如：

> 公开多年、广泛转载、Github大量镜像的测试题。

---

# 一百零九、什么可能 Low？

比如：

> 最近内部专家刚构造、未进入公开网络的案例。

---

# 一百一十、这不是绝对证明。

只是：

> 风险评级。

---

# 一百一十一、现在看一个非常隐蔽的泄漏：

# Post-outcome Feature Leakage

假设我们训练一个模型判断：

> 招标文件是否可能引起投诉。

Input 中加入：

```text
complaint_count
```

---

# 一百一十二、但是：

`complaint_count`：

> 只有项目结束以后才知道。

---

# 一百一十三、模型准确率可能非常高。

为什么？

因为它不是在预测：

> 会不会投诉。

它在读取：

> 已经投诉了几次。

---

# 一百一十四、这就是：

# Outcome Leakage

---

# 一百一十五、类似字段还有：

```text
是否被更正
最终废标原因
质疑次数
监管处理结果
最终合同是否签署
```

如果任务时点早于这些结果：

> 都不能放进 Input。

---

# 一百一十六、所以任何 Feature 都要问：

> **在预测时点，它真的可用吗？**

---

# 一百一十七、可以建立：

# Availability Test

对每个字段问：

```text
这个字段什么时候产生？
模型什么时候做预测？
```

---

# 一百一十八、如果：

\[
FeatureAvailableTime
>
PredictionTime
\]

那么：

> 高度可疑。

---

# 一百一十九、这个原则不限政府采购。

金融、医疗、风控：

> 都一样。

---

# 一百二十、现在看一个采购例子

我们要判断：

> 某资格条件发布时是否需要重点复核。

字段：

```text
项目预算
采购方式
采购品目
原始资格条款
```

在发布时：

> 都存在。

合理。

---

# 一百二十一、另一些字段：

```text
后续更正次数
质疑是否成立
投诉结果
最终中标供应商
```

在发布时：

> 还不存在。

不能作为预测 Input。

---

# 一百二十二、但是它们可以帮助：

> 建 Label。

再次强调：

```text
Label Construction Data
≠
Model Input Data
```

---

# 一百二十三、这一条非常重要。

---

# 一百二十四、现在看 Annotation Leakage

假设专家在标注时看到：

```text
后续监管认定结果
```

然后确定：

```text
risk_present = true
```

这是允许的吗？

---

# 一百二十五、可以。

如果我们的目的：

> 是建立尽量准确的回顾性 Gold Label。

---

# 一百二十六、但模型 Input：

> 不能看到后续监管结果。

---

# 一百二十七、所以标注系统要区分两个界面：

```text
Annotator View
```

和：

```text
Model View
```

---

# 一百二十八、Annotator View 可以有：

```text
原文件
上下文
法规
后续证据
裁决
```

---

# 一百二十九、Model View 只允许：

> 预测时点可得的信息。

---

# 一百三十、这就是：

# Annotation Privilege

标注者可以有更多证据。

模型：

> 不可以。

---

# 一百三十一、如果没有这个区别，

很多团队会无意中：

> 把标注辅助信息一起导出成模型 Feature。

---

# 一百三十二、现在看 Metadata Leakage

例如：

```text
annotator_comment = “典型地域限制案例”
```

你以为训练只用了：

```text
clause_text
```

但数据加载代码：

> 把整个 JSON 序列化给模型。

于是 Prompt 里出现：

```text
annotator_comment
```

---

# 一百三十三、这类 Bug 特别隐蔽。

所以 SFT Input Builder 应该：

> **白名单字段。**

而不是：

> “除了 label 之外全部输入”。

---

# 一百三十四、也就是：

```text
allowed_input_fields = [
    clause_text,
    section_path,
    allowed_context
]
```

---

# 一百三十五、而不是：

```text
drop(label)
然后剩下全部喂进去
```

---

# 一百三十六、这叫：

# Allowlist > Blocklist

对于高风险数据系统，

白名单通常：

> 更安全。

---

# 一百三十七、为什么？

新加一个字段：

```text
expert_final_decision
```

如果采用 Blocklist，

开发者忘了加进删除列表：

> 它就泄漏。

---

# 一百三十八、如果用 Allowlist：

> 新字段默认不会进入模型。

---

# 一百三十九、非常实用。

---

# 一百四十、现在看 Prompt Leakage

假设 Test 中有一类特别难：

> 本地服务机构。

团队根据 Test 错误改 System Prompt：

```text
特别注意：
涉及要求供应商在项目所在地预先设立机构时，
重点判断是否与履约存在必要关系。
```

---

# 一百四十一、这条规则本身：

> 没有复制 Test 原文。

但它是根据 Test 错误：

> 专门总结出来的。

---

# 一百四十二、如果以后还拿同一 Test 报最终成绩，

分数：

> 已经受到 Test 信息影响。

---

# 一百四十三、这就是：

# Prompt Overfitting to Test

---

# 一百四十四、同理：

Rule Engine：

```text
if "本市设立固定机构":
    increase_risk_score()
```

如果这个 Rule：

> 是看了 Final Test 后写的，

也是 Test 污染。

---

# 一百四十五、所以完整 Benchmark Audit 必须记录：

```text
prompt_version
rule_version
rag_version
model_version
```

---

# 一百四十六、不然：

> 你甚至不知道某次 Test 到底测了什么系统。

---

# 一百四十七、现在看 Threshold Leakage

假设模型输出风险概率：

```text
0～1
```

我们需要选择：

```text
threshold
```

---

# 一百四十八、如果在 Test 上试：

```text
0.3
0.4
0.5
0.6
```

然后选择 Test F1 最好的：

```text
0.42
```

---

# 一百四十九、你已经：

> 用 Test 调参。

---

# 一百五十、正确做法：

Threshold：

> 在 Validation 上选。

Test：

> 只使用已经冻结的 Threshold。

---

# 一百五十一、所以 Test 污染不只是：

> 文本。

一个数字参数：

> 也可以因为 Test 而过拟合。

---

# 一百五十二、类似还有：

```text
Temperature
Top-p
Retrieval k
Rerank threshold
Abstention threshold
Rule weight
```

---

# 一百五十三、所有这些：

> 都应该主要用 Validation 调。

---

# 一百五十四、现在建立一个重要分类：

# Direct Leakage

与：

# Indirect Leakage

---

# 一百五十五、Direct：

```text
Test原文进入Train
Test标签进入Input
Test答案进入RAG
```

比较容易理解。

---

# 一百五十六、Indirect：

```text
看Test错误后改Prompt
根据Test调Threshold
从Test生成Synthetic Data
根据Test写Rule
```

---

# 一百五十七、Indirect 往往：

> 更难审计。

---

# 一百五十八、因此真正专业的 Benchmark Governance：

> 需要记录开发历史。

---

# 一百五十九、例如每次实验：

```text
experiment_id
model_version
prompt_version
rule_version
rag_snapshot
dataset_version
split_version
```

---

# 一百六十、以及：

```text
which benchmark was inspected
```

---

# 一百六十一、这会让我们以后知道：

> 某个 Final Test 是否已经被开发人员多次使用。

---

# 一百六十二、现在出现一个重要概念：

# Benchmark Firewall

Benchmark 防火墙。

---

# 一百六十三、什么是 Firewall？

不是某一个算法。

而是一套：

> **让 Final Test 与日常开发流程隔离的制度 + 数据 + 工程机制。**

---

# 一百六十四、第一层 Firewall：

# Access Control

不是所有人：

> 都能看到 Final Test Label。

---

# 一百六十五、例如：

```text
Developers
→ 可以看Train / Validation

Benchmark owner
→ 管理Hidden Test
```

---

# 一百六十六、开发者提交：

```text
model endpoint
```

系统自动：

> 跑 Hidden Test。

只返回：

```text
summary metrics
```

---

# 一百六十七、这样减少：

> 针对单个 Test Case 调参。

---

# 一百六十八、第二层 Firewall：

# Dataset Isolation

Final Test 文件：

> 放在独立目录 / 权限空间。

---

# 一百六十九、不要：

```text
dataset/
  train.jsonl
  val.jsonl
  test.jsonl
```

然后大家都随便打开。

对早期课程练习当然可以。

但成熟项目：

> 可以更严格。

---

# 一百七十、第三层 Firewall：

# Input Allowlist

测试运行时：

只给系统允许的字段。

例如：

```text
clause_text
section_path
allowed_context
```

---

# 一百七十一、不传：

```text
gold_label
expert_rationale
future_outcome
annotation_note
```

---

# 一百七十二、第四层 Firewall：

# RAG Snapshot

评测时记录：

```text
knowledge_snapshot_version
```

---

# 一百七十三、例如：

```text
rag_knowledge_2026_09_01
```

---

# 一百七十四、这样以后知道：

> 模型当时查的是哪一版知识库。

---

# 一百七十五、第五层 Firewall：

# Time Cutoff

对于 Temporal Benchmark：

明确：

```text
knowledge_cutoff
```

---

# 一百七十六、例如：

```text
Test项目发布日期：
2026-06-01

允许知识：
≤ 2026-06-01
```

---

# 一百七十七、这样未来法规：

> 不会倒灌回去。

---

# 一百七十八、第六层 Firewall：

# Lineage Guard

任何：

```text
Synthetic
Paraphrase
Translation
Derived Sample
```

如果祖先属于 Test：

> 自动禁止进入 Train。

---

# 一百七十九、第七层 Firewall：

# Evaluation Log

每次运行 Final Test：

记录：

```text
who
when
which model
which prompt
which rules
which RAG snapshot
```

---

# 一百八十、这样可以知道：

> Test 被使用了多少次。

---

# 一百八十一、这七层组合起来：

才真正接近：

# Benchmark Firewall

---

# 一百八十二、现在给它画一张图

```text
                   Final Test
                       │
             ┌─────────┴─────────┐
             │ Benchmark Firewall │
             └─────────┬─────────┘
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
 Access Control   Input Allowlist    Time Cutoff
       │               │                │
       ├───────────────┼────────────────┤
       ▼               ▼                ▼
 Lineage Guard    RAG Snapshot      Eval Logging
       │               │                │
       └───────────────┼────────────────┘
                       ▼
                  Model/System
                       │
                       ▼
                    Metrics
```

---

# 一百八十三、现在建立 Leakage Audit Checklist

这是第七阶段最实用的产物之一。

第一组：

# Split Integrity

检查：

```text
同project_id是否跨Split？
同duplicate_group_id是否跨Split？
同source_case_id是否跨Split？
派生样本是否跨Split？
```

---

# 一百八十四、第二组：

# Text Similarity

检查：

```text
Test vs Train
Exact match?

Near duplicate?

Template overlap?

High embedding similarity?
```

---

# 一百八十五、第三组：

# Label Leakage

检查：

```text
Input中是否存在Gold Label？

是否存在专家结论？

是否存在修改建议？

是否存在裁决结果？

是否存在风险类别名称？
```

---

# 一百八十六、第四组：

# Temporal Leakage

检查：

```text
Input字段是否在预测时点可用？

法规版本是否符合时间点？

是否使用了后续更正？

是否使用了后续投诉结论？

是否使用了未来统计信息？
```

---

# 一百八十七、第五组：

# RAG Leakage

检查：

```text
RAG中是否存在Test Case本身？

是否存在Test Gold Rationale？

是否存在该项目后续审查报告？

知识库Snapshot是否被冻结？
```

---

# 一百八十八、第六组：

# Prompt / Rule Leakage

检查：

```text
Prompt是否根据Final Test错误专门改过？

Rules是否根据Final Test写过？

Threshold是否在Test上调过？
```

---

# 一百八十九、第七组：

# Human Leakage

检查：

```text
开发人员是否看过Test Label？

是否逐条看过Final Test Error？

Final Test被跑过多少轮？

是否已经实际上变成Validation？
```

---

# 一百九十、第八组：

# Contamination Risk

检查：

```text
Benchmark是否公开多年？

基础模型是否可能见过？

Test是否来自大量互联网转载材料？

是否有低污染的私有/近期补充集？
```

---

# 一百九十一、把这 8 组跑完，

我们才真正可以说：

> “做过泄漏审计。”

---

# 一百九十二、现在谈 Leakage Severity

不是每个问题都一样严重。

可以概念分：

```text
Critical
High
Medium
Low
```

---

# 一百九十三、Critical

例如：

```text
Test答案进入SFT Train
Test Gold Rationale进入RAG
同一Exact Duplicate跨Train/Test
```

这基本：

> 直接破坏 Benchmark。

---

# 一百九十四、High

例如：

```text
Test改写样本进入Train
测试项目后续裁决进入Input
长期反复用Final Test调Prompt
```

---

# 一百九十五、Medium

例如：

```text
大量Template overlap
同代理机构风格高度重合
```

是否致命：

> 取决于评测目标。

---

# 一百九十六、Low

可能是：

```text
公共法规知识在Train和Test都出现
```

如果它本来就是：

> Allowed Knowledge。

这通常：

> 不叫问题。

---

# 一百九十七、所以不要把 Leakage Audit 变成：

> “只要任何信息重复就全部判死刑。”

---

# 一百九十八、我们还是要问：

# Does this invalidate the generalization claim?

它是否让你的：

> 泛化结论失真？

---

# 一百九十九、这是最核心的判断。

---

# 二百、例如同一部《政府采购法》

Train 和 Test：

> 都涉及。

并不会使：

> “新项目泛化”

这个结论失效。

---

# 二百零一、但同一个项目的专家答案：

Train/Test 都出现。

就会直接：

> 让泛化结论失真。

---

# 二百零二、所以：

\[
\boxed{
Leakage
不是简单的“信息重复”
而是“不恰当的信息可用性”
}
\]

---

# 二百零三、现在设计一个 Leakage Record

发现一个问题时，

不要只写：

```text
有泄漏
```

---

# 二百零四、最好记录：

```json
{
  "audit_id": "LEAK-00017",
  "test_sample_id": "TEST-0091",
  "related_train_sample_id": "TRAIN-2217",

  "leakage_type": "lineage_leakage",
  "severity": "critical",

  "evidence": "train sample derived from test sample paraphrase",

  "action": "remove_train_sample",

  "status": "resolved",

  "audit_version": "leakage_audit_v0.1"
}
```

---

# 二百零五、为什么需要 `evidence`？

因为：

> “疑似泄漏”

和：

> “确认泄漏”

不是一回事。

---

# 二百零六、可以有：

```text
suspected
confirmed
resolved
accepted_risk
```

---

# 二百零七、例如 Template Overlap：

可能：

```text
accepted_risk
```

因为我们主 Benchmark 本来就允许：

> Seen Template。

---

# 二百零八、但是报告里：

> 必须说清楚。

---

# 二百零九、这叫：

# Evaluation Transparency

不是所有问题都必须消灭。

但：

> 必须让分数的含义清楚。

---

# 二百一十、现在看一个很真实的案例

假设我们有：

```text
Test Sample T1
```

条款：

> “供应商注册地须在本市。”

Gold：

```text
potential_risk
```

---

# 二百一十一、Train 里没有 T1。

项目也不同。

看起来很干净。

---

# 二百一十二、但我们发现 Train 中有：

```text
Synthetic S77:
投标企业须为本地注册企业。
```

它来自专家培训案例 E12。

---

# 二百一十三、继续查 Lineage：

```text
E12
```

原来就是：

> T1 的内部专家分析版本。

---

# 二百一十四、于是链条是：

```text
T1 Test Case
   ↓
Expert Case E12
   ↓
Synthetic Rewrite S77
   ↓
Train
```

---

# 二百一十五、文本 Dedup：

> 很可能发现不了。

Project ID：

> 完全不同。

---

# 二百一十六、只有：

# Lineage

才能发现。

---

# 二百一十七、这就是为什么前六个阶段一直强调：

> 来源和血缘不能丢。

---

# 二百一十八、再看另一个案例

Test：

> 某评分办法。

RAG 里没有 Gold Answer。

但 Rule Engine 有：

```text
如果“本地服务机构”得分 > 0
则标记地域风险
```

---

# 二百一十九、这条 Rule：

> 是开发人员看 Test 错误后加的。

---

# 二百二十、那么最终系统测试成功，

到底是谁成功？

```text
LLM？
Rule？
Test-specific patch？
```

---

# 二百二十一、这就是为什么一个成熟的 Benchmark：

> 评的是系统版本。

需要记录：

```text
model_version
prompt_version
rule_version
rag_version
```

---

# 二百二十二、否则你没法解释：

> 分数为什么提高。

---

# 二百二十三、现在看 Validation 的正确角色

假设你发现：

> “本地服务机构”这种案例总出错。

应该在哪里发现？

最好：

# Validation

---

# 二百二十四、然后：

```text
改Prompt
改SFT
改Rule
```

继续看 Validation。

---

# 二百二十五、等方案冻结以后：

> 才去 Final Test。

---

# 二百二十六、如果 Final Test 又暴露新问题怎么办？

可以记录。

但如果你：

> 根据这些问题继续开发，

那下一轮最好：

# 新建 Test Version

或者：

> 把当前 Test 降级为 Development Benchmark。

---

# 二百二十七、这是一种很成熟的 Benchmark 生命周期管理。

---

# 二百二十八、比如：

```text
GoldTest_v1
```

使用一段时间后：

> 团队已经熟悉大量案例。

---

# 二百二十九、此时它仍然很适合：

# Regression Test

---

# 二百三十、也就是说：

> 检查新模型有没有退化。

---

# 二百三十一、但不再适合声称：

> “完全未见过的最终泛化成绩”。

---

# 二百三十二、然后创建：

```text
GoldTest_v2_private
```

作为新 Final Test。

---

# 二百三十三、所以 Benchmark 也有生命周期：

```text
Hidden Final Test
       ↓
被使用/被分析
       ↓
Development Regression Set
       ↓
新Hidden Test替代
```

---

# 二百三十四、这叫：

# Benchmark Rotation

---

# 二百三十五、尤其长期 AI 产品：

> 很有必要。

---

# 二百三十六、否则一个 Test 用三年，

团队每个人都能背答案。

最后 99%：

> 不代表任何新能力。

---

# 二百三十七、现在看 Benchmark Contamination 与 Memorization

假设模型真的见过测试题。

是不是一定：

> 会背出来？

不一定。

---

# 二百三十八、但我们已经不能确定高分来自：

```text
真正推理
```

还是：

```text
记忆
```

---

# 二百三十九、这就是污染最大的问题：

> **它破坏的是分数的可解释性。**

---

# 二百四十、所以 Benchmark 的价值不是：

> 有 1000 道题。

而是：

> 这些题能支持一个可信结论。

---

# 二百四十一、例如：

> “模型对未来未见采购项目的高风险条款召回率为 91%。”

要说这句话，

你必须能证明：

```text
未来
未见
项目
高风险
```

这些限定：

> 基本成立。

---

# 二百四十二、如果 Test 已经污染，

“91%”只是一个数字。

---

# 二百四十三、这就是第七阶段最深的一层：

# Benchmark = Claim

一个 Benchmark 本质上是在支持：

> 一个能力声明。

---

# 二百四十四、所以每个 Benchmark 都应该有：

# Evaluation Claim

例如：

> **评估 ProcurementAI 在没有访问该项目后续裁决和专家答案的情况下，对未参与训练的新采购项目条款进行潜在合规风险筛查的能力。**

---

# 二百四十五、有了这句话，

我们就能判断：

某个信息是否泄漏。

---

# 二百四十六、例如 RAG 使用有效法规：

> 与这个 Claim 不冲突。

---

# 二百四十七、RAG 使用该项目最终投诉结论：

> 与这个 Claim 冲突。

---

# 二百四十八、所以 Leakage 不是凭感觉判断。

它应该相对于：

# Evaluation Claim

判断。

---

# 二百四十九、这是一套特别强的思维框架：

```text
先写能力声明
      ↓
定义允许信息
      ↓
定义禁止信息
      ↓
再做Leakage Audit
```

---

# 二百五十、现在第一次设计

# Benchmark Contract

可以概念包括：

```text
task
prediction_time
allowed_inputs
allowed_external_knowledge
forbidden_information
split_policy
test_access_policy
```

---

# 二百五十一、例如：

```json
{
  "task": "procurement_compliance_risk_review",

  "prediction_time": "document_publication_time",

  "allowed_inputs": [
    "target_clause",
    "same-document prior context",
    "project_metadata_available_at_publication"
  ],

  "allowed_external_knowledge": [
    "regulations effective at prediction_time"
  ],

  "forbidden_information": [
    "future_correction_notice",
    "complaint_result",
    "gold_rationale",
    "expert_final_decision"
  ]
}
```

---

# 二百五十二、注意：

这不是最终法律制度。

只是：

> 我们的评测工程合同。

---

# 二百五十三、这个 Contract 非常有用。

因为不同人不会：

> 各自猜什么算泄漏。

---

# 二百五十四、现在看 RAG 的时间问题

例如法规：

2025 年版本：

```text
Rule V1
```

2026 年修订：

```text
Rule V2
```

---

# 二百五十五、Test Case 发生于：

```text
2025
```

如果 RAG 永远只返回：

> 2026 V2，

可能发生：

# Future Law Leakage

---

# 二百五十六、所以法规 RAG 最终必须支持：

```text
effective_from
effective_to
```

---

# 二百五十七、第六课我们会详细处理：

> 法规时间、层级、地域。

今天只需要知道：

> Benchmark Leakage 和 RAG Versioning 是连在一起的。

---

# 二百五十八、现在看另一个时间陷阱

某个项目：

> 2025 年发布。

专家：

> 2026 年标注。

---

# 二百五十九、专家可以用 2026 年新法规吗？

如果我们的 Label 定义是：

> “按 2025 年当时有效规则判断”。

那么：

> 不能直接按 2026 新规则重新定罪。

---

# 二百六十、所以 Annotation 本身也有：

# Temporal Semantics

---

# 二百六十一、标注说明应该写清：

> **按照哪个时点的规范环境判断。**

---

# 二百六十二、否则 Test Gold 本身：

> 可能时间穿越。

---

# 二百六十三、这不是模型泄漏。

这是：

# Gold Construction Error

---

# 二百六十四、但最终效果一样：

> Benchmark 不可信。

---

# 二百六十五、所以第七阶段其实在告诉我们：

# Leakage Audit 不能只查 Train/Test

还要查：

> Gold 本身是怎么来的。

---

# 二百六十六、现在我们给整个数据链加时间

```text
Raw Document
    │ event_time
    ▼
ParsedDocument
    ▼
ClauseUnit
    ▼
Annotation
    │ annotation_time
    ▼
Gold Sample
    ▼
Split
    ▼
Training / Test
```

---

# 二百六十七、再加：

```text
knowledge_snapshot_time
```

和：

```text
model_training_cutoff
```

整个系统就开始真正具有：

# Temporal Provenance

---

# 二百六十八、以后如果问：

> “为什么 2025 年这个 Case 这么判断？”

可以回答：

```text
依据的是当时有效规则
Gold由2026专家回顾标注
模型输入不含2025之后项目结果
```

这才是：

> 专业可解释。

---

# 二百六十九、现在谈泄漏自动检测

哪些能自动？

第一类：

# ID overlap

```text
project_id
document_id
duplicate_group_id
source_case_id
```

很好自动查。

---

# 二百七十、第二类：

# Exact Hash

```text
normalized_text_hash
```

很好查。

---

# 二百七十一、第三类：

# Near Similarity

可以用：

```text
MinHash
Embedding
```

找候选。

---

# 二百七十二、第四类：

# Lineage

沿着：

```text
parent_sample_id
source_sample_id
```

图搜索。

---

# 二百七十三、第五类：

# Temporal Check

比较：

```text
feature_available_time
prediction_time
```

---

# 二百七十四、第六类：

# Input Schema Audit

检查 Input 中：

> 是否包含禁用字段。

---

# 二百七十五、哪些很难全自动？

例如：

> 某条 Prompt 规则是不是因为看 Final Test 才写的？

这需要：

# Process Governance

---

# 二百七十六、所以：

\[
\boxed{
LeakageControl
=
Automation
+
Governance
}
\]

只靠代码：

> 不够。

只靠制度：

> 也不够。

---

# 二百七十七、现在给 `LeakageAudit_V0.1` 设计一个总报告

概念上可以包含：

```text
Audit Scope
Split Version
Dataset Version
Benchmark Version
Model Development Cutoff
```

---

# 二百七十八、然后统计：

```text
Project overlap count
Exact duplicate overlap count
Near duplicate suspects
Lineage violations
Temporal violations
Forbidden-field violations
RAG contamination findings
Human test exposure
```

---

# 二百七十九、例如：

```json
{
  "audit_version": "leakage_audit_v0.1",

  "dataset_version": "procurement_dataset_v0.1",
  "split_version": "procurement_split_v0.1",

  "project_overlap": 0,
  "exact_duplicate_overlap": 0,

  "near_duplicate_suspects": 27,
  "confirmed_near_duplicate_leaks": 3,

  "lineage_violations": 0,
  "temporal_violations": 2,

  "forbidden_input_field_violations": 0,

  "audit_status": "needs_remediation"
}
```

---

# 二百八十、这时不能说：

> Benchmark 已通过。

要先解决：

```text
3个Near Duplicate Leak
2个Temporal Leak
```

---

# 二百八十一、修完再跑：

```text
LeakageAudit_v0.2
```

---

# 二百八十二、这就是工程化质量门槛：

# Quality Gate

---

# 二百八十三、比如规定：

```text
Critical Leakage = 0
```

才能发布 Benchmark。

---

# 二百八十四、High Severity：

> 必须人工审议。

---

# 二百八十五、Medium：

> 可以记录为已知限制。

---

# 二百八十六、这比：

> “我们觉得没泄漏”

靠谱得多。

---

# 二百八十七、现在看一个常见误区：

> “我们从来没把 Test 放进 Train，所以肯定没泄漏。”

错。

---

# 二百八十八、Test 可能通过：

```text
Synthetic
RAG
Rule
Prompt
Threshold
Human
```

六条路回来。

---

# 二百八十九、另一个误区：

> “我们已经做了去重，所以不会泄漏。”

错。

去重：

> 只能解决部分内容重合。

解决不了：

```text
未来信息
答案知识库
Test调Prompt
```

---

# 二百九十、另一个误区：

> “基础模型冻结，没有训练，所以 RAG 泄漏没关系。”

错。

Benchmark 测的是最终系统输出。

RAG 如果：

> 藏着标准答案，

系统一样作弊。

---

# 二百九十一、另一个误区：

> “人看Test不算机器看Test。”

如果人的观察：

> 改变了系统，

就产生了信息通道。

---

# 二百九十二、另一个误区：

> “只要测试样本够新，就一定没污染。”

也不一定。

如果 Test 是从旧案例：

> 改写而来，

而旧案例已在 Train，

仍可能高度相关。

---

# 二百九十三、所以真正核心始终是：

# Information Lineage

信息从哪里来。

---

# 二百九十四、现在做几个思维实验

### 思维实验 A

Train/Test 没有任何相同 `project_id`。

是不是就可以宣布：

> 无泄漏？

不能。

还要检查：

> Duplicate、Template、Lineage、Time、RAG、Human Feedback。

---

# 二百九十五、### 思维实验 B

Test 的原文从未进 Train，

但 Gold Rationale 在 RAG 中。

是否泄漏？

> 是，属于严重 Answer/RAG Leakage。

---

# 二百九十六、### 思维实验 C

Test Case 的改写版本进入 Train。

文字不一样。

是否泄漏？

> 是，属于 Lineage Leakage。

---

# 二百九十七、### 思维实验 D

测试 2025 年项目时，

系统查到了 2026 年才生效的法规。

是否有问题？

> 如果评测目标是模拟 2025 年当时决策，这是 Temporal Leakage。

---

# 二百九十八、### 思维实验 E

专家在 2026 年利用后续证据给 2025 项目标 Gold。

允许吗？

> 可以，只要后续证据不进入模型 Input，并且 Gold 定义明确。

---

# 二百九十九、### 思维实验 F

同一法律法规同时存在于 Train 和 Test 相关 Context。

一定泄漏吗？

> 不一定。公共允许知识不等于测试答案。

---

# 三百、### 思维实验 G

Final Test 跑过 50 次，每次团队根据错误改系统。

它还是完全独立 Final Test 吗？

> 基本不能再这样理解。

它已经逐渐变成 Development Benchmark。

---

# 三百零一、### 思维实验 H

模型 Base Pretraining 可能看过公开 Benchmark。

我们自己没有训练过它。

有没有污染风险？

> 有，属于 Pretraining / Benchmark Contamination 风险。

---

# 三百零二、### 思维实验 I

Input 里没有 Label，

但有字段：

```text
整改状态 = 已整改
```

任务是判断：

> 是否存在问题。

是否可能泄漏？

> 很可能，因为这个字段是结果代理。

---

# 三百零三、### 思维实验 J

Threshold 是在 Test 上挑出来的最佳值。

训练数据完全干净。

Test 分数还能作为纯 Final Estimate 吗？

> 不能，因为 Test 已参与模型选择。

---

# 三百零四、现在总结本阶段最容易犯的 12 个错误

**错误 1：**

> Project 不重叠 = 没有泄漏。

错。

---

**错误 2：**

> 只有原文重复才算泄漏。

错。

答案、派生数据、未来信息都可以泄漏。

---

**错误 3：**

> Label 没进 Input，所以不会 Label Leakage。

错。

可能有 Target Proxy。

---

**错误 4：**

> RAG 不改权重，所以 RAG 里的 Test Answer 不算泄漏。

错。

---

**错误 5：**

> Synthetic Data 字不一样，所以安全。

错。

Lineage 才重要。

---

**错误 6：**

> 未来结果可以作为模型 Feature，因为能提高准确率。

这正是严重 Temporal / Outcome Leakage。

---

**错误 7：**

> 专家能看到的信息，模型也都能看到。

错。

Annotator View 和 Model View 应分开。

---

**错误 8：**

> Final Test 可以无限次调 Prompt。

会产生 Test Peeking。

---

**错误 9：**

> Threshold 调节不算使用 Test。

算。

---

**错误 10：**

> 公开 Benchmark 一定能代表真实泛化。

不一定，可能存在预训练污染。

---

**错误 11：**

> 只要技术上做了隔离，流程治理不重要。

错。

人类反馈也能造成泄漏。

---

**错误 12：**

> Leakage Audit 是一次性的。

错。

Dataset、RAG、Prompt、Rules 每次重要更新后都应该重新检查。

---

# 三百零五、本阶段最重要的 7 个“≠”

```text
Different Project
≠
No Leakage
```

```text
No Exact Duplicate
≠
No Contamination
```

```text
Label Column Removed
≠
No Label Leakage
```

```text
Frozen Model Weights
≠
Clean Evaluation
```

```text
Public Knowledge
≠
Test-specific Answer
```

```text
Future Evidence for Annotation
≠
Future Evidence for Model Input
```

```text
Test Not Used for Gradient
≠
Test Not Used for Development
```

最后一条尤其重要。

---

# 三百零六、再记住本阶段最重要的“=”

\[
\boxed{
CleanBenchmark
=
SplitIsolation
+
TemporalIntegrity
+
LineageIntegrity
+
SystemIsolation
+
HumanProcessControl
}
\]

翻译成人话：

> **真正干净的 Benchmark，不只是 Train 和 Test 的行不重复，而是测试项目、答案、派生数据、时间信息、RAG、Prompt、规则和人工开发反馈都处在被明确控制的边界之内。**

---

# 三百零七、现在把第四课前 7 个阶段连起来

```text
Stage 1
Task Schema
“什么是一条样本？”
       │
       ▼
Stage 2
ParsedDocument
“文件里到底有什么？”
       │
       ▼
Stage 3
ClauseUnit
“文字属于哪个业务要求？”
       │
       ▼
Stage 4
CleanClause
“怎样安全规范文本？”
       │
       ▼
Stage 5
DedupedClauseSet
“这些样本到底有多少独立信息？”
       │
       ▼
Stage 6
DatasetSplit
“哪些数据用来学，哪些留下考试？”
       │
       ▼
Stage 7
LeakageAudit
“考试题真的没有被提前泄露吗？”
```

到这里，我们的数据才第一次开始拥有：

> **可信评测边界。**

---

# 三百零八、但还有一个巨大问题没有解决

现在我们有：

```text
Clause
Clean Text
Dedup Group
Split
Leakage Audit
```

但是：

> **到底让专家标什么？**

---

# 三百零九、如果专家 A 标：

```text
违规
```

专家 B 标：

```text
有风险
```

专家 C 标：

```text
建议修改
```

专家 D 标：

```text
需要进一步核查
```

这些到底是不是：

> 同一个 Label？

---

# 三百一十、再比如风险类型

有人写：

```text
地域限制
```

有人写：

```text
资格条件不合理
```

有人写：

```text
差别待遇
```

有人写：

```text
供应商资格风险
```

---

# 三百一十一、如果没有统一 Schema，

最后得到的不是：

> Gold Dataset。

而是：

> 一堆专家各自语言风格的 Excel。

---

# 三百一十二、所以泄漏控制以后，

第四课的下一步终于进入：

# Label Schema

---

# 三百一十三、本阶段掌握测试

如果现在不看前文，你能够完整解释下面这些问题，第 7 阶段就算真正掌握：

> 为什么 Project-disjoint 不等于没有数据泄漏？

> Data Leakage 的本质是什么？

> 为什么答案相关信息不一定以 Label 字段出现？

> 什么是 Target Proxy？

> 什么是 Label Leakage？

> 为什么“专家意见”也可能泄漏答案？

> 什么是 Duplicate Leakage？

> 什么是 Template Leakage？

> Template overlap 为什么有时不是绝对非法，而是泛化难度问题？

> 什么是 Temporal Leakage？

> 为什么未来更正公告不能帮助模型模拟过去时点判断？

> Prediction Time 和 Information Available Time 有什么关系？

> 为什么未来结果可以辅助 Gold Label，却不能进入 Model Input？

> 什么是 Retrospective Label / Prospective Input？

> 什么是 Lineage Leakage？

> 为什么 Synthetic Data 必须继承母样本 Split？

> 翻译、改写、摘要为什么都属于派生关系？

> 什么是 Answer Leakage？

> 为什么 Gold Rationale 进入 RAG 会污染 Benchmark？

> Allowed Knowledge 和 Test-specific Knowledge 有什么区别？

> 为什么 Benchmark 必须定义 RAG 允许访问的知识范围？

> 什么是 Human-in-the-loop Leakage？

> 为什么反复看 Test Error 会让 Test 逐渐变成 Validation？

> 什么是 Benchmark Feedback Loop？

> 什么是 Pretraining Contamination？

> 为什么公开 Benchmark 的污染风险通常更高？

> 什么是 Outcome Leakage？

> 为什么“后续是否被投诉”不能用于预测发布时的风险？

> Annotator View 和 Model View 为什么必须分开？

> 为什么模型 Input Builder 最好用字段白名单？

> Prompt 如何产生 Test Leakage？

> Rule Engine 如何产生 Test Leakage？

> 为什么 Threshold 也不能在 Final Test 上调？

> Direct Leakage 和 Indirect Leakage 有什么区别？

> 什么叫 Benchmark Firewall？

> Benchmark Firewall 为什么不仅是一个算法？

> Access Control 在 Benchmark 中有什么作用？

> 为什么 Final Test 可以设置 Hidden Label？

> 为什么 RAG Snapshot 需要版本化？

> 为什么 Temporal Benchmark 需要 Knowledge Cutoff？

> 什么是 Lineage Guard？

> 为什么每次 Final Test Run 都值得记录？

> 什么是 Leakage Audit Checklist？

> Leakage Severity 为什么需要分级？

> 为什么“任何重复信息都是泄漏”这种理解也是错误的？

> Evaluation Claim 为什么决定了什么算泄漏？

> 什么叫 Benchmark Contract？

> 为什么 Gold Label 本身也可能存在时间错误？

> 什么是 Temporal Provenance？

> 哪些泄漏可以自动检查？

> 哪些泄漏必须依靠流程治理？

> 为什么 `LeakageAudit_V0.1` 应该成为 Dataset 的正式组成部分？

> 为什么 Final Test 用久以后可以降级为 Regression Set？

> 什么是 Benchmark Rotation？

如果这些你都能自己讲清楚：

\[
\boxed{
第四课第7阶段真正掌握
}
\]

---

# 三百一十四、本阶段最终只记一句话

> **Data Leakage 不只是“Train 里出现了 Test 原文”，而是任何不应该在开发阶段可用的测试相关信息——标签、专家答案、未来结果、派生样本、RAG 内容、Prompt 规则、阈值，甚至人类对 Test 错误的反复观察——越过评测边界并影响了系统；真正可信的 Benchmark 必须依靠数据血缘、时间约束、系统隔离和 Benchmark Firewall 共同保护。**

最后把这一阶段压成一张图：

```text
                    Final Test
                        │
                        ▼
                Evaluation Claim
                        │
                        ▼
                Benchmark Contract
                        │
       ┌────────────────┼─────────────────┐
       ▼                ▼                 ▼
  Allowed Info      Forbidden Info      Time Cutoff
       │                │                 │
       └────────────────┼─────────────────┘
                        ▼
                 Leakage Audit
       ┌────────────────┼──────────────────┐
       ▼                ▼                  ▼
    Dataset           System             Human
       │                │                  │
 Project/Dup       Prompt/RAG/Rules     Test Peeking
 Lineage/Time      Threshold/Tools      Error Feedback
       │                │                  │
       └────────────────┼──────────────────┘
                        ▼
                Benchmark Firewall
                        │
                        ▼
                LeakageAudit_V0.1
                        │
                        ▼
                 Trusted Evaluation
```

---

# 下一阶段：第四课 · 第 8 阶段
## Label Schema——专家到底应该标什么？为什么“有风险 / 没风险”两个标签远远不够构建一个真正的政府采购专业模型？

第 8 阶段我们会第一次真正把：

```text
专家判断
```

变成：

# 可训练、可评测、可统计的结构化标签。

核心会解决：

```text
risk_present
risk_type
risk_level
needs_review
rationale
evidence
suggested_action
```

这些字段究竟：

> 哪些应该成为训练 Target？

哪些：

> 只是 Metadata？

哪些：

> 应该由专家填写？

哪些：

> 可以后续派生？

而且会正式建立我们政府采购风险审查的第一版五大类：

```text
A 供应商资格
B 技术参数
C 商务要求
D 评分标准
E 采购需求
```

同时处理一个非常关键的问题：

> **“不知道 / 证据不足 / 需要人工复核”到底是不是一个合法答案？**

最终我们会得到：

# `AnnotationSchema_V0.1`

从那个阶段开始，我们的数据才真正进入：

> **专家标注体系。**

---
