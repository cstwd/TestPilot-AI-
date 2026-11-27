"""Exercise the proposal gate using actual pytest observations from the sandbox."""
import json

from backend.mutation_feedback import additions
from backend.mutation_flow import select_green_additions
from backend.mutation_results import baseline_ok
from backend.runner import execute


def test_partial_local_suggestions_keep_only_green_appended_tests():
    source = "def delta(n):\n    return n + 1\n"
    original = "from subject import delta\n\ndef test_original():\n    assert delta(0) == 1\n"
    suggestions = [{"site": 1, "reason": "positive input", "call": "delta(3)", "expected": "4"},
                   {"site": 2, "reason": "negative input", "call": "delta(-2)", "expected": "77"}]
    code, added, cases = additions(json.dumps({"cases": suggestions}), "delta", [{"id": "a"}, {"id": "b"}], original)
    green = execute(source, original, detailed=True)
    trial = execute(source, code, detailed=True)
    assert baseline_ok(green)
    assert (trial["passed"], trial["failed"]) == (2, 1)
    proposal = {"code": code, "cases": cases, "added_code": added}
    selected = select_green_additions(original, proposal, green, trial)
    assert selected["accepted_names"] == [cases[0]["test_name"]]
    assert selected["rejected_names"] == [cases[1]["test_name"]]
    assert selected["code"].startswith(original) and "77" not in selected["code"]
    confirmed = execute(source, selected["code"], detailed=True)
    assert baseline_ok(confirmed) and confirmed["passed"] == 2
    assert select_green_additions(original, proposal, green, {"result_complete": False})["code"] is None
