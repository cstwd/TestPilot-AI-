"""Browser checks for the actual workbench, started through main.py."""
import os
import sys

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
    page.get_by_role("button", name="生成测试").click()
    expect(page.locator("#test-source")).to_contain_text("def test_")
    expect(page.locator("#suite-detail")).to_contain_text("template")
    expect(page.get_by_role("link", name="前往执行此测试")).to_have_attribute("href", f"/workbench/runs?project={project}&file={file}&suite=1")
    page.reload()
    expect(page.locator("#suite-detail")).to_contain_text("语法检查通过")
