import random

from datetime import datetime, timedelta
from traceback import format_exc

def get_date(method_or_date):
    try:

        if method_or_date == 'today':
            date_for_brief = datetime.now().strftime('%Y-%m-%dT00:00:00')
        elif method_or_date == 'yesterday':
            yesterday = datetime.now() - timedelta(1)
            date_for_brief = datetime.strftime(yesterday, '%Y-%m-%dT00:00:00') 
        elif method_or_date == 'week':
            date_for_brief = get_days_week() # Возвращает список дней текущий недели до текущего дня и исключая его
        else:
            date_for_brief = f'{method_or_date}T00:00:00'

        return date_for_brief

    except Exception as e:
        print('Ошибка:\n', format_exc())

def get_days_week():
    """ Создание массива дней за неделю дня использования в api """
    try:
        now = datetime.now()

        now_day_1 = now - timedelta(days=now.weekday())
        
        days = []
        for n_week in range(1):
            week = [(now_day_1 - timedelta(days=d+n_week*7)).strftime('%Y-%m-%dT00:00:00') for d in range(7)]
            for day in week:
                days.append(day)

        return days

    except Exception as e:
        print('Ошибка:\n', format_exc())

def get_days_vievs(method_or_date):
    """ Создание массива дней за неделю в удобночитаемом формате """
    try:
        days = []
        if method_or_date == 'today':
            day = datetime.now().strftime('%Y-%m-%d')
            days.append(day)
        elif method_or_date == 'yesterday':
            day = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
            days.append(day)
        elif method_or_date == 'week':
            now = datetime.now()
            now_day_1 = now - timedelta(days=now.weekday())
            for n_week in range(1):
                week = [(now_day_1 - timedelta(days=d+n_week*7)).strftime('%Y-%m-%d') for d in range(7)]
                
                count = None
                for day_num, day in enumerate(week):
                    if count == None:
                        days.append(day)
                        if day == datetime.now().strftime('%Y-%m-%d'):
                            count = day_num
                            days.remove(day)
        else:
            day = method_or_date
            days.append(day)

        return days

    except Exception as e:
        print('Ошибка:\n', format_exc())

def dynamic_delay(specifed_timer, get_order):
    try:
        if specifed_timer is True:
            if get_order is True:
                return random.randint(10, 15)
            else:
                return random.randint(5, 9)
        else:
            if get_order is True:
                return random.randint(5, 10)
            else:
                return random.randint(2, 5)

    except Exception as e:
        print('Ошибка:\n', format_exc())