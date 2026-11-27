import json
import pytest
from backend import mutation_feedback as mf
from backend.model_protocol import MutationCase
from backend.model_provider import ModelError, Reply

SOURCE = 'def double(x): return x * 2'
PREVIOUS = 'from subject import double\ndef test_zero(): assert double(0) == 0'
SURVIVORS = [{"id":"sample-id","operator":"arithmetic","line":1,"before":"*","after":"+"}]

def test_protocol_double_append_only_and_provenance(monkeypatch):
    model = MutationCase(disposition="test",call="double(-2)",expected=-4,reason="Zero alone cannot distinguish.")
    def infer(operation,messages,schema,**kwargs):
        assert operation=="mutation-feedback" and schema is MutationCase
        context=json.loads(messages[1]["content"])
        assert context["source"]==SOURCE and context["measured"]["exit_code"]==0
        assert context["diff"]["before"]=="*"
        return Reply("run-fixture",kwargs["validate"](model),[{"raw":model.model_dump_json()}])
    monkeypatch.setattr(mf.provider,"infer",infer)
    r=mf.supplement(SOURCE,"double",PREVIOUS,SURVIVORS,observations={"sample-id":{"exit_code":0}})
    assert r["code"]==PREVIOUS+"\n\n"+r["added_code"]
    assert "assert double(-2) == -4" in r["code"] and r["cases"][0]["mutant_id"]=="sample-id"
    assert r["attempts"][0]["run_id"]=="run-fixture"

def test_no_case_preserves_survivor(monkeypatch):
    model=MutationCase(disposition="no_distinguishing_case",call=None,expected=None,reason="Equal on the domain.")
    def infer(*args,**kwargs):
        return Reply("no-case",kwargs["validate"](model),[])
    monkeypatch.setattr(mf.provider,"infer",infer)
    r=mf.supplement(SOURCE,"double",PREVIOUS,SURVIVORS)
    assert r["status"]=="rejected" and not r["cases"]
    assert r["attempts"][0]["status"]=="no_distinguishing_case"

def test_cancel_between_model_calls(monkeypatch):
    cancelled=False
    def infer(*args,**kwargs):
        nonlocal cancelled
        cancelled=True
        model=MutationCase(disposition="test",call="double(1)",expected=2,reason="Nonzero.")
        return Reply("first",kwargs["validate"](model),[])
    monkeypatch.setattr(mf.provider,"infer",infer)
    r=mf.supplement(SOURCE,"double",PREVIOUS,[*SURVIVORS,{**SURVIVORS[0],"id":"other"}],
                    should_cancel=lambda:cancelled)
    assert r["status"]=="cancelled" and r["pending_ids"]==["other"]
    assert r["attempts"][0]["run_id"]=="first" and r["code"] is None

@pytest.mark.parametrize("call,expected", [("wrong(3)", "6"), ("double(side_effect())", "6"),
                                          ("double(2)", "bad()"), ("double(1)", "raises Unknown")])
def test_only_literal_test_cases(call, expected):
    raw = json.dumps({"cases": [{"site": 1, "reason": "candidate", "call": call, "expected": expected}]})
    with pytest.raises(ValueError):
        mf.additions(raw, "double", SURVIVORS, PREVIOUS)


@pytest.mark.parametrize("target", ["ValueError", "pytest"])
def test_subject_names_do_not_shadow_raises(target):
    raw = json.dumps({"cases": [{"site": 1, "reason": "negative", "call": target + "(-1)",
                                 "expected": "raises ValueError"}]})
    _, added, _ = mf.additions(raw, target, SURVIVORS, PREVIOUS)
    assert f"from subject import {target} as _testpilot_subject_function" in added
    assert "with pytest.raises(ValueError):\n        _testpilot_subject_function(-1)" in added

def test_simple_predicate_hint_has_no_expected_value():
    from backend.mutation_generator import make_plan
    from backend.engine_analyzer import analyze_source
    import ast
    src = "def rate(units: int, active: bool) -> int:\n    if units > 7 and active:\n        return 4\n    return 0"
    assert analyze_source(src)["valid"]
    plan = make_plan(src, "rate")
    site = next(m for m in plan if m["before"] == ">" and m["after"] == ">=")
    hint = mf.input_hint(src, ast.parse(src).body[0], site)
    assert hint == "rate(7, True)"
