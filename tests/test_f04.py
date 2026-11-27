import pytest
from fastapi import HTTPException

from backend import projects, runs


def test_real_execution_and_history(sample_workspace):
    req, project, versions, suite = sample_workspace
    run = runs.execute_suite(suite["id"], runs.RunInput(file_id=versions[0]["id"]), req)
    assert run["status"] == "failed", run["log"]
    assert run["failed"] == 1 and run["passed"] >= 2
    assert any(c["outcome"] == "failed" and "test_example_3" in c["nodeid"] for c in run["cases"])
    assert "test_example_3" in run["log"] and run["coverage_pct"] is not None
    assert runs.read_run(run["id"], req) == run
    assert runs.list_runs(project["id"], req)[0]["suite_id"] == suite["id"]


def test_wrong_file_refused(sample_workspace):
    req, project, _, suite = sample_workspace
    other = projects.import_file(project["id"], projects.FileInput(filename="other.py", source=""), req)
    with pytest.raises(HTTPException) as error:
        runs.execute_suite(suite["id"], runs.RunInput(file_id=other["id"]), req)
    assert error.value.status_code == 422
