# F04 回归报告

WP06-F04-001，2026-11-27。运行者 Codex。真实 API 和 SQLite 由本机 TestPilot 服务提供，Edge 中文界面用于业务交接与可视状态核对。[验收记录](F04_BROWSER_ACCEPTANCE.md)

## 复验命令

```powershell
$env:TESTPILOT_F04_CAPTURE_DIR = Join-Path (Get-Location) 'reports/WP06-F04-001/screenshots'
.\.venv\Scripts\python.exe -m pytest -q -s tests/test_execution_center.py --tb=short
.\.venv\Scripts\python.exe -m pytest -q tests/test_f04.py tests/ui_workbench.py::test_f04 tests/ui_workbench.py::test_f03 tests/ui_workbench.py::test_f05 tests/ui_workbench.py::test_f06 tests/test_ast_studio.py::test_file_to_generation --tb=short
.\.venv\Scripts\python.exe -m pytest -q tests/test_runner.py --tb=short
```

| 批次 | 结果 | 核对范围 |
| --- | --- | --- |
| 新增 F04 浏览器测试 | **3 passed in 167.47s**，退出码 0 | 真实等待及防重复、全部通过、断言失败、收集错误、截止时间、截断、忙与标注的故障注入。历史、刷新、日志、F05 节点交接和四种视口。 |
| 原有业务链路 | **7 passed in 256.20s**，退出码 0 | F04 同名约束与结果持久化，F01→F02→F03，F03 首跑与 F04 复跑、F05 回归、F06 报告下载。 |
| 受限执行器 | **5 passed in 38.48s**，退出码 0 | 结果与覆盖率、客体能力限制、截止时间和工作目录清理、收集错误、日志预算、全部跳过。 |

`node --check` 检查 `runs.js`、`run-evidence.js`、`workbench.js`、`bugs.js`。提交前后检查 `git diff --check`。验证修改范围可用 `git diff 7c796e7 -- backend`。F05 的接入点只消费已存在用例的可选 `nodeid` 查询参数，缺陷登记与回归协议沿用原路径。[F04 端点](../../backend/runs.py) · [F05 端点](../../backend/bugs.py) · [执行器测试](../../tests/test_runner.py)

## 调整记录

初测时，只带套件 ID 的旧入口提前在 URL 增加历史 run，旧业务用例会把原首跑识别为刚提交的新运行。现在只对显式指定 run 的历史链接规范化该 ID，POST 完成后再进入新运行的链接。被测版本及状态选择器补充了稳定的可访问名称。[缺陷记录](../../collab-log/bugs/WP06-F04-001.md)

浏览器测试既核对页面，也向同一运行端点重新读取持久化记录。正常记录的 case 字段有限，验收检查未记录的耗时、断言栈和异常类型在页面没有被替代。终端核对真实顺序、截断提示和原文复制。[新增用例](../../tests/test_execution_center.py)
