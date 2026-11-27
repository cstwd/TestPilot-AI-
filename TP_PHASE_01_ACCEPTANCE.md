# TP-PHASE-01 初始化验收报告

**工程验收通过。** 2026-11-27（北京时间），Codex 在 Windows 11 的 PyCharm 2026.1.2 中实际点击绿色 Run，默认浏览器 Edge 自动打开 `http://127.0.0.1:8000/`。页面显示 FastAPI 和 SQLite 均已连接，点击运行自检得到“通过”。最终工程回归为 **5 passed in 42.12s**。项目组长负责后续阶段安排，本报告记录实际工程操作及结果。

**交付位置**　`D:\TestPilot AI` 本身是项目根目录。工程基线为本地 `main` 分支提交 `8038be278d656a716a5c9cb2cb629602864eb011`。本报告、IDE 现场证据和工作包验收回填在后续归档提交中，可用 `git log --oneline --decorate -2` 复查。提交操作者为 Codex。

## 初始化任务核对

| 序号 | 任务及实际状态 | 检查结果与文件 | 待办 |
| --- | --- | --- | --- |
| 1 | 环境与技能检查完成 | Windows 11 25H2 build 26200，Python 3.13.11，Git 2.51.1.windows.1，Codex CLI 0.134.0，Node.js v24.13.0，npm 11.6.2。已检查本机技能目录及会话技能清单，本次使用 frontend-design、computer-use；已创建项目虚拟环境，`pip check` 返回 `No broken requirements found.`。实测依赖见 [requirements.txt](requirements.txt)。 | 新机器须在项目解释器安装依赖 |
| 2 | 目标目录检查和原文件保全完成 | 初始目录仅有 `.idea/` 和 PyCharm 示例入口。保留原 IDE 配置；原示例以原始字节单独归档，SHA-256 为 `E78EB0059F17F824153147068FFE0775DE7C3B0B0B60C6C9BF222D8FE1E43DCB`。[原始示例](transcripts/original-main.py.txt) | 无 |
| 3 | Git 与分支建立 | 初始化前 `git rev-parse` 报目录不属于仓库，随后 `git init -b main` 成功。提交基线含 44 个文件。使用 `.gitignore` 排除本机虚拟环境、数据库与 IDE 私有状态。 | 无 |
| 4 | 五人责任与贡献表完成 | 五个独立工作包各含任务、输入输出、标准、文件、Git 记录及结果。陈帅廷、陈万策、赵君豪、马雪朋、王选中计划各占 20%，合计 100%。[贡献表](collab-log/member_contributions.md) · [工作包](docs/work-packages/) | 实际执行持续按人或代理记账 |
| 5 | 目录结构建立 | 前后端、测试、评测、Agent 工程、协作、报告和演示目录已纳入 Git；空目录含占位文件，可从基线还原。`git ls-tree -r --name-only 8038be2` 可复核。 | 按三天计划填充后续模块 |
| 6 | 正式访谈与 SPEC 初稿完成 | 三问均收到需求提出者答复“沿用任务书”。SPEC 包含 F01–F06、P0、业务验收场景、阶段边界和待决事项。[真实问答](transcripts/requirements-interview.md) · [SPEC](docs/SPEC.md) | 业务阶段细化导入范围、导出格式、评测口径 |
| 7 | AGENTS V1、架构和功能映射完成 | 长期 PyCharm 规范、可信执行边界、六项功能的输入输出、责任和验收标准均已归档。[AGENTS](AGENTS.md) · [架构](docs/ARCHITECTURE.md) · [功能映射](docs/FEATURE_MAP.md) | 随后续接口演进修订 |
| 8 | 协作与证据目录完成 | [协作日志](collab-log/LOG.md)区分责任人与实际操作人，[缺陷日志](collab-log/bugs/LOG.md)记录三项实查问题，访谈保存在 [transcripts](transcripts/)。 | 后续阶段追加真实记录 |
| 9 | 基础项目和启动实测通过 | 根入口、共享运行配置、同源模板与静态资源、SQLite 和固定 Pytest 自检均可运行。见下方十项验收及 [PyCharm 教程](README.md)。 | F01–F06 核心业务另行实现 |
| 10 | 评估、排期、风险及阶段报告形成 | [项目评估](docs/PROJECT_ASSESSMENT.md) · [三天计划](docs/THREE_DAY_PLAN.md) · [风险登记](docs/RISK_REGISTER.md)；本文件为 PHASE-01 独立验收报告。 | 由组长协调下一阶段 |

