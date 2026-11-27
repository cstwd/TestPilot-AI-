# TP-MODEL-SCHEMA · AI 输出引入

| 项 | 记录 |
|---|---|
| 发现 | 2026-11-27，PHASE-05 T02 源码理解和质量评分；责任 WP03，操作 Codex 与 Qwen3.8-27B |
| 初始 Prompt | 冻结系统提示要求 `parameters` 的每项为名称、注解、默认值的三元素数组。用户请求包含带行号 `cap` 函数。原文在 `request.messages`。[真实请求与回应](../../reports/phase05/raw/understanding/clamp.json) |
| AI 原始输出 | 在 `raw.choices[0].message.content`，例如 `{"name":"n","annotated_type":"int","default":null}` |
| 复现与现象 | 使用该响应回放冻结协议，`parameters` 因对象结构失败，其它字段独立评分。10 项参数均按冻结协议计 0，总分 56/70 |
| 根因 | PHASE-05 请求仅限制 JSON 对象，字段值的具体形状由提示文字表达 |
| 修复 | PHASE-06 使用类型化固定 Schema 和受限重试。测试先注入对象形式，再注入合法数组，校验拒绝及审计原文。[Schema](../../backend/model_protocol.py) · [回归](../../tests/test_model_provider.py) |
| Git | 历史证据 `8923f2c`，统一 Schema `98adf18`，主线合并 `646ef7d` |
| 结果 | 历史严格分数保留。[逐字段评分](../../reports/phase05/T02_SOURCE_UNDERSTANDING.md) |
| 沉淀 | 将格式问题计入真实评估，并在后续运行通过结构化协议预防 |
