# PHASE-03 独立工程复核

2026-11-27，本阶段负责人陈帅廷。质量验证与归档分别对应既有工作包 WP04、WP05，实际操作与复核为 Codex。以下记录覆盖在共享工作树查看的实现和独立运行。模型适配器 F09 由编写者完成独测，主代理另行审查。

| 范围 | 审查方法与观察 | 复核结果 |
| --- | --- | --- |
| F07 → F08 | 检查静态分析的范围、位置、函数签名、嵌套定义、doctest 和输入编码，复跑合法、无效及不可独立测试的样例。策略引用同一源码摘要与契约 ID，将已知预期和需人工确认的输入区分。 | `tests/test_f07.py tests/test_f08.py tests/test_engine_history.py` 初轮共 17 项通过。 |
| F08 → F09 | 用带 `# doctest: +SKIP` 的示例复现了策略忽略此契约、模板仍生成断言的问题。PHASE-03 模板现显式遵守示例指令，PHASE-02 旧调用方式继续使用原默认行为。 | 跨模块测试覆盖 `tests/test_f03.py`、F07、F08、F09 和历史记录，31 项通过。 |
| 八种事件与 SQLite 历史 | 检查 UUID、UTC 时间、必需 payload 字段、写事务串行化和终态报告提交。补查最终报告对执行的引用，原实现仅校验字符串类型。现在归档时要求引用属于本任务且类型为 TestExecution，未产生执行的错误报告仍可空引用。跨任务、错误类型及终态回滚均用真实 SQLite 验证。 | 新测试首次因夹具缺少新字段 `result_complete` 失败，补齐夹具后独立复跑 2 项通过。 |

跨模块原始测试输出保存在 [cross-module-review.txt](cross-module-review.txt)。F09 协议测试使用本机 HTTP 替身，其输出与真实 WASI Pytest 验证分别记录在 [F09.txt](F09.txt)。

## F10 运行和覆盖证据

复核 `backend/runner.py`、`backend/wasi_worker.py`、`backend/guest_pytest.py`。详细模式延用已隔离的固定 Pytest 命令；它分别采集两路输出、异常类型和现场帧，并从 Coverage.py branch_stats 取得分支分子、分母。超时记录保留输出及诊断，测试数与覆盖计数为空。完整个案以实际 pytest 钩子和完成记录为依据。

独立运行 `.venv/Scripts/python -m pytest tests/test_f10.py -q` 得到 **3 passed in 19.39s**。真实 guest 的断言、类型异常、收集错误及超时均经过复验。示例行覆盖 3/4，分支覆盖 1/2，两个百分比各自使用对应的可测分母。[模块明细](F10.txt)

## F11 失败归属

审查 `backend/engine_failures.py` 并独立运行 `.venv/Scripts/python -m pytest tests/test_f11.py -q`，得到 **6 passed in 15.90s**。实测涵盖缺陷、错误预期、未确定、跳过及超时。分析使用真实失败节点、回溯帧与独立 doctest 契约；没有匹配契约或导入绑定不清楚时保留未确定。已向集成负责人提交有状态目标的归因边界，需复核测试函数中较早调用是否改变了受检断言的前置状态。[模块明细](F11.txt)

## F12 反馈与回归

检查 `backend/engine_feedback.py` 对失败节点、局部 AST、更改前后摘要的检查，以及 `backend/engine_flow.py` 记录初末执行、回归上限、重复候选和终止原因的事务路径。独立执行 `.venv/Scripts/python -m pytest tests/test_f12.py -q` 得到 **4 passed in 15.16s**。端到端反馈样例在真实来宾中先失败、后通过，两版测试和执行关联到同一份源码；重复候选和非法弱化的拒绝另外用测试替身检查。首次审查发现未定义辅助函数的替换缺乏独立语义依据，已提交负责人。[模块明细](F12.txt)

## 审查发现的修正复验

F11 现仅用独立的单条测试语句匹配 doctest 归属；有前置调用的真实状态样例保留为未确定。F12 已移除缺少独立契约时替换未定义被调用名的路径；`assert f(2) == oracle(2)` 会保留原始失败供复核。独立联合复验命令 `.venv/Scripts/python -m pytest tests/test_f11.py tests/test_f12.py -q`，**12 passed in 32.54s**。本次独立审查报告的四处问题均已修正并获得针对性复验证据。
