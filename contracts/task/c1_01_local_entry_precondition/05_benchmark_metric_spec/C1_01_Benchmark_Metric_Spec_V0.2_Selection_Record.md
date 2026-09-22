# C1-01 BenchmarkMetricSpec V0.2 选择记录

**任务**：C1-01_LOCAL_ENTRY_PRECONDITION  
**验证编号**：QA-REVERIFY-GATE-A-01  
**记录时间**：2026-09-22T14:27:06Z  
**Owner**：04-测试与评测组

## 1. 对比对象

本轮发现两个内容不同、但文件名同为 `C1_01_Benchmark_Metric_Spec_V0.2.md` 的候选：

| 候选 | SHA-256 | 链路状态 |
|---|---|---|
| 算法分支顶层候选 | `18b73e559485317ee0883486fd14923196ca017d862d6797209da96b53a5046c` | 未被 Baseline lock、Dependency Registry、Freeze Manifest 或 Gate-A evidence 引用 |
| 正式冻结候选 | `cb443a64178fb894d751bc02dbc6fc9f142e33a9e2130a121ab9e0a881f64a7d` | 被 Baseline lock、Dependency Registry、Freeze Manifest、Gate-A reports 和 harness deps 一致引用 |

## 2. 选择结论

本项目唯一正式依赖为：

```text
C1_01_Benchmark_Metric_Spec_V0.2
sha256 = cb443a64178fb894d751bc02dbc6fc9f142e33a9e2130a121ab9e0a881f64a7d
```

算法分支候选 `18b73...` 不进入本轮正式 hash chain，也不作为 Gate-A 验收依据。选择依据是可追溯的冻结链绑定，而不是通过修改业务语义或降低指标门槛。

## 3. 影响边界

- 未修改 BusinessTaskSpec、LabelGuide、DatasetSchema、BaselineProtocol 或 Metric Gate。
- 本记录只固定候选选择和证据链，不代表 Gate-B Benchmark Ready。
- 最终结论仍为 `GATE-A_REVERIFY_PASS`，等待项目负责人执行 FINAL CONTRACT FREEZE REVIEW。
