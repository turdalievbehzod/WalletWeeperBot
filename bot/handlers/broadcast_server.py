"""
Внутренний HTTP-сервер для приёма рассылок от Django/Celery.

Django (или Celery-задача) делает:
  POST http://bot-host:8001/internal/broadcast
  Header: X-Internal-Secret: <INTERNAL_SECRET>
  Body:   {"telegram_ids": [123, 456], "message": "Не забудь записать расходы!"}

Бот получает запрос и рассылает сообщение всем указанным пользователям.
"""
import json
import logging

from aiohttp import web
from aiogram import Bot

from services.broadcast import broadcast_to

logger = logging.getLogger(__name__)


async def _handle_broadcast(request: web.Request) -> web.Response:
    internal_secret: str = request.app['internal_secret']
    bot: Bot = request.app['bot']

    # Проверка секрета
    if request.headers.get('X-Internal-Secret', '') != internal_secret:
        return web.json_response({'detail': 'Forbidden'}, status=403)

    try:
        body = await request.json()
    except json.JSONDecodeError:
        return web.json_response({'detail': 'Invalid JSON'}, status=400)

    telegram_ids: list[int] = body.get('telegram_ids', [])
    text: str = body.get('message', '').strip()

    if not telegram_ids or not text:
        return web.json_response({'detail': 'telegram_ids and message are required'}, status=400)

    sent, failed = await broadcast_to(bot, telegram_ids, text)
    return web.json_response({'sent': sent, 'failed': failed})


def create_broadcast_app(bot: Bot, internal_secret: str) -> web.Application:
    """Создаёт aiohttp-приложение с единственным маршрутом рассылки."""
    app = web.Application()
    app['bot'] = bot
    app['internal_secret'] = internal_secret
    app.router.add_post('/internal/broadcast', _handle_broadcast)
    return app
