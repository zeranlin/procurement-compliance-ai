# C1-01 外地企业进入本地市场前置限制识别标注指南

**文档标识**：`C1_01_Label_Guide_V0.1`  
**状态**：V0.1 · FROZEN（业务标注语义；2026-09-22）  
**责任方**：业务组／产品组；适用人员为案例采集、标注、复核、数据和评测人员  
**上游契约**：`BR_C1_01_Business_Task_Spec_V0.1.md`；若两者冲突，以已冻结的 Business Task Spec 为准，记录冲突并修改版本，不能由标注员临场改口径。  
**任务 ID**：`C1-01_LOCAL_ENTRY_PRECONDITION`（内部工程 ID）；**任务性质**：`candidate_detection`；**标签权威**：`INTERNAL_SILVER`。

## 1 标注结果是什么

对采购文件中的**一个可独立判断的 Requirement**，标注是否将供应商既有注册地、所在地距采购人的距离、预先设立的本地分支机构，或投标时必须承诺中标后在指定地区设立售后服务机构，作为资格、实质响应或评审条件。结果只能是 `MATCH`、`NO_MATCH`、`NEEDS_CONTEXT`。`MATCH` 是待核查的 C1-01 候选线索，**不是违法认定**；`NO_MATCH` 只说明该 Requirement 未命中 C1-01，**不表示整个文件合规或已全面检查**。

