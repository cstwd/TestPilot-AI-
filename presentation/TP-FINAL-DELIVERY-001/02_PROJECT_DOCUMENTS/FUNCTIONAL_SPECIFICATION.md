# 功能与验收

| 功能 | 可观察验收 | 实际成果 |
|---|---|---|
| F01 导入 | 同名文件形成新版本，旧版与原始 SHA 继续可读 | 项目中心与 Demo Lab v1/v2 |
| F02 分析 | 识别有效源码的限定名、类函数、行号及语法错误 | telemetry.py 工作台图谱、源码和局部邻域 |
| F03 生成 | 套件有目标、模式、源与校验状态 | 模板工作台实录，历史 AI API 成功，最新试跑受资源守卫 |
| F04 执行 | 持久化 pytest 结果、退出码和失败节点 | Edge 单样本原版 1 失败、修复版 1 通过 |
| F05 回归 | 同套件验证新版本，并核对原失败节点 | unit_scaling v2 将缺陷收敛为 resolved |
| F06 分析及导出 | 同运行查询、显示及导出可复核 | 独立报告中心、真实 JSON 及通用质量页 HTML |
| F13 变异 | 原版基线通过、变异结果可定位、报告含分母 | geometry 原始 2/5，有效 2/3，另有冻结四组 |

[完整 SPEC](raw/docs/SPEC.md) · [原功能映射](raw/docs/FEATURE_MAP.md) · [样本回执](../04_TESTING_EVIDENCE/MUTATION_TESTING/reports/phase07/edge-run.json)
