# C1-01 QA Revalidation Record

> **验收主题**：04 - 测试与评测组 / Cross-Team Contract Verification 复核
> **日期**：2026-09-22
> **结论**：`BLOCKED`
> **冻结结论**：`C1-01 END-TO-END CONTRACT FROZEN = NOT APPROVED`

## 1. 核验范围与证据边界

本记录只依据当前仓库实物核验，不把网页对话或未提交文件当作项目资产。

| 项目 | 观察结果 |
|---|---|
| HEAD | `7de2d95` |
| 工作树 | clean（核验开始时无未提交变更） |
| 当前项目控制入口 | `docs/project-management/C1_01_PROJECT_CONTROL.md` |
| V0.2 评测产物 | 未发现 |
| 非 README 数据文件 | `datasets/` 下为 0 |
| 可执行 evaluator / harness | 未发现 |
| `blind_test_gold` 实际内容 | 未进入仓库；仅有 README 和规则说明 |

“未发现”在本记录中不是对外部受控存储的否定，只表示当前仓库没有足够证据完成可复现冻结验收。

## 2. 六资产核验

| 资产 | 当前仓库实物 | 状态 | 结论 |
|---|---|---|---|
| A1 Business Task Spec | `BR_C1_01_Business_Task_Spec_V0.1.md` | V0.1 / FROZEN | `PASS`（文档存在，未代替跨团队签署） |
| A2 Label Guide | `C1_01_Label_Guide_V0.1.md` | V0.1 / FROZEN | `PASS`（业务语义文档存在） |
| A3 Dataset Schema | `C1_01_Dataset_Schema_V0.1.json` | DRAFT / INTERNAL_SILVER only | `BLOCKED` |
| A4 Baseline Protocol | `C1_01_Baseline_Harness_V0.1_README.md` | DRAFT；仅接口联调说明 | `BLOCKED` |
| A5 Benchmark Metric Spec | `C1_01_Benchmark_Metric_Spec_V0.1.md` | FROZEN 文档 | `BLOCKED`（依赖的 Snapshot 与 evaluator 不存在） |
| A6 Blind Test Rules / Access Boundary | 两份 V0.1 规则文档 | FROZEN 文档 | `PASS`（静态规则）；运行时回归 `BLOCKED` |

关键证据：

- Dataset Schema 的 description 明确写有 `DRAFT, INTERNAL_SILVER only`；
- Baseline Harness 明确写有“状态：DRAFT”，并声明尚未产生 Base Model 成绩；
- Metric Spec 与 Blind Rules 引用了 `C1_01_BenchmarkSnapshot_V0.1`，但仓库不存在该 Snapshot 目录或 Manifest；
- Access Boundary 明确禁止算法组读取 Gold，但仓库没有可执行权限回归或隔离 evaluator 可供运行。

## 3. Eligibility / Snapshot / Runtime 核验

### 3.1 Benchmark candidate

项目控制要求的候选资格为：

```text
parser_quality = PASS
review_state = INTERNAL_REVIEWED
data_eligibility = BENCHMARK_CANDIDATE
target != null
```

当前仓库 `datasets/` 下除 README 外没有 JSON/JSONL/CSV/TSV 等数据记录，因此无法证明任何一条记录满足上述条件，也无法从仓库实物确认“现有 29 条”或 `BENCHMARK_CANDIDATE` 数量。该项判定为 `BLOCKED`，不能按 0 条候选快照继续评测，也不能把文档示例当成数据。

### 3.2 Frozen Snapshot

未发现以下可运行资产：

```text
BenchmarkSnapshot/
blind_test_input.jsonl
blind_test_gold.jsonl（受控仓库外不要求提交，但必须有受控指针）
manifest.json
freeze_record.json
```

因此无法执行：输入/Gold 对齐、切片计数、Train/Dev/Blind 泄漏检查、反事实对检查、内容哈希锁定或 evaluator 版本锁定。`Freeze Manifest = BLOCKED`。

### 3.3 Executable evaluator / baseline runtime

当前仓库没有 `harness.py`、评测器入口、预测对齐实现、Schema cross-field validator 或可执行 Gold/evaluator runtime。现有三个 Python 脚本仅完成 JSON 语法、结构路径和敏感内容检查，不能替代 Benchmark evaluator，也不能产生 Base Model 成绩。

因此：

- `Metric / Schema Compatibility Test = BLOCKED`；
- `Gold Access Boundary Regression = BLOCKED`（静态规则为 PASS）；
- `End-to-End Traceability Verification = BLOCKED`；
- `Formal Model Run = BLOCKED`。

## 4. 已执行的静态检查

| 检查 | 命令/范围 | 结果 |
|---|---|---|
| Contract JSON syntax | `python3 scripts/validate_contracts.py` | `PASS` |
| Repository structure | `python3 scripts/validate_structure.py` | `PASS` |
| Sensitive-content check | `python3 scripts/detect_leakage.py` | `PASS` |
| Six-asset hash inventory | 当前公开契约文件 | `PASS`（可计算哈希；不等于 Freeze Manifest） |
| Snapshot eligibility | 当前 `datasets/` 实物 | `BLOCKED` |
| Contract compatibility | 可执行 Schema/Baseline/Metric runtime | `BLOCKED` |
| Access boundary regression | 可运行隔离权限测试 | `BLOCKED` |
| End-to-end traceability | 实际样本→预测→评分→报告 | `BLOCKED` |

静态检查通过只说明当前提交没有明显结构或敏感内容违规，不授权进入模型实验、冻结 Snapshot 或打开 Blind Gold。

## 5. Blind Gold 权限判定

`blind_test_gold` 继续保持测试与评测组独占。算法组不得：

- 读取、复制、搜索或猜测 Gold；
- 获取隐藏切片、`leakage_group_id` 或逐例反馈；
- 运行测试组专用的 Gold 评分选项；
- 将任何真值派生物放入训练、few-shot、提示词、验证、回归或向量索引。

本次复核没有改变权限边界，也没有因缺少 runtime 而放宽边界。由于没有实际隔离运行环境，权限结论只能是：静态规则 `PASS`，运行时验证 `BLOCKED`。

## 6. Gate 决定

```text
CROSS_TEAM_CONTRACT_VERIFICATION = BLOCKED
C1-01 END-TO-END CONTRACT FROZEN = NOT APPROVED
BASE MODEL / FINE-TUNE / BLIND BENCHMARK / DEMO GATE = BLOCKED
```

不得以“文档已写出”“静态权限规则通过”或“教程中的示例结构”替代以下硬证据：

1. Dataset Schema 从 DRAFT 变为经 QA 接受的版本；
2. 至少一个可追溯、可审计、满足资格条件的 DEV/候选数据快照；
3. BaselineProtocol 的正式冻结版本与可执行 runtime；
4. Benchmark Snapshot、Freeze Manifest、版本/哈希和泄漏检查结果；
5. 独立 evaluator 与访问边界回归结果；
6. End-to-End Traceability Verification 和项目负责人 Final Freeze Review。

## 7. 解锁顺序

```text
数据组交付可核验候选数据与 Dataset Snapshot
    ↓
算法组提交冻结的 BaselineProtocol / 可执行 harness
    ↓
测试组完成 Metric-Schema Compatibility Test
    ↓
测试组在受控环境建立 Snapshot + Freeze Manifest
    ↓
测试组完成 Access Boundary Regression + E2E Traceability
    ↓
项目负责人执行 G1~G13 Final Freeze Review
    ↓
才允许 Base Model Baseline
```

任何一步失败都不得通过降低样本资格、降低 Gate、暴露 Gold 或把 smoke 结果包装成正式成绩来解锁。
