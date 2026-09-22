# 政府采购采购文件合规审查垂直领域 AI
# 工程目录结构规划 V0.1

## 1. 设计结论

首期采用 **Monorepo + 八个逻辑模块边界**。

这样既能让 C1-01 最小闭环快速联调，又不会把数据、规则、法规、模型、引擎、Agent、评测和平台代码混成一个不可治理的目录。后续如果团队或权限需要拆分，可按 `modules/` 下的八个目录直接迁移为独立仓库。

顶层系统保持蓝图定义：

```text
Data + Rules + Policy + Legal RAG + Calculator
    + Compliance LM + Hybrid Engine + Agent
    + Benchmark + Production Governance
```

强制原则：

1. 共享契约必须同时包含中文业务语义、示例、边界、失败表达和契约测试。
2. `Finding` 必须能够追溯到采购文件证据和法规/政策证据。
3. `blind_test_gold` 只由测试与评测组管理；普通开发、训练和模型评测流程不能读取其内容。
4. 原始采购文件、真实盲测金标、模型权重和密钥不作为普通 Git 文件提交。
5. 目录可以先建齐，代码和数据按建设优先级逐步填充：Schema → Benchmark → Gold Data → Model → Engine → Agent → Production。

## 2. 首期 Monorepo 目录

```text
procurement-compliance-ai/
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE
├── Makefile
├── pyproject.toml
├── uv.lock                         # 或项目实际采用的锁文件
├── .gitignore
├── .env.example                    # 只放变量名，不放密钥
│
├── .github/
│   ├── CODEOWNERS
│   ├── pull_request_template.md
│   └── workflows/
│       ├── contract-check.yml
│       ├── data-quality-check.yml
│       ├── benchmark-gate.yml
│       ├── integration-test.yml
│       └── security-scan.yml
│
├── docs/
│   ├── architecture/
│   │   ├── overall-architecture.md
│   │   ├── module-contracts.md
│   │   ├── repository-boundaries.md
│   │   └── adr/
│   ├── tutorial/
│   │   ├── README.md                 # 十一课教程入口与工程映射
│   │   ├── COURSE_ALL.md             # 十一课完整合订内容
│   │   └── lessons/                  # 后续按课拆分的 canonical 文档
│   │       └── README.md
│   ├── governance/
│   │   ├── release-policy.md
│   │   ├── access-boundary.md
│   │   ├── blind-test-management.md
│   │   └── data-classification.md
│   ├── operations/
│   │   ├── local-development.md
│   │   ├── benchmark-runbook.md
│   │   ├── incident-response.md
│   │   └── rollback-runbook.md
│   └── traceability/
│       ├── traceability-matrix.md
│       └── release-evidence-index.md
│
├── contracts/                      # 共享契约唯一事实源
│   ├── common/
│   │   ├── identifiers/
│   │   ├── enums/
│   │   ├── evidence_span.schema.json
│   │   ├── version_binding.schema.json
│   │   └── error_state.schema.json
│   ├── task/
│   │   └── c1_01_local_entry_precondition/
│   │       ├── 01_business_task_spec/
│   │       │   ├── BusinessTaskSpec_V0.1.md
│   │       │   ├── schema.json
│   │       │   └── examples/
│   │       ├── 02_label_guide/
│   │       │   ├── LabelGuide_V0.1.md
│   │       │   ├── schema.json
│   │       │   └── examples/
│   │       ├── 03_dataset_schema/
│   │       │   ├── DatasetSchema_V0.1.json
│   │       │   └── examples/
│   │       ├── 04_baseline_protocol/
│   │       │   ├── BaselineProtocol_V0.1.md
│   │       │   ├── schema.json
│   │       │   └── examples/
│   │       ├── 05_benchmark_metric_spec/
│   │       │   ├── BenchmarkMetricSpec_V0.1.md
│   │       │   ├── schema.json
│   │       │   └── examples/
│   │       ├── 06_blind_test/
│   │       │   ├── BlindTest_Management_Rules_V0.1.md
│   │       │   ├── BlindTest_Gold_Access_Boundary_V0.1.md
│   │       │   ├── manifest.schema.json
│   │       │   └── gold_location.pointer
│   │       └── traceability_matrix.md
│   ├── document/
│   │   ├── procurement_document_ir.schema.json
│   │   ├── clause.schema.json
│   │   ├── requirement.schema.json
│   │   └── evidence.schema.json
│   ├── policy/
│   │   ├── policy_snapshot.schema.json
│   │   ├── legal_proposition.schema.json
│   │   └── citation_support.schema.json
│   ├── rule/
│   │   ├── rule_definition.schema.json
│   │   ├── rule_evaluation.schema.json
│   │   └── calculator_result.schema.json
│   ├── model/
│   │   ├── compliance_lm_request.schema.json
│   │   ├── compliance_lm_assessment.schema.json
│   │   └── structured_output.schema.json
│   ├── engine/
│   │   ├── compliance_review_request.schema.json
│   │   ├── compliance_review_result.schema.json
│   │   ├── finding.schema.json
│   │   └── decision_trace.schema.json
│   ├── agent/
│   │   ├── review_state.schema.json
│   │   ├── human_review_task.schema.json
│   │   └── report_state.schema.json
│   └── benchmark/
│       ├── benchmark_snapshot.schema.json
│       ├── evaluation_report.schema.json
│       ├── error_analysis.schema.json
│       └── gate_decision.schema.json
│
├── modules/                        # 蓝图中的八个可独立拆仓边界
│   ├── procurement-data/
│   ├── procurement-policy/
│   ├── procurement-rules/
│   ├── procurement-model/
│   ├── procurement-engine/
│   ├── procurement-agent/
│   ├── procurement-benchmark/
│   └── procurement-platform/
│
├── datasets/                       # Git 只保存清单、版本和指针
│   ├── manifests/
│   ├── source_catalog/
│   ├── staging/
│   ├── curated/
│   ├── snapshots/
│   ├── benchmark/
│   │   ├── train/
│   │   ├── dev/
│   │   ├── public_eval/
│   │   ├── candidate/
│   │   ├── red_team/
│   │   └── blind_test_gold/        # 仅保留受控指针，不放金标内容
│   └── reports/
│
├── experiments/
│   ├── baseline/                    # Base Model / Model Only
│   ├── model_only/                  # 实验 A
│   ├── workbuddy_swap/              # 实验 B
│   ├── company_agent_swap/          # 实验 C
│   └── full_system/                 # 实验 D
│
├── configs/
│   ├── local/
│   ├── dev/
│   ├── benchmark/
│   └── prod/
│
├── tests/
│   ├── contract/
│   ├── integration/
│   ├── regression/
│   ├── security/
│   └── fixtures/                    # 不含 blind_test_gold
│
├── scripts/
│   ├── validate_structure.py
│   ├── validate_contracts.py
│   ├── validate_dataset.py
│   ├── detect_leakage.py
│   ├── run_baseline.py
│   ├── run_benchmark.py
│   ├── generate_traceability.py
│   └── build_release_bundle.py
│
├── deploy/
│   ├── docker/
│   ├── compose/
│   ├── k8s/
│   └── environments/
│
└── tools/
    ├── cli/
    ├── devtools/
    └── repo_checks/
```

