
# AI 盲测验收

WP03-DEMO-LAB-001 · 2026-11-27 · 操作者 Codex

**10 个样本完成 F01 导入和 F02 静态分析，0 个走完真实 AI F03/F04。** 在固定模型的三次启动中，守护都完成了权重校验和 Vulkan 识别。模型加载过程中，实测物理内存余量分别降至 1.87、1.66 和 1.74 GiB，触发项目既有的 2 GiB 安全下限。模型健康接口返回 HTTP 503，10 个 AI 套件请求各返回 HTTP 422，产品保留了原因。第三次在实验室数据验证、F13 和模板回归完成后单独执行。记录见 [资源观测](reports/model_resource_observations.json)、[首轮](reports/product_blind_resource_guard.json)、[复测](reports/product_blind_resource_retry.json) 和 [串行复测](reports/product_blind.json)。

| 样本 | 领域 | 类型 | F02 目标 | F01/F02 | AI F03 | F04 |
| --- | --- | --- | --- | --- | --- | --- |
| binary_search | 算法 | BUGGY | locate | 完成 | 资源保护 | 无运行 |
| booking_timezones | 日期 | CHALLENGE | utc_window | 完成 | 资源保护 | 无运行 |
| calculator | 数学 | GOOD | add | 完成 | 资源保护 | 无运行 |
| csv_processor | 数据 | GOOD | rows | 完成 | 资源保护 | 无运行 |
| log_parser | 数据 | BUGGY | message | 完成 | 资源保护 | 无运行 |
| scientific_calculator | 数学 | BUGGY | slope | 完成 | 资源保护 | 无运行 |
| shipping_calculator | 电商 | GOOD | shipping_fee | 完成 | 资源保护 | 无运行 |
| team_roster | 人员 | BUGGY | surname_key | 完成 | 资源保护 | 无运行 |
| user_validator | 人员 | GOOD | normalize_username | 完成 | 资源保护 | 无运行 |
| volume_discount | 电商 | BUGGY | discount | 完成 | 资源保护 | 无运行 |

盲测通过本机 `main.py` 和独立临时数据库完成。F01 只上传 `source/` 下的冻结源码，F03 显式指定 `ai`。答案与验证测试保留在独立目录，只有离线评分器读取。手工演示工作台的模板模式另有独立 F05 与 F13 证据。

## 指标与测量状态

| 指标 | 分子 / 分母 | 实测结果 |
| --- | --- | --- |
| Bug Detection Rate | 通过原版失败、修复版通过、竞争修复可唯一归因的缺陷数 / 完成有效 AI 执行的目标函数已知缺陷数 | 未测得，计划 6 项 |
| Test Pass Rate | GOOD 的实际通过节点 / GOOD 有效 AI 执行的通过与失败节点 | 未测得 |
| False Positive Rate | 至少出现一个可确认测试侧误报的 GOOD 模块 / 有效 AI 执行且离线重放一致的 GOOD 模块 | 未测得 |
| Boundary Test Coverage | 实际通过的直接字面量比较断言命中的冻结边界输入数 / 有效 AI 执行的目标函数冻结边界输入数 | 未测得，计划 9 项 |
| Regression Pass Rate | 修复后失败节点通过且状态已关闭的回归次数 / 已执行的回归次数 | 1 / 1，100%，模板流程 |
| Mutation Score | 已杀死变异 / 正式变异清单全部变异 | 34 / 48，70.83%，模板基线 |

边界指标采用保守计数，直接断言须引用实际项目目标并带独立字面预期，复杂间接调用需要单独审阅。报告 JSON 在缺少分母时使用 `null`。模型生成数量、执行完成数量、归因后检出数量和修复回归结果可分别核对。[独立指标 JSON](reports/evaluation.json) · [F05 回执](reports/product_regression.json) · [F13 验收](reports/MUTATION_EVALUATION.md)

```powershell
.venv/Scripts/python.exe -X utf8 demo/TestPilot-Demo-Lab/scripts/product_acceptance.py blind --workflow
.venv/Scripts/python.exe -X utf8 demo/TestPilot-Demo-Lab/evaluation/evaluator.py
```

盲测尚需在固定模型可通过健康检查的环境复验。现有证据覆盖真实导入、静态分析、模型拒绝路径和服务有序关闭。
