# WP03-DEMO-LAB-001 工作包验收

2026-11-27 · Windows 11 · 项目 Python 3.13.11 · 操作者 Codex

WP03 测试工程，登记负责人赵君豪。关联 F01–F06、F13 与 WP01、WP04、WP05 的验收。独立只读复核按仓库的 `testpilot-reviewer` 定义进行，项目组人工签收待登记。

| 项目 | 输入、输出与观测 |
| --- | --- |
| 源码与合同 | 25 GOOD、50 BUGGY、25 CHALLENGE。75 个独立修复版，150 个逐一复现的缺陷，400 个合同场景。[数据集验收](../../demo/TestPilot-Demo-Lab/reports/dataset_validation.md) |
| 独立验证 | 通过 `backend.runner.execute` 执行 WASI Pytest，700 通过、150 预期失败、0 跳过。8 项评分回归通过。 |
| 产品联调 | `main.py` 回环服务与临时 SQLite。F01/F02 处理十个冻结源码，F03 模板、F04 真运行、F05 同套件回归、F06 JSON 导出通过。[F05 回执](../../demo/TestPilot-Demo-Lab/reports/product_regression.json) |
| 真实 AI | 三轮固定本机模型启动均触发资源保护。30 次样本尝试中 10 个唯一模块完成 F01/F02，0 个样本完成 AI F03/F04。[盲测报告](../../demo/TestPilot-Demo-Lab/AI_BLIND_EVALUATION.md) |
| F13 | 15 个原版绿基线，48 个变异，34 杀死、11 存活、3 执行错误，得分 70.83%。[F13 报告](../../demo/TestPilot-Demo-Lab/reports/MUTATION_EVALUATION.md) |
| 发布完整性 | Git 归档中 225 个文件，224 个文件逐一校验成功，另含 SHA-256 清单自身。[清单](../../demo/TestPilot-Demo-Lab/SHA256SUMS.txt) |

测试与取证入口为 `scripts/validate_dataset.py`、`scripts/product_acceptance.py`、`evaluation/evaluator.py` 及 `scripts/generate_catalog.py`。[操作手册](../../demo/TestPilot-Demo-Lab/DEMO_SCENARIO.md)

本地实现提交 `f563c6d`，结果归档 `cb91a19`，计分与跨检出校验 `fb064e0`。

## 仓库全量回归

使用仓库 `hooks/verify.py --scope full`，报表另存本工作包。首次在受限宿主中，回环检查观测到 WinError 10013，Pytest 汇总为 112 通过、6 失败、50 错误，Node 测试通过。使用允许回环连接的权限复跑，编译检查通过，168 项 Pytest 和 3 项 Node 测试全部通过。[首次记录](verify-full.txt) · [复跑记录](verify-full-permitted.txt)
