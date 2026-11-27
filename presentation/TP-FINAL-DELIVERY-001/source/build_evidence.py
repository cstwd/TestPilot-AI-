"""Build the course evidence package from immutable Git blobs and checked receipts."""
import csv
import hashlib
import json
import posixpath
import re
import subprocess
from collections import Counter
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[3]
PACK = Path(__file__).resolve().parents[1]
AUDIT = "0d9e893"
PRODUCT = "039b14d"
REMED = "reports/TP-COURSE-REMEDIATION-001/"
CI_RUN = "45992897616"

def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)

def blob(ref, path):
    return git("show", f"{ref}:{path}")

def save(path, content):
    target = PACK / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
    return target

def repo_link(path, label=None):
    return f"[{label or path}](../../../{path})"

def read_json(ref, path):
    return json.loads(blob(ref, path))

matrix_path = "reports/TP_COURSE_REMEDIATION_MATRIX.md"
previous = [
    [value.strip() for value in line.strip("|").split("|")]
    for line in blob(AUDIT, matrix_path).decode().splitlines()
    if re.match(r"^\| [A-I R]\d", line)
]
assert len(previous) == 64 and Counter(row[3] for row in previous) == {
    "PASS": 44, "PARTIAL": 17, "MISSING": 1, "UNVERIFIED": 2,
}
area = {
    "A":"选题与里程碑", "B":"需求与上下文", "C":"可选工程扩展",
    "D":"测试与验证（评分维度）", "E":"缺陷档案", "F":"协作日志",
    "G":"产品结果", "H":"汇报与答辩", "I":"可选加分", "R":"课程来源及专项复核",
}
updates = {
    "A01":("PASS","原图 1 已按原始字节恢复并复核。",""),
    "H01":("PASS","正式幻灯片与讲稿 P01–P04、P12、P14 交代用户、问题、架构和可观测验收。","课堂实际讲解见 H05。"),
    "H02":("PASS","P13 及演讲备注覆盖两项 Skills、MCP、Hook、Reviewer 和有失败反馈的 Goal；对应回执入包。","实际讲解待联排。"),
    "H04":("PASS","P11 双案与 P14 五岗各有证据，逐页讲稿和五份岗位日志提供复盘材料。","个人答辩、本人反思与签收待核。"),
    "H05":("PARTIAL","本轮附五人建议分段、现场操作和备份视频。","全员联排、答辩及现场模型通过待核。"),
    "R01":("PASS","用户确认五张图即完整教师原件。五份 SHA-256 全部匹配，重新核对 100 分、+5 和选做项。",""),
    "R03":("PASS","已打包仓库快照、个人日志及可编辑正式幻灯片，仓库快照保留既有课程汇报。","组长按教师提交渠道递交。"),
    "G03":("PARTIAL","历史 PHASE-06 AI HTTP 200；PHASE-07 单样本触发 2 GiB 资源保护。","在满足资源条件的答辩机上单样本复验。"),
    "G08":("PARTIAL","PHASE-07 最近展示验证仍无 AI 套件或 WASI 执行，保留失败报告。","在答辩机上用原守卫复验。"),
}
scoring = [
 ("S1","评分维度","需求与上下文工程",20,"可测 SPEC、精简上下文与目标／范围／标准明确的 Prompt","PARTIAL","B1.1–B3.2","部分历史 Prompt 版本及关键输出链待补"),
 ("S2","评分维度","扩展的运用",5,"说明 Skills、MCP、Hooks、子智能体实际收益或必要性","PASS","C1.1–C5.2","Claude 客户端实际调用仍未验证，独立 stdio 有实证"),
 ("S3","评分维度","测试与验证体系",15,"有多层验证，真实检出问题，保留完整证据链","PASS","D1.1–D6.2","最新 AI 盲测未形成额外指标"),
 ("S4","评分维度","调试与问题解决",10,"Bug 档案完整，定位根因并留回归","PASS","E01–E03","两案原开发同期假设仍缺，保留本轮历史复验前假设"),
 ("S5","评分维度","协作日志与反思",10,"真实具体，与 Git 一致，有失败及反思","PARTIAL","F01–F06","本人核证及关键历史会话材料"),
 ("S6","评分维度","产品结果",20,"核心功能可用，README 支持他人独立启动","PARTIAL","A04、G01–G09","他人异机启动及现场模型复验"),
 ("S7","评分维度","汇报与答辩",20,"讲清过程，每位成员说明本人负责部分","PARTIAL","H01–H05、R04","全员联排和实际答辩待核"),
 ("S8","可选加分","可复用 Skill 包、交叉红队、自建 MCP",5,"教师统一列 +5，未说明子项分值","PARTIAL","I01–I03","有自建 MCP 实证，外部 Skill 包及跨组回执待补"),
]
audit_files = [f"reports/TP_COURSE_{name}.md" for name in (
 "FINAL_ACCEPTANCE","REMEDIATION_MATRIX","REMEDIATION_REPORT","CI_ACCEPTANCE",
 "COLLAB_ACCEPTANCE","DEMO_ACCEPTANCE","BUG_ARCHIVE_AUDIT","LOOP_EVIDENCE")]
