import json
from urllib.parse import unquote

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import EditProfile
from .models import Course
from .models import Module
from .models import Lesson
from .models import Category
from .models import PracticeTask
from .models import UserLessonProgress
from .models import CourseEnrollment
from .models import ModulesInCourse
from .models import LessonsInModule
from .paginator import paginator
from .search import SORT_CHOICES
from .search import apply_course_filters
from .search import distinct_languages
from .search import distinct_levels
from .search import expand_query


def _course_celebration_key(course_id):
    return f"course_celebration_{course_id}"


def _course_is_fully_completed(user, course):
    total_lessons = 0
    for module in course.ordered_modules():
        total_lessons += module.ordered_lessons().count()
    if total_lessons == 0:
        return False
    completed = UserLessonProgress.objects.filter(
        user=user,
        course=course,
        completed=True,
    ).count()
    return completed >= total_lessons


def _get_course_by_slug(course_slug):
    return get_object_or_404(Course, slug=course_slug)


def _get_course_module(course_slug, module_slug):
    course = _get_course_by_slug(course_slug)
    module = get_object_or_404(Module, slug=module_slug)
    if not ModulesInCourse.objects.filter(course=course, module=module).exists():
        raise Http404("Модуль не входит в курс")
    return course, module


def _get_course_module_lesson(course_slug, module_slug, lesson_slug):
    course, module = _get_course_module(course_slug, module_slug)
    lesson = get_object_or_404(Lesson, slug=lesson_slug)
    if not LessonsInModule.objects.filter(module=module, lesson=lesson).exists():
        raise Http404("Урок не входит в модуль")
    return course, module, lesson


def query_params_in_dict(query_params: str) -> dict:
    query_params = query_params.replace("&", " ").replace("=", " ").split()
    return {
        query_params[i]: query_params[i + 1]
        for i in range(0, len(query_params) - 1, 2)
    } if query_params else {}


def _parse_category_slugs(request) -> list[str]:
    slugs = list(request.GET.getlist("category"))
    if slugs:
        return slugs
    legacy = request.GET.get("category")
    if legacy:
        return [s for s in unquote(legacy).split(",") if s]
    return []


def _courses_base_queryset() -> QuerySet[Course]:
    return Course.objects.prefetch_related("modules", "category")


def courses_list(request, queryset=None):
    """Каталог курсов с умным поиском и фильтрами."""
    categories = Category.objects.all()
    selected_category_slugs = _parse_category_slugs(request)
    query = request.GET.get("q", "")
    level = request.GET.get("level", "")
    language = request.GET.get("lang", "")
    sort = request.GET.get("sort", "relevance" if query else "name")
    if sort not in SORT_CHOICES:
        sort = "relevance" if query else "name"

    base = queryset if queryset is not None else _courses_base_queryset()
    courses_qs, search_hits, meta = apply_course_filters(
        base,
        query=query,
        category_slugs=selected_category_slugs or None,
        level=level,
        language=language,
        sort=sort,
    )

    hit_map = {hit.course.id: hit for hit in search_hits}

    default_sort = "relevance" if query else "name"
    active_filter_count = len(selected_category_slugs)
    if level:
        active_filter_count += 1
    if language:
        active_filter_count += 1
    if sort != default_sort:
        active_filter_count += 1

    context = {
        "courses": paginator(request, courses_qs),
        "categories": categories,
        "selected_category_slugs": selected_category_slugs,
        "selected_level": level,
        "selected_language": language,
        "selected_sort": sort,
        "search_query": meta.get("query", ""),
        "search_variants": meta.get("variants", []),
        "search_hit_map": hit_map,
        "result_count": meta.get("total_before_pagination", 0),
        "languages": distinct_languages(_courses_base_queryset().filter(is_published=True)),
        "levels": distinct_levels(),
        "sort_choices": SORT_CHOICES,
        "active_filter_count": active_filter_count,
        "filters_expanded": active_filter_count > 0,
    }

    return render(
        request,
        template_name="lesson/courses_list.html",
        context=context,
    )


