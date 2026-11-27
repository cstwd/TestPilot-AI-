"""Project and immutable source revision API. Imported text stays in SQLite."""
import hashlib
import re
import sqlite3
from ntpath import isreserved

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .store import connect, many, one

router = APIRouter(prefix="/api")
SCHEMA = (
    "CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL)",
    """CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL REFERENCES projects(id),
        filename TEXT NOT NULL COLLATE NOCASE, revision INTEGER NOT NULL,
        source TEXT NOT NULL, sha256 TEXT NOT NULL, UNIQUE(project_id,filename,revision))""",
)
FIELDS = "id,project_id,filename,revision,sha256"


class ProjectInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class FileInput(BaseModel):
    filename: str = Field(min_length=1, max_length=100)
    source: str = Field(max_length=131072)


@router.get("/projects")
def list_projects(request: Request):
    with connect(request.app.state.db_path) as db:
        return many(db, "SELECT * FROM projects ORDER BY id DESC")


@router.post("/projects", status_code=201)
def create_project(item: ProjectInput, request: Request):
    name = item.name.strip()
    if not name or any(ord(c) < 32 for c in name):
        raise HTTPException(422, "请输入有效的项目名称")
    with connect(request.app.state.db_path, write=True) as db:
        try:
            key = db.execute("INSERT INTO projects(name) VALUES (?)", (name,)).lastrowid
        except sqlite3.IntegrityError as exc:
            raise HTTPException(409, "项目名称已存在") from exc
        return {"id": key, "name": name}


@router.get("/projects/{project_id}/files")
def list_files(project_id: int, request: Request):
    with connect(request.app.state.db_path) as db:
        one(db, "SELECT id FROM projects WHERE id=?", (project_id,))
        return many(db, f"SELECT {FIELDS} FROM files WHERE project_id=? ORDER BY id DESC", (project_id,))


def source_digest(filename, source):
    if not re.fullmatch(r"[\w-]+\.py", filename) or isreserved(filename):
        raise HTTPException(422, "仅支持单个 .py 文件名，不能含路径或保留设备名")
    try:
        data = source.encode("utf-8")
    except UnicodeError as exc:
        raise HTTPException(422, "源码须为有效的 UTF-8 文本") from exc
    if len(data) > 131072 or b"\0" in data:
        raise HTTPException(422, "源码须为 128 KiB 以内、不含 NUL 的文本")
    return hashlib.sha256(data).hexdigest()


def save_revision(db, project_id, filename, source, digest, *, reuse_latest=True):
    latest = db.execute("SELECT * FROM files WHERE project_id=? AND filename=? ORDER BY revision DESC LIMIT 1",
                        (project_id, filename)).fetchone()
    if reuse_latest and latest and latest["sha256"] == digest:
        return dict(latest)
    revision = latest["revision"] + 1 if latest else 1
    key = db.execute("INSERT INTO files(project_id,filename,revision,source,sha256) VALUES (?,?,?,?,?)",
                     (project_id, filename, revision, source, digest)).lastrowid
    return one(db, "SELECT * FROM files WHERE id=?", (key,))


@router.post("/projects/{project_id}/files")
def import_file(project_id: int, item: FileInput, request: Request):
    digest = source_digest(item.filename, item.source)
    with connect(request.app.state.db_path, write=True) as db:
        one(db, "SELECT id FROM projects WHERE id=?", (project_id,))
        return save_revision(db, project_id, item.filename, item.source, digest)


@router.get("/files/{file_id}")
def read_file(file_id: int, request: Request):
    with connect(request.app.state.db_path) as db:
        return one(db, "SELECT * FROM files WHERE id=?", (file_id,))
