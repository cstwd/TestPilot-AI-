# PHASE-02 缺陷与修复

| 发现 | 影响与处理 | 复核证据 | 工作包负责人 / 实际操作 |
| --- | --- | --- | --- |
| F02 漏掉条件语句中的函数定义 | AST 遍历补上控制流下的定义，保留原始行号。 | `743e24f` · [模块验收](../../F02_MODULE_ACCEPTANCE.md) | WP01 陈帅廷 / Codex 主代理、Reviewer |
| F05 文件名匹配与 SQLite 不一致，部分错误缺少可重跑节点 | 使用与数据库一致的文件身份规则，从有可重跑节点的失败项登记缺陷。 | `b6f4ef5` · [模块验收](../../F05_MODULE_ACCEPTANCE.md) | WP04 马雪朋 / Codex 主代理、Reviewer |
| F04 浏览器验收在跳转后读取旧响应体 | 首轮全套测试有 1 项失败。修正验收脚本，从新页面的运行 ID 回读持久化结果，并核验套件与运行状态。 | `f31a901` · [首次输出](../../reports/phase02/first-integration.txt) · [重跑输出](../../reports/phase02/full-suite.txt) | WP02 陈万策、WP04 马雪朋 / Codex 主代理 |

演示样例另有一条负数处理缺陷，经实际测试发现并登记在验收临时数据库。修复版本沿用原套件，导出的 JSON 保存了原失败节点和回归的运行 ID。[样例缺陷与回归证据](../../reports/phase02/fixed-report.json)
