"""
Рассылка от владельца бота — /broadcast.

Доступна только telegram_id из ADMIN_IDS (bot/config.py). Флоу:
  1. /broadcast                — просим прислать текст следующим сообщением.
  2. свободный текст от админа — сохраняем как черновик, показываем
     предпросмотр с кнопками [Отправить] / [Отмена].
  3. broadcast_confirm         — тянем всех зарегистрированных пользователей
     из бэкенда и рассылаем всем одновременно (services/broadcast.py).
     broadcast_cancel — просто чистим черновик.

Немного жёстче, чем /note: неадмины не получают вообще никакого ответа —
фильтр IsAdmin просто не пропускает апдейт дальше, feature не палится.
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import BaseFilter, Command
from aiogram.types import CallbackQuery, Message

from api.client import DjangoAPIError, DjangoClient
from i18n import t
from keyboards.inline import broadcast_confirm_keyboard
from services.broadcast import broadcast_to
from services.pending_broadcast import PendingBroadcastStore

router = Router(name='admin')


class IsAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery, admin_ids: frozenset[int]) -> bool:
        return event.from_user.id in admin_ids


class AwaitingBroadcastText(BaseFilter):
    async def __call__(self, message: Message, pending_broadcast: PendingBroadcastStore, admin_ids: frozenset[int]) -> bool:
        if not message.text or message.from_user.id not in admin_ids:
            return False
        return await pending_broadcast.is_awaiting(message.from_user.id)


@router.message(Command('broadcast'), IsAdmin())
async def cmd_broadcast(message: Message, pending_broadcast: PendingBroadcastStore, lang: str):
    await pending_broadcast.start_awaiting(message.from_user.id)
    await message.reply(t('broadcast_prompt', lang), parse_mode='HTML')


@router.message(AwaitingBroadcastText())
async def on_broadcast_text(message: Message, pending_broadcast: PendingBroadcastStore, lang: str):
    await pending_broadcast.set_text(message.from_user.id, message.text)
    await message.reply(
        t('broadcast_preview', lang, text=message.text),
        parse_mode='HTML',
        reply_markup=broadcast_confirm_keyboard(lang),
    )


@router.callback_query(F.data == 'broadcast_confirm', IsAdmin())
async def on_broadcast_confirm(call: CallbackQuery, django: DjangoClient, pending_broadcast: PendingBroadcastStore, lang: str):
    text = await pending_broadcast.pop_text(call.from_user.id)
    if not text:
        await call.answer(t('broadcast_expired', lang), show_alert=True)
        return

    try:
        telegram_ids = await django.get_broadcast_targets('all')
    except DjangoAPIError as e:
        await call.answer(t('broadcast_error', lang, detail=e.detail), show_alert=True)
        return

    await call.answer()
    sent, failed = await broadcast_to(call.bot, telegram_ids, text)
    try:
        await call.message.edit_text(t('broadcast_done', lang, sent=sent, failed=failed))
    except Exception:
        pass  # сообщение уже могло быть удалено/устарело — молча игнорируем


@router.callback_query(F.data == 'broadcast_cancel', IsAdmin())
async def on_broadcast_cancel(call: CallbackQuery, pending_broadcast: PendingBroadcastStore, lang: str):
    await pending_broadcast.pop_text(call.from_user.id)
    await call.answer()
    try:
        await call.message.edit_text(t('broadcast_cancelled', lang))
    except Exception:
        pass
