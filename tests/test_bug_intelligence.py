"""WP07-F05-001. Exercise the issue, Diff and regression UI against persisted WASI results."""
import os
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect

from test_ast_studio import post_json, record, studio, upload
from test_dashboard import app_url


ORIGINAL = """def magnitude(x: float) -> float:
    \"\"\"Return the magnitude of a measurement.

    >>> magnitude(-2)
    2
    >>> magnitude(-3)
    3
    \"\"\"
    return x
"""
WRONG = ORIGINAL.replace("return x", "return x - 1")
FIXED = ORIGINAL.replace("return x", "return abs(x)")


def capture(page, name):
    folder = os.environ.get("TESTPILOT_F05_CAPTURE_DIR")
    if folder:
        dest = Path(folder)
        dest.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=dest / f"{name}.png", animations="disabled")


def choose_diff(page, left, right):
    page.locator("#fix-file").select_option(str(right["id"]))
    expect(page.locator("#diff-workspace")).to_be_visible()
    expect(page.locator("#diff-from-sha")).to_have_text("SHA-256 " + left["sha256"])
    expect(page.locator("#diff-to-sha")).to_have_text("SHA-256 " + right["sha256"])
    expect(page.locator("#diff-from")).to_contain_text(f"v{left['revision']} · #{left['id']}")
    expect(page.locator("#diff-to")).to_contain_text(f"v{right['revision']} · #{right['id']}")
    expect(page.locator("#diff-lines [data-kind=removed] code")).to_have_text("return x")
    patch = right["source"].splitlines()[-1].strip()
    expect(page.locator("#diff-lines [data-kind=added] code")).to_have_text(patch)
    assert not page.locator("#diff-lines [data-kind=removed] .bug-unified-no").text_content().strip()
    assert page.locator("#diff-lines [data-kind=removed] .bug-line-no").first.inner_text() == str(
        len(left["source"].splitlines()))
    assert page.locator("#diff-lines [data-kind=added] .bug-line-no").first.inner_text() == str(
        len(right["source"].splitlines()))
    assert not page.locator("#diff-lines").evaluate("node => node.isContentEditable")


def regress(page, issue, candidate, case, status, *, waiting=False):
    url = f"/api/bugs/{issue['id']}/regressions"
    page.get_by_role("button", name="运行回归", exact=True).click()
    expect(page.locator("#confirm-regression")).to_be_visible()
    expect(page.locator("#confirm-regression-detail")).to_contain_text(f"套件 #{issue['suite_id']}")
    expect(page.locator("#confirm-regression-detail")).to_contain_text(f"v{candidate['revision']} · #{candidate['id']}")
    with page.expect_response(lambda res: urlsplit(res.url).path == url and res.request.method == "POST",
                              timeout=120_000) as pending:
        page.get_by_role("button", name="确认运行", exact=True).click()
        if waiting:
            expect(page.locator("#notice")).to_contain_text("回归执行中")
            expect(page.locator("#regress-button")).to_be_disabled()
            expect(page.locator("#fix-file")).to_be_disabled()
            capture(page, "desktop-regressing")
    response = pending.value
    assert response.ok and response.request.post_data_json == {"file_id": candidate["id"]}
    saved = response.json()
    known = {row["run_id"] for row in issue["regressions"]}
    assert saved["run_id"] == issue["run_id"] and saved["nodeid"] == case
    [row] = [row for row in saved["regressions"] if row["run_id"] not in known]
    assert row["file_id"] == candidate["id"]
    run = page.request.get(f"/api/runs/{row['run_id']}").json()
    assert (run["project_id"], run["file_id"], run["suite_id"], run["status"]) == (
        issue["project_id"], candidate["id"], issue["suite_id"], status)
    [result] = [case_result["outcome"] for case_result in run["cases"] if case_result["nodeid"] == case]
    assert result == status
    expect(page.locator("#notice")).to_contain_text(f"已保存回归运行 #{run['id']}", timeout=15_000)
    expect(page.locator("#regression-facts")).to_contain_text(f"v{candidate['revision']} · #{candidate['id']}")
    record("F05_REGRESSION", {"issue": issue["id"], "source_run": issue["run_id"], "suite": issue["suite_id"],
               "regression_run": run["id"], "candidate": candidate["id"], "revision": candidate["revision"],
               "nodeid": case, "run_status": status, "judgement": row["status"], "issue_status": saved["status"]})
    return saved, run


