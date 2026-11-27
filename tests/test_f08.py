import json

import pytest

from backend.engine_analyzer import analyze_source
from backend.engine_strategy import build_strategy


def test_oracles_and_thresholds():
    code = '''def cost(count: int, /, *, names: list[str], rate: float = 1.0) -> float:
    """Return the cost.

    >>> cost(3, names=["x"])
    3.0
    >>> cost(-1, names=[])
    Traceback (most recent call last):
    ...
    ValueError: negative
    """
    if count < -2:
        raise ValueError("negative")
    for name in names:
        print(name)
    return rate * count
'''
    analysis = analyze_source(code)
    result = build_strategy(analysis, "cost")
    assert result == build_strategy(analysis, "cost")
    assert json.loads(json.dumps(result, allow_nan=False)) == result and result["source_sha256"] == analysis["sha256"]
    cases = result["cases"]
    assert len({c["id"] for c in cases}) == len(cases)
    kinds = {c["type"] for c in cases}
    assert kinds >= {"normal", "boundary", "empty", "null", "missing", "invalid_type", "special_numeric", "branch",
                     "return_constraint", "exception", "loop"}
    assert len(result["contracts"]) == 2
    assert [(c["expected"], c["contract_id"]) for c in cases if c["oracle"] == "doctest"] == [
        ("3.0", "example_1"), ("raises ValueError", "example_2")]
    branch, = [c for c in cases if c["type"] == "branch"]
    assert branch["condition"] == "count < -2" and not branch["needs_input_design"]
    assert {call.split(",", 1)[0] for call in branch["inputs"]} == {"cost(-3", "cost(-2", "cost(-1"}
    missing, = [c for c in cases if c["type"] == "missing"]
    assert missing["oracle"] == "signature" and missing["inputs"] == ["cost()"]
    hypothesis, = [c for c in cases if c.get("observed_exception")]
    assert hypothesis["oracle"] == "review" and hypothesis["observed_exception"] == "ValueError"
    assert all(c["oracle"] == "review" for c in cases if c["type"] == "invalid_type")
    assert any("float('nan')" in call for c in cases for call in c["inputs"])
    assert all(c["inputs"] and c["expected"] and c["purpose"] for c in cases)


def test_decorators_and_defaults():
    result = build_strategy(analyze_source("@custom\ndef f(*, x: int = 42): return x"), "f")
    missing, = [c for c in result["cases"] if c["type"] == "missing"]
    assert missing["inputs"] == ["f()"] and missing["oracle"] == "review"
    assert all(c["oracle"] != "signature" for c in result["cases"])
    assert result["contracts"] == []


def test_kwargs_and_positional_only_inputs():
    result = build_strategy(analyze_source("def f(a: int, /, **extras): return a"), "f")
    assert any(c["inputs"] == ["f(2)"] for c in result["cases"])
    assert not any("_testpilot_unknown" in arg for c in result["cases"] for arg in c["inputs"])


@pytest.mark.parametrize(("source", "target"), [("if False:\n def f(): pass", "f"), ("def broken(:", "f"),
                                              ("class C:\n def f(self): pass", "C.f"), ("def f(): pass", "g")])
def test_no_strategy_for_invalid_target(source, target):
    with pytest.raises(ValueError):
        build_strategy(analyze_source(source), target)
