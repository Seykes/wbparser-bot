from telebot import types

from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from database import UsersDBFunc
from config import test_chat_id

def main_keyboard(chat_id):

    keyboard = types.ReplyKeyboardMarkup(True)
    keyboard.row('Сводка',)
    keyboard.row('Заказы', 'Выкупы')
    if UsersDBFunc.check_notifications(chat_id):
        keyboard.row('Остатки', 'Выключить уведомления')
    else:
        keyboard.row('Остатки', 'Включить уведомления')
    keyboard.row('Реферальная ссылка', 'Профиль')
    keyboard.row('Обратная связь', 'FAQ')
    return keyboard

def non_sub_keyboard(chat_id):

    keyboard = types.ReplyKeyboardMarkup(True)
    keyboard.row('Сводка',)
    keyboard.row('Заказы', 'Выкупы')
    if UsersDBFunc.check_notifications(chat_id):
        keyboard.row('Остатки', 'Выключить уведомления')
    else:
        keyboard.row('Остатки', 'Включить уведомления')
    keyboard.row('Реферальная ссылка', 'Профиль')
    keyboard.row('Обратная связь', 'FAQ')
    return keyboard

def new_user_keys(chat_id):
    new_user_keyboard = types.InlineKeyboardMarkup()
    new_user_keyboard.add(
        types.InlineKeyboardButton(text='Попробовать бесплатно', callback_data=f'testrequest_{chat_id}'),
        types.InlineKeyboardButton(text='Может позже', callback_data=f'testrequestfail_{chat_id}')
    )
    return new_user_keyboard

def profile_keys(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text='Пополнить баланс', callback_data='addpay'),
        types.InlineKeyboardButton(text='Изменить API ключ', callback_data='editkey')
    )
    return keyboard

def choice_date_keyboard(method):
    if method in ('brief', 'orders', 'sales'):
        keyboard = types.InlineKeyboardMarkup()
        data = {
            'Сегодня':f'{method}_today',
            'Вчера':f'{method}_yesterday',
            'Выбрать дату':f'{method}_calendar'
        }
        #'Неделя':f'{method}_week',

        for key, value in data.items():
            keyboard.add(
                types.InlineKeyboardButton(text=key, callback_data=value)
            )
        return keyboard

def calendar_keyboard(method):
    """ Отправка клавиатуры календаря """
    if method in ('brief_calendar', 'orders_calendar', 'sales_calendar'):
        calendar, step = DetailedTelegramCalendar(locale='ru').build()

        return calendar, step

def choice_cancel_keyboard():
	""" Отправка клавиатура отмены процессов """
	keyboard = types.ReplyKeyboardMarkup(True)
	keyboard.add(types.KeyboardButton('Отмена'))

	return keyboard

def change_notifications_keyboard():
    """ Клавиатура смены многовенных оповещений о заказе """
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text='Включить', callback_data='notify_on'),
        types.InlineKeyboardButton(text='Не надо', callback_data='notify_not_established')# Не используется
    ) 
    return keyboard

def remains_keyboard(all_remains_name):
    """ Клавиатура складов """
    keyboard = types.InlineKeyboardMarkup()
    for remain in all_remains_name:
        keyboard.add(types.InlineKeyboardButton(text=remain, callback_data=f'remain_{remain}'))
    keyboard.add(
        types.InlineKeyboardButton(text='Все склады', callback_data='all_remains')
    ) 
    return keyboard
    
def nextpay_keybroad(link, check):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text='Оплатить счет', url=link),
        types.InlineKeyboardButton(text='Проверить оплату', callback_data=f'checkpay_{check}')
    )

    return keyboard

def newkey_keyboard(key):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text='Да', callback_data=f'acceptnewkey_{key}'),
        types.InlineKeyboardButton(text='Нет', callback_data='declinekey')
    )

    return keyboard

def trialactivate(key):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text='Да', callback_data=f'acceptkey_{key}'),
        types.InlineKeyboardButton(text='Нет', callback_data='declinekey')
    )

    return keyboard