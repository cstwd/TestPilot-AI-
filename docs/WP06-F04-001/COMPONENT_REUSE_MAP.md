# F04 组件复用地图

工作包 WP06-F04-001。F04 界面继续使用本地 Jinja、原生 JavaScript、CSS，并消费 F01–F03 已使用的 Design System V1。[V1 实现](../WP04-F01-001/DESIGN_SYSTEM_V1_IMPLEMENTATION.md) · [F03 复用地图](../WP05-F03-001/COMPONENT_REUSE_MAP.md)

| 公共来源 | F04 复用 |
| --- | --- |
| `topbar()`、`context_selectors()`、`rail()`、`icons()` | 品牌、项目选择、模块定位、统一 Lucide 风格图标。工作台保留原 `#project` 和 `#file`。F04 顶栏绑定项目，执行配置绑定被测文件。 |
| `pane_heading()`、`state()`、`search()` | 左侧历史、右侧 Inspector、读取／空／错误状态，以及历史、用例、日志检索。 |
| `.tree-row`、`.pane`、`.explorer`、`.inspector`、`.ai-identity`、`.ai-facts` | 历史项选中状态、面板标题与层次、用例身份及证据属性。 |
| `.primary`、`.tool`、`--mono` | 紫色执行按钮、蓝色窗口控制，以及 nodeid、日志、耗时与 ID 的 JetBrains Mono／Consolas 回退字体。 |
| 运行词汇与 `readout()` | F03 的执行结果、F05 运行选择和 F06 质量报告使用的公共导出继续由 `runs.js` 提供。F04 为工作台结果加上视图层颜色和上下文字段。 |

[公共模板](../../frontend/templates/studio_components.html) · [基础样式](../../frontend/static/studio-system.css) · [执行工作台样式](../../frontend/static/runs.css) · [运行证据展示](../../frontend/static/run-evidence.js)

F04 的专用组件包括双版本执行配置、按已保存记录分页的历史、带证据入口的用例表及可折叠终端。终端只处理常规文本节点和搜索标记，保留传输中的原始载荷。[本页模板](../../frontend/templates/runs.html) · [协调控制器](../../frontend/static/runs.js)
