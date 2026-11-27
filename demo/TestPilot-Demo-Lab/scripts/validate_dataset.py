
"""Validate frozen module contracts using Pytest inside TestPilot's WASI runner."""
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import sys


LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB.parents[1]))
from backend.runner import execute  # noqa: E402

ALLOWED_IMPORTS = {"bisect", "collections", "csv", "datetime", "decimal", "io", "json", "math"}
GUEST = LAB / "tests/verification/guest_checks.py"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_json(path):
    return json.loads((LAB / path).read_text(encoding="utf-8"))


def read_source(path, expected_sha):
    file = LAB / path
    source = file.read_text(encoding="utf-8")
    require(0 < len(source.encode()) <= 128 * 1024, f"size: {path}")
    require(hashlib.sha256(source.encode()).hexdigest() == expected_sha, f"sha256: {path}")
    tree = ast.parse(source, filename=path, feature_version=(3, 10))
    compile(tree, path, "exec", dont_inherit=True)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(value.name for value in node.names)
        elif isinstance(node, ast.ImportFrom):
            require(not node.level, f"relative import: {path}")
            imports.add(node.module)
    require(imports <= ALLOWED_IMPORTS, f"unexpected import: {path} {imports - ALLOWED_IMPORTS}")
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    require(len(functions) >= 2, f"fewer than two public functions: {path}")
    require(all(ast.get_docstring(node) and node.returns is not None for node in functions),
            f"undocumented function: {path}")
    return source, [node.name for node in functions]


def patch(source, repair):
    old, new = repair["find"], repair["replace"]
    require(source.count(old) == 1 and old != new, f"ambiguous change: {old!r}")
    return source.replace(old, new, 1)


def prepare():
    truth = load_json("reference/ground_truth.json")
    public = load_json("scenarios/modules.json")
    index = load_json("reference/answer_index.json")
    modules = truth["modules"]
    require(truth["schema_version"] == 1, "unsupported ground truth")
    require(Counter(row["tier"] for row in modules) == {"good": 25, "buggy": 50, "challenge": 25},
            "tier counts differ from the release contract")
    require({row["domain"] for row in modules} == {"math", "people", "commerce", "data", "algorithms", "time"},
            "domain set")
    for domain in {row["domain"] for row in modules}:
        require({row["tier"] for row in modules if row["domain"] == domain} == {"good", "buggy", "challenge"},
                f"tier coverage: {domain}")
    require(len({row["name"] for row in modules}) == len({row["sha256"] for row in modules}) == len(modules),
            "duplicate name or content")
    require(public == [{key: row[key] for key in ("name", "tier", "domain", "path", "targets", "sha256", "cases")}
                       for row in modules], "catalog differs from ground truth")
    expected_index = {defect["id"]: {"module": row["name"], "case": defect["case_id"],
                                    "category": defect["category"], "corrected_path": row["corrected_path"]}
                      for row in modules for defect in row["defects"]}
    require(index == expected_index, "defect index mismatch")
    require({path.relative_to(LAB).as_posix() for path in (LAB / "source").rglob("*.py")}
            == {row["path"] for row in modules}, "source file inventory mismatch")
    require({path.relative_to(LAB).as_posix() for path in (LAB / "reference/corrected").glob("*.py")}
            == {row["corrected_path"] for row in modules if row["defects"]}, "corrected file inventory mismatch")
    return modules


