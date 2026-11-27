# F13 变异算子验收

实现提交 `5b757b9`。选型提交 `b784715`。工作包 WP03/WP04，阶段负责人陈帅廷，实际操作 Codex。样例是签名为 `bonus(n: int, enabled: bool = True) -> int` 的真实 Python 文件。源码规定负数抛出 ValueError，启用奖励且 n ≥ 2 时返回 n + 1，其余返回 n。[样例源码](../../eval/phase04/bonus.py)

| 家族 | 在该样例中生成的一级变异 | 数量 |
| --- | --- | ---: |
| 比较 | L8 的 `<` 改为 `<=`，L10 的 `>=` 改为 `>` | 2 |
| 算术 | L11 的 `+` 改为 `-` | 1 |
| 条件 | 分别对 L8、L10 完整条件取反 | 2 |
| 布尔 | L10 的 `and` 改为 `or` | 1 |
| 返回值 | 分别将 L11、L12 的返回值替换为 None | 2 |
| 异常 | 将 L9 的显式 `raise ValueError(...)` 替换为 `pass` | 1 |

每个样例位置均实际生成和重放，九份改动分别经过 Python 编译。相同源码、目标及算子配置生成相同的 UUID 和副本摘要。范围与重放测试还检查了中文列偏移、CRLF、跨行链式比较、源文件摘要变化、等价候选识别及超出清单容量时整体拒绝。当前配置支持顶层同步函数，清单最多 128 项。算子配置表示可测范围，新增算子需要新配置版本。[算子实现](../../backend/mutation_generator.py) · [逐项生成输出](operators.txt)

从 `D:\TestPilot AI` 运行下列命令，生成器独测 4 项通过。执行器判定独测 10 项通过，其中实际在 WASI 运行预期异常被抑制、普通断言失败、异常退出、语法错误、超时、取消等路径。每个位置的实际前后结论另存于[得分报告](MUTATION_SCORE.md)。待办为人工签收与后续算子族扩展。

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_mutation_generator.py -q -s
.\.venv\Scripts\python.exe -m pytest tests/test_mutation_results.py -q -s
```

[执行判定原始输出](results-test.txt) · [执行判定及分母实现](../../backend/mutation_results.py)
