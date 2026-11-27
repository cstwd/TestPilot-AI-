"""Verify the real F12 provider on a deliberately faulty test suite and the established contract."""
from pathlib import Path
from backend.engine_analyzer import analyze_source
from backend.engine_failures import analyze_failures
from backend.engine_feedback import digest, eligible, propose
from backend.engine_strategy import build_strategy
from backend.generation import checked
from backend.model_identity import MODEL
from backend.runner import execute
from .quality import save

ROOT = Path(__file__).resolve().parents[2]


def main():
    source=(ROOT/"eval/phase03/repair/subject.py").read_text("utf8")
    target="reciprocal_units"
    old=checked("from subject import reciprocal_units as target\n"
                "def test_zero():\n    assert isinstance(target(x=0), int)\n"
                "def test_value():\n    assert target(2) == 50")
    baseline=execute(source,old,detailed=True,timeout_s=25)
    analysis=analyze_source(source)
    strategy=build_strategy(analysis,target)
    findings=analyze_failures(baseline,strategy,old,analysis)["findings"]
    assert baseline["status"]=="failed" and eligible(findings)
    requested={"mode":"ai","code":old,"sha256":digest(old)}
    selected,reason,rejected=propose(source,target,analysis,strategy,requested,findings,None)
    proof=selected if selected["mode"]=="ai" else rejected
    result=execute(source,selected["code"],detailed=True,timeout_s=25)
    save(ROOT/"reports/phase06/raw/repair-live.json",{
        "input":"designed test-error fixture", "subject_sha256":digest(source),
        "before":baseline,"findings":findings,"after":result,"reason":reason,
        "chosen":selected,"actual_qwen_proposal":proof})
    assert proof["model"]==MODEL and proof["attempts"] and result["status"]=="passed"
    assert "assert target(2) == 50" in selected["code"]
    print("F12 real Ollama proposal routed through Provider. Actual repair mode",selected["mode"])

if __name__=="__main__":
    main()
