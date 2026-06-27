import time
from fastapi import Request, HTTPException

# Simple in-memory sliding window rate limiter
_rate_limits = {}


def check_rate_limit(client_id: str, limit_count: int, window_seconds: int):
    """Enforces rate limits by tracking timestamps in a sliding window."""
    now = time.time()

    if client_id not in _rate_limits:
        _rate_limits[client_id] = []

    # Remove old requests outside the window
    _rate_limits[client_id] = [
        t for t in _rate_limits[client_id] if now - t < window_seconds
    ]

    if len(_rate_limits[client_id]) >= limit_count:
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")

    _rate_limits[client_id].append(now)


async def rate_limit_query(request: Request):
    """Dependency: 30 requests per minute."""
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(f"query_{client_ip}", limit_count=30, window_seconds=60)


async def rate_limit_upload(request: Request):
    """Dependency: 10 uploads per hour."""
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(f"upload_{client_ip}", limit_count=10, window_seconds=3600)
