# 第一课～第十一课 V2 完整体系阅读指南

## 一、V2 为什么不再按“几百个点”平铺记忆？

V2 统一成四层阅读结构：

```text
Layer 1：Core Mental Models    # 中文：每阶段先抓 5～8 个核心判断框架
↓
Layer 2：Key Mechanism / Formula / Workflow    # 中文：理解公式、数据结构和系统流程
↓
Layer 3：Government Procurement Examples / Counterexamples    # 中文：用政府采购案例和反例理解边界
↓
Layer 4：Detailed Engineering Expansion    # 中文：大量编号细节作为查阅层，不要求一次背完
```

\[
\boxed{
DetailedPoints
\neq
ThingsToMemorize
}
\]

**中文业务释义：** 一个阶段出现很多展开点，不等于这些点都应该以同等优先级记忆；真正需要长期保留的是核心心智模型、关键机制和判断边界。

## 二、11 课完整演化体系

```text
第1课：机器学习的学习本质、泛化、评测与不确定性
↓
第2课：神经网络 → Attention → Transformer → LLM
↓
第3课：GPU / CUDA / PyTorch / 开源大模型运行环境
↓
第4课：政府采购文档 → Schema → Clause → Label → Dataset
↓
第5课：SFT + LoRA / QLoRA → ProcurementLM_V0.1
↓
第6课：RAG + Embedding + Retrieval → ProcurementRAG_V0.1
↓
第7课：Agent + Tool Calling + State → ProcurementAgent_V0.1
↓
第8课：CPT + 高级领域适配 → ProcurementLM_V0.2
↓
第9课：Gold Benchmark + Reliability → ProcurementBench_V1
↓
第10课：Inference + Serving + MLOps → ProcurementAI
↓
第11课：规则、法规、数据、模型、Agent、Benchmark、生产治理
↓
ProcurementLM_V1.0
```

## 三、跨课程总心智模型

\[
\boxed{
AIProject
\neq
ModelProject
}
\]

**中文业务释义：** 一个政府采购 AI 项目不是“选个模型再调参”，而是数据、规则、知识、工具、评测和生产治理共同构成的系统工程。

\[
\boxed{
ReliableAI
=
CorrectWhenKnown
+
AbstainWhenUnknown
+
EscalateWhenHighRisk
+
TraceEverything
+
RollbackWhenWrong
}
\]

**中文业务释义：** 可靠 AI = 知道时正确判断 + 不知道时拒绝武断 + 高风险时升级人工 + 全过程可追踪 + 出错时能够回滚。
