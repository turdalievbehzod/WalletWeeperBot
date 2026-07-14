from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import TelegramAuthView, UserProfileView, ExchangeRatesView, NoteViewSet

router = DefaultRouter()
router.register('notes', NoteViewSet, basename='note')

urlpatterns = [
    path('auth/',           TelegramAuthView.as_view(),   name='telegram-auth'),
    path('auth/refresh/',   TokenRefreshView.as_view(),   name='token-refresh'),
    path('auth/me/',        UserProfileView.as_view(),    name='user-profile'),
    path('exchange-rates/', ExchangeRatesView.as_view(),  name='exchange-rates'),
    path('', include(router.urls)),
]
