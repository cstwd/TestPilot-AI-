# TestPilot AI

智能软件测试生成与缺陷检测平台。当前版本提供本地 Dashboard、SQLite 健康检查和一次可以从浏览器发起的 Pytest 自检。F01–F06 的业务验收场景见[需求规格](docs/SPEC.md)。

## Windows 11 上使用 PyCharm

1. 在 PyCharm 选择 **File → Open**，打开 `D:\TestPilot AI`。
2. 在 **Settings → Python → Interpreter**（部分版本显示为 **Project → Python Interpreter**）选择该项目的解释器。本机已经创建 `D:\TestPilot AI\.venv\Scripts\python.exe`。若列表中没有它，选择 **Add Local Interpreter → Existing** 并定位到该文件。
3. 在新电脑首次打开时，可用 Python 3.13 创建项目虚拟环境。打开根目录的 `requirements.txt`，使用 PyCharm 提示的 **Install requirements** 将依赖装入项目解释器。也可以在 Python Packages 窗口按文件逐项安装。已配置的环境只需执行下一步。
4. 打开根目录 `main.py`，点击绿色 **Run**。也可在工具栏选共享配置 **TestPilot AI** 后点击 Run。应用就绪后，默认浏览器会自动打开本地 Dashboard。[打开本机 Dashboard](http://127.0.0.1:8000/)
5. 确认“后端接口”和“项目数据库”均为“已连接”，点击 **运行自检**。按钮会调用后端，在临时目录运行仓库固定样例。点击 PyCharm 红色 **Stop** 即可停止；再次点击 Run 可重新启动。

## 演示、调试与常见问题

| 场景 | PyCharm 操作 / 预期 |
| --- | --- |
| 本机演示（默认） | 共享配置无参数。使用单个 Uvicorn 进程、普通日志和自动打开浏览器。 |
| 开发调试 | 在 **Run → Edit Configurations** 复制共享配置，Parameters 填 `--mode dev`。在 `backend/app.py` 的 `health` 函数体边栏设置断点，点击 **Debug**。入口探测或页面“重新检查”会触发断点，按 **F9** 继续。开发模式提供调试日志及 `/docs`。 |
| 端口被占用 | 查看 Run 控制台提示。停止自己启动的旧服务后重试；需要同时调试时，在副本配置填 `--port 8001`。 |
| 无浏览器或批量验收 | Parameters 可加 `--no-browser`，按日志中的地址访问。自动打开请求失败时日志也会给出地址。 |
| 缺少依赖 | 对照 Run 控制台首行与项目 Interpreter 路径，用该解释器安装根目录依赖。 |
| SQLite 初始化问题 | 默认路径为 `data/testpilot.sqlite3`。检查数据目录写权限、数据库版本和控制台异常。可在运行配置环境变量中用 `TESTPILOT_DATA_DIR` 指定独立数据目录。 |

## 模块与验收

- [入口](main.py)和[共享运行配置](.run/TestPilot_AI.run.xml)控制本地启动。[后端](backend/)提供路由、数据库探测与固定自检，[前端](frontend/)由同一服务发布 Jinja2 模板、CSS 和 JavaScript。
- [架构](docs/ARCHITECTURE.md)、[功能映射](docs/FEATURE_MAP.md)、[三天计划](docs/THREE_DAY_PLAN.md)描述三天范围。[工作包](docs/work-packages/)和[贡献表](collab-log/member_contributions.md)列出负责人、实际操作和验收归属。
- [本阶段验收报告](TP_PHASE_01_ACCEPTANCE.md)包含真实的 PyCharm Run、浏览器操作、断点、重启与端口冲突证据。

可从 PyCharm 的测试运行配置执行 `tests/`。需要在 PowerShell 独立复验时，从项目根目录运行以下命令。本机浏览器验收采用已安装的 Microsoft Edge。

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

当前工程只执行随项目发布的固定样例。项目导入、AI 生成测试以及对用户代码的受限执行将在后续阶段交付。
