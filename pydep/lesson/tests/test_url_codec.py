from django.urls import reverse

from lesson.slugs import translit_slug


def test_translit_slug_cyrillic():
    assert translit_slug("Файлы и ошибки") == "fajly-i-oshibki"
    assert translit_slug('Такой "лёгкий" Python') == "takoj-legkij-python"


def test_lesson_detail_reverse_uses_translit_slugs(db):
    from lesson.models import Category, Course, Lesson, Module

    category = Category.objects.create(name="Prog")
    lesson = Lesson.objects.create(title="Обработка ошибок try / except")
    module = Module.objects.create(title="Файлы и ошибки", description="d", image="t/x.jpg")
    module.lessons.add(lesson)
    course = Course.objects.create(
        name='Такой "лёгкий" Python',
        description="d",
        image="t/x.jpg",
        programming_language="Python",
        category=category,
        price=0,
    )
    course.modules.add(module)

    url = reverse(
        "lesson:lesson_detail",
        kwargs={
            "course_slug": course.slug,
            "module_slug": module.slug,
            "lesson_slug": lesson.slug,
        },
    )
    assert "/course/" in url
    assert course.slug in url
    assert module.slug in url
    assert lesson.slug in url
    assert "Файлы" not in url
    assert "%D0" not in url
