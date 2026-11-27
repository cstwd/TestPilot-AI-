# TP-PHASE-02 核心业务引擎验收

**工程验收通过，待项目组长陈帅廷审核。** 2026-11-27 在 Windows 11 上完成六个模块的独立测试和审查、实际浏览器交互、统一回归与 PyCharm 启动复验。最终全套平台测试 **35 passed in 153.33s**，退出码 0。[最终测试输出](reports/phase02/full-suite.txt)

项目根目录为 `D:\TestPilot AI`，分支为 `main`。初始工程提交 `8038be2`，PHASE-01 验收提交 `88ebf23`，本阶段规范独立提交 `097358b`，最终受测业务代码提交 **`f31a901`**。根入口、共享 PyCharm 配置和上一阶段验收报告及证据保留原件。本文及六份模块报告列出的路径均相对于项目根目录。[启动入口](main.py) · [共享配置](.run/TestPilot_AI.run.xml) · [PHASE-01 验收记录](TP_PHASE_01_ACCEPTANCE.md)

## 模块验收

每份报告附实现路径、命令、实测结果、审查记录、提交和适用边界。下表的独立测试与最终全套回归有重叠。

| 模块 | 已验证的用户操作 | 独立验证 | 实现提交 |
| --- | --- | --- | --- |
| [F01 项目与导入](F01_MODULE_ACCEPTANCE.md) | 创建项目、导入 Python 文件、保存并回看多个修订；拒绝非法文件名 | 后端 5 项，Edge 1 项通过 | `77e6177` |
| [F02 AST 分析](F02_MODULE_ACCEPTANCE.md) | 展示类、函数签名及行号，定位语法错误；分析期间源码副作用未运行 | 后端 3 项，Edge 1 项通过 | `743e24f` |
| [F03 自动测试生成](F03_MODULE_ACCEPTANCE.md) | 按签名和显式示例生成、审阅并保存套件，生成后关联真实隔离首跑 | 后端 2 项，Edge 1 项通过；端到端另验自动首跑 | `2b2185c`、`f31a901` |
| [F04 Pytest 执行](F04_MODULE_ACCEPTANCE.md) | 从工作台运行原套件，查看真实退出结果、失败节点、日志及覆盖行；验证访问权限、超时与清理 | 运行服务与执行器 7 项，Edge 1 项通过 | `d988ecc` |
| [F05 缺陷与回归](F05_MODULE_ACCEPTANCE.md) | 从失败节点登记缺陷，使用原套件对同名文件新版本回归，跟踪原始运行及修复状态 | 后端 2 项，Edge 1 项通过 | `b6f4ef5` |
| [F06 质量与导出](F06_MODULE_ACCEPTANCE.md) | 查看选定运行的指标、计数、原始日志和缺陷历史，下载与页面数据一致的 JSON | 后端 4 项，Edge 1 项通过 | `c874456` |

## 从真实失败到修复验证

在临时 SQLite 数据库创建项目，导入带有显式预期 `magnitude(-3) == 3` 的源文件。生成操作保存套件 1 并触发隔离 Pytest 首跑。首跑捕获负数处理错误，随后从失败节点登记缺陷 1，导入修复版同名文件并执行回归。两次运行使用相同套件及 SHA-256，原始记录仍可按 ID 回读。[缺陷版源码](eval/phase02/buggy/magnitude.py) · [修复版源码](eval/phase02/fixed/magnitude.py) · [端到端测试](tests/test_phase02_flow.py)

| 源码和运行 | 通过 | 失败 | 错误 | 跳过 | 通过率 | 实测覆盖行 | 原失败节点 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [修订 1 / 运行 1](reports/phase02/buggy-report.json) | 5 | 1 | 0 | 1 | 83.33% | 2/2 | `test_generated.py::test_example_3` 断言失败 |
| [修订 2 / 运行 2](reports/phase02/fixed-report.json) | 6 | 0 | 0 | 1 | 100% | 2/2 | 同一节点通过，缺陷状态更新为已解决 |

