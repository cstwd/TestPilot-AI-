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
| 08 F04/F05 交互 | Codex、Edge、Playwright · [F04](../transcripts/WP06-F04-001.md) · [F05](../transcripts/WP07-F05-001.md) | 展示运行节点、日志、失败版本差异及确认回归 | `9fdfa7e`, `c49dde2` · [F04](../reports/WP06-F04-001/F04_BROWSER_ACCEPTANCE.md) · [F05](../reports/WP07-F05-001/F05_BROWSER_ACCEPTANCE.md) | 注入状态证据单独标记 |

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
