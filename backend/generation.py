"""Persist reviewable, immutable test suites; an adapter can replace local templates."""
import ast
import doctest
import hashlib
import json
from typing import Protocol

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .analysis import analyze
from .runs import run_suite
from .store import connect, many, one

router = APIRouter(prefix="/api")
SCHEMA = ("""CREATE TABLE IF NOT EXISTS suites (
    id INTEGER PRIMARY KEY, file_id INTEGER NOT NULL REFERENCES files(id),
    target TEXT NOT NULL, mode TEXT NOT NULL, source TEXT NOT NULL, sha256 TEXT NOT NULL,
    suggestions TEXT NOT NULL, UNIQUE(file_id,target,mode,sha256))""",)
SAMPLES = {"int": (2, 0), "float": (1.5, 0.0), "str": ("sample", ""), "bool": (True, False),
           "list": ([1], []), "dict": ({"a": 1}, {}), "tuple": ((1,), ())}


class GenerateInput(BaseModel):
    target: str = Field(min_length=1, max_length=256)
    mode: str = Field(default="template", max_length=64)


class ModelAdapter(Protocol):
    """Trusted, explicitly configured adapter. Returned code is only parsed on the host."""
    def generate(self, source: str, target: str) -> tuple[str, list[str]]: ...


class AIAdapter:
    def generate(self, source, target):
        from .engine_analyzer import analyze_source
        from .engine_strategy import build_strategy
        from .engine_llm import generate_tests

        analysis = analyze_source(source)
        strategy = build_strategy(analysis,target)
        result = generate_tests(source,target,analysis,strategy)
        return result["code"], [f"本机 AI 运行 ID {result['run_id']}"]


def example_tests(fn, *, respect_directives=False):
    result = []
    for example in doctest.DocTestParser().get_examples(ast.get_docstring(fn) or ""):
        if respect_directives and example.options:
            continue
        try:
            call = ast.parse(example.source.strip(), mode="eval").body
            if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name) or call.func.id != fn.name:
                continue
            for arg in [*call.args, *(kw.value for kw in call.keywords)]:
                ast.literal_eval(arg)
            call.func.id = "target"
            invocation = ast.unparse(call)
            if example.exc_msg:
                exc = example.exc_msg.split(":")[0].strip()
                if exc not in {"ValueError", "TypeError", "ZeroDivisionError", "IndexError", "KeyError"}:
                    continue
                assertion = f"with pytest.raises({exc}):\n        {invocation}"
            else:
                expected = ast.literal_eval(example.want.strip())
                assertion = f"assert {invocation} == {expected!r}"
            result.append(f"def test_example_{len(result)+1}():\n    {assertion}")
        except (SyntaxError, ValueError, TypeError, RecursionError):
            continue
    return result


class TemplateAdapter:
    def generate(self, source, target, *, respect_directives=False):
        analysis = analyze(source)
        if not analysis["valid"]:
            raise ValueError("请先修复语法错误")
        matches = [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == target]
        if len(matches) != 1:
            raise ValueError("请选择唯一的模块顶层同步函数")
        fn = matches[0]
        tests = example_tests(fn, respect_directives=respect_directives)
        signature = next(s for s in analysis["symbols"] if s["name"] == target)
        params = signature["parameters"]
        calls = [[], []]
        supported = True
        for p in params:
            if p["kind"].startswith("var_"):
                continue
            typ = (p["annotation"] or "").split("[")[0]
            if typ not in SAMPLES:
                if p["default"] is not None and p["kind"] != "positional_only":
                    continue
                supported = False
                break
            for i, values in enumerate(calls):
                value = repr(SAMPLES[typ][i])
                values.append(value if p["kind"] == "positional_only" else p["name"] + "=" + value)
        returns = (signature["returns"] or "").split("[")[0]
        if supported and returns in SAMPLES:
            for kind, values in zip(("normal", "boundary"), calls):
                tests.append(f"def test_{kind}_return_contract():\n"
                             f"    assert isinstance(target({', '.join(values)}), {returns})")
        if not fn.decorator_list and not fn.args.kwarg:
            unknown = "_testpilot_unexpected"
            while any(p["name"] == unknown for p in params):
                unknown += "_"
            tests.append(f"def test_invalid_keyword():\n    with pytest.raises(TypeError):\n        target({unknown}=None)")
        suggestions = []
        if supported and len(params) == 1 and params[0]["annotation"] == "int" and returns in SAMPLES:
            p = params[0]
            invocation = "target(x)" if p["kind"] == "positional_only" else f"target({p['name']}=x)"
            suggestions.append("用 Hypothesis 的 integers(min_value=-100, max_value=100) 检查返回类型契约。"
                               "若函数有输入前置条件，请先核对生成的取值范围。")
            if not p["kind"].startswith("var_"):
                tests.append("def test_property_return_contract():\n"
                             "    hypothesis = pytest.importorskip('hypothesis')\n"
                             "    from hypothesis import strategies as st\n"
                             "    @hypothesis.settings(max_examples=12, database=None, deadline=None)\n"
                             "    @hypothesis.given(st.integers(min_value=-100, max_value=100))\n"
                             "    def check(x):\n"
                             f"        assert isinstance({invocation}, {returns})\n    check()")
        if not tests:
            raise ValueError("缺少可验证契约，请补充带预期输出的 doctest 或类型标注")
        return "\n\n".join(["import pytest", f"from subject import {target} as target", *tests]), suggestions


