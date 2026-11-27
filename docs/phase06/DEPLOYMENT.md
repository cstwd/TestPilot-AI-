# PHASE-06 统一模型部署

工作包 WP01/WP03/WP04。Windows 11 上使用现有 Ollama 0.40.18、RTX 5080 Laptop Vulkan、已按发布修订校验的 Qwen3.8-27B UD-IQ3_XXS GGUF。API 费用为零。

## 从工作树启动

在项目 Python 解释器中运行 `python -m eval.phase06.serve --models E:/OllamaModels`。守护进程启动专用 Ollama `127.0.0.1:11763`，先完整读取权重验证 SHA-256，并核对固定标签清单。服务日志必须实际检测到 Vulkan 和 RTX 5080。运行 `main.py` 后访问 `/api/model/health`。接口用一次真实的 schema 推理、运行中的 GPU 分配、Ollama 版本和固定身份返回状态。F01 导入和静态分析可独立运行。AI 操作使用实时许可和请求队列。

生产默认资源配置为单推理一个槽，队列最多额外四个请求，项目请求最多 150 秒。RTX 5080 启用 Vulkan 与量化 KV，默认上下文为 4096。禁用 Ollama 随附 runner 的 prompt RAM cache 和 context checkpoints，避免重复任务保留大量 CPU 内存。Windows 物理内存和 Commit 余量需各维持 2 GiB，GPU 余量至少 512 MiB。守护进程每 0.5 秒检查，触线即关闭所管理的 Ollama 进程树。可在模型运行目录创建 STOP 文件有序关闭本实验进程。使用默认运行目录时应用与守护进程从同一工作树启动。

## 模块入口与协议

| 功能 | 调用路径 |
| --- | --- |
| F01 导入与 F04 执行 | 两者直接调用文件版本存储与 WASI，无推理。 |
| F02 / F07 静态分析 | 现有 GET 继续提供 AST 结果。POST `/api/engine/files/{id}/understanding` 调用统一 Provider，并返回冻结七字段结构、运行 ID 及响应记录。 |
| F03 / F09 生成 | F03 suite API 的显式 `ai` 与 F09 的 `configured` 均由统一 Provider 处理。JSON `code` 先过 Schema 与 AST 门，再进入实际隔离校验。 |
| F12 修复 | 仅在既有可判定条件满足时调用同一 F09。文档契约允许的规则修正仍按原接口以 `rules` 标记。 |
| F13 补测 | Provider 返回单个结构化候选或无区别输入。候选必须经原版校验，再用固定清单复跑。 |

Provider 记录每个响应原文、状态、重试次数、运行 ID、token 数、首个可见内容及后端版本。两个相邻尝试保存在同一运行 ID 下。模块级结构不符最多修复一次，连接、身份或资源失败明确返回。旧远程供应商与小模型环境变量不参与正式管线。当前源码与响应仅传到同机回环 Ollama。

[部署前审计](AUDIT.md) · [统一 Provider](../../backend/model_provider.py) · [冻结 Schema](../../backend/model_protocol.py) · [Ollama 硬件支持](https://docs.ollama.com/gpu) · [Ollama 结构化输出](https://docs.ollama.com/capabilities/structured-outputs)
