# TP-COURSE-FINAL-001 课程要求逐项核对

本页是 TP-COURSE-FINAL-001 的历史工程核对，范围来自当时的原始任务书。教师五张原图的现行对照见[课程要求映射](COURSE_REQUIREMENTS_MAPPING.md)。项目组长人工签收独立办理。[原始任务书](../transcripts/TP-COURSE-FINAL-001.md) · [五人记录](../collab-log/COURSE_HISTORY.md) · [开工审计及验收基线](../reports/course-final/WORKTREE_AUDIT.md)

| 课程要求 | 完成及核验状态 |
|---|---|
| F01–F06、F13 与业务链路 | 真实 Edge、同源 FastAPI、SQLite、WASI 验证缺陷版到修复版、质量导出及 F13。 [演示实测](../reports/course-final/demo.txt) · [测试](COURSE_TESTING.md) |
| 本地 Qwen3.8-27B | 历史连续 10/10；PHASE-06 有 F02/F03/F09/F13 实测，主线实际通过本机 Vulkan 健康探针。 [历史](../reports/phase05/T01_PERFORMANCE.md) · [统一模型链路](../reports/course-final/model-health.json) · [主线探针](../reports/course-final/model-main-live.json) |
| 规格与上下文 | [SPEC](SPEC.md) · [AGENTS](../AGENTS.md) · [架构](ARCHITECTURE.md) |
| 两个可用 Skill | `verify` 与 `testpilot-workflow` 通过定义检查，Codex 实际读入和执行。 [工具链](../reports/course-final/TOOLCHAIN.md) |
| MCP | stdio 握手与两项工具实际调用成功，真实 WASI 记录 6 通过／1 跳过，坏参数被拒。 [实测](../reports/course-final/toolchain.txt) |
| 确定性 Hook | Git 实际触发拒绝和通过，已用于仓库课程提交。 [实测](../reports/course-final/toolchain.txt) |
| 自定义 Subagent / Loop | 独立 Reviewer 复现并提交结构化问题报告，MCP 记录包含实际失败、诊断、修复和复验。 [审查](../reports/course-final/REVIEWER.md) · [循环](../reports/course-final/LOOP.md) |
| 自动化、属性、差分与 AI 评估 | 固定快照 163 项 Pytest、3 项 Node 通过，后续模型变更与 F13 另做定向回归。覆盖真实 Edge、WASI、宿主 Hypothesis 与冻结差分。[全量复验](../reports/course-final/acceptance-72a53b8.txt) · [测试说明](COURSE_TESTING.md) · [只读复算](../reports/course-final/offline-replay.txt) |
| 五人协作及 20% × 5 | 20 条有证据恢复记录，五个 WP 全覆盖，实际操作者和贡献份额可区分。 [日志](../collab-log/LOG.md) · [贡献](COURSE_TEAM_CONTRIBUTIONS.md) |
| Bug 档案和 AI 引入 | 至少三份完整个案，包括真实本机模型参数输出格式偏离、生成器断言和 F13 定位。 [Bug 档案](../collab-log/bugs/LOG.md) |
| Prompt 和关键输出 | 15 份历史任务或阶段摘录及本次原始任务。模型评测完整交互保留在冻结原始记录。 [会话索引](../transcripts/README.md) |
| Git 与课程归档 | 保留原作者、历史分支、实际合并及按工作包提交。 [证据](COURSE_EVIDENCE_INDEX.md) |
| PPT、截图、备份视频 | 8 页可编辑 PPTX、PDF 预览、9 张截图、59 秒 H.264 备用演示。 [展示](../presentation/README.md) |

复验范围与仍待签收事项见 [课程最终报告](COURSE_FINAL_REPORT.md)。

PHASE-07 在正式产品中增加可重复的 Demo Lab 验收入口，现场操作、样本证据、报告导出和仓库回归见 [阶段验收](../reports/phase07/ACCEPTANCE.md)。
