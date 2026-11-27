"""WP09-001. Cross-page acceptance against real local FastAPI, SQLite and Edge."""
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect

from test_ast_studio import studio, post_json, upload, record
from test_dashboard import app_url


MODULES = ("projects", "analysis", "generation", "runs", "bugs", "reports")
VIEWS = ((1920, 1080), (1440, 900), (1280, 800), (1024, 768), (768, 1024), (390, 844))
SAMPLE = """class Sample:
    def __init__(self, value):
        self.value = value


def magnitude(value: float) -> float:
    \"\"\"Return the magnitude of a signed measurement.

    >>> magnitude(-2)
    2
    >>> magnitude(-3)
    3
    \"\"\"
    return value


def doubled(value: float) -> float:
    return value * 2
"""
FIXED = SAMPLE.replace("return value\n", "return abs(value)\n")
SYMBOL = "magnitude"
NODEID = "test_generated.py::test_example_2"


def test_mobile_module_navigation(studio):
    page = studio
    page.set_viewport_size({"width": 390, "height": 844})
    project = post_json(page, "/api/projects", {"name": "通用导航探针"})["id"]
    row = upload(page, project, "probe.py", "def probe():\n    return 1\n")
    missing = []
    for name in MODULES:
        page.goto(f"/workbench/{name}?project={project}&file={row['id']}")
        expect(page.locator("#file")).to_have_value(str(row["id"]))
        handle = page.locator('.topbar summary[aria-label="工作台导航"]')
        if not handle.count():
            missing.append(name)
            record("WP09_NAV", {"page": name, "menu": "missing"})
            continue
        expect(handle).to_be_visible()
        handle.press("Enter")
        menu = handle.locator("..")
        expect(menu.locator("[data-dest]")).to_have_count(6)
        expect(menu.locator("[aria-current=page]")).to_have_attribute("data-dest", name)
        ids = {}
        for slug in MODULES:
            href = menu.locator(f'[data-dest="{slug}"]').get_attribute("href")
            ids[slug] = parse_qs(urlsplit(href).query)
            assert ids[slug] == {"project": [str(project)], "file": [str(row["id"])]}
        handle.press("Escape")
        expect(menu).not_to_have_attribute("open", "")
        handle.press("Space")
        expect(menu).to_have_attribute("open", "")
        page.locator("h1").click()
        if menu.get_attribute("open") is not None:
            missing.append(name + ":outside")
        record("WP09_NAV", {"page": name, "targets": len(ids), "outsideClosed": menu.get_attribute("open") is None})
    assert not missing, missing
    file_list = f"**/api/projects/{project}/files"
    page.route(file_list, lambda route: route.fulfill(status=503, json={"detail": "WP09 文件列表故障注入"}))
    page.goto(f"/workbench/projects?project={project}&file={row['id']}")
    expect(page.locator("#project")).to_have_value(str(project))
    page.locator("#mobile-navigation summary").click()
    links = page.locator("#mobile-navigation [data-dest]").evaluate_all("nodes => nodes.map(node => node.href)")
    assert len(links) == 6
    assert all(parse_qs(urlsplit(href).query) == {"project": [str(project)]} for href in links)
    page.unroute(file_list)
    record("WP09_NAV_FILE_ERROR", {"project": project, "targets": len(links), "http": 503, "fixture": "fault injection"})

def get(page, endpoint):
    result = page.request.get(endpoint, timeout=120_000)
    assert result.ok, result.text()
    return result.json()


def query(page):
    return {key: values[0] for key, values in parse_qs(urlsplit(page.url).query).items()}


def expect_route(page, *, project, file, **extra):
    values = {k: str(v) for k, v in {"project": project, "file": file, **extra}.items()}
    page.wait_for_url(lambda url: all(parse_qs(urlsplit(url).query).get(key) == [value] for key, value in values.items()))


def save(page, name):
    if target := os.getenv("TESTPILOT_WP09_CAPTURE"):
        directory = Path(target) / "screenshots"
        directory.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=directory / (name + ".png"), animations="disabled")


