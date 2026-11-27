from backend.analysis import analyze


def test_ast_without_execution(tmp_path):
    marker = tmp_path / "untouched"
    source = (f"open({str(marker)!r}, 'w')\nclass Box:\n"
              "    async def size(self, x:int, /, *, k=2, **options) -> int:\n        return x*k\n")
    result = analyze(source)
    assert result["valid"] and not marker.exists()
    cls, method = result["symbols"]
    assert cls["kind"] == "class" and method["name"] == "Box.size"
    assert (method["line"], method["end_line"], method["returns"]) == (3, 4, "int")
    assert method["parameters"][1]["kind"] == "positional_only"
    assert method["parameters"][2]["default"] == "2"
    assert method["parameters"][-1]["kind"] == "var_keyword"


def test_invalid_and_empty():
    assert analyze("def broken(:")["error"]["line"] == 1
    assert not analyze("return 1")["valid"]
    assert analyze("")["symbols"] == []


def test_conditional_definition():
    result = analyze("if True:\n    def enabled():\n        pass")
    assert [symbol["name"] for symbol in result["symbols"]] == ["enabled"]
