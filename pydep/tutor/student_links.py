from django.db.models import Q

from users.models import CustomUser

from .models import TutorStudentLink


def student_user_q():
    return Q(is_student=True) | Q(is_tutor_student=True)


def accepted_students_for_teacher(teacher):
    """Ученики, подтвердившие привязку к преподавателю."""
    return CustomUser.objects.filter(
        tutor_student_links_as_student__teacher=teacher,
        tutor_student_links_as_student__status=TutorStudentLink.Status.ACCEPTED,
    ).distinct().order_by("first_name", "username")


def students_available_to_invite(teacher):
    """Пользователи, которых преподаватель ещё может пригласить."""
    linked_ids = TutorStudentLink.objects.filter(
        teacher=teacher,
        status__in=(
            TutorStudentLink.Status.PENDING,
            TutorStudentLink.Status.ACCEPTED,
        ),
    ).values_list("student_id", flat=True)
    return CustomUser.objects.filter(
        student_user_q(),
    ).exclude(
        pk=teacher.pk,
    ).exclude(
        pk__in=linked_ids,
    ).order_by("first_name", "username")


def user_card_data(user):
    """Данные пользователя для карточки в UI."""
    return {
        "id": user.pk,
        "username": user.username,
        "full_name": user.get_full_name().strip() or user.username,
        "avatar_url": user.image.url if user.image else None,
    }


def users_cards_json(users, default_avatar=""):
    import json

    cards = []
    for u in users:
        data = user_card_data(u)
        if not data["avatar_url"]:
            data["avatar_url"] = default_avatar
        cards.append(data)
    return json.dumps(cards, ensure_ascii=False)


def is_student_linked(teacher, student):
    return TutorStudentLink.objects.filter(
        teacher=teacher,
        student=student,
        status=TutorStudentLink.Status.ACCEPTED,
    ).exists()
