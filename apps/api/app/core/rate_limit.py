import logging
import threading
import time
from dataclasses import dataclass

from fastapi import HTTPException, Request
from redis import Redis

from app.core.config import settings

logger = logging.getLogger("applyforge.rate_limit")


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    remaining: int
    retry_after_seconds: int


class InMemoryRateLimitStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._bucket: dict[str, tuple[int, float]] = {}

    def consume(self, key: str, limit: int, window_seconds: int) -> RateLimitResult:
        now = time.time()
        with self._lock:
            count, expires_at = self._bucket.get(key, (0, now + window_seconds))
            if expires_at <= now:
                count = 0
                expires_at = now + window_seconds
            count += 1
            self._bucket[key] = (count, expires_at)
            remaining = max(0, limit - count)
            retry_after_seconds = max(1, int(expires_at - now))
            return RateLimitResult(allowed=count <= limit, remaining=remaining, retry_after_seconds=retry_after_seconds)


_memory_store = InMemoryRateLimitStore()


def _redis_client() -> Redis | None:
    try:
        client = Redis.from_url(settings.redis_url)
        client.ping()
        return client
    except Exception:
        return None


def _subject_from_request(request: Request | None, *, fallback: str) -> str:
    if request and request.client and request.client.host:
        return request.client.host
    return fallback


def consume_rate_limit(*, bucket: str, subject: str, limit: int, window_seconds: int) -> RateLimitResult:
    redis_client = _redis_client()
    key = f"applyforge:rate:{bucket}:{subject}"
    if redis_client:
        current = int(redis_client.incr(key))
        if current == 1:
            redis_client.expire(key, window_seconds)
        ttl = int(redis_client.ttl(key))
        return RateLimitResult(
            allowed=current <= limit,
            remaining=max(0, limit - current),
            retry_after_seconds=max(1, ttl if ttl > 0 else window_seconds),
        )
    return _memory_store.consume(key, limit, window_seconds)


def enforce_rate_limit(
    *,
    bucket: str,
    request: Request | None,
    limit: int,
    window_seconds: int,
    subject_suffix: str = "",
) -> None:
    subject = _subject_from_request(request, fallback="local")
    if subject_suffix:
        subject = f"{subject}:{subject_suffix.lower()}"
    result = consume_rate_limit(bucket=bucket, subject=subject, limit=limit, window_seconds=window_seconds)
    if result.allowed:
        return
    logger.warning(
        "rate_limit_exceeded",
        extra={
            "bucket": bucket,
            "subject": subject,
            "limit": limit,
            "window_seconds": window_seconds,
            "retry_after_seconds": result.retry_after_seconds,
        },
    )
    raise HTTPException(
        status_code=429,
        detail=f"Too many requests. Retry in about {result.retry_after_seconds} seconds.",
        headers={"Retry-After": str(result.retry_after_seconds)},
    )
