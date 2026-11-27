# F03 回归报告

工作包 WP05-F03-001，2026-11-27。Codex 在实际 Windows 工作区使用项目虚拟环境、真实 FastAPI 与本机 Edge 执行测试。浏览器场景使用各自的临时 SQLite 数据库。项目组人工复核待签收。[图文浏览器验收](F03_BROWSER_ACCEPTANCE.md)

## 复验命令

```powershell
$env:TESTPILOT_F03_CAPTURE_DIR = Join-Path (Get-Location) 'reports/WP05-F03-001/screenshots'
.\.venv\Scripts\python.exe -m pytest -q -s tests/test_generation_studio.py --tb=short
.\.venv\Scripts\python.exe -m pytest -q tests/test_f03.py tests/ui_workbench.py::test_f03 tests/test_ast_studio.py::test_file_to_generation tests/test_project_workspace.py::test_import_history_and_analysis tests/ui_workbench.py::test_f04 --tb=short
```

| 验证批次 | 结果 | 覆盖 |
| --- | --- | --- |
| F03 新工作台 | **3 passed in 121.94s**，退出码 0 | 模式固定、两次真实首跑、历史刷新及 F04 跳转、版本隔离、无效上下文、HTTP 422、HTTP 409、候选无首跑和重试。 |
| 原有链路 | **6 passed in 174.22s**，退出码 0 | 原模板及静态校验单元测试，F01 的旧／新修订 → F02 → F03，F03 生成及真实首跑 → F04，以及 F04 独立执行。 |

`node --check frontend/static/generation.js`、`git diff --check` 均执行。可从 `git diff 9f048d0 -- backend frontend/static/runs.js frontend/static/analysis.js frontend/static/projects.js` 核对业务边界。前端仍在原路由同源读取 API，提交内容是 F03 模板、样式、控制器与共享工作台的接入点。[公共分派](../../frontend/templates/workbench.html) · [生成 API](../../backend/generation.py) · [真实运行 API](../../backend/runs.py)

## 实测调整

首轮回归定位到目标表单标签与源码区的可访问名称包含同一词组，原有 `get_by_label("目标函数")` 路径出现多匹配。目标控制的名称保留为“目标函数”，源码区改用单独名称后复验现有调用。新增拒绝用例在通过 API 导入语法错误样本后先重载清单，再选择新修订。通过断言分别检查当前目标、套件来源、静态结果、运行 ID 和运行结论。[缺陷记录](../../collab-log/bugs/WP05-F03-001.md)

签收范围包含桌面、平板和手机 CSS 视口。人工观感、其他浏览器及物理手机留待项目组验收。
