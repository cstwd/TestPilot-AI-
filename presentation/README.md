# TestPilot AI 课程展示

[可编辑 PPTX](TestPilot_AI_课程汇报.pptx) · [PDF 预览](TestPilot_AI_课程汇报.pdf) · [备用演示 MP4](TestPilot_AI_备用演示.mp4) · [变异检出率图](../reports/phase05/mutation-score.png)

现场演示用 PyCharm Run 启动根入口，依次导入 `eval/phase02/buggy/magnitude.py` 和 `eval/phase02/fixed/magnitude.py`。在缺陷版分析函数并生成套件，从失败节点登记缺陷，然后在修复版运行原套件，查看 F06 报告并导出。F13 点击智能引擎任务的“评估变异测试与补测”。备用视频将同一流程的实测页面配字幕串联，最后回放真实本机模型健康响应。

| 步骤 | 截图 |
|---|---|
| 首页 | [启动仪表盘](screenshots/00-dashboard.png) |
| F01 / F02 | [文件版本](screenshots/01-project.png) · [AST](screenshots/02-ast.png) |
| F03 / F04 | [生成套件](screenshots/03-suite.png) · [实际失败](screenshots/04-execution.png) |
| F05 / F06 | [缺陷回归](screenshots/05-regression.png) · [质量报告](screenshots/06-quality.png) |
| F13 与模型 | [变异执行](screenshots/07-mutation.png) · [27B 健康响应](screenshots/08-model.png) |

复建截图执行 `python -m pytest -q -s presentation/capture_demo.py`。PPT 源码为 [build_deck.mjs](build_deck.mjs)。设 `TESTPILOT_ARTIFACT_RUNTIME` 为含 `@oai/artifact-tool` 的 Codex 运行时 dependencies 目录，设 `TESTPILOT_PRESENTATIONS_SKILL` 为 Presentations 技能目录，用 Node 执行。列图数据取自冻结评测摘要并嵌入可编辑工作簿。MP4 复建用带 Pillow 的 Python 与 FFmpeg 执行 [build_demo_video.py](build_demo_video.py)。

[当前 Edge 实测](../reports/course-final/demo.txt) · [导出 JSON](../reports/course-final/demo-quality.json) · [变异 JSON](../reports/course-final/demo-mutation.json) · [PHASE-06 本机接口返回](../reports/course-final/model-health.json) · [PPTX 结构](../reports/course-final/pptx-integrity.json) · [视频信息](../reports/course-final/video-probe.json)
