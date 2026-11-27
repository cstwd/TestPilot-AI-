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
    ("local-compact", "https://example.test", None, None, True, "default"),
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
    monkeypatch.setenv("TESTPILOT_MODEL_PROVIDER", "ollama")
    monkeypatch.setenv("TESTPILOT_MODEL_NAME", "protocol-double")
    monkeypatch.setenv("TESTPILOT_MODEL_BASE_URL", base)
    monkeypatch.setenv("TESTPILOT_MODEL_PROMPT_PROFILE", profile)
    monkeypatch.delenv("TESTPILOT_MODEL_API_KEY", raising=False)
    suite = engine_llm.generate_tests(SOURCE, "add_one", analysis, strategy, feedback=feedback, previous_code=previous)
    attempt, = suite["attempts"]
    assert attempt["prompt_profile"] == expected and attempt["prompt"] == requests[0]
    context = json.loads(attempt["prompt"][1]["content"])
    if expected == "local-compact":
        assert context["analysis"]["name"] == "add_one"
        assert context["strategy"]["contracts"] == strategy["contracts"]
        assert "from subject import add_one" in context["feedback"]["task"]
    else:
        assert context["analysis"] == analysis and context["strategy"] == strategy
        assert context["feedback"] == feedback and context["previous_code"] == previous
