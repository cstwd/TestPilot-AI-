# 基线与旧稿核对

| 版本 | 定位 | 本次用法 |
|---|---|---|
| `0d9e893` | 第二轮课程终验，私有远端课程分支本地跟踪记录 | 64 行历史状态、八份原文、第三轮 CI、五份岗位日志 |
| `000a19c` | 第三轮 Windows 托管 CI 的被测提交 | 168 Pytest、3 Node、另 8 项 Demo Lab 评分 |
| `039b14d` | 本次开工时本地同名分支的 Phase 07 产品快照，实际实现为 `fed7a62` | 7 个样本、浏览器实录、报告与独立变异实例；本机 173 Pytest、3 Node，另有 1 项定位测试 |
| `6a77ef2` | 两条本地证据历史的共同祖先 | 分别提取原记录，材料不做分支合并；本轮提交可用 `git log -- presentation/TP-FINAL-DELIVERY-001` 定位。 |

项目原稿为仓库 `presentation/TestPilot_AI_课程汇报.pptx`，共 8 页。旧稿依次展示封面、产品流程、AST、magnitude 回归、F13、四组评测、模型证据及五人分工。新增的 15 页汇报大纲沿用可验证的流程和评测，在相应页面列入教师评分、工具回执、双案、Demo Lab 回归和最新模型边界。原 8 页幻灯片随仓库快照原样保留。新旧运行的样例和 ID 逐处标明。

规范演化依次为 `8038be2` 初版、`097358b` 阶段验收约定、`4b1b574` V2 工具链。实际为 AGENTS.md，图 4 接受 AGENTS.md 或 CLAUDE.md。可执行 `git log --all -- AGENTS.md`，使用 `git show <提交>:AGENTS.md` 比较。旧版基线保持历史证据用途。

**归档截止补充**　产品快照固定至 cf448f3。F05 专项 d8226c3（实现 b40b54e）有两次真实 Qwen 修复推理，原套件 #8 从 1 通过、2 失败、1 跳过变为 3 通过、0 失败、1 跳过。该专项独立于 Demo Lab 的课堂模板套件 #1 和 F03 冷启动试跑。cf448f3 五份周报的编排日期与实际证据时间分别保留。[F05 专项](../04_TESTING_EVIDENCE/F05_AI_REPAIR/reports/TP-F05-AI-REPAIR-001/TP_F05_AI_REPAIR_001_ACCEPTANCE.md) · [周报版日志](../03_TEAM_COLLABORATION/weekly/collab-log/members/)
