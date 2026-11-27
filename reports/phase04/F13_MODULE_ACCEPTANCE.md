# F13 Mutation Testing Engine 模块验收

阶段负责人陈帅廷，实际操作者 Codex。工作目录 `D:\TestPilot AI`，验收使用 Windows 11 项目解释器、真实本机服务、Ollama 及 WASI Pytest。

| 范围 | 可复核结果 | 实现及证据 |
| --- | --- | --- |
| F13-01 生成 | 对选定函数冻结一级变异清单，每处包含 UUID、行列、算子、文本编辑及 SHA-256；演示文件产生六个家族共九项。 | [生成器](../../backend/mutation_generator.py) · [算子报告](MUTATION_OPERATORS.md) · `5b757b9` |
| F13-02 执行 | 逐个建立独立临时副本，调用 F10。记录退出码、日志、节点、覆盖率及两个输入摘要。支持终止活动 worker、处理排队、重启后按检查点继续。 | [流程](../../backend/mutation_flow.py) · [取消和恢复实测](lifecycle.txt) · `6de6844` / `f6daaa1` |
| F13-03 判读 | 要求原版绿色、收集一致、失败节点具有测试侧断言证据。超时、错误和中止各有独立类别。异常抑制由真实 Pytest 的预期异常未发生证据判定。 | [判读代码](../../backend/mutation_results.py) · [真实故障与超时实测](results-test.txt) |
| F13-04 计分 | 固定分母包含整个清单，待执行、超时、错误、等价候选也计入总数。零位置或无有效基线时分数为 null。报告给出改进前后完整统计。 | [分数及逐位置表](MUTATION_SCORE.md) · [独立核算脚本](../../eval/phase04/check_experiment.py) |
| F13-05 本地反馈 | 针对实际存活位置请求已安装的本地 GGUF。原版运行验证候选，保留被拒记录，追加有效测试，完整重放原清单。已分别用 AI 初始套件和模板初始套件复验。 | [反馈报告](AI_FEEDBACK.md) · [适配器](../../backend/mutation_feedback.py) · [原版校准独测](selection-test.txt) · `5be8d12` / `f6daaa1` |
| 工作台与导出 | 从 F12 任务创建/运行会话，页面查看候选、基线及每处结论，下载完整 JSON。Edge 验证页面创建、执行、下载及失败状态。 | [同源接口](../../backend/mutation_web.py) · [浏览器验收代码](../../tests/test_mutation_ui.py) |

## 复验

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_mutation_generator.py tests/test_mutation_results.py -q -s
.\.venv\Scripts\python.exe -m pytest tests/test_mutation_selection.py tests/test_mutation_feedback.py tests/test_mutation_initial_profile.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_mutation_lifecycle.py tests/test_mutation_ui.py tests/test_mutation_flow.py -q
.\.venv\Scripts\python.exe -m eval.phase04.ai_initial_campaign
```

最后一条命令需要本机 Ollama 中已安装的验收模型。完整任务、实验 JSON 和精确命令随[阶段报告](../../TP_PHASE_04_ACCEPTANCE.md)归档。尚待陈帅廷人工签收。当前仅以静态规则标记等价候选；任意 Python 程序的语义等价性仍需人工分析。

最终代码上的 47 个 F13 测试全部通过，连同旧版及工作台共 146 项通过。复核添加了通过真实执行辨认 `pytest.raises` 别名的检查，提交 `8607ffa`。完整回归证据提交 `38dd0bc`。[别名导入的实测输出](assertion-alias.txt) · [最终 JUnit](final-junit.xml)
