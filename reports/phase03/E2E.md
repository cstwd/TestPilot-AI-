# PHASE-03 端到端实测与反馈修正案例

**7 项端到端测试通过，耗时 55.20 秒。** 实际通过 HTTP 向根入口启动的 FastAPI 服务导入七份源码，生成八个套件版本并在 WASI 中运行八次。四个带预置缺陷的项目均有违反明确 doctest 契约的失败证据。附加项目首跑发现生成测试的预期有误，修正后原节点通过。[测试原始输出](E2E.txt) · [入口与断言](../../tests/test_phase03_e2e.py)

| 源函数 | 生成模式 | 通过 / 失败 / 错误 / 跳过，按执行顺序 | 事件数 | 原始导出 |
| --- | --- | --- | ---: | --- |
| [quicksort](../../eval/phase03/quicksort/subject.py) | template | 6 / 0 / 0 / 0 | 7 | [任务 1634e1f8](cases/quicksort.json) |
| [magnitude](../../eval/phase03/negative/subject.py) | template | 5 / 1 / 0 / 1 | 7 | [任务 49029392](cases/negative.json) |
| [first_or_default](../../eval/phase03/empty/subject.py) | template | 3 / 2 / 0 / 0 | 7 | [任务 5cbfbbcd](cases/empty.json) |
| [valid_index](../../eval/phase03/boundary/subject.py) | template | 6 / 1 / 0 / 0 | 7 | [任务 aacedec3](cases/boundary.json) |
| [parse_count](../../eval/phase03/exception/subject.py) | template | 4 / 1 / 0 / 0 | 7 | [任务 e90d1048](cases/exception.json) |
| [classify_temperature](../../eval/phase03/branches/subject.py) | template | 7 / 0 / 0 / 1 | 7 | [任务 ba4e3ad7](cases/branches.json) |
| [reciprocal_units](../../eval/phase03/repair/subject.py) | template → rules | 4 / 1 / 0 / 1 → 5 / 0 / 0 / 1 | 12 | [任务 f2766af9](cases/repair.json) |

验收请求显式指定 `generation_mode=template`。七次首跑的生成方式均为本地模板，第八次是按文档契约做的规则修正。表中的“通过”指生成用例的实际 Pytest 结果。各项目使用独立的临时 SQLite 数据库，任务 ID 与事件 ID 使用 UUID；完整导出包含初次及修正后测试源码、输出流、覆盖分母、逐个用例和任务历史。跳过的属性测试可用其节点 ID `test_generated.py::test_property_return_contract` 在相应导出的 stdout 中核查。[覆盖率明细](COVERAGE.md)

## 发现的程序缺陷

下表的测试节点均属于 `test_generated.py`。报告将断言失败时推定的函数入口与真实异常回溯帧分别标记。四个预置缺陷均保留首跑失败记录，未进入自动修正。

| 样例及失败节点 | 文档契约 | 执行证据与定位 |
| --- | --- | --- |
| [负数处理](cases/negative.json) · `test_example_3` | `magnitude(-8) == 8` | 断言比较显示 `-8 == 8`，测试第 11 行。缺陷定位精度为函数入口 `subject.py:1`。 |
| [空输入](cases/empty.json) · `test_example_2` | `first_or_default([], 7) == 7` | `subject.py:9` 执行 `return values[0]` 抛出 IndexError。另一节点 `test_boundary_return_contract` 也抛出 IndexError，但它的实际输入缺少独立契约，因此保留 `undetermined` 归属。 |
| [上界](cases/boundary.json) · `test_example_3` | `valid_index(3, 3) == False` | 实测返回 True，测试第 11 行断言失败。缺陷定位精度为函数入口 `subject.py:1`。 |
| [异常处理](cases/exception.json) · `test_example_2` | `parse_count("unknown")` 应抛出 ValueError | Pytest 在测试第 8 行报告 `DID NOT RAISE ValueError`，记录异常类型为 Failed。缺陷定位精度为函数入口 `subject.py:1`。 |

## 修正错误的生成测试

`reciprocal_units(0)` 的 docstring 明确要求抛出 ValueError。首次模板生成的 `test_boundary_return_contract` 在测试第 15 行期望整数返回值，实际调用按文档抛出 `ValueError: zero has no reciprocal`。F11 将该节点归为 `test_error`。F12 的第 1 次修正为这一调用生成 `pytest.raises(ValueError)`，保留其他节点并重新执行。同名用例从失败变为通过。两次运行的用户源文件 SHA-256 一致。[源码](../../eval/phase03/repair/subject.py) · [包含原始与修正源码的完整事件链](cases/repair.json)

| 运行 | TestExecution ID | 生成的测试 SHA-256 |
| --- | --- | --- |
| 首次 | `29a994ff-bb8b-44d6-b86b-64efa1937bf3` | `6157dd2abfe707f3618c0edb42cbdeb98e79a6d45f5cfa8459cb828833c1b914` |
| 修正后 | `3622ee07-fe33-45fd-af61-0c12a4a0b7c7` | `d43dc8b67d8b1699070b516bc5b77ff586baa85432cc69bdf36180cf6c4592ea` |

## 复验

从项目根目录运行以下命令，日志会逐项打印用例计数、行及分支的分子与分母、初次归因。归档的七份 JSON 对应上表任务 ID；新的验收运行会创建新的临时数据库和任务 UUID。

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_phase03_e2e.py -q -s
```

本次对七份 JSON 的 54 条事件核对了事件 UUID、UTC 时间戳、同任务前序链接、源文件摘要、生成代码摘要、初末执行 ID、覆盖记录绑定的运行 ID、逐例计数和覆盖率算术。跨运行复核可从每份文件的 `TestReport.initial_execution_id` 和 `final_execution_id` 开始，再沿 `generated_test_id` 查阅对应测试源码。责任人为陈帅廷。实测与独立记录核对由 Codex 执行。
