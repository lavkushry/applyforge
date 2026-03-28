import os
import sys
import types


os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

playwright_module = types.ModuleType("playwright")
sync_api_module = types.ModuleType("playwright.sync_api")
sync_api_module.sync_playwright = lambda: None
playwright_module.sync_api = sync_api_module
sys.modules.setdefault("playwright", playwright_module)
sys.modules["playwright.sync_api"] = sync_api_module

from app.playwright_runner import classify_required_fields, detect_manual_challenge_signals


def test_detect_manual_challenge_signals_includes_text_and_dom_evidence() -> None:
    evidence = detect_manual_challenge_signals(
        "Before continuing, complete the CAPTCHA security check.",
        {
            "iframe[src*='captcha']": 1,
            "[data-sitekey]": 0,
        },
    )

    assert len(evidence) == 2
    assert evidence[0]["kind"] == "text"
    assert "captcha" in evidence[0]["tokens"]
    assert evidence[1]["kind"] == "dom"
    assert evidence[1]["matches"][0]["selector"] == "iframe[src*='captcha']"


def test_detect_manual_challenge_signals_returns_empty_for_clean_page() -> None:
    evidence = detect_manual_challenge_signals(
        "Thanks for applying. Continue to the next step.",
        {
            "iframe[src*='captcha']": 0,
            "[data-sitekey]": 0,
        },
    )

    assert evidence == []


def test_classify_required_fields_flags_screening_questions_for_manual_review() -> None:
    step_name, reason = classify_required_fields(
        [
            {
                "tag_name": "textarea",
                "type": "",
                "name": "why_work_here",
                "label_text": "Why do you want to work here?",
            }
        ]
    )

    assert step_name == "manual_question_review_required"
    assert "Manual review required" in reason


def test_classify_required_fields_keeps_simple_missing_inputs_as_supported_gap() -> None:
    step_name, reason = classify_required_fields(
        [
            {
                "tag_name": "input",
                "type": "text",
                "name": "full_name",
                "label_text": "Full name",
            }
        ]
    )

    assert step_name == "unsupported_fields_detected"
    assert reason == "Unsupported required fields detected"
