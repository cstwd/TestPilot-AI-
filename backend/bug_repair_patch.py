"""Validate and assemble a source repair proposed by the pinned local model."""
import ast
from collections import Counter
import re

from pydantic import Field

from .model_protocol import Protocol


class Diagnosis(Protocol):
    cause: str = Field(min_length=1, max_length=1000)
    line: int = Field(ge=1)
    expected: str = Field(min_length=1, max_length=500)
    observed: str = Field(min_length=1, max_length=500)
    plan: str = Field(min_length=1, max_length=1000)


class Edit(Protocol):
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    original: str = Field(min_length=1, max_length=3000)
    replacement: str = Field(max_length=3000)
    reason: str = Field(min_length=1, max_length=500)


class Patch(Protocol):
    edits: list[Edit] = Field(min_length=1, max_length=5)


FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)
SCOPE = (*FUNCTIONS, ast.ClassDef)
# The edited implementation has no reason to interact with the regression
# harness or perform new introspection or runtime code loading.
HARNESSES = {
    "pytest", "hypothesis", "conftest", "test_generated", "inspect", "importlib",
    "sys", "os", "subprocess", "builtins", "__import__", "eval", "exec", "compile",
    "globals", "locals", "getattr", "setattr", "breakpoint", "__dict__", "__builtins__",
    "PYTEST_CURRENT_TEST", "AssertionError",
}


def interfaces(tree):
    result = []

    def visit(node, path):
        if isinstance(node, SCOPE):
            path = (*path, node.name)
            fields = tuple(
                (key, ast.dump(value) if isinstance(value, ast.AST) else tuple(map(ast.dump, value))
                 if isinstance(value, list) else value)
                for key, value in ast.iter_fields(node) if key != "body"
            )
            result.append((path, type(node), fields))
        for child in ast.iter_child_nodes(node):
            visit(child, path)

    visit(tree, ())
    return result


def protected_constructs(tree):
    findings = Counter()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Assert)):
            findings[ast.dump(node)] += 1
        if isinstance(node, ast.Name) and node.id in HARNESSES:
            findings[node.id] += 1
        if isinstance(node, ast.Attribute) and node.attr in HARNESSES:
            findings[node.attr] += 1
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in HARNESSES:
            findings[node.value] += 1
        if isinstance(node, ast.Return) and node.value is not None:
            value = node.value
            if isinstance(value, ast.Constant) and type(value.value) in (type(None), bool):
                continue
            if not any(isinstance(part, (ast.Name, ast.Call, ast.Attribute)) for part in ast.walk(value)):
                findings[ast.dump(node)] += 1
    return findings


def lines(text):
    return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def apply_patch(source, patch):
    original = ast.parse(source)
    content = re.findall(r"[^\r\n]*(?:\r\n|\r|\n|$)", source)
    if content and not content[-1]:
        content.pop()
    scopes = [node for node in ast.walk(original) if isinstance(node, FUNCTIONS)]
    previous = 0
    removed = added = 0
    replacements = []
    for edit in sorted(patch.edits, key=lambda item: item.start_line):
        start, end = edit.start_line, edit.end_line
        if start <= previous or start > end or end > len(content):
            raise ValueError("修复行号无效或有重叠")
        if not any(node.body[0].lineno <= start <= end <= node.end_lineno for node in scopes):
            raise ValueError("修复只能替换已有函数体内的连续行")
        old = "".join(content[start - 1:end])
        if lines(edit.original.rstrip("\r\n")) != lines(old.rstrip("\r\n")):
            raise ValueError("修复所引用的原文与原始版本不符，须逐字保留缩进")
        replacement = edit.replacement.rstrip("\r\n")
        if replacement == old.rstrip("\r\n"):
            raise ValueError("修复包含无变化的编辑")
        ending = re.search(r"(\r\n|\r|\n)$", old)
        separator = ending[0] if ending else "\n"
        inserted = separator.join(lines(replacement)) + (ending[0] if replacement and ending else "")
        removed += end - start + 1
        added += len(lines(replacement)) if replacement else 0
        replacements.append((start - 1, end, inserted))
        previous = end
    if max(removed, added) > 30:
        raise ValueError("修复范围超过 30 行，请缩小修改")
    for start, end, value in reversed(replacements):
        content[start:end] = [value]
    candidate = "".join(content)
    updated = ast.parse(candidate)
    compile(updated, "<repair-candidate>", "exec")
    if ast.dump(original) == ast.dump(updated):
        raise ValueError("修复没有改变 Python 逻辑")
    if interfaces(original) != interfaces(updated):
        raise ValueError("修复改变了原有函数、方法或类的接口")
    # Prevent an edit from escaping its original function body by dedenting new code.
    if strip_bodies(updated) - strip_bodies(original):
        raise ValueError("修复引入了测试框架、运行时反射或写死的返回值")
    if ast.dump(original) != ast.dump(updated):
        raise ValueError("修复在函数体外引入了修改")
    return candidate


def strip_bodies(tree):
    protected = protected_constructs(tree)
    for node in ast.walk(tree):
        if isinstance(node, FUNCTIONS):
            node.body = [ast.Pass()]
    return protected
