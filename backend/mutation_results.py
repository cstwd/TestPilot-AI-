"""Adjudicate mutation results against the measured green original."""
from collections import Counter
import ast
import re


STATUSES = ("killed", "survived", "timeout", "execution_error", "cancelled", "unrun")


def case_map(execution):
    """Reject partial or internally inconsistent evidence from the guest."""
    if not execution.get("result_complete"):
        return None
    cases = execution["cases"]
    results = {case["nodeid"]: case["outcome"] for case in cases}
    if len(results) != len(cases):
        return None
    counts = Counter(results.values())
    columns = {"passed": "passed", "failed": "failed", "error": "errors", "skipped": "skipped"}
    if counts.keys() - columns.keys() or any(counts[key] != execution[column] for key, column in columns.items()):
        return None
    return results


def baseline_ok(execution):
    return (execution.get("status") == "passed" and execution.get("exit_code") == 0
            and bool(case_map(execution)) and execution["passed"] > 0
            and execution["failed"] == execution["errors"] == 0)


def pytest_binding(scope, name, direct_raises, inherited=False, before=None):
    """Accept an explicit import in this scope. Ambiguous or rebound names fail closed."""
    if isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if any(isinstance(arg, ast.arg) and arg.arg == name for arg in ast.walk(scope.args)):
            return False
    found = inherited
    pending = list(scope.body)
    while pending:
        node = pending.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name == name:
                return False
            continue
        if isinstance(node, ast.Lambda):
            continue
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                if alias.name == "*":
                    return False
                if (alias.asname or alias.name.split(".")[0]) != name:
                    continue
                if isinstance(node, ast.Import):
                    trusted = not direct_raises and alias.name == "pytest"
                else:
                    trusted = direct_raises and not node.level and node.module == "pytest" and alias.name == "raises"
                if not trusted or node not in scope.body or (before is not None and node.lineno >= before):
                    return False
                found = True
        elif ((isinstance(node, ast.Name) and node.id == name and isinstance(node.ctx, (ast.Store, ast.Del)))
              or (isinstance(node, (ast.ExceptHandler, ast.MatchAs, ast.MatchStar)) and node.name == name)
              or (isinstance(node, ast.MatchMapping) and node.rest == name)
              or (isinstance(node, (ast.Global, ast.Nonlocal)) and name in node.names)
              or (isinstance(node, ast.Attribute) and isinstance(node.ctx, (ast.Store, ast.Del))
                  and isinstance(node.value, ast.Name) and node.value.id == name and node.attr == "raises")):
            return False
        pending.extend(ast.iter_child_nodes(node))
    return found


def verified_raises(test_code, frame):
    try:
        tree = ast.parse(test_code)
    except (SyntaxError, ValueError, RecursionError):
        return False
    line = frame["line"]
    scopes = sorted((n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                     and n.lineno <= line <= n.end_lineno), key=lambda n: n.lineno)
    if not scopes or scopes[-1].name != frame["function"]:
        return False
    contexts = [n for n in ast.walk(scopes[-1]) if isinstance(n, ast.With) and n.lineno == line]
    if len(contexts) != 1 or len(contexts[0].items) != 1:
        return False
    expr = contexts[0].items[0].context_expr
    if not isinstance(expr, ast.Call):
        return False
    direct = isinstance(expr.func, ast.Name)
    if direct:
        name = expr.func.id
    elif isinstance(expr.func, ast.Attribute) and expr.func.attr == "raises" and isinstance(expr.func.value, ast.Name):
        name = expr.func.value.id
    else:
        return False
    trusted = pytest_binding(tree, name, direct)
    for scope in scopes:
        trusted = pytest_binding(scope, name, direct, trusted, line)
    return trusted


def test_assertion(failure, test_code=None):
    """Allow only a documented test-side assertion or missing expected exception."""
    frames = failure.get("frames") or []
    if failure.get("phase") != "call" or not frames or frames[-1]["path"] != "test_generated.py":
        return False
    line = frames[-1]["source"].strip()
    if failure["exception_type"] == "AssertionError":
        return bool(re.match(r"assert\b", line))
    if failure["exception_type"] != "Failed" or not re.match(r"DID NOT RAISE\b", failure["message"]):
        return False
    if test_code is None:
        return bool(re.match(r"with\s+pytest\.raises\s*\(", line))
    return verified_raises(test_code, frames[-1])


def classify(baseline, execution, test_code=None):
    def result(status, reason, nodeids=()):
        return {"status": status, "reason": reason, "nodeids": sorted(nodeids)}

    if execution["status"] in ("cancelled", "timeout"):
        return result(execution["status"], execution.get("diagnostic") or execution["status"])
    if not baseline_ok(baseline):
        return result("execution_error", "原始源码缺少有效的通过基线")
    observed = case_map(execution)
    original = case_map(baseline)
    if observed is None or observed.keys() != original.keys():
        return result("execution_error", "执行不完整或前后测试节点集合不同")
    if any((observed[key] == "skipped") != (original[key] == "skipped") for key in original):
        return result("execution_error", "跳过的测试节点与原始运行不同")
    if baseline_ok(execution):
        return result("survived", "相同测试节点运行通过")
    if execution["status"] != "failed" or execution["exit_code"] != 1 or execution["errors"]:
        return result("execution_error", "执行、收集或夹具出现错误")
    failed = {key for key, outcome in observed.items() if outcome == "failed"}
    details = execution.get("failures", [])
    if (not failed or execution.get("failure_details_omitted") or
            {f["nodeid"] for f in details} != failed or not all(test_assertion(f, test_code) for f in details)):
        return result("execution_error", "失败没有完整的测试断言证据", failed)
    return result("killed", "原始通过节点在变异副本上触发测试断言", failed)


def score(mutants, outcomes):
    ids = {mutant["id"] for mutant in mutants}
    if len(ids) != len(mutants) or outcomes.keys() - ids:
        raise ValueError("变异标识重复，或结果引用了清单外的变异")
    counts = dict.fromkeys(STATUSES, 0)
    for mutant_id in ids:
        status = outcomes[mutant_id]["status"] if mutant_id in outcomes else "unrun"
        if status not in counts:
            raise ValueError("未识别的变异状态")
        counts[status] += 1
    return {**counts, "total": len(ids),
            "equivalent_candidates": sum(bool(m.get("equivalent_candidate")) for m in mutants),
            "score_pct": round(100 * counts["killed"] / len(ids), 2) if ids else None}
