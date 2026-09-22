# C1-01 Blind Test Management Rules V0.1

**文档状态**：`FROZEN`  
**生效日期**：2026-09-22  
**责任团队**：测试与评测组  
**适用对象**：C1-01 Benchmark Snapshot、算法组模型提交、测试组评分与报告发布

## 1. 目的与边界

本规则用于保证 Blind Test 的结果可重复、不可调参污染、可审计，并保证模型团队不能通过访问真值或真值派生信息间接优化。

本规则冻结的是管理流程和操作边界；它不改变 `C1_01_Label_Guide_V0.1` 的业务语义，也不把当前 `INTERNAL_SILVER` 升级为独立专家 Gold。`blind_test_gold` 中的“gold”是运行时隐藏参考的工程名称。

## 2. 角色与责任

| 角色 | 允许负责 | 明确禁止 |
|---|---|---|
| 测试负责人 | 冻结 Snapshot、指标、Gate、评分流程和发布决定 | 为模型通过而改真值或回溯改阈值 |
| 测试操作员 | 在隔离评测环境加载隐藏真值、运行固定评测器、生成报告 | 将真值复制到普通工作区、日志、报告或调试输出 |
| 业务/产品组 | 提供业务边界、复核争议、在冻结前参与标签确认 | 直接读取冻结后的 `blind_test_gold`；按模型结果改标签 |
| 数据工程组 | 完成来源、Schema、去重、泄漏和分组检查；向测试组交接候选数据 | 在冻结后修改 Benchmark 成员或访问隐藏真值 |
| 算法组 | 使用盲测输入生成预测并提交模型/运行清单 | 访问真值、运行 `--qa-blind`、通过盲测结果迭代提示词或标签 |
| 项目负责人 | 在真值打开前批准规则和 Gate；处理升级事项 | 绕过测试组直接取真值或要求临时降低门槛 |
| 平台/运维 | 提供存储、隔离、审计和备份能力 | 以平台权限读取或导出真值内容 |

测试组是 Benchmark 的最终所有者；算法组不是 Benchmark Owner。

## 3. Snapshot 结构与版本标识

每个可运行 Snapshot 必须有不可变 ID、版本、内容哈希和责任人。标准结构为：

```text
C1_01_BenchmarkSnapshot_V0.1/
├── blind_test_input.jsonl       # 算法组可见
├── blind_test_gold.jsonl        # 测试组独占
├── benchmark_spec.md
├── metric_spec.json
├── manifest.json
├── leakage_groups.json          # 测试组保存；不向算法组发布
└── freeze_record.json
```

算法组交付包不得包含 `blind_test_gold.jsonl`、`leakage_groups.json`、金标元数据或可由元数据重建切片的字段。

`manifest.json` 至少记录：

```text
snapshot_id
task_id
schema_version
label_guide_version
metric_spec_version
input_file_hash
gold_file_hash
evaluator_version
sample_count
split_counts
leakage_check_result
counterfactual_check_result
owner
freeze_time
```

## 4. 生命周期

### 4.1 候选收集与资格检查

测试组接收数据工程组交付的候选记录，逐项检查：

- 来源和文档版本可追溯；
- Requirement 可独立判断；
- 标签、子型、阶段、证据和缺失问题满足 Schema；
- 双人标注分歧已处理，未处理记录保持 `HOLD` 或 `DISPUTED`；
- `leakage_group_id` 已分配；
- 同项目/模板家族、近重复和反事实对可以审计；
- Train、Dev、Blind Test 不发生项目级泄漏；
- `INTERNAL_SILVER` 标签权威字段不被抹除。

不满足条件的记录不得进入本次 Blind Gold。`BENCHMARK_CANDIDATE` 只是候选状态，不等于正式 Gold。

### 4.2 冻结前联合确认

在冻结前完成一次联合检查，但不向算法组开放隐藏真值：

1. 测试组确认样本数、切片覆盖和评测器输入输出；
2. 数据工程组确认 split、重复、泄漏组和反事实对；
3. 业务/产品组确认边界案例可测，争议项已记录；
4. 算法组确认输入协议和预测协议可执行；
5. 项目负责人和测试负责人确认 Metric Spec 与 Gate 已预注册。

以上确认必须写入 `freeze_record.json`，包括版本、哈希、签署角色和时间。

### 4.3 冻结与锁定

冻结动作完成后：

- `blind_test_input.jsonl`、`blind_test_gold.jsonl`、切片清单和指标规范均只读；
- 任何变更都生成新的 Snapshot ID，不得原地覆盖；
- 任何人不得根据模型输出调整样本、标签、切片或 Gate；
- 测试组撤销数据工程组、业务组和算法组对隐藏真值的访问；
- 算法组只接收盲测输入、输出契约和提交说明。

