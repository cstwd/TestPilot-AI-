"""Build Phase 06 counters and compare checkpoints without mutating historical evidence."""
from collections import Counter
import json
from pathlib import Path
from statistics import mean,median
from .quality import ARCHIVE, RAW as QUALITY, SPEC, SEEDS, checked_project

RAW=QUALITY.parent
OUT=RAW.parent


def read(path,default=None):
    return json.loads(path.read_bytes()) if path.exists() else default


def lines(path):
    if not path.exists():
        return []
    return [json.loads(row) for row in path.read_bytes().splitlines() if row.strip()]


def resources(path):
    values=lines(path)
    if not values:
        return {}
    keys={
        "peak_physical_gib":("physical_used_gib",max),
        "min_physical_free_gib":("physical_free_gib",min),
        "peak_commit_gib":("commit_used_gib",max),
        "min_commit_free_gib":("commit_free_gib",min),
        "peak_gpu_mib":("gpu_used_mib",max),
        "peak_cpu_pct":("cpu_pct",max),
        "mean_cpu_pct":("cpu_pct",mean),
    }
    result={}
    for key,(col,f) in keys.items():
        values_for_key=[r[col] for r in values if r.get(col) is not None]
        if values_for_key:
            result[key]=round(f(values_for_key),3)
    result.update(samples=len(values),duration_s=round(values[-1]["at"]-values[0]["at"],3))
    return result


def workload(rows):
    attempts=[a for row in rows for a in row.get("attempts",[]) if a.get("status")=="accepted"]
    ttft=[a["ttft_s"] for a in attempts if a.get("ttft_s") is not None]
    tps=[a["tokens_out"]*1e9/a["generation_ns"] for a in attempts if a.get("tokens_out") and a.get("generation_ns")]
    return dict(rows=len(rows),ok=sum(r.get("ok",False) for r in rows),
                errors=dict(Counter(r.get("kind") or r.get("error") or "wrong_answer" for r in rows if not r.get("ok"))),
                median_ttft_s=round(median(ttft),3) if ttft else None,
                mean_output_tps=round(mean(tps),3) if tps else None,
                input_tokens=[r["tokens_in"] for r in rows if "tokens_in" in r])


def semantic(dir):
    data=[read(p) for p in dir.glob("*.json")]
    counts=Counter()
    for row in data:
        counts.update(row["scores"])
    return {"projects":len(data),"points":sum(counts.values()),"fields":dict(counts),
            "retries":sum(max(0,len(r["attempts"])-1) for r in data)}


def main():
    historical = read(ARCHIVE/"reports/phase05/summary.json")
    old = {a:historical["groups"][a]["killed"] for a in "BCD"}
    stages={a:Counter() for a in ("before","after")}
    attempts=0
    feedback=Counter()
    observations=[]
    for n in SPEC:
        p=checked_project(n)
        for seed in SEEDS:
            base=QUALITY/n/str(seed)
            result=read(base/"result.json")
            if result is None:
                continue
            attempts+=1
            proposals=read(base/"feedback.json",{})
            feedback["survivor_requests"]+=len(proposals.get("attempts",[]))
            feedback["provider_attempts"]+=sum(len(r.get("responses",[])) for r in proposals.get("attempts",[]))
            feedback["no_case"]+=sum(r["status"]=="no_distinguishing_case" for r in proposals.get("attempts",[]))
            feedback["candidates"]+=len(proposals.get("cases",[]))
            feedback["accepted"]+=len(read(base/"selection.json",{}).get("accepted_names",[]))
            counts={}
            for arm in stages:
                expected=p["manifest"]
                item=result[arm]
                if not item:
                    continue
                assert item["total"]==len(expected)
                observed_ids={r.stem for r in (base/arm).glob("*.json")}
                assert observed_ids=={m["id"] for m in expected}
                for site in expected:
                    outcome=read(base/arm/(site["id"]+".json"))
                    assert outcome["execution"]["source_sha256"]==site["mutated_sha256"]
                stages[arm].update({k:v for k,v in item.items() if k!="score_pct"})
                counts[arm]=item["killed"]
            observations.append(dict(project=n,seed=seed,**counts))
    feedback["net_kills"]=stages["after"]["killed"]-stages["before"]["killed"]
    for v in stages.values():
        v["full_plan_pct"]=round(100*v["killed"]/117,2)
    traces={}
    for p in RAW.glob("*.ndjson"):
        traces[p.stem]=workload(lines(p))
        if p.stem=="stability-4k":
            traces[p.stem]["median_ttft_s"]=None
    inputs={"attempts":attempts,"stages":{k:dict(v) for k,v in stages.items()},"historical_kills":old,
            "feedback":dict(feedback),"understanding":semantic(QUALITY/"understanding"),
            "first_schema":semantic(RAW/"understanding-first-schema"),
            "observed": observations,"workloads":traces,
            "resources":{p.parent.name:resources(p) for p in RAW.glob("*/telemetry.ndjson")},
            "recovery":read(RAW/"recovery.json"),"live_keys":list(read(RAW/"live.json",{}))}
    (OUT/"summary.json").write_text(json.dumps(inputs,ensure_ascii=False,indent=2),encoding="utf8")
    print(json.dumps({k:inputs[k] for k in ("attempts","stages","feedback","understanding")},ensure_ascii=False))

if __name__=="__main__":
    main()
