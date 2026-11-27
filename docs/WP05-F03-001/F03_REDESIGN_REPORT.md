# F03 AI Test Generation Studio

工作包 WP05-F03-001，日期 2026-11-27。WP05 登记负责人王选中，F03 业务关联 WP03，界面与交互关联 WP02。实际实施、测试、截图和提交由 Codex 执行，组长陈帅廷协调人工复核。[贡献表](../../collab-log/member_contributions.md) · [功能映射](../FEATURE_MAP.md)

## 开工审计

实际工作区是 `D:\TestPilot AI`，开工提交为 `9f048d09985f9493eb117ba0d2e9f0559aff9144`。开工时只有其他工作遗留的未跟踪目录 `reports/model/`。F01 和 F02 已共用工作台壳层、图标、控件、状态、等宽源码样式及 Python 着色器。原 F03 是普通工作台中两个表单区块，使用全局项目／文件选择器、目标函数下拉框和一个预格式化文本区。原实现可用 `git show 9f048d0:frontend/templates/generation.html` 和 `git show 9f048d0:frontend/static/generation.js` 查看。[共享模板](../../frontend/templates/studio_components.html) · [公共 V1 说明](../WP04-F01-001/DESIGN_SYSTEM_V1_IMPLEMENTATION.md) · [既有浏览器测试](../../tests/ui_workbench.py#L60)

| 请求 | 读取或写入的真实证据 |
| --- | --- |
| `GET /api/projects`、`GET /api/projects/{project}/files` | 项目和该项目下的不可变修订清单，文件行 ID 同时用作版本记录 ID。 |
| `GET /api/files/{file}`、`GET /api/files/{file}/analysis` | 同一修订的源码、SHA-256 及 AST 符号、定义起止行、参数、返回标注、文档字符串。 |
| `POST /api/files/{file}/suites` | 固定提交 `{target, mode:"template"}`；服务端模板生成 Pytest、做静态检查、按内容存储套件，再尝试首跑。422 返回服务端详情。忙时返回 409，刷新套件列表可发现已持久化的候选。再次提交同内容复用套件，若已有首跑也复用首跑。 |
| `GET /api/files/{file}/suites`、`GET /api/suites/{suite}` | 当前修订的套件清单和单条详情。详情含 `file_id`、`target`、`mode`、`source`、`sha256`、`suggestions`、`format_checked`，另有可空的 `initial_run`。数据库套件表当前没有生成时间字段。 |
| `GET /api/runs/{run}` | 用首跑的真实 ID 读取执行状态、各结果计数、耗时、落库时间；以项目、版本、套件、运行的四个键核对关联。落库时间标成运行记录时间。 |

接口位置见 [版本及源码](../../backend/projects.py) · [AST 响应](../../backend/analysis.py) · [生成与检查](../../backend/generation.py) · [真实运行](../../backend/runs.py)。

## 页面与交互

| 区域 | 呈现及身份约束 |
| --- | --- |
| Explorer | 直接选择项目和不可变文件版本。当前文件加 vN 与记录号。搜索匹配限定名，结果用原生可键盘操作的列表；过滤时保留当前选择并标注。复用 F02 AST 适配器的 `topLevelEligible`，限模块体内唯一的同步函数，同时遵守接口名称长度。能否形成具体测试仍由服务端模板校验。 |
| 中央源码与配置 | 选择函数后按真实定义行显示对应片段及原始行号。固定 `template` 模式明示为本地模板，生成按钮使用 V1 紫色主操作。请求期间禁用重复提交，以不定时的等待文字反馈。 |
| 中央套件区 | 可在当前版本内查看历史套件。套件 ID、受服务端检查的测试源码、属性测试建议及首次运行状态一并展示。两处源码只读、按需分页、独立滚动，通过文本节点着色。 |
| Inspector | 目标函数与套件来源分别记录，历史套件可以与当前目标不同。签名、限定名、定义行、输入版本、套件摘要、检查详情和运行明细使用 API 数据。 |
| Console | 生成请求、当前套件静态检查、该套件首次 Pytest 各有独立状态。明确显示当前套件 ID、真实运行 ID。可进入 F04 查看该运行。没有首跑时提供按指定套件进入 F04 的入口。 |

桌面占用单屏工作台，三栏分别滚动，Console 留在视口底部。900 px 以下依次阅读 Explorer、源码与配置、测试结果、Inspector、Console。手机标题区可跳转输入、结果或状态，顶部菜单提供模块导航。[页面模板](../../frontend/templates/generation.html) · [布局](../../frontend/static/generation.css)

切换函数或历史套件更新 URL，保留项目 ID、版本 ID、函数限定名和套件 ID。显式指定的项目、修订或套件无法匹配时提示重选，历史查询限定在当前版本。在 F04 链接中传递当前套件及可用的首跑 ID。[公共路由](../../frontend/static/workbench.js) · [F03 控制器](../../frontend/static/generation.js)

## 验收交接

[截图及测试证据](../../reports/WP05-F03-001/F03_BROWSER_ACCEPTANCE.md) · [回归与失败路径](../../reports/WP05-F03-001/F03_REGRESSION_REPORT.md) · [组件复用地图](COMPONENT_REUSE_MAP.md)

通过 `git log -1 --format="%H %an %s" -- docs/WP05-F03-001/F03_REDESIGN_REPORT.md` 查询实际提交。工作包状态为 `READY_FOR_F03_VISUAL_ACCEPTANCE`，人工签收待项目组确认。
