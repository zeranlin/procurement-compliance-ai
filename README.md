# Procurement Compliance AI

政府采购采购文件合规审查垂直领域 AI 工程。

## 当前定位

本仓库采用 **Monorepo + 八个逻辑模块边界**，目标不是单独训练一个模型，而是建设可被 WorkBuddy、公司 Agent、Web/API 复用的专业能力平台：

```text
Data + Rules + Policy + Legal RAG + Calculator
    + Compliance LM + Hybrid Engine + Agent
    + Benchmark + Production Governance
```

当前首期范围为 `C1-01_LOCAL_ENTRY_PRECONDITION` 最小闭环，数据标签仍需严格遵守各资产中的版本和资格状态。`INTERNAL_SILVER` 不等于 `GOLD`，`PASS_DEMO` 不等于 `PRODUCTION_READY`。

## 目录入口

- `docs/architecture/`：总体架构、模块边界和 C1-01 Demo 蓝图。
- `docs/tutorial/`：此前形成的十一课工程教程。
- `contracts/`：共享契约与 C1-01 六项核心资产。
- `modules/`：Data、Policy、Rules、Model、Engine、Agent、Benchmark、Platform 八个逻辑模块。
- `datasets/`：数据清单、快照和受控指针；不存放原始敏感文件和盲测金标。
- `experiments/`：Model Only、Agent Swap、Full System 等四类验证实验。

## 首期验证

```bash
make validate
```

验证内容包括目录结构、契约 JSON、敏感文件排除规则和 Git 工作区基本卫生。

## 安全边界

- `blind_test_gold` 只由测试与评测责任方管理。
- 训练、调参和普通开发流程不得读取真实盲测金标。
- 原始采购文件、模型权重、Adapter、密钥和访问令牌不得提交。
- 所有 Finding 必须能够追溯到采购证据和法规/政策证据。

## 版本状态

当前为首期工程骨架与 C1-01 内部协作版本。正式发布必须通过独立 Benchmark、Release Gate 和治理审批。
