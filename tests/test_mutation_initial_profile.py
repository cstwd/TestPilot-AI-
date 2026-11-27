"""Verify selection and provenance of the optional local-model initial prompt."""
import json

import pytest

from backend import engine_llm
from backend.engine_analyzer import analyze_source
from backend.engine_strategy import build_strategy


SOURCE = 'def add_one(n: int) -> int:\n    """Example.\n\n    >>> add_one(4)\n    5\n    """\n    return n+1'


@pytest.mark.parametrize(("profile", "base", "feedback", "previous", "contracts", "expected"), [
    ("local-compact", "http://127.0.0.1:11434", None, None, True, "local-compact"),
    ("local-compact", "http://[::1]:11434", None, None, True, "local-compact"),
    ("local-compact", "https://example.test", None, None, True, "blocked"),
    ("local-compact", "http://localhost:11434", {"failure": "example"}, None, True, "default"),
    ("local-compact", "http://localhost:11434", None, "prior suite", True, "default"),
    ("local-compact", "http://localhost:11434", None, None, False, "default"),
    ("", "http://127.0.0.1:11434", None, None, True, "default"),
])
def test_profile(monkeypatch, profile, base, feedback, previous, contracts, expected):
    analysis = analyze_source(SOURCE)
    strategy = build_strategy(analysis, "add_one")
    if not contracts:
        strategy["contracts"] = []
    requests = []
    def provider_double(url, provider, model, key, timeout, messages):
        requests.append(messages)
        return "from subject import add_one\ndef test_value():\n    assert add_one(4) == 5"
    monkeypatch.setattr(engine_llm, "fetch_code", provider_double)
    checked = []

    def metadata_double(base, path, payload, timeout):
        checked.append(path)
        if path == "/api/tags":
            return {"models": [{"name": "protocol-double", "digest": "fixture-digest"}]}
        assert path == "/api/show"
        return {"details": {"format": "gguf"}, "model_info": {"general.architecture": "qwen"}}

    monkeypatch.setattr(engine_llm.local_ollama, "request_json", metadata_double)
    monkeypatch.setenv("TESTPILOT_MODEL_PROVIDER", "ollama")
    monkeypatch.setenv("TESTPILOT_MODEL_NAME", "protocol-double")
    monkeypatch.setenv("TESTPILOT_MODEL_BASE_URL", base)
    monkeypatch.setenv("TESTPILOT_MODEL_PROMPT_PROFILE", profile)
    monkeypatch.delenv("TESTPILOT_MODEL_API_KEY", raising=False)
    suite = engine_llm.generate_tests(SOURCE, "add_one", analysis, strategy, feedback=feedback, previous_code=previous)
    if expected == "blocked":
        assert suite["mode"] == "template" and suite["fallback_reason"] and not requests and not checked
        return
    attempt, = suite["attempts"]
    assert attempt["prompt_profile"] == expected and attempt["prompt"] == requests[0]
    context = json.loads(attempt["prompt"][1]["content"])
    if profile == "local-compact":
        assert checked == ["/api/tags", "/api/show"] and attempt["local_model_digest"] == "fixture-digest"
    else:
        assert not checked
    if expected == "local-compact":
        assert context["analysis"]["name"] == "add_one"
        assert context["strategy"]["contracts"] == strategy["contracts"]
        assert "from subject import add_one" in context["feedback"]["task"]
    else:
        assert context["analysis"] == analysis and context["strategy"] == strategy
        assert context["feedback"] == feedback and context["previous_code"] == previous


def test_remote_alias_refused_before_sending_source(monkeypatch):
    def metadata(base, path, payload, timeout):
        if path == "/api/tags":
            return {"models": [{"name": "seemingly-local", "digest": "fixture"}]}
        return {"remote_host": "remote.invalid", "details": {"format": "gguf"},
                "model_info": {"general.architecture": "qwen"}}

    monkeypatch.setattr(engine_llm.local_ollama, "request_json", metadata)
    monkeypatch.setattr(engine_llm, "fetch_code", lambda *args: pytest.fail("source may not reach this model"))
    cfg = {"provider": "ollama", "model": "seemingly-local", "prompt_profile": "local-compact"}
    result = engine_llm.generate_tests(SOURCE, "add_one", {}, {}, config=cfg)
    assert result["mode"] == "template" and result["fallback_reason"] and result["attempts"] == []


@pytest.mark.parametrize("examples", [[{"expected": "1"}, {"expected": "2"}], [{"exception": "ValueError"}]])
def test_complex_contracts_keep_full_strategy(examples):
    strategy = {"contracts": examples}
    context, profile = engine_llm.prompt_context(True, SOURCE, "add_one", {}, strategy, None, None)
    assert profile == "default" and context["strategy"] == strategy
