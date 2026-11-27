"""Coordinate the engine and commit each evidence record before advancing."""
from hashlib import sha256
import logging
from threading import BoundedSemaphore

from fastapi import HTTPException

from . import engine_history as history
from .engine_analyzer import analyze_source
from .engine_failures import analyze_failures
from .engine_feedback import eligible, propose
from .engine_history import RecordKind as Kind
from .engine_llm import GenerationFailure, generate_tests
from .engine_strategy import build_strategy
from .runner import execute
from .store import connect, one


LOG = logging.getLogger("testpilot.engine")
SLOTS = BoundedSemaphore(1)


class Workflow:
    def __init__(self, path, task, file, target, max_repairs, generation_mode):
        self.path = path
        self.task = task
        self.file = file
        self.target = target
        self.max_repairs = max_repairs
        self.config = {"provider": "template"} if generation_mode == "template" else None
        self.generation_mode = generation_mode
        self.stage = Kind.analysis
        self.initial_id = self.final_id = None
        self.generated_id = None
        self.execution_count = 0

    def save(self, kind, status, payload):
        key = history.append_record(self.path, self.task, kind, status, payload)
        LOG.info("task=%s record=%s kind=%s status=%s", self.task, key, kind.value, status)
        return key

    def finish(self, status, reason):
        summary = {"stop_reason": reason, "initial_execution_id": self.initial_id,
                   "final_execution_id": self.final_id, "execution_count": self.execution_count,
                   "source_sha256": self.file["sha256"], "target": self.target,
                   "generation_mode_requested": self.generation_mode}
        history.append_record(self.path, self.task, Kind.report, status, summary, terminal=status)
        LOG.info("task=%s terminal=%s runs=%s", self.task, status, self.execution_count)

    def prepare(self, saved_suite=None):
        self.stage = Kind.analysis
        analysis = analyze_source(self.file["source"])
        analysis.update(file_id=self.file["id"], filename=self.file["filename"], revision=self.file["revision"])
        self.save(self.stage, "ready" if analysis["valid"] else "invalid", analysis)
        if not analysis["valid"]:
            self.finish("error", analysis["diagnostics"][0]["message"])
            return None
        self.stage = Kind.strategy
        strategy = build_strategy(analysis, self.target)
        self.save(self.stage, "ready", strategy)
        self.stage = Kind.generated
        suite = saved_suite if saved_suite is not None else generate_tests(
            self.file["source"], self.target, analysis, strategy, config=self.config)
        self.generated_id = self.save(self.stage, "ready", suite)
        return analysis, strategy, suite

    def measure(self, suite):
        self.stage = Kind.execution
        result = execute(self.file["source"], suite["code"], detailed=True)
        result.update(generated_test_id=self.generated_id, test_sha256=suite["sha256"],
                      source_sha256=self.file["sha256"])
        self.final_id = self.save(self.stage, result["status"], result)
        if self.initial_id is None:
            self.initial_id = self.final_id
        self.execution_count += 1
        self.stage = Kind.coverage
        metrics = {key: result[key] for key in ("covered_lines", "total_lines", "coverage_pct",
                                                "covered_branches", "total_branches", "branch_pct")}
        self.save(self.stage, "measured" if result["covered_lines"] is not None else "unavailable",
                  {**metrics, "execution_id": self.final_id})
        return result

    def evaluate(self, analysis, strategy, suite):
        seen = {suite["sha256"]}
        for number in range(self.max_repairs + 1):
            result = self.measure(suite)
            self.stage = Kind.failure
            findings = analyze_failures(result, strategy, suite["code"], analysis)
            findings["execution_id"] = self.final_id
            self.save(self.stage, "analyzed", findings)
            if not result["result_complete"]:
                self.finish("error", "隔离执行未完成，详见执行器诊断")
                return
            if not eligible(findings["findings"]):
                reasons = {"passed": "已执行测试通过", "skipped": "所有测试均跳过"}
                self.finish("completed", reasons.get(result["status"], "保留原始失败证据，详见缺陷归因"))
                return
            if number == self.max_repairs:
                self.finish("completed", "已达到反馈次数上限，保留当前结果")
                return
            self.stage = Kind.repair
            attempt = {"number": number + 1, "previous_sha256": suite["sha256"],
                       "execution_id": self.final_id, "previous_generated_id": self.generated_id}
            try:
                candidate, reason, rejected = propose(self.file["source"], self.target, analysis,
                                                      strategy, suite, findings["findings"], self.config)
            except ValueError as exc:
                candidate, reason, rejected = None, str(exc), None
            attempt.update(reason=reason, candidate_sha256=candidate["sha256"] if candidate else None,
                           rejected_proposal=rejected)
            if not candidate or candidate["sha256"] in seen:
                status = "duplicate" if candidate else "needs_review"
                if candidate:
                    attempt.update(reason="已记录相同测试摘要，停止重复执行", rejected_proposal=candidate)
                self.save(self.stage, status, attempt)
                self.finish("completed", attempt["reason"])
                return
            repair_id = self.save(self.stage, "accepted", attempt)
            suite = {**candidate, "repair_attempt_id": repair_id}
            self.stage = Kind.generated
            self.generated_id = self.save(self.stage, "ready", suite)
            seen.add(suite["sha256"])


def run_task(path, file_id, target, max_repairs=1, generation_mode="configured", *, saved_suite=None):
    if not SLOTS.acquire(blocking=False):
        raise HTTPException(409, "已有智能测试任务在运行，请稍后重试")
    try:
        task, file = history.create_task(path, file_id, target, max_repairs)
        flow = Workflow(path, task, file, target, max_repairs, generation_mode)
        try:
            prepared = flow.prepare(saved_suite)
            if prepared is not None:
                flow.evaluate(*prepared)
        except GenerationFailure as exc:
            flow.save(flow.stage, "unavailable", exc.evidence)
            flow.finish("error", str(exc))
        except Exception as exc:
            LOG.exception("task=%s failed at %s", task, flow.stage.value)
            reason = str(exc)[:1000] or type(exc).__name__
            flow.save(flow.stage, "unavailable", {"error": reason, "exception": type(exc).__name__})
            flow.finish("error", reason)
        return history.read_task(path, task)
    finally:
        SLOTS.release()


def run_saved_suite_task(path, file_id, suite_id):
    """Start an engine task with the exact persisted suite already used by F04/F05."""
    with connect(path) as db:
        suite = one(db, "SELECT s.*,f.project_id,f.filename FROM suites s JOIN files f ON f.id=s.file_id "
                        "WHERE s.id=?", (suite_id,))
        file = one(db, "SELECT project_id,filename FROM files WHERE id=?", (file_id,))
    if ((file["project_id"], file["filename"]) != (suite["project_id"], suite["filename"])
            or suite["sha256"] != sha256(suite["source"].encode("utf-8")).hexdigest()):
        raise HTTPException(422, "文件版本或已保存套件的摘要不匹配")
    mode = "configured" if suite["mode"] == "ai" else "template"
    evidence = {"code": suite["source"], "sha256": suite["sha256"], "mode": suite["mode"],
                "attempts": [], "workbench_suite_id": suite_id}
    return run_task(path, file_id, suite["target"], 0, mode, saved_suite=evidence)
