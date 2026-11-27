"""WP08-F06-001. Read and export real run snapshots through the Edge quality workspace."""
import json
import os
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect

from backend import generation
from test_ast_studio import post_json, record, studio, upload
from test_dashboard import app_url


SUBJECT = """def magnitude(x: float) -> float:
    \"\"\"Return a non-negative measurement.

    >>> magnitude(-2)
    2
    >>> magnitude(-3)
    3
    \"\"\"
    return x
"""

MIXED_TESTS = """import pytest

@pytest.fixture
def unavailable():
    raise RuntimeError("F06 fixture setup failure")

def test_ok():
    assert True

def test_failed():
    assert False

def test_error(unavailable):
    assert True

def test_skipped():
    pytest.skip("F06 explicit skip")
"""


def capture(page, name):
    target = os.environ.get("TESTPILOT_F06_CAPTURE_DIR")
    if target:
        folder = Path(target)
        folder.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=folder / f"{name}.png", animations="disabled")


def report_url(run_id):
    return f"/api/runs/{run_id}/report"


def fetch_report(page, run_id):
    response = page.request.get(report_url(run_id))
    assert response.ok, response.text()
    return response.json()


def open_report(page, data):
    page.goto(f"/workbench/reports?project={data['project']['id']}&file={data['source']['id']}&run={data['run']['id']}")


def download_snapshot(page, dest, data):
    with page.expect_download() as pending:
        page.get_by_role("link", name="下载 JSON 报告", exact=True).click()
    download = pending.value
    assert download.suggested_filename == f"testpilot-run-{data['run']['id']}.json"
    download.save_as(dest)
    assert json.loads(dest.read_text(encoding="utf-8")) == data


def show_matches(page, data):
    project, run, source, suite, q = (data[key] for key in ("project", "run", "source", "suite", "quality"))
    measured = q["passed"] + q["failed"] + q["errors"]
    rate = f"{q['pass_rate_pct']:g}%" if q["pass_rate_pct"] is not None else "无可计算的用例"
    coverage = f"{q['coverage_pct']:g}%" if q["coverage_pct"] is not None else "未采集"
    expect(page.locator("#report")).to_be_visible()
    expect(page.locator("#report-origin")).to_have_text(f"{source['filename']} v{source['revision']}")
    expect(page.locator("#quality-run-number")).to_have_text(f"运行 #{run['id']}")
    expect(page.locator('[data-metric="pass-rate"] dd').first).to_have_text(rate)
    expect(page.locator('[data-metric="pass-rate"] .quality-metric-note')).to_contain_text(f"{q['passed']} / {measured}")
    expect(page.locator('[data-metric="total"] dd').first).to_have_text(str(q["total"]))
    expect(page.locator('[data-metric="coverage"] dd').first).to_have_text(coverage)
    if q["covered_lines"] is not None and q["total_lines"] is not None:
        expect(page.locator('[data-metric="coverage"] .quality-metric-note')).to_contain_text(f"{q['covered_lines']} / {q['total_lines']} 行")
    expect(page.locator('[data-metric="defects"] dd').first).to_have_text(str(len(data["bugs"])))
    expect(page.locator("#quality-case-legend strong")).to_have_text(
        [f"{q[key]} / {q['total']}" for key in ("passed", "failed", "errors", "skipped")])
    expect(page.locator("#quality-identities dd")).to_have_text([
        f"#{run['id']}", f"#{project['id']}", f"#{source['id']}", f"v{source['revision']}",
        f"#{suite['id']}", f"#{suite['file_id']}", run["status"], f"{run['duration_ms']} ms",
    ])
    expect(page.locator("#report-hashes")).to_contain_text(source["sha256"])
    expect(page.locator("#report-hashes")).to_contain_text(suite["sha256"])
    for bug in data["bugs"]:
        box = page.locator(f"[data-bug-id='{bug['id']}']")
        expect(box).to_contain_text(bug["title"])
        expect(box).to_contain_text(bug["nodeid"])
        expect(box).to_contain_text("已解决" if bug["status"] == "resolved" else "待修复")
        for item in bug["regressions"]:
            row = box.locator(f"[data-regression-id='{item['run_id']}']")
            expect(row).to_contain_text(f"运行 #{item['run_id']} · v{item['revision']} (#{item['file_id']})")
            expect(row).to_contain_text("判定 已解决" if item["status"] == "resolved" else "判定 待修复")
    expect(page.locator("#report-bugs .quality-issue")).to_have_count(len(data["bugs"]))
    record("F06_REPORT", {
        "project": project["id"], "file": source["id"], "version": source["revision"], "run": run["id"],
        "suite": suite["id"], "status": run["status"], "quality": q,
        "bugs": [{"id": row["id"], "status": row["status"], "regression_ids": [r["run_id"] for r in row["regressions"]]}
                 for row in data["bugs"]],
    })