archives = [
 (AUDIT,"07_FINAL_REPORT/historical",audit_files),
 (AUDIT,"04_TESTING_EVIDENCE/CI", [".github/workflows/course-verification.yml"]+
   [p for p in git("ls-tree","-r","--name-only",AUDIT,REMED+"ci-github").decode().splitlines()]),
 (AUDIT,"04_TESTING_EVIDENCE/AUTOMATED_TESTING",[REMED+n for n in (
  "local-full.txt","local-targeted.txt","local-affected-regression.txt","wasi-cold-warmup.json")]+
  ["reports/course-final/toolchain.txt","reports/course-final/REVIEWER.md","tests/test_course_properties.py",
   "tests/test_wp09_integration.py","demo/TestPilot-Demo-Lab/evaluation/evaluator.py"]),
 (PRODUCT,"04_TESTING_EVIDENCE/AUTOMATED_TESTING",["reports/phase07/verify-full.txt","reports/phase07/failure-paths.json"]),
 (AUDIT,"04_TESTING_EVIDENCE/AI_EVALUATION",[REMED+n for n in (
  "offline-evaluation-hardened.json","offline-failure.json","ci-independent-review.json",
  "goal-receipts.json","goal-complete.json","loop-prompt-1.txt","loop-response-1.json","demo-model-live.json")]+
  ["eval/phase05/PROTOCOL.md","eval/phase05/frozen.json","eval/phase05/verify_frozen.py",
   "reports/phase06/E2E.md","reports/phase06/raw/live.json"]),
 (PRODUCT,"04_TESTING_EVIDENCE/AI_EVALUATION",["reports/phase07/ai-live.json"]),
 (AUDIT,"04_TESTING_EVIDENCE/BUG_CASES",["collab-log/bugs/TP-MODEL-SCHEMA.md","collab-log/bugs/TP-F13-IS-NOT.md",
  REMED+"bug-precheck.md",REMED+"bug-replay.json"]),
 (PRODUCT,"04_TESTING_EVIDENCE/MUTATION_TESTING",["reports/phase07/f13-geometry.json",
  "reports/phase07/edge-run.json","reports/phase07/end-to-end.json","reports/phase07/ACCEPTANCE.md",
  "reports/phase07/f13-view-check.txt"]),
 (AUDIT,"03_TEAM_COLLABORATION/raw",["collab-log/LOG.md","collab-log/member_contributions.md",
  "collab-log/transcripts/README.md","collab-log/transcripts/TP-COURSE-REMEDIATION-001-claude-attempt.txt",
  "collab-log/transcripts/WP03-DEMO-LAB-001-original-prompt.txt",
  "collab-log/transcripts/WP09-001-original-prompt.txt",REMED+"export-terminal.json",
  REMED+"member-verification-recovered.txt","transcripts/requirements-interview.md"]),
 (AUDIT,"02_PROJECT_DOCUMENTS/raw",["mcp-server/server.py","hooks/verify.py","docs/COURSE_TESTING.md","reports/course-final/TOOLCHAIN.md","reports/course-final/skill-definitions.txt","README.md","AGENTS.md","docs/SPEC.md","docs/FEATURE_MAP.md",
  "docs/ARCHITECTURE.md","docs/COURSE_EVIDENCE_INDEX.md","docs/COURSE_REQUIREMENTS_AUDIT.md",
  ".claude/skills/verify/SKILL.md",".claude/skills/testpilot-workflow/SKILL.md",".claude/agents/testpilot-reviewer.md",
  ".mcp.json","hooks/pre-commit"]),
 (PRODUCT,"05_DEMO_ASSETS/code_samples",["eval/ast_visual/telemetry.py",
  "demo/TestPilot-Demo-Lab/source/buggy/unit_scaling.py","demo/TestPilot-Demo-Lab/reference/corrected/unit_scaling.py",
  "demo/TestPilot-Demo-Lab/source/good/calculator.py",
  "demo/TestPilot-Demo-Lab/source/challenge/booking_timezones.py"]),
 (AUDIT,"04_TESTING_EVIDENCE/AI_EVALUATION",[REMED+"run-loop-round.ps1", REMED+"demo-provider-recovery.txt"]),
 (PRODUCT,"06_PRESENTATION/assets",["presentation/TestPilot_AI_备用演示.mp4",
  "reports/course-final/video-probe.json","reports/WP03-AST-VISUAL-REFINE-001/video/analysis-session.mp4"]),
]
screens = {
 "01-workbench.png":"reports/phase07/01-source-and-filters.png",
 "05-ast.png":"reports/WP03-AST-VISUAL-REFINE-001/screenshots/07-replay-complete.png",
 "05-ast-source.png":"reports/WP03-AST-VISUAL-REFINE-001/screenshots/05-source.png",
 "06-template.png":"reports/WP05-F03-001/screenshots/desktop-passed.png",
 "07-pytest.png":"reports/WP06-F04-001/screenshots/desktop-failed.png",
 "08-regression.png":"reports/phase07/02-regression-and-mutation.png",
 "09-mutant.png":"reports/phase07/05-f13-surviving-mutant.png",
 "12-report.png":"reports/phase07/04-report-center.png",
 "12-f06.png":"reports/WP08-F06-001/screenshots/desktop-html-report.png",
}

