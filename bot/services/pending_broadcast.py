"""
Two-step draft for the admin-only /broadcast flow — same Redis-TTL shape
as PendingNoteStore. One key marks "waiting for the admin to type the
announcement text", a second holds that text once received, waiting for
the [Отправить]/[Отмена] confirmation.
"""
from __future__ import annotations

import redis.asyncio as redis

from config import Config

_PREFIX_AWAIT = 'bot:broadcast:awaiting:'
_PREFIX_TEXT = 'bot:broadcast:text:'
_TTL_SECONDS = 300  # draft expires after 5 minutes of inactivity


class PendingBroadcastStore:
    def __init__(self, cfg: Config):
        self._redis = redis.from_url(cfg.redis_url, decode_responses=True)

    async def start_awaiting(self, admin_id: int) -> None:
        await self._redis.set(_PREFIX_AWAIT + str(admin_id), '1', ex=_TTL_SECONDS)

    async def is_awaiting(self, admin_id: int) -> bool:
        return bool(await self._redis.exists(_PREFIX_AWAIT + str(admin_id)))

    async def set_text(self, admin_id: int, text: str) -> None:
        await self._redis.delete(_PREFIX_AWAIT + str(admin_id))
        await self._redis.set(_PREFIX_TEXT + str(admin_id), text, ex=_TTL_SECONDS)

    async def pop_text(self, admin_id: int) -> str | None:
        key = _PREFIX_TEXT + str(admin_id)
        text = await self._redis.get(key)
        if text is not None:
            await self._redis.delete(key)
        return text

    async def aclose(self):
        await self._redis.aclose()
