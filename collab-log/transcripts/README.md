# 课程关键会话导出索引

## 已实际导出

| 会话 ID | 客户端和任务 | 原始导出 | 关联 Git 与证据 |
|---|---|---|---|
| `f3144135-6acf-4076-b274-b9bda8939531` | Claude Code 2.1.308。课程 CI 冻结评测的失败路径验证。 | [Claude 原生 /export](TP-COURSE-REMEDIATION-001-claude-attempt.txt) | CI 实现 `617fe45`、Loop `a726024`；[真实导出终端回执](../../reports/TP-COURSE-REMEDIATION-001/export-terminal.json)。 |

在隔离工作树以 `claude --resume` 打开该会话，运行 `/export ../../collab-log/transcripts/TP-COURSE-REMEDIATION-001-claude-attempt.txt`。终端返回 Conversation exported to。文件为 1110 字节，SHA-256 `0e5f46a9306000dc0d033303163f0eefdbe11a90b0168dbd93861c735cf1ba07`。原文包含完整 Prompt 和实际 403 结果。文件按字节保留。

## 现有历史证据与待补范围

[Codex 原文总索引](../../transcripts/README.md)包含六组阶段原始 Prompt 与关键输出、两份单独恢复的 Prompt，并保留各文件的来源。

| 阶段 | 历史材料 | Git / Bug | /export 状态 |
|---|---|---|---|
| 需求分析 | [三问访谈](../../transcripts/requirements-interview.md) | `be2813f`，规格 | Codex 摘录，缺对应 /export。 |
| AI 开发 | [阶段五](../../transcripts/TP-PHASE-05.md)、[阶段六](../../transcripts/TP-PHASE-06.md) | `8923f2c`、`98adf18`；[模型格式](../bugs/TP-MODEL-SCHEMA.md) | Codex 历史来源可定位，Claude 根项目无该历史会话。 |
| Bug 修复 | [F13 迁移与验收](../../transcripts/TP-PHASE-05.md) | `5b757b9`、`8923f2c`；[定位缺陷](../bugs/TP-F13-IS-NOT.md) | 可用 Prompt、Git 和测试原始证据；缺该会话的 /export。 |
| 测试与验证 | [课程验证任务](../../transcripts/TP-COURSE-FINAL-001.md)、[本次 Loop](../../reports/TP_COURSE_LOOP_EVIDENCE.md) | `617fe45`、`a726024`；[原始 Goal 回执](../../reports/TP-COURSE-REMEDIATION-001/goal-receipts.json) | 只完成本次 Claude 验证失败会话的原生导出。 |

历史 Codex 原材料未转录为 Claude 会话。需要课程负责人确定可否采用历史 Codex 原生记录与已取得的 /export 组合，或提供相关真实 Claude 会话。