def responsive(page, module, surface, switch=None):
    measures = []
    for width, height in VIEWS:
        page.set_viewport_size({"width": width, "height": height})
        if switch:
            tab = page.locator(switch)
            if tab.is_visible():
                tab.click()
        item = page.locator(surface)
        expect(item).to_be_visible()
        style = page.evaluate("""selector => {
          const el=document.querySelector(selector), rect=el.getBoundingClientRect();
          return {width:Math.round(rect.width), height:Math.round(rect.height),
            page:document.documentElement.scrollWidth, topbar:Math.round(document.querySelector('.topbar').getBoundingClientRect().height),
            panel:getComputedStyle(document.documentElement).getPropertyValue('--panel').trim(),
            ink:getComputedStyle(document.documentElement).getPropertyValue('--ink').trim(),
            duplicated:[...document.querySelectorAll('[id]')].map(x=>x.id).filter((id,i,all)=>all.indexOf(id)!==i)};
        }""", surface)
        assert style["page"] == width and style["width"] >= 150 and style["height"] > 20, (module, width, style)
        assert style["panel"] == "#141620" and style["ink"] == "#eef0fa" and not style["duplicated"]
        if width > 650:
            expect(page.locator(".module-rail [aria-current=page]")).to_have_attribute("data-dest", module)
        else:
            expect(page.locator("#mobile-navigation summary")).to_be_visible()
        measures.append({"viewport": [width, height], **style})
        if width in (1440, 390):
            if width == 390:
                item.scroll_into_view_if_needed()
            save(page, f"{module}-{width}x{height}")
    page.set_viewport_size({"width": 1440, "height": 900})
    record("WP09_RESPONSIVE", {"module": module, "surface": surface, "results": measures})


def enter_revision(page, project, source, name="telemetry.py"):
    page.get_by_label("本地文件").set_input_files({"name": name, "mimeType": "text/plain", "buffer": source.encode()})
    page.get_by_role("button", name="导入文件", exact=True).click()
    digest = hashlib.sha256(source.encode()).hexdigest()
    expect(page.locator("#digest-value")).to_have_text(digest)
    selected = int(page.locator("#file").input_value())
    record = get(page, f"/api/files/{selected}")
    assert record["project_id"] == project and record["source"] == source and record["sha256"] == digest
    return record


def check_graph(page, file):
    expect(page.locator("#ast-stage")).to_have_text("COMPLETE", timeout=25_000)
    data = get(page, f"/api/files/{file['id']}/analysis")
    assert data["valid"] and data["sha256"] == file["sha256"]
    expect(page.locator("#ast-node-count")).to_have_text(str(1 + len(data["symbols"])))
    expect(page.locator("#ast-edge-count")).to_have_text(str(len(data["symbols"])))
    [symbol] = [item for item in data["symbols"] if item["name"] == SYMBOL]
    page.locator("#ast-search").fill(SYMBOL)
    page.locator("#ast-search").press("Enter")
    expect(page.locator("#ast-selected")).to_have_text(SYMBOL)
    page.locator("#inspector-body").get_by_role("tab", name="Source").click()
    line = page.locator(f'#inspector-body [data-line="{symbol["line"]}"]')
    expect(line).to_contain_text(f"def {SYMBOL}(")
    return symbol["line"]


def download(page, button, directory, filename, role="button"):
    with page.expect_download() as event:
        page.get_by_role(role, name=button, exact=True).click()
    artifact = event.value
    assert artifact.suggested_filename == filename
    path = directory / filename
    artifact.save_as(path)
    return path


