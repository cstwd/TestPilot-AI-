"""Attribute observed pytest failures using traceback positions and explicit source contracts."""
import ast
import builtins
import inspect


def literal(node):
    # Use representations to keep booleans and integers distinct when binding inputs.
    return repr(ast.literal_eval(node))


def signature(params):
    items = []
    for param in params:
        default = inspect.Parameter.empty
        if param["default"] is not None:
            try:
                default = literal(param["default"])
            except (ValueError, TypeError, SyntaxError):
                default = object()
        items.append(inspect.Parameter(param["name"], getattr(inspect.Parameter, param["kind"].upper()),
                                       default=default))
    return inspect.Signature(items)


def argument_key(call, sig):
    if not isinstance(call, ast.Call) or any(kw.arg is None for kw in call.keywords):
        return None
    try:
        bound = sig.bind(*(literal(v) for v in call.args), **{kw.arg: literal(kw.value) for kw in call.keywords})
        bound.apply_defaults()
        return repr(bound.arguments)
    except (ValueError, TypeError, RecursionError, OverflowError):
        return None


def imports(tree, target):
    names = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "subject" and not node.level:
            names.update(a.asname or a.name for a in node.names if a.name == target)
        elif isinstance(node, ast.Import):
            names.update(f"{a.asname or a.name}.{target}" for a in node.names if a.name == "subject")
    return names


def tested_expression(tree, frame, target, names):
    """Recognize direct assertions on a subject import at the observed traceback line."""
    tests = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == frame["function"]]
    if len(tests) != 1:
        return None
    fn = tests[0]
    if fn.decorator_list or any(not isinstance(n, (ast.Assert, ast.With, ast.Expr)) for n in fn.body):
        return None
    shadowed = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
    shadowed.update(p.arg for p in ast.walk(fn.args) if isinstance(p, ast.arg))
    shadowed.update(n.id for top in tree.body if isinstance(top, (ast.Assign, ast.AnnAssign))
                    for n in ast.walk(top) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store))
    names = {name for name in names if name.split(".")[0] not in shadowed}
    for stmt in fn.body:
        if not stmt.lineno <= frame["line"] <= stmt.end_lineno:
            continue
        call = None
        if isinstance(stmt, ast.Assert):
            expr = stmt.test
            if isinstance(expr, ast.Compare) and len(expr.ops) == 1 and isinstance(expr.ops[0], ast.Eq):
                a, b = expr.left, expr.comparators[0]
                call, rhs = (a, b) if isinstance(a, ast.Call) else (b, a)
                try:
                    kind, expected = "equals", literal(rhs)
                except (ValueError, TypeError, RecursionError, OverflowError):
                    continue
            elif (isinstance(expr, ast.Call) and ast.unparse(expr.func) == "isinstance" and "isinstance" not in shadowed
                  and len(expr.args) == 2 and isinstance(expr.args[1], ast.Name)):
                call, kind, expected = expr.args[0], "type", expr.args[1].id
        elif isinstance(stmt, ast.With) and len(stmt.items) == len(stmt.body) == 1:
            context = stmt.items[0].context_expr
            if (isinstance(context, ast.Call) and ast.unparse(context.func) == "pytest.raises"
                    and len(context.args) == 1 and isinstance(context.args[0], ast.Name)
                    and not context.keywords and isinstance(stmt.body[0], ast.Expr)):
                call, kind, expected = stmt.body[0].value, "raises", context.args[0].id
        if isinstance(call, ast.Call) and ast.unparse(call.func) in names:
            return call, kind, expected
    return None


def catches(expected, observed):
    kind, actual = vars(builtins).get(expected), vars(builtins).get(observed)
    return expected == observed or (isinstance(kind, type) and isinstance(actual, type) and issubclass(actual, kind))


