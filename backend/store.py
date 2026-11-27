"""Short SQLite transactions shared by the workbench modules."""
from contextlib import closing, contextmanager
import os
from pathlib import Path
import sqlite3

from fastapi import HTTPException


@contextmanager
def connect(path, *, write=False):
    with closing(sqlite3.connect(path, timeout=8)) as db, db:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        if write:
            db.execute("BEGIN IMMEDIATE")
        yield db


def one(db, query, params=()):
    row = db.execute(query, params).fetchone()
    if row is None:
        raise HTTPException(404, "对应记录不存在")
    return dict(row)


def many(db, query, params=()):
    return [dict(row) for row in db.execute(query, params)]


@contextmanager
def exclusive_file(path: Path, busy_message: str):
    """Hold an OS advisory lock on a local sidecar until the handle closes."""
    with path.open("a+b") as handle:
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise HTTPException(409, busy_message) from exc
        yield
