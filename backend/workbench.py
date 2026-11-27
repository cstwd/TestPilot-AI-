"""Register the phase 02 business modules on the existing application."""
from fastapi import HTTPException, Request

from . import analysis, bug_repairs, bugs, demo_lab, engine_history, engine_web, generation, mutation_store, mutation_web, projects, quality, runs
from .store import connect

MODULES = (projects, analysis, generation, runs, bugs, bug_repairs, quality)
PAGES = {"projects", "analysis", "generation", "runs", "bugs", "reports"}


def initialize(path, *, lab=False):
    with connect(path, write=True) as db:
        for module in (*MODULES, engine_history, mutation_store, *((demo_lab,) if lab else ())):
            for statement in getattr(module, "SCHEMA", ()):
                db.execute(statement)
    if lab:
        demo_lab.recover(path)


def register(app, templates, path, mode):
    app.state.db_path = path
    app.state.demo_lab_db_path = demo_lab.workspace_path(path)
    app.state.generators = {"template": generation.TemplateAdapter(), "ai":generation.AIAdapter()}
    for module in (*MODULES, demo_lab):
        app.include_router(module.router)
    engine_web.register(app, templates)
    mutation_web.register(app, templates)

    @app.get("/workbench/demo-lab", include_in_schema=False)
    def demo_lab_page(request: Request):
        return templates.TemplateResponse(request=request, name="demo_lab.html")

    @app.middleware("http")
    async def local_writes(request: Request, call_next):
        from fastapi.responses import JSONResponse
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            origin = request.headers.get("origin")
            if request.headers.get("sec-fetch-site") == "cross-site" or (
                origin is not None and origin != str(request.base_url).rstrip("/")
            ):
                return JSONResponse({"detail": "仅允许本地同源操作"}, status_code=403)
        return await call_next(request)

    @app.get("/workbench/{page}", include_in_schema=False)
    def workbench(page: str, request: Request):
        if page not in PAGES:
            raise HTTPException(404)
        return templates.TemplateResponse(request=request, name="workbench.html",
                                          context={"page": page, "mode": mode})
