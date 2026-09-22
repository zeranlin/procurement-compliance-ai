# C1-01 标注种子案例包 V0.1

**状态**：业务边界已冻结、29 条已完成 AI 辅助第二遍内部业务复核；仍为 `INTERNAL_SILVER` 待验种子，尚未达到独立人工双人复核、采购原文验证和数据 QA 准入。
**任务 ID**：`C1-01_LOCAL_ENTRY_PRECONDITION`；对应 `BR_C1_01_Business_Task_Spec_V0.1.md` 与 `C1_01_Label_Guide_V0.1.md`。
**复核后分布**：12 `MATCH`、12 `NO_MATCH`、4 个可作为正常 Missing Context 候选、1 个解析失败**无可用复核标签**；3 组反事实对。`C101-SEED-03` 保持 `Business Boundary / Disputed Case`，`C101-SEED-21` 保持 `Parse Failure / REWORK_SOURCE`。

## 来源与资格

01–05 为中国政府采购网典型案例的**业务改写**，06–29 为合成文本；没有一条是已从原采购文件核实页码和逐字证据的案例。前五条也不是五个独立采购项目：01–02 同属典型案例 4，03–04 同属典型案例 1，05 属典型案例 2。03 的业务标签已有暂定裁决但仍是边界争议样本，21 的原始输入解析失败。JSONL 中 `proposed_label` 仅保留首轮采集历史，当前业务口径以 `reviewed_label` 为准；21 的 `reviewed_label=null`。所有案例仍保持 `HOLD`，21 为 `REWORK_SOURCE`；本包不能直接用作训练或 Blind Gold。

