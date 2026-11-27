# F01 项目中心浏览器验收

**WP04-F01-001 · 2026-11-27**。Codex 实际执行，人工复核待项目组签收。在 Windows 的 Microsoft Edge 158.0.4370.33 中，从真实 F01 页面创建项目、选择本地文件、提交三次导入，再分别读取两条不可变记录。服务通过根目录 `main.py --no-browser --port <临时端口>` 启动，每个用例独立使用临时 SQLite。浏览器截图来自这些实测窗口。[入口与临时库夹具](../../tests/test_dashboard.py) · [完整测试](../../tests/test_project_workspace.py)

## 导入与版本身份

测试通过真实项目接口创建“边界样例”“排序回归”，以便核查 Explorer 搜索。随后在 F01 表单中创建 `Telemetry Lab`，响应 HTTP 201，项目 ID 为 **3**。文件导入均通过文件选择器和“导入文件”按钮提交，接口三次返回 HTTP 200。每次导航后，测试用浏览器当前选择器的记录 ID 重新 GET 文件，对照原文、UTF-8 字节数及独立计算的 SHA-256。[真实输入 telemetry.py](../../eval/ast_visual/telemetry.py) · [服务端导入逻辑](../../backend/projects.py#L58)

| 导入内容 | 文件 ID / 不可变版本 ID | 修订 | UTF-8 字节数 | Inspector 与本地计算一致的 SHA-256 |
| --- | --- | --- | ---: | --- |
| telemetry.py 原文 | 1 / 1 | v1 | 1268 | `84c097052cfbecef569b405c96b34f477373d3c7ce4037a245fb9934fc675490` |
| 原文再导入 | 1 / 1 | v1 | 1268 | 同上 |
| 原文末尾增加带中文文档字符串的函数 `pipeline_ready` | 2 / 2 | v2 | 1351 | `c9226a6602e75159bfafe97149a755b5d276f2e05e1bf0e53b97fc4aa3795135` |

三次提交后，当前项目的文件列表中只有 ID 2、1 两条记录。两行属于同一个文件名分组。在同一项目另导入 `magnitude.py` 后，页面展示 2 个文件、3 个版本。项目和文件名搜索均能缩小列表并恢复，展开、折叠 telemetry 版本组后仍可点击 v1。Inspector 的项目名、文件名、两种 ID、修订号、大小和完整摘要均与接口相符。[桌面版本工作区](screenshots/desktop-versions.png)

两版源码均通过只读预览与原文进行逐字符比对。复制 v1 时，测试观测 `navigator.clipboard.writeText` 的参数并调用原生方法，传入的全文与源文件完全一致。Windows 系统剪贴板回读将行尾转换为 CRLF，按平台换行规范化后包含所有字符和尾换行。将含字面 HTML 标签的 Python 字符串显示在 Inspector 中，测试验证页面中不存在对应的 HTML 元素。

## 从同一文件名进入不同分析结果

| F01 选中项 | 刷新后点击的 F02 路由 | 真实图谱 | 函数核对 |
| --- | --- | --- | --- |
| telemetry.py · v1 | `/workbench/analysis?project=3&file=1` | 16 个节点，15 条包含边 | 没有 `pipeline_ready` |
| telemetry.py · v2 | `/workbench/analysis?project=3&file=2` | 17 个节点，16 条包含边 | 选中新增的 `pipeline_ready`，F03 的 URL 为 `project=3&file=2&symbol=pipeline_ready`，目标控件值一致 |

每个 F02 节点的 `file_id`、`version_id` 都等于所选文件记录 ID，`revision` 分别为 1、2。测试还核对了 F02 画布实际显示的两个计数。项目接口未提供文件创建时间，Inspector 所列元数据以查询响应和 UTF-8 文本为依据。[图数据适配器](../../frontend/static/ast-model.js) · [文件列表与详情契约](../../backend/projects.py)

## 选择、布局与失败状态

| 实测路径 | 结果 |
| --- | --- |
| 初次进入无项目的临时库 | 创建入口可用，导入不可用，详情显示待选择。选择已有但尚无文件的项目后可导入。通过 Explorer 在空项目与含文件项目间切换，项目 ID 和可见内容同步。[空库](screenshots/empty.png) |
| 中文长文件名 | 文件名含 53 个字符（含扩展名）。列表省略处可从 Inspector 读到完整名称，64 个十六进制摘要字符可在窄屏换行。测试将 `<b>湿度</b>` 当作 Python 字符串核对。[手机文件](screenshots/mobile-files.png) · [手机详情](screenshots/mobile-details.png) |
| 文件录入错误 | 依次提交 .txt、无效 UTF-8、131073 字节文本及含 NUL 文本，界面显示相应错误。真实项目文件列表仍为空，分析入口隐藏。 |
| 跨项目版本号与不存在的项目 | 先给当前项目导入合法 own.py，再拼接另一项目的文件 ID，另测不存在的项目 ID。两种情况下均提示失效，源码预览区隐藏，分析链接无 href。 |
| 服务错误与恢复 | 仅在浏览器侧对一个详情 GET 注入一次带明示详情的 HTTP 503。错误时详情与分析按钮隐藏。点击“重新读取”后由真实服务返回正确源码、摘要和不可变 ID。[503 错误态](screenshots/network-error.png) |
| 手机初次读取失败 | 项目列表请求返回一次 503 时，文件版本和详情面板仍可切换并显示错误，“重新读取”可恢复。单个项目的版本清单返回一次 503 时，Explorer 仍保留已读取的项目，顶栏可切换到另一个可用项目。[启动恢复用例](../../tests/test_project_startup.py) |

| 窗口（CSS px） | 实测摘要宽度（CSS px） | 布局验收 |
| --- | ---: | --- |
| 1440 × 900 | 409 | 桌面三栏并排。[版本展开与源码](screenshots/desktop-versions.png) |
| 1024 × 768 | 275 | 三栏压缩；完整摘要仍可读。 |
| 768 × 1024 | 688 | 切换项目、文件版本、详情后各面板可用。[平板详情](screenshots/tablet-inspector.png) |
| 390 × 844 | 354 | 三个面板均验证，页面总宽为 390 px。v2 的 57 行源码可独立滚动，详情首屏直接显示分析按钮，测试检查按钮上下边界。[项目](screenshots/mobile-projects.png) · [两次修订](screenshots/mobile-telemetry-versions.png) · [源码与分析入口](screenshots/mobile-telemetry-source.png) |

## 复验命令与结果

从开工 Git 快照 `765e95a` 将入口、前后端和相关测试只读导出到临时目录，使用相同解释器运行原有 `tests/test_f01.py` 与 `tests/ui_workbench.py::test_f01`，**6 passed in 35.03s**。在真实工作区运行以下命令并记录截图，得到 **9 passed in 141.89s**，退出码 0，涵盖 3 项新增 Edge 场景、1 项原始窄屏浏览器场景和 5 项项目版本及文件校验用例。补充启动恢复后的最终测试命令及结果见[全包回归记录](F01_REGRESSION_REPORT.md)。

```powershell
$env:TESTPILOT_F01_CAPTURE_DIR = Join-Path $env:TEMP ('F01-review-' + [guid]::NewGuid().ToString('N'))
.\.venv\Scripts\python.exe -m pytest tests/test_project_workspace.py tests/ui_workbench.py::test_f01 tests/test_f01.py -q -s -r f --tb=short
```

截图环境变量可省略；测试仍使用临时库完成全部操作。上述窗口使用 Edge 无头浏览器，桌面显示器、物理手机与其他浏览器的人工观感留待签收。[全包回归记录](F01_REGRESSION_REPORT.md)
