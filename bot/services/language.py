"""
Resolves and caches each Telegram user's language preference.

Backed by a dedicated redis.asyncio client (kept separate from aiogram's
own RedisStorage, which is used for FSM state) so this cache has its own
lifecycle and isn't coupled to aiogram internals.
"""
from __future__ import annotations

import redis.asyncio as redis

from api.client import DjangoAPIError, DjangoClient
from config import Config

_CACHE_PREFIX = 'bot:lang:'


class LanguageResolver:
    def __init__(self, cfg: Config, django: DjangoClient):
        self._redis = redis.from_url(cfg.redis_url, decode_responses=True)
        self._django = django

    async def get_language(self, telegram_id: int, tg_language_code: str | None) -> str:
        cached = await self._redis.get(_CACHE_PREFIX + str(telegram_id))
        if cached:
            return cached

        try:
            data = await self._django.get_language(telegram_id)
        except DjangoAPIError:
            # Not registered yet (or backend unreachable) — fall back to the
            # Telegram client's own language; not cached since there's no
            # user row to key this cache entry off yet.
            return 'en' if tg_language_code == 'en' else 'ru'

        language = data.get('language', 'ru')
        await self._redis.set(_CACHE_PREFIX + str(telegram_id), language)
        return language

    async def set_language(self, telegram_id: int, language: str) -> None:
        await self._django.set_language(telegram_id, language)
        await self._redis.set(_CACHE_PREFIX + str(telegram_id), language)

    async def aclose(self):
        await self._redis.aclose()
