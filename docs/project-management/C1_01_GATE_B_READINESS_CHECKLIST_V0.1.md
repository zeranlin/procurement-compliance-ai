# C1-01 Gate-B Readiness Checklist V0.1

**基线**：Gate-A 最终冻结 `67948a8`  
**当前状态**：`NOT_READY / REVIEW_DEFERRED`
**下一评审**：Gate-B Data / Benchmark Readiness Review  
**规则**：未有证据不得勾选 PASS；计划、候选和运行结果必须分开记录。

## 1. 数据就绪

| ID | 检查项 | 必需证据 | Owner | 状态 |
|---|---|---|---|---|
| D-B01 | Gate-A 绑定资产未漂移 | 六项主契约 + Blind Governance hash 对照 | PM/04 | PASS（Gate-A） |
| D-B02 | Seed/Schema 基线可重现 | Seed `fa3db35e...`、Schema `484cb50e...`、29/29、`integrity_errors=[]` | 02 | PASS（Gate-A） |
| D-B03 | 候选数据来源可追溯 | source、document/version、evidence、lineage report | 02 | NOT_STARTED |
| D-B04 | Train/Dev/Benchmark Candidate 角色合法 | split manifest、role allowlist、数量和 hash | 02 | NOT_STARTED |
| D-B05 | pair/leakage 不跨 split | pair report、leakage report、项目/模板族检查 | 02 | NOT_STARTED |
| D-B06 | `DISPUTED`/`HOLD`/`REWORK_SOURCE` 隔离 | 过滤结果、`C101-SEED-03/21` 专项核对 | 02/04 | NOT_STARTED |
| D-B07 | Benchmark Candidate 达到预注册规模与覆盖 | sample count、切片覆盖、hard negative、counterfactual 覆盖 | 02/04 | NOT_STARTED |
| D-B08 | 数据包签署 | Data Manifest、输入 hash、Owner、时间、签名 | 02 | NOT_STARTED |

### 1.1 复核延期治理

| ID | 检查项 | 必需证据 | Owner | 状态 |
|---|---|---|---|---|
| R-B01 | 候选逐条 Codex 暂代复核工作项关闭 | Owner 延期决策、聚合计数、状态边界 | PM/01 | COMPLETE_WITH_DEFERRED_REVIEW |
| R-B02 | 402 条未复核候选保持隔离 | `PENDING_01_CODEX_REVIEW`、`label=null`、三项资格均为 false | 01/02 | QUEUED_NOT_REVIEWED |
| R-B03 | 人工专家二审 | 专家 Owner、逐条结论、证据与版本化回归报告 | 专家团队/01/04 | DEFERRED_UNTIL_EXPERT_TEAM_ONBOARDING |
| R-B04 | 6 个旧版文档解析阻塞隔离 | `PARSER_BLOCKED` 清单与后续解析修复记录 | 02/01 | PARSER_BLOCKED |

`R-B01` 的完成只表示延期决策已执行，不表示 `R-B02` 或 `R-B03` PASS。402 条记录不得进入正式训练、DEV、Benchmark 或 Gold。

## 2. Benchmark Snapshot 与 ACL

| ID | 检查项 | 必需证据 | Owner | 状态 |
|---|---|---|---|---|
| B-B01 | Snapshot 有不可变 ID | `snapshot_id`、版本、freeze record | 04 | NOT_STARTED |
| B-B02 | Input/Gold 物理隔离 | `blind_test_input` 与 `blind_test_gold` 存储、挂载、路径清单 | 04 | NOT_STARTED |
| B-B03 | Gold 无普通工作区副本 | 搜索、备份、缓存和导出检查；不得回传 Gold 内容 | 04 | NOT_STARTED |
| B-B04 | Snapshot Manifest 完整 | input/gold/evaluator/metric hash、split、leakage、counterfactual、Owner | 04 | NOT_STARTED |
| B-B05 | Runtime ACL 正向/拒绝场景 | QA 账号可读；02/03/01/PM/运维拒绝；审计日志齐全 | 04 | NOT_STARTED |
| B-B06 | Isolated Evaluator 可复现 | evaluator version/hash、依赖、运行命令、输出 schema | 04 | NOT_STARTED |
| B-B07 | Metric/Gate 预注册 | MetricSpec、阈值、分母规则、变更记录 | 04 | PASS（Gate-A Contract）；Gate-B Runtime NOT_STARTED |
| B-B08 | Blind 提交流程固定 | run_id、model/revision、code、prompt、tokenizer、generation config、prediction hash | 04/03 | NOT_STARTED |

