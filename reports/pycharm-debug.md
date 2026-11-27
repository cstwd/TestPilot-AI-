# PyCharm 调试后端断点实测

2026-11-27 11:14（UTC+8）复验，实际操作人 Codex。使用本机 PyCharm 2026.1.2 自带的 Python 调试后端与项目虚拟环境运行根入口。测试脚本扮演调试客户端，设置行断点，读取暂停帧后发出继续指令。

```powershell
& '.venv/Scripts/python.exe' tests/check_pycharm_debug.py 'E:/PyCharm 2026.1.2/plugins/python-ce/helpers/pydev/pydevd.py'
```

| 观察项 | 实测值 |
| --- | --- |
| 入口及参数 | `main.py --mode dev --no-browser --port 57008` |
| 暂停位置 | `backend/app.py` 第 24 行，`create_app` 函数 |
| 调试协议返回 | `CMD_THREAD_SUSPEND`，`stop_reason=111`（行断点） |
| 继续后的服务进程 | Uvicorn 日志显示 PID 46328 |
| 继续后的实际 HTTP 请求 | `GET /api/health` 返回 200，响应为 `{"status":"ok","database":"ok","mode":"dev"}` |
| 数据隔离 | 以 `TemporaryDirectory` 创建本次专用目录，通过 `TESTPILOT_DATA_DIR` 传给子进程；脚本确认其中生成 `testpilot.sqlite3`，输出 `database_in_temp_dir=true` |
| 检查退出码 | 0 |

调试连接和应用均使用单独的本机回环端口，退出后清理专用数据目录。较早的沙箱内尝试被 Windows 拒绝（10013），本轮经获准使用本机回环连接后完成。该证据覆盖 PyCharm 原生调试后端、真实入口、断点命中和继续执行；IDE 编辑器中的设置断点及按钮操作需要独立界面证据。
