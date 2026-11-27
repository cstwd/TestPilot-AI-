"""Check all course sources, then optionally seal and reread the delivery ZIP."""
import argparse
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from xml.etree import ElementTree
from urllib.parse import unquote
from PIL import Image
from openpyxl import load_workbook

pack=Path(__file__).resolve().parents[1]
repo=pack.parents[1]
distribution=pack.with_name(pack.name+"_完整汇报包.zip")
manifest=pack/"07_FINAL_REPORT/FILE_MANIFEST.csv"
report=pack/"07_FINAL_REPORT/verification.json"
def sha(b):
    return hashlib.sha256(b).hexdigest()
def read(path):
    return (pack/path).read_bytes()
def rows(path):
    with (pack/path).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.reader(f))
def git(*args):
    return subprocess.check_output(["git",*args],cwd=repo)
def blob_sha(b):
    return hashlib.sha1(f"blob {len(b)}\0".encode()+b).hexdigest()
def tracked_snapshot():
    revision=git("rev-parse","cf448f3").decode().strip()
    entries=git("ls-tree","-rz",revision).split(b"\0")
    expected={}
    for item in entries:
        if item:
            head,path=item.split(b"\t",1)
            expected["TestPilot-AI/"+path.decode()]=head.split()[2].decode()
    with ZipFile(pack/"02_PROJECT_DOCUMENTS/repository/TestPilot-AI_cf448f3.zip") as archive:
        assert archive.comment.decode()==revision
        files=[e for e in archive.infolist() if not e.is_dir()]
        assert set(expected)=={e.filename for e in files}
        for item in files:
            assert blob_sha(archive.read(item))==expected[item.filename], item.filename
    return len(expected)

def check_slides():
    from io import BytesIO
    from pptx import Presentation
    from pypdf import PdfReader

    folder=pack/"06_PRESENTATION"
    ppt=folder/"TestPilot_AI_正式汇报.pptx"
    deck=Presentation(ppt)
    pdf=PdfReader(folder/"TestPilot_AI_正式汇报.pdf")
    seeds=json.loads(read("source/slides.json"))
    cues=json.loads(read("source/stage-cues.json"))
    qa=json.loads(read("07_FINAL_REPORT/powerpoint-qa.json"))
    assert qa["slides"]==len(deck.slides)==len(pdf.pages)==len(seeds)==len(cues)==15
    assert qa["renderer"]=="Microsoft PowerPoint" and qa["overflow_candidates"]==[]
    assert abs(deck.slide_width/deck.slide_height-16/9)<0.001
    notes=read("06_PRESENTATION/SPEAKER_NOTES.md").decode()
    design=read("06_PRESENTATION/VISUAL_DESIGN_SPEC.md").decode()
    texts=[]
    for index,(slide,page,seed,cue) in enumerate(zip(deck.slides,pdf.pages,seeds,cues),1):
        raw=" ".join(shape.text for shape in slide.shapes if shape.has_text_frame)
        texts.append(raw)
        assert seed[0] in raw and seed[0] in design and seed[0] in notes, index
        assert cue["action"] in slide.notes_slide.notes_text_frame.text and cue["action"] in notes,index
        assert (folder/cue["evidence"]).is_file(),cue
        assert abs(float(page.mediabox.width)/float(page.mediabox.height)-16/9)<0.001
        flattened=lambda value: "".join(value.split())
        assert flattened(seed[0]) in flattened(page.extract_text()),index
        with Image.open(pack/f"07_FINAL_REPORT/previews/P{index:02}.png") as preview:
            assert preview.size==(1280,720)
    raw_dir=pack/"04_TESTING_EVIDENCE/F05_AI_REPAIR/reports/TP-F05-AI-REPAIR-001"
    original=json.loads((raw_dir/"original.json").read_bytes())
    repair=json.loads((raw_dir/"repair.json").read_bytes())
    fixed=json.loads((raw_dir/"run.json").read_bytes())
    assert original["run"]["suite_id"]==repair["suite_id"]==8
    assert original["run"]["id"]==repair["original_run_id"]==12 and repair["applied_file_id"]==17
    for result in (original["run"]["result"],fixed):
        assert f"{result['passed']} 通过     {result['failed']} 失败     {result['skipped']} 跳过" in texts[7]
    chart=next(shape.chart for shape in deck.slides[9].shapes if shape.has_chart)
    values=[int(row[3]) for row in rows("05_DEMO_ASSETS/charts/frozen-evaluation.csv")[1:]]
    assert list(chart.series[0].values)==values==[0,81,104,105]
    with ZipFile(ppt) as archive:
        embedded=next(n for n in archive.namelist() if n.startswith("ppt/embeddings/") and n.endswith(".xlsx"))
        book=load_workbook(BytesIO(archive.read(embedded)),read_only=True)
        assert [r[1] for r in list(book.active.values)[1:]]==values
        book.close()
    for suffix in (".pptx",".pdf"):
        old="presentation/TestPilot_AI_课程汇报"+suffix
        assert git("show","039b14d:"+old)==(repo/old).read_bytes()
    return dict(pptx_slides=15,pdf_pages=15,notes_and_stage_cues=15,editable_chart_values=values,
                office_renderer=qa["renderer"],text_overflow=len(qa["overflow_candidates"]),
                independent_svg_assets=len(list((pack/"05_DEMO_ASSETS").rglob("*.svg"))),
                original_deck_and_pdf_preserved=True)


