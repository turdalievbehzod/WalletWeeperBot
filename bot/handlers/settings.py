"""
Управление настройками уведомлений и языка.

Команды: /settings, /reminders
Inline-кнопки: notify:daily | notify:weekly | notify:off | lang:ru | lang:en
"""
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from api.client import DjangoAPIError, DjangoClient
from i18n import t
from keyboards.inline import settings_keyboard
from services.language import LanguageResolver

router = Router(name='settings')


@router.message(Command('settings', 'reminders'))
async def cmd_settings(message: Message, lang: str):
    await message.answer(
        t('settings_text', lang),
        parse_mode='HTML',
        reply_markup=settings_keyboard(current_notify='off', current_lang=lang, lang=lang),
    )


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

    # Перерисовываем экран настроек целиком на новом языке
    try:
        await call.message.edit_text(t('settings_text', new_lang), parse_mode='HTML')
        await call.message.edit_reply_markup(
            reply_markup=settings_keyboard(current_notify='off', current_lang=new_lang, lang=new_lang)
        )
    except Exception:
        pass
