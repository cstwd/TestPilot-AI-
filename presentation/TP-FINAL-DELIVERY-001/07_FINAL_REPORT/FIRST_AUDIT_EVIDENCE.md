# 第一轮 E01–E26 证据编号索引

源文件为 TP-COURSE-AUDIT-001/07_EVIDENCE_INDEX.md。以下沿用历史编号及其证据类别。原仓库路径可在[仓库快照](../02_PROJECT_DOCUMENTS/repository/TestPilot-AI_cf448f3.zip)内查找，整改专有文件另见[Git 副本清单](COPIED_EVIDENCE.csv)。教师要求以本轮核对的五张原图为准。

| 编号 | 类别 | 代表性原文件／文件夹 |
|---|---|---|
| E01 | 审计上游标准 | `docs/COURSE_REQUIREMENTS_AUDIT.md` · `transcripts/TP-COURSE-FINAL-001.md` |
| E02 | 需求、结构和角色 | `docs/SPEC.md` · `docs/SPEC.md` · `docs/SPEC.md` · `docs/ARCHITECTURE.md` |
| E03 | 上下文和计划 | `AGENTS.md` · `AGENTS.md` · `docs/THREE_DAY_PLAN.md` · `docs/work-packages/` |
| E04 | 访谈与 Prompt | `transcripts/requirements-interview.md` · `transcripts/TP-PHASE-01.md` · `transcripts/TP-PHASE-02.md` · `transcripts/TP-PHASE-03.md` |
| E05 | 映射状态 | `docs/FEATURE_MAP.md` · `F01_MODULE_ACCEPTANCE.md` · `F06_MODULE_ACCEPTANCE.md` · `reports/WP09-001/END_TO_END_ACCEPTANCE.md` |
| E06 | 缺失项检索边界 | `reports/course-final/LOOP.md` · `transcripts/README.md` · `reports/TP_GITHUB_001_ACCEPTANCE.md` |
| E07 | 后期工作 Prompt 缺口 | `collab-log/members/陈万策_WP02_个人操作日志.md` · `reports/WP09-001/FRONTEND_V1_FINAL_ACCEPTANCE.md` |
| E08 | Skills、verify 和 Reviewer 定义 | `.claude/skills/verify/SKILL.md` · `.claude/skills/testpilot-workflow/SKILL.md` · `hooks/verify.py` · `.claude/agents/testpilot-reviewer.md` |
| E09 | MCP 配置/实现/回包、Hook 及 Loop | `.mcp.json` · `mcp-server/server.py` · `mcp-server/server.py` · `hooks/pre-commit` |
| E10 | 工具链通过及失败原回执 | `tests/test_course_toolchain.py` · `tests/test_course_toolchain.py` · `reports/course-final/toolchain.txt` · `reports/course-final/toolchain-first.txt` |
| E11 | 自动化原始测试 | `reports/course-final/verify-full.txt` · `reports/course-final/acceptance-72a53b8.txt` · `reports/WP09-001/raw/final-full-verify.txt` · `reports/WP09-001/raw/final-full-verify-overlay.json` |
| E12 | Run、Debug、独立安装资料 | `README.md` · `main.py` · `.run/TestPilot_AI.run.xml` · `requirements.txt` |
| E13 | 六页真实闭环及导出 | `reports/WP09-001/END_TO_END_ACCEPTANCE.md` · `reports/WP09-001/raw/workflow-identities.json` · `reports/WP09-001/raw/report-snapshot.json` · `reports/WP09-001/raw/report-download.html` |
| E14 | 属性及受限执行 | `tests/test_course_properties.py` · `backend/runner.py` · `backend/wasi_worker.py` · `tests/test_runner.py` |
| E15 | 冻结差分与历史 AI 离线 | `eval/phase05/PROTOCOL.md` · `eval/phase05/frozen.json` · `eval/phase05/projects/` · `eval/phase05/README.md` |
| E16 | 真实模型、健康与部署 | `backend/model_provider.py` · `backend/model_provider.py` · `backend/model_protocol.py` · `docs/phase06/DEPLOYMENT.md` |
| E17 | F13 真实 WASI、界面与归档 | `backend/mutation_web.py` · `backend/mutation_flow.py` · `backend/mutation_results.py` · `tests/test_mutation_lifecycle.py` |
| E18 | Bug 八环节原始凭据 | `collab-log/bugs/LOG.md` · `collab-log/bugs/TP-MODEL-SCHEMA.md` · `reports/phase05/raw/understanding/clamp.json` · `collab-log/bugs/TP-F13-IS-NOT.md` |
| E19 | 工作包、49 条和 20 条 | `collab-log/LOG.md` · `collab-log/COURSE_HISTORY.md` · `docs/COURSE_TEAM_CONTRIBUTIONS.md` · `collab-log/member_contributions.md` |
| E20 | 会话材料及关键答复 | `transcripts/README.md` · `transcripts/` · `transcripts/TP-PHASE-05.md` · `transcripts/TP-PHASE-06.md` |
| E21 | Git 及远端 | `reports/TP_GITHUB_001_ACCEPTANCE.md` · `reports/course-final/WORKTREE_AUDIT.md` · `reports/course-final/git-history.txt` · `docs/COURSE_EVIDENCE_INDEX.md` |
| E22 | PPTX、PDF、视频与截图 | `presentation/TestPilot_AI_课程汇报.pptx` · `presentation/TestPilot_AI_课程汇报.pdf` · `presentation/TestPilot_AI_备用演示.mp4` · `presentation/README.md` |
| E23 | Reviewer 执行 | `reports/course-final/REVIEWER.md` · `reports/course-final/REVIEWER.md` · `reports/WP09-001/GLOBAL_REGRESSION_REPORT.md` · `demo/TestPilot-Demo-Lab/reports/REVIEW.md` |
| E24 | Demo Lab 与最近回归 | `demo/TestPilot-Demo-Lab/README.md` · `demo/TestPilot-Demo-Lab/AI_BLIND_EVALUATION.md` · `demo/TestPilot-Demo-Lab/SHA256SUMS.txt` · `demo/TestPilot-Demo-Lab/reference/ground_truth.json` |
| E25 | 核心路由、前端及独立验收 | `backend/workbench.py` · `backend/projects.py` · `backend/analysis.py` · `backend/generation.py` |
| E26 | 智能引擎任务证据 | `backend/engine_web.py` · `backend/engine_flow.py` · `backend/engine_failures.py` · `backend/engine_feedback.py` |
