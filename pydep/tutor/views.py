from django.db.models import Count
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import json
import uuid

from .models import FilesProject, Lesson, Homework, TutorStudentLink
from .forms import (
    LessonForm,
    PaymentUpdateForm,
    HomeworkForm,
    HomeworkSubmissionForm,
    HomeworkGradeForm,
    StudentHourlyRateForm,
    LessonHomeworkForm,
    FileProjectForm,
    FileProjectAccessForm,
)
from .file_access import can_manage_project_file, file_access_user_queryset
from .file_access import file_access_users_cards_json
from .schedule_helpers import lesson_calendar_events, lessons_unpaid_count
from .billing import (
    resolve_lesson_hourly_rate,
    student_debt_summary,
    teacher_income_summary,
    student_hourly_rates_for_teacher,
    lesson_total_cost,
)
from .nav_helpers import finance_month_from_request, month_choices, schedule_role
from .student_links import (
    accepted_students_for_teacher,
    students_available_to_invite,
    users_cards_json,
)
from .student_items import accepted_student_items
from .lesson_series import attach_series_counts, lessons_in_series, series_count


def _is_teacher(user):
    """Может ли пользователь вести занятия (преподаватель/админ)."""
    return bool(
        user.is_authenticated
        and (user.is_teacher or user.is_superuser or user.is_tutor_admin)
    )


def _wants_json(request):
    return (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or "application/json" in request.headers.get("Accept", "")
    )


def _projectbox_access_context(user):
    from django.templatetags.static import static

    avatar = static("img/anonymous_user.png")
    return {
        "access_group_choices_json": json.dumps(
            list(FilesProject.AccessGroup.choices), ensure_ascii=False
        ),
        "access_users_json": file_access_users_cards_json(user, avatar),
        "default_avatar": avatar,
    }


def my_tutor(request):
    if request.user.is_authenticated:
        return redirect(reverse('tutor:dashboard'))
    return render(request, "tutor/my_tutor.html")


@login_required
def dashboard(request):
    """Лёгкий обзор: ближайшие занятия и важные уведомления."""
    user = request.user
    is_teacher = _is_teacher(user)
    is_student = user.is_student or user.is_tutor_student
    today = timezone.localdate()

    upcoming_teach = (
        Lesson.objects.filter(teacher=user, date__gte=today)
        .select_related('student')
        .order_by('date', 'start_time')[:3]
        if is_teacher else Lesson.objects.none()
    )
    upcoming_learn = (
        Lesson.objects.filter(student=user, date__gte=today)
        .select_related('teacher')
        .order_by('date', 'start_time')[:3]
    )

    pending_requests = TutorStudentLink.objects.filter(
        student=user,
        status=TutorStudentLink.Status.PENDING,
    ).select_related('teacher')[:5]

    pending_invites_count = 0
    if is_teacher:
        pending_invites_count = TutorStudentLink.objects.filter(
            teacher=user,
            status=TutorStudentLink.Status.PENDING,
        ).count()

    unpaid_count = Lesson.objects.filter(
        student=user,
        is_paid=False,
    ).filter(
        Lesson.ended_q(),
    ).exclude(
        status=Lesson.LessonStatus.CANCELED,
    ).count()

    teacher_unpaid_count = 0
    if is_teacher:
        teacher_unpaid_count = lessons_unpaid_count(
            Lesson.objects.filter(teacher=user)
        )

    hw_pending = Homework.objects.filter(
        lesson__student=user, grade__isnull=True,
    ).count()

    student_debt = student_debt_summary(user)
    debt_total = student_debt['total'] if student_debt['count'] else None

    context = {
        'user': user,
        'is_teacher': is_teacher,
        'is_student': is_student,
        'upcoming_teach': upcoming_teach,
        'upcoming_learn': upcoming_learn,
        'pending_requests': pending_requests,
        'pending_invites_count': pending_invites_count,
        'unpaid_count': unpaid_count,
        'teacher_unpaid_count': teacher_unpaid_count,
        'debt_total': debt_total,
        'hw_pending': hw_pending,
    }
    return render(request, 'tutor/dashboard.html', context)


