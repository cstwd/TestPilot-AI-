import json
import os
import sys
from urllib.request import ProxyHandler, Request, build_opener

from playwright.sync_api import expect, sync_playwright

from backend import mutation_store
from test_dashboard import app_url


def api(url, path, data=None):
    client = build_opener(ProxyHandler({}))
    body = json.dumps(data).encode() if data is not None else None
    req = Request(url + path, data=body, headers={"Content-Type": "application/json"})
    with client.open(req, timeout=60) as response:
        return json.load(response)


def create_task(url):
    project = api(url, "/api/projects", {"name": "Mutation UI"})
    revision = api(url, f"/api/projects/{project['id']}/files", {"filename": "unit.py",
                    "source": "def unit(x: int) -> int:\n    '''>>> unit(3)\n    3\n    '''\n    return x\n"})
    return api(url, f"/api/engine/files/{revision['id']}/tasks", {"target": "unit", "generation_mode": "template"})


def test_open_run_and_export_mutations(app_url):
    task = create_task(app_url)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=os.getenv("TESTPILOT_BROWSER_CHANNEL",
                                               "msedge" if sys.platform == "win32" else "chromium"), headless=True)
        try:
            page = browser.new_page()
            page.goto(app_url+"/engine?task_id="+task["id"])
            page.get_by_role("link", name="评估变异测试与补测").click()
            page.get_by_role("checkbox").uncheck()
            page.get_by_role("button", name="创建并运行").click()
            expect(page.locator("#status")).to_contain_text("已完成", timeout=120000)
            expect(page.locator("#before")).to_contain_text("1/1")
            expect(page.locator("#sites")).to_contain_text("已杀死")
            expect(page.locator("#feedback-status")).to_contain_text("未启用")
            expect(page.locator("#baseline-evidence")).to_contain_text("退出码 0")
            with page.expect_download() as saved:
                page.get_by_role("link", name="下载完整实验 JSON").click()
            report = json.loads(saved.value.path().read_bytes())
            assert report["before"]["killed"] == 1 and report["after"] is None
            page.get_by_label("历史会话").select_option("")
            expect(page.locator("#export")).to_be_hidden()
            expect(page.locator("#feedback-panel")).to_be_hidden()
        finally:
            browser.close()


def test_feedback_summary_ui_and_export(app_url, tmp_path):
    """Presentation fixtures exercise UI states independently of a particular installed model."""
    task = create_task(app_url)
    path = tmp_path / "testpilot.sqlite3"
    create = "/api/engine/tasks/" + task["id"] + "/mutations"
    selected = api(app_url, create, {"feedback": True})
    key = selected["id"]
    mutant = selected["manifest"][0]["id"]
    added = "def test_candidate():\n    from subject import unit\n    assert unit(2) == 2\n"
    payload = {
        "provider": "ollama", "model": "ui-fixture", "mode": "ai", "added_code": added,
        "code": "original suite and extra code",
        "cases": [{"mutant_id": mutant, "test_name": "test_candidate", "call": "unit(2)", "expected": "2",
                   "reason": "检查另一输入", "internal": "private-case-field"}],
        "attempts": [{"number": 1, "focus_id": mutant, "status": "rejected", "reason": "候选语法错误",
                      "messages": [{"content":"private-prompt"}], "raw": "private-response"}],
    }
    mutation_store.record(path, key, "after", "feedback", "generated", "候选已生成", payload)
    validation = {"status": "failed", "exit_code": 1, "passed": 1, "failed": 1, "errors": 0, "skipped": 0,
                  "stdout": "private-full-output", "failures": [{"nodeid": "test_generated.py::test_candidate",
                  "exception_type": "AssertionError", "message": "fixture assertion mismatch"}]}
    mutation_store.record(path, key, "after", "validation", "failed", "全部候选在原版上的执行结果", validation)
    mutation_store.record(path, key, "after", "selection", "rejected", "按原版测试节点筛选", {
        "accepted_names": [], "rejected_names": ["test_candidate"], "code": None})
    mutation_store.state(path, key, "feedback_baseline_failed", "候选在原版上失败")
    unavailable = api(app_url, create, {"feedback": True})["id"]
    mutation_store.record(path, unavailable, "after", "feedback", "unavailable", "没有可用本机模型",
                          {"provider": "ollama", "requested_model": "missing-model"})
    mutation_store.state(path, unavailable, "feedback_unavailable", "没有可用本机模型")

    route = "/api/mutations/" + key
    progress = api(app_url, route)
    raw = json.dumps(progress, ensure_ascii=False)
    for private in ("private-prompt", "private-response", "private-full-output", "private-case-field", payload["code"]):
        assert private not in raw
    report = api(app_url, route + "/report")
    assert report["events"][0]["payload"] == payload
    assert report["events"][1]["payload"] == validation
    with sync_playwright() as playwright:
        channel = os.getenv("TESTPILOT_BROWSER_CHANNEL", "msedge" if sys.platform == "win32" else "chromium")
        browser = playwright.chromium.launch(channel=channel, headless=True)
        try:
            page = browser.new_page(viewport={"width": 375, "height": 812})
            page.goto(app_url + "/mutations?task_id=" + task["id"])
            history = page.get_by_label("历史会话")
            history.select_option(key)
            expect(page.locator("#feedback-status")).to_contain_text("ollama / ui-fixture")
            for phrase in ("unit(2) → 2", "检查另一输入", "未采纳"):
                expect(page.locator("#feedback-cases")).to_contain_text(phrase)
            expect(page.locator("#feedback-attempts")).to_contain_text("候选语法错误")
            expect(page.locator("#baseline-evidence")).to_contain_text("退出码 1")
            expect(page.locator("#baseline-evidence")).to_contain_text("fixture assertion mismatch")
            page.get_by_text("查看模型提出的 Pytest 补测").click()
            expect(page.locator("#feedback-code")).to_have_text(added)
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            history.select_option(unavailable)
            expect(page.locator("#feedback-status")).to_contain_text("模型不可用")
            expect(page.locator("#feedback-status")).to_contain_text("已请求模型 missing-model")
            expect(page.locator("#feedback-source")).to_be_hidden()
            expect(page.locator("#feedback-attempts")).to_be_empty()
        finally:
            browser.close()
