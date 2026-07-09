from django.conf import settings
from django.db import models
from django.utils import timezone


class Category(models.Model):
    """
    A spending category. System-level rows have user=NULL and is_system=True.
    User-created categories have user set and is_system=False.

    on_delete=CASCADE on the user FK is intentional: deleting the user removes
    their private categories. Transactions referencing those categories are
    protected separately via SET_NULL on Transaction.category.
    """
    user      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories',
        null=True, blank=True,
    )
    name      = models.CharField(max_length=64)
    icon      = models.CharField(max_length=8)   # single emoji
    is_system = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        constraints = [
            # Prevent a user from creating two categories with the same name.
            models.UniqueConstraint(
                fields=['user', 'name'],
                condition=models.Q(user__isnull=False),
                name='unique_category_per_user',
            )
        ]

    def __str__(self) -> str:
        return f'{self.icon} {self.name}'


class Transaction(models.Model):
    """
    A single expense entry.

    created_at is NOT auto_now_add so users can back-fill past expenses.
    It defaults to now() in the serializer. All values are stored as UTC;
    timezone conversion happens at aggregation time (TruncDay with tzinfo).

    category uses SET_NULL so deleting a custom category never deletes spend
    history — the transaction simply moves to the "Uncategorised" bucket.
    """
    user     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,   # requirement: deleting a category must not delete transactions
        null=True, blank=True,
        related_name='transactions',
    )
    amount      = models.DecimalField(max_digits=16, decimal_places=4)
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at  = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
        indexes  = [
            # Composite index for the two most common filter patterns:
            # dashboard (user + date range) and calendar (user + date range + day grouping).
            models.Index(fields=['user', 'created_at'], name='idx_transaction_user_date'),
        ]

    def __str__(self) -> str:
        return f'{self.user} — {self.amount} @ {self.created_at:%Y-%m-%d}'


class QuickTemplate(models.Model):
    """
    A one-tap shortcut that pre-fills the expense form.
    'fixed'   → amount is set, tap = instant expense.
    'dynamic' → amount is null, tap = open form with category pre-selected.
    """
    FIXED   = 'fixed'
    DYNAMIC = 'dynamic'
    TYPE_CHOICES = [
        (FIXED,   'Fixed amount'),
        (DYNAMIC, 'Dynamic (category preset only)'),
    ]

    user          = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quick_templates',
    )
    title         = models.CharField(max_length=64)
    category      = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='quick_templates',
    )
    amount        = models.DecimalField(max_digits=16, decimal_places=4, null=True, blank=True)
    template_type = models.CharField(max_length=8, choices=TYPE_CHOICES, default=FIXED)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'quick_templates'
        verbose_name = 'Quick Template'

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.template_type == self.FIXED and self.amount is None:
            raise ValidationError({'amount': 'Fixed templates must specify an amount.'})

    def __str__(self) -> str:
        return f'{self.title} ({self.get_template_type_display()})'
