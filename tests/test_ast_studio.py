"""WP03-AST-VISUAL-001. End-to-end checks against main.py and an isolated database."""

import hashlib
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
from playwright.sync_api import expect, sync_playwright

from test_dashboard import app_url


# Demonstration input imported through F01. It is never executed.
TELEMETRY = (Path(__file__).resolve().parents[1] / "eval" / "ast_visual" / "telemetry.py").read_text(encoding="utf-8")
VIEWS = [(1920, 1080), (1440, 900), (1280, 800), (1024, 768), (768, 1024), (390, 844)]


def capture(page, name):
    folder = os.environ.get("TESTPILOT_AST_CAPTURE_DIR")
    if folder:
        target = Path(folder)
        target.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=target / (name + ".png"), animations="disabled")


def record(name, data):
    print(name + " " + json.dumps(data, ensure_ascii=True))


@pytest.fixture
def studio(app_url):
    channel = os.environ.get("TESTPILOT_BROWSER_CHANNEL", "msedge" if sys.platform == "win32" else "chromium")
    with sync_playwright() as driver:
        browser = driver.chromium.launch(channel=channel)
        errors = []
        try:
            page = browser.new_page(base_url=app_url, viewport={"width": 1440, "height": 900})
            page.on("pageerror", lambda e: errors.append(str(e)))
            yield page
            assert not errors, errors
        finally:
            browser.close()


def post_json(page, url, payload):
    response = page.request.post(url, data=payload)
    assert response.ok, response.text()
    return response.json()


def upload(page, project, filename, source):
    return post_json(page, f"/api/projects/{project}/files", {"filename": filename, "source": source})


def wait_complete(page):
    expect(page.locator("#ast-stage")).to_contain_text("COMPLETE", timeout=20_000)


def open_file(page, row, complete=True):
    page.goto(f"/workbench/analysis?project={row['project_id']}&file={row['id']}")
    if complete:
        wait_complete(page)


def graph_model(page, file_id):
    return page.evaluate("""async file => {
        const {buildGraph} = await import('/static/ast-model.js');
        const [result, source] = await Promise.all([
            fetch('/api/files/' + file + '/analysis').then(r => r.json()),
            fetch('/api/files/' + file).then(r => r.json())
        ]);
        return buildGraph(result, source);
    }""", file_id)


def node_button(page, node):
    return page.locator(f'#symbols button[data-node-id="{node["id"]}"]')


def show_panel(page, name):
    switch = page.locator(f'#ast-panel-nav [data-panel="{name}"]')
    if switch.is_visible():
        switch.click()


