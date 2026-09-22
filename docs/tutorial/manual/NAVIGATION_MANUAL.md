# 第一课～第十一课：课程 / 产品说明书式导航

> 用于快速阅读、查找问题和架构设计参考。

## 按问题查

### 模型学不好 / 泛化失败 / 过拟合

训练基础、数据分布、泛化、Error Analysis、Threshold、Calibration

`L01S01` · `L01S02` · `L01S06` · `L01S07` · `L01S11`

### 指标很好但业务仍不可靠

Accuracy、Precision/Recall、Slice、Calibration、Benchmark

`L01S03` · `L01S08` · `L01S11` · `L09S01` · `L09S02` · `L11S15`

### Transformer / Attention / Token / KV Cache

神经网络到完整 LLM 内部机制

`L02S01` · `L02S07` · `L02S08` · `L02S09` · `L02S10` · `L02S11` · `L02S12`

### GPU 跑不起来 / CUDA / 显存不足

环境、dtype、VRAM、加载、生成、量化

`L03S01` · `L03S02` · `L03S03` · `L03S04` · `L03S05` · `L03S06` · `L10S02` · `L10S03`

### PDF / Word / OCR / 表格解析差

文档解析、版面、Clause、Evidence、数据质量

`L04S01` · `L04S02` · `L04S03` · `L04S04` · `L11S03` · `L11S10`

### Dataset / 标注 / 数据泄漏

Schema、Label、Annotation、Split、Near-duplicate、Leakage

`L04S05` · `L04S06` · `L04S07` · `L04S08` · `L04S09` · `L04S10` · `L04S11` · `L04S12`

### SFT / LoRA / QLoRA 微调

Chat Template、Loss Mask、LoRA、QLoRA、训练配置、Checkpoint

`L05S01` · `L05S02` · `L05S03` · `L05S04` · `L05S05` · `L05S06` · `L05S07` · `L05S08` · `L05S09` · `L05S10` · `L05S11` · `L05S12` · `L05S13` · `L05S14`

### RAG 检索不到 / 召回差 / 引用不准

Chunking、Embedding、BM25、Hybrid、Rerank、Context、Citation

`L06S01` · `L06S02` · `L06S03` · `L06S04` · `L06S05` · `L06S06` · `L06S07` · `L06S08` · `L06S09` · `L06S10` · `L06S11` · `L11S12`

### Agent 工具乱 / 状态丢 / 流程跑不完

Tool Calling、State、Planning、Routing、Recovery、Human-in-the-loop

`L07S01` · `L07S02` · `L07S03` · `L07S04` · `L07S05` · `L07S06` · `L07S07` · `L07S08` · `L07S09` · `L07S10` · `L07S11` · `L11S14`

### 领域知识多，SFT 装不下

CPT、领域语料、数据混合、遗忘、Replay、Synthetic Data

`L08S01` · `L08S02` · `L08S03` · `L08S04` · `L08S05` · `L08S06` · `L08S07` · `L08S08` · `L08S09` · `L08S10`

### Benchmark / 能不能发布

Gold、Hard Cases、Red Team、Regression、Confidence Interval、Release Gate

`L09S01` · `L09S02` · `L09S03` · `L09S04` · `L09S05` · `L09S06` · `L09S07` · `L09S08` · `L09S09` · `L09S10` · `L09S11` · `L09S12` · `L11S15`

### 部署延迟高 / 吞吐低 / 多GPU效率差

Latency、Throughput、KV Cache、Quantization、Batching、Parallelism

`L10S01` · `L10S02` · `L10S03` · `L10S04` · `L10S05` · `L10S06` · `L10S07`

### 监控 / 灰度 / 回滚 / MLOps

Serving、Monitoring、Release、Rollback、Production Readiness

`L10S08` · `L10S09` · `L10S10` · `L11S16`

### 差别歧视 D01-D22

22项规则、资格准入、Evidence、Exception、Rule Version

`L11S04` · `L11S05`

### 技术参数 / 品牌 / 专利 / 检测 / 授权

参数组合指向、等效机制、市场证据、厂家授权

`L11S06`

### 评分 / 业绩 / 奖项 / 人员 / 主观分

评分函数、资格评分化、量化、主观评分边界

`L11S07`

### 中小企业 / 本国产品 / 绿色 / 创新 / 进口

政策适用、政策优惠与非法歧视的边界

`L11S08` · `L11S02` · `L11S12`

### 采购方式 / 竞争充分性 / 异常低价

竞争、采购方式、异常低价、确定性计算

`L11S09` · `L11S11`

### 法规版本 / 生效时间 / 辖区冲突

Policy Registry、Temporal、Jurisdiction、Applicable Policy

`L11S02` · `L11S12`

### 系统架构：Rule / RAG / LLM / Calculator / Agent

混合引擎、组件边界、任务路由、证据门

`L11S11` · `L11S14` · `L11S16`


## 按架构查

### 产品/业务边界

系统做什么、不做什么、输入输出、人工责任

`L11S01`

### 数据与文档理解层

PDF/Word/OCR → Section/Clause/Requirement/Evidence

`L04S01` · `L04S02` · `L04S03` · `L04S04` · `L11S03` · `L11S10`

### 训练数据层

Schema、Label、Hard Cases、Split、Leakage、Dataset Version

`L04S05` · `L04S06` · `L04S07` · `L04S08` · `L04S09` · `L04S10` · `L04S11` · `L04S12`

### 模型基础层

Transformer / LLM / Token / Attention / KV Cache

`L02S01` · `L02S07` · `L02S11` · `L02S12`

### 训练与领域适配层

SFT、LoRA/QLoRA、CPT、Hard Case / Counterfactual

