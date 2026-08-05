"""Данные для наполнения БД учебными курсами."""

from lesson.seed_data.blocks import (
    IMG,
    code,
    delimiter,
    header,
    image,
    list_block,
    paragraph,
    quote,
)
from lesson.seed_data.light_python import LIGHT_PYTHON_COURSE

COURSE_IMAGES = {
    "python": "courses/seed/course-python.png",
    "django": "courses/seed/course-django.png",
    "javascript": "courses/seed/course-javascript.png",
    "sql": "courses/seed/course-sql.png",
    "git": "courses/seed/course-git.png",
    "html": "courses/seed/course-html-css.png",
    "algorithms": "courses/seed/course-algorithms.png",
    "docker": "courses/seed/course-docker.png",
}

# Обложки модулей по курсу (3 модуля на курс)
COURSE_MODULE_IMAGES = {
    "Основы Python": [
        "lessons/seed/lesson-terminal.png",
        "lessons/seed/lesson-flowchart.png",
        "lessons/seed/lesson-python-types.png",
    ],
    "Веб на Django": [
        "lessons/seed/lesson-django-mvt.png",
        "lessons/seed/lesson-database.png",
        "lessons/seed/lesson-dom-browser.png",
    ],
    "JavaScript с нуля": [
        "lessons/seed/javascript-logo.svg",
        "lessons/seed/lesson-dom-browser.png",
        "lessons/seed/lesson-async-js.png",
    ],
    "SQL для разработчика": [
        "lessons/seed/postgresql-logo.svg",
        "lessons/seed/lesson-sql-join.png",
        "lessons/seed/lesson-database.png",
    ],
    "Git: версии и ветки": [
        "lessons/seed/git-logo.svg",
        "lessons/seed/lesson-git-branching.png",
        "lessons/seed/github-logo.svg",
    ],
    "HTML и CSS": [
        "lessons/seed/html5-logo.svg",
        "lessons/seed/lesson-flexbox.png",
        "lessons/seed/lesson-css-grid.png",
    ],
    "Алгоритмы и структуры": [
        "lessons/seed/lesson-big-o.png",
        "lessons/seed/lesson-stack-queue.png",
        "lessons/seed/lesson-binary-search.png",
    ],
    "Docker: контейнеры": [
        "lessons/seed/docker-logo.svg",
        "lessons/seed/lesson-docker-compose.png",
        "lessons/seed/linux-logo.svg",
    ],
    'Такой "лёгкий" Python': [
        "lessons/seed/python-logo.svg",
        "lessons/seed/lesson-flowchart.svg",
        "lessons/seed/python-logo.svg",
        "lessons/seed/vscode-logo.svg",
        "lessons/seed/github-logo.svg",
        "lessons/seed/python-logo.svg",
    ],
}

CATEGORIES = [
    "Программирование",
    "Веб-разработка",
    "Базы данных",
    "DevOps",
    "Алгоритмы",
]