from functools import lru_cache
@lru_cache(maxsize=None)
def revision_sha(ref):
    return git("rev-parse",ref).decode().strip()

records = []
def archive(ref, source, target):
    data = blob(ref, source)
    save(target, data)
    records.append((target,revision_sha(ref),source,hashlib.sha256(data).hexdigest()))

repair_dir = "reports/TP-F05-AI-REPAIR-001"
repair_paths = git("ls-tree","-r","--name-only","d8226c3",repair_dir).decode().splitlines()
archives.append(("d8226c3","04_TESTING_EVIDENCE/F05_AI_REPAIR",[x for x in repair_paths if not x.endswith(".gitattributes")]))
for ref, folder, paths in archives:
    for path in paths:
        archive(ref,path,f"{folder}/{path}")
for revision in ("8038be2","097358b","4b1b574"):
    archive(revision,"AGENTS.md",f"02_PROJECT_DOCUMENTS/context_history/AGENTS-{revision}.md")
for name, path in screens.items():
    archive(PRODUCT,path,f"05_DEMO_ASSETS/screenshots/{name}")

members = [
 ("WP01","陈帅廷",9,"总体架构、入口与本机模型","8038be2、646ef7d","P01–P04"),
 ("WP02","陈万策",10,"需求与前端工作台","9f048d0、d872fa1","P05–P06"),
 ("WP03","赵君豪",11,"AST、生成、测试与冻结评测","743e24f、f563c6d","P07、P10"),
 ("WP04","马雪朋",9,"WASI、缺陷、回归与变异","d988ecc、b6f4ef5、5b757b9","P08–P09、P11–P12"),
 ("WP05","王选中",10,"Agent 工具链、CI 与交付","4b1b574、000a19c、6480e27","P13–P15"),
]
team = []
for wp,name,count,work,commits,pages in members:
    folder=f"03_TEAM_COLLABORATION/WP01-WP05/{wp}"
    log=f"collab-log/members/{name}_{wp}_个人操作日志.md"
    archive(AUDIT,log,f"{folder}/{log}")
    archive("cf448f3",log,f"03_TEAM_COLLABORATION/weekly/{log}")
    archive(AUDIT,f"docs/work-packages/{wp}.md",f"{folder}/docs/work-packages/{wp}.md")
    save(f"{folder}/README.md",f"# {wp} {name}\n\n职责为{work}，计划份额 20%，已有 {count} 条按岗归档记录。\n\n"
          f"代表提交 `{commits}`。请核对[原工作包](docs/work-packages/{wp}.md)与[逐条日志]({log})中的输入、产物、实际操作者、验收证据及 Git。\n")
    save(f"03_TEAM_COLLABORATION/MEMBER_CONFIRMATION/{wp}-{name}.md",f"# {wp} {name} 本人核证单\n\n"
         f"状态 **待本人填写**。请阅读 [岗位日志](../WP01-WP05/{wp}/{log})并按可核实的事实填写。\n\n"
         "- 本人实际操作的日期、任务和条目编号　________\n"
         "- 可核对链接、Git、原始会话或运行回执　________\n"
         "- Codex 代办内容及本人实际复核内容　________\n"
         "- 与现有记录有差异的条目及更正依据　________\n"
         "- 本人签名及日期　________\n- 组长复核及日期　________\n")
    team.append(f"| {wp} | {name} | {work} | 20% | {count} | `{commits}` | {pages} |")
