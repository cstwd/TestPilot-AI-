# TestPilot AI 课程汇报大纲

建议 15 页，合计 12 分 55 秒，现场操作另计。分段为建议，五位成员按本人核证的工作准备讲解。

## P01　TestPilot AI

**陈帅廷 · 25 秒**　我们把 Python 源码、测试、失败证据和修复验证放在同一个工作台。今天沿着一个真实的单位换算缺陷，展示这条链路如何运行。展示 Phase 07 的真实 Edge 样本库。

材料　[PHASE-07 · Edge 样本库实录](../05_DEMO_ASSETS/screenshots/01-workbench.png)

## P02　测试工作的难点在交接处

**陈帅廷 · 40 秒**　开发者要理解陌生代码，测试人员要把预期写成可执行断言，质量人员需要复核缺陷和回归。访谈保留三个实际问答，验收按任务书落实。我们选同一套件复跑、原失败节点通过、结果可导出这三件可观察的事。

材料　[docs/SPEC.md · transcripts/requirements-interview.md](../03_TEAM_COLLABORATION/raw/transcripts/requirements-interview.md)

## P03　工作台把七项能力接成一条链

**陈帅廷 · 35 秒**　从导入开始，六项主功能共享项目和版本。F13 从已经验证的套件出发，看它能否识别代码被改错。Demo Lab 用固定课程样例把这条路径压缩成一次可复核运行。

材料　[docs/SPEC.md · docs/FEATURE_MAP.md · PHASE-07](../02_PROJECT_DOCUMENTS/raw/docs/FEATURE_MAP.md)

## P04　执行隔离与证据留存各有入口

**陈帅廷 · 55 秒**　PyCharm 运行根 main.py，Uvicorn 和 FastAPI 同源提供页面与 API。分析读取源码做 AST。AI 走本机 Ollama/Vulkan 回环。测试和变异经 runner 进入 WASI CPython 与 Pytest。SQLite 保存证据，Demo Lab 使用独立数据库。

材料　[backend/app.py · runner.py · model_provider.py · database.py](../02_PROJECT_DOCUMENTS/SYSTEM_ARCHITECTURE.md)

## P05　从 telemetry.py 的图谱跳到源码

**陈万策 · 55 秒**　打开 telemetry.py，选类或方法，Inspector 返回限定名和对应源码行。界面的边表达词法包含。源码中的 average 调用 mean_value 来自直接阅读原始源码，用于说明局部调用。

材料　[telemetry.py · ast-model.js · WP03 AST 视觉复验](../05_DEMO_ASSETS/screenshots/05-ast-source.png)

## P06　生成模式决定套件的证据来源

**陈万策 · 60 秒**　PHASE-06 的 Qwen3.8-27B UD-IQ3_XXS 经 Ollama/Vulkan 回环调用。F03 接口返回 200 和 mode=ai，原始回执保存 bonus 的生成断言。区分普通工作台模板、历史 AI 和 CI 冻结复算；最新现场试跑在源码理解阶段触发资源守卫。

材料　[PHASE-06 raw/live.json · PHASE-07 ai-live.json](../04_TESTING_EVIDENCE/AI_EVALUATION/reports/phase06/raw/live.json)

## P07　Pytest 持久化了可定位的失败

**赵君豪 · 50 秒**　unit_scaling v1 的真实 Pytest 运行只有一项，失败，退出 1，耗时 5.644 秒，实际值 1，预期 1.25。独立 F04 界面截图用于指认日志与详情位置，数值以 unit_scaling JSON 为准。

材料　[PHASE-07 edge-run.json · F04 Execution Center 实录](../04_TESTING_EVIDENCE/MUTATION_TESTING/reports/phase07/edge-run.json)

## P08　用同一套件验证 unit_scaling 修复

**马雪朋 · 65 秒**　这次我们打开项目 7 的单位换算缺陷。原套件有两项失败。Qwen 根据失败信息提出把整除改为真除法。操作者在浏览器核对差异并点击应用，系统创建文件 17。继续选原套件 8 运行回归，三项通过，零失败；同一项属性测试因 WASI 缺少 Hypothesis 继续跳过。原套件主要检查返回类型，另有四个独立数值用例验证换算结果。

