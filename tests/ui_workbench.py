"""Browser checks for the actual workbench, started through main.py."""
import os
import sys
import json
from urllib.parse import parse_qs, urlsplit

import pytest
from playwright.sync_api import expect, sync_playwright

from test_dashboard import app_url  # same real service and isolated DB fixture


@pytest.fixture
def page(app_url):
    with sync_playwright() as driver:
        channel = os.environ.get("TESTPILOT_BROWSER_CHANNEL", "msedge" if sys.platform == "win32" else "chromium")
        browser = driver.chromium.launch(channel=channel, headless=True)
        try:
            tab = browser.new_page(base_url=app_url, viewport={"width": 375, "height": 812})
            yield tab
            assert tab.evaluate("document.documentElement.scrollWidth <= innerWidth")
        finally:
            browser.close()


def test_f01(page):
    page.goto("/")
    page.get_by_role("link", name="项目与文件").click()
    page.get_by_label("项目名称").fill("样例项目")
    page.get_by_role("button", name="创建项目").click()
    expect(page.locator("#project option:checked")).to_have_text("样例项目")
    for revision, value in enumerate([b"def value():\n    return 1\n", b"def value():\n    return 2\n"], 1):
        page.get_by_label("本地文件").set_input_files({"name": "calc.py", "mimeType": "text/plain", "buffer": value})
        page.get_by_role("button", name="导入文件").click()
        expect(page.locator("#digest")).to_contain_text(f"v{revision}")
        expect(page.locator("#source")).to_have_text(value.decode())
    page.get_by_label("文件版本").select_option(label="calc.py · v1")
    expect(page.locator("#source")).to_contain_text("return 1")
    page.reload()
    expect(page.get_by_role("link", name="分析此版本")).to_have_attribute("href", "/workbench/analysis?project=1&file=1")


def import_source(page, project_id, source, filename="sample.py"):
    result = page.request.post(f"/api/projects/{project_id}/files", data={"filename": filename, "source": source})
    assert result.ok, result.text()
    return result.json()["id"]


def test_f02(page):
    project = page.request.post("/api/projects", data={"name": "静态分析"}).json()["id"]
    first = import_source(page, project, "def convert(number: int = 2) -> int:\n    return number\n")
    second = import_source(page, project, "def invalid(:\n")
    page.goto(f"/workbench/analysis?project={project}&file={first}")
    expect(page.locator("#symbols")).to_contain_text("convert(number: int = 2) → int")
    expect(page.locator("#symbols")).to_contain_text("第 1–2 行")
    page.get_by_label("文件版本").select_option(str(second))
    expect(page.locator("#symbols")).to_contain_text("语法错误 · 行 1")


def test_f03(page):
    project = page.request.post("/api/projects", data={"name": "生成评审"}).json()["id"]
    source = "def magnitude(x: int) -> int:\n    return abs(x)\n"
    file = import_source(page, project, source)
    page.goto(f"/workbench/analysis?project={project}&file={file}")
    page.get_by_role("link", name="为此函数生成测试").click()
    expect(page.get_by_label("目标函数")).to_have_value("magnitude")
    page.get_by_role("button", name="生成并验证").click()
    expect(page.locator("#test-source")).to_contain_text("def test_", timeout=120_000)
    expect(page.locator("#suite-detail")).to_contain_text("template")
    expect(page.locator("#initial-status")).to_contain_text("首次 Pytest 运行 #1 · 通过")
    page.reload()
    expect(page.locator("#suite-detail")).to_contain_text("语法检查通过")
    page.get_by_role("link", name="查看首次执行记录").click()
    expect(page.locator("#run-identity")).to_contain_text("运行 #1")


def prepare_suite(page, name):
    project = page.request.post("/api/projects", data={"name": name}).json()["id"]
    file = import_source(page, project, "def add(x: int) -> int:\n    return x + 1\n")
    result = page.request.post(f"/api/files/{file}/suites", data={"target": "add", "mode": "template"}, timeout=120_000)
    assert result.ok, result.text()
    return project, file, result.json()["id"]


def test_f04(page):
    project, file, suite = prepare_suite(page, "执行验收")
    initial = page.request.get(f"/api/suites/{suite}").json()["initial_run"]["id"]
    page.goto(f"/workbench/runs?project={project}&file={file}&suite={suite}")
    with page.expect_response(lambda r: r.url.endswith(f"/api/suites/{suite}/runs") and r.request.method == "POST", timeout=120_000) as response:
        page.get_by_role("button", name="执行测试").click()
    assert response.value.ok
    page.wait_for_url(lambda url: "run" in parse_qs(urlsplit(url).query), timeout=120_000)
    run_id = int(parse_qs(urlsplit(page.url).query)["run"][0])
    result = page.request.get(f"/api/runs/{run_id}").json()
    assert run_id != initial and result["suite_id"] == suite and result["status"] == "passed"
    expect(page.locator("#run-identity")).to_contain_text(f"运行 #{run_id}", timeout=120_000)
    expect(page.locator("#run-log")).to_contain_text("passed")
    expect(page.locator("#to-bugs")).to_have_attribute("href", f"/workbench/bugs?project={project}&file={file}&run={run_id}")


def test_f05(page):
    project = page.request.post("/api/projects", data={"name": "回归验收"}).json()["id"]
    filename = "counter.py"
    source = 'def add(x: int) -> int:\n    """\n    >>> add(1)\n    2\n    """\n    return x\n'
    first = import_source(page, project, source, filename)
    suite = page.request.post(f"/api/files/{first}/suites", data={"target": "add"}, timeout=120_000).json()["id"]
    failed = page.request.post(f"/api/suites/{suite}/runs", data={"file_id": first}, timeout=120_000).json()
    assert failed["status"] == "failed", failed
    fixed = import_source(page, project, source.replace("return x", "return x + 1"), filename)
    page.goto(f"/workbench/bugs?project={project}&file={fixed}&run={failed['id']}")
    page.get_by_label("缺陷标题").fill("加一示例失败")
    page.get_by_role("button", name="登记缺陷").click()
    expect(page.locator("#failure-node")).to_contain_text("test_example")
    page.get_by_role("button", name="运行回归").click()
    expect(page.locator("#regressions")).to_contain_text("已解决", timeout=120_000)
    page.locator("#original-run").click()
    expect(page.locator("#run-identity")).to_contain_text(f"运行 #{failed['id']} · 套件 #{suite} · {filename} v1")
    expect(page.locator("#run-summary")).to_contain_text("失败")


def test_f06(page):
    project, file, suite = prepare_suite(page, "报告验收")
    run = page.request.post(f"/api/suites/{suite}/runs", data={"file_id": file}, timeout=120_000).json()
    assert run["status"] == "passed", run
    page.goto(f"/workbench/reports?project={project}&file={file}&run={run['id']}")
    expect(page.locator("#report-origin")).to_contain_text("sample.py v1")
    data = page.request.get(f"/api/runs/{run['id']}/report").json()
    expect(page.locator("#report-hashes")).to_contain_text(data["source"]["sha256"])
    expect(page.locator("#report-quality")).to_contain_text(str(data["quality"]["passed"]))
    with page.expect_download() as downloading:
        page.get_by_role("link", name="下载 JSON 报告").click()
    download = downloading.value
    assert download.suggested_filename.endswith(".json")
    assert json.loads(download.path().read_text(encoding="utf-8-sig")) == data
