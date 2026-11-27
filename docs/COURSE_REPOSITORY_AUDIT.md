# 课程仓库最终审计

2026-11-27 · TP-COURSE-REPOSITORY-001 · WP05。负责人王选中，实际操作者 Codex。独立技术复核由 Codex 按 `testpilot-reviewer` 角色执行，个人与阶段签收待本人或组长办理。

[教师要求与证据](COURSE_REQUIREMENTS_MAPPING.md) · [文件筛选矩阵](COURSE_REPOSITORY_FILE_MATRIX.md) · [Git 历史和外部归档](GIT_CLEANUP_REPORT.md)

## 审计范围

开工位于 `D:\TestPilot AI` 的 `codex/tp-course-remediation-001`，HEAD 为 `0633984`。原有 2,653 个跟踪路径。核查工作树、远程引用、版本谱系、忽略规则、源码及冻结评测、协作和 Bug、会话原文、工程扩展、历史 CI 和正式成品。五张教师原图逐页核对其必做、可选和评分标注。

课程整理涉及 F01–F13 的文档和验收证据，归属 WP05。CI 恢复历史已通过的 WASI 预热。产品实现、API Schema、依赖、业务测试源码及冻结评测输入沿用 `0633984` 候选的字节。用户在整理期间修改了 F05 分析提示和对应测试，由其自己的工作继续处理，在独立快照上隔离。

## 验收记录

| 核查项 | 方法与实际结果 |
|---|---|
| 教师原图、会话、汇报 | 对五张教师原图和六组阶段消息逐一比对 SHA-256。核对两份恢复 Prompt 与 `d429244` 的 Git blob 及唯一原生 `/export` 的 1,110 字节和摘要。PPTX 容器及 XML 通过，15 页与 15 个 notes parts，PDF 15 页。备用视频 H.264，59 秒。正式成品与旧交付字节一致。 |
| README 安装与命令 | Windows 11、Python 3.13.11、Node 24.13.0。核对 PyCharm 共享配置及产品帮助、模型部署命令帮助、本机依赖与实际 UI 名称。新机冷启动由独立人员签收。 |
| 本地全量验收 | 使用项目解释器运行 `python hooks/verify.py --scope full --report reports/course-final/verify-full.txt`。独立快照报告待填。 |
| GitHub Actions | YAML 结构与 WASI 门控解析通过，配置与 `000a19c` 逐字节一致。[真实成功](../reports/TP-COURSE-REMEDIATION-001/ci-github/45992897616/receipt.json)为历史 SHA，覆盖 Pytest、Node、Demo Lab 与冻结离线评测。[真实失败](../reports/TP-COURSE-REMEDIATION-001/ci-github/45990819569/receipt.json)保留排查价值。本轮以本机验收为准。 |
| 冻结评测与变异 | `python -m eval.phase05.verify_frozen` 通过。四组固定分母 117，杀死数依次 0、81、104、105。源、原始记录及冻结文件与基线无差异。该命令复算存档数据。 |
| Skills、MCP、Hook、Reviewer | 读入两个 Skill，按 `verify` 执行并核查输出；按 `testpilot-workflow` 记录基线、问题、修正、回归和证据。[定义、权限及历史实测](../reports/course-final/TOOLCHAIN.md) · [原始工具链输出](../reports/course-final/toolchain.txt)。 |
| 协作日志 | `python hooks/verify_member_logs.py` 通过。WP01–05 共 49 条，分别 9/10/11/9/10。49 条均有工程、Git 与测试证据。恢复后原始 Prompt 为 48/49，WP05 首次发布独立指令仍未找到。 |
| Bug 两案 | [两案八步复验](../reports/TP_COURSE_BUG_ARCHIVE_AUDIT.md)与 [原回执](../reports/TP-COURSE-REMEDIATION-001/bug-replay.json)交叉核对。F13 的 `is not` 落点缺陷由 AI 生成实现引入，修补与精确位置回归可查。模型 Schema 偏差有原请求、原输出、拒绝和修复。两案初步假设取自事后复验前，原开发同期假设待补。 |
| 原文与原生导出 | [原文索引](../transcripts/README.md)可定位来源会话、事件角色、时间或恢复提交。原生 Claude `/export` 的真实 403 结果保留。需求、开发和典型 Bug 的原生导出仍缺。 |
| 敏感信息与历史 | 交付文本扫描私钥头、常见令牌、带密码 URL、强特征明文凭据和身份证号。历史以已知 Git 秘密文件名和高置信特征复查，命中与检查边界见本报告最终记录。 |
| 独立复核 | 检查正式课件原字节、原文校验、README 操作、旧包删减和工作流来源。发现演示链接失效、重复截图、F13 少一步和 AI UI 描述错误，均已修订。 |

## 待核证事项

- 历史 `/export` 的覆盖范围须由组长补实物或取得教师对原始 Codex 记录的认可。
- 五份个人日志有原始会话、Git 与结果索引，本人实际操作、反思及答辩各段仍须分别核对。
- 答辩机独立安装启动及现场 27B 实跑待验。历史成功和失败均可查。
- 图 5 的实际一周历程、首天空测 CI 及跨组红队记录待核。Skills 外部复用为可选加分。
- 组长正式递交与教师评分待课堂流程完成。

正式状态待本机独立验收和必做证据确认。Git 标签与远程发布需按最终结果办理。
