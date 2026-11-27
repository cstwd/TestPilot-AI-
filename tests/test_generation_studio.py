"""WP05-F03-001. Exercise the live template, static check and WASI run boundaries."""
import os
import socket
import threading
import time
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
import uvicorn
from playwright.sync_api import expect

from backend import runs
from backend.app import create_app
from test_ast_studio import post_json, record, studio, upload
from test_dashboard import app_url


SAMPLE = """def magnitude(x: int) -> int:
    \"\"\"Return an absolute measurement.

    >>> magnitude(-3)
    3
    \"\"\"
    return abs(x)


def signed_magnitude(x: int) -> int:
    \"\"\"Compare the implementation against a deliberately failing example.

    >>> signed_magnitude(-3)
    3
    \"\"\"
    return x
"""

REJECTED = """def keep(function):
    return function


@keep
def no_contract(**options):
    return options


if False:
    def conditional():
        return 0


async def async_value():
    return 1


def duplicate():
    return 1


def duplicate():
    return 2
"""


def capture(page, key):
    folder = os.environ.get("TESTPILOT_F03_CAPTURE_DIR")
    if folder:
        target = Path(folder)
        target.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=target / f"{key}.png", animations="disabled")


def submit(page, *, status=200):
    with page.expect_response(lambda res: urlsplit(res.url).path.endswith("/suites")
                              and res.request.method == "POST", timeout=120_000) as pending:
        page.get_by_role("button", name="生成并验证").click()
    response = pending.value
    assert response.status == status, response.text()
    assert response.request.post_data_json["mode"] == "template"
    return response.json()


def verify_run(page, suite, file, project_id, expected):
    expect(page.locator("#suite-detail")).to_contain_text(f"#{suite['id']} · template · 语法检查通过")
    expect(page.locator("#stage-static")).to_have_text("已通过")
    assert suite["format_checked"] and suite["file_id"] == file["id"]
    assert suite["initial_run"]["status"] == expected
    run_id = suite["initial_run"]["id"]
    run = page.request.get(f"/api/runs/{run_id}").json()
    assert (run["project_id"], run["file_id"], run["suite_id"], run["status"]) == (
        project_id, file["id"], suite["id"], expected)
    expect(page.locator("#run-facts")).to_contain_text(f"#{run_id}")
    expect(page.locator("#run-facts")).to_contain_text(run["created_at"])
    assert "生成时间" not in page.locator("#suite-facts").text_content()
    assert parse_qs(urlsplit(page.locator("#run-suite").get_attribute("href")).query) == {
        "project": [str(project_id)], "file": [str(file["id"])],
        "suite": [str(suite["id"])], "run": [str(run_id)],
    }
    assert page.locator("#test-source .ai-code").all_text_contents() == suite["source"].splitlines()
    record("F03_RESULT", {key: run[key] for key in (
        "id", "project_id", "file_id", "suite_id", "status", "passed", "failed", "errors", "skipped", "exit_code")})
    return run


def test_template_static_and_real_first_runs(studio):
    page = studio
    project = post_json(page, "/api/projects", {"name": "Telemetry Lab"})
    file = upload(page, project["id"], "measurements.py", SAMPLE)
    newer = upload(page, project["id"], "measurements.py", SAMPLE + "\ndef new_revision():\n    return None\n")
    base = f"/workbench/generation?project={project['id']}&file={file['id']}"
    page.goto(base + "&symbol=magnitude")
    expect(page.locator("#gen-revision")).to_have_text(f"v1 · #{file['id']}")
    expect(page.get_by_label("目标函数")).to_have_value("magnitude")
    expect(page.locator("#target-source .ai-line-no").first).to_have_attribute("data-number", "1")
    expect(page.locator("#target-source")).to_contain_text("return abs(x)")
    expect(page.locator("#target-source")).not_to_contain_text("def signed_magnitude")
    expect(page.locator("#run-suite")).not_to_be_visible()
    capture(page, "desktop-ready")

    passed = submit(page)
    run = verify_run(page, passed, file, project["id"], "passed")
    assert run["passed"] > 0 and run["exit_code"] == 0
    expect(page.locator("#stage-request")).to_have_text("套件已生成")
    expect(page.locator("#stage-run")).to_have_text(f"通过 #{run['id']}")
    capture(page, "desktop-passed")

    page.get_by_label("搜索函数").fill("SIGNED")
    expect(page.locator("#target-meta")).to_contain_text("1 个匹配")
    page.get_by_label("目标函数").select_option("signed_magnitude")
    expect(page.locator("#target-source .ai-line-no").first).to_have_attribute("data-number", "10")
    expect(page.locator("#target-source")).to_contain_text("return x")
    expect(page.locator("#target-signature")).to_contain_text("signed_magnitude")
    failed = submit(page)
    run = verify_run(page, failed, file, project["id"], "failed")
    assert run["failed"] == 1 and run["exit_code"] == 1
    expect(page.locator("#stage-static")).to_have_attribute("data-state", "ok")
    expect(page.locator("#stage-run")).to_have_text(f"失败 #{run['id']}")
    capture(page, "desktop-failed")

    page.reload()
    expect(page.get_by_label("目标函数")).to_have_value("signed_magnitude")
    expect(page.locator("#suite")).to_have_value(str(failed["id"]))
    page.locator("#suite").select_option(str(passed["id"]))
    expect(page.locator("#stage-run")).to_contain_text("通过")
    expect(page.locator("#target-signature")).to_contain_text("signed_magnitude")
    for width, height in ((1440, 900), (1024, 768), (768, 1024), (390, 844)):
        page.set_viewport_size({"width": width, "height": height})
        assert page.evaluate("document.documentElement.scrollWidth === innerWidth")
        assert page.locator(".gen-center").bounding_box()["width"] > 220
        if width == 768:
            page.locator("#gen-output").scroll_into_view_if_needed()
            capture(page, "tablet-suite")
        if width == 390:
            page.locator(".gen-jump a[href='#gen-output']").click()
            capture(page, "mobile-suite")
            page.locator("#gen-console").scroll_into_view_if_needed()
            capture(page, "mobile-console")
        record("F03_VIEW", {"width": width, "height": height,
                            "center": round(page.locator(".gen-center").bounding_box()["width"]),
                            "engine": page.context.browser.version})
    page.locator("#run-suite").click()
    expect(page.locator("#run-identity")).to_contain_text(f"运行 #{passed['initial_run']['id']}")

    page.goto(base + f"&suite={passed['id']}")
    page.locator("#file").select_option(str(newer["id"]))
    expect(page.locator("#gen-revision")).to_have_text(f"v2 · #{newer['id']}")
    expect(page.locator("#run-suite")).not_to_be_visible()
    page.goto(f"/workbench/generation?project={project['id']}&file={newer['id']}&suite={passed['id']}")
    expect(page.locator("#suite-empty")).to_contain_text("套件不属于当前版本")
    expect(page.locator("#suite-panel")).not_to_be_visible()


