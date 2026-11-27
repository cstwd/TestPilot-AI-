# F03 测试生成 · 模块验收

责任工作包：WP03 赵君豪、WP02 陈万策。实际实现与测试为 Codex，独立复核为 Codex Reviewer。实现提交 `2b2185c`，可从项目根目录用 `git show --stat 2b2185c` 核对。

**模板模式通过。** 保留 [ModelAdapter 与模板实现](backend/generation.py)，当前安装使用 `template`。从签名和字面量 doctest 构造正常、边界、显式预期、非法参数和适用的属性建议。生成源码经 AST 格式化和编译再保存，附不可变 suite、文件及摘要。页面可审阅并传入执行器。[生成页面](frontend/templates/generation.html)

**边界与待办。** 当前未配置在线模型；支持模块顶层同步函数。类型样本可能触发业务前置条件，须人工核对。当前来宾缺少 Hypothesis 原生扩展，属性用例标记跳过，建议和源码可查。

## 实际测试

集成提交 `f31a901` 将生成与 F04 首跑打通。生成 API 先保存不可变套件，再由隔离执行器实际运行；生成页和回读接口返回 `initial_run.id` 与实际状态，同版本重复请求复用首跑。验收命令 `.venv/Scripts/python -m pytest tests/test_phase02_flow.py -q -s`，结果 `1 passed in 17.57s`。[实测输出](reports/phase02/e2e.txt)

- `.venv/Scripts/python -m pytest tests/test_f03.py -q` → `2 passed in 1.10s`，验证显式预期、非法目标和输出格式。[输出](reports/phase02/F03.txt)
- `.venv/Scripts/python -m pytest tests/ui_workbench.py -q -k f03` → `1 passed, 2 deselected in 5.12s`，浏览器实际生成并回读套件。
- 独立探针在 WASI 以固定 `pytest.main(...)` 运行生成源码，`1 failed, 5 passed, 1 skipped`。`test_example_3` 捕获负数符号缺陷，退出码 1。探针使用 `.venv/Scripts/python .runtime/probes/probe.py`；正式复现入口见 [F04](F04_MODULE_ACCEPTANCE.md) 和 [集成验收](TP_PHASE_02_ACCEPTANCE.md)。[真实来宾输出](reports/phase02/F03-guest.txt)
- Reviewer 独立复跑生成测试并检查显式 oracle 与推断契约的区别。
