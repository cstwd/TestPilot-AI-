"""Generate additional tests from survivors with an installed, local Ollama model."""
import ast
import hashlib
import json
import keyword
import os
import operator
import time
from itertools import islice, product
from http.client import HTTPException
from urllib.error import HTTPError

from .local_ollama import choose_model as verified_model, local_base, request_json


PREFERRED_MODELS = ("qwen2.5-coder:0.5b", "testpilot-f13-local:latest")
EXCEPTIONS = {"ValueError", "TypeError", "ZeroDivisionError", "IndexError", "KeyError",
              "OverflowError", "RuntimeError", "ArithmeticError", "AssertionError"}


def predicate(node, values):
    """Interpret only comparisons of scalar input data, with no host execution of source."""
    if isinstance(node, ast.Name):
        return values[node.id]
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, bool, float, str)):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return not predicate(node.operand, values)
    if isinstance(node, ast.BoolOp):
        parts = [predicate(x, values) for x in node.values]
        return all(parts) if isinstance(node.op, ast.And) else any(parts)
    if isinstance(node, ast.Compare) and len(node.ops) == 1:
        ops = {ast.Lt: operator.lt, ast.LtE: operator.le, ast.Gt: operator.gt,
               ast.GtE: operator.ge, ast.Eq: operator.eq, ast.NotEq: operator.ne}
        return ops[type(node.ops[0])](predicate(node.left, values), predicate(node.comparators[0], values))
    raise ValueError("unknown predicate")


def input_hint(source, fn, site):
    """Suggest an input for simple numeric/boolean guards; infer no expected result."""
    edit = site.get("edit")
    if not edit or fn.args.posonlyargs or fn.args.kwonlyargs or len(fn.args.args) > 4:
        return ""
    original_conditions = [n for n in ast.walk(fn) if isinstance(n, ast.If)]
    guards = [n for n in original_conditions if n.lineno < site["line"] <= n.body[-1].end_lineno]
    focus = next((n for n in original_conditions if n.lineno == site["line"]), None)
    if not guards and not focus:
        return ""
    mutated = source[:edit["start"]] + edit["new"] + source[edit["end"]:]
    alternate = next((n for n in ast.walk(ast.parse(mutated)) if isinstance(n, ast.If)
                      and n.lineno == site["line"]), None)
    pool = [0, 1, -1]
    for cond in original_conditions:
        for value in ast.walk(cond.test):
            if isinstance(value, ast.Constant) and type(value.value) is int and value.value.bit_length() <= 32:
                pool.extend([value.value, value.value - 1, value.value + 1])
    choices = []
    for arg in fn.args.args:
        annotation = ast.unparse(arg.annotation) if arg.annotation else ""
        if annotation not in {"int", "bool"}:
            return ""
        choices.append([True, False] if annotation == "bool" else list(dict.fromkeys(pool)))
    for args in islice(product(*choices), 128):
        values = dict(zip((a.arg for a in fn.args.args), args))
        try:
            if not all(predicate(g.test, values) for g in guards):
                continue
            if focus and (not alternate or predicate(focus.test, values) == predicate(alternate.test, values)):
                continue
        except (TypeError, KeyError, ValueError):
            return ""
        return fn.name + "(" + ", ".join(map(repr, args)) + ")"
    return ""


def prompt_for(source, target, previous_code, site):
    """Summarize what the old suite checks; avoid confusing its import alias with the API."""
    fn = next((n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == target), None)
    if fn is None:
        raise ValueError("源码中未找到目标顶层函数")
    contract = (ast.get_docstring(fn) or "").split(">>>")[0].strip()
    body = fn.body[1:] if ast.get_docstring(fn) is not None else fn.body
    original = "\n".join(ast.unparse(n) for n in body)
    tree = ast.parse(previous_code)
    old_cases = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    type_only = sum(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "isinstance"
                        for n in ast.walk(f)) for f in old_cases)
    hint = input_hint(source, fn, site)
    question = (f"Evaluate this suggested input on the ORIGINAL: {hint}. Use this exact call if appropriate."
                if hint else f"Choose one distinguishing call to {target}; evaluate the original result.")
    return (f"Python {target}({ast.unparse(fn.args)}). {contract or original}\n"
            f"Existing suite: {len(old_cases)} tests, {type_only} with type checks. "
            f"Line {site['line']}: {site['before']} changed to {site['after']}.\n"
            f"{question} Return only one JSON object with call (Python expression), expected (JSON value, "
            "or string 'raises ValueError' for an exception, use its actual name), and reason (short).")


def choose_model(base, requested):
    return verified_model(base, requested, preferred=PREFERRED_MODELS, query=request_json)


