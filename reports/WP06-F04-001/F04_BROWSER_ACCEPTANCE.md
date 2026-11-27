# F04 Edge 浏览器验收

WP06-F04-001，2026-11-27。Codex 使用本机 Edge 158.0.4370.33 和真实 TestPilot AI。正常及终态样例从根目录 `main.py --no-browser --port <临时端口>` 启动独立 SQLite。并发与故障注入场景使用同一个 FastAPI 工厂，在本机 Uvicorn 独立启动和落库。[启动夹具](../../tests/test_dashboard.py#L20) · [验收用例](../../tests/test_execution_center.py)

## 真实执行与身份连续性

在 F03 为 `measurements.py` v1 的 `magnitude` 使用 `template` 生成套件 1，打开首跑运行 1。项目 ID 为 1。随后执行界面将被测版本切换到同名 v2，保留套件 1 与来源 v1。提交体只有 `{"file_id":2}`。等待阶段禁用提交和配置，原用例、运行 ID 和日志退场，浏览器追加一次表单提交事件仍只观测到一个 POST。[实际请求等待](screenshots/desktop-waiting.png)

| 运行 | 被测版本与套件来源 | 真实结果 |
| --- | --- | --- |
| 运行 1 | 被测 v1／ID 1，套件 1 源自 v1／ID 1 | 5 通过、0 失败、0 错误、0 跳过，退出码 0。[全部通过](screenshots/desktop-passed.png) |
| 运行 2 | 被测 v2／ID 2，套件 1 仍源自 v1／ID 1 | 3 通过、2 失败、0 错误、0 跳过，退出码 1。两个负输入 doctest 的断言失败。[断言失败及原始日志](screenshots/desktop-failed.png) |

失败项置顶。手动选择第二项 `test_generated.py::test_example_2` 后，F05 接收到项目、被测修订、运行 ID 和完整 nodeid，原有表单预选该用例。历史状态筛选、文件／ID 检索、两条运行往返、页面刷新均检查运行 ID、两种版本、计数和日志。日志搜索用含正则符号的字面查询与真实用例名各测试一次。高亮前后文本一致，点击复制后，Windows 剪贴板经平台换行归一化与服务端原串一致。历史、Inspector 和终端可折叠，Inspector 的日志入口会重新展开终端。[手机失败用例](screenshots/mobile-inspector.png)

## 执行错误与明确注入

三种真实终态在单独项目运行。套件 1 均源自 v1，分别应用到三条同名修订。用例核对持久化结果和响应数据。

| 样例 | 证据 |
| --- | --- |
| v2 语法错误 | 运行 2，`error`，真实收集错误 1 个，退出码 2，原始日志含 `SyntaxError`。[执行错误](screenshots/desktop-error.png) |
| v3 达到 WASI 截止时间 | 运行 3，`timeout`，原始诊断含 `deadline`，没有可核对的用例及退出码。[执行超时](screenshots/desktop-timeout.png) |
| v4 超过输出预算 | 运行 4，`error`，原始日志含 runner 结束诊断“输出达到上限，本次日志不完整，结果无效。”。Console 明示截断。[日志截断](screenshots/desktop-truncated.png) |
| 并发冲突 | 测试持有真实 `runs.SLOTS` 信号量以触发服务端 HTTP 409。浏览器显示并发冲突，查询项目历史仍为空。[执行器忙](screenshots/desktop-busy.png) |
| **故障注入：空日志** | 仅在测试进程替换 `runner.execute` 返回空基准记录，走真实执行路由保存。运行 1 的 `log` 是空串，终端提示无日志，复制按钮禁用。[空日志注入](screenshots/injected-empty-log.png) |
| **故障注入：执行器不可用** | 仅在测试进程让 `run_worker` 抛出带 `F04 test-only` 标签的 OSError。真实 runner 持久化运行 2 的 `error` 与环境诊断，UI 显示“执行器不可用”。[不可用注入](screenshots/injected-unavailable.png) |

另测不同文件名的版本无法使用该套件，无效历史 ID 显示错误且日志区为空。

## 响应式实测

| 视口 | 中央实测宽度 | 布局 |
| --- | ---: | --- |
| 1440 × 900 | 832 px | 桌面三栏，底部日志可折叠 |
| 1024 × 768 | 538 px | 压缩三栏，配置仍可提交 |
| 768 × 1024 | 724 px | 顺序阅读并保持用例表可访问。[平板](screenshots/tablet-results.png) |
| 390 × 844 | 390 px | 通过区段链接定位配置与结果，无页面横向溢出。[手机结果](screenshots/mobile-results.png) · [手机 Inspector](screenshots/mobile-inspector.png) |

三个新增浏览器场景均通过，记录 12 张真实 Edge 截图。浏览器以无头模式运行，物理设备和人工视觉签收待项目组确认。[回归命令与退出结果](F04_REGRESSION_REPORT.md)
