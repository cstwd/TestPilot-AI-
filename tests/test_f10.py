"""Exercise phase 03 measurements inside the real WASI guest."""
from backend.runner import execute


def test_branch_evidence_and_runtime_failure_details():
    source = """def classify(n):
    if n > 0:
        return 'positive'
    return 'other'
"""
    suite = """import sys
import pytest
from subject import classify

def test_compare():
    print("written-to-stdout")
    print("written-to-stderr", file=sys.stderr)
    assert classify(2) == "other"

def test_type():
    classify(None)

def test_skipped():
    pytest.skip("no contract")
"""
    report = execute(source, suite, detailed=True)
    assert report["result_complete"], report["log"]
    assert report["status"] == "failed"
    assert (report["failed"], report["skipped"], report["exit_code"]) == (2, 1, 1)
    assert (report["covered_branches"], report["total_branches"], report["branch_pct"]) == (1, 2, 50)
    assert (report["covered_lines"], report["total_lines"]) == (3, 4)
    assert "written-to-stdout" in report["stdout"] and "written-to-stderr" in report["stderr"]
    assert "TESTPILOT_RESULT" not in report["stdout"]
    failures = {detail["nodeid"]: detail for detail in report["failures"]}
    comparison = failures["test_generated.py::test_compare"]
    assert comparison["exception_type"] == "AssertionError" and comparison["phase"] == "call"
    assert all(s in comparison["assertion_diff"] for s in ("positive", "other"))
    assert comparison["frames"][-1]["line"] == 8
    type_error = failures["test_generated.py::test_type"]
    assert type_error["exception_type"] == "TypeError"
    assert type_error["frames"][-1] == {"path": "subject.py", "line": 2, "function": "classify", "source": "if n > 0:"}
    print("WASI", report["environment"], "line 3/4 branch 1/2", comparison, type_error)


def test_collection_failure_is_structured():
    report = execute("def ok(): return True", "from subject import missing\ndef test_it(): pass", detailed=True)
    assert report["result_complete"] and report["status"] == "error", report["log"]
    assert report["errors"] == 1 and report["exit_code"] == 2
    failure, = report["failures"]
    assert failure["phase"] == "collect" and failure["exception_type"] == "ImportError"
    assert failure["frames"][-1]["path"] == "test_generated.py"
    assert (report["total_branches"], report["branch_pct"]) == (0, None)
    print("collection failure", failure)


def test_timeout_preserves_incomplete_evidence():
    report = execute("", "def test_wait():\n    while True:\n        pass", timeout_s=2, detailed=True)
    assert report["status"] == "timeout" and not report["result_complete"], report["log"]
    assert report["failed"] is None and report["covered_branches"] is None and report["total_lines"] is None
    assert isinstance(report["stdout"], str) and isinstance(report["stderr"], str)
    assert "deadline" in report["diagnostic"]
    print("deadline", report["diagnostic"], "case counts and coverage unavailable")
