
"""Materialize the frozen sources, public index and hidden assertions."""
import ast
from collections import Counter
import hashlib
import importlib
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "authoring"))
from spec import E, MODULES  # noqa: E402

DOMAINS = ("math_samples", "people", "commerce", "data", "algorithms", "time_rules",
           "challenge_a", "challenge_b")
MUTATION_EXAMPLES = {
    "calculator": ("add(2, 3)", 5),
    "prime_checker": ("is_prime(11)", True),
    "percentage_calculator": ("basis_points(0.125)", 1250),
    "geometry_calculator": ("area(2, 6)", 12),
    "role_manager": ("active_labels({'B': False, 'A': True})", ["A"]),
    "account_lock": ("remaining_wait(20, 21)", 1),
    "record_projection": ("complete({'x': 0}, ['x', 'y'])", False),
    "inventory_manager": ("available(5, 1)", 4),
    "shipping_calculator": ("shipping_fee(1000, True)", 700),
    "stack": ("push([1], 3)", [1, 3]),
    "interval_overlap": ("overlaps(1, 3, 2, 4)", True),
    "date_calculator": ("leap(2024)", True),
    "booking_validator": ("valid_slot(0, 6, 6)", True),
    "timezone_converter": ("local_minute(1435, 30)", 25),
    "text_analyzer": ("word_count('alpha  beta')", 2),
}
BLIND_NAMES = {"calculator", "scientific_calculator", "user_validator", "team_roster",
               "shipping_calculator", "volume_discount", "csv_processor", "log_parser",
               "binary_search", "booking_timezones"}
# Keep published examples usable when a campaign rotates to another target.
EARLIER_EXAMPLES = {
    "percentage_calculator": ("percent_of(1, 5)", 20.0),
    "significant_digits": ("round_significant(18, 1)", 20),
    "shopping_cart": ("cart_total([[300, 3]])", 900),
    "retry_policy": ("retry_delay(2, 2, 10)", 4),
}


def digest(source):
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def json_file(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                    encoding="utf-8", newline="\n")


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = value.encode("utf-8")
    if not path.exists() or path.read_bytes() != data:
        path.write_bytes(data)


def replace_once(source, previous, current):
    if source.count(previous) != 1:
        raise ValueError(f"Expected exactly one occurrence of {previous!r}")
    return source.replace(previous, current, 1)


def add_example(source, call, expected):
    node = ast.parse(source).body
    function = next(n for n in node if isinstance(n, ast.FunctionDef) and n.name == target(call))
    lines = source.splitlines(keepends=True)
    doc = function.body[0]
    old = lines[doc.lineno - 1]
    assert old.strip().endswith('"""')
    lines[doc.lineno - 1] = old.rstrip()[:-3] + f'\n\n    >>> {call}\n    {expected!r}\n    """\n'
    return "".join(lines)


def target(call):
    expr = ast.parse(call, mode="eval").body
    if not isinstance(expr, ast.Call) or not isinstance(expr.func, ast.Name):
        raise ValueError(f"Invalid call {call!r}")
    for arg in [*expr.args, *(keyword.value for keyword in expr.keywords)]:
        ast.literal_eval(arg)
    if any(keyword.arg is None for keyword in expr.keywords):
        raise ValueError("Keyword unpacking is unsupported")
    return expr.func.id


def outcome(value):
    return {"exception": value.type_name} if isinstance(value, E) else {"value": repr(value)}


def main():
    for module in DOMAINS:
        importlib.import_module(module)
    public, truth = [], []
    names = set()
    for tier, domain, name, corrected, scenarios in sorted(MODULES, key=lambda spec: spec[2]):
        if name in names or not re.fullmatch(r"[a-z][a-z0-9_]+", name):
            raise ValueError(f"Invalid or duplicate name: {name}")
        names.add(name)
        if name in EARLIER_EXAMPLES:
            corrected = add_example(corrected, *EARLIER_EXAMPLES[name])
        if name in MUTATION_EXAMPLES:
            corrected = add_example(corrected, *MUTATION_EXAMPLES[name])
        source = corrected
        cases, defects = [], []
        for ordinal, (call, expected, category, *defect) in enumerate(scenarios, 1):
            identifier = f"{name}_{ordinal:02}"
            case = {"id": identifier, "call": call, "target": target(call),
                    "category": category, "expected": outcome(expected)}
            if defect:
                actual, before, after, kind = defect[0]
                source = replace_once(source, before, after)
                defect_id = f"DL-{name}-{ordinal:02}"
                case["defect"] = defect_id
                defects.append({"id": defect_id, "case_id": identifier, "category": kind,
                                "trigger": call, "expected": outcome(expected), "actual": outcome(actual),
                                "repair": {"find": before, "replace": after}})
            cases.append(case)
        functions = [node.name for node in ast.parse(source, feature_version=(3, 10)).body
                     if isinstance(node, ast.FunctionDef)]
        if len(functions) < 2 or any(case["target"] not in functions for case in cases):
            raise ValueError(f"Missing public functions for {name}")
        if len(defects) != (0 if tier == "good" else 2):
            raise ValueError(f"Unexpected defect count for {name}")
        if tier == "challenge" and sum(c["category"] == "combination" for c in cases) < 2:
            raise ValueError(f"Missing challenge scenarios for {name}")
        if len({case["call"] for case in cases}) != len(cases):
            raise ValueError(f"Duplicate scenario in {name}")
        relative = f"source/{tier}/{name}.py"
        entry = {"name": name, "tier": tier, "domain": domain, "path": relative,
                 "targets": functions, "sha256": digest(source), "cases": len(cases)}
        write(ROOT / relative, source)
        fixed_path = f"reference/corrected/{name}.py" if defects else relative
        if defects:
            write(ROOT / fixed_path, corrected)
        public.append(entry)
        truth.append({**entry, "corrected_path": fixed_path, "corrected_sha256": digest(corrected),
                      "tests": cases, "defects": defects})
    assert Counter(row["tier"] for row in public) == {"good": 25, "buggy": 50, "challenge": 25}
    json_file(ROOT / "scenarios/modules.json", public)
    selections = {
        "basic_demo": [(name, example[0]) for name, example in MUTATION_EXAMPLES.items() if name == "calculator"],
        "bug_hunting": [(item["name"], item["targets"][0]) for item in public if item["name"] in BLIND_NAMES],
        "regression_demo": [("unit_scaling", "metric_kilometers")],
        "mutation_demo": [(name, example[0]) for name, example in MUTATION_EXAMPLES.items()],
    }
    for scenario, entries in selections.items():
        definition = [{"module": name, "target": target(call) if "(" in call else call}
                      for name, call in entries]
        json_file(ROOT / f"scenarios/{scenario}.json", definition)
    json_file(ROOT / "reference/ground_truth.json", {"schema_version": 1, "modules": truth})
    json_file(ROOT / "reference/answer_index.json", {
        defect["id"]: {"module": row["name"], "case": defect["case_id"],
                       "category": defect["category"], "corrected_path": row["corrected_path"]}
        for row in truth for defect in row["defects"]
    })


if __name__ == "__main__":
    main()
