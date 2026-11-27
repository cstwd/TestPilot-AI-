# F05 缺陷登记与回归 · 模块验收

责任工作包：WP04 马雪朋、WP02 陈万策。实际实现与测试为 Codex，独立复核为 Codex Reviewer。实现提交 `b6f4ef5`，可从项目根目录用 `git show --stat b6f4ef5` 核对。

**通过。** 用户从有真实失败/错误证据的测试项登记缺陷。回归必须使用原套件、同一项目同名文件的更新版本；只有整次运行通过且原 nodeid 明确通过才标记已解决。原始运行保持可查，新的运行与状态更新在同一事务中关联，按较新源码修订判定当前状态。[缺陷服务](backend/bugs.py) · [页面](frontend/templates/bugs.html)

**边界与待办。** 收集错误、超时和基础设施故障可在运行日志定位；没有可重跑 nodeid 时不能作为该流程的可关闭测试缺陷。当前状态为待修复/已解决；待组长审核后评估是否扩展指派与人工复核状态。

## 实际测试

- `.venv/Scripts/python -m pytest tests/test_f05.py -q` → `2 passed in 13.85s`。实际运行负数样例，修复后同套件重跑，保留失败证据；拒绝旧版本和 Unicode 名称不同的文件。[原始输出](reports/phase02/F05.txt)
- `.venv/Scripts/python -m pytest tests/ui_workbench.py -q -k f05` → `1 passed, 4 deselected in 19.31s`。在 Edge 登记、回归并从已解决记录返回原始 v1 失败运行。[浏览器验收](tests/ui_workbench.py)
- Reviewer 发现文件名比较与 SQLite 的 NOCASE 规则不一致，以及收集错误无法按节点关闭；两项均已修复。
