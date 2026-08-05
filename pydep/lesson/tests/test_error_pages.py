import pytest
from django.test import RequestFactory
from django.test import override_settings

from lesson.views import page_not_found
from lesson.views import permission_denied_page
from lesson.views import server_error


@pytest.mark.django_db
@override_settings(DEBUG=False)
class TestErrorPages:
    def test_404_page(self, client):
        resp = client.get('/no-such-page-here/')
        assert resp.status_code == 404
        assert 'Страница не найдена' in resp.content.decode()

    def test_404_handler(self):
        request = RequestFactory().get('/missing/')
        resp = page_not_found(request, exception=None)
        assert resp.status_code == 404

    def test_500_handler(self):
        request = RequestFactory().get('/')
        resp = server_error(request)
        assert resp.status_code == 500
        assert 'Что-то пошло не так' in resp.content.decode()

    def test_403_handler(self):
        request = RequestFactory().get('/forbidden/')
        resp = permission_denied_page(request, exception=None)
        assert resp.status_code == 403
        assert 'Доступ закрыт' in resp.content.decode()