## 3. 模型环境就绪（不等于模型运行）

| ID | 检查项 | 必需证据 | Owner | 状态 |
|---|---|---|---|---|
| E-B01 | Student/Base 候选已登记 | 模型选择记录、license/访问方式、revision 字段 | 03/PM | PLAN_ONLY |
| E-B02 | Qwen 环境可复现 | Python/Transformers/runtime、tokenizer、hardware、driver、revision manifest | 03 | NOT_STARTED |
| E-B03 | 输入/输出适配器固定 | allowlisted input、冻结 output contract、代码 commit/hash | 03 | NOT_STARTED |
| E-B04 | generation config 固定 | temperature、seed、max tokens、thinking/non-thinking 设置 | 03 | NOT_STARTED |
| E-B05 | 环境级 smoke 可运行 | 依赖导入、配置解析、协议 adapter smoke；不得调用模型或读取 Gold | 03 | NOT_STARTED |
| E-B06 | 运行审计可追溯 | run manifest 模板、日志脱敏、输出路径和权限 | 03/04 | NOT_STARTED |

## 4. 治理与授权

| ID | 检查项 | 必需证据 | Owner | 状态 |
|---|---|---|---|---|
| G-B01 | Gate-B Readiness Review 完成 | 02/03/04/PM 联合矩阵 | PM | NOT_STARTED |
| G-B02 | `benchmark_ready` 明确 | `contract_ready=true` 不得替代 `benchmark_ready` | 04/PM | NOT_STARTED |
| G-B03 | Base Zero/Few-shot 授权 | Gate-B PASS 后单独授权记录 | PM | BLOCKED |
| G-B04 | Training Decision 授权 | Base 结果、DEV 误差分析、回归后单独记录 | PM | BLOCKED |
| G-B05 | LoRA/QLoRA 授权 | Training Decision=GO、数据与评测快照锁定 | PM/03 | BLOCKED |
| G-B06 | Blind Benchmark 授权 | Snapshot、ACL、evaluator、提交规则全部 PASS | PM/04 | BLOCKED |

## 5. Gate-B 退出判定

```text
PASS  = 所有 D-B01~D-B08、B-B01~B-B08、E-B01~E-B06、G-B01~G-B02 有证据并签署
FAIL  = 任一 P0 安全/泄漏/版本/分母问题，或证据不一致
PENDING = 证据缺失但尚未形成失败结论
```

Gate-B PASS 后仅能解锁 Base Model Zero/Few-shot 申请；不会自动授权 Training、Fine-tune 或 Blind Benchmark。

## 6. 当前结果

```text
DATA_READY = FALSE
SNAPSHOT_READY = FALSE
ACL_READY = FALSE
MODEL_ENV_READY = FALSE
GATE_B_READY = FALSE
CODEX_REVIEW_TASK = COMPLETE_WITH_DEFERRED_REVIEW
EXPERT_REVIEW = DEFERRED_UNTIL_EXPERT_TEAM_ONBOARDING
REVIEWED_CANDIDATES = 1
PENDING_CANDIDATES = 402
PARSER_BLOCKED_DOCUMENTS = 6
BENCHMARK_READY = FALSE
TRAINING_AUTHORIZED = FALSE
BASE_MODEL = BLOCKED
FINE_TUNE = BLOCKED
BLIND_BENCHMARK = BLOCKED
```
