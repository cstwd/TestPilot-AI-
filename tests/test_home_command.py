"""WP10-HOME-001. Verify the Command Center against the real local service."""
import os
import re
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect

from test_ast_studio import studio, post_json, record, upload
from test_dashboard import app_url


VIEWS = ((1920, 1080), (1440, 900), (1280, 800), (1024, 768), (768, 1024), (390, 844))
MODULES = ("projects", "analysis", "generation", "runs", "bugs", "reports")
SAMPLE = """def magnitude(value: int) -> int:
    \"\"\"Return the magnitude.

    >>> magnitude(-3)
    3
    \"\"\"
    return value
"""


def home(page):
    page.goto("/")
    expect(page.get_by_role("heading", name="智能测试控制中心")).to_be_visible()
    expect(page.locator("#activity")).to_have_attribute("aria-busy", "false")


def capture(page, name, full_page=False):
    if folder := os.getenv("TESTPILOT_WP10_CAPTURE"):
        destination = Path(folder)
        destination.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=destination / f"{name}.png", animations="disabled", full_page=full_page)


def verify_target(link, slug, **expected):
    href = urlsplit(link.get_attribute("href"))
    assert href.path == "/workbench/" + slug
    assert parse_qs(href.query) == {key: [str(value)] for key, value in expected.items()}


