"""Fixed-input smoke test. This module accepts no imported code or commands."""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run_self_test() -> tuple[bool, str]:
    source = Path(__file__).with_name("sample_case.py")
    with tempfile.TemporaryDirectory(prefix="testpilot-self-test-") as directory:
        work = Path(directory)
        shutil.copyfile(source, work / "test_sample.py")
        (work / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
        env = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR") if key in os.environ}
        env.update(PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", TEMP=directory, TMP=directory, TMPDIR=directory)
        try:
            result = subprocess.run(
                [sys.executable, "-I", "-B", "-m", "pytest", "-q", "--noconftest",
                 "-p", "no:cacheprovider", "-c", "pytest.ini", "test_sample.py"],
                cwd=directory, env=env, capture_output=True, timeout=15,
                stdin=subprocess.DEVNULL, encoding="utf-8", errors="replace",
            )
        except subprocess.TimeoutExpired:
            return False, "自检超过 15 秒，已终止 Pytest 子进程。"
        output = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
        return result.returncode == 0, output[-2000:]
