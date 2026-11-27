# F02 有头浏览器动画验收

**WP03-AST-VISUAL-REFINE-001 · 2026-11-27**。操作者 Codex，项目组人工签收待办。录制从 F01 导入不可变 Python 文件开始，经 F02 结构动画、节点选择和重播，结束于 F03 选定目标函数。[播放连续实录（MP4）](video/analysis-session.mp4)

## 录制环境与输入

使用 Windows 11、项目虚拟环境的 Playwright 1.65.2 和本机 Microsoft Edge 158.0.4370.33。浏览器以 `headless=False` 启动，脚本读取浏览器实际启动参数，验证未启用 headless。录制窗口内容区为 1440 × 900、DPR 1，系统动效偏好为正常。项目由根目录 `main.py --no-browser --port <空闲端口>` 启动，操作经过真实同源页面和端点，每次录制使用独立临时 SQLite 库。源码只经静态解析。[录制脚本](../../tests/capture_ast_refinement.py) · [服务夹具](../../tests/test_dashboard.py) · [导入样例](../../eval/ast_visual/telemetry.py)

通过 F01 的文件选择器上传 `telemetry.py`。全链路核对项目 ID 1、不可变文件 ID 1、修订 v1 与 SHA-256 `84c097052cfbecef569b405c96b34f477373d3c7ce4037a245fb9934fc675490`。真实分析接口返回 15 个定义，工作台展示文件根与 15 个定义、15 条包含边。

为拍清请求等待状态，本次录制通过 Edge DevTools 网络规则仅对 `/api/files/*/analysis` 配置 1600 ms 传输延迟。应用实际发出 GET 并处理服务端原始 JSON。该轮控制台读数为“分析请求（浏览器端） 1619 ms”。独立新开的窄屏页面未应用延迟规则，其读数为 7 ms。两个数值都包含客户端等待。性能回归另在关闭该规则的环境中采样。[性能复验](PERFORMANCE_REGRESSION.md)

## 现场操作与证据

| 画面 | 核对内容 |
| --- | --- |
| [请求等待](screenshots/01-request.png) | 项目、文件版本已确定，控制台为 SCANNING，顶栏显示“分析请求中”。 |
| [节点渐现](screenshots/02-nodes.png) | PARSING 阶段，文件根先出现，随后在最终布局位置逐批显现定义。 |
| [包含边绘制](screenshots/03-edges.png) | STRUCTURE BUILDING 阶段，父定义向子定义的曲线处在不同绘制位置。 |
| [类及邻域](screenshots/04-neighborhood.png) | 从树选择 Sample，再双击画布中该类，选中节点 ID 为 `symbol:1:3:Sample`。Inspector 显示同一类。 |
| [源码定位](screenshots/05-source.png) | 由 Structure 进入 Sample.normalized 并切换 Source。行 10 是方法定义，行 10–11 随所选方法高亮。 |
| [暂停](screenshots/06-paused.png) | 从放大的局部视野重播，在包含边绘制期间点击暂停。等待 850 ms 并逐字节比较 Canvas 图像，像素保持一致。 |
| [继续至完成](screenshots/07-replay-complete.png) | 点击继续后阶段到达 COMPLETE，保留原节点选择和请求时长；本次重播未产生第二个分析 GET。 |
| [控制台折叠](screenshots/08-console-folded.png) | 点击标题折叠，阶段仍可读；再次展开，统计和计时可见。 |
| [390 × 844](screenshots/09-mobile.png) | 单独打开同一深链，恢复 mean_value；画布可见，页面总宽度等于窗口宽度。此帧由独立窄屏页面采集。 |

视频末段搜索并选择 `mean_value`，刷新后从本机分析快照恢复同一节点，随后进入 F03。实际路由参数为 `project=1&file=1&symbol=mean_value`，目标函数选择框值为 `mean_value`。录制断言覆盖 F02 页面未处理脚本异常。

## 视频校验与时间索引

最终有头验收退出码 0，结果为 **1 passed in 60.87s**，包含打开浏览器、业务操作、窄屏复查和视频封装。MP4 时长 **23.28 秒**，1440 × 900，H.264，25 fps，无音轨，1,781,169 字节。已用 FFmpeg 解码全部 582 帧，并将 8 张桌面 PNG 与缩小至同一分辨率的解码帧逐帧比较。以下为视频中画面最接近相应截图的播放位置，可直接拖动复核。

| 请求等待 | 节点渐现 | 包含边生长 | 类的邻域 | 源码定位 | 暂停 | 重播完成 | 控制台折叠 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 03.64 s | 04.80 s | 06.04 s | 09.12 s | 10.68 s | 14.20 s | 15.76 s | 16.16 s |

重播前读数为 **263%**，完成后为 **100%**。Source 帧可见 `Sample.normalized` 和直接父级之间的高亮边，先前局部视野中悬空的文件标签已消失。视频 SHA-256 为 `7ea8fa34f8aa87ecb352c57370bcbdeb8461cec3c0c75eecabbe1270cae2b0e0`。

实录先让用户读完 Source，再重播。最终代码还补验了两个不同的操作节奏：刚选中就立即重播并暂停时清除旧选择外环的剩余动画，以及大图搜索跨页时把选中行滚入符号树可见区。这两种边界情况分别由[画布像素断言](../../tests/test_ast_canvas_refinement.py)和[大图跨页复验](PERFORMANCE_REGRESSION.md)留证。

## 复现

在仓库根目录 PowerShell 执行以下两行。选择新的输出目录以保留本次归档。录制脚本通过 Playwright 获取浏览器连续画面，最终使用本机 FFmpeg 将原始 WebM 转码为 H.264 MP4，保留原始播放速度与完整镜头顺序。附带 PNG 在对应阶段直接截自页面。

```powershell
$env:TESTPILOT_AST_REFINE_CAPTURE_DIR = Join-Path $env:TEMP ('F02-headed-' + [guid]::NewGuid().ToString('N'))
.\.venv\Scripts\python.exe -m pytest tests/capture_ast_refinement.py -q -s --tb=short
```
