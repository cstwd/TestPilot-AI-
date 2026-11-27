# TP-COURSE-FINAL-001 最终课程工程报告

TestPilot AI 是面向 Python 开发、测试和质量人员的单机工作台。项目用真实运行支持缺陷呈现、版本回归和质量评估。课程工程由陈帅廷统一协调，五个工作包各 20%，实际操作以 Git 与会话为准。项目组长人工签收待记录。[课程要求](COURSE_REQUIREMENTS_AUDIT.md) · [五人贡献](COURSE_TEAM_CONTRIBUTIONS.md)

## 需求和实现

开发人员导入同名源码的缺陷版与修复版，测试人员选择 AST 暴露的函数和行段，生成并检查测试，质量人员选择实际执行记录进行报告导出与变异评估。FastAPI 在本机同源提供 Web 与 API。SQLite 用项目、源码版本、用例、运行和缺陷 ID 串联证据。宿主只解析被测代码与生成代码，真实执行交给独立 WASI CPython 与 Pytest。F13 生成六类变异，先确认原版，按固定清单逐个判读，补测还要重新通过原版校验。[规格](SPEC.md) · [架构](ARCHITECTURE.md) · [隔离实现](phase03/SANDBOX.md)

## 本机模型和可复算实验

统一的 Qwen3.8-27B UD-IQ3_XXS Provider 使用 Ollama/Vulkan，权重与清单经过固定摘要校验。生成、智能理解和反馈使用结构化协议。输入和结果保存在本机证据中，拒绝身份、资源、连接或格式异常，模板为独立选择。PHASE-05 的 10 个项目与 3 个种子共形成四组 120 次归档试验，所有组的分母均为 117。

| 评测组 | 杀死／预登记 | 检出率 |
|---|---:|---:|
| A 0.5B | 0/117 | 0.00% |
| B 模板 | 81/117 | 69.23% |
| C 27B 初始 | 104/117 | 88.89% |
| D 27B 反馈后 | 105/117 | 89.74% |

模型源码理解严格得分 56/70。RTX 5080 Laptop Vulkan 连续 10 次推理完整且正确，热请求首 Token 中位数 0.553 秒，热请求平均 19.21 token/s，API 费用为零。C 组比模板高 19.66 个百分点，D 组多检出 1 个变异。本结果适用于固定小项目与算子集。[冻结协议](../eval/phase05/PROTOCOL.md) · [性能资源明细](../reports/phase05/T01_PERFORMANCE.md) · [离线复算](../reports/course-final/offline-replay.txt)

PHASE-06 独立阶段报告记录了 148 项回归通过、源码理解 67/70，以及一轮端到端例证从 4/9 到 7/9，两次各保留 2 项执行错误。在该阶段单独的对照复验中，初测和补测均为 93/117。该轮执行存在资源与质量限制，阶段状态为 `READY_WITH_LIMITATIONS`。[PHASE-06 验收](../reports/phase06/TP_PHASE_06_ACCEPTANCE.md) · [逐接口原文](../reports/phase06/raw/live.json)

## 工程验收

固定快照 `72a53b8` 在独立目录通过 **163 项 Pytest 与 3 项 Node 测试**。该轮含 F06 边界指标、完整缺陷回归、和静态编译。后续交付基线 `ae21701` 纳入 PHASE-06 整体归档及 F13 补测总时限，另跑对应定向回归。[完整回归输出](../reports/course-final/acceptance-72a53b8.txt)

- PHASE-04 历史 146 项整体回归，F13 模块 47 项通过。PHASE-05 的变异定向 8 项通过，文件逐项保留。课程轮在主线使用 Edge、FastAPI 与 WASI 复验 F01–F06、真实缺陷回归、质量 JSON 导出和 F13 完整报告。
- 最新的模型、属性、变异和冻结清单定向测试 39 项通过。Hypothesis 生成 40 个宿主 AST 参数及行号示例，同时检查序列化。工程工具 2 项通过，MCP 实际返回项目和 WASI 运行，Git Hook 实际拒绝错误提交并通过修正提交。
- 最终 PHASE-06 合并后，F13 真实 WASI 和 Edge 端到端定向回归 3 项通过。[合并后 F13](../reports/course-final/phase06-merge-f13.txt)
- 初次整套测试发现 MCP 测试库命名与标准配置不符，157 项通过、1 项失败。测试库按真实入口命名后，MCP 和 Hook 定向复验通过。首轮输出见 `git show 0633984:reports/course-final/verify-full.txt` · [修复复验](../reports/course-final/toolchain.txt)
- 15 份历史任务及阶段摘录、20 条分类协作记录、3 份重点 Bug 档案、工程工具及复核记录已纳入课程索引。可编辑 PPTX 提供 8 页，另有 PDF 预览、9 张真实页面／记录截图和 59 秒备用视频。

主线模型健康复验先跟随独立阶段工作树的守护进程，实际返回 503。稍后在隔离目录启动专用 Ollama 和根入口，使用同一份已校验权重。在当前模型 Provider 上实际收到 HTTP 200、Vulkan 为 true、GPU 分配约 9.70 GiB。结束后用该实例的 STOP 文件关闭守护，应用进程与临时库随测试释放。[初次响应](../reports/course-final/model-main-check.json) · [主线成功响应](../reports/course-final/model-main-live.json)

[测试体系](COURSE_TESTING.md) · [项目证据](COURSE_EVIDENCE_INDEX.md) · [Edge 演示](../reports/course-final/demo.txt) · [合并后定向测试](../reports/course-final/phase06-merge-focused.txt) · [工具验证](../reports/course-final/toolchain.txt) · [展示](../presentation/README.md)

## Git 与交付

| 提交 | 归属及工作 |
|---|---|
| `1acd2ff` | WP05 合并 PHASE-05 冻结评测和全量历史原始工件 |
| `646ef7d` | WP01 合并 PHASE-06 固定模型 Provider，保留 F13 身份比较定位修复 |
| `7fdccc9` | WP01 修复模型重试身份与 GPU 健康状态 |
| `4b1b574`, `13a5d09` | WP05 提交工程工具、入口和 Hook 可执行配置 |
| `b7a8b40` | 并行工作完成 F06 质量工作台，课程映射 WP02/WP04 |
| `be2813f` | WP05 恢复规格、课程工作包、协作记录、Bug 与原始 Prompt |
| `72a53b8` | WP05 归档可编辑 PPTX、截图、视频及复建入口 |
| `ae21701` | WP01 合入 PHASE-06 已完成的阶段验收、原始报告与 F13 补测总时限 |

发布边界为 Windows 11 本机单实例，产品支持单文件 UTF-8 Python 的导入路径。PHASE-05 多文件任务使用独立评测适配层。整组冻结数据中 A 组首跑均未通过原版，按完整分母计 0。主线常规 F03 屏幕展示模板路径，27B 证据来自模型 API 和智能引擎。Claude CLI 已识别项目 MCP 配置，首次客户端信任与成员人工签收仍待确认。[Claude 配置发现](../reports/course-final/claude-mcp-discovery.txt)
