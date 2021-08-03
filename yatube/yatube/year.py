import datetime as dt


def year(request):
    """
    Добавляет переменную с текущим годом.
    """
    current_year = dt.date.today().year
    return {
        'year': current_year,
    }
