"""
Holds the text of a reminder the user just typed while they pick a time
via inline buttons — a two-step flow without introducing FSM, backed by
Redis the same way LanguageResolver caches language preferences.
"""
from __future__ import annotations

import redis.asyncio as redis

from config import Config

_CACHE_PREFIX = 'bot:pending_note:'
_TTL_SECONDS = 600  # draft expires if no time is picked within 10 minutes


class PendingNoteStore:
    def __init__(self, cfg: Config):
        self._redis = redis.from_url(cfg.redis_url, decode_responses=True)

    async def set(self, telegram_id: int, text: str) -> None:
        await self._redis.set(_CACHE_PREFIX + str(telegram_id), text, ex=_TTL_SECONDS)

    async def pop(self, telegram_id: int) -> str | None:
        """Returns the pending text and clears it, or None if there isn't one / it expired."""
        key = _CACHE_PREFIX + str(telegram_id)
        text = await self._redis.get(key)
        if text is not None:
            await self._redis.delete(key)
        return text

    async def aclose(self):
        await self._redis.aclose()
