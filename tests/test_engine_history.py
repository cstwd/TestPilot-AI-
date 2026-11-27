import pytest

from backend import engine_history as history
from backend.store import connect


def test_atomic_immutable_history(sample_workspace):
    req, _, files, _ = sample_workspace
    path = req.app.state.db_path
    with connect(path, write=True) as db:
        for statement in history.SCHEMA:
            db.execute(statement)
    task, original = history.create_task(path, files[0]["id"], "magnitude", 1)
    first = history.append_record(path, task, history.RecordKind.analysis, "ready",
                                  {"valid": True, "symbols": [], "diagnostics": [], "sha256": original["sha256"]})
    with pytest.raises(ValueError):
        history.append_record(path, task, history.RecordKind.strategy, "error", {}, terminal="error")
    last = history.append_record(path, task, history.RecordKind.report, "completed",
                                 {"stop_reason": "verified", "initial_execution_id": None,
                                  "final_execution_id": None}, terminal="completed")
    with pytest.raises(ValueError):
        history.append_record(path, task, history.RecordKind.generated, "ready", {"code": ""})
    saved = history.read_task(path, task)
    assert saved["status"] == "completed" and history.task_list(path, original["id"])[0]["id"] == task
    assert [r["id"] for r in saved["records"]] == [first, last]
    assert saved["records"][1]["parent_id"] == first


def test_report_references_own_execution(sample_workspace):
    req, _, files, _ = sample_workspace
    path = req.app.state.db_path
    with connect(path, write=True) as db:
        for statement in history.SCHEMA:
            db.execute(statement)
    task, source = history.create_task(path, files[0]["id"], "magnitude", 1)
    other, _ = history.create_task(path, source["id"], "magnitude", 1)
    execution = history.append_record(path, task, history.RecordKind.execution, "ready",
                                      {"status": "error", "passed": 0, "failed": 0, "errors": 0, "skipped": 0,
                                       "cases": [], "stdout": "", "stderr": "fixture", "exit_code": None,
                                       "result_complete": False})
    summary = {"stop_reason": "fixture", "initial_execution_id": execution, "final_execution_id": execution}
    with pytest.raises(ValueError, match="TestExecution"):
        history.append_record(path, other, history.RecordKind.report, "error", summary, terminal="error")
    assert history.read_task(path, other)["records"] == []
    analysis = history.append_record(path, task, history.RecordKind.analysis, "ready",
                                     {"valid": True, "symbols": [], "diagnostics": [], "sha256": source["sha256"]})
    with pytest.raises(ValueError, match="TestExecution"):
        history.append_record(path, task, history.RecordKind.report, "error", dict(summary, final_execution_id=analysis))
    history.append_record(path, task, history.RecordKind.report, "error", summary, terminal="error")
    assert history.read_task(path, task)["status"] == "error"
