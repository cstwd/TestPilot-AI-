"""WP04-F01-001. Drive the public workspace and compare each selection to its SQLite-backed API."""

import hashlib
import os
import re
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect

from test_ast_studio import TELEMETRY, graph_model, post_json, record, studio, upload, wait_complete
from test_dashboard import app_url


PROJECTS = "/workbench/projects"
SECOND = TELEMETRY + '\n\ndef pipeline_ready() -> bool:\n    """第二版采集检查。"""\n    return True\n'
LONG_NAME = "山地观测站气象传感器遥测数据采样频率与时间戳偏差校验报告生成工具_多通道合并与数据缺失处理_二批实验.py"


def capture(page, name):
    folder = os.environ.get("TESTPILOT_F01_CAPTURE_DIR")
    if folder:
        target = Path(folder)
        target.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=target / (name + ".png"), animations="disabled")


def submit_file(page, filename, raw):
    page.get_by_label("本地文件").set_input_files(
        {"name": filename, "mimeType": "text/plain", "buffer": raw})
    page.get_by_role("button", name="导入文件", exact=True).click()


def import_revision(page, project_id, source):
    api_path = f"/api/projects/{project_id}/files"
    with page.expect_response(lambda r: urlsplit(r.url).path == api_path and r.request.method == "POST") as response:
        submit_file(page, "telemetry.py", source.encode("utf-8"))
    assert response.value.status == 200
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    expect(page.locator("#digest")).to_contain_text(digest)
    row = page.request.get("/api/files/" + page.locator("#file").input_value()).json()
    assert row["project_id"] == project_id and row["source"] == source
    assert row["sha256"] == digest
    return row


def check_identity(page, row):
    shown_id = re.compile(rf"(?<!\d){row['id']}(?!\d)")
    for element in ("#file-id", "#file-version-id"):
        expect(page.locator(element)).to_contain_text(shown_id)
    expect(page.locator("#revision")).to_contain_text(str(row["revision"]))
    expect(page.locator("#digest")).to_contain_text(row["sha256"])
    expect(page.locator("#inspect-file")).to_have_text(row["filename"])
    expect(page.locator("#analyze-version")).to_have_attribute(
        "href", f"/workbench/analysis?project={row['project_id']}&file={row['id']}")
    assert page.locator("#source").text_content() == row["source"]
    assert not page.locator("#source").evaluate("node => node.isContentEditable")
    expect(page.locator("#file-byte-size")).to_contain_text(
        re.compile(f"{len(row['source'].encode('utf-8')):,}".replace(",", "[,， ]?")))


