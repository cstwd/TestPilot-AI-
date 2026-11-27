# PHASE-03 已复核的工程缺陷

| 涉及模块 | 复现和修复 | 回归证据 |
| --- | --- | --- |
| F08 / F09 | 含 doctest 指令的示例未在两个模块得到一致处理，增加有单独开关的生成策略 | [跨模块复验](../../reports/phase03/cross-module-review.txt) |
| 任务历史 | 最终报告可能引用其他任务的执行；归档时验证归属和记录类型 | [事务测试](../../tests/test_engine_history.py) |
| F11 | 有前置状态调用的测试断言可能被归到业务源码；定位证据不足时保留未定 | [状态计数器实测](../../reports/phase03/F11-review.txt) |
| F12 | F11 调用签名变化，首次联调发生 TypeError；已修正接口调用 | [初次失败](../../reports/phase03/F12-first.txt) · [成功复验](../../reports/phase03/F12-review.txt) |
| F12 | 未定义的期望值辅助函数不能凭名称替换成被测函数；只在有明确契约时修正 | [复核](../../reports/phase03/REVIEW.md) · [测试](../../tests/test_f12.py) |

预置样例暴露的功能缺陷与生成测试自身的错误分别记在[业务端到端报告](../../reports/phase03/E2E.md)。项目负责人为陈帅廷，工程操作和复核由 Codex 执行。
