"""Register the phase 02 business modules on the existing application."""
from fastapi import HTTPException, Request

from . import analysis, bugs, engine_history, engine_web, generation, mutation_store, mutation_web, projects, quality, runs
from .store import connect

MODULES = (projects, analysis, generation, runs, bugs, quality)
PAGES = {"projects", "analysis", "generation", "runs", "bugs", "reports"}


def initialize(path):
    with connect(path, write=True) as db:
        for module in (*MODULES, engine_history, mutation_store):
            for statement in getattr(module, "SCHEMA", ()):
                db.execute(statement)


def register(app, templates, path, mode):
    app.state.db_path = path
    app.state.generators = {"template": generation.TemplateAdapter(), "ai":generation.AIAdapter()}
    for module in MODULES:
        app.include_router(module.router)
    engine_web.register(app, templates)
    mutation_web.register(app, templates)

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
