import pytz
from rest_framework import serializers
from django.utils import timezone

from .models import UserProfile, Note


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserProfile
        fields = [
            'telegram_id', 'username', 'first_name', 'last_name',
            'currency', 'timezone', 'notification_setting', 'language',
        ]
        read_only_fields = ['telegram_id']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserProfile
        fields = ['currency', 'timezone', 'notification_setting', 'language']

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

    def validate_language(self, value: str) -> str:
        allowed = {c[0] for c in UserProfile.LANGUAGE_CHOICES}
        if value not in allowed:
            raise serializers.ValidationError(
                f'Unsupported language. Choose from: {", ".join(sorted(allowed))}.'
            )
        return value

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'text', 'remind_at', 'repeat', 'is_sent']
        read_only_fields = ['id', 'is_sent']

    def validate_remind_at(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError('remind_at must be in the future.')
        return value