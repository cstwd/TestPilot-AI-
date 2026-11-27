"""Run a fixed Pytest command inside an offline, read-only WASI guest."""
import json
import os
from concurrent.futures import CancelledError
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time


ROOT = Path(__file__).resolve().parents[1]
WORKER = Path(__file__).with_name("wasi_worker.py")
ACTIVE = threading.BoundedSemaphore(1)
MARKER = "\nTESTPILOT_RESULT "
SLOT_WAIT_SECONDS = 110


def empty_result(detailed=False):
    count = None if detailed else 0
    report = dict(status="error", passed=count, failed=count, errors=count, skipped=count, cases=[], exit_code=None,
                  covered_lines=None, total_lines=None, coverage_pct=None, log="", duration_ms=0)
    if detailed:
        report.update(stdout="", stderr="", diagnostic="", result_complete=False, failures=[], failure_details_omitted=0,
                      covered_branches=None, total_branches=None, branch_pct=None)
    return report


def read_log(path):
    return path.read_bytes().decode("utf-8", errors="replace") if path.exists() else ""


def check_coverage(covered, total):
    if (covered, total) != (None, None) and not (
        type(covered) is int and type(total) is int and 0 <= covered <= total
    ):
        raise ValueError("覆盖率计数异常")


def read_details(payload, report, seen):
    failures = payload["failures"]
    omitted = payload["failure_details_omitted"]
    if not isinstance(failures, list) or type(omitted) is not int or omitted < 0:
        raise ValueError("失败证据格式异常")
    for failure in failures:
        if (failure["nodeid"] not in seen or failure["phase"] not in {"setup", "call", "teardown", "collect"}
                or not isinstance(failure["message"], str) or not isinstance(failure["exception_type"], str)
                or not isinstance(failure["frames"], list)
                or not (failure["assertion_diff"] is None or isinstance(failure["assertion_diff"], str))):
            raise ValueError("异常记录格式错误")
        for frame in failure["frames"]:
            if (type(frame["line"]) is not int or frame["line"] < 1
                    or not all(isinstance(frame[key], str) for key in ("path", "function", "source"))):
                raise ValueError("回溯帧格式错误")
    covered, total = payload["covered_branches"], payload["total_branches"]
    check_coverage(covered, total)
    report.update(failures=failures, failure_details_omitted=omitted,
                  covered_branches=covered, total_branches=total, result_complete=True,
                  branch_pct=round(100 * covered / total, 2) if total else None)


def read_cases(payload, report, detailed=False):
    cases = payload["cases"]
    if not isinstance(cases, list) or not cases:
        raise ValueError("没有可核对的 Pytest 个案记录")
    counts = dict(passed=0, failed=0, errors=0, skipped=0)
    seen = set()
    for case in cases:
        outcome, nodeid = case["outcome"], case["nodeid"]
        if outcome not in {"passed", "failed", "error", "skipped"} or not isinstance(nodeid, str) or nodeid in seen:
            raise ValueError("Pytest 个案记录格式异常")
        seen.add(nodeid)
        counts["errors" if outcome == "error" else outcome] += 1
    covered, total = payload["covered_lines"], payload["total_lines"]
    check_coverage(covered, total)
    if detailed:
        read_details(payload, report, seen)
    report.update(cases=cases, covered_lines=covered, total_lines=total,
                  environment=payload.get("environment"),
                  coverage_pct=round(100 * covered / total, 2) if total else None, **counts)


def run_worker(command, directory, env, timeout, cancel_event):
    options = dict(cwd=directory, env=env, stdin=subprocess.DEVNULL, encoding="utf-8", errors="replace")
    if cancel_event is None:
        return subprocess.run(command, capture_output=True, timeout=timeout, **options)
    if cancel_event.is_set():
        raise CancelledError
    deadline = time.monotonic() + timeout
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **options) as process:
        try:
            while True:
                if cancel_event.is_set():
                    raise CancelledError
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise subprocess.TimeoutExpired(command, timeout)
                try:
                    stdout, stderr = process.communicate(timeout=min(0.2, remaining))
                    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
                except subprocess.TimeoutExpired:
                    continue
        except BaseException:
            # The guest cannot create children. Reap our one worker before removing its job.
            if process.poll() is None:
                process.kill()
            process.communicate()
            raise


