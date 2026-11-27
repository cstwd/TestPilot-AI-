"""Design reproducible test inputs and make the strength of each oracle explicit."""
import ast

from .generation import SAMPLES


REVIEW = "预期业务结果待核对，请从规格或独立契约补充。"
EMPTY = {"list": "[]", "str": "''", "dict": "{}", "tuple": "()", "set": "set()", "bytes": "b''"}


def base_type(annotation):
    if not annotation:
        return ""
    return annotation.split("[", 1)[0].strip("'\"").removeprefix("typing.").lower()


def call_for(target, params, values):
    arguments = []
    for param in params:
        name = param["name"]
        if name not in values:
            continue
        value = values[name]
        arguments.append(value if param["kind"] == "positional_only" else f"{name}={value}")
    return f"{target}({', '.join(arguments)})"


def near_threshold(condition, defaults):
    """Infer neighbouring values for single integer comparisons in a condition."""
    if condition is None:
        return []
    try:
        expr = ast.parse(condition, mode="eval")
    except (ValueError, SyntaxError, RecursionError):
        return []
    values = []
    for part in ast.walk(expr):
        if not isinstance(part, ast.Compare) or len(part.ops) != 1:
            continue
        left, right = part.left, part.comparators[0]
        if not isinstance(left, ast.Name):
            left, right = right, left
        if not isinstance(left, ast.Name) or left.id not in defaults:
            continue
        try:
            boundary = ast.literal_eval(right)
        except (ValueError, SyntaxError):
            continue
        if type(boundary) is int and boundary.bit_length() <= 64:
            values.extend((left.id, str(boundary + delta)) for delta in (-1, 0, 1))
    return values[:12]


def build_strategy(analysis: dict, target: str) -> dict:
    if not analysis["valid"]:
        raise ValueError("请先修复源码的编译或编码错误。")
    matches = [s for s in analysis["symbols"] if s["name"] == target and s["testable"]]
    if len(matches) != 1:
        raise ValueError("请选择一个可独立测试的顶层同步函数。")
    fn = matches[0]
    params = [p for p in fn["parameters"] if not p["kind"].startswith("var_")]
    defaults = {}
    for p in params:
        typ = base_type(p["annotation"])
        sample = SAMPLES.get(typ)
        defaults[p["name"]] = repr(sample[0]) if sample else EMPTY.get(typ, "None")
    cases = []

    def add(kind, purpose, inputs, expected=REVIEW, oracle="review", **fields):
        cases.append({"id": f"case_{len(cases) + 1}", "type": kind, "purpose": purpose, "inputs": inputs,
                      "expected": expected, "oracle": oracle, **fields})

    def vary(p, value):
        return call_for(target, params, {**defaults, p["name"]: value})

    contracts = fn["examples"]
    for item in contracts:
        raises = item["exception"]
        add("exception" if raises else "example", "验证文档中此输入的明确预期。", [item["call"]],
            f"raises {raises}" if raises else item["expected"], "doctest", contract_id=item["id"])

    normal = call_for(target, params, defaults)
    add("normal", "以签名和类型标注选取常见输入。", [normal])
    if fn["returns"]:
        add("return_constraint", "核验声明的返回类型；检查调用是否满足业务前置条件。", [normal],
            fn["returns"], "annotation")
    required = [p["name"] for p in params if p["default"] is None]
    if not fn["decorators"] and not any(p["kind"] == "var_keyword" for p in fn["parameters"]):
        unknown = "_testpilot_unknown"
        while unknown in defaults:
            unknown += "_"
        add("exception", "添加签名不接受的关键字参数。", [normal[:-1] + (", " if params else "") + unknown + "=None)"],
            "raises TypeError", "signature")
    if required and not fn["decorators"]:
        add("missing", "省略必需参数，覆盖 Python 调用绑定检查。", [f"{target}()"], "raises TypeError", "signature")
    elif any(p["default"] is not None for p in params):
        required_values = {p["name"]: defaults[p["name"]] for p in params if p["name"] in required}
        add("missing", "省略有默认值的参数，验证默认行为。", [call_for(target, params, required_values)])

    # Multiple inputs of the same type are also varied independently.
    for p in params[:16]:
        name, typ = p["name"], base_type(p["annotation"])
        add("null", f"核验 {name} 为 None 时的行为。", [vary(p, "None")])
        if typ in EMPTY:
            add("empty", f"核验 {name} 长度为零时的行为。", [vary(p, EMPTY[typ])])
        if typ in SAMPLES:
            add("boundary", f"核验 {name} 的基础边界值。", [vary(p, repr(SAMPLES[typ][1]))])
        if typ:
            incompatible = "'invalid'" if typ != "str" else "1"
            add("invalid_type", f"传入与 {name} 的标注不同的值，核对类型约束及错误处理。",
                [vary(p, incompatible)])
        if typ in ("int", "float"):
            numbers = ["-1", "0", "1", "2**63"] if typ == "int" else ["-0.0", "float('inf')", "float('nan')"]
            add("special_numeric", f"检查 {name} 的特殊数值输入。", [vary(p, value) for value in numbers])

    for branch in fn["branches"][:32]:
        condition = branch["condition"]
        probes = near_threshold(condition, defaults)
        calls = [call_for(target, params, {**defaults, name: value}) for name, value in probes]
        add("branch", f"覆盖第 {branch['line']} 行的 {branch['kind']} 路径。", calls or [normal],
            condition=condition, line=branch["line"], needs_input_design=not bool(calls))
    for loop in fn["loops"][:16]:
        add("loop", f"覆盖第 {loop['line']} 行循环的零次、一次与多次迭代。", [normal],
            expression=loop["expression"], line=loop["line"], needs_input_design=True)
    for raised in fn["raises"][:16]:
        add("exception", f"核验第 {raised['line']} 行的异常路径及触发条件。", [normal],
            observed_exception=raised["name"], line=raised["line"], needs_input_design=True)

    return {"target": target, "source_sha256": analysis["sha256"], "cases": cases, "contracts": contracts}
