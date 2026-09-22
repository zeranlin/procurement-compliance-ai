# C1-01 Gate-B Data / Benchmark Readiness Plan V0.1

**任务**：`C1-01_LOCAL_ENTRY_PRECONDITION`  
**基线**：`67948a874546627a07e6a7578e6938a2ff01fa7d`（Gate-A 最终冻结）  
**分支**：`codex/c1-01-gate-b-readiness`  
**计划状态**：`GATE_B_READINESS_PLANNING`  
**范围**：数据就绪、Benchmark Snapshot 就绪、Blind 隔离与运行时 ACL、模型环境准备  
**明确边界**：本计划不生产 Gold、不读取 Blind Gold、不运行模型、不运行训练。

## 1. 目标与非目标

### 目标

在不改变 Gate-A 冻结契约的前提下，完成可审计的 Gate-B Readiness Review，使项目具备申请以下后续步骤的条件：

```text
Base Model Zero-shot / Few-shot
        ↓
Training Decision
        ↓
LoRA / QLoRA（仅在明确授权后）
        ↓
Blind Benchmark（再次经授权）
```

### 非目标

- 不修改 BusinessTaskSpec、LabelGuide、DatasetSchema、BaselineProtocol、MetricSpec 或 Blind Governance；
- 不把当前 `INTERNAL_SILVER` 直接升级为 Gold；
- 不创建、导出、查看或复制 `blind_test_gold`；
- 不调用 Teacher API，不下载或运行 Student/Base Model；
- 不在 Gate-B 未通过前解锁 Base Model、Fine-tune 或 Blind Benchmark。

## 2. 依赖图

```text
Gate-A Contract Frozen (67948a8)
        │
        ├── 02 Data Readiness
        │     ├── 来源/证据/Schema
        │     ├── split、pair、leakage
        │     └── Train / Dev / Benchmark Candidate Manifest
        │
        ├── 04 Benchmark Readiness
        │     ├── Snapshot ID 与 input/gold 隔离
        │     ├── Metric/评测器版本锁定
        │     └── Runtime ACL + audit log
        │
        └── 03 Model Environment Readiness
              ├── Student/Base 环境清单
              ├── tokenizer、framework、revision、硬件
              └── 只做环境级可复现性检查，不运行模型
        │
        ▼
Gate-B Readiness Review
        │
        ├── 通过 → 申请 Base Zero/Few-shot
        └── 未通过 → 保持模型/训练/盲测 BLOCKED
```

## 3. Owner 与职责

| Owner | Gate-B 职责 | 明确禁止 |
|---|---|---|
| 项目负责人 / 总控 | 维护计划、依赖、风险、入口/退出判定和授权顺序 | 读取 Blind Gold；绕过 Gate-B 授权模型或训练 |
| 02 数据工程组 | 候选数据整理、来源/Schema、去重、split、pair、leakage、数据 Manifest | Freeze 后修改 Gold；将争议或源件修复记录升格为训练数据 |
| 03 算法/平台组 | 模型环境、adapter、tokenizer、运行参数与可复现清单 | 读取 Gold、生成训练数据、在授权前运行模型/训练 |
| 04 测试与评测组 | Snapshot、评测器、Blind input/gold 隔离、ACL、审计和 Gate-B 验收 | 向算法组提供逐例 Gold、调参反馈或隐藏切片成员 |
| 01 业务组 | 仅处理新增真实业务争议或复核请求 | 改写已冻结语义；按模型结果回标 |

## 4. 当前交付盘点

| 组别 | 已确认来源 | 当前判断 | Gate-B 缺口 |
|---|---|---|---|
| 02 数据 | `83aff9a`；已纳入 `67948a8`，Seed SHA、Schema、29/29、Manifest 8/8 已签署 | Gate-A 输入基线可用 | 尚无 Gate-B 正式 Snapshot、Train/Dev/Benchmark 候选清单和签署包 |
| 03 算法 | `4019011`、`a720a03`；Protocol/lock/Harness 已冻结 | 协议可用 | 未发现模型环境提交；需提交 Qwen 环境、adapter、tokenizer、framework、硬件和复现清单 |
| 04 评测 | `3bea201`、`bf151ba`；Gate-A 复验与治理规则已冻结 | Contract Ready | 未发现真实 Snapshot、隔离评测器部署证明、Runtime ACL Probe、审计日志 |
| 01 业务 | `0751558` 与最终冻结记录 | 语义冻结 | 仅处理新增业务冲突，不重新打开既有语义 |

> 以上“未发现”表示当前候选分支和已盘点分支没有可核验的对应交付物，不代表其他工作区不可存在；收到新提交后必须重新登记来源、哈希和责任人。

## 5. 入口条件

Gate-B 工作只能在以下条件全部成立时进入正式 Readiness Review：

