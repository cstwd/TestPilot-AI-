
"""Exercise Phase 07 from real HTTP and Edge through the repository WASI runner."""
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
import time
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener
from uuid import uuid4

from playwright.sync_api import expect, sync_playwright
import pytest

from backend.demo_lab import lock_path, run_record, workspace_path
from backend.engine_history import stamp
from backend.store import exclusive_file
from test_dashboard import app_url
from test_startup import running_server, vacant_port


RECEIPTS = Path(__file__).resolve().parents[1] / "reports" / "phase07"
API = "/api/demo-lab"
CASES = [
    ("unit_scaling", True, "buggy"),
    ("calculator", True, "good"),
    ("binary_search", False, "buggy"),
    ("volume_discount", False, "buggy"),
    ("booking_timezones", False, "challenge"),
    ("member_checkout", False, "challenge"),
    ("filtered_pagination", False, "challenge"),
]


def http(url, path, body=None, expected=200):
    request = Request(url + path, data=None if body is None else json.dumps(body).encode(),
                      headers={"Content-Type": "application/json"})
    client = build_opener(ProxyHandler({}))
    try:
        with client.open(request, timeout=20) as response:
            status, payload = response.status, response.read()
    except HTTPError as error:
        status, payload = error.code, error.read()
    assert status == expected, (path, status, payload[:600])
    return json.loads(payload)


def wait(url, receipt):
    deadline = time.monotonic() + 150
    while receipt["status"] == "running" and time.monotonic() < deadline:
        time.sleep(.4)
        receipt = http(url, f"{API}/runs/{receipt['id']}")
    assert receipt["status"] != "running", receipt["stages"]
    return receipt


def capture(filename, value):
    if os.environ.get("TESTPILOT_PHASE07_CAPTURE") == "1":
        RECEIPTS.mkdir(parents=True, exist_ok=True)
        (RECEIPTS / filename).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                                        encoding="utf-8", newline="\n")


def test_frozen_sample_surface(app_url):
    records = http(app_url, API + "/samples")
    assert records["active"] is None
    counts = Counter(row["tier"] for row in records["samples"])
    assert counts == {"good": 25, "buggy": 50, "challenge": 25}
    assert len({row["domain"] for row in records["samples"]}) == 6
    for row in records["samples"]:
        item = http(app_url, f"{API}/samples/{row['name']}")
        assert hashlib.sha256(item["source"].encode()).hexdigest() == row["sha256"]
        assert set(item["contract"]) == {"provenance", "code", "cases"}
        assert {"source", "corrected", "targets", "docstring"} <= item.keys()
        assert isinstance(item["corrected"], str) == (row["tier"] != "good")
        if item["corrected"] is not None:
            assert hashlib.sha256(item["corrected"].encode()).hexdigest() == row["repair_sha256"]
        assert "def test_" in item["contract"]["code"]
        assert not {"tests", "defects", "ground_truth", "corrected_path"} & item.keys()
    http(app_url, "/api/demo-lab/samples/ground_truth.json", expected=404)
    http(app_url, "/demo/TestPilot-Demo-Lab/reference/ground_truth.json", expected=404)
    http(app_url, API + "/samples/calculator/runs", {"source": "print('unsupported')"}, expected=422)
    print("PHASE07_CATALOG", json.dumps(dict(counts), sort_keys=True), "domains=6, source hashes=100, repair hashes=75")


