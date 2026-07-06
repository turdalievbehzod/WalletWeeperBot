"""
Управление настройками уведомлений.

Команды: /settings, /reminders
Inline-кнопки: notify:daily | notify:weekly | notify:off
"""
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from api.client import DjangoAPIError, DjangoClient
from keyboards.inline import notifications_keyboard

router = Router(name='settings')

_LABELS = {
    'daily':  '🟢 Каждый вечер',
    'weekly': '🔵 Раз в неделю (в воскресенье утром)',
    'off':    '🔴 Уведомления отключены',
}

_SETTINGS_TEXT = (
    '⚙️ <b>Настройка уведомлений</b>\n\n'
    'Выбери, как часто тебе напоминать о ведении учёта:'
)


@router.message(Command('settings', 'reminders'))
async def cmd_settings(message: Message):
    await message.answer(
        _SETTINGS_TEXT,
        parse_mode='HTML',
        reply_markup=notifications_keyboard(),
    )


@router.callback_query(F.data.startswith('notify:'))
async def on_notify_change(call: CallbackQuery, django: DjangoClient):
    setting = call.data.split(':', 1)[1]  # 'daily' | 'weekly' | 'off'
    telegram_id = call.from_user.id

    try:
        await django.set_notification(telegram_id, setting)
    except DjangoAPIError as e:
        await call.answer(f'Ошибка (код {e.status_code}). Попробуйте позже.', show_alert=True)
        return

    label = _LABELS.get(setting, setting)
    await call.answer(f'✅ Настройки сохранены!\n{label}', show_alert=True)

    # Обновляем клавиатуру, чтобы галочка переместилась на новую опцию
    try:
        await call.message.edit_reply_markup(
            reply_markup=notifications_keyboard(current=setting)
        )
    except Exception:
        pass  # Если сообщение уже устарело — молча игнорируем
