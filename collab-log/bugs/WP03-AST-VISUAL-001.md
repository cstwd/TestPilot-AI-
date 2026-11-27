# WP03-AST-VISUAL-001 · Source 行号对齐

| 字段 | 记录 |
| --- | --- |
| 责任包与操作人 | WP03，界面联调关联 WP02。发现、修复、复验由 Codex 执行；人工复核待签收。 |
| 观察与复现 | 在 Edge 的 1440 × 900 视口中，经 F01 导入 telemetry.py，进入 F02，选中 Sample.normalized 并打开 Source。长短代码行的行号列起点不一致。 |
| 原因与修复 | 源码行复用了按钮的 Flex 布局，继承的居中对齐与图文间距会随内容宽度移动行号。为源码行单独设置起始对齐和零间距，行号列保留固定最小宽度。 |
| 实测复核 | 浏览器测试比较可见行号的左缘像素位置，再核对范围高亮、复制和反向定位；新版截图已重新拍摄。[检查器样式](../../frontend/static/ast-inspector.css) · [浏览器验收](../../reports/WP03-AST-VISUAL-001/BROWSER_ACCEPTANCE.md) · [修复后截图](../../reports/WP03-AST-VISUAL-001/screenshots/source-inspector.png) |
