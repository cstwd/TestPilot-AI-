"""Local SQLite bootstrap and health checks."""

import sqlite3
from contextlib import closing
from pathlib import Path

SCHEMA_VERSION = "1"
VERSION_QUERY = "SELECT value FROM app_metadata WHERE key='schema_version'"


def initialize(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("BEGIN IMMEDIATE")
        tables = {row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT GLOB 'sqlite_*'"
        )}
        if tables:
            row = connection.execute(VERSION_QUERY).fetchone() if "app_metadata" in tables else None
            if row != (SCHEMA_VERSION,):
                found = row[0] if row else "缺失"
                raise RuntimeError(
                    f"SQLite 数据库版本不兼容：{path} 的 schema_version={found}，"
                    f"本版本要求 {SCHEMA_VERSION}。请使用匹配的数据库或新的数据目录。"
                )
            return
        connection.execute(
            "CREATE TABLE app_metadata "
            "(key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO app_metadata (key, value) VALUES ('schema_version', ?)", (SCHEMA_VERSION,)
        )


def is_ready(path: Path) -> bool:
    try:
        with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=2)) as connection:
            return connection.execute(VERSION_QUERY).fetchone() == (SCHEMA_VERSION,)
    except sqlite3.Error:
        return False
