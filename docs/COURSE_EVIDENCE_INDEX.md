# TestPilot AI 课程成果索引

[教师要求入口](COURSE_REQUIREMENTS_MAPPING.md) · [最新仓库审计](COURSE_REPOSITORY_AUDIT.md)

| 交付 | 主要成果 | 实现及证据 |
|---|---|---|
| PHASE-01 | PyCharm Run/Debug、单服务、Dashboard 与固定自检 | `8038be2`, `88ebf23` · [阶段报告](../TP_PHASE_01_ACCEPTANCE.md) · [截图](../reports/dashboard.png) · [会话](../transcripts/TP-PHASE-01.md) |
| PHASE-02 / F01–F06 | 不可变导入、AST、用例生成、隔离执行、缺陷与报告 | `77e6177`, `743e24f`, `2b2185c`, `d988ecc`, `b6f4ef5`, `c874456`, `f31a901` · [阶段报告](../TP_PHASE_02_ACCEPTANCE.md) · [完整 E2E](../reports/phase02/e2e.txt) · [会话](../transcripts/TP-PHASE-02.md) |
| PHASE-03 / F07–F12 | 智能引擎、结构化审计、七项目复验 | `978323d`, `7422857` · [阶段报告](../TP_PHASE_03_ACCEPTANCE.md) · [用例证据](../reports/phase03/E2E.md) · [会话](../transcripts/TP-PHASE-03.md) |
| PHASE-04 / F13 | 六类算子、原版绿灯、固定分母与 F13 补测 | `5b757b9`, `6de6844`, `5be8d12`, `f6daaa1`, `8607ffa`, `38dd0bc`, `307d4bd` · [验收](../TP_PHASE_04_ACCEPTANCE.md) · [146 项历史回归](../reports/phase04/final-suite.txt) · [会话](../transcripts/TP-PHASE-04.md) |
| PHASE-05 | 10/10 推理、120 次比较、117 个位置／组 | `8923f2c`，课程合并 `1acd2ff` · [验收](../reports/phase05/TP_PHASE_05_ACCEPTANCE.md) · [图](../reports/phase05/mutation-score.png) · [会话](../transcripts/TP-PHASE-05.md) |
| PHASE-06 | Qwen3.8-27B 本机统一 Provider、Vulkan 监督与资源保护 | `98adf18`, `0ddc083`, `d4fbdf9`, `74ba1b4`，课程合并 `646ef7d`、`ae21701` · [阶段验收](../reports/phase06/TP_PHASE_06_ACCEPTANCE.md) · [部署](phase06/DEPLOYMENT.md) · [会话](../transcripts/TP-PHASE-06.md) |
| 工作台升级 | 导入中心、AST 动画、生成 Studio、执行中心、缺陷中心 | `9f048d0`, `7f724d0`, `76bd9e0`, `7c796e7`, `9fdfa7e`, `c49dde2` · [F01](../reports/WP04-F01-001/F01_BROWSER_ACCEPTANCE.md) · [F02](../reports/WP03-AST-VISUAL-001/BROWSER_ACCEPTANCE.md) · [F03](../reports/WP05-F03-001/F03_BROWSER_ACCEPTANCE.md) · [F04](../reports/WP06-F04-001/F04_BROWSER_ACCEPTANCE.md) · [F05](../reports/WP07-F05-001/F05_BROWSER_ACCEPTANCE.md) |
| F06 质量工作台升级 | 实测指标、运行对照和质量导出 | `b7a8b40` · [浏览器](../reports/WP08-F06-001/) |
| 课程交付 | 验收、五人记录、工程工具、Bug 案例、截图、PPT 与视频 | [要求审计](COURSE_REQUIREMENTS_AUDIT.md) · [验收报告](COURSE_FINAL_REPORT.md) · [工作记录](../collab-log/LOG.md) · [会话索引](../transcripts/README.md) · [展示材料](../presentation/README.md) |


## 五人个人操作日志证据

| 工作包与成员 | 日志证据范围 | 原始任务与复验入口 |
| --- | --- | --- |
| [WP01 陈帅廷](../collab-log/members/陈帅廷_WP01_个人操作日志.md) | 立项与集成、模型部署及统一 Provider，9 条 | [原始会话](../transcripts/TP-PHASE-01.md) · [复验证据](../reports/phase06/TP_PHASE_06_ACCEPTANCE.md) |
| [WP02 陈万策](../collab-log/members/陈万策_WP02_个人操作日志.md) | 需求、各页改版及浏览器终验，10 条 | [原始会话](../transcripts/WP08-F06-001.md) · [复验证据](../reports/WP09-001/FRONTEND_V1_FINAL_ACCEPTANCE.md) |
| [WP03 赵君豪](../collab-log/members/赵君豪_WP03_个人操作日志.md) | AST、套件、属性测试及冻结理解评分，11 条 | [原始会话](../transcripts/TP-PHASE-03.md) · [复验证据](../reports/phase05/T02_SOURCE_UNDERSTANDING.md) |
| [WP04 马雪朋](../collab-log/members/马雪朋_WP04_个人操作日志.md) | WASI、缺陷回归、F13 与固定分母，9 条 | [原始会话](../transcripts/TP-PHASE-04.md) · [复验证据](../reports/phase06/MUTATIONS.md) |
| [WP05 王选中](../collab-log/members/王选中_WP05_个人操作日志.md) | 工作包、Git、会话和工程工具链，10 条 | [原始会话](../transcripts/TP-COURSE-FINAL-001.md) · [复验证据](../reports/course-final/TOOLCHAIN.md) |

[五人总索引](../collab-log/LOG.md) · [20 条历史摘要与明细对照](../collab-log/COURSE_HISTORY.md) · [日志校验脚本](../hooks/verify_member_logs.py)

## 目录入口

[完整 Git 路径清单](../reports/course-final/repository-index.txt) · [分支与工作树审计](../reports/course-final/WORKTREE_AUDIT.md)

| 目录 | 内容 |
|---|---|
| `.run/`、`main.py` | PyCharm 共享启动、Uvicorn 入口 |
| `backend/`、`frontend/` | FastAPI、SQLite、AST、执行与模型 Provider，以及同源 Jinja 与静态资源 |
| `tests/`、`eval/` | 平台测试、固定样本、冻结评测及实验工具 |
| `docs/`、`reports/` | 规格、工作包、历史验收、原始报告与课程验证 |
| `collab-log/`、`transcripts/` | 工作记录、Bug 及原始会话摘录 |
| `.claude/`、`.mcp.json`、`hooks/`、`mcp-server/` | Skills、Reviewer、MCP stdio、Git Hook 与校验入口 |
| `presentation/` | 正式课件、演示手册和备份视频 |
| `.git/`、`.idea/`、`.venv/`、`.runtime/`、`data/` | Git 元数据、用户 IDE、本地解释器、模型／WASI 缓存和数据库。交付包按 Git 跟踪清单打包。 |
