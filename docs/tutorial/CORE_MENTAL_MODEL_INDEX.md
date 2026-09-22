# 第一课～第十一课：核心心智模型索引（V2）

> 每个阶段先抓判断框架，再回正文看公式、案例、反例和工程细节。


## 第1课：机器学习到底在学习什么？


### 第 1 阶段

- 数据 = 经验：模型世界来自训练样本，而不是模型名称。
- 信息决定上限：X 中不存在的信息，模型无法可靠利用。
- 标签 = 老师：错误、冲突、粗糙标签会直接塑造错误行为。
- 学习 = 减少 Loss：模型不会读懂我们的愿望，只会响应训练信号。
- 能力 = 泛化：真正能力体现在未知项目，不体现在训练集背诵成绩。

### 第 2 阶段

- 学不好 ≠ 训练不够：先诊断输入、标签、模型和优化。
- Train 好 ≠ 模型好：泛化只能靠未见数据评价。
- 测试必须模拟真实部署：项目级、时间级、地区级隔离非常关键。
- 必须防止模型走捷径：Hard Cases 和反事实改写能暴露 shortcut。
- 错误是信息：Error Analysis 是下一轮训练设计的入口。

### 第 3 阶段

- 错误有不同类型，FP 与 FN 不能混成一个“错”。
- Accuracy 会被类别分布欺骗，必须检查 Baseline。
- 指标服从业务目标，不是业务服从指标。
- Threshold 是业务决策层，而不是模型固定常数。
- 平均值会掩盖局部弱点，必须做 Slice Evaluation。

### 第 4 阶段

- Score 与 Decision 分离：模型分数不是最终业务动作。
- Loss 定义错误的几何形状：不同 Loss 对不同错误施加不同压力。
- Gradient 是 Credit Assignment：决定每个参数应该承担多少纠错责任。
- 训练是无数微小参数更新的累积：不是一次“灌知识”。
- Confidence ≠ Truth：概率必须经过评测、校准和证据验证。

### 第 5 阶段

- Batch 是对整体数据分布的有噪声局部估计。
- Epoch 是训练深度，不是模型能力分数。
- Gradient、Optimizer、Learning Rate 是三个不同角色。
- 训练本质是随机/有噪声优化，曲线抖动不等于失败。
- Monitoring 本身就是训练的一部分，没有日志就难以诊断。

### 第 6 阶段

- 训练数据只是世界的样本，不是世界本身。
- 样本频率就是隐形权重，采样本身就是训练策略。
- 困难样本决定决策边界，简单重复样本边际价值会下降。
- 高置信度错误暴露最深的错误规律，是高价值训练资产。
- Dataset 是课程设计：应该主动决定模型看什么、看多少、以什么对比方式看。

### 第 7 阶段

- 模型有经验边界，能力必须描述“在哪些分布内经过验证”。
- Label 只是对现实的测量，专家也可能错，分歧本身也是信息。
- 模型是某一时刻训练分布的 Snapshot，现实会 Drift。
- 可靠系统必须知道什么时候不应该自动回答。
- 先诊断再优化，Error Analysis 往往比盲目 Scale 更重要。

### 第 8 阶段

- 大模型项目应该拆成一串可证伪的小实验。
- Test Set 不是剩余数据，而是未来使用场景模拟器。
- 模型价值来自相对 Baseline 的提升和成本差异。
- 成功标准必须在看到结果之前定义。
- 实验记录、失败结论和错误分析都是研发资产。

### 第 9 阶段

- 模型是完整训练状态，不是一个权重文件。
- 所有影响结果的东西都应该版本化。
- 单次训练结果具有随机性，要考虑 Seed 和方差。
- 训练日志和实验记录是科学证据，不是临时垃圾。
- 专业模型必须可追溯到数据、代码、配置、评测和规则。

### 第 10 阶段

- 上线才是真实考试，离线 Test 只是模拟。
- 生产质量由完整系统决定，不由单个 LLM 决定。
- 必须主动监控沉默的 FN，而不是只看报警项。
- 专家不是失败兜底，而是持续学习系统的一部分。
- 每个新模型都默认可能退化，必须 Shadow/Canary/Regression/Rollback。

### 第 11 阶段

- 答案和对答案的自知能力是两种不同能力。
- 不确定性要区分问题本身不确定与模型知道得不够。
- Accuracy 与 Calibration 必须分别评估和优化。
- 拒答、补信息、转专家是专业系统能力，不是失败。
- 最终目标是最小化高代价业务错误，而不是最大化模型自信或自动化率。

### 第 12 阶段

- 为什么这条数据会出现在我的数据库里？
- 哪些数据永远不会被我看到？
- 没有发生投诉但实际存在隐性风险的项目
- 你的数据可能系统性缺失重要样本。
- 改了之后会更好。
- 越接近真正专家能力。
- “某类技术参数项目风险特别高。”

## 第2课：神经网络到完整 Transformer / LLM


### 第 1 阶段

- Neuron = Weighted Sum + Bias + Activation。单个神经元本质上是一个可学习的打分函数。
- Weight 不是人工写死的业务规则，而是训练过程中由 Loss 和 Gradient 共同塑造的参数。
- 一层线性加权只能形成有限的线性决策边界，神经网络的能力来自多层变换与非线性组合。
- 神经网络的价值不是手工列出所有特征，而是让模型从数据中学习内部 Representation。
- 单个神经元是理解深层网络的最小单元：后面所有复杂结构仍然建立在“输入→加权→变换→输出”之上。

### 第 2 阶段

- No Activation ⇒ Deep Linear Model。没有非线性激活函数，多层线性层可以合并成一个线性变换。
- Activation Function 的核心作用是引入非线性，使网络能够表示弯曲、分段和更复杂的决策边界。
- ReLU / GELU / SiLU 的差异主要影响数值形状、梯度流和优化行为，不代表某一种激活函数“更懂政府采购”。
- 激活函数会影响梯度是否容易传播，因此它既是表达能力问题，也是训练稳定性问题。
- 对预训练模型而言，Activation 是架构的一部分，不能因为“另一个函数看起来更好”就随意替换。

### 第 3 阶段

- Hidden Layer ≠ Human Rule Table。隐藏层不是一张可直接阅读的专家规则表。
- Representation 是分布式的：一个业务概念通常由很多维度共同编码，而不是对应某一个神经元。
- Depth 的价值来自多层函数复合，让模型逐步把表面输入转换成更抽象的内部特征。
- 更深 ≠ 自动更好；只有在优化稳定、数据足够、架构合理时，深度才可能转化为能力。
- “模型内部形成了某种表示”是需要通过探针、消融和行为实验验证的工程判断，不能只凭直觉解释。

### 第 4 阶段

- Forward Propagation = 在固定参数下把输入逐层变成输出；Forward 本身不等于学习。
- 每一层都同时有“数值”和“Shape”，Shape 跟错会直接导致矩阵运算或后续层语义出错。
- Logit 是模型原始打分，Probability 是经过 Sigmoid/Softmax 等变换后的分数，Business Decision 还要再经过 Threshold。
- 同一个输入和同一组参数下，Forward 应是可重复的计算过程；训练发生在后续 Loss、Backward 和 Optimizer Step。
- 理解 Forward 的关键不是背每个矩阵，而是能追踪：输入表示 → 中间表示 → 输出分数。

### 第 5 阶段

- Backpropagation = Loss 通过 Chain Rule 沿计算图反向传播，把错误信号分配给可训练参数。
- Gradient ≠ Parameter Update。backward() 计算梯度，optimizer.step() 才真正改变参数。
- Credit Assignment 的核心是回答“最终错误应该由前面哪些参数承担多少责任”。
- 深层网络中的梯度是局部导数连续相乘的结果，因此会遇到梯度过小、过大和数值不稳定问题。
- 只有 requires_grad / 可训练参数会被优化；被冻结参数即使参与 Forward，也不应该被更新。

### 第 6 阶段

- Gradient 告诉你局部方向，Optimizer 决定怎样利用当前和历史梯度真正更新参数。
- Learning Rate 是最关键的更新尺度：太大可能震荡/发散，太小可能训练极慢或停在差的区域。
- Adam / AdamW 会利用梯度一阶、二阶统计量做自适应更新，它不是“自动保证收敛”的魔法。
- Weight Decay 与 Learning Rate 是不同控制量：前者用于参数规模正则化，后者控制更新步幅。
- Warmup / Decay / Scheduler 属于完整优化策略的一部分，不能把“优化器名称”当成全部训练方案。

### 第 7 阶段

- Deep Network 需要 Signal Stability。深度增加以后，激活和梯度的尺度必须被主动控制。
- Initialization 决定训练从什么数值尺度起步；坏初始化可能让信号一开始就爆炸或衰减。
- Normalization ≠ Data Cleaning。它是在网络内部稳定表示尺度，不是对原始采购数据做清洗。
- Residual Connection 提供 Identity Path，让信息和梯度可以跨层直接传播，是深层 Transformer 可训练的重要条件。
- Initialization + Normalization + Residual 是一套协同稳定机制，但它们只能让深网络更容易训练，不保证数据和任务本身正确。

