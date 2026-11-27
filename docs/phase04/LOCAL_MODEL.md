# F13 本地模型配置及验收边界

F13 从回环 HTTP 地址连接 Ollama。默认端口为 11434，生成前使用模型清单和 GGUF 元数据核对模型名、摘要、本地架构和云转发标志。适配器禁用代理和 HTTP 重定向，拒绝远端 URL 及云模型。F13 的配置独立于此前阶段的供应商设置。推理日志记录实际模型、输入、原始输出、解析状态和反馈位置。[实现](../../backend/mutation_feedback.py)

| PyCharm 运行配置中的环境变量 | 用法 |
| --- | --- |
| `TESTPILOT_MUTATION_BASE_URL` | 可选。默认值为 `http://127.0.0.1:11434`，也可使用其他回环地址与端口。 |
| `TESTPILOT_MUTATION_MODEL` | 可选。填写 `ollama list` 已登记的本地 GGUF 模型名称。本机验收为 `qwen2.5-coder:0.5b`。缺省时优先探测该轻量编码模型，然后探测本机已有候选。 |
| `TESTPILOT_MUTATION_TIMEOUT` | 可选。反馈时间预算 1–180 秒，默认 120 秒。每条模型调用前检查取消信号及剩余时间，未处理的位置可查。 |

本机首次模型清单为空。已有 27.3B/IQ3_XXS 权重经本地 blob 注册成功；三次实际加载分别因 CUDA 设备缓冲或 CUDA Host 缓冲分配失败。随后从官方 Ollama 仓库下载约 398 MB 的 `qwen2.5-coder:0.5b`，模型清单摘要为 `4ff64a7f502a08b7616edb8ca0a79eb1853fc363d842b7df4b46915d11a3fb09`。下载是一次性的，本次测试生成与模型反馈均在本机处理。[模型信息](https://ollama.com/library/qwen2.5-coder:0.5b)

每次请求聚焦一个实际存活变异，包含原函数契约或函数体、测试数量及类型检查摘要、变异行号与改动。简单整数和布尔条件会附上一个由静态谓词比较推导的候选输入。模型选择实际调用、给出预期和解释；程序校验字面量和函数绑定，再将用例追加到原测试。模型的归因和预期仍须经过原版与变异版的实跑核对。小模型可能给出错误类型、错误异常或不能区分变异的输入。[模块测试](../../tests/test_mutation_feedback.py)

实际探测对去除异常、布尔替换、比较边界三处变异先用原套件实跑，三处均存活。带嵌套 schema 的尝试超时；短 JSON 最初复制了旧测试的局部导入名；随后一次生成的普通输入能通过原版但三个变异仍然存活。最终探测保留每次模型输出和单项 WASI 结果。探针只涵盖这三个位置，阶段总分另由完整清单核算。[首次超时](../../reports/phase04/local-model-schema-timeout.json) · [别名拒绝](../../reports/phase04/local-model-alias-rejections.json) · [未产生增益的补测](../../reports/phase04/local-model-nondiscriminating.json) · [最终探针](../../reports/phase04/local-model-probe.json)
