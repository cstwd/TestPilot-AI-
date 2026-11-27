"""Run a fixed Pytest command inside an offline, read-only WASI guest."""
import json
import os
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


def empty_result():
    return dict(status="error", passed=0, failed=0, errors=0, skipped=0, cases=[], exit_code=None,
                covered_lines=None, total_lines=None, coverage_pct=None, log="", duration_ms=0)


def read_log(path):
    return path.read_bytes().decode("utf-8", errors="replace") if path.exists() else ""


def read_cases(payload, report):
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
    if (covered, total) != (None, None) and not (
        type(covered) is int and type(total) is int and 0 <= covered <= total
    ):
        raise ValueError("覆盖率计数异常")
    report.update(cases=cases, covered_lines=covered, total_lines=total,
                  environment=payload.get("environment"),
                  coverage_pct=round(100 * covered / total, 2) if total else None, **counts)


def execute(source: str, test_code: str, *, timeout_s: int = 15) -> dict:
    """Run a versioned subject and test suite. Imported text never enters host Python."""
    started = time.monotonic()
    report = empty_result()
    if type(timeout_s) is not int or not 1 <= timeout_s <= 60:
        raise ValueError("执行超时必须在 1–60 秒之间")
    if not ACTIVE.acquire(blocking=False):
        report["log"] = "隔离执行器忙，请稍后重试。"
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
            try:
                # The guest cannot spawn children. On timeout run() kills and waits for the sole worker.
                process = subprocess.run(
                    [sys.executable, "-I", str(WORKER), str(timeout_s), str(runtime / "wasm-cache")],
                    cwd=temp, env=env, stdin=subprocess.DEVNULL, capture_output=True,
                    timeout=45 + timeout_s, encoding="utf-8", errors="replace",
                )
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
                        read_cases(json.loads(tail), report)
                        if state["exit_code"] == 0 and not (report["errors"] or report["failed"]):
                            report["status"] = "passed" if report["passed"] else "skipped"
                        elif state["exit_code"] == 1 and report["failed"] and not report["errors"]:
                            report["status"] = "failed"
            except subprocess.TimeoutExpired:
                report["status"] = "timeout"
                diagnostic += "\n启动及执行总时限已到，工作进程已结束。"
            except (ValueError, TypeError, KeyError, RecursionError) as exc:
                diagnostic += f"\n执行证据无效：{exc}"
            finally:
                report["log"] = (read_log(job / "stdout.log") + "\n" + read_log(job / "stderr.log") + diagnostic).strip()
    except (OSError, UnicodeError) as exc:
        report["status"] = "error"
        report["log"] += f"\n执行器环境错误：{exc}"
    finally:
        ACTIVE.release()
        report["duration_ms"] = round((time.monotonic() - started) * 1000)
    return report