`L05S01` · `L05S04` · `L05S08` · `L08S01` · `L08S05` · `L11S13`

### 知识与法规层

RAG、Embedding、BM25、Reranker、Policy Registry、Legal RAG

`L06S01` · `L06S04` · `L06S07` · `L06S09` · `L11S02` · `L11S12`

### 确定性规则/计算层

D01-D22、资格/技术/评分/政策/竞争规则与计算器

`L11S04` · `L11S05` · `L11S06` · `L11S07` · `L11S08` · `L11S09` · `L11S11`

### 合规决策引擎层

Rules + Calculator + Policy Resolver + Legal RAG + LLM

`L11S11`

### Agent 工作流层

Planner、State、Tools、Evidence、Human Gate、Completion

`L07S01` · `L07S05` · `L07S08` · `L11S14`

### 评测与发布门

Gold Benchmark、Slice、Red Team、Regression、Release Gate

`L09S01` · `L09S06` · `L09S10` · `L11S15`

### 生产服务与治理

Serving、Latency、Throughput、MLOps、Canary、Rollback、RBAC、Safe Mode

`L10S01` · `L10S07` · `L10S09` · `L10S10` · `L11S16`


## 130阶段目录


### 第1课：机器学习到底在学习什么？

- **L01S01 第1阶段：模型到底在“学习”什么？** — 数据 = 经验：模型世界来自训练样本，而不是模型名称。；信息决定上限：X 中不存在的信息，模型无法可靠利用。

- **L01S02 第2阶段：欠拟合、过拟合与泛化诊断** — 学不好 ≠ 训练不够：先诊断输入、标签、模型和优化。；Train 好 ≠ 模型好：泛化只能靠未见数据评价。

- **L01S03 第3阶段：如何正确评价一个模型** — 错误有不同类型，FP 与 FN 不能混成一个“错”。；Accuracy 会被类别分布欺骗，必须检查 Baseline。

- **L01S04 第4阶段：概率、Loss、Gradient 与反向传播** — Score 与 Decision 分离：模型分数不是最终业务动作。；Loss 定义错误的几何形状：不同 Loss 对不同错误施加不同压力。

- **L01S05 第5阶段：Batch、Step、Epoch 与真实训练过程** — Batch 是对整体数据分布的有噪声局部估计。；Epoch 是训练深度，不是模型能力分数。

- **L01S06 第6阶段：数据分布、采样与“数据即模型”** — 训练数据只是世界的样本，不是世界本身。；样本频率就是隐形权重，采样本身就是训练策略。

- **L01S07 第7阶段：模型诊断——Bias、Drift、OOD 与数据污染** — 模型有经验边界，能力必须描述“在哪些分布内经过验证”。；Label 只是对现实的测量，专家也可能错，分歧本身也是信息。

- **L01S08 第8阶段：完整机器学习实验——ProcurementML Experiment 001** — 大模型项目应该拆成一串可证伪的小实验。；Test Set 不是剩余数据，而是未来使用场景模拟器。

- **L01S09 第9阶段：工程化与可复现性——Versioning、Tracking、Registry** — 模型是完整训练状态，不是一个权重文件。；所有影响结果的东西都应该版本化。

- **L01S10 第10阶段：Production ML——监控、反馈与持续学习** — 上线才是真实考试，离线 Test 只是模拟。；生产质量由完整系统决定，不由单个 LLM 决定。

- **L01S11 第11阶段：不确定性、校准、选择性预测与风险控制** — 答案和对答案的自知能力是两种不同能力。；不确定性要区分问题本身不确定与模型知道得不够。

- **L01S12 第12阶段：因果、相关性、反事实，以及模型到底有没有学到“真正规律”** — 为什么这条数据会出现在我的数据库里？；哪些数据永远不会被我看到？


### 第2课：神经网络到完整 Transformer / LLM

- **L02S01 第1阶段：从一个神经元开始——神经网络最小计算单元到底在做什么** — Neuron = Weighted Sum + Bias + Activation。单个神经元本质上是一个可学习的打分函数。；Weight 不是人工写死的业务规则，而是训练过程中由 Loss 和 Gradient 共同塑造的参数。

- **L02S02 第2阶段：Activation Function——为什么没有激活函数，再深的神经网络也只是一个线性模型** — No Activation ⇒ Deep Linear Model。没有非线性激活函数，多层线性层可以合并成一个线性变换。；Activation Function 的核心作用是引入非线性，使网络能够表示弯曲、分段和更复杂的决策边界。

- **L02S03 第3阶段：Hidden Layer 与 Representation——为什么多层网络能逐步形成更抽象的“内部表示”** — Hidden Layer ≠ Human Rule Table。隐藏层不是一张可直接阅读的专家规则表。；Representation 是分布式的：一个业务概念通常由很多维度共同编码，而不是对应某一个神经元。

- **L02S04 第4阶段：Forward Propagation——一条政府采购样本到底如何从输入开始，逐层穿过整个神经网络，最终变成一个风险概率** — Forward Propagation = 在固定参数下把输入逐层变成输出；Forward 本身不等于学习。；每一层都同时有“数值”和“Shape”，Shape 跟错会直接导致矩阵运算或后续层语义出错。

- **L02S05 第5阶段：Backpropagation——最终 Loss 到底怎样穿过计算图，把“错误责任”一层层分配给每一个 Weight？** — Backpropagation = Loss 通过 Chain Rule 沿计算图反向传播，把错误信号分配给可训练参数。；Gradient ≠ Parameter Update。backward() 计算梯度，optimizer.step() 才真正改变参数。

