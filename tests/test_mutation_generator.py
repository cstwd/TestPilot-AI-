from pathlib import Path

import pytest

from backend.mutation_generator import apply_site, digest, make_plan


SOURCE = (Path(__file__).resolve().parents[1] / "eval/phase04/bonus.py").read_text("utf8")


def test_all_six_families_are_real_replayable_edits():
    plan = make_plan(SOURCE, "bonus")
    assert plan == make_plan(SOURCE, "bonus")
    assert len(plan) == len({m["id"] for m in plan}) == 9
    assert {m["family"] for m in plan} == {"comparison","arithmetic","condition","boolean","return","exception"}
    for m in plan:
        mutant = apply_site(SOURCE, m)
        assert digest(mutant) == m["mutated_sha256"] and mutant != SOURCE
        compile(mutant, "subject.py", "exec")
        print(m["line"], m["operator"], repr(m["before"]), "->", repr(m["after"]))
    assert SOURCE == (Path(__file__).resolve().parents[1] / "eval/phase04/bonus.py").read_text("utf8")


def test_only_selected_function_unicode_line_offsets_and_candidates():
    source = "# A\f B\ndef helper(x): return x+1\ndef measure(数):\n    if 数<0: return None\n    return 数+1\n"
    sites = make_plan(source, "measure")
    assert all(m["line"] >= 4 for m in sites)
    equivalent, = [m for m in sites if m["equivalent_candidate"]]
    assert equivalent["before"] == "return None" and equivalent["after"] == "return"
    for m in sites:
        altered = apply_site(source, m)
        assert altered.split("\ndef measure")[0] == source.split("\ndef measure")[0]
        compile(altered, "subject.py", "exec")
    with pytest.raises(ValueError):
        apply_site(source + "#changed", equivalent)


def test_entire_manifest_rejected_when_oversize():
    with pytest.raises(ValueError, match="整体拒绝"):
        make_plan("def f(x):\n" + "    if x: return x\n" * 70, "f")


def test_multiline_and_chained_comparisons():
    source = "def check(数):\r\n    return (0 < 数\r\n            <= 7)\r\n"
    sites = make_plan(source, "check")
    comparisons = [s for s in sites if s["family"] == "comparison"]
    assert len(comparisons) == 2 and comparisons[0]["line"] != comparisons[1]["line"]
    for m in comparisons:
        compile(apply_site(source, m), "subject.py", "exec")
