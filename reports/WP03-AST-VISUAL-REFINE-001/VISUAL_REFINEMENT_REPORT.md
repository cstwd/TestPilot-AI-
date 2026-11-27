# F02 动态图谱视觉精修

**WP03-AST-VISUAL-REFINE-001** · 2026-11-27 · 工作目录 `D:\TestPilot AI`。实现基线 `7f724d05c622e6be73de2f01ac5ddbb8e5171dc1`，证据基线 `c9737be`。WP03 登记负责人赵君豪，实际实现与测试由 Codex 执行，组长陈帅廷协调人工验收。[成员职责](../../collab-log/member_contributions.md)

## 截图中的 7 ms

旧截图的右下角实际写着 **分析请求往返 7 ms**。截图对应已获取分析响应的 `telemetry.py` v1。按基线执行 `git show c9737be:frontend/static/analysis.js`，第 352 行记录 `performance.now()`，第 353 行等待 `api(base + "/analysis")`，第 354 行取两次时钟之差并四舍五入为整数，第 361 行将它显示在 `#ast-timing`。截图只保留当次显示值，无法从这个整数倒推网络与服务端各耗了多少时间。[基线截图右下角](../WP03-AST-VISUAL-001/screenshots/class-overview.png)

| 计量边界 | 从源码可核对的事实 |
| --- | --- |
| 起点 | 已获得并验证项目、文件及修订，浏览器即将发出 `GET /api/files/{file_id}/analysis`。获取文件源码的前一次 GET 已完成。[计时调用](../../frontend/static/analysis.js#L360) |
| 终点 | 公共 `api()` 等待 `fetch` 并返回 `response.json()`。外层 `await` 在收到、读完并解析 JSON 后才结束。读表、Python 解析、HTTP 传输和客户端调度都可能影响这段时长；图适配、布局、绘制与动画发生在取差之后。[请求辅助函数](../../frontend/static/workbench.js#L13) |
| 后端 | 路由读取不可变修订并调用 `analyze`。其中执行 `ast.parse`、节点上限检查、编译校验与符号提取。响应字段为 `file_id`、`filename`、`revision`、`sha256`、`valid`、`symbols` 和 `error`，没有分段计时。[分析函数](../../backend/analysis.py#L46) · [响应构造](../../backend/analysis.py#L60) |
| 新显示规则 | 成功读到分析响应后显示“分析请求（浏览器端） N ms”。悬停及操作帮助给出起止点。合法 HTTP 响应携带语法错误时仍可计量；HTTP 获取失败时数值留空。读取已校验快照仅显示“已读取本机分析快照”。重播沿用同一结果和控制台记录。[工作台控制器](../../frontend/static/analysis.js) |

旧压力报告另有 **7.0 ms**，测量的是测试画布创建渲染器与布局句柄的时间，输入为 1000 节点、2000 边。该量与截图的 7 ms 分别取自两次不同操作。[旧压力测量](../WP03-AST-VISUAL-001/PERFORMANCE.md)

## 图谱的五个观看动作

| 查看时机 | 本次改动 | 人工复核动作 |
| --- | --- | --- |
| 首次读图 | 沿原树的广度顺序揭示文件、类与函数。每个节点在 320 ms 内由半径的一半增长到正常大小，透明度用两端缓动，名称在节点显现后淡入。位置在播放前一次确定。 | 导入样例，观察根节点先显现，随后出现直接子项和更深的定义。 |
| 跟随连线 | 每条真实包含边用 460 ms 从父向子绘出。普通规模画布用小亮点标出正在绘制的线头，到达节点后消失。密图沿用同色批绘以限制每帧工作。 | 观察 STRUCTURE BUILDING 中途的一帧与完成帧。稳定后线条停止生长，图中没有常驻流光。 |
| 阅读邻域 | 选中点由外环标识，直接父子节点加亮轮廓，当前包含边以 2.1 px 绘在普通边之上。选中、悬停和邻接标签优先占位，标签避让节点、其他标签、文件标识及浮动工具栏。位置不足时省略低优先级标签。全名可从 Inspector 读取。 | 选中类，再双击读局部。将长符号移近工具栏，比较缩放前后标签与图元。 |
| 重播 | 当前镜头平滑返回当前可见结构的适配范围；平移和缩放共享 600 ms 开场。已适配时做一次轻微后拉。镜头跟随前端播放时钟，暂停冻结、继续衔接，缩放数值取当前帧。减少动画模式直接到适配位置。 | 聚焦方法，点重播，在开场暂停并继续，核对选择、最终视野和请求数量。 |
| 概览大型结果 | 保留本地 D3 树坐标与词法顺序。超过 160 节点时加大分支之间的角间距；同一父项下至少 12 个且全为叶子的定义，在各自扇区内分布到多条交错半径上。按各层负载计算环距。布局随同一数据可复现。 | 查看 1000 节点全图，再搜索 `Channel26.signal35`，对照其父级和第 999 行。 |

节点身份和包含边都沿用同一份图模型。文件蓝、类紫、函数青、方法黄绿贯穿画布、类型筛选与 Inspector。节点的基础大小按类型设定。[时间轴](../../frontend/static/ast-animation.js) · [现有画布上的布局、绘制与镜头变更](../../frontend/static/ast-canvas.js) · [图数据适配器](../../frontend/static/ast-model.js)

在首轮有头录制的 Source 画面里，聚焦后的 `Sample.normalized` 在中央，文件根节点已经移至画布外，它的标签却被压在左边缘。最终实现对标签检查圆心是否在视口中，同时保留跨边界连线的绘制。可以沿着方法与父类的边追踪邻域，画布边缘不再出现无主的文件名。[问题定位及复验](../../collab-log/bugs/WP03-AST-VISUAL-REFINE-001.md)

## 选择、源码与控制台

- **Inspector** 将类型标志和完整限定名放在三个标签共享的固定区域。由 Structure 跳到同名方法，或在 Source 中选择另一行时，用户可同时看到新的父级限定名和代码。切换节点会触发一次 220 ms 的类型标志反馈。选择立即生效，系统减少动态或关闭动效时保留静态标志。同一节点内移动行号、翻源码或切标签时维持标题稳定。[选择与渲染](../../frontend/static/ast-inspector.js) · [选择反馈样式](../../frontend/static/ast-inspector.css)
- **Analysis Console** 默认展开。点标题，或在标题获得焦点时按 Enter 或空格，可用浏览器原生控件展开与折叠。折叠后继续显示真实请求／播放阶段，释放的高度交还给画布；重新展开可读当前修订、包含边计数、响应来源和错误信息。[模板](../../frontend/templates/analysis.html#L94) · [控制台样式](../../frontend/static/analysis.css)
- **等待分析** 在文件归属验证完成后即显示名称与修订。在真实分析 GET 待返回时，画布显示“正在读取 AST 分析”。请求结束后，前端在已返回定义上播放视觉时间轴。播放控制、树、源码、F03 目标选择继续使用相同的图节点及不可变文件 ID。[请求分支](../../frontend/static/analysis.js)
- **跨页定位** 在 1000 节点验收中，搜索最后一个方法后，Explorer 在正确的分页上高亮了该行，但该行落在可见区下面。现在切换符号页后将目标行滚入最近的滚动容器；画布焦点与 Inspector 同步显示限定名。[大图全览](screenshots/large-real-layout.png) · [定位第 999 行](screenshots/large-real-focus.png)

## 人工验收入口

1. [播放 23.28 秒实录](video/analysis-session.mp4)。约 4.80 秒观察尚未连线的节点，6.04 秒看正在绘制的包含边，10.68 秒看 `Sample.normalized` 的第 10–11 行，14.20 秒看暂停帧，15.76 秒看重播归位。拍摄时给分析请求增加 1600 ms 浏览器传输延迟以看清等待，单独的性能回归采用正常网络条件。[逐帧索引与录制命令](ANIMATION_ACCEPTANCE.md)
2. 重走主线时，从 PyCharm Run 根目录 `main.py`，经 F01 导入 [telemetry.py](../../eval/ast_visual/telemetry.py)，在 F02 搜索 `mean_value`、刷新并点“为此函数生成测试”。用 F03 的目标函数控件和 URL 复核上下文。六个视口实测、版本异常、网络错误与压力数据见[性能与业务回归](PERFORMANCE_REGRESSION.md)。
3. 检查边缘情形的自动化证据可运行 `.\.venv\Scripts\python.exe -m pytest tests/test_ast_canvas_refinement.py -q -s --tb=short`。两项通过，用时 70.06 秒。测试从 Edge 的绘图调用实测样例中的 16 个名称，标签相互重叠及压住节点的计数均为 0。把文件中心移到 x = −12 px 后，文件名退出画面。从 300% 重播时开场暂停 350 ms，像素保持一致；恢复后归位至 100%。大图中实测 27 个类的每组 36 个方法均占三个半径。[画布断言](../../tests/test_ast_canvas_refinement.py)

实现、测试和证据按本工作包独立提交；可在当前仓库用 `git log -1 --format="%h %an %s" -- reports/WP03-AST-VISUAL-REFINE-001/VISUAL_REFINEMENT_REPORT.md` 定位交付提交。到此进入人工验收。
