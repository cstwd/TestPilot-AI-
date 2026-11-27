"""F09 keeps its code and template contracts while transport is exercised by Provider tests."""
import hashlib
import json
import pytest

from backend import engine_llm
from backend.engine_llm import GenerationFailure, generate_tests, validate_model_output
from backend.model_identity import MODEL
from backend.model_protocol import GeneratedCode
from backend.model_provider import ModelError, Reply

SOURCE = "def double(x: int) -> int:\n    return x * 2\n"
MODEL_CODE = "from subject import double\n\ndef test_double():\n    assert double(3) == 6\n"

def run(config, **extra):
    return generate_tests(SOURCE,"double",{"valid":True},{"cases":[]},config=config,**extra)

def test_provider_contract_and_provenance(monkeypatch):
    def inference(operation,messages,schema,**kwargs):
        assert operation=="test-repair" and schema is GeneratedCode
        assert json.loads(messages[1]["content"])["previous_code"]=="invalid"
        return Reply("test-id",kwargs["validate"](GeneratedCode(code=MODEL_CODE)),[{"raw":"recorded"}])
    monkeypatch.setattr(engine_llm.provider,"infer",inference)
    result=run({"model":"external","base_url":"https://elsewhere.invalid"},previous_code="invalid")
    assert result["mode"]=="ai" and result["model"]==MODEL and result["run_id"]=="test-id"
    assert result["sha256"]==hashlib.sha256(result["code"].encode()).hexdigest()

def test_unavailable_ai_keeps_evidence_without_fallback(monkeypatch):
    def unavailable(*args,**kwargs):
        raise ModelError("unavailable","Ollama offline","call",[{"raw":"rejected candidate"}])
    monkeypatch.setattr(engine_llm.provider,"infer",unavailable)
    with pytest.raises(GenerationFailure) as error:
        run({})
    assert error.value.evidence["attempts"][0]["raw"]=="rejected candidate"
    assert error.value.evidence["code"] is None and error.value.evidence["error_kind"]=="unavailable"

@pytest.mark.parametrize("candidate", [
    "", "def test_empty(): pass", "def test_constant(): assert True",
    "def test_unrelated(): assert len([]) == 0",
    MODEL_CODE + "\ndef test_double():\n    assert double(2) == 4",
])
def test_reject_empty_or_unrelated_tests(candidate):
    with pytest.raises(ValueError):
        validate_model_output(candidate, "double")


def test_explicit_template_overrides_environment(monkeypatch):
    monkeypatch.setenv("TESTPILOT_MODEL_PROVIDER", "ollama")
    monkeypatch.setenv("TESTPILOT_MODEL_NAME", "fixture-model")
    for cfg in ({"provider": "template"},):
        result = run(cfg)
        assert result["mode"] == "template" and result["attempts"] == []
        assert result["fallback_reason"] and result["sha256"]


def test_analysis_and_template_agree_on_directed_doctests():
    from backend.engine_analyzer import analyze_source
    from backend.engine_strategy import build_strategy

    source = '''def double(x: int) -> int:
    """
    >>> double(4)  # doctest: +SKIP
    999
    >>> double(2)
    4
    """
    return x * 2
'''
    analysis = analyze_source(source)
    strategy = build_strategy(analysis, "double")
    assert [c["call"] for c in strategy["contracts"]] == ["double(2)"]
    suite = generate_tests(source, "double", analysis, strategy, config={"provider": "template"})
    assert "assert target(2) == 4" in suite["code"]
    assert "999" not in suite["code"]