### 第 8 阶段

- Token ID ≠ Semantic Meaning。整数 ID 本身没有语义，语义来自对应的 Embedding Vector。
- Embedding 本质是一个可学习查表：离散 Token → 连续高维向量。
- Embedding Space 的几何关系可以承载相似性，但“距离近”不自动等于法律规则或业务等价。
- Embedding 的每一维通常没有稳定的人类命名含义，语义是分布式编码。
- 输入 Embedding 只是起点；经过 Attention 和 MLP 后，表示会随上下文不断变化。

### 第 9 阶段

- Token ≠ Word ≠ Concept。Tokenizer 切出来的是模型计算单位，不是天然语言学词或完整知识概念。
- Subword Tokenization 在词表大小与序列长度之间做折中，使模型能处理未登录词和组合词。
- Tokenizer 是模型协议的一部分；训练、推理和微调必须使用与模型匹配的 Tokenizer。
- Tokenization 直接影响 Context 占用、训练成本、数字/法规文号切分和领域术语效率。
- 随意更换或扩展 Tokenizer 可能导致 Embedding/LM Head 尺寸和已学参数失配，需要专门训练与兼容性验证。

### 第 10 阶段

- 没有 Position Information 的 Self-Attention 很难区分相同 Token 集合的不同顺序。
- Positional Encoding 的任务是把“谁在前、谁在后、相距多远”注入模型表示。
- RoPE 通过旋转 Query/Key 表示位置关系，使 Attention Score 同时感知内容与相对位置。
- Max Context Length 是架构/训练/推理共同约束，不等于模型在整个最大长度上都同样可靠。
- Long-Context Extension ≠ Free Extrapolation。扩展上下文窗口仍需要位置编码、训练分布和评测共同支持。

### 第 11 阶段

- Self-Attention 的核心不是“平均看所有 Token”，而是根据 Query–Key 匹配动态决定从哪里读取信息。
- Query 决定“我要找什么”，Key 决定“我怎样被匹配”，Value 承载“真正被汇聚的内容”。
- Attention Score 经过缩放与 Softmax 后形成权重；除以 √d_k 是为了避免高维点积过大导致 Softmax 饱和。
- Causal Mask 保证 Decoder 当前位置看不到未来 Token，从而维持 Next Token Prediction 的因果训练目标。
- Attention Weight ≠ Human Explanation。高权重说明当前计算中的信息路由强度，不等于法律因果解释或最终决策依据。

### 第 12 阶段

- LLM ≠ One Giant Layer。现代 Decoder-only LLM 是许多 Transformer Block 重复堆叠形成的系统。
- RMSNorm / Residual / Attention / MLP 各自承担不同角色：稳定、信息通路、跨 Token 交互和逐位置非线性变换。
- Decoder-only Transformer 使用 Causal Mask，通过 Next Token Prediction 学习序列分布。
- LM Head 把最终 Hidden State 映射成 Vocabulary Logits；生成则把“选一个 Token”循环成完整文本。
- KV Cache 只是在推理时减少历史 Attention 的重复计算，它不会给模型增加新知识或改变已训练权重。

## 第3课：GPU 环境与第一个开源大模型


### 第 1 阶段

- Compute Capacity ≠ Memory Capacity。GPU 算得快，不代表显存一定装得下模型和上下文。
- RAM ≠ VRAM。系统内存与 GPU 显存位置、带宽和用途不同，不能用硬盘/内存数字替代显存预算。
- Inference ≠ Training。训练除了权重，还需要梯度、优化器状态和激活，因此显存需求通常远高于推理。
- GPU Speed 依赖并行算子、数据搬运和 Kernel；不是所有工作都比 CPU 快。
- “模型权重能装下”只是第一道门，真正可用还要给 KV Cache、Batch、Context 和运行时 Workspace 留余量。

### 第 2 阶段

- Driver ≠ CUDA Toolkit ≠ PyTorch CUDA Build。三者是不同层级，必须分别确认版本与兼容性。
- nvidia-smi 能看到 GPU ≠ PyTorch 一定能用 CUDA；它只能证明驱动层基本工作。
- 正确诊断顺序应从 Hardware/Driver → Python Environment → PyTorch Build → cuda.is_available() → Tensor/Model 实测。
- Python Interpreter / Virtual Environment 也是环境链的一部分，同一机器不同环境可能安装完全不同的 PyTorch。
- 遇到 CUDA unavailable 时先定位断在哪一层，不要直接“全卸载重装”。

### 第 3 阶段

- config.json 定义 Architecture Metadata，Tokenizer 定义 Text↔Token 协议，safetensors 保存真正的参数数值。
- Model Weight ≠ Model Code。权重只是训练后的参数状态，模型结构仍需要代码和配置解释。
- Shard 只是把大权重文件分箱保存，Index 记录参数在哪个 Shard；分片本身不改变模型能力。
- 一个可运行 Checkpoint 需要结构、权重、Tokenizer 和必要配置彼此匹配，不能随意混用不同仓库文件。
- Generation Config / Chat Template 等文件影响推理协议，但它们与核心权重承担的职责不同。

### 第 4 阶段

- from_pretrained() 不是一个神秘黑盒：读取 Config → 构建模型结构 → 加载权重 → 设置 dtype/device → 返回可运行对象。
- Download Complete ≠ Model Ready。文件到磁盘后还要完成解析、权重装载和设备放置。
- device_map / Offloading 改变“权重放在哪里”，不等于改变模型语义能力。
- Loading Peak Memory 可能高于最终驻留内存；能保存文件不代表加载过程一定不会 OOM。
- 第三方 Remote Code / 自定义模型实现属于执行代码边界，加载前要关注来源与安全，而不只是模型参数大小。

### 第 5 阶段

- 完整生成链是 Text → Token IDs → Tensor → Forward → Logits → Decode，不应把“文字直接进入神经网络”当作真实过程。
- generate() 本质是 Autoregressive Loop：反复 Forward、选择下一个 Token、追加到序列再继续。
- Tokenizer / Chat Template 是输入协议的一部分；协议不一致会让同一模型表现明显变化。
- Logits ≠ Final Text。Logits 只是下一 Token 的分数，解码策略决定如何从分数得到实际 Token。
- 推理时要区分 eval()/no_grad() 与训练状态，避免无谓梯度和随机层行为影响结果与显存。

### 第 6 阶段

- Weight Memory 的第一近似 = Parameter Count × Bytes per Parameter；7B 模型在不同 dtype 下显存差异巨大。
- dtype ≠ Quantization。FP16/BF16 是浮点精度选择，INT8/INT4 量化是更强的离散近似与压缩。
- Quantization = Memory/Quality/Kernel Trade-off。更低 bit 通常更省显存，但可能带来精度损失和算子限制。
- Smaller Storage ≠ Faster Inference。真实速度还取决于硬件是否有高效低位宽 Kernel。
- Training Precision 与 Serving Precision 可以不同；选择精度必须匹配训练稳定性、推理质量和硬件支持。

### 第 7 阶段

- Serving VRAM ≠ Weight VRAM。完整显存账本至少包括 Weights + KV Cache + Activations/Workspace + Runtime Overhead。
- Context Length 增长会显著扩大 KV Cache；“模型刚加载成功”不代表长上下文时仍不会 OOM。
- Batch / Concurrency 会让多个请求同时占用 KV Cache，因此单请求显存不能直接代表服务显存。
- OOM 可能发生在生成过程中而不是加载阶段，所以显存预算必须覆盖真实 Workload Shape。
- 专业显存预算必须留 Headroom，不能把理论可用显存全部吃满。

### 第 8 阶段

- Greedy = 每一步选择最高概率 Token；Sampling = 按概率分布随机选择，两者只是解码策略不同。
- Temperature / Top-k / Top-p 改变候选分布和随机性，不会给模型增加新知识。
- More Random ≠ More Creative Truth。采样提高多样性，也可能增加不稳定和错误表达。
- 固定 Seed 可以改善实验复现，但不同 Kernel、并发和硬件下不一定保证逐 Token 完全一致。
- Low Temperature ≠ High Truthfulness。确定性更高不代表事实、法规和业务判断一定正确。

### 第 9 阶段

- Latency ≠ Throughput。单个用户等多久与服务器单位时间处理多少请求是不同指标。
- TTFT ≠ Decode Speed。首 Token 等待时间和后续 Token 流速来自不同阶段瓶颈。
- Batching 可以提高 GPU 利用率和吞吐，但过度 Batch 也可能增加排队与单请求延迟。
- Continuous Batching / PagedAttention 的价值在于动态请求与 KV Cache 管理，不是改变模型能力。
- Serving Benchmark 必须使用真实输入长度、输出长度、并发和 P95/P99，而不是只看一个 tokens/s。

### 第 10 阶段

