# TestPilot AI 产品需求规格

面向 Python 开发人员、测试人员与质量工程人员的本机测试工作台。开发人员用代码版本和失败节点确认修复，测试人员按源码契约生成并核查用例，质量人员复核实测覆盖率、变异得分和证据。陈帅廷协调五个等额工作包。[需求访谈](../transcripts/requirements-interview.md) · [PHASE-01 原始任务](../transcripts/TP-PHASE-01.md)

## 核心场景与验收条件

| 功能 | 用户过程 | 可测试条件及接口 |
|---|---|---|
| F01 项目与文件 | 创建项目，上传同名文件并切换历史版本 | `POST /api/projects/{project_id}/files` 保存 UTF-8 原文、递增版本和 SHA-256。旧版本仍可读 |
| F02 静态与智能分析 | 选择版本并定位函数、类或语法诊断 | `GET /api/files/{file_id}/analysis` 给出 AST、行段及语法信息。智能理解走 `POST /api/engine/files/{file_id}/understanding` |
| F03 套件生成 | 选择函数，以模板生成或显式请求本机 AI | `POST /api/files/{file_id}/suites` 记录生成方式、测试文本、SHA-256、静态校验和首跑。AI 请求异常有可见失败 |
| F04 测试执行 | 选择套件和同项目同名文件版本，查询日志 | `POST /api/suites/{suite_id}/runs` 真实执行，`GET /api/runs/{run_id}` 保留退出码、节点、计数和覆盖率，忙碌时返回 409 |
| F05 缺陷与回归 | 从失败节点登记缺陷，选择较新版本回归 | `POST /api/runs/{run_id}/bugs` 建立缺陷，`POST /api/bugs/{bug_id}/regressions` 仅在原套件的原失败节点通过时解决 |
| F06 质量报告 | 切换运行并下载 JSON | `GET /api/runs/{run_id}/report/export` 与页面所选运行和摘要一致。通过率排除跳过，覆盖率使用可执行行 |
| F07–F12 智能引擎 | 选择函数，生成、实跑并查看失败归因与修正记录 | `POST /api/engine/files/{file_id}/tasks` 固定生成模式，工件可追溯，归因不确定时保留待复核，修复条件独立于首次执行 |
| F13 变异测试 | 从完成任务创建会话，评估并可选反馈补测 | `POST /api/engine/tasks/{task_id}/mutations` 固定清单，校验未变异原版，逐项运行。终止、错误和未跑仍占分母，`GET /api/mutations/{id}/report` 导出 |

## 数据与组件

FastAPI 通过 Uvicorn 在 Windows/PyCharm 单进程监听 `127.0.0.1:8000`，同源提供 Jinja2 与静态资源。SQLite 以项目 ID 与文件版本 ID 关联不可变源码、套件、运行和缺陷回归。智能引擎按任务 ID 存储类型化记录，变异会话和逐项事件保存原始编辑、清单、校准和执行结果。模型请求通过固定 Qwen3.8-27B Provider 发送到同机 Ollama，使用 Schema 和独立日志关联运行 ID。WASI CPython、Wasmtime 与 Pytest 承载所有产品业务测试。[架构图](ARCHITECTURE.md)

## 非功能标准

- Windows 11 从根入口 Run 自动打开默认浏览器。Debug 与 Run 使用同一进程。停服应释放端口，端口已被占用时保留原服务并给出诊断。
- 导入限制为 128 KiB UTF-8 单个 Python 文件。分析在宿主以静态数据解析，生成源码也经过静态校验。业务运行在独立 WASI，宿主的固定自检只运行仓库样例。
- WASI 使用明确的只读挂载，关闭网络和子进程，限制内存、燃料、输出及执行时限。缺少运行条件时返回错误。记录区分静态通过、模型生成及真实执行。
- 本机模型记录固定权重和清单身份。身份、连接、上下文或资源校验失败时回报失败。模板作为独立显式操作。提示和模型回复归入本机运行证据，课程材料使用合成样例。
- 单实例与本机信任范围以外的部署需要独立设计授权与数据治理。[执行边界](phase03/SANDBOX.md) · [模型部署](phase06/DEPLOYMENT.md) · [测试与评测](COURSE_TESTING.md)
