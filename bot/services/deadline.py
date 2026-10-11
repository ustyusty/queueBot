import calendar
from datetime import date

from telegram import InlineKeyboardButton as Button, InlineKeyboardMarkup as Keyboard

MONTHS = ('Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
          'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь')


def date_choices():
    return Keyboard([
        [Button('Сегодня', callback_data='study:date:today'), Button('Завтра', callback_data='study:date:tomorrow')],
        [Button('📅 Выбрать дату', callback_data='study:date:calendar')],
        [Button('Без срока', callback_data='study:date:none')],
    ])


def month_keyboard(year, month):
    rows = [[Button(f'{MONTHS[month - 1]} {year}', callback_data='study:date:noop')],
            [Button(day, callback_data='study:date:noop') for day in ('Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс')]]
    for week in calendar.Calendar().monthdayscalendar(year, month):
        rows.append([Button(str(day) if day else '·',
                            callback_data=f'study:date:day:{date(year, month, day).isoformat()}' if day else 'study:date:noop')
                     for day in week])
    previous = (year - 1, 12) if month == 1 else (year, month - 1)
    following = (year + 1, 1) if month == 12 else (year, month + 1)
    rows.append([Button('◀️', callback_data=f'study:date:month:{previous[0]}:{previous[1]}'),
                 Button('▶️', callback_data=f'study:date:month:{following[0]}:{following[1]}')])
    rows.append([Button('Без срока', callback_data='study:date:none')])
    return Keyboard(rows)


def time_keyboard():
    return Keyboard([
        [Button(value, callback_data=f'study:date:time:{value}') for value in ('09:00', '12:00', '18:00')],
        [Button('23:59', callback_data='study:date:time:23:59'), Button('Другое время', callback_data='study:date:custom')],
        [Button('⬅️ Изменить дату', callback_data='study:date:calendar')],
    ])
