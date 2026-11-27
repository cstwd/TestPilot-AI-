# F02 图谱精修性能与业务回归

**WP03-AST-VISUAL-REFINE-001 · 2026-11-27**

基线代码 `7f724d0`、证据 `c9737be`。实际操作者 Codex。测量在 Windows 11 本机进行，Playwright 驱动 Edge 158.0.4370.33，每项测试均通过根目录 `main.py` 启动 FastAPI，使用临时端口和独立 SQLite。浏览器性能测试使用无头模式，有头录屏单独留存。[原始基线](../WP03-AST-VISUAL-001/PERFORMANCE.md) · [相同的压力用例](../../tests/test_ast_studio.py) · [本轮补充断言](../../tests/test_ast_refinement.py)

## 业务回归

| 用户路径 | 本次观测 |
| --- | --- |
| F01 导入 → F02 → F03 | 通过文件选择器导入 telemetry.py，项目 1、文件版本记录 1、修订 v1，SHA-256 为 `84c097052cfbecef569b405c96b34f477373d3c7ce4037a245fb9934fc675490`。15 个定义和文件根组成 16 个节点、15 条包含边。搜索选中 `mean_value` 后刷新，恢复相同节点并通过 `project=1&file=1&symbol=mean_value` 进入 F03，目标控件值为 `mean_value`。 |
| 原窄屏 F02 / F03 路径 | 在 375 × 812 验证带类型的函数签名、行范围、切换语法错误版本。独立生成用例选中 `magnitude`、生成并验证、复查首次 Pytest 通过，刷新后进入真实运行记录。 |
| 版本与失败 | 同名文件的修订 v1/v2 分别对应文件版本记录 1、2。两个同名类的方法分别连到第 1、3 行的真实父定义。空文件有 1 个根与 0 条边，语法错误能定位到第 1 行。跨项目组合、过期项目号无可生成目标；全量筛选后可通过搜索恢复节点。 |
| 控制台与计时 | 在 390 × 844 收起控制台，正文隐藏，阶段始终可读，画布高度增加；用 Enter 重新展开并核对选中项。真实分析接口的 JSON 在浏览器端加入 220 ms 的测试延迟，界面计时为 230 ms。刷新从快照恢复，重播保持原文，两者均没有再次发送分析请求。模拟一次 HTTP 503 后计时为空，用户重试后真实服务恢复。这项延迟注入只用于证明计时区间。[计时断言](../../tests/test_ast_refinement.py) |
| 重播镜头的暂停 | 放大至 195% 后点重播，在镜头首次可观测的缩放变化（194%）暂停 650 ms；画布维持 194%。继续至 COMPLETE 恢复 100% 且选中同一节点。 |
| 大图跨页聚焦 | 搜索最后一个类的 `Channel26.signal35`。Inspector 定位到 channels.py 的第 999 行，左侧符号树自动翻页并滚动。补测选中行上、下边缘均落在滚动视口内。[1000 节点全图](screenshots/large-real-layout.png) · [最后一个方法](screenshots/large-real-focus.png) |

