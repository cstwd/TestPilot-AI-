import json
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

import pytest
from playwright.sync_api import expect, sync_playwright

from test_dashboard import app_url


def test_diagnostics_history_and_local_access(app_url):
    client = build_opener(ProxyHandler({}))

    def request(path, body=None, headers=None):
        data = json.dumps(body).encode() if body is not None else None
        req = Request(app_url + path, data=data, headers={"Content-Type": "application/json", **(headers or {})})
        with client.open(req, timeout=30) as response:
            return json.load(response)

    project = request("/api/projects", {"name": "diagnostics"})
    url = f"/api/projects/{project['id']}/files"
    file = request(url, {"filename": "incomplete.py", "source": "def unfinished(:\n"})
    tasks = f"/api/engine/files/{file['id']}/tasks"
    payload = {"target": "unfinished"}
    for body, headers, code in [(payload, {"Origin": "https://external.invalid"}, 403),
                                ({**payload, "max_repairs": 4}, {}, 422)]:
        with pytest.raises(HTTPError) as rejected:
            request(tasks, body, headers)
        assert rejected.value.code == code
    assert request(tasks) == []
    task = request(tasks, payload)
    assert task["status"] == "error"
    assert [r["kind"] for r in task["records"]] == ["SourceAnalysis", "TestReport"]
    assert task["records"][0]["payload"]["diagnostics"][0]["line"] == 1
    assert request("/api/engine/tasks/" + task["id"]) == task


def test_engine_browser(app_url):
    client = build_opener(ProxyHandler({}))
    def post(route, data):
        req = Request(app_url + route, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
        with client.open(req, timeout=20) as response:
            return json.load(response)

    project = post("/api/projects", {"name": "Browser"})
    post(f"/api/projects/{project['id']}/files", {"filename": "identity.py",
         "source": "def identity(n: int) -> int:\n    '''>>> identity(4)\n    4\n    '''\n    return n\n"})
    import os
    import sys
    channel = os.environ.get("TESTPILOT_BROWSER_CHANNEL", "msedge" if sys.platform == "win32" else "chromium")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=channel, headless=True)
        try:
            page = browser.new_page()
            page.goto(app_url)
            page.get_by_role("link", name="打开智能测试引擎").click()
            page.get_by_label("生成方式").select_option("template")
            page.get_by_role("button", name="生成并运行").click()
            expect(page.get_by_role("heading", name="运行结果")).to_be_visible(timeout=90000)
            expect(page.locator("#task-result")).to_contain_text("template")
            expect(page.locator("#task-result")).to_contain_text("completed")
            with page.expect_download() as download:
                page.get_by_role("link", name="下载完整 JSON").click()
            with open(download.value.path(), encoding="utf-8") as stream:
                evidence = json.load(stream)
            assert evidence["records"][-1]["kind"] == "TestReport"
            assert evidence["records"][-1]["payload"]["execution_count"] == 1
        finally:
            browser.close()
