# 按教师要求找文件

| 教师查看内容 | 包内入口 | 核验方法 |
|---|---|---|
| 选题、需求、目标用户、验收条件 | [SPEC](../02_PROJECT_DOCUMENTS/raw/docs/SPEC.md) · [三问访谈](../03_TEAM_COLLABORATION/raw/transcripts/requirements-interview.md) · [产品概述](../02_PROJECT_DOCUMENTS/PROJECT_OVERVIEW.md) | 对照五张原图与可观察的功能验收条件。 |
| 项目仓库与运行 | [产品快照](../02_PROJECT_DOCUMENTS/repository/TestPilot-AI_cf448f3.zip) · [Git 历史](../02_PROJECT_DOCUMENTS/repository/GIT_HISTORY.txt) | 解压快照，按根 README 配置，PyCharm Run 根 main.py。 |
| 上下文及演化 | [AGENTS 初版](../02_PROJECT_DOCUMENTS/context_history/AGENTS-8038be2.md) · [阶段二版](../02_PROJECT_DOCUMENTS/context_history/AGENTS-097358b.md) · [工具链版](../02_PROJECT_DOCUMENTS/context_history/AGENTS-4b1b574.md) | 对比三个实际 Git 版本。 |
| Skills | [verify](../02_PROJECT_DOCUMENTS/raw/.claude/skills/verify/SKILL.md) · [testpilot-workflow](../02_PROJECT_DOCUMENTS/raw/.claude/skills/testpilot-workflow/SKILL.md) · [调用记录](../02_PROJECT_DOCUMENTS/raw/reports/course-final/TOOLCHAIN.md) | 检查定义、权限、输入输出与实际执行。 |
| MCP、Hook 和独立 Reviewer | [MCP 配置](../02_PROJECT_DOCUMENTS/raw/.mcp.json) · [服务端](../02_PROJECT_DOCUMENTS/raw/mcp-server/server.py) · [Hook](../02_PROJECT_DOCUMENTS/raw/hooks/pre-commit) · [Reviewer 定义](../02_PROJECT_DOCUMENTS/raw/.claude/agents/testpilot-reviewer.md) · [实测](../04_TESTING_EVIDENCE/AUTOMATED_TESTING/reports/course-final/toolchain.txt) · [审查结果](../04_TESTING_EVIDENCE/AI_EVALUATION/reports/TP-COURSE-REMEDIATION-001/ci-independent-review.json) | 对照 stdio 访问、Hook 拦截、审查发现及修复。 |
| Loop、Prompt、关键输出与失败原文 | [Goal 回执](../07_FINAL_REPORT/historical/reports/TP_COURSE_LOOP_EVIDENCE.md) · [六阶段原文](../03_TEAM_COLLABORATION/transcripts/README.md) · [历史 /export](../03_TEAM_COLLABORATION/raw/collab-log/transcripts/TP-COURSE-REMEDIATION-001-claude-attempt.txt) | 单独核对原生导出覆盖范围，记录关键历史会话待认可。 |
| 自动化、属性、E2E、差分与 AI 评测 | [测试原件入口](../04_TESTING_EVIDENCE/README.md) · [CI 验收](../07_FINAL_REPORT/historical/reports/TP_COURSE_CI_ACCEPTANCE.md) | 同时保留真实失败、复验和冻结评测协议。 |
| 两份工程 Bug，至少一份 AI 引入 | [模型参数形状](../04_TESTING_EVIDENCE/BUG_CASES/collab-log/bugs/TP-MODEL-SCHEMA.md) · [F13 定位](../04_TESTING_EVIDENCE/BUG_CASES/collab-log/bugs/TP-F13-IS-NOT.md) · [八步复验](../07_FINAL_REPORT/historical/reports/TP_COURSE_BUG_ARCHIVE_AUDIT.md) | 原现象、假设时点、复现、根因、修复、回归逐项可查。 |
| 五人日志、五岗分工与本人核证 | [协作总日志](../03_TEAM_COLLABORATION/raw/collab-log/LOG.md) · [五个工作包与个人原日志](../03_TEAM_COLLABORATION/WP01-WP05/) · [本人确认单](../03_TEAM_COLLABORATION/MEMBER_CONFIRMATION/) | 按本人、岗位与 Codex 实际执行三类身份核对。 |
| 汇报与最终提交 | [15 页大纲](../06_PRESENTATION/PPT_OUTLINE.md) · [备用演示视频](../06_PRESENTATION/assets/presentation/TestPilot_AI_备用演示.mp4) · [演示手册](../06_PRESENTATION/DEMO_RUNBOOK.md) | 教师图 5 最终提交三类为仓库、日志、幻灯片。原有 8 页幻灯片位于仓库快照 presentation/，本次新增汇报材料为大纲。 |
| 评分与待确认 | [评分矩阵](SCORING_MATRIX.xlsx) · [64 项明细](../07_FINAL_REPORT/FINAL_ACCEPTANCE_MATRIX.xlsx) · [A–D 缺口](../07_FINAL_REPORT/GAP_REGISTER.md) | 基础满分 100，另加 5；教师核定答辩系数及实际成绩。 |

**归档截止补充**　产品快照固定至 cf448f3。F05 专项 d8226c3（实现 b40b54e）有两次真实 Qwen 修复推理，原套件 #8 从 1 通过、2 失败、1 跳过变为 3 通过、0 失败、1 跳过。该专项独立于 Demo Lab 的课堂模板套件 #1 和 F03 冷启动试跑。cf448f3 五份周报的编排日期与实际证据时间分别保留。[F05 专项](../04_TESTING_EVIDENCE/F05_AI_REPAIR/reports/TP-F05-AI-REPAIR-001/TP_F05_AI_REPAIR_001_ACCEPTANCE.md) · [周报版日志](../03_TEAM_COLLABORATION/weekly/collab-log/members/)
