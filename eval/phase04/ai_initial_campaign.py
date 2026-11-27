"""Run the F09 and F13 local-model acceptance through the real main.py HTTP endpoints."""
import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import ProxyHandler, Request, build_opener
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[2]


@contextmanager
def service(folder, model):
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    env = dict(os.environ, TESTPILOT_DATA_DIR=str(folder.resolve()), TESTPILOT_MODEL_PROVIDER="ollama",
               TESTPILOT_MODEL_BASE_URL="http://127.0.0.1:11434", TESTPILOT_MODEL_NAME=model,
               TESTPILOT_MODEL_RETRIES="1", TESTPILOT_MODEL_TIMEOUT="120",
               TESTPILOT_MODEL_PROMPT_PROFILE="local-compact", TESTPILOT_MUTATION_MODEL=model,
               TESTPILOT_MUTATION_BASE_URL="http://127.0.0.1:11434", PYTHONUTF8="1")
    opener = build_opener(ProxyHandler({}))

    def call(route, body=None):
        req = Request(f"http://127.0.0.1:{port}" + route, data=json.dumps(body).encode() if body is not None else None,
                      headers={"Content-Type": "application/json"})
        with opener.open(req, timeout=1800) as response:
            return json.load(response)

    with (folder / "service.log").open("a", encoding="utf8") as log:
        proc = subprocess.Popen([sys.executable, "main.py", "--no-browser", "--port", str(port)],
                                cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 30
            while proc.poll() is None and time.monotonic() < deadline:
                try:
                    if call("/api/health")["status"] == "ok":
                        break
                except URLError:
                    time.sleep(0.15)
            else:
                raise RuntimeError(f"Service startup failed, inspect {log.name}")
            yield call
        finally:
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=10)


def save(folder, prefix, label, data):
    with (folder / (prefix + "-" + label + ".json")).open("x", encoding="utf8") as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="qwen2.5-coder:0.5b")
    parser.add_argument("--data-dir", type=Path, default=ROOT / ".runtime" / str(uuid4()))
    parser.add_argument("--export-dir", type=Path)
    parser.add_argument("--prefix", choices=["ai-initial-final", "ai-hardened"], default="ai-initial-final")
    parser.add_argument("--initial-only", action="store_true")
    parser.add_argument("--existing-task")
    args = parser.parse_args()
    folder = args.export_dir or args.data_dir
    for path in (folder, args.data_dir):
        path.mkdir(exist_ok=True, parents=True)
    with service(args.data_dir, args.model) as call:
        if args.existing_task:
            task = call("/api/engine/tasks/" + args.existing_task)
        else:
            project = call("/api/projects", {"name": f"F13 AI validation {uuid4()}"})
            file = call(f"/api/projects/{project['id']}/files", {
                "filename": "bonus.py", "source": Path(__file__).with_name("bonus.py").read_text(encoding="utf8")})
            task = call(f"/api/engine/files/{file['id']}/tasks", {
                "target": "bonus", "max_repairs": 0, "generation_mode": "configured"})
            save(folder, args.prefix, "task", task)
        generated = next(r["payload"] for r in task["records"] if r["kind"] == "GeneratedTest")
        execution = next(r["payload"] for r in task["records"] if r["kind"] == "TestExecution")
        print("F09", task["id"], generated["mode"], generated["model"], execution["status"], execution["passed"],
              flush=True)
        if (generated["mode"] != "ai" or generated["model"] != args.model or execution["status"] != "passed"
                or not execution["result_complete"] or execution["passed"] < 1):
            raise SystemExit(f"F09 did not produce a green AI suite. Evidence in {folder}")
        if not args.initial_only:
            session = call(f"/api/engine/tasks/{task['id']}/mutations", {"feedback": True, "timeout_s": 15})
            url = "/api/mutations/" + session["id"]
            print("F13", session["id"], flush=True)
            call(url + "/run", {})
            report = call(url + "/report")
            save(folder, args.prefix, "campaign", report)
            print(report["status"], report["before"], report["after"], flush=True)


if __name__ == "__main__":
    main()
