# TP-PHASE-01 协作日志

2026-11-27，Windows 11 本机。组长按任务书统一协调。下表记录此轮可核对的代理操作，不推算成员工时。

| 工作包及责任人 | 实际操作人 | 本次操作及结果 | 证据 |
| --- | --- | --- | --- |
| WP01 陈帅廷 | Codex 主代理、服务子代理 | 检查目录及工具，备份示例，创建 Git main、虚拟环境与单服务入口。实现 SQLite 生命周期、进程退出和端口诊断 | `transcripts/original-main.py.txt`、`main.py`、`backend/`、`reports/startup-check.txt` |
| WP02 陈万策 | Codex 主代理、前端子代理；需求提出者答复 | 完成三问访谈；按答复编制 SPEC。实现同源 Dashboard，做真实 Edge 桌面、窄屏和断连恢复检查 | `transcripts/requirements-interview.md`、`docs/SPEC.md`、`reports/dashboard-check.txt` |
| WP03 赵君豪 | Codex 服务、前端子代理 | 编写固定可信样例和可调用的 Pytest 执行器，用页面按钮触发并核对实际结果 | `backend/self_test.py`、`backend/sample_case.py`、`tests/test_dashboard.py` |
| WP04 马雪朋 | Codex Reviewer（规划子代理复核服务/前端）、服务及前端子代理修复、主代理复验 | 发现不兼容 SQLite 版本会持续等待；补启动退出、保留原库与等待超时回归。修正 Windows 控制台退出码和浏览器图标请求 | `collab-log/bugs/LOG.md`、`reports/startup-check.txt` |
| WP05 王选中 | Codex 主代理、规划子代理 | 建立五份工作包、贡献分配、架构、排期及风险表。实际操作 PyCharm 与浏览器并独立验证调试协议；汇总验收和真实提交 | `docs/work-packages/`、`reports/pycharm-debug.md`、`TP_PHASE_01_ACCEPTANCE.md` |

本阶段 Git 提交的实际操作者使用 Codex 身份。各工作包给出路径过滤命令，阶段报告记录基线提交。以上记录未代替五位成员签收。