def assert_reports(app_url, item, mutant):
    assert item["status"] == "completed", item["stages"]
    assert item["analysis"]["static"]["valid"]
    assert item["analysis"]["ai"]["status"] == "not_requested"
    assert item["suite"]["provenance"] == "classroom"
    original = item["execution"]
    assert original["result_complete"]
    assert original["file_id"] == item["original"]["id"]
    assert original["suite_id"] == item["suite"]["id"]
    assert original["log"]
    if item["sample_info"]["tier"] != "good":
        after = item["regression"]
        assert (original["status"], after["status"], item["bug"]["status"]) == ("failed", "passed", "resolved")
        assert original["failed"] == 1 and after["passed"] == 1
        assert after["result_complete"]
        assert {c["nodeid"] for c in original["cases"]} == {c["nodeid"] for c in after["cases"]}
        assert item["finding"]["verdict"] == "verified" and item["finding"]["frames"]
        assert original["suite_id"] == after["suite_id"] and original["id"] != after["id"]
        assert item["original"]["revision"] == 1 and item["corrected"]["revision"] == 2
        assert item["quality"]["regression"]["bugs"][0]["id"] == item["bug"]["id"]
        assert http(app_url, f"{API}/runs/{item['id']}/quality/regression") == item["quality"]["regression"]
    else:
        assert original["status"] == "passed" and item["stages"]["regression"]["status"] == "skipped"
    if mutant:
        result = item["mutation"]
        assert result["result"]["status"] == "completed"
        before = result["result"]["before"]
        assert before["total"] > 0 and before["unrun"] == 0
        assert result["effective"]["denominator"] == before["total"] - before["execution_error"]
        assert result["result"]["test_sha256"] == item["suite"]["sha256"]
        assert http(app_url, f"{API}/runs/{item['id']}/mutation") == result["result"]
    assert http(app_url, f"{API}/runs/{item['id']}/export") == item


def test_real_seven_sample_workflows(app_url):
    evidence = []
    for sample, mutate, tier in CASES:
        path = f"{API}/samples/{sample}/runs"
        receipt = http(app_url, path, {"mode": "template", "mutation": mutate}, expected=202)
        assert receipt["sample_info"]["tier"] == tier
        if sample == "unit_scaling":
            rejection = http(app_url, path, {"mode": "template", "mutation": False}, expected=409)
            assert rejection["detail"]["id"] == receipt["id"]
        item = wait(app_url, receipt)
        assert_reports(app_url, item, mutate)
        evidence.append(item)
        print("PHASE07_RUN", sample, item["id"], item["execution"]["status"],
              item.get("regression", {}).get("status"), item.get("mutation", {}).get("all_score_pct"), flush=True)
    receipt = http(app_url, f"{API}/samples/unit_scaling/runs", {"mutation": False}, expected=202)
    repeat = wait(app_url, receipt)
    assert_reports(app_url, repeat, False)
    assert repeat["id"] != evidence[0]["id"]
    assert repeat["project"]["id"] != evidence[0]["project"]["id"]
    history = http(app_url, f"{API}/samples/unit_scaling/runs")
    assert [item["id"] for item in history] == [repeat["id"], evidence[0]["id"]]
    assert http(app_url, f"{API}/runs/{evidence[0]['id']}/export") == evidence[0]
    assert len(http(app_url, API + "/runs")) == 8
    assert http(app_url, "/api/projects") == []
    http(app_url, "/api/runs/1", expected=404)
    capture("end-to-end.json", {"sample_runs": evidence, "rerun": repeat})


def test_restart_ownership_and_ai_rejection(tmp_path, monkeypatch):
    """Exercise genuine service isolation using a staged crash row and an absent attestation."""
    monkeypatch.setenv("TESTPILOT_MODEL_RUNTIME", str(tmp_path / "no-model-attestation"))
    data = tmp_path / "workspace"
    db = workspace_path(data / "testpilot.sqlite3")
    crashed_id = str(uuid4())
    with running_server(vacant_port(), data, tmp_path / "first.log", "demo"):
        with exclusive_file(lock_path(db), "occupied"):
            with sqlite3.connect(db) as connection:
                connection.execute("INSERT INTO demo_lab_runs VALUES (?,?,?,?,?,?,?)",
                                   (crashed_id, "calculator", "template", "running", stamp(), stamp(),
                                    json.dumps({"stages": {"execution": {"status": "running"}}})))
            with running_server(vacant_port(), data, tmp_path / "contending.log", "demo") as contender:
                blocked = http(contender, f"{API}/samples/calculator/runs", {}, expected=409)
                assert blocked["detail"]["id"] == crashed_id
                assert run_record(db, crashed_id)["status"] == "running"
    with running_server(vacant_port(), data, tmp_path / "restarted.log", "demo") as restarted:
        previous = http(restarted, f"{API}/runs/{crashed_id}/export")
        assert previous["status"] == previous["stages"]["execution"]["status"] == "interrupted"
        pending = http(restarted, f"{API}/samples/calculator/runs", {"mode": "ai"}, expected=202)
        rejected = wait(restarted, pending)
        assert rejected["status"] == "failed" and rejected["analysis"]["ai"]["status"] == "unavailable"
        assert rejected["stages"]["analysis"]["status"] == "failed"
        assert rejected["stages"]["generation"]["status"] == "skipped"
        assert "suite" not in rejected and "execution" not in rejected
        assert http(restarted, f"{API}/runs/{rejected['id']}/export") == rejected
        capture("failure-paths.json", {"restart_fixture": previous, "ai_missing_attestation": rejected})


