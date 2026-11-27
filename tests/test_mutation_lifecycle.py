"""Exercise cancel, conflict and durable resume through real main.py HTTP entry points."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import json
import sqlite3
import time
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

import pytest

from test_dashboard import app_url
from test_startup import running_server, vacant_port


SOURCE = '''def increment(n: int) -> int:
    """Increment an integer by one.

    >>> increment(2)
    3
    """
    return n + 1
'''


def request(url, path, data=None):
    body = json.dumps(data).encode("utf8") if data is not None else None
    req = Request(url + path, data=body, headers={"Content-Type": "application/json"})
    with build_opener(ProxyHandler({})).open(req, timeout=150) as response:
        return json.load(response)


def campaign(url, source):
    project = request(url, "/api/projects", {"name": "Lifecycle"})
    file = request(url, f"/api/projects/{project['id']}/files", {"filename": "sample.py", "source": source})
    task = request(url, f"/api/engine/files/{file['id']}/tasks",
                   {"target": "increment", "max_repairs": 0, "generation_mode": "template"})
    assert task["status"] == "completed"
    create = f"/api/engine/tasks/{task['id']}/mutations"
    return file, create, request(url, create, {"feedback": False})


def test_cancel_then_resume_a_real_checkpoint(app_url, tmp_path):
    file, create, session = campaign(app_url, SOURCE)
    api = "/api/mutations/" + session["id"]
    assert len(session["manifest"]) == 2
    backup = tmp_path / "recovered"
    backup.mkdir()
    with ThreadPoolExecutor(max_workers=1) as thread:
        process = thread.submit(request, app_url, api + "/run", {})
        deadline = time.monotonic() + 100
        while time.monotonic() < deadline and not process.done():
            live = request(app_url, api)
            if live["before"] and live["before"]["unrun"] == 1:
                break
            time.sleep(.15)
        else:
            pytest.fail("did not observe first durable mutant result")
        # Capture an actual running SQLite checkpoint. The new service gets only its files.
        with closing(sqlite3.connect((tmp_path / "testpilot.sqlite3").as_uri() + "?mode=ro", uri=True)) as original:
            with closing(sqlite3.connect(backup / "testpilot.sqlite3")) as snapshot:
                original.backup(snapshot)
        with pytest.raises(HTTPError) as blocked:
            request(app_url, api + "/run", {})
        assert blocked.value.code == 409
        request(app_url, api + "/cancel", {})
        stopped = process.result(timeout=30)
    assert stopped["status"] == "cancelled"
    assert stopped["before"]["total"] == 2
    assert stopped["before"]["cancelled"] + stopped["before"]["unrun"] == 1
    original = request(app_url, api + "/report")
    assert request(app_url, api + "/run", {})["events"] == stopped["events"]
    unopened = request(app_url, create, {"feedback": False})
    unused = "/api/mutations/" + unopened["id"]
    assert request(app_url, unused + "/cancel", {})["status"] == "cancelled"
    assert request(app_url, unused + "/run", {})["events"] == []
    with running_server(vacant_port(), backup, backup / "service.log", "demo") as recovered:
        before = request(recovered, api + "/report")
        assert before["status"] == "running" and before["before"]["unrun"] == 1
        assert before["events"] == original["events"][:len(before["events"])]
        request(recovered, api + "/run", {})
        after = request(recovered, api + "/report")
        assert after["manifest"] == before["manifest"]
        assert after["events"][:-1] == before["events"]
        assert after["status"] == "completed" and after["before"]["unrun"] == 0
        assert after["before"]["killed"] == 2 and after["before"]["score_pct"] == 100
        assert len({r["mutant_id"] for r in after["events"] if r["kind"] == "observation"}) == 2
        assert request(recovered, f"/api/files/{file['id']}")["source"] == SOURCE
        assert request(recovered, api + "/run", {})["status"] == "completed"
        assert request(recovered, api + "/report") == after
    print("original stopped:", stopped["before"], "checkpoint events:", len(before["events"]),
          "recovered events:", len(after["events"]), "final:", after["before"])


def test_red_original_does_not_score(app_url):
    file, _, session = campaign(app_url, SOURCE.replace("return n + 1", "return n - 1"))
    api = "/api/mutations/" + session["id"]
    run = request(app_url, api + "/run", {})
    report = request(app_url, api + "/report")
    assert len(run["manifest"]) == 2 and run["status"] == "baseline_failed"
    assert run["before"] is None and run["after"] is None
    event, = report["events"]
    assert event["kind"] == "baseline" and event["status"] == "invalid"
    assert event["payload"]["exit_code"] == 1 and event["payload"]["source_sha256"] == file["sha256"]
    print("red baseline: two planned, zero observations, score unavailable; exit", event["payload"]["exit_code"])

