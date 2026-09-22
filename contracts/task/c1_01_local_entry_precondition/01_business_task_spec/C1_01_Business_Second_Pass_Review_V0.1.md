# C1-01 业务第二遍复核与边界裁决记录 V0.1

**复核日**：2026-09-22；**复核方式**：AI 辅助业务第二遍复核，逐条核对已有建议标签与冻结规则；**人工独立双人复核**：尚未完成。
**裁决**：`BR-C101-DEC-03`、`BR-C101-DEC-04`；**冻结对象**：Business Task Spec 与 Label Guide 的业务语义。

**冻结内容 SHA-256**：Business Task Spec `0fa169fa0fa34ef8e702c4cae8e10e89cdce4260aa198f7a45a4a28d5c3a74ab`；Label Guide `9b6352b5f6e400f2ad9ecca1cead4e26b03b3e81b8e6f761276b15ac3ffd67a6`。下游绑定这两个内容哈希；后续如有修正须产生新版本和变更记录。

## 裁决依据及规则

中国政府采购网刊载的财政部典型案例 1 报告将省内已有售后机构或承诺中标后设立作为实质要求，不响应即投标无效；报告同时列出明确的到场与维修时限。二者是不同的 Requirement。业务裁决仅把前者作为地域实体候选，后者保持结果型服务负例。原始招标文件目前未核，案例改写仍是种子。

## 复核结果

- 29 条均核对对象、地域实体／服务结果、投标阶段、竞争后果、子型和范围。
- 03：`NEEDS_CONTEXT/NONE` → 暂定 `MATCH/OTHER_RELATED`；案例身份保留为 `Business Boundary / Disputed Case`，`review_state=DISPUTED`，仍 `HOLD`。
- 21：原 `NEEDS_CONTEXT/NONE` 暂定值留痕，**复核标签置空**，按 `BR-C101-DEC-04` 归入 `Parse Failure / REWORK_SOURCE`；不得混入正常缺上下文切片。
- 25：改写合成句以明确“不要求本地实体”；标签仍 `NO_MATCH/NONE`，并继续与 24 绑定 CF01。
- 其余 26 条主标签与子型确认；全部仍缺独立人工复核／数据 QA 或采购原文证据，不升训练资格。

## BR-C101-DEC-04 补充裁决：ParseFailure != NeedsContext

- `NEEDS_CONTEXT`：原文已经可靠读取，但业务判断所需信息不足；补齐业务定义、引用条款或评分后果后重新判断。
- `REWORK_SOURCE / PARSE_FAILURE`：OCR、附件、页码或表格结构本身不可靠，当前不能形成正式业务标签；修复原件后重新进入 Annotation。
- 文本清楚但事实不够 → `NEEDS_CONTEXT`；原文坏了 → `REWORK_SOURCE`；`REWORK_SOURCE` 不生成正式 target，不进入训练或 `blind_test_gold`。
- `C101-SEED-03` 保持 `Business Boundary / Disputed Case` 与 `HOLD`；`C101-SEED-21` 保持 `Parse Failure / REWORK_SOURCE`，`reviewed_label=null`。

## 与下游的变更单

| 接收方 | 需要核对的变化 | 当前状态 |
|---|---|---|
| 数据组 | `OTHER_RELATED` 已明确包含强制承诺中标后设本地售后机构；21 不生成正式 target，标 `REWORK_SOURCE`；训练准入闸门继续阻断全部种子。 | Dataset Schema V0.1 仍 DRAFT，待数据负责人核对。 |
| 算法组 | 模型任务增加该明确的 OTHER_RELATED 正例；只用允许的输入字段，不接触 blind gold；结果型响应仍为负例。 | Baseline 接口待核对，不自行改变标签。 |
| 测试组 | 更新边界案例切片、Subtype 与缺上下文分母；如 Blind Benchmark 已冻结，上游语义变化需新快照／规范版本，不可静默改旧真值。 | Metric Spec 已 FROZEN，依其版本变更规则处理。 |

## 冻结权限与未完成事项

本轮项目任务发起人已明确要求将两份业务文件从 DRAFT 推至 FROZEN，因此冻结**业务判定语义**。这里未冒充数据、算法、测试负责人的实际签字，也未宣布 Dataset Schema 或 Benchmark 集成已通过。按上游版本依赖，任何团队对新边界提出实质异议，需在新版本中裁决并重新核对样本与评测快照。

## 逐例核对索引

