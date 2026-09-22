# C1-01 Gate-B QA 工具

本目录只提供 Gate-B 的可执行流程和测试夹具，不修改 Gate-A Contract。

## 组件

- `benchmark_snapshot.py`：读取 Dataset Schema V0.2 记录，只允许 `TRAIN_ELIGIBLE` 的 DEV 和 `BENCHMARK_CANDIDATE` 的 Blind 候选通过；输出只含模型可见 input，不生成 Gold。
- `runtime_acl.py`：服务账号、角色、资源和动作的最小权限矩阵，以及审计日志和拒绝探针。
- `isolated_evaluator.py`：QA 隔离评测入口，严格校验 prediction ID 对齐，保留 INVALID 并计入结构化输出分母。
- `gate_b_regression.py`：合成输入回归；Gold 只在临时目录生成，覆盖三类状态、四个 MATCH subtype、Hard Negative、反事实 Pair、INVALID、重复/缺失/未知 ID 和 ACL 拒绝。

真实 `blind_test_gold`、真实预测、原始采购文件和模型权重不进入仓库。
