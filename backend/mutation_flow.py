"""Run an immutable mutation manifest, checkpoint evidence and compare two real suites."""
from contextlib import contextmanager
from pathlib import Path
import ast
import os
import time

from fastapi import HTTPException

from . import mutation_store as store
from .mutation_feedback import supplement
from .mutation_generator import apply_site, digest
from .mutation_results import baseline_ok, case_map, classify
from .runner import execute
from .store import connect


@contextmanager
def run_lock(db_path):
    """One campaign per database, including across PyCharm instances. OS releases it on crash."""
    lock = Path(str(db_path) + ".mutation.lock")
    with lock.open("a+b") as handle:
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise HTTPException(409, "同一数据库已有变异会话在执行") from exc
        yield


class Cancellation:
    def __init__(self, path, key):
        self.path, self.key = path, key
        self.last_poll = 0
        self.cancelled = False

    def is_set(self):
        now = time.monotonic()
        if not self.cancelled and now - self.last_poll >= 0.1:
            with connect(self.path) as db:
                self.cancelled = bool(db.execute("SELECT cancel_requested FROM mutation_sessions WHERE id=?",
                                                 (self.key,)).fetchone()[0])
            self.last_poll = now
        return self.cancelled


class RunnerBusy(Exception):
    """No execution took place. The manifest position remains pending."""


def select_green_additions(previous, feedback, green, trial):
    """Retain only appended test functions observed passing on the original revision."""
    proposed = feedback["code"]
    names = [case["test_name"] for case in feedback["cases"]]
    old, observed = case_map(green), case_map(trial)
    accepted = []
    code = None
    if (observed and old and all(observed.get(k) == v for k, v in old.items())
            and trial["status"] in {"passed", "failed"} and trial["exit_code"] in {0, 1}):
        nodes = {"test_generated.py::" + name for name in names}
        if observed.keys() - old.keys() == nodes:
            accepted = [name for name in names if observed["test_generated.py::" + name] == "passed"]
        if accepted and len(accepted) == len(names):
            code = proposed
        elif accepted:
            added = feedback["added_code"]
            blocks = [ast.get_source_segment(added, n) for n in ast.parse(added).body
                      if isinstance(n, ast.FunctionDef) and n.name in accepted]
            if len(blocks) != len(accepted) or not all(blocks):
                raise ValueError("无法逐字重建已验证的补测")
            code = previous + "\n\n" + "\n\n".join(blocks) + "\n"
    return {"code": code, "accepted_names": accepted, "rejected_names": [n for n in names if n not in accepted]}


