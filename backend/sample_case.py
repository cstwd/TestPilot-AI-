"""Bundled, trusted pytest input for checking the executor installation."""

import sqlite3
from contextlib import closing


def test_sqlite_round_trip(tmp_path):
    with closing(sqlite3.connect(tmp_path / "sample.sqlite3")) as connection:
        connection.execute("CREATE TABLE sample (label TEXT NOT NULL)")
        connection.execute("INSERT INTO sample VALUES (?)", ("TestPilot AI",))
        assert connection.execute("SELECT label FROM sample").fetchone() == ("TestPilot AI",)
