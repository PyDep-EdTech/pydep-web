"""Умный поиск курсов: транслит, алиасы, ранжирование."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import unquote

from django.db.models import QuerySet
from transliterate import translit

from .models import Category, Course

# Русские разговорные названия → канонические токены в каталоге
ALIASES: dict[str, str] = {
    "гит": "git",
    "гитхаб": "github",
    "питон": "python",
    "пайтон": "python",
    "джанго": "django",
    "докер": "docker",
    "джаваскрипт": "javascript",
    "яваскрипт": "javascript",
    "жс": "javascript",
    "js": "javascript",
    "эскюэл": "sql",
    "скл": "sql",
    "постгрес": "postgresql",
    "постгре": "postgresql",
    "линукс": "linux",
    "алгоритмы": "алгоритм",
    "верстка": "html",
    "фронт": "html",
    "бэкенд": "django",
    "бекенд": "django",
    "веб": "django",
    "контейнер": "docker",
    "контейнеры": "docker",
}

SORT_CHOICES = {
    "relevance": "По релевантности",
    "name": "По названию",
    "price_asc": "Сначала дешевле",
    "price_desc": "Сначала дороже",
    "duration": "По длительности",
}


@dataclass
class SearchResult:
    course: Course
    score: float
    matched_in: str


def _normalize(text: str) -> str:
    text = unquote(text or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def _safe_translit_to_latin(text: str) -> str:
    try:
        return translit(text, "ru", reversed=True).lower()
    except Exception:
        return text


def _safe_translit_to_cyrillic(text: str) -> str:
    try:
        return translit(text, "ru").lower()
    except Exception:
        return text


def expand_query(query: str) -> list[str]:
    """Строит набор вариантов запроса для нечёткого совпадения."""
    q = _normalize(query)
    if not q:
        return []

    variants: set[str] = {q}

    if q in ALIASES:
        variants.add(ALIASES[q])

    for alias, canonical in ALIASES.items():
        if alias in q:
            variants.add(canonical)
            variants.add(alias)
        if canonical in q:
            variants.add(canonical)
            variants.add(alias)

    latin = _safe_translit_to_latin(q)
    cyrillic = _safe_translit_to_cyrillic(q)
    variants.update({latin, cyrillic})

    for token in re.split(r"[\s,;/]+", q):
        if not token:
            continue
        variants.add(token)
        if token in ALIASES:
            variants.add(ALIASES[token])
        variants.add(_safe_translit_to_latin(token))
        variants.add(_safe_translit_to_cyrillic(token))

    return [v for v in variants if v]


def _course_haystacks(course: Course) -> dict[str, str]:
    category_name = course.category.name if course.category_id else ""
    module_titles = " ".join(course.modules.values_list("title", flat=True))

    fields = {
        "name": course.name,
        "description": course.description or "",
        "language": course.programming_language or "",
        "level": course.level or "",
        "category": category_name,
        "modules": module_titles,
    }

    expanded: dict[str, str] = {}
    for key, value in fields.items():
        raw = value.lower()
        expanded[key] = raw
        expanded[f"{key}_lat"] = _safe_translit_to_latin(raw)
    return expanded


def _match_score(course: Course, variants: Iterable[str]) -> SearchResult | None:
    haystacks = _course_haystacks(course)
    weights = {
        "name": 12,
        "language": 10,
        "category": 7,
        "modules": 6,
        "description": 4,
        "level": 2,
    }

    best_score = 0.0
    matched_in = ""

    for variant in variants:
        if not variant:
            continue
        for field, weight in weights.items():
            for suffix in ("", "_lat"):
                hay = haystacks.get(f"{field}{suffix}", "")
                if not hay:
                    continue
                if hay == variant:
                    score = weight * 3
                elif hay.startswith(variant):
                    score = weight * 2.2
                elif variant in hay:
                    score = weight * 1.5
                else:
                    continue

                if score > best_score:
                    best_score = score
                    matched_in = field

    if best_score <= 0:
        return None

    return SearchResult(course=course, score=best_score, matched_in=matched_in)


def search_courses(
    queryset: QuerySet[Course],
    query: str,
) -> tuple[list[SearchResult], list[str]]:
    """Фильтрует и ранжирует курсы по запросу."""
    variants = expand_query(query)
    if not variants:
        return [], []

    queryset = queryset.prefetch_related("modules", "category")
    results: list[SearchResult] = []

    for course in queryset:
        hit = _match_score(course, variants)
        if hit:
            results.append(hit)

    results.sort(key=lambda item: (-item.score, item.course.name))
    return results, variants


def apply_course_filters(
    queryset: QuerySet[Course],
    *,
    query: str = "",
    category_slugs: list[str] | None = None,
    level: str = "",
    language: str = "",
    sort: str = "relevance",
) -> tuple[QuerySet[Course], list[SearchResult], dict]:
    """Применяет фильтры и сортировку к каталогу курсов."""
    queryset = queryset.filter(is_published=True).select_related("category")
    meta: dict = {
        "query": _normalize(query),
        "variants": [],
        "total_before_pagination": 0,
    }

    if category_slugs:
        queryset = queryset.filter(category__slug__in=category_slugs)

    if level:
        queryset = queryset.filter(level=level)

    if language:
        queryset = queryset.filter(programming_language__iexact=language)

    search_results: list[SearchResult] = []
    if meta["query"]:
        search_results, meta["variants"] = search_courses(queryset, meta["query"])
        ids = [item.course.id for item in search_results]
        meta["total_before_pagination"] = len(ids)
        if not ids:
            return queryset.none(), search_results, meta
        ordered = _as_ordered_queryset(queryset, ids)
        if sort != "relevance":
            ordered = _apply_sort(ordered, sort)
        return ordered, search_results, meta

    meta["total_before_pagination"] = queryset.count()
    effective_sort = sort if sort != "relevance" else "name"
    return _apply_sort(queryset, effective_sort), search_results, meta


def _as_ordered_queryset(queryset: QuerySet[Course], ids: list[int]) -> QuerySet[Course]:
    if not ids:
        return queryset.none()
    from django.db.models import Case, IntegerField, When

    ordering = Case(
        *[When(id=pk, then=pos) for pos, pk in enumerate(ids)],
        output_field=IntegerField(),
    )
    return queryset.filter(id__in=ids).order_by(ordering)


def _apply_sort(queryset: QuerySet[Course], sort: str) -> QuerySet[Course]:
    mapping = {
        "name": ("name",),
        "price_asc": ("price",),
        "price_desc": ("-price",),
        "duration": ("duration", "name"),
        "relevance": ("name",),
    }
    return queryset.order_by(*mapping.get(sort, ("name",)))


def distinct_languages(queryset: QuerySet[Course] | None = None) -> list[str]:
    qs = queryset or Course.objects.filter(is_published=True)
    return sorted(
        {lang for lang in qs.values_list("programming_language", flat=True) if lang},
        key=str.lower,
    )


def distinct_levels() -> list[str]:
    return [choice[0] for choice in Course.level_choices]
