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
            '/settings — настройка уведомлений и языка'
        ),
        'en': (
            'Hi, {name}! 👋\n\n'
            '📱 <b>My Expenses</b> — your personal spending tracker.\n\n'
            'Tap the button below to open the app, '
            'or just send me an amount and a description, e.g.:\n'
            '<code>25000 lunch</code>\n'
            '<code>3500 taxi</code>\n\n'
            '⚙️ Commands:\n'
            '/settings — notification and language settings'
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
}


def t(key: str, lang: str, **kwargs) -> str:
    entry = STRINGS[key]
    text = entry.get(lang, entry['ru'])
    return text.format(**kwargs) if kwargs else text
