# 政府采购 AI / ML 实战教程

本目录收录此前形成的十一门课程。教程服务于 `ProcurementLM_V1.0` 工程建设，不是泛化的机器学习教材；每一课都对应真实模块、工程资产或验收门禁。

## 教程文件

- [`COURSE_ALL.md`](./COURSE_ALL.md)：第一课至第十一课完整合订内容。
- `lessons/`：后续按课程拆分的 canonical 文档目录；拆分时保持合订稿的原始顺序和版本语义。

## 十一课导航

| 课次 | 课程 | 主要工程映射 |
|---|---|---|
| 1 | 机器学习到底在学习什么？ | Compliance LM、训练、Benchmark 的学习/泛化边界 |
| 2 | 神经网络到 Transformer / LLM | Compliance LM 的模型底层机制 |
| 3 | GPU 环境与开源大模型 | 训练、推理和模型运行基础设施 |
| 4 | 政府采购数据工程与训练数据集 | Document/Data、Schema、Label、Evidence、Dataset |
| 5 | SFT + LoRA / QLoRA | 领域监督微调与 PEFT |
| 6 | RAG、Embedding 与向量检索 | Policy Registry、Legal RAG、证据召回与引用 |
| 7 | Agent、Tool Calling 与工作流 | Agent、工具路由、状态、恢复和人工回路 |
| 8 | CPT 与高级领域适配 | 领域分布适配、能力保持和训练边界 |
| 9 | Gold Benchmark、评测与可靠性 | Gold、切片、红队、回归和 Release Gate |
| 10 | 推理部署、性能优化与 MLOps | Serving、性能、监控、发布和回滚 |
| 11 | ProcurementLM V1.0 全流程实战 | 产品、数据、规则、法规、模型、Agent、Benchmark、生产治理的总集成 |

## 教程与工程建设顺序

```text
Schema
  → Gold Benchmark
  → Gold Data / Decision Boundary
  → Compliance LM
  → Policy / Legal RAG
  → Hybrid Compliance Engine
  → Compliance Agent
  → Production Governance
```

对应版本里程碑：

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

## 使用规则

1. 课程中的工程字段、状态值、流程节点和 Schema 标识保留稳定英文名称，并配套中文业务释义。
2. 教程内容不能替代 `contracts/` 下的正式契约；正式接口、Schema、门禁和权限以 `contracts/` 与 `docs/governance/` 为准。
3. 第 9 课的 Benchmark 内容必须遵守 `blind_test_gold` 访问边界；教程可以讲方法和规则，不包含真实盲测金标。
4. 第 11 课是系统集成课，不能被解释为跳过前置 Schema、数据质量和独立 Benchmark。
