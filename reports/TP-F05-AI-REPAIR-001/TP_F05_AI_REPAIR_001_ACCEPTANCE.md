# TP-F05-AI-REPAIR-001 验收报告

2026-11-27，F05「缺陷与修复回归」接入本机 Qwen 源码修复。实现提交 `b40b54e`，开发基线 `039b14d`。WP04 责任人马雪朋，实际实现、操作与验收由 Codex 主代理完成，代码由独立 Codex Reviewer 复核。成员人工签收待项目组确认。

## 操作说明

1. 确认既有 Qwen 本地模型守护程序正在运行。首次配置或本机模型服务已停止时，按现有部署手册启动同一模型。可从 PyCharm 运行根目录 `main.py`，并访问 `http://127.0.0.1:8000`。[模型部署手册](../../docs/phase06/DEPLOYMENT.md)
2. 打开「缺陷管理」，选择项目与已登记缺陷。专项演示可直接打开 `/workbench/bugs?project=7&file=16&bug=2`。
3. 在**原始失败证据下方的「AI 修复」**点击「AI 分析并生成修复」。页面显示排队、分析、生成或失败状态。
4. 生成后查看根因、预期与实际行为、行号、修改原因和并列 Diff。可以点击「重新生成修复」，也可以点击「应用 AI 修复」。应用后，工作台创建独立文件修订，并将其选入「修复候选版本」。
5. 点击「运行回归」，核对确认框中的原始套件和候选版本，再点击「确认运行」。在右侧「选中的回归」查看修复前后失败数、修复后通过数和「回归执行日志」，在缺陷标题旁查看最终缺陷状态。

本次模型服务使用 Ollama 0.40.18、RTX 5080 Laptop Vulkan 和现有 Qwen3.8-27B UD-IQ3_XXS 权重，API 费用为 0。推理应用进程设置 `TESTPILOT_MODEL_USE_MMAP=0`，沿用已有 Windows 资源保护部署选项。未设置该变量时沿用 Provider 的映射默认行为。验收使用独立运行目录和端口，两次修复推理完成后关闭该次模型进程，再开始 WASI 回归。

## 真实专项验收

通过根目录 `main.py --port 49261 --no-browser` 启动，Playwright 驱动本机 Edge 158.0.4370.33 操作实际页面。宿主 Windows 11 build 26200，Python 3.13.11。模型使用同机守护 `python -m eval.phase06.serve --data <验收模型运行目录> --port 11769`。数据库来自当前项目库的 SQLite 备份副本，保留原始 IDs。

| 证据 | 实际结果 |
| --- | --- |
| 原始项目、缺陷、源码 | 项目 #7，缺陷 #2，`unit_scaling.py` v1 文件 #16 |
| 原始运行、套件、失败项 | 运行 #12，套件 #8，`test_generated.py::test_normal_return_contract` |
| 分析推理 | `1a427e21-b823-4746-86de-3d4bc11777c6`，首次响应通过协议校验，输入 1028 / 输出 170 tokens，约 10.54 秒 |
| 代码生成推理 | `3c293070-6047-48e3-accb-bab0dca9a3c8`，首次响应通过协议及静态校验，输入 1218 / 输出 93 tokens，约 7.49 秒 |
| 根因与修复 | 第 3 行的 `meters // 1000` 返回整数并丢失小数；模型建议改为 `meters / 1000` |
| 修复记录、候选修订 | AI 修复 #1，独立文件 #17 / v2，SHA-256 `7d89f9c815fbf2116407c92a72fe5fe575aac3a9c4c0e10437cc1b3edf5b1a09` |
| 原版套件 #8 的结果 | 原始 #12 为 1 通过、2 失败、1 跳过、0 错误。AI 候选回归 #14 为 3 通过、0 失败、1 跳过、0 错误，退出码 0，缺陷 #2 已解决 |
| 受限环境 | 离线 WASI，Python 3.15.2、Pytest 9.2.0、Coverage.py 7.17.5。两次运行中同一个属性测试均因 WASI 缺少 Hypothesis 而跳过 |
| 补充值检查 | 原版套件主要检查返回类型。另对候选运行 4 个 WASI 参数用例，分别核对 2、0、−2 和 1999 米的精确换算预期，4 项通过。该执行独立于原套件和缺陷关闭判定 |
| 历史证据保护 | 原始文件 #16、套件 #8、运行 #12 的数据库行在原库和副本逐项一致。原库的缺陷 #2 保持待修复，原库未创建 v2 |

