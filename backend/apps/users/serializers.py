import pytz
from rest_framework import serializers

from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserProfile
        fields = [
            'telegram_id', 'username', 'first_name', 'last_name',
            'currency', 'timezone', 'notification_setting',
        ]
        read_only_fields = ['telegram_id']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserProfile
        fields = ['currency', 'timezone', 'notification_setting']

    def validate_timezone(self, value: str) -> str:
        if value not in pytz.all_timezones_set:
            raise serializers.ValidationError(f'Unknown timezone: "{value}".')
        return value

    def validate_currency(self, value: str) -> str:
        allowed = {c[0] for c in UserProfile.CURRENCY_CHOICES}
        if value not in allowed:
            raise serializers.ValidationError(
                f'Unsupported currency. Choose from: {", ".join(sorted(allowed))}.'
            )
        return value

    def validate_notification_setting(self, value: str) -> str:
        allowed = {c[0] for c in UserProfile.NOTIFICATION_CHOICES}
        if value not in allowed:
            raise serializers.ValidationError(
                f'Invalid setting. Choose from: {", ".join(sorted(allowed))}.'
            )
        return value
