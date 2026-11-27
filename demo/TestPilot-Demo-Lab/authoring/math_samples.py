
from spec import E, group

m = group("math")

m("g", "calculator", '''
def add(a: int, b: int) -> int:
    """Add two signed integers."""
    return a + b

def quotient(a: int, b: int) -> int:
    """Return the floor quotient."""
    return a // b
''', [
 ("add(4, 6)", 10, "normal"), ("add(-4, 4)", 0, "boundary"),
 ("quotient(-3, 2)", -2, "special"), ("quotient(1, 0)", E("ZeroDivisionError"), "exception")])

m("g", "prime_checker", '''
def is_prime(n: int) -> bool:
    """Check primality for a signed integer."""
    if n < 2:
        return False
    from math import isqrt

    return all(n % d != 0 for d in range(2, isqrt(n) + 1))

def primes_through(n: int) -> list[int]:
    """Return primes at or below n."""
    return [k for k in range(2, n + 1) if is_prime(k)]
''', [("is_prime(2)", True, "boundary"), ("is_prime(49)", False, "special"),
 ("primes_through(7)", [2, 3, 5, 7], "normal"), ("is_prime(None)", E("TypeError"), "exception")])

m("g", "percentage_calculator", '''
def percent_of(part: int, base: int) -> float:
    """Express part as a percentage of the nonzero base."""
    return part * 100 / base

def basis_points(rate: float) -> int:
    """Round a fractional rate to its nearest basis point."""
    return round(rate * 10000)
''', [("percent_of(3, 4)", 75.0, "normal"), ("percent_of(0, 10)", 0., "boundary"),
 ("basis_points(-0.125)", -1250, "special"), ("percent_of(1, 0)", E("ZeroDivisionError"), "exception")])

m("g", "geometry_calculator", '''
def area(width: int, height: int) -> int:
    """Calculate the area of a rectangle with nonnegative dimensions."""
    if min(width, height) < 0:
        raise ValueError("negative dimension")
    return width * height

def perimeter(width: int, height: int) -> int:
    """Calculate perimeter using the same dimension contract."""
    area(width, height)
    return 2 * (width + height)
''', [("area(3, 4)", 12, "normal"), ("area(0, 5)", 0, "boundary"),
 ("perimeter(2, 5)", 14, "normal"), ("area(-1, 5)", E("ValueError"), "exception")])

m("g", "significant_digits", '''
def round_significant(value: float, digits: int) -> float:
    """Round a finite number to the requested positive significant digits."""
    import math

    if digits < 1:
        raise ValueError("digits must be positive")
    if not value:
        return 0.0
    return round(value, digits - 1 - math.floor(math.log10(abs(value))))

def approximation_error(value: float, digits: int) -> float:
    """Return the absolute residual after rounding."""
    return abs(value - round_significant(value, digits))
''', [("round_significant(12340, 2)", 12000, "normal"), ("round_significant(0, 1)", 0., "boundary"),
 ("approximation_error(-1250, 2)", 50, "special"), ("round_significant(4, 0)", E("ValueError"), "exception")])

m("b", "scientific_calculator", '''
def slope(y0: float, y1: float, x0: float, x1: float) -> float:
    """Return signed rise over signed run."""
    return (y1 - y0) / (x1 - x0)

def interpolate(a: float, b: float, fraction: float) -> float:
    """Interpolate linearly between a and b."""
    return a + (b - a) * fraction
''', [("slope(2, 8, 1, 4)", 2., "normal", (1.2, "x1 - x0", "x1 + x0", "denominator")),
 ("interpolate(10, 30, 0.25)", 15., "boundary", (17.5, "(b - a) * fraction", "b * fraction", "weighting")),
 ("slope(0, 3, 0, 3)", 1., "normal"), ("slope(0, 4, 0, 0)", E("ZeroDivisionError"), "exception")])

m("b", "statistics_tool", '''
def trimmed_mean(values: list[int], trim: int) -> float:
    """Drop trim items at both ends of the sorted input before averaging."""
    kept = sorted(values)[trim:len(values) - trim]
    return sum(kept) / len(kept)

def population_variance(values: list[int]) -> float:
    """Return population variance, dividing by the population size."""
    center = sum(values) / len(values)
    return sum((x - center) ** 2 for x in values) / len(values)
''', [("trimmed_mean([0, 3, 9, 40], 1)", 6., "boundary", (3., "len(values) - trim]", "len(values) - trim - 1]", "slice")),
 ("population_variance([2, 4])", 1., "special", (2., "for x in values) / len(values)", "for x in values) / (len(values) - 1)", "normalization")),
 ("trimmed_mean([4, 4, 4], 0)", 4., "normal"), ("trimmed_mean([], 0)", E("ZeroDivisionError"), "exception")])

