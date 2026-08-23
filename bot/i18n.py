"""
Flat EN/RU string catalog for the bot — same flavor as the _LABELS /
_SETTINGS_TEXT constants that used to live inline in handlers/settings.py.
"""

STRINGS: dict[str, dict[str, str]] = {
    'welcome': {
        'ru': (
            'Привет, {name}! 👋\n\n'
            '📱 <b>Мои расходы</b> — твой личный трекер трат.\n\n'
            'Нажми кнопку ниже, чтобы открыть приложение, '
            'или просто напиши мне сумму и описание, например:\n'
            '<code>25000 обед</code>\n'
            '<code>3500 такси</code>\n\n'
            '⚙️ Команды:\n'
            '/settings — настройка уведомлений и языка\n'
            '/switch — переключить быстрый ввод между расходом и доходом\n'
            '/note — создать напоминание\n'
            '/notes — список напоминаний'
        ),
        'en': (
            'Hi, {name}! 👋\n\n'
            '📱 <b>My Expenses</b> — your personal spending tracker.\n\n'
            'Tap the button below to open the app, '
            'or just send me an amount and a description, e.g.:\n'
            '<code>25000 lunch</code>\n'
            '<code>3500 taxi</code>\n\n'
            '⚙️ Commands:\n'
            '/settings — notification and language settings\n'
            '/switch — toggle quick text entry between expense and income\n'
            '/note — create a reminder\n'
            '/notes — list your reminders'
        ),
    },
    'open_app_button': {'ru': '📊 Открыть приложение', 'en': '📊 Open app'},

    'not_registered': {
        'ru': '⚠️ Вы ещё не зарегистрированы.\nОткройте приложение один раз, чтобы создать профиль.',
        'en': "⚠️ You're not registered yet.\nOpen the app once to create your profile.",
    },

    'quick_expense_invalid_amount': {
        'ru': '❌ Неверная сумма. Пример: <code>25000 обед</code>',
        'en': '❌ Invalid amount. Example: <code>25000 lunch</code>',
    },
    'quick_expense_error': {
        'ru': '❌ Ошибка при сохранении (код {code}).',
        'en': '❌ Error while saving (code {code}).',
    },
    'quick_expense_success': {
        'ru': '✅ Расход <b>{amount} сум</b> на «{description}» успешно добавлен!',
        'en': '✅ Expense of <b>{amount}</b> for "{description}" added successfully!',
    },
    'quick_income_success': {
        'ru': '✅ Доход <b>{amount} сум</b> на «{description}» успешно добавлен!',
        'en': '✅ Income of <b>{amount}</b> for "{description}" added successfully!',
    },

    'switch_pick': {
        'ru': '🔀 Куда записывать быстрый ввод суммы?',
        'en': '🔀 Where should quick amount entries go?',
    },
    'switch_expense': {'ru': '💸 Расходы', 'en': '💸 Expenses'},
    'switch_income':  {'ru': '💰 Доходы', 'en': '💰 Income'},
    'switch_saved': {'ru': '✅ Режим сохранён: {label}', 'en': '✅ Mode saved: {label}'},

    'settings_text': {
        'ru': '⚙️ <b>Настройки</b>\n\nВыбери, как часто напоминать о ведении учёта, и язык бота:',
        'en': "⚙️ <b>Settings</b>\n\nChoose how often you'd like reminders, and the bot's language:",
    },
    'notify_daily':  {'ru': '🟢 Каждый вечер', 'en': '🟢 Every evening'},
    'notify_weekly': {'ru': '🔵 Раз в неделю (в воскресенье утром)', 'en': '🔵 Once a week (Sunday morning)'},
    'notify_off':    {'ru': '🔴 Уведомления отключены', 'en': '🔴 Notifications off'},
    'notify_saved':  {'ru': '✅ Настройки сохранены!\n{label}', 'en': '✅ Settings saved!\n{label}'},
    'notify_error':  {'ru': 'Ошибка (код {code}). Попробуйте позже.', 'en': 'Error (code {code}). Please try again later.'},

    'language_ru': {'ru': '🇷🇺 Русский', 'en': '🇷🇺 Russian'},
    'language_en': {'ru': '🇬🇧 English', 'en': '🇬🇧 English'},
    'language_saved': {'ru': '✅ Язык переключён на русский', 'en': '✅ Language switched to English'},
    'language_error': {'ru': 'Ошибка (код {code}). Попробуйте позже.', 'en': 'Error (code {code}). Please try again later.'},

    'note_usage': {
        'ru': '📝 Формат: <code>/note текст</code>\nНапример: <code>/note Забрать посылку</code>',
        'en': '📝 Format: <code>/note text</code>\nExample: <code>/note Pick up the package</code>',
    },
    'note_pick_mode': {
        'ru': '🕐 Как напомнить?\n«{text}»',
        'en': '🕐 How should I remind you?\n"{text}"',
    },
    'note_mode_once':  {'ru': '1️⃣ Одноразово', 'en': '1️⃣ One time'},
    'note_mode_daily': {'ru': '🔁 Регулярно', 'en': '🔁 Recurring'},

    'note_pick_once': {
        'ru': '⏰ Когда напомнить один раз?\n«{text}»',
        'en': '⏰ When should I remind you once?\n"{text}"',
    },
    'note_once_1h':     {'ru': '⏰ Через час', 'en': '⏰ In an hour'},
    'note_once_custom': {'ru': '📅 Указать время', 'en': '📅 Pick a time'},

    'note_pick_daily': {
        'ru': '🔁 Когда напоминать каждый день?\n«{text}»',
        'en': '🔁 When should I remind you every day?\n"{text}"',
    },
    'note_daily_now':    {'ru': '🔁 Каждый день в это время', 'en': '🔁 Every day at this time'},
    'note_daily_custom': {'ru': '📅 Указать время', 'en': '📅 Pick a time'},

    'note_ask_datetime': {
        'ru': '📅 Введи дату и время в формате <code>дд.мм.гггг чч:мм</code>\nНапример: <code>25.12.2026 14:30</code>',
        'en': '📅 Enter the date and time as <code>dd.mm.yyyy hh:mm</code>\nExample: <code>25.12.2026 14:30</code>',
    },
    'note_ask_time': {
        'ru': '📅 Введи время в формате <code>чч:мм</code>\nНапример: <code>09:00</code>',
        'en': '📅 Enter the time as <code>hh:mm</code>\nExample: <code>09:00</code>',
    },
    'note_bad_datetime': {
        'ru': '❌ Не удалось распознать дату и время. Формат: <code>дд.мм.гггг чч:мм</code>',
        'en': '❌ Could not parse that date/time. Format: <code>dd.mm.yyyy hh:mm</code>',
    },
    'note_bad_time': {
        'ru': '❌ Не удалось распознать время. Формат: <code>чч:мм</code>',
        'en': '❌ Could not parse that time. Format: <code>hh:mm</code>',
    },
    'note_expired': {
        'ru': '⌛ Черновик напоминания устарел, попробуй /note ещё раз.',
        'en': "⌛ This reminder draft expired, please try /note again.",
    },
    'note_create_error': {
        'ru': '❌ Не удалось создать напоминание: {detail}',
        'en': '❌ Failed to create the reminder: {detail}',
    },
    'note_created': {
        'ru': '✅ Напоминание создано ({repeat}, {when}):\n«{text}»',
        'en': '✅ Reminder created ({repeat}, {when}):\n"{text}"',
    },
    'note_list_error': {
        'ru': '❌ Не удалось получить список напоминаний: {detail}',
        'en': '❌ Failed to fetch reminders: {detail}',
    },
    'note_list_empty': {
        'ru': '📭 У тебя пока нет активных напоминаний. Создать: /note',
        'en': '📭 You have no active reminders yet. Create one: /note',
    },
    'note_list_item': {
        'ru': '🔔 {when} ({repeat})\n«{text}»',
        'en': '🔔 {when} ({repeat})\n"{text}"',
    },
    'note_delete_button': {'ru': '🗑 Удалить', 'en': '🗑 Delete'},
    'note_deleted': {'ru': '✅ Напоминание удалено', 'en': '✅ Reminder deleted'},
    'note_delete_error': {
        'ru': '❌ Не удалось удалить: {detail}',
        'en': '❌ Failed to delete: {detail}',
    },
    'note_reminder': {
        'ru': '🔔 <b>Напоминание:</b> {text}',
        'en': '🔔 <b>Reminder:</b> {text}',
    },

    'repeat_once':   {'ru': 'разово', 'en': 'once'},
    'repeat_daily':  {'ru': 'ежедневно', 'en': 'daily'},
    'repeat_weekly': {'ru': 'еженедельно', 'en': 'weekly'},

    'broadcast_usage': {
        'ru': '📢 Формат: <code>/broadcast текст</code>\nНапример: <code>/broadcast Добавили новую функцию!</code>',
        'en': '📢 Format: <code>/broadcast text</code>\nExample: <code>/broadcast We shipped a new feature!</code>',
    },
    'broadcast_preview': {
        'ru': '📢 <b>Предпросмотр рассылки</b>\n\n{text}\n\nОтправить всем зарегистрированным пользователям?',
        'en': '📢 <b>Broadcast preview</b>\n\n{text}\n\nSend this to all registered users?',
    },
    'broadcast_send_button':   {'ru': '✅ Отправить', 'en': '✅ Send'},
    'broadcast_cancel_button': {'ru': '❌ Отмена', 'en': '❌ Cancel'},
    'broadcast_expired': {
        'ru': '⌛ Черновик рассылки устарел, начни заново: /broadcast',
        'en': '⌛ This broadcast draft expired, start again with /broadcast',
    },
    'broadcast_error': {
        'ru': '❌ Не удалось получить список пользователей: {detail}',
        'en': '❌ Failed to fetch the recipient list: {detail}',
    },
    'broadcast_done': {
        'ru': '✅ Рассылка завершена: отправлено {sent}, ошибок {failed}',
        'en': '✅ Broadcast finished: sent {sent}, failed {failed}',
    },
    'broadcast_cancelled': {'ru': '❌ Рассылка отменена', 'en': '❌ Broadcast cancelled'},

    'digest_reminder': {
        'ru': (
            '👋 Не забудь заглянуть и записать сегодняшние траты!\n'
            'Открой приложение или просто напиши мне сумму и описание, например: <code>25000 обед</code>'
        ),
        'en': (
            "👋 Don't forget to log today's spending!\n"
            'Open the app or just send me an amount and description, e.g.: <code>25000 lunch</code>'
        ),
    },
}


def t(key: str, lang: str, **kwargs) -> str:
    entry = STRINGS[key]
    text = entry.get(lang, entry['ru'])
    return text.format(**kwargs) if kwargs else text