- **L02S06 第6阶段：Optimizer 与 Learning Rate——梯度已经算出来了，参数究竟应该怎样迈出下一步？** — Gradient 告诉你局部方向，Optimizer 决定怎样利用当前和历史梯度真正更新参数。；Learning Rate 是最关键的更新尺度：太大可能震荡/发散，太小可能训练极慢或停在差的区域。

- **L02S07 第7阶段：Initialization、Normalization 与 Residual Connection** — Deep Network 需要 Signal Stability。深度增加以后，激活和梯度的尺度必须被主动控制。；Initialization 决定训练从什么数值尺度起步；坏初始化可能让信号一开始就爆炸或衰减。

- **L02S08 第8阶段：Embedding 与高维向量空间** — Token ID ≠ Semantic Meaning。整数 ID 本身没有语义，语义来自对应的 Embedding Vector。；Embedding 本质是一个可学习查表：离散 Token → 连续高维向量。

- **L02S09 第9阶段：Tokenizer 与 Subword** — Token ≠ Word ≠ Concept。Tokenizer 切出来的是模型计算单位，不是天然语言学词或完整知识概念。；Subword Tokenization 在词表大小与序列长度之间做折中，使模型能处理未登录词和组合词。

- **L02S10 第10阶段：Position Encoding 与 RoPE** — 没有 Position Information 的 Self-Attention 很难区分相同 Token 集合的不同顺序。；Positional Encoding 的任务是把“谁在前、谁在后、相距多远”注入模型表示。

- **L02S11 第11阶段：Self-Attention** — Self-Attention 的核心不是“平均看所有 Token”，而是根据 Query–Key 匹配动态决定从哪里读取信息。；Query 决定“我要找什么”，Key 决定“我怎样被匹配”，Value 承载“真正被汇聚的内容”。

- **L02S12 第12阶段：Transformer Block 与完整 Decoder-only LLM** — LLM ≠ One Giant Layer。现代 Decoder-only LLM 是许多 Transformer Block 重复堆叠形成的系统。；RMSNorm / Residual / Attention / MLP 各自承担不同角色：稳定、信息通路、跨 Token 交互和逐位置非线性变换。


### 第3课：GPU 环境与第一个开源大模型

- **L03S01 第1阶段：CPU、GPU、内存、显存、CUDA** — Compute Capacity ≠ Memory Capacity。GPU 算得快，不代表显存一定装得下模型和上下文。；RAM ≠ VRAM。系统内存与 GPU 显存位置、带宽和用途不同，不能用硬盘/内存数字替代显存预算。

- **L03S02 第2阶段：Driver、CUDA、PyTorch 到底是什么关系？** — Driver ≠ CUDA Toolkit ≠ PyTorch CUDA Build。三者是不同层级，必须分别确认版本与兼容性。；nvidia-smi 能看到 GPU ≠ PyTorch 一定能用 CUDA；它只能证明驱动层基本工作。

- **L03S03 第3阶段：一个开源大模型的文件夹里到底有什么？** — config.json 定义 Architecture Metadata，Tokenizer 定义 Text↔Token 协议，safetensors 保存真正的参数数值。；Model Weight ≠ Model Code。权重只是训练后的参数状态，模型结构仍需要代码和配置解释。

- **L03S04 第4阶段：`from_pretrained()` 背后到底发生了什么？** — from_pretrained() 不是一个神秘黑盒：读取 Config → 构建模型结构 → 加载权重 → 设置 dtype/device → 返回可运行对象。；Download Complete ≠ Model Ready。文件到磁盘后还要完成解析、权重装载和设备放置。

- **L03S05 第5阶段：第一次真正让一个开源 LLM 从“文字输入”走到“文字输出”** — 完整生成链是 Text → Token IDs → Tensor → Forward → Logits → Decode，不应把“文字直接进入神经网络”当作真实过程。；generate() 本质是 Autoregressive Loop：反复 Forward、选择下一个 Token、追加到序列再继续。

- **L03S06 第6阶段：FP32、FP16、BF16、INT8、INT4 与 Quantization** — Weight Memory 的第一近似 = Parameter Count × Bytes per Parameter；7B 模型在不同 dtype 下显存差异巨大。；dtype ≠ Quantization。FP16/BF16 是浮点精度选择，INT8/INT4 量化是更强的离散近似与压缩。

- **L03S07 第7阶段：第一次建立完整“显存账本”** — Serving VRAM ≠ Weight VRAM。完整显存账本至少包括 Weights + KV Cache + Activations/Workspace + Runtime Overhead。；Context Length 增长会显著扩大 KV Cache；“模型刚加载成功”不代表长上下文时仍不会 OOM。

- **L03S08 第8阶段：Greedy、Temperature、Top-k、Top-p 与 Sampling** — Greedy = 每一步选择最高概率 Token；Sampling = 按概率分布随机选择，两者只是解码策略不同。；Temperature / Top-k / Top-p 改变候选分布和随机性，不会给模型增加新知识。

- **L03S09 第9阶段：从“模型能跑”到“模型服务能用”** — Latency ≠ Throughput。单个用户等多久与服务器单位时间处理多少请求是不同指标。；TTFT ≠ Decode Speed。首 Token 等待时间和后续 Token 流速来自不同阶段瓶颈。

- **L03S10 第10阶段：基础模型选型与 ProcurementAI Baseline** — Best Leaderboard Model ≠ Best Procurement Model。选型必须看真实政府采购任务，而不是只看通用榜单。；模型选型是多目标问题：中文理解、Context、RAG/Tool 兼容、质量、延迟、显存、许可证和部署成本都要一起看。


### 第4课：政府采购数据工程与训练数据集

- **L04S01 第1阶段：Task Schema 与数据单元设计** — 文件 ≠ 数据样本；Schema = 我们对“一个样本是什么”的正式契约

