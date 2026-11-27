"""WP06-F04-001. Exercise persisted F04 evidence through the real Edge UI."""
import os
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect

from backend import runner, runs
from test_ast_studio import post_json, record, studio, upload
from test_dashboard import app_url
from test_generation_studio import occupied_service


SOURCE = """def magnitude(x: float) -> float:
    \"\"\"Return the magnitude.

    >>> magnitude(-2)
    2
    >>> magnitude(-3)
    3
    \"\"\"
    return abs(x)
"""


def capture(page, name):
    folder = os.environ.get("TESTPILOT_F04_CAPTURE_DIR")
    if folder:
        dest = Path(folder)
        dest.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=dest / f"{name}.png", animations="disabled")


def route(project, subject, suite, run=None):
    url = f"/workbench/runs?project={project}&file={subject}&suite={suite}"
    return url + f"&run={run}" if run is not None else url


def verify_view(page, run, origin, subject):
    expect(page.locator("#exec-run-id")).to_have_text(f"#{run['id']}")
    expect(page.locator("#exec-revision")).to_have_text(f"v{subject['revision']} · #{subject['id']}")
    expect(page.locator("#exec-suite-origin")).to_have_text(f"v{origin['revision']} · #{origin['id']}")
    expect(page.locator("#run-identity")).to_contain_text(
        f"运行 #{run['id']} · 套件 #{run['suite_id']} · {subject['filename']} v{subject['revision']}")
    assert page.locator("#run-summary dd").all_text_contents() == [
        str(run[key]) for key in ("passed", "failed", "errors", "skipped")] + [f"{run['duration_ms']} ms"]
    assert page.locator("#run-log").text_content() == run["log"]
    record("F04_RUN", {key: run[key] for key in (
        "id", "project_id", "file_id", "suite_id", "status", "passed", "failed", "errors", "skipped", "exit_code")})


def execute(page, suite_id, file_id, *, status=200, waiting_capture=False):
    request_path = f"/api/suites/{suite_id}/runs"
    previous = parse_qs(urlsplit(page.url).query).get("run")
    with page.expect_response(lambda response: urlsplit(response.url).path == request_path
                              and response.request.method == "POST", timeout=120_000) as request:
        page.get_by_role("button", name="执行测试", exact=True).click()
        if waiting_capture:
            expect(page.locator("#request-state")).to_have_text("请求等待中")
            expect(page.locator("#execute")).to_be_disabled()
            expect(page.locator("#run-result")).to_be_hidden()
            expect(page.locator("#run-log")).to_be_hidden()
            expect(page.locator("#console-indicator")).to_have_text("等待执行响应")
            page.locator("#start-run").evaluate("form => form.requestSubmit()")
            capture(page, "desktop-waiting")
    response = request.value
    assert response.status == status
    assert response.request.post_data_json == {"file_id": file_id}
    if status != 200:
        return response.json()
    def new_run(url):
        selected = parse_qs(urlsplit(url).query).get("run")
        return bool(selected and selected != previous)

    page.wait_for_url(new_run, timeout=120_000)
    run_id = parse_qs(urlsplit(page.url).query)["run"][0]
    # Fetch the durable result by the route ID after the POST-triggered navigation.
    root = urlsplit(page.url)
    result = page.request.get(f"{root.scheme}://{root.netloc}/api/runs/{run_id}").json()
    assert result["id"] == int(run_id) and result["file_id"] == file_id and result["suite_id"] == suite_id
    return result


