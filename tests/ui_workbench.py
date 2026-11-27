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
