# TP-COURSE-REMEDIATION-001 · CI 与冻结 AI 评测验收

**CI 通过。** WP05 王选中负责，Codex 执行，独立复核为 Codex `testpilot_reviewer`。第三次托管运行在 `000a19c` 上完成 168 项 Pytest 和 3 项 Node，独立 Demo Lab 评分 8 项通过。两次先前失败与最终成功分别归档。各 ZIP 的 SHA-256 已与 GitHub artifact 摘要逐一对照。

| 环境和基线 | 结果 | 可核验回执 |
|---|---|---|
| 本机 Windows 隔离工作树，`617fe45` | 原全量 168 Pytest、3 Node，0 失败、0 跳过，Hook 退出 0。Pytest 用时 13 分 49 秒。 | [本机验收](TP-COURSE-REMEDIATION-001/local-full.txt) |
| 托管 Windows 2025，`617fe45` | 165 Pytest 通过、3 失败，3 Node 和 8 项 Demo Lab 评分通过，离线重放通过。Actions 终态 `failure`。 | [GitHub run 1](https://github.com/cstwd/TestPilot-AI-/actions/runs/45989629255) · [完整输出](TP-COURSE-REMEDIATION-001/ci-github/45989629255/verify-full.txt) · [终态 JSON](TP-COURSE-REMEDIATION-001/ci-github/45989629255/receipt.json) |
| 托管 Windows 2025，`6a77ef2` | 165 Pytest 通过、3 失败，3 Node 和 8 项 Demo Lab 评分通过，离线重放通过。Actions 终态 `failure`。 | [GitHub run 2](https://github.com/cstwd/TestPilot-AI-/actions/runs/45990819569) · [完整输出](TP-COURSE-REMEDIATION-001/ci-github/45990819569/verify-full.txt) · [终态 JSON](TP-COURSE-REMEDIATION-001/ci-github/45990819569/receipt.json) |
| 托管 Windows 2025，`000a19c` | 168 Pytest 通过、0 失败，3 Node 和 8 项 Demo Lab 评分通过，离线重放通过。Actions 终态 `success`。 | [GitHub run 3](https://github.com/cstwd/TestPilot-AI-/actions/runs/45992897616) · [完整输出](TP-COURSE-REMEDIATION-001/ci-github/45992897616/verify-full.txt) · [终态 JSON](TP-COURSE-REMEDIATION-001/ci-github/45992897616/receipt.json) |
| 托管负向 `6a77ef2` 与 `000a19c` | `python -O` 关闭必要断言时退出 1。工作流实际校验退出码，负向 JSON 为 failed。 | [最终负向](TP-COURSE-REMEDIATION-001/ci-github/45992897616/offline-failure.json) |

## 入口、语料和失败规则

- [工作流](../.github/workflows/course-verification.yml) 在指定分支 push、PR 与手动触发时运行，使用 Windows 2025、Python 3.13.11、Node 24.13.0、Microsoft Edge 和锁定项目依赖。模型复算无需模型机器、API 密钥或付费推理服务。全量复用 `hooks/verify.py --scope full`。
- `python -m eval.phase05.verify_frozen --report <新文件>` 按固定源码、种子 513/727/941、评分规则和每组 117 位置，逐轮读取历史模型与 WASI 回执。十项目，每组 30 次，共 120 次。A/B/C/D 分别为 0/81/104/105，全部字段与冻结汇总一致。历史输入为 `8923f2c`，大模型权重与修订、小模型 Ollama 摘要和四份固定输入 SHA-256 均可查。[协议](../eval/phase05/PROTOCOL.md) · [最终模型评测](TP-COURSE-REMEDIATION-001/ci-github/45992897616/offline-evaluation.json)
- `6a77ef2` 落实独立评审找到的三处缺口。变更模型身份、删掉显式空值指标和非法分组均实测返回 1，输出失败 JSON。使用原始输入通过。Goal 另验证改动临时冻结种子后拒绝并恢复原始结果。[复核](TP-COURSE-REMEDIATION-001/ci-independent-review.json) · [Goal](TP_COURSE_LOOP_EVIDENCE.md)
- 前两轮的 F05、MCP 真实执行、F04 首跑出现三次请求或 WASI 超时。下一版增加固定代码的 WASI 预热，只运行 `print(2 + 2)`，用同一个 runner 上的本地编译缓存。第三轮 warmup 显示 compiled=1、written=1，原 168 项随后全部通过。原沙箱约束、业务超时和测试断言保持原样。定向复验相同三项本机 3 通过。[冷缓存实测](TP-COURSE-REMEDIATION-001/wasi-cold-warmup.json) · [托管预热](TP-COURSE-REMEDIATION-001/ci-github/45992897616/wasi-warmup.txt) · [本机定向](TP-COURSE-REMEDIATION-001/local-affected-regression.txt)
- 托管第三轮源提交 `000a19c`，归档 run/job、提交、runner 版本、JUnit、实际输出、评测及错误回执。后续材料提交不影响执行入口和产品源码。
