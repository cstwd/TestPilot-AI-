"""Adjudicate mutation results against the measured green original."""
from collections import Counter
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


def test_assertion(failure):
    """Allow only a documented test-side assertion or missing expected exception."""
    frames = failure.get("frames") or []
    if failure.get("phase") != "call" or not frames or frames[-1]["path"] != "test_generated.py":
        return False
    line = frames[-1]["source"].strip()
    if failure["exception_type"] == "AssertionError":
        return bool(re.match(r"assert\b", line))
    return (failure["exception_type"] == "Failed" and "DID NOT RAISE" in failure["message"]
            and bool(re.match(r"with\s+pytest\.raises\s*\(", line)))


def classify(baseline, execution):
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
            {f["nodeid"] for f in details} != failed or not all(test_assertion(f) for f in details)):
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
