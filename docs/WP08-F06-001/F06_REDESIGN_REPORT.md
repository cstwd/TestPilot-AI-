# F06 Quality Intelligence Center

工作包 WP08-F06-001，2026-11-27。F06 功能在原映射关联 WP03、WP04、WP05，产品前端关联 WP02。实际实施、测试、截图及提交由 Codex 执行，陈帅廷协调人工验收。[职责一览](../../collab-log/member_contributions.md) · [功能映射](../FEATURE_MAP.md)

## 开工审计

工作区为 `D:\TestPilot AI`，开工 HEAD 为 `1acd2ff78e8fa42f11a53817ae3f4b1a15e70f77`。开工时存在其他工作留下的未跟踪目录 `reports/model/`。原报告页使用通用工作台中的运行下拉框、统计列表和 JSON 下载链接。用 `git show 1acd2ff:frontend/templates/reports.html` 和 `git show 1acd2ff:frontend/static/reports.js` 可核对原页面。[原 F06 服务与度量用例](../../tests/test_f06.py) · [既有浏览器用例](../../tests/ui_workbench.py#L126)

| 证据来源 | 当前接口与真实字段 |
| --- | --- |
| 运行筛选 | `GET /api/projects/{project}/runs` 给出运行 ID、项目、被测文件、套件、终态、耗时和真实落库时间。文件版本清单给出文件 ID、文件名、修订号、SHA-256。 |
| 质量报告 | `GET /api/runs/{run}/report` 返回 `testpilot.quality.v1`。一次 SQLite 读事务绑定项目、运行、被测版本、套件、质量指标、状态说明、环境、用例、原始日志、关联缺陷。 |
| 行覆盖率 | 原 WASI Pytest 客体采集 `subject.py` 的覆盖行和可执行行。执行器把比例、分子、分母写入运行，质量报告沿用已保存值。 |
| 缺陷与回归 | 报告关联原始失败运行或该次缺陷回归运行。每个缺陷含读取时的状态、原始运行及其保存的回归列表。单次回归列表包含运行 ID、文件 ID、修订和回归判定。 |
| JSON | `GET /api/runs/{run}/report/export` 保留原路由、文件名和附件响应，请求时生成当时的报告快照。 |

[质量计算及导出](../../backend/quality.py) · [运行模型](../../backend/runs.py) · [覆盖率采集](../../backend/guest_pytest.py#L91) · [回归模型](../../backend/bugs.py)

## 工作台与报告

- **运行 Explorer** 以当前项目持久化历史为索引，支持文件版本和运行状态过滤。筛选改变列表，打开运行后才替换全部证据。每页最多八条，深链接直接显示所选运行所在页。显式无效或异项目的运行号进入空错误态。
- **执行上下文** 显示项目、文件名、修订、运行 ID、终态、套件和真实 UTC 运行记录时间。来源校验同时对比项目、运行、状态、被测版本、源码 SHA-256 与套件 ID。
- **指标与可视化** 用四张关键指标卡和两张分布图展示本次运行。测试通过率和覆盖率均带分母，四类用例图包含跳过。没有分母或没有采集记录时保留文本状态。指标口径 Drawer 提供每项定义。
- **多次运行比较** 只提供同项目、同名文件、同套件的已保存运行。用户显式选择对照后，读取第二份真实报告。比较表每一列保留自己的版本、结果和分母，当前报告、Inspector 和导出范围由原选中运行决定。
- **Evidence Inspector** 对照项目、运行、被测版本、套件与来源摘要。关联缺陷可跳转 F05，原始运行和回归记录可跳转 F04。回归列表的状态明确标为服务端判定。
- **HTML 与导出** HTML 视图复用现有报告 DOM 和内存快照。相同快照生成 JSON 下载，文件名保持 `testpilot-run-{id}.json`。这使浏览器页面与下载在后台状态改变时仍一致。浏览器刷新后重新读取服务端状态。HTML 深链接可恢复，浏览器打印样式保留证据并折去筛选和对比操作。

桌面为 Explorer、指标与证据三栏。平板和手机顺序阅读，手机图表纵向排列。保留 Jinja、CSS 与原生 JavaScript，标注使用浏览器本地字体回退和公共令牌。

[模板](../../frontend/templates/reports.html) · [交互](../../frontend/static/reports.js) · [指标呈现](../../frontend/static/report-metrics.js) · [样式](../../frontend/static/reports.css) · [指标定义](QUALITY_METRIC_DEFINITIONS.md) · [复用地图](COMPONENT_REUSE_MAP.md)

[Edge 实拍验收](../../reports/WP08-F06-001/F06_BROWSER_ACCEPTANCE.md) · [回归结果](../../reports/WP08-F06-001/F06_REGRESSION_REPORT.md)

实际 Git 提交从 `git log -1 --format="%H %an %s" -- docs/WP08-F06-001/F06_REDESIGN_REPORT.md` 查询。状态为 `READY_FOR_F06_VISUAL_ACCEPTANCE`，待人工签收。
