# WP05 工程工具链实测

| 组件 | 运行方式、权限和结果证据 |
|---|---|
| verify | 读取 [Skill 定义](../../.claude/skills/verify/SKILL.md) 后通过项目 Python 选择模块。静态编译与 Pytest/Node 实际输出见 [工具链](toolchain.txt) 和 [全套报告](verify-full.txt) |
| testpilot-workflow | 读取 [Skill 定义](../../.claude/skills/testpilot-workflow/SKILL.md) 后用于 MCP 兼容诊断与回归。[循环记录](LOOP.md) |
| MCP | Claude 项目配置 [.mcp.json](../../.mcp.json) 启动同目录 Python stdio 子进程，读取 `TESTPILOT_DATA_DIR` 或默认 `data` 的 SQLite。只返回项目 ID/名称、执行状态和四类计数。提供 Schema、参数错误、数据库错误及无结果处理。[服务](../../mcp-server/server.py) · [真实握手、工具列表及调用](toolchain.txt) · [stdio 协议](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports) |
| Hook | 以 `git -c core.hooksPath=hooks` 启用单条命令，或由维护人选择在本仓库设置 `git config core.hooksPath hooks`。只检查暂存差异，失败阻止提交。在临时 Git 仓库实际触发坏文件拒绝与修正后的成功。[脚本](../../hooks/pre-commit) · [输出](toolchain.txt) |
| Reviewer | Codex 独立子代理按 [角色定义](../../.claude/agents/testpilot-reviewer.md) 阅读、复现、结构化报告，无写入操作。[独立审查](REVIEWER.md) |

本次两个 Skill 由 Codex 显式读入并执行。MCP 测试使用协议客户端真实启动本机 Server，读一条 WASI 通过记录并确认数据库字节未改变。Claude CLI 已识别项目 MCP 配置，客户端首次信任仍待确认。[定义校验](skill-definitions.txt) · [Claude 项目发现](claude-mcp-discovery.txt)
