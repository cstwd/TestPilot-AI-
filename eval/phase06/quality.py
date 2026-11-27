"""Replay the immutable Phase 05 corpus with the production Provider and WASI."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import os
from pathlib import Path
import sys
import time

from backend.engine_analyzer import analyze_source
from backend.engine_llm import GenerationFailure, generate_tests
from backend.engine_strategy import build_strategy
from backend.model_understanding import understand
from backend.model_provider import ModelError, provider
from backend.mutation_feedback import supplement
from backend.mutation_flow import select_green_additions
from backend.mutation_generator import apply_site, digest
from backend.mutation_results import baseline_ok, classify, score

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path(os.getenv("TESTPILOT_PHASE05_ROOT", str(ROOT.parent/"tp-phase-05"))).resolve()
sys.path.append(str(ARCHIVE))
from eval.phase05.corpus import get, SPEC, SEEDS, staged
from eval.phase05.measure import calibrate, measured

RAW = ROOT/"reports/phase06/raw/quality"
FROZEN = json.loads((ARCHIVE/"eval/phase05/frozen.json").read_bytes())


def load(path):
    return json.loads(path.read_bytes())


def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf8")
    tmp.replace(path)


def checked_project(name):
    p = get(name)
    f = FROZEN["projects"][name]
    assert p["gold"]==f["rubric"] and p["manifest"]==f["manifest"]
    assert {k:digest(v) for k,v in p["files"].items()}==f["files"]
    return p


def semantic(name):
    p = checked_project(name)
    file = RAW/"understanding"/f"{name}.json"
    if file.exists():
        return
    try:
        reply = understand(p["files"],p["target"],normal=p["normal"],boundary=p["edge"],exception_probe=p["probe"])
        predicted = json.loads(reply.value.model_dump_json())
        points = {k:int(json.dumps(predicted[k],sort_keys=True)==json.dumps(v,sort_keys=True))
                  for k,v in p["gold"].items()}
        save(file,{"project":name,"predicted":predicted,"expected":p["gold"],"scores":points,
                   "run_id":reply.run_id,"attempts":reply.attempts})
    except ModelError as exc:
        save(file,{"project":name,"error":exc.kind,"message":str(exc),"attempts":exc.attempts,"scores":{}})
    print("understanding",name,flush=True)


def generate(name,seed):
    p = checked_project(name)
    dest = RAW/name/str(seed)/"generation.json"
    if dest.exists():
        return
    started = time.monotonic()
    analysis = analyze_source(p["source"])
    analysis["dependencies"]={k:v for k,v in p["files"].items() if k!="subject.py"}
    strategy=build_strategy(analysis,p["target"])
    try:
        item=generate_tests(p["source"],p["target"],analysis,strategy,config={"seed":seed,"temperature":.35})
    except GenerationFailure as exc:
        item=exc.evidence
    save(dest,{**item,"seconds":time.monotonic()-started})
    print("generated",name,seed,item.get("error_kind","ok"),flush=True)


def execution(p,out,code,green):
    verdicts,evidence = {},{}
    for site in p["manifest"]:
        file=out/(site["id"]+".json")
        if not file.exists():
            ex=measured(apply_site(p["source"],site),code)
            save(file,{"execution":ex,"verdict":classify(green,ex,test_code=code),"mutant":site["id"]})
        item=load(file)
        assert item["execution"]["source_sha256"]==site["mutated_sha256"]
        assert item["execution"]["test_sha256"]==digest(code)
        verdicts[site["id"]]=item["verdict"]
        evidence[site["id"]]=item["execution"]
    return score(p["manifest"],verdicts),verdicts,evidence


def run(args):
    name,seed = args
    p=checked_project(name)
    folder=RAW/name/str(seed)
    result=folder/"result.json"
    if result.exists():
        return
    g=load(folder/"generation.json")
    report={"project":name,"seed":seed,"before":None,"after":None,"planned":len(p["manifest"]),"initial_run_id":g.get("run_id")}
    if not g.get("code"):
        return save(result,{**report,"reason":g.get("error","no code")})
    code=staged(g["code"],p["files"])
    trial=folder/"trial.json"
    if not trial.exists():
        save(trial,measured(p["source"],code))
    run=load(trial)
    accepted=calibrate(code,run)
    if not accepted:
        return save(result,{**report,"reason":"original rejected suite"})
    if accepted != code:
        green=folder/"validated-original.json"
        if not green.exists():
            save(green,measured(p["source"],accepted))
        run=load(green)
    if not baseline_ok(run):
        return save(result,{**report,"reason":"original rejected filtered suite"})
    (folder/"validated_test.py").write_text(accepted,encoding="utf8")
    before,status,executions=execution(p,folder/"before",accepted,run)
    report["before"]=before
    survivors=[m for m in p["manifest"] if status[m["id"]]["status"]=="survived"]
    draft=folder/"feedback.json"
    if not draft.exists():
        value=supplement(p["source"],p["target"],accepted,survivors,observations=executions,seed=seed,
                         dependencies={k:v for k,v in p["files"].items() if k!="subject.py"})
        save(draft,value)
    proposal=load(draft)
    chosen=accepted
    if proposal.get("code"):
        proof=folder/"validation.json"
        if not proof.exists():
            save(proof,measured(p["source"],proposal["code"]))
        selection=select_green_additions(accepted,proposal,run,load(proof))
        save(folder/"selection.json",selection)
        chosen=selection["code"] or accepted
    after_baseline=folder/"after-original.json"
    if not after_baseline.exists():
        save(after_baseline,measured(p["source"],chosen))
    green=load(after_baseline)
    if not baseline_ok(green):
        return save(result,{**report,"reason":"after/original rejected suite"})
    (folder/"augmented_test.py").write_text(chosen,encoding="utf8")
    after,_,_=execution(p,folder/"after",chosen,green)
    save(result,{**report,"after":after})
    print("measured",name,seed,before["killed"],after["killed"],flush=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=("generate","measure","understanding"))
    p.add_argument("--workers",type=int,choices=(1,2),default=2)
    a=p.parse_args()
    order=[(name,seed) for seed in SEEDS for name in SPEC]
    if a.mode=="understanding":
        for name in SPEC:
            semantic(name)
    elif a.mode=="generate":
        for name,seed in order:
            generate(name,seed)
    else:
        with ProcessPoolExecutor(a.workers) as pool:
            remaining=list(order)
            active={}
            while remaining or active:
                for key,future in list(active.items()):
                    if future.done():
                        future.result()
                        del active[key]
                for key in list(remaining):
                    name,seed=key
                    if len(active)<a.workers and (RAW/name/str(seed)/"generation.json").exists():
                        active[key]=pool.submit(run,key)
                        remaining.remove(key)
                time.sleep(.35)

if __name__=="__main__":
    main()
