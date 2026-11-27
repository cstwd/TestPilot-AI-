# 测试与离线评测

| 层级 | 验证对象及入口 | 证据 |
|---|---|---|
| 单元与属性 | AST、版本摘要、生成结构、变异定位与计分，项目解释器运行 Pytest | [测试目录](../tests/) |
| API 与集成 | `main.py` 启动临时服务，导入缺陷版与修复版，运行原套件和原失败节点，下载报告 | [端到端用例](../tests/test_phase02_flow.py) |
| Edge | Dashboard、F01–F06、AST 工作台、F13 导出 | [业务 UI 用例](../tests/ui_workbench.py) · [F13 用例](../tests/test_mutation_ui.py) |
| 实际执行 | 项目和变异代码使用 Wasmtime 中的 WASI CPython 与 Pytest，结果记录退出码和完整性 | [执行器测试](../tests/test_runner.py) |
| 差分 | 缺陷版与修复版、原版与变异版、模板与本机模型在相同位置比较 | [F13 生命周期](../tests/test_mutation_lifecycle.py) · [四组报告](../reports/phase05/T04_COMPARISON.md) |
| 评测复算 | 每组 10 项目 × 3 种子 × 共 39 个位置／种子 = 117，历史原始数据保持冻结 | [协议](../eval/phase05/PROTOCOL.md) · [逐次结果](../reports/phase05/campaigns.csv) |

`python hooks/verify.py --scope full --report reports/course-final/verify-full.txt` 同时执行平台 Pytest、冻结清单回归和前端 Node 测试。宿主属性测试只处理 AST 数据，来宾 Hypothesis 的原生扩展仍需另行兼容，适用建议记录在套件中。

历史推理和冻结评测生成脚本引用当时的 `backend.local_ollama`。现场重跑从 `8923f2c` 的工作树进入，按[原流程](../eval/phase05/README.md)设置本机权重。主线只读复算可导入 `eval.phase05.aggregate` 的 `cases` 和 `summarize` 来比较已归档的 `groups`。直接调用聚合模块的命令行会重写汇总文件，应在隔离副本中执行。主线真实推理使用 [PHASE-06 固定 Provider](phase06/DEPLOYMENT.md)。

[10/10 稳定性、TTFT、吞吐与内存](../reports/phase05/T01_PERFORMANCE.md) · [严格结构评估 56/70](../reports/phase05/T02_SOURCE_UNDERSTANDING.md) · [生成质量](../reports/phase05/T03_TEST_GENERATION.md) · [原始反馈与选择](../reports/phase05/T05_MUTATION_FEEDBACK.md)
