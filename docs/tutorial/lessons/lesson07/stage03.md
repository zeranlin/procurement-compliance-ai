# 第七课 · 第 3 阶段
# Structured Output：JSON Schema、Validation 与可靠参数生成
## 模型输出“看起来像 JSON”为什么还不够？怎样让 Tool Arguments 真正可执行？

<!-- PEDAGOGY_CN_ENHANCEMENT_V2 START -->
## V2 增强阅读导航：先抓主干，再看细节
> **本阶段修复级别：LIGHT。** 审计原因：英文工程术语/代码表达较多，中文释义不足。  
> 原正文完整保留；新增这一层的目的，是把“要长期记住的判断框架”提前，把大量编号内容降为展开、案例、反例和工程参考。

### A. 本阶段核心心智模型（前置）
1. **第一，Structured Output 的目标不是让模型输出“像 JSON 的文本”，而是得到 Parseable + SchemaValid + SemanticallyValid + PolicyValid 的可执行参数。**
2. **第二，合法 JSON 只解决语法层；JSON Schema 继续约束 Required、Type、Enum、Nested Object、Array 和是否允许额外字段，但 Schema 正确仍不代表业务语义正确。**
3. **第三，Semantic Validation 必须检查日期先后、金额范围、字段依赖、互斥条件和标识符一致性；Policy Validation 再决定这个结构化动作是否被授权。**
4. **第四，Constrained Generation 可以减少格式错误，但不能保证模型选对业务值；ConstrainedSyntax ≠ CorrectSemantics。**
5. **第五，Validation 失败后可以 Repair、Retry 或 Reject，但 Repair 只能用于确定性、无歧义的格式修复，绝不能为了让 Schema 通过而偷偷猜测缺失业务信息。**

### B. 中文释义增强：本阶段重要英文工程术语

| 英文工程表达 | 中文工程 / 业务含义 |
|---|---|
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `Validation` | 验证集：开发阶段用于选模型、调参数和早停 |
| `Structured Output` | 结构化输出：按照固定字段和枚举生成可校验结果 |
| `JSON Schema` | JSON Schema：约束工具输入输出字段和类型 |
| `Query` | Query/Q：当前 Token 表示“我要找什么”的向量 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |

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

第 2 阶段我们已经得到：

\[
Model
\rightarrow
ToolCall
\rightarrow
Runtime
\rightarrow
ToolResult
\]

其中最脆弱的一段就是：

\[
\boxed{
Model
\rightarrow
ToolArguments
}
\]

因为 LLM 天生擅长的是：

> **生成自然语言 Token。**

而 Runtime 真正需要的是：

> **稳定、可解析、可验证、可执行的数据结构。**

例如模型生成：

```text
{
  query: 查一下本地机构,
  jurisdiction: 广东,
}
```

人一眼能看懂。

但它可能同时存在：

```text
不是合法JSON
字段名不符合Schema
地区值不符合系统枚举
缺少必填字段
日期格式不合法
语义条件互相冲突
```

所以本阶段正式解决：

# Structured Output
## 结构化输出

本阶段最终形成：

# `ProcurementStructuredOutputPolicy_V0.1`

---

# 一、先锁死本阶段最重要的一句话

“能被人看懂”不是系统要求。

真正要求是：

\[
\boxed{
Parseable
+
SchemaValid
+
SemanticallyValid
+
PolicyValid
}
\]

也就是四层：

```text
1. 能不能解析？
2. 结构对不对？
3. 值在业务上合理吗？
4. 这个动作是否允许？
```

因此：

\[
\boxed{
LooksLikeJSON
\neq
ExecutableArguments
}
\]

---

# 二、第一层：Syntax Validity——它首先必须真的是合法 JSON

合法 JSON 至少要求：

```text
字符串使用双引号
没有多余尾逗号
对象和数组括号正确
布尔值是 true / false
null 使用标准写法
键名和字符串正确转义
```

例如：

```json
{
  "query": "投标前本地机构限制",
  "jurisdiction": "广东省"
}
```

这是合法 JSON。

而：

```text
{
  query: '投标前本地机构限制',
  jurisdiction: 广东省,
}
```

