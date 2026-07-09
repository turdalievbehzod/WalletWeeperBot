from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(decimal_places=4, max_digits=16),
        ),
        migrations.AlterField(
            model_name='quicktemplate',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=16, null=True),
        ),
    ]
