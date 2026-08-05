from django.db import migrations, models

from lesson.slugs import unique_slug


def populate_slugs(apps, schema_editor):
    for model_name in ("Course", "Module", "Lesson"):
        Model = apps.get_model("lesson", model_name)
        for obj in Model.objects.all():
            source = obj.name if model_name == "Course" else obj.title
            if not obj.slug:
                obj.slug = unique_slug(Model, source, exclude_pk=obj.pk)
                obj.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("lesson", "0012_course_module_image_blank"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="slug",
            field=models.SlugField(blank=True, max_length=120, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="module",
            name="slug",
            field=models.SlugField(blank=True, max_length=120, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="lesson",
            name="slug",
            field=models.SlugField(blank=True, max_length=120, null=True, unique=True),
        ),
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="course",
            name="slug",
            field=models.SlugField(blank=True, max_length=120, unique=True),
        ),
        migrations.AlterField(
            model_name="module",
            name="slug",
            field=models.SlugField(blank=True, max_length=120, unique=True),
        ),
        migrations.AlterField(
            model_name="lesson",
            name="slug",
            field=models.SlugField(blank=True, max_length=120, unique=True),
        ),
    ]
