import json
import os
from pathlib import Path
import subprocess
import sys

from backend import runs


ROOT = Path(__file__).resolve().parents[1]


def test_mcp_reads_real_testpilot_run(sample_workspace):
    request, project, files, suite = sample_workspace
    path = request.app.state.db_path
    run = runs.run_suite(path, suite["id"], files[1]["id"])
    path = path.rename(path.with_name("testpilot.sqlite3"))
    messages = [
        ("initialize", {"protocolVersion": "2025-11-25", "capabilities": {},
                        "clientInfo": {"name": "acceptance", "version": "1.0"}}),
        ("notifications/initialized", {}),
        ("tools/list", {}),
        ("tools/call", {"name": "list_projects"}),
        ("tools/call", {"name": "get_run", "arguments": {"run_id": run["id"]}}),
        ("tools/call", {"name": "get_run", "arguments": {"run_id": "invalid"}}),
    ]
    requests = []
    for index, (method, params) in enumerate(messages):
        request = {"jsonrpc": "2.0", "method": method, "params": params}
        if not method.startswith("notifications/"):
            request["id"] = index
        requests.append(json.dumps(request))
    config = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]["testpilot"]
    before = path.read_bytes()
    process = subprocess.run(
        [sys.executable, *config["args"]], cwd=ROOT, input="\n".join(requests) + "\n",
        text=True, encoding="utf-8", capture_output=True, timeout=15, check=True,
        env={**os.environ, "TESTPILOT_DATA_DIR": str(path.parent)},
    )
    assert not process.stderr
    replies = {row["id"]: row["result"] for row in map(json.loads, process.stdout.splitlines())}
    assert set(replies) == {0, 2, 3, 4, 5}
    assert replies[0]["protocolVersion"] == "2025-11-25"
    assert {tool["name"] for tool in replies[2]["tools"]} == {"get_run", "list_projects"}
    assert json.loads(replies[3]["content"][0]["text"]) == {"projects": [project]}
    actual = json.loads(replies[4]["content"][0]["text"])
    assert actual == {field: run[field] for field in ("id", "status", "passed", "failed", "errors", "skipped")}
    assert actual["status"] == "passed" and actual["passed"] > 0
    assert replies[5]["isError"] is True
    assert path.read_bytes() == before
    print(process.stdout, end="")


def test_pre_commit_rejects_and_accepts(tmp_path):
    def git(*args, check=True):
        return subprocess.run(
            ["git", "-c", "user.name=TestPilot fixture", "-c", "user.email=fixture@example.invalid",
             "-c", "commit.gpgsign=false", "-c", f"core.hooksPath={(ROOT / 'hooks').as_posix()}", *args],
            cwd=tmp_path, text=True, encoding="utf-8", errors="replace",
            capture_output=True, timeout=15, check=check,
        )

    git("init", "-q")
    fixture = tmp_path / "fixture.txt"
    fixture.write_text("example " + "\n", encoding="utf-8")
    git("add", "fixture.txt")
    rejected = git("commit", "-m", "bad staged whitespace", check=False)
    assert rejected.returncode != 0
    assert "TestPilot WP05" in rejected.stderr and "trailing whitespace" in rejected.stdout + rejected.stderr
    assert git("rev-parse", "--verify", "HEAD", check=False).returncode != 0
    fixture.write_text("example\n", encoding="utf-8")
    git("add", "fixture.txt")
    accepted = git("commit", "-m", "clean staged whitespace")
    assert "TestPilot WP05" in accepted.stderr
    print("Hook rejected commit:", rejected.stderr.strip(), rejected.stdout.strip())
    print("Hook accepted commit:", accepted.stderr.strip(), git("log", "-1", "--oneline").stdout.strip())