def test_six_page_business_loop(studio, tmp_path):
    page = studio
    page.emulate_media(reduced_motion="reduce")
    console = []
    faults = []
    writes = []
    page.on("console", lambda entry: console.append(entry.text) if entry.type == "error" else None)
    page.on("response", lambda response: faults.append((response.status, response.url))
            if urlsplit(response.url).path.startswith("/api/") and response.status >= 400 else None)
    page.on("request", lambda request: writes.append(urlsplit(request.url).path)
            if request.method == "POST" and urlsplit(request.url).path.startswith("/api/") else None)
    # A separate empty project is used only to verify clearing old context at the end.
    other = post_json(page, "/api/projects", {"name": "WP09 隔离项目"})["id"]
    page.goto("/workbench/projects")
    page.get_by_label("项目名称").fill("WP09 · 遥测质量验收")
    page.get_by_role("button", name="创建项目").click()
    expect(page.locator("#project option:checked")).to_have_text("WP09 · 遥测质量验收")
    project = int(page.locator("#project").input_value())
    before = enter_revision(page, project, SAMPLE)
    after = enter_revision(page, project, FIXED)
    assert (before["revision"], after["revision"]) == (1, 2) and before["id"] != after["id"]
    responsive(page, "projects", "#file-groups", '#project-panels [data-panel="files"]')

    page.get_by_role("link", name="分析此版本").click()
    expect_route(page, project=project, file=after["id"])
    v2_line = check_graph(page, after)
    page.locator("#file").select_option(str(before["id"]))
    expect_route(page, project=project, file=before["id"])
    v1_line = check_graph(page, before)
    assert v1_line == v2_line
    save(page, "analysis-source")
    responsive(page, "analysis", "#ast-canvas", '#ast-panel-nav [data-panel="graph"]')
    page.locator("#ast-generation").click()
    expect_route(page, project=project, file=before["id"], symbol=SYMBOL)
    expect(page.get_by_label("目标函数")).to_have_value(SYMBOL)
    page.go_back()
    expect(page.locator("#ast-selected")).to_have_text(SYMBOL)
    expect_route(page, project=project, file=before["id"])
    page.go_forward()
    expect(page.get_by_label("目标函数")).to_have_value(SYMBOL)
    expect(page.locator("#target-source")).to_contain_text(f"def {SYMBOL}(")
    with page.expect_response(lambda r: r.url.endswith(f"/files/{before['id']}/suites")
                              and r.request.method == "POST", timeout=120_000) as response:
        page.get_by_role("button", name="生成并验证").click()
    posted = response.value
    assert posted.ok and posted.request.post_data_json == {"target": SYMBOL, "mode": "template"}
    expect(page.locator("#stage-static")).to_have_text("已通过", timeout=120_000)
    expect(page.locator("#initial-status")).to_contain_text("失败")
    suite = get(page, "/api/suites/" + query(page)["suite"])
    assert suite["file_id"] == before["id"] and suite["format_checked"] and suite["target"] == SYMBOL
    first_run = get(page, f"/api/runs/{suite['initial_run']['id']}")
    assert first_run["file_id"] == before["id"] and first_run["status"] == "failed"
    responsive(page, "generation", "#suite-panel")

    page.get_by_role("link", name="查看首次执行记录").click()
    expect_route(page, project=project, file=before["id"], run=first_run["id"], suite=suite["id"])
    expect(page.locator("#exec-run-id")).to_have_text(f"#{first_run['id']}")
    with page.expect_response(lambda r: r.url.endswith(f"/suites/{suite['id']}/runs")
                              and r.request.method == "POST", timeout=120_000) as returned:
        page.get_by_role("button", name="执行测试", exact=True).click()
    assert returned.value.ok and returned.value.request.post_data_json == {"file_id": before["id"]}
    page.wait_for_url(lambda url: parse_qs(urlsplit(url).query).get("run") not in (None, [str(first_run["id"])]))
    failure = get(page, "/api/runs/" + query(page)["run"])
    assert (failure["project_id"], failure["file_id"], failure["suite_id"], failure["status"]) == (
        project, before["id"], suite["id"], "failed")
    assert failure["failed"] == 2 and {"nodeid": NODEID, "outcome": "failed"} in failure["cases"]
    expect(page.locator("#run-log")).to_contain_text(NODEID)
    assert page.locator("#run-log").text_content() == failure["log"]
    responsive(page, "runs", "#run-result")
    page.get_by_role("button", name="test_example_2", exact=True).click()
    page.locator("#case-bug").click()
    expect_route(page, project=project, file=before["id"], run=failure["id"], nodeid=NODEID)
    expect(page.locator("#nodeid")).to_have_value(NODEID)
    expect(page.locator("#original-assertion")).to_contain_text("assert target(-3) == 3")
    page.get_by_label("缺陷标题").fill("负数测量值未取绝对值")
    page.get_by_role("button", name="登记缺陷").click()
    expect(page.locator("#bug-state")).to_have_text("待修复")
    bug_id = int(query(page)["bug"])
    expect(page.locator("#fix-file")).to_have_value(str(after["id"]))
    expect(page.locator("#diff-to-sha")).to_contain_text(after["sha256"])
    expect(page.locator("#diff-from-sha")).to_contain_text(before["sha256"])
    expect(page.locator("#diff-lines [data-kind=removed] code")).to_have_text("return value")
    expect(page.locator("#diff-lines [data-kind=added] code")).to_have_text("return abs(value)")
    href = page.locator('.module-rail [data-dest="projects"]').get_attribute("href")
    assert parse_qs(urlsplit(href).query)["file"] == [str(after["id"])]
    original_link = page.locator("#original-run").get_attribute("href")
    assert parse_qs(urlsplit(original_link).query)["file"] == [str(before["id"])]
    responsive(page, "bugs", "#diff-workspace", '.bug-panel-nav [data-panel="diff"]')
    page.get_by_role("button", name="运行回归", exact=True).click()
    page.get_by_role("button", name="确认运行", exact=True).click()
    expect(page.locator("#bug-state")).to_have_text("已解决", timeout=120_000)
    expect(page.locator("#regression-evidence")).to_contain_text("执行通过")
    bug = get(page, f"/api/bugs/{bug_id}")
    [regression] = bug["regressions"]
    assert bug["run_id"] == failure["id"] and bug["suite_id"] == suite["id"] and bug["nodeid"] == NODEID
    assert regression["file_id"] == after["id"] and regression["status"] == bug["status"] == "resolved"
    assert get(page, f"/api/runs/{failure['id']}") == failure
    assert [row["id"] for row in get(page, f"/api/projects/{project}/runs")] == [
        regression["run_id"], failure["id"], first_run["id"]]
    page.locator("#regression-run").click()
    expect_route(page, project=project, file=after["id"], run=regression["run_id"])
    expect(page.locator("#exec-run-state")).to_have_text("执行通过")
    page.locator("#to-report").click()
    expect_route(page, project=project, file=after["id"], run=regression["run_id"])
    path = f"/api/runs/{regression['run_id']}/report"
    snapshot = get(page, path)
    q = snapshot["quality"]
    assert (q["passed"], q["failed"], q["errors"], q["skipped"], q["total"], q["pass_rate_pct"]) == (5, 0, 0, 0, 5, 100)
    repair_run = get(page, f"/api/runs/{regression['run_id']}")
    assert all(q[key] == repair_run[key] for key in ("covered_lines", "total_lines", "coverage_pct"))
    assert 0 < q["covered_lines"] <= q["total_lines"] and 0 < q["coverage_pct"] <= 100
    assert snapshot["source"]["id"] == after["id"] and snapshot["bugs"] == [bug]
    assert get(page, path + "/export") == snapshot
    expect(page.locator("#quality-case-legend")).to_contain_text("5 / 5")
    expect(page.locator('[data-metric="coverage"] .quality-metric-note')).to_contain_text(
        f"{q['covered_lines']} / {q['total_lines']} 行")
    expect(page.locator(f'[data-regression-id="{regression["run_id"]}"]')).to_contain_text("判定 已解决")
    responsive(page, "reports", "#report-quality")
    page.reload()
    expect(page.locator("#quality-run-number")).to_have_text("运行 #" + str(regression["run_id"]))
    json_path = download(page, "下载 JSON 报告", tmp_path, f"testpilot-run-{regression['run_id']}.json", role="link")
    assert json.loads(json_path.read_text("utf-8")) == snapshot
    page.get_by_role("button", name="HTML 报告", exact=True).click()
    html_path = download(page, "下载 HTML 报告", tmp_path, f"testpilot-run-{regression['run_id']}.html")
    offline = page.context.browser.new_page(viewport={"width": 1440, "height": 900})
    try:
        offline.goto(html_path.as_uri())
        expect(offline.locator("#quality-run-number")).to_have_text(f"运行 #{regression['run_id']}")
        for selector in ("#report-origin", "#report-quality", "#quality-case-legend", "#quality-identities", "#report-hashes", "#report-bugs"):
            assert offline.locator(selector).text_content() == page.locator(selector).text_content(), selector
        assert not offline.locator("script,link[rel=stylesheet]").count()
        save(offline, "report-standalone")
    finally:
        offline.close()
    identity = {"project_id": project, "file_id": [before["id"], after["id"]],
                "version_id": [before["id"], after["id"]], "revision": [before["revision"], after["revision"]],
                "symbol": SYMBOL, "source_lines": [v1_line, v2_line], "suite_id": suite["id"],
                "run_id": {"initial": first_run["id"], "failure": failure["id"], "regression": regression["run_id"]},
                "bug_id": bug_id, "nodeid": NODEID, "report_snapshot": hashlib.sha256(
                    json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
                ).hexdigest()}
    if target := os.getenv("TESTPILOT_WP09_CAPTURE"):
        native = Path(target) / "raw"
        native.mkdir(parents=True, exist_ok=True)
        (native / "report-snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (native / "workflow-identities.json").write_text(json.dumps(identity, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (native / "report-download.html").write_bytes(html_path.read_bytes())
    record("WP09_WORKFLOW", identity)
    page.get_by_role("button", name="返回工作台").click()
    page.locator(f'#report-bugs [data-bug-id="{bug_id}"] a').first.click()
    expect(page.locator("#bug-state")).to_have_text("已解决")
    expect_route(page, project=project, file=after["id"], bug=bug_id)
    page.go_back()
    expect(page.locator("#quality-run-number")).to_have_text("运行 #" + str(regression["run_id"]))
    page.locator("#report-run").click()
    expect(page.locator("#exec-run-id")).to_have_text("#" + str(regression["run_id"]))
    page.go_back()
    expect(page.locator("#quality-run-number")).to_have_text("运行 #" + str(regression["run_id"]))
    page.locator("#project").select_option(str(other))
    expect(page.locator("#quality-empty")).to_contain_text("项目尚无运行记录")
    expect(page.locator("#report")).to_be_hidden()
    assert query(page) == {"project": str(other)}
    assert writes == ["/api/projects", f"/api/projects/{project}/files", f"/api/projects/{project}/files",
                      f"/api/files/{before['id']}/suites", f"/api/suites/{suite['id']}/runs",
                      f"/api/runs/{failure['id']}/bugs", f"/api/bugs/{bug_id}/regressions"]
    assert not console and not faults, (console, faults)
    record("WP09_NETWORK", {"api_writes": writes, "http_errors": len(faults), "console_errors": len(console)})


def test_graph_lifecycle(studio):
    page = studio
    page.add_init_script("""(() => {
      const request = window.requestAnimationFrame.bind(window);
      const cancel = window.cancelAnimationFrame.bind(window);
      const listen = EventTarget.prototype.addEventListener;
      const frames = new Set(), listeners = new Set();
      let rendered = 0;
      window.requestAnimationFrame = callback => {
        const id = request(time => { frames.delete(id); rendered++; callback(time); });
        frames.add(id);
        return id;
      };
      window.cancelAnimationFrame = id => { frames.delete(id); cancel(id); };
      EventTarget.prototype.addEventListener = function(type, listener, options) {
        if (options?.signal && (/^(visibilitychange|keydown|pagehide|wheel)$/.test(type))) listeners.add(options.signal);
        return listen.call(this, type, listener, options);
      };
      window.graphProbe = () => ({pending:frames.size, rendered, signals:listeners.size,
        live:[...listeners].filter(signal => !signal.aborted).length});
    })()""")
    project = post_json(page, "/api/projects", {"name": "画布生命周期探针"})["id"]
    row = upload(page, project, "telemetry.py", SAMPLE)
    page.goto(f"/workbench/analysis?project={project}&file={row['id']}")
    expect(page.locator("#ast-stage")).to_have_text("COMPLETE", timeout=25_000)
    page.locator("#ast-replay").click()
    assert page.evaluate("graphProbe().pending") > 0

    def transition(event, persisted):
        return page.evaluate("""([type, persisted]) => {
          dispatchEvent(new PageTransitionEvent(type, {persisted})); return graphProbe();
        }""", [event, persisted])

    hidden = transition("pagehide", True)
    assert hidden["pending"] == 0 and hidden["live"] >= 2
    assert page.evaluate("async () => { await new Promise(resolve => setTimeout(resolve, 150)); return graphProbe(); }") == hidden
    restored = transition("pageshow", True)
    assert restored["pending"] > 0
    page.wait_for_function("previous => graphProbe().rendered > previous", arg=hidden["rendered"])
    pause = page.locator("#ast-pause")
    pause.click()
    paused_label = pause.get_attribute("aria-label")
    transition("pagehide", True)
    transition("pageshow", True)
    expect(pause).to_have_attribute("aria-label", paused_label)
    pause.click()
    assert pause.get_attribute("aria-label") != paused_label
    cleared = transition("pagehide", False)
    assert cleared["pending"] == cleared["live"] == 0 and cleared["signals"] == hidden["signals"]
    page.locator("body").evaluate("el => el.focus()")
    page.keyboard.press("/")
    assert page.evaluate("document.activeElement.id") != "ast-search"
    record("WP09_LIFECYCLE", {"hidden": hidden, "restored": restored, "disposed": cleared,
                             "probe": "Edge synthetic PageTransitionEvent with real canvas"})


def test_real_long_log_mobile(studio):
    page = studio
    project = post_json(page, "/api/projects", {"name": "长日志探针"})["id"]
    before = upload(page, project, "telemetry.py", FIXED)
    token = "bounded-line-"
    failing = upload(page, project, "telemetry.py", f'print("{token}" * 12000)\n' + SAMPLE)
    page.goto(f"/workbench/generation?project={project}&file={before['id']}&symbol={SYMBOL}")
    page.get_by_role("button", name="生成并验证").click()
    expect(page.locator("#initial-status")).to_contain_text("通过", timeout=120_000)
    suite = int(query(page)["suite"])
    run = post_json(page, f"/api/suites/{suite}/runs", {"file_id": failing["id"]})
    saved = get(page, f"/api/runs/{run['id']}")
    assert token * 12000 in saved["log"] and saved["status"] == "failed"
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(f"/workbench/runs?project={project}&file={failing['id']}&suite={suite}&run={run['id']}")
    expect(page.locator("#exec-run-state")).to_have_text("用例失败")
    log = page.locator("#run-log")
    expect(log).to_be_visible()
    assert log.text_content() == saved["log"]
    measured = page.locator("#log-search").evaluate("""async (input, query) => {
      const start = performance.now(); input.value = query; input.dispatchEvent(new InputEvent('input'));
      await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
      const log = document.querySelector('#run-log');
      return {elapsedMs:performance.now()-start, clientWidth:log.clientWidth, scrollWidth:log.scrollWidth,
        pageWidth:document.documentElement.scrollWidth, marks:log.querySelectorAll('mark').length};
    }""", token)
    assert measured["pageWidth"] == 390 and 0 < measured["clientWidth"] == measured["scrollWidth"]
    assert 0 < measured["marks"] <= 300 and measured["elapsedMs"] < 3000, measured
    assert log.text_content() == saved["log"]
    page.context.grant_permissions(["clipboard-read", "clipboard-write"])
    page.locator("#copy-log").click()
    expect(page.locator("#notice")).to_contain_text("已复制原始执行日志")
    assert page.evaluate("navigator.clipboard.readText()").replace("\r\n", "\n") == saved["log"].replace("\r\n", "\n")
    record("WP09_LONG_LOG", {**measured, "bytes": len(saved["log"].encode()), "run": run["id"]})
