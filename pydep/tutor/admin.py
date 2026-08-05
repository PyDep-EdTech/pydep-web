from django.contrib import admin

from .models import FilesProject
from .models import Lesson
from .models import Homework
from .models import TutorStudentLink


@admin.register(FilesProject)
class FilesProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "access_group", "uploaded_by", "created_at")
    list_filter = ("access_group",)
    search_fields = ("name",)
    filter_horizontal = ("allowed_users",)


@admin.register(TutorStudentLink)
class TutorStudentLinkAdmin(admin.ModelAdmin):
    list_display = (
        "teacher", "student", "status", "hourly_rate", "created_at", "responded_at",
    )
    list_filter = ("status",)
    search_fields = ("teacher__username", "student__username")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        'subject', 'teacher', 'student', 'date', 'status', 'hourly_rate', 'is_paid',
    )
    list_filter = ('status', 'is_paid', 'lesson_format')
    search_fields = ('subject',)
    date_hierarchy = 'date'


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'due_date', 'submitted_at', 'grade')
    list_filter = ('grade',)
    search_fields = ('title',)
