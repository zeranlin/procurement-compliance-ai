# 第八课 · 第 9 阶段
# CPT vs SFT：什么时候继续预训练，什么时候监督微调，怎样正确串联？
## 两者都会改 Weight，但一个在学“领域分布”，一个在学“任务行为”；真实项目里怎样判断到底该做哪一个、先做哪一个、做完以后怎样评测？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **DomainGap ≠ BehaviorGap。不懂领域和不会按要求做任务，是两个不同问题。**
2. **TrainingChoice 必须由 ErrorDiagnosis 驱动。先判断错误发生在哪一层，再决定 CPT、SFT、RAG 或 Agent。**
3. **DomainCompetence ≠ InstructionBehavior。领域底座能力和任务行为能力必须分层看。**
4. **CPT = WorldModeling，SFT = BehaviorShaping。CPT 主要塑造领域表示，SFT 主要塑造任务行为。**
5. **CourseOrder ≠ ProductionTrainingGraph。课程先学 SFT 后学 CPT，不代表真实训练顺序就应该如此。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `CPT` | CPT/继续预训练：在领域语料上继续执行预训练目标 |
| `SFT` | 监督微调：用监督样本继续更新模型参数 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `Observe` | Observe/观察：读取当前状态和工具结果 |

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

到第 8 阶段，我们已经把 CPT 的数据、训练目标、采样、遗忘、能力保持和合成数据都串起来了。

现在必须解决一个真实项目里最容易做错的技术路线问题：

> **模型效果不好，到底应该继续做 CPT，还是做 SFT？**

很多团队会把这两件事混在一起：

```text
模型不懂领域
→ 做SFT

模型格式不好
→ 继续CPT

模型答错政策
→ 再训练一遍

模型不会按Schema输出
→ 加更多领域语料
```

这些做法的问题是：

> 没有先判断“错的是哪一层”。

所以本阶段正式建立：

# `ProcurementCPTSFTDecisionPolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

CPT 和 SFT 都会改变模型参数。

但它们优化的不是同一个问题。

\[
\boxed{
DomainGap
\neq
BehaviorGap
}
\]

# Domain Gap
## 领域分布差距

指：

> 模型对政府采购语言、结构、术语和统计分布本身不够熟。

# Behavior Gap
## 任务行为差距

指：

> 模型虽然理解输入，但不会按要求完成任务、遵守格式或执行输出协议。

所以：

\[
\boxed{
CPT
主要解决
DomainGap
}
\]

\[
\boxed{
SFT
主要解决
BehaviorGap
}
\]

---

# 二、核心心智模型 ①：先诊断 Error Layer，再选择 Training Method

错误流程：

```text
效果不好
↓
训练更多
```

专业流程：

```text
Observed Error
观察到错误
↓
Error Decomposition
拆解错误来源
↓
Domain Gap?
是否领域理解不足
↓
Behavior Gap?
是否任务行为不足
↓
Knowledge Freshness Gap?
是否外部知识过期
↓
Tool / Workflow Gap?
是否执行链问题
↓
Choose Intervention
选择干预方式
```

中文解释：

> 先判断问题发生在领域理解、任务行为、知识新鲜度，还是工具执行层，再决定 CPT、SFT、RAG 或 Agent。

所以：

\[
\boxed{
TrainingChoice
必须由
ErrorDiagnosis
驱动
}
\]

---

# 三、CPT 到底学什么？

CPT 仍然做：

# Causal Language Modeling
## 因果语言建模

它学习：

```text
政府采购术语怎样共同出现
采购文件结构怎样延续
领域语言有哪些统计模式
长文档章节之间怎样关联
行业采购文本是什么风格
```

所以更接近：

\[
\boxed{
CPT
=
LearnDomainDistribution
}
\]

它在提升的是：

> 模型的领域底座。

---

# 四、SFT 到底学什么？

SFT：

# Supervised Fine-Tuning
## 监督微调

通常有明确的：

```text
Input
输入

Target Response
目标回答
```

