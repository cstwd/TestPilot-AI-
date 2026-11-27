# F04 Test Execution Control Center

工作包 WP06-F04-001，2026-11-27。实际设计、实施、测试与提交由 Codex 执行。F04 业务责任按现有功能映射关联 WP03 赵君豪、WP04 马雪朋，前端关联 WP02 陈万策。组长陈帅廷协调人工验收。[责任分配](../../collab-log/member_contributions.md) · [功能映射](../FEATURE_MAP.md)

## 开工审计

工作区为 `D:\TestPilot AI`，开工 HEAD 为 `7c796e73ffdc352641cb5a0dffd6d58fa6d75f43`，另有此前未跟踪的 `reports/model/`。原 F04 使用普通工作台中的执行表单、运行选择器、计数和一段预格式化日志。既有用例覆盖同名运行拒绝、真实失败、F03 首跑、F04 复跑及 F05 缺陷回归。原页面可用 `git show 7c796e7:frontend/templates/runs.html` 与 `git show 7c796e7:frontend/static/runs.js` 比对。[旧验收入口](../../tests/ui_workbench.py#L85) · [F04 接口用例](../../tests/test_f04.py) · [Design System V1](../WP04-F01-001/DESIGN_SYSTEM_V1_IMPLEMENTATION.md)

| 环节 | 当前真实契约 |
| --- | --- |
| 选择版本与套件 | 文件 ID 是不可变修订主键。套件 `file_id` 是生成来源。运行 `file_id` 是实际被测版本。允许同项目、同名文件跨修订执行，文件名同一性以 SQLite NOCASE 为准。[文件模型](../../backend/projects.py) · [套件模型](../../backend/generation.py) · [执行校验](../../backend/runs.py#L30) |
| 提交执行 | `POST /api/suites/{suite}/runs` 请求体只有 `file_id`。Web 层有单进程一个运行槽，无空位时立即返回 HTTP 409。受限执行和落库结束后才返回完整记录。[执行接口](../../backend/runs.py#L30) |
| 运行时 | 受信任的 worker 将固定 Pytest 程序放在离线 WASI 中运行。默认客体截止时间 15 秒，宿主等待上限为 45 秒加客体预算。标准 worker 输出预算 256 KiB。日志保存到 SQLite 的 `result`，内容是 stdout、stderr、宿主诊断的拼接顺序。页面按保存顺序读取，可在文本上定位，跨流的逐事件时序没有单独记录。[执行器](../../backend/runner.py#L126) · [WASI worker](../../backend/wasi_worker.py#L29) |
| 历史与详情 | `GET /api/projects/{project}/runs` 只返回已保存运行的身份、终态、耗时和 `created_at`。结果计数、用例及日志来自 `GET /api/runs/{run}`。页面时间标为 UTC 的保存时间。[响应字段](../../backend/runs.py#L11) |
| 逐用例证据 | 常规 F04 的记录含 `nodeid` 与 `outcome`。名称从 nodeid 提取。Pytest 的异常文本和断言随整次运行日志保存，逐用例耗时、异常类型、文件行号及结构化栈在普通记录中未提供。Inspector 展示可核对字段，并可在原始日志中定位用例名。[客体记录](../../backend/guest_pytest.py) · [结果解析](../../backend/runner.py#L57) |

执行过程是同步 HTTP 响应。页面等待状态跟随实际网络请求，没有 SSE、WebSocket 或实时日志流。日志截断识别来自 runner 追加的终止诊断，指示保存结果不完整。HTTP 409 表示请求遇到并发冲突。已保存运行的 `failed` 表示测试调用失败，`error` 可包含收集、执行环境或输出预算错误，`timeout` 表示截止时间。执行器不可用由明确的环境错误证据识别。

## 布局与交互

| 区域 | 呈现 |
| --- | --- |
| 顶部 | 项目、被测文件、被测修订、套件、来源修订五项并列。运行号与终态独立显示，换版后等待选定记录。 |
| 左栏 | 运行以 ID 倒序提供终态、保存时间、被测版本和用例四项统计。按 ID／文件和持久化状态筛选，每页最多六行。计数按当前页读取，同一运行详情在页内复用。历史和 Inspector 可独立折叠。 |
| 中央 | 选择被测修订、套件来源修订和套件。紫色执行操作提交一次，请求完成后以服务端返回的 ID 打开对应记录。结果区依次显示四个真实计数、服务端耗时、覆盖率和完整用例表。失败及错误排在前面，搜索和分页仍可访问全部记录。 |
| 右栏 | 显示选中用例、nodeid、状态和已记录的证据。可回到本次规范顺序的原始日志。能登记缺陷的失败或错误项携带项目、被测版本、运行与 nodeid 进入现有 F05 表单。 |
| 底部 | 可折叠终端用等宽字体呈现原始日志。搜索按字面高亮并保留完整文本，复制发送服务端原串。空日志与截断各有提示。等待执行时只显示等待说明。 |

桌面三栏共享底部日志区，面板由分隔线组织。普通导航用文件蓝色，操作用紫色，通过、失败和警示分别采用绿色、红色和橙色。900 px 以下顺序阅读，顶部区段链接可跳到历史、执行、结果和日志。[模板](../../frontend/templates/runs.html) · [样式](../../frontend/static/runs.css) · [证据显示](../../frontend/static/run-evidence.js)

切到显式历史记录会读取该运行的真实被测版本与套件，运行和版本身份通过链接在刷新后恢复。只指定套件的入口保留原有参数，并可显示该套件适用的已保存记录。F05 只接收真实失败项的可选 `nodeid`，缺陷创建和回归使用既有接口。[执行控制](../../frontend/static/runs.js) · [F05 节点接收](../../frontend/static/bugs.js)

[浏览器验收](../../reports/WP06-F04-001/F04_BROWSER_ACCEPTANCE.md) · [回归报告](../../reports/WP06-F04-001/F04_REGRESSION_REPORT.md) · [组件复用地图](COMPONENT_REUSE_MAP.md)

实际提交可用 `git log -1 --format="%H %an %s" -- docs/WP06-F04-001/F04_REDESIGN_REPORT.md` 查询。状态为 `READY_FOR_F04_VISUAL_ACCEPTANCE`，等待人工签收。
