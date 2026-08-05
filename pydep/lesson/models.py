from django_ckeditor_5.fields import CKEditor5Field
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from transliterate import translit

from lesson.slugs import unique_slug
import json


class Category(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        blank=True
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            # Транслитерируем с русского → английский, затем слаг
            transliterated = translit(self.name, 'ru', reversed=True)
            self.slug = slugify(transliterated)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = CKEditor5Field('Text', config_name='extends', blank=True, null=True)
    # Блочный контент урока - массив блоков в формате Editor.js
    content_blocks = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Блоки контента',
        help_text='Структурированный контент урока в формате блоков'
    )
    authors = models.ManyToManyField(
        "users.CustomUser",
        related_name="authored_lessons",
        verbose_name="Авторы"
    )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'

    def __str__(self):
        return self.title

    def has_blocks(self):
        """Проверяет, есть ли блоки контента"""
        return bool(self.content_blocks and len(self.content_blocks) > 0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Lesson, self.title, exclude_pk=self.pk)
        super().save(*args, **kwargs)


class Module(models.Model):
    title = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Название"
    )
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(
        verbose_name='Описание'
    )
    image = models.ImageField(
        upload_to='courses/modules',
        verbose_name='Логотип модуля',
        blank=True,
    )
    lessons = models.ManyToManyField(
        Lesson,
        through="LessonsInModule",
        verbose_name="Уроки"
    )
    authors = models.ManyToManyField(
        "users.CustomUser",
        related_name="authored_modules",
        verbose_name="Авторы"
    )

    class Meta:
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модули'

    def __str__(self):
        return self.title

    def ordered_lessons(self):
        return Lesson.objects.filter(
            lessonsinmodule__module=self,
        ).order_by("lessonsinmodule__sequence_number")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Module, self.title, exclude_pk=self.pk)
        super().save(*args, **kwargs)


class Course(models.Model):
    level_choices = [
        ("С нуля", "С нуля"),
        ("С опытом", "С опытом")
    ]
    category_choices = [
        ("Программирование", "Программирование")
    ]
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(
        verbose_name='Описание'
    )
    price = models.IntegerField(
        default=1000,
        verbose_name='Цена'
    )
    image = models.ImageField(
        upload_to='courses',
        verbose_name='Логотип курса',
        blank=True,
    )
    duration = models.IntegerField(
        default=3,
        verbose_name="Продолжительность"
    )
    level = models.CharField(
        choices=level_choices,
        max_length=50,
        default="С нуля",
        verbose_name="Уровень"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Категория",
        null=True
    )
    modules = models.ManyToManyField(
        Module,
        through='ModulesInCourse',
        verbose_name='Модули'
    )
    programming_language = models.CharField(max_length=255)
    authors = models.ManyToManyField(
        "users.CustomUser",
        related_name="authored_courses",
        verbose_name="Авторы"
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name="Опубликован"
    )

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ["name"]

    @property
    def monthly_price(self):
        """Ориентировочная стоимость в месяц (цена курса / длительность)."""
        if self.duration and self.duration > 0:
            return round(self.price / self.duration)
        return self.price

    @property
    def is_free(self):
        return self.price is None or self.price <= 0

    def access_for(self, user):
        """
        Статус доступа пользователя к курсу:
        'open'     — можно проходить;
        'pending'  — заявка на рассмотрении;
        'rejected' — заявка отклонена;
        'none'     — доступа нет, можно записаться.
        Бесплатные курсы открыты всем авторизованным.
        """
        if not (user and user.is_authenticated):
            return 'none'
        if self.is_free or user.is_superuser:
            return 'open'
        enrollment = self.enrollments.filter(user=user).first()
        if enrollment is None:
            return 'none'
        return {
            CourseEnrollment.Status.APPROVED: 'open',
            CourseEnrollment.Status.PENDING: 'pending',
            CourseEnrollment.Status.REJECTED: 'rejected',
        }.get(enrollment.status, 'none')

    def has_access(self, user):
        return self.access_for(user) == 'open'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Course, self.name, exclude_pk=self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def ordered_modules(self):
        return Module.objects.filter(
            modulesincourse__course=self,
        ).order_by("modulesincourse__sequence_number")