例如：

```text
输入：
某采购条款

目标输出：
risk_type
reason
evidence
recommendation
```

SFT 主要学习：

```text
任务格式
输出风格
指令遵循
Schema结构
回答边界
拒答行为
```

所以：

\[
\boxed{
SFT
=
LearnTaskBehavior
}
\]

---

# 五、核心心智模型 ②：Language Modeling Competence 和 Instruction Behavior 是两个不同能力层

一个模型可能：

```text
很懂采购语言
但不会按JSON输出
```

也可能：

```text
JSON输出非常稳定
但对采购概念理解浅
```

所以：

\[
\boxed{
DomainCompetence
\neq
InstructionBehavior
}
\]

前者偏：

> CPT。

后者偏：

> SFT。

这就是为什么两者不能互相简单替代。

---

# 六、什么时候优先做 CPT？

典型信号包括：

```text
大量高质量无标注领域文本存在

模型对领域术语和结构理解不稳定

长采购文档语言建模明显弱

行业语料分布和通用语料差异大

SFT样本有限但无标注Corpus很大

希望提升的是多任务共享的领域底座
```

例如：

> 不只是风险识别弱，而是多个采购任务都表现出领域理解不足。

这时更像：

\[
\boxed{
SharedDomainRepresentationGap
}
\]

CPT 更有价值。

---

# 七、什么时候优先做 SFT？

典型信号包括：

```text
模型基本理解输入
但不会按要求回答

格式不稳定
Schema不遵守
不会拒答
任务边界不清
分类标签不稳定
解释模板不一致
```

这类问题更像：

\[
\boxed{
TaskAlignmentGap
}
\]

所以优先：

> SFT。

---

# 八、核心心智模型 ③：如果问题只发生在一个任务上，先怀疑 Behavior；如果多个任务都受影响，才更像 Domain Foundation 问题

假设：

```text
风险分类
表现差

但：
摘要正常
术语解释正常
文件理解正常
问答正常
```

那不一定需要 CPT。

可能只是：

> 风险分类任务本身没有对齐好。

反过来，如果：

```text
风险识别差
文件问答差
术语理解差
长文档摘要也差
```

多个任务共同受影响，

就更像：

> 共享领域表示不足。

所以：

\[
\boxed{
SingleTaskFailure
优先检查
BehaviorGap
}
\]

\[
\boxed{
CrossTaskFailure
更值得检查
DomainGap
}
\]

---

# 九、什么问题其实既不该 CPT，也不该 SFT？

非常重要。

如果用户问：

```text
2026年最新采购政策是什么？
```

而模型不知道，

这更像：

# Knowledge Freshness Gap
## 知识新鲜度差距

应该优先：

\[
\boxed{
RAG / Tool
}
\]

不是把最新政策重新写进 Weight。

---

如果问题是：

```text
需要读取项目当前预算
需要查实时供应商信息
需要提交审批
```

这更像：

# Tool / Workflow Gap
## 工具或工作流差距

应该优先：

\[
\boxed{
Agent / Tool Calling
}
\]

所以：

\[
\boxed{
NotEveryError
NeedsWeightUpdate
}
\]

---

# 十、完整技术路线诊断流程

英文流程：

```text
Observe Failure
↓
Classify Failure
↓
Domain Gap?
↓
Behavior Gap?
↓
Fresh Knowledge Gap?
↓
Execution Gap?
↓
Select Intervention
↓
Run Controlled Experiment
↓
Evaluate
↓
Promote / Reject
```

中文解释：

```text
观察真实失败案例
↓
给错误分类
↓
判断是不是领域理解不足
↓
判断是不是任务行为不对
↓
判断是不是外部知识过期
↓
判断是不是工具执行链问题
↓
选择CPT / SFT / RAG / Agent
↓
做受控实验
↓
分别评测能力变化
↓
决定升级还是否决
```

所以：

\[
\boxed{
Intervention
必须匹配
FailureType
}
\]

