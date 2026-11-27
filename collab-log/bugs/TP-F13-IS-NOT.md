# TP-F13-IS-NOT 变异位置偏移

| 项 | 记录 |
|---|---|
| 发现 | 2026-11-27，F13 预登记样本；责任 WP04，操作 Codex |
| 原始任务 | [PHASE-05 Prompt 和答复](../../transcripts/TP-PHASE-05.md) |
| 初始 AI 实现 | `5b757b9` 实现最小文本差分定位。对比 `git diff 5b757b9 8923f2c -- backend/mutation_generator.py` |
| 症状与复现 | 用 PHASE-05 冻结样本中含 identity compare 的文件生成清单。Cosmic Ray 的结果 `is → is not` 引发“变异位置与清单不一致”，整份清单拒绝 |
| 根因 | 字符串共同前缀可越过原 `is` 运算符，偏移进入空格或后继标识符 |
| 修复 | 在 operator 类型精确匹配且完整内容可复演时，把 ` not` 插入点锚定到原运算符末尾。[实现](../../backend/mutation_generator.py) |
| Git | `8aab4d6` 至 `8923f2c`，通过 `1acd2ff` 进入主线 |
| 回归 | `python -m pytest tests/test_mutation_generator.py eval/phase05/test_manifest.py -q`，历史 8 项通过。旧 bonus 清单逐项相同。[原始记录](../../reports/phase05/raw/manifest-tests.txt) |
| 沉淀 | 定位证据要同时复核运算符类型、文本回放和持久化 ID |