COURSES = [
    # ── 1. Основы Python ──────────────────────────────────────────────
    {
        "name": "Основы Python",
        "description": (
            "Полный вводный курс по Python 3: от установки интерпретатора "
            "до написания первых программ. Изучите переменные, типы данных, "
            "условия, циклы, функции и работу с файлами."
        ),
        "price": 4900,
        "image": COURSE_IMAGES["python"],
        "duration": 4,
        "level": "С нуля",
        "category": "Программирование",
        "programming_language": "Python",
        "modules": [
            {
                "title": "Python: Введение и синтаксис",
                "description": "Установка Python, REPL, базовый синтаксис и PEP 8.",
                "lessons": [
                    {
                        "title": "Что такое Python и зачем его учить",
                        "blocks": [
                            header("Язык Python", 2),
                            paragraph(
                                "Python — интерпретируемый язык высокого уровня, созданный "
                                "Гвидо ван Россумом в 1991 году. Сегодня он применяется в "
                                "веб-разработке, анализе данных, машинном обучении, "
                                "автоматизации и научных вычислениях."
                            ),
                            image(IMG["python"], "Логотип Python"),
                            list_block([
                                "Простой и читаемый синтаксис — код похож на псевдокод",
                                "Огромная экосистема библиотек (pip install ...)",
                                "Кроссплатформенность: Windows, macOS, Linux",
                                "Активное сообщество и обширная документация",
                            ]),
                            quote(
                                "Красота лучше уродства. Явное лучше неявного.",
                                "Дзен Python (PEP 20)",
                            ),
                            header("Установка", 3),
                            paragraph(
                                "Скачайте Python 3.12+ с python.org. При установке "
                                "на Windows обязательно отметьте «Add Python to PATH». "
                                "Проверьте установку в терминале:"
                            ),
                            code("python3 --version\n# Python 3.12.4"),
                            image(IMG["terminal"], "Терминал — основной инструмент разработчика"),
                        ],
                    },
                    {
                        "title": "Переменные и типы данных",
                        "blocks": [
                            header("Переменные", 2),
                            paragraph(
                                "Переменная — именованная область памяти. В Python не нужно "
                                "указывать тип явно: интерпретатор определяет его автоматически."
                            ),
                            code("name = 'Анна'       # str\n"
                                "age = 25            # int\n"
                                "height = 1.68       # float\n"
                                "is_student = True   # bool\n"
                                "print(type(name))   # <class 'str'>"),
                            image(IMG["python_types"], "Основные типы данных в Python"),
                            header("Основные типы", 3),
                            list_block([
                                "int — целые числа: 42, -7, 0",
                                "float — дробные: 3.14, -0.5",
                                "str — строки: 'Привет', \"Мир\"",
                                "bool — логические: True, False",
                                "None — отсутствие значения",
                            ], ordered=True),
                            paragraph(
                                "Функция type() показывает тип переменной. "
                                "Преобразование типов: int('42'), str(100), float('3.14')."
                            ),
                            code("x = input('Введите число: ')\nprint(int(x) * 2)"),
                            delimiter(),
                            paragraph(
                                "Правило именования: snake_case для переменных "
                                "(user_name, total_price). Имена чувствительны к регистру."
                            ),
                        ],
                    },
                    {
                        "title": "Операторы и ввод-вывод",
                        "blocks": [
                            header("Арифметические операторы", 2),
                            code(
                                "a, b = 10, 3\n"
                                "print(a + b)   # 13  сложение\n"
                                "print(a - b)   # 7   вычитание\n"
                                "print(a * b)   # 30  умножение\n"
                                "print(a / b)   # 3.333... деление\n"
                                "print(a // b)  # 3   целочисленное деление\n"
                                "print(a % b)   # 1   остаток\n"
                                "print(a ** b)  # 1000 возведение в степень"
                            ),
                            header("Строки и f-строки", 3),
                            paragraph(
                                "f-строки (форматированные строки) — самый удобный способ "
                                "вставки переменных в текст с Python 3.6+."
                            ),
                            code(
                                "name = 'Мария'\n"
                                "score = 95\n"
                                "msg = f'Студент {name} набрал {score} баллов'\n"
                                "print(msg)"
                            ),
                            list_block([
                                "print() — вывод на экран",
                                "input() — чтение строки с клавиатуры",
                                "len() — длина строки или коллекции",
                                "round() — округление числа",
                            ]),
                        ],
                    },
                ],
            },
            {
                "title": "Python: Условия и циклы",
                "description": "Ветвление if/elif/else, циклы for и while, break/continue.",
                "lessons": [
                    {
                        "title": "Условные конструкции if",
                        "blocks": [
                            header("Ветвление if / elif / else", 2),
                            paragraph(
                                "Условные операторы позволяют выполнять разный код "
                                "в зависимости от истинности выражения."
                            ),
                            image(IMG["flowchart"], "Блок-схема условного оператора"),
                            code(
                                "temperature = 28\n\n"
                                "if temperature > 30:\n"
                                "    print('Жарко!')\n"
                                "elif temperature > 20:\n"
                                "    print('Тепло')\n"
                                "else:\n"
                                "    print('Прохладно')"
                            ),
                            header("Операторы сравнения и логики", 3),
                            list_block([
                                "== равно, != не равно, > < >= <=",
                                "and — логическое И, or — ИЛИ, not — НЕ",
                                "in — проверка вхождения: 'py' in 'python'",
                            ]),
                            code(
                                "age = 20\n"
                                "has_ticket = True\n"
                                "if age >= 18 and has_ticket:\n"
                                "    print('Добро пожаловать!')"
                            ),
                        ],
                    },
                    {
                        "title": "Цикл for и итерация",
                        "blocks": [
                            header("Цикл for", 2),
                            paragraph(
                                "Цикл for перебирает элементы итерируемого объекта: "
                                "список, строку, range, словарь."
                            ),
                            code(
                                "fruits = ['яблоко', 'груша', 'слива']\n"
                                "for fruit in fruits:\n"
                                "    print(f'Мне нравится {fruit}')\n\n"
                                "for i in range(5):\n"
                                "    print(i)  # 0, 1, 2, 3, 4"
                            ),
                            header("Функция range()", 3),
                            paragraph(
                                "range(start, stop, step) генерирует последовательность "
                                "целых чисел. stop не включается."
                            ),
                            code(
                                "for i in range(2, 11, 2):\n"
                                "    print(i)  # 2, 4, 6, 8, 10\n\n"
                                "for index, value in enumerate(fruits):\n"
                                "    print(index, value)"
                            ),
                        ],
                    },
                    {
                        "title": "Цикл while и управление потоком",
                        "blocks": [
                            header("Цикл while", 2),
                            code(
                                "count = 0\n"
                                "while count < 5:\n"
                                "    print(f'Счётчик: {count}')\n"
                                "    count += 1"
                            ),
                            paragraph(
                                "break прерывает цикл, continue переходит к следующей "
                                "итерации. else у цикла выполняется, если цикл завершился "
                                "без break."
                            ),
                            code(
                                "password = ''\n"
                                "attempts = 0\n"
                                "while password != 'secret' and attempts < 3:\n"
                                "    password = input('Пароль: ')\n"
                                "    attempts += 1\n"
                                "else:\n"
                                "    if password == 'secret':\n"
                                "        print('Доступ разрешён')"
                            ),
                            list_block([
                                "Избегайте бесконечных циклов — всегда меняйте условие",
                                "while True + break — паттерн для меню",
                                "Вложенные циклы используйте осторожно",
                            ]),
                        ],
                    },
                ],
            },
            {
                "title": "Python: Коллекции и функции",
                "description": "Списки, словари, кортежи, множества и определение функций.",
                "lessons": [
                    {
                        "title": "Списки и методы списков",
                        "blocks": [
                            header("Списки (list)", 2),
                            paragraph(
                                "Список — упорядоченная изменяемая коллекция. "
                                "Элементы могут быть любого типа."
                            ),
                            code(
                                "numbers = [1, 2, 3, 4, 5]\n"
                                "numbers.append(6)      # добавить в конец\n"
                                "numbers.insert(0, 0)     # вставить по индексу\n"
                                "numbers.remove(3)        # удалить по значению\n"
                                "last = numbers.pop()     # удалить и вернуть последний\n"
                                "print(numbers[1:4])      # срез: [1, 2, 3]"
                            ),
                            list_block([
                                "len(lst) — длина списка",
                                "sorted(lst) — отсортированная копия",
                                "sum(lst) — сумма чисел",
                                "lst.reverse() — развернуть на месте",
                            ]),
                        ],
                    },
                    {
                        "title": "Словари и множества",
                        "blocks": [
                            header("Словари (dict)", 2),
                            code(
                                "user = {\n"
                                "    'name': 'Иван',\n"
                                "    'email': 'ivan@mail.ru',\n"
                                "    'age': 30\n"
                                "}\n"
                                "print(user['name'])          # доступ по ключу\n"
                                "print(user.get('phone', 'нет'))  # безопасный доступ\n"
                                "for key, value in user.items():\n"
                                "    print(f'{key}: {value}')"
                            ),
                            header("Множества (set)", 3),
                            paragraph(
                                "Множество хранит уникальные элементы без порядка. "
                                "Полезно для удаления дубликатов и операций над множествами."
                            ),
                            code(
                                "tags = {'python', 'web', 'django', 'python'}\n"
                                "print(tags)  # {'python', 'web', 'django'}\n"
                                "a = {1, 2, 3}\n"
                                "b = {2, 3, 4}\n"
                                "print(a & b)  # пересечение: {2, 3}"
                            ),
                        ],
                    },
                    {
                        "title": "Функции и модули",
                        "blocks": [
                            header("Определение функций", 2),
                            code(
                                "def greet(name, greeting='Привет'):\n"
                                "    \"\"\"Приветствует пользователя.\"\"\"\n"
                                "    return f'{greeting}, {name}!'\n\n"
                                "print(greet('Анна'))\n"
                                "print(greet('Борис', 'Здравствуйте'))"
                            ),
                            header("Модули и import", 3),
                            paragraph(
                                "Модуль — файл .py с кодом. Стандартная библиотека Python "
                                "содержит сотни готовых модулей."
                            ),
                            code(
                                "import math\n"
                                "from datetime import date\n"
                                "from random import randint\n\n"
                                "print(math.sqrt(16))       # 4.0\n"
                                "print(date.today())\n"
                                "print(randint(1, 100))"
                            ),
                            quote(
                                "Простое лучше сложного. Читаемость имеет значение.",
                                "Дзен Python",
                            ),
                        ],
                    },
                ],
            },
        ],
    },
    # ── 2. Django ──────────────────────────────────────────────────────
    {
        "name": "Веб на Django",
        "description": (
            "Создание веб-приложений на Django 5: модели, представления, "
            "шаблоны, формы, админ-панель и REST API. Практический проект — "
            "блог с авторизацией."
        ),
        "price": 7900,
        "image": COURSE_IMAGES["django"],
        "duration": 6,
        "level": "С опытом",
        "category": "Веб-разработка",
        "programming_language": "Python",
        "modules": [
            {
                "title": "Django: Архитектура и старт",
                "description": "MVT-паттерн, создание проекта, настройка settings.",
                "lessons": [
                    {
                        "title": "Что такое Django и MVT",
                        "blocks": [
                            header("Фреймворк Django", 2),
                            paragraph(
                                "Django — полнофункциональный Python-фреймворк для "
                                "веб-разработки. Следует паттерну MVT: Model-View-Template."
                            ),
                            image(IMG["django"], "Логотип Django"),
                            image(IMG["django_mvt"], "Паттерн MVT в Django"),
                            list_block([
                                "View — представления (бизнес-логика, обработка запросов)",
                                "Template — HTML-шаблоны с тегами Django",
                                "URLconf — маршрутизация запросов",
                            ]),
                            code(
                                "# Создание проекта\n"
                                "pip install django\n"
                                "django-admin startproject mysite\n"
                                "cd mysite\n"
                                "python manage.py startapp blog\n"
                                "python manage.py runserver"
                            ),
                        ],
                    },
                    {
                        "title": "Модели и миграции",
                        "blocks": [
                            header("ORM Django", 2),
                            code(
                                "from django.db import models\n\n"
                                "class Article(models.Model):\n"
                                "    title = models.CharField(max_length=200)\n"
                                "    text = models.TextField()\n"
                                "    pub_date = models.DateTimeField(auto_now_add=True)\n"
                                "    author = models.ForeignKey(\n"
                                "        'auth.User', on_delete=models.CASCADE\n"
                                "    )\n\n"
                                "    def __str__(self):\n"
                                "        return self.title"
                            ),
                            paragraph(
                                "Миграции — версионирование схемы БД. "
                                "makemigrations создаёт файлы, migrate применяет их."
                            ),
                            code(
                                "python manage.py makemigrations\n"
                                "python manage.py migrate\n"
                                "python manage.py createsuperuser"
                            ),
                            image(IMG["database"], "Django ORM абстрагирует работу с БД"),
                        ],
                    },
                    {
                        "title": "Представления и URL-маршруты",
                        "blocks": [
                            header("Function-Based Views", 2),
                            code(
                                "# blog/views.py\n"
                                "from django.shortcuts import render, get_object_or_404\n"
                                "from .models import Article\n\n"
                                "def article_list(request):\n"
                                "    articles = Article.objects.all()\n"
                                "    return render(request, 'blog/list.html', {\n"
                                "        'articles': articles\n"
                                "    })\n\n"
                                "def article_detail(request, pk):\n"
                                "    article = get_object_or_404(Article, pk=pk)\n"
                                "    return render(request, 'blog/detail.html', {\n"
                                "        'article': article\n"
                                "    })"
                            ),
                            code(
                                "# blog/urls.py\n"
                                "from django.urls import path\n"
                                "from . import views\n\n"
                                "urlpatterns = [\n"
                                "    path('', views.article_list, name='list'),\n"
                                "    path('<int:pk>/', views.article_detail, name='detail'),\n"
                                "]"
                            ),
                        ],
                    },
                ],
            },
            {
                "title": "Django: Шаблоны и формы",
                "description": "Django Template Language, формы, CSRF, валидация.",
                "lessons": [
                    {
                        "title": "Шаблоны Django (DTL)",
                        "blocks": [
                            header("Django Template Language", 2),
                            code(
                                "{% extends 'base.html' %}\n"
                                "{% block content %}\n"
                                "<h1>{{ article.title }}</h1>\n"
                                "<p>{{ article.text|truncatewords:50 }}</p>\n"
                                "{% for comment in article.comment_set.all %}\n"
                                "  <div>{{ comment.text }}</div>\n"
                                "{% empty %}\n"
                                "  <p>Комментариев пока нет</p>\n"
                                "{% endfor %}\n"
                                "{% endblock %}"
                            ),
                            list_block([
                                "{{ variable }} — вывод переменной",
                                "{% tag %} — теги: for, if, block, include",
                                "{{ value|filter }} — фильтры: date, safe, length",
                                "{% url name arg %} — генерация URL",
                            ]),
                        ],
                    },
                    {
                        "title": "Формы Django",
                        "blocks": [
                            header("ModelForm", 2),
                            code(
                                "from django import forms\n"
                                "from .models import Article\n\n"
                                "class ArticleForm(forms.ModelForm):\n"
                                "    class Meta:\n"
                                "        model = Article\n"
                                "        fields = ['title', 'text']\n"
                                "        widgets = {\n"
                                "            'text': forms.Textarea(attrs={'rows': 5}),\n"
                                "        }"
                            ),
                            paragraph(
                                "В шаблоне обязательно добавляйте {% csrf_token %} "
                                "для защиты от подделки межсайтовых запросов."
                            ),
                            code(
                                "<form method='post'>\n"
                                "  {% csrf_token %}\n"
                                "  {{ form.as_p }}\n"
                                "  <button type='submit'>Сохранить</button>\n"
                                "</form>"
                            ),
                        ],
                    },
                    {
                        "title": "Админ-панель Django",
                        "blocks": [
                            header("Django Admin", 2),
                            paragraph(
                                "Админка — встроенный CRUD-интерфейс для моделей. "
                                "Доступна по адресу /admin/ после createsuperuser."
                            ),
                            code(
                                "# blog/admin.py\n"
                                "from django.contrib import admin\n"
                                "from .models import Article\n\n"
                                "@admin.register(Article)\n"
                                "class ArticleAdmin(admin.ModelAdmin):\n"
                                "    list_display = ['title', 'author', 'pub_date']\n"
                                "    list_filter = ['pub_date', 'author']\n"
                                "    search_fields = ['title', 'text']\n"
                                "    date_hierarchy = 'pub_date'"
                            ),
                            list_block([
                                "list_display — колонки в списке",
                                "list_filter — боковые фильтры",
                                "search_fields — полнотекстовый поиск",
                                "inlines — вложенные формы",
                            ]),
                        ],
                    },
                ],
            },
            {
                "title": "Django: Авторизация и API",
                "description": "Система пользователей, DRF, деплой.",
                "lessons": [
                    {
                        "title": "Аутентификация пользователей",
                        "blocks": [
                            header("Auth в Django", 2),
                            code(
                                "from django.contrib.auth.decorators import login_required\n"
                                "from django.contrib.auth import login, logout\n"
                                "from django.contrib.auth.forms import UserCreationForm\n\n"
                                "@login_required\n"
                                "def profile(request):\n"
                                "    return render(request, 'profile.html')"
                            ),
                            paragraph(
                                "Встроенная модель User, формы LoginForm и UserCreationForm, "
                                "декораторы login_required и permission_required."
                            ),
                        ],
                    },
                    {
                        "title": "Django REST Framework",
                        "blocks": [
                            header("REST API с DRF", 2),
                            code(
                                "from rest_framework import serializers, viewsets\n"
                                "from .models import Article\n\n"
                                "class ArticleSerializer(serializers.ModelSerializer):\n"
                                "    class Meta:\n"
                                "        model = Article\n"
                                "        fields = '__all__'\n\n"
                                "class ArticleViewSet(viewsets.ModelViewSet):\n"
                                "    queryset = Article.objects.all()\n"
                                "    serializer_class = ArticleSerializer"
                            ),
                            list_block([
                                "Serializer — преобразование модели в JSON",
                                "ViewSet — CRUD-операции одним классом",
                                "Router — автоматическая маршрутизация",
                                "Permissions — контроль доступа к API",
                            ]),
                        ],
                    },
                    {
                        "title": "Деплой Django-приложения",
                        "blocks": [
                            header("Подготовка к продакшену", 2),
                            list_block([
                                "DEBUG = False в settings.py",
                                "ALLOWED_HOSTS — список доменов",
                                "Статика: python manage.py collectstatic",
                                "Gunicorn + Nginx как reverse proxy",
                                "PostgreSQL вместо SQLite",
                            ], ordered=True),
                            code(
                                "# gunicorn\n"
                                "pip install gunicorn\n"
                                "gunicorn mysite.wsgi:application --bind 0.0.0.0:8000"
                            ),
                            paragraph(
                                "Используйте переменные окружения (.env) для SECRET_KEY, "
                                "паролей БД и API-ключей. Никогда не коммитьте секреты."
                            ),
                        ],
                    },
                ],
            },
        ],
    },
    # ── 3. JavaScript ──────────────────────────────────────────────────
    {
        "name": "JavaScript с нуля",
        "description": (
            "Базовый курс по JavaScript ES6+: переменные, функции, DOM, "
            "события, асинхронность (Promise, async/await) и работа с API."
        ),
        "price": 5200,
        "image": COURSE_IMAGES["javascript"],
        "duration": 4,
        "level": "С нуля",
        "category": "Программирование",
        "programming_language": "JavaScript",
        "modules": [
            {
                "title": "JS: Основы языка",
                "description": "Синтаксис ES6+, let/const, типы, функции.",
                "lessons": [
                    {
                        "title": "Введение в JavaScript",
                        "blocks": [
                            header("JavaScript в браузере", 2),
                            paragraph(
                                "JavaScript — язык программирования, который делает "
                                "веб-страницы интерактивными. Выполняется в браузере "
                                "и на сервере (Node.js)."
                            ),
                            image(IMG["javascript"], "Логотип JavaScript"),
                            code(
                                "// Подключение в HTML\n"
                                "<script src='app.js'></script>\n\n"
                                "// Или в консоли браузера (F12)\n"
                                "console.log('Привет, мир!');"
                            ),
                            list_block([
                                "console.log() — вывод в консоль разработчика",
                                "alert() — всплывающее окно",
                                "document — доступ к DOM-дереву",
                            ]),
                        ],
                    },
                    {
                        "title": "Переменные let, const и типы",
                        "blocks": [
                            header("Объявление переменных", 2),
                            code(
                                "let count = 0;          // можно менять\n"
                                "const PI = 3.14159;     // константа\n"
                                "// var — устаревший, не используйте\n\n"
                                "let name = 'Алексей';\n"
                                "let isActive = true;\n"
                                "let items = [1, 2, 3];\n"
                                "let user = { name: 'Алексей', age: 28 };"
                            ),
                            header("Типы данных", 3),
                            list_block([
                                "number — числа (целые и дробные)",
                                "string — строки в кавычках",
                                "boolean — true / false",
                                "undefined — не присвоено значение",
                                "null — намеренное отсутствие",
                                "object — объекты и массивы",
                            ]),
                        ],
                    },
                    {
                        "title": "Функции и стрелочный синтаксис",
                        "blocks": [
                            header("Функции в JS", 2),
                            code(
                                "function greet(name) {\n"
                                "  return `Привет, ${name}!`;\n"
                                "}\n\n"
                                "// Стрелочная функция\n"
                                "const add = (a, b) => a + b;\n\n"
                                "// Колбэк\n"
                                "const nums = [1, 2, 3];\n"
                                "const doubled = nums.map(n => n * 2);\n"
                                "console.log(doubled); // [2, 4, 6]"
                            ),
                            paragraph(
                                "Шаблонные строки (``) поддерживают интерполяцию "
                                "через ${выражение}."
                            ),
                        ],
                    },
                ],
            },
            {
                "title": "JS: DOM и события",
                "description": "Работа с HTML-элементами, обработка событий.",
                "lessons": [
                    {
                        "title": "Document Object Model",
                        "blocks": [
                            header("DOM — дерево документа", 2),
                            image(IMG["browser"], "Браузер парсит HTML в DOM-дерево"),
                            code(
                                "const title = document.querySelector('h1');\n"
                                "title.textContent = 'Новый заголовок';\n"
                                "title.style.color = '#e74c3c';\n\n"
                                "const btn = document.getElementById('myBtn');\n"
                                "const items = document.querySelectorAll('.item');"
                            ),
                            list_block([
                                "querySelector(selector) — первый элемент",
                                "querySelectorAll(selector) — все элементы",
                                "createElement(tag) — создать элемент",
                                "appendChild(node) — добавить в DOM",
                            ]),
                        ],
                    },
                    {
                        "title": "Обработка событий",
                        "blocks": [
                            header("addEventListener", 2),
                            code(
                                "const button = document.querySelector('#submit');\n\n"
                                "button.addEventListener('click', (event) => {\n"
                                "  event.preventDefault();\n"
                                "  console.log('Кнопка нажата!');\n"
                                "});\n\n"
                                "document.addEventListener('keydown', (e) => {\n"
                                "  if (e.key === 'Enter') submitForm();\n"
                                "});"
                            ),
                            paragraph(
                                "Всплытие (bubbling): событие поднимается от целевого "
                                "элемента к родителям. event.stopPropagation() останавливает."
                            ),
                        ],
                    },
                    {
                        "title": "Формы и валидация",
                        "blocks": [
                            header("Работа с формами", 2),
                            code(
                                "const form = document.querySelector('#loginForm');\n\n"
                                "form.addEventListener('submit', (e) => {\n"
                                "  e.preventDefault();\n"
                                "  const email = form.email.value.trim();\n"
                                "  const password = form.password.value;\n\n"
                                "  if (!email.includes('@')) {\n"
                                "    alert('Некорректный email');\n"
                                "    return;\n"
                                "  }\n"
                                "  // отправка данных...\n"
                                "});"
                            ),
                        ],
                    },
                ],
            },
            {
                "title": "JS: Асинхронность",
                "description": "Promise, fetch, async/await, работа с API.",
                "lessons": [
                    {
                        "title": "Promise и асинхронный код",
                        "blocks": [
                            header("Асинхронность в JS", 2),
                            paragraph(
                                "JavaScript однопоточный, но умеет выполнять операции "
                                "ввода-вывода асинхронно через Event Loop."
                            ),
                            code(
                                "const fetchData = () => {\n"
                                "  return new Promise((resolve, reject) => {\n"
                                "    setTimeout(() => resolve('Данные'), 1000);\n"
                                "  });\n"
                                "};\n\n"
                                "fetchData()\n"
                                "  .then(data => console.log(data))\n"
                                "  .catch(err => console.error(err));"
                            ),
                        ],
                    },
                    {
                        "title": "fetch и работа с API",
                        "blocks": [
                            header("HTTP-запросы с fetch", 2),
                            image(IMG["async_js"], "Цепочка Promise и async/await"),
                            code(
                                "async function getUsers() {\n"
                                "  try {\n"
                                "    const response = await fetch('/api/users/');\n"
                                "    if (!response.ok) throw new Error('Ошибка сети');\n"
                                "    const users = await response.json();\n"
                                "    return users;\n"
                                "  } catch (error) {\n"
                                "    console.error(error);\n"
                                "  }\n"
                                "}"
                            ),
                            list_block([
                                "GET — получение данных",
                                "POST — создание (с телом JSON)",
                                "PUT/PATCH — обновление",
                                "DELETE — удаление",
                            ]),
                        ],
                    },
                    {
                        "title": "async/await на практике",
                        "blocks": [
                            header("Современный асинхронный код", 2),
                            code(
                                "async function loadPage() {\n"
                                "  const [user, posts] = await Promise.all([\n"
                                "    fetch('/api/user/').then(r => r.json()),\n"
                                "    fetch('/api/posts/').then(r => r.json()),\n"
                                "  ]);\n"
                                "  renderProfile(user);\n"
                                "  renderPosts(posts);\n"
                                "}\n\n"
                                "loadPage();"
                            ),
                            paragraph(
                                "Promise.all выполняет запросы параллельно. "
                                "try/catch обрабатывает ошибки в async-функциях."
                            ),
                        ],
                    },
                ],
            },
        ],
    },
    # ── 4. SQL ─────────────────────────────────────────────────────────
    {
        "name": "SQL для разработчика",
        "description": (
            "Реляционные базы данных: проектирование схем, SELECT/JOIN, "
            "агрегация, индексы, транзакции. Практика на PostgreSQL."
        ),
        "price": 5700,
        "image": COURSE_IMAGES["sql"],
        "duration": 3,
        "level": "С нуля",
        "category": "Базы данных",
        "programming_language": "SQL",
        "modules": [
            {
                "title": "SQL: Основы и SELECT",
                "description": "Реляционная модель, CREATE TABLE, базовые запросы.",
                "lessons": [
                    {
                        "title": "Реляционные базы данных",
                        "blocks": [
                            header("Что такое SQL", 2),
                            paragraph(
                                "SQL (Structured Query Language) — язык запросов к "
                                "реляционным СУБД: PostgreSQL, MySQL, SQLite, Oracle."
                            ),
                            image(IMG["sql"], "SQL — стандарт работы с базами данных"),
                            list_block([
                                "Таблица — набор строк (записей) и столбцов (полей)",
                                "Первичный ключ (PRIMARY KEY) — уникальный идентификатор",
                                "Внешний ключ (FOREIGN KEY) — связь между таблицами",
                                "Нормализация — устранение дублирования данных",
                            ]),
                        ],
                    },
                    {
                        "title": "CREATE TABLE и типы данных",
                        "blocks": [
                            header("Создание таблиц", 2),
                            code(
                                "CREATE TABLE users (\n"
                                "    id SERIAL PRIMARY KEY,\n"
                                "    username VARCHAR(50) UNIQUE NOT NULL,\n"
                                "    email VARCHAR(100) NOT NULL,\n"
                                "    created_at TIMESTAMP DEFAULT NOW()\n"
                                ");\n\n"
                                "CREATE TABLE posts (\n"
                                "    id SERIAL PRIMARY KEY,\n"
                                "    title VARCHAR(200) NOT NULL,\n"
                                "    body TEXT,\n"
                                "    author_id INTEGER REFERENCES users(id)\n"
                                ");"
                            ),
                        ],
                    },
                    {
                        "title": "SELECT, WHERE, ORDER BY",
                        "blocks": [
                            header("Выборка данных", 2),
                            code(
                                "SELECT username, email\n"
                                "FROM users\n"
                                "WHERE created_at > '2024-01-01'\n"
                                "ORDER BY username ASC\n"
                                "LIMIT 10;"
                            ),
                            list_block([
                                "WHERE — фильтрация строк",
                                "ORDER BY ASC/DESC — сортировка",
                                "LIMIT / OFFSET — пагинация",
                                "DISTINCT — уникальные значения",
                                "LIKE '%pattern%' — поиск по шаблону",
                            ]),
                        ],
                    },
                ],
            },
            {
                "title": "SQL: JOIN и агрегация",
                "description": "Соединение таблиц, GROUP BY, подзапросы.",
                "lessons": [
                    {
                        "title": "JOIN — соединение таблиц",
                        "blocks": [
                            header("Типы JOIN", 2),
                            code(
                                "SELECT u.username, p.title, p.created_at\n"
                                "FROM users u\n"
                                "INNER JOIN posts p ON u.id = p.author_id\n"
                                "WHERE u.username = 'ivan';"
                            ),
                            list_block([
                                "INNER JOIN — только совпадающие строки",
                                "LEFT JOIN — все из левой + совпадения справа",
                                "RIGHT JOIN — все из правой + совпадения слева",
                                "FULL OUTER JOIN — все строки из обеих таблиц",
                            ]),
                            image(IMG["sql_join"], "JOIN связывает таблицы по ключам"),
                        ],
                    },
                    {
                        "title": "Агрегатные функции и GROUP BY",
                        "blocks": [
                            header("Группировка данных", 2),
                            code(
                                "SELECT author_id,\n"
                                "       COUNT(*) AS post_count,\n"
                                "       MAX(created_at) AS last_post\n"
                                "FROM posts\n"
                                "GROUP BY author_id\n"
                                "HAVING COUNT(*) > 5\n"
                                "ORDER BY post_count DESC;"
                            ),
                            paragraph(
                                "HAVING фильтрует группы (аналог WHERE для агрегатов). "
                                "Функции: COUNT, SUM, AVG, MIN, MAX."
                            ),
                        ],
                    },
                    {
                        "title": "Подзапросы и CTE",
                        "blocks": [
                            header("Подзапросы (subqueries)", 2),
                            code(
                                "SELECT username FROM users\n"
                                "WHERE id IN (\n"
                                "    SELECT author_id FROM posts\n"
                                "    GROUP BY author_id HAVING COUNT(*) > 10\n"
                                ");\n\n"
                                "WITH top_authors AS (\n"
                                "    SELECT author_id, COUNT(*) AS cnt\n"
                                "    FROM posts GROUP BY author_id\n"
                                "    ORDER BY cnt DESC LIMIT 5\n"
                                ")\n"
                                "SELECT u.username, t.cnt\n"
                                "FROM top_authors t\n"
                                "JOIN users u ON u.id = t.author_id;"
                            ),
                        ],
                    },
                ],
            },
            {
                "title": "SQL: Индексы и транзакции",
                "description": "Оптимизация запросов, ACID, блокировки.",
                "lessons": [
                    {
                        "title": "Индексы и оптимизация",
                        "blocks": [
                            header("Индексы", 2),
                            code(
                                "CREATE INDEX idx_posts_author\n"
                                "ON posts(author_id);\n\n"
                                "CREATE INDEX idx_users_email\n"
                                "ON users(email);\n\n"
                                "EXPLAIN ANALYZE\n"
                                "SELECT * FROM posts WHERE author_id = 42;"
                            ),
                            paragraph(
                                "Индекс ускоряет SELECT, но замедляет INSERT/UPDATE. "
                                "EXPLAIN ANALYZE показывает план выполнения запроса."
                            ),
                        ],
                    },
                    {
                        "title": "Транзакции ACID",
                        "blocks": [
                            header("ACID-принципы", 2),
                            list_block([
                                "Atomicity — всё или ничего",
                                "Consistency — данные остаются валидными",
                                "Isolation — параллельные транзакции не мешают",
                                "Durability — зафиксированные данные сохраняются",
                            ]),
                            code(
                                "BEGIN;\n"
                                "UPDATE accounts SET balance = balance - 100\n"
                                "  WHERE id = 1;\n"
                                "UPDATE accounts SET balance = balance + 100\n"
                                "  WHERE id = 2;\n"
                                "COMMIT;  -- или ROLLBACK при ошибке"
                            ),
                        ],
                    },
                    {
                        "title": "INSERT, UPDATE, DELETE",
                        "blocks": [
                            header("Модификация данных", 2),
                            code(
                                "INSERT INTO users (username, email)\n"
                                "VALUES ('anna', 'anna@mail.ru');\n\n"
                                "UPDATE users SET email = 'new@mail.ru'\n"
                                "WHERE username = 'anna';\n\n"
                                "DELETE FROM posts\n"
                                "WHERE created_at < '2020-01-01';"
                            ),
                            paragraph(
                                "Всегда используйте WHERE при UPDATE и DELETE, "
                                "иначе затронете все строки таблицы!"
                            ),
                        ],
                    },
                ],
            },
        ],
    },
    # ── 5. Git ─────────────────────────────────────────────────────────
    {
        "name": "Git: версии и ветки",
        "description": (
            "Система контроля версий Git: коммиты, ветки, merge, rebase, "
            "GitHub, pull request и code review."
        ),
        "price": 3500,
        "image": COURSE_IMAGES["git"],
        "duration": 2,
        "level": "С нуля",
        "category": "DevOps",
        "programming_language": "Git",
        "modules": [
            {
                "title": "Git: Основы",
                "description": "Инициализация, коммиты, история, .gitignore.",
                "lessons": [
                    {
                        "title": "Зачем нужен Git",
                        "blocks": [
                            header("Контроль версий", 2),
                            paragraph(
                                "Git отслеживает изменения в файлах проекта, позволяет "
                                "откатываться к предыдущим версиям и работать в команде."
                            ),
                            image(IMG["git"], "Логотип Git"),
                            list_block([
                                "Локальный репозиторий — папка .git с историей",
                                "Коммит — снимок состояния проекта",
                                "Ветка — независимая линия разработки",
                                "Удалённый репозиторий — GitHub, GitLab, Bitbucket",
                            ]),
                        ],
                    },
                    {
                        "title": "Первые коммиты",
                        "blocks": [
                            header("Базовые команды", 2),
                            code(
                                "git init\n"
                                "git add file.py\n"
                                "git add .                    # все файлы\n"
                                "git commit -m 'Добавил модуль авторизации'\n"
                                "git log --oneline\n"
                                "git status"
                            ),
                            paragraph(
                                "Рабочая область → Staging (git add) → Repository "
                                "(git commit). Хорошее сообщение коммита описывает "
                                "зачем, а не что."
                            ),
                        ],
                    },
                    {
                        "title": "gitignore и конфигурация",
                        "blocks": [
                            header(".gitignore", 2),
                            code(
                                "# .gitignore\n"
                                "__pycache__/\n"
                                "*.pyc\n"
                                ".env\n"
                                "venv/\n"
                                "db.sqlite3\n"
                                "media/\n"
                                ".DS_Store"
                            ),
                            code(
                                "git config --global user.name 'Иван Иванов'\n"
                                "git config --global user.email 'ivan@mail.ru'"
                            ),
                        ],
                    },
                ],
            },
            {
                "title": "Git: Ветки и слияние",
                "description": "branch, merge, конфликты, rebase.",
                "lessons": [
                    {
                        "title": "Работа с ветками",
                        "blocks": [
                            header("Ветвление", 2),
                            image(IMG["git_branching"], "Модель ветвления Git"),
                            code(
                                "git checkout feature/login\n"
                                "# или одной командой:\n"
                                "git checkout -b feature/login\n\n"
                                "git branch          # список веток\n"
                                "git merge feature/login\n"
                                "git branch -d feature/login"
                            ),
                            paragraph(
                                "Git Flow: main (продакшен), develop (разработка), "
                                "feature/* (фичи), hotfix/* (срочные исправления)."
                            ),
                        ],
                    },
                    {
                        "title": "Разрешение конфликтов",
                        "blocks": [
                            header("Merge conflicts", 2),
                            paragraph(
                                "Конфликт возникает, когда две ветки изменили одни "
                                "и те же строки. Git помечает конфликт маркерами:"
                            ),
                            code(
                                "<<<<<<< HEAD\n"
                                "const greeting = 'Привет';\n"
                                "=======\n"
                                "const greeting = 'Hello';\n"
                                ">>>>>>> feature/i18n"
                            ),
                            list_block([
                                "Откройте файл, выберите нужный вариант",
                                "Удалите маркеры <<<<<<, =======, >>>>>>>",
                                "git add file.js && git commit",
                            ], ordered=True),
                        ],
                    },
                    {
                        "title": "Rebase vs Merge",
                        "blocks": [
                            header("Rebase", 2),
                            code(
                                "git checkout feature/api\n"
                                "git rebase main\n"
                                "# переносит коммиты feature поверх main"
                            ),
                            paragraph(
                                "Merge сохраняет историю ветвлений (merge commit). "
                                "Rebase создаёт линейную историю. Не делайте rebase "
                                "опубликованных веток!"
                            ),
                        ],
                    },
                ],
            },
            {
                "title": "Git: GitHub и командная работа",
                "description": "Remote, pull request, code review.",
                "lessons": [
                    {
                        "title": "Удалённые репозитории",
                        "blocks": [
                            header("Remote", 2),
                            code(
                                "git remote add origin git@github.com:user/repo.git\n"
                                "git push -u origin main\n"
                                "git pull origin main\n"
                                "git fetch origin\n"
                                "git clone git@github.com:user/repo.git"
                            ),
                        ],
                    },
                    {
                        "title": "Pull Request workflow",
                        "blocks": [
                            header("Pull Request", 2),
                            list_block([
                                "Создайте ветку от main: git checkout -b fix/bug-42",
                                "Сделайте коммиты с понятными сообщениями",
                                "git push origin fix/bug-42",
                                "Откройте PR на GitHub с описанием изменений",
                                "Пройдите code review, исправьте замечания",
                                "Merge PR в main после одобрения",
                            ], ordered=True),
                        ],
                    },
                    {
                        "title": "Полезные команды",
                        "blocks": [
                            header("Шпаргалка Git", 2),
                            code(
                                "git stash              # спрятать изменения\n"
                                "git stash pop          # вернуть изменения\n"
                                "git cherry-pick abc123 # перенести один коммит\n"
                                "git reset --soft HEAD~1  # отменить коммит\n"
                                "git log --graph --oneline --all"
                            ),
                        ],
                    },
                ],
            },
        ],
    },
    # ── 6. HTML и CSS ──────────────────────────────────────────────────
    {
        "name": "HTML и CSS",
        "description": (
            "Вёрстка веб-страниц: семантический HTML5, CSS Flexbox и Grid, "
            "адаптивный дизайн, переменные и анимации."
        ),
        "price": 4500,
        "image": COURSE_IMAGES["html"],
        "duration": 3,
        "level": "С нуля",
        "category": "Веб-разработка",
        "programming_language": "HTML/CSS",
        "modules": [
            {
                "title": "HTML: Структура страницы",
                "description": "Семантические теги, формы, метаданные.",
                "lessons": [
                    {
                        "title": "Основы HTML5",
                        "blocks": [
                            header("HTML — язык разметки", 2),
                            image(IMG["html_css"], "HTML5 — стандарт вёрстки"),
                            code(
                                "<!DOCTYPE html>\n"
                                "<html lang='ru'>\n"
                                "<head>\n"
                                "  <meta charset='UTF-8'>\n"
                                "  <meta name='viewport' content='width=device-width'>\n"
                                "  <title>Моя страница</title>\n"
                                "</head>\n"
                                "<body>\n"
                                "  <h1>Заголовок</h1>\n"
                                "  <p>Абзац текста</p>\n"
                                "</body>\n"
                                "</html>"
                            ),
                        ],
                    },
                    {
                        "title": "Семантическая разметка",
                        "blocks": [
                            header("Семантические теги", 2),
                            code(
                                "<header>Шапка сайта</header>\n"
                                "<nav>Навигация</nav>\n"
                                "<main>\n"
                                "  <article>\n"
                                "    <h2>Заголовок статьи</h2>\n"
                                "    <p>Текст...</p>\n"
                                "  </article>\n"
                                "  <aside>Боковая панель</aside>\n"
                                "</main>\n"
                                "<footer>Подвал</footer>"
                            ),
                            paragraph(
                                "Семантика улучшает доступность (screen readers) "
                                "и SEO-оптимизацию."
                            ),
                        ],
                    },
                    {
                        "title": "Формы и медиа",
                        "blocks": [
                            header("HTML-формы", 2),
                            code(
                                "<form action='/submit' method='post'>\n"
                                "  <label for='email'>Email:</label>\n"
                                "  <input type='email' id='email' required>\n"
                                "  <button type='submit'>Отправить</button>\n"
                                "</form>\n\n"
                                "<img src='photo.jpg' alt='Описание'>\n"
                                "<video controls src='video.mp4'></video>"
                            ),
                        ],
                    },
                ],
            },
            {
                "title": "CSS: Стилизация",
                "description": "Селекторы, box model, Flexbox, Grid.",
                "lessons": [
                    {
                        "title": "Селекторы и Box Model",
                        "blocks": [
                            header("CSS-селекторы", 2),
                            code(
                                "/* По тегу */\n"
                                "p { color: #333; }\n\n"
                                "/* По классу */\n"
                                ".card { border-radius: 8px; }\n\n"
                                "/* По id */\n"
                                "#header { background: #1a1a2e; }\n\n"
                                "/* Псевдоклассы */\n"
                                "a:hover { color: red; }\n"
                                "li:nth-child(odd) { background: #f5f5f5; }"
                            ),
                            paragraph(
                                "Box Model: content → padding → border → margin. "
                                "box-sizing: border-box включает padding и border в width."
                            ),
                        ],
                    },
                    {
                        "title": "Flexbox",
                        "blocks": [
                            header("Flexbox-вёрстка", 2),
                            image(IMG["flexbox"], "Схема Flexbox-контейнера"),
                            code(
                                ".container {\n"
                                "  display: flex;\n"
                                "  justify-content: space-between;\n"
                                "  align-items: center;\n"
                                "  gap: 16px;\n"
                                "  flex-wrap: wrap;\n"
                                "}\n\n"
                                ".item {\n"
                                "  flex: 1 1 300px;\n"
                                "}"
                            ),
                            list_block([
                                "justify-content — горизонтальное выравнивание",
                                "align-items — вертикальное выравнивание",
                                "flex-direction: column — вертикальный стек",
                                "gap — отступы между элементами",
                            ]),
                        ],
                    },
                    {
                        "title": "CSS Grid",
                        "blocks": [
                            header("Grid-сетка", 2),
                            image(IMG["css_grid"], "CSS Grid — двумерная сетка"),
                            code(
                                ".grid {\n"
                                "  display: grid;\n"
                                "  grid-template-columns: repeat(3, 1fr);\n"
                                "  grid-template-rows: auto;\n"
                                "  gap: 20px;\n"
                                "}\n\n"
                                ".span-2 {\n"
                                "  grid-column: span 2;\n"
                                "}"
                            ),
                            paragraph(
                                "Grid идеален для двумерных макетов (строки + столбцы). "
                                "Flexbox — для одномерных (ряд или колонка)."
                            ),
                        ],
                    },
                ],
            },
            {
                "title": "CSS: Адаптивность",
                "description": "Media queries, mobile-first, CSS-переменные.",
                "lessons": [
                    {
                        "title": "Адаптивный дизайн",
                        "blocks": [
                            header("Media Queries", 2),
                            code(
                                "/* Mobile first */\n"
                                ".container { padding: 16px; }\n\n"
                                "@media (min-width: 768px) {\n"
                                "  .container {\n"
                                "    padding: 32px;\n"
                                "    max-width: 1200px;\n"
                                "    margin: 0 auto;\n"
                                "  }\n"
                                "}"
                            ),
                            list_block([
                                "320px — мобильные телефоны",
                                "768px — планшеты",
                                "1024px — ноутбуки",
                                "1440px — десктопы",
                            ]),
                        ],
                    },
                    {
                        "title": "CSS-переменные",
                        "blocks": [
                            header("Custom Properties", 2),
                            code(
                                ":root {\n"
                                "  --color-primary: #6c5ce7;\n"
                                "  --color-bg: #0f0f1a;\n"
                                "  --radius: 12px;\n"
                                "  --font-main: 'Inter', sans-serif;\n"
                                "}\n\n"
                                ".button {\n"
                                "  background: var(--color-primary);\n"
                                "  border-radius: var(--radius);\n"
                                "}"
                            ),
                        ],
                    },
                    {
                        "title": "Анимации и переходы",
                        "blocks": [
                            header("Transitions и Animations", 2),
                            code(
                                ".card {\n"
                                "  transition: transform 0.3s ease,\n"
                                "              box-shadow 0.3s ease;\n"
                                "}\n"
                                ".card:hover {\n"
                                "  transform: translateY(-4px);\n"
                                "  box-shadow: 0 8px 24px rgba(0,0,0,0.15);\n"
                                "}\n\n"
                                "@keyframes fadeIn {\n"
                                "  from { opacity: 0; }\n"
                                "  to { opacity: 1; }\n"
                                "}"
                            ),
                        ],
                    },
                ],
            },
        ],
    },
    # ── 7. Алгоритмы ───────────────────────────────────────────────────
    {
        "name": "Алгоритмы и структуры",
        "description": (
            "Базовые алгоритмы и структуры данных: массивы, стеки, очереди, "
            "сортировки, поиск, сложность O-нотация. Подготовка к собеседованиям."
        ),
        "price": 6100,
        "image": COURSE_IMAGES["algorithms"],
        "duration": 5,
        "level": "С опытом",
        "category": "Алгоритмы",
        "programming_language": "Python",
        "modules": [
            {
                "title": "Алгоритмы: Сложность и массивы",
                "description": "Big O, массивы, хеш-таблицы.",
                "lessons": [
                    {
                        "title": "О-нотация Big O",
                        "blocks": [
                            header("Анализ сложности", 2),
                            image(IMG["algorithms"], "График роста сложности алгоритмов"),
                            list_block([
                                "O(1) — константное время (доступ по индексу)",
                                "O(log n) — логарифмическое (бинарный поиск)",
                                "O(n) — линейное (перебор массива)",
                                "O(n log n) — сортировки (merge sort)",
                                "O(n²) — квадратичное (вложенные циклы)",
                            ]),
                            paragraph(
                                "Big O описывает худший случай роста времени/памяти "
                                "при увеличении входных данных."
                            ),
                        ],
                    },
                    {
                        "title": "Массивы и строки",
                        "blocks": [
                            header("Задачи на массивы", 2),
                            code(
                                "def two_sum(nums, target):\n"
                                "    seen = {}\n"
                                "    for i, num in enumerate(nums):\n"
                                "        complement = target - num\n"
                                "        if complement in seen:\n"
                                "            return [seen[complement], i]\n"
                                "        seen[num] = i\n"
                                "    return []"
                            ),
                            paragraph(
                                "Хеш-таблица (dict) даёт O(1) поиск — классический "
                                "приём для ускорения с O(n²) до O(n)."
                            ),
                        ],
                    },
                    {
                        "title": "Два указателя и скользящее окно",
                        "blocks": [
                            header("Two Pointers", 2),
                            code(
                                "def is_palindrome(s):\n"
                                "    left, right = 0, len(s) - 1\n"
                                "    while left < right:\n"
                                "        if s[left] != s[right]:\n"
                                "            return False\n"
                                "        left += 1\n"
                                "        right -= 1\n"
                                "    return True"
                            ),
                            paragraph(
                                "Техника двух указателей работает на отсортированных "
                                "массивах и строках за O(n)."
                            ),
                        ],
                    },
                ],
            },
            {
                "title": "Алгоритмы: Стеки и очереди",
                "description": "LIFO, FIFO, BFS, DFS.",
                "lessons": [
                    {
                        "title": "Стек (Stack)",
                        "blocks": [
                            header("LIFO — Last In, First Out", 2),
                            image(IMG["stack_queue"], "Стек (LIFO) и очередь (FIFO)"),
                            code(
                                "stack = []\n"
                                "stack.append(1)  # push\n"
                                "stack.append(2)\n"
                                "top = stack.pop()  # 2\n\n"
                                "def is_valid_parentheses(s):\n"
                                "    stack = []\n"
                                "    pairs = {')': '(', ']': '[', '}': '{'}\n"
                                "    for ch in s:\n"
                                "        if ch in pairs.values():\n"
                                "            stack.append(ch)\n"
                                "        elif not stack or stack.pop() != pairs[ch]:\n"
                                "            return False\n"
                                "    return not stack"
                            ),
                        ],
                    },
                    {
                        "title": "Очередь (Queue) и BFS",
                        "blocks": [
                            header("BFS — поиск в ширину", 2),
                            code(
                                "from collections import deque\n\n"
                                "def bfs(graph, start):\n"
                                "    visited = {start}\n"
                                "    queue = deque([start])\n"
                                "    while queue:\n"
                                "        node = queue.popleft()\n"
                                "        print(node)\n"
                                "        for neighbor in graph[node]:\n"
                                "            if neighbor not in visited:\n"
                                "                visited.add(neighbor)\n"
                                "                queue.append(neighbor)"
                            ),
                        ],
                    },
                    {
                        "title": "DFS — поиск в глубину",
                        "blocks": [
                            header("Рекурсивный DFS", 2),
                            code(
                                "def dfs(graph, node, visited=None):\n"
                                "    if visited is None:\n"
                                "        visited = set()\n"
                                "    visited.add(node)\n"
                                "    print(node)\n"
                                "    for neighbor in graph[node]:\n"
                                "        if neighbor not in visited:\n"
                                "            dfs(graph, neighbor, visited)"
                            ),
                            paragraph(
                                "BFS находит кратчайший путь в невзвешенном графе. "
                                "DFS использует меньше памяти (стек рекурсии)."
                            ),
                        ],
                    },
                ],
            },
            {
                "title": "Алгоритмы: Сортировки и поиск",
                "description": "Bubble, merge, quick sort, binary search.",
                "lessons": [
                    {
                        "title": "Бинарный поиск",
                        "blocks": [
                            header("Binary Search — O(log n)", 2),
                            image(IMG["binary_search"], "Бинарный поиск по отсортированному массиву"),
                            code(
                                "def binary_search(arr, target):\n"
                                "    left, right = 0, len(arr) - 1\n"
                                "    while left <= right:\n"
                                "        mid = (left + right) // 2\n"
                                "        if arr[mid] == target:\n"
                                "            return mid\n"
                                "        elif arr[mid] < target:\n"
                                "            left = mid + 1\n"
                                "        else:\n"
                                "            right = mid - 1\n"
                                "    return -1"
                            ),
                            paragraph(
                                "Работает только на отсортированном массиве. "
                                "На каждом шаге отбрасывается половина элементов."
                            ),
                        ],
                    },
                    {
                        "title": "Сортировка слиянием",
                        "blocks": [
                            header("Merge Sort — O(n log n)", 2),
                            code(
                                "def merge_sort(arr):\n"
                                "    if len(arr) <= 1:\n"
                                "        return arr\n"
                                "    mid = len(arr) // 2\n"
                                "    left = merge_sort(arr[:mid])\n"
                                "    right = merge_sort(arr[mid:])\n"
                                "    return merge(left, right)\n\n"
                                "def merge(left, right):\n"
                                "    result = []\n"
                                "    i = j = 0\n"
                                "    while i < len(left) and j < len(right):\n"
                                "        if left[i] <= right[j]:\n"
                                "            result.append(left[i]); i += 1\n"
                                "        else:\n"
                                "            result.append(right[j]); j += 1\n"
                                "    return result + left[i:] + right[j:]"
                            ),
                        ],
                    },
                    {
                        "title": "Быстрая сортировка",
                        "blocks": [
                            header("Quick Sort", 2),
                            code(
                                "def quick_sort(arr):\n"
                                "    if len(arr) <= 1:\n"
                                "        return arr\n"
                                "    pivot = arr[len(arr) // 2]\n"
                                "    left = [x for x in arr if x < pivot]\n"
                                "    mid = [x for x in arr if x == pivot]\n"
                                "    right = [x for x in arr if x > pivot]\n"
                                "    return quick_sort(left) + mid + quick_sort(right)"
                            ),
                            paragraph(
                                "В среднем O(n log n), в худшем O(n²). "
                                "На практике быстрее merge sort из-за кэш-локальности."
                            ),
                        ],
                    },
                ],
            },
        ],
    },
    # ── 8. Docker ──────────────────────────────────────────────────────
    {
        "name": "Docker: контейнеры",
        "description": (
            "Контейнеризация приложений: Docker, Dockerfile, docker-compose, "
            "volumes, сети и деплой микросервисов."
        ),
        "price": 4900,
        "image": COURSE_IMAGES["docker"],
        "duration": 3,
        "level": "С опытом",
        "category": "DevOps",
        "programming_language": "Docker",
        "modules": [
            {
                "title": "Docker: Основы",
                "description": "Контейнеры vs VM, установка, базовые команды.",
                "lessons": [
                    {
                        "title": "Контейнеры и виртуализация",
                        "blocks": [
                            header("Что такое Docker", 2),
                            paragraph(
                                "Docker упаковывает приложение со всеми зависимостями "
                                "в изолированный контейнер, который работает одинаково "
                                "на любой машине."
                            ),
                            image(IMG["docker"], "Логотип Docker"),
                            list_block([
                                "Образ (image) — шаблон для контейнера",
                                "Контейнер — запущенный экземпляр образа",
                                "Dockerfile — инструкция сборки образа",
                                "Registry (Docker Hub) — хранилище образов",
                            ]),
                        ],
                    },
                    {
                        "title": "Базовые команды Docker",
                        "blocks": [
                            header("CLI Docker", 2),
                            code(
                                "docker pull nginx:latest\n"
                                "docker run -d -p 8080:80 --name web nginx\n"
                                "docker ps                  # запущенные\n"
                                "docker ps -a               # все\n"
                                "docker logs web\n"
                                "docker stop web && docker rm web"
                            ),
                            paragraph(
                                "-d — фоновый режим, -p host:container — проброс портов, "
                                "--name — имя контейнера."
                            ),
                        ],
                    },
                    {
                        "title": "Dockerfile",
                        "blocks": [
                            header("Сборка образа", 2),
                            code(
                                "FROM python:3.12-slim\n"
                                "WORKDIR /app\n"
                                "COPY requirements.txt .\n"
                                "RUN pip install --no-cache-dir -r requirements.txt\n"
                                "COPY . .\n"
                                "EXPOSE 8000\n"
                                "CMD ['gunicorn', 'mysite.wsgi:application', '--bind', '0.0.0.0:8000']"
                            ),
                            code(
                                "docker build -t myapp:1.0 .\n"
                                "docker run -p 8000:8000 myapp:1.0"
                            ),
                        ],
                    },
                ],
            },
            {
                "title": "Docker: Compose и сети",
                "description": "Мультиконтейнерные приложения, volumes.",
                "lessons": [
                    {
                        "title": "docker-compose",
                        "blocks": [
                            header("Оркестрация контейнеров", 2),
                            image(IMG["docker_compose"], "docker-compose: web + db в одной сети"),
                            code(
                                "# docker-compose.yml\n"
                                "services:\n"
                                "  web:\n"
                                "    build: .\n"
                                "    ports:\n"
                                "      - '8000:8000'\n"
                                "    depends_on:\n"
                                "      - db\n"
                                "    environment:\n"
                                "      - DATABASE_URL=postgres://user:pass@db:5432/mydb\n"
                                "  db:\n"
                                "    image: postgres:16\n"
                                "    volumes:\n"
                                "      - pgdata:/var/lib/postgresql/data\n"
                                "volumes:\n"
                                "  pgdata:"
                            ),
                            code("docker compose up -d\ndocker compose down"),
                        ],
                    },
                    {
                        "title": "Volumes и персистентность",
                        "blocks": [
                            header("Тома данных", 2),
                            paragraph(
                                "Контейнеры эфемерны — при удалении данные теряются. "
                                "Volumes сохраняют данные на хосте."
                            ),
                            code(
                                "docker volume create mydata\n"
                                "docker run -v mydata:/data alpine\n\n"
                                "# Bind mount — привязка к папке хоста\n"
                                "docker run -v $(pwd):/app -w /app python:3.12 python script.py"
                            ),
                        ],
                    },
                    {
                        "title": "Сети Docker",
                        "blocks": [
                            header("Docker Networking", 2),
                            code(
                                "docker network create mynet\n"
                                "docker run --network mynet --name api myapi\n"
                                "docker run --network mynet --name db postgres\n"
                                "# api обращается к db по имени хоста 'db'"
                            ),
                            list_block([
                                "bridge — сеть по умолчанию для контейнеров",
                                "host — использует сеть хоста напрямую",
                                "none — без сети",
                                "Контейнеры в одной сети видят друг друга по имени",
                            ]),
                        ],
                    },
                ],
            },
            {
                "title": "Docker: Практика и best practices",
                "description": "Оптимизация образов, .dockerignore, деплой.",
                "lessons": [
                    {
                        "title": "Оптимизация образов",
                        "blocks": [
                            header("Многоступенчатая сборка", 2),
                            code(
                                "FROM python:3.12 AS builder\n"
                                "WORKDIR /app\n"
                                "COPY requirements.txt .\n"
                                "RUN pip install --prefix=/install -r requirements.txt\n\n"
                                "FROM python:3.12-slim\n"
                                "COPY --from=builder /install /usr/local\n"
                                "COPY . /app\n"
                                "WORKDIR /app\n"
                                "CMD ['python', 'app.py']"
                            ),
                            paragraph(
                                "Используйте slim/alpine образы, кэшируйте слои "
                                "(COPY requirements.txt до COPY .), "
                                "добавьте .dockerignore."
                            ),
                        ],
                    },
                    {
                        "title": ".dockerignore",
                        "blocks": [
                            header("Исключения при сборке", 2),
                            code(
                                "# .dockerignore\n"
                                "venv/\n"
                                "__pycache__/\n"
                                ".git/\n"
                                "*.pyc\n"
                                ".env\n"
                                "db.sqlite3\n"
                                "htmlcov/\n"
                                "node_modules/"
                            ),
                        ],
                    },
                    {
                        "title": "Деплой контейнеров",
                        "blocks": [
                            header("Продакшен-деплой", 2),
                            list_block([
                                "Используйте конкретные теги образов (не :latest)",
                                "Настройте healthcheck в Dockerfile",
                                "Ограничьте ресурсы: --memory, --cpus",
                                "CI/CD: build → push to registry → deploy",
                                "Мониторинг: docker stats, логи, Prometheus",
                            ], ordered=True),
                            quote(
                                "Контейнеры не заменяют оркестраторы (Kubernetes) "
                                "на больших проектах, но идеальны для разработки "
                                "и небольших сервисов.",
                                "Best practice",
                            ),
                        ],
                    },
                ],
            },
        ],
    },
    LIGHT_PYTHON_COURSE,
]