def additions(raw, target, survivors, previous_code):
    if not target.isidentifier() or keyword.iskeyword(target):
        raise ValueError("需要可调用的顶层函数名")
    cases = json.loads(raw)["cases"]
    if not isinstance(cases, list) or not 1 <= len(cases) <= len(survivors):
        raise ValueError("模型补测数量与存活位置清单不匹配")
    names = {n.name for n in ast.parse(previous_code).body if isinstance(n, (ast.ClassDef, ast.FunctionDef))}
    blocks, accepted = [], []
    for case in cases:
        site = case["site"]
        if type(site) is not int or not 1 <= site <= len(survivors) or not case["reason"].strip():
            raise ValueError("用例缺少有效的存活变异索引或说明")
        call = ast.parse(case["call"].strip(), mode="eval").body
        if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name) or call.func.id != target:
            raise ValueError("用例必须直接调用选定目标")
        if any(kw.arg is None for kw in call.keywords):
            raise ValueError("用例不能展开关键字参数")
        for arg in [*call.args, *(kw.value for kw in call.keywords)]:
            ast.literal_eval(arg)
        imported = target
        if target in EXCEPTIONS or target == "pytest":
            imported = target + " as _testpilot_subject_function"
            call.func.id = "_testpilot_subject_function"
        expr = ast.unparse(call)
        expected = case["expected"].strip()
        imports = [f"    from subject import {imported}"]
        if expected.startswith("raises "):
            exc = expected[len("raises "):]
            if exc not in EXCEPTIONS:
                raise ValueError("用例预期异常不在支持范围内")
            imports.append("    import pytest")
            assertion = f"    with pytest.raises({exc}):\n        {expr}"
        else:
            truth = ast.parse(expected, mode="eval").body
            ast.literal_eval(truth)
            assertion = f"    assert {expr} == {ast.unparse(truth)}"
        name = "test_mutation_" + hashlib.sha256(assertion.encode()).hexdigest()[:16]
        if name in names:
            continue
        names.add(name)
        blocks.append("\n".join([f"def {name}():", *imports, assertion]))
        accepted.append({**case, "mutant_id": survivors[site - 1]["id"], "test_name": name})
    if not blocks:
        raise ValueError("模型重复生成已有补测")
    added = "\n\n".join(blocks) + "\n"
    # Preserve every byte of the baseline suite, including imports and test conditions.
    code = previous_code + "\n\n" + added
    compile(code, "test_generated.py", "exec", dont_inherit=True)
    return code, added, accepted


def supplement(source, target, previous_code, survivors, *, config=None, should_cancel=None):
    cfg = config if config is not None else {
        key: os.getenv("TESTPILOT_MUTATION_" + key.upper()) for key in ("model", "base_url", "timeout")}
    result = dict(status="unavailable", mode=None, provider="ollama", model=None, reason="",
                  code=None, added_code=None, cases=[], attempts=[])
    if not survivors:
        return {**result, "status": "not_needed", "reason": "所有变异均已处理，没有存活变异"}
    if should_cancel and should_cancel():
        return {**result, "status": "cancelled", "reason": "生成前已收到终止请求",
                "pending_ids": [m["id"] for m in survivors]}
    try:
        base = local_base(cfg.get("base_url") or "http://127.0.0.1:11434")
        result.update(endpoint=base, requested_model=cfg.get("model") or None)
        timeout = int(cfg.get("timeout") or 120)
        if not 1 <= timeout <= 180:
            raise ValueError("模型超时须在 1 至 180 秒之间")
        model, digest = choose_model(base, cfg.get("model") or "")
        result.update(model=model, model_digest=digest)
        evidence = []
        deadline = time.monotonic() + timeout
        for index, site in enumerate(survivors):
            if should_cancel and should_cancel():
                return {**result, "status": "cancelled", "reason": "后续本地模型调用已终止",
                        "pending_ids": [m["id"] for m in survivors[index:]]}
            user = prompt_for(source, target, previous_code, site)
            if len(user.encode("utf8")) > 12000:
                raise ValueError("完整模型上下文超过本机输入预算 12000 字节")
            messages = [{"role": "user", "content": user}]
            time_left = deadline - time.monotonic()
            if time_left <= 0:
                result["pending_ids"] = [m["id"] for m in survivors[index:]]
                break
            options = {"temperature": 0, "seed": 23, "num_predict": 160, "num_ctx": 4096,
                       "num_batch": 128}
            if model == "qwen2.5-coder:0.5b":
                options["num_gpu"] = 0
            attempt = {"number": index + 1, "messages": messages, "options": options,
                       "mutant_ids": [survivors[index]["id"]], "focus_id": survivors[index]["id"]}
            result["attempts"].append(attempt)
            payload = {"model": model, "messages": messages, "format": "json", "stream": False,
                       "keep_alive": "30s", "options": options}
            start = time.monotonic()
            response = request_json(base, "/api/chat", payload, time_left)
            raw = response["message"]["content"]
            attempt.update(raw=raw, elapsed_ms=round(1000 * (time.monotonic() - start)),
                           response_model=response.get("model"), prompt_eval_count=response.get("prompt_eval_count"),
                           eval_count=response.get("eval_count"), done_reason=response.get("done_reason"))
            try:
                if not response.get("done") or response.get("done_reason") == "length":
                    raise ValueError("模型输出未完整结束")
                candidate = json.loads(raw)
                expected = candidate["expected"]
                expected_expr = expected if isinstance(expected, str) and expected.startswith("raises ") else repr(expected)
                case = {"site": index + 1, "reason": candidate["reason"], "call": candidate["call"],
                        "expected": expected_expr}
                additions(json.dumps({"cases": [case]}), target, survivors, previous_code)
                evidence.append(case)
                attempt["status"] = "accepted"
            except (ValueError, SyntaxError, RecursionError, TypeError, AttributeError, KeyError) as exc:
                attempt.update(status="rejected", reason=f"模型候选无效：{str(exc)[:250]}")
        if evidence:
            code, added, cases = additions(json.dumps({"cases": evidence}), target, survivors, previous_code)
            return {**result, "status": "generated", "mode": "ai", "code": code, "added_code": added,
                    "cases": cases, "reason": "本机模型提出补测输入及预期；效果由隔离重跑判定"}
        result.update(status="rejected", reason="本次模型输出未产生可执行补测，详见逐位置尝试")
    except (OSError, HTTPException, ValueError, KeyError, TypeError) as exc:
        result["reason"] = f"本地模型不可用：{str(exc)[:300]}"
        if result["attempts"] and "status" not in result["attempts"][-1]:
            result["attempts"][-1].update(status="unavailable", reason=result["reason"])
    return result
