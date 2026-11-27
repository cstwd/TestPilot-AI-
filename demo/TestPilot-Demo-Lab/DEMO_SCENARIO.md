
# TestPilot Demo Lab 实操手册

## 准备隔离工作区

在 PyCharm 中选用项目的 `.venv`，运行根目录 `main.py`。为本次演示复制一个运行配置，在环境变量中把 `TESTPILOT_DATA_DIR` 指向 `D:\TestPilot AI\.runtime\demo-lab-course`。脚本参数可填 `--port 8018`，浏览器打开 `http://127.0.0.1:8018`。如端口空闲，也可使用默认的 8000。以下命令与该配置等效。

```powershell
$env:TESTPILOT_DATA_DIR = 'D:\TestPilot AI\.runtime\demo-lab-course'
.venv/Scripts/python.exe main.py --port 8018
```

在独立窗口启动正式配置的本机守护，或在已有守护运行时直接检查 `GET /api/model/health`。自定义守护运行目录时，给应用设置相同的 `TESTPILOT_MODEL_RUNTIME`。按 [部署文档](../../docs/phase06/DEPLOYMENT.md) 使用已安装权重及资源保护。健康检查返回 `ready` 后，在智能测试引擎选择本机 Qwen3.8-27B。返回 503 时记录原因，可继续做下面标为模板的可复现演示。

## 推荐演示顺序

1. **F01 导入 GOOD。** 打开项目中心 `/workbench/projects`，新建 `Demo Lab - GOOD`，选择 `D:\TestPilot AI\demo\TestPilot-Demo-Lab\source\good\calculator.py`。核对 v1 和 SHA-256。每次导入一个 UTF-8 `.py`，上限 128 KiB。
2. **F02 静态分析。** 打开代码分析 `/workbench/analysis`，选刚上传的版本，确认两个可选函数 `add`、`quotient`。需要模型语义分析时，在 `/engine` 内使用源码理解功能，或向 `POST /api/engine/files/{id}/understanding` 传 `{"target":"add"}`。
3. **F03 生成。** 在 `/engine` 选 `add` 和本机 Qwen3.8-27B。智能引擎的 `configured` 与 F03 套件 API 的 `ai` 都调用正式 Provider。普通生成工作台 `/workbench/generation` 固定使用 `template`。要获得工作台可读取的 AI 套件，直接向 `POST /api/files/{id}/suites` 提交 `{"target":"add","mode":"ai"}`。
4. **F04 执行。** 套件 API 的生成调用会验证并保存首次运行。打开生成工作台的「查看首次执行记录」，或进入 `/workbench/runs` 选定文件和套件后点击「执行测试」。对应 API 为 `POST /api/suites/{suite_id}/runs`，请求体为 `{"file_id":实际版本ID}`。保留运行 ID、测试节点、退出码、日志和套件摘要。
5. **盲测 BUGGY 与 CHALLENGE。** 在另一个新项目导入 `source/buggy/binary_search.py`，目标为 `locate`。然后导入 `source/challenge/booking_timezones.py`，目标为 `utc_window`。仅提供 `source/` 文件，生成模式显式选 AI。先保存实际运行，再用独立评估核对失败节点。用例通过、错误断言、执行错误和有效缺陷检出分别记录。其余七个盲测样本见 [选样清单](scenarios/bug_hunting.json)。
6. **F05 登记与修复。** 可复现演示使用新项目 `Demo Lab - Regression`。导入 `source/buggy/unit_scaling.py`，在生成工作台为 `metric_kilometers` 显式生成模板套件。首次运行的返回类型断言应失败。进入「缺陷管理」，选择该失败节点并登记。执行结束后，在同一项目上传 `reference/corrected/unit_scaling.py`，文件名保持 `unit_scaling.py`，核对 v2。回到缺陷页选 v2，点击「运行回归」，核对失败节点翻绿、同一套件 ID 和新的运行 ID。
7. **F06 报告。** 从 v1、v2 的运行结果点击「质量报告」，核对通过、失败、错误、覆盖和缺陷关联。下载 JSON。复核接口 `GET /api/runs/{run_id}/report` 及 `GET /api/runs/{run_id}/report/export`。源码覆盖率衡量代码执行范围，业务结论查看合同与回归证据。
8. **F13 变异测试。** 在 `/engine` 返回 GOOD `calculator.py`，为 `add` 选择「仅本地模板」，最大修复次数为 0，执行完并确认原版通过。进入任务的「变异测试」链接 `/mutations?task_id=...`，取消「将存活变异提交本机模型补测」，启动实验并下载 JSON。先看基线，再核对清单内每个变异的状态。全量目标在 [F13 选样](scenarios/mutation_demo.json)，变异清单包含既有产品支持的比较、算术、布尔、返回值、分支和异常算子。

自动验收脚本用真实 `main.py` 回环服务和临时 SQLite，在 Windows 退出时有序关闭子进程。

```powershell
.venv/Scripts/python.exe -X utf8 demo/TestPilot-Demo-Lab/scripts/product_acceptance.py regression
.venv/Scripts/python.exe -X utf8 demo/TestPilot-Demo-Lab/scripts/product_acceptance.py mutation
.venv/Scripts/python.exe -X utf8 demo/TestPilot-Demo-Lab/scripts/product_acceptance.py blind --workflow
.venv/Scripts/python.exe -X utf8 demo/TestPilot-Demo-Lab/evaluation/evaluator.py
```