- Best Leaderboard Model ≠ Best Procurement Model。选型必须看真实政府采购任务，而不是只看通用榜单。
- 模型选型是多目标问题：中文理解、Context、RAG/Tool 兼容、质量、延迟、显存、许可证和部署成本都要一起看。
- Baseline 必须可复现：固定模型版本、Tokenizer、Prompt、解码参数和 Benchmark，才能公平比较。
- Model Comparison 要在 Same Protocol 下进行；测试集、Prompt 或硬件不同，分数不能直接归因给模型。
- 最终选择的是 System Fit，而不是参数量最大或宣传最强的模型。

## 第4课：政府采购数据工程与训练数据集


### 第 1 阶段

- 文件 ≠ 数据样本
- Schema = 我们对“一个样本是什么”的正式契约
- 先定义任务，再定义样本，再开始收数据
- 一个原始采购文件可以产生很多不同任务的数据
- Input、Label、Evidence、Metadata 必须分清楚
- 数据最重要的不是“多少条”， 而是每一条到底代表什么

### 第 2 阶段

- 文件里“看得见文字” ≠ 文件里真的存着可直接读取的文字
- Extract Text ≠ Parse Document
- 文档解析真正要恢复的是： 文字 + 阅读顺序 + 结构 + 表格 + 来源位置
- OCR 是扫描页的后备方案， 不是所有PDF默认第一步
- 原始文档解析时不要过早丢失： 页码、位置、区块类型、来源信息
- 解析质量不是看“程序有没有报错”， 而是看“下游业务判断会不会被解析错误带偏”

### 第 3 阶段

- Clause Segmentation ≠ Sentence Splitting 一条采购条款可能有很多句
- 标题不是靠“字体大”一个特征判断， 而是多个结构信号共同决定
- 文档结构恢复的核心不是切得越细， 而是恢复“谁属于谁”
- Target Clause 可以很小， 但它必须保留 Parent Section 和必要 Context
- 表格中的一行、一个评分项， 也可能是一条真正的业务 Clause
- 结构恢复错误会直接污染： 风险类型、Train/Test切分、RAG、SFT和最终审查结果

### 第 4 阶段

- Cleaning ≠ Rewriting 清洗不是改写原文
- 原始文本必须保留， Normalized Text 应该是派生版本
- 可以统一“表现形式”， 不能擅自统一“业务含义”
- 数字、单位、否定词、比较符号、日期、编号 都属于高风险信息
- 自动修复必须可追踪、可回滚、可审计
- 不确定的时候， 宁可标 Warning，也不要偷偷猜

### 第 5 阶段

- 主要让模型偏科。
- 会让考试成绩造假。
- Data Count ≠ Independent Information Count
- 去重 ≠ 删除所有相似文本
- Exact Duplicate 最容易， Near Duplicate 才是真正困难的部分
- 模板相同 ≠ 项目完全相同
- Duplicate Detection 应先“聚类和建立关系”， 再决定是否删除

### 第 6 阶段

- Benchmark 泄漏不一定是把答案文件直接放进训练集。
- Split 的单位不一定是 Row， 很多时候应该是 Project / Group
- Train / Validation / Test 的核心区别 不是“比例”，而是“用途”
- 同一个 Project 的 Clause 通常不应该跨 Train / Test
- Duplicate Group / Template Group 也不能随便跨 Split
- 时间是最接近真实生产环境的一种隔离方式
- Test Set 一旦开始被反复看， 它就正在慢慢变成 Train Set

### 第 7 阶段

- 泄漏的本质，是测试问题相关的信息通过某条不被允许的路径参与了模型开发。
- Split不重叠 ≠ 没有泄漏
- Leakage 的本质不是“文件重复”， 而是答案相关信息越过了不该越过的边界
- 泄漏既可能发生在数据里， 也可能发生在Prompt、RAG、规则和人脑里
- 时间方向非常重要： 未来信息不能帮助模型回答过去时点的测试问题
- Test被反复用于改系统， 就会逐渐变成Validation
- 防泄漏不能只靠“大家小心一点”， 必须建立Benchmark Firewall

### 第 8 阶段

- ClauseUnit ▼ 事实层 What does the document say? ▼ 判断层 Is there a potential risk? ▼ 分类层 What kind of risk? ▼ 证据层 Why / based on what? ▼ 不确定性层 Can we conclude confidently? ▼ 行动层 What should happen next? ▼ AnnotationSchema_V0.1
- 政府采购专业 Label Schema 的目标，不是把所有 Clause 压缩成“有风险 / 没风险”，而是把专家的判断拆成风险状态、风险类型、不确定性、理由、证据、行动建议和标注来源，让“专家脑子里的专业判断”第一次变成可以训练、可以评测、可以审计的数据结构。
- missing ≠ fabricated
- 二百五十五、本阶段最重要的 7 个“≠”

### 第 9 阶段

- “这个专家很厉害，所以他说什么就是什么。”
- 明确规则 + 独立标注 + 分歧检测 + 专家裁决 + 可追溯记录。
- “删掉这条，太麻烦了。”
- 为什么他们会不一致？
- 专家分歧常常是在帮助我们找到 Dataset 最重要的边界。
- Label定义不清 上下文不足 风险类别边界重叠 标注指南没覆盖这种情况 案例本身就是Hard Case 法规依据存在解释空间
- 使用自己的经验规则；

### 第 10 阶段

- Hard Negative 不是普通负样本，而是“非常像正样本的负样本”。 它的作用是打掉模型的错误捷径。
- 真正有价值的数据经常是一对，而不是一条。 两个案例越相似、结论越不同，越能暴露模型是否抓住了关键条件。
- 最好的 Hard Case 往往来自真实错误和专家分歧，而不是靠人凭空编故事。 模型错过什么，就围绕什么补数据。
- Boundary Case（边界案例）不是必须强行二选一。 如果合理结论确实依赖缺失上下文，就应该保留 uncertain / needs_review。
- Hard Case 既是训练材料，也是 Benchmark 的压力测试材料。 但同一个案例及其改写版本绝不能一边训练、一边考试。
- Hard Negative 的价值，是让模型不能再靠关键词和表面模式取巧。
- 真正高价值的数据经常不是一条样本，而是一对只差关键条件的对比样本。

### 第 11 阶段

- 一套冻结的数据状态。
- 数据 + 代码版本 + 配置版本。
- final_dataset_v2_really_final/
- 包含哪些样本？ 样本内容是什么？ 用了什么Schema？ 怎么切的Train/Test？ 标签是哪一版？ 处理程序是哪一版？
- Parser v1
- Parser v2
- Dedup threshold = 0.85

### 第 12 阶段

- 只是 Dataset 派生出来的一种使用方式。
- 我已经有 train.jsonl 所以我已经有 Dataset
- Master Data 主数据
- Task Views 训练 / 评测视图
- Governance Assets 治理与审计资产
- 第一，Dataset 不是一个训练文件，而是 Master Data、Task View 和 Governance Asset 的组合。
- 第二，Master Data 是完整真相源，训练数据只是从它派生出来的任务视图。

## 第5课：SFT + LoRA / QLoRA 微调


### 第 1 阶段

- “这是 Prompt。”
- “这是 Response。”
- 我们通过 Chat Template 和 Loss Mask 把这种结构编码进去。
- Token₁ Token₂ Token₃ ... Tokenₙ
- 第一，模型最终训练的不是 JSON、Prompt 或问答表，而是一条 Token 序列。
- 第二，Chat Template 是 Base Model 的对话通信协议，不是排版装饰。
- 第三，Prompt 是模型必须看到的条件，Response 是我们主要希望它学习生成的目标。

### 第 2 阶段

- 第一，SFT 仍然是在做 Next Token Prediction，只是正确答案来自我们的专家数据。
- 第二，Forward 负责产生预测，Cross Entropy 把预测和正确 Token 比较后得到 Loss。
- 第三，Loss 只告诉模型“错多少”，Backward 才通过链式法则计算每个可训练参数应该往哪个方向调整。
- 第四，loss.backward() 负责计算 Gradient，optimizer.step() 才真正更新参数。
- 第五，SFT 的最终效果，是大量小的参数更新不断重塑 P(Response | Prompt)；训练 Loss 下降并不等于真实业务能力一定提升。
- 优化目标正在改善。
- Business Quality ↑

### 第 3 阶段

- 每条训练样本都应该做成 32K。
- 一次序列允许使用的最大 Token 空间。
- 32K Context
- 业务所需上下文 + Response长度 + 显存 + 训练速度 + Batch Size
- 第一，Context Window 是模型容量上限，不等于所有训练样本都应该使用最大长度。
- 第二，Truncation 本质是信息优先级决策；优先保护 Target Clause、决定判断的上下文和完整 Assistant Response。
- 第三，真正专业的顺序是 Context Selection → Tokenize → 必要 Truncation，而不是把完整文档 Tokenize 后粗暴切头或切尾。

### 第 4 阶段

