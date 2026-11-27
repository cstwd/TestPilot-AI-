# 课程仓库最终审计

2026-11-27 · TP-COURSE-REPOSITORY-001 · WP05。负责人王选中，实际操作者 Codex。独立技术复核由 Codex 按 `testpilot-reviewer` 角色执行，个人与阶段签收待本人或组长办理。

[教师要求与证据](COURSE_REQUIREMENTS_MAPPING.md) · [文件筛选矩阵](COURSE_REPOSITORY_FILE_MATRIX.md) · [Git 历史和外部归档](GIT_CLEANUP_REPORT.md)

## 审计范围

开工位于 `D:\TestPilot AI` 的 `codex/tp-course-remediation-001`，HEAD 为 `0633984`。原有 2,653 个跟踪路径。核查工作树、远程引用、版本谱系、忽略规则、源码及冻结评测、协作和 Bug、会话原文、工程扩展、历史 CI 和正式成品。五张教师原图逐页核对其必做、可选和评分标注。

课程整理涉及 F01–F13 的文档和验收证据，归属 WP05。CI 恢复历史已通过的 WASI 预热。用 `git diff 0633984 0613012 -- backend frontend main.py requirements.txt tests eval reports/phase05 demo` 核对产品实现、API Schema、依赖、业务测试和冻结评测输入。用户在整理期间继续修改产品代码和测试，运行以 `0613012` 的独立 ZIP 快照为准。

## 验收记录

| 核查项 | 方法与实际结果 |
|---|---|
| 教师原图、会话、汇报 | 对五张教师原图和六组阶段消息逐一比对 SHA-256。核对两份恢复 Prompt 与 `d429244` 的 Git blob 及唯一原生 `/export` 的 1,110 字节和摘要。PPTX 容器及 XML 通过，共 15 页和 15 份页内讲稿。PDF 15 页已全部渲染审阅。备用视频 H.264，59 秒。正式成品与旧交付字节一致。 |
| README 安装与命令 | Windows 11、Python 3.13.11、Node 24.13.0。用已安装的 Python 3.13 创建全新 venv，从 PyPI 安装 `requirements.txt`，`pip check` 通过。在固定快照运行 `python -m pytest -q -s tests/test_startup.py tests/test_project_startup.py`，5 项通过，覆盖 Edge、健康探针、端口冲突、退出重启与数据库错误。核对共享运行配置、CLI 帮助及实际 UI 名称。答辩机由独立人员复验。 |
| 本地全量验收 | 在 `0613012` 的独立快照运行 `python hooks/verify.py --scope full --report reports/course-final/verify-full.txt`，静态编译、184 项 Pytest、3 项 Node 全部通过，退出 0。覆盖真实 Edge 158、WASI、F01–F06、F13 取消与续跑、MCP、Hook 和回归。独立 Demo Lab 评分测试 8 项通过。[全量报告](../reports/course-final/verify-full.txt) |
| GitHub Actions | YAML 结构与 WASI 门控解析通过，配置与 `000a19c` 逐字节一致。缓存预热脚本本机退出 0，固定来宾输出 `4`。[真实成功](../reports/TP-COURSE-REMEDIATION-001/ci-github/45992897616/receipt.json)归属历史 SHA，含 168 项 Pytest、3 项 Node、8 项 Demo Lab 评分测试及冻结离线评测。[真实失败](../reports/TP-COURSE-REMEDIATION-001/ci-github/45990819569/receipt.json)保留排查价值。本轮候选依本机验收。 |
| 冻结评测与变异 | `python -m eval.phase05.verify_frozen` 通过。四组固定分母 117，杀死数依次 0、81、104、105。源、原始记录及冻结文件与基线无差异。使用 `python -O -m eval.phase05.verify_frozen` 得到预期退出码 1，明确拒绝跳过断言的复算。 |
| Skills、MCP、Hook、Reviewer | 读入两个 Skill，按 `verify` 执行并核查输出，按 `testpilot-workflow` 记录基线、问题、修正、回归和证据。本轮通过 MCP stdio 握手、工具发现、真实 WASI 记录读取、错误参数拒绝及数据库字节不变检查。Hook 实际拒绝暂存尾随空格，修正后允许提交。[定义、权限及历史实测](../reports/course-final/TOOLCHAIN.md) · [本轮原始输出](../reports/course-final/verify-full.txt) |
| 协作日志 | `python hooks/verify_member_logs.py` 通过。WP01–05 共 49 条，分别 9/10/11/9/10。49 条均有工程、Git 与测试证据。恢复后原始 Prompt 为 48/49，WP05 首次发布独立指令仍未找到。 |
| Bug 两案 | [两案八步复验](../reports/TP_COURSE_BUG_ARCHIVE_AUDIT.md)与 [原回执](../reports/TP-COURSE-REMEDIATION-001/bug-replay.json)交叉核对。F13 的 `is not` 落点缺陷由 AI 生成实现引入，修补与精确位置回归可查。模型 Schema 偏差有原请求、原输出、拒绝和修复。两案初步假设取自事后复验前，原开发同期假设待补。 |
| 原文与原生导出 | [原文索引](../transcripts/README.md)可定位来源会话、事件角色、时间或恢复提交。原生 Claude `/export` 的真实 403 结果保留。需求、开发和典型 Bug 的原生导出仍缺。 |
| Git 与链接 | `git fsck --no-dangling` 通过，两个指定历史节点均可从原始 HEAD 到达。197 份 Markdown 文件的相对文件路径检查曾发现一处阶段报告引用已移除的模块，现已指向其历史 Git 版本。正式源及冻结清单的 Git 差异为空。 |
| 敏感信息与历史 | 候选 2,195 个不同文本 blob 及 99 个 Office XML 部件以私钥头、常见令牌、带密码 URL、强特征明文凭据及身份证号扫描，未命中。历史另扫 1,227 个不同文本 blob，4 个命中均为两版 F09 测试中的夹具。三份旧 ZIP 通过 CRC，已扫描其中 2,286 个去重文本条目，未命中私钥或令牌特征。历史 Office 锁存在本机元数据，已退出当前树并忽略。图像以人工审阅为主。 |
| 独立复核 | 检查正式课件原字节、原文校验、README 操作、旧包删减和工作流来源。复核者独立执行 Node，3 项通过，独立执行 `pip check` 通过。发现演示链接失效、重复截图、F13 少一步、AI UI 描述错误和 MCP 选择理由不足，均已修订。 |

受限终端的首轮尝试发生本机健康探针超时。随后直接在共享工作树启动的试跑因用户并行编辑而中止。两次过程输出留在本机运行目录。最终报告来自完整执行的独立快照，提交版仅脱敏 Windows 用户和临时目录账户标识，原报告留在快照目录。

## 待核证事项

- 历史 `/export` 的覆盖范围须由组长补实物或取得教师对原始 Codex 记录的认可。
- 五份个人日志有原始会话、Git 与结果索引，本人实际操作、反思及答辩各段仍须分别核对。
- 答辩机独立安装启动及现场 27B 实跑待验。历史成功和失败均可查。
- 图 5 的实际一周历程、首天空测 CI 及跨组红队记录待核。Skills 外部复用为可选加分。
- 组长正式递交与教师评分待课堂流程完成。

本机工程验收通过。当前正式状态为 `PENDING_REQUIRED_EVIDENCE`，等待关键 `/export` 覆盖及成员本人核证。课程整理与验收记录在本地课程分支，正式标签和远程递交待必做证据确认后办理。
