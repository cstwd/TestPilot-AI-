"""Immutable experiment manifests, checkpointed observations and read-only reports."""
import json
from uuid import uuid4

from fastapi import HTTPException

from .engine_history import read_task, stamp
from .mutation_generator import PROFILE, digest, make_plan
from .mutation_results import score
from .store import connect, one


SCHEMA = (
    """CREATE TABLE IF NOT EXISTS mutation_sessions (
        id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES engine_tasks(id),
        file_id INTEGER NOT NULL REFERENCES files(id), suite_id TEXT NOT NULL REFERENCES engine_records(id),
        target TEXT NOT NULL, profile TEXT NOT NULL, source_sha256 TEXT NOT NULL, test_sha256 TEXT NOT NULL,
        manifest TEXT NOT NULL, feedback_enabled INTEGER NOT NULL, timeout_s INTEGER NOT NULL,
        status TEXT NOT NULL, cancel_requested INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL, diagnostic TEXT NOT NULL DEFAULT '')""",
    "CREATE INDEX IF NOT EXISTS mutation_task ON mutation_sessions(task_id,created_at)",
    """CREATE TABLE IF NOT EXISTS mutation_events (
        seq INTEGER PRIMARY KEY, id TEXT NOT NULL UNIQUE, session_id TEXT NOT NULL REFERENCES mutation_sessions(id),
        phase TEXT NOT NULL, kind TEXT NOT NULL, mutant_id TEXT NOT NULL,
        created_at TEXT NOT NULL, status TEXT NOT NULL, reason TEXT NOT NULL, payload TEXT NOT NULL,
        UNIQUE(session_id,phase,kind,mutant_id))""",
)


def create(path, task_id, feedback_enabled=True, timeout_s=15):
    task = read_task(path, task_id)
    records = {r["id"]: r for r in task["records"]}
    if task["status"] != "completed" or not task["records"] or task["records"][-1]["kind"] != "TestReport":
        raise HTTPException(409, "请选择已完成并保留实际执行记录的引擎任务")
    final = records.get(task["records"][-1]["payload"].get("final_execution_id"))
    suite = records.get(final["payload"].get("generated_test_id")) if final and final["kind"] == "TestExecution" else None
    if not suite or suite["kind"] != "GeneratedTest":
        raise HTTPException(409, "原任务缺少最终执行对应的生成测试")
    with connect(path) as db:
        file = one(db, "SELECT source,sha256 FROM files WHERE id=?", (task["file_id"],))
    test_sha = digest(suite["payload"]["code"])
    if (digest(file["source"]) != file["sha256"] or final["payload"].get("source_sha256") != file["sha256"]
            or suite["payload"]["sha256"] != test_sha or final["payload"].get("test_sha256") != test_sha):
        raise HTTPException(409, "原任务与文件或测试的摘要不一致")
    try:
        manifest = make_plan(file["source"], task["target"])
    except (ValueError, SyntaxError, RecursionError) as exc:
        raise HTTPException(422, str(exc)) from exc
    key, now = str(uuid4()), stamp()
    with connect(path, write=True) as db:
        db.execute("INSERT INTO mutation_sessions(id,task_id,file_id,suite_id,target,profile,source_sha256,"
                   "test_sha256,manifest,feedback_enabled,timeout_s,status,created_at,updated_at) "
                   "VALUES(?,?,?,?,?,?,?,?,?,?,?,'ready',?,?)",
                   (key, task_id, task["file_id"], suite["id"], task["target"], PROFILE, file["sha256"], test_sha,
                    json.dumps(manifest, ensure_ascii=False), int(feedback_enabled), timeout_s, now, now))
    return key


def preview(value, limit):
    return value if value is None or len(value) <= limit else value[:limit] + "…（完整内容见实验 JSON）"


