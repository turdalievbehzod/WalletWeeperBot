"""
Holds the draft of a reminder the user just typed while they walk through
the /note flow (pick once/daily, then a quick default or type their own
date/time) — a multi-step conversation without introducing FSM, backed by
Redis the same way LanguageResolver caches language preferences.

Draft shape (JSON): {"text": str, "await": None | "once_custom" | "daily_custom"}
`await` is set right before we prompt the user to type a date/time by hand,
so the next free-text message from them is recognized as that reply
instead of falling through to the quick-expense parser.
"""
from __future__ import annotations

import json

import redis.asyncio as redis

from config import Config

_CACHE_PREFIX = 'bot:pending_note:'
_TTL_SECONDS = 600  # draft expires if the flow isn't finished within 10 minutes


class PendingNoteStore:
    def __init__(self, cfg: Config):
        self._redis = redis.from_url(cfg.redis_url, decode_responses=True)

    async def set(self, telegram_id: int, text: str) -> None:
        """Starts a fresh draft right after `/note <text>`."""
        draft = {'text': text, 'await': None}
        await self._redis.set(_CACHE_PREFIX + str(telegram_id), json.dumps(draft), ex=_TTL_SECONDS)

    async def get(self, telegram_id: int) -> dict | None:
        """Peeks at the current draft without clearing it, or None if there isn't one / it expired."""
        raw = await self._redis.get(_CACHE_PREFIX + str(telegram_id))
        return json.loads(raw) if raw is not None else None

    async def set_awaiting(self, telegram_id: int, kind: str) -> bool:
        """Marks that the next free-text message is a custom date/time reply. Returns False if the draft is gone."""
        draft = await self.get(telegram_id)
        if draft is None:
            return False
        draft['await'] = kind
        await self._redis.set(_CACHE_PREFIX + str(telegram_id), json.dumps(draft), ex=_TTL_SECONDS)
        return True

    async def pop(self, telegram_id: int) -> dict | None:
        """Returns the pending draft and clears it, or None if there isn't one / it expired."""
        key = _CACHE_PREFIX + str(telegram_id)
        draft = await self.get(telegram_id)
        if draft is not None:
            await self._redis.delete(key)
        return draft

    async def aclose(self):
        await self._redis.aclose()
