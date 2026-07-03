from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserProfileManager(BaseUserManager):
    def create_user(self, telegram_id: int, **extra_fields):
        user = self.model(telegram_id=telegram_id, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, telegram_id: int, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(telegram_id, **extra_fields)


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model identified by Telegram user ID.
    No password — authentication is exclusively via Telegram initData → JWT.
    """
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('UZS', 'Uzbek Som'),
        ('EUR', 'Euro'),
        ('RUB', 'Russian Ruble'),
    ]

    telegram_id = models.BigIntegerField(primary_key=True)
    username    = models.CharField(max_length=64, blank=True, null=True)
    first_name  = models.CharField(max_length=64, blank=True, null=True)
    last_name   = models.CharField(max_length=64, blank=True, null=True)
    currency    = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    # IANA timezone string, e.g. "Asia/Tashkent" — sent by the frontend on first auth
    timezone    = models.CharField(max_length=64, default='UTC')

    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    USERNAME_FIELD  = 'telegram_id'
    REQUIRED_FIELDS = []

    objects = UserProfileManager()

    class Meta:
        db_table     = 'user_profiles'
        verbose_name = 'User Profile'

    def __str__(self) -> str:
        return f'@{self.username}' if self.username else f'tg:{self.telegram_id}'
