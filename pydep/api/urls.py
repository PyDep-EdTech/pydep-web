from django.urls import path

from .views import CourseListView

app_name = "api"

urlpatterns = [
    path("courses/", CourseListView.as_view(), name="api"),
]
