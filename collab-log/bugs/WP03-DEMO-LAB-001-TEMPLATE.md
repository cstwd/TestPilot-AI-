# WP03-DEMO-LAB-001 · 模板测试取值违反函数前置条件

2026-11-27 · 操作者 Codex · 归属 WP03，复核由独立 reviewer 执行，成员签收待登记。

在隔离的 `main.py` 服务中为 GOOD 模块创建模板引擎任务，并进入 F13。原版源码在独立合同中通过。模板引擎将零和扁平列表作为边界输入后，以下任务的原版基线出现预期输入异常。

| 模块目标 | 输入限制 | 观测 |
| --- | --- | --- |
| `percentage_calculator.percent_of` | 分母非零 | `ZeroDivisionError` |
| `significant_digits.round_significant` | 有效位数为正 | `ValueError` |
| `shopping_cart.cart_total` | 每行包含价格和数量 | `TypeError` |
| `retry_policy.retry_delay` | 重试从 1 开始 | `ValueError` |

F13 正确将相关组归为 `baseline_failed` 并保留无得分的原版运行。触发处和执行记录可在 [初选回执](../../demo/TestPilot-Demo-Lab/reports/product_mutation_initial.json) 中复核。实验室将最终清单调整为有实测绿色基线的目标。