class Experiment:
    def __init__(self, path, row):
        self.path, self.row, self.key = path, row, row["id"]
        self.source, self.original = store.inputs(path, row)
        self.events = {(e["phase"], e["kind"], e["mutant_id"]): e for e in row["events"]}
        self.cancel = Cancellation(path, self.key)

    def save(self, phase, kind, status, reason, payload, mutant_id=""):
        store.record(self.path, self.key, phase, kind, status, reason, payload, mutant_id)
        self.events[(phase, kind, mutant_id)] = dict(status=status, reason=reason, payload=payload)

    def measure(self, source, code):
        result = execute(source, code, detailed=True, timeout_s=self.row["timeout_s"], cancel_event=self.cancel)
        if result.get("resource_busy"):
            raise RunnerBusy("隔离执行器尚未释放；已保存进度，可继续执行")
        result.update(source_sha256=digest(source), test_sha256=digest(code))
        return result

    def phase(self, phase, code, original_baseline=None, verified_original=None):
        prior = self.events.get((phase, "baseline", ""))
        if prior:
            original, usable = prior["payload"], prior["status"] == "passed"
        else:
            original = verified_original if verified_original is not None else self.measure(self.source, code)
            usable = baseline_ok(original)
            if usable and original_baseline is not None:
                old, new = case_map(original_baseline), case_map(original)
                usable = (all(new.get(k) == v for k, v in old.items())
                          and any(new[k] == "passed" for k in new.keys() - old.keys()))
            self.save(phase, "baseline", "passed" if usable else "invalid",
                      "原始源码通过基线验证" if usable else "原版测试未通过，或新增测试没有产生有效通过节点", original)
        if not usable or self.cancel.is_set():
            return False
        for mutant in self.row["manifest"]:
            if self.cancel.is_set():
                return False
            if (phase, "observation", mutant["id"]) in self.events:
                continue
            measured = self.measure(apply_site(self.source, mutant), code)
            verdict = classify(original, measured, test_code=code)
            self.save(phase, "observation", verdict["status"], verdict["reason"],
                      {"execution": measured, "nodeids": verdict["nodeids"]}, mutant["id"])
        return not self.cancel.is_set()

    def run(self):
        if self.cancel.is_set():
            return "cancelled", "用户已终止"
        if not self.phase("before", self.original):
            return "baseline_failed", "原版基线无效或会话已终止"
        survived = [m for m in self.row["manifest"]
                    if self.events[("before", "observation", m["id"])]["status"] == "survived"]
        if not self.row["feedback_enabled"] or not survived:
            return "completed", "未启用反馈" if not self.row["feedback_enabled"] else "没有存活变异"
        previous = self.events.get(("after", "feedback", ""))
        if previous:
            feedback = previous["payload"]
        else:
            measurements = {m["id"]:self.events[("before","observation",m["id"])]["payload"]["execution"]
                            for m in survived}
            feedback = supplement(self.source, self.row["target"], self.original, survived,
                                  should_cancel=self.cancel.is_set, observations=measurements)
            self.save("after", "feedback", feedback["status"], feedback["reason"], feedback)
        if self.cancel.is_set():
            return "cancelled", "用户已终止"
        if feedback["status"] != "generated":
            return "feedback_" + feedback["status"], feedback["reason"]
        code = feedback["code"]
        if not code.startswith(self.original) or len(code) <= len(self.original):
            return "feedback_rejected", "补测必须追加到原始测试"
        green = self.events[("before", "baseline", "")]["payload"]
        validation = self.events.get(("after", "validation", ""))
        if validation:
            trial = validation["payload"]
        else:
            trial = self.measure(self.source, code)
            self.save("after", "validation", trial["status"], "全部候选在原始源码上的执行结果", trial)
        if self.cancel.is_set():
            return "cancelled", "用户已终止"
        if ("after", "selection", "") in self.events:
            selection = self.events[("after", "selection", "")]["payload"]
        else:
            selection = select_green_additions(self.original, feedback, green, trial)
            self.save("after", "selection", "selected" if selection["code"] else "rejected",
                      "依据原版测试节点选择补测，保留全部候选和未采纳原因", selection)
        chosen = selection["code"]
        if not chosen or not self.phase("after", chosen, green, trial if chosen == code else None):
            return "feedback_baseline_failed", "原始源码未通过补测验证，可查阅实际输出"
        if ("after", "impact", "") not in self.events:
            additions = {"test_generated.py::" + c["test_name"]: c for c in feedback["cases"]}
            findings = []
            for site in survived:
                observed = self.events[("after", "observation", site["id"])]
                killers = observed["payload"]["nodeids"] if observed["status"] == "killed" else []
                findings.append({
                    "mutant_id": site["id"], "line": site["line"], "before": "survived",
                    "after": observed["status"], "new_killing_cases": [additions[k] for k in killers if k in additions],
                    "nodeids": killers, "reason": observed["reason"],
                })
            self.save("after", "impact", "measured", "逐个对照原测试未检出的变异与追加断言的实际结果",
                      {"candidates":len(feedback["cases"]), "accepted":len(selection["accepted_names"]),
                       "newly_killed":sum(f["after"]=="killed" for f in findings),
                       "original_passed_nodes": [k for k, v in case_map(green).items() if v == "passed"],
                       "survivors": findings})
        return "completed", "原始测试与追加测试已在同一清单上执行"


def run_session(path, key):
    with run_lock(path):
        row = store.read(path, key, full=True)
        if row["status"] not in {"ready", "running"}:
            return store.read(path, key)
        store.state(path, key, "running")
        try:
            status, reason = Experiment(path, row).run()
        except RunnerBusy as exc:
            status, reason = "ready", str(exc)
        except Exception as exc:
            status, reason = "error", f"{type(exc).__name__}: {str(exc)[:500]}"
            store.record(path, key, "system", "failure", status, reason, {})
        store.state(path, key, status, reason)
    return store.read(path, key)


def cancel_session(path, key):
    row = store.cancel(path, key)
    if row["status"] == "running":
        try:
            with run_lock(path):
                # The previous service may have stopped before recording its terminal state.
                store.state(path, key, "cancelled", "用户已终止")
        except HTTPException as exc:
            if exc.status_code != 409:
                raise
    return store.read(path, key)
