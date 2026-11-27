# 技术成果与适用条件

- AST 派生符号与节点交互共享不可变文件 ID，支持从 Inspector 定位原始行号。
- Qwen3.8-27B UD-IQ3_XXS 经 Ollama/Vulkan、本机回环和结构校验。PHASE-06 有 AI 生成成功，PHASE-07 现场单样本停在资源守卫，演示使用可显式选择的课堂模板。
- Pytest 结果来自 WASI 受限流程。保存实际运行退出、节点、日志与覆盖，在新文件版本复跑同一套件。
- F13 使用真实变异执行，按会话记录杀死、存活和执行错误。冻结评测按每组 117 个登记位置复算，口径独立。
- Agent 工具链采用两项 Skill、只读 MCP、确定性 Hook 和独立 Reviewer，原生 Goal 留失败、修正和完成证据。

[工程工具链原始回执](../04_TESTING_EVIDENCE/AUTOMATED_TESTING/reports/course-final/toolchain.txt) · [历史 AI API](../04_TESTING_EVIDENCE/AI_EVALUATION/reports/phase06/raw/live.json) · [本机 AI 降级](../04_TESTING_EVIDENCE/AI_EVALUATION/reports/phase07/ai-live.json)
