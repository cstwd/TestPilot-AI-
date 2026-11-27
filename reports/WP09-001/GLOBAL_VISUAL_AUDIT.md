# WP09-001 全站视觉审查

开工时的工作区为 `D:\TestPilot AI`，Git HEAD 为 `b7a8b400db1ebacefb273f377baf0d97a1c440c0`。同期课程交付有独立的文档、图稿、Hook 和报告改动。WP09 只包含六页前端、独立新增测试与本工作包证据。

## 页面基线

| 模块 | 页面路由 | 独立视觉实现基线 | 主要证据来源 |
| --- | --- | --- | --- |
| F01 Project Explorer | `/workbench/projects` | `9f048d09985f9493eb117ba0d2e9f0559aff9144` | 项目、文件和不可变导入版本 |
| F02 Visual Intelligence Studio | `/workbench/analysis` | `76bd9e0fa1c2cf9d5c22c4812227e7d77430066b` | 文件详情与 AST 分析数据 |
| F03 AI Test Generation Studio | `/workbench/generation` | `7c796e73ffdc352641cb5a0dffd6d58fa6d75f43` | 套件、静态检查与真实首次执行 |
| F04 Test Execution Control Center | `/workbench/runs` | `9fdfa7e6c5266bb55ddfbdd0fdee1427f5232daa` | 受限 Pytest 的持久化运行记录 |
| F05 Bug Intelligence Center | `/workbench/bugs` | `c49dde2ea089f2379eacd9b4f8aaf2494e2b59eb` | 缺陷、原始运行、源码版本与回归记录 |
| F06 Quality Intelligence Center | `/workbench/reports` | `b7a8b400db1ebacefb273f377baf0d97a1c440c0` | 单次运行报告读取事务 |

路由、项目身份、文件版本和运行接口沿用 [工作台路由](../../backend/workbench.py)、[项目](../../backend/projects.py)、[AST](../../backend/analysis.py)、[生成](../../backend/generation.py)、[运行](../../backend/runs.py)、[缺陷](../../backend/bugs.py) 和 [质量报告](../../backend/quality.py) 的现有契约。

## Design System V1 的继承

| 检查项 | 全站规则 | 页面保留的业务表达 |
| --- | --- | --- |
| 底色、面板、边框、间距 | 石墨 `--page`、`--panel`、`--border`，使用既有间距和圆角变量 | 图谱画布、运行终端和只读 Diff 使用面向内容的局部底色 |
| 字体、层级 | Inter 与系统中文字体回退，代码和身份编号采用 JetBrains Mono 与 Consolas 回退 | 质量指标数字、文件版本和日志的阅读顺序各自保留 |
| 顶栏、侧栏、图标 | 公共品牌、现有本地线条 SVG 图标、桌面模块栏和统一手机菜单 | 宽屏保留项目/文件选择或业务面包屑，手机沿用各页面板顺序 |
| 按钮、搜索、徽标 | 共用紫色主操作、文本链接、键盘焦点、搜索输入和面板标题样式 | 属性筛选、运行终态和缺陷判定仍按真实业务状态呈现 |
| Loading / Empty / Error | 复用公共状态结构及深色提示语义 | F02 分析请求、F04 持久化日志和 F06 无覆盖率保留各自状态口径 |
| Inspector、Modal / Drawer | 同一组层次、实线边框和键盘焦点规则 | F02 图谱 Inspector 与帮助弹窗、F05 回归确认、F06 Evidence Inspector 各自承担原有交互 |
| 表格、源码、终端、Diff、图表 | 选择态与文字层次一致，代码和日志采用共用等宽字体 | F04 用例表、F05 双栏/统一 Diff、F06 分布和分母展示按各自阅读任务组织 |

来源为 [Design System V1](../../docs/WP04-F01-001/DESIGN_SYSTEM_V1_IMPLEMENTATION.md)、[公共样式](../../frontend/static/studio-system.css) 和 [Jinja 组件](../../frontend/templates/studio_components.html)。桌面截图中 F01 在小数据集时留有纵向空白，F02 让图谱占据中央主要区域，F04 和 F06 将高频结果放在页面上方。

## 处理记录

| 现象 | 最小处理 | 复核证据 |
| --- | --- | --- |
| 手机 F02 缺少直接模块菜单，F03–F06 菜单点击外部后仍打开 | 六页复用 `module_menu` 和原生 `details`，支持键盘开关、Escape 恢复焦点与外侧关闭 | [修复前复现](raw/baseline-mobile.txt)及[修复后 Edge 输出](raw/integration-edge.txt) |
| F05 选择候选后全局链接可能仍携带旧文件身份 | 通用导航跟随已验证的候选版本，原运行链接继续带原版本、套件和运行 ID | [业务闭环](END_TO_END_ACCEPTANCE.md) |
| F02 首次进入往返缓存后，下一次离页的清理可能丢失 | 根据 `pagehide` 和 `pageshow` 暂停或释放 Canvas，保持 Cinematic 时间轴和图谱布局 | [性能复核](PERFORMANCE_AUDIT.md) |
| F04 原始终端和 F05 原始运行日志的超长单行需横向追读 | 对日志展示换行，复制时使用持久化原始文本 | [性能复核](PERFORMANCE_AUDIT.md) |
| F06 页面已提供 HTML 阅读与打印，验收还要求下载独立 HTML | 从当前显示的同一报告生成内联样式的 HTML，保留已有 JSON 接口和证据链接 | [业务闭环](END_TO_END_ACCEPTANCE.md) |
