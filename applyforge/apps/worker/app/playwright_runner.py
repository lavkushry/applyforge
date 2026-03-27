from pathlib import Path
from uuid import uuid4

from playwright.sync_api import sync_playwright

from app.config import settings


def run_assisted_flow(application_url: str, answers: dict) -> dict:
    Path(settings.artifacts_path).mkdir(parents=True, exist_ok=True)
    screenshot = str(Path(settings.artifacts_path) / f'{uuid4()}.png')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(application_url, wait_until='domcontentloaded')
        if answers.get('full_name'):
            for selector in ["input[name='name']", "input[autocomplete='name']"]:
                if page.locator(selector).count() > 0:
                    page.fill(selector, answers['full_name'])
                    break
        page.screenshot(path=screenshot, full_page=True)
        browser.close()

    return {
        'status': 'paused_for_review',
        'steps': [
            {'name': 'open_url', 'status': 'completed'},
            {'name': 'fill_basic_fields', 'status': 'completed'},
            {'name': 'pause_before_submit', 'status': 'paused'},
        ],
        'screenshot': screenshot,
    }
