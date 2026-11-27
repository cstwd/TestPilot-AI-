"""Render the comparison, generation and repair reports from verified observations."""
from collections import Counter
from statistics import mean
from .aggregate import ARMS, read
from .audit import RAW, REPORT
from .corpus import SPEC, SEEDS


def percent(x):
    return "—" if x is None else f"{x:.2f}%"


def write(name, lines):
    (REPORT/name).write_text("\n".join(lines)+"\n",encoding="utf8")


def main():
    summary=read(REPORT/"summary.json")
    groups=summary["groups"]
    campaigns=summary["campaigns"]
    assert all(r["run_count"]==30 and r["planned"]==117 for r in groups.values())
    performance=read(RAW/"vulkan-01"/"ready.json")
    pairs=summary["paired"]
    table=[]
    for arm,row in groups.items():
        table.append(f"| {arm} {ARMS[arm]} | {row['baseline']}/30 | {row['killed']} | {row['survived']} | "
                     f"{row['execution_error']} | {row['timeout']} | {row['noscored']} | {row['equivalent_candidates']} | "
                     f"{row['killed']}/{row['scorable_mutants']} · {percent(row['mutation_score'])} | "
                     f"{row['killed']}/117 · {percent(row['all_manifest_detection'])} |")
    write("T04_COMPARISON.md",["# T04 四组变异对照","",
       "每组 10 个固定项目、三轮独立尝试、每轮 39 个位置。A/C 使用同一 F09 输入、采样温度与种子；B 每轮重新调用确定性模板；D 与 C 配对。运行使用相同的隔离 WASI、源码摘要、算子清单与 F13 判读。",
       "每个有效原版基线的 F13 得分都使用该项目整个清单作分母。组级另给出统一的 117 位置检出率；降级、未通过原版或其他无可用套件的尝试保留在该分母中。等价候选单独列数并保留在分母内。","",
       "| 组别 | 绿色初始套件 | 杀死 | 存活 | 执行错误 | 超时 | 无有效套件 | 等价候选 | 已运行清单 F13 得分 | 全部 117 位置检出率 |",
       "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",*table,"",
       "## 三轮稳定性","",
       "| 组别 | 513 检出率 | 727 检出率 | 941 检出率 | 三轮产生不同的已验证源码摘要的项目数 |",
       "| --- | ---: | ---: | ---: | ---: |",
       *[f"| {arm} | "+" | ".join(percent(summary["rounds"][arm][str(s)]["all_manifest_detection"]) for s in SEEDS)+
         f" | {sum(x>1 for x in row['distinct_test_sha_per_project'].values())}/10 |" for arm,row in groups.items()],
       "","## 逐项目，三轮合计","",
       "| 项目 | 每组分母 | A 杀死 | B 杀死 | C 杀死 | D 杀死 |",
       "| --- | ---: | ---: | ---: | ---: | ---: |",
       *[f"| {name} | {sum(r['planned'] for r in campaigns if r['project']==name and r['arm']=='A')} | "+
         " | ".join(str(sum(r["killed"] for r in campaigns if r["project"]==name and r["arm"]==a)) for a in ARMS)+" |"
         for name in SPEC],"",
       "历史 bonus.py 的 9 项变异采用与 PHASE-04 相同的完整清单、UUID 和位置。本次套件从头生成，历史得分可独立查看。四个多文件项目保留主文件字节，辅助模块原文在来宾进程内加载。","",
       "[对照图](mutation-score.png) · [逐次 CSV](campaigns.csv) · [计算数据](summary.json) · [冻结协议](../../eval/phase05/PROTOCOL.md) · [PHASE-04 历史结果](../phase04/MUTATION_SCORE.md)"])
    lines=[]
    for a,r in groups.items():
        modes="、".join(f"{mode} {count}" for mode,count in r["suite_modes"].items())
        lines.append(f"| {a} {ARMS[a]} | {modes} | {r['responses']}/{r['model_requests']} | "
                     f"{r['baseline']}/30 | {r['generation_mean_s']:.3f} | "
                     f"{r['complete_jobs']}/{r['executions']} · {percent(r['actual_job_completion_pct'])} |")
    write("T03_TEST_GENERATION.md",["# T03 F09 测试生成与执行","",
      "A/C 通过既有 F09 适配器和 AST 门禁。回环转接记录实际提示与完整响应，并将同一采样参数应用到两种模型。原版由 F10 隔离执行。若有错误断言但原基线仍产生有效节点，则按完整函数去除失败用例并重验，保留原始代码、删减前执行记录和最终通过代码。模板降级只出现在生成日志中，AI 组对其保留未计分结果。","",
      "| 组别 | F09 来源或配对状态 | 返回的模型响应/请求 | 绿色原版 | 平均生成或反馈秒数 | Pytest 作业完整返回 |",
      "| --- | --- | ---: | ---: | ---: | ---: |",*lines,"",
      f"Qwen3.8 初始生成的实际后端平均吞吐为 {groups['C']['throughput_mean_tps']:.2f} token/s（按请求平均，含以结构拒绝的响应）。D 的生成时间包含原版校准。Pytest 完整返回率表示取得有效结构化作业记录，包含能正常报告断言失败的作业。","",
      "[完整 F09 提示、回复及测试文件](raw/campaigns) · [每次生成、原版和复跑指标](campaigns.csv)"])
    before=sum(p["before"] for p in pairs)
    after=sum(p["after"] for p in pairs)
    total=sum(p["total"] for p in pairs)
    differences=Counter(p["after"]-p["before"] for p in pairs)
    d=groups["D"]
    write("T05_MUTATION_FEEDBACK.md",["# T05 本机变异反馈","",
       f"{len(pairs)} 个有效 C/D 配对使用同一清单，杀死数由 {before}/{total}（{percent(100*before/total if total else None)}）"
       f"变为 {after}/{total}（{percent(100*after/total if total else None)}）。配对中 {sum(v for k,v in differences.items() if k>0)} 次提升，"
       f"{differences[0]} 次持平，{sum(v for k,v in differences.items() if k<0)} 次下降。",
       f"存活变异的真实模型反馈 {d['responses']}/{d['model_requests']} 个响应；F13 AST/字面量校验并去重后有 {d['proposal_count']} 个候选，"
       f"在原版上通过并采纳 {d['accepted_count']} 个，候选通过率 {percent(d['validated_candidate_pct'])}。",
       "每次请求包含原版文件、源代码差异、原套件和存活变异的 Pytest 节点、覆盖率及摘要。补测必须通过原版门禁；验证拒绝、重复、空候选和错误均可按位置查阅。无可采纳补测的有效原版套件仍执行全清单。","",
       "| 项目 | 种子 | 初始杀死 | 复测杀死 | 分母 |",
       "| --- | ---: | ---: | ---: | ---: |",
       *[f"| {r['project']} | {r['seed']} | {r['before']} | {r['after']} | {r['total']} |" for r in pairs],"",
       "[候选、选择记录与实际 Pytest](raw/campaigns) · [计算数据](summary.json)"])
    hit=lambda x, goal: "达到" if x is not None and x>=goal else "未达到"
    cs=groups["C"]["all_manifest_detection"]
    ds=d["all_manifest_detection"]
    cov=d["validated_candidate_pct"]
    write("TP_PHASE_05_ACCEPTANCE.md",["# TP-PHASE-05 Qwen3.8-27B 本地模型验收","",
       "项目 TestPilot AI。责任工作包 WP03、WP04，阶段负责人陈帅廷，实验操作 Codex。基线 `307d4bd`，实验分支 `experiment/tp-phase-05`。",
       "目标模型为本机已有的 Qwen3.8-27B UD-IQ3_XXS GGUF。CUDA 在首请求遇到 PTX JIT 资源分配失败，改用 RTX 5080 Laptop Vulkan 后完成连续推理以及 F09、F13 全流程。推理经本机回环接口完成，API 费用为零。","",
       "| 维度 | 结果 |","| --- | --- |",
       "| 模型源码理解 | 严格评分 56/70，80.00%。十组参数值在人工复核中正确，但结构与冻结要求不符，仍按规则计分。 |",
       f"| 测试质量 | Qwen3.8 初始 {percent(cs)}，模板 {percent(groups['B']['all_manifest_detection'])}，补测后 {percent(ds)}。按所有预登记位置计算。 |",
       f"| 推理性能 | 进程就绪 {performance['load_wall_s']:.3f} 秒，连续有效响应 10/10。短请求后九轮均值 19.21 token/s。 |","",
       f"初始目标 ≥55% {hit(cs,55)}。补测目标 ≥70% {hit(ds,70)}。候选原版通过率 {percent(cov)}，≥80% {hit(cov,80)}。",
       f"Qwen3.8 初始分数相对模板差 {cs-groups['B']['all_manifest_detection']:+.2f} 个百分点；反馈相对初始差 {ds-cs:+.2f} 个百分点。",
       "结论适用于这十个小型项目、三个采样种子及固定算子配置。多文件加载是独立评测适配层。整机物理内存采样在模型加载和执行期间接近上限。性能记录采用文本推理模式。",
       "F13 发现身份比较变异的最小文本差分可能错过算子位置，导致整个清单拒绝。实验分支仅对经 Cosmic Ray 精确复验的 `is → is not` 插入做定位修正。既有 bonus 清单逐项与 PHASE-04 一致。","",
       "- [环境与权重审计](T01_ENVIRONMENT.md) · [连续推理及内存数据](T01_PERFORMANCE.md)",
       "- [源码理解报告](T02_SOURCE_UNDERSTANDING.md) · [F09 生成报告](T03_TEST_GENERATION.md)",
       "- [四组对照报告](T04_COMPARISON.md) · [得分图](mutation-score.png) · [反馈报告](T05_MUTATION_FEEDBACK.md)",
       "- [完整原始数据](raw) · [逐次 CSV](campaigns.csv) · [可复算汇总](summary.json) · [冻结协议](../../eval/phase05/PROTOCOL.md)",
       "- [变异回归实测](raw/manifest-tests.txt) · [代码与实验脚本](../../eval/phase05)",
       "","项目组长人工签收待办。"])

if __name__=="__main__":
    main()
