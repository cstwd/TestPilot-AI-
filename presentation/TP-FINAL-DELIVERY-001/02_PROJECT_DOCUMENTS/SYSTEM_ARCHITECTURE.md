# 系统架构

| 层 | 实际实现 | 观察及边界 |
|---|---|---|
| 入口、浏览器 | `main.py`、Uvicorn、Jinja2、原生 JS 与本地静态资源 | 同源页面和 API，PyCharm 单入口 |
| API 与编排 | `backend/app.py`、`workbench.py`、`demo_lab.py` | Demo Lab 按目录索引读样本，以独立 SQLite 保存记录 |
| 静态分析与生成 | `analysis.py`、`generation.py`、`engine_flow.py`、`model_provider.py` | 静态 AST 解析，AI 经回环 Ollama/Vulkan，生成源码做静态检查 |
| 受限执行 | `runs.py`、`runner.py`、`wasi_worker.py`、`mutation_flow.py` | WASI CPython 与 Pytest，边界由运行器维护 |
| 缺陷、数据及报告 | `bugs.py`、`quality.py`、`mutation_store.py`、`database.py` | SQLite 保留版本、套件、执行、缺陷和变异链，质量报告导出 |

F02 图谱主视图展示词法包含。代码可用于讲解局部调用，如 `SignalWindow.average` 对 `mean_value` 的调用。产品图上的包含线与此源码调用示例是两种关系。

[架构图](../05_DEMO_ASSETS/architecture/04-system.svg) · [仓库架构](raw/docs/ARCHITECTURE.md) · [产品阶段验收](../04_TESTING_EVIDENCE/MUTATION_TESTING/reports/phase07/ACCEPTANCE.md)
