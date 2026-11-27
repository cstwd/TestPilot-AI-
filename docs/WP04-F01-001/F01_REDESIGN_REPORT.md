# F01 项目中心视觉重构

**工作包 WP04-F01-001** · 2026-11-27。实际工作目录 `D:\TestPilot AI`。登记负责人马雪朋（WP04），前端职责关联 WP02；实施、截图、测试、提交的实际操作者为 Codex，人工验收待组长陈帅廷协调。[职责记录](../../collab-log/member_contributions.md)

## 实施前审计

| 核对项 | 实际依据与本次决定 |
| --- | --- |
| Git 与并行工作 | 开工 HEAD 为 `765e95acc3cbc88ee7f914495ce988f0ad99a991`。当时 README、Phase 04 验收文档和测试记录已有未提交内容，另有 `reports/model/`。实施中 Phase 04 独立提交至 `307d4bd`。本工作包以路径限定提交。 |
| F02 视觉基线 | F02 的图谱精修实现为 `76bd9e0`。原 `analysis.html` 内联了 SVG 符号、顶部选择器和模块导航；`analysis.css` 同时包含颜色变量、通用控件和图谱专用规则。Python 上色原在 `ast-inspector.js` 内。公共层按这些实际边界提取。[基线精修](../../reports/WP03-AST-VISUAL-REFINE-001/VISUAL_REFINEMENT_REPORT.md) · [公共组件映射](COMPONENT_REUSE_MAP.md) |
| 原 F01 路径 | `/workbench/projects` 由共用 Jinja 模板包含约十行的表单与预览片段。`workbench.js` 负责初始化两个选择器、上传、创建项目与源码回显。老版本选中态同时依赖 URL 和 select。两份原件可用 `git show 765e95a:frontend/templates/projects.html` 与 `git show 765e95a:frontend/static/workbench.js` 查证。[入口分派](../../frontend/templates/workbench.html) · [启动代码](../../frontend/static/workbench.js) |
| 不可变身份 | `projects.id` 表示项目。`files.id` 是一条不可变文件修订的主键，同一行的文件 ID 与版本记录 ID 相同。`revision` 是同一项目、同一文件名的修订序号。文件名列使用 SQLite NOCASE（ASCII 大小写），跨项目的同名文件独立。[表定义及返回字段](../../backend/projects.py#L14) |
| 旧用例 | F01 接口已有并发同内容导入、版本保留、项目隔离、非法路径及设备名测试。375 × 812 的浏览器用例连续导入两版、选择旧版并在刷新后核对 F02 链接。实施前在冻结提交的临时副本上实际运行这 6 项与 1 项 F02 画布采样，合计 7 项通过。[F01 后端用例](../../tests/test_f01.py) · [原浏览器路径](../../tests/ui_workbench.py#L26) |

## 用户如何识别同一个文件的不同版本

F01 解决的是“哪个项目下的哪一版源码将进入分析”。项目选择决定文件清单的范围，文件名组织版本记录，右侧用修订号、记录 ID、完整摘要与源码共同标识选中版本。进入 F02 的链接形如 `/workbench/analysis?project=P&file=R`，其中 R 始终是所选修订的记录 ID。明确指定的项目或版本不存在时，不能用列表第一行替代它。[入口上下文](../../frontend/static/workbench.js) · [文件及修订 API](../../backend/projects.py)

| 接口 | 业务契约 |
| --- | --- |
| `GET /api/projects`、`POST /api/projects` | 列表与创建结果包含 `id,name`。提交体为 `{name}`；名称最长 100，空白、控制字符和重复名称沿用原服务校验。 |
| `GET /api/projects/{P}/files` | 每行包含 `id,project_id,filename,revision,sha256`，按行 ID 降序。不含源码、时间、字节数或额外的文件族 ID。 |
| `POST /api/projects/{P}/files` | 提交 `{filename,source}`。仅最新一版摘要相同时复用最新记录，否则在写事务中分配下一修订。导入与复用均返回 HTTP 200，另一个创建项目端点返回 201。若 v1→v2 后重新导入 v1 的内容，契约会创建 v3。 |
| `GET /api/files/{R}` | 读取该记录的元数据与 `source`。摘要由服务端对源码的 UTF-8 字节计算，页面据已存源码计算 UTF-8 字节数。服务没有创建时间字段，因此详情仅提供有来源的元数据。 |

保留既有单个 Python 文本导入流程。浏览器检查本地文件字节上限并以严格 UTF-8 解码；服务继续校验文件名、扩展名、保留名、字符数、128 KiB 上限和 NUL。复制与预览使用服务返回的文本，语法颜色只用于阅读。[导入校验](../../backend/projects.py#L59) · [写事务](../../backend/store.py#L8)

## 三栏怎样配合

| 区域 | 正常操作 | 边界与反馈 |
| --- | --- | --- |
| 顶栏、模块轨和页头 | 顶栏选择当前项目或不可变修订；页头先选择本地文件，再点“导入文件”。链接保留当前可用的 project/file。 | 没有项目时禁用导入。手机顶栏的工作台菜单提供同一组六个模块入口，可用键盘开合。 |
| 左侧项目 Explorer | 搜索项目名称，从列表选中项目，或在固定的创建表单中输入名称。 | 当前项目使用与 F02 树行一致的底色、边框和可读选中标记。搜索无匹配和库中尚无项目分别给出说明。 |
| 中央文件与版本 | 工作区显示项目 ID、文件组与修订的实数。文件名可搜索；点击文件名选择其最新版，展开文件组可逐条选择历史版本。 | “最新”跟随该组的最大修订；紫色选中标记跟随当前查看的记录，两者可以落在不同行。版本行同时显示短摘要和记录号。 |
| 右侧 Inspector | 对照项目、文件名、行记录 ID、vN、UTF-8 字节数及完整 SHA-256。以每页 100 行查看只读源码，可翻页、复制完整源码或进入 F02。 | 同名历史行仍使用各自的源码和摘要。长文件名及 64 位摘要可换行。读取文件详情时复核其项目、文件 ID、文件名、修订与摘要，验证通过后才显示分析入口。 |
| 反馈区 | 项目载入、创建、导入、复用、复制均有文字反馈。真实失败提供错误信息；读取失败可重新读取。 | 上传反馈仅在匹配返回记录的导航中消费。源码和项目名通过文本节点写入界面，代码中的 HTML 外观字符按文本显示。 |

桌面以三栏并列读同一版本。≤900 px 改为“项目 → 文件版本 → 详情”面板切换。空库先给创建项目入口；新建项目后进入文件面板，经明确版本链接或导入成功后进入详情。所有页面由同一个 FastAPI 服务同源提供静态文件。字体使用本地 Inter 与中文回退、JetBrains Mono 与 Consolas 回退。[F01 模板](../../frontend/templates/projects.html) · [面板样式](../../frontend/static/projects.css) · [控制器](../../frontend/static/projects.js) · [公共设计规范](DESIGN_SYSTEM_V1_IMPLEMENTATION.md)

“分析此版本”固定在 Inspector 底部。390 × 844 实测时，按钮覆盖纵向 759.5–799 px，状态栏从 809 px 开始；将详情和源码分别滚到末尾后仍可直接进入所选版本的 F02。[手机实拍](../../reports/WP04-F01-001/screenshots/mobile-telemetry-source.png)

## 人工验收入口

1. 在 PyCharm Run 根目录 `main.py`，从首页进入“项目与文件”。新建项目后，连续两次导入同一份 [telemetry.py](../../eval/ast_visual/telemetry.py)。检查两次读到同一个不可变 ID，文件组中只有 v1。
2. 修改同名文件的函数定义并导入。分别选择 v1 和 v2，对照源码与 SHA-256，再点“分析此版本”。检查 F02 的文件名、vN 和 URL 中的项目、文件记录 ID。浏览器返回后可继续查看另一版。
3. 在窄屏进入“详情”复制源码，检查长中文文件名和全部 64 位摘要。应用访问失败时，可在恢复服务后点“重新读取”。[实测截图、身份核对与验收命令](../../reports/WP04-F01-001/F01_BROWSER_ACCEPTANCE.md) · [既有功能与图谱回归](../../reports/WP04-F01-001/F01_REGRESSION_REPORT.md)

交付提交可用 `git log -1 --format="%h %an %s" -- docs/WP04-F01-001/F01_REDESIGN_REPORT.md` 在本地定位。阶段状态为 `READY_FOR_F01_VISUAL_ACCEPTANCE`，等待人工签收。
