# 测试生成模型配置

PyCharm 的 Run/Debug 配置可以给同一 `main.py` 入口设置下列环境变量。默认由本地模板生成用例。显式选择模型后，服务会把选定源码、目标、分析、策略以及该次修复的上一版测试和反馈发送给指定端点。先确认项目允许把这些输入交给该提供方。

| 变量 | 含义 |
| --- | --- |
| `TESTPILOT_MODEL_PROVIDER` | `ollama` 或 `openai-compatible`（别名 `openai`）。`template` 强制本地模板。 |
| `TESTPILOT_MODEL_NAME` | 推理端已安装或已授权的模型标识。 |
| `TESTPILOT_MODEL_BASE_URL` | Ollama 默认 `http://127.0.0.1:11434`。OpenAI 兼容服务填写其 API 基础地址，通常包含 `/v1`。 |
| `TESTPILOT_MODEL_API_KEY` | 提供方要求时传入 Bearer 令牌。只在本机私有环境配置。 |
| `TESTPILOT_MODEL_TIMEOUT` | 单次 HTTP 套接字超时秒数，范围 1–120，默认 30。 |
| `TESTPILOT_MODEL_RETRIES` | 首次请求失败后的重试次数，范围 0–2，默认 1。 |

例如选用本机已安装的 Ollama 模型时，将 PROVIDER 设为 `ollama`，NAME 设为 `ollama list` 实际列出的名称。兼容服务须支持 Chat Completions 的消息结构。Ollama 使用原生 `POST /api/chat`；兼容服务会在所配基础地址追加 `/chat/completions`。远端使用 HTTPS，本机回环地址支持 HTTP。客户端直接连接指定地址并拒绝跳转。[Ollama 请求格式](https://docs.ollama.com/api/chat) · [Chat Completions 消息结构](https://developers.openai.com/api/reference/resources/chat)

## 结果与复核

- `ai` 表示模型返回的 Python 测试通过了语法与结构检查。检查会拒绝空测试、无有效断言的测试、重复用例名，以及没有引用并调用目标函数的候选模块。业务断言正确性和测试执行结果另由实际运行及评审判读。
- `template` 表示由既有模板提供源码。未配置提供方、模型不可用或候选未通过检查时，返回实际降级原因。尝试记录保留所用提供方、模型、消息、诊断和失败输出片段，便于核查。令牌通过请求头传递。
- 每个生成包保存规范化源码与 SHA-256。初次生成失败且模板也无法处理时，`GenerationFailure.evidence` 保留两条路径的失败信息与已发生的尝试，代码及摘要为空。任务历史中可能含有提交的源码和反馈，请按源项目的可见范围管理。
- 协议测试采用本机 HTTP 测试替身，分别检查两种提供方的请求、响应、重试、降级与重定向。固定样例另经真实 WASI Pytest 验证；模型推理及其生成物的真实结果应以对应的运行证据为准。[模块测试](../../tests/test_f09.py) · [验收输出](../../reports/phase03/F09.txt)
