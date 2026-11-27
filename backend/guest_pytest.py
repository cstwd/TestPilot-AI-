"""Fixed entry point executed inside WASI CPython, never by the web service."""
import json
import linecache
import os
import sys

import coverage
import pytest


class Cases:
    """Receive real Pytest reports, including collection and fixture errors."""

    def __init__(self):
        self.outcomes = {}

    def pytest_collectreport(self, report):
        if report.failed or report.skipped:
            self.outcomes[report.nodeid or "(collection)"] = "error" if report.failed else "skipped"

    def pytest_runtest_logreport(self, report):
        if report.failed:
            self.outcomes[report.nodeid] = "failed" if report.when == "call" else "error"
        elif report.skipped:
            self.outcomes.setdefault(report.nodeid, "skipped")
        elif report.when == "call":
            self.outcomes.setdefault(report.nodeid, "passed")


class FailureDetails:
    """Collect bounded evidence from pytest's actual exception and traceback objects."""

    def __init__(self):
        self.failures = []
        self.remaining_bytes = 32 * 1024
        self.omitted = 0

    def pytest_exception_interact(self, node, call, report):
        if not report.failed or call.excinfo is None:
            return
        if self.remaining_bytes <= 0:
            self.omitted += 1
            return
        exc = call.excinfo
        if call.when == "collect" and isinstance(exc.value, pytest.Collector.CollectError):
            cause = exc.value.__cause__
            if cause is not None:
                exc = pytest.ExceptionInfo.from_exception(cause)
        frames = []
        for entry in exc.traceback:
            path = str(entry.path)
            if path.startswith("/work/"):
                line = entry.lineno + 1
                frames.append({"path": path.removeprefix("/work/"), "line": line,
                               "function": entry.name, "source": linecache.getline(path, line).strip()[:320]})
        if not frames and exc.traceback:
            entry = exc.traceback[-1]
            frames.append({"path": str(entry.path), "line": entry.lineno + 1, "function": entry.name,
                           "source": linecache.getline(str(entry.path), entry.lineno + 1).strip()[:320]})
        if isinstance(exc.value, SyntaxError) and exc.value.filename and exc.value.lineno:
            frames.append({"path": exc.value.filename.removeprefix("/work/"), "line": exc.value.lineno,
                           "function": "(parse)", "source": (exc.value.text or "").strip()[:320]})
        message = str(exc.value)[:1200]
        detail = {"nodeid": report.nodeid or "(collection)", "phase": call.when,
                  "exception_type": exc.typename, "message": message, "frames": frames[-8:],
                  "assertion_diff": message if isinstance(exc.value, AssertionError) else None}
        size = len(json.dumps(detail).encode("utf-8"))
        if size <= self.remaining_bytes:
            self.failures.append(detail)
            self.remaining_bytes -= size
        else:
            self.omitted += 1


def main():
    os.chdir("/work")
    sys.path.insert(0, "/work")
    cases = Cases()
    detailed = sys.argv[1:] == ["detailed"]
    details = FailureDetails()
    if detailed:
        sys.dont_write_bytecode = True
    cov = coverage.Coverage(data_file=None, timid=True, branch=detailed, config_file=False,
                            include=["/work/subject.py"])
    cov.start()
    result = pytest.main([
        "-q", "-s", "-rA", "--color=no", "--tb=short", "--assert=rewrite" if detailed else "--assert=plain",
        "--noconftest",
        "-p", "no:faulthandler", "-p", "no:logging", "-p", "no:cacheprovider", "/work/test_generated.py",
    ], plugins=[cases, details] if detailed else [cases])
    cov.stop()
    covered = total = None
    branches = total_branches = None
    try:
        _, statements, _, missing, _ = cov.analysis2("/work/subject.py")
        covered, total = len(statements) - len(missing), len(statements)
        if detailed:
            stats = cov.branch_stats("/work/subject.py")
            total_branches = sum(exits for exits, _ in stats.values())
            branches = sum(taken for _, taken in stats.values())
    except (coverage.exceptions.CoverageException, SyntaxError) as exc:
        print(f"Coverage unavailable: {exc}", file=sys.stderr)
    evidence = {
        "environment": {"platform": sys.platform, "python": sys.version.split()[0],
                        "pytest": pytest.__version__, "coverage": coverage.__version__},
        "cases": [{"nodeid": name, "outcome": outcome} for name, outcome in cases.outcomes.items()],
        "covered_lines": covered, "total_lines": total,
    }
    if detailed:
        evidence.update(covered_branches=branches, total_branches=total_branches, failures=details.failures,
                        failure_details_omitted=details.omitted)
    print("\nTESTPILOT_RESULT " + json.dumps(evidence), flush=True)
    return int(result)


if __name__ == "__main__":
    raise SystemExit(main())
