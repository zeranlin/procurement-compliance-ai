# 02 数据工程组：采购文件设置差别歧视条款专项模型

状态：`SOURCE_PERMISSION_AND_VERSION_HOLD`（2026-09-28）。这是一套可运行的数据契约和来源核验产物，尚无可进入 TRAIN/DEV 的真实 AI Silver。旧 C1-01 的 309/99 Pilot、`MATCH/OTHER_RELATED` 标签和切分均未迁入本轮。

## 契约与权限

- [contract_binding.json](reports/contract_binding.json) 锁定 V0.3 业务需求、V0.2 输入规范和 01 组六份 V0.1 文件的 SHA-256；[rule_registry.json](rule_registry.json) 从 01-01/01-02 原文机械生成 7 类、22 表现形式、64 子点及固定依据映射。02 不改规则含义。总控告知 00 组已复验通过业务接口返工，该结论未附独立复验文件；原始附件未逐字核验，7.4 处理依据为 `null/待原始附件核实`，01 的 64 卡、320 示例逐项两遍历史留痕尚不完整。
- 本地用户提供目录中的 Word 文件可做来源盘点与局部定位；逐份公开发布来源、内部训练许可、更正/答疑关系和当前有效版本未被确认。`source_version_ledger.jsonl` 的每行都明确写 `HOLD`，发布日期、地区、权限和有效性未知时保持 `null/UNKNOWN`，文件名提取的项目名/品目仅是未核提示。对本地可读不推断出训练许可。
- 原始文件和真实条款文本没有复制进仓库。逐份台账及两个从原件抽取的 HOLD 审查单元只在 `/private/tmp/procurement-discriminatory-terms-02/`。台账哈希和路径见 [source_quality_report.json](reports/source_quality_report.json)。
- [官网小批量试采记录](reports/official_source_pilot_2026-09-28.md)另核对 V0.2 下载包 8/8 清单文件，并记录 3 份官网 PDF 原件、1 个未取得正式附件的深圳项目及两个未标注的原子线索；它们不改变本目录的 168 份本地来源台账与 0 TRAIN/0 DEV 结论。

## 审查数据流

`review_schema.json` 分开约束 `discover`、`judge` 与单元级 `scope_review`。`discover` 只有候选和补证请求；`judge` 必须指向 64 个正式 `rule_id` 中的一个，仅允许“发现/未发现/需要补充材料”；范围外的 `rule_id=null`、`case_type=null` 且 `judgments=[]`。同一要求可分多个 `judge` 调用，再按单元汇总。

模型输入只有项目概况、有效文件、章节、一个原子要求和按需证据。`case_type`、状态、教师标签、预期答案、处理依据文字均不属于输入。八种补证请求须写具体材料、阻碍要件、检索范围与有效时间。服务端记录 `review_revision`，保留请求、检索失败和每个版本的输出；首次补证 `case_type=null`，合理检索仍缺才是“无法判断案例”。两遍 Codex 自动复核若用于真实 AI Silver，须分别留下正向要件与逆向反证记录，分歧不能强判。

六步审查路径落在记录字段和校验上：文档章节及 XML 位置 → 版本/条款效力 → 父条款与原子要求 → 投标前竞争作用或中标后履约及后果 → 逐要件/例外 → 连续原文证据或具体缺口。真实 HOLD 示例的评分行与后续承诺通过 `linked_unit_ids` 连接；服务网点不自动等于分支机构，也不因评分语句单独形成违规结论。

## 验收及移交

从仓库根目录运行：

```bash
python3 contracts/task/procurement_document_discriminatory_terms/02_data/build_artifacts.py
python3 contracts/task/procurement_document_discriminatory_terms/02_data/fixtures/build_synthetic.py
python3 contracts/task/procurement_document_discriminatory_terms/02_data/validate_artifacts.py
```

校验器使用本环境已安装的 `jsonschema>=4`。构建脚本锁定 8 份契约的哈希；校验器复核 168 份本地文件的实际 SHA-256、两个 HOLD 单元的原件段落和 XML 路径、合成事件的 Schema/跨字段/证据连续位置、补证及版本链。`fixtures/synthetic_review_events.jsonl` 是 9 个纯合成情境、13 个事件，含两子点候选发现和带来源/有效时间的项目事实补证，仅用于结构验收，不能充作真实覆盖或 Gold。

[real_coverage_matrix.json](reports/real_coverage_matrix.json) 明示 64×5=320 个真实覆盖格目前全空；[split_and_leakage_report.json](reports/split_and_leakage_report.json) 记录 0 TRAIN/0 DEV。因为无可用真实样本，跨 split 泄漏校验是“不适用”，不能将其解释成已证明切分安全。04 独立掌管 Blind；当前 `training_authorized=false`、`benchmark_ready=false`、`gold_eligible=false`。

后续移交所需条件：逐份明确许可与内部训练用途、核对官方发布及更正后有效版本、获取完整评分/证明栏与必要外部事实；再对合格来源按项目家族和版本关系整体切分，执行真实近重复检查及两遍 Codex AI Silver。原始附件或 7.4 依据发生变化时向 01 提变更请求，02 不静默改规则。
