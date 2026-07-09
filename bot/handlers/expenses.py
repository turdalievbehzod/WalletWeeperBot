"""
Быстрый текстовый ввод расходов.

Форматы, которые распознаёт бот:
  25000 обед
  3 500 такси          (пробел внутри числа игнорируется)
  12000.50 кофе
"""
import re

from aiogram import F, Router
from aiogram.types import Message

from api.client import DjangoAPIError, DjangoClient
from i18n import t

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


@router.message(F.text.regexp(_PATTERN))
async def handle_quick_expense(message: Message, django: DjangoClient, lang: str):
    match = _PATTERN.match(message.text.strip())
    if not match:
        return

    raw_amount, description = match.group(1), match.group(2).strip()
    amount = _parse_amount(raw_amount)
    if amount is None:
        await message.reply(t('quick_expense_invalid_amount', lang), parse_mode='HTML')
        return

    telegram_id = message.from_user.id

    try:
        await django.create_expense(telegram_id, amount, description)
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
    await message.reply(
        t('quick_expense_success', lang, amount=fmt, description=description),
        parse_mode='HTML',
    )
