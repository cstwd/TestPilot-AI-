# WP03-AST-VISUAL-REFINE-001 · 人工评审反馈

基线 `c9737be`。WP03 登记负责人赵君豪，定位和修复操作者 Codex，人工复核待签收。

| 可复查的问题 | 定位与修复 | 复验依据 |
| --- | --- | --- |
| 控制台的 7 ms 被理解成了 AST 解析耗时。 | 基线 `analysis.js` 第 352–354 行包裹浏览器 API 调用，第 361 行写入控制台。改成“分析请求（浏览器端）”，在帮助中标明响应正文和 JSON 读取边界。 | 延迟浏览器 JSON promise 的独立测试，快照、重播和 HTTP 错误分支。[指标审计](../../reports/WP03-AST-VISUAL-REFINE-001/VISUAL_REFINEMENT_REPORT.md) |
| 放大局部后重播，画布沿用原镜头，其他分支会在视野之外出现。 | 基线 `createCanvas` 直接导出 `animation.replay`，只重置时间轴。本次在相同时钟上从当前位置返回可见结构的适配镜头。 | 从局部重播，暂停、继续并核对最终视野。[有头验收](../../reports/WP03-AST-VISUAL-REFINE-001/ANIMATION_ACCEPTANCE.md) |
| 窄屏下控制台一直占据图谱高度，用户无法临时收起。 | 基线控制台是静态 section。本次改成默认展开的原生 details，播放阶段保留在 summary。 | 点击与键盘展开，检查画布高度及宽度和选中状态。[回归记录](../../reports/WP03-AST-VISUAL-REFINE-001/PERFORMANCE_REGRESSION.md) |
| 首轮有头实拍中，聚焦 `Sample.normalized` 后文件根节点已移出图外，左边缘仍留有 `telemetry.py` 标签。 | 点的绘制保留外沿缓冲区，名称又受到屏幕边界钳位。标签现在仅跟随圆心在视口中的节点。手动缩放后的窗口尺寸变化也重新报告当前倍率。 | 修正后重新载入页面、从 F01 重新录制；复查方法局部图。[最终 Source 截图](../../reports/WP03-AST-VISUAL-REFINE-001/screenshots/05-source.png) |
| 大图中搜索第 999 行的方法后，Explorer 切到了正确分页，选中行却仍在可见区下方。 | 创建目标符号行并切页后，滚动最近的符号列表到足以看清该行的位置。 | 检查目标行相对滚动容器的上下界，并重新拍摄。[大图局部](../../reports/WP03-AST-VISUAL-REFINE-001/screenshots/large-real-focus.png) |