本指南只覆盖项目蓝图中“第1类第1项”的工作切片，不扩成完整 7 类 22 项。相关专项整治通知将差别歧视条款列为重点，并将线索梳理、核实和处理处罚分阶段开展；标注作业停留在候选识别阶段。[财政部等关于开展2026年政府采购领域专项整治工作的通知](https://www.mof.gov.cn/gp/xxgkml/gks/202606/t20260611_3991484.htm)。

## 2 核心心智模型在标注中的动作

| 模型 | 标注员必须做的事 | 常见错误 |
|---|---|---|
| `Task != FinalViolationJudgment` | 只标候选类型、证据及待核查点；不写“违法／合法／应处罚”。 | 凭一个条款直接定性。 |
| `KeywordMatch != ItemMatch` | 同时核对**对象、既有地域属性、作用阶段和竞争后果**。 | 看见“本市”“分公司”“距离”就标 `MATCH`。 |
| `LocalServiceNeed != LocalEntityPrecondition` | 分清不限服务方式的结果型能力与投标时要求已有机构或必须承诺在当地设机构。 | 把两小时到场承诺当成设本地机构；或把强制设机构承诺错判为普通服务时效。 |
| `Clause != Requirement` | 先拆原子要求，每个要求独立标注，保留共同条款来源。 | 一段话含两项不同要求却只出一个总标签。 |
| `CollectedCase != TrainingCase` | 验原件、定位、复核与质检；未完成不能宣称训练可用。 | 把采集人的“疑似”直接当真值。 |
| `InternalSilver != Gold` | 标 `label_authority=INTERNAL_SILVER`，记录分歧和内部裁决者。 | 把内部共识写成独立专家 Gold。 |
| `TrainingSet != BenchmarkSet` | 保留项目、模板家族和反事实对关联；测试组独立持盲测真值。 | 条款随机切分导致训练和盲测相互泄漏。 |

## 3 一条案例的完整作业顺序

1. **登记来源**：记录 `case_id`、`project_id`、`document_id`、`document_version`、页码／章节／表格单元和采集来源；与原件核对文字。不同版本不混标，若更正公告改变条件，以各版本分别建要求并关联版本关系。
2. **检查可读性**：若 OCR、表格列关系或引用页缺失影响关键事实，尝试补原件、附表或更正公告。可定位的歧义可先作 `NEEDS_CONTEXT`，但原始数据缺陷未修复的记录应为 `REWORK_SOURCE`，不得直接入训练。
3. **拆成 Requirement**：按独立的资格后果、评分作用或履约义务拆分；同一句中的不同条件分别建 `requirement_id`，共用 `clause_id`，保留完整原句和必要上下文。禁止改写原文后再取证。
4. **回答四问**：谁被约束？是企业既有地域身份、强制承诺设当地实体，还是不限方式的服务能力？承诺义务何时影响投标，实体何时设立？产生资格、无效投标、加减分或优先选择后果吗？
5. **标主标签及子型**：按第 4 节优先顺序；然后标 `business_stage`、事实因子、证据跨度、缺失问题、案例切片和复核状态。
6. **独立复核及裁决**：第二标注员在看不到首轮结论时独立标；分歧按第 8 节处理。数据组完成 Schema、来源、重复与泄漏检查后，才决定数据资格。

**示范拆分**：“投标人须在本市注册，且中标后两小时内响应。”拆为 R1“投标人须在本市注册”→ `MATCH`；R2“中标后两小时内响应”→ `NO_MATCH`。两条都引用原句，可各自标精确证据片段。若语法或表格结构使拆分对象无法可靠判断，先标 `NEEDS_CONTEXT` 并提出拆分问题，设置 `data_eligibility=HOLD`，修复后重标；不把不可分的混合句当作合格单条训练样本。

## 4 三分类决策树

| 顺序 | 核验问题 | 行动 |
|---|---|---|
| 0 | 原文是否可追溯？解析／表格关系是否足以确认当前 Requirement？ | 否：补原件；存在实质歧义时暂标 `NEEDS_CONTEXT`，标 `REWORK_SOURCE` 并暂停入库。 |
| 1 | 文字是否约束供应商地域属性或要求在指定地区设立实体，而非采购人／项目地点或不限方式的服务能力？ | 明确没有：`NO_MATCH`；对象不明且会改变结果：`NEEDS_CONTEXT`。 |
| 2 | 是否指注册／登记地、既有地点距采购人的距离、评审前已有地区分支机构，或投标时强制承诺中标后设当地售后机构？ | 明确属于其他条件：`NO_MATCH`；“服务点”是否实体不明：`NEEDS_CONTEXT`。 |
| 3 | 是否用作资格准入、投标有效性、评分、排名或优先选择？ | 明确有：继续；明确仅为地址描述或履约标准：`NO_MATCH`；后果只在未取得的引用中：`NEEDS_CONTEXT`。 |
| 4 | 投标时要求已有地域属性，还是必须作出中标后设当地实体的承诺？ | 两者明确且影响竞争：`MATCH`；仅承诺服务结果、自由选择方式：`NO_MATCH`；机构性质或竞争后果不明：`NEEDS_CONTEXT`。 |
| 5 | 文本显示特定法定依据／例外并有待核实材料吗？ | 保留事实证据，标 `NEEDS_CONTEXT` 并移交业务／法律复核；不得由标注员自行裁定合法性。没有明确例外材料时，明确门槛仍可标 `MATCH`。 |

要标 `MATCH`，至少有**主体地域身份或强制设当地实体承诺 + 竞争后果**两项原文事实。资格章节中的“投标人须……”可与该章节标题共同证明后果；不能因为没有“违法”字样就弃权。明确的评分优势也命中，即使外地企业没有被禁止投标。`NEEDS_CONTEXT` 要求缺失事实**确实可能改变标签**，不能当作“觉得复杂”的万能标签。

### 4.1 标签和子型联合约束

| `match_state` | `subtype` | 必填证据和动作 |
|---|---|---|
| `MATCH` | `SUPPLIER_REGISTRATION_LOCATION` / `DISTANCE_TO_PURCHASER` / `PREEXISTING_LOCAL_BRANCH` / 经业务批准的 `OTHER_RELATED` | 地域属性及竞争后果的原文跨度、来源定位；后续可能仍需法律核查。 |
| `NO_MATCH` | `NONE` | 记录排除理由；hard negative 保留含误报词的原文和解释。 |
| `NEEDS_CONTEXT` | `NONE` | 记录歧义原文或解析失败位置、**具体缺失问题**、索取材料及负责方；`human_review_required=true`。 |

禁止出现 `MATCH/NONE`、`NO_MATCH/某命中子型`、`NEEDS_CONTEXT/某命中子型`。对 `NO_MATCH` 无相关引文时 `evidence_text=null`、`evidence_spans=[]`，但来源定位仍须存在。`NEEDS_CONTEXT` 不是第四种 subtype。

## 5 子型、阶段和事实因子

| 子型 | 触发条件 | 易混淆反例 |
|---|---|---|
| `SUPPLIER_REGISTRATION_LOCATION` | “须在本市注册”“注册地址位于本区得分”等主体登记／住所地成为门槛或评分。 | “提供营业执照及注册地址供核验”；只申报信息不产生地域门槛。 |
| `DISTANCE_TO_PURCHASER` | 将供应商**既有**经营／办公地点到采购人的距离阈值直接作准入或得分条件。 | “接报后 2 小时到达”；是履约结果而非企业地址半径。 |
| `PREEXISTING_LOCAL_BRANCH` | 投标或评审时“已设／现有”本地分支机构作为资格或加分。 | 强制承诺中标后设实体改用 `OTHER_RELATED`；只保障服务结果且不要求本地机构则 `NO_MATCH`。 |
| `OTHER_RELATED` | V0.1 **仅**包含业务裁决 `BR-C101-DEC-03`：投标时必须承诺中标后在指定地区设立售后服务机构，不承诺即投标无效或失分；“已设有或承诺中标后设立”也属于此情形。 | 不把其冒充 `PREEXISTING_LOCAL_BRANCH`；普通到场时效、可自选人员或合作维修方式均不属此型。 |
| `NONE` | `NO_MATCH` 或 `NEEDS_CONTEXT` 的占位值。 | 不可单独代表“尚未检查”。 |

V0.1 中 `OTHER_RELATED` **仅限上述已冻结情形**；每次使用均记录强制实体义务与竞争后果的证据。其他同质情形须提出新版本变更，不允许标注员将疑难样本直接放入该桶。

`business_stage` 取 `QUALIFICATION`（资格／无效投标）、`SCORING`（评分／优先排序）、`TECHNICAL`（技术服务要求）、`CONTRACT`（中标后履约），或 `null`（证据不足并写明原因）。**功能优先于章节标题**：置于“技术评分表”的现有本地分公司加分，仍标 `SCORING`。一项要求若同时有资格否决和单独加分，拆成两条并分别标阶段；仅语法无法拆解时进入复核。

`reasoning_factors` 只写可由原文验证的事实，初始受控词表如下。没有原文支持不能填，新增值须版本化；不得用自由文本推理链替代。

| 因子 | 何时使用 |
|---|---|
| `supplier_location_attribute` | 企业注册、住所、既有办公／营业地点。 |
| `distance_to_purchaser` | 企业既有地点距采购人的距离被限制或评分。 |
| `preexisting_branch` | 评审前须已设区域分支机构。 |
| `pre_award_condition` | 条件在投标／资格／评审时生效。 |
| `market_entry_gate` | 不满足条件将失去资格或投标无效。 |
| `scoring_advantage` | 地域条件导致加减分、排名或优先。 |
| `post_award_service` | 仅中标后建立服务能力的负例事实。 |
| `location_mention_only` | 只是地理事实或地址披露。 |
| `local_service_term_ambiguous` | “本地化服务”等词需要补定义／阶段。 |
| `cross_reference_missing` | 决定标签的关联条款缺失。 |
| `source_parse_uncertain` | OCR／表格关系影响关键事实。 |
| `exception_needs_review` | 已显示特殊依据或例外材料，但未核实。 |

`BR-C101-DEC-03` 的 `OTHER_RELATED` 在现有 Dataset Schema V0.1 受控词表下，可用 `pre_award_condition` 加 `market_entry_gate`（或评分时用 `scoring_advantage`）记录投标时竞争作用；`post_award_service` 仅表示机构设置的履约时点，不得单独充当“必须设本地实体”的证据。实体义务必须由 `subtype=OTHER_RELATED`、原文证据及裁决编号共同表达；若数据组要求专用新因子，应修订 Schema 和接口版本，不能私自向 V0.1 枚举加值。

## 6 证据、上下文与缺失问题

**原文证据**须能够从 `project_id + document_id + document_version + page/section/offset` 或等效定位复核。`evidence_text` 是一个连续原文片段；`evidence_spans[]` 分别记录地域条件和资格／评分后果，跨条款时各自带定位；`evidence_refs[]` 与证据段对应。不能拼接成伪引文，不能把法律评价写进证据，也不能用截图文件名代替原句。

可采集同一文件的资格条件、评分表、投标须知、合同和更正公告作为 `context`，同时标注引用的文档版本。引用新版本对旧版本的修改时保留修改链，不能把两个版本拼成同一时点的要求。外部法律依据可在人工复核记录中引用，但不作本任务原文证据。

`NEEDS_CONTEXT` 至少包含一条可执行问题：**缺什么材料／事实、从哪里取得、谁复核**。若缺失缘由是 OCR／附表解析失败，可保留**暂定** `NEEDS_CONTEXT` 占位用于修复队列，但其 `reviewed_label=null`、`data_eligibility=REWORK_SOURCE`，不得进入普通 `NEEDS_CONTEXT` 训练／盲测切片。推荐问题模板：

- “请补充‘本地化服务能力’的定义及评分表：是否要求投标时已有当地机构？”
- “请补资格条件第七项和关联附表：该‘服务证明’是否构成资格否决？”
- “请调取原 PDF 对应表格行／列：20 公里指供应商现有地址还是项目现场到达范围？”
- “请业务／法律复核明确写出的特殊依据及适用范围；在本任务中暂不作最终法律认定。”

若文本已清晰构成身份门槛，但尚无完整法源材料，只将后续法律核查记为备注，主标签仍是 `MATCH`；已显示具体例外争议且该材料可能改变本项分类时才转 `NEEDS_CONTEXT`。无命中、未检查、解析失败应分别记录；**不能用 `NO_MATCH` 填补覆盖空白**。

## 7 六类样例切片与逐例答案

下列全是**合成业务样例**，用于统一内部标注，不表示实际项目的法律结论。方括号为缺失文本说明，不视为原文。每例的 `subtype=NONE` 对应非 `MATCH`。

| ID／切片 | Requirement 原文 | `match_state`／`subtype`／阶段 | 决定事实或下一问题 |
|---|---|---|---|
| P01 典型正例 | “投标人须为本市注册企业，否则投标无效。” | `MATCH`／`SUPPLIER_REGISTRATION_LOCATION`／`QUALIFICATION` | 注册地＋资格后果均明确。 |
| P02 典型正例 | “供应商办公地点距采购人不超过20公里的，得5分。” | `MATCH`／`DISTANCE_TO_PURCHASER`／`SCORING` | 既有地点的半径影响评分。 |
| P03 典型正例 | “投标时在本区已设分公司的，资格审查通过。” | `MATCH`／`PREEXISTING_LOCAL_BRANCH`／`QUALIFICATION` | 投标前已有机构＋资格后果。 |
| P04 隐蔽正例 | “注册地址在本市行政区域的，商务评分另加3分。” | `MATCH`／`SUPPLIER_REGISTRATION_LOCATION`／`SCORING` | 虽未禁止外地投标，评分仍偏向地域身份。 |
| P05 隐蔽正例 | “以开标日之前本地分公司营业执照作为服务保障评分依据。” | `MATCH`／`PREEXISTING_LOCAL_BRANCH`／`SCORING` | “服务保障”措辞下仍按既有实体加分。 |
| P06 机构承诺正例 | “投标人须承诺中标后在本省设立售后服务机构，否则投标无效。” | `MATCH`／`OTHER_RELATED`／`QUALIFICATION` | 投标时被强制承担指定地区实体义务，不是可自选方式的响应时效。 |
| N01 普通负例 | “本项目交货地点为采购人本市办公楼。” | `NO_MATCH`／`NONE`／`CONTRACT` | 项目地点，不限制供应商地域身份。 |
| N02 普通负例 | “投标人应提交营业执照及其登记地址。” | `NO_MATCH`／`NONE`／`QUALIFICATION` | 信息披露；没有注册地范围门槛。 |
| N03 相似负例 | “中标后在项目现场配备驻场人员。” | `NO_MATCH`／`NONE`／`CONTRACT` | 中标后履约安排。 |
| N04 相似负例 | “中标供应商应建立两小时内到达现场的服务机制。” | `NO_MATCH`／`NONE`／`CONTRACT` | 响应时效，不是已有办公地点距离。 |
| N05 相似负例 | “供应商注册资本不少于5000万元。” | `NO_MATCH`／`NONE`／`QUALIFICATION` | 可能属于另一项；不属 C1-01 地域身份。 |
| U01 信息不足 | “供应商应具备本地化服务能力。” | `NEEDS_CONTEXT`／`NONE`／`TECHNICAL` | 要定义与评分表：是否要求既有地区实体？ |
| U02 信息不足 | “本市服务证明按资格条件第七项执行。”第七项未提供。 | `NEEDS_CONTEXT`／`NONE`／`null` | 要第七项、文件版本及后果。 |
| U03 解析失败 | “距采购人不超过[模糊]，按附表得分。”附表缺失。 | 暂定 `NEEDS_CONTEXT`／`NONE`／`null` | 补原 PDF、表格与附表；正式 `reviewed_label=null`，`REWORK_SOURCE`，不入训练或普通缺上下文切片。 |
| U04 例外待核 | “依照本项目特殊法定要求，须在本市已有分支机构。”但依据及适用条件未附。 | `NEEDS_CONTEXT`／`NONE`／`QUALIFICATION` | 核实依据、项目范围；标 `exception_needs_review`。 |

**反事实对 CF01**：`投标时已在本市设立分公司方可投标` → `MATCH`；改为 `中标后按响应时效提供服务，可自行组织方式，无须设本地实体` → `NO_MATCH`。改变的是**设当地实体门槛与不限方式的服务结果**。  
**反事实对 CF02**：`供应商办公地点距采购人20公里内得5分` → `MATCH`；改为 `承诺接报后2小时到现场得5分` → `NO_MATCH`。改变的是**企业地址代理变量与履约结果变量**。  
**反事实对 CF03**：`本市注册供应商得3分` → `MATCH`；改为 `提交营业执照并载明注册地址得3分` → `NO_MATCH`。改变的是**限制地域的评分条件与对所有人一致的信息要求**。
**反事实对 CF04**：`投标时须承诺中标后在本市设立售后服务机构，否则投标无效` → `MATCH/OTHER_RELATED`；仅改为 `投标时须承诺两小时到场，可自行组织服务，不要求本地实体` → `NO_MATCH/NONE`。改变的是**指定地区设实体义务与结果型服务承诺**。

反事实对的两个样本使用相同 `pair_id`，记录唯一关键改动和预期翻转。来源为同项目／模板家族的样本必须共享 `leakage_group_id`；同一反事实对不跨 train/dev/blind 分割。合成例和真实采集例分开标识 `case_origin`，合成例不得冒充官方案例或法源真值。

## 8 双人标注、分歧裁决和回标

**标注角色**：采集人验证来源；标注员 A 和 B 独立给出要求拆分、主标签、子型、阶段、证据及问题；业务复核人处理分歧；数据质检人验结构与来源；测试组独立定义盲测切片并保管 blind gold。当前缺独立专家组，业务复核仅形成**内部暂定共识**。

比较 A/B 时先核对**拆分与原文版本**，再比较主标签、子型、阶段、证据跨度和缺失问题。若来源或拆分不同，先修输入再重标；若同一要求的判定不同，各方各自指向原句和判定问题，业务复核人写下决定、依据及影响案例。不能以多数票代替缺失材料，不能按模型预测修改标注，也不能把“无法达成一致”默认为 `NO_MATCH`。复核后仍有实质缺口，保留 `NEEDS_CONTEXT` 并发补件任务；解析失败按 `REWORK_SOURCE` 隔离；新规则层冲突则设 `DISPUTED`、`data_eligibility=HOLD` 并提版本变更。

**裁决日志**至少记录 `case_id`、`requirement_id`、A/B 标签、分歧类型、原文定位、业务决定、决定者、日期、补件／回标范围、指南版本。影响同一模板的变更，要按模板家族批量查找并重标，不只修一个例子；冻结后的改动生成新版本并保留旧快照。盲测真值冻结后，不得因模型表现临时修改判定口径或门槛。

## 9 标注记录与数据资格

以下是**纯演示业务记录**，其中项目、文档及页码均为虚构占位，不能作为可入库的真实案例。数据组将在 `C1_01_Dataset_Schema_V0.1.json` 中落实字段类型和必填约束；不得把此示例当作数据组已冻结的正式 Schema。

```json
{
  "case_id": "CASE-C101-0001",
  "requirement_id": "REQ-C101-0001-A",
  "project_id": "P-001",
  "document_id": "DOC-001",
  "document_version": "V1",
  "clause_id": "CL-008",
  "requirement_text": "投标人须为本市注册企业。",
  "source_location": {"page": 8, "section": "供应商资格条件"},
  "context": null,
  "parser_quality": "PASS",
  "business_stage": "QUALIFICATION",
  "label": {"match_state": "MATCH", "subtype": "SUPPLIER_REGISTRATION_LOCATION"},
  "evidence_text": "投标人须为本市注册企业。",
  "evidence_spans": [{"text": "投标人须为本市注册企业。", "document_id": "DOC-001", "document_version": "V1", "page": 8, "section": "供应商资格条件"}],
  "evidence_refs": [{"document_id": "DOC-001", "document_version": "V1", "page": 8, "section": "供应商资格条件"}],
  "reasoning_factors": ["supplier_location_attribute", "pre_award_condition", "market_entry_gate"],
  "missing_context_questions": [],
  "human_review_required": false,
  "source_verified": false,
  "case_origin": "ILLUSTRATIVE",
  "case_slice": "TYPICAL_POSITIVE",
  "pair_id": null,
  "leakage_group_id": "LG-001",
  "review_state": "PENDING_SECOND_PASS",
  "label_authority": "INTERNAL_SILVER",
  "data_eligibility": "HOLD",
  "guide_version": "C1_01_Label_Guide_V0.1"
}
```

**状态分层**：`review_state` 可为 `PENDING_SECOND_PASS`、`DISPUTED`、`INTERNAL_REVIEWED`；`data_eligibility` 可为 `HOLD`、`REWORK_SOURCE`、`PENDING_DATA_QA`、`TRAIN_ELIGIBLE`、`BENCHMARK_CANDIDATE`。业务复核不等于数据验收；是否最终分配到 train/dev/blind，由数据和测试团队按快照权限确定。解析失败可保留暂定采集标签，但正式 `reviewed_label` 为空；不能把失败文本作为普通缺上下文训练实例。`BENCHMARK_CANDIDATE` 不等于“正式 Gold”，盲测真值由测试组独立持有，算法组只见盲测输入。

**最低入库门槛**：来源真伪与版本已核；Requirement 可独立判断；主标签与 subtype 符合联合约束；证据可回原文；双人分歧已处理；`INTERNAL_SILVER` 标签保留；项目／模板家族和反事实对已关联。任何一项缺失则 `HOLD` 或 `REWORK_SOURCE`。`NEEDS_CONTEXT` 可以作为有效的**信息不足样本**，前提是原文可核、缺失问题具体、来源解析足够可靠；由 OCR 失败造成的未修复伪歧义不可混入这一类训练样本。

## 10 质检清单与验收

业务组在交付前逐项核对：

- [ ] 样例覆盖典型正例、隐蔽正例、普通负例、高相似负例、信息不足和反事实对；三子型各有明确正例。
- [ ] 每个 `MATCH` 同时能指认地域身份属性和资格／评分后果，并有原文版本定位。
- [ ] 每个 `NO_MATCH` 是对已检查 Requirement 的排除，而非未解析或未检查；相似负例写明差异。
- [ ] 每个正常 `NEEDS_CONTEXT` 有可改变标签的缺失事实、补件来源和负责方；解析失败仅进 `REWORK_SOURCE`，不混入训练／盲测。
- [ ] 子型、阶段、事实因子取值受控；`OTHER_RELATED` 均有业务负责人裁决。
- [ ] 来源、案例起源、双人分歧、回标、`INTERNAL_SILVER` 和 `leakage_group_id` 可审计。
- [ ] 同项目／模板及反事实对不跨 split；盲测真值不进入算法目录；测试组确认本指南可测。
- [ ] 结构化示例可通过数据组 Schema；不输出最终法律责任和处罚判断。

**冻结记录**：2026-09-22，按项目任务发起人的本轮业务指令冻结本指南的标注语义，裁决编号 `BR-C101-DEC-03`。本记录不代替数据、算法、测试团队的实际接口确认；数据 Schema 当前仍为 DRAFT，下游应依照本指南核对 `OTHER_RELATED`、`REWORK_SOURCE` 与切片映射，完成契约测试后方可正式集成。若上游 Business Task Spec 改变主标签、子型或要求粒度，先同步改本指南并重审影响样本；不得让两个版本在同一数据快照里混用。

## 11 关联文件

- `BR_C1_01_Business_Task_Spec_V0.1.md`：业务范围、标签语义和模型接口的上位约束。
- `ProcurementComplianceLM_C1_01_Minimum_Demo_Execution_Blueprint_V0.1.md`：WP-BIZ-02、内部 Silver、样本切片、泄漏隔离和 Demo Gate。
- 后续产物：`C1_01_Case_Intake_V0.1.jsonl`、`C1_01_InternalSilver_CasePack_V0.1.jsonl`、`C1_01_Dataset_Schema_V0.1.json`、独立 Benchmark Snapshot。
