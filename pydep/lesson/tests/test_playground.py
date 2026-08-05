import json

import pytest
from django.urls import reverse

from lesson.models import Lesson
from lesson.models import PracticeTask
from lesson.views import normalize_playground_output


@pytest.mark.django_db
class TestPlaygroundCheck:
    def test_normalize_output_matches_js(self):
        assert normalize_playground_output("a  \r\nb\n\n") == "a\nb"

    def test_check_ok(self, client):
        lesson = Lesson.objects.create(title="L", description="D")
        task = PracticeTask.objects.create(
            lesson=lesson,
            title="T",
            statement="S",
            expected_output="hello\n",
        )
        url = reverse("lesson:python_playground_check")
        resp = client.post(
            url,
            data=json.dumps({"task_id": task.id, "output": "hello\n"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert "expected" not in data

    def test_check_fail_returns_expected(self, client):
        lesson = Lesson.objects.create(title="L", description="D")
        task = PracticeTask.objects.create(
            lesson=lesson,
            title="T",
            statement="S",
            expected_output="42",
        )
        url = reverse("lesson:python_playground_check")
        resp = client.post(
            url,
            data=json.dumps({"task_id": task.id, "output": "41"}),
            content_type="application/json",
        )
        data = resp.json()
        assert data["ok"] is False
        assert data["expected"] == "42"
        assert data["got"] == "41"

    def test_check_unknown_task(self, client):
        url = reverse("lesson:python_playground_check")
        resp = client.post(
            url,
            data=json.dumps({"task_id": 99999, "output": "x"}),
            content_type="application/json",
        )
        assert resp.status_code == 404


@pytest.mark.django_db
class TestPlaygroundPage:
    def test_tasks_json_without_expected(self, client):
        lesson = Lesson.objects.create(title="L", description="D")
        PracticeTask.objects.create(
            lesson=lesson,
            title="T",
            statement="S",
            starter_code="print(1)",
            expected_output="1",
        )
        url = reverse("lesson:python_playground") + f"?lesson={lesson.id}"
        resp = client.get(url)
        assert resp.status_code == 200
        assert '"expected"' not in resp.content.decode()
        assert "python/runner/" in resp.content.decode()

    def test_runner_page(self, client):
        url = reverse("lesson:python_playground_runner")
        resp = client.get(url)
        assert resp.status_code == 200
        assert "python-playground-runner.js" in resp.content.decode()
