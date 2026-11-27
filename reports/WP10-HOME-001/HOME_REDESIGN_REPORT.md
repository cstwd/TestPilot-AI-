# WP10-HOME-001 首页重设计

TestPilot AI 的根页现在是 Command Center。首页左侧依次呈现系统连接、自检和六个工作台，右侧呈现真实项目活动。窄屏按快捷操作、系统状态、自检、业务模块、最近活动和外部工具的顺序阅读。

## 实施基线

| 项目 | 核对结果 |
| --- | --- |
| 工作区 | `D:\TestPilot AI`，分支 `codex/tp-course-remediation-001` |
| 开工 HEAD | `039b14d2af6a1eef52f15978225d231cef1d2236`，已包含 Demo Lab 实际工作台 |
| WP09 最终提交 | `d872fa1b1bcfaf6041f80aef4a6b408ce6db9dfd`，F01–F06 统一基线 |
| 并行文件 | 课程成员验收日志、模型报告和 Office 锁文件已在开工时存在，由各任务继续维护 |
| 旧根页 | [Dashboard 模板](../../frontend/templates/dashboard.html) 使用 Jinja，旧版 [`dashboard.css`](../../frontend/static/dashboard.css) 仍被现有引擎和变异工作台引用 |

## 布局与操作

- 顶栏复用工作台品牌、线形图标和工具按钮。运行模式取根路由传入的真实参数。系统设置可保存在本机浏览器中自动展开自检输出的偏好。帮助说明首页与 F04 会运行哪些测试。
- Hero 用顶部标题、三项入口和轻量 CSS 结构图标识工作流。创建项目提交到现有项目接口。导入代码打开所选项目中的 F01 上传控件，空数据时先打开创建项目表单，再进入上传。恢复入口记录本浏览器实际打开的项目 ID，在项目列表中核对后进入 F01。首次使用时可打开最近创建的项目。 [模板](../../frontend/templates/dashboard.html) · [首页控制器](../../frontend/static/dashboard.js)
- 工作台以 F01–F06 实际路由为准，随着活动项目选择提供真实项目上下文。TestPilot Demo Lab 和智能测试引擎沿用 `/workbench/demo-lab`、`/engine` 的同标签页打开方式，并保留原有可访问名称。 [模块表](../../frontend/templates/modules.html) · [工作台路由](../../backend/workbench.py) · [引擎路由](../../backend/engine_web.py)

## 数据来源

| 区域 | 真实契约与展示 |
| --- | --- |
| System Health | `GET /api/health` 的 `ok / 200` 对应服务、SQLite 连接成功，`degraded / 503` 对应服务响应和数据库异常。请求或格式错误显示检查失败及数据库无法确认。时间为本次响应或失败在浏览器完成的时间。 [FastAPI 路由](../../backend/app.py) · [SQLite 健康检查](../../backend/database.py) |
| Test Runner | `POST /api/self-test` 返回通过、失败、并发占用或请求拒绝。保留固定样例入口、请求等待状态及 API 真实返回的文本。确认完成时更新自检时间，原始输出使用纯文本终端呈现。 [接口](../../backend/app.py) · [固定样例执行](../../backend/self_test.py) |
| 项目和版本 | `GET /api/projects` 提供最近创建的项目。右侧其余活动按项目选择读取，`GET /api/projects/{id}/files` 提供最近导入的文件版本。项目及版本新旧采用接口的 ID 排序。 [项目与版本接口](../../backend/projects.py) |
| 运行和缺陷 | `GET /api/projects/{id}/runs` 提供真实终态、时间、套件及版本。`GET /api/projects/{id}/bugs` 提供缺陷状态和原始运行身份。 [运行](../../backend/runs.py) · [缺陷](../../backend/bugs.py) |
| 质量报告 | 由最近运行请求 `GET /api/runs/{id}/report`，核对报告的项目、运行和被测版本后显示。项目、文件或缺陷没有时间字段时显示真实 ID 或版本。 [报告接口](../../backend/quality.py) |

最近活动在项目切换时清除上一个项目的详情，取消其未完成请求，并分别显示四类数据的读取结果。项目列表不可用、单类服务故障和没有记录都有明确状态。最近创建项目单列在筛选器上方。

## 交付索引

- [浏览器验收与真实 Edge 截图](HOME_BROWSER_ACCEPTANCE.md)
- [全站回归与原始输出](HOME_REGRESSION_REPORT.md)
- [视觉组件复用地图](HOME_VISUAL_COMPONENT_MAP.md)
- [协作缺陷记录](../../collab-log/bugs/WP10-HOME-001.md)

完整回归在隔离基线通过，当前分支的首页及既有工作台兼容复验也通过。独立提交标题为 `WP10-HOME-001 redesign the TestPilot Command Center`。可用 `git log -1 --format=%H -- reports/WP10-HOME-001/HOME_REDESIGN_REPORT.md` 查询提交。等待人工验收。

**READY_FOR_HOME_VISUAL_ACCEPTANCE**
