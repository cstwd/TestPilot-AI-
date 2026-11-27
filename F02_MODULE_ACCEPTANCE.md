# F02 Python AST 静态分析 · 模块验收

责任工作包：WP01 陈帅廷、WP02 陈万策。实际实现与测试为 Codex，独立复核为 Codex Reviewer。实现提交 `743e24f`，可从项目根目录用 `git show --stat 743e24f` 核对。

**通过。** [分析器](backend/analysis.py)读取一个不可变文件版本，返回行号范围、函数/类/异步函数、形参种类、标注、默认值、返回标注与文档字符串。页面定位语法错误，可选目标继续生成。[业务页面](frontend/templates/analysis.html)

**边界与待办。** 不解析依赖、不执行源码；动态创建的符号和运行时实际类型超出静态分析能力。导入限额为保存的源码大小；分析另设语法节点上限。

## 实际测试

- `.venv/Scripts/python -m pytest tests/test_f02.py -q` → `3 passed in 1.08s`。顶层副作用未执行，类、异步签名、语法错误和控制流中的定义均有断言。[原始输出](reports/phase02/F02.txt)
- `.venv/Scripts/python -m pytest tests/ui_workbench.py -q -k f02` → `1 passed, 1 deselected in 3.21s`，在实际浏览器验证版本、行号、签名及错误状态。[用例](tests/ui_workbench.py)
- Reviewer 指出条件语句中的定义遗漏，已修复并增加回归。
