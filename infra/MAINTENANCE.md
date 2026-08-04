# Страница технических работ (maintenance)

Статическая страница `infra/nginx/maintenance.html` показывается посетителям,
когда основной сайт недоступен или когда вы вручную включили режим техработ.

## Что уже настроено

1. Страница в стиле главной PyDep с окном IDE и анимацией печатающегося кода.
2. Nginx отдаёт её автоматически при ошибках бэкенда **502 / 503 / 504**
   (Django/Gunicorn не отвечает).
3. Можно включить вручную на время деплоя или обновлений.

## Как включить вручную (Docker)

Из каталога `infra/`:

```bash
# Включить режим техработ
touch nginx/maintenance.on
docker compose exec nginx nginx -s reload
```

После этого любой запрос к сайту получит **HTTP 503** и страницу
«Ведутся технические работы».

## Как выключить

```bash
rm nginx/maintenance.on
docker compose exec nginx nginx -s reload
```

Файл-флаг `nginx/maintenance.on` примонтирован в контейнер как
`/etc/nginx/maintenance-flag/maintenance.on` (см. `docker-compose.yml`).

## Проверка без деплоя

Откройте файл локально в браузере:

```text
infra/nginx/maintenance.html
```

Или отдайте его любым статическим сервером:

```bash
cd infra/nginx && python3 -m http.server 8080
# http://localhost:8080/maintenance.html
```

## Поведение при падении Django

Даже без флага `maintenance.on`, если контейнер `web` недоступен,
nginx перехватит 502/503/504 и покажет ту же страницу.
