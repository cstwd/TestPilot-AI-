import json

from hypothesis import given, settings, strategies as st

from backend.analysis import analyze


@given(st.integers(min_value=0, max_value=30), st.integers(), st.booleans())
@settings(max_examples=40, deadline=None, derandomize=True, database=None)
def test_ast_reports_exact_lines_and_parameter_defaults(prefix, default, asynchronous):
    declaration = "async def" if asynchronous else "def"
    source = "\n" * prefix + f"{declaration} sample(a: int, /, *, flag: int = {default}) -> int:\n    return a\n"
    result = analyze(source)
    assert result["valid"] and result["error"] is None
    symbol, = result["symbols"]
    assert symbol["kind"] == ("async_function" if asynchronous else "function")
    assert (symbol["line"], symbol["end_line"]) == (prefix + 1, prefix + 2)
    assert symbol["parameters"] == [
        {"name": "a", "kind": "positional_only", "annotation": "int", "default": None},
        {"name": "flag", "kind": "keyword_only", "annotation": "int", "default": str(default)},
    ]
    assert json.loads(json.dumps(result)) == result
