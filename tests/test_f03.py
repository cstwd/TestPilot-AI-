import ast
import pytest

from backend.generation import TemplateAdapter, checked


def test_templates_include_actual_spec():
    source = "def magnitude(x: int) -> int:\n    '''\n    >>> magnitude(-3)\n    3\n    '''\n    return x"
    code, hints = TemplateAdapter().generate(source, "magnitude")
    formatted = checked(code)
    assert "assert target(-3) == 3" in formatted and "test_invalid_keyword" in formatted
    assert "test_boundary_return_contract" in formatted and hints
    assert any(n.name == "test_property_return_contract" for n in ast.parse(formatted).body if isinstance(n, ast.FunctionDef))


def test_reject_bad_output_and_targets():
    with pytest.raises(ValueError):
        checked("n = 42")
    with pytest.raises(SyntaxError):
        checked("def test_x(")
    with pytest.raises(ValueError):
        TemplateAdapter().generate("class A: pass", "A")