def test_issue_diff_and_real_regression_history(studio):
    page = studio
    other = post_json(page, "/api/projects", {"name": "独立项目"})
    project = post_json(page, "/api/projects", {"name": "Telemetry Lab"})
    first = upload(page, project["id"], "measurements.py", ORIGINAL)
    suite = post_json(page, f"/api/files/{first['id']}/suites", {"target": "magnitude", "mode": "template"})
    source_run = page.request.get(f"/api/runs/{suite['initial_run']['id']}").json()
    assert source_run["status"] == "failed" and source_run["failed"] == 2
    path = f"/workbench/runs?project={project['id']}&file={first['id']}&suite={suite['id']}&run={source_run['id']}"
    page.goto(path)
    case = "test_generated.py::test_example_2"
    page.get_by_role("button", name="test_example_2", exact=True).click()
    page.locator("#case-bug").click()
    expect(page.locator("#nodeid")).to_have_value(case)
    expect(page.locator("#bug-run")).to_have_value(str(source_run["id"]))
    expect(page.locator("#inspect-nodeid")).to_have_text(case)
    expect(page.locator("#original-assertion")).to_contain_text("assert target(-3) == 3")
    expect(page.locator("#original-assertion")).not_to_contain_text("assert target(-2) == 2")
    expect(page.locator("#original-run")).to_have_attribute("href", path)
    capture(page, "desktop-intake")

    page.get_by_label("缺陷标题").fill("负数遥测值的绝对值返回错误")
    page.get_by_role("button", name="登记缺陷").click()
    expect(page.locator("#bug-state")).to_have_text("待修复")
    issue_id = parse_qs(urlsplit(page.url).query)["bug"][0]
    issue_url = f"/api/bugs/{issue_id}"
    issue = page.request.get(issue_url).json()
    assert issue["nodeid"] == case and issue["run_id"] == source_run["id"] and issue["regressions"] == []
    expect(page.locator("#diff-empty")).to_contain_text("没有可用候选版本")
    expect(page.locator("#regress-button")).to_be_disabled()
    expect(page.locator("#diff-workspace")).to_be_hidden()
    capture(page, "desktop-no-candidate")

    ignored = upload(page, project["id"], "other_name.py", FIXED)
    upload(page, other["id"], first["filename"], FIXED)
    page.reload()
    expect(page.locator("#fix-file")).to_be_disabled()
    wrong = upload(page, project["id"], "MEASUREMENTS.py", WRONG)
    fixed = upload(page, project["id"], first["filename"], FIXED)
    page.reload()
    expect(page.locator("#fix-file option")).to_have_count(2)
    assert page.locator("#fix-file option").evaluate_all("options => options.map(item => Number(item.value))") == [
        fixed["id"], wrong["id"]]
    assert ignored["id"] not in (fixed["id"], wrong["id"])

    page.get_by_role("button", name="查看原始测试套件").click()
    expect(page.locator("#suite-drawer")).to_be_visible()
    expect(page.locator("#suite-drawer-meta")).to_contain_text(f"套件 #{suite['id']}")
    expect(page.locator("#suite-drawer-meta")).to_contain_text(f"v1 · #{first['id']}")
    expect(page.locator("#suite-drawer-sha")).to_have_text("SHA-256 " + suite["sha256"])
    assert page.locator("#suite-drawer-source").text_content() == suite["source"]
    capture(page, "desktop-original-suite")
    page.get_by_role("button", name="关闭套件").click()

    choose_diff(page, first, wrong)
    expect(page.locator("#bug-state")).to_have_text("待修复")
    capture(page, "desktop-diff")
    page.get_by_role("button", name="运行回归", exact=True).click()
    expect(page.locator("#confirm-regression")).to_be_visible()
    capture(page, "desktop-confirm")
    page.get_by_role("button", name="取消", exact=True).click()
    expect(page.locator("#confirm-regression")).not_to_be_visible()
    assert page.request.get(issue_url).json()["regressions"] == []

    issue, bad_run = regress(page, issue, wrong, case, "failed", waiting=True)
    expect(page.locator("#bug-state")).to_have_text("待修复")
    expect(page.locator("#regression-evidence")).to_contain_text("用例失败")
    capture(page, "desktop-regression-failed")

    choose_diff(page, first, fixed)
    expect(page.locator("#bug-state")).to_have_text("待修复")
    issue, good_run = regress(page, issue, fixed, case, "passed")
    expect(page.locator("#bug-state")).to_have_text("已解决")
    expect(page.locator("#regressions")).to_contain_text("已解决")
    expect(page.locator("#regression-evidence")).to_contain_text("执行通过")
    page.locator("#regressions .bug-regression-row").first.scroll_into_view_if_needed()
    capture(page, "desktop-resolved")

    choose_diff(page, first, wrong)
    issue, repeated_bad_run = regress(page, issue, wrong, case, "failed")
    assert issue["status"] == "resolved" and issue["regressions"][0]["run_id"] == good_run["id"]
    assert repeated_bad_run["id"] > good_run["id"]
    expect(page.locator("#bug-state")).to_have_text("已解决")
    expect(page.locator("#regression-evidence")).to_contain_text("用例失败")
    expect(page.locator("#regressions .bug-regression-row")).to_have_count(3)
    assert page.request.get(f"/api/runs/{source_run['id']}").json() == source_run

    prior = page.locator(f"#regressions [data-run-id='{bad_run['id']}'] button")
    prior.click()
    expect(page.locator("#regression-evidence")).to_contain_text("用例失败")
    page.reload()
    expect(page.locator("#fix-file")).to_have_value(str(wrong["id"]))
    expect(page.locator("#inspect-nodeid")).to_have_text(case)
    expect(page.locator(f"#regressions [data-run-id='{bad_run['id']}']")).to_have_attribute("data-selected", "")
    expect(page.locator("#regression-run")).to_have_attribute("href",
        f"/workbench/runs?project={project['id']}&file={wrong['id']}&suite={suite['id']}&run={bad_run['id']}")

    page.route(f"**/api/files/{wrong['id']}", lambda request: request.fulfill(
        status=503, json={"detail": "F05 test-only version read outage"}), times=1)
    page.reload()
    expect(page.locator("#diff-empty")).to_contain_text("版本读取失败")
    expect(page.locator("#diff-workspace")).to_be_hidden()
    expect(page.locator("#regress-button")).to_be_disabled()
    expect(page.locator("#original-assertion")).to_contain_text("assert target(-3) == 3")
    capture(page, "injected-version-read-failure")
    page.get_by_role("button", name="重新读取版本").click()
    expect(page.locator("#diff-workspace")).to_be_visible()

    page.get_by_label("缺陷状态", exact=True).select_option("resolved")
    page.get_by_label("搜索缺陷").fill("missing")
    expect(page.locator("#issue-list-empty")).to_contain_text("没有匹配")
    page.get_by_label("搜索缺陷").fill(case)
    expect(page.locator("#issue-list [aria-current=page]")).to_have_count(1)
    page.get_by_label("搜索缺陷").fill("")
    check = path.replace("/workbench/runs?", "/workbench/bugs?") + "&nodeid=" + case
    page.goto(check)
    expect(page.locator("#bug-state")).to_have_text("已解决")
    expect(page.locator("#intake-panel")).to_be_hidden()

    for width, height in ((1440, 900), (1024, 768), (768, 1024), (390, 844)):
        page.set_viewport_size({"width": width, "height": height})
        assert page.evaluate("document.documentElement.scrollWidth === innerWidth")
        if width <= 900:
            page.get_by_role("button", name="缺陷列表", exact=True).click()
            expect(page.locator("#issue-list [aria-current=page]")).to_be_visible()
            if width == 390:
                capture(page, "mobile-explorer")
            page.get_by_role("button", name="详情", exact=True).click()
            expect(page.locator("#original-assertion")).to_contain_text("assert target(-3) == 3")
            expect(page.locator("#inspect-nodeid")).to_have_text(case)
            if width == 390:
                capture(page, "mobile-details")
            page.get_by_role("button", name="Diff", exact=True).click()
            expect(page.locator("#diff-workspace")).to_be_visible()
            assert page.locator("#diff-lines .bug-diff-row").first.evaluate("node => getComputedStyle(node).display") == "block"
            capture(page, "mobile-diff" if width == 390 else "tablet-diff")
        record("F05_VIEW", {"width": width, "height": height, "engine": page.context.browser.version})

    page.get_by_role("button", name="缺陷列表", exact=True).click()
    page.locator("#project").select_option(str(other["id"]))
    expect(page.locator("#issue-list-empty")).to_contain_text("尚无登记缺陷")
    expect(page.locator("#bug-state")).not_to_be_visible()
    page.goto(check)
    expect(page.locator("#bug-state")).to_have_text("已解决")
    page.locator("#original-run").click()
    expect(page.locator("#exec-run-id")).to_have_text(f"#{source_run['id']}")
    expect(page.locator("#exec-run-state")).to_have_text("用例失败")
