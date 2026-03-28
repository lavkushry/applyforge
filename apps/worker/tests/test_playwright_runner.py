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

from app.field_adapters import resolve_field_action
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


def test_resolve_field_action_maps_select_to_matching_option() -> None:
    action = resolve_field_action(
        {
            "tag_name": "select",
            "type": "",
            "name": "authorized",
            "label_text": "Are you legally authorized to work in the United States?",
            "options": [
                {"value": "", "text": "Choose"},
                {"value": "yes", "text": "Yes"},
                {"value": "no", "text": "No"},
            ],
        },
        {"authorized_to_work": "yes"},
    )

    assert action is not None
    assert action["answer_key"] == "authorized_to_work"
    assert action["type"] == "select"
    assert action["option"]["value"] == "yes"


def test_resolve_field_action_maps_radio_and_checkbox_questions() -> None:
    radio_action = resolve_field_action(
        {
            "tag_name": "input",
            "type": "radio",
            "name": "relocation",
            "group_label": "Are you willing to relocate?",
            "option_text": "Yes",
        },
        {"willing_to_relocate": "yes"},
    )
    checkbox_action = resolve_field_action(
        {
            "tag_name": "input",
            "type": "checkbox",
            "name": "relocation_confirmed",
            "label_text": "I am willing to relocate",
        },
        {"willing_to_relocate": "yes"},
    )

    assert radio_action is not None
    assert radio_action["type"] == "radio"
    assert checkbox_action is not None
    assert checkbox_action["type"] == "checkbox"
    assert checkbox_action["value"] is True


def test_resolve_field_action_normalizes_date_answers() -> None:
    action = resolve_field_action(
        {
            "tag_name": "input",
            "type": "date",
            "name": "available_start",
            "label_text": "Available start date",
        },
        {"available_start_date": "04/15/2026"},
    )

    assert action is not None
    assert action["type"] == "fill"
    assert action["value"] == "2026-04-15"