看起来像 JSON，

但严格来说：

> **不是合法 JSON。**

因此第一道门是：

# Parser
## 语法解析器

---

# 三、第二层：Schema Validity——合法 JSON 也可能完全不能用

假设工具定义要求：

```json
{
  "query": "string",
  "jurisdiction": "string",
  "query_time": "YYYY-MM-DD"
}
```

模型输出：

```json
{
  "query": "本地机构限制"
}
```

它是合法 JSON。

但缺少：

```text
jurisdiction
query_time
```

如果这两个字段是必填，

它仍然不能执行。

所以：

\[
\boxed{
ValidJSON
\neq
ValidSchema
}
\]

---

# 四、JSON Schema 到底解决什么？

JSON Schema 可以把“参数应该长什么样”写成机器可验证规则。

概念上：

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string"
    },
    "jurisdiction": {
      "type": "string"
    },
    "query_time": {
      "type": "string"
    }
  },
  "required": [
    "query",
    "jurisdiction",
    "query_time"
  ]
}
```

它告诉 Runtime：

```text
顶层必须是object
query必须是string
jurisdiction必须是string
query_time必须是string
三个字段都必须存在
```

所以：

\[
\boxed{
Schema
=
MachineCheckableContract
}
\]

---

# 五、Required Field：缺字段和字段为空不是一回事

假设：

```text
jurisdiction
```

是必填字段。

这两个情况不一样：

### 情况 A：字段不存在

```json
{
  "query": "本地机构限制"
}
```

### 情况 B：字段存在，但值为空

```json
{
  "query": "本地机构限制",
  "jurisdiction": null
}
```

系统必须提前定义：

> `null` 是否允许。

因此：

\[
\boxed{
Required
\neq
NonNull
}
\]

很多 Agent Bug 就出在这里。

---

# 六、Type Constraint：类型不能靠猜

工具需要：

```text
max_results = integer
```

模型却可能输出：

```json
{
  "max_results": "10"
}
```

这里 `"10"` 是字符串，

不是整数。

有些 Runtime 会自动转成：

```text
10
```

但这种自动类型转换必须非常谨慎。

因为：

```text
"00123"
```

可能是：

> 项目编号的一部分，

而不是数字 123。

所以：

\[
\boxed{
SilentTypeCoercion
可能破坏业务语义
}
\]

高风险字段最好严格校验。

---

# 七、Enum：为什么受控字段不要让模型自由发挥？

假设采购阶段只能是：

```text
pre_bid
evaluation
award
contract
acceptance
```

如果让模型自由生成，

它可能输出：

```text
投标前阶段
招标前
前置阶段
before_bid
```

人能理解，

程序却很难稳定路由。

所以应使用：

# Enum
## 枚举

概念上：

```json
{
  "procurement_stage": {
    "type": "string",
    "enum": [
      "pre_bid",
      "evaluation",
      "award",
      "contract",
      "acceptance"
    ]
  }
}
```

这样输出空间从：

> 无限自然语言

收缩为：

> **有限合法状态集合。**

---

# 八、additionalProperties：为什么“多生成几个字段”也可能是问题？

假设 Schema 只允许：

```text
query
jurisdiction
query_time
```

模型却生成：

```json
{
  "query": "本地机构限制",
  "jurisdiction": "广东省",
  "query_time": "2026-09-17",
  "legal_conclusion": "违法"
}
```

这里：

```text
legal_conclusion
```

可能根本不应该出现在 Tool Arguments。

更危险的是：

> 模型提前把结论注入检索请求。

所以很多高可靠场景应该考虑：

```text
additionalProperties = false
```

核心思想：

\[
\boxed{
只允许Contract定义过的字段
}
\]

---

# 九、Nested Object 和 Array：真实参数往往不是扁平字典

政府采购工具可能需要：

```json
{
  "query": "资格条件审查",
  "filters": {
    "jurisdiction": "广东省",
    "valid_at": "2026-09-17"
  },
  "document_types": [
    "law",
    "regulation",
    "policy"
  ]
}
```

这里包含：

```text
Nested Object
嵌套对象

