# 演示素材索引

[浏览器原始截图](screenshots/)保留归档 PNG。[课程样例源码](code_samples/)可静态阅读。[图表输入 JSON](charts/measurements.json)记录同一运行的两次 Pytest 和独立变异会话，四组冻结评测另有 [CSV](charts/frozen-evaluation.csv)。所有截图的源提交、原路径和摘要见[副本清单](../07_FINAL_REPORT/COPIED_EVIDENCE.csv)。

| 演示对象 | 实际截图 | 原始数据或图解 |
|---|---|---|
| 系统与模块 | [工作台](screenshots/01-workbench.png) | [架构图](architecture/04-system.svg) · [功能图](architecture/03-feature-map.svg) |
| telemetry 图谱 | [全图](screenshots/05-ast.png) · [源码检查](screenshots/05-ast-source.png) | [源码](code_samples/eval/ast_visual/telemetry.py) |
| 测试生成 | [模板套件](screenshots/06-template.png) | [原 AI 套件及断言](../04_TESTING_EVIDENCE/AI_EVALUATION/reports/phase06/raw/live.json) |
| 执行与回归 | [F04 独立失败页](screenshots/07-pytest.png) · [Lab 运行](screenshots/08-regression.png) | [同套件对比](workflow/08-regression.svg) |
| 变异、CI 与质量报告 | [存活位置](screenshots/09-mutant.png) · [报告中心](screenshots/12-report.png) · [F06 HTML](screenshots/12-f06.png) | [CI 流程](workflow/10-ci.svg) · [冻结检出数](charts/10-offline.svg) · [完整闭环](workflow/12-closed-loop.svg) |
| 项目成果与分工 | [历史 64 项统计](charts/15-outcomes.svg) | [五个工作包](architecture/14-team.svg) |

图片中的视口、样本和运行 ID 按各自原始证据解读。F04 独立截图与 unit_scaling 浏览器回执对应不同运行。公开合同流程与 AI 历史路径见[操作手册](../06_PRESENTATION/DEMO_RUNBOOK.md)。