@login_required
def finances(request):
    """Финансы: доход преподавателя и задолженность ученика."""
    user = request.user
    is_teacher = _is_teacher(user)
    today = timezone.localdate()
    finance_month = finance_month_from_request(request, today=today)

    student_debt = student_debt_summary(user)
    teacher_finance = (
        teacher_income_summary(user, finance_month.year, finance_month.month)
        if is_teacher else None
    )

    unpaid_teacher_items = []
    if is_teacher:
        unpaid_qs = (
            Lesson.objects.filter(teacher=user, is_paid=False)
            .filter(Lesson.ended_q())
            .exclude(status=Lesson.LessonStatus.CANCELED)
            .select_related('student')
            .order_by('-date', '-start_time')
        )
        for lesson in unpaid_qs:
            cost = lesson_total_cost(lesson)
            if cost is not None and cost > 0:
                unpaid_teacher_items.append({'lesson': lesson, 'cost': cost})

    context = {
        'is_teacher': is_teacher,
        'student_debt': student_debt,
        'teacher_finance': teacher_finance,
        'unpaid_teacher_items': unpaid_teacher_items,
        'finance_month': finance_month.strftime('%Y-%m'),
        'month_choices': month_choices(today=today),
    }
    return render(request, 'tutor/finances.html', context)


