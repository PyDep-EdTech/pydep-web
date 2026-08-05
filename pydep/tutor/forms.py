from django import forms
from decimal import Decimal

from .models import Lesson
from .models import Homework
from .models import TutorStudentLink
from .models import FilesProject
from .file_access import file_access_user_queryset
from .student_links import accepted_students_for_teacher, is_student_linked
from users.models import CustomUser


def _apply_platform_field_styles(form):
    """Bootstrap 5: select → form-select, checkbox → form-check-input, остальное → form-control."""
    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs["class"] = "form-check-input"
            continue
        if isinstance(widget, (forms.Select, forms.RadioSelect)):
            widget.attrs["class"] = "form-select"
            continue
        base = widget.attrs.get("class", "")
        css = f"{base} form-control".strip()
        if isinstance(widget, forms.DateInput) and widget.input_type == "date":
            css += " platform-input-date"
            widget.attrs.setdefault("data-platform-picker", "date")
        elif isinstance(widget, forms.TimeInput) and widget.input_type == "time":
            css += " platform-input-time"
            widget.attrs.setdefault("data-platform-picker", "time")
        elif isinstance(widget, forms.DateTimeInput) and widget.input_type == "datetime-local":
            css += " platform-input-datetime"
        widget.attrs["class"] = css


class LessonForm(forms.ModelForm):
    REPEAT_CHOICES = (
        ("", "Без повтора"),
        ("1m", "Повторять месяц"),
        ("6m", "Повторять полгода"),
        ("12m", "Повторять год"),
    )

    repeat_period = forms.ChoiceField(
        label="Повтор",
        choices=REPEAT_CHOICES,
        required=False,
        help_text=(
            "Автоматически создать такие же занятия "
            "по неделям до выбранного периода"
        ),
    )

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher = teacher
        if "student" in self.fields and teacher is not None:
            qs = accepted_students_for_teacher(teacher)
            self.fields["student"].queryset = qs
            self.fields["student"].empty_label = None
            self.fields["student"].widget = forms.HiddenInput()
            self.fields["student"].required = True
        elif "student" in self.fields:
            self.fields["student"].queryset = CustomUser.objects.none()
            self.fields["student"].widget = forms.HiddenInput()
        _apply_platform_field_styles(self)
        # Оплата доступна только после окончания занятия
        if not self.instance.pk:
            self.fields.pop("is_paid", None)
        elif not self.instance.has_ended:
            self.fields.pop("is_paid", None)
        # Плейсхолдеры и подсказки
        self.fields["subject"].widget.attrs.setdefault(
            "placeholder", "Например: Python, математика, английский"
        )
        if "hourly_rate" in self.fields:
            self.fields["hourly_rate"].required = False
            self.fields["hourly_rate"].widget.attrs.setdefault(
                "placeholder", "Авто из ставки ученика"
            )
            self.fields["hourly_rate"].help_text = (
                "Если у ученика закреплена ставка — подставится автоматически. "
                "Можно изменить для этого занятия."
            )
        if self.instance and self.instance.pk:
            self.fields["repeat_period"].widget = forms.HiddenInput()
            self.fields["repeat_period"].required = False

    def clean_student(self):
        student = self.cleaned_data.get("student")
        if student and self.teacher and not is_student_linked(self.teacher, student):
            raise forms.ValidationError(
                "Выберите ученика из списка ваших подтверждённых учеников."
            )
        return student

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        # Разрешаем равенство? Нет: окончание должно быть строго позже начала
        if start_time and end_time and end_time <= start_time:
            self.add_error(
                "end_time",
                "Время окончания должно быть позже времени начала.",
            )
        return cleaned_data

    class Meta:
        model = Lesson
        # Преподаватель проставляется автоматически (текущий пользователь),
        # поэтому в форме его нет.
        fields = [
            "student",
            "subject",
            "date",
            "start_time",
            "end_time",
            "hourly_rate",
            "lesson_format",
            "comment",
            "status",
            "is_paid",
            # виртуальное поле формы (не из модели)
            "repeat_period",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "comment": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Ссылка на созвон, тема урока, домашнее задание…",
                }
            ),
        }


class PaymentUpdateForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["is_paid"]