- **L04S02 第2阶段：PDF、HTML、DOCX 到底怎样变成“可信文本”？** — 文件里“看得见文字” ≠ 文件里真的存着可直接读取的文字；Extract Text ≠ Parse Document

- **L04S03 第3阶段：文档结构恢复与 Clause Segmentation** — Clause Segmentation ≠ Sentence Splitting 一条采购条款可能有很多句；标题不是靠“字体大”一个特征判断， 而是多个结构信号共同决定

- **L04S04 第4阶段：数据清洗与规范化** — Cleaning ≠ Rewriting 清洗不是改写原文；原始文本必须保留， Normalized Text 应该是派生版本

- **L04S05 第5阶段：去重与近似去重** — 主要让模型偏科。；会让考试成绩造假。

- **L04S06 第6阶段：Train / Validation / Test 到底应该怎么切？** — Benchmark 泄漏不一定是把答案文件直接放进训练集。；Split 的单位不一定是 Row， 很多时候应该是 Project / Group

- **L04S07 第7阶段：数据泄漏与 Benchmark 污染** — 泄漏的本质，是测试问题相关的信息通过某条不被允许的路径参与了模型开发。；Split不重叠 ≠ 没有泄漏

- **L04S08 第8阶段：政府采购 Label Schema 与标注体系** — ClauseUnit ▼ 事实层 What does the document say? ▼ 判断层 Is there a potential risk? ▼ 分类层 What kind of risk? ▼ 证据层 Why / based on what? ▼ 不确定性层 Can we conclude confidently? ▼ 行动层 What should happen next? ▼ AnnotationSchema_V0.1；政府采购专业 Label Schema 的目标，不是把所有 Clause 压缩成“有风险 / 没风险”，而是把专家的判断拆成风险状态、风险类型、不确定性、理由、证据、行动建议和标注来源，让“专家脑子里的专业判断”第一次变成可以训练、可以评测、可以审计的数据结构。

- **L04S09 第9阶段：专家标注、双人复核与一致性** — “这个专家很厉害，所以他说什么就是什么。”；明确规则 + 独立标注 + 分歧检测 + 专家裁决 + 可追溯记录。

- **L04S10 第10阶段：Hard Negative 与边界案例设计** — Hard Negative 不是普通负样本，而是“非常像正样本的负样本”。 它的作用是打掉模型的错误捷径。；真正有价值的数据经常是一对，而不是一条。 两个案例越相似、结论越不同，越能暴露模型是否抓住了关键条件。

- **L04S11 第11阶段：Dataset Versioning、Lineage 与数据质量报告** — 一套冻结的数据状态。；数据 + 代码版本 + 配置版本。

- **L04S12 第12阶段：正式组装 `ProcurementDataset_V0.1`** — 只是 Dataset 派生出来的一种使用方式。；我已经有 train.jsonl 所以我已经有 Dataset


### 第5课：SFT + LoRA / QLoRA 微调

- **L05S01 第1阶段：Chat Template、Prompt、Response 与 Loss Mask** — “这是 Prompt。”；“这是 Response。”

- **L05S02 第2阶段：SFT 到底在训练什么？** — 第一，SFT 仍然是在做 Next Token Prediction，只是正确答案来自我们的专家数据。；第二，Forward 负责产生预测，Cross Entropy 把预测和正确 Token 比较后得到 Loss。

- **L05S03 第3阶段：训练样本长度、Truncation 与 Padding** — 每条训练样本都应该做成 32K。；一次序列允许使用的最大 Token 空间。

- **L05S04 第4阶段：Packing：怎样减少 GPU 浪费？** — 对齐 Tensor。；尽量让 GPU 算真实训练 Token，而不是 PAD。

- **L05S05 第5阶段：Full Fine-Tuning 与 PEFT** — 仍然使用整个 7B 模型。；模型有没有参加训练计算。

- **L05S06 第6阶段：LoRA 到底在改什么？** — 把 Base Model 某一层删掉，再装一个小层。；Base Model 保留原能力，LoRA 在旁边提供任务相关的修正。

- **L05S07 第7阶段：LoRA Rank、Alpha、Dropout** — 第一，Rank r 决定 LoRA 的低秩适配容量，并线性影响 Adapter 参数量。；第二，Alpha 不增加容量；在标准 LoRA 中真正起作用的是 alpha / r 这样的有效 Scaling。

- **L05S08 第8阶段：Target Modules：LoRA 到底插在哪里？** — A 容量一定更大，因为 64 > 16。；“Rank 用多少？”

- **L05S09 第9阶段：QLoRA 与 4-bit / NF4** — Base Model 的存储方式。；Base Model BF16 / FP16 等 Frozen + LoRA Adapter Trainable

- **L05S10 第10阶段：训练显存到底花在哪里？** — 能推理，不代表能训练。；Model Weights + KV Cache + Activations / Runtime Buffers

- **L05S11 第11阶段：真正跑一次 SFT 训练** — 第一，真正的 SFT 不是 trainer.train()，而是一份由 Dataset、Template、Mask、Length、Model、LoRA、Optimizer 和 Evaluation 共同构成的训练协议。；第二，在正式花 GPU 时间以前，必须人工 Decode Chat Template、检查 Assistant Loss Mask、检查长度和 Trainable Parameters，并先跑 5～20 Step Smoke Test。

- **L05S12 第12阶段：Checkpoint、Logging 与训练曲线** — 训练样本上的目标 Token 概率在上升。；Logging 告诉你训练过程正在发生什么

- **L05S13 第13阶段：LoRA Merge、模型保存与推理** — 把原来分开的 Base Weight 和 LoRA 增量提前加在一起。；这个 merged checkpoint 本身不会替你保留“可随时拆出来的 LoRA”。

