# 会话证据索引

来自 Codex Desktop 本机会话保存记录的用户消息与最终答复摘录。每个文件保留原会话 ID、北京时间、实证链接和 Git 引用。尚未取得最终答复的记录使用已截取的可见进度。全文日志含内部工具数据，课程归档范围为用户 Prompt、可公开的可见答复和模型评测原始交互。

| 原文类型 | 取证入口及边界 |
|---|---|
| AI 需求访谈 | [三问及实际用户答复](requirements-interview.md)，结合 [立项原任务](raw/phase01-06/TP-PHASE-01-user.txt) 确认课程范围。 |
| 阶段原始 Prompt 与关键输出 | [PHASE-01 至 06 的六组原文字节](raw/phase01-06/)。[原会话 ID、事件行号、角色、时间与 SHA-256](raw/phase01-06/message-index.json) 随附。来自 `0633984`，为 Codex 历史原消息提取。 |
| 补回的两份原始 Prompt | [WP03 Demo Lab](raw/WP03-DEMO-LAB-001-original-prompt.txt) · [WP09 工作台](raw/WP09-001-original-prompt.txt)。从 `d429244` 逐字节恢复。 |
| Claude 原生 `/export` | [实际导出的原始文件](../collab-log/transcripts/TP-COURSE-REMEDIATION-001-claude-attempt.txt) · [导出及覆盖范围](../collab-log/transcripts/README.md)。该会话记录了课程验证尝试的 403 失败。 |
| 本机模型原始输出 | [格式失败](../collab-log/bugs/TP-MODEL-SCHEMA.md) · [F05 实际诊断与补丁调用](../reports/TP-F05-AI-REPAIR-001/model.ndjson)。 |

历史 Codex 原消息与原生 Claude `/export` 按各自来源保留。需求、关键开发和历史 Bug 的对应 Claude `/export` 待补或待教师确认替代材料。

| 工作包 | 原始会话摘录及直接证据 |
|---|---|
| WP01 | [立项](TP-PHASE-01.md) · [本机部署](TP-MODEL-002.md) · [统一迁移](TP-PHASE-06.md) |
| WP02 | [需求访谈](requirements-interview.md) · [前端研究](TESTPILOT-FRONTEND-REFERENCE-001.md) · [F01](WP04-F01-001.md) · [F04](WP06-F04-001.md) · [F05](WP07-F05-001.md) · [F06](WP08-F06-001.md) |
| WP03 | [核心引擎](TP-PHASE-02.md) · [智能引擎](TP-PHASE-03.md) · [AST](WP03-AST-VISUAL-001.md) · [交互优化](WP03-AST-VISUAL-REFINE-001.md) · [F03](WP05-F03-001.md) |
| WP04 | [F13](TP-PHASE-04.md) · [固定分母评测](TP-PHASE-05.md) · [真实 27B 推理原文](../reports/phase05/raw/vulkan-01/stability.jsonl) |
| WP05 | [课程整合原始任务书](TP-COURSE-FINAL-001.md) · [课程工具链记录](../reports/course-final/TOOLCHAIN.md) |
