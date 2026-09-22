# BR-C1-01 业务裁决日志 V0.1

**文档标识**：`BR_C1_01_Decision_Log_V0.1`  
**状态**：`FROZEN`（规范性业务增补）  
**生效日期**：2026-09-22  
**责任方**：业务组／产品组  
**任务**：`C1-01_LOCAL_ENTRY_PRECONDITION`  
**关联裁决**：`BR-C101-DEC-03`（强制承诺中标后设本地售后服务机构属于 `OTHER_RELATED`）

## 1. 本轮正式裁决

### `BR-C101-DEC-04`：`ParseFailure != NeedsContext`

本裁决是 `BR_C1_01_Business_Task_Spec_V0.1` 与 `C1_01_Label_Guide_V0.1` 的**冻结增补**，属于后续 Dataset Schema、数据准入、Baseline 和 Blind Test 管理的规范性输入。

```text
NEEDS_CONTEXT
= 原文已经可靠读取，但业务判断所需信息不足

REWORK_SOURCE / PARSE_FAILURE
= 输入本身不可靠，当前不能形成正式业务标签
```

`Missing Business Context != Broken Source`。两者都可能表现为“当前不能完成最终判断”，但处理对象不同：前者补业务材料后继续标注，后者先修复来源或解析质量，修复前不得形成正式标签。

## 2. 可执行边界

### 2.1 `NEEDS_CONTEXT`

只有在以下条件同时满足时才可使用：

1. 原文、表格关系和引用定位已可靠读取，`parser_quality=PASS` 或等价的可用状态；
2. 当前 Requirement 可以独立重建，未丢失主体、条件或竞争后果的关键文字；
3. 缺少的是业务判断事实，例如术语定义、被引用的资格条款、评分后果、例外适用材料；
4. 补充该事实后，标签可能在 `MATCH`、`NO_MATCH`、`NEEDS_CONTEXT` 之间改变。

输出为正式 `NEEDS_CONTEXT/NONE`，必须列出可执行的 `missing_context_questions`、补件来源和复核责任方；数据资格可进入普通 Missing Context 候选，但仍须经过来源、复核和数据 QA 闸门。

### 2.2 `REWORK_SOURCE / PARSE_FAILURE`

出现以下任一情形时，必须走 `REWORK_SOURCE`：

- OCR 看不清核心数字、主体、否决／评分关系或关键限定词；
- 扫描件、PDF 页、附件、引用页或更正公告缺失，导致原文不能可靠恢复；
- 表格行列关系错乱，无法确认要求的主体、条件与分值／后果归属；
- 文本片段被截断、乱码或版面解析错误，不能形成可独立判断的 Requirement。

此时可以保留采集阶段的暂定值以便审计，但正式 `reviewed_label` 必须为空；不得把暂定 `NEEDS_CONTEXT` 作为普通标签，不得进入训练、开发切片或 `blind_test_gold`。

## 3. 四类对照

| 输入状态 | 正确状态 | 业务理由 |
|---|---|---|
| “供应商应具备本地化服务能力”，文本清晰但定义缺失 | `NEEDS_CONTEXT` | 原文可靠；缺少“本地化”是否要求既有实体、何时生效以及是否产生评分／资格后果。 |
| 引用“资格条件第七项”，但第七项未提供 | `NEEDS_CONTEXT` | 当前引用关系可读，但决定性业务条款缺失；补齐第七项后重新判断。 |
| OCR 核心数字、主体或评分关系不可辨认 | `REWORK_SOURCE` | 输入不可靠，无法证明 Requirement 的原文事实。 |
| 表格行列关系错乱，无法确认要求主体 | `REWORK_SOURCE` | 结构解析失败，不能确认谁承担条件以及条件产生什么后果。 |

## 4. 强制处理流程

```text
Parser / Source Failure
        ↓
REWORK_SOURCE
        ↓
修复原件、附件、OCR 或表格结构
        ↓
重新进入 Annotation
        ↓
MATCH / NO_MATCH / NEEDS_CONTEXT
```

