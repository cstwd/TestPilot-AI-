"""Plan one first-order mutation per supported operator occurrence on an immutable revision."""
import ast
import re
from functools import lru_cache
from hashlib import sha256
from itertools import accumulate
from uuid import NAMESPACE_URL, uuid5

from cosmic_ray.ast import ast_nodes, get_ast
from cosmic_ray.mutating import mutate_code
from cosmic_ray.plugins import get_operator


PROFILE = "cosmic-ray-8.9.0/testpilot-first-order-v1"
MAX_SITES = 128
CORE = {
    **{"core/ReplaceBinaryOperator_" + pair: "arithmetic" for pair in
       ("Add_Sub", "Sub_Add", "Mul_Add", "Div_Mul", "FloorDiv_Mul", "Mod_Mul", "Pow_Mul")},
    **{"core/ReplaceComparisonOperator_" + pair: "comparison" for pair in
       ("Lt_LtE", "LtE_Lt", "Gt_GtE", "GtE_Gt", "Eq_NotEq", "NotEq_Eq", "Is_IsNot", "IsNot_Is")},
    "core/ReplaceAndWithOr": "boolean", "core/ReplaceOrWithAnd": "boolean",
}


def digest(text):
    return sha256(text.encode("utf-8")).hexdigest()


@lru_cache(maxsize=1)
def operators():
    return [(name, family, get_operator(name)()) for name, family in CORE.items()]


def apply_site(source, site):
    edit = site["edit"]
    start, end = edit["start"], edit["end"]
    if source[start:end] != edit["old"]:
        raise ValueError("变异位置与源文件不匹配")
    changed = source[:start] + edit["new"] + source[end:]
    if digest(changed) != site["mutated_sha256"]:
        raise ValueError("变异副本摘要校验失败")
    return changed


def make_plan(source, target):
    tree = ast.parse(source)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == target]
    if len(functions) != 1:
        raise ValueError("请选择可唯一定位的顶层同步函数")
    fn = functions[0]
    # AST and Parso count only Python physical newlines, not Unicode line separators.
    lines = re.findall(r"[^\r\n]*(?:\r\n|\r|\n|$)", source)
    starts = [0, *accumulate(len(line) for line in lines)]
    identity = digest(source)
    plan = []

    def offset(line, byte_col):
        return starts[line - 1] + len(lines[line - 1].encode("utf-8")[:byte_col].decode("utf-8"))

    body_start = offset(fn.body[0].lineno, fn.body[0].col_offset)
    body_end = offset(fn.end_lineno, fn.end_col_offset)

    def add(family, operator, line, column, start, end, new, *, before=None, after=None, candidate=False):
        if len(plan) >= MAX_SITES:
            raise ValueError(f"固定算子清单超过 {MAX_SITES} 个位置，本次整体拒绝且不计分")
        old = source[start:end]
        changed = source[:start] + new + source[end:]
        key = str(uuid5(NAMESPACE_URL, f"{PROFILE}/{identity}/{target}/{operator}/{line}/{column}"))
        plan.append({"id": key, "family": family, "operator": operator, "line": line, "column": column,
                     "before": old if before is None else before, "after": new if after is None else after,
                     "edit": {"start": start, "end": end, "old": old, "new": new},
                     "mutated_sha256": digest(changed), "equivalent_candidate": candidate})

    cst = get_ast(source)
    nodes = list(ast_nodes(cst))
    if any(n.type in ("error_node", "error_leaf") for n in nodes):
        raise ValueError("当前 Cosmic Ray 解析器不支持此文件的语法，本次整体不计分")
    for name, family, operator in operators():
        occurrence = 0
        for node in nodes:
            for (line, col), (last_line, last_col) in operator.mutation_positions(node):
                start, end = starts[line-1] + col, starts[last_line-1] + last_col
                index = occurrence
                occurrence += 1
                if not body_start <= start < end <= body_end:
                    continue
                mutated = mutate_code(source, operator, index)
                if not mutated or mutated == source:
                    raise ValueError(f"算子未生成可验证的变异 {name} L{line}")
                # Cosmic Ray can normalize whitespace adjacent to a comparison.
                # Capture its exact edit, including that whitespace, for byte-for-byte replay.
                left, right_old, right_new = 0, len(source), len(mutated)
                while left < min(right_old, right_new) and source[left] == mutated[left]:
                    left += 1
                while right_old > left and right_new > left and source[right_old-1] == mutated[right_new-1]:
                    right_old -= 1
                    right_new -= 1
                if (name == "core/ReplaceComparisonOperator_Is_IsNot" and left > end
                        and mutated == source[:end] + " not" + source[end:]):
                    # The first space and even the start of the next name can match.
                    left, right_old, right_new = end, end, end + len(" not")
                if left > end or right_old < start:
                    raise ValueError("Cosmic Ray 的变异位置与清单不一致")
                add(family, name, line, col+1, left, right_old, mutated[left:right_new],
                    before=source[start:end], after=mutated[min(start,left):max(right_new,end+len(mutated)-len(source))].strip())

    for stmt in fn.body:
        for node in ast.walk(stmt):
            if isinstance(node, (ast.If, ast.While, ast.IfExp)):
                expr = node.test
                start, end = offset(expr.lineno, expr.col_offset), offset(expr.end_lineno, expr.end_col_offset)
                family, name, new, candidate = "condition", "testpilot/NegateCondition", "not ("+source[start:end]+")", False
                node = expr
            elif isinstance(node, ast.Return):
                start, end = offset(node.lineno, node.col_offset), offset(node.end_lineno, node.end_col_offset)
                candidate = node.value is None or isinstance(node.value, ast.Constant) and node.value.value is None
                family, name = "return", "testpilot/ReturnNone"
                new = "return" if node.value is not None and candidate else "return None"
            elif isinstance(node, ast.Raise):
                start, end = offset(node.lineno, node.col_offset), offset(node.end_lineno, node.end_col_offset)
                family, name, new, candidate = "exception", "testpilot/SuppressRaise", "pass", False
            else:
                continue
            add(family, name, node.lineno, start-starts[node.lineno-1]+1, start, end, new, candidate=candidate)
    plan.sort(key=lambda s: (s["line"], s["column"], s["operator"]))
    return plan
