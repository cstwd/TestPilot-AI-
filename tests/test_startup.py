"""Real main.py startup, port ownership and shutdown checks on loopback."""

import json
import os
import signal
import socket
import sqlite3
import subprocess
import sys
import threading
import time
from contextlib import closing, contextmanager
from pathlib import Path
from urllib.error import URLError
from urllib.request import ProxyHandler, Request, build_opener

import pytest
from main import open_when_ready

ROOT = Path(__file__).resolve().parents[1]
CLIENT = build_opener(ProxyHandler({}))


def vacant_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def launch_args(port):
    return [sys.executable, str(ROOT / "main.py"), "--port", str(port), "--no-browser"]


def launch_env(data_dir):
    return {**os.environ, "TESTPILOT_DATA_DIR": str(data_dir), "PYTHONIOENCODING": "utf-8"}


@contextmanager
def running_server(port, data_dir, log, mode):
    url = f"http://127.0.0.1:{port}"
    with log.open("w", encoding="utf-8") as stream:
        process = subprocess.Popen(
            [*launch_args(port), "--mode", mode], cwd=ROOT, env=launch_env(data_dir),
            stdout=stream, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        )
        try:
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                assert process.poll() is None, log.read_text(encoding="utf-8")
                try:
                    with CLIENT.open(url + "/api/health", timeout=1) as response:
                        health = json.load(response)
                    break
                except URLError:
                    time.sleep(0.1)
            else:
                pytest.fail("health readiness timeout")
            print("GET /api/health", health, flush=True)
            assert health == {"status": "ok", "database": "ok", "mode": mode}
            yield url
        finally:
            try:
                if process.poll() is None:
                    event = signal.CTRL_BREAK_EVENT if os.name == "nt" else signal.SIGINT
                    process.send_signal(event)
                    process.wait(timeout=20)
                    print("Graceful stop exit", process.returncode, flush=True)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=5)
                print(log.read_text(encoding="utf-8"), flush=True)
    assert "Application shutdown complete" in log.read_text(encoding="utf-8")
    assert process.returncode == 0


def test_entry_conflict_database_shutdown_restart(tmp_path):
    port = vacant_port()
    data_dir = tmp_path / "sqlite"
    db = data_dir / "testpilot.sqlite3"
    for mode in ("demo", "dev"):
        with running_server(port, data_dir, tmp_path / f"{mode}.log", mode) as url:
            with CLIENT.open(url + "/", timeout=5) as response:
                assert response.status == 200 and "TestPilot AI" in response.read().decode("utf-8")
            with closing(sqlite3.connect(db)) as connection, connection:
                assert connection.execute("SELECT value FROM app_metadata WHERE key='schema_version'").fetchone() == ("1",)
                if mode == "demo":
                    connection.execute("INSERT INTO app_metadata VALUES ('acceptance_probe', 'retained')")
                else:
                    assert connection.execute("SELECT value FROM app_metadata WHERE key='acceptance_probe'").fetchone() == ("retained",)
                    print("SQLite restart probe retained", flush=True)
            if mode == "demo":
                conflict = subprocess.run(launch_args(port), cwd=ROOT, env=launch_env(data_dir),
                                          capture_output=True, encoding="utf-8", timeout=15)
                print("Second launch exit", conflict.returncode, conflict.stderr.strip(), flush=True)
                assert conflict.returncode == 1 and str(port) in conflict.stderr and "占用" in conflict.stderr
                request = Request(url + "/api/self-test", method="POST")
                with CLIENT.open(request, timeout=20) as response:
                    result = json.load(response)
                print("POST /api/self-test", result, flush=True)
                assert result["status"] == "passed" and "1 passed" in result["detail"]


def test_startup_failure(tmp_path):
    bad_dir = tmp_path / "regular_file"
    bad_dir.write_text("fixture", encoding="utf-8")
    failure = subprocess.run(launch_args(vacant_port()), cwd=ROOT, env=launch_env(bad_dir),
                             capture_output=True, encoding="utf-8", timeout=15)
    print("Unwritable database path exit", failure.returncode, failure.stderr, flush=True)
    assert failure.returncode != 0 and "无法初始化 SQLite 数据库" in failure.stderr


def test_incompatible_database_preserved(tmp_path):
    db = tmp_path / "testpilot.sqlite3"
    with closing(sqlite3.connect(db)) as connection, connection:
        connection.execute("CREATE TABLE app_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        connection.execute("INSERT INTO app_metadata VALUES ('schema_version', '2')")
    before = db.read_bytes()
    failure = subprocess.run(launch_args(vacant_port()), cwd=ROOT, env=launch_env(tmp_path),
                             capture_output=True, encoding="utf-8", timeout=15)
    diagnostic = next(line for line in failure.stderr.splitlines() if line.startswith("RuntimeError:"))
    print("Incompatible database exit", failure.returncode, diagnostic)
    assert failure.returncode != 0 and "schema_version=2" in diagnostic
    assert db.read_bytes() == before


def test_browser_wait_timeout(caplog, monkeypatch):
    def unexpected_open(*args, **kwargs):
        pytest.fail("browser opened while health check was failing")

    monkeypatch.setattr("webbrowser.open", unexpected_open)
    url = f"http://127.0.0.1:{vacant_port()}"
    open_when_ready(url, threading.Event(), timeout=0.25)
    print(caplog.text)
    assert "健康检查等待超时" in caplog.text and url in caplog.text
