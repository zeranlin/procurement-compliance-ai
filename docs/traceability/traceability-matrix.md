# 端到端追踪矩阵入口

```text
BusinessTaskSpec
  → LabelGuide
  → DatasetSchema
  → BaselineProtocol
  → BenchmarkMetricSpec
  → BlindTest
  → GateDecision / Release Evidence
```

当前 C1-01 对应资产位于 `contracts/task/c1_01_local_entry_precondition/`。每一项资产必须保留版本、状态、生产者、消费者、验证方式和禁止用途。
