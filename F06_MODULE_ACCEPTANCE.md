# F06 质量评估与报告导出 · 模块验收

责任工作包：WP03 赵君豪、WP04 马雪朋、WP05 王选中。实际实现与测试为 Codex，独立复核为 Codex Reviewer。实现提交 `c874456`，可从项目根目录用 `git show --stat c874456` 核对。

**通过。** [质量模块](backend/quality.py)从选定运行、版本、套件、缺陷及回归链构建报告。页面和 JSON 附件共用同一计算函数；一次读取处于同一个 SQLite 快照。记录实测 Python/Pytest/Coverage 版本、测试计数、用例明细、日志、覆盖行与分母、SHA-256 以及缺陷的当前状态。[报告页面](frontend/templates/reports.html)

**边界与待办。** 导出格式为 JSON。通过率排除跳过；无有效分母时为 null。报告给出基于观察结果的解释，不将覆盖率视为正确性证明。历史运行不可变，关联缺陷状态以查看时为准。

## 实际测试

- `.venv/Scripts/python -m pytest tests/test_f06.py -q` → `4 passed in 10.00s`；Reviewer 独立复验 `4 passed in 9.75s`。核对真实失败运行、计数、覆盖率、缺陷以及零分母等情况。[模块测试](reports/phase02/F06.txt)
- `.venv/Scripts/python -m pytest tests/ui_workbench.py -q -k f06` → `1 passed, 5 deselected in 11.74s`，Edge 下载的文件与 API 解码结果逐字段相同。
- [缺陷版真实导出](reports/phase02/buggy-report.json) · [修复版真实导出](reports/phase02/fixed-report.json) · [端到端记录](reports/phase02/e2e.txt)。
