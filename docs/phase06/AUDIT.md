# PHASE-06 迁移前审计

起点为主分支提交 `7c796e7`。主工作区另有执行中心开发。独立工作树保留 `307d4bd` 的祖先关系；PHASE-05 位于独立分支 `experiment/tp-phase-05` 和归档 `8923f2c`。WP01 负责集成，WP03 负责模型评测，WP04 负责执行与资源边界，实际操作 Codex。

| 入口 | 审计发现 |
| --- | --- |
| F01、F02、F04 | 导入、AST、Pytest/WASI 均为确定性操作。F02 与 F07 的静态分析可独立使用。 |
| F03 | 旧 suite API 只注册显式模板。新工作台的配置生成接入 F09 任务。 |
| F09、F12 | `engine_llm.py` 可按环境变量选择供应商、模型、远程 HTTPS、API key，直接调用推理。F12 可复用 F09，也有基于文档契约的显式规则修正。 |
| F13 | `mutation_feedback.py` 直接调用 Ollama，优先 0.5B，并可枚举本机其他模型。原版候选校验和隔离复跑在 F13 流程层。 |
| MCP 与 Agent 目录 | 当前提交仅有占位文件。 |

已安装的 Ollama 清单只接受固定标签 `hf.co/Jfish123/Qwen3.8-27B-16GB-GGUF:latest`，清单 SHA-256 为 `a9d632842caa805667b010be2b685525a3f8c8fd363988dcda9e80ce334fcfc7`，权重层 SHA-256 为 `8e9d04d41fd6bd47787aad7919ae8594a3d7488d4adc859f6fb00ef07416526c`。先前实际成功的 27B Vulkan 运行使用 Ollama 随附的独立 llama-server，历史峰值物理内存达 31.42 GiB。本阶段须实测 Ollama 管理 API 下的加载和资源余量。初次盘点物理内存空余 12.82 GiB、Windows Commit 余量 17.60 GiB，RTX 5080 Laptop 报告 16,303 MiB 总显存。
