from django.db import migrations


def approve_existing(apps, schema_editor):
    """Записи, созданные до появления флоу одобрения, считаем одобренными."""
    CourseEnrollment = apps.get_model("lesson", "CourseEnrollment")
    CourseEnrollment.objects.update(status="approved")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("lesson", "0010_alter_courseenrollment_options_and_more"),
    ]

    operations = [
        migrations.RunPython(approve_existing, noop),
    ]
