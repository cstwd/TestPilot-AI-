# WP10-HOME-001 视觉组件复用地图

Command Center 通过 [`studio-system.css`](../../frontend/static/studio-system.css) 接入 [Design System V1](../../docs/WP04-F01-001/DESIGN_SYSTEM_V1_IMPLEMENTATION.md)。[`home.css`](../../frontend/static/home.css) 处理首页网格、链接卡片、状态行和 CSS 图形。它在根页模板中加载。

| 视觉部分 | 既有基础 | 首页布局或用法 |
| --- | --- | --- |
| 背景、面板、分隔线 | `--page`、`--panel`、`--field`、`--border`、`--soft` | 外部工具、活动和系统区域共用石墨色阶，边界通过 1px 线条区分 |
| 品牌、导航、图标 | Jinja `topbar`、`icons`、`icon`、`.tool`、`.row-version` | 工作台品牌、模式标签、系统设置和帮助入口 |
| 文字、代码、时间 | `--sans`、`--mono`、`--ink`、`--muted` | 沿用 Inter / Windows 系统字体和 JetBrains Mono / Consolas 回退，终端使用等宽字体和可读换行 |
| Hero 与操作 | `.primary`、`--violet`、`--file`、`--function`、已有图标 | 紫色创建，普通按钮导入，文字入口恢复工作区。结构图由 CSS 节点和边组成 |
| 健康和自检 | `pane_heading`、`.status-pill`、公共按钮和语义状态 Token | 健康状态、连接检查时间、子进程状态和可折叠原始输出 |
| 模块与工具卡 | `--radius-md`、`--space-*`、选中表面和焦点规则 | 整张卡片为语义链接，键盘焦点与 hover 同步突出边界，模块代码辨识 F01–F06 |
| 活动与空态 | 使用公共面板层级、`select`、`--status-error` 和焦点 | 独立项目筛选、真实可追溯链接，空和错误在对应行呈现 |
| 对话框 | 公共 `dialog`、`.dialog-heading` 和 `.tool` | 原生关闭与 Escape，项目表单错误由 `role=alert` 读出 |

桌面内容最大宽度为 1360px，系统与自检并列。窄桌面在保有活动侧栏时将模块改为双列。平板把侧栏移到模块之后，390px 依照阅读与操作顺序排列为单列。静态结构图在手机省略，品牌、操作、结果和模块入口全部保留。 [Edge 布局证据](HOME_BROWSER_ACCEPTANCE.md)
