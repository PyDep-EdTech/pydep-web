from django.contrib import admin

from .models import Course
from .models import ModulesInCourse
from .models import Lesson
from .models import Module
from .models import LessonsInModule
from .models import Category
from .models import UserLessonProgress
from .models import Cohort
from .models import CourseEnrollment
from django.utils import timezone


class ModulesInCourseInline(admin.TabularInline):
    model = ModulesInCourse
    extra = 1
    min_num = 1


class LessonsInModuleInline(admin.TabularInline):
    model = LessonsInModule
    extra = 1
    min_num = 1


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    min_num = 1


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    inlines = (LessonsInModuleInline,)
    list_display = (
        'title',
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [ModulesInCourseInline,]
    list_display = (
        "pk",
        'name',
    )


# @admin.register(ModulesInCourse)
# class LessonInCourseAdmin(admin.ModelAdmin):
#     list_display = (
#         'module',
#         'course',
#     )


class PracticeTaskInline(admin.StackedInline):
    from .models import PracticeTask as _PT
    model = _PT
    extra = 0
    fields = ("position", "title", "statement", "starter_code", "expected_output")
    ordering = ("position", "id")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "pk", 'title',
    )
    search_fields = ("title",)
    inlines = [PracticeTaskInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "module", "lesson", "completed", "current",)


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ("pk", "course", "start_date")


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "user", "course", "status", "enrolled_at", "decided_at", "decided_by",
    )
    list_filter = ("status",)
    search_fields = ("user__username", "course__name")
    autocomplete_fields = ()
    actions = ("approve_selected", "reject_selected")

    @admin.action(description="Одобрить выбранные заявки")
    def approve_selected(self, request, queryset):
        updated = queryset.update(
            status=CourseEnrollment.Status.APPROVED,
            decided_at=timezone.now(),
            decided_by=request.user,
        )
        self.message_user(request, f"Одобрено заявок: {updated}.")

    @admin.action(description="Отклонить выбранные заявки")
    def reject_selected(self, request, queryset):
        updated = queryset.update(
            status=CourseEnrollment.Status.REJECTED,
            decided_at=timezone.now(),
            decided_by=request.user,
        )
        self.message_user(request, f"Отклонено заявок: {updated}.")


from .models import PracticeTask


@admin.register(PracticeTask)
class PracticeTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson", "position", "has_check", "created_by")
    list_filter = ("lesson",)
    search_fields = ("title", "statement")
    list_editable = ("position",)
    autocomplete_fields = ("lesson",)

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
