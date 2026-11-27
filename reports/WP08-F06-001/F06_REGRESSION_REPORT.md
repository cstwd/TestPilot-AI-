# F06 回归报告

WP08-F06-001，2026-11-27。实际操作者 Codex。Edge 在真实本机 FastAPI 和独立 SQLite 上运行。测试以 `template` 模式或测试专用固定套件存储，报告来源均为真实 WASI 运行。[验收数据](F06_BROWSER_ACCEPTANCE.md)

```powershell
$env:TESTPILOT_F06_CAPTURE_DIR = Join-Path (Get-Location) 'reports/WP08-F06-001/screenshots'
.\.venv\Scripts\python.exe -m pytest -q -s tests/test_quality_intelligence.py tests/ui_workbench.py::test_f06 --tb=short
.\.venv\Scripts\python.exe -m pytest -q tests/test_f06.py tests/ui_workbench.py::test_f06 tests/test_phase02_flow.py tests/ui_workbench.py::test_f04 tests/ui_workbench.py::test_f05 --tb=short
```

| 批次 | 实测结果 | 覆盖范围 |
| --- | --- | --- |
| 定稿浏览器验收 | **3 passed in 154.01s**，退出码 0 | 正常、失败、混合错误跳过、真零、空分母、缺陷回归、跨版本对照、JSON 快照、HTML 恢复和打印、四种视口。另复跑既有 F06 下载。 |
| 既有业务回归 | **8 passed in 172.21s**，退出码 0 | 原 F06 指标和导出、阶段二链路、F04 复跑、F05 真实回归及 F06 浏览器原路径。 |

执行 `node --check` 核查变更的 JavaScript，使用 `git diff --check` 核对提交。用 `git diff 1acd2ff -- backend/quality.py backend/runs.py backend/runner.py backend/bugs.py` 可查本工作包涉及的业务边界。同期课程模型与证据工作有其他路径修改，提交仅按 WP08 文件范围组织。[指标定义](../../docs/WP08-F06-001/QUALITY_METRIC_DEFINITIONS.md) · [验收脚本](../../tests/test_quality_intelligence.py)

两批合计 10 个不同的测试。按仓库的 `testpilot-reviewer` 流程完成独立只读复核，核对了报告身份、边界指标、对照隔离和共享快照，未发现阻断问题。PDF 验收检查打印视图字段和有效 A4 PDF 文件头，实体打印与产出文件逐页核对留待人工签收。同期课程全量验收使用独立记录。
