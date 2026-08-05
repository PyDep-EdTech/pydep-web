# Generated manually

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tutor', '0007_filesproject_access_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='filesproject',
            name='allowed_users',
            field=models.ManyToManyField(
                blank=True,
                help_text='Видят файл независимо от группы доступа',
                related_name='allowed_project_files',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Доп. пользователи',
            ),
        ),
    ]