---

# 十一、真实训练顺序为什么通常是 Base → CPT → SFT？

经典路线：

```text
Base Model
基础模型
↓
CPT
学习领域分布
↓
Domain-adapted Base
领域适配底座
↓
SFT
学习任务行为
↓
Task Model
任务模型
```

也就是：

\[
\boxed{
Base
\rightarrow
CPT
\rightarrow
SFT
}
\]

为什么？

因为 CPT 先塑造：

> 模型“懂什么样的语言世界”。

SFT 再塑造：

> 模型“应该怎样完成任务”。

---

# 十二、核心心智模型 ④：CPT 先学“世界”，SFT 再学“行为”

可以压成一句：

\[
\boxed{
CPT
=
WorldModeling
}
\]

\[
\boxed{
SFT
=
BehaviorShaping
}
\]

这里的 World Modeling 不是说模型真的构建完整世界模型，

而是强调：

> CPT 更偏向学习领域文本分布和表示结构。

SFT 更偏向：

> 把已有能力导向指定任务行为。

---

# 十三、为什么 SFT → CPT 可能破坏对齐？

假设你已经有：

```text
ProcurementLM_V0.1
```

它经过 SFT 后会：

```text
遵守JSON Schema
按任务格式回答
保持拒答边界
```

如果这时直接做大量 CPT，

训练目标重新变成：

> 全文 Next Token Prediction。

模型可能逐渐弱化：

```text
Instruction Following
Chat格式
Schema遵循
任务对齐
```

所以：

\[
\boxed{
SFT
\rightarrow
LargeCPT
可能导致
BehaviorRegression
}
\]

---

# 十四、那已经有 SFT 模型了怎么办？

这正是我们当前项目的现实情况。

我们已经有：

```text
ProcurementLM_V0.1
```

如果现在决定 CPT，

更稳的工程路线通常是：

```text
回到Base Model
↓
做CPT
↓
得到Domain-adapted Base
↓
重新做SFT
↓
得到ProcurementLM_V0.2
```

即：

\[
\boxed{
Base
\rightarrow
CPT
\rightarrow
SFT
\rightarrow
V0.2
}
\]

而不是：

\[
\boxed{
V0.1
\rightarrow
直接CPT
\rightarrow
结束
}
\]

---

# 十五、核心心智模型 ⑤：课程顺序不是最终训练图谱

我们先学过 SFT，

现在才学 CPT。

但这只是：

> 教学顺序。

真实工程 DAG 可能是：

```text
Base
├─ CPT
│   └─ Domain Base
│       └─ SFT
│           └─ ProcurementLM_V0.2
│
└─ 原有SFT实验
    └─ ProcurementLM_V0.1
```

所以：

\[
\boxed{
CourseOrder
\neq
ProductionTrainingGraph
}
\]

这条在第 1 阶段提过，

现在正式进入技术路线决策。

---

# 十六、CPT 后 SFT，SFT 数据还可以继续用原来的么？

通常可以：

> 但必须重新做兼容性和分布检查。

因为 CPT 后模型的：

```text
领域表示
Token概率分布
可能的Tokenizer
Embedding
```

都可能变化。

所以应该重新验证：

```text
SFT Dataset Version
Tokenizer Compatibility
Prompt Template
Loss Mask
Max Length
Evaluation Baseline
```

不能简单：

> “旧 SFT 脚本原样跑。”

---

# 十七、Adapter Compatibility：LoRA 能不能直接从旧模型搬过去？

如果旧的 LoRA 是在：

```text
BaseModel_A
```

上训练的。

CPT 后得到：

```text
BaseModel_A_CPT
```

即使模型结构相同，

参数底座已经变化。

所以旧 Adapter：

> 可能还能加载。

但这不等于：

> 行为一定仍然正确。

所以：

\[
\boxed{
Loadable
\neq
Compatible
}
\]

真正应该：

```text
重新评测

最好重新SFT / 重新训练Adapter
```

---

