# TestPilot AI 协作日志

[20 条历史摘要及明细对照](COURSE_HISTORY.md) · [贡献分配](member_contributions.md) · [原始会话](../transcripts/README.md) · [课程验收](../docs/COURSE_FINAL_REPORT.md)

历史原始记录继续保存在 [PHASE-02](PHASE_02.md)、[PHASE-03](PHASE_03.md) 和 [PHASE-04](PHASE_04.md)。

## 五人个人操作日志

| 工作包 | 责任成员 | 详细日志 | 操作记录 | 课程份额 |
| --- | --- | --- | ---: | ---: |
| WP01 | 陈帅廷 | [个人操作日志](members/陈帅廷_WP01_个人操作日志.md) | 9 | 20% |
| WP02 | 陈万策 | [个人操作日志](members/陈万策_WP02_个人操作日志.md) | 10 | 20% |
| WP03 | 赵君豪 | [个人操作日志](members/赵君豪_WP03_个人操作日志.md) | 11 | 20% |
| WP04 | 马雪朋 | [个人操作日志](members/马雪朋_WP04_个人操作日志.md) | 9 | 20% |
| WP05 | 王选中 | [个人操作日志](members/王选中_WP05_个人操作日志.md) | 10 | 20% |
| 合计 | 五名成员 | | 49 | 100% |

按实际历史记录恢复，会话、提交、报告及复核按对应岗位归档。贡献份额沿用课程分工，实际操作者及成员签收另行记录。可在仓库根目录执行 `python hooks/verify_member_logs.py` 核验目录、内容、引用和比例。

## TP-PHASE-01 原始协作日志

2026-11-27，Windows 11 本机。组长按任务书统一协调。下表记录此轮可核对的代理操作，不推算成员工时。

| 工作包及责任人 | 实际操作人 | 本次操作及结果 | 证据 |
| --- | --- | --- | --- |
| WP01 陈帅廷 | Codex 主代理、服务子代理 | 检查目录及工具，备份示例，创建 Git main、虚拟环境与单服务入口。实现 SQLite 生命周期、进程退出和端口诊断 | `transcripts/original-main.py.txt`、`main.py`、`backend/`、`reports/startup-check.txt` |
| WP02 陈万策 | Codex 主代理、前端子代理；需求提出者答复 | 完成三问访谈；按答复编制 SPEC。实现同源 Dashboard，做真实 Edge 桌面、窄屏和断连恢复检查 | `transcripts/requirements-interview.md`、`docs/SPEC.md`、`reports/dashboard-check.txt` |
| WP03 赵君豪 | Codex 服务、前端子代理 | 编写固定可信样例和可调用的 Pytest 执行器，用页面按钮触发并核对实际结果 | `backend/self_test.py`、`backend/sample_case.py`、`tests/test_dashboard.py` |
| WP04 马雪朋 | Codex Reviewer（规划子代理复核服务/前端）、服务及前端子代理修复、主代理复验 | 发现不兼容 SQLite 版本会持续等待；补启动退出、保留原库与等待超时回归。修正 Windows 控制台退出码和浏览器图标请求 | `collab-log/bugs/LOG.md`、`reports/startup-check.txt` |
| WP05 王选中 | Codex 主代理、规划子代理 | 建立五份工作包、贡献分配、架构、排期及风险表。实际操作 PyCharm 与浏览器并独立验证调试协议；汇总验收和真实提交 | `docs/work-packages/`、`reports/pycharm-debug.md`、`TP_PHASE_01_ACCEPTANCE.md` |

本阶段 Git 提交的实际操作者使用 Codex 身份。各工作包给出路径过滤命令，阶段报告记录基线提交。以上记录未代替五位成员签收。
