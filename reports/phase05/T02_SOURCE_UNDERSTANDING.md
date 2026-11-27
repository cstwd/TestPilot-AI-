# T02 源码理解

十个项目、七项逐字段评分，实得 56/70（80.00%）。四个项目含两个真实 Python 文件。模型只接收带行号源码及问题。预登记答案、完整模型输出和 WASI 对行为参考值的核验分别可查。

| 项目 | 函数 | 参数 | 实际返回 | 分支 | 边界 | 异常 | 缺陷位置 | 总分 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| [bonus](raw/understanding/bonus.json) | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 6/7 |
| [freight](raw/understanding/freight.json) | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 6/7 |
| [clamp](raw/understanding/clamp.json) | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 6/7 |
| [expiry](raw/understanding/expiry.json) | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 6/7 |
| [tax](raw/understanding/tax.json) | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 5/7 |
| [prefix](raw/understanding/prefix.json) | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 6/7 |
| [pages](raw/understanding/pages.json) | 0 | 0 | 1 | 1 | 0 | 1 | 1 | 4/7 |
| [tier](raw/understanding/tier.json) | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 6/7 |
| [head](raw/understanding/head.json) | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 5/7 |
| [invoice](raw/understanding/invoice.json) | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 6/7 |
| 合计 | 8 | 0 | 10 | 10 | 9 | 9 | 10 | 56/70 |

人工复核发现，十个参数答案都采用带字段名的对象；其名称、类型和默认值表达正确，但与指定的三元素数组格式不同，依照冻结规则该项均计 0。分页样例将边界输入返回值写为契约期望的 1，源码实测为 2；空列表回退样例将 None 输入判断为 TypeError，实际走回退分支。税率和每页数量常量曾被报告为函数。定位项包含四处文档冲突和六个无冲突样例。

[冻结题集与规则](../../eval/phase05/frozen.json) · [十个实际行为参考作业](raw/references) · [评测程序](../../eval/phase05/understand.py)
