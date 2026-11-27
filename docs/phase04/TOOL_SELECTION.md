# F13 生产变异工具选型

**采用 Cosmic Ray 8.9.0 的静态算子接口生成候选，复用 F10 WASI 执行器运行并判读 Pytest。** 两种工具都在 Windows 11 成功安装，两个内部生成器都能产生有效算术变异。Cosmic Ray 另有可独立核验的变异位置、算子与出现序号，以及实际跑通的原生批执行及 JSON 报告。mutmut 3.8.1 的 Windows CLI 在进入测试前即以退出码 1 要求 WSL。[原始对照数据](../../reports/phase04/tools/windows-benchmark.json)

2026-11-27，项目根目录 `D:\TestPilot AI`。责任工作包 WP03（测试与离线评测）、WP04（执行边界），阶段协调陈帅廷，实际操作 Codex 基准子代理。工具安装在独立虚拟环境 `.runtime/phase04-tools`，宿主 Windows 11 build 26200，CPython 3.13.11，Pytest 9.2.0。`pip check` 返回 `No broken requirements found.`。[依赖清单](../../reports/phase04/tools/benchmark-requirements.txt) · [安装核查](../../reports/phase04/tools/dependency-check.txt)

## 输入与结果

基准程序只接受内置的七行可信函数 `charge(n, enabled)` 及两个 Pytest 用例。它包含比较、布尔组合、条件分支、算术、返回常量和异常处理。两个用例分别检查启用时的正常值与无效输入回退值。宿主 Pytest 基线实跑 2 项通过。每个工具、每个并发分片使用独立临时副本。所有分片收尾时逐字核验原始源码。[基准程序](../../eval/phase04/tools_benchmark.py)

| 观察项 | mutmut 3.8.1 | Cosmic Ray 8.9.0 |
| --- | --- | --- |
| 安装与 Windows 11 | pip 成功安装，LibCST 内部接口可导入 | pip 成功安装，原生 CLI 的 init、baseline、exec、dump 均退出 0 |
| 基准上的算子 | 生成 8 项，实测含 `and → or`、`> → >=`、`+ → -`、数值与一元符号替换 | 注册 213 个算子名称，本例默认配置实际枚举 31 次变异，涉及 24 个算子名。含算术、关系、条件加 not、布尔、数值和异常处理器替换 |
| Pytest 集成与性能 | 1 个子进程配置运行 0.469 秒后退出 1，无原生测试吞吐率。生成 8 个内部候选耗时 0.0214 秒 | init 1.958 秒，原生 baseline 2.491 秒，exec 串行运行全部 31 项耗时 28.715 秒。静态探针从已解析节点列出位置并渲染一个算术变异耗时 0.0045 秒 |
| 并行 | `run --max-children 2` 实测 0.498 秒后退出 1，给出同一 WSL 提示 | 本地 distributor 在单 session 串行；基准将全量工作单按原 job ID 分到两个独立 session（16+15），两个真实 CLI 进程并发，耗时 15.931 秒。逐个核对 31 个 ID 与串行结论相同。本机此轮加速约 1.80 倍 |
| 报告可解析性 | `results` 退出 1，未产出原生报告；内部生成接口可取变异前后节点 | `dump` 输出 31 条 JSON Lines，含 job_id、算子、位置、出现序号、Pytest 文本和 diff；24 条工具自报 killed，7 条 survived |
| 隔离兼容性 | 用内部 `create_mutations` 获得单次替换，提取独立源码后，F10 实跑 1 通过、1 断言失败 | 用 `get_operator` 和 `mutate_code` 在内存将 `return n + 2` 改为 `return n - 2`，F10 实跑同样的 1 通过、1 断言失败。原始源码在同一 WASI 中为 2 通过 |

并发时间从创建两个 CLI 进程前开始，含其启动、分片执行及等待，不含准备两个副本的时间。此处测量两个本机 session；官方 HTTP distributor 支持独立 worker，未测远程部署。串并行均为同机单轮实测，静态生成计时的工作量不同，不用于计算工具间速度比。[原生逐项报告](../../reports/phase04/tools/cosmic-dump.ndjson) · [两种工具的真实 WASI 结果](../../reports/phase04/tools/wasi-bridge.json) · [官方并行机制](https://cosmic-ray.readthedocs.io/en/latest/tutorials/distributed/index.html)

## 生产边界

Cosmic Ray 的原生命令执行路径在此版本会把超时和测试调用出错也归为 killed。实测固定的休眠命令在 0.5 秒时限被记为 `killed / timeout`；调用不存在的可信 Pytest 文件同样被记为 `killed`。因此该工具的 24/31 是兼容性基准的原生标签，生产计分由 F13 基于干净基线、F10 有效执行与逐例证据单独计算。[实际诊断](../../reports/phase04/tools/windows-benchmark.json)

生产可用 `cosmic_ray.ast.get_ast`、`ast_nodes` 与已固定版本的受信算子读取纯文本，定位后构造独立的变异文本。基准的 `core/ExceptionReplacer` 会引入名为 `CosmicRayTestingException` 的异常类型；未定义符号引出的错误须留在错误类别。生产对分支、返回及异常处理使用明示的算子策略，并保留完整候选清单及分母。Pytest 运行由无网络、只读挂载且限时限量的 WASI 负责。[Cosmic Ray 接口](https://github.com/sixty-north/cosmic-ray/blob/master/src/cosmic_ray/mutating.py) · [mutmut 平台要求](https://mutmut.readthedocs.io/en/latest/) · [既有隔离设计](../phase03/SANDBOX.md)

## 复验命令

以下命令从项目根目录运行，基准只运行仓库内嵌的可信输入。重跑会刷新 `reports/phase04/tools` 下的当轮数据。

```powershell
.\.venv\Scripts\python.exe -m venv .runtime/phase04-tools
.\.runtime\phase04-tools\Scripts\python.exe -m pip install -r reports/phase04/tools/benchmark-requirements.txt
.\.runtime\phase04-tools\Scripts\python.exe -m pip check
.\.runtime\phase04-tools\Scripts\python.exe eval/phase04/tools_benchmark.py --wasi
```