save("03_TEAM_COLLABORATION/TEAM_CONTRIBUTION_MATRIX.md","# 团队职责与答辩分段\n\n"
     "| WP | 责任人 | 课程职责 | 计划份额 | 日志条数 | 代表 Git | 建议讲解 |\n|---|---|---|---:|---:|---|---|\n"+
     "\n".join(team)+"\n| 合计 | 五人 | 陈帅廷协调 | 100% | 49 | | |\n\n"
     "日志校验为证据、Git、验收各 49/49、原始 Prompt 48/49。历史实际操作者按原日志记录。教师按答辩讲解核定 0.8–1.2，个人核证单均为空白待本人填写。\n")

edge=read_json(PRODUCT,"reports/phase07/edge-run.json")
geom=read_json(PRODUCT,"reports/phase07/f13-geometry.json")
ai=read_json(PRODUCT,"reports/phase06/raw/live.json")
phase_ci=read_json(AUDIT,REMED+f"ci-github/{CI_RUN}/receipt.json")
offline=read_json(AUDIT,REMED+"offline-evaluation-hardened.json")
assert phase_ci["run"]["conclusion"]=="success" and phase_ci["run"]["head_sha"].startswith("000a19c")
assert ai["F03/suite"]["http"]==200 and ai["F03/suite"]["payload"]["mode"]=="ai"
assert edge["execution"]["suite_id"]==edge["regression"]["suite_id"]==edge["suite"]["id"]
def run(which):
    return {k:edge[which][k] for k in ("id","file_id","suite_id","status","passed","failed","errors",
             "skipped","duration_ms","exit_code","covered_lines","total_lines")}

mut=geom["mutation"]
data = {"audit":dict(Counter(r[3] for r in previous)),"lab_id":edge["id"],"target":edge["suite"]["target"],
 "v1":run("execution"),"v2":run("regression"),"geometry_lab_id":geom["id"],"geometry_session":mut["result"]["id"],
 "geometry":{"killed":mut["effective"]["killed"],"effective_n":mut["effective"]["denominator"],
             "effective_score":mut["effective"]["score_pct"],"all_score":mut["all_score_pct"],
             "survived":len(mut["survivors"]),"total":mut["result"]["before"]["total"],
             "execution_errors":mut["result"]["before"]["execution_error"]},
 "offline":[{"group":k,"label":v["label"],"planned":v["planned"],"killed":v["killed"],
             "detect":v["all_manifest_detection"],"unscored":v["noscored"]} for k,v in offline["groups"].items()],
 "ai":{"model":ai["model"]["payload"]["model"],"path":ai["F03/suite"]["path"],
       "http":ai["F03/suite"]["http"],"mode":ai["F03/suite"]["payload"]["mode"]}}
assert [x["killed"] for x in data["offline"]]==[0,81,104,105]
assert data["geometry"]["total"]==5
save("05_DEMO_ASSETS/charts/measurements.json",json.dumps(data,indent=2,ensure_ascii=False)+"\n")
with (PACK/"05_DEMO_ASSETS/charts/frozen-evaluation.csv").open("w",encoding="utf-8-sig",newline="") as stream:
    writer=csv.DictWriter(stream,fieldnames=list(data["offline"][0]))
    writer.writeheader()
    writer.writerows(data["offline"])

def workbook(name,tabs):
    wb=Workbook()
    wb.remove(wb.active)
    for title,headers,rows,widths in tabs:
        ws=wb.create_sheet(title)
        ws.append(headers)
        for row in rows:
            ws.append(row)
        ws.freeze_panes="C2"
        ws.auto_filter.ref=ws.dimensions
        ws.sheet_view.showGridLines=False
        for i,w in enumerate(widths,1):
            ws.column_dimensions[get_column_letter(i)].width=w
        for row in ws.iter_rows():
            for c in row:
                c.alignment=Alignment(wrap_text=True,vertical="center")
                colors={"PASS":"D8F3E8","PARTIAL":"FFF1CD","MISSING":"FCE0DE","UNVERIFIED":"E7EAF0"}
                if c.row==1:
                    c.fill=PatternFill("solid",fgColor="11263D")
                    c.font=Font(name="Microsoft YaHei",color="FFFFFF",bold=True,size=11)
                else:
                    c.fill=PatternFill("solid",fgColor=colors.get(str(c.value),"EBF3F9" if c.row%2==0 else "FFFFFF"))
                    c.font=Font(name="Microsoft YaHei",color="14283D",size=10)
            longest=max(len(str(c.value or "")) / max(widths[c.column-1]/2,4) for c in row)
            ws.row_dimensions[row[0].row].height=max(29,16*(int(longest)+1))
        ws.print_title_rows="1:1"
    wb.save(PACK/name)

