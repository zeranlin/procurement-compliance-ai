# 贡献规范

## 基本要求

1. 任何跨模块改动必须说明影响的契约、数据快照和评测切片。
2. 共享 Contract 必须包含中文业务语义、示例、边界、失败表达和契约测试。
3. 不得把 Prompt 代替 Rule Registry，不得把模型自由文本直接当作 Finding。
4. 不得修改或读取真实 `blind_test_gold` 来调参或训练。
5. 代码、Schema、数据清单和评测报告必须带版本信息。

## Pull Request 最低检查

- [ ] 通过 `make validate`；
- [ ] 没有提交密钥、原始采购文件、模型权重或盲测金标；
- [ ] 相关 Contract Test 已补充或说明不适用原因；
- [ ] 变更涉及的 Benchmark Slice 已登记；
- [ ] 没有绕过人工复核、Evidence Gate 或 Release Gate。
