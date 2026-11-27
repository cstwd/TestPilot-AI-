# TP-F12-GENERATED-ORACLE · 生成器引入

| 项 | 记录 |
|---|---|
| 发现 | 2026-11-27，F11/F12 端到端；责任 WP03，操作 Codex；模式 template → rules |
| 初始 Prompt | [PHASE-03 原始任务书](../../transcripts/TP-PHASE-03.md)；产品收到显式 template 的目标函数及一次修正上限 |
| 初始生成输出 | `test_boundary_return_contract` 调用 `reciprocal_units(0)` 并要求整数。完整初次和修正源码保存在 [GeneratedTest 事件](../../reports/phase03/cases/repair.json) |
| 复现与现象 | 导入 [零输入样例](../../eval/phase03/repair/subject.py)，选择 `reciprocal_units`、template，允许一次修正。首跑执行到 ValueError，节点失败 |
| 根因 | 边界候选沿用了返回类型约束，但该输入的独立文档契约明确要求引发 ValueError |
| 修复 | F11 标记 `test_error`，F12 将该调用包在 `pytest.raises(ValueError)` 内，原源码摘要和其他用例保留。[实现](../../backend/engine_feedback.py) |
| Git | `f4de268`, `978323d`, `7422857` |
| 回归及结果 | `python -m pytest tests/test_phase03_e2e.py -q -s`，历史 7 项通过，样例计数 4/1/0/1 → 5/0/0/1。[实测](../../reports/phase03/E2E.md) |
| 沉淀 | 自动修复依据独立文档契约，保留原失败运行 |
