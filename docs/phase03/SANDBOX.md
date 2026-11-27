# F10 隔离执行与取证

工作包 WP01/WP04，本阶段负责人陈帅廷。平台将用户源码和生成测试作为 UTF-8 文本分别写入每次任务专属的 `.runtime/job-*/work/subject.py` 和 `test_generated.py`。业务执行只接受源码、测试文本、数值时限和详细模式开关。宿主用当前项目解释器的隔离选项启动固定 worker，代码在独立进程内的 WASI CPython 中导入。工作目录和依赖包只读，来宾内部没有宿主文件系统根、网络能力或启动其他进程的能力。[宿主控制器](../../backend/runner.py) · [能力配置](../../backend/wasi_worker.py)

| 资源 | 实现与行为 |
| --- | --- |
| 运行槽与进程 | 单个服务进程一次接纳一个隔离 worker。Python 来宾运行在该 worker 内。槽位繁忙时返回环境诊断。 |
| 时间与清理 | 来宾默认 15 秒，允许 1–60 秒。包含编译启动的宿主硬时限为 45 秒加来宾时限。超限后结束并等待 worker；正常退出、超时与解析异常均释放运行槽和临时目录。共享的引擎编译缓存位于 `.runtime/wasm-cache`，来宾没有其读写授权。 |
| 内存与句柄 | 限制 WASM 线性内存为 256 MiB、打开文件最多 128 个。这一内存值适用于来宾线性内存，宿主解释器和 Wasmtime 另有启动开销。 |
| 输入与依赖 | 两个只读映射分别包含任务文件和白名单依赖归档。来宾关闭 Pytest 配置插件自动加载，命令和挂载由 worker 固定。宿主模型密钥和环境变量不传入来宾。 |
| 输出与失败记录 | 每路输出上限 256 KiB。触限即取消并标注日志不完整；未完成时详细模式的计数和覆盖率为 null。已捕获的两路内容及 worker 诊断分别保留。 |

## 详细执行接口

`backend.runner.execute(source, test_code, detailed=True, timeout_s=15)` 启用 Pytest 断言重写、逐例异常证据和 Coverage.py 分支采集。PHASE-02 的调用继续使用默认参数，保留原来宾参数、用例记录结构和日志格式。

- `status`、`exit_code`、`duration_ms`、`cases`、`passed/failed/errors/skipped` 来自执行状态、宿主计时及 Pytest 回调。`result_complete` 表示已收到并解析完成记录。超时、输出超限和缺失记录均可见；退出码仅在取得来宾退出状态时填入。
- `stdout` 和 `stderr` 是测量到的输出流；成功解析时从 stdout 分出末尾的 JSON 协议消息。`diagnostic` 保存宿主执行与协议错误，`log` 供人工查看。Pytest 启用 `-s`，允许查看被测代码自身的打印。
- `covered_lines/total_lines/coverage_pct` 仅度量 `subject.py`。`covered_branches/total_branches/branch_pct` 使用 Coverage.py 公共接口 `branch_stats` 汇总已走过和可走的分支出口。没有可用分母时百分比为 null；取得测量且文件无分支时计数为 0/0。
- `failures` 保留 Pytest 的节点 ID、阶段、异常类型、异常消息、比较断言的实际差异和回溯位置。优先记录测试与被测文件帧，行号从 1 开始。收集期的导入与语法错误还原 Pytest 包装的原始异常。缺少可取得的比较差异时该字段可为空。每条最多保留末尾 8 帧，消息最多 1,200 字符，结构化详情共最多 32 KiB；超预算详情数量进入 `failure_details_omitted`。完整用例状态仍由 Pytest 个案列表提供。

运行结果与测覆盖信息均在同一 Python 来宾采集，可用于功能 QA 和复现。可以控制来宾解释器的恶意代码可能干扰该来宾中的测量，详情不构成独立防篡改证明。沙箱按最小能力执行，用户原始源码保存在不可变文件修订中，worker 只收到该修订的副本。[来宾记录器](../../backend/guest_pytest.py) · [本阶段测量用例](../../tests/test_f10.py) · [权限与超时回归](../../tests/test_runner.py)
