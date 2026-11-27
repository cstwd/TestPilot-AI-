"""WP04-F01-001. Keep available navigation usable during partial startup failure."""

from playwright.sync_api import expect

from test_ast_studio import post_json, studio, upload
from test_dashboard import app_url


def test_mobile_recovery_from_startup_errors(studio):
    page = studio
    page.set_viewport_size({"width": 390, "height": 844})
    first = post_json(page, "/api/projects", {"name": "Readable project"})
    revision = upload(page, first["id"], "sample.py", "def sample(): return 1\n")
    second = post_json(page, "/api/projects", {"name": "Temporarily unavailable"})
    panels = page.locator("#project-panels")
    retry = page.locator("#project-retry")

    def unavailable(route):
        route.fulfill(status=503, json={"detail": "Service temporarily unavailable"})

    page.route("**/api/projects", unavailable, times=1)
    page.goto("/workbench/projects")
    expect(retry).to_be_visible()
    panels.locator("[data-panel=files]").click()
    expect(page.locator("#files-empty")).to_be_visible()
    panels.locator("[data-panel=details]").click()
    expect(page.locator("#inspect-empty")).to_be_visible()
    expect(page.locator("#analyze-version")).not_to_be_visible()
    retry.click()
    expect(page.locator("#connection-state")).to_have_text("已连接")
    expect(page.locator("#project")).to_have_value(str(second["id"]))

    page.route(f"**/api/projects/{second['id']}/files", unavailable, times=1)
    page.reload()
    expect(retry).to_be_visible()
    expect(page.locator(".project-row")).to_have_count(2)
    panels.locator("[data-panel=details]").click()
    expect(page.locator("#inspect-empty")).to_be_visible()
    expect(page.locator("#analyze-version")).not_to_be_visible()
    page.locator("#project").select_option(str(first["id"]))
    expect(page.locator("#connection-state")).to_have_text("已连接")
    panels.locator("[data-panel=details]").click()
    expect(page.locator("#source")).to_have_text(revision["source"])
    expect(page.locator("#analyze-version")).to_have_attribute(
        "href", f"/workbench/analysis?project={first['id']}&file={revision['id']}")
