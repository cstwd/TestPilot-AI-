# WP10-HOME-001 回归与签收记录

前端与产品职责对应 WP02 陈万策。实际实施、浏览器操作及测试记录人为 Codex。`testpilot_reviewer` 独立复核入口、项目身份和状态映射。陈帅廷协调人工签收。

## 环境与命令

Windows 11、Python 3.13.11、Node 24.13.0、Playwright 1.65.2、Edge 158.0.4370.33。用例用真实 `main.py` 同源服务、独立 SQLite 与现有 WASI 执行器。截图来自 Edge，无实体移动设备参与。

| 回归范围 | 命令或实测路径 | 证据 |
| --- | --- | --- |
| 首页与工具定向 | `python -m pytest -q -s tests/test_dashboard.py tests/test_home_command.py tests/test_demo_lab.py::test_edge_full_product_flow tests/test_phase03_api.py::test_engine_browser --tb=short` | 5 项通过，82.95 秒。[原始输出](raw/home-edge.txt) |
| 正常启动 | `python main.py --port <独立端口>`，在浏览器自动请求根页后由 Edge 核对标题与 SQLite | [启动轨迹](raw/main-start.txt) |
| JS 语法 | `node --check frontend/static/dashboard.js` | [静态与范围检查](raw/scope-audit.txt) |
| 测试清单 | `python -m pytest -q --collect-only tests eval/phase05/test_manifest.py` | [176 项](raw/test-inventory.txt) |
| 完整 Hook | `python hooks/verify.py --scope full --report reports/course-final/verify-full.txt` | 在隔离目录执行。Pytest 176 项通过，18 分 56 秒。Node 3 项通过，退出码 0。[原始输出](raw/full-verify.txt) · [基线与源文件摘要](raw/full-verify-overlay.json) |

原首页浏览器测试只将主标题断言更新为需求指定的“智能测试控制中心”，健康、自检、移动端和断网恢复断言保留。两个新增测试验证真实活动、快捷操作、八个入口、空态、故障和恢复。旧 Demo Lab 与智能测试引擎测试原样复用。早期定向执行发现测试读取创建响应体与正常导航竞争，定向复验改用返回 201、目的路由和真实持久化列表的联合断言。

## 影响范围

WP10 的产品代码只改动根页模板、脚本并新增 `home.css`。`dashboard.css` 继续服务旧工具。全量运行基于开工提交 `039b14d` 加本包 5 个源码和测试文件，含 F01–F06 原有浏览器用例、WP09 端到端与 36 个尺寸组合。F01–F06 模板、公共设计系统、运行器、业务 API、数据库及 WP09 截图位于本包的提交范围之外。 [WP09 基线](../WP09-001/FRONTEND_V1_FINAL_ACCEPTANCE.md)

回归期间并行提交 `b40b54e` 引入 F05 AI 修复，并重用 F01 源码校验和版本写入逻辑。另以 `f5a28c5` 为基线运行 `python -m pytest -q -s tests/test_dashboard.py tests/test_home_command.py tests/test_project_workspace.py tests/test_bug_intelligence.py tests/test_wp09_integration.py --tb=short`。首页、F01、F05 和 WP09 原有六页闭环合计 11 项通过，耗时 134.18 秒。 [当前分支复验](raw/head-compatibility.txt)

“打开最近工作区”按本机浏览器记录恢复项目。记录来自首页打开工作台，或工作台经品牌链接返回首页。无本机历史时进入最近创建的项目。首页只使用现有项目记录，跨工作台的浏览器后退历史由各工作台管理。
