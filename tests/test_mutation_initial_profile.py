"""A configured generation forwards the full contract with no alternate model selector."""
import json
import pytest
from backend import engine_llm
from backend.model_provider import Reply


@pytest.mark.parametrize("contracts", [[{"expected":"1"},{"expected":"2"}],[{"exception":"ValueError"}]])
def test_contracts_preserved(contracts,monkeypatch):
    source="def increment(x): return x+1"
    def infer(operation,messages,schema,**kwargs):
        assert operation=="test-generation"
        payload=json.loads(messages[1]["content"])
        assert payload["contracts"]==contracts and payload["source"]==source
        return Reply("contract-id","from subject import increment\ndef test(): assert increment(0)==1",[])
    monkeypatch.setattr(engine_llm.provider,"infer",infer)
    result=engine_llm.generate_tests(source,"increment",{},{"contracts":contracts})
    assert result["run_id"]=="contract-id" and result["model"]==engine_llm.MODEL
