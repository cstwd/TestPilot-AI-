"""Fixed entry point executed inside WASI CPython, never by the web service."""
import json
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


def main():
    os.chdir("/work")
    sys.path.insert(0, "/work")
    cases = Cases()
    cov = coverage.Coverage(data_file=None, timid=True, config_file=False, include=["/work/subject.py"])
    cov.start()
    result = pytest.main([
        "-q", "-s", "-rA", "--color=no", "--tb=short", "--assert=plain", "--noconftest",
        "-p", "no:faulthandler", "-p", "no:logging", "-p", "no:cacheprovider", "/work/test_generated.py",
    ], plugins=[cases])
    cov.stop()
    covered = total = None
    try:
        _, statements, _, missing, _ = cov.analysis2("/work/subject.py")
        covered, total = len(statements) - len(missing), len(statements)
    except (coverage.exceptions.CoverageException, SyntaxError) as exc:
        print(f"Coverage unavailable: {exc}", file=sys.stderr)
    print("\nTESTPILOT_RESULT " + json.dumps({
        "environment": {"platform": sys.platform, "python": sys.version.split()[0],
                        "pytest": pytest.__version__, "coverage": coverage.__version__},
        "cases": [{"nodeid": name, "outcome": outcome} for name, outcome in cases.outcomes.items()],
        "covered_lines": covered, "total_lines": total,
    }), flush=True)
    return int(result)


if __name__ == "__main__":
    raise SystemExit(main())
