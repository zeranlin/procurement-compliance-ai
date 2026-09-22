# ProcurementComplianceLM — ALG-PATCH-01 交付包

本包汇总 03-算法组本轮 Protocol Integration 交付物。

## 冻结结论

- Protocol：`C1_01_Baseline_Protocol_V0.2.1`
- 状态：`FROZEN`
- MetricSpec：`C1_01_Benchmark_Metric_Spec_V0.2`
- MetricSpec SHA-256：`cb443a64178fb894d751bc02dbc6fc9f142e33a9e2130a121ab9e0a881f64a7d`
- DatasetSchema：`C1_01_Dataset_Schema_V0.2`
- 回归：15/15 PASS
- Stub smoke：PASS
- 模型 / DEV Benchmark / Blind Test：未运行

## 目录

- `protocol/`：协议正文、lock、Preflight、依赖 Registry、Run Manifest 模板、回归报告、Freeze Record 和输出 Schema。
- `harness/`：完整 `C1_01_Baseline_Harness_V0.2.1` 目录及其 ZIP 包。
- `reports/`：Preflight 依赖回归 JSON 和 Stub smoke JSON。