def test_real_report_comparison_and_export_snapshot(studio, tmp_path):
    page = studio
    other_project = post_json(page, "/api/projects", {"name": "独立项目"})
    project = post_json(page, "/api/projects", {"name": "Telemetry Lab"})
    first = upload(page, project["id"], "measurements.py", SUBJECT)
    suite = post_json(page, f"/api/files/{first['id']}/suites", {"target": "magnitude", "mode": "template"})
    original = page.request.get(f"/api/runs/{suite['initial_run']['id']}").json()
    assert original["status"] == "failed" and original["failed"] == 2
    failure = next(case for case in original["cases"] if case["outcome"] == "failed")
    bug = post_json(page, f"/api/runs/{original['id']}/bugs",
                    {"title": "负数遥测值应返回绝对值", "nodeid": failure["nodeid"]})
    snapshot = fetch_report(page, original["id"])

    page.goto(f"/workbench/runs?project={project['id']}&file={first['id']}&run={original['id']}&suite={suite['id']}")
    page.locator("#to-report").click()
    show_matches(page, snapshot)
    expect(page.locator("#report-history [aria-current=page]")).to_have_attribute("data-run-id", str(original["id"]))
    capture(page, "desktop-failed")

    fixed = upload(page, project["id"], "measurements.py", SUBJECT.replace("return x", "return abs(x)"))
    saved = post_json(page, f"/api/bugs/{bug['id']}/regressions", {"file_id": fixed["id"]})
    [regression] = saved["regressions"]
    assert saved["status"] == "resolved" and regression["status"] == "resolved"
    latest = fetch_report(page, original["id"])
    passed = fetch_report(page, regression["run_id"])
    assert passed["run"]["status"] == "passed" and passed["quality"]["pass_rate_pct"] == 100
    assert latest["bugs"][0]["status"] == "resolved" and snapshot["bugs"][0]["status"] == "open"
    original_export = page.request.get(report_url(original["id"]) + "/export")
    assert original_export.ok and original_export.json() == latest
    assert "attachment" in original_export.headers["content-disposition"]

    # A concurrent regression updates the server; the two views and download stay on the loaded snapshot.
    download_snapshot(page, tmp_path / "open.json", snapshot)
    page.get_by_role("button", name="HTML 报告", exact=True).click()
    expect(page.locator("body")).to_have_attribute("data-report-view", "html")
    assert parse_qs(urlsplit(page.url).query)["view"] == ["html"]
    show_matches(page, snapshot)
    download_snapshot(page, tmp_path / "open-html.json", snapshot)
    page.get_by_role("button", name="返回工作台").click()
    page.reload()
    show_matches(page, latest)
    expect(page.locator("#quality-defect-legend")).to_contain_text("已解决")
    expect(page.locator("#quality-defect-legend strong")).to_have_text("1 / 1")
    page.get_by_role("button", name="指标口径").click()
    expect(page.locator("#metric-notes-drawer")).to_be_visible()
    expect(page.locator("#quality-definitions")).to_contain_text("跳过不进入通过率")
    expect(page.locator("#metric-notes")).to_have_text(latest["metric_notes"])
    capture(page, "desktop-definitions")
    page.get_by_role("button", name="关闭指标口径").click()

    page.get_by_label("对照运行", exact=True).select_option(str(regression["run_id"]))
    expect(page.locator("#compare-current")).to_contain_text("measurements.py v1")
    expect(page.locator("#compare-other")).to_contain_text("measurements.py v2")
    expect(page.locator("#compare-metrics tr").first).to_contain_text("60% · 3/5")
    expect(page.locator("#compare-metrics tr").first).to_contain_text("100% · 5/5")
    expect(page.locator('[data-metric="pass-rate"] dd').first).to_have_text("60%")
    capture(page, "desktop-comparison")
    download_snapshot(page, tmp_path / "resolved.json", latest)

    page.get_by_label("筛选文件版本").select_option(str(fixed["id"]))
    expect(page.locator("#report-history a")).to_have_count(1)
    page.get_by_label("筛选运行状态").select_option("failed")
    expect(page.locator("#quality-history-empty")).to_contain_text("没有匹配")
    page.get_by_label("筛选运行状态").select_option("passed")
    page.locator(f"#report-history [data-run-id='{regression['run_id']}']").click()
    show_matches(page, passed)
    expect(page.locator("#report-history [aria-current=page]")).to_have_attribute("data-run-id", str(regression["run_id"]))
    page.reload()
    show_matches(page, passed)
    capture(page, "desktop-passed")
    page.get_by_role("button", name="HTML 报告", exact=True).click()
    show_matches(page, passed)
    expect(page.get_by_role("button", name="打印 / PDF")).to_be_visible()
    capture(page, "desktop-html-report")
    page.emulate_media(media="print")
    expect(page.locator("#quality-explorer")).to_be_hidden()
    show_matches(page, passed)
    pdf = page.pdf(format="A4")
    assert pdf.startswith(b"%PDF-") and len(pdf) > 5000
    page.emulate_media(media="screen")
    page.reload()
    expect(page.locator("body")).to_have_attribute("data-report-view", "html")
    show_matches(page, passed)
    page.get_by_role("button", name="返回工作台").click()

    for width, height in ((1440, 900), (1024, 768), (768, 1024), (390, 844)):
        page.set_viewport_size({"width": width, "height": height})
        assert page.evaluate("document.documentElement.scrollWidth === innerWidth")
        size = round(page.locator(".quality-main").bounding_box()["width"])
        assert size > 300
        record("F06_VIEW", {"width": width, "height": height, "main": size, "engine": page.context.browser.version})
        if width <= 768:
            page.locator(".quality-jumps a[href='#quality-report-context']").click()
            capture(page, "mobile-metrics" if width == 390 else "tablet-metrics")
    page.locator(".quality-jumps a[href='#quality-evidence']").click()
    capture(page, "mobile-evidence")
    page.locator(f"#report-bugs [data-bug-id='{bug['id']}'] a").first.click()
    expect(page.locator("#bug-state")).to_have_text("已解决")
    open_report(page, passed)
    page.locator("#report-run").click()
    expect(page.locator("#exec-run-id")).to_have_text(f"#{regression['run_id']}")
    open_report(page, passed)
    page.locator("#project").select_option(str(other_project["id"]))
    expect(page.locator("#quality-empty")).to_contain_text("项目尚无运行记录")
    page.goto(f"/workbench/reports?project={other_project['id']}&run={original['id']}")
    expect(page.locator("#quality-empty")).to_contain_text("指定运行不属于当前项目")
    expect(page.locator("#quality-actions")).to_be_hidden()


