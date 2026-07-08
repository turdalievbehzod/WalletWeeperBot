import json
import urllib.request
from decimal import Decimal

from django.core.cache import cache
from django.db import transaction
from django.db.models import ExpressionWrapper, F
from django.db.models.fields import DecimalField
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from core.authentication import validate_telegram_init_data
from .models import UserProfile
from .serializers import UserProfileSerializer, UserProfileUpdateSerializer


def _get_fx_rates() -> dict:
    rates = cache.get('fx_rates_usd')
    if not rates:
        try:
            url = 'https://api.exchangerate-api.com/v4/latest/USD'
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.loads(resp.read())
            rates = {k: data['rates'][k] for k in ['USD', 'UZS', 'EUR', 'RUB'] if k in data['rates']}
            cache.set('fx_rates_usd', rates, 3600)
        except Exception:
            rates = {'USD': 1.0, 'UZS': 12870.0, 'EUR': 0.93, 'RUB': 88.5}
    return rates

# Default categories created for every new user on first login.
_DEFAULT_CATEGORIES = [
    {'name': 'Продукты',      'icon': '🛒'},
    {'name': 'Транспорт',     'icon': '🚌'},
    {'name': 'Развлечения',   'icon': '🎮'},
    {'name': 'Рестораны',     'icon': '🍕'},
    {'name': 'Здоровье',      'icon': '💊'},
    {'name': 'Одежда',        'icon': '👗'},
    {'name': 'Коммунальные',  'icon': '🏠'},
]


class TelegramAuthView(APIView):
    """
    POST /api/v1/auth/
    Body: { "initData": "<telegram initData string>", "timezone": "Asia/Tashkent" }

    Validates Telegram initData, creates the user on first login (with default
    categories), and returns a JWT access + refresh token pair.
    """
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        init_data = request.data.get('initData')
        if not init_data:
            return Response(
                {'detail': 'initData is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Raises AuthenticationFailed (→ 401) on invalid/expired initData.
        tg_user = validate_telegram_init_data(init_data)

        timezone = request.data.get('timezone', 'UTC')

        user, is_new = UserProfile.objects.get_or_create(
            telegram_id=tg_user['id'],
            defaults={
                'username':   tg_user.get('username'),
                'first_name': tg_user.get('first_name', ''),
                'last_name':  tg_user.get('last_name', ''),
                'timezone':   timezone,
            },
        )

        if is_new:
            # Deferred import avoids a circular dependency at module load time.
            from apps.expenses.models import Category
            Category.objects.bulk_create([
                Category(user=user, name=c['name'], icon=c['icon'], is_system=False)
                for c in _DEFAULT_CATEGORIES
            ])

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'access':  str(refresh.access_token),
                'refresh': str(refresh),
                'user':    UserProfileSerializer(user).data,
                'is_new':  is_new,
            },
            status=status.HTTP_200_OK,
        )


class ExchangeRatesView(APIView):
    """GET /api/v1/exchange-rates/ — current rates relative to USD, cached 1 h."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'rates': _get_fx_rates(), 'base': 'USD'})


class UserProfileView(APIView):
    """
    GET  /api/v1/auth/me/  → returns current user profile
    PATCH /api/v1/auth/me/ → updates currency and/or timezone
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)

    def patch(self, request):
        old_currency = request.user.currency
        serializer = UserProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        new_currency = serializer.validated_data.get('currency', old_currency)

        if new_currency != old_currency:
            rates = _get_fx_rates()
            if old_currency in rates and new_currency in rates:
                multiplier = Decimal(str(rates[new_currency] / rates[old_currency]))
                from apps.expenses.models import Transaction
                Transaction.objects.filter(user=request.user).update(
                    amount=ExpressionWrapper(
                        F('amount') * multiplier,
                        output_field=DecimalField(max_digits=14, decimal_places=2),
                    )
                )

        serializer.save()
        return Response(UserProfileSerializer(request.user).data)