def test_command_center_navigation_and_live_activity(studio):
    page = studio
    idle = post_json(page, "/api/projects", {"name": "归档工作区"})
    project = post_json(page, "/api/projects", {"name": "遥测质量工作区"})
    project_id = project["id"]
    first = upload(page, project_id, "telemetry.py", SAMPLE)
    fixed = upload(page, project_id, "telemetry.py", SAMPLE.replace("return value", "return abs(value)"))
    suite = post_json(page, f"/api/files/{first['id']}/suites", {"target": "magnitude", "mode": "template"})
    failure = suite["initial_run"]
    assert failure["status"] == "failed"
    failed_run = page.request.get(f"/api/runs/{failure['id']}").json()
    failed_case = next(case for case in failed_run["cases"] if case["outcome"] == "failed")
    defect = post_json(page, f"/api/runs/{failure['id']}/bugs",
                       {"nodeid": failed_case["nodeid"], "title": "负数未转换为绝对值"})
    regression = post_json(page, f"/api/bugs/{defect['id']}/regressions", {"file_id": fixed["id"]})
    latest_run = regression["regressions"][0]["run_id"]
    home(page)
    expect(page.locator("#api-status")).to_have_text("已连接")
    expect(page.locator("#database-status")).to_have_text("已连接")
    expect(page.locator("#home-mode")).to_have_text("本地演示模式")
    expect(page.locator("#activity-project")).to_have_value(str(project_id))
    rows = {kind: page.locator(f'[data-kind="{kind}"] a') for kind in ("project", "file", "run", "bug", "report")}
    expect(rows["project"]).to_have_text(project["name"])
    expect(rows["file"]).to_have_text("telemetry.py")
    expect(rows["run"]).to_have_text(f"运行 #{latest_run}")
    expect(rows["bug"]).to_have_text(defect["title"])
    expect(rows["report"]).to_have_text("telemetry.py v2")
    verify_target(rows["project"], "projects", project=project_id)
    verify_target(rows["file"], "projects", project=project_id, file=fixed["id"])
    verify_target(rows["run"], "runs", project=project_id, file=fixed["id"], suite=suite["id"], run=latest_run)
    verify_target(rows["bug"], "bugs", project=project_id, file=first["id"], bug=defect["id"], run=failure["id"])
    verify_target(rows["report"], "reports", project=project_id, file=fixed["id"], run=latest_run)
    with page.expect_response(lambda response: urlsplit(response.url).path == "/api/self-test") as received:
        page.get_by_role("button", name="运行自检").click()
    result = received.value.json()
    assert received.value.ok and result["status"] == "passed"
    expect(page.locator("#self-test-status")).to_have_text("通过")
    assert page.locator("#self-test-detail").text_content() == result["detail"]
    capture(page, "home-self-test-1440x900")
    page.locator("#self-test-output summary").click()
    record("WP10_SELF_TEST", result)
    record("WP10_ACTIVITY", {"project": project_id, "versions": [first["id"], fixed["id"]],
                             "failed_run": failure["id"], "run": latest_run, "bug": defect["id"],
                             "suite": suite["id"], "links": {kind: link.get_attribute("href") for kind, link in rows.items()}})

    for width, height in VIEWS:
        page.set_viewport_size({"width": width, "height": height})
        expect(page.get_by_role("button", name="运行自检")).to_be_enabled()
        expect(page.locator(".home-module")).to_have_count(6)
        metrics = page.evaluate("""() => {
          const grid = document.querySelector('.home-module-grid');
          return {pageWidth:document.documentElement.scrollWidth,
            columns:getComputedStyle(grid).gridTemplateColumns.split(' ').length,
            colorScheme:getComputedStyle(document.documentElement).colorScheme,
            panel:getComputedStyle(document.querySelector('.home-panel')).backgroundColor};
        }""")
        assert metrics["pageWidth"] == width and metrics["colorScheme"] == "dark"
        assert metrics["panel"] == "rgb(20, 22, 32)"
        if width == 390:
            assert metrics["columns"] == 1
        record("WP10_VIEW", {"viewport": [width, height], **metrics})
        capture(page, f"home-{width}x{height}")
    capture(page, "home-390x844-full", full_page=True)
    page.locator("#activity-project").select_option(str(idle["id"]))
    expect(page.locator('[data-kind=file] [data-note]')).to_have_text("暂无文件版本")
    expect(page.locator('[data-kind=report] a')).to_be_hidden()
    expect(rows["project"]).to_have_text(project["name"])
    selected_entry = page.locator('.home-module[data-module="projects"]')
    verify_target(selected_entry, "projects", project=idle["id"])
    selected_entry.click()
    expect(page.locator("#project")).to_have_value(str(idle["id"]))
    home(page)
    verify_target(page.locator("#quick-resume"), "projects", project=idle["id"])
    expect(page.locator("#quick-resume")).to_have_attribute("title", "上次打开：" + idle["name"])
    page.goto("/workbench/projects")
    expect(page.locator("#project")).to_have_value(str(project_id))
    page.get_by_role("link", name="TestPilot AI 首页").click()
    expect(page.locator("#activity")).to_have_attribute("aria-busy", "false")
    verify_target(page.locator("#quick-resume"), "projects", project=project_id)
    page.locator("#activity-project").select_option(str(project_id))
    expect(rows["report"]).to_have_text("telemetry.py v2")

    # Reuse the existing F01 import form in the mobile layout.
    page.locator("#quick-import").click()
    page.wait_for_url(f"**/workbench/projects?project={project_id}#upload")
    expect(page.locator("#upload")).to_be_enabled()
    page.locator("#upload").set_input_files({
        "name": "review.py", "mimeType": "text/plain", "buffer": b"def ready():\n    return True\n"})
    page.locator("#import-button").click()
    expect(page.locator("#inspect-file")).to_have_text("review.py")
    home(page)
    expect(page.locator('[data-kind=file] a')).to_have_text("review.py")
    page.locator("#quick-resume").click()
    expect(page.locator("#project")).to_have_value(str(project_id))
    home(page)
    page.set_viewport_size({"width": 1440, "height": 900})
    for slug in MODULES:
        card = page.locator(f'.home-module[data-module="{slug}"]')
        with page.expect_navigation() as route:
            card.click()
        assert route.value.ok and urlsplit(page.url).path == f"/workbench/{slug}"
        expect(page.locator("main h1")).to_be_visible()
        home(page)
    for label, path, heading in (("TestPilot Demo Lab", "/workbench/demo-lab", "Demo Lab"),
                                 ("智能测试引擎", "/engine", "智能测试引擎")):
        with page.expect_navigation() as route:
            page.get_by_role("link", name=label, exact=False).click()
        assert route.value.ok and urlsplit(page.url).path == path
        expect(page.get_by_role("heading", name=heading, exact=True)).to_be_visible()
        home(page)
    page.get_by_role("button", name="帮助").click()
    expect(page.get_by_role("dialog", name="使用帮助")).to_be_visible()
    page.keyboard.press("Escape")
    expect(page.get_by_role("dialog", name="使用帮助")).to_be_hidden()
    record("WP10_DESTINATIONS", {"modules": list(MODULES), "tools": ["/workbench/demo-lab", "/engine"]})