def test_file_to_generation(studio):
    """Exercise user import, clickable hierarchy, selection, inspector and six window sizes."""
    page = studio
    page.goto("/workbench/projects")
    page.get_by_label("项目名称").fill("Telemetry Lab")
    page.get_by_role("button", name="创建项目").click()
    expect(page.locator("#project option:checked")).to_have_text("Telemetry Lab")
    page.get_by_label("本地文件").set_input_files({"name": "telemetry.py", "mimeType": "text/plain", "buffer": TELEMETRY.encode()})
    page.get_by_role("button", name="导入文件").click()
    digest = hashlib.sha256(TELEMETRY.encode()).hexdigest()
    expect(page.locator("#digest")).to_contain_text(digest)
    page.get_by_role("link", name="分析此版本").click()
    wait_complete(page)
    project, file_id = page.locator("#project").input_value(), page.locator("#file").input_value()
    model = graph_model(page, file_id)
    nodes = {n["qualified_name"]: n for n in model["nodes"]}
    sample, method, nested = nodes["Sample"], nodes["Sample.normalized"], nodes["group_channels.channel_key"]
    assert method["type"] == "method" and method["parent_id"] == sample["id"]
    assert nested["type"] == "function" and nested["parent_id"] == nodes["group_channels"]["id"]
    assert len(model["edges"]) == len(model["nodes"]) - 1
    expect(page.locator("#ast-node-count")).to_contain_text(str(len(model["nodes"])))
    expect(page.locator("#ast-edge-count")).to_contain_text(str(len(model["edges"])))
    for name in ("settings", "help"):
        page.locator("#ast-" + name).click()
        expect(page.locator("#ast-dialog")).to_be_visible()
        page.keyboard.press("Escape")
        expect(page.locator("#ast-dialog")).not_to_be_visible()
    inspector = page.locator("#inspector-body")
    node_button(page, sample).click()
    canvas = page.locator("#ast-canvas")
    page.wait_for_timeout(280)  # camera transition, node now under canvas centre
    canvas.click(position={"x": 8, "y": 40})
    expect(canvas).to_have_attribute("data-selected", "")
    box = canvas.bounding_box()
    center = {"x": box["width"]/2, "y": box["height"]/2}
    canvas.click(position=center)
    expect(canvas).to_have_attribute("data-selected", sample["id"])
    canvas.dblclick(position=center)
    expect(inspector).to_contain_text("Sample")
    page.locator("#ast-fit").click()
    capture(page, "class-overview")
    inspector.get_by_role("tab", name="Structure").click()
    capture(page, "class-structure")
    inspector.get_by_role("button", name=re.compile("normalized")).click()
    expect(page.locator("#ast-canvas")).to_have_attribute("data-selected", method["id"])
    inspector.get_by_role("tab", name="Overview").click()
    expect(inspector).to_contain_text("scale")
    inspector.get_by_role("tab", name="Source").click()
    line = inspector.locator(f'[data-line="{method["start_line"]}"]')
    expect(line).to_contain_text("def normalized")
    gutters = inspector.locator(".ai-line-no").evaluate_all(
        "rows => rows.map(row=>Math.round(row.getBoundingClientRect().left))")
    assert len(set(gutters)) == 1, "Source line numbers must share one gutter"
    page.context.grant_permissions(["clipboard-read", "clipboard-write"])
    inspector.get_by_role("button", name="复制代码").click()
    expect(inspector.get_by_role("button", name="已复制")).to_be_visible()
    assert "return self.value / scale" in page.evaluate("navigator.clipboard.readText()")
    capture(page, "source-inspector")
    # Reverse lookup crosses to the enclosing class when clicking its definition.
    inspector.locator(f'[data-line="{sample["start_line"]}"]').click()
    expect(page.locator("#ast-canvas")).to_have_attribute("data-selected", sample["id"])
    inspector.get_by_role("tab", name="Overview").click()

    checkbox = page.locator('#ast-types input[value="method"]')
    checkbox.uncheck()
    checkbox.check()
    node_button(page, method).click()
    page.locator("#ast-search").fill("mean_value")
    match = page.locator("#ast-matches button[data-node-id]").first
    expect(match).to_contain_text("mean_value")
    match.focus()
    match.press("Enter")
    expect(page.locator("#ast-canvas")).to_have_attribute("data-selected", nodes["mean_value"]["id"])
    requests = []
    page.on("request", lambda r: requests.append(r.url) if r.url.endswith("/analysis") else None)
    page.reload()
    wait_complete(page)
    expect(page.locator("#ast-timing")).to_contain_text("本机分析快照")
    assert requests == []
    expect(page.locator("#ast-canvas")).to_have_attribute("data-selected", nodes["mean_value"]["id"])
    page.locator("#ast-replay").click()
    page.locator("#ast-pause").click()
    frozen = page.locator("#ast-stage").inner_text()
    page.wait_for_timeout(450)
    assert page.locator("#ast-stage").inner_text() == frozen
    page.locator("#ast-pause").click()
    wait_complete(page)

    original_zoom = page.locator("#ast-zoom").inner_text()
    page.locator("#ast-plus").click()
    expect(page.locator("#ast-zoom")).not_to_have_text(original_zoom)
    page.locator("#ast-minus").click()
    page.locator("#ast-reset").click()
    page.locator("#ast-fit").click()
    sizes = []
    for width, height in VIEWS:
        page.set_viewport_size({"width": width, "height": height})
        show_panel(page, "graph")
        expect(page.locator("#ast-canvas")).to_be_visible()
        page.locator("#ast-fit").click()
        page.wait_for_timeout(350)
        size = page.locator("#ast-canvas").evaluate("""el => ({
            width: Math.round(el.getBoundingClientRect().width),
            height: Math.round(el.getBoundingClientRect().height),
            pageWidth: document.documentElement.scrollWidth
        })""")
        assert size["width"] >= 200 and size["height"] >= 180 and size["pageWidth"] <= width, (width, size)
        sizes.append([width, height, size])
        capture(page, f"graph-{width}x{height}")
        if width <= 768:
            for name in ("explorer", "inspector"):
                show_panel(page, name)
                assert page.locator("#ast-canvas").evaluate("el => el.getBoundingClientRect().width > 0")
    record("VIEWPORTS", sizes)

    show_panel(page, "explorer")
    node_button(page, nodes["mean_value"]).click()
    show_panel(page, "graph")
    page.locator("#ast-generation").click()
    expect(page.get_by_label("目标函数")).to_have_value("mean_value")
    query = parse_qs(urlsplit(page.url).query)
    assert query == {"project": [project], "file": [file_id], "symbol": ["mean_value"]}
    record("WORKFLOW", {"project": project, "file": file_id, "revision": 1, "sha256": digest,
                        "symbols": len(nodes) - 1, "contains": len(model["edges"]),
                        "target": "mean_value", "engine": page.context.browser.version})


