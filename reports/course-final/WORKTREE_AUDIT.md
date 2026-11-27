# 开工审计与验收基线

2026-11-27，工作目录 `D:\TestPilot AI`，主线最初为 `9fdfa7e`，Git 显示相对 `origin/main` 领先 37 个提交。最初读取工作目录、分支、所有可达提交、根文件、隐藏路径及忽略规则。实际使用 `git status --short --branch`、`git branch -avv --no-abbrev`、`git log --all --oneline --decorate`、`git worktree list`、`git ls-files` 和 `Get-ChildItem -Force`。测试和模型证据逐阶段列入[成果索引](../../docs/COURSE_EVIDENCE_INDEX.md)。

| 开工状态 | 核对结果 |
|---|---|
| main | F01–F04 界面升级已提交。F05 曾在工作区开发，随后由原工程流程独立提交 `c49dde2` |
| develop / 远程跟踪 | `93f7a18`，初始历史归档。远程读取使用本机已存在的跟踪引用 |
| experiment/tp-phase-05 | `8923f2c`，工作树 `.runtime/tp-phase-05`，主线合并 `1acd2ff` |
| integration/tp-phase-06 | 起始 `98adf18`，随后已有 `0ddc083` 修补，主线合并 `646ef7d` |
| 根目录现有工作 | `reports/model/` 的未跟踪阶段中间试验和同时进行的其他前端工作保持原工作区状态。课程装包按已提交的课程基线进行 |
| 工程工具 | `.agents/skills`、`agents`、`hooks`、`mcp-server` 初始以占位文件为主。新增工具正式定义见 [工具链](TOOLCHAIN.md) |
| 会话 | 从本机 Codex 按确认的会话 ID 提取可见信息，项目文件见[索引](../../transcripts/README.md) |

交付基线完整 Git 路径清单由 `git -c core.quotepath=false ls-tree -r -t --name-only ae21701` 得到。课程全面复验使用 `72a53b8` 的完整产品与工具，以主目录的 Python 3.13.11 执行。并行的工作台变更曾令实时工作区的 F06 浏览器会话读到不匹配的脚本和模板。待阶段六提交完整后合并 `74ba1b4`、复验新增的 F13 限时逻辑。课程归档使用合并后的 `ae21701` 加最终验收资料。[Git 路径清单](repository-index.txt) · [提交图](git-history.txt) · [环境核对](environment.txt) · [实时工作区 F06 记录](f06-working-tree.txt)

## 复现主线本机模型探针

用项目解释器在专用临时目录中运行 `python -m eval.phase06.serve --models E:/OllamaModels --data <临时模型目录> --port <可用回环端口>`。该监督器全量校验固定权重。观测到 `attestation.json` 的 `status=serving`、`vulkan=true` 后，将应用的 `TESTPILOT_MODEL_RUNTIME` 指向该临时目录，`TESTPILOT_DATA_DIR` 指向独立临时数据库目录，从同一根入口运行 `main.py --no-browser --port <用例端口>`。观测 `GET /api/health` 为 200 后请求 `GET /api/model/health`。主线成功输出记录 GPU 分配与权重指纹。关闭测试应用，向模型目录写入 `STOP` 后等监督器结束。[实际响应](model-main-live.json)
