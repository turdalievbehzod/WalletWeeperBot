from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
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
    path('', include(router.urls)),
    path('dashboard/',              DashboardView.as_view(),     name='dashboard'),
    path('calendar/',               CalendarView.as_view(),      name='calendar'),
    path('simulator/',              BudgetSimulatorView.as_view(), name='simulator'),
    # Carousel & grouped history
    path('summary/',                SummaryView.as_view(),       name='summary'),
    path('history/main/',           HistoryMainView.as_view(),   name='history-main'),
    path('history/week-details/',   WeekDetailsView.as_view(),   name='week-details'),
    path('history/month-details/',  MonthDetailsView.as_view(),  name='month-details'),
]
