"""Курс «Такой "лёгкий" Python» — мягкий ввод в программирование."""

from lesson.seed_data.light_python_modules import LIGHT_PYTHON_MODULES

COURSE_NAME = 'Такой "лёгкий" Python'

LIGHT_PYTHON_COURSE = {
    "name": COURSE_NAME,
    "description": (
        "Подробный курс для новичков: пошаговая теория, иллюстрации, "
        "примеры кода с показом результата в терминале и уроки практики. "
        "От print() до самостоятельных мини-проектов — 6 модулей, 22 урока."
    ),
    "price": 0,
    "image": "courses/seed/course-python.png",
    "duration": 8,
    "level": "С нуля",
    "category": "Программирование",
    "programming_language": "Python",
    "plain_lesson_titles": True,
    "modules": LIGHT_PYTHON_MODULES,
}
