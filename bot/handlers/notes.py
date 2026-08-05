"""
Заметки-напоминания.

Создание — многошаговый флоу без FSM, состояние черновика живёт в Redis
(PendingNoteStore):
  1. /note <текст>                 — сохраняем текст, спрашиваем режим.
  2. note_mode:once|daily          — уточняем: разово или регулярно.
  3. note_once:1h / note_daily:now — готовый вариант, создаём сразу.
     note_once:custom / note_daily:custom — просим ввести дату/время
     текстом и ждём следующее сообщение (see AwaitingNoteInput).
  4. Свободный текст (если ждём дату/время) — парсим и создаём.
Во всех случаях бэкенд сам считает remind_at в часовом поясе пользователя
(бот его не знает).

Список: /notes — активные напоминания с кнопкой удаления на каждом.
"""
from __future__ import annotations

import re
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import BaseFilter, Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from api.client import DjangoAPIError, DjangoClient
from i18n import t
from keyboards.inline import note_daily_keyboard, note_mode_keyboard, note_once_keyboard
from services.pending_note import PendingNoteStore

router = Router(name='notes')

_DATETIME_RE = re.compile(r'^(\d{1,2})\.(\d{1,2})\.(\d{4})\s+(\d{1,2}):(\d{2})$')
_TIME_RE = re.compile(r'^(\d{1,2}):(\d{2})$')


class AwaitingNoteInput(BaseFilter):
    """True когда для этого пользователя ждём ручной ввод даты/времени — чтобы
    это сообщение не перехватил быстрый парсер расходов в handlers/expenses.py."""

    async def __call__(self, message: Message, pending_notes: PendingNoteStore) -> bool:
        if not message.text:
            return False
        draft = await pending_notes.get(message.from_user.id)
        return bool(draft and draft.get('await'))


def _repeat_label(repeat: str, lang: str) -> str:
    return t(f'repeat_{repeat}', lang) if repeat in ('once', 'daily', 'weekly') else repeat


def _fmt_when(iso_string: str) -> str:
    try:
        return datetime.fromisoformat(iso_string).strftime('%d.%m.%Y %H:%M')
    except (TypeError, ValueError):
        return iso_string


async def _reply(target: CallbackQuery | Message, text: str) -> None:
    try:
        if isinstance(target, CallbackQuery):
            await target.message.edit_text(text, parse_mode='HTML')
        else:
            await target.answer(text, parse_mode='HTML')
    except Exception:
        pass  # сообщение уже могло быть удалено/устарело — молча игнорируем


async def _create_and_confirm(
    target: CallbackQuery | Message,
    django: DjangoClient,
    telegram_id: int,
    lang: str,
    text: str,
    **create_kwargs,
) -> bool:
    """Creates the note and renders a confirmation. Returns whether it succeeded."""
    try:
        note = await django.create_note(telegram_id, text, **create_kwargs)
    except DjangoAPIError as e:
        msg = t('not_registered', lang) if e.status_code == 404 else t('note_create_error', lang, detail=e.detail)
        await _reply(target, msg)
        return False

    await _reply(
        target,
        t(
            'note_created', lang,
            text=note['text'],
            when=_fmt_when(note['remind_at']),
            repeat=_repeat_label(note['repeat'], lang),
        ),
    )
    return True


@router.message(Command('note'))
async def cmd_note_create(message: Message, pending_notes: PendingNoteStore, lang: str):
    args = message.text.split(maxsplit=1)
    text = args[1].strip() if len(args) > 1 else ''
    if not text:
        await message.reply(t('note_usage', lang), parse_mode='HTML')
        return

    await pending_notes.set(message.from_user.id, text)
    await message.reply(
        t('note_pick_mode', lang, text=text),
        parse_mode='HTML',
        reply_markup=note_mode_keyboard(lang),
    )


@router.callback_query(F.data == 'note_mode:once')
async def on_mode_once(call: CallbackQuery, pending_notes: PendingNoteStore, lang: str):
    draft = await pending_notes.get(call.from_user.id)
    if not draft:
        await call.answer(t('note_expired', lang), show_alert=True)
        return
    await call.message.edit_text(
        t('note_pick_once', lang, text=draft['text']),
        parse_mode='HTML',
        reply_markup=note_once_keyboard(lang),
    )
    await call.answer()


