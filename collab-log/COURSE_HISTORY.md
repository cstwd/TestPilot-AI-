# 五人历史工作记录

全部历史条目发生于 2026-11-27（UTC+8）。每行按课程责任归档。实际工程操作和验证来自 Codex 的主代理或原会话代理，个人签收待补。模型列若为“Codex”且原记录未载模型版本，版本保留为未记录。各行的原始 Prompt 链接同时包含可取得的关键可见答复，模型输入输出另有原始 JSON。

## WP01 陈帅廷

| 编号与主题 | 工具和模型 · 原始 Prompt | 目标、操作及关键输出 | 验收、提交与成果 | 经验 |
|---|---|---|---|---|
| 01 立项与入口 | Codex、PyCharm、Git · [立项](../transcripts/TP-PHASE-01.md) | 把样例脚本扩展成同源服务，配置默认浏览器和数据库探测 | `8038be2`, `88ebf23` · [Run/Debug](../TP_PHASE_01_ACCEPTANCE.md) | 共用入口便于断点和发布复验 |
| 02 核心集成 | Codex、FastAPI、SQLite · [PHASE-02](../transcripts/TP-PHASE-02.md) | 串联不可变版本、初次执行、原失败节点和报告 | `f31a901`, `da798a4` · [真实缺陷到回归](../reports/phase02/e2e.txt) | 用版本与运行 ID 避免证据串用 |
| 03 本机部署 | Codex、Ollama、Vulkan、27B · [部署](../transcripts/TP-MODEL-002.md) · [PHASE-05](../transcripts/TP-PHASE-05.md) | 使用现存权重，验证摘要，并在 CUDA 资源错误后使用 Vulkan | `8923f2c` · [10/10 连续有效响应](../reports/phase05/T01_PERFORMANCE.md) | 分开记录冷首轮与热请求 |
| 04 统一模型 | Codex、Ollama、Qwen3.8-27B · [PHASE-06](../transcripts/TP-PHASE-06.md) | 固定模型、权重身份和回环连接，增加队列及资源守卫 | `98adf18`, `0ddc083`, `646ef7d` · [部署与路径](../docs/phase06/DEPLOYMENT.md) | UI 就绪要关联实际进程 |

## WP02 陈万策

| 编号与主题 | 工具和模型 · 原始 Prompt | 目标、操作及关键输出 | 验收、提交与成果 | 经验 |
|---|---|---|---|---|
| 05 需求与视觉研究 | Codex、Edge · [原始问答](../transcripts/requirements-interview.md) · [前端研究](../transcripts/TESTPILOT-FRONTEND-REFERENCE-001.md) | 根据同源工作台约束提取页面布局与组件设计 | `d937d4b` · [设计与页面映射](../docs/TESTPILOT-FRONTEND-REFERENCE-001/) | 保留来源截图和实际产品截图 |
| 06 F01 项目与版本 | Codex、Edge、Playwright · [F01](../transcripts/WP04-F01-001.md) | 建项目中心、可浏览版本和共用 Studio 样式 | `9f048d0` · [桌面、平板、手机验收](../reports/WP04-F01-001/F01_BROWSER_ACCEPTANCE.md) | 窄屏按操作链分区 |
| 07 F03 工作台 | Codex、Edge、Jinja2 · [F03](../transcripts/WP05-F03-001.md) | 提供准备、源码审阅、失败、重试和运行导航 | `7c796e7` · [9 项回归](../reports/WP05-F03-001/F03_REGRESSION_REPORT.md) | 源码区与目标输入分别命名 |
| 08 F04–F06 交互 | Codex、Edge、Playwright · [F04](../transcripts/WP06-F04-001.md) · [F05](../transcripts/WP07-F05-001.md) · [F06](../transcripts/WP08-F06-001.md) | 展示运行节点、日志、失败版本差异、确认回归和质量对照 | `9fdfa7e`, `c49dde2`, `b7a8b40` · [F04](../reports/WP06-F04-001/F04_BROWSER_ACCEPTANCE.md) · [F05](../reports/WP07-F05-001/F05_BROWSER_ACCEPTANCE.md) · [F06](../reports/WP08-F06-001/F06_BROWSER_ACCEPTANCE.md) | 注入状态证据单独标记 |

## WP03 赵君豪

