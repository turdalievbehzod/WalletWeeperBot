from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(BaseUserAdmin):
    list_display  = ('telegram_id', 'username', 'first_name', 'currency', 'timezone', 'is_staff')
    search_fields = ('telegram_id', 'username', 'first_name')
    ordering      = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None,          {'fields': ('telegram_id', 'username', 'first_name', 'last_name')}),
        ('Preferences', {'fields': ('currency', 'timezone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Timestamps',  {'fields': ('created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('telegram_id',)}),
    )
    filter_horizontal = ('groups', 'user_permissions')
