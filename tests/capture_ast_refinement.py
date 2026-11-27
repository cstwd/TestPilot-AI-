"""Manual headed F02 acceptance. Run this file explicitly with pytest and an empty output directory."""

import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import playwright
from playwright.sync_api import expect, sync_playwright

from test_dashboard import ROOT, app_url


VIEW = {"width": 1440, "height": 900}
SAMPLE = ROOT / "eval/ast_visual/telemetry.py"


def local_video_encoder(tmp_path, monkeypatch):
    """A local system FFmpeg also works when the optional Playwright encoder is absent."""
    registry = Path(playwright.__file__).parent / "driver/package/browsers.json"
    packages = json.loads(registry.read_text(encoding="utf-8"))["browsers"]
    revision = next(p["revision"] for p in packages if p["name"] == "ffmpeg")
    executable = Path("ffmpeg-" + revision) / "ffmpeg-win64.exe"
    cache = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", Path.home() / "AppData/Local/ms-playwright"))
    if (cache / executable).is_file():
        return
    binary = shutil.which("ffmpeg")
    if not binary:
        raise RuntimeError("Install the local Playwright FFmpeg encoder or put ffmpeg.exe on PATH.")
    private_cache = tmp_path / "video-encoder"
    target = private_cache / executable
    target.parent.mkdir(parents=True)
    shutil.copyfile(binary, target)
    monkeypatch.setenv("PLAYWRIGHT_BROWSERS_PATH", str(private_cache))


