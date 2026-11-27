# F13 本地 AI 补测验收

在两场完成的实验中，本机模型都提出了 `bonus(-1, True)` 应抛出 `ValueError` 的补测。该测试在原程序上通过，在移除 L9 异常的副本上失败。重新执行全部 9 个变异后，AI 初始套件从 3/9 提高到 4/9，模板初始套件从 4/9 提高到 5/9。模型还给出了错误的预期值，均保留了原版运行证据和筛选结果。[全部位置与杀死节点](MUTATION_SCORE.md)

## 初始测试和模型身份

| 项目 | 本地 AI 生成初始测试 | 本地模板生成初始测试 |
| --- | --- | --- |
| F09 任务 | `1d4cabe3-74dc-437e-96a8-3656aad75cd6` | `eaa51ec8-3c78-4875-abb3-54b9493490eb` |
| F13 会话 | `27ac7d81-cc78-4ce5-9759-49d4db310213` | `77cca17a-f680-404d-8c92-808487ac95fb` |
| 起始套件 | 1 个测试，断言 `bonus(3) == 4` | 4 个测试，覆盖文档例、常规及边界返回类型、非法关键字 |
| 输入反馈的位置 | 5 个实际存活变异 | 3 个实际存活变异 |
| 实际模型请求 / 去重后候选 | 5 / 4 | 3 / 3 |
| 全部候选在原版上运行 | 2 通过、3 失败，退出码 1 | 5 通过、2 失败，退出码 1 |
| 筛选后原版套件 | 保留原有 1 项、追加 1 项，2 通过 | 保留原有 4 项、追加 1 项，5 通过 |

AI 初始实验经根目录 `main.py` 提供的 HTTP 接口完成导入、F09 生成、F10 执行、F13 建立和重跑。模板初始实验也通过该入口开展。两场 F13 反馈均调用本机 Ollama `http://127.0.0.1:11434`，实际模型为 `qwen2.5-coder:0.5b`，模型摘要为 `4ff64a7f502a08b7616edb8ca0a79eb1853fc363d842b7df4b46915d11a3fb09`。本次推理未调用付费 API。[AI 初始测试](ai-initial-final-task.json) · [模板初始测试](local-ai-task.json) · [AI 入口运行日志](ai-initial-final-run.txt) · [模板入口运行日志](live-experiment.txt)

## 逐候选校验

模型接收存活位置、相应改动、函数及现有测试摘要，返回调用、预期与理由。F13 将可解析的候选追加到原套件，在 WASI 内对原版执行 Pytest，按实际通过节点进行筛选，然后在同一份完整清单上执行采纳后的套件。表中单引号表示模型实际提出了字符串预期。节点完整名称的共同前缀为 `test_generated.py::test_mutation_`。

| 初始套件与反馈位置 | 实际候选调用 | 模型给出的预期 | 原版实测及选择 | 节点后缀 |
| --- | --- | --- | --- | --- |
| AI，L8:10、L10:16 | `bonus(0, True)` | 字符串 `'1'` | 返回整数 0，断言失败，未采纳。两处响应给出相同调用及预期，去重后实跑一项 | `e804e2b2ec3c23bd` |
| AI，L9:9 | `bonus(-1, True)` | 抛出 `ValueError` | 原版按预期抛出，采纳 | `0473d9a7eced8496` |
| AI，L10:22 | `bonus(2, True)` | 字符串 `'1'` | 返回整数 3，断言失败，未采纳 | `e49b8cc7b59c304a` |
| AI，L12:5 | `bonus(1, True)` | 字符串 `'None'` | 返回整数 1，断言失败，未采纳 | `e4acf0e00c4dc92a` |
| 模板，L9:9 | `bonus(-1, True)` | 抛出 `ValueError` | 原版按预期抛出，采纳 | `0473d9a7eced8496` |
| 模板，L10:16 | `bonus(0, True)` | 抛出 `ValueError` | Pytest 报告 `DID NOT RAISE ValueError`，未采纳 | `2a12089eaaaaab5c` |
| 模板，L10:22 | `bonus(2, True)` | 字符串 `'2'` | 返回整数 3，断言失败，未采纳 | `438069270eb9f7eb` |