# 十八、核心心智模型 ⑥：Checkpoint Compatibility 和 Behavioral Compatibility 是两回事

一个 Adapter：

```text
shape对得上
可以load
不报错
```

只能说明：

# Structural Compatibility
## 结构兼容

不能说明：

# Behavioral Compatibility
## 行为兼容

所以：

\[
\boxed{
StructuralCompatibility
\neq
BehavioralCompatibility
}
\]

这条对 LoRA、Tokenizer、Checkpoint 组合都成立。

---

# 十九、CPT 和 SFT 应该怎样分层评测？

CPT 后先测：

```text
Domain Perplexity
领域困惑度

Domain Probes
领域理解探针

General Regression
通用能力回归

Long Context
长文档能力
```

这是：

# Foundation Evaluation
## 底座能力评测

然后 SFT 后再测：

```text
Instruction Following
指令遵循

Task Accuracy
任务正确率

Schema Compliance
结构化输出

Abstention
拒答与不确定性

Procurement Workflow Tasks
采购业务任务
```

这是：

# Behavior Evaluation
## 行为评测

所以：

\[
\boxed{
CPTEval
\neq
SFTEval
}
\]

---

# 二十、核心心智模型 ⑦：不要用下游任务分数替代 CPT 诊断，也不要用 Perplexity 替代 SFT 诊断

如果 CPT 后：

```text
PPL下降
```

只能说明：

> 语言建模改善。

不能自动说明：

> 风险识别一定更好。

如果 SFT 后：

```text
任务F1提高
```

也不能自动说明：

> 模型领域底座更强。

所以：

\[
\boxed{
FoundationMetric
\neq
BehaviorMetric
}
\]

两层必须分开。

---

# 二十一、Decision Matrix：到底该选 CPT、SFT、RAG 还是 Agent？

可以建立第一版决策矩阵：

| 现象 | 更可能的问题 | 优先技术 |
|---|---|---|
| 多个采购任务都不懂领域术语 | Domain Gap | CPT |
| 只是不按格式输出 | Behavior Gap | SFT |
| 不知道最新政策 | Fresh Knowledge Gap | RAG |
| 不会调用系统完成任务 | Execution Gap | Agent |
| 长采购文件结构理解弱 | Domain / Context Gap | CPT + Context策略 |
| 会理解但分类标签不稳定 | Behavior Gap | SFT |
| 会回答但引用旧规则 | Freshness / Evidence Gap | RAG |
| 工具会调用但流程混乱 | Workflow Control Gap | Agent |

这张表非常重要。

因为：

\[
\boxed{
BestTechnique
取决于
FailureLayer
}
\]

---

# 二十二、Go / No-Go Gate：什么时候允许进入 CPT？

进入 CPT 前至少确认：

```text
跨任务Domain Gap存在

高质量无标注领域语料足够

RAG / SFT不能更低成本解决

Benchmark已隔离

Forgetting Eval已准备

Retention机制已准备
```

如果不满足：

> 不应该直接开始大规模 CPT。

所以：

\[
\boxed{
CPT
需要
GoNoGoGate
}
\]

---

# 二十三、什么时候允许进入 SFT？

SFT 前至少确认：

```text
任务定义稳定

输入输出Schema明确

Gold / High-quality Target存在

评价指标明确

Prompt / Template版本锁定

错误主要属于Behavior Gap
```

否则：

> 可能在用监督数据“硬教”一个本来没定义清楚的任务。

---

# 二十四、Ablation：怎样证明 CPT 真的值得？

至少可以比较三组：

```text
A
Base → SFT

B
Base → CPT → SFT

C
Base → CPT
```

然后分别比较：

```text
Domain Foundation Metrics
领域底座能力

Task Metrics
任务能力

General Regression
通用回归

Training Cost
训练成本
```

如果：

```text
B 相比 A
没有明显收益
```

那就要认真质疑：

> CPT 是否真的值得。

所以：

\[
\boxed{
CPTValue
需要
ControlledComparison
}
\]

