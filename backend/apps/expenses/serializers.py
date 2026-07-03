from django.utils import timezone
from rest_framework import serializers

from .models import Category, Transaction, QuickTemplate


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ['id', 'name', 'icon', 'is_system']
        read_only_fields = ['id', 'is_system']


class TransactionSerializer(serializers.ModelSerializer):
    # Read-only denormalised fields for display — no extra query with select_related.
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    category_icon = serializers.CharField(source='category.icon', read_only=True, default=None)

    # Optional on create/update; defaults to now() if omitted.
    created_at = serializers.DateTimeField(
        required=False,
        default=serializers.CreateOnlyDefault(timezone.now),
    )

    class Meta:
        model  = Transaction
        fields = [
            'id', 'category', 'category_name', 'category_icon',
            'amount', 'description', 'created_at',
        ]
        read_only_fields = ['id']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero.')
        return value


class QuickTemplateSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    category_icon = serializers.CharField(source='category.icon', read_only=True, default=None)

    class Meta:
        model  = QuickTemplate
        fields = ['id', 'title', 'category', 'category_name', 'category_icon',
                  'amount', 'template_type']
        read_only_fields = ['id']

    def validate(self, data):
        if data.get('template_type') == QuickTemplate.FIXED and not data.get('amount'):
            raise serializers.ValidationError(
                {'amount': 'Fixed templates must have an amount.'}
            )
        return data
