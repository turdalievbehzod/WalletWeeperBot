"""
Быстрый текстовый ввод расходов/доходов.

Форматы, которые распознаёт бот:
  25000 обед
  3 500 такси          (пробел внутри числа игнорируется)
  12000.50 кофе

Куда именно попадает сумма — в расходы или в доходы — определяется личным
режимом пользователя (InputModeStore), переключается командой /switch.
По умолчанию режим 'expense', как и было до появления доходов.
"""
from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from api.client import DjangoAPIError, DjangoClient
from i18n import t
from keyboards.inline import switch_mode_keyboard
from services.input_mode import InputModeStore

router = Router(name='expenses')

# Захватываем: (цифры, возможно с пробелами и точкой) + (описание)
_PATTERN = re.compile(
    r'^([\d][\d\s]*(?:[.,]\d+)?)\s+(.+)$',
    re.UNICODE,
)


def _parse_amount(raw: str) -> float | None:
    """'3 500' → 3500.0   '12000.50' → 12000.5   '3,500' → 3500.0"""
    cleaned = raw.replace(' ', '').replace(',', '.')
    try:
        val = float(cleaned)
        return val if val > 0 else None
    except ValueError:
        return None


@router.message(Command('switch'))
async def cmd_switch(message: Message, input_mode: InputModeStore, lang: str):
    current = await input_mode.get(message.from_user.id)
    await message.reply(
        t('switch_pick', lang),
        parse_mode='HTML',
        reply_markup=switch_mode_keyboard(current, lang),
    )


@router.callback_query(F.data.startswith('switch_mode:'))
async def on_switch_mode(call: CallbackQuery, input_mode: InputModeStore, lang: str):
    mode = call.data.split(':', 1)[1]  # 'expense' | 'income'
    await input_mode.set(call.from_user.id, mode)

    label = t(f'switch_{mode}', lang)
    await call.answer(t('switch_saved', lang, label=label), show_alert=True)
    try:
        await call.message.edit_reply_markup(reply_markup=switch_mode_keyboard(mode, lang))
    except Exception:
        pass  # сообщение уже могло быть удалено/устарело — молча игнорируем


@router.message(F.text.regexp(_PATTERN))
async def handle_quick_expense(message: Message, django: DjangoClient, input_mode: InputModeStore, lang: str):
    match = _PATTERN.match(message.text.strip())
    if not match:
        return

    raw_amount, description = match.group(1), match.group(2).strip()
    amount = _parse_amount(raw_amount)
    if amount is None:
        await message.reply(t('quick_expense_invalid_amount', lang), parse_mode='HTML')
        return

    telegram_id = message.from_user.id
    mode = await input_mode.get(telegram_id)

    try:
        await django.create_expense(telegram_id, amount, description, transaction_type=mode)
    except DjangoAPIError as e:
        if e.status_code == 404:
            await message.reply(t('not_registered', lang))
        else:
            await message.reply(
                t('quick_expense_error', lang, code=e.status_code),
                parse_mode=None,
            )
        return

    # Форматируем сумму с разделителями тысяч
    fmt = f'{int(amount):,}'.replace(',', ' ')
    success_key = 'quick_income_success' if mode == 'income' else 'quick_expense_success'
    await message.reply(
        t(success_key, lang, amount=fmt, description=description),
        parse_mode='HTML',
    )
