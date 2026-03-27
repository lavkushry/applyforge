from pathlib import Path
from uuid import uuid4

from playwright.sync_api import sync_playwright

from app.config import settings


def run_assisted_flow(application_url: str, answers: dict) -> dict:
    Path(settings.artifacts_path).mkdir(parents=True, exist_ok=True)
    step_artifacts = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=settings.playwright_headless)
        page = browser.new_page()
        page.set_default_timeout(settings.page_timeout_ms)
        page.goto(application_url, wait_until="domcontentloaded")

        open_url_shot = str(Path(settings.artifacts_path) / f"{uuid4()}-open.png")
        page.screenshot(path=open_url_shot, full_page=True)
        step_artifacts.append({"name": "open_url", "status": "completed", "screenshot": open_url_shot})

        if answers.get("full_name"):
            for selector in [
                "input[name='name']",
                "input[autocomplete='name']",
                "input[name='fullName']",
            ]:
                if page.locator(selector).count() > 0:
                    page.fill(selector, answers["full_name"])
                    break

        if answers.get("email"):
            for selector in ["input[type='email']", "input[name='email']", "input[autocomplete='email']"]:
                if page.locator(selector).count() > 0:
                    page.fill(selector, answers["email"])
                    break

        fill_shot = str(Path(settings.artifacts_path) / f"{uuid4()}-filled.png")
        page.screenshot(path=fill_shot, full_page=True)
        step_artifacts.append({"name": "fill_basic_fields", "status": "completed", "screenshot": fill_shot})

        browser.close()

    return {
        "status": "paused_for_review",
        "steps": [
            *step_artifacts,
            {
                "name": "pause_before_submit",
                "status": "paused",
                "screenshot": fill_shot,
                "output": {"requires_user_review": True},
            },
        ],
        "final_screenshot": fill_shot,
    }
