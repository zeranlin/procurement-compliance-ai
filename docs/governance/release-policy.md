# 发布策略入口

`ReleaseReady` 必须满足：

```text
ModelGate ∧ RuleGate ∧ LegalGate ∧ AgentGate ∧ RedTeamGate
```

总体准确率不能掩盖关键规则漏检、证据错误、法源不支持、边界不一致或人工门绕过。`PASS_DEMO` 只表示最小闭环达到 Demo 门槛，不表示生产就绪。