def test_revision_and_boundary_inputs(studio):
    page = studio
    project = post_json(page, "/api/projects", {"name": "Revision checks"})["id"]
    first = upload(page, project, "signal.py", "def sample(): return 1")
    duplicate = """class Sensor:
    def read(self): pass
class Sensor:
    async def read(self):
        def nested(): pass
        return nested
"""
    second = upload(page, project, "signal.py", duplicate)
    empty = upload(page, project, "empty.py", "")
    invalid = upload(page, project, "broken.py", "def missing(:\n")
    open_file(page, first)
    node_button(page, graph_model(page, first["id"])["nodes"][1]).click()
    page.locator("#file").select_option(str(second["id"]))
    wait_complete(page)
    data = graph_model(page, second["id"])
    classes = [n for n in data["nodes"] if n["type"] == "class"]
    methods = [n for n in data["nodes"] if n["type"] == "method"]
    assert [n["parent_id"] for n in methods] == [n["id"] for n in classes]
    assert all(n["file_id"] == second["id"] for n in data["nodes"])
    assert 'symbol:' + str(first["id"]) + ':' not in (page.locator("#ast-canvas").get_attribute("data-selected") or '')
    assert len({n["id"] for n in data["nodes"]}) == len(data["nodes"])
    page.locator("#file").select_option(str(empty["id"]))
    wait_complete(page)
    expect(page.locator("#ast-edge-count")).to_contain_text("0")
    assert len(graph_model(page, empty["id"])["nodes"]) == 1
    page.locator("#file").select_option(str(invalid["id"]))
    expect(page.locator("#symbols")).to_contain_text("语法错误 · 行 1")
    page.locator("#file").select_option(str(first["id"]))
    wait_complete(page)
    expect(page.locator("#symbols")).to_contain_text("sample")
    with page.expect_response(lambda r: r.url.endswith(f"/files/{first['id']}/analysis")) as read:
        page.locator("#ast-refresh").click()
    assert read.value.ok and read.value.json()["sha256"] == first["sha256"]
    wait_complete(page)
    record("BOUNDARIES", {"revision_ids": [first["id"], second["id"]], "revisions": [first["revision"], second["revision"]],
                          "duplicate_parents": [n["parent_id"] for n in methods], "empty_nodes": 1})