overview_headers=["编号","类别","教师维度","满分","教师要求","证据状态","映射核查项","余项"]
totals=[("","合计","基础评分","=SUM(D2:D8)","教师给分另行登记","","",""),
        ("","合计","含加分最高","=SUM(D2:D9)","个人成绩＝小组成绩 × 个人贡献系数","","","")]
width=[10,18,25,12,52,14,19,46]
detail=[]
for ident,standard,old,base,observed,evidence in previous:
    new,added,remaining=updates.get(ident,(base,"","见历史观察及待确认清单" if base!="PASS" else ""))
    detail.append((ident,area[ident[0]],standard,old,base,new,observed,added,evidence,remaining))
current=Counter(row[5] for row in detail)
totals_by_status=[(x,Counter(r[3] for r in previous)[x],current[x]) for x in ("PASS","PARTIAL","MISSING","UNVERIFIED")]
summ=[("0d9e893 历史课程终验","64 项课程核查","历史课程报告 NOT_READY"),
 ("039b14d 本机产品证据","PHASE-07 真实 Edge 和本机回归","独立于托管 CI"),
 ("000a19c 托管 CI",CI_RUN,"168 Pytest、3 Node、8 Demo Lab 评分；成功"),
 ("本轮课程材料复核","新增正式汇报与讲稿，H01、H02、H04 的材料覆盖更新为 PASS","本人核证、关键历史 /export、异机与联排仍待办")]
workbook("01_TEACHER_REQUIREMENTS/SCORING_MATRIX.xlsx",[("教师评分",overview_headers,scoring+totals,width),
 ("使用说明",["项目","判读"],[("来源","教师原图 3 满分，原图 4 红蓝标注确定必做与可选。"),
   ("状态","证据覆盖状态。无自评得分。"),("个人系数","教师根据答辩个人讲解核定，范围 0.8–1.2。")],[25,76])])
workbook("07_FINAL_REPORT/FINAL_ACCEPTANCE_MATRIX.xlsx",[
 ("64项验收",["编号","类别","核查项","初轮","历史二轮","当前材料","历史观察","新增证据","历史证据","待办"],
  detail,[12,23,35,15,15,15,62,52,48,48]),
 ("验收摘要",["状态","历史二轮","当前材料"],totals_by_status,[25,20,20]),
 ("验收口径",["基线","范围","观察"],summ,[37,41,73])])
head="| ID | 类别 | 教师要求或拆解核查点 | 上轮状态 | 当前材料 | 成果与证据 | 余项 |\n|---|---|---|---|---|---|---|"
def cell(s):
    return str(s).replace("|","\\|").replace("\n"," ")
def local_evidence_links(match):
    caption,relative=match.groups()
    source=posixpath.normpath(posixpath.join("reports",relative))
    target=next((row[0] for row in records if row[2]==source),None)
    if not target:
        raise ValueError("Missing evidence target "+source)
    return "["+caption+"]("+posixpath.relpath(target,"01_TEACHER_REQUIREMENTS")+")"
md_rows=["| "+" | ".join(map(cell,(ident,cat,std,hist,now," ".join((old_obs,new_obs,evidence)),remain)))+" |"
         for ident,cat,std,_,hist,now,old_obs,new_obs,evidence,remain in detail]
save("01_TEACHER_REQUIREMENTS/REQUIREMENT_EVIDENCE_MAP.md","# 教师要求、产品与证据对照\n\n"
     "64 个核查点沿用整改矩阵，第 H 组对应本包正式幻灯片、逐页讲稿及现场演示手册。E 编号由证据索引定位；历史报告链接以原提交路径解释。\n\n"
     "[历史矩阵](../07_FINAL_REPORT/historical/reports/TP_COURSE_REMEDIATION_MATRIX.md) · "
     "[E 证据与功能索引](../04_TESTING_EVIDENCE/README.md) · [本轮验收表](../07_FINAL_REPORT/FINAL_ACCEPTANCE_MATRIX.xlsx)\n\n"+
     head+"\n"+re.sub(r"\[([^\]]+)\]\(([^)]+)\)",local_evidence_links,"\n".join(md_rows))+"\n")
with (PACK/"07_FINAL_REPORT/COPIED_EVIDENCE.csv").open("w",encoding="utf-8-sig",newline="") as stream:
    writer=csv.writer(stream)
    writer.writerow(("交付路径","Git SHA","仓库原路径","SHA-256"))
    writer.writerows(records)
