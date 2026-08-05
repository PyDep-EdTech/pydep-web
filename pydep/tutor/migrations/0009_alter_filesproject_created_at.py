# Заполнить NULL в created_at перед NOT NULL + auto_now_add.
# AlterField напрямую на Django 4.2 даёт TypeError: fromisoformat (баг effective_default).

from django.db import migrations, models
from django.utils import timezone


def fill_created_at(apps, schema_editor):
    FilesProject = apps.get_model('tutor', 'FilesProject')
    FilesProject.objects.filter(created_at__isnull=True).update(created_at=timezone.now())


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0008_filesproject_allowed_users'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(fill_created_at, migrations.RunPython.noop),
                migrations.RunSQL(
                    sql="ALTER TABLE tutor_filesproject ALTER COLUMN created_at SET NOT NULL;",
                    reverse_sql=(
                        "ALTER TABLE tutor_filesproject "
                        "ALTER COLUMN created_at DROP NOT NULL;"
                    ),
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name='filesproject',
                    name='created_at',
                    field=models.DateTimeField(auto_now_add=True, verbose_name='Загружен'),
                ),
            ],
        ),
    ]
