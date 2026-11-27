# F02 代码知识图谱技术设计

**WP03-AST-VISUAL-001 · Visual Intelligence Engine**

本任务归属 WP03，登记负责人为赵君豪，组长陈帅廷协调阶段验收。本次实现、文档和自动化核查的实际操作者为 Codex。F02 静态分析契约归属 WP01，界面联调关联 WP02。人工复核人及签收日期待登记。[工作包职责](../../collab-log/member_contributions.md)

用户从项目的一个不可变 Python 文件版本开始，选择图上的定义，查看它的行区间、直接父子和参数；有合法测试目标时，携带相同版本进入 F03。桌面主阅读面是结构画布，Explorer 与 Inspector 提供两条查证路径。图中每条边都可以通过子节点的限定名和源码范围复核。设计参考采用 GitNexus A 的工具工作台、Balanced 信息密度和 Cinematic 渐进显现，落实为 TestPilot 自有的深色紫、文件蓝和函数青；本任务只面向 F02。[设计参考的原始审计](../TESTPILOT-FRONTEND-REFERENCE-001/GITNEXUS_DESIGN_AUDIT.md) · [F02 原验收](../../F02_MODULE_ACCEPTANCE.md)

## 实施前十项核对

| 项 | 核对结果与设计影响 |
| --- | --- |
| 1. 实际目录与 Git | `Get-Location` 为 `D:\TestPilot AI`。实施起点为 `74228571823aa5f38824e948dc111920fae72c3f`，可用 `git show 7422857:frontend/static/analysis.js` 等命令回看原件。 |
| 2. F02 模板 | 基线 `frontend/templates/analysis.html` 是 5 行被包含的片段，仅提供符号索引、计数和分析元数据。新版由 `workbench.html` 在 analysis 分支载入完整模板，公共导航仍由既有模块表生成。[模板分派](../../frontend/templates/workbench.html#L1) · [新版分析模板](../../frontend/templates/analysis.html) |
| 3. 后端静态分析 | `ast.parse`、遍历计数及仅编译校验；可记录类、同步与异步函数、签名参数、返回注解、文档字符串、起止行。语法错误和处理上限进入错误体；分析路径不会导入或运行用户程序。[后端定义](../../backend/analysis.py#L29) |
| 4. 接口实查 | Codex 用真实 `main.py` 服务读取 Audit 项目和 audit.py v1。下节保留实际数据；本文另以同一原文重新计算摘要和分析字段，核对完整内容。F02 进入页面的业务请求均为 GET。[导入版本服务](../../backend/projects.py#L51) · [分析路由](../../backend/analysis.py#L61) |
| 5. 原页面脚本 | 基线 `analysis.js` 的 `showAnalysis` 获取一次分析结果，逐行生成 article；已有语法错误提示与 F03 入口。新版复用同源请求与链接，单独组织图模型、浏览器画布、检查器和呈现动画。[公共调度](../../frontend/static/workbench.js#L89) · [新版控制器](../../frontend/static/analysis.js#L287) |
| 6. 公共样式与壳层 | 原版加载 `dashboard.css`、`workbench.css`，共享上方项目/文件选择、左侧模块导航和 1040 px 容器。新版 F02 单独加载两份静态 CSS，以整窗容纳画布；路由继续使用原 /workbench/analysis。[旧样式](../../frontend/static/dashboard.css#L16) · [新版加载顺序](../../frontend/templates/analysis.html#L3) |
| 7. 节点及嵌套 | API 返回词法先序的扁平符号数组；同名定义可出现在不同行。文件根来自所选文件，方法取决于直接父节点是否为类；嵌套函数继续标记 Function。当前投影只连 contains，调用、导入、运行依赖均无适用返回字段。[模型](../../frontend/static/ast-model.js#L23) |
| 8. 依赖盘点 | 起始 frontend 无已提交前端包清单或图库静态件，Python 依赖描述 FastAPI、Jinja 与测试工具。评估三个图方案后仅分发 d3-hierarchy 两个导出的本地 ESM 和许可证。[项目依赖](../../requirements.txt) · [图库本地目录](../../frontend/static/vendor/) |
| 9. 原测试 | `tests/test_f02.py` 覆盖静态无执行、错误或空结果、条件定义；原 Edge 工作台用例对签名、行号和语法错误有断言，F03 用例从分析页跳转。保留这些语义，并补测交互、版本切换、密图与窄屏。[原 F02 测试](../../tests/test_f02.py) · [原浏览器验收](../../tests/ui_workbench.py#L49) · [新增测试](../../tests/test_ast_studio.py) |
| 10. 并行改动 | 起步 `git status --short --branch` 只有 `reports/model/` 为未跟踪产物。该目录归属既有工作。技术设计核查时出现的 F02 文件、测试及截图逐项按本 WP 对照；提交前按路径检查 staged diff，避免纳入并行产物。 |

## F01 → F02 的请求与实数样本

在一个只有 Audit 项目与 audit.py v1 的验收数据集中，进入 `/workbench/analysis?project=1&file=1`。以下列出无本机快照时的四个业务请求与 JSON 正文，GET 无请求体，成功时均为 HTTP 200。字段顺序与空白不属于接口契约。实际图在浏览器生成。[公共入口](../../frontend/static/workbench.js#L89) · [版本与请求核验](../../frontend/static/analysis.js#L342)

```http
GET /api/projects HTTP/1.1

[{"id":1,"name":"Audit"}]
```

```http
GET /api/projects/1/files HTTP/1.1

[{"id":1,"project_id":1,"filename":"audit.py","revision":1,"sha256":"aa3c05b3d81b3db1b90303dbeb28661fb9081d4fe982720b3376f469c4b2b5bb"}]
```

```http
GET /api/files/1 HTTP/1.1

{"id":1,"project_id":1,"filename":"audit.py","revision":1,"source":"class Deck:\n    async def item(self, n: int = 2):\n        def value():\n            return n\n        return value()\n","sha256":"aa3c05b3d81b3db1b90303dbeb28661fb9081d4fe982720b3376f469c4b2b5bb"}
```

```http
GET /api/files/1/analysis HTTP/1.1

{
  "file_id": 1,
  "filename": "audit.py",
  "revision": 1,
  "sha256": "aa3c05b3d81b3db1b90303dbeb28661fb9081d4fe982720b3376f469c4b2b5bb",
  "valid": true,
  "symbols": [
    {"name":"Deck","kind":"class","line":1,"end_line":5,"parameters":[],"returns":null,"docstring":""},
    {"name":"Deck.item","kind":"async_function","line":2,"end_line":5,
     "parameters":[
       {"name":"self","kind":"positional_or_keyword","annotation":null,"default":null},
       {"name":"n","kind":"positional_or_keyword","annotation":"int","default":"2"}
     ],"returns":null,"docstring":""},
    {"name":"Deck.item.value","kind":"function","line":3,"end_line":4,"parameters":[],"returns":null,"docstring":""}
  ],
  "error": null
}
```

| 场景 | 真实语义与界面处理 |
| --- | --- |
| 同名重导入 | 相同项目同名文件与最新版本摘要相同则复用该条记录，变化后创建新 file ID 和递增 revision。`version_id` 是浏览器节点上对不可变 `file.id` 的别名。revision 序号须结合项目和文件名使用。[写入逻辑](../../backend/projects.py#L60) |
| 无符号与解析失败 | 合法空源返回 `valid:true,symbols:[],error:null`，画布仅保留 File、0 边。样例 `def missing(:\n` 对分析函数返回 `valid:false,symbols:[],error:{"message":"invalid syntax","line":1,"column":13}`；HTTP 可成功但图显示错误，源码仍可读。行列缺失显示“—”。超过 24000 个 AST 语法节点时错误消息标明上限，非图中的可视符号上限。[分析结果](../../backend/analysis.py#L46) · [错误呈现](../../frontend/static/analysis.js#L303) |
| 记录或连接不可用 | 查无文件时 HTTP 404，JSON 为 `{"detail":"对应记录不存在"}`。网址所指版本和当前项目成员不一致，界面报告无法定位，避免默认选中另一文件。请求异常或摘要不匹配时显示诊断；无项目或无文件时给出 F01 导入路径。[记录查询](../../backend/store.py#L18) · [入口保护](../../frontend/static/analysis.js#L342) |
| 重读、重播与重新分析 | 本机最多保留最近四份分析响应，键含项目 ID、文件 ID、修订、文件名、SHA-256。每次进入先读原文件并核验身份。快照命中用于呈现，`?refresh=1` 绕过快照并重新 GET 后端，重播仅从当前图重新播放。存储不可用时本页仍可显示与重播。[快照管理](../../frontend/static/analysis.js#L36) · [请求分支](../../frontend/static/analysis.js#L281) |
| 耗时和阶段 | 接口一次返回完整 JSON，没有逐阶段百分比、推送流或服务端耗时字段。Console 中“分析请求往返”取浏览器 performance.now 前后差，含传输与服务处理；读取快照单独标注。SCANNING 为读取待返回，随后动画阶段只解释已取得的结果。[请求计时](../../frontend/static/analysis.js#L289) · [呈现时钟](../../frontend/static/ast-animation.js) |

## 从符号到图元

`buildGraph` 在源码与分析的 ID、文件名、revision、SHA-256 一致后，按限定名和行范围恢复父子关系。栈弹出已越过结束行的祖先，同名不同区间用开始行消歧。前缀或父区间不一致则拒绝建图。根 ID 为 `file:1`，符号 ID 的形式为 `symbol:文件ID:起始行:限定名`。每条边的 id 为 `contains:` 加子节点 ID，边上记录 source、target 和 relation_type。[图模型](../../frontend/static/ast-model.js#L23)

| 本例图元 | 类型与行区间 | 父节点 |
| --- | --- | --- |
| `file:1` | File · audit.py，1–5 | 根 |
| `symbol:1:1:Deck` | Class，1–5 | `file:1` |
| `symbol:1:2:Deck.item` | Method · async，2–5 | `symbol:1:1:Deck` |
| `symbol:1:3:Deck.item.value` | Function，3–4 | `symbol:1:2:Deck.item` |

以上为 4 节点、3 条有向包含关系。参数和返回注解保留在属性中；调用表达式 `value()` 位于源码中，不产生额外边。F03 的准入要求按 Module.body 的单一同名顶层同步函数判定，条件块中的间接定义、方法、异步或嵌套函数不提供生成入口。文件根恰有一个合格目标时也可直接前往该目标。[生成入口映射](../../frontend/static/ast-model.js#L65) · [选择与跳转](../../frontend/static/analysis.js#L392)

## 选型、离线分发与可重建性

| 候选 | 直接适用能力 | 对本项目的决策 |
| --- | --- | --- |
| Sigma.js + Graphology | Graphology 提供有向、无向和混合图，Sigma 使用 WebGL 绘图，内置缩放、平移、悬停。适合面向多类边的网络探索。[Sigma](https://www.sigmajs.org/) · [Graphology](https://graphology.github.io/) | 保留为未来跨文件关系有可靠数据后的候选。当前每个非根节点只有一个父亲；引入通用图容器与 WebGL 管线，对这一层级任务增加维护面。 |
| Cytoscape.js | 支持图元素及集合、样式、事件与多种布局；内置 breadthfirst 可表达层级。[Cytoscape.js 官方文档](https://js.cytoscape.org/#layouts/breadthfirst) | 若未来需要编辑网络、算法遍历和多布局切换，可再次评估。当前仅需节点位置，测试目标、行定位与检查器仍须由产品自行维护。 |
| D3 hierarchy/tree + 原生 Canvas 2D | tree 给层级节点分配坐标，可将一个维度投射为角度。只引入层级构造与布局，Canvas 和 DOM 保留本项目的交互、标签避让和检查器。[D3 tree](https://d3js.org/d3-hierarchy/tree) · [集成代码](../../frontend/static/ast-canvas.js#L13) | **采用。** 一个文件对应一棵固定的树，每个定义有可解释的深度。按叶数与深度设置半径，单分支时收窄角度以减轻边回折。画布和 Explorer 共用一套业务 ID。 |

构建机使用 `d3-hierarchy@3.1.2`、`esbuild@0.27.0`。已用相同入口和构建参数在内存重建 ESM，得到与提交候选逐字节相同的 **4,354 B**。下列示例适用于含上述固定 npm 包的暂存工程，工作目录为它的 `node_modules`。输出目录选独立复验位置；Windows 项目演示只需现成分发件和 `main.py`。[本地 ESM](../../frontend/static/vendor/d3-hierarchy.js) · [随附 ISC 许可证](../../frontend/static/vendor/d3-hierarchy.LICENSE.txt)

```powershell
$verifyDir = Join-Path ([IO.Path]::GetTempPath()) ('testpilot-d3-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $verifyDir | Out-Null
'export {hierarchy, tree} from "d3-hierarchy";' | & .\.bin\esbuild.cmd --bundle --minify --format=esm "--outfile=$verifyDir\d3-hierarchy.js"
Copy-Item -LiteralPath '.\d3-hierarchy\LICENSE' -Destination (Join-Path $verifyDir 'd3-hierarchy.LICENSE.txt')
Get-ChildItem -File $verifyDir | Get-FileHash -Algorithm SHA256
```

| 同源分发文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| `d3-hierarchy.js` | 4354 | `8b39952c4cc364fa36797092c45059f45fcf5a6d5659138ae5aacecb5007ea73` |
| `d3-hierarchy.LICENSE.txt` | 731 | `e008c5e25a6be382593089c29bfabbc553c6378eee02895aec46ce396cc404ee` |

本地静态模块经相对 import 解析，正常加载无 CDN、前端开发服务或浏览器端安装步骤。表中摘要用于比对制品字节；发布者身份认证须另有签名凭据。

## 视觉、交互与时间轴

顶部保留品牌、项目／版本、节点搜索、设置与帮助。工作区左侧模块导航以当前页标识选中项。1000 px 起，顶栏并列真实节点数和关系数；窗口更窄时，计数移至画布顶栏，底部 Selection Bar 给出当前限定名和适用的下一步。底部 Analysis Console 播报状态、类别计数与计时来源。[页面结构](../../frontend/templates/analysis.html) · [工作台布局](../../frontend/static/analysis.css#L54)

| 区域／输入 | 行为与核验方法 |
| --- | --- |
| Explorer | 项目文件可搜索并切换版本，符号树能收合父项、按每页 120 项阅读符号；跨页选中后展开其上级并切至对应页。点击行与画布同步选择；类型开关控制 File/Class/Function/Method，隐藏已选类型会清除失效选择。无匹配和全部隐藏有文字反馈。[文件与搜索](../../frontend/static/analysis.js#L93) · [符号树](../../frontend/static/analysis.js#L210) |
| 全局节点搜索 | `/` 聚焦，按当前文件内限定名忽略大小写匹配，最多二十项，方向键、Enter、Esc 可完成选择或关闭。选择后聚焦画布，版本和节点写入 URL，刷新可恢复。[搜索处理](../../frontend/static/analysis.js#L150) |
| 画布与选中态 | 悬停显示重点标签；单击选择、空白取消、双击按选中节点和直接邻接范围聚焦；单指或主键拖拽平移，滚轮绕指针缩放，按钮以中心为基点。适配按可见范围，复位按全图。对稠密图限制非重点标签，优先选中或悬停，绘制后释放空闲帧。[绘制与标签](../../frontend/static/ast-canvas.js#L209) · [指针处理](../../frontend/static/ast-canvas.js#L365) |
| Inspector | Overview 给出名称、身份、类型、版本、行范围及可用签名／摘要。Source 显示只读源码、行号、定义范围和本地词法着色；每页 80 行，可复制当前定义或整份原文。选择源码行会定位包含它的最内层定义，支持上下键及 Home/End。Structure 显示可点击的父项与直接子项。[检查器](../../frontend/static/ast-inspector.js#L166) |
| F03 联动 | 只有合格目标才显示“为此函数生成测试”，路由继续传递 project、file、symbol。选不同修订重新取证，不沿用上一次的套件、AST 选择或源码片段。[跳转与选中同步](../../frontend/static/analysis.js#L392) |
| 设置、帮助与可访问性 | 设置可切换节点名称和渐进动画，有已存快照时可重新读取；帮助对话框列出手势、快捷键与项目入口。图标按钮提供可访问名称。Explorer 的真实按钮及 Inspector 提供画布的键盘等价入口；系统减少动画偏好可跳过时间轴。[设置／帮助](../../frontend/static/analysis.js#L133) · [标签与焦点](../../frontend/static/ast-inspector.js#L121) |

File 为蓝色 `#639cff`（半径 19、文件符号），Class 为紫色 `#b291ff`（15、立方图符），Function 为青色 `#46dcc7`（11、ƒ），Method 为浅黄绿色 `#c3df77`（9、m）。半径是布局的基础像素，绘制会随缩放、密度调整。contains 由父向子绘出二次曲线，使用子类型色。通常宽 1.3 px，密图 0.8 px，所选邻边 1.95 px；选中优先绘制标签，弱化非邻接节点。[图元规范](../../frontend/static/ast-canvas.js#L4) · [线型与选择](../../frontend/static/ast-canvas.js#L209)

**播放时序。** SCANNING 的长度取决于实际请求。取得数据后，PARSING 在 0–1050 ms 依序显现节点（730 ms 分布、单点淡入 320 ms），STRUCTURE BUILDING 在 1050–2200 ms 显现边（690 ms 分布、单边 460 ms），INSPECTION 在 2200–2700 ms 让当前节点的外环舒展后收束，随后 COMPLETE。相机聚焦和选中扩环为 210 ms。暂停冻结呈现时钟，继续时从原位置推进，重播从图的已有数据开始；关闭动画或系统要求减少动态时直接完成。空闲时停止调度，画布尺寸或交互变化才触发重绘。[时间常量](../../frontend/static/ast-animation.js#L1) · [帧调度](../../frontend/static/ast-canvas.js#L330)

**响应式。** 1180 px 及以上左列 clamp(220–250 px)，右列 clamp(320–380 px)，中央取得剩余空间。901–1179 px 保留 220 px 左栏，320 px Inspector 为可开合覆盖层；900 px 及以下使用“资源／图谱／详情”互切，默认图谱。650 px 及以下顶栏两行、模块轨收起，品牌回首页，项目与版本在第二行。[断点](../../frontend/static/analysis.css#L135)

## 复核与证据

六个视口为 1920×1080、1440×900、1280×800、1024×768、768×1024 和 390×844。浏览器用例通过真实 F01 导入、F02 分析和 F03 目标跳转，核查选中、代码行、复制、筛选、大小变化和网络重读。验收分开登记真实产品链路和纯渲染压力数据。后者只向测试画布添加额外边，不能据此声称 API 返回跨定义关系。[测试入口](../../tests/test_ast_studio.py) · [可直接从 F01 导入的示例文件](../../eval/ast_visual/telemetry.py) · [实截与 QA 记录](../../reports/WP03-AST-VISUAL-001/)

| 复核口径 | 输入与可审查结果 |
| --- | --- |
| 真实结构 | 导入含 27 个类、每类 36 个方法的 Python 文件，真实分析应产生 1 + 27 + 972 = **1000 节点、999 条 contains**。点击末端定义应能查看对应限定名与源码。 |
| 渲染器上界样本 | 保留同一类节点规模，在测试渲染器输入中将边增至 **1000 节点／2000 边**。记录初始化时间、40 次缩放的帧间隔统计、600 ms 空闲窗口重绘次数。性能取实测记录，节点数不能代替流畅度结论。 |
| 复验命令 | 在根目录运行 `.\.venv\Scripts\python.exe -m pytest tests/test_f02.py tests/ui_workbench.py::test_f02 tests/ui_workbench.py::test_f03 tests/test_ast_studio.py -q -s`。正式 P0 复验仍从 PyCharm Run/Debug 启动根目录 main.py，并保留端口冲突、停止、重启与旧页面回归记录。 |

[宽屏 1440×900](../../reports/WP03-AST-VISUAL-001/screenshots/graph-1440x900.png) · [窄屏 390×844](../../reports/WP03-AST-VISUAL-001/screenshots/graph-390x844.png) · [类的直接子节点](../../reports/WP03-AST-VISUAL-001/screenshots/class-structure.png) · [源码检查器](../../reports/WP03-AST-VISUAL-001/screenshots/source-inspector.png)
