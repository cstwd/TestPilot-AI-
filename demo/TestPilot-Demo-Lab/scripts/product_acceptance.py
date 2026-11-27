
"""Drive the existing TestPilot API with a disposable SQLite workspace."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from urllib.error import HTTPError, URLError
from urllib.request import Request



LAB = Path(__file__).resolve().parents[1]
REPO = LAB.parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / 'tests'))
from test_startup import CLIENT, running_server, vacant_port  # noqa: E402
from backend.mutation_results import test_assertion  # noqa: E402
from backend.runner import execute  # noqa: E402


def read(path):
    return json.loads((LAB / path).read_text(encoding="utf-8"))


def request(url, path, body=None):
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = Request(url + path, data=data, headers={"Content-Type": "application/json"})
    try:
        with CLIENT.open(request, timeout=240) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        detail = error.read().decode("utf-8", "replace")
        try:
            return error.code, json.loads(detail)
        except json.JSONDecodeError:
            return error.code, detail


def checked(client, path, body=None):
    status, payload = request(client, path, body)
    if not 200 <= status < 300:
        raise RuntimeError(f"{path} HTTP {status}: {payload}")
    return payload


def get(client, path):
    return checked(client, path)


def post(client, path, payload):
    return checked(client, path, payload)


def import_text(client, project, filename, source):
    version = post(client, f"/api/projects/{project['id']}/files",
                   {"filename": filename, "source": source})
    assert version["sha256"] == hashlib.sha256(source.encode("utf-8")).hexdigest()
    return version


def prepare(client, sample, entry):
    project = post(client, "/api/projects", {"name": f"Demo Lab · {entry['name']}"})
    path = (LAB / entry["path"]).resolve()
    assert entry["path"] == f"source/{entry['tier']}/{entry['name']}.py"
    assert path.is_relative_to((LAB / "source").resolve())
    source = path.read_text(encoding="utf-8")
    assert hashlib.sha256(source.encode()).hexdigest() == entry["sha256"]
    version = import_text(client, project, Path(entry["path"]).name, source)
    analysis = get(client, f"/api/files/{version['id']}/analysis")
    assert analysis["valid"] and analysis["sha256"] == version["sha256"]
    assert sample["target"] in {symbol["name"] for symbol in analysis["symbols"]}
    return project, version, analysis


def generate_and_run(client, sample, entry, row, mode):
    project, version, analysis = prepare(client, sample, entry)
    row.update(project=project, revision_id=version["id"], analysis=analysis)
    suite = post(client, f"/api/files/{version['id']}/suites",
                 {"target": sample["target"], "mode": mode})
    assert suite["mode"] == mode and suite["file_id"] == version["id"]
    initial = suite["initial_run"]
    run = get(client, f"/api/runs/{initial['id']}")
    assert run["file_id"] == version["id"] and run["suite_id"] == suite["id"]
    row.update(suite=suite, run=run)
    report = get(client, f"/api/runs/{run['id']}/report")
    assert report == get(client, f"/api/runs/{run['id']}/report/export")
    row["quality"] = report


def mutation(client, sample, entry, row):
    _, version, _ = prepare(client, sample, entry)
    task = post(client, f"/api/engine/files/{version['id']}/tasks",
                {"target": sample["target"], "generation_mode": "template", "max_repairs": 0})
    row["task"] = task
    session = post(client, f"/api/engine/tasks/{task['id']}/mutations", {"feedback": False})
    api = f"/api/mutations/{session['id']}"
    row["session_id"] = session["id"]
    post(client, api + "/run", {})
    result = get(client, api + "/report")
    assert result["source_sha256"] == version["sha256"] and result["manifest"] == session["manifest"]
    row["report"] = result


def assert_regression(client, project, version, suite, run, source, corrected, filename):
    assert run["status"] == "failed"
    code = suite["source"]
    detailed = execute(source, code, detailed=True)
    fixed_check = execute(corrected, code, detailed=True)
    assert detailed["result_complete"] and fixed_check["status"] == "passed", "suite failed its reference replay"
    assert detailed["cases"] == run["cases"], "original replay disagrees with F04"
    old_nodes = {case["nodeid"] for case in run["cases"]}
    fixed_nodes = {case["nodeid"]: case["outcome"] for case in fixed_check["cases"]}
    assert old_nodes == fixed_nodes.keys(), "reference replay changed collection"
    failure = next(f for f in detailed["failures"]
                   if fixed_nodes[f["nodeid"]] == "passed" and test_assertion(f, code))
    bug = post(client, f"/api/runs/{run['id']}/bugs",
               {"nodeid": failure["nodeid"], "title": "Demo Lab assertion regression"})
    assert bug["status"] == "open"
    second = import_text(client, project, filename, corrected)
    assert second["revision"] == 2 and second["sha256"] != version["sha256"]
    updated = post(client, f"/api/bugs/{bug['id']}/regressions", {"file_id": second["id"]})
    regression = get(client, f"/api/runs/{updated['regressions'][-1]['run_id']}")
    assert regression["suite_id"] == suite["id"] and regression["file_id"] == second["id"]
    assert updated["status"] == "resolved" and regression["cases"] == fixed_check["cases"]
    report = get(client, f"/api/runs/{regression['id']}/report")
    assert report == get(client, f"/api/runs/{regression['id']}/report/export")
    return {"original_run": run, "detailed_original": detailed, "reference_replay": fixed_check,
            "bug": bug, "updated_bug": updated,
            "regression": regression, "quality": report}


def write_evidence(path, evidence):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def regression_candidate(client, row, entry):
    filename = row["module"] + ".py"
    source = (LAB / entry["path"]).read_text(encoding="utf-8")
    fixed = (LAB / "reference" / "corrected" / filename).read_text(encoding="utf-8")
    revision = {"id": row["revision_id"], "sha256": row["analysis"]["sha256"]}
    return assert_regression(client, row["project"], revision, row["suite"], row["run"],
                             source, fixed, filename)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("blind", "mutation", "regression"))
    parser.add_argument("--module", action="append", help="Only run selected scenario modules")
    parser.add_argument("--output", type=Path, help="Override the receipt path")
    parser.add_argument("--workflow", action="store_true", help="Run F05 after blind capture is complete")
    args = parser.parse_args()
    lab_runtime = REPO / ".runtime"
    lab_runtime.mkdir(exist_ok=True)
    modules = {row["name"]: row for row in read("scenarios/modules.json")}
    output = args.output or LAB / "reports" / f"product_{args.stage}.json"
    evidence = {"stage": args.stage, "date": datetime.now(timezone.utc).isoformat(), "samples": []}
    scenarios = {"blind": "bug_hunting", "mutation": "mutation_demo", "regression": "regression_demo"}
    chosen = read(f"scenarios/{scenarios[args.stage]}.json")
    if args.module and set(args.module) - {sample["module"] for sample in chosen}:
        parser.error("--module must identify a module in the selected scenario")
    with TemporaryDirectory(prefix="demo-lab-", dir=lab_runtime) as directory:
        data = Path(directory)
        with running_server(vacant_port(), data, data / "service.log", "demo") as client:
            evidence["health"] = get(client, "/api/health")
            if args.stage == "blind":
                status, health = request(client, "/api/model/health")
                evidence["model_health"] = {"http": status, **health}
            for sample in chosen:
                entry = modules[sample["module"]]
                if args.module and entry["name"] not in args.module:
                    continue
                row = {**sample, "tier": entry["tier"], "domain": entry["domain"]}
                evidence["samples"].append(row)
                try:
                    if args.stage == "mutation":
                        mutation(client, sample, entry, row)
                    elif args.stage == "blind":
                        generate_and_run(client, sample, entry, row, "ai")
                    else:
                        generate_and_run(client, sample, entry, row, "template")
                        row["workflow"] = regression_candidate(client, row, entry)
                except (RuntimeError, AssertionError, StopIteration, URLError, TimeoutError) as exc:
                    row["error"] = str(exc) or type(exc).__name__
                print(row["module"], row.get("error") or row.get("report", row.get("run", {})).get("status"),
                      flush=True)
                write_evidence(output, evidence)
            if args.stage == "blind" and args.workflow:
                workflow = {"stage": "regression", "date": evidence["date"], "samples": []}
                for row in evidence["samples"]:
                    if row.get("run", {}).get("status") != "failed" or row["tier"] == "good":
                        continue
                    entry = modules[row["module"]]
                    outcome = {"module": row["module"], "target": row["target"]}
                    workflow["samples"].append(outcome)
                    try:
                        outcome["workflow"] = regression_candidate(client, row, entry)
                    except (RuntimeError, AssertionError, StopIteration, URLError, TimeoutError) as exc:
                        outcome["error"] = str(exc) or type(exc).__name__
                    print("F05", outcome["module"], outcome.get("error", "executed"), flush=True)
                write_evidence(output.with_name("product_blind_regression.json"), workflow)


if __name__ == "__main__":
    main()
