"""Black-box Phase 03 benchmark against a real main.py, isolated SQLite and WASI."""
import hashlib
import json
import os
from pathlib import Path
from urllib.request import ProxyHandler, Request, build_opener

import pytest

from test_dashboard import app_url


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = [
    ("quicksort", "quicksort", False), ("negative", "magnitude", True),
    ("empty", "first_or_default", True), ("boundary", "valid_index", True),
    ("exception", "parse_count", True), ("branches", "classify_temperature", False),
    ("repair", "reciprocal_units", False),
]


@pytest.mark.parametrize("sample,target,defective", SAMPLES)
def test_real_engine(app_url, sample, target, defective):
    client = build_opener(ProxyHandler({}))

    def get(path, body=None):
        data = None if body is None else json.dumps(body).encode()
        request = Request(app_url + path, data=data, headers={"Content-Type": "application/json"})
        with client.open(request, timeout=240) as response:
            return response.read()

    source = (ROOT / "eval" / "phase03" / sample / "subject.py").read_text(encoding="utf-8")
    digest = hashlib.sha256(source.encode()).hexdigest()
    project = json.loads(get("/api/projects", {"name": sample}))
    file = json.loads(get(f"/api/projects/{project['id']}/files", {"filename": "subject.py", "source": source}))
    route = f"/api/engine/files/{file['id']}"
    task = json.loads(get(route + "/tasks", {"target": target, "max_repairs": 1, "generation_mode": "template"}))
    url = "/api/engine/tasks/" + task["id"]
    exported = get(url + "/report")
    assert json.loads(exported) == json.loads(get(url)) == task
    assert json.loads(get(route + "/tasks"))[0]["id"] == task["id"]
    assert json.loads(get(f"/api/files/{file['id']}"))["sha256"] == digest

    events = task["records"]
    assert all(e["parent_id"] == (events[i-1]["id"] if i else None) for i, e in enumerate(events))
    assert len({e["id"] for e in events}) == len(events)
    assert all(e["created_at"] and e["status"] and e["task_id"] == task["id"] for e in events)

    def payloads(kind):
        return [e["payload"] for e in events if e["kind"] == kind]

    analysis, = payloads("SourceAnalysis")
    assert analysis["sha256"] == digest and analysis["valid"]
    strategy, = payloads("TestStrategy")
    assert strategy["target"] == target and strategy["contracts"]
    suites = payloads("GeneratedTest")
    assert suites[0]["mode"] == "template" and suites[0]["code"]
    assert get(url + "/tests").decode() == suites[-1]["code"]
    runs = payloads("TestExecution")
    metrics = payloads("CoverageResult")
    assert len(metrics) == len(runs) and len(runs) >= 1
    assert runs[-1]["status"] == ("failed" if defective else "passed"), runs[-1]["log"]
    final = metrics[-1]
    assert 0 < final["covered_lines"] <= final["total_lines"]
    assert 0 <= final["covered_branches"] <= final["total_branches"]
    if sample in {"quicksort", "branches"}:
        assert final["total_branches"] > 0 and final["covered_branches"] > 0
    initial_findings = payloads("FailureAnalysis")[0]["findings"]
    if defective:
        confirmed = [f for f in initial_findings if f["category"] == "program_defect"]
        assert confirmed, initial_findings
        assert all(f["contract"] and f["nodeid"] for f in confirmed)
        assert len(runs) == 1
    if sample == "repair":
        assert len(runs) == 2 and runs[0]["failed"] > 0 and runs[1]["failed"] == 0
        assert any(f["category"] == "test_error" for f in initial_findings)
        assert payloads("RepairAttempt") and suites[0]["sha256"] != suites[-1]["sha256"]
    report, = payloads("TestReport")
    assert report["initial_execution_id"] and report["final_execution_id"]
    assert task["status"] == "completed"
    print(sample, [(r["passed"], r["failed"], r["errors"], r["skipped"]) for r in runs],
          final["covered_lines"], "/", final["total_lines"], "lines;",
          final["covered_branches"], "/", final["total_branches"], "branches",
          sorted({f["category"] for f in initial_findings}))
    if os.environ.get("TESTPILOT_CAPTURE_PHASE03") == "1":
        folder = ROOT / "reports" / "phase03" / "cases"
        folder.mkdir(exist_ok=True, parents=True)
        (folder / (sample + ".json")).write_bytes(exported)
