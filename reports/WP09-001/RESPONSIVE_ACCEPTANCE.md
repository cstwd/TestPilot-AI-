# WP09-001 六页响应式验收

使用 Microsoft Edge 158.0.4370.33 和 Playwright 1.65.2 在 Windows 11 调整同一浏览器的视口尺寸。六页加载真实数据，手机视口通过相应面板选择入口打开主区域。每格为 Edge 测得的主工作区宽度，单位为 CSS 像素。

| 模块与表面 | 1920×1080 | 1440×900 | 1280×800 | 1024×768 | 768×1024 | 390×844 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| F01 文件及版本 `#file-groups` | 1135 | 655 | 495 | 313 | 694 | 360 |
| F02 图谱 `#ast-canvas` | 1316 | 836 | 676 | 750 | 724 | 390 |
| F03 套件与代码 `#suite-panel` | 1278 | 785 | 638 | 415 | 700 | 366 |
| F04 用例与结果 `#run-result` | 1280 | 795 | 640 | 514 | 690 | 366 |
| F05 版本比较 `#diff-workspace` | 1292 | 804 | 652 | 521 | 700 | 366 |
| F06 质量指标 `#report-quality` | 1297 | 813 | 657 | 434 | 690 | 366 |

36 个组合实测页面横向 `scrollWidth` 等于视口宽度，主工作区高度大于 20px，未检出重复 DOM ID。六页共用 `--panel=#141620`、`--ink=#eef0fa`。桌面与平板的模块栏高亮当前页，390px 顶部菜单提供全部六个目标，支持 Enter、Space、Escape 与点击外部关闭。390px 的图谱高 471px。F01 文件面板、F02 图谱与 Source、F03 源码与结果、F04 用例与日志、F05 统一 Diff、F06 指标与证据均在真实数据上检查。数值与选择器见原始输出中的 `WP09_RESPONSIVE`、`WP09_NAV` 与各模块回归记录。 [Edge 原始输出](raw/integration-edge.txt)

## Edge 截图

| 页面 | 1440×900 | 390×844 |
| --- | --- | --- |
| F01 项目中心 | [桌面](screenshots/projects-1440x900.png) | [手机](screenshots/projects-390x844.png) |
| F02 代码知识图谱 | [桌面](screenshots/analysis-1440x900.png) | [手机](screenshots/analysis-390x844.png) |
| F03 AI 测试生成 | [桌面](screenshots/generation-1440x900.png) | [手机](screenshots/generation-390x844.png) |
| F04 测试执行 | [桌面](screenshots/runs-1440x900.png) | [手机](screenshots/runs-390x844.png) |
| F05 缺陷与回归 | [桌面](screenshots/bugs-1440x900.png) | [手机](screenshots/bugs-390x844.png) |
| F06 质量报告 | [桌面](screenshots/reports-1440x900.png) | [手机](screenshots/reports-390x844.png) |

这些是 Windows Edge 的视口验收，未使用实体手机或平板。