m("b", "matrix_operations", '''
def diagonal_sum(matrix: list[list[int]]) -> int:
    """Sum the main diagonal of a square matrix."""
    return sum(row[i] for i, row in enumerate(matrix))

def multiply_vector(matrix: list[list[int]], vector: list[int]) -> list[int]:
    """Multiply a matrix by a column vector of matching width."""
    return [sum(a * b for a, b in zip(row, vector, strict=True)) for row in matrix]
''', [("diagonal_sum([[6, 1], [4, 9]])", 15, "normal", (5, "row[i]", "row[-i-1]", "axis")),
 ("multiply_vector([[2, 3]], [5, 8])", [34], "normal", ([31], "zip(row, vector, strict=True)", "zip(row, reversed(vector), strict=True)", "index_order")),
 ("diagonal_sum([])", 0, "boundary"), ("multiply_vector([[1]], [])", E("ValueError"), "exception")])

m("b", "number_converter", '''
def decode_word(raw: int, bits: int) -> int:
    """Interpret an unsigned word as signed two's complement."""
    if not 0 <= raw < 1 << bits:
        raise ValueError("word out of range")
    return raw - (1 << bits) if raw >= 1 << (bits - 1) else raw

def encode_word(value: int, bits: int) -> int:
    """Encode a signed integer as an unsigned word of fixed width."""
    bound = 1 << (bits - 1)
    if not -bound <= value < bound:
        raise ValueError("signed value out of range")
    return value % (2 * bound)
''', [("decode_word(128, 8)", -128, "boundary", (128, "raw >= 1 << (bits - 1)", "raw > 1 << (bits - 1)", "sign_bit")),
 ("encode_word(128, 8)", E("ValueError"), "exception", (128, "value < bound", "value <= bound", "range")),
 ("encode_word(-1, 8)", 255, "special"), ("decode_word(12, 8)", 12, "normal")])

m("b", "financial_rounding", '''
from decimal import Decimal, ROUND_HALF_UP

def cents(amount: str) -> int:
    """Round a decimal amount to cents with ties away from zero."""
    return int(Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) * 100)

def cash_round(value: int) -> int:
    """Round nonnegative cents to the nearest five cents."""
    return ((value + 2) // 5) * 5
''', [("cents('1.005')", 101, "special", (100, ", rounding=ROUND_HALF_UP", "", "rounding_mode")),
 ("cash_round(8)", 10, "boundary", (5, "value + 2", "value + 1", "rounding_threshold")),
 ("cash_round(10)", 10, "normal"), ("cents(None)", E("TypeError"), "exception")])

m("b", "expression_evaluator", '''
def evaluate(left: int, operator: str, right: int) -> int:
    """Evaluate a restricted integer expression with one operator."""
    if operator == "+":
        return left + right
    if operator == "-":
        return left - right
    if operator == "*":
        return left * right
    raise ValueError("unknown operator")

def fold_expression(initial: int, steps: list[list]) -> int:
    """Apply operator and operand pairs from left to right."""
    for operator, operand in steps:
        initial = evaluate(initial, operator, operand)
    return initial
''', [("evaluate(7, '-', 3)", 4, "normal", (-4, "left - right", "right - left", "operand_order")),
 ("fold_expression(2, [['+', 3], ['*', 4]])", 20, "combination", (11, "in steps:", "in reversed(steps):", "evaluation_order")),
 ("fold_expression(5, [])", 5, "boundary"), ("evaluate(1, '/', 2)", E("ValueError"), "exception")])

m("b", "histogram_binning", '''
def bin_number(value: int, width: int) -> int:
    """Map a value to the floor bin, with negative bins below zero."""
    if width <= 0:
        raise ValueError("nonpositive bin width")
    return value // width

def frequency(values: list[int], width: int) -> dict[int, int]:
    """Count observations in each integer bin."""
    counts = {}
    for value in values:
        key = bin_number(value, width)
        counts[key] = counts.get(key, 0) + 1
    return counts
''', [("bin_number(-1, 5)", -1, "boundary", (0, "value // width", "int(value / width)", "negative_rounding")),
 ("frequency([0, 1, 5], 5)", {0: 2, 1: 1}, "normal", ({0: 1, 1: 1}, "counts.get(key, 0) + 1", "1", "accumulator")),
 ("frequency([], 1)", {}, "boundary"), ("bin_number(0, 0)", E("ValueError"), "exception")])

m("b", "unit_scaling", '''
def metric_kilometers(meters: int) -> float:
    """Convert meters to kilometers, retaining fractional kilometers."""
    return meters / 1000

def fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return celsius * 9 / 5 + 32
''', [("metric_kilometers(250)", 0.25, "boundary", (0, "meters / 1000", "meters // 1000", "precision")),
 ("fahrenheit(0)", 32., "special", (0., " / 5 + 32", " / 5", "offset")),
 ("metric_kilometers(2000)", 2., "normal"), ("fahrenheit(None)", E("TypeError"), "exception")])
