# F05 Bug Intelligence Center

工作包 WP07-F05-001，2026-11-27。F05 的功能责任在贡献表中关联 WP04 马雪朋，前端与交互关联 WP02 陈万策。Codex 实际实施、测试、截图和提交，组长陈帅廷协调人工复核。[贡献表](../../collab-log/member_contributions.md) · [功能映射](../FEATURE_MAP.md)

## 实施前审计

工作区为 `D:\TestPilot AI`，开工 HEAD 为 `9fdfa7e6c5266bb55ddfbdd0fdee1427f5232daa`。开工状态中有其他工作的未跟踪目录 `reports/model/`。原 F05 使用通用工作台内的登记表单与回归记录列表。可用 `git show 9fdfa7e:frontend/templates/bugs.html` 与 `git show 9fdfa7e:frontend/static/bugs.js` 查看基线。F04 已从真实失败项把项目、文件、运行和 `nodeid` 传到 F05。[F04 交接](../../frontend/static/run-evidence.js#L157) · [原 F05 接口测试](../../tests/test_f05.py) · [原跨模块浏览器入口](../../tests/ui_workbench.py#L101)

| 能力 | 当前真实接口和字段 |
| --- | --- |
| 缺陷登记与定位 | `GET /api/projects/{project}/bugs` 提供本项目清单，`GET /api/bugs/{bug}` 补充回归历史。 `POST /api/runs/{run}/bugs` 接收标题和真实失败项 nodeid。同一运行及 nodeid 复用已有缺陷。收集阶段若缺可复跑的 `::` 测试项，接口会拒绝登记。 |
| 失败证据 | `GET /api/runs/{run}` 获得项目、被测文件、套件、用例状态和日志；普通运行没有分拆的逐用例断言字段。若日志中有唯一匹配的 Pytest FAILURES 段与同一 nodeid 的终端摘要，页面显示原文片段。其余情况提供完整日志和 F04 链接。 |
| 原始套件 | `GET /api/suites/{suite}` 提供真实 Pytest 原文、目标函数、模式、不可变来源修订和 SHA-256。Drawer 同时标明套件来源，避免与失败运行的被测修订混淆。 |
| 源码版本 | `GET /api/projects/{project}/files` 提供版本列表，`GET /api/files/{file}` 提供对应源码。版本主键即文件 ID。候选使用与 SQLite NOCASE 一致的 ASCII 大小写折叠，必须是同项目同名文件的更高修订。 |
| 执行回归 | `POST /api/bugs/{bug}/regressions` 只传候选 `file_id`。服务端复用原套件，保存真实运行，返回缺陷和回归列表。运行详情仍由原运行端点读取。 |
| 状态与排序 | 登记产生 `open`。服务端判定整套运行 `passed` 且缺陷 nodeid 也 `passed` 后，此次回归为 `resolved`，其他结果保持 `open`。当前缺陷状态由按修订号倒序、同修订内按回归记录 ID 倒序后的第一条决定。 |

[缺陷与回归契约](../../backend/bugs.py) · [运行详情](../../backend/runs.py) · [套件详情](../../backend/generation.py) · [版本模型](../../backend/projects.py)

## 页面与证据

左栏列表可切换项目，按标题、缺陷号、来源运行或 nodeid 查找，并按真实缺陷状态过滤。来自 F04 的深链优先匹配现存缺陷，否则预选对应的失败记录。显式传入的 nodeid 无法匹配时，页面等待用户重新选择。

桌面以原始证据、候选比较和下方回归记录组织中央作业区。右栏固定查阅项目、原始文件／版本、候选版本、套件／来源、原始及选中回归 ID、失败 nodeid。手机用“缺陷列表”“详情”“Diff”三个入口切换，详情后续排列回归与 Inspector。套件 Drawer 和执行确认使用原生模态对话框。

两个版本详情均须通过项目、文件名、ID、修订号和 SHA-256 元数据核对后才显示差异。Diff 按行比对原始文本（包括行尾），桌面并排对齐，窄屏为双行号统一 Diff。蓝色加号与琥珀减号标识源码变化。绿、红分别用于真实通过／解决和失败。每页最多渲染 72 组行，保留完整上下文。精确对齐的矩阵限制为 150 万格，超限时显示无法精确配对部分的两侧原文，并提示原因。

候选选中和 Diff 读取期间，缺陷状态取自已保存业务记录。明确确认后才提交回归。处理中等待实际响应，成功后以返回的缺陷和回归列表更新。查询中保留项目、原始运行、nodeid、当前候选及选中回归；刷新可恢复。历史链接可从 F05 回到原始失败或任一回归运行。

[页面模板](../../frontend/templates/bugs.html) · [控制器](../../frontend/static/bugs.js) · [Diff 与断言提取](../../frontend/static/bug-evidence.js) · [复用地图](COMPONENT_REUSE_MAP.md)

[Edge 实拍与验收](../../reports/WP07-F05-001/F05_BROWSER_ACCEPTANCE.md) · [回归结果](../../reports/WP07-F05-001/F05_REGRESSION_REPORT.md)

可用 `git log -1 --format="%H %an %s" -- docs/WP07-F05-001/F05_REDESIGN_REPORT.md` 定位独立提交。工作包状态为 `READY_FOR_F05_VISUAL_ACCEPTANCE`，等待人工验收。
