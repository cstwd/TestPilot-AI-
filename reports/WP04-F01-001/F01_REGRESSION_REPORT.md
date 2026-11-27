# F01 回归与 F02 公共样式对照

**WP04-F01-001** · 2026-11-27。由 Codex 在 Windows 的项目虚拟环境执行。浏览器由 Playwright 启动本机 Edge；每个业务用例通过 `main.py --no-browser --port <临时端口>` 使用真实 FastAPI 与独立临时 SQLite。截图与修订证据另见 [F01 浏览器验收](F01_BROWSER_ACCEPTANCE.md)。

## 冻结版本和当前 F02 的并排测量

同一台机器、同一浏览器下，分别启动从 `765e95a` 导出的临时基线及当前工作区。向临时项目导入仓库的 `telemetry.py`，在 F02 选中文件根节点，使用 DPR 1 和减少动态模式，等待 COMPLETE，然后依次测量两种视口。读 `getBoundingClientRect()`、计算背景色，并对浏览器导出的画布 PNG 字节做 SHA-256。每个样本均是 16 个节点、15 条包含边。[输入样例](../../eval/ast_visual/telemetry.py) · [应用夹具](../../tests/test_dashboard.py#L20)

| F02 测量项 | 1440 × 900，提取前 / 后 | 390 × 844，提取前 / 后 |
| --- | --- | --- |
| 顶栏高度 | 61 / 61 px | 94 / 94 px |
| 模块轨宽度 | 54 / 54 px | 收起 / 收起 |
| 画布宽 × 高 | 835.61 × 589.45 / 835.61 × 589.45 px | 390 × 470.92 / 390 × 470.92 px |
| 顶栏、图谱面板背景 | 两次均为 `#11121c`、`#0d101b` | 同左 |
| 画布 PNG SHA-256 | 两次均为 `161cdb8a8224559a228db4c9f44aecb734b056bec72ddfaed3ca053f35a92e4a` | 两次均为 `d1aad3387750ee9161fd9509541f8125ee228cf0dbae64319176accf9f5b9d64` |

这个指纹覆盖图谱画布本身。页面字体栈按新系统设置，顶栏与各面板额外测量几何尺寸，交互和动画由以下真实浏览器用例另行验证。开工版的 5 项既有 F01 接口用例、1 项既有 F01 浏览器用例和画布采样合计 **7 passed in 68.90s**。加入手机启动恢复后的定稿再次独立采样为 **1 passed in 35.08s**，表中两组尺寸与摘要一致。

## 原有 F02 与跨模块主线

以下命令在仓库根目录运行，均退出 0。图谱、分析、执行环境均沿用原有业务路径。

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_f02.py tests/ui_workbench.py::test_f02 tests/ui_workbench.py::test_f03 tests/test_ast_refinement.py tests/test_ast_studio.py::test_revision_and_boundary_inputs tests/test_ast_studio.py::test_unavailable_context_and_retry tests/test_ast_studio.py::test_large_real_analysis
.\.venv\Scripts\python.exe -m pytest -q tests/test_ast_studio.py::test_file_to_generation tests/test_ast_studio.py::test_dense_renderer_and_pointer_gestures tests/test_ast_canvas_refinement.py
```

| 批次 | 结果 | 复核范围 |
| --- | --- | --- |
| 第一条命令 | **11 passed in 305.28s** | 同名/嵌套定义、语法错误、空文件、无效链接、失败重试、控制台、镜头暂停及 1000 个真实节点；既有 F03 生成、首次 Pytest 与运行记录跳转。 |
| 第二条命令 | **4 passed in 154.84s** | 从新版 F01 导入文件，经 F02 选择后进入 F03；六种视口、实时缩放、标签避让、稠密布局、指针手势及独立 2000 边绘制用例。 |

可用 `git diff 765e95a -- backend/projects.py backend/analysis.py frontend/static/analysis.js frontend/static/ast-model.js frontend/static/ast-canvas.js frontend/static/ast-animation.js` 核对契约与图谱核心。这些路径在本工作包没有差异。F02 的 Jinja、样式和 Inspector 对共享源码显示函数的导入属于呈现层。[公共系统实现说明](../../docs/WP04-F01-001/DESIGN_SYSTEM_V1_IMPLEMENTATION.md) · [复用地图](../../docs/WP04-F01-001/COMPONENT_REUSE_MAP.md)

## F01 源码与文件名边界

定稿后的 F01 回归共 **11 passed in 208.85s**，包括 5 项既有接口测试、1 项既有窄屏测试、3 项浏览器验收，以及源码边界和手机启动恢复各 1 项。结合上表的 15 项，共 26 项不同的业务与呈现回归通过。桌面、平板、手机实拍及版本 ID、SHA-256 见[浏览器验收记录](F01_BROWSER_ACCEPTANCE.md)。

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_project_startup.py tests/test_project_workspace.py tests/test_project_source_preview.py tests/ui_workbench.py::test_f01 tests/test_f01.py --tb=short
```

启动恢复测试在 390 × 844 视口中分别向项目列表和当前项目版本列表注入一次 HTTP 503。首次失败后可以切换面板和重新读取。版本列表失败后，Explorer 仍显示已读取的项目，顶栏切换到可用项目后可预览源码，并核对 F02 链接对应的项目及版本 ID。[手机启动恢复用例](../../tests/test_project_startup.py)

独立用例在页面上传带 UTF-8 BOM 的 `Probe.py`，正文包含中文、102 行、CRLF，最后一行没有换行。服务收到的正文按原浏览器契约已解码并去除 BOM。检查 Inspector 的源码字节数、SHA-256，以及所有行在两页间的顺序、着色与换行。第二页点“复制源码”，检查系统剪贴板包含第一页到最后一行。比较系统回读时允许 Windows 剪贴板的换行约定。先以 `probe.py` 导入修改内容，再用 `PROBE.py` 导入初版，页面实测只有一个文件组，包含 v1、v2、v3；v1、v3 摘要一致且记录 ID 不同。

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_project_source_preview.py --tb=short
```

结果为 **1 passed in 35.02s**。初次编写验收时曾把创建项目的 201 误用到文件导入，并试图在成功导航后读取上个页面的 POST 响应正文。最终断言依据文件 POST 的真实 200、当前页面选中的 ID 和重新读取的不可变记录。服务端契约与浏览器导航行为均保持原样。[源码边界用例](../../tests/test_project_source_preview.py)