def test_import_history_and_analysis(studio):
    page = studio
    page.emulate_media(reduced_motion="reduce")
    # Two real auxiliary projects keep the populated Explorer useful for search.
    for name in ("边界样例", "排序回归"):
        post_json(page, "/api/projects", {"name": name})
    page.goto(PROJECTS)
    expect(page.locator("#connection-state")).to_have_text("已连接")
    page.get_by_label("项目名称", exact=True).fill("Telemetry Lab")
    with page.expect_response(lambda r: urlsplit(r.url).path == "/api/projects" and r.request.method == "POST") as created:
        page.get_by_role("button", name="创建项目", exact=True).click()
    assert created.value.status == 201
    expect(page.locator("#project option:checked")).to_have_text("Telemetry Lab")
    project = next(p for p in page.request.get("/api/projects").json() if p["name"] == "Telemetry Lab")
    expect(page.locator("#project")).to_have_value(str(project["id"]))
    expect(page.locator("#analyze-version")).not_to_be_visible()
    first = import_revision(page, project["id"], TELEMETRY)
    repeated = import_revision(page, project["id"], TELEMETRY)
    assert first == repeated and first["revision"] == 1
    second = import_revision(page, project["id"], SECOND)
    assert second["revision"] == 2 and first["id"] != second["id"]
    check_identity(page, second)
    entries = page.request.get(f"/api/projects/{project['id']}/files").json()
    assert [r["id"] for r in entries] == [second["id"], first["id"]]
    upload(page, project["id"], "magnitude.py", "def magnitude(x):\n    return abs(x)\n")
    page.reload()
    page.locator("#file").select_option(str(second["id"]))
    expect(page.locator("#digest")).to_contain_text(second["sha256"])
    expect(page.locator("#inspect-project")).to_have_text(project["name"])
    page.locator("#project-search").fill("Telemetry")
    expect(page.locator(".project-row")).to_have_count(1)
    page.locator("#project-search").fill("")
    expect(page.locator(".project-row")).to_have_count(3)
    page.locator("#file-search").fill("magnitude")
    expect(page.locator("a[data-file-latest]")).to_have_count(1)
    expect(page.locator("a[data-file-latest]")).to_contain_text("magnitude")
    page.locator("#file-search").fill("")
    expect(page.locator("a[data-file-latest]")).to_have_count(2)
    toggle = page.locator('button[data-group-toggle="telemetry.py"]')
    if toggle.get_attribute("aria-expanded") == "true":
        toggle.click()
    expect(toggle).to_have_attribute("aria-expanded", "false")
    toggle.click()
    expect(toggle).to_have_attribute("aria-expanded", "true")
    old = page.locator(f'a[data-file-id="{first["id"]}"]')
    expect(old).to_be_visible()
    capture(page, "desktop-versions")
    page.set_viewport_size({"width": 390, "height": 844})
    page.locator('#project-panels [data-panel="files"]').click()
    capture(page, "mobile-telemetry-versions")
    page.locator('#project-panels [data-panel="details"]').click()
    action = page.locator("#analyze-version").bounding_box()
    assert action and action["y"] > 0 and action["y"] + action["height"] <= 844
    capture(page, "mobile-telemetry-source")
    page.set_viewport_size({"width": 1440, "height": 900})
    old.click()
    check_identity(page, first)
    page.context.grant_permissions(["clipboard-read", "clipboard-write"])
    page.evaluate("""() => {
        const write = navigator.clipboard.writeText.bind(navigator.clipboard);
        navigator.clipboard.writeText = value => { window.copiedSource = value; return write(value); };
    }""")
    page.locator("#copy-source").click()
    expect(page.locator("#notice")).to_contain_text("已复制")
    assert page.evaluate("window.copiedSource") == first["source"]
    # The Windows clipboard exposes platform CRLF when reading back text.
    assert page.evaluate("navigator.clipboard.readText()").replace("\r\n", "\n") == first["source"]
    for row in (first, second):
        page.locator("#file").select_option(str(row["id"]))
        expect(page.locator("#digest")).to_contain_text(row["sha256"])
        page.reload()
        expect(page.locator("#digest")).to_contain_text(row["sha256"])
        check_identity(page, row)
        page.locator("#analyze-version").click()
        wait_complete(page)
        params = parse_qs(urlsplit(page.url).query)
        assert params["project"] == [str(project["id"])] and params["file"] == [str(row["id"])]
        graph = graph_model(page, row["id"])
        assert all(node["file_id"] == node["version_id"] == row["id"] for node in graph["nodes"])
        assert all(node["revision"] == row["revision"] for node in graph["nodes"])
        is_second = row["id"] == second["id"]
        assert ("pipeline_ready" in [n["qualified_name"] for n in graph["nodes"]]) == is_second
        expect(page.locator("#ast-node-count")).to_have_text("17" if is_second else "16")
        expect(page.locator("#ast-edge-count")).to_have_text("16" if is_second else "15")
        if is_second:
            page.locator("#ast-search").fill("pipeline_ready")
            page.locator("#ast-search").press("Enter")
            page.locator("#ast-generation").click()
            expect(page.get_by_label("目标函数")).to_have_value("pipeline_ready")
            assert parse_qs(urlsplit(page.url).query) == {
                "project": [str(project["id"])], "file": [str(row["id"])], "symbol": ["pipeline_ready"]}
        else:
            page.go_back()
            expect(page.locator("#file")).to_have_value(str(first["id"]))
    record("F01_REVISIONS", {"project": project["id"], "rows": [
        {k:r[k] for k in ("id","revision","sha256")} for r in (first, repeated, second)],
        "bytes": [len(text.encode("utf-8")) for text in (TELEMETRY, SECOND)]})


