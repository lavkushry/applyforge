from pathlib import Path
from uuid import uuid4

from playwright.sync_api import sync_playwright

from app.config import settings
from app.db import SessionLocal
from app.field_adapters import resolve_field_action
from app.logging_utils import configure_logging
from app.models import UploadedFile
from app.persistence import RunRecorder, persist_uploaded_file

configure_logging()


FIELD_RULES = [
    {
        "answer_key": "full_name",
        "step_name": "fill_full_name",
        "selectors": ["input[name='name']", "input[autocomplete='name']", "input[name='fullName']"],
    },
    {
        "answer_key": "email",
        "step_name": "fill_email",
        "selectors": ["input[type='email']", "input[name='email']", "input[autocomplete='email']"],
    },
    {
        "answer_key": "phone",
        "step_name": "fill_phone",
        "selectors": ["input[type='tel']", "input[name='phone']", "input[autocomplete='tel']"],
    },
    {
        "answer_key": "location",
        "step_name": "fill_location",
        "selectors": ["input[name='location']", "input[autocomplete='address-level2']", "input[name='city']"],
    },
    {
        "answer_key": "linkedin_url",
        "step_name": "fill_linkedin",
        "selectors": ["input[name*='linkedin' i]", "input[id*='linkedin' i]"],
    },
    {
        "answer_key": "github_url",
        "step_name": "fill_github",
        "selectors": ["input[name*='github' i]", "input[id*='github' i]"],
    },
    {
        "answer_key": "portfolio_url",
        "step_name": "fill_portfolio",
        "selectors": ["input[name*='portfolio' i]", "input[name*='website' i]", "input[id*='portfolio' i]"],
    },
]

MANUAL_CHALLENGE_TOKENS = (
    "captcha",
    "verify you are human",
    "i'm not a robot",
    "i am not a robot",
    "security check",
    "robot check",
    "cloudflare",
    "challenge required",
)

MANUAL_CHALLENGE_SELECTORS = (
    "iframe[src*='captcha']",
    "iframe[title*='captcha' i]",
    "[id*='captcha' i]",
    "[class*='captcha' i]",
    "[name*='captcha' i]",
    "[data-sitekey]",
    "textarea[name='g-recaptcha-response']",
    "[data-testid*='captcha' i]",
)
NEXT_BUTTON_SELECTOR = (
    "button:has-text('Next'), "
    "button:has-text('Continue'), "
    "button:has-text('Review'), "
    "button:has-text('Save and continue'), "
    "input[type='button'][value*='next' i], "
    "input[type='button'][value*='continue' i], "
    "input[type='submit'][value*='next' i], "
    "input[type='submit'][value*='continue' i]"
)


def _save_screenshot(page, user_id: int | None, suffix: str) -> int:
    Path(settings.artifacts_path).mkdir(parents=True, exist_ok=True)
    screenshot_path = str(Path(settings.artifacts_path) / f"{uuid4()}-{suffix}.png")
    page.screenshot(path=screenshot_path, full_page=True)
    return persist_uploaded_file(
        user_id=user_id,
        path=screenshot_path,
        original_name=Path(screenshot_path).name,
        mime_type="image/png",
    )


def _fill_first(page, selectors: list[str], value: str) -> bool:
    for selector in selectors:
        locator = page.locator(selector)
        if locator.count() > 0:
            locator.first.fill(value)
            return True
    return False


def _upload_resume(page, resume_path: str) -> bool:
    locator = page.locator("input[type='file']")
    if locator.count() == 0:
        return False
    locator.first.set_input_files(resume_path)
    return True


