"""
Sends ERROR+ log records (unhandled exceptions in views, etc.) to a
Telegram channel via the Bot API — reuses TELEGRAM_BOT_TOKEN, already
configured for initData validation, no separate bot needed on this side.
"""
import logging
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

# Separate, plain logger (no handlers of our own) so failures to reach
# Telegram are still visible somewhere (console/docker logs) instead of
# vanishing silently — this is what made the missing-admin-rights issue
# invisible the first time around.
_fallback_logger = logging.getLogger('telegram_log_handler')


class TelegramErrorHandler(logging.Handler):
    def emit(self, record):
        token   = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        chat_id = getattr(settings, 'LOG_TELEGRAM_CHAT_ID', None)
        if not token or not chat_id:
            return

        try:
            header = f'🚨 {record.levelname} in {record.name}'
            request = getattr(record, 'request', None)
            if request is not None:
                header += f'\n{request.method} {request.path}'

            text = f'{header}\n\n{self.format(record)}'
            # Telegram's message length cap is 4096 chars.
            if len(text) > 3900:
                text = text[:3900] + '\n… (truncated)'

            url = f'https://api.telegram.org/bot{token}/sendMessage'
            data = urllib.parse.urlencode({'chat_id': chat_id, 'text': text}).encode()
            urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=5)
        except urllib.error.HTTPError as e:
            # Never let logging crash the request it's reporting on — but do
            # surface *why* delivery failed (e.g. 403 = bot isn't a channel
            # admin) to the console, since this handler is otherwise a black box.
            _fallback_logger.warning('Failed to deliver log to Telegram: %s %s', e.code, e.read())
        except Exception as e:
            _fallback_logger.warning('Failed to deliver log to Telegram: %s', e)
