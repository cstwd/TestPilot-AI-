"""Recompute report metrics from individual F09, F10 and F13 evidence."""
from collections import Counter
import csv
import json
from pathlib import Path
from statistics import mean
from backend.mutation_generator import digest
from backend.mutation_results import baseline_ok, classify, score
from .audit import RAW, REPORT, save
from .corpus import SPEC, SEEDS, get

ARMS = {"A":"Qwen2.5-Coder 0.5B", "B":"模板", "C":"Qwen3.8 初始", "D":"Qwen3.8 补测后"}


def read(path):
    return json.loads(path.read_bytes())


def pct(n, d):
    return round(100 * n / d, 2) if d else None


def cases(arm, require_complete):
    results = []
    for name in SPEC:
        project = get(name)
        for seed in SEEDS:
            out = RAW/"campaigns"/name/str(seed)/arm
            if not (out/"result.json").exists():
                if require_complete:
                    raise ValueError(f"Missing result for {name}/{seed}/{arm}")
                continue
            gen = read(out/"generation.json")
            result = read(out/"result.json")
            assert result["generated"] == gen["id"] and result["planned"] == len(project["manifest"])
            tests = [read(out/file) for file in ("trial.json","selected-original.json","calibration.json")
                     if (out/file).exists()]
            if result["baseline"]:
                green = next(t for t in tests if t["job_id"] == result["green_job"])
                code = (out/"validated_test.py").read_text("utf8")
                assert baseline_ok(green) and digest(code) == green["test_sha256"] == result["test_sha256"]
                assert green["source_sha256"] == digest(project["source"])
                outcomes = {}
                for site in project["manifest"]:
                    row=read(out/(site["id"]+".json"))
                    run=row["run"]
                    assert row["id"] == site["id"]
                    assert run["source_sha256"] == site["mutated_sha256"] and run["test_sha256"] == digest(code)
                    verdict=classify(green, run, test_code=code)
                    assert row["verdict"] == verdict
                    outcomes[site["id"]]=verdict
                    tests.append(run)
                assert outcomes == result["outcomes"] and score(project["manifest"],outcomes) == result["score"]
            if arm == "D":
                parent=read(out.parent/"C/result.json")
                assert parent["id"] == gen["parent"]
                if result["baseline"]:
                    previous=(out.parent/"C/validated_test.py").read_text("utf8")
                    assert code.startswith(previous)
            attempts=[]
            if (out/"requests.jsonl").exists():
                attempts=[json.loads(line) for line in (out/"requests.jsonl").read_bytes().splitlines()]
            if arm=="D":
                attempts=[read(p) for p in sorted(out.glob("model-*.json"))]
            selected=read(out/"selection.json") if (out/"selection.json").exists() else {}
            proposal=read(out/"proposal.json") if (out/"proposal.json").exists() else {}
            original_trial=read(out/"trial.json") if (out/"trial.json").exists() else {}
            stat=result.get("score") or {}
            results.append({
                "arm":arm,"project":name,"seed":seed,"planned":result["planned"],"baseline":result["baseline"],
                "mode":gen["artifact"].get("mode"),"model_requests":len(attempts),"responses":sum("response" in x for x in attempts),
                "generation_s":gen["seconds"],"test_sha256":result.get("test_sha256"),"reason":result["reason"],
                "feedback_reason":gen.get("reason"),"local_response_rates":[x["response"]["timings"]["predicted_per_second"]
                   for x in attempts if (x.get("response",{}).get("timings") or {}).get("predicted_per_second")],
                "proposal_count":len(proposal.get("cases",[])), "accepted_count":len(selected.get("accepted_names",[])),
                "trial_passed":original_trial.get("passed"),"trial_failed":original_trial.get("failed"),
                "trial_errors":original_trial.get("errors"),
                "executions":len(tests),"complete_jobs":sum(r["result_complete"] for r in tests),
                **{key:stat.get(key,0) for key in ("killed","survived","timeout","execution_error","equivalent_candidates")},
                "noscored":0 if stat else result["planned"],"score_pct":stat.get("score_pct")})
    return results


def summarize(results):
    keys=("planned","killed","survived","timeout","execution_error","equivalent_candidates","noscored","executions",
          "complete_jobs","proposal_count","accepted_count","baseline","model_requests","responses")
    sums=Counter(dict.fromkeys(keys,0))
    for r in results:
        sums.update({k:r[k] for k in keys})
    scores=[r["score_pct"] for r in results if r["score_pct"] is not None]
    speed=[value for r in results for value in r["local_response_rates"]]
    observed=sums["planned"]-sums["noscored"]
    return {**sums,"run_count":len(results),"scorable_mutants":observed,
            "mutation_score":pct(sums["killed"],observed),
            "all_manifest_detection":pct(sums["killed"],sums["planned"]),
            "validated_candidate_pct":pct(sums["accepted_count"],sums["proposal_count"]),
            "suite_modes":dict(Counter(r["mode"] for r in results)),
            "generation_mean_s":mean(r["generation_s"] for r in results) if results else None,
            "throughput_mean_tps":mean(speed) if speed else None,
            "actual_job_completion_pct":pct(sums["complete_jobs"],sums["executions"]),
            "score_range":[min(scores),max(scores)] if scores else None,
            "distinct_test_sha_per_project":{n:len({r["test_sha256"] for r in results if r["project"]==n and r["test_sha256"]})
                                             for n in SPEC}}


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--partial",action="store_true")
    ns=parser.parse_args()
    observations=[r for arm in ARMS for r in cases(arm,not ns.partial)]
    all_stats={a:summarize([r for r in observations if r["arm"]==a]) for a in ARMS}
    rounds={a:{str(s):summarize([r for r in observations if r["arm"]==a and r["seed"]==s])
               for s in SEEDS} for a in ARMS}
    pairs=[]
    for name in SPEC:
        for seed in SEEDS:
            pair={r["arm"]:r for r in observations if r["project"]==name and r["seed"]==seed}
            if all(k in pair and pair[k]["baseline"] for k in ("C","D")):
                pairs.append(dict(project=name,seed=seed,
                    before=pair["C"]["killed"],after=pair["D"]["killed"],total=pair["C"]["planned"]))
    payload={"groups":all_stats,"rounds":rounds,"campaigns":observations,"paired":pairs,
             "planned_per_round":sum(len(get(name)["manifest"]) for name in SPEC)}
    save(REPORT/"summary.json",payload)
    if observations:
        with (REPORT/"campaigns.csv").open("w",encoding="utf-8-sig",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=[k for k in observations[0] if k!="local_response_rates"])
            writer.writeheader()
            writer.writerows({k:v for k,v in x.items() if k!="local_response_rates"} for x in observations)
    for arm,row in all_stats.items():
        print(arm,row["run_count"],row["baseline"],row["killed"],row["all_manifest_detection"],row["mutation_score"])

if __name__=="__main__":
    main()
