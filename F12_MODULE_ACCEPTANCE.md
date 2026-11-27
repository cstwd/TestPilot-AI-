# F12 · Feedback & Repair Engine

实测通过。责任人陈帅廷，实际实现、测试和交叉审查由 Codex 执行。实现提交 `f4de268`，工作台和真实样例集成提交 `978323d`。

[反馈修正器](backend/engine_feedback.py) 只在失败证据指向生成测试且有独立契约时修正失败语句。模型生成的套件可带上失败证据和原测试重新请求模型；自动接受要求候选符合可核验的局部改动。模板可按契约重新生成该语句并标记 `rules`。未决或混合程序错误保留复核；缺少外部依据的期望函数不会自动替换。按归一化代码摘要防重复，最多三次反馈，默认一次。每次尝试、初末测试和运行结果都写入[任务历史](backend/engine_flow.py)。

- `.venv/Scripts/python.exe -m pytest tests/test_f12.py -q -s` 最初暴露 F11/F12 函数签名不一致，2 项失败、2 项通过。对齐接口后 4 项通过，加入保护独立期望函数的回归后最终 **5 passed in 11.71s**。[初次输出](reports/phase03/F12-first.txt) · [修正后输出](reports/phase03/F12-review.txt)
- 真实 `reciprocal_units(0)` 文档约定抛出 ValueError。初版测试对该输入检查返回整数；分析器识别测试预期错误，修正器仅更新该语句。相同源码上初次 4 通过、1 失败、1 跳过，重跑 5 通过、0 失败、1 跳过。两次测试文件、摘要、失败证据和执行 ID 可复查。[完整任务 JSON](reports/phase03/cases/repair.json) · [源码](eval/phase03/repair/subject.py)
- 已实跑的修正样例来自模板，模型候选的拒绝路径另作协议/控制流测试。真实模型修正能力的验收范围见[阶段总报告](TP_PHASE_03_ACCEPTANCE.md)。
