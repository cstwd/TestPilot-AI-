# TP-GITHUB-001 · GitHub 远程连接验收

2026-11-27（北京时间）　|　WP05 交付管理　|　责任人：王选中　|　实际操作与技术核验：Codex　|　项目负责人审核：待陈帅廷确认

**首次推送通过。** 在读取到空的远程 refs 后，依次执行 `git push -u origin main` 和 `git push -u origin develop`。两次均创建了远程分支并设置上游。随后直接从 GitHub 回读并逐分支核对 SHA。工作区清洁项仍待主开发任务收尾。

## 目标与分支

项目根目录为 `D:\TestPilot AI`。初查时无 remote，只有本地 `main`。原指定的仓库名两次查询均返回 404；项目负责人在本次对话中改选已有的 `cstwd/TestPilot-AI-`（名称末尾带短横线）。GitHub 元数据显示该仓库为 Private。配置的 fetch 和 push 地址均为 `https://github.com/cstwd/TestPilot-AI-.git`。[GitHub 仓库](https://github.com/cstwd/TestPilot-AI-)

下表为首次推送完成后、提交本报告之前的实测快照。远程 SHA 取自 `git ls-remote --refs --heads origin main develop`。

| 本地分支 | 上游 | 本地及远程共同 SHA | 验证结果 |
| --- | --- | --- | --- |
| main | origin/main | `93f7a187d3964ad373221d87261d05413e623f12` | 已推送，逐位一致 |
| develop | origin/develop | `93f7a187d3964ad373221d87261d05413e623f12` | 从当时的 main 新建，已推送，逐位一致 |

首次检查的 `main` 为 `743e24f`。并行开发随后提交 F03；安全规则另以 `93f7a18` 提交。两条分支均保留工程基线 `8038be278d656a716a5c9cb2cb629602864eb011` 和阶段验收归档 `88ebf23777605a20a22279a62578b77a108e0e0e`。祖先关系经 `git merge-base --is-ancestor` 核实。

## 安全与现场保护

| 核查 | 证据与结论 |
| --- | --- |
| 忽略规则 | 补充环境文件、私钥和凭据文件、私有数据和上传目录、SQLite 临时文件及 IDE 本机设置。[.gitignore](../.gitignore) |
| 实际生效 | `git check-ignore` 命中环境文件、密钥、上传目录、缓存、数据库、私人目录等样本；`git ls-files --cached -i --exclude-standard` 输出为空。 |
| 提交内容 | 对首次推送快照可达的 7 个提交、86 个不同文件对象及工作区当时的 72 个已跟踪路径进行路径与字节模式扫描。常见服务令牌、私钥、带认证信息的 URL、认证头、JWT 和明文密码赋值等规则均无命中。扫描日志只统计命中类型和文件路径；此检查无法证明任意格式的秘密均不存在。 |
| 未提交文件 | `git status` 和 `git diff --stat` 显示主开发任务有执行器、前端、测试和模块验收材料在写入。原样留在当前工作区，未纳入交付管理提交。没有切换分支、stash、重置、清理或强推。 |

## 复核与待办

从项目根目录执行以下命令，可核对归档提交之后的实时状态。持续开发可能使分支前进，以远程实际回读为准。

```powershell
git remote -v
git branch -vv
git rev-parse main develop
git ls-remote --heads origin main develop
git log -1 --format=%H -- reports/TP_GITHUB_001_ACCEPTANCE.md
git status --short --branch
```

**工作区干净：未通过。** 两条分支推送成功与工作区存在未提交业务代码可同时成立。由主开发任务按 F04–F06 模块验收节奏处理这些改动，再复查工作区；此次未替业务模块提交或丢弃文件。
