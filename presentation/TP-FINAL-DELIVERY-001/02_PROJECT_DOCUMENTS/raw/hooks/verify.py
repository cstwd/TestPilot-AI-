"""Run the repository acceptance checks and write a reproducible text report."""
import argparse
from datetime import datetime
from pathlib import Path
import platform
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
MODULES = {
    "f01": ["tests/test_f01.py", "tests/test_project_workspace.py"],
    "f02": ["tests/test_f02.py", "tests/test_ast_studio.py"],
    "f03": ["tests/test_f03.py", "tests/test_generation_studio.py"],
    "f04": ["tests/test_f04.py", "tests/test_execution_center.py"],
    "f05": ["tests/test_f05.py", "tests/test_bug_intelligence.py"],
    "f06": ["tests/test_f06.py", "tests/test_quality_intelligence.py", "tests/test_phase02_flow.py"],
    "f13": ["tests/" + path.name for path in sorted((ROOT / "tests").glob("test_mutation_*.py"))],
    "phase05": ["tests/test_mutation_generator.py", "eval/phase05/test_manifest.py"],
    "toolchain": ["tests/test_course_toolchain.py"],
    "full": ["tests", "eval/phase05/test_manifest.py"],
}


def execute(report, args):
    report.write(f"\n$ {subprocess.list2cmdline(args)}\n")
    report.flush()
    start = time.monotonic()
    try:
        status = subprocess.run(args, cwd=ROOT, stdout=report, stderr=subprocess.STDOUT,
                                timeout=2700).returncode
    except (OSError, subprocess.TimeoutExpired) as error:
        report.write(str(error) + "\n")
        status = 1
    report.write(f"exit={status} elapsed={time.monotonic() - start:.2f}s\n")
    report.flush()
    return status == 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=MODULES, default="full")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    path = args.report.resolve()
    if not path.is_relative_to(ROOT / "reports"):
        parser.error("--report must be under reports/")
    path.parent.mkdir(parents=True, exist_ok=True)
    python = [sys.executable, "-X", "utf8", "-m"]
    commands = [
        [*python, "compileall", "-q", "main.py", "backend", "tests", "hooks", "mcp-server",
         "eval/phase05", "eval/phase06"],
        [*python, "pytest", "-q", "-s", *MODULES[args.scope]],
    ]
    if args.scope in ("f05", "full"):
        commands.append(["node", "--test", "tests/bug_diff.test.mjs"])
    with path.open("w", encoding="utf-8") as report:
        report.write(f"TestPilot WP05 verify | {datetime.now().astimezone().isoformat()}\n")
        report.write(f"{platform.platform()} | Python {platform.python_version()} | {args.scope}\n")
        results = [execute(report, command) for command in commands]
        report.write(f"outcome={'passed' if all(results) else 'failed'}\n")
    print(path)
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
