# F01 项目与代码导入 · 模块验收

责任工作包：WP01 陈帅廷、WP02 陈万策。实际实现与测试为 Codex，独立复核为 Codex Reviewer。实现提交 `77e6177`，可从项目根目录用 `git show --stat 77e6177` 核对。

**通过。** 从 Dashboard 建立项目，选择本地 UTF-8 Python 文件，保存为 SQLite 中不可变的版本，页面可刷新回看并带版本进入 F02。后端按项目、文件名和最新摘要判断重复，事务防止并发分配重复版本。实现见 [API](backend/projects.py)、[数据连接](backend/store.py)、[页面](frontend/templates/projects.html)。

**边界与待办。** 单次导入一个不超过 128 KiB 的 `.py` 文件。目录递归导入、依赖安装及删除版本不在本期范围。

## 实际测试

- `.venv/Scripts/python -m pytest tests/test_f01.py -q` → `5 passed in 1.36s`，覆盖并发重复导入、版本保留、项目隔离、路径及设备名拒绝。[原始输出](reports/phase02/F01.txt)
- `.venv/Scripts/python -m pytest tests/ui_workbench.py -q -k f01` → `1 passed in 4.11s`。真实 Edge 在 375px 视口导入两版并回看旧源码。[浏览器用例](tests/ui_workbench.py)
- 独立复核检查 SQL 参数绑定和版本事务，复跑五项通过；弃用的 Windows 保留名判断已替换。