def checked(code):
    if not isinstance(code, str) or len(code) > 131072:
        raise ValueError("测试源码超过限制")
    tree = ast.parse(code)
    if not any(isinstance(n, ast.FunctionDef) and n.name.startswith("test_") for n in tree.body):
        raise ValueError("未找到 Pytest 测试函数")
    normalized = ast.unparse(tree) + "\n"
    compile(normalized, "<generated-tests>", "exec", dont_inherit=True)
    return normalized


def unpack(row):
    return {**row, "suggestions": json.loads(row["suggestions"]), "format_checked": True}


def generate(file_id: int, item: GenerateInput, request: Request):
    path = request.app.state.db_path
    adapter = request.app.state.generators.get(item.mode)
    if adapter is None:
        raise HTTPException(422, "生成模式未配置")
    with connect(path) as db:
        source = one(db, "SELECT source FROM files WHERE id=?", (file_id,))["source"]
    try:
        code, suggestions = adapter.generate(source, item.target)
        code = checked(code)
    except (ValueError, SyntaxError, RecursionError) as exc:
        raise HTTPException(422, str(exc)) from exc
    digest = hashlib.sha256(code.encode()).hexdigest()
    with connect(path, write=True) as db:
        db.execute("INSERT OR IGNORE INTO suites(file_id,target,mode,source,sha256,suggestions) VALUES (?,?,?,?,?,?)",
                   (file_id, item.target, item.mode, code, digest, json.dumps(suggestions, ensure_ascii=False)))
        return unpack(one(db, "SELECT * FROM suites WHERE file_id=? AND target=? AND mode=? AND sha256=?",
                          (file_id, item.target, item.mode, digest)))


@router.post("/files/{file_id}/suites")
def generate_and_validate(file_id: int, item: GenerateInput, request: Request):
    suite = generate(file_id, item, request)
    saved = read_suite(suite["id"], request)
    if saved["initial_run"] is None:
        run_suite(request.app.state.db_path, suite["id"], file_id, reuse_existing=True)
        return read_suite(suite["id"], request)
    return saved


@router.get("/files/{file_id}/suites")
def list_suites(file_id: int, request: Request):
    with connect(request.app.state.db_path) as db:
        one(db, "SELECT id FROM files WHERE id=?", (file_id,))
        return many(db, "SELECT id,file_id,target,mode,sha256 FROM suites WHERE file_id=? ORDER BY id DESC", (file_id,))


@router.get("/suites/{suite_id}")
def read_suite(suite_id: int, request: Request):
    with connect(request.app.state.db_path) as db:
        suite = unpack(one(db, "SELECT * FROM suites WHERE id=?", (suite_id,)))
        run = db.execute("SELECT id,status FROM runs WHERE suite_id=? AND file_id=? ORDER BY id LIMIT 1",
                         (suite_id, suite["file_id"])).fetchone()
        suite["initial_run"] = dict(run) if run is not None else None
        return suite
