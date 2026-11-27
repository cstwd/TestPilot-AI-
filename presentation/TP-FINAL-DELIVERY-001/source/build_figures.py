"""Produce individually reusable SVGs and a data-backed outcome chart."""
from pathlib import Path
import json
from xml.sax.saxutils import escape

root = Path(__file__).resolve().parents[1]/"05_DEMO_ASSETS"
metrics=json.loads((root/"charts/measurements.json").read_bytes())
def label(x,y,value,size=28,color="#eff7fe",weight=400):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}">{escape(str(value))}</text>'
def box(x,y,w,h,color):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"/>'
def save(rel,title,kicker,marks,source):
    canvas=['<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720"><g font-family="Microsoft YaHei,Arial,sans-serif">',box(0,0,1280,720,"#0d1824"),label(62,62,kicker,22,"#6cdedf",700),label(62,143,title,44,weight=700),box(62,177,1156,2,"#315267")]+marks+[label(62,674,source,18,"#91b0c5"),"</g></svg>"]
    (root/rel).write_text("".join(canvas),encoding="utf-8")
def series(rel,title,kicker,pairs,source):
    marks=[]
    for i,(left,right) in enumerate(pairs):
        y=207+i*84
        marks.extend([box(62,y,266,66,"#20394b"),label(81,y+43,left,23,"#6cdedf",700),label(354,y+43,right,24)])
    save(rel,title,kicker,marks,source)
series("workflow/10-ci.svg","两次冷启动失败后，第三轮托管验证通过","GitHub Actions",[
 ("检出固定提交","Windows runner 安装依赖，并记录环境和 Git SHA。"),
 ("冻结评测","复算 120 轮历史数据；负向输入应返回非零退出码。"),
 ("独立评分","运行 8 项 Demo Lab 评分检查。"),
 ("WASI 预热与回归","预热固定解释器后，168 项 Pytest 与 3 项 Node 测试通过。"),
 ("上传工件","保存环境、原始测试输出、JUnit 与离线评测 JSON。")],"证据   45992897616  /  000a19c  /  course-verification.yml")
series("architecture/14-team.svg","五个工作包共同负责一次课程交付","课程分工 · 计划责任各 20%",[
 ("WP01   陈帅廷","架构、入口与集成   ·   9 条岗位日志"),
 ("WP02   陈万策","需求、产品与前端   ·   10 条岗位日志"),
 ("WP03   赵君豪","测试生成、属性测试与评测   ·   11 条岗位日志"),
 ("WP04   马雪朋","质量、缺陷管理与同套件回归   ·   9 条岗位日志"),
 ("WP05   王选中","Skills、MCP、Hook、Reviewer 与交付   ·   10 条岗位日志")],
 "证据   0d9e893 协作验收及五份日志  /  实际操作按条目登记  /  本人核证待办")
marks=[]
for i,r in enumerate(metrics["offline"]):
    y=235+i*82
    marks.extend([label(62,y+32,r["group"]+"   "+r["label"],24),box(420,y,675,41,"#1f3548")])
    if r["killed"]:
        marks.append(box(420,y,675*r["killed"]/r["planned"],41,"#6cdedf"))
    marks.append(label(1120,y+31,r["killed"],30))
save("charts/10-offline.svg","四种生成策略的固定清单检出数","PHASE-05  /  每组 117 个位置",marks+[label(62,594,"A 组未形成可评分变异；按全清单检出数登记为 0。",22,"#c3d5e2")],"数据   frozen-evaluation.csv  /  offline-evaluation-hardened.json")
marks=[]
for i,(status,n) in enumerate(metrics["audit"].items()):
    y=226+i*82
    marks.extend([label(62,y+32,status,24),box(330,y,760,42,"#20394b"),box(330,y,760*n/64,42,"#75acc5"),label(1125,y+31,n,29)])
save("charts/15-outcomes.svg","历史验收的 64 个核查项","课程整改  /  0d9e893",marks+[label(62,612,"此图记录历史证据状态。新版材料复核结果见 FINAL_ACCEPTANCE_MATRIX.xlsx。",21,"#c3d5e2")],"数据   measurements.json  /  TP_COURSE_REMEDIATION_MATRIX.md")
series("architecture/05-ast-relations.svg","从语法树查到方法定义与局部调用","F02  /  telemetry.py",[
 ("输入","解析 telemetry.py 的源码文本。"),
 ("类型与方法","在图谱选择 Sample，再选中 normalized。"),
 ("图谱边","类包含方法；Inspector 展示源文件第 10–11 行。"),
 ("源码调用","SignalWindow.average 调用 mean_value(self.readings)。"),
 ("查证","点击源码检查对应行，分别判断包含关系和实际调用。")],
 "来源   eval/ast_visual/telemetry.py  /  真实 Edge 图谱与源码截图")
series("workflow/07-execution-flow.svg","一次失败怎样成为可以定位的记录","F04  /  PHASE-07 · Demo Lab",[
 ("绑定输入","以 v1 文件和套件 #1 创建运行 #1。"),
 ("受限执行","在 WASI CPython 中调用 Pytest。"),
 ("采集结果",f"通过 {metrics['v1']['passed']}，失败 {metrics['v1']['failed']}，耗时 {metrics['v1']['duration_ms']/1000:.3f} 秒。"),
 ("定位断言","1250 米应为 1.25 千米，v1 实际给出 1。"),
 ("保存证据","保留节点、运行日志和退出码，可供回归时核对。")],
 "来源   reports/phase07/edge-run.json  /  Demo Lab d564ee8f")
g=metrics["geometry"]
series("workflow/09-mutation-principle.svg","抑制一次异常，测试还能发现变化吗？","F13  /  geometry_calculator.area",[
 ("原版基线","先在原文件运行同一套件，确认可以比较。"),
 ("产生变异","第 8 行 SuppressRaise 将 raise ValueError 改为 pass。"),
 ("逐一执行","每个一阶变异用同一套件在受限运行器独立执行。"),
 ("本轮记录",f"{g['killed']} 杀死、{g['survived']} 存活、{g['execution_errors']} 执行错误。第 8 行变异存活。"),
 ("两种分母","全量 2/5 = 40%；有效 2/3 = 66.67%。")],
 "来源   reports/phase07/f13-geometry.json  /  本地模板测试套件")
