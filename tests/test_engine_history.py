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
    first = history.append_record(path, task, history.RecordKind.analysis, "ready", {"file": original["id"]})
    with pytest.raises(ValueError):
        history.append_record(path, task, history.RecordKind.strategy, "error", {}, terminal="error")
    last = history.append_record(path, task, history.RecordKind.report, "completed", {}, terminal="completed")
    with pytest.raises(ValueError):
        history.append_record(path, task, history.RecordKind.generated, "ready", {"code": ""})
    saved = history.read_task(path, task)
    assert saved["status"] == "completed" and history.task_list(path, original["id"])[0]["id"] == task
    assert [r["id"] for r in saved["records"]] == [first, last]
    assert saved["records"][1]["parent_id"] == first
