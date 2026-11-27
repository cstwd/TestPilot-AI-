# TP-PHASE-04 正式验收报告

日期 2026-11-27。项目 TestPilot AI，工作目录 `D:\TestPilot AI`。阶段负责人陈帅廷，开发、实测、复核与归档的实际操作者见[协作记录](collab-log/PHASE_04.md)。

**工程验收通过，待陈帅廷人工签收。** 最终全量回归 146 项通过，包括原 89 项、本阶段 47 项及既有 AST 工作台 10 项。已从正常产品入口完成本机 AI 初始生成、隔离变异、补测校验和全清单复验。[最终 JUnit](reports/phase04/final-junit.xml)

## 真实端到端结果

在 Windows 11 上直接启动根目录 `main.py`，从同源 HTTP 接口导入 `bonus.py` 并选择顶层函数 `bonus`。两种初始套件使用同一修订、同一算子配置和相同的 9 个变异位置。每次计分之前均在原版源码建立绿色基线。模型推理使用本机 Ollama 中的 `qwen2.5-coder:0.5b` GGUF，实际运行使用独立 WASI Pytest。模型下载后可离线执行，本次推理无 API 费用。[样例源码](eval/phase04/bonus.py) · [本机模型设置及零费用边界](docs/phase04/LOCAL_MODEL.md)

| 初始测试 | 初测 | 本地模型补测并复跑全部 9 项后 | 未杀死的位置 |
| --- | ---: | ---: | --- |
| 本机模型生成，初始 1 条测试 | 3/9，33.33% | 4/9，44.44% | 4 存活，1 执行错误 |
| F09 本地模板生成，初始 4 条测试 | 4/9，44.44% | 5/9，55.56% | 2 存活，2 执行错误 |

两条路径均新增检出 L9 的异常抑制。原版 `bonus(-1, True)` 会抛出 `ValueError`，删除 `raise` 的变异版未抛出，Pytest 记录 `DID NOT RAISE`。AI 初始套件那一轮提出 4 个去重候选，整批在原版上 2 通过、3 失败（含 1 个原始测试）。保留通过原版校验的 1 个追加断言后，原版 2 通过，再在 9 个副本上完整重跑。报告同时保留错误预期、原始输出、候选筛选及逐例执行证据。[模型前后对照](reports/phase04/AI_FEEDBACK.md) · [每处变异的前后判定](reports/phase04/MUTATION_SCORE.md)

最近一次验证模型身份的 F09 任务为 `c9638b45-3f74-4bf0-b452-0670a7921f31`，F13 会话为 `6151a7c2-6c8c-4731-9df8-b9db2762eed1`。模型摘要、原测试摘要、变异副本摘要、节点、退出码、行及分支覆盖率都可在导出中核对。覆盖率沿用 F10 的计量方式，变异得分的分母为冻结清单总数。[实际 AI 初始测试](reports/phase04/ai-hardened-task.json) · [完整对照实验与 impact 事件](reports/phase04/ai-hardened-campaign.json) · [复算输出](reports/phase04/verified-ai-hardened.txt)

## 工程交付与独立复核

| 项目 | 实际完成情况与证据 | Git |
| --- | --- | --- |
| 开发前审计 | 检查 F07–F12、SQLite、Pytest、WASI、Coverage、模型和测试基线。PHASE-01 至 PHASE-03 的归档保持原样。`f31a901`、`da798a4`、`7422857` 均为当前提交的祖先。[审计](docs/phase04/AUDIT.md) | `8eb13f9` |
| 工具选型 | Win11 实装两者。mutmut 3.8.1 原生 CLI 以退出码 1 要求 WSL；Cosmic Ray 8.9.0 跑完 31 个原生作业，串行 28.715 秒，两分片 15.931 秒。两个工具均提取真实变异在 WASI 执行。采用 Cosmic Ray 静态算子，使用 F10 和测试断言证据独立判读。[选型报告与原始测量](docs/phase04/TOOL_SELECTION.md) | `b784715` |
| 生成及评分 | 六类算子，SHA-256 验证的独立副本，稳定 UUID，不按覆盖率筛选。错误、超时、取消、未运行均在分母中，等价候选单独标注。[算子测试](reports/phase04/MUTATION_OPERATORS.md) · [模块报告](reports/phase04/F13_MODULE_ACCEPTANCE.md) | `5b757b9`、`6de6844` |
| 本机 AI | 签名、契约、旧测试摘要及存活位置进入推理。选用本机模型时检查回环服务、GGUF、远端转发标志，保留模型答复与拒绝原因。[反馈适配](backend/mutation_feedback.py) · [本地验证接口](backend/local_ollama.py) | `5be8d12`、`d847cab`、`43c01c5` |
| 服务与界面 | 运行 `main.py`，在已完成 F12 任务点击“评估变异测试与补测”。创建、运行、终止、继续、查询候选与下载完整 JSON 已接入同一服务。Edge 实测从 F12 打开 F13、计算 1/1、导出报告与查看失败反馈。额外浏览器测试使用标注的呈现夹具校验错误态，生成效果来自上表的真实模型推理。[运行说明](README.md) · [接口](backend/mutation_web.py) · [浏览器测试](tests/test_mutation_ui.py) | `f6daaa1` |
| 中止与恢复 | 实测运行中终止 WASI worker、清理资源、同库并发返回 409。从运行中 SQLite 的一致性快照另启 `main.py`，续跑后清单项各保存一次。红基线保留执行结果，得分为 null。[生命周期证据](reports/phase04/lifecycle.txt) · [判读独测](reports/phase04/results-test.txt) | `6de6844`、`f6daaa1` |
| 历史与复验 | 同时保留早期模型输出被拒、整套补测基线失败的会话，以及成功的前后对照、输出摘要、计分复算工具和原 89 个节点的重新执行。[失败首轮](reports/phase04/live-first-experiment.json) · [另一轮红基线](reports/phase04/ai-initial-campaign.json) · [原 89 项 JUnit](reports/phase04/original-89.xml) | `eab8f4f`、`bfc05d7` |
| 独立审查修正 | 复核者用真实 WASI 重现了 `pytest.raises` 被别名导入时漏判。现结合实际执行的测试源码核对绑定和 traceback，验证了三种合法导入与两种自定义绑定。使用修正后的判读器再核对两条路径全部 36 条观察，判定及节点均与原始输出一致。[修正实测](reports/phase04/assertion-alias.txt) | `8607ffa` |

