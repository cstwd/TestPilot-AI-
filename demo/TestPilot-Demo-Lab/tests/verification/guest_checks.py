
"""Pytest cases supplied to the accepted TestPilot WASI runner."""
import ast
import builtins
from types import ModuleType

import pytest
import subject


def prepare_call(module, call):
    """Load a standalone frozen version and call its public function."""
    label, source = subject.SOURCES[module]
    loaded = ModuleType(label)
    exec(compile(source, label + ".py", "exec"), loaded.__dict__)
    expression = ast.parse(call, mode="eval").body
    args = [ast.literal_eval(arg) for arg in expression.args]
    kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in expression.keywords}
    return getattr(loaded, expression.func.id), args, kwargs


def assert_outcome(module, call, expected):
    function, args, kwargs = prepare_call(module, call)
    if "exception" in expected:
        with pytest.raises(getattr(builtins, expected["exception"])) as caught:
            function(*args, **kwargs)
        assert type(caught.value).__name__ == expected["exception"]
    else:
        assert function(*args, **kwargs) == ast.literal_eval(expected["value"])


@pytest.mark.parametrize("row", subject.CASES, ids=[row["id"] for row in subject.CASES])
def test_contract(row):
    assert_outcome(row["module"], row["call"], row["expected"])


@pytest.mark.parametrize("row", subject.WITNESSES, ids=[row["id"] for row in subject.WITNESSES])
def test_defect_witness(row):
    """Verify the exact faulty output and that fixing this change alone restores the contract."""
    assert_outcome(row["module"], row["call"], row["actual"])
    assert_outcome(row["fixed_one"], row["call"], row["expected"])
