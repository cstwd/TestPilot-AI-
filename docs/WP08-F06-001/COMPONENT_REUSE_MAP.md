# F06 组件复用地图

WP08-F06-001。F06 继承 F01–F05 的 Design System V1，沿用本地 Jinja、CSS 与原生 JavaScript。[V1 实现](../WP04-F01-001/DESIGN_SYSTEM_V1_IMPLEMENTATION.md) · [F05 复用地图](../WP07-F05-001/COMPONENT_REUSE_MAP.md)

| 公共入口 | F06 应用 |
| --- | --- |
| `topbar()`、`rail()`、`context_selectors()`、`icons()` | 共用品牌、模块导航、项目选择器和 Lucide 风格图标。项目选择放在运行 Explorer。 |
| `pane_heading()`、`state()`、`.tree-row`、`.row-version` | 历史及证据区标题、读取和空状态、选中运行和真实运行身份。 |
| `.primary`、`.ai-facts`、`dialog` | 主导出操作、报告证据定义表、指标口径 Drawer。 |
| `runState()`、`setStatus()`、`readout()`、`setupPager()` | 沿用 F04 的真实运行状态呈现及属性渲染。共享分页接受可选起始索引，F06 用以定位深链接。 |
| `--file`、`--status-ok`、`--status-error`、`--mono` | 蓝色辅助信息、真实状态语义和 JetBrains Mono／Consolas 回退。 |
| `sameFilename()` | 比较列表与现有 SQLite NOCASE 文件名身份一致。 |

[共享壳层](../../frontend/templates/studio_components.html) · [样式基线](../../frontend/static/studio-system.css) · [F04 视图工具](../../frontend/static/run-evidence.js)

F06 专用呈现包括 MetricCard、用例和缺陷分布、通过与覆盖度量、同套件对照表、HTML 阅读及打印样式。图形仅使用 CSS 与真实比率，旁边保留文字和分母。页面与下载使用同一读取快照。[指标实现](../../frontend/static/report-metrics.js) · [报告控制](../../frontend/static/reports.js) · [工作台样式](../../frontend/static/reports.css)
