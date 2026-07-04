from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


def open_app_keyboard(mini_app_url: str) -> InlineKeyboardMarkup:
    """Кнопка открытия Mini App на главном экране /start."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text='📊 Открыть приложение',
            web_app=WebAppInfo(url=mini_app_url),
        )
    ]])


def notifications_keyboard(current: str = 'off') -> InlineKeyboardMarkup:
    """
    Клавиатура настроек уведомлений.
    current — текущее значение ('off' | 'daily' | 'weekly').
    Активная опция помечается галочкой.
    """
    mark = lambda key: ' ✅' if current == key else ''

    builder = InlineKeyboardBuilder()
    builder.button(
        text=f'🟢 Каждый вечер{mark("daily")}',
        callback_data='notify:daily',
    )
    builder.button(
        text=f'🔵 Раз в неделю (вс утром){mark("weekly")}',
        callback_data='notify:weekly',
    )
    builder.button(
        text=f'🔴 Отключить{mark("off")}',
        callback_data='notify:off',
    )
    builder.adjust(1)
    return builder.as_markup()
