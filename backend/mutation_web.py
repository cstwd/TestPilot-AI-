"""Same-origin mutation campaign controls."""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from . import mutation_store as store
from .mutation_flow import cancel_session, run_session
from .store import connect, many, one


class Options(BaseModel):
    feedback: bool = True
    timeout_s: int = Field(default=15, ge=1, le=60)


def register(app, templates):
    router = APIRouter()

    @router.post("/api/engine/tasks/{task_id}/mutations", status_code=201)
    def create(task_id: str, options: Options, request: Request):
        path = request.app.state.db_path
        return store.read(path, store.create(path, task_id, options.feedback, options.timeout_s))

    @router.get("/api/mutations/{key}")
    def progress(key: str, request: Request):
        return store.read(request.app.state.db_path, key)

    @router.post("/api/mutations/{key}/run")
    def execute(key: str, request: Request):
        return run_session(request.app.state.db_path, key)

    @router.post("/api/mutations/{key}/cancel")
    def cancel(key: str, request: Request):
        return cancel_session(request.app.state.db_path, key)

    @router.get("/api/mutations/{key}/report")
    def export(key: str, request: Request):
        report = store.read(request.app.state.db_path, key, full=True)
        return JSONResponse(report, headers={"Content-Disposition": f'attachment; filename="mutation-{report["id"]}.json"'})

    @router.get("/mutations", include_in_schema=False)
    def page(task_id: str, request: Request):
        with connect(request.app.state.db_path) as db:
            task = one(db, "SELECT t.id,t.target,t.status,f.filename,f.revision FROM engine_tasks t "
                       "JOIN files f ON f.id=t.file_id WHERE t.id=?", (task_id,))
            sessions = many(db, "SELECT id,created_at,status FROM mutation_sessions WHERE task_id=? ORDER BY created_at DESC",
                            (task_id,))
        return templates.TemplateResponse(request=request, name="mutations.html", context={"task": task, "sessions": sessions})

    app.include_router(router)
