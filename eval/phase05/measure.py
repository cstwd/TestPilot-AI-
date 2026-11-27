"""Fresh isolated Pytest jobs for originals and every frozen first-order mutant."""
import argparse
import ast
from concurrent.futures import ProcessPoolExecutor
import json
import msvcrt
import os
from pathlib import Path
import time
from uuid import uuid4

from backend.engine_llm import generate_tests
from backend.mutation_generator import apply_site, digest
from backend.mutation_results import baseline_ok, classify, score
from backend.runner import execute
from .audit import RAW, LAB, save, stamp
from .corpus import SEEDS, SPEC, evidence_contract, get, staged


def directory(name,seed,arm):
    out=RAW/"campaigns"/name/str(seed)/arm
    out.mkdir(parents=True,exist_ok=True)
    return out


def measured(source,code):
    t=stamp()
    run=execute(source,code,detailed=True,timeout_s=25)
    run.update(job_id=str(uuid4()),started=t,ended=stamp(),source_sha256=digest(source),test_sha256=digest(code))
    return run


def calibrate(code, trial):
    if baseline_ok(trial):
        return code
    if not trial["result_complete"] or not trial["passed"] or not (trial["failed"] or trial["errors"]):
        return None
    groups={}
    for case in trial["cases"]:
        name=case["nodeid"].removeprefix("test_generated.py::").split("[",1)[0]
        groups.setdefault(name,set()).add(case["outcome"])
    rejected={k for k,v in groups.items() if v!={"passed"}}
    tree=ast.parse(code)
    defs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name.startswith("test_")}
    if not rejected <= defs.keys() or not groups.keys()-rejected:
        return None
    lines=code.splitlines(keepends=True)
    for name in rejected:
        n=defs[name]
        start=min([n.lineno]+[d.lineno for d in n.decorator_list])
        for i in range(start-1,n.end_lineno):
            lines[i]="\n"
    return "".join(lines)


def run_one(args):
    name, seed, arm = args
    locks = LAB.parents[1] / ".runtime" / "phase05-locks"
    locks.mkdir(parents=True, exist_ok=True)
    with (locks / f"{name}-{seed}-{arm}.lock").open("a+b") as lock:
        lock.seek(0)
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            return "active in another worker"
        try:
            run_campaign(args)
            return "archived"
        finally:
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)


def run_campaign(args):
    name,seed,arm=args
    p=get(name)
    out=directory(name,seed,arm)
    if (out/"result.json").exists():
        return
    frozen=json.loads((LAB/"frozen.json").read_bytes())["projects"][name]
    assert p["manifest"]==frozen["manifest"] and {k:digest(v) for k,v in p["files"].items()}==frozen["files"]
    if arm=="B" and not (out/"generation.json").exists():
        t=time.monotonic()
        artifact=generate_tests(p["source"],p["target"],{}, {},config={"provider":"template"})
        save(out/"generation.json",{"id":str(uuid4()),"at":stamp(),"seconds":time.monotonic()-t,"artifact":artifact})
    if not (out/"generation.json").exists():
        raise RuntimeError(f"Generation missing {out}")
    generation=json.loads((out/"generation.json").read_bytes())
    artifact=generation.get("artifact") or {}
    summary=dict(name=name,seed=seed,arm=arm,planned=len(p["manifest"]),baseline=False,score=None,
                 reason="",outcomes={},id=str(uuid4()),generated=generation["id"])
    def finish(reason):
        save(out/"result.json",{**summary,"reason":reason,"finished":stamp()})
    if not artifact.get("code") or arm in {"A","C"} and artifact.get("mode")!="ai":
        return finish("no validated suite from assigned generator")
    original=artifact["code"]
    code=original if arm=="D" else staged(original,p["files"])
    if not (out/"trial.json").exists():
        save(out/"trial.json",measured(p["source"],code))
    trial=json.loads((out/"trial.json").read_bytes())
    green_code=calibrate(code,trial) if arm!="D" else code
    if not green_code:
        return finish("original rejected candidate suite")
    if green_code!=code:
        if not (out/"selected-original.json").exists():
            save(out/"selected-original.json",measured(p["source"],green_code))
        green=json.loads((out/"selected-original.json").read_bytes())
    else:
        green=trial
    if not baseline_ok(green):
        return finish("selected suite failed original gate")
    (out/"validated_test.py").write_text(green_code, encoding="utf8")
    summary.update(baseline=True,test_sha256=digest(green_code),green_job=green["job_id"])
    for site in p["manifest"]:
        path=out/(site["id"]+".json")
        if not path.exists():
            run=measured(apply_site(p["source"],site),green_code)
            verdict=classify(green,run,test_code=green_code)
            save(path,{"id":site["id"],"verdict":verdict,"run":run})
        summary["outcomes"][site["id"]]=json.loads(path.read_bytes())["verdict"]
    summary["score"]=score(p["manifest"],summary["outcomes"])
    finish("complete")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("arm",choices=["A","B","C","D","reference"])
    parser.add_argument("--workers",type=int,choices=(1,2),default=1)
    parser.add_argument("--follow",action="store_true")
    a=parser.parse_args()
    if a.arm=="reference":
        for name in SPEC:
            p=get(name)
            r=measured(p["source"],evidence_contract(p))
            save(RAW/"references"/(name+".json"),r)
            if not baseline_ok(r):
                raise RuntimeError(f"{name} reference gate: {r['log']}")
        return
    pending=[(name,seed,a.arm) for seed in SEEDS for name in SPEC]
    with ProcessPoolExecutor(a.workers) as pool:
        active={}
        while pending or active:
            for key,future in list(active.items()):
                if future.done():
                    print(*key, future.result(),flush=True)
                    del active[key]
            for args in list(pending):
                if len(active)>=a.workers:
                    break
                out=directory(*args)
                if a.arm=="B" or (out/"generation.json").exists():
                    pending.remove(args)
                    active[args]=pool.submit(run_one,args)
            if pending and not active and not a.follow:
                raise RuntimeError("Waiting on generation; use --follow for pipeline")
            time.sleep(.5)

if __name__=="__main__":
    main()
