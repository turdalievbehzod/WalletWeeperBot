"""
Async HTTP client for bot ↔ Django backend communication.

All requests use header-based auth (X-Bot-Secret + X-Telegram-Id)
instead of JWT — the bot is a trusted internal service, not a user client.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any

import httpx

from config import Config


class DjangoAPIError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f'[{status_code}] {detail}')


class DjangoClient:
    def __init__(self, cfg: Config):
        self._base = cfg.django_api_url + '/api/v1'
        self._secret = cfg.bot_secret
        # Shared async client — reuse connections across requests.
        self._http = httpx.AsyncClient(timeout=10.0)

    def _bot_headers(self, telegram_id: int | None = None) -> dict:
        h = {'X-Bot-Secret': self._secret}
        if telegram_id is not None:
            h['X-Telegram-Id'] = str(telegram_id)
        return h

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        resp = await self._http.request(method, f'{self._base}{path}', **kwargs)
        if resp.status_code >= 400:
            try:
                detail = resp.json().get('detail', resp.text)
            except Exception:
                detail = resp.text
            raise DjangoAPIError(resp.status_code, detail)
        return resp.json()

    # ── Expenses ──────────────────────────────────────────────────────────────

    async def create_expense(
        self,
        telegram_id: int,
        amount: Decimal | float,
        description: str,
    ) -> dict:
        """POST /expenses/bot-create/"""
        return await self._request(
            'POST', '/expenses/bot-create/',
            headers=self._bot_headers(telegram_id),
            json={'amount': float(amount), 'description': description},
        )

    # ── Notifications ─────────────────────────────────────────────────────────

    async def set_notification(self, telegram_id: int, setting: str) -> dict:
        """PATCH /expenses/bot-notify/ — setting: 'off' | 'daily' | 'weekly'"""
        return await self._request(
            'PATCH', '/expenses/bot-notify/',
            headers=self._bot_headers(telegram_id),
            json={'notification_setting': setting},
        )

    # ── Language ──────────────────────────────────────────────────────────────

    async def get_language(self, telegram_id: int) -> dict:
        """GET /expenses/bot-language/ → {"language": "ru" | "en"}"""
        return await self._request(
            'GET', '/expenses/bot-language/',
            headers=self._bot_headers(telegram_id),
        )

    async def set_language(self, telegram_id: int, language: str) -> dict:
        """PATCH /expenses/bot-language/ — language: 'ru' | 'en'"""
        return await self._request(
            'PATCH', '/expenses/bot-language/',
            headers=self._bot_headers(telegram_id),
            json={'language': language},
        )

    # ── Broadcast targets (called by scheduler, not by bot) ───────────────────

    async def get_broadcast_targets(self, mode: str) -> list[int]:
        """GET /expenses/bot-broadcast-targets/?mode=daily|weekly"""
        data = await self._request(
            'GET', f'/expenses/bot-broadcast-targets/?mode={mode}',
            headers=self._bot_headers(),
        )
        return data.get('telegram_ids', [])

    async def aclose(self):
        await self._http.aclose()
