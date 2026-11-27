"""Create an editable course deck using the original presentation's layout and masters."""
from pathlib import Path
import base64
import json
import re
from xml.sax.saxutils import escape
from PIL import Image
from pptx import Presentation
from pptx.util import Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor

pack = Path(__file__).resolve().parents[1]
assets = pack / "05_DEMO_ASSETS"
out = pack / "06_PRESENTATION"
source = pack.parent / "TestPilot_AI_课程汇报.pptx"
slides = json.loads((pack/"source/slides.json").read_text(encoding="utf-8"))
metrics = json.loads((assets/"charts/measurements.json").read_text(encoding="utf-8"))
cues = json.loads((pack/"source/stage-cues.json").read_bytes())
if source.exists():
    deck = Presentation(source)
else:
    from io import BytesIO
    from zipfile import ZipFile
    with ZipFile(pack/"02_PROJECT_DOCUMENTS/repository/TestPilot-AI_cf448f3.zip") as snapshot:
        deck = Presentation(BytesIO(snapshot.read("TestPilot-AI/presentation/TestPilot_AI_课程汇报.pptx")))
for entry in list(deck.slides._sldIdLst):
    deck.part.drop_rel(entry.rId)
    deck.slides._sldIdLst.remove(entry)
layout = min(deck.slide_layouts, key=lambda item:len(item.placeholders))
u = deck.slide_width / 1280
v = deck.slide_height / 720
bg, panel, raised = "0D1824", "172A3B", "20394B"
white, soft, mute = "F2F7FC", "C3D5E2", "91B0C5"
cyan, purple, green, red = "6CDEDF", "C3A9FF", "83DEAA", "FF9F9B"
font = "Microsoft YaHei"
def rgb(code):
    return RGBColor.from_string(code)
def txt(x,y,w,h,value,size=25,color=white,bold=False,align="left",face=font):
    value=str(value)
    sh=slide.shapes.add_textbox(int(x*u),int(y*v),int(w*u),int(h*v))
    tf=sh.text_frame
    tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
    tf.word_wrap=False
    tf.vertical_anchor=MSO_ANCHOR.MIDDLE
    lines=value.split("\n")
    for i,line in enumerate(lines):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.alignment={"left":PP_ALIGN.LEFT,"center":PP_ALIGN.CENTER,"right":PP_ALIGN.RIGHT}[align]
        p.space_before=Pt(0)
        p.space_after=Pt(0)
        r=p.add_run()
        r.text=line
        r.font.name=face
        r.font.size=Pt(size*u/12700)
        r.font.bold=bold
        r.font.color.rgb=rgb(color)
        from pptx.oxml.xmlchemy import OxmlElement
        ea=OxmlElement("a:ea")
        ea.set("typeface",face)
        r._r.get_or_add_rPr().append(ea)
    x_anchor=x if align=="left" else x+w/2 if align=="center" else x+w
    anchor={"left":"start","center":"middle","right":"end"}[align]
    for i,line in enumerate(lines):
        t=y+h/2+(i-(len(lines)-1)/2)*size*1.23+size*.33
        svg.append(f'<text x="{x_anchor}" y="{t}" text-anchor="{anchor}" font-size="{size}" fill="#{color}" font-weight="{700 if bold else 400}" font-family="{face},sans-serif">{escape(line)}</text>')
def rect(x,y,w,h,color):
    sh=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,int(x*u),int(y*v),int(w*u),int(h*v))
    sh.fill.solid()
    sh.fill.fore_color.rgb=rgb(color)
    sh.line.fill.background()
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#{color}"/>')
def picture(name,x,y,w,h,caption):
    path=assets/"screenshots"/name
    with Image.open(path) as im:
        scale=min(w/im.width,h/im.height)
        iw,ih=im.width*scale,im.height*scale
    xx,yy=x+(w-iw)/2,y+(h-ih)/2
    slide.shapes.add_picture(str(path),int(xx*u),int(yy*v),int(iw*u),int(ih*v))
    enc=base64.b64encode(path.read_bytes()).decode()
    svg.append(f'<image x="{xx}" y="{yy}" width="{iw}" height="{ih}" href="data:image/png;base64,{enc}"/>')
    txt(x,y+h+4,w,26,caption,16,mute)
def band(x,y,w,title,detail,accent=cyan):
    rect(x,y,4,69,accent)
    txt(x+19,y-1,w-19,33,title,26,white,True)
    txt(x+19,y+37,w-19,28,detail,21,soft)