- **L05S14 第14阶段：Baseline vs Fine-tuned Model 正式对比** — 微调的价值不是“模型参数变了”，而是它在独立、固定、可复现的业务测试上，证明自己改变了正确的行为，同时没有付出不可接受的回归代价。；模型更会预测训练目标。


### 第6课：RAG、Embedding 与向量检索

- **L06S01 第1阶段：RAG 到底是什么？从 Parametric Memory 到 External Knowledge** — 第一，Parametric Memory 是模型通过 Weight 表现出来的已有能力与知识；External Knowledge 是模型外部、可以独立更新和检索的知识资产。；第二，Fine-tuning 主要改变参数 \(\theta\)，RAG 主要在推理时增加检索证据 \(E\)，把 \(P_\theta(Y|X)\) 变成 \(P_\theta(Y|X,E)\)。

- **L06S02 第2阶段：Knowledge Base：法规、采购文件与知识版本怎样进入 RAG？** — 第一，RAG Knowledge Base 不是 PDF 文件夹，而是“正文 + Metadata + Provenance + Version + Validity”组成的可治理知识系统。；第二，每一份知识都必须能够从 Chunk 追溯到 Document，再追溯到原始 Source；否则 Citation 只是表面上有链接，并不是真正可审计。

- **L06S03 第3阶段：Chunking：长文档到底应该怎样切？** — 第一，Chunking 不是把长文本机械切短，而是在定义 Retriever 眼中的“知识最小单位”。；第二，Chunk 太大会产生语义稀释，Chunk 太小会产生语义碎片化，所以目标是兼顾检索聚焦度与语义完整性。

- **L06S04 第4阶段：Embedding：文本为什么可以变成“语义向量”？** — 第一，Embedding 是把 Query 或 Chunk 映射成固定维度向量，使语义相关的文本在模型学出的向量空间里尽量靠近。；第二，Dense Retrieval 的核心就是分别得到 Query Vector 和 Document Vector，再用 Cosine、Dot Product 或其它兼容度量做 Top-K 排序。

- **L06S05 第5阶段：Vector Index / Vector Database：向量到底怎样被快速找到？** — 第一，Exact Search 是把 Query 和全部向量逐个比较；ANN 则通过索引结构减少搜索范围，用少量近似误差换更低延迟和更高吞吐。；第二，Vector Index 是近邻搜索的数据结构，Vector Database 则还负责向量、Metadata、过滤、增删改、持久化和生命周期管理，两者不是同一个概念。

- **L06S06 第6阶段：Retrieval：Top-K 找到了，真的代表找对了吗？** — 第一，Retriever 的目标不是让“看起来相关”的文本靠前，而是让真正能够支持问题的 Gold Evidence 尽可能进入足够靠前的位置。；第二，Hit@K 看是否至少命中，Recall@K 看 Gold Set 覆盖率，MRR 看第一条正确证据出现得有多早；三者回答的问题不同。

- **L06S07 第7阶段：BM25 + Dense Retrieval：为什么只靠向量检索不够？** — 第一，BM25 属于 Sparse Retrieval，依赖词项匹配、IDF、词频饱和和长度归一化；它尤其擅长文号、金额、条款号、标准号和专有名词等精确信号。；第二，Dense Retrieval 擅长同义改写和语义泛化，但可能淡化数字、编号和细粒度字面差异；因此 Sparse 与 Dense 的盲区具有明显互补性。

- **L06S08 第8阶段：Reranker：为什么“先召回，再精排”比直接 Top-K 更可靠？** — 第一，Retriever 负责高 Recall 召回，Reranker 负责把最相关的候选重新排到最前面；两者优化目标不同。；第二，Bi-Encoder 通过独立 Query / Document Vector 实现高效大规模检索，而 Cross-Encoder 让 Query 与候选文本逐 Token 交互，因此更适合细粒度精排，但成本更高。

- **L06S09 第9阶段：Query Rewrite、Metadata Filter 与多路检索** — 第一，User Query 不一定适合直接检索；Query Processing 的职责是恢复上下文、显式化检索条件和生成必要的检索变体，但绝不能改变用户真实意图。；第二，Query Expansion 是“同一意图的多种表达”，Query Decomposition 是“把复杂问题拆成多个子意图”，两者不是一回事。

- **L06S10 第10阶段：Context Assembly、Citation 与 Grounded Generation** — 第一，Retrieval Top-K 只是候选集合，Context Assembly 还必须完成去重、版本检查、父级扩展、证据选择、Token Budget、排序和来源标记。；第二，Citation 不是模型随便生成一个编号，而必须形成 CitationID → Evidence → Chunk → Document → Source 的可审计映射，并检查引用是否真的支持对应 Claim。

- **L06S11 第11阶段：真正搭建 `ProcurementRAG_V0.1`：端到端检索、生成与评测** — 第一，Fine-tuning 改变模型参数和稳定行为，RAG 改变推理时模型能看到的外部证据；两者是互补关系。；第二，RAG 的上限首先受知识库质量限制：来源、版本、时间、辖区和有效性如果错，后面的检索越强只会越快找到错误证据。


### 第7课：Agent、Tool Calling 与政府采购工作流

- **L07S01 第1阶段：Agent 到底是什么？从一次性生成到 Observe → Decide → Act** — 第一，Agent 不是“更会聊天的 LLM”，而是 Model + State + Tools + Policy + Loop 组成的任务执行系统。；第二，普通 LLM 是 Prompt → Generate，RAG 通常是固定的 Retrieve → Generate Pipeline；Agent 的关键升级是模型可以根据 Observation 动态决定下一步 Action。

