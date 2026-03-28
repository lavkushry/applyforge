from collections.abc import Iterable


def coerce_text(value: object | None) -> str:
    if value is None:
        return ""
    return str(value).strip()


def compact_list(values: Iterable[object | None]) -> list[str]:
    result: list[str] = []
    for value in values:
        text = coerce_text(value)
        if text:
            result.append(text)
    return result


def dedupe_preserve_order(values: Iterable[object | None]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in compact_list(values):
        lowered = value.casefold()
        if lowered in seen:
            continue
        seen.add(lowered)
        result.append(value)
    return result


def compact_mapping(values: dict[str, object | None]) -> dict[str, str]:
    return {key: text for key, text in ((key, coerce_text(value)) for key, value in values.items()) if text}