- [典型案例 1：售后机构与响应时效](https://www.ccgp.gov.cn/aljd/202512/t20251202_25830205.htm)
- [典型案例 2：经营面积、人员与销售额](https://www.ccgp.gov.cn/aljd/202512/t20251202_25830258.htm)
- [典型案例 4：注册地址到采购人的驾车时间](https://www.ccgp.gov.cn/aljd/202512/t20251202_25830319.htm)
- [中国政府采购网合辑](https://www.ccgp.gov.cn/llsw/202512/t20251204_25850212.htm)

## 业务裁决 BR-C101-DEC-03

`C101-SEED-03` 的投标条件允许两条路径：已有省内售后服务机构，或投标时承诺中标后在省内设置；两条路径均使投标人承担**指定地区设实体机构**的义务，不满足则投标无效。因此本任务复核标签为 `MATCH/OTHER_RELATED`，阶段 `QUALIFICATION`。普通到场／维修时效要求仍为 `NO_MATCH`。这里是候选识别口径，非对任何新项目的最终法律认定。

## 业务裁决 BR-C101-DEC-04：ParseFailure != NeedsContext

文本清楚但业务事实不够时，才使用 `NEEDS_CONTEXT`；OCR、附件、页码或表格结构本身不可靠时，必须使用 `REWORK_SOURCE`。因此 `C101-SEED-03` 保持 `Business Boundary / Disputed Case` 与 `HOLD`，`C101-SEED-21` 保持 `Parse Failure / REWORK_SOURCE`，不得混入普通训练或 Blind Gold。

## 解析失败的隔离

`C101-SEED-21` 原采集者暂列 `NEEDS_CONTEXT`；第二遍发现 OCR 残缺和附表缺失阻止重建一个可靠 Requirement。保留历史 `proposed_label` 仅供审计，`reviewed_label=null`、`data_eligibility=REWORK_SOURCE`；修复原件之前不计入普通 `NEEDS_CONTEXT` 分布、训练或盲测。

## 29 条逐例复核

| ID | 来源 | 文本（官方案例为改写） | 复核标签 | 第二遍核对结果 | 资格 |
|---|---|---|---|---|---|
| C101-SEED-01 | 官方案例改写 | 在应急方案评分中，将营业执照载明的地址到采购人的驾车时间纳入比较。 | `MATCH/DISTANCE_TO_PURCHASER` | 登记地址到采购人的驾车时间参与评分，是地域距离代理变量；保留官方案例改写身份。 | `HOLD` |
| C101-SEED-02 | 官方案例改写 | 投标人须承诺发生突发事件时十分钟内到场、负责人或项目经理三十分钟内到场。 | `NO_MATCH/NONE` | 到场分钟数是响应结果，与另一条按地址比较的评分要求拆开。 | `HOLD` |
| C101-SEED-03 | 官方案例改写 | 供应商在省内已有售后服务机构，或者承诺中标后设立；两种方式任选其一，作为实质性响应要求。 | `MATCH/OTHER_RELATED`；`Business Boundary / Disputed Case` | 按裁决 BR-C101-DEC-03 暂定命中；案例保持边界争议，独立人工复核、原件核验和数据 QA 前不入普通训练。 | `HOLD` |
| C101-SEED-04 | 官方案例改写 | 收到售后通知后须在二十四小时内到场，并在七十二小时内修复或更换。 | `NO_MATCH/NONE` | 到场和维修时限是服务结果；不得把同案另一地域条款的结论转移到此要求。 | `HOLD` |
| C101-SEED-05 | 官方案例改写 | 按供应商经营面积、参保人数和既往销售额分别计算评分。 | `NO_MATCH/NONE` | 面积、社保人数、销售额属规模财务因素；虽同为被处理案例，不属于 C1-01。 | `HOLD` |
| C101-SEED-06 | 合成 | 投标企业注册地须在本市，否则资格审查不通过。 | `MATCH/SUPPLIER_REGISTRATION_LOCATION` | 本市注册地直接决定资格，条件与后果均明确。 | `HOLD` |
| C101-SEED-07 | 合成 | 营业执照注册地址属于本区的供应商可加三分。 | `MATCH/SUPPLIER_REGISTRATION_LOCATION` | 本区注册地作为加分条件，外地仍可投标不妨碍候选命中。 | `HOLD` |
| C101-SEED-08 | 合成 | 现有办公地点距采购人不超过二十公里的，得五分。 | `MATCH/DISTANCE_TO_PURCHASER` | 既有办公地点距采购人的半径决定分数。 | `HOLD` |
| C101-SEED-09 | 合成 | 投标时营业场所距采购人须在十公里以内，否则响应无效。 | `MATCH/DISTANCE_TO_PURCHASER` | 既有营业地点的地域半径决定投标有效性。 | `HOLD` |
| C101-SEED-10 | 合成 | 投标截止前须在本市设有分公司，并提交其登记证明。 | `MATCH/PREEXISTING_LOCAL_BRANCH` | 投标截止前已设分公司及登记证明，是前置实体门槛。 | `HOLD` |
| C101-SEED-11 | 合成 | 已在采购人所在区设有分支机构的，商务评分加四分。 | `MATCH/PREEXISTING_LOCAL_BRANCH` | 既有地区分支机构形成评分优势。 | `HOLD` |
| C101-SEED-12 | 合成 | 营业执照住所栏记载为本市的投标人方可入围。 | `MATCH/SUPPLIER_REGISTRATION_LOCATION` | 营业执照住所栏即注册地的同义表达，作为入围条件。 | `HOLD` |
| C101-SEED-13 | 合成 | 项目实施地点为采购人位于本市的办公楼。 | `NO_MATCH/NONE` | 这是采购项目地点，未约束供应商身份。 | `HOLD` |
| C101-SEED-14 | 合成 | 供应商提交营业执照，并如实填写其注册地址。 | `NO_MATCH/NONE` | 要求披露注册地址，不限定其行政区域。 | `HOLD` |
| C101-SEED-15 | 合成 | 中标后可自行选择远程、派驻或合作维修方式满足售后时效，无须设本地机构。 | `NO_MATCH/NONE` | 明确可用远程、派驻或合作维修，且无本地机构义务。 | `HOLD` |
| C101-SEED-16 | 合成 | 承诺接报后两小时到现场的，服务方案得五分，不考察营业地点。 | `NO_MATCH/NONE` | 评分依据是可兑现的到场时效，明确不考察营业地点。 | `HOLD` |
| C101-SEED-17 | 合成 | 供应商注册资本须达到五千万元，否则不具资格。 | `NO_MATCH/NONE` | 注册资本并非注册地；应移交其他任务切片，不误报 C1-01。 | `HOLD` |
| C101-SEED-18 | 合成 | 合同生效后安排两名人员在现场常驻。 | `NO_MATCH/NONE` | 中标后派驻人员属于履约安排，不要求投标时已有实体或强制承诺设实体。 | `HOLD` |
| C101-SEED-19 | 合成 | 供应商应具有本地化服务能力。 | `NEEDS_CONTEXT/NONE` | “本地化服务能力”未定义，实体义务及评审后果仍需补证。 | `HOLD` |
| C101-SEED-20 | 合成 | 本市服务证明按资格条件第七项执行。 | `NEEDS_CONTEXT/NONE` | 引用的资格条件第七项缺失，无法还原具体要求。 | `HOLD` |
| C101-SEED-21 | 合成 | 供应商地址距采购人不超过[OCR缺失]，按附表评分。 | **无可用标签**（仅留历史暂定值） | Parse Failure：OCR 和附表缺失导致输入本身不可靠；按 BR-C101-DEC-04 撤销正式复核标签，转源件修复，不进入普通 `NEEDS_CONTEXT`。 | `REWORK_SOURCE` |
| C101-SEED-22 | 合成 | 投标人在本区设有服务点者按评分表另行计分。 | `NEEDS_CONTEXT/NONE` | “服务点”性质和评分条件缺失，可能是实体限制也可能仅服务安排。 | `HOLD` |
| C101-SEED-23 | 合成 | 依本项目特殊法定要求，投标人在本地已有分支机构；具体依据见未附的附件。 | `NEEDS_CONTEXT/NONE` | 具体法定例外依据未附，标注不能代替适用性核查。 | `HOLD` |
| C101-SEED-24 | 合成 | 投标时在本市已有分公司方可参与。 | `MATCH/PREEXISTING_LOCAL_BRANCH` | 反事实 CF01 正侧：投标时已有分公司为准入门槛。 | `HOLD` |
| C101-SEED-25 | 合成 | 中标后按响应时效提供服务，可自行组织方式，无须设本地实体。 | `NO_MATCH/NONE` | 反事实 CF01 负侧：仅承诺服务结果且无须设本地实体；与新裁决的强制设机构情形分开。 | `HOLD` |
| C101-SEED-26 | 合成 | 投标人既有办公地点距采购人二十公里以内得五分。 | `MATCH/DISTANCE_TO_PURCHASER` | 反事实 CF02 正侧：既有办公地点半径直接加分。 | `HOLD` |
| C101-SEED-27 | 合成 | 投标人承诺接报后二小时内到采购人现场得五分。 | `NO_MATCH/NONE` | 反事实 CF02 负侧：到场时效加分，不取企业既有地址。 | `HOLD` |
| C101-SEED-28 | 合成 | 本市注册的供应商得三分。 | `MATCH/SUPPLIER_REGISTRATION_LOCATION` | 反事实 CF03 正侧：本市注册地直接加分。 | `HOLD` |
| C101-SEED-29 | 合成 | 如实填报注册地址的供应商得三分，注册地不限。 | `NO_MATCH/NONE` | 反事实 CF03 负侧：只要求如实登记地址且不限定地域。 | `HOLD` |

## 反事实与防泄漏

- CF01：24 `MATCH` ↔ 25 `NO_MATCH`；既有分公司准入门槛与不限服务方式的履约结果相对。
- CF02：26 `MATCH` ↔ 27 `NO_MATCH`；现有办公地点半径与到场时效相对。
- CF03：28 `MATCH` ↔ 29 `NO_MATCH`；本市注册地加分与不限区域的信息填报相对。
- 两侧同 `pair_id`、同 `leakage_group_id`，不可跨训练、开发、盲测拆分；同一官方项目也必须同组。

## 下一道门

1. 业务判定语义可交付，但第二遍复核由 AI 辅助完成，**没有虚构两名独立人工标注员或四方签名**；真正的人工双盲复核和争议记录仍须补齐。
2. 对 01–05 调取原始采购文件版本和页码，重建逐字 Requirement 与证据跨度；对 21 修复 OCR／附表并重新拆分、重标。
3. 数据组须核对 `OTHER_RELATED` 的新冻结语义、`REWORK_SOURCE` 隔离和正式 JSON Schema；测试组核对已冻结评测依赖的版本／快照，不能把本次回标静默写进旧 Blind Gold。
4. 通过来源、独立人工复核、Schema、泄漏检查和数据 QA 后，再逐条提升资格；Demo 的 `INTERNAL_SILVER` 仍不是 Gold。
