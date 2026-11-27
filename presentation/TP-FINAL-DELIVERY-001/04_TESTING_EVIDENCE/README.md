# 测试原证据入口

| 范围 | 原始材料 |
|---|---|
| 托管 CI | [三轮归档](CI/reports/TP-COURSE-REMEDIATION-001/ci-github/) · [最终 45992897616](https://github.com/cstwd/TestPilot-AI-/actions/runs/45992897616) · [工作流](CI/.github/workflows/course-verification.yml) |
| 自动化、属性、E2E、差分 | [本机课程回归](AUTOMATED_TESTING/reports/TP-COURSE-REMEDIATION-001/local-full.txt) · [PHASE-07 回归](AUTOMATED_TESTING/reports/phase07/verify-full.txt) · [属性用例](AUTOMATED_TESTING/tests/test_course_properties.py) · [浏览器 E2E](AUTOMATED_TESTING/tests/test_wp09_integration.py) · [差分评分器](AUTOMATED_TESTING/demo/TestPilot-Demo-Lab/evaluation/evaluator.py) |
| AI 离线与真实模型 | [固定协议](AI_EVALUATION/eval/phase05/PROTOCOL.md) · [冻结复算](AI_EVALUATION/reports/TP-COURSE-REMEDIATION-001/offline-evaluation-hardened.json) · [历史真实 API](AI_EVALUATION/reports/phase06/raw/live.json) · [最新试跑](AI_EVALUATION/reports/phase07/ai-live.json) |
| 两案实证 | [模型 Schema](BUG_CASES/collab-log/bugs/TP-MODEL-SCHEMA.md) · [F13 定位](BUG_CASES/collab-log/bugs/TP-F13-IS-NOT.md) · [双案复验](BUG_CASES/reports/TP-COURSE-REMEDIATION-001/bug-replay.json) |
| 真执行、回归、变异 | [unit_scaling 实录](MUTATION_TESTING/reports/phase07/edge-run.json) · [geometry 变异](MUTATION_TESTING/reports/phase07/f13-geometry.json) · [7 个样本及重跑](MUTATION_TESTING/reports/phase07/end-to-end.json) |
| 需求矩阵 E 编号 | [项目课程索引](../02_PROJECT_DOCUMENTS/raw/docs/COURSE_EVIDENCE_INDEX.md) · [第一轮 E01–E26](../07_FINAL_REPORT/FIRST_AUDIT_EVIDENCE.md) |

[副本来源及逐文件 SHA-256](../07_FINAL_REPORT/COPIED_EVIDENCE.csv)。归档原文件保留历史链接和原始字节，历史相对链接以 CSV 中仓库原路径定位。
