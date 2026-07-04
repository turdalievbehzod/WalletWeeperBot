from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.inline import open_app_keyboard

router = Router(name='start')


@router.message(CommandStart())
async def cmd_start(message: Message, mini_app_url: str):
    first = message.from_user.first_name or 'друг'
    await message.answer(
        f'Привет, {first}! 👋\n\n'
        '📱 <b>Мои расходы</b> — твой личный трекер трат.\n\n'
        'Нажми кнопку ниже, чтобы открыть приложение, '
        'или просто напиши мне сумму и описание, например:\n'
        '<code>25000 обед</code>\n'
        '<code>3500 такси</code>\n\n'
        '⚙️ Команды:\n'
        '/settings — настройка уведомлений',
        parse_mode='HTML',
        reply_markup=open_app_keyboard(mini_app_url),
    )