def batch_data(modules):
    sources, cases, witnesses = {}, [], []
    for row in modules:
        name = row["name"]
        require(re.fullmatch(r"[a-z][a-z0-9_]+", name), f"name: {name}")
        require(row["path"] == f"source/{row['tier']}/{name}.py", f"path: {name}")
        expected_ref = f"reference/corrected/{name}.py" if row["defects"] else row["path"]
        require(row["corrected_path"] == expected_ref, f"reference path: {name}")
        source, symbols = read_source(row["path"], row["sha256"])
        corrected, corrected_symbols = read_source(row["corrected_path"], row["corrected_sha256"])
        require(symbols == corrected_symbols == row["targets"], f"public interface: {name}")
        sources[name] = (name, source)
        sources[name + "_ref"] = (name, corrected)
        defects = {item["id"]: item for item in row["defects"]}
        require(len(defects) == (0 if row["tier"] == "good" else 2), f"defect count: {name}")
        recreated = corrected
        for defect in defects.values():
            recreated = patch(recreated, defect["repair"])
        require(recreated == source, f"changes do not reproduce {name}")
        require(row["cases"] == len({case["id"] for case in row["tests"]})
                == len({ast.dump(ast.parse(case["call"], mode="eval")) for case in row["tests"]}),
                f"case count or duplicate input: {name}")
        require(set(defects) == {case["defect"] for case in row["tests"] if "defect" in case},
                f"missing defect witness: {name}")
        for case in row["tests"]:
            cases.append({**case, "module": name, "phase": "source"})
            if not defects:
                continue
            cases.append({**case, "id": case["id"] + "_ref", "module": name + "_ref", "phase": "reference"})
            if "defect" in case:
                defect = defects[case["defect"]]
                require(defect["case_id"] == case["id"] and defect["trigger"] == case["call"]
                        and defect["expected"] == case["expected"] and defect["actual"] != case["expected"],
                        f"defect evidence: {case['id']}")
                repaired = corrected
                for other_id, other in defects.items():
                    if other_id != defect["id"]:
                        repaired = patch(repaired, other["repair"])
                fixed_one = case["id"] + "_repair"
                sources[fixed_one] = (name, repaired)
                witnesses.append({**case, "id": case["id"] + "_witness", "module": name,
                                  "fixed_one": fixed_one, "phase": "witness", "actual": defect["actual"]})
    return sources, cases, witnesses


def run_batch(modules, guest):
    sources, cases, witnesses = batch_data(modules)
    payload = f"SOURCES = {sources!r}\nCASES = {cases!r}\nWITNESSES = {witnesses!r}\n"
    result = execute(payload, guest, detailed=True, timeout_s=45)
    observed = {row["nodeid"]: row["outcome"] for row in result["cases"]}
    rows = []
    for group, checks in (("contract", cases), ("defect_witness", witnesses)):
        for row in checks:
            node = f"test_generated.py::test_{group}[{row['id']}]"
            known_failure = row["phase"] == "source" and "defect" in row
            expected = "failed" if known_failure else "passed"
            actual = observed.get(node, "unrun")
            rows.append({"nodeid": node, "phase": row["phase"], "expected": expected,
                         "actual": actual, "matches": expected == actual, "case_id": row["id"]})
    return {
        "modules": [row["name"] for row in modules],
        "status": result["status"],
        "exit_code": result["exit_code"],
        "complete": bool(result["result_complete"] and observed.keys() == {row["nodeid"] for row in rows}),
        "duration_ms": result["duration_ms"],
        "failures": result["failures"],
        "diagnostic": result["diagnostic"],
        "log": result["log"],
        "cases": rows,
    }


def main():
    modules = prepare()
    guest = GUEST.read_text(encoding="utf-8")
    batches = []
    for start in range(0, len(modules), 10):
        batch = run_batch(modules[start:start + 10], guest)
        batches.append(batch)
        mismatches = [row["nodeid"] for row in batch["cases"] if not row["matches"]]
        print(start, batch["status"], len(batch["cases"]), mismatches[:10], batch["diagnostic"], flush=True)
    outcomes = {phase: dict(Counter(case["actual"] for batch in batches for case in batch["cases"]
                                     if case["phase"] == phase))
                for phase in ("source", "reference", "witness")}
    types = Counter(case["category"] for row in modules for case in row["tests"])
    ok = all(batch["complete"] and all(row["matches"] for row in batch["cases"]) for batch in batches)
    report = {"timestamp": datetime.now(timezone.utc).isoformat(), "host": platform.platform(),
              "python": platform.python_version(), "executor": "backend.runner.execute / WASI Pytest",
              "modules": dict(Counter(row["tier"] for row in modules)),
              "source_sha256": {row["name"]: row["sha256"] for row in modules},
              "reference_sha256": {row["name"]: row["corrected_sha256"] for row in modules if row["defects"]},
              "defects": sum(len(row["defects"]) for row in modules), "categories": dict(types),
              "outcomes": outcomes, "match": ok, "batches": batches}
    (LAB / "reports/dataset_validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
