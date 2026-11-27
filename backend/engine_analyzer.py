"""Static facts about one Python revision. Source and doctests are parsed as data."""
import ast
import builtins
import doctest
import hashlib
import io
import tokenize

from .analysis import expression, parameters


DEFINITIONS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
MAX_BYTES = 128 * 1024


def examples(node):
    contracts = []
    try:
        entries = doctest.DocTestParser().get_examples(ast.get_docstring(node) or "")
    except ValueError:
        return contracts
    for entry in entries:
        if entry.options or not entry.want:
            continue
        try:
            call = ast.parse(entry.source.strip(), mode="eval").body
            if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name) or call.func.id != node.name:
                continue
            if any(kw.arg is None for kw in call.keywords):
                continue
            for arg in [*call.args, *(kw.value for kw in call.keywords)]:
                ast.literal_eval(arg)
            exception = expected = None
            if entry.exc_msg:
                exception = entry.exc_msg.split(":", 1)[0].strip()
                cls = vars(builtins).get(exception)
                if not isinstance(cls, type) or not issubclass(cls, Exception):
                    continue
            else:
                expected = repr(ast.literal_eval(entry.want.strip()))
            contracts.append({"id": f"example_{len(contracts) + 1}", "source": "doctest",
                              "call": ast.unparse(call), "expected": expected, "exception": exception})
        except (SyntaxError, ValueError, TypeError, RecursionError, OverflowError):
            continue
    return contracts


def within_scope(statements):
    """Yield facts in source order without attributing a nested body's effects to its parent."""
    stack = list(reversed(statements))
    while stack:
        node = stack.pop()
        yield node
        if not isinstance(node, (*DEFINITIONS, ast.Lambda)):
            stack.extend(reversed(list(ast.iter_child_nodes(node))))


def import_names(node):
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if isinstance(node, ast.ImportFrom):
        return ["." * node.level + (node.module or "")]
    return []


def facts(node):
    result = {key: [] for key in ("branches", "loops", "return_values", "raises", "calls", "dependencies")}
    for child in within_scope(node.body):
        line = getattr(child, "lineno", None)
        if isinstance(child, (ast.If, ast.IfExp, ast.While)):
            result["branches"].append({"kind": type(child).__name__, "condition": expression(child.test), "line": line})
        if isinstance(child, ast.Match):
            for case in child.cases:
                result["branches"].append({"kind": "match_case", "condition": expression(case.pattern),
                                           "guard": expression(case.guard), "line": case.pattern.lineno})
        if isinstance(child, (ast.For, ast.AsyncFor, ast.While)):
            test = child.test if isinstance(child, ast.While) else child.iter
            result["loops"].append({"kind": type(child).__name__, "expression": expression(test), "line": line})
        elif isinstance(child, ast.comprehension):
            result["loops"].append({"kind": "comprehension", "expression": expression(child.iter), "line": child.iter.lineno})
            for condition in child.ifs:
                result["branches"].append({"kind": "filter", "condition": expression(condition), "line": condition.lineno})
        elif isinstance(child, ast.Raise):
            exc = child.exc.func if isinstance(child.exc, ast.Call) else child.exc
            result["raises"].append({"name": expression(exc), "expression": expression(child.exc), "line": line})
        elif isinstance(child, ast.ExceptHandler):
            result["branches"].append({"kind": "except", "condition": expression(child.type), "line": line})
        elif isinstance(child, ast.Return):
            result["return_values"].append({"expression": expression(child.value) or "None", "line": line})
        elif isinstance(child, ast.Call):
            result["calls"].append({"name": expression(child.func), "line": line})
        result["dependencies"].extend(import_names(child))
    result["dependencies"] = sorted(set(result["dependencies"]))
    return result


def collect_symbols(statements, prefix="", owner=None):
    direct_ids = {id(statement) for statement in statements}
    for node in within_scope(statements):
        if not isinstance(node, DEFINITIONS):
            continue
        name = prefix + node.name
        is_class = isinstance(node, ast.ClassDef)
        method = isinstance(owner, ast.ClassDef)
        kind = "class" if is_class else "method" if method else "function"
        if isinstance(node, ast.AsyncFunctionDef):
            kind = "async_" + kind
        testable = not prefix and kind == "function" and id(node) in direct_ids
        symbol = {"name": name, "kind": kind, "line": node.lineno, "end_line": node.end_lineno,
                  "parameters": [] if is_class else parameters(node.args),
                  "returns": None if is_class else expression(node.returns),
                  "docstring": ast.get_docstring(node) or "", "testable": testable,
                  "decorators": [expression(d) for d in node.decorator_list],
                  "examples": [] if is_class else examples(node), **facts(node)}
        yield symbol
        yield from collect_symbols(node.body, name + ".", node)


def analyze_source(source: str | bytes) -> dict:
    report = {"valid": False, "symbols": [], "dependencies": [], "diagnostics": [], "sha256": None}
    try:
        if not isinstance(source, (bytes, str)):
            raise TypeError("源码必须是文本或字节。")
        raw = source.encode("utf-8") if isinstance(source, str) else source
        report["sha256"] = hashlib.sha256(raw).hexdigest()
        if len(raw) > MAX_BYTES:
            raise ValueError("源码超过 128 KiB 分析上限。")
        if isinstance(source, bytes):
            try:
                encoding, _ = tokenize.detect_encoding(io.BytesIO(source).readline)
                source = source.decode(encoding)
            except (SyntaxError, UnicodeError, LookupError) as exc:
                raise UnicodeError(str(exc)) from exc
        tree = ast.parse(source)
        if sum(1 for _ in ast.walk(tree)) > 24000:
            raise ValueError("源码超过 24000 个语法节点。")
        compile(tree, "<revision>", "exec", dont_inherit=True)
        symbols = list(collect_symbols(tree.body))
        names = {}
        for symbol in symbols:
            names[symbol["name"]] = names.get(symbol["name"], 0) + 1
        for symbol in symbols:
            if names[symbol["name"]] != 1:
                symbol["testable"] = False
        report.update(valid=True, symbols=symbols, dependencies=sorted({
            name for node in ast.walk(tree) for name in import_names(node)
        }))
        if not any(symbol["testable"] for symbol in symbols):
            report["diagnostics"].append({"kind": "unsupported_entry", "message": "未找到可独立生成测试的顶层同步函数。"})
    except (SyntaxError, TypeError, ValueError, RecursionError, OverflowError) as exc:
        kind = "encoding" if isinstance(exc, UnicodeError) else "syntax" if isinstance(exc, SyntaxError) else "unsupported"
        report["diagnostics"].append({"kind": kind, "message": getattr(exc, "msg", str(exc)),
                                      "line": getattr(exc, "lineno", None), "column": getattr(exc, "offset", None)})
    return report