## 3. 八个模块的内部结构

除 `procurement-platform` 外，各模块采用统一形态：

```text
<module>/
├── README.md
├── pyproject.toml
├── src/<python_package>/
├── configs/
├── examples/
├── tests/
│   ├── unit/
│   ├── contract/
│   ├── integration/
│   └── regression/
└── docs/
```

模块专属目录如下：

```text
modules/procurement-data/
├── src/procurement_data/
│   ├── ingest/
│   ├── parsing/                    # PDF / Word / OCR / 表格
│   ├── normalization/
│   ├── document_ir/
│   ├── clause/
│   ├── requirement/
│   ├── evidence/
│   ├── quality_gate/
│   └── lineage/
├── schemas/
├── fixtures/
└── tests/golden/

modules/procurement-policy/
├── src/procurement_policy/
│   ├── registry/
│   ├── resolver/
│   ├── temporal/
│   ├── jurisdiction/
│   ├── conflict/
│   ├── exception/
│   ├── citation/
│   └── legal_rag/
├── policy_sources/                  # 只保存索引/元数据，原件按权限管理
└── snapshots/

modules/procurement-rules/
├── src/procurement_rules/
│   ├── registry/
│   ├── predicates/
│   ├── exceptions/
│   ├── calculator/
│   └── domains/
│       ├── method/
│       ├── threshold/
│       ├── competition/
│       ├── abnormal_low_price/
│       ├── temporal/
│       ├── qualification/
│       ├── technical/
│       ├── scoring/
│       └── policy/
├── rule_catalog/
└── tests/rule_regression/

modules/procurement-model/
├── src/procurement_model/
│   ├── inference/
│   ├── structured_output/
│   ├── prompting/
│   ├── training/
│   ├── adapters/
│   ├── serving/
│   └── abstention/
├── training_configs/
├── manifests/
├── checkpoints/                     # Git 忽略；只登记版本指针
└── reports/

modules/procurement-engine/
├── src/procurement_engine/
│   ├── router/
│   ├── orchestration/
│   ├── rule_adapter/
│   ├── policy_adapter/
│   ├── model_adapter/
│   ├── calculator_adapter/
│   ├── decision_trace/
│   ├── evidence_gate/
│   ├── coverage/
│   ├── finding/
│   └── replay/
└── tests/conflict_and_failure/

modules/procurement-agent/
├── src/procurement_agent/
│   ├── planner/
│   ├── state_machine/
│   ├── tool_routing/
│   ├── checkpoint/
│   ├── human_review/
│   ├── coverage_gate/
│   ├── report_projection/
│   └── prompt_injection_guard/
└── tests/workflow_recovery/

modules/procurement-benchmark/
├── src/procurement_benchmark/
│   ├── harness/
│   ├── datasets/
│   ├── slices/
│   ├── metrics/
│   ├── gates/
│   ├── baselines/
│   ├── error_analysis/
│   └── reports/
├── protocols/
├── manifests/
└── access/                          # blind gold 权限与审计定义

modules/procurement-platform/
├── src/procurement_platform/
│   ├── api/
│   ├── auth/
│   ├── rbac/
│   ├── audit/
│   ├── serving/
│   ├── monitoring/
│   ├── release/
│   ├── canary/
│   └── rollback/
├── migrations/
└── deployment/
```

