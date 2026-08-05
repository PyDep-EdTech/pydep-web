from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.db.models import Q

from .models import Lesson, TutorStudentLink


def duration_minutes_between(start_time, end_time):
    """Минуты между началом и окончанием (0, если интервал некорректен)."""
    start_mins = start_time.hour * 60 + start_time.minute
    end_mins = end_time.hour * 60 + end_time.minute
    if end_mins <= start_mins:
        return 0
    return end_mins - start_mins


def format_duration_minutes(minutes: int) -> str | None:
    """Человекочитаемая длительность: «1 ч 30 мин»."""
    if minutes <= 0:
        return None
    hours, mins = divmod(minutes, 60)
    parts = []
    if hours:
        parts.append(f"{hours} ч")
    if mins:
        parts.append(f"{mins} мин")
    return " ".join(parts) if parts else "0 мин"


def lesson_duration_hours(lesson):
    """Длительность занятия в часах (дробное число)."""
    mins = duration_minutes_between(lesson.start_time, lesson.end_time)
    return Decimal(mins) / Decimal("60")


def effective_hourly_rate(lesson):
    """Ставка занятия: сначала с урока, иначе из привязки ученика."""
    if lesson.hourly_rate is not None:
        return lesson.hourly_rate
    if not lesson.student_id or not lesson.teacher_id:
        return None
    link = TutorStudentLink.objects.filter(
        teacher_id=lesson.teacher_id,
        student_id=lesson.student_id,
        status=TutorStudentLink.Status.ACCEPTED,
    ).first()
    if link and link.hourly_rate is not None:
        return link.hourly_rate
    return None


def lesson_total_cost(lesson):
    """Стоимость занятия или None, если не начисляется."""
    if lesson.status == Lesson.LessonStatus.CANCELED:
        return None
    rate = effective_hourly_rate(lesson)
    if rate is None:
        return None
    hours = lesson_duration_hours(lesson)
    if hours <= 0:
        return None
    return (rate * hours).quantize(Decimal("0.01"))


def billable_lessons_q():
    """Занятия, по которым может начисляться оплата."""
    return Q(status__in=(
        Lesson.LessonStatus.SCHEDULED,
        Lesson.LessonStatus.COMPLETED,
    ))


def resolve_lesson_hourly_rate(lesson, teacher, explicit_rate=None):
    """Подставить ставку: явная → из привязки ученика."""
    if explicit_rate not in (None, ""):
        return explicit_rate
    if lesson.hourly_rate is not None:
        return lesson.hourly_rate
    if not lesson.student_id:
        return None
    link = TutorStudentLink.objects.filter(
        teacher=teacher,
        student_id=lesson.student_id,
        status=TutorStudentLink.Status.ACCEPTED,
    ).first()
    if link and link.hourly_rate is not None:
        return link.hourly_rate
    return None


def _month_bounds(year: int, month: int):
    last_day = monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def student_debt_summary(student):
    """Задолженность ученика по завершённым неоплаченным занятиям."""
    qs = Lesson.objects.filter(
        student=student,
        is_paid=False,
    ).filter(
        Lesson.ended_q(),
        billable_lessons_q(),
    ).select_related("teacher")

    total = Decimal("0")
    items = []
    for lesson in qs:
        cost = lesson_total_cost(lesson)
        if cost is None or cost <= 0:
            continue
        total += cost
        items.append({"lesson": lesson, "cost": cost})

    return {
        "total": total.quantize(Decimal("0.01")),
        "count": len(items),
        "items": items,
    }


def teacher_income_summary(teacher, year: int, month: int):
    """Сводка дохода преподавателя за выбранный месяц."""
    month_start, month_end = _month_bounds(year, month)
    base = Lesson.objects.filter(
        teacher=teacher,
        date__gte=month_start,
        date__lte=month_end,
    )

    paid_total = Decimal("0")
    unpaid_total = Decimal("0")
    canceled_count = 0
    scheduled_count = 0
    completed_count = 0
    no_rate_count = 0
    paid_count = 0
    paid_items = []

    for lesson in base.select_related("student"):
        if lesson.status == Lesson.LessonStatus.CANCELED:
            canceled_count += 1
            continue
        if lesson.status == Lesson.LessonStatus.SCHEDULED:
            scheduled_count += 1
        if lesson.status == Lesson.LessonStatus.COMPLETED:
            completed_count += 1

        cost = lesson_total_cost(lesson)
        if lesson.is_paid:
            paid_count += 1
            if cost is not None:
                paid_total += cost
                paid_items.append({"lesson": lesson, "cost": cost})
            elif lesson.has_ended:
                no_rate_count += 1
            continue

        if cost is None:
            if lesson.has_ended:
                no_rate_count += 1
            continue

        if lesson.has_ended:
            unpaid_total += cost

    return {
        "year": year,
        "month": month,
        "month_start": month_start,
        "month_end": month_end,
        "paid_total": paid_total.quantize(Decimal("0.01")),
        "unpaid_total": unpaid_total.quantize(Decimal("0.01")),
        "expected_total": (paid_total + unpaid_total).quantize(Decimal("0.01")),
        "paid_count": paid_count,
        "paid_items": paid_items,
        "canceled_count": canceled_count,
        "scheduled_count": scheduled_count,
        "completed_count": completed_count,
        "no_rate_count": no_rate_count,
        "lessons_count": base.count(),
    }


def student_hourly_rates_for_teacher(teacher):
    """Словарь student_id → ставка для автоподстановки в форме занятия."""
    links = TutorStudentLink.objects.filter(
        teacher=teacher,
        status=TutorStudentLink.Status.ACCEPTED,
        hourly_rate__isnull=False,
    ).values_list("student_id", "hourly_rate")
    return {str(sid): str(rate) for sid, rate in links}