def test_execution_history_log_and_case_handoff(studio):
    page = studio
    project = post_json(page, "/api/projects", {"name": "Telemetry Lab"})
    first = upload(page, project["id"], "measurements.py", SOURCE)
    second = upload(page, project["id"], "measurements.py", SOURCE.replace("return abs(x)", "return x"))
    page.goto(f"/workbench/generation?project={project['id']}&file={first['id']}&symbol=magnitude")
    page.get_by_role("button", name="生成并验证").click()
    expect(page.locator("#initial-status")).to_contain_text("通过", timeout=120_000)
    page.get_by_role("link", name="查看首次执行记录").click()
    expect(page.locator("#exec-run-state")).to_have_text("执行通过")
    suite = int(page.locator("#run-suite").input_value())
    good_id = int(parse_qs(urlsplit(page.url).query)["run"][0])
    good = page.request.get(f"/api/runs/{good_id}").json()
    assert good["status"] == "passed" and good["passed"] > 0
    assert good["failed"] == good["errors"] == good["skipped"] == 0
    verify_view(page, good, first, first)
    capture(page, "desktop-passed")

    page.get_by_label("被测版本", exact=True).select_option(str(second["id"]))
    expect(page.locator("#exec-revision")).to_contain_text("v2")
    expect(page.locator("#exec-suite-origin")).to_contain_text("v1")
    expect(page.locator("#run-result")).to_be_hidden()
    posts = []
    page.on("request", lambda request: posts.append(request.url) if request.method == "POST" else None)
    failed = execute(page, suite, second["id"], waiting_capture=True)
    assert len(posts) == 1, posts
    assert failed["status"] == "failed" and failed["failed"] == 2 and failed["errors"] == 0
    verify_view(page, failed, first, second)
    expect(page.locator("#exec-run-state")).to_have_text("用例失败")
    assert page.locator("#run-cases tr").all()[0].get_attribute("data-outcome") == "failed"
    assert page.locator("#run-cases tr").count() == len(failed["cases"])

    failed_cases = [case for case in failed["cases"] if case["outcome"] == "failed"]
    selected = next(case for case in failed_cases if case["nodeid"].endswith("::test_example_2"))
    page.get_by_role("button", name="test_example_2", exact=True).click()
    expect(page.locator("#case-nodeid")).to_have_text(selected["nodeid"])
    expect(page.locator("#case-facts")).to_contain_text("未记录")
    expect(page.locator("#case-assertion")).to_be_hidden()
    expect(page.locator("#case-stack")).to_be_hidden()
    expect(page.locator("#run-history [aria-current]")).to_contain_text("失败 2")
    page.get_by_label("搜索执行日志").fill("[.*]")
    expect(page.locator("#log-match")).to_have_text("0 处匹配")
    page.get_by_label("搜索执行日志").fill("test_example_2")
    assert page.locator("#run-log mark").count() > 0
    assert page.locator("#run-log").text_content() == failed["log"]
    page.context.grant_permissions(["clipboard-read", "clipboard-write"])
    page.get_by_role("button", name="复制日志").click()
    expect(page.locator("#notice")).to_contain_text("已复制原始执行日志")
    clipboard = page.evaluate("navigator.clipboard.readText()")
    assert clipboard.replace("\r\n", "\n") == failed["log"].replace("\r\n", "\n")
    capture(page, "desktop-failed")

    page.locator("#toggle-history").click()
    expect(page.locator("#exec-history-content")).to_be_hidden()
    page.locator("#toggle-inspector").click()
    expect(page.locator("#exec-inspector-content")).to_be_hidden()
    page.locator("#toggle-history").click()
    page.locator("#toggle-inspector").click()
    page.locator("#exec-console summary").click()
    expect(page.locator("#run-log")).to_be_hidden()
    page.locator("#case-log-link").click()
    expect(page.locator("#run-log")).to_be_visible()

    page.get_by_label("运行状态", exact=True).select_option("passed")
    expect(page.locator("#run-history .tree-row")).to_have_count(1)
    page.get_by_label("搜索运行记录").fill("missing")
    expect(page.locator("#history-empty")).to_contain_text("没有匹配")
    page.get_by_label("搜索运行记录").fill(f"#{good['id']}")
    page.locator(f"#run-history [data-run-id='{good['id']}']").click()
    verify_view(page, good, first, first)
    page.locator(f"#run-history [data-run-id='{failed['id']}']").click()
    verify_view(page, failed, first, second)
    page.reload()
    verify_view(page, failed, first, second)
    expect(page.get_by_label("搜索执行日志")).to_have_value("")

    for width, height in ((1440, 900), (1024, 768), (768, 1024), (390, 844)):
        page.set_viewport_size({"width": width, "height": height})
        assert page.evaluate("document.documentElement.scrollWidth === innerWidth")
        center = round(page.locator(".exec-center").bounding_box()["width"])
        assert center >= 300
        record("F04_VIEW", {"width": width, "height": height, "center": center,
                            "engine": page.context.browser.version})
        if width == 768:
            page.locator("#run-result").scroll_into_view_if_needed()
            capture(page, "tablet-results")
        if width == 390:
            page.locator(".exec-jumps a[href='#start-run']").click()
            capture(page, "mobile-results")

    page.get_by_role("button", name="test_example_2", exact=True).click()
    expect(page.locator("#case-nodeid")).to_have_text(selected["nodeid"])
    capture(page, "mobile-inspector")
    page.locator("#case-bug").click()
    path = parse_qs(urlsplit(page.url).query)
    assert path["run"] == [str(failed["id"])] and path["file"] == [str(second["id"])]
    assert path["nodeid"] == [selected["nodeid"]]
    expect(page.locator("#bug-run")).to_have_value(str(failed["id"]))
    expect(page.locator("#nodeid")).to_have_value(selected["nodeid"])