def steps(y,labels,subtitle=None):
    n=len(labels)
    gap=23
    width=(1168-gap*(n-1))/n
    for i,label in enumerate(labels):
        x=56+i*(width+gap)
        rect(x,y,width,70,panel)
        txt(x+4,y+5,width-8,60,label,24,white,True,"center")
        if i<n-1:
            txt(x+width,y+9,gap,50,"›",30,cyan,True,"center")
    if subtitle:
        txt(56,y+82,1168,35,subtitle,23,soft)
def asset(name,content=None):
    folder="architecture" if name.startswith(("03-","04-","05-","14-team")) else "charts" if name.startswith(("10-offline","14-score","15-outcomes")) else "workflow"
    elements=svg if content is None else content
    (assets/folder/name).write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720"><rect width="1280" height="720" fill="#'+bg+'"/>'+"".join(elements)+'</svg>',encoding="utf-8")
def subhead(x,y,title,w=600):
    txt(x,y,w,32,title,21,cyan,True)
def row(x,y,label,value,w=550):
    txt(x,y,128,39,label,19,mute)
    txt(x+134,y,w-134,39,value,22,white)
def stats(x,y,count,label,color):
    txt(x,y,165,93,count,70,color,True)
    txt(x,y+99,195,38,label,22,soft)
def write_chart():
    values=[a["killed"] for a in metrics["offline"]]
    labels=["A · 0.5B","B · 模板","C · 27B 初始","D · 27B 补测"]
    cd=CategoryChartData()
    cd.categories=labels
    cd.add_series("检出位置数",values)
    chart=slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,int(56*u),int(224*v),int(656*u),int(304*v),cd).chart
    chart.has_legend=False
    chart.has_title=False
    chart.chart_style=10
    from pptx.oxml import parse_xml
    chart._chartSpace.append(parse_xml(
        '<c:spPr xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<a:solidFill><a:srgbClr val="'+panel+'"/></a:solidFill><a:ln><a:noFill/></a:ln></c:spPr>'))
    chart.value_axis.minimum_scale=0
    chart.value_axis.maximum_scale=117
    chart.value_axis.major_unit=30
    for ax in (chart.category_axis,chart.value_axis):
        ax.tick_labels.font.size=Pt(12)
        ax.tick_labels.font.name=font
        ax.tick_labels.font.color.rgb=rgb(soft)
    chart.value_axis.has_major_gridlines=False
    s=chart.series[0]
    s.format.fill.solid()
    s.format.fill.fore_color.rgb=rgb(cyan)
    plot=chart.plots[0]
    plot.has_data_labels=True
    plot.data_labels.show_value=True
    plot.data_labels.position=XL_LABEL_POSITION.OUTSIDE_END
    plot.data_labels.font.size=Pt(14)
    plot.data_labels.font.color.rgb=rgb(white)
    for i,(label,value) in enumerate(zip(labels,values)):
        x=82+i*153
        h=222*value/117
        svg.append(f'<rect x="{x}" y="{490-h}" width="82" height="{h}" fill="#{cyan}"/><text x="{x+41}" y="{472-h}" fill="white" text-anchor="middle" font-size="25">{value}</text><text x="{x+41}" y="523" fill="#{soft}" text-anchor="middle" font-family="Microsoft YaHei,sans-serif" font-size="18">{label}</text>')
def description(i):
    return slides[i-1][5]

