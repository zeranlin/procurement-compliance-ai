# C1-01 Dataset Schema Change Log V0.2

**Change type：结构性不兼容升级**  
**Previous：`C1_01_Dataset_Schema_V0.1`**  
**Current：`C1_01_Dataset_Schema_V0.2`**  
**Schema SHA-256：`484cb50e52e337d24cd014db9ddf1af98d5d82fee9706c512307bb8190da25fb`**  
**Status：FROZEN_FOR_DATA_ENGINEERING_HANDOFF**

## 1. 升级原因

V0.1 将 `target` 作为必填对象，只允许 `MATCH / NO_MATCH / NEEDS_CONTEXT`。这会把 OCR、表格关系、原件或附表缺失造成的源件问题错误地挤进业务标签，无法表达：

```text
source defect prevents judgment
→ target = null
→ REWORK_SOURCE
```

V0.2 把记录生命周期拆成两个机器状态：

```text
LABELED
  → target 必须存在
  → target.match_state = MATCH | NO_MATCH | NEEDS_CONTEXT

UNAVAILABLE_SOURCE_REWORK
  → target 必须为 null
  → parser_quality = UNCERTAIN
  → source_defect_prevents_judgment = true
  → data_eligibility = REWORK_SOURCE
```

这是结构性不兼容变化，因此不覆盖 V0.1，也不使用 V0.1 的文件名伪装成兼容补丁。

## 2. 变更明细

| 编号 | 变更 | V0.1 | V0.2 | 影响 |
|---|---|---|---|---|
| C-01 | 增加 `annotation_state` | 无 | `LABELED` / `UNAVAILABLE_SOURCE_REWORK` | 解析失败不再伪造业务 target |
| C-02 | `target` 生命周期 | 必填对象 | LABELED 为对象；REWORK 为 `null` | 下游必须处理 nullable target |
| C-03 | 源件缺陷字段 | 只有 `parser_quality` | 增加 `source_defect_prevents_judgment`、`source_defect_reason` | 机器区分缺上下文与坏源件 |
| C-04 | 来源可追溯 | 单一来源定位 | 增加 `source_record_sha256`、`evidence_status`、采购文件强制条件 | 可审计原始种子和证据资格 |
| C-05 | 资格与角色 | 条件较弱 | `REWORK_SOURCE`、`TRAIN/DEV/BLIND_GOLD` 交叉硬约束 | 源件修复记录无法进入监督 split |
| C-06 | 争议处理 | `DISPUTED` 仅部分约束 | `review_state=DISPUTED → data_eligibility=HOLD` | 争议标签不能进入训练或盲测 |
| C-07 | 证据 | MATCH 结构上要求证据 | HOLD 标签可暂缺证据；可训练/Benchmark 必须有精确跨度 | 兼容种子预标注与训练准入 |
| C-08 | 版本元数据 | `schema_version=0.1` | `schema_version=0.2` + `schema_sha256` | 防止静默混用 |

## 3. 迁移规则

### 3.1 V0.1 已有业务标签记录

满足原文已可靠读取且存在业务标签时：

1. 添加 `annotation_state=LABELED`；
2. 保留原 `target` 对象；
3. 添加 `input.source_defect_prevents_judgment=false` 和 `source_defect_reason=null`；
4. 加 `schema_version=0.2`、实际 V0.2 `schema_sha256`；
5. 将没有采购文件逐字证据的记录保持为 `data_eligibility=HOLD`，不能仅因有 target 就升格训练。

### 3.2 V0.1 的解析失败记录

凡是 OCR 不清、原件缺失、附表缺失、表格行列关系无法确认，且该缺陷会改变业务判断的记录：

1. `annotation_state=UNAVAILABLE_SOURCE_REWORK`；
2. `target=null`；
3. `input.parser_quality=UNCERTAIN`；
4. `input.source_defect_prevents_judgment=true`；
5. 填写 `source_defect_reason`；
6. `metadata.data_eligibility=REWORK_SOURCE`；
7. `metadata.dataset_role=UNASSIGNED` 或 `REWORK_QUEUE`；
8. 历史 `proposed_label` 只进入审计报告，不进入监督 target。

不得把这类记录迁移为 `NEEDS_CONTEXT`。`NEEDS_CONTEXT` 仅用于原文已经可靠读取、但业务事实不足的记录。

### 3.3 争议记录

`review_state=DISPUTED` 的记录可以保留暂定 target 供审计，但必须 `data_eligibility=HOLD`，不得分配 `TRAIN`、`DEV` 或 `BLIND_GOLD`。完成正式裁决后，生成新快照或新版本回标，不能覆盖旧行的审计历史。

## 4. 对下游的接口影响

- Baseline Harness：读取 `annotation_state`；遇到 `UNAVAILABLE_SOURCE_REWORK` 必须跳过监督 target，并记录跳过原因。
- Benchmark Metric Spec：不得把 source-rework 计入 MATCH/NO_MATCH/NEEDS_CONTEXT 分母；blind gold 只能来自 `LABELED` 且完成资格闸门的记录。
- Blind Test：`UNAVAILABLE_SOURCE_REWORK` 不得进入 `BLIND_GOLD`；source repair 后要重新建立 benchmark 快照。
- Traceability Matrix：将 `annotation_state`、`source_defect_prevents_judgment`、`data_eligibility` 和 `schema_sha256` 纳入数据契约追踪。

## 5. 变更验证

使用 `validate_sample.py revalidate-seeds` 对当前 29 条 Seed Cases 全量重跑：

| 结果 | 数量 |
|---|---:|
| Schema Valid | 29/29 |
| Cross-field Valid | 29/29 |
| `LABELED` | 28 |
| `UNAVAILABLE_SOURCE_REWORK` | 1 |
| `C101-SEED-03` | `LABELED` + `MATCH/OTHER_RELATED` + `DISPUTED/HOLD` |
| `C101-SEED-21` | `target=null` + `UNCERTAIN` + `REWORK_SOURCE` |
| TRAIN / DEV / BLIND_GOLD | 0 / 0 / 0 |

完整逐条结果见 `C1_01_Seed_Cases_Revalidation_Report_V0.2.md` 与对应 JSON。
