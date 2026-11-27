
# F13 变异测试验收

15 个 GOOD 函数通过原版 Pytest 基线后实际执行 F13。使用现有智能引擎的 `template` 生成模式，最大修复次数为 0，F13 的模型补测关闭。冻结清单的源码摘要、会话 ID、基线、每个变异的位置与观测结果见 [正式回执](product_mutation.json)。

| 模块与目标 | 总数 | 杀死 | 存活 | 执行错误 | 超时 | 等价候选 | 得分 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| calculator.add | 2 | 2 | 0 | 0 | 0 | 0 | 100% |
| prime_checker.is_prime | 7 | 4 | 3 | 0 | 0 | 0 | 57.14% |
| percentage_calculator.basis_points | 2 | 2 | 0 | 0 | 0 | 0 | 100% |
| geometry_calculator.area | 5 | 2 | 1 | 2 | 0 | 0 | 40% |
| role_manager.active_labels | 1 | 1 | 0 | 0 | 0 | 0 | 100% |
| account_lock.remaining_wait | 2 | 2 | 0 | 0 | 0 | 0 | 100% |
| record_projection.complete | 1 | 1 | 0 | 0 | 0 | 0 | 100% |
| inventory_manager.available | 2 | 2 | 0 | 0 | 0 | 0 | 100% |
| shipping_calculator.shipping_fee | 5 | 4 | 1 | 0 | 0 | 0 | 80% |
| stack.push | 2 | 1 | 0 | 1 | 0 | 0 | 50% |
| interval_overlap.overlaps | 2 | 1 | 1 | 0 | 0 | 0 | 50% |
| date_calculator.leap | 9 | 5 | 4 | 0 | 0 | 0 | 55.56% |
| booking_validator.valid_slot | 4 | 3 | 1 | 0 | 0 | 0 | 75% |
| timezone_converter.local_minute | 3 | 3 | 0 | 0 | 0 | 0 | 100% |
| text_analyzer.word_count | 1 | 1 | 0 | 0 | 0 | 0 | 100% |
| **汇总** | **48** | **34** | **11** | **3** | **0** | **0** | **70.83%** |

取消和未运行均为 0。按现有 F13 口径，分母为清单中的全部变异，分子为有效测试断言杀死的变异。三项执行错误保留在分母。初选中的四项模板红基线保存在 [初选回执](product_mutation_initial.json)，随后的绿色基线和冻结版本更新见 [复测回执](product_mutation_recheck.json)。

```powershell
.venv/Scripts/python.exe -X utf8 demo/TestPilot-Demo-Lab/scripts/product_acceptance.py mutation
```

发布快照由 `scripts/select_mutation_receipts.py` 按最终源码摘要和函数名汇合实测回执，并核查绿色基线、观测集合和计分。报告没有应用模型补测。
