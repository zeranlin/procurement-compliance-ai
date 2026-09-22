# 数据分类

| 类别 | 示例 | Git 处理 |
|---|---|---|
| PUBLIC | 架构、协议、脱敏示例 | 可提交 |
| INTERNAL | 内部规范、非敏感报告 | 私有仓库提交前审查 |
| RESTRICTED | 原始采购文件、未脱敏证据 | 外部受控存储，不提交 |
| BLIND_GOLD | 盲测输入与金标 | 测试组独占，不提交普通仓库 |
| SECRET | Token、密钥、凭据 | 只进 Secret Manager |
