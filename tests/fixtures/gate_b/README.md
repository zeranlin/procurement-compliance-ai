# Gate-B 合成盲测输入

`C1_01_Synthetic_Blind_Input_V0.1.jsonl` 只包含模型可见输入，不包含 target、切片、泄漏组或 Gold。

该文件用于验证 Snapshot/隔离评测/ID 对齐流程，不代表真实 Benchmark Snapshot，也不宣称 `N>=50`。测试脚本在临时目录中生成合成 Gold，运行结束后删除，不写入仓库。
