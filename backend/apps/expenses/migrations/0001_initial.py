import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('icon', models.CharField(max_length=8)),
                ('is_system', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='categories',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'db_table': 'categories', 'verbose_name_plural': 'Categories'},
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=14)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('category', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='transactions',
                    to='expenses.category',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='transactions',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'db_table': 'transactions', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='QuickTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=64)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('template_type', models.CharField(
                    choices=[('fixed','Fixed amount'),('dynamic','Dynamic (category preset only)')],
                    default='fixed', max_length=8,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='quick_templates',
                    to='expenses.category',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='quick_templates',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'db_table': 'quick_templates', 'verbose_name': 'Quick Template'},
        ),
        migrations.AddConstraint(
            model_name='category',
            constraint=models.UniqueConstraint(
                condition=models.Q(user__isnull=False),
                fields=['user', 'name'],
                name='unique_category_per_user',
            ),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['user', 'created_at'], name='idx_transaction_user_date'),
        ),
    ]
