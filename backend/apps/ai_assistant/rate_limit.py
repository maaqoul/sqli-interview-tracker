from django.core.cache import cache
from rest_framework.exceptions import Throttled

AI_RATE_LIMIT = 20
AI_RATE_WINDOW_SECONDS = 3600


def check_ai_rate_limit(user) -> None:
    """Enforce max 20 AI calls per user per hour (INT-034)."""
    key = f"ai_rate:{user.id}"
    count = cache.get(key, 0)
    if count >= AI_RATE_LIMIT:
        raise Throttled(
            detail=f"AI rate limit exceeded ({AI_RATE_LIMIT} calls per hour)."
        )
    if count == 0:
        cache.set(key, 1, timeout=AI_RATE_WINDOW_SECONDS)
    else:
        cache.incr(key)


def reset_ai_rate_limit(user) -> None:
    cache.delete(f"ai_rate:{user.id}")
