from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from i18n import t


def open_app_keyboard(mini_app_url: str, lang: str) -> InlineKeyboardMarkup:
    """Кнопка открытия Mini App на главном экране /start."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=t('open_app_button', lang),
            web_app=WebAppInfo(url=mini_app_url),
        )
    ]])


def settings_keyboard(current_notify: str, current_lang: str, lang: str) -> InlineKeyboardMarkup:
    """
    Combined notifications + language keyboard shown by /settings.
    current_notify — currently selected notification setting ('off' | 'daily' | 'weekly').
    current_lang   — currently selected language ('ru' | 'en').
    lang           — language to render the button labels in.
    Active options are marked with a checkmark.
    """
    mark = lambda flag: ' ✅' if flag else ''

    builder = InlineKeyboardBuilder()
    builder.button(
        text=t('notify_daily', lang) + mark(current_notify == 'daily'),
        callback_data='notify:daily',
    )
    builder.button(
        text=t('notify_weekly', lang) + mark(current_notify == 'weekly'),
        callback_data='notify:weekly',
    )
    builder.button(
        text=t('notify_off', lang) + mark(current_notify == 'off'),
        callback_data='notify:off',
    )
    builder.button(
        text=t('language_ru', lang) + mark(current_lang == 'ru'),
        callback_data='lang:ru',
    )
    builder.button(
        text=t('language_en', lang) + mark(current_lang == 'en'),
        callback_data='lang:en',
    )
    builder.adjust(1)
    return builder.as_markup()


def note_mode_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Shown right after /note <text> — one-time vs recurring."""
    builder = InlineKeyboardBuilder()
    builder.button(text=t('note_mode_once', lang),  callback_data='note_mode:once')
    builder.button(text=t('note_mode_daily', lang), callback_data='note_mode:daily')
    builder.adjust(1)
    return builder.as_markup()


def note_once_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Shown after picking 'Одноразово' — quick default vs manual date/time."""
    builder = InlineKeyboardBuilder()
    builder.button(text=t('note_once_1h', lang),     callback_data='note_once:1h')
    builder.button(text=t('note_once_custom', lang), callback_data='note_once:custom')
    builder.adjust(1)
    return builder.as_markup()


def note_daily_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Shown after picking 'Регулярно' — quick default vs manual time."""
    builder = InlineKeyboardBuilder()
    builder.button(text=t('note_daily_now', lang),    callback_data='note_daily:now')
    builder.button(text=t('note_daily_custom', lang), callback_data='note_daily:custom')
    builder.adjust(1)
    return builder.as_markup()


def switch_mode_keyboard(current_mode: str, lang: str) -> InlineKeyboardMarkup:
    """Shown by /switch — which type free-text amount entries create."""
    mark = lambda flag: ' ✅' if flag else ''
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t('switch_expense', lang) + mark(current_mode == 'expense'),
        callback_data='switch_mode:expense',
    )
    builder.button(
        text=t('switch_income', lang) + mark(current_mode == 'income'),
        callback_data='switch_mode:income',
    )
    builder.adjust(1)
    return builder.as_markup()


def broadcast_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Shown after the admin types the announcement text, before it actually goes out."""
    builder = InlineKeyboardBuilder()
    builder.button(text=t('broadcast_send_button', lang),   callback_data='broadcast_confirm')
    builder.button(text=t('broadcast_cancel_button', lang), callback_data='broadcast_cancel')
    builder.adjust(2)
    return builder.as_markup()
