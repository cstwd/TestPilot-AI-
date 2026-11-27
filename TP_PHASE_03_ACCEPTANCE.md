# TP-PHASE-03 · AI Testing Engine 正式验收报告

**工程实现及离线闭环通过；真实模型成功推理待验。** 2026-11-27 在 Windows 11 项目 `D:\TestPilot AI` 完成 F07–F12 实施、独立测试、交叉审查和完整回归。**89 项平台测试全部通过**，用时 245.44 秒。按 PHASE-02 基线测试文件核对 JUnit，原有 35 项和新增 54 项均执行，平台测试失败、错误、跳过均为零。实际来宾运行的失败和跳过另记录在每次任务中。[逐项回归日志](reports/phase03/full-suite.txt) · [JUnit 记录](reports/phase03/platform-junit.xml)

本机 Ollama 返回 HTTP 200 和空模型列表。一次真实请求将负数评测源码及策略发送给本机已配置探测地址，请求的模型未安装，返回 HTTP 404。引擎记录原因并回退到 `template`，实际 Pytest 为 5 通过、1 失败、1 跳过。当前证据覆盖两种供应商协议、真实端点失败和降级；尚未取得真实模型生成成功或模型反馈修正成功的验收样本。[真实服务记录](reports/phase03/ollama-probe.json) · [模型配置与复查方法](docs/phase03/MODELS.md)

## 架构、保护与实际入口

开发前只读盘点确认基线 `da798a4` 和 `f31a901`、SQLite 版本 1 的七张表、实际安装的依赖版本及 35 项测试清单。阶段审计和接口先以 `9f107cb` 提交，再按 F07–F12 建立模块。新任务使用两张独立表，按文件修订串联 UUID、UTC 时间、状态与前序事件；持久化前校验八类数据模型和最终报告的执行引用。原测试文件、PHASE-01/02 验收报告与证据、根入口及共享 PyCharm 配置均已与基线核对。[开发前审计](docs/phase03/AUDIT.md) · [接口与数据契约](docs/phase03/INTERFACES.md) · [模型定义](backend/engine_models.py) · [事务历史](backend/engine_history.py)

PyCharm 直接运行根目录 `main.py`，在仪表盘点击 **打开智能测试引擎**。从 F01 导入文件后，选版本、函数、生成模式和反馈上限，提交即可查看历史、下载测试文件及完整 JSON。实际 Edge 验证了页面交互和下载；根入口的端口冲突、重启、SQLite 和旧六页面均参加统一回归。另用本机 PyCharm 自带的 pydevd 命中 `backend/app.py:24`，继续执行后开发模式与数据库均正常。[使用指南](README.md) · [浏览器及 HTTP 测试](tests/test_phase03_api.py) · [断点实测](reports/phase03/debug.txt)

## 模块签收范围

| 模块 | 实测能力与证据 | 实现及复核提交 |
| --- | --- | --- |
| [F07 Code Analyzer](F07_MODULE_ACCEPTANCE.md) | 符号和签名、返回及异常、控制流、静态依赖、文档契约、可测入口、编码和语法诊断 | `643b0ca` |
| [F08 Test Strategy](F08_MODULE_ACCEPTANCE.md) | 生成带类型、目的、输入、预期和依据的策略；对缺少明确契约的行为保留待核对标记 | `36a76f7` |
| [F09 AI Test Generation](F09_MODULE_ACCEPTANCE.md) | Ollama 原生与 OpenAI 兼容 HTTP、配置、超时、重试、测试结构校验、请求证据及降级；真实模型成功路径待验 | `c370d42`、`ab954d0` |
| [F10 Sandbox Execution](F10_MODULE_ACCEPTANCE.md) | 真实 WASI Pytest、独立进程、只读挂载、权限限额、超时清理、逐例异常、双路输出、行和分支覆盖 | `d551a2d` |
| [F11 Failure Analysis](F11_MODULE_ACCEPTANCE.md) | 核对 traceback 和断言差异，区分文档契约违例、测试自身错误、环境与未决项；定位分为真实栈帧与候选函数入口 | `eb931c8`、`6bc372f` |
| [F12 Feedback & Repair](F12_MODULE_ACCEPTANCE.md) | 在原文档支持时局部修正生成测试，保存初末证据、拒绝重复与弱化候选，原始源码摘要保持一致 | `f4de268` |

任务记录基础提交 `805ec36`；同源工作台、七个样例及其验收集成提交 **`978323d`**。团队实际操作、审查分工、额外并行提交归属均单独记录。本阶段负责人陈帅廷。此报告供负责人审核，未代签其他成员。[协作记录](collab-log/PHASE_03.md) · [独立审查](reports/phase03/REVIEW.md) · [工程问题及修正](collab-log/bugs/PHASE_03.md)

## 端到端、覆盖率与修正

| 验收问题 | 实际结论 |
| --- | --- |
| 能否对真实源码完成闭环 | 通过 HTTP 导入六个要求的项目和一个额外修正项目。七项端到端验收通过，用时 55.20 秒；八次来宾执行与 54 条事件均可回读。 |
| 能否发现预置程序缺陷 | 负数、空输入、上界、异常处理四种缺陷均有明确文档契约和真实失败节点；正确的快速排序和多分支分类通过。空输入还有一条缺少独立预期的失败，保留未决。 |
| 能否修正错误测试 | 模板把 `reciprocal_units(0)` 误写为返回整数；系统改成文档要求的 `pytest.raises(ValueError)`。在同一份源码上由 4 通过、1 失败、1 跳过变为 5 通过、0 失败、1 跳过。 |
| 覆盖率能否复查 | 六个指定项目的最终执行累计 30/31 行、13/14 个分支出口。加上修正项目为 34/35 行、15/16 个分支出口。覆盖 JSON 与对应执行 ID 关联。 |

[七个任务摘要和原始 JSON 索引](reports/phase03/E2E.md) · [完整修正案例](reports/phase03/cases/repair.json) · [覆盖率报告](reports/phase03/COVERAGE.md) · [沙箱设计及其边界](docs/phase03/SANDBOX.md)

## 复验与未完成事项

从项目根目录使用现有解释器可运行以下命令。第一条跑全部平台用例，第二条只跑端到端基准。样例显式选择本地模板，避免供应商配置影响对照。测试任务默认使用临时数据库。

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
.\.venv\Scripts\python.exe -m pytest tests/test_phase03_e2e.py -q -s
```

全量归档使用 Coverage.py 包裹第一条命令，并指定 `--durations=8 --junitxml=reports/phase03/platform-junit.xml`。独立 WASI、浏览器和调试实测均保留真实输出。[平台覆盖明细](reports/phase03/platform-coverage.json) · [全套输出](reports/phase03/full-suite.txt)

在受测集成提交 `978323d` 上另行复验 `tests/test_phase03_api.py`，真实 Edge 与 HTTP 共 **2 passed in 10.69s**。[工作台复验输出](reports/phase03/workbench.txt)

- 真模型后续验收需可响应的模型名和服务。按配置文档运行同一样例，核对 `GeneratedTest.mode=ai`、模型标识、测试源码、执行 ID 和真实 Pytest 记录；如触发可核验的测试错误，再核对模型修正候选与重跑。
- 自动生成当前限于可独立分析的顶层同步函数。类、方法与异步函数可静态分析；动态调用和缺乏独立契约的业务预期需要人工核对。
- 当前来宾中的 Hypothesis 属性用例保留显式跳过。样例统计按实际 Pytest 结果计，失败与跳过详情均可回读。
- 真实模型验收与负责人最终人工签收均保持待办。
