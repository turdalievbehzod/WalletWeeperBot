from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import TelegramAuthView, UserProfileView, ExchangeRatesView

urlpatterns = [
    path('auth/',           TelegramAuthView.as_view(),   name='telegram-auth'),
    path('auth/refresh/',   TokenRefreshView.as_view(),   name='token-refresh'),
    path('auth/me/',        UserProfileView.as_view(),    name='user-profile'),
    path('exchange-rates/', ExchangeRatesView.as_view(),  name='exchange-rates'),
    path('note/', NoteView.as_view(),  name='user-note')
]