材料　[F05 专项 d8226c3 · 原套件 #8 · 原始 #12 / 回归 #14](../04_TESTING_EVIDENCE/F05_AI_REPAIR/reports/TP-F05-AI-REPAIR-001/TP_F05_AI_REPAIR_001_ACCEPTANCE.md)

## P09　5 个变异中有 1 个存活

**马雪朋 · 60 秒**　先跑原版，给运算等位置施加一阶变化，再在同一套件下执行变异。geometry 的 5 个变异里 2 杀死、1 存活、2 执行错误。全量 2/5，有效 2/3。存活记录定位回源码第 8 行，帮助找断言盲区。 本地模板生成的套件中，第 8 行 SuppressRaise 将抛出 ValueError 改为 pass，套件仍通过。

材料　[PHASE-07 f13-geometry.json · geometry_calculator.area](../04_TESTING_EVIDENCE/MUTATION_TESTING/reports/phase07/f13-geometry.json)

## P10　冻结评测可以在 CI 中复算

**赵君豪 · 65 秒**　10 个小项目和三个固定种子，四组共 120 轮，每组 117 个登记位置。四组检出依次为 0、81、104、105。A 未形成可计分的变异，图示为固定分母检出。托管第三轮 168 Pytest、3 Node 和另 8 项独立评分通过。前两轮 WASI 冷启动超时，经固定预热后通过。

材料　[GitHub Actions 45992897616 · PHASE-05 冻结回执](../04_TESTING_EVIDENCE/CI/reports/TP-COURSE-REMEDIATION-001/ci-github/45992897616/receipt.json)

## P11　两个真实 Bug 促成了可测的约束

**马雪朋 · 60 秒**　模型案实际输出对象，冻结协议期待三元素数组。把形状写进 Schema 并加限次重试。另一个案是 Codex 生成的 F13 定位逻辑，共同前缀越过运算符，修复后用语义位置锚定。双案新一轮定向共 9 项。历史同期假设缺失，本次复验前的假设已归档。

材料　[TP-MODEL-SCHEMA.md · TP-F13-IS-NOT.md · bug-replay.json](../07_FINAL_REPORT/historical/reports/TP_COURSE_BUG_ARCHIVE_AUDIT.md)

## P12　一个运行 ID 串起从导入到报告

**马雪朋 · 55 秒**　一份 Edge 报告连上两版文件、suite #1、两次 Pytest、缺陷状态和质量指标。Demo Lab 直接下载完整 JSON，再从报告中心打开同一个运行。通用 F06 还能导出 HTML。

材料　[PHASE-07 Edge d564ee8f · 报告中心与 F06 导出](../04_TESTING_EVIDENCE/MUTATION_TESTING/reports/phase07/edge-run.json)

## P13　六项技术如何让测试结果可以复核

**王选中 · 55 秒**　图谱把方法定位回源码，套件保存生成来源，WASI 留下运行日志。同一套件能比较修复效果，存活变异揭示测试盲区，质量报告可以按运行编号重读。开发时，两项 Skill 固定工作步骤，只读 MCP 查询证据，Hook 检查提交。独立 Reviewer 指出评测校验缺口，Goal 接受失败反馈后改用种子漂移检查，修正后完成。

材料　[course-final/TOOLCHAIN.md · CI 独立复核 · Goal 原回执](../07_FINAL_REPORT/historical/reports/TP_COURSE_LOOP_EVIDENCE.md)

## P14　课程评分对应到可核对的材料

**王选中 · 55 秒**　课程七项共 100 分，另加 5。需求用 SPEC 与访谈，测试用 CI、属性、端到端和冻结评测，调试与协作用双 Bug 和五份日志，产品与答辩用实录及本套材料。五岗各 20% 为项目计划责任，个人答辩系数由教师核定。 原始矩阵 64 项为 44 PASS、17 PARTIAL、1 MISSING、2 UNVERIFIED。

材料　[教师原图 2–5 · 5 份岗位日志 · 本包 64 项验收](../01_TEACHER_REQUIREMENTS/TEACHER_REQUIREMENTS.md)

## P15　可追溯的回归是项目的主要成果

**王选中 · 40 秒**　现场按 telemetry、unit_scaling、F13 和 F06 顺序展示。工程成果是可以重读的测试证据。后续需要在答辩机复验本机 AI、完成异机交接及五人联排，补齐关键历史会话覆盖和本人核证。

材料　[PHASE-07 验收 · 第二轮课程验收 · 最终交付报告](../07_FINAL_REPORT/GAP_REGISTER.md)
