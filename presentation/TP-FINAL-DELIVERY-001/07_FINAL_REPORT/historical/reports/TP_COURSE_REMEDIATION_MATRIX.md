# TP-COURSE-REMEDIATION-001 · 第二轮逐项矩阵

原 58 项全部复核，PASS 39，PARTIAL 17，MISSING 1，UNVERIFIED 1。新增 6 项后共 64 项，PASS 44，PARTIAL 17，MISSING 1，UNVERIFIED 2。状态反映证据完整性，分数按教师七类共 100 分另加 5 分。扩展、测试与 Loop 是教师图 4 蓝框可选项，仍按本轮用户要求实际执行。

| 核查项 | 标准 | 上轮 | 本轮 | 观察和剩余范围 | 证据 |
|---|---|---|---|---|---|
| A01 | 四类选题或自拟题目 | UNVERIFIED | PASS | 教师图 1 明确允许具有复杂度或创意、功能完整的自拟题。TestPilot 的多模块 WASI 和 AI 链路满足自拟题证明。 | [来源摘要](TP_COURSE_REMEDIATION_REPORT.md) · E02/E13 |
| A02 | 复杂度、创新性及完整功能 | PASS | PASS | 版本、AST、隔离实跑、缺陷回归、固定分母变异及本机 AI 构成完整工程链 | E02 E13 E16 E17 |
| A03 | 问题、用户、架构与可运行核心 | PASS | PASS | 有开发、测试和质量三类用户，六项业务跨 UI、API、SQLite、WASI 跑通 | E02 E12 E13 |
| A04 | README、完整步骤、异机独立运行 | PARTIAL | PARTIAL | README 安装、单机 Run/Debug 与固定模板已实测。托管 Windows 复现实测覆盖自动化，异机由他人按 README 操作及 27B 交接未验。 | E12 · [现场](TP_COURSE_DEMO_ACCEPTANCE.md) |
| A05 | 教师一周时间线和阶段交接 | UNVERIFIED | PARTIAL | 图 5 的四阶段、各检查点和提交物已映射。Git 和历史三天计划无法证明按一周日历完成，图中四项红框定义工作均有证据。 | [里程碑对照](TP_COURSE_REMEDIATION_REPORT.md) |
| B1.1 | SPEC 及 AI 访谈过程和用户需求 | PASS | PASS | 三问均有用户原答「沿用任务书」，SPEC 引用需求来源及角色 | E02 E04 |
| B1.2 | 功能、非功能及可测试验收条件 | PASS | PASS | 8 组功能含接口、判定和数据关联；5 条非功能含启动、沙箱、模型等 | E02 E12–E17 |
| B1.3 | 需求与实现、测试一致 | PARTIAL | PARTIAL | SPEC 8/8 有实现。FEATURE_MAP 已更新实测和边界，保持原验收条件。普通 F03 页固定模板，来宾原生属性测试仍有跳过。 | [功能映射](../docs/FEATURE_MAP.md) |
| B2.1 | 项目级上下文含结构、规范、约束和质量要求 | PASS | PASS | AGENTS V2 写明单服务、测试、模型和证据审查 | E03 E08 |
| B2.2 | 多个版本及具体历史 | PASS | PASS | 初版、阶段约定和 V2 三次提交可查 | E03 |
| B3.1 | 原始 Prompt、背景、目标范围和输出要求 | PASS | PASS | 阶段、模块、课程整合任务书保留所列信息 | E04 E20 |
| B3.2 | Prompt 前后版本、关键原文、失败和迭代 | PARTIAL | PARTIAL | 新增两份真实历史原件和一次有真实失败及反馈的 Goal。部分历史工作仍无前后两版 Prompt 对照。 | [会话索引](../collab-log/transcripts/README.md) · [Loop](TP_COURSE_LOOP_EVIDENCE.md) |
| C1.1 | 至少两个自定义 Skill，含 verify | PASS | PASS | verify 与 testpilot-workflow 有定义、调用步骤；verify 真跑编译、Pytest、Node | E08 E10 E11 |
| C1.2 | 实际使用记录 | PASS | PASS | Codex 显式读入、使用并归档工具链和诊断结果 | E08 E09 E10 |
| C2.1 | 至少一个 MCP Server，有配置、实现、工具和权限 | PASS | PASS | 1 个项目 stdio Server，2 项工具，只读 SQLite | E09 |
| C2.2 | 实际调用、输入输出与使用理由 | PASS | PASS | 协议发现后调用成功，真实 WASI 计数；使用结构化 Schema 与工具发现服务 Agent | E09 E10 |
| C2.3 | Claude 客户端调用演示 | UNVERIFIED | UNVERIFIED | 历史 Claude CLI 配置发现有记录，本轮 CLI OAuth 调用实际 403。已通过的 MCP 仍由真实独立 stdio 客户端支持。 | E09 · [Claude 回执](TP-COURSE-REMEDIATION-001/loop-response-1.json) |
| C3.1 | 确定性 Hook、触发、命令、阻断和实跑 | PASS | PASS | Git pre-commit 检查暂存差异，实际拒绝和接受，Git 文件模式 100755 | E09 E10 |
| C3.2 | 当前克隆 Hook 已启用 | PARTIAL | PARTIAL | 本轮各提交均用显式 core.hooksPath=hooks 执行。曾拒绝工作流空行尾随空格，清理后提交成功。默认克隆未强设启用。 | E09/E21 · [CI 验收](TP_COURSE_CI_ACCEPTANCE.md) |
| C4.1 | 自定义独立角色与权限 | PASS | PASS | testpilot-reviewer 定义只读职责、有限命令和报告要求 | E08 E23 |
| C4.2 | 委派、输入、运行、输出及实际参与 | PASS | PASS | 独立 Reviewer 实际复现三处溯源/指标缺口，修复后执行二次复核，原始身份与差分证据可查。 | [复核](TP-COURSE-REMEDIATION-001/ci-independent-review.json) |
| C5.1 | 至少一次 /goal、/loop 或 claude -p | MISSING | PASS | 使用 Codex 原生 Goal 创建、执行和完成，Claude -p 403 单列失败。教师图 4 标注该扩展为可选，本轮已实做。 | [Loop](TP_COURSE_LOOP_EVIDENCE.md) |
| C5.2 | 目标、反馈、迭代和终态 | PARTIAL | PASS | 优化模式失败反馈促成临时数据漂移复验。原始输入恢复后重放通过，前后 SHA 一致、有明确终态。 | [Loop](TP_COURSE_LOOP_EVIDENCE.md) |
| D1.1 | Pytest 和 Node 核心自动化、通过失败跳过数及原报告 | PASS | PASS | 本机隔离 168 Pytest、3 Node 全过，含旧核心业务、专门测试和错误路径；独立 Demo Lab 评分另在 CI 跑。 | [本机全量](TP-COURSE-REMEDIATION-001/local-full.txt) · [CI](TP_COURSE_CI_ACCEPTANCE.md) |
| D1.2 | 最终候选可核对的全量终态 | PARTIAL | PASS | 当前产品与既有规则 SHA 对比一致。617fe45 隔离全量 168/3 通过，托管课程回归各次结果留档。 | [CI 验收](TP_COURSE_CI_ACCEPTANCE.md) |
| D2 | 属性测试含生成、性质和实跑 | PASS | PASS | 宿主 Hypothesis 40 示例断言 AST 类型、行号、参数与序列化；来宾有跳过 | E14 E11 |
| D3 | 真实跨模块 E2E 与结果 | PASS | PASS | Edge、FastAPI、SQLite、WASI 同项目两版本及运行记录相连 | E13 E17 |
| D4 | 独立参考、实测差异及差异识别 | PASS | PASS | 冻结合同、独立修复版和三方结果验证；变异以同节点比较 | E15 E17 E24 |
| D5.1 | 固定输入、参考、规则、输出、可重复执行和指标 | PASS | PASS | 可重复入口复算四组 120 轮，每组 117 个位置，检出 0/81/104/105，验证冻结清单、汇总和模型身份文件。 | [评测回执](TP-COURSE-REMEDIATION-001/offline-evaluation-hardened.json) |
| D5.2 | 新增 AI 盲测真实运行及指标 | PARTIAL | PARTIAL | 真实 Demo Lab 单样本冷加载仍触发守卫，无 AI F04，有模板回归和变异。历史冻结评测真实可用，但此批 AI 指标仍不可算。 | [现场](TP_COURSE_DEMO_ACCEPTANCE.md) |
| D6.1 | CI 工作流自动执行测试、专门测试与 AI 离线评测 | MISSING | PASS | 工作流已在项目私有 GitHub 的 Windows runner 自动触发，自动测试与固定 AI 离线复算均实际执行。 | [工作流](../.github/workflows/course-verification.yml) · [CI 验收](TP_COURSE_CI_ACCEPTANCE.md) |
| D6.2 | CI 环境、成功与失败记录 | MISSING | PASS | 归档 2 次托管全量失败、1 次通过及真实子命令负向回执。GitHub 和本机分别记账。 | [CI 验收](TP_COURSE_CI_ACCEPTANCE.md) |
| E01 | 至少两份有实际证据的 Bug 档案 | PASS | PASS | 三份独立案包含复现、根因、修复及回归的交叉证据 | E18 |
| E02 | 至少一个真实 AI 引入的 Bug | PASS | PASS | 真实模型格式输出和 Codex 变异定位实现分别可归因；模板断言个案单列 | E15 E16 E18 |
| E03 | 现象→复现→假设→证据→根因→修复→回归→沉淀齐全 | PARTIAL | PASS | 两案这次各有先记录的初步假设、真实历史重现及修复回归，均完整呈现八环节。历史同期假设仍明确标缺。 | [双案复验](TP_COURSE_BUG_ARCHIVE_AUDIT.md) |
| F01 | 每人至少一条、全组至少八条 | PARTIAL | PARTIAL | 五份日志数量 9/10/11/9/10，总 49，达到材料数量。每人真实记录身份或人工核证仍待提供。 | [协作验收](TP_COURSE_COLLAB_ACCEPTANCE.md) |
| F02 | 每条任务、产物、工具模型、核验与反思 | PARTIAL | PARTIAL | 49/49 交付、Git、测试证据，48/49 原始 Prompt。部分关键工程回复仍只是原始可见摘录。 | [协作验收](TP_COURSE_COLLAB_ACCEPTANCE.md) |
| F03 | 保留原 Prompt、关键输出及失败尝试 | PARTIAL | PASS | 有需求/开发原始 Prompt、冻结 AI 原请求与回复、原始失败和 Git 关联。恢复了 WP09 和 Demo Lab 两份原文。 | [会话索引](../collab-log/transcripts/README.md) · E15/E18 |
| F04 | 通过 /export 导出关键会话到 transcripts/ | MISSING | PARTIAL | 实际 `/export` 生成 1110 字节的本轮 Claude 失败会话，并校验 SHA-256。历史关键开发、需求和修复没有相应原生导出，尚无等价认可。 | [会话索引](../collab-log/transcripts/README.md) |
| F05 | 日志与 Git 一致，个人贡献可核验 | PARTIAL | PARTIAL | 校验 49/49 Git 引用，仍只有 Codex 操作的实际证据与五岗归属，五位成员独立操作或核证待补。 | [协作验收](TP_COURSE_COLLAB_ACCEPTANCE.md) |
| F06 | 协作包含两 Bug 和至少一 AI Bug | PARTIAL | PASS | 两份真实档案新增完整复验记录，有真实 Qwen 引入的模型格式问题。 | [双案复验](TP_COURSE_BUG_ARCHIVE_AUDIT.md) |
| G01 | F01 导入和不可变版本可用 | PASS | PASS | 项目、源文件、摘要和较旧版本经真实浏览器验证 | E12 E13 E25 |
| G02 | F02 分析、位置及智能分析 | PASS | PASS | 静态分析与图谱实跑，智能理解有历史成功回执 | E13 E16 E25 |
| G03 | F03 真 AI 生成与前后端连通 | PARTIAL | PARTIAL | 模板 UI 实际连通，AI 套件 API 有历史 200，当前 27B 冷加载 503/422，真实现场 AI 有阻塞。 | [现场](TP_COURSE_DEMO_ACCEPTANCE.md) |
| G04 | F04 实际 Pytest 及错误边界 | PASS | PASS | WASI 实跑、失败节点和持久日志，忙、超时、截断另有测试 | E13 E14 E25 |
| G05 | F05 缺陷、差异、原节点回归 | PASS | PASS | 同一套件在 v2 形成新运行，原失败节点通过并解决缺陷 | E13 E25 |
| G06 | F06 真实运行数据、页面与导出一致 | PASS | PASS | 5/5 通过、5/7 行覆盖可在 JSON/HTML 和页面对照 | E13 E25 |
| G07 | F13 确实运行变异、评分和导出 | PASS | PASS | 本轮短场景真实 WASI 两个变异杀死 2/2；历史模型补测 4/9→7/9 仍可作为原回执。 | [现场](TP_COURSE_DEMO_ACCEPTANCE.md) · E17 |
| G08 | 本地模型能调用并可独立部署和现场演示 | PARTIAL | PARTIAL | 真实守卫在物理内存 0.685 GiB 时停止独立模型。退出后资源恢复，12 个 Provider 替身测试通过。当前成功加载待核。 | [现场](TP_COURSE_DEMO_ACCEPTANCE.md) |
| G09 | 区分实际功能、模板及模拟数据 | PASS | PASS | 核心 API 真实联通，Dashboard 固定自检和错误注入有标记，常规生成入口的 AI 标题与模板模式需讲清 | E12 E13 E25 |
| H01 | 汇报选题、需求功能、验收和架构 | PARTIAL | PARTIAL | PPT 第 1–4 页覆盖标题、业务架构和一个验收；用户、访谈和判据未成节 | E02 E22 |
| H02 | 汇报 Skills、MCP、Hook、Subagent、Loop | PARTIAL | PARTIAL | 工具可引用，PPT 无逐项展示，指定 Loop 案缺回执 | E08–E10 E22 E23 |
| H03 | 汇报自动化、AI 离线评测与 Mutation Testing | PASS | PASS | 第 5–8 页有阶段对照、模型分数、变异和回归概览 | E11 E15 E17 E22 |
| H04 | 汇报两 Bug、五人协作、总结反思 | PARTIAL | PARTIAL | PPT 有业务样本和五人分配，两工程 Bug、贡献凭据和反思未成节 | E18 E19 E22 |
| H05 | 现场流程、备份及每人可讲真实内容 | PARTIAL | PARTIAL | 实际模板缺陷回归及 F13 可以现场，五人讲解主题可追溯。现场 27B 和全员联排未完成。 | [现场](TP_COURSE_DEMO_ACCEPTANCE.md) · [协作](TP_COURSE_COLLAB_ACCEPTANCE.md) |
| I01 | Skills 独立打包供他人复用 | PARTIAL | PARTIAL | 仓库定义可复用；未找到发布包与外部安装证明 | E06 E08 |
| I02 | 交叉红队交换代码并植入 3 Bug | MISSING | MISSING | 图 5 明确交叉红队为选做加分，需两组交换、三处植入及漏检记录。暂无真实跨组回执。 | 教师图 5 · E06 |
| I03 | 自建 MCP Server | PASS | PASS | 自建 stdio Server、协议成功交易及只读证据齐 | E09 E10 |
| R01 | 按教师图逐项确定课程分值、项目选题及可选项 | — | PASS | 七项共 100 分，加分 +5；扩展/测试/Loop 蓝框标为可选。自拟题满足范围。 | [来源](TP_COURSE_REMEDIATION_REPORT.md) |
| R02 | 定义阶段红框四项 | — | PASS | 选题与五岗、AI 访谈/SPEC、AGENTS 初版演化、技术选型及单服务均可核对。 | E02/E03/E04/E12 |
| R03 | 仓库、日志、幻灯片三类最终交付材料 | — | PASS | 私有仓库有隔离整改分支，工作包日志可读，正式已有 PPTX 继续作为交付材料。教师收件另由课程方处理。 | [最终验收](TP_COURSE_FINAL_ACCEPTANCE.md) · E19/E22 |
| R04 | 教师按个人答辩讲解核定贡献系数 0.8–1.2 | — | UNVERIFIED | 五岗各 20% 是课程分工，答辩实际系数尚未发生。 | 教师图 3 · [协作验收](TP_COURSE_COLLAB_ACCEPTANCE.md) |
| R05 | 冻结数据与正式业务源码的完整性 | — | PASS | 原始 Phase 05 清单、源码和报告与历史 SHA 无差异。产品和原测试未纳入并行 Phase 07，冻结身份和指标变更拒绝已实测。 | [CI 验收](TP_COURSE_CI_ACCEPTANCE.md) |
| R06 | 资源守卫和模板备份的受控小规模实测 | — | PASS | 本机真实触发既有守卫、专用进程退出，执行了同版本模板修复回归和短 F13。真实模型通过另见 G08。 | [现场](TP_COURSE_DEMO_ACCEPTANCE.md) |

E 编号沿用 [第一轮证据索引](<D:/TestPilot AI_AUDIT/TP-COURSE-AUDIT-001/07_EVIDENCE_INDEX.md>)。仓库的历史入口集中在 [项目证据索引](../docs/COURSE_EVIDENCE_INDEX.md)。最新工程、成员和模型事项使用表中所列原始回执。