def test_empty_invalid_network_and_membership(studio):
    page = studio
    page.goto(PROJECTS)
    expect(page.locator("#import-button")).to_be_disabled()
    expect(page.locator("#analyze-version")).not_to_be_visible()
    capture(page, "empty")
    page.get_by_label("项目名称", exact=True).fill("导入检查")
    page.get_by_role("button", name="创建项目", exact=True).click()
    expect(page.locator("#project option:checked")).to_have_text("导入检查")
    project = int(page.locator("#project").input_value())
    for name, raw, warning in [
        ("fail.txt", b"x=1", "py"), ("fail.py", b"\xff", "UTF-8"), ("fail.py", b"x" * 131073, "128 KiB"),
        ("fail.py", b"x\0y", "NUL")]:
        submit_file(page, name, raw)
        expect(page.locator("#notice")).to_contain_text(warning)
        expect(page.locator("#analyze-version")).not_to_be_visible()
    assert page.request.get(f"/api/projects/{project}/files").json() == []
    upload(page, project, "own.py", "local_value = 1\n")
    other = post_json(page, "/api/projects", {"name": "独立项目"})
    foreign = upload(page, other["id"], "private.py", "token='ISOLATED_CONTENT'\n")
    for address in (f"{PROJECTS}?project={project}&file={foreign['id']}",
                    f"{PROJECTS}?project=9999&file={foreign['id']}"):
        page.goto(address)
        expect(page.locator("#notice")).to_have_attribute("data-error", "")
        expect(page.locator("#analyze-version")).not_to_be_visible()
        expect(page.locator("#source-panel")).to_be_hidden()
        assert page.locator("#analyze-version").get_attribute("href") is None
        expect(page.locator("body")).not_to_contain_text("ISOLATED_CONTENT")
    src_url = f"/api/files/{foreign['id']}"
    page.route("**" + src_url, lambda route: route.fulfill(
        status=503, content_type="application/json", body='{"detail":"F01 test outage"}'), times=1)
    page.goto(f"{PROJECTS}?project={other['id']}&file={foreign['id']}")
    expect(page.locator("#notice")).to_contain_text("F01 test outage")
    expect(page.locator("#analyze-version")).not_to_be_visible()
    capture(page, "network-error")
    page.locator("#project-retry").click()
    expect(page.locator("#source")).to_contain_text("ISOLATED_CONTENT")
    check_identity(page, foreign)


def test_project_navigation_and_long_filename(studio):
    page = studio
    project = post_json(page, "/api/projects", {"name": "中文文件验收"})
    empty = post_json(page, "/api/projects", {"name": "空白项目"})
    source = 'channel = "山地气象站"\nlegend = "<b>湿度</b>"\n# 遥测数据\n'
    row = upload(page, project["id"], LONG_NAME, source)
    page.goto(f"{PROJECTS}?project={project['id']}&file={row['id']}")
    check_identity(page, row)
    expect(page.locator("#source b")).to_have_count(0)
    page.locator(f'.project-row[data-project-id="{empty["id"]}"]').click()
    expect(page.locator("#project")).to_have_value(str(empty["id"]))
    expect(page.locator("#analyze-version")).not_to_be_visible()
    page.locator(f'.project-row[data-project-id="{project["id"]}"]').click()
    expect(page.locator("#digest")).to_contain_text(row["sha256"])
    for width, height in ((1440, 900), (1024, 768), (768, 1024), (390, 844)):
        page.set_viewport_size({"width": width, "height": height})
        nav = page.locator("#project-panels")
        if nav.is_visible():
            for panel in ("projects", "files", "details"):
                nav.locator(f'button[data-panel="{panel}"]').click()
                visible_item = {"projects": "#project-search", "files": "#file-search", "details": "#digest"}[panel]
                element = page.locator(visible_item)
                expect(element).to_be_visible()
                assert element.bounding_box()["width"] > 45
                assert page.evaluate("document.documentElement.scrollWidth === innerWidth")
                if width == 390:
                    capture(page, "mobile-" + panel)
        digest = page.locator("#digest")
        expect(digest).to_be_visible()
        assert digest.evaluate("n => n.scrollWidth <= n.clientWidth + 1")
        assert page.evaluate("document.documentElement.scrollWidth === innerWidth")
        if width == 768:
            capture(page, "tablet-inspector")
        record("F01_VIEW", {"viewport": [width,height], "digestWidth": round(digest.bounding_box()["width"]),
                            "name": len(LONG_NAME), "engine": page.context.browser.version})
