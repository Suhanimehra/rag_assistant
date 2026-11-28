"""Process-local abuse controls.

These limits are intentionally lightweight and have no external dependency.
For multi-worker or multi-instance deployments, replace the in-memory store
with a shared Redis-backed limiter or enforce limits at the reverse proxy.
"""
from collections import deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = {}
        self._lock = Lock()

    def check(self, key: str) -> None:
        now = monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            bucket = self._events.setdefault(key, deque())
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= self.limit:
                retry_after = max(1, int(self.window_seconds - (now - bucket[0])))
                raise HTTPException(
                    429,
                    "Too many requests. Try again later.",
                    headers={"Retry-After": str(retry_after)},
                )
            bucket.append(now)
            if len(self._events) > 10_000:
                for event_key, events in list(self._events.items()):
                    if not events or events[-1] <= cutoff:
                        del self._events[event_key]

    def reset(self) -> None:
        with self._lock:
            self._events.clear()


login_limiter = SlidingWindowLimiter(limit=10, window_seconds=60)
login_ip_limiter = SlidingWindowLimiter(limit=60, window_seconds=60)
register_limiter = SlidingWindowLimiter(limit=5, window_seconds=300)
register_ip_limiter = SlidingWindowLimiter(limit=20, window_seconds=300)
chat_limiter = SlidingWindowLimiter(limit=30, window_seconds=60)


def client_key(request: Request) -> str:
    # request.client.host is the direct peer. Only trust forwarded headers when
    # a known reverse proxy is responsible for overwriting them.
    return request.client.host if request.client else "unknown"