采纳节点对应的存活变异 UUID 为 `bad0575f-acc5-58a6-a467-7a1cb312a19b`。两场模型反馈都将负数契约作为选例理由，初始套件都没有向 `bonus` 传负数。补测后，对照副本继续执行了原先未抛异常的路径，Pytest 在补测的 `pytest.raises(ValueError)` 上报告 `DID NOT RAISE ValueError`。其余位置的 Killed、Survived 与执行错误数分别保留。按事件 `feedback`、`validation`、`selection`、`baseline` 及 `observation` 可逐步复查提示、原始响应、输入、测试和判定。[AI 初始实验原始事件](ai-initial-final-campaign.json) · [模板初始实验原始事件](local-ai-experiment.json)

加固复验中，F09 的 `local_model_digest` 与 F13 的 `model_digest` 均为 `4ff64a7f502a08b7616edb8ca0a79eb1853fc363d842b7df4b46915d11a3fb09`，得分再次从 3/9 升至 4/9，`impact` 将唯一新增检出关联到 L9 和实际失败节点 `test_generated.py::test_mutation_0473d9a7eced8496`。[初始模型身份记录](ai-hardened-task.json) · [反馈身份与检出记录](ai-hardened-campaign.json)

## 首轮失败记录

| 早期会话 | 观察结果 | 补测后得分 |
| --- | --- | --- |
| 模板初始 `596884a8-df7f-48e3-ae7e-9d7beb6b1301` | 原版 4 项通过，变异得分 4/9。两次模型输出分别因调用语法无效、未直接调用选定目标而被拒绝；状态为 `feedback_rejected` | 无有效补测，无得分 |
| AI 初始 `738e2c7c-b6ca-485f-ac4b-df1165cff925` | 原版 1 项通过，变异得分 3/9。模型候选去重后有 2 项；整套在原版上 2 通过、1 失败。错误候选期望 `bonus(1, True) == 2`，实际值为 1；状态为 `feedback_baseline_failed` | 无有效补测基线，无得分 |

这两场独立保留，没有将它们与后续成功会话拼接。完成的两场实验为每处仍然存活的变异分别收集候选，再以原版实测筛选；同一位置同时保留模型提议及人可复核的断言差异。[模板首轮原始报告](live-first-experiment.json) · [模板首轮独立复算](verified-template-first.txt) · [AI 首轮原始报告](ai-initial-campaign.json) · [AI 首轮独立复算](verified-ai-first.txt)

## 复验与剩余问题

在仓库根目录运行以下命令，可在独立数据目录中通过 `main.py` 重新开展 AI 初始实验。本机需要已安装上述模型。每场新运行有独立任务及会话 ID，其模型预期和最终得分由本次实测决定。[入口脚本](../../eval/phase04/ai_initial_campaign.py) · [模型配置](../../docs/phase04/LOCAL_MODEL.md)

```powershell
.\.venv\Scripts\python.exe -m eval.phase04.ai_initial_campaign
```

本次两场最终实验都留下 L10 的布尔逻辑和比较边界变异存活。AI 初始套件额外留下 L8 的比较边界和 L12 的返回值变异存活。实验只覆盖 `bonus`、单一固定算子配置及本机这一模型，尚无跨项目效果估计。工作包 WP03/WP04，阶段负责人陈帅廷，实际操作 Codex，人工签收待办。反馈实现提交 `5be8d12`，原版筛选与集成提交 `f6daaa1`。[最终 AI 实验独立复算](verified-ai-initial.txt) · [最终模板实验独立复算](verified-template-initial.txt)