---

# 二十五、核心心智模型 ⑧：技术路线的目标不是“把所有方法都用上”，而是最小充分干预

这条非常重要。

工程上不是：

```text
CPT
+
SFT
+
RAG
+
Agent
全上
```

就一定最好。

而是：

\[
\boxed{
UseMinimumSufficientIntervention
}
\]

中文：

> **用最小但足够的技术干预解决当前错误。**

因为每加一层：

```text
成本增加
版本复杂度增加
评测复杂度增加
失败模式增加
维护负担增加
```

所以：

\[
\boxed{
MoreTech
\neq
BetterSystem
}
\]

---

# 二十六、把 CPT、SFT、RAG、Agent 压成一张能力边界图

```text
                    Observed Failure
                       观察到失败
                           │
                           ▼
                     Error Diagnosis
                        错误诊断
                           │
          ┌────────────────┼────────────────┬────────────────┐
          ▼                ▼                ▼                ▼
      Domain Gap      Behavior Gap    Knowledge Gap     Execution Gap
      领域分布差距      任务行为差距      外部知识差距      执行流程差距
          │                │                │                │
          ▼                ▼                ▼                ▼
         CPT              SFT              RAG             Agent
    学领域底座        学任务行为        补当前证据        完成真实流程
          │                │                │                │
          └────────────────┼────────────────┴────────────────┘
                           ▼
                    Controlled Eval
                       受控评测
                           │
                           ▼
                     Release Decision
                       发布决策
```

这张图必须成为后面所有模型升级决策的基础。

---

# 二十七、本阶段正式工程产物：`ProcurementCPTSFTDecisionPolicy_V0.1`

第一版至少锁定：

```text
decision_policy_version

failure_taxonomy

domain_gap_definition

behavior_gap_definition

knowledge_gap_definition

execution_gap_definition

cpt_go_no_go

sft_go_no_go

rag_preferred_conditions

agent_preferred_conditions

training_order

base_model_version

cpt_checkpoint

sft_dataset_version

sft_config_version

adapter_compatibility_check

tokenizer_compatibility_check

foundation_eval_suite

behavior_eval_suite

general_regression_suite

ablation_plan

minimum_sufficient_intervention

release_gate

trace_logging
=
enabled
```

每次技术路线决策至少记录：

```text
issue_id

observed_failure

failure_layer

evidence

candidate_interventions

selected_intervention

reason

experiment_id

before_metrics

after_metrics

cost

regression

final_decision
```

这样以后才能回答：

> **为什么这个问题选择 CPT，而不是 SFT / RAG / Agent？**

---

# 二十八、本阶段最重要的 8 个核心心智模型

> **心智模型 ①：`DomainGap ≠ BehaviorGap`。不懂领域和不会按要求做任务，是两个不同问题。**

> **心智模型 ②：`TrainingChoice 必须由 ErrorDiagnosis 驱动`。先判断错误发生在哪一层，再决定 CPT、SFT、RAG 或 Agent。**

> **心智模型 ③：`DomainCompetence ≠ InstructionBehavior`。领域底座能力和任务行为能力必须分层看。**

> **心智模型 ④：`CPT = WorldModeling，SFT = BehaviorShaping`。CPT 主要塑造领域表示，SFT 主要塑造任务行为。**

> **心智模型 ⑤：`CourseOrder ≠ ProductionTrainingGraph`。课程先学 SFT 后学 CPT，不代表真实训练顺序就应该如此。**

> **心智模型 ⑥：`StructuralCompatibility ≠ BehavioralCompatibility`。Checkpoint 或 Adapter 能加载，不代表行为一定兼容。**

> **心智模型 ⑦：`FoundationMetric ≠ BehaviorMetric`。CPT 与 SFT 的评测必须分层，不能用一个指标替代另一个。**

> **心智模型 ⑧：`MoreTech ≠ BetterSystem`。真正专业的系统优先采用最小但足够的干预，而不是把所有技术都堆上去。**

