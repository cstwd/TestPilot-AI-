# 教师要求与仓库证据

课程任务 TP-COURSE-REPOSITORY-001，WP05。依据 [图 1 选题](course/originals/teacher-01.png)、[图 2 过程记录](course/originals/teacher-02.png)、[图 3 评分](course/originals/teacher-03.png)、[图 4 仓库](course/originals/teacher-04.png)、[图 5 里程碑](course/originals/teacher-05.png)及[原图来源与校验](course/originals/SHA256.json)。

| 教师要求 | 可直接检查的材料 | 当前证据状态 |
|---|---|---|
| 自拟项目须有一定复杂度或创意，功能完整 | [需求与目标](SPEC.md) · [WASI、SQLite 与本地模型架构](ARCHITECTURE.md) · [F01–F13](FEATURE_MAP.md) | 项目用版本、用例、执行和缺陷 ID 串起可演示的测试闭环。 |
| 定义阶段完成选题、分工、AI 访谈、可测试 SPEC、初版上下文和技术选型 | [职责](../collab-log/member_contributions.md) · [真实三问访谈](../transcripts/requirements-interview.md) · [原任务](../transcripts/raw/phase01-06/TP-PHASE-01-user.txt) · [功能及非功能规格](SPEC.md) · [变异工具选型](phase04/TOOL_SELECTION.md) | 三个用户答复均为“沿用任务书”，原任务与访谈共同限定需求。SPEC 有可观察端点、字段、错误状态和完成条件。 |
| 上下文在 Git 中体现演化 | [AGENTS.md](../AGENTS.md) · [Git 版本对照](GIT_CLEANUP_REPORT.md) | 可检视初版 `8038be2`、阶段验收规则 `097358b`、工具链及课程规则 `4b1b574`。 |
| 至少两项真正可用的自定义 Skills，含 verify | [verify](../.claude/skills/verify/SKILL.md) · [testpilot-workflow](../.claude/skills/testpilot-workflow/SKILL.md) · [使用与失败处理](../reports/course-final/TOOLCHAIN.md) | 两项有触发场景、步骤和实测记录。外部团队复用未核证。图 4 蓝框可选。 |
| 至少一个 MCP，说明选择理由 | [配置](../.mcp.json) · [Server](../mcp-server/server.py) · [真实 stdio 与工具调用](../reports/course-final/toolchain.txt) · [为何使用 MCP](../reports/course-final/TOOLCHAIN.md) | 真实读取 WASI 结果和数据不变验证齐备。Claude 客户端配置发现有回执，端到端调用未证。图 4 蓝框可选。 |
| 至少一个确定性 Hook | [pre-commit](../hooks/pre-commit) · [启用方式及拒绝/通过](../reports/course-final/TOOLCHAIN.md) | 暂存差异违规会阻止提交，修正后可提交。新克隆按说明显式启用。图 4 蓝框可选。 |
| 至少一个自定义 Reviewer | [角色及工具配置](../.claude/agents/testpilot-reviewer.md) · [独立审查](../reports/course-final/REVIEWER.md) · [CI 溯源复核](../reports/TP-COURSE-REMEDIATION-001/ci-independent-review.json) | 已有真实问题、修复与复核记录。图 4 蓝框可选。 |
| 自动化测试与至少一种属性、E2E 或差分，AI 离线评测在 CI 运行 | [测试入口](COURSE_TESTING.md) · [Hypothesis](../tests/test_course_properties.py) · [真实端到端](../tests/test_phase02_flow.py) · [Node](../tests/bug_diff.test.mjs) · [离线协议](../eval/phase05/PROTOCOL.md) · [Workflow](../.github/workflows/course-verification.yml) · [托管成功回执](../reports/TP-COURSE-REMEDIATION-001/ci-github/45992897616/receipt.json) | 包含真实 Pytest、Node、Edge、WASI、冻结合成数据复算。托管成功回执固定在 `000a19c`。 |
| Mutation Testing 的实现、判读和结果 | [变异实现](../backend/mutation_generator.py) · [生命周期回归](../tests/test_mutation_lifecycle.py) · [117 个固定位置对照](../reports/phase05/T04_COMPARISON.md) · [F13 页面实测](../reports/phase07/f13-geometry.json) | 运行原版校准、变异位置和实际结果均可查，固定分母保留错误与未运行。 |
| 至少一次 Goal、Loop 或 claude -p 完成任务 | [任务、轮次与终态](../reports/TP_COURSE_LOOP_EVIDENCE.md) · [Goal 完成回执](../reports/TP-COURSE-REMEDIATION-001/goal-complete.json) | Codex 原生 Goal 实际完成。Claude CLI 返回 403，原始失败回执保留。图 4 蓝框可选。 |
| 五人每人至少一条、组内至少八条，保留工具、Prompt、过程、结果和反思 | [总日志与五份个人日志](../collab-log/LOG.md) · [历史索引](../collab-log/COURSE_HISTORY.md) · [本人确认单](../collab-log/member-confirmation/) | 49 条，五岗分布 9/10/11/9/10。49 条均有关联 Git 与测试证据，48 条有原始 Prompt 链接。个人实际操作及反思待本人核证。 |
| 两份 Bug 档案，至少一份 AI 引入，记录八步 | [模型输出 Schema](../collab-log/bugs/TP-MODEL-SCHEMA.md) · [AI 引入的 F13 定位缺陷](../collab-log/bugs/TP-F13-IS-NOT.md) · [八步复验与原始证据](../reports/TP_COURSE_BUG_ARCHIVE_AUDIT.md) · [生成断言备选案](../collab-log/bugs/TP-F12-GENERATED-ORACLE.md) | 两份均有现象、复现、证据、根因、修复、回归及沉淀。假设来自复验前记录，原开发同期假设缺失。 |
| 保留原 Prompt、关键输出、失败尝试，关键会话用 /export 进入 transcripts | [原文总索引](../transcripts/README.md) · [12 条阶段原文字节与校验索引](../transcripts/raw/phase01-06/) · [原生 Claude /export](../collab-log/transcripts/TP-COURSE-REMEDIATION-001-claude-attempt.txt) · [终端回执](../reports/TP-COURSE-REMEDIATION-001/export-terminal.json) | 部分覆盖。原生导出覆盖 CI 失败会话。需求、主要技术开发与两案的同期 Claude 导出待补或待教师确认现有 Codex 原文。 |
| 产品可用，README 支持他人安装启动 | [Windows 安装、运行与操作](../README.md) · [本机 27B 部署](phase06/DEPLOYMENT.md) · [实机 F05 AI 修复结果](../reports/TP-F05-AI-REPAIR-001/TP_F05_AI_REPAIR_001_ACCEPTANCE.md) | 保留本机实测和历史模型回执。独立人员在答辩机冷启动及现场权重复验另待核证。 |
| 最终提交仓库、日志、幻灯片，另备演示视频，每人讲解负责部分 | [仓库入口](../README.md) · [日志](../collab-log/LOG.md) · [正式 PPTX、PDF、讲稿及视频](../presentation/README.md) | 材料可本地查阅。正式递交、五人联排与课堂答辩由组长安排。 |
| 时间线中的四阶段和检查点 | [原始三天计划](THREE_DAY_PLAN.md) · [阶段与 Git 索引](COURSE_EVIDENCE_INDEX.md) · [最终验收](COURSE_REPOSITORY_AUDIT.md) | 原图列定义、构建、加固、复盘。实际进展以 Git 和日志为准。首天空测试 CI 及按图中一周日历完成待核证。 |
| 可选加分与个人贡献 | [MCP 实测](../reports/course-final/toolchain.txt) · [五人职责与边界](COURSE_TEAM_CONTRIBUTIONS.md) | 自建 MCP 有证据。外部 Skills 复用及跨组红队无回执。个人系数 0.8–1.2 由教师按答辩判定。 |

图 3 的七项基础评分依次为需求与上下文 20、扩展 5、测试 15、调试 10、协作 10、产品 20、答辩 20，共 100 分。加分上限 5 分。本表记录可查证据，实际评分由教师决定。