class ModulesInCourse(models.Model):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        verbose_name='Модуль'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name='Курс'
    )
    sequence_number = models.IntegerField(
        default=1,
        verbose_name="Порядковый номер модуля"
    )

    class Meta:
        verbose_name = 'Модули в курсе'
        verbose_name_plural = 'Модули в курсах'


class LessonsInModule(models.Model):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        verbose_name='Модуль'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        verbose_name='Урок'
    )
    sequence_number = models.IntegerField(
        default=1,
        verbose_name="Порядковый номер урока"
    )

    class Meta:
        verbose_name = 'Уроки в модуле'
        verbose_name_plural = 'Уроки в модулях'


class UserLessonProgress(models.Model):
    user = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        related_name="lesson_progress"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lesson_progress"
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lesson_progress"
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="lesson_progress"
    )
    completed = models.BooleanField(default=False)
    current = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Прогресс прохождения урока"
        verbose_name_plural = "Прогресс прохождения уроков"

    def __str__(self):
        return f"{self.user} {self.lesson} {self.completed}"


class Cohort(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="cohorts",
        verbose_name="Когорта"
    )
    students = models.ManyToManyField(
        "users.CustomUser",
        verbose_name="Студенты"
    )
    start_date = models.DateField(
        verbose_name="Дата старта"
    )

    class Meta:
        verbose_name = "Когорта"
        verbose_name_plural = "Когорты"

    def __str__(self):
        return f"№{self.id} - {self.course.name} ({self.start_date})"


class CourseEnrollment(models.Model):
    """
    Заявка/запись на курс.

    Жизненный цикл: pending → approved/rejected.
    Шаг одобрения — точка будущей интеграции эквайринга: вместо ручного
    одобрения админом сюда встанет обработчик успешной оплаты
    (см. CourseEnrollment.approve — его же будет вызывать платёжный вебхук).
    """

    class Status(models.TextChoices):
        PENDING = "pending", "На рассмотрении"
        APPROVED = "approved", "Одобрена"
        REJECTED = "rejected", "Отклонена"

    user = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        related_name="course_learn",
        verbose_name="Пользователь"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Курс"
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус",
    )
    enrolled_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Заявка создана",
    )
    decided_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Решение принято",
    )
    decided_by = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="decided_enrollments",
        verbose_name="Кто одобрил/отклонил",
    )

    class Meta:
        verbose_name = "Запись на курс"
        verbose_name_plural = "Записи на курсы"
        ordering = ["-enrolled_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"], name="uniq_user_course_enrollment"
            )
        ]

    def __str__(self):
        return f"{self.user} → {self.course} ({self.get_status_display()})"

    @property
    def is_approved(self):
        return self.status == self.Status.APPROVED

    @property
    def is_pending(self):
        return self.status == self.Status.PENDING

    def approve(self, by=None):
        """Одобрить заявку (точка подключения успешной оплаты)."""
        self.status = self.Status.APPROVED
        self.decided_at = timezone.now()
        self.decided_by = by
        self.save(update_fields=["status", "decided_at", "decided_by"])

    def reject(self, by=None):
        self.status = self.Status.REJECTED
        self.decided_at = timezone.now()
        self.decided_by = by
        self.save(update_fields=["status", "decided_at", "decided_by"])


class PracticeTask(models.Model):
    """Практическое задание для песочницы, опционально привязанное к уроку."""

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="practice_tasks",
        null=True,
        blank=True,
        verbose_name="Урок",
    )
    title = models.CharField("Заголовок", max_length=200)
    statement = models.TextField(
        "Условие",
        help_text="Что нужно сделать. Поддерживается обычный текст.",
    )
    starter_code = models.TextField(
        "Стартовый код",
        blank=True,
        default="",
        help_text="Код, который подставится в редактор при выборе задания.",
    )
    expected_output = models.TextField(
        "Ожидаемый вывод",
        blank=True,
        default="",
        help_text=(
            "Если заполнено — кнопка «Проверить» сравнит вывод программы "
            "с этим значением (без учёта хвостовых пробелов)."
        ),
    )
    position = models.PositiveIntegerField("Порядок", default=0)
    created_by = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_practice_tasks",
        verbose_name="Автор",
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Практическое задание"
        verbose_name_plural = "Практические задания"
        ordering = ["position", "id"]

    def __str__(self):
        return self.title

    @property
    def has_check(self):
        return bool(self.expected_output.strip())