---

# 二十九、把完整 CPT / SFT 决策流程压成一张专业工程图

```text
                      Real Failure Cases
                        真实失败案例
                              │
                              ▼
                       Error Taxonomy
                        错误类型归因
                              │
          ┌───────────────────┼───────────────────┬───────────────────┐
          ▼                   ▼                   ▼                   ▼
      Domain Gap         Behavior Gap       Knowledge Gap        Execution Gap
       领域差距             行为差距            知识差距              执行差距
          │                   │                   │                   │
          ▼                   ▼                   ▼                   ▼
         CPT                 SFT                 RAG                Agent
          │                   │                   │                   │
          └───────────────────┼───────────────────┴───────────────────┘
                              ▼
                     Controlled Experiment
                         受控对比实验
                              │
                              ▼
               Foundation + Behavior Evaluation
                  底座能力 + 行为能力评测
                              │
                              ▼
                    General Regression Check
                       通用能力回归检查
                              │
                              ▼
                  Cost / Benefit / Complexity
                     成本收益与复杂度分析
                              │
                              ▼
                 Minimum Sufficient Intervention
                       最小充分技术干预
                              │
                              ▼
                        Release Gate
```

脑中最后只留一句：

> **CPT 和 SFT 的专业区别，不是“无监督训练”和“有监督训练”这么简单，而是先判断模型缺的是领域分布能力还是任务行为能力，再用最小充分干预解决对应问题，并把底座能力、任务行为、通用回归和训练成本分层评测。**

---

# 第八课 · 第 9 阶段掌握测试

现在不回看正文，你应该能够解释：Domain Gap 和 Behavior Gap 为什么不是一回事；CPT 和 SFT 分别在学习什么；为什么单任务失败更优先检查 Behavior，而跨任务共同失败更值得怀疑 Domain Foundation；为什么最新政策问题优先是 RAG 而不是 Weight Update；为什么工具执行问题优先属于 Agent；为什么真实训练顺序通常是 `Base → CPT → SFT`；为什么 `SFT → Large CPT` 可能破坏对齐；已经有 SFT 模型时为什么更稳的做法通常是回到 Base 做 CPT 后重新 SFT；为什么 Course Order 不等于 Production Training Graph；LoRA Adapter 能加载为什么不代表行为兼容；CPT 和 SFT 应该分别评什么；为什么 Foundation Metric 和 Behavior Metric 不能混；什么时候 CPT 应该被 Go / No-Go Gate 拦住；怎样用 Ablation 证明 CPT 是否真的值得；以及为什么真正专业的路线是 Minimum Sufficient Intervention，而不是把 CPT、SFT、RAG、Agent 全部堆上去。

如果这些能够完整讲出来：

\[
\boxed{
第八课第9阶段真正掌握
}
\]

---

# 下一阶段：第八课 · 第 10 阶段
# 真正训练 `ProcurementLM_V0.2`：端到端 CPT、评测、回归测试与 Release Gate
## 怎样把前 9 个阶段全部接成一个真正可运行、可复现、可审计、可回滚的 CPT 工程系统？

下一阶段会正式把：

```text
Domain Gap Diagnosis
领域差距诊断

Corpus Governance
语料治理

Tokenizer Audit
分词器审计

Sequence Construction
训练序列构造

Data Mixture
数据混合

Forgetting Evaluation
遗忘评测

Retention
能力保持

Synthetic Data
合成数据

Curriculum
课程式训练

CPT → SFT
训练链路

Release Gate
发布门槛
```

全部连接起来。

最终形成：

# `ProcurementLM_V0.2`

并把第八课正式闭环。

下一阶段最重要的总原则会是：

\[
\boxed{
CPTExperiment
\neq
ModelRelease
}
\]

也就是说：

> **训练跑完，只代表得到一个实验 Checkpoint；只有通过完整评测、回归、版本、可复现和 Release Gate，才算真正得到可发布的 `ProcurementLM_V0.2`。**

---
