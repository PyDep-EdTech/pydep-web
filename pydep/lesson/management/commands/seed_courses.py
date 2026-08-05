from django.core.management.base import BaseCommand
from django.db import transaction

from lesson.models import Category
from lesson.models import Course
from lesson.models import Lesson
from lesson.models import LessonsInModule
from lesson.models import Module
from lesson.models import ModulesInCourse
from lesson.seed_data.courses import CATEGORIES
from lesson.seed_data.courses import COURSE_MODULE_IMAGES
from lesson.seed_data.courses import COURSES


class Command(BaseCommand):
    help = (
        "Наполняет БД полноценными учебными курсами: "
        "категории, модули, уроки с теорией и иллюстрациями"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Удалить ранее созданные seed-курсы перед загрузкой",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["clear"]:
            self._clear_seed_courses()

        self.stdout.write(self.style.MIGRATE_HEADING("Создание категорий"))
        categories = {}
        for name in CATEGORIES:
            cat, created = Category.objects.get_or_create(name=name)
            categories[name] = cat
            status = "создана" if created else "существует"
            self.stdout.write(f"  [{status}] {name}")

        total_courses = 0
        total_modules = 0
        total_lessons = 0

        self.stdout.write(self.style.MIGRATE_HEADING("Создание курсов"))
        for course_data in COURSES:
            cat = categories[course_data["category"]]
            course, created = Course.objects.update_or_create(
                name=course_data["name"],
                defaults={
                    "description": course_data["description"],
                    "price": course_data["price"],
                    "image": course_data["image"],
                    "duration": course_data["duration"],
                    "level": course_data["level"],
                    "category": cat,
                    "programming_language": course_data["programming_language"],
                    "is_published": True,
                },
            )
            total_courses += 1
            action = "создан" if created else "обновлён"
            self.stdout.write(
                self.style.SUCCESS(f"  Курс {action}: {course.name}")
            )

            expected_module_titles = {
                mod_data["title"] for mod_data in course_data["modules"]
            }
            stale_links = ModulesInCourse.objects.filter(course=course).exclude(
                module__title__in=expected_module_titles
            )
            if stale_links.exists():
                removed = stale_links.count()
                stale_links.delete()
                self.stdout.write(
                    f"    отвязано устаревших модулей: {removed}"
                )

            for mod_idx, mod_data in enumerate(course_data["modules"], start=1):
                module_image = COURSE_MODULE_IMAGES.get(
                    course_data["name"], []
                )
                mod_image = (
                    module_image[mod_idx - 1]
                    if mod_idx - 1 < len(module_image)
                    else module_image[-1] if module_image else ""
                )
                module, mod_created = Module.objects.update_or_create(
                    title=mod_data["title"],
                    defaults={
                        "description": mod_data["description"],
                        "image": mod_image,
                    },
                )
                total_modules += 1

                ModulesInCourse.objects.update_or_create(
                    course=course,
                    module=module,
                    defaults={"sequence_number": mod_idx},
                )

                expected_titles = {
                    (
                        les["title"]
                        if course_data.get("plain_lesson_titles")
                        else f"{course.name} — {les['title']}"
                    )
                    for les in mod_data["lessons"]
                }
                stale_lessons = LessonsInModule.objects.filter(
                    module=module
                ).exclude(lesson__title__in=expected_titles)
                if stale_lessons.exists():
                    stale_lessons.delete()

                for les_idx, les_data in enumerate(mod_data["lessons"], start=1):
                    if course_data.get("plain_lesson_titles"):
                        lesson_title = les_data["title"]
                    else:
                        lesson_title = f"{course.name} — {les_data['title']}"

                    lesson, _ = Lesson.objects.update_or_create(
                        title=lesson_title,
                        defaults={
                            "description": "",
                            "content_blocks": les_data["blocks"],
                        },
                    )
                    total_lessons += 1

                    LessonsInModule.objects.update_or_create(
                        module=module,
                        lesson=lesson,
                        defaults={"sequence_number": les_idx},
                    )

            if course_data.get("plain_lesson_titles"):
                removed_old, _ = Lesson.objects.filter(
                    title__startswith=f"{course.name} — "
                ).delete()
                if removed_old:
                    self.stdout.write(
                        f"    удалено уроков со старым префиксом: {removed_old}"
                    )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Готово! Курсов: {total_courses}, "
                f"модулей: {total_modules}, уроков: {total_lessons}"
            )
        )

    def _clear_seed_courses(self):
        names = [c["name"] for c in COURSES]
        deleted, _ = Course.objects.filter(name__in=names).delete()
        self.stdout.write(
            self.style.WARNING(f"Удалено seed-объектов: {deleted}")
        )
