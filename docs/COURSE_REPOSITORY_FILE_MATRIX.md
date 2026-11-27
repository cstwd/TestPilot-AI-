# 课程仓库材料筛选矩阵

TP-COURSE-REPOSITORY-001 · WP05。按从 Git 工作树提供的价值归类。下表覆盖已跟踪目录、明确撤下的项和本机环境。

| 类别 | 实际路径或范围 | 处理与理由 |
|---|---|---|
| A 必须 | [README.md](../README.md)、[AGENTS.md](../AGENTS.md)、[SPEC](SPEC.md)、[功能映射](FEATURE_MAP.md)、[需求访谈](../transcripts/requirements-interview.md) | 教师入口、可测试规格、AI 访谈和规范演化。AGENTS 为唯一根级开发规范。 |
| A 必须 | `main.py`、`requirements.txt`、`pytest.ini`、`.run/`、`backend/`、`frontend/` | Windows 单服务、固定依赖与原有入口。一并保留静态资源、来宾执行和数据契约。 |
| A 必须 | `tests/`、`eval/`、`demo/TestPilot-Demo-Lab/`、`reports/phase04/`、`reports/phase05/` | 测试、冻结清单、合成源码和评分语料。原始模型与 WASI 结果关系到冻结复算及审计，即使位于 raw/ 仍保留。 |
| A 必须 | `.claude/`、`.mcp.json`、`mcp-server/`、`hooks/`、`.github/`、`.gitignore`、`.gitattributes` | 两个 Skill、自定义 Reviewer、一个真实 Server、确定性 Hook、CI 流程和字节完整性规则。 |
| A 必须 | [协作总日志](../collab-log/LOG.md)、`collab-log/members/`、`collab-log/bugs/`、`collab-log/transcripts/`、`transcripts/` | 五份个人日志、工件关联、两案及失败档案、Prompt 与真实原生导出。六组原始任务与回复迁入 `transcripts/raw/phase01-06/`，带原有 SHA-256 索引。 |
| A 必须 | [教师要求映射](COURSE_REQUIREMENTS_MAPPING.md)、`docs/course/originals/`、`presentation/` 正式 PPTX、PDF、讲稿、演示手册与备用视频 | 按教师原图核对交付与评分。沿用发布字节，教师可直接打开。 |
| B 建议 | `docs/` 的架构、工作包、部署与阶段报告；根部 F01–F12 和 PHASE-01–04 验收文档 | 架构、可复验工作包、失败记录及来源持续有效。它们被日志和其他文档直接引用，保持现有路径。 |
| B 建议 | `reports/course-final/`、`reports/TP-COURSE-REMEDIATION-001/`、`reports/TP-F05-AI-REPAIR-001/`、`reports/phase02` 至 `phase07`、`reports/WP*` 及根级阶段回执 | 有来源的阶段与工作包关键证据。其中保留一次托管失败、一次托管成功及其代表性工件、本机模型失败与恢复。单纯生成的本机 CI 缓存按 D。 |
| B 建议 | `docs/course/SCORING_MATRIX.xlsx`、`presentation/PPT_OUTLINE.md`、`presentation/TECHNICAL_QA.md`、`presentation/POWERPOINT_QA.json`、`reports/phase07/05-f13-surviving-mutant.png`、`collab-log/member-confirmation/` | 原评分工作簿、逐页证据、历史 PPT 查验、课上存活变异截图、待本人核对单。 |
| B 建议 | `.agents/skills/.gitkeep`、`agents/.gitkeep` 及其他轻量目录标记 | 历史路径和归档结构。实际角色与技能均由 `.claude/` 提供。 |
| C 仓库外 | `presentation/TP-FINAL-DELIVERY-001.zip`、`presentation/TP-FINAL-DELIVERY-001_完整汇报包.zip`、旧交付树及内部 `TestPilot-AI_cf448f3.zip` | 多重压缩包、整库快照、重复团队日志、原型截图、导出构建源。课程材料在相应正式路径查阅，需要重建旧版时从归档或 Git 历史恢复。 |
| C 仓库外 | 旧 8 页 `presentation/TestPilot_AI_课程汇报.*`、`presentation/screenshots/`、旧制作脚本 | 旧产品演示已由正式 15 页汇报和当前工作台实录接替。备用 MP4 保留一个正式入口。 |
| C 仓库外 | 初始未跟踪的 `reports/model/`、`reports/TP-COURSE-REMEDIATION-001/member-verification.txt` 与旧 `reports/course-final/verify-full.txt` | 既有本机实验细项与历史运行留档。一级目录下的本机原件仍保留并按 D 排除。当前协作核验与全量验证以最终审计中的回执为准。 |
| C 仓库外 | Codex 全会话、重复工作副本与原始过程包 | 课程范围保留可定位的重要原文。历史项目原会话留在原保存位置，仅归档经筛选的文件。 |
| D 忽略 | `.venv/`、`.idea/`、`.runtime/`、`data/`、测试缓存、`reports/ci/`、`*.sqlite*`、`*.db*`、密钥与权重模式 | 虚拟环境、机器配置、临时数据库、运行时权重及凭据均从工作树排除。 |
| D 忽略 | `.~lock.*#`、`~$*.pptx`、历史压缩包和本机报告路径 | 编辑器会话锁和意外回拷的副本应保持在版本控制之外。 |

另见[归档位置、校验及恢复](GIT_CLEANUP_REPORT.md)。原始模型调用记录只保留项目的冻结合成样例。