class StudentHourlyRateForm(forms.ModelForm):
    """Ставка за час для прикреплённого ученика."""

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher = teacher
        _apply_platform_field_styles(self)
        self.fields["hourly_rate"].widget.attrs.setdefault(
            "placeholder", "Например: 1500"
        )

    def clean_hourly_rate(self):
        rate = self.cleaned_data.get("hourly_rate")
        if rate is not None and rate < Decimal("0"):
            raise forms.ValidationError("Ставка не может быть отрицательной.")
        return rate

    class Meta:
        model = TutorStudentLink
        fields = ["hourly_rate"]
        labels = {"hourly_rate": "₽/час"}
        widgets = {
            "hourly_rate": forms.NumberInput(
                attrs={"step": "0.01", "min": "0", "class": "form-control form-control-sm"},
            ),
        }


class HomeworkForm(forms.ModelForm):
    """Создание/редактирование задания преподавателем."""

    def __init__(self, *args, teacher=None, lesson=None, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher is not None and "lesson" in self.fields:
            qs = Lesson.objects.filter(
                teacher=teacher, student__isnull=False
            ).select_related("student")
            if lesson is not None:
                qs = qs.filter(pk=lesson.pk)
            self.fields["lesson"].queryset = qs
            self.fields["lesson"].empty_label = "— выберите занятие —"
            if lesson is not None:
                self.fields["lesson"].initial = lesson.pk
                self.fields["lesson"].widget = forms.HiddenInput()
        _apply_platform_field_styles(self)

    class Meta:
        model = Homework
        fields = ["lesson", "title", "description", "attachment", "due_date"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }


class LessonHomeworkForm(forms.ModelForm):
    """Выдача ДЗ к конкретному занятию (без выбора урока в форме)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_platform_field_styles(self)
        self.fields["title"].widget.attrs.setdefault(
            "placeholder", "Например: Задачи на циклы"
        )
        self.fields["description"].widget.attrs.setdefault(
            "placeholder", "Опишите задание для ученика…"
        )

    class Meta:
        model = Homework
        fields = ["title", "description", "attachment", "due_date"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }
        labels = {
            "title": "Заголовок",
            "description": "Задание",
            "attachment": "Материалы",
            "due_date": "Срок сдачи",
        }


class HomeworkSubmissionForm(forms.ModelForm):
    """Сдача задания учеником."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_platform_field_styles(self)
        for field in self.fields.values():
            field.required = False

    class Meta:
        model = Homework
        fields = ["submission_text", "submission_file"]
        widgets = {
            "submission_text": forms.Textarea(
                attrs={"rows": 6, "placeholder": "Ваш ответ или решение..."}
            ),
        }


class HomeworkGradeForm(forms.ModelForm):
    """Проверка задания преподавателем."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["grade"].widget = forms.Select(
            choices=[("", "—")] + [(i, str(i)) for i in range(1, 6)]
        )
        _apply_platform_field_styles(self)

    class Meta:
        model = Homework
        fields = ["grade", "teacher_comment"]
        widgets = {
            "teacher_comment": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Комментарий ученику..."}
            ),
        }


class FileProjectForm(forms.ModelForm):
    """Загрузка файла в ProjectBox."""

    def __init__(self, *args, teacher=None, **kwargs):
        self.teacher = teacher
        super().__init__(*args, **kwargs)
        _apply_platform_field_styles(self)
        self.fields["name"].required = False
        self.fields["name"].widget.attrs.setdefault(
            "placeholder", "Название (необязательно)"
        )

    def clean(self):
        cleaned = super().clean()
        name = (cleaned.get("name") or "").strip()
        uploaded = cleaned.get("file")
        if not name and uploaded:
            cleaned["name"] = uploaded.name
        elif name:
            cleaned["name"] = name
        return cleaned

    class Meta:
        model = FilesProject
        fields = ["name", "file", "access_group"]
        labels = {
            "name": "Название",
            "file": "Файл",
            "access_group": "Группа доступа",
        }


class FileProjectAccessForm(forms.ModelForm):
    """Настройка доступа к уже загруженному файлу."""

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_platform_field_styles(self)
        if teacher is not None:
            self.fields["allowed_users"].queryset = (
                file_access_user_queryset(teacher)
            )

    class Meta:
        model = FilesProject
        fields = ["access_group", "allowed_users"]
        labels = {
            "access_group": "Группа доступа",
            "allowed_users": "Доп. пользователи",
        }
        help_texts = {
            "allowed_users": "Индивидуальный доступ поверх группы.",
        }
        widgets = {
            "allowed_users": forms.SelectMultiple(),
        }
