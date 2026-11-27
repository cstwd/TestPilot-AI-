# TP-COURSE-REMEDIATION-001 · Loop 回执

WP05 王选中负责，Codex 执行。Codex Goal 已实际激活和完成。它在当前会话中由原生 `create_goal` 创建，再以 `update_goal` 记录真实终态。对应 Codex 产品的 [/goal 运行机制](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex)。

| 轮次 | 实际输入及反馈 | 决策和结果 |
|---|---|---|
| CLI 尝试 | Claude Code 2.1.308，OAuth 状态可读。使用 PowerShell 包装器实际执行 `claude -p`，禁用文件/MCP 工具。 | 服务端实际返回 403、退出 1，0 tokens，停止该路径。回执保留。 |
| Goal 第 1 轮 | 固定输入正向复算通过。Python -O 的负向运行退出 1，错误明确说明断言必须启用。 | 该负向只覆盖执行模式，调整为直接验证冻结数据漂移。Goal 原始创建回执为 active。 |
| Goal 第 2 轮 | 在固定提交 617fe45 上，将冻结输入的第一个种子 513 改为 514，只写临时副本。原命令入口拒绝，诊断指向冻结源、规则、种子或清单差异。 | CLI 实测退出 1，恢复到原始输入路径后复算成功，检出 0、81、104、105。原清单和汇总分别对比前后 SHA-256 均一致。 |
| 终态 | 原始通过、变更拒绝、固定输入完整性三条件均满足。 | Goal 工具回执 complete，持续 39 秒。 |

原始材料包括 [尝试脚本](TP-COURSE-REMEDIATION-001/run-loop-round.ps1)、[Prompt](TP-COURSE-REMEDIATION-001/loop-prompt-1.txt)、[Claude 403 JSON](TP-COURSE-REMEDIATION-001/loop-response-1.json)、[Goal 创建、实测脚本与原始输出](TP-COURSE-REMEDIATION-001/goal-receipts.json)、[终态工具回执](TP-COURSE-REMEDIATION-001/goal-complete.json)。这是工程验证任务的 Goal，Claude 路径保留为失败尝试。
