"""The HTTP server below is a protocol test double, not a live language model."""
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread

import pytest

from backend.engine_llm import GenerationFailure, generate_tests, validate_model_output


SOURCE = "def double(x: int) -> int:\n    return x * 2\n"
MODEL_CODE = "from subject import double\n\ndef test_double():\n    assert double(3) == 6\n"


@pytest.fixture
def endpoint_double():
    received = []
    responses = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            received.append((self.path, request, self.headers.get("Authorization")))
            status, headers, payload = responses.pop(0)
            self.send_response(status)
            for name, value in headers.items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode())

        def log_message(self, *args):
            pass

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}", responses, received
        finally:
            server.shutdown()
            thread.join(timeout=2)


def run(config, **extra):
    return generate_tests(SOURCE, "double", {"valid": True}, {"cases": []}, config=config, **extra)


@pytest.mark.parametrize("provider,path", [("ollama", "/api/chat"), ("openai-compatible", "/v1/chat/completions")])
def test_provider_contract_and_provenance(endpoint_double, provider, path):
    url, responses, received = endpoint_double
    msg = {"content": "```python\n" + MODEL_CODE + "```"}
    payload = {"message": msg} if provider == "ollama" else {"choices": [{"message": msg}]}
    responses.append((200, {}, payload))
    config = {"provider": provider, "base_url": url if provider == "ollama" else url + "/v1",
              "model": "fixture-model", "api_key": "fixture-secret", "retries": 0}
    result = run(config, feedback={"message": "previous test syntax error"}, previous_code="invalid")
    assert result["mode"] == "ai" and result["fallback_reason"] is None
    assert result["sha256"] == hashlib.sha256(result["code"].encode()).hexdigest()
    assert "fixture-secret" not in json.dumps(result)
    [(actual_path, body, auth)] = received
    assert actual_path == path and auth == "Bearer fixture-secret"
    assert body["messages"] == result["attempts"][0]["prompt"]
    assert json.loads(body["messages"][1]["content"])["previous_code"] == "invalid"


def test_validation_retry_then_template(endpoint_double):
    url, responses, received = endpoint_double
    responses.extend([(200, {}, {"message": {"content": "def test_empty(): pass"}}),
                      (503, {}, {"error": "service unavailable"})])
    result = run({"provider": "ollama", "base_url": url, "model": "fixture-model", "retries": 1})
    assert result["mode"] == "template" and result["provider"] == "local-template"
    assert result["model"] is None and "503" in result["fallback_reason"]
    assert len(received) == len(result["attempts"]) == 2
    assert "test_empty" in result["attempts"][0]["output_excerpt"]
    assert len(received[1][1]["messages"]) > len(received[0][1]["messages"])
    assert "test_empty" in received[1][1]["messages"][-2]["content"]


def test_provider_and_template_failure_preserves_evidence(endpoint_double):
    url, responses, received = endpoint_double
    responses.append((200, {}, {"message": {"content": "def test_empty(): pass"}}))
    with pytest.raises(GenerationFailure) as failure:
        generate_tests("class Unsupported: pass", "Unsupported", {}, {},
                       config={"provider": "ollama", "model": "fixture-model", "base_url": url, "retries": 0})
    evidence = failure.value.evidence
    assert len(received) == 1 and evidence["code"] is None and evidence["sha256"] is None
    assert evidence["attempts"][0]["status"] == "rejected" and evidence["fallback_reason"] and evidence["error"]


def test_no_redirect_and_no_plaintext_remote(endpoint_double):
    url, responses, received = endpoint_double
    responses.append((307, {"Location": url + "/should-not-follow"}, {}))
    cfg = {"provider": "ollama", "base_url": url, "model": "fixture-model", "retries": 0}
    result = run(cfg)
    assert len(received) == 1 and "307" in result["fallback_reason"]
    for base in ("http://example.test", "https://user:fixture-secret@example.test"):
        result = run({**cfg, "base_url": base})
        assert result["mode"] == "template" and not result["attempts"]
        assert "fixture-secret" not in json.dumps(result)


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
    for cfg in ({}, {"provider": "template"}):
        result = run(cfg)
        assert result["mode"] == "template" and result["attempts"] == []
        assert result["fallback_reason"] and result["sha256"]
