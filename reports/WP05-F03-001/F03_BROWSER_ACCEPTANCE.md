# F03 浏览器验收

工作包 WP05-F03-001，2026-11-27。由 Codex 在 Windows 的 Microsoft Edge 158.0.4370.33 中执行。正常、拒绝与首次失败场景以仓库根目录的 `main.py --no-browser --port <临时端口>` 提供页面和 API，每个用例分配独立 SQLite。首次 Pytest 由项目原有 WASI 运行器执行。[主启动夹具](../../tests/test_dashboard.py#L20) · [验收用例](../../tests/test_generation_studio.py)

## 源码、套件与首次运行

测试导入同名 `measurements.py` 的 v1、v2。选择 v1 中的 `magnitude` 后，源码窗从第 1 行开始，仅显示该定义。搜索 `SIGNED` 后可选择第二个函数，源码自动从真实第 10 行开始。同一版本的两次生成请求均发送 `template`。浏览器逐行比对 Pytest 窗口与服务返回的源码，读取实际运行端点并核对四个 ID、结果及运行记录时间。[待生成界面](screenshots/desktop-ready.png)

| 项目／版本 | 函数限定名 | 套件 ID | 静态检查 | 首次 Pytest 与真实运行 ID |
| --- | --- | ---: | --- | --- |
| 项目 1，v1／ID 1 | `magnitude` | 1 | 通过 | 运行 1，4 通过、0 失败、0 错误、1 跳过，退出码 0。[桌面通过](screenshots/desktop-passed.png) |
| 项目 1，v1／ID 1 | `signed_magnitude` | 2 | 通过 | 运行 2，3 通过、1 失败、0 错误、1 跳过，退出码 1。真实 doctest 输入 `-3` 的预期为 `3`，实现返回 `-3`。[桌面失败](screenshots/desktop-failed.png) |

刷新后保留所选函数和套件。历史切换到套件 1 时，上方仍显示当前目标 `signed_magnitude`，Inspector 的套件来源则为 `magnitude`。F04 链接携带 `project=1&file=1&suite=1&run=1`，点击后出现 `运行 #1`。切换到同名 v2 不显示 v1 套件。显式把 v1 套件 ID 带入 v2 会显示版本不匹配说明。[移动端详情及 F04 入口](screenshots/mobile-console.png)

## 失败与恢复

| 场景 | 实测 |
| --- | --- |
| 服务端生成拒绝 | 定义 `no_contract` 通过函数范围筛选，模板返回真实 HTTP 422，解释缺少可验证契约。当前版本的套件列表为空，Console 的静态检查和首跑均无记录。[拒绝状态](screenshots/desktop-rejected.png) |
| 不可生成的跳转目标 | AST 包含条件块内的同步函数、异步函数和两个同名顶层同步定义，列表排除这些目标；深链指定条件函数时保留提示并禁用提交。另测语法错误与无效项目上下文。 |
| 执行器忙，暂无首跑 | 独立本机 Uvicorn 使用同一个应用工厂和临时 SQLite，测试持有原始 `runs.SLOTS` 信号量以确定性制造忙状态。真实端点返回 HTTP 409，套件详情保留静态检查通过，`initial_run=null`、运行列表为空。Console 显示“执行器忙”和“尚无记录”，F04 链接只有套件身份。释放信号量后重试复用套件 1，运行器写入首跑 1 并返回通过。[执行器忙](screenshots/desktop-busy.png) |

## 响应式

| 浏览器视口 | 中央区域实测宽度 | 观察 |
| --- | ---: | --- |
| 1440 × 900 | 838 px | Explorer、源码与套件、Inspector 三栏并排，Console 在底部。 |
| 1024 × 768 | 520 px | 三栏保持可用。编辑器内局部滚动。 |
| 768 × 1024 | 724 px | 顺序阅读，Inspector 属性分两列。[平板结果](screenshots/tablet-suite.png) |
| 390 × 844 | 390 px | 源码、结果、Inspector 与状态顺序阅读，测试验证结果区快捷跳转，文档无横向溢出。[手机结果](screenshots/mobile-suite.png) · [手机状态](screenshots/mobile-console.png) |

三个新增浏览器场景全部通过并生成八张截图。Edge 以无头方式运行，物理设备和其他浏览器的人工观感待签收。[回归命令与退出结果](F03_REGRESSION_REPORT.md)
