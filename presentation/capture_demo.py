"""Capture a course walkthrough using real Edge, the local API and WASI fixtures."""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from test_dashboard import app_url  # noqa: E402,F401


def test_capture_course_demo(app_url):
    output = ROOT / "presentation/screenshots"
    output.mkdir(exist_ok=True)
    evidence = ROOT / "reports/course-final"
    evidence.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=os.getenv("TESTPILOT_BROWSER_CHANNEL", "msedge"))
        page = browser.new_page(base_url=app_url, viewport={"width": 1440, "height": 900})
        page.set_default_timeout(25_000)
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))

        def request(path, data=None):
            result = (page.request.get(path, timeout=180_000) if data is None else
                      page.request.post(path, data=data, timeout=180_000))
            assert result.ok, result.text()
            return result.json()

        def shot(name, path=None, marker=None, content=None):
            if path:
                page.goto(path)
            if marker:
                target = page.locator(marker)
                expect(target).to_be_visible()
                if content:
                    expect(target).to_contain_text(content)
            page.screenshot(path=output / f"{name}.png", animations="disabled")
            print(f"{name}: {page.url}")

        shot("00-dashboard", "/", "#database-status", "已连接")
        demo = request("/api/projects", {"name": "课程演示 · 版本与回归"})
        project_id = demo["id"]
        files = []
        for variant in ("buggy", "fixed"):
            source = (ROOT / "eval/phase02" / variant / "magnitude.py").read_text(encoding="utf-8")
            files.append(request(f"/api/projects/{project_id}/files",
                                 {"filename": "magnitude.py", "source": source})["id"])
        first, fixed = files
        context = f"project={project_id}&file={first}"
        shot("01-project", f"/workbench/projects?{context}", "#source", "def magnitude")
        shot("02-ast", f"/workbench/analysis?{context}", "#symbols", "magnitude")
        page.goto(f"/workbench/generation?{context}&target=magnitude")
        expect(page.get_by_label("目标函数")).to_have_value("magnitude")
        with page.expect_response(lambda res: res.request.method == "POST" and
                                  f"/api/files/{first}/suites" in res.url, timeout=120_000) as generation:
            page.get_by_role("button", name="生成并验证").click()
        suite = generation.value.json()
        expect(page.locator("#initial-status")).to_contain_text("首次 Pytest 运行")
        shot("03-suite", marker="#test-source", content="test_example_3")
        failure = suite["initial_run"]
        assert failure["status"] == "failed"
        run_id = failure["id"]
        shot("04-execution", f"/workbench/runs?{context}&suite={suite['id']}&run={run_id}",
             "#run-identity", f"运行 #{run_id}")
        page.goto(f"/workbench/bugs?project={project_id}&file={fixed}&run={run_id}")
        page.get_by_label("缺陷标题").fill("负输入违反绝对值契约")
        page.get_by_role("button", name="登记缺陷").click()
        expect(page.locator("#bug-state")).to_have_text("待修复")
        page.get_by_role("button", name="运行回归").click()
        with page.expect_response(lambda res: res.request.method == "POST" and
                                  "/regressions" in res.url, timeout=120_000) as regression:
            page.get_by_role("button", name="确认运行").click()
        assert regression.value.ok
        expect(page.locator("#notice")).to_contain_text("已保存回归运行", timeout=120_000)
        shot("05-regression", marker="#regressions", content="已解决")
        restored = [row for row in request(f"/api/projects/{project_id}/runs")
                    if row["file_id"] == fixed and row["status"] == "passed"]
        assert restored
        restored_id = restored[0]["id"]
        shot("06-quality", f"/workbench/reports?project={project_id}&file={fixed}&run={restored_id}",
             "#report-origin", "magnitude.py")
        payload = request(f"/api/runs/{restored_id}/report")
        with page.expect_download() as downloaded:
            page.get_by_role("link", name="下载 JSON 报告").click()
        assert json.loads(downloaded.value.path().read_bytes()) == payload
        (evidence / "demo-quality.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), "utf-8")

        subject = "def unit(x: int) -> int:\n    '''>>> unit(3)\n    3\n    '''\n    return x\n"
        unit = request(f"/api/projects/{project_id}/files", {"filename": "unit.py", "source": subject})
        task = request(f"/api/engine/files/{unit['id']}/tasks", {"target": "unit", "generation_mode": "template"})
        page.goto(f"/engine?task_id={task['id']}")
        page.get_by_role("link", name="评估变异测试与补测").click()
        page.get_by_role("checkbox").uncheck()
        page.get_by_role("button", name="创建并运行").click()
        expect(page.locator("#status")).to_contain_text("已完成", timeout=120_000)
        shot("07-mutation", marker="#before", content="1/1")
        with page.expect_download() as mutation:
            page.get_by_role("link", name="下载完整实验 JSON").click()
        result = json.loads(mutation.value.path().read_bytes())
        assert result["before"]["killed"] == result["before"]["total"] == 1
        (evidence / "demo-mutation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), "utf-8")
        assert errors == []
        browser.close()


def test_capture_model_evidence():
    source = ROOT / "reports/course-final/model-health.json"
    entry = json.loads(source.read_text("utf-8"))["model"]
    data = entry["payload"]
    assert entry["http"] == 200 and data["state"] == "ready" and data["vulkan"]
    stamp = datetime.fromtimestamp(data["at"], timezone(timedelta(hours=8))).isoformat(timespec="seconds")
    evidence = {
        "model": data["model"], "state": data["state"], "vulkan": data["vulkan"],
        "backend_version": data["backend_version"], "context": data["context"],
        "size_vram_gib": round(data["size_vram"] / (1024 ** 3), 2),
        "weight_sha256": data["weight_sha256"], "run_id": data["run_id"],
    }
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=os.getenv("TESTPILOT_BROWSER_CHANNEL", "msedge"))
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.set_content("""<meta charset="utf-8"><style>
        body {background:#102b3d;color:#e9f5f7;font:24px 'Microsoft YaHei',sans-serif;margin:85px;}
        h1 {font-size:54px;margin-bottom:18px} p {color:#8ee2cb;} pre {font:24px/1.62 Consolas,monospace;
        color:#f2f7f9;padding:35px;background:#15384d;border-left:5px solid #69d3bd;}
        </style><h1>Qwen3.8-27B 本机推理记录</h1><p></p><pre></pre>""")
        page.locator("p").evaluate("(node, value) => node.textContent = value",
                                  f"PHASE-06 · {stamp} · {entry['path']} · HTTP {entry['http']}")
        page.locator("pre").evaluate("(node, value) => node.textContent = value",
                                    json.dumps(evidence, ensure_ascii=False, indent=2))
        page.screenshot(path=ROOT / "presentation/screenshots/08-model.png")
        browser.close()