@login_required
def projectbox(request):
    """Файлы проектов: предпросмотр, скачивание, загрузка (для преподавателей)."""
    can_upload = _is_teacher(request.user) or request.user.is_superuser

    if request.method == "POST":
        if not can_upload:
            raise PermissionDenied("Загружать файлы могут только преподаватели.")
        form = FileProjectForm(request.POST, request.FILES, teacher=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.uploaded_by = request.user
            obj.save()
            allowed_ids = request.POST.getlist("allowed_users")
            if allowed_ids:
                valid_ids = file_access_user_queryset(request.user).filter(
                    pk__in=allowed_ids
                )
                obj.allowed_users.set(valid_ids)
            messages.success(request, "Файл добавлен.")
            return redirect(reverse("tutor:projectbox"))
        messages.error(request, "Не удалось загрузить файл. Проверьте форму.")
    else:
        form = FileProjectForm(teacher=request.user) if can_upload else None

    files = (
        FilesProject.visible_for(request.user)
        .annotate(allowed_users_count=Count("allowed_users"))
    )
    manageable_ids = {
        f.pk for f in files if can_manage_project_file(request.user, f)
    }
    return render(
        request,
        "tutor/projectbox.html",
        {
            "files": files,
            "form": form,
            "can_upload": can_upload,
            "manageable_ids": manageable_ids,
            **_projectbox_access_context(request.user),
        },
    )


@login_required
def projectbox_file_access(request, pk: int):
    """Тонкая настройка доступа к файлу (JSON API для модального окна)."""
    file_obj = get_object_or_404(FilesProject, pk=pk)
    if not file_obj.user_can_access(request.user):
        raise PermissionDenied()
    if not can_manage_project_file(request.user, file_obj):
        raise PermissionDenied("Недостаточно прав для изменения доступа.")

    if request.method == "GET":
        if not _wants_json(request):
            return redirect(reverse("tutor:projectbox"))
        return JsonResponse(
            {
                "ok": True,
                "file": {
                    "id": file_obj.pk,
                    "name": file_obj.name,
                    "access_group": file_obj.access_group,
                    "allowed_user_ids": list(
                        file_obj.allowed_users.values_list("pk", flat=True)
                    ),
                },
            }
        )

    if request.method == "POST":
        form = FileProjectAccessForm(
            request.POST, instance=file_obj, teacher=request.user
        )
        if form.is_valid():
            form.save()
            count = file_obj.allowed_users.count()
            if _wants_json(request):
                group_label = file_obj.get_access_group_display()
                return JsonResponse(
                    {
                        "ok": True,
                        "file": {
                            "id": file_obj.pk,
                            "access_group": file_obj.access_group,
                            "access_group_label": group_label,
                            "allowed_user_ids": list(
                                file_obj.allowed_users.values_list("pk", flat=True)
                            ),
                            "allowed_users_count": count,
                        },
                    }
                )
            messages.success(request, "Доступ к файлу обновлён.")
            return redirect(reverse("tutor:projectbox"))
        if _wants_json(request):
            return JsonResponse(
                {"ok": False, "errors": form.errors}, status=400
            )
        messages.error(request, "Проверьте форму.")
        return redirect(reverse("tutor:projectbox"))

    return redirect(reverse("tutor:projectbox"))


@login_required
def profile(request):
    """Аккаунт: имя, роли, настройки."""
    user = request.user
    is_teacher = _is_teacher(user)

    roles = []
    if user.is_superuser:
        roles.append('Модератор')
    if user.is_teacher:
        roles.append('Преподаватель')
    if user.is_student:
        roles.append('Студент')
    if user.is_tutor_student and 'Студент' not in roles:
        roles.append('Ученик')

    context = {
        'user': user,
        'is_teacher': is_teacher,
        'roles_label': ' · '.join(roles) if roles else '',
    }
    return render(request, 'tutor/profile.html', context)


@login_required
def schedule(request):
    """Расписание: календарь и компактный список занятий."""
    user = request.user
    is_teacher = _is_teacher(user)
    is_student = user.is_student or user.is_tutor_student
    role = schedule_role(request, is_teacher=is_teacher, is_student=is_student)

    teacher_lessons_qs = (
        Lesson.objects.select_related('teacher', 'student').filter(
            teacher=user
        ).order_by('date', 'start_time')
        if is_teacher
        else Lesson.objects.none()
    )
    student_lessons_qs = (
        Lesson.objects.select_related('teacher', 'student').filter(
            student=user
        ).order_by('date', 'start_time')
    )

    if role == 'teach':
        lessons_qs = teacher_lessons_qs
        lessons = (
            attach_series_counts(teacher_lessons_qs) if is_teacher else lessons_qs
        )
        calendar_events = lesson_calendar_events(lessons_qs, can_edit=True)
        can_edit = True
    else:
        lessons_qs = student_lessons_qs
        lessons = lessons_qs
        calendar_events = lesson_calendar_events(lessons_qs, can_edit=False)
        can_edit = False

    def _stats(qs):
        return {
            'scheduled': qs.filter(
                status=Lesson.LessonStatus.SCHEDULED
            ).count(),
            'unpaid': lessons_unpaid_count(qs),
        }

    context = {
        'is_teacher': is_teacher,
        'is_student': is_student,
        'role': role,
        'lessons': lessons,
        'stats': _stats(lessons_qs),
        'calendar_events': calendar_events,
        'can_edit': can_edit,
        'calendar_json_id': 'schedule-calendar-data',
    }
    return render(request, 'tutor/schedule.html', context)


@login_required
def lesson_create(request):
    if not _is_teacher(request.user):
        messages.error(
            request, 'Создавать занятия могут только преподаватели.'
        )
        return redirect(reverse('tutor:schedule'))

    if request.method == 'POST':
        form = LessonForm(request.POST, teacher=request.user)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.teacher = request.user
            lesson.hourly_rate = resolve_lesson_hourly_rate(
                lesson,
                request.user,
                form.cleaned_data.get('hourly_rate'),
            )
            repeat = form.cleaned_data.get('repeat_period')
            repeat_group = uuid.uuid4() if repeat else None
            if repeat_group:
                lesson.repeat_group = repeat_group
            lesson.save()
            if repeat:
                months = {"1m": 1, "6m": 6, "12m": 12}.get(repeat, 0)
                if months:
                    end_date = lesson.date + relativedelta(months=+months)
                    current_date = lesson.date + timedelta(weeks=1)
                    while current_date <= end_date:
                        Lesson.objects.create(
                            teacher=lesson.teacher,
                            student=lesson.student,
                            subject=lesson.subject,
                            date=current_date,
                            start_time=lesson.start_time,
                            end_time=lesson.end_time,
                            lesson_format=lesson.lesson_format,
                            comment=lesson.comment,
                            status=lesson.status,
                            hourly_rate=lesson.hourly_rate,
                            repeat_group=repeat_group,
                            is_paid=False,
                        )
                        current_date += timedelta(weeks=1)
            messages.success(request, 'Занятие создано.')
            return redirect(reverse('tutor:schedule'))
    else:
        form = LessonForm(teacher=request.user)
    return _lesson_form_response(request, form, 'Новое занятие')


def _lesson_form_response(
    request, form, title, *, lesson=None, homework_form=None, lesson_homeworks=None
):
    from django.templatetags.static import static

    students = accepted_students_for_teacher(request.user)
    avatar = request.build_absolute_uri(static('img/anonymous_user.png'))
    import json
    return render(
        request,
        'tutor/lesson_form.html',
        {
            'form': form,
            'title': title,
            'lesson': lesson or form.instance,
            'teacher_students': students,
            'students_cards_json': users_cards_json(
                students,
                default_avatar=avatar,
            ),
            'student_rates_json': json.dumps(
                student_hourly_rates_for_teacher(request.user),
                ensure_ascii=False,
            ),
            'lesson_series_count': (
                series_count(form.instance) if form.instance.pk else 0
            ),
            'homework_form': homework_form,
            'lesson_homeworks': lesson_homeworks or [],
            'can_add_homework': bool(
                form.instance.pk
                and form.instance.student_id
                and _is_teacher(request.user)
            ),
        },
    )


@login_required
def lesson_update(request, pk: int):
    lesson = get_object_or_404(Lesson, pk=pk)
    if not (
        request.user == lesson.teacher
        or request.user.is_superuser
        or request.user.is_tutor_admin
    ):
        raise PermissionDenied(
            'Вы можете редактировать только свои занятия.'
        )

    lesson_homeworks = Homework.objects.filter(lesson=lesson).order_by('-created_at')
    homework_form = LessonHomeworkForm()
    form = LessonForm(instance=lesson, teacher=request.user)

    if request.method == 'POST':
        if request.POST.get('form_type') == 'homework':
            if not lesson.student_id:
                messages.error(request, 'Нельзя выдать ДЗ без ученика на занятии.')
                return redirect(reverse('tutor:lesson_update', args=[pk]))
            homework_form = LessonHomeworkForm(request.POST, request.FILES)
            if homework_form.is_valid():
                hw = homework_form.save(commit=False)
                hw.lesson = lesson
                hw.save()
                messages.success(request, 'Задание выдано ученику.')
                return redirect(reverse('tutor:lesson_update', args=[pk]) + '#homework')
            form = LessonForm(instance=lesson, teacher=request.user)
        else:
            form = LessonForm(request.POST, instance=lesson, teacher=request.user)
            if form.is_valid():
                lesson = form.save(commit=False)
                lesson.hourly_rate = resolve_lesson_hourly_rate(
                    lesson,
                    request.user,
                    form.cleaned_data.get('hourly_rate'),
                )
                lesson.save()
                messages.success(request, 'Занятие обновлено.')
                return redirect(reverse('tutor:schedule'))
    else:
        form = LessonForm(instance=lesson, teacher=request.user)

    return _lesson_form_response(
        request,
        form,
        'Редактировать занятие',
        lesson=lesson,
        homework_form=homework_form,
        lesson_homeworks=lesson_homeworks,
    )


@login_required
def lesson_payment_toggle(request, pk: int):
    lesson = get_object_or_404(Lesson, pk=pk)
    # Отмечать оплату может только преподаватель этого занятия (или админ).
    if not (
        request.user == lesson.teacher
        or request.user.is_superuser
        or request.user.is_tutor_admin
    ):
        raise PermissionDenied(
            'Вы можете отмечать оплату только своих занятий.'
        )
    if not lesson.has_ended:
        messages.warning(
            request,
            'Отметить оплату можно только после окончания занятия.',
        )
        return redirect(reverse('tutor:schedule'))
    if lesson.status == Lesson.LessonStatus.CANCELED:
        messages.warning(request, 'Отменённое занятие нельзя оплатить.')
        return redirect(reverse('tutor:schedule'))
    if request.method == 'POST':
        form = PaymentUpdateForm(request.POST, instance=lesson)
        if form.is_valid():
            lesson = form.save(commit=False)
            if lesson.is_paid and lesson.hourly_rate is None:
                lesson.hourly_rate = resolve_lesson_hourly_rate(
                    lesson, request.user
                )
            lesson.save()
            return redirect(reverse('tutor:schedule'))
    else:
        form = PaymentUpdateForm(instance=lesson)
    return render(
        request,
        'tutor/lesson_payment.html',
        {'form': form, 'lesson': lesson}
    )


# ──────────────────────────── Домашние задания ────────────────────────────

@login_required
def homework_list(request):
    """Список ДЗ: одна роль за раз через ?view=issued|assigned."""
    user = request.user
    is_teacher = _is_teacher(user)
    is_student = user.is_student or user.is_tutor_student

    view = request.GET.get('view')
    if is_teacher and is_student:
        view = view if view in ('issued', 'assigned') else 'issued'
    elif is_teacher:
        view = 'issued'
    else:
        view = 'assigned'

    base = Homework.objects.select_related(
        "lesson", "lesson__teacher", "lesson__student"
    )
    if view == 'issued':
        homeworks = base.filter(lesson__teacher=user) if is_teacher else Homework.objects.none()
    else:
        homeworks = base.filter(lesson__student=user)

    context = {
        "is_teacher": is_teacher,
        "is_student": is_student,
        "view": view,
        "homeworks": homeworks,
        "show_view_switch": is_teacher and is_student,
    }
    return render(request, "tutor/homework_list.html", context)


@login_required
def homework_create(request):
    if not _is_teacher(request.user):
        messages.error(request, "Выдавать задания могут только преподаватели.")
        return redirect(reverse("tutor:homework_list"))

    lesson = None
    lesson_id = request.GET.get("lesson") or request.POST.get("lesson")
    if lesson_id:
        lesson = Lesson.objects.filter(
            pk=lesson_id,
            teacher=request.user,
            student__isnull=False,
        ).first()

    if request.method == "POST":
        form = HomeworkForm(
            request.POST, request.FILES, teacher=request.user, lesson=lesson
        )
        if form.is_valid():
            hw = form.save()
            messages.success(request, "Задание выдано ученику.")
            if lesson:
                return redirect(reverse("tutor:lesson_update", args=[lesson.pk]) + "#homework")
            return redirect(reverse("tutor:homework_detail", args=[hw.pk]))
    else:
        form = HomeworkForm(teacher=request.user, lesson=lesson)
    back_url = (
        reverse("tutor:lesson_update", args=[lesson.pk]) + "#homework"
        if lesson else reverse("tutor:homework_list")
    )
    return render(
        request,
        "tutor/homework_form.html",
        {"form": form, "title": "Новое задание", "back_url": back_url},
    )


@login_required
def homework_detail(request, pk: int):
    hw = get_object_or_404(
        Homework.objects.select_related(
            "lesson", "lesson__teacher", "lesson__student"
        ),
        pk=pk,
    )
    user = request.user
    is_owner_teacher = (
        user == hw.lesson.teacher or user.is_superuser or user.is_tutor_admin
    )
    is_recipient = user == hw.lesson.student
    if not (is_owner_teacher or is_recipient):
        raise PermissionDenied("Это задание вам недоступно.")

    submit_form = HomeworkSubmissionForm(instance=hw)
    grade_form = HomeworkGradeForm(instance=hw)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "submit" and is_recipient:
            submit_form = HomeworkSubmissionForm(
                request.POST, request.FILES, instance=hw
            )
            if submit_form.is_valid():
                hw = submit_form.save(commit=False)
                hw.submitted_at = timezone.now()
                hw.save()
                messages.success(request, "Задание отправлено на проверку.")
                return redirect(
                    reverse("tutor:homework_detail", args=[hw.pk])
                )
        elif action == "grade" and is_owner_teacher:
            grade_form = HomeworkGradeForm(request.POST, instance=hw)
            if grade_form.is_valid():
                hw = grade_form.save(commit=False)
                hw.reviewed_at = timezone.now()
                hw.save()
                messages.success(request, "Оценка выставлена.")
                return redirect(
                    reverse("tutor:homework_detail", args=[hw.pk])
                )

    context = {
        "hw": hw,
        "is_owner_teacher": is_owner_teacher,
        "is_recipient": is_recipient,
        "submit_form": submit_form,
        "grade_form": grade_form,
    }
    return render(request, "tutor/homework_detail.html", context)


# ──────────────────────── Быстрые действия по занятию ────────────────────────

def _post_redirect(request, default_name='tutor:schedule'):
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(reverse(default_name))


def _can_manage_lesson(user, lesson):
    return (
        user == lesson.teacher
        or user.is_superuser
        or user.is_tutor_admin
    )


@login_required
def lesson_toggle_paid(request, pk: int):
    """Переключить статус оплаты в один клик (POST, преподаватель)."""
    lesson = get_object_or_404(Lesson, pk=pk)
    if not _can_manage_lesson(request.user, lesson):
        raise PermissionDenied("Недоступно.")
    if request.method == "POST":
        if lesson.status == Lesson.LessonStatus.CANCELED:
            messages.info(request, "Отменённое занятие нельзя отметить оплаченным.")
            return _post_redirect(request, 'tutor:finances')
        if not lesson.has_ended:
            messages.warning(
                request,
                'Отметить оплату можно только после окончания занятия.',
            )
            return _post_redirect(request, 'tutor:finances')
        if not lesson.is_paid and lesson.hourly_rate is None:
            resolved = resolve_lesson_hourly_rate(lesson, request.user)
            if resolved is not None:
                lesson.hourly_rate = resolved
        lesson.is_paid = not lesson.is_paid
        lesson.save(update_fields=["is_paid", "hourly_rate", "updated_at"])
        messages.success(
            request,
            "Оплата отмечена." if lesson.is_paid else "Отметка оплаты снята.",
        )
    return _post_redirect(request, 'tutor:finances')


@login_required
def lesson_complete(request, pk: int):
    """Отметить занятие проведённым (только POST, для преподавателя)."""
    lesson = get_object_or_404(Lesson, pk=pk)
    if not _can_manage_lesson(request.user, lesson):
        raise PermissionDenied("Недоступно.")
    if request.method == "POST":
        lesson.status = Lesson.LessonStatus.COMPLETED
        lesson.save(update_fields=["status", "updated_at"])
        messages.success(request, "Занятие отмечено как проведённое.")
    return redirect(reverse("tutor:schedule"))


@login_required
def lesson_cancel(request, pk: int):
    """Отменить занятие (статус «Отменено», без удаления)."""
    lesson = get_object_or_404(Lesson, pk=pk)
    if not _can_manage_lesson(request.user, lesson):
        raise PermissionDenied("Недоступно.")
    if request.method == "POST":
        if lesson.status == Lesson.LessonStatus.CANCELED:
            messages.info(request, "Занятие уже отменено.")
        elif lesson.status == Lesson.LessonStatus.COMPLETED:
            messages.warning(
                request, "Проведённое занятие нельзя отменить — только запланированное."
            )
        else:
            lesson.status = Lesson.LessonStatus.CANCELED
            lesson.save(update_fields=["status", "updated_at"])
            messages.success(request, "Занятие отменено.")
    return redirect(reverse("tutor:schedule"))


@login_required
def lesson_delete(request, pk: int):
    """Удалить занятие или всю серию повторов (POST)."""
    lesson = get_object_or_404(Lesson, pk=pk)
    if not _can_manage_lesson(request.user, lesson):
        raise PermissionDenied("Недоступно.")
    if request.method != "POST":
        return redirect(reverse("tutor:schedule"))

    scope = request.POST.get("scope", "single")
    if scope == "series":
        series = lessons_in_series(lesson)
        count = series.count()
        series.delete()
        if count > 1:
            messages.success(request, f"Удалено занятий серии: {count}.")
        else:
            messages.success(request, "Занятие удалено.")
    else:
        lesson.delete()
        messages.success(request, "Занятие удалено.")
    return redirect(reverse("tutor:schedule"))


# ──────────────────────── Привязка учеников ────────────────────────

@login_required
def students_manage(request):
    """Управление учениками преподавателя."""
    if not _is_teacher(request.user):
        raise PermissionDenied("Доступно только преподавателям.")

    teacher = request.user
    available = students_available_to_invite(teacher)
    context = {
        'accepted_student_items': accepted_student_items(teacher),
        'pending_links': TutorStudentLink.objects.filter(
            teacher=teacher,
            status=TutorStudentLink.Status.PENDING,
        ).select_related('student'),
        'available_students': available,
        'invite_cards_json': users_cards_json(
            available,
            default_avatar='/static/img/anonymous_user.png',
        ),
        'default_avatar': '/static/img/anonymous_user.png',
    }
    return render(request, 'tutor/students.html', context)


@login_required
def student_invite(request, student_id: int):
    if request.method != 'POST':
        return redirect(reverse('tutor:students_manage'))
    if not _is_teacher(request.user):
        raise PermissionDenied()

    from users.models import CustomUser
    from .student_links import student_user_q

    student = get_object_or_404(
        CustomUser.objects.filter(student_user_q()),
        pk=student_id,
    )
    if student == request.user:
        messages.error(request, 'Нельзя пригласить самого себя.')
        return redirect(reverse('tutor:students_manage'))

    link, created = TutorStudentLink.objects.get_or_create(
        teacher=request.user,
        student=student,
        defaults={'status': TutorStudentLink.Status.PENDING},
    )
    if not created:
        if link.status == TutorStudentLink.Status.ACCEPTED:
            messages.info(request, 'Этот ученик уже прикреплён к вам.')
        elif link.status == TutorStudentLink.Status.PENDING:
            messages.info(request, 'Приглашение уже отправлено.')
        else:
            link.status = TutorStudentLink.Status.PENDING
            link.responded_at = None
            link.save(update_fields=['status', 'responded_at'])
            messages.success(
                request,
                f'Приглашение отправлено ученику {student.username}.',
            )
    else:
        messages.success(
            request,
            f'Приглашение отправлено ученику {student.username}.',
        )

    next_url = request.POST.get('next', reverse('tutor:students_manage'))
    return redirect(next_url)


@login_required
def student_request_accept(request, pk: int):
    if request.method != 'POST':
        return redirect(reverse('tutor:dashboard'))
    link = get_object_or_404(
        TutorStudentLink,
        pk=pk,
        student=request.user,
        status=TutorStudentLink.Status.PENDING,
    )
    link.status = TutorStudentLink.Status.ACCEPTED
    link.responded_at = timezone.now()
    link.save(update_fields=['status', 'responded_at'])
    if not link.student.is_tutor_student:
        link.student.is_tutor_student = True
        link.student.save(update_fields=['is_tutor_student'])
    messages.success(
        request,
        f'Вы прикреплены к преподавателю '
        f'{link.teacher.get_full_name() or link.teacher.username}.',
    )
    return redirect(reverse('tutor:dashboard'))


@login_required
def student_request_reject(request, pk: int):
    if request.method != 'POST':
        return redirect(reverse('tutor:dashboard'))
    link = get_object_or_404(
        TutorStudentLink,
        pk=pk,
        student=request.user,
        status=TutorStudentLink.Status.PENDING,
    )
    link.status = TutorStudentLink.Status.REJECTED
    link.responded_at = timezone.now()
    link.save(update_fields=['status', 'responded_at'])
    messages.info(request, 'Запрос отклонён.')
    return redirect(reverse('tutor:dashboard'))


@login_required
def student_unlink(request, link_id: int):
    if request.method != 'POST':
        return redirect(reverse('tutor:students_manage'))
    link = get_object_or_404(TutorStudentLink, pk=link_id)
    if request.user != link.teacher and not request.user.is_superuser:
        raise PermissionDenied()
    if link.status != TutorStudentLink.Status.ACCEPTED:
        messages.info(request, 'Приглашение отменено.')
    else:
        messages.info(request, 'Ученик откреплён.')
    link.delete()
    return redirect(reverse('tutor:students_manage'))


@login_required
def student_set_rate(request, link_id: int):
    if request.method != 'POST':
        return redirect(reverse('tutor:students_manage'))
    if not _is_teacher(request.user):
        raise PermissionDenied()

    link = get_object_or_404(
        TutorStudentLink,
        pk=link_id,
        teacher=request.user,
        status=TutorStudentLink.Status.ACCEPTED,
    )
    form = StudentHourlyRateForm(
        request.POST, instance=link, teacher=request.user
    )
    if form.is_valid():
        form.save()
        messages.success(
            request,
            f'Ставка для {link.student.username} сохранена.',
        )
    else:
        messages.error(request, 'Укажите корректную стоимость часа.')
    next_url = request.POST.get('next', reverse('tutor:students_manage'))
    return redirect(next_url)
