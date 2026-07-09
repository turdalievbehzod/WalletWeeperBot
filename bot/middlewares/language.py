"""
Injects the resolved `lang: str` ('ru' | 'en') into every handler's
workflow data, based on the update's sender.
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from services.language import LanguageResolver


class LanguageMiddleware(BaseMiddleware):
    def __init__(self, resolver: LanguageResolver):
        self._resolver = resolver

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get('event_from_user')
        data['lang'] = (
            await self._resolver.get_language(user.id, user.language_code)
            if user is not None else 'ru'
        )
        return await handler(event, data)
