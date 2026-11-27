
# Demo Lab 数据集验收

WP03-DEMO-LAB-001 · 2026-11-27 · 操作者 Codex

| 验收项 | 实测结果 |
| --- | --- |
| 冻结源码 | 100 个独立模块，GOOD 25、BUGGY 50、CHALLENGE 25，六个领域各有三种类型 |
| 独立修复版 | 75 个，接口与对应待测文件一致 |
| 文件核对 | 100 个唯一文件名和 SHA-256，175 份源码均可用 Python 3.10 的语法规则解析，宿主编译通过 |
| 可运行性 | 175 份原版和修复版分别在 WASI 来宾内加载并运行，各源文件至少有两个带 Docstring 的顶层同步函数 |
| 合同场景 | 400 个，含边界 163、异常 53、组合 68、特殊值 20、常规 96 |
| GOOD 源码 | 100 项通过 |
| BUGGY 源码 | 100 项通过，100 项预期失败 |
| CHALLENGE 源码 | 50 项通过，50 项预期失败 |
| 隐藏修复版 | 300 项通过 |
| 缺陷见证 | 150 项通过，逐个验证精确的错误输出或异常，并在其余缺陷仍存在时验证定点修复 |
| 总计 | 850 次 Pytest 判定，700 通过、150 预期失败，0 意外结果、0 跳过 |
| 评分回归 | 6 项 Python 层回归通过，覆盖无观测值、不可达断言、目标重绑定和自比较 |

验证读取冻结的 [ground_truth.json](../reference/ground_truth.json)，用实际测试节点匹配每个案例。已知缺陷的合同测试保留 Pytest 原始失败。见证逐项区分返回值、预期异常和实际异常。独立验证中的检测率描述冻结合同对已知缺陷的复现，AI 检出率以单独盲测评估为准。首轮发现两个控制场景本身触发缺陷、一个错误值标注错误，已修订并全量复验。

环境为 Windows 11，项目宿主 Python 3.13.11，WASI 执行器调用仓库固定 Pytest。每个用例单独加载模块副本。验证输入跨空数据、相等边界、时间边界、无效类型、Unicode 和异常路径，所有源模块保持单文件导入规模。当前每个模块四个手写合同场景，真实生产模块和跨文件依赖超出首版覆盖。

```powershell
.venv/Scripts/python.exe -X utf8 demo/TestPilot-Demo-Lab/scripts/validate_dataset.py
.venv/Scripts/python.exe -X utf8 -m pytest -q demo/TestPilot-Demo-Lab/tests/regression/test_evaluator.py
```

逐批 Pytest 退出码、节点结果、时间、日志和源码版本见 [dataset_validation.json](dataset_validation.json)。
