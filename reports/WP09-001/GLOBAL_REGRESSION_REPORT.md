# WP09-001 全站回归记录

实际操作者 Codex。Windows 11，项目解释器 Python 3.13.11，Node.js 24.13.0，Playwright 1.65.2，Microsoft Edge 158.0.4370.33。浏览器用例以不同的临时 SQLite 数据目录运行 `main.py --no-browser`，工作台和 API 同源。仓库现有测试与断言未编辑。

## 验收命令和输入

| 运行项 | 命令 | 证据 |
| --- | --- | --- |
| 新增 Edge 集成测试 | `python -m pytest -q -s tests/test_wp09_integration.py --tb=short` | [4 项通过](raw/integration-edge.txt) |
| 收集原有和新增测试 | `python -m pytest -q --collect-only tests eval/phase05/test_manifest.py` | [168 项清单](raw/test-inventory.txt) |
| 仓库完整 Hook | `python hooks/verify.py --scope full --report reports/course-final/verify-full.txt` | 编译通过，Pytest 168 项通过，Node 3 项通过，退出码 0。[完整原始输出](raw/final-full-verify.txt) · [源清单](raw/final-full-verify-overlay.json) |
| 前端语法 | `node --check` 逐一检查 9 个修改的 JS 文件 | [全部通过](raw/frontend-syntax.txt) |
| F02 原生往返缓存 | Edge 去除 Playwright 默认的禁用 BFCache 标志，执行浏览器后退、刷新与文件恢复 | [1 项通过](raw/edge-bfcache.txt) |

四个新增回归分别覆盖六页导航与 503、同项目业务闭环与 36 个视口组合、画布生命周期、真实长日志换行与复制。已有各页用例继续覆盖运行器忙、超时、截断、无日志、生成失败、不可用候选、真实 0% 与未采集覆盖率等边界。 [原始测试清单](raw/test-inventory.txt)

Pytest 全量耗时 35 分 49 秒。日志也保留了受限环境内测试样本故意触发的失败断言，用于核验失败证据和修复流程。外层 Pytest 汇总为 `168 passed`，Node 汇总为 `pass 3`，Hook 汇总为 `outcome=passed`。

## 工作区与数据库

开工 HEAD 是 `b7a8b400db1ebacefb273f377baf0d97a1c440c0`。有课程文档、图稿、Hook 和报告工作并行推进。完整回归基于启动运行时的 `ae21701fefe2d9a7d2282aa9d2494bcd4769e05a` 源码和本包覆盖文件，使用隔离的 WASI 运行目录与临时数据库，将输出复制至本包目录。独立源码清单记录每个被覆盖文件的 SHA-256。

截图和报告下载来自单独的 Edge 集成执行。全量回归会用另一套临时数据库重新创建样本。报告摘要包含执行时间等真实字段，因此每个测试各自核对该次报告、页面和导出。

工作区实际数据库 `data/testpilot.sqlite3` 采用 SQLite URI `mode=ro` 读取。前后 `PRAGMA quick_check` 为 `ok`，项目、文件、套件、运行、缺陷和回归表行数为 `2 / 2 / 2 / 2 / 0 / 0`，六张表的 DDL 摘要一致。业务验收项目和故障注入均在临时数据目录。 [验收后只读巡检](raw/database-readonly.json)

审核者 `testpilot_reviewer` 独立阅读前端改动。其指出文件清单错误路径仍可能丢失已知项目，随后在读取文件前填入已验证项目，并通过 Edge 503 注入复验。人工签收单独登记。
