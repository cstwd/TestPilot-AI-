"""Diagnose real guest outcomes; ambiguous behavior remains available for review."""
import pytest

from backend.engine_analyzer import analyze_source
from backend.engine_failures import analyze_failures
from backend.engine_strategy import build_strategy
from backend.runner import execute


SOURCE = '''def units(n: int) -> int:
    """Examples.

    >>> units(2)
    50
    >>> units(0)
    Traceback (most recent call last):
    ...
    ValueError: zero
    >>> units(4)
    25
    >>> units(-2)
    Traceback (most recent call last):
    ...
    ValueError: negative
    """
    if n == 0:
        raise ValueError("zero")
    if n == 4:
        raise LookupError("bad")
    return n
'''

SUITE = '''import pytest
from subject import units as target

def test_wrong_output():
    assert target(n=2) == 50

def test_wrong_input_assumption():
    assert isinstance(target(n=0), int)

def test_wrong_expected():
    assert target(2) == 4

def test_unexpected_exception():
    assert target(4) == 25

def test_missing_exception():
    with pytest.raises(ValueError):
        target(-2)

def test_unknown_contract():
    assert target(11) == 99

def test_test_code():
    assert absent_name == 5

def test_skip():
    pytest.skip("optional")
'''


def test_real_failure_categories():
    analysis = analyze_source(SOURCE)
    strategy = build_strategy(analysis, "units")
    run = execute(SOURCE, SUITE, detailed=True)
    assert run["result_complete"] and run["failed"] == 7, run["log"]
    report = analyze_failures(run, strategy, SUITE, analysis)
    findings = {f["nodeid"].split("::")[-1]: f for f in report["findings"]}
    for name in ("test_wrong_output", "test_missing_exception", "test_unexpected_exception"):
        finding = findings[name]
        assert finding["category"] == "program_defect", finding
        assert finding["location"]["path"] == "subject.py" and finding["contract"]
    assert findings["test_wrong_output"]["assertion_diff"] and "50" in findings["test_wrong_output"]["assertion_diff"]
    assert findings["test_unexpected_exception"]["location"]["line"] > 1
    for name in ("test_wrong_expected", "test_wrong_input_assumption", "test_test_code"):
        assert findings[name]["category"] == "test_error", findings[name]
        assert findings[name]["location"]["path"] == "test_generated.py"
    assert findings["test_wrong_input_assumption"]["contract"]["call"] == "units(0)"
    assert findings["test_unknown_contract"]["category"] == "undetermined"
    assert findings["test_skip"]["category"] == "skipped"
    print([(name, item["category"], item["exception_type"]) for name, item in findings.items()])
    print("real traceback", findings["test_unexpected_exception"]["frames"])
    print("assertion difference", findings["test_wrong_output"]["assertion_diff"])


def test_incomplete_execution():
    analysis = analyze_source("def f(n): return n")
    strategy = build_strategy(analysis, "f")
    run = execute("def f(n): return n", "def test_slow():\n    while True: pass", timeout_s=3, detailed=True)
    findings = analyze_failures(run, strategy, "def test_slow():\n    while True: pass", analysis)["findings"]
    assert run["status"] == "timeout" and not run["result_complete"]
    assert len(findings) == 1 and findings[0]["category"] == "environment" and findings[0]["outcome"] == "timeout"
    print("timeout", findings[0]["message"])


@pytest.mark.parametrize("source", [
    "from subject import units as target\ndef test_f(target):\n    assert target(2) == 50",
    "from subject import units as target\ntarget = lambda n: 0\ndef test_f():\n    assert target(2) == 50",
    "from other import units as target\ndef test_f():\n    assert target(2) == 50",
])
def test_ambiguous_target_binding(source):
    # Narrow unit inputs for ambiguous bindings, separate from real guest checks above.
    analysis = analyze_source(SOURCE)
    strategy = build_strategy(analysis, "units")
    key = "test_generated.py::test_f"
    frames = [{"path": "test_generated.py", "line": len(source.splitlines()), "function": "test_f"}]
    run = {"status": "failed", "cases": [{"nodeid": key, "outcome": "failed"}],
           "failures": [{"phase": "call", "nodeid": key, "exception_type": "AssertionError", "frames": frames}]}
    finding, = analyze_failures(run, strategy, source, analysis)["findings"]
    assert finding["category"] == "undetermined" and finding["contract"] is None