Array
数组
```

复杂 Schema 的问题是：

> 约束更精确，

但模型生成难度也会上升。

所以设计原则不是：

> Schema 越复杂越专业。

而是：

\[
\boxed{
最小必要结构
}
\]

只保留真正影响执行的字段。

---

# 十、第三层：Semantic Validation——Schema 对了，业务含义仍然可能错

这是 Structured Output 最容易被低估的一层。

例如：

```json
{
  "effective_from": "2026-12-31",
  "effective_to": "2026-01-01"
}
```

两个字段都是合法日期字符串。

Schema 也完全通过。

但业务上：

\[
effective\_from
>
effective\_to
\]

显然矛盾。

再比如：

```json
{
  "min_amount": 1000000,
  "max_amount": 100000
}
```

类型都正确。

但范围不合理。

因此：

\[
\boxed{
SchemaValid
\neq
SemanticallyValid
}
\]

这就需要：

# Business Validator
## 业务语义校验器

---

# 十一、Semantic Validation 应该校验哪些东西？

政府采购 Tool Arguments 至少可能需要检查：

```text
时间先后关系
金额上下限
辖区层级关系
文号格式
项目编号格式
采购阶段是否冲突
版本状态是否冲突
字段之间的依赖关系
互斥字段是否同时出现
```

例如：

```text
如果 historical_query = true
那么 query_time 必须存在
```

或者：

```text
如果 action = publish_notice
那么 approval_id 必须存在
```

这类规则：

> 不是 JSON Schema 的简单类型检查就能完全解决的。

---

# 十二、第四层：Policy Validation——结构和语义都正确，也不代表允许执行

假设模型输出：

```json
{
  "action": "publish_notice",
  "project_id": "P_001",
  "content": "..."
}
```

它可能：

```text
语法正确
Schema正确
业务字段正确
```

但用户当前权限只是：

```text
read_only
```

那仍然必须拒绝。

所以完整校验链应该是：

\[
\boxed{
Syntax
\rightarrow
Schema
\rightarrow
Semantics
\rightarrow
Policy
}
\]

而不是：

> JSON 能 parse 就直接执行。

---

# 十三、Constrained Generation：能不能让模型一开始就少犯格式错误？

可以。

一个重要思路是：

# Constrained Generation
## 受约束生成

也就是：

> 在模型生成过程中，限制它只能生成符合某种结构的输出。

概念上：

```text
普通生成：
任意Token都可能出现

受约束生成：
只允许当前Schema状态下合法的Token
```

这样可以大幅减少：

```text
括号不闭合
字段名乱写
非法枚举值
多余自然语言
```

但必须注意：

\[
\boxed{
ConstrainedSyntax
\neq
CorrectSemantics
}
\]

模型即使只能输出合法 JSON，

仍然可能选错：

```text
jurisdiction
date
project_id
tool
```

---

# 十四、Validation 失败以后：Repair、Retry、Reject 三种策略

假设第一次输出：

```json
{
  "query": "本地机构限制",
  "query_time": "明年"
}
```

Schema 要求：

```text
YYYY-MM-DD
```

系统有三种典型处理方式。

## 1. Repair
### 修复

对于非常确定的格式问题，

Runtime 可以做安全修复。

例如：

```text
去除多余空格
标准化大小写
```

但不能擅自把：

```text
明年
```

猜成：

```text
2027-01-01
```

因为这已经是：

> 语义推断。

---

## 2. Retry
### 重试生成

把 Validation Error 返回模型：

```text
query_time必须为YYYY-MM-DD
```

让模型重新生成。

---

## 3. Reject
### 拒绝执行

如果问题高风险或无法安全修复：

> 不执行 Tool。

所以：

\[
\boxed{
Repair
只适合确定性、无歧义修复
}
\]

---

# 十五、不要“自动补全”模型没有依据的信息

这是政府采购 Agent 非常重要的规则。

用户没有提供：

```text
jurisdiction
```

模型却输出：

```json
{
  "jurisdiction": "广东省"
}
```

如果上下文根本没有广东省，

即使 Schema 完全合法，

这仍然是：

# Hallucinated Argument
## 幻觉参数

所以参数来源最好区分：

```text
user_provided
context_derived
tool_derived
system_default
model_inferred
unknown
```

对于高风险字段：

\[
\boxed{
Unknown
优于
InventedValue
}
\]

---

# 十六、Canonicalization：为什么同一个值最好只有一种标准表示？

例如地区可能出现：

```text
广东
广东省
Guangdong
CN-GD
```

如果下游数据库使用：

```text
CN-GD
```

就需要：

# Canonicalization
## 标准化表示

例如：

```json
{
  "jurisdiction_raw": "广东省",
  "jurisdiction_code": "CN-GD"
}
```

同理：

```text
日期
金额
文号
机构名称
项目编号
```

也可以分别设计标准格式。

这样下游 Tool 才不会每个模块各自猜。

---

# 十七、Schema Version：参数协议本身也必须版本化

今天工具参数可能是：

```json
{
  "query": "...",
  "jurisdiction": "..."
}
```

未来可能改成：

```json
{
  "query": "...",
  "jurisdiction_code": "...",
  "query_time": "...",
  "document_types": []
}
```

这意味着：

> Tool Contract 变了。

所以应该记录：

```text
schema_version
```

例如：

```text
search_regulation@v1
search_regulation@v2
```

否则旧 Agent 和新 Runtime 混用时：

> 很难定位兼容性问题。

---

# 十八、Structured Output 的错误分类

至少要拆成：

```text
1. Syntax Error
不是合法JSON

