from django.contrib import admin

from .models import Category, QuickTemplate, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('icon', 'name', 'user', 'is_system', 'created_at')
    list_filter   = ('is_system',)
    search_fields = ('name', 'user__username')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display   = ('user', 'category', 'amount', 'description', 'created_at')
    list_filter    = ('category',)
    search_fields  = ('description', 'user__username')
    date_hierarchy = 'created_at'
    raw_id_fields  = ('user', 'category')


@admin.register(QuickTemplate)
class QuickTemplateAdmin(admin.ModelAdmin):
    list_display  = ('title', 'user', 'category', 'amount', 'template_type')
    list_filter   = ('template_type',)
    search_fields = ('title', 'user__username')