## 4. 六项核心资产的归属和流向

| 资产 | 权威路径 | 生产者 | 下游消费者 | 不允许的动作 |
|---|---|---|---|---|
| `BusinessTaskSpec` | `contracts/task/<task>/01_business_task_spec/` | business_product | 数据、算法、Benchmark | 不得绕过业务范围直接造样本 |
| `LabelGuide` | `contracts/task/<task>/02_label_guide/` | business_product | 数据、算法、Benchmark | 争议标签不得静默进入训练集 |
| `DatasetSchema` | `contracts/task/<task>/03_dataset_schema/` | data_engineering | 数据、算法、Benchmark | Schema 未通过校验不得生成快照 |
| `BaselineProtocol` | `contracts/task/<task>/04_baseline_protocol/` | algorithm + qa_benchmark | Base Model、模型实验 | 不得改变输入/输出协议后比较分数 |
| `BenchmarkMetricSpec` | `contracts/task/<task>/05_benchmark_metric_spec/` | qa_benchmark | 评测 Harness、Release Gate | 不得用总体分数掩盖关键切片失败 |
| `BlindTest` | `contracts/task/<task>/06_blind_test/` | qa_benchmark | 受控评测流程 | 训练、调参和普通开发不得读取 gold 内容 |

对应的端到端追踪关系为：