2. Missing Field Error
缺少必填字段

3. Type Error
字段类型错误

4. Enum Error
输出非法枚举值

5. Extra Field Error
生成Schema外字段

6. Semantic Conflict
字段之间业务矛盾

7. Hallucinated Argument
生成上下文中不存在的关键值

8. Canonicalization Error
标准编码映射错误

9. Policy Violation
结构正确但动作不允许

10. Repair Error
自动修复反而改变原意
```

所以：

> Structured Output Accuracy

不能只统计：

```text
JSON parse成功率
```

---

# 十九、应该怎样评测 Structured Output？

第一版至少可以记录：

```text
json_parse_rate

schema_valid_rate

required_field_accuracy

type_accuracy

enum_accuracy

semantic_valid_rate

identifier_preservation_rate

hallucinated_argument_rate

policy_violation_rate

retry_success_rate

repair_success_rate

tool_execution_success_rate
```

其中最关键的一点是：

\[
\boxed{
ExecutionSuccess
比
PrettyJSON
更重要
}
\]

最终目的是：

> Tool 真能正确执行。

---

# 二十、政府采购案例：资格条件审查 Tool

假设 Tool：

```text
analyze_qualification_requirement
```

Schema：

```json
{
  "requirement_text": "string",
  "procurement_stage": "pre_bid | evaluation | award | contract",
  "jurisdiction_code": "string",
  "query_time": "YYYY-MM-DD",
  "evidence_ids": ["string"]
}
```

模型输出：

```json
{
  "requirement_text": "供应商投标前须在本市设立办事机构",
  "procurement_stage": "pre_bid",
  "jurisdiction_code": "CN-GD",
  "query_time": "2026-09-17",
  "evidence_ids": ["E1", "E3"]
}
```

Runtime 应依次检查：

```text
JSON Parse
↓
Schema Validation
↓
Evidence ID存在性
↓
Jurisdiction Code合法性
↓
Date合法性
↓
Policy Check
↓
Execute
```

而不是：

> 一 parse 成功就直接跑。

---

# 二十一、本阶段工程产物：`ProcurementStructuredOutputPolicy_V0.1`

第一版至少锁定：

```text
output_format
=
json

schema_id
schema_version

required_fields

field_types

enum_constraints

nullable_fields

additional_properties_policy

nested_object_policy

array_policy

identifier_preservation_policy

canonicalization_policy

semantic_validation_rules

policy_validation_enabled
=
true

repair_policy

retry_policy

max_retry_count

reject_policy

validation_error_schema

trace_logging
=
enabled
```

同时每次调用最好记录：

```text
raw_model_output

