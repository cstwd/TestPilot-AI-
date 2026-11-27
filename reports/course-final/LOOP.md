# WP05 循环执行记录

2026-11-27。责任 WP05 王选中，操作 Codex，项目组长人工签收待记。目标是让可安装的只读 MCP 同时查询真实项目和一个 F04 WASI 结果。完成条件为握手成功、发现两项工具、返回实测通过计数、拒绝坏参数且数据库字节保持一致。

1. **分析与验证**。按 Skill 检查 Git 与 API。先向本机 stdio Server 发 `list_projects`，查询归档返回数据库结构错误。[初次调用](mcp-before.txt)
2. **修改与诊断**。F01 使用整数 ID 且项目表无创建时间，F04 四类计数位于 `result` JSON。修正 SQL 和 Schema。实际协议回归进一步暴露测试数据库名为 `workflow.sqlite3`，而配置约定 `testpilot.sqlite3`。[第一次回归](toolchain-first.txt)
3. **修复**。在隔离 fixture 中将实际 WASI 输出所在库置于标准文件名。继续验证错误输入和 Git Hook，保留原库字节比对。[测试](../../tests/test_course_toolchain.py)
4. **回归与验收**。按 verify Skill 运行工具链 scope，实际 stdio 回包和 Git Hook 的退出由 [报告](toolchain.txt) 记录。另按实验规范核对冻结评测，结果见 [离线复算](offline-replay.txt)。
