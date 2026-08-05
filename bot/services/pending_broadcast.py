"""
Draft for the admin-only /broadcast <text> flow — same Redis-TTL shape as
PendingNoteStore. The announcement text comes in as the command's argument
(not a separate "type your next message" step — that pattern used to
intercept ANY subsequent text from the admin, including normal quick-expense
input, whenever a /broadcast was started and not finished), so all this
store needs to hold is the confirmed text while [Отправить]/[Отмена] is
pending.
"""
from __future__ import annotations

import redis.asyncio as redis

from config import Config

_CACHE_PREFIX = 'bot:broadcast:text:'
_TTL_SECONDS = 300  # draft expires after 5 minutes if never confirmed/cancelled


class PendingBroadcastStore:
    def __init__(self, cfg: Config):
        self._redis = redis.from_url(cfg.redis_url, decode_responses=True)

    async def set_text(self, admin_id: int, text: str) -> None:
        await self._redis.set(_CACHE_PREFIX + str(admin_id), text, ex=_TTL_SECONDS)

    async def pop_text(self, admin_id: int) -> str | None:
        key = _CACHE_PREFIX + str(admin_id)
        text = await self._redis.get(key)
        if text is not None:
            await self._redis.delete(key)
        return text

    async def aclose(self):
        await self._redis.aclose()
