
"""Adjudicate frozen AI suites offline after all product requests finish."""
import argparse
import ast
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

from metrics import summarize

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB.parents[1]))
from backend.mutation_results import case_map, test_assertion  # noqa: E402
from backend.runner import execute  # noqa: E402


def load(path, fallback=None):
    if not path.exists() and fallback is not None:
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def frozen_text(path, expected):
    value = (LAB / path).read_text(encoding="utf-8")
    if hashlib.sha256(value.encode()).hexdigest() != expected:
        raise ValueError(f"SHA-256 mismatch: {path}")
    return value


def corrupted_with_only(source, changes, omitted):
    for defect in changes:
        if defect["id"] == omitted:
            continue
        old, new = defect["repair"]["find"], defect["repair"]["replace"]
        if source.count(old) != 1:
            raise ValueError(f"Ambiguous change {defect['id']}")
        source = source.replace(old, new, 1)
    return source


def node_outcomes(report):
    if report["status"] in ("passed", "failed"):
        return {item["nodeid"]: item["outcome"] for item in report["cases"]}
    return {}


def test_names(code, target, witnesses, executed):
    """Count only unconditional top-level literal calls in executed test assertions."""
    module = ast.parse(code)
    function_names, module_names = set(), set()
    for node in module.body:
        if isinstance(node, ast.ImportFrom) and node.module == "subject":
            function_names.update(alias.asname or alias.name for alias in node.names if alias.name == target)
        if isinstance(node, ast.Import):
            module_names.update(alias.asname or alias.name for alias in node.names if alias.name == "subject")
    rebound = {node.id for node in ast.walk(module) if isinstance(node, ast.Name)
               and isinstance(node.ctx, (ast.Store, ast.Del))}
    function_names -= rebound
    module_names -= rebound
    signatures = {}
    for witness in witnesses:
        call = ast.parse(witness["call"], mode="eval").body
        signatures[ast.dump(call)] = witness["id"]
    covered = set()
    for function in module.body:
        if (not isinstance(function, ast.FunctionDef) or function.decorator_list
                or function.args.args or function.args.posonlyargs or function.args.kwonlyargs
                or function.args.vararg or function.args.kwarg):
            continue
        nodeid = "test_generated.py::" + function.name
        # Require a passed node so earlier assertions cannot have prevented the call.
        if executed.get(nodeid) != "passed":
            continue
        body = function.body[bool(ast.get_docstring(function)):]
        if not all(isinstance(statement, ast.Assert) for statement in body):
            continue
        for assertion in body:
            if not isinstance(assertion.test, ast.Compare):
                continue
            compare = assertion.test
            if len(compare.comparators) != 1 or not isinstance(compare.ops[0], (ast.Eq, ast.Is)):
                continue
            left, right = compare.left, compare.comparators[0]
            for call, control in ((left, right), (right, left)):
                if not isinstance(call, ast.Call) or isinstance(control, ast.Call):
                    continue
                try:
                    ast.literal_eval(control)
                except (TypeError, ValueError):
                    continue
                fn = call.func
                if ((isinstance(fn, ast.Name) and fn.id in function_names) or
                    (isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name)
                     and fn.value.id in module_names and fn.attr == target)):
                    call.func = ast.Name(id=target, ctx=ast.Load())
                    signature = ast.dump(call)
                    if signature in signatures:
                        covered.add(signatures[signature])
    return sorted(covered)


def evaluate(sample, module):
    target = sample["target"]
    cases = [case for case in module["tests"] if case["target"] == target]
    boundaries = [case for case in cases if case["category"] == "boundary"]
    ids = {case.get("defect") for case in cases}
    defects = [defect["id"] for defect in module["defects"] if defect["id"] in ids]
    row = {"module": module["name"], "tier": module["tier"], "target": target,
           "defects": defects, "boundaries": [case["id"] for case in boundaries],
           "evaluated": False, "detected": {}, "covered_boundaries": [], "false_alarm_nodes": []}
    suite = sample.get("suite")
    run = sample.get("run", {})
    observed = node_outcomes(run) if run else {}
    if not suite or suite["mode"] != "ai" or not observed or "error" in observed.values():
        return {**row, "reason": sample.get("error", "no complete AI Pytest run")}
    code = suite["source"]
    if (sample["analysis"]["sha256"] != module["sha256"] or
        suite["sha256"] != hashlib.sha256(code.encode()).hexdigest() or
        suite["id"] != run["suite_id"] or suite["file_id"] != run["file_id"] or
        suite["target"] != target):
        raise ValueError(f"Product linkage mismatch: {module['name']}")
    source = frozen_text(module["path"], module["sha256"])
    replay = execute(source, code, detailed=True)
    if case_map(replay) != observed:
        return {**row, "reason": "detailed WASI replay disagrees with recorded F04 nodes", "replay": replay}
    row.update(evaluated=True, counts={key: replay[key] for key in ("passed", "failed", "skipped")},
               covered_boundaries=test_names(code, target, boundaries, observed), replay=replay)
    asserted = {failure["nodeid"] for failure in replay["failures"] if test_assertion(failure, code)}
    if module["tier"] == "good":
        row["false_alarm_nodes"] = sorted(asserted)
    if not asserted or not defects:
        return row
    fixed = frozen_text(module["corrected_path"], module["corrected_sha256"])
    fixed_run = execute(fixed, code, detailed=True)
    row["corrected_replay"] = fixed_run
    fixed_nodes = case_map(fixed_run) or {}
    recovered = {node for node in asserted if fixed_nodes.get(node) == "passed"}
    if not recovered or fixed_nodes.keys() != observed.keys():
        return row
    attributed = defaultdict(list)
    row["single_repair_replays"] = {}
    adjudicable = True
    for defect in module["defects"]:
        key = defect["id"]
        repaired = corrupted_with_only(fixed, module["defects"], key)
        repair_run = execute(repaired, code, detailed=True)
        row["single_repair_replays"][key] = repair_run
        repaired_nodes = case_map(repair_run) or {}
        if repaired_nodes.keys() != observed.keys():
            adjudicable = False
            continue
        for node in recovered:
            if repaired_nodes[node] == "passed":
                attributed[node].append(key)
    for node, candidates in sorted(attributed.items()) if adjudicable else ():
        if len(candidates) == 1 and candidates[0] in defects:
            row["detected"].setdefault(candidates[0], []).append(node)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=LAB / "reports")
    args = parser.parse_args()
    directory = args.reports
    inventory = {item["name"]: item for item in load(LAB / "reference/ground_truth.json")["modules"]}
    product = load(directory / "product_blind.json", {"samples": []})["samples"]
    regressions = load(directory / "product_regression.json", {"samples": []})["samples"]
    campaigns = load(directory / "product_mutation.json", {"samples": []})["samples"]
    rows = []
    for sample in product:
        row = evaluate(sample, inventory[sample["module"]])
        rows.append(row)
        print(row["module"], row["evaluated"], sorted(row["detected"]), flush=True)
    result = {"schema_version": 1, "recorded_at": datetime.now(timezone.utc).isoformat(),
              "metrics": summarize(rows, regressions, campaigns), "samples": rows,
              "selection": {"planned_defects": sum(len(row["defects"]) for row in rows),
                            "planned_boundaries": sum(len(row["boundaries"]) for row in rows),
                            "captured_samples": len(rows),
                            "evaluable_samples": sum(row["evaluated"] for row in rows)}}
    (directory / "evaluation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                                               encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
