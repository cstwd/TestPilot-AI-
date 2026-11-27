# 公共组件复用地图

**WP04-F01-001**。F01 和 F02 直接加载同一份 CSS，使用同一组 Jinja 宏和源码显示函数。宏负责语义化结构，控制器负责版本、状态和操作。模块轨遍历仓库现有的 F01–F06 模块表；引擎和变异分析有各自独立的入口。[模块声明](../../frontend/templates/modules.html) · [工作台分派](../../frontend/templates/workbench.html) · [Design System V1](DESIGN_SYSTEM_V1_IMPLEMENTATION.md)

| 公共组件及真实定位 | F01 项目中心 | F02 AST 工作台 | 接入约定 |
| --- | --- | --- | --- |
| [icons / icon](../../frontend/templates/studio_components.html#L1) | 导入、版本、复制、项目与文件 | 图谱、节点查看、相机及播放控制 | 页面一次加载 sprite；传入稳定的 glyph 名称，操作按钮提供可读名称。 |
| [topbar](../../frontend/templates/studio_components.html#L42) | 当前项目、不可变文件版本和连接状态 | 相同两项选择器，附节点搜索、设置与帮助 | 提供插槽供页面扩展。公共选择器保留 `project`、`file` 两个 ID。 |
| [rail](../../frontend/templates/studio_components.html#L54) | projects 为当前项 | analysis 为当前项 | 模块表决定顺序及名称，`data-dest` 供控制器补入当前路由上下文。 |
| [pane_heading](../../frontend/templates/studio_components.html#L65) / .pane | 左 Explorer 和右 Inspector | 左 Explorer、右 Inspector 和相同面板标题语言 | 可用 caller 插入计数或关闭按钮。页面各自决定中央列比例及移动端面板切换。 |
| [search](../../frontend/templates/studio_components.html#L61) | 搜索项目、搜索文件名 | Explorer 搜索项目文件 | 生成带可访问名称的 search input，页面自行处理筛选。图谱搜索结果列表继续由 F02 管理。 |
| [.tree-row / .row-version](../../frontend/static/studio-system.css#L85) | 项目行当前高亮、文件组及历史修订 vN 标明版本 | 可展开符号树、当前文件行和 vN 修订标记 | 行复用选中底色、文本、边框与单行缩略；F01 执行页面导航，F02 执行图节点定位。 |
| [按钮、状态标记和输入](../../frontend/static/studio-system.css) | 新建、导入、复制与进入分析 | 分析请求、重播、图谱设置和过滤 | 原生 disabled、focus-visible 和文字反馈。主操作使用 .primary，图标按钮使用 .tool。 |
| [state](../../frontend/templates/studio_components.html#L69) | 未选中文件、空项目、失败详情与恢复入口 | 画布等待、不可用、语法错误、类型筛空时的内容容器 | 传入稳定 id、标题、具体说明与图标。F02 另在状态栏和控制台持续公布真实阶段。 |
| [.ai-identity / .ai-facts](../../frontend/static/studio-system.css#L126) | 文件身份和真实版本属性 | 当前定义身份和对应的版本、行区间及参数属性 | 文件上下文与节点上下文使用相同层次。需要解释的值如 SHA-256 用等宽文字并允许换行。 |
| [只读源码工具](../../frontend/static/studio-source.js) / [.ai-source-*](../../frontend/static/studio-system.css#L134) | 用不可变版本原文着色、分页及完整复制 | 同一词法器和行号布局，支持用定义范围自动定位与反向选符号 | 函数接收文本，生成 Text 节点和 token span。数据库原文保留为复制来源。 |

### 数据与交互的归属

- **项目和版本**。项目搜索依赖项目清单，版本分组来自该项目的文件记录。一个文件版本记录主键同时用于 `file_id` 和不可变版本身份，`revision` 是修订序号。样式层只消费页面已核验的数据。计时、执行状态、文件大小等属性由各业务页按数据来源独立计算或读取。[F01 控制器](../../frontend/static/projects.js) · [文件 API](../../backend/projects.py)
- **源码与图谱**。三个通用显示函数保留字面文本、真实换行位置和跨行字符串状态。F02 的父子关系适配、源码范围选中、暂停、重播与相机控制分别留在原模块。仅 Inspector 的源码渲染改为导入共享工具。[F02 Inspector](../../frontend/static/ast-inspector.js) · [图适配器](../../frontend/static/ast-model.js) · [时间轴](../../frontend/static/ast-animation.js) · [画布](../../frontend/static/ast-canvas.js)

### 后续页面可采用的入口

| 模块 | 建议先复用 | 留给该页面的决定 |
| --- | --- | --- |
| F03 测试生成 | 顶栏及版本上下文、源码行、Inspector 标题、主按钮、加载/错误状态 | 生成配置和结果如何切换，生成模式和目标函数如何核对 |
| F04 自动化执行 | 顶栏、模块轨、状态文字、等宽字体与条目高亮 | 运行阶段、日志来源、真实结果及刷新策略 |
| F05 缺陷管理 | 搜索、列表选中、Inspector 属性和安全源码片段 | 缺陷筛选、具体证据与 Diff 的数据供应 |
| F06 质量分析 | 页面外壳、面板、状态颜色、排版与空态 | 指标定义、分母、时间范围与图表交互 |

本表中 F01、F02 为当前消费方。F03–F06 列出的是未来接入点，可分别选择最适合各自业务的布局。
