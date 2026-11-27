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

## 十二项核心图表

| 任务书素材 | 可单独打开的图 |
|---|---|
| 1 系统架构、2 功能模块 | [技术分层](architecture/04-system.svg) · [七项功能](architecture/03-feature-map.svg) |
| 3 智能测试流程、4 AST 与图谱 | [业务交接与证据](workflow/02-manual-and-workbench.svg) · [源码与图谱关系](architecture/05-ast-relations.svg) |
| 5 AI 生成、6 执行与结果分析 | [生成和静态检查](workflow/06-ai-generation.svg) · [失败记录的形成](workflow/07-execution-flow.svg) |
| 7 修复前后、8 变异原理 | [真实 Qwen 修复与原套件回归](workflow/08-regression.svg) · [原版与变异如何比较](workflow/09-mutation-principle.svg) |
| 9 自动化 CI、10 五岗协作 | [托管 CI](workflow/10-ci.svg) · [WP01–WP05](architecture/14-team.svg) |
| 11 成果统计、12 完整闭环 | [按同一清单比较四组检出](charts/10-offline.svg) · [从导入到质量报告](workflow/12-closed-loop.svg) |

统计输入为归档 JSON 和 CSV。[幻灯片与截图排版源码](../source/build_deck.py)与[独立 SVG 绘图源码](../source/build_figures.py)随包保留。P08 的原始证据包括[模型修复预览](../04_TESTING_EVIDENCE/F05_AI_REPAIR/reports/TP-F05-AI-REPAIR-001/preview.png)与[原套件回归截图](../04_TESTING_EVIDENCE/F05_AI_REPAIR/reports/TP-F05-AI-REPAIR-001/regression.png)。
