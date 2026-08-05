# Generated manually for FilesProject access groups

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tutor', '0006_lesson_repeat_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='filesproject',
            name='access_group',
            field=models.CharField(
                choices=[
                    ('all', 'Все'),
                    ('teachers', 'Преподаватели'),
                    ('students', 'Ученики'),
                ],
                default='all',
                max_length=16,
                verbose_name='Группа доступа',
            ),
        ),
        migrations.AddField(
            model_name='filesproject',
            name='created_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Загружен'),
        ),
        migrations.AddField(
            model_name='filesproject',
            name='uploaded_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='uploaded_project_files',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Загрузил',
            ),
        ),
        migrations.AlterField(
            model_name='filesproject',
            name='file',
            field=models.FileField(upload_to='files', verbose_name='Файл'),
        ),
        migrations.AlterField(
            model_name='filesproject',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Название'),
        ),
        migrations.AlterModelOptions(
            name='filesproject',
            options={
                'ordering': ['-created_at', 'name'],
                'verbose_name': 'Файл',
                'verbose_name_plural': 'Файлы',
            },
        ),
    ]
