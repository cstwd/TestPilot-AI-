"""Read-only TestPilot MCP tools for project and run evidence."""
import json
import os
from pathlib import Path
import sqlite3
import sys
from contextlib import closing


PROTOCOL = "2025-11-25"
DB = Path(os.getenv("TESTPILOT_DATA_DIR", "data")) / "testpilot.sqlite3"
TOOLS = {
    "list_projects": {
        "description": "List up to 50 recent TestPilot project IDs and names.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    "get_run": {
        "description": "Read the status and test counts for one TestPilot execution.",
        "inputSchema": {
            "type": "object", "properties": {"run_id": {"type": "integer", "minimum": 1, "maximum": 9223372036854775807}},
            "required": ["run_id"], "additionalProperties": False,
        },
    },
}
for name, tool in TOOLS.items():
    tool.update(name=name, annotations={"readOnlyHint": True, "openWorldHint": False})


def query(name, arguments):
    if name not in TOOLS or not isinstance(arguments, dict):
        raise ValueError("Unknown tool or invalid arguments")
    expected = set(TOOLS[name]["inputSchema"].get("required", []))
    if set(arguments) != expected:
        raise ValueError("Arguments do not match inputSchema")
    with closing(sqlite3.connect(DB.resolve().as_uri() + "?mode=ro", uri=True, timeout=2)) as conn:
        conn.row_factory = sqlite3.Row
        if name == "list_projects":
            rows = conn.execute("SELECT id, name FROM projects ORDER BY id DESC LIMIT 50")
            return {"projects": [dict(row) for row in rows]}
        key = arguments["run_id"]
        if type(key) is not int or not 1 <= key <= 9223372036854775807:
            raise ValueError("run_id must be a positive SQLite integer")
        row = conn.execute(
            "SELECT id, status, result FROM runs WHERE id = ?", (key,)
        ).fetchone()
        if row is None:
            raise ValueError("Run not found")
        result = json.loads(row["result"])
        return {"id": row["id"], "status": row["status"],
                **{field: result.get(field) for field in ("passed", "failed", "errors", "skipped")}}


def dispatch(method, params):
    if method == "initialize":
        return {
            "protocolVersion": PROTOCOL, "capabilities": {"tools": {}},
            "serverInfo": {"name": "testpilot", "version": "1.0.0"},
        }
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": list(TOOLS.values())}
    if method == "tools/call":
        try:
            data = query(params.get("name"), params.get("arguments", {}))
            return {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}]}
        except (TypeError, ValueError, AttributeError) as error:
            message = str(error)
        except sqlite3.Error:
            message = "TestPilot database is unavailable or incompatible"
        return {"isError": True, "content": [{"type": "text", "text": message}]}
    raise LookupError(method)


def reply(line):
    try:
        request = json.loads(line)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"id": None, "error": {"code": -32700, "message": "Parse error"}}
    if not isinstance(request, dict) or request.get("jsonrpc") != "2.0" or not isinstance(request.get("method"), str):
        return {"id": None, "error": {"code": -32600, "message": "Invalid Request"}}
    if "id" not in request:
        return None
    request_id = request["id"]
    params = request.get("params", {})
    if not isinstance(params, dict):
        return {"id": request_id, "error": {"code": -32602, "message": "Invalid params"}}
    try:
        return {"id": request_id, "result": dispatch(request["method"], params)}
    except LookupError:
        return {"id": request_id, "error": {"code": -32601, "message": "Method not found"}}


def main():
    for line in sys.stdin.buffer:
        result = reply(line)
        if result is not None:
            print(json.dumps({"jsonrpc": "2.0", **result}), flush=True)


if __name__ == "__main__":
    main()