def course_search_api(request):
    """JSON-подсказки для живого поиска в каталоге."""
    query = request.GET.get("q", "").strip()
    if len(query) < 2:
        return JsonResponse({"query": query, "total": 0, "results": [], "variants": []})

    selected_category_slugs = _parse_category_slugs(request)
    level = request.GET.get("level", "")
    language = request.GET.get("lang", "")

    courses_qs, search_hits, meta = apply_course_filters(
        _courses_base_queryset(),
        query=query,
        category_slugs=selected_category_slugs or None,
        level=level,
        language=language,
        sort="relevance",
    )

    results = []
    for hit in search_hits[:8]:
        course = hit.course
        results.append({
            "id": course.id,
            "name": course.name,
            "language": course.programming_language,
            "level": course.level,
            "category": course.category.name if course.category_id else "",
            "price": course.price,
            "monthly_price": course.monthly_price,
            "image": course.image.url if course.image else "",
            "url": reverse("lesson:course_detail", kwargs={"course_slug": course.slug}),
            "matched_in": hit.matched_in,
            "score": hit.score,
        })

    return JsonResponse({
        "query": meta.get("query", ""),
        "variants": expand_query(query)[:6],
        "total": len(search_hits),
        "results": results,
    })


def index(request):
    """
    Отображение главной страницы
    """
    return render(request, 'lesson/index.html')


def page_not_found(request, exception):
    return render(request, '404.html', status=404)


def server_error(request):
    return render(request, '500.html', status=500)


def permission_denied_page(request, exception):
    return render(request, '403.html', status=403)


def normalize_playground_output(text):
    """Сверка вывода в песочнице (та же логика, что в python-playground.js)."""
    normalized = str(text).replace('\r', '')
    lines = [line.rstrip() for line in normalized.split('\n')]
    return '\n'.join(lines).rstrip('\n')


def python_playground(request):
    """
    Встроенный Python-интерпретатор в браузере (Pyodide — настоящий CPython 3
    в WebAssembly). Код выполняется только на клиенте: сервер код не принимает
    и не запускает.

    С параметром ?lesson=<id> открывается в режиме практики: в боковой панели
    показываются задания, привязанные к уроку.
    """
    tasks = []
    lesson_title = ''
    lesson_id = request.GET.get('lesson')
    if lesson_id and str(lesson_id).isdigit():
        lesson_obj = Lesson.objects.filter(pk=lesson_id).first()
        if lesson_obj:
            lesson_title = lesson_obj.title
            for t in lesson_obj.practice_tasks.all():
                tasks.append({
                    'id': t.id,
                    'title': t.title,
                    'statement': t.statement,
                    'starter': t.starter_code,
                    'has_check': t.has_check,
                })
    return render(request, "lesson/python_playground.html", {
        'pg_tasks': tasks,
        'pg_lesson_title': lesson_title,
    })


def python_playground_runner(request):
    """Минимальная страница для изолированного запуска Pyodide в sandbox-iframe."""
    return render(request, 'lesson/python_playground_runner.html')


