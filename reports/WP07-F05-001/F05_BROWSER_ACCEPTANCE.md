# F05 Edge 浏览器验收

WP07-F05-001，2026-11-27。Codex 在 Windows 使用本机 Microsoft Edge 158.0.4370.33。项目通过根目录 `main.py --no-browser --port <临时端口>` 启动，测试使用独立 SQLite 和原有 WASI 执行边界。[夹具](../../tests/test_dashboard.py#L20) · [浏览器验收用例](../../tests/test_bug_intelligence.py)

## 从失败运行到已登记缺陷

项目 2、`measurements.py` v1／文件 ID 1 的 `magnitude` 用 `template` 生成套件 1。真实首跑 1 有两个断言失败。由 F04 选择第二项进入 F05，恢复了 `test_generated.py::test_example_2`、运行 1 和项目 2。原始 Pytest 片段包含 `assert target(-3) == 3`，没有将第一项的断言归到第二项。登记得到缺陷 1，状态为待修复，打开套件 Drawer 核对原样 Pytest、套件来源和 SHA-256。[从 F04 定位](screenshots/desktop-intake.png) · [套件 Drawer](screenshots/desktop-original-suite.png)

只导入不同文件名和其他项目的同名文件时，无可用候选。之后导入 `MEASUREMENTS.py` v2（ID 4）与 `measurements.py` v3（ID 5），两者均按服务端 NOCASE 规则列为候选。双侧文件名、ID、修订及 SHA-256 与真实接口一致。测试核对替换行、两侧行号、标记和只读性。[无候选](screenshots/desktop-no-candidate.png) · [桌面并栏 Diff](screenshots/desktop-diff.png)

## 确认、执行和服务端判定

仅打开确认框后取消，API 的回归列表仍为空。实测请求只发送候选文件 ID，等待期间选择器及运行按钮禁用。通过持久化运行端点复核了每次运行的项目、文件、套件及确切 nodeid。[确认](screenshots/desktop-confirm.png) · [等待](screenshots/desktop-regressing.png)

| 顺序 | 被测候选 | 真实回归运行 ID | 用例及整套结果 | 该次判定 | 缺陷状态 |
| --- | --- | ---: | --- | --- | --- |
| 1 | v2／ID 4，`return x - 1` | 2 | 失败 | 待修复 | 待修复 |
| 2 | v3／ID 5，`return abs(x)` | 3 | 通过 | 已解决 | 已解决 |
| 3 | 再执行 v2／ID 4 | 4 | 失败 | 待修复 | 已解决，服务端优先采用 v3 的判定 |

三个回归均复用套件 1。浏览器选择运行 2 后刷新，恢复了缺陷、原始失败、候选 v2 和选中的回归 2。真实 API 对原始运行 1 的完整响应与回归前相同；通过页面再次打开时，F04 仍显示运行 1 的失败结果。从该失败用例回到 F05 会直接打开已登记的缺陷 1。[失败回归](screenshots/desktop-regression-failed.png) · [已解决](screenshots/desktop-resolved.png)

## 失败恢复与响应式

向候选 v2 的版本 GET 注入一次明确标注的 HTTP 503。页面隐藏 Diff、禁用回归，原始断言保留。点击“重新读取版本”后由真实服务重建两侧比较。缺陷搜索、已解决过滤和切换到无登记缺陷的独立项目均已核对。[注入截图](screenshots/injected-version-read-failure.png)

| 浏览器视口 | 观察 |
| --- | --- |
| 1440 × 900、1024 × 768 | Explorer、证据主区和 Inspector 并列，Diff 两列，页面无横向溢出。 |
| 768 × 1024 | 可按缺陷列表、详情、差异切换，Diff 用统一行格式。[平板 Diff](screenshots/tablet-diff.png) |
| 390 × 844 | 实测三个区段。双行号明确标示删行和加行，原始证据与回归历史可继续纵向阅读。[列表](screenshots/mobile-explorer.png) · [详情](screenshots/mobile-details.png) · [统一 Diff](screenshots/mobile-diff.png) |

实测保存 13 张无头 Edge 截图。人工视觉、物理手机和其他浏览器留待验收。[测试命令及退出结果](F05_REGRESSION_REPORT.md)
