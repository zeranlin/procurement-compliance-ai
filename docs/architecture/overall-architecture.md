# 总体架构入口

`ProcurementLM_V1.0` 的顶层定义为：

```text
Data + Rules + Policy + Legal RAG + Calculator
    + Compliance LM + Hybrid Engine + Agent
    + Benchmark + Production Governance
```

架构原则：

- AI Project 不等于 Model Project；
- LLM 不等于 Compliance Engine；
- 相关法规不等于适用法规；
- Agent 是工作流编排器，不是专业知识本体；
- Benchmark 从第一天约束全系统；
- 没有 Evidence Trace 和 Release Gate，不产生可发布 Finding。

详细目录边界见 [`repository-structure.md`](./repository-structure.md)，模块契约见 [`../../contracts/README.md`](../../contracts/README.md)。