def test_unusable_lab_database_preserves_workbench(tmp_path):
    data = tmp_path / "workspace"
    data.mkdir()
    database = workspace_path(data / "testpilot.sqlite3")
    invalid = b"case fixture: invalid SQLite database"
    database.write_bytes(invalid)
    with running_server(vacant_port(), data, tmp_path / "isolated.log", "demo") as url:
        assert http(url, "/api/projects") == []
        service = http(url, f"{API}/samples", expected=503)
        assert "Demo Lab 独立数据库" in service["detail"]
        assert database.read_bytes() == invalid


def screenshot(page, filename):
    if os.environ.get("TESTPILOT_PHASE07_CAPTURE") == "1":
        RECEIPTS.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=RECEIPTS / filename, full_page=True, animations="disabled")


def test_edge_full_product_flow(app_url):
    channel = os.environ.get("TESTPILOT_BROWSER_CHANNEL", "msedge" if sys.platform == "win32" else "chromium")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=channel, headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(app_url)
        page.get_by_role("link", name="打开 Demo Lab").click()
        expect(page.locator("#lab-count")).to_have_text("100 / 100")
        expect(page.locator("#lab-name")).to_have_text("unit_scaling.py")
        page.locator("#lab-tier").select_option("buggy")
        expect(page.locator("#lab-count")).to_have_text("50 / 100")
        page.locator("#lab-domain").select_option("math")
        page.locator("#lab-search").fill("unit_scaling")
        expect(page.locator("#lab-count")).to_have_text("1 / 100")
        page.get_by_role("button", name="公开合同").click()
        expect(page.locator("#lab-contract")).to_contain_text("assert target(1250) == 1.25")
        page.get_by_role("button", name="源码", exact=True).click()
        expect(page.locator("#lab-source")).to_contain_text("修复版本")
        screenshot(page, "01-source-and-filters.png")
        page.get_by_role("button", name="运行演示").click()
        expect(page.locator("#lab-run-state")).to_contain_text("完成", timeout=120000)
        expect(page.get_by_role("heading", name="F13 变异结果")).to_be_visible()
        expect(page.locator("#lab-result")).to_contain_text("已关闭")
        expect(page.locator("#lab-result")).to_contain_text("AssertionError")
        screenshot(page, "02-regression-and-mutation.png")
        with page.expect_download() as event:
            page.get_by_role("link", name="下载完整 JSON").click()
        downloaded = json.loads(event.value.path().read_text(encoding="utf-8"))
        assert downloaded["bug"]["status"] == "resolved" and downloaded["mutation"]["result"]["before"]["total"] > 0
        capture("edge-run.json", downloaded)
        page.get_by_role("button", name="运行历史").click()
        page.locator("[data-run]").first.click()
        expect(page.get_by_role("link", name="下载完整 JSON")).to_be_visible()
        page.reload()
        expect(page.locator("#lab-result")).to_be_visible()
        expect(page.locator("#lab-run-state")).to_contain_text(downloaded["id"][:8])
        page.get_by_role("button", name="报告中心").click()
        expect(page.locator("#lab-report-center")).to_be_visible()
        expect(page.locator("#lab-reports-list")).to_contain_text("unit_scaling.py")
        screenshot(page, "04-report-center.png")
        page.locator("[data-report-sample]").first.click()
        expect(page.locator("#lab-result")).to_be_visible()
        page.set_viewport_size({"width": 390, "height": 884})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        screenshot(page, "03-mobile-report.png")
        assert errors == []
        print("PHASE07_EDGE", browser.version, downloaded["id"])
        browser.close()