- **L07S02 第2阶段：Tool Calling：LLM 为什么可以“调用函数”？** — 第一，LLM 并不会直接执行函数；Tool Calling 的本质是模型生成结构化调用请求，外部 Runtime 真正执行，再把结果作为新的 Observation 返回模型。；第二，Tool Definition 告诉模型“有哪些工具”，Function Schema 告诉模型“参数应该长什么样”，Tool Call 只是执行请求，不等于执行已经发生。

- **L07S03 第3阶段：Structured Output：JSON Schema、Validation 与可靠参数生成** — 第一，Structured Output 的目标不是让模型输出“像 JSON 的文本”，而是得到 Parseable + SchemaValid + SemanticallyValid + PolicyValid 的可执行参数。；第二，合法 JSON 只解决语法层；JSON Schema 继续约束 Required、Type、Enum、Nested Object、Array 和是否允许额外字段，但 Schema 正确仍不代表业务语义正确。

- **L07S04 第4阶段：Tool Registry 与 Capability Boundary：模型到底允许调用什么？** — 第一，系统里“已注册的 Tool”“当前模型可见的 Tool”“当前请求真正可执行的 Tool”必须分成三层；Registered ≠ Visible ≠ Authorized。；第二，Tool Registry 不只是函数目录，而是同时保存 Schema、版本、副作用、权限范围、审批要求、状态和审计信息的 Capability Catalog。

- **L07S05 第5阶段：Agent Loop：Plan → Act → Observe → Continue / Stop** — 第一，Tool Calling 解决“这一刻调用什么”，Agent Loop 解决“怎样持续执行直到整个任务完成”；Action Success ≠ Task Success。；第二，可靠 Agent Loop 的最小结构是 State → Plan → Act → Observe → Update State → Continue / Stop，而 Plan 应该依赖当前真实 State，不应假装一开始就知道未来全部步骤。

- **L07S06 第6阶段：Planning 与 Task Decomposition：复杂采购任务怎样拆步骤？** — 第一，Planning 不是写待办清单，而是把 Goal → Subgoal → Executable Task → Dependency → Completion Criteria 变成一个可执行任务模型。；第二，复杂任务更适合表示成 Task Graph，而不是单一线性步骤；Dependency 决定 Sequential / Parallel，Join 决定并行分支何时可以重新汇合。

- **L07S07 第7阶段：State、Memory 与 Working Context：Agent 怎样记住任务进度？** — 第一，Agent Memory 绝不等于把全部聊天历史塞回 Context；Persistent State ≠ Working Context，前者保存真实任务状态，后者只提供当前一步最需要的信息。；第二，Conversation History 只是交互历史，Task State 才应该成为当前任务的结构化 Source of Truth；Artifact Store 保存大对象，State 只保存必要引用。

- **L07S08 第8阶段：RAG + Tools：什么时候检索知识，什么时候调用外部工具？** — 第一，RAG + Tools Routing 的核心不是“选择一个最方便的工具”，而是先确定这个问题真正的 Source of Truth 在哪里。；第二，规则依据优先走 RAG，实时结构化业务事实优先走权威数据库，具体文件内容走 File Tool，确定性计算走 Compute Tool，改变现实状态的请求才进入 Action Tool。

- **L07S09 第9阶段：Failure Recovery、Retry 与 Human-in-the-loop** — 第一，可靠 Agent 的目标不是“永不失败”，而是 Fails Explicitly + Recovers Safely + Escalates When Needed；Retry 只是 Recovery 的一种。；第二，失败必须先分类：Transient Failure 才适合 Retry，Validation Error 应修参数或 Replan，Authorization / Policy Failure 应停止或请求权限，Terminal Failure 应明确终止。

- **L07S10 第10阶段：Agent Safety：权限、Prompt Injection、Approval 与 Audit Trail** — 第一，Agent Safety 最重要的两条边界是 UntrustedContent ≠ TrustedInstruction 与 ModelDecision ≠ Authorization。；第二，Prompt Injection 真正危险的地方不是模型说错话，而是恶意内容是否能够穿透模型并驱动真实 Tool；因此 Tool Result、RAG Evidence、文件和网页都必须默认视为不可信数据。

- **L07S11 第11阶段：真正搭建 `ProcurementAgent_V0.1`：端到端政府采购工作流** — 第一，LLM 不是 Agent；Agent 是 Model + State + Tools + Policy + Loop，模型只是决策组件。；第二，Tool Calling 不是模型直接执行函数，而是 Structured Tool Request → Runtime Execution → Tool Result → New Observation。


### 第8课：CPT 与高级领域适配

- **L08S01 第1阶段：CPT 到底在学什么？为什么已经有 SFT / RAG / Agent 还要继续预训练？** — 第一，CPT 是在领域语料上继续执行 Next Token Prediction，让模型参数适应新的 Domain Distribution；它不是 SFT，也不是把知识库简单写进 Weight。；第二，CPT 学的是领域语言与统计结构，SFT 学的是任务行为，RAG 提供当前外部证据，Agent 负责受控执行工作流。

- **L08S02 第2阶段：Domain Corpus：什么样的政府采购领域语料值得用于 CPT？** — CPTCorpus ≠ DocumentDump。Corpus 是你希望模型长期吸收的领域分布，不是采购文件仓库。；MoreDocuments ≠ MoreSignal。真正有意义的是经过质量过滤、去重和领域相关性折算后的 Effective Tokens。

- **L08S03 第3阶段：Tokenizer Audit：领域术语怎样被切分，什么时候需要调整 Tokenizer？** — Token ≠ Word ≠ Concept。Token 是模型输入单位，不是天然语言学词，也不是一个完整知识概念。；High Fragmentation ≠ No Knowledge。切得碎首先意味着效率和表示成本上升，不等于模型一定不懂。

