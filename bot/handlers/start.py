from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from i18n import t
from keyboards.inline import open_app_keyboard

router = Router(name='start')


@router.message(CommandStart())
async def cmd_start(message: Message, mini_app_url: str, lang: str):
    first = message.from_user.first_name or ('friend' if lang == 'en' else 'друг')
    await message.answer(
        t('welcome', lang, name=first),
        parse_mode='HTML',
        reply_markup=open_app_keyboard(mini_app_url, lang),
    )
