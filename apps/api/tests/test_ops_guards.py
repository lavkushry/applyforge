import json
import logging

from app.core.observability import JsonLogFormatter
from app.core.rate_limit import InMemoryRateLimitStore


def test_json_log_formatter_keeps_request_id_and_extra_fields() -> None:
    formatter = JsonLogFormatter()
    record = logging.LogRecord(
        name="applyforge.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="request_completed",
        args=(),
        exc_info=None,
    )
    record.request_id = "req-123"
    record.path = "/jobs"
    payload = json.loads(formatter.format(record))

    assert payload["request_id"] == "req-123"
    assert payload["path"] == "/jobs"
    assert payload["message"] == "request_completed"


def test_in_memory_rate_limit_store_blocks_after_limit() -> None:
    store = InMemoryRateLimitStore()

    first = store.consume("auth.login:test", limit=2, window_seconds=60)
    second = store.consume("auth.login:test", limit=2, window_seconds=60)
    third = store.consume("auth.login:test", limit=2, window_seconds=60)

    assert first.allowed is True
    assert second.allowed is True
    assert third.allowed is False
    assert third.retry_after_seconds >= 1