### 4.4 模型提交

每次提交必须有唯一 `run_id`，包括：

```text
model_version
base_model_and_revision
code_commit
prompt_or_template_hash
tokenizer_revision
inference_framework_version
generation_config
input_snapshot_id
prediction_file_hash
submitter
submit_time
```

提交文件必须：

- 每个 `sample_id` 恰好一条预测；
- 符合结构化输出协议；
- 不附带真值、切片、泄漏组、人工标签或额外调试列；
- 固定模型、代码、提示词和生成配置；
- 不以测试组返回的指标结果为依据进行同一 Snapshot 的自适应调参。

提交校验失败时，测试组只能返回协议级错误，例如缺 ID、重复 ID、JSON 无法解析；不得返回金标标签、逐例对错或可推断真值的提示。修复后须以新的 `run_id` 重新提交。

### 4.5 评分与结果发布

测试组在隔离环境中完成：

1. 预测与真值的精确 ID 对齐；
2. 按 `C1_01_Benchmark_Metric_Spec_V0.1` 运行固定评测器；
3. 保存完整审计日志、错误码和内容哈希；
4. 进行必要的人工 Evidence 核查；
5. 生成整体指标、切片指标、基线比较和 Gate Decision；
6. 由测试负责人和项目负责人签署后发布。

正式盲测过程中不提供中间分数、逐例真值、错误样例的金标答案或切片成员反馈。运行关闭后，按发布审批向算法组提供聚合报告和经过批准的 Error Analysis；任何发布内容都不能包含原始 `blind_test_gold` 或可重建其完整内容的导出。

## 5. 评测期间的禁止行为

以下行为一律视为 Blind Test 违规：

- 将 `blind_test_gold` 或其任何字段放入训练集、few-shot 示例、提示词、验证集、回归集或向量库；
- 把真值复制到模型日志、异常堆栈、缓存、检查点、实验追踪或本地工作区；
- 通过文件名、切片名、`leakage_group_id`、样本顺序或统计量推断隐藏标签；
- 让算法组执行 `--qa-blind` 或读取测试组的隐藏评测目录；
- 在盲测结果出来后修改样本、标签、切片、指标公式或 Gate 阈值并复用原 Snapshot；
- 把“协议校验通过”误称为“模型通过评测”；
- 以任何外部同步、截图、手工复制或口头反馈方式泄漏逐例真值。

## 6. 变更、缺陷与事故

### 6.1 冻结前

发现数据缺陷、标签争议或指标错误时，可以在 `freeze_record` 前修订，但必须：

- 记录原因、影响范围、原版本和新版本；
- 重跑 Schema、重复、泄漏和反事实检查；
- 重新确认 Metric Spec 和 Gate；
- 不得保留旧路径下的混合文件。

### 6.2 冻结后

发现真值、切片或评测器缺陷时：

1. 立即将当前 Snapshot 标记为 `QUARANTINED`，暂停发布；
2. 保留原文件、哈希、访问日志和已产生的结果；
3. 由测试负责人判定是重算、作废还是新建 Snapshot；
4. 修复必须生成新版本，并重新预注册 Gate；
5. 不得删除或覆盖已经发布的历史结果。

发现疑似权限越界时，先撤销相关主体访问，再按 `C1_01_Blind_Test_Gold_Access_Boundary_V0.1` 处理事故；不得为了继续跑测而继续扩大访问范围。

## 7. 产物与留痕

测试组至少保留：

```text
freeze_record.json
evaluation_run_manifest.json
EvaluationMetrics_V0.1.json
EvaluationReport_V0.1.html
ErrorAnalysis_V0.1.md
GateDecision_V0.1.json
access_audit.jsonl
incident_log.jsonl（如有）
```

每个产物必须带 Snapshot ID、运行 ID、版本和哈希。隐藏真值仅允许出现在测试组受控存储和隔离评测运行的受控输入中。

## 8. 关闭条件

一次 Blind Test 只有在以下条件全部满足后才可关闭：

- 预测集与真值集 ID 完全对齐；
- 输出格式和证据定位校验完成；
- 评测器、Metric Spec、Snapshot 版本和哈希已记录；
- 关键切片和 Hard Negative 均有结果；
- 无未处置的访问异常或泄漏疑点；
- Gate Decision 已由授权角色签署；
- 发布给算法组的结果不包含未经批准的真值内容。

## 9. 冻结验收

- [ ] 角色、权限和交接路径已确认；
- [ ] Snapshot 目录和清单已生成；
- [ ] Freeze Record 已写入版本、哈希和责任人；
- [ ] Blind Gold 已从算法组可见目录移除；
- [ ] 指标与 Gate 已在开测前冻结；
- [ ] 违规、缺陷和事故处理路径已演练一次。