- [Edge 修复预览](preview.png) · [Edge 回归结果](regression.png) · [实际修复 Diff](unit_scaling.diff)
- [原始源码、套件与失败运行](original.json) · [本机推理原始请求与响应](model.ndjson)
- [修复记录](repair.json) · [候选文件](file.json) · [缺陷状态](issue.json) · [正式回归记录](run.json) · [补充验证](supplemental.json)

## 实现与保护

- 前端复用 F05 深色页面、只读 Diff、版本选择与回归确认。新增 `frontend/static/bug-repair.js`，接入 `frontend/static/bugs.js`、`frontend/static/bugs.css` 和 `frontend/templates/bugs.html`。
- `backend/bug_repairs.py` 将原始源码、同一份套件、Pytest 日志、失败断言、函数签名、导入和可查到的原始版本依赖交给统一 `backend/model_provider.py`。Provider 保留两阶段推理的原始响应、请求、模型身份和运行 ID，并对结构或候选校验失败最多重试一次。模型不可用时显示失败原因。
- `backend/bug_repair_patch.py` 校对行号与原文，检查 Python AST、编译和定义签名，仅组装已有函数体内最多 30 行的改动。静态门拦截已覆盖的硬编码、测试框架访问和反射模式。复杂逻辑正确性仍依赖 Diff 审阅和回归证据。
- `backend/workbench.py` 在 SQLite 初始化时追加 `bug_repairs` 表及活动任务唯一索引。 `backend/projects.py` 在一个事务内创建版本与关联。重复应用同一修复返回已写入的版本。原始源码、套件和运行记录保持不可变。生成阶段和应用前核对原始内容 SHA-256。
- 新增 API 为 `GET/POST /api/bugs/{bug_id}/ai-repairs` 以及 `POST /api/bugs/{bug_id}/ai-repairs/{repair_id}/apply`。回归继续使用现有 `POST /api/bugs/{bug_id}/regressions`。`backend/bugs.py` 对 AI 候选比对回归用例清单及跳过状态，要求原失败项实际通过，并沿用现有最新修订决定缺陷状态的规则。
- F05 本次支持可在现有函数内完成的小范围补丁。需要引入新依赖、修改函数签名或超出本机上下文字节限制的任务会返回失败。原始日志过长时保留首尾和对应失败片段。

## 定向验证

| 命令 | 结果 | 证据 |
| --- | --- | --- |
| `python -m pytest -p no:cacheprovider -q tests/test_bug_repairs.py tests/test_f05.py tests/test_bug_intelligence.py` | 11 项通过。新增错误分支以受控模型响应验证，WASI 回归实际执行。已有 F05 Edge 回归保留 | [Pytest 输出](focused-pytest.txt) |
| `node --test tests/bug_diff.test.mjs` | 3 项通过 | [Node 输出](focused-diff.txt) |
| 从 F05 点击生成、应用、确认回归 | 真实推理 2 次，指定套件实际执行 1 次，专项通过 | [推理日志](model.ndjson) · [回归记录](run.json) |
| 单次 WASI 补充语义检查 | 4 个参数用例通过 | [用例与实际输出](supplemental.json) |
| `git diff --check` | 通过 | 实现提交 `b40b54e` |

独立复核确认了事务创建版本、原件只读和原套件复用。针对复核发现，补齐了按内容哈希校验、保留同项目候选在其他缺陷上的原有回归用途，以及将候选结果和整体缺陷状态分别显示。按任务要求执行定向验证。

[归档文件 SHA-256](SHA256SUMS)
