# 英文工程术语 → 中文释义总表（V2）

> 保留英文工程标识，中文解释说明其在机器学习 / 大模型 / 政府采购 AI 中的实际含义。

| 英文术语 | 中文释义 |
|---|---|
| `Accuracy` | 准确率：全部样本中判断正确的比例 |
| `Act` | Act/行动：调用工具、写状态或请求人工 |
| `Activation Function` | 激活函数：给网络引入非线性表达能力 |
| `Adapter` | 适配器：附加在基座模型上的轻量可训练参数模块 |
| `Adjudication` | 专家裁决：对分歧样本形成最终 Gold 结论 |
| `Agent` | Agent/智能体：基于状态、工具和策略循环执行多步任务的系统 |
| `Alpha` | LoRA Alpha：控制低秩更新缩放幅度 |
| `ANN` | ANN/近似最近邻：在大规模向量中快速寻找相似项 |
| `Annotation Guideline` | 标注规范：统一专家如何理解字段、边界和例外 |
| `Attention` | 注意力：根据内容相关性动态聚合信息 |
| `Backpropagation` | 反向传播：把最终损失沿计算图反向分配到参数 |
| `Batch` | 批次：一次参与计算的一组样本 |
| `Benchmark` | Benchmark/基准评测：冻结数据、协议、指标和治理后公平比较版本 |
| `Benchmark Contamination` | 基准污染：Benchmark 内容进入训练/开发导致评测失真 |
| `BF16` | BF16：保留较大指数范围的 16 位浮点，常用于大模型 |
| `Block` | 版面块：文档解析后保留布局和位置的基本块 |
| `BM25` | BM25：基于词频和逆文档频率的经典词法检索算法 |
| `Calibration` | 校准：使模型置信度更接近实际正确率 |
| `Canary` | 灰度发布：让有限真实流量先使用新版本 |
| `Capability Boundary` | 能力边界：明确模型/工具允许做什么、不允许做什么 |
| `Catastrophic Forgetting` | 灾难性遗忘：领域训练后通用能力明显退化 |
| `Causal LM` | 因果语言模型：只能利用前文 Token 预测后续 Token |
| `Causal Mask` | 因果掩码：阻止当前位置看到未来 Token |
| `Chat Template` | 对话模板：把角色消息转换成模型训练/推理序列 |
| `Checkpoint` | 检查点：保存模型和训练状态以便恢复/发布 |
| `Chunking` | 分块：把长文档切成适合检索和上下文组装的片段 |
| `Citation` | 引用：把生成结论和具体来源建立可追踪链接 |
| `Clause Segmentation` | 条款切分：把连续文档恢复成可审查业务条款 |
| `Confidence Interval` | 置信区间：表示有限样本指标的不确定范围 |
| `Context Assembly` | 上下文组装：按顺序、预算和去重策略组织证据 |
| `Continued Pretraining` | 继续预训练：让基座模型适应特定领域语言和知识分布 |
| `Continuous Batching` | 连续批处理：动态把不同时间到达的请求加入 GPU 批次 |
| `Cosine Similarity` | 余弦相似度：比较两个向量方向相似程度 |
| `Counterfactual` | 反事实：改变关键事实，检查正确结论是否应随之变化 |
| `CPT` | CPT/继续预训练：在领域语料上继续执行预训练目标 |
| `CPU` | CPU：负责通用控制、数据准备和部分算子 |
| `CUDA` | CUDA：NVIDIA GPU 通用并行计算平台与软件生态 |
| `CUDA Toolkit` | CUDA 工具包：开发、编译和运行 CUDA 程序的工具与库 |
| `Curriculum` | 课程式训练：按难度、类型或阶段安排训练数据顺序 |
| `Data Leakage` | 数据泄漏：训练阶段获得了本不应看到的测试或未来信息 |
| `Data Mixture` | 数据混合：控制通用语料和领域语料等来源比例 |
| `Data Unit` | 数据单元：从原始文件切出的可追踪业务片段 |
| `Dataset` | 数据集：按统一 Schema、版本和质量标准组织的样本集合 |
| `Decide` | Decide/决策：根据目标和状态选择下一步动作 |
| `Deduplication` | 去重：识别并处理完全重复或近似重复的数据 |
| `device_map` | 设备映射：指定模型模块放在哪个 GPU/CPU |
| `Domain Corpus` | 领域语料：用于继续预训练的政府采购专业文本集合 |
| `Drift` | 漂移：数据、业务、政策或模型行为分布发生变化 |
| `Driver` | 驱动：操作系统与 GPU 硬件之间的底层接口 |
| `dtype` | 数据类型：FP32/FP16/BF16 等，影响显存、速度和数值稳定性 |
| `Embedding` | 嵌入：把离散 Token 映射到连续高维向量 |
| `Epoch` | 训练轮次：训练数据完整遍历一次 |
| `Evidence` | 证据：可回到采购文件或法规来源的支撑片段 |
| `External Knowledge` | 外部知识：位于模型参数之外、可检索可更新的资料 |
| `Forward Propagation` | 前向传播：输入逐层计算直到得到预测 |
| `FP16` | FP16：16 位浮点，节省显存但数值范围较窄 |
| `Frozen Data` | 冻结数据：评测周期内不随意改动的 Benchmark 样本 |
| `Generalization` | 泛化：对未见项目、时间、地区和表达的有效能力 |
| `Gold Benchmark` | Gold Benchmark：由高质量证据、专家标注和治理形成的正式评测集 |
| `Governance` | 治理：控制版本、权限、污染、审批和发布决策 |
| `GPU` | GPU：擅长大规模并行矩阵计算的大模型核心硬件 |
| `Gradient` | 梯度：损失对参数变化方向和敏感度的局部信息 |
| `Gradient Accumulation` | 梯度累积：多次小 Batch 累积梯度后再更新参数 |
| `Hard Negative` | 高难负例：表面像风险但正确结论不应判风险 |
| `Hard Positive` | 高难正例：没有明显关键词但确实需要识别的风险 |
| `Hidden Layer` | 隐藏层：逐层形成内部表示的中间网络层 |
| `Hugging Face` | Hugging Face：开源模型、数据与 Transformer 工具生态 |
| `Human-in-the-loop` | 人在回路：高风险或不确定任务引入人工复核 |
| `Hybrid Retrieval` | 混合检索：结合词法/稀疏检索与向量语义检索 |
| `Idempotency` | 幂等：重复执行不会产生不可控重复副作用 |
| `Inference` | 推理：系统接收请求并产生结果的在线计算过程 |
| `Initialization` | 初始化：训练开始前设置参数初值 |
| `Input` | 输入：模型在当前任务中允许看到的条件信息 |
| `JSON Schema` | JSON Schema：约束工具输入输出字段和类型 |
| `Key` | Key/K：其他 Token 表示“我可被怎样匹配”的向量 |
| `KV Cache` | KV 缓存：生成时缓存历史 Key/Value 以减少重复计算 |
| `Label` | 标签：专家或规则给出的监督目标/Gold 结论 |
| `Label Schema` | 标签结构：定义风险状态、类型、等级、证据等标注字段 |
| `Latency` | 延迟：单个请求从进入到完成的时间 |
| `LayerNorm` | LayerNorm：按特征维度规范化中间表示 |
| `Layout` | 版面结构：文字块、表格、列、坐标和阅读顺序信息 |
| `Learning Rate` | 学习率：控制每次参数更新步幅 |
| `LoRA` | LoRA：冻结大部分基座参数，只训练低秩增量矩阵 |
| `Loss` | 损失函数：把预测错误压缩成可优化的数值信号 |
| `Loss Mask` | 损失掩码：指定哪些 Token 参与训练 Loss |
| `max_new_tokens` | 最大新 Token 数：限制模型输出长度 |
| `Memory` | 任务记忆：保存跨步骤需要复用的结构化信息 |
| `Metadata` | 元数据：项目、来源、时间、地区、版本等辅助信息 |
| `MLOps` | MLOps：模型、数据、版本、部署、监控和回滚的工程体系 |
| `MLP` | MLP/前馈网络：对每个位置表示做非线性变换 |
| `Monitoring` | 监控：持续观察系统、模型和业务指标是否健康 |
| `Multi-Head Attention` | 多头注意力：并行从不同子空间建模关系 |
| `Near-duplicate` | 近重复：表面略有差异但实质高度相似的数据 |
| `Neuron` | 神经元：加权、偏置和非线性变换的最小计算单元 |
| `Next Token Prediction` | 下一 Token 预测：大语言模型预训练核心目标 |
| `NF4` | NF4：适合近似正态权重的 4 位量化格式 |
| `Normalization` | 规范化：稳定中间激活与训练过程 |
| `Observability` | 可观测性：通过指标、日志、追踪理解系统内部状态 |
| `Observe` | Observe/观察：读取当前状态和工具结果 |
| `OCR` | OCR：把扫描图像中的文字转换成机器可读文本 |
| `Offloading` | 卸载：把部分权重/计算转移到 CPU 或磁盘 |
| `OOD` | 分布外数据：明显偏离训练/验证分布的新输入 |
| `Optimizer` | 优化器：依据梯度规则更新参数 |
| `Overfitting` | 过拟合：训练集很好但新项目泛化变差 |
| `Padding` | 补齐：把不同长度序列补到统一批次长度 |
| `Parametric Memory` | 参数记忆：编码在模型权重中的知识和模式 |
| `Parser` | 解析器：把 PDF/Word/HTML 转换为结构化可处理内容 |
| `Pipeline Parallel` | 流水线并行：把不同层/阶段分配到不同 GPU |
| `Planning` | 任务规划：把目标拆成可执行、带依赖的子任务 |
| `Precision` | 精确率：系统报出的风险中真正成立的比例 |
| `Prompt` | 提示输入：给模型的任务说明与条件 |
| `Prompt Injection` | 提示注入：外部文本试图越权改变系统指令/工具行为 |
| `PyTorch` | PyTorch：张量计算、自动求导和训练/推理框架 |
| `QLoRA` | QLoRA：量化基座模型并训练 LoRA，以降低显存成本 |
| `Quantization` | 量化：用更低位宽表示权重/激活以降低显存和计算成本 |
| `Query` | Query/Q：当前 Token 表示“我要找什么”的向量 |
| `Query Rewriting` | 查询改写：把问题改成更适合检索的表达 |
| `RAG` | RAG/检索增强生成：推理时先检索外部证据再生成 |
| `Rank` | LoRA Rank：低秩增量的容量参数 |
| `Raw Document` | 原始文档：未经结构化处理的采购文件源材料 |
| `Recall` | 召回率：真实风险中被系统成功找出的比例 |
| `Recall@K` | Recall@K：相关证据是否进入前 K 条检索结果 |
| `Recovery` | 恢复：工具失败或中断后安全重试、降级和继续 |
| `Red Team` | 红队：主动构造对抗和异常场景寻找未知失败模式 |
| `Regression` | 回归测试：更新后验证旧能力和关键切片没有退化 |
| `Replay` | 回放：混入旧/通用数据以减少遗忘 |
| `Representation` | 表示：模型内部承载语义或特征的向量结构 |
| `Reranker` | 重排器：对初筛候选做更精细相关性排序 |
| `Residual Connection` | 残差连接：让信息跨层直接传递、改善深层优化 |
| `Response` | 目标响应：希望模型学习生成的答案部分 |
| `Retention` | 能力保持：领域增强时尽量保住原有通用能力 |
| `RMSNorm` | RMSNorm：基于均方根的轻量归一化 |
| `Rollback` | 回滚：出现问题时恢复上一稳定系统版本 |
| `RoPE` | RoPE：旋转位置编码，把位置信息融入注意力 |
| `Routing` | 路由：决定当前任务交给哪个工具/模块 |
| `Sample` | 样本：具有明确输入、目标和来源的一条训练/评测记录 |
| `Schema` | Schema/结构契约：规定一个数据对象有哪些字段及其含义 |
| `Self-Attention` | 自注意力：同一序列内部各位置计算相关性并聚合 |
| `Serving` | 服务化：把模型包装成可扩展、可观测、可治理的在线服务 |
| `SFT` | 监督微调：用监督样本继续更新模型参数 |
| `Shortcut Learning` | 捷径学习：利用表面相关线索而非真正任务规律 |
| `Softmax` | Softmax：把一组分数转换成归一化权重 |
| `Speculative Decoding` | 投机解码：先生成候选、再由大模型验证以加速生成 |
| `Split` | 数据切分：按项目/时间/地区划分训练、验证、测试数据 |
| `Stable Protocol` | 稳定协议：固定输入、工具、提示和输出判定方式 |
| `State` | 状态：保存任务进度、事实和待办 |
| `Step` | 训练步：通常指一次优化器更新 |
| `Structured Output` | 结构化输出：按照固定字段和枚举生成可校验结果 |
| `Synthetic Data` | 合成数据：由规则/模型生成、需质量控制的训练数据 |
| `Target Modules` | 目标模块：指定 LoRA 插入哪些线性层 |
| `Temperature` | 温度：控制采样分布平滑程度和随机性 |
| `Tensor Parallel` | 张量并行：把同一层矩阵计算拆到多张 GPU |
| `Test` | 测试集：模型选择完成后独立估计泛化能力 |
| `Threshold` | 阈值：把连续分数转成业务动作的决策门槛 |
| `Throughput` | 吞吐：单位时间内处理请求或生成 Token 的能力 |
| `Token` | Token：模型实际处理的离散文本单元 |
| `Tokenization` | Token 化：把文本转换成 Token 序列 |
| `Tokenizer` | 分词器：文本与 Token ID 之间的编码/解码组件 |
| `Tokenizer Audit` | 分词器审计：检查专业术语、数字、符号的 Token 化质量 |
| `tokens/s` | 每秒 Token 数：衡量生成速度或系统吞吐的常见指标 |
| `Tool Calling` | 工具调用：模型按受控协议选择工具并构造参数 |
| `Tool Registry` | 工具注册表：管理工具能力、权限和版本 |
| `top_k` | Top-k：只在概率最高的 k 个 Token 中采样 |
| `top_p` | Top-p：在累计概率达到 p 的候选 Token 中采样 |
| `TPOT` | 每输出 Token 时间：首 Token 后平均生成一个 Token 的耗时 |
| `Transformer` | Transformer：以注意力和前馈网络为核心的序列架构 |
| `Transformers` | Transformers：Hugging Face 的模型加载与推理库 |
| `Truncation` | 截断：超过最大长度时裁掉部分 Token |
| `TTFT` | 首 Token 时间：用户等待第一个输出 Token 的时间 |
| `Underfitting` | 欠拟合：模型连训练数据主要规律都没有学好 |
| `Validation` | 验证集：开发阶段用于选模型、调参数和早停 |
| `Value` | Value/V：被注意力权重实际汇聚的内容向量 |
| `Vector Database` | 向量数据库：存储向量并支持相似度检索 |
| `VRAM` | 显存：GPU 上存放权重、激活和 KV Cache 等的高速内存 |