当前适配器将 `file_id` 和 `version_id` 指向同一条不可变文件记录；`revision` 表示该文件名的修订序号。F03 路由沿用 `file` 传递版本记录主键，上表核对的 `v1` 和 `id=1` 各有独立含义。[适配器模型](../../frontend/static/ast-model.js#L30) · [文件修订写入](../../backend/projects.py)

| 视口 | 精修后展开控制台时的画布（CSS px） | 页面宽度 |
| --- | --- | --- |
| 1920 × 1080 | 1236 × 762 | 1920 |
| 1440 × 900 | 836 × 589 | 1440 |
| 1280 × 800 | 686 × 493 | 1280 |
| 1024 × 768 | 750 × 461 | 1024 |
| 768 × 1024 | 724 × 688 | 768 |
| 390 × 844 | 390 × 471 | 390 |

## 计时口径

分析请求的浏览器 Resource Timing 值测量完整 HTTP 传输。页面控制台另使用 `performance.now()` 包围 `await api(.../analysis)`，包含响应体读取、JSON 解码与浏览器调度。以下压力样本均关闭测试附加延迟。正常动画的帧间隔由业务画布每次 `clearRect` 时刻的差值计算；缩放延迟取交替缩放指令后下一次帧回调。首次构造耗时是创建布局与渲染器句柄的同步时间。静置指标只计画布重绘。[后端分析响应](../../backend/analysis.py) · [客户端计时](../../frontend/static/analysis.js) · [HTTP 封装](../../frontend/static/workbench.js)

## 与原工作台的同口径比较

等本 WP 的录制与仓库回归进程结束，再依次运行原压力用例。第一项分析一个真实 Python 文件，其中 27 个类各含 36 个方法；使用常规 Cinematic 动画。第二项在同源测试画布复用相同 1000 个节点，在 999 条真实包含关系之上加 1001 条仅供压测的边。此项画布为 1200 × 720，启用减少动画；与基线一样交替缩放 40 次，再静置 600 ms。两次观测均为同一台 Windows 机器的单轮采样。

| 输入及指标 | 基线 | 本轮 |
| --- | ---: | ---: |
| 真实 1000 节点、999 边，分析 GET 的 Resource Timing | 74.7 ms | 60.4 ms |
| 文档响应结束至读到 COMPLETE 与统计 | 3062.2 ms | 3161.1 ms |
| 画布绘制帧数 | 164 | 164 |
| 绘制帧间隔 P50 / P95 | 16.7 / 16.9 ms | 16.7 / 16.9 ms |
| 1000 节点、2000 测试边，构造渲染器 | 7.0 ms | 7.7 ms |
| 缩放至下一帧 P50 / P95 | 16.6 / 17.1 ms | 16.6 / 17.2 ms |
| 静置 600 ms 的额外画布重绘 | 0 | 0 |
| 减少动画的阶段回调 | 1 次 COMPLETE | 1 次 COMPLETE |

真实图的帧间隔 P95 保持 16.9 ms。独立压力画布的初始化比基线多 0.7 ms，缩放 P95 多 0.1 ms。端到端读出时间增加 98.9 ms，该量包含导航、动画和 Playwright 读出断言。单次采样不能分解上述差值，HTTP 的差值也不能用来估算服务端 AST 解析的变化。硬件为 Intel Core Ultra 9 275HX；本轮未测系统级 CPU、显存或其他硬件。

## 重现

从仓库根目录使用下列 PowerShell 命令。采集大图截图时，可设置 `TESTPILOT_AST_REFINE_CAPTURE_DIR` 为新建目录；其余情形可保持未设置。旧仓库回归在本 WP 开工时完成用例收集，89 项通过，用时 536.90 s。仓库中其他工作包后来新增的用例另由其责任包验收。

```powershell
$env:TESTPILOT_CAPTURE_DASHBOARD = '0'
$env:TESTPILOT_CAPTURE_REPORTS = '0'
$env:TESTPILOT_CAPTURE_PHASE03 = '0'
.\.venv\Scripts\python.exe -m pytest tests -q --ignore=tests/test_ast_studio.py --ignore=tests/test_ast_refinement.py
.\.venv\Scripts\python.exe -m pytest tests/test_ast_studio.py tests/test_ast_refinement.py -q -s -k 'not large_real_analysis and not dense_renderer'
.\.venv\Scripts\python.exe -m pytest tests/test_ast_studio.py -q -s -k 'large_real_analysis or dense_renderer'
```

| 本轮独立调用 | 真实结果 |
| --- | --- |
| 计时/折叠，原 F02 浏览器，原 F03 生成浏览器 | 3 passed in 110.20s |
| 原工作台的三项业务用例，计时/折叠用例、大图末端搜索 | 5 passed in 198.47s |
| 重播镜头暂停与恢复至适配视野 | 1 passed in 40.07s |
| 滚动定位修复后再次检查大图末端树项全高可见并拍照 | 1 passed in 34.20s |
| 其他本 WP 浏览器作业退出后，单独执行上述两项性能用例 | 2 passed in 73.13s |

表中部分用例因修复复验而重复执行。录制过程中的限速和截图操作单独记录。[有头动画验收](ANIMATION_ACCEPTANCE.md) · [视觉精修与指标溯源](VISUAL_REFINEMENT_REPORT.md)
