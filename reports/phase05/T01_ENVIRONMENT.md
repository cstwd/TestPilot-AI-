# T01 模型文件和本地环境

实验工作树基于 307d4bd。校验时间 2026-11-27T08:06:28.323592+00:00，读取本地文件 `D:\TestPilot AI\.runtime\tp-model-001\Qwen3.8-27B-UD-IQ3_XXS-fixed.gguf`，大小 10,934,860,608 字节。
SHA-256 为 `8e9d04d41fd6bd47787aad7919ae8594a3d7488d4adc859f6fb00ef07416526c`。与发布修订 `33a91d0e6fa53bf04accf398fde7b8ee1a1c9294` 的 LFS 摘要和长度一致。本阶段使用已有权重。
[原始逐字节校验与 GGUF 元数据](raw/audit.json) · [固定发布文件](https://huggingface.co/Jfish123/Qwen3.8-27B-16GB-GGUF/tree/33a91d0e6fa53bf04accf398fde7b8ee1a1c9294)

| 项目 | 实查值 |
| --- | --- |
| 文件与量化 | GGUF v3，866 个张量，文件类型码 23（IQ3_XXS），发布文件标记 UD，量化作者 Unsloth |
| 名称与架构 | Qwen3.8-27B，架构字段 `qwen35`，GGUF 中 65 个块；后端日志记录未用于本轮普通解码的预测头张量 |
| Tokenizer | gpt2，预分词器 qwen35，词表 248,320 |
| 环境 | Windows-11-10.0.26200-SP0，Python 3.13.11 |
| GPU／驱动 | NVIDIA GeForce RTX 5080 Laptop GPU, 592.27, 16303 MiB, 15984 MiB |
| 物理内存 | 31.42 GiB，审计时可用 7.65 GiB，提交余量 7.41 GiB |

旧 Ollama 加载日志显示 CUDA_Host 缓冲区分配失败。本轮直接使用已安装的 llama-server，通过内存映射及全层卸载成功加载相同文件。CUDA 在首个请求中遇到 PTX JIT 内存分配错误，未取得有效输出。改为显式选择 Vulkan1（RTX 5080 Laptop）后，连续推理成功。实验参数、stderr 与失败数据同时保留。未更改驱动、分页文件或系统配置。
[后端版本](raw/backend-version.txt) · [设备清单](raw/vulkan-devices.txt) · [CUDA 实测](raw/native-01/server.log) · [Vulkan 启动参数](raw/vulkan-01/launch.json) · [本机服务使用说明](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)
