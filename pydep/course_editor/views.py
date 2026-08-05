import uuid
import json
import logging
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import CreateLessonForm, CourseForm, ModuleForm
from .permissions import (
    can_edit_course,
    can_edit_lesson,
    can_edit_module,
    require_course_edit,
    require_lesson_edit,
    require_module_edit,
)
from lesson.models import (
    Course,
    Lesson,
    LessonsInModule,
    Module,
    ModulesInCourse,
    PracticeTask,
)

logger = logging.getLogger(__name__)


def _course_modules_ordered(course):
    return (
        ModulesInCourse.objects.filter(course=course)
        .select_related("module")
        .prefetch_related(
            "module__lessonsinmodule_set__lesson"
        )
        .order_by("sequence_number")
    )


def _module_lessons_ordered(module):
    return (
        LessonsInModule.objects.filter(module=module)
        .select_related("lesson")
        .order_by("sequence_number")
    )


def _build_course_tree(course):
    tree = []
    for mic in _course_modules_ordered(course):
        lessons = [
            {
                "lesson": lim.lesson,
                "sequence": lim.sequence_number,
            }
            for lim in _module_lessons_ordered(mic.module)
        ]
        tree.append(
            {
                "module": mic.module,
                "sequence": mic.sequence_number,
                "lessons": lessons,
                "lesson_count": len(lessons),
            }
        )
    return tree


def _course_stats(course):
    tree = _build_course_tree(course)
    module_count = len(tree)
    lesson_count = sum(item["lesson_count"] for item in tree)
    return {
        "module_count": module_count,
        "lesson_count": lesson_count,
    }


def _save_modules_order(course, module_ids, user):
    ModulesInCourse.objects.filter(course=course).delete()
    for sequence_number, module_id in enumerate(module_ids, start=1):
        try:
            module = Module.objects.get(pk=module_id)
        except Module.DoesNotExist:
            continue
        if not can_edit_module(user, module):
            continue
        ModulesInCourse.objects.create(
            course=course,
            module=module,
            sequence_number=sequence_number,
        )


def _save_lessons_order(module, lesson_ids, user):
    LessonsInModule.objects.filter(module=module).delete()
    for sequence_number, lesson_id in enumerate(lesson_ids, start=1):
        try:
            lesson = Lesson.objects.get(pk=lesson_id)
        except Lesson.DoesNotExist:
            continue
        if not can_edit_lesson(user, lesson):
            continue
        LessonsInModule.objects.create(
            module=module,
            lesson=lesson,
            sequence_number=sequence_number,
        )


def _attach_module_to_course(course, module, user):
    if not can_edit_module(user, module):
        return False
    if ModulesInCourse.objects.filter(course=course, module=module).exists():
        return True
    last = (
        ModulesInCourse.objects.filter(course=course)
        .order_by("-sequence_number")
        .values_list("sequence_number", flat=True)
        .first()
    )
    ModulesInCourse.objects.create(
        course=course,
        module=module,
        sequence_number=(last or 0) + 1,
    )
    return True


def _attach_lesson_to_module(module, lesson, user):
    if not can_edit_lesson(user, lesson):
        return False
    if LessonsInModule.objects.filter(module=module, lesson=lesson).exists():
        return True
    last = (
        LessonsInModule.objects.filter(module=module)
        .order_by("-sequence_number")
        .values_list("sequence_number", flat=True)
        .first()
    )
    LessonsInModule.objects.create(
        module=module,
        lesson=lesson,
        sequence_number=(last or 0) + 1,
    )
    return True


@login_required
@require_http_methods(["GET", "POST"])
def upload_image(request):
    if request.method != "POST":
        return JsonResponse({"success": 0, "error": "Метод не разрешен"}, status=405)

    if "image" not in request.FILES:
        return JsonResponse({"success": 0, "error": "Файл не найден"}, status=400)

    image_file = request.FILES["image"]
    allowed_types = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/webp",
    ]
    if image_file.content_type not in allowed_types:
        return JsonResponse(
            {
                "success": 0,
                "error": "Неподдерживаемый формат. Разрешены: JPG, PNG, GIF, WebP",
            },
            status=400,
        )

    max_size = 10 * 1024 * 1024
    if image_file.size > max_size:
        return JsonResponse(
            {"success": 0, "error": "Файл слишком большой. Максимум: 10 МБ"},
            status=400,
        )

    try:
        file_extension = (
            image_file.name.split(".")[-1] if "." in image_file.name else "jpg"
        )
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        date_path = datetime.now().strftime("%Y/%m/%d")
        file_path = default_storage.save(
            f"editorjs/{date_path}/{unique_filename}",
            ContentFile(image_file.read()),
        )
        file_url = default_storage.url(file_path)
        if not file_url.startswith("http") and not file_url.startswith("/"):
            file_url = "/" + file_url.lstrip("/")
        return JsonResponse({"success": 1, "url": file_url})
    except Exception as exc:
        logger.exception("Ошибка загрузки изображения: %s", exc)
        return JsonResponse(
            {"success": 0, "error": f"Ошибка при сохранении файла: {exc}"},
            status=500,
        )


