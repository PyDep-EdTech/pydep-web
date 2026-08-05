"""Хелперы для формирования content_blocks в формате Editor.js."""

MEDIA = "/media/lessons/seed"


def header(text, level=2):
    return {"type": "header", "data": {"text": text, "level": level}}


def paragraph(text):
    return {"type": "paragraph", "data": {"text": text}}


def image(url, caption=""):
    return {"type": "image", "data": {"url": url, "caption": caption}}


def code(snippet, language="python"):
    return {"type": "code", "data": {"code": snippet, "language": language}}


def output(text, label="Результат в терминале"):
    return {"type": "output", "data": {"text": text, "label": label}}


def example(code_snippet, output_text, language="python"):
    """Код и ожидаемый вывод программы — пара блоков для урока."""
    return [code(code_snippet, language), output(output_text)]


def table(rows):
    return {"type": "table", "data": {"content": rows}}


def list_block(items, ordered=False):
    return {
        "type": "list",
        "data": {
            "style": "ordered" if ordered else "unordered",
            "items": items,
        },
    }


def quote(text, caption=""):
    return {"type": "quote", "data": {"text": text, "caption": caption}}


def delimiter():
    return {"type": "delimiter", "data": {}}


def practice_lesson(title, goal, tasks, hints=None, solution_code=None, solution_output=None):
    """Шаблон блоков для отдельного урока-практики."""
    blocks = [
        header(f"Практика: {title}", 2),
        paragraph(goal),
        quote(
            "Сначала попробуйте решить сами — хотя бы 15–20 минут. "
            "Подсказки и решение ниже, но они станут полезнее после попытки.",
            "Как работать с практикой",
        ),
        header("Задания", 3),
        list_block(tasks, ordered=True),
    ]
    if hints:
        blocks.extend([
            delimiter(),
            header("Подсказки", 3),
            list_block(hints),
        ])
    if solution_code:
        blocks.extend([
            delimiter(),
            header("Пример решения", 3),
            paragraph(
                "Это один из возможных вариантов. Ваш код может отличаться — "
                "главное, чтобы программа работала и была читаемой."
            ),
            code(solution_code),
        ])
        if solution_output:
            blocks.append(output(solution_output))
    return blocks


# Локальные иллюстрации: сгенерированные PNG + SVG-логотехи
IMG = {
    "python": f"{MEDIA}/python-logo.svg",
    "django": f"{MEDIA}/django-logo.svg",
    "javascript": f"{MEDIA}/javascript-logo.svg",
    "sql": f"{MEDIA}/postgresql-logo.svg",
    "git": f"{MEDIA}/git-logo.svg",
    "html_css": f"{MEDIA}/html5-logo.svg",
    "css3": f"{MEDIA}/css3-logo.svg",
    "algorithms": f"{MEDIA}/lesson-big-o.png",
    "docker": f"{MEDIA}/docker-logo.svg",
    "terminal": f"{MEDIA}/lesson-terminal.png",
    "database": f"{MEDIA}/lesson-database.png",
    "browser": f"{MEDIA}/lesson-dom-browser.png",
    "flowchart": f"{MEDIA}/lesson-flowchart.svg",
    "django_mvt": f"{MEDIA}/lesson-django-mvt.png",
    "git_branching": f"{MEDIA}/lesson-git-branching.png",
    "flexbox": f"{MEDIA}/lesson-flexbox.png",
    "css_grid": f"{MEDIA}/lesson-css-grid.png",
    "sql_join": f"{MEDIA}/lesson-sql-join.png",
    "stack_queue": f"{MEDIA}/lesson-stack-queue.png",
    "async_js": f"{MEDIA}/lesson-async-js.png",
    "binary_search": f"{MEDIA}/lesson-binary-search.png",
    "docker_compose": f"{MEDIA}/lesson-docker-compose.png",
    "python_types": f"{MEDIA}/lesson-python-types.svg",
    "vscode": f"{MEDIA}/vscode-logo.svg",
    "github": f"{MEDIA}/github-logo.svg",
    "install_python": f"{MEDIA}/lesson-install-python.svg",
    "variable_box": f"{MEDIA}/lesson-variable-box.svg",
    "repl": f"{MEDIA}/lesson-repl.svg",
    "if_else": f"{MEDIA}/lesson-if-else.svg",
    "for_loop": f"{MEDIA}/lesson-for-loop.svg",
    "list_visual": f"{MEDIA}/lesson-list.svg",
    "dict_visual": f"{MEDIA}/lesson-dict.svg",
    "function_visual": f"{MEDIA}/lesson-function.svg",
    "file_io": f"{MEDIA}/lesson-file-io.svg",
}
