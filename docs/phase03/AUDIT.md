# PHASE-03 开发前架构及依赖审计

2026-11-27。陈帅廷负责决策与验收，实际审计由 Codex 执行。检查时本地主分支 HEAD 为 `da798a4`，受测代码 `f31a901` 和初始归档 `88ebf23` 均在祖先链。独立工作产生的 `reports/model/` 按其原有归属保留。

| 实查入口 | 实际观察 | 开发影响 |
| --- | --- | --- |
| `git log -13 --oneline`、`git status --short --branch` | 首查工作区干净，主分支比本地 origin/main 引用多四个提交 | 保留已有历史和阶段归档 |
| `main.py`、`backend/app.py`、`backend/workbench.py` | 单 Uvicorn 实例，FastAPI + Jinja2 同源，本机写操作验证 Origin | 新增独立引擎路由，复用主入口 |
| SQLite 只读打开 `data/testpilot.sqlite3`，查询 sqlite_master 和 schema_version | 版本为 1，表为 app_metadata、projects、files、suites、runs、bugs、regressions | 加表并以不可变文件 ID 关联，不改旧数据及版本号 |
| `backend/analysis.py`、`generation.py` | F02 已提取签名、文档、符号和位置；ModelAdapter 收 source、target，只有 TemplateAdapter 已注册 | 共用签名和静态检查，新增上下文、策略与生成溯源 |
| `runner.py`、`wasi_worker.py`、`guest_pytest.py` | 宿主工作进程运行只读 WASI，固定 Pytest 命令；解析 JSON 个案与行覆盖，旧报告只提供合并日志 | 继续使用该隔离边界，按需新增分支数据和逐例追踪 |
| `.venv/Scripts/python -m pytest tests --collect-only -q` | 实际收集 35 项，覆盖启动、六模块、浏览器及跨版本回归。历史通过记录为 35 passed in 153.33s | 集成后重新运行原件和新增测试 |
| 项目解释器和 importlib.metadata | Windows / CPython 3.13.11，FastAPI 0.165.0，Jinja2 3.1.6，Uvicorn 0.54.0，pytest 9.2.0，Coverage.py 7.17.5，Hypothesis 6.170.17，Playwright 1.65.2，wasi-python 0.1.6，wasmtime 51.0.0 | 已安装 Coverage.branch_stats 可提供分支分子、分母 |
| 实际桌面 `ollama list` 和本机模型列表接口 | Ollama 已安装，首次盘点无已登记模型。LM Studio 未返回模型列表，应用尚无供应商配置 | 模型模式须由真实响应驱动。可用性在 F09 实测时再次核对 |

基线工程验收和此次采集的测试清单可分别核对。[PHASE-02 报告](../../TP_PHASE_02_ACCEPTANCE.md) · [测试定义](../../tests/)
