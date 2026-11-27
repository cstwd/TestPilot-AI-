# F03 组件复用地图

工作包 WP05-F03-001。F03 使用 TestPilot AI Design System V1，保留 Jinja、原生 JavaScript 和本地 CSS。[V1 实现说明](../WP04-F01-001/DESIGN_SYSTEM_V1_IMPLEMENTATION.md) · [F01/F02 复用地图](../WP04-F01-001/COMPONENT_REUSE_MAP.md)

| 公共来源 | F03 用法 |
| --- | --- |
| `icons()`、`icon()`、`topbar()`、`rail()` | 品牌、Lucide 风格线图标和当前模块导航。顶栏保留默认布局参数给 F01/F02。F03 用顶栏插槽放置面包屑与手机模块菜单。 |
| `context_selectors()` | 从原顶栏提取项目、修订选择器及原有 ID。F01/F02 仍由顶栏默认渲染这一模板，F03 把它放在 Explorer 里。 |
| `pane_heading()`、`search()`、`state()` | Explorer 和 Inspector 标题、函数搜索、真实加载／空／错误状态。 |
| `.pane`、`.explorer`、`.inspector`、`.primary`、`.ai-facts` | 深色表面、面板分隔、紫色生成操作及语义化属性列表。普通导航用文件蓝色令牌，状态文字与图标共用 V1 语义色。 |
| `splitSource()`、`tokenize()`、`colorLine()`、`.ai-source-*` | 目标源码与生成源码使用公共行号、等宽字体和 Python 词法颜色。F03 截取定义范围、按页渲染、以原文复制。 |
| `buildGraph()`、`labelStatus()` | 沿用 F02 对可生成目标的识别、函数签名和版本校验；沿用 F04 的运行状态词汇。 |

[模板宏](../../frontend/templates/studio_components.html) · [V1 样式](../../frontend/static/studio-system.css) · [源码工具](../../frontend/static/studio-source.js) · [F02 AST 适配器](../../frontend/static/ast-model.js) · [F04 状态词汇](../../frontend/static/runs.js)

F03 自有的版面与交互包括函数列表、固定模式的生成表单、历史套件选择、独立验证状态和 F04 交接。给定相同输入，各页面共享版本身份和代码阅读样式，各自呈现对应的业务证据。[页面样式](../../frontend/static/generation.css) · [控制器](../../frontend/static/generation.js)