def test_record_headed_session(app_url, tmp_path, monkeypatch):
    out = Path(os.environ["TESTPILOT_AST_REFINE_CAPTURE_DIR"]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if any(out.glob("screenshots/*.png")) or any(out.glob("video/*.mp4")):
        raise FileExistsError("Choose an empty output folder to preserve the previous capture.")
    shots = out / "screenshots"
    shots.mkdir(exist_ok=True)
    video_dir = out / "video"
    video_dir.mkdir(exist_ok=True)
    local_video_encoder(tmp_path, monkeypatch)
    stages, analysis_requests, errors = [], [], []
    digest = hashlib.sha256(SAMPLE.read_bytes()).hexdigest()
    with sync_playwright() as driver:
        browser = driver.chromium.launch(channel="msedge", headless=False, args=["--enable-automation"])
        command = browser.new_browser_cdp_session().send("Browser.getBrowserCommandLine")["arguments"]
        assert not any(arg.startswith("--headless") for arg in command)
        context = browser.new_context(base_url=app_url, viewport=VIEW, screen=VIEW,
                                      device_scale_factor=1, reduced_motion="no-preference",
                                      record_video_dir=tmp_path / "footage", record_video_size=VIEW)
        start = time.monotonic()
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        stage = page.locator("#ast-stage")
        canvas = page.locator("#ast-canvas")
        inspector = page.locator("#inspector-body")

        def mark(label):
            stages.append([round(time.monotonic() - start, 2), label])

        def shot(label, expected_stage=None):
            if expected_stage:
                expect(stage).to_contain_text(expected_stage)
            mark(label)
            page.screenshot(path=shots / (label + ".png"), animations="allow")
            if expected_stage:
                assert expected_stage in stage.inner_text(), label

        def complete():
            expect(stage).to_have_text("COMPLETE", timeout=15000)

        page.goto("/workbench/projects")
        page.get_by_label("项目名称").fill("Telemetry Lab")
        page.get_by_role("button", name="创建项目").click()
        expect(page.locator("#project option:checked")).to_have_text("Telemetry Lab")
        page.get_by_label("本地文件").set_input_files(SAMPLE)
        page.get_by_role("button", name="导入文件").click()
        expect(page.locator("#digest")).to_contain_text(digest)
        mark("F01 imported")
        page.wait_for_timeout(850)

        # Only this request gets extra transport latency. The actual server sends its own JSON.
        cdp = context.new_cdp_session(page)
        cdp.send("Network.enable")
        cdp.send("Network.emulateNetworkConditionsByRule", {
            "offline": False, "matchedNetworkConditions": [
                {"urlPattern": app_url + "/api/files/*/analysis", "latency": 1600,
                 "downloadThroughput": -1, "uploadThroughput": -1},
            ],
        })
        result_path = "/api/files/1/analysis"
        page.on("request", lambda req: analysis_requests.append(req.url)
                if urlsplit(req.url).path == result_path else None)
        with page.expect_response(lambda resp: urlsplit(resp.url).path == result_path) as response:
            page.get_by_role("link", name="分析此版本").click()
            expect(page.locator("#ast-status")).to_have_text("分析请求中")
            shot("01-request", "SCANNING")
        assert response.value.ok
        model = response.value.json()
        assert model["file_id"] == model["revision"] == 1 and model["sha256"] == digest
        expect(stage).to_have_text("PARSING")
        page.wait_for_timeout(255)
        shot("02-nodes", "PARSING")
        expect(stage).to_have_text("STRUCTURE BUILDING")
        page.wait_for_timeout(320)
        shot("03-edges", "STRUCTURE BUILDING")
        complete()
        current_timing = page.locator("#ast-timing").inner_text()
        assert re.search(r"\d+ ms", current_timing)
        assert len(model["symbols"]) == 15
        expect(page.locator("#ast-node-count")).to_have_text("16")
        expect(page.locator("#ast-edge-count")).to_have_text("15")
        mark("COMPLETE initial")
        page.wait_for_timeout(700)
        sample = page.locator('#symbols [data-node-id$=":3:Sample"]')
        sample.click()
        page.wait_for_timeout(480)
        box = canvas.bounding_box()
        canvas.dblclick(position={"x": box["width"] / 2, "y": box["height"] / 2})
        expect(canvas).to_have_attribute("data-selected", "symbol:1:3:Sample")
        page.wait_for_timeout(350)
        shot("04-neighborhood")
        inspector.get_by_role("tab", name="Structure").click()
        inspector.get_by_role("button", name=re.compile("normalized")).click()
        expect(canvas).to_have_attribute("data-selected", "symbol:1:10:Sample.normalized")
        inspector.get_by_role("tab", name="Source").click()
        expect(inspector.locator('[data-line="10"][data-range]')).to_contain_text("def normalized")
        page.wait_for_timeout(500)
        shot("05-source")
        page.wait_for_timeout(850)
        # Replay from a zoomed, non-central view so the camera transition is visible.
        page.locator("#ast-plus").click()
        page.wait_for_timeout(400)
        zoom_start = page.locator("#ast-zoom").inner_text()
        page.locator("#ast-replay").click()
        mark("replay")
        expect(stage).to_have_text("STRUCTURE BUILDING")
        page.wait_for_timeout(280)
        page.locator("#ast-pause").click()
        expect(stage).to_contain_text("已暂停")
        frozen = canvas.evaluate("el => el.toDataURL()")
        shot("06-paused", "已暂停")
        page.wait_for_timeout(850)
        assert frozen == canvas.evaluate("el => el.toDataURL()")
        page.locator("#ast-pause").click()
        mark("resume")
        complete()
        assert len(analysis_requests) == 1
        assert page.locator("#ast-timing").inner_text() == current_timing
        zoom_end = page.locator("#ast-zoom").inner_text()
        shot("07-replay-complete", "COMPLETE")
        page.locator("#ast-console-toggle").click()
        expect(page.locator("#ast-console-body")).not_to_be_visible()
        shot("08-console-folded", "COMPLETE")
        page.wait_for_timeout(500)
        page.locator("#ast-console-toggle").click()
        expect(page.locator("#ast-console-body")).to_be_visible()
        page.locator("#ast-search").fill("mean_value")
        page.locator("#ast-matches button[data-node-id]").first.click()
        selected = canvas.get_attribute("data-selected")
        saved_url = page.url
        page.reload()
        complete()
        expect(canvas).to_have_attribute("data-selected", selected)
        expect(page.locator("#ast-timing")).to_contain_text("本机分析快照")
        assert len(analysis_requests) == 1
        mark("restored mean_value")
        page.locator("#ast-generation").click()
        expect(page.get_by_label("目标函数")).to_have_value("mean_value")
        target = parse_qs(urlsplit(page.url).query)
        assert target == {"project": ["1"], "file": ["1"], "symbol": ["mean_value"]}
        mark("F03")
        page.wait_for_timeout(800)
        video = page.video
        context.close()
        recording = video.path()

        # Record the narrow viewport separately; the video stays at its native desktop dimensions.
        narrow = browser.new_page(base_url=app_url, viewport={"width": 390, "height": 844})
        narrow.goto(saved_url)
        expect(narrow.locator("#ast-stage")).to_have_text("COMPLETE")
        expect(narrow.locator("#ast-canvas")).to_have_attribute("data-selected", selected)
        assert narrow.evaluate("document.documentElement.scrollWidth === innerWidth")
        narrow.screenshot(path=shots / "09-mobile.png")
        browser_version = browser.version
        browser.close()
    assert not errors, errors
    movie = video_dir / "analysis-session.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-n", "-i", str(recording), "-an",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", str(movie)], check=True)
    print(json.dumps({"engine": browser_version, "digest": digest, "timing": current_timing,
                      "zoom_before_replay": zoom_start, "zoom_after_replay": zoom_end,
                      "F03": target, "timeline": stages, "video_bytes": movie.stat().st_size},
                     ensure_ascii=True))
