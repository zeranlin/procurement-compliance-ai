# 模块契约入口

模块契约采用：

```text
Contract = Schema + BusinessExample + MentalModel
         + Invariant + FailureCase + TestCase
```

每个模块必须明确：职责、输入、输出、非职责、错误/降级、Contract Test、Benchmark Slice 和验收标准。共享对象以 `contracts/` 为唯一事实源，模块内部不得复制并维护冲突版本。