def check():
    copied=rows("07_FINAL_REPORT/COPIED_EVIDENCE.csv")[1:]
    gitrefs=[f"{rev}:{path}" for dest,rev,path,digest in copied]
    batch=subprocess.run(["git","cat-file","--batch-check=%(objectname)"],cwd=repo,input=("\n".join(gitrefs)+"\n").encode(),capture_output=True,check=True).stdout.splitlines()
    assert len(copied)==len(batch)
    for (dest,_,_,digest),obj in zip(copied,batch):
        b=read(dest)
        assert sha(b)==digest and blob_sha(b)==obj.decode(),dest
    assert sha(read("01_TEACHER_REQUIREMENTS/TP-FINAL-DELIVERY-001_任务书原文.txt"))=="48be991eba76cf7fbc2f75eae8fb3596b77fbd774dd4b0057466424ca143a771"
    teacher=json.loads(read("01_TEACHER_REQUIREMENTS/originals/SHA256.json"))["images"]
    assert len(teacher)==5
    for i,item in enumerate(teacher,1):
        b=read(f"01_TEACHER_REQUIREMENTS/originals/teacher-{i:02}.png")
        assert len(b)==item["Bytes"] and sha(b).upper()==item["SHA256"]
    msgs=json.loads(read("03_TEAM_COLLABORATION/transcripts/message-index.json"))
    assert len(msgs)==12
    for item in msgs:
        assert sha(read("03_TEAM_COLLABORATION/transcripts/"+item["file"]))==item["sha256"]
    w=load_workbook(pack/"07_FINAL_REPORT/FINAL_ACCEPTANCE_MATRIX.xlsx",read_only=True)
    data=list(w.worksheets[0].values)[1:]
    assert len(data)==len({row[0] for row in data})==64
    historical=dict(Counter(row[4] for row in data))
    assert historical=={"PASS":44,"PARTIAL":17,"MISSING":1,"UNVERIFIED":2}
    assert {r[0] for r in data if r[4]!=r[5]}=={"H01","H02","H04"}
    assert all(r[4:6]==("PARTIAL","PASS") for r in data if r[4]!=r[5])
    tally=dict(Counter(row[5] for row in data))
    assert tally=={"PASS":47,"PARTIAL":14,"MISSING":1,"UNVERIFIED":2}
    w.close()
    w=load_workbook(pack/"01_TEACHER_REQUIREMENTS/SCORING_MATRIX.xlsx",read_only=True)
    scores=[w.worksheets[0].cell(i,4).value for i in range(2,10)]
    assert scores==[20,5,15,10,10,20,20,5] and sum(scores[:7])==100
    w.close()
    outline=read("06_PRESENTATION/PPT_OUTLINE.md").decode()
    assert len(re.findall(r"^## P\d\d",outline,re.M))==15
    assert sum(map(int,re.findall(r"· (\d+) 秒\*\*",outline)))==775
    slide_checks=check_slides()
    for f in pack.rglob("*.png"):
        with Image.open(f) as img:
            img.verify()
    for f in pack.rglob("*.svg"):
        ElementTree.parse(f)
    for f in pack.rglob("*.json"):
        json.loads(f.read_bytes())
    raw={pack/row[0] for row in copied}
    links=0
    for f in pack.rglob("*.md"):
        if f in raw:continue
        for m in re.finditer(r"\[[^\]]*?\]\(([^)\n]+)\)",f.read_text(encoding="utf-8-sig")):
            t=unquote(m.group(1).strip("<>"))
            if t.startswith(("https://","http://","#")):continue
            file=t.split("#")[0]
            assert (f.parent/file).exists(),f"{f.name} => {file}"
            links+=1
    return dict(snapshot="cf448f3",repository_snapshot_files=tracked_snapshot(),audit_commit="0d9e893",git_blob_copies=len(copied),teacher_original_images=5,historical_course_checkpoints=historical,current_material_checkpoints=tally,presentation=slide_checks,base_points=sum(scores[:7]),bonus_cap=scores[7],work_packages=5,archived_log_entries=49,original_prompt_coverage_at_audit="48/49",additional_original_messages=len(msgs),outline_pages=15,suggested_seconds=775,local_navigation_links_checked=links)

