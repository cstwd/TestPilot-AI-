# F10 · Sandbox Execution Engine

实测通过。工程负责人陈帅廷，实际实现和测试由 Codex 执行器子代理完成，Codex 主代理复核。实现提交 `d551a2d`。旧调用默认使用原有输出格式，PHASE-03 显式选择详细采集。

[受限执行器](backend/runner.py) 将源码与测试文件写入每次任务独享的临时目录，独立宿主 worker 在受限 WASI 中执行固定的 Pytest 命令。详细模式的来宾使用 Pytest 的实际异常对象和 Coverage.py 公共 API，保存标准输出、标准错误、退出码、行和分支覆盖、每个异常的测试阶段和 traceback。超时或输出截断的计数及覆盖率缺失时记录 null。执行环境和证据边界见[安全设计说明](docs/phase03/SANDBOX.md)。

| 项目根目录命令 | 实测结果 |
| --- | --- |
| `.venv/Scripts/python.exe -m pytest tests/test_f10.py -q -s` | 3 passed in 18.95s。测得行覆盖 3/4、分支覆盖 1/2；断言差异、源码第 2 行 TypeError、收集时 ImportError 及真实截止超时均有验证。[详细输出](reports/phase03/F10.txt) |
| `.venv/Scripts/python.exe -m pytest tests/test_runner.py -q` | 旧执行器回归 5 passed in 32.62s，覆盖网络、进程、内存、文件、输出及清理。[兼容性输出](reports/phase03/F10-compat.txt) |

被测 Python 仅在来宾进程中运行。采集依赖来宾内的 Pytest 和 Coverage 测量，解释和适用范围见设计说明。
