from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CourseReadSerializer
from lesson.models import Course


class CourseListView(APIView):
    """Список опубликованных курсов (read-only)."""

    def get(self, request):
        courses = Course.objects.filter(is_published=True)
        serializer = CourseReadSerializer(courses, many=True)
        return Response(serializer.data)
