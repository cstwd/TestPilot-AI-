# 课程关键会话导出索引

## 已实际导出

| 会话 ID | 客户端和任务 | 原始导出 | 关联 Git 与证据 |
|---|---|---|---|
| `f3144135-6acf-4076-b274-b9bda8939531` | Claude Code 2.1.308。课程 CI 冻结评测的失败路径验证。 | [Claude 原生 /export](TP-COURSE-REMEDIATION-001-claude-attempt.txt) | CI 实现 `617fe45`、Loop `a726024`；[真实导出终端回执](../../reports/TP-COURSE-REMEDIATION-001/export-terminal.json)。 |

在隔离工作树以 `claude --resume` 打开该会话，运行 `/export ../../collab-log/transcripts/TP-COURSE-REMEDIATION-001-claude-attempt.txt`。终端返回 Conversation exported to。文件为 1110 字节，SHA-256 `0e5f46a9306000dc0d033303163f0eefdbe11a90b0168dbd93861c735cf1ba07`。原文包含完整 Prompt 和实际 403 结果。文件按字节保留。

## 现有历史证据与待补范围

| 阶段 | 历史材料 | Git / Bug | /export 状态 |
|---|---|---|---|
| 需求分析 | [三问访谈](../../transcripts/requirements-interview.md) | `be2813f`，规格 | Codex 摘录，缺对应 /export。 |
| AI 开发 | [阶段五](../../transcripts/TP-PHASE-05.md)、[阶段六](../../transcripts/TP-PHASE-06.md) | `8923f2c`、`98adf18`；[模型格式](../bugs/TP-MODEL-SCHEMA.md) | Codex 历史来源可定位，Claude 根项目无该历史会话。 |
| Bug 修复 | [F13 迁移与验收](../../transcripts/TP-PHASE-05.md) | `5b757b9`、`8923f2c`；[定位缺陷](../bugs/TP-F13-IS-NOT.md) | 可用 Prompt、Git 和测试原始证据；缺该会话的 /export。 |
| 测试与验证 | [课程验证任务](../../transcripts/TP-COURSE-FINAL-001.md)、[本次 Loop](../../reports/TP_COURSE_LOOP_EVIDENCE.md) | `617fe45`、`a726024`；[原始 Goal 回执](../../reports/TP-COURSE-REMEDIATION-001/goal-receipts.json) | 只完成本次 Claude 验证失败会话的原生导出。 |

| 本轮找到的历史 Prompt 原件 | 原始位置、身份与校验 | 交付和关键执行结果 |
|---|---|---|
| [WP09 用户消息](WP09-001-original-prompt.txt) | Codex 会话 `01a21b37-6705-7041-b791-69105c8abe9e`，2026-11-27 17:27:17 北京时间，原始用户消息文本；5,067 字节、SHA-256 `43874104eb590c525f6a32dc0e030e6af8edbb7548168d6fa3e93b86cb719319`。 | `d872fa1`，[真实六页 E2E](../../reports/WP09-001/END_TO_END_ACCEPTANCE.md)、[完整输出](../../reports/WP09-001/raw/final-full-verify.txt)。 |
| [Demo Lab 用户原附件](WP03-DEMO-LAB-001-original-prompt.txt) | Codex 会话 `01a21c79-6994-7500-b630-e3d5c548d877`，2026-11-27 18:07:47 北京时间；用户贴入附件完整字节 14,763，SHA-256 `9fd9fc58cf3359d1ab3ea2d181ee3439be59e4bbca6d184a0c4db90a6031df67`。 | `f563c6d`、`cb91a19`、`3a5d597`，[数据集实测](../../demo/TestPilot-Demo-Lab/reports/dataset_validation.md)、[模型盲测错误原回执](../../demo/TestPilot-Demo-Lab/reports/product_blind.json)。 |

上表两份属于原始 Prompt 的直接保全。对应历史 Codex 会话仍无 Claude /export 产物。

历史 Codex 原材料未转录为 Claude 会话。需要课程负责人确定可否采用历史 Codex 原生记录与已取得的 /export 组合，或提供相关真实 Claude 会话。
