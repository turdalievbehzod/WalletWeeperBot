"""
Заметки-напоминания.

Создание — двухшаговый флоу без FSM:
  1. /note <текст>              — бот сохраняет текст в Redis (PendingNoteStore)
                                   и показывает кнопки с готовым временем.
  2. Нажатие кнопки note_when:* — читает текст, шлёт (текст, пресет) на бэкенд;
                                   бэкенд сам считает remind_at в часовом поясе
                                   пользователя (бот его не знает) и создаёт
                                   напоминание.

Список: /notes — активные напоминания с кнопкой удаления на каждом.
"""
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from api.client import DjangoAPIError, DjangoClient
from i18n import t
from keyboards.inline import note_time_keyboard
from services.pending_note import PendingNoteStore

router = Router(name='notes')


def _repeat_label(repeat: str, lang: str) -> str:
    return t(f'repeat_{repeat}', lang) if repeat in ('once', 'daily', 'weekly') else repeat


def _fmt_when(iso_string: str) -> str:
    try:
        return datetime.fromisoformat(iso_string).strftime('%d.%m.%Y %H:%M')
    except (TypeError, ValueError):
        return iso_string


@router.message(Command('note'))
async def cmd_note_create(message: Message, pending_notes: PendingNoteStore, lang: str):
    args = message.text.split(maxsplit=1)
    text = args[1].strip() if len(args) > 1 else ''
    if not text:
        await message.reply(t('note_usage', lang), parse_mode='HTML')
        return

    await pending_notes.set(message.from_user.id, text)
    await message.reply(
        t('note_pick_time', lang, text=text),
        parse_mode='HTML',
        reply_markup=note_time_keyboard(lang),
    )


@router.callback_query(F.data.startswith('note_when:'))
async def on_note_time_picked(
    call: CallbackQuery,
    django: DjangoClient,
    pending_notes: PendingNoteStore,
    lang: str,
):
    preset = call.data.split(':', 1)[1]
    telegram_id = call.from_user.id

    text = await pending_notes.pop(telegram_id)
    if not text:
        await call.answer(t('note_expired', lang), show_alert=True)
        return

    try:
        note = await django.create_note(telegram_id, text, preset)
    except DjangoAPIError as e:
        if e.status_code == 404:
            await call.answer(t('not_registered', lang), show_alert=True)
        else:
            await call.answer(t('note_create_error', lang, detail=e.detail), show_alert=True)
        return

    await call.answer(t('note_saved', lang))
    try:
        await call.message.edit_text(
            t(
                'note_created', lang,
                text=note['text'],
                when=_fmt_when(note['remind_at']),
                repeat=_repeat_label(note['repeat'], lang),
            ),
            parse_mode='HTML',
        )
    except Exception:
        pass  # сообщение уже могло быть удалено/устарело — молча игнорируем


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