@login_required
def course_editor_main(request):
    courses = request.user.authored_courses.all()
    published_count = courses.filter(is_published=True).count()
    context = {
        "courses_count": courses.count(),
        "published_count": published_count,
        "draft_count": courses.count() - published_count,
        "recent_courses": courses.order_by("-id")[:3],
    }
    return render(request, "course_editor/course_editor_main.html", context)


@login_required
def my_courses(request):
    courses = (
        request.user.authored_courses.annotate(
            module_count=Count(
                "modulesincourse",
                distinct=True,
            ),
            lesson_count=Count(
                "modulesincourse__module__lessonsinmodule",
                distinct=True,
            ),
        )
        .order_by("-id")
    )
    return render(request, "course_editor/my_courses.html", {"courses": courses})


@login_required
def course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            if not course.programming_language:
                course.programming_language = "—"
            course.save()
            course.authors.add(request.user)
            messages.success(request, f"Курс «{course.name}» создан. Настройте структуру.")
            return redirect("studio:course_edit", course_id=course.id)
        messages.error(request, "Исправьте ошибки в форме.")
    else:
        form = CourseForm()

    return render(
        request,
        "course_editor/course_create.html",
        {"form": form, "course": None},
    )


@login_required
def course_edit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    require_course_edit(request.user, course)

    if request.method == "POST":
        if "toggle_publish" in request.POST:
            course.is_published = not course.is_published
            course.save(update_fields=["is_published"])
            if course.is_published:
                messages.success(request, f"Курс «{course.name}» опубликован.")
            else:
                messages.warning(request, f"Курс «{course.name}» скрыт.")
            return redirect("studio:course_edit", course_id=course.id)

        if "detach_module" in request.POST:
            module_id = request.POST.get("module_id")
            ModulesInCourse.objects.filter(
                course=course,
                module_id=module_id,
            ).delete()
            messages.info(request, "Модуль откреплён от курса.")
            return redirect("studio:course_edit", course_id=course.id)

        if "attach_module" in request.POST:
            module_id = request.POST.get("module_id")
            module = get_object_or_404(Module, pk=module_id)
            if _attach_module_to_course(course, module, request.user):
                messages.success(request, f"Модуль «{module.title}» добавлен в курс.")
            return redirect("studio:course_edit", course_id=course.id)

        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            saved_course = form.save()
            modules_order = request.POST.get("modules_order", "")
            if modules_order:
                module_ids = [
                    int(item.strip())
                    for item in modules_order.split(",")
                    if item.strip().isdigit()
                ]
                _save_modules_order(saved_course, module_ids, request.user)
            messages.success(request, f"Курс «{saved_course.name}» сохранён.")
            return redirect("studio:course_edit", course_id=saved_course.id)
        messages.error(request, "Исправьте ошибки в форме.")
    else:
        form = CourseForm(instance=course)

    course_tree = _build_course_tree(course)
    attached_ids = [item["module"].id for item in course_tree]
    available_modules = (
        request.user.authored_modules.exclude(id__in=attached_ids).order_by("title")
    )
    available_modules_data = [
        {
            "id": m.id,
            "title": m.title,
            "subtitle": (m.description or "")[:120],
        }
        for m in available_modules
    ]
    stats = _course_stats(course)

    context = {
        "form": form,
        "course": course,
        "course_tree": course_tree,
        "available_modules": available_modules,
        "available_modules_data": available_modules_data,
        "stats": stats,
        "studio_section": "settings",
    }
    return render(request, "course_editor/course_studio.html", context)


