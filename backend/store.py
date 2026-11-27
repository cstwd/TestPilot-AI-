"""Short SQLite transactions shared by the workbench modules."""
from contextlib import closing, contextmanager
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
