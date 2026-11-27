# 逐页讲稿

## P01 TestPilot AI

陈帅廷 · 25 秒

我们把 Python 源码、测试、失败证据和修复验证放在同一个工作台。今天沿着一个真实的单位换算缺陷，展示这条链路如何运行。右侧是 Phase 07 的 Edge 实际页面。

演示操作　打开 Demo Lab 的样本库，让听众先看到 unit_scaling 的入口。

[打开对应证据](../05_DEMO_ASSETS/screenshots/01-workbench.png)

## P02 测试工作的难点在交接处

陈帅廷 · 40 秒

开发者要理解陌生代码，测试人员要把预期写成可执行断言，质量人员需要复核缺陷和回归。访谈保留三个实际问答，验收按任务书落实。我们选同一套件复跑、原失败节点通过、结果可导出这三件可观察的事。

演示操作　打开需求访谈，指向三项可在工作台观察的验收条件。

[打开对应证据](../03_TEAM_COLLABORATION/raw/transcripts/requirements-interview.md)

## P03 工作台把七项能力接成一条链

陈帅廷 · 35 秒

从导入开始，六项主功能共享项目和版本。F13 从已经验证的套件出发，看它能否识别代码被改错。Demo Lab 用固定课程样例把这条路径压缩成一次可复核运行。

演示操作　沿图逐个指出文件版本、套件和运行，再指出 F13 的输入。

[打开对应证据](../02_PROJECT_DOCUMENTS/raw/docs/FEATURE_MAP.md)

## P04 执行隔离与证据留存各有入口

陈帅廷 · 55 秒

PyCharm 运行根 main.py，Uvicorn 和 FastAPI 同源提供页面与 API。分析读取源码做 AST。AI 走本机 Ollama/Vulkan 回环。测试和变异经 runner 进入 WASI CPython 与 Pytest。SQLite 保存证据，Demo Lab 使用独立数据库。

演示操作　打开架构文档，依次定位 main.py、model_provider 和受限运行入口。

[打开对应证据](../02_PROJECT_DOCUMENTS/SYSTEM_ARCHITECTURE.md)

## P05 从 telemetry.py 的图谱跳到源码

陈万策 · 55 秒

打开 telemetry.py，选类或方法，Inspector 返回限定名和对应源码行。界面的边表达词法包含。右侧的 average 调用 mean_value 来自直接阅读原始源码，用于说明局部调用。

演示操作　在代码分析页选 Sample.normalized，核对第 10–11 行，再打开源码中的 average。

[打开对应证据](../05_DEMO_ASSETS/screenshots/05-ast-source.png)

## P06 生成模式决定套件的证据来源

陈万策 · 60 秒

历史 PHASE-06 使用 Qwen3.8-27B UD-IQ3_XXS，Ollama/Vulkan 本机回环，AI 套件接口实际 200，mode=ai。模型给出场景和断言，服务静态检查后保存。右侧是该次生成的 bonus 边界断言，普通 F03 的模板截图另附在素材目录。最新现场单样本触发资源守卫，所以现场演示预设课堂模板。CI 历史回放只复算存档。

演示操作　打开历史 live.json 的 F03/suite，查 mode 和 bonus 的断言；需要展示模板时切到单独的截图。

[打开对应证据](../04_TESTING_EVIDENCE/AI_EVALUATION/reports/phase06/raw/live.json)

## P07 Pytest 持久化了可定位的失败

赵君豪 · 50 秒

unit_scaling v1 的真实 Pytest 运行只有一项，失败，退出 1，耗时 5.644 秒，实际值 1，预期 1.25。独立 F04 界面截图用于指认日志与详情位置，数值以 unit_scaling JSON 为准。

演示操作　在失败详情展开日志，将断言和退出码与 Edge 回执核对。

[打开对应证据](../04_TESTING_EVIDENCE/MUTATION_TESTING/reports/phase07/edge-run.json)

## P08 用同一套件验证 unit_scaling 修复

马雪朋 · 65 秒

这次我们打开项目 7 的单位换算缺陷。原套件有两项失败。Qwen 根据失败信息提出把整除改为真除法。操作者在浏览器核对差异并点击应用，系统创建文件 17。继续选原套件 8 运行回归，三项通过，零失败；同一项属性测试因 WASI 缺少 Hypothesis 继续跳过。原套件主要检查返回类型，另有四个独立数值用例验证换算结果。

演示操作　打开专项的预览与回归截图；在缺陷管理依次选择 AI 分析、审阅差异、应用候选和原套件回归。