def import_large_graph(page):
    project = post_json(page, "/api/projects", {"name": "Render benchmark"})["id"]
    # 27 classes with 36 methods each: file + 27 + 972 = 1000 nodes / 999 AST edges.
    code = "".join(f"class Channel{i}:\n" + "".join(
        f"    def signal{j}(self): return {j}\n" for j in range(36)) for i in range(27))
    return upload(page, project, "channels.py", code)


def test_unavailable_context_and_retry(studio):
    page = studio
    page.emulate_media(reduced_motion="reduce")
    page.goto("/workbench/analysis")
    expect(page.locator("#ast-stage")).to_have_text("IDLE")
    one = post_json(page, "/api/projects", {"name": "A"})["id"]
    two = post_json(page, "/api/projects", {"name": "B"})["id"]
    row = upload(page, two, "helpers.py", "def convert(): return 7")
    for requested_project in (one, 99999):
        page.goto(f"/workbench/analysis?project={requested_project}&file={row['id']}")
        expect(page.locator("#ast-stage")).to_have_text("UNAVAILABLE")
        expect(page.locator("#ast-generation")).to_be_hidden()
        expect(page.locator("#symbols")).not_to_contain_text("convert")

    seen = []
    def unavailable(route):
        seen.append((route.request.method, page.locator("#ast-stage").inner_text()))
        route.fulfill(status=503, content_type="application/json", body='{"detail":"QA temporary outage"}')

    page.route("**/api/files/*/analysis", unavailable, times=1)
    open_file(page, row, complete=False)
    expect(page.locator("#ast-stage")).to_have_text("ERROR")
    expect(page.locator("#notice")).to_contain_text("QA temporary outage")
    assert seen == [("GET", "SCANNING")]
    page.locator("#ast-refresh").click()
    wait_complete(page)
    expect(page.locator("#symbols")).to_contain_text("convert")
    for box in page.locator("#ast-types input").all():
        box.uncheck()
    expect(page.locator("#ast-message")).to_be_visible()
    page.locator("#ast-search").fill("convert")
    page.locator("#ast-search").press("Enter")
    expect(page.locator('#ast-types input[value="function"]')).to_be_checked()
    expect(page.locator("#ast-message")).to_be_hidden()
    expect(page.locator("#ast-selected")).to_have_text("convert")


def test_large_real_analysis(studio):
    page = studio
    row = import_large_graph(page)
    page.add_init_script("""window.drawTimes = [];
        const clear = CanvasRenderingContext2D.prototype.clearRect;
        CanvasRenderingContext2D.prototype.clearRect = function(...args) {
            if(this.canvas.id==='ast-canvas') window.drawTimes.push(performance.now());
            return clear.apply(this, args);
        };""")
    open_file(page, row)
    expect(page.locator("#ast-node-count")).to_contain_text("1000")
    expect(page.locator("#ast-edge-count")).to_contain_text("999")
    result = page.evaluate("""() => {
        const entries = performance.getEntriesByType('resource').filter(e => e.name.endsWith('/analysis'));
        const analysis = entries.at(-1);
        const intervals = drawTimes.slice(1).map((t,i)=>t-drawTimes[i]).sort((a,b)=>a-b);
        return {analysisHttpMs: analysis.duration, endOfNavigationToReadoutMs:
            performance.now()-performance.getEntriesByType('navigation')[0].responseEnd,
            frames:drawTimes.length, frameIntervalP50:intervals[Math.floor(intervals.length * .50)],
            frameIntervalP95:intervals[Math.floor(intervals.length * .95)]};
    }""")
    model = graph_model(page, row["id"])
    assert len(model["nodes"]) == 1000 and len(model["edges"]) == 999
    assert len(page.locator("#symbols button[data-node-id]").all()) > 0
    page.emulate_media(reduced_motion="reduce")
    page.locator("#ast-replay").click()
    wait_complete(page)
    record("REAL_LARGE", result)


