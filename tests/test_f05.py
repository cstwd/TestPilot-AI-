import pytest
from fastapi import HTTPException

from backend import bugs, generation, projects, runs


def test_bug_regression(sample_workspace):
    req, project, (old, fixed), suite = sample_workspace
    failed = runs.run_suite(req.app.state.db_path, suite["id"], old["id"])
    with pytest.raises(HTTPException):
        bugs.open_bug(failed["id"], bugs.BugInput(title="x", nodeid="not-a-case"), req)
    nodeid = next(c["nodeid"] for c in failed["cases"] if c["outcome"] == "failed")
    item = bugs.BugInput(title="负数的绝对值返回了负数", nodeid=nodeid)
    issue = bugs.open_bug(failed["id"], item, req)
    assert bugs.open_bug(failed["id"], item, req)["id"] == issue["id"]
    with pytest.raises(HTTPException):
        bugs.regress(issue["id"], runs.RunInput(file_id=old["id"]), req)
    closed = bugs.regress(issue["id"], runs.RunInput(file_id=fixed["id"]), req)
    assert closed["status"] == "resolved" and closed["run_id"] == failed["id"]
    rerun = runs.read_run(closed["regressions"][0]["run_id"], req)
    assert rerun["suite_id"] == suite["id"] and rerun["status"] == "passed"
    assert bugs.list_bugs(project["id"], req)[0]["status"] == "resolved"
    assert runs.read_run(failed["id"], req) == failed


def test_regression_uses_database_filename_identity(sample_workspace):
    req, project, _, _ = sample_workspace
    files = [projects.import_file(project["id"], projects.FileInput(filename=name, source="def f(): return 1"), req)
             for name in ("Ä.py", "ä.py")]
    suite = generation.generate(files[0]["id"], generation.GenerateInput(target="f"), req)
    with pytest.raises(HTTPException) as error:
        runs.run_suite(req.app.state.db_path, suite["id"], files[1]["id"])
    assert error.value.status_code == 422
