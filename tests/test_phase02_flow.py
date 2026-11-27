"""Black-box acceptance: drive a real main.py service, sandbox and SQLite via HTTP."""
import hashlib
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

import pytest

from test_dashboard import app_url  # shared real main.py / temporary database fixture


SAMPLES = Path(__file__).resolve().parents[1] / "eval" / "phase02"
FAILED_CASE = "test_generated.py::test_example_3"


def test_real_defect_to_regression_report(app_url):
    client = build_opener(ProxyHandler({}))

    def request(path, body=None, *, report_copy=None):
        encoded = None if body is None else json.dumps(body).encode("utf-8")
        req = Request(app_url + "/api" + path, data=encoded, headers={"Content-Type": "application/json"})
        try:
            with client.open(req, timeout=120) as response:
                content = response.read()
                if report_copy is not None:
                    assert response.headers["Content-Disposition"].startswith("attachment;")
                    if os.getenv("TESTPILOT_CAPTURE_REPORTS") == "1":
                        destination = SAMPLES.parents[1] / "reports" / "phase02" / report_copy
                        destination.write_bytes(content)
                return json.loads(content)
        except HTTPError as error:
            pytest.fail(f"{req.get_method()} {path}: HTTP {error.code} {error.read().decode('utf-8', 'replace')}")

    project = request("/projects", {"name": "magnitude regression acceptance"})

    def import_revision(folder):
        source = (SAMPLES / folder / "magnitude.py").read_text(encoding="utf-8")
        version = request(f"/projects/{project['id']}/files", {"filename": "magnitude.py", "source": source})
        assert version["sha256"] == hashlib.sha256(source.encode("utf-8")).hexdigest()
        return version

    old = import_revision("buggy")
    analysis = request(f"/files/{old['id']}/analysis")
    assert analysis["valid"] and analysis["sha256"] == old["sha256"]
    symbol, = analysis["symbols"]
    assert (symbol["name"], symbol["line"], symbol["returns"]) == ("magnitude", 1, "int")
    generate_path = f"/files/{old['id']}/suites"
    generate_input = {"target": symbol["name"], "mode": "template"}
    suite = request(generate_path, generate_input)
    assert suite["mode"] == "template" and suite["file_id"] == old["id"]
    assert "assert target(-3) == 3" in suite["source"]

    initial = suite["initial_run"]
    assert initial and initial["status"] == "failed", suite
    assert request(generate_path, generate_input) == suite
    assert request(f"/suites/{suite['id']}") == suite
    assert [r["id"] for r in request(f"/projects/{project['id']}/runs")] == [initial["id"]]
    failed = request(f"/runs/{initial['id']}")
    assert failed["status"] == "failed", failed
    assert failed["file_id"] == old["id"] and failed["suite_id"] == suite["id"]
    assert {entry["nodeid"]: entry["outcome"] for entry in failed["cases"]}[FAILED_CASE] == "failed"
    assert FAILED_CASE in failed["log"] and "AssertionError" in failed["log"]
    bug = request(f"/runs/{failed['id']}/bugs", {"nodeid": FAILED_CASE, "title": "magnitude returns a negative value"})
    assert (bug["status"], bug["nodeid"], bug["run_id"]) == ("open", FAILED_CASE, failed["id"])
    fixed = import_revision("fixed")
    assert (old["revision"], fixed["revision"]) == (1, 2)
    assert old["sha256"] != fixed["sha256"]
    closed = request(f"/bugs/{bug['id']}/regressions", {"file_id": fixed["id"]})
    assert closed["status"] == "resolved", closed
    regression, = closed["regressions"]
    assert regression["file_id"] == fixed["id"]
    passed = request(f"/runs/{regression['run_id']}")
    assert passed["id"] != failed["id"] and passed["status"] == "passed", passed
    assert passed["suite_id"] == suite["id"]
    assert {entry["nodeid"]: entry["outcome"] for entry in passed["cases"]}[FAILED_CASE] == "passed"
    assert request(f"/bugs/{bug['id']}") == closed

    for run, version, failures in [(failed, old, 1), (passed, fixed, 0)]:
        report_path = f"/runs/{run['id']}/report"
        report = request(report_path)
        artifact = "buggy-report.json" if failures else "fixed-report.json"
        exported = request(report_path + "/export", report_copy=artifact)
        assert report == exported
        assert report["run"]["id"] == run["id"]
        assert report["source"]["id"] == version["id"]
        assert report["source"]["sha256"] == version["sha256"]
        assert report["suite"]["id"] == suite["id"] and report["suite"]["sha256"] == suite["sha256"]
        assert any(item["id"] == bug["id"] for item in report["bugs"])
        quality = report["quality"]
        assert quality["failed"] == failures and quality["errors"] == 0
        for metric in ("passed", "failed", "errors", "skipped", "coverage_pct"):
            assert quality[metric] == run[metric]
        assert quality["passed"] >= 5 and 0 <= quality["coverage_pct"] <= 100
        counts = {key: quality[key] for key in ("passed", "failed", "errors", "skipped", "pass_rate_pct", "coverage_pct")}
        print(f"run={run['id']} file_revision={version['revision']} suite={suite['id']} "
              f"status={run['status']} node={FAILED_CASE} metrics={counts}")
    assert request(f"/runs/{failed['id']}") == failed
