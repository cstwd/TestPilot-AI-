# TP-PHASE-05 Qwen3.8-27B 本地模型验收

项目 TestPilot AI。责任工作包 WP03、WP04，阶段负责人陈帅廷，实验操作 Codex。基线 `307d4bd`，实验分支 `experiment/tp-phase-05`。
目标模型为本机已有的 Qwen3.8-27B UD-IQ3_XXS GGUF。CUDA 在首请求遇到 PTX JIT 资源分配失败，改用 RTX 5080 Laptop Vulkan 后完成连续推理以及 F09、F13 全流程。推理经本机回环接口完成，API 费用为零。

| 维度 | 结果 |
| --- | --- |
| 模型源码理解 | 严格评分 56/70，80.00%。十组参数值在人工复核中正确，但结构与冻结要求不符，仍按规则计分。 |
| 测试质量 | Qwen3.8 初始 88.89%，模板 69.23%，补测后 89.74%。按所有预登记位置计算。 |
| 推理性能 | 进程就绪 35.250 秒，连续有效响应 10/10。短请求后九轮均值 19.21 token/s。 |

初始目标 ≥55% 达到。补测目标 ≥70% 达到。候选原版通过率 100.00%（1/1），达到阈值的样本只有一条。全部 4 次反馈请求中有 1 条转化为有效补测。
Qwen3.8 初始分数比模板高 19.66 个百分点。反馈比初始高 0.85 个百分点。
结论适用于这十个小型项目、三个采样种子及固定算子配置。多文件加载是独立评测适配层。整机物理内存采样在模型加载和执行期间接近上限。性能记录采用文本推理模式。
F13 发现身份比较变异的最小文本差分可能错过算子位置，导致整个清单拒绝。实验分支仅对经 Cosmic Ray 精确复验的 `is → is not` 插入做定位修正。既有 bonus 清单逐项与 PHASE-04 一致。

- [环境与权重审计](T01_ENVIRONMENT.md) · [连续推理及内存数据](T01_PERFORMANCE.md)
- [源码理解报告](T02_SOURCE_UNDERSTANDING.md) · [F09 生成报告](T03_TEST_GENERATION.md)
- [四组对照报告](T04_COMPARISON.md) · [得分图](mutation-score.png) · [反馈报告](T05_MUTATION_FEEDBACK.md)
- [完整原始数据](raw) · [逐次 CSV](campaigns.csv) · [可复算汇总](summary.json) · [冻结协议](../../eval/phase05/PROTOCOL.md)
- [四组分数复算](raw/independent-recalculation.txt) · [变异回归实测](raw/manifest-tests.txt) · [代码与实验脚本](../../eval/phase05)

项目组长人工签收待办。
