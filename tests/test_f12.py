"""Check the bounded feedback path on a real erroneous generated test."""
import hashlib
from pathlib import Path

import pytest

from backend import engine_feedback, engine_flow, engine_history, projects
from backend.engine_analyzer import analyze_source
from backend.engine_failures import analyze_failures
from backend.engine_history import RecordKind
from backend.engine_strategy import build_strategy
from backend.generation import checked


SOURCE = (Path(__file__).resolve().parents[1] / "eval/phase03/repair/subject.py").read_text(encoding="utf8")


def test_repair_runs_both_versions_without_changing_subject(sample_workspace):
    request, project, _, _ = sample_workspace
    file = projects.import_file(project["id"], projects.FileInput(filename="unit.py", source=SOURCE), request)
    task = engine_flow.run_task(request.app.state.db_path, file["id"], "reciprocal_units", 1, "template")
    runs = [r for r in task["records"] if r["kind"] == RecordKind.execution.value]
    assert [r["status"] for r in runs] == ["failed", "passed"], task["records"][-1]
    print("actual executions", [(r["id"], r["status"], r["payload"]["test_sha256"]) for r in runs])
    assert all(r["payload"]["source_sha256"] == file["sha256"] for r in runs)
    assert projects.read_file(file["id"], request)["source"] == SOURCE
    revisions = [r["payload"] for r in task["records"] if r["kind"] == "GeneratedTest"]
    assert [r["mode"] for r in revisions] == ["template", "rules"]
    assert revisions[0]["sha256"] != revisions[1]["sha256"]
    assert task == engine_history.read_task(request.app.state.db_path, task["id"])
    assert {c["nodeid"] for c in runs[0]["payload"]["cases"]} == {c["nodeid"] for c in runs[1]["payload"]["cases"]}


def test_never_repair_program_or_unknown():
    assert not engine_feedback.eligible([{"category": c, "outcome": "failed"} for c in ["test_error", "program_defect"]])
    assert not engine_feedback.eligible([{"category": "undetermined", "outcome": "error"}])
    assert not engine_feedback.eligible([{"category": "skipped", "outcome": "skipped"}])


def test_unknown_oracle_is_preserved():
    original = "from subject import f\ndef test_f():\n    assert f(2) == oracle(2)"
    finding = {"category": "test_error", "nodeid": "test_generated.py::test_f", "test_line": 3,
               "exception_type": "NameError", "message": "name 'oracle' is not defined", "contract": None}
    with pytest.raises(ValueError, match="文档契约"):
        engine_feedback.allowed_edit(original, "f", [finding])


def test_feedback_bound_and_duplicate_are_audited(sample_workspace, monkeypatch):
    # Isolate control flow using a test double. The first test exercises actual WASI.
    request, project, _, _ = sample_workspace
    file = projects.import_file(project["id"], projects.FileInput(filename="unit.py", source=SOURCE), request)
    def adjudicate(self, suite):
        self.execution_count += 1
        return {"status": "failed", "result_complete": True}
    monkeypatch.setattr(engine_flow.Workflow, "measure", adjudicate)
    monkeypatch.setattr(engine_flow, "analyze_failures", lambda *a: {"findings": [{"outcome": "failed", "category": "test_error"}]})
    monkeypatch.setattr(engine_flow, "propose", lambda src, target, a, s, suite, f, c: (suite, "duplicate", None))
    for limit, expected in [(0, []), (3, ["duplicate"])]:
        task = engine_flow.run_task(request.app.state.db_path, file["id"], "reciprocal_units", limit, "template")
        assert [r["status"] for r in task["records"] if r["kind"] == "RepairAttempt"] == expected
        assert task["records"][-1]["payload"]["execution_count"] == 1
        assert task["status"] == "completed"


def test_unsafe_regeneration_keeps_unrelated_tests(monkeypatch):
    target = "reciprocal_units"
    before = checked("from subject import reciprocal_units as target\n"
                     "def test_zero():\n    assert isinstance(target(x=0), int)\n"
                     "def test_value():\n    assert target(2) == 50")
    frames = [{"path": "test_generated.py", "function": "test_zero", "line": 4}]
    analysis = analyze_source(SOURCE)
    strategy = build_strategy(analysis, target)
    key = "test_generated.py::test_zero"
    run = {"status": "failed", "cases": [{"nodeid": key, "outcome": "failed"}], "failures": [
        {"nodeid": key, "phase": "call", "frames": frames, "exception_type": "ValueError", "message": "zero"}]}
    findings = analyze_failures(run, strategy, before, analysis)["findings"]
    assert findings[0]["category"] == "test_error"
    original = {"mode": "ai", "code": before, "sha256": hashlib.sha256(before.encode()).hexdigest()}
    weakened = {"mode": "ai", "code": "def test_zero(): assert True", "sha256": "fixture-candidate"}
    monkeypatch.setattr(engine_feedback, "generate_tests", lambda *args, **kwargs: weakened)
    corrected, _, rejected = engine_feedback.propose(SOURCE, target, analysis, strategy, original, findings, None)
    assert rejected == weakened and corrected["mode"] == "rules"
    assert "assert target(2) == 50" in corrected["code"] and "pytest.raises(ValueError)" in corrected["code"]
