from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lesson", "0011_existing_enrollments_approved"),
    ]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="image",
            field=models.ImageField(
                blank=True,
                upload_to="courses",
                verbose_name="Логотип курса",
            ),
        ),
        migrations.AlterField(
            model_name="module",
            name="image",
            field=models.ImageField(
                blank=True,
                upload_to="courses/modules",
                verbose_name="Логотип модуля",
            ),
        ),
    ]
