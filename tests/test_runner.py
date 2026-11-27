"""Black-box checks of the real WASI/Pytest pipeline and its capability limits."""
from backend.runner import ROOT, execute


def test_results_coverage_and_isolation(tmp_path):
    canary = tmp_path / "private.txt"
    canary.write_text("private", encoding="utf-8")
    source = "def inc(x):\n    if x:\n        return x + 1\n    return 0\n"
    suite = f"""
import errno
import os
import socket
import subprocess
from pathlib import Path
import pytest
from subject import inc

def test_value():
    assert inc(2) == 3

def test_bad_contract():
    assert inc(1) == 99

def test_omitted():
    pytest.skip('no contract')

def test_capabilities():
    assert not Path({str(canary)!r}).exists()
    with pytest.raises(OSError):
        Path('/work/guest-write').write_text('example')
    with pytest.raises(OSError) as net:
        socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    assert net.value.errno == errno.ENOTSUP
    with pytest.raises(OSError) as child:
        subprocess.run(['python', '-V'], check=False)
    assert child.value.errno == errno.ENOTSUP
    with pytest.raises(MemoryError):
        bytearray(300 * 1024 * 1024)
    print('WASI limits:', net.value, child.value, '300 MiB allocation denied')
"""
    result = execute(source, suite)
    assert result["status"] == "failed", result["log"]
    assert (result["passed"], result["failed"], result["skipped"], result["errors"]) == (2, 1, 1, 0), result["log"]
    assert {"nodeid": "test_generated.py::test_bad_contract", "outcome": "failed"} in result["cases"]
    assert (result["covered_lines"], result["total_lines"], result["coverage_pct"]) == (3, 4, 75)
    assert "assert inc(1) == 99" in result["log"]
    print(result["log"])
    assert canary.read_text() == "private"


def test_deadline_and_cleanup():
    before = set((ROOT / ".runtime").glob("job-*"))
    result = execute("", "def test_deadline():\n    while True:\n        pass", timeout_s=3)
    assert result["status"] == "timeout", result["log"]
    assert "deadline" in result["log"]
    assert not set((ROOT / ".runtime").glob("job-*")) - before


def test_collection_error():
    result = execute("def broken(:", "import subject\ndef test_unreachable(): pass")
    assert result["status"] == "error", result["log"]
    assert result["errors"] == 1 and result["passed"] == 0
    assert "SyntaxError" in result["log"]


def test_output_budget():
    result = execute("", "def test_output():\n    print('x' * 300000)")
    assert result["status"] == "error"
    assert "日志不完整" in result["log"]
    assert len(result["log"]) < 300000


def test_all_skipped_is_not_a_pass():
    result = execute("", "import pytest\ndef test_optional():\n    pytest.skip('unsupported')")
    assert result["status"] == "skipped", result["log"]
    assert result["exit_code"] == 0 and result["passed"] == 0 and result["skipped"] == 1