1. Gate-A 状态为 `C1-01 END-TO-END CONTRACT FROZEN / GATE-A_COMPLETE`；
2. 02 `DATA_SIGNOFF_PASS` 与 04 `QA_FINAL_SIGNOFF_PASS` 绑定同一候选 `717a0bb`；
3. 六项主契约和盲测治理哈希不变；任何变化必须新建版本和重新走 Gate-A；
4. 02、03、04 提交完整来源、版本、SHA-256、Owner 和可复现命令；
5. 任何新数据不得包含 Blind Gold 明文或可逆真值派生物。

## 6. Exit Gate：Gate-B Readiness PASS

只有以下条件全部 PASS，项目负责人才能申请 Base Model Zero/Few-shot：

- 数据：Train、Dev、Benchmark Candidate 的角色、数量、来源、证据、pair 和 leakage 检查有签署清单；`DISPUTED`、`HOLD`、`REWORK_SOURCE` 不进入训练或 Benchmark；
- Snapshot：拥有不可变 `snapshot_id`、input hash、gold hash、metric/evaluator hash、split counts、leakage/counterfactual 结果和 Owner；
- 隔离：算法组只能读取脱敏的 `blind_test_input`，QA 独占 Gold；Runtime ACL 正向/拒绝场景和审计日志均 PASS；
- 评测：MetricSpec、Schema、协议、评测器和 Gate 在 Snapshot 前预注册，不能以模型结果反向改写；
- 环境：Qwen Student/Base 环境、revision、tokenizer、framework、generation config、硬件和代码提交可复现；
- 治理：02、03、04 和项目负责人完成 Gate-B Readiness Review，明确 `benchmark_ready` 与下一步授权，不把计划状态写成运行结果。

## 7. 里程碑与授权顺序

| 阶段 | 交付 | Owner | 当前状态 | 授权结果 |
|---|---|---|---|---|
| B0 | Gate-B 计划、Checklist、模型选择、验收矩阵 | 项目总控 | 本提交 | 仅建立计划 |
| B1 | 数据候选包、Snapshot 组装材料、leakage/pair 报告 | 02 + 04 | NOT_STARTED | 仍不运行模型 |
| B2 | Runtime ACL、隔离评测器、审计日志 | 04 | NOT_STARTED | 仍不运行模型 |
| B3 | Qwen 环境与 adapter 可复现清单 | 03 | NOT_STARTED | 仍不运行模型 |
| B4 | Gate-B Readiness Review | PM + 02/03/04 | BLOCKED_BY_B1_B2_B3 | 未通过则保持 BLOCKED |
| B5 | Base Zero/Few-shot | 03 + 04 | BLOCKED | 仅 B4 PASS 后申请 |
| B6 | Training Decision | PM | BLOCKED | 仅基线结果和误差分析后决定 |
| B7 | LoRA/QLoRA | 03 | BLOCKED | 仅明确授权后执行 |

强制顺序：

```text
数据就绪
  → Benchmark Snapshot / Blind 隔离就绪
  → Base Model Zero/Few-shot
  → Training Decision
  → LoRA/QLoRA
```

## 8. 风险清单

| 风险 | 影响 | 责任人 | 控制措施 | 当前状态 |
|---|---|---|---|---|
| Silver 被误当 Gold | 污染训练/评测，结论不可解释 | 02/04 | `INTERNAL_SILVER` lineage、人工复核、Gold 独占 | OPEN |
| Blind Gold 泄漏 | Blind 评测作废 | 04 | P0 ACL、隔离 evaluator、审计和拒绝场景 | OPEN |
| Seed/候选角色漂移 | 泄漏或错误分母 | 02 | manifest、role allowlist、重跑 Schema/Cross-field | OPEN |
| Teacher 生成偏差 | 候选标签错误进入 Silver | 03/02 | Teacher 仅 Silver candidate，来源/提示词/版本留痕，禁止 Gold 权威 | OPEN |
| 模型 revision 不可复现 | Base/Student 比较失真 | 03 | pin revision、tokenizer、framework、硬件和 config | OPEN |
| Benchmark 规模/覆盖不足 | Gate-B 不能代表目标能力 | 04/02 | 预注册 sample count、切片、pair、coverage 和最小门槛 | OPEN |
| Gate-B 结论倒灌 Gate-A | 冻结链被静默修改 | PM | 版本/hash 变化新建候选，不改冻结资产 | OPEN |

## 9. 当前判定

```text
GATE_B_READINESS = PLANNING
BENCHMARK_READY = FALSE
BASE_MODEL = BLOCKED
FINE_TUNE = BLOCKED
BLIND_BENCHMARK = BLOCKED
```

本计划提交不产生模型运行结果，不产生 Gold，不构成训练授权。