@router.callback_query(F.data == 'note_mode:daily')
async def on_mode_daily(call: CallbackQuery, pending_notes: PendingNoteStore, lang: str):
    draft = await pending_notes.get(call.from_user.id)
    if not draft:
        await call.answer(t('note_expired', lang), show_alert=True)
        return
    await call.message.edit_text(
        t('note_pick_daily', lang, text=draft['text']),
        parse_mode='HTML',
        reply_markup=note_daily_keyboard(lang),
    )
    await call.answer()


@router.callback_query(F.data == 'note_once:1h')
async def on_once_1h(call: CallbackQuery, django: DjangoClient, pending_notes: PendingNoteStore, lang: str):
    draft = await pending_notes.pop(call.from_user.id)
    if not draft:
        await call.answer(t('note_expired', lang), show_alert=True)
        return
    await call.answer()
    await _create_and_confirm(call, django, call.from_user.id, lang, draft['text'], preset='once_1h')


@router.callback_query(F.data == 'note_daily:now')
async def on_daily_now(call: CallbackQuery, django: DjangoClient, pending_notes: PendingNoteStore, lang: str):
    draft = await pending_notes.pop(call.from_user.id)
    if not draft:
        await call.answer(t('note_expired', lang), show_alert=True)
        return
    await call.answer()
    await _create_and_confirm(call, django, call.from_user.id, lang, draft['text'], preset='daily_now')


@router.callback_query(F.data == 'note_once:custom')
async def on_once_custom(call: CallbackQuery, pending_notes: PendingNoteStore, lang: str):
    if not await pending_notes.set_awaiting(call.from_user.id, 'once_custom'):
        await call.answer(t('note_expired', lang), show_alert=True)
        return
    await call.message.edit_text(t('note_ask_datetime', lang), parse_mode='HTML')
    await call.answer()


@router.callback_query(F.data == 'note_daily:custom')
async def on_daily_custom(call: CallbackQuery, pending_notes: PendingNoteStore, lang: str):
    if not await pending_notes.set_awaiting(call.from_user.id, 'daily_custom'):
        await call.answer(t('note_expired', lang), show_alert=True)
        return
    await call.message.edit_text(t('note_ask_time', lang), parse_mode='HTML')
    await call.answer()


@router.message(AwaitingNoteInput())
async def on_custom_input(message: Message, django: DjangoClient, pending_notes: PendingNoteStore, lang: str):
    telegram_id = message.from_user.id
    draft = await pending_notes.get(telegram_id)
    kind = draft['await']
    raw = message.text.strip()

    if kind == 'once_custom':
        m = _DATETIME_RE.match(raw)
        if not m:
            await message.reply(t('note_bad_datetime', lang), parse_mode='HTML')
            return
        day, month, year, hour, minute = (int(g) for g in m.groups())
        try:
            dt = datetime(year, month, day, hour, minute)
        except ValueError:
            await message.reply(t('note_bad_datetime', lang), parse_mode='HTML')
            return
        # Черновик не трогаем до подтверждения бэкендом — если он откажет
        # (например дата уже в прошлом), просто попросим ввести ещё раз,
        # не заставляя проходить /note → выбор режима заново.
        ok = await _create_and_confirm(
            message, django, telegram_id, lang, draft['text'],
            remind_at=dt.isoformat(), repeat='once',
        )
        if ok:
            await pending_notes.pop(telegram_id)
        else:
            await message.answer(t('note_ask_datetime', lang), parse_mode='HTML')

    elif kind == 'daily_custom':
        m = _TIME_RE.match(raw)
        if not m or not (0 <= int(m.group(1)) <= 23 and 0 <= int(m.group(2)) <= 59):
            await message.reply(t('note_bad_time', lang), parse_mode='HTML')
            return
        ok = await _create_and_confirm(
            message, django, telegram_id, lang, draft['text'],
            time=raw, repeat='daily',
        )
        if ok:
            await pending_notes.pop(telegram_id)
        else:
            await message.answer(t('note_ask_time', lang), parse_mode='HTML')


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
