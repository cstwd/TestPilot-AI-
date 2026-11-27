import json
from textwrap import dedent

import pytest

from backend.engine_analyzer import analyze_source


def test_scope_and_dependencies(tmp_path):
    marker = tmp_path / "never_written"
    code = dedent("""
        from math import floor
        class Box:
            def size(self, x: float = 1.5, /, *, strict=False) -> int:
                """ + "'''Size of the box.'''" + """
                def nested():
                    raise LookupError()
                if strict and x < 0:
                    raise ValueError(x)
                return floor(x)
        def iterate(xs: list[int]):
            for n in xs:
                while n > 0:
                    n -= 1
            return [v for v in xs if v]
    """) + f"\nopen({str(marker)!r}, 'w')\n"
    result = analyze_source(code)
    assert result["valid"] and result["dependencies"] == ["math"]
    symbols = {s["name"]: s for s in result["symbols"]}
    method = symbols["Box.size"]
    assert method["kind"] == "method" and not method["testable"] and method["returns"] == "int"
    assert method["docstring"] == "Size of the box."
    assert method["parameters"][1] == {"name": "x", "kind": "positional_only", "annotation": "float", "default": "1.5"}
    assert method["parameters"][2]["kind"] == "keyword_only"
    assert [exc["name"] for exc in method["raises"]] == ["ValueError"]
    assert method["return_values"][0]["expression"] == "floor(x)"
    assert [call["name"] for call in method["calls"]] == ["ValueError", "floor"]
    assert [r["condition"] for r in method["branches"]] == ["strict and x < 0"]
    assert not symbols["Box.size.nested"]["testable"]
    target = symbols["iterate"]
    assert target["testable"] and [loop["kind"] for loop in target["loops"]] == ["For", "While", "comprehension"]
    assert not marker.exists() and json.loads(json.dumps(result)) == result


def test_literal_examples_are_not_executed():
    source = '''def f(x):
    """Examples.

    >>> f(-3)
    3
    >>> f(None)
    Traceback (most recent call last):
    ...
    ValueError: positive number required
    >>> f(open("anything"))
    0
    >>> f(9)  # doctest: +SKIP
    7
    """
    return x
'''
    examples = analyze_source(source)["symbols"][0]["examples"]
    assert examples == [
        {"id": "example_1", "source": "doctest", "call": "f(-3)", "expected": "3", "exception": None},
        {"id": "example_2", "source": "doctest", "call": "f(None)", "expected": None, "exception": "ValueError"},
    ]


@pytest.mark.parametrize(("source", "kind"), [
    (b"def bad(:", "syntax"), (b"\xff", "encoding"), (b"# coding: unknown_enc\n", "encoding"),
    ("return 1", "syntax"), (" " * (128 * 1024 + 1), "unsupported"), (object(), "unsupported"),
])
def test_invalid_source(source, kind):
    result = analyze_source(source)
    assert not result["valid"] and result["diagnostics"][0]["kind"] == kind
    assert result["symbols"] == []


def test_encoding_and_entries():
    raw = "# coding: latin-1\ndef café():\n    pass\n".encode("latin-1")
    assert analyze_source(raw)["symbols"][0]["name"] == "café"
    source = "if flag:\n    def optional(): pass\ndef same(): pass\ndef same(): pass\nasync def slow(): pass"
    result = analyze_source(source)
    assert result["valid"] and not any(s["testable"] for s in result["symbols"])
    assert result["diagnostics"][0]["kind"] == "unsupported_entry"
