# TP-COURSE-REMEDIATION-001 · 缺口整改报告

项目 TestPilot AI。阶段一审计的八份报告来自 `D:\TestPilot AI_AUDIT\TP-COURSE-AUDIT-001`，以其中 58 个核查点建立第二轮追踪。正式基线 `3a5d597`。执行者 Codex，课程责任按 WP 分配，独立技术复核为 Codex `testpilot_reviewer`，人工确认单独核对。详细判定见 [逐项矩阵](TP_COURSE_REMEDIATION_MATRIX.md) 与 [最终验收](TP_COURSE_FINAL_ACCEPTANCE.md)。

共享目录中的 Phase 07 并行提交 `fed7a62` 继续保留。交付工作树从已测试的 `6a77ef2` 接续，单独摘取本轮两案补证，后续全部整改进入 `codex/tp-course-remediation-delivery`。GitHub 核验使用同仓库私有分支 `codex/tp-course-remediation-001`。业务及原测试由基线差异验证，PPT 使用已有归档，汇报材料没有在本轮制作。

## 教师五张原图与本轮请求

原图从本次对话附件读取。按附件顺序逐份复核，并保存文件名、字节数和 SHA-256。截图中的产品例子与交叉红队描述用于核对评分，不作为本轮的新执行任务。[原图校验索引](TP-COURSE-REMEDIATION-001/teacher-source-receipts.json)

| 原图 | 判据与实际核对 |
|---|---|
| 1，选题 | 四个示例方向为视频监控、RAG、Text-to-SQL、MiniAgent。明确允许有复杂度或创意、功能完整的自拟题，TestPilot 符合这一入口。 |
| 2，协作日志 | 每人至少一条、全组至少八条；双 Bug 及至少一个 AI 引入；保留 Prompt 和关键输出原文以及关键 /export，失败也记录，和 Git/会话一致。 |
| 3，评分 | 需求 20、扩展 5、验证 15、调试 10、协作 10、产品 20、汇报 20，合计 100，加分 +5。个人贡献系数 0.8–1.2 由个人答辩讲解确定，项目 20% 是计划责任份额。 |
| 4，仓库最低要求 | 红标 SPEC 及 AGENTS/CLAUDE 必须有。Skills、MCP、Hook、子智能体、测试及 Loop 处在蓝框可选组。任务另明确要求完成 CI 和 Loop，仍按本轮标准验收。右侧目录是参考。 |
| 5，里程碑 | 红框列定义四项为必有，最终提交为仓库、日志和幻灯片。交叉红队标为选做加分。本轮保留真实日期。 |

| 教师里程碑 | 当前可核证据 |
|---|---|
| 第 1–2 天，定义 | 自拟选题、五岗分工、AI 三问与 SPEC、AGENTS 初版 8038be2、单服务与 WASI 技术选型。项目自己的三天计划保留。CI 原阶段缺失，本轮补做。 |
| 第 2–3 天，构建 | F01–F06 按模块交付，verify、MCP、pre-commit 有原始通过回执和触发记录。 |
| 第 4–5 天，加固 | 属性、Edge E2E、差分、实测变异、Bug 修复和独立 Reviewer 有记录；红队无跨组实施证据。 |
| 第 6–7 天，复盘 | 49 条明细、上下文演化、既有 PPTX 和备用视频、课程整改报告齐。分阶段实作证据可对照，真实一周日期暂无完整材料。 |

## 执行与交付

| 工作批次 | 实际操作与验证 | 交付 |
|---|---|---|
| WP05 CI、离线 | 本机与托管测试均使用 Windows。固定模型档案、分数和变异位置均有通过与失败回执。保留第三方 runner 上的真实冷启动失败和修复复验。 | [CI](TP_COURSE_CI_ACCEPTANCE.md) |
| WP05 Loop | Claude -p 实际 403 后换原生 Goal，临时改 seeds 后拒绝，恢复原路径成功并校验原文件未变。 | [Loop](TP_COURSE_LOOP_EVIDENCE.md) |
| WP05 会话 | 对实际 Claude 失败会话执行 /export；保全两份历史原始用户输入，分别留真实来源。 | [会话索引](../collab-log/transcripts/README.md) |
| WP03/WP04 双 Bug | 模型对象形状和 F13 历史定位补完整同轮复验链，独立保留同期史料缺标，定向 9 项通过。 | [Bug](TP_COURSE_BUG_ARCHIVE_AUDIT.md) |
| WP05 五人协作 | 全组 49，证据、Git、验收 49/49，Prompt 48/49，复验退出 0。 | [协作](TP_COURSE_COLLAB_ACCEPTANCE.md) |
| WP01/WP03/WP04 现场 | 固定 27B 单样本、物理头寸实测、原守卫阻断、12 项 Provider 恢复测试。模板修复回归与变异 2/2 完成。 | [现场](TP_COURSE_DEMO_ACCEPTANCE.md) |
| WP02/WP05 第二轮审计 | 对照教师图与 58 个旧项和 6 个新增观察，追溯测试基线、提交和仍缺实据。 | [矩阵](TP_COURSE_REMEDIATION_MATRIX.md) · [最终验收](TP_COURSE_FINAL_ACCEPTANCE.md) |