```text
BusinessTaskSpec
      ↓ 定义任务边界
LabelGuide
      ↓ 定义标签与边界
DatasetSchema
      ↓ 约束样本结构与资格
BaselineProtocol
      ↓ 固定比较方法
BenchmarkMetricSpec
      ↓ 固定指标与门禁
BlindTest
      ↓ 独立证明是否达到发布条件
GateDecision / Release Evidence
```

## 5. GitHub 同步时的初始策略

收到仓库地址后，按以下顺序执行：

1. 只读检查仓库 URL、默认分支、现有目录、未提交变更和已有工作流。
2. 保留已有内容；如果现有结构与蓝图冲突，先生成迁移映射，不直接覆盖。
3. 建立上述目录和最小占位文件，先提交结构与契约骨架。
4. 将当前已经冻结或进入冻结流程的 C1-01 资产放入对应权威路径，并生成追踪索引。
5. 配置 `.gitignore`、CODEOWNERS 和 CI 门禁，明确 `blind_test_gold`、原始文件、密钥和模型权重的排除规则。
6. 运行结构检查、JSON Schema 校验、样本资格检查和现有测试后，再提交同步。

默认不执行强制覆盖、历史重写或删除已有文件；如发现需要拆仓，再单独形成迁移提交。

## 6. 首期提交边界

第一批进入 GitHub 的内容：

- 目录骨架、README、贡献规范和安全规范；
- 总体架构、模块边界和 Traceability Matrix；
- 六项核心资产的契约文件、Schema、示例和版本标识；
- C1-01 的非敏感样例、数据清单和质量报告；
- Baseline Harness 接口、Benchmark Harness 接口和 CI 校验脚本；
- blind test 的管理规则与访问边界文档，不包含真实 `blind_test_gold`。

## 7. 十一课教程在工程中的位置

教程不是独立于工程之外的学习材料，而是把十一门课程映射到真实模块、资产和建设里程碑的工程文档。入口位于：

```text
docs/tutorial/README.md
docs/tutorial/COURSE_ALL.md
```

课程顺序保持此前版本：

1. 机器学习到底在学习什么？ → L4 / L8 / L9
2. 神经网络到 Transformer / LLM → L4
3. GPU 环境与开源大模型 → L8 / L9
4. 政府采购数据工程与训练数据集 → L7 / L8
5. SFT + LoRA / QLoRA → L8 / L4
6. RAG、Embedding 与向量检索 → L6
7. Agent、Tool Calling 与工作流 → L2 / L1
8. CPT 与高级领域适配 → L8 / L4
9. Gold Benchmark、评测与可靠性 → L9
10. 推理部署、性能优化与 MLOps → L1 / L9
11. ProcurementLM V1.0 全流程实战 → L0–L9

课程驱动的工程里程碑链：

```text
ProcurementDataset_V0.1
    → ProcurementLM_V0.1
    → ProcurementRAG_V0.1
    → ProcurementAgent_V0.1
    → ProcurementLM_V0.2
    → ProcurementBench_V1
    → ProcurementAI
    → ProcurementLM_V1.0
```

后续需要按课程独立检索、练习和验收时，再将 `COURSE_ALL.md` 拆解为 `lessons/lesson01` 至 `lessons/lesson11`；拆分后的文件不得改变合订原文的课程顺序和版本语义。

首期不进入普通 Git 的内容：

- 未脱敏的采购原始文件；
- `blind_test_gold` 实际样本与标签；
- 模型权重、Adapter、Tokenization 缓存；
- API Key、云端凭据、个人访问令牌；
- 未经裁决的生产反馈和争议案例。
