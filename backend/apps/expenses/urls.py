from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BotBroadcastTargetsView,
    BotDueNotesView,
    BotExpenseView,
    BotLanguageView,
    BotNoteCreateView,
    BotNoteDeleteView,
    BotNoteListView,
    BotNoteMarkSentView,
    BotNotificationView,
    BudgetSimulatorView,
    CalendarView,
    CategoryViewSet,
    DashboardView,
    HistoryMainView,
    MonthDetailsView,
    QuickTemplateViewSet,
    SummaryView,
    TransactionViewSet,
    WeekDetailsView,
)

router = DefaultRouter()
router.register('expenses',   TransactionViewSet,   basename='expense')
router.register('categories', CategoryViewSet,      basename='category')
router.register('templates',  QuickTemplateViewSet, basename='template')

urlpatterns = [
    # Bot-only endpoints must come BEFORE the router so that
    # 'expenses/bot-notify/' is not swallowed by the router's expenses/<pk>/ pattern.
    path('expenses/bot-create/',            BotExpenseView.as_view(),            name='bot-expense'),
    path('expenses/bot-notify/',            BotNotificationView.as_view(),       name='bot-notify'),
    path('expenses/bot-language/',          BotLanguageView.as_view(),           name='bot-language'),
    path('expenses/bot-broadcast-targets/', BotBroadcastTargetsView.as_view(),   name='bot-broadcast-targets'),
    # Note: 'bot/notes/...' (not 'notes/bot-...') on purpose — apps.users.urls
    # registers NoteViewSet at 'notes/<pk>/' and is included before this urls.py
    # in core/urls.py, so anything under 'notes/' here would be swallowed by
    # that detail route (pk='bot-create' etc.) before ever reaching this file.
    path('bot/notes/',                    BotNoteCreateView.as_view(),   name='bot-note-create'),
    path('bot/notes/list/',               BotNoteListView.as_view(),     name='bot-note-list'),
    path('bot/notes/due/',                BotDueNotesView.as_view(),     name='bot-due-notes'),
    path('bot/notes/<int:note_id>/',      BotNoteDeleteView.as_view(),   name='bot-note-delete'),
    path('bot/notes/<int:note_id>/sent/', BotNoteMarkSentView.as_view(), name='bot-note-mark-sent'),
    # Standard CRUD router
    path('', include(router.urls)),
    path('dashboard/',             DashboardView.as_view(),       name='dashboard'),
    path('calendar/',              CalendarView.as_view(),        name='calendar'),
    path('simulator/',             BudgetSimulatorView.as_view(), name='simulator'),
    path('summary/',               SummaryView.as_view(),         name='summary'),
    path('history/main/',          HistoryMainView.as_view(),     name='history-main'),
    path('history/week-details/',  WeekDetailsView.as_view(),     name='week-details'),
    path('history/month-details/', MonthDetailsView.as_view(),    name='month-details'),
]
