# F13 变异得分报告

同一个 `bonus` 函数生成了涵盖六类算子的 9 个变异。F09 本地 AI 初始套件在补测前杀死 3 个，补测后杀死 4 个。F09 模板初始套件在补测前杀死 4 个，补测后杀死 5 个。两场实验新杀死的都是 L9 抑制异常变异。两场各自重跑完整清单，原版 SHA-256 均为 `6e35907cec8eac40250fb30175de48a12fef3aed25a9ca6d4afa0427c02f2bf2`。[样例源码](../../eval/phase04/bonus.py) · [算子和适用范围](MUTATION_OPERATORS.md)

## 完整分母

得分为 `100 × Killed / 清单总数`，显示两位小数。仅在原版基线有效时计分。每个变异在每次计分中恰有一个状态。等价候选另外标记，仍计入分母。下表的“原版通过”是对原始源码实际运行的 Pytest 节点数。[计分实现](../../backend/mutation_results.py)

| 初始套件 | 阶段 | 原版通过 | Killed | Survived | 执行错误 | 超时 | 取消 | 未运行 | 等价候选 | 分母 | 得分 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 本地 AI | 补测前 | 1 | 3 | 5 | 1 | 0 | 0 | 0 | 0 | 9 | 33.33% |
| 本地 AI | 补测后 | 2 | 4 | 4 | 1 | 0 | 0 | 0 | 0 | 9 | 44.44% |
| 模板 | 补测前 | 4 | 4 | 3 | 2 | 0 | 0 | 0 | 0 | 9 | 44.44% |
| 模板 | 补测后 | 5 | 5 | 2 | 2 | 0 | 0 | 0 | 0 | 9 | 55.56% |

两场的精确增量均为 1/9，约 11.11 个百分点。模板实验各端点独立四舍五入，显示为 44.44% 和 55.56%。[AI 初始实验复算](verified-ai-initial.txt) · [模板初始实验复算](verified-template-initial.txt)

加固后另起的 AI 初始会话 `6151a7c2-6c8c-4731-9df8-b9db2762eed1` 再次得到 3/9 → 4/9，`impact` 逐项对应原先 5 个存活变异，其中仅 L9 由新增测试检出，另外 4 个仍然存活。[复验原始事件](ai-hardened-campaign.json) · [独立复算](verified-ai-hardened.txt)

## 每个位置的执行结果

每格的“杀死”“存活”“错误”分别对应归档的 `killed`、`survived`、`execution_error`。最后一列列出所有实际杀死节点的函数名，完整 Pytest nodeid 均以 `test_generated.py::` 开头。

| 源码位置与单处变更 | AI 前 | AI 后 | 模板前 | 模板后 | 实际杀死节点 |
| --- | --- | --- | --- | --- | --- |
| L8:8 · 对 `n < 0` 取反 | 错误 | 错误 | 错误 | 错误 | — |
| L8:10 · `<` → `<=` | 存活 | 存活 | 错误 | 错误 | — |
| L9:9 · `raise ValueError("negative")` → `pass` | 存活 | 杀死 | 存活 | 杀死 | 两场补测后的 `test_mutation_0473d9a7eced8496` |
| L10:8 · 对 `enabled and n >= 2` 取反 | 杀死 | 杀死 | 杀死 | 杀死 | AI 为 `test_bonus`，模板为 `test_example_1` |
| L10:16 · `and` → `or` | 存活 | 存活 | 存活 | 存活 | — |
| L10:22 · `>=` → `>` | 存活 | 存活 | 存活 | 存活 | — |
| L11:9 · `return n + 1` → `return None` | 杀死 | 杀死 | 杀死 | 杀死 | AI 为 `test_bonus`，模板为 `test_example_1` 和 `test_normal_return_contract` |
| L11:18 · `+` → `-` | 杀死 | 杀死 | 杀死 | 杀死 | AI 为 `test_bonus`，模板为 `test_example_1` |
| L12:5 · `return n` → `return None` | 存活 | 存活 | 杀死 | 杀死 | 模板为 `test_boundary_return_contract` |

L8 的错误记录中，变异后的函数向原本正常的调用抛出 `ValueError`，Pytest 退出码为 1。判定器要求完整的测试侧断言证据，故这两处分别按各次实测记录为错误或存活，保留在分母中。L9 补测则使用 `pytest.raises(ValueError)`，原版通过；删除异常的变异版触发 `DID NOT RAISE ValueError`，形成可核查的杀死节点。[AI 初始完整实验](ai-initial-final-campaign.json) · [模板初始完整实验](local-ai-experiment.json)

## 复核与追溯

两份完整实验各保留 23 条事件，包括原始基线、两轮各 9 个变异执行、模型反馈、候选原版校验、筛选以及采纳后的基线。复核程序从源码重建全部变异，校验副本和测试的 SHA-256、UUID、原版是否通过、杀死节点、退出码与各状态计数。[独立复核程序](../../eval/phase04/check_experiment.py)

在仓库根目录运行以下命令，两次均以退出码 0 结束。

```powershell
.\.venv\Scripts\python.exe eval/phase04/check_experiment.py reports/phase04/ai-initial-final-task.json reports/phase04/ai-initial-final-campaign.json eval/phase04/bonus.py
.\.venv\Scripts\python.exe eval/phase04/check_experiment.py reports/phase04/local-ai-task.json reports/phase04/local-ai-experiment.json eval/phase04/bonus.py
```

工作包 WP03/WP04，阶段负责人陈帅廷，执行与复核记录由 Codex 生成。计分实现提交 `6de6844`，实验流程提交 `f6daaa1`。待办为项目负责人签收。两场中尚存活及执行错误的位置保留在各自的最终报告中。[反馈与未采纳候选](AI_FEEDBACK.md)
