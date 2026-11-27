import json

import pytest

from backend import mutation_feedback as mf

SOURCE = 'def double(x): return x * 2'
PREVIOUS = 'from subject import double\ndef test_zero(): assert double(0) == 0'
SURVIVORS = [{"id": "sample-id", "operator": "arithmetic", "line": 1, "before": "*", "after": "+"}]


@pytest.mark.parametrize("base", ["https://example.test", "http://example.test:11434",
                                  "http://token@127.0.0.1", "http://127.0.0.1:11434/v1",
                                  "http://localhost:11434?model=foo"])
def test_only_local_endpoints(base, monkeypatch):
    monkeypatch.setattr(mf, "request_json", lambda *args: pytest.fail("unexpected network request"))
    assert mf.supplement(SOURCE, "double", PREVIOUS, SURVIVORS, config={"base_url": base})["status"] == "unavailable"


def test_remote_model_alias_rejected_before_source(monkeypatch):
    paths = []
    def fake_request(base, path, payload, timeout):
        paths.append(path)
        if path == "/api/tags":
            return {"models": [{"name": "alias:latest", "digest": "fixture"}]}
        return {"remote_model": "remote", "remote_host": "service.invalid", "details": {"format": "gguf"}}
    monkeypatch.setattr(mf, "request_json", fake_request)
    result = mf.supplement(SOURCE, "double", PREVIOUS, SURVIVORS, config={"model": "alias"})
    assert result["status"] == "unavailable" and result["attempts"] == []
    assert paths == ["/api/tags", "/api/show"]


def test_protocol_double_append_only_and_provenance(monkeypatch):
    # Isolate the protocol; the real local model result is archived separately.
    record = {"call": "double(-2)", "expected": -4, "reason": "Zero alone cannot distinguish the operators."}
    calls = []
    def fake_request(base, path, payload, timeout):
        calls.append(path)
        if path == "/api/tags":
            return {"models": [{"name": "local:latest", "digest": "fixture-digest"}]}
        if path == "/api/show":
            return {"details": {"format": "gguf"}, "model_info": {"general.architecture": "fixture"}}
        prompt = payload["messages"][0]["content"]
        assert "return x * 2" in prompt and "Existing suite: 1 tests" in prompt
        assert "Line 1: * changed to +" in prompt
        raw = json.dumps(record)
        return {"message": {"content": raw}, "done": True}
    monkeypatch.setattr(mf, "request_json", fake_request)
    result = mf.supplement(SOURCE, "double", PREVIOUS, SURVIVORS, config={"model": "local"})
    assert calls == ["/api/tags", "/api/show", "/api/chat"]
    assert result["code"] == PREVIOUS + "\n\n" + result["added_code"]
    assert "assert double(-2) == -4" in result["code"]
    assert result["cases"][0]["mutant_id"] == "sample-id"
    assert json.loads(result["attempts"][0]["raw"]) == record


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


def test_cancel_between_model_calls(monkeypatch):
    cancelled = False
    other = {**SURVIVORS[0], "id": "other"}
    monkeypatch.setattr(mf, "choose_model", lambda *args: ("local", "fixture"))
    def first_request(*args):
        nonlocal cancelled
        cancelled = True
        return {"message": {"content": json.dumps({"call": "double(1)", "expected": 2, "reason": "test"})},
                "done": True}
    monkeypatch.setattr(mf, "request_json", first_request)
    result = mf.supplement(SOURCE, "double", PREVIOUS, [*SURVIVORS, other], config={}, should_cancel=lambda: cancelled)
    assert result["status"] == "cancelled" and result["pending_ids"] == ["other"]
    assert len(result["attempts"]) == 1 and result["attempts"][0]["status"] == "accepted"
    assert result["code"] is None


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