def test_command_center_empty_errors_settings_and_creation(studio):
    page = studio
    page.set_viewport_size({"width": 390, "height": 844})
    home(page)
    expect(page.locator("#activity-message")).to_contain_text("创建项目")
    expect(page.locator("#activity [data-kind][data-state=empty]")).to_have_count(5)
    capture(page, "home-empty-390", full_page=True)
    page.get_by_role("link", name="导入代码").click()
    expect(page.get_by_role("dialog", name="创建项目")).to_be_visible()
    page.get_by_label("项目名称", exact=True).fill("从首页创建")
    with page.expect_response(lambda response: urlsplit(response.url).path == "/api/projects"
                              and response.request.method == "POST") as created:
        page.get_by_role("button", name="创建并打开").click()
    assert created.value.status == 201
    page.wait_for_url(re.compile(r"/workbench/projects\?project=\d+#upload$"))
    expect(page.locator("#upload")).to_be_enabled()
    project_id = int(parse_qs(urlsplit(page.url).query)["project"][0])
    assert {"id": project_id, "name": "从首页创建"} in page.request.get("/api/projects").json()
    home(page)
    page.get_by_role("button", name="创建项目", exact=True).click()
    page.get_by_label("项目名称", exact=True).fill("从首页创建")
    page.get_by_role("button", name="创建并打开").click()
    expect(page.locator("#home-create-error")).to_have_text("项目名称已存在")
    page.keyboard.press("Escape")

    page.get_by_role("button", name="系统设置").click()
    expect(page.get_by_role("dialog", name="系统设置")).to_be_visible()
    page.get_by_label("自检完成后展开原始输出").uncheck()
    page.keyboard.press("Escape")
    page.reload()
    expect(page.locator("#activity")).to_have_attribute("aria-busy", "false")
    page.get_by_role("button", name="系统设置").click()
    expect(page.get_by_label("自检完成后展开原始输出")).not_to_be_checked()
    page.keyboard.press("Escape")

    health = "**/api/health"
    page.route(health, lambda route: route.fulfill(status=503, json={"status": "degraded", "database": "error", "mode": "demo"}))
    page.get_by_role("button", name="重新检查").click()
    expect(page.locator("#api-status")).to_have_text("已连接")
    expect(page.locator("#database-status")).to_have_text("异常")
    expect(page.locator("#health-checked")).to_have_attribute("datetime", re.compile(r"^\d{4}-"))
    page.unroute(health)

    runner = "**/api/self-test"
    output = "实际接口渲染探针\n失败输出 <code>"
    for status, result, label in ((409, "busy", "执行器忙碌"), (503, "failed", "未通过")):
        page.route(runner, lambda route: route.fulfill(status=status, json={"status": result, "detail": output}))
        page.get_by_role("button", name="运行自检").click()
        expect(page.locator("#self-test-status")).to_have_text(label)
        assert page.locator("#self-test-output").get_attribute("open") is None
        assert page.locator("#self-test-detail").text_content() == output
        assert page.locator("#self-test-detail code").count() == 0
        page.unroute(runner)

    files = f"**/api/projects/{project_id}/files"
    page.route(files, lambda route: route.fulfill(status=502, body="unavailable"))
    page.get_by_role("button", name="刷新最近活动").click()
    expect(page.locator('[data-kind=file] [data-note]')).to_have_text("读取失败，可刷新重试")
    expect(page.locator('[data-kind=bug] [data-note]')).to_have_text("暂无缺陷记录")
    page.unroute(files)

    page.context.set_offline(True)
    page.get_by_role("button", name="重新检查").click()
    expect(page.locator("#api-status")).to_have_text("检查失败")
    expect(page.locator("#database-status")).to_have_text("无法确认")
    page.get_by_role("button", name="刷新最近活动").click()
    expect(page.locator("#activity-message")).to_contain_text("无法读取项目记录")
    capture(page, "home-offline-390", full_page=True)
    page.context.set_offline(False)
    page.get_by_role("button", name="重新检查").click()
    page.get_by_role("button", name="刷新最近活动").click()
    expect(page.locator("#database-status")).to_have_text("已连接")
    expect(page.locator('[data-kind=project] a')).to_have_text("从首页创建")
    record("WP10_ERROR_PROBES", {"real_empty": True, "real_duplicate": 409, "injected_database": 503,
                               "injected_runner": [409, 503], "injected_files": 502, "offline_recovery": True})
