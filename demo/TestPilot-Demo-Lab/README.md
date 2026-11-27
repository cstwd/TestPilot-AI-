
# TestPilot Demo Lab

WP03-DEMO-LAB-001 是 TestPilot AI 的独立 Python 演示与验收数据集。首版包含 25 个 GOOD、50 个 BUGGY、25 个 CHALLENGE，覆盖六个领域。100 个文件均可单独导入，接口采用 Python 3.10+ 语法。产品和独立验证沿用仓库配置的 Python 3.13 与 WASI Pytest。

| 目录 | 用途 |
| --- | --- |
| [source](source/) | F01 的上传入口，每次只选择一个文件 |
| [scenarios](scenarios/) | 公开索引和演示选样，仅含路径、目标、散列与用例计数 |
| [reference](reference/) | 独立评分使用的修复版、缺陷索引、合同及触发值 |
| [authoring](authoring/) | 含答案的模块定义和扩展入口，按领域维护 |
| [tests](tests/) | 独立验证的 Pytest 源码，通过仓库 WASI 运行器执行 |
| [evaluation](evaluation/) | F03/F04 捕获完成后的独立评分 |
| [reports](reports/) | 版本化证据、原始观测与报告 |

人员模块只使用合成数据做名册、状态展示和业务规则。数据和订单模块使用字符串、内存结构和整数金额。

## 复验

从项目根目录运行以下命令。只生成目录索引时，使用同一脚本并省略参数。

```powershell
.venv/Scripts/python.exe -X utf8 demo/TestPilot-Demo-Lab/scripts/generate_catalog.py --check
.venv/Scripts/python.exe -X utf8 demo/TestPilot-Demo-Lab/scripts/validate_dataset.py
.venv/Scripts/python.exe -X utf8 demo/TestPilot-Demo-Lab/scripts/product_acceptance.py mutation
.venv/Scripts/python.exe -X utf8 demo/TestPilot-Demo-Lab/scripts/product_acceptance.py blind --workflow
.venv/Scripts/python.exe -X utf8 demo/TestPilot-Demo-Lab/evaluation/evaluator.py
```

先完成数据验证与 F13，再启动受保护的模型执行盲测。重复运行会更新对应 JSON 证据。验收发行目录的散列检查应在重跑前完成。模型与隔离数据库的启动方法见 [演示手册](DEMO_SCENARIO.md)。

## 扩展

在 `authoring/` 对应领域登记新模块、接口合同、确定性输入和预期结果。缺陷案例同时登记可观测错误结果和唯一的源文本改动。修改案例配额时同步更新构建器与独立验证器的发行合同。运行 `scripts/build_dataset.py` 生成冻结源码与索引，再执行全量验证。归档证据后运行 `scripts/generate_catalog.py --freeze`。单个缺陷通过完整源文件、唯一修复版本和精确异常或输出逐项核实。历史版本的报告可用 Git 修订和发布清单复核。
