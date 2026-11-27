# PyCharm 与默认浏览器现场记录

2026-11-27，北京时间，实际操作 Codex。此记录摘取与验收有关的可见控件、响应和控制台输出；以下为操作摘要。项目窗口为 PyCharm 2026.1.2 的 TestPilot AI，项目解释器显示 Python 3.13 (TestPilot AI)。

| 操作 | 现场读数 |
| --- | --- |
| 在工具栏点击根入口的绿色 Run | 运行面板显示 Uvicorn 进程 39968 和 `Application startup complete.` |
| 等待系统默认浏览器 | Edge 出现项目页。地址栏值为 `127.0.0.1:8000`，文档地址为 `http://127.0.0.1:8000/`，标题为 `Dashboard · TestPilot AI`。未手动导航到该地址。 |
| 读取页面并点击“运行自检” | 页面标题“启动仪表盘”，后端和数据库两处“已连接”。点击按钮后实际观察到“运行中”随后变为“通过”。 |
| 核对 Run 控制台 | `GET /`、`GET /static/dashboard.css`、`GET /static/dashboard.js`、`GET /api/health`、`POST /api/self-test` 均为 HTTP 200。首轮还出现浏览器对 favicon 的 404，修复后已在 [Edge 测试](../tests/test_dashboard.py) 中回归。 |
| 点击红色 Stop | 控制台依次显示 `Shutting down`、`Application shutdown complete.`、`Finished server process [39968]`，进程退出代码为 0。 |
| 从根入口再次启动并调试 | IDE 可复用 8000。在最终源码编辑器边栏设置行断点并点击 Debug；暂停帧显示 `MainThread`、`<module>, main.py:15`。清除本次临时断点后按 F9 继续。[IDE 暂停帧](pycharm-breakpoint.jpg) |

F9 恢复后，控制台再次记录页面和健康接口 HTTP 200；最后一次 Stop 显示进程 43756 完成关闭，退出码 0。PyCharm 的运行配置列表已识别项目随附的 `TestPilot AI` 共享配置。

另以项目解释器运行 PyCharm 附带的调试后端，对应用工厂设置断点并验证恢复后的 HTTP 响应。[调试复验](pycharm-debug.md)