| 编号与主题 | 工具和模型 · 原始 Prompt | 目标、操作及关键输出 | 验收、提交与成果 | 经验 |
|---|---|---|---|---|
| 09 AST 与位置 | Codex、Python AST、Edge · [核心引擎](../transcripts/TP-PHASE-02.md) · [AST Studio](../transcripts/WP03-AST-VISUAL-001.md) | 识别函数、类和行段，节点与只读源码联动 | `743e24f`, `7f724d0`, `c9737be` · [浏览器和性能](../reports/WP03-AST-VISUAL-001/) | 分清推定入口和精确回溯帧 |
| 10 AST 动画与响应 | Codex、Edge、Playwright · [原 Prompt](../transcripts/WP03-AST-VISUAL-REFINE-001.md) | 支持渐进布局、暂停、回放和窄屏检查 | `76bd9e0` · [交互验收](../reports/WP03-AST-VISUAL-REFINE-001/ANIMATION_ACCEPTANCE.md) | 还需在真实设备检查动画表现 |
| 11 生成与试跑 | Codex、模板、WASI/Pytest · [F07–F12](../transcripts/TP-PHASE-03.md) | 明确断言来源，保存源摘要，修正一条有独立契约的错误用例 | `36a76f7`, `f4de268`, `978323d` · [七项目实测](../reports/phase03/E2E.md) | 分开记录生成错误和源程序缺陷 |
| 12 结构化评估 | Codex、Qwen3.8-27B、WASI · [PHASE-05](../transcripts/TP-PHASE-05.md) | 冻结 10 个项目七字段并保留每个响应 | `8923f2c` · [严格 56/70](../reports/phase05/T02_SOURCE_UNDERSTANDING.md) | 语义正确不能替代格式评分 |

## WP04 马雪朋

| 编号与主题 | 工具和模型 · 原始 Prompt | 目标、操作及关键输出 | 验收、提交与成果 | 经验 |
|---|---|---|---|---|
| 13 受限执行 | Codex、Wasmtime、WASI/Pytest · [PHASE-02](../transcripts/TP-PHASE-02.md) | 限制受测代码文件、网络、子进程、时间和输出 | `d988ecc`, `d551a2d` · [执行器报告](../F04_MODULE_ACCEPTANCE.md) | 日志截断须影响证据完整性 |
| 14 缺陷与质量 | Codex、SQLite、Pytest · [PHASE-02](../transcripts/TP-PHASE-02.md) | 从真实节点确认缺陷，修复版重跑并报告核对 | `b6f4ef5`, `c874456` · [修复前](../reports/phase02/buggy-report.json) · [修复后](../reports/phase02/fixed-report.json) | 修复必须保留首次失败证据 |
| 15 F13 算子与计分 | Codex、Cosmic Ray、WASI · [F13](../transcripts/TP-PHASE-04.md) | 复验六类算子、原版门禁、终止及固定分母 | `5b757b9`, `6de6844`, `307d4bd` · [F13 验收](../reports/phase04/F13_MODULE_ACCEPTANCE.md) | 未运行项仍占分母 |
| 16 AI 补测对照 | Codex、0.5B、Qwen3.8-27B · [PHASE-05](../transcripts/TP-PHASE-05.md) | 原版拒绝错误候选，按相同清单逐项复跑 | `5be8d12`, `8923f2c` · [0/81/104/105](../reports/phase05/T04_COMPARISON.md) | 本批补测只增加一个实际检出 |

## WP05 王选中

| 编号与主题 | 工具和模型 · 原始 Prompt | 目标、操作及关键输出 | 验收、提交与成果 | 经验 |
|---|---|---|---|---|
| 17 规范和职责 | Codex、Git、PyCharm · [PHASE-01](../transcripts/TP-PHASE-01.md) | 建 AGENTS、风险和任务分配，校对启动证据 | `88ebf23`, `93f7a18` · [工作包](../docs/work-packages/) | 实际执行与课程份额分开 |
| 18 阶段发布 | Codex、Git、Pytest · [PHASE-02](../transcripts/TP-PHASE-02.md) · [PHASE-03](../transcripts/TP-PHASE-03.md) | 保存各模块验收、Git 发版回执和阶段回归 | `894e7d4`, `da798a4`, `7422857` · [归档索引](../docs/COURSE_EVIDENCE_INDEX.md) | 用真实报告支持阶段声明 |
| 19 冻结评测入库 | Codex、Git、Python · [课程任务](../transcripts/TP-COURSE-FINAL-001.md) | 合入历史分支与全部原始数据，按归档分组只读复算 | `1acd2ff` · [冻结语料](../eval/phase05/frozen.json) · [原始数据](../reports/phase05/raw/) | 保留旧提交可复现现场实验 |
| 20 课程工具与交付 | Codex（主代理和 Reviewer）、Git、Edge · [课程任务](../transcripts/TP-COURSE-FINAL-001.md) | 编写两个 Skill、MCP、Hook 和循环记录，整理演示与验收 | [当前课程提交](../docs/COURSE_FINAL_REPORT.md) · [工具证据](../reports/course-final/TOOLCHAIN.md) | 用实际通过和失败的输出证明工具行为 |

