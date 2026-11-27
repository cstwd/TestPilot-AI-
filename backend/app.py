"""Single-origin FastAPI application and Phase 01 routes."""

import logging
import os
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from threading import Lock

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.trustedhost import TrustedHostMiddleware

from backend import database
from backend.self_test import run_self_test

ROOT = Path(__file__).resolve().parent.parent
LOG = logging.getLogger("testpilot.self_test")


def create_app(mode: str = "demo", db_path: Path | None = None) -> FastAPI:
    data_dir = Path(os.environ.get("TESTPILOT_DATA_DIR", ROOT / "data"))
    path = (db_path or data_dir / "testpilot.sqlite3").resolve()
    templates = Jinja2Templates(directory=ROOT / "frontend" / "templates")
    running_test = Lock()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            database.initialize(path)
        except (OSError, sqlite3.Error) as exc:
            raise RuntimeError(f"无法初始化 SQLite 数据库 {path}。请检查目录和写入权限。") from exc
        yield

    app = FastAPI(title="TestPilot AI", lifespan=lifespan,
                  docs_url="/docs" if mode == "dev" else None, redoc_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])
    app.mount("/static", StaticFiles(directory=ROOT / "frontend" / "static"), name="static")

    @app.get("/", include_in_schema=False)
    def dashboard(request: Request):
        return templates.TemplateResponse(
            request=request, name="dashboard.html", context={"mode": mode}
        )

    @app.get("/api/health")
    def health():
        ready = database.is_ready(path)
        return JSONResponse(
            {"status": "ok" if ready else "degraded", "database": "ok" if ready else "error",
             "mode": mode}, status_code=200 if ready else 503,
        )

    @app.post("/api/self-test")
    def self_test(request: Request):
        origin = request.headers.get("origin")
        if request.headers.get("sec-fetch-site") == "cross-site" or (
            origin is not None and origin != str(request.base_url).rstrip("/")
        ):
            return JSONResponse({"status": "rejected", "detail": "仅接受同源请求。"}, status_code=403)
        if not running_test.acquire(blocking=False):
            return JSONResponse({"status": "busy", "detail": "已有自检正在运行。"}, status_code=409)
        try:
            success, detail = run_self_test()
            if not success:
                LOG.error("固定样例自检失败 %s", detail)
            return JSONResponse({"status": "passed" if success else "failed", "detail": detail},
                                status_code=200 if success else 503)
        except OSError:
            LOG.exception("无法创建临时目录或启动 Pytest")
            return JSONResponse({"status": "failed", "detail": "执行器无法启动，请检查运行日志。"},
                                status_code=503)
        finally:
            running_test.release()

    return app
