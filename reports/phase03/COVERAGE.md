# PHASE-03 被测项目行覆盖与分支覆盖

本次在 WASI CPython 中用 Coverage.py 对七个项目分别测量 `subject.py`，每个文件按其最终运行计入一次。合计覆盖 **34/35（97.14%） 行** 和 **15/16（93.75%） 个分支出口**。源码测量与生成模式、Pytest 执行结果都可通过同一份任务导出复查。[端到端原始输出](E2E.txt) · [测量实现](../../backend/guest_pytest.py)

| 被测函数 / 任务证据 | 最终 TestExecution ID | 已覆盖行 / 可执行行 | 已走分支出口 / 所有出口 |
| --- | --- | ---: | ---: |
| [quicksort](cases/quicksort.json) | `c26b4006-f6df-45bc-8de0-d88037a64d27` | 11/12（91.67%） | 7/8（87.50%） |
| [magnitude](cases/negative.json) | `9978181e-19bc-4324-87b8-6bed86ede18c` | 2/2（100.00%） | 0/0（无适用分支） |
| [first_or_default](cases/empty.json) | `4bf530c5-a69f-4ece-b828-96edd614a9f7` | 2/2（100.00%） | 0/0（无适用分支） |
| [valid_index](cases/boundary.json) | `9c3d0d85-bc7f-42c7-92cc-04c83c1b3065` | 2/2（100.00%） | 0/0（无适用分支） |
| [parse_count](cases/exception.json) | `38f6be11-5b36-45b8-b503-63923e7dc49a` | 5/5（100.00%） | 0/0（无适用分支） |
| [classify_temperature](cases/branches.json) | `17ded197-c26d-4a6c-9e35-ab1ace217147` | 8/8（100.00%） | 6/6（100.00%） |
| [reciprocal_units](cases/repair.json) | `3622ee07-fe33-45fd-af61-0c12a4a0b7c7` | 4/4（100.00%） | 2/2（100.00%） |

规定的六个样例合计为 30/31 行、13/14 个分支出口。附加的反馈修正样例首次执行和修正重跑均测得 4/4 行、2/2 个分支出口。修正仅更新测试文件；两次生成的 Pytest 断言不同。快速排序样本尚有一条可执行行和一个分支出口未覆盖。多分支温度分类的六个出口均已执行。[反馈修正样例](cases/repair.json) · [多分支样例](cases/branches.json)

行数由 Coverage.py 的 `analysis2` 提供，分支分子、分母分别累加 `branch_stats` 返回的 taken exits 和 total exits。四个样本测得分支分母为零，对应百分比在 JSON 中为 null。报告总百分比以合计分子除以合计分母计算。四个预置缺陷各自文件行覆盖率均为 100%，其行为错误通过输入输出和异常契约检出。[F10 计量与限制](../../docs/phase03/SANDBOX.md) · [缺陷证据](E2E.md)

## 平台主测试进程

全套 89 项回归另用 `coverage run --branch --source=backend,main` 测量宿主测试进程。该进程覆盖 1,222/1,721 行（71.01%）和 363/558 个分支出口（65.05%）。通过 HTTP 或浏览器测试另行启动的服务、worker 和 WASI 来宾不向这个覆盖数据库合并数据。各样例的来宾测量见上表。[平台覆盖 JSON](platform-coverage.json) · [完整回归输出](full-suite.txt)
