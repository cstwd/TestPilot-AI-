# TestPilot AI 工作台 Design System V1

**WP04-F01-001**。公共层已在项目中心和 AST 工作台使用。其余页面可按需接入。WP04 登记负责人马雪朋，本次实际操作者 Codex，组长陈帅廷协调人工验收。[职责表](../../collab-log/member_contributions.md) · [组件复用地图](COMPONENT_REUSE_MAP.md)

## 提取起点

工作区为 `D:\TestPilot AI`。本包开工 HEAD 是 `765e95acc3cbc88ee7f914495ce988f0ad99a991`，F02 精修提交是 `76bd9e0`。可用 `git show 76bd9e0:frontend/templates/analysis.html` 查看旧版顶栏、SVG 字形与资源树，用 `git show 76bd9e0:frontend/static/analysis.css` 查看原始石墨色阶。旧版 Inspector 在单个模块中计算源码偏移、词法着色并生成文本节点。F01 原来通过普通工作台加载 dashboard.css 和 workbench.css。此次将可以由两页消费的模板、样式与源码显示能力单独落盘。[共享模板](../../frontend/templates/studio_components.html) · [样式入口](../../frontend/static/studio-system.css) · [源码显示入口](../../frontend/static/studio-source.js)

## 颜色、文字与尺寸

| 作用 | V1 取值与消费方式 |
| --- | --- |
| 背景层级 | 页面 `--page` 为 #0c0d15，输入底 `--field` 为 #10121b，面板 `--panel` 为 #141620，按钮与高层表面 `--panel-top` 为 #181a26。用色阶决定区域归属，面板之间以 1 px 分隔。 |
| 文字 | `--ink` #eef0fa 用于标题及主要数据，`--muted` #a4a9bd 用于标签，`--dim` #8990a8 用于辅助信息。标题随视口从 22 到 30 px，基础正文 14 px，按钮 13 px，属性和源码通常 12 px。 |
| 强调与状态 | 品牌紫 `--violet` #b495ff 用于焦点与主操作。文件蓝 `--file` #639cff 也提供请求中的色彩，青色 `--status-ok` #46dcc7 对应成功，`--status-error` #ffa7ad 对应异常。状态另配可读文字。 |
| 选中项 | `--surface-selected` #2b233a、`--border-selected` #42344f 和 `--ink-selected` #eee8ff 同时更新行底、边框及文字。文件树按钮以 `aria-pressed` 或当前文件类记录状态，模块导航使用 `aria-current="page"`。 |
| 字体 | `--sans` 按 Inter、Segoe UI、Microsoft YaHei UI、PingFang SC 与系统无衬线字体回退。`--mono` 按 JetBrains Mono、Consolas、本地中文字体与系统等宽字体回退。页面仅请求本地静态资源；实际所用字形取决于机器安装的字体。 |
| 间距与圆角 | `--space-1` 至 `--space-6` 分别对应 4、8、12、16、20、24 px。控件圆角令牌为 5 / 7 / 12 px；普通面板主要依靠边框，搜索浮层用 `--shadow-float`，对话框使用遮罩。 |

令牌按原值、语义、组件分层。例如 `--graphite-800 → --panel-top → --button-bg`，选中背景通过 `--tree-selected-bg` 引用 `--surface-selected`。颜色或尺寸在应用层有含义时优先采用对应语义。F02 节点类型色仍保持文件、类、函数与方法的四种语义。[令牌与实际选择器](../../frontend/static/studio-system.css#L1)

## 页面接入

1. 在页面自身 CSS 前载入 `/static/studio-system.css`。此文件包含深色页面的字体、基础控件和响应式壳层。现有普通工作台采用原入口；页面选择由 Jinja 分支决定。[工作台分派](../../frontend/templates/workbench.html)
2. 从 `studio_components.html` 引入所需宏。`icons()` 每页渲染一次。顶栏使用 `{% call topbar() %}…{% endcall %}`，在插槽中放置本页的搜索或连接状态。顶栏保留公共控制器使用的 `#project` 和 `#file`。`rail(modules, active)` 使用当前模块表设置目标和高亮。[顶栏与导航](../../frontend/templates/studio_components.html#L42)
3. 资料面板采用 `.pane`、`.explorer` 或 `.inspector` 与 `pane_heading()`。输入检索用 `search()`，按钮可选 `.primary` 或带可访问名称的 `.tool`。空态与加载说明用 `state()`，显示错误时保留后端详情和可操作的恢复入口。[F01 页面](../../frontend/templates/projects.html) · [F02 页面](../../frontend/templates/analysis.html)
4. 代码视图先用 `splitSource(source)` 取得行及原文偏移，再用 `tokenize(lines)` 取得每一行的着色区间。对可见行使用 `colorLine(text, spans)` 创建只读 DOM。行号与正文共用 23 px 行高。复制操作从原始 source 或其偏移切片读取，可保留缩进与行尾。[源码工具](../../frontend/static/studio-source.js) · [F02 Inspector](../../frontend/static/ast-inspector.js)

## 图标、响应式与状态

本系统沿用 F02 自有的 Lucide 风格 SVG 线性符号。图标使用 24 × 24 viewBox、圆角端点、圆角连接与 currentColor，默认在 17 × 17 px 的盒内绘制。装饰 SVG 隐藏于辅助技术，独立图标按钮和链接须有功能名称。宏与符号均随模板渲染，运行时通过本页的 `<use>` 引用。[图标源](../../frontend/templates/studio_components.html#L2)

桌面顶栏高 61 px，模块轨宽 54 px。至 900 px 时模块轨缩至 44 px，至 650 px 时选择器进入顶栏第二行，顶栏高 94 px，各业务页提供自己的窄屏阅读顺序。Focus-visible 的 2 px 紫色轮廓、禁用状态和系统减少动态效果设置属于公共层。工作台负责把实际请求映射为加载、已就绪、空数据或错误状态，并在 `role="status"` 区域提供操作反馈。[壳层断点](../../frontend/static/studio-system.css#L105)

## 复核

在开工工作区实际渲染了 F02 Jinja，检查模块高亮和关键控件 ID 各出现一次。对比 `76bd9e0` 的源码显示函数，7 组输入的行、原文偏移、词法区间和文本节点投影完全一致，输入包含 telemetry.py、空文件、空行 CRLF、带中文标识符的异步定义、跨行三引号字符串、HTML 外观文本与超长数字列表。F01↔F02 的实际浏览器观察与回归命令收录于工作包报告。[F01 浏览器验收](../../reports/WP04-F01-001/F01_BROWSER_ACCEPTANCE.md) · [回归报告](../../reports/WP04-F01-001/F01_REGRESSION_REPORT.md)

Codex 在隔离的开工版本和提取后的真实 Edge 页面，以相同文件、根节点和减少动态设置复测。1440 × 900 的顶栏为 61 px、模块轨为 54 px、画布为 835.61 × 589.45 CSS px。390 × 844 的顶栏为 94 px、画布为 390 × 470.92 CSS px。两种尺寸下，16 节点、15 条包含边的画布 PNG 摘要均与对应基线相同。[对照方法与结果](../../reports/WP04-F01-001/F01_REGRESSION_REPORT.md)