| ID | 复核结果 | 关键核对 |
|---|---|---|
| C101-SEED-01 | `MATCH/DISTANCE_TO_PURCHASER` | 登记地址到采购人的驾车时间参与评分，是地域距离代理变量；保留官方案例改写身份。 |
| C101-SEED-02 | `NO_MATCH/NONE` | 到场分钟数是响应结果，与另一条按地址比较的评分要求拆开。 |
| C101-SEED-03 | 暂定 `MATCH/OTHER_RELATED`；`Business Boundary / Disputed Case` | 两条替代路径均要求当地售后机构；按裁决 BR-C101-DEC-03 暂定命中，但案例保持争议状态并继续 HOLD。 |
| C101-SEED-04 | `NO_MATCH/NONE` | 到场和维修时限是服务结果；不得把同案另一地域条款的结论转移到此要求。 |
| C101-SEED-05 | `NO_MATCH/NONE` | 面积、社保人数、销售额属规模财务因素；虽同为被处理案例，不属于 C1-01。 |
| C101-SEED-06 | `MATCH/SUPPLIER_REGISTRATION_LOCATION` | 本市注册地直接决定资格，条件与后果均明确。 |
| C101-SEED-07 | `MATCH/SUPPLIER_REGISTRATION_LOCATION` | 本区注册地作为加分条件，外地仍可投标不妨碍候选命中。 |
| C101-SEED-08 | `MATCH/DISTANCE_TO_PURCHASER` | 既有办公地点距采购人的半径决定分数。 |
| C101-SEED-09 | `MATCH/DISTANCE_TO_PURCHASER` | 既有营业地点的地域半径决定投标有效性。 |
| C101-SEED-10 | `MATCH/PREEXISTING_LOCAL_BRANCH` | 投标截止前已设分公司及登记证明，是前置实体门槛。 |
| C101-SEED-11 | `MATCH/PREEXISTING_LOCAL_BRANCH` | 既有地区分支机构形成评分优势。 |
| C101-SEED-12 | `MATCH/SUPPLIER_REGISTRATION_LOCATION` | 营业执照住所栏即注册地的同义表达，作为入围条件。 |
| C101-SEED-13 | `NO_MATCH/NONE` | 这是采购项目地点，未约束供应商身份。 |
| C101-SEED-14 | `NO_MATCH/NONE` | 要求披露注册地址，不限定其行政区域。 |
| C101-SEED-15 | `NO_MATCH/NONE` | 明确可用远程、派驻或合作维修，且无本地机构义务。 |
| C101-SEED-16 | `NO_MATCH/NONE` | 评分依据是可兑现的到场时效，明确不考察营业地点。 |
| C101-SEED-17 | `NO_MATCH/NONE` | 注册资本并非注册地；应移交其他任务切片，不误报 C1-01。 |
| C101-SEED-18 | `NO_MATCH/NONE` | 中标后派驻人员属于履约安排，不要求投标时已有实体或强制承诺设实体。 |
| C101-SEED-19 | `NEEDS_CONTEXT/NONE` | “本地化服务能力”未定义，实体义务及评审后果仍需补证。 |
| C101-SEED-20 | `NEEDS_CONTEXT/NONE` | 引用的资格条件第七项缺失，无法还原具体要求。 |
| C101-SEED-21 | `SOURCE_REWORK_REQUIRED`；`Parse Failure / REWORK_SOURCE` | OCR 和附表缺失导致输入本身不可靠；按 BR-C101-DEC-04 撤销正式复核标签，转源件修复。 |
| C101-SEED-22 | `NEEDS_CONTEXT/NONE` | “服务点”性质和评分条件缺失，可能是实体限制也可能仅服务安排。 |
| C101-SEED-23 | `NEEDS_CONTEXT/NONE` | 具体法定例外依据未附，标注不能代替适用性核查。 |
| C101-SEED-24 | `MATCH/PREEXISTING_LOCAL_BRANCH` | 反事实 CF01 正侧：投标时已有分公司为准入门槛。 |
| C101-SEED-25 | `NO_MATCH/NONE` | 反事实 CF01 负侧：仅承诺服务结果且无须设本地实体；与新裁决的强制设机构情形分开。 |
| C101-SEED-26 | `MATCH/DISTANCE_TO_PURCHASER` | 反事实 CF02 正侧：既有办公地点半径直接加分。 |
| C101-SEED-27 | `NO_MATCH/NONE` | 反事实 CF02 负侧：到场时效加分，不取企业既有地址。 |
| C101-SEED-28 | `MATCH/SUPPLIER_REGISTRATION_LOCATION` | 反事实 CF03 正侧：本市注册地直接加分。 |
| C101-SEED-29 | `NO_MATCH/NONE` | 反事实 CF03 负侧：只要求如实登记地址且不限定地域。 |
