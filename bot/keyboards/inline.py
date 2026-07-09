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
