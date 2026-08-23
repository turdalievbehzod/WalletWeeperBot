"""
Per-user preference for what a free-text "<amount> <description>" message
creates — 'expense' (default) or 'income'. Set via /switch, persists in
Redis indefinitely (same lifetime as LanguageResolver's cache) until the
user changes it again.
"""
from __future__ import annotations

import redis.asyncio as redis

from config import Config

_CACHE_PREFIX = 'bot:input_mode:'
_DEFAULT = 'expense'


class InputModeStore:
    def __init__(self, cfg: Config):
        self._redis = redis.from_url(cfg.redis_url, decode_responses=True)

    async def get(self, telegram_id: int) -> str:
        mode = await self._redis.get(_CACHE_PREFIX + str(telegram_id))
        return mode if mode in ('expense', 'income') else _DEFAULT

    async def set(self, telegram_id: int, mode: str) -> None:
        await self._redis.set(_CACHE_PREFIX + str(telegram_id), mode)

    async def aclose(self):
        await self._redis.aclose()
