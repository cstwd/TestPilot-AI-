# testpilot-reviewer 实际审查

2026-11-27，Codex 子代理 `testpilot_reviewer`，只读，基线 `646ef7d`。输入为 [仓库角色定义](../../.claude/agents/testpilot-reviewer.md)、Phase 05 归档与 Phase 06 合并。

| 优先级 | 实际发现与回归处理 |
|---|---|
| P1 | 阶段五三个历史在线工具移除依赖后无法从主线启动。现场重跑固定 `8923f2c`，主线可只读复算。[复现入口说明](../../docs/COURSE_TESTING.md) |
| P2 | 在模拟守护进程换 PID／端口后，第二次调用发送到新回环端口，旧实现只校验了首端口。现对改变的运行身份重新核验，加入定向测试。 |
| P2 | 在模拟 `/api/ps` 缺少 GPU 分配时，健康 API 返回 unavailable，UI 仍显示刚刚验证。现检查 GPU 后才更新探测状态。非对象 JSON 也从曾抛出的 `AttributeError` 改为 protocol 错误。 |

审查命令 `python -m pytest tests/test_model_provider.py tests/test_f09.py tests/test_mutation_feedback.py tests/test_mutation_initial_profile.py eval/phase05/test_manifest.py -q`。默认隔离环境阻止回环，批准回环后 **35 passed in 1.07s**。按原始证据只读复算得到 0/81/104/105，并比对全部归档组字典。Reviewer 未加载真实模型。成员签收待办。

[Provider 修改](../../backend/model_provider.py) · [Provider 测试](../../tests/test_model_provider.py)
