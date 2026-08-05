from django.core.exceptions import PermissionDenied

from lesson.models import Course, Module, Lesson


def can_edit_course(user, course):
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return course.authors.filter(pk=user.pk).exists()


def can_edit_module(user, module):
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return module.authors.filter(pk=user.pk).exists()


def can_edit_lesson(user, lesson):
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return lesson.authors.filter(pk=user.pk).exists()


def require_course_edit(user, course):
    if not can_edit_course(user, course):
        raise PermissionDenied("Нет доступа к редактированию курса.")


def require_module_edit(user, module):
    if not can_edit_module(user, module):
        raise PermissionDenied("Нет доступа к редактированию модуля.")


def require_lesson_edit(user, lesson):
    if not can_edit_lesson(user, lesson):
        raise PermissionDenied("Нет доступа к редактированию урока.")