def test_rejected_generation_and_unavailable_context(studio):
    page = studio
    project = post_json(page, "/api/projects", {"name": "边界验收"})
    file = upload(page, project["id"], "unavailable.py", REJECTED)
    base = f"/workbench/generation?project={project['id']}&file={file['id']}"
    page.goto(base + "&symbol=conditional")
    expect(page.locator("#target option")).to_have_text(["keep", "no_contract"])
    expect(page.locator("#generate-button")).to_be_disabled()
    expect(page.locator("#target-empty")).to_contain_text("链接中的函数不可生成")
    page.get_by_label("目标函数").select_option("no_contract")
    rejected = submit(page, status=422)
    assert "缺少可验证契约" in rejected["detail"]
    expect(page.locator("#stage-request")).to_have_text("请求失败")
    expect(page.locator("#stage-static")).to_have_text("暂无记录")
    expect(page.locator("#stage-run")).to_have_text("暂无记录")
    expect(page.locator("#notice")).to_contain_text(rejected["detail"])
    assert page.request.get(f"/api/files/{file['id']}/suites").json() == []
    capture(page, "desktop-rejected")
    invalid = upload(page, project["id"], "invalid.py", "def invalid(")
    page.reload()
    page.locator("#file").select_option(str(invalid["id"]))
    expect(page.locator("#target-empty")).to_contain_text("源码分析未通过")
    expect(page.locator("#generate-button")).to_be_disabled()
    page.goto(f"/workbench/generation?project=9999&file={file['id']}")
    expect(page.locator("#target-empty")).to_contain_text("当前来源版本不可用")
    expect(page.locator("#run-suite")).not_to_be_visible()


@pytest.fixture
def occupied_service(tmp_path):
    """Serve the real app while this test owns F04's process-local semaphore."""
    application = create_app(db_path=tmp_path / "f03-busy.sqlite3")
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        url = f"http://127.0.0.1:{listener.getsockname()[1]}"
        server = uvicorn.Server(uvicorn.Config(application, log_level="warning"))
        thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
        thread.start()
        try:
            deadline = time.monotonic() + 10
            while not server.started and thread.is_alive() and time.monotonic() < deadline:
                time.sleep(0.05)
            assert server.started
            yield url
        finally:
            server.should_exit = True
            thread.join(10)
            assert not thread.is_alive()


def test_busy_saves_candidate_without_first_run(studio, occupied_service):
    page = studio
    root = occupied_service
    project = post_json(page, root + "/api/projects", {"name": "执行槽验收"})
    files = root + f"/api/projects/{project['id']}/files"
    file = post_json(page, files, {"filename": "measurements.py", "source": SAMPLE})
    base = root + f"/api/files/{file['id']}"
    page.goto(root + f"/workbench/generation?project={project['id']}&file={file['id']}&symbol=magnitude")
    expect(page.locator("#generate-button")).to_be_enabled()
    assert runs.SLOTS.acquire(blocking=False)
    try:
        error = submit(page, status=409)
        assert "受限运行在进行" in error["detail"]
        expect(page.locator("#stage-request")).to_have_text("执行器忙")
        expect(page.locator("#stage-static")).to_have_text("已通过")
        expect(page.locator("#stage-run")).to_have_text("尚无记录")
        expect(page.locator("#initial-status")).to_have_text("尚无首次执行记录。")
        rows = page.request.get(base + "/suites").json()
        assert len(rows) == 1
        candidate = page.request.get(root + f"/api/suites/{rows[0]['id']}").json()
        assert candidate["format_checked"] and candidate["initial_run"] is None
        assert page.request.get(root + f"/api/projects/{project['id']}/runs").json() == []
        assert "run" not in parse_qs(urlsplit(page.locator("#run-suite").get_attribute("href")).query)
        capture(page, "desktop-busy")
    finally:
        runs.SLOTS.release()
    saved = submit(page)
    assert saved["id"] == candidate["id"]
    assert saved["initial_run"]["status"] == "passed"
    expect(page.locator("#stage-run")).to_have_text("通过 #1")
    record("F03_BUSY_RECOVERY", {"project_id": project["id"], "file_id": file["id"],
                                 "suite_id": saved["id"], "run_id": saved["initial_run"]["id"]})
