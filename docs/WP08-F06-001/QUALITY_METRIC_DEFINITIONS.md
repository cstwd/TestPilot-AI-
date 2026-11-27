# F06 质量指标定义

WP08-F06-001。页面百分比以 `GET /api/runs/{run}/report` 返回的值为准。可在“指标口径”中查看本次报告附带的说明。断言失败、执行错误、超时或全部跳过时，上方判断说明也来自相同快照。[业务定义](../../backend/quality.py#L11) · [页面显示](../../frontend/static/report-metrics.js)

| 项目 | 源字段及分母 | 边界 |
| --- | --- | --- |
| 测试通过率 | `quality.pass_rate_pct`。公式为 Passed ÷（Passed + Failed + Error）× 100，后端保留两位小数。分子显示实际 Passed 数。 | 分母 0 对应 `null`，显示“无可计算的用例”。分母为正且分子 0 显示 0%。 |
| 总用例数 | `quality.total`，Passed + Failed + Error + Skipped。 | 收录数为 0 时显示 0。 |
| 用例分布 | `quality.passed`、`failed`、`errors`、`skipped`。四种结果以收录总数作分母。 | 每项同时显示名称与 (n/总数)。跳过独立保留，分布条在总数为 0 时折去。 |
| 行覆盖率 | `quality.coverage_pct`、`covered_lines`、`total_lines`。按被测单文件实际覆盖行 ÷ 可执行行。 | `null` 显示“未采集”。已有的 0/0 行继续显示；无行数时说明字段未记录。0/正数对应真实 0%。 |
| 关联缺陷 | `bugs[]` 的真实记录，包含本次原始失败或该次回归关系。给定状态的分布使用关联缺陷数作分母。 | 比较与导出的证据属于当前报告快照。缺陷状态取报告读取时的记录。0 条显示“无关联缺陷”。 |
| 回归证据 | 每条关联缺陷的 `regressions[]`。包含 `run_id`、`file_id`、`revision` 和服务端回归判定。 | 判定状态明确标注，F04 证据链接可打开独立执行结果。 |

执行覆盖范围评估使用客体的 `coverage.analysis2`，运行保存覆盖行、可执行行和比例。质量页引用这些数据，不依据测试结果推算覆盖率。[覆盖来源](../../backend/guest_pytest.py#L91) · [记录口径](../../backend/runner.py#L67)

多次运行比较只列同项目、同名文件、同套件的实际报告。表格两列保留各自的测试总量、通过分母与覆盖分母。对照报告单独读取，HTML 与 JSON 下载继续使用原报告快照。[跨运行校验](../../frontend/static/reports.js)
