"""F05 source repair contracts. The model adapter is stubbed here; WASI runs for real."""
import asyncio

import pytest
from fastapi import BackgroundTasks, HTTPException

from backend import bug_repairs, bugs, projects, runs
from backend.bug_repair_patch import Patch, apply_patch
from backend.model_provider import ModelError, Reply
from backend.store import connect, one


def patch(line, old, new):
    return Patch.model_validate({"edits": [
        {"start_line": line, "end_line": line, "original": old,
         "replacement": new, "reason": "Correct the implementation"},
    ]})


@pytest.mark.parametrize("new", ["return x + 1", "    return (", "    return 2", "    return 2 / 1000",
                                  "    return __import__('pytest').skip()",
                                  "    return x\ndef other():\n    pass"])
def test_patch_rejects_unsafe_or_nonlocal_replacements(new):
    with pytest.raises((ValueError, SyntaxError)):
        apply_patch("def f(x):\n    return x\n", patch(2, "    return x", new))


def test_patch_preserves_line_endings_and_checks_original():
    source = "def f(x):\r\n    return x\r\n"
    assert apply_patch(source, patch(2, "    return x", "    return abs(x)")) == (
        "def f(x):\r\n    return abs(x)\r\n")
    with pytest.raises(ValueError, match="原文"):
        apply_patch(source, patch(2, "    return -x", "    return abs(x)"))


def test_source_repair_and_real_regression(sample_workspace, monkeypatch):
    req, project, (old, manual_fix), suite = sample_workspace
    path = req.app.state.db_path
    failed = runs.run_suite(path, suite["id"], old["id"])
    nodeid = next(case["nodeid"] for case in failed["cases"] if case["outcome"] == "failed")
    issue = bugs.open_bug(failed["id"], bugs.BugInput(title="Magnitude contract", nodeid=nodeid), req)
    changed = len(old["source"].splitlines())
    key = issue["id"]
    assert bug_repairs.latest(key, req) == {"repair": None}
    transitions = []
    server_requests = [True]

    def infer(operation, messages, schema, *, max_tokens, validate, check_gpu):
        assert check_gpu and max_tokens > 0
        assert nodeid in messages[1]["content"]
        assert "unchanged_tests" in messages[1]["content"]
        assert "pytest_log" in messages[1]["content"]
        current = bug_repairs.latest(key, req)["repair"]
        transitions.append(current["state"])
        if current["state"] == "analyzing":
            duplicate = BackgroundTasks()
            assert bug_repairs.start(key, req, duplicate)["id"] == current["id"]
            assert not duplicate.tasks
        elif server_requests:
            server_requests.pop()
            raise ModelError("schema", "Invalid proposed patch", "failed-id", [{"raw": "bad response"}])
        value = (schema.model_validate({
            "cause": "Returns a negative value", "line": changed, "expected": "Absolute magnitude",
            "observed": "Negative magnitude", "plan": "Return abs(x)",
        }) if operation.endswith("analysis") else patch(changed, "    return x", "    return abs(x)"))
        return Reply(operation, validate(value), [{"raw": value.model_dump_json()}])

    monkeypatch.setattr(bug_repairs.provider, "infer", infer)
    def run_request():
        tasks = BackgroundTasks()
        assert bug_repairs.start(key, req, tasks)["state"] == "queued"
        asyncio.run(tasks())

    run_request()
    rejected = bug_repairs.latest(key, req)["repair"]
    assert rejected["state"] == "failed" and rejected["generation_run_id"] == "failed-id"
    with pytest.raises(HTTPException) as exc:
        bug_repairs.apply(key, rejected["id"], req)
    assert exc.value.status_code == 409
    run_request()
    ready = bug_repairs.latest(key, req)["repair"]
    assert ready["state"] == "ready" and ready["analysis_run_id"] == "bug-repair-analysis"
    assert transitions == ["analyzing", "generating"] * 2
    assert projects.list_files(project["id"], req)[0]["id"] == manual_fix["id"]
    with connect(path, write=True) as db:
        db.execute("UPDATE suites SET source=? WHERE id=?", (suite["source"] + "\n# altered", suite["id"]))
    with pytest.raises(HTTPException) as exc:
        bug_repairs.apply(key, ready["id"], req)
    assert exc.value.status_code == 409
    with connect(path, write=True) as db:
        db.execute("UPDATE suites SET source=? WHERE id=?", (suite["source"], suite["id"]))
    saved = bug_repairs.apply(key, ready["id"], req)
    assert saved["source"] == manual_fix["source"] and saved["revision"] == manual_fix["revision"] + 1
    assert bug_repairs.apply(key, ready["id"], req) == saved
    assert bug_repairs.latest(key, req)["repair"]["state"] == "applied"
    assert bugs.read_bug(issue["id"], req)["status"] == "open"

    closed = bugs.regress(key, runs.RunInput(file_id=saved["id"]), req)
    assert closed["status"] == "resolved"
    assert bug_repairs.latest(key, req)["repair"]["applied_file_id"] == saved["id"]
    actual = runs.read_run(closed["regressions"][0]["run_id"], req)
    assert actual["result_complete"] and actual["suite_id"] == suite["id"] and actual["file_id"] == saved["id"]
    assert runs.read_run(failed["id"], req) == failed
    assert projects.read_file(old["id"], req) == old
    with connect(path) as db:
        assert one(db, "SELECT sha256 FROM suites WHERE id=?", (suite["id"],))["sha256"] == suite["sha256"]
        assert "bad response" in one(db, "SELECT attempts FROM bug_repairs WHERE id=?", (rejected["id"],))["attempts"]