def test_dense_renderer_and_pointer_gestures(studio):
    page = studio
    row = import_large_graph(page)
    page.emulate_media(reduced_motion="reduce")
    # Reuse the production renderer at its documented module interface on a separate
    # same-origin test surface. The extra cross-links never enter the business model.
    page.goto("/workbench/projects")
    expect(page.locator("#source-panel")).to_be_visible()
    model = graph_model(page, row["id"])
    page.evaluate("""async model => {
        const {createCanvas} = await import('/static/ast-canvas.js');
        const nodes = model.nodes, edges = model.edges.slice();
        for (let i = 0; edges.length < 2000; i++) {
            const a = i % nodes.length, b = (i + (i < nodes.length ? 57 : 91)) % nodes.length;
            edges.push({id:'bench:'+i, source:nodes[a].id, target:nodes[b].id, relation_type:'stress'});
        }
        const canvas = document.createElement('canvas');
        canvas.style.cssText = 'display:block;width:1200px;height:720px';
        document.body.replaceChildren(canvas);
        const ctx = canvas.getContext('2d'), clear = ctx.clearRect.bind(ctx);
        const benchmark = window.astBenchmark = {draws:0, click:null, double:null, stages:[]};
        ctx.clearRect = (...args) => {benchmark.draws++; clear(...args)};
        const start = performance.now();
        const renderer = createCanvas(canvas, {nodes,edges}, {
            onSelect(id){benchmark.click = id; renderer.select(id)},
            onInspect(id){benchmark.double = id},
            onStage(name){benchmark.stages.push(name)}
        });
        benchmark.constructMs = performance.now()-start;
        benchmark.renderer = renderer;
        benchmark.root = nodes[0].id;
        benchmark.nodeCount = nodes.length;
        benchmark.edgeCount = edges.length;
    }""", model)
    canvas = page.locator("canvas")
    page.wait_for_function("window.astBenchmark.draws > 0")
    point = page.evaluate("astBenchmark.renderer.positionOf(astBenchmark.root)")
    canvas.click(position=point)
    assert page.evaluate("astBenchmark.click === astBenchmark.root")
    canvas.dblclick(position=point)
    assert page.evaluate("astBenchmark.double === astBenchmark.root")
    page.evaluate("astBenchmark.renderer.fit()")
    origin = canvas.bounding_box()
    page.mouse.move(origin["x"] + 10, origin["y"] + 10)
    before = page.evaluate("astBenchmark.renderer.positionOf(astBenchmark.root)")
    page.mouse.down()
    page.mouse.move(origin["x"] + 70, origin["y"] + 50, steps=3)
    page.mouse.up()
    page.wait_for_timeout(100)
    after = page.evaluate("astBenchmark.renderer.positionOf(astBenchmark.root)")
    assert abs((after["x"] - before["x"])-60) <= 2 and abs((after["y"] - before["y"])-40) <= 2
    canvas.click(position={"x": 5, "y": 5})
    assert page.evaluate("astBenchmark.click === null")
    metrics = page.evaluate("""async () => {
        const b=astBenchmark, frame=()=>new Promise(resolve=>requestAnimationFrame(resolve));
        const times=[];
        b.renderer.reset();
        await frame();
        for(let i=0;i<40;i++){
            const t=performance.now();
            b.renderer.zoom(i%2 === 0 ? 1.05 : 1/1.05);
            await frame();
            times.push(performance.now()-t);
        }
        times.sort((a,b)=>a-b);
        const idleStart=b.draws;
        await new Promise(resolve=>setTimeout(resolve,600));
        const output={nodes:b.nodeCount, edges:b.edgeCount, constructMs:b.constructMs,
            zoomFrameMedianMs:times[19], zoomFrameP95Ms:times[37], repaintsWhileIdle:b.draws-idleStart,
            motionStages:b.stages};
        b.renderer.destroy();
        return output;
    }""")
    assert metrics["nodes"] == 1000 and metrics["edges"] == 2000 and metrics["repaintsWhileIdle"] == 0
    assert metrics["motionStages"] == ["COMPLETE"]
    record("SYNTHETIC_RENDERER", metrics)
