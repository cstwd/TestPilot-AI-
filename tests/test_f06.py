import json
import pytest

from backend import bugs, quality, runs


def test_report_matches_real_run(sample_workspace):
    req, _, (old, _), suite = sample_workspace
    run = runs.run_suite(req.app.state.db_path, suite["id"], old["id"])
    case = next(c for c in run["cases"] if c["outcome"] == "failed")
    issue = bugs.open_bug(run["id"], bugs.BugInput(title="负数", nodeid=case["nodeid"]), req)
    report = quality.report(run["id"], req)
    assert report["quality"]["total"] == len(run["cases"])
    assert report["quality"]["pass_rate_pct"] == round(100 * run["passed"] / (run["passed"] + run["failed"]), 2)
    assert report["source"]["sha256"] == old["sha256"] and report["suite"]["sha256"] == suite["sha256"]
    assert report["quality"]["coverage_pct"] == run["coverage_pct"]
    assert report["bugs"][0]["id"] == issue["id"] and report["log"] == run["log"]
    response = quality.export(run["id"], req)
    assert json.loads(response.body) == report and "attachment" in response.headers["Content-Disposition"]


@pytest.mark.parametrize("status", ["timeout", "error", "skipped"])
def test_missing_measures(status):
    result = quality.metrics(dict(status=status, passed=0, failed=0, errors=0, skipped=int(status=="skipped"),
                                  coverage_pct=None, covered_lines=None, total_lines=None))
    assert result["pass_rate_pct"] is None and result["coverage_pct"] is None