parsed_object

schema_validation_result

semantic_validation_result

policy_validation_result

repair_applied

retry_count

final_arguments

execution_result
```

这样 Structured Output 出错时才能完整重放。

---

# 二十二、把本阶段压成最精准的 6 句话

> **第一，Structured Output 的目标不是让模型输出“像 JSON 的文本”，而是得到 `Parseable + SchemaValid + SemanticallyValid + PolicyValid` 的可执行参数。**

> **第二，合法 JSON 只解决语法层；JSON Schema 继续约束 Required、Type、Enum、Nested Object、Array 和是否允许额外字段，但 Schema 正确仍不代表业务语义正确。**

> **第三，Semantic Validation 必须检查日期先后、金额范围、字段依赖、互斥条件和标识符一致性；Policy Validation 再决定这个结构化动作是否被授权。**

> **第四，Constrained Generation 可以减少格式错误，但不能保证模型选对业务值；`ConstrainedSyntax ≠ CorrectSemantics`。**

> **第五，Validation 失败后可以 Repair、Retry 或 Reject，但 Repair 只能用于确定性、无歧义的格式修复，绝不能为了让 Schema 通过而偷偷猜测缺失业务信息。**

> **第六，Structured Output 最终要看 Tool Execution Success，而不是 JSON 看起来多漂亮；参数协议本身还必须版本化、可追踪、可重放。**

---

# 本阶段最核心的一张图

```text
                       Model Output
                            │
                            ▼
                       JSON Parser
                            │
                      Parseable?
                            │
                            ▼
                    Schema Validation
                            │
                Required / Type / Enum
                            │
                            ▼
                  Semantic Validation
                            │
          Date / Amount / Dependency / ID
                            │
                            ▼
                    Policy Validation
                            │
                  Allowed to Execute?
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
              Reject                 Execute
                                        │
                                        ▼
                                   Tool Runtime
```

脑中最后只留一句：

> **结构化输出真正解决的不是“让模型会写 JSON”，而是建立一条从模型生成到程序执行之间可验证、可拒绝、可重试、不会偷偷猜值的数据契约。**

---

# 第七课 · 第 3 阶段掌握测试

现在不回看正文，你应该能够解释：为什么合法 JSON 不等于合法 Tool Arguments；JSON Schema 解决什么问题；Required 和 NonNull 为什么不是一回事；为什么类型自动转换可能破坏项目编号等业务语义；Enum 为什么能提高稳定性；为什么要限制额外字段；复杂 Nested Schema 为什么不能无限堆；Schema Valid 为什么仍不等于 Semantically Valid；Semantic Validation 需要检查哪些业务关系；为什么 Policy Validation 必须独立存在；Constrained Generation 能解决什么、不能解决什么；Repair、Retry、Reject 应该怎样选择；什么是 Hallucinated Argument；为什么 Canonicalization 和 Schema Version 都很重要；以及为什么最终指标应该落到 Tool Execution Success。

如果这些能够完整讲出来：

\[
\boxed{
第七课第3阶段真正掌握
}
\]

---

# 下一阶段：第七课 · 第 4 阶段
# Tool Registry 与 Capability Boundary：模型到底允许调用什么？
## 工具越多越好吗？为什么“能调用什么”本身就是 Agent 的能力边界和安全边界？

第 3 阶段我们已经把单个 Tool Call 的参数变成：

\[
\boxed{
可解析
+
可验证
+
可执行
}
\]

下一阶段要解决的是：

> **系统里如果有几十、几百个工具，模型到底应该看到哪些？谁能调用？什么条件下能调用？哪些 Tool 根本不应该暴露给当前 Agent？**

我们会正式进入：

```text
Tool Registry
Capability
Tool Discovery
Tool Namespace
Least Privilege
Read / Write Boundary
Permission Scope
Approval Boundary
Tool Visibility
Capability Token
Audit
```

并建立：

# `ProcurementToolRegistryPolicy_V0.1`

这会把 Agent 从：

> “会调用一个函数”

推进到：

> **拥有清楚、受控、最小权限的工具能力空间。**



---
