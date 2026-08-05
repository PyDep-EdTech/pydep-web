from django.urls import reverse

from .models import Lesson


def lessons_unpaid_count(qs):
    return qs.filter(
        Lesson.ended_q(),
        is_paid=False,
    ).exclude(
        status=Lesson.LessonStatus.CANCELED,
    ).count()


def lesson_calendar_events(qs, *, can_edit=False):
    """Сериализация занятий для клиентского календаря."""
    events = []
    for lesson in qs:
        person = ""
        if can_edit:
            if lesson.student:
                person = (
                    lesson.student.get_full_name() or lesson.student.username
                )
        else:
            person = (
                lesson.teacher.get_full_name() or lesson.teacher.username
            )
        events.append({
            "id": lesson.pk,
            "date": lesson.date.isoformat(),
            "start": lesson.start_time.strftime("%H:%M"),
            "end": lesson.end_time.strftime("%H:%M"),
            "title": lesson.subject,
            "person": person,
            "status": lesson.status,
            "statusLabel": lesson.get_status_display(),
            "format": lesson.get_lesson_format_display(),
            "isPaid": lesson.is_paid,
            "hasEnded": lesson.has_ended,
            "isCanceled": lesson.status == Lesson.LessonStatus.CANCELED,
            "totalCost": (
                str(lesson.total_cost) if lesson.total_cost is not None else None
            ),
            "homeworkUrl": (
                reverse("tutor:lesson_update", args=[lesson.pk]) + "#homework"
                if can_edit and lesson.student_id else None
            ),
            "editUrl": (
                reverse("tutor:lesson_update", args=[lesson.pk])
                if can_edit else None
            ),
        })
    return events