def _attribute_selector(attribute: str, value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'[{attribute}="{escaped}"]'


def _field_locator(page, field: dict):
    tag_name = str(field.get("tag_name", "input") or "input").lower()
    if field.get("id"):
        return page.locator(_attribute_selector("id", str(field["id"])))
    selector = tag_name
    if field.get("type"):
        selector += _attribute_selector("type", str(field["type"]))
    if field.get("name"):
        selector += _attribute_selector("name", str(field["name"]))
    if field.get("value"):
        selector += _attribute_selector("value", str(field["value"]))
    return page.locator(selector)


def _collect_required_fields(page) -> list[dict]:
    script = """
    (elements) => elements.map((element) => {
      const tagName = element.tagName.toLowerCase();
      const type = (element.getAttribute('type') || '').toLowerCase();
      const required = element.required || element.getAttribute('aria-required') === 'true';
      const hasValue = tagName === 'select'
        ? Boolean(element.value)
        : type === 'checkbox' || type === 'radio'
          ? element.checked
          : Boolean(element.value);
      const linkedLabel = element.id ? document.querySelector(`label[for="${element.id}"]`) : null;
      const wrappedLabel = element.closest('label');
      const fieldset = element.closest('fieldset');
      const groupLabel = fieldset?.querySelector('legend')?.innerText || '';
      const labelText = (linkedLabel?.innerText || wrappedLabel?.innerText || '').trim();
      const optionText = (type === 'radio' || type === 'checkbox') ? labelText : '';
      const options = tagName === 'select'
        ? Array.from(element.options || []).map((option) => ({
            value: option.value || '',
            text: (option.innerText || option.textContent || '').trim(),
          })).filter((option) => option.value || option.text)
        : [];
      return {
        tag_name: tagName,
        type,
        name: element.getAttribute('name') || '',
        id: element.getAttribute('id') || '',
        label_text: labelText,
        group_label: (groupLabel || '').trim(),
        option_text: optionText,
        placeholder: element.getAttribute('placeholder') || '',
        aria_label: element.getAttribute('aria-label') || '',
        value: element.getAttribute('value') || '',
        required,
        has_value: hasValue,
        options,
      };
    }).filter((field) => field.required && !field.has_value);
    """
    return page.locator("input, textarea, select").evaluate_all(script)


def _apply_field_action(page, field: dict, action: dict) -> bool:
    locator = _field_locator(page, field)
    if locator.count() == 0:
        return False
    action_type = action["type"]
    if action_type == "fill":
        locator.first.fill(str(action["value"]))
        return True
    if action_type == "select":
        option = action["option"]
        if option.get("value"):
            locator.first.select_option(str(option["value"]))
        else:
            locator.first.select_option(label=str(option.get("text", "")))
        return True
    if action_type == "radio":
        locator.first.check()
        return True
    if action_type == "checkbox":
        desired = bool(action["value"])
        if desired:
            locator.first.check()
        else:
            locator.first.uncheck()
        return True
    return False


def _fill_supported_required_fields(page, answers: dict) -> tuple[list[dict], list[dict]]:
    fields = _collect_required_fields(page)
    filled: list[dict] = []
    seen_radio_groups: set[str] = set()
    seen_checkbox_groups: set[str] = set()
    for field in fields:
        field_type = str(field.get("type", "")).lower()
        field_name = str(field.get("name", ""))
        if field_type == "radio" and field_name in seen_radio_groups:
            continue
        if field_type == "checkbox" and field_name and field_name in seen_checkbox_groups:
            continue
        action = resolve_field_action(field, answers)
        if not action:
            continue
        if _apply_field_action(page, field, action):
            filled.append(
                {
                    "field": action["answer_key"],
                    "control": field_type or field.get("tag_name", "input"),
                    "name": field_name,
                    "label": field.get("label_text") or field.get("group_label") or field_name,
                }
            )
            if field_type == "radio" and field_name:
                seen_radio_groups.add(field_name)
            if field_type == "checkbox" and field_name:
                seen_checkbox_groups.add(field_name)
    return filled, _collect_required_fields(page)


def _click_next_or_continue(page) -> str | None:
    locator = page.locator(NEXT_BUTTON_SELECTOR)
    if locator.count() == 0:
        return None
    label = (
        locator.first.get_attribute("value")
        or locator.first.get_attribute("aria-label")
        or locator.first.text_content()
        or "Continue"
    )
    locator.first.click()
    page.wait_for_timeout(1200)
    return label.strip() or "Continue"


def classify_required_fields(fields: list[dict]) -> tuple[str, str]:
    if any(field.get("tag_name") in {"textarea", "select"} or field.get("type") in {"checkbox", "radio", "date", "number"} for field in fields):
        return ("manual_question_review_required", "Manual review required for unsupported screening questions")
    return ("unsupported_fields_detected", "Unsupported required fields detected")


def detect_manual_challenge_signals(body_text: str, selector_counts: dict[str, int]) -> list[dict]:
    lowered = body_text.lower()
    token_matches = [token for token in MANUAL_CHALLENGE_TOKENS if token in lowered]
    selector_matches = [{"selector": selector, "count": count} for selector, count in selector_counts.items() if count > 0]
    evidence: list[dict] = []
    if token_matches:
        evidence.append({"kind": "text", "tokens": token_matches})
    if selector_matches:
        evidence.append({"kind": "dom", "matches": selector_matches})
    return evidence


def _detect_manual_challenge(page) -> list[dict]:
    body_text = page.locator("body").inner_text(timeout=5_000).lower()
    selector_counts = {selector: page.locator(selector).count() for selector in MANUAL_CHALLENGE_SELECTORS}
    return detect_manual_challenge_signals(body_text, selector_counts)


def _resolve_resume_path(resume_file_id: int | None) -> str:
    if not resume_file_id:
        return ""
    with SessionLocal() as db:
        uploaded = db.query(UploadedFile).filter(UploadedFile.id == resume_file_id).first()
        return uploaded.path if uploaded else ""


def run_application_flow(run_id: int, packet: dict) -> dict:
    recorder = RunRecorder(run_id)
    recorder.set_status("running", "worker_started")
    answers = packet.get("answers", {})
    application_url = packet.get("job", {}).get("application_url", "")
    user_id = packet.get("user_id")
    resume_path = _resolve_resume_path(packet.get("resume_file_id"))
    result = {"status": "completed", "steps": []}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=settings.playwright_headless)
            page = browser.new_page()
            page.set_default_timeout(settings.page_timeout_ms)
            page.goto(application_url, wait_until="domcontentloaded")
            open_screenshot = _save_screenshot(page, user_id, "open")
            recorder.log_step(
                name="open_application_url",
                status="completed",
                output={"url": application_url},
                step_kind="navigation",
                screenshot_file_id=open_screenshot,
            )

            challenge_signals = _detect_manual_challenge(page)
            if challenge_signals:
                recorder.log_step(
                    name="captcha_or_antibot_detected",
                    status="paused",
                    output={
                        "reason": "Manual security challenge detected",
                        "signals": challenge_signals,
                    },
                    step_kind="anti_bot",
                    requires_approval=True,
                    screenshot_file_id=open_screenshot,
                )
                recorder.set_status("paused", "captcha_or_antibot_detected")
                browser.close()
                return {"status": "paused", "steps": [{"name": "captcha_or_antibot_detected", "status": "paused"}]}

            filled_fields = []
            for rule in FIELD_RULES:
                value = answers.get(rule["answer_key"], "")
                if value and _fill_first(page, rule["selectors"], value):
                    filled_fields.append(rule["answer_key"])
                    recorder.log_step(
                        name=rule["step_name"],
                        status="completed",
                        output={"field": rule["answer_key"]},
                        step_kind="form_fill",
                    )

            uploaded_resume = False
            if resume_path and _upload_resume(page, resume_path):
                uploaded_resume = True
                recorder.log_step(
                    name="upload_resume",
                    status="completed",
                    output={"resume_file_id": packet.get("resume_file_id")},
                    step_kind="file_upload",
                )

            fill_screenshot = _save_screenshot(page, user_id, "filled")
            recorder.log_step(
                name="fill_known_fields",
                status="completed",
                output={"filled_fields": filled_fields, "uploaded_resume": uploaded_resume},
                step_kind="form_fill",
                screenshot_file_id=fill_screenshot,
            )

            challenge_signals = _detect_manual_challenge(page)
            if challenge_signals:
                recorder.log_step(
                    name="captcha_or_antibot_detected",
                    status="paused",
                    output={
                        "reason": "Manual security challenge detected after form interaction",
                        "signals": challenge_signals,
                    },
                    step_kind="anti_bot",
                    requires_approval=True,
                    screenshot_file_id=fill_screenshot,
                )
                recorder.set_status("paused", "captcha_or_antibot_detected")
                browser.close()
                return {"status": "paused", "steps": [{"name": "captcha_or_antibot_detected", "status": "paused"}]}

            resolved_required_fields, unsupported_fields = _fill_supported_required_fields(page, answers)
            if resolved_required_fields:
                recorder.log_step(
                    name="resolve_supported_required_fields",
                    status="completed",
                    output={"resolved_fields": resolved_required_fields},
                    step_kind="form_fill",
                )

            submit_locator = page.locator("button[type='submit'], input[type='submit']")
            if unsupported_fields == [] and submit_locator.count() == 0:
                next_label = _click_next_or_continue(page)
                if next_label:
                    advance_screenshot = _save_screenshot(page, user_id, "advance")
                    recorder.log_step(
                        name="advance_application_step",
                        status="completed",
                        output={"button_label": next_label},
                        step_kind="navigation",
                        screenshot_file_id=advance_screenshot,
                    )
                    challenge_signals = _detect_manual_challenge(page)
                    if challenge_signals:
                        recorder.log_step(
                            name="captcha_or_antibot_detected",
                            status="paused",
                            output={
                                "reason": "Manual security challenge detected after advancing the application flow",
                                "signals": challenge_signals,
                            },
                            step_kind="anti_bot",
                            requires_approval=True,
                            screenshot_file_id=advance_screenshot,
                        )
                        recorder.set_status("paused", "captcha_or_antibot_detected")
                        browser.close()
                        return {"status": "paused", "steps": [{"name": "captcha_or_antibot_detected", "status": "paused"}]}
                    additional_resolved_fields, unsupported_fields = _fill_supported_required_fields(page, answers)
                    if additional_resolved_fields:
                        recorder.log_step(
                            name="resolve_follow_up_required_fields",
                            status="completed",
                            output={"resolved_fields": additional_resolved_fields},
                            step_kind="form_fill",
                            screenshot_file_id=advance_screenshot,
                        )

            if unsupported_fields:
                step_name, reason = classify_required_fields(unsupported_fields)
                recorder.log_step(
                    name=step_name,
                    status="paused",
                    output={"reason": reason, "unsupported_fields": unsupported_fields},
                    step_kind="field_detection",
                    requires_approval=True,
                    screenshot_file_id=fill_screenshot,
                )
                recorder.set_status("paused", step_name)
                browser.close()
                return {"status": "paused", "steps": [{"name": step_name, "status": "paused"}]}

            if packet.get("mode") == "assisted":
                recorder.log_step(
                    name="pause_before_submit",
                    status="paused",
                    output={"requires_user_review": True},
                    step_kind="approval_gate",
                    requires_approval=True,
                    screenshot_file_id=fill_screenshot,
                )
                recorder.set_status("paused", "pause_before_submit")
                browser.close()
                return {"status": "paused", "steps": [{"name": "pause_before_submit", "status": "paused"}]}

            submit_locator = page.locator("button[type='submit'], input[type='submit']")
            if submit_locator.count() == 0:
                recorder.log_step(
                    name="submit_confirmation_uncertain",
                    status="paused",
                    output={"reason": "No submit control detected"},
                    step_kind="submission",
                    requires_approval=True,
                    screenshot_file_id=fill_screenshot,
                )
                recorder.set_status("uncertain", "submit_confirmation_uncertain")
                browser.close()
                return {"status": "uncertain", "steps": [{"name": "submit_confirmation_uncertain", "status": "paused"}]}

            submit_locator.first.click()
            page.wait_for_timeout(1500)
            submit_screenshot = _save_screenshot(page, user_id, "submitted")
            page_text = page.locator("body").inner_text(timeout=5_000).lower()
            confirmed = any(token in page_text for token in ("thank you", "application received", "submitted", "success"))
            recorder.log_step(
                name="submit_application",
                status="completed" if confirmed else "paused",
                output={"confirmed": confirmed},
                step_kind="submission",
                requires_approval=not confirmed,
                screenshot_file_id=submit_screenshot,
            )
            browser.close()
    except Exception as exc:
        recorder.log_step(
            name="worker_execution_failed",
            status="failed",
            output={"error": str(exc)},
            step_kind="worker_error",
        )
        raise

    final_status = "completed" if confirmed else "uncertain"
    recorder.set_status(final_status, "submit_application")
    return {"status": final_status, "steps": [{"name": "submit_application", "status": final_status}]}
