# PHASE-02 · PyCharm 启动与调试回归

2026-11-27，Windows 11，PyCharm 2026.1.2，实际操作 Codex。开始时默认端口由已有会话占用，准备期间该会话正常退出。正式 Run 直接使用默认 8000；调试协议单独使用临时端口和临时数据目录。

| 核验 | 实际观察 |
| --- | --- |
| Run | 打开根目录 `main.py`，工具栏 **main → 绿色 Run**。控制台显示 `D:\TestPilot AI\.venv\Scripts\python.exe` 运行 `D:\TestPilot AI\main.py`，demo 模式，Uvicorn 进程 43164。 |
| 自动打开 | 控制台记录默认浏览器打开请求，Edge 文档标题为 Dashboard · TestPilot AI，实际地址为 `http://127.0.0.1:8000/`。 |
| 单服务 | Run 控制台记录 `GET /` 及 `GET /api/health` 为 HTTP 200。Edge 无障碍树显示两处“已连接”以及 F01–F06 六个工作台入口，链接同源。 |
| Stop | 点击本次验收进程的红色 Stop，控制台记录 `Application shutdown complete.`、`Finished server process [43164]`、退出码 0。 |
| Debug | 使用 PyCharm 自带的 pydevd 启动根入口，实测断点位于 `backend/app.py:24` 的 `create_app`，暂停原因 111；继续后健康接口返回 `status=ok, database=ok, mode=dev`。本项通过真实调试协议复验。 |

[Run 控制台截图](pycharm-run.jpg) · [调试输出](debug.txt) · [复查脚本](../../tests/check_pycharm_debug.py)

```powershell
.\.venv\Scripts\python.exe tests/check_pycharm_debug.py "E:/PyCharm 2026.1.2/plugins/python-ce/helpers/pydev/pydevd.py"
```