def event_summary(kind, payload):
    """Project only user-facing evidence. Preserve full prompts and logs in the export."""
    if kind == "feedback":
        return {
            **{key: payload.get(key) for key in ("provider", "model", "requested_model", "mode")},
            "added_code": preview(payload.get("added_code"), 16000),
            "cases": [{key: preview(case.get(key), 600) for key in
                       ("call", "expected", "reason", "test_name", "mutant_id")} for case in payload.get("cases", [])],
            "attempts": [{key: attempt.get(key) for key in ("number", "focus_id", "status", "reason")}
                         for attempt in payload.get("attempts", []) if attempt.get("status") != "accepted"],
            "pending_ids": payload.get("pending_ids", []),
        }
    if kind == "selection":
        return {key: payload.get(key, []) for key in ("accepted_names", "rejected_names")}
    return {
        **{key: payload.get(key) for key in ("status", "exit_code", "passed", "failed", "errors", "skipped")},
        "diagnostic": preview(payload.get("diagnostic"), 450),
        "failures": [{"nodeid": f.get("nodeid"), "exception_type": f.get("exception_type"),
                      "message": preview(f.get("message"), 350)} for f in payload.get("failures", [])[:4]],
    }


def events_for(db, key, full):
    # Observation payloads include captured output and tracebacks; polling only needs their verdict.
    payload_column = "payload" if full else "CASE WHEN kind IN ('feedback','baseline','validation','selection') THEN payload END AS payload"
    columns = "id,phase,kind,mutant_id,created_at,status,reason," + payload_column
    rows = [dict(r) for r in db.execute(f"SELECT {columns} FROM mutation_events WHERE session_id=? ORDER BY seq", (key,))]
    for row in rows:
        raw = row.pop("payload")
        if raw is not None:
            payload = json.loads(raw)
            if full:
                row["payload"] = payload
            else:
                row["summary"] = event_summary(row["kind"], payload)
    return rows


def read(path, key, full=False):
    with connect(path) as db:
        db.execute("BEGIN")
        row = one(db, "SELECT * FROM mutation_sessions WHERE id=?", (key,))
        events = events_for(db, key, full)
    plan = json.loads(row.pop("manifest"))
    row.update(manifest=plan, events=events, feedback_enabled=bool(row["feedback_enabled"]),
               cancel_requested=bool(row["cancel_requested"]))
    for phase in ("before", "after"):
        outcomes = {e["mutant_id"]: e for e in events if e["phase"] == phase and e["kind"] == "observation"}
        ready = any(e["phase"] == phase and e["kind"] == "baseline" and e["status"] == "passed" for e in events)
        row[phase] = score(plan, outcomes) if ready else None
    return row


def inputs(path, row):
    with connect(path) as db:
        source = one(db, "SELECT source FROM files WHERE id=?", (row["file_id"],))["source"]
        payload = one(db, "SELECT payload FROM engine_records WHERE task_id=? AND id=? AND kind='GeneratedTest'",
                      (row["task_id"], row["suite_id"]))["payload"]
    code = json.loads(payload)["code"]
    if digest(source) != row["source_sha256"] or digest(code) != row["test_sha256"]:
        raise ValueError("重放前摘要校验失败")
    return source, code


def record(path, key, phase, kind, status, reason, payload, mutant_id=""):
    now = stamp()
    with connect(path, write=True) as db:
        db.execute("INSERT INTO mutation_events(id,session_id,phase,kind,mutant_id,created_at,status,reason,payload) "
                   "VALUES(?,?,?,?,?,?,?,?,?)", (str(uuid4()), key, phase, kind, mutant_id, now, status, reason,
                                                json.dumps(payload, ensure_ascii=False, allow_nan=False)))
        db.execute("UPDATE mutation_sessions SET updated_at=? WHERE id=?", (now, key))


def state(path, key, status, diagnostic=""):
    with connect(path, write=True) as db:
        db.execute("UPDATE mutation_sessions SET status=CASE WHEN cancel_requested=1 THEN 'cancelled' ELSE ? END,"
                   "updated_at=?,diagnostic=? WHERE id=?", (status, stamp(), diagnostic, key))


def cancel(path, key):
    with connect(path, write=True) as db:
        one(db, "SELECT id FROM mutation_sessions WHERE id=?", (key,))
        db.execute("UPDATE mutation_sessions SET cancel_requested=1,updated_at=?,"
                   "status=CASE WHEN status='ready' THEN 'cancelled' ELSE status END "
                   "WHERE id=? AND status IN ('ready','running')", (stamp(), key))
    return read(path, key)
