def evaluate(left: int, operator: str, right: int) -> int:
    """Evaluate a restricted integer expression with one operator."""
    if operator == "+":
        return left + right
    if operator == "-":
        return right - left
    if operator == "*":
        return left * right
    raise ValueError("unknown operator")

def fold_expression(initial: int, steps: list[list]) -> int:
    """Apply operator and operand pairs from left to right."""
    for operator, operand in reversed(steps):
        initial = evaluate(initial, operator, operand)
    return initial
