import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    bot_token:        str
    django_api_url:   str
    bot_secret:       str
    mini_app_url:     str
    redis_url:        str
    internal_secret:  str
    broadcast_port:   int


def load_config() -> Config:
    def _require(key: str) -> str:
        val = os.getenv(key)
        if not val:
            raise EnvironmentError(f'Missing required env var: {key}')
        return val

    return Config(
        bot_token       = _require('BOT_TOKEN'),
        django_api_url  = os.getenv('DJANGO_API_URL', 'http://localhost:8000').rstrip('/'),
        bot_secret      = _require('BOT_SECRET'),
        mini_app_url    = _require('MINI_APP_URL'),
        redis_url       = os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
        internal_secret = os.getenv('INTERNAL_SECRET', 'change-me'),
        broadcast_port  = int(os.getenv('BROADCAST_PORT', '8001')),
    )
