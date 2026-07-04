from datetime import datetime, timedelta
from decimal import Decimal

import pytz
from dateutil.relativedelta import relativedelta
from django.conf import settings as django_settings
from django.db.models import Q, Sum
from django.db.models.functions import TruncDay
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import UserProfile
from .models import Category, QuickTemplate, Transaction
from .serializers import (
    CategorySerializer,
    QuickTemplateSerializer,
    TransactionSerializer,
)


def _bot_auth(request):
    """
    Validates the bot-to-backend internal request.
    Returns (UserProfile, None) on success or (None, Response) on failure.
    """
    secret = request.headers.get('X-Bot-Secret', '')
    if secret != getattr(django_settings, 'BOT_SECRET', ''):
        return None, Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

    raw_id = request.headers.get('X-Telegram-Id', '')
    try:
        user = UserProfile.objects.get(telegram_id=int(raw_id))
    except (UserProfile.DoesNotExist, ValueError, TypeError):
        return None, Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    return user, None

_DAYS_RU = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']


def _tx_to_dict(t: Transaction) -> dict:
    name = t.description or (t.category.name if t.category else '—')
    return {
        'id': t.id,
        'description': name,
        'amount': float(t.amount),
        'category_name': t.category.name if t.category else None,
        'category_icon': t.category.icon if t.category else None,
        'created_at': t.created_at.isoformat(),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────────────────────────────────────

def _user_tz(user) -> pytz.BaseTzInfo:
    """Returns the user's pytz timezone, falling back to UTC on bad input."""
    try:
        return pytz.timezone(user.timezone)
    except pytz.UnknownTimeZoneError:
        return pytz.UTC


# ──────────────────────────────────────────────────────────────────────────────
# CRUD ViewSets
# ──────────────────────────────────────────────────────────────────────────────

class TransactionViewSet(viewsets.ModelViewSet):
    """
    Standard CRUD for the authenticated user's transactions.
    GET /api/v1/expenses/          — paginated list, newest first
    POST /api/v1/expenses/         — create
    GET /api/v1/expenses/<id>/     — retrieve
    PATCH /api/v1/expenses/<id>/   — partial update
    DELETE /api/v1/expenses/<id>/  — delete
    """
    serializer_class   = TransactionSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields    = ['created_at', 'amount']
    search_fields      = ['description']

    def get_queryset(self):
        return (
            Transaction.objects
            .filter(user=self.request.user)
            .select_related('category')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Returns the user's own categories plus all system categories.
    System categories cannot be modified or deleted.
    """
    serializer_class   = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(
            Q(user=self.request.user) | Q(user__isnull=True, is_system=True)
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_system=False)

    def perform_update(self, serializer):
        if serializer.instance.is_system:
            raise PermissionDenied('System categories cannot be modified.')
        if serializer.instance.user != self.request.user:
            raise PermissionDenied('You can only edit your own categories.')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.is_system:
            raise PermissionDenied('System categories cannot be deleted.')
        if instance.user != self.request.user:
            raise PermissionDenied('You can only delete your own categories.')
        instance.delete()


class QuickTemplateViewSet(viewsets.ModelViewSet):
    """CRUD for quick-tap expense templates."""
    serializer_class   = QuickTemplateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            QuickTemplate.objects
            .filter(user=self.request.user)
            .select_related('category')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ──────────────────────────────────────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────────────────────────────────────

class DashboardView(APIView):
    """
    GET /api/v1/dashboard/

    Returns spending totals for today / this week / this month / this year,
    all computed in the user's local timezone.

    Key technique: we construct timezone-aware datetime objects in the user's
    local TZ, then pass them directly to ORM filters. Because USE_TZ=True,
    Django converts them to UTC for the SQL WHERE clause automatically — so
    "today" means 00:00–23:59 in Asia/Tashkent, not in UTC.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user     = request.user
        user_tz  = _user_tz(user)
        now_local = datetime.now(user_tz)

        # Truncate to midnight in the user's local timezone.
        today_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start  = today_start - timedelta(days=today_start.weekday())  # Monday
        month_start = today_start.replace(day=1)
        year_start  = today_start.replace(month=1, day=1)
        # Exclusive upper bound — "up to but not including tomorrow 00:00 local"
        tomorrow    = today_start + timedelta(days=1)

        base_qs = Transaction.objects.filter(user=user)

        def _sum(start, end) -> Decimal:
            return (
                base_qs
                .filter(created_at__gte=start, created_at__lt=end)
                .aggregate(total=Sum('amount'))['total']
                or Decimal('0')
            )

        return Response({
            'today':    float(_sum(today_start, tomorrow)),
            'week':     float(_sum(week_start,  tomorrow)),
            'month':    float(_sum(month_start, tomorrow)),
            'year':     float(_sum(year_start,  tomorrow)),
            'currency': user.currency,
            'timezone': user.timezone,
        })


# ──────────────────────────────────────────────────────────────────────────────
# Calendar aggregator
# ──────────────────────────────────────────────────────────────────────────────

class CalendarView(APIView):
    """
    GET /api/v1/calendar/?month=YYYY-MM

    Returns a flat dict of {date_string: total_amount} for every day that has
    at least one transaction in the requested month.

    Example response:
        {"2026-07-01": 15000.0, "2026-07-14": 42500.0}

    The frontend uses this to paint the calendar grid without loading every
    individual transaction — O(days) payload instead of O(transactions).

    Key technique: TruncDay(..., tzinfo=user_tz) tells the database to group
    UTC timestamps by local calendar day, so a 23:30 UTC transaction that is
    actually 04:30 the next morning in Asia/Tashkent lands on the correct day.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month_str = request.query_params.get('month', '')
        try:
            year, month = map(int, month_str.split('-'))
            datetime(year, month, 1)          # raises ValueError on invalid date
        except (ValueError, AttributeError):
            return Response(
                {'detail': 'month parameter is required in YYYY-MM format.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user    = request.user
        user_tz = _user_tz(user)

        # Aware datetimes at the boundary of the requested month in the user's TZ.
        start = user_tz.localize(datetime(year, month, 1))
        end   = start + relativedelta(months=1)

        rows = (
            Transaction.objects
            .filter(user=user, created_at__gte=start, created_at__lt=end)
            # TruncDay with tzinfo converts the stored UTC value to local time
            # before truncating, ensuring correct calendar-day grouping.
            .annotate(day=TruncDay('created_at', tzinfo=user_tz))
            .values('day')
            .annotate(total=Sum('amount'))
            .order_by('day')
        )

        result = {
            row['day'].strftime('%Y-%m-%d'): float(row['total'])
            for row in rows
        }
        return Response(result)


# ──────────────────────────────────────────────────────────────────────────────
# Budget simulator
# ──────────────────────────────────────────────────────────────────────────────

class BudgetSimulatorView(APIView):
    """
    POST /api/v1/simulator/
    Body: { "item_name": "AirPods", "price": 15000 }

    Answers two questions about a hypothetical purchase:
      1. What percentage of this month's total would it add?
      2. How many days of average daily spending does it represent?
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_name = request.data.get('item_name', 'Unknown item')
        price_raw = request.data.get('price')

        if price_raw is None:
            return Response(
                {'detail': 'price is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            price = Decimal(str(price_raw))
            if price <= 0:
                raise ValueError
        except (Exception,):
            return Response(
                {'detail': 'price must be a positive number.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user    = request.user
        user_tz = _user_tz(user)
        now_local = datetime.now(user_tz)

        month_start = user_tz.localize(datetime(now_local.year, now_local.month, 1))
        month_end   = month_start + relativedelta(months=1)

        month_total: Decimal = (
            Transaction.objects
            .filter(user=user, created_at__gte=month_start, created_at__lt=month_end)
            .aggregate(total=Sum('amount'))['total']
            or Decimal('0')
        )

        # Days elapsed so far this month (minimum 1 to avoid division by zero).
        days_elapsed = max((now_local - month_start).days + 1, 1)
        daily_avg    = month_total / days_elapsed

        # Percentage: how much this item adds relative to the new monthly total.
        new_total = month_total + price
        pct_of_month = float(price / new_total * 100) if new_total else 0.0

        # Days needed to "save" the item at the current daily spending rate.
        days_to_save = float(price / daily_avg) if daily_avg > 0 else None

        return Response({
            'item_name':       item_name,
            'price':           float(price),
            'month_total':     float(month_total),
            'daily_avg':       round(float(daily_avg), 2),
            'percentage_of_month': round(pct_of_month, 2),
            'days_to_save':    round(days_to_save, 1) if days_to_save is not None else None,
            'currency':        user.currency,
        })


# ──────────────────────────────────────────────────────────────────────────────
# Carousel summary  (/api/v1/summary/)
# ──────────────────────────────────────────────────────────────────────────────

class SummaryView(APIView):
    """
    GET /api/v1/summary/
    Returns this_week / this_month / this_year totals for the expense carousel.
    All ranges start from Monday (week) or 1st (month/year) and end at "now".
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_tz = _user_tz(user)
        now_local = datetime.now(user_tz)
        today_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today_start + timedelta(days=1)

        week_start  = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)
        year_start  = today_start.replace(month=1, day=1)

        base_qs = Transaction.objects.filter(user=user)

        def _s(start, end):
            return float(
                base_qs.filter(created_at__gte=start, created_at__lt=end)
                .aggregate(t=Sum('amount'))['t'] or 0
            )

        return Response({
            'this_week':  _s(week_start, tomorrow),
            'this_month': _s(month_start, tomorrow),
            'this_year':  _s(year_start, tomorrow),
            'currency':   user.currency,
        })


# ──────────────────────────────────────────────────────────────────────────────
# Main history (/api/v1/history/main/)
# ──────────────────────────────────────────────────────────────────────────────

class HistoryMainView(APIView):
    """
    GET /api/v1/history/main/
    Returns three blocks for the home screen history feed:
      • today      — transactions since local midnight
      • last_week  — previous full calendar week (Mon–Sun)
      • last_month — previous full calendar month
    Each block: { total_sum, transactions[] }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_tz = _user_tz(user)
        now_local = datetime.now(user_tz)
        today_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today_start + timedelta(days=1)

        current_week_start = today_start - timedelta(days=today_start.weekday())
        last_week_start    = current_week_start - timedelta(weeks=1)

        this_month_start  = today_start.replace(day=1)
        last_month_start  = this_month_start - relativedelta(months=1)

        base_qs = Transaction.objects.filter(user=user).select_related('category')

        def _block(start, end):
            items = [_tx_to_dict(t) for t in base_qs.filter(created_at__gte=start, created_at__lt=end)]
            return {'total_sum': sum(i['amount'] for i in items), 'transactions': items}

        return Response({
            'today':      _block(today_start, tomorrow),
            'last_week':  _block(last_week_start, current_week_start),
            'last_month': _block(last_month_start, this_month_start),
        })


# ──────────────────────────────────────────────────────────────────────────────
# Week detail  (/api/v1/history/week-details/)
# ──────────────────────────────────────────────────────────────────────────────

class WeekDetailsView(APIView):
    """
    GET /api/v1/history/week-details/
    Breaks down last week's spending by calendar day.
    Response: [{day_name, date, total_sum, transactions[]}, ...]  ordered Mon→Sun.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_tz = _user_tz(user)
        now_local = datetime.now(user_tz)
        today_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)

        current_week_start = today_start - timedelta(days=today_start.weekday())
        last_week_start    = current_week_start - timedelta(weeks=1)

        rows = (
            Transaction.objects
            .filter(user=user, created_at__gte=last_week_start, created_at__lt=current_week_start)
            .select_related('category')
            .annotate(day=TruncDay('created_at', tzinfo=user_tz))
            .order_by('day', '-created_at')
        )

        grouped: dict = {}
        for t in rows:
            key = t.day.strftime('%Y-%m-%d')
            if key not in grouped:
                grouped[key] = {
                    'day_name': _DAYS_RU[t.day.weekday()],
                    'date': key,
                    'total_sum': 0,
                    'transactions': [],
                }
            grouped[key]['total_sum'] += float(t.amount)
            grouped[key]['transactions'].append(_tx_to_dict(t))

        return Response(sorted(grouped.values(), key=lambda x: x['date']))


# ──────────────────────────────────────────────────────────────────────────────
# Month detail  (/api/v1/history/month-details/)
# ──────────────────────────────────────────────────────────────────────────────

class MonthDetailsView(APIView):
    """
    GET /api/v1/history/month-details/
    Breaks down last month's spending by week-within-month.
    Week boundaries: days 1–7 = Неделя 1, 8–14 = Неделя 2, etc.
    Response: [{week_label, week_num, total_sum, transactions[]}, ...]
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_tz = _user_tz(user)
        now_local = datetime.now(user_tz)
        today_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)

        this_month_start = today_start.replace(day=1)
        last_month_start = this_month_start - relativedelta(months=1)

        rows = (
            Transaction.objects
            .filter(user=user, created_at__gte=last_month_start, created_at__lt=this_month_start)
            .select_related('category')
            .annotate(day=TruncDay('created_at', tzinfo=user_tz))
            .order_by('day', '-created_at')
        )

        grouped: dict = {}
        for t in rows:
            week_num = (t.day.day - 1) // 7 + 1
            if week_num not in grouped:
                grouped[week_num] = {
                    'week_label': f'Неделя {week_num}',
                    'week_num': week_num,
                    'total_sum': 0,
                    'transactions': [],
                }
            grouped[week_num]['total_sum'] += float(t.amount)
            grouped[week_num]['transactions'].append(_tx_to_dict(t))

        return Response(sorted(grouped.values(), key=lambda x: x['week_num']))


# ──────────────────────────────────────────────────────────────────────────────
# Bot-only endpoints (authenticated via X-Bot-Secret + X-Telegram-Id headers)
# ──────────────────────────────────────────────────────────────────────────────

class BotExpenseView(APIView):
    """
    POST /api/v1/expenses/bot-create/
    Headers: X-Bot-Secret, X-Telegram-Id
    Body:    { "amount": 25000, "description": "обед" }

    Creates a transaction for the identified user without JWT.
    Used by the Telegram bot quick-input feature.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        user, err = _bot_auth(request)
        if err:
            return err

        serializer = TransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tx = serializer.save(user=user)
        return Response({
            'id':          tx.id,
            'amount':      float(tx.amount),
            'description': tx.description or '',
            'created_at':  tx.created_at.isoformat(),
        }, status=status.HTTP_201_CREATED)


class BotNotificationView(APIView):
    """
    PATCH /api/v1/expenses/bot-notify/
    Headers: X-Bot-Secret, X-Telegram-Id
    Body:    { "notification_setting": "daily" | "weekly" | "off" }

    Updates the notification preference for the identified user.
    """
    permission_classes = [AllowAny]

    def patch(self, request):
        user, err = _bot_auth(request)
        if err:
            return err

        setting = request.data.get('notification_setting', '')
        allowed = {'off', 'daily', 'weekly'}
        if setting not in allowed:
            return Response(
                {'detail': f'Invalid setting. Use one of: {", ".join(sorted(allowed))}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.notification_setting = setting
        user.save(update_fields=['notification_setting'])
        return Response({'notification_setting': setting})


class BotBroadcastTargetsView(APIView):
    """
    GET /api/v1/expenses/bot-broadcast-targets/?mode=daily
    Header: X-Bot-Secret

    Returns the list of telegram_ids for users who have the given
    notification mode enabled. Called by Celery/APScheduler to know
    whom to notify before posting to the bot's broadcast endpoint.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        secret = request.headers.get('X-Bot-Secret', '')
        if secret != getattr(django_settings, 'BOT_SECRET', ''):
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        mode = request.query_params.get('mode', '')
        if mode not in ('daily', 'weekly'):
            return Response(
                {'detail': 'mode must be "daily" or "weekly".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ids = list(
            UserProfile.objects
            .filter(notification_setting=mode, is_active=True)
            .values_list('telegram_id', flat=True)
        )
        return Response({'telegram_ids': ids, 'count': len(ids)})
