# 逐页视觉设计

16:9，深蓝底色 #0D1824，青色标注流程，紫色标注模型，绿色与红色用于实测成功与失败。中文使用微软雅黑。图形、文字和统计图在 PPTX 内可编辑，截图保留原 PNG；SVG 为可单独打开的素材。

## P01 TestPilot AI

左侧标题和成员，右侧真实样本库截图；选中 unit_scaling 为讲解入口。

素材　01-workbench.png

[来源及核对位置](../05_DEMO_ASSETS/screenshots/01-workbench.png)

## P02 测试工作的难点在交接处

用上下双轨对照人工交接和工作台的证据关联；下方列出三项可观测的验收条件。

素材　02-manual-and-workbench.svg

[来源及核对位置](../03_TEAM_COLLABORATION/raw/transcripts/requirements-interview.md)

## P03 工作台把七项能力接成一条链

上排 F01–F06 六节点，下排 F13 分支和可追踪身份。

素材　03-feature-map.svg

[来源及核对位置](../02_PROJECT_DOCUMENTS/raw/docs/FEATURE_MAP.md)

## P04 执行隔离与证据留存各有入口

同源入口单独高亮，以下分成静态编排、AI 回环、受限执行、存储四层原生对象。

素材　04-system.svg

[来源及核对位置](../02_PROJECT_DOCUMENTS/SYSTEM_ARCHITECTURE.md)

## P05 从 telemetry.py 的图谱跳到源码

左侧展示真实 Edge 图谱，右侧列出被选方法的限定名、源码行号和实际局部调用。

素材　05-ast.png / 05-ast-code.svg

[来源及核对位置](../05_DEMO_ASSETS/screenshots/05-ast-source.png)

## P06 生成模式决定套件的证据来源

顶部可编辑五步流程，左侧历史 AI 成功和当前资源状态，右侧展示原始 AI 生成断言。

素材　06-ai-generation.svg / 06-template.png

[来源及核对位置](../04_TESTING_EVIDENCE/AI_EVALUATION/reports/phase06/raw/live.json)

## P07 Pytest 持久化了可定位的失败

左侧大数值和断言，右侧以 F04 失败页说明界面操作；独立批次在图注区分。

素材　07-pytest.png / 07-execution.svg

[来源及核对位置](../04_TESTING_EVIDENCE/MUTATION_TESTING/reports/phase07/edge-run.json)

## P08 用同一套件验证 unit_scaling 修复

左右对照两版源码和同一套件的通过、失败、跳过数，下方按顺序区分模型建议、浏览器应用和 WASI 实跑。

素材　08-regression.svg / preview.png / regression.png

[来源及核对位置](../04_TESTING_EVIDENCE/F05_AI_REPAIR/reports/TP-F05-AI-REPAIR-001/TP_F05_AI_REPAIR_001_ACCEPTANCE.md)

## P09 5 个变异中有 1 个存活

左侧带状态标记和两种分母，右侧保留真实定位截图；下方独立原理图。

素材　09-mutation.svg / 09-mutant.png

[来源及核对位置](../04_TESTING_EVIDENCE/MUTATION_TESTING/reports/phase07/f13-geometry.json)

## P10 冻结评测可以在 CI 中复算

左侧原生列图并保留 117 分母，右侧 CI 主流程及一次失败修复。

素材　10-ci.svg / 10-offline.svg

[来源及核对位置](../04_TESTING_EVIDENCE/CI/reports/TP-COURSE-REMEDIATION-001/ci-github/45992897616/receipt.json)

## P11 两个真实 Bug 促成了可测的约束

两案各用现象、根因、修复、回归四行对照，避免和 unit_scaling 样本合并。

素材　11-bug-cases.svg

[来源及核对位置](../07_FINAL_REPORT/historical/reports/TP_COURSE_BUG_ARCHIVE_AUDIT.md)

## P12 一个运行 ID 串起从导入到报告

顶部真实身份链，左下报告中心截图，右下显示导出验证步骤。

素材　12-closed-loop.svg / 12-report.png

[来源及核对位置](../04_TESTING_EVIDENCE/MUTATION_TESTING/reports/phase07/edge-run.json)

## P13 六项技术如何让测试结果可以复核

左栏对应六个技术选择与可检查的产物，右栏列出开发工具在项目里执行的工作。

素材　13-toolchain.svg

[来源及核对位置](../07_FINAL_REPORT/historical/reports/TP_COURSE_LOOP_EVIDENCE.md)

## P14 课程评分对应到可核对的材料

左侧七行将满分与代表性证据并列，右侧列五岗、各自日志条数与计划份额。

素材　14-score.svg / 14-team.svg

[来源及核对位置](../01_TEACHER_REQUIREMENTS/TEACHER_REQUIREMENTS.md)

## P15 可追溯的回归是项目的主要成果

顶部归纳结果，底部列出演示入口与答辩待办；独立素材附历史验收统计图。

素材　15-outcomes.svg

[来源及核对位置](../07_FINAL_REPORT/GAP_REGISTER.md)
