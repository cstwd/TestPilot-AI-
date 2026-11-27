# F09 · AI Test Generation Engine

**供应商适配、候选校验和离线降级已通过。** 首次盘点时本机 Ollama 接口可连但没有已登记模型；本报告的协议测试不能用于评定模型推理质量。真实模型的可用性和实测情况以[阶段总报告](TP_PHASE_03_ACCEPTANCE.md)为准。

责任人陈帅廷，实际实现与执行为 Codex 模型适配子代理，集成复核为 Codex 主代理。实现提交 `c370d42`，契约复核修正 `ab954d0`。[模型适配器](backend/engine_llm.py) 调用已配置的 Ollama 或 OpenAI 兼容模型，传入源码、策略、目标、失败上下文及上一版测试。记录每次请求的模型、消息、重试、拒绝候选与诊断；只在模型响应通过 AST 和测试结构校验后标记 `ai`。有界超时/重试、禁重定向、明确的模板降级和双重失败证据均经过测试。[模型配置](docs/phase03/MODELS.md)

- `.venv/Scripts/python.exe -m pytest tests/test_f09.py -q -s` 实际为 **11 passed in 3.06s**。两种请求协议使用明确标识的本地 HTTP 测试替身。另一项 WASI 执行实测模板生成的用例 3 通过、0 失败、1 跳过。[独立输出](reports/phase03/F09.txt)
- 跨模块复核发现带 doctest 指令的示例在分析和模板阶段处理不一致。PHASE-03 在共享适配器中选择尊重这些指令，旧调用保留原行为。独立复验包含提供方、生成、分析和证据链。[复核输出](reports/phase03/cross-module-review.txt) · [单元测试](tests/test_f09.py)
- 模型生成的测试只能在真实执行后计入统计。未配置远程服务时，远程推理能力的表现需用目标端点另测。
