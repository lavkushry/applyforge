from __future__ import annotations

from datetime import datetime

FIELD_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("linkedin_url", ("linkedin",)),
    ("github_url", ("github",)),
    ("portfolio_url", ("portfolio", "website", "personal site", "personal webpage")),
    ("email", ("email", "e-mail")),
    ("phone", ("phone", "mobile", "cell")),
    ("full_name", ("full name", "legal name", "applicant name", "candidate name")),
    ("willing_to_relocate", ("relocate", "relocation")),
    ("location", ("location", "city", "current location")),
    ("salary_expectation", ("salary expectation", "desired salary", "expected salary", "compensation", "salary")),
    ("years_of_experience", ("years of experience", "years experience", "experience years")),
    ("available_start_date", ("available start", "start date", "available to start", "available from")),
    ("notice_period", ("notice period", "notice", "availability")),
    ("requires_sponsorship", ("require sponsorship", "need sponsorship", "sponsorship", "visa sponsorship")),
    ("authorized_to_work", ("authorized to work", "work authorization", "legally authorized")),
    ("work_authorization", ("work permit", "work authorization details")),
)

YES_TOKENS = ("yes", "true", "authorized", "available", "willing", "immediately", "now")
NO_TOKENS = ("no", "false", "not authorized", "not available", "not willing")


def field_context_text(field: dict) -> str:
    return " ".join(
        str(field.get(key, ""))
        for key in ("label_text", "group_label", "name", "id", "placeholder", "aria_label", "option_text")
    ).strip().lower()


def resolve_answer_key(field: dict) -> str | None:
    context = field_context_text(field)
    if not context:
        return None
    for answer_key, keywords in FIELD_KEYWORDS:
        if any(keyword in context for keyword in keywords):
            return answer_key
    return None


def normalize_boolean_answer(value: object) -> bool | None:
    text = str(value or "").strip().lower()
    if not text:
        return None
    if any(token in text for token in YES_TOKENS):
        return True
    if any(token in text for token in NO_TOKENS):
        return False
    return None


def normalize_date_answer(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return text if len(text) == 10 and text[4] == "-" else ""


def choice_match_tokens(answer_key: str, answer: object) -> tuple[str, ...]:
    text = str(answer or "").strip().lower()
    if not text:
        return ()
    boolean_value = normalize_boolean_answer(text)
    if answer_key in {"authorized_to_work", "willing_to_relocate"} and boolean_value is not None:
        return ("yes", "true", "authorized", "willing") if boolean_value else ("no", "false", "not")
    if answer_key == "requires_sponsorship" and boolean_value is not None:
        return ("yes", "true", "require") if boolean_value else ("no", "false", "not")
    return tuple(part for part in text.replace("/", " ").replace(",", " ").split() if len(part) > 1)


def select_option(field: dict, answer_key: str, answer: object) -> dict | None:
    options = field.get("options") or []
    tokens = choice_match_tokens(answer_key, answer)
    if not options:
        return None
    if tokens:
        for option in options:
            haystack = f"{option.get('text', '')} {option.get('value', '')}".strip().lower()
            if haystack and any(token in haystack for token in tokens):
                return {"type": "select", "option": option}
    answer_text = str(answer or "").strip().lower()
    for option in options:
        haystack = f"{option.get('text', '')} {option.get('value', '')}".strip().lower()
        if answer_text and answer_text == haystack:
            return {"type": "select", "option": option}
    return None


def resolve_field_action(field: dict, answers: dict) -> dict | None:
    answer_key = resolve_answer_key(field)
    if not answer_key:
        return None
    answer = answers.get(answer_key)
    field_type = str(field.get("type", "")).lower()
    tag_name = str(field.get("tag_name", "")).lower()
    if answer in (None, ""):
        return None

    if tag_name == "select":
        selected = select_option(field, answer_key, answer)
        if selected:
            return {"answer_key": answer_key, **selected}
        return None

    if field_type == "radio":
        tokens = choice_match_tokens(answer_key, answer)
        option_text = str(field.get("option_text", "")).lower()
        if option_text and any(token in option_text for token in tokens):
            return {"answer_key": answer_key, "type": "radio", "value": True}
        return None

    if field_type == "checkbox":
        boolean_value = normalize_boolean_answer(answer)
        if boolean_value is None:
            return None
        return {"answer_key": answer_key, "type": "checkbox", "value": boolean_value}

    if field_type == "date":
        normalized = normalize_date_answer(answer)
        if normalized:
            return {"answer_key": answer_key, "type": "fill", "value": normalized}
        return None

    if field_type in {"number", "tel", "email", "url", "text", ""} or tag_name == "textarea":
        return {"answer_key": answer_key, "type": "fill", "value": str(answer)}

    return None
