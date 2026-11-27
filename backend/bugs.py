"""Track reviewed failures and preserve each regression against the original suite."""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .runs import RunInput, run_record, run_suite
from .store import connect, many, one

router = APIRouter(prefix="/api")
SCHEMA = ("""CREATE TABLE IF NOT EXISTS bugs (
    id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL REFERENCES projects(id),
    run_id INTEGER NOT NULL REFERENCES runs(id), nodeid TEXT NOT NULL, title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open', UNIQUE(run_id,nodeid))""",
    """CREATE TABLE IF NOT EXISTS regressions (
    id INTEGER PRIMARY KEY, bug_id INTEGER NOT NULL REFERENCES bugs(id),
    run_id INTEGER UNIQUE NOT NULL REFERENCES runs(id), status TEXT NOT NULL)""")
DETAIL = "SELECT b.*,r.file_id,r.suite_id FROM bugs b JOIN runs r ON r.id=b.run_id"


class BugInput(BaseModel):
    nodeid: str = Field(min_length=1, max_length=2048)
    title: str = Field(min_length=1, max_length=180)


def bug_record(db, key):
    row = one(db, DETAIL + " WHERE b.id=?", (key,))
    row["regressions"] = many(db, "SELECT g.id,g.run_id,g.status,r.file_id,f.revision FROM regressions g "
                              "JOIN runs r ON r.id=g.run_id JOIN files f ON f.id=r.file_id "
                              "WHERE g.bug_id=? ORDER BY f.revision DESC,g.id DESC", (key,))
    return row


@router.post("/runs/{run_id}/bugs")
def open_bug(run_id: int, item: BugInput, request: Request):
    title = item.title.strip()
    if not title:
        raise HTTPException(422, "请输入缺陷标题")
    with connect(request.app.state.db_path, write=True) as db:
        run = run_record(db, run_id)
        if "::" not in item.nodeid:
            raise HTTPException(422, "收集错误请查看日志；登记回归缺陷需要可重跑的测试项")
        if run["status"] not in {"failed", "error"} or not any(
            c["nodeid"] == item.nodeid and c["outcome"] in {"failed", "error"} for c in run["cases"]
        ):
            raise HTTPException(422, "仅可从有真实失败或错误证据的用例建立缺陷")
        db.execute("INSERT OR IGNORE INTO bugs(project_id,run_id,nodeid,title) VALUES (?,?,?,?)",
                   (run["project_id"], run_id, item.nodeid, title))
        key = one(db, "SELECT id FROM bugs WHERE run_id=? AND nodeid=?", (run_id, item.nodeid))["id"]
        return bug_record(db, key)


@router.get("/projects/{project_id}/bugs")
def list_bugs(project_id: int, request: Request):
    with connect(request.app.state.db_path) as db:
        one(db, "SELECT id FROM projects WHERE id=?", (project_id,))
        return many(db, DETAIL + " WHERE b.project_id=? ORDER BY b.id DESC", (project_id,))


@router.get("/bugs/{bug_id}")
def read_bug(bug_id: int, request: Request):
    with connect(request.app.state.db_path) as db:
        return bug_record(db, bug_id)


@router.post("/bugs/{bug_id}/regressions")
def regress(bug_id: int, item: RunInput, request: Request):
    return regress_run(request.app.state.db_path, bug_id, item.file_id)


def regress_run(path, bug_id, file_id, *, detailed=False):
    with connect(path) as db:
        bug = bug_record(db, bug_id)
        old = one(db, "SELECT revision FROM files WHERE id=?", (bug["file_id"],))
        new = one(db, "SELECT revision FROM files WHERE id=?", (file_id,))
        if new["revision"] <= old["revision"]:
            raise HTTPException(422, "请选择比缺陷版本更新的同名文件版本")
        original = run_record(db, bug["run_id"]) if detailed else None

    def link_regression(db, run):
        passed = run["status"] == "passed" and any(
            c["nodeid"] == bug["nodeid"] and c["outcome"] == "passed" for c in run["cases"]
        )
        if detailed:
            expected = {case["nodeid"]: case["outcome"] == "skipped" for case in original["cases"]}
            observed = {case["nodeid"]: case["outcome"] == "skipped" for case in run["cases"]}
            passed = passed and original["result_complete"] and run["result_complete"] and expected == observed
        outcome = "resolved" if passed else "open"
        db.execute("INSERT INTO regressions(bug_id,run_id,status) VALUES (?,?,?)", (bug_id, run["id"], outcome))
        latest = bug_record(db, bug_id)["regressions"][0]
        db.execute("UPDATE bugs SET status=? WHERE id=?", (latest["status"], bug_id))

    run_suite(path, bug["suite_id"], file_id, on_saved=link_regression, detailed=detailed)
    with connect(path) as db:
        return bug_record(db, bug_id)
