from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='language',
            field=models.CharField(
                choices=[('ru', 'Russian'), ('en', 'English')],
                default='ru', max_length=2,
            ),
        ),
    ]
