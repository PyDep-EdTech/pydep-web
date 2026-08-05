from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls import include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('tutor/', include('tutor.urls', namespace='tutor')),
    path('', include('lesson.urls', namespace='lesson')),
    path("studio/", include("course_editor.urls", namespace="studio")),
    path('', include('users.urls', namespace='users')),
    path("api/", include("api.urls", namespace="api")),
]

urlpatterns += [
    path(
        "ckeditor5/",
        include('django_ckeditor_5.urls'),
        name="ck_editor_5_upload_file"
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'lesson.views.page_not_found'
handler500 = 'lesson.views.server_error'
handler403 = 'lesson.views.permission_denied_page'
