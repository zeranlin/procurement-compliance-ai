# Blind Test 管理入口

真实盲测金标不进入普通 Git 工作区。仓库只保存：

- 管理规则；
- 访问边界；
- Snapshot/Manifest 指针；
- 评测接口和结果索引。

具体规则见 `contracts/task/c1_01_local_entry_precondition/06_blind_test/`。
