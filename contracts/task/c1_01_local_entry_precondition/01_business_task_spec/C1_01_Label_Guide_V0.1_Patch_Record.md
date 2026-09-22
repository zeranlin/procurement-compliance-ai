# C1-01 Label Guide V0.1 补丁记录

**补丁标识**：`C1_01_Label_Guide_V0.1_Patch_Record`  
**补丁编号**：`LG-PATCH-20260922-01`  
**状态**：`FROZEN`（Label Guide 的规范性 Frozen Addendum）  
**生效日期**：2026-09-22  
**适用任务**：`C1-01_LOCAL_ENTRY_PRECONDITION`  
**关联裁决**：`BR-C101-DEC-04`  
**上游依赖**：`BR-C1-01_Decision_Log_V0.1.md`

## 1. 补丁目的

本补丁把 `Missing Business Context != Broken Source` 写成标注和数据准入的强制规则，补足 `C1_01_Label_Guide_V0.1.md` 中对业务信息缺失与来源／解析失败的边界。补丁不改变 `MATCH`、`NO_MATCH`、`NEEDS_CONTEXT` 的三分类，也不改变 `BR-C101-DEC-03` 对 `C101-SEED-03` 的业务标签裁决。

冻结正文继续保留原版本号；本记录与正文共同构成 V0.1 的有效规范。发生冲突时，本补丁关于解析失败的规则优先。

## 2. 标注规则补丁

### 2.1 可靠来源才能形成普通标签

标注员先判断输入是否可靠，再判断业务事实是否充分：

1. 来源、页码／章节、OCR 文本或表格结构可核对；
2. 能重建一个独立 Requirement；
3. 然后才判断它是 `MATCH`、`NO_MATCH` 或 `NEEDS_CONTEXT`。

来源不可靠时，记录进入 `REWORK_SOURCE`，不得用 `NEEDS_CONTEXT` 代替解析质量结论。

### 2.2 两个状态的定义

| 状态 | 必备条件 | 缺失内容 | 正确动作 |
|---|---|---|---|
| `NEEDS_CONTEXT` | 原文已可靠读取，Requirement 可重建 | 业务定义、引用条款、评分后果、例外材料等 | 提出具体补件问题，补齐后重标；经 QA 才可成为训练候选 |
| `REWORK_SOURCE` / `PARSE_FAILURE` | 原文、页面、OCR、附件或结构解析不可靠 | 核心数字、主体、条件、分值关系或表格归属无法确认 | 修复来源，再重新进入 Annotation；不生成正式 target |

### 2.3 禁止的回退路径

以下映射一律禁止：

```text
OCR 看不清 → NEEDS_CONTEXT → 进入训练
表格列错乱 → NEEDS_CONTEXT → 进入 Blind Gold
附件缺页且主体不可辨 → NO_MATCH
```

正确路径是：

```text
Parser / Source Failure → REWORK_SOURCE → 修复原件 → 重新标注
```

## 3. 最小对照集

| 案例 | 输入 | 标签／状态 |
|---|---|---|
| U-CTX-01 | “供应商应具备本地化服务能力”，文字清晰，但没有定义“本地化”是否要求既有实体，也没有评分／资格后果。 | `NEEDS_CONTEXT / NONE` |
| U-CTX-02 | “按照资格条件第七项提供本市服务证明”，句子可读，但资格条件第七项未提供。 | `NEEDS_CONTEXT / NONE` |
| U-REWORK-01 | OCR 不能辨认距离数值、要求主体或评分后果。 | `REWORK_SOURCE`，正式标签为空 |
| U-REWORK-02 | 表格行列关系错乱，无法确认条件属于投标人还是项目地点。 | `REWORK_SOURCE`，正式标签为空 |

## 4. 对 `C101-SEED-03` 与 `C101-SEED-21` 的约束

| Seed | 业务复核状态 | 数据资格 | 补丁要求 |
|---|---|---|---|
| `C101-SEED-03` | `Business Boundary / Disputed Case`；暂定 `MATCH / OTHER_RELATED` | `HOLD` | 保留争议身份，不得进入普通训练池或 Blind Gold；等待独立人工业务复核、原件核验和数据 QA。 |
| `C101-SEED-21` | `Parse Failure / REWORK_SOURCE`；`reviewed_label=null` | `REWORK_SOURCE` | 不得进入普通 `NEEDS_CONTEXT` 切片、训练集、开发集或 Blind Gold；修复原件和附表后重新标注。 |

## 5. Schema 与数据准入映射

数据 Schema 必须能表达以下约束：

- `parser_quality` 或等价字段必须区分可靠文本与来源／解析失败；
- `REWORK_SOURCE` 记录的正式 `reviewed_label` 为 `null`，不得自动回退到 `NEEDS_CONTEXT`；
- `REWORK_SOURCE` 不生成 `training_target`，不进入 `blind_test_gold`；
- `NEEDS_CONTEXT` 必须有具体 `missing_context_questions`，且只在来源可靠时计入 Missing Context 分母；
- `C101-SEED-03` 的争议状态和 `HOLD` 闸门必须保留，不能因存在暂定业务标签而自动入训练。

这些约束是后续 `C1_01_Dataset_Schema_V0.1` 的规范性输入；Schema 若无法表达，必须先修订 Schema 或建立版本变更单，不能通过数据清洗静默丢弃状态。

## 6. 业务组验收签核项

- [x] 文本清楚但事实不够，标 `NEEDS_CONTEXT`。
- [x] 原文损坏或解析失败，标 `REWORK_SOURCE`。
- [x] `REWORK_SOURCE` 不直接训练。
- [x] `REWORK_SOURCE` 不进入 Blind Gold。
- [x] `C101-SEED-03` 保持 `Business Boundary / Disputed Case` 与 `HOLD`。
- [x] `C101-SEED-21` 保持 `Parse Failure / REWORK_SOURCE`，正式标签为空。

**补丁生效条件**：上述规则已写入 `BR-C1-01_Decision_Log_V0.1.md` 的 `BR-C101-DEC-04`，并由数据组在 Schema 契约测试中实现字段和准入闸门。

**依赖冻结正文哈希**：`C1_01_Label_Guide_V0.1.md`：`9b6352b5f6e400f2ad9ecca1cead4e26b03b3e81b8e6f761276b15ac3ffd67a6`。
