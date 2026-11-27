"""Run the Windows tool comparison only on the fixed trusted fixture below.

Run with .runtime/phase04-tools/Scripts/python.exe. The --wasi switch delegates
one unmodified and two mutated copies to the project's actual isolated runner.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextlib import chdir
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
from time import monotonic

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "phase04" / "tools"
SOURCE = """def charge(n, enabled):
    try:
        if n > 1 and enabled:
            return n + 2
        return 0
    except TypeError:
        return -1
"""
SUITE = """from subject import charge

def test_enabled():
    assert charge(3, True) == 5

def test_type_fallback():
    assert charge(None, True) == -1
"""


def record(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf8")


def command(args, folder):
    start = monotonic()
    result = subprocess.run([str(a) for a in args], cwd=folder,
                            env={**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"},
                            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            encoding="utf8", errors="replace", timeout=240)
    return {"command": [Path(args[0]).name, *args[1:]], "returncode": result.returncode,
            "wall_seconds": round(monotonic() - start, 3), "stdout": result.stdout, "stderr": result.stderr}


def fixture(folder):
    folder.mkdir()
    (folder / "subject.py").write_text(SOURCE, encoding="utf8")
    (folder / "test_subject.py").write_text(SUITE, encoding="utf8")
    (folder / "pyproject.toml").write_text('[tool.mutmut]\nsource_paths = ["subject.py"]\n', encoding="utf8")
    invocation = f'"{Path(sys.executable).as_posix()}" -B -m pytest -q -p no:cacheprovider test_subject.py'
    (folder / "cosmic.toml").write_text(
        '[cosmic-ray]\nmodule-path = "subject.py"\ntimeout = 15.0\nexcluded-modules = []\n'
        + "test-command = " + json.dumps(invocation) + '\n[cosmic-ray.distributor]\nname = "local"\n', encoding="utf8")


def render_summary(rows):
    return dict(Counter(result["test_outcome"] for _, result in rows))


def main(wasi):
    from cosmic_ray.ast import ast_nodes, get_ast
    from cosmic_ray.mutating import mutate_code
    from cosmic_ray.plugins import get_operator, operator_names
    from cosmic_ray.testing import run_tests
    from cosmic_ray.work_db import use_db, WorkDB
    from mutmut.mutation.file_mutation import create_mutations

    scripts = Path(sys.executable).parent
    OUT.mkdir(parents=True, exist_ok=True)
    cosmic = scripts / "cosmic-ray.exe"
    mutmut = scripts / "mutmut.exe"
    data = {"utc": datetime.now(timezone.utc).isoformat(), "platform": platform.platform(),
            "python": platform.python_version(),
            "packages": {p: version(p) for p in ("mutmut", "cosmic-ray", "pytest")},
            "sha256": sha256(SOURCE.encode()).hexdigest(), "fixture": SOURCE, "tests": SUITE}
    with tempfile.TemporaryDirectory(dir=ROOT / ".runtime", prefix="mutation-bench-") as tmp:
        root = Path(tmp)
        project = root / "serial"
        fixture(project)
        data["baseline"] = command([sys.executable, "-m", "pytest", "-q"], project)
        data["mutmut_cli"] = [command([mutmut, "run", "--max-children", str(n)], project) for n in (1, 2)]
        data["mutmut_cli"].append(command([mutmut, "results"], project))
        started = monotonic()
        with chdir(project):
            module, muts, _, _ = create_mutations("subject.py", SOURCE)
        changes = [(module.code_for_node(m.original_node), module.code_for_node(m.mutated_node)) for m in muts]
        mutmut_source = next(module.deep_replace(m.original_node, m.mutated_node).code for m in muts
                             if module.code_for_node(m.mutated_node) == "n - 2")
        data["mutmut_static"] = {"seconds": round(monotonic() - started, 4), "count": len(muts), "changes": changes,
                                 "arithmetic_copy": mutmut_source}
        nodes = list(ast_nodes(get_ast(SOURCE)))
        started = monotonic()
        opportunities = {}
        for name in operator_names():
            cls = get_operator(name)
            if cls.arguments():  # Same default parameterization as cosmic-ray init.
                continue
            op = cls()
            points = [p for node in nodes for p in op.mutation_positions(node)]
            if points:
                opportunities[name] = points
        cosmic_source = mutate_code(SOURCE, get_operator("core/ReplaceBinaryOperator_Add_Sub")(), 0)
        data["cosmic_static"] = {"seconds": round(monotonic() - started, 4), "registered": len(operator_names()),
                                 "opportunities": opportunities, "arithmetic_copy": cosmic_source}
        for phase, args in [("init", ["init", "cosmic.toml", "session.sqlite"]),
                            ("baseline", ["baseline", "cosmic.toml"]),
                            ("exec", ["exec", "cosmic.toml", "session.sqlite"]),
                            ("dump", ["dump", "session.sqlite"])]:
            result = command([cosmic, *args], project)
            if result["returncode"] != 0:
                record("native-failure.json", result)
                raise RuntimeError(result)
            if phase == "dump":
                rows = [json.loads(line) for line in result["stdout"].splitlines()]
                (OUT / "cosmic-dump.ndjson").write_text(result.pop("stdout"), encoding="utf8")
                result["outcomes"] = render_summary(rows)
            data["cosmic_" + phase] = result
        assert (project / "subject.py").read_text(encoding="utf8") == SOURCE

        # All native jobs, split across two separate local sessions, with no listening HTTP workers.
        with use_db(project / "session.sqlite", WorkDB.Mode.open) as db:
            jobs = db.work_items
        workers = [root / f"worker{i}" for i in range(2)]
        for i, worker in enumerate(workers):
            fixture(worker)
            with use_db(worker / "session.sqlite") as db:
                db.add_work_items(jobs[i::2])
        started = monotonic()
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(lambda folder: command([cosmic, "exec", "cosmic.toml", "session.sqlite"], folder), workers))
        elapsed = round(monotonic() - started, 3)
        partitions = []
        for worker in workers:
            dump = command([cosmic, "dump", "session.sqlite"], worker)
            assert dump["returncode"] == 0, dump
            partitions.extend(json.loads(line) for line in dump["stdout"].splitlines())
            assert (worker / "subject.py").read_text(encoding="utf8") == SOURCE
        expected = {job["job_id"]: result["test_outcome"] for job, result in rows}
        assert expected == {job["job_id"]: result["test_outcome"] for job, result in partitions}
        data["parallel"] = {"workers": 2, "total_seconds": elapsed, "processes": outcomes,
                            "unique_jobs": len(expected), "outcomes": render_summary(partitions)}
        # Demonstrate why native return-code labels cannot serve as F13 killing evidence.
        python = '"' + Path(sys.executable).as_posix() + '"'
        with chdir(project):
            timeout, log = run_tests(python + ' -c "import time; time.sleep(3)"', .5)
            usage, usage_log = run_tests(python + ' -m pytest -q missing-test.py', 15)
        data["native_classification_probe"] = {"timeout": [timeout.value, log], "missing_pytest_path": [usage.value, usage_log]}
        record("windows-benchmark.json", data)
        if wasi:
            probe = "import json,sys; from backend.runner import execute; " \
                    "p=json.load(sys.stdin); r=execute(p['source'],p['tests'],detailed=True); print(json.dumps(r))"
            executions = {}
            for name, source in [("original", SOURCE), ("cosmic", cosmic_source), ("mutmut-static", mutmut_source)]:
                result = subprocess.run([ROOT / ".venv/Scripts/python.exe", "-c", probe], cwd=ROOT,
                                        input=json.dumps({"source": source, "tests": SUITE}), encoding="utf8",
                                        env={**os.environ, "PYTHONUTF8": "1"}, capture_output=True, timeout=90, check=True)
                executions[name] = json.loads(result.stdout)
                assert executions[name]["status"] == ("passed" if name == "original" else "failed")
            record("wasi-bridge.json", executions)
    print(json.dumps({"mutmut_cli": data["mutmut_cli"][0]["returncode"], "mutmut_static": len(muts),
                      "cosmic_jobs": len(rows), "serial_seconds": data["cosmic_exec"]["wall_seconds"],
                      "parallel_seconds": elapsed, "outcomes": data["cosmic_dump"]["outcomes"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wasi", action="store_true")
    main(parser.parse_args().wasi)

