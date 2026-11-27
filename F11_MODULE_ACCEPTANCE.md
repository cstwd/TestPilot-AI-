# F11 · Failure Analysis Engine

实测通过。责任人陈帅廷，实际开发、执行和独立复核由 Codex 完成。实现提交 `eb931c8`，保守归因复核修正 `6bc372f`。

[分析器](backend/engine_failures.py) 读取 F10 的真实节点、失败阶段、异常类型、差异和 traceback，把实际失败语句中的目标调用按签名绑定到文档契约。结果区分程序缺陷、测试错误、环境、跳过及未确定，附判断理由与定位精度。没有实际业务帧时只给出目标函数入口这一候选位置。复杂状态准备或无法证明的期望保留未决。

- `.venv/Scripts/python.exe -m pytest tests/test_f11.py -q -s` 的首次模块提交实测 5 项通过，后续绑定与契约复核版本 6 项通过；最终加上有状态调用用例后为 **7 passed in 20.41s**。WASI 中分别观察到真实断言差异、意外异常、没有抛出约定异常、测试自身错误、跳过与超时。[模块输出](reports/phase03/F11.txt) · [最终输出](reports/phase03/F11-review.txt)
- 状态计数器第二次调用返回 2 并触发 `assert 2 == 1`；系统保留差异，将归属标记为未确定。源码和原始判断链可在测试中复核。[测试定义](tests/test_f11.py) · [独立审查](reports/phase03/REVIEW.md)
