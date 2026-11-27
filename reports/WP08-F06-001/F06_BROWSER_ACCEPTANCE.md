# F06 Edge 浏览器验收

WP08-F06-001，2026-11-27。实际操作者 Codex。Windows 11、Edge 158.0.4370.33。服务从根目录 `main.py --no-browser --port <临时端口>` 启动，运行与报告写入独立 SQLite，执行沿用原 WASI。浏览器以无头方式运行。[启动夹具](../../tests/test_dashboard.py#L20) · [验收脚本](../../tests/test_quality_intelligence.py)

## 真实报告与来源

| 项目与运行 | 版本和套件 | 通过／失败／错误／跳过 | 通过率 | 行覆盖率 |
| --- | --- | --- | --- | --- |
| 项目 2，运行 1，断言失败 | `measurements.py` v1，文件 1，套件 1 | 3 / 2 / 0 / 0 | 60%，3/5 | 100%，2/2 |
| 项目 2，运行 2，回归通过 | `measurements.py` v2，文件 2，套件 1 | 5 / 0 / 0 / 0 | 100%，5/5 | 100%，2/2 |
| 项目 1，运行 1，测试和 setup 混合结果 | `worker.py` v1，文件 1，套件 1 | 1 / 1 / 1 / 1 | 33.33%，1/3 | **0%**，0/2 |
| 项目 1，运行 2，全部执行项失败 | `worker.py` v1，文件 1，套件 2 | 0 / 1 / 0 / 0 | **0%**，0/1 | **0%**，0/2 |
| 项目 1，运行 3，全部跳过 | `blank.py` v1，文件 2，套件 3 | 0 / 0 / 0 / 1 | **无可计算的用例**，0/0 | **未采集**，0/0 |

两组使用独立临时库，表中的 ID 为各自库内真实主键。首组从 F03 模板生成，经 F04 失败运行登记缺陷，由 F05 回归修复版本。第二组通过测试夹具提供固定 Pytest 源码并用原生成持久化保存套件，实际执行、计数、覆盖率及报告全由生产路径生成。混合样例的测试未导入 `subject.py`，所以 0/2 行为真实值。[失败运行](screenshots/desktop-failed.png) · [通过运行](screenshots/desktop-passed.png) · [混合结果和真零覆盖率](screenshots/desktop-mixed-zero.png) · [零分母与缺失覆盖率](screenshots/desktop-unmeasured.png)

从 F04 原始运行进入报告后，Inspector 与 API 逐项对照运行 ID、项目 ID、文件 ID、修订、套件、来源文件、终态、耗时与两项 SHA-256。缺陷 1 关联原始运行 1，最终回归记录为运行 2、v2、文件 2。链接分别打开 F05 缺陷和 F04 原始或回归证据。按文件版本、状态筛选后可切换运行，刷新保留已选运行。无运行或异项目运行只显示对应的空态或错误。[两次运行对照](screenshots/desktop-comparison.png) · [口径 Drawer](screenshots/desktop-definitions.png)

## JSON、HTML 与打印

在失败运行报告仍为“待修复”时，真实服务执行了 v2 回归并更新缺陷状态。工作台、HTML 与两个 JSON 下载仍展示打开报告时的同一快照，JSON 解析结果与原报告逐字段相等。原 `/report/export` 路由仍响应 JSON 附件，且即时内容与刷新后的“已解决”报告一致。选择对照运行后，再次下载仍等于当前主报告。对照数据只出现于比较表。

HTML 视图保留主报告的真实身份、统计、覆盖率、关联缺陷和回归判定。刷新 HTML 深链接后恢复同一运行。切换到 Chromium 打印媒体时，筛选和工作台工具隐藏，报告数据仍可见。浏览器实际生成了带 `%PDF-` 文件头的 A4 PDF，测试产物写入临时内存。[HTML 报告](screenshots/desktop-html-report.png)

## 响应式

| 视口 | 主区实测宽度 | 观察 |
| --- | ---: | --- |
| 1440 × 900 | 849 px | 运行、指标、证据三栏。 |
| 1024 × 768 | 562 px | 保留三栏，指标具备标签与分母。 |
| 768 × 1024 | 724 px | 运行、指标、证据顺序阅读。[平板](screenshots/tablet-metrics.png) |
| 390 × 844 | 390 px | 图表纵向排列，指标跳转保留运行上下文，页面无横向溢出。[手机指标](screenshots/mobile-metrics.png) · [手机证据](screenshots/mobile-evidence.png) |

共保存 10 张真实 Edge 截图。人工视觉、物理设备和其他浏览器待项目组验收。[回归命令与退出结果](F06_REGRESSION_REPORT.md)