- **L08S04 第4阶段：CPT Training Objective：Next Token Prediction、Sequence、Context Length 与 Loss** — ObjectiveFormula 相同 ≠ LearningContext 相同。Next Token Prediction 的公式没变，但 Sequence 怎样构造会改变模型看到的条件上下文。；Sequence Boundary = Dependency Boundary。切在哪里，会决定哪些跨段关系能够在一次训练上下文中被直接学习。

- **L08S05 第5阶段：Data Mixture & Sampling：领域语料比例、质量权重、重复控制与采样策略** — CorpusShare ≠ TrainingShare。原始数据占比只是“你有什么”，训练占比才决定“模型实际看什么”。；SamplingPolicy = GradientAllocationPolicy。采样策略本质上是在给不同能力分配训练梯度。

- **L08S06 第6阶段：Catastrophic Forgetting：为什么模型学会领域知识以后，反而可能忘掉原来的能力？** — SharedParameters ⇒ CapabilityInterference。模型能力共享参数，学习新领域可能干扰旧能力。；DomainGain ≠ NetModelGain。领域能力上涨只是收益的一面，原有能力回归必须同时计入。

- **L08S07 第7阶段：Replay、Regularization 与能力保持：怎样防止 CPT 越训越窄？** — DetectForgetting ≠ PreventForgetting。发现遗忘是诊断，能力保持是训练控制。；Retention ≠ FreezeEverything。能力保持不是不让模型变化，而是让变化发生在值得变化的地方。

- **L08S08 第8阶段：Synthetic Data & Curriculum：合成领域语料、难度分层与覆盖扩展** — SyntheticData ≠ FreeNewKnowledge。合成数据能扩展表达和组合覆盖，但不能凭空创造可靠事实。；SyntheticGeneration 必须由 CoverageGap 驱动。先发现真实语料缺口，再生成，不做无目标数据膨胀。

- **L08S09 第9阶段：CPT vs SFT：什么时候继续预训练，什么时候监督微调，怎样正确串联？** — DomainGap ≠ BehaviorGap。不懂领域和不会按要求做任务，是两个不同问题。；TrainingChoice 必须由 ErrorDiagnosis 驱动。先判断错误发生在哪一层，再决定 CPT、SFT、RAG 或 Agent。

- **L08S10 第10阶段：真正训练 `ProcurementLM_V0.2`：端到端 CPT、评测、回归测试与 Release Gate** — CPTExperiment ≠ ModelRelease。训练跑完只是得到实验 Checkpoint，不代表模型可以发布。；ModelRelease ≠ WeightsOnly。真正模型版本必须包含 Tokenizer、配置、数据血缘、评测证据和 Release Manifest。


### 第9课：Gold Benchmark、评测与可靠性

- **L09S01 第1阶段：Benchmark 到底是什么？Validation、Test、Gold Benchmark 的边界** — Benchmark ≠ DatasetOnly。Benchmark 是被冻结的数据、协议、指标与治理的组合。；Training ≠ Validation ≠ Test ≠ Gold Benchmark。四者的核心区别是它们在模型开发生命周期中的信息权限不同。

- **L09S02 第2阶段：Gold Set：专家标注、Adjudication 与 Ground Truth** — ExpertOpinion ≠ GroundTruth。专家意见只是输入，Gold Truth 来自受控标注与裁决流程。；Gold = AuthorityByProcess。Gold 的权威性来自 Schema、证据、独立判断、裁决和版本治理，而不是单一专家身份。

- **L09S03 第3阶段：Evaluation Schema：到底评什么，不只是 Correct / Wrong** — CorrectAnswer ≠ CompleteEvaluation。最终答案正确，不代表过程、证据和系统行为都可靠。；WhatYouMeasure → WhatYouCanImprove。评测维度决定你能诊断和优化到什么粒度。

- **L09S04 第4阶段：Classification Metrics：Precision、Recall、F1、PR-AUC 与业务代价** — Accuracy ≠ RiskQuality。类别不平衡时，高 Accuracy 可能掩盖风险类完全失效。；Precision 对应误报负担，Recall 对应漏报风险，两者必须绑定业务代价。

- **L09S05 第5阶段：Generation Evaluation：理由、引用、事实性、幻觉与 Groundedness** — FluentAnswer ≠ CorrectAnswer。语言流畅和事实正确是两个不同维度。；ReferenceSimilarity ≠ SemanticCorrectness。文本重合度不能替代语义正确性。

- **L09S06 第6阶段：RAG Evaluation：Retrieval、Ranking、Context、Generation 分层评测** — RAGFailure ≠ LLMFailure。RAG 错误必须分层归因。；RetrievedContext = LLMVisibleWorld。Retriever 决定模型实际看到的证据世界。

- **L09S07 第7阶段：Agent Evaluation：Planning、Tool、State、Recovery、Safety、Completion** — ToolCallSuccess ≠ TaskCompletion。工具调用成功不等于真实任务完成。；AgentEval = OutcomeEval + TrajectoryEval。结果和执行轨迹必须同时评。

- **L09S08 第8阶段：Slice Evaluation：Risk Type、行业、地区、难度、Hard Case** — OverallScore ≠ SliceReliability。总体平均不能证明所有关键场景都可靠。；Average 会隐藏 Heterogeneity。不同子群性能可能差异巨大。

- **L09S09 第9阶段：Calibration、Abstention、OOD 与 Risk-Coverage** — ConfidenceScore ≠ ProbabilityOfBeingCorrect。置信分必须通过真实数据校准。；Accuracy ≠ Calibration。答得准和知道自己有多确定是两个能力。

