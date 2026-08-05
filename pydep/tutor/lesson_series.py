from datetime import timedelta

from .models import Lesson


def lessons_in_series(lesson):
    """Все занятия одной серии повторов (включая текущее)."""
    if lesson.repeat_group:
        return Lesson.objects.filter(
            teacher=lesson.teacher,
            repeat_group=lesson.repeat_group,
        ).order_by("date", "start_time")

    window_start = lesson.created_at - timedelta(seconds=30)
    window_end = lesson.created_at + timedelta(seconds=30)
    candidates = list(
        Lesson.objects.filter(
            teacher=lesson.teacher,
            student=lesson.student,
            subject=lesson.subject,
            start_time=lesson.start_time,
            end_time=lesson.end_time,
            lesson_format=lesson.lesson_format,
            repeat_group__isnull=True,
            created_at__gte=window_start,
            created_at__lte=window_end,
        ).order_by("date", "start_time")
    )
    if len(candidates) <= 1:
        return Lesson.objects.filter(pk=lesson.pk)

    anchor = candidates[0].date
    series = [
        item
        for item in candidates
        if (item.date - anchor).days % 7 == 0
    ]
    if not any(item.pk == lesson.pk for item in series):
        return Lesson.objects.filter(pk=lesson.pk)
    return Lesson.objects.filter(
        pk__in=[item.pk for item in series]
    ).order_by("date", "start_time")


def series_count(lesson):
    return lessons_in_series(lesson).count()


def _legacy_series_count(lesson, bucket):
    """Счётчик серии для занятия без repeat_group внутри одного списка."""
    if len(bucket) <= 1:
        return 1
    bucket = sorted(bucket, key=lambda item: item.date)
    anchor = bucket[0].date
    series = [
        item for item in bucket
        if (item.date - anchor).days % 7 == 0
    ]
    series_pks = {item.pk for item in series}
    if lesson.pk not in series_pks:
        return 1
    return len(series)


def attach_series_counts(lessons):
    """Добавляет lesson.series_count для списка занятий без N+1."""
    lessons = list(lessons)
    by_repeat_group = {}
    legacy_buckets = {}

    for lesson in lessons:
        if lesson.repeat_group:
            by_repeat_group.setdefault(lesson.repeat_group, []).append(lesson)
            continue
        key = (
            lesson.student_id,
            lesson.subject,
            lesson.start_time,
            lesson.end_time,
            lesson.lesson_format,
            lesson.created_at.replace(second=0, microsecond=0),
        )
        legacy_buckets.setdefault(key, []).append(lesson)

    for group in by_repeat_group.values():
        count = len(group)
        for lesson in group:
            lesson.series_count = count

    for bucket in legacy_buckets.values():
        for lesson in bucket:
            lesson.series_count = _legacy_series_count(lesson, bucket)

    for lesson in lessons:
        if not hasattr(lesson, "series_count"):
            lesson.series_count = 1
    return lessons