## PYCHARM_RUN_ACCEPTANCE

| 项 | 验收项 | 状态与实际证据 | 实现 / 可复核证据 |
| --- | --- | --- | --- |
| 1 | PyCharm Run 启动 | **通过。** 项目解释器运行根入口。点击 PyCharm 绿色 Run 后，控制台显示服务 PID 39968 和 `Application startup complete`。 | [main.py](main.py) · [共享配置](.run/TestPilot_AI.run.xml) |
| 2 | 默认浏览器自动打开 | **通过。** 未手动输入网址。Run 后发现新打开的 Edge 项目页；读取到文档地址 `http://127.0.0.1:8000/` 和标题 `Dashboard · TestPilot AI`。控制台同时记录默认浏览器打开请求。 | [现场记录](reports/pycharm-run.md) |
| 3 | Dashboard 显示 | **通过。** Edge 显示“启动仪表盘”和两项“已连接”。Playwright 在 1366×900 桌面窗口和 375px 宽窗口上复验，窄屏无横向溢出。 | [页面截图](reports/dashboard.png) · [浏览器测试](tests/test_dashboard.py) |
| 4 | 前后端通信 | **通过。** 页面请求 `GET /api/health` 成功；点击自检后 `POST /api/self-test` 返回 200。浏览器测试还验证断连后的错误状态、恢复后的状态刷新以及页面显示结果与 JSON 一致。 | [浏览器日志](reports/dashboard-check.txt) · [页面脚本](frontend/static/dashboard.js) |
| 5 | SQLite | **通过。** 健康接口读取实际元数据并返回 `database=ok`；集成测试写入临时库探针，重启后读回同一值。不可写路径和不兼容版本均有诊断，已验证原版本库文件字节不变。 | [数据库模块](backend/database.py) · [启动日志](reports/startup-check.txt) |
| 6 | 测试执行器 | **通过。** 按钮真实运行 Pytest。Edge 验收的固定样例结果为 `1 passed in 0.03s`。该结果对应平台自检样例。 | [执行器](backend/self_test.py) · [固定样例](backend/sample_case.py) · [运行输出](reports/dashboard-check.txt) |
| 7 | 停止服务与重启 | **通过。** 点击 Stop 后 IDE 记录 `Application shutdown complete` 和退出码 0，随后 Debug 成功复用 8000。独立进程测试用同一端口 61723 运行 demo、dev，两次正常退出码均为 0。 | [原始日志](reports/startup-check.txt) · [启动测试](tests/test_startup.py) |
| 8 | 端口冲突 | **通过。** 第二个入口申请已占用的 61723 时退出 1，中文提示端口已被占用；原实例仍可执行自检。 | [启动日志](reports/startup-check.txt) |
| 9 | PyCharm Debug 断点 | **通过。** 在根入口设置行断点，最终源码 Debug 会话显示 `MainThread`、`<module>, main.py:15`，按 F9 继续。独立调试协议复验另命中 `backend/app.py:24` 的 `create_app`，恢复后健康接口返回 200。 | [IDE 断点截图](reports/pycharm-breakpoint.jpg) · [后端调试证据](reports/pycharm-debug.md) |
| 10 | 单服务运行 | **通过。** 实际入口用一个 Uvicorn 提供 HTML、CSS、JS 和 API，演示期间所有应用请求都到同一回环地址。固定测试请求短暂启动 Pytest 子进程。 | [架构](docs/ARCHITECTURE.md) · [路由](backend/app.py) · [现场记录](reports/pycharm-run.md) |

## 复验和阶段边界

在项目根目录执行 `.\.venv\Scripts\python.exe -m pytest tests -q`，最终输出为 `5 passed in 42.12s`，退出码 0。构成为 4 项入口/异常回归及 1 项真实浏览器综合测试。IDE 操作和 PyCharm 调试协议验证分别记证，未重复计入这五项。依赖安装和本机 HTTP/浏览器验收通过环境许可执行；首次受沙箱网络策略阻止的尝试未计为通过。

后续按工作包开发 F01–F06，包括导入、AST、AI 生成、受限执行、缺陷回归和质量报告。WP04 须先验证受限执行器，再开放对用户源码和生成测试的运行；当前阶段只向页面开放固定自检。WP05 的项目专用 MCP、Skills、Hooks 与常设 Reviewer 配置列入后续交付。团队贡献按任务书分配，个人签收由项目组另行记录。
