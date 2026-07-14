"""
Заметки-напоминания.

Создание: /note once|daily|weekly ДД.ММ.ГГГГ ЧЧ:ММ текст
  Например: /note once 20.07.2026 18:00 Забрать посылку
            /note daily 15.07.2026 09:00 Проверить расходы

Список:   /notes — активные напоминания с кнопкой удаления на каждом.
"""
import re
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from api.client import DjangoAPIError, DjangoClient
from i18n import t

router = Router(name='notes')

_CREATE_PATTERN = re.compile(
    r'^(once|daily|weekly)\s+(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}):(\d{2})\s+(.+)$',
    re.IGNORECASE | re.DOTALL,
)


def _repeat_label(repeat: str, lang: str) -> str:
    return t(f'repeat_{repeat}', lang) if repeat in ('once', 'daily', 'weekly') else repeat


def _fmt_when(iso_string: str) -> str:
    try:
        return datetime.fromisoformat(iso_string).strftime('%d.%m.%Y %H:%M')
    except (TypeError, ValueError):
        return iso_string


@router.message(Command('note'))
async def cmd_note_create(message: Message, django: DjangoClient, lang: str):
    args = message.text.split(maxsplit=1)
    match = _CREATE_PATTERN.match(args[1].strip()) if len(args) > 1 else None
    if not match:
        await message.reply(t('note_usage', lang), parse_mode='HTML')
        return

    repeat, day, month, year, hour, minute, text = match.groups()
    repeat = repeat.lower()
    try:
        remind_at = datetime(int(year), int(month), int(day), int(hour), int(minute))
    except ValueError:
        await message.reply(t('note_invalid_date', lang))
        return

    try:
        await django.create_note(message.from_user.id, text.strip(), remind_at.isoformat(), repeat)
    except DjangoAPIError as e:
        if e.status_code == 404:
            await message.reply(t('not_registered', lang))
        else:
            await message.reply(t('note_create_error', lang, detail=e.detail))
        return

    await message.reply(
        t(
            'note_created', lang,
            text=text.strip(),
            when=remind_at.strftime('%d.%m.%Y %H:%M'),
            repeat=_repeat_label(repeat, lang),
        ),
        parse_mode='HTML',
    )


@router.message(Command('notes'))
async def cmd_note_list(message: Message, django: DjangoClient, lang: str):
    try:
        notes = await django.list_notes(message.from_user.id)
    except DjangoAPIError as e:
        if e.status_code == 404:
            await message.reply(t('not_registered', lang))
        else:
            await message.reply(t('note_list_error', lang, detail=e.detail))
        return

    if not notes:
        await message.answer(t('note_list_empty', lang))
        return

    for note in notes:
        builder = InlineKeyboardBuilder()
        builder.button(text=t('note_delete_button', lang), callback_data=f"note_del:{note['id']}")
        await message.answer(
            t(
                'note_list_item', lang,
                text=note['text'],
                when=_fmt_when(note['remind_at']),
                repeat=_repeat_label(note['repeat'], lang),
            ),
            reply_markup=builder.as_markup(),
        )


@router.callback_query(F.data.startswith('note_del:'))
async def on_note_delete(call: CallbackQuery, django: DjangoClient, lang: str):
    note_id = int(call.data.split(':', 1)[1])

    try:
        await django.delete_note(call.from_user.id, note_id)
    except DjangoAPIError as e:
        await call.answer(t('note_delete_error', lang, detail=e.detail), show_alert=True)
        return

    await call.answer(t('note_deleted', lang))
    try:
        await call.message.delete()
    except Exception:
        pass  # сообщение уже могло быть удалено — молча игнорируем
