"""WP03-AST-VISUAL-REFINE-001. User-facing console state and the browser timer."""

import os
import re
from pathlib import Path

from playwright.sync_api import expect

from test_ast_studio import import_large_graph, open_file, post_json, record, studio, upload, wait_complete
from test_dashboard import app_url


def test_console_and_timing_source(studio):
    page = studio
    page.emulate_media(reduced_motion="reduce")
    project = post_json(page, "/api/projects", {"name": "Console regression"})
    file = upload(page, project["id"], "sample.py", "def apply(value):\n    return value\n")
    requests = []
    endpoint = f"/api/files/{file['id']}/analysis"
    page.on("request", lambda request: requests.append(request.method) if request.url.endswith(endpoint) else None)

    # Keep the real response. Delay only fulfillment of the browser's JSON promise
    # so a server-only or response-header-only timer cannot pass this check.
    page.add_init_script("""const readJSON = Response.prototype.json;
        Response.prototype.json = async function(...args) {
            const data = await readJSON.apply(this, args);
            if (this.ok && new URL(this.url).pathname.endsWith('/analysis')) {
                await new Promise(resolve => setTimeout(resolve, 220));
            }
            return data;
        };""")
    open_file(page, file)
    timer = page.locator("#ast-timing")
    label = timer.inner_text()
    measured = re.fullmatch(r"分析请求（浏览器端）\s+(\d+)\s+ms", label)
    assert measured and int(measured[1]) >= 200, label
    assert requests == ["GET"]
    expect(timer).to_have_attribute("title", re.compile("JSON"))
    page.set_viewport_size({"width": 390, "height": 844})
    body = page.locator("#ast-console-body")
    header = page.locator("#ast-console-toggle")
    canvas = page.locator("#ast-canvas")
    expect(body).to_be_visible()
    open_height = canvas.bounding_box()["height"]
    selected_before_fold = canvas.get_attribute("data-selected")
    header.click()
    expect(body).to_be_hidden()
    expect(page.locator("#ast-stage")).to_be_visible()
    assert canvas.bounding_box()["height"] > open_height
    assert page.evaluate("document.documentElement.scrollWidth === innerWidth")
    header.press("Enter")
    expect(body).to_be_visible()
    assert canvas.get_attribute("data-selected") == selected_before_fold
    page.locator("#ast-replay").click()
    wait_complete(page)
    expect(timer).to_have_text(label)
    assert requests == ["GET"]
    page.reload()
    wait_complete(page)
    expect(timer).to_have_text("已读取本机分析快照")
    assert requests == ["GET"]

    page.route("**" + endpoint, lambda route: route.fulfill(
        status=503, content_type="application/json", body='{"detail":"Console regression 503"}'), times=1)
    page.locator("#ast-refresh").click()
    expect(page.locator("#ast-stage")).to_have_text("ERROR")
    expect(page.locator("#notice")).to_contain_text("Console regression 503")
    expect(timer).to_have_text("")
    page.locator("#ast-refresh").click()
    wait_complete(page)
    expect(timer).to_contain_text("分析请求（浏览器端）")
    assert requests == ["GET", "GET", "GET"]
    record("CONSOLE_REGRESSION", {"project": project["id"], "file": file["id"],
                                  "revision": file["revision"], "delayInjectedMs": 220,
                                  "timerWithInjectionMs": int(measured[1]), "requests": requests})


def test_fit_and_focus_last_dense_symbol(studio):
    page = studio
    page.emulate_media(reduced_motion="reduce")
    file = import_large_graph(page)
    open_file(page, file)
    expect(page.locator("#ast-node-count")).to_have_text("1000")
    expect(page.locator("#ast-edge-count")).to_have_text("999")
    output = os.environ.get("TESTPILOT_AST_REFINE_CAPTURE_DIR")
    if output:
        Path(output).mkdir(parents=True, exist_ok=True)
        page.screenshot(path=Path(output) / "large-real-layout.png")

    symbol = "Channel26.signal35"
    search = page.locator("#ast-search")
    search.fill(symbol)
    search.press("Enter")
    expect(page.locator("#ast-selected")).to_have_text(symbol)
    expect(page.locator("#inspector-body")).to_contain_text(symbol)
    expect(page.locator("#inspector-body")).to_contain_text("第 999–999 行")
    tree_selection = page.locator('#symbols [aria-pressed="true"]')
    expect(tree_selection).to_contain_text("signal35")
    row = tree_selection.bounding_box()
    scroller = page.locator(".explorer-scroll").bounding_box()
    assert row["y"] >= scroller["y"] - 1
    assert row["y"] + row["height"] <= scroller["y"] + scroller["height"] + 1
    if output:
        page.screenshot(path=Path(output) / "large-real-focus.png")


def test_replay_camera_pauses_with_presentation(studio):
    page = studio
    page.emulate_media(reduced_motion="no-preference")
    project = post_json(page, "/api/projects", {"name": "Replay camera"})
    file = upload(page, project["id"], "camera.py",
                  "class Sensor:\n    def read(self): pass\ndef convert(): return 1\n")
    open_file(page, file)
    zoom = page.locator("#ast-zoom")
    fitted = zoom.inner_text()
    selected = page.locator("#ast-canvas").get_attribute("data-selected")
    page.locator("#ast-plus").click(click_count=3)
    expect(zoom).not_to_have_text(fitted)
    start = zoom.inner_text()
    page.locator("#ast-replay").click()
    # Pause at the first observed change in the displayed camera scale, even on
    # a slow CI host. Animation and zoom are read through the public interface.
    page.wait_for_function("""initial => {
        const scale = document.querySelector('#ast-zoom').textContent;
        if (scale === initial) return false;
        document.querySelector('#ast-pause').click();
        return true;
    }""", arg=start)
    expect(page.locator("#ast-stage")).to_contain_text("已暂停")
    paused = zoom.inner_text()
    assert paused not in (start, fitted)
    page.wait_for_timeout(650)  # Longer than the entire camera move.
    expect(zoom).to_have_text(paused)
    page.locator("#ast-pause").click()
    wait_complete(page)
    expect(zoom).to_have_text(fitted)
    expect(page.locator("#ast-canvas")).to_have_attribute("data-selected", selected)
    record("REPLAY_CAMERA", {"zoomed": start, "paused": paused, "complete": fitted})
