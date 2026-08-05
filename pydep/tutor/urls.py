from django.urls import path

from .views import my_tutor
from .views import dashboard, finances
from .views import projectbox, projectbox_file_access
from .views import profile
from .views import schedule
from .views import lesson_create, lesson_update, lesson_payment_toggle
from .views import lesson_toggle_paid, lesson_complete, lesson_cancel, lesson_delete
from .views import homework_list, homework_create, homework_detail
from .views import (
    students_manage,
    student_invite,
    student_request_accept,
    student_request_reject,
    student_unlink,
    student_set_rate,
)

app_name = 'tutor'

urlpatterns = [
    path('', my_tutor, name='my_tutor'),
    path('dashboard/', dashboard, name='dashboard'),
    path('finances/', finances, name='finances'),
    path('projectbox/', projectbox, name='projectbox'),
    path(
        'projectbox/<int:pk>/access/',
        projectbox_file_access,
        name='projectbox_file_access',
    ),
    path('profile/', profile, name='profile'),
    path('schedule/', schedule, name='schedule'),
    path('lessons/new/', lesson_create, name='lesson_create'),
    path('lessons/<int:pk>/edit/', lesson_update, name='lesson_update'),
    path(
        'lessons/<int:pk>/payment/',
        lesson_payment_toggle,
        name='lesson_payment'
    ),
    path('lessons/<int:pk>/pay/', lesson_toggle_paid, name='lesson_pay'),
    path(
        'lessons/<int:pk>/cancel/',
        lesson_cancel,
        name='lesson_cancel',
    ),
    path(
        'lessons/<int:pk>/delete/',
        lesson_delete,
        name='lesson_delete',
    ),
    path(
        'lessons/<int:pk>/complete/',
        lesson_complete,
        name='lesson_complete',
    ),
    path('homework/', homework_list, name='homework_list'),
    path('homework/new/', homework_create, name='homework_create'),
    path('homework/<int:pk>/', homework_detail, name='homework_detail'),
    path('students/', students_manage, name='students_manage'),
    path(
        'students/invite/<int:student_id>/',
        student_invite,
        name='student_invite',
    ),
    path(
        'students/requests/<int:pk>/accept/',
        student_request_accept,
        name='student_request_accept',
    ),
    path(
        'students/requests/<int:pk>/reject/',
        student_request_reject,
        name='student_request_reject',
    ),
    path(
        'students/links/<int:link_id>/rate/',
        student_set_rate,
        name='student_set_rate',
    ),
    path(
        'students/links/<int:link_id>/unlink/',
        student_unlink,
        name='student_unlink',
    ),
]