- **L09S10 第10阶段：Benchmark Leakage、Contamination、Firewall 与 Test Governance** — NoExactDuplicate ≠ NoContamination。没有完全重复只能说明最浅层没有泄漏。；Semantic Independence > String Independence。Benchmark 独立性要覆盖语义、项目、血缘和派生关系。

- **L09S11 第11阶段：Benchmark Versioning、Regression Test 与模型版本比较** — HigherOverallScore ≠ NoRegression。总分上涨仍可能伴随关键能力退化。；BenchmarkVersion 决定 Score Meaning，跨 Benchmark 版本不能裸比。

- **L09S12 第12阶段：真正搭建 `ProcurementBench_V1`：端到端评测与 Release Gate** — Benchmark ≠ DatasetOnly。评测基准是数据、协议、指标和治理的组合。；ExpertOpinion ≠ GroundTruth。Gold 的权威来自受控流程，不来自单一专家身份。


### 第10课：推理部署、性能优化与 MLOps

- **L10S01 第1阶段：Inference 到底在优化什么？Latency、Throughput、TTFT、TPOT** — Latency ≠ Throughput。一个请求快和整个服务处理得多，是两个不同目标。；Prefill ≠ Decode。输入处理和逐 Token 生成是两个不同性能阶段，瓶颈也可能不同。

- **L10S02 第2阶段：Quantization：FP16、BF16、INT8、INT4 与精度—显存权衡** — Quantization ≠ FreeCompression。低 bit 是数值近似，不是无损压缩。；DataTypeChoice = Memory + Numerical + Kernel Decision。

- **L10S03 第3阶段：KV Cache：为什么推理显存不只是模型 Weight？** — ModelFitsInGPU ≠ ServingFitsInGPU。；KVCache = MemoryForComputeTradeoff。

- **L10S04 第4阶段：Paged Attention 与 vLLM：怎样提高显存利用率？** — ContiguousKVAllocation ≠ EfficientDynamicServing。；LogicalContinuity ≠ PhysicalContinuity。

- **L10S05 第5阶段：Batching：Static、Dynamic、Continuous Batching** — MaxBatch ≠ BestBatch。；BatchSize ≠ TokenLoad。

- **L10S06 第6阶段：Tensor Parallel、Pipeline Parallel 与多 GPU 推理** — MoreGPUs ≠ LinearSpeedup。；ScaleUp ≠ ScaleOut。模型分片和多副本服务是两种不同扩展。

- **L10S07 第7阶段：Serving Architecture：把 Model + RAG + Agent 接成真实 API 服务** — Deployment ≠ ModelLoading。；ProductionAI = ModelSystem + DistributedSystem。

- **L10S08 第8阶段：Observability：Metrics、Logs、Tracing、GPU 与业务监控** — Monitoring ≠ GPUUtilizationOnly。；Observability = Metrics + Logs + Traces + Quality + Cost。

- **L10S09 第9阶段：Model Versioning、Canary、Shadow、A/B 与 Rollback** — NewVersionReady ≠ 100% Traffic Ready。；ProductionVersion = ArtifactBundle。

- **L10S10 第10阶段：真正部署 `ProcurementAI`：性能压测、SLO、Release Gate 与生产闭环** — GoodModel ≠ GoodProductionSystem。；Latency ≠ Throughput。


### 第11课：ProcurementLM V1.0 政府采购合规智能体全流程实战

- **L11S01 第1阶段：业务目标与系统边界：政府采购合规 AI 到底要做什么？** — 

- **L11S02 第2阶段：法规知识体系与 Policy Registry：法律层级、辖区、生效时间、版本和冲突** — 

- **L11S03 第3阶段：采购文件业务解剖：Qualification、Technical、Commercial、Scoring、Contract** — 

- **L11S04 第4阶段：“四类”专项整治——采购人设置差别歧视条款：附件 9 的 22 项规则工程化** — 22项 ≠ 22个关键词。附件 9 的 22 项是 7 类问题下的 22 种具体表现形式。；Rule ≠ PromptInstruction。每个 Dxx 必须是可版本化、可执行、可测试、可审计的 Rule Object。

- **L11S05 第5阶段：资格条件与市场准入合规：地域、行业、所有制、规模、年限、财务、资质、业绩** — 

- **L11S06 第6阶段：技术参数合规：品牌、专利、技术路线、检测报告、认证、授权、样品** — 

- **L11S07 第7阶段：评审标准合规：量化、分值、业绩、奖项、人员、主观分与资格评分化** — 

- **L11S08 第8阶段：政府采购政策合规：本国产品、中小企业、绿色采购、创新、进口产品** — 

- **L11S09 第9阶段：采购方式、竞争充分性与异常低价检查** — ProcurementOrganization ≠ ProcurementMethod ≠ EvaluationMethod。集中 / 分散采购、采购方式、评审方法是三套不同维度。；PublicTenderThreshold ≠ OneNationalConstant。公开招标数额标准必须按预算级次、地区、采购对象和时点解析。

- **L11S10 第10阶段：采购文件数据工程：PDF、Word、表格、OCR、章节树、Clause ID 与 Evidence Span** — 

- **L11S11 第11阶段：Hybrid Compliance Engine：Rules + LLM + RAG + Calculator** — 

- **L11S12 第12阶段：法规 RAG 与 Temporal / Jurisdiction Reasoning** — 

- **L11S13 第13阶段：SFT / Hard Cases / Counterfactual Training：训练真正的合规判断能力** — 

- **L11S14 第14阶段：Compliance Agent：多轮审查、工具调用、状态、人工复核与报告生成** — 

- **L11S15 第15阶段：Gold Benchmark、Red Team 与 Release Gate** — 

- **L11S16 第16阶段：真正交付 `ProcurementLM_V1.0`** — 
