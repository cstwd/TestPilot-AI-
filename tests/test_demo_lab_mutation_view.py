
"""Verify the survivor-location UI against actual F13 observations."""
import os
import sys

from playwright.sync_api import expect, sync_playwright

from test_dashboard import app_url
from test_demo_lab import API, capture, http, screenshot


def test_survivor_location_and_score_denominators(app_url):
    channel = os.environ.get("TESTPILOT_BROWSER_CHANNEL", "msedge" if sys.platform == "win32" else "chromium")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=channel, headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto(app_url + "/workbench/demo-lab?sample=geometry_calculator")
        expect(page.locator("#lab-name")).to_have_text("geometry_calculator.py")
        page.get_by_role("button", name="运行演示").click()
        expect(page.locator("#lab-run-state")).to_contain_text("完成", timeout=150000)
        panel = page.locator(".lab-mutation")
        expect(panel).to_contain_text("全量分母 5，有效分母 3")
        expect(panel).to_contain_text("40%")
        expect(panel).to_contain_text("66.67%")
        panel.get_by_text("定位存活变异").click()
        expect(panel.locator("pre")).to_contain_text("L")
        run_id = page.url.split("run=")[-1]
        receipt = http(app_url, f"{API}/runs/{run_id}/export")
        report = receipt["mutation"]
        before = report["result"]["before"]
        assert (before["total"], before["killed"], before["survived"], before["execution_error"]) == (5, 2, 1, 2)
        survivor, = report["survivors"]
        assert survivor["line"] > 0 and survivor["operator"]
        capture("f13-geometry.json", receipt)
        screenshot(page, "05-f13-surviving-mutant.png")
        print("PHASE07_SURVIVOR", run_id, survivor["line"], survivor["operator"])
        browser.close()
