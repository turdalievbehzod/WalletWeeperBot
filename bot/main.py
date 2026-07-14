"""
Точка входа бота.

Запускает два asyncio-корутины параллельно:
  1. aiogram long-polling — обрабатывает входящие сообщения
  2. aiohttp веб-сервер  — принимает рассылки от Django/Celery
"""
import asyncio
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from config import load_config
from api.client import DjangoAPIError, DjangoClient
from handlers import start, expenses, settings, notes
from handlers.broadcast_server import create_broadcast_app
from i18n import t
from middlewares.language import LanguageMiddleware
from services.language import LanguageResolver

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-8s  %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)

_NOTE_POLL_INTERVAL = 30  # seconds


async def _note_reminder_loop(bot: Bot, django: DjangoClient, language_resolver: LanguageResolver):
    """
    Polls for due reminders and delivers them by direct message.
    Runs alongside long-polling for the lifetime of the process — there's no
    Celery/cron in this stack, so the bot itself owns the delivery schedule.
    """
    while True:
        try:
            due = await django.get_due_notes()
        except DjangoAPIError:
            logger.exception('Failed to fetch due notes')
            due = []

        for note in due:
            telegram_id = note['telegram_id']
            lang = await language_resolver.get_language(telegram_id, None)
            try:
                await bot.send_message(telegram_id, t('note_reminder', lang, text=note['text']), parse_mode='HTML')
            except Exception:
                logger.warning('Failed to deliver reminder %s to %s', note['id'], telegram_id)
                continue
            try:
                await django.mark_note_sent(note['id'])
            except DjangoAPIError:
                logger.exception('Failed to mark note %s as sent', note['id'])

        await asyncio.sleep(_NOTE_POLL_INTERVAL)


async def main():
    cfg = load_config()

    # ── Bot & Storage ──────────────────────────────────────────────────────────
    bot = Bot(
        token=cfg.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    storage = RedisStorage.from_url(cfg.redis_url)
    dp = Dispatcher(storage=storage)

    # ── Django API client — один на всё приложение ─────────────────────────────
    django_client = DjangoClient(cfg)
    language_resolver = LanguageResolver(cfg, django_client)

    # ── Middleware: пробрасываем зависимости в хэндлеры ───────────────────────
    # Используем workflow_data — данные, доступные в каждом хэндлере через аргументы
    dp['django']            = django_client
    dp['mini_app_url']      = cfg.mini_app_url
    dp['language_resolver'] = language_resolver

    # Резолвит язык пользователя для каждого входящего апдейта → data['lang']
    dp.message.middleware(LanguageMiddleware(language_resolver))
    dp.callback_query.middleware(LanguageMiddleware(language_resolver))

    # ── Регистрация роутеров ───────────────────────────────────────────────────
    dp.include_router(start.router)
    dp.include_router(expenses.router)
    dp.include_router(settings.router)
    dp.include_router(notes.router)

    # ── Фоновая доставка напоминаний ────────────────────────────────────────────
    reminder_task = asyncio.create_task(_note_reminder_loop(bot, django_client, language_resolver))

    # ── Broadcast HTTP-сервер ──────────────────────────────────────────────────
    broadcast_app = create_broadcast_app(bot, cfg.internal_secret)
    runner = web.AppRunner(broadcast_app)
    await runner.setup()
    site = web.TCPSite(runner, host='0.0.0.0', port=cfg.broadcast_port)
    await site.start()
    logger.info('Broadcast server started on port %d', cfg.broadcast_port)

    # ── Старт polling ──────────────────────────────────────────────────────────
    logger.info('Bot is starting polling...')
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        reminder_task.cancel()
        await runner.cleanup()
        await django_client.aclose()
        await language_resolver.aclose()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
