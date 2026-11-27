# PHASE-06 真实应用链路验收

从项目根入口启动 FastAPI，独立使用 SQLite 与 WASI。已核验的模型身份出现在健康探针、源码理解、初始测试和补测记录。
| 路径 | HTTP |
| --- | ---: |
| model · `/api/model/health` | 200 |
| F01/project · `/api/projects` | 201 |
| F01/file · `/api/projects/1/files` | 200 |
| F02/ast · `/api/engine/files/1/analysis` | 200 |
| F02/ai · `/api/engine/files/1/understanding` | 200 |
| F03/suite · `/api/files/1/suites` | 200 |
| F04/execution · `/api/runs/1` | 200 |
| F09/configured · `/api/engine/files/1/tasks` | 201 |
| F13/explicit-template · `/api/engine/files/1/tasks` | 201 |
| F13/plan · `/api/engine/tasks/aa06edf5-8249-4bb7-be4e-424cc9cf5259/mutations` | 201 |
| F13/run · `/api/mutations/51a9b5d8-4b04-4b1a-a7a9-6868796585d1/run` | 200 |
| F13/evidence · `/api/mutations/51a9b5d8-4b04-4b1a-a7a9-6868796585d1/report` | 200 |

同一源码的显式模板 F13 会话实际检出 4/9 → 7/9。另由默认 Qwen 初始套件经正式 API 获得 7/9。
F12 使用预设错误测试调用实际 Provider，原版 Pytest 为 failed，最终为 passed，依据既有文档契约门选择 rules。
项目测试在集成提交 `0ddc083` 完成 148 项，其中 0 项失败。后续变异反馈总预算改动另有 21 项测试通过。HTTP 协议异常测试使用明确标注的替身，真实 AI 判定来自现场模型与 WASI。
独立工作区运行期间，主分支已包含 Provider 及并行加固。对主分支快照 `b0f488e` 使用独立 Ollama 实测健康状态为 `ready`。该快照完成真实健康探针。
[完整 API 记录](raw/live.json) · [AI 初始套件实际 F13](raw/live-ai-mutation.json) · [F12 测试](raw/repair-live.json) · [完整 JUnit](raw/full-regression.xml) · [最终定向复测](raw/final-budget-tests.txt) · [主分支真实探针](raw/main-head-health.json)
