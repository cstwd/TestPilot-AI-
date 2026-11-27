# TP-COURSE-REMEDIATION-001 · 现场演示复验

**模板路径 PASS，现场真实 27B 路径 PARTIAL。** WP01、WP03、WP04 负责，Codex 执行。本机实测采用独立工作树 `64da56c`、已存在的 Ollama 和固定 GGUF、专用回环端口及临时数据库。Windows 11、Python 3.13.11、RTX 5080 Laptop 设备。模型启动复用 `eval.phase06.serve`，默认 4096 上下文、Vulkan、单槽、q4_0 KV、关闭 prompt RAM cache 和 context checkpoints，[历史部署](../docs/phase06/DEPLOYMENT.md)。

| 观察 | 真实结果 |
|---|---|
| 历史保护 | Demo Lab 三轮分别剩 1.87、1.66、1.74 GiB 物理内存，均低于 2 GiB。历史 PHASE-06 曾健康 200 并完成 F03/F13；回环停止后的 503 已归档。 |
| 当前启动前 | 物理 10.50 GiB、Commit 14.37 GiB、显存 15,984 MiB。校验固定模型身份后，守卫状态 serving、Vulkan 为 true。 |
| 离线拒绝 | 不启动模型时，探针 503，AI 套件请求 422，F01 导入和 F02 分析可用。 |
| 当前真实加载 | `calculator.add` 单样本仍触发 `resource_guard`。触发点物理只余 0.685 GiB，Commit 4.35 GiB、显存 15,970 MiB。健康 503，F03 AI 422，F04 AI 无执行。守卫终止专用 Ollama，监控退出 0，运行脚本按现场 AI 未通过返回 1。 |
| 恢复 | 本次实例退出后，物理余量回到 10.63 GiB、Commit 14.49 GiB。12 项 Provider 替身测试通过，包括超时恢复、PID/端口变更复查和 GPU 未就绪拒绝。当前成功模型加载仍欠证据。 |
| 模板 F01–F06 | `unit_scaling.metric_kilometers` 的缺陷版 1 通过、2 失败。沿用同一套件从 run 1 到 run 2，修复合约 3 通过、1 跳过，缺陷 resolved，行覆盖 75%。F06 API 和导出一致。 |
| 模板 F13 | `calculator.add` 走绿色基线，真实 WASI 运行 2 个变异，杀死 2/2，已完成并导出。模型反馈关闭，短路径可现场演示。 |

同样负载下当前恢复余量不足以覆盖这次观测到的冷加载瞬时占用并保留下限。无需在资源未变化时重复加载。现场展示时提前验证演示机的固定身份及资源，只在健康 200 后进入 AI F03。课程展示可沿用已验证的模板版本回归和 F13，历史真实 AI 回执按其基线说明。资源阈值及产品代码保持原值。

[实际执行脚本](TP-COURSE-REMEDIATION-001/run-controlled-demo.ps1) · [资源、状态和退出码](TP-COURSE-REMEDIATION-001/demo-controls.json) · [实际主机日志](TP-COURSE-REMEDIATION-001/demo-execution.json) · [本轮 AI 拒绝](TP-COURSE-REMEDIATION-001/demo-model-live.json) · [模板回归](TP-COURSE-REMEDIATION-001/demo-template-regression.json) · [模板 F13](TP-COURSE-REMEDIATION-001/demo-template-mutation.json) · [Provider 恢复测试](TP-COURSE-REMEDIATION-001/demo-provider-recovery.txt) · [历史恢复](phase06/raw/recovery.json)
