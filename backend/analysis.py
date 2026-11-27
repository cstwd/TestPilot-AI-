"""Bounded, non-executing structural analysis of a Python source revision."""
import ast

from fastapi import APIRouter, Request

from .projects import read_file

router = APIRouter(prefix="/api")


def expression(node):
    return ast.unparse(node) if node is not None else None


def parameters(args):
    positional = [*args.posonlyargs, *args.args]
    defaults = [None] * (len(positional) - len(args.defaults)) + args.defaults
    entries = [(arg, "positional_only" if i < len(args.posonlyargs) else "positional_or_keyword", default)
               for i, (arg, default) in enumerate(zip(positional, defaults))]
    if args.vararg:
        entries.append((args.vararg, "var_positional", None))
    entries.extend((arg, "keyword_only", default) for arg, default in zip(args.kwonlyargs, args.kw_defaults))
    if args.kwarg:
        entries.append((args.kwarg, "var_keyword", None))
    return [{"name": arg.arg, "kind": kind, "annotation": expression(arg.annotation),
             "default": expression(default)} for arg, kind, default in entries]


def symbols_in(nodes, prefix=""):
    for node in nodes:
        if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if isinstance(node, (ast.stmt, ast.ExceptHandler, ast.match_case)):
                yield from symbols_in(ast.iter_child_nodes(node), prefix)
            continue
        name = prefix + node.name
        is_class = isinstance(node, ast.ClassDef)
        yield {"name": name, "kind": "class" if is_class else
               ("async_function" if isinstance(node, ast.AsyncFunctionDef) else "function"),
               "line": node.lineno, "end_line": node.end_lineno,
               "parameters": [] if is_class else parameters(node.args),
               "returns": None if is_class else expression(node.returns),
               "docstring": ast.get_docstring(node) or ""}
        yield from symbols_in(node.body, name + ".")


def analyze(source):
    try:
        tree = ast.parse(source)
        if sum(1 for _ in ast.walk(tree)) > 24000:
            raise ValueError("超过 24000 个语法节点的分析上限")
        # Compilation catches context errors such as return outside a function.
        compile(tree, "<revision>", "exec", dont_inherit=True)
        return {"valid": True, "symbols": list(symbols_in(tree.body)), "error": None}
    except (SyntaxError, ValueError, RecursionError, OverflowError) as exc:
        return {"valid": False, "symbols": [], "error": {
            "message": getattr(exc, "msg", str(exc)), "line": getattr(exc, "lineno", None),
            "column": getattr(exc, "offset", None)}}


@router.get("/files/{file_id}/analysis")
def analysis(file_id: int, request: Request):
    row = read_file(file_id, request)
    return {"file_id": file_id, "filename": row["filename"], "revision": row["revision"],
            "sha256": row["sha256"], **analyze(row["source"])}
