"""Транслитерация названий в URL-slug (латиница)."""

from django.utils.text import slugify
from transliterate import translit


def translit_slug(text: str, *, max_length: int = 100) -> str:
    """Русское название → латинский slug: «Файлы и ошибки» → fajly-i-oshibki."""
    raw = str(text).strip()
    if not raw:
        return "item"
    try:
        latin = translit(raw, "ru", reversed=True)
    except Exception:
        latin = raw
    slug = slugify(latin, allow_unicode=False)
    if not slug:
        slug = slugify(raw, allow_unicode=False)
    return (slug or "item")[:max_length]


def unique_slug(model_class, text: str, *, exclude_pk=None, max_length: int = 100) -> str:
    """Уникальный slug для модели (суффикс -2, -3 при коллизии)."""
    base = translit_slug(text, max_length=max_length - 6)
    slug = base
    counter = 2
    while True:
        qs = model_class.objects.filter(slug=slug)
        if exclude_pk is not None:
            qs = qs.exclude(pk=exclude_pk)
        if not qs.exists():
            return slug
        suffix = f"-{counter}"
        slug = f"{base[: max_length - len(suffix)]}{suffix}"
        counter += 1
