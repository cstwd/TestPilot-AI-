# 现场演示操作手册

幻灯片取证基线为历史快照 `cf448f3`。现场运行使用当前仓库根目录。P08 的 AI 修复实现始于 `b40b54e`，演示所用数据库为专项验收副本。组长按操作手册协调成员联排。准备 Windows 11、PyCharm Python 3.13 与 Edge，Run 根目录 `main.py`，确认首页可见且 `/api/health` 返回 200。可为演示指定独立 `TESTPILOT_DATA_DIR`。提前打开 [telemetry.py](../eval/ast_visual/telemetry.py)、原版和修复版 unit_scaling、[归档证据](../docs/COURSE_REQUIREMENTS_MAPPING.md)。

| 段落 | 文件与页面 | 点击和预期 |
|---|---|---|
| P05 F01/F02 | eval/ast_visual/telemetry.py，项目中心和代码分析页 | 创建演示项目，导入该源码，进入分析。选 SignalWindow 或 Sample.normalized，查看父子节点、行号和源码。选择 mean_value 可送目标到生成 Studio。 |
| P06 F03 | 测试生成 Studio；历史 AI 接口归档 | 选择目标函数后用已有模板演示页查看套件来源、断言和静态检查。用 P06 历史 API 回执讲真实 AI 路径。只有健康检查通过且预计演示时间允许时才从 Demo Lab 显式选本机 AI。 |
| P07、P12 课堂模板 F04/F05 | Demo Lab，source/buggy/unit_scaling.py 和 reference/corrected/unit_scaling.py | 首页点「打开 Demo Lab」，搜 unit_scaling，查看「源码」与「公开合同」。选「公开合同 / 本地模板」，勾「通过后运行 F13」，点「运行演示」。展开 Pytest，原版断言 1 == 1.25，修复版同套件通过，缺陷 resolved。以现场界面的新 ID 为准。 |
| P08 真正的 AI 修复 | 缺陷管理页；预先打开[原始失败](../reports/TP-F05-AI-REPAIR-001/original.json)、[候选差异](../reports/TP-F05-AI-REPAIR-001/preview.png)、[回归](../reports/TP-F05-AI-REPAIR-001/regression.png) | 选择单位换算缺陷 →「AI 分析并生成修复」→ 查差异 →「应用 AI 修复」→ 选原套件并「确认运行」。核对失败数、跳过数和缺陷状态。历史专项使用文件 #16/#17、套件 #8、运行 #12/#14；新建会话按实际编号。 |
| 选样验证 | GOOD calculator；BUGGY unit_scaling；CHALLENGE booking_timezones | 在 Demo Lab 用「类型」筛选，确认目录类别并点样本预览。历史实跑分别支持原版通过、原版失败后回归、复杂组合逻辑修复。上台只执行优先样本以留足时间。 |
| P09 F13 | Demo Lab 中的 geometry_calculator.area | 勾 F13 后运行，展开「定位存活变异」看第 8 行。历史记录 5 项，2 杀死、1 存活、2 执行错误。时间不足时放 [真实存活截图](../reports/phase07/05-f13-surviving-mutant.png)；unit_scaling 归档另有 2/2。 |
| P12 F06 | Demo Lab「运行历史」／「报告中心」及 F06 质量工作台 | 从完成报告点「下载完整 JSON」，按当前 run ID 验证；重新进入报告验证历史可读，可点 F06 原始快照。普通质量工作台另支持 JSON 与 HTML。 |

观测依据 [浏览器回执](../reports/phase07/edge-run.json)、[七样本](../reports/phase07/end-to-end.json)、[本机 AI 失败](../reports/phase07/ai-live.json)。浏览器、服务或现场模型不可用时，按照汇报大纲顺序指读真实截图和保存结果。[旧版全流程 59 秒备用录屏](TestPilot_AI_备用演示.mp4)使用 magnitude 样例，[AST 动画备用录屏](../reports/WP03-AST-VISUAL-REFINE-001/video/analysis-session.mp4)使用 telemetry.py。

补充案例　[独立 F05 真实 Qwen 修复](../reports/TP-F05-AI-REPAIR-001/TP_F05_AI_REPAIR_001_ACCEPTANCE.md)。选择缺陷，点击「AI 分析并生成修复」，审阅并应用候选，再运行原套件 #8。归档回归 #14 为 3 通过、1 跳过，和 Demo Lab 模板套件 #1 分开讲解。