def test_real_worker_error_timeout_and_truncation(studio):
    page = studio
    project = post_json(page, "/api/projects", {"name": "运行失败路径"})
    first = upload(page, project["id"], "worker_cases.py", SOURCE)
    suite = post_json(page, f"/api/files/{first['id']}/suites", {"target": "magnitude", "mode": "template"})
    scenarios = [
        ("def broken(:", "error", "SyntaxError", "执行错误", "desktop-error"),
        ("while True:\n    pass\n", "timeout", "deadline", "执行超时", "desktop-timeout"),
        ("print('bounded output / ' * 20000)\n", "error", "输出达到上限", "执行错误 · 输出截断", "desktop-truncated"),
    ]
    for source, status, diagnostic, label, screenshot in scenarios:
        file = upload(page, project["id"], "worker_cases.py", source)
        page.goto(route(project["id"], file["id"], suite["id"]))
        result = execute(page, suite["id"], file["id"])
        verify_view(page, result, first, file)
        assert result["status"] == status and diagnostic in result["log"]
        expect(page.locator("#exec-run-state")).to_have_text(label)
        if screenshot == "desktop-truncated":
            expect(page.locator("#log-truncation")).to_be_visible()
            expect(page.locator("#run-log")).to_be_visible()
        else:
            expect(page.locator("#log-truncation")).to_be_hidden()
        capture(page, screenshot)

    other = upload(page, project["id"], "different.py", SOURCE)
    page.goto(route(project["id"], other["id"], suite["id"]))
    expect(page.locator("#execute")).to_be_disabled()
    expect(page.locator("#exec-config-note")).to_contain_text("同名文件")
    page.goto(route(project["id"], first["id"], suite["id"], 999))
    expect(page.locator("#run-empty")).to_contain_text("运行不属于当前项目")
    expect(page.locator("#run-log")).to_be_hidden()


def test_real_busy_and_explicit_fault_injection(studio, occupied_service, monkeypatch):
    page = studio
    root = occupied_service
    project = post_json(page, root + "/api/projects", {"name": "故障注入验收"})
    project_api = root + f"/api/projects/{project['id']}"
    file = post_json(page, project_api + "/files", {"filename": "worker_cases.py", "source": SOURCE})
    source_api = root + f"/api/files/{file['id']}/suites"
    assert runs.SLOTS.acquire(blocking=False)
    try:
        response = page.request.post(source_api, data={"target": "magnitude", "mode": "template"})
        assert response.status == 409
        [suite] = page.request.get(source_api).json()
        page.goto(root + route(project["id"], file["id"], suite["id"]))
        busy = execute(page, suite["id"], file["id"], status=409)
        assert "受限运行在进行" in busy["detail"]
        expect(page.locator("#request-state")).to_have_text("并发冲突")
        expect(page.locator("#run-result")).to_be_hidden()
        assert page.request.get(project_api + "/runs").json() == []
        capture(page, "desktop-busy")
    finally:
        runs.SLOTS.release()

    with monkeypatch.context() as injected:
        # Test-only seam: force a persisted empty legacy record through the real route.
        injected.setattr(runner, "execute", lambda *_args: runner.empty_result())
        empty = execute(page, suite["id"], file["id"])
        verify_view(page, empty, file, file)
        expect(page.locator("#console-indicator")).to_have_text("无日志输出")
        expect(page.locator("#log-empty")).to_have_text("本次运行没有日志输出。")
        expect(page.locator("#copy-log")).to_be_disabled()
        assert empty["log"] == "" and empty["status"] == "error"
        capture(page, "injected-empty-log")

    def unavailable(*_args):
        raise OSError("F04 test-only unavailable worker")

    with monkeypatch.context() as injected:
        injected.setattr(runner, "run_worker", unavailable)
        missing = execute(page, suite["id"], file["id"])
        verify_view(page, missing, file, file)
        expect(page.locator("#exec-run-state")).to_have_text("执行器不可用")
        assert missing["status"] == "error" and "F04 test-only unavailable worker" in missing["log"]
        capture(page, "injected-unavailable")

    expect(page.locator("#execute")).to_be_enabled()
    assert len(page.request.get(project_api + "/runs").json()) == 2