- 对齐 Tensor。
- 尽量让 GPU 算真实训练 Token，而不是 PAD。
- 为了提高 GPU 利用率，把多个独立 Sample 放进同一个计算容器。
- 可能仍然能够 Attention 到 A。
- A A A PAD PAD PAD

### 第 5 阶段

- 仍然使用整个 7B 模型。
- 模型有没有参加训练计算。
- Optimizer 最后可以更新谁。
- 从零重新学习语言和世界知识。
- 未必是最合理的工程选择。

### 第 6 阶段

- 把 Base Model 某一层删掉，再装一个小层。
- Base Model 保留原能力，LoRA 在旁边提供任务相关的修正。
- “重新学习这个巨大矩阵。”
- “学习这个巨大矩阵需要改变多少。”
- 原矩阵 \(W\) 本身是低秩的。

### 第 7 阶段

- 第一，Rank r 决定 LoRA 的低秩适配容量，并线性影响 Adapter 参数量。
- 第二，Alpha 不增加容量；在标准 LoRA 中真正起作用的是 alpha / r 这样的有效 Scaling。
- 第三，Learning Rate 决定参数怎样更新，Alpha 决定 LoRA 分支怎样缩放，两者不是同一个东西。
- 第四，Dropout 是训练阶段的正则化工具，不是能力旋钮，也不是越大越好。
- 第五，任何 r / alpha / dropout 配置都必须放进固定 Dataset、固定 Target Modules、固定 Benchmark 的控制变量实验里判断。

### 第 8 阶段

- A 容量一定更大，因为 64 > 16。
- “Rank 用多少？”
- Rank 多大，并且 LoRA 装在哪里？
- 只训练 Attention 和同时训练 MLP，给模型的适配自由度是不一样的。
- “知识全在 MLP。”

### 第 9 阶段

- Base Model 的存储方式。
- Base Model BF16 / FP16 等 Frozen + LoRA Adapter Trainable
- Base Model 4-bit Quantized Frozen + LoRA Adapter Trainable
- Input Attention MLP Loss Gradient
- 全部都只有4-bit

### 第 10 阶段

- 能推理，不代表能训练。
- Model Weights + KV Cache + Activations / Runtime Buffers
- Model Weights + Forward中间结果 + Backward所需信息 + Gradients + Optimizer States
- BF16 Base 约16-bit/parameter
- NF4 Base 约4-bit/parameter + metadata

### 第 11 阶段

- 第一，真正的 SFT 不是 trainer.train()，而是一份由 Dataset、Template、Mask、Length、Model、LoRA、Optimizer 和 Evaluation 共同构成的训练协议。
- 第二，在正式花 GPU 时间以前，必须人工 Decode Chat Template、检查 Assistant Loss Mask、检查长度和 Trainable Parameters，并先跑 5～20 Step Smoke Test。
- 第三，loss.backward() 只是计算和累积 Gradient，真正改变 LoRA A/B 的时刻是 optimizer.step()；Gradient Accumulation 决定多少个 Micro-batch 合成一次参数更新。
- 第四，Learning Rate、Warmup、Epoch、Batch、Gradient Clipping 各自解决不同问题，不能把一个异常全部归因于“LoRA 参数不够”。
- 第五，Training Loss 下降只说明训练目标的 Token 概率在改善；是否真的成为更好的政府采购模型，必须交给独立 Validation、Hard Case 和最终 Benchmark。
- 真正可靠的 SFT 训练，不是“代码终于跑起来了”，而是我们能够证明：模型看到了正确的 Prompt，只有正确的 Response Token 在产生 Loss，正确的 LoRA 参数在获得 Gradient，每次 Optimizer Step 都在按可复现配置更新它们，而且整个过程能被 Validation 和 Benchmark 独立检验。

### 第 12 阶段

- 训练样本上的目标 Token 概率在上升。
- Logging 告诉你训练过程正在发生什么
- Checkpoint 保存某一时刻的模型 / 训练状态
- Evaluation 检查这个时刻的模型在未训练数据上表现如何
- 政府采购判断更准确 Hard Negative更好 新项目泛化更强 幻觉更少

### 第 13 阶段

- 把原来分开的 Base Weight 和 LoRA 增量提前加在一起。
- 这个 merged checkpoint 本身不会替你保留“可随时拆出来的 LoRA”。
- Merge 前永远保留 Adapter 原件。
- 同样的模型权重收到的是不同 Token 序列。
- Adapter A/B + Adapter Config

### 第 14 阶段

- 微调的价值不是“模型参数变了”，而是它在独立、固定、可复现的业务测试上，证明自己改变了正确的行为，同时没有付出不可接受的回归代价。
- 模型更会预测训练目标。
- 真正高风险条款，
- 漏报了什么，误报了什么。
- 关键词 Shortcut。

## 第6课：RAG、Embedding 与向量检索


### 第 1 阶段

- 第一，Parametric Memory 是模型通过 Weight 表现出来的已有能力与知识；External Knowledge 是模型外部、可以独立更新和检索的知识资产。
- 第二，Fine-tuning 主要改变参数 \(\theta\)，RAG 主要在推理时增加检索证据 \(E\)，把 \(P_\theta(Y|X)\) 变成 \(P_\theta(Y|X,E)\)。
- 第三，Knowledge Base 只是知识仓库，Retriever 负责找证据，RAG 是“检索 → 组装 Context → 生成”的完整系统流程，Prompt 则是最终真正送进模型的输入。
- 第四，SFT 更适合稳定行为和任务模式，RAG 更适合动态知识、巨大知识库、来源追溯和频繁更新；两者不是竞争关系，而是互补关系。
- 第五，RAG 答错以后必须先定位 Knowledge、Retrieval、Ranking、Context 还是 Generation 出错，不能把所有问题统称为“LLM 幻觉”。

### 第 2 阶段

- 第一，RAG Knowledge Base 不是 PDF 文件夹，而是“正文 + Metadata + Provenance + Version + Validity”组成的可治理知识系统。
- 第二，每一份知识都必须能够从 Chunk 追溯到 Document，再追溯到原始 Source；否则 Citation 只是表面上有链接，并不是真正可审计。
- 第三，政府采购知识天然带时间和辖区条件，所以 effective_from / effective_to / jurisdiction / validity_status 必须成为一等字段。
- 第四，新版本不能简单覆盖旧版本；真正的版本管理要保留 supersedes / superseded_by 等关系，因为最新版本不一定是历史问题的正确版本。
- 第五，Metadata、去重、有效性审查和来源验证不是 Embedding 之前的杂活，它们直接决定未来 Retriever 有没有机会找到正确证据。

### 第 3 阶段

- 第一，Chunking 不是把长文本机械切短，而是在定义 Retriever 眼中的“知识最小单位”。
- 第二，Chunk 太大会产生语义稀释，Chunk 太小会产生语义碎片化，所以目标是兼顾检索聚焦度与语义完整性。
- 第三，政府采购法规和采购文件优先采用 Structure-aware Chunking：先尊重章、节、条、款、项等业务结构，再用 Token 长度做二次约束。
- 第四，Overlap 只能缓解局部边界断裂，不能解决远距离依赖；需要时可以用 Parent-Child Retrieval 实现“小单元检索、大上下文生成”。
- 第五，每个 Chunk 必须继承 Document 的版本、时间、辖区、来源和结构 Metadata，否则检索出来的只是匿名文本，无法真正 Citation 和审计。

### 第 4 阶段

- 第一，Embedding 是把 Query 或 Chunk 映射成固定维度向量，使语义相关的文本在模型学出的向量空间里尽量靠近。
- 第二，Dense Retrieval 的核心就是分别得到 Query Vector 和 Document Vector，再用 Cosine、Dot Product 或其它兼容度量做 Top-K 排序。
- 第三，Query 和 Document 必须进入兼容的检索表示空间；有些模型是对称编码，有些模型需要不同的 Query / Document Prefix 或任务指令。
- 第四，Embedding Similarity 只负责候选召回，不等于最终业务正确性；政府采购里的“投标前 vs 中标后”等 Hard Negative 仍可能让语义向量犯错。
- 第五，Embedding Model、Revision、Normalization、Similarity Metric 和编码策略必须版本锁定；换模型通常意味着旧知识向量需要重新计算。

### 第 5 阶段

- 第一，Exact Search 是把 Query 和全部向量逐个比较；ANN 则通过索引结构减少搜索范围，用少量近似误差换更低延迟和更高吞吐。
- 第二，Vector Index 是近邻搜索的数据结构，Vector Database 则还负责向量、Metadata、过滤、增删改、持久化和生命周期管理，两者不是同一个概念。
- 第三，HNSW 的核心直觉是“图导航”，IVF 的核心直觉是“先定位候选区域再局部搜索”；两者都在用搜索范围控制 Recall / Latency Trade-off。
- 第四，Metadata Filter、Similarity Metric、Normalization、Top-K 和 ANN 参数都会直接影响最终检索结果，不能把它们当成与 Embedding 无关的数据库配置。
- 第五，Vector Index 的目标不是单独追求最快，而是在可接受的内存和延迟下，保持足够高的 Index Recall 和真正业务上的 Retrieval Recall。

