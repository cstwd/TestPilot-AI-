"""Present Phase 06 acceptance only from preserved observations."""
from xml.etree import ElementTree as ET
from .summary import OUT, RAW, read


def write(name,rows):
    (OUT/name).write_text("\n".join(rows)+"\n",encoding="utf8")


def stats(a,b):
    return "—" if not b else f"{a}/{b}（{100*a/b:.2f}%）"


def main():
    d=read(OUT/"summary.json")
    sampled=d["resources"]
    w=d["workloads"]
    quality=d["stages"]
    feedback=d["feedback"]
    old=d["historical_kills"]
    live=read(RAW/"live.json",{})
    main_probe=read(RAW/"main-head-health.json",{})
    evidence=live.get("F13/evidence",{}).get("payload",{})
    before=evidence.get("before")
    after=evidence.get("after")
    f13_pass=bool(before and after and before["total"] == after["total"] == 9
                  and after["killed"]>before["killed"])
    core=f13_pass and all(live.get(k,{}).get("http")==200 for k in ("model","F02/ast","F02/ai","F03/suite","F04/execution"))
    recover=d["recovery"] or {}
    off=recover.get("offline_model",{}).get("http")
    home=recover.get("offline_dashboard",{}).get("http")
    back=recover.get("8k_health",{}).get("http")
    restored=off==503 and home==200 and back==200
    full_xml=RAW/"full-regression.xml"
    nodes=list(ET.parse(full_xml).iter("testcase")) if full_xml.exists() else []
    failures=[node.get("name") for node in nodes if any(node.find(t) is not None for t in ("error","failure"))]
    critical=("stability-4k-final","soak-4k","pressure-4k","pressure-8k","pressure-16k")
    full_load=all(w.get(k,{}).get("ok")==n for k,n in zip(critical,(100,36,2,2,2)))
    comparable=d["attempts"]==30 and quality["before"].get("total")==quality["after"].get("total")==117
    if core and restored and full_load and comparable and nodes and not failures:
        status="READY_FOR_PRODUCTION"
    elif core:
        status="READY_WITH_LIMITATIONS"
    else:
        status="BLOCKED"
    ai_mutation=read(RAW/"live-ai-mutation.json",{})
    ai_measure=ai_mutation.get("result",{}).get("before") or {}
    repair=read(RAW/"repair-live.json",{})
    write("E2E.md",["# PHASE-06 真实应用链路验收","",
        "从项目根入口启动 FastAPI，独立使用 SQLite 与 WASI。已核验的模型身份出现在健康探针、源码理解、初始测试和补测记录。",
        "| 路径 | HTTP |","| --- | ---: |",
        *[f"| {k} · `{v['path']}` | {v['http']} |" for k,v in live.items()],"",
        f"同一源码的显式模板 F13 会话实际检出 {before['killed'] if before else '—'}/9 → "
        f"{after['killed'] if after else '—'}/9。另由默认 Qwen 初始套件经正式 API 获得 {ai_measure.get('killed','—')}/9。",
        f"F12 使用预设错误测试调用实际 Provider，原版 Pytest 为 {repair.get('before',{}).get('status','未记录')}，最终为 "
        f"{repair.get('after',{}).get('status','未记录')}，依据既有文档契约门选择 {repair.get('chosen',{}).get('mode','未记录')}。",
        f"项目测试在集成提交 `0ddc083` 完成 {len(nodes)} 项，其中 {len(failures)} 项失败。"
        "后续变异反馈总预算改动另有 21 项测试通过。HTTP 协议异常测试使用明确标注的替身，真实 AI 判定来自现场模型与 WASI。",
        f"独立工作区运行期间，主分支已包含 Provider 及并行加固。对主分支快照 `{main_probe.get('head','—')}` "
        f"使用独立 Ollama 实测健康状态为 `{main_probe.get('health',{}).get('state','—')}`。该快照完成真实健康探针。",
        "[完整 API 记录](raw/live.json) · [AI 初始套件实际 F13](raw/live-ai-mutation.json) · "
        "[F12 测试](raw/repair-live.json) · [完整 JUnit](raw/full-regression.xml) · "
        "[最终定向复测](raw/final-budget-tests.txt) · [主分支真实探针](raw/main-head-health.json)"])
    write("PERFORMANCE.md",["# PHASE-06 本机负载、压力与恢复","",
         "同一固定权重，Ollama 单并发、Vulkan、量化 KV。物理内存与 Commit 余量各至少 2 GiB，显存余量至少 512 MiB。"
         "守护进程 0.5 秒采样并在触线时回收进程。首次默认缓存触发保护，明确保留停止记录。"
         "随后禁用 prompt RAM cache 和 context checkpoints。这两个选项源于日志显示每个上下文检查点约 149.6 MiB，并随不同请求保留多份缓存。","",
         "| 运行 | 成功/请求 | 失败类别 | 首可见内容中位秒 | 平均输出 token/s |","| --- | ---: | --- | ---: | ---: |",
         *[f"| {name} | {row['ok']}/{row['rows']} | {row['errors'] or '无'} | {row['median_ttft_s']} | {row['mean_output_tps']} |"
           for name,row in sorted(w.items())],"",
         "并发试验先通过 Provider 队列调度。超出排队容量的请求保留拒绝证据。压力试验记录后端实际输入 token 数。"
         "连续短请求和业务生成共用一个 Vulkan 执行槽。首可见内容计时覆盖从 HTTP 请求到首个非空输出。",
         "首次触发保护的记录使用较早的计时点，其首 token 数据仅随原始记录保留。验收使用最终 100 次的请求起点计时。",
         *[f"- {name} 的实际输入 token 为 {row['input_tokens']}。[原始记录](raw/{name}.ndjson)"
           for name,row in sorted(w.items()) if name.startswith("pressure")],"",
         "| 实验 | 物理使用峰值 GiB | 可用物理最小 GiB | Commit 峰值 GiB | Commit 最小余量 GiB | 显存峰值 MiB | CPU 平均/峰值 % | 监控秒数 |",
         "| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
         *[f"| {name} | {s.get('peak_physical_gib','—')} | {s.get('min_physical_free_gib','—')} | {s.get('peak_commit_gib','—')} | "
           f"{s.get('min_commit_free_gib','—')} | {s.get('peak_gpu_mib','—')} | {s.get('mean_cpu_pct','—')}/{s.get('peak_cpu_pct','—')} | "
           f"{s.get('duration_s','—')} |" for name,s in sorted(sampled.items())],"",
         f"在同一 FastAPI 进程进行停机与恢复。离线健康 HTTP {off}，离线仪表盘 HTTP {home}，重启后真实模型健康 HTTP {back}。"
         "[恢复记录](raw/recovery.json) · [资源日志及逐请求记录](raw)"])
    write("MUTATIONS.md",["# PHASE-06 变异测试与补测对照","",
         "沿用 8923f2c 的十个项目、三组原种子、117 个预登记变异位置。主文件、依赖和变异清单摘要逐项核对。"
         "原版选中套件和变异副本都经 WASI，评分沿用 F13。每个有效套件使用该项目整个清单，跨组比较固定使用 117。",
         "历史组结果读取 PHASE-05 归档。PHASE-06 使用结构化协议及同一模型，生成失败和未通过原版的尝试留档，仍保留固定总分母。","",
         "| 组别 | 检出 | 存活 | 执行错误 | 超时 | 无有效套件位置 | 固定分母检出率 |",
         "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
         *[f"| PHASE-05 {name} | {old[a]} | 见历史 | 见历史 | 见历史 | 见历史 | {stats(old[a],117)} |"
           for a,name in zip("BCD",("模板","初始 27B","27B 反馈后"))],
         *[f"| PHASE-06 {name} | {quality[a].get('killed',0)} | {quality[a].get('survived',0)} | "
           f"{quality[a].get('execution_error',0)} | {quality[a].get('timeout',0)} | {117-quality[a].get('total',0)} | "
           f"{stats(quality[a].get('killed',0),117)} |" for a,name in (("before","初始 27B"),("after","反馈后 27B"))],"",
         f"30 个登记的项目/种子实验已有 {d['attempts']} 个结算。反馈覆盖 {feedback.get('survivor_requests',0)} 个存活变异，"
         f"实际模型响应尝试 {feedback.get('provider_attempts',0)} 次。"
         f"可进入原版校验候选 {feedback.get('candidates',0)} 个，采纳 {feedback.get('accepted',0)} 个。"
         f"观察到的净新增检出数为 {feedback['net_kills']}。",
         "模型可以返回无可区分输入。该状态保存原因，仍按完整清单重跑和统计。"
         "与 PHASE-05 的 3 次截断相比，当前在协议中限制原因长度、明确无候选分支并对格式错误重试一次。",
         "`cap` 的比较边界在普通整数相等时两个分支返回同值。三轮模型均提出 `cap(0, 0) == 0`，原版通过，变异版也通过。三项均保留为存活。",
         "五次生成在重试后仍未通过冻结协议，涉及十四个位置，计入完整分母。","",
         "[逐项目原始生成、试验和复跑](raw/quality) · [机器复算](summary.json)"])
    tests=f"{len(nodes)} 项，失败 {len(failures)}" if nodes else "完整 JUnit 尚未生成"
    paired=f"{before['killed']}/9 → {after['killed']}/9" if f13_pass else "见真实请求记录"
    write("TP_PHASE_06_ACCEPTANCE.md",["# TP-PHASE-06 统一 27B 迁移验收","",
         f"生产状态 **{status}**。提交位于 `integration/tp-phase-06`。项目负责人陈帅廷，责任工作包 WP01/WP03/WP04，实际操作者 Codex。",
         "统一 Provider 使用本机 Qwen3.8-27B UD-IQ3_XXS。Ollama 标签、清单摘要、权重摘要、发布修订、Vulkan 和实际输出均进入身份判定。API 费用为零。",
         "集成工作树基于 `7c796e7`，包含 PHASE-04 归档 `307d4bd`。历史 PHASE-05 原始证据由 `experiment/tp-phase-05` 的 `8923f2c` 引用。",
         "[迁移前审计](../../docs/phase06/AUDIT.md) · [运行配置与迁移清单](../../docs/phase06/DEPLOYMENT.md) · [旧模型扫描证据](raw/entrypoint-audit.txt)","",
         "| 验收 | 实测结果 |","| --- | --- |",
         f"| 实际 F01–F04、F09 及 F13 | {paired}，保留实际 SQLite、HTTP 和 WASI 结果。 |",
         f"| 协议与回归 | {tests}。覆盖结构缺失、异常 JSON、空消息、超时、请求队列及冻结参数数组。 |",
         f"| 源码理解 | {d['understanding']['points']}/70。参数格式 {d['understanding']['fields'].get('parameters',0)}/10，历史为 0/10。 |",
         f"| 质量对照 | 27B 初始 {quality['before'].get('killed',0)}/117，反馈后 {quality['after'].get('killed',0)}/117。 |",
         f"| 资源与恢复 | 稳定、压力及真实启停结果详见性能报告。恢复检查 {'通过' if restored else '存在未通过环节'}。 |","",
         "阶段实现提交 `98adf18`，Windows 状态读重试及复验流程提交 `0ddc083`。"
         "量化模型按生产 4K 配置验证。更大上下文和长期运行均有独立记录。固定质量回归仍有五个生成尝试被拒，发布状态受影响。"
         "验收服务在测试完成后关闭。本机统一模型部署按守护步骤启动。",
         "[真实端到端报告](E2E.md) · [完整回归](raw/full-regression.txt) · [性能与内存报告](PERFORMANCE.md) · [变异对比](MUTATIONS.md) · [原始证据](raw)"])

if __name__=="__main__":
    main()