@login_required
def module_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    require_course_edit(request.user, course)

    if request.method == "POST":
        form = ModuleForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                module = form.save(commit=False)
                module.save()
                module.authors.add(request.user)
                _attach_module_to_course(course, module, request.user)

                lessons_order = request.POST.get("lessons_order", "")
                if lessons_order:
                    lesson_ids = [
                        int(item.strip())
                        for item in lessons_order.split(",")
                        if item.strip().isdigit()
                    ]
                    _save_lessons_order(module, lesson_ids, request.user)

            messages.success(
                request,
                f"Модуль «{module.title}» создан и добавлен в курс.",
            )
            return redirect("studio:module_edit", course_id=course.id, module_id=module.id)
        messages.error(request, "Исправьте ошибки в форме.")
    else:
        form = ModuleForm()

    lessons = request.user.authored_lessons.order_by("title")
    context = {
        "form": form,
        "course": course,
        "module": None,
        "lessons": lessons,
        "existing_lesson_ids": [],
        "course_tree": _build_course_tree(course),
        "stats": _course_stats(course),
        "studio_section": "module",
    }
    return render(request, "course_editor/module_edit.html", context)


@login_required
def module_edit(request, course_id, module_id):
    course = get_object_or_404(Course, pk=course_id)
    module = get_object_or_404(Module, pk=module_id)
    require_course_edit(request.user, course)
    require_module_edit(request.user, module)

    if not ModulesInCourse.objects.filter(course=course, module=module).exists():
        messages.warning(request, "Модуль не привязан к этому курсу.")
        return redirect("studio:course_edit", course_id=course.id)

    if request.method == "POST":
        if "detach_lesson" in request.POST:
            lesson_id = request.POST.get("lesson_id")
            LessonsInModule.objects.filter(module=module, lesson_id=lesson_id).delete()
            messages.info(request, "Урок откреплён от модуля.")
            return redirect(
                "studio:module_edit",
                course_id=course.id,
                module_id=module.id,
            )

        if "attach_lesson" in request.POST:
            lesson = get_object_or_404(Lesson, pk=request.POST.get("lesson_id"))
            if _attach_lesson_to_module(module, lesson, request.user):
                messages.success(request, f"Урок «{lesson.title}» добавлен в модуль.")
            return redirect(
                "studio:module_edit",
                course_id=course.id,
                module_id=module.id,
            )

        form = ModuleForm(request.POST, request.FILES, instance=module)
        if form.is_valid():
            form.save()
            lessons_order = request.POST.get("lessons_order", "")
            if lessons_order:
                lesson_ids = [
                    int(item.strip())
                    for item in lessons_order.split(",")
                    if item.strip().isdigit()
                ]
                _save_lessons_order(module, lesson_ids, request.user)
            messages.success(request, f"Модуль «{module.title}» сохранён.")
            return redirect("studio:course_edit", course_id=course.id)
        messages.error(request, "Исправьте ошибки в форме.")
    else:
        form = ModuleForm(instance=module)

    existing_lessons = _module_lessons_ordered(module)
    existing_lesson_ids = [lim.lesson_id for lim in existing_lessons]
    attached_lessons = [lim.lesson for lim in existing_lessons]
    available_lessons = (
        request.user.authored_lessons.exclude(id__in=existing_lesson_ids).order_by("title")
    )
    available_lessons_data = [
        {
            "id": lesson.id,
            "title": lesson.title,
            "subtitle": "Есть контент" if lesson.has_blocks() else "Без контента",
        }
        for lesson in available_lessons
    ]

    context = {
        "form": form,
        "module": module,
        "course": course,
        "attached_lessons": attached_lessons,
        "available_lessons": available_lessons,
        "available_lessons_data": available_lessons_data,
        "existing_lesson_ids": existing_lesson_ids,
        "course_tree": _build_course_tree(course),
        "stats": _course_stats(course),
        "studio_section": "module",
        "active_module_id": module.id,
    }
    return render(request, "course_editor/module_edit.html", context)


@login_required
def lesson_create(request, course_id, module_id):
    course = get_object_or_404(Course, pk=course_id)
    module = get_object_or_404(Module, pk=module_id)
    require_course_edit(request.user, course)
    require_module_edit(request.user, module)

    if request.method == "POST":
        form = CreateLessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.save()
            lesson.authors.add(request.user)
            _attach_lesson_to_module(module, lesson, request.user)
            messages.success(request, f"Урок «{lesson.title}» создан.")
            return redirect(
                "studio:lesson_edit",
                course_id=course_id,
                module_id=module_id,
                lesson_id=lesson.id,
            )
    else:
        form = CreateLessonForm()

    context = {
        "form": form,
        "lesson": None,
        "course": course,
        "module": module,
        "course_tree": _build_course_tree(course),
        "stats": _course_stats(course),
        "studio_section": "lesson",
        "active_module_id": module.id,
    }
    return render(request, "course_editor/lesson_edit.html", context)


