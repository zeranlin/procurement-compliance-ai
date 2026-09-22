# C1-01 Gate-B 模型准备包

本目录只冻结本地可验证的模型、运行和教师适配器接口，不包含模型权重、密钥或外部 API 调用。

当前状态：`BLOCKED_PENDING_ARTIFACT_AND_RUNTIME`

- 首选基座：`Qwen/Qwen3.5-4B` post-trained。
- 可选消融：`Qwen/Qwen3.5-4B-Base`。
- text-only、non-thinking、严格裸 JSON。
- 教师模型接口记录为 DeepSeek `deepseek-flash`，当前禁用外部传输。
- Zero-shot、Few-shot、LoRA、QLoRA 仅为模板，正式运行开关保持关闭。

数据、Blind Snapshot、生产 ACL、隔离 evaluator 和实际模型 artifact 就绪前，不得启动正式 Benchmark、Teacher 生成或训练。
