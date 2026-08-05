from django.db import models
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
import uuid
from datetime import datetime


class FilesProject(models.Model):
    """Файл в ProjectBox с группой доступа."""

    class AccessGroup(models.TextChoices):
        ALL = "all", "Все"
        TEACHERS = "teachers", "Преподаватели"
        STUDENTS = "students", "Ученики"

    file = models.FileField("Файл", upload_to="files")
    name = models.CharField("Название", max_length=200)
    access_group = models.CharField(
        "Группа доступа",
        max_length=16,
        choices=AccessGroup.choices,
        default=AccessGroup.ALL,
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_project_files",
        verbose_name="Загрузил",
    )
    created_at = models.DateTimeField("Загружен", auto_now_add=True)
    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="allowed_project_files",
        verbose_name="Доп. пользователи",
        help_text="Видят файл независимо от группы доступа",
    )

    class Meta:
        ordering = ["-created_at", "name"]
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"

    def __str__(self):
        return self.name

    def user_can_access(self, user) -> bool:
        if not user.is_authenticated:
            return False
        if user.is_superuser or user.is_tutor_admin:
            return True
        if self.allowed_users.filter(pk=user.pk).exists():
            return True
        if self.access_group == self.AccessGroup.ALL:
            return True
        if self.access_group == self.AccessGroup.TEACHERS:
            return bool(user.is_teacher)
        if self.access_group == self.AccessGroup.STUDENTS:
            return bool(user.is_student or user.is_tutor_student)
        return False

    @classmethod
    def visible_for(cls, user):
        if not user.is_authenticated:
            return cls.objects.none()
        if user.is_superuser or user.is_tutor_admin:
            return cls.objects.prefetch_related("allowed_users")
        q = Q(access_group=cls.AccessGroup.ALL)
        if user.is_teacher:
            q |= Q(access_group=cls.AccessGroup.TEACHERS)
        if user.is_student or user.is_tutor_student:
            q |= Q(access_group=cls.AccessGroup.STUDENTS)
        q |= Q(allowed_users=user)
        return cls.objects.filter(q).prefetch_related("allowed_users").distinct()


class TutorStudentLink(models.Model):
    """Привязка ученика к преподавателю (с подтверждением учеником)."""

    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает подтверждения"
        ACCEPTED = "accepted", "Принято"
        REJECTED = "rejected", "Отклонено"

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tutor_student_links_as_teacher",
        verbose_name="Преподаватель",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tutor_student_links_as_student",
        verbose_name="Ученик",
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус",
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    responded_at = models.DateTimeField("Ответ ученика", null=True, blank=True)
    hourly_rate = models.DecimalField(
        "Стоимость часа",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Ставка за час для этого ученика (₽)",
    )

    class Meta:
        verbose_name = "Привязка ученика"
        verbose_name_plural = "Привязки учеников"
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "student"],
                name="unique_teacher_student_link",
            ),
        ]

    def __str__(self):
        return f"{self.teacher} → {self.student} ({self.get_status_display()})"


