import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("lesson", "0013_course_lesson_module_slug"),
    ]

    operations = [
        migrations.CreateModel(
            name="PracticeTask",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200, verbose_name="Заголовок")),
                (
                    "statement",
                    models.TextField(
                        help_text="Что нужно сделать. Поддерживается обычный текст.",
                        verbose_name="Условие",
                    ),
                ),
                (
                    "starter_code",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Код, который подставится в редактор при выборе задания.",
                        verbose_name="Стартовый код",
                    ),
                ),
                (
                    "expected_output",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text=(
                            "Если заполнено — кнопка «Проверить» сравнит вывод "
                            "программы с этим значением (без учёта хвостовых пробелов)."
                        ),
                        verbose_name="Ожидаемый вывод",
                    ),
                ),
                (
                    "position",
                    models.PositiveIntegerField(default=0, verbose_name="Порядок"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Создано"),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_practice_tasks",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Автор",
                    ),
                ),
                (
                    "lesson",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="practice_tasks",
                        to="lesson.lesson",
                        verbose_name="Урок",
                    ),
                ),
            ],
            options={
                "verbose_name": "Практическое задание",
                "verbose_name_plural": "Практические задания",
                "ordering": ["position", "id"],
            },
        ),
    ]
