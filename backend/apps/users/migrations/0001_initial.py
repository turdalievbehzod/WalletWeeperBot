import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False)),
                ('telegram_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('username', models.CharField(blank=True, max_length=64, null=True)),
                ('first_name', models.CharField(blank=True, max_length=64, null=True)),
                ('last_name', models.CharField(blank=True, max_length=64, null=True)),
                ('currency', models.CharField(
                    choices=[('USD','US Dollar'),('UZS','Uzbek Som'),('EUR','Euro'),('RUB','Russian Ruble')],
                    default='USD', max_length=3,
                )),
                ('timezone', models.CharField(default='UTC', max_length=64)),
                ('notification_setting', models.CharField(
                    choices=[('off','Отключены'),('daily','Каждый вечер'),('weekly','Раз в неделю')],
                    default='off', max_length=8,
                )),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'user_profiles', 'verbose_name': 'User Profile'},
        ),
        migrations.AddField(
            model_name='userprofile',
            name='groups',
            field=models.ManyToManyField(
                blank=True, related_name='user_set', related_query_name='user',
                to='auth.group', verbose_name='groups',
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user_permissions',
            field=models.ManyToManyField(
                blank=True, related_name='user_set', related_query_name='user',
                to='auth.permission', verbose_name='user permissions',
            ),
        ),
    ]
