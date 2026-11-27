"""WP04-F01-001. Preserve the uploaded text across preview pages and immutable revisions."""

import hashlib

from playwright.sync_api import expect

from test_ast_studio import post_json, studio
from test_dashboard import app_url


def test_paged_source_and_case_group(studio):
    page = studio
    project = post_json(page, "/api/projects", {"name": "Source preview"})
    path = f"/api/projects/{project['id']}/files"
    page.goto(f"/workbench/projects?project={project['id']}")
    source = "".join(f"# 遥测行 {n}\r\n" for n in range(1, 102)) + "end_value = '完成'"
    original = source.encode("utf-8")

    def submit(name, raw):
        page.get_by_label("本地文件").set_input_files({"name": name, "mimeType": "text/plain", "buffer": raw})
        with page.expect_response(lambda r: r.url.endswith(path) and r.request.method == "POST") as response:
            page.get_by_role("button", name="导入文件", exact=True).click()
        assert response.value.status == 200
        expected = hashlib.sha256(raw.decode("utf-8-sig").encode("utf-8")).hexdigest()
        expect(page.locator("#digest-value")).to_have_text(expected)
        record_id = page.locator("#file").input_value()
        return page.request.get(f"/api/files/{record_id}").json()

    first = submit("Probe.py", b"\xef\xbb\xbf" + original)
    assert first["source"] == source and first["sha256"] == hashlib.sha256(original).hexdigest()
    expect(page.locator("#file-byte-size")).to_have_text(f"{len(original)} B")
    lines = source.splitlines(keepends=True)
    assert page.locator("#source").text_content() == "".join(lines[:100])
    page.get_by_role("button", name="下一页").click()
    assert page.locator("#source").text_content() == "".join(lines[100:])
    expect(page.locator("#source .ai-token-string")).to_have_text("'完成'")
    page.context.grant_permissions(["clipboard-read", "clipboard-write"])
    page.locator("#copy-source").click()
    expect(page.locator("#notice")).to_contain_text("已复制")
    # Normalise the operating system clipboard's line endings for the read-back.
    copied = page.evaluate("navigator.clipboard.readText()")
    assert copied.replace("\r\n", "\n") == source.replace("\r\n", "\n")
    page.get_by_role("button", name="上一页").click()
    assert page.locator("#source").text_content() == "".join(lines[:100])

    second = submit("probe.py", original + b"\r\nphase = 2")
    third = submit("PROBE.py", original)
    assert [r["revision"] for r in (first, second, third)] == [1, 2, 3]
    assert first["sha256"] == third["sha256"] and first["id"] != third["id"]
    expect(page.locator("[data-file-latest]")).to_have_count(1)
    expect(page.locator("[data-file-id]")).to_have_count(3)