通过率分母包含通过、失败和错误。两次跳过的均为 Hypothesis 属性测试，原因写入了来宾日志。两版均覆盖了全部两行可执行代码，只有修复版满足该负数示例的预期。以上是被测项目的实际结果，35 项是平台自身的回归测试。[端到端原始输出](reports/phase02/e2e.txt)

## 执行环境和复验命令

FastAPI 提供六个同源工作页面、JSON API 和 SQLite 持久化。业务执行使用独立临时目录和固定的 Pytest 调用。独立宿主 worker 通过 WASI 运行来宾 CPython，仅读取挂载的源码和测试依赖。断网、禁止启动子进程、内存和输出上限、超时清理均经过实际测试。日志触及上限时取消该次运行并标明日志不完整。导出的样例记录了来宾 CPython 3.15.2、Pytest 9.2.0 和 Coverage.py 7.17.5。[执行器与限制](F04_MODULE_ACCEPTANCE.md) · [隔离测试输出](reports/phase02/F04-runner-test.txt)

在项目根目录复验统一回归：

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

单独复验业务闭环：

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_phase02_flow.py -q -s
```

闭环独立执行结果为 `1 passed in 17.57s`。首次全套运行有 `1 failed, 34 passed in 169.20s`。F04 浏览器用例在页面跳转后读取旧响应体，Playwright 无法取回该数据。修正后的用例确认提交成功，按新页面的运行 ID 读取持久化数据，核验关联套件与运行状态。完整重跑结果为 `35 passed in 153.33s`。[首次失败记录](reports/phase02/first-integration.txt) · [修正后的用例](tests/ui_workbench.py) · [最终回归输出](reports/phase02/full-suite.txt)

## PYCHARM_RUN_ACCEPTANCE

| 检查 | 实测情况 |
| --- | --- |
| 根入口与自动打开 | 在 PyCharm 2026.1.2 打开根目录 `main.py` 并点击绿色 Run。默认浏览器 Edge 自动打开 `http://127.0.0.1:8000/`，Dashboard 显示六个工作台入口。 |
| 接口、数据库及单服务 | 同一服务的首页和健康接口均返回 HTTP 200，页面显示后端和数据库均已连接。六个工作台的交互另由真实 Edge 验收。 |
| 停止、重启和端口冲突 | PyCharm 红色 Stop 后进程 43164 正常退出，退出码 0。入口自动化回归另验证同端口重启保留数据、占用提示、拒绝重复实例和固定自检。 |
| Debug | 以本机 PyCharm 附带的 pydevd 调试根入口。在 `backend/app.py:24` 的 `create_app` 命中断点，继续后健康接口报告开发模式与数据库均正常。 |

[PyCharm 核验记录](reports/phase02/PYCHARM.md) · [Run 控制台截图](reports/phase02/pycharm-run.jpg) · [调试协议实测日志](reports/phase02/debug.txt) · [启动回归用例](tests/test_startup.py)

## 团队归属与待办

五个工作包沿用各 20% 的计划分配。实际实现、运行、复核和归档由 Codex 主代理及子代理执行。分工、独立审查与修复归属可分别复查。[协作记录](collab-log/PHASE_02.md) · [工程缺陷记录](collab-log/bugs/PHASE_02.md) · [成员贡献分配](collab-log/member_contributions.md)

- 当前可运行生成模式为本地模板，在线模型接入保留适配接口。测试生成支持顶层同步函数；导入范围为最多 128 KiB 的单个 UTF-8 Python 文件。
- 当前来宾支持普通 Pytest 及行覆盖率采集。Hypothesis 属性建议和相应用例源码随套件保留，本期来宾缺少运行其所需的依赖，适用用例显式跳过。
- 质量导出为 JSON。来宾内测得的结果与日志支持重运行和复核，对刻意篡改来宾测量过程的程序没有独立的结果真实性认证。
- 待陈帅廷审核本阶段工程交付并决定是否进入 PHASE-03。