def contract_verdict(kind, expected, contract, finding, subject_frame):
    exc = finding["exception_type"]
    documented = contract["exception"]
    if documented:
        if kind != "raises" or not catches(expected, documented):
            return "test_error", "该输入的文档契约要求抛出异常，生成测试的预期与契约冲突。"
        no_raise = exc == "Failed" and "DID NOT RAISE" in finding["message"]
        if no_raise or (subject_frame and not catches(documented, exc)):
            return "program_defect", "同一输入违反了文档指定的异常契约。"
    else:
        if kind == "raises" or (kind == "equals" and expected != contract["expected"]
                                and ast.literal_eval(expected) != ast.literal_eval(contract["expected"])):
            return "test_error", "生成测试的预期与该输入的文档返回值冲突。"
        if subject_frame:
            return "program_defect", "文档要求返回明确值，实测目标代码在该输入上抛出异常。"
        if exc == "AssertionError" and kind == "equals":
            return "program_defect", "实际执行未满足与文档示例一致的返回值断言。"
        if exc == "AssertionError" and kind == "type":
            cls = vars(builtins).get(expected)
            if isinstance(cls, type):
                if not isinstance(ast.literal_eval(contract["expected"]), cls):
                    return "test_error", "类型断言与文档中该输入的返回值类型冲突。"
                return "program_defect", "实际返回类型与文档示例不兼容。"
    return "undetermined", "已定位相关契约，本次失败证据不足以确定归属。"


def analyze_failures(execution, strategy, generated_code, analysis):
    target = strategy["target"]
    symbol = next((s for s in analysis["symbols"] if s["name"] == target and s["testable"]), None)
    try:
        tree = ast.parse(generated_code)
    except (SyntaxError, ValueError, RecursionError):
        tree = ast.Module(body=[], type_ignores=[])
    names = imports(tree, target)
    sig = signature(symbol["parameters"]) if symbol else inspect.Signature()
    contracts = {}
    for contract in strategy["contracts"]:
        key = argument_key(ast.parse(contract["call"], mode="eval").body, sig)
        if key is not None:
            contracts.setdefault(key, []).append(contract)
    details = {f["nodeid"]: f for f in execution.get("failures", [])}
    findings = []
    for case in execution["cases"]:
        if case["outcome"] == "passed":
            continue
        detail = details.get(case["nodeid"], {})
        frames = detail.get("frames", [])
        test = next((f for f in reversed(frames) if f["path"] == "test_generated.py"), None)
        subject = next((f for f in reversed(frames) if f["path"] == "subject.py"), None)
        exc = detail.get("exception_type")
        item = {**case, "phase": detail.get("phase"), "exception_type": exc, "message": detail.get("message", ""),
                "frames": frames, "assertion_diff": detail.get("assertion_diff"), "contract": None,
                "location": subject or test, "test_line": test["line"] if test else None}
        category, reason = "undetermined", "缺少可与失败语句核对的独立契约，请人工核实。"
        if case["outcome"] == "skipped":
            category, reason = "skipped", "Pytest 记录为跳过。"
        elif exc == "ModuleNotFoundError" and not subject:
            category, reason = "environment", "来宾无法加载测试引用的模块，请核实依赖名称及环境。"
        elif test and not subject and exc in {"NameError", "UnboundLocalError", "SyntaxError"}:
            category, reason = "test_error", "生成测试在自身代码位置触发了名称或语法错误。"
        elif test and not subject and exc == "ImportError" and "from 'subject'" in item["message"]:
            category, reason = "test_error", "测试导入了目标模块未提供的名称。"
        elif test and symbol and detail.get("phase") == "call":
            observed = tested_expression(tree, test, target, names)
            if observed:
                call, kind, expected = observed
                candidates = contracts.get(argument_key(call, sig), [])
                if candidates and len({(c["expected"], c["exception"]) for c in candidates}) == 1:
                    item["contract"] = candidates[0]
                    category, reason = contract_verdict(kind, expected, candidates[0], item, subject)
        if category == "test_error":
            item["location"] = test
        elif category == "program_defect" and not subject:
            item["location"] = {"path": "subject.py", "function": target, "line": symbol["line"], "precision": "entry"}
        findings.append({**item, "category": category, "reason": reason})
    if execution["status"] == "timeout" or (not execution.get("result_complete", True) and not findings):
        findings.append({"nodeid": None, "outcome": execution["status"], "phase": "execution", "category": "environment",
                         "reason": "执行时限已到。" if execution["status"] == "timeout" else "执行器未取得完整结果。",
                         "message": execution.get("diagnostic", ""), "location": None, "test_line": None,
                         "exception_type": None, "assertion_diff": None, "frames": [], "contract": None})
    return {"status": execution["status"], "findings": findings}
