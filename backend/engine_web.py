"""Local HTML and JSON interfaces to the Phase 03 evidence history."""
import os
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

from . import engine_history as history
from .engine_analyzer import analyze_source
from .store import connect, many, one


class TaskInput(BaseModel):
    target: str = Field(min_length=1, max_length=256)
    max_repairs: int = Field(default=1, ge=0, le=3)
    generation_mode: Literal["configured", "template"] = "configured"


def latest(task, kind):
    return next((item["payload"] for item in reversed(task["records"]) if item["kind"] == kind.value), {})


def register(app, templates):
    router = APIRouter()
    kind = history.RecordKind

    @router.get("/api/engine/files/{file_id}/analysis")
    def analyze_file(file_id: int, request: Request):
        with connect(request.app.state.db_path) as db:
            row = one(db, "SELECT source FROM files WHERE id=?", (file_id,))
        return analyze_source(row["source"])

    @router.post("/api/engine/files/{file_id}/tasks", status_code=201)
    def run(file_id: int, item: TaskInput, request: Request):
        from .engine_flow import run_task
        return run_task(request.app.state.db_path, file_id, item.target, item.max_repairs, item.generation_mode)

    @router.get("/api/engine/files/{file_id}/tasks")
    def list_tasks(file_id: int, request: Request):
        return history.task_list(request.app.state.db_path, file_id)

    @router.get("/api/engine/tasks/{task_id}")
    def task_detail(task_id: str, request: Request):
        return history.read_task(request.app.state.db_path, task_id)

    @router.get("/api/engine/tasks/{task_id}/report")
    def export_task(task_id: str, request: Request):
        task = task_detail(task_id, request)
        return JSONResponse(task, headers={"Content-Disposition": f'attachment; filename="task-{task["id"]}.json"'})

    @router.get("/api/engine/tasks/{task_id}/tests")
    def export_tests(task_id: str, request: Request):
        task = task_detail(task_id, request)
        generated = latest(task, kind.generated)
        if not generated.get("code"):
            raise HTTPException(404, "尚无可下载的测试文件")
        return PlainTextResponse(generated["code"], headers={
            "Content-Disposition": 'attachment; filename="test_generated.py"'})

    @router.get("/engine", include_in_schema=False)
    def page(request: Request, file_id: int | None = None, task_id: str | None = None):
        path = request.app.state.db_path
        task = task_detail(task_id, request) if task_id else None
        with connect(path) as db:
            files = many(db, "SELECT f.id,f.filename,f.revision,p.name AS project FROM files f "
                         "JOIN projects p ON p.id=f.project_id ORDER BY f.id DESC")
        if task:
            file_id = task["file_id"]
        elif file_id is None and files:
            file_id = files[0]["id"]
        provider = os.environ.get("TESTPILOT_MODEL_PROVIDER", "").lower()
        model = os.environ.get("TESTPILOT_MODEL_NAME", "")
        configuration = (f"已配置 {provider} / {model}，可用性以实际调用为准"
                         if model and provider in {"ollama", "openai", "openai-compatible"}
                         else "当前使用本地模板")
        context = dict(task=task, files=files, file_id=file_id, analysis=None, history=[],
                       configuration=configuration)
        if file_id is not None:
            context.update(analysis=analyze_file(file_id, request), history=history.task_list(path, file_id))
        if task:
            context.update(summary=latest(task, kind.report), generation=latest(task, kind.generated),
                           execution=latest(task, kind.execution),
                           findings=latest(task, kind.failure).get("findings", []))
        return templates.TemplateResponse(request=request, name="engine.html", context=context)

    app.include_router(router)
