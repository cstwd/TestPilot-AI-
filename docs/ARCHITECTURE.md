# TestPilot AI 技术架构 V1

## 运行拓扑

Windows 11 上，PyCharm 以项目解释器执行根目录 `main.py`。入口配置本地监听地址、端口、运行模式和浏览器启动行为，Uvicorn 在同一 Python 进程内运行 FastAPI。浏览器访问 `http://127.0.0.1:8000/`，页面、静态资源和 JSON 接口共享地址。演示部署聚焦单机、单实例。

```text
PyCharm Run / Debug → main.py → Uvicorn → FastAPI
                                            ├─ GET / → Jinja2 → Dashboard
浏览器 ← HTML、CSS、JavaScript ←───────────────├─ GET /static/…
                                            ├─ GET /api/health → SQLite 检查
                                            └─ POST /api/self-test → 固定可信 Pytest 用例
```

## 模块边界

| 位置 | 职责 | 边界 |
| --- | --- | --- |
| `main.py`、`.run/` | 脚本入口与共享 PyCharm 配置 | Run 和 Debug 走同一入口，业务路由独立于入口 |
| `backend/` | FastAPI 应用、SQLite 生命周期、健康检查、可信自检 | 路由负责 HTTP 契约，持久化和执行细节留在后端模块 |
| `frontend/` | Jinja2 模板和随服务发布的静态资源 | 浏览器通过相对 URL 调用本机 API，无需启动第二个服务 |
| `tests/`、`eval/` | 工程回归、后续离线评测 | 区分平台自检、用户项目测试和评测样本 |
| `agents/`、`.agents/skills/`、`hooks/`、`mcp-server/` | 后续自动化集成与复核 | 工具接口、授权范围、审查记录由 WP05 管理 |
| `collab-log/`、`transcripts/`、`reports/` | 责任分配、实际操作、验收证据 | 记录执行方式、可复查证据和未验收项 |

## PHASE-01 接口

| 请求 | 调用方 | 成功条件 | 失败如何判读 |
| --- | --- | --- | --- |
| `GET /` | 默认浏览器 | 200，页面可见且静态资源成功加载 | 同时检查响应、资源路径和控制台错误 |
| `GET /api/health` | Dashboard、验收脚本 | 200，`status=ok` 且 `database=ok` | 将服务不可达和数据库异常分别记录 |
| `POST /api/self-test` | Dashboard、验收脚本 | 平台固定可信用例确实运行，返回 `status=passed` | 以实际执行结果判定，异常不能计入通过 |

## 存储、启停和调试

SQLite 默认文件为 `data/testpilot.sqlite3`，由 `backend/database.py` 管理。应用在启动时初始化数据库，浏览器通过健康接口读取探测结果。服务退出时应释放数据库资源与监听端口，再次运行同一入口应可启动。端口被其他进程占用时，入口提供诊断，保留占用进程。

默认 `demo` 模式采用单实例和常规日志。开发时使用 `--mode dev` 开启调试日志和 `/docs`，断点可设在 `backend/app.py` 的路由函数内。自检由 `backend/self_test.py` 调用，运行期间重复自检返回 HTTP 409。参数、解释器配置及实际验证范围参见 [README](../README.md) 和 [阶段验收](../TP_PHASE_01_ACCEPTANCE.md)。

## 业务阶段的执行边界

后续流水线由项目导入、静态分析、测试生成、受限执行、缺陷确认与回归、报告导出组成。导入的 Python 源码先作为数据解析。生成的测试与用户代码具有同一信任级别，均须进入独立受限环境，执行权限、可写目录、网络、时间及资源限额必须有验证证据。受限环境未验收时，业务运行请求保持关闭。当前固定自检只能证明平台可调用测试模块。

建议以项目、文件摘要、测试版本、运行标识串联证据。修复后在同一用例和受控环境上重新运行，记录新结果并保留旧结果。详细业务表结构和运行器方案由 WP01、WP03、WP04 在相应接口开发前确定。
