# F05 回归报告

WP07-F05-001，2026-11-27。测试、截图及提交操作人为 Codex，人工验收待签收。[证据与截图](F05_BROWSER_ACCEPTANCE.md)

```powershell
$env:TESTPILOT_F05_CAPTURE_DIR = Join-Path (Get-Location) 'reports/WP07-F05-001/screenshots'
.\.venv\Scripts\python.exe -m pytest -q -s tests/test_bug_intelligence.py --tb=short
.\.venv\Scripts\python.exe -m pytest -q tests/test_f05.py tests/ui_workbench.py::test_f05 tests/test_execution_center.py::test_execution_history_log_and_case_handoff tests/test_phase02_flow.py --tb=short
node --test tests/bug_diff.test.mjs
```

| 批次 | 结果 | 覆盖 |
| --- | --- | --- |
| 新增 F05 浏览器流程 | **1 passed in 54.94s**，退出码 0 | F04 精确 nodeid、登记、原始套件、同名版本、差异、取消确认、三次真实回归、刷新、503 恢复、四种视口。 |
| 既有业务回归 | **5 passed in 138.70s**，退出码 0 | 缺陷幂等登记、同名判断、F04 的第二个失败项交接、窄屏缺陷回归、阶段二跨模块实测。 |
| Diff 与证据单元测试 | **3 passed** | 插入、删除、行尾差异、空源码、大文件回退、唯一断言归属与歧义拒绝。 |

Edge 在真实服务和临时 SQLite 上执行。仅版本读取失败场景注入一次 HTTP 503，回归结果全部由既有 WASI 产生。以接口核对被测 ID、套件 ID 和对应 nodeid，原始失败运行在变更前后逐字段相同。[F05 浏览器用例](../../tests/test_bug_intelligence.py) · [Diff 单元测试](../../tests/bug_diff.test.mjs)

新版 375 px 流程需要切到 Diff 和显式确认，再回到详情读取结果。首轮旧测试在详情区直接找按钮超时，更新交互断言后保留原先的失败、解决和 F04 回查验收。手机统一 Diff 的删行单元仅保留原始行号。[复核记录](../../collab-log/bugs/WP07-F05-001.md)

执行 `node --check` 核查变更脚本并运行 `git diff --check`。后端、数据库、F04 执行器和回归判定可用 `git diff 9fdfa7e -- backend frontend/static/runs.js frontend/static/run-evidence.js` 核对范围。[原回归判定](../../backend/bugs.py#L62)
