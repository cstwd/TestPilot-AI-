# TP-PHASE-06 统一 27B 迁移验收

生产状态 **READY_WITH_LIMITATIONS**。提交位于 `integration/tp-phase-06`。项目负责人陈帅廷，责任工作包 WP01/WP03/WP04，实际操作者 Codex。
统一 Provider 使用本机 Qwen3.8-27B UD-IQ3_XXS。Ollama 标签、清单摘要、权重摘要、发布修订、Vulkan 和实际输出均进入身份判定。API 费用为零。
集成工作树基于 `7c796e7`，包含 PHASE-04 归档 `307d4bd`。历史 PHASE-05 原始证据由 `experiment/tp-phase-05` 的 `8923f2c` 引用。
[迁移前审计](../../docs/phase06/AUDIT.md) · [运行配置与迁移清单](../../docs/phase06/DEPLOYMENT.md) · [旧模型扫描证据](raw/entrypoint-audit.txt)

| 验收 | 实测结果 |
| --- | --- |
| 实际 F01–F04、F09 及 F13 | 4/9 → 7/9，保留实际 SQLite、HTTP 和 WASI 结果。 |
| 协议与回归 | 148 项，失败 0。覆盖结构缺失、异常 JSON、空消息、超时、请求队列及冻结参数数组。 |
| 源码理解 | 67/70。参数格式 10/10，历史为 0/10。 |
| 质量对照 | 27B 初始 93/117，反馈后 93/117。 |
| 资源与恢复 | 稳定、压力及真实启停结果详见性能报告。恢复检查 通过。 |

阶段实现提交 `98adf18`，Windows 状态读重试及复验流程提交 `0ddc083`。量化模型按生产 4K 配置验证。更大上下文和长期运行均有独立记录。固定质量回归仍有五个生成尝试被拒，发布状态受影响。验收服务在测试完成后关闭。本机统一模型部署按守护步骤启动。
[真实端到端报告](E2E.md) · [完整回归](raw/full-regression.txt) · [性能与内存报告](PERFORMANCE.md) · [变异对比](MUTATIONS.md) · [原始证据](raw)
