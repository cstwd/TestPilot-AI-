
"""Regression checks for independent scoring evidence."""
from pathlib import Path
import sys

import pytest

LAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LAB / "evaluation"))
from evaluator import test_names as covered_inputs  # noqa: E402
from metrics import ratio  # noqa: E402


@pytest.mark.parametrize(("body", "expected"), [
    ("assert target(5) == 10", ["example_01"]),
    ("return\n    assert target(5) == 10", []),
    ("target = lambda x: 10\n    assert target(5) == 10", []),
    ("assert target(5) == target(5)", []),
    ("assert target(4) == 8", []),
])
def test_only_observed_direct_assertions_count(body, expected):
    code = f"from subject import multiply as target\n\ndef test_case():\n    {body}\n"
    witnesses = [{"id": "example_01", "call": "multiply(5)"}]
    nodes = {"test_generated.py::test_case": "passed"}
    assert covered_inputs(code, "multiply", witnesses, nodes) == expected


@pytest.mark.parametrize(("prelude", "call"), [
    ("from subject import multiply as target\ndef target(x): return 10", "target(5)"),
    ("import subject\nsubject.multiply = lambda x: 10", "subject.multiply(5)"),
])
def test_module_scope_rebinding_cannot_count(prelude, call):
    code = prelude + f"\ndef test_case():\n    assert {call} == 10"
    witnesses = [{"id": "example_01", "call": "multiply(5)"}]
    assert covered_inputs(code, "multiply", witnesses, {"test_generated.py::test_case": "passed"}) == []


def test_absent_denominator_stays_unmeasured():
    assert ratio(0, 0) == {"numerator": 0, "denominator": 0, "percentage": None}
    assert ratio(0, 2) == {"numerator": 0, "denominator": 2, "percentage": 0.0}
    with pytest.raises(ValueError):
        ratio(3, 2)