@require_POST
def python_playground_check(request):
    """
    Сверка вывода программы с эталоном задания.
    Ожидаемый вывод хранится только на сервере — в HTML не отдаётся.
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'invalid_json'}, status=400)

    task_id = payload.get('task_id')
    output = payload.get('output', '')

    if not task_id:
        return JsonResponse({'error': 'missing_task_id'}, status=400)

    task = PracticeTask.objects.filter(pk=task_id).first()
    if not task or not task.has_check:
        return JsonResponse({'error': 'task_not_found'}, status=404)

    got = normalize_playground_output(output)
    expected = normalize_playground_output(task.expected_output)
    ok = got == expected

    response = {'ok': ok}
    if not ok:
        response['expected'] = task.expected_output
        response['got'] = output
    return JsonResponse(response)


def category_detail(request, slug):
    categories = Category.objects.all()
    category = Category.objects.get(slug=slug)
    courses = Course.objects.filter(category=category, is_published=True)
    return render(
        request,
        "lesson/courses_list.html",
        {
            "courses": paginator(request, courses),
            "categories": categories,
            "category": category,
            "selected_category_slugs": [slug],
            "selected_level": "",
            "selected_language": "",
            "selected_sort": "name",
            "search_query": "",
            "search_variants": [],
            "search_hit_map": {},
            "result_count": courses.count(),
            "languages": distinct_languages(),
            "levels": distinct_levels(),
            "sort_choices": SORT_CHOICES,
            "active_filter_count": 1,
            "filters_expanded": True,
        },
    )


@login_required
def course_detail(request, course_slug):
    """
    Получение модулей в курсе и прогресса прохождения курса
    """
    course = _get_course_by_slug(course_slug)
    user_modules = []

    # Заявка на платный курс: пользователь жмёт «Записаться».
    if request.method == 'POST' and not course.is_free:
        enrollment, _ = CourseEnrollment.objects.get_or_create(
            user=request.user, course=course
        )
        # Повторная подача после отказа — снова на рассмотрение.
        if enrollment.status == CourseEnrollment.Status.REJECTED:
            enrollment.status = CourseEnrollment.Status.PENDING
            enrollment.decided_at = None
            enrollment.decided_by = None
            enrollment.save(
                update_fields=['status', 'decided_at', 'decided_by']
            )
        if enrollment.status == CourseEnrollment.Status.APPROVED:
            messages.info(request, 'Вы уже записаны на этот курс.')
        else:
            messages.success(
                request,
                'Заявка отправлена. Курс откроется после одобрения.',
            )
        return redirect('lesson:course_detail', course_slug=course.slug)

    access = course.access_for(request.user)

    # Первый урок открываем только при наличии доступа
    # (бесплатные — всем, платные — после одобрения заявки).
    course_modules = list(course.ordered_modules())
    if access == 'open' and course_modules:
        first_module = course_modules[0]
        first_module_lessons = list(first_module.ordered_lessons())
        if first_module_lessons:
            first_lesson = first_module_lessons[0]
            first_lesson_exists = UserLessonProgress.objects.filter(
                user=request.user,
                course=course,
                module=first_module,
                lesson=first_lesson
            ).exists()

            if not first_lesson_exists:
                UserLessonProgress.objects.filter(
                    user=request.user,
                    course=course
                ).update(current=False)
                UserLessonProgress.objects.create(
                    user=request.user,
                    course=course,
                    module=first_module,
                    lesson=first_lesson,
                    current=True
                )

    total_lessons_count = 0
    total_completed_count = 0
    course_modules_list = list(course.ordered_modules())
    
    # Используем course_modules_list для правильного порядка модулей
    for module_index, module in enumerate(course_modules_list):
        lessons = module.ordered_lessons()
        total_lessons = lessons.count()
        total_lessons_count += total_lessons

        # Фильтруем прогресс по пользователю, курсу, модулю и уроку
        completed_lessons = UserLessonProgress.objects.filter(
            user=request.user,
            course=course,
            module=module,
            lesson__in=lessons,
            completed=True
        ).count()
        total_completed_count += completed_lessons

        # Рассчёт прогресса модуля
        progress = int(
            (completed_lessons / total_lessons) * 100
        ) if total_lessons > 0 else 0

        # Проверка доступности модуля
        is_available = False
        
        # Первый модуль всегда доступен
        if module_index == 0:
            is_available = True
        else:
            # Проверяем, пройден ли предыдущий модуль полностью
            try:
                prev_module = course_modules_list[module_index - 1]
                prev_module_lessons = prev_module.ordered_lessons()
                prev_completed_lessons = UserLessonProgress.objects.filter(
                    user=request.user,
                    course=course,
                    module=prev_module,
                    lesson__in=prev_module_lessons,
                    completed=True
                ).count()
                prev_total_lessons = prev_module_lessons.count()
                
                # Модуль доступен, если предыдущий модуль полностью пройден
                if prev_total_lessons > 0 and prev_completed_lessons == prev_total_lessons:
                    is_available = True
            except (IndexError, AttributeError):
                pass
        
        # Также модуль доступен, если в нем есть текущий урок
        if not is_available:
            has_current_lesson = UserLessonProgress.objects.filter(
                user=request.user,
                course=course,
                module=module,
                current=True
            ).exists()
            if has_current_lesson:
                is_available = True

        # Без доступа к курсу все модули заблокированы.
        if access != 'open':
            is_available = False

        user_modules.append({
            'module': module,
            'progress': progress,
            'completed': progress == 100,
            'completed_lessons': completed_lessons,
            'total_lessons': total_lessons,
            'is_available': is_available,
        })
    
    # Общий прогресс курса - считаем только уроки этого курса у этого пользователя
    total_progress = int(
        (total_completed_count / total_lessons_count) * 100
    ) if total_lessons_count > 0 else 0

    celebration_key = _course_celebration_key(course.pk)
    show_celebration = (
        total_progress == 100
        and total_lessons_count > 0
        and request.session.pop(celebration_key, False)
    )

    context = {
        'course': course,
        'modules': user_modules,
        'access': access,
        'is_free': course.is_free,
        "total_progress": total_progress,
        "total_lessons_count": total_lessons_count,
        "total_completed_count": total_completed_count,
        "show_celebration": show_celebration,
    }
    return render(request, 'lesson/course_detail.html', context)


# @course_required
@login_required
def lesson_detail(request, course_slug, module_slug, lesson_slug):
    """
    Просмотр материалов урока
    """
    course, module, lesson = _get_course_module_lesson(
        course_slug, module_slug, lesson_slug
    )
    if not course.has_access(request.user):
        messages.error(request, 'Сначала запишитесь на курс.')
        return redirect('lesson:course_detail', course_slug=course.slug)
    try:
        les = UserLessonProgress.objects.get(
            user=request.user,
            course=course,
            module=module,
            lesson=lesson
        )
        if not (les.completed or les.current):
            return redirect(
                "lesson:module_detail",
                course_slug=course.slug,
                module_slug=module.slug,
            )
    except Exception:
        return redirect(
            "lesson:module_detail",
            course_slug=course.slug,
            module_slug=module.slug,
        )
    is_completed = UserLessonProgress.objects.get_or_create(
        user=request.user,
        course=course,
        module=module,
        lesson=lesson
    )[0].completed
    context = {
        'course': course,
        'module': module,
        'lesson': lesson,
        "is_completed": is_completed,
        "practice_count": lesson.practice_tasks.count(),
    }
    return render(
        request,
        'lesson/lesson_detail.html',
        context=context
    )


@login_required
def module_detail(request, course_slug, module_slug):
    """
    Получение уроков в модуле. Открытие первого урока если модуль новый
    """
    course, module = _get_course_module(course_slug, module_slug)
    if not course.has_access(request.user):
        messages.error(request, 'Сначала запишитесь на курс.')
        return redirect('lesson:course_detail', course_slug=course.slug)

    # Проверка доступности модуля
    course_modules_list = list(course.ordered_modules())
    try:
        module_index = course_modules_list.index(module)
    except ValueError:
        # Модуль не найден в курсе - редирект на курс
        return redirect('lesson:course_detail', course_slug=course.slug)
    
    # Первый модуль всегда доступен
    if module_index > 0:
        # Проверяем, пройден ли предыдущий модуль полностью
        prev_module = course_modules_list[module_index - 1]
        prev_module_lessons = prev_module.ordered_lessons()
        prev_completed_lessons = UserLessonProgress.objects.filter(
            user=request.user,
            course=course,
            module=prev_module,
            lesson__in=prev_module_lessons,
            completed=True
        ).count()
        prev_total_lessons = prev_module_lessons.count()
        
        # Если предыдущий модуль не пройден полностью и в текущем модуле нет текущего урока
        if prev_total_lessons > 0 and prev_completed_lessons != prev_total_lessons:
            has_current_lesson = UserLessonProgress.objects.filter(
                user=request.user,
                course=course,
                module=module,
                current=True
            ).exists()
            
            if not has_current_lesson:
                # Модуль заблокирован - редирект на курс
                return redirect('lesson:course_detail', course_slug=course.slug)
    
    lessons_module = module.ordered_lessons()

    # Если в модуле не открыт первый урок, назначаем его текущим
    # if module.lessons.all()[0].id not in UserLessonProgress.objects.filter(
    #         user=request.user
    # ).values_list("lesson_id", flat=True):
    #     print(request.user, module.lessons.all()[0])
    #     UserLessonProgress.objects.create(
    #         user=request.user,
    #         course=course,
    #         module=module,
    #         lesson=module.lessons.all()[0],
    #         current=True
    #     )

    # Получаем список уроков в модуле + пройден,
    # текущий или закрыт (Закрыт если записи нет)
    lessons = []
    for lesson in lessons_module:
        try:
            current_lesson = UserLessonProgress.objects.get(
                user=request.user,
                course=course,
                module=module,
                lesson=lesson
            )
            is_completed = current_lesson.completed
            is_current = current_lesson.current
        except Exception:
            is_completed = False
            is_current = False

        lessons.append({
            'lesson': lesson,
            'is_completed': is_completed,
            'is_current': is_current,
        })

    context = {
        'lessons': lessons,
        'course': course,
        'module': module,
    }
    return render(request, 'lesson/module_detail.html', context)


@login_required
def complete_lesson(request, course_slug, module_slug, lesson_slug):
    """
    Отметка урока как пройденного и открытие следующего урока.
    """
    course, module, lesson = _get_course_module_lesson(
        course_slug, module_slug, lesson_slug
    )
    if not course.has_access(request.user):
        messages.error(request, 'Сначала запишитесь на курс.')
        return redirect('lesson:course_detail', course_slug=course.slug)

    # Бесплатный курс попадает в «проходимые» при прохождении первого урока.
    if course.is_free:
        CourseEnrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={
                'status': CourseEnrollment.Status.APPROVED,
                'decided_at': timezone.now(),
            },
        )

    # 1. Отметить текущий урок как завершённый
    progress, created = UserLessonProgress.objects.get_or_create(
        user=request.user,
        course=course,
        module=module,
        lesson=lesson,
    )
    progress.completed = True
    progress.current = False
    progress.save()
    
    # 2. Убрать флаг current у всех уроков этого пользователя в этом курсе
    UserLessonProgress.objects.filter(
        user=request.user,
        course=course
    ).update(current=False)
    
    # 3. Найти следующий урок
    module_lessons = list(module.ordered_lessons())
    course_modules = list(course.ordered_modules())
    
    # Получаем индекс текущего урока в модуле
    try:
        current_lesson_index = module_lessons.index(lesson)
    except ValueError:
        # Если урока нет в списке, редиректим на модуль
        return redirect(
            'lesson:module_detail',
            course_slug=course.slug,
            module_slug=module.slug,
        )
    
    next_module = None
    next_lesson = None
    
    # Проверяем, есть ли следующий урок в текущем модуле
    if current_lesson_index + 1 < len(module_lessons):
        # Есть следующий урок в том же модуле
        next_lesson = module_lessons[current_lesson_index + 1]
        next_module = module
    else:
        # Это последний урок в модуле - ищем следующий модуль
        try:
            current_module_index = course_modules.index(module)
            if current_module_index + 1 < len(course_modules):
                # Есть следующий модуль
                next_module = course_modules[current_module_index + 1]
                next_module_lessons = list(next_module.ordered_lessons())
                if next_module_lessons:
                    next_lesson = next_module_lessons[0]
        except ValueError:
            pass
    
    # 4. Открыть следующий урок, если он найден
    if next_lesson and next_module:
        next_progress, created = UserLessonProgress.objects.get_or_create(
            user=request.user,
            course=course,
            module=next_module,
            lesson=next_lesson,
        )
        next_progress.current = True
        next_progress.save()

        # Следующий урок уже открыт (current=True). Возвращаем пользователя
        # к текущему модулю, чтобы он увидел отметку о прохождении и открытый
        # следующий шаг, а не «выбрасывался» в другой модуль.
        return redirect(
            'lesson:module_detail',
            course_slug=course.slug,
            module_slug=module.slug,
        )

    if _course_is_fully_completed(request.user, course):
        request.session[_course_celebration_key(course.pk)] = True
        messages.success(
            request,
            f'Поздравляем! Курс «{course.name}» пройден полностью!',
        )
        return redirect('lesson:course_detail', course_slug=course.slug)

    # Курс не завершён — остаёмся в текущем модуле
    return redirect(
        'lesson:module_detail',
        course_slug=course.slug,
        module_slug=module.slug,
    )


@login_required
def profile(request):
    """Личный кабинет PyDep: роль, прогресс по курсам, быстрые действия."""
    user = request.user

    roles = []
    if user.is_superuser:
        roles.append('Модератор')
    if user.is_teacher:
        roles.append('Преподаватель')
    if user.is_student:
        roles.append('Студент')
    result = ' & '.join(roles)

    # Курсы, на которые записан пользователь, с прогрессом прохождения.
    enrollments = (
        CourseEnrollment.objects
        .filter(user=user, status=CourseEnrollment.Status.APPROVED)
        .select_related('course')
    )
    # Заявки, ожидающие одобрения админом.
    pending_enrollments = (
        CourseEnrollment.objects
        .filter(user=user, status=CourseEnrollment.Status.PENDING)
        .select_related('course')
    )
    courses_progress = []
    total_done = 0
    total_lessons = 0
    for enrollment in enrollments:
        course = enrollment.course
        module_ids = ModulesInCourse.objects.filter(
            course=course
        ).values_list('module_id', flat=True)
        lessons_count = LessonsInModule.objects.filter(
            module_id__in=module_ids
        ).count()
        done = UserLessonProgress.objects.filter(
            user=user, course=course, completed=True
        ).count()
        pct = round(done / lessons_count * 100) if lessons_count else 0
        total_done += done
        total_lessons += lessons_count
        courses_progress.append({
            'course': course,
            'total': lessons_count,
            'done': done,
            'pct': pct,
            'completed': lessons_count and done >= lessons_count,
        })

    context = {
        'result': result,
        'user': user,
        'is_teacher': user.is_teacher,
        'is_student': user.is_student,
        'is_tutor_student': user.is_tutor_student,
        'courses_progress': courses_progress,
        'pending_enrollments': pending_enrollments,
        'courses_count': len(courses_progress),
        'completed_courses': sum(1 for c in courses_progress if c['completed']),
        'overall_pct': (
            round(total_done / total_lessons * 100) if total_lessons else 0
        ),
    }
    return render(request, 'lesson/profile.html', context)


# @login_required
# @require_http_methods(["GET", "POST"])
# def upload_image(request):
#     """
#     Endpoint для загрузки изображений в Editor.js
#     """
#     if request.method == 'POST':
#         if 'image' not in request.FILES:
#             return JsonResponse({'success': 0, 'error': 'Файл не найден'}, status=400)
#
#         image_file = request.FILES['image']
#
#         # Проверка типа файла
#         allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
#         if image_file.content_type not in allowed_types:
#             return JsonResponse({
#                 'success': 0,
#                 'error': 'Неподдерживаемый формат изображения. Разрешены: JPG, PNG, GIF, WebP'
#             }, status=400)
#
#         # Проверка размера файла (максимум 10 МБ)
#         max_size = 10 * 1024 * 1024  # 10 МБ
#         if image_file.size > max_size:
#             return JsonResponse({
#                 'success': 0,
#                 'error': f'Файл слишком большой. Максимальный размер: 10 МБ'
#             }, status=400)
#
#         # Сохранение файла
#         try:
#             # Генерируем уникальное имя файла
#             file_extension = image_file.name.split('.')[-1] if '.' in image_file.name else 'jpg'
#             unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
#
#             # Создаем путь с датой для организации файлов
#             date_path = datetime.now().strftime('%Y/%m/%d')
#             file_path = default_storage.save(
#                 f'editorjs/{date_path}/{unique_filename}',
#                 ContentFile(image_file.read())
#             )
#
#             # Получаем URL файла
#             file_url = default_storage.url(file_path)
#
#             # Убеждаемся, что URL начинается с правильного пути
#             if not file_url.startswith('http') and not file_url.startswith('/'):
#                 file_url = '/' + file_url.lstrip('/')
#
#             return JsonResponse({
#                 'success': 1,
#                 'url': file_url
#             })
#         except Exception as e:
#             import traceback
#             print(f"Ошибка загрузки изображения: {e}")
#             print(traceback.format_exc())
#             return JsonResponse({
#                 'success': 0,
#                 'error': f'Ошибка при сохранении файла: {str(e)}'
#             }, status=500)
#
#     return JsonResponse({'success': 0, 'error': 'Метод не разрешен'}, status=405)
#
#
# @login_required
# def lesson_create(request):
#     """
#     Создание нового урока с блочным редактором
#     """
#     if request.method == 'POST':
#         form = CreateLessonForm(request.POST)
#         if form.is_valid():
#             lesson = form.save()
#             return redirect('lesson:lesson_edit', lesson_id=lesson.id)
#     else:
#         form = CreateLessonForm()
#
#     context = {
#         'form': form,
#         'lesson': None,
#     }
#     return render(request, 'lesson/lesson_edit.html', context)
#
#
# @login_required
# def lesson_edit(request, lesson_id):
#     """
#     Редактирование урока с блочным редактором
#     """
#     try:
#         lesson = Lesson.objects.get(id=lesson_id)
#     except Lesson.DoesNotExist:
#         return redirect('lesson:courses')
#
#     if request.method == 'POST':
#         form = CreateLessonForm(request.POST, instance=lesson)
#         if form.is_valid():
#             form.save()
#             return redirect('lesson:courses')
#     else:
#         form = CreateLessonForm(instance=lesson)
#
#     context = {
#         'form': form,
#         'lesson': lesson,
#     }
#     return render(request, 'lesson/lesson_edit.html', context)