class Lesson(models.Model):
    class LessonFormat(models.TextChoices):
        ONLINE = "online", "Онлайн"
        OFFLINE = "offline", "Офлайн"

    class LessonStatus(models.TextChoices):
        SCHEDULED = "scheduled", "Запланировано"
        COMPLETED = "completed", "Проведено"
        CANCELED = "canceled", "Отменено"

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lessons_as_teacher",
        verbose_name="Преподаватель",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lessons_as_student",
        verbose_name="Ученик",
    )
    subject = models.CharField("Предмет", max_length=200)
    date = models.DateField("Дата", default=timezone.localdate)
    start_time = models.TimeField("Начало")
    end_time = models.TimeField("Окончание")
    lesson_format = models.CharField(
        "Формат",
        max_length=16,
        choices=LessonFormat.choices,
        default=LessonFormat.ONLINE,
    )
    comment = models.CharField("Комментарий", max_length=500, blank=True)
    status = models.CharField(
        "Статус",
        max_length=16,
        choices=LessonStatus.choices,
        default=LessonStatus.SCHEDULED,
    )
    is_paid = models.BooleanField("Оплачено", default=False)
    hourly_rate = models.DecimalField(
        "Стоимость часа",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Ставка на момент занятия (₽/час)",
    )
    repeat_group = models.UUIDField(
        "Группа повторов",
        null=True,
        blank=True,
        db_index=True,
        help_text="Общий идентификатор для занятий, созданных одним повтором",
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        ordering = ["date", "start_time"]
        verbose_name = "Занятие"
        verbose_name_plural = "Занятия"

    def __str__(self) -> str:
        student_name = getattr(self.student, "get_full_name", None)
        if callable(student_name):
            full_name = self.student.get_full_name()
            another_full_name = self.student and self.student.username
            student_name = full_name or another_full_name
        else:
            student_name = self.student and getattr(
                self.student,
                "username",
                str(self.student)
            )
        return (
            f"{self.subject} — {self.date} "
            f"{self.start_time}-{self.end_time} "
            f"({student_name or 'без ученика'})"
        )

    @property
    def duration_hours(self):
        from .billing import lesson_duration_hours
        return lesson_duration_hours(self)

    @property
    def total_cost(self):
        from .billing import lesson_total_cost
        return lesson_total_cost(self)

    @property
    def end_at(self):
        """Дата и время окончания занятия (aware)."""
        tz = timezone.get_current_timezone()
        return timezone.make_aware(
            datetime.combine(self.date, self.end_time),
            tz,
        )

    @property
    def has_ended(self):
        """Занятие завершилось: текущий момент позже даты и времени окончания."""
        return timezone.now() > self.end_at

    @property
    def payment_due(self):
        """Требуется оплата: завершено, не отменено, есть ставка, не оплачено."""
        return (
            self.status != self.LessonStatus.CANCELED
            and self.has_ended
            and not self.is_paid
            and self.total_cost is not None
        )

    @property
    def is_cancelable(self):
        return self.status not in (
            self.LessonStatus.CANCELED,
            self.LessonStatus.COMPLETED,
        )

    @classmethod
    def ended_q(cls):
        """Q-объект для фильтрации уже завершённых занятий."""
        now = timezone.localtime()
        return Q(date__lt=now.date()) | Q(
            date=now.date(),
            end_time__lt=now.time(),
        )


class Homework(models.Model):
    """Домашнее задание, привязанное к занятию (преподаватель → ученик)."""

    class State(models.TextChoices):
        ASSIGNED = "assigned", "Выдано"
        SUBMITTED = "submitted", "Сдано"
        GRADED = "graded", "Проверено"

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="homeworks",
        verbose_name="Занятие",
    )
    title = models.CharField("Заголовок", max_length=200)
    description = models.TextField("Задание")
    attachment = models.FileField(
        "Материалы",
        upload_to="homework/tasks",
        blank=True,
        null=True,
    )
    due_date = models.DateField("Срок сдачи", blank=True, null=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    # Сдача ученика
    submission_text = models.TextField("Ответ ученика", blank=True)
    submission_file = models.FileField(
        "Файл ученика",
        upload_to="homework/submissions",
        blank=True,
        null=True,
    )
    submitted_at = models.DateTimeField("Сдано", blank=True, null=True)

    # Проверка преподавателя
    grade = models.PositiveSmallIntegerField(
        "Оценка", blank=True, null=True,
        help_text="Оценка от 1 до 5",
    )
    teacher_comment = models.TextField("Комментарий преподавателя", blank=True)
    reviewed_at = models.DateTimeField("Проверено", blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Домашнее задание"
        verbose_name_plural = "Домашние задания"

    def __str__(self):
        return f"{self.title} ({self.lesson.subject})"

    @property
    def teacher(self):
        return self.lesson.teacher

    @property
    def student(self):
        return self.lesson.student

    @property
    def state(self):
        if self.grade is not None:
            return self.State.GRADED
        if self.submitted_at:
            return self.State.SUBMITTED
        return self.State.ASSIGNED

    @property
    def state_label(self):
        return self.State(self.state).label

    @property
    def is_overdue(self):
        if self.due_date and not self.submitted_at:
            return self.due_date < timezone.localdate()
        return False
