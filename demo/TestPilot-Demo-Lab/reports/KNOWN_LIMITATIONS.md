
# 产品联调观察

| 情况 | 可复核证据 | 处理 |
| --- | --- | --- |
| F03 模板的同类型默认输入会触发某些函数的合法异常 | `percentage_calculator.percent_of` 零分母、`significant_digits.round_significant` 非正精度、`shopping_cart.cart_total` 嵌套行形状、`retry_policy.retry_delay` 第零次尝试 | 保留红基线回执，正式 F13 使用有效绿色基线的函数 |
| F03 普通工作台固定模板 | `frontend/static/generation.js` 的生成模式为 `template` | 实际模型盲测显式调用 F03 的 `ai` 套件接口 |
| F13 当前算子由产品固定 | 报告的 profile 与 manifest 来自既有 F13 | 验收比较、算术、布尔、条件、返回和异常，边界通过比较算子改变 |
| 首次本机模型触发 Windows 资源保护 | [首轮盲测回执](product_blind_resource_guard.json) | 保存 10 项 F01/F02 与 F03 结构性错误，随后使用独立运行目录重试 |