[打开对应证据](../04_TESTING_EVIDENCE/F05_AI_REPAIR/reports/TP-F05-AI-REPAIR-001/TP_F05_AI_REPAIR_001_ACCEPTANCE.md)

## P09 5 个变异中有 1 个存活

马雪朋 · 60 秒

先跑原版，给运算等位置施加一阶变化，再在同一套件下执行变异。geometry 的 5 个变异里 2 杀死、1 存活、2 执行错误。全量 2/5，有效 2/3。存活记录定位回源码第 8 行，帮助找断言盲区。

演示操作　打开 geometry 变异详情，定位第 8 行 SuppressRaise 并对照两个分母。

[打开对应证据](../04_TESTING_EVIDENCE/MUTATION_TESTING/reports/phase07/f13-geometry.json)

## P10 冻结评测可以在 CI 中复算

赵君豪 · 65 秒

10 个小项目和三个固定种子，四组共 120 轮，每组 117 个登记位置。四组检出依次为 0、81、104、105。A 未形成可计分的变异，图示为固定分母检出。托管第三轮 168 Pytest、3 Node 和另 8 项独立评分通过。前两轮 WASI 冷启动超时，经固定预热后通过。

演示操作　指向四组原始计数，再打开第三轮 CI 回执的工作流步骤。

[打开对应证据](../04_TESTING_EVIDENCE/CI/reports/TP-COURSE-REMEDIATION-001/ci-github/45992897616/receipt.json)

## P11 两个真实 Bug 促成了可测的约束

马雪朋 · 60 秒

模型案实际输出对象，冻结协议期待三元素数组。把形状写进 Schema 并加限次重试。另一个案是 Codex 生成的 F13 定位逻辑，共同前缀越过运算符，修复后用语义位置锚定。双案新一轮定向共 9 项。历史同期假设缺失，本次复验前的假设已归档。

演示操作　依次打开两份 Bug 档案，指向复现、根因、修复提交与定向回归。

[打开对应证据](../07_FINAL_REPORT/historical/reports/TP_COURSE_BUG_ARCHIVE_AUDIT.md)

## P12 一个运行 ID 串起从导入到报告

马雪朋 · 55 秒

一份 Edge 报告连上两版文件、suite #1、两次 Pytest、缺陷状态和质量指标。Demo Lab 直接下载完整 JSON，再从报告中心打开同一个运行。通用 F06 还能导出 HTML。

演示操作　在 Demo Lab 的运行历史打开同一报告，下载完整 JSON，对照运行 ID。

[打开对应证据](../04_TESTING_EVIDENCE/MUTATION_TESTING/reports/phase07/edge-run.json)

## P13 六项技术如何让测试结果可以复核

王选中 · 55 秒

图谱把方法定位回源码，套件保存生成来源，WASI 留下运行日志。同一套件能比较修复效果，存活变异揭示测试盲区，质量报告可以按运行编号重读。开发时，两项 Skill 固定工作步骤，只读 MCP 查询证据，Hook 检查提交。独立 Reviewer 指出评测校验缺口，Goal 接受失败反馈后改用种子漂移检查，修正后完成。

演示操作　打开工具链与 Goal 回执，指出一次失败反馈和据此更改的验证动作。

[打开对应证据](../07_FINAL_REPORT/historical/reports/TP_COURSE_LOOP_EVIDENCE.md)

## P14 课程评分对应到可核对的材料

王选中 · 55 秒

课程七项共 100 分，另加 5。需求用 SPEC 与访谈，测试用 CI、属性、端到端和冻结评测，调试与协作用双 Bug 和五份日志，产品与答辩用实录及本套材料。五岗各 20% 为项目计划责任，个人答辩系数由教师核定。

演示操作　打开评分工作簿与五人贡献矩阵，选择一个维度对照其证据。

[打开对应证据](../01_TEACHER_REQUIREMENTS/TEACHER_REQUIREMENTS.md)

## P15 可追溯的回归是项目的主要成果

王选中 · 40 秒

现场按 telemetry、unit_scaling、F13 和 F06 顺序展示。工程成果是可以重读的测试证据。后续需要在答辩机复验本机 AI、完成异机交接及五人联排，补齐关键历史会话覆盖和本人核证。

演示操作　打开现场手册、备用视频和剩余事项，交接给下一位演示者。

[打开对应证据](../07_FINAL_REPORT/GAP_REGISTER.md)
