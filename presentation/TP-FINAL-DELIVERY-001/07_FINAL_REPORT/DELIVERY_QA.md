# 交付验收记录

WP02 / WP05；实际操作者 Codex。教师来源为用户确认的五张原图。材料核查保留历史二轮列及当前材料列。H01、H02、H04 补齐幻灯片与讲稿展示，H05 的现场环节仍待五人联排。

| 检查对象 | 验证方法 |
|---|---|
| 评分与证据 | 从 0d9e893 读取八份原件，重算 64 行历史分布；重开两份 XLSX，核对每项编号、变更的三行、七维满分及加分上限。 |
| 放映与可编辑性 | 用本机 Microsoft PowerPoint 16.0 打开 PPTX，导出 PDF 与 15 张逐页 PNG；核对页面数量、宽高比、原生文本、演讲备注和图表内嵌工作簿。检查全页缩略图及六张技术重点页。 |
| 数值和来源 | P07、P12 使用 Demo Lab 套件 #1；P08 使用专项套件 #8。P09 单独使用 geometry 的五个变异。P10 的四个检出计数与冻结 CSV、独立图表及原始评测相互核对。 |
| 原件与归档 | 对 Git 副本、五张原图和十二条恢复消息验 SHA-256；逐个核对仓库快照中的 Git blob。在本机 Edge 逐一打开 19 份独立 SVG，检查每段文字的包围盒均位于 1280 × 720 画布内；解析 PNG、JSON 与导航链接，对最终 ZIP 再读 CRC、文件名、字节及摘要。 |

独立 Reviewer 查验了演示内容、备注和运行证据，指出 P07 的模板与 P08 的模型修复需要分开操作。本版已单列手册入口与版本，注明归档编号只适用于历史数据库副本。现场操作与签收保留在[缺口记录](GAP_REGISTER.md)。

[PowerPoint 边界测量](powerpoint-qa.json) · [逐页预览](previews/) · [机器校验回执](verification.json) · [文件指纹](FILE_MANIFEST.csv) · [原始副本来源](COPIED_EVIDENCE.csv)

复查命令为 `python -X utf8 presentation/TP-FINAL-DELIVERY-001/source/verify_package.py`。Python 环境使用 python-pptx、Pillow、pypdf 与 openpyxl。
