
# TP-PHASE-07 Demo Lab 产品验收

2026-11-27 · Windows 11 · 项目 Python 3.13.11 · Edge 158.0.4370.33

| 角色 | 记录 |
| --- | --- |
| 联调责任人 | 陈帅廷（WP01），关联 WP02 界面、WP03 测试、WP04 质量、WP05 取证 |
| 实际操作者 | Codex |
| 独立复核 | 按仓库 `testpilot-reviewer` 定义执行。发现并复验运行所有权、主库隔离、F05 证据绑定和界面历史顺序问题 |
| 人工签收 | 由项目组后续登记 |
| 实现提交 | `fed7a62` |

## 功能结果

| 验收项 | 实际观察 |
| --- | --- |
| 冻结索引 | 100 个模块和源码摘要、75 个修复版摘要全部通过 HTTP 检查。GOOD 25、BUGGY 50、CHALLENGE 25，覆盖六个领域。隐藏 JSON 路径不可访问，提交源码字段返回 422。 |
| 优先演示 | `unit_scaling` 原版 v1 的真实断言为 `1 == 1.25`，同套件修复版 v2 通过，缺陷关闭，F13 实际执行。 |
| GOOD | `calculator` 的 `add` 流程通过，F13 实跑两项。 |
| BUGGY | `unit_scaling`、`binary_search`、`volume_discount` 均完成原版失败、同套件修复回归、缺陷关闭。 |
| CHALLENGE | `booking_timezones`、`member_checkout`、`filtered_pagination` 均实际执行，并在修复版本通过原失败节点。 |
| 重跑与独立报告 | 再运行 `unit_scaling` 获得新项目 ID 和演示 ID，原报告仍能等值读取。完整导出与 GET JSON 一致。Lab 运行 ID 对应的 F06 和 F13 快照分别可读。 |
| 运行边界 | 同源 API 只接收目录内样本 ID、模式和变异开关。WASI 执行遵循既有只读挂载及执行界限。演示与主工作台使用独立数据库。主工作台空项目列表和不存在运行编号的响应保持对应含义。 |
| 浏览器 | 桌面 Edge 从首页进入、按类型领域和名称筛选、查看合同、启动真实演示、对照断言与回归、下载、刷新重读和从报告中心返回。390 px 视口无页面横向溢出。 |

每组运行使用独立 SQLite 项目，带源和套件摘要、阶段耗时、Pytest 退出码和节点、日志、修复原文及回归结果。AI 模式和模板来源分别记录。原始七样本、重跑及浏览器记录见 [七样本回执](end-to-end.json) 和 [浏览器下载回执](edge-run.json)。

另用实际 F13 会话检查 `geometry_calculator.area` 的存活定位。共 5 个变异，杀死 2，存活 1，执行错误 2，全量得分 40%，有效得分 66.67%。Edge 展开了第 8 行的存活变异。[会话 JSON](f13-geometry.json) · [浏览器检查](f13-view-check.txt) · [定位截图](05-f13-surviving-mutant.png)

## 专项统计复算

- Git 归档包含 225 个冻结文件。SHA-256 清单是其中 1 个文件，清单中 224 条记录逐项匹配其余文件。本阶段继续采用同一冻结快照。
- 历史 F13 的 48 个变异包含 34 个杀死、11 个存活和 3 个执行错误。全量得分使用全部清单位置，`34 / 48 = 70.83%`。有效得分的分母仅移除执行错误，`34 / 45 = 75.56%`。其他观测状态仍单列，原历史 JSON 和原始分数保持该运行的原有口径。

## 入口与证据

仓库全量校验完成，编译检查、173 项 Pytest 和 3 项 Node 测试全部通过。独立追加的 F13 存活定位测试另有 1 项通过。[全量日志](verify-full.txt) · [追加定位检查](f13-view-check.txt)

双实例争用、重启恢复、缺少模型证明和侧库损坏均实测了拒绝或降级路径。故障用例使用临时目录，重启用例使用预置的中断状态检查恢复机制。[故障路径回执](failure-paths.json)

## 本机 AI 实测

全量回归结束后，单独启动已安装的固定 Qwen3.8-27B Ollama/Vulkan 守护，并用产品 AI 模式提交 `calculator`。该次运行完成导入和静态分析。模型加载时可用物理内存降到约 0.98 GiB，触发既有的 2 GiB 资源保护，源码理解返回 unavailable，AI 套件生成和 WASI 执行未发生。完整失败报告仍保存并可按相同 ID 导出。[实际 AI 回执](ai-live.json)

## 复现命令与归档

```powershell
.venv/Scripts/python.exe -X utf8 hooks/verify.py --scope full --report reports/phase07/verify-full.txt
.venv/Scripts/python.exe -X utf8 -m pytest -q -s tests/test_demo_lab_mutation_view.py
.venv/Scripts/python.exe -X utf8 demo/TestPilot-Demo-Lab/scripts/generate_catalog.py --check
```

截图来自真实 Edge 会话。[样本与筛选](01-source-and-filters.png) · [回归和 F13](02-regression-and-mutation.png) · [移动端](03-mobile-report.png) · [报告中心](04-report-center.png)

交付清单按 Git blob 的原始字节计算，校验时按每一行路径读取提交对应的 `git cat-file blob HEAD:<path>` 并计算 SHA-256，Windows 工作区换行转换不改变该校验口径。冻结数据集仍用其独立清单校验。

[运行手册](../../docs/phase07/DEMO_MANUAL.md) · [问题记录](../../collab-log/bugs/TP-PHASE-07-DEMO-LAB.md) · [交付清单](SHA256SUMS.txt)
