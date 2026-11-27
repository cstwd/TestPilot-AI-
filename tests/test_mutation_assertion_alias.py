"""WP04: replay real missing-exception assertions with explicit and ambiguous bindings."""
from backend.mutation_results import baseline_ok, classify
from backend.mutation_results import test_assertion as assertion_supported
from backend.runner import execute


SOURCE = """def check(x):
    if x < 0:
        raise ValueError('negative')
    return x
"""


def measure(code):
    green = execute(SOURCE, code, detailed=True, timeout_s=25)
    mutant = execute(SOURCE.replace("raise ValueError('negative')", "pass"), code, detailed=True, timeout_s=25)
    assert baseline_ok(green) and mutant["status"] == "failed" and mutant["exit_code"] == 1
    assert all(f["phase"] == "call" and f["message"].startswith("DID NOT RAISE") for f in mutant["failures"])
    verdict = classify(green, mutant, test_code=code)
    print("WASI:", green["passed"], "passed on original,", mutant["failed"], "failed on mutant;", verdict)
    return verdict, mutant


def test_real_imported_aliases_kill_suppressed_raise():
    code = """import pytest as pt
from pytest import raises
from subject import check

def test_module_alias():
    with pt.raises(ValueError):
        check(-1)

def test_direct_binding():
    with raises(ValueError):
        check(-1)

def test_local_alias():
    from pytest import raises as expect_error
    with expect_error(ValueError):
        check(-1)
"""
    verdict, _ = measure(code)
    assert verdict["status"] == "killed"
    assert len(verdict["nodeids"]) == 3


def test_real_custom_and_rebound_names_cannot_prove_a_kill():
    code = """import pytest as pt
from pytest import raises as delegate
from subject import check

class LocalChecks:
    raises = staticmethod(delegate)

def test_custom_binding():
    pytest = LocalChecks
    with pytest.raises(ValueError):
        check(-1)

def test_rebound_alias():
    pt = LocalChecks
    with pt.raises(ValueError):
        check(-1)
"""
    verdict, mutant = measure(code)
    assert verdict["status"] == "execution_error"
    # Both delegating context managers produce genuine pytest Failed outcomes.
    # The submitted source still supplies neither call through a trusted import.
    for failure in mutant["failures"]:
        assert not assertion_supported(failure, code)
