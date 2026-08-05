def accepted_student_items(teacher):
    """Прикреплённые ученики с формой ставки и счётчиком занятий."""
    from django.db.models import Count, Q

    from .forms import StudentHourlyRateForm
    from .models import TutorStudentLink

    links = (
        TutorStudentLink.objects.filter(
            teacher=teacher,
            status=TutorStudentLink.Status.ACCEPTED,
        )
        .select_related("student")
        .annotate(
            lessons_count=Count(
                "student__lessons_as_student",
                filter=Q(student__lessons_as_student__teacher=teacher),
                distinct=True,
            ),
        )
        .order_by("student__first_name", "student__username")
    )
    return [
        {
            "link": link,
            "rate_form": StudentHourlyRateForm(instance=link, teacher=teacher),
            "lessons_count": link.lessons_count,
        }
        for link in links
    ]