def acquire_slot(cancel_event):
    if cancel_event is None:
        return "acquired" if ACTIVE.acquire(blocking=False) else "busy"
    deadline = time.monotonic() + SLOT_WAIT_SECONDS
    while not cancel_event.is_set():
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return "busy"
        if ACTIVE.acquire(timeout=min(remaining, 0.2)):
            return "acquired"
    return "cancelled"


def execute(source: str, test_code: str, *, timeout_s: int = 15, detailed: bool = False,
            cancel_event: threading.Event | None = None) -> dict:
    """Run a versioned subject and test suite. Imported text never enters host Python."""
    started = time.monotonic()
    report = empty_result(detailed)
    if type(timeout_s) is not int or not 1 <= timeout_s <= 60:
        raise ValueError("执行超时必须在 1–60 秒之间")
    slot = acquire_slot(cancel_event)
    if slot != "acquired":
        report["log"] = "隔离执行器忙，请稍后重试。" if slot == "busy" else "等待执行槽时已取消。"
        if slot == "cancelled":
            report["status"] = "cancelled"
        if cancel_event is not None:
            report["resource_busy"] = slot == "busy"
            report["duration_ms"] = round((time.monotonic() - started) * 1000)
        if detailed:
            report["diagnostic"] = report["log"]
        return report
    try:
        runtime = ROOT / ".runtime"
        runtime.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="job-", dir=runtime) as temp:
            job = Path(temp)
            work = job / "work"
            work.mkdir()
            (work / "subject.py").write_text(source, encoding="utf-8")
            (work / "test_generated.py").write_text(test_code, encoding="utf-8")
            env = dict(os.environ, TMPDIR=temp, TMP=temp, TEMP=temp, PYTHONIOENCODING="utf-8")
            diagnostic = ""
            result_marker_found = False
            command = [sys.executable, "-I", str(WORKER), str(timeout_s), str(runtime / "wasm-cache")]
            if detailed:
                command.append("detailed")
            try:
                process = run_worker(command, temp, env, 45 + timeout_s, cancel_event)
                diagnostic = process.stderr
                if process.returncode:
                    diagnostic += f"\n隔离执行进程退出 {process.returncode}。"
                else:
                    state = json.loads(process.stdout)
                    report["exit_code"] = state["exit_code"]
                    if state["cut"]:
                        diagnostic += "\n输出达到上限，本次日志不完整，结果无效。"
                    elif state["trapped"]:
                        report["status"] = "timeout" if state["trapped"] == "deadline" else "error"
                        diagnostic += f"\nWASI 停止执行：{state['trapped']}"
                    else:
                        raw = read_log(job / "stdout.log")
                        _, marker, tail = raw.rpartition(MARKER)
                        if not marker:
                            raise ValueError("未收到 Pytest 完成记录")
                        read_cases(json.loads(tail), report, detailed)
                        result_marker_found = True
                        if state["exit_code"] == 0 and not (report["errors"] or report["failed"]):
                            report["status"] = "passed" if report["passed"] else "skipped"
                        elif state["exit_code"] == 1 and report["failed"] and not report["errors"]:
                            report["status"] = "failed"
            except CancelledError:
                report["status"] = "cancelled"
                diagnostic += "\n已取消隔离执行。"
            except subprocess.TimeoutExpired:
                report["status"] = "timeout"
                diagnostic += "\n启动及执行总时限已到，工作进程已结束。"
            except (ValueError, TypeError, KeyError, RecursionError) as exc:
                diagnostic += f"\n执行证据无效：{exc}"
            finally:
                stdout, stderr = read_log(job / "stdout.log"), read_log(job / "stderr.log")
                if detailed:
                    if result_marker_found:
                        stdout = stdout.rpartition(MARKER)[0]
                    report.update(stdout=stdout, stderr=stderr, diagnostic=diagnostic.strip())
                report["log"] = (stdout + "\n" + stderr + diagnostic).strip()
    except (OSError, UnicodeError) as exc:
        report["status"] = "error"
        report["log"] += f"\n执行器环境错误：{exc}"
        if detailed:
            report["diagnostic"] = report["log"]
    finally:
        ACTIVE.release()
        report["duration_ms"] = round((time.monotonic() - started) * 1000)
    return report
