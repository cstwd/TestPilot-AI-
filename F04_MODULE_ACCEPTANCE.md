# F04 受限 Pytest 执行 · 模块验收

责任工作包：WP03 赵君豪、WP04 马雪朋、WP01 陈帅廷。实际实现与测试为 Codex，独立复核为 Codex Reviewer。实现提交 `d988ecc`，可从项目根目录用 `git show --stat d988ecc` 核对。

**通过。** API 只接受套件与文件版本 ID，同项目同名文件可复用原套件。独立宿主 worker 以固定参数启动 WASI 版 CPython 和 Pytest。每次运行创建临时目录，只读映射源码、测试和所需依赖；禁用网络及进程创建。SQLite 保存运行 ID、源码与套件引用、退出码、个案、日志、耗时和 Coverage.py 行数。[运行服务](backend/runs.py) · [执行器](backend/runner.py) · [WASI 配置](backend/wasi_worker.py) · [来宾 Pytest 插件](backend/guest_pytest.py)

**限制与待办。** 默认来宾 15 秒、宿主启动及执行共 60 秒、256 MiB 线性内存、最多 128 个打开文件、单服务同时一个业务任务。每个输出流限额 256 KiB；触限取消，标记日志不完整并判无效。首次编译需时间和本机缓存。受支持输入是单文件、标准库及已随来宾提供的依赖；无法导入时记录错误。来宾中的用例与覆盖率来自同一 Python 解释器，不能作为恶意被测程序的独立防篡改证明。

## 实际测试

- `.venv/Scripts/python -m pytest tests/test_f04.py tests/test_runner.py -q` → `7 passed in 53.90s`。覆盖真实运行、错误文件拒绝、读写能力、内存、断网、子进程、超时清理、输出超限、收集错误、全部跳过。[执行输出](reports/phase02/F04.txt)
- 单独运行 `.venv/Scripts/python -m pytest tests/test_runner.py -q -s` → `5 passed in 45.12s`。创建网络套接字和来宾进程时均被拒绝；300 MiB 分配失败；含预置失败的样例准确报告 Coverage.py 3/4 行。[详细日志](reports/phase02/F04-runner-test.txt)
- `.venv/Scripts/python -m pytest tests/ui_workbench.py -q -k f04` → `1 passed, 3 deselected in 11.42s`。通过浏览器触发并读取实际运行记录。Reviewer 独立复验业务测试 `2 passed in 9.14s`。
