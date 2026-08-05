from datetime import date

from dateutil.relativedelta import relativedelta

MONTH_NAMES_RU = (
    '', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь',
)


def finance_month_from_request(request, *, today=None):
    today = today or date.today()
    finance_month = today.replace(day=1)
    month_param = request.GET.get('month')
    if month_param:
        try:
            year_s, month_s = month_param.split('-', 1)
            finance_month = date(int(year_s), int(month_s), 1)
        except (ValueError, TypeError):
            pass
    return finance_month


def month_choices(*, today=None, count=12):
    today = today or date.today()
    cursor = today.replace(day=1)
    choices = []
    for _ in range(count):
        choices.append({
            'value': cursor.strftime('%Y-%m'),
            'label': f'{MONTH_NAMES_RU[cursor.month]} {cursor.year}',
        })
        cursor = cursor - relativedelta(months=1)
    return choices


def schedule_role(request, *, is_teacher, is_student):
    """Какое расписание показывать: teach | learn."""
    role = request.GET.get('role')
    if is_teacher and is_student:
        return role if role in ('teach', 'learn') else 'teach'
    if is_teacher:
        return 'teach'
    return 'learn'
