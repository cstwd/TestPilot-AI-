# PHASE-04 开发前工程审计

2026-11-27，Windows 11 项目目录 `D:\TestPilot AI`。责任人陈帅廷，实际检查由 Codex 执行。开工 HEAD 为 `c9737be`，PHASE-03 验收归档 `7422857` 位于祖先链。工作区另有 AST 可视化前端及本地模型任务在进行；本次按文件提交。

| 实查项目 | 观察与接口决定 |
| --- | --- |
| F07/F08 | `engine_analyzer.analyze_source` 提供函数范围、源码摘要、文档实例和静态控制流；`engine_strategy.build_strategy` 区分独立预期与待确认假设。F13 以原任务选定函数作为变异范围。 |
| F09/F12 | `GeneratedTest` 内保留生成代码、生成方式和 SHA-256，F12 的 TestExecution 对应实际 generated_test_id。F13 使用原任务最终实际执行的测试版本，补充测试另存。 |
| F10 | `backend.runner.execute(source, code, detailed=True)` 使用独立临时目录、一个受限 WASI worker、只读挂载、禁网和禁进程、256 MiB 线性内存、每路 256 KiB 输出、来宾与宿主时限。 |
| F11 / Coverage | Pytest 钩子记录节点、阶段、异常、traceback 与完整性，不能只按退出码判断杀死。Coverage.py 7.17.5 测行、分支；覆盖率与变异得分各有自己的分母。 |
| 运行环境 | 项目解释器 CPython 3.13.11，pytest 9.2.0，wasi-python 0.1.6，wasmtime 51.0.0，FastAPI 0.165.0。 |
| SQLite | 只读查询 sqlite_master 确认 app_metadata、projects、files、suites、runs、bugs、regressions、engine_tasks、engine_records 共九张表。本阶段的新会话引用旧证据 ID。 |
| 本地模型 | Phase-03 归档显示当时 Ollama 返回空清单。盘点时已有独立任务记录本机 GGUF 下载完成；模型名称、可推理性与测试补充效果须经本阶段真实本机调用确认。 |
| 测试基线 | PHASE-03 的 platform-junit.xml 有 89 个节点。当前工作树 `pytest --collect-only -q` 实收 96 项，含后续可视化工作。保留历史用例和报告，回归按原 89 个节点核对。 |

[PHASE-03 归档](../../TP_PHASE_03_ACCEPTANCE.md) · [原始测试结果](../../reports/phase03/platform-junit.xml) · [执行器安全边界](../phase03/SANDBOX.md)
