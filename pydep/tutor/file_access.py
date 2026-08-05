from django.db.models import Q

from users.models import CustomUser

from .student_links import accepted_students_for_teacher, users_cards_json


def file_access_user_queryset(actor):
    """Пользователи, которых можно указать в тонкой настройке доступа к файлу."""
    base = CustomUser.objects.filter(is_active=True)
    if actor.is_superuser or actor.is_tutor_admin:
        return base.order_by("first_name", "last_name", "username")
    if actor.is_teacher:
        student_ids = accepted_students_for_teacher(actor).values_list("pk", flat=True)
        return base.filter(
            Q(pk__in=student_ids) | Q(pk=actor.pk)
        ).distinct().order_by("first_name", "last_name", "username")
    return CustomUser.objects.none()


def file_access_users_cards_json(actor, default_avatar=""):
    return users_cards_json(file_access_user_queryset(actor), default_avatar)


def can_manage_project_file(user, file_obj) -> bool:
    if user.is_superuser or user.is_tutor_admin:
        return True
    if not user.is_teacher:
        return False
    return file_obj.uploaded_by_id in (None, user.pk)
