"""Repair only diagnosed generated test statements; keep the submitted source immutable."""
import ast
import hashlib

from .engine_failures import imports, tested_expression
from .engine_llm import GenerationFailure, generate_tests
from .generation import checked


def digest(code):
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def eligible(findings):
    failing = [f for f in findings if f["outcome"] != "skipped"]
    return bool(failing) and all(f["category"] == "test_error" for f in failing)


def allowed_edit(previous, target, findings):
    """A model edit must match an independently justified change at the failing line."""
    tree = ast.parse(previous)
    aliases = imports(tree, target)
    tests = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    needs_pytest = False
    edits = []
    for finding in findings:
        if finding["category"] != "test_error":
            continue
        name = finding["nodeid"].split("::")[-1]
        fn = tests.get(name)
        line = finding["test_line"]
        if not fn or not line or fn.decorator_list:
            raise ValueError("失败节点不能对应到单一顶层测试语句")
        index = next((i for i, stmt in enumerate(fn.body) if stmt.lineno <= line <= stmt.end_lineno), None)
        if index is None:
            raise ValueError("无法定位失败语句")
        frame = {"function": name, "line": line}
        contract = finding.get("contract")
        observed = tested_expression(tree, frame, aliases)
        if contract and observed:
            call = ast.unparse(observed[0])
            if contract["exception"]:
                replacement = f"with pytest.raises({contract['exception']}):\n    {call}"
                needs_pytest = True
            else:
                ast.literal_eval(contract["expected"])
                replacement = f"assert {call} == {contract['expected']}"
            edits.append((fn, index, ast.parse(replacement).body[0]))
        else:
            raise ValueError("缺少能独立核验修正的文档契约，保留失败语句供复核")
    if not edits:
        raise ValueError("没有可以核验的修正")
    for fn, index, replacement in edits:
        fn.body[index] = replacement
    if needs_pytest and not any(isinstance(node, ast.Import) and
                                any(a.name == "pytest" and a.asname in (None, "pytest") for a in node.names)
                                for node in tree.body):
        # Preserve the module docstring and any __future__ imports.
        offset = 0
        for node in tree.body:
            if ((offset == 0 and isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
                 and isinstance(node.value.value, str)) or
                    (isinstance(node, ast.ImportFrom) and node.module == "__future__")):
                offset += 1
            else:
                break
        tree.body.insert(offset, ast.parse("import pytest").body[0])
    return checked(ast.unparse(tree))


def propose(source, target, analysis, strategy, suite, findings, config):
    expected = allowed_edit(suite["code"], target, findings)
    proposal = None
    reason = "按失败语句对应的文档契约重新生成测试"
    if suite["mode"] == "ai":
        try:
            proposal = generate_tests(source, target, analysis, strategy, feedback=findings,
                                      previous_code=suite["code"], config=config)
        except GenerationFailure as exc:
            proposal = exc.evidence
        if proposal["mode"] == "ai" and proposal.get("code"):
            if proposal["sha256"] == suite["sha256"]:
                return proposal, "模型重复返回原测试", None
            if proposal["code"] == expected:
                return proposal, "模型修正与失败节点的可核验改动一致", None
        reason = "模型候选未满足局部修正条件，依据文档契约重新生成失败语句"
    return {"code": expected, "mode": "rules", "sha256": digest(expected), "provider": "local-contract",
            "model": None, "attempts": [], "fallback_reason": reason}, reason, proposal