for index,m in enumerate(slides,1):
    title,section,citation,seconds,owner,notes,design,resources=m
    slide=deck.slides.add_slide(layout)
    for placeholder in list(slide.placeholders):
        el=placeholder._element
        el.getparent().remove(el)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb=rgb(bg)
    svg=[]
    if index>1:
        txt(56,29,1055,33,section,18,cyan,True)
        txt(56,76,1174,73,title,45,white,True)
        rect(56,163,1168,2,raised)
    slide.notes_slide.notes_text_frame.text=f"建议讲解 {seconds} 秒 · {owner}\n{notes}\n演示操作：{cues[index-1]['action']}\n来源：{citation}\n{cues[index-1]['evidence']}"
    txt(56,672,1100,28,citation,15,mute)
    txt(1165,670,59,30,f"{index:02d} / 15",16,mute,False,"right")
    if index==1:
        txt(56,44,1180,37,"软件工程课程项目   /   2026.11",22,cyan,True)
        txt(56,159,575,112,"TestPilot AI",83,white,True,face="Arial")
        txt(58,274,550,90,"AI-Powered Software Testing\nand Defect Detection Platform",33,soft,False,face="Arial")
        rect(58,428,68,4,cyan)
        txt(58,452,500,58,"从一条失败断言到修复回归",31,white,True)
        txt(58,565,560,42,"陈帅廷  ·  陈万策  ·  赵君豪  ·  马雪朋  ·  王选中",21,soft)
        picture("01-workbench.png",624,139,600,405,"Demo Lab   /   已归档 Edge 页面")
    elif index==2:
        subhead(56,201,"开发、测试与质量人员怎样交接？")
        steps(255,["读懂代码","编写用例","定位失败","修复回归","评估质量"])
        subhead(56,380,"三问访谈与规格确定了工作台要保留的证据")
        steps(433,["AST 与源码","测试套件","失败节点","同套件重跑","质量报告"])
        txt(56,561,1168,47,"验收条件     同一套件复跑   /   原失败节点通过   /   报告可按运行 ID 导出",25,cyan)
        asset("02-manual-and-workbench.svg")
    elif index==3:
        steps(242,["F01  导入","F02  分析","F03  生成","F04  执行","F05  回归","F06  报告"])
        rect(56,368,548,185,panel)
        subhead(78,392,"身份关联")
        txt(78,448,510,65,"项目 → 文件版本 → 套件 → 运行",28,white,True)
        rect(630,368,594,185,panel)
        subhead(655,392,"F13    变异测试")
        txt(655,444,553,77,"验证原版基线，逐个执行变异\n从存活位置回看测试盲区",25,white,True)
        asset("03-feature-map.svg")
    elif index==4:
        for k,(label,detail,clr) in enumerate([
            ("浏览器与入口","PyCharm → main.py → Uvicorn；同源 Jinja2 页面、静态资源和 JSON API",cyan),
            ("FastAPI 编排","app / workbench 注册路由；Demo Lab 按样本 ID 创建独立运行",cyan),
            ("分析与生成","analysis 解析 AST；generation 经 model_provider 调用回环 Ollama / Vulkan",purple),
            ("受限执行","runs / mutation_flow → runner → WASI CPython + Pytest",cyan),
            ("持久化与报告","SQLite 保存文件、套件、运行和缺陷；quality 读取快照并导出",cyan)]):
            y=187+88*k
            rect(56,y,226,67,raised)
            txt(70,y+2,198,63,label,24,clr,True)
            rect(286,y,938,67,panel)
            txt(302,y+3,907,60,detail,22,white)
        asset("04-system.svg")
    elif index==5:
        picture("05-ast.png",48,185,760,430,"真实 Edge 图谱   /   节点连线表示词法包含")
        subhead(840,207,"Inspector 与源码",374)
        txt(840,267,363,83,"Sample\n  ↳ normalized",31,white,True)
        txt(840,380,371,68,"选中方法即可查看\n限定名与第 10–11 行。",25,soft)
        rect(840,482,360,2,raised)
        txt(840,503,375,98,"源码中的局部调用\nSignalWindow.average()\n→ mean_value(self.readings)",22,cyan)
        asset("05-ast-code.svg")
    elif index==6:
        steps(193,["读取源码","识别测试场景","生成断言","静态检查","保存套件"])
        band(56,315,610,"历史真实 AI   /   PHASE-06",metrics["ai"]["model"],purple)
        txt(76,401,615,75,"Ollama / Vulkan → /api/files/1/suites\nHTTP 200     mode = ai",24,white)
        band(56,498,620,"现场单样本   /   PHASE-07","内存守卫中止源码理解，保留失败回执。",purple)
        live=json.loads((pack/"04_TESTING_EVIDENCE/AI_EVALUATION/reports/phase06/raw/live.json").read_bytes())
        suite=live["F03/suite"]["payload"]
        lines=[line.strip() for line in suite["source"].splitlines() if line.strip().startswith("assert ")]
        rect(676,298,548,278,panel)
        txt(697,316,504,44,"真实生成源码   /   bonus",24,purple,True)
        txt(697,374,499,110,"\n".join(lines[:3]),18,white,False,face="Consolas")
        txt(697,493,500,61,"原 API 回执保留完整测试套件。\n普通 F03 工作台截图归档为 template。",20,soft)
        asset("06-ai-generation.svg")
    elif index==7:
        p=metrics["v1"]
        subhead(56,206,"unit_scaling   /   原始 v1")
        stats(56,258,"1","用例总数",white)
        stats(263,258,str(p["failed"]),"失败",red)
        txt(56,417,610,55,"assert 1 == 1.25",34,red,True,face="Consolas")
        txt(56,490,615,106,f"通过 {p['passed']}   /   错误 {p['errors']}   /   跳过 {p['skipped']}\n运行 #{p['id']}   ·   {p['duration_ms']/1000:.3f} s   ·   退出码 {p['exit_code']}",23,soft)
        picture("07-pytest.png",649,204,575,349,"另一 F04 失败实录   /   可查看堆栈与日志")
        total=p["passed"]+p["failed"]+p["errors"]+p["skipped"]
        rect(56,607,390,12,raised)
        rect(56,607,390*p["failed"]/total,12,red)
        txt(460,593,175,40,f"失败 {p['failed']}/{total}",19,red)
        asset("07-execution.svg")
    elif index==8:
        evidence=pack/"04_TESTING_EVIDENCE/F05_AI_REPAIR/reports/TP-F05-AI-REPAIR-001"
        original=json.loads((evidence/"original.json").read_bytes())
        fixed=json.loads((evidence/"run.json").read_bytes())
        for x,title,code,r,identity,clr in [
            (56,"v1   原始缺陷","meters // 1000",original["run"]["result"],"文件 #16    ·    运行 #12",red),
            (654,"v2   已应用 AI 候选","meters / 1000",fixed,"文件 #17    ·    运行 #14",green)]:
            rect(x,205,570,274,panel)
            txt(x+23,224,520,48,title,27,clr,True)
            txt(x+23,291,520,57,code,38,white,True,face="Consolas")
            txt(x+23,361,520,48,f"{r['passed']} 通过     {r['failed']} 失败     {r['skipped']} 跳过",27,white,True)
            txt(x+23,418,520,40,identity+"    ·    套件 #8",21,soft)
        txt(56,507,1170,55,"Qwen 提出差异   →   操作者审阅并应用   →   WASI 执行原套件",28,cyan,True)
        txt(56,573,1170,43,"两次均跳过同一属性测试。另有 4 项数值检查通过，单独计数。",21,soft)
        asset("08-regression.svg")
    elif index==9:
        g=metrics["geometry"]
        subhead(56,197,"geometry_calculator.area   /   本地模板")
        txt(56,250,552,72,f"{g['killed']} 杀死     {g['survived']} 存活     {g['execution_errors']} 执行错误",27,white,True)
        band(56,349,540,"全量得分     2 / 5 = 40%","分母包含登记的全部变异。")
        band(56,465,540,"有效得分     2 / 3 = 66.67%","分母扣除 2 个执行错误。")
        picture("09-mutant.png",625,225,599,337,"Edge 展开第 8 行存活变异的真实截图")
        txt(56,593,1170,42,"第 8 行   SuppressRaise    ·    raise ValueError(…)  →  pass    ·    同一套件仍通过",22,cyan)
        asset("09-mutation.svg")
    elif index==10:
        subhead(56,183,"固定清单检出数   /   各组 117 个登记位置")
        write_chart()
        txt(56,548,683,60,"10 个项目 × 3 个种子 × 4 组 = 120 轮\nA 组 117 个位置均无可评分结果。",20,soft)
        subhead(751,183,"托管 Windows CI",450)
        for i,(top,bottom) in enumerate([("01   冻结复算","核对模型、种子、清单与负向退出"),("02   实跑工程测试","168 Pytest + 3 Node；另 8 项评分"),("03   归档成功与失败","前两轮冷启动超时，预热后第三轮通过")]):
            band(751,253+i*112,471,top,bottom)
        asset("10-ci.svg")
        asset("10-offline.svg")
    elif index==11:
        for x,lab,cells,accent in [(56,"模型输出的参数形状",["冻结字段 0/10 符合","输出对象，规则期待三元素数组","在 Schema 中约束形状并限次重试","后续真实模型参数 10/10"],purple),
                                  (654,"变异定位越过运算符",["is → is not 的定位被拒","相同前缀延伸到算子以后","按运算符锚定并精确回放","8 项定位／清单用例通过"],cyan)]:
            rect(x,205,570,352,panel)
            txt(x+20,222,529,61,lab,30,accent,True)
            for i,(k,val) in enumerate(zip(["现象","根因","修复","回归"],cells)):
                y=302+i*56
                txt(x+20,y,69,38,k,20,mute)
                txt(x+89,y,468,38,val,23,white)
        txt(56,577,1165,51,"两案复验前分别记录假设，定向共 9 项通过。原开发同期假设仍缺。",23,soft)
        asset("11-bug-cases.svg")
    elif index==12:
        steps(190,["导入 v1","选目标","套件 #1","运行 #1","v2 回归 #2","导出报告"])
        picture("12-report.png",56,293,570,279,"Demo Lab 报告中心   /   可按运行重读")
        band(667,313,550,"课堂样本   /   unit_scaling","导出报告绑定同一演示 ID。")
        band(667,430,550,"质量快照   /   F06","按运行复核用例、缺陷和行覆盖。")
        txt(667,540,560,72,"v2 覆盖 3 / 4 行   ·   原节点通过\n完整 JSON 可与 GET 返回值核对。",21,soft)
        asset("12-closed-loop.svg")
    elif index==13:
        subhead(56,196,"产品证据")
        subhead(673,196,"工程实践",540)
        for x,rows in [(56,[("AST 图谱","节点关联源码行"),("本地 AI","套件记录模式与断言"),("WASI","受限执行并留存日志"),("回归","原套件比较两版结果"),("变异测试","存活位置揭示断言盲区"),("质量报告","按运行 ID 读取、导出")]),
                        (673,[("两项 Skills","verify / testpilot-workflow"),("MCP","只读工具查 SQLite 证据"),("Hook","提交前检查暂存差异"),("Subagent","Reviewer 指出身份校验缺口"),("Goal","失败后改查种子漂移")])]:
            for k,(a,b) in enumerate(rows):
                y=251+k*57
                rect(x,y,142,44,raised)
                txt(x+8,y,129,44,a,21,cyan,True)
                txt(x+156,y,390,44,b,22,white)
        asset("13-toolchain.svg")
    elif index==14:
        subhead(56,194,"教师评分   /   100 分 + 加分上限 5")
        dimensions=[("需求与上下文",20,"规格与三问访谈"),("扩展运用",5,"两项 Skill、MCP、Hook"),("测试与验证",15,"CI、属性与冻结评测"),("调试与解决",10,"两份 Bug 档案"),("协作与反思",10,"五份日志、核证单"),("产品结果",20,"Edge 实录与导出报告"),("汇报与答辩",20,"逐页讲稿与备用录屏")]
        for k,(label,points,proof) in enumerate(dimensions):
            y=246+k*47
            txt(56,y,163,39,label,22,white)
            txt(223,y,68,39,f"{points} 分",21,cyan,True)
            txt(315,y,294,39,proof,20,soft)
        subhead(626,194,"责任分工   /   各 20%",500)
        for k,(owner,task,count) in enumerate([("陈帅廷","架构与集成",9),("陈万策","需求与前端",10),("赵君豪","生成与评测",11),("马雪朋","质量与回归",9),("王选中","工具链与交付",10)]):
            txt(626,249+k*55,590,38,f"WP0{k+1}   {owner}     {task}     {count} 条",22,white)
        txt(626,543,592,80,"49 条岗位日志可追溯；本人核证待登记。\n答辩系数 0.8–1.2 由教师核定。",21,soft)
        asset("14-team.svg")
        asset("14-score.svg")
    elif index==15:
        txt(56,218,1167,100,"一次失败，留下两次可复核的运行。",45,white,True)
        txt(56,339,1164,71,"复盘：固定套件和版本，才能判断修复效果；跳过项要留在报告里。",28,soft)
        rect(56,449,1168,2,raised)
        subhead(56,477,"演示入口")
        txt(56,523,575,78,"telemetry.py → unit_scaling\n→ geometry_calculator → F06 导出",24,cyan)
        subhead(678,477,"答辩准备",540)
        txt(678,523,544,78,"答辩机模型与异机启动待复验；\n五人核证、历史会话覆盖及联排待办。",23,soft)
        asset("15-outcomes.svg")

deck.core_properties.title="TestPilot AI 课程最终汇报"
deck.core_properties.author="Codex"
deck.save(out/"TestPilot_AI_正式汇报.pptx")
def md(name,body):
    (out/name).write_text(body+"\n",encoding="utf-8")
md("SPEAKER_NOTES.md","# 逐页讲稿\n\n"+"\n\n".join(f"## P{i:02} {m[0]}\n\n{m[4]} · {m[3]} 秒\n\n{m[5]}\n\n演示操作　{cues[i-1]['action']}\n\n[打开对应证据]({cues[i-1]['evidence']})" for i,m in enumerate(slides,1)))
md("VISUAL_DESIGN_SPEC.md","# 逐页视觉设计\n\n16:9，深蓝底色 #0D1824，青色标注流程，紫色标注模型，绿色与红色用于实测成功与失败。中文使用微软雅黑。图形、文字和统计图在 PPTX 内可编辑，截图保留原 PNG；SVG 为可单独打开的素材。\n\n"+"\n\n".join(f"## P{i:02} {m[0]}\n\n{m[6]}\n\n素材　{m[7]}\n\n[来源及核对位置]({cues[i-1]['evidence']})" for i,m in enumerate(slides,1)))
