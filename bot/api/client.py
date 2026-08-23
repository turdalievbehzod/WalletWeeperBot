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
        # DELETE and some PATCH responses come back 204/empty — .json() would
        # raise on an empty body, so short-circuit rather than special-case
        # every call site.
        if not resp.content:
            return None
        return resp.json()

    # ── Expenses ──────────────────────────────────────────────────────────────

    async def create_expense(
        self,
        telegram_id: int,
        amount: Decimal | float,
        description: str,
        transaction_type: str = 'expense',
    ) -> dict:
        """POST /expenses/bot-create/ — transaction_type: 'expense' | 'income'"""
        return await self._request(
            'POST', '/expenses/bot-create/',
            headers=self._bot_headers(telegram_id),
            json={'amount': float(amount), 'description': description, 'transaction_type': transaction_type},
        )

    # ── Notifications ─────────────────────────────────────────────────────────

    async def get_notification(self, telegram_id: int) -> dict:
        """GET /expenses/bot-notify/ → {"notification_setting": "off" | "daily" | "weekly"}"""
        return await self._request(
            'GET', '/expenses/bot-notify/',
            headers=self._bot_headers(telegram_id),
        )

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

    # ── Notes / reminders ────────────────────────────────────────────────────

    async def create_note(self, telegram_id: int, text: str, **fields) -> dict:
        """
        POST /bot/notes/
        fields is ONE of:
          preset='once_1h' | 'daily_now'
          time='14:30', repeat='daily'
          remind_at='2026-12-25T14:30:00', repeat='once'
        The backend resolves all of these to an actual remind_at in the
        user's own timezone (user.timezone), since the bot doesn't know it.
        """
        return await self._request(
            'POST', '/bot/notes/',
            headers=self._bot_headers(telegram_id),
            json={'text': text, **fields},
        )

    async def list_notes(self, telegram_id: int) -> list[dict]:
        """GET /bot/notes/list/ — this user's upcoming (unsent) reminders, soonest first."""
        return await self._request(
            'GET', '/bot/notes/list/',
            headers=self._bot_headers(telegram_id),
        )

    async def delete_note(self, telegram_id: int, note_id: int) -> None:
        """DELETE /bot/notes/<note_id>/"""
        await self._request(
            'DELETE', f'/bot/notes/{note_id}/',
            headers=self._bot_headers(telegram_id),
        )

    async def get_due_notes(self) -> list[dict]:
        """GET /bot/notes/due/ — reminders across all users whose time has come. Polled by the bot."""
        return await self._request(
            'GET', '/bot/notes/due/',
            headers=self._bot_headers(),
        )

    async def mark_note_sent(self, note_id: int) -> dict:
        """PATCH /bot/notes/<note_id>/sent/ — call right after delivering a due reminder."""
        return await self._request(
            'PATCH', f'/bot/notes/{note_id}/sent/',
            headers=self._bot_headers(),
        )

    # ── Broadcast targets ──────────────────────────────────────────────────────

    async def get_broadcast_targets(self, mode: str) -> list[int]:
        """GET /expenses/bot-broadcast-targets/?mode=daily|weekly|all — 'all' backs the /broadcast admin command."""
        data = await self._request(
            'GET', f'/expenses/bot-broadcast-targets/?mode={mode}',
            headers=self._bot_headers(),
        )
        return data.get('telegram_ids', [])

    # ── Digest reminders ("don't forget to log your expenses") ────────────────

    async def get_digest_due(self) -> list[int]:
        """GET /expenses/bot-digest-due/ — telegram_ids whose daily/weekly digest is due right now."""
        data = await self._request(
            'GET', '/expenses/bot-digest-due/',
            headers=self._bot_headers(),
        )
        return data.get('telegram_ids', [])

    async def mark_digest_sent(self, telegram_ids: list[int]) -> None:
        """PATCH /expenses/bot-digest-sent/ — call right after delivering the digest to these users."""
        await self._request(
            'PATCH', '/expenses/bot-digest-sent/',
            headers=self._bot_headers(),
            json={'telegram_ids': telegram_ids},
        )

    async def aclose(self):
        await self._http.aclose()