## 回归与运行条件

原 PHASE-03 JUnit 中的 89 个节点已逐一重跑，89 通过，耗时 502.50 秒。独立核对脚本使用原始节点标识进行集合比较。[原 89 项逐条输出](reports/phase04/original-89.txt) · [节点比较脚本](eval/phase04/check_regression.py)

开发期间一次并行验证收集 130 项，129 通过、1 失败。当时多组 WASI 任务共享宿主临时根目录，旧版 `test_deadline_and_cleanup` 正确观察到执行超时，但它对整个目录进行前后快照，快照中出现另一个仍在运行的 job。该批运行结束后核对，两次快照中的临时目录均已回收。保留该轮日志与完整 JUnit，并按原断言在最终回归中复测。[中间轮执行日志](reports/phase04/full-suite.txt) · [当轮异常与两个目录名](reports/phase04/full-suite.xml)

最终执行开启 `TESTPILOT_F13_LIVE=1`，146 项全部通过，耗时 1230.49 秒，退出码 0，失败、错误和跳过均为 0。原 89 项对应的 20 个文件与 `7422857` 逐文件比较相同。超时清理用例通过，结束后检查 `.runtime/job-*` 为空。最终结果提交为 `38dd0bc`。[完整输出](reports/phase04/final-suite.txt) · [逐节点集合核对](reports/phase04/regression-verification.txt)

## 复验命令

以下命令从项目根目录运行。PyCharm 使用同一项目解释器，按 README 启动单服务。实时 AI 验收需先有上述已安装的本机模型。重演脚本默认生成独立 SQLite 及导出目录，既有验收文件可只读复算。

```powershell
$oldNodes = .\.venv\Scripts\python.exe -m eval.phase04.check_regression
.\.venv\Scripts\python.exe -m pytest @oldNodes -v
$env:TESTPILOT_F13_LIVE='1'
$env:TESTPILOT_MUTATION_MODEL='qwen2.5-coder:0.5b'
.\.venv\Scripts\python.exe -m pytest tests -v --durations=8
.\.venv\Scripts\python.exe -m eval.phase04.ai_initial_campaign
.\.venv\Scripts\python.exe -m eval.phase04.check_experiment reports/phase04/ai-hardened-task.json reports/phase04/ai-hardened-campaign.json eval/phase04/bonus.py
```

## 范围与待办

- 当前算子配置面向可唯一定位的顶层同步函数。超过 128 个位置时整体拒绝并提示，零位置的得分为 null。语义等价候选保留在固定总数中。
- 执行器对 WASI worker 实施终止和资源上限。取消请求会阻止后续模型调用，已发出的本机 HTTP 推理受配置时限约束。
- 恢复实测使用运行中的 SQLite 快照和新服务进程。操作系统强制结束 Web 进程时，宿主临时目录的回收仍待专项验证。
- 本次验证使用 Windows 根入口与 Edge。PyCharm 的交互式绿色 Run 按钮和 Debug 断点沿用前三阶段验收记录；本阶段没有重新进行人工 IDE 签收。
- 验收样例中仍有未杀死的变异。每个位置的模型建议、实测状态及相应证据已归档，供团队后续补充业务契约与测试。项目负责人陈帅廷待人工审核。