### 第 6 阶段

- 第一，Retriever 的目标不是让“看起来相关”的文本靠前，而是让真正能够支持问题的 Gold Evidence 尽可能进入足够靠前的位置。
- 第二，Hit@K 看是否至少命中，Recall@K 看 Gold Set 覆盖率，MRR 看第一条正确证据出现得有多早；三者回答的问题不同。
- 第三，政府采购 Retrieval Benchmark 必须包含 Hard Negative、时间版本、辖区和 No-answer Query，否则无法测出真正的业务边界。
- 第四，正确证据没进 Top-K 时，要区分 Knowledge、Chunking、Metadata Filter、Embedding、ANN、Ranking、Version 和 Duplicate 等失败类型，不能一律归咎于 Embedding。
- 第五，Retrieval Evaluation 必须和 Generation Evaluation 分离：先证明“证据找到了”，再讨论“模型有没有正确使用证据”。

### 第 7 阶段

- 第一，BM25 属于 Sparse Retrieval，依赖词项匹配、IDF、词频饱和和长度归一化；它尤其擅长文号、金额、条款号、标准号和专有名词等精确信号。
- 第二，Dense Retrieval 擅长同义改写和语义泛化，但可能淡化数字、编号和细粒度字面差异；因此 Sparse 与 Dense 的盲区具有明显互补性。
- 第三，Hybrid Retrieval 的稳妥第一版是 BM25 与 Dense 并行召回，各自得到候选，再做去重、融合和后续排序，而不是让其中一条路径先把另一条路径的候选空间砍掉。
- 第四，BM25 Score 和 Dense Similarity 通常不能直接裸相加；Score Fusion 需要归一化 / 校准，而 RRF 可以直接利用排名进行相对稳健的融合。
- 第五，Hybrid 是否值得采用，必须回到 ProcurementRetrievalBenchmark_V0.1 比较 Hit@K、Recall@K、MRR、Hard Negative、No-answer 和 Latency，不能因为“用了两种检索”就默认更强。

### 第 8 阶段

- 第一，Retriever 负责高 Recall 召回，Reranker 负责把最相关的候选重新排到最前面；两者优化目标不同。
- 第二，Bi-Encoder 通过独立 Query / Document Vector 实现高效大规模检索，而 Cross-Encoder 让 Query 与候选文本逐 Token 交互，因此更适合细粒度精排，但成本更高。
- 第三，Reranker 只能重排已经召回的 Candidate Set，不能救回根本没进入候选集的 Gold Evidence；所以调试必须先区分 Recall Failure 和 Rerank Failure。
- 第四，政府采购 Reranker 的关键价值是压制“投标前 vs 中标后”“准入 vs 履约”这类语义很近但业务边界不同的 Hard Negative。
- 第五，是否启用 Reranker 必须同时比较 MRR、Gold Rank、Hard Negative 排名改善和新增 Latency / VRAM 成本，而不是只看一个排序分数。

### 第 9 阶段

- 第一，User Query 不一定适合直接检索；Query Processing 的职责是恢复上下文、显式化检索条件和生成必要的检索变体，但绝不能改变用户真实意图。
- 第二，Query Expansion 是“同一意图的多种表达”，Query Decomposition 是“把复杂问题拆成多个子意图”，两者不是一回事。
- 第三，时间、辖区、版本、文号、金额、条款号、否定词和“投标前 / 中标后”等高风险字段必须被精确保护；不确定 Metadata 应标记 unknown 或请求澄清，而不是自动猜。
- 第四，Metadata Filter 可以大幅缩小错误搜索空间，但只有确定条件才适合 Hard Filter；错误过滤比排序错误更危险，因为它会让 Gold Evidence 根本没有机会进入 Candidate Set。
- 第五，Query Rewrite、Multi-query、Routing 和 Metadata Filter 是否值得启用，最终都必须回到 ProcurementRetrievalBenchmark_V0.1 做 A/B，并额外监控 Intent Preservation、Identifier Preservation 和 Metadata Extraction Accuracy。

### 第 10 阶段

- 第一，Retrieval Top-K 只是候选集合，Context Assembly 还必须完成去重、版本检查、父级扩展、证据选择、Token Budget、排序和来源标记。
- 第二，Citation 不是模型随便生成一个编号，而必须形成 CitationID → Evidence → Chunk → Document → Source 的可审计映射，并检查引用是否真的支持对应 Claim。
- 第三，Grounded Generation 允许模型做分析和推断，但必须清楚区分“证据直接支持的事实”和“基于证据的推断”，不能把模型参数记忆伪装成外部证据。
- 第四，证据不足和证据冲突都必须成为正式系统状态；可靠的 RAG 可以说“不足以判断”，也必须能够说明不同版本 / 不同来源之间的冲突。
- 第五，检索到的内容永远是 Data，不是 System Instruction；Context Assembly 同时承担证据组织、引用可追溯和 Retrieval Prompt Injection 防护。

### 第 11 阶段

- 第一，Fine-tuning 改变模型参数和稳定行为，RAG 改变推理时模型能看到的外部证据；两者是互补关系。
- 第二，RAG 的上限首先受知识库质量限制：来源、版本、时间、辖区和有效性如果错，后面的检索越强只会越快找到错误证据。
- 第三，Chunking 定义检索单元，Embedding 定义语义空间，Vector Index 定义怎样快速找到候选；三者分别解决不同层的问题。
- 第四，Retriever 的目标是高 Recall，Hybrid Retrieval 用 BM25 和 Dense 互补，Reranker 再负责把真正 Gold Evidence 压到前排。
- 第五，Query Processing 负责恢复真实检索意图，但不能注入不存在的条件；Metadata Filter 可以显著提升质量，但错误 Hard Filter 会直接杀掉 Gold Evidence。
- 第六，Context Assembly 决定哪些证据真正进入 Prompt，Citation 必须形成从 Claim 到 Evidence、Chunk、Document、Source 的可审计映射，证据不足时 Abstention 是正确行为。
- 第七，真正的 RAG 不是“LLM + 向量库”四个字，而是一套可以分别评测 Knowledge、Retrieval、Ranking、Context、Generation 和 Citation，并能沿 Trace 定位错误的完整系统。

## 第7课：Agent、Tool Calling 与政府采购工作流


### 第 1 阶段

- 第一，Agent 不是“更会聊天的 LLM”，而是 Model + State + Tools + Policy + Loop 组成的任务执行系统。
- 第二，普通 LLM 是 Prompt → Generate，RAG 通常是固定的 Retrieve → Generate Pipeline；Agent 的关键升级是模型可以根据 Observation 动态决定下一步 Action。
- 第三，真正的 Agent Action 必须由 Tool Runtime 实际执行；模型说“我执行了”不等于真实世界已经执行。
- 第四，Workflow 与 Agent 的核心区别不是步骤多少，而是谁决定下一步：Workflow 主要由预定义控制流决定，Agent 允许模型在受控范围内动态决策。
- 第五，Agent 必须维护 State、拥有 Stop Condition，并受 Policy 与 Human Approval 约束；自主程度越高不代表工程质量越高。

### 第 2 阶段

- 第一，LLM 并不会直接执行函数；Tool Calling 的本质是模型生成结构化调用请求，外部 Runtime 真正执行，再把结果作为新的 Observation 返回模型。
- 第二，Tool Definition 告诉模型“有哪些工具”，Function Schema 告诉模型“参数应该长什么样”，Tool Call 只是执行请求，不等于执行已经发生。
- 第三，Runtime 必须负责 Schema Validation、Authorization、Execution、Timeout、Retry 和 Error Handling，不能把这些责任全部交给模型。
- 第四，Tool Result 必须通过 Tool Call ID 和对应调用绑定，并作为数据返回模型；模型必须依据真实结果继续决策，不能在失败时假装成功。
- 第五，Read、Compute、Write 和 External Action Tool 的风险等级不同；参数合法不等于动作有权限，ValidArguments ≠ AuthorizedAction。

### 第 3 阶段

- 第一，Structured Output 的目标不是让模型输出“像 JSON 的文本”，而是得到 Parseable + SchemaValid + SemanticallyValid + PolicyValid 的可执行参数。
- 第二，合法 JSON 只解决语法层；JSON Schema 继续约束 Required、Type、Enum、Nested Object、Array 和是否允许额外字段，但 Schema 正确仍不代表业务语义正确。
- 第三，Semantic Validation 必须检查日期先后、金额范围、字段依赖、互斥条件和标识符一致性；Policy Validation 再决定这个结构化动作是否被授权。
- 第四，Constrained Generation 可以减少格式错误，但不能保证模型选对业务值；ConstrainedSyntax ≠ CorrectSemantics。
- 第五，Validation 失败后可以 Repair、Retry 或 Reject，但 Repair 只能用于确定性、无歧义的格式修复，绝不能为了让 Schema 通过而偷偷猜测缺失业务信息。

