# Режим технических работ PyDep
#
# Страница на сервере: /etc/templates/index.html
# В контейнер nginx монтируется: /etc/templates:/etc/templates:ro
#
# ── Автоматически (Django/gunicorn недоступен) ──
# nginx отдаёт index.html при ошибках 502, 503, 504.
#
# ── Вручную ──
#   touch /etc/templates/enabled
#   docker compose exec nginx nginx -s reload
#
# Выключить:
#   rm /etc/templates/enabled
#   docker compose exec nginx nginx -s reload
#
# Проверка:
#   curl -I https://pydep.ru/   → HTTP/2 503 + Retry-After
#
# Проверка внутри контейнера (файл обязан существовать):
#   docker compose exec nginx ls -la /etc/templates/index.html
#
# Если «No such file» — на хосте:
#   ls -la /etc/templates/index.html
#   docker compose up -d nginx
# После правок скопируйте на сервер:
#   cp infra/maintenance/index.html /etc/templates/index.html
