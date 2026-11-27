"""Verify a PyCharm pydevd line breakpoint while running the actual project entry."""

import argparse
import ast
import http.client
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.parse import unquote
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
HOST = "127.0.0.1"


def verify(helper: Path, data_dir: Path) -> dict:
    source = ROOT / "backend" / "app.py"
    factory = next(node for node in ast.parse(source.read_text(encoding="utf-8")).body
                   if isinstance(node, ast.FunctionDef) and node.name == "create_app")
    line = factory.body[0].lineno
    with socket.socket() as candidate:
        candidate.bind((HOST, 0))
        app_port = candidate.getsockname()[1]

    with socket.socket() as listener:
        listener.bind((HOST, 0))
        listener.listen(1)
        listener.settimeout(20)
        command = [sys.executable, str(helper), "--client", HOST, "--port",
                   str(listener.getsockname()[1]), "--file", str(ROOT / "main.py"),
                   "--mode", "dev", "--no-browser", "--port", str(app_port)]
        process = subprocess.Popen(command, cwd=ROOT, env={
            **os.environ, "TESTPILOT_DATA_DIR": str(data_dir),
        })
        try:
            debugger, _ = listener.accept()
            with debugger, debugger.makefile("rb") as messages:
                debugger.settimeout(25)
                # Native JetBrains debugger protocol: version, set line breakpoint, run.
                debugger.sendall(("501\t1\t1.0\tWINDOWS\tID\n"
                                  f"111\t3\t1\tpython-line\t{source}\t{line}\tcreate_app\tNone\tNone\n"
                                  "101\t5\t\n").encode("utf-8"))
                while True:
                    message = messages.readline()
                    if not message:
                        raise RuntimeError("Debugger closed before reporting suspension")
                    command_id, _, payload = message.decode().rstrip("\n").split("\t", 2)
                    if command_id == "105":
                        thread = ElementTree.fromstring(unquote(payload)).find("thread")
                        frame = thread.find("frame")
                        break
                file = Path(unquote(frame.attrib["file"]))
                if (not os.path.samefile(file, source) or int(frame.attrib["line"]) != line
                        or thread.attrib["stop_reason"] != "111"):
                    raise RuntimeError(f"Unexpected stop: {frame.attrib!r} {thread.attrib!r}")
                debugger.sendall(f"106\t7\t{thread.attrib['id']}\n".encode())
                deadline = time.monotonic() + 10
                while True:
                    connection = http.client.HTTPConnection(HOST, app_port, timeout=3)
                    try:
                        connection.request("GET", "/api/health")
                        response = connection.getresponse()
                        health = json.load(response)
                        if response.status != 200 or health.get("database") != "ok":
                            raise RuntimeError(f"Health probe failed: {health!r}")
                        break
                    except ConnectionRefusedError:
                        if time.monotonic() >= deadline:
                            raise
                        time.sleep(.1)
                    finally:
                        connection.close()
                if not (data_dir / "testpilot.sqlite3").is_file():
                    raise RuntimeError("The debug session did not initialize the temporary database")
                return {"debugger": str(helper), "entry": "main.py", "pid": process.pid,
                        "app_port": app_port, "breakpoint": str(source.relative_to(ROOT)),
                        "function": unquote(frame.attrib["name"]), "line": line,
                        "stop_reason": thread.attrib["stop_reason"], "resumed_health": health,
                        "database_in_temp_dir": True}
        finally:
            process.terminate()
            process.wait(timeout=8)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pydevd", type=Path, help="PyCharm's helpers/pydev/pydevd.py")
    with tempfile.TemporaryDirectory(prefix="testpilot-debug-") as directory:
        result = verify(parser.parse_args().pydevd.resolve(strict=True), Path(directory))
    print(json.dumps(result, ensure_ascii=False, indent=2))