### 第 4 阶段

- 第一，系统里“已注册的 Tool”“当前模型可见的 Tool”“当前请求真正可执行的 Tool”必须分成三层；Registered ≠ Visible ≠ Authorized。
- 第二，Tool Registry 不只是函数目录，而是同时保存 Schema、版本、副作用、权限范围、审批要求、状态和审计信息的 Capability Catalog。
- 第三，Least Privilege 是 Agent 工程的核心原则：只给当前任务完成所需的最小能力；根本不暴露的 Capability，比依赖 Prompt 告诉模型“不要调用”更可靠。
- 第四，Permission 必须包含 Resource Scope；同一个 read_file 被允许，不代表可以读取所有文件，同一个发布能力被授权，也不代表可以跳过 Approval。
- 第五，工具很多时应该通过 Tool Discovery、Namespace 和 Dynamic Tool Exposure，把当前任务真正相关的 Tool 子集提供给模型，同时保留禁用、撤销、版本控制和 Fallback。

### 第 5 阶段

- 第一，Tool Calling 解决“这一刻调用什么”，Agent Loop 解决“怎样持续执行直到整个任务完成”；Action Success ≠ Task Success。
- 第二，可靠 Agent Loop 的最小结构是 State → Plan → Act → Observe → Update State → Continue / Stop，而 Plan 应该依赖当前真实 State，不应假装一开始就知道未来全部步骤。
- 第三，Stop Condition 和 Completion Check 必须分开：停止可以因为完成、预算耗尽、不可恢复错误或等待人工，而只有 Completion Requirements 全部满足才叫任务完成。
- 第四，Retry 适合“动作正确但执行暂时失败”，Replan 适合“原策略本身需要改变”；两者混用会导致死循环或无效重试。
- 第五，Agent 必须检测 Repeated Action 和 No-progress，并为 Write Tool 考虑 Idempotency、Checkpoint 和 Resume，否则重试可能造成重复副作用或任务重跑。

### 第 6 阶段

- 第一，Planning 不是写待办清单，而是把 Goal → Subgoal → Executable Task → Dependency → Completion Criteria 变成一个可执行任务模型。
- 第二，复杂任务更适合表示成 Task Graph，而不是单一线性步骤；Dependency 决定 Sequential / Parallel，Join 决定并行分支何时可以重新汇合。
- 第三，一个 Task 最好具有清楚的 Inputs、Preconditions、Action、Outputs 和 Completion Criteria；拆得太粗无法执行，拆得太细则会造成步骤爆炸。
- 第四，可靠规划通常采用“稳定高层骨架 + 动态细节展开”：High-level Plan 可以稳定，Detailed Plan 应根据真实 Observation 随时 Revision。
- 第五，Planning Error 必须和 Tool Execution Error 分开；即使所有 Tool 都成功，只要遗漏 Subtask、依赖错误或错误并行化，整个任务仍然可能失败。

### 第 7 阶段

- 第一，Agent Memory 绝不等于把全部聊天历史塞回 Context；Persistent State ≠ Working Context，前者保存真实任务状态，后者只提供当前一步最需要的信息。
- 第二，Conversation History 只是交互历史，Task State 才应该成为当前任务的结构化 Source of Truth；Artifact Store 保存大对象，State 只保存必要引用。
- 第三，Short-term Memory 服务当前任务，Long-term Memory 服务跨任务信息，但长期记忆必须有 Write Policy、Validity、Provenance 和 Staleness Control。
- 第四，Observation 不能直接修改 State，必须经过 State Transition Rule；Task State 还需要 Version 和并发控制，避免 Lost Update。
- 第五，Working Context 应该从 State、Recent Observation、Relevant Memory、Artifacts、RAG Evidence 和 Tool Schema 中按当前 Subtask 选择，而不是 Dump Everything。

### 第 8 阶段

- 第一，RAG + Tools Routing 的核心不是“选择一个最方便的工具”，而是先确定这个问题真正的 Source of Truth 在哪里。
- 第二，规则依据优先走 RAG，实时结构化业务事实优先走权威数据库，具体文件内容走 File Tool，确定性计算走 Compute Tool，改变现实状态的请求才进入 Action Tool。
- 第三，Routing 至少要同时考虑 Information Type、Authority、Freshness、Determinism 和 Side Effect；同一个用户问题完全可能需要多个 Source 联合完成。
- 第四，Vector Search 不能替代业务数据库，Memory 不能替代更权威的实时系统，LLM 参数知识也不能替代当前有效规则或实时项目状态。
- 第五，多 Source 结果进入 Working Context 前必须保留 Provenance、Version、Time 和 Authority；如果来源冲突，必须显式解决或标记 needs_review，不能让模型静默选边。

### 第 9 阶段

- 第一，可靠 Agent 的目标不是“永不失败”，而是 Fails Explicitly + Recovers Safely + Escalates When Needed；Retry 只是 Recovery 的一种。
- 第二，失败必须先分类：Transient Failure 才适合 Retry，Validation Error 应修参数或 Replan，Authorization / Policy Failure 应停止或请求权限，Terminal Failure 应明确终止。
- 第三，有副作用的 Action 一旦超时，不能直接视为失败；Timeout ≠ DefinitelyFailed，必须先 Verify 执行状态，再决定是否用同一个 Idempotency Key 重试。
- 第四，Partial Failure、Rollback、Compensation 和 Circuit Breaker 都属于真实 Agent 必备的恢复机制；多步任务不能只有“成功 / 失败”两个状态。
- 第五，Human-in-the-loop 至少要区分 Clarification、Approval 和 Escalation；需要人工时 Agent 应进入正式暂停状态，而不是继续猜测或绕过控制。

### 第 10 阶段

- 第一，Agent Safety 最重要的两条边界是 UntrustedContent ≠ TrustedInstruction 与 ModelDecision ≠ Authorization。
- 第二，Prompt Injection 真正危险的地方不是模型说错话，而是恶意内容是否能够穿透模型并驱动真实 Tool；因此 Tool Result、RAG Evidence、文件和网页都必须默认视为不可信数据。
- 第三，安全首先依赖 Least Privilege、Capability Isolation、Read / Write Separation 和 Resource Scope，而不是依赖模型“自觉不调用危险工具”。
- 第四，高影响动作必须经过真实 Approval Gate 与明确 Action Intent；讨论 ≠ 草稿 ≠ 执行，模型声称“已批准”也绝不等于系统批准。
- 第五，Secret、敏感数据和访问范围必须由 Runtime 隔离；模型不需要知道 Credential 本身，只需要通过受授权 Tool 使用能力。
- 第六，真正的 Agent Safety 必须由 Runtime Policy 强制执行，并通过完整 Audit Trail 证明“谁请求、谁批准、为什么放行、真正执行了什么、结果是什么”。

### 第 11 阶段

- 第一，LLM 不是 Agent；Agent 是 Model + State + Tools + Policy + Loop，模型只是决策组件。
- 第二，Tool Calling 不是模型直接执行函数，而是 Structured Tool Request → Runtime Execution → Tool Result → New Observation。
- 第三，复杂任务必须经过 Planning 与 Task Graph，Agent Loop 必须依赖真实 State，而不是只靠聊天历史。
- 第四，RAG、Database、File、Compute、Action Tool 不能混为一谈；Routing 首先要找到正确 Source of Truth。
- 第五，可靠 Agent 不是永不失败，而是失败以后能够正确 Retry、Replan、Verify、Fallback、Compensate 或 Escalate。
- 第六，Agent Safety 不是让模型“更听话”，而是用 Least Privilege、Capability Boundary、Approval Gate、Data Boundary 和 Runtime Policy 阻止不该发生的真实动作。
- 第七，真正可发布的 Agent 必须让 Planning、Tool、State、Recovery、Safety、Evidence、Completion 与 Audit 都能单独评测和 Trace；AgentQuality ≠ FinalAnswerQualityOnly。

## 第8课：CPT 与高级领域适配


### 第 1 阶段

- 第一，CPT 是在领域语料上继续执行 Next Token Prediction，让模型参数适应新的 Domain Distribution；它不是 SFT，也不是把知识库简单写进 Weight。
- 第二，CPT 学的是领域语言与统计结构，SFT 学的是任务行为，RAG 提供当前外部证据，Agent 负责受控执行工作流。
- 第三，课程把 CPT 放在第八课，但真实训练顺序通常更接近 Base → CPT → SFT；如果在 SFT 后直接大量 CPT，可能破坏原有对齐行为。
- 第四，CPT 最适合“大量高质量无标注领域语料 + 明显领域分布差距”的场景；实时知识、结构化输出和任务格式问题往往应该优先用 RAG 或 SFT。
- 第五，CPT 的核心风险包括 Catastrophic Forgetting、Domain Over-specialization 和 Benchmark Contamination，所以必须同时评测领域收益、通用能力回归和数据防泄漏。

