"""F13 evidence classification and cancellation in the real WASI runner."""
import copy
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from backend import runner
from backend.mutation_results import baseline_ok, classify, score


SOURCE = "def check(x):\n    if x < 0:\n        raise ValueError('negative')\n    return x + 1"
SUITE = """import pytest
from subject import check

def test_value():
    assert check(0) == 1

def test_negative():
    from subject import check
    import pytest
    with pytest.raises(ValueError):
        check(-1)

def test_pending():
    pytest.skip("explicit optional check")
"""


@pytest.fixture(scope="module")
def green():
    report = runner.execute(SOURCE, SUITE, detailed=True)
    assert baseline_ok(report), report
    return report


@pytest.mark.parametrize(("replacement", "verdict", "node"), [
    ("return x + 1", "survived", None),
    ("return x + 2", "killed", "test_value"),
    ("return int('invalid')", "execution_error", "test_value"),
])
def test_real_outcomes(green, replacement, verdict, node):
    changed = SOURCE.replace("return x + 1", replacement)
    observed = runner.execute(changed, SUITE, detailed=True, cancel_event=threading.Event())
    result = classify(green, observed)
    print("WASI", repr(replacement), observed["status"], observed["exit_code"], result)
    assert result["status"] == verdict
    if node:
        assert result["nodeids"] == ["test_generated.py::" + node]


def test_expected_exception_removed(green):
    changed = SOURCE.replace("raise ValueError('negative')", "return 0")
    observed = runner.execute(changed, SUITE, detailed=True)
    result = classify(green, observed)
    assert result["status"] == "killed", observed["failures"]
    assert result["nodeids"] == ["test_generated.py::test_negative"]
    print("exception removed", observed["failures"][0]["message"], result)


def test_changed_evidence_cannot_score(green):
    for status in ("timeout", "cancelled"):
        assert classify(green, {"status": status})["status"] == status
    assert classify(green, {"status": "error", "result_complete": False})["status"] == "execution_error"
    changed = copy.deepcopy(green)
    changed["cases"][0]["nodeid"] += "_renamed"
    assert classify(green, changed)["status"] == "execution_error"
    changed = copy.deepcopy(green)
    skipped = next(c for c in changed["cases"] if c["outcome"] == "skipped")
    passed = next(c for c in changed["cases"] if c["outcome"] == "passed")
    skipped["outcome"], passed["outcome"] = "passed", "skipped"
    assert classify(green, changed)["status"] == "execution_error"
    changed["passed"] += 1
    assert not baseline_ok(changed)


@pytest.mark.parametrize(("replacement", "timeout", "status"), [
    ("if", 15, "execution_error"), ("while True:\n        pass", 4, "timeout"),
])
def test_unusable_mutant_execution(green, replacement, timeout, status):
    changed = SOURCE.replace("return x + 1", replacement)
    observed = runner.execute(changed, SUITE, detailed=True, timeout_s=timeout)
    result = classify(green, observed)
    assert result["status"] == status, observed
    print("invalid or timed-out mutant", observed["exit_code"], result)


def test_manifest_denominator():
    pool = [{"id": str(i), "equivalent_candidate": i == 5} for i in range(6)]
    outcomes = {str(i): {"status": val} for i, val in enumerate(
        ["killed", "survived", "cancelled", "execution_error", "timeout"])}
    assert score(pool, outcomes) == {"total": 6, "killed": 1, "survived": 1, "cancelled": 1, "unrun": 1,
                                    "execution_error": 1, "timeout": 1, "equivalent_candidates": 1,
                                    "score_pct": 16.67}
    assert score([], {})["score_pct"] is None
    with pytest.raises(ValueError):
        score(pool + [pool[0]], outcomes)
    with pytest.raises(ValueError):
        score(pool, {"other": {"status": "killed"}})


def test_cancel_live_guest(monkeypatch):
    token = threading.Event()
    spawned = threading.Event()
    actual_process = {}
    real_popen = runner.subprocess.Popen

    def observe(*args, **kwargs):
        proc = real_popen(*args, **kwargs)
        actual_process.update(process=proc, job=Path(kwargs["cwd"]))
        spawned.set()
        return proc

    monkeypatch.setattr(runner.subprocess, "Popen", observe)
    suite = "def test_loop():\n    print('guest running', flush=True)\n    while True:\n        pass"
    with ThreadPoolExecutor(max_workers=1) as thread:
        future = thread.submit(runner.execute, SOURCE, suite, timeout_s=40, detailed=True, cancel_event=token)
        try:
            assert spawned.wait(timeout=10)
            stream = actual_process["job"] / "stdout.log"
            deadline = time.monotonic() + 35
            while "guest running" not in runner.read_log(stream):
                assert time.monotonic() < deadline and not future.done(), "guest did not reach running test"
                time.sleep(0.1)
        finally:
            token.set()
        result = future.result(timeout=10)
    assert result["status"] == "cancelled" and not result["result_complete"]
    assert result["passed"] is None and result["exit_code"] is None
    assert "guest running" in result["stdout"]
    assert actual_process["process"].poll() is not None
    assert not actual_process["job"].exists()
    print("live guest cancelled; worker reaped; job cleaned; result_complete=False")


def test_bounded_slot_wait_and_queue_cancellation(monkeypatch):
    with runner.ACTIVE:
        monkeypatch.setattr(runner, "SLOT_WAIT_SECONDS", 0.1)
        busy = runner.execute(SOURCE, SUITE, detailed=True, cancel_event=threading.Event())
        assert busy["resource_busy"] and busy["exit_code"] is None
        token = threading.Event()
        token.set()
        cancelled = runner.execute(SOURCE, SUITE, detailed=True, cancel_event=token)
        assert cancelled["status"] == "cancelled" and not cancelled["resource_busy"]
    print("queued slot timeout returns retryable resource_busy; queued cancellation stops before spawn")