@login_required
def lesson_edit(request, course_id, module_id, lesson_id):
    course = get_object_or_404(Course, pk=course_id)
    module = get_object_or_404(Module, pk=module_id)
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    require_course_edit(request.user, course)
    require_module_edit(request.user, module)
    require_lesson_edit(request.user, lesson)

    if request.method == "POST":
        form = CreateLessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, f"Урок «{lesson.title}» сохранён.")
            return redirect(
                "studio:lesson_edit",
                course_id=course_id,
                module_id=module_id,
                lesson_id=lesson.id,
            )
    else:
        form = CreateLessonForm(instance=lesson)

    context = {
        "form": form,
        "lesson": lesson,
        "course": course,
        "module": module,
        "practice_tasks": lesson.practice_tasks.all(),
        "course_tree": _build_course_tree(course),
        "stats": _course_stats(course),
        "studio_section": "lesson",
        "active_module_id": module.id,
        "active_lesson_id": lesson.id,
    }
    return render(request, "course_editor/lesson_edit.html", context)


def _practice_task_payload(task):
    return {
        "id": task.id,
        "title": task.title,
        "statement": task.statement,
        "starter_code": task.starter_code,
        "expected_output": task.expected_output,
        "has_check": task.has_check,
        "position": task.position,
    }


@login_required
@require_http_methods(["POST"])
def practice_task_save(request, course_id, module_id, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    require_lesson_edit(request.user, lesson)

    title = (request.POST.get("title") or "").strip()
    statement = (request.POST.get("statement") or "").strip()
    if not title:
        return JsonResponse({"ok": False, "error": "Укажите заголовок задания."}, status=400)
    if not statement:
        return JsonResponse({"ok": False, "error": "Опишите условие задания."}, status=400)

    starter_code = request.POST.get("starter_code") or ""
    expected_output = request.POST.get("expected_output") or ""

    task_id = request.POST.get("task_id")
    if task_id:
        task = get_object_or_404(PracticeTask, pk=task_id, lesson=lesson)
    else:
        task = PracticeTask(lesson=lesson, created_by=request.user)
        last = (
            lesson.practice_tasks.order_by("-position")
            .values_list("position", flat=True)
            .first()
        )
        task.position = (last or 0) + 1

    task.title = title
    task.statement = statement
    task.starter_code = starter_code
    task.expected_output = expected_output
    task.save()
    return JsonResponse({"ok": True, "task": _practice_task_payload(task)})


@login_required
@require_http_methods(["POST"])
def practice_task_delete(request, course_id, module_id, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    require_lesson_edit(request.user, lesson)
    task = get_object_or_404(PracticeTask, pk=request.POST.get("task_id"), lesson=lesson)
    task.delete()
    return JsonResponse({"ok": True})


@login_required
@require_http_methods(["POST"])
def practice_task_reorder(request, course_id, module_id, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    require_lesson_edit(request.user, lesson)
    try:
        order = json.loads(request.body.decode("utf-8")).get("order") or []
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Неверный JSON"}, status=400)
    for position, task_id in enumerate(order, start=1):
        PracticeTask.objects.filter(pk=task_id, lesson=lesson).update(position=position)
    return JsonResponse({"ok": True})


@login_required
@require_http_methods(["POST"])
def studio_reorder(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Неверный JSON"}, status=400)

    reorder_type = payload.get("type")
    course = get_object_or_404(Course, pk=payload.get("course_id"))
    require_course_edit(request.user, course)

    if reorder_type == "modules":
        order = payload.get("order") or []
        if not isinstance(order, list):
            return JsonResponse({"ok": False, "error": "Неверный порядок"}, status=400)
        _save_modules_order(course, order, request.user)
        return JsonResponse({"ok": True})

    if reorder_type == "lessons":
        module = get_object_or_404(Module, pk=payload.get("module_id"))
        require_module_edit(request.user, module)
        order = payload.get("order") or []
        if not isinstance(order, list):
            return JsonResponse({"ok": False, "error": "Неверный порядок"}, status=400)
        _save_lessons_order(module, order, request.user)
        return JsonResponse({"ok": True})

    return JsonResponse({"ok": False, "error": "Неизвестный тип"}, status=400)