### 第 2 阶段

- CPTCorpus ≠ DocumentDump。Corpus 是你希望模型长期吸收的领域分布，不是采购文件仓库。
- MoreDocuments ≠ MoreSignal。真正有意义的是经过质量过滤、去重和领域相关性折算后的 Effective Tokens。
- CorpusQuality × Coverage 决定 CPT 上限。训练更久不能弥补语料里根本不存在的领域覆盖。
- Authority ≠ Representativeness。权威法规很重要，但只训练法规并不能代表完整政府采购语言世界。
- Coverage 是多维空间。文件类型、行业、地区、时间、复杂度和生命周期必须一起看，不能只看总 Token。

### 第 3 阶段

- Token ≠ Word ≠ Concept。Token 是模型输入单位，不是天然语言学词，也不是一个完整知识概念。
- High Fragmentation ≠ No Knowledge。切得碎首先意味着效率和表示成本上升，不等于模型一定不懂。
- TokenizerVocabulary ↔ EmbeddingRows。Tokenizer 是模型架构的一部分，不是随便替换的文本工具。
- Audit First, Modify Second。先量化碎片率、Token 成本和真实错误，再决定是否动词表。
- AddToken ≠ AddKnowledge。新增 Token 只新增 ID 和参数入口，知识必须通过 CPT 学出来。

### 第 4 阶段

- ObjectiveFormula 相同 ≠ LearningContext 相同。Next Token Prediction 的公式没变，但 Sequence 怎样构造会改变模型看到的条件上下文。
- Sequence Boundary = Dependency Boundary。切在哪里，会决定哪些跨段关系能够在一次训练上下文中被直接学习。
- ChooseContextLength ≠ MaxSupportedContext。Context Length 应由任务依赖距离、文档长度分布和计算预算共同决定。
- Attention Mask ≠ Loss Mask。前者控制能看什么，后者控制哪里算损失，这是两套完全不同的机制。
- TruncationPolicy = ImplicitSamplingPolicy。截断不是简单裁长度，而是在重新定义哪些文档区域更常进入训练。

### 第 5 阶段

- CorpusShare ≠ TrainingShare。原始数据占比只是“你有什么”，训练占比才决定“模型实际看什么”。
- SamplingPolicy = GradientAllocationPolicy。采样策略本质上是在给不同能力分配训练梯度。
- Oversampling = SignalAmplification + DuplicateExposure。过采样能强化稀有能力，也会放大重复和过拟合风险。
- SameTrainingShare ≠ SameExposure。同样的训练占比，对不同大小的 Unique Token Pool 会产生完全不同的重复曝光。
- Eligibility ≠ Priority。Filter 决定能不能训练，Weight 决定有资格的数据训练多频繁。

### 第 6 阶段

- SharedParameters ⇒ CapabilityInterference。模型能力共享参数，学习新领域可能干扰旧能力。
- DomainGain ≠ NetModelGain。领域能力上涨只是收益的一面，原有能力回归必须同时计入。
- Overfitting ≠ Forgetting。前者是新任务泛化变差，后者是旧能力被新学习破坏。
- BestDomainCheckpoint ≠ BestReleaseCheckpoint。领域分数最高的模型，不一定是综合能力最适合发布的模型。
- WeightDistance ≠ CapabilityRegression。参数漂移只能做诊断，行为 Benchmark 才是最终证据。

### 第 7 阶段

- DetectForgetting ≠ PreventForgetting。发现遗忘是诊断，能力保持是训练控制。
- Retention ≠ FreezeEverything。能力保持不是不让模型变化，而是让变化发生在值得变化的地方。
- Replay = OldDistributionReminder。回放的本质是让旧分布在训练过程中继续获得梯度支持。
- Retention = Data Constraint + Objective Constraint + Parameter Constraint。能力保持可以从数据、目标函数和参数更新范围三个层面同时实现。
- ReferenceModel ≠ GroundTruth。参考模型只是行为锚点，不是永远正确的老师。

### 第 8 阶段

- SyntheticData ≠ FreeNewKnowledge。合成数据能扩展表达和组合覆盖，但不能凭空创造可靠事实。
- SyntheticGeneration 必须由 CoverageGap 驱动。先发现真实语料缺口，再生成，不做无目标数据膨胀。
- SurfaceDiversity ≠ DistributionDiversity。句子看起来不同，不代表训练分布真的扩展。
- Generated ≠ TrainingEligible。合成数据必须经过验证、去重、证据检查和风险审核才能进入训练。
- TeacherModel ≠ GroundTruth。教师模型是候选数据生成器，不是事实权威。

### 第 9 阶段

- DomainGap ≠ BehaviorGap。不懂领域和不会按要求做任务，是两个不同问题。
- TrainingChoice 必须由 ErrorDiagnosis 驱动。先判断错误发生在哪一层，再决定 CPT、SFT、RAG 或 Agent。
- DomainCompetence ≠ InstructionBehavior。领域底座能力和任务行为能力必须分层看。
- CPT = WorldModeling，SFT = BehaviorShaping。CPT 主要塑造领域表示，SFT 主要塑造任务行为。
- CourseOrder ≠ ProductionTrainingGraph。课程先学 SFT 后学 CPT，不代表真实训练顺序就应该如此。

### 第 10 阶段

- CPTExperiment ≠ ModelRelease。训练跑完只是得到实验 Checkpoint，不代表模型可以发布。
- ModelRelease ≠ WeightsOnly。真正模型版本必须包含 Tokenizer、配置、数据血缘、评测证据和 Release Manifest。
- NoFrozenBaseline = NoReliableComparison。没有固定基线，就无法可靠证明模型到底变好还是变坏。
- Scale amplifies Signal and Error。扩大训练规模会同时放大正确方向和错误配置，所以 Full Run 前必须先做 Pilot。
- BestCheckpoint = MultiObjectiveDecision。最优发布 Checkpoint 不是 Loss 最低，而是领域收益、通用保持、成本和兼容性的综合折中。

## 第9课：Gold Benchmark、评测与可靠性


### 第 1 阶段

- Benchmark ≠ DatasetOnly。Benchmark 是被冻结的数据、协议、指标与治理的组合。
- Training ≠ Validation ≠ Test ≠ Gold Benchmark。四者的核心区别是它们在模型开发生命周期中的信息权限不同。
- NoGradientLeakage ≠ NoEvaluationLeakage。即使没有直接训练，也可能通过反复调参产生决策泄漏。
- ComparableScore requires ComparableProtocol。协议、Prompt、阈值、评分脚本不同，分数不能直接归因给模型。
- Component Eval ≠ End-to-End Eval。组件评测负责定位问题，端到端评测负责判断结果是否真正成功。

### 第 2 阶段

- ExpertOpinion ≠ GroundTruth。专家意见只是输入，Gold Truth 来自受控标注与裁决流程。
- Gold = AuthorityByProcess。Gold 的权威性来自 Schema、证据、独立判断、裁决和版本治理，而不是单一专家身份。
- BadSchema + GoodExperts = UnstableGold。标注结构和边界没定义清楚，再好的专家也会产生不稳定标签。
- GoodExpert ≠ GoodAnnotator。领域知识和高一致性标注能力是两种不同能力。
- Agreement Metric ≠ Ground Truth Quality。一致性高不代表一定正确，一致性低也不等于谁必须被淘汰。

### 第 3 阶段

- CorrectAnswer ≠ CompleteEvaluation。最终答案正确，不代表过程、证据和系统行为都可靠。
- WhatYouMeasure → WhatYouCanImprove。评测维度决定你能诊断和优化到什么粒度。
- TaskType → EvaluationLogic。分类、检索、生成、Agent 不应该被同一套指标粗暴衡量。
- Outcome ≠ Process。结果对不代表过程可靠，尤其在需要审计的系统里。
- SameErrorRate ≠ SameRiskProfile。错误数量相同，错误结构和严重度可能完全不同。

### 第 4 阶段

- Accuracy ≠ RiskQuality。类别不平衡时，高 Accuracy 可能掩盖风险类完全失效。
- Precision 对应误报负担，Recall 对应漏报风险，两者必须绑定业务代价。
- SameModel + DifferentThreshold = DifferentOperatingPoint。Threshold 是部署行为的一部分。
- PRCurve = OperatingTradeoffMap。不要只看单个阈值，要看整条误报—漏报权衡。
- AggregateMetric 必须配合 PerClassMetric，否则稀有关键类会被平均掉。

### 第 5 阶段

- FluentAnswer ≠ CorrectAnswer。语言流畅和事实正确是两个不同维度。
- ReferenceSimilarity ≠ SemanticCorrectness。文本重合度不能替代语义正确性。
- Factuality ≠ Groundedness。事实可能是真的，但当前证据未必支持。
- AnswerLevelEval 应尽可能拆到 ClaimLevelEval，否则很难定位幻觉。
- CitationPresent ≠ CitationCorrect，而 CitationCorrect ≠ CitationComplete。