## 历史摘要与个人明细对照

上方 01–20 为原课程摘要。下方逐条链接个人日志，标为“新增”的条目从阶段报告、实际会话及 Git 补录。时间按原始会话或主要提交（UTC+8）组织，共享的阶段验收数量在相关工作包复用。

本次核对了本地和远程跟踪分支的全部可达提交。PHASE-05 实验分支 `8923f2c` 和 PHASE-06 集成分支 `74ba1b4` 对应已合入的课程证据；`git diff 8923f2c HEAD -- eval/phase05/frozen.json reports/phase05/raw` 输出为空。另核对 `integration/tp-phase-07` 的 `550dcb2`、`fc417d8` 和 `integration/tp-crud-001` 的 `820ba76`，其报告在各自分支，属于课程基线之后的独立工作。WP09 已以 `d872fa1` 提交，详见 [全站终验](../reports/WP09-001/FRONTEND_V1_FINAL_ACCEPTANCE.md)。

### WP01 陈帅廷

| 原摘要 | 已恢复的操作记录 |
| --- | --- |
| 01 | [立项并确定单机技术路线](members/陈帅廷_WP01_个人操作日志.md#wp01-01) |
| 01 | [实现 FastAPI 根入口、SQLite 生命周期与原生 Run/Debug](members/陈帅廷_WP01_个人操作日志.md#wp01-02) |
| 02 | [实现项目、事务与不可变源码版本](members/陈帅廷_WP01_个人操作日志.md#wp01-03) |
| 02 | [集成生成、真实首跑、原节点回归和质量报告](members/陈帅廷_WP01_个人操作日志.md#wp01-04) |
| 新增 | [集成智能引擎任务、模型适配和 SQLite 证据链](members/陈帅廷_WP01_个人操作日志.md#wp01-05) |
| 新增 | [集成变异会话、检查点和完整导出](members/陈帅廷_WP01_个人操作日志.md#wp01-06) |
| 03 | [核验 27B 权重、诊断 CUDA 并验证 Vulkan 推理](members/陈帅廷_WP01_个人操作日志.md#wp01-07) |
| 04 | [迁移统一模型 Provider 并建立健康、资源和恢复验证](members/陈帅廷_WP01_个人操作日志.md#wp01-08) |
| 04 | [合入阶段验收并记录最终上线边界](members/陈帅廷_WP01_个人操作日志.md#wp01-09) |

### WP02 陈万策

| 原摘要 | 已恢复的操作记录 |
| --- | --- |
| 05 | [整理三问需求访谈并建立 SPEC 追踪](members/陈万策_WP02_个人操作日志.md#wp02-01) |
| 05 | [设计 Dashboard 信息架构并验收浏览器交互](members/陈万策_WP02_个人操作日志.md#wp02-02) |
| 新增 | [把六个业务页面串联成同源用户路径](members/陈万策_WP02_个人操作日志.md#wp02-03) |
| 05 | [研究工作台分区、组件和 F01–F06 页面映射](members/陈万策_WP02_个人操作日志.md#wp02-04) |
| 06 | [重构项目中心并提取共享 Studio 设计系统](members/陈万策_WP02_个人操作日志.md#wp02-05) |
| 07 | [重构测试生成 Studio 的审阅和重试交互](members/陈万策_WP02_个人操作日志.md#wp02-06) |
| 08 | [实现执行控制中心、日志查看与缺陷交接](members/陈万策_WP02_个人操作日志.md#wp02-07) |
| 08 | [实现缺陷工作区、版本 Diff 和回归确认](members/陈万策_WP02_个人操作日志.md#wp02-08) |
| 08 | [实现质量工作台、运行对照与共享导出快照](members/陈万策_WP02_个人操作日志.md#wp02-09) |
| 新增 | [统一六页视觉、窄屏导航和端到端验收](members/陈万策_WP02_个人操作日志.md#wp02-10) |

### WP03 赵君豪

| 原摘要 | 已恢复的操作记录 |
| --- | --- |
| 新增 | [建立固定可信样例及 Dashboard 自检](members/赵君豪_WP03_个人操作日志.md#wp03-01) |
| 09 | [解析 Python AST、签名、条件定义和源码行号](members/赵君豪_WP03_个人操作日志.md#wp03-02) |
| 11 | [构造签名和 doctest 驱动的测试及不可变套件](members/赵君豪_WP03_个人操作日志.md#wp03-03) |
| 11 | [扩展代码契约、控制流和分层测试策略](members/赵君豪_WP03_个人操作日志.md#wp03-04) |
| 11 | [收集七项目结果并验证生成测试可局部修正](members/赵君豪_WP03_个人操作日志.md#wp03-05) |
| 09 | [建设可交互的 AST 图谱和精确源码联动](members/赵君豪_WP03_个人操作日志.md#wp03-06) |
| 10 | [精修布局、重播暂停和真实 Edge 动画验收](members/赵君豪_WP03_个人操作日志.md#wp03-07) |
| 12 | [冻结十个项目并逐字段复核真实模型理解和生成](members/赵君豪_WP03_个人操作日志.md#wp03-08) |
| 07、11 | [验证生成工作台套件历史、失败结果和执行器重试](members/赵君豪_WP03_个人操作日志.md#wp03-09) |
| 12、20 | [补充 Hypothesis 属性检查并复核 PHASE-06 结构评分](members/赵君豪_WP03_个人操作日志.md#wp03-10) |
| 新增 | [冻结课程演示数据集并独立验证已知缺陷](members/赵君豪_WP03_个人操作日志.md#wp03-11) |

### WP04 马雪朋

| 原摘要 | 已恢复的操作记录 |
| --- | --- |
| 新增 | [复核启动缺陷、数据库保护与退出重启](members/马雪朋_WP04_个人操作日志.md#wp04-01) |
| 13 | [实施 Wasmtime/WASI 执行器和真实运行日志](members/马雪朋_WP04_个人操作日志.md#wp04-02) |
| 14 | [建立缺陷生命周期和质量统计并验证真实修复](members/马雪朋_WP04_个人操作日志.md#wp04-03) |
| 13、14 | [采集运行分支、日志和失败帧，保持归因边界](members/马雪朋_WP04_个人操作日志.md#wp04-04) |
| 15 | [验证 Cosmic Ray 选型并实现六类一级变异算子](members/马雪朋_WP04_个人操作日志.md#wp04-05) |
| 15 | [验证原版门禁和固定分母，复核错误、超时与取消](members/马雪朋_WP04_个人操作日志.md#wp04-06) |
| 16 | [面向存活变异生成 AI 补测并校准原版](members/马雪朋_WP04_个人操作日志.md#wp04-07) |
| 16 | [比较 27B、模板和小模型在 117 位置的检出率](members/马雪朋_WP04_个人操作日志.md#wp04-08) |
| 16 | [重新验证补测总时限和统一模型质量退化](members/马雪朋_WP04_个人操作日志.md#wp04-09) |

### WP05 王选中

| 原摘要 | 已恢复的操作记录 |
| --- | --- |
| 17 | [建立五份工作包、贡献表和工程说明](members/王选中_WP05_个人操作日志.md#wp05-01) |
| 17、18 | [将 F01–F06 独立验收规则写入 AGENTS](members/王选中_WP05_个人操作日志.md#wp05-02) |
| 18 | [管理主开发分支并核验首次 GitHub 发布回执](members/王选中_WP05_个人操作日志.md#wp05-03) |
| 18 | [归档独立模块报告、初次失败和阶段回归](members/王选中_WP05_个人操作日志.md#wp05-04) |
| 19 | [合入冻结评测分支并只读复算](members/王选中_WP05_个人操作日志.md#wp05-05) |
| 20 | [创建 verify 与 testpilot-workflow Skills，并验证 Git Hook](members/王选中_WP05_个人操作日志.md#wp05-06) |
| 20 | [配置 MCP 并通过 Loop 修复查询兼容与真实数据验证](members/王选中_WP05_个人操作日志.md#wp05-07) |
| 20 | [建立 Reviewer Subagent 角色并保存独立复核证据](members/王选中_WP05_个人操作日志.md#wp05-08) |
| 20 | [恢复原始 Prompt、Bug 档案及团队历史索引](members/王选中_WP05_个人操作日志.md#wp05-09) |
| 20 | [整合课程交付、固定快照验收和最终回执](members/王选中_WP05_个人操作日志.md#wp05-10) |
