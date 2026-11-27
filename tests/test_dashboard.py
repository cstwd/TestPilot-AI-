"""Exercise the distributed application entry point using a real local browser."""

import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener

import pytest
from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def app_url(tmp_path):
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]

    url = f"http://127.0.0.1:{port}"
    client = build_opener(ProxyHandler({}))
    log_path = tmp_path / "service.log"
    with log_path.open("wb") as log:
        process = subprocess.Popen(
            [sys.executable, str(ROOT / "main.py"), "--no-browser", "--port", str(port)],
            cwd=ROOT,
            env={**os.environ, "TESTPILOT_DATA_DIR": str(tmp_path), "PYTHONIOENCODING": "utf-8"},
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        try:
            deadline = time.monotonic() + 20
            while process.poll() is None and time.monotonic() < deadline:
                try:
                    with client.open(url + "/api/health", timeout=1) as response:
                        if response.status == 200:
                            break
                except (URLError, OSError):
                    time.sleep(0.1)
            else:
                pytest.fail("服务未就绪\n" + log_path.read_text("utf-8", errors="replace"))
            assert (tmp_path / "testpilot.sqlite3").is_file()
            yield url
            assert "GET /favicon.ico" not in log_path.read_text("utf-8", errors="replace")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


def test_dashboard(app_url):
    """Check live responses, responsive layout, real self-test and offline recovery."""
    default_channel = "msedge" if sys.platform == "win32" else "chromium"
    channel = os.environ.get("TESTPILOT_BROWSER_CHANNEL", default_channel)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=channel, headless=True, timeout=20000)
        try:
            context = browser.new_context(viewport={"width": 1366, "height": 900})
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(app_url, wait_until="load")
            expect(page.get_by_role("heading", name="启动仪表盘")).to_be_visible()
            expect(page.locator("#api-status")).to_have_text("已连接")
            expect(page.locator("#database-status")).to_have_text("已连接")
            expect(page.locator(".module-id")).to_have_count(6)
            assert page.locator('link[rel="icon"]').get_attribute("href").startswith("data:")

            with page.expect_response(lambda r: r.url == app_url + "/api/self-test") as result:
                page.get_by_role("button", name="运行自检").click()
            assert result.value.request.method == "POST"
            assert result.value.ok
            payload = result.value.json()
            assert payload["status"] == "passed"
            assert "passed" in payload["detail"]
            expect(page.locator("#self-test-status")).to_have_text("通过")
            expect(page.locator("#self-test-detail")).to_have_text(payload["detail"])
            print(f"Browser: {channel} {browser.version}; self-test response: {payload['detail']}")
            if os.environ.get("TESTPILOT_CAPTURE_DASHBOARD") == "1":
                page.screenshot(path=ROOT / "reports" / "dashboard.png", full_page=True)

            page.set_viewport_size({"width": 375, "height": 812})
            expect(page.get_by_role("button", name="运行自检")).to_be_visible()
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            context.set_offline(True)
            refresh = page.get_by_role("button", name="重新检查")
            refresh.click()
            expect(page.locator("#api-status")).to_have_text("检查失败")
            context.set_offline(False)
            refresh.click()
            expect(page.locator("#database-status")).to_have_text("已连接")
            assert errors == []
        finally:
            browser.close()