def paths():
    return sorted((f for f in pack.rglob("*") if f.is_file()),key=lambda f:f.relative_to(pack).as_posix())

def verify_archive():
    entries=rows("07_FINAL_REPORT/FILE_MANIFEST.csv")[1:]
    assert {row[0] for row in entries}=={f.relative_to(pack).as_posix() for f in paths() if f!=manifest}
    with ZipFile(distribution) as z:
        assert z.testzip() is None
        assert set(z.namelist())=={pack.name+"/"+f.relative_to(pack).as_posix() for f in paths()}
        for name,size,digest in entries:
            b=read(name)
            assert len(b)==int(size) and sha(b)==digest==sha(z.read(pack.name+"/"+name)),name
        assert z.read(pack.name+"/"+manifest.relative_to(pack).as_posix())==manifest.read_bytes()
    return len(entries)+1

if __name__=="__main__":
    args=argparse.ArgumentParser()
    args.add_argument("--seal",action="store_true",help="Regenerate the receipt, manifest and ZIP")
    opts=args.parse_args()
    if opts.seal:
        report.write_text("{}\n",encoding="utf8")
        manifest.touch(exist_ok=True)
    result=check()
    if opts.seal:
        report.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
        with manifest.open("w",newline="",encoding="utf-8-sig") as f:
            writer=csv.writer(f)
            writer.writerow(("归档相对路径","字节","SHA-256"))
            for file in paths():
                if file!=manifest:
                    b=file.read_bytes()
                    writer.writerow((file.relative_to(pack).as_posix(),len(b),sha(b)))
        with ZipFile(distribution,"w",ZIP_DEFLATED,compresslevel=6) as z:
            for f in paths():
                z.write(f,pack.name+"/"+f.relative_to(pack).as_posix())
    print(json.dumps({"files_in_final_zip":verify_archive(),"zip_bytes":distribution.stat().st_size,"zip_sha256":sha(distribution.read_bytes()),**result},indent=2,ensure_ascii=False))
