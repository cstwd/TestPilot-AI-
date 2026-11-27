# F02 浏览器交互验收

**WP03-AST-VISUAL-001 · 2026-11-27**　实际操作者 Codex，人工复核待项目组安排。本报告记录真实页面及交互结果，配套[性能测量](PERFORMANCE.md)。测试入口为 [tests/test_ast_studio.py](../../tests/test_ast_studio.py)。

## 环境与重现

工作目录 `D:\TestPilot AI`，开工基线 `74228571823aa5f38824e948dc111920fae72c3f`。Windows 11 10.0.26200、Python 3.13.11、Playwright 1.65.2、Microsoft Edge 158.0.4370.33（无头，DPR 1）。测试复用[仓库的应用夹具](../../tests/test_dashboard.py)，由 `main.py --no-browser --port <临时端口>` 启动 FastAPI，并通过 `TESTPILOT_DATA_DIR` 向每项测试提供独立临时 SQLite 目录。

从仓库根目录执行以下 PowerShell 命令可重现验收。未设置截图变量时，用例仍在临时库创建验收数据，磁盘截图保持原样。

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_f02.py tests/ui_workbench.py::test_f02 -q
$env:TESTPILOT_AST_CAPTURE_DIR = 'reports/WP03-AST-VISUAL-001/screenshots'
.\.venv\Scripts\python.exe -m pytest tests/test_ast_studio.py -q -s --tb=short
```

改动前的 F02 基线结果为 **4 passed in 33.67s**。既有用例覆盖 Python 静态结构、语法错误、无符号文件、条件定义，以及窄窗用浏览器切换文件版本。[既有静态检查](../../tests/test_f02.py) · [既有浏览器检查](../../tests/ui_workbench.py)

## 业务主线

最终五项浏览器用例 **5 passed in 202.93s (0:03:22)**，退出码 0。可直接下载或用 F01 选择[同一份 telemetry.py 样例](../../eval/ast_visual/telemetry.py)复现。

1. 在 F01 创建项目 `Telemetry Lab`，通过文件选择器导入验收源码 `telemetry.py`，核对 UI 展示的 SHA-256 为 `84c097052cfbecef569b405c96b34f477373d3c7ce4037a245fb9934fc675490`。
2. 点击“分析此版本”，取得项目 ID 1、不可变文件 ID 1、修订 v1 的真实分析。图中为 1 个文件、3 个类、4 个函数（其中 1 个为函数内定义）、8 个方法，共 16 个节点、15 条包含边。没有将 Python 中对其他符号的引用计为调用边。
3. 从树选择 `Sample`，点击画布空白取消，再点击节点恢复选择和双击查看局部结构。从 Structure 进入 `Sample.normalized`。Overview 显示 `scale` 参数；Source 跳到第 10 行，复制结果包含方法体。点击第 3 行的类定义，当前选择回到 `Sample`。[类与图谱](screenshots/class-overview.png) · [父子结构](screenshots/class-structure.png) · [带行号的源码](screenshots/source-inspector.png)
4. 搜索 `mean_value`，用键盘选定。刷新后恢复相同节点，从快照加载，浏览器未再发起分析 GET。点击重播、暂停、等待 450 ms、继续，完整播放后恢复探索。缩放、复位、适配及打开／Esc 关闭帮助和设置均成功。
5. 在 390 px 单面板模式下从资源区选回 `mean_value`，进入既有 F03。浏览器路由参数为 `project=1&file=1&symbol=mean_value`，目标函数控件实际值为 `mean_value`。此主线在 F03 正确选中目标后结束。

## 视口实测

表中宽高取自 `canvas.getBoundingClientRect()`（CSS px，取整）。所有视口的 `documentElement.scrollWidth` 均等于窗口宽度。窄屏下切到资源、详情后，也检查了图谱容器的实际宽度。

| 视口 | 中央画布 | 图像 |
| --- | --- | --- |
| 1920 × 1080 | 1236 × 764 | [大屏](screenshots/graph-1920x1080.png) |
| 1440 × 900 | 836 × 591 | [桌面](screenshots/graph-1440x900.png) |
| 1280 × 800 | 686 × 495 | [小桌面](screenshots/graph-1280x800.png) |
| 1024 × 768 | 750 × 463 | [侧栏叠层](screenshots/graph-1024x768.png) |
| 768 × 1024 | 724 × 690 | [平板](screenshots/graph-768x1024.png) |
| 390 × 844 | 390 × 478 | [手机](screenshots/graph-390x844.png) |

## 版本、失败与读写边界

| 场景 | 实际检查 |
| --- | --- |
| 同名的两个类及其同名方法 | `signal.py` 第一版为单个函数，第二版含两处 `class Sensor`。用版本选择器切至第二版；两个 `read` 的父节点分别为 `symbol:2:1:Sensor`、`symbol:2:3:Sensor`，异步方法中的 `nested` 仍按函数收录。对象 ID 唯一，旧版选择清除。 |
| 空文件、错误、恢复 | 通过真实导入接口创建空文件和语法错误文件，空文件产生文件节点 1、边 0；错误文件显示真实第 1 行错误。切回第一版并点击“重新分析”，收到相同文件摘要的 HTTP 成功应答。 |
| 无项目与无效深链 | 新库直接打开 F02 可进入待导入态。把项目 A 与项目 B 的文件 ID 拼为一条链接，或访问无效项目号；均不得展示其他项目符号或提供 F03 动作。 |
| 网络错误与重试 | 首次分析 GET 在浏览器内注入一次 HTTP 503，验证请求等待态、错误详情与按钮重试。重试由实际服务返回；此处 503 是确定性的故障注入。 |
| 类型过滤与恢复 | 关闭全部类型，显示筛选空态；从全量符号搜索 `convert`，实际恢复函数类型和选中对象。 |
| 渲染与安全 | 图谱输入来自测试创建的不可变文件，后端静态解析。正文和文档字符串作为只读文本展示。所有浏览器用例均在退出时核对未捕获的页面脚本异常。 |

首次独立渲染器测试的绘制和鼠标断言已通过，但测试夹具把直接访问 JSON 页面引起的浏览器默认 favicon 请求视为异常。基准入口已改为自带 favicon 的正常同源页面，保留原夹具断言。目视检查另发现旧样式会使 Source 行号随行长移动；验收增加逐行测量行号左缘的断言。

## 仓库回归与提交记录

实现提交为 `7f724d05c622e6be73de2f01ac5ddbb8e5171dc1`，提交作者 Codex。对既有测试另外运行以下命令，得到 **89 passed in 491.44s**，退出码 0。连同新增的 5 项，共有 94 项在两次调用中通过。三个截图环境变量用于保留前期验收截图。

```powershell
$env:TESTPILOT_CAPTURE_DASHBOARD = '0'
$env:TESTPILOT_CAPTURE_REPORTS = '0'
$env:TESTPILOT_CAPTURE_PHASE03 = '0'
.\.venv\Scripts\python.exe -m pytest tests -q --ignore=tests/test_ast_studio.py
```

在实现提交上再次启动本机服务，复跑原 F02 和 F01 → F02 → F03 浏览器主线。以下命令得到 **5 passed in 80.34s**，退出码 0。此次复验覆盖前述用例的子集。

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_f02.py tests/ui_workbench.py::test_f02 tests/test_ast_studio.py::test_file_to_generation
```

本次在 Windows 的无头 Edge 中检查了真实页面。人工使用 PyCharm 和物理设备的视觉复核留待项目组签收。WP03 登记负责人赵君豪，实际操作者 Codex，人工复核待组长陈帅廷协调。技术选型、交互规则、原始量测和缺陷复验可分别查阅。[技术设计与交互说明](../../docs/WP03-AST-VISUAL-001/TECHNICAL_DESIGN.md) · [性能报告](PERFORMANCE.md) · [Source 行号缺陷记录](../../collab-log/bugs/WP03-AST-VISUAL-001.md)

阶段状态为 `READY_FOR_VISUAL_INTELLIGENCE_REVIEW`。
