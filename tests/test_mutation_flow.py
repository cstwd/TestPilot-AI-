"""Drive the distributed main.py through F07-F13 and verify real WASI observations."""
import json
import os
from pathlib import Path
from urllib.request import ProxyHandler, Request, build_opener

from test_dashboard import app_url


ROOT = Path(__file__).resolve().parents[1]


def test_mutation_experiment(app_url):
    client = build_opener(ProxyHandler({}))
    def http(path, body=None):
        data = None if body is None else json.dumps(body).encode()
        req = Request(app_url + path, data=data, headers={"Content-Type": "application/json"})
        with client.open(req, timeout=900) as response:
            return response.read()
    def api(path, body=None):
        return json.loads(http(path, body))

    live = os.environ.get("TESTPILOT_F13_LIVE") == "1"
    original_ai = live and os.environ.get("TESTPILOT_F13_INITIAL_AI") == "1"
    capture = os.environ.get("TESTPILOT_F13_CAPTURE") == "1"
    folder = ROOT / "reports/phase04"
    source = (ROOT / "eval/phase04/bonus.py").read_text("utf8")
    project = api("/api/projects", {"name": "Mutation evaluation"})
    version = api(f"/api/projects/{project['id']}/files", {"filename": "bonus.py", "source": source})
    task = api(f"/api/engine/files/{version['id']}/tasks", {"target": "bonus", "max_repairs": 0,
               "generation_mode": "configured" if original_ai else "template"})
    last = task["records"][-1]["payload"]["final_execution_id"]
    original = next(r for r in task["records"] if r["id"] == last)["payload"]
    suite = next(r for r in task["records"] if r["id"] == original["generated_test_id"])["payload"]
    tag = "initial-ai" if original_ai else "local-ai" if live else "before"
    if capture:
        (folder / (tag+"-task.json")).write_text(json.dumps(task, ensure_ascii=False), encoding="utf8")
    if original_ai:
        assert suite["mode"] == "ai", (suite["fallback_reason"], suite["attempts"])
    assert task["status"] == "completed" and original["status"] == "passed", original["log"]
    row = api("/api/engine/tasks/"+task["id"]+"/mutations", {"feedback": live})
    route = "/api/mutations/" + row["id"]
    assert row["before"] is None and len(row["manifest"]) == 9
    assert row["suite_id"] == original["generated_test_id"] and row["test_sha256"] == suite["sha256"]
    html = http("/mutations?task_id="+task["id"]).decode("utf8")
    assert "变异测试" in html and "ws://" not in html
    result = api(route+"/run", {})
    exported = http(route+"/report")
    report = json.loads(exported)
    if capture:
        (folder / (tag+"-experiment.json")).write_bytes(exported)
    assert api("/api/files/"+str(version["id"]))["sha256"] == report["source_sha256"] == version["sha256"]
    assert result["before"] == report["before"]
    before = report["before"]
    assert before["total"] == 9 and before["unrun"] == 0 and before["killed"] > 0
    assert before["score_pct"] == round(100 * before["killed"]/9, 2)
    before_results = [e for e in report["events"] if e["phase"] == "before" and e["kind"] == "observation"]
    ids = {m["id"] for m in row["manifest"]}
    assert {e["mutant_id"] for e in before_results} == ids
    for event in before_results:
        ex = event["payload"]["execution"]
        assert ex["test_sha256"] == row["test_sha256"] and ex["source_sha256"] != row["source_sha256"]
        if event["status"] == "killed":
            assert ex["result_complete"] and ex["errors"] == 0 and event["payload"]["nodeids"]
    print("baseline suite", suite["mode"], suite["sha256"], "before", before, flush=True)
    if live:
        fb = next((e["payload"] for e in report["events"] if e["kind"] == "feedback"), {})
        print("local feedback", result["status"], fb.get("status"), fb.get("model"), fb.get("reason"),
              "after", result["after"], flush=True)
        assert fb.get("mode") == "ai" and fb["code"].startswith(suite["code"])
        assert fb["attempts"][-1]["raw"] and result["after"]["total"] == before["total"]
        assert {e["mutant_id"] for e in report["events"] if e["phase"] == "after" and e["kind"] == "observation"} == ids
    else:
        assert result["after"] is None
    assert result["status"] == "completed", result["diagnostic"]
    assert api(route+"/run", {}) == result
