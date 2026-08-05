from django.urls import path

from .views import course_detail
from .views import course_search_api
from .views import courses_list
from .views import index
from .views import python_playground
from .views import python_playground_check
from .views import python_playground_runner
from .views import lesson_detail
from .views import profile
from .views import module_detail
from .views import profile_edit
from .views import category_detail
from .views import complete_lesson
from .views import enrollment_requests
from .views import enrollment_decide
# from .views import lesson_edit
# from .views import lesson_create
# from .views import upload_image
from .views import course_editor

app_name = 'lesson'

urlpatterns = [
    path(
        '',
        index,
        name='index'
    ),
    path(
        'profile/',
        profile,
        name='profile'
    ),
    path(
        'profile/edit/',
        profile_edit,
        name='profile_edit'
    ),
    path(
        'courses/',
        courses_list,
        name='courses'
    ),
    path(
        'python/',
        python_playground,
        name='python_playground'
    ),
    path(
        'python/runner/',
        python_playground_runner,
        name='python_playground_runner'
    ),
    path(
        'python/check/',
        python_playground_check,
        name='python_playground_check'
    ),
    path(
        'courses/search/',
        course_search_api,
        name='course_search'
    ),
    path(
        'enrollment-requests/',
        enrollment_requests,
        name='enrollment_requests'
    ),
    path(
        'enrollment-requests/<int:pk>/<str:decision>/',
        enrollment_decide,
        name='enrollment_decide'
    ),
    path(
        'course/<slug:course_slug>/',
        course_detail,
        name='course_detail'
    ),
    path(
        "courses/<str:slug>",
        category_detail,
        name="category"
    ),
    path(
        'course/<slug:course_slug>/<slug:module_slug>/',
        module_detail,
        name='module_detail'),
    path(
        'course/<slug:course_slug>/<slug:module_slug>/<slug:lesson_slug>/',
        lesson_detail,
        name='lesson_detail'
    ),
    path(
        'course/<slug:course_slug>/<slug:module_slug>/<slug:lesson_slug>/complete/',
        complete_lesson,
        name='complete_lesson'
    ),
    # path(
    #     'lesson/create/',
    #     lesson_create,
    #     name='lesson_create'
    # ),
    # path(
    #     'lesson/<int:lesson_id>/edit/',
    #     lesson_edit,
    #     name='lesson_edit'
    # ),
    # path(
    #     'upload-image/',
    #     upload_image,
    #     name='upload_image'
    # ),
]