业务信息不足但原文可靠时，不得先标 `REWORK_SOURCE` 逃避业务判断；来源本身损坏时，也不得硬标 `NEEDS_CONTEXT`。

## 5. 边界案例复核结论

### 5.1 `C101-SEED-03`

- **业务身份**：`Business Boundary / Disputed Case`。
- **业务裁决**：按 `BR-C101-DEC-03`，其业务标签保留为 `MATCH / OTHER_RELATED`：已有省内售后机构或投标时承诺中标后设立，均把指定地区实体义务置于竞争条件中。
- **数据处置**：`review_state=DISPUTED`、`data_eligibility=HOLD`；独立人工业务复核、原采购文件逐字核验和数据 QA 完成前，不进入普通训练或 Blind Gold。
- **解释**：标签语义已经有临时业务裁决，但案例本身仍是边界争议样本，不能因有 `reviewed_label` 就把它当作普通已验训练例。

### 5.2 `C101-SEED-21`

- **业务身份**：`Parse Failure / REWORK_SOURCE`。
- **正式标签**：`reviewed_label=null`；原采集的 `proposed_label=NEEDS_CONTEXT/NONE` 只保留为历史痕迹。
- **数据处置**：`data_eligibility=REWORK_SOURCE`；不进入普通 Missing Context、训练集、开发集或 `blind_test_gold`。
- **修复动作**：调取原 PDF 页面、完整附表和可核对的表格结构，重建 Requirement 后重新进入 Annotation。

## 6. 对后续 Schema 的规范性输入

数据组实现时必须保持下列不变量：

| 场景 | `reviewed_label` | `data_eligibility` | `training_target` | `blind_test_gold` |
|---|---|---|---|---|
| 原文可靠、业务事实不足 | 正式 `NEEDS_CONTEXT` | 依 QA 结果决定，不能绕过准入闸门 | 可作为 Missing Context 候选 | 需测试组独立批准，不自动进入 |
| 原文或解析失败 | `null` | `REWORK_SOURCE` | 不生成／不导出 | 禁止进入 |
| `C101-SEED-03` 边界争议 | 暂定 `MATCH/OTHER_RELATED`，保留争议状态 | `HOLD` | 禁止进入普通训练 | 禁止进入 |

`REWORK_SOURCE` 的 `missing_context_questions` 可以描述修复所需材料，但这不把记录变成业务型 `NEEDS_CONTEXT`。Schema 不得通过默认值、回退标签或自动映射把 `REWORK_SOURCE` 转成正式 target。

## 7. 验收问题

项目负责人验收时四问，答案固定为：

| 验收问题 | 答案 |
|---|---|
| 文本清楚但事实不够 → `NEEDS_CONTEXT`？ | 是 |
| 原文坏了 → `REWORK_SOURCE`？ | 是 |
| `REWORK_SOURCE` 能直接训练？ | 否 |
| `REWORK_SOURCE` 能进 Blind Gold？ | 否 |

## 8. 版本和优先级

本日志采用 `V0.1 + Frozen Addendum` 方式，不改写已冻结正文的历史版本。对 `ParseFailure`、`REWORK_SOURCE`、`NEEDS_CONTEXT` 的冲突解释，以 `BR-C101-DEC-04` 为准；若要扩大适用范围、改变字段约束或改变 `C101-SEED-03` 的争议处置，必须新建版本并记录受影响案例、Schema 迁移和评测快照。

**依赖的冻结正文哈希**：

- `BR_C1_01_Business_Task_Spec_V0.1.md`：`0fa169fa0fa34ef8e702c4cae8e10e89cdce4260aa198f7a45a4a28d5c3a74ab`
- `C1_01_Label_Guide_V0.1.md`：`9b6352b5f6e400f2ad9ecca1cead4e26b03b3e81b8e6f761276b15ac3ffd67a6`

本裁决不把内部 Silver 变成 Gold，也不替代数据、算法或测试组的接口签字。