def store_sample_suite(tmp_path, file, target, tests):
    class FixedSampleAdapter:
        def generate(self, source, name):
            assert source == file["source"] and name == target
            return tests, []

    # Save a trusted test fixture to this run's real temporary database. The actual
    # F04 endpoint runs it in WASI; coverage, case outcomes and reports are unmocked.
    state = SimpleNamespace(db_path=tmp_path / "testpilot.sqlite3", generators={"template": FixedSampleAdapter()})
    request = SimpleNamespace(app=SimpleNamespace(state=state))
    return generation.generate(file["id"], generation.GenerateInput(target=target), request)


def run_sample(page, tmp_path, file, target, tests):
    suite = store_sample_suite(tmp_path, file, target, tests)
    run = post_json(page, f"/api/suites/{suite['id']}/runs", {"file_id": file["id"]})
    return fetch_report(page, run["id"])


def test_zero_and_missing_metrics_from_real_wasi(studio, tmp_path):
    page = studio
    project = post_json(page, "/api/projects", {"name": "质量口径验收"})
    file = upload(page, project["id"], "worker.py", "def sample():\n    return 7\n")
    mixed = run_sample(page, tmp_path, file, "sample", MIXED_TESTS)
    q = mixed["quality"]
    assert mixed["run"]["status"] == "error"
    assert (q["passed"], q["failed"], q["errors"], q["skipped"], q["total"]) == (1, 1, 1, 1, 4)
    assert (q["pass_rate_pct"], q["coverage_pct"], q["covered_lines"], q["total_lines"]) == (33.33, 0, 0, 2)
    open_report(page, mixed)
    show_matches(page, mixed)
    expect(page.locator("#quality-comparison")).to_be_hidden()
    capture(page, "desktop-mixed-zero")

    zero = run_sample(page, tmp_path, file, "sample", "def test_all_fails():\n    assert False\n")
    assert zero["quality"]["pass_rate_pct"] == 0 and zero["quality"]["coverage_pct"] == 0
    open_report(page, zero)
    show_matches(page, zero)

    blank = upload(page, project["id"], "blank.py", "")
    skipped = run_sample(page, tmp_path, blank, "blank", "import pytest\ndef test_skip():\n    pytest.skip('no case')\n")
    q = skipped["quality"]
    assert skipped["run"]["status"] == "skipped" and q["total"] == q["skipped"] == 1
    assert q["pass_rate_pct"] is None and q["coverage_pct"] is None and q["covered_lines"] == q["total_lines"] == 0
    open_report(page, skipped)
    show_matches(page, skipped)
    expect(page.locator('[data-metric="coverage"] .quality-meter')).to_have_count(0)
    expect(page.locator('[data-metric="pass-rate"] .quality-meter')).to_have_count(0)
    capture(page, "desktop-unmeasured")
