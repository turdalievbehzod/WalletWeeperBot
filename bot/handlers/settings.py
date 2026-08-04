"""
Управление настройками уведомлений и языка.

Команды: /settings, /reminders
Inline-кнопки: notify:daily | notify:weekly | notify:off | lang:ru | lang:en
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from api.client import DjangoAPIError, DjangoClient
from i18n import t
from keyboards.inline import settings_keyboard
from services.language import LanguageResolver

router = Router(name='settings')


async def _render_settings(target: Message | CallbackQuery, django: DjangoClient, telegram_id: int, lang: str) -> None:
    """Fetches the user's real notification setting and draws the /settings screen —
    shared by the initial /settings command and the redraw after a language change,
    so the checkmark on the notify options is never stale."""
    try:
        current_notify = (await django.get_notification(telegram_id))['notification_setting']
    except DjangoAPIError as e:
        message = target.message if isinstance(target, CallbackQuery) else target
        if e.status_code == 404:
            await message.answer(t('not_registered', lang))
        else:
            await message.answer(t('notify_error', lang, code=e.status_code))
        return

    text = t('settings_text', lang)
    markup = settings_keyboard(current_notify=current_notify, current_lang=lang, lang=lang)

    if isinstance(target, CallbackQuery):
        try:
            await target.message.edit_text(text, parse_mode='HTML')
            await target.message.edit_reply_markup(reply_markup=markup)
        except Exception:
            pass  # сообщение уже могло быть удалено/устарело — молча игнорируем
    else:
        await target.answer(text, parse_mode='HTML', reply_markup=markup)


@router.message(Command('settings', 'reminders'))
async def cmd_settings(message: Message, django: DjangoClient, lang: str):
    await _render_settings(message, django, message.from_user.id, lang)


@router.callback_query(F.data.startswith('notify:'))
async def on_notify_change(call: CallbackQuery, django: DjangoClient, lang: str):
    setting = call.data.split(':', 1)[1]  # 'daily' | 'weekly' | 'off'
    telegram_id = call.from_user.id

    try:
        await django.set_notification(telegram_id, setting)
    except DjangoAPIError as e:
        await call.answer(t('notify_error', lang, code=e.status_code), show_alert=True)
        return

    label = t(f'notify_{setting}', lang)
    await call.answer(t('notify_saved', lang, label=label), show_alert=True)

    # Обновляем клавиатуру, чтобы галочка переместилась на новую опцию
    try:
        await call.message.edit_reply_markup(
            reply_markup=settings_keyboard(current_notify=setting, current_lang=lang, lang=lang)
        )
    except Exception:
        pass  # Если сообщение уже устарело — молча игнорируем


@router.callback_query(F.data.startswith('lang:'))
async def on_language_change(
    call: CallbackQuery,
    django: DjangoClient,
    language_resolver: LanguageResolver,
    lang: str,
):
    new_lang = call.data.split(':', 1)[1]  # 'ru' | 'en'
    telegram_id = call.from_user.id

    try:
        await language_resolver.set_language(telegram_id, new_lang)
    except DjangoAPIError as e:
        await call.answer(t('language_error', lang, code=e.status_code), show_alert=True)
        return

    await call.answer(t('language_saved', new_lang), show_alert=True)

    # Перерисовываем экран настроек целиком на новом языке, с реальным notification_setting
    await _render_settings(call, django, telegram_id, new_lang)
