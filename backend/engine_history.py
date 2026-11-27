"""Append-only, transactionally linked records for Phase 03 test tasks."""
import json
from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from .store import connect, one


class RecordKind(StrEnum):
    analysis = "SourceAnalysis"
    strategy = "TestStrategy"
    generated = "GeneratedTest"
    execution = "TestExecution"
    coverage = "CoverageResult"
    failure = "FailureAnalysis"
    repair = "RepairAttempt"
    report = "TestReport"


SCHEMA = (
    """CREATE TABLE IF NOT EXISTS engine_tasks (
        id TEXT PRIMARY KEY, file_id INTEGER NOT NULL REFERENCES files(id),
        target TEXT NOT NULL, created_at TEXT NOT NULL, status TEXT NOT NULL,
        max_repairs INTEGER NOT NULL CHECK(max_repairs BETWEEN 0 AND 3))""",
    """CREATE INDEX IF NOT EXISTS engine_tasks_file ON engine_tasks(file_id, created_at)""",
    """CREATE TABLE IF NOT EXISTS engine_records (
        seq INTEGER PRIMARY KEY, id TEXT UNIQUE NOT NULL,
        task_id TEXT NOT NULL REFERENCES engine_tasks(id),
        parent_id TEXT REFERENCES engine_records(id), kind TEXT NOT NULL,
        created_at TEXT NOT NULL, status TEXT NOT NULL, payload TEXT NOT NULL)""",
    """CREATE INDEX IF NOT EXISTS engine_records_task ON engine_records(task_id, seq)""",
)


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def create_task(path, file_id, target, max_repairs):
    task = str(uuid4())
    with connect(path, write=True) as db:
        file = one(db, "SELECT * FROM files WHERE id=?", (file_id,))
        db.execute("INSERT INTO engine_tasks VALUES (?,?,?,?,?,?)",
                   (task, file_id, target, stamp(), "running", max_repairs))
    return task, file


def append_record(path, task, kind: RecordKind, status, payload, *, terminal=None):
    """Appending a terminal report and marking the task complete is a single write."""
    key, created = str(uuid4()), stamp()
    encoded = json.dumps(payload, ensure_ascii=True, allow_nan=False, separators=(",", ":"))
    with connect(path, write=True) as db:
        if one(db, "SELECT status FROM engine_tasks WHERE id=?", (task,))["status"] != "running":
            raise ValueError("该任务已结束")
        parent = db.execute("SELECT id FROM engine_records WHERE task_id=? ORDER BY seq DESC LIMIT 1",
                            (task,)).fetchone()
        db.execute("INSERT INTO engine_records(id,task_id,parent_id,kind,created_at,status,payload) "
                   "VALUES (?,?,?,?,?,?,?)", (key, task, parent["id"] if parent else None,
                                               kind.value, created, status, encoded))
        if terminal is not None:
            if kind != RecordKind.report:
                raise ValueError("只有最终报告可以结束任务")
            db.execute("UPDATE engine_tasks SET status=? WHERE id=?", (terminal, task))
    return key


def read_task(path, task):
    with connect(path) as db:
        db.execute("BEGIN")
        result = one(db, "SELECT * FROM engine_tasks WHERE id=?", (task,))
        records = db.execute("SELECT id,task_id,parent_id,kind,created_at,status,payload FROM engine_records "
                             "WHERE task_id=? ORDER BY seq", (task,))
        result["records"] = [{**dict(row), "payload": json.loads(row["payload"])} for row in records]
    return result


def task_list(path, file_id):
    with connect(path) as db:
        one(db, "SELECT id FROM files WHERE id=?", (file_id,))
        return [dict(r) for r in db.execute("SELECT * FROM engine_tasks WHERE file_id=? ORDER BY created_at DESC",
                                            (file_id,))]
