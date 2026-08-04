"""
Shared "send this message to many users concurrently" helper — used by both
handlers/broadcast_server.py (Django-triggered HTTP broadcast) and
handlers/admin.py (the owner-triggered /broadcast command), so the fan-out
logic isn't duplicated between the two entry points.
"""
import asyncio
import logging

from aiogram import Bot

logger = logging.getLogger(__name__)


async def broadcast_to(bot: Bot, telegram_ids: list[int], text: str) -> tuple[int, int]:
    """Sends `text` to every id in `telegram_ids` concurrently. Returns (sent, failed)."""
    sent, failed = 0, 0

    async def _send(tid: int):
        nonlocal sent, failed
        try:
            await bot.send_message(tid, text, parse_mode='HTML')
            sent += 1
        except Exception as exc:
            logger.warning('Broadcast failed for %d: %s', tid, exc)
            failed += 1

    await asyncio.gather(*(_send(tid) for tid in telegram_ids))
    logger.info('Broadcast done: sent=%d failed=%d', sent, failed)
    return sent, failed
