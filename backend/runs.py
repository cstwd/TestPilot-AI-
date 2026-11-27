"""Bind sandbox results to immutable test and source revisions."""
import json
from threading import BoundedSemaphore

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from .store import connect, many, one

router = APIRouter(prefix="/api")
SLOTS = BoundedSemaphore(1)
SCHEMA = ("""CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL REFERENCES projects(id),
    file_id INTEGER NOT NULL REFERENCES files(id), suite_id INTEGER NOT NULL REFERENCES suites(id),
    status TEXT NOT NULL, duration_ms INTEGER NOT NULL, result TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')))""",)
SUMMARY = "id,project_id,file_id,suite_id,status,duration_ms,created_at"


class RunInput(BaseModel):
    file_id: int


def run_record(db, key):
    row = one(db, "SELECT * FROM runs WHERE id=?", (key,))
    result = json.loads(row.pop("result"))
    return {**result, **row}


def run_suite(path, suite_id, file_id):
    with connect(path) as db:
        suite = one(db, "SELECT s.source,s.sha256,f.project_id,f.filename FROM suites s JOIN files f "
                        "ON f.id=s.file_id WHERE s.id=?", (suite_id,))
        file = one(db, "SELECT * FROM files WHERE id=?", (file_id,))
    if file["project_id"] != suite["project_id"] or file["filename"].lower() != suite["filename"].lower():
        raise HTTPException(422, "仅可对同一项目的同名文件运行该套件")
    if not SLOTS.acquire(blocking=False):
        raise HTTPException(409, "已有受限运行在进行，请稍后重试")
    try:
        from .runner import execute
        result = execute(file["source"], suite["source"])
        with connect(path, write=True) as db:
            key = db.execute("INSERT INTO runs(project_id,file_id,suite_id,status,duration_ms,result) "
                             "VALUES (?,?,?,?,?,?)", (file["project_id"], file_id, suite_id, result["status"],
                              result["duration_ms"], json.dumps(result, ensure_ascii=False))).lastrowid
            return run_record(db, key)
    finally:
        SLOTS.release()


@router.post("/suites/{suite_id}/runs")
def execute_suite(suite_id: int, item: RunInput, request: Request):
    return run_suite(request.app.state.db_path, suite_id, item.file_id)


@router.get("/projects/{project_id}/runs")
def list_runs(project_id: int, request: Request):
    with connect(request.app.state.db_path) as db:
        one(db, "SELECT id FROM projects WHERE id=?", (project_id,))
        return many(db, f"SELECT {SUMMARY} FROM runs WHERE project_id=? ORDER BY id DESC", (project_id,))


@router.get("/runs/{run_id}")
def read_run(run_id: int, request: Request):
    with connect(request.app.state.db_path) as db:
        return run_record(db, run_id)