### 第 6 阶段

- RAGFailure ≠ LLMFailure。RAG 错误必须分层归因。
- RetrievedContext = LLMVisibleWorld。Retriever 决定模型实际看到的证据世界。
- RetrievalRecall ≠ RankingQuality。找到了和排对了是两个问题。
- RetrievedDocs ≠ FinalContext。Context Builder 还可能丢证据或引入噪声。
- GoodContext ≠ GoodAnswer。上下文正确不代表生成一定正确。

### 第 7 阶段

- ToolCallSuccess ≠ TaskCompletion。工具调用成功不等于真实任务完成。
- AgentEval = OutcomeEval + TrajectoryEval。结果和执行轨迹必须同时评。
- Action = Tool + Arguments。只评工具名远远不够。
- HappyPathSuccess ≠ RobustAgent。没有故障注入就测不出恢复能力。
- ActionSuccess ≠ PolicySuccess。成功执行的动作仍可能违反权限或安全策略。

### 第 8 阶段

- OverallScore ≠ SliceReliability。总体平均不能证明所有关键场景都可靠。
- Average 会隐藏 Heterogeneity。不同子群性能可能差异巨大。
- Difficulty ≠ LengthOnly。真正难度来自语义边界、结构、证据、噪声和稀有度。
- SingleSlice 可能遗漏 InteractionFailure，交叉切片是生产评测的重要补充。
- PointEstimate ≠ Certainty。Slice 指标必须结合 Support 和不确定性。

### 第 9 阶段

- ConfidenceScore ≠ ProbabilityOfBeingCorrect。置信分必须通过真实数据校准。
- Accuracy ≠ Calibration。答得准和知道自己有多确定是两个能力。
- ReliableAI = AnswerCorrectly + AbstainAppropriately。合理拒答是可靠性的一部分。
- AccuracyWithoutCoverage 可能误导，拒答系统必须同时报告 Coverage。
- RiskCoverage 是选择性预测的核心权衡。

### 第 10 阶段

- NoExactDuplicate ≠ NoContamination。没有完全重复只能说明最浅层没有泄漏。
- Semantic Independence > String Independence。Benchmark 独立性要覆盖语义、项目、血缘和派生关系。
- HumanExposure 也是 Benchmark Exposure，开发者同样会对测试集过拟合。
- RAG 评测需要 RetrievalFirewall，否则系统可能直接检索到 Gold 答案。
- Unlimited Benchmark Queries 会把 Hidden Test 逐渐变成 Validation。

### 第 11 阶段

- HigherOverallScore ≠ NoRegression。总分上涨仍可能伴随关键能力退化。
- BenchmarkVersion 决定 Score Meaning，跨 Benchmark 版本不能裸比。
- PairedEvaluation 比单纯比较两个总分更能定位真实变化。
- RegressionAnalysis = StructuredDeltaAnalysis。要按能力、Slice、错误类型和严重度看变化。
- StatisticalSignificance ≠ BusinessSignificance。统计显著不等于值得发布。

### 第 12 阶段

- Benchmark ≠ DatasetOnly。评测基准是数据、协议、指标和治理的组合。
- ExpertOpinion ≠ GroundTruth。Gold 的权威来自受控流程，不来自单一专家身份。
- CorrectAnswer ≠ CompleteEvaluation。结果、过程、证据和错误严重度都需要评。
- Accuracy ≠ RiskQuality。分类指标必须和真实业务错误成本绑定。
- FluentAnswer ≠ CorrectAnswer。生成质量必须拆事实、证据、引用和拒答。

## 第10课：推理部署、性能优化与 MLOps


### 第 1 阶段

- Latency ≠ Throughput。一个请求快和整个服务处理得多，是两个不同目标。
- Prefill ≠ Decode。输入处理和逐 Token 生成是两个不同性能阶段，瓶颈也可能不同。
- tokens/s 必须带 Scope。单请求、整机、输入、输出、单卡、多卡不能混为一谈。
- FastStart ≠ FastFinish。TTFT、TPOT / ITL、E2E Latency 必须分开看。
- Requests/s ≠ Tokens/s。吞吐指标必须匹配真实 Workload Shape。
- AverageLatency ≠ TailLatency。生产体验往往由 P95 / P99 决定，而不是平均值。
- FastKernel ≠ FastService。Queue Time 可以让一个很快的模型服务变得很慢。

### 第 2 阶段

- Quantization ≠ FreeCompression。低 bit 是数值近似，不是无损压缩。
- DataTypeChoice = Memory + Numerical + Kernel Decision。
- StoragePrecision ≠ ComputePrecision。
- WeightQuantization ≠ ActivationQuantization。
- QuantizedModel 是独立 Serving Version。
- SmallerModel ≠ FasterModel。性能收益取决于真实 Kernel。
- WeightMemorySaving ≠ TotalVRAMSaving。

### 第 3 阶段

- ModelFitsInGPU ≠ ServingFitsInGPU。
- KVCache = MemoryForComputeTradeoff。
- ParameterCount ≠ ServingMemoryProfile。
- MaxContext ≠ BestServingContext。
- PrefixCache 主要节省重复 Prefill，必须看 Hit Rate。

### 第 4 阶段

- ContiguousKVAllocation ≠ EfficientDynamicServing。
- LogicalContinuity ≠ PhysicalContinuity。
- Allocation Granularity 越细通常越省预留浪费，但管理开销更高。
- Model ≠ Engine。
- PagedKV + PrefixCache 可以联合优化，但收益取决于真实 Workload。

### 第 5 阶段

- MaxBatch ≠ BestBatch。
- BatchSize ≠ TokenLoad。
- Continuous Batching 解决请求生命周期不同步。
- Prefill 与 Decode 会争 GPU，长 Prefill 会伤流式体验。
- HigherBatch 用 Queue / Tail Latency 换 Throughput。
- 100% Accept ≠ ReliableService，过载时需要准入控制。
- 生产配置应该找 Knee Point，不是绝对最大吞吐。

### 第 6 阶段

- MoreGPUs ≠ LinearSpeedup。
- ScaleUp ≠ ScaleOut。模型分片和多副本服务是两种不同扩展。
- Tensor Parallel 用高频通信换取单层并行。
- Pipeline Parallel 的关键是 Stage Balance，而不是层数平均。
- 单副本放不下才优先考虑 Sharding；放得下但吞吐不够优先考虑 Replica。

### 第 7 阶段

- Deployment ≠ ModelLoading。
- ProductionAI = ModelSystem + DistributedSystem。
- Traceability 从统一 Request ID 开始。
- AgentControlPlane ≠ ModelExecutionPlane。
- Decision ≠ Authorization。

### 第 8 阶段

- Monitoring ≠ GPUUtilizationOnly。
- Observability = Metrics + Logs + Traces + Quality + Cost。
- HealthyGPU ≠ HealthyAI。
- Metrics 适合聚合，Logs/Traces 适合高基数细节。
- 没有 Trace Span 只能知道慢，不能知道哪里慢。

### 第 9 阶段

- NewVersionReady ≠ 100% Traffic Ready。
- ProductionVersion = ArtifactBundle。
- Canary = LimitBlastRadius。
- Shadow 用真实流量观察，但必须阻断真实副作用。
- A/B 测真实用户因果效果，Shadow 更适合先测技术风险。

### 第 10 阶段

- GoodModel ≠ GoodProductionSystem。
- Latency ≠ Throughput。
- Quantization ≠ FreeCompression。
- ModelFitsInGPU ≠ ServingFitsInGPU。
- EfficientMemory ≠ EfficientScheduling。

## 第11课：ProcurementLM V1.0 政府采购合规智能体全流程实战


### 第 4 阶段

- 22项 ≠ 22个关键词。附件 9 的 22 项是 7 类问题下的 22 种具体表现形式。
- Rule ≠ PromptInstruction。每个 Dxx 必须是可版本化、可执行、可测试、可审计的 Rule Object。
- InspectionRule ≠ LegalProvision。专项检查规则与法律政策依据必须分层，但保持可追踪。
- Trigger → Candidate，不是 Trigger → Violation。触发器负责召回候选，不负责最终宣判。
- All22Rules ≠ SameInferenceMethod。有的规则偏确定性、有的依赖例外、有的依赖政策状态、有的需要强语义与项目必要性判断。

### 第 9 阶段

- ProcurementOrganization ≠ ProcurementMethod ≠ EvaluationMethod。集中 / 分散采购、采购方式、评审方法是三套不同维度。
- PublicTenderThreshold ≠ OneNationalConstant。公开招标数额标准必须按预算级次、地区、采购对象和时点解析。
- ReasonablePackageDesign ≠ TenderEvasion。合理拆包和化整为零规避公开招标必须区分。
- ObservedOneSupplier ≠ OnlyOneSupplierExists。只有一家来投不等于市场唯一供应商。
- FailedTender + OneSupplier ≠ AutomaticSingleSource。招标失败不能自动转单一来源。