@login_required
def profile_edit(request):
    """
    Редактирование профайла
    """
    if request.method == 'POST':
        form = EditProfile(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            if request.FILES.get('image'):
                user.image = request.FILES['image']
            user.save()
            return redirect('lesson:profile')
    else:
        form = EditProfile(instance=request.user)
    return render(request, 'lesson/profile_edit.html', {'form': form})


def course_editor(request):
    pass


@login_required
def enrollment_requests(request):
    """Модерация заявок на курсы (для персонала).

    Точка будущего эквайринга: одобрение здесь заменится подтверждением
    оплаты, но статусная модель и интерфейс остаются теми же.
    """
    if not request.user.is_staff:
        raise PermissionDenied
    pending = (
        CourseEnrollment.objects
        .filter(status=CourseEnrollment.Status.PENDING)
        .select_related('course', 'user')
        .order_by('enrolled_at')
    )
    decided = (
        CourseEnrollment.objects
        .exclude(status=CourseEnrollment.Status.PENDING)
        .select_related('course', 'user', 'decided_by')
        .order_by('-decided_at')[:25]
    )
    return render(
        request,
        'lesson/enrollment_requests.html',
        {'pending': pending, 'decided': decided},
    )


@login_required
def enrollment_decide(request, pk, decision):
    if not request.user.is_staff:
        raise PermissionDenied
    enrollment = get_object_or_404(CourseEnrollment, pk=pk)
    if request.method == 'POST':
        if decision == 'approve':
            enrollment.approve(by=request.user)
            student = (
                enrollment.user.get_full_name() or enrollment.user.username
            )
            messages.success(
                request,
                f'Курс «{enrollment.course}» открыт для {student}.'
            )
        elif decision == 'reject':
            enrollment.reject(by=request.user)
            messages.info(request, 'Заявка отклонена.')
    return redirect('lesson:enrollment_requests')
