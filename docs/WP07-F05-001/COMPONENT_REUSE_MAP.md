# F05 组件复用地图

WP07-F05-001。F05 消费 F01–F04 的 Design System V1，沿用本地 Jinja、CSS 和原生 JavaScript。[V1 设计系统](../WP04-F01-001/DESIGN_SYSTEM_V1_IMPLEMENTATION.md) · [F04 复用地图](../WP06-F04-001/COMPONENT_REUSE_MAP.md)

| 公共组件 | F05 消费方式 |
| --- | --- |
| `topbar()`、`rail()`、`icons()`、`context_selectors()` | 共用品牌、模块轨、Lucide 风格图标和项目控件。项目选择器置于 Explorer。 |
| `pane_heading()`、`search()`、`state()` | Explorer 和 Inspector 标题、缺陷文本过滤、缺陷读取及 Diff 缺失／异常反馈。 |
| `.tree-row`、`.row-version`、`.primary`、`.ai-facts` | 列表选中、记录编号、运行与登记主按钮、证据 ID。 |
| `dialog`、`.dialog-heading` | 套件 Drawer 与确认回归共享模态基础样式及浏览器原生键盘行为。 |
| `.ai-code`、`.ai-token-*`、`splitSource()`、`tokenize()`、`colorLine()` | Diff 提取行文本和原始偏移，沿用只读的 Python 着色和等宽源代码。 |
| `sameFilename()`、`runState()`、`readout()` | 沿用 F04 文件名同一性与执行状态，Inspector 属性使用统一定义列表呈现。 |

[共享模板](../../frontend/templates/studio_components.html) · [V1 CSS](../../frontend/static/studio-system.css) · [代码工具](../../frontend/static/studio-source.js) · [执行证据](../../frontend/static/run-evidence.js)

F05 专用控制包括失败项定位、候选版本比对、原始套件 Drawer、确认回归和回归历史。原始断言片段与历史状态从对应运行记录读取，Diff 使用真实版本源文件计算。[F05 模板](../../frontend/templates/bugs.html) · [版式](../../frontend/static/bugs.css) · [证据实现](../../frontend/static/bug-evidence.js)
